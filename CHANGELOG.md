# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-29

### Added

- `develop-work` skill: cuts a work branch off the integration branch from an
  issue, delegates investigation to the `explorer` subagent, runs the
  lint/typecheck(/test) quality gate, then opens a PR. #28
- `doc-sync` skill: compares `plugin.config.json`'s `docSync` target docs
  against SSOT files over a commit range, delegates drift detection to the
  `doc-auditor` subagent, and applies edits only after user approval. #29
- `agents/explorer.md`: read-only subagent that investigates target files,
  existing implementation patterns, and impact scope before implementation
  starts. #30
- `agents/doc-auditor.md`: read-only subagent that compares `docSync` target
  docs against SSOT files and lists discrepancies. #30

## [0.1.0] - 2026-07-28

### Added
- Repository scaffolding: MIT license, `.gitignore`, README skeleton.
- Claude Code plugin manifest (`.claude-plugin/plugin.json`) and marketplace
  entry (`.claude-plugin/marketplace.json`).
- Config loader (`scripts/load-config.py`), `plugin.config.schema.json`, and
  `plugin.config.example.json`.
- `deploy` skill: config-driven EAS production build & submit.
- `release-draft` skill: config-driven version bump, release PR, and release notes.
- Bilingual documentation (`README.md`, `README.ja.md`).
- CI workflow validating plugin manifests and skill frontmatter.
- Repo formatting/lint: `.editorconfig`, Prettier (JSON/YAML/Markdown), `ruff`
  for `scripts/`, and a CI `format` job. #21
- `requirements-dev.txt` pinning CI/dev dependencies (`pyyaml`, `jsonschema`,
  `pytest`). #34
- Unit test suite (`tests/`, pytest) covering `scripts/load-config.py` and
  `scripts/validate_plugin.py`. #33
- `load-config.py` now validates the resolved config against
  `plugin.config.schema.json` (strict, path-annotated errors) when `jsonschema`
  is installed, falling back to the previous minimal checks otherwise;
  `appDir`/`appConfigPath` are now `required` in the schema. #32
- `validate_plugin.py` now checks that `.claude-plugin/plugin.json`'s `version`
  matches its entry in `marketplace.json`, so the two can't silently drift. #31

Target scope: `deploy` and `release-draft` skills working end-to-end on a real
Expo project via `plugin.config.json`.

[Unreleased]: https://github.com/eas-flow/eas-flow/compare/main...develop
[0.2.0]: https://github.com/eas-flow/eas-flow/releases/tag/Ver0.2.0
[0.1.0]: https://github.com/eas-flow/eas-flow/releases/tag/Ver0.1.0
