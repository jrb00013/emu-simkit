import pytest

from emu_simkit.errors import PatchError
from emu_simkit.patches.loader import iter_patch_entries, load_patch_file
from emu_simkit.patches.validate import validate_patch_doc


def test_load_and_validate_example():
    doc = load_patch_file("examples/sample-pack/example_patch.yml")
    warnings = validate_patch_doc(doc)
    assert isinstance(warnings, list)
    entries = iter_patch_entries(doc)
    assert len(entries) == 1


def test_validate_empty_raises():
    with pytest.raises(PatchError):
        validate_patch_doc({"Version": 1})
