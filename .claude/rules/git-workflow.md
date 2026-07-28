# Git workflow / Git 運用規約

## Branches
- `main` — production. Release-only; never commit directly.
- `develop` — integration. All feature work merges here first.
- Work branches: `<prefix>/#<issue>` cut from the latest `develop`
  (e.g. `feat/#23`, `docs/#20`, `chore/#19`, `ci/#7`, `fix/#31`).

## Commits & PRs
- Prefix: `feat:` / `fix:` / `chore:` / `docs:` / `ci:` / `refactor:` / `perf:`.
- End the subject with the issue number: `docs: add CONTRIBUTING #20`.
- PRs target `develop`, follow `.github/pull_request_template.md`, and link the
  issue with `Closes #N`.
- Releases: `develop` → `main` via a `release: VerX.Y.Z` PR (see the
  `release-draft` skill).

## Prohibitions
- No direct push to `main` / `develop`.
- No force-push to shared branches.
- No `--no-verify` commits.
- Do not open a PR until `python3 scripts/validate_plugin.py` passes.
- Do not commit secrets; `.env*` is git-ignored.
