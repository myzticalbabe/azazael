@echo off
REM ============================================================
REM  Azazael Worm Execution Matrix — Scheduled Runner
REM  Runs every 4 hours via Windows Task Scheduler.
REM  Appends results to worm_execution_history.jsonl
REM ============================================================
setlocal

REM --- Project root (parent of this script's directory) ---
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM --- Python executable ---
set "PYTHON=%PROJECT_ROOT%\miniforge3\python.exe"

REM --- Log directory ---
set "LOG_DIR=%PROJECT_ROOT%\azazael\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM --- Timestamp for log file (PowerShell — wmic is deprecated) ---
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMddHHmmss"') do set "TS=%%I"
set "LOGFILE=%LOG_DIR%\worm_matrix_%TS%.log"

REM --- Execute matrix with history append ---
echo [%date% %time%] Starting worm execution matrix... > "%LOGFILE%"
"%PYTHON%" "%PROJECT_ROOT%\azazael\_worm_execution_matrix.py" ^
    --timeout 60 ^
    --cluster ^
    --concurrent ^
    --output-html ^
    --append-history ^
    --json-only >> "%LOGFILE%" 2>&1

set "EXIT_CODE=%ERRORLEVEL%"
echo [%date% %time%] Finished with exit code %EXIT_CODE% >> "%LOGFILE%"

REM --- Cleanup: keep only last 30 log files ---
for /f "skip=30" %%F in ('dir /b /o-d "%LOG_DIR%\worm_matrix_*.log" 2^>nul') do (
    del "%LOG_DIR%\%%F" 2>nul
)

exit /b %EXIT_CODE%
