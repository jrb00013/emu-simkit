"""In-place key updates for emulator YAML that must not be fully rewritten.

Many emulator configs are hand-edited or tool-generated. Full dump via PyYAML
drops comments and reorders keys. This module updates matching ``Key: value``
lines (with optional indentation) and appends missing keys under a section.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from emu_simkit.backup import backup_file
from emu_simkit.errors import ConfigError

_KEY_LINE = re.compile(r"^([ \t]*)([^:#\n]+?)\s*:\s*(.*?)\s*$")


def _flatten(overrides: dict[str, Any], prefix: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    items: list[tuple[tuple[str, ...], Any]] = []
    for key, value in overrides.items():
        path = (*prefix, str(key))
        if isinstance(value, dict):
            items.extend(_flatten(value, path))
        else:
            items.append((path, value))
    return items


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def apply_inplace(
    path: Path | str,
    overrides: dict[str, Any] | Path | str,
    *,
    backup: bool = True,
) -> list[str]:
    """Apply nested overrides to a YAML file by editing matching key lines.

    Returns a list of human-readable change descriptions.
    """
    path = Path(path)
    if isinstance(overrides, (str, Path)):
        from emu_simkit.config.merge import load_yaml

        loaded = load_yaml(overrides)
        if not isinstance(loaded, dict):
            raise ConfigError("overrides must be a mapping")
        overrides = loaded

    if not path.is_file():
        raise ConfigError(f"config not found: {path}")

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    flat = _flatten(overrides)
    changes: list[str] = []
    # Track current section stack by indentation
    for key_path, value in flat:
        leaf = key_path[-1]
        new_val = _format_value(value)
        updated = False
        for i, line in enumerate(lines):
            m = _KEY_LINE.match(line.rstrip("\n\r"))
            if not m:
                continue
            indent, key, _old = m.groups()
            if key.strip() != leaf:
                continue
            # Prefer matches whose parent section appears above with less indent
            if len(key_path) > 1:
                parent = key_path[-2]
                parent_indent = None
                for j in range(i - 1, -1, -1):
                    pm = _KEY_LINE.match(lines[j].rstrip("\n\r"))
                    if not pm:
                        continue
                    p_indent, p_key, p_rest = pm.groups()
                    if p_rest.strip() == "" and p_key.strip() == parent:
                        parent_indent = len(p_indent.replace("\t", "  "))
                        break
                    if len(p_indent.replace("\t", "  ")) < len(indent.replace("\t", "  ")):
                        break
                if parent_indent is None:
                    continue
            newline = f"{indent}{leaf}: {new_val}\n"
            if lines[i] != newline and lines[i].rstrip("\r\n") + "\n" != newline:
                lines[i] = newline
                changes.append(f"set {'.'.join(key_path)} = {new_val}")
            else:
                changes.append(f"unchanged {'.'.join(key_path)} = {new_val}")
            updated = True
            break
        if not updated:
            # Append under last matching parent section if possible
            parent = key_path[-2] if len(key_path) > 1 else None
            insert_at = len(lines)
            indent = "  "
            if parent:
                for i, line in enumerate(lines):
                    m = _KEY_LINE.match(line.rstrip("\n\r"))
                    if m and m.group(2).strip() == parent and m.group(3).strip() == "":
                        base_indent = m.group(1)
                        indent = base_indent + "  "
                        insert_at = i + 1
                        # skip existing children to append at end of section? keep simple: right after header
                        break
            lines.insert(insert_at, f"{indent}{leaf}: {new_val}\n")
            changes.append(f"added {'.'.join(key_path)} = {new_val}")

    if backup:
        backup_file(path)
    path.write_text("".join(lines), encoding="utf-8")
    return changes
