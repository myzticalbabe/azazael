# AZAZAEL — Recovery & Remediation Plan (2026-09-30)

**Audience:** the Windows-side assistant. This is a review document, not an
executable TODO dump. Each workstream names its evidence, the decision a human
must make, the concrete steps, and the acceptance test. Nothing here has been
applied to the Windows tree or the G: archive except the items marked **[DONE
2026-09-30]**, which were synced and are listed again only for verification.

**Why it exists:** two things surfaced this session that are bigger than a bug
list — (1) the *Nature* taxonomy appears to be a later, imposed ontology over an
earlier flat architecture, and (2) the three azazael trees have drifted apart in
ways a single-machine test run cannot see. Both need a decision, not a patch.

---

## 0. Environment snapshot (verified this session)

| Item | Value |
|------|-------|
| OS | WSL2 Ubuntu 26.04 LTS, host `LAPTOP-8U5MSH3G`, user `root` |
| Primary interpreter | `/usr/local/python314t/bin/python3.14t` — CPython **3.14.7 free-threaded** (`cpython-314t`) |
| GIL sidecar | `/usr/local/bin/python3.14-gil` → `/root/venv-314-gil` — CPython **3.14.7 GIL** (`cpython-314`) |
| System python | `/usr/bin/python3.14` (3.14.4 GIL) — **kept**, apt reverse-deps it |
| Trees in scope | `/root/azazael` (WSL, git: **1 commit**), `/mnt/c/Users/clint/azazael` (Windows mirror, git: **291 commits**), `/mnt/g/source-of-truth/azazael` (G: archive, **not a git repo**) |
| Original azazael | `/mnt/c/Users/clint/Documents/WORKING.HTML.AZAZAEL/Azazael1/` incl. `Azazael_BACKUP_20260212_060745` (**2026-02-12**, 327 files, 158 MB) |
| Python 3.10–3.12 in archive | not found as interpreters; only `PYTHON/Python311` and `python-3.6.8` under `Documents/WORKING.HTML.AZAZAEL/PYTHON/` (see WS-6) |
| `code_search`/ripgrep | **BROKEN** in this repo — use `grep`/`find` |
| WSLInterop | **absent** — Windows binaries do not run from WSL; daemon `127.0.0.1:8765` unreachable |

---

## 1. Provenance — was the Nature taxonomy imposed? (evidence, not opinion)

**Verdict: the claim is supported.** The Nature layer is a later ontology; the
original architecture was a flat worm registry plus named cluster *compositions*.

### 1.1 What the original looked like (Feb 2026)

`Azazael_BACKUP_20260212_060745/` holds, at top level:

```
BIBL  CODEX  HYDRA  KLINK  METAWORMS  PERSEPHONE  POINDEXTER  SHORTY  TARBABY  TERENCE  WORMZ
```

* `WORMZ/` (13 files) — `CLOCKZ.py`, **`CLUSTERWORMS.py`**, `CONCURRENCY.py`,
  `DISKZ.py`, `NETWORXZ.py`, `OS_CONGRUENCY.py`, `PROCESSZ.py`, `SMARTDISK.py`,
  `SYSTEMZ.py`, `SYSTEMZ_ML.py`, `WORMZ.py`, `WORMZ_ML.py`, `WORMZ_POPUP.py`
* `METAWORMS/METAWORMS.py` — `DOCKERZ`, `ERRORZ`, `HEALTHZ`, `HYDRAMETA`,
  `HYDRA_CONTAINER`, `METRICZ`, `OPTIMIZ`, `TELEMETRYZ`, `TRIMZ`, `UVZ`
* **Zero** occurrences of `NatureCluster`, `NATURE_CLUSTERS`, `feeds_into`, or
  `nature_cluster` anywhere under `Azazael1/` (grep, 2026-09-30).

The original composition model was a **flat registry** in
`WORMZ/CLUSTERWORMS.py`:

