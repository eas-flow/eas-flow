"""Shared pytest fixtures/helpers for eas-flow's script tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent


def load_module_from_path(name: str, path: Path) -> ModuleType:
    """Import a standalone script (even a hyphenated filename) as a module.

    ``scripts/load-config.py`` is not a valid Python identifier, so it can't be
    imported with a normal ``import`` statement. This loads it directly from
    its file path instead, giving tests access to its functions.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
