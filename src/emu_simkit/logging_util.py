"""Lightweight logging setup for library and CLI."""

from __future__ import annotations

import logging
import sys


def get_logger(name: str = "emu_simkit") -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(verbose: bool = False, quiet: bool = False) -> None:
    level = logging.WARNING if quiet else (logging.DEBUG if verbose else logging.INFO)
    root = logging.getLogger("emu_simkit")
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        root.addHandler(handler)
    root.setLevel(level)
