# RESTART-QUEUE-v1 — what runs after a restart, and how the queue is read

**Standing order.** This block used to exist only as hand-appended prose in
`~/AGENTS.md` and `C:/Azazael/AGENTS.md` — no source, no byte-check, nothing able
to notice it rot. `orders-in-sync` now owns it. Edit this file, never a copy.

## Read the queue by claiming it

```bash
python C:/Users/clint/_board.py claim <lane> 10
python C:/Users/clint/_board.py done <id> "<command + result>"
python C:/Users/clint/_board.py stats <lane>
```

A lane that asks "what is pending" instead of claiming is reading history, not
work. `done`/`block` exit non-zero when the row was never claimed — a real
signal, never noise. A claim expires after 30 minutes, so a lane that dies
mid-batch cannot strand work.

## Quote no count you did not just measure

This block deliberately carries **no lane counts**. The version that did said
`freebuff 0 open; kilo 6; opencode 11` while the live board read
`100 / 0 / 47` — four days stale and believed, because nothing could check it.
`stats` returns `available`, `claimed`, `retired`, `open`, and all four move
while you work. Run it in the turn where you quote it.

## Gate first, and read it literally

```bash
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix
```

- `PASS=n WARN=n` with exit 0 is a working stack. A WARN is named in the status
  you report, never rounded into a pass.
- **`[BLOCKED]` is recorded, never worked around** — only a client restart
  clears it. Degraded memory work proceeds on the supervisor fallback
  (`tools/supervisor_mcp.py --verdict`) with the gap named in the first sentence.
- Never kill a `pams`, `pmb` or `supervisor` process to "refresh" it: they are
  the client's stdio children and killing one breaks the live session.

## Standing constraints

- **Interpreter:** production is 3.16t free-threaded
  (`C:/Azazael/.venvs/py316t/Scripts/python.exe`); 3.15t is the GIL sidecar for
  packages without `cp316t` wheels. Bare `python` is 3.14 with the GIL and is not
  production.
- **Commits:** never `git add -A`; stage by explicit path; read `git show --stat
  HEAD` back (an empty commit is a silent failure); ≤8 files and ≤150 changed
  lines per commit (the bulk gate counts added *and* deleted); verify ancestry
  after every commit.
- **Turf:** a lane does not clean up another lane's paths. Destructive cleanup
  needs an explicit GO, and `TREE_REPAIR` must satisfy its six conditions before
  any `D:` clone.
- **Freebuff owns Eve** (`eve_unleashed/`); other lanes hands off.

## Expose the screen before any work starts (2026-11-13)

**Order: a session's first act after the gate is to say the machine is visible.**
A human cannot check an agent's claim about pixels they cannot take. So before
queue work, print the capability and its landing folder — not a promise to take
a screenshot later:

**Historical (2026-11-13, not in this tree):** the capture tools this section
named — sys_screenshot.py and gui_act.py — were developed on another branch and
are absent here, so the commands are removed rather than left pointing at files
that do not exist. The Win+PrtScr naming notes and the gated-automation protocol
described those tools and go with them. Until they merge, do not claim screen
visibility from a tool run; the standing part is the order at the top: say what
the session can actually show, and if there is no capture capability in this
tree, say so instead of printing a tool path.
- Human-side check: an agent that says it clicked something must be able to show
  the before and after frames. A claim about the UI without a frame is a claim.

## Critique loop — every restart carries one expiry

Each lane's restart report names **one residual failure** with its repro command
and **one repair** with a file, a price and a test. Every number in it is trusted
only for the session that measured it; the expiry date goes in the report, and
the next session re-measures rather than inheriting the figure.

Verify this block:

```bash
python tools/agent_orders_sync.py --check --wsl
```
