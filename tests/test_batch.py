from emu_simkit.packs.batch import find_packs, validate_many


def test_find_and_validate_examples():
    packs = find_packs("examples")
    assert packs
    results = validate_many("examples")
    assert results
    assert all(not any(str(w).startswith("ERROR:") for w in ws) for ws in results.values())
