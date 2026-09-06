---
name: background-sweep-resilience
description: Run long multi-thousand-file automated sweeps (CDP render checks,
  audits, hash scans) without losing hours to one crash — background launch,
  per-file try/except isolation, log-to-file with progress, resume-from-crash-point,
  basename-dedup pitfalls, and Windows path gotchas. Hard-won 2026-09-02 on the
  2,754-file CDP sweep.
metadata:
  category: process
  projects: azazael, aoa
  priority: medium
  audit_date: 2026-09-02
  auto_load: false
---

# Background Sweep Resilience — Long-Run Automation Without Rage-Quits

## 🛑 LONG-RUN GATE — assertion before batch / background runs

**Gate owner for BATCH RUNS / LONG BACKGROUND PROCESSES** (sweeps, refreshes,
graph regenerations, fetcher batches, model pilots — anything with an expected
runtime that approaches or exceeds the command timeout). The pre-action gates
gate FILE-EDIT actions; a batch that runs for 10+ minutes in the foreground
(or dies silently mid-sweep) was outside every gate until 2026-09-04.
Route: `pre-action-gate-lite` **Gate 0c**.

**Before launching ANY batch/background run (est. duration > ~2 min, or any
background launch with `&`), print this assertion in response text (NOT
thinking):**

```text
🛑 [LONG-RUN GATE]
- Sized? (unit count × per-unit cost from a pilot → time estimate printed)
- Foreground or background chosen? (est > timeout → background + log file;
  never hold the foreground for a 10-min+ run)
- Per-unit isolation? (try/except per file/unit → FAIL row, never whole-run
  unwind — the 2,754-file crash-at-2,598 lesson)
- Progress observable? (log file + flush=True progress lines you can tail)
- Resume plan? (deterministic sorted order → resume-from-crash-point known)
- Orphan cleanup? (kill/cleanup path identified for the process class —
  java, python, robocopy)
- GATE DECISION: [PROCEED / HALT — size it and isolate it first]
```

HALT rule: **an unsized run, or a run without per-unit try/except, or a
foreground hold on an expected-10-min+ job = CRITICAL** — the exact shapes
that wasted hours on 2026-09-02/04. When in doubt, pilot 50 units first, then
background with a log.

## The incident that writes this skill

2026-09-02: a 2,754-file project-wide CDP render sweep crashed at file 2,598 with
an unhandled `WebSocketTimeoutException` — the run had been going ~50 minutes and
died silently mid-stream, wasting the tail. Root causes: (1) the per-file receive
loop let one slow page's socket timeout escape and kill `main()`; (2) a
double-escaped newline in a builder had already taught the same lesson — the sweep
harness itself had the non-resilient shape. This skill exists so that never
happens again.

## Rules

1. **Per-file try/except, ALWAYS.** The unit of work is one file; a timeout,
   socket error, or parse failure on one file must become that file's FAIL row —
   never an exception that unwinds the whole run.
2. **Log to a file, stream progress.** Redirect stdout to a log you can `tail`
   while it runs (`> /tmp/sweep.log 2>&1`). A 10-minute sweep you can't watch is
   a black box; a 2-hour one without `flush=True` progress lines is a guess.
3. **Background launch returns control.** On Git Bash, `cmd > log 2>&1 &` then
   poll with `tail`/`grep -c "PASS|FAIL"` — don't hold the foreground for the
   whole sweep.
4. **Resume from the crash point.** If it does die, find the LAST logged unit in
   the deterministic iteration order and re-run from THERE, not from zero. The
   remainder is usually a tiny fraction of the work.
5. **Deterministic order = resumable.** Iterate the file list in sorted order;
   random/shuffled order makes resume-from-crash-point impossible.
6. **Basename pitfalls.** Files with duplicate basenames across directories
   (`graph.html` ×4) collapse under set-dedup-by-basename — match by FULL PATH,
   or count conservatively and say so.
7. **Windows path gotchas.** Native `python` cannot see Git Bash's `/tmp` — use
   `cygpath -w /tmp/...` or the `C:\Users\...\AppData\Local\Temp` form.
   Heredoc regexes with `\d`/`\n` get mangled by shell layers — prefer raw
   strings + `PYTHONIOENCODING=utf-8` (emoji in logs breaks cp1252 stdout).
8. **Expected runtime > your timeout = background.** Estimate per-file cost ×
   count up front. 2,700 × 1.4s ≈ 60+ min — never run that in a blocking call.

## Sizing before you start

```python
# count the scope and estimate — then pick foreground vs background
files = [...]            # the full list
per_file = 1.4           # seconds, from a 50-file pilot
print(f'estimated {len(files)*per_file/60:.0f} min')
# > 10 min → background + progress log + resume plan
```

## Also see

- `pre-action-gate-lite` — Gate 0c routes batch/long-run actions to this skill's LONG-RUN GATE.
- `html-render-verification` — the CDP harness this discipline applies to.
- `corpus-reference-integrity` — another sweep-shaped task (fast: pure regex).
- `aoa-kali-arm` (#1247) — long WSL tool sweeps are a natural fit for the
  background + resume discipline.