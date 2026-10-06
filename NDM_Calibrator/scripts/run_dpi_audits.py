from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts" / "audit_chart_layout.py"
SCALES = (1.0, 1.25, 1.5)


def main() -> int:
    for scale in SCALES:
        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        environment["QT_SCALE_FACTOR"] = str(scale)
        result = subprocess.run(
            [sys.executable, str(AUDIT)],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)
            return result.returncode
        report = ROOT / "docs" / f"QT_LAYOUT_AUDIT_{round(scale * 100)}.json"
        print(f"PASS scale={scale:.2f}: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
