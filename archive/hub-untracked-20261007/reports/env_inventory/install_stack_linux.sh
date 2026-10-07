#!/usr/bin/env bash
# Install the self-adaptation stack on a Linux free-threaded interpreter.
#
# Disk is the constraint: Ubuntu's ext4.vhdx lives on C: (36 GB free) and Kali's
# on E: (29 GB free), so a default `pip install ... trl` that drags in
# torch+CUDA (~5 GB of nvidia-* wheels) is not affordable.  Two strategies:
#
#   pin      - keep the torch already installed (Ubuntu has 2.12.0), so the
#              resolver never reaches for a CUDA build.  Smallest change.
#   cputorch - no torch present (Kali): install a CPU-only torch from the
#              PyTorch CPU index first, then the stack around it.
#
# Both paths then install the two leaf dependencies that transformers 5.17
# imports but does not declare (see reports/ADAPTATION_314T_WHEEL_AUDIT.md).
#
# Usage: bash install_stack_linux.sh <python> <pin|cputorch>
set -uo pipefail

PY="${1:-/usr/bin/python3}"
MODE="${2:-pin}"
STACK="gymnasium stable_baselines3 peft trl datasets transformers accelerate"
LEAF="narwhals threadpoolctl"

export PIP_DISABLE_PIP_VERSION_CHECK=1
# Ubuntu/Kali mark the system interpreter externally managed (PEP 668).
COMMON=(--break-system-packages --only-binary=:all:)

echo "=== $PY  (mode=$MODE) ==="
"$PY" -c 'import sys; print("  python", sys.version.split()[0], "free_threaded=", not getattr(sys,"_is_gil_enabled",lambda:True)())'

if [ "$MODE" = "cputorch" ]; then
  if "$PY" -c "import torch" 2>/dev/null; then
    echo "  torch already present: $("$PY" -c 'import torch;print(torch.__version__)')"
  else
    echo "  -- installing CPU-only torch (avoiding ~5 GB of CUDA wheels) --"
    if ! "$PY" -m pip install "${COMMON[@]}" \
           --index-url https://download.pytorch.org/whl/cpu torch 2>&1 | tail -3; then
      echo "  !! CPU index unavailable; falling back to PyPI (may pull CUDA wheels)"
      "$PY" -m pip install "${COMMON[@]}" torch 2>&1 | tail -3
    fi
  fi
fi

if [ "$MODE" = "pin" ]; then
  TV="$("$PY" -c 'import torch;print(torch.__version__)' 2>/dev/null)"
  if [ -n "$TV" ]; then
    echo "  -- pinning torch==$TV so the resolver keeps the installed build --"
    printf 'torch==%s\n' "$TV" > /tmp/azazael_torch_constraint.txt
    CT=("--constraint" "/tmp/azazael_torch_constraint.txt")
  else
    echo "  !! torch not importable; pin mode has nothing to pin"
    CT=()
  fi
else
  CT=()
fi

echo "  -- installing stack --"
"$PY" -m pip install "${COMMON[@]}" "${CT[@]}" $STACK 2>&1 | grep -E "^(Successfully|ERROR|error:)" | tail -4

echo "  -- installing undeclared leaf deps ($LEAF) --"
"$PY" -m pip install "${COMMON[@]}" $LEAF 2>&1 | grep -E "^(Successfully|ERROR|error:|Requirement already)" | tail -3

echo "  -- verification --"
"$PY" - <<'PY'
import importlib, sys
mods = ["torch","transformers","gymnasium","stable_baselines3","peft","trl",
        "datasets","accelerate","safetensors","numpy","networkx"]
ok = 0
for m in mods:
    try:
        mod = importlib.import_module(m)
        ok += 1
        print(f"    OK   {m:20s} {getattr(mod,'__version__','?')}")
    except Exception as exc:
        print(f"    FAIL {m:20s} {type(exc).__name__}")
print(f"  RESULT {ok}/{len(mods)}  free_threaded={not getattr(sys,'_is_gil_enabled',lambda:True)()}")
PY
