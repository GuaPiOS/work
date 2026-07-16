"""Playback subsystem — the extensibility core.

A PlaybackCoordinator owns runtime/player_control.json as the single "playback
intent" and hands it to a pluggable, ordered list of PlaybackAdapters. Today:
  - BrowserAdapter   : the connected web UI plays via <audio> (preferred).
  - LocalAfplayAdapter: macOS afplay subprocess, used when no browser client is
    connected and player.local_fallback is on.

Whether a browser is connected is signalled cross-process via
runtime/last_ui_poll (the UI server writes it on each /api/state poll), so the
collector — a separate process — can make the same decision.

Because generation hands the coordinator a control and asks "what actually
happened?", the Feishu success receipt can finally be honest: it says 'playing'
only when something is actually playing, else 'open the app to listen'.

Future mobile/remote clients implement the same PlaybackAdapter protocol.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Protocol

from .runtime import (
    PROJECT_ROOT, RUNTIME_DIR, PLAYER_PID_FILE_DEFAULT,
    is_process_alive, process_command, read_pid, stop_pid_file,
    ignore_sighup, touch_activity,
)
from .io_utils import read_text, write_text, read_json, write_json, get_hash
from .config import player_pid_file

PLAYER_CONTROL_FILE = RUNTIME_DIR / "player_control.json"
LAST_UI_POLL_FILE = RUNTIME_DIR / "last_ui_poll"
RUN_PY = PROJECT_ROOT / "run.py"
UI_FRESH_SECONDS = 12  # browser counts as connected if it polled within this window


# ─── audio primitives ─────────────────────────────────────────────────────────

def find_player() -> str:
    if shutil.which("afplay"):
        return "afplay"
    if shutil.which("ffplay"):
        return "ffplay"
    raise RuntimeError("No audio player found. Install ffplay or run on macOS (uses afplay).")


def play_audio_once(audio_file: str) -> int:
    player = find_player()
    if player == "afplay":
        return subprocess.run(["afplay", audio_file], check=False).returncode
    if player == "ffplay":
        return subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_file], check=False
        ).returncode
    return 1


def run_player_control_child(control_file: str) -> None:
    """Loop reading a control file and playing its playlist. Spawned as a detached
    child by LocalAfplayAdapter (and by run.py --player-control)."""
    last_signature = ""
    current_index = 0
    try:
        while True:
            control = read_player_control(control_file)
            playlist = control.get("playlist") if isinstance(control, dict) else []
            if not playlist:
                print("player: empty playlist; waiting", flush=True)
                time.sleep(2)
                continue
            signature = control_signature(control)
            if signature != last_signature:
                print(f"player: loaded playlist mode={control.get('mode')} size={len(playlist)}", flush=True)
                last_signature = signature
                current_index = 0
            if current_index >= len(playlist):
                if not control.get("loop", True):
                    return
                current_index = 0
            item = playlist[current_index]
            audio_file = str(item.get("audio") or "")
            if not audio_file:
                current_index += 1
                continue
            print(f"player: playing {audio_file}", flush=True)
            returncode = play_audio_once(audio_file)
            print(f"player: playback exited rc={returncode}", flush=True)
            interval_seconds = int(control.get("interval_seconds", 5))
            if interval_seconds > 0:
                time.sleep(interval_seconds)
            next_control = read_player_control(control_file)
            if control_signature(next_control) != last_signature:
                continue
            current_index += 1
    except Exception as exc:
        print(f"player: failed: {exc}", flush=True)
        raise


# ─── control file ─────────────────────────────────────────────────────────────

def latest_batch_items(items: list[dict]) -> list[dict]:
    if not items:
        return []
    latest = items[-1]
    latest_message_id = str(latest.get("message_id") or "").strip()
    if not latest_message_id:
        return [latest]
    batch = []
    for item in reversed(items):
        if str(item.get("message_id") or "").strip() != latest_message_id:
            break
        batch.append(item)
    return list(reversed(batch))


def select_playback_items(payload: dict, config: dict) -> tuple[str, list[dict]]:
    """Resolve (mode, items) from config. Mode override is already merged into
    config by the config layer, so there's no second override read here (that was
    the dead computation that made UI mode overrides silently no-op via collector)."""
    items = payload.get("items", []) if isinstance(payload, dict) else []
    if not items:
        return "single", []
    # Daily playback is the safe default: direct bot messages accumulate into
    # today's learning set and must not silently disappear from the queue.
    # "auto" remains available as an explicit latest-message mode.
    mode = str(config.get("player", {}).get("mode", "daily")).strip().lower()
    latest_items = latest_batch_items(items)
    if mode == "single":
        return "single", latest_items[-1:] or items[-1:]
    if mode == "list":
        return "list", latest_items or items
    if mode == "daily":
        return "daily", items
    # auto is an explicit opt-in latest-message mode.
    if len(latest_items) <= 1:
        return "single", latest_items or items[-1:]
    return "list", latest_items


def audio_path_for_item(day: str, item: dict) -> str:
    from .study import study_output_dir
    audio = str(item.get("audio") or "").strip()
    if audio:
        return str(study_output_dir(day) / audio)
    return ""


def build_player_control(day: str, payload: dict | None, config: dict) -> dict:
    player_config = config.get("player", {})
    interval_seconds = int(player_config.get("interval_seconds", 5))
    loop = bool(player_config.get("loop", True))
    default_mode = str(player_config.get("mode", "daily")).strip().lower() or "daily"

    playlist = []
    mode = default_mode
    if payload:
        mode, playback_items = select_playback_items(payload, config)
        for item in playback_items:
            audio_path = audio_path_for_item(day, item)
            if audio_path and Path(audio_path).exists():
                playlist.append({
                    "audio": audio_path,
                    "message_id": item.get("message_id", ""),
                    "text": item.get("spoken_english", ""),
                })
    if not playlist and Path(config["output_audio"]).exists():
        playlist.append({"audio": config["output_audio"], "message_id": "", "text": ""})

    signature_source = get_hash(json_dumps({
        "mode": mode, "loop": loop, "interval_seconds": interval_seconds,
        "playlist": [i["audio"] for i in playlist],
    }))
    return {
        "updated_at": time.time(),
        "signature": signature_source,
        "mode": mode,
        "loop": loop,
        "interval_seconds": interval_seconds,
        "playlist": playlist,
    }


def json_dumps(data) -> str:
    import json
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def write_player_control(control: dict, control_file: str | Path = PLAYER_CONTROL_FILE) -> None:
    write_json(control_file, control)


def read_player_control(control_file: str | Path = PLAYER_CONTROL_FILE) -> dict:
    data = read_json(control_file)
    return data if isinstance(data, dict) else {}


def control_signature(control: dict) -> str:
    return str(control.get("signature") or control.get("updated_at") or "")


# ─── local afplay subprocess management ──────────────────────────────────────

def _player_uses_control(pid: int) -> bool:
    return "--player-control" in process_command(pid)


def start_local_player(config: dict) -> int | None:
    """Ensure a detached afplay child is running and reading the control file.
    Idempotent: if one is already running (control-driven), just leaves it to
    pick up the latest queue. Returns the player pid (or None)."""
    player_config = config.get("player", {})
    if not player_config.get("enabled", True):
        return None
    pid_file = player_pid_file(config)

    existing = read_pid(pid_file)
    if existing and is_process_alive(existing) and _player_uses_control(existing):
        logging.info("Local player already running pid=%s; queue will update.", existing)
        return existing
    if existing and is_process_alive(existing):
        stop_pid_file(pid_file, "player")

    cmd = [sys.executable, str(RUN_PY), "--player-control", str(PLAYER_CONTROL_FILE)]
    log_handle = (PROJECT_ROOT / "logs" / "player.out.log").open("a", encoding="utf-8")
    process = subprocess.Popen(
        cmd, cwd=PROJECT_ROOT, stdin=subprocess.DEVNULL,
        stdout=log_handle, stderr=subprocess.STDOUT,
        preexec_fn=ignore_sighup, start_new_session=True, text=True,
    )
    log_handle.close()
    write_text(pid_file, str(process.pid))
    logging.info("Started local player pid=%s", process.pid)
    return process.pid


def stop_local_player(config: dict) -> None:
    stop_pid_file(player_pid_file(config), "player")


# ─── adapter protocol + implementations ───────────────────────────────────────

class PlaybackAdapter(Protocol):
    name: str

    def is_active(self) -> bool: ...
    def apply(self, control: dict) -> None: ...
    def stop(self) -> None: ...


class BrowserAdapter:
    """Represents connected web UI clients. 'apply' just ensures the control file
    is fresh — the UI polls /api/state and plays the <audio> itself. Whether a
    client is connected is decided by the coordinator from runtime/last_ui_poll."""
    name = "browser"

    def __init__(self, coordinator: "PlaybackCoordinator"):
        self._coordinator = coordinator

    def is_active(self) -> bool:
        return self._coordinator.browser_active()

    def apply(self, control: dict) -> None:
        write_player_control(control)  # UI picks it up on next poll

    def stop(self) -> None:
        pass  # nothing to stop server-side; the UI owns its <audio>


class LocalAfplayAdapter:
    """macOS afplay subprocess fallback for when no browser client is connected."""
    name = "local-afplay"

    def __init__(self, config: dict):
        self._config = config

    def is_active(self) -> bool:
        return bool(self._config.get("player", {}).get("local_fallback", True))

    def apply(self, control: dict) -> None:
        write_player_control(control)
        start_local_player(self._config)

    def stop(self) -> None:
        stop_local_player(self._config)


# ─── coordinator ──────────────────────────────────────────────────────────────

class PlaybackCoordinator:
    """Single owner of the playback intent. Generation hands it a control; it
    picks the best active adapter and reports what actually happened."""

    def __init__(self, config: dict):
        self._config = config
        self._adapters: list[PlaybackAdapter] = []
        self.register(BrowserAdapter(self))
        if config.get("player", {}).get("local_fallback", True):
            self.register(LocalAfplayAdapter(config))

    def register(self, adapter: PlaybackAdapter) -> None:
        self._adapters.append(adapter)

    # cross-process "is a browser open?" signal
    def mark_ui_poll(self) -> None:
        try:
            write_text(LAST_UI_POLL_FILE, str(time.time()))
        except OSError:
            pass

    def browser_active(self) -> bool:
        if not LAST_UI_POLL_FILE.exists():
            return False
        try:
            ts = float(LAST_UI_POLL_FILE.read_text(encoding="utf-8").strip())
            return (time.time() - ts) <= UI_FRESH_SECONDS
        except (ValueError, OSError):
            return False

    def pick_adapter(self) -> PlaybackAdapter | None:
        """Browser preferred; local afplay fallback; else None (waiting)."""
        for adapter in self._adapters:
            if adapter.is_active():
                return adapter
        return None

    def on_generation_ready(self, control: dict) -> str:
        """Apply a fresh control and return a receipt-honest status string:
        'playing' (audio is playing / about to play on a connected client) or
        'waiting' (generated, but nothing is playing yet)."""
        write_player_control(control)
        touch_activity()
        # If the browser took over, release any leftover local afplay (no double audio).
        browser = next((a for a in self._adapters if a.name == "browser"), None)
        local = next((a for a in self._adapters if a.name == "local-afplay"), None)

        if browser and browser.is_active():
            if local:
                local.stop()
            browser.apply(control)
            return "playing"
        if local and local.is_active():
            local.apply(control)
            return "playing"
        return "waiting"


def coordinator_from_config(config: dict) -> PlaybackCoordinator:
    return PlaybackCoordinator(config)
