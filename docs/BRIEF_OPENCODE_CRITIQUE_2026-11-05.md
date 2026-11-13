# BRIEF — opencode: critique + paradigm-shifting adaptations of the HYPER_EDGE guards

**Lane:** opencode (critique only, no implementation in this brief)
**Pinned HEAD:** `7e337913` on `azazael-intel-ultra-9-evo` ("Guard the HYPER_EDGE kernel layer
against quiet degradation", 13 files, +821/−28). The pin is advisory: re-derive first with
`git log --oneline -5` and `git status --porcelain` before you trust a line of this brief.
**This brief is the sole execution authority for the opencode critique.** Every other brief
touching HYPER_EDGE is foreign to it; do not execute kilo's build items.

## What landed, and why it is a guard rather than a feature

Ten followups landed in `7e337913`. Each one exists because a measurement could previously
report success while being wrong — the same shape as the three silent failures of 2026-10-30
(a stale supervisor child, a nonce scoring 0.644 against a 0.62 floor, six double-bound
proxies). Read them as claims to attack, not as work to admire:

| # | guard | the failure it is meant to make visible | where |
| --- | --- | --- | --- |
| 1 | patch↔artefact binding | a ledger says "patch applied" while the file at that path is a different file | `mutate.apply`, `mutate.chain().artifacts` |
| 2 | POSIX identity + `RUSAGE_THREAD` | a Windows-only identity call is silently absent on WSL/Kali, so "verified" means "not checked" | `kernel.file_identity`, `kernel.thread_cpu` |
| 3 | `leg_kernel` in the deep dive | the kernel layer's own proof never runs in the default battery | `tools/deep_dive.py`, `config/defaults.json` |
| 4 | serial-optimize detection | 4 workers report "converged in 1.1 s" while one thread does all the work | `mutate.optimize` `concurrency` block |
| 5 | `acquire`/`held`/`release` lease | two `optimize` runs interleave writes to one policy file and both "succeed" | `kernel.acquire` |
| 6 | dream artefact binding + `stale_dropped` | a dream graded against a control that has since changed is replayed as current evidence | `dream.binding`, `dream.replay` |
| 7 | par baseline | today's parallelism is compared to nothing, so a regression reads as a number | `kernel.compare_baseline`, `cli kernel --baseline` |
| 8 | `EVIDENCE_GRADE` per op | an op that can only ever reach `record` is counted next to one that reaches `kernel` | `microcode.EVIDENCE_GRADE`, `cli isa` |
| 9 | `ctypes_restype_audit` | a `HANDLE` returned as `c_int` truncates on 64-bit and the failure surfaces far away | `tools/ctypes_restype_audit.py` |
| 10 | stale-converge guard | a converge record for an older corpus is quoted as today's proof | `mutate._converge_record`, `ARC/cain/hyper_edge_converge.json` |

## What this lane is asked for — two passes, both written, both with commands

### Pass A — attack each guard (a critique, not an endorsement)

For **each** of the ten, answer three things in one row of a table:

1. **the residual failure** — what wrong answer still gets through, described concretely
   (state, not adjective). If you believe there is none, say what makes it impossible.
2. **a reproduction or a reason you cannot build one** — a command that shows the residual
   failure, or the named obstacle (needs a second host, needs a 3.16 interpreter, needs a
   filesystem that reuses inodes). "I could not construct one" is a valid finding; it is not
   a pass, and it must not be written as one.
3. **the least-severe repair** — the smallest change that closes it, with the knob it moves.
   A repair that needs a new dependency, a new config file, or a new exit code is not
   least-severe; say so if it is the only option.

Two residuals I already know and have not closed, so you do not have to discover them:

- **`unbound` legacy ledger entry.** `cli patches` prints `1 unbound` — a patch recorded before
  binding existed. It is honest, and it is also a hole: a pre-binding patch is unverifiable
  forever. Decide whether the right answer is backfill-by-replay, a quarantine list, or naming
  it in the ledger as `legacy-unverifiable`.
- **`cpu unjudged` below ~0.20 s.** Four cheap envs total 35 ms of CPU, below the `SERIAL_FLOOR_S`
  where `GetThreadTimes` resolution (~15.6 ms) can distinguish threads at all. The run says
  `unjudged` instead of pretending. The open question is whether a cheap run should be *made*
  measurable (repeat to a floor) or *kept* fast and left unjudged.

### Pass B — paradigm-shifting adaptations

"Paradigm-shifting" here means: a change that removes the need for a guard rather than
sharpening it. Five I believe are real; judge each, then add any you see that I have not:

1. **Derived ceiling instead of a recorded baseline.** Today par is compared to
   `hyper_edge_kernel_baseline.json` (par 2.68 of 4). A baseline is a memory of one machine.
   A *ceiling* is derived per run from the work's serial fraction (Amdahl from the measured
   per-env CPU and wall), so "parallelism regressed" becomes "this run is below its own
   arithmetic bound", which cannot go stale.
