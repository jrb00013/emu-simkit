# CLI

```bash
emu-simkit [-v|-q] backends
emu-simkit doctor [--backend generic]
emu-simkit discover [--backend generic]

emu-simkit config merge --base base.yml --overrides over.yml [--out out.yml]
emu-simkit config diff left.yml right.yml

emu-simkit patch validate PATH

emu-simkit pack init DEST --name NAME [--title ID] [--backend generic] [--force]
emu-simkit pack export PACK --out file.zip
emu-simkit pack import ARCHIVE --dest DIR
emu-simkit pack lock PACK
emu-simkit pack verify PACK

emu-simkit install PACK [--root DIR] [--backend NAME] [--dry-run] [--no-backup]
emu-simkit uninstall NAME [--root DIR] [--backend NAME] [--dry-run]
emu-simkit list [--root DIR]

emu-simkit diagnose log LOG [--out report.json]
emu-simkit diagnose watch LOG [--pattern REGEX]

emu-simkit snapshot --out DIR [--root DIR] [--backend NAME] [--label LABEL]
emu-simkit restore ARCHIVE [--root DIR] [--backend NAME]
```

Environment:

- `EMU_SIMKIT_ROOT` or `EMU_DIR` — default root for discovery
