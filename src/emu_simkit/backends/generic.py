"""Generic filesystem backend — conventional patches/ + config/ layout."""

from __future__ import annotations

import os
from pathlib import Path


class GenericBackend:
    """Default layout used when no emulator-specific backend is registered.

    Expected tree::

        <root>/
          patches/
          config/
            config.yml
            patch_config.yml
            custom_configs/
    """

    name = "generic"

    def discover_roots(self) -> list[Path]:
        roots: list[Path] = []
        env = os.environ.get("EMU_SIMKIT_ROOT") or os.environ.get("EMU_DIR")
        if env:
            p = Path(env).expanduser()
            if p.is_dir():
                roots.append(p.resolve())
        cwd = Path.cwd()
        if (cwd / "patches").is_dir() or (cwd / "config").is_dir():
            roots.append(cwd.resolve())
        return roots

    def patches_dir(self, root: Path) -> Path:
        return root / "patches"

    def config_dir(self, root: Path) -> Path:
        return root / "config"

    def custom_configs_dir(self, root: Path) -> Path:
        return root / "config" / "custom_configs"

    def patch_config_path(self, root: Path) -> Path:
        return root / "config" / "patch_config.yml"

    def global_config_path(self, root: Path) -> Path:
        return root / "config" / "config.yml"

    def validate_root(self, root: Path) -> bool:
        return root.is_dir() and (
            (root / "patches").exists()
            or (root / "config").exists()
            or (root / "config.yml").exists()
        )
