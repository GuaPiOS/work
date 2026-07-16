"""LLM layer: Ollama call, prompt construction, JSON extraction.

Ported from run.py. The legacy single-text build_prompt (prompts/
rewrite_to_spoken_english.txt) was dead code and is intentionally not ported —
generation uses the structured study prompt exclusively.
"""
from __future__ import annotations

import json
import logging
import re

import requests


def strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


def call_ollama(prompt: str, config: dict, *, json_mode: bool = False) -> str:
    llm = config["llm"]
    endpoint = llm["endpoint"]
    model = llm["model"]
    options = {
        "temperature": float(llm.get("temperature", 0.2)),
        "num_predict": int(llm.get("num_predict", 1600)),
    }
    try:
        request_body = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": options,
        }
        if json_mode:
            # Constrain decoding instead of relying on a small local model to
            # reproduce every quote and colon perfectly.
            request_body["format"] = "json"
        response = requests.post(
            endpoint,
            json=request_body,
            timeout=int(config.get("llm", {}).get("timeout_seconds", 180)),
        )
        response.raise_for_status()
        return strip_thinking(response.json().get("response", ""))
    except requests.ConnectionError as exc:
        raise RuntimeError("Cannot connect to Ollama. Is 'ollama serve' running?") from exc
    except requests.Timeout as exc:
        raise RuntimeError(
            "Ollama request timed out. Try a smaller model in config.yaml, e.g. qwen3:4b"
        ) from exc


def build_study_prompt(level: str, items: list[dict]) -> str:
    model_items = [
        {"id": i, "text": prepare_text_for_model(item["original_zh"])}
        for i, item in enumerate(items, start=1)
    ]
    payload = json.dumps(model_items, ensure_ascii=False, separators=(",", ":"))
    return f"""/no_think
You are a precise workplace English learning assistant.

Convert Chinese workplace notes into simple, natural spoken English for listening practice.

Return exactly one line per input item. Do not use JSON or Markdown.
Each line must use this format:
ID|||spoken English|||useful English phrase|||short Chinese learning note

Rules:
1. Keep business meaning accurate. Do not add facts.
2. Stay near {level}: mostly A2 words and grammar, with a small step toward B1.
3. Translate the speaker's intent, not each Chinese word. Write what a friendly coworker would actually say out loud.
4. Prefer short sentences, contractions where natural, and clear transitions. Use common verbs such as "check", "send", "need", "plan", "fix", and "confirm".
5. Avoid stiff business English, long noun phrases, idioms, rare words, and formal words such as "facilitate", "utilize", or "regarding".
6. Return exactly {len(items)} lines and keep the same id/order as the input.
7. Each spoken_english item should be easy to compare with the original Chinese.
8. Keep each spoken_english under 35 words unless the source item needs more detail.
9. Do not output Chinese inside spoken_english.
10. useful English phrase must be one reusable everyday sentence pattern, not a difficult vocabulary item. Prefer patterns such as "Could you + verb...?", "Can we + verb...?", "I’ll + verb...", "We need to + verb...", "Let’s + verb...", or "The main issue is...". Keep it under 8 words when possible.
11. note_zh must be a very short, friendly Chinese explanation (under 20 Chinese characters). Explain when to use the pattern; do not use grammar jargon.
12. Do not mention metadata such as p2p, channel, message ID, item count, or source type.
13. Avoid filler such as "let's take a closer look" unless the original text says that.
14. Never use ||| inside a field.

Input items ({len(items)} items):
{payload}
"""


def extract_study_rows(text: str, expected_count: int) -> dict:
    rows = []
    for raw_line in strip_thinking(text).splitlines():
        parts = [part.strip() for part in raw_line.strip().split("|||")]
        if len(parts) != 4 or not parts[0].isdigit():
            continue
        rows.append({
            "id": int(parts[0]),
            "spoken_english": parts[1],
            "focus_phrase": parts[2],
            "note_zh": parts[3],
        })
    rows.sort(key=lambda row: row["id"])
    if len(rows) != expected_count:
        raise ValueError(f"Expected {expected_count} study rows, received {len(rows)}")
    return {"items": rows}


def prepare_text_for_model(text: str, max_chars: int = 900) -> str:
    cleaned = re.sub(r"<cite\b[^>]*>.*?</cite>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"</?(grid|column|p|span|div|table|tbody|thead|tr|td|th)[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = cleaned.replace("~~", "")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned).strip()
    if len(cleaned) > max_chars:
        return cleaned[:max_chars].rstrip() + "\n[content truncated]"
    return cleaned


def extract_json_object(text: str) -> dict:
    cleaned = strip_thinking(text).strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start: end + 1])
