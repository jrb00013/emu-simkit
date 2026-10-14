"""Named config profiles (title knobs as reusable overlays)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from emu_simkit.config.merge import load_yaml, merge_overrides
from emu_simkit.errors import ConfigError


@dataclass
class ConfigProfile:
    name: str
    overrides: dict[str, Any]
    path: Path | None = None


def load_profile(path: Path | str) -> ConfigProfile:
    path = Path(path)
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ConfigError(f"profile must be a mapping: {path}")
    name = str(data.get("name") or path.stem)
    overrides = data.get("overrides", data)
    if "name" in overrides and overrides is data:
        overrides = {k: v for k, v in data.items() if k != "name"}
    if not isinstance(overrides, dict):
        raise ConfigError(f"overrides must be a mapping in {path}")
    return ConfigProfile(name=name, overrides=overrides, path=path)


def apply_profile(base: Path | str | dict[str, Any], profile: ConfigProfile) -> dict[str, Any]:
    return merge_overrides(base, profile.overrides)
