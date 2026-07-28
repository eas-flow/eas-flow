# CLAUDE.md

Guidance for AI coding agents (Claude Code etc.) working in this repository.
Keep changes small, follow the develop-based flow, and let CI validate structure.

## What this project is

`eas-flow` is a **Claude Code plugin** that packages skills for an Expo/EAS release
& deploy workflow. The skills are driven by a per-project `plugin.config.json`
instead of hardcoded repo names, directories, or branches — so the plugin works in
any Expo project. See [README.md](./README.md) for the user-facing overview.

## Repository layout

```
.claude-plugin/
  plugin.json            # plugin manifest (name/version/description)
  marketplace.json       # marketplace entry (this repo = one plugin)
skills/<name>/SKILL.md   # each skill: YAML frontmatter + instructions
agents/<name>.md         # read-only subagents used by skills (YAML frontmatter + prompt)
rules/                   # optional rule templates a consuming project can adopt
scripts/
  load-config.py         # resolves plugin.config.json (defaults, repo autodetect)
  validate_plugin.py     # CI validation (manifests, SKILL.md frontmatter, schema)
plugin.config.schema.json / plugin.config.example.json
.claude/rules/           # this repo's own dev conventions (see below)
```

## How the skills work

Each skill is a `skills/<name>/SKILL.md` with YAML frontmatter (`name`,
`description`, `hint`, `tools`, `allowed-tools`) and step-by-step instructions.
Every skill starts by running `scripts/load-config.py` to get resolved config,
then references values like `{integrationBranch}` / `{appDir}`. Skills keep strict
safety gates: never act on the wrong branch, stop on uncommitted changes, require
lint/type checks to pass, and ask for user approval before build/version-bump/release.

**Frontmatter gotcha:** `description` and `hint` often contain `:` and `/`
(e.g. `使用例: /eas-flow:deploy`). Always wrap those values in double quotes,
or `scripts/validate_plugin.py` (strict YAML) will fail.

## How the agents work

`agents/<name>.md` are read-only subagents that skills delegate investigative
work to (e.g. `explorer` for codebase exploration, `doc-auditor` for doc/impl
drift detection). They run in an independent context via the Task tool, use only
read-only tools (`Read`, `Grep`, `Glob`, and read-only `Bash` patterns like
`git log`/`git diff`), and return a structured summary — they never edit files
or make decisions on the calling skill's behalf.

## Development workflow

Branches: `main` (production) and `develop` (integration). Feature work branches
off `develop` per issue and merges back via PR into `develop`. Releases go
`develop` → `main`.

- Branch name: `<prefix>/#<issue>` (e.g. `feat/#23`, `docs/#20`, `chore/#19`).
- Commit / PR title prefix: `feat:` / `fix:` / `chore:` / `docs:` / `ci:` /
  `refactor:`, ending with the issue number (`... #23`).
- Never push directly to `main` / `develop`; never force-push shared branches.

See [.claude/rules/git-workflow.md](./.claude/rules/git-workflow.md) and
[.claude/rules/coding-conventions.md](./.claude/rules/coding-conventions.md)
for the details, and [.claude/rules/README.md](./.claude/rules/README.md) for the index.

## Quality gate

Before opening a PR, run:

```bash
pip install pyyaml jsonschema   # once
python3 scripts/validate_plugin.py
```

CI (`.github/workflows/ci.yml`) runs the same check on every PR. A PR should not be
opened until it passes.

## When adding a skill

1. Create `skills/<name>/SKILL.md`; `name` must equal the directory name.
2. Quote `description` / `hint`. Drive behavior from `plugin.config.json`.
3. Keep the safety gates. Update `README.md` / `README.ja.md` skill tables and
   `CHANGELOG.md`.
4. Run the validator, then open a PR into `develop`.

## When adding an agent

1. Create `agents/<name>.md`; `name` must equal the frontmatter's `name`.
2. Keep it read-only: only grant read/inspection tools, never `Edit`/`Write`
   or mutating `Bash` commands.
3. Document which skill(s) delegate to it, both in the agent's `description`
   and in `agents/README.md`.
4. Update `CHANGELOG.md`.
