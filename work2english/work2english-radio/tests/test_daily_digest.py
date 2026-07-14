from datetime import date

from w2e import daily_digest, feishu, study


def test_compact_sources_extracts_message_text():
    sources = {
        "messages": [{
            "create_time": "1", "chat_name": "项目群",
            "sender": {"name": "小李"}, "content": '{"text":"进度正常"}',
        }],
        "calendar": [],
        "tasks": [],
    }
    compact = daily_digest.compact_sources(sources)
    assert "进度正常" in compact
    assert "项目群" in compact


def test_select_relevant_messages_keeps_group_context_and_p2p():
    group = [
        {"chat_id": "g", "chat_type": "group", "msg_type": "text", "create_time": str(i),
         "sender": {"id": "me" if i == 2 else "other"}, "content": f"消息{i}"}
        for i in range(6)
    ]
    p2p = {"chat_id": "p", "chat_type": "p2p", "msg_type": "text", "create_time": "9",
           "sender": {"id": "other"}, "content": "私聊消息"}
    selected = daily_digest.select_relevant_messages(group + [p2p], "me", context_radius=1)
    assert [x["content"] for x in selected] == ["消息1", "消息2", "消息3", "私聊消息"]


def test_select_relevant_messages_ignores_unrelated_group_noise():
    noise = [{"chat_id": "g", "chat_type": "group", "msg_type": "text", "create_time": "1",
              "sender": {"id": "other"}, "content": "群公告"}]
    assert daily_digest.select_relevant_messages(noise, "me") == []


def test_summary_items_limits_and_deduplicates():
    assert daily_digest.summary_items("- 事项一\n- 事项一\n* 事项二", limit=5) == ["事项一", "事项二"]


def test_build_digest_items_balances_multiple_chats():
    messages = []
    for chat, timestamp in (("a", "3"), ("b", "4"), ("c", "5")):
        messages.append({"chat_id": chat, "chat_type": "p2p", "msg_type": "text",
                         "create_time": timestamp, "sender": {"id": "other"},
                         "content": f"来自聊天{chat}的重要工作消息"})
    items = daily_digest.build_digest_items(
        {"messages": messages, "calendar": [], "tasks": []}, "me", limit=3,
    )
    assert items == ["来自聊天c的重要工作消息", "来自聊天b的重要工作消息", "来自聊天a的重要工作消息"]


def test_build_digest_items_uses_calendar_when_space_available():
    items = daily_digest.build_digest_items(
        {"messages": [], "calendar": [{"summary": "产品周会"}], "tasks": []}, "me", limit=5,
    )
    assert items == ["今天的日程包括：产品周会。"]


def test_build_digest_items_skips_system_notices():
    messages = [
        {"chat_id": "a", "chat_type": "p2p", "msg_type": "text", "create_time": "3",
         "sender": {"id": "other"}, "content": "您的运费询价PI260615059于2026-07-15到期，请及时前往Odoo处理。"},
        {"chat_id": "b", "chat_type": "p2p", "msg_type": "text", "create_time": "4",
         "sender": {"id": "other"}, "content": "锁机问题需要明天尽快验证，避免我们误判状态。"},
    ]
    items = daily_digest.build_digest_items(
        {"messages": messages, "calendar": [], "tasks": []}, "me", limit=3,
    )
    assert items == ["锁机问题需要明天尽快验证，避免我们误判状态。"]


def test_build_digest_items_removes_obvious_mentions():
    messages = [
        {"chat_id": "a", "chat_type": "p2p", "msg_type": "text", "create_time": "3",
         "sender": {"id": "other"}, "content": "@Easnow.Cai @Xiaokai.Liu 北美第一波实勘反馈来了"},
    ]
    items = daily_digest.build_digest_items(
        {"messages": messages, "calendar": [], "tasks": []}, "me", limit=3,
    )
    assert items == ["北美第一波实勘反馈来了"]


def test_write_digest_document_renders_level_and_items(tmp_path, monkeypatch):
    monkeypatch.setattr(daily_digest, "DIGEST_DIR", tmp_path / "digest")
    sources = {"messages": [{"id": "m1"}], "calendar": [], "tasks": []}
    digest = daily_digest.write_digest_document(
        date(2026, 7, 13), ["今天讨论了发版计划。"], sources,
        {"level": "A2", "daily_digest": {"target_level": "B1"}},
    )
    text = digest.read_text(encoding="utf-8")
    assert "A2->B1" in text
    assert "今天讨论了发版计划。" in text
    assert "not a full work report" in text


def test_write_digest_document_renders_source_issues(tmp_path, monkeypatch):
    monkeypatch.setattr(daily_digest, "DIGEST_DIR", tmp_path / "digest")
    sources = {
        "messages": [],
        "calendar": [{"summary": "产品周会"}],
        "tasks": [],
        "_issues": [{"source": "messages", "error": "permission denied"}],
    }
    digest = daily_digest.write_digest_document(
        date(2026, 7, 13), ["今天的日程包括：产品周会。"], sources,
        {"level": "A2", "daily_digest": {"target_level": "B1"}},
    )
    text = digest.read_text(encoding="utf-8")
    assert "## Source Issues" in text
    assert "messages: permission denied" in text


def test_render_digest_inbox_can_be_parsed_for_preview():
    inbox = daily_digest.render_digest_inbox(date(2026, 7, 13), ["今天讨论了发版计划。"])
    items = study.parse_daily_items(inbox)
    assert len(items) == 1
    assert items[0]["source"] == "daily digest"
    assert items[0]["original_zh"] == "今天讨论了发版计划。"


def test_write_digest_to_inbox_replaces_old_digest_and_preserves_manual(tmp_path, monkeypatch):
    input_file = tmp_path / "feishu_raw.md"
    daily_dir = tmp_path / "daily"
    monkeypatch.setattr(feishu, "DAILY_DIR", daily_dir)
    input_file.write_text(
        "# Work2English Radio Daily Inbox\n\nDate: 2026-07-13\n"
        "\n\n## 09:00 - p2p text\n\nMessage ID: m1\n\n手动发送的句子。\n"
        "\n\n## 10:00 - daily digest\n\nMessage ID: old\n\n旧摘要。\n",
        encoding="utf-8",
    )
    config = {"input_file": str(input_file), "collector": {"max_daily_chars": 20000}}
    daily_digest.write_digest_to_inbox(date(2026, 7, 13), ["新的每日摘要。"], config)
    content = input_file.read_text(encoding="utf-8")
    assert "手动发送的句子。" in content
    assert "旧摘要。" not in content
    assert "新的每日摘要。" in content
    assert "daily digest" in content


def test_generation_decision_respects_idle_policy(monkeypatch):
    config = {"daily_digest": {"generation_policy": "idle", "min_idle_seconds": 300}}
    monkeypatch.setattr(daily_digest, "system_idle_seconds", lambda: 301)
    assert daily_digest.generation_decision(config)[0] is True
    monkeypatch.setattr(daily_digest, "system_idle_seconds", lambda: 120)
    should_generate, reason = daily_digest.generation_decision(config)
    assert should_generate is False
    assert "waiting" in reason


def test_generation_decision_can_be_forced_when_idle_unknown(monkeypatch):
    config = {"daily_digest": {"generation_policy": "idle"}}
    monkeypatch.setattr(daily_digest, "system_idle_seconds", lambda: None)
    assert daily_digest.generation_decision(config)[0] is False
    assert daily_digest.generation_decision(config, force=True) == (True, "forced")
