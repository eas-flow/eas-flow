# Coding conventions / コーディング規約

Minimal, enforced-where-possible conventions. Prefer clarity over cleverness.

## General
- UTF-8, LF line endings, final newline. No trailing whitespace.
- Keep changes scoped to the issue; avoid unrelated refactors in the same PR.
- English for code and identifiers; Japanese is fine in docs and skill bodies.

## Python (scripts/)
- Target Python 3.10+. Standard library first; third-party only when justified
  (currently `pyyaml`, `jsonschema` for CI only).
- Add a module docstring, type hints, and clear exit codes. No bare `except`.
- Format/lint with `ruff` (added in the Lint/format issue).

## JSON / YAML
- 2-space indent. Valid against schema where one exists
  (`plugin.config.schema.json`).
- `.github/*.yml` and manifests must parse cleanly (CI checks this).

## Markdown
- One H1 per file. Reference-friendly relative links.
- Wrap prose reasonably; do not hard-wrap tables.

## SKILL.md
- `name` must equal the skill's directory name.
- **Quote `description` and `hint`** — they contain `:` / `/` and break strict YAML
  otherwise (see the frontmatter gotcha in CLAUDE.md).
- Drive all project-specific values from `plugin.config.json`; never hardcode a
  repo, directory, or branch.
- Preserve safety gates (wrong-branch refusal, uncommitted-change stop, quality
  gate, user approval before build/version-bump/release).