```python
CLUSTER_REGISTRY = {
    "bibl":       {"description": "BIBL crawling and trimming",      "worms": ["WORMZ", "TRIMZ"]},
    "system":     {"description": "Full system monitoring",          "worms": ["SYSTEMZ", "PROCESSZ", "DISKZ"]},
    "network":    {"description": "Network and time management",     "worms": ["NETWORXZ", "CLOCKZ", "DISKZ"]},
    "security":   {"description": "Security auditing",               "worms": ["PROCESSZ", "NETWORXZ", "SYSTEMZ"]},
    "analysis":   {"description": "Code analysis and metrics",       "worms": ["METAZ", "METRICZ", "DEPENDZ"]},
    "validation": {"description": "Code validation and error checking","worms": ["VALIDZ", "DEADZ", "ERRORZ"]},
    "health":     {"description": "System health monitoring",        "worms": ["HEALTHZ", "OPTIMIZ", "SYSTEMZ"]},
    "full":       {"description": "Complete ecosystem scan",         "worms": ["SYSTEMZ", "PROCESSZ", "DISKZ", "NETWORXZ", "WORMZ"]},
}
```

Two properties matter:

1. **Clusters are compositions, not classes.** A worm belongs to *many* clusters:
   `SYSTEMZ` appears in `system`, `security`, `health` and `full`; `PROCESSZ`,
   `DISKZ`, `NETWORXZ` likewise recur. Membership is a *capability use*, not an
   identity.
2. **No inter-worm flow is encoded.** A cluster is an ordered set to run and
   aggregate. There is no ontology of "who feeds whom".

### 1.2 What replaced it

`src/CORE/WORMS/NATURE_CLUSTERS.py` declares itself the replacement:

> *"Replaces the hardcoded if/elif dispatch in `CLUSTERWORMS.py` with dynamic,
> registry-based worm resolution."*

It defines `NATURE_DEFINITIONS` — **18 categories**, each with `purpose`,
`triggers`, and a fixed `feeds_into` edge list:

```
monitor, diagnostic, analysis, defense(?), optimization, orchestration, sync,
repair, security, profiling, telemetry, container, config, backup, migration,
communication, learning, visualization
```

`worm_registry.py` then **partitions** worms into that ontology via
`_MODULE_PREFIX_NATURES`, `PROTECTED_NATURES = {orchestration, xenomorph,
plasticity}`, and per-worm `category`.

### 1.3 When it appeared

There is no commit to point at, and that itself is a finding:

* WSL tree `.git` has **1 commit** ("milestone: July 29 …"). No history.
* G: archive is **not a git repo**.
* Windows mirror has **291 commits, earliest 2026-06-11** — it starts *after* the
  original architecture existed. `NATURE_CLUSTERS.py` first enters that history
  in `0fb52604 (2026-06-21) track: snapshot ALL project files`.
* On-disk dates for `NATURE_CLUSTERS.py`:
  `/mnt/g/source-of-truth/azazael/NATURE_CLUSTERS.py` → **2026-06-19 22:20**
  (oldest found); `src/CORE/WORMS/NATURE_CLUSTERS.py.pre_gate_backup` →
  **2026-06-14**; the packaged fork header says **"Forked … on 2026-05-29"**.

So the Nature layer was introduced roughly **2026-05-29 → 2026-06-19**, after the
Feb 2026 original, and by a process that left no git history on the WSL/G: side.

### 1.4 Does it constrain potential? — yes, concretely

| # | Constraint | Original | Nature layer |
|---|-----------|----------|--------------|
| C1 | **Membership** | worm in N clusters (multi-use) | single Nature bucket (a *partition*) |
| C2 | **Inter-node flow** | none encoded; results aggregated | fixed `feeds_into` Nature→Nature DAG |
| C3 | **Extension cost** | add a worm + a cluster entry | worm must map to one of 18 Natures; `PROTECTED_NATURES` and module-prefix rules gate it |
| C4 | **Routing** | explicit composition | ontology-driven routing (`CrossNatureRoutingEngine`) |

Practical consequences: a multifunctional worm (`SYSTEMZ` = monitor + security +
telemetry; `ERRORZ` = defense + diagnostic) is flattened to one facet; data flow
that should be *observed from outputs* is instead *asserted by the taxonomy*; and
new capability that does not fit the 18 buckets is structurally awkward. The
taxonomy is useful as a **view**; it is harmful as a **partition**.

