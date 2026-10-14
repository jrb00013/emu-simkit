"""Timestamped file backups before mutating an emulator tree."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path


def backup_file(path: Path | str) -> Path | None:
    path = Path(path)
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bak = path.with_suffix(path.suffix + f".bak.{stamp}")
    shutil.copy2(path, bak)
    return bak
