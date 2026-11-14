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
#   scripts/graphify_bin.sh update src
#   GRAPHIFY_BIN=scripts/graphify_bin.sh scripts/graphify_refresh_all.sh
#
# Overrides:
#   GRAPHIFY_PY  — interpreter to use, skipping resolution entirely.
#   GRAPHIFY_ALLOW_SCOPE_DRIFT=1 — permit a graph write outside the store
#                  codegraph reads (announced on stderr; see below).
#
# Scope guard (2026-11-14): before exec, tools/graphify_scope_guard.py decides
# whether this invocation would write a graph nobody reads. graphify writes
# beside whatever it is pointed at, so `cd <repo> && graphify update` (or a
# plain `graphify .`) lands a graph in <repo>/graphify-out/ while every lane --
# and the startup gate -- read <repo>/src/graphify-out/graph.json. The write
# succeeded, so nothing complained; the store just stayed stale. The guard
# computes the real out dir and exits 3 naming the remedy instead. Read
# commands, and runs whose output lands outside this repo, pass through
# untouched. A guard that cannot run is a loud failure, never a silent skip.
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

# Last resort: the project's own roles, primary first (3.14t is retired).
# The Python314 install is deliberately absent from this ladder: it is a base
# interpreter kept on disk, not a launch choice.
if [ -z "$PY" ] || [ ! -x "$PY" ]; then
    for cand in \
        "C:/Azazael/.venvs/py315t/Scripts/python.exe" \
        "C:/Azazael/.venvs/py315/Scripts/python.exe" \
        "C:/Azazael/.venvs/py314m/Scripts/python.exe"; do
        [ -x "$cand" ] && { PY="$cand"; break; }
    done
    [ -x "$PY" ] || {
        echo "graphify_bin.sh: no usable graphify interpreter found" >&2
        echo "  tried: resolver candidates, then the 3.15t/3.15-gil/3.14m roles" >&2
        echo "  set GRAPHIFY_PY=<python with graphify installed>" >&2
        exit 127
    }
fi

# Write-side scope guard. `|| exit $?` is load-bearing: this script runs with
# `set -uo pipefail` and no -e, so an unhandled non-zero would fall through to
# exec and produce exactly the orphan graph the guard exists to prevent.
"$PY" "$ROOT/tools/graphify_scope_guard.py" --repo-root "$ROOT" -- "$@" || exit $?

exec "$PY" -m graphify "$@"
