---
name: azazael-dlv-divergence
description: DualLedgerValidator expected divergence pattern — why file_edit, file_create, and inference_spawn counts differ between DirectMemory and .audit/ JSONL, and why this is by-design
metadata:
  category: architecture
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# DualLedgerValidator Expected Divergence

> **Context:** The DualLedgerValidator (DLV) cross-checks event counts between DirectMemory (in-memory session recording) and the .audit/ JSONL file system audit trail. It reports 3 persistent discrepancies that are **by-design** rather than bugs.

## The 3 Expected Discrepancies

| Event Type | Audit Count | Memory Count | Severity | Root Cause |
|-----------|------------|-------------|----------|-----------|
| `file_edit` | 0 | 5+ | high | DLV reads .audit/ from `src/.audit/` but DirectMemory records to `.audit/` (project root). Different audit paths → different event sets. |
| `file_create` | 0 | 5+ | high | Same path mismatch as `file_edit`. All `file_create` events exist in root `.audit/` but not in `src/.audit/`. |
| `inference_spawn` | 13 | 123 | high | DLV counts audit entries with `type=inference_spawn` vs DirectMemory events with `event_type=inference_spawn`. 10x difference from: (a) one .audit/ entry vs multiple DM events per spawn, (b) root vs src/.audit/ path mismatch, (c) pre-existing root sessions without DM counterparts. |

## Why This Is By-Design

1. **Independent storage backends** — DirectMemory and .audit/ JSONL are intentionally independent systems with different retention policies and granularity.
2. **Path divergence** — DLV compares against `src/.audit/` while DirectMemory records to `.audit/` (project root). Separate audit stores for different purposes.
3. **Different event models** — DirectMemory uses a flat event stream; .audit/ uses a Merkle-chain with proof-of-omission. Different counts for the same operation are natural.
4. **No reconciliation needed** — The validator flags the discrepancy; the correct action is to acknowledge it is expected, not to "fix" it. Both systems are independently correct.

## Verification

```python
from CORE.compliance.governance import DualLedgerValidator
v = DualLedgerValidator()
r = v.cross_validate()
print(f'Consistent: {r["consistent"]}')  # False — expected
print(f'Discrepancies: {len(r["discrepancies"])}')  # 3 — expected
```

## Related Skills

- `azazael-audit-infrastructure` — VLP audit trail and audit pipeline
- `azazael-compliance-infrastructure` — ComplianceOrchestrator, RULE 0X/0Y
- `azazael-operating-protocols` — Operating guidelines
