# emu-simkit

Generalized **library + CLI** for console emulator / simulator pack work.

Not tied to one game, one title ID, or one emulator. Bring a **backend**
(or use the generic filesystem backend) and use the same APIs for:

- discovering emulator install trees
- merging title/profile config overrides
- loading and enabling patch packs
- installing packs (backup + dry-run)
- parsing logs and shaping diagnostics

## Install

```bash
pip install -e ".[dev]"
```

## Quick start

```bash
emu-simkit discover
emu-simkit config merge --base config.yml --overrides overrides.yml --out out.yml
emu-simkit patch validate ./my-pack
emu-simkit install ./my-pack --root "$EMU_DIR" --dry-run
emu-simkit diagnose log emulator.log
```

## Library

```python
from emu_simkit.paths import discover_roots
from emu_simkit.config.merge import merge_overrides
from emu_simkit.patches.loader import load_patch_file
from emu_simkit.backends import get_backend
```

## Legacy

The old Black Ops II survival pack that used to live at the repo root is
frozen under [`legacy/bo2-splitscreen/`](legacy/bo2-splitscreen/). Runtime
behavior for that title belongs elsewhere; this repo is the reusable toolkit.

See [`docs/`](docs/) for architecture, pack format, and CLI.
