@echo off
REM ==========================================================================
REM PREFLIGHT.cmd -- the front door named by the canon block (START HERE 0.1).
REM
REM A double-click is one click: this runs tools/preflight_boot.py on the
REM production 3.16t interpreter and stays open so the verdict is readable.
REM Called with arguments (a shortcut, a scheduled task, a lane script) it
REM returns that exit code and does NOT pause.
REM
REM   0 every check PASS   1 a FAIL   2 BLIND (a check could not be performed)
REM
REM Read-only: it starts nothing, kills nothing and stages nothing. Its artifact
REM is C:\Users\clint\state\preflight_boot.json -- quote that, not a memory.
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "PY=C:\Azazael\.venvs\py316t\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" "%~dp0tools\preflight_boot.py" %*
set "RC=%ERRORLEVEL%"

if "%~1"=="" (
    echo.
    echo preflight exit code: %RC%   ^(0 PASS ^| 1 FAIL ^| 2 BLIND^)
    pause
)
exit /b %RC%
