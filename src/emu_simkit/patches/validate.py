"""Validate patch document shape (backend-agnostic)."""

from __future__ import annotations

from typing import Any

from emu_simkit.errors import PatchError
from emu_simkit.patches.loader import iter_patch_entries


def validate_patch_doc(doc: dict[str, Any]) -> list[str]:
    """Return warnings; raise PatchError on hard failures."""
    warnings: list[str] = []
    entries = iter_patch_entries(doc)
    if not entries:
        raise PatchError("no patch entries found in document")
    for key, name, body in entries:
        patch_list = body.get("Patch") or body.get("patch")
        if patch_list is None:
            warnings.append(f"{key}/{name}: missing Patch list")
            continue
        if not isinstance(patch_list, list) or not patch_list:
            raise PatchError(f"{key}/{name}: Patch must be a non-empty list")
        for i, row in enumerate(patch_list):
            if not isinstance(row, (list, tuple)) or len(row) < 2:
                raise PatchError(f"{key}/{name}: Patch[{i}] must be a list row")
    return warnings
