## SESSION ORDER — what runs first, in what order, in every lane

**This section is the single source for session order. It is generated into every
lane's instruction file by `azazael/tools/agent_orders_sync.py` from
`docs/agent_orders/00_session_order.md`. Edit the source, never a copy; the MCP
gate fails when a copy drifts.**

### The chain (this is the precedence — nothing else claims to go "first")

0. **GATE** — `C:/Azazael/.venvs/py316t/Scripts/python.exe C:/Azazael/azazael/tools/mcp_startup_gate.py --fix`
1. **MEMORY LOAD** — `C:/Azazael/.venvs/py316t/Scripts/python.exe C:/Azazael/azazael/tools/session_start.py "<task>"`
   (runs the gate as its own step 0, prints both PMB and Engram context)
2. **VERDICT** — `supervisor__verdict` MCP tool (or `C:/Azazael/.venvs/py316t/Scripts/python.exe tools/supervisor_mcp.py --verdict`).
   `NO-GO` blocks non-memory work; `GO` proceeds.
3. **SKILLS + CANON** — loaded **on trigger**, not up front: a skill when its
   description matches the task, a canon document when the task touches what it
   governs. The permanent canon order (RULE 0K) governs *the order of those
   reads*, never "before everything else".

Where any other document says "first", it means "first within its own step".
Steps 0–2 are unconditional; step 3 is demand-driven.

### Gate semantics — exit 0 clean, exit 1 do not proceed silently

- **`[FAIL]`** — a real defect: daemon down, floor not filtering, duplicate proxy,
  a lane wired at :8765 (the daemon, unfloored) instead of :8766. Repair before
  trusting any recall answer.
- **`[BLOCKED]`** — only a client restart clears it (a stdio child still serving
  old code, or pams not running). Say so plainly in the first response.
- **NEVER kill a `pams` or `supervisor` process to "refresh" it.** They are the
  client's stdio children; killing one breaks the live session.
- A lane config is data, not proof: the gate checks behaviour first.

### What the gate actually checks (as implemented, not as promised)

- `pmb-daemon` — :8765 answers MCP `initialize`.
- `floor-proxy` — :8766 up, **and a DIFFERENTIAL**: the same noise query asked of
  daemon and proxy must return fewer rows through the proxy. It is *not* a
  "nonce returns zero rows" test — one nonce in fifteen scored 0.836, so a
  threshold-shaped assertion false-fails a healthy stack. The differential proves
  filtering wherever the thresholds sit.
- `proxy-singleton` — exactly one proxy **instance** (one healthy instance is two
  processes: the interpreter re-execs itself).
- `floor-origin` — the live proxy was started by a **durable** starter, not by a
  client session. A stack a previous session left running passes every
  behavioural check above and still dies at the next reboot; the starter declares
  itself in `PMB_FLOOR_ORIGIN`, the proxy stamps origin+pid on bind, and a
  session-scoped one is a FAIL with the remedy named.
- `supervisor-fresh` / `pams-running` — child start time vs script mtime.
- `lane-config` — kilo, freebuff and opencode all route `pmb` through :8766.
- `orders-in-sync` — every generated block in this section and the two canon
  blocks is byte-identical to its source.
- `lane-context` — **every server the lane configures must resolve.** The check
  reads kilo/freebuff/opencode through `tools/mcp_eight_verify.py --fast`, so an
  enabled entry whose command does not exist, whose endpoint is closed, or which
  points at the raw :8765 daemon is a FAIL. Measured 2026-11-01: the old version
  matched three hard-coded names (engram, codegraph, barta) and read green while
  the Kilo lane configured **eight** servers — scrapling, pams, supervisor and
  both pmb endpoints were never examined, so a path that a restart turns into a
  dead server passed untouched. Full proof (spawn + `initialize` + `tools/list`,
  with a negative control) is `python tools/mcp_eight_verify.py`.

### Cold start is a client deadline, not a bootstrap detail

opencode's remote MCP client gives an unreachable endpoint **three attempts in
1.65 s** (measured 2026-10-31: 0.39 s, 0.65 s, 1.65 s) and then marks the server
failed for the whole session. pams is spawned at the same millisecond and used to
reach its old floor-proxy spawn site ~2.5 s in, so every cold start lost the race
— daemon at 2.5 s, :8766 at 3.0 s, `pmb` dead until the next restart, with a
green gate throughout.

Two rules follow, both enforced:

- **:8766 must exist before the client.** `Startup\pmb-floor-proxy.vbs` starts it
  hidden at logon (`PMB_FLOOR_ORIGIN=logon`). pams still spawns one when the port
  is free and declares it `origin=pams`; that state is `floor-origin` FAIL, not a
  working stack. pams also starts its watcher before its heavy imports (bind
  measured 1.34 s vs 2.9 s) as a second line of defence, not as the guarantee.
