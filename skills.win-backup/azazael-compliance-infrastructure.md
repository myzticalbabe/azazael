---
name: azazael-compliance-infrastructure
description: RULE 0X + 0Y compliance infrastructure — ComplianceOrchestrator API, 13 components, sentinel_gate.py integration, and session startup wiring.
metadata:
  category: domain
  project: azazael
  priority: high
  version: 1.0.0
---

# Azazael Compliance Infrastructure (RULE 0X + 0Y)

## Overview

The compliance infrastructure in `azazael/src/CORE/compliance/` provides **programmatic
enforcement** of RULE 0X (Auto-Compliance) and RULE 0Y (Multi-Agent Governance). It
replaces the old manual text-only assertions with verifiable, component-level checks.

**13 components total** across 8 source files:

| Rule | Components | File |
|------|-----------|------|
| RULE 0X-1 | PolicyEngine | `CORE/compliance/policy.py` |
| RULE 0X-2 | BrokerInterceptor | `CORE/compliance/policy.py` |
| RULE 0X-3 | FormalVerifier | `CORE/compliance/state_machine.py` |
| RULE 0X-4 | ComplianceStateMachine | `CORE/compliance/state_machine.py` |
| RULE 0X-5 | SchemaValidator | `CORE/compliance/validating.py` |
| RULE 0X-6 | ComplianceScorer | `CORE/compliance/validating.py` |
| RULE 0X-7 | ASTAntiPatternScanner | `CORE/compliance/scanner.py` |
| RULE 0X-8 | ComplianceTelemetry | `CORE/compliance/telemetry.py` |
| RULE 0Y-1 | MultiAgentJudge | `CORE/compliance/governance.py` |
| RULE 0Y-2 | ConfidenceGate | `CORE/compliance/governance.py` |
| RULE 0Y-3 | BehavioralGraphAnalyzer | `CORE/compliance/governance.py` |
| RULE 0Y-4 | DualLedgerValidator | `CORE/compliance/governance.py` |
| RULE 0Y-5 | RealtimeAuditPipeline | `CORE/compliance/governance.py` |

**Orchestrator** (`CORE/compliance/orchestrator.py`): Wires all 13 components together.

---

## Quick Start

### Session Initialization (Step 4.5)

Per `skill("azazael-system-startup")` Step 4.5, initialize at every session start:

```python
import sys; sys.path.insert(0, 'azazael/src')
from CORE.compliance.orchestrator import ComplianceOrchestrator
from CORE.compliance.state_machine import ComplianceState

co = ComplianceOrchestrator()
co.state_machine.transition_to(ComplianceState.GATE_ASSERT)
# Compliance infrastructure is now hot: check_rule_0x(), check_rule_0y() ready
```

### Full Compliance Check

```python
from CORE.compliance import ComplianceOrchestrator

co = ComplianceOrchestrator()
co.state_machine.transition_to(ComplianceState.GATE_ASSERT)

result = co.check_all(
    action="str_replace",
    role="developer",
    context={
        "state": "CODE_EDIT",
        "can_edit": True,
        "can_review": False,
        "has_gate": True,
        "code_reviewed": True,
        "synced": True,
        "gate_decision": "PROCEED",
        "filepath": "path/to/file.py",
        "source_code": "# optional source for AST scanning",
    }
)

if result.all_passed:
    print(result.summary)  # ALL 8 RULE 0X + 5 RULE 0Y checks PASSED (score: 0.95)
else:
    print(result.summary)  # FAILING: 0X:state_machine, 0Y:judge_consensus (score: 0.45)
```

---

## ComplianceOrchestrator API

### Constructor

```python
co = ComplianceOrchestrator()
```

Creates all 13 components with defaults:
- **PolicyEngine**: Global singleton with developer/reviewer/auditor/guest rules
- **StateMachine**: Starts at `IDLE`, must be transitioned to `GATE_ASSERT`
- **FormalVerifier**: 4 default constraints (0J gate, 0V review, 0R sync, 0X valid state)
- **SchemaValidator**: Dict-based validation (pydantic optional fallback)
- **ComplianceScorer**: 7 metrics, halt threshold 0.5
- **ASTAntiPatternScanner**: 7 anti-pattern categories
- **ComplianceTelemetry**: 2000-event ring buffer
- **MultiAgentJudge**: 2 default judges (policy + state machine), 2/3 consensus
- **ConfidenceGate**: Threshold 0.7
- **BehavioralGraphAnalyzer**: networkx optional, dict fallback
- **DualLedgerValidator**: Reads `.audit/` JSONL + `~/.azazael/direct_memory.db`
- **RealtimeAuditPipeline**: 15-layer VLP (hardened mode enabled)

