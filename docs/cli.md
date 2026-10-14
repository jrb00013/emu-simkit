# CLI

```bash
emu-simkit doctor
emu-simkit discover [--backend generic]
emu-simkit backends

emu-simkit check PACK [--root DIR] [--backend NAME]
emu-simkit plan  PACK [--root DIR] [--backend NAME]
emu-simkit install PACK [--root DIR] [--dry-run] [--force] [--no-backup]
emu-simkit uninstall NAME [--root DIR] [--dry-run]
emu-simkit list [--root DIR]

emu-simkit config merge --base base.yml --overrides over.yml [--out out.yml]
emu-simkit config diff left.yml right.yml
emu-simkit config apply --target config.yml --overrides knobs.yml

emu-simkit patch validate PATH
emu-simkit pack init|export|import|lock|verify|batch-validate ...
emu-simkit diagnose log|watch ...
emu-simkit snapshot|restore ...
```

Environment: `EMU_SIMKIT_ROOT` or `EMU_DIR`.
