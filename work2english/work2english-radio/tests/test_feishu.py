"""Tests for w2e.feishu parsing + dedupe helpers."""
from w2e import feishu


def test_content_to_text_string_passthrough():
    assert feishu.content_to_text("plain text") == "plain text"


def test_content_to_text_json_string_extracts_text():
    assert feishu.content_to_text('{"text":"hello"}') == "hello"


def test_content_to_text_nested_post_payload():
    payload = '{"content":{"zh_cn":{"title":"标题","content":[{"text":"行一"},{"text":"行二"}]}}}'
    out = feishu.content_to_text(payload)
    assert "标题" in out and "行一" in out and "行二" in out


def test_content_to_text_none_and_empty():
    assert feishu.content_to_text(None) == ""
    assert feishu.content_to_text("   ") == ""


def test_strip_bot_addressing_read_command():
    assert feishu.strip_bot_addressing("/read 这是要读的内容") == "这是要读的内容"


def test_strip_bot_addressing_doc_command():
    assert feishu.strip_bot_addressing("/doc https://x.feishu.cn/docx/abc") == "https://x.feishu.cn/docx/abc"


def test_strip_bot_addressing_bare_command_yields_empty():
    assert feishu.strip_bot_addressing("/read") == ""
    assert feishu.strip_bot_addressing("/doc") == ""


def test_strip_bot_addressing_leading_at():
    assert feishu.strip_bot_addressing("@bot hello") == "hello"


def test_find_doc_url_picks_supported_pattern():
    text = "see https://xxx.feishu.cn/docx/abc123 and also https://yyy.feishu.cn/sheets/z"
    url = feishu.find_doc_url(text, ["/docx/", "/doc/", "/wiki/"])
    assert url == "https://xxx.feishu.cn/docx/abc123"


def test_find_doc_url_none_when_no_supported_pattern():
    assert feishu.find_doc_url("https://x.feishu.cn/sheets/abc", ["/docx/", "/doc/", "/wiki/"]) == ""


def test_group_message_addressed_p2p_always_addressed():
    assert feishu.group_message_is_addressed_to_bot({"chat_type": "p2p"}, "hi") is True


def test_group_message_plain_text_not_addressed():
    assert feishu.group_message_is_addressed_to_bot({"chat_type": "group"}, "just chatting") is False


def test_group_message_with_at_is_addressed():
    # non-empty mentions (a real @-mention) → addressed; an empty dict is falsy and does not count
    assert feishu.group_message_is_addressed_to_bot({"chat_type": "group", "mentions": {"u1": {}}}, "x") is True
    # <at> tag lives in the event content (real flow); the function scans the serialized event JSON
    assert feishu.group_message_is_addressed_to_bot({"chat_type": "group", "content": "<at>bot</at> hi"}, "hi") is True
    assert feishu.group_message_is_addressed_to_bot({"chat_type": "group", "mentions": {}}, "x") is False


def test_group_message_with_read_command_is_addressed():
    assert feishu.group_message_is_addressed_to_bot({"chat_type": "group"}, "/read hello") is True


def test_dedupe_fingerprint_stable_for_same_inputs():
    event = {"chat_id": "c1", "sender_id": "s1", "message_type": "text"}
    a = feishu.dedupe_fingerprint(event, "Hello World")
    b = feishu.dedupe_fingerprint(event, "hello world")  # normalized → same fingerprint
    assert a == b


def test_dedupe_fingerprint_differs_by_chat():
    e1 = {"chat_id": "c1", "sender_id": "s1", "message_type": "text"}
    e2 = {"chat_id": "c2", "sender_id": "s1", "message_type": "text"}
    assert feishu.dedupe_fingerprint(e1, "hi") != feishu.dedupe_fingerprint(e2, "hi")


def test_truncate_input():
    assert feishu.truncate_input("短", 10) == "短"
    assert len(feishu.truncate_input("x" * 100, 10)) == 10


def test_append_daily_inbox_keeps_all_same_day_bot_messages(tmp_path, monkeypatch):
    input_file = tmp_path / "feishu_raw.md"
    daily_dir = tmp_path / "daily"
    monkeypatch.setattr(feishu, "DAILY_DIR", daily_dir)
    config = {
        "input_file": str(input_file),
        "collector": {"daily_rollup": True, "max_daily_chars": 20000},
    }

    feishu.append_daily_inbox("第一句", config, {"collected_date": "2026-07-16", "message_id": "m1"})
    feishu.append_daily_inbox("第二句", config, {"collected_date": "2026-07-16", "message_id": "m2"})

    content = input_file.read_text(encoding="utf-8")
    assert "第一句" in content
    assert "第二句" in content
    assert "Message ID: m1" in content
    assert "Message ID: m2" in content
