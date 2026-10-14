"""emu-simkit command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from emu_simkit import __version__
from emu_simkit.backends import list_backends
from emu_simkit.config.diff import diff_mappings, format_diff
from emu_simkit.config.merge import load_yaml, merge_overrides
from emu_simkit.diagnostics.report import DiagnosticReport, report_to_json
from emu_simkit.diagnostics.watch import follow_log
from emu_simkit.envinfo import probe
from emu_simkit.hooks import run_hooks
from emu_simkit.integrity import verify_lockfile, write_lockfile
from emu_simkit.logging_util import configure_logging
from emu_simkit.packs.archive import export_pack, import_pack
from emu_simkit.packs.batch import validate_many
from emu_simkit.packs.install import install_pack
from emu_simkit.packs.inventory import list_installed, uninstall_pack
from emu_simkit.packs.manifest import load_manifest
from emu_simkit.packs.scaffold import scaffold_pack
from emu_simkit.packs.validate import validate_pack
from emu_simkit.patches.loader import load_patch_file
from emu_simkit.patches.validate import validate_patch_doc
from emu_simkit.paths import discover_roots, require_root
from emu_simkit.plugins import load_backend_plugins
from emu_simkit.snapshot import restore_snapshot, snapshot_root


def _cmd_discover(args: argparse.Namespace) -> int:
    roots = discover_roots(args.backend)
    if not roots:
        print(f"no roots for backend={args.backend!r}", file=sys.stderr)
        return 1
    for r in roots:
        print(r)
    return 0


def _cmd_backends(_: argparse.Namespace) -> int:
    load_backend_plugins()
    for name in list_backends():
        print(name)
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    print(json.dumps(probe(args.backend), indent=2))
    return 0


def _cmd_config_merge(args: argparse.Namespace) -> int:
    merged = merge_overrides(args.base, args.overrides)
    dumped = yaml.safe_dump(merged, sort_keys=False, default_flow_style=False)
    if args.out:
        Path(args.out).write_text(dumped, encoding="utf-8")
        print(args.out)
    else:
        print(dumped, end="")
    return 0


def _cmd_config_diff(args: argparse.Namespace) -> int:
    left = load_yaml(args.left)
    right = load_yaml(args.right)
    if not isinstance(left, dict) or not isinstance(right, dict):
        print("error: both sides must be mappings", file=sys.stderr)
        return 1
    text = format_diff(diff_mappings(left, right))
    print(text if text else "(no differences)")
    return 0


def _cmd_patch_validate(args: argparse.Namespace) -> int:
    target = Path(args.path)
    if target.is_dir() and (target / "pack.yml").exists():
        warnings = validate_pack(target)
        print(f"OK pack {target}" + (f" ({len(warnings)} warnings)" if warnings else ""))
        for w in warnings:
            print(f"  warn: {w}")
        return 0
    if target.is_dir():
        files = list(target.glob("*.yml")) + list(target.glob("*.yaml"))
    else:
        files = [target]
    if not files:
        print("no patch YAML found", file=sys.stderr)
        return 1
    for f in files:
        warnings = validate_patch_doc(load_patch_file(f))
        print(f"OK {f}" + (f" ({len(warnings)} warnings)" if warnings else ""))
        for w in warnings:
            print(f"  warn: {w}")
    return 0


def _cmd_install(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.pack)
    backend = args.backend or manifest.backend
    root = require_root(args.root, backend=backend)
    run_hooks("before_install", pack=args.pack, root=root)
    for line in install_pack(
        args.pack,
        root,
        dry_run=args.dry_run,
        backup=not args.no_backup,
        backend=backend,
    ):
        print(line)
    run_hooks("after_install", pack=args.pack, root=root)
    return 0


def _cmd_uninstall(args: argparse.Namespace) -> int:
    root = require_root(args.root, backend=args.backend)
    for line in uninstall_pack(
        root,
        args.name,
        backend=args.backend,
        dry_run=args.dry_run,
        backup=not args.no_backup,
    ):
        print(line)
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    root = require_root(args.root, backend=args.backend)
    packs = list_installed(root)
    if not packs:
        print("(none)")
        return 0
    for p in packs:
        print(f"{p.name}\tpatches={len(p.patch_files)}\tconfig={p.custom_config}")
    return 0


def _cmd_pack_init(args: argparse.Namespace) -> int:
    dest = scaffold_pack(
        args.dest,
        name=args.name,
        title=args.title,
        backend=args.backend,
        force=args.force,
    )
    print(dest)
    return 0


def _cmd_pack_export(args: argparse.Namespace) -> int:
    print(export_pack(args.pack, args.out))
    return 0


def _cmd_pack_import(args: argparse.Namespace) -> int:
    print(import_pack(args.archive, args.dest))
    return 0


def _cmd_pack_lock(args: argparse.Namespace) -> int:
    print(write_lockfile(args.pack))
    return 0


def _cmd_pack_verify(args: argparse.Namespace) -> int:
    problems = verify_lockfile(args.pack)
    if problems:
        for p in problems:
            print(p)
        return 1
    print("OK")
    return 0


def _cmd_diagnose_log(args: argparse.Namespace) -> int:
    report = DiagnosticReport.from_log(args.path)
    text = report_to_json(report, args.out)
    print(args.out if args.out else text)
    return 0


def _cmd_diagnose_watch(args: argparse.Namespace) -> int:
    try:
        for line in follow_log(args.path, pattern=args.pattern):
            print(line, flush=True)
    except KeyboardInterrupt:
        return 0
    return 0


def _cmd_snapshot(args: argparse.Namespace) -> int:
    root = require_root(args.root, backend=args.backend)
    print(snapshot_root(root, args.out, backend=args.backend, label=args.label))
    return 0


def _cmd_restore(args: argparse.Namespace) -> int:
    root = require_root(args.root, backend=args.backend)
    for line in restore_snapshot(args.archive, root, backend=args.backend):
        print(line)
    return 0



def _cmd_pack_batch_validate(args: argparse.Namespace) -> int:
    results = validate_many(args.root)
    rc = 0
    for path, warnings in results.items():
        errors = [w for w in warnings if str(w).startswith("ERROR:")]
        if errors:
            rc = 1
            print(f"FAIL {path}")
            for e in errors:
                print(f"  {e}")
        else:
            print(f"OK {path}" + (f" ({len(warnings)} warnings)" if warnings else ""))
    return rc

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="emu-simkit", description="Emulator/simulator pack toolkit")
    p.add_argument("--version", action="version", version=f"emu-simkit {__version__}")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("-q", "--quiet", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("discover", help="discover emulator roots")
    d.add_argument("--backend", default="generic")
    d.set_defaults(func=_cmd_discover)

    b = sub.add_parser("backends", help="list registered backends")
    b.set_defaults(func=_cmd_backends)

    doc = sub.add_parser("doctor", help="print environment probe JSON")
    doc.add_argument("--backend", default="generic")
    doc.set_defaults(func=_cmd_doctor)

    c = sub.add_parser("config", help="config utilities")
    csub = c.add_subparsers(dest="config_cmd", required=True)
    cm = csub.add_parser("merge", help="deep-merge overrides onto base")
    cm.add_argument("--base", required=True)
    cm.add_argument("--overrides", required=True)
    cm.add_argument("--out")
    cm.set_defaults(func=_cmd_config_merge)
    cd = csub.add_parser("diff", help="structural diff of two YAML configs")
    cd.add_argument("left")
    cd.add_argument("right")
    cd.set_defaults(func=_cmd_config_diff)

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

    un = sub.add_parser("uninstall", help="uninstall a recorded pack")
    un.add_argument("name")
    un.add_argument("--root")
    un.add_argument("--backend", default="generic")
    un.add_argument("--dry-run", action="store_true")
    un.add_argument("--no-backup", action="store_true")
    un.set_defaults(func=_cmd_uninstall)

    ls = sub.add_parser("list", help="list packs recorded in a root")
    ls.add_argument("--root")
    ls.add_argument("--backend", default="generic")
    ls.set_defaults(func=_cmd_list)

    pk = sub.add_parser("pack", help="pack lifecycle")
    pksub = pk.add_subparsers(dest="pack_cmd", required=True)
    pi = pksub.add_parser("init", help="scaffold a new pack")
    pi.add_argument("dest")
    pi.add_argument("--name", required=True)
    pi.add_argument("--title", default="EXAMPLE00000")
    pi.add_argument("--backend", default="generic")
    pi.add_argument("--force", action="store_true")
    pi.set_defaults(func=_cmd_pack_init)
    pe = pksub.add_parser("export", help="export pack as zip")
    pe.add_argument("pack")
    pe.add_argument("--out", required=True)
    pe.set_defaults(func=_cmd_pack_export)
    pim = pksub.add_parser("import", help="import pack zip")
    pim.add_argument("archive")
    pim.add_argument("--dest", required=True)
    pim.set_defaults(func=_cmd_pack_import)
    pl = pksub.add_parser("lock", help="write PACK.lock.json digests")
    pl.add_argument("pack")
    pl.set_defaults(func=_cmd_pack_lock)
    pvfy = pksub.add_parser("verify", help="verify PACK.lock.json")
    pvfy.add_argument("pack")
    pvfy.set_defaults(func=_cmd_pack_verify)
    pbv = pksub.add_parser("batch-validate", help="validate all packs under a tree")
    pbv.add_argument("root")
    pbv.set_defaults(func=_cmd_pack_batch_validate)

    diag = sub.add_parser("diagnose", help="diagnostics")
    dsub = diag.add_subparsers(dest="diag_cmd", required=True)
    dl = dsub.add_parser("log", help="parse an emulator log")
    dl.add_argument("path")
    dl.add_argument("--out")
    dl.set_defaults(func=_cmd_diagnose_log)
    dw = dsub.add_parser("watch", help="follow a log (Ctrl-C to stop)")
    dw.add_argument("path")
    dw.add_argument("--pattern")
    dw.set_defaults(func=_cmd_diagnose_watch)

    snap = sub.add_parser("snapshot", help="snapshot config+patches tree")
    snap.add_argument("--root")
    snap.add_argument("--backend", default="generic")
    snap.add_argument("--out", required=True)
    snap.add_argument("--label")
    snap.set_defaults(func=_cmd_snapshot)

    rst = sub.add_parser("restore", help="restore a snapshot archive")
    rst.add_argument("archive")
    rst.add_argument("--root")
    rst.add_argument("--backend", default="generic")
    rst.set_defaults(func=_cmd_restore)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(verbose=getattr(args, "verbose", False), quiet=getattr(args, "quiet", False))
    try:
        code = args.func(args)
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    raise SystemExit(code)


if __name__ == "__main__":
    main()
