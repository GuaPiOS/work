#!/usr/bin/env python3
"""Work2English OS — HTTP bridge between the UI and the w2e pipeline.

Zero-extra-dependency (stdlib + requests) server. Jobs:
  1. Serve the built UI      (ui/dist)   at /
  2. Serve generated audio    (output/)   at /files/
  3. GET  /api/state          -> study.json + health + player_control
  4. POST /api/generate       -> w2e.generate coordinator (single-flight)
  5. POST /api/tts-settings   -> persist provider/voice override + bust cache
  6. POST /api/player-mode    -> persist mode override + rebuild control
  7. Keep the collector alive (delegates to w2e.runtime.ensure_running)

Run:  python3 server.py   -> http://127.0.0.1:8000
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import requests

import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from w2e.config import load_config, PLAYER_MODE_FILE, TTS_SETTINGS_FILE, player_pid_file
from w2e.io_utils import read_json, write_json, write_text, get_hash
from w2e.runtime import (
    PROJECT_ROOT, RUNTIME_DIR, OUTPUT_DIR, ensure_dirs,
    COLLECTOR_PID_FILE, LOGS_DIR, ensure_running,
)
from w2e import health, playback, generate, feishu
from w2e.study import STUDY_DIR

UI_DIST = PROJECT_ROOT / "ui" / "dist"
HOST = "127.0.0.1"  # loopback by default; config server.bind: lan exposes to LAN
PORT = int(os.environ.get("W2E_PORT") or os.environ.get("PORT") or "8000")

_coordinator = generate.get_coordinator()


# ─── persisted UI overrides ───────────────────────────────────────────────────

def save_tts_settings(provider: str, voice: str) -> dict:
    write_json(TTS_SETTINGS_FILE, {"provider": provider, "voice": voice}, indent=0)


def save_player_mode(mode: str) -> None:
    write_json(PLAYER_MODE_FILE, {"mode": mode}, indent=0)


def bust_audio_cache(config: dict) -> None:
    """Force the next generation to rebuild audio (used when voice changes)."""
    hash_file = PROJECT_ROOT / config.get("input_hash_file", "runtime/last_input_hash.txt")
    try:
        hash_file.write_text("", encoding="utf-8")
    except OSError:
        pass
    out_audio = PROJECT_ROOT / config.get("output_audio", "output/today_audio.mp3")
    if out_audio.exists():
        try:
            out_audio.unlink()
        except OSError:
            pass
    # Voice change invalidates per-item clips too. Option B's reuse check keys on
    # source text + file existence, so removing the clip dirs forces a full
    # re-synth with the new voice on the next generation.
    import shutil as _shutil
    for audio_dir in STUDY_DIR.glob("*/audio"):
        if audio_dir.is_dir():
            _shutil.rmtree(audio_dir, ignore_errors=True)


# ─── state assembly ───────────────────────────────────────────────────────────

def _audio_path_to_url(path: str) -> str:
    p = str(path).replace("\\", "/").lstrip("/")
    if p.startswith("output/"):
        return "/files/" + p[len("output/"):]
    if p.startswith("/files/") or p.startswith("http"):
        return p
    return "/files/" + p


def _player_control_for_state() -> dict:
    ctrl = playback.read_player_control()
    if not ctrl:
        return {"mode": "auto", "loop": True, "signature": "", "updated_at": 0, "playlist": []}
    playlist = [
        {
            "audioUrl": _audio_path_to_url(it.get("audio", "")),
            "message_id": it.get("message_id", ""),
            "text": it.get("text", ""),
        }
        for it in ctrl.get("playlist", [])
    ]
    return {
        "mode": ctrl.get("mode", "auto"),
        "loop": bool(ctrl.get("loop", True)),
        "signature": ctrl.get("signature", "") or str(ctrl.get("updated_at", "")),
        "updated_at": ctrl.get("updated_at", 0),
        "playlist": playlist,
    }


def build_state() -> dict:
    config = load_config()  # merges runtime tts/player overrides
    day = health.latest_study_day()
    study = health.load_study(day)

    items = []
    if study:
        for it in study.get("items", []):
            audio_rel = it.get("audio", "")
            audio_url = f"/files/study/{day}/{audio_rel}" if (audio_rel and day) else ""
            items.append({
                "time": it.get("time", ""),
                "source": it.get("source", ""),
                "original_zh": it.get("original_zh", ""),
                "spoken_english": it.get("spoken_english", ""),
                "focus_phrase": it.get("focus_phrase", ""),
                "note_zh": it.get("note_zh", ""),
                "audioUrl": audio_url,
            })

    fstate, freason = health.feishu_health(config)
    lstate, lreason = health.ollama_health(config)
    tstate, treason = health.tts_health(config)
    pstate, preason = health.player_health(study, day)

    from w2e import tts as tts_provider

    return {
        "day": day or datetime.now().strftime("%Y-%m-%d"),
        "level": config.get("level", "A2"),
        "voice": config.get("tts", {}).get("voice", "en-US-JennyNeural"),
        "tts": tts_provider.provider_choices(config),
        "player_control": _player_control_for_state(),
        "daily_briefing": (study or {}).get("daily_briefing", ""),
        "items": items,
        "hasAudio": bool(items),
        "stale": health.inbox_stale(config),
        "generating": _coordinator.running,
        "last_error": _coordinator.state.get("last_error"),
        "connectionStatus": {"feishu": fstate, "llm": lstate, "tts": tstate, "player": pstate},
        "diagnostics": {"feishu": freason, "llm": lreason, "tts": treason, "player": preason},
    }


# ─── HTTP handler ─────────────────────────────────────────────────────────────

def guess_mime(path: Path) -> str:
    return {
        ".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
        ".mjs": "application/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8", ".mp3": "audio/mpeg", ".wav": "audio/wav",
        ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ico": "image/x-icon",
        ".map": "application/json; charset=utf-8",
    }.get(path.suffix.lower(), "application/octet-stream")


def send_file(handler: BaseHTTPRequestHandler, path: Path, cacheable: bool = False) -> None:
    if not path.exists() or not path.is_file():
        handler.send_error(HTTPStatus.NOT_FOUND, f"Not found: {path.name}")
        return
    size = path.stat().st_size
    range_header = handler.headers.get("Range")
    if range_header and path.suffix.lower() in {".mp3", ".wav"}:
        try:
            start_spec = range_header.strip().split("=")[1]
            start = int(start_spec.split("-")[0])
            end = int(start_spec.split("-")[1]) if "-" in start_spec and start_spec.split("-")[1] else size - 1
            end = min(end, size - 1)
            length = end - start + 1
            handler.send_response(HTTPStatus.PARTIAL_CONTENT)
            handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            handler.send_header("Accept-Ranges", "bytes")
            handler.send_header("Content-Length", str(length))
            handler.send_header("Content-Type", guess_mime(path))
            handler.end_headers()
            with path.open("rb") as f:
                f.seek(start)
                handler.wfile.write(f.read(length))
            return
        except (ValueError, IndexError):
            pass
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", guess_mime(path))
    handler.send_header("Content-Length", str(size))
    handler.send_header("Accept-Ranges", "bytes")
    if cacheable:
        handler.send_header("Cache-Control", "public, max-age=31536000, immutable")
    handler.end_headers()
    with path.open("rb") as f:
        handler.wfile.write(f.read())


def send_json(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "http://localhost:8000")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "Work2EnglishOS/0.2"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        logging.info("%s - %s", self.address_string(), fmt % args)

    def _read_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            return None
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else None
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _serve_static(self, rel: str) -> None:
        candidate = (UI_DIST / rel).resolve()
        try:
            candidate.relative_to(UI_DIST.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if rel == "" or rel == "/":
            send_file(self, UI_DIST / "index.html")
            return
        if candidate.is_file():
            send_file(self, candidate, cacheable=rel.startswith("assets/"))
            return
        if (UI_DIST / "index.html").exists() and "." not in Path(rel).name:
            send_file(self, UI_DIST / "index.html")
            return
        self.send_error(HTTPStatus.NOT_FOUND, f"Not found: {rel}")

    def _serve_file(self, rel: str) -> None:
        candidate = (OUTPUT_DIR / rel).resolve()
        try:
            candidate.relative_to(OUTPUT_DIR.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        send_file(self, candidate)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/state":
            # A browser poll = a connected client. Record it so the playback
            # coordinator knows the browser adapter can take playback.
            try:
                write_text(playback.LAST_UI_POLL_FILE, str(time.time()))
            except OSError:
                pass
            send_json(self, build_state())
            return
        if path == "/api/health":
            send_json(self, {"ok": True, "time": datetime.now().isoformat()})
            return
        if path.startswith("/files/"):
            self._serve_file(path[len("/files/"):])
            return

        if not UI_DIST.exists():
            body = (
                b"<html><body style='font-family:monospace;background:#05060b;color:#e6e8f0;padding:40px'>"
                b"<h2>UI not built yet</h2>"
                b"<p>Run: <code>cd ui &amp;&amp; npm run build</code></p>"
                b"<p>Then reload.</p></body></html>"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self._serve_static(path.lstrip("/"))

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/tts-settings":
            body = self._read_json()
            if body is None:
                send_json(self, {"ok": False, "error": "invalid json"}, status=400)
                return
            provider = str(body.get("provider", "")).strip()
            voice = str(body.get("voice", "")).strip()
            if provider not in ("edge-tts", "fish-audio"):
                send_json(self, {"ok": False, "error": "unknown provider"}, status=400)
                return
            prev = read_json(TTS_SETTINGS_FILE, {})
            changed = prev.get("provider") != provider or prev.get("voice") != voice
            save_tts_settings(provider, voice)
            if changed:
                bust_audio_cache(load_config())
            from w2e import tts as tts_provider
            send_json(self, {"ok": True, "changed": changed, "tts": tts_provider.provider_choices(load_config())})
            return

        if path == "/api/player-mode":
            body = self._read_json()
            if body is None:
                send_json(self, {"ok": False, "error": "invalid json"}, status=400)
                return
            mode = str(body.get("mode", "")).strip().lower()
            if mode not in ("auto", "single", "list", "daily"):
                send_json(self, {"ok": False, "error": "unknown mode"}, status=400)
                return
            save_player_mode(mode)
            config = load_config()  # picks up the new mode override
            day = health.latest_study_day()
            study_payload = health.load_study(day)
            control = playback.build_player_control(day, study_payload, config)
            playback.write_player_control(control)
            send_json(self, {"ok": True, "mode": mode})
            return

        if path != "/api/generate":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        if _coordinator.running:
            send_json(self, {"ok": False, "already_running": True}, status=409)
            return

        threading.Thread(target=_coordinator.run_now, args=(load_config(),), daemon=True).start()
        send_json(self, {"ok": True, "started": True})

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def _collector_selfheal_loop() -> None:
    """Keep the Feishu collector alive while the UI server runs."""
    def loop():
        while True:
            time.sleep(10)
            try:
                ensure_running(
                    "collector", [sys.executable, "feishu_collect.py"],
                    COLLECTOR_PID_FILE, LOGS_DIR / "collector.out.log",
                )
            except Exception:
                logging.exception("collector self-heal check failed.")

    threading.Thread(target=loop, daemon=True).start()


def main():
    ensure_dirs()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    if not UI_DIST.exists():
        logging.warning("ui/dist not found — UI will show a build hint. Run `cd ui && npm run build`.")

    _collector_selfheal_loop()

    cfg = load_config()
    host = "0.0.0.0" if (cfg.get("server", {}) or {}).get("bind") == "lan" else HOST
    server = ThreadingHTTPServer((host, PORT), Handler)
    url = f"http://localhost:{PORT}"
    logging.info("Work2English OS server on %s (bind=%s)  (Ctrl+C to stop)", url, host)
    print(f"\n  ▶  Work2English OS  →  {url}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
