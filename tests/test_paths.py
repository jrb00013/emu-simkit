import os
from pathlib import Path

from emu_simkit.paths import discover_roots, require_root


def test_discover_from_env(tmp_path, monkeypatch):
    (tmp_path / "patches").mkdir()
    monkeypatch.setenv("EMU_SIMKIT_ROOT", str(tmp_path))
    roots = discover_roots()
    assert tmp_path.resolve() in roots


def test_require_root_explicit(tmp_path):
    (tmp_path / "config").mkdir()
    assert require_root(tmp_path) == tmp_path.resolve()
