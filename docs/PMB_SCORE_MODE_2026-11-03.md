# PMB recall scoring — cosine-dominant mode, measured 2026-11-03

**Question asked:** make `raw_cosine` dominate the PMB recall score so
importance/recency only break ties, then re-run `floor_measure` and see whether a
real separation gap appears.

**Answer:** implemented and exercised; **no gap appears**, and the class that
matters most for a floor (plausible-but-absent questions) scores *higher* than
genuine ones. Cosine dominance is therefore **not enabled by default** — the
daemon runs the hybrid composition, which is what the 0.89 / 0.70 floors were
calibrated against.

## What changed, and where

The scoring path lives in the installed package, which is **not under version
control** (`pmb_ai` 1.2.3, no `direct_url.json`, not an editable install):

- file: `C:/Users/clint/.pmb-venv/Lib/site-packages/pmb/core/engine/recall.py`
- pristine copy kept beside it: `recall.py.orig-2026-11-03`
  (sha256 `6ffa149a2c2dd1fda314ed55168bbdf8fe9facd6a4e53a5812ff5a45cd43c7ce`)
- one composition point changed, inside `_recall_impl`, immediately before
  `scored.append((h, ev, base, recency))`:

```python
if _SCORE_MODE == "cosine":
    # raw cosine carries the score; importance/recency only break ties
    base = max(0.0, float(getattr(h, "raw_vec", 0.0) or 0.0))
    base += _COSINE_TIE * (0.5 * float(ev.importance or 0.0) + 0.5 * float(recency))
```

`_COSINE_TIE` is `1e-3` (`PMB_SCORE_TIE`), i.e. importance+recency can move a row
by at most 0.001 — enough to order rows that are effectively tied on similarity,
not enough to lift a dissimilar row over a similar one. `PMB_SCORE_MODE=cosine`
selects the mode; the default is `hybrid`.

Gating it is deliberate, not timidity: `raw_cosine` is `1/(1+L2dist)` and on this
corpus it lands in **0.03–0.11** for everything, while the floor constants live on
the hybrid scale (scores ~1.0–1.6). Enabling cosine with the old floors makes
`pmb_floor_proxy` reject **every** row, because no score can reach 0.89 or 0.70.

## Measurement

`python tools/floor_measure.py --noise 20 --adjacent 8 --real 12`

| composition | noise (n=20) | adjacent (n=8) | real (n=12) | gap (real min − noise max) | exit |
| --- | --- | --- | --- | --- | --- |
| hybrid (baseline) | 1.415 max | 1.575 max | **1.054 min** | **−0.521** | 1 |
| cosine-dominant | 0.030 / 0.046 / 0.060 (min/mean/max) | 0.055 / 0.077 / **0.109** | 0.052 / 0.069 / **0.087** | **−0.057** | 1 |

Both runs: `query floor 0.89 inside the gap: NO`, `row floor 0.70 inside the gap: NO`.

**Reading the cosine column.** The overlap is far tighter in relative terms
(−0.008 absolute inside a ~0.06 band, vs −0.36 inside a ~0.5 band), so the
composition change did move in the intended direction: importance and recency no
longer manufacture relevance. But it does **not** produce a positive gap, for two
measured reasons:

1. **A random nonce is not a stranger to the vector space.** Nonces such as
   `zzqc5e138bf2f24` score up to 0.060, above the weakest real probe (0.052).
   `1/(1+dist)` puts an absolute floor under nonsense; no threshold on it can
   separate the classes.
2. **Adjacent near-misses beat real questions.** The top adjacent probe
   ("how does the anti-pattern ratchet sign its baselines with ed25519", 0.109)
   scores above the best real probe (0.087). A floor set to admit real queries
   necessarily admits these; a floor set to exclude them rejects real ones.

So the defect the change was meant to fix (importance/recency amplification) is
real and is fixed by `PMB_SCORE_MODE=cosine`, but it was not what makes the floor
unmeasurable. The binding blocker is that `raw_cosine` is a compressed,
uncalibrated transform of distance rather than a similarity on a comparable
scale.

## Enable / revert

```bash
# enable (per daemon process; the spawned child inherits it)
PMB_SCORE_MODE=cosine C:/Users/clint/.pmb-venv/Scripts/pmb.exe daemon restart

# revert to the default composition
C:/Users/clint/.pmb-venv/Scripts/pmb.exe daemon restart

# revert the source entirely
cd C:/Users/clint/.pmb-venv/Lib/site-packages/pmb/core/engine
cp -p recall.py.orig-2026-11-03 recall.py
```

Verified after the last restart: daemon score back to 1.484 on a real query, and
`recall` through the floor proxy (`:8766`) returns 5 rows.

Note on the switch: the first `PMB_SCORE_MODE=cosine ... daemon restart` did not
take effect — the daemon kept the hybrid composition until a second restart.
`restart` calls `start()` in-process with `env=dict(os.environ)`, and the second
restart bound the env as expected; the cause of the first miss was not
established, so it is recorded here as an observation rather than explained.

## Expiry

The numbers above are readings of one corpus on 2026-11-03. Re-measure with the
same command before quoting them; `raw_cosine`'s band depends on how the vectors
are stored and on the model, so it moves with a re-index.
