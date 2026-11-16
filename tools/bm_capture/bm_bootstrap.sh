#!/usr/bin/env bash
# BM first-boot bootstrap: verifies the BM estate, then runs every capture
# probe in order. Fails fast with a named step (set -e + step echoes), so a
# first-try failure names its step instead of half-writing captures.
# Usage on the BM boot:  bash bm_bootstrap.sh /path/to/repo-checkout [/tmp/bm_pkg]
set -e
step() { echo "=== STEP: $1 ==="; }

REPO="${1:?usage: bm_bootstrap.sh /path/to/repo-checkout [/tmp/bm_pkg]}"
CAP="${2:-/tmp/bm_pkg}"
HERE="$(cd "$(dirname "$0")" && pwd)"

step "0 precondition: python3 + repo checkout"
python3 --version
test -d "$REPO" || { echo "MISSING repo checkout: $REPO"; exit 2; }
mkdir -p "$CAP"

step "1 apt captures"
apt list --installed > "$CAP/apt_installed.txt"
apt-mark showmanual > "$CAP/apt_manual.txt"
wc -l "$CAP/apt_installed.txt" "$CAP/apt_manual.txt"

step "2 pip capture (no pip required)"
python3 "$HERE/probe_pip.py" > "$CAP/pip_14t.txt"
wc -l "$CAP/pip_14t.txt"

step "3 tree imports (repo: $REPO)"
python3 "$HERE/probe_tree.py" "$REPO" > "$CAP/tree_imports.json"
head -c 200 "$CAP/tree_imports.json"; echo

step "4 reverse deps"
python3 "$HERE/probe_revdeps.py" > "$CAP/revdeps.json"
head -c 120 "$CAP/revdeps.json"; echo

step "5 entry points + locations (locations is REQUIRED, never skip)"
python3 "$HERE/probe_env.py" entry_points > "$CAP/entry_points.json"
python3 "$HERE/probe_env.py" locations > "$CAP/locations.json"
CAP="$CAP" python3 -c 'import json,os;d=json.load(open(os.environ["CAP"]+"/locations.json"));print("locations:",len(d))'
test -s "$CAP/locations.json" || { echo "EMPTY locations.json"; exit 3; }

step "DONE: $CAP"
ls -la "$CAP"
