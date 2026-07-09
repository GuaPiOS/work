#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DIR = ROOT / "projects" / "active"

REQUIRED_FILES = (
    "project.yaml",
    "session-brief.md",
    "workflow.md",
    "brief.md",
    "scope.md",
    "plan.md",
    "status.md",
    "next-actions.md",
    "open-questions.md",
    "worklog.jsonl",
    "context/routing/read-policy.yaml",
    "context/routing/current-readset.md",
    "context/summaries/compact-state.md",
    "context/summaries/working-summary.md",
    "context/summaries/rolling-summary.md",
    "context/summaries/handoff.md",
    "artifacts/registry.jsonl",
    "memory/facts.jsonl",
    "memory/decisions.jsonl",
    "memory/lessons.jsonl",
    "memory/procedures.jsonl",
)

REQUIRED_DIRS = (
    "context/inputs",
    "context/sources",
    "context/research",
    "context/tool_outputs",
    "context/pad",
    "context/routing",
    "context/summaries",
    "context/manifests",
    "artifacts/current",
    "artifacts/archive",
    "reviews",
)

REQUIRED_PROJECT_KEYS = (
    "id",
    "slug",
    "title",
    "category",
    "domain",
    "status",
    "current_phase",
    "objective",
    "success_criteria",
    "stakeholder",
    "owner",
    "priority",
    "automation_profile",
    "default_read_policy",
    "current_readset",
    "compact_state",
    "working_summary",
    "artifact_registry",
    "primary_artifact",
    "created_at",
    "updated_at",
    "tags",
)


def simple_yaml_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line or raw_line.startswith(" ") or raw_line.startswith("#"):
            continue
        if ":" not in raw_line:
            continue
        key = raw_line.split(":", 1)[0].strip()
        keys.add(key)
    return keys


def first_jsonl_line(path: Path) -> dict[str, object] | None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        return json.loads(line)
    return None


def placeholder_warnings(project_dir: Path) -> list[str]:
    warnings: list[str] = []
    status_text = (project_dir / "status.md").read_text(encoding="utf-8")
    if "待定义" in status_text or "待开始" in status_text:
        warnings.append("status.md still contains placeholders.")

    session_text = (project_dir / "session-brief.md").read_text(encoding="utf-8")
    if "待定义" in session_text:
        warnings.append("session-brief.md still contains placeholders.")

    compact_text = (project_dir / "context/summaries/compact-state.md").read_text(encoding="utf-8")
    if "待定义" in compact_text:
        warnings.append("compact-state.md still contains placeholders.")

    readset_text = (project_dir / "context/routing/current-readset.md").read_text(encoding="utf-8")
    if "待定义" in readset_text:
        warnings.append("current-readset.md still contains placeholders.")

    return warnings


def validate_project(project_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED_FILES:
        if not (project_dir / relative).exists():
            errors.append(f"Missing file: {relative}")

    for relative in REQUIRED_DIRS:
        if not (project_dir / relative).is_dir():
            errors.append(f"Missing directory: {relative}")

    project_yaml = project_dir / "project.yaml"
    if project_yaml.exists():
        keys = simple_yaml_keys(project_yaml)
        missing_keys = [key for key in REQUIRED_PROJECT_KEYS if key not in keys]
        for key in missing_keys:
            errors.append(f"project.yaml missing key: {key}")

    for relative in (
        "worklog.jsonl",
        "artifacts/registry.jsonl",
        "memory/facts.jsonl",
        "memory/decisions.jsonl",
        "memory/lessons.jsonl",
        "memory/procedures.jsonl",
    ):
        path = project_dir / relative
        if path.exists():
            try:
                schema = first_jsonl_line(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative} schema line is not valid JSON: {exc}")
                continue
            if not schema or "_schema" not in schema:
                errors.append(f"{relative} missing schema line.")

    pad_files = [path for path in (project_dir / "context/pad").glob("*") if path.is_file()]
    if pad_files:
        warnings.append(f"context/pad contains {len(pad_files)} file(s); confirm cleanup classification.")

    warnings.extend(placeholder_warnings(project_dir))
    return errors, warnings


def discover_projects(requested: str | None) -> list[Path]:
    if requested:
        path = Path(requested)
        if not path.is_absolute():
            path = ROOT / requested
        if path.is_dir():
            return [path]
        raise SystemExit(f"Project directory not found: {requested}")

    return sorted(
        path
        for path in ACTIVE_DIR.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one project or all active projects.")
    parser.add_argument("project", nargs="?", help="Project path. Defaults to all active projects.")
    args = parser.parse_args()

    projects = discover_projects(args.project)
    if not projects:
        print("No active projects found.")
        return 0

    failed = False
    for project_dir in projects:
        errors, warnings = validate_project(project_dir)
        print(f"[{project_dir.name}]")
        if not errors and not warnings:
            print("  OK")
            continue
        for error in errors:
            print(f"  ERROR: {error}")
        for warning in warnings:
            print(f"  WARN: {warning}")
        if errors:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
