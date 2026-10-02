---
name: azazael-mermaid
description: Azazael Mermaid graph generation — diagram patterns (graph TD, sequenceDiagram), ASCII safety rules, graph generation from clusters, execution flow visualization.
metadata:
  category: conventions
  project: azazael
---
# Azazael Mermaid — Graph Generation Patterns

## Critical Rule: ASCII Only

**Never use Unicode characters in Mermaid output.** Windows terminals without `PYTHONIOENCODING=utf-8` will crash.

| ❌ Unicode | ✅ ASCII |
|-----------|---------|
| `✓` check mark | `OK` |
| `✗` ballot x | `FAIL` |
| `🔷` blue diamond | `*` |
| `⚡` high voltage | `>>` |

## Graph Types Used in the Codebase

### Graph TD (Top-Down) — Architecture & Hierarchy
Used in CLUSTERWORMS, METACLUSTER v2 (U3: NATURE_CLUSTERS deleted):
```python
def to_mermaid(self) -> str:
    lines = ["graph TD"]
    lines.append(f'    MC[MetaCluster] --> C1[monitor]')
    lines.append(f'    C1 --> W1[VulnScanner p=8]')
    lines.append(f'    C1 --> W2[PortAuditor p=7]')
    lines.append(f'    MC --> C2[security]')
    lines.append(f'    classDef ok fill:#1a3a1a,stroke:#00ff88,color:#00ff88')
    lines.append(f'    class W1,W2 ok')
    return "\n".join(lines)
```

### Execution Flow Graph
Used in CLUSTERWORMS.execute_all():
```python
def to_mermaid_execution_flow(self, results) -> str:
    lines = ["graph TD"]
    total = len(results)
    ok = sum(1 for r in results if r.get("success"))
    fail = total - ok
    lines.append(f'    title["CODEX Execution Flow: {self.cluster_type}"]')
    lines.append(f'    title --> stats["{ok} OK / {fail} FAIL"]')
    for i, r in enumerate(results):
        status = "OK" if r.get("success") else "FAIL"
        name = r.get("name", f"worm_{i}")
        lines.append(f'    {name}["{name}: {status}"]')
    return "\n".join(lines)
```

### Sequence Diagram — Execution Timeline
```python
def to_mermaid_sequence(self) -> str:
    lines = ["sequenceDiagram"]
    lines.append("    participant User")
    lines.append("    participant ClusterWORMZ")
    lines.append("    participant WormRegistry")
    lines.append("    participant WormExecutor")
    lines.append("    User->>ClusterWORMZ: build_from_nature('security')")
    lines.append("    ClusterWORMZ->>WormRegistry: get_worms_by_category()")
    lines.append("    WormRegistry-->>ClusterWORMZ: [VulnScanner, PortAuditor, ...]")
    lines.append("    ClusterWORMZ->>WormExecutor: execute_parallel(configs)")
    lines.append("    WormExecutor-->>ClusterWORMZ: [results]")
    return "\n".join(lines)
```

## Color & Styling

### Status-Based Class Definitions
```python
lines.append("    classDef ok fill:#1a3a1a,stroke:#00ff88,color:#00ff88")
lines.append("    classDef fail fill:#3a1a1a,stroke:#ff4444,color:#ff4444")
lines.append("    classDef running fill:#1a1a3a,stroke:#4488ff,color:#4488ff")
lines.append("    classDef pending fill:#2a2a2a,stroke:#666666,color:#888888")
```

### Applying Classes
```python
for r in results:
    if r.get("success"):
        ok_worms.append(r["name"])
    else:
        fail_worms.append(r["name"])
if ok_worms:
    lines.append(f"    class {','.join(ok_worms)} ok")
if fail_worms:
    lines.append(f"    class {','.join(fail_worms)} fail")
```

## Where Mermaid is Generated

| File | Method | Type |
|------|--------|------|
| `CLUSTERWORMS.py` | `to_mermaid_execution_flow()` | Graph TD — execution results |
| `METACLUSTER.py` | `to_mermaid()` | Graph TD — flat category graph (U3: was cross-nature routes) |
| `METACLUSTER.py` | Custom methods | Sequence diagram — orchestration flow |

## Output Size Guidelines

- Architecture graphs: 500-2000 chars
- Execution flow graphs: 1000-5000 chars (depends on worm count)
- Sequence diagrams: 500-1500 chars
- Largest measured output was NATURE_CLUSTERS' 8,535 chars (module deleted U3; re-measure for v2 graphs)

## Related Skills
- `azazael-conventions` — Parent: Python coding patterns, thread safety, factory methods
- `azazael-clusters` — CLUSTERWORMS, METACLUSTER v2 flat (all generate Mermaid)
- `azazael-codex` — CODEX video generation (uses Mermaid for flow diagrams)
