"""Study artifact generation: parse daily inbox → LLM rewrite → normalize →
study.json + per-item audio + study table HTML.

Ported from run.py. Differences:
- HTML is rendered from templates/study_table.html (string.Template), not inlined.
- Audio uses w2e.tts.synthesize (provider-agnostic).
- write_study_artifacts no longer writes player_control.json — that is the
  playback layer's job, called by the generation coordinator after artifacts land.
- fallback_english_for_text drops the hardcoded domain content (Turkey/Central
  Asia etc.) that had been baked into source; the fallback is now generic.
"""
from __future__ import annotations

import html
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from string import Template

from . import llm
from . import tts
from .io_utils import read_text, write_text, read_json, write_json
from .runtime import PROJECT_ROOT

STUDY_DIR = PROJECT_ROOT / "output" / "study"
TEMPLATE_FILE = PROJECT_ROOT / "templates" / "study_table.html"


# ─── parsing ──────────────────────────────────────────────────────────────────

def today_label_from_input(input_text: str) -> str:
    match = re.search(r"(?m)^Date:\s*(\d{4}-\d{2}-\d{2})\s*$", input_text)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")


def parse_daily_items(input_text: str) -> list[dict]:
    sections = re.split(r"(?m)^##\s+", input_text.strip())
    items: list[dict] = []
    for section in sections:
        section = section.strip()
        if not section or section.startswith("#"):
            continue
        lines = section.splitlines()
        heading = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:]).strip()
        message_id = ""
        body_lines = []
        for line in body.splitlines():
            if line.startswith("Message ID:"):
                message_id = line.removeprefix("Message ID:").strip()
                continue
            body_lines.append(line)
        original = re.sub(r"\n{3,}", "\n\n", "\n".join(body_lines).strip())
        if original:
            parts = heading.split(" - ", 1)
            base = {
                "time": parts[0].strip() if parts else "",
                "source": parts[1].strip() if len(parts) > 1 else "",
                "message_id": message_id,
                "original_zh": original,
            }
            items.extend(split_long_item(base))
    if items:
        return items
    stripped = input_text.strip()
    return [{"time": "", "source": "manual", "message_id": "", "original_zh": stripped}] if stripped else []


def split_long_item(item: dict, max_chars: int = 900) -> list[dict]:
    original = item["original_zh"].strip()
    if len(original) <= max_chars:
        return [item]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for block in re.split(r"\n(?=#{1,4}\s+)|\n\s*-\s+|\n\s*\d+[.、]\s+", original):
        block = block.strip()
        if not block:
            continue
        if current and current_len + len(block) > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(block)
        current_len += len(block)
    if current:
        chunks.append("\n\n".join(current))
    if len(chunks) <= 1:
        chunks = [original[i: i + max_chars] for i in range(0, len(original), max_chars)]
    out = []
    for index, chunk in enumerate(chunks, start=1):
        split_item = dict(item)
        split_item["original_zh"] = chunk
        split_item["source"] = f"{item.get('source', '').strip()} part {index}".strip()
        out.append(split_item)
    return out


# ─── payload build ────────────────────────────────────────────────────────────

def compose_daily_briefing(items: list[dict]) -> str:
    seen: set[str] = set()
    lines: list[str] = []
    for item in reversed(items):
        spoken = item.get("spoken_english", "").strip()
        key = spoken.lower()
        if spoken and key not in seen:
            seen.add(key)
            lines.append(spoken)
    if not lines:
        return ""
    if len(lines) == 1:
        return f"Here is the latest English briefing. {lines[0]}"
    max_lines = 8
    selected = lines[:max_lines]
    suffix = " Check today's study table for the full set of practice clips." if len(lines) > max_lines else ""
    return "Here is the latest English briefing. " + " ".join(selected) + suffix


def normalize_study_payload(payload: dict, source_items: list[dict]) -> dict:
    raw_items = payload.get("items", [])
    normalized = []
    for index, source in enumerate(source_items):
        generated = raw_items[index] if index < len(raw_items) and isinstance(raw_items[index], dict) else {}
        spoken = str(generated.get("spoken_english", "")).strip()
        if not spoken:
            spoken = str(generated.get("english", "")).strip()
        if not spoken:
            spoken = source["original_zh"]
        normalized.append({
            "time": source.get("time", ""),
            "source": source.get("source", ""),
            "message_id": source.get("message_id", ""),
            "original_zh": source.get("original_zh", ""),
            "spoken_english": spoken,
            "focus_phrase": str(generated.get("focus_phrase", "")).strip(),
            "note_zh": str(generated.get("note_zh", "")).strip(),
        })
    return {"daily_briefing": compose_daily_briefing(normalized), "items": normalized}


