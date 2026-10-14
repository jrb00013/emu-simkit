"""Structural diff of nested config mappings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DiffEntry:
    path: str
    left: Any
    right: Any
    kind: str  # added | removed | changed


def _walk(left: Any, right: Any, prefix: str = "") -> list[DiffEntry]:
    entries: list[DiffEntry] = []
    if isinstance(left, dict) and isinstance(right, dict):
        keys = sorted(set(left) | set(right), key=str)
        for key in keys:
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in left:
                entries.append(DiffEntry(path=path, left=None, right=right[key], kind="added"))
            elif key not in right:
                entries.append(DiffEntry(path=path, left=left[key], right=None, kind="removed"))
            else:
                entries.extend(_walk(left[key], right[key], path))
        return entries
    if left != right:
        entries.append(DiffEntry(path=prefix or "$", left=left, right=right, kind="changed"))
    return entries


def diff_mappings(left: dict[str, Any], right: dict[str, Any]) -> list[DiffEntry]:
    return _walk(left, right)


def format_diff(entries: list[DiffEntry]) -> str:
    lines: list[str] = []
    for e in entries:
        if e.kind == "added":
            lines.append(f"+ {e.path} = {e.right!r}")
        elif e.kind == "removed":
            lines.append(f"- {e.path} = {e.left!r}")
        else:
            lines.append(f"~ {e.path}: {e.left!r} -> {e.right!r}")
    return "\n".join(lines)
