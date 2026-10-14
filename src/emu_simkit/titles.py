"""Title-id helpers (opaque strings; backends may specialize later)."""

from __future__ import annotations

import re

from emu_simkit.types import TitleId

_SAFE = re.compile(r"^[A-Za-z0-9._-]+$")


def normalize_title_id(value: str) -> TitleId:
    value = value.strip()
    if not value or not _SAFE.match(value):
        raise ValueError(f"invalid title id: {value!r}")
    return TitleId(value=value.upper())
