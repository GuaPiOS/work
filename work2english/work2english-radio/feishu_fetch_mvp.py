#!/usr/bin/env python3
"""Minimal Feishu acquisition smoke test.

Fetches Feishu sources and prints counts + a few safe previews. It does not
write the Work2English inbox, call Ollama, synthesize audio, or start playback.
"""
from __future__ import annotations

import argparse
from datetime import date

from w2e.runtime import chdir_root, ensure_dirs, ensure_venv_python

ensure_venv_python()

from w2e import feishu_sources
from w2e.feishu import content_to_text


PROVIDER_MAP = {
    "messages": feishu_sources.MessagesProvider,
    "calendar": feishu_sources.CalendarProvider,
    "tasks": feishu_sources.TasksProvider,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal Feishu fetch MVP; no LLM/TTS/playback.")
    parser.add_argument("--date", help="Date to fetch (YYYY-MM-DD); defaults to today.")
    parser.add_argument(
        "--source", choices=["messages", "calendar", "tasks", "all"],
        default="messages", help="Source to fetch; default is messages.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Preview item count per source.")
    parser.add_argument("--archive", action="store_true", help="Write raw source JSON to inbox/sources/.")
    return parser.parse_args()


def preview_text(item: dict) -> str:
    text = content_to_text(item.get("content"))
    if not text:
        text = str(item.get("summary") or item.get("title") or item.get("name") or item.get("id") or "")
    return " ".join(text.split())[:160]


def selected_providers(source: str) -> list[feishu_sources.SourceProvider]:
    if source == "all":
        return list(feishu_sources.ACTIVE_PROVIDERS)
    return [PROVIDER_MAP[source]()]


def main() -> None:
    chdir_root()
    ensure_dirs()
    args = parse_args()
    target_day = date.fromisoformat(args.date) if args.date else date.today()
    sources = feishu_sources.collect_sources(target_day, providers=selected_providers(args.source))
    counts = feishu_sources.source_counts(sources)
    print(f"Feishu fetch MVP date={target_day.isoformat()} source={args.source}")
    print(f"Counts: {counts}")
    for issue in feishu_sources.source_issues(sources):
        print(f"Source warning: {issue.get('source', 'unknown')}: {issue.get('error', 'unknown error')}")
    for name, items in sources.items():
        if name.startswith("_"):
            continue
        print(f"\n[{name}] preview")
        if not items:
            print("- (empty)")
            continue
        for index, item in enumerate(items[: max(args.limit, 0)], start=1):
            text = preview_text(item)
            print(f"{index}. {text or '(no preview text)'}")
    if args.archive:
        path = feishu_sources.write_source_archive(target_day, sources)
        print(f"\nArchive written: {path.relative_to(feishu_sources.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
