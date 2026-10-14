# sample-pack

End-to-end demo for **emu-simkit**.

```bash
# 1. fake emulator tree
mkdir -p /tmp/emu/{patches,config/custom_configs}
cat > /tmp/emu/config/config.yml <<'YAML'
Core:
  Example Accuracy: false
  Max Worker Threads: 2
Video:
  Frame limit: 60
YAML

# 2. preflight + plan
emu-simkit check ./examples/sample-pack --root /tmp/emu
emu-simkit plan ./examples/sample-pack --root /tmp/emu

# 3. install (merges patch_config, copies patches, writes custom config)
emu-simkit install ./examples/sample-pack --root /tmp/emu

# 4. verify
emu-simkit list --root /tmp/emu
ls /tmp/emu/patches /tmp/emu/config/custom_configs

# 5. uninstall
emu-simkit uninstall sample-pack --root /tmp/emu
```

In-place knob edits (preserves surrounding YAML lines):

```bash
emu-simkit config apply --target /tmp/emu/config/config.yml \
  --overrides ./examples/sample-pack/overrides.yml
```
