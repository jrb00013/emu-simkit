from emu_simkit.backends import get_backend, list_backends
from emu_simkit.backends.generic import GenericBackend


def test_generic_registered():
    assert "generic" in list_backends()
    be = get_backend("generic")
    assert isinstance(be, GenericBackend)