### check_all(action, role, context) -> ComplianceResult

**The main entry point.** Runs ALL 8 RULE 0X + 5 RULE 0Y component checks.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `action` | str | `""` | The action being evaluated (e.g., `"str_replace"`, `"write_file"`) |
| `role` | str | `"developer"` | Subject role (developer, reviewer, auditor, guest) |
| `context` | dict | `{}` | Evaluation context (see table below) |

**Context fields:**

| Field | Type | Default | Used By |
|-------|------|---------|---------|
| `state` | str | `"IDLE"` | StateMachine (0X-4), Judge (0Y-1) |
| `can_edit` | bool | `False` | StateMachine, Judge |
| `can_review` | bool | `False` | StateMachine, Judge |
| `has_gate` | bool | `False` | FormalVerifier (0X-3) |
| `code_reviewed` | bool | `False` | FormalVerifier |
| `synced` | bool | `True` | FormalVerifier |
| `filepath` | str | `""` | ASTScanner (0X-7), GraphAnalyzer (0Y-3), AuditPipeline (0Y-5) |
| `source_code` | str\|None | `None` | ASTScanner (0X-7) |
| `policy_score` | float | `1.0` | ConfidenceGate (0Y-2) |
| `formal_verified` | bool | `True` | ConfidenceGate |
| `reviewer_score` | float | `1.0` | ConfidenceGate |
| `gate_decision` | str | `"PROCEED"` | SchemaValidator (0X-5) |
| `scope_check_ok` | bool | `True` | SchemaValidator |
| `gemini_phase_ok` | bool | `True` | SchemaValidator |
| `anti_pattern_scanned` | bool | `False` | SchemaValidator |
| `batch_script_ok` | bool | `True` | SchemaValidator |
| `test_failure_handled` | bool | `True` | SchemaValidator |
| `concurrent_inference_ok` | bool | `True` | SchemaValidator |
| `post_phase_verified` | bool | `True` | SchemaValidator |
| `system_reminders_obeyed` | bool | `True` | SchemaValidator |
| `code_reviewer_spawned` | bool | `False` | SchemaValidator |
| `agent_utilization_ok` | bool | `True` | SchemaValidator |
| `audit_filepath` | str | `""` | AuditPipeline (0Y-5) |

**Returns** `ComplianceResult`:

| Attribute | Type | Description |
|-----------|------|-------------|
| `all_passed` | bool | True if ALL 0X + 0Y checks passed |
| `rule_0x` | dict | RULE 0X component results (8 components) |
| `rule_0y` | dict | RULE 0Y component results (5 components) |
| `score` | float | Weighted compliance score (0.0–1.0) |
| `summary` | str | Human-readable summary |
| `checked_at` | str | ISO timestamp |
| `to_dict()` | method | Serialize to plain dict |

### check_rule_0x(action, role, context) -> dict

Run only the 8 RULE 0X component checks. Returns:

```python
{
    "all_passed": bool,
    "components": {
        "policy_gate": {"allowed": bool, "reason": str, ...},
        "broker_interception": {"active": True, ...},
        "formal_verification": {"passed": bool, "passed_count": int, ...},
        "state_machine": {"valid": bool, "current_state": str, ...},
        "schema_validation": {"passed": bool, "errors": [], ...},
        "compliance_scoring": {"weighted_score": float, "should_halt": bool, ...},
        "ast_scanning": {"passed": bool, "findings": [], ...},
        "telemetry": {"active": True, "total_events": int, ...},
    },
    "component_count": 8,
}
```

### check_rule_0y(action, role, context) -> dict

Run only the 5 RULE 0Y governance checks. Returns:

```python
{
    "all_passed": bool,
    "components": {
        "judge_consensus": {"approved": bool, "consensus_ratio": float, ...},
        "confidence_gate": {"passed": bool, "aggregate_score": float, ...},
        "graph_analysis": {"anomalies_detected": int, "anomalies": [], ...},
        "dual_ledger": {"consistent": bool, "discrepancies": [], ...},
        "audit_pipeline": {"all_passed": bool, "layer_results": [], ...},
    },
    "component_count": 5,
}
```

### get_status() -> dict

Get the orchestrator's current runtime status:

```python
{
    "check_count": int,
    "state_machine": {"current_state": str, "transitions": int, ...},
    "score": {"weighted_score": float, "metrics": {...}},
    "telemetry": {"total_events": int, "by_type": {...}},
    "graph": {"total_actions": int, "action_counts": {...}},
    "rules": int,
}
```

