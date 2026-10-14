from emu_simkit.envinfo import probe
from emu_simkit.hooks import clear_hooks, list_hooks, register_hook, run_hooks


def test_hooks():
    clear_hooks()
    seen = []
    register_hook("before_install", lambda **kw: seen.append(kw))
    run_hooks("before_install", pack="x", root="y")
    assert seen and list_hooks()["before_install"] == 1
    clear_hooks()


def test_probe():
    info = probe()
    assert "emu_simkit_version" in info
    assert "generic" in info["backends"]
