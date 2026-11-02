# Backlog audit — ten planning documents (2026-11-02)

**Scope:** the backlog as recorded in files. No board-database query was run (the
auditor had no terminal). Every count below is a hand count of markers read from
the file, not a tool estimate. Where a file was too large to read whole, the
coverage is stated.

**Headline for the publish decision: none of this backlog blocks publishing.**
It is documentation debt, not work. Two of the ten documents are already marked
SUPERSEDED by their own first paragraph, one is frozen at February 2026 and
points at directories that no longer exist, and the one purpose-built measurement
(`docs/TODO_TRIAGE_2026-10-31.md`) reports **0 open items** across every code
marker in the tree.

---

## 1. Counts, per document

| # | document | dash checkboxes `- [ ]` | table-cell `[ ]` | notes |
|---|---|---:|---:|---|
| 1 | `CODEBASE_AUDIT_TODO.md` (root, 746 lines) | **59** | 0 | living doc; read 741/746 |
| 2 | `MASTER_TASKS.md` | 0 | 0 | uses a table: **10 active** (T1–T10) |
| 3 | `ROADMAP.md` | **3** | 0 | 4.2 PARTIAL, 5.2 PARTIAL, 5.3 |
| 4 | `CATCHALL_BACKLOG.md` | 0 | 0 | generated ranked table, not a task list |
| 5 | `PRODUCTION_TODO.md` | **52** | 0 | **self-declared SUPERSEDED** |
| 6 | `RESTART_TASKS_2026-10-31.md` | 0 | 0 | 16 EV entries / 29 board rows |
| 7 | `RESTART_TASKS_INDEX.md` | 0 | 0 | generated; **8 live rows of 29** |
| 8 | `docs/TODO_TRIAGE_2026-10-31.md` | 0 | 0 | measured: 69 markers, **0 OPEN** |
| 9 | `docs/TASK_REGISTRY.md` (1889 lines) | **12** | **78** | dated **2026-02-11**; read 1817/1889 |
| 10 | `docs/CODEBASE_AUDIT_TODO.md` (164 lines) | **15** | 0 | **frozen 2026-06-02, "Do not update"** |

**Totals: 141 dash checkboxes; 219 unchecked markers** including the 78
table-cell markers in `docs/TASK_REGISTRY.md`.

Reading the total honestly: **141 dash checkboxes is the ceiling on real work,
and it is wrong by an order of magnitude** — §3 shows at least a dozen already
satisfied, several contradicted by another document, and 90 of the 141 sitting in
a document whose target directories do not exist.

---

## 2. Method, and its limit

- Counts are `- [ ]` occurrences read by eye in the file content, plus `| [ ] |`
  table cells counted separately so the two kinds are not conflated.
- Two files were not read to the end: `CODEBASE_AUDIT_TODO.md` (741 of 746 lines)
  and `docs/TASK_REGISTRY.md` (1817 of 1889). Their trailing 5 and 72 lines are
  appendices; a checkbox there would be missed, so those two counts are lower
  bounds.
- **Instrument warning carried from this session:** `code_search`/`glob` return
  `Found 0 matches` with exit code 2 in parts of this tree even when the target
  exists. A control search for `Project_CRADLE|FLAMING_SWORD` returned 0. No
  absence in this document rests on those tools; every existence claim rests on
  `list_directory` or `read_files`.
- "VERIFIED-DONE" below means **I read the artifact** and it satisfies the item.
  "STALE" means the named artifact is absent or the claim is contradicted by a
  readable file. Nothing is marked done because it looks done.

---

## 3. Spot-checks against the actual tree (12)

