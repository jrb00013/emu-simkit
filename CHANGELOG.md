# Changelog

## 0.2.1

- In-place config apply that preserves comments/ordering
- Deep-merge `patch_config` (no more blind overwrite)
- `apply_mode`: custom | inplace | both | none
- `check` / `plan` preflight; install refuses bad roots unless `--force`
- OS path probing for emulator-like trees; doctor root health
- Real e2e sample-pack workflow + tests

## 0.2.0

- Pack scaffold (`pack init`), zip export/import, whole-pack validate
- Install inventory, `list`, and `uninstall`
- SHA-256 `PACK.lock.json` lock/verify
- Config structural diff
- Flat + portable backends; entry-point plugin loader
- Environment `doctor`, hooks, logging helpers
- Config/patches snapshot + restore
- Log follow/watch diagnostics
- Expanded CLI and tests

## 0.1.0

- Initial **emu-simkit** library and CLI
- Pluggable backends (generic filesystem layout)
- Config merge, patch validate/enable, pack install, log diagnostics
- Example `sample-pack` and docs
- Legacy single-title pack archived under `legacy/`
