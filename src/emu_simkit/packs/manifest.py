"""Pack manifest (pack.yml) load/save."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from emu_simkit.config.merge import load_yaml, write_yaml
from emu_simkit.errors import PackError
from emu_simkit.types import PackManifest


def load_manifest(path: Path | str) -> PackManifest:
    path = Path(path)
    if path.is_dir():
        path = path / "pack.yml"
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise PackError(f"pack manifest must be a mapping: {path}")
    name = data.get("name")
    if not name:
        raise PackError(f"pack manifest missing name: {path}")
    return PackManifest(
        name=str(name),
        version=str(data.get("version", "0.1.0")),
        description=str(data.get("description", "")),
        backend=str(data.get("backend", "generic")),
        titles=[str(t) for t in data.get("titles", [])],
        patches=[str(p) for p in data.get("patches", [])],
        overrides=[str(o) for o in data.get("overrides", [])],
        patch_config=str(data["patch_config"]) if data.get("patch_config") else None,
        metadata=dict(data.get("metadata", {})),
    )


def save_manifest(path: Path | str, manifest: PackManifest) -> None:
    path = Path(path)
    payload: dict[str, Any] = {
        "name": manifest.name,
        "version": manifest.version,
        "description": manifest.description,
        "backend": manifest.backend,
        "titles": manifest.titles,
        "patches": manifest.patches,
        "overrides": manifest.overrides,
    }
    if manifest.patch_config:
        payload["patch_config"] = manifest.patch_config
    if manifest.metadata:
        payload["metadata"] = manifest.metadata
    write_yaml(path, payload)
