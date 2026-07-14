"""Feishu content acquisition layer.

Each Feishu source (messages, calendar, tasks, ...) is a :class:`SourceProvider`
that owns four concerns: building its lark-cli command, pagination, envelope
normalization, and its own errors. :func:`collect_sources` runs the active
providers in isolation, and records any source failure in ``_issues`` so the
caller can show an incomplete-pull warning instead of silently trusting it.

This module is pure acquisition — it fetches and normalizes raw records. It has
no dependency on curation, summary, TTS, or playback. Curation of the fetched
records lives in :mod:`w2e.daily_digest`.

Adding a new source = add a SourceProvider subclass and register it in
``ACTIVE_PROVIDERS``. No edits to ``collect_sources`` or ``daily_collect.py``
are required.
"""
from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Callable

from .feishu import lark_cli_bin
from .io_utils import write_json
from .runtime import PROJECT_ROOT

logger = logging.getLogger(__name__)

SOURCE_ARCHIVE_DIR = PROJECT_ROOT / "inbox" / "sources"
SOURCE_ISSUES_KEY = "_issues"
CANONICAL_SOURCE_NAMES = ("messages", "calendar", "tasks")


# ─── shared primitives ────────────────────────────────────────────────────────

def day_bounds(day: date | None = None) -> tuple[str, str]:
    """Local-midnight to local-23:59:59 ISO window for ``day`` (default today)."""
    current = day or date.today()
    tz = datetime.now().astimezone().tzinfo
    start = datetime.combine(current, time.min, tzinfo=tz)
    end = datetime.combine(current, time.max, tzinfo=tz)
    return start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds")


def run_json(args: list[str]) -> Any:
    """Run a lark-cli command and parse its stdout as JSON.

    Raises RuntimeError on non-zero exit or non-JSON stdout. Kept as a free
    function so tests can inject a fake via ``CollectContext.runner`` instead
    of monkeypatching subprocess.
    """
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown lark-cli error"
        raise RuntimeError(detail)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"lark-cli returned invalid JSON: {result.stdout[:200]}") from exc


def find_list(value: Any, preferred: tuple[str, ...]) -> list[dict]:
    """Tolerate shortcut / native response envelopes across lark-cli versions.

    Accepts a bare list, a dict whose list lives under any of ``preferred``
    keys, or the same nested under ``data`` / ``result``.
    """
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []
    for key in preferred:
        child = value.get(key)
        if isinstance(child, list):
            return [item for item in child if isinstance(item, dict)]
    for key in ("data", "result"):
        child = value.get(key)
        found = find_list(child, preferred)
        if found:
            return found
    return []


def dedupe_by_keys(items: list[dict], keys: tuple[str, ...]) -> list[dict]:
    """Deduplicate dicts by the first present key in ``keys``, falling back to a
    stable JSON fingerprint so keyless records still dedupe. Order-preserving."""
    seen: set[str] = set()
    result: list[dict] = []
    for item in items:
        identity = next((str(item.get(k)) for k in keys if item.get(k)), "")
        identity = identity or json.dumps(item, ensure_ascii=False, sort_keys=True)
        if identity not in seen:
            seen.add(identity)
            result.append(item)
    return result


def current_user_id() -> str:
    """Resolve the current lark-cli user's open_id (user identity).

    ``auth status`` is JSON by default and, unlike resource shortcuts, does not
    accept ``--format`` in lark-cli 1.0.63.
    """
    payload = run_json([lark_cli_bin(), "auth", "status"])
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("identities", {}).get("user", {}).get("openId", ""))


# ─── provider contract ────────────────────────────────────────────────────────

@dataclass
class CollectContext:
    """Everything a provider needs to fetch one day's slice.

    ``runner`` is injected so tests can fake the lark-cli subprocess without
    touching the real process or needing Feishu permissions.
    """
    day: date
    start: str
    end: str
    cli: str
    runner: Callable[[list[str]], Any] = run_json


class SourceProvider:
    """Base class for one Feishu acquisition source.

    Subclasses set ``name`` and ``active`` and implement :meth:`collect`.
    ``active`` controls whether :func:`collect_sources` includes it; reserved
    providers keep their interface and TODO reasoning visible so future
    activation is a one-flag flip.
    """
    name: str = ""
    active: bool = True

    def collect(self, ctx: CollectContext) -> list[dict]:  # pragma: no cover - contract
        raise NotImplementedError

    def _list(self, ctx: CollectContext, args: list[str], envelope: tuple[str, ...]) -> list[dict]:
        return find_list(ctx.runner(args), envelope)


class MessagesProvider(SourceProvider):
    """P2P + group messages visible to the user within [start, end].

    ``--page-all`` follows every page server-side; ``--no-reactions`` drops
    reaction noise. Fetched as the user identity (the bot cannot read personal
    messages)."""
    name = "messages"

    def collect(self, ctx: CollectContext) -> list[dict]:
        return self._list(ctx, [
            ctx.cli, "im", "+messages-search", "--query", "", "--start", ctx.start,
            "--end", ctx.end, "--page-size", "50", "--page-all", "--no-reactions",
            "--format", "json", "--as", "user",
        ], ("items", "messages"))


class CalendarProvider(SourceProvider):
    """Calendar agenda entries within [start, end] (user identity)."""
    name = "calendar"

    def collect(self, ctx: CollectContext) -> list[dict]:
        return self._list(ctx, [
            ctx.cli, "calendar", "+agenda", "--start", ctx.start, "--end", ctx.end,
            "--format", "json", "--as", "user",
        ], ("items", "events"))


