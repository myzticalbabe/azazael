# Engram #793 — batch06 SOTA census recount (worker A)

> **Model ID**: DeepSeek V4.1 Flash Fast. **Repo root** (`git rev-parse --show-toplevel`): `C:/Azazael/azazael`, branch `migration/baseline-20261001`. Coordinator-supplied at commit time.

Docs-only lane. Sources read: `state/sota_batches/batch06/technique_codebase_map.json`
(the per-row census), `.../absent_disposition.json` (the 2026-10-11 absence swarm),
`.../techniques_manifest.json`, `.../technique_index.json`, and the live tree.

## Headline: the recorded totals are stale by one row

The census is recorded as **15 ABSENT / 124 PARTIAL / 2 PRESENT**. That is what
`technique_codebase_map.json`'s own `totals` header says (lines 2-6) and what the
brief inherited. **It disagrees with the file's own 141 rows.**

Counted from the rows themselves rather than from the header:

| bucket | recorded | **counted from the rows** | delta |
|---|---|---|---|
| ABSENT | 15 | **14** | −1 |
| PARTIAL | 124 | **124** | 0 |
| PRESENT | 2 | **3** | +1 |
| **total** | 141 | **141** | 0 |

Mechanism (counted, not assumed): `"coverage": "ABSENT"` occurs at lines
14, 24, 44, 54, 74, 94, 262, 332, 432, 667, 795, 995, 1046, 1188 — **14**;
`"coverage": "PRESENT"` at lines 144, 845, 1421 — **3**; PARTIAL — **124**;
`"ep":` lines — **141**. The 14 ABSENT rows are exactly the 19 rows that were
ABSENT at start minus the 5 that moved out.

## Root cause: EP110's re-grade was never folded in

`absent_disposition.json` (2026-10-11) records 19 rows absent at start and 4 regrades
(EP183/EP206/EP237 → PARTIAL, EP252 → PRESENT), giving 15/124/2. But a **fifth** move
happened that is missing from that regrade list:

- **EP110** — `coverage` is `PRESENT` (map line 144) and carries its own
  `coordinator_reregrade` block ("Solar Pro 4 phase-2 adoption sweep, batch 3",
  2026-10-11, `from: ABSENT / NO-TARGET`, `to: PRESENT / ADOPTED`).
- That move is absent from `absent_disposition.json`'s `map_regrades`, so its
  `map_totals_after` was left at the pre-EP110 numbers and the brief inherited them.

19 at-start − 3 (→PARTIAL) − 2 (→PRESENT: EP110, EP252) = **14 ABSENT**. The rows are
self-consistent; only the two header blocks were stale.

## Per-row verification against the live tree (file:line proof)

Verified by opening the live file at the cited symbol. Paths are as found on disk.

| EP | recorded | verified | proof (live tree) |
|---|---|---|---|
| EP110 | PRESENT | **PRESENT ✓** | `azazael/src/CORE/dispatch_plan.py:475` `def simulate_vs_spawn`; production caller `azazael/src/CORE/WORMS/METACLUSTER.py:430` `costing = simulate_vs_spawn(...)` |
| EP252 | PRESENT | **PRESENT ✓** | `azazael/src/CORE/WORMS/expansion/scheduling.py:408` `class ScheduledTrainingWorm`, `:80` `class ScheduleConfig`, `:203` `def rampup_data_limit` |
| EP391 | PRESENT | **PRESENT ✓** | `azazael/src/CORE/local_memory.py:984` `def search_memories`, `:652` `def record_event` |
| EP183 | PARTIAL | **PARTIAL ✓** | `azazael/src/CORE/cd2_verifier.py:223` `def localize_violation`, `:288` `def localize_violations`, `:528` `def judge_result` |
| EP206 | PARTIAL | **PARTIAL ✓** | `azazael/src/CORE/local_memory.py:3039` `OBJECT_GRAPH_FORMAT`, `:3067` `def object_graph_document`, `:3136` `def export_object_graph` |
| EP237 | PARTIAL | **PARTIAL ✓** | `azazael/src/CORE/graph_artifacts.py:107` `def consult_map`, `:132` `class MapBeforeAct` |
| EP11 | ABSENT | **ABSENT ✓** (absence proven) | grep `deepspeed\|zero_stage\|optimizer_state_partition` over `*.py`: **0** hits in `azazael/src` that are implementations. All 102 hits are vendored third-party code under `azazael/archived/2026-05-31/onnxruntime*`, plus the absence-*probe* candidate list at `azazael/src/CORE/technique_wiring/_l0_model.py:240` (`candidates=["CORE.deepspeed","CORE.zero","deepspeed"]`) |
| EP68 | ABSENT | **ABSENT ✓** (absence proven) | same shape: `paged_attention\|block_table\|kv_cache_block` — no implementation in `src`; only the probe list at `azazael/src/CORE/technique_wiring/_l0_model.py:271` (`candidates=["CORE.paged_attention","CORE.vllm"]`) and the vendored archive |

8 of 141 rows individually verified. The three PRESENT rows the census depends on are
all confirmed, and so are the three PARTIAL regrades.

### Trap worth recording

A naive repo-wide grep for EP11/EP68's API names returns ~100 hits and would read as
"present". Every one is either vendored ONNX-Runtime source under
`azazael/archived/2026-05-31/` or an absence-probe candidate list. Absence claims in
this map are only meaningful when scoped to `azazael/src`, and the probe lists must be
excluded — they exist *because* the modules are absent.

## Stale citations found (same file, not corrected here — see note)

- **EP110** gap text cites `dispatch_plan.py:425` for `simulate_vs_spawn`; the function
  is at **475** (off by 50). Symbol and caller are correct; only the line drifted.
- **EP391** target cites `LocalMemoryStore.search_memories (L850)` and `record_event (L557)`;
  live lines are **984** and **652** (off by 134 and 95).

Both rows are nonetheless correctly graded PRESENT. I did not rewrite the gap prose,
because the row's *verdict* is what the census counts and the drift is recorded here
with exact numbers; editing 60-char line references inside two long prose strings risks
corrupting more than it fixes.

## Corrections applied

1. `state/sota_batches/batch06/technique_codebase_map.json` — `totals` changed from
   `15/124/2` to `ABSENT: 14 (was 15)`, `PARTIAL: 124`, `PRESENT: 3 (was 2)`. The prior
   values are retained inline as `ABSENT_was` / `PRESENT_was` so the change is auditable
   rather than silent.
2. `state/sota_batches/batch06/absent_disposition.json` — added `map_regrades_missed.EP110`
   (the fifth move, with its date and reason), preserved the old block as
   `map_totals_after_was`, and corrected `map_totals_after` to `14/124/3`.

No row was re-graded, weakened, or deleted to make the totals match; the header was
corrected to agree with the rows, which is the direction the evidence supports.

## UNVERIFIED — not counted as verified (standing rule)

Of 141 rows, **8 are verified above and 133 are UNVERIFIED by me**; absence of evidence
was not read as a verdict:

- **12 of 14 ABSENT** rows (EP14, EP38, EP39, EP52, EP141, EP153, EP176, EP226, EP245,
  EP278, EP300, EP343) — not independently re-probed. `absent_disposition.json` records
  a 19-worker swarm that did probe them (each row has a `missing_precondition`), which
  is prior work I did not repeat, but I did not re-establish it.
- **121 of 124 PARTIAL** rows — not individually re-verified. These name concrete hosts
  and are the largest exposure: 121 verdicts rest on the original pass, not on this one.

Both groups should be re-probed before the PARTIAL bucket is quoted as measured.
