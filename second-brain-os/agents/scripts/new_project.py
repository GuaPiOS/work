#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = ROOT / "projects" / "_templates"
ACTIVE_DIR = ROOT / "projects" / "active"
INDEX_FILE = ROOT / "projects" / "index.jsonl"

VALID_CATEGORIES = {"delivery", "build", "research", "operations", "learning", "writing"}
VALID_DOMAINS = {"work", "startup", "personal", "learning", "other"}
VALID_AUTOMATION = {"manual", "assisted", "delegated"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "new-project"


def project_id_from_slug(slug: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"proj_{stamp}_{slug}"


def render_text(content: str, replacements: dict[str, str]) -> str:
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def copy_template_files(template_dir: Path, destination: Path, replacements: dict[str, str]) -> None:
    for source in template_dir.rglob("*"):
        if source.is_dir():
            continue
        relative = source.relative_to(template_dir)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        rendered = render_text(source.read_text(encoding="utf-8"), replacements)
        target.write_text(rendered, encoding="utf-8")


def ensure_project_dirs(project_dir: Path) -> None:
    for relative in (
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
        "memory",
    ):
        (project_dir / relative).mkdir(parents=True, exist_ok=True)


def append_index_entry(entry: dict[str, str]) -> None:
    with INDEX_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new Second Brain OS project.")
    parser.add_argument("--title", required=True, help="Human-readable project title.")
    parser.add_argument("--slug", help="Directory name. Defaults to a slugified title.")
    parser.add_argument("--category", required=True, choices=sorted(VALID_CATEGORIES))
    parser.add_argument("--domain", required=True, choices=sorted(VALID_DOMAINS))
    parser.add_argument("--automation-profile", default="assisted", choices=sorted(VALID_AUTOMATION))
    parser.add_argument("--priority", default="P1", choices=sorted(VALID_PRIORITIES))
    parser.add_argument("--owner", default="guapi")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    slug = slugify(args.slug or args.title)
    project_dir = ACTIVE_DIR / slug
    if project_dir.exists():
        raise SystemExit(f"Project already exists: {project_dir}")

    base_template = TEMPLATES_DIR / "base"
    category_template = TEMPLATES_DIR / args.category
    if not category_template.exists():
        raise SystemExit(f"Missing category template: {category_template}")

    created_at = now_iso()
    replacements = {
        "project_id": project_id_from_slug(slug),
        "slug": slug,
        "title": args.title,
        "category": args.category,
        "domain": args.domain,
        "owner": args.owner,
        "priority": args.priority,
        "automation_profile": args.automation_profile,
        "created_at": created_at,
        "updated_at": created_at,
    }

    project_dir.mkdir(parents=True)
    ensure_project_dirs(project_dir)
    copy_template_files(base_template, project_dir, replacements)
    copy_template_files(category_template, project_dir, replacements)

    append_index_entry(
        {
            "id": replacements["project_id"],
            "slug": slug,
            "title": args.title,
            "category": args.category,
            "domain": args.domain,
            "status": "draft",
            "automation_profile": args.automation_profile,
            "priority": args.priority,
            "updated_at": created_at,
            "path": str(project_dir.relative_to(ROOT)),
        }
    )

    print(f"Created project: {project_dir}")
    print("Next:")
    print("  1. Fill project.yaml")
    print("  2. Update brief.md and scope.md")
    print("  3. Refresh session-brief.md and context/routing/current-readset.md")
    print("  4. Rewrite context/summaries/compact-state.md before the first work session")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
