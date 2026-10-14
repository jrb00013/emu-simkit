"""Simple before/after hook registry for install and diagnose."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

Hook = Callable[..., Any]

_HOOKS: dict[str, list[Hook]] = {}


def register_hook(event: str, fn: Hook) -> None:
    _HOOKS.setdefault(event, []).append(fn)


def clear_hooks(event: str | None = None) -> None:
    if event is None:
        _HOOKS.clear()
    else:
        _HOOKS.pop(event, None)


def run_hooks(event: str, **kwargs: Any) -> list[Any]:
    return [fn(**kwargs) for fn in _HOOKS.get(event, [])]


def list_hooks() -> dict[str, int]:
    return {k: len(v) for k, v in _HOOKS.items()}
