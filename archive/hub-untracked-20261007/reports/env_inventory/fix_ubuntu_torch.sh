#!/usr/bin/env bash
# Ubuntu's torch 2.12.0 is a CUDA build whose CUDA runtime libs are absent:
#   OSError: libcudart.so.13: cannot open shared object file
#   ValueError: libcublasLt.so.*[0-9] not found in the system path
# so `import torch` dies at _load_global_deps() and every consumer sees
# "torch missing" while `pip list` reports it installed.
#
# Options were (a) install the nvidia-* CUDA wheels (multi-GB, and Ubuntu's vhdx
# sits on C: which has ~36 GB free) or (b) replace with CPU-only torch (~200 MB,
# actually works). This does (b) and reports what it found.
set -uo pipefail
PY="${1:-/usr/bin/python3}"
COMMON=(--break-system-packages --only-binary=:all:)
export PIP_DISABLE_PIP_VERSION_CHECK=1

echo "=== pre-state ==="
"$PY" -m pip show torch 2>/dev/null | grep -E "^(Name|Version)" | sed 's/^/  /'
"$PY" -m pip list 2>/dev/null | grep -icE "^nvidia-" | sed 's/^/  nvidia-* packages installed: /'
echo "  --- removing the broken CUDA build ---"
"$PY" -m pip uninstall -y torch 2>&1 | grep -E "^(Successfully|WARNING|ERROR)" | tail -2

echo "=== installing CPU-only torch ==="
if "$PY" -m pip install "${COMMON[@]}" \
      --index-url https://download.pytorch.org/whl/cpu torch 2>&1 \
      | grep -E "^(Successfully|ERROR|error:)" | tail -3
then :; fi

echo "=== verify torch ==="
"$PY" -c "
import torch
print('  torch', torch.__version__, 'cuda_available=', torch.cuda.is_available())
" 2>&1 | tail -3
