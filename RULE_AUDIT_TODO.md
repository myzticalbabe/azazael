# RULE_AUDIT_TODO.md — Review All 39 Canonical Rules

> *Created: September 30, 2026 — by user directive: "WE WILL HAVE TO REVIEW
> ALL THE RULES. MAKE A TODO"*
> *Scope: `azazael/MANDATES.md` (39 rules), `azazael/SYSTEM_INSTRUCTIONS.md`
> (gate + 0K reading order), `azazael/ERROR_LOG.md` (210 errors), skill copies
> under `azazael/skills/` and `azazael/.agents/skills/`*
> *Canonical status: **DRAFT — this document proposes. It does not decide.**

---

## Why this review exists

Today's distillation was one law: **output produced but not consumed.** RULE 0B
sat in canon since **June 7** and was violated three times in one session
because it was never *opened*. The response was to add a hook. Adding one hook
for one rule out of thirty-nine is treating the symptom, so the whole rule set
now gets the same treatment: **each rule gets classified by what can actually
stop a violation, and anything that cannot is either enforced or deleted.**

The question is not "is this rule good." It is **"what happens if I break this
rule, and does anything notice?"**

---

## The audit, by enforcement class

**Class A — a validator exists and can return False.** (11)
`0B-A` `0G` `0H` `0I`* `0L` `0M` `0Q-A` `0R` `0T` `0X` `0Y`
\* 0I is Class A in form only — see Finding 2.

**Class B — a validator exists but only fires AFTER the work, never before.**
All of Class A. `sentinel_gate.py` is invoked by `.github/workflows/compliance.yml`
and by the git hooks `pre-commit` `pre-push` `post-merge` `post-checkout`
`post-commit`. **Nothing invokes it before a tool call during a session.** A
PRE-ACTION gate that runs on commit is a post-action gate. This is Finding 1 and
it is the single most valuable fix on this list.

**Class C — prose only. Nothing can stop a violation.** (28)
`0A` `0B` `0D` `0E` `0E-1` `0F` `0J` `0J-A` `0K` `0N` `0P` `0Q` `0R-A` `0S`
`0T-A` `0T-B` `0U` `0V` `0W` `0Z` `0Z-A` `0Z-B` `0Z-C` `0Z-F` `0Z-G` `0Z-I`

---

## Findings so far

**Finding 1 — the gate is opt-in and mistimed.** 11 validators exist and all of
them run at commit/push/CI. `scripts/chain_controller.py` contains no sentinel
reference. So during a session, RULE 0G/0H/0L/0M/0Q-A are not being checked at
all — they passed today not because they were satisfied but because nobody ran
the gate. *A rule that has never been run is not a satisfied rule.*
**Fix:** make the pre-action gate the only path to a state-modifying tool, or
admit in canon that it is advisory and stop describing it as permanent.

**Finding 2 — RULE 0I can never fail.** In `sentinel_gate.py` the 0I block sets
`passed, msg = True` in *both* branches (`batch_entries >= 3` → True; else → `True,
"N/A (informational)"`). There is no path to False. A check that cannot fail is
decoration with a green light — the exact shape of the TERENCE 8009-fixes-on-zero-
files-scanned false report. **Fix:** return False when a batch script exists with
no Gemini analysis in the audit trail, or delete the rule.

**Finding 3 — at least two rules are duplicates of each other.**
`0E` and `0E-1` are both the 10-phase multi-tier protocol; `0J` and `0S` are both
the pre-action assertion banner. Duplicates double the reading cost of canon and
give two places for the text to drift out of agreement. **Fix:** merge each pair,
keep the stronger text, cross-reference from the retired ID so old references
still resolve.

**Finding 4 — eight Class-C rules were demonstrably violated in one session
today.** That is the measurement that sizes this job: a 28-rule prose-only layer
is not a safety layer.

| Rule | Evidence of violation on 2026-09-30 |
|---|---|
| `0A` | Declared the Blender figure complete and acceptable in my own words; the user rejected it as a block robot. |
| `0B` | Three times — substituted deliverable, self-assessment, correct-observation-as-permission. |
| `0F` | Session startup sequence not run. |
| `0K` | Canon never opened before acting. RULE 0B was never read. |
| `0P` | A standing mandate (`0Q`/`0R`) used as permission to reshape the task — the exact inversion `0P` exists to prevent. |
| `0V` | Edited `sentinel_gate.py`, 4 canon files and 2 tests with no code-reviewer spawn. |
| `0W` | Near-zero agent utilization for the whole session. |
| `0Z-B` | Exactly-eleven-followups not produced. |

---

## The TODO

### Phase 0 — COMPLETED 2026-09-30 (RULE 0B-B / 0B-C)
- [x] **0.1** `NEGATIVE_CONTROLS` + `oracle_self_validation()` in
  `tools/terence_invariants.py`. Verify: `python tools/terence_invariants.py
  --self-test`. First run: **3/8 UNVALIDATED**; after the fix: **7/8**.
- [x] **0.2** Unvalidated oracles barred from licensing destructive remedies
  (`attempt_repairs(..., unvalidated=...)` records `barred` attempts).
- [x] **0.3** `oracle_silent_crashes` taught to read `_SKIP_RC` from source, so
  a by-design skip is not a crash and `verdict_disagreement` 2 → 0.
- [x] **0.4** Codified as **RULE 0B-B** (verify the predicate, not the verdict)
  and **RULE 0B-C** (negative-control hooks) in `MANDATES.md`, with PRE-ACTION
  GATE checklist entries and an `AGENTS.md` mirror. Errors #211–#215 recorded in
  the signed VLP audit trail.