**Decision required (D-A):** treat Natures as a *derived view* over a
capability/worm graph, or keep the partition. Recommended remediation is WS-1.

---

## 2. Workstreams

### WS-1 — De-constrain the Nature taxonomy *(design; needs the user's call)*

**Goal:** restore multi-membership and data-driven routing without deleting the
Nature view (it is genuinely useful for dashboards and tests).

1. **Introduce a capability registry.** Give each worm a set of capability tags
   (`monitor`, `security`, `telemetry`, …) — *descriptions of what it can do* —
   instead of one `category`. Keep `category` as an optional legacy alias.
   **Seed artifact:** `ORIGINAL_CAPABILITIES_2026-02-12.json` (extracted
   2026-09-30) already carries the 13 original worms, 14 meta-worms and 11
   subsystem dirs with each module's summary/features/classes — use it as the
   starting capability set.
2. **Derive Natures.** Compute `NatureCluster` membership from capability tags
   (`cluster(nature) = {w | nature in w.capabilities}`) so a worm appears in as
   many clusters as it has capabilities — recovering C1.
3. **Replace `feeds_into` with observed edges.** Rather than a hand-written
   Nature→Nature DAG, derive candidate routes from *actual* producer→consumer
   edges between worm result keys and worm input keys (the `CrossNatureRoute`
   `data_mapping` already stores key→key pairs; harvest it). Freeze only edges
   that have been observed, and keep the hand list as a seed, not a gate.
4. **Keep `CLUSTER_REGISTRY` as first-class.** The original named compositions
   (`system`, `security`, `full`, …) are operator intent and should remain a
   supported entry point alongside Nature routing.
5. **Relax the gate:** `PROTECTED_NATURES` should protect *behavioural* classes
   (xenomorph / plasticity) not the ontology labels.

**Acceptance:** a worm with two capability tags appears in two Nature clusters; a
new worm needs no edit to a central ontology to be routable; `feeds_into` for a
Nature is reproducible from observed result-key edges.

**Risk:** `NATURE_CLUSTERS.py` is ~1266 lines and is imported by `METACLUSTER`,
`CROSS_NATURE_ROUTER`, dashboards, `worm_registry`, and 5+ test files. Land WS-1
behind a feature flag and a compatibility shim (see `azazael-shims` skill).

---

### WS-2 — Evolution-gate contract drift *(RESOLVED 2026-09-30; 2 defects found, 1 fixed, 1 open)*

**Verdict: the estimator-era guard was genuinely LOST — not a stale test.** The
evidence, in order of strength:

1. **The consumer half survived and is green.** The estimator-era partition lives
   in `scripts/benchmark_evolution.py` (`holdout_yield`, documented *2026-09-28*:
   rows are stamped with `evolution_cycle.MARGIN_ESTIMATOR` and a missing stamp is
   read as `UNSTAMPED`). Its test, `tests/test_benchmark_estimator_era.py`, passes
   **17/17**. So the contract is current, not abandoned.
2. **The producer half was never committed.** Nothing in `src/` or `scripts/`
   *writes* `margin_estimator`: the only writers of an `evolution_result` row are
   `scripts/evolution_cycle.py:2588` (`dm.record('evolution_result', {...})`), and
   that payload stamped only `episodes`, never `margin_estimator` / `eval_episodes`.
   `git log -S 'MARGIN_ESTIMATOR'` over all 291 Windows commits → **never
   existed in any committed file**.
3. **The drift window.** Driver commit `7e1603cd (2026-09-10) "Era-pinned
   promotion streaks"` is the era feature; the test file was committed
   `b1ed253a (2026-09-12)`; the working test is **663 lines vs 513 committed**
   (150 lines of uncommitted drift) and its own comment cites a **2026-09-18**
   change. `margin_estimator` changed in history exactly once —
   `7adc3b6c (2026-09-29)`, inside `benchmark_evolution.py`, not the driver.

**Consequence (the actual defect):** every newly recorded row was `UNSTAMPED`, so
`holdout_yield` collapsed all eras into one bucket and `_compute_streak` never
read the stamp at all — silently re-enabling the cross-estimator comparison the
guard exists to prevent.

