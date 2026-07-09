# Claude Code Project Instructions

Follow the same repository rules as `AGENTS.md`.

## Project Shape

- `curriculum/`, `chapters/`, and `manuscript/` contain the Chinese learning and book-writing materials.
- `apps/wordydesk/` contains a standalone Swift macOS menu-bar app.
- `second-brain-os/` contains a file-based context operating system with its own rules in `second-brain-os/AGENTS.md`.

## Package and Build Commands

- Root dependency install: `npm ci`
- WordyDesk build: `swift build --package-path apps/wordydesk`
- Second Brain OS validation: `python3 second-brain-os/agents/scripts/validate_project.py`

## Working Rules

- Use branch-based work. Do not push directly to `main`.
- Prefer small, focused PRs.
- Do not modify generated files, build outputs, caches, or local app data.
- Do not place API keys, GitHub tokens, model keys, or cloud credentials in files or prompts.
- For documentation updates, preserve the existing Chinese writing style and structure.

## Pull Requests

PR descriptions must include:

- `Summary`: what changed and why.
- `Tests`: exact commands run or why they were not run.
- `Risk`: known limitations, migration concerns, or follow-up checks.