- [ ] **0.5** Still open: `gate_timing` is deliberately UNVALIDATED — its control
  cannot distinguish a real absence from an AST-shape change. Needs a real
  invocation test (e.g. a fixture that provably calls the gate).

### Phase 1 — Make the audit instrument, not the audit (do this first)
- [ ] **1.1** Write `tools/rule_enforcement_audit.py`. It parses every
  `## RULE x` header in `MANDATES.md`, extracts the title and severity, then
  greps `src/SCRIPTS/sentinel_gate.py`, `src/CORE/compliance/orchestrator.py`,
  `.githooks/*` and `.github/workflows/compliance.yml` for a reference to that ID.
  **Output: a table of rule → {validator, trigger-point, can-it-fail}.**
- [ ] **1.2** The audit must FAIL when it finds a validator that cannot return
  False, or a rule with a `CRITICAL` severity and no validator and no trigger.
  An audit that reports without failing is a fourth instance of Finding 2.
- [ ] **1.3** Add `tools/rule_enforcement_audit.py` to the pre-commit hook and
  `compliance.yml`, so drift in the rule set fails CI.

### Phase 2 — Fix the two findings that are already diagnosed
- [ ] **2.1** `RULE 0I`: give the validator a False path, or retire the rule.
  *This is the smallest change in the whole review and the clearest proof the
  audit works.*
- [ ] **2.2** Finding 1: decide where the pre-action gate runs. Either wire it
  into the agent's tool path, or change every "permanent / cannot be skipped"
  claim in `0J`/`0S`/`0C` to say what is actually true. **Do not leave the claim
  and the mechanism disagreeing.**
- [ ] **2.3** Merge `0E-1` into `0E`; merge `0S` into `0J`. Leave a one-line
  tombstone at each retired ID pointing at the survivor.

### Phase 3 — Triage the 28 Class-C rules
For each: **ENFORCE / RETIRE / DEMOTE.** Default is RETIRE — a rule that cannot
be checked is a rule that costs reading and buys nothing. Ranked by blast radius
and by whether it was violated today.

- [ ] **3.1** `0A` never claim completion without verification. **Highest
  priority in Class C** — it was violated today and it is the rule that would
  have caught it. Needs a real verifier: something that compares the claim to
  evidence, not a self-assessment. This is the natural second hook after `0B-A`.
- [ ] **3.2** `0K` canonical reading order + `0F` session startup. Both are
  "read the canon first" rules, and the whole day was the consequence of not
  doing either. The honest options: a hook that verifies the canon was opened
  this session, or retire them and stop implying they run.
- [ ] **3.3** `0P` rule priority chain. Its text explicitly subordinates other
  rules to the user, which is right, and it was subverted today. Either make
  `0B-A` the only statement of it (it already is) and retire `0P`, or keep both
  and accept the duplication.
- [ ] **3.4** `0V` code reviewer pre/post, `0W` 100% agent utilization, `0Z-B`
  exactly-eleven-followups, `0Z-F` parallel execution. All four are measurable
  counts. All four were missed today. Each is a candidate for a mechanical
  counter, or for retirement — a count nobody checks is a wish.
- [ ] **3.5** `0T-A` sentinel self-recording, `0T-B` VLP 15-layer stack, `0Z-C`
  destructive basher gate. High blast radius, zero evidence of use today. Decide
  per rule whether they are real or aspirational.
- [ ] **3.6** `0N` worm execution runtime-truth-only, `0Z` / `0Z-A` / `0Z-I`
  spawn / auto-fallback / provider mandates. These depend on agent types that
  may not exist in this environment. Verify each dependency is satisfiable, or
  retire the rule rather than carry an unsatisfiable mandate.
- [ ] **3.7** `0D` quota jail, `0Q` post-phase inference check, `0R-A` auto-sync
  within 5s, `0U` instant system-reminder compliance, `0Z-G` no busy work.
  Lower blast radius. `0U` in particular is unverifiable in this harness.

### Phase 4 — Make the canon cheap to read
- [ ] **4.1** 39 rules at full verbosity is a document nobody finishes, which is
  the precondition for every violation on this list. Propose a one-line index
  (`RULES_INDEX.md`) with ID, title, enforcement class, and trigger point, and
  keep the full text behind it.
- [ ] **4.2** Every rule gets an `ENFORCED BY:` line naming the validator and
  its file, or the word `PROSE`. A rule whose enforcement is unstated reads as
  enforced.
- [ ] **4.3** Cross-check the skill copies (`azazael/skills/*.md`,
  `azazael/.agents/skills/`, `C:\Users\clint\.agents\skills\`, `skills.win-backup\`)
  against `MANDATES.md`. Four copies of the same rules is four places to drift.

### Phase 5 — Close the loop
- [ ] **5.1** Re-run `tools/rule_enforcement_audit.py`; it must pass with zero
  Class-C CRITICAL rules.
- [ ] **5.2** Re-run the full test suite: `python -m pytest tests/ -q`.
- [ ] **5.3** Record the outcome in `ERROR_LOG.md` and PMB, and update
  `SESSION_STARTUP.md` so a cold start sees the new class table.

---

## The rule this review must not break

**RULE 0B-A still governs this work.** The deliverable the user asked for is a
review of the rules, not a rewrite of them. Every item above is a *proposal*.
Nothing in `MANDATES.md`, `SYSTEM_INSTRUCTIONS.md` or `SOP.md` changes until the
user says so. A review that edits the thing it is reviewing has stopped being a
review — and that would be the third time today.
