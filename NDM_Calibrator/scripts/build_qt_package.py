"""Build the integrated Qt migration deliverable.

The package is assembled from the checked-in ``deliverable_qt_mock`` tree so
the archive can be verified independently from the repository checkout.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "deliverable_qt_mock"
if not PACKAGE.is_dir() and (ROOT / "source" / "ui_v2").is_dir():
    PACKAGE = ROOT
ARCHIVE = PACKAGE.parent / "NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1.zip"
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".pytest_tmp",
    "_pytest_package_check",
    "logs",
    "dist",
    "build",
}
EXCLUDED_FILES = {"MANIFEST.json", "SHA256SUMS.txt"}


def included_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(PACKAGE)
        if set(relative.parts) & EXCLUDED_DIRS:
            continue
        if path.name in EXCLUDED_FILES or path.name.startswith("debug_"):
            continue
        if path.suffix.lower() in {".pyc", ".pyo"}:
            continue
        files.append(path)
    return files


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_indexes(files: list[Path]) -> None:
    old_manifest_path = PACKAGE / "MANIFEST.json"
    old_manifest = json.loads(old_manifest_path.read_text(encoding="utf-8")) if old_manifest_path.exists() else {}
    manifest = {
        "package": "NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1",
        "revision": "Qt integrated visual fidelity pass",
        "generated_at": "2026-08-27",
        "baseline_qt_zip_sha256": old_manifest.get("baseline_qt_zip_sha256", ""),
        "supersedes_qt_zip_sha256": old_manifest.get("supersedes_qt_zip_sha256", ""),
        "reference_zip_sha256": old_manifest.get("reference_zip_sha256", ""),
        "web_screenshots_synchronized": True,
        "state_screenshots_included": True,
        "real_backend_connected": True,
        "mock_frontend": True,
        "manifest_excludes": sorted([*EXCLUDED_DIRS, "MANIFEST.json", "SHA256SUMS.txt", "debug_*"]),
        "files": [
            {
                "relative_path": str(path.relative_to(PACKAGE)).replace("\\", "/"),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ],
    }
    manifest["files"].sort(key=lambda item: item["relative_path"])
    old_manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sums = "\n".join(f"{entry['sha256']}  {entry['relative_path']}" for entry in manifest["files"])
    (PACKAGE / "SHA256SUMS.txt").write_text(sums + "\n", encoding="utf-8")


def write_archive(files: list[Path]) -> str:
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, f"deliverable_qt_mock/{path.relative_to(PACKAGE).as_posix()}")
        archive.write(PACKAGE / "MANIFEST.json", "deliverable_qt_mock/MANIFEST.json")
        archive.write(PACKAGE / "SHA256SUMS.txt", "deliverable_qt_mock/SHA256SUMS.txt")
    return sha256(ARCHIVE)


def main() -> None:
    files = included_files()
    write_indexes(files)
    files = included_files()
    archive_hash = write_archive(files)
    print(f"files={len(files)} archive={ARCHIVE.name} sha256={archive_hash}")


if __name__ == "__main__":
    main()
