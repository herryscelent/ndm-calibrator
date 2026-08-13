# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for NDM-Calibrator V1.0.

Build:  pyinstaller NDM_Calibrator.spec
Output: dist/NDM-Calibrator/
"""

import os
import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve()

block_cipher = None

a = Analysis(
    [str(ROOT / "app" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "ui" / "styles"), "ui/styles"),
    ],
    hiddenimports=[
        "PySide6",
        "pyqtgraph",
        "scipy",
        "sympy",
        "openpyxl",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtMultimedia",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="NDM-Calibrator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="NDM-Calibrator",
)
