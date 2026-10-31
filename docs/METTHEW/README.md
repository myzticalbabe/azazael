# Metthew — index

Metthew is a **gaming** project: a group of friends (a circle) creating, exchanging and
playing small, portable game modules (**Shards**) on the hardware they already own,
instead of renting them from a centralised gaming industry.

It is not a fork of `src/SHARDS/*` and touches none of them. It borrows exactly one
idea from that tree — the own / validated / replaceable unit with a declared contract —
and applies it to games.

## Files

| file | what it is |
| --- | --- |
| [METTHEW_PLAN_2026-10-31.md](METTHEW_PLAN_2026-10-31.md) | the plan: why, what exists to reuse, what a Shard is, the low-end budget, the four tracks, the explicit non-goals |
| [tasks.json](tasks.json) | the same 12 tasks machine-readable, with owner, dependencies, deliverable, acceptance and risk. It is the scheduling copy; the markdown is the reasoning copy. |

## Separation of tasks in one screen

| track | name | tasks | who | first gate |
| --- | --- | --- | --- | --- |
| **A** | Contract | M-01 shard schema · M-02 low-end bench · M-03 validator · M-04 minting CLI | freebuff (bench shared with every host owner) | **M-01**, then M-02 → M-03 → M-04 |
| **B** | Runtime | M-05 three reference shards · M-06 deterministic ledger and replay · M-07 exploit-as-content | freebuff | after M-03 |
| **C** | Circle (no server, no accounts) | M-08 bundle exchange · M-09 signed result files · M-10 3-person play test | freebuff, M-10 owned by kilo | M-08 after M-03, M-10 after M-06 |
| **D** | Portability and gates | M-11 portability matrix · M-12 unplayable ratchet + weekly cold run | windows/ubuntu/kali owners, kilo | after M-05 / M-03 |

**Critical path:** `M-01 → M-03 → M-05 → M-06`.

Nothing in tracks B, C or D may claim a task before M-03's validator exists, because
every other task's acceptance is phrased in terms of something the validator prints.
That is deliberate: it makes the validator the first deliverable rather than an
afterthought, and it stops "it works on my machine" from being an acceptance argument.

## Why the work is separated this way

- **A before B** — a reference shard only proves a contract if there is an instrument
  that can refuse it. Today the repository has a `shard.json` *concept* and 151 shard
  directories, but no machine-readable shard contract and no validator for one; M-01
  and M-03 create both.
- **B before C** — exchange and reputation are meaningless without a deterministic
  play record. Two players disagreeing about a score with no replay is a shouting
  match, and M-06 is what turns it into a diff.
- **C separately** — the circle features are the only part of Metthew with a social
  failure mode (Sybil, collusion, discovery). They are kept out of A and B so that a
  working single-player Shard is never blocked on a reputation argument.
- **D last and continuously** — portability has to be measured, not assumed, and the
  ratchet only makes sense once there is a validator whose verdict can be ratcheted.

## Running the plan

Claims go through the lane queue, not through this document:

```bash
python C:/Users/clint/_board.py claim freebuff 10
python C:/Users/clint/_board.py done <board_id> "<command + result>"
```

Status lines to `lane.freebuff.status`; announce to `lane.all.announce`. A task is
finished when a command proves it, not when a document says so.