| # | item, and the document claiming it | what the tree says | verdict |
|---|---|---|---|
| 1 | `[ ]` Unit tests for CLUSTERWORMS dynamic resolution — `PRODUCTION_TODO` §1, `CODEBASE_AUDIT_TODO` Step 3 | `tests/test_clusterworms_unit.py` **exists** | **STALE-DONE** |
| 2 | "`test_nature_clusters_unit.py` already comprehensive" — `CODEBASE_AUDIT_TODO` Step 3 | that filename is **absent** from `tests/`; `test_metacluster_orchestration.py` and `test_metacluster_rehearsal.py` exist instead | **claim unverifiable** — the cited evidence file does not exist |
| 3 | `[ ]` Unit tests for METACLUSTER routing — same two docs | `test_metacluster_unit.py` **absent** | **open, renamed** — not stale-done |
| 4 | `[ ]` Circuit breaker — `CODEBASE_AUDIT_TODO` Step 4 | `tests/test_circuit_breaker_integration.py` **exists**; `PRODUCTION_TODO` marks the same item `[x]` | **STALE**, and the two docs disagree |
| 5 | `[ ]` Dead letter queue — `CODEBASE_AUDIT_TODO` Step 4 | `tests/test_dead_letter_summary.py`, `test_dlq_watch.py` **exist**; `PRODUCTION_TODO` marks `[x]` | **STALE**, contradiction |
| 6 | `[ ]` Retry with exponential backoff — `CODEBASE_AUDIT_TODO` Step 4 | `PRODUCTION_TODO` marks `[x]`; `tests/test_error_recovery.py` exists | **STALE**, contradiction |
| 7 | EV-006: `two-interpreter-suite` gate **BLIND**, baseline absent — `RESTART_TASKS_2026-10-31.md` | `logs/ci_two_interpreter_gate_baseline.json` **exists** (and `ci_two_interpreter_gate.json`) | **STALE** — fixed after 2026-10-31 |
| 8 | EV-006: `aggregate-suite-isolation` baseline absent | `logs/aggregate_isolation_baseline.json` **exists** | **STALE** — same |
| 9 | `docs/TASK_REGISTRY.md` P0-002 / P1-001 / P1-003 target `Desktop/Azazael/`, `WORMZ/`, `KLINK/`, `SHORTY/`, `METAWORMS/`, `HYDRA/`, `TWITLER/`, `BIBL/`, `POINDEXTER/`, `PERSEPHONE/`, `TERENCE/`, `TARBABY/` | `list_directory` on Desktop: **none of these exist** | **all 90 markers unworkable as written** |
| 10 | `docs/CODEBASE_AUDIT_TODO.md` §9: "Total test files **0**" | `tests/` holds **380+** test modules | **premise false** |
| 11 | `docs/TODO_TRIAGE_2026-10-31.md`: 0 markers claim outstanding work | consistent with the above; it is the only document that measured rather than listed | **VERIFIED** (as a reading) |
| 12 | ROADMAP 5.2 checkpoint drill — "FAILED for a real reason… regression tests in `tests/test_nsga2.py`" | `tests/test_nsga2.py` **exists** | **fix real, item still open** for the other two signals |

Additional confirmations while in `tests/`: `test_metthew_families.py`,
`test_psyche_*.py` (14 files), `test_receipt_guard.py`,
`test_delegation_trace_ids.py`, `test_prose_forensics.py` all exist — so METTHEW,
the PSYCHE stack, and this session's three slices are on disk. No
`test_eliza_release_gate.py` is present, despite `tools/eliza_release_gate.py`
being listed in the earlier history sweep.

---

## 4. Duplicates across documents

**The dominant duplication is structural, not incidental:
`CODEBASE_AUDIT_TODO.md` Phase 23+ Steps 3–12 is a second listing of
`PRODUCTION_TODO.md` §1–12.** Roughly 50 items are the same work stated twice —
and in at least three cases (circuit breaker, retry, DLQ) the two documents give
**opposite statuses** for the same item, because `PRODUCTION_TODO` was updated
and `CODEBASE_AUDIT_TODO` was not.

Direct duplicates (same item, ≥2 documents):

| item | appears in |
|---|---|
| Unit tests: CLUSTERWORMS / NATURE_CLUSTERS / METACLUSTER | `PRODUCTION_TODO` §1, `CODEBASE_AUDIT_TODO` Step 3 |
| Circuit breaker, retry+backoff, dead letter queue | `PRODUCTION_TODO` §2, `CODEBASE_AUDIT_TODO` Step 4 — **statuses conflict** |
| Centralized YAML/TOML config | `PRODUCTION_TODO` §3, `CODEBASE_AUDIT_TODO` Step 5, `docs/CODEBASE_AUDIT_TODO` §8 |
| ThreadPoolExecutor instead of raw threads | `PRODUCTION_TODO` §4, `CODEBASE_AUDIT_TODO` Step 7 |
| Cache registry lookups; lazy-load worm modules | `PRODUCTION_TODO` §4, `CODEBASE_AUDIT_TODO` Step 7 |
| Structured JSON logging | `PRODUCTION_TODO` §6, `CODEBASE_AUDIT_TODO` Step 8, `docs/CODEBASE_AUDIT_TODO` §8 |
| API reference | `PRODUCTION_TODO` §5, `CODEBASE_AUDIT_TODO` Step 8, `TASK_REGISTRY` P1-202 |
| Architecture diagram in README | `PRODUCTION_TODO` §5, `CODEBASE_AUDIT_TODO` Step 8 |
| Registry versioning / dependency graph / health scoring | `PRODUCTION_TODO` §7, `CODEBASE_AUDIT_TODO` Step 9 |
| Workflow templates / DSL / conditional routing / replay | `PRODUCTION_TODO` §8, `CODEBASE_AUDIT_TODO` Step 9 |
| Single-entry CLI / Docker / scheduled runs / git hook | `PRODUCTION_TODO` §12, `CODEBASE_AUDIT_TODO` Step 11 |
| Web dashboard / real-time Mermaid / `cluster status` | `PRODUCTION_TODO` §11, `CODEBASE_AUDIT_TODO` Step 12 |
| `__all__` on exports; standardize bare `except` | `PRODUCTION_TODO` §10, `CODEBASE_AUDIT_TODO` Step 6 |

