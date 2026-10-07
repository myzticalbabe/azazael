#!/usr/bin/env bash
# Why does `pip list` show torch while `import torch` fails?
PY="${1:-/usr/bin/python3}"
echo "=== interpreter ==="
"$PY" -c 'import sys,sysconfig;print(" exe:",sys.executable);print(" ver:",sys.version.split()[0]);print(" purelib:",sysconfig.get_paths()["purelib"]);print(" platlib:",sysconfig.get_paths()["platlib"])'
echo "=== pip view of torch ==="
"$PY" -m pip show torch 2>&1 | grep -Ei "^(Name|Version|Location|Requires)" | head -6
echo "=== actual import attempt (full traceback) ==="
"$PY" -c "
import traceback
try:
    import torch
    print(' torch imported:', torch.__version__)
except Exception as e:
    print(' type:', type(e).__name__)
    print(' msg :', str(e)[:400])
    traceback.print_exc(limit=3)
" 2>&1 | tail -20
echo "=== is torch on disk? ==="
"$PY" -c "
import importlib.util, sysconfig, os
for key in ('purelib','platlib'):
    base = sysconfig.get_paths()[key]
    p = os.path.join(base, 'torch')
    print(f'  {key}: {p} exists={os.path.isdir(p)}')
" 2>&1 | tail -4