def build_study_payload(input_text: str, config: dict) -> dict:
    source_items = parse_daily_items(input_text)
    if not source_items:
        raise RuntimeError("No input items found.")
    prompt = llm.build_study_prompt(config["level"], source_items)
    try:
        raw = llm.call_ollama(prompt, config)
        return normalize_study_payload(llm.extract_json_object(raw), source_items)
    except Exception:
        logging.exception("Structured study generation failed; using fallback payload.")
        return build_fallback_study_payload(source_items)


def fallback_english_for_text(text: str) -> str:
    """Generic fallback (model timed out / returned nothing usable). The previous
    version hardcoded specific business content; kept domain-free on purpose."""
    return "Here is the latest work update. Please check the study table for the original Chinese details."


def build_fallback_study_payload(source_items: list[dict]) -> dict:
    items = []
    for source in source_items:
        cleaned = llm.prepare_text_for_model(source["original_zh"], max_chars=600)
        items.append({
            "time": source.get("time", ""),
            "source": source.get("source", ""),
            "message_id": source.get("message_id", ""),
            "original_zh": source.get("original_zh", ""),
            "spoken_english": fallback_english_for_text(cleaned),
            "focus_phrase": "",
            "note_zh": "模型生成超时，已先生成简短英文播报；稍后可重试生成更精细版本。",
        })
    return {"daily_briefing": compose_daily_briefing(items), "items": items}


# ─── artifacts ────────────────────────────────────────────────────────────────

def study_output_dir(day: str) -> Path:
    return STUDY_DIR / day


def write_study_json(day: str, payload: dict) -> None:
    out = study_output_dir(day)
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "study.json", payload)


def generate_item_audio(day: str, payload: dict, config: dict) -> None:
    audio_dir = study_output_dir(day) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(payload["items"], start=1):
        rel = f"audio/item_{index:03d}.mp3"
        item["audio"] = rel
        tts.synthesize(item["spoken_english"], config, str(audio_dir / f"item_{index:03d}.mp3"))


def _render_rows(payload: dict) -> str:
    rows = []
    for index, item in enumerate(payload["items"], start=1):
        rows.append(
            "<tr>"
            f"<td class=\"idx\">{index}</td>"
            f"<td class=\"meta\"><div>{html.escape(item.get('time') or '-')}</div>"
            f"<small>{html.escape(item.get('source') or '')}</small></td>"
            f"<td class=\"zh\">{html.escape(item['original_zh']).replace(chr(10), '<br>')}</td>"
            f"<td class=\"en\">{html.escape(item['spoken_english']).replace(chr(10), '<br>')}</td>"
            f"<td class=\"audio\"><audio controls preload=\"none\" src=\"{html.escape(item['audio'])}\"></audio></td>"
            f"<td class=\"note\"><strong>{html.escape(item.get('focus_phrase') or '')}</strong>"
            f"<p>{html.escape(item.get('note_zh') or '')}</p></td>"
            "</tr>"
        )
    return "\n        ".join(rows)


def render_study_html(day: str, payload: dict) -> None:
    template = Template(TEMPLATE_FILE.read_text(encoding="utf-8"))
    html_content = template.safe_substitute(
        day=html.escape(day),
        briefing=html.escape(payload["daily_briefing"]),
        rows=_render_rows(payload),
    )
    write_text(study_output_dir(day) / "index.html", html_content)
    today_link = (
        '<!doctype html>\n<html lang="zh-CN">\n<head>\n'
        '  <meta charset="utf-8">\n'
        f'  <meta http-equiv="refresh" content="0; url={html.escape(day)}/index.html">\n'
        '  <title>Work2English Study</title>\n</head>\n<body>\n'
        f'  <p><a href="{html.escape(day)}/index.html">Open today\'s study table</a></p>\n'
        '</body>\n</html>\n'
    )
    write_text(STUDY_DIR / "today.html", today_link)


def write_study_artifacts(day: str, payload: dict, config: dict) -> None:
    """Write study.json, per-item audio, the full radio mp3 copy, and the HTML
    table. Does NOT touch player_control.json — the playback layer decides that."""
    write_study_json(day, payload)
    generate_item_audio(day, payload, config)
    full_audio = Path(config["output_audio"])
    if full_audio.exists():
        shutil.copyfile(full_audio, study_output_dir(day) / "radio.mp3")
    render_study_html(day, payload)


def read_study_payload_for_today(config: dict) -> tuple[str, dict | None]:
    input_text = read_text(config["input_file"])
    day = today_label_from_input(input_text) if input_text else datetime.now().strftime("%Y-%m-%d")
    study_json = study_output_dir(day) / "study.json"
    if not study_json.exists():
        return day, None
    data = read_json(study_json)
    return day, (data if isinstance(data, dict) else None)
