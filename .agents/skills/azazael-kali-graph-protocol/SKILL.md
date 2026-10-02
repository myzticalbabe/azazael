---
name: azazael-kali-graph-protocol
description: Established protocol for graphing the full Kali Linux tree with graphify + cosmos into the Desktop atlas — rsync mirror, .git boundary to seal the home-gitignore leak, go/ and venv exclusions, extract → cluster-only → tree → sync_out → cosmos. Load before any Kali graph extract.
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: false
  version: 1.0.0
  created: 2026-08-31
---

# azazael-kali-graph-protocol — Kali → Atlas Graph Pipeline

> **Created:** August 31, 2026
> **Purpose:** The ONLY known-working procedure for graphing the full Kali Linux codebase with graphify + cosmos into the Desktop atlas. Encodes the root causes of 4+ hours of failed runs so a re-scan is fast and correct.
> **Cross-reference:** `azazael-sync-kali`, `azazael-sync-patterns`, `Desktop/Graphify_Codebase_Atlas_2026-08-27/graphify_refresh_all.sh`, `Desktop/Graphify_Codebase_Atlas_2026-08-27/cosmos_build_atlas.sh`

## Why This Protocol Exists (failure history)

Three+ consecutive attempts stalled 10 hours+ with zero output. Every stall traced to the SAME class of mistake — graphify silently scanning trees it must not scan:

| Root cause | Symptom | Which run |
|---|---|---|
| Single 26k-file graph (venv site-packages + `.c` + vendored deps) | Assembly spun 10h+, 340MB flat memory, no output | Initial split attempt |
| Home-`.gitignore` leak: mirror nested under `C:/Users/clint/` (a git repo whose `.gitignore` lists `azazael/`, `Desktop/`, `go/`, `vermillion_lightfury/`) | `update`/`extract` recorded only 398–888 files; azazael entirely absent | Protocol run #1–3 |
| `go/pkg/mod` scanned (38,583 vendored `.go` files, zero project code) — exclusion file written to WRONG path (home dir, not mirror) | Assembly grinds 3h at 3.5GB, never converges | Protocol run #4 |
| `update` mechanism with stale incremental manifests | Undercount replayed from poisoned `graphify-out/` cache | Protocol run #2 |

**The fix that worked:** mirror → `.git` boundary + `go/.gitignore` + venv self-exclusions → `extract` → **steady-state refresh measured 45.5 s wallclock** (see Benchmark section): 41,531 nodes / 71,648 edges / 1,844 communities, 50 MB `graph.json` (Sep 2, 2026 measurement).

## Measured Benchmarks (Sep 2, 2026 — DO NOT quote unmeasured numbers)

Extract-phase wallclock on this machine (16 cores, graphify 0.9.50, kali_src mirror at 81k files):

| Run type | Workers | Workload | Wallclock |
|---|---|---|---|
| Steady-state refresh | 16 | 210 re-extracted + 1,997 cached (incremental) | **45.5 s** |
| Full cold AST | 16 | 2,005 files, fresh out-dir | **63.2 s** |
| Full cold AST | 32 | 2,005 files, fresh out-dir (identical) | **61.2 s** |

**Workers are NOT a speedup lever on this machine (16 cores):** doubling 16 → 32 changed cold extract by 63.2 → 61.2 s (−3.2%, noise-level — the pool is already at 1 thread/core; extra threads just contend). Do not recommend `GRAPHIFY_MAX_WORKERS` bumps as a fix here; the only lever that measurably shortens runs is shrinking the re-extraction set via the exclusions (the incremental manifest + AST cache are already doing the heavy lifting: 45.5 s steady-state vs 63.2 s cold).

## One-Command Summary (after mirror is in place)

```bash
cd "/c/Users/clint/Desktop/Graphify_Codebase_Atlas_2026-08-27"
bash graphify_refresh_all.sh kali   # extract → cluster-only → tree → sync_out → new kali/ folder
bash cosmos_build_atlas.sh kali     # cosmos-viewer.html + cosmos/ data + Desktop AZAZAEL_COSMOS_VIEWER_kali.html
```

Both scripts already have `kali` registered (`REPOS_EXTRACT` + viewer-shortcuts + cosmos defaults). A future refresh is those two lines.

