# emu-simkit

A **practical** toolkit for installing and managing emulator/simulator **packs**:
patches, config knobs, enable flags, backups, plans, and uninstalls.

Not tied to one game or one emulator. Layout differences go in **backends**.

## Why this exists

Hand-copying patch YAML and sed-editing `config.yml` does not scale. emu-simkit
gives you a repeatable pack format and a CLI that:

1. **Checks** a pack against a real tree before writing
2. **Plans** exactly what will change
3. **Installs** with backups (patches copy, `patch_config` **deep-merges**,
   overrides write a custom config and/or apply **in-place** keys)
4. **Lists / uninstalls** using an on-disk inventory
5. **Diffs / applies** config knobs without nuking comments when using inplace

## Install

```bash
pip install -e ".[dev]"
```

## 5-minute real workflow

```bash
# fake emulator root (or export EMU_SIMKIT_ROOT=/path/to/real)
mkdir -p /tmp/emu/{patches,config/custom_configs}
printf 'Core:\n  Example Accuracy: false\nVideo:\n  Frame limit: 60\n' \
  > /tmp/emu/config/config.yml

emu-simkit check examples/sample-pack --root /tmp/emu
emu-simkit plan  examples/sample-pack --root /tmp/emu
emu-simkit install examples/sample-pack --root /tmp/emu
emu-simkit list --root /tmp/emu
emu-simkit uninstall sample-pack --root /tmp/emu
```

In-place knobs on the live global config (preserves `# comments`):

```bash
emu-simkit config apply \
  --target /tmp/emu/config/config.yml \
  --overrides examples/sample-pack/overrides.yml
```

## Pack format (`pack.yml`)

```yaml
name: my-pack
backend: generic          # or flat / portable / your plugin
apply_mode: custom        # custom | inplace | both | none
patches: [foo_patch.yml]
overrides: [overrides.yml]
patch_config: patch_config.yml
```

| `apply_mode` | Behavior |
|--------------|----------|
| `custom` | Write `config/custom_configs/config_<name>.yml` (merged with global) |
| `inplace` | Edit keys in the global `config.yml` in place |
| `both` | Do both |
| `none` | Skip overrides |

`patch_config` is **merged** into the existing file so other titles stay enabled.

## Library

```python
from emu_simkit import install_pack, load_manifest
from emu_simkit.packs import check_pack_against_root, format_plan, plan_install
from emu_simkit.config import apply_inplace, merge_overrides
```

## Docs

- [Architecture](docs/architecture.md)
- [Pack format](docs/pack-format.md)
- [CLI](docs/cli.md)
- [API](docs/api.md)
- [Backends](docs/backends.md)

Legacy single-title material: [`legacy/bo2-splitscreen/`](legacy/bo2-splitscreen/).
