# BRIEF — kilo: build the cross-host half (POSIX, 3.16t) and integrate what the critique accepts

**Lane:** kilo (build). **Pinned HEAD:** `7e337913` on `azazael-intel-ultra-9-evo`.
The pin is advisory — re-derive with `git log --oneline -5` and `git status --porcelain`
before you act. **This brief is the sole execution authority for the kilo build.** The
opencode critique brief (`docs/BRIEF_OPENCODE_CRITIQUE_2026-11-05.md`) is a *foreign* brief:
read its document when it lands to know what to build, but do not execute its critique items.

## What exists (measured, not remembered)

`7e337913` landed ten guards in `src/HYPER_EDGE/{kernel,mutate,dream,microcode,cli}.py`,
`tools/ctypes_restype_audit.py`, a `leg_kernel` row in `tools/deep_dive.py`, and three
readings under `ARC/cain/`. The proof state on **win32** at that commit:

```
cli selftest                      33 check(s), 0 failed, 0 skipped      exit 0
pytest tests/test_hyper_edge.py   32 passed in 0.83s                   exit 0
cli kernel --workers 4 --work 0.08   par 2.68 of 4, NATIVE-WITH-PARITY  exit 0
cli kernel --baseline <fake 9.0>     par 2.69 < 6.30, regressed        exit 1
optimize --env windows,wsl,kali,rc   4 converged, concurrency unjudged exit 0
ctypes_restype_audit --strict       1173 file(s), 0 finding(s)         exit 0
ctypes_restype_audit --self-test    caught=True declared_clean=True    exit 0
deep_dive --forensics               verdict: PASS, kernel leg 0.27s    exit 0 (39.1 s)
```

Every number above is win32. **That is the gap this brief exists to close**, and it is
named in the RC doc's Part XI as a limitation rather than papered over.

## Deliverables — five, in this order, each with its own acceptance command

### D1 — POSIX identity, measured where it runs

`kernel.file_identity` grew a `stat` branch (`source: "stat"`, dev+ino) and `kernel.thread_cpu`
a `RUSAGE_THREAD` branch, both untested on a real Linux host this session. On WSL2 or Kali:

```bash
PYTHONPATH=src python -m HYPER_EDGE.cli kernel --workers 4 --work 0.08 --write-baseline
```

Acceptance: the JSON proof shows `"platform": "linux"`, `"source": "stat"` on every identity
row (never `"win32"` or `"absent"`), a `par_ratio` > 1.0, and `faults: []`. Record the exact
`par_ratio` and worker count in your status row — a `par` of 1.0 on a 1-core container is a
true result about the box, not a pass about the code, and must be labelled as such.

**Write the baseline only on the host you measured it on.** `--write-baseline` on Linux
overwrites a win32 reading; name the file per-host instead
(`ARC/cain/hyper_edge_kernel_baseline_<platform>.json`) and leave the win32 one intact, or
the next Windows run compares itself to a different machine and calls it a regression.

### D2 — 3.16t: measure it, or name the blocker precisely

There is **no 3.16 interpreter on this box** (production is `C:/Azazael/.venvs/py315t`,
3.15.0rc3 free-threaded). If you can build or locate one:

```bash
<py316> -c "import sys; print(sys.version, sys._is_gil_enabled())"
PYTHONPATH=src <py316> -m HYPER_EDGE.cli kernel --workers 8 --work 0.08 --write-baseline
```

Acceptance: a proof JSON with `"python": "3.16…"`, `"gil": false`, `workers: 8`, and a
`par_ratio` — plus the baseline written under a 3.16-specific name. Then run the selftest and
the 32 tests under 3.16 and report both. If the interpreter cannot be obtained, the deliverable
is a **blocker note**: the exact failure (download source, build error, missing wheel, disk
space), the command that produced it, and what it would take — not a claim that 3.16 is "fine
by construction". A guard that has never executed on the target interpreter is untested, and
untested is not a pass.

### D3 — the `unbound` legacy ledger entry, resolved

`cli patches` prints `1 bound, 1 unbound`. The unbound row predates binding and can never be
verified. Choose one and implement it:

- **backfill by replay** — re-apply the patch in a scratch policy, let `mutate.apply` record the
  identity, confirm the resulting policy equals the live one, then write the bound row; or
- **quarantine** — mark it `legacy-unverifiable` in the ledger with the date and the reason, so
  `chain()` reports it as classified instead of as a hole.