## Step 1 — Source Layout (what "Kali" means)

Kali Linux lives in WSL2 (`E:/Kali/ext4.vhdx` — not directly browsable; all file ops via `wsl -d kali-linux`). The code roots inside `/root/`:

| Kali path | Contents | Graph treatment |
|---|---|---|
| `/root/azazael` | project code | INCLUDE |
| `/root/azazael-dev` | dev copy | INCLUDE |
| `/root/osint-tools/*` (theHarvester, GHunt, blackbird, TorBot, Moriarty, Osintgram, WhatsMyName, social-analyzer) | project code | INCLUDE (`node_modules` auto-pruned by built-in noise list) |
| `/root/FACEBOOK` | project code | INCLUDE |
| `/root/vermillion_lightfury` | project code | INCLUDE |
| `/root/go/pkg/mod` + `pkg/sumdb` | 38,583 vendored third-party Go modules, zero project code | EXCLUDE via `go/.gitignore` (`*`) |
| `/root/osint_venv`, `/root/openwebui-venv` | venv site-packages | self-exclude (their own `.gitignore` contains `*`) |

**The mirror** (Windows copy that graphify reads): `Desktop/Graphify_Codebase_Atlas_2026-08-27/kali_src/`. Rebuild it from Kali with `rsync -a` (batched, not per-file — each `wsl.exe` call has ~200ms overhead). **Do not interrupt the copy mid-run and do not let a later `--delete` pass wipe files added meanwhile.**

## Step 2 — The Two Exclusions (non-negotiable)

### 2a. `.git` boundary — seal the home-gitignore leak

The mirror must be its own VCS root. Without it, graphify's `_find_vcs_root` walks up to `C:/Users/clint/.git` and applies `C:/Users/clint/.gitignore` (which ignores `azazael/`, `azazael-dev/`, `go/`, `Desktop/`, `vermillion_lightfury/`) as the ceiling — silently excluding most of the tree.

```bash
cd "/c/Users/clint/Desktop/Graphify_Codebase_Atlas_2026-08-27/kali_src"
git init          # creates the .git boundary directory (nothing is committed)
```

### 2b. `go/.gitignore` — exclude the Go module cache

```bash
# File: kali_src/go/.gitignore
*
```

Verify BOTH are physically in the mirror before extracting:

```bash
test -d kali_src/.git && echo "git boundary OK" || echo "MISSING .git"
cat kali_src/go/.gitignore   # must print *
```

**WRITE-PATH GOTCHA (this bit us):** the write_file tool with a bare relative path (e.g. `kali_src/go/.gitignore`) resolves against the project root `C:/Users/clint/` — NOT the Desktop atlas. The exclusion silently landed in the home dir and every run scanned `go/pkg/mod`. Always use the full relative path from the project root: `Desktop/Graphify_Codebase_Atlas_2026-08-27/kali_src/go/.gitignore`, then verify with `cat` in the mirror.

## Step 3 — Extract (use `extract`, NOT `update`)

`update` reuses stale incremental manifests from `graphify-out/` and replays undercounts. `extract` does a fresh scan.

```bash
export GRAPHIFY_VIZ_NODE_LIMIT=1000000 GRAPHIFY_MAX_NODES=1000000
bash graphify_refresh_all.sh kali
```

Under the hood: `graphify extract kali_src --code-only --out <atlas>/kali`. Healthy signature to watch:

- **Scan count ≈ 2,000** files (not 26k–30k — if you see 30k, the go exclusion is missing or mispathed)
- **Assembly worker**: CPU monotonically advancing on a full core, memory ~3.4GB
- **STALL SIGNATURE (kill immediately)**: flat memory, ~340MB or unchanging CPU seconds, no output after minutes

## Step 4 — Cluster + Tree + Sync

`graphify_refresh_all.sh kali` runs the whole `refresh_extract` sequence automatically: `extract --code-only` → `cluster-only` → `tree` → `sync_out` into `Desktop/Graphify_Codebase_Atlas_2026-08-27/kali/`.

Expected artifacts in `kali/`:

