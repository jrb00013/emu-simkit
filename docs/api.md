# Library API (high level)

## Backends
- `register_backend(backend)`, `get_backend(name)`, `list_backends()`
- Built-ins: `GenericBackend`, `FlatBackend`, `PortableBackend`
- Plugins: entry point group `emu_simkit.backends` via `load_backend_plugins()`

## Config
- `load_yaml`, `write_yaml`, `merge_overrides`, `deep_merge`
- `diff_mappings`, `format_diff`
- `load_profile`, `apply_profile`

## Packs
- `load_manifest`, `save_manifest`, `scaffold_pack`, `validate_pack`
- `plan_install`, `apply_plan`, `install_pack`
- `list_installed`, `uninstall_pack`, `record_install`
- `export_pack`, `import_pack`

## Integrity / snapshots
- `sha256_file`, `digest_tree`, `write_lockfile`, `verify_lockfile`
- `snapshot_root`, `restore_snapshot`

## Diagnostics
- `parse_log`, `summarize_log`, `DiagnosticReport`, `report_to_json`
- `follow_log`, `watch_until`

## Other
- `probe()` environment info
- `register_hook` / `run_hooks`
- `normalize_title_id`
- `backup_file`
