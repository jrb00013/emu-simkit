from emu_simkit.config.diff import diff_mappings, format_diff


def test_diff():
    left = {"Core": {"A": 1, "B": 2}}
    right = {"Core": {"A": 1, "B": 3}, "Video": {"X": True}}
    entries = diff_mappings(left, right)
    kinds = {e.kind for e in entries}
    assert "changed" in kinds and "added" in kinds
    text = format_diff(entries)
    assert "Core.B" in text
