---
name: azazael-compliance-deep-dive
description: Deep diagnostic of ComplianceOrchestrator self_test — 0X: 8/8 pass, 0Y: 4/5 pass (dual_ledger by-design failure), state machine startup wiring needed
metadata:
  category: architecture
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# Compliance Self-Test Deep Dive

## Test Results (June 14, 2026)

| Component | Result | Notes |
|-----------|--------|-------|
| Policy Engine (0X-1) | PASS | Developer allowed, Guest denied |
| State Machine (0X-3/4) | PASS | 5 legal transitions completed, illegal blocked |
| Formal Verifier (0X-3) | PASS | 4/4 constraints passed |
| Schema Validator (0X-5) | PASS | 11 fields validated |
| Compliance Scorer (0X-6) | PASS | Score=1.000, Halt threshold=0.5 |
| AST Scanner (0X-7) | PASS | Clean=True, Dirty found=2 issues |
| Multi-Agent Judge (0Y-1) | PASS | 2/3 consensus (0.667) |
| Compliance Orchestrator (full) | FAIL | RULE 0X: PASS (8/8), RULE 0Y: FAIL (4/5) |

## Failing Component: 0Y:dual_ledger

**Status:** By-design expected failure.

**Root cause:** The DualLedgerValidator compares DirectMemory count(events) against .audit/ JSONL count(entries). These counts are expected to differ for 3 event types:
- file_edit events
- file_create events  
- inference_spawn events

See  skill for full documentation of each discrepancy.

**Score:** 1.00 (passes threshold but component reports as failing)

## State Machine: Always IDLE

The ComplianceStateMachine initializes to IDLE and never transitions because  creates a fresh machine each call or doesn't call . The self-test PASSES for transitions (tests 5 legal transitions) but the  method always reports .

**States available:** IDLE(1), GATE_ASSERT(2), GEMINI_SPAWN(3), CODE_EDIT(4), CODE_REVIEW(5), SYNC(6), HALTED(7)

**Available transitions:** transition_to(), assert_gate(), can_edit(), can_review(), halt(), reset(), is_in_sequence()

**Fix needed:** Add startup wiring to transition IDLE → CODE_EDIT when ComplianceOrchestrator initializes (e.g., in sentinel_gate.py or azazael-system-startup Step 4.5).

## All States Check Results

| State | sm_valid | sm_state | Score |
|-------|----------|----------|-------|
| IDLE | False | IDLE | 1.0 |
| CODE_EDIT | False | IDLE | 0.75 |
| INFERENCE | False | IDLE | 0.75 |
| REVIEW | False | IDLE | 0.75 |

All states show  because the state machine is permanently stuck at IDLE. The weighted score drops for non-IDLE states because the  is used in scoring.
