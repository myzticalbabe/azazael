# Azazael — the tree, and where each package sits

**Standing order, 2026-11-01.** This document exists because a package was filed
under the wrong name and shipped that way. The correction is recorded here once,
in the place the next session will look, rather than argued again in chat.

## The structure

Azazael is the **Tree-of-Life**: the trunk every other project here grows from.
It is not a package beside the others — it is the thing they live inside.

```
Azazael  (root: canon, engine, tools, canon docs, all lanes)
├── Project ELIZA            forensic investigation — the full suite
├── Project Nurse Ratchet    the behavioral package
└── (declared)               CAIN, EVE, CODEX, AOA … as they are separated
```

On GitHub the umbrella repository is **`Azazael-Intel-Ultra-9-EVO`**: the root, the
canon and the engine, with each package as a directory inside it. A package that
grows enough to stand alone can be split later; until then one repository, one
history, one gate.

## What each package is

| package | what it is | what it is not |
|---|---|---|
| **Azazael** (root) | canon (`AGENTS.md`, `MANDATES.md`, `SOP.md`), the engine under `src/`, the instruments under `tools/`, the lane board, the gates | a product; a published library |
| **Project ELIZA** | the **forensic investigation full suite** — flock/tier method, edge proof ledger, identity tie-breaks, negative universes, behavioural inference from public record, and the tooling that executes it | the behavioural package; a repository of case data |
| **Project Nurse Ratchet** | the **behavioral package** — trait/affect model, construct graph, compiled intuition, the realtime loop, live counselors, the construct battery, and the instruments that grade them | a therapist; a clinical product; the forensic suite |

## The misfiling this document corrects

On 2026-11-01 the published tree was renamed `Project_ELIZA` →
`Project_Nurse_Ratchet`, because its *contents* were the behavioural stack and
`ELIZA` had been read as that project's name. The contents were filed correctly;
the meaning of the name was wrong. **ELIZA is the forensic suite.** It is not a
different spelling of the behavioural package, and the two are not
interchangeable: one interrogates public records about institutions, the other
models a single person's state.

The behavioural stack therefore stays in `Project_Nurse_Ratchet/`, and
`Project_ELIZA/` is the forensic suite. Neither may absorb the other.

## The one rule that keeps them apart

A forensic suite and a behavioural package fail in opposite directions.

- The forensic suite's failure is **publishing**: a name, a tenancy, a clinical
  record. Its gate is an allowlist and its default is refusal.
- The behavioural package's failure is **believing a number**: a recall figure
  from a corpus its own author wrote, a bridge fitted against a synthetic truth,
  a graph built from tags wearing construct names. Its gate is a negative
  control and its default is "this says nothing about a person".

Mixing them produces the worst of both: a behavioural claim with a forensic
suite's confidence, applied to a named individual. That is why they are separate
packages with separate gates, not two directories in one.

## "This will only work here"

The reference build is tuned to one box: an **Intel Core Ultra 9 285H (Arrow
Lake)** with an Arc 140T iGPU, running Windows, with a free-threaded CPython
3.15 build in `.venvs/py315t`. Accelerator choice, VRAM budgets, Blender device
strings and renderer settings are all properties of that machine. On a Mac, an
NVIDIA card or an Android phone, several of them are wrong.

That is not a defect to hide; it is a fitting problem, and it has a documented
answer:

- `docs/platforms/README.md` — the procedure, and the measurement that starts it
- `docs/platforms/intel-ultra-9-evo.md` — the reference box, measured
- `docs/platforms/windows.md`, `macos.md`, `android.md`, `cuda.md` — per-box
- `docs/platforms/BOX_PROMPTS.md` — the prompts to hand an agent to do the fitting
- `tools/box_profile.py` — measures a box and writes `box_profile.json`
- `scripts/box/` — the bootstrap per platform

No document in that set may claim a backend that `tools/box_profile.py` does not
report on the box it describes. `box_profile.py --check` fails a stored profile
that has drifted from the machine, because a platform document nobody can follow
is worse than no document.
