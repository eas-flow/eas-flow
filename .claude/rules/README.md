# Rules index / ルール索引

Development conventions for this repository, referenced from
[CLAUDE.md](../../CLAUDE.md). Keep these minimal and accurate.

| Rule                                              | Scope                                                        |
| -------------------------------------------------- | ------------------------------------------------------------ |
| [coding-conventions.md](./coding-conventions.md) | Python / JSON / YAML / Markdown / SKILL.md style             |
| [git-workflow.md](./git-workflow.md)             | Branch/commit conventions, develop-based flow, prohibitions  |

## Single Source of Truth / 信頼できる唯一の情報源

When documenting numbers or settings, transcribe from the source file rather than
guessing:

| Fact                  | SSOT                                                     |
| ---------------------- | ---------------------------------------------------------- |
| Plugin name / version | `.claude-plugin/plugin.json`                              |
| Config schema         | `plugin.config.schema.json`                               |
| CI checks             | `.github/workflows/ci.yml`, `scripts/validate_plugin.py`  |