### reset()

Reset all components to initial state (for testing or session reset). Clears:
- StateMachine back to `IDLE`
- ComplianceScorer metrics
- BehavioralGraphAnalyzer action history
- ASTAntiPatternScanner scan log

---

## Per-Component Pass/Fail Logic

Each component uses a **type-specific success key** (fail-closed — missing keys
default to `False`). No OR chains between unrelated keys.

### RULE 0X Component Checks (`_ox_component_passed`)

| Component | Success Key | Passes When |
|-----------|-------------|-------------|
| `policy_gate` | `allowed` | `True` |
| `broker_interception` | `active` | `True` |
| `formal_verification` | `passed` | `True` |
| `state_machine` | `valid` | `True` |
| `schema_validation` | `passed` | `True` |
| `compliance_scoring` | `should_halt` | `False` |
| `ast_scanning` | `passed` | `True` |
| `telemetry` | `active` | `True` |

### RULE 0Y Component Checks (`_oy_component_passed`)

| Component | Success Key | Passes When |
|-----------|-------------|-------------|
| `judge_consensus` | `approved` | `True` |
| `confidence_gate` | `passed` | `True` |
| `graph_analysis` | `anomalies_detected` | `== 0` |
| `dual_ledger` | `consistent` | `True` |
| `audit_pipeline` | `all_passed` | `True` |

---

## sentinel_gate.py Integration

The ComplianceOrchestrator is wired into `azazael/src/SCRIPTS/sentinel_gate.py`
as the programmatic backend for RULE 0X and RULE 0Y validation.

### How It Works

```python
# In sentinel_gate.py:
try:
    from CORE.compliance import ComplianceOrchestrator, ComplianceState
    from CORE.compliance.orchestrator import _ox_component_passed, _oy_component_passed
    _COMPLIANCE_AVAILABLE = True
except ImportError:
    _COMPLIANCE_AVAILABLE = False  # Graceful fallback
```

**Lazy singleton** — the orchestrator is created on first validation call:

```python
def _get_compliance_orchestrator():
    co = ComplianceOrchestrator()
    co.state_machine.transition_to(ComplianceState.GATE_ASSERT)
    return co
```

**`validate_rule_0x()`** — replaces old text assertion:
1. Gets/creates the orchestrator singleton
2. Transitions state machine to `GATE_ASSERT`
3. Calls `co.check_rule_0x()` with full context
4. Reports per-component results using `_ox_component_passed()`
5. Returns `(passed, message)` tuple

**`validate_rule_0y()`** — replaces old text assertion:
1. Same pattern as 0x
2. Calls `co.check_rule_0y()` with governance context
3. Reports per-component results using `_oy_component_passed()`
4. Returns `(passed, message)` tuple

**Graceful degradation** — if ComplianceOrchestrator can't be imported,
both functions return `(True, "N/A — ComplianceOrchestrator not available")`
so the gate still functions without the full infrastructure.

### Running the Gate

```bash
# Validate a PRE-ACTION GATE assertion from stdin
echo "{AP-1: Yes, user asked for this...}" | python sentinel_gate.py --validate

# With audit cross-reference
echo "{...}" | python sentinel_gate.py --validate --audit .audit/session_X.jsonl
```

---

## Package Imports

All 16 classes are exported from `CORE.compliance.__init__`:

```python
from CORE.compliance import (
    # RULE 0X
    PolicyEngine, PolicyRule, enforce_gate, BrokerInterceptor, default_policy_rules,
    ComplianceStateMachine, ComplianceState, StateMachineError, FormalVerifier,
    verify_rule_set,
    SchemaValidator, ComplianceScorer, build_gate_schema,
    ASTAntiPatternScanner, AntiPatternResult, scan_file,
    ComplianceTelemetry, TelemetryEvent,
    # RULE 0Y
    MultiAgentJudge, JudgeVerdict, ConfidenceGate,
    BehavioralGraphAnalyzer, DualLedgerValidator, RealtimeAuditPipeline,
    # Orchestrator
    ComplianceOrchestrator, ComplianceResult,
)
```

Or import individual components:

```python
from CORE.compliance import ComplianceOrchestrator  # Most common
from CORE.compliance.orchestrator import _ox_component_passed, _oy_component_passed  # For custom checks
from CORE.compliance.state_machine import ComplianceState  # For transitions
```

---

## Key Design Decisions

1. **Fail-closed defaults**: Every component check defaults to `False` (reject).
   Missing or corrupted data never produces a false positive.

2. **No OR chains**: Each component has exactly ONE semantically correct success key.
   No `allowed or passed or valid` chains that mask failures.

