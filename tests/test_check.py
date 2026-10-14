from pathlib import Path

from emu_simkit.packs.check import check_pack_against_root


def test_check_fails_missing_root(tmp_path: Path):
    result = check_pack_against_root("examples/sample-pack", tmp_path / "nope")
    assert not result.ok
