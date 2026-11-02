# ELIZA lineage correction (2026-11-02)

**Status:** correction recorded. One project restored; one open question named and
deliberately left unresolved.

This document exists because an agent renamed one project into another and the
result read as a clean refactor. It was not. A `Project_*` directory was moved to a
different project's name, and the two projects have different subjects.

---

## 1. What happened

| Commit | Message | Effect |
|---|---|---|
| `c68e04e8` | "Project ELIZA: live channel, graded triage, PAMS refusal, and open-source packaging" | **Created** `Project_ELIZA/` — 17 files |
| `3fd0b463` | "Fitted affect bridge, concept-coherence triage, and an installable ELIZA" | Extended it |
| `f8c80428` | "Rename to Project Nurse Ratchet, and ship the construct battery that was the real blocker" | **Deleted** `Project_ELIZA/`, **created** `Project_Nurse_Ratchet/` |

`f8c80428` is a git file-level rename, not a deletion plus an unrelated add. The
similarity scores make that unambiguous:

| File | Similarity |
|---|---|
| `LICENSE` | 100% |
| `CODE_OF_CONDUCT.md` | 100% |
| `SECURITY.md` | 100% |
| `tests/test_psyche_fit_pams.py` | 100% |
| `CONTRIBUTING.md` | 96% |
| `docs/explanation/why-eliza.md` → `docs/explanation/why-nurse-ratchet.md` | 96% |
| `tests/test_psyche_network.py` | 99% |
| `.github/PULL_REQUEST_TEMPLATE.md` | 95% |
| `pyproject.toml` | 90% |
| `README.md` | 72% |

Every file survived with its content substantially intact. The project identity did
not.

---

## 2. Why it was wrong

**ELIZA is the FORENSIC INVESTIGATION suite.**
**Nurse Ratchet is the THERAPEUTIC HEALTH agent.**

These are two different projects with two different subjects. The rename treated
them as one project under two names, which means:

- the forensic investigation suite lost its directory and its name in one commit;
- the therapeutic health agent inherited a name it was never given;
- afterwards, a search for the forensic project by name returned nothing, because
  the name no longer existed on disk. Directory listings are evidence about
  *names*, not about *existence* — a renamed tree keeps every file and disappears
  from `ls` entirely.

That last point is the operational damage. The project looked deleted. It was not.

---

## 3. What was restored, and how

`Project_ELIZA/` was restored into the working tree from the last commit that
contained it under its own name:

```bash
git -C C:/Azazael/azazael checkout 3fd0b463 -- Project_ELIZA
```

This is additive and non-destructive: it restores files into the working tree, does
not touch `Project_Nurse_Ratchet/`, and does not rewrite history. `Project_ELIZA/`
exists again and both projects are present.

---

## 4. The rule

**Never rename a `Project_*` directory to a different project's name.**

A rename is valid only when the project identity is unchanged: a typo, a case
change, a corrected spelling of the same thing. A rename across two subjects is two
operations that must be performed separately:

1. **Retire** the old project — a deletion with a stated reason, recorded.
2. **Create** the new project — under its own name, with its own identity.

Collapsing those two into one `git mv` makes the retirement invisible and the
creation look like a continuation. It also guarantees that whoever looks for the
old name finds nothing and concludes the work was never done.

Corollary, earned the same day: **before concluding a project does not exist, check
git history, not just directories.** `git log --all --diff-filter=A --name-only` and
`git log --all --diff-filter=R --summary` answer "was this ever built" in a way that
`ls` and directory listings cannot.

---

## 5. Open question — stated, not resolved

`Project_ELIZA/` was restored, but **its committed contents at `3fd0b463` were the
psyche/affect stack** — `tests/test_psyche_affect.py`, `test_psyche_intuition.py`,
`test_psyche_network.py`, `test_psyche_rt_agent.py`, `test_psyche_traits.py`,
`test_psyche_bridge_fit.py`, `test_psyche_fit_pams.py`, plus
`docs/reference/psyche.md`. Its own `CITATION.cff` described it as "a therapeutic
agent loop with auditable psychological modelling", version 0.1.0, released
2026-11-01 — which reads as the therapeutic subject, not the forensic one.

So restoring the directory restores the *name and packaging*. It does not, by
itself, make `Project_ELIZA/` a forensic investigation suite. **Which tree holds
the forensic suite's actual code is unresolved.**

There is a second candidate: `C:/Azazael/azazael-forensics`, a standalone portable
forensic tree with its **own `.git`** ("Yggdrasil Cleave #11", landed 2026-10-28),
holding `goal_liveness`, `marker_audit`, `count_derivation`, `board_stale`, `home`
and `portable`. It contains no `eliza` string anywhere.

This document does **not** decide that `azazael-forensics` must be merged into, moved
into, or renamed to `Project_ELIZA/`. Two candidate homes exist, they were built at
different times for related purposes, and the decision belongs to the owner. Naming
the question is the deliverable here; answering it is not.

---

## 6. Related rename, recorded for completeness

The same sweep found one other rename touching a `Project_*` tree:

```
rename tools/sword_engine.py => Project_FLAME/tools/flame_engine.py (96%)
rename tests/{test_sword_engine.py => test_flame_engine.py} (94%)
```

This one moved a tool *into* a project tree and renamed it to match. It is recorded
here because it appeared in the same history search, not because it is asserted to
be wrong — unlike `Project_ELIZA` → `Project_Nurse_Ratchet`, no subject change is
established for it in the evidence available.

---

*Written 2026-11-02. Commit SHAs and file paths quoted as measured from
`C:/Azazael/azazael` git history on that date. No history was rewritten and no
project was deleted to produce this document.*
