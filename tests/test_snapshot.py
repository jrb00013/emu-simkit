from emu_simkit.snapshot import restore_snapshot, snapshot_root


def test_snapshot_restore(tmp_path):
    root = tmp_path / "emu"
    (root / "config").mkdir(parents=True)
    (root / "patches").mkdir()
    (root / "config" / "config.yml").write_text("A: 1\n", encoding="utf-8")
    (root / "patches" / "x.yml").write_text("Version: 1\n", encoding="utf-8")
    snap = snapshot_root(root, tmp_path / "snaps")
    (root / "config" / "config.yml").write_text("A: 2\n", encoding="utf-8")
    restore_snapshot(snap, root)
    assert "A: 1" in (root / "config" / "config.yml").read_text(encoding="utf-8")