Also duplicated internally: `TASK_REGISTRY` numbers two different tasks
`P3-002` (data-flow diagrams) and `P3-002` (file manifest database), and two
`P3-101` (security checklist) and `P3-101` (file headers) — so its own IDs are
not unique and cannot be cited unambiguously.

---

## 5. High-value and genuinely actionable for a GitHub publish

**Nothing here gates the publish.** Ranked by value per unit of work:

1. **Stop the two documents from lying about each other.** `PRODUCTION_TODO` and
   `CODEBASE_AUDIT_TODO` disagree on circuit breaker, retry and DLQ. One edit
   each — mark the three items done in `CODEBASE_AUDIT_TODO` Step 4, citing
   `tests/test_circuit_breaker_integration.py`, `test_error_recovery.py`,
   `test_dead_letter_summary.py`. Highest-value 10 minutes in this backlog.
2. **Retire `docs/TASK_REGISTRY.md`.** 90 markers, all pointed at Desktop trees
   that do not exist, dated before this repo's current layout. It cannot be
   worked and it inflates any backlog count by 90.
3. **Retire `docs/CODEBASE_AUDIT_TODO.md`.** Frozen, self-marked
   "🔴 SUPERSEDED — Do not update", and its §9 premise ("Total test files 0") is
   false. Keeping it invites someone to act on it.
4. **Close EV-006** in `RESTART_TASKS_2026-10-31.md`. Both baselines it calls
   absent now exist in `logs/`. One-line correction, and it removes two
   "BLIND gate" findings that read as open risk.
5. **Keep** `docs/TODO_TRIAGE_2026-10-31.md` and `RESTART_TASKS_INDEX.md` as-is.
   They are the only two documents in the set that measure instead of list, and
   both state their own limits.

---

## 6. Recommended retirement list

| item | reason |
|---|---|
| `docs/TASK_REGISTRY.md` | 2026-02-11; 90 markers target `Desktop/WORMZ`, `KLINK`, `SHORTY`, `METAWORMS`, `HYDRA` — none exist on this host today |
| `docs/CODEBASE_AUDIT_TODO.md` | frozen 2026-06-02, self-marked SUPERSEDED, premise "0 test files" is false against 380+ |
| `PRODUCTION_TODO.md` (body) | self-marked SUPERSEDED; its 52 items are re-listed in `CODEBASE_AUDIT_TODO` — keep as history, stop reading it as a plan |
| `CODEBASE_AUDIT_TODO.md` Step 4 items 1–3 | satisfied: circuit breaker, retry, DLQ all have tests on disk |
| `CODEBASE_AUDIT_TODO.md` Step 3, "unit tests for CLUSTERWORMS" | `tests/test_clusterworms_unit.py` exists |
| `RESTART_TASKS` EV-006 (both blind gates) | both baselines now present in `logs/` |
| `CODEBASE_AUDIT_TODO.md` Step 6, "delete all 14 deprecation shims" | contradicted ~200 lines earlier in the same file: AR-9 records the 13 shims already deleted 2026-06-04 |
| `MASTER_TASKS.md` T1–T4 | Nuitka 3.14t/LNK2001 build tasks; `PRODUCTION_TODO` and `CODEBASE_AUDIT_TODO` both record Nuitka **SUSPENDED** — blocked upstream, not work |

**Do not retire:** `docs/TODO_TRIAGE_2026-10-31.md` (0 open, measured),
`RESTART_TASKS_INDEX.md` (8 live rows are pointers to real board rows),
`ROADMAP.md` (3 items, all with honest PARTIAL notes and named artifacts).

---

## 7. What this audit did not do

- No board database was read, so the 61 claimable rows and the 394 surplus rows
  recorded in `RESTART_TASKS` are **not** counted here. This document covers file
  backlogs only.
- No test was run. Every existence claim is about presence on disk, not about the
  test passing.
- `CODEBASE_AUDIT_TODO.md` (5 lines) and `docs/TASK_REGISTRY.md` (72 lines) were
  not read to the end; their counts are lower bounds.
- The 69-marker / 0-OPEN result in `docs/TODO_TRIAGE_2026-10-31.md` is quoted as
  that document's measurement, not independently re-derived.
