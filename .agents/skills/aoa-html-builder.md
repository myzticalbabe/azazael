---
name: aoa-html-builder
description: AOA Architecture HTML Builder — generates professional Mermaid-based
  architecture disclosure documents. Windows Git Bash heredoc workaround
  (short-line strategy), colorized classDef patterns, 7-diagram layout,
  particle JS, benchmark cards, arm capability tables.
metadata:
  category: documentation
  projects: aoa, azazael
---

# AOA HTML Builder — Professional Architecture Disclosure

## Problem Solved

Building large HTML files with embedded Mermaid diagrams on Windows Git Bash
fails when using heredocs because long lines (>120 chars) get silently
truncated. This skill documents the short-line strategy that works.

## The Short-Line Heredoc Strategy

### Rule: Every heredoc line MUST be under 100 characters

When writing Python scripts via `cat > file.py << 'EOF'`, break ALL long
strings into fragments joined at the Python level:

```python
# Build output list
O = []
def A(*lines):
    for line in lines:
        O.append(line)

# CSS: one property per line
A('body{background:#06060e;')
A('color:#d1d5db;')
A('font-family:system-ui}')

# Mermaid: each diagram line as separate string
M1 = [
    'graph TB',
    '    AOA{{"AOA Umbrella v1.1.0"}}',
    '    AZ["Azazael<br/>77 Worms"]',
    '    AOA --> AZ',
]
A(*M1)

# Write output
out = '\n'.join(O)
with open(path, 'w', encoding='utf-8') as f:
    f.write(out)
```

### Anti-Patterns (DO NOT USE)

- `python << 'EOF'` with long f-strings — truncates
- `python -c "..."` with complex Mermaid — shell escaping chaos
- Line-by-line injection into existing HTML — injection markers don't match
- File write outside project root via `str_replace` — fails silently
- `cat > file.py << 'EOF'` with lines >120 chars — GIT BASH TRUNCATES
- **Literal `\n` join (REAL INCIDENT 2026-09-02): `f.write('\\n'.join(H))`** — the
  double-escaped backslash-n emits the ENTIRE HTML as ONE line of literal `\n`
  characters instead of real newlines. Chrome then throws
  `SyntaxError: Invalid or unexpected token @ :0` on the inline
  `<script>mermaid.initialize(...)` because a literal `\` outside a string is an
  invalid JS token. The structural HTML audit does NOT catch it (single giant
  line passes string checks); only rendering does. SAFE FORM:
  `f.write('\n'.join(H))` (single backslash = real newline escape).

### Literal-newline verification (after ANY builder edit)

```bash
# file inside src/AOA builds correctly; expect many lines, zero literal backslash-n
python -c "import sys; d=open('AOA_STRUCTURE.html',encoding='utf-8').read();\
print('lines:', len(d.split(chr(10))), '| literal-backslash-n:', chr(92)+'n' in d)"
# should print: lines: ≥100 · literal-backslash-n: False
```

Plus the CDP render harness (`verify_aoa_cdp.py` at project root) — a rebuilt
HTML must load with **0 console errors / 0 exceptions** (catches both the
literal-`\n` join and any other inline-JS breakage).

## Builder status map (audited 2026-09-02)

Know which `src/AOA/` builder is canonical before editing or regenerating:

| Builder | Status | Notes |
|---|---|---|
| `build.py` | ✅ **CANONICAL** (regenerate AOA_STRUCTURE.html) | Registry-driven since 2026-09-02 — imports arm modules to snapshot live arms/caps, renders the diagram from source, pulls worm count live (falls back to `benchmark_data.json`); emits the audit-required quoted `<meta name="viewport" …>` and live arm-count badges; safe `'\n'` join (REAL-INCIDENT fix above) |
| `build_disclosure.py` | ✅ **CANONICAL** (regenerate AOA_DISCLOSURE.html) | Same registry-driven rebuild; flat node-list diagram with orchestrator summary; safe `'\n'` writer |
| `gen_html.py` | ✅ **CLEAN, legacy** (older flat variant of build.py) | Byte-verified 2026-09-02: `f.write("\n".join(parts))` is the correct single-escape newline join (0 double-escapes); isolated run produced 84 real lines / zero literal `\n`. Pre-dates the registry-driven rebuild — emits static 8-era content if run; regenerating via build.py is recommended |
| `build_final.py` | ⚠️ **NON-WRITING STUB — do not use** | Reads AOA_STRUCTURE.html and assembles extra diagram content into `N` via `w()` (`line+'\n'`, correct), but ends at `print(f'Built {len(N)} lines')` — **never writes back to disk**. Incomplete variant; treated as dead code |

Only `build.py` / `build_disclosure.py` should be edited; their outputs are what
ships. `gen_html.py` and `build_final.py` are legacy — verified clean of the
literal-`\n` defect (0 double-escapes), but not the canonical producers.

## Mermaid Color System

### Arm Color Palette (classDef per arm)

| Arm | Fill | Stroke | Text |
|-----|------|--------|------|
| Azazael | #1a0a2e | #7c3aed / #a855f7 | #c4b5fd |
| CODEX | #1a1200 | #f59e0b / #fbbf24 | #fde68a |
| EveUnleashed | #001a10 | #10b981 / #34d399 | #a7f3d0 |
| Libra | #00102a | #3b82f6 / #60a5fa | #bfdbfe |
| PAMS | #1a0010 | #f43f5e | #fecdd3 |
| PerfMon | #001a1a | #06b6d4 | #a5f3fc |
| LlamaServer | #0a0020 | #8b5cf6 | #ddd6fe |
| AgentSelector | #0a0a1a | #818cf8 | #e0e7ff |

### Node Shapes by Function

| Shape | Mermaid Syntax | Use Case |
|-------|---------------|----------|
| Rectangle | `[text]` | Standard arms, processes |
| Stadium | `([text])` | Endpoints, outputs |
| Diamond | `{{text}}` | Orchestrators, registries |
| Hexagon | `{{text}}` | Meta-objects, top-level |
| Subgraph | `subgraph NAME["title"]` | Category groupings |
| Database | `[(text)]` | Storage, memory systems |
| Rounded | `(text)` | Optional/auxiliary nodes |
| Asymmetric | `>text]` | Async flows, streams |
| Slanted | `[/text/]` | I/O, file operations |

## The 7-Diagram Architecture Layout

1. **Quartet Architecture** (graph TB) — Top-level, all arms (8 at original build; **9 since the Kali Toolchain arm was added 2026-09-02** — regenerate AOA_STRUCTURE.html via build.py to reflect the kali arm), classDef colored
2. **Cross-Arm Pipeline** (graph LR) — Data flow, step sequence
3. **Neural Core Topology** (graph TB + subgraphs) — Internal arm detail
4. **Neural Data Pathways** (sequenceDiagram) — Message passing
5. **Session Lifecycle** (stateDiagram-v2) — State machine
6. **Memory Architecture** (graph LR) — PAMS DirectMemory
7. **Worm Cluster Topology** (graph TB + subgraphs) — Azazael meta-cluster

## Build Pipeline

1. Read `benchmark_data.json` for live metrics
2. Build HTML head with Mermaid CDN and dark theme config
3. Build CSS (one property per line in heredoc)
4. Build 7 Mermaid diagrams (each line <100 chars)
5. Build arm capability table from arm data
6. Build benchmark cards from live metrics
7. Build color legend
8. Build particle JS canvas animation (80 particles)
9. Build clean footer (NO session IDs, regression notes, or codebuff refs)
10. Write to `AOA_STRUCTURE.html`

## Verification Checklist

- File size: >15KB
- Mermaid diagrams: exactly 7 (`class="mermaid"` count)
- DOCTYPE at position 0-1 (not after CSS)
- CSS inside `<head>`, not before DOCTYPE
- CDN script src: no newlines in URL
- Footer: no "codebuff", "session_end", "Regression", or "MEDIUM crash"
- Particle JS: `requestAnimationFrame` present
- Arm table: `<th>Arm</th>` present
- Stats cards: 8 `class="stat"` divs

## Related Skills

- `azazael-mermaid` — Mermaid ASCII safety rules, graph types, color patterns
- `azazael-clusters` — ClusterWORMZ, MetaCluster topology
- `azazael-worms` — Full 77-worm catalog for worm diagrams
- `azazael-crossplat-fileops` — Safe Windows/Git Bash file operations
- `azazael-architecture` — Project layout, key numbers
- `html-render-verification` (#1248) — run after EVERY build: the CDP render check that catches the literal-`\n` / unterminated-string traps (audit ≠ render)
- `aoa-artifact-cross-check` (#1250) — run after every rebuild: proves the shipped diagrams are TRUTHFUL against the live registry (render check + truth check = the complete verification pair)
- `builder-status-discipline` (#1252) — which producer is canonical: only `build.py` / `build_disclosure.py` are editable; the status map lives here
- `pre-action-gate-lite` (#1253) — fix-then-REVERIFY + corpus isolation scan whenever a builder output fails

## Lessons Learned

1. **Heredoc truncation on Windows Git Bash is real.** Lines >120 chars
get silently cut. The fix: break everything into short fragments.
2. **Injection strategies fail.** Markers don't match, regexes miss.
Build from scratch every time.
3. **CSS before DOCTYPE is invalid HTML.** Always put DOCTYPE first,
then `<head>` with `<style>` inside.
4. **CDN URLs with embedded newlines break.** Keep `src` attributes on
one line.
