# emu-simkit

Generalized **library + CLI** for console emulator / simulator pack work.

Not tied to one game, one title ID, or one emulator. Bring a **backend**
(or use `generic` / `flat` / `portable`) and use the same APIs for:

- discovering emulator install trees
- merging and diffing config overrides
- loading, validating, and enabling patch packs
- scaffolding, installing, listing, and uninstalling packs
- lockfiles, zip export/import, config snapshots
- parsing / watching logs and shaping diagnostics
- hooks and entry-point backend plugins

## Install

```bash
pip install -e ".[dev]"
```

## Quick start

```bash
emu-simkit doctor
emu-simkit backends
emu-simkit pack init ./my-pack --name my-pack --title EXAMPLE00000
emu-simkit patch validate ./my-pack
emu-simkit pack lock ./my-pack && emu-simkit pack verify ./my-pack
emu-simkit install ./my-pack --root "$EMU_DIR" --dry-run
emu-simkit list --root "$EMU_DIR"
emu-simkit config merge --base config.yml --overrides overrides.yml
emu-simkit config diff a.yml b.yml
emu-simkit diagnose log emulator.log
emu-simkit snapshot --root "$EMU_DIR" --out ./snaps
```

## Library

```python
from emu_simkit import install_pack, load_manifest, merge_overrides, register_backend
from emu_simkit.packs import scaffold_pack, export_pack
from emu_simkit.integrity import write_lockfile, verify_lockfile
```

## Backends

| Name | Layout |
|------|--------|
| `generic` | `patches/`, `config/config.yml`, `config/custom_configs/` |
| `flat` | `patches/`, `config.yml` at root |
| `portable` | everything under `data/` |

Register more via `register_backend(...)` or entry point group `emu_simkit.backends`.

## Legacy

Historical single-title material is under [`legacy/bo2-splitscreen/`](legacy/bo2-splitscreen/).

See [`docs/`](docs/) for architecture, pack format, CLI, and backends.
