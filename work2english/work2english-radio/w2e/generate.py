"""Generation pipeline + coordinator.

`generate_once(config)` is the single synchronous pipeline (parse → LLM → TTS →
study artifacts → playback control → honest receipts). `GenerationCoordinator`
wraps it with single-flight + debounce so the collector (debounced) and the UI
server (immediate) share one implementation instead of the two parallel ones
that previously lived in feishu_collect.py and server.py.

The cross-process fcntl lock (runtime/generating.lock) stays as the底层 mutual
exclusion so collector + UI can't regenerate concurrently.
"""
from __future__ import annotations

import fcntl
import logging
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from . import study, tts, playback, feishu, ollama, notify
from .io_utils import read_text, write_text, get_hash
from .runtime import PROJECT_ROOT, RUNTIME_DIR

LOCK_FILE = RUNTIME_DIR / "generating.lock"
DEBOUNCE_SECONDS = 2.0


def has_input_changed(current_hash: str, hash_file: str) -> bool:
    p = Path(hash_file)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    if not p.exists():
        return True
    return p.read_text(encoding="utf-8").strip() != current_hash


@contextmanager
def generation_lock():
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOCK_FILE, "w", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def generate_once(config: dict, *, ensure_playback: bool = True, start_ollama: bool = True) -> tuple[bool, str]:
    """Run the full pipeline if the inbox changed.

    Returns (generated, status) where status is the playback coordinator's
    verdict ('playing' / 'waiting'). On 'unchanged', still (re)applies playback
    control so existing content is ready to play, but does not re-send receipts.
    """
    input_text = read_text(config["input_file"])
    if not input_text:
        raise RuntimeError("Input file is empty. Send Feishu content first.")

    if start_ollama:
        try:
            ollama.ensure_ollama_running(config)
        except Exception:
            logging.exception("ensure_ollama_running failed during generation.")

    current_hash = get_hash(input_text)
    audio_path = Path(config["output_audio"])
    if not audio_path.is_absolute():
        audio_path = PROJECT_ROOT / audio_path
    hash_file = config.get("input_hash_file", "runtime/last_input_hash.txt")
    changed = has_input_changed(current_hash, hash_file) or not audio_path.exists()

    if changed:
        logging.info("New input detected. Generating English script + audio.")
        day = study.today_label_from_input(input_text)
        payload = study.build_study_payload(input_text, config)
        if not payload.get("daily_briefing"):
            raise RuntimeError("Generation returned empty content.")
        write_text(config["output_text"], payload["daily_briefing"])
        tts.synthesize(payload["daily_briefing"], config, config["output_audio"])
        study.write_study_artifacts(day, payload, config)
        write_text(hash_file, current_hash)
        logging.info("Generated successfully.")
    else:
        logging.info("Input unchanged; reusing existing audio.")
        day, payload = study.read_study_payload_for_today(config)

    status = "waiting"
    if ensure_playback:
        control = playback.build_player_control(day, payload, config)
        status = playback.PlaybackCoordinator(config).on_generation_ready(control)

    if changed:
        feishu.send_pending_success_receipts(status)
    return changed, status


class GenerationCoordinator:
    """Single-flight (in-process) + debounced generation, shared by collector and UI."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._pending = False
        self._timer: threading.Timer | None = None
        self._timer_lock = threading.Lock()
        self.state: dict[str, Any] = {
            "running": False, "last_result": None, "last_error": None, "finished_at": 0.0,
        }

    @property
    def running(self) -> bool:
        return self.state["running"]

    def run_now(self, config: dict) -> dict:
        """Blocking run for the UI. Returns immediately with already_running if busy."""
        if not self._lock.acquire(blocking=False):
            return {"ok": False, "already_running": True}
        try:
            return self._execute(config)
        finally:
            self._lock.release()

    def schedule(self, config: dict, debounce: float = DEBOUNCE_SECONDS) -> None:
        """Debounced run for the collector: batch rapid messages into one run."""
        with self._timer_lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(debounce, self._trigger, args=(config,))
            self._timer.daemon = True
            self._timer.start()

    def _trigger(self, config: dict) -> None:
        if not self._lock.acquire(blocking=False):
            with self._timer_lock:
                self._pending = True
            logging.info("Generation in progress; queued another run.")
            return
        try:
            while True:
                with self._timer_lock:
                    self._pending = False
                self._execute(config)
                with self._timer_lock:
                    again = self._pending
                    self._pending = False
                if not again:
                    break
                logging.info("Running pending generation after in-flight update.")
        finally:
            self._lock.release()

    def _execute(self, config: dict) -> dict:
        self.state["running"] = True
        self.state["last_error"] = None
        try:
            with generation_lock():
                generated, status = generate_once(config, ensure_playback=True)
            self.state["last_result"] = "generated" if generated else "unchanged"
            if generated:
                notify.notify("Work2English", "新内容已就绪，打开界面收听")
            return {"ok": True, "generated": generated, "status": status}
        except Exception as exc:
            logging.exception("Generation failed.")
            self.state["last_error"] = str(exc)
            return {"ok": False, "error": str(exc)}
        finally:
            self.state["running"] = False
            self.state["finished_at"] = time.time()


# Process-wide singleton: collector + server (when in-process) share one coordinator.
_default: GenerationCoordinator | None = None


def get_coordinator() -> GenerationCoordinator:
    global _default
    if _default is None:
        _default = GenerationCoordinator()
    return _default
