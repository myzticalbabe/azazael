# Forensic Investigation — All Environments

**Date:** 2026-10-02
**Investigator:** Buffy (Codebuff) — read-only probes; no environment mutated.
**Probe host:** Windows 11 / Git Bash, `MINGW64_NT-10.0-26300`, host `LAPTOP-8U5MSH3G`.

---

## 1. Environment Inventory (measured, not declared)

Six environments are configured in `scripts/sync_all.py::ENVIRONMENTS`; the canonical
SDK doc (`CROSS_ENV_MANIFEST.md`, Jul 2) predates the Quartet re-role and lists four.

| # | Environment | Path probed | Present | .py | Files | Size | Git |
|---|-------------|-------------|:-------:|:---:|:-----:|:----:|-----|
| 1 | **Windows — RUNNING tree (clone)** | `/c/Azazael/azazael` | ✅ | 4,488 | 31,915 | 3.3 G | `migration/baseline-20261001 @ fa0c41d5` (2026-10-02 14:58), 8 dirty |
| 2 | **Windows — original (sync hub)** | `/c/Users/clint/azazael` | ✅ | — | 66,803 | — | `migration/baseline-20261001 @ 1e30c2c1` (2026-10-02 17:55), **719 dirty** |
| 3 | **WSL Ubuntu-26.04** | `Ubuntu-26.04:/root/azazael` | ✅ | 2,425 | 11,119 | 870 M | `master @ 7d883baba2` (2026-07-29), dirty |
| 4 | **WSL Kali Linux** | `kali-linux:/root/azazael` | ✅ | 2,896 | 6,731 | 519 M | **NO `.git`** |
| 5 | **Desktop AZAZAEL_Standalone** | `C:/Users/clint/Desktop/AZAZAEL_Standalone` | ❌ **ABSENT** | — | — | — | — |
| 6 | **G: archives** | `/g/AZAZAEL`, `/g/AZAZAEL_SOURCE_OF_TRUTH`, `/g/AZAZAEL_Standalone`, `/g/AZAZAEL_UBUNTU` | ✅ | — | — | large/slow | see below |

### G: sub-archives
- `/g/AZAZAEL` — main archive (16 GB declared). Sub-trees: `AZAZAEL_ROOT`, `AOA`, `CODEX_Studio`, `CODEX_VIDEOS`. Newest content Sep 5 / Jul 2.
- `/g/AZAZAEL_SOURCE_OF_TRUTH` — archive mirror, `.git` present, `master @ e47e3e36` (2026-06-21), **clean**.
- `/g/AZAZAEL_Standalone` — **52 `.exe`** at top level (built May 28–29).
- `/g/AZAZAEL_UBUNTU` — `drivers/`, `python-wheels/`, `scripts/` (Feb 15). No source.
- `/g/AZAZAEL/AZAZAEL_ROOT` — `.git` present but **branch `master` has NO commits** (unborn HEAD); 856 `.py`. Largest source tree.

### Other
- **WSL distros registered:** `Ubuntu-26.04` (v2), `kali-linux` (v2), `docker-desktop` (v2). All were **Stopped** on first probe.
- **Docker daemon:** NOT running (`npipe:////./pipe/dockerDesktopLinuxEngine` missing). Consistent — Docker Desktop rides WSL, which was stopped.
- `/root/vermillion_lightfury` present **only on Kali** — correct per Quartet role.

---

## 2. Interpreters

| Environment | Version | `Py_GIL_DISABLED` | Verdict |
|-------------|---------|:-----------------:|---------|
| Windows `python` | 3.14.7 | **0** | ⚠️ **GIL build — NOT free-threaded** |
| Windows `python3.14t` | 3.14.7 | 1 | ✅ free-threaded |
| Ubuntu-26.04 | 3.14.7 | 1 | ✅ free-threaded |
| Kali Linux | 3.14.6 | 1 | ✅ free-threaded |

The project mandates the 3.14t free-threaded interpreter. The bare `python` on PATH
resolves to the **GIL build**; only `python3.14t` is free-threaded. `sync_all.py`'s own
docstrings call `python3.14t sync_all.py --verify`, but any tool invoked as bare
`python` runs on the GIL build.

---

## 3. `sync_all.py --status` verdict (run on Windows GIL interpreter)

```
[OK] Windows 11 (primary dev)      .py: 757  docs: 53
[OK] WSL2 Ubuntu-26.04 (wsl)       .py: 633  docs: 53
[XX] Desktop AZAZAEL_Standalone (release)          <-- MISSING
[OK] G: source-of-truth (archive)  .py: 735  docs: 53
[OK] G: AZAZAEL_ROOT (archive)     .py: 856  docs: 53
[OK] Kali Linux (WSL2) (wsl)       .py: 668  docs: 53

Integrity: ALL SYNCED
```

---

## 4. Defects found

