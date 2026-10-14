# rpcs3-sim-toolkit

Generalized **library + CLI** for RPCS3-class PS3 simulators.

Use this when you need reusable tooling around:

- discovering RPCS3 install trees (Linux, Windows, WSL, macOS)
- merging title-specific `config.yml` overrides
- loading / enabling patch YAML packs
- installing packs into an emulator tree (with backup + dry-run)
- parsing logs and shaping diagnostic dumps

## Not this repo

Black Ops II split-screen survival is **not** maintained here anymore.
That lives indefinitely in the couchlink-linked RPCS3 fork. The old
BLUS31011 pack is archived under [`legacy/bo2-splitscreen/`](legacy/bo2-splitscreen/).

## Install

```bash
pip install -e ".[dev]"
```

## Quick start

```bash
rpcs3-simkit discover
rpcs3-simkit config merge --base config.yml --overrides my_title.yml --out out.yml
rpcs3-simkit patch validate packs/example/
rpcs3-simkit install ./my-pack --rpcs3 "$RPCS3_DIR" --dry-run
rpcs3-simkit diagnose log RPCS3.log
```

## Library

```python
from rpcs3_simkit.paths import discover_rpcs3
from rpcs3_simkit.config.merge import merge_overrides
from rpcs3_simkit.patches.loader import load_patch_file
```

See [`docs/`](docs/) for architecture, CLI, and pack format.
