from emu_simkit.integrity import verify_lockfile, write_lockfile


def test_lock_roundtrip(tmp_path):
    (tmp_path / "a.txt").write_text("hi", encoding="utf-8")
    write_lockfile(tmp_path)
    assert verify_lockfile(tmp_path) == []
    (tmp_path / "a.txt").write_text("bye", encoding="utf-8")
    assert verify_lockfile(tmp_path)