class TasksProvider(SourceProvider):
    """Tasks created or due on ``day`` (user identity), merged and deduped."""
    name = "tasks"

    def collect(self, ctx: CollectContext) -> list[dict]:
        day_string = ctx.day.isoformat()
        created = self._list(ctx, [
            ctx.cli, "task", "+get-my-tasks", "--created_at", day_string,
            "--page-all", "--format", "json", "--as", "user",
        ], ("items", "tasks"))
        due = self._list(ctx, [
            ctx.cli, "task", "+get-my-tasks", "--due-start", day_string,
            "--due-end", day_string, "--page-all", "--format", "json", "--as", "user",
        ], ("items", "tasks"))
        return dedupe_by_keys(created + due, ("task_id", "id", "guid"))


# ─── reserved providers (interface designed, not yet active) ──────────────────

class DocsInMessagesProvider(SourceProvider):
    """Reserved: fetch the body of each Feishu doc linked in the day's messages.

    NOT active. TODO / reasons:

    - Derived source — must first scan :class:`MessagesProvider` output for
      ``/docx/`` / ``/doc/`` / ``/wiki/`` URLs.
    - Each link needs its own fetch (``lark-cli docs +fetch`` for docx, or wiki
      ``get_node`` then docx ``raw_content``), with rate limiting, per-doc
      permission handling, and dedup against already-archived docs.
    - The daily pull must stay cheap; eagerly fetching every linked doc risks
      heavy, recursive reads on doc-heavy days.

    Activation plan: accept the messages list via the context, resolve URLs,
    fetch with bounded concurrency + a per-doc cache, and return
    ``[{"url", "title", "content"}]``.
    """
    name = "docs"
    active = False

    def collect(self, ctx: CollectContext) -> list[dict]:
        logger.info("docs-in-messages provider is reserved (not active); skipping.")
        return []


class MinutesProvider(SourceProvider):
    """Reserved: meeting minutes / transcripts for meetings on ``day``.

    lark-cli 1.0.63 exposes the ``minutes`` (content + metadata) and ``note``
    (meeting note / unified transcript) domains, so the capability exists.
    NOT active:

    - The exact list/envelope shape for "minutes on a given day" is unverified
      (no real sample to normalize against here), so a live command would be a
      guess.
    - Requires user OAuth scope for minutes/note read; most days have none.

    Activation plan: list meetings from :class:`CalendarProvider`, fetch each
    meeting's minutes/note, normalize to ``[{"meeting", "title", "transcript"}]``.
    """
    name = "minutes"
    active = False

    def collect(self, ctx: CollectContext) -> list[dict]:
        logger.info("minutes provider is reserved (not active); skipping.")
        return []


# ─── registry & orchestration ─────────────────────────────────────────────────

#: Sources that ``collect_sources`` fetches by default. Order only affects
#: archive key order, not semantics.
ACTIVE_PROVIDERS: list[SourceProvider] = [
    MessagesProvider(),
    CalendarProvider(),
    TasksProvider(),
]

#: All known providers, including reserved ones. Useful for documentation and
#: for callers that want to opt into a reserved provider explicitly.
ALL_PROVIDERS: list[SourceProvider] = ACTIVE_PROVIDERS + [
    DocsInMessagesProvider(),
    MinutesProvider(),
]


def collect_sources(
    day: date | None = None,
    *,
    providers: list[SourceProvider] | None = None,
    runner: Callable[[list[str]], Any] | None = None,
    cli: str | None = None,
) -> dict[str, list[dict]]:
    """Fetch every active source for ``day``, each in isolation.

    A provider that raises (CLI error, bad JSON, network) is recorded as an
    empty list plus a ``_issues`` entry; it never aborts the other sources.
    Callers must surface these issues before treating the digest as complete.

    Pass ``providers``, ``runner`` and/or ``cli`` to inject fakes in tests —
    e.g. a fake ``runner`` with ``cli="lark-cli"`` exercises the full provider
    pipeline without needing lark-cli installed or any Feishu permissions.
    """
    start, end = day_bounds(day)
    ctx = CollectContext(
        day=day or date.today(),
        start=start,
        end=end,
        cli=cli if cli is not None else lark_cli_bin(),
        runner=runner or run_json,
    )
    pool = providers if providers is not None else ACTIVE_PROVIDERS
    active = [p for p in pool if getattr(p, "active", True)]
    sources: dict[str, list[dict]] = {}
    issues: list[dict] = []
    for provider in active:
        try:
            sources[provider.name] = list(provider.collect(ctx))
        except Exception as exc:  # isolate per-source failures
            logger.warning("Feishu source %s failed: %s", provider.name, exc)
            sources[provider.name] = []
            issues.append({"source": provider.name, "error": str(exc)})
    if issues:
        sources[SOURCE_ISSUES_KEY] = issues
    return sources


def source_counts(sources: dict[str, list[dict]]) -> dict[str, int]:
    """Per-source counts, with canonical sources first and internal keys hidden."""
    counts = {key: len(sources.get(key, [])) for key in CANONICAL_SOURCE_NAMES}
    for key, value in sources.items():
        if key in counts or key.startswith("_"):
            continue
        counts[key] = len(value) if isinstance(value, list) else 0
    return counts


def source_issues(sources: dict[str, list[dict]]) -> list[dict]:
    issues = sources.get(SOURCE_ISSUES_KEY, [])
    return issues if isinstance(issues, list) else []


def has_source_issue(sources: dict[str, list[dict]], source_name: str) -> bool:
    return any(issue.get("source") == source_name for issue in source_issues(sources))


def write_source_archive(day: date, sources: dict[str, list[dict]]) -> Path:
    """Persist the raw acquired sources for debugging/review.

    The archive is deliberately written under ``inbox/sources/`` which is
    git-ignored except for ``.gitkeep``, so real Feishu data is never committed.
    """
    path = SOURCE_ARCHIVE_DIR / f"feishu-{day.isoformat()}.json"
    write_json(path, sources)
    return path
