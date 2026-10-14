"""Load third-party backends via entry points."""

from __future__ import annotations

from importlib.metadata import entry_points

from emu_simkit.backends import register_backend
from emu_simkit.logging_util import get_logger

log = get_logger(__name__)
_GROUP = "emu_simkit.backends"


def load_backend_plugins(*, replace: bool = False) -> list[str]:
    """Discover and register backends from installed packages."""
    loaded: list[str] = []
    eps = entry_points()
    selected = eps.select(group=_GROUP) if hasattr(eps, "select") else eps.get(_GROUP, [])
    for ep in selected:
        try:
            backend = ep.load()
            instance = backend() if isinstance(backend, type) else backend
            register_backend(instance, replace=replace)
            loaded.append(getattr(instance, "name", ep.name))
        except Exception as exc:  # noqa: BLE001
            log.warning("failed to load backend plugin %s: %s", ep.name, exc)
    return loaded
