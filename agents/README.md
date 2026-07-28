# agents/

Read-only subagents used by the skills. Each is a single Markdown file with
YAML frontmatter (`name`, `description`, `tools`) and a system prompt, invoked
by a skill in its own independent context via the Task tool.

| Agent         | Used by                  | What it does                                                                                          |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------------------- |
| `explorer`    | `develop-work` (planned) | Locates target files, existing implementation patterns, and impact scope before implementation starts |
| `doc-auditor` | `doc-sync` (planned)     | Compares `docSync` target docs against SSOT files and lists discrepancies                             |

Both agents are strictly read-only: they never edit files. They return a
structured summary to the calling skill, which decides what to do with it.
