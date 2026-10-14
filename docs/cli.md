# CLI

```bash
emu-simkit backends
emu-simkit discover [--backend generic]
emu-simkit config merge --base base.yml --overrides over.yml [--out out.yml]
emu-simkit patch validate PATH
emu-simkit install PACK --root DIR [--dry-run] [--no-backup] [--backend NAME]
emu-simkit diagnose log LOG [--out report.json]
```

Environment:

- `EMU_SIMKIT_ROOT` or `EMU_DIR` — default root for the generic backend
