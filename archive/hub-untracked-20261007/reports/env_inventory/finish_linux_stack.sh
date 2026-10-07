#!/usr/bin/env bash
# Finish installing the adaptation stack once torch works.
# Ubuntu already has transformers; Kali has neither, so this handles both.
set -uo pipefail
PY="${1:-/usr/bin/python3}"
COMMON=(--break-system-packages --only-binary=:all:)
export PIP_DISABLE_PIP_VERSION_CHECK=1

TV="$("$PY" -c 'import torch;print(torch.__version__)' 2>/dev/null || true)"
echo "=== $PY  torch=${TV:-NONE} ==="
if [ -z "$TV" ]; then
  echo "  -- no working torch; installing CPU-only torch first --"
  "$PY" -m pip install "${COMMON[@]}" --index-url https://download.pytorch.org/whl/cpu torch \
    2>&1 | grep -E "^(Successfully|ERROR)" | tail -2
  TV="$("$PY" -c 'import torch;print(torch.__version__)' 2>/dev/null || true)"
  echo "  torch now = ${TV:-STILL NONE}"
fi

CT=()
if [ -n "$TV" ]; then
  printf 'torch==%s\n' "$TV" > /tmp/azazael_torch_pin.txt
  CT=("--constraint" "/tmp/azazael_torch_pin.txt")
  echo "  pinning torch==$TV so the resolver does not swap in a CUDA build"
fi

echo "  -- installing stack (transformers first: it is the slow one) --"
"$PY" -m pip install "${COMMON[@]}" "${CT[@]}" \
  transformers gymnasium stable_baselines3 peft accelerate trl datasets \
  2>&1 | grep -E "^(Successfully|ERROR|error:)" | tail -4

echo "  -- undeclared leaf deps --"
"$PY" -m pip install "${COMMON[@]}" narwhals threadpoolctl 2>&1 \
  | grep -E "^(Successfully|ERROR|Requirement already)" | tail -2

echo "  -- verification --"
"$PY" - <<'PY'
import importlib, sys
mods = ["torch","transformers","gymnasium","stable_baselines3","peft","trl",
        "datasets","accelerate","safetensors","numpy","networkx"]
ok = 0
for m in mods:
    try:
        importlib.import_module(m); ok += 1; print(f"    OK   {m}")
    except Exception as exc:
        print(f"    FAIL {m:20s} {type(exc).__name__}: {str(exc)[:70]}")
print(f"  RESULT {ok}/{len(mods)}  free_threaded={not getattr(sys,'_is_gil_enabled',lambda:True)()}")
PY
