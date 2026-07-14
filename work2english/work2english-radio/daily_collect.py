#!/usr/bin/env python3
"""Collect today's Feishu activity, curate a digest, and optionally generate."""
from __future__ import annotations

import argparse
import logging
from datetime import date

from w2e.runtime import chdir_root, ensure_dirs, ensure_venv_python, setup_logger

ensure_venv_python()

from w2e import daily_digest, feishu_sources, generate, ollama, study
from w2e.config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect and curate daily Feishu activity.")
    parser.add_argument("--date", help="Date to collect (YYYY-MM-DD); defaults to today.")
    parser.add_argument("--collect-only", action="store_true", help="Write the digest without feeding the generator.")
    parser.add_argument("--preview-english", action="store_true", help="Print a bilingual preview without TTS/playback.")
    parser.add_argument("--force-generate", action="store_true", help="Generate immediately, ignoring idle policy.")
    return parser.parse_args()


def print_english_preview(payload: dict) -> None:
    print("\nEnglish preview (no audio generated):")
    for index, item in enumerate(payload.get("items", []), start=1):
        print(f"\n{index}. 中文: {item.get('original_zh', '').strip()}")
        print(f"   EN: {item.get('spoken_english', '').strip()}")
        phrase = item.get("focus_phrase", "").strip()
        note = item.get("note_zh", "").strip()
        if phrase:
            print(f"   Phrase: {phrase}")
        if note:
            print(f"   Note: {note}")


def main() -> None:
    chdir_root()
    ensure_dirs()
    setup_logger("logs/daily_collect.log")
    args = parse_args()
    target_day = date.fromisoformat(args.date) if args.date else date.today()
    config = load_config()
    sources = feishu_sources.collect_sources(target_day)
    counts = feishu_sources.source_counts(sources)
    issues = feishu_sources.source_issues(sources)
    logging.info("Fetched daily Feishu activity: %s", counts)
    print(f"Fetched Feishu activity: {counts}", flush=True)
    for issue in issues:
        print(f"Source warning: {issue.get('source', 'unknown')}: {issue.get('error', 'unknown error')}", flush=True)
    archive_path = feishu_sources.write_source_archive(target_day, sources)
    items = daily_digest.curate_learning_items(sources, config, feishu_sources.current_user_id())
    if not items:
        raise RuntimeError("今天没有找到适合生成英语简报的相关飞书内容。")
    digest_path = daily_digest.write_digest_document(target_day, items, sources, config)
    logging.info("Archived sources at %s and digest at %s", archive_path, digest_path)
    logging.info("Collected daily Feishu activity: %s", counts)
    if args.collect_only:
        print("\n".join(f"- {item}" for item in items))
        print(f"Digest written: {digest_path.relative_to(daily_digest.PROJECT_ROOT)}")
        return
    if args.preview_english:
        if feishu_sources.has_source_issue(sources, "messages") and not args.force_generate:
            print("English preview skipped: messages source failed.")
            print("Use --force-generate only if you accept a preview without chat messages.")
            print(f"Digest written: {digest_path.relative_to(daily_digest.PROJECT_ROOT)}")
            return
        if not ollama.ensure_ollama_running(config):
            raise RuntimeError("Ollama is unavailable; cannot generate English preview.")
        preview_input = daily_digest.render_digest_inbox(target_day, items)
        print_english_preview(study.build_study_payload(preview_input, config))
        print(f"\nDigest written: {digest_path.relative_to(daily_digest.PROJECT_ROOT)}")
        return
    if feishu_sources.has_source_issue(sources, "messages") and not args.force_generate:
        print("Daily Feishu digest collected; generation skipped: messages source failed.")
        print("Use --force-generate only if you accept a digest without chat messages.")
        print(f"Digest written: {digest_path.relative_to(daily_digest.PROJECT_ROOT)}")
        return
    daily_digest.write_digest_to_inbox(target_day, items, config)
    should_generate, reason = daily_digest.generation_decision(config, force=args.force_generate)
    if not should_generate:
        print(f"Daily Feishu digest collected; generation skipped: {reason}")
        print(f"Digest written: {digest_path.relative_to(daily_digest.PROJECT_ROOT)}")
        return
    result = generate.get_coordinator().run_now(config)
    if not result.get("ok"):
        raise RuntimeError(result.get("error") or "generation is already running")
    print(f"Daily Feishu digest collected; Work2English status: {result['status']} ({reason})")


if __name__ == "__main__":
    main()
