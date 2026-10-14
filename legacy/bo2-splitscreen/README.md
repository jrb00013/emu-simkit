# Legacy: BO2 (BLUS31011) split-screen survival pack

**Deprecated.** This directory is frozen historical material.

Runtime split-screen survival for Black Ops II is handled by the
couchlink-linked RPCS3 fork. Do not treat these files as the supported
path forward.

The parent repository is now **rpcs3-sim-toolkit**: a generalized library
for RPCS3-class simulators (config merge, patch packs, install, diagnostics).

| File | Role (historical) |
|------|-------------------|
| `BLUS31011_patch.yml` | Hang-detect watchdog NOP patch |
| `patch_config.yml` | Enable the patch |
| `config_BLUS31011.overrides.yml` | SPURS / RSX load-reduction knobs |
| `install.sh` | WSL → Windows RPCS3 tree installer |
| `rpcs3-dump-other-threads-on-fatal-av.diff` | Proposed RPCS3 diagnostic |
| `issue-16426-comment.md` | Notes for RPCS3#16426 |
