"""Backend protocol — any emulator tree that has config/patches layout."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmulatorBackend(Protocol):
    """Filesystem layout + discovery for one emulator family."""

    name: str

    def discover_roots(self) -> list[Path]:
        """Return candidate install roots on this machine."""
        ...

    def patches_dir(self, root: Path) -> Path:
        ...

    def config_dir(self, root: Path) -> Path:
        ...

    def custom_configs_dir(self, root: Path) -> Path:
        ...

    def patch_config_path(self, root: Path) -> Path:
        ...

    def global_config_path(self, root: Path) -> Path:
        ...

    def validate_root(self, root: Path) -> bool:
        """True if root looks like a usable install for this backend."""
        ...
