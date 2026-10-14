from pathlib import Path

from emu_simkit.packs.install import apply_plan, plan_install
from emu_simkit.packs.manifest import load_manifest


def test_load_sample_manifest():
    m = load_manifest("examples/sample-pack")
    assert m.name == "sample-pack"
    assert m.backend == "generic"


def test_dry_run_install(tmp_path):
    (tmp_path / "patches").mkdir()
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "custom_configs").mkdir()
    (tmp_path / "config" / "config.yml").write_text("Core:\n  A: 1\n", encoding="utf-8")
    plan = plan_install("examples/sample-pack", tmp_path, dry_run=True)
    actions = apply_plan(plan)
    assert any("DRY-RUN" in a for a in actions)
    assert plan.copies
