## SESSION ORDER — what runs first, in what order, in every lane

**This section is the single source for session order. It is generated into every
lane's instruction file by `azazael/tools/agent_orders_sync.py` from
`docs/agent_orders/00_session_order.md`. Edit the source, never a copy; the MCP
gate fails when a copy drifts.**

### The chain (this is the precedence — nothing else claims to go "first")

0. **GATE** — `python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix`
1. **MEMORY LOAD** — `python C:/Azazael/azazael/tools/session_start.py "<task>"`
   (runs the gate as its own step 0, prints both PMB and Engram context)
2. **VERDICT** — `supervisor__verdict` MCP tool (or `engram_supervise.py`).
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
- `supervisor-fresh` / `pams-running` — child start time vs script mtime.
- `lane-config` — kilo, freebuff and opencode all route `pmb` through :8766.
- `orders-in-sync` — every generated block in this section and the two canon
  blocks is byte-identical to its source.
- `lane-context` — engram / codegraph / barta presence (warn only).

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
