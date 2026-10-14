"""Probe common OS locations for emulator-style trees.

Does not hard-require any one emulator. Looks for directories that already
contain ``patches/`` and/or ``config/`` (or ``config.yml``), including WSL
mounts and typical user config homes.
"""

from __future__ import annotations

import os
from pathlib import Path


def _candidates() -> list[Path]:
    home = Path.home()
    names = (
        "RPCS3",
        "rpcs3",
        "PCSX2",
        "pcsx2",
        "Dolphin",
        "dolphin-emu",
        "Ryujinx",
        "yuzu",
        "suyu",
        "citra",
        "PPSSPP",
        "emu",
        "Emulators",
    )
    out: list[Path] = []
    env = os.environ.get("EMU_SIMKIT_ROOT") or os.environ.get("EMU_DIR")
    if env:
        out.append(Path(env).expanduser())

    bases = [
        home,
        home / ".config",
        home / ".local" / "share",
        home / "Documents",
        home / "Games",
        home / "Emulators",
    ]
    # Windows via WSL
    user = os.environ.get("USER") or os.environ.get("USERNAME") or ""
    if user:
        bases.append(Path(f"/mnt/c/Users/{user}"))
        bases.append(Path(f"/mnt/c/Users/{user}/Documents"))
        bases.append(Path(f"/mnt/c/Users/{user}/RPCS3"))
    bases.append(Path("/mnt/c/Games"))

    for base in bases:
        if not base.is_dir():
            continue
        out.append(base)
        for name in names:
            out.append(base / name)

    # de-dupe while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in out:
        try:
            rp = p.expanduser()
        except Exception:  # noqa: BLE001
            continue
        if rp in seen:
            continue
        seen.add(rp)
        unique.append(rp)
    return unique


def looks_like_emu_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    return (
        (path / "patches").is_dir()
        or (path / "config").is_dir()
        or (path / "config.yml").is_file()
        or (path / "data" / "patches").is_dir()
        or (path / "data" / "config").is_dir()
    )


def probe_roots() -> list[Path]:
    """Return existing dirs that look like emulator trees."""
    found: list[Path] = []
    for cand in _candidates():
        if looks_like_emu_root(cand):
            found.append(cand.resolve())
    return found