| Artifact | Size (Aug 2026 reference) |
|---|---|
| `graph.json` | 50 MB — 41,524 nodes / 71,623 edges / 1,803 communities |
| `GRAPH_REPORT.md` | ~506 KB |
| `GRAPH_TREE.html` | ~2.9 MB |
| `graph.html` | ~41 MB |
| `manifest.json` | ~459 KB |

## Step 5 — Cosmos Build

```bash
bash cosmos_build_atlas.sh kali
```

Produces `kali/cosmos-viewer.html` + `kali/cosmos/*` data chunks + Desktop `AZAZAEL_COSMOS_VIEWER_kali.html` (11 MB single-file viewer) + `KALI_VIEWER.lnk` Desktop shortcut.

## Step 6 — End-to-End Verification

```bash
A="/c/Users/clint/Desktop/Graphify_Codebase_Atlas_2026-08-27"
ls -la "$A/kali/graph.json" "$A/kali/GRAPH_REPORT.md" "$A/kali/GRAPH_TREE.html" "$A/kali/graph.html"
ls -la "$HOME/Desktop/AZAZAEL_COSMOS_VIEWER_kali.html" "$HOME/Desktop/KALI_VIEWER.lnk"
tasklist | grep -iE "graphify|python"   # expect: none (no stray workers)
```

Open `AZAZAEL_COSMOS_VIEWER_kali.html` in Chrome to visually confirm azazael, osint-tools, FACEBOOK are present and venv/Go bloat is absent.

> **Since Sep 3, 2026 this step is automatic.** `graphify_refresh_all.sh` runs a CDP render check as its final step (see Step 7); you only need to do the manual Chrome look-see when the script's own check warns or when you changed the mirror contents.

## Step 7 — Auto-Verify: the CDP render check + stale-chunk guard (added Sep 3, 2026)

`graphify_refresh_all.sh` (both copies: `azazael/scripts/` and the atlas root) now ends with an automated viewer-render verification, so a broken or stale viewer can never silently ship.

### 7a. The stale-chunk failure mode (why verification is needed)

The atlas `graph.html` for **update-mode repos (azazael)** loads its data from 40 external chunks via `<script src>` — `graph.nd*.js` (nodes) + `graph.ed*.js` (edges). `graphify_refresh_all.sh`'s `sync_out()` used to copy only 7 files (graph.json, manifest, graph.html, report, labels, root) and **never the nd/ed chunks**. Result: after a refresh the atlas held a fresh `graph.html` next to Aug-27 chunks, and the deployed viewer rendered **404,317 nodes while GRAPH_REPORT.md said 410,128** — a silent 5,811-node undercount with zero errors in the console. The report was always correct; the viewer was stale.

Kali and the small repos embed their data **inline** in `graph.html` (no chunk srcs — verified: 0 `graph.nd*.js` references), so they were never affected by the chunk bug. The guard matters for azazael; the check covers all five.

**Detected by:** cross-checking the rendered node count (CDP `network.getPositions()`) against the GRAPH_REPORT.md summary — 410,128 vs 404,317 didn't match.

### 7b. The fix baked into the pipeline

1. **`sync_out()` now copies the chunks** — `graph.nd*.js` + `graph.ed*.js` alongside the 7 core artifacts (with a dated comment explaining why). Re-run refreshes can no longer strand stale chunks under a fresh html.
2. **Step 5 of the script = CDP render check** — `verify_viewers()` (in the script) runs `verify_graphs_cdp.py` (at `~/verify_graphs_cdp.py`) over every refreshed atlas `graph.html`:
   - Launches headless Chrome, navigates each viewer, waits for load + a rendered vis-network, counts nodes via `network.getPositions()`, and captures console errors/exceptions.
   - **Report cross-check is AUTOMATIC (Sep 3, 2026):** the harness parses each viewer's sibling `GRAPH_REPORT.md` `- N nodes` summary and compares it to the rendered count — a mismatch is flagged `COUNT-MISMATCH` with the rendered-vs-report values and **exit code 1**, so a stale-chunk regression like 404,317-vs-410,128 now fails the verify step instead of passing silently. `nodes=` and `report=` are shown side by side in the per-file output.
   - The generic `verify_aoa_cdp.py` 8s deadline cannot handle the 20–41 MB viewers — `verify_graphs_cdp.py` uses 90s load / 120s probe deadlines with a retry-loop probe.
   - **Non-fatal on failure** (warns with the FAIL lines; the refresh already succeeded) — but treat a FAIL as blocking before using the viewer.
