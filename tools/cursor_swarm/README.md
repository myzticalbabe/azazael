# cursor_swarm — a swarm of WORKER cursors that build a site, or none of it does

**This is not the arena.** `tools/swarm_arena/` is a different project: it judges
candidate texts against each other with three language shards (Rust, Go, Python)
and an Elo board. Nothing here reads it, and nothing in it reads this. The two
share a subject, not a codebase.

A **worker** is an agent that takes a *scope* of files, *reads* them, *reports*
what it found, and *lands* a layer of the site. A **judge** is an agent that
scores one candidate against another and lands nothing. The video this project
is drawn from shows the first kind: agents building a page, each one visible as
a coloured mouse cursor.

## Run

```bash
python tools/cursor_swarm/swarm.py --make-plan --scope src/CORE --workers 72 \
    --out tools/cursor_swarm/plan_workers.json
python tools/cursor_swarm/swarm.py --plan tools/cursor_swarm/plan_workers.json \
    --ledger tools/cursor_swarm/worker_frames.jsonl \
    --attempts tools/cursor_swarm/worker_attempts.jsonl \
    --out tools/cursor_swarm/out/swarm_site.html
```

Then open `tools/cursor_swarm/out/swarm_site.html`. It is one static file — no
server, no fetch — so a desktop and a headless Chrome render the same pixels.

Exit codes: **0** the swarm landed · **1** a worker was red and the swarm rolled
back · **2** the swarm could not run (bad plan, scope outside the index, missing
import). 2 is not a pass.

## The three properties

**Cursor-local.** A worker's verdict is about the files *that* worker touched,
not about the repository. The auditors in this tree answer whole-tree
questions, so their per-file callables are **composed** here rather than their
CLIs re-implemented:

| check | composed from | red when |
|---|---|---|
| `parse` | `ast.parse` of every file in the scope | a file in the scope will not parse |
| `settings` | `settings_shadow.readers_in` + `.bypasses_in`, per file | the scope reads an undeclared key, or hand-parses the shared config |
| `reading` | the layer the worker produced | the layer carries no denominator over its scope |
| `scope` | one `git status --porcelain` over the scope | a file in the scope is dirty (that is `held`, not red) |

**Transactional.** Every worker's layer lands, or none does. A rolled-back swarm
writes its rows to an *attempts* file and leaves the canonical ledger
untouched — the ledger is inside the transaction, because a ledger claiming work
that does not exist is the one artifact everything else is built on.

**Measured.** The verdict phase is timed on every run, against a *real* serial
baseline (a second sweep at one thread), and the speed-up is the quotient of two
measured wall times. The sub-second claim is a number this run produced.

## The ledger

The dialect is the tree's, not a new one: the four verdicts
(`landed` / `held` / `rolledback` / `quarantine`) and the hash rule
`tools/claim_agreement.py` enforces — the sha256 of the canonical JSON of every
key the row carries, chained through `prev_hash` from `"GENESIS"`. A row that
does not recompute is quarantined and never drawn.

Rows carry an optional `ts` (epoch ms) so the pulse can compute an age; the
A8 audit (§2.4) checked the design's proposal to restrict the hash to the
canonical eight keys and found it backwards, so the hash covers `ts` too and the
column is authenticated. Old eight-key rows stay valid.

`tools/claim_agreement.py` finds this ledger as its second candidate, after the
live one in the user's home directory.

## The view

Three layers, all read from the ledger rather than invented:

* **colour** — `monitor_theme.SEMANTIC`, imported not copied. `held` has its own
  slot: `warn` and `advisory` share a hex, so a cursor held mid-flight used to
  render exactly like a warning.
* **tracer** — four dots per worker, `placed → verified → applied → settled`,
  which the ledger already carried and the v0 view never showed.
* **pulse** — a follower element whose opacity is keyed to the row's age, with
  `pointer-events: none`. It is never the OS pointer: `cursor: url(...)` accepts
  only non-animated formats, so a pulsing glyph cannot be the pointer.

The page prints its own denominator and a self-test line computed from the live
DOM — `hotspot_misaligned` is the count of cursors whose *tip* (not their
corner) drifted from the node they claim, and `CHAIN` is `MISMATCH` when that
count is non-zero or the slowest cursor exceeds the budget.
