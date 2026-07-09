#!/usr/bin/env python3
"""Background service manager: start / stop / restart / status for the
collector, ollama, and player. Thin wrapper around w2e.

On-demand architecture: only the lightweight collector is resident. Ollama +
translation start when a Feishu message arrives (or the UI presses Start), then
release memory when idle.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from w2e.runtime import (
    ensure_venv_python, chdir_root, ensure_dirs,
    start_process, ensure_running, stop_pid_file,
    read_pid, is_process_alive,
    mark_stop_requested, clear_stop_requested, stop_requested,
    WATCHER_PID_FILE, COLLECTOR_PID_FILE, OLLAMA_PID_FILE,
    LOGS_DIR, PROJECT_ROOT,
)
ensure_venv_python()
chdir_root()

from w2e.config import load_config, player_pid_file
from w2e import ollama, tts as tts_provider


def check_tts_ready(config: dict) -> None:
    provider = (config.get("tts", {}) or {}).get("provider", "edge-tts")
    if provider == "fish-audio":
        if not tts_provider.fish_api_key(config):
            raise RuntimeError("fish-audio: API key not configured. Set fish_audio.api_key or FISH_AUDIO_API_KEY.")
        model = (config.get("fish_audio", {}) or {}).get("model") or "s2.1-pro-free"
        print(f"fish-audio: ready (model={model})")
        return
    edge_tts = shutil.which("edge-tts") or PROJECT_ROOT / ".venv" / "bin" / "edge-tts"
    if isinstance(edge_tts, Path) and not edge_tts.exists():
        raise RuntimeError("edge-tts: not found. Run pip install -r requirements.txt")
    print(f"edge-tts: ready ({edge_tts})")


def ensure_collector_running(config: dict) -> bool:
    return ensure_running(
        "collector", [sys.executable, "feishu_collect.py"],
        COLLECTOR_PID_FILE, LOGS_DIR / "collector.out.log",
    )


def start_services() -> None:
    ensure_dirs()
    clear_stop_requested()
    config = load_config()  # validate config exists
    # Best-effort retention prune (no-op unless config.retention.days is set).
    try:
        from w2e.cleanup import cleanup_old_artifacts
        cleanup_old_artifacts(config)
    except Exception:
        pass
    start_process(
        "collector", [sys.executable, "feishu_collect.py"],
        COLLECTOR_PID_FILE, LOGS_DIR / "collector.out.log",
    )
    print(
        "collector: running (Feishu listener). "
        "ollama + translation start on demand when a message arrives."
    )


def stop_services() -> None:
    ensure_dirs()
    mark_stop_requested()
    config = load_config()
    stop_pid_file(COLLECTOR_PID_FILE, "collector")
    stop_pid_file(WATCHER_PID_FILE, "watcher")
    stop_pid_file(player_pid_file(config), "player")
    stop_pid_file(OLLAMA_PID_FILE, "ollama")


def print_status() -> None:
    ensure_dirs()
    config = load_config()
    ollama_state = "running" if ollama.is_ollama_available(config) else "stopped"
    ollama_pid = read_pid(OLLAMA_PID_FILE)
    suffix = f" pid={ollama_pid}" if ollama_pid else ""
    print(f"ollama: {ollama_state}{suffix}")
    try:
        check_tts_ready(config)
    except RuntimeError as exc:
        print(str(exc))
    for label, pid_file in (
        ("watcher", WATCHER_PID_FILE),
        ("collector", COLLECTOR_PID_FILE),
        ("player", player_pid_file(config)),
    ):
        pid = read_pid(pid_file)
        if is_process_alive(pid):
            print(f"{label}: running pid={pid}")
        elif pid:
            print(f"{label}: stopped (stale pid={pid})")
        else:
            print(f"{label}: stopped")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Work2English Radio background services.")
    parser.add_argument("command", choices=["start", "stop", "restart", "status"])
    args = parser.parse_args()
    if args.command == "start":
        try:
            start_services()
        except RuntimeError as exc:
            if str(exc).startswith("start aborted:"):
                print(str(exc))
                return
            raise
    elif args.command == "stop":
        stop_services()
    elif args.command == "restart":
        stop_services()
        start_services()
    elif args.command == "status":
        print_status()


if __name__ == "__main__":
    main()
