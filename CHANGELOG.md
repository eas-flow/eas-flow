# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [0.1.0] - unreleased
Target scope: `deploy` and `release-draft` skills working end-to-end on a real
Expo project via `plugin.config.json`.

[Unreleased]: https://github.com/eas-flow/eas-flow/compare/main...develop
