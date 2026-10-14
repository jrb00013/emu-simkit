"""Structured diagnostic report + JSON export."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from emu_simkit.diagnostics.log_parse import LogSummary, parse_log


@dataclass
class DiagnosticReport:
    source: str
    summary: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_log(cls, path: Path | str) -> DiagnosticReport:
        parsed: LogSummary = parse_log(path)
        notes: list[str] = []
        if parsed.fatals:
            notes.append("fatal patterns detected — inspect faulting vs watchdog threads")
        if parsed.warnings:
            notes.append("hang/timeout-like warnings present")
        return cls(
            source=str(path),
            summary={
                "lines": parsed.lines,
                "fatal_count": len(parsed.fatals),
                "warning_count": len(parsed.warnings),
                "thread_hint_count": len(parsed.thread_hints),
                "fatals": parsed.fatals[:20],
                "warnings": parsed.warnings[:20],
            },
            notes=notes,
        )


def report_to_json(report: DiagnosticReport, path: Path | str | None = None) -> str:
    payload = asdict(report)
    text = json.dumps(payload, indent=2)
    if path is not None:
        Path(path).write_text(text + "\n", encoding="utf-8")
    return text
