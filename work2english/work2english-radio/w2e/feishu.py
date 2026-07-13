"""Feishu (Lark) collection: lark-cli invocation, event parsing, dedupe,
daily inbox rollup, and bot receipts.

Consolidates what lived in feishu_collect.py, and removes the duplicate reply
path that run.py carried (reply_to_feishu hardcoded "lark-cli" without PATH
resolution). Pure of the generation/playback layers — process_event hands off
to a caller-supplied on_ready callback so the collector stays decoupled from
the pipeline.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Callable

from .runtime import PROJECT_ROOT
from .io_utils import read_json, write_json, write_text

EVENTS_DIR = PROJECT_ROOT / "inbox" / "events"
FAILED_DIR = PROJECT_ROOT / "inbox" / "failed"
DAILY_DIR = PROJECT_ROOT / "inbox" / "daily"
PENDING_RECEIPTS_FILE = PROJECT_ROOT / "runtime" / "pending_receipts.ndjson"
DEDUPE_STATE_FILE = PROJECT_ROOT / "runtime" / "event_dedupe_state.json"

DOC_URL_RE = re.compile(r"https?://[^\s<>'\"\]\)]+/(?:docx|doc|wiki)/[^\s<>'\"\]\)]*")
AT_TAG_RE = re.compile(r"<at\b[^>]*>.*?</at>", re.IGNORECASE)
LEADING_AT_RE = re.compile(r"^\s*@\S+\s*")

UNSUPPORTED_MESSAGE_TYPES = {
    "image", "audio", "file", "video", "media", "sticker",
    "interactive", "share_chat", "share_user",
}

RECEIPT_RECEIVED = "收到内容，正在生成英文播报。"
RECEIPT_SUCCESS_PLAYING = "已生成英文播报，正在播放。"
RECEIPT_SUCCESS_WAITING = "已生成英文播报。打开 Work2English 应用即可收听。"
RECEIPT_DOC_FAILED = "文档读取失败。请确认机器人有文档权限，或复制正文发送。"
RECEIPT_UNPARSEABLE = "当前版本只支持文本和飞书文档链接。请复制文本发送。"
RECEIPT_MERGE_FAILED = "当前版本无法稳定解析合并转发卡片。请复制其中的文本后直接发送给我。"


# ─── lark-cli ──────────────────────────────────────────────────────────────────

def lark_cli_bin() -> str:
    found = shutil.which("lark-cli")
    if found:
        return found
    candidates = [
        Path.home() / ".npm-global" / "bin" / "lark-cli",
        Path.home() / ".local" / "bin" / "lark-cli",
        Path.home() / ".nvm" / "current" / "bin" / "lark-cli",
        Path("/opt/homebrew/bin/lark-cli"),
        Path("/usr/local/bin/lark-cli"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    raise FileNotFoundError(
        "lark-cli not found. Install it or add it to PATH. "
        "Expected common path: ~/.npm-global/bin/lark-cli"
    )


def reply(message_id: str, text: str) -> bool:
    """Send a bot reply to a Feishu message. Single implementation (was duplicated)."""
    if not message_id:
        return False
    cmd = [
        lark_cli_bin(), "im", "+messages-reply",
        "--message-id", message_id, "--text", text, "--as", "bot",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        logging.warning("Failed to send Feishu receipt for %s: %s", message_id, result.stderr.strip())
        return False
    return True


def fetch_doc_markdown(url: str, config: dict) -> str:
    command_template = config["feishu"]["doc_fetch_command"]
    command = command_template.format(url=url)
    args = shlex.split(command)
    if args and args[0] == "lark-cli":
        args[0] = lark_cli_bin()
    result = subprocess.run(args, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "docs +fetch failed")
    stdout = result.stdout.strip()
    if not stdout:
        return ""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout
    document = payload.get("data", {}).get("document", {})
    return document.get("content", "").strip()


# ─── event parsing ────────────────────────────────────────────────────────────

def collect_text_values(value) -> list[str]:
    texts: list[str] = []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        for item in value:
            texts.extend(collect_text_values(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {"text", "title"} and isinstance(item, str):
                texts.append(item)
            elif key in {"content", "zh_cn", "en_us"}:
                texts.extend(collect_text_values(item))
    return texts


def content_to_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        stripped = content.strip()
        if not stripped:
            return ""
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return stripped
        return content_to_text(parsed)
    texts = collect_text_values(content)
    return "\n".join(t.strip() for t in texts if t and t.strip()).strip()


def strip_bot_addressing(text: str) -> str:
    text = AT_TAG_RE.sub("", text)
    text = LEADING_AT_RE.sub("", text)
    stripped = text.strip()
    for command in ("/read", "/doc"):
        if stripped == command:
            return ""
        if stripped.startswith(command + " "):
            return stripped[len(command):].strip()
    return stripped


def group_message_is_addressed_to_bot(event: dict, raw_text: str) -> bool:
    if event.get("chat_type") != "group":
        return True
    raw_event = json.dumps(event, ensure_ascii=False)
    if "<at" in raw_event or event.get("mentions"):
        return True
    stripped = raw_text.strip()
    if stripped.startswith("@"):
        return True
    return stripped.startswith("/read ") or stripped.startswith("/doc ")


def find_doc_url(text: str, supported_patterns: list[str]) -> str:
    for match in DOC_URL_RE.finditer(text):
        url = match.group(0).rstrip(".,;，。；")
        if any(p in url for p in supported_patterns):
            return url
    return ""


def truncate_input(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip()


def source_label(event: dict) -> str:
    return f"{event.get('chat_type', 'unknown')} {event.get('message_type', 'unknown')}".strip()


# ─── dedupe ───────────────────────────────────────────────────────────────────

def _empty_dedupe() -> dict:
    return {"message_ids": {}, "fingerprints": {}}


def load_dedupe_state() -> dict:
    state = read_json(DEDUPE_STATE_FILE, _empty_dedupe())
    if not isinstance(state, dict):
        return _empty_dedupe()
    state.setdefault("message_ids", {})
    state.setdefault("fingerprints", {})
    return state


def write_dedupe_state(state: dict) -> None:
    write_json(DEDUPE_STATE_FILE, state)


def event_created_at_ms(event: dict) -> int | None:
    value = event.get("create_time") or event.get("created_at") or event.get("timestamp")
    try:
        if value is None:
            return None
        created = int(value)
        if created < 10_000_000_000:
            created *= 1000
        return created
    except (TypeError, ValueError):
        return None


def is_stale_event(event: dict, config: dict, collector_started_at_ms: int) -> bool:
    grace = int(config.get("collector", {}).get("ignore_events_older_than_start_seconds", 120))
    if grace < 0:
        return False
    created_at = event_created_at_ms(event)
    if created_at is None:
        return False
    return created_at < collector_started_at_ms - grace * 1000


def normalize_dedupe_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def dedupe_fingerprint(event: dict, parsed_text: str) -> str:
    parts = [
        event.get("chat_id", ""),
        event.get("sender_id", ""),
        event.get("message_type", ""),
        normalize_dedupe_text(parsed_text),
    ]
    raw = "\n".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def prune_dedupe_state(state: dict, duplicate_window_seconds: int) -> None:
    import time
    now = time.time()
    message_ttl = 24 * 60 * 60
    state["message_ids"] = {
        k: ts for k, ts in state.get("message_ids", {}).items()
        if isinstance(ts, (int, float)) and now - float(ts) <= message_ttl
    }
    fingerprint_ttl = max(duplicate_window_seconds, 60)
    state["fingerprints"] = {
        k: ts for k, ts in state.get("fingerprints", {}).items()
        if isinstance(ts, (int, float)) and now - float(ts) <= fingerprint_ttl
    }


def message_already_seen(message_id: str) -> bool:
    if not message_id:
        return False
    return message_id in load_dedupe_state().get("message_ids", {})


def remember_message(message_id: str, parsed_text: str = "", event: dict | None = None, config: dict | None = None) -> None:
    state = load_dedupe_state()
    duplicate_window = int((config or {}).get("collector", {}).get("duplicate_text_window_seconds", 600))
    prune_dedupe_state(state, duplicate_window)
    import time
    now = time.time()
    if message_id:
        state["message_ids"][message_id] = now
    if event is not None and parsed_text:
        state["fingerprints"][dedupe_fingerprint(event, parsed_text)] = now
    write_dedupe_state(state)


def text_already_seen_recently(event: dict, parsed_text: str, config: dict) -> bool:
    import time
    duplicate_window = int(config.get("collector", {}).get("duplicate_text_window_seconds", 600))
    if duplicate_window <= 0:
        return False
    fingerprint = dedupe_fingerprint(event, parsed_text)
    state = load_dedupe_state()
    prune_dedupe_state(state, duplicate_window)
    seen_at = state.get("fingerprints", {}).get(fingerprint)
    write_dedupe_state(state)
    if not isinstance(seen_at, (int, float)):
        return False
    return time.time() - float(seen_at) <= duplicate_window


# ─── event files & daily inbox ────────────────────────────────────────────────

def event_file_name(event: dict, suffix: str = "json") -> str:
    event_id = event.get("event_id") or event.get("message_id") or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(event_id))
    return f"{timestamp}-{safe}.{suffix}"


def save_event(event: dict, parsed_text: str = "") -> None:
    write_json(EVENTS_DIR / event_file_name(event), {"event": event, "parsed_text": parsed_text})


def save_failure(event: dict, reason: str, parsed_text: str = "") -> None:
    write_json(FAILED_DIR / event_file_name(event), {"reason": reason, "event": event, "parsed_text": parsed_text})
    logging.warning("Saved failed event: %s: %s", event_file_name(event), reason)


def daily_header(today: str) -> str:
    return f"# Work2English Radio Daily Inbox\n\nDate: {today}\n"


def current_day_from_content(content: str) -> str:
    for line in content.splitlines()[:5]:
        if line.startswith("Date: "):
            return line.removeprefix("Date: ").strip()
    return ""


def append_daily_inbox(text: str, config: dict, event: dict) -> None:
    input_file = PROJECT_ROOT / config["input_file"]
    input_file.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    today = event.get("collected_date") or now.strftime("%Y-%m-%d")
    current = input_file.read_text(encoding="utf-8") if input_file.exists() else ""
    if current_day_from_content(current) != today:
        current = daily_header(today)
    section_title = now.strftime("%H:%M")
    message_id = event.get("message_id") or event.get("id") or "unknown"
    item = (
        f"\n\n## {section_title} - {source_label(event)}\n\n"
        f"Message ID: {message_id}\n\n"
        f"{text.strip()}\n"
    )
    next_content = (current.rstrip() + item).strip() + "\n"
    max_daily = int(config.get("collector", {}).get("max_daily_chars", 20000))
    if max_daily > 0 and len(next_content) > max_daily:
        keep = max_daily - len(daily_header(today)) - 120
        next_content = (
            daily_header(today)
            + "\n[Earlier items were truncated because today's inbox exceeded the configured limit.]\n\n"
            + next_content[-max(keep, 0):].lstrip()
        )
    write_text(str(input_file), next_content)
    write_text(str(DAILY_DIR / f"{today}.md"), next_content)


def remove_daily_summary_sections(config: dict, day: str) -> None:
    """Make an on-demand digest idempotent while preserving bot-fed items."""
    input_file = PROJECT_ROOT / config["input_file"]
    if not input_file.exists():
        return
    content = input_file.read_text(encoding="utf-8")
    if current_day_from_content(content) != day:
        return
    cleaned = re.sub(
        r"(?ms)^##\s+[^\n]+ - daily (?:feishu_summary|digest)\n.*?(?=^##\s+|\Z)",
        "",
        content,
    ).rstrip() + "\n"
    write_text(str(input_file), cleaned)
    write_text(str(DAILY_DIR / f"{day}.md"), cleaned)


def write_inbox(text: str, config: dict, event: dict) -> None:
    if config.get("collector", {}).get("daily_rollup", True):
        append_daily_inbox(text, config, event)
        return
    input_file = PROJECT_ROOT / config["input_file"]
    write_text(str(input_file), text.strip() + "\n")


# ─── receipts ─────────────────────────────────────────────────────────────────

def append_success_receipt(message_id: str) -> None:
    """Queue a success receipt; its final text is resolved at send time from the
    playback status (so it never claims 'playing' when nothing is playing)."""
    if not message_id:
        return
    PENDING_RECEIPTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PENDING_RECEIPTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"message_id": message_id}, ensure_ascii=False) + "\n")


def send_pending_success_receipts(status: str = "playing") -> None:
    """Send queued success receipts. `status` reflects what the playback
    coordinator actually did: 'playing' (audio is playing somewhere) or
    'waiting' (generated, but no client is playing yet)."""
    if not PENDING_RECEIPTS_FILE.exists():
        return
    text = RECEIPT_SUCCESS_PLAYING if status == "playing" else RECEIPT_SUCCESS_WAITING
    remaining: list[str] = []
    for line in PENDING_RECEIPTS_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        message_id = item.get("message_id", "")
        if not reply(message_id, text):
            remaining.append(line)
    if remaining:
        PENDING_RECEIPTS_FILE.write_text("\n".join(remaining) + "\n", encoding="utf-8")
    else:
        PENDING_RECEIPTS_FILE.unlink(missing_ok=True)


# ─── event processing ─────────────────────────────────────────────────────────

def process_event(
    event: dict,
    config: dict,
    *,
    collector_started_at_ms: int,
    on_ready: Callable[[dict], None] | None = None,
) -> None:
    """Parse, dedupe, write to inbox, queue receipt, then hand off to on_ready.

    on_ready(config) is invoked after fresh content lands in the inbox — the
    caller wires it to the generation coordinator. Kept as a callback so this
    module has no dependency on the pipeline.
    """
    message_id = event.get("message_id") or event.get("id", "")
    message_type = event.get("message_type", "")
    raw_text = content_to_text(event.get("content"))

    if message_already_seen(message_id):
        logging.info("Ignored duplicate message_id %s", message_id)
        return

    if is_stale_event(event, config, collector_started_at_ms):
        remember_message(message_id, config=config)
        logging.info("Ignored stale event %s", message_id)
        return

    if event.get("chat_type") == "group" and not group_message_is_addressed_to_bot(event, raw_text):
        logging.info("Ignored non-addressed group message %s", message_id)
        return

    if message_type in UNSUPPORTED_MESSAGE_TYPES:
        remember_message(message_id, raw_text, event, config)
        save_failure(event, f"unsupported message type: {message_type}", raw_text)
        reply(message_id, RECEIPT_UNPARSEABLE)
        return

    if message_type == "merge_forward":
        extracted = strip_bot_addressing(raw_text)
        if len(extracted) < 10:
            remember_message(message_id, raw_text, event, config)
            save_failure(event, "merge_forward cannot be parsed", raw_text)
            reply(message_id, RECEIPT_MERGE_FAILED)
            return
        raw_text = extracted

    parsed_text = strip_bot_addressing(raw_text)
    if not parsed_text:
        remember_message(message_id, raw_text, event, config)
        save_failure(event, "empty parsed text", raw_text)
        reply(message_id, RECEIPT_UNPARSEABLE)
        return

    if text_already_seen_recently(event, parsed_text, config):
        remember_message(message_id, parsed_text, event, config)
        logging.info("Ignored duplicate text from message %s", message_id)
        return

    collector_cfg = config.get("collector", {})
    max_chars = int(collector_cfg.get("max_input_chars", 5000))
    supported_patterns = collector_cfg.get("supported_doc_patterns", ["/docx/", "/doc/", "/wiki/"])
    doc_url = find_doc_url(parsed_text, supported_patterns)

    if doc_url:
        reply(message_id, RECEIPT_RECEIVED)
        try:
            parsed_text = fetch_doc_markdown(doc_url, config)
        except Exception as exc:
            save_failure(event, f"doc fetch failed: {exc}", raw_text)
            reply(message_id, RECEIPT_DOC_FAILED)
            return
        if not parsed_text:
            save_failure(event, "doc fetch returned empty content", raw_text)
            reply(message_id, RECEIPT_DOC_FAILED)
            return
    else:
        reply(message_id, RECEIPT_RECEIVED)

    parsed_text = truncate_input(parsed_text, max_chars)
    write_inbox(parsed_text, config, event)
    save_event(event, parsed_text)
    remember_message(message_id, parsed_text, event, config)
    append_success_receipt(message_id)
    logging.info("Wrote Feishu input from message %s", message_id)
    if on_ready is not None:
        try:
            on_ready(config)
        except Exception:
            logging.exception("on_ready callback failed after feishu event.")
