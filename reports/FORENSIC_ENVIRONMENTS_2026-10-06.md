# FORENSIC ENVIRONMENTS + GIT — 2026-10-06

Host: LAPTOP-8U5MSH3G · Probed from Windows/Git Bash · Read-only investigation
Supersedes baseline: `reports/FORENSIC_ENVIRONMENTS_2026-10-02.md`

**Production runtime: Python 3.15t** (user-confirmed). All other versions are migration targets for systematic retirement.

---

## 1. Environment inventory

| # | Pillar | Path | Git | HEAD | State |
|---|--------|------|-----|------|-------|
| 1 | Windows RUNNING tree | `C:/Azazael/azazael` | branch `migration/baseline-20261001` | `5bc7ca63` (Oct 6 15:25, "Lab: CISPO clipped off-policy IS weights…") | 31,649 tracked files, 4,718 py; 60 dirty (33 M / 27 ??) |
| 2 | Windows HUB (origin) | `C:/Users/clint/azazael` | same branch | `db0f1b15` (Oct 4 17:34, "PSYCHE live-fit tool") | 404 dirty (2 M / 402 ??), 2 stashes, `.python-version=3.14.6t` |
| 3 | WSL Ubuntu-26.04 | `/root/azazael` | `master` | `7d883ba` (2026-07-29) — **unchanged since July** | 1,066 dirty, 2,425 py, 870M, Python 3.14.7 |
| 4 | WSL kali-linux | `/root/azazael` | **NO .git** | — | 2,896 py, 519M, Python 3.14.6 |
| 5 | G: source-of-truth (bare) | `G:/source-of-truth/azazael.git` | bare | `b32b0ed2` (Oct 4 16:53, PSYCHE Phase 5) | **12 commits behind running tree** |
| 6 | G: archives | `G:/AZAZAEL` (52G), `G:/azazael` | — | — | du on `/g/azazael` timed out (not re-measured) |
| 7 | Desktop standalone | — | — | — | **GONE.** No AZAZAEL dir on `C:/Users/clint/Desktop` (only a shortcut .lnk). `C:/Azazael/desktop` exists (Oct 2) |

## 2. Git forensics — the headline

**The Oct-2 divergence (D-6) has INVERTED.** The running tree was 3h behind the hub on Oct 2; it is now **11 commits ahead**:

- Running-only (11): Python 3.15t migration wave — CI→3.15t workflow, `requires-python>=3.15`, scripts renamed 314→315, launchers→Python315, build/installer 3.15 paths (`d5a959c9`, **C-body of nuitka patch UNVERIFIED per commit msg**), cycle scripts sys.path fix, quarantine validator + xdist watchdog, test importers, INTEROP.mmd regeneration, GDPO + CISPO lab commits.
- Hub-only (1): `db0f1b15` PSYCHE live-fit tool (PAMS rows → fitted theta) — **not in running tree**.
- Histories diverged (not fast-forwardable either way). Hub still `.python-version=3.14.6t`, requirements-3.14t only.
- Hub holds 2 stashes: `stash@{0}` "hub working tree pre-reconcile (folded into A d95b1d3a)", `stash@{1}` WIP on feat/worm-nuclei-bridge.
- Hub's 402 untracked = state(95), logs(77), tools(63), scripts(46), src(20), reports(20), dashboard(19), docs(7), config(5), .agents(4)…
- Running tree origin → hub. Hub remote `gdrive` → bare repo. **G: backup is 12 commits stale.**
- No local `master` in the running tree (only baseline branch + remotes).
- MCP/tooling processes (`codegraph_mcp.py`, `pams_server_launcher.py`) still reference **the HUB tree**, not the running tree — same class of defect as D-6, now in the MCP layer.

## 3. Python version census (retirement targets)

| Runtime | Location | Size | Verdict |
|---|---|---|---|
| **3.15t** (prod) | `C:\...\Python315\python3.15t.exe`, default `py -V:3.15t *` | 169M (site-packages only 14M — sparse) | KEEP — expand |
| **3.15 GIL** | `C:\...\Python315\python.exe`, `C:/Azazael/.venvs/py315` | venv 1.1G | KEEP (watchdogs run on it) |
| **3.14t** | `C:\...\Python314\python3.14t.exe` | **9.0G total / 7.1G site-packages** | RETIRE after freeze |
| **3.14 GIL** | `C:\...\Python314\python.exe` | (in the 9.0G) | RETIRE |
| **uv 3.14.3+ft** | `AppData\Roaming\uv\python\cpython-3.14.3+ft…` | 3.9M | RETIRE |
| **Store 3.13** | `WindowsApps\…Python.3.13…` | unknown | RETIRE |
| venvs (repo-external) | `C:/Azazael/.venvs/`: build315t 41M, py315t 1.3G, py315 1.1G | — | KEEP (3.15 family) |
| WSL Ubuntu | `/usr/local/bin/python3.14t` + `-gil` sidecar, pip at `/usr/local/python314t/…` | — | RETIRE/UPGRADE to 3.15t |
| WSL Kali | system 3.13 (`python3.13`), no 3.15t | — | RETIRE/UPGRADE |
| Hub `.python-version` | `3.14.6t` | — | REPOINT to 3.15t |
| Stale reqs | `requirements-3.14t.txt`, `requirements-gil.txt`, `requirements_314_full.txt` (hub); `requirements-3.14t.txt` (running) | — | REMOVE after freeze |

