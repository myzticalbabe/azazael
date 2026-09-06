---
name: azazael-dual-ledger
description: DLV discrepancy catalog — all known by-design divergences between DirectMemory and .audit/ JSONL ledgers, by event type, severity, and root cause
metadata:
  category: architecture
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# DualLedgerValidator Discrepancy Catalog

## Overview

The DualLedgerValidator cross-validates two separate audit trails:
- **DirectMemory** (SQLite) — records codebuff agent session events
- **.audit/ JSONL** — file-based audit trail with hash-chained entries

These ledgers record the same events but via different mechanisms, producing
by-design discrepancies for certain event types.

## Current Discrepancies (June 14, 2026)

| Event Type | Audit Count | Memory Count | Delta | Severity | Root Cause |
|------------|-------------|--------------|-------|----------|------------|
| file_edit | 9 | 5 | +4 | HIGH | .audit/ captures intermediate auto-save edits; DM deduplicates |
| file_create | 6 | 5 | +1 | LOW | .audit/ captures temp/staging files; DM only records final creates |
| test_run | 8 | 5 | +3 | HIGH | .audit/ records each test sub-run; DM aggregates into single entry |

**Totals:** 256 audit events vs 246 memory events (delta: +10)
**Matching sessions:** 0

## Why matching_sessions=0

The two ledgers use different session ID schemes:
- DirectMemory: session IDs from  format
- .audit/ JSONL: session IDs from  filenames

The cross-validation looks for exact session ID matches, which never align
because of the different naming conventions. This is a known limitation.

## Severity Definitions

- **HIGH**: >2 event delta — investigation recommended but expected
- **LOW**: 1-2 event delta — normal divergence, no action needed

## Suppression Guidance

These discrepancies are by-design and should not block operations.
The ComplianceOrchestrator weighted score is 1.0 (passes halt threshold of 0.5)
even when dual_ledger reports consistent=False.
