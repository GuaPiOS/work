"""Health checks + state accessors for the UI server and CLI status.

Consolidates server.py's ollama_health / tts_health / feishu_health /
player_health / inbox_stale / latest_study_day / load_study so the HTTP layer
and `./status.sh` share one source of truth.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

import requests

from .runtime import PROJECT_ROOT, RUNTIME_DIR, OUTPUT_DIR, read_pid
from .io_utils import read_text, get_hash
from . import tts as tts_provider
from .config import player_pid_file

STUDY_DIR = OUTPUT_DIR / "study"
COLLECTOR_PID_FILE = RUNTIME_DIR / "collector.pid"


def collector_alive() -> bool:
    pid = read_pid(COLLECTOR_PID_FILE)
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def latest_study_day() -> str | None:
    if not STUDY_DIR.exists():
        return None
    days = [p.name for p in STUDY_DIR.iterdir() if p.is_dir() and p.name[:4].isdigit()]
    if not days:
        return None
    days.sort(reverse=True)
    for d in days:
        if (STUDY_DIR / d / "audio").exists():
            return d
    return days[0]


def load_study(day: str | None) -> dict | None:
    if not day:
        return None
    path = STUDY_DIR / day / "study.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def ollama_health(config: dict) -> tuple[str, str]:
    llm = config.get("llm", {})
    endpoint = llm.get("endpoint", "")
    wanted = llm.get("model", "qwen3:8b")
    tags_url = endpoint.replace("/api/generate", "/api/tags") or "http://localhost:11434/api/tags"
    try:
        r = requests.get(tags_url, timeout=2.0)
    except requests.ConnectionError:
        return ("error", "Ollama 未运行。请在终端执行：ollama serve")
    except requests.Timeout:
        return ("error", "Ollama 响应超时（>2s），可能正在加载模型。")
    except requests.RequestException as exc:
        return ("error", f"无法连接 Ollama：{exc}")
    if r.status_code != 200:
        return ("error", f"Ollama 返回 {r.status_code}。请重启：ollama serve")
    try:
        models = [m.get("name", "") for m in r.json().get("models", [])]
    except ValueError:
        return ("error", "Ollama 响应格式异常。")
    if wanted and wanted not in models:
        return ("processing", f"模型 {wanted} 未拉取。请在终端执行：ollama pull {wanted}")
    return ("connected", "")


def tts_health(config: dict) -> tuple[str, str]:
    provider = (config.get("tts", {}) or {}).get("provider", "edge-tts")
    if provider == "fish-audio":
        if not tts_provider.fish_api_key(config):
            return ("error", "Fish Audio API key 未配置。")
        model = (config.get("fish_audio", {}) or {}).get("model") or "s2.1-pro-free"
        if not model:
            return ("error", "Fish Audio model 未配置。")
        return ("connected", "")
    bin_path = shutil.which("edge-tts") or str(PROJECT_ROOT / ".venv" / "bin" / "edge-tts")
    if Path(bin_path).exists():
        return ("connected", "")
    return ("error", "未安装 edge-tts。请在激活的虚拟环境中执行：pip install edge-tts")


def feishu_health(config: dict) -> tuple[str, str]:
    if collector_alive():
        return ("connected", "")
    inbox_path = PROJECT_ROOT / config.get("input_file", "inbox/feishu_raw.md")
    has_inbox = inbox_path.exists() and inbox_path.read_text(encoding="utf-8").strip()
    hint = "飞书采集器未运行，消息不会被接收。请通过启动器启动。" if has_inbox else "采集器未运行，且收件箱为空。"
    return ("idle", hint)


def player_health(study: dict | None, day: str | None) -> tuple[str, str]:
    if study and day and (STUDY_DIR / day / "audio").exists() and study.get("items"):
        return ("connected", "")
    return ("idle", "暂无音频，点 Start 生成。")


def inbox_stale(config: dict) -> bool:
    inbox_path = PROJECT_ROOT / config.get("input_file", "inbox/feishu_raw.md")
    if not inbox_path.exists():
        return False
    text = inbox_path.read_text(encoding="utf-8").strip()
    if not text:
        return False
    current_hash = get_hash(text)
    hash_file = PROJECT_ROOT / config.get("input_hash_file", "runtime/last_input_hash.txt")
    if not hash_file.exists():
        return True
    return hash_file.read_text(encoding="utf-8").strip() != current_hash