### D-1 (HIGH) — "ALL SYNCED" printed while an environment is `[XX]`
`verify_integrity()` checks only four dimensions: `expansion`, `docs_g`, `tests`,
`scripts`. **Desktop standalone is never included in the verdict.** A missing release
environment therefore reports green. The status table says `[XX]`; the integrity line
says `ALL SYNCED`. Two instruments in the same tool disagree, and the reassuring one wins.

### D-2 (HIGH) — Kali is invisible to the integrity check
`verify_integrity()` hardcodes a single WSL root: `Path("/root/azazael")` (Ubuntu) or
`run_wsl("ls /root/azazael/...")` against the **default** distro. Kali shares the same
path string, so the two WSL pillars are indistinguishable to the check. Kali — declared
**canonical source** — is not verified at all, and the Ubuntu/Kali swap would be silent.

### D-3 (MEDIUM) — Missing `G:` fails open
`results["docs_g"] = win_docs.issubset(g_docs) if g_docs else True`. An unavailable or
empty G: returns **True** ("skip"). This is the codebase's own named class: *empty ≠ clean*.

### D-4 (HIGH) — Kali, the canonical source, has no git history
`/root/azazael` on Kali is **not a git repository**. The Quartet declares Kali canonical.
It carries the smallest `.py` count of any source tree (2,896 in 6,731 files) and no way
to diff it against anything.

### D-5 (HIGH) — Kali and Windows diverged by months; Ubuntu by ~2 months
HEADs (where they exist): Windows `2026-10-02`, Ubuntu `2026-07-29`, G: SOURCE `2026-06-21`.
No common revision exists across the pillars. "ALL SYNCED" is a *filename-subset* check,
not a content or revision check — it can pass across a two-month code gap.

### D-6 (HIGH) — Two Windows trees, the newer one is NOT the running one
The probe host runs `/c/Azazael/azazael` @ `fa0c41d5` (14:58). The original
`/c/Users/clint/azazael` is **ahead** @ `1e30c2c1` (17:55) and carries **719 dirty paths**.
`sync_all.py`'s `windows` hub root points at `C:/Users/clint/azazael`, so sync measures the
original while the agent session edits the clone. This is the known editable-install
shadowing failure, now with the clone *behind* its own hub.

### D-7 (MEDIUM) — `AZAZAEL_ROOT` is a git repo with zero commits
`/g/AZAZAEL/AZAZAEL_ROOT/.git` exists, branch `master` unborn. 856 `.py` — the largest
source tree — with no revision history, so it cannot be a source of truth.

### D-8 (LOW/CONTEXT) — Desktop standalone stale-vs-declared
`CROSS_ENV_MANIFEST.md` declares a Desktop release environment; the configured path does
not exist. G: holds **52** `.exe` (manifest claims 39), all dated May 28–29 — an earlier
successful build, contradicting the "standalone never built" note in the skill catalog.

### D-9 (INFO) — Probe noise
WSL emitted `The wsl2.localhostForwarding setting has no effect when using mirrored
networking mode` and `Failed to create stream fd` on each cold start. Cosmetic, but it
precedes real stdout and was reported three times per invocation.

---

## 5. What was NOT determined
- Content-level (hash) parity between pillars — not attempted; the tree spans >3 GB and a
  slow G: volume. The status/verify path is filename-based, so no hash comparison exists.
- Whether Kali's missing `.git` is by design (Kali "mined" from G:) or accidental.
- pgrep/process liveness of chain controllers in each WSL distro (out of scope here).

---

## 6. Method / reproduction
Read-only. Commands used: `git rev-parse/log/status`, `find -type f | wc -l`,
`du -sh`, `uname -a`, `wsl.exe -l -v`, `wsl.exe -d <distro> -e bash -lc '...'`,
`python -c "import sysconfig; get_config_var('Py_GIL_DISABLED')"`,
`python scripts/sync_all.py --status`, `docker ps -a`.
Full recursive scans of G: were aborted (multi-GB, slow volume); top-level metadata only.

---

## 7. Reconciliation addendum (2026-10-02, same day)

### Determination
`C:\Azazael\azazael` (A) is NOT a disposable clone — it is the **live execution tree**:
the editable install points at it (`__editable__.azazael-1.0.0.pth` → `C:\Azazael\azazael\src`;
`direct_url.json` → `file:///C:/Azazael/azazael`; `import CORE` → `C:\Azazael\azazael\src\CORE`).
`C:\Users\clint\azazael` (B) is the **git hub/origin** (A.origin = B; B pushes to
`G:/source-of-truth/azazael.git`). B strictly contained A's HEAD as an ancestor plus **6 commits**.

