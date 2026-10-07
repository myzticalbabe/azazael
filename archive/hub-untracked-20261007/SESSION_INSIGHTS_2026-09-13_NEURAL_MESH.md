# Session Insights — Neural Mesh Audit Closure + Self-Improving Spine

**Date:** September 13, 2026
**Agent:** Buffy (Codebuff) on z-ai/glm-5.3-flash
**Scope:** Neural mesh audit → gap closure → architectural leaps (A/B/C) → full verification

---

## 1. What Was Audited and Found

Baseline: 182 registered worms across 27 categories, including the 8 mesh-fabric
natures (mesh, synapse, consensus, engram, federated, servemesh, immune,
xenomorph) living in `CORE/WORMS/expansion/`.

Confirmed architectural gaps (all closed this session unless noted):

| # | Gap | Fix |
|---|-----|-----|
| G1 | `discover_worms()` flat-scanned `WORMS/`; the 32 expansion worms registered only via the deprecated `ECOSYSTEM_EXPANSION.py` shim re-export chain | Recursive `os.walk` into package subdirs (`__init__.py`-gated), package-qualified imports (`CORE.WORMS.expansion.mesh`) with bare-name fallback |
| G2 | `_guess_category()`/`_guess_cooldown()` blind to the 8 mesh natures | Mesh-aware heuristic rules, checked before the legacy table |
| G3 | Mesh could not map itself; no live topology publisher | `SpineMapperWorm` → `CORE.spine_registry` shared map |
| G4 | Zero feedback loop: `record_outcome()` existed, nothing consumed or drove cooldowns/Q | `HomeostatWorm` + ledger written by `NatureCluster.execute()` |
| G5 | No tests for the spine layer | `tests/test_spine_mesh.py` — 28 tests, all passing |

---

## 2. Root Causes Found During Verification (the real gold)

The reported failure — `TestMetaClusterDiscovery::test_metacluster_has_ncm`
seeing "16 natures / 141 worms" in batch but passing in isolation — was NOT
test-ordering pollution. Instrumented tracing (a throwaway pytest plugin
patching `reset_registry`/`repair_registry`/`discover_worms` with caller
capture) exposed two genuine product bugs under Python 3.14t free-threading:

1. **Unsynchronized concurrent discovery.** `discover_worms()` ran its import
   loop without holding `_registry_lock`. Background discovery (startup_warm /
   doctor paths) racing an in-flight pass produced *partial* registries
   (top-level only, 142/17) or *double-registered* ones (199).
   **Fix:** `discover_worms()` is now a thin RLock-guarded wrapper around
   `_discover_worms_impl()`; racers queue, latecomers see `_discovery_done`
   and return 0. Reentrant lock ⇒ no deadlock with `register_worm()`.

2. **Torn cache writes.** `save_cache()` wrote `worm_registry_cache.pkl`
   non-atomically; a concurrent reader (or crash mid-write) observed an EMPTY
   file → `pickle` `EOFError` → every reader forced into the 38–45s cold
   rebuild. **Fix:** tmp-file + `os.replace()` atomic write with non-atomic
   fallback (AV-lock edge on Windows). Corrupt empty cache file deleted.

3. **Unfaithful repair path.** `repair_registry()` cleared the registry and
   re-ran discovery *without purging* worm modules from `sys.modules`, so
   `@register_worm` decorators could not re-fire and the rebuild fell through
   to the dir()-fallback with heuristic metadata (fewer natures, wrong
   categories, expansion/ dropped). **Fix:** shared `_purge_worm_modules()`
   used by both `reset_registry()` and `repair_registry()`.

Verification tail: registry now deterministically **184 worms / 27 categories**
(cold rebuild), idempotent on re-discovery. *(2026-09-14: re-verified 184; was 183 on 09-13 — +1 mesh worm; MorphingWorm description backfilled.)*

---

## 3. Architectural Leaps Implemented

### LEAP A — Q-weight brainstem (`CORE.spine_registry`)
- `_Q_WEIGHTS` table keyed `nature:worm`; **every** `record_outcome()`
  auto-reinforces via EMA: `q += α(reward − q)`, α=0.2, clamped [−1, +1].
  Success ≈ +1, failure ≈ −1. This is the always-on reflex; it requires no
  worm to fire.
