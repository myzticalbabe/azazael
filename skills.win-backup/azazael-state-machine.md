---
name: azazael-state-machine
description: ComplianceStateMachine reference — 7 states, legal transitions, is_in_sequence rules, and the startup wiring fix (IDLE→GATE_ASSERT→CODE_EDIT on __init__)
metadata:
  category: architecture
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# ComplianceStateMachine Reference

## Overview

The ComplianceStateMachine enforces a workflow sequence for compliance operations.
All code-modifying actions must pass through the sequence before execution.

## States

| State | Value | Description |
|-------|-------|-------------|
| IDLE | 1 | Initial bootstrap state — no operations allowed |
| GATE_ASSERT | 2 | Gate assertion phase — policy checks run here |
| GEMINI_SPAWN | 3 | Gemini spawning phase — AI injector activation |
| CODE_EDIT | 4 | Code editing allowed — str_replace, write_file, etc. |
| CODE_REVIEW | 5 | Code review phase — review must occur after edits |
| SYNC | 6 | Synchronization phase — sync state before next cycle |
| HALTED | 7 | Emergency halt — all operations blocked |

## Legal Transitions

IDLE → GATE_ASSERT → CODE_EDIT → CODE_REVIEW → SYNC → IDLE (cycle)
Any state → HALTED (emergency)
HALTED → IDLE (reset)

## Startup Flow (Wired in __init__)

On  initialization:
1. State machine starts at IDLE
2.  — enters gate assertion phase
3.  — enters code editing phase
4. Machine is now ready for  with 

Previously, the machine stayed at IDLE, causing  to report  because  returned False.

## is_in_sequence() Check

 checks:

This returns True if the current state is one of these valid workflow states.

## Self-Test Compatibility

The self_test creates its own  instance and tests transitions independently. It no longer manually transitions the orchestrator's machine since  handles this.