- **The proxy waits for its own upstream.** The daemon loads an embedding model,
  so a request that arrives during a cold start is answered by waiting up to
  `PMB_UPSTREAM_WAIT` (default 30 s) instead of 502. A 502 during a cold start is
  indistinguishable to the client from a dead stack.

### Floor thresholds (a property of the store, not of the software)

`PMB_RECALL_MIN_BEST=0.89` (query floor) and `PMB_RECALL_FLOOR=0.70` (row floor)
in `pmb_floor_proxy.py` and `supervisor_mcp.py`. Measured 2026-10-30 on this
corpus after the contaminated records were purged: noise best 0.836 max / 0.645
mean, real best 0.949 min — a 0.113 gap, and the thresholds sit in it. Re-measure
after a large purge; the numbers move with the corpus.

### Why this is not optional

On 2026-10-30 three silent failures were live at once: supervisor children had run
since 10:34 while `supervisor_mcp.py` was edited at 13:19 (nonsense queries still
answered with 0.28-score rows); a random nonce scored 0.644 against a 0.62 floor;
and six proxies were double-bound on :8766 because Windows `SO_REUSEADDR` lets a
second instance bind a live port with no error. None of them raises an exception.
They only make answers wrong.

### Memory write timing — the ambiguity is resolved here

- **Encounter time, immediately:** every error, near-miss, falsification, or claim
  you had to retract. One small `record_batch` at the moment it happens — never
  deferred to session end, where reconstruction loses detail and over-weights
  whatever is still salient.
- **End of turn, one batch:** outcomes — completed work, decisions and their
  reason, goals stated by the user.
- So "one `record_batch` per turn" in the generated PMB block means *one atomic
  batch per turn for outcomes*, not a prohibition on logging an error the moment
  it appears. Encounter-time writes win over batching. (Recorded 2026-10-30; this
  paragraph is the resolution of a direct contradiction between the PMB block's
  "batch them together at turn end" and the ERROR CAPTURE rules.)

### Tooling facts — measured 2026-11-08, verify before contradicting

- **The production interpreter is 3.16t free-threaded:**
  `C:/Azazael/.venvs/py316t/Scripts/python.exe` (3.16.0a1, `sys._is_gil_enabled()`
  is False). `python` on PATH is 3.14.7 **with** the GIL. Run the suite with the
  3.16t interpreter; a "hang" measured under 3.14 is not evidence about production.
- **3.15t is now the GIL sidecar** for packages without `cp316t` wheels:
  `C:/Azazael/.venvs/py315t/Scripts/python.exe` (3.15.0rc3, free-threaded).
  Use only when a dependency refuses to install under 3.16t.
- **Session startup, test suite, commit hooks, and all gates use 3.16t:**
  Measured 2026-11-08: gate, session_start, supervisor --verdict, and 122 tests
  (type_check, pmb, mcp, agent_orders, anti_pattern, compliance) all pass under 3.16t.
  The "suite not proven" blocker is resolved.
- **6,975 tests exist and nothing gates them.** (Collected 2026-11-05 by
  `python tools/head_state.py --write`, which runs `pytest --collect-only -q` under
  the 3.15t interpreter and writes `state/head.json`. This line said 5,380 for
  three days, then 6,277 for three more, because no gate read this file — which is
  why `tools/prompt_check.py` now does, and it is what caught the 6,277.) No stanza of
  the commit hook runs pytest. Before concluding "the suite is slow", check that it is not *stuck*:
  metering helpers need a bound, and a test with no timeout can wedge a whole run
  (two did, for months — the compliance gate under test read a 5.4 GB store on
  every `check_all()`; it now costs 0.09 s, measured).
- **`azazael-pkg-*` are no longer skills.** 1,042 package references were archived
  on 2026-10-30 (`skills.pkg-archive/`) because their descriptions alone cost
  ~34.7k tokens on every request. Look one up with
  `python C:/Azazael/azazael/tools/skills_find.py <package>`; never restore the
  catalogue to `skills/`. 204 skills remain loadable.
- **Memory has a verified backup path:** `python C:/Azazael/azazael/tools/memory_backup.py`
  copies through SQLite's online backup API and refuses a copy that fails
  `integrity_check`. The 5.4 GB DirectMemory store is excluded unless
  `--include-large`, because this disk runs at 98%.
- **The commit gates bite, by design.** A scanner finding is fixed, not
  rebaselined; a bulk override (`ALLOW_BULK_COMMIT=1`) is declared in the commit
  message. Both were used today and named in their commits.