2. **Identity from two independent sources.** `FILE_ID_INFO` (or dev+ino) is one answer to
   "same file". A second source — content hash of the artefact — makes re-issue detection
   survive a filesystem that reuses ids (`os.replace` already produces a new id at the same
   path; a filesystem that recycles inodes after delete defeats it, documented in `kernel.py`).
   Two agreeing sources is a proof; one is a hint.
3. **Lease with crash detection, not just exclusion.** `O_EXCL` proves one holder *now*; it
   cannot tell a crashed holder from a slow one, so a stale lease file blocks forever until
   a human deletes it. A holder that must refresh a heartbeat (mtime) turns "blocked" into
   "stale, reclaimable", which is the same one-shot-alarm shape as the converge guard.
4. **Coverage arithmetic for evidence grades.** Right now `grades()` states each op's ceiling.
   The stronger statement is a *ratio*: of the ops a given decision used, how many reached
   `kernel` versus `record`. A decision built only on `record` ops should be refused by the
   engine, not merely labelled — the label is information, the refusal is a guard.
5. **Content-addressed converge instead of a dated corpus.** The converge guard compares a
   corpus hash and marks `stale` once. Keying the record *by* that hash (`converge.<hash>.json`)
   makes staleness unrepresentable rather than detected.

For each adaptation you endorse, state: the failure it removes, the file it touches, the
price (what gets slower or stricter), and the test that would prove it — a test name and the
assertion, not "add tests". For each you reject, state what the guard catches that the
adaptation would not.

## Turf, forbidden list, proof bar

- **Allowlist (yours to name in a repair):** `src/HYPER_EDGE/{kernel,mutate,dream,microcode,cli}.py`,
  `tools/ctypes_restype_audit.py`, `tools/deep_dive.py`, `tests/test_hyper_edge.py`,
  `config/microcode.json`, `ARC/cain/hyper_edge_*.json`.
- **Forbidden:** `tests/` fixtures belonging to other subsystems; `MANDATES.md`, `SOP.md`
  (canon ownership — check `git status --porcelain` before any canon write); every file this
  brief does not name; `git add -A`; rebaselining a scanner finding to get a commit through.
- **Proof bar for any claim:** the command, its exit status, and the line it printed. `passes`,
  `verified`, `in place` are claims, not evidence. A claim without a command is a recollection.
- **Shared index:** this worktree carries other lanes' edits (~80 modified, ~114 untracked).
  Stage by explicit path, ≤8 files, never `-A`.
- **Interpreter:** `C:/Azazael/.venvs/py315t/Scripts/python.exe`. Bare `python` is 3.14.7 with
  the GIL — measurements taken with it are not evidence about production.
- **Run form:** from `C:/Azazael/azazael`, `PYTHONPATH=src <py315t> -m HYPER_EDGE.cli <cmd>`.

## ERROR CAPTURE (mandatory, #714/#716)

Record every error, near-miss and falsification at ENCOUNTER TIME into
`state/bake_harvest_opencode_<date>.jsonl` with schema `{source, item_id, title, body, kind}`;
body ≥ 40 chars; kinds: `error_fix | lesson | mandate | sop_rule | violation | anti_pattern`.
Do not defer to session end — reconstruction loses detail and over-weights what is still
salient. Validate: `tools/merge_bake_lane.py --lane <file> --apply`.

**Definition of done for this brief:** a critique document with ten rows (Pass A) and an
adaptation table (Pass B), every claim carrying its command, the two known residuals judged
rather than restated, and a `lane.opencode.status` row naming the document path.
