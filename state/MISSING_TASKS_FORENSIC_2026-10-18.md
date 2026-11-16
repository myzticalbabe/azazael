# MISSING TASKS — FULL FORENSIC INVESTIGATION (2026-10-18)

Method: sweep protocol 0Z-L — 3.15t free-threaded (`C:/Azazael/.venvs/py315t/Scripts/python.exe`),
ThreadPoolExecutor(24), per-file `git show HEAD:<path>` (HEAD-pinned, never worktree),
subprocess `encoding="utf-8", errors="replace"`, scripts in `/tmp` (invoked via `cygpath -w`
to avoid the git-bash/Python `/tmp` divergence trap). Read-only pass; scripts wrote output to
`%TEMP%` only. Sweep scope: 3,917 md+py files at HEAD of `C:/Azazael/azazael` (vendored/
archived trees excluded: archive/, packages/, vendor/, node_modules/, .build/, .agents/skills/azazael-pkg*),
0 `git show` errors. Sources cross-referenced: Engram plan items (64 open, lower bound),
PMB goals (80 active: 65 pending / 12 in_progress / 2 blocked / 1 planned), supervisor triage,
and all 6 environments (windows, wsl2_ubuntu, kali, g_source, g_root, desktop) + G: archive
`G:/AZAZAEL_MD_ARCHIVE_2026-10-18` (5,083-row SHA-256 manifest, format-verified).

Estate totals (measured): **72 md files / 4,715 open checkboxes at HEAD**, **129 first-party
TODO-class markers in 50 py files** (232 more in 107 vendored files), plus 8 files / 159 open
boxes in the azazael-coord repo and 881 open boxes in untracked md.

---

## A. LOST TASK ARTIFACTS — 2 files gone from every environment, archive, and git history

| Engram | File | Claimed | Evidence |
|---|---|---|---|
| #1229 | COHERENCE_AUDIT_2026-10-10.md | 11 open | Absent at HEAD (never tracked), absent worktree, absent all 6 envs (full-depth find), absent G: archive manifest (format-verified grep, 0 hits) |
| #1222 | EXHAUSTIVE_WIRING_AUDIT_2026-10-13.md | 17 open + 13 blocked | Same: exists nowhere |

**28 task items' surrounding context is unrecoverable** except from the Engram task text itself.
These two plan items cannot be executed as written — they need either content recovery from a
quoting agent's memory or disposition as dead-with-proof.

## B. MISLOCATED — 1 file found in a Desktop project, not at the tracked path

| Engram | File | Claimed | Found |
|---|---|---|---|
| #1238 | POSTDOC_RESEARCH_MANIFEST.md | 21 open | `C:/Azazael/desktop/EveUnleashed_Selector/docs/POSTDOC_RESEARCH_MANIFEST.md` (measured 21 open — exact match) + copy in `G:/source-of-truth/azazael/azazael-dirty-baseline-20261002/` |

The task content is intact; the plan item points at the wrong path.

## C. CONSUMED-BUT-OPEN — 4 Engram items contradicted by live content

All four files exist at HEAD but contain **zero checkbox markers of any syntax** (`[ ]`, `[x]`,
`[-]`, …) — the claimed counts reference content that no longer exists in the files (likely
consumed by the 2026-10-18 md-churn disposition commits `4aa472b2`/`03a6980a`):

| Engram | File | Claimed | Measured at HEAD |
|---|---|---|---|
| #1287 | NEURAL_MESH_GAP_AUDIT_2026-09-14.md | 1 open, 15 stale | 0 boxes |
| #1286 | NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md | 1 open, 4 blocked | 0 boxes |
| #1285 | NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-15.md | 1 open | 0 boxes |
| #1217 | TODO_315T_BUILD.md | 7 blocked | 0 boxes |

## D. UNTRACKED-BUT-EMPTY — 2 plan items on git-invisible files

