# Contributing to eas-flow

Thanks for your interest! This guide covers the development flow. For AI agents,
see [CLAUDE.md](./CLAUDE.md); for conventions, see
[.claude/rules/](./.claude/rules/README.md).

日本語話者へ: 要点は各セクションに日本語でも併記しています。

## Prerequisites / 前提ツール

- Git and [GitHub CLI](https://cli.github.com) (`gh`), authenticated
- Python 3.10+ (for the config loader and validator)
- For testing the skills against a real project: Node.js, `eas-cli`, an Expo app

## Setup / セットアップ

```bash
git clone https://github.com/eas-flow/eas-flow.git
cd eas-flow
pip install pyyaml jsonschema   # for the validator
python3 scripts/validate_plugin.py
```

To try the plugin locally in Claude Code:

```
/plugin marketplace add eas-flow/eas-flow
/plugin install eas-flow@eas-flow
```

## Branching model / ブランチ運用

- `main` — production. `develop` — integration.
- Cut a work branch from the latest `develop`, named `<prefix>/#<issue>`
  (e.g. `feat/#23`). 作業ブランチは最新 `develop` から切る。

```bash
git switch develop && git pull --ff-only
git switch -c "feat/#23"
```

## Commit & PR conventions / コミット・PR 規約

- Prefix subjects: `feat:` / `fix:` / `chore:` / `docs:` / `ci:` / `refactor:` /
  `perf:`, ending with the issue number — `feat: add develop-work skill #23`.
- Open PRs into `develop` using
  [the PR template](./.github/pull_request_template.md); link the issue with
  `Closes #N`.
- Never push directly to `main` / `develop`; never force-push shared branches.

## Before opening a PR / PR 前チェック

```bash
python3 scripts/validate_plugin.py
```

This validates the plugin manifests, `SKILL.md` frontmatter, and the example
config. CI runs the same check on every PR — please make sure it passes.

## Adding a skill / スキル追加時

1. `skills/<name>/SKILL.md` — `name` must equal the directory name.
2. Quote `description` / `hint` (they contain `:` and `/`).
3. Drive project-specific values from `plugin.config.json`; keep the safety gates.
4. Update the skill tables in `README.md` / `README.ja.md` and `CHANGELOG.md`.

## Release flow / リリースフロー

Releases go `develop` → `main`. Use the `release-draft` skill to bump the version,
open the `release: VerX.Y.Z` PR, and draft release notes; after merge, tag/publish
(and, for a consuming app, run `deploy`).

## Reporting issues / 起票

Use the [issue templates](./.github/ISSUE_TEMPLATE) (bug / feature / task).
Questions and open-ended discussion go to Discussions.
