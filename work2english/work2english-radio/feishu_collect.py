#!/usr/bin/env python3
"""Feishu collector entry point.

Thin wrapper around w2e.feishu (parsing / dedupe / inbox / receipts) and
w2e.generate (debounced generation). The collector stays lightweight at idle;
generation + ollama spin up on demand when a message arrives.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from w2e.runtime import (
    ensure_venv_python, chdir_root, ensure_dirs, setup_logger,
    PROJECT_ROOT, RUNTIME_DIR, LOGS_DIR, OLLAMA_PID_FILE,
    is_process_alive, read_pid, stop_pid_file,
    seconds_idle, IDLE_SHUTDOWN_SECONDS,
)
ensure_venv_python()
chdir_root()

from w2e.config import load_config, player_pid_file
from w2e import feishu, generate, runtime

COLLECTOR_STARTED_AT_MS = int(time.time() * 1000)


def _idle_watchdog(config: dict) -> None:
    """Stop ollama + player after IDLE_SHUTDOWN_SECONDS with no activity."""
    from w2e import ollama, playback

    def heavy_active() -> bool:
        return ollama.is_ollama_available(config) or is_process_alive(read_pid(player_pid_file(config)))

    while True:
        time.sleep(15)
        try:
            if seconds_idle() >= IDLE_SHUTDOWN_SECONDS and heavy_active():
                playback.stop_local_player(config)
                stop_pid_file(OLLAMA_PID_FILE, "ollama")
                logging.info("Idle %.0fs ≥ %ds: stopped ollama + player.", seconds_idle(), IDLE_SHUTDOWN_SECONDS)
        except Exception:
            logging.exception("idle watchdog iteration failed.")


def consume_events(config: dict) -> None:
    event_type = config["feishu"].get("event_type", "im.message.receive_v1")
    cmd = [feishu.lark_cli_bin(), "event", "consume", event_type, "--as", "bot", "--quiet"]
    coordinator = generate.get_coordinator()
    while True:
        logging.info("Starting event consumer: %s", " ".join(cmd))
        process = subprocess.Popen(
            cmd, cwd=PROJECT_ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                logging.warning("Skipping non-JSON event line: %s", line)
                continue
            try:
                feishu.process_event(
                    event, config,
                    collector_started_at_ms=COLLECTOR_STARTED_AT_MS,
                    on_ready=coordinator.schedule,
                )
            except Exception as exc:
                feishu.save_failure(event, f"unexpected processing error: {exc}", feishu.content_to_text(event.get("content")))
        return_code = process.wait()
        stderr = process.stderr.read().strip() if process.stderr else ""
        logging.warning("Event consumer exited rc=%s stderr=%s", return_code, stderr)
        time.sleep(5)


def parse_args():
    parser = argparse.ArgumentParser(description="Collect Feishu bot messages into Work2English inbox.")
    parser.add_argument("--event-file", help="Process one local JSON event file for testing, then exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    setup_logger("logs/collect.log")
    config = load_config()

    if not config.get("collector", {}).get("enabled", True):
        print("Collector is disabled in config.yaml.")
        return

    coordinator = generate.get_coordinator()
    if args.event_file:
        event = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
        feishu.process_event(
            event, config,
            collector_started_at_ms=COLLECTOR_STARTED_AT_MS,
            on_ready=coordinator.run_now,
        )
        return

    watchdog = threading.Thread(target=_idle_watchdog, args=(config,), daemon=True)
    watchdog.start()
    consume_events(config)


if __name__ == "__main__":
    main()
