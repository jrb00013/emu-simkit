"""Batch operations over multiple pack directories."""

from __future__ import annotations

from pathlib import Path

from emu_simkit.errors import PackError
from emu_simkit.packs.install import install_pack
from emu_simkit.packs.validate import validate_pack


def find_packs(root: Path | str) -> list[Path]:
    root = Path(root)
    return sorted({p.parent for p in root.rglob("pack.yml")})


def validate_many(root: Path | str) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    for pack in find_packs(root):
        try:
            results[str(pack)] = validate_pack(pack)
        except PackError as exc:
            results[str(pack)] = [f"ERROR: {exc}"]
    return results


def install_many(
    packs: list[Path | str],
    emu_root: Path | str,
    *,
    dry_run: bool = False,
) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for pack in packs:
        out[str(pack)] = install_pack(pack, emu_root, dry_run=dry_run)
    return out
