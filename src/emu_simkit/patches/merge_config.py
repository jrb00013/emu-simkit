"""Merge patch enable flags into an existing patch_config.yml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from emu_simkit.backup import backup_file
from emu_simkit.config.merge import deep_merge, load_yaml, write_yaml
from emu_simkit.errors import PatchError


def merge_patch_config(
    dest: Path | str,
    source: Path | str | dict[str, Any],
    *,
    backup: bool = True,
) -> dict[str, Any]:
    dest = Path(dest)
    incoming = load_yaml(source) if not isinstance(source, dict) else source
    if not isinstance(incoming, dict):
        raise PatchError("patch_config source must be a mapping")
    existing: dict[str, Any] = {}
    if dest.exists():
        loaded = load_yaml(dest)
        if loaded is None:
            existing = {}
        elif not isinstance(loaded, dict):
            raise PatchError(f"existing patch_config is not a mapping: {dest}")
        else:
            existing = loaded
    merged = deep_merge(existing, incoming)
    assert isinstance(merged, dict)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if backup and dest.exists():
        backup_file(dest)
    write_yaml(dest, merged)
    return merged
