# EDGE0 x AZAZAEL — Why edge0-intel is NOT incorporated (2026-09-24)

## Verdict: BY DESIGN — a covenant forbids absorption

"The Oxford Compact" (edge0-intel/COMPACT.md, named 2026-09-23) defines three
powers — and rule 1 is explicit: "Separation of powers: forge builds, mesh
executes, audit verifies. **No member absorbs another's role.**"

| Power | Repo | Role (verbatim from COMPACT.md) |
|-------|------|--------------------------------|
| The Oxford ShardFoundry | edge0-intel | "evolves tensor-shard populations into champion models. Builds, never executes mesh tasks." |
| The Azazael Neural Mesh | azazael | "226 worms executing triage, monitoring, and action. Runs drivers, never grades them." |
| The Audit Office | evals / SVI / gates / ledgers | "measures and certifies. Builds neither genomes nor runs worms; it admits or rejects." |

## The integration model is endpoint + ledger, not code

Compact rule 2: "Drivers cross by endpoint only (providers contract); fitness
crosses by ledger row only. **No shared mutable state between powers.**"

Evidence of that pattern in code (read 2026-09-24):

- `edge0-intel/scripts/build_az_eval.py:1-22` — READS azazael's
  `worm_config_trace.json` + `neural_mesh_*_2026-09-16.jsonl` to build driver
  fitness sets (`eval_sets/az_tasks_50.json`). One-way, read-only consumption.
- `edge0-intel/scripts/repaird.py:14` — hard interlock: "never: git ops,
  weight-file deletes, ledger edits, anything outside edge0-intel
  (azazael/BCC off limits)."
- azazael references edge0 in exactly 2 places: `azazael/tools/_edge0_collect_gemma_dir.py`
  (a parked copy of an edge0 foundry script) and this session's audit report.
  Zero code coupling, zero shared mutable state.

## Why the wall exists (history)

- `edge0-intel/INCIDENT_freebuff.md` (2026-09-22): two foundry scripts were
  found rewritten on disk by an unknown external writer; the response added the
  "azazael/BCC off limits" interlock and an OBSERVE-first logging rule.
- The Compact was named ONE DAY LATER (2026-09-23). The separation-of-powers
  covenant reads as the governance answer to that incident: a shared-mutable-state
  ban so no power can silently rewrite another's work.
- `edge0-intel/TOOL_GAP_AUDIT.md` notes the repo is "shared with an unknown
  writer" (foreign files appear in the index from another process) — the
  covenant + allowlists are the containment strategy.

## What edge0-intel actually is

- In-repo work: tensor-shard model evolution ("meta-evolution" — GGUF/safetensors
  surgery, abliteration, dose-response sweeps, SVI gates; see HANDOFF.md,
  META_EVOLUTION.md, SVI_SPEC.md). Different domain from the worm mesh.
- `edge0-intel/_upstream/`: a separate OSS project (Edge0 — streaming MoE
  inference framework: SSD expert offload + Recover-LoRA + prerouter routing;
  arXiv 2609.18063, github.com/Edge0-AI/Edge0). Vendored upstream — not
  azazael material either.
- Cross-references that DO exist are read-only tooling: `build_az_eval.py`
  (reads azazael records to build fitness evals) and `SESSION_2026-09-23.md:72`
  (doc-sprawl audit comparing the two doc sets).

## Implications

1. "Incorporating" edge0 into azazael would violate Compact rule 1 and the
   repaird interlock. Any such change requires renegotiating the Compact first
   (it lives at edge0-intel/COMPACT.md and is one day older than this analysis).
2. The sanctioned integration surface is exactly what already exists: providers
   contract (drivers cross by endpoint), ledger rows (fitness crosses as data),
   and read-only record pulls (build_az_eval.py pattern).
3. If tighter coupling is ever wanted, amend the Compact deliberately — do not
   absorb code quietly. That quiet absorption is precisely what the 2026-09-22
   incident made unacceptable.

## Sources (all read 2026-09-24)

edge0-intel/COMPACT.md, edge0-intel/HANDOFF.md, edge0-intel/META_EVOLUTION.md,
edge0-intel/INCIDENT_freebuff.md, edge0-intel/TOOL_GAP_AUDIT.md:35-55,
edge0-intel/SESSION_2026-09-23.md:65-80, edge0-intel/scripts/build_az_eval.py:1-28,
edge0-intel/scripts/repaird.py:1-22, edge0-intel/_upstream/README.md:1-15,
azazael/tools/_edge0_collect_gemma_dir.py:1-15.
