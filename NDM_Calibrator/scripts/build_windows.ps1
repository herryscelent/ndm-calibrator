# Build Windows executable for NDM-Calibrator using PyInstaller.
# Usage (PowerShell):
#   .\scripts\build_windows.ps1
$ErrorActionPreference = "Stop"

Write-Host "=== NDM-Calibrator Windows build ==="
Write-Host "Step 1: checking Python..."
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw "Python not found. Install Python 3.11+ and retry." }

Write-Host "Step 2: checking PyInstaller..."
python -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..."
    python -m pip install pyinstaller
}

Write-Host "Step 3: running PyInstaller..."
python -m PyInstaller NDM_Calibrator.spec --noconfirm --clean

if (Test-Path "dist\NDM-Calibrator\NDM-Calibrator.exe") {
    Write-Host "Build OK: dist\NDM-Calibrator\NDM-Calibrator.exe"
} else {
    Write-Host "[WARN] Build finished but exe not found. Check PyInstaller log."
}
