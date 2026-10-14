"""Deep-merge YAML config overrides onto a base document."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from emu_simkit.errors import ConfigError


def load_yaml(path: Path | str) -> Any:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {path}: {exc}") from exc


def write_yaml(path: Path | str, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def deep_merge(base: Any, override: Any) -> Any:
    """Recursively merge override into base; override wins on scalars."""
    if isinstance(base, dict) and isinstance(override, dict):
        out = dict(base)
        for key, value in override.items():
            if key in out:
                out[key] = deep_merge(out[key], value)
            else:
                out[key] = value
        return out
    return override


def merge_overrides(
    base: Path | str | dict[str, Any],
    overrides: Path | str | dict[str, Any],
) -> dict[str, Any]:
    base_data = load_yaml(base) if not isinstance(base, dict) else base
    over_data = load_yaml(overrides) if not isinstance(overrides, dict) else overrides
    if not isinstance(base_data, dict) or not isinstance(over_data, dict):
        raise ConfigError("base and overrides must be mapping documents")
    merged = deep_merge(base_data, over_data)
    assert isinstance(merged, dict)
    return merged
