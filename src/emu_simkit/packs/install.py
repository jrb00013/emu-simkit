"""Plan and apply pack installs into an emulator root."""

from __future__ import annotations

import shutil
from pathlib import Path

from emu_simkit.backends import get_backend
from emu_simkit.backup import backup_file
from emu_simkit.config.inplace import apply_inplace
from emu_simkit.config.merge import load_yaml, merge_overrides, write_yaml
from emu_simkit.errors import PackError
from emu_simkit.packs.inventory import record_install
from emu_simkit.packs.manifest import load_manifest
from emu_simkit.patches.merge_config import merge_patch_config
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

    plan = InstallPlan(
        root=root,
        dry_run=dry_run,
        backup=backup,
        pack_name=manifest.name,
    )
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
        plan.patch_merges.append((src, be.patch_config_path(root)))

    mode = manifest.apply_mode
    for rel in manifest.overrides:
        src = pack_dir / rel
        if not src.is_file():
            raise PackError(f"missing override: {src}")
        if mode in {"custom", "both"}:
            out = be.custom_configs_dir(root) / f"config_{manifest.name}.yml"
            base = be.global_config_path(root)
            plan.merges.append((base, src, out))
        if mode in {"inplace", "both"}:
            plan.inplaces.append((src, be.global_config_path(root)))

    return plan


def format_plan(plan: InstallPlan) -> str:
    lines = [f"pack={plan.pack_name or '?'} root={plan.root} dry_run={plan.dry_run}"]
    for src, dst in plan.copies:
        lines.append(f"  copy   {src.name} -> {dst}")
    for src, dst in plan.patch_merges:
        lines.append(f"  merge  patch_config {src.name} -> {dst}")
    for base, over, out in plan.merges:
        lines.append(f"  custom {over.name} onto {base.name} -> {out}")
    for over, target in plan.inplaces:
        lines.append(f"  inplace keys from {over.name} -> {target}")
    if len(lines) == 1:
        lines.append("  (nothing to do)")
    return "\n".join(lines)


def apply_plan(plan: InstallPlan) -> list[str]:
    """Execute an InstallPlan; returns human-readable action log."""
    actions: list[str] = []
    if plan.dry_run:
        actions.append(format_plan(plan))
        return actions

    for src, dst in plan.copies:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if plan.backup:
            backup_file(dst)
        shutil.copy2(src, dst)
        actions.append(f"copied {src.name} -> {dst}")

    for src, dst in plan.patch_merges:
        merge_patch_config(dst, src, backup=plan.backup)
        actions.append(f"merged patch_config into {dst}")

    for base, over, out in plan.merges:
        out.parent.mkdir(parents=True, exist_ok=True)
        if plan.backup and out.exists():
            backup_file(out)
        if base.exists():
            merged = merge_overrides(base, over)
        else:
            merged = load_yaml(over)
        write_yaml(out, merged)
        actions.append(f"wrote custom config {out}")

    for over, target in plan.inplaces:
        if not target.exists():
            raise PackError(
                f"cannot apply inplace overrides; global config missing: {target}"
            )
        changes = apply_inplace(target, over, backup=plan.backup)
        actions.extend(changes)

    return actions


def install_pack(
    pack_dir: Path | str,
    root: Path | str,
    *,
    dry_run: bool = False,
    backup: bool = True,
    backend: str | None = None,
) -> list[str]:
    """Plan, apply, and record a pack install."""
    pack_dir = Path(pack_dir)
    root = Path(root)
    manifest = load_manifest(pack_dir)
    if backend:
        manifest.backend = backend
    plan = plan_install(
        pack_dir, root, dry_run=dry_run, backup=backup, manifest=manifest
    )
    actions = apply_plan(plan)
    if not dry_run:
        record_install(root, pack_dir, plan=plan)
        actions.append(f"recorded install for {manifest.name}")
    return actions
