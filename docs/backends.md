# Backends

A backend describes how an emulator lays out files on disk.

Built-in:

- `generic` — `patches/`, `config/config.yml`, `config/patch_config.yml`,
  `config/custom_configs/`

Register your own:

```python
from emu_simkit.backends import register_backend
from emu_simkit.backends.generic import GenericBackend

class MyEmuBackend(GenericBackend):
    name = "myemu"

register_backend(MyEmuBackend())
```

Set `EMU_SIMKIT_ROOT` (or `EMU_DIR`) for discovery with the generic backend.
