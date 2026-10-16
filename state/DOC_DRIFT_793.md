# DOC-DRIFT AUDIT — Engram #793 (worker B of 3), 2026-10-15

> **Model ID**: DeepSeek V4.1 Flash Fast. **Repo root** (`git rev-parse --show-toplevel`): `C:/Azazael/azazael`, branch `migration/baseline-20261001`. Coordinator-supplied at commit time.

Lane: docs-only. Every claim below was checked against the live tree; the `proof`
column cites a line that was actually opened, not an assumption. Claims I could not
check are in **UNVERIFIED**, not in the table.

Instrument note, load-bearing: **`code_search`/`ripgrep` cannot see `state/`** — `state/*`
is git-ignored, and ripgrep honours `.gitignore` even for files git already tracks. Every
`state/` doc was therefore read with `read_files`/`list_directory`, and searching *inside*
them needed `-uu`. A "0 matches" result over `azazael/state` is a query artifact, not
evidence of absence — the same trap `SOTA_STEAL_AUDIT.md` §1 already records.

## Claim table

| # | claim | where written | current truth | proof | stale? |
|---|---|---|---|---|---|
| 1 | `state/*` is at `.gitignore:248` | `SOTA_REACH_AUDIT.md` (closing note) | `state/*` is at **`:257`**; line 248 is a comment line (`# defect as S10 …`) | `azazael/.gitignore:257` = `state/*`; `:256` = `!state/`; `git check-ignore -v` → `.gitignore:257` | **YES** |
| 2 | "the coordinator must `git add -f` it to version it" | `SOTA_REACH_AUDIT.md` (closing note) | already in the index — force-add is not required for this file | `git ls-files state/` lists `state/SOTA_REACH_AUDIT.md` (22 tracked `state/` files) | **YES** |
| 3 | `next_interval_hours` read at `scheduling.py:921` | `SOTA_REACH_AUDIT.md` row `scheduling.next_interval_hours` | read at **`:941`** | `scheduling.py:941` = `deadline = time.time() + self.next_interval_hours() * 3600` | **YES** |
| 4 | `plan["ready_order"]` read at `METACLUSTER.py:441` | `SOTA_REACH_AUDIT.md` row `dispatch_plan.plan_dag` | read at **`:455`** (`:441` is a `_publish_plan(...)` argument) | `METACLUSTER.py:455` = `rank = ({n: i for i, n in enumerate(plan.get("ready_order") or [])}`; call at `:411` | **YES** |
| 5 | `participation_prior` called by `action_space` at `allocation.py:301` | `SOTA_REACH_AUDIT.md` row `allocation.participation_prior` | called at **`:303`** (`:301` is `"actions": list(self.arms),`) | `allocation.py:303` = `"priors": self.participation_prior(),`; defs `:248` / `action_space` `:291` | **YES** |
| 6 | `allocation.action_space` "called by `joint_action_space` (`allocation.py:301/376`)" | `SOTA_REACH_AUDIT.md` row `allocation.action_space` | `:376` ✓ (`space = alloc.action_space()`); `:301` does not support this claim — it belongs to row 5 | `allocation.py:357` def `joint_action_space`; `:376` inside it | **partly** |
| 7 | "**41** hook symbols … with a production caller **8** … internal-only **8** … test-only **23** … no caller anywhere **2** … **31 of 41 (76%)** do not reach a live call site" | `SOTA_REACH_AUDIT.md` §Counts | the doc's **own table** holds **42** rows and classifies **8 / 6 / 27 / 1**, i.e. the counts do not reconcile with the table they summarise | re-derived from the table's own `production caller?` column in this same file (8 `YES`; 6 `internal only`; 1 `READ live, SET never`; 27 `NO`) | **YES** |
| 8 | the 8 live-caller names include `dialectic` | `SOTA_REACH_AUDIT.md` §Counts | `dialectic` appears in **no row** of that table; the table's 8th `YES` row is `dispatch_plan.plan_dag` (consumer), which the list omits | same file: table rows vs §Counts list | **YES** |
| 9 | scanner `if len(body) != 1` at `:487` | `GATE_SEMANTICS.md` §2 | `:487` | `scanner.py:487` = `if len(body) != 1:` | no |
| 10 | `ast.Pass` → `silent_except_pass` at `:493-495` | `GATE_SEMANTICS.md` §2 | `:493-495` | `scanner.py:493` = `if isinstance(stmt, ast.Pass):` | no |
| 11 | `_SUPPRESSION_MARKER` at `:197` | `GATE_SEMANTICS.md` §3 | `:197` | `scanner.py:197` = `_SUPPRESSION_MARKER = "# scanner:ignore"` | no |
| 12 | suppression set built at `:516` | `GATE_SEMANTICS.md` §3 | `:516` | `scanner.py:516` = `suppressed = {i for i, line in enumerate(lines, 1) if _SUPPRESSION_MARKER in line}` | no |
| 13 | "Rules added 2026-10-03 (measured first, see FINDING_SEVERITIES)" at `:178` | `GATE_SEMANTICS.md` §2 | `:178` | `scanner.py:178` = that comment, verbatim | no |
| 14 | severities "`:73`-`:75`" for `silent_except_pass`/`except_return_default`/`subprocess_no_timeout` | `GATE_SEMANTICS.md` §2 | **`:72`-`:74`** (dict opens at `:59`, `unicode_emoji` at `:60`) | `scanner.py:72,73,74`; counts 842 / 692 / 244 all present and correct | **YES** |
| 15 | precondition rationale at `:482-486` | `GATE_SEMANTICS.md` §2 | **`:481-485`** (`:486` = `body = node.body`) | `scanner.py:481-486` | **YES** |
| 16 | "Report at the STATEMENT's line" comment at `:489-491` | `GATE_SEMANTICS.md` §2 | **`:490-492`** | `scanner.py:490-492` | **YES** |
| 17 | "The file is explicit" comment at `:497-499` | `GATE_SEMANTICS.md` §2 | **`:498-500`** | `scanner.py:498-500` | **YES** |
| 18 | constant-restriction rule at `:499-503` | `GATE_SEMANTICS.md` §2 | **`:502-504`** (`:502` = `if value is None or isinstance(value, ast.Constant):`) | `scanner.py:502-504` | **YES** |
| 19 | findings dropped when line suppressed at `:520-521` | `GATE_SEMANTICS.md` §3 | **`:522-523`** (`:521` = `for ln, cat, sn in findings:`) | `scanner.py:521-523` | **YES** |
| 20 | scanner `severity_order` mirrored at `:1039` | `GATE_SEMANTICS.md` §2 | **`:1034`** | `scanner.py:1034` = `severity_order = {"error": 0, "warning": 1, "info": 2}` | **YES** |
| 21 | `subprocess_no_timeout` timeout check at `:443`, doc/string skips at `:445-447` | `GATE_SEMANTICS.md` §2 | range `:439-448` ✓ as a range; the checks are at **`:442`** and **`:444`/`:446`** | `scanner.py:442` = `if "timeout" in _call_text(lines, i - 1, m.start()):` | **YES** |
| 22 | `SEVERITY_ORDER` at `staged_scanner_gate.py:42` | `GATE_SEMANTICS.md` §2 | `:42` | `staged_scanner_gate.py:42` | no |
| 23 | staged file list from `git diff --cached … --diff-filter=ACMR` filtered to `.py` at `:58` and `:94` | `GATE_SEMANTICS.md` §4 | `:58` = the `--diff-filter=ACMR` call; `:94` = `files = _staged_py_files()` | `staged_scanner_gate.py:58`, `:94` | no |
| 24 | `_counts` counts at `:69` | `GATE_SEMANTICS.md` §2 | def is at **`:67`**; `:69` is inside it | `staged_scanner_gate.py:67-72` | **YES** (minor) |
| 25 | `IDENTITY_SCHEME` at `anti_pattern_gate.py:64` | `GATE_SEMANTICS.md` §5 | **`:65`** | `anti_pattern_gate.py:65`; `DEFAULT_DIR`/`BASELINE` at `:67`/`:68` ✓ | **YES** (minor) |
| 26 | `DEFAULT_MAX_FILES = 8` at `:32`, `DEFAULT_MAX_LINES = 150` at `:31` | `GATE_SEMANTICS.md` §5 | `:32` / `:31` | `scripts/commit_gate.py:31,32` | no |
| 27 | `evaluate` at `:86` | `GATE_SEMANTICS.md` §5 | `:86` | `scripts/commit_gate.py:86` = `def evaluate(rows: …` | no |
| 28 | create-exemption + "Creates still count toward the file tally" at `:96-99` | `GATE_SEMANTICS.md` §5 | docstring is **`:90-93`**; the `len(tracked) > max_files` guard is at **`:98`** | `scripts/commit_gate.py:90-98` | **YES** |
| 29 | `ALLOW_BULK_COMMIT == "1"` short-circuit at `:120` | `GATE_SEMANTICS.md` §5 | **`:121`** (`:122` prints the quoted line ✓) | `scripts/commit_gate.py:121,122` | **YES** (minor) |
| 30 | "A second copy of this hook exists at `scripts/hooks/pre-commit` … **Unverified:** whether it is a stale duplicate" | `GATE_SEMANTICS.md` §1 | the file **exists** (`scripts/hooks/pre-commit`); which host uses it is still unverified, so the doc's hedge is right but its "exists" half can be promoted from unverified to verified | `glob azazael/scripts/hooks/*` → `azazael/scripts/hooks/pre-commit` | no (improvable) |
| 31 | "**every future modification needs `git add -f`**" to `.githooks/pre-commit` | `ACTION_REGISTRY_2026-10-10.md` §12 | **superseded**: `.gitignore` now carries `.githooks/*` (contents, not the directory) plus `!.githooks/pre-commit`, so a plain `git add .githooks/pre-commit` succeeds and no force-add is needed | `azazael/.gitignore:82` = `.githooks/*`, `:95` = `!.githooks/pre-commit`; the rule's own comment (`:89-94`) states the trailing-slash form was why the negation was inert | **YES** |
| 32 | D-2: `engram_read_pressure` write-only, "1 hit repo-wide" | `ACTION_REGISTRY_2026-10-10.md` (§D) | **already corrected in place** — the row is marked `[x] D-2 **CLOSED**`, "Both halves have real readers"; code agrees: `technique_runtime._read_pressure_summary` (`:504`) is called at `:591` | `ACTION_REGISTRY_2026-10-10.md:108`; `technique_runtime.py:504`, `:591`; `engram.py:745` names the consumer | no |
| 33 | H-3 host citations: `training_intake.py:143 build_training_records()`, `run_training_orchestrator.py:370 run_intake_cycle` | `ACTION_REGISTRY_2026-10-10.md` (H-3, DONE `07fcb0bd`) | both **exact** | `training_intake.py:143`; `run_training_orchestrator.py:370` | no |
| 34 | H-3 host citation `scripts/track_registry.py:65` for the `INTAKE` track | `ACTION_REGISTRY_2026-10-10.md` (H-3) | the `"INTAKE"` entry is at **`:67`** | `track_registry.py:67` = `"INTAKE": {"kind": "cycle", "runner": "run_intake_cycle",` | **YES** (minor) |
| 35 | artifacts `azazael/state/sota_manifest_ep1-478.json`, `sota_diff_vs_held15.json`, `sota_yt_index.txt` | `SOTA_STEAL_AUDIT.md` §6 | all three **exist** | `list_directory azazael/state` (all three listed) | no |
| 36 | tools `sota_dedup_check.py`, `sota_tech_source.py` | `SOTA_STEAL_AUDIT.md` §6 | both **exist** | `glob azazael/tools/sota_*.py` (7 files, both present) | no |
| 37 | `state/sota_batches/batch0{1,2,3,4}/` carry `MANIFEST.md` + `TECHNIQUES.md` | `SOTA_STEAL_AUDIT.md` §6 | all 8 **exist** | `glob state/sota_batches/batch0{1,2,3,4}/*.md` → 8 files | no |
| 38 | batch06 = 141 techniques / 168 note rows / 159 distinct `topic_key` | `SOTA_STEAL_AUDIT.md` §7.1-7.2 | `technique/` holds **141** files, and the corpus review reconciles the same numbers | `list_directory state/sota_batches/batch06` → `technique: 141`; `state/bake_harvest_2026-10-15.jsonl` row `engram#354` | no |
| 39 | `next_interval_hours` has a **production** caller (row 3 aside) | `SOTA_REACH_AUDIT.md` | corroborated: the call sits in the scheduler loop, not a test | `scheduling.py:941` (inside `_scheduler_loop`'s scheduling body) | no |
| 40 | `apply_dense_reward` at `learning_grpo.py:284`; `dense_implicit_reward` called at `:488` | `SOTA_REACH_AUDIT.md` | both **exact** | `learning_grpo.py:284`, `:488` | no |
| 41 | `locate_pivotal_turn` at `reflexion.py:190`; `pivotal_credit_weights` at `:195` | `SOTA_REACH_AUDIT.md` | both **exact**; `record_reflection` (def `:130`) also has a production caller | `reflexion.py:190`, `:195`; `technique_runtime.py:319` calls `record_reflection` | no |
| 42 | `drive_for_workflow_step` "imported and called by `workflow.py:73`" | `SOTA_REACH_AUDIT.md` | `:73` is the **import**; the claim's word "called" is not evidenced at that line | `workflow.py:73` = `from CORE.structured_action import drive_for_workflow_step as _react_step_drive` | **partly** |
| 43 | `governance.quantify` called by `evaluate_with_uncertainty` at `governance.py:451` | `SOTA_REACH_AUDIT.md` | **exact** — `:451` is the call | `compliance/governance.py:448` def, `:451` = `result["quantified"] = self.quantify()` | no |
| 44 | `mode_decider` read at `neural_loop.py:504` | `SOTA_REACH_AUDIT.md` | **exact** | `neural_loop.py:504` = `if ctx.mode_decider is not None:` | no |
| 45 | `dream_arena.predict_next` called by `simulate` at `dream_arena.py:176` | `SOTA_REACH_AUDIT.md` | **exact** | `dream_arena.py:176` = `cur = predict_next(cur, act, magnitude)` | no |
| 46 | `graph_artifacts.py:161` calls `consult_map` | `SOTA_REACH_AUDIT.md` | **exact** | `graph_artifacts.py:161` = `consultation = consult_map(target, graph=self.graph, atlas=self.atlas)` | no |
| 47 | "309 of 701 `src/` modules reachable, 392 unreachable … 330 have no importer" | `STRUCTURAL_FLAWS_315T.md` §S1 | internal arithmetic ✓ (309+392=701); the **tree has moved** since: a later lane measured **707** and the coordinator measured a 705-file `src/` | `STRUCTURAL_FLAWS_315T.md:54`; `state/bake_harvest_2026-10-15.jsonl` row `engram#652` ("HEAD has **707**") | **dated** |
| 48 | "`state/` … 19 state/ files ARE tracked" | `state/bake_deepseek_next.jsonl` row `732-P0-02` | now **22** tracked `state/` files (three dated docs landed after that measurement) | `git ls-files state/ \| wc -l` → 22 | **YES** |

## Docs edited (all inside `azazael/state/`, the lane's write scope)

1. **`SOTA_REACH_AUDIT.md`** — rows 1, 2, 3, 4, 5, 6, 7, 8, 42 of the table.
   Line citations corrected; the §Counts block re-derived from the doc's own table and the
   disagreement stated, rather than a new headline number asserted in its place; the closing
   `git add -f` note corrected.
2. **`GATE_SEMANTICS.md`** — rows 14-21, 24, 25, 28, 29, 30. Twelve drifted line numbers
   corrected (the load-bearing ones — `:487`, `:178`, `:197`, `:516`, `:493-495`,
   `staged_scanner_gate.py:42/58/94`, `commit_gate.py:31/32/86` — were all **already correct**
   and are unchanged). The `scripts/hooks/pre-commit` hedge was narrowed: existence verified,
   which host uses it still unverified.
3. **`ACTION_REGISTRY_2026-10-10.md`** — rows 31, 34. §12's `.githooks` force-add consequence
   corrected to the current `.gitignore` rule; H-3's `track_registry.py` citation corrected.
4. **`SOTA_STEAL_AUDIT.md`** — no edit: rows 35-38 all verified. Recorded here as clean so the
   next lane does not re-audit it.

## Found stale, NOT fixed — outside this lane's write scope

Reported, not touched (`state/` at the repo ROOT and the repo-root `*.md` files are other lanes'
territory; `state/*.json` is frozen by the #793 brief, and `state/adoption_census.json` is
off-limits outright):

- **`azazael/.gitignore:245`** — the comment says "**three** of its files are the EVIDENCE", but
  the block below it now negates **five** (`adoption_census.json`, `orphan_scan.json`,
  `suite_baseline.jsonl`, `SOLAR_PRO4_EVIDENCE_2026-10-14.jsonl`, `…​.md`). Proof:
  `.gitignore:258-262`.
- **`azazael/.gitignore:248`** — the citation line every other doc copied is itself the *comment*
  line; the rule is at `:257`. Whoever edits the comment should fix the count in the same pass.
- **`STRUCTURAL_FLAWS_315T.md` §S1** — "309 of 701" is a dated snapshot; the tree has since been
  measured at 707 and 705 by two independent lanes. A count of this kind should carry its date
  and the instrument that produced it.
- **`state/bake_deepseek_next.jsonl` row `732-P0-02`** — "19 state/ files ARE tracked / `.gitignore:257`":
  the line number is right, the count is now 22.
- **`state/bake_harvest_2026-10-15.jsonl` row `engram#367`** — repeats "`engram_read_pressure` …
  write-only, zero consumers", which D-2 closed **and** the code contradicts
  (`technique_runtime._read_pressure_summary` called at `:591`). A harvest row is data, not a doc,
  so it is flagged for the ingest owner rather than edited.

## Cross-check handed to worker A (batch06 census)

The #793 brief pre-states **15 ABSENT / 124 PARTIAL / 2 PRESENT** for batch06. The reconciled
corpus review in this tree records a **different** split of the same 141 rows —
**19 ABSENT / 121 PARTIAL / 1 PRESENT** (`state/bake_harvest_2026-10-15.jsonl` row `engram#354`;
both triples sum to 141). Two reconciliations of one census cannot both be current, and the row
itself warns that the map's `gap` field "corrected the first pass repeatedly: 16+ rows flipped
ABSENT→PARTIAL/PRESENT on recheck, so a first-pass ABSENT verdict is not trustworthy." The
recount must therefore state which of the two it is correcting, or it will re-litigate a settled
split. `state/sota_batches/batch06/absent/` holds **19** files, which is a third figure for the
same question and is the number to reconcile against first.

## UNVERIFIED

1. **`.githooks/pre-commit`'s own header comment** (GATE_SEMANTICS §1: "documents only checks
   1-4; the body implements six"). The file is a dotfile directory; the search tool skips it and
   this lane has no terminal, so the claim is neither confirmed nor denied here.
2. **`.githooks/pre-commit`'s check ORDER and blocking flags** (§1 table, six rows) — same reason.
   The doc's own citations are verbatim section headers, so the claim is re-checkable by a lane
   with a shell; I could not re-check it.
3. **"this session measured `2670 finding(s) in 702 file(s)`"** (`GATE_SEMANTICS.md` §2) — the doc
   already frames this as a dated measurement whose authority is the gate's own output. Neither the
   number nor the file count is re-derivable without running `tools/anti_pattern_gate.py --check`,
   which this lane cannot do. Note for the reader: the coordinator of #784 separately found the
   anti-pattern baseline recording **708** files against a live **705**, so the *file* half of this
   pair has moved since it was written.
4. **`docs/` ADR drift** — `azazael/docs/` and `azazael/ADRs/` exist, but this lane's scope was the
   eight named sources; the ADR set was not opened. ADR drift remains unaudited.
5. **Which host uses `scripts/hooks/pre-commit`** (GATE_SEMANTICS §1). Existence verified; usage
   not.
6. **`state/` docs at the repo ROOT** (as opposed to `azazael/state/`) — `state/sota_batches/…`
   and the other root-`state/` maps were read only where a citation pointed into them.
