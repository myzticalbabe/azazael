# agents.md — agent-facing workstation config (WSL Ubuntu-26.04)

## Paste into this CLI (wl-clipboard)

`wl-clipboard` installed 2026-10-21 via `apt install wl-clipboard`.
Transport is WSLg Wayland (`WAYLAND_DISPLAY=wayland-0`); verified
`wl-paste --list-types` returns `text/plain` + `STRING`.

```bash
wl-paste > /tmp/pasted.txt          # dump Windows clipboard to a file
wl-paste | head -c 2000             # peek without flooding the transcript
some-command | wl-copy              # put output on the Windows clipboard
```

Notes: `wl-paste` blocks when the clipboard is empty — always wrap probes
in `timeout 10`. This is a Wayland client; if `wsl --shutdown` was run,
re-check `WAYLAND_DISPLAY` before trusting it.

## Stale-reference census (retired pathways + Natures fold-back)

Instrument: `scripts/audit_stale_refs.py` (doctrine: CHOICE vs INVENTORY —
a launcher that EXECUTEs a retired name is ERROR; a doc/archive that DESCRIBES
it is INFO and must not be rewritten). Severity model (2026-10-21): `.py` `#`
comments demote to INFO (they record, never execute); `.json` data demotes to
WARN (verify the consumer); generated/frozen dirs (`.graphify-live`, `var`,
`logs`, `temp`) are skipped. Only executable references fail the run.

```bash
python3 -u scripts/audit_stale_refs.py --root <tree> --tag <env> --error-only
```

Reports land as `state/stale_refs_<env>.json`. Tags in use:
`win-primary` (C:/Azazael/azazael), `win-secondary`
(C:/Users/clint/azazael — DISTINCT live tree, not a copy of primary),
`wsl` (/root/azazael), `g-archive` (/mnt/g/AZAZAEL/AZAZAEL_ROOT, frozen).

9P THROTTLE RULE: never run the census or the graph build from WSL over
/mnt/c. The DrvFs/9P bridge turns 73k small-file reads into a multi-minute
crawl and throttles the free-threaded interpreter. Run Windows trees
natively in Git Bash under py315t (free-threaded, NTFS-direct):

```bash
/c/Azazael/.venvs/py315t/Scripts/python.exe \
  /c/Azazael/azazael/scripts/audit_stale_refs.py \
  --root C:/Users/clint/azazael --tag win-secondary --error-only
/c/Azazael/.venvs/py315t/Scripts/python.exe \
  /c/Azazael/azazael/scripts/audit_stale_refs.py \
  --root C:/Azazael/azazael --tag win-primary --error-only
```

WSL-side scans are fallback only (wsl + g-archive trees are local/ext4
or single-pass archival — those are fine from here).

Retirement records (read before proposing deletions):
- 3.14 pathways: this session's trace (py315t @ /opt/python315t, GIL wrapper
  /usr/local/bin/python3.14-gil); `tools/repoint_315t.py` (Windows migration).
- Natures taxonomy (U3/G3, D1): `NATURE_CLUSTERS.py` + `CROSS_NATURE_ROUTER.py`
  deleted 2026-10-02; `NATURE_DEFINITIONS == {}` is the ASSERTED end-state
  (packages/azazael-core/run_tests.py). Forensic recovery:
  `state/RECOVERED_NATURE_DEFINITIONS.json` (16 natures, bytecode-authoritative).
  Fold-back signatures the audit flags: a live `NATURE_CLUSTERS.py` source,
  a repopulated (non-empty) `NATURE_DEFINITIONS` literal, any
  `CROSS_NATURE_ROUTER` import. Importing the empty symbol is a legit shim.

## Import-edge graph (find ALL edges before claiming a removal is clean)

```bash
python3 scripts/ecosystem_graph.py --out state/graph_refresh_<date> --no-db
```

922 nodes / 1694 import edges on the 2026-10-21 refresh of win-primary.
Query `graph.json` for edges into the removed symbol's former module —
zero edges + zero live imports == removal holds. Scope is src/+scripts/;
packages//tools/ need the content audit above, not the graph.
Windows-only `graphify_refresh_all.sh` atlas is NOT refreshed from here
(WSL cannot exec the Windows venv interpreters; interop launches fail).
Same 9P rule applies to `ecosystem_graph.py`: refresh win-primary's graph
from Git Bash with py315t, not from WSL python3 over /mnt/c.
