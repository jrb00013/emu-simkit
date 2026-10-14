"""emu-simkit — generalized toolkit for console emulator / simulator packs."""

from emu_simkit.backends import get_backend, list_backends, register_backend
from emu_simkit.config.merge import merge_overrides
from emu_simkit.packs.install import install_pack
from emu_simkit.packs.manifest import load_manifest

__version__ = "0.2.0"
__all__ = [
    "__version__",
    "get_backend",
    "install_pack",
    "list_backends",
    "load_manifest",
    "merge_overrides",
    "register_backend",
]
