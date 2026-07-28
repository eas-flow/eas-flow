"""Unit tests for scripts/load-config.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import ROOT, load_module_from_path


@pytest.fixture()
def load_config_mod():
    return load_module_from_path("load_config", ROOT / "scripts" / "load-config.py")


def _write_config(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "plugin.config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_defaults_are_filled_in(load_config_mod, tmp_path):
    path = _write_config(
        tmp_path,
        {
            "repo": "owner/repo",
            "appDir": "src/App",
            "appConfigPath": "src/App/app.json",
        },
    )

    cfg = load_config_mod.load_config(path)

    assert cfg["integrationBranch"] == "develop"
    assert cfg["productionBranch"] == "main"
    assert cfg["platform"] == "ios"
    assert cfg["easProfile"] == "production"
    assert cfg["commands"]["lint"] == "npm run lint"
    assert cfg["commands"]["typecheck"] == "npx tsc --noEmit"
    assert cfg["labelPrefixMap"]["bug"] == "fix"


def test_explicit_values_override_defaults(load_config_mod, tmp_path):
    path = _write_config(
        tmp_path,
        {
            "repo": "owner/repo",
            "appDir": "src/App",
            "appConfigPath": "src/App/app.json",
            "platform": "android",
            "commands": {"lint": "yarn lint"},
        },
    )

    cfg = load_config_mod.load_config(path)

    assert cfg["platform"] == "android"
    # Partial `commands` overrides merge with (not replace) the defaults.
    assert cfg["commands"]["lint"] == "yarn lint"
    assert cfg["commands"]["typecheck"] == "npx tsc --noEmit"


def test_missing_required_field_exits_3(load_config_mod, tmp_path):
    path = _write_config(
        tmp_path,
        {
            "repo": "owner/repo",
            "appDir": "src/App",
            # appConfigPath omitted
        },
    )

    with pytest.raises(SystemExit) as exc:
        load_config_mod.load_config(path)

    assert exc.value.code == 3


def test_invalid_platform_exits_3(load_config_mod, tmp_path):
    path = _write_config(
        tmp_path,
        {
            "repo": "owner/repo",
            "appDir": "src/App",
            "appConfigPath": "src/App/app.json",
            "platform": "windows",
        },
    )

    with pytest.raises(SystemExit) as exc:
        load_config_mod.load_config(path)

    assert exc.value.code == 3


def test_invalid_json_exits_2(load_config_mod, tmp_path):
    path = tmp_path / "plugin.config.json"
    path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        load_config_mod.load_config(path)

    assert exc.value.code == 2


def test_missing_file_exits_1(load_config_mod, tmp_path):
    path = tmp_path / "does-not-exist.json"

    with pytest.raises(SystemExit) as exc:
        load_config_mod.load_config(path)

    assert exc.value.code == 1


def test_repo_autodetect_via_gh_mocked(load_config_mod, tmp_path, monkeypatch):
    path = _write_config(
        tmp_path,
        {
            "appDir": "src/App",
            "appConfigPath": "src/App/app.json",
            # `repo` omitted -> should be auto-detected via `gh repo view`
        },
    )

    class FakeCompletedProcess:
        stdout = "octocat/hello-world\n"

    def fake_run(cmd, **kwargs):
        assert cmd[:3] == ["gh", "repo", "view"]
        return FakeCompletedProcess()

    monkeypatch.setattr(load_config_mod.subprocess, "run", fake_run)

    cfg = load_config_mod.load_config(path)

    assert cfg["repo"] == "octocat/hello-world"


def test_repo_autodetect_unavailable_exits_3(load_config_mod, tmp_path, monkeypatch):
    path = _write_config(
        tmp_path,
        {
            "appDir": "src/App",
            "appConfigPath": "src/App/app.json",
        },
    )

    def fake_run(cmd, **kwargs):
        raise FileNotFoundError("gh: command not found")

    monkeypatch.setattr(load_config_mod.subprocess, "run", fake_run)

    with pytest.raises(SystemExit) as exc:
        load_config_mod.load_config(path)

    assert exc.value.code == 3
