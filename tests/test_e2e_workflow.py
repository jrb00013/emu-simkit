"""Full useful workflow against a fake emulator tree."""

from pathlib import Path

from emu_simkit.packs.check import check_pack_against_root
from emu_simkit.packs.install import format_plan, install_pack, plan_install
from emu_simkit.packs.inventory import list_installed, uninstall_pack


def _fake_root(tmp_path: Path) -> Path:
    root = tmp_path / "emu"
    (root / "patches").mkdir(parents=True)
    (root / "config" / "custom_configs").mkdir(parents=True)
    (root / "config" / "config.yml").write_text(
        "Core:\n  Example Accuracy: false\n  Max Worker Threads: 2\n"
        "Video:\n  Frame limit: 60\n"
        "Miscellaneous:\n  Start games in fullscreen mode: true\n",
        encoding="utf-8",
    )
    (root / "config" / "patch_config.yml").write_text(
        "HASH-existing:\n  keep me:\n    X:\n      Y:\n        '01.00':\n          Enabled: true\n",
        encoding="utf-8",
    )
    return root


def test_check_plan_install_list_uninstall(tmp_path: Path):
    root = _fake_root(tmp_path)
    pack = "examples/sample-pack"
    result = check_pack_against_root(pack, root)
    assert result.ok, result.as_text()

    plan = plan_install(pack, root, dry_run=True)
    text = format_plan(plan)
    assert "copy" in text and "merge" in text

    actions = install_pack(pack, root)
    assert any("copied" in a for a in actions)
    assert any("merged patch_config" in a for a in actions)
    assert (root / "patches" / "example_patch.yml").is_file()
    # existing patch_config entry preserved
    pc = (root / "config" / "patch_config.yml").read_text(encoding="utf-8")
    assert "HASH-existing" in pc
    assert "HASH-example" in pc or "example" in pc.lower()

    custom = root / "config" / "custom_configs" / "config_sample-pack.yml"
    assert custom.is_file()
    assert "Frame limit: 30" in custom.read_text(encoding="utf-8")

    installed = list_installed(root)
    assert any(p.name == "sample-pack" for p in installed)

    uninstall_pack(root, "sample-pack")
    assert list_installed(root) == []
    assert not (root / "patches" / "example_patch.yml").exists()
    # global config and existing unrelated patch entries remain
    assert (root / "config" / "config.yml").exists()
