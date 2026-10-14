"""Shared dataclasses for packs, titles, and install plans."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TitleId:
    """Opaque title identifier (format is backend-defined)."""

    value: str

    def __str__(self) -> str:
        return self.value


@dataclass
class PackManifest:
    """Declarative description of a pack on disk."""

    name: str
    version: str = "0.1.0"
    description: str = ""
    backend: str = "generic"
    titles: list[str] = field(default_factory=list)
    patches: list[str] = field(default_factory=list)
    overrides: list[str] = field(default_factory=list)
    patch_config: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.name


@dataclass
class InstallPlan:
    """Files that will be copied or merged into an emulator tree."""

    root: Path
    copies: list[tuple[Path, Path]] = field(default_factory=list)
    merges: list[tuple[Path, Path, Path]] = field(default_factory=list)
    dry_run: bool = False
    backup: bool = True
