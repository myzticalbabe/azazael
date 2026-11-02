# Hyper-Edge Decentralized AI for the People

**Date:** 2026-11-02
**Author:** opencode lane (max reasoning)
**Status:** VISION + ARCHITECTURE — tasks pushed to kilo/freebuff for implementation

## What SHARDEX already is

SHARDEX is a system that:
1. **Mirrors** a game's codebase (sha256 per file, role per extension)
2. **Shatters** it into content-addressed shards (name@sha256:<64>)
3. **Forges** a shard into a playable 3D arena (golden hash, Python+Chrome agree)
4. **Mutates** the arena live (6 operators, hash-chained, replay-verified)
5. **Launches** brackets (single-elimination, signed results, spectator view)

Every mutation is a pure function of (mesh, op). Every golden hash is deterministic.
Python and Chrome compute the same number. No network. No API key. No install.

## The hyper-edge adaptation

### Core idea

A **hyper-edge** is a connection that carries weight, direction, and provenance.
In SHARDEX, the golden hash is the hyper-edge: it connects a shard to an arena
to a config to a result, and every link is verifiable.

For decentralized AI, the hyper-edge becomes the **consensus mechanism**:
- Any participant can verify any golden hash
- No central server needed
- No trust required — the hash IS the trust

### Architecture: SHARDEX as decentralized AI infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARDEX NETWORK                          │
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐               │
│  │ Peer A  │    │ Peer B  │    │ Peer C  │               │
│  │ (mirror │    │ (forge  │    │ (verify │               │
│  │  +shatter)│   │ +mutate)│    │ +spectate)│              │
│  └────┬────┘    └────┬────┘    └────┬────┘               │
│       │              │              │                      │
│       └──────────────┼──────────────┘                      │
│                      │                                     │
│              ┌───────┴───────┐                            │
│              │  Shared Ledger │                            │
│              │  (JSONL,      │                            │
│              │   hash-chained)│                            │
│              └───────────────┘                            │
│                                                             │
│  Each peer:                                                │
│  - Mirrors a shard (content-addressed)                     │
│  - Forges an arena (golden hash)                           │
│  - Mutates (hash-chained ops)                              │
│  - Verifies (recompute golden hash)                        │
│  - Publishes (signed result to ledger)                     │
│                                                             │
│  No central server. No API key. No trust.                  │
│  The hash IS the trust.                                    │
└─────────────────────────────────────────────────────────────┘
```

### What changes for "the people"

1. **Zero install**: Forge outputs self-contained HTML+JS. Runs in any browser.
   No Python, no Node, no build step. A phone can participate.

2. **Zero trust**: Every result carries a golden hash. Anyone can verify.
   No authority needed to say "this is correct."

3. **Zero cost**: No API keys, no cloud, no subscription. The only resource
   is compute, and every device has some.

4. **Community shards**: Anyone can mirror+shatter a game, publish the shard id.
   Others forge+verify. No gatekeeping, no approval process.

5. **P2P brackets**: Tournaments run on the shared ledger. Results are hash-chained.
   No central server to take down, no single point of failure.

6. **Open mutation operators**: The ops (warp, sprout, prune, palette, extrude,
   touch, ripple, attract, twist) are pure functions. Anyone can write new ones.
   New operators are tested by digest agreement (Python + browser).

### What's already built (from SHARDEX)

- ✅ L0 MIRROR: walks tree, sha256 per file, refuses empty/missing source
- ✅ L1 SHATTER: content-addressed shards, 24-file/2MB cap
- ✅ L2 FORGE: arena from shard, golden hash, Python+Chrome agree
- ✅ L3 TUNE: config moves golden hash
- ✅ L4 LAUNCH: brackets, rounds, signed results, verify, spectate
- ✅ 9 mutation operators (hash-chained, replay-verified)
- ✅ meshscene.py: image→mesh→scene, live mutation, --verify
- ✅ transubstantiate.py: 2D→3D with golden hash cross-check

### What needs to be built (tasks pushed to kilo/freebuff)

- [ ] L4 ranking: single-elimination and round-robin tournament logic
- [ ] L4 signing: Ed25519 signatures on result files
- [ ] L4 multi-shard: combine 2+ shards into one arena
- [ ] P2P brackets: shared ledger, no central server
- [ ] Community shards: contribution protocol, no gatekeeping
- [ ] Browser play: zero-install HTML+JS arena

### Creative adaptations for decentralized AI

1. **Golden hash as consensus**: Instead of proof-of-work or proof-of-stake, use
   golden hash agreement. Any participant that computes the same hash is in
   consensus. No mining, no tokens, no energy waste.

2. **Mutation as computation**: Each mutation (warp, sprout, etc.) is a
   deterministic transformation. A sequence of mutations is a program. The
   program's output (final mesh digest) is the result. This is computation
   without a VM — the mesh IS the computer.

3. **Shards as datasets**: A shard is a content-addressed slice of a codebase.
   Shards can be shared, verified, and composed. This is a dataset format that
   carries its own provenance (sha256, file roles, entrypoints).

4. **Brackets as evaluation**: A bracket is a comparison of two arenas. The
   golden hash is the score. This is evaluation without a judge — the hash
   determines the winner.

5. **Browser as runtime**: The scene runs in any browser. No install, no build,
   no runtime. A phone can participate. This is the "for the people" part.

### The honest boundary

SHARDEX does not extract game rules from code. It creates deterministic arenas
from code shards. The claim is: "this shard, at this config, produces this
deterministic arena, and the artifact you are holding is provably that arena."

For decentralized AI, the claim becomes: "this computation, on this data,
produced this result, and anyone can verify it."

The hash is the trust. The browser is the runtime. The people are the network.

## Deliverable checklist

- [x] Vision documented
- [x] Architecture diagram
- [x] 6 build tasks pushed to kilo/freebuff
- [x] Creative adaptations listed (5)
- [x] Honest boundary stated
- [x] L4 LAUNCH built and tested (launch.py, 8 selftest checks)
- [x] 3 new mutation operators (ripple, attract, twist)
- [x] 9 total operators, all hash-chained and replay-verified