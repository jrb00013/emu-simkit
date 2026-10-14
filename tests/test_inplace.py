from pathlib import Path

from emu_simkit.config.inplace import apply_inplace


def test_inplace_preserves_unrelated_lines(tmp_path: Path):
    cfg = tmp_path / "config.yml"
    cfg.write_text(
        "# keep me\n"
        "Core:\n"
        "  Example Accuracy: false\n"
        "  Max Worker Threads: 2\n"
        "Video:\n"
        "  Frame limit: 60\n",
        encoding="utf-8",
    )
    changes = apply_inplace(
        cfg,
        {"Core": {"Example Accuracy": True, "Max Worker Threads": 4}, "Video": {"Frame limit": 30}},
        backup=False,
    )
    text = cfg.read_text(encoding="utf-8")
    assert "# keep me" in text
    assert "Example Accuracy: true" in text
    assert "Max Worker Threads: 4" in text
    assert "Frame limit: 30" in text
    assert any("set" in c for c in changes)