3. **Graceful fallbacks**: All optional libraries (wrapt, pydantic, networkx) are
   wrapped in try/except. The infrastructure works with stdlib only.

4. **Thread safety**: All mutable state is protected by `threading.Lock` or
   `threading.RLock`. The orchestrator itself uses a Lock for `_check_count`.

5. **No stdlib shadowing**: Only `azazael/src/` is added to `sys.path` (not
   `azazael/src/CORE/`) to avoid `CORE/logging.py` masking the stdlib `logging`
   module.

6. **Verifiable telemetry**: Every check emits a `ComplianceTelemetry` event with
   pass/fail/error status, component name, and structured details. The telemetry
   ring buffer provides an audit trail for every compliance decision.

---

## Common Usage Patterns

### Before Every Code Edit (Full Check)

```python
result = co.check_all(
    action="str_replace",
    role="developer",
    context={
        "state": "CODE_EDIT",
        "can_edit": True,
        "has_gate": True,
        "code_reviewed": True,
        "synced": True,
        "filepath": "target_file.py",
        "source_code": source_string,  # For AST scanning
        "gate_decision": "PROCEED",
    }
)
if not result.all_passed:
    print(f"HALT: {result.summary}")
    # Handle gate failure
```

### Checking Only Policy (No State Machine)

```python
from CORE.compliance import ComplianceOrchestrator
co = ComplianceOrchestrator()
ox = co.check_rule_0x(action="write_file", role="developer")
if ox["components"]["policy_gate"]["allowed"]:
    print("Developer is authorized to write files")
```

### Inspecting Judge Consensus

```python
oy = co.check_rule_0y(action="delete_file", role="developer")
judge = oy["components"]["judge_consensus"]
print(f"Approved: {judge['approved']} ({judge['approved_count']}/{judge['total_judges']})")
for jid, verdict in judge["verdicts"].items():
    print(f"  {jid}: {'APPROVE' if verdict['approved'] else 'DENY'} ({verdict['confidence']})")
```

### Checking AST for Anti-Patterns

```python
from CORE.compliance.scanner import scan_file, ASTAntiPatternScanner

# Single file (convenience)
result = scan_file("path/to/file.py")
print(f"Passed: {result.passed}, Findings: {result.finding_count}")

# Custom scanner
scanner = ASTAntiPatternScanner()
result = scanner.scan_source("test.py", "def foo():\\n    return 42")
assert result.passed
```

### Reset Between Sessions

```python
co.reset()  # StateMachine -> IDLE, scores cleared, graph cleared
```

---

## Running the Self-Test

```bash
python azazael/src/CORE/compliance/orchestrator.py
```

This runs 8 tests covering all 13 components. Test 8 requires the state machine
to be in `CODE_EDIT` — the self-test handles this internally via
`co.state_machine.transition_to(ComplianceState.CODE_EDIT)`.

### Self-Test Coverage

| Test | Component(s) | What It Checks |
|------|-------------|----------------|
| 1/8 | PolicyEngine | Developer allowed, Guest denied |
| 2/8 | StateMachine | 5 legal transitions + illegal transition blocked |
| 3/8 | FormalVerifier | 4 default constraints pass with valid context |
| 4/8 | SchemaValidator | Valid gate data passes 11-field schema |
| 5/8 | ComplianceScorer | Weighted score >0.5 with all passes, no halt |
| 6/8 | ASTAntiPatternScanner | Clean code passes, dirty code detects 2 issues |
| 7/8 | MultiAgentJudge | 2/3 consensus approves, ratio >= 0.67 |
| 8/8 | ComplianceOrchestrator | Full check_all() returns ComplianceResult with 13 components |

---

## File Locations

| Component | Path |
|-----------|------|
| Package init | `azazael/src/CORE/compliance/__init__.py` |
| Orchestrator | `azazael/src/CORE/compliance/orchestrator.py` |
| Policy | `azazael/src/CORE/compliance/policy.py` |
| State Machine | `azazael/src/CORE/compliance/state_machine.py` |
| Validating | `azazael/src/CORE/compliance/validating.py` |
| Scanner | `azazael/src/CORE/compliance/scanner.py` |
| Telemetry | `azazael/src/CORE/compliance/telemetry.py` |
| Governance | `azazael/src/CORE/compliance/governance.py` |
| Sentinel Gate | `azazael/src/SCRIPTS/sentinel_gate.py` |
| Startup Skill | `azazael/skills/azazael-system-startup.md` (Step 4.5) |
| Checklist | `azazael/COMPLIANCE_CHECKLIST.md` |
