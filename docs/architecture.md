# Architecture

emu-simkit is layered so no single emulator owns the core:

1. **Backends** (`emu_simkit.backends`) — filesystem layout + discovery
2. **Config** — YAML load / deep-merge / profiles
3. **Patches** — load, validate, enable flags
4. **Packs** — `pack.yml` manifest + install plan/apply
5. **Diagnostics** — log heuristics + JSON reports
6. **CLI** — thin argv surface over the library

Register a custom backend with `register_backend(...)` when an emulator's
tree differs from the generic `patches/` + `config/` layout.
