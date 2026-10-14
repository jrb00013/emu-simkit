"""Generic filesystem backend — conventional patches/ + config/ layout."""

from __future__ import annotations

import os
from pathlib import Path

from emu_simkit.discover import looks_like_emu_root, probe_roots


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
        for probed in probe_roots():
            if probed not in roots and looks_like_emu_root(probed):
                # prefer trees that match generic layout
                if (probed / "config").exists() or (probed / "patches").exists():
                    roots.append(probed)
        cwd = Path.cwd()
        if ((cwd / "patches").is_dir() or (cwd / "config").is_dir()) and cwd.resolve() not in roots:
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