| Engram | File | Claimed | Measured (worktree) |
|---|---|---|---|
| #1290 | state/BRIEF_884_MIMO_MERGE.md | 1 open, 4 blocked | 0 boxes; file exists **untracked** only |
| #1279 | state/MIMO_STRAIGHTEN_REPORT_2026-10-14.md | 2 open, 9 blocked | 0 boxes; file exists **untracked** only |

First forensic pass mislabeled these "dead at HEAD"; corrected — HEAD-absence was untrackedness.
(Verification protocol rule 4/5 near-miss, caught before reporting.)

## E. SUPERSEDED-BUT-LIVE — the single largest stale artifact

**NEURAL_MESH_FUNCTION_TODO.md (Engram #1216, "superseded by ledger") is still at HEAD with
3,659 open boxes — 77.6% of the entire estate's checkbox mass (3,659 / 4,715).** Either the
file must be cut (it is declared superseded) or the supersession proven. As long as it lives,
every estate-wide checkbox count is dominated by a document nobody intends to execute.

## F. UNTRACKED TASK MASS — 62 files / 881 open boxes with NO plan item (azazael repo)

Top offenders (open boxes, at HEAD unless noted):

- 86 DISCLOSURE_WHITEPAPER_TODO.md (coord copy has 88 — the mirrors have **drifted apart**)
- 67 TODO_FULL_PRODUCTION_WIRING.md
- 53 PRODUCTION_TODO.md · 53 research/RESEARCH_RECORD.md · 50 output/EVE_UNLEASHED_TODO.md
- 37 LESSONS_MASTER.md · 30 docs/RUST_CONVERSION_PLAN.md
- 24 state/ACTION_REGISTRY_2026-10-10.md (untracked; coord repo has identical 24)
- 19 NEURAL_MESH_BRAINSTEM_TODO.md · 17 PLATFORM_DEPLOYMENT.md
- 14+14+9 Azazael_ENHANCEMENT_PLAN.md (3 divergent copies: root docs/, src/CODEX/DOCUMENTATION/, src/ORCHESTRATION/)
- 12 RESEARCH_AI_ML_RL_PROTOCOL_EVOLUTION.md · 12 docs/web_research_synthesis.md
- 10 SOP.md · 10 docs/NUITKA_3_14T_SKILL.md · 8 DIRECT_MEMORY_INSTRUCTIONS.md · 7 CONTRIBUTING.md · 7 SYSTEM_INSTRUCTIONS.md

Caveat: the 62 include skill-checklist mirrors (skills/, skills.win-backup/, .agents/skills/
each carry copies — e.g. azazael-production 53×3, devtools-* ×3), which triple-count.
Deduped, the distinct untracked task docs number roughly 30–35. The untracked md sweep of the
worktree (`git ls-files --others`) found **0** additional open boxes beyond the HEAD set.

## G. CODE-LEVEL MISSING TASKS — 129 first-party TODO/FIXME/XXX/HACK markers, no tracker

Top: `tools/graph_semantic/semantic_layer.py` 18 · `tools/mesh_function_preflight.py` 8 ·
`src/CORE/spine_registry.py` 7 · `src/META/METAWORMS_ENRICHED.py` 6 + `src/METAWORMS_ENRICHED.py`
6 (duplicate copy — one more mirror-pair) · `tools/render_monitors.py` 6 ·
`src/CORE/enforcement_harness.py` 5 · `tests/test_sync_g_drive.py` 5.
None of these appear in any task store. Vendored remainder (SCons/pkg_resources under
`nuitka_build_backup/inline_copy/`): 232 markers, correctly excluded from the count.

## H. ENVIRONMENT DRIFT — task docs disagree across the 6 environments

Measured open-box counts per environment (probe scope: root/docs/state + `find -maxdepth 3`
for WSL; **absence in this table is not proof of absence in unprobed subdirs**):

| Doc | windows | g_source | g_root | wsl2/kali | Note |
|---|---|---|---|---|---|
| SOP.md | 10 | **16** | 10 | 10 | G: "source of truth" holds 6 MORE open canon items |
| PRODUCTION_TODO.md | 53 | **51** | 53 | 53 | g_source 2 behind |
| azazael-production.md | 1 (root copy) | – | 1 | **53** | full checklist only on WSL/Kali |
| RESEARCH_RECORD.md | (research/) | – | – | 53 | WSL/Kali only |
| NEURAL_MESH_FUNCTION_TODO.md | 3659 | – | – | – | Windows-only |
| RULE_AUDIT_TODO.md | 20 | – | – | – | Windows-only |
| ACTION_REGISTRY_2026-10-10.md | 24 | – | – | – | Windows-only |
| NEURAL_MESH_BRAINSTEM_TODO.md | 19 | – | – | – | Windows-only |
| ROADMAP.md | 3 | – | – | – | Windows-only |
| web_research_synthesis.md | 12 | – | – | – | Windows-only |

Per-env distinct-doc counts (44 basenames probed): windows 27, wsl2_ubuntu 32, kali 32,
g_root 21, g_source 19, desktop 10. **SOP.md canon drift is the highest-severity row: the
declared source of truth disagrees with every other environment on open canon items.**

## I. CROSS-STORE GAP — tasks tracked in one memory, absent from the other

- Engram: 64 open plan items (lower bound; union of 27 queries). The checkbox-doc items
  (#1216–#1290) and lane items (#932–#1059) exist **only** in Engram — no PMB goal twins.
- PMB: 80 active goals. Entire blocks have **no Engram plan item**: Eve/GGUF merge (#884/#786/#790),
  SOTA batch06 swarms & census, trainer wiring/retirement (#770/#721/wave-3), tooling builds
  (test_paradigm_gate, preflight_all wiring, GGUFAnalyzer.convert, sharded runner, baseline
  persist), sidecar cleanup, KV/n-gram llama tuning.
- PAMS: contributes nothing — conversation capture dead (0 messages since 2026-05-27),
  3 curated memories, tool_calls 49 rows. Advisory in the supervisor verdict.

## J. AUDIT INTEGRITY NOTES (near-misses, recorded)

1. `git status` entry count moved 12→13 during this read-only session; my commands issued no
   repo writes (all outputs to `%TEMP%`/`/tmp`). Baseline was saved as a **count, not a list** —
   the delta is therefore unattributable; suspected concurrent lane/daemon. Instrument gap.
2. First pass labeled state/BRIEF_884 + MIMO_STRAIGHTEN "dead at HEAD"; corrected to
   alive-untracked after full-depth find (rule 4/5).
3. `supervisor__verdict` and `supervisor__fanout_search` MCP calls timed out (-32001) twice;
   CLI fallback (`session_start.py` / `engram_supervise.py`) delivered CLARIFY — consistent.

---

## DISPOSITION RECOMMENDATIONS (not executed — ownership lanes decide)

1. #1229 / #1222: dead-with-proof or content-recovery ask; 28 items' context is gone.
2. #1238: repoint to the desktop copy (21 boxes verified intact).
3. #1287 / #1286 / #1285 / #1217 / #1290 / #1279: close as consumed — live files carry zero boxes.
4. #1216: cut NEURAL_MESH_FUNCTION_TODO.md (3,659 boxes) or prove the ledger supersession.
5. File plan items for the ~30 distinct untracked task docs (section F) or declare them archival.
6. Reconcile SOP.md (16 vs 10) between g_source and all other environments — canon-critical.
7. Mint a tracker for the 129 first-party code TODOs (section G) or triage them to wontfix.
8. Memory-unity (#380): PMB↔Engram twin mapping for the two disjoint goal blocks (section I).

---

## CORRECTION ADDENDUM + IMPLEMENTATION (2026-10-18, post-verification)

The user mandate "everything shall be verified before you cut" drove a second
verification pass before dispositions. It falsified parts of this report:

**C/D CLASSES REVERSED — premise-drifted, NOT consumed.** The minted plan-item
claims (e.g. #1217 "7 BLOCKED, 2 stale, 2 todo", #1290 "1 open, 4 blocked,
1 stale") were counted on a STATUS-MARKER basis (BLOCKED/stale/todo labels in
tables and prose), while the sweep counted only `- [ ]` checkboxes. The two
bases are incommensurable, so "zero checkboxes vs claimed counts" was never a
contradiction. Line-level re-reads show live content: TODO_315T_BUILD.md holds
a live T-n table (T-3 promotion gate, T-6 Intel wheels, T-10 memory-store
debt), MIMO_STRAIGHTEN holds 23 status rows. Items #1217 #1279 #1285 #1286
#1287 #1290 stay LIVE pending re-derivation with the minting parser's scheme
(Engram #1316; #1312's C/D claim superseded by judgment).

**CLASS B CORRECTED — #1238 was accurate as minted.** The item already pointed
at desktop/EveUnleashed_Selector/docs/POSTDOC_RESEARCH_MANIFEST.md (21 claimed
= 21 measured). The "mislocation" was the forensic search key (supervisor
display truncates the path), not the item. No repoint needed.

**CLASS A STANDS — dead-with-proof.** #1229 and #1222 verified gone from every
plane: never tracked in any ref of either repo (git log --all, rc=0, empty),
no referencing file at HEAD, absent worktree / all 6 envs / G:/AZAZAEL /
G:/AZAZAEL_SOURCE_OF_TRUTH / G:/source-of-truth incl. dirty-baseline / E: /
desktop / state backups / the 5,083-row archive manifest (format read first).

**EXECUTED — FU2 cut (commit 314cae20, branch deepseek-engram-813 [renamed to azazael-intel-ultra-9-evo 2026-11-04]).**
NEURAL_MESH_FUNCTION_TODO.md deleted with 2 consumer-checked companion edits:
artifact_freshness REGISTRY entry dropped (spine.py:1888 proprioception gate
reads that module; a missing row reads as stale and would refuse every heart
beat) and refresh_all census step dropped (--verdict calls build() itself,
proven by mesh --check green post-cut). The #1216 "superseded by ledger"
rationale was scope-mismatched (ledger declares 370 functions, the file 1,543);
the verified grounds: generated probe census, 0/3,659 boxes ever ticked, stale
vs rebuild (3,961/1,553 vs 3,939/1,543), semantic layer calls it "a census ...
not a to-do list". Post-cut battery: pytest 43 passed 2 skipped (rc=0),
mesh --check rc=0 (370 declarations fresh), freshness rows show the TODO row
gone and no new stale/missing. Bulk gate blocked the deletion commit on the
150-line cap; re-run under the sanctioned ALLOW_BULK_COMMIT=1 declaration with
justification in-message. Rebuild anytime: one tools/mesh_function_preflight.py
run.

**EXECUTED — FU3 reconciled.** G:/source-of-truth/azazael/SOP.md overwrote from
canonical after verifying the 6 extra boxes were a stale duplicate checklist
section (backup: state/SOP_g_source_backup_2026-10-18.md); G: now byte-identical
to canonical, 16→10 boxes. Root cause fixed: SOP.md added to SYNC_DOC_PATTERNS
(scripts/sync_all.py), membership verified by dry-run inspection. MANDATES.md
has the identical sync gap — filed as a plan goal.

**EXECUTED — FU4 filed.** 22 PMB plan goals (outbox 749): one per distinct
untracked task doc, 3 code-TODO area goals (129 first-party markers in 50
files), a template/skill-checklist reclassification goal (SOP/SYSTEM_INSTRUCTIONS/
skills checkbox classes are per-session checklist templates, not work items),
a mirror-dedupe goal, and the MANDATES.md sync goal. FU1 dispositions: Engram
#1316/#1317, 7 conflict pairs judged including the self-correction supersedes.
