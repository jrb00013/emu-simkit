from pathlib import Path

from emu_simkit.patches.merge_config import merge_patch_config

_OLD = """
HASH-old:
  old patch:
    Game:
      TITLE:
        '01.00':
          Enabled: false
"""

_NEW = """
HASH-new:
  new patch:
    Game:
      TITLE:
        '01.00':
          Enabled: true
"""


def test_merge_preserves_existing(tmp_path: Path):
    dest = tmp_path / "patch_config.yml"
    dest.write_text(_OLD, encoding="utf-8")
    src = tmp_path / "incoming.yml"
    src.write_text(_NEW, encoding="utf-8")
    merged = merge_patch_config(dest, src, backup=False)
    assert "HASH-old" in merged and "HASH-new" in merged
