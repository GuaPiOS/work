"""Optional retention cleanup for accumulated runtime artifacts.

Off by default — only runs when config.retention.days is set to a positive int.
Prunes inbox/events, inbox/failed, and output/study/<day>/ directories older
than the configured window. Daily rollups (inbox/daily) and the current inbox
file are never touched.

Best-effort and fault-tolerant: a cleanup failure logs but never breaks startup.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

from .runtime import PROJECT_ROOT, INBOX_DIR, OUTPUT_DIR


def _prune_dir_children(parent: Path, pattern: str, max_age_seconds: float, now: float) -> int:
    """Delete children of `parent` matching `pattern` older than max_age. Returns count removed."""
    removed = 0
    if not parent.exists():
        return 0
    for child in parent.glob(pattern):
        try:
            mtime = child.stat().st_mtime
        except OSError:
            continue
        if now - mtime <= max_age_seconds:
            continue
        try:
            if child.is_dir():
                import shutil
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
            removed += 1
        except OSError as exc:
            logging.warning("retention: could not remove %s: %s", child, exc)
    return removed


def cleanup_old_artifacts(config: dict) -> dict:
    """Prune old events/failed/study dirs per config.retention.days. No-op if unconfigured."""
    days = int((config.get("retention", {}) or {}).get("days", 0))
    if days <= 0:
        return {"enabled": False, "removed": 0}
    max_age = days * 86400
    now = time.time()
    removed = 0
    removed += _prune_dir_children(INBOX_DIR / "events", "*.json", max_age, now)
    removed += _prune_dir_children(INBOX_DIR / "failed", "*.json", max_age, now)
    removed += _prune_dir_children(OUTPUT_DIR / "study", "*", max_age, now)
    logging.info("retention: pruned %d artifact(s) older than %dd", removed, days)
    return {"enabled": True, "days": days, "removed": removed}
