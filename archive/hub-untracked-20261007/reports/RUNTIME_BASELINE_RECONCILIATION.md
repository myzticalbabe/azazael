# Runtime Baseline Reconciliation — what one lockfile would cost

**Date:** 2026-09-20
**Baseline:** `azazael/config/runtime_baseline.toml` (generated, 35 contract + 29 supporting pins)
**Checkers:** `scripts/build_runtime_baseline.py`, `scripts/check_runtime_baseline.py`
**Evidence:** `reports/env_inventory/baseline_check.json` (live probe of all 6 environments)

---

## 1. The contract, in one sentence

Across the six Python environments there are **64 distributions present
everywhere**, of which **35 cross a process, machine, or file boundary** — HTTP
clients, serialisation, encodings, dates, numerics. Those 35 are the
*interoperability contract*: if two environments disagree on one of them, a
message produced by one can be rejected, silently mis-parsed, or ordered
differently by the other. The remaining 29 are supporting packages where pinning
is desirable but a mismatch is tolerated.

**Current state: 22 of the 35 contract packages are skewed. 50 changes are
required before one lockfile could be valid on all six environments.**

```
  [FAIL] win-main         637 dists   violations= 5  supporting_drift= 9
  [FAIL] win-314t         178 dists   violations=10  supporting_drift= 6
  [FAIL] win-313tools     127 dists   violations= 4  supporting_drift= 5
  [FAIL] win-interp       149 dists   violations=12  supporting_drift=12
  [FAIL] ubuntu           300 dists   violations=12  supporting_drift=11
  [FAIL] kali            1009 dists   violations= 7  supporting_drift= 7

VERDICT: FAIL — 50 contract violation(s)
```

---

## 2. Exactly what has to change

### win-main — 5 moves

| package | now | target |
|---|---|---|
| `aiohappyeyeballs` | 2.6.2 | **2.7.1** |
| `aiohttp` | 3.13.5 | **3.14.3** |
| `filelock` | 3.32.3 | **3.32.5** |
| `typing-inspection` | 0.4.2 | **0.4.4** |
| `yarl` | 1.24.2 | **1.24.5** |

### win-314t (the 3.14t target) — 10 moves

| package | now | target | direction |
|---|---|---|---|
| `filelock` | 4.0.0 | **3.32.5** | ⬇ **downgrade** |
| `fsspec` | 2026.6.0 | **2026.7.0** | ⬆ |
| `idna` | 3.20 | **3.19** | ⬇ **downgrade** |
| `multidict` | 6.9.0 | **6.7.1** | ⬇ **downgrade** |
| `numpy` | 2.4.6 | **2.5.3** | ⬆ |
| `propcache` | 0.5.4 | **0.5.2** | ⬇ **downgrade** |
| `pydantic` | 2.13.5 | **2.13.4** | ⬇ **downgrade** |
| `pydantic-core` | 2.46.5 | **2.46.4** | ⬇ **downgrade** |
| `urllib3` | 2.8.0 | **2.7.0** | ⬇ **downgrade** |
| `yarl` | 1.25.1 | **1.24.5** | ⬇ **downgrade** |

### win-313tools — 4 moves

| package | now | target |
|---|---|---|
| `anyio` | 4.15.0 | **4.15.1** |
| `numpy` | 2.5.2 | **2.5.3** |
| `pydantic` | 2.13.5 | **2.13.4** ⬇ |
| `pydantic-core` | 2.46.5 | **2.46.4** ⬇ |

### win-interp — 12 moves

| package | now | target |
|---|---|---|
| `aiohttp` | 3.14.1 | **3.14.3** |
| `anyio` | 4.14.1 | **4.15.1** |
| `certifi` | 2026.6.17 | **2026.7.22** |
| `charset-normalizer` | 3.4.9 | **3.5.1** |
| `click` | 8.4.2 | **8.5.0** |
| `filelock` | 3.29.6 | **3.32.5** |
| `fsspec` | 2026.6.0 | **2026.7.0** |
| `idna` | 3.18 | **3.19** |
| `numpy` | 2.5.1 | **2.5.3** |
| `packaging` | 26.2 | **26.3** |
| `typing-inspection` | 0.4.2 | **0.4.4** |
| `yarl` | 1.24.2 | **1.24.5** |

### ubuntu — 12 moves

| package | now | target |
|---|---|---|
| `anyio` | 4.13.0 | **4.15.1** |
| `certifi` | 2026.5.20 | **2026.7.22** |
| `charset-normalizer` | 3.4.7 | **3.5.1** |
| `click` | 8.4.1 | **8.5.0** |
| `filelock` | 3.29.0 | **3.32.5** |
| `fsspec` | 2026.4.0 | **2026.7.0** |
| `idna` | 3.16 | **3.19** |
| `numpy` | 2.4.6 | **2.5.3** |
| `packaging` | 26.2 | **26.3** |
| `rpds-py` | 2026.5.1 | **2026.6.3** |
| `typing-extensions` | 4.15.0 | **4.16.0** |
| `typing-inspection` | 0.4.2 | **0.4.4** |

