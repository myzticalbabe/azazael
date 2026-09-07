@echo off
rem open_live_monitor.bat — persistent live dashboard window for the Azazael learning loop.
rem Double-click this (or run from a shortcut). The window NEVER closes on its own:
rem   - the dashboard loops forever, refreshing every 30s
rem   - if the dashboard ever exits, `pause` holds the window open so you can read errors
rem Press Ctrl+C inside the window to stop the dashboard (window still stays for reading).

title AZAZAEL LIVE MONITOR
color 0A
cd /d "%~dp0.."

set PY=C:\Users\clint\AppData\Local\Programs\Python\Python314\python.exe
if not exist "%PY%" set PY=python

:loop
echo [%date% %time%] starting live monitor...
"%PY%" scripts\live_monitor.py --refresh 30
echo.
echo ============================================================
echo  Monitor stopped or errored at %date% %time%.
echo  Showing this window instead of closing so you can read it.
echo  (Ctrl+C to fully close)
echo ============================================================
pause
goto loop