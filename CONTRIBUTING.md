# Contributing

1. Use feature branches and small commits
2. Keep the core **emulator-agnostic** — put layout quirks in backends
3. Add tests for library behavior
4. Run `ruff check src tests` and `pytest`

Packs for specific titles belong under `examples/` or separate repos that
depend on emu-simkit — not in the core package.
