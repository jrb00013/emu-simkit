"""List and uninstall packs from an emulator root."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from emu_simkit.backends import get_backend
from emu_simkit.backup import backup_file
from emu_simkit.errors import PackError
from emu_simkit.packs.manifest import load_manifest
from emu_simkit.types import InstallPlan


@dataclass
class InstalledPack:
    name: str
    version: str
    backend: str
    files: list[str]
    custom_config: Path | None
    patch_files: list[str]


def _state_path(root: Path) -> Path:
    return root / "config" / "emu_simkit_installed.json"


def record_install(
    root: Path | str,
    pack_dir: Path | str,
    *,
    plan: InstallPlan | None = None,
) -> Path:
    root = Path(root)
    pack_dir = Path(pack_dir)
    manifest = load_manifest(pack_dir)
    path = _state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = (
        json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"packs": {}}
    )
    files: list[str] = []
    if plan is not None:
        # Only remove pack-owned artifacts. patch_config merges and inplace
        # edits touch shared files — do not delete those on uninstall.
        files.extend(str(dst) for _, dst in plan.copies)
        files.extend(str(out) for _, _, out in plan.merges)
    else:
        files = [Path(p).name for p in manifest.patches]

    data.setdefault("packs", {})[manifest.name] = {
        "version": manifest.version,
        "backend": manifest.backend,
        "patches": [Path(p).name for p in manifest.patches],
        "custom_config": f"config_{manifest.name}.yml",
        "files": files,
        "apply_mode": manifest.apply_mode,
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def list_installed(root: Path | str) -> list[InstalledPack]:
    root = Path(root)
    path = _state_path(root)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[InstalledPack] = []
    for name, meta in data.get("packs", {}).items():
        backend = meta.get("backend", "generic")
        be = get_backend(backend)
        cfg = be.custom_configs_dir(root) / meta.get("custom_config", f"config_{name}.yml")
        out.append(
            InstalledPack(
                name=name,
                version=str(meta.get("version", "")),
                backend=backend,
                files=list(meta.get("files", [])),
                custom_config=cfg if cfg.exists() else None,
                patch_files=list(meta.get("patches", [])),
            )
        )
    return out


def uninstall_pack(
    root: Path | str,
    name: str,
    *,
    backend: str = "generic",
    dry_run: bool = False,
    backup: bool = True,
) -> list[str]:
    root = Path(root)
    path = _state_path(root)
    if not path.exists():
        raise PackError("no install inventory; nothing to uninstall")
    data = json.loads(path.read_text(encoding="utf-8"))
    packs = data.get("packs", {})
    if name not in packs:
        raise PackError(f"pack not recorded as installed: {name}")
    meta = packs[name]
    be = get_backend(meta.get("backend", backend))
    actions: list[str] = []
    targets: list[Path] = []
    for file_path in meta.get("files", []):
        targets.append(Path(file_path))
    if not targets:
        for patch in meta.get("patches", []):
            targets.append(be.patches_dir(root) / patch)
        cfg_name = meta.get("custom_config", f"config_{name}.yml")
        targets.append(be.custom_configs_dir(root) / cfg_name)

    for target in targets:
        # never delete the global config.yml via uninstall
        if target.name == "config.yml" and target.parent.name in {"config", root.name}:
            actions.append(f"skip global config {target}")
            continue
        if not target.exists():
            actions.append(f"skip missing {target}")
            continue
        if dry_run:
            actions.append(f"DRY-RUN remove {target}")
            continue
        if backup:
            backup_file(target)
        target.unlink()
        actions.append(f"removed {target}")

    if not dry_run:
        del packs[name]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        actions.append(f"unregistered {name}")
    return actions
