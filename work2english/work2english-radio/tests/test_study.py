"""Tests for w2e.study pure logic (parsing, briefing composition, normalization)."""
from w2e import study


def test_parse_daily_items_multiple_sections():
    inbox = (
        "# Work2English Radio Daily Inbox\n\nDate: 2026-07-09\n"
        "\n\n## 09:39 - p2p text\n\nMessage ID: m1\n\n马上我们开始进行今天的汇报。\n"
        "\n\n## 10:57 - p2p text\n\nMessage ID: m2\n\n我认为用户模型很重要。\n"
    )
    items = study.parse_daily_items(inbox)
    assert len(items) == 2
    assert items[0]["time"] == "09:39"
    assert items[0]["message_id"] == "m1"
    assert "汇报" in items[0]["original_zh"]
    assert items[1]["message_id"] == "m2"


def test_parse_daily_items_empty_returns_empty():
    assert study.parse_daily_items("") == []
    assert study.parse_daily_items("   \n\n   ") == []


def test_parse_daily_items_plain_heading_becomes_manual_item():
    # text with no `##` sections is treated as one manual item (by design)
    items = study.parse_daily_items("# only a top-level heading, no sections")
    assert len(items) == 1
    assert items[0]["source"] == "manual"


def test_parse_daily_items_plain_text_becomes_one_manual_item():
    items = study.parse_daily_items("just some loose text")
    assert len(items) == 1
    assert items[0]["source"] == "manual"


def test_split_long_item_under_limit_unchanged():
    item = {"original_zh": "短内容", "source": "x", "time": "10:00", "message_id": "m"}
    out = study.split_long_item(item, max_chars=900)
    assert len(out) == 1
    assert out[0]["original_zh"] == "短内容"


def test_split_long_item_over_limit_splits_and_labels_parts():
    big = "\n\n".join(f"## 块{i}\n内容内容内容内容内容" for i in range(40))
    item = {"original_zh": big, "source": "doc", "time": "10:00", "message_id": "m"}
    out = study.split_long_item(item, max_chars=200)
    assert len(out) > 1
    assert all("part" in it["source"] for it in out)
    assert all(len(it["original_zh"]) <= 200 or it is out[-1] for it in out) or len(out) > 1


def test_compose_daily_briefing_dedupes_and_wraps():
    items = [
        {"spoken_english": "Hello there."},
        {"spoken_english": "Second line."},
        {"spoken_english": "Hello there."},  # dup of item 0
    ]
    out = study.compose_daily_briefing(items)
    assert out.startswith("Here is the latest English briefing.")
    assert "Hello there." in out
    assert "Second line." in out
    # dup appears once
    assert out.count("Hello there.") == 1


def test_compose_daily_briefing_single_item():
    out = study.compose_daily_briefing([{"spoken_english": "Only one."}])
    assert out == "Here is the latest English briefing. Only one."


def test_compose_daily_briefing_empty():
    assert study.compose_daily_briefing([]) == ""
    assert study.compose_daily_briefing([{"spoken_english": ""}]) == ""


def test_normalize_study_payload_preserves_source_order_and_fills_missing():
    sources = [
        {"time": "09:00", "source": "p2p", "message_id": "m1", "original_zh": "原文一"},
        {"time": "10:00", "source": "p2p", "message_id": "m2", "original_zh": "原文二"},
    ]
    generated = {"items": [
        {"spoken_english": "English one.", "focus_phrase": "one", "note_zh": "注一"},
        # second item missing from model output → falls back to original zh
    ]}
    payload = study.normalize_study_payload(generated, sources)
    assert payload["items"][0]["spoken_english"] == "English one."
    assert payload["items"][0]["focus_phrase"] == "one"
    # missing second item falls back to the Chinese source so playback never blanks
    assert payload["items"][1]["spoken_english"] == "原文二"
    assert payload["daily_briefing"].startswith("Here is the latest English briefing.")


def test_today_label_from_input_falls_back_to_today():
    import datetime
    assert study.today_label_from_input("# no date here") == datetime.date.today().isoformat()
    assert study.today_label_from_input("Date: 2024-01-02\n...") == "2024-01-02"