- `q_order(nature, names)` ranks healthy → cold(stable) → failing.
- `NatureCluster.execute()` now orders execution by (−Q, −priority): healthy
  worms run first, failing ones are demoted; cold worms keep priority order
  (stable sort). Fails open to priority-only if the ledger is unavailable.

### LEAP B — Restart-safe, gossip-ready persistence
- `save_spine_state()` / `load_spine_state()` round-trip spine map + events +
  homeostat ledger + Q-weights to `~/.azazael/spine_state.json`
  (atomic write; corrupt/missing file = clean no-op).
- Load merges (`setdefault`) rather than clobbers, so live state wins.
- SpineCycleWorm persists at the end of every cycle → the mesh remembers
  itself across restarts, and the JSON payload is the gossip unit.

### LEAP C — `SpineCycleWorm` (the one-entry self-improvement cycle)
- One call runs: **map → homeostat(Q+proposals) → red queen(probes, stand-down
  aware) → persist** — each stage isolated, failures reported, never raises.
- Safety rails:
  - Registered `orchestration` (not in `RedQueenWorm.PROBE_NATURES`) so the
    queen can never probe/recurse into a running cycle.
  - Non-reentrant (`busy` lock, skip-not-block) + min-interval throttle.
  - Homeostat `apply=True` remains explicit; the cycle defaults to
    propose-only for deterministic fleet behavior.

---

## 4. Verification Results

| Check | Result |
|-------|--------|
| `tests/test_spine_mesh.py` (28 tests incl. LEAPs + regressions) | ✅ 28/28 |
| Poison batch `test_spine_mesh + test_worm_registry + test_cross_nature_orchestration` | ✅ 85/85 (was: 1 failed) |
| Cold rebuild count / idempotency | ✅ 183/27, second pass returns 0 |
| Live `SpineCycleWorm().run_cycle()` | ✅ map 183 nodes, 70 nature edges, queen_interim, persisted |
| Pre-existing `test_metacluster` failure (with changes stashed) | reproduced → root-caused → fixed |

---

## 5. Thoughts for Training

1. **Instrument before theorizing.** The batch failure survived five
   hypotheses (cache staleness, test pollution, shim breakage, dotted-name
   collision, doctor path). The 20-line tracing plugin found it in one run.
   Cheap, throwaway instrumentation beats speculative fixes — keep this as a
   standard tool for "passes alone, fails in batch" reports.

2. **Free-threading changes the audit checklist.** Any function that mutates
   process-global state must be checked for (a) lock coverage of the *whole*
   read-modify-write window, not just the dict writes, and (b) torn
   file artifacts. Both bugs were invisible single-threaded. `RLock`
   reentrancy is the correct primitive here (discovery calls register which
   takes the same lock).

3. **"Fix the source, not the symptom" paid off twice.** The teardown
   re-discovery I added to the test file was a symptom patch; the real fixes
   (lock + purge + atomic write) made the ordering problem structurally
   impossible rather than merely tolerated. Result: no per-test sleeps, no
   fixture ordering constraints, no flaky retries.

4. **Feedback loops need both a reflex and a deliberator.** The brainstem
   (auto-Q on every outcome, sub-microsecond) and the deliberator
   (HomeostatWorm batch proposals, bounded, apply-explicit) serve different
   timescales. Collapsing them into one mechanism would either make the
   reflex too slow or the deliberation too twitchy.

5. **Self-improving systems need structural self-protection.** SpineCycleWorm
   is safe from Red-Queen recursion by *category algebra* (orchestration ∉
   PROBE_NATURES), not by runtime checks that can be forgotten. Prefer making
   unsafe interactions unrepresentable over guarding them at runtime.

6. **Observation:** the registry's own `source_file`-based skip
   (`registered_files`) means a same-named worm in two subdirs would
   silently skip the second. Not a bug today (names are unique), but a
   latent constraint worth a guard if the mesh keeps growing.

---

## 6. Open Threads (next session candidates)

- Wire `load_spine_state()` into session startup (startup_warm) so learned
  Q-weights restore automatically.
- Gossip merge: EnvBeacon + `spine_state.json` diffing across envs
  (windows/wsl2/bare) — payload format is already gossip-ready.
- Quarantine currently requires cross-env quorum by design; consider an
  explicit operator override channel for single-env failures.
- `SpineMapperWorm` route edges are nature-graph edges; per-worm route
  usage (which edge actually fired) is still unfilled telemetry.
