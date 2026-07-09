"""TTS provider abstraction.

Two providers:
  - edge-tts   : free Microsoft Edge TTS (offline CLI, no key).
  - fish-audio : high-quality neural voices (https://fish.audio). Needs an API key.

The dispatcher `synthesize()` reads config["tts"]["provider"] and the current
voice and writes an MP3 to out_path. Provider/voice are chosen at runtime from
the UI (the config layer merges runtime/tts_settings.json in).

If fish-audio fails (network, credit, bad key), synthesize() falls back to
edge-tts so generation never breaks the pipeline.
"""
from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import requests

from .runtime import PROJECT_ROOT

FISH_ENDPOINT = "https://api.fish.audio/v1/tts"

EDGE_VOICES = [
    {"id": "en-US-AriaNeural", "name": "Aria · US"},
    {"id": "en-US-JennyNeural", "name": "Jenny · US"},
    {"id": "en-US-AvaNeural", "name": "Ava · US"},
    {"id": "en-US-GuyNeural", "name": "Guy · US"},
    {"id": "en-US-DavisNeural", "name": "Davis · US"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia · UK"},
    {"id": "en-AU-NatashaNeural", "name": "Natasha · AU"},
]


# ─── public API ───────────────────────────────────────────────────────────────

def fish_api_key(config: dict) -> str:
    fa = config.get("fish_audio", {}) or {}
    return (os.environ.get("FISH_AUDIO_API_KEY") or fa.get("api_key") or "").strip()


def fish_configured(config: dict) -> bool:
    return bool(fish_api_key(config))


def _fish_voices(config: dict) -> list[dict]:
    fa = config.get("fish_audio", {}) or {}
    return [v for v in (fa.get("voices") or []) if v.get("id")]


def provider_choices(config: dict) -> dict[str, Any]:
    fa = config.get("fish_audio", {}) or {}
    endpoint = fa.get("endpoint") or FISH_ENDPOINT
    model = fa.get("model") or "s2.1-pro-free"
    return {
        "current": {
            "provider": (config.get("tts", {}) or {}).get("provider", "edge-tts"),
            "voice": (config.get("tts", {}) or {}).get("voice", "en-US-AriaNeural"),
        },
        "providers": [
            {"id": "edge-tts", "name": "Edge TTS", "free": True, "configured": True},
            {
                "id": "fish-audio",
                "name": "Fish Audio",
                "free": model.endswith("-free"),
                "configured": fish_configured(config),
                "endpoint": endpoint,
                "model": model,
            },
        ],
        "voices": {
            "edge-tts": EDGE_VOICES,
            "fish-audio": _fish_voices(config),
        },
    }


def synthesize(text: str, config: dict, out_path: str) -> None:
    """Generate out_path MP3 for text using the configured provider, falling
    back to edge-tts if fish-audio can't be reached."""
    tts = config.get("tts", {}) or {}
    provider = tts.get("provider", "edge-tts")
    voice = tts.get("voice", "")
    if provider == "fish-audio":
        try:
            _fish_tts(text, config, out_path, _fish_voice_id(config, voice))
            return
        except Exception as exc:
            logging.warning("Fish Audio failed, falling back to edge-tts: %s", exc)
            _edge_tts(text, config, out_path, "en-US-AriaNeural")
            return
    _edge_tts(text, config, out_path, voice or "en-US-AriaNeural")


# ─── edge-tts ─────────────────────────────────────────────────────────────────

def _find_edge_tts() -> str:
    which = shutil.which("edge-tts")
    if which:
        return which
    venv_bin = PROJECT_ROOT / ".venv" / "bin" / "edge-tts"
    if venv_bin.exists():
        return str(venv_bin)
    local_bin = Path.home() / ".local" / "bin" / "edge-tts"
    if local_bin.exists():
        return str(local_bin)
    raise RuntimeError("edge-tts not found. Install it with: pip install edge-tts")


def _clean(value: str) -> str:
    return str(value).strip().strip("`'\"")


def _edge_tts(text: str, config: dict, out_path: str, voice: str) -> None:
    tts = config.get("tts", {}) or {}
    rate = _clean(tts.get("rate", "+0%"))
    pitch = _clean(tts.get("pitch", "+0Hz"))
    cmd = [
        _find_edge_tts(), "--voice", voice, "--rate", rate, "--pitch", pitch,
        "--text", text, "--write-media", out_path,
    ]
    result = subprocess.run(cmd, check=False, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"edge-tts failed (exit {result.returncode}): {details}")


# ─── fish-audio ───────────────────────────────────────────────────────────────

def _fish_default_voice(config: dict) -> str:
    voices = _fish_voices(config)
    return voices[0]["id"] if voices else ""


def _looks_like_fish_voice_id(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{32}", str(value or "").strip()))


def _fish_voice_id(config: dict, selected_voice: str) -> str:
    selected_voice = str(selected_voice or "").strip()
    configured = {v["id"] for v in _fish_voices(config)}
    if selected_voice in configured or _looks_like_fish_voice_id(selected_voice):
        return selected_voice
    return _fish_default_voice(config)


def _fish_tts(text: str, config: dict, out_path: str, voice_id: str) -> None:
    api_key = fish_api_key(config)
    if not api_key:
        raise RuntimeError(
            "Fish Audio API key 未配置。请在 config.yaml 的 fish_audio.api_key 填入，"
            "或设置环境变量 FISH_AUDIO_API_KEY。"
        )
    fa = config.get("fish_audio", {}) or {}
    endpoint = fa.get("endpoint") or FISH_ENDPOINT
    model = fa.get("model") or "s2.1-pro-free"
    payload = {"text": text, "format": "mp3", "latency": "normal"}
    if voice_id:
        payload["reference_id"] = voice_id
    if "speed" in fa:
        payload["prosody_speed"] = float(fa["speed"])
    if "pitch" in fa:
        payload["prosody_pitch"] = int(fa["pitch"])
    try:
        resp = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "model": model,
            },
            json=payload,
            timeout=90,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Fish Audio 网络请求失败：{exc}") from exc

    if resp.status_code != 200:
        snippet = resp.text[:300] if resp.text else ""
        raise RuntimeError(
            f"Fish Audio 返回 {resp.status_code}：{snippet or '未知错误'}。"
            "请检查 API key、model、语音 UUID 和额度。"
        )

    content_type = resp.headers.get("Content-Type", "")
    body = resp.content
    if not body or (body[:4] != b"ID3\x03" and body[:2] != b"\xff\xfb" and "audio" not in content_type):
        preview = body[:200].decode("utf-8", errors="replace")
        raise RuntimeError(f"Fish Audio 未返回有效音频。响应预览：{preview}")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(body)
    logging.info("Fish Audio TTS ok: %s (%d bytes) voice=%s", out_path, len(body), voice_id or "default")
