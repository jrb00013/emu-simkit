"""Shared exception types for the toolkit."""


class SimkitError(Exception):
    """Base error for rpcs3-sim-toolkit."""


class PathNotFoundError(SimkitError):
    """RPCS3 tree or required file was not found."""


class ConfigError(SimkitError):
    """Config load/merge/validate failure."""


class PatchError(SimkitError):
    """Patch pack load/validate/enable failure."""


class PackError(SimkitError):
    """Pack manifest or install failure."""


class DiagnosticError(SimkitError):
    """Log parse or diagnostic shaping failure."""
