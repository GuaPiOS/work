from datetime import date

from w2e import content_pipeline


def test_build_candidates_filters_mentions_and_system_notices():
    sources = {
        "messages": [
            {
                "message_id": "m1",
                "chat_id": "a",
                "chat_type": "p2p",
                "msg_type": "text",
                "create_time": "3",
                "sender": {"id": "other"},
                "content": "@Easnow.Cai 锁机问题需要明天尽快验证，避免我们误判状态。",
            },
            {
                "message_id": "m2",
                "chat_id": "b",
                "chat_type": "p2p",
                "msg_type": "text",
                "create_time": "4",
                "sender": {"id": "other"},
                "content": "您的运费询价PI260615059于2026-07-15到期，请及时前往Odoo处理。",
            },
        ],
        "calendar": [],
        "tasks": [],
    }
    candidates = content_pipeline.build_candidates(sources, "me", limit=10, recommended_limit=3)
    assert [candidate["text"] for candidate in candidates] == ["锁机问题需要明天尽快验证，避免我们误判状态。"]
    assert candidates[0]["recommended"] is True
    assert "工作信号" in candidates[0]["tags"]


def test_selected_texts_uses_checked_candidates_in_candidate_order():
    candidates = [
        {"id": "a", "text": "第一条", "recommended": True},
        {"id": "b", "text": "第二条", "recommended": True},
        {"id": "c", "text": "第三条", "recommended": False},
    ]
    assert content_pipeline.selected_texts(candidates, ["c", "a"], limit=3) == ["第一条", "第三条"]
    assert content_pipeline.selected_texts(candidates, limit=3) == ["第一条", "第二条"]


def test_build_candidates_filters_urls_and_order_status_notices():
    sources = {
        "messages": [
            {"message_id": "m1", "chat_id": "a", "chat_type": "p2p", "msg_type": "text",
             "create_time": "1", "sender": {"id": "me"},
             "content": "https://fjdynamics.feishu.cn/docx/example"},
            {"message_id": "m2", "chat_id": "a", "chat_type": "p2p", "msg_type": "text",
             "create_time": "2", "sender": {"id": "other"},
             "content": "AGLANTIS PTY LTD - 【PI260714035】签署状态更新为：待客户签署，请及时关注，转为销售订单"},
            {"message_id": "m3", "chat_id": "a", "chat_type": "p2p", "msg_type": "text",
             "create_time": "3", "sender": {"id": "me"},
             "content": "这个问题需要明天确认一下处理方案。"},
        ],
        "calendar": [],
        "tasks": [],
    }
    candidates = content_pipeline.build_candidates(sources, "me", limit=10, recommended_limit=3)
    assert [candidate["text"] for candidate in candidates] == ["这个问题需要明天确认一下处理方案。"]


def test_write_candidate_pool(tmp_path, monkeypatch):
    monkeypatch.setattr(content_pipeline, "CANDIDATE_DIR", tmp_path)
    path = content_pipeline.write_candidate_pool(date(2026, 7, 14), [{"id": "a", "text": "内容"}])
    assert path.name == "2026-07-14.json"
    assert "内容" in path.read_text(encoding="utf-8")
