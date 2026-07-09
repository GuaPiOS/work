"""Tests for w2e.playback mode resolution (the area that had the dead override bug)."""
from w2e import playback


def _payload(n_latest=2, n_older=1):
    items = []
    for i in range(n_older):
        items.append({"message_id": "old", "spoken_english": f"old {i}", "audio": f"audio/item_{i:03d}.mp3"})
    for i in range(n_latest):
        items.append({"message_id": "latest", "spoken_english": f"new {i}", "audio": "audio/x.mp3"})
    return {"daily_briefing": "...", "items": items}


def test_latest_batch_items_groups_by_last_message_id():
    items = _payload(n_latest=3, n_older=2)["items"]
    batch = playback.latest_batch_items(items)
    assert len(batch) == 3
    assert all(it["message_id"] == "latest" for it in batch)


def test_latest_batch_items_no_message_id_returns_last_only():
    items = [{"message_id": "", "spoken_english": "a"}, {"message_id": "", "spoken_english": "b"}]
    assert len(playback.latest_batch_items(items)) == 1


def test_select_playback_items_daily_returns_all():
    payload = _payload(n_latest=2, n_older=2)
    mode, sel = playback.select_playback_items(payload, {"player": {"mode": "daily"}})
    assert mode == "daily"
    assert len(sel) == 4


def test_select_playback_items_auto_multi_returns_latest_batch():
    payload = _payload(n_latest=3, n_older=2)
    mode, sel = playback.select_playback_items(payload, {"player": {"mode": "auto"}})
    assert mode == "list"  # auto + multi-part → list
    assert len(sel) == 3
    assert all(it["message_id"] == "latest" for it in sel)


def test_select_playback_items_auto_single_returns_one():
    payload = _payload(n_latest=1, n_older=2)
    mode, sel = playback.select_playback_items(payload, {"player": {"mode": "auto"}})
    assert mode == "single"
    assert len(sel) == 1


def test_select_playback_items_single_returns_latest_one():
    payload = _payload(n_latest=3, n_older=2)
    mode, sel = playback.select_playback_items(payload, {"player": {"mode": "single"}})
    assert mode == "single"
    assert len(sel) == 1
    assert sel[0]["message_id"] == "latest"


def test_select_playback_items_empty():
    assert playback.select_playback_items({"items": []}, {"player": {"mode": "daily"}}) == ("single", [])


def test_build_player_control_has_signature_and_mode(tmp_path, monkeypatch):
    # Avoid real filesystem checks by pointing output_audio at a nonexistent path.
    config = {"output_audio": "output/does_not_exist.mp3", "player": {"mode": "daily", "interval_seconds": 3, "loop": True}}
    payload = _payload(n_latest=2, n_older=1)
    control = playback.build_player_control("2026-07-09", payload, config)
    assert control["mode"] in ("daily", "list", "single")
    assert control["interval_seconds"] == 3
    assert control["loop"] is True
    assert isinstance(control["signature"], str) and control["signature"]
    assert "updated_at" in control


def test_build_player_control_empty_payload_falls_back_to_main_audio(tmp_path):
    # main audio missing too → empty playlist, but control still well-formed
    config = {"output_audio": "output/missing.mp3", "player": {"mode": "daily", "interval_seconds": 5, "loop": True}}
    control = playback.build_player_control("2026-07-09", None, config)
    assert control["playlist"] == []
    assert control["signature"]
