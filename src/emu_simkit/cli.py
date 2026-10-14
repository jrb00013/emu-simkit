"""emu-simkit command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from emu_simkit import __version__
from emu_simkit.backends import list_backends
from emu_simkit.config.merge import merge_overrides, write_yaml
from emu_simkit.diagnostics.report import DiagnosticReport, report_to_json
from emu_simkit.packs.install import apply_plan, plan_install
from emu_simkit.packs.manifest import load_manifest
from emu_simkit.patches.loader import load_patch_file
from emu_simkit.patches.validate import validate_patch_doc
from emu_simkit.paths import discover_roots, require_root


def _cmd_discover(args: argparse.Namespace) -> int:
    roots = discover_roots(args.backend)
    if not roots:
        print(f"no roots for backend={args.backend!r}", file=sys.stderr)
        return 1
    for r in roots:
        print(r)
    return 0


def _cmd_backends(_: argparse.Namespace) -> int:
    for name in list_backends():
        print(name)
    return 0


def _cmd_config_merge(args: argparse.Namespace) -> int:
    merged = merge_overrides(args.base, args.overrides)
    if args.out:
        write_yaml(args.out, merged)
        print(args.out)
    else:
        write_yaml("/dev/stdout", merged) if False else print(
            __import__("yaml").safe_dump(merged, sort_keys=False)
        )
    return 0


def _cmd_patch_validate(args: argparse.Namespace) -> int:
    target = Path(args.path)
    files = list(target.glob("*.yml")) + list(target.glob("*.yaml")) if target.is_dir() else [target]
    # also check pack patches
    if target.is_dir() and (target / "pack.yml").exists():
        manifest = load_manifest(target)
        files = [target / p for p in manifest.patches] or files
    if not files:
        print("no patch YAML found", file=sys.stderr)
        return 1
    rc = 0
    for f in files:
        doc = load_patch_file(f)
        warnings = validate_patch_doc(doc)
        print(f"OK {f}" + (f" ({len(warnings)} warnings)" if warnings else ""))
        for w in warnings:
            print(f"  warn: {w}")
    return rc


def _cmd_install(args: argparse.Namespace) -> int:
    root = require_root(args.root, backend=args.backend) if args.backend else require_root(args.root)
    # allow manifest to pick backend
    manifest = load_manifest(args.pack)
    if args.backend:
        manifest.backend = args.backend
    root = require_root(args.root, backend=manifest.backend)
    plan = plan_install(args.pack, root, dry_run=args.dry_run, backup=not args.no_backup, manifest=manifest)
    for line in apply_plan(plan):
        print(line)
    return 0


def _cmd_diagnose_log(args: argparse.Namespace) -> int:
    report = DiagnosticReport.from_log(args.path)
    text = report_to_json(report, args.out)
    if not args.out:
        print(text)
    else:
        print(args.out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="emu-simkit", description="Emulator/simulator pack toolkit")
    p.add_argument("--version", action="version", version=f"emu-simkit {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("discover", help="discover emulator roots")
    d.add_argument("--backend", default="generic")
    d.set_defaults(func=_cmd_discover)

    b = sub.add_parser("backends", help="list registered backends")
    b.set_defaults(func=_cmd_backends)

    c = sub.add_parser("config", help="config utilities")
    csub = c.add_subparsers(dest="config_cmd", required=True)
    cm = csub.add_parser("merge", help="deep-merge overrides onto base")
    cm.add_argument("--base", required=True)
    cm.add_argument("--overrides", required=True)
    cm.add_argument("--out")
    cm.set_defaults(func=_cmd_config_merge)

    pt = sub.add_parser("patch", help="patch utilities")
    ptsub = pt.add_subparsers(dest="patch_cmd", required=True)
    pv = ptsub.add_parser("validate", help="validate patch YAML or pack")
    pv.add_argument("path")
    pv.set_defaults(func=_cmd_patch_validate)

    inst = sub.add_parser("install", help="install a pack into an emulator root")
    inst.add_argument("pack")
    inst.add_argument("--root")
    inst.add_argument("--backend")
    inst.add_argument("--dry-run", action="store_true")
    inst.add_argument("--no-backup", action="store_true")
    inst.set_defaults(func=_cmd_install)

    diag = sub.add_parser("diagnose", help="diagnostics")
    dsub = diag.add_subparsers(dest="diag_cmd", required=True)
    dl = dsub.add_parser("log", help="parse an emulator log")
    dl.add_argument("path")
    dl.add_argument("--out")
    dl.set_defaults(func=_cmd_diagnose_log)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        code = args.func(args)
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    raise SystemExit(code)


if __name__ == "__main__":
    main()
