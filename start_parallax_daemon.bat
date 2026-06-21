@echo off
REM ============================================================
REM  Parallax Validator Daemon Launcher (MANDATORY)
REM  The daemon is architecturally mandatory — the pre-action
REM  gate requires it to be running before any file edits.
REM
REM  One-time install (run once, no admin needed):
REM    python azazael\src\DAEMONS\install_parallax_startup.py
REM
REM  After install, the daemon auto-starts on every Windows login.
REM  This script starts it immediately if it's not already running.
REM ============================================================
cd /d C:\Users\clint

echo ============================================================
echo   Parallax Validator Daemon — MANDATORY PRE-ACTION GATE
echo ============================================================
echo.

REM Check if already running
python azazael/src/DAEMONS/parallax_validator.py --status 2>nul | findstr "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Daemon is already RUNNING.
    echo       Pre-action gate is active.
    goto :end
)

echo Daemon is NOT running. Attempting to start...
echo.

REM Try to start directly in a new window
start "Parallax Validator" /MIN python azazael/src/DAEMONS/parallax_validator.py --watch 2>nul
timeout /t 4 /nobreak >nul
python azazael/src/DAEMONS/parallax_validator.py --status 2>nul | findstr "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Daemon started successfully.
    goto :end
)

REM Not running — check if Startup folder launcher exists
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AzazaelParallaxValidator.bat" (
    echo [INFO] Startup launcher is installed. Daemon will auto-start on next login.
    echo        To start now: close this window and run this batch file again
    echo        from your own terminal (not Codebuff).
    goto :end
)

REM Not installed at all — install now
echo.
echo [INFO] Daemon not installed. Running one-time installer (no admin needed)...
python azazael/src/DAEMONS/install_parallax_startup.py
if %ERRORLEVEL% EQU 0 (
    timeout /t 3 /nobreak >nul
    python azazael/src/DAEMONS/parallax_validator.py --status
    goto :end
)

echo.
echo [FAIL] Could not start daemon. The pre-action gate is NOT active.
echo        Please run manually from your own terminal:
echo          python azazael\src\DAEMONS\parallax_validator.py --watch

:end
echo.
echo Pre-flight check: python azazael\src\DAEMONS\check_parallax.py
echo Uninstall:        python azazael\src\DAEMONS\install_parallax_startup.py --uninstall
pause
