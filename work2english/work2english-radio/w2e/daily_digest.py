"""Collect and curate the current user's daily Feishu activity."""
from __future__ import annotations

import json
import logging
import re
import sys
import subprocess
from collections import defaultdict
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

from . import llm, ollama
from .feishu import content_to_text, lark_cli_bin
from .io_utils import write_json, write_text
from .runtime import PROJECT_ROOT

DIGEST_DIR = PROJECT_ROOT / "inbox" / "digest"
SOURCE_ARCHIVE_DIR = PROJECT_ROOT / "inbox" / "sources"


def day_bounds(day: date | None = None) -> tuple[str, str]:
    current = day or date.today()
    tz = datetime.now().astimezone().tzinfo
    start = datetime.combine(current, time.min, tzinfo=tz)
    end = datetime.combine(current, time.max, tzinfo=tz)
    return start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds")


def _run_json(args: list[str]) -> Any:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown lark-cli error"
        raise RuntimeError(detail)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"lark-cli returned invalid JSON: {result.stdout[:200]}") from exc


def _find_list(value: Any, preferred: tuple[str, ...]) -> list[dict]:
    """Tolerate shortcut response envelopes across lark-cli versions."""
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []
    for key in preferred:
        child = value.get(key)
        if isinstance(child, list):
            return [item for item in child if isinstance(item, dict)]
    for key in ("data", "result"):
        child = value.get(key)
        found = _find_list(child, preferred)
        if found:
            return found
    return []


def collect_sources(day: date | None = None) -> dict[str, list[dict]]:
    start, end = day_bounds(day)
    cli = lark_cli_bin()
    messages = _run_json([
        cli, "im", "+messages-search", "--query", "", "--start", start,
        "--end", end, "--page-size", "50", "--page-all", "--no-reactions",
        "--format", "json", "--as", "user",
    ])
    agenda = _run_json([
        cli, "calendar", "+agenda", "--start", start, "--end", end,
        "--format", "json", "--as", "user",
    ])
    day_string = (day or date.today()).isoformat()
    created_tasks = _run_json([
        cli, "task", "+get-my-tasks", "--created_at", day_string,
        "--page-all", "--format", "json", "--as", "user",
    ])
    due_tasks = _run_json([
        cli, "task", "+get-my-tasks", "--due-start", day_string,
        "--due-end", day_string, "--page-all", "--format", "json", "--as", "user",
    ])
    tasks = _dedupe(
        _find_list(created_tasks, ("items", "tasks"))
        + _find_list(due_tasks, ("items", "tasks")),
        ("task_id", "id", "guid"),
    )
    return {
        "messages": _find_list(messages, ("items", "messages")),
        "calendar": _find_list(agenda, ("items", "events")),
        "tasks": tasks,
    }


def source_counts(sources: dict[str, list[dict]]) -> dict[str, int]:
    return {key: len(sources.get(key, [])) for key in ("messages", "calendar", "tasks")}


def write_source_archive(day: date, sources: dict[str, list[dict]]) -> Path:
    path = SOURCE_ARCHIVE_DIR / f"feishu-{day.isoformat()}.json"
    write_json(path, sources)
    return path


def current_user_id() -> str:
    # auth status is JSON by default and, unlike resource shortcuts, does not
    # accept a --format flag in lark-cli 1.0.63.
    payload = _run_json([lark_cli_bin(), "auth", "status"])
    return str(
        payload.get("identities", {}).get("user", {}).get("openId", "")
        if isinstance(payload, dict) else ""
    )


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


def _dedupe(items: list[dict], keys: tuple[str, ...]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for item in items:
        identity = next((str(item.get(k)) for k in keys if item.get(k)), "")
        identity = identity or json.dumps(item, ensure_ascii=False, sort_keys=True)
        if identity not in seen:
            seen.add(identity)
            result.append(item)
    return result


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


def summarize_sources(sources: dict[str, list[dict]], config: dict) -> str:
    raw_messages = sources.get("messages", [])
    selected_messages = select_relevant_messages(raw_messages, current_user_id())
    focused = dict(sources)
    focused["messages"] = selected_messages
    counts = {key: len(focused.get(key, [])) for key in ("messages", "calendar", "tasks")}
    if not any(counts.values()):
        return "今天在飞书中没有检索到消息、日程或任务活动。"
    max_chars = int(config.get("daily_digest", {}).get("max_source_chars", 4500))
    prompt = f"""/no_think
你是一名严谨的工作信息助理。请把下面的飞书当日活动整理成简洁的中文工作摘要，供后续转换成英语听力材料。

要求：
1. 只陈述输入中明确出现的事实，不猜测，不添加结论。
2. 按主题合并重复消息，不要逐条复述聊天。
3. 优先保留：决定、进展、问题/风险、待办和明确时间点。
4. 忽略寒暄、机器人通知和无业务含义的短消息。
5. 只输出 3-5 条短句，每条只讲一个信息点，适合 A2 英语学习者随后翻译和朗读。
6. 每条以“- ”开头；不输出标题、Markdown 代码块、消息 ID 或原始 JSON。
7. 若输入包含 messages_truncated，最后增加一条“部分较早消息因长度限制未纳入摘要”。

数据量：从 {len(raw_messages)} 条可见消息中选出 {counts['messages']} 条与你直接相关的消息；日程 {counts['calendar']}，任务 {counts['tasks']}。
输入：
{compact_sources(focused, max_chars=max_chars)}
"""
    ollama.ensure_ollama_running(config)
    try:
        result = llm.call_ollama(prompt, config).strip()
        if result:
            return result
    except Exception:
        logging.exception("Daily Feishu summary failed; using a source-count fallback.")
    # Graceful degradation: preserve useful source facts rather than reading
    # meaningless counts or an internal error aloud.
    fallback = []
    for item in selected_messages[-5:]:
        text = content_to_text(item.get("content"))
        if len(text) >= 8:
            fallback.append(f"- {text[:180]}")
        if len(fallback) == 3:
            break
    if fallback:
        return "\n".join(fallback)
    raise RuntimeError("No useful Feishu content was available for today's briefing.")


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
            text = content_to_text(items[depth].get("content"))
            text = " ".join(text.split())[:180]
            if len(text) >= 8 and text not in picked:
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
    lines = [
        "# Work2English Daily Feishu Digest",
        "",
        f"Date: {day.isoformat()}",
        f"Learning level: {learning_level_range(config)}",
        f"Source counts: messages={counts['messages']}, calendar={counts['calendar']}, tasks={counts['tasks']}",
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
