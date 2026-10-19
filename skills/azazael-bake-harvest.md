---
name: azazael-bake-harvest
description: Precondition-gated error/near-miss harvest into bake-lane JSONL. Use when a task brief carries the ERROR CAPTURE clause or when running a multi-step lane where errors must survive to session end.
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: false
  version: 1.0.0
  created: 2026-10-19
---

# Bake-Harvest — Precondition-Gated Error Capture

Errors recorded at encounter time survive; errors reconstructed at session
end lose detail and over-weight what is still salient. This skill is the
reusable form of the ERROR CAPTURE clause (codified Oct 17 2026, RULE #716).

## Preconditions (all three, else do not open a lane)

1. **Lane file named**: `state/bake_<agent>_<date>.jsonl` (twin of the task
   brief where briefs use file twins, e.g. `state/bake_kilo_merge.jsonl`).
2. **Validator present**: `tools/merge_bake_lane.py` — dry-run must be runnable
   before the first write, not after the last.
3. **Kinds fixed**: `error_fix | lesson | mandate | sop_rule | violation |
   anti_pattern` — anything else is dropped at merge with BAD_KIND.

## Row schema (validator-enforced)

`{source, item_id, title, body, kind}` — all five keys required, `kind` in
the schema above, `body >= 40 chars`. Invalid rows go to the merge report,
never the merged lane.

## The gate rule

Record at ENCOUNTER TIME — the moment an error, near-miss, or falsification
appears — not at session end. Dead ends count. Zero-error completion still
writes the attestation the brief requires.

## Close-out

1. `python tools/merge_bake_lane.py --lane state/<lane>.jsonl` (dry run) clean.
2. With `--apply` only when the brief authorizes the merge.
3. ONE summary at end (Engram or PMB per brief), naming the lane file.
