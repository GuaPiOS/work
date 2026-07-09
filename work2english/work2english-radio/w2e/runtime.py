"""Process & runtime utilities (stdlib only).

Import-safe before the venv interpreter switch, so entry points can do
`from w2e.runtime import ensure_venv_python` first, then load heavy deps.

Consolidates what was previously duplicated across run.py, radio_service.py,
and feishu_collect.py (ensure_venv_python / ensure_dirs / setup_logger /
is_process_alive / stop_pid_file / start_process / activity tracking /
stop-request handshake).
"""
from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
LOGS_DIR = PROJECT_ROOT / "logs"
INBOX_DIR = PROJECT_ROOT / "inbox"
OUTPUT_DIR = PROJECT_ROOT / "output"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

WATCHER_PID_FILE = RUNTIME_DIR / "watcher.pid"
COLLECTOR_PID_FILE = RUNTIME_DIR / "collector.pid"
OLLAMA_PID_FILE = RUNTIME_DIR / "ollama.pid"
PLAYER_PID_FILE_DEFAULT = RUNTIME_DIR / "player.pid"
STOP_REQUEST_FILE = RUNTIME_DIR / "stop.request"
ACTIVITY_FILE = RUNTIME_DIR / "last_activity"
IDLE_SHUTDOWN_SECONDS = 180

# Ollama unloads the model from RAM after this many seconds idle; the serve
# process itself stays up so the next message is fast.
os.environ.setdefault("OLLAMA_KEEP_ALIVE", "60s")


def chdir_root() -> None:
    os.chdir(PROJECT_ROOT)


def ensure_venv_python() -> None:
    """Re-exec under the project venv interpreter if we're not already in it."""
    venv_root = PROJECT_ROOT / ".venv"
    venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    if venv_python.exists() and Path(sys.prefix).resolve() != venv_root.resolve():
        subprocess.run([str(venv_python), *sys.argv], cwd=PROJECT_ROOT, check=False)
        sys.exit(0)


def ensure_dirs() -> None:
    for d in (
        RUNTIME_DIR, LOGS_DIR, INBOX_DIR,
        INBOX_DIR / "events", INBOX_DIR / "failed", INBOX_DIR / "daily",
        OUTPUT_DIR, OUTPUT_DIR / "study", PROMPTS_DIR,
    ):
        d.mkdir(parents=True, exist_ok=True)


def ignore_sighup() -> None:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)


def setup_logger(log_file: str | Path = "logs/run.log") -> None:
    """Configure root logging with a rotating file handler (2 MB × 3 backups).

    Idempotent: only attaches a handler if the root logger has none, so calling
    it from multiple entry points doesn't pile up duplicate handlers."""
    from logging.handlers import RotatingFileHandler

    path = Path(log_file)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        return
    handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    root.addHandler(handler)
    root.setLevel(logging.INFO)


# ─── process / pid ────────────────────────────────────────────────────────────

def read_pid(pid_file: Path | str | None) -> int | None:
    if not pid_file:
        return None
    path = Path(pid_file)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def is_process_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    stat = subprocess.run(
        ["ps", "-p", str(pid), "-o", "stat="],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    if not stat or "Z" in stat:
        return False
    return True


def process_command(pid: int) -> str:
    return subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True, text=True, check=False,
    ).stdout.strip()


def _safe_unlink(pid_file: Path) -> None:
    """unlink that tolerates a mount refusing removal; blanks the file as fallback."""
    try:
        pid_file.unlink(missing_ok=True)
    except OSError:
        try:
            pid_file.write_text("", encoding="utf-8")
        except OSError:
            pass


def stop_pid_file(pid_file: Path | str, label: str) -> None:
    path = Path(pid_file)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    pid = read_pid(path)
    if not pid:
        _safe_unlink(path)
        print(f"{label}: not running")
        return
    if not is_process_alive(pid):
        _safe_unlink(path)
        print(f"{label}: stale pid removed")
        return
    print(f"Stopping {label} pid={pid} ...")
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except PermissionError:
        os.kill(pid, signal.SIGTERM)
    for _ in range(30):
        if not is_process_alive(pid):
            break
        time.sleep(0.1)
    if is_process_alive(pid):
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except PermissionError:
            os.kill(pid, signal.SIGKILL)
    _safe_unlink(path)
    print(f"{label}: stopped")


def start_process(
    label: str,
    cmd: list[str],
    pid_file: Path,
    log_file: Path,
    abort_check=None,
) -> None:
    """Start a detached child (own session, ignores SIGHUP) and record its pid."""
    if abort_check:
        abort_check()
    pid = read_pid(pid_file)
    if is_process_alive(pid):
        print(f"{label}: already running pid={pid}")
        return
    _safe_unlink(pid_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_file.open("a", encoding="utf-8")
    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        preexec_fn=ignore_sighup,
        start_new_session=True,
        text=True,
    )
    log_handle.close()
    pid_file.write_text(str(process.pid), encoding="utf-8")
    print(f"{label}: started pid={process.pid}, log={log_file.relative_to(PROJECT_ROOT)}")


def ensure_running(
    label: str,
    cmd: list[str],
    pid_file: Path,
    log_file: Path,
) -> bool:
    """Idempotent keep-alive: if already running, do nothing; if a stop was
    requested, bail; otherwise start it. Used by the collector self-heal loop
    and by radio_service.start."""
    if stop_requested():
        return False
    if is_process_alive(read_pid(pid_file)):
        return True
    try:
        clear_stop_requested()
        start_process(label, cmd, pid_file, log_file)
        return True
    except RuntimeError:
        return False


# ─── stop-request handshake ─────────────────────────────────────────────────

def mark_stop_requested() -> None:
    RUNTIME_DIR.mkdir(exist_ok=True)
    STOP_REQUEST_FILE.write_text(str(time.time()), encoding="utf-8")


def clear_stop_requested() -> None:
    try:
        STOP_REQUEST_FILE.unlink(missing_ok=True)
    except OSError:
        try:
            STOP_REQUEST_FILE.write_text("", encoding="utf-8")
        except OSError:
            pass


def stop_requested() -> bool:
    if not STOP_REQUEST_FILE.exists():
        return False
    try:
        return STOP_REQUEST_FILE.read_text(encoding="utf-8").strip() != ""
    except OSError:
        return False


def abort_if_stop_requested() -> None:
    if stop_requested():
        raise RuntimeError("start aborted: stop was requested")


# ─── idle auto-shutdown activity tracking ─────────────────────────────────────

def touch_activity() -> None:
    try:
        RUNTIME_DIR.mkdir(exist_ok=True)
        ACTIVITY_FILE.write_text(str(time.time()), encoding="utf-8")
    except OSError:
        pass


def seconds_idle() -> float:
    if not ACTIVITY_FILE.exists():
        return 0.0
    try:
        ts = float(ACTIVITY_FILE.read_text(encoding="utf-8").strip())
        return max(0.0, time.time() - ts)
    except (ValueError, OSError):
        return 0.0
