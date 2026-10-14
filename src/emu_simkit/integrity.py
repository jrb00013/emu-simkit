"""File integrity: SHA-256 digests and pack lockfiles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from emu_simkit.errors import PackError


def sha256_file(path: Path | str, *, chunk: int = 1024 * 1024) -> str:
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def digest_tree(root: Path | str, *, patterns: tuple[str, ...] = ("**/*",)) -> dict[str, str]:
    root = Path(root)
    out: dict[str, str] = {}
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            if path.name.endswith(".lock.json") or path.name == "PACK.lock.json":
                continue
            seen.add(path)
            rel = path.relative_to(root).as_posix()
            out[rel] = sha256_file(path)
    return out


def write_lockfile(pack_dir: Path | str, digests: dict[str, str] | None = None) -> Path:
    pack_dir = Path(pack_dir)
    digests = digests or digest_tree(pack_dir)
    path = pack_dir / "PACK.lock.json"
    payload = {"algorithm": "sha256", "files": digests}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def verify_lockfile(pack_dir: Path | str) -> list[str]:
    """Return list of mismatch descriptions; empty means OK."""
    pack_dir = Path(pack_dir)
    lock = pack_dir / "PACK.lock.json"
    if not lock.is_file():
        raise PackError(f"missing lockfile: {lock}")
    data: dict[str, Any] = json.loads(lock.read_text(encoding="utf-8"))
    expected: dict[str, str] = dict(data.get("files", {}))
    actual = digest_tree(pack_dir)
    problems: list[str] = []
    for rel, digest in expected.items():
        if rel not in actual:
            problems.append(f"missing: {rel}")
        elif actual[rel] != digest:
            problems.append(f"changed: {rel}")
    for rel in actual:
        if rel not in expected:
            problems.append(f"extra: {rel}")
    return problems
