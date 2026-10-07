@echo off
rem run_evolution_cycle_314t.bat — EvolutionCycle on the free-threaded interpreter.
rem
rem The 3.14t (free-threaded) build SHARES Python314\Lib\site-packages with the
rem GIL build. cp314t wheels (numpy/scipy/sklearn) installed there would break
rem the GIL python.exe everything else runs on, so they live in an isolated
rem dir and are exposed ONLY to this process via PYTHONPATH.
rem
rem PYTHONPATH is prepended (not replaced) so the project's own src/ resolution
rem and stdlib still work exactly as before.
set PYTHONPATH=C:\Users\clint\.azazael\py314t_site;%PYTHONPATH%
"C:\Users\clint\AppData\Local\Programs\Python\Python314\python3.14t.exe" "%~dp0evolution_cycle.py"
exit /b %ERRORLEVEL%