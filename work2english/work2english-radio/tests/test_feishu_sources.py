"""Tests for the Feishu acquisition layer (w2e.feishu_sources).

All lark-cli calls go through an injected fake runner, so nothing here depends
on real Feishu permissions or network. Covers: primitive helpers, each active
provider's command/normalization/empty/error paths, per-source error isolation
in collect_sources, reserved (inactive) providers, and the source-archive
contract that keeps real data out of git.
"""
from datetime import date

import pytest

from w2e import feishu_sources
from w2e.feishu_sources import (
    ACTIVE_PROVIDERS,
    ALL_PROVIDERS,
    CalendarProvider,
    CollectContext,
    DocsInMessagesProvider,
    MessagesProvider,
    MinutesProvider,
    TasksProvider,
    collect_sources,
    day_bounds,
    dedupe_by_keys,
    find_list,
    has_source_issue,
    source_counts,
    source_issues,
    write_source_archive,
)


# ─── moved primitives ─────────────────────────────────────────────────────────

def test_day_bounds_uses_full_requested_day():
    start, end = day_bounds(date(2026, 7, 13))
    assert start.startswith("2026-07-13T00:00:00")
    assert end.startswith("2026-07-13T23:59:59")
    assert start[-6] in ("+", "-")


def test_find_list_supports_nested_envelope():
    assert find_list({"data": {"items": [{"id": "one"}]}}, ("items",))[0]["id"] == "one"


def test_find_list_tolerates_bare_list_preferred_keys_and_empty():
    assert find_list([{"id": "a"}], ("items",))[0]["id"] == "a"
    assert find_list({"messages": [{"id": "m"}]}, ("items", "messages"))[0]["id"] == "m"
    assert find_list({"data": {}}, ("items",)) == []
    assert find_list("not a dict", ("items",)) == []


def test_dedupe_by_keys_keeps_first_and_falls_back_to_fingerprint():
    tasks = [{"task_id": "a", "x": 1}, {"task_id": "a", "x": 2}, {"task_id": "b"}]
    out = dedupe_by_keys(tasks, ("task_id",))
    assert [(t["task_id"], t.get("x")) for t in out] == [("a", 1), ("b", None)]
    # keyless records still dedupe by a content fingerprint
    assert len(dedupe_by_keys([{"k": "v"}, {"k": "v"}], ("missing",))) == 1


# ─── providers: command, normalization, empty, error ─────────────────────────

def _ctx(runner, day=date(2026, 7, 13)):
    return CollectContext(
        day=day,
        start="2026-07-13T00:00:00+08:00",
        end="2026-07-13T23:59:59+08:00",
        cli="lark-cli",
        runner=runner,
    )


def test_messages_provider_normalizes_items_envelope_and_command_shape():
    seen = {}

    def runner(args):
        seen["args"] = args
        return {"data": {"items": [{"id": "m1"}, {"id": "m2"}]}}

    out = MessagesProvider().collect(_ctx(runner))
    assert [m["id"] for m in out] == ["m1", "m2"]
    assert "+messages-search" in seen["args"]
    assert "--page-all" in seen["args"]
    assert "--as" in seen["args"] and "user" in seen["args"]


def test_messages_provider_tolerates_envelope_variants():
    def bare(args):
        return [{"id": "m1"}]
    assert MessagesProvider().collect(_ctx(bare))[0]["id"] == "m1"

    def keyed(args):
        return {"messages": [{"id": "m9"}]}
    assert MessagesProvider().collect(_ctx(keyed))[0]["id"] == "m9"


def test_calendar_provider_normalizes_events_and_uses_agenda():
    seen = {}

    def runner(args):
        seen["args"] = args
        return {"items": [{"summary": "站会"}]}

    out = CalendarProvider().collect(_ctx(runner))
    assert out[0]["summary"] == "站会"
    assert "+agenda" in seen["args"]


def test_tasks_provider_merges_created_and_due_and_dedupes():
    calls = {"n": 0}
    payloads = [
        {"items": [{"task_id": "t1", "tag": "created"}]},
        {"items": [{"task_id": "t1", "tag": "due"}, {"task_id": "t2", "tag": "due"}]},
    ]

    def runner(args):
        i = calls["n"]
        calls["n"] += 1
        return payloads[i]

    out = TasksProvider().collect(_ctx(runner))
    assert calls["n"] == 2  # created + due
    assert [t["task_id"] for t in out] == ["t1", "t2"]  # t1 deduped
    assert out[0]["tag"] == "created"  # dedupe keeps the first occurrence