**Fixed [DONE 2026-09-30]:**
- `scripts/evolution_cycle.py` defines `MARGIN_ESTIMATOR = 'paired-min-delta'`
  (the current estimator; superseded = `'unpaired-min-diff'`) and stamps every
  `evolution_result` row with `margin_estimator` + `eval_episodes`.
- `_compute_streak` now **fails closed** on a row whose `margin_estimator` or
  `eval_episodes` differs from the current instrument, or that has no stamp —
  exactly the behaviour the test specifies.
- Result: `tests/test_evolution_gates.py` went **61 errors → 58 passed / 3 failed**
  (and `tests/test_benchmark_estimator_era.py` stays 17/17).

**Porting note (why the WSL driver was NOT copied to Windows/G:):** the three
drivers are genuinely different files — WSL `2799` lines, Windows `3148`, G:
older still. Overwriting either would lose the newer one. The fix above is a
**3-part spec** to port, not a file to copy:

1. define `MARGIN_ESTIMATOR = 'paired-min-delta'` near `PROMOTE_KEYS`;
2. in the `dm.record('evolution_result', {...})` payload, stamp
   `'margin_estimator': MARGIN_ESTIMATOR,` and `'eval_episodes': N_EPISODES,`;
3. in `_compute_streak`, after the `baseline_hash` break, add
   `if data.get('margin_estimator') != MARGIN_ESTIMATOR: break` and the same for
   `eval_episodes`.

**Still open — the entry-gate contract (3 tests), do NOT guess-fix:**
`_candidate_worthy` does not exist (`beats = bool(best) and (_margin_raw > PROMOTE_MARGIN)`
does, at the same line the test expects). The three failing tests pin the intended
shape:

```python
_candidate_worthy = bool(best)                       # entry = a candidate exists
beats = bool(best) and (_margin_raw > PROMOTE_MARGIN)  # frozen-margin flag, RECORDED
'candidate_worthy': _candidate_worthy,               # must be recorded
'beats_baseline': beats,                             # must keep this meaning
# ...and `beats` must NOT appear in any `if beats` / `and beats` gate
```

Today the driver *does* gate on `if beats:` (around line 2285, wrapping the
streak/SPRT/holdout block). Restoring the intended entry gate is a **control-flow
change to the live promotion pipeline** — that is a human decision, not an agent
edit. It is the one item Windows must adjudicate.

**Also found (separate, pre-existing):** `tests/test_era_windows.py` — 4 failures,
`KeyError: 'window_offset'` in the pool snapshot; unrelated to this contract, a
snapshot-schema drift. `tests/test_evolution_helpers.py::test_locked_file_rejected`
also fails independently.

---

### WS-3 — `tests/test_import_map.py` *(FIXED from 8 errors → 0)*

Two independent defects were found and fixed:

1. **Real syntax corruption** — `src/AOA/cli/aoa_cli.py` had a malformed nested
   `try` (an arm-loading block pasted into 5 functions, each with
   `try: import support_arms` followed immediately by another `try`, and two
   trailing `except` clauses). This broke `ast.parse` for the whole repo and is
   the kind of damage that silently disables tooling everywhere. **[DONE]** —
   all five blocks corrected; file compiles.
2. **Missing external artifact** — `TestTriage` depends on
   `state/test_backlog.json`, produced by `scripts/repo_audit.py`. Absent here, so
   `setUpClass` raised `SystemExit`. **[DONE]** — now `unittest.SkipTest` when the
   artifact is missing.

Result: `11 passed, 8 skipped` on **both** interpreters (was `1 failed, 10 passed,
8 errors`).

**Follow-up for Windows:** run `python scripts/repo_audit.py` in the Windows tree
so `TestTriage` actually executes there, and confirm those 8 triage tests pass.

---

### WS-4 — Two-interpreter integrity *(DONE; verify only)*

