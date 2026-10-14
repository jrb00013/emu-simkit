"""List and uninstall packs from an emulator root."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from emu_simkit.backends import get_backend
from emu_simkit.backup import backup_file
from emu_simkit.errors import PackError
from emu_simkit.packs.manifest import load_manifest


@dataclass
class InstalledPack:
    name: str
    custom_config: Path | None
    patch_files: list[str]


def _state_path(root: Path) -> Path:
    return root / "config" / "emu_simkit_installed.json"


def record_install(root: Path | str, pack_dir: Path | str) -> Path:
    root = Path(root)
    pack_dir = Path(pack_dir)
    manifest = load_manifest(pack_dir)
    path = _state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"packs": {}}
    data.setdefault("packs", {})[manifest.name] = {
        "version": manifest.version,
        "patches": [Path(p).name for p in manifest.patches],
        "custom_config": f"config_{manifest.name}.yml",
        "backend": manifest.backend,
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
    be = get_backend("generic")
    for name, meta in data.get("packs", {}).items():
        cfg = be.custom_configs_dir(root) / meta.get("custom_config", f"config_{name}.yml")
        out.append(
            InstalledPack(
                name=name,
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
    for patch in meta.get("patches", []):
        targets.append(be.patches_dir(root) / patch)
    cfg_name = meta.get("custom_config", f"config_{name}.yml")
    targets.append(be.custom_configs_dir(root) / cfg_name)

    for target in targets:
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


def installed_as_dicts(root: Path | str) -> list[dict]:
    return [asdict(p) | {"custom_config": str(p.custom_config) if p.custom_config else None}
            for p in list_installed(root)]
