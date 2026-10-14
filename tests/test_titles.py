import pytest

from emu_simkit.titles import normalize_title_id


def test_normalize():
    assert str(normalize_title_id("example00000")) == "EXAMPLE00000"


def test_bad():
    with pytest.raises(ValueError):
        normalize_title_id("bad id!")
