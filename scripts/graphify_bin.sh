#!/usr/bin/env bash
# coding: utf-8
# graphify_bin.sh — launch graphify through the install that actually works.
#
# Why this exists (2026-10-09): graphify_refresh_all.sh defaulted to
# ~/.local/bin/graphify.exe, a uv trampoline that has stopped resolving:
#
#     $ ~/.local/bin/graphify.exe --version
#     error: uv trampoline failed to canonicalize script path
#
# That killed the refresh at repo 1 (azazael) and the remaining repos never
# ran. The box still has a working graphify -- 0.9.72 in Python314's
# site-packages -- so the failure was binary resolution, not a missing tool.
#
# Three places were resolving graphify independently and disagreeing:
#   1. tools/graphify_interpreter.py  -> capability-based, correct (ADR-019)
#   2. graphify_refresh_all.sh        -> hard-coded ~/.local/bin/graphify.exe
#   3. scripts/graphify_node_limit_patch.py -> picked the uv install and SKIPped
# This wrapper removes (2) by delegating to (1), so the refresher and the
# resolver can no longer drift apart.
#
# Usage (drop-in for the graphify binary):
#   scripts/graphify_bin.sh update C:/Azazael/azazael
#   GRAPHIFY_BIN=scripts/graphify_bin.sh scripts/graphify_refresh_all.sh
#
# Overrides:
#   GRAPHIFY_PY  — interpreter to use, skipping resolution entirely.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"

resolve() {
    local py="$1"
    command -v "$py" >/dev/null 2>&1 || return 1
    "$py" - "$ROOT" <<'PYEOF' 2>/dev/null
import sys
root = sys.argv[1]
sys.path.insert(0, root + "/tools")
try:
    import graphify_interpreter as gi
except Exception:
    sys.exit(1)
# report=no-op: the resolver's own chatter belongs to its callers, not to a
# process whose stdout is a subcommand's output.
py = gi.resolve_graphify_python(report=lambda *a, **k: None)
if py:
    print(py)
PYEOF
}

PY=""
if [ -n "${GRAPHIFY_PY:-}" ]; then
    PY="$GRAPHIFY_PY"
else
    for cand in python python3 py; do
        out="$(resolve "$cand")" && [ -n "$out" ] && { PY="$out"; break; }
    done
fi

# Last resort measured on this box: the install the resolver itself prefers.
if [ -z "$PY" ] || [ ! -x "$PY" ]; then
    PY="$HOME/AppData/Local/Programs/Python/Python314/python.exe"
    [ -x "$PY" ] || {
        echo "graphify_bin.sh: no usable graphify interpreter found" >&2
        echo "  tried: resolver candidates, then $PY" >&2
        echo "  set GRAPHIFY_PY=<python with graphify installed>" >&2
        exit 127
    }
fi

exec "$PY" -m graphify "$@"