### Actions taken
1. `git fetch origin` in A — this alone killed the silent drift; A then reported `[behind 6]`
   instead of a false `0/0` (its `origin/*` refs had frozen at A's own HEAD).
2. `git reset --hard origin/migration/baseline-20261001` — A advanced `fa0c41d5` → `1e30c2c1`.
   Verified lossless: every conflicting file was byte-identical to the target; untracked
   `embedding_config.json`, `reports/`, `state/*.jsonl` preserved. `conftest.py` and the
   `archive/live-monitors-20261002/` set now present.
3. **Hub flip was already implemented** in B's committed `sync_all.py` (commit `0cc201bd`):
   `_WINDOWS_ROOT = Path(__file__).resolve().parent.parent`. Advancing A flipped the hub
   automatically — A now measures itself (`.py` 620).
4. New guard: `scripts/origin_freshness_check.py` — fetches, then measures; exits `1` when
   behind, `0` when current, `2` when undeterminable; never advances the branch. Verified
   with stubbed git: behind-6 → rc1, current → rc0, no-upstream → rc2.
5. Wired as **Step 0.5** of the MANDATORY STARTUP SEQUENCE in `SESSION_STARTUP.md`.

### Status changes
- **D-1 (Desktop `[XX]` vs `ALL SYNCED`)** — symptom **RESOLVED**: the Desktop path in B's
  newer `sync_all.py` is `C:/Azazael/desktop/AZAZAEL_Standalone`, which exists and reports `[OK]`.
  *Correction:* my original D-1 evidence was against A's OLDER `sync_all.py`.
- **D-6 (two Windows trees)** — **RESOLVED**: A is the live/execution tree, B the hub;
  the relationship is now explicit and A is current.
- **D-2, D-3** — **RESOLVED** (see §8). `verify_integrity()` now probes Ubuntu and Kali
  with separate runners and fails closed when G: is absent. The verdict still does not
  score the Desktop environment (an `.exe`-only release, deliberately not a parity peer).
- **D-4** — **RESOLVED BY DECISION** (see §9): Kali deliberately keeps no `.git`.
- **D-5, D-7** — unchanged (revision divergence; `AZAZAEL_ROOT` unborn).

---

## 8. Integrity-check fix (D-2, D-3) — 2026-10-02

Both defects lived in `scripts/sync_all.py::verify_integrity()` and both were
*false-green* modes: the verdict could pass while the thing it claimed to measure
was never examined.

**D-2 — Kali indistinguishable from Ubuntu.** The helper read:

```python
rc, stdout, _ = run_wsl(f"ls /root/azazael/{subpath}/{ext} 2>/dev/null")
```

`run_wsl` is hardwired to `Ubuntu-26.04`, and Ubuntu and Kali *both* keep their
tree at `/root/azazael`. So the two distros were addressed by the same path and the
same runner: Kali was never probed, and any divergence between the distros — or
between Windows and Kali — was invisible. Fix: the helper now takes a `distro`
argument that selects `run_wsl_kali` vs `run_wsl`, and the verdict adds explicit
`expansion_kali`, `tests_kali`, `scripts_kali` results. An unreachable Kali yields an
empty set and therefore a mismatch, i.e. it fails closed.

**D-3 — missing G: passed.** The read:

```python
results["docs_g"] = win_docs.issubset(g_docs) if g_docs else True  # skip if G: unavailable
```

`if g_docs else True` made an unmounted/empty G: (an *unknown* archive) report as
synced. An unknown archive is not a passing one. Fix: `results["docs_g"] =
bool(g_docs) and win_docs.issubset(g_docs)` — absent G: now fails.

Verified: `python3.14t -m py_compile scripts/sync_all.py` clean; `--status` and
`--verify` re-run and the new `*_kali` keys appear in the verdict.

---

## 9. Decision (D-4): Kali deliberately keeps no git repository — 2026-10-02

**Probed state of Kali** (`wsl.exe -d kali-linux`): `/root/azazael/.git` does not
exist, `git rev-parse HEAD` fails, and the tree is otherwise present (668 `.py` under
`src/`). No remote, no refs.

**Decision: do NOT `git init` Kali.** Rationale:

1. **Role.** Kali is a *sync target*, not a source. `sync_wsl_to_kali()` populates it
   from Ubuntu-26.04 via the `E:\kali_sync_temp` bridge. Its content is defined by a
   copy, so its provenance is a file comparison — not a commit history it would author.
2. **History topology.** There is exactly one canonical history: the Windows hub
   (`C:\Azazael\azazael`, origin `C:\Users\clint\azazael`) pushing to
   `G:/source-of-truth/azazael.git`. A repo inside Kali would be a *third* independent
   history with no shared ancestry — the same class of divergence that produced the
   silent-lag defect this reconciliation just fixed. Adding it would manufacture the
   next instance of the bug being repaired.
3. **What would change the decision.** If Kali ever becomes a development source (edits
   originate there rather than being copied in), it must not be a bare repo synced by
   file copy. At that point the correct move is to give it a real clone of the canonical
   history with the hub as `origin` — i.e. promote it to a peer of the Windows hub, not to
   give it a fresh unrelated repo.

This decision is recorded here so the absence of `.git` in Kali is read as **intentional
and explained**, not as an environment that lost its history.
