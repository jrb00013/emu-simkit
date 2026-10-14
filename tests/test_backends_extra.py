from emu_simkit.backends import get_backend, list_backends


def test_extra_backends(tmp_path):
    names = list_backends()
    assert "flat" in names and "portable" in names
    flat = get_backend("flat")
    portable = get_backend("portable")
    assert flat.patches_dir(tmp_path) == tmp_path / "patches"
    assert portable.patches_dir(tmp_path) == tmp_path / "data" / "patches"
    assert flat.global_config_path(tmp_path) == tmp_path / "config.yml"
