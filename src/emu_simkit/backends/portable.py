"""Portable backend — data/ under root for self-contained trees."""

from __future__ import annotations

import os
from pathlib import Path


class PortableBackend:
    name = "portable"

    def discover_roots(self) -> list[Path]:
        roots: list[Path] = []
        env = os.environ.get("EMU_SIMKIT_ROOT") or os.environ.get("EMU_DIR")
        if env:
            p = Path(env).expanduser()
            if p.is_dir():
                roots.append(p.resolve())
        return roots

    def patches_dir(self, root: Path) -> Path:
        return root / "data" / "patches"

    def config_dir(self, root: Path) -> Path:
        return root / "data" / "config"

    def custom_configs_dir(self, root: Path) -> Path:
        return root / "data" / "config" / "custom_configs"

    def patch_config_path(self, root: Path) -> Path:
        return root / "data" / "config" / "patch_config.yml"

    def global_config_path(self, root: Path) -> Path:
        return root / "data" / "config" / "config.yml"

    def validate_root(self, root: Path) -> bool:
        return root.is_dir() and ((root / "data").exists() or True)
