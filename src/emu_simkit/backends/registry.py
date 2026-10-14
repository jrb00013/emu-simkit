"""Backend registry — register and resolve by name."""

from __future__ import annotations

from emu_simkit.backends.base import EmulatorBackend
from emu_simkit.backends.flat import FlatBackend
from emu_simkit.backends.generic import GenericBackend
from emu_simkit.backends.portable import PortableBackend
from emu_simkit.errors import BackendError

_REGISTRY: dict[str, EmulatorBackend] = {}


def register_backend(backend: EmulatorBackend, *, replace: bool = False) -> None:
    if backend.name in _REGISTRY and not replace:
        raise BackendError(f"backend already registered: {backend.name}")
    _REGISTRY[backend.name] = backend


def get_backend(name: str = "generic") -> EmulatorBackend:
    if name not in _REGISTRY:
        raise BackendError(f"unknown backend: {name!r}; known={list_backends()}")
    return _REGISTRY[name]


def list_backends() -> list[str]:
    return sorted(_REGISTRY)


# Built-in default
register_backend(GenericBackend())
register_backend(FlatBackend())
register_backend(PortableBackend())
