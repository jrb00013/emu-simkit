"""Heuristic emulator log parsing (backend-agnostic patterns)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from emu_simkit.errors import DiagnosticError

_FATAL = re.compile(r"\b(fatal|access violation|segfault|panic)\b", re.I)
_WARN = re.compile(r"\b(warn(?:ing)?|hang|timeout|livelock|deadlock)\b", re.I)
_THREAD = re.compile(r"\b(PPU|SPU|thread|CIA|PC[=: ])", re.I)


@dataclass
class LogSummary:
    path: Path
    lines: int = 0
    fatals: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    thread_hints: list[str] = field(default_factory=list)


def parse_log(path: Path | str, *, max_hits: int = 50) -> LogSummary:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise DiagnosticError(f"cannot read log {path}: {exc}") from exc
    summary = LogSummary(path=path)
    for line in text.splitlines():
        summary.lines += 1
        if _FATAL.search(line) and len(summary.fatals) < max_hits:
            summary.fatals.append(line.strip())
        elif _WARN.search(line) and len(summary.warnings) < max_hits:
            summary.warnings.append(line.strip())
        if _THREAD.search(line) and len(summary.thread_hints) < max_hits:
            summary.thread_hints.append(line.strip())
    return summary


def summarize_log(path: Path | str) -> dict[str, object]:
    s = parse_log(path)
    return {
        "path": str(s.path),
        "lines": s.lines,
        "fatal_count": len(s.fatals),
        "warning_count": len(s.warnings),
        "thread_hint_count": len(s.thread_hints),
        "fatals": s.fatals[:10],
        "warnings": s.warnings[:10],
    }