Acceptance: `cli patches` exits 0 with `0 unbound` **or** prints the quarantine line naming the
entry; the choice and its command go in your status row. Do not delete the row — an erased
ledger entry is worse than an unverifiable one.

### D4 — integrate the accepted adaptations

When the opencode critique lands (`docs/OPENCODE_CRITIQUE_2026-11-05.md` or whatever path its
status row names), build the ones it *endorses* and this brief does not forbid. My own ranking,
so you can start before the critique arrives:

1. **Doubled identity** (content hash alongside `FILE_ID_INFO`/dev+ino, two agreeing sources).
   Cheapest real gain: defeats inode reuse after delete, which `kernel.py` already documents as
   a known weakness. Touches `kernel.file_identity`, `mutate.apply`, `dream.binding`.
2. **Heartbeat lease** (mtime refresh + reclaim when stale) — turns a crashed holder from a
   permanent block into a reclaimable one. Touches `kernel.acquire/held/release`.
3. **Coverage arithmetic** (a decision that used only `record`-grade ops is refused, not just
   labelled) — the label is information; the refusal is a guard. Touches `microcode.evaluate`,
   `cli`.

Skip until measured: derived par ceiling (needs a serial-fraction model that survives a
1-core box) and content-addressed converge files (a migration of an existing reading for a
failure that the one-shot alarm already catches). Say which you skipped and why.

Acceptance per adaptation: the 32 existing tests still pass, a **new** test asserts the
adaptation's specific failure, and a negative control shows the old code failing the new test
(state how you ran the negative control: stash, or a temporary copy — never by editing the
test to pass).

### D5 — close with the durable artefact set

- protobuf-equivalent: JSON artefacts only, under `ARC/cain/`, named per host.
- `python tools/head_state.py --write` is **not** yours to run (shared state); the freebuff
  lane owns it.
- One `lane.kilo.status` row naming: every deliverable, its command, exit code, and the line
  it printed. Read the row back.

## Turf, forbidden list, proof bar

- **Allowlist:** `src/HYPER_EDGE/*.py`, `tools/ctypes_restype_audit.py`, `tools/deep_dive.py`,
  `tests/test_hyper_edge.py`, `config/{microcode,defaults}.json`, `ARC/cain/hyper_edge_*.json`,
  `docs/HYPER_EDGE_ENGINEERING_RC_2026-11-05.md` (append a Part XII; do not rewrite Parts I–XI
  — they are measurements taken at `7e337913` and their numbers are provenance).
- **Forbidden:** other lanes' dirty files; `MANDATES.md`, `SOP.md`, `SYSTEM_INSTRUCTIONS.md`
  (canon ownership — `git status --porcelain -- MANDATES.md SOP.md` first); `tests/` fixtures
  outside `test_hyper_edge.py`; `git add -A`; rebaselining a scanner finding; a suppression in
  a test file (repair structurally).
- **Shared index:** ~80 modified / ~114 untracked files belong to other lanes. Stage ≤8 explicit
  paths. `.githooks/pre-commit` takes ~3 minutes — commit in the background to a log and poll
  `git log`, never with a 30 s timeout that reads as failure while the hook is still running.
- **Bulk gate:** >8 staged files or >150 changed lines per file blocks. A bulk *operation*
  declares `ALLOW_BULK_COMMIT=1` in the message and says why; it is never a silent bypass.
- **Interpreter:** `C:/Azazael/.venvs/py315t/Scripts/python.exe` on Windows; bare `python` is
  3.14.7 GIL and its numbers are not evidence about production.
- **Run form:** from `C:/Azazael/azazael`, `PYTHONPATH=src <py> -m HYPER_EDGE.cli <cmd>`.

## ERROR CAPTURE (mandatory, #714/#716)

Record every error, near-miss and falsification at ENCOUNTER TIME into
`state/bake_harvest_kilo_<date>.jsonl` with schema `{source, item_id, title, body, kind}`;
body ≥ 40 chars; kinds: `error_fix | lesson | mandate | sop_rule | violation | anti_pattern`.
Do not defer to session end. Validate: `tools/merge_bake_lane.py --lane <file> --apply`.

**Definition of done:** D1 and D3 measured with commands quoted; D2 either measured under a
real 3.16 interpreter or blocked with the exact failure; D4 built for the accepted subset with
its new tests; D5's status row read back. A deliverable that could not be performed is
reported as `BLOCKED` with its command — never as done.
