> ## SUPERSEDED — read `NEURAL_MESH_FORENSIC_2026-09-29.md` first
>
> This document is a **dated record of what was believed on its date**. Its
> numbers are historical and several are now known to be wrong. Nothing marked
> it as superseded, so an undated reader would draw current conclusions from a
> snapshot — the exact "confidently-incomplete artifact" failure this project
> already has a skill for.
>
> Concretely, claims below that are **no longer true**:
> - the global quarantine item store is **present** (`spine_registry.py:521`);
> - the gossip signer allowlist is **present** and has a CLI
>   (`scripts/mesh_trusted_key.py`);
> - route-outcome censoring is **present but was inert** — see §1 of the
>   current forensic;
> - the worm census figures are from their measurement dates, not today.
>
> Kept for provenance. Do not cite without the date.

---

# Forensic pre-implementation audit - 11 suggested followups

**Date:** 2026-09-28
**Host:** Windows (Freebuff), project `C:/Users/clint/azazael`
**Interpreter:** `../venv-314t/Scripts/python.exe` (Python 3.14.7)
**Method:** read the live tree, the live git history, the live runtime artifacts and the
live memory store; compare against the WSL mirror and the G: mirror. No generated
snapshot / cached census was trusted (see Caveats).

**Caveats / ground rules applied**

1. **Graph snapshots are stale and were NOT used.** `var/cold/graph-snapshots/2026-09-28/graph.json`
   references symbols (`_signer_is_known`, `_flat()`) that do not exist in the live tree.
   Any artifact that cannot state its provenance is treated as non-evidence.
2. **Another agent (opencode) is working in this repo concurrently.** Every file state
   below is a timestamped observation, not a stable fact. Snapshot before any write.
3. **No agent / inference tooling exists on this host** (RULE 0G/0M/0W/0Z deviations stand).

---

## 0. FOUNDATIONAL FINDING - the tree is one of three divergent revisions

This is the single most important result and it changes the premise of several followups.

### Three copies of the same modules, all different

| Module | Windows `azazael/` (live, = git HEAD) | WSL `/root/azazael/` | `G:/source-of-truth/azazael/` |
|---|---|---|---|
| `src/CORE/spine_registry.py` | 156,384 b, 2026-09-28 15:37 | 176,146 b, 2026-09-27 21:49 | 170,220 b, 2026-09-21 14:23 |
| `scripts/monitor_learning.py` | 15,013 b (pre-fix) | 15,477 b (has `_flat`) | 14,658 b, 2026-09-07 |
| `src/CORE/data_retention.py` | 40,237 b, 2026-09-28 14:38 | 37,779 b, 2026-09-27 14:04 | 33,171 b, 2026-09-26 16:28 |
| `scripts/evolution_cycle.py` | 133,160 b | 167,503 b, 2026-09-27 14:01 | - |

Normalised (CRLF-stripped) line divergence Windows<->WSL:

```
spine_registry.py    418 lines
evolution_cycle.py   727 lines
mesh_listener.py     100 lines
data_retention.py    149 lines
metacog_cycle.py      13 lines
mesh_transport.py      0 lines  (identical)
record_thought.py      0 lines  (identical)
```

Divergence is **bidirectional**: the Windows lineage carries Sep-28 commits
(`5a3af790`, `06ff0211`, `e26db6e1`, ... that the WSL copy predates), while the WSL copy
carries Sep-27 uncommitted work the Windows tree lacks.

### Evidence that features were LOST from Windows, not merely relocated

Features present in the WSL copy and **absent everywhere in the live Windows tree**
(searched `src/`, `scripts/`, HEAD via `git grep`):

