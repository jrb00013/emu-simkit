"""Validate an entire pack directory."""

from __future__ import annotations

from pathlib import Path

from emu_simkit.errors import PackError, PatchError
from emu_simkit.packs.manifest import load_manifest
from emu_simkit.patches.loader import load_patch_file
from emu_simkit.patches.validate import validate_patch_doc


def validate_pack(pack_dir: Path | str) -> list[str]:
    """Return warnings; raise on hard errors."""
    pack_dir = Path(pack_dir)
    manifest = load_manifest(pack_dir)
    warnings: list[str] = []
    if not manifest.patches:
        warnings.append("manifest has no patches")
    for rel in manifest.patches:
        path = pack_dir / rel
        if not path.is_file():
            raise PackError(f"missing patch file: {rel}")
        try:
            warnings.extend(validate_patch_doc(load_patch_file(path)))
        except PatchError as exc:
            raise PackError(f"{rel}: {exc}") from exc
    for rel in manifest.overrides:
        if not (pack_dir / rel).is_file():
            raise PackError(f"missing override file: {rel}")
    if manifest.patch_config and not (pack_dir / manifest.patch_config).is_file():
        raise PackError(f"missing patch_config: {manifest.patch_config}")
    if not manifest.titles:
        warnings.append("manifest has no titles listed")
    return warnings
