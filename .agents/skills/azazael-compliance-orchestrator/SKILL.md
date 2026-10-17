---
name: azazael-compliance-orchestrator
description: Automated Compliance Infrastructure (RULE 0X/0Y) — 13 compliance components, policy engine, formal verifier, state machine, multi-agent judge, dual-ledger validation.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael Compliance Orchestrator — RULE 0X / 0Y

> **Canonical source:** `SYSTEM_INSTRUCTIONS.md` (RULE 0X, RULE 0Y)
> **Implementation:** `src/CORE/compliance/` (13 components)

---

## RULE 0X: Automated Compliance Infrastructure

Transition from manual text assertions to programmatic, cryptographically verified compliance boundaries.

### 8 Implementation Components

| # | Component | Library | Function |
|---|-----------|---------|----------|
| 1 | **Policy-as-Code Gate** | Casbin / OPA | Programmatic RBAC/ABAC before every tool call |
| 2 | **Runtime Broker Interception** | wrapt | `@enforce_gate` decorator intercepts all tool calls |
| 3 | **Formal Verification** | z3-solver | Z3 SMT proofs that plans satisfy all rule constraints |
| 4 | **State Machine Workflow** | transitions | Strict finite states: IDLE → GATE_ASSERT → ... → IDLE |
| 5 | **Structured Output Validation** | pydantic / jsonschema | Schema-validate all gate assertions |
| 6 | **Automated Compliance Scoring** | structlog | Real-time metric thresholds; score < min = HALT |
| 7 | **Automated AST Scanning** | ast (stdlib) | Auto-scan 7 anti-pattern categories on every code change |
| 8 | **Compliance Telemetry** | OpenTelemetry | Traces of all agent actions for live dashboard |

## RULE 0Y: Multi-Agent Governance

Democratize decision-making via cross-agent consensus and automate behavioral verification.

### 5 Components

| # | Component | Pattern | Function |
|---|-----------|---------|----------|
| 1 | **Multi-Agent Judge/Consensus** | Worker → Verifier → Judge → Execute | >2/3 consensus required for code changes |
| 2 | **Confidence Gates** | Threshold scoring | Block actions below collective confidence score |
| 3 | **Behavioral Graph Anomaly Detection** | Directed action graph | Detect emergent non-compliance patterns |
| 4 | **Dual-Ledger Cross-Validation** | JSONL ↔ SQLite | Auto cross-validate audit trail vs DirectMemory |
| 5 | **Real-Time Audit Cross-Validation** | Interleaved VLP | 15-layer VLP in middleware, not post-hoc |

## Session Startup Initialization

At every session start (via `azazael-system-startup` Step 4.5):
```python
import sys; sys.path.insert(0, 'src')
from CORE.compliance.orchestrator import ComplianceOrchestrator
from CORE.compliance.state_machine import ComplianceState

co = ComplianceOrchestrator()
co.state_machine.transition_to(ComplianceState.GATE_ASSERT)
# check_rule_0x(), check_rule_0y() now ready
```

## Verification

All decisions logged to `.audit/` per RULE 0T:
- `casbin_allow`: Policy evaluation result
- `z3_proof_passed`: Formal proof status
- `state_transition`: State machine sequence validation
- `judge_vote_consensus`: >2/3 consensus verification
- `confidence_threshold_met`: Confidence score check
- `dual_ledger_sync_ok`: JSONL ↔ SQLite cross-validation

## Enforcement

| Violation | Severity |
|-----------|:--------:|
| Skipping Casbin/OPA policy evaluation | 🔴 CRITICAL |
| Illegal state machine transition | 🔴 CRITICAL |
| Compliance score below threshold without HALT | 🔴 CRITICAL |
| Code change without >2/3 consensus | 🔴 CRITICAL |
| Below confidence threshold | 🔴 CRITICAL |
| Dual-ledger desync without HALT | 🔴 CRITICAL |

## Related Skills

- `azazael-verifiable-truth` — 15-layer VLP (complemented by real-time middleware)
- `azazael-pre-action-gate` — Manual gate assertion (complemented by auto-compliance)
- `azazael-sentinel-gate` — Pre-action authorization sentinel
- `azazael-system-startup` — Step 4.5 initializes compliance infrastructure
