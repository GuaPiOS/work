"""Best-effort macOS user notification via osascript (zero-dependency).

Surfaces 'generation finished' to the user even though the service runs
headless under launchd. Must never raise — a notification failure must not
break generation.
"""
from __future__ import annotations

import logging
import subprocess

_APPLESCRIPT = """on run argv
    display notification (item 1 of argv) with title (item 2 of argv) sound name (item 3 of argv)
end run"""


def notify(title: str, body: str, sound: str = "Glass") -> None:
    """Post a macOS notification. Fails silently."""
    try:
        subprocess.run(
            ["osascript", "-e", _APPLESCRIPT, body, title, sound],
            check=False,
            capture_output=True,
            timeout=5,
        )
    except Exception:
        logging.exception("macOS notification failed (ignored).")
