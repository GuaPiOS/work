# Changelog

## 0.3.0 - 2026-07-13

### Added

- Added an independent daily Feishu digest flow: collect sources, archive raw data, write a curated Chinese digest, then optionally feed the existing Work2English generator.
- Added `inbox/digest/YYYY-MM-DD.md` as the human-readable daily learning document.
- Added `inbox/sources/feishu-YYYY-MM-DD.json` as the raw source archive for debugging and review.
- Added idle-aware generation policy for daily digest runs with `daily_digest.generation_policy` and `daily_digest.min_idle_seconds`.
- Added `daily_collect.py --force-generate` to bypass the idle policy for manual testing.
- Added A2 to B1 learning-level configuration through `daily_digest.target_level`.

### Changed

- Daily digest reruns now replace previous daily digest sections while preserving content manually sent to the Feishu bot.
- Daily digest generation now uses the same study generator as the bot entry point, keeping the core English/TTS path shared.

### Verified

- Added unit coverage for digest document rendering, source archiving, inbox replacement, and idle generation decisions.
