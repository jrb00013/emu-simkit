"""Read/write patch_config enable flags."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from emu_simkit.config.merge import load_yaml, write_yaml
from emu_simkit.errors import PatchError


def load_patch_config(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {}
    data = load_yaml(path)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise PatchError(f"patch_config must be a mapping: {path}")
    return data


def save_patch_config(path: Path | str, data: dict[str, Any]) -> None:
    write_yaml(path, data)


def enable_patch(
    config: dict[str, Any],
    *,
    hash_key: str,
    patch_name: str,
    game: str,
    title_id: str,
    version: str = "01.00",
    enabled: bool = True,
) -> dict[str, Any]:
    """Set Enabled for a nested patch_config path; returns mutated config."""
    node: dict[str, Any] = config.setdefault(hash_key, {})
    by_name: dict[str, Any] = node.setdefault(patch_name, {})
    by_game: dict[str, Any] = by_name.setdefault(game, {})
    by_title: dict[str, Any] = by_game.setdefault(title_id, {})
    by_title[version] = {"Enabled": enabled}
    return config
