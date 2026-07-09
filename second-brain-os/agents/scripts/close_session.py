#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2].resolve()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def resolve_project(project: str) -> Path:
    path = Path(project)
    if not path.is_absolute():
        path = ROOT / project
    path = path.resolve()
    if not path.is_dir():
        raise SystemExit(f"Project directory not found: {project}")
    return path


def append_jsonl(path: Path, payload: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Close a project session by writing manifest and worklog entries.")
    parser.add_argument("--project", required=True, help="Project path relative to the Second Brain OS root.")
    parser.add_argument("--goal", required=True, help="Session goal.")
    parser.add_argument("--summary", required=True, help="Session summary.")
    parser.add_argument("--carry-forward", default="", help="What should continue next session.")
    parser.add_argument("--files-read", default="", help="Comma-separated list of files read.")
    parser.add_argument("--files-written", default="", help="Comma-separated list of files written.")
    parser.add_argument("--artifact-refs", default="", help="Comma-separated list of artifact IDs or paths.")
    parser.add_argument("--next-step", default="", help="Immediate next step.")
    parser.add_argument("--actor", default="guapi")
    args = parser.parse_args()

    project_dir = resolve_project(args.project)
    timestamp = now_iso()
    month_file = project_dir / "context" / "manifests" / f"{datetime.now().strftime('%Y-%m')}.jsonl"
    worklog_file = project_dir / "worklog.jsonl"

    append_jsonl(
        month_file,
        {
            "timestamp": timestamp,
            "goal": args.goal,
            "files_read": split_csv(args.files_read),
            "files_written": split_csv(args.files_written),
            "summary": args.summary,
            "carry_forward": args.carry_forward,
        },
    )

    append_jsonl(
        worklog_file,
        {
            "timestamp": timestamp,
            "actor": args.actor,
            "action": "close_session",
            "summary": args.summary,
            "artifact_refs": split_csv(args.artifact_refs),
            "next_step": args.next_step or args.carry_forward,
        },
    )

    pad_files = [path.name for path in (project_dir / "context" / "pad").glob("*") if path.is_file()]
    print(f"Wrote manifest: {month_file.relative_to(ROOT)}")
    print(f"Wrote worklog entry: {worklog_file.relative_to(ROOT)}")
    if pad_files:
        print("Pad cleanup still needed for:")
        for name in pad_files:
            print(f"  - {name}")
    else:
        print("Pad cleanup: clear")
    print("Reminder: update next-actions.md, session-brief.md, current-readset.md, compact-state.md, and handoff.md if the session changed project direction.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
