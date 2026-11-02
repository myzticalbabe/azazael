# SHARDEX P2P Bracket Tournament Design
**Date:** November 2, 2026  
**Task:** SHARDEX-HYPEREDGE-P2P (board_id=47300)  
**Deliverable:** docs/SHARDEX_P2P_DESIGN.md

---

## Overview

Design a peer-to-peer bracket tournament system where:
- Brackets are shared via JSONL
- Results verified by any participant
- No central server required
- Golden hash as consensus mechanism

---

## Architecture

### Core Principles
1. **Decentralized** - No central authority
2. **Verifiable** - Anyone can verify results
3. **Deterministic** - Same inputs = same outputs
4. **Audit Trail** - Full history in JSONL

### Data Structures

#### Bracket Definition (JSONL)
```jsonl
{"type": "bracket_def", "id": "sha256", "version": 1, "timestamp": "2026-11-02T12:00:00Z", "participants": ["p1", "p2", "p3", "p4"], "format": "single_elim", "seed": 42, "rules": {"best_of": 3, "time_limit": 300}}
{"type": "match", "bracket_id": "sha256", "round": 1, "match_id": "m1", "player_a": "p1", "player_b": "p2", "status": "pending"}
{"type": "match", "bracket_id": "sha256", "round": 1, "match_id": "m2", "player_a": "p3", "player_b": "p4", "status": "pending"}
```

#### Match Result (JSONL)
```jsonl
{"type": "match_result", "bracket_id": "sha256", "match_id": "m1", "winner": "p1", "score_a": 2, "score_b": 0, "games": [{"game_id": "g1", "winner": "p1", "duration": 180}, {"game_id": "g2", "winner": "p1", "duration": 210}], "timestamp": "2026-11-02T12:30:00Z", "submitted_by": "p1", "hash": "sha256_of_result"}
```

### Golden Hash Consensus

#### Definition
The **Golden Hash** is a deterministic hash of the complete tournament state that serves as the single source of truth.

#### Computation
```python
def compute_golden_hash(bracket_jsonl_lines):
    # Sort by (round, match_id) for deterministic ordering
    sorted_lines = sorted(bracket_jsonl_lines, key=lambda x: (x.get('round', 0), x.get('match_id', '')))
    # Concatenate canonical JSON
    canonical = ''.join(json.dumps(line, sort_keys=True, separators=(',', ':')) for line in sorted_lines)
    return hashlib.sha256(canonical.encode()).hexdigest()
```

#### Verification Protocol
1. Any participant can compute the golden hash from their local JSONL
2. Hashes must match across all participants
3. Mismatch = fork detected, requires resolution

### Tournament Flow

#### 1. Bracket Creation
- Host creates `bracket_def` with participants, format, seed
- Golden hash computed and shared
- All participants verify initial hash matches

#### 2. Match Play
- Players play matches per bracket structure
- Each game produces deterministic result (winner, score, duration)
- Results recorded as `match_result` entries

#### 3. Result Submission
- Winner submits `match_result` with golden hash
- Other participants verify:
  - Hash matches their computed golden hash
  - Scores are valid for format (e.g., best-of-3 → 2-0, 2-1)
  - Timestamps are sequential
- If verified, result is appended to local JSONL

#### 4. Bracket Progression
- When all matches in round complete, next round matches generated
- New golden hash computed and shared
- Process repeats until champion determined

### Conflict Resolution

#### Fork Detection
- Golden hash mismatch between participants
- Automatic detection on next sync

#### Resolution Protocol
1. Compare JSONL line-by-line
2. Identify first divergent line
3. Apply deterministic tiebreaker:
   - Earlier timestamp wins
   - If equal timestamp, lower participant ID wins
   - If equal, hash of line content wins
4. Re-compute from divergence point
5. Re-verify golden hash

### Synchronization

#### JSONL Sync
- Participants exchange JSONL files (or diffs)
- Append-only: never modify existing lines
- New lines appended with verification

#### State Machine
```
CREATED → IN_PROGRESS → ROUND_COMPLETE → ... → COMPLETED
                ↓
            FORKED → RESOLVING → RESOLVED → IN_PROGRESS
```

### Security Considerations

1. **No Central Authority** - Trust is in the math, not a server
2. **Immutable History** - JSONL is append-only
3. **Deterministic Outcomes** - Same inputs always produce same golden hash
4. **Audit Trail** - Every action recorded with timestamp and submitter
4. **Sybil Resistance** - Participant identities tied to cryptographic keys

### Implementation Checklist

- [ ] Bracket definition schema (JSON Schema)
- [ ] Match result schema
- [ ] Golden hash computation (deterministic, sorted)
- [ ] Result verification (format, scores, timestamps)
- [ ] Fork detection (hash comparison)
- [ ] Conflict resolution (deterministic tiebreaker)
- [ ] JSONL sync protocol (diff + verification)
- [ ] CLI tool for bracket management
- [ ] Test suite with known tournament vectors

### Example Tournament Vector

```jsonl
{"type":"bracket_def","id":"test_bracket_4","participants":["alice","bob","charlie","dave"],"format":"single_elim","seed":42,"rules":{"best_of":3}}
{"type":"match","bracket_id":"test_bracket_4","round":1,"match_id":"m1","player_a":"alice","player_b":"bob","status":"pending"}
{"type":"match","bracket_id":"test_bracket_4","round":1,"match_id":"m2","player_a":"charlie","player_b":"dave","status":"pending"}
{"type":"match_result","bracket_id":"test_bracket_4","match_id":"m1","winner":"alice","score_a":2,"score_b":1,"games":[{"game_id":"g1","winner":"alice"},{"game_id":"g2","winner":"bob"},{"game_id":"g3","winner":"alice"}],"timestamp":"2026-11-02T12:00:00Z","submitted_by":"alice"}
{"type":"match_result","bracket_id":"test_bracket_4","match_id":"m2","winner":"charlie","score_a":2,"score_b":0,"games":[{"game_id":"g4","winner":"charlie"},{"game_id":"g5","winner":"charlie"}],"timestamp":"2026-11-02T12:30:00Z","submitted_by":"charlie"}
{"type":"match","bracket_id":"test_bracket_4","round":2,"match_id":"m3","player_a":"alice","player_b":"charlie","status":"pending"}
{"type":"match_result","bracket_id":"test_bracket_4","match_id":"m3","winner":"alice","score_a":2,"score_b":0,"games":[{"game_id":"g6","winner":"alice"},{"game_id":"g7","winner":"alice"}],"timestamp":"2026-11-02T13:00:00Z","submitted_by":"alice"}
```

**Golden Hash for above:** `a1b2c3d4e5f6...` (computed deterministically)

---

## Next Steps

1. Implement core schemas in `shardex/schemas/`
2. Build CLI in `shardex/cli/`
3. Write test vectors in `shardex/tests/vectors/`
4. Document sync protocol in `docs/SHARDEX_SYNC.md`