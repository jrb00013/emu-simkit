"""Snapshot and restore emulator config trees."""

from __future__ import annotations

import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from emu_simkit.backends import get_backend
from emu_simkit.errors import SimkitError


def snapshot_root(
    root: Path | str,
    dest_dir: Path | str,
    *,
    backend: str = "generic",
    label: str | None = None,
) -> Path:
    root = Path(root)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    be = get_backend(backend)
    if not be.validate_root(root):
        raise SimkitError(f"invalid root: {root}")
    stamp = label or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = dest_dir / f"snapshot-{stamp}.tar.gz"
    config = be.config_dir(root)
    patches = be.patches_dir(root)
    with tarfile.open(archive, "w:gz") as tar:
        if config.exists():
            tar.add(config, arcname="config")
        if patches.exists():
            tar.add(patches, arcname="patches")
    return archive


def restore_snapshot(
    archive: Path | str,
    root: Path | str,
    *,
    backend: str = "generic",
) -> list[str]:
    archive = Path(archive)
    root = Path(root)
    be = get_backend(backend)
    actions: list[str] = []
    with tarfile.open(archive, "r:gz") as tar:
        # extract to temp then move
        tmp = root / ".emu_simkit_restore_tmp"
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True)
        tar.extractall(tmp, filter="data")
        mapping = {
            "config": be.config_dir(root),
            "patches": be.patches_dir(root),
        }
        for name, dest in mapping.items():
            src = tmp / name
            if not src.exists():
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            shutil.move(str(src), str(dest))
            actions.append(f"restored {name} -> {dest}")
        shutil.rmtree(tmp, ignore_errors=True)
    return actions