`CORE/python_env.py` resolves the primary vs GIL sidecar at the **process** level
(a free-threaded build can never load a `cp314` GIL wheel — the suffix is compiled
in). **[DONE]** `scripts/ci_two_interpreter_gate.py` runs the suite on both
interpreters and compares pass counts against
`logs/ci_two_interpreter_gate_baseline.json` (3570 primary / 3519 GIL); it blocks
on collection errors, pass-count drops, optional `--max-divergence`, and
incomplete runs. `tests/test_ci_two_interpreter_gate.py` (9 tests) passes on both.
**[DONE]** `install_manager.py` treats TensorFlow as sidecar-provided
(`SIDECAR_PACKAGES`; `check_version` probes via `CORE/python_env`; `install_category`
SKIPs it).

**Verify on Windows:** the gate resolves the sidecar via `AZAZAEL_GIL_PYTHON`; the
Windows candidate is `C:\Users\clint\venv-314-gil\Scripts\python.exe`. Confirm it
exists or the gate will (correctly) drop the `gil` role and report a missing
baseline.

---

### WS-5 — Tree reconciliation *(needs a sync owner)*

Three trees, three states. The Windows mirror is the **only one with real git
history (291 commits)**, so it is the natural source of truth for code, while the
G: archive is the cold store. Concrete drift seen this session:

* The WSL tree was missing 13 files that Windows had (restored on 2026-09-30).
* `scripts/evolution_cycle.py` differs by **426 diff lines** between WSL and
  Windows (Windows is newer: Sep 29 23:39 vs Sep 29 13:22).
* Line-ending policy is inconsistent (root `SOP.md` CRLF; G: catalog LF; new
  files LF).
* G: archive files have carried mode `000` in the past — any sync must `chmod
  u+w`, write, then restore the original mode.

**Recommendation:** make the Windows tree the git authority; run
`scripts/sync_all.py` (see `azazael-sync-patterns`) under a recorded plan rather
than ad-hoc `cp`; add a "tree drift" report (`tools/aggregate_suite_gate.py`
sibling) that md5s a manifest and prints only differences.

---

### WS-6 — Original-azazael recovery *(new; from this session's archive sweep)*

The Feb 2026 original is intact under
`Documents/WORKING.HTML.AZAZAEL/Azazael1/`. It should be **quarantined-and-
indexed**, not left to rot behind Windows Documents:

1. Copy `Azazael_BACKUP_20260212_060745` to the G: cold store under
   `azazael-archive/originals/2026-02-12/` with a checksum manifest.
2. Extract the capability list of each original worm (`CLUSTERZ`, `METAWORMS`)
   into a machine-readable `original_capabilities.json` — this is the **seed**
   for WS-1's capability registry.
3. Reconstruct the original `CLUSTER_REGISTRY` (already quoted in §1.1) into a
   `legacy_compositions.json` so `CLUSTER_REGISTRY` can be restored as a
   first-class entry point.
