"""Shared exception types for emu-simkit."""


class SimkitError(Exception):
    """Base error for emu-simkit."""


class PathNotFoundError(SimkitError):
    """Emulator tree or required file was not found."""


class ConfigError(SimkitError):
    """Config load/merge/validate failure."""


class PatchError(SimkitError):
    """Patch pack load/validate/enable failure."""


class PackError(SimkitError):
    """Pack manifest or install failure."""


class DiagnosticError(SimkitError):
    """Log parse or diagnostic shaping failure."""


class BackendError(SimkitError):
    """Pluggable emulator backend failure."""
