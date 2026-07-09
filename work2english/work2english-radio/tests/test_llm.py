"""Tests for w2e.llm JSON extraction + text cleaning."""
from w2e import llm


def test_extract_json_object_clean():
    assert llm.extract_json_object('{"items":[]}') == {"items": []}


def test_extract_json_object_fenced():
    assert llm.extract_json_object('```json\n{"a": 1}\n```') == {"a": 1}
    assert llm.extract_json_object('```\n{"b": 2}\n```') == {"b": 2}


def test_extract_json_object_with_surrounding_text():
    assert llm.extract_json_object('sure, here you go: {"a": 1, "b": [1,2]} done') == {"a": 1, "b": [1, 2]}


def test_extract_json_object_strips_think_block():
    assert llm.extract_json_object('<think>reasoning</think>{"ok": true}') == {"ok": True}


def test_prepare_text_for_model_strips_tags_and_cite():
    raw = '<p>hello <cite>x</cite> world <div>line</div> ~~struck~~</p>'
    out = llm.prepare_text_for_model(raw)
    assert "<" not in out and ">" not in out
    assert "hello" in out and "world" in out and "line" in out
    assert "~~" not in out  # strikethrough markers removed (text kept)
    assert "x" not in out  # cite content removed


def test_prepare_text_for_model_truncates_with_marker():
    big = "a" * 500
    out = llm.prepare_text_for_model(big, max_chars=100)
    assert out.endswith("[content truncated]")
    assert len(out) <= 120  # 100 chars + marker


def test_strip_thinking_removes_block():
    assert llm.strip_thinking("<think>hidden</think>visible") == "visible"
    assert llm.strip_thinking("no think tag") == "no think tag"


def test_build_study_prompt_includes_level_and_count():
    items = [{"original_zh": "你好"}, {"original_zh": "再见"}]
    prompt = llm.build_study_prompt("B2", items)
    assert "B2" in prompt
    assert "2 items" in prompt
    assert "你好" in prompt
    assert '"id": 1' in prompt or '"id":1' in prompt
