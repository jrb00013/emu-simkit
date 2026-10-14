"""Load patch documents from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from emu_simkit.config.merge import load_yaml
from emu_simkit.errors import PatchError


def load_patch_file(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise PatchError(f"patch file must be a mapping: {path}")
    return data


def iter_patch_entries(doc: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    """Yield (hash_or_key, patch_name, body) for patch entries in a doc."""
    entries: list[tuple[str, str, dict[str, Any]]] = []
    for key, value in doc.items():
        if key in {"Version", "version"}:
            continue
        if not isinstance(value, dict):
            continue
        for patch_name, body in value.items():
            if isinstance(body, dict):
                entries.append((str(key), str(patch_name), body))
    return entries
