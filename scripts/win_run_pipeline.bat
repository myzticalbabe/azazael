@echo off
REM win_run_pipeline.bat - run the graphing pipeline with the GIL-enabled
REM Windows Python 3.14 against the live memory DB (native env, no WSL mangling).
REM Usage:  win_run_pipeline.bat  [learning_loop|ecosystem|temporal|all]
setlocal
set AZAZAEL_MEMORY_DIR=C:\Users\clint\.azazael
set PYW=C:\Users\clint\AppData\Local\Programs\Python\Python314\python.exe
cd /d C:\Users\clint\azazael

if "%1"=="learning_loop" goto learning_loop
if "%1"=="ecosystem" goto ecosystem
if "%1"=="temporal" goto temporal
if "%1"=="all" goto all
echo usage: win_run_pipeline.bat [learning_loop^|ecosystem^|temporal^|all]
exit /b 1

:learning_loop
"%PYW%" scripts\learning_loop_graph.py --out graphs\learning_loop_win
exit /b %errorlevel%

:ecosystem
"%PYW%" scripts\ecosystem_graph.py --out graphs\ecosystem_win
exit /b %errorlevel%

:temporal
"%PYW%" scripts\learning_loop_temporal.py --hours 24 --out graphs\learning_loop_temporal_win
exit /b %errorlevel%

:all
call :learning_loop
call :ecosystem
call :temporal
exit /b %errorlevel%