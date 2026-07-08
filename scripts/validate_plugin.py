#!/usr/bin/env python3
"""Validate the eas-flow plugin structure.

Checks, from the repository root:
  1. .claude-plugin/plugin.json      - valid JSON with required keys.
  2. .claude-plugin/marketplace.json - valid JSON with a non-empty plugins list.
  3. skills/<name>/SKILL.md           - YAML frontmatter has name & description,
                                        and name matches the directory.
  4. plugin.config.example.json       - validates against plugin.config.schema.json.
  5. scripts/load-config.py           - resolves the example config without error.

Exit code is 0 when all checks pass, 1 otherwise. Intended to run in CI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml  # PyYAML
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        err(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return None


def check_plugin_manifest() -> None:
    data = load_json(ROOT / ".claude-plugin" / "plugin.json")
    if data is None:
        return
    for key in ("name", "version", "description"):
        if not data.get(key):
            err(f"plugin.json: missing '{key}'")


def check_marketplace() -> None:
    data = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if data is None:
        return
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        err("marketplace.json: 'plugins' must be a non-empty array")
        return
    for i, p in enumerate(plugins):
        for key in ("name", "source"):
            if not p.get(key):
                err(f"marketplace.json: plugins[{i}] missing '{key}'")


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip()
    try:
        return yaml.safe_load(block)
    except yaml.YAMLError as exc:
        err(f"frontmatter YAML error: {exc}")
        return None


def check_skills() -> None:
    skills_dir = ROOT / "skills"
    found = False
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        found = True
        rel = skill_md.relative_to(ROOT)
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm is None:
            err(f"{rel}: missing or invalid YAML frontmatter")
            continue
        name = fm.get("name")
        if not name:
            err(f"{rel}: frontmatter missing 'name'")
        elif name != skill_md.parent.name:
            err(f"{rel}: name '{name}' != directory '{skill_md.parent.name}'")
        if not fm.get("description"):
            err(f"{rel}: frontmatter missing 'description'")
    if not found:
        print("note: no skills found yet (skills/*/SKILL.md)")


def check_example_config() -> None:
    schema = load_json(ROOT / "plugin.config.schema.json")
    example = load_json(ROOT / "plugin.config.example.json")
    if schema is None or example is None:
        return
    validator = Draft7Validator(schema)
    for e in sorted(validator.iter_errors(example), key=lambda x: list(x.path)):
        loc = "/".join(str(p) for p in e.path) or "(root)"
        err(f"plugin.config.example.json: {loc}: {e.message}")


def check_loader() -> None:
    loader = ROOT / "scripts" / "load-config.py"
    example = ROOT / "plugin.config.example.json"
    if not loader.exists():
        err("missing scripts/load-config.py")
        return
    result = subprocess.run(
        [sys.executable, str(loader), str(example)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        err(f"load-config.py failed on example: {result.stderr.strip()}")


def main() -> int:
    check_plugin_manifest()
    check_marketplace()
    check_skills()
    check_example_config()
    check_loader()

    if errors:
        print("Plugin validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Plugin validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