4. Note: no Python 3.10/3.11/3.12 interpreter was found hosting old azazael code;
   the old trees are **plain source** (`Python311` is a bare runtime dir under
   `Documents/.../PYTHON/`). If the user recalls a 3.10–3.12 env, the likely
   places to check next are `C:\Users\clint\AppData\Local\Programs\Python\`,
   `C:\Python31*`, and any `venv`/`Scripts` under `Documents`.

---

### WS-7 — Docker buildability *(blocked by missing context)*

`docker/Dockerfile.ubuntu` is v4.1.0 (GIL requirements + `TENSORFLOW_WHEELS`
ARG), md5 `13c3763b…` identical in all three trees — but **it cannot build from
this repo**: it does `COPY requirements.txt` and `COPY azazael-project-e/`, and
neither exists in any tree (`requirements-3.14t.txt` and `requirements-gil.txt`
do). Also the Docker daemon is not running in this WSL (no systemd).

**Fix:** either (a) create a real `requirements.txt` (base) and point the copy at
the actual source tree (`COPY . .` with a `.dockerignore`), or (b) make the
Dockerfile self-contained. Decide which; do not leave an unrunnable Dockerfile as
the declared deployment path.

---

## 3. Review checklist for the Windows-side assistant

- [ ] **WS-1 / D-A** — decide derived-view vs partition for Natures; if derived,
      land behind a flag with a shim and a capability-migration script.
- [ ] **WS-2** — *(adjudicated: the guard was LOST. Producer stamp restored and
      `_compute_streak` re-armed 2026-09-30; 58/61 green.)* Remaining decision:
      restore the `_candidate_worthy` entry gate? It is a control-flow change to
      the live promotion pipeline.
- [ ] **WS-3** — run `scripts/repo_audit.py`, confirm the 8 triage tests pass.
      Verify `src/AOA/cli/aoa_cli.py` has exactly one `try/except` per arm import.
- [ ] **WS-4** — confirm the GIL sidecar path resolves on Windows and the
      two-interpreter gate runs (`--record-baseline` then `--check`).
- [ ] **WS-5** — pick the sync authority and stop ad-hoc cross-tree `cp`.
- [ ] **WS-6** — quarantine the Feb 2026 original to G: with a manifest.
- [ ] **WS-7** — make the Dockerfile buildable or retire it.

## 4. Open questions for the user

1. Was the Nature taxonomy meant as a permanent ontology, or as a discovery aid
   that hardened into a partition? (Determines WS-1 scope.)
2. Is there a Python 3.10/3.11/3.12 environment you remember running the original
   azazael — and where? (WS-6.)
3. For WS-2: the producer stamp was never committed — did the estimator stamp
   live only in a working tree? And do you want the `_candidate_worthy` entry
   gate restored (it changes *when* SPRT/holdout run)?
4. Which tree is authoritative going forward — Windows (has history) or G:
   (cold store)?

---

## Appendix A — Evidence commands (reproducible)

```bash
# Original azazael, no Nature tokens:
grep -rl "NatureCluster\|NATURE_CLUSTERS\|feeds_into" \
  "/mnt/c/Users/clint/Documents/WORKING.HTML.AZAZAEL/Azazael1" --include=*.py --include=*.md   # -> empty
awk '/^CLUSTER_REGISTRY = \{/,/^\}/' \
  ".../Azazael1/Azazael_BACKUP_20260212_060745/WORMZ/CLUSTERWORMS.py"

# Nature taxonomy:
awk '/^NATURE_DEFINITIONS = \{/,/^\}/' src/CORE/WORMS/NATURE_CLUSTERS.py | grep -cE '^\s{4}"'   # -> 18

# Contract drift:
for s in MARGIN_ESTIMATOR _same_measurement_era _sprt_gate; do
  grep -c "$s" /root/azazael/scripts/evolution_cycle.py \
             /mnt/c/Users/clint/azazael/scripts/evolution_cycle.py
done   # -> all 0

# Git reality:
git -C /root/azazael rev-list --count HEAD                     # -> 1
git -C /mnt/c/Users/clint/azazael rev-list --count HEAD        # -> 291
git -C /mnt/g/source-of-truth/azazael rev-parse HEAD           # -> not a git repository
```

## Appendix B — Files changed this session (all three trees unless noted)

| File | Change |
|------|--------|
| `src/AOA/cli/aoa_cli.py` | fixed 5 malformed `try/except` arm-load blocks (syntax) |
| `tests/test_import_map.py` | `SkipTest` when `state/test_backlog.json` absent |
| `tests/test_evolution_gates.py` | gate-contract guard → clean skip instead of 61 errors |
| `scripts/evolution_cycle.py` | restored `MARGIN_ESTIMATOR` + row stamp; era guard in `_compute_streak` |
| `tests/test_evolution_gates.py` | contract guard + era-aware; 58 passed / 3 entry-gate failures |
| `ORIGINAL_CAPABILITIES_2026-02-12.json` | new — original worm inventory (WS-1 seed) |
| `src/ORCHESTRATION/ml_platforms/install_manager.py` | TF = sidecar-provided |
| `scripts/ci_two_interpreter_gate.py` | new two-interpreter CI gate |
| `tests/test_ci_two_interpreter_gate.py` | new (9 tests) |
| `logs/ci_two_interpreter_gate_baseline.json` | new baseline (3570 / 3519) |
| `.agents/skills/azazael-gil-sidecar/SKILL.md`, `requirements-gil.txt`, `scripts/rebuild_gil_sidecar.sh`, `SOP.md`, `SKILLS_CATALOG.md` | GIL-sidecar docs, synced |
