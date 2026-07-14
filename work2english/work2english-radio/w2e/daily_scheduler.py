"""Weekday scheduler for automatic daily Feishu preview refreshes."""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Callable

from .io_utils import read_json, write_json
from .runtime import RUNTIME_DIR

STATE_FILE = RUNTIME_DIR / "daily_scheduler_state.json"
DEFAULT_TIMES = ("09:30", "12:30", "18:00")
DEFAULT_WEEKDAYS = (1, 2, 3, 4, 5)  # ISO weekday: Monday=1


def schedule_config(config: dict) -> dict:
    raw = (config.get("daily_digest", {}) or {}).get("schedule", {}) or {}
    return {
        "enabled": bool(raw.get("enabled", True)),
        "weekdays": tuple(int(x) for x in raw.get("weekdays", DEFAULT_WEEKDAYS)),
        "times": tuple(str(x) for x in raw.get("times", DEFAULT_TIMES)),
    }


def due_slots(now: datetime, config: dict) -> list[str]:
    schedule = schedule_config(config)
    if not schedule["enabled"] or now.isoweekday() not in schedule["weekdays"]:
        return []
    current_minutes = now.hour * 60 + now.minute
    slots: list[str] = []
    for slot in schedule["times"]:
        try:
            hour, minute = [int(part) for part in slot.split(":", 1)]
        except ValueError:
            logging.warning("Ignoring invalid daily digest schedule time: %s", slot)
            continue
        if current_minutes >= hour * 60 + minute:
            slots.append(slot)
    return slots


def completed_key(now: datetime, slot: str) -> str:
    return f"{now.date().isoformat()} {slot}"


def should_run(now: datetime, config: dict) -> tuple[bool, str]:
    state = read_json(STATE_FILE, {})
    completed = set(state.get("completed", [])) if isinstance(state, dict) else set()
    for slot in due_slots(now, config):
        key = completed_key(now, slot)
        if key not in completed:
            return True, key
    return False, ""


def mark_done(key: str) -> None:
    state = read_json(STATE_FILE, {})
    completed = list(state.get("completed", [])) if isinstance(state, dict) else []
    if key not in completed:
        completed.append(key)
    # Keep state bounded; 60 weekday slots is enough for several weeks.
    write_json(STATE_FILE, {"completed": completed[-60:]}, indent=2)


def start_weekday_preview_scheduler(
    load_config: Callable[[], dict],
    run_preview: Callable[[dict], None],
    *,
    interval_seconds: int = 60,
) -> None:
    def loop() -> None:
        while True:
            try:
                config = load_config()
                run, key = should_run(datetime.now(), config)
                if run:
                    logging.info("Daily Feishu preview scheduler running slot %s.", key)
                    run_preview(config)
                    mark_done(key)
            except Exception:
                logging.exception("Daily Feishu preview scheduler failed.")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
