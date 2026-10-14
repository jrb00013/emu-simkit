"""Environment / host probe for troubleshooting."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any

from emu_simkit import __version__
from emu_simkit.backends import get_backend, list_backends
from emu_simkit.discover import probe_roots
from emu_simkit.paths import discover_roots


def _root_health(root: Path, backend: str) -> dict[str, Any]:
    be = get_backend(backend)
    cfg = be.global_config_path(root)
    patches = be.patches_dir(root)
    return {
        "path": str(root),
        "valid": be.validate_root(root),
        "writable": os.access(root, os.W_OK),
        "has_config": cfg.is_file(),
        "has_patches_dir": patches.is_dir(),
        "config": str(cfg),
        "patches": str(patches),
    }


def probe(backend: str = "generic") -> dict[str, Any]:
    discovered = discover_roots(backend)
    probed = probe_roots()
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
        "discovered_roots": [str(p) for p in discovered],
        "probed_roots": [str(p) for p in probed],
        "root_health": [_root_health(p, backend) for p in discovered[:10]],
    }
