# HYPER-EDGE-DEFAULTS-v1 — the practice that runs without being asked

**Canonical source.** Generated into every lane's instruction file by
`tools/agent_orders_sync.py`; the MCP gate fails (`orders-in-sync`) when a copy
drifts. Edit this file, never a copy.

A best practice that depends on someone remembering it is not a practice, it is
a hope. These eight are the ones this tree has actually paid for, each with the
command that proves it and the failure that bought it.

### HED-1 — Verify by running, never by importing

Months of import sweeps missed a live `NameError` (`src/CORE/langgraph_integration.py`,
`TypedDict` undefined) because nothing imported the module. An import check
answers "does this module raise at load time". A test answers "does this
behaviour hold". Only the second one finds defects.

### HED-2 — Every test file, every time, one file per process

```
python tools/golden_arrow.py            # full; on completion runs the deep dive too
python tools/golden_arrow.py --staged   # commit path: only the index's test files
python tools/golden_arrow.py --strict   # recorded debt fails as well
python tools/golden_arrow.py --status   # read the last report, run nothing
```

`python -m pytest -q tests` did not finish inside 600 s twice; the suite was
WEDGED, not slow. One file per process with its own wall bound means a wedged
file is NAMED (`HUNG`) while the other hundreds still report. **A hung file is
never a pass and never a skip** — it is the test whose assertion might have
found the next defect. Recorded failures (`logs/golden_arrow_baseline.json`) are
DEBT: printed every run, failing the gate only under `--strict`, and the list may
only shrink (`--baseline` rewrites it after you pay a file down).

Exit codes are part of the contract: `0` ran and clean of new defects, `1` a new
failure or a hung file, `2` the run could not be performed. **`2` is not a pass**,
and a gate that reports 0 after being unable to run has reported a lie.

`logs/` is gitignored, so the baseline survives a fresh clone only if it is
force-added (`git add -f logs/golden_arrow_baseline.json`), the way
`logs/anti_pattern_baseline.json` is. An uncommitted baseline is a ratchet that
resets on every checkout — and a ratchet that resets reports today's known debt
as today's new breakage.

**A narrower run must not answer for a wider one.** `--file` and `--staged` write
`logs/golden_arrow_file.json` / `logs/golden_arrow_staged.json`; only a full run
owntes `logs/golden_arrow.json`, which is the file the deep dive reads and a
commit message quotes. Measured 2026-11-02: a single-file run overwrote the
full-suite report, leaving a 1-file artifact where a 499-file reading was
recorded — a stale artifact answering for a tree it no longer described.

### HED-3 — AST audit by default

```
python tools/ast_audit.py --root . --out logs/ast_audit.json --label .
```

A file that will not parse is a defect with a name, so the deep dive lifts
`syntax_errors` out of the report and into the verdict. The audit prints
`py=` **and** `parsed=`: reporting one number as if it were the other
under-reported by exactly the syntax-error count (2,817 vs 2,824 on 2026-11-01)
and read as drift between two runs of one tool over one tree. **A reading that
hides its count is a defect in the reading.**

### HED-4 — Deep dive by default: forensics and a bounded web leg

```
python tools/deep_dive.py                 # both legs, from config/defaults.json
python tools/deep_dive.py --forensics     # no network at all
python tools/deep_dive.py --query "..."   # explicit question
python tools/deep_dive.py --offline       # force the recorded fallback
```

A full `golden_arrow` run invokes this as a stage and folds its forensic verdict
into the run's exit code — tests and audits answer different questions, and a
run that answers only the first is the state that let HED-1's `NameError` live.
`--no-deep-dive` turns the stage off for one run.

Web leg rules, all enforced in the tool: **bounded** (`deep_dive.web_timeout_s`,
`deep_dive.max_queries`); **offline is `skipped` with the reason printed** — an
unavailable reading is not a zero and not a pass; **a network failure never fails
the run**, because a gate that fails when the internet is down gets switched off,
and a switched-off gate protects nothing; **a forensic failure always does**.

Providers are a chain, not a hope: Stack Exchange's public API (keyless, 300
calls/day) answers Python-defect questions, then DuckDuckGo's HTML endpoint.
Measured 2026-11-02: DDG answers a scripted query with a 14 KB
anomaly/challenge page containing **zero** `result__a` anchors. The first version
of this leg called that `ok, 0 results` — a **blocked** provider reported as an
empty answer, the exact defect HED-3 names. It is now `blocked`, the leg prints
`hits via stackexchange; blocked: duckduckgo`, and `empty` is reserved for a
provider that actually replied. Four states are recorded and never collapsed:
`ok`, `empty`, `skipped`, `error`.

### HED-5 — One settings surface, and it must show what is OFF

```
python tools/defaults_profile.py             # --show: the live defaults
python tools/defaults_profile.py --set deep_dive.web_search=false
python tools/defaults_profile.py --check     # validates shapes and bounds
```

Settings live in `config/defaults.json` only. Every tool reads them through
`defaults_profile.read_default(key, fallback)` and keeps a module constant as the
fallback, so a missing or corrupt config degrades to shipped defaults instead of
crashing. A default that lives in three tools drifts in three tools. `--show`
prints every default including the ones set to `false`; a silently-off default is
indistinguishable from a deleted gate.

### HED-6 — Robust fallback, never silent success

Each leg of a multi-part run is isolated: it may `ok`, `error`, `timeout` or
`skip`, and every one of those is a distinct recorded state with its reason and
its seconds in `logs/deep_dive.json`. No leg may abort the run; no leg may report
success it did not have. `record-and-continue` is the shipped `fallback.on_error`
for exactly this reason: a run that dies on one broken leg produces no readings at
all, and a run that swallows one produces a false PASS. The middle path is a
recorded failure next to the readings that did land.

### HED-7 — A claim needs its command

`done`, `fixed`, `passes`, `verified`, `in place`, `landed` are claims. Each one
is written with the command that produced it and the line it printed:

- not "all tests pass" but `golden_arrow --staged: 6 files, 0 new defects`
- not "the gate is wired" but the gate's own output naming the block it checked
- not "deep dive clean" but `verdict: PASS  forensic legs ok, web skipped (offline)`

A claim without a command is a recollection, and a recollection is what HED-1
already caught costing months.

### HED-8 — Extend the default, do not shadow it

A new check joins the deep dive as a **leg** (bounded, isolated, recorded) and a
new knob joins `config/defaults.json`. It does not get its own constant in a
third file, its own private timeout, or its own exit code that only it returns.
A practice that exists in one tool and not in the canon is a practice the next
session will re-derive — which is the whole cost these eight rules exist to stop
paying.

### ONE CLICK — the defaults have a single front door

```
ONE_CLICK.cmd                 # double-click, Send-To, shortcut, scheduled task
python tools/one_click.py     # --fast (staged) | --no-web | --json <path>
```

Three steps, in order, each a bounded child process: the stack gate, every test
file, then the deep dive. A step that fails does **not** stop the next one — a
red stack and a red suite are usually unrelated facts, and stopping at the first
one makes the operator run the command three times to learn three things. Verdict
is one line and one file (`logs/one_click.json`): `PASS`, `FAIL` (naming the
step) or `BLIND` (a step could not be performed — missing tool, no interpreter).
`BLIND` is its own verdict because "could not run" is neither a pass nor a
failure; it is the state to fix first.

A double-click is one click. `--fast` runs only the index's test files and says
so when the index is empty rather than narrowing silently.

**Verify this block:**
`python tools/agent_orders_sync.py --check && python tools/defaults_profile.py --check`
