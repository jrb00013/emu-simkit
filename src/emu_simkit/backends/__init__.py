"""Pluggable emulator backends."""

from __future__ import annotations

from emu_simkit.backends.base import EmulatorBackend
from emu_simkit.backends.flat import FlatBackend
from emu_simkit.backends.generic import GenericBackend
from emu_simkit.backends.portable import PortableBackend
from emu_simkit.backends.registry import get_backend, list_backends, register_backend

__all__ = [
    "EmulatorBackend",
    "FlatBackend",
    "GenericBackend",
    "PortableBackend",
    "get_backend",
    "list_backends",
    "register_backend",
]
