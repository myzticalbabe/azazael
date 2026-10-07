#!/usr/bin/env bash
# Can the self-adaptation stack resolve on this Linux interpreter?
PY="${1:-/usr/bin/python3}"
echo "=== $PY ==="
"$PY" -c 'import sys;print("python",sys.version.split()[0],"free_threaded=",not getattr(sys,"_is_gil_enabled",lambda:True)())'
"$PY" -m pip install --dry-run --only-binary=:all: \
    gymnasium stable_baselines3 peft trl datasets transformers 2>&1 \
  | grep -E "^(Would install|ERROR|error:|Successfully)" | head -5

