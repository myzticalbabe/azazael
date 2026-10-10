# Why the harvested techniques are an outlier layer, not a refactored codebase

Date: 2026-10-09. Question asked: *why are the techniques outlier instead of
refactored code base as instructed?* Every number below comes from a command run
against this tree; nothing is inferred from the docs' claims about themselves.

## 1. What the instruction actually said — adoption, not adjacency

`state/SOTA_INTEGRATION_BLUEPRINT.md` (the plan of record) asks for mechanisms to
be **absorbed by existing subsystems**:

| blueprint line | instruction |
|---|---|
| L1 Prove | "ATP capsules + verified negatives **onto the existing hash chains**" |
| L2 | "procedural-family system, **replaces flat files**" |
| L3 | "**one acceptance gate** with five detectors … **extends the engram gate**" |
| L5 Plan | "**extends clusters**" |
| L5 Place | "Agora role pools + affinity (**extends pools**)" |
| L3 governance | "step remediation at tool-call boundaries (**extends the engram gate**)" |
| P2 | "L2 family library + CASS gate (**organize what exists**)" |
| DATA FLOWS #2 | "L3's gate sits on **EVERY transition** (tool calls, memory writes, rollouts)" |

So the instruction is unambiguous: existing modules adopt the mechanism, and the
gate sits on every transition.

## 2. What was executed — a new layer beside the codebase

| measurement | value |
|---|---|
| new files in the technique family | 18 (8 sibling `CORE/*.py` + 10 `technique_wiring/` files: `__init__` + 9 slices) |
| lines in that family | **6,322** |
| commits ever touching `skill_library.py`, `verification_gate.py`, `structured_action.py`, `dispatch_plan.py`, `rubric_evolution.py`, `technique_runtime.py` | **0 each** — the whole programme is an uncommitted working-tree dump |
| production call sites into the layer, from files *outside* it | **1** (`METACLUSTER` → `dispatch_plan.plan_dag`) before 2026-10-09; **4** after the boundary hooks added the same day (corrected 2026-10-09→10: the 5th counted engram read-pressure, which is intra-module in `engram.py` with zero technique imports) |
| technique count given a "call path" that way | **181** |
| consumers that actually drove it | **6 exercise tools** (`tools/exercise_*.py`) |
| `skill_library.py` / `structured_action.py` / `verification_gate.py` diff vs HEAD | 399+/399, 188+/188, 616+/616 — **100% insertions**: new files, not edits to anything |

One production caller for 181 techniques, and the only things exercising the rest
were the exercise scripts. By the project's own test (`a capability invoked only
by a test is still dead code`) the layer was dead at the time of measurement.

## 3. Why it happened — three mechanisms, all checkable

1. **The map's own target column pointed at the new layer.** The named Azazael
   targets in `SOTA_TECHNIQUE_CODEBASE_MAP.md` are, by mention count:
   `local_memory.py` 9× — then `verification_gate.py` 5×, `skill_library.py` 5×,
   `structured_action.py` 3×, `dispatch_plan.py` 2×: i.e. the *programme's own
   modules* are among the most-cited "hosts". The blueprint modules were written
   first and then became the landing sites, so "the technique landed on its host"
   self-confirmed inside the new layer. The map names this itself — "Five modules
   already compose earlier steals … (the **'SOTA blueprint' programme**)".

2. **121 of 141 rows already had a host, and the plan had no refactor step.**
   The map's verdict table is PARTIAL = **121**, ABSENT = 19, PRESENT = 1. A
   PARTIAL row means a real module covers part of the mechanism and the named
   element is missing — the delta belongs *in that module*. The build plan
   (`TODO_315T_BUILD.md`, T-1…T-12) contains no task of the form "edit host H to
   adopt technique T"; its nearest entry, T-11, is "**Build** the L1/L3 blueprint
   items that need real work". A plan with no refactor task cannot produce a
   refactor, so the delta was written next to the host instead of into it.

3. **The instrument could not tell wiring from adoption.** Engagement was
   measured through the registry's own loop — `exercise_technique_runtime.py`
   reports `corpus 181 / wired 181 / engaged 181 / errored 0`, which is a
   statement about the registry, not about the codebase. Nothing counted
   production call sites. This is the same defect class as a metric reading a
   clean zero on a table that was never written: the number was green because the
   thing it measured was the thing that was built.

## 4. Consequence

The defect being repaired on 2026-10-09 ("a capability invoked only by an exercise
is dead code") existed at the **layer** level, not only at the function level. The
four boundary hooks added that day (sentinel_enforcer → `verify_boundary`,
circuit_breaker → `reflect_on_failure`, METACLUSTER → `reflect_on_failure`,
engram → read-pressure consolidation) are the first real adoption — 4 hosts, not
121. They repair symptom #1; they are not the structural fix.

## 5. Remediation shape (what "as instructed" would look like)

- For each PARTIAL row, move the delta **into the host named in the map**
  (`local_memory`, `audit_trail`, `meta_evolution`, `data_retention`,
  `WORMS/expansion/engram`, `compliance/state_machine`, …) and leave behind (a) a
  registration call and (b) a call at the host's natural boundary — the exact
  shape of the 2026-10-09 hooks.
- Demote `technique_runtime` from "where techniques live" to "the ledger that
  proves which host adopted which technique". A registry entry is evidence of
  wiring; it is never evidence of adoption.
- Replace the engagement instrument: count **production call sites per
  technique** and score exercise-only engagement as **zero**. Keep
  `exercise_technique_runtime.py` as a smoke test, but stop citing its
  `engaged=181` as coverage.

## 6. Limits of this finding

- "Production call site" is a grep for imports/references from `src/` outside the
  new layer; a host that later calls the layer through a string/dynamic dispatch
  would be undercounted. No such dispatch was found, but the count is a lower
  bound, not a proof of zero.
- The 121 PARTIAL rows were graded by workers in `map_part{1..8}.md`; the
  per-row claims are not re-verified here. What is verified here is the *shape*:
  new files, one caller, exercise-only consumers, no refactor task in the plan.
