@echo off
rem open_lilith_live_monitor.bat - persistent live wallboard for the xenomorph hive.
rem Double-click this (or run from a shortcut). The window NEVER closes on its own:
rem   - the monitor loops forever, refreshing every 15s
rem   - if the monitor ever exits, `pause` holds the window open so you can read errors
rem Press Ctrl+C inside the window to stop (window still stays for reading).

title LILITH LIVE MONITOR
color 0D
rem Fixed size so the full wallboard fits ONE screen for snapshots
mode con: cols=110 lines=30
cd /d "%~dp0.."

rem Prefer the free-threaded interpreter (project mandate; the scientific stack
rem publishes cp314t-only wheels). Fall back to GIL, then to `python`.
set PY=C:\Users\clint\AppData\Local\Programs\Python\Python314\python3.14t.exe
if not exist "%PY%" set PY=C:\Users\clint\AppData\Local\Programs\Python\Python314\python.exe
if not exist "%PY%" set PY=python

:loop
echo [%date% %time%] starting Lilith live monitor...
"%PY%" scripts\lilith_live_monitor.py --refresh 15
echo.
echo ============================================================
echo  Monitor stopped or errored at %date% %time%.
echo  Relaunching in 10s (Ctrl+C to fully close)
echo ============================================================
timeout /t 10 /nobreak >nul
goto loop