### kali — 7 moves

| package | now | target |
|---|---|---|
| `charset-normalizer` | 3.5.0 | **3.5.1** |
| `click` | 8.4.2 | **8.5.0** |
| `fsspec` | 2025.12.0 | **2026.7.0** |
| `jsonschema-specifications` | 2023.12.1 | **2025.9.1** |
| `packaging` | 24.2 | **26.3** |
| `rich` | 13.9.4 | **15.0.0** |
| `rpds-py` | 0.30.0 | **2026.6.3** |

---

## 3. The honest caveat — 10 of the 50 moves are downgrades

The generator picks the **modal** version — the one the most pillars already
run — because that minimises the number of environments that must move. The
cost is that `win-314t` (the 3.14t target runtime) has to move *backwards* on
8 packages, and `win-313tools` on 2, to match the majority.

That is a real trade-off, not an oversight:

| Policy | Moves | Envs touched | Downgrades | Effect |
|---|---:|---:|---:|---|
| **modal** (chosen) | 50 | 6 | 10 | Fewest total moves; the newest environment is dragged back |
| **newest-wins** | ~62 | 6 | 0 | Nothing ever goes backwards; every env moves |

If downgrading the target runtime is unacceptable, regenerate with the
newest-wins policy — but expect ~12 more moves, several of them on Kali and
Ubuntu, where the newer versions may not be available from the distro repos at
all.

**Recommendation:** adopt the modal baseline for the 22 skewed packages *except*
`filelock` (4.0.0 → 3.32.5 is a major-version downgrade). Pin `filelock` at
`4.x` and move the other five environments up instead — one extra move buys
avoidance of a major-version regression.

---

## 4. What "one lockfile valid everywhere" actually requires

A single lockfile is achievable **only if the platform constraint is handled
explicitly**, because two of the six environments are Linux and four are
Windows, and `torch` alone resolves to `+cpu` on Windows and CUDA builds on
Linux:

1. **A shared `contract` requirement set** — the 35 pins above, identical in
   every environment's install step.
2. **A per-role layer** for what is *allowed to differ* — `ml-accelerator`
   (Ubuntu, CUDA), `security` (Kali, the 1,009-package offensive surface),
   `graph`, `interpreter`. The `[roles]` table in the baseline already names
   these.
3. **Platform markers.** `torch==2.14.0+cpu ; sys_platform == "win32"` and the
   CUDA line for Linux. Without this, one lockfile is not expressible.
4. **A resolution environment per platform.** `pip-compile`-style tools resolve
   for one platform at a time; a single cross-platform lock needs the
   `--python-platform` / multi-hash form, or two lockfiles (one per platform)
   that both satisfy the shared `contract` block.

**Realistic deliverable:** not one file, but **one contract block + two platform
lockfiles**, with `check_runtime_baseline.py` enforcing the contract block on all
six environments and failing CI on any skew.

---

## 5. Enforcement

```bash
# rebuild after any deliberate version change
python azazael/scripts/build_runtime_baseline.py

# verify all six environments (live probe; exits 1 on any contract violation)
python azazael/scripts/check_runtime_baseline.py
python azazael/scripts/check_runtime_baseline.py --json reports/env_inventory/baseline_check.json
python azazael/scripts/check_runtime_baseline.py --envs win-314t,ubuntu
python azazael/scripts/check_runtime_baseline.py --strict        # supporting drift fails too

# offline / no-WSL mode, using saved captures
python azazael/scripts/check_runtime_baseline.py --from-captures
```

Exit codes: `0` clean · `1` contract violation · `2` an environment was
unreachable (result incomplete — a stopped WSL distro must not read as "clean").

The exit code is the point. `benchmark_evolution.py` check [7] sat red for three
days because nothing ran it; this check should be wired into the same scheduled
run as the drift alarm so that "the estate diverged" is a signal rather than a
discovery.

---

## 6. Dependencies on other findings

| Relationship | Detail |
|---|---|
| Enables | The drift alarm (`scripts/env_drift_alarm.py`) invokes this checker as one of its signals. |
| Depends on | The I1 fix (adaptation stack on 3.14t) is already reflected — `win-314t` moved 161 → 178 dists during this session. |
| Blocked by | Ubuntu's CUDA extras: aligning Ubuntu pulls ~25 `nvidia-*` wheels (~5 GB). Decide whether the accelerator role needs them before committing the baseline. |
| Constrained by | C: free fluctuates 25–36 GB. A full six-environment realignment downloads several GB. The model-store relocation that would have freed 78 GB (Ollama → D:, LM Studio → G:) was **planned and declined on 2026-09-20** — C: stays near-full by decision, recorded as an accepted condition in the drift alarm. Realigning the baseline therefore needs either a narrower scope (contract packages only, ~35 wheels) or revisiting that decision. |
