"""Plan and apply pack installs into an emulator root."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from emu_simkit.backends import get_backend
from emu_simkit.config.merge import merge_overrides, write_yaml
from emu_simkit.errors import PackError
from emu_simkit.packs.manifest import load_manifest
from emu_simkit.types import InstallPlan, PackManifest


def plan_install(
    pack_dir: Path | str,
    root: Path | str,
    *,
    dry_run: bool = False,
    backup: bool = True,
    manifest: PackManifest | None = None,
) -> InstallPlan:
    pack_dir = Path(pack_dir)
    root = Path(root)
    manifest = manifest or load_manifest(pack_dir)
    be = get_backend(manifest.backend)
    if not be.validate_root(root):
        raise PackError(f"invalid root for backend {manifest.backend}: {root}")

    plan = InstallPlan(root=root, dry_run=dry_run, backup=backup)
    patches_dst = be.patches_dir(root)
    for rel in manifest.patches:
        src = pack_dir / rel
        if not src.is_file():
            raise PackError(f"missing patch file: {src}")
        plan.copies.append((src, patches_dst / src.name))

    if manifest.patch_config:
        src = pack_dir / manifest.patch_config
        if not src.is_file():
            raise PackError(f"missing patch_config: {src}")
        plan.copies.append((src, be.patch_config_path(root)))

    for rel in manifest.overrides:
        src = pack_dir / rel
        if not src.is_file():
            raise PackError(f"missing override: {src}")
        # merge into custom config named after pack
        out = be.custom_configs_dir(root) / f"config_{manifest.name}.yml"
        base = be.global_config_path(root)
        plan.merges.append((base, src, out))

    return plan


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bak = path.with_suffix(path.suffix + f".bak.{stamp}")
    shutil.copy2(path, bak)
    return bak


def apply_plan(plan: InstallPlan) -> list[str]:
    """Execute an InstallPlan; returns human-readable action log."""
    actions: list[str] = []
    if plan.dry_run:
        for src, dst in plan.copies:
            actions.append(f"DRY-RUN copy {src} -> {dst}")
        for base, over, out in plan.merges:
            actions.append(f"DRY-RUN merge {base} + {over} -> {out}")
        return actions

    for src, dst in plan.copies:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if plan.backup:
            _backup(dst)
        shutil.copy2(src, dst)
        actions.append(f"copied {src.name} -> {dst}")

    for base, over, out in plan.merges:
        out.parent.mkdir(parents=True, exist_ok=True)
        if plan.backup and out.exists():
            _backup(out)
        if base.exists():
            merged = merge_overrides(base, over)
        else:
            from emu_simkit.config.merge import load_yaml

            merged = load_yaml(over)
        write_yaml(out, merged)
        actions.append(f"merged overrides -> {out}")

    return actions
