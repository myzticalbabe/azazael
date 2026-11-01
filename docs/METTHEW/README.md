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
| [REJECTION_ANALYSIS_2026-10-31.md](REJECTION_ANALYSIS_2026-10-31.md) | Metthew's contract measured against PICO-8, Doom WADs, Luanti, Factorio, OpenTTD, SMAPI, Minecraft/Fabric, Workshop and Steam Remote Play: 12 ranked reasons players would bounce, and the five contract changes that should land before M-01 freezes. |
| [BLEEDING_EDGE_ADAPTATIONS_2026-10-31.md](BLEEDING_EDGE_ADAPTATIONS_2026-10-31.md) | what already exists to catch them: 14 dated strands (2024–2026) — Wasm 3.0's deterministic profile, WASM-4 carts, Uxn/permacomputing, iroh 1.0, deterministic simulation testing, GGRS rollback, TAS verification, N64 recompilation, Playdate/Picotron, s&box and Dreams, Nostr catalogues, AI minting, web3's collapse — each mapped to the task it changes. |
| [DEEPER_DIVE_2026-10-31.md](DEEPER_DIVE_2026-10-31.md) | the verification pass: every figure in the plan re-read from its artefact and confirmed, plus the three things written down nowhere — the executor hands a shard the player's whole environment, the measured tick cost rules four of six languages out of a 30 fps loop, and the 24-file cap is borrowed from a rule that wastes 64% of its own capacity. Proposes three M-01 fields and two M-03 controls. |
| [FORENSIC_DIVE_LOWEND_2026-10-31.md](FORENSIC_DIVE_LOWEND_2026-10-31.md) | the low-end forensic dive, split three ways for creatively adapted bleeding-edge dev. Lane A ran here (interpreter bench on the production 3.15t interpreter, tick-cost split, capacity arithmetic, five figures); lanes B and C were dispatched to the board as `LOWEND-ARTIFACT` to kilo and `LOWEND-CIRCLE` to opencode, each with the negative control it must ship. §5 is the dispatch record with every delivery row. |

## Separation of tasks in one screen

| track | name | tasks | who | first gate |
| --- | --- | --- | --- | --- |
| **A** | Contract | M-01 shard schema · M-02 low-end bench · M-03 validator · M-04 minting CLI | freebuff (bench shared with every host owner) | **M-01**, then M-02 → M-03 → M-04 |
| **B** | Runtime | M-05 three reference shards · M-06 deterministic ledger and replay · M-07 exploit-as-content | freebuff | after M-03 |
| **C** | Circle (no server, no accounts) | M-08 bundle exchange · M-09 signed result files · M-10 3-person play test | freebuff, M-10 owned by kilo | M-08 after M-03, M-10 after M-06 |
| **D** | Portability and gates | M-11 portability matrix · M-12 unplayable ratchet + weekly cold run | windows/ubuntu/kali owners, kilo | after M-05 / M-03 |

**Critical path:** `M-01 → M-03 → M-05 → M-06`.

**Before M-01 freezes**, the five changes in the rejection analysis must each be decided
either way (sandboxed loader, one-download player, versioned hubs, a `competitive`
flag on determinism, content-addressed ids). They are proposals, not accepted scope; the
bleeding-edge research has already specified the first one as a Wasm 3.0 deterministic-profile
host and proposed one candidate task (M-13, the recovery track).

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
