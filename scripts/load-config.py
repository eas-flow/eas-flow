#!/usr/bin/env python3
"""Resolve eas-flow plugin configuration.

Reads ``plugin.config.json`` from the project root (or a path given as the first
argument), fills in defaults, auto-detects ``repo`` via the GitHub CLI when it is
missing, validates a few basics, and prints the resolved config as JSON to stdout.

The eas-flow skills run this at their start so every downstream step reads a
single, fully-resolved config instead of hardcoded values.

Usage:
    python3 scripts/load-config.py [path/to/plugin.config.json]

Exit codes:
    0  success (resolved config printed to stdout)
    1  config file not found
    2  config file is not valid JSON
    3  required field missing and could not be resolved
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DEFAULTS: dict = {
    "integrationBranch": "develop",
    "productionBranch": "main",
    "platform": "ios",
    "easProfile": "production",
    "commands": {
        "lint": "npm run lint",
        "typecheck": "npx tsc --noEmit",
        "test": "npm run test",
    },
    "labelPrefixMap": {
        "bug": "fix",
        "feature": "feat",
        "improvement": "chore",
        "docs": "docs",
    },
    "docSync": {"docs": [], "ssot": []},
    "storeUrl": "",
}

VALID_PLATFORMS = {"ios", "android", "all"}
REQUIRED = ("appDir", "appConfigPath")


def _die(code: int, message: str) -> None:
    print(f"load-config error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _detect_repo() -> str | None:
    """Return owner/repo from the GitHub CLI, or None if unavailable."""
    try:
        out = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        return out.stdout.strip() or None
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def _merge_defaults(cfg: dict) -> dict:
    resolved = dict(cfg)
    for key, default in DEFAULTS.items():
        if isinstance(default, dict):
            merged = dict(default)
            merged.update(resolved.get(key) or {})
            resolved[key] = merged
        else:
            resolved.setdefault(key, default)
    return resolved


def load_config(path: Path) -> dict:
    if not path.exists():
        _die(1, f"config file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _die(2, f"invalid JSON in {path}: {exc}")

    raw.pop("$schema", None)
    cfg = _merge_defaults(raw)

    if not cfg.get("repo"):
        detected = _detect_repo()
        if detected:
            cfg["repo"] = detected
        else:
            _die(3, "`repo` is missing and could not be detected via `gh repo view`")

    missing = [f for f in REQUIRED if not cfg.get(f)]
    if missing:
        _die(3, f"missing required field(s): {', '.join(missing)}")

    if cfg["platform"] not in VALID_PLATFORMS:
        _die(3, f"platform must be one of {sorted(VALID_PLATFORMS)}")

    return cfg


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("plugin.config.json")
    cfg = load_config(path)
    print(json.dumps(cfg, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
