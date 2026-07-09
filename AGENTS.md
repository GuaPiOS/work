# Repository Agent Rules

This repository contains a Chinese context-engineering learning/book project, a Swift macOS app under `apps/wordydesk`, and a file-based context system under `second-brain-os`.

## Start Here

- Read `README.md` before making repository-wide changes.
- For WordyDesk work, read `apps/wordydesk/README.md` and nearby source files first.
- For `second-brain-os` work, read `second-brain-os/AGENTS.md` and follow its context routing rules.
- Keep changes focused on the requested task. Do not reformat unrelated files.

## Git Workflow

- Do not work directly on `main` for feature or bug-fix tasks.
- Use focused branches named `agent/<issue-or-topic>` or `codex/<issue-or-topic>`.
- Prefer small commits with clear messages.
- Do not commit generated build outputs, local caches, or secrets.
- Before opening a PR, summarize changed files, tests run, and known risks.

## Verification

- For root Node dependency checks, run `npm ci` when dependencies need validation.
- For WordyDesk changes, run `swift build --package-path apps/wordydesk`.
- For Second Brain OS project structure changes, run `python3 second-brain-os/agents/scripts/validate_project.py`.
- If a relevant test cannot be run locally, state the reason in the PR.

## Review Guidelines

- Flag missing tests or missing manual verification for user-facing behavior.
- Flag accidental changes to generated files, build outputs, caches, or private notes.
- Treat secrets, API keys, tokens, and private personal data as release blockers.
- Do not merge your own PR. Human review is required for production-facing changes.

## PR Description Format

Use this structure:

```markdown
## Summary

-

## Tests

-

## Risk

-
```
