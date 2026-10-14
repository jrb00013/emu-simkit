from emu_simkit.packs.archive import export_pack, import_pack
from emu_simkit.packs.scaffold import scaffold_pack
from emu_simkit.packs.validate import validate_pack


def test_scaffold_export_import(tmp_path):
    pack = scaffold_pack(tmp_path / "p", name="demo", title="DEMO00001")
    warnings = validate_pack(pack)
    assert isinstance(warnings, list)
    z = export_pack(pack, tmp_path / "demo.zip")
    assert z.exists()
    dest = import_pack(z, tmp_path / "imported")
    assert (dest / "pack.yml").exists() or (tmp_path / "imported" / "pack.yml").exists()
