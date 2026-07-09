#!/usr/bin/env python3
"""Work2English Radio CLI.

Thin entry over w2e. Modes:
  python run.py --once             # generate if changed, then play (Ctrl+C stops)
  python run.py --watch            # watch the inbox, regenerate on change
  python run.py --player-control F # (internal) afplay loop driven by control file
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from w2e.runtime import ensure_venv_python, chdir_root, ensure_dirs, setup_logger, is_process_alive, read_pid
ensure_venv_python()
chdir_root()

from w2e.config import load_config, player_pid_file
from w2e import generate, playback
from w2e.io_utils import read_text

WATCH_INTERVAL_SECONDS = 2


def run_once(config: dict) -> None:
    result = generate.get_coordinator().run_now(config)
    if not result.get("ok"):
        print(f"Generation failed: {result.get('error') or 'unknown'}")
        return
    pid = read_pid(player_pid_file(config))
    if pid and is_process_alive(pid):
        print(f"Playing (pid={pid}). Press Ctrl+C to stop playback.")
        try:
            while is_process_alive(pid):
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping audio playback.")
            playback.stop_local_player(config)
    else:
        print("Generated. Open the Work2English app to listen.")


def run_watch(config: dict) -> None:
    print("Watching inbox/feishu_raw.md. Press Ctrl+C to stop.")
    coordinator = generate.get_coordinator()
    last_mtime_ns = None
    try:
        while True:
            input_path = Path(config["input_file"])
            input_text = read_text(config["input_file"])
            current_mtime_ns = input_path.stat().st_mtime_ns if input_path.exists() else None
            if input_text and current_mtime_ns != last_mtime_ns:
                try:
                    coordinator.run_now(config)
                    last_mtime_ns = current_mtime_ns
                except Exception:
                    logging.exception("Failed to generate or play audio.")
                    print("Generation failed. Check logs/run.log.")
                    time.sleep(10)
            time.sleep(WATCH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Stopping watcher and audio playback.")
        playback.stop_local_player(config)


def parse_args():
    parser = argparse.ArgumentParser(description="Work2English Radio")
    parser.add_argument("--once", action="store_true", help="Generate once if input changed, then play.")
    parser.add_argument("--watch", action="store_true", help="Watch the inbox and regenerate on change.")
    parser.add_argument("--player-control", metavar="CONTROL_FILE", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.player_control:
        playback.run_player_control_child(args.player_control)
        return
    ensure_dirs()
    config = load_config()
    setup_logger(config["log_file"])
    logging.info("Work2English Radio started.")
    if args.watch:
        run_watch(config)
    else:
        run_once(config)


if __name__ == "__main__":
    main()
