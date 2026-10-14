"""Environment / host probe for troubleshooting."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any

from emu_simkit import __version__
from emu_simkit.backends import list_backends
from emu_simkit.paths import discover_roots


def probe(backend: str = "generic") -> dict[str, Any]:
    return {
        "emu_simkit_version": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "env": {
            "EMU_SIMKIT_ROOT": os.environ.get("EMU_SIMKIT_ROOT"),
            "EMU_DIR": os.environ.get("EMU_DIR"),
        },
        "backends": list_backends(),
        "discovered_roots": [str(p) for p in discover_roots(backend)],
    }
