"""Ollama lifecycle: probe, on-demand start, model check. stdlib-only (urllib),
so it has no heavy deps and can be imported freely."""
from __future__ import annotations

import shutil
import subprocess
import time
import urllib.error
import urllib.request

from .runtime import (
    LOGS_DIR, OLLAMA_PID_FILE,
    start_process, touch_activity, abort_if_stop_requested,
)


def ollama_endpoint(config: dict) -> str:
    gen = config.get("llm", {}).get("endpoint", "http://localhost:11434/api/generate")
    return gen.replace("/api/generate", "/api/tags")


def is_ollama_available(config: dict, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(ollama_endpoint(config), timeout=timeout) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def start_ollama(config: dict) -> None:
    abort_if_stop_requested()
    if is_ollama_available(config):
        print("ollama: already available")
        return
    if not shutil.which("ollama"):
        raise RuntimeError("ollama: command not found. Install Ollama first.")
    start_process(
        "ollama", ["ollama", "serve"],
        OLLAMA_PID_FILE, LOGS_DIR / "ollama.out.log",
        abort_check=abort_if_stop_requested,
    )
    for _ in range(30):
        abort_if_stop_requested()
        if is_ollama_available(config):
            print("ollama: ready")
            return
        time.sleep(0.5)
    raise RuntimeError("ollama: started but did not become ready. Check logs/ollama.out.log")


def check_ollama_model(config: dict) -> None:
    abort_if_stop_requested()
    model = config.get("llm", {}).get("model", "")
    if not model:
        return
    result = subprocess.run(["ollama", "show", model], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ollama model: {model} not found. Run: ollama pull {model}")
    print(f"ollama model: ready ({model})")


def ensure_ollama_running(config: dict, timeout: float = 40.0) -> bool:
    """Start ollama serve on demand if it isn't up. Non-fatal: returns False if
    ollama can't be reached. The model auto-unloads after OLLAMA_KEEP_ALIVE idle."""
    if is_ollama_available(config):
        return True
    if not shutil.which("ollama"):
        return False
    try:
        start_process("ollama", ["ollama", "serve"], OLLAMA_PID_FILE, LOGS_DIR / "ollama.out.log")
    except RuntimeError:
        return False
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_ollama_available(config):
            touch_activity()
            return True
        time.sleep(0.5)
    return False
