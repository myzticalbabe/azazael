@echo off
REM Build azazael-core.exe with Nuitka
REM Requires: Python 3.15t — C:\Azazael\.venvs\py315t (production interpreter)
REM           pyyaml (only runtime dependency)
REM           nuitka installed in that 3.15t venv
REM NOTE: Nuitka is NOT currently installed in py315t, so this --standalone
REM       build is SUSPENDED (see CODEBASE_AUDIT_TODO.md). 3.13 is not a
REM       supported build interpreter here; 3.14t is retired (2026-10-19).

set PYTHON_EXE=C:\Azazael\.venvs\py315t\Scripts\python.exe

echo ========================================
echo   Building azazael-core.exe (Nuitka)
echo   Python: 3.15t (py315t)
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
