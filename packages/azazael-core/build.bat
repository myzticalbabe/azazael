@echo off
REM Build azazael-core.exe with Nuitka
REM Requires: Python 3.13 (NOT 3.14 — Nuitka 4.1.2 is incompatible with Python 3.14 C API changes)
REM           pyyaml (only runtime dependency)
REM           nuitka installed in the Python 3.13 environment

set PYTHON_EXE=C:\Users\clint\AppData\Local\Programs\Python\Python313\python.exe

echo ========================================
echo   Building azazael-core.exe (Nuitka)
echo   Python: Python 3.13
echo ========================================
echo.

REM Install package in dev mode (skip if already installed)
echo [1/2] Installing azazael-core package...
%PYTHON_EXE% -m pip install -e . --quiet
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Package install failed
    exit /b 1
)

REM Build standalone onefile .exe
echo [2/2] Building .exe with Nuitka ...
%PYTHON_EXE% -m nuitka --standalone --onefile src/azazael_core/cli.py ^
    -o azazael-core.exe ^
    --nofollow-import-to=torch ^
    --nofollow-import-to=optree ^
    --nofollow-import-to=openvino

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   BUILD SUCCESS
    echo   azazael-core.exe created
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   BUILD FAILED - check nuitka-crash-report.xml
    echo ========================================
    exit /b 1
)
