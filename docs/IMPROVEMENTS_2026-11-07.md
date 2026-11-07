# IMPROVEMENTS — 2026-11-07 (deep dive: every item measured, ranked by failure removed per unit price)

Every item names the measurement that justifies it. Nothing here is a
preference: each is a failure observed this session, or a defect visible in a
cited line. Ranked by (failure removed) / (price). Items marked LAND are small
enough for one green commit; items marked QUEUE need a lane session.

## L1. Gate layer

**L1-a LAND — the gate tests a process name, not the behaviour it cares about.**
`tools/mcp_startup_gate.py` reports `[BLOCKED] pams-running pams_server_launcher.py
is not running`, while the same session's `session_start.py` printed
`pams capture open>stored message_id=6c1fa7ac-...` twice — the capture path
works with no launcher process. The floor-proxy check already solved this shape
with a differential (behaviour, not config). Apply the same: `pams-capture`
should attempt one small write+read through the capture path and PASS on
success, BLOCKED only when the write fails. Price: ~25 lines + 2 tests.
Failure removed: a gate that says "down" while the thing it gates is up trains
lanes to ignore it.

**L1-b LAND — BLOCKED has no in-session contract, so each session re-derives
one.** Tonight's restart rows 47752/47754 had to spell out "degraded path: use
the supervisor fallback, record the gap". Make the gate print it:
`DEGRADED: memory reads trusted; recall answers suspect; commit gate expects
supervisor verdict -> rerun after restart`. Price: ~10 lines of constant text.
Failure removed: every lane inventing a different definition of "still safe".

**L1-c QUEUE — `supervisor-fresh` should name whether *this* session edited the
script.** It already prints mtime deltas (pid 9324 @ 12:48:58 vs edit 23:13:53).
Adding `edited_by=this_session` when the edit falls inside the session window
turns a BLOCKED into an explained BLOCKED, and tells the next reader the fix is
already on disk.

## L2. Interpreter / runtime layer

**L2-a LAND — py316t has no editable-install `.pth`.** Measured:
`py316t -m eve_unleashed.cli` -> `ModuleNotFoundError: No module named
'eve_unleashed'`; `PYTHONPATH=src` -> green. py315t carries
`__editable__.azazael-1.0.0.pth`. Run the editable install (or drop the same
`.pth`) under py316t so startup and `-m` invocations agree. Price: one command.
Failure removed: a new interpreter whose module invocations silently differ
from the old one.

**L2-b QUEUE — prove the suite, then move the hook.** `head_state.py --write`
under py316t collected 7,220 tests (state/head.json), so collection works there;
nothing yet proves *execution* under 3.16. Run `tools/golden_arrow.py` with the
py316t interpreter, compare against the recorded baseline, and only then move
`.githooks/pre-commit:69 PYTHON3`. Do not move the hook before this — a hook
that runs untested interpreter semantics gates every commit in the tree.

## L3. Testing layer

**L3-a LAND — live tests are deselected by name, five times over.** `cli.py
cmd_e2e` carries five literal `--deselect tests/test_eve_websearch_challenge.py::...`
arguments; the same five names must also be kept in step by any future caller.
Declare `@pytest.mark.live` on them and call `-m "not live"`. Price: 5 decorators
+ one pytest.ini line + one flag. Failure removed: a rename silently un-deselects
a network test into the deterministic path.

**L3-b QUEUE — the e2e command should exercise one live rung by default.** It
skips live fetch unless `--live-url`; tonight's proof of rings 6–8 came from
manual invocations, not from e2e. A keyless, always-up target (example.com)
makes e2e prove the ladder's first rung on every run. Price: one extra phase,
bounded by `_TIMEOUT`.

## L4. Cognition layer (the 8 named gaps)

Order by evidence already in hand — each of these can be measured with today's
live log, no new instrumentation.

**L4-a LAND — inhibition**: a rung that keeps failing for a host is skipped
next time. `intuition.intuit` already computes per-host answer rates; the
ladder ignores them. Price: ~20 lines in websearch + 2 tests (3 failures ->
rung suppressed; 1 failure -> not suppressed).

**L4-b LAND — salience**: weight events by outcome, not recency. `dream()`
counts pairs; nothing weights `state=blocked` above `state=ok`. Price: ~15 lines.

**L4-c QUEUE — consolidation**: merge repeated episodes into one rule while
idle (the "dream" that turns 40 identical `plain` answers into a single prior
statement). Needs a write target in memory; PMB `record_fact` is the obvious one.

**L4-d QUEUE — prospective-memory, priming, incubation, counterfactual-replay,
affect**: named and unbuilt; listed here so the gap stays visible. Do not build
them speculatively — each needs a failure it removes.

## L5. Board / lane layer

**L5-a LAND — a claim lease that expires silently looks like "no work".**
`stats` prints `claimed_expired: 4` tonight with no owner named. Add
`_board.py stale [lane]` printing rows whose lease expired and by whom, so a
dead lane's work is visible instead of quietly re-offered. Price: ~15 lines.

**L5-b QUEUE — critique rows have no closure obligation.** Rows 47757/47759 ask
for critique "as critique rows"; nothing requires an answer or retires the row.
Make the restart instruction name the *expected reply row format* and a
`retire-after` date, and have `stats` surface age.

## L6. Instruction / canon layer

**L6-a LAND — the drift tool exists and the gate does not call it.**
`tools/head_audit.py` (HED-12) already compares lane file digests against
`state/head.json`; `mcp_startup_gate.py` runs `orders-in-sync` only, which
compares generated blocks to their source, not lane files to the last measured
digest. Add head_audit as a WARN-level line in the gate. Price: one subprocess
+ parse. Failure removed: a lane obeying bytes nobody re-read.

