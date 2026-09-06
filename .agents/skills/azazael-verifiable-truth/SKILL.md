---
name: azazael-verifiable-truth
description: Verifiable Truth Mandate (RULE 0T/0T-A/0T-B) — 15-layer VLP verification stack, audit trail format, Ed25519 signatures, Merkle inclusion proofs. Every session action must be auditable.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael Verifiable Truth — 15-Layer VLP Framework

> **Canonical source:** `azazael/SYSTEM_INSTRUCTIONS.md` (RULE 0T, RULE 0T-A, RULE 0T-B)
> **Version:** v3.2.0 — 15 verification layers, Ed25519-signed, Merkle-proved

---

## Core Mandate (RULE 0T)

Every session action that CAN be backed by disk evidence MUST cite an audit trail
entry from `.audit/session_*.jsonl`. The audit trail is append-only, cryptographically
chained, Ed25519-signed, Merkle-proved.

---

## 15 Verification Layers (v3.2.0)

| # | Layer | Function | Detects |
|---|-------|----------|---------|
| 1 | File existence | `verify_citation_exists()` | Missing audit file |
| 2 | Line existence | `get_line()` | Missing line in file |
| 3 | Type match | `_verify_audit_citation()` | Wrong entry type claimed |
| 4 | Agent match | `_verify_audit_citation()` | Wrong agent claimed |
| 5 | Per-entry hash | `verify_entry_hash()` | Tampered entry content |
| 6 | Full chain | `verify_chain()` | Hash chain break |
| 7 | Ed25519 signature | `verify_signature()` | Spoofed/unsigned entries |
| 8 | Merkle inclusion proof | `verify_inclusion_proof()` | Single-entry O(log n) verification |
| 9 | Proof of omission | `verify_completeness()` | Intentionally unrecorded actions |
| 10 | Anomaly detection | `audit_anomaly_scan()` | Rate/temporal/structural impossibilities |
| 11 | Non-canonical sig check | `verify_ed25519_canonical()` | Ed25519 S >= L malleability |
| 12 | Replay prevention | `verify_nonce_and_counter()` | Duplicate sequence numbers |
| 13 | Cross-session chaining | `verify_cross_session_chain()` | Session isolation attacks |
| 14 | Truncation defense | `verify_root_hash_witness()` | Log truncation with valid hashes |
| 15 | Quantum-resistant backup | `verify_hybrid_signature()` | Future quantum attacks on Ed25519 |

## Citation Format

```
.audit/session_20260611_120000.jsonl:42
```

### Valid vs Invalid Citations

| Answer | Meaning |
|--------|---------|
| `"Yes — CITING: .audit/session_20260611_120000.jsonl:42"` | Legitimate — entry + hash + sig verified |
| `"Yes — CITING: Gemini: architecture sound"` | VIOLATION — no filepath |
| `"Yes"` (without evidence) | VIOLATION — false claim |
| `"NOT VERIFIED"` | Honest — HALT required |

## Enforcement (v3.2.0)

| Violation | Severity |
|-----------|:--------:|
| Citing non-existent audit lines | 🔴 CRITICAL — VERIFIABLE LIE |
| Invalid Ed25519 signature | 🔴 CRITICAL — SPOOFED ENTRY |
| Expected actions not fulfilled | 🔴 CRITICAL — BY OMISSION |
| Anomaly detected | 🔴 CRITICAL |

## Sentinel Self-Recording (RULE 0T-A)

The sentinel gate MUST record its own execution:
```python
audit_sentinel_run(result="AUTHORIZED" if passed else "DENIED", errors=[...])
if passed:
    audit_gate_passed(checks_passed=passed_count, checks_failed=failed_count)
```

## Related Skills

- `azazael-pre-action-gate` — The PRE-ACTION GATE that triggers audit recording
- `azazael-sentinel-gate` — Compliance sentinel with self-recording mandate
- `azazael-compliance-orchestrator` — Programmatic compliance infrastructure
- `azazael-sop` — SOP mirror with VLP enforcement
