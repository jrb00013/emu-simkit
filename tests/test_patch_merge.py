from pathlib import Path

from emu_simkit.patches.merge_config import merge_patch_config


def test_merge_preserves_existing(tmp_path: Path):
    dest = tmp_path / "patch_config.yml"
    dest.write_text(
        "HASH-old:\n  old patch:\n    Game:\n      TITLE:\n        '01.00':\n          Enabled: false\n",
        encoding="utf-8",
    )
    src = tmp_path / "incoming.yml"
    src.write_text(
        "HASH-new:\n  new patch:\n    Game:\n      TITLE:\n        '01.00':\n          Enabled: true\n",
        encoding="utf-8",
    )
    merged = merge_patch_config(dest, src, backup=False)
    assert "HASH-old" in merged and "HASH-new" in merged