**L6-b — the expiry rule is prose.** `state/head.json` carries `written_at`; make
`prompt_check.py` print `head.json is N hours old (expiry 72h)` so staleness is
read, not remembered.

## L7. What NOT to do (measured this session)

- Do not move the test-suite or hook interpreter before L2-b is proven.
- Do not build the remaining cognition gaps speculatively; each needs a failure.
- Do not sweep untracked paths another lane left (`dist-native/`,
  `.worktree-snapshots/`, `nul.a.*.o`) — attribution first, cleanup second.
- Do not read `def main` twice in `supervisor_mcp.py` as a duplicate: the first
  two matches are inside `TOOL_TEMPLATE`, a string. (Checked, false alarm.)

## D. Deep dive, measured tonight (`tools/deep_dive.py --forensics`, 64.6 s)

`verdict: FAIL`. Four of five legs ok; one leg errored. The failures below are
ranked by what they actually cost, not by which tool printed them.

**D1 — `evidence_gate` FAIL: the mesh ledger cannot prove a rotation.**
Leg output: `RuntimeError: evidence_gate exited 1: no successful rotation is
recorded; that is absence of evidence, not evidence that credentials are
fresh | GATE: FAIL -- ledger_freshness`.
`tools/evidence_gate.py:456 check_ledger_fresh` shells out to
`mesh_function_preflight.py --check` and fails on any `STALE` token. So the
gate is honest and the ledger is empty. Two repairs, pick one deliberately:
(a) record one rotation event through the existing writer so the ledger has a
first row, or (b) declare the dimension unmeasured (`status: skip` + reason)
until a rotation path exists. Currently it does neither, so every deep dive
FAILs on it and the FAIL becomes noise. Price: one writer call or one status
change. Failure removed: a red verdict nobody can act on.

**D2 — the anti-pattern ratchet disagrees with the tree it ratchets.**
`golden_arrow --status`: `FAIL tests/test_anti_pattern_gate.py (rc=1) --
NOT in the baseline`, specifically
`TestCommittedBaseline::test_baseline_agrees_with_a_live_scan`. The committed
`logs/anti_pattern_baseline.json` is also dirty in this worktree. A ratchet
whose self-check fails is a ratchet that cannot hold: either regenerate the
baseline deliberately (`--baseline`, with the diff read) or fix the findings
that made it drift. Do not silence the test.

**D3 — five failing files, none in the baseline.** `test_anti_pattern_gate.py`,
`test_cain_obsolescence_cli.py`, `test_cain_obsolescence_mark.py`,
`test_preflight_all.py` (166 s), `test_session_mappings.py`, plus 1 KILLED file
with no verdict. These are other lanes' turf; the improvement is procedural:
`golden_arrow` should print the owner lane (from the path) beside each FAIL so
the row goes to a lane instead of to a reader. Price: ~15 lines mapping
path prefix -> lane.

**D4 — 3,813 orphan modules.** `ast_audit`: `5632 .py parsed, 0 syntax error(s),
114 bare-except, 3813 orphan module(s)`. Zero syntax errors is the good half.
The 114 bare-except are single-statement suppressions the scanner already
tracks (`scanner.py:487`); the 3,813 orphans are a much larger question and
should NOT be swept in one pass — they are the reason `wired` claims needed
T1–T4 tiers in the first place. Proposal: one report that lists orphans by
directory with a count, so the tree's shape is visible without a 3,813-row wall.

**D5 — four worktree heads live only in the reflog.** `head_audit`: 16 gaps.
Reclaimable today: `git worktree prune` clears 3 prunable registrations
(`Temp/headcheck`, `Temp/kilo/baselinewt`, `Temp/opencode/headwt`). NOT
reclaimable without a decision: the 4 orphaned heads in those same Temp dirs
(`324ce549`, `c7caa606`, `ed3f0e9f`, +1) are in no ref and `git gc` will take
them. Adopt by ref or drop deliberately — never leave them to gc.

**D6 — four verdicts with no denominator.** `reading_audit`:
`esquire_capture.json` (CLEAN), `hook_evidence.json` (PASS), `one_click.json`
(PASS), `pin_audit.json` (CLEAN) — `denominator_free`, already known since
HED-9's first run. A verdict with no count cannot be audited; each needs one
line saying "N of M".

**D7 — one knob, three reader names.** `settings_shadow`: 33 leaves, 33 read,
0 findings, but three vocabularies: `get_default`, `read_default`, and local
wrappers `_profile`/`_setting`/`setting`. HED-5's rule is one surface; three
wrappers are how a fallback drifts silently. Price: collapse the wrappers onto
`read_default`. Failure removed: a knob that reads differently in three tools.

**D8 — the golden arrow report is five days old.** `golden_arrow_status:
537 file(s) ... (run 2026-11-05T14:34:46Z)`. Tonight's Eve slices were
verified with `mend verify` (49/49) and targeted pytest, not the full arrow.
The improvement is not "run it more": it is that `mend verify` should write its
scope and timestamp where `golden_arrow --status` can read it, so a reader can
tell a 5-day-old full run from tonight's targeted one instead of assuming the
worse of both.

### Order I would actually work in

1. D2 + D3 baseline decision (unblocks the whole ratchet).
2. D1 one decision on ledger_freshness (turns a red leg green or honestly skipped).
3. D5 worktree prune + the four head decisions (cheap, then gc is safe).
4. L1-a pams behavioural check, L1-b DEGRADED line (gate stops lying and stops
   being re-derived).
5. L4-a inhibition, L4-b salience (the two cognition gaps with evidence in hand).
6. D7 wrapper collapse, D8 scope stamp (drift and staleness, both cheap).
