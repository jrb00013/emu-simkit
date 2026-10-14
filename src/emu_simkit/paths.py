"""Root discovery helpers."""

from __future__ import annotations

from pathlib import Path

from emu_simkit.backends import get_backend
from emu_simkit.errors import PathNotFoundError


def discover_roots(backend: str = "generic") -> list[Path]:
    """Discover candidate emulator roots for a backend."""
    return get_backend(backend).discover_roots()


def require_root(root: Path | str | None = None, backend: str = "generic") -> Path:
    """Resolve an explicit root or the first discovered one."""
    be = get_backend(backend)
    if root is not None:
        path = Path(root).expanduser().resolve()
        if not be.validate_root(path):
            raise PathNotFoundError(f"not a valid {backend} root: {path}")
        return path
    found = be.discover_roots()
    if not found:
        raise PathNotFoundError(
            f"no {backend} root found; set EMU_SIMKIT_ROOT or pass --root"
        )
    return found[0]
