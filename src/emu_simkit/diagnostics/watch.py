"""Follow a log file and emit matching lines."""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Iterator
from pathlib import Path

from emu_simkit.errors import DiagnosticError


def follow_log(
    path: Path | str,
    *,
    pattern: str | None = None,
    poll: float = 0.25,
    from_start: bool = False,
) -> Iterator[str]:
    path = Path(path)
    if not path.exists():
        raise DiagnosticError(f"log not found: {path}")
    rx = re.compile(pattern, re.I) if pattern else None
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        if not from_start:
            fh.seek(0, 2)
        while True:
            line = fh.readline()
            if not line:
                time.sleep(poll)
                continue
            if rx is None or rx.search(line):
                yield line.rstrip("\n")


def watch_until(
    path: Path | str,
    predicate: Callable[[str], bool],
    *,
    timeout: float = 30.0,
    pattern: str | None = None,
) -> str | None:
    deadline = time.monotonic() + timeout
    for line in follow_log(path, pattern=pattern):
        if predicate(line):
            return line
        if time.monotonic() > deadline:
            return None
