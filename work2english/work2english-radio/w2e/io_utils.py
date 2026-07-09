"""Tiny file / json / hash helpers (stdlib only).

All relative paths resolve against PROJECT_ROOT, so behaviour no longer depends
on the process cwd.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else PROJECT_ROOT / p


def read_text(path: str | Path) -> str:
    file_path = _resolve(path)
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("", encoding="utf-8")
        return ""
    return file_path.read_text(encoding="utf-8").strip()


def write_text(path: str | Path, content: str) -> None:
    file_path = _resolve(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def read_json(path: str | Path, default: Any = None) -> Any:
    file_path = _resolve(path)
    if not file_path.exists():
        return default
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: str | Path, data: Any, indent: int = 2) -> None:
    file_path = _resolve(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8")


def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