3. **`--no-verify` opt-out** exists (also `--dry-run` lists it as `verify`); default is ON.

### 7c. Healthy signature (Sep 3, 2026 re-extract)

```
==> CDP render check: 5 viewer(s) via verify_graphs_cdp.py
  PASS  graph.html  loaded=True  vis=True  network=True  nodes=410133  report=410133  canvas=1  errs=0
  PASS  graph.html  loaded=True  vis=True  network=True  nodes=700     report=700     canvas=1  errs=0
  PASS  graph.html  loaded=True  vis=True  network=True  nodes=193     report=193     canvas=1  errs=0
  PASS  graph.html  loaded=True  vis=True  network=True  nodes=193     report=193     canvas=1  errs=0
  PASS  graph.html  loaded=True  vis=True  network=True  nodes=41529   report=41529   canvas=1  errs=0
SWEEP: 5 viewers — 5 passed, 0 failed
VERDICT: ALL CLEAN
```

Rendered counts must equal each repo's `GRAPH_REPORT.md` `- N nodes` line **exactly**. Expect tiny run-to-run churn from the incremental refresh (azazael drifted 410,128 → 410,133, kali 41,530 → 41,529 across a re-extract) — that is normal and both report + viewer move together; a mismatch between them is the bug.

## Anti-Patterns

- ❌ **`update` instead of `extract`** — stale incremental manifests replay undercounts. Use `extract` for kali.
- ❌ **Copying only graph.html + graph.json into the atlas, skipping `graph.nd*.js`/`graph.ed*.js`** — the atlas viewer renders STALE chunks under a fresh html (silent node undercount, 0 console errors). `sync_out()` must copy the chunks; verify the chunk dates match the refresh.
- ❌ **Trusting a viewer render without a node-count cross-check** — a stale viewer looks perfect in Chrome. Compare the rendered `network.getPositions()` count against the GRAPH_REPORT.md summary; they must match exactly.
- ❌ **Skipping the CDP render check** (`--no-verify`) on a release refresh — it is the only automated guard that a viewer loads, builds its network, and shows the right node count. Use `--no-verify` only for quick iteration runs.
- ❌ **Writing exclusions to a bare relative path** — lands in `C:/Users/clint/`, not the mirror. Always full path + verify with `cat`.
- ❌ **Single monolithic graph of the whole Kali tree** — 26k files (venvs, `.c`, Go cache) does not converge. Exclude caches, then graph.
- ❌ **Interrupting the rsync mirror mid-copy** — yields an incomplete mirror (2,366 py vs 6,752 live) and silently missing dirs.
- ❌ **Letting the mirror live deep under a git repo** — home `.gitignore` leaks in via the VCS ceiling. The mirror MUST have its own `.git`.

## Deprecated Leftovers — CLEANED UP (Sep 1, 2026) ✅

The improvised `kali_*` / `kali_test_*` split folders (`kali_azazael`, `kali_theHarvester`, `kali_ghunt`, `kali_blackbird`, `kali_FACEBOOK`, `kali_vermillion`, `kali_osint_misc`, `kali_src_osint_misc`, `kali_go`, `kali_osint_venv`, `kali_openwebui_venv`, `kali_test_az`, `kali_test_az2`, `kali_test_live`) and the `kali_split_graphs.sh` script were the first (wrong) approach and are superseded by the proper `kali/` repo. **All 16 were deleted on Sep 1, 2026 (user-directed).** As of that date the atlas root holds only the 5 repos (azazael, aoa_g, aoa_source, vermillion_lightfury, kali) + scripts + the `kali_src/` mirror. Do not recreate them or use them as a model.

## Related Skills

- `azazael-sync-kali` — Kali WSL2 sync integration (E: bridge, run_wsl_kali)
- `azazael-sync-patterns` — sync_all.py / sync_skills.py infrastructure
- `azazael-paths` — dynamic path resolution
- `azazael-catalog-maintenance` — how this skill is registered in SKILLS_CATALOG.md