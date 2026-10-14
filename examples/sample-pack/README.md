# sample-pack

Minimal pack layout for **emu-simkit**:

```
sample-pack/
  pack.yml
  example_patch.yml
  overrides.yml
  patch_config.yml
```

```bash
emu-simkit patch validate ./examples/sample-pack
emu-simkit install ./examples/sample-pack --root /path/to/emu --dry-run
```
