"""Export/import packs as zip archives."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from emu_simkit.errors import PackError
from emu_simkit.packs.manifest import load_manifest


def export_pack(pack_dir: Path | str, dest: Path | str) -> Path:
    pack_dir = Path(pack_dir)
    dest = Path(dest)
    load_manifest(pack_dir)  # validate present
    if dest.suffix.lower() != ".zip":
        dest = dest.with_suffix(".zip")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(pack_dir).as_posix())
    return dest


def import_pack(archive: Path | str, dest_dir: Path | str) -> Path:
    archive = Path(archive)
    dest_dir = Path(dest_dir)
    if not archive.is_file():
        raise PackError(f"archive not found: {archive}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "r") as zf:
        # prevent path traversal
        for info in zf.infolist():
            target = (dest_dir / info.filename).resolve()
            if not str(target).startswith(str(dest_dir.resolve())):
                raise PackError(f"unsafe path in archive: {info.filename}")
        zf.extractall(dest_dir)
    try:
        load_manifest(dest_dir)
    except PackError:
        # maybe nested single folder
        children = [p for p in dest_dir.iterdir() if p.is_dir()]
        if len(children) == 1:
            return children[0]
        raise
    return dest_dir


def export_to_temp(pack_dir: Path | str) -> Path:
    pack_dir = Path(pack_dir)
    name = load_manifest(pack_dir).name
    tmp = Path(tempfile.mkdtemp(prefix="emu-simkit-")) / f"{name}.zip"
    return export_pack(pack_dir, tmp)
