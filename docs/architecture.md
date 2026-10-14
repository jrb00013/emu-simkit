# Architecture

emu-simkit is layered so no single emulator owns the core:

1. **Backends** — filesystem layout + discovery (`generic`, `flat`, `portable`, plugins)
2. **Config** — YAML load / deep-merge / profiles / structural diff
3. **Patches** — load, validate, enable flags
4. **Packs** — `pack.yml`, scaffold, validate, install, inventory, zip archive
5. **Integrity** — SHA-256 lockfiles
6. **Snapshots** — tar.gz of config + patches
7. **Diagnostics** — log heuristics, JSON reports, follow/watch
8. **Hooks / plugins** — extension points without forking core
9. **CLI** — thin argv surface over the library

Title-specific content lives in **packs** (or separate repos), never in core.