def test_provider_empty_or_flat_envelope_yields_empty_list():
    def runner(args):
        return {"data": {}}
    assert MessagesProvider().collect(_ctx(runner)) == []
    assert CalendarProvider().collect(_ctx(runner)) == []
    assert TasksProvider().collect(_ctx(runner)) == []


def test_provider_surfaces_cli_error_so_collect_can_isolate_it():
    def runner(args):
        raise RuntimeError("non-zero exit")
    with pytest.raises(RuntimeError):
        MessagesProvider().collect(_ctx(runner))


# ─── orchestration & per-source isolation ─────────────────────────────────────

def test_collect_sources_returns_canonical_keys_by_default():
    def runner(args):
        if "+messages-search" in args:
            return {"items": [{"id": "m"}]}
        if "+agenda" in args:
            return {"items": [{"summary": "e"}]}
        return {"items": [{"task_id": "t"}]}
    sources = collect_sources(date(2026, 7, 13), runner=runner, cli="lark-cli")
    assert set(sources) == {"messages", "calendar", "tasks"}
    assert sources["messages"][0]["id"] == "m"


def test_collect_sources_isolates_failing_provider():
    def runner(args):
        if "+messages-search" in args:
            raise RuntimeError("messages cli down")
        if "+agenda" in args:
            return {"items": [{"summary": "站会"}]}
        return {"items": [{"task_id": "t1"}]}
    sources = collect_sources(date(2026, 7, 13), runner=runner, cli="lark-cli")
    assert sources["messages"] == []          # failed → isolated, not fatal
    assert sources["calendar"][0]["summary"] == "站会"
    assert sources["tasks"][0]["task_id"] == "t1"
    assert source_issues(sources) == [{"source": "messages", "error": "messages cli down"}]
    assert has_source_issue(sources, "messages") is True
    assert has_source_issue(sources, "calendar") is False


def test_source_counts_hides_issues_and_includes_extra_sources():
    counts = source_counts({
        "messages": [{"id": "m"}],
        "calendar": [],
        "tasks": [],
        "docs": [{"url": "u"}],
        "_issues": [{"source": "tasks", "error": "x"}],
    })
    assert counts == {"messages": 1, "calendar": 0, "tasks": 0, "docs": 1}


def test_collect_sources_skips_reserved_providers_in_full_registry():
    def runner(args):
        return {"items": [{"id": "x"}]}
    sources = collect_sources(date(2026, 7, 13), providers=ALL_PROVIDERS, runner=runner, cli="lark-cli")
    assert set(sources) == {"messages", "calendar", "tasks"}  # docs/minutes not fetched


def test_reserved_providers_are_inactive_and_no_op():
    for provider in (DocsInMessagesProvider(), MinutesProvider()):
        assert provider.active is False
        assert provider.collect(_ctx(lambda a: {})) == []
        assert provider.name in ("docs", "minutes")


def test_active_registry_contains_only_the_three_active_sources():
    assert [p.name for p in ACTIVE_PROVIDERS] == ["messages", "calendar", "tasks"]
    assert all(p.active for p in ACTIVE_PROVIDERS)


# ─── source archive (real data must stay out of git) ──────────────────────────

def test_write_source_archive_writes_json_named_by_day(tmp_path, monkeypatch):
    monkeypatch.setattr(feishu_sources, "SOURCE_ARCHIVE_DIR", tmp_path / "sources")
    sources = {"messages": [{"id": "m1"}], "calendar": [], "tasks": []}
    path = write_source_archive(date(2026, 7, 13), sources)
    assert path.name == "feishu-2026-07-13.json"
    import json
    assert json.loads(path.read_text(encoding="utf-8"))["messages"][0]["id"] == "m1"


def test_source_archive_dir_is_the_gitignored_location():
    # inbox/sources/* is git-ignored except .gitkeep, so real Feishu data is
    # never committed. Lock the directory contract so a future move can't
    # silently start landing raw data somewhere tracked.
    archive_dir = feishu_sources.SOURCE_ARCHIVE_DIR
    assert archive_dir.parent.name == "inbox"
    assert archive_dir.name == "sources"