## 4. opencode build takeover (user mandate)

- opencode PID 10268 (12:03 PM, ~53 min CPU) — still running.
- **The binary build = lancedb 0.39.0 Python wheel, compiled from source via maturin** for the 3.15t free-threaded ABI:
  `C:/Azazael/.venvs/build315t/Scripts/python.exe -m maturin build --release --interpreter C:/Azazael/.venvs/py315t/Scripts/python.exe --out C:/Azazael/.build/wheels` (PIDs 4888/5376, alive at 16:5x, >1h).
- Source at `C:/Azazael/.build/lancedb-0.39.0` (protoc.zip downloaded 15:10). `wheels/` still empty — normal: lancedb+arrow+datafusion stack is a multi-hour --release compile. Log shows steady crate progress; only a dead-code warning so far. **No error — let it run.**
- Why: no prebuilt cp315t wheel exists; PMB (vector store) needs it. **No lancedb references in app code/requirements** — dependency belongs to `.pmb-venv`, not azazael itself.
- Second opencode task: py315t pytest-xdist run (`test_config_and_breaker.py` et al., ~30 workers, 4:06 PM) — **finished**; `pmb_session_observe.py --pytest-exit 0` hooks ran.
- `watchdog_5min.py` ×2 running on `py315` venv.

## 5. Natures (user mandate: removed but keeps resurrecting; needs refactor)

- `NATURE_CLUSTERS.py` exists in **3 divergent git-tracked copies**: repo root, `src/CORE/WORMS/`, `packages/azazael-core/src/azazael_core/worms/clusters/` (3 distinct md5s) + a 4th stale copy in hub root (Jul 27).
- **60+ referencing files**: `CLUSTERWORMS.py`, `worm_registry.py`, `expansion/{mesh,spine,queens,fabric_state,federated,learning_grpo,wiring_genome,spawn_credit}.py`, `azazael_arm.py`, `azazael_ctl.py`, `metrics.py`, `worm_governance.py`, `worm_health.py`, `dead_letter_queue.py`, `neural_loop.py`, `spine_registry.py`, `INFERENCE_WORM.py`, `NIM_INFERENCE.py`, `PARALLEL_INFERENCE_WORM.py`, `CODEX_TOOLS.py`, 15 test files, `tools/nature_integration_map.py`, `tests/test_nature_integration_map.py`, `scripts/{generate_capability_templates,metacog_cycle,run_mesh_cycle}.py`, graph_semantic layers.
- `__pycache__` shows cpython-314 **and cpython-315** imports → it is still live in the 3.15t runtime.
- Resurrection mechanism: hub tree copy (Jul 27, outside git tracking of running tree) + 3 in-tree copies + sync scripts = any single-point deletion gets re-imported/re-synced. Requires a coordinated multi-copy removal with import-site refactor, not a file delete.

## 6. Remediation queue (proposed order)

1. **P0 — protect work**: wait for maturin wheel; verify install into py315t + pmb-venv. Verify nuitka patch C-body (`d5a959c9` says UNVERIFIED).
2. **P0 — reconcile git**: land hub's `db0f1b15` (PSYCHE live-fit) onto the running tree lineage; resolve the 60 dirty paths in running tree (33 M / 27 ??); update G: backup (+12 commits); decide hub-tree fate (stashes, 404 dirty).
3. **P1 — Natures refactor**: single source of truth (or full removal), refactor 60+ import sites, delete 3 root copies + hub copy, update tests/tools.
4. **P2 — version retirement**: after freeze — uninstall Python 3.14 pair (frees 9G), uv 3.14.3+ft, Store 3.13; repoint hub `.python-version`; purge 3.14 requirement files; upgrade WSL interpreters; delete old cpython-314 `__pycache__` trees.
5. **P2 — MCP repoint**: `codegraph_mcp.py`/`pams_server_launcher.py` and opencode config point at hub tree; repoint to running tree (D-6 class).
6. **P3 — repo hygiene**: hub 404 untracked paths triage; 2 stashes resolve-or-drop; `master` vs baseline strategy on running tree.
