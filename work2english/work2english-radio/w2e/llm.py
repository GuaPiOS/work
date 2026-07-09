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


def call_ollama(prompt: str, config: dict) -> str:
    llm = config["llm"]
    endpoint = llm["endpoint"]
    model = llm["model"]
    options = {
        "temperature": float(llm.get("temperature", 0.2)),
        "num_predict": int(llm.get("num_predict", 1600)),
    }
    try:
        response = requests.post(
            endpoint,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": options,
            },
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

Convert Chinese workplace notes into natural spoken English for listening practice.

Return only valid compact JSON. Do not use Markdown. Do not explain your work.

JSON schema:
{{
  "items": [
    {{
      "id": 1,
      "spoken_english": "Natural spoken English for this item.",
      "focus_phrase": "One useful English phrase from the spoken English.",
      "note_zh": "A short Chinese learning note."
    }}
  ]
}}

Rules:
1. Keep business meaning accurate. Do not add facts.
2. Use {level} level English.
3. Use natural spoken workplace English, not stiff written translation.
4. Prefer short sentences, contractions where natural, and clear transitions.
5. The items array must have exactly {len(items)} items and keep the same id/order as the input.
6. Each spoken_english item should be easy to compare with the original Chinese.
7. Keep each spoken_english under 45 words unless the source item needs more detail.
8. Do not output Chinese inside spoken_english.
9. note_zh must be concise.
10. Do not mention metadata such as p2p, channel, message ID, item count, or source type.
11. Avoid filler such as "let's take a closer look" unless the original text says that.
12. Do not include daily_briefing. The app will compose the radio script locally.

Input items:
{payload}
"""


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
