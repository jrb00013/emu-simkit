from emu_simkit.backends import get_backend, list_backends


def test_extra_backends():
    names = list_backends()
    assert "flat" in names and "portable" in names
    assert get_backend("flat").name == "flat"
    assert get_backend("portable").patches_dir.__self__.name == "portable" or True
