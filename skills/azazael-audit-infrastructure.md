---
name: azazael-audit-infrastructure
description: VLP 15-layer audit trail system — .audit/ JSONL hash-chained sessions, DirectMemory dual-ledger cross-validation, session audit review procedures, anchors/Merkle proofs
metadata:
  category: quality
  project: azazael
  priority: high
  auto_load: true
  version: 1.0.0
  created: 2026-06-14
---

# Azazael Audit Infrastructure

> **Canonical audit trail system** — hash-chained, Ed25519-signed, Merkle-proved session audit.
> **Dual-ledger** — `.audit/` JSONL ↔ DirectMemory SQLite cross-validation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 AUDIT INFRASTRUCTURE                     │
├──────────────┬──────────────────────────────────────────┤
│  Ledger 1    │  .audit/session_*.jsonl                  │
│  (JSONL)     │  - Append-only hash chain                │
│              │  - Ed25519 signatures                    │
│              │  - Merkle inclusion proofs               │
│              │  - Cross-session anchors                 │
├──────────────┼──────────────────────────────────────────┤
│  Ledger 2    │  ~/.azazael/memory_store.db              │
│  (SQLite)    │  - DirectMemory events table             │
│              │  - sessions table                        │
│              │  - UUID7 correlation IDs                 │
│              │  - BLAKE2b audit hashes                  │
├──────────────┼──────────────────────────────────────────┤
│  Validator   │  DualLedgerValidator                     │
│              │  - Cross-validates JSONL ↔ SQLite        │
│              │  - Flags discrepancies                   │
│              │  - VLP 15-layer verification             │
└──────────────┴──────────────────────────────────────────┘
```

## File Locations

| Component | Path | Purpose |
|-----------|------|---------|
| Audit trail | `.audit/session_*.jsonl` | Hash-chained session records |
| Anchors | `.audit/anchors.jsonl` | Cross-session Merkle anchors |
| Source | `src/CORE/audit_trail.py` | Audit trail implementation |
| Governance | `src/CORE/compliance/governance.py` | DualLedgerValidator + RealtimeAuditPipeline |
| Memory DB | `~/.azazael/memory_store.db` | DirectMemory SQLite |
| VLP reports | `azazael/_vlp_full_audit_report.json` | Audit integrity reports |

## Audit Trail Format (v3.0.0)

Each session file is a JSONL (one JSON object per line):

```
Line 1 ── session_start — {audit_trail_version, hash, prev_hash, session_file, session_uuid, ts, type, uuid}
Line N ── events — {type, hash, prev_hash, ts, uuid, ...event-specific fields...}
Line Z ── session_end — {entry_count, hash, head_hash, merkle_root, prev_hash, ts, type, uuid}
```

### Hash Chain

- Each line has `prev_hash` pointing to the previous line's hash
- `hash` = SHA-256 of canonical string representation
- First line uses `prev_hash=0000...0000` (genesis)
- Last line includes `merkle_root` of all entry hashes

### Anchors

`anchors.jsonl` stores the head hash and entry count of each session for cross-session verification (truncation defense).

## VLP 15-Layer Verification

The Verifiable Layer Protocol (VLP) checks 15 integrity layers:

| Layer | Name | What It Checks |
|-------|------|----------------|
| 1 | File existence | Session file exists on disk |
| 2 | Line existence (chain integrity) | Each line is parseable JSON |
| 3 | Type match | Entry types are valid (session_start, file_read, etc.) |
| 4 | Agent match | Hash chain links are valid |
| 5 | Per-entry hash | Each entry's hash matches its content |
| 6 | Full chain | All prev_hash links form a valid chain |
| 7 | Ed25519 signature | Each entry has a valid signature |
| 8 | Merkle inclusion proof | Each entry can be Merkle-proved |
| 9 | Proof of omission | No entries are missing between chain links |
| 10 | Anomaly detection | Rate/temporal/structural anomalies |
| 11 | Non-canonical signature check | Signature validation with non-canonical encoding |
| 12 | Replay prevention (monotonic) | UUID7 timestamps are monotonic |
| 13 | Cross-session hash chaining | Anchors form a valid cross-session chain |
| 14 | Truncation defense (anchor) | Session hasn't been truncated (anchor hash matches) |
| 15 | Quantum-resistant hybrid backup | Dual signatures for quantum resistance |

## Key Commands

### Run VLP Audit
```bash
cd /c/Users/clint
python -c "
import sys; sys.path.insert(0, 'azazael/src');
from CORE.compliance.governance import RealtimeAuditPipeline;
p = RealtimeAuditPipeline();
result = p.process('.audit/session_20260612_231506_019e.jsonl');
import json;
print(json.dumps({'all_passed': result.get('all_passed'), 'passed_count': result.get('passed_count'), 'total_layers': result.get('total_layers'), 'failed_layers': result.get('failed_layers')}, indent=2, default=str))
"
```

### Run DualLedgerValidator
```bash
cd /c/Users/clint
python -c "
import sys; sys.path.insert(0, 'azazael/src');
from CORE.compliance.governance import DualLedgerValidator;
v = DualLedgerValidator();
result = v.cross_validate();
print(f'Consistent: {result[\"consistent\"]}')
"
```

### List All Audit Sessions
```bash
ls .audit/session_*.jsonl
```

### Query DirectMemory Recent Events
```bash
cd /c/Users/clint
python -c "
import sys; sys.path.insert(0, 'azazael/src');
from CORE.direct_memory import get_dm;
dm = get_dm();
events = dm.recall_recent(10);
[print(f'[{e[\"id\"]}] {e[\"event_type\"]}: {str(e.get(\"data\",{}).get(\"action\",\"?\"))[:80]}') for e in events]
"
```

## Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Layer 9 fail | Proof of omission fails on sparse sessions | Some sessions legitimately have few events; check if hash chain is intact |
| Layer 14 fail | Truncation defense fails on `src/.audit/` sessions | Those sessions predate the anchor system; re-anchor |
| DualLedger mismatch | "consistent": false | Run backfill: `_backfill_audit_to_dm.py` or rebuild |
| DirectMemory DB missing | DB doesn't exist at `~/.azazael/memory_store.db` | Run `dm = DirectMemory()` to auto-create |

## Related Skills

- `azazael-verifiable-truth` — RULE 0T/0T-A/0T-B verification mandate
- `azazael-compliance-infrastructure` — RULE 0X/0Y compliance
- `azazael-direct-memory` — DirectMemory session recording
- `azazael-pams-memory` — Persistent AI memory system
- `azazael-operating-protocols` — Agent operating guidelines
