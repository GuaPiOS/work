#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DIR = ROOT / "projects" / "active"
WEEKLY_DIR = ROOT / "ops" / "weekly"

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def simple_yaml_map(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line or raw_line.startswith(" ") or raw_line.startswith("#"):
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def first_numbered_lines(path: Path, limit: int = 3) -> list[str]:
    items: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if len(items) >= limit:
            break
        if line[:2].isdigit() and line[1] == ".":
            items.append(line)
        elif line and line[0].isdigit() and line[1:2] == ".":
            items.append(line)
    return items


def summarize_project(project_dir: Path) -> dict[str, object]:
    meta = simple_yaml_map(project_dir / "project.yaml")
    next_actions = first_numbered_lines(project_dir / "next-actions.md")
    status_text = (project_dir / "status.md").read_text(encoding="utf-8").splitlines()
    summary_line = next((line.strip("- ").strip() for line in status_text if line.strip().startswith("- 摘要：")), "待更新")
    return {
        "slug": project_dir.name,
        "title": meta.get("title", project_dir.name),
        "category": meta.get("category", ""),
        "domain": meta.get("domain", ""),
        "status": meta.get("status", ""),
        "current_phase": meta.get("current_phase", ""),
        "primary_artifact": meta.get("primary_artifact", ""),
        "priority": meta.get("priority", "P3"),
        "updated_at": meta.get("updated_at", ""),
        "summary": summary_line,
        "next_actions": next_actions,
    }


def build_report(projects: list[dict[str, object]]) -> str:
    today = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "# Weekly Project Review",
        "",
        f"- 生成时间：{today}",
        f"- 活跃项目数：{len(projects)}",
        "",
        "## 总览",
        "",
        "| 优先级 | 项目 | 分类 | 阶段 | 状态 | 当前 artifact | 摘要 |",
        "|---|---|---|---|---|---|---|",
    ]

    for item in projects:
        lines.append(
            f"| {item['priority']} | {item['title']} | {item['category']} | {item['current_phase']} | {item['status']} | {item['primary_artifact']} | {item['summary']} |"
        )

    lines.extend(["", "## 下周最靠前动作", ""])
    if not projects:
        lines.append("- 暂无活跃项目。")
    else:
        for item in projects:
            lines.append(f"### {item['title']}")
            actions = item["next_actions"]
            if actions:
                lines.extend(actions)
            else:
                lines.append("- `next-actions.md` 为空或未更新。")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    projects = [
        summarize_project(path)
        for path in sorted(ACTIVE_DIR.iterdir())
        if path.is_dir() and not path.name.startswith(".")
    ]
    projects.sort(key=lambda item: (PRIORITY_ORDER.get(str(item["priority"]), 9), str(item["title"])))

    week = datetime.now().isocalendar()
    output = WEEKLY_DIR / f"{week.year}-W{week.week:02d}.md"
    output.write_text(build_report(projects), encoding="utf-8")
    print(f"Wrote weekly review: {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
