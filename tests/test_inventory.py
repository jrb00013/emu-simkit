from emu_simkit.packs.install import install_pack
from emu_simkit.packs.inventory import list_installed, uninstall_pack


def test_install_list_uninstall(tmp_path):
    root = tmp_path / "emu"
    (root / "patches").mkdir(parents=True)
    (root / "config" / "custom_configs").mkdir(parents=True)
    (root / "config" / "config.yml").write_text("Core:\n  A: 1\n", encoding="utf-8")
    actions = install_pack("examples/sample-pack", root)
    assert any("recorded" in a for a in actions)
    assert list_installed(root)
    removed = uninstall_pack(root, "sample-pack")
    assert any("unregistered" in a for a in removed)
    assert list_installed(root) == []
