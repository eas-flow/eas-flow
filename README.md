# eas-flow

> A Claude Code plugin that automates the Expo/EAS release & deploy workflow.

**Status:** early development (pre-`v0.1.0`). APIs and structure may change.

`eas-flow` packages a set of Claude Code skills for running an Expo + EAS + GitHub
development flow — from cutting a work branch off `develop`, through drafting a
release, to building and submitting to the App Store with EAS — driven by a small
per-project config file instead of hardcoded values.

日本語の説明は [README.ja.md](./README.ja.md) を参照してください（整備中）。

## Planned skills (v0.1.0)

| Skill | What it does |
| --- | --- |
| `deploy` | Runs `eas build --auto-submit` for a production build after lint/type checks |
| `release-draft` | Bumps `app.json` version/build number and drafts a release PR + notes |

`develop-work` and `doc-sync` are planned for `v0.2.0`.

## Install (planned)

```
/plugin marketplace add eas-flow/eas-flow
/plugin install eas-flow@eas-flow
```

## Configuration (planned)

Each project provides a `plugin.config.json` describing its repo, app directory,
branches, and commands. See `plugin.config.example.json` (added in a later issue).

## License

[MIT](./LICENSE)
