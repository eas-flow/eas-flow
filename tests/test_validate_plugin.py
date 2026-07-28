"""Unit tests for scripts/validate_plugin.py."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from conftest import ROOT, load_module_from_path


@pytest.fixture()
def validate_plugin_mod():
    module = load_module_from_path("validate_plugin", ROOT / "scripts" / "validate_plugin.py")
    module.errors.clear()
    return module


def _build_valid_repo(root: Path) -> None:
    """Assemble a minimal, fully-valid plugin repo under ``root``."""
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "sample", "version": "1.0.0", "description": "A sample plugin."}),
        encoding="utf-8",
    )
    (root / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(
            {
                "plugins": [
                    {"name": "sample", "source": "./", "description": "d", "version": "1.0.0"}
                ]
            }
        ),
        encoding="utf-8",
    )

    (root / "skills" / "sample").mkdir(parents=True)
    (root / "skills" / "sample" / "SKILL.md").write_text(
        '---\nname: sample\ndescription: "A sample skill."\n---\n\nBody text.\n',
        encoding="utf-8",
    )

    shutil.copy(ROOT / "plugin.config.schema.json", root / "plugin.config.schema.json")
    (root / "plugin.config.example.json").write_text(
        json.dumps(
            {
                "repo": "owner/repo",
                "appDir": "src/App",
                "appConfigPath": "src/App/app.json",
            }
        ),
        encoding="utf-8",
    )

    (root / "scripts").mkdir(parents=True)
    shutil.copy(ROOT / "scripts" / "load-config.py", root / "scripts" / "load-config.py")


@pytest.fixture()
def valid_repo(tmp_path):
    _build_valid_repo(tmp_path)
    return tmp_path


def test_normal_case_passes(validate_plugin_mod, valid_repo, monkeypatch):
    monkeypatch.setattr(validate_plugin_mod, "ROOT", valid_repo)

    validate_plugin_mod.check_plugin_manifest()
    validate_plugin_mod.check_marketplace()
    validate_plugin_mod.check_skills()
    validate_plugin_mod.check_example_config()
    validate_plugin_mod.check_loader()

    assert validate_plugin_mod.errors == []


def test_broken_frontmatter_is_reported(validate_plugin_mod, valid_repo, monkeypatch):
    monkeypatch.setattr(validate_plugin_mod, "ROOT", valid_repo)
    (valid_repo / "skills" / "sample" / "SKILL.md").write_text(
        "---\nname: [unclosed\ndescription: broken\n---\n\nBody.\n",
        encoding="utf-8",
    )

    validate_plugin_mod.check_skills()

    assert any("frontmatter" in e.lower() for e in validate_plugin_mod.errors)


def test_skill_name_directory_mismatch_is_reported(validate_plugin_mod, valid_repo, monkeypatch):
    monkeypatch.setattr(validate_plugin_mod, "ROOT", valid_repo)
    (valid_repo / "skills" / "sample" / "SKILL.md").write_text(
        '---\nname: not-sample\ndescription: "A sample skill."\n---\n\nBody.\n',
        encoding="utf-8",
    )

    validate_plugin_mod.check_skills()

    assert any("!=" in e or "name" in e.lower() for e in validate_plugin_mod.errors)
    assert any("not-sample" in e for e in validate_plugin_mod.errors)


def test_missing_description_is_reported(validate_plugin_mod, valid_repo, monkeypatch):
    monkeypatch.setattr(validate_plugin_mod, "ROOT", valid_repo)
    (valid_repo / "skills" / "sample" / "SKILL.md").write_text(
        "---\nname: sample\n---\n\nBody.\n",
        encoding="utf-8",
    )

    validate_plugin_mod.check_skills()

    assert any("description" in e.lower() for e in validate_plugin_mod.errors)


def test_schema_violation_is_reported(validate_plugin_mod, valid_repo, monkeypatch):
    monkeypatch.setattr(validate_plugin_mod, "ROOT", valid_repo)
    # `appDir` is required by plugin.config.schema.json; omit it to trigger a
    # schema violation, and add a property the schema doesn't allow.
    (valid_repo / "plugin.config.example.json").write_text(
        json.dumps({"appConfigPath": "src/App/app.json", "unknownField": True}),
        encoding="utf-8",
    )

    validate_plugin_mod.check_example_config()

    assert validate_plugin_mod.errors
    assert any("plugin.config.example.json" in e for e in validate_plugin_mod.errors)


def test_marketplace_missing_plugins_array_is_reported(
    validate_plugin_mod, valid_repo, monkeypatch
):
    monkeypatch.setattr(validate_plugin_mod, "ROOT", valid_repo)
    (valid_repo / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({"plugins": []}), encoding="utf-8"
    )

    validate_plugin_mod.check_marketplace()

    assert any("non-empty array" in e for e in validate_plugin_mod.errors)


def test_plugin_manifest_missing_key_is_reported(validate_plugin_mod, valid_repo, monkeypatch):
    monkeypatch.setattr(validate_plugin_mod, "ROOT", valid_repo)
    (valid_repo / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "sample"}), encoding="utf-8"
    )

    validate_plugin_mod.check_plugin_manifest()

    assert any("version" in e for e in validate_plugin_mod.errors)
    assert any("description" in e for e in validate_plugin_mod.errors)


# NOTE: a plugin.json <-> marketplace.json version-consistency check does not
# exist yet (tracked in #31); once added, a corresponding
# "version mismatch is reported" test belongs here alongside it.
