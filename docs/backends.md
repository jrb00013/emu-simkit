# Backends

A backend describes how an emulator lays out files on disk.

Built-in:

| Name | Layout |
|------|--------|
| `generic` | `patches/`, `config/config.yml`, `config/patch_config.yml`, `config/custom_configs/` |
| `flat` | `patches/`, `config.yml`, `patch_config.yml`, `custom_configs/` at root |
| `portable` | same as generic but under `data/` |

Register your own:

```python
from emu_simkit.backends import register_backend
from emu_simkit.backends.generic import GenericBackend

class MyEmuBackend(GenericBackend):
    name = "myemu"

register_backend(MyEmuBackend())
```

Or ship a package with entry point:

```toml
[project.entry-points."emu_simkit.backends"]
myemu = "mypkg.backend:MyEmuBackend"
```

Set `EMU_SIMKIT_ROOT` (or `EMU_DIR`) for discovery.
