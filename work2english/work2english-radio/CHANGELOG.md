# Changelog

## 0.3.1 - Unreleased

### Changed

- 学习记录现在是打开界面的默认首页，并排在第一标签；今日训练保留为第二入口。
- 收紧学习记录顶部摘要的视觉占比，摘要默认折叠，需要时手动展开；状态菜单提升层级，避免被导航遮挡。
- 将“重点短语”改为 A2→B1 更容易复用的“常用句型”，学习提示改为简短、少术语的中文说明。
- 优化本地模型提示词：英文更接近日常同事间的口语表达，优先短句、高频词和自然缩写，减少生硬直译与过难词汇。
- 日常英文播报开场改为更自然的口语表达：`Here’s a quick update from today.`。

- 修复机器人直发内容的默认播放范围：默认从“只播放最新一批”改为播放当天全部内容；`auto` 仍保留为手动选择的最新内容模式。
- 明确当天机器人消息会持续追加到当天收件箱和学习表，不会因为后续消息到达而删除先前内容。

- 重做 UI 信息架构：将“今日训练”和“学习记录”提升为两个清晰的用户入口；今日训练按“选择内容 → 英文稿 → 开始播放”推进，学习记录负责长期复习。
- 统一用户界面为中文，隐藏技术路径和内部服务术语；系统状态改为“正常 / 待机 / 处理中 / 需要处理”等用户可理解的状态。
- 移除固定视口高度和全局页面锁定滚动；学习记录增加独立滚动区域、固定表头和小屏横向查看提示。
- 统一视觉为安静的工作台风格：减少玻璃层级、降低装饰噪声、使用中文友好字体和单一主色强调。

- Extracted the Feishu acquisition logic out of `w2e/daily_digest.py` into a dedicated `w2e/feishu_sources.py` acquisition layer. Each source (messages, calendar, tasks) is now a `SourceProvider` that owns its lark-cli command, pagination, envelope normalization, and errors. Adding a source = add a provider and register it.
- `collect_sources` now runs every active source **in isolation**: a single source failing (CLI error, bad JSON, network) is recorded as an empty list plus a visible `_issues` entry instead of aborting the whole daily pull. Previously any one failure lost all sources for the day.
- `daily_digest.py` is now curation / rendering / policy only — no lark-cli calls remain in it.
- `daily_collect.py` CLI arguments (`--date` / `--collect-only` / `--force-generate`) are unchanged; output now surfaces source warnings when a source pull is incomplete.
- If the messages source fails, `daily_collect.py` writes the digest and archive but skips English/audio generation by default. Use `--force-generate` only when an incomplete digest is acceptable.
- The UI/server now auto-refreshes the daily Feishu English preview on weekdays using `daily_digest.schedule`.
- Daily digest curation now removes obvious @mentions / Feishu at-tags and filters low-value machine notices such as Odoo freight, logistics, order status, and identifier-heavy messages.

### Added

- Reserved provider interfaces for future sources: `DocsInMessagesProvider` (doc bodies linked in messages) and `MinutesProvider` (meeting minutes / transcripts). Both are inactive by design — lark-cli's `minutes` / `note` domains exist, but the response envelopes and required permissions are unverified, and doc fetching needs per-link rate limiting + dedup. Their interfaces and TODO reasoning are documented in code so activation is a one-flag flip.
- Added `feishu_fetch_mvp.py`, a minimal Feishu fetch smoke-test command that prints counts and optional previews without touching the inbox, Ollama, TTS, or playback.
- Added `daily_collect.py --preview-english` to print a bilingual preview in the terminal without writing the playback inbox, synthesizing audio, or starting playback.
- Added `w2e/daily_scheduler.py` for weekday preview scheduling.

### Verified

- Added `tests/test_feishu_sources.py` covering each provider's command shape, envelope normalization (`items` / `messages` / `events` / `tasks` keys, bare list, nested `data` / `result`), empty results, CLI errors, per-source isolation in `collect_sources`, visible source issues, reserved (inactive) providers, and the source-archive gitignore contract.

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
