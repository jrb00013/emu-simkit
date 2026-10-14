from emu_simkit.config.merge import deep_merge, merge_overrides


def test_deep_merge_nested():
    base = {"Core": {"A": 1, "B": 2}, "Video": {"X": True}}
    over = {"Core": {"B": 9}, "Misc": {"Z": 0}}
    assert deep_merge(base, over) == {
        "Core": {"A": 1, "B": 9},
        "Video": {"X": True},
        "Misc": {"Z": 0},
    }


def test_merge_overrides_dicts():
    out = merge_overrides({"a": 1}, {"a": 2, "b": 3})
    assert out == {"a": 2, "b": 3}
