# CURSOR SWARM v1 — workers, not judges

**Date:** 2026-11-15 · **Lane:** opencode · **Supersedes:** nothing; extends
`docs/CURSOR_SWARM_A8_DESIGN_2026-11-13.md` and answers
`docs/CURSOR_SWARM_A8_AUDIT_2026-11-14.md`

---

## 0. The topic, and where it came from

The TikTok video open in Firefox at the start of this session was
<https://www.tiktok.com/@leos.logos/video/7704853939681873165> — *"A website
built itself live — 72 AI agents, each shown as a coloured mouse cursor"*.
Its own narration, read off the frames:

> this website built itself live — and every [agent is a] mouse cursor · in
> Harshit's video, a swarm of AI agents assembles his portfolio on screen, each
> one shown as a cursor · watch the counter at the bottom · ten agents early on,
> seventy-two by the end · through nine hundred and twenty-two layers · the
> same idea showed up in another post today — a proof of concept · a site
> called Swarm promises the same thing · a thousand agents, run as one · one
> agent edits a file · a swarm builds the whole thing while you wait

The topic is therefore: **many agents, each one visible as a coloured mouse
cursor, collectively building a page live, with verdicts that arrive fast.**

The video names its own source: <https://github.com/califa/swarm-site>
("a website that builds itself as you scroll"), and a Rust proof of concept
posted the same day. Both are the same idea in a different substrate.

## 1. The reorientation (this is the part that was wrong first)

The first reading of this task put the work inside `tools/swarm_arena/`, next
to the judge shards. **That was the wrong project.** `tools/swarm_arena/` is a
blind pairwise *judging* rig: three language shards score candidate texts
against each other, a majority decides, an Elo board ranks them. A worker does
not score candidates — a worker *does the work*, reads a scope, reports what it
found, and lands a layer.

The tree already draws the line. The v0 ledger's stages are
`[placed] → [verified] → [applied] → [settled]` — a worker's lifecycle, not a
judge's score. The A8 design's own `Cursor` struct carries
`mutation: Option<Mutation>` — *the edit, held until the gate passes*. A judge
has no mutation.

So this project lives in `tools/cursor_swarm/`, imports nothing from
`tools/swarm_arena/`, and the pointer glyph is a plain mouse arrow authored in
this project rather than the arena's Vulcan salute. Two subjects, two
codebases.

## 2. What was built

| piece | where |
|---|---|
| the worker swarm: plan, cursor-local verdicts, transaction, ledger | `tools/cursor_swarm/swarm.py` |
| the live site: coloured cursors, tracer, pulse, self-test | `tools/cursor_swarm/swarm_site.py` |
| the plan: 72 workers over `src/CORE` | `tools/cursor_swarm/plan_workers.json` |
| the ledger this run produced (288 rows) | `tools/cursor_swarm/worker_frames.jsonl` |
| the project doc | `tools/cursor_swarm/README.md` |
| the tests | `tests/test_cursor_swarm.py` |

Three properties, each of which the v0 did not have:

**Cursor-local.** A worker's verdict is about the files *that* worker touched.
The auditors in this tree answer whole-tree questions, so their per-file
callables are **composed** — the A8 audit's correction of the design's
"extract a `read_scope`" step (`readers_in` and `bypasses_in` already exist and
per-file work; the win is composition, not extraction).

**Transactional.** Every worker's layer lands or none does, and the ledger is
*inside* the transaction. The audit's P0 finding was that a rolled-back swarm
left the ledger claiming work that did not exist; a red swarm now writes its
rows to `worker_attempts.jsonl` and leaves the canonical ledger untouched.

**One dialect.** The rows are the tree's rows: the four verdicts
(`landed`/`held`/`rolledback`/`quarantine`) and the hash rule
`claim_agreement.validate_ledger` enforces. The swarm's rows are readable by
the tree's own validator, unchanged — `tests/test_cursor_swarm.py` pins that.

## 3. Measured

Interpreter `C:/Azazael/.venvs/py316t/Scripts/python.exe` (3.16.0a1,
`Py_GIL_DISABLED`), repo `C:/Azazael/azazael`, branch
`professional-public-standards-rule-0z-r`.

```
$ python tools/cursor_swarm/swarm.py --plan tools/cursor_swarm/plan_workers.json \
      --ledger tools/cursor_swarm/worker_frames.jsonl \
      --attempts tools/cursor_swarm/worker_attempts.jsonl \
      --out tools/cursor_swarm/out/swarm_site.html
workers: 72  landed: 72  held: 0  rolledback: 0
verdict phase: 1756 ms wall (serial 5014 ms, speed-up 2.86x, 16 threads)
per-worker: min 1.2 ms  median 309.2 ms  max 1230.9 ms  (n=72)
per-module: 5.1 ms of the verdict phase across 343 module(s)
schedule: 8 ms stagger, slowest 868 ms of a 900 ms budget
ledger: ...\worker_frames.jsonl (288 rows, last f3d8dc7087cf)
ledger validate: 288 row(s), 0 bad
```

The page's own self-test, read out of a headless Chrome render of the emitted
file (`chrome --headless --dump-dom`, not asserted by hand):

```
SELFTEST: workers=72 layers=72 landed=72 held=0 rolledback=0 quarantine=0
quarantine_strip=0 hotspot_misaligned=0 slowest=868ms budget=900ms CHAIN=OK
```

