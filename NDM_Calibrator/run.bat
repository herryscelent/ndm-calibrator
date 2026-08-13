@echo off
setlocal

echo ================================================
echo   NDM-Calibrator  V1.0
echo   非线性动态模型参数辨识与校准软件
echo ================================================
echo.

REM 1. Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] 未找到 Python, 请先安装 Python 3.11+
    pause
    exit /b 1
)

REM 2. Check/use virtual environment
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [INFO] 未检测到虚拟环境 .venv
    choice /c yn /m "是否现在创建并安装依赖到 .venv?"
    if errorlevel 2 goto :use_system
    python -m venv .venv
    call ".venv\Scripts\activate.bat"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

:use_system
REM 3. Launch app
echo [INFO] 启动软件...
python -m app.main
if errorlevel 1 (
    echo [ERROR] 启动失败, 请检查依赖: pip install -r requirements.txt
    pause
)
endlocal
