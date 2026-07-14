"""Curation, rendering, and generation policy for the daily Feishu digest.

Consumes the raw sources produced by :mod:`w2e.feishu_sources` (the acquisition
layer) and turns them into: a relevant-message selection, a compact payload for
the summary model, curated learning items, the rendered digest document, the
inbox rollup, and the idle-aware generation decision.

Deliberately contains no lark-cli calls and no acquisition subprocess — that
boundary now lives in feishu_sources.py. The bot-message main path
(w2e.feishu.process_event) is untouched.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from .feishu import content_to_text, daily_header
from .feishu_sources import source_counts, source_issues
from .io_utils import write_text
from .runtime import PROJECT_ROOT

DIGEST_DIR = PROJECT_ROOT / "inbox" / "digest"
SYSTEM_NOTICE_PATTERNS = (
    "物流状态通知",
    "订单状态变更提醒",
    "您的运费询价",
    "请及时前往Odoo处理",
    "若运费过期",
    "提运单号",
    "签署状态更新",
    "转为销售订单",
    "待客户签署",
    "待我司签署",
)
MENTION_RE = re.compile(r"@\s*[\w.\-\u4e00-\u9fff]+")
AT_TAG_RE = re.compile(r"<at\b[^>]*>.*?</at>", re.IGNORECASE)


def select_relevant_messages(
    messages: list[dict], user_id: str, *, context_radius: int = 2, per_chat_limit: int = 16,
) -> list[dict]:
    """Build a personal attention stream instead of summarizing every busy chat.

    P2P messages are inherently relevant. In groups, keep messages authored by
    or mentioning the user plus a small context window around those messages.
    A per-chat cap prevents one noisy room from consuming the whole briefing.
    """
    chats: dict[str, list[dict]] = defaultdict(list)
    for item in messages:
        if item.get("deleted"):
            continue
        text = content_to_text(item.get("content"))
        if not text or item.get("msg_type") not in ("text", "post"):
            continue
        chats[str(item.get("chat_id", "unknown"))].append(item)

    chosen: list[dict] = []
    for items in chats.values():
        items.sort(key=lambda x: str(x.get("create_time", "")))
        indexes: set[int] = set()
        for index, item in enumerate(items):
            sender = item.get("sender") or {}
            mentions = item.get("mentions") or []
            mention_ids = {
                str(m.get("id", "")) for m in mentions if isinstance(m, dict)
            } if isinstance(mentions, list) else set()
            signal = (
                item.get("chat_type") == "p2p"
                or (user_id and isinstance(sender, dict) and sender.get("id") == user_id)
                or (user_id and user_id in mention_ids)
            )
            if signal:
                start = max(0, index - context_radius)
                end = min(len(items), index + context_radius + 1)
                indexes.update(range(start, end))
        selected = [items[i] for i in sorted(indexes)][-per_chat_limit:]
        chosen.extend(selected)
    chosen.sort(key=lambda x: str(x.get("create_time", "")))
    return chosen


def _compact_message(item: dict) -> dict:
    sender = item.get("sender") or {}
    return {
        "time": item.get("create_time", ""),
        "chat": item.get("chat_name") or item.get("chat_id", ""),
        "sender": sender.get("name") if isinstance(sender, dict) else str(sender),
        "text": content_to_text(item.get("content"))[:1200],
    }


def compact_sources(sources: dict[str, list[dict]], max_chars: int = 4500) -> str:
    payload = {
        "messages": [_compact_message(x) for x in sources.get("messages", [])],
        "calendar": sources.get("calendar", []),
        "tasks": sources.get("tasks", []),
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
    if len(raw) <= max_chars:
        return raw
    # Messages dominate volume. Keep the most recent ones while retaining
    # calendar/task context, and let the summary disclose that truncation.
    messages = payload["messages"]
    while messages and len(json.dumps(payload, ensure_ascii=False, default=str)) > max_chars:
        messages.pop(0)
    payload["messages_truncated"] = True
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)


def summary_items(summary: str, limit: int = 5) -> list[str]:
    items = []
    for line in summary.splitlines():
        cleaned = line.strip().lstrip("-*• ").strip()
        if cleaned and cleaned not in items:
            items.append(cleaned)
    return items[:limit]


def build_digest_items(sources: dict[str, list[dict]], user_id: str, limit: int = 3) -> list[str]:
    """Choose a small, diverse learning set without spending an extra LLM call."""
    relevant = select_relevant_messages(sources.get("messages", []), user_id)
    by_chat: dict[str, list[dict]] = defaultdict(list)
    for item in relevant:
        by_chat[str(item.get("chat_id", "unknown"))].append(item)
    # Most recently active chats first, then round-robin across them so one
    # active group cannot monopolize the daily lesson.
    chat_lists = sorted(
        (sorted(items, key=lambda x: str(x.get("create_time", "")), reverse=True)
         for items in by_chat.values()),
        key=lambda items: str(items[0].get("create_time", "")) if items else "",
        reverse=True,
    )
    picked: list[str] = []
    depth = 0
    while len(picked) < limit and any(depth < len(items) for items in chat_lists):
        for items in chat_lists:
            if depth >= len(items):
                continue
            text = clean_learning_text(content_to_text(items[depth].get("content")))
            if len(text) >= 8 and not is_low_value_learning_text(text) and text not in picked:
                picked.append(text)
                if len(picked) == limit:
                    break
        depth += 1

    # Calendar/task facts fill free slots, but never overwhelm conversation
    # content. Field names are tolerant of shortcut and native API envelopes.
    if len(picked) < limit:
        for event in sources.get("calendar", []):
            title = str(event.get("summary") or event.get("title") or "").strip()
            if title:
                fact = f"今天的日程包括：{title}。"
                if fact not in picked:
                    picked.append(fact)
                    break
    if len(picked) < limit:
        for task in sources.get("tasks", []):
            title = str(task.get("summary") or task.get("title") or task.get("name") or "").strip()
            if title:
                fact = f"今天需要关注的任务：{title}。"
                if fact not in picked:
                    picked.append(fact)
                    break
    return picked[:limit]


def clean_learning_text(text: str) -> str:
    """Remove obvious person-name noise before using chat text as study input."""
    text = AT_TAG_RE.sub("", text)
    text = MENTION_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:180].rstrip()


def is_low_value_learning_text(text: str) -> bool:
    compact = " ".join(text.split())
    if re.fullmatch(r"https?://\S+", compact):
        return True
    if any(pattern in compact for pattern in SYSTEM_NOTICE_PATTERNS):
        return True
    # Machine notices tend to be identifier-heavy and poor spoken-English input.
    digit_count = sum(ch.isdigit() for ch in compact)
    return len(compact) > 80 and digit_count >= 18


def learning_limit(config: dict) -> int:
    return int(config.get("daily_digest", {}).get("max_learning_items", 3))


def learning_level_range(config: dict) -> str:
    current = str(config.get("level", "A2")).strip() or "A2"
    target = str(config.get("daily_digest", {}).get("target_level", "B1")).strip() or "B1"
    return f"{current}->{target}"


def curate_learning_items(sources: dict[str, list[dict]], config: dict, user_id: str) -> list[str]:
    return build_digest_items(sources, user_id, limit=learning_limit(config))


def render_digest_document(
    day: date,
    items: list[str],
    sources: dict[str, list[dict]],
    config: dict,
) -> str:
    counts = source_counts(sources)
    count_text = ", ".join(f"{key}={value}" for key, value in counts.items())
    issues = source_issues(sources)
    lines = [
        "# Work2English Daily Feishu Digest",
        "",
        f"Date: {day.isoformat()}",
        f"Learning level: {learning_level_range(config)}",
        f"Source counts: {count_text}",
        "",
        "## Curated Learning Items",
        "",
    ]
    for index, item in enumerate(items, start=1):
        lines.append(f"{index}. {item}")
    lines.extend([
        "",
        "## Notes",
        "",
        "- This digest is a curated learning input, not a full work report.",
        "- Raw Feishu source data is archived separately for debugging and review.",
        "- The normal bot-message entry point remains independent of this digest.",
        "",
    ])
    if issues:
        lines.extend(["## Source Issues", ""])
        for issue in issues:
            source = issue.get("source", "unknown")
            error = issue.get("error", "unknown error")
            lines.append(f"- {source}: {error}")
        lines.append("")
    return "\n".join(lines)


def write_digest_document(
    day: date,
    items: list[str],
    sources: dict[str, list[dict]],
    config: dict,
) -> Path:
    path = DIGEST_DIR / f"{day.isoformat()}.md"
    write_text(path, render_digest_document(day, items, sources, config))
    return path


def render_digest_inbox(day: date, items: list[str]) -> str:
    """Render curated digest items as an in-memory inbox for English preview.

    This mirrors the daily inbox section format enough for study.parse_daily_items
    without writing to the real playback inbox.
    """
    content = daily_header(day.isoformat()).rstrip()
    for index, item in enumerate(items, start=1):
        content += (
            f"\n\n## preview - daily digest\n\n"
            f"Message ID: daily-feishu-preview-{day.isoformat()}-{index}\n\n"
            f"{item.strip()}\n"
        )
    return content.strip() + "\n"


def _sanitize_digest_item(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:240].rstrip()


def write_digest_to_inbox(day: date, items: list[str], config: dict) -> None:
    from . import feishu

    day_string = day.isoformat()
    feishu.remove_daily_summary_sections(config, day_string)
    for index, item in enumerate(items, start=1):
        event = {
            "message_id": f"daily-feishu-digest-{day_string}-{index}",
            "chat_type": "daily",
            "message_type": "digest",
            "collected_date": day_string,
        }
        feishu.append_daily_inbox(_sanitize_digest_item(item), config, event)


def system_idle_seconds() -> float | None:
    if sys.platform != "darwin":
        return None
    result = subprocess.run(
        ["ioreg", "-c", "IOHIDSystem"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return None
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.stdout)
    if not match:
        return None
    return int(match.group(1)) / 1_000_000_000


def generation_decision(config: dict, *, force: bool = False) -> tuple[bool, str]:
    if force:
        return True, "forced"
    settings = config.get("daily_digest", {})
    policy = str(settings.get("generation_policy", "idle")).strip().lower()
    if policy == "never":
        return False, "generation_policy=never"
    if policy == "always":
        return True, "generation_policy=always"
    min_idle = int(settings.get("min_idle_seconds", 300))
    idle = system_idle_seconds()
    if idle is None:
        return False, "system idle time is unavailable; use --force-generate to run now"
    if idle >= min_idle:
        return True, f"idle for {int(idle)}s"
    return False, f"idle for {int(idle)}s; waiting for {min_idle}s"