Scope census for the 343 modules under `src/CORE`, measured independently:

```
declared keys: 91 | reader vocab: 3 from config/defaults.json
files=343 reads=15 undeclared_reads=0 bypasses=0 unparseable=0
read only        :    27.8 ms
read + ast.parse :   572.3 ms
readers_in       :  3163.0 ms
bypasses_in      :  2230.9 ms
total lines: 169 644
```

## 4. Three findings, stated as findings

**F1 — the swarm's verdict phase is not sub-second; a cursor's is.** The whole
swarm's verdict phase measures **1756 ms wall** over 343 modules. The *cursor
schedule* — the thing the viewer sees, and the only number the page claims a
budget against — is **868 ms of a 900 ms budget**, and that one is proven by
arithmetic rather than measured after the fact. The per-cursor verdict is
**median 309 ms (n=72)**, which is the design's own bar ("per-cursor verdict
< 1 s wall") and is met. The video's headline — a swarm that finishes in
under a second — is **not** reproduced by this implementation, and the page
does not claim it.

**F2 — free-threading does not make AST work parallel.** Sixteen threads gave a
**2.86×** speed-up on a **5014 ms** serial baseline, not 16×. The work is
`ast.parse` plus two full-tree AST walks per module, and CPython's `ast` module
builds Python objects while holding the interpreter lock, so the parallelism
the free-threaded interpreter was adopted for does not apply here. The first
version of this run reported a **14.43×** speed-up; that number was the sum of
per-worker times measured *while 16 threads contended for the same lock*, which
is neither the serial cost nor any real quantity. The tool now runs a **second
sweep at one thread** and divides two measured wall times.

**F3 — the cursor's tip must land on the node, and the arithmetic is not
optional.** The first render put the cursor's *corner* on the node. The
page's self-test caught it (`hotspot_misaligned=72`) because the check is
`left + hotspot_x == target_x` in the live DOM. The fix is one subtraction in
the emitter. A second bug in the same line: `counts.misaligned` started
`undefined`, so `undefined + 1` was `NaN` and `NaN === 0` was false — the
self-test reported `CHAIN=MISMATCH` on a correct page. The counter is now a
separate variable.

## 5. What this closes against the audit

| audit item | status here |
|---|---|
| **P0** ledger written outside the transaction | **closed** — the canonical ledger is appended only when every worker is green; a red swarm writes `worker_attempts.jsonl` and leaves it alone. Pinned by `test_a_red_worker_leaves_the_canonical_ledger_untouched`. |
| **P0** scope declared, never enforced | **closed in the read direction** — one `git status --porcelain` over the scope decides each worker's verdict, and a dirty scope is `held`, not green. The *write* direction (a cursor editing outside its scope) is not implemented; the swarm produces a site, not source edits. |
| **P1** `held` and `warn` share a colour | **closed** — `monitor_theme.SEMANTIC` gained a `held` slot, taken from `ACCENTS["mesh"]` rather than invented. |
| **P1** the pulse cannot be an OS cursor | **closed** — the pulse is a follower element with `pointer-events: none`; the pointer is a static SVG. |
| **P2** the ledger is one hard-coded home path | **partly closed** — the ledger's in-repo twin is `tools/cursor_swarm/worker_frames.jsonl`, and `claim_agreement.LEDGER_CANDIDATES` now lists it second, after the live one. |
| **§2.4** the hash rule is backwards | **closed, in the direction the audit corrected** — the hash still covers every key the row carries, so the new `ts` column is authenticated; only the key check widened to `LEDGER_KEYS ⊆ keys ⊆ LEDGER_KEYS ∪ {ts}`. A test rewrites a `ts` and requires the chain to break. |
| **§2.5** the crate cannot build (no `src/CORE/worm_manifest.json`) | **not addressed** — out of scope for a swarm that is pure Python. |
| **§3.5** worktree per cursor (6.96 s, 401 MB each) | **avoided** — no worktree is created at all; the swarm writes one page. |
| **step 8** NSGA-II placement | **dropped** — `src/ML/nsga2.py` does not exist, exactly as the audit said. |

## 6. What is not built

* **The swarm does not edit the repository.** It reads a scope and lands a
  layer of a page. The A8 design's "cursor edits files or proposes edits"
  question is answered "proposes", and the licence boundary that answer needs
  is still open.
* **No cross-environment parity.** One environment (Windows) was run.
* **No native crate.** The verdict phase is pure Python, so the Rust path in
  the design (`native/worm_manifest`) is untouched.
* **`swarm_arena/` is untouched** — deliberately. It is a different project.

## 7. References

- `docs/CURSOR_SWARM_A8_DESIGN_2026-11-13.md` — the design
- `docs/CURSOR_SWARM_A8_AUDIT_2026-11-14.md` — the audit this answers
- `tools/claim_agreement.py` — `LEDGER_KEYS`, `LEDGER_VERDICTS`, the hash rule
- `tools/monitor_theme.py` — `SEMANTIC`, `ACCENTS`
- `tools/settings_shadow.py` — `readers_in`, `bypasses_in`, `flatten`
- <https://github.com/califa/swarm-site> — the site the video is about
- <https://www.tiktok.com/@leos.logos/video/7704853939681873165> — the video
