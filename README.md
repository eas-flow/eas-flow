# eas-flow

> A Claude Code plugin that automates the Expo/EAS release & deploy workflow.

日本語版は [README.ja.md](./README.ja.md) を参照してください。

**Status:** early development (`v0.1.0` in progress). APIs and structure may change.

`eas-flow` packages a set of Claude Code skills for running an Expo + EAS + GitHub
development flow. Instead of hardcoding repository names, directories, and branches,
each skill reads a small per-project `plugin.config.json`, so the same plugin works
across any Expo project.

## Skills

| Skill | Status | What it does |
| --- | --- | --- |
| `deploy` | v0.1.0 | Runs lint/type checks, then `eas build --auto-submit` to build and submit a production build to the store |
| `release-draft` | v0.1.0 | Bumps `app.json` version (and iOS build number), pushes, and drafts a release PR + release notes |
| `develop-work` | planned (v0.2.0) | Cuts a work branch off the integration branch from an issue, runs quality gates, and opens a PR |
| `doc-sync` | planned (v0.2.0) | Detects drift between implementation and docs and proposes updates |

## Requirements

- [Claude Code](https://claude.com/claude-code)
- An Expo project managed with [EAS](https://docs.expo.dev/eas/) (`eas-cli`, logged in)
- [GitHub CLI](https://cli.github.com) (`gh`), authenticated
- Python 3 (used by the config loader)

## Install

```
/plugin marketplace add eas-flow/eas-flow
/plugin install eas-flow@eas-flow
```

## Configuration

Add a `plugin.config.json` to your project root. Start from
[`plugin.config.example.json`](./plugin.config.example.json):

```jsonc
{
  "repo": "owner/repo",            // optional; auto-detected via `gh repo view`
  "appDir": "src/MyApp",          // where npm/eas commands run
  "appConfigPath": "src/MyApp/app.json",
  "integrationBranch": "develop",
  "productionBranch": "main",
  "platform": "ios",             // ios | android | all
  "easProfile": "production",
  "commands": {
    "lint": "npm run lint",
    "typecheck": "npx tsc --noEmit",
    "test": "npm run test"
  }
}
```

Only `appDir` and `appConfigPath` are required; everything else has sensible
defaults (see [`plugin.config.schema.json`](./plugin.config.schema.json)). The
skills resolve the config by running `scripts/load-config.py` at their start.

## Usage

```
# After a release PR is merged to the production branch:
/eas-flow:deploy

# On the integration branch, to draft the next release:
/eas-flow:release-draft 3.0.0
```

Every skill enforces safety gates: it refuses to run on the wrong branch, stops on
uncommitted changes, requires lint/type checks to pass, and asks for your approval
before building, pushing a version bump, or creating a release.

## Contributing

Development follows a `develop`-based flow: branch off `develop` per issue, open a
PR into `develop`, and cut releases from `develop` to `main`. See
[CONTRIBUTING.md](./CONTRIBUTING.md) for setup and conventions, and the issues on
the [tracker](https://github.com/eas-flow/eas-flow/issues).

## License

[MIT](./LICENSE)
