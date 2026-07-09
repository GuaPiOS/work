"""Single source of truth for runtime config.

Layered (later wins): config.yaml  ←  runtime/tts_settings.json  ←
runtime/player_mode.json  ←  process env. Every entry point and the UI server
go through load_config(), so "which voice / mode will actually be used" always
has one answer — and the collector path now respects UI-selected overrides too
(previously it ignored player_mode.json, a latent bug).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

from .runtime import PROJECT_ROOT, RUNTIME_DIR

CONFIG_FILE = PROJECT_ROOT / "config.yaml"
CONFIG_EXAMPLE = PROJECT_ROOT / "config.example.yaml"
TTS_SETTINGS_FILE = RUNTIME_DIR / "tts_settings.json"
PLAYER_MODE_FILE = RUNTIME_DIR / "player_mode.json"

PLAYER_MODES = ("auto", "single", "list", "daily")
TTS_PROVIDERS = ("edge-tts", "fish-audio")


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _merge_tts_settings(config: dict) -> None:
    settings = _read_json(TTS_SETTINGS_FILE)
    if not settings:
        return
    tts = config.setdefault("tts", {})
    provider = str(settings.get("provider", "")).strip()
    voice = str(settings.get("voice", "")).strip()
    if provider in TTS_PROVIDERS:
        tts["provider"] = provider
    if voice:
        tts["voice"] = voice


def _merge_player_mode(config: dict) -> None:
    mode = str(_read_json(PLAYER_MODE_FILE).get("mode", "")).strip().lower()
    if mode in PLAYER_MODES:
        config.setdefault("player", {})["mode"] = mode


def _merge_env(config: dict) -> None:
    """Env overrides (e.g. FISH_AUDIO_API_KEY) are read lazily by the consumers
    that need them (tts.fish_api_key), so nothing to merge here yet — kept as a
    hook for future env-first config."""
    return None


def load_config(path: str | Path | None = None, apply_overrides: bool = True) -> dict[str, Any]:
    config_path = Path(path) if path else CONFIG_FILE
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    if not config_path.exists():
        raise FileNotFoundError(
            f"config not found: {config_path}. Copy config.example.yaml to config.yaml."
        )
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if apply_overrides:
        _merge_tts_settings(config)
        _merge_player_mode(config)
        _merge_env(config)
    return config


def player_pid_file(config: dict) -> Path:
    return PROJECT_ROOT / config.get("player", {}).get("pid_file", "runtime/player.pid")
