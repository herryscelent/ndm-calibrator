"""Generate MANIFEST.json and SHA256SUMS.txt for the deliverable.

Excludes .git, .venv, __pycache__, .pytest_cache, temp/log/build caches.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".pytest_tmp", "logs", "deliverable", "dist", "build", ".mypy_cache", ".ipynb_checkpoints"}
EXCLUDE_FILES = {"MANIFEST.json", "SHA256SUMS.txt"}


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect() -> list[Path]:
    files = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        parts = set(rel.parts)
        if parts & EXCLUDE_DIRS:
            continue
        if p.name in EXCLUDE_FILES or p.suffix in (".pyc", ".pyo"):
            continue
        files.append(p)
    return files


def main() -> None:
    files = collect()
    manifest = []
    for p in files:
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        manifest.append({
            "path": rel,
            "size": p.stat().st_size,
            "sha256": _hash(p),
        })
    manifest.sort(key=lambda e: e["path"])

    (ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [f"{e['sha256']}  {e['path']}" for e in manifest]
    (ROOT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"MANIFEST: {len(manifest)} files")


if __name__ == "__main__":
    main()
