# Migration from the old single-title repo

This repository used to be a one-off survival pack. It is now **emu-simkit**.

| Old | New |
|-----|-----|
| Root YAML + `install.sh` | Pack directory + `emu-simkit install` |
| Hard-coded title paths | `pack.yml` + pluggable backends |
| Repo = one game | Repo = library; games are packs |

Historical files remain under `legacy/` for reference only.
