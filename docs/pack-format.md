# Pack format

A pack is a directory with `pack.yml`:

```yaml
name: my-pack
version: 0.1.0
description: optional
backend: generic
apply_mode: custom   # custom | inplace | both | none
titles: [ TITLEID ]
patches: [ foo_patch.yml ]
overrides: [ overrides.yml ]
patch_config: patch_config.yml   # optional; deep-merged on install
metadata: {}
```

## Install behavior

| Artifact | Action |
|----------|--------|
| `patches[]` | Copied into backend `patches/` (backup first) |
| `patch_config` | **Deep-merged** into backend `patch_config.yml` |
| `overrides` + `custom` | Merged with global config → `custom_configs/config_<name>.yml` |
| `overrides` + `inplace` | Key lines updated in global `config.yml` (comments kept) |

Always run `emu-simkit check` / `plan` before `install` on a live tree.
