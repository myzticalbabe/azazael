@echo off
rem run_evolution_cycle_hyper.bat — HYPEROPTIMIZED EvolutionCycle (all phases ON).
rem
rem The stock launcher (run_evolution_cycle_314t.bat) runs every PROTEUS phase
rem with its DEFAULT, which is OFF, so the scheduled task has been running the
rem baseline search this whole time. This launcher turns on every phase that is
rem wired, and each one is a measured, separately-verdict'd change:
rem
rem   ORACLE      Phase C  imagined-era robustness pre-gate (torch-free JSON)
rem   CRANIUM     Phase D  cross-era pooled decision at the SPRT site
rem   CIRCULATION Phase D  Thompson allocator replaces the fixed 2x margin gate
rem   MORPH       Phase E  one extra structural gene, round-robin trialled
rem   TENSOR      deliverable  genes as tensors declaring their own usefulness
rem
rem Every flag is set for THIS PROCESS ONLY, so the scheduled task and any
rem manual GIL-side run stay reproducible from the batch file alone.
rem
rem The 3.14t (free-threaded) build SHARES Python314\Lib\site-packages with the
rem GIL build. cp314t wheels (numpy/scipy/sklearn) installed there would break
rem the GIL python.exe everything else runs on, so they live in an isolated
rem dir and are exposed ONLY to this process via PYTHONPATH.
rem
rem PYTHONPATH is prepended (not replaced) so the project's own src/ resolution
rem and stdlib still work exactly as before.
set AZAZAEL_PROTEUS_ORACLE=1
set AZAZAEL_PROTEUS_TRAIN=1
set AZAZAEL_PROTEUS_CRANIUM=1
set AZAZAEL_PROTEUS_CIRCULATION=1
set AZAZAEL_PROTEUS_MORPH=1
set AZAZAEL_TENSOR_GENOME=1

"C:\Azazael\.venvs\py315t\Scripts\python.exe" "%~dp0evolution_cycle.py"
exit /b %ERRORLEVEL%
