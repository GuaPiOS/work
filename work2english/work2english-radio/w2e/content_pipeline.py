"""Extensible content pipeline for daily Feishu learning material.

This module sits between acquisition (feishu_sources) and generation
(daily_digest/study/tts). It deliberately returns small, UI-friendly candidate
objects so the user can review, filter, and later replace the scorer with an
LLM reranker without changing the acquisition layer.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Iterable

from . import daily_digest
from .feishu import content_to_text
from .io_utils import write_json
from .runtime import PROJECT_ROOT

CANDIDATE_DIR = PROJECT_ROOT / "inbox" / "candidates"

SIGNAL_KEYWORDS = (
    "需要", "确认", "验证", "测试", "反馈", "问题", "风险", "方案", "策略",
    "逻辑", "优化", "推进", "安排", "复盘", "总结", "决策", "结论", "阻塞",
    "deadline", "review", "test", "confirm", "issue", "risk",
)


def _candidate_id(source: str, *parts: object) -> str:
    raw = "|".join(str(part or "") for part in (source, *parts))
    return f"{source}:{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def _is_name_only(text: str) -> bool:
    compact = text.strip()
    if not compact:
        return True
    if len(compact) <= 24 and re.fullmatch(r"[\w.\-\s@\u4e00-\u9fff]+", compact):
        # Short pure name / @mention fragments are poor learning material.
        return not any(mark in compact for mark in "，。！？,.!?")
    return False


def _score_message(item: dict, text: str, user_id: str) -> tuple[int, list[str], list[str]]:
    sender = item.get("sender") or {}
    mentions = item.get("mentions") or []
    mention_ids = {
        str(m.get("id", "")) for m in mentions if isinstance(m, dict)
    } if isinstance(mentions, list) else set()

    score = 0
    reasons: list[str] = []
    tags: list[str] = []

    if item.get("chat_type") == "p2p":
        score += 4
        tags.append("私聊")
        reasons.append("私聊内容通常更贴近你的实际工作输入")
    if user_id and isinstance(sender, dict) and sender.get("id") == user_id:
        score += 3
        tags.append("我发送")
        reasons.append("你自己表达过的内容适合转成英语表达")
    if user_id and user_id in mention_ids:
        score += 3
        tags.append("提到我")
        reasons.append("群聊中明确与你相关")

    keyword_hits = [kw for kw in SIGNAL_KEYWORDS if kw.lower() in text.lower()]
    if keyword_hits:
        score += min(4, 1 + len(keyword_hits))
        tags.append("工作信号")
        reasons.append("包含需要表达清楚的工作动作或判断")

    if 18 <= len(text) <= 120:
        score += 2
        reasons.append("长度适合 A2 到 B1 口语训练")
    elif len(text) > 160:
        score -= 2
        tags.append("偏长")

    digit_count = sum(ch.isdigit() for ch in text)
    if len(text) > 50 and digit_count >= 12:
        score -= 3
        tags.append("编号多")

    if not tags:
        tags.append("上下文")
    if not reasons:
        reasons.append("来自与你相关的聊天上下文")
    return score, reasons[:3], tags[:3]


def _message_candidates(messages: Iterable[dict], user_id: str) -> list[dict]:
    relevant = daily_digest.select_relevant_messages(list(messages), user_id)
    candidates: list[dict] = []
    seen_text: set[str] = set()
    for item in relevant:
        text = daily_digest.clean_learning_text(content_to_text(item.get("content")))
        if len(text) < 8 or text in seen_text:
            continue
        if _is_name_only(text) or daily_digest.is_low_value_learning_text(text):
            continue
        seen_text.add(text)
        score, reasons, tags = _score_message(item, text, user_id)
        candidates.append({
            "id": _candidate_id("messages", item.get("message_id") or item.get("id"), item.get("chat_id"), item.get("create_time"), text),
            "source": "messages",
            "time": str(item.get("create_time", "")),
            "chat": item.get("chat_name") or item.get("chat_id") or "",
            "text": text,
            "score": score,
            "reasons": reasons,
            "tags": tags,
            "recommended": False,
        })
    return candidates


def _calendar_candidates(events: Iterable[dict]) -> list[dict]:
    candidates: list[dict] = []
    for event in events:
        title = str(event.get("summary") or event.get("title") or "").strip()
        if not title or _is_name_only(title):
            continue
        text = f"今天的日程包括：{title}。"
        candidates.append({
            "id": _candidate_id("calendar", event.get("event_id") or event.get("id"), title),
            "source": "calendar",
            "time": str(event.get("start_time") or event.get("start") or ""),
            "chat": "calendar",
            "text": text,
            "score": 2,
            "reasons": ["日程可补充当天工作背景"],
            "tags": ["日程"],
            "recommended": False,
        })
    return candidates


def _task_candidates(tasks: Iterable[dict]) -> list[dict]:
    candidates: list[dict] = []
    for task in tasks:
        title = str(task.get("summary") or task.get("title") or task.get("name") or "").strip()
        if not title or _is_name_only(title):
            continue
        text = f"今天需要关注的任务：{title}。"
        candidates.append({
            "id": _candidate_id("tasks", task.get("guid") or task.get("id"), title),
            "source": "tasks",
            "time": str(task.get("due") or task.get("updated_at") or ""),
            "chat": "tasks",
            "text": text,
            "score": 2,
            "reasons": ["任务可补充当天行动项"],
            "tags": ["任务"],
            "recommended": False,
        })
    return candidates


def build_candidates(
    sources: dict[str, list[dict]],
    user_id: str,
    *,
    limit: int = 30,
    recommended_limit: int = 3,
) -> list[dict]:
    candidates = (
        _message_candidates(sources.get("messages", []), user_id)
        + _calendar_candidates(sources.get("calendar", []))
        + _task_candidates(sources.get("tasks", []))
    )
    candidates.sort(key=lambda c: (int(c.get("score", 0)), str(c.get("time", ""))), reverse=True)

    recommended_ids = {c["id"] for c in candidates[:recommended_limit]}
    for candidate in candidates:
        candidate["recommended"] = candidate["id"] in recommended_ids
    return candidates[:limit]


def selected_texts(candidates: list[dict], selected_ids: list[str] | None = None, *, limit: int = 3) -> list[str]:
    selected = set(selected_ids or [])
    if selected:
        items = [str(c.get("text", "")).strip() for c in candidates if c.get("id") in selected]
    else:
        items = [str(c.get("text", "")).strip() for c in candidates if c.get("recommended")]
    # Keep UI order/score order, remove empties and duplicates.
    result: list[str] = []
    for item in items:
        if item and item not in result:
            result.append(item)
        if len(result) >= limit:
            break
    return result


def write_candidate_pool(day: date, candidates: list[dict]) -> Path:
    path = CANDIDATE_DIR / f"{day.isoformat()}.json"
    write_json(path, {"day": day.isoformat(), "candidates": candidates}, indent=2)
    return path