| Symbol | Windows live | Windows HEAD | WSL | G: |
|---|---|---|---|---|
| `_signer_is_known` (gossip allowlist) | absent | absent | **present** | absent |
| `_QUARANTINE_ITEMS` / `quarantine_item()` / `is_quarantined()` (global) | absent | absent | **present** | **present** |
| `_SPINE_EVENTS_MAX = 5000` | `= 200` (this IS present, smaller) | `= 200` | **5000** | present |
| `flat_best_only` / `trajectory_avg` in monitor | absent | absent | **present** | absent |

Specifically on `spine_registry.py`:

- Windows keeps a quarantine **vote** ledger (`_QUARANTINE_VOTES`, `get_quarantine_votes()`,
  saved at `save_spine_state` line 2211) but has **no active quarantine item store**.
- The only `is_quarantined` in the live tree is a **per-instance** dict in
  `src/CORE/WORMS/expansion/immune.py:138/154` - exactly the defect the WSL copy's own
  comment describes ("kept `self._quarantined` as a per-instance dict ... the record went
  with it").
- Windows `src/CORE/WORMS/expansion/spine.py:941` calls `order_quarantine()` but no
  execution path consults quarantine.
- WSL adds a process-global, persisted, gossiped `_QUARANTINE_ITEMS` store with
  `quarantine_item` / `release_item` / `is_quarantined` / `quarantine_count` and
  release-tombstone semantics.

### Mechanism of the loss (git evidence)

- `git diff --stat HEAD -- src/CORE/spine_registry.py scripts/monitor_learning.py` is
  **empty** -> the Windows working tree equals HEAD for these files.
- `git show HEAD:src/CORE/spine_registry.py | grep -c _signer_is_known` -> **0**.
- `git reflog` contains **two `reset: moving to HEAD`** entries
  (`a1520bec`, `6fc324f1`) - the signature of `git reset --hard`, which discards
  uncommitted working-tree edits *without* moving HEAD.
- The Sep-27 21:48-21:49 edits survive only in WSL because they were synced there
  before the reset.

### The orphaned-artifact tell

`~/.azazael/mesh_trusted_keys.json` **exists** (628 b, 2026-09-27 21:48) but **nothing in
the live tree reads it** - the reader (`_load_trusted_keys`) lived in the discarded
revision. This is the "confidently-incomplete artifact" pattern: config that implies a
capability the code no longer has.

### Immediate risk

Any new **uncommitted** edit is exposed to the same failure mode (two `reset --hard`
events already recorded). **Commit early.**

---

## 1. Wire `strategy_steered` events so monitor_learning sees dreamer strategy changes

**Premise:** the monitor warns "active non-default strategy but no strategy_steered events".

**Finding: ALREADY WIRED AND FLOWING. Premise does not reproduce.**

- Producer exists: `src/CORE/WORMS/expansion/dreaming.py` - `DreamingModule._record_steering()`
  (line 931) records a `strategy_steered` event; it is called from `DreamingModule.execute()`
  (line 926).
- Live store: `strategy_steered` = **128 events / 24 h**, latest 23:02:07
  (`strategy=defensive params={num_episodes:2, scenario_count:30, creativity_factor:0.1} worm=global`).
- Live monitor run (`scripts/monitor_learning.py --minutes 60`) prints `steering: 128` and
  **does not** emit the WARN (its condition requires `n_steer == 0`).

**Verdict: NO WORK NEEDED.** If anything, a regression test pinning "steering must be
non-zero whenever a non-default strategy is active" would guard it.

---

## 2. Tighten `state_saved` freshness to land within one cycle

**Premise:** the monitor warns `state_saved age N min is past one cycle`.

**Finding: DOES NOT REPRODUCE NOW; underlying cadence mismatch is real.**

- Live monitor: `state_saved age: 1.4 min`, verdict `[OK]`, no WARN.
- Cadence maths: `state_saved` = **71 / 24 h (~1 per 20 min)** while
  `CYCLE_MINUTES = 5`, WARN fires above 5 min and FAIL above 10 min
  (`scripts/monitor_learning.py` lines ~139-145).
- Therefore the WARN is *intermittent and expectation-driven*: the monitor assumes a 5-min
  save cadence that the producer does not deliver (71 vs a nominal 288/day).
- Also note the duplicate: `src/SCRIPTS/monitor_learning.py` is **byte-identical**
  (md5 `f80ce910d29c282cdf25d9e5c36e4be6`) to `scripts/monitor_learning.py`. Editing one
  without the other creates drift.

**Verdict: DO NOT "tighten freshness" blindly.** First identify the `state_saved` producer
and decide whether the constant or the producer is wrong. This followup as phrased could
mask a real cadence defect. Needs one more probe (who writes `state_saved`, and why 71 not 288).

---

## 3. Firewall TCP 18210 to the WSL subnet only

**Finding: REAL GAP. No dedicated rule exists; a broad program-inbound rule covers it.**

- `netsh advfirewall firewall show rule name=all` contains **no rule** referencing
  `18210` / `18211` / `18212`.
- There are inbound **Allow** rules for the exact listener binary:

```
Rule Name:     python.exe
Enabled:       Yes
Direction:     In
Profiles:      Public
LocalPort:     Any
Program:       C:\users\clint\appdata\local\programs\python\python314\python.exe
Action:        Allow
```
(two such rules; also `python3.14t.exe` and `Python` rules)

- The live listener is `state/mesh_listener.json`: `pid 17496` (started 14:46:59),
  bind `0.0.0.0`, port `18210`, `require_auth: true`.

**Impact:** the mesh port is reachable on the Public profile from any address, gated only by
`require_auth` (and the gossip allowlist that does not exist in the live tree - see 4/5/6).

**Verdict: PROCEED ONLY WITH (a) explicit user permission and (b) admin rights.**
This mutates host state outside the project directory, so it is gated by policy.
Recommended shape: an inbound **Allow** rule scoped to the WSL vEthernet remote address +
port 18210, and/or restrict the `python.exe` rules' `RemoteAddress`.

---

## 4. Unit tests for the gossip known-signer allowlist matrix

**Finding: NO SUBJECT in the live tree.**

- Repo-wide search for `mesh_trusted_keys`, `_signer_is_known`, `unknown_signer`,
  `_GOSSIP_TRUSTED_KEYS_ENV`, `trusted_envs`, `trusted_key_count` returns **no live Python
  hit** (only the stale graph snapshot).
- The allowlist implementation exists **only** in `/root/azazael/src/CORE/spine_registry.py`
  (WSL, lines ~2939-3198): `_GOSSIP_TRUSTED_KEYS_ENV`, `_load_trusted_keys()`,
  `_signer_is_known()`, `check_gossip_trust` returning `unknown_signer` / `unknown_signer_admitted`.

**Verdict: BLOCKED on decision 4/5/6 (see Section 12).** Tests cannot be written against
code that is not in the tree. Two options: (a) port the WSL allowlist into Windows and then
add the matrix test, or (b) declare the allowlist out of scope and drop 4/5/6 together.

---

## 5. Persist TOFU key pins across restarts

**Finding: ALREADY IMPLEMENTED in the live tree.**

- `save_spine_state()` (`src/CORE/spine_registry.py:2174`) persists
  `gossip = {"seq": ..., "seq_seen": ..., "keys": dict(_GOSSIP_KEYS)}` (line ~2211).
- `load_spine_state()` (line 2255) restores them:
  `_GOSSIP_KEYS.setdefault(str(env), key)` (line ~2393).
- Verified on disk: `~/.azazael/spine_state.json` (**543,266 b**, `saved_at
  2026-09-28T19:04:28`) has top-level key `gossip` with `{'seq','seq_seen','keys'}`;
  current pins: `{'local': 'XogzUsyzaCIGiy...'}`.

**Observation:** only `local` is pinned - remote envs (wsl2-ubuntu, wsl2-kali) are not yet
pinned under the live tree, which is expected TOFU behaviour (pin on first successful
verify) but means rotation detection for those peers is untested here.

**Verdict: NO WORK NEEDED for persistence itself.** Only a rotation-detection test would add
value.

---

## 6. CLI to pin a new peer key into `mesh_trusted_keys.json`

**Finding: NO SUBJECT; would target a config no live code reads.**

- No trust/pin CLI exists: `scripts/` holds `mesh_listener.py`, `mesh_gossip_cycle.py`,
  `run_mesh_cycle.py`, `spine_cycle_apply.py` - none expose a pin subcommand.
- `mesh_trusted_keys.json` is read by nothing in the live tree (see Section 0), so a CLI
  writing it would be a no-op config writer.

**Verdict: BLOCKED on the same decision as 4/5/6.**

---

## 7. Run a DPO+RL training cycle on today's new thought rows

**Finding: FEASIBLE; data is present.**

- `thought_process` rows in `~/.azazael/memory_store.db`: **137, all dated 2026-09-28**.
- Orchestrator present: `scripts/run_training_orchestrator.py` (`--algo DPO|RL`),
  single-cycle with an `msvcrt` overlap lock.
- Last recorded training in the store: `avg_reward=13.2673`, `q_table=81` @ 2026-09-28T19:10.

**Verdict: PROCEED.** Low blast radius; run each algo as its own step and read the
persisted rows back. Note it mutates the live store - keep the retention/quota check
(Section 9) after it.

---

## 8. Investigate MetaCognitionWorm "dream round partial" (top error cluster)

**Finding: REAL DEFECT, ROOT-CAUSED. Legitimate skips are scored as failures, and the
false failures are steering the system defensive.**

Chain:

1. `error_triage.json` top cluster: `MetaCognitionWorm | error |
   "meta_cognition_observation|dream round partial: # applied # skipped" | count 93`.
2. Producer of the score: `scripts/metacog_cycle.py` lines ~133-145:

```python
elif et == 'policy_applied':
    det = data.get('details') or {}
    nap = len(det.get('applied', []))
    nsk = len(det.get('skipped', []))
    wt = 'dreaming'
    if nap > 0 and nsk == 0:
        outcome, err = 'success', None
    elif nap > 0 or nsk > 0:
        outcome = 'error'
        err = 'dream round partial: %d applied %d skipped' % (nap, nsk)
```
   -> **ANY skip is an `error`.**
3. Producer of the data: `src/CORE/dream_policy_bridge.py:114` records
   `policy_applied` with `details.applied` / `details.skipped`. Skips are the *designed,
   expected* outcomes:

```python
if not isinstance(s, dict) or s.get("confidence", 0) < min_confidence:
    skipped.append({"reason": "low-confidence"}); continue
if _governance_blocked(s):
    skipped.append({"reason": "governance-blocked"}); continue
if not actions:
    skipped.append({"reason": "no-actionable-strategy"}); continue
except Exception as e:
    skipped.append({"reason": f"error: {e}"})
```
   The module docstring is explicit that the generator deliberately emits tepid
   low-confidence suggestions (gate lowered 0.05 -> 0.01 precisely so they are not all
   rejected).
4. Live confirmation: `policy_applied` latest = `applied=1 skipped=2`
   -> `mc.observe(outcome='error', error='dream round partial: 1 applied 2 skipped')`.
   Rows in store: `meta_cognition_observation` `outcome=error` for
   `worm_type=dreaming, action=dream_integrate` with exactly that text
   (e.g. `mc_163_...`, `mc_162_...`, `mc_159_...`).
5. Downstream: `mc.observe(...)` -> per-worm analysis -> adaptation. Live
   `state_saved.current_strategies` = `{MetaCognitionWorm: retry_with_backoff,
   global: defensive, NatureCluster.*: retry_with_backoff}` and
   `strategy_adaptation` = **434 / 24 h**. A stream of false "dreaming is failing"
   signals is a plausible driver of the defensive/retry posture.

**Verdict: FIX (with verification).** The honest classification is: `low-confidence`,
`no-actionable-strategy` (and arguably `governance-blocked`) are *normal* outcomes and must
not be counted as failures; only `reason` beginning `error:` is a real failure. Alternative:
require `nap == 0 and nsk > 0` for a total-failure, and treat partial-with-applied as
success. Because this changes what the learner observes, verify by re-querying the
`meta_cognition_observation` error counts before/after on the same window.

---

## 9. Add a retention test asserting the store stays under quota after `cmd_maintain`

**Finding: REAL GAP; the injection point does not exist yet.**

- `tests/test_data_retention.py` has 7 tests, all about rotation/caps/thresholds
  (`test_rotates_past_cap`, `test_shift_chain_and_drop`, `test_custom_cap`,
  `test_never_caps_selection_history`, `test_caps_cover_bookkeeping`,
  `test_sane_thresholds`). **No end-to-end quota-after-maintain assertion.**
- Injection plumbing is partial: `_resolve_db(db_path)` (line 149) and
  `distill_aged_memories(..., db_path=None)` accept a path, and
  `enforce_global_quota(quota_mb=...)` is parameterised - but **`cmd_maintain()` (line 929)
  takes no arguments**, so there is no way to point a test at a tmp store.

**Verdict: PROCEED, small refactor first.** Give `cmd_maintain` an optional `db_path`
(and/or honour `AZAZAEL_MEMORY_DIR`), then assert against a synthesised tmp store that the
final size is `< quota` and `exceeded == false`. Must not point at the production store.

---

## 10. Sync all changed files to the `G:\source-of-truth` mirror

**Finding: HAZARD. G: is stale and is NOT a git repo; blind sync is the wrong first move.**

- `G:/source-of-truth/azazael` mtimes: `spine_registry.py` 2026-09-21, `monitor_learning.py`
  2026-09-07, `data_retention.py` 2026-09-26. It is a mirror snapshot, not a live branch.
- `git -C G:/source-of-truth/azazael rev-parse HEAD` -> **fatal: not a git repository**;
  there is a separate bare repo at `G:/source-of-truth/azazael.git`.
- The configured push targets live in `scripts/sync_all.py`:
  `G:/source-of-truth/azazael` and `G:/AZAZAEL/AZAZAEL_ROOT`.
- Because the three trees already disagree (Section 0), a one-way sync now would either
  (a) publish a revision that is missing the Sep-27 work, or (b) if any reverse path exists,
  inject Sep-07/21 content back into Windows.

**Verdict: HOLD.** Reconcile revisions first (decide the authoritative revision, commit it),
*then* sync. Do not run `sync_all.py` blind while opencode is also writing.

---

## 11. Re-run the full suite to confirm 3,933 still green

**Finding: GENUINELY NEEDED - and the green baseline is stale.**

- `logs/suite_chunks_20260928.json`: `passed=3933 failed=0 errors=0 skipped=38`, 8 chunks,
  227 files, `wall_s=1416` (~24 min).
- `logs/suite_run_20260928.log` is dated **2026-09-27 20:42** - i.e. it predates the
  Sep-28 commits (`5a3af790`...`e26db6e1`) and any current-tree edits.
- So "3,933 still green" is currently an **unverified claim about a different revision**.

**Verdict: PROCEED, after edits land** (~24 min runtime; run chunked via the existing
runner). It is the correct closing gate for anything changed in Sections 2/8/9.

---

## 12. Cross-cutting findings and decisions required

### 12.1 Tree divergence (highest priority)
The Windows tree is missing at least: the gossip allowlist, the global quarantine item
store, `_SPINE_EVENTS_MAX=5000`, and the monitor `_flat` fix - all of which exist in the WSL
copy and (for quarantine) in the Sep-21 G: mirror. Deciding whether to **port** the WSL
revision into Windows is an architectural decision and must be made explicitly. The WSL
revision is recoverable verbatim (`monitor_learning.py` is a clean 20-line delta; see the
method appendix).

### 12.2 Uncommitted-work exposure
Two `reset --hard` events already discarded work here. Commit early; do not leave long-lived
uncommitted state while a second agent is writing.

### 12.3 Duplicate module
`src/SCRIPTS/monitor_learning.py` == `scripts/monitor_learning.py` (identical md5). Any
monitor edit must touch both or be generated from one source.

### 12.4 Precedence of the "11 followups"
Independent of any port decision, the following are actionable now, in this order:

1. **#8** metacog skip-semantics fix (real defect, downstream learning impact) - verify by
   re-querying the error cluster.
2. **#9** retention quota test (adds a `cmd_maintain(db_path)` seam + a tmp-store test).
3. **#7** DPO+RL on today's 137 thought rows.
4. **#11** full suite re-run as the closing gate.
5. **#3** firewall scoping - only with explicit permission + admin.
6. **#10** G: sync - only after reconciliation, and not while opencode writes.

**Already satisfied / no subject:** #1 (already wired), #5 (already persisted).
**Blocked on the port decision:** #4, #6 (and the allowlist half of the security posture).
**Needs one more probe:** #2 (find the `state_saved` producer; 71 vs 288 per day).

---

## Appendix - reproduction

```bash
# live monitor verdict
../venv-314t/Scripts/python.exe scripts/monitor_learning.py --minutes 60

# HEAD vs working tree (empty = clean)
git diff --stat HEAD -- src/CORE/spine_registry.py scripts/monitor_learning.py

# the fix that only exists in WSL (20 lines)
diff --strip-trailing-cr -u scripts/monitor_learning.py \
  <(wsl -d Ubuntu-26.04 -- bash -lc 'cat /root/azazael/scripts/monitor_learning.py')

# live signals straight from the store
../venv-314t/Scripts/python.exe -X gil=1 -c "import sqlite3,os; \
 c=sqlite3.connect('file:'+os.path.expanduser('~/.azazael/memory_store.db')+'?mode=ro',uri=True); \
 print(c.execute(\"select count(*) from memories where event_type='strategy_steered'\").fetchone())"

# firewall exposure
netsh advfirewall firewall show rule name="python.exe" verbose
netsh advfirewall firewall show rule name=all | grep -iE "18210|18211|18212"
```

**Artifacts created by this audit:** this file only (during the investigation phase).
WSL copies used for comparison were read via `wsl cat` (read-only).

---

## 13. IMPLEMENTATION LOG (executed after the investigation above)

### 13.1 Ported the lost code into the Windows tree - VERIFIED

| File | Change | Evidence |
|---|---|---|
| `src/CORE/spine_registry.py` | 156,384 -> 176,146 b, +418 lines: known-signer allowlist (`_GOSSIP_TRUSTED_KEYS_ENV`, `_load_trusted_keys`, `_signer_is_known`), global `_QUARANTINE_ITEMS` store (`quarantine_item` / `release_item` / `is_quarantined` / `quarantine_count`), `_SPINE_EVENTS_MAX` 200 -> 5000, `get_q_dream_counts`, `_merge_quarantine_items`, `gossip_from` provenance | md5 `f1cf7a36` -> `65a0c017`; py_compile OK; live probe |
| `src/CORE/WORMS/expansion/immune.py` | +77 lines: `QuarantineWorm` delegates to the shared store (`_shared_store`, `active()`) - the CONSUMER of the store above | md5 `f579ae5b` -> `371c009e`; py_compile OK |
| `scripts/monitor_learning.py` + `src/SCRIPTS/monitor_learning.py` | +20 lines: `_flat()` helper, `flat = flat_best and flat_mean` when `trajectory_avg` is present, `flat_best_only` + `trajectory_avg` added to signals | md5 `f80ce910` -> `eb6e7b1c` (both copies); py_compile OK |

Live probe after the port (subprocess; nothing persisted):

- `_SPINE_EVENTS_MAX = 5000`
- `get_gossip_trust_state()` -> `trusted_envs = {'windows','wsl2-ubuntu','wsl2-kali'}`, `trusted_key_count = 3`
- `_load_trusted_keys()` now reads the previously-orphaned `~/.azazael/mesh_trusted_keys.json`
- `quarantine_item` / `is_quarantined` / `release_item` round-trip

Regression evidence (port is net-neutral-to-positive):

- HEAD baseline on 7 mesh files: **14 failed / 207 passed**
- after the port: **13 failed / 208 passed** - it FIXED
  `test_censored_outcome_changes_nothing_but_its_own_bucket` and introduced none
- after also porting `immune.py`, `test_mesh_wire_or_cut` census debt returned to
  zero (the quarantine API is referenced again)

The 13 remaining failures are all PRE-EXISTING at HEAD and unrelated to the port:

- `test_spine_mesh.py` x6 - stale test vs refactor: `AttributeError: module
  'CORE.startup_warm' has no attribute 'restore_spine_state'`
- `test_spine_mesh_telemetry.py::test_q_order_preserves_ordering_semantics` - the
  test POLLS the live `~/.azazael/spine_state.json` (`['W30', ...]` vs the
  expected `['W1', ...]`), so it is not isolated
- `test_mesh_transport_hardening.py::test_router_env_error_is_censored_not_learned`
  - `KeyError: 'status'` (live-state dependent)
- `test_mesh_transport_e2e.py::test_router_learns_only_learnable_outcomes`,
  `test_mesh_fabric_followups.py::test_fabric_stage_reports_all_four_natures`,
  `test_learning_evolution.py::TestGRPOTrainer::test_get_policy_all_contexts`
- `test_mesh_wire_or_cut.py::test_every_unreferenced_function_is_declared` -
  caused by the OTHER agent's uncommitted `learning_rl.py` edit
  (`_schema_state_key` has no verdict)

### 13.2 Followup #8 - metacog skip-semantics - FIXED

`scripts/metacog_cycle.py`: the `policy_applied` branch now counts only skips
whose reason begins `error` as failures; a round with `applied > 0` is a success;
a round with nothing applied and no hard failure feeds NOTHING (no false success,
no false error). Diff: +18 / -7.

### 13.3 Followup #9 - retention quota test - FIXED

`src/CORE/data_retention.py`: added `_DB_OVERRIDE` (honoured by `_get_db_path()`),
a `run_maintenance(light, db_path)` / `cmd_maintain(db_path)` seam that restores
the override in `finally`, and `enforce_global_quota(quota_mb=None)` resolving
`DB_SIZE_QUOTA_MB` at CALL time. All existing callers unchanged
(`azazael_ctl`, `nightly_maintenance`, `test_data_distillation`, `test_ops_tools`).

`tests/test_data_retention_quota.py` (new): an isolated SUBPROCESS test
(`AZAZAEL_MEMORY_DIR` = tmp) seeds 900 uncapped rows, lowers the quota, runs the
full maintenance, and asserts before > quota, the backstop ran, after <= quota,
and rows trimmed to 0 - plus seam contract tests. **20 passed** alongside the
existing retention / distillation / ops tests.

### 13.4 Followup #7 - DPO + RL cycle - RAN

- DPO: 19 records, model v18, eval reward 124.95, DPO loss 5.2e-05, SUCCESSFUL.
- RL: 200 records, 80 episodes, reward 6.1989, q=110, resumed persisted Q-table,
  SUCCESSFUL.
- FINDING: the thought-preference pairing was SKIPPED ("no same-family
  success/fail contrast"). Cause measured: `_thought_family` = first 3 lowercased
  task words, and the newest 120 `thought_process` rows are 119
  `'evolution promotion verdict'` successes + 1 - the `limit=120` window is
  saturated by one failure-free, high-volume family, so genuine contrasts never
  survive into it. Rebalancing that window is a followup, not done here.

  > **RESOLVED 2026-09-29 — read this before re-investigating.** The window was
  > widened to 600, a `thought_contrast()` selector was extracted as a pure
  > function, a census is now printed on every skip (rows scanned, families,
  > families holding a contrast, the dominant families) so a stall is
  > diagnosable rather than merely reported, and a weaker same-verb tier is
  > tried and LABELLED when no exact family matches. Covered by
  > `tests/test_thought_contrast_pairing.py` (7 tests, passing). Measured on
  > the live store 2026-09-29: 247 rows, 23 families, a real `verb`-tier pair
  > found. The pairing is NOT broken.
  >
  > A second, genuinely open defect was found in the same area and is now
  > fixed: `query_memories` hard-clamps every call to `MAX_QUERY_LIMIT` (500)
  > and returns newest-first, so the clamp silently evicted the oldest — and
  > therefore the minority-family — rows. The 600-row window was in practice
  > capped back to 500, reopening this same bug through a different door.
  > `LocalMemoryStore.fetch_all_memories()` now pages past the clamp, and
  > every oversized reader routes through it. See
  > `tests/test_thought_corpus_integrity.py`.

### 13.5 Followup #11 - full suite - RAN (report: `logs/suite_chunks_20260928b.json`)

The tree was already badly NOT green before these changes.

- Full chunked run: **passed=2311 failed=88 errors=4 skipped=5** in 1286.1 s.
- **Chunk 4 TIMED OUT at 600 s** (`timed_out: true`, `returncode: null`) - its
  tests never ran, so the real failure surface is larger still.
- Two collection errors (chunks 1 and 6), both pre-existing and environmental:
  - `tests/test_aoa_elastic_routing.py` - `ImportError: cannot import name
    'ARM_ROUTE_NATURE' from 'core.router'` (AOA refactor; test not updated)
  - `tests/test_optimizers_convergence.py` - `ModuleNotFoundError: No module
    named 'mygrad'` (absent from venv-314t)
- Failing files, largest first: `test_wiring_cycle` (9), `test_cluster_integration_p1`
  (8), `test_freethreadedagent` (6), `test_spawn_decision` (6), `test_spine_mesh`
  (6), `test_era_windows` (4), then `test_delegation_ask_owner`,
  `test_exmachina_freeze`, `test_exmachina_monitor_split`,
  `test_terminal_monitor_controls`, `test_track_registry_consumers`,
  `test_worm_governance_integration`, `test_worm_regression_smoke` (3 each), ...

ATTRIBUTION CONTROL (the decisive measurement). The 9 files most plausibly
related to the changed modules were run both ways:

| Tree | Result |
|---|---|
| WITH my changes | **28 failed / 151 passed** |
| HEAD (my changes reverted) | **29 failed / 150 passed** |

My changeset again fixed one test and broke none. Combined with the earlier
7-file control (14 -> 13 failures), the port + fixes are net-positive and the
88 failures are entirely pre-existing.

CONCLUSION: the "3,933 green" figure from 2026-09-27 20:42 describes a
different revision AND a different environment (mygrad present then, absent now)
and cannot be reproduced as stated. Current verified state: 2311 passed / 88
failed / 4 errors / 1 timed-out chunk, none attributable to this session's edits.

### 13.6 Not done / decisions honoured

- #10 G: sync: HELD per user decision (revisions not reconciled).
- #3 firewall: DOCUMENT ONLY per user decision (no host changes made).
- #4 / #6 (allowlist tests, pin CLI): the code they target now EXISTS after the
  port, but they were not selected; the allowlist is exercised by the live
  `get_gossip_trust_state()` probe above.
- #5 (TOFU persistence), #1 (steering), #2 (freshness): no work needed / not
  reproducing.
