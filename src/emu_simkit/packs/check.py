"""Preflight checks before installing a pack into a root."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from emu_simkit.backends import get_backend
from emu_simkit.packs.manifest import load_manifest
from emu_simkit.packs.validate import validate_pack


@dataclass
class CheckResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_text(self) -> str:
        lines: list[str] = []
        status = "OK" if self.ok else "FAIL"
        lines.append(status)
        for e in self.errors:
            lines.append(f"error: {e}")
        for w in self.warnings:
            lines.append(f"warn: {w}")
        return "\n".join(lines)


def check_pack_against_root(
    pack_dir: Path | str,
    root: Path | str,
    *,
    backend: str | None = None,
) -> CheckResult:
    pack_dir = Path(pack_dir)
    root = Path(root)
    result = CheckResult(ok=True)
    try:
        warnings = validate_pack(pack_dir)
        result.warnings.extend(warnings)
    except Exception as exc:  # noqa: BLE001
        result.ok = False
        result.errors.append(str(exc))
        return result

    manifest = load_manifest(pack_dir)
    be_name = backend or manifest.backend
    try:
        be = get_backend(be_name)
    except Exception as exc:  # noqa: BLE001
        result.ok = False
        result.errors.append(str(exc))
        return result

    if not be.validate_root(root):
        result.ok = False
        result.errors.append(f"root is not valid for backend {be_name}: {root}")
        return result

    cfg = be.global_config_path(root)
    if manifest.apply_mode in {"inplace", "both"} and not cfg.exists():
        result.ok = False
        result.errors.append(
            f"apply_mode={manifest.apply_mode} needs global config at {cfg}"
        )
    elif manifest.apply_mode in {"custom", "both"} and not cfg.exists():
        result.warnings.append(
            f"global config missing at {cfg}; custom config will be overrides-only"
        )

    patches = be.patches_dir(root)
    if not patches.exists():
        result.warnings.append(f"patches dir will be created: {patches}")

    # writable?
    try:
        root_stat = root.stat()
        if not os_access_write(root):
            result.errors.append(f"root not writable: {root}")
            result.ok = False
    except OSError as exc:
        result.errors.append(f"cannot stat root: {exc}")
        result.ok = False

    return result


def os_access_write(path: Path) -> bool:
    import os

    return os.access(path, os.W_OK)
