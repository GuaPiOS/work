"""Tests for w2e.config layered override merge (the single-source-of-truth layer)."""
import json

import pytest

from w2e import config


def _write_cfg(path, body):
    path.write_text(body, encoding="utf-8")


def test_load_config_merges_tts_and_player_overrides(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    _write_cfg(cfg, "level: A2\ntts:\n  provider: edge-tts\n  voice: en-US-AriaNeural\nplayer:\n  mode: auto\n")
    (tmp_path / "tts_settings.json").write_text(json.dumps({"provider": "fish-audio", "voice": "abc"}))
    (tmp_path / "player_mode.json").write_text(json.dumps({"mode": "daily"}))
    monkeypatch.setattr(config, "TTS_SETTINGS_FILE", tmp_path / "tts_settings.json")
    monkeypatch.setattr(config, "PLAYER_MODE_FILE", tmp_path / "player_mode.json")

    c = config.load_config(cfg)
    assert c["tts"]["provider"] == "fish-audio"   # overridden
    assert c["tts"]["voice"] == "abc"             # overridden
    assert c["player"]["mode"] == "daily"         # overridden


def test_load_config_no_overrides_when_runtime_files_absent(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    _write_cfg(cfg, "level: B1\ntts:\n  provider: edge-tts\n  voice: v1\nplayer:\n  mode: auto\n")
    monkeypatch.setattr(config, "TTS_SETTINGS_FILE", tmp_path / "missing1.json")
    monkeypatch.setattr(config, "PLAYER_MODE_FILE", tmp_path / "missing2.json")

    c = config.load_config(cfg)
    assert c["tts"]["provider"] == "edge-tts"
    assert c["player"]["mode"] == "auto"


def test_load_config_invalid_player_mode_override_ignored(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    _write_cfg(cfg, "player:\n  mode: auto\n")
    (tmp_path / "player_mode.json").write_text(json.dumps({"mode": "bogus"}))
    monkeypatch.setattr(config, "PLAYER_MODE_FILE", tmp_path / "player_mode.json")
    monkeypatch.setattr(config, "TTS_SETTINGS_FILE", tmp_path / "missing.json")

    c = config.load_config(cfg)
    assert c["player"]["mode"] == "auto"  # invalid value not applied


def test_load_config_unknown_tts_provider_ignored(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    _write_cfg(cfg, "tts:\n  provider: edge-tts\n  voice: v\n")
    (tmp_path / "tts_settings.json").write_text(json.dumps({"provider": "unknown"}))
    monkeypatch.setattr(config, "TTS_SETTINGS_FILE", tmp_path / "tts_settings.json")
    monkeypatch.setattr(config, "PLAYER_MODE_FILE", tmp_path / "missing.json")

    c = config.load_config(cfg)
    assert c["tts"]["provider"] == "edge-tts"  # unknown provider not applied


def test_load_config_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        config.load_config(tmp_path / "does_not_exist.yaml")


def test_apply_overrides_can_be_disabled(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    _write_cfg(cfg, "player:\n  mode: auto\n")
    (tmp_path / "player_mode.json").write_text(json.dumps({"mode": "daily"}))
    monkeypatch.setattr(config, "PLAYER_MODE_FILE", tmp_path / "player_mode.json")
    monkeypatch.setattr(config, "TTS_SETTINGS_FILE", tmp_path / "missing.json")

    c = config.load_config(cfg, apply_overrides=False)
    assert c["player"]["mode"] == "auto"  # override NOT applied
