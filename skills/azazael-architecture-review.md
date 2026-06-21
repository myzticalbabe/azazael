---
name: azazael-architecture-review
description: Systematic project architecture review methodology — 3-pass inventory, 12-dimension quality scoring, coupling/cohesion analysis, TODO cross-referencing. Load before reviewing project structure or updating production plans.
metadata:
  category: architecture
  project: azazael
  version: 1.0.0
---

# Azazael Architecture Review Methodology

## Overview

This skill documents the systematic 3-pass approach for reviewing all projects in the Azazael ecosystem. It produces a comprehensive architecture quality scorecard and actionable improvement items cross-referenced against existing plans.

**Why:** The Azazael ecosystem spans 13+ sub-layers, 14 Desktop projects, an archive, package infrastructure, and test infrastructure. A disciplined review methodology ensures no project is missed and findings integrate cleanly with existing TODO documents.

---

## Pass 1: Inventory (What exists)

### Step 1: Load context
```bash
# Load all architecture skills
skill azazael-architecture
skill azazael-files
skill azazael-production

# Read existing analysis documents
read_files AZAZAEL_ARCHITECTURE_ANALYSIS.md PROJECT_MAP.md PATH_FORWARD.md
```

### Step 2: Explore directory trees
```bash
# For each major directory, read the subtree to understand structure
read_subtree paths=["src/CORE", "src/CORE/WORMS", "src/CODEX", "src/ORCHESTRATION"]
read_subtree paths=["packages"]
```

### Step 3: Read all TODO documents
```bash
# Read every TODO document to understand existing plans
read_files CODEBASE_AUDIT_TODO.md PRODUCTION_TODO.md REWRITE_TODO.md PHASE_6_TODO.md
```

### Step 4: Cross-reference
```bash
# Does the inventory match existing documentation?
# Flag discrepancies: files that exist but aren't documented,
# or documented projects that no longer exist.
```

**Checklist:**
- [ ] All sub-layers inventoried (CORE, WORMS, CODEX, ORCHESTRATION, HYDRA, META, UTILITIES, root *.py, AZAZAEL_TOOLKIT, TOOLS, SCRIPTS, CLI)
- [ ] Desktop Standalone Suite inventoried (EXE count, BAT count, build system)
- [ ] External Desktop projects inventoried (all 14, with status)
- [ ] G: Drive archive inventoried (size, contents, sync status)
- [ ] Package system inventoried (azazael-core scaffold, sys.path.insert count)
- [ ] Test infrastructure inventoried (test files, counts, known issues)
- [ ] Cross-reference with PROJECT_MAP.md for accuracy
- [ ] Cross-reference with PATH_FORWARD.md for separation plan alignment

---

## Pass 2: Rate (How healthy)

For each project/layer, rate on 3 axes:

### Cohesion (0.0-1.0)
How well do the files in this directory relate to each other?

| Score | Meaning | Example |
|-------|---------|---------|
| 0.9-1.0 | Highly cohesive — all files serve one purpose | CODEX/ (all video generation) |
| 0.6-0.8 | Moderately cohesive — mixed but related purposes | ORCHESTRATION/ (deployment + ML + analysis) |
| 0.3-0.5 | Weakly cohesive — unrelated files together | Root *.py files (30+ standalone entry points) |
| 0.0-0.2 | Not cohesive — just a dumping ground | META/ (deprecation shims being phased out) |

### Coupling (1-10)
How many outbound dependencies does this module have?

| Score | Meaning | Example |
|-------|---------|---------|
| 1-3 | Low coupling — few imports, independent | CLI/ (thin layer, 2 files) |
| 4-6 | Moderate coupling — several dependencies | UTILITIES/ (depends on CORE partially) |
| 7-9 | High coupling — many dependents/dependencies | CORE/WORMS/ (depends on CORE + registry) |
| 9-10 | Critical coupling — single point of failure | CORE/paths.py (139+ inbound deps) |

### Health (🔴/🟡/🟢)
Qualitative assessment of maintainability and completeness.

| Health | Meaning | Example |
|--------|---------|---------|
| 🟢 Healthy | Well-structured, actively maintained | CODEX/, CORE/WORMS/ |
| 🟡 Mixed | Functional but has known issues | ORCHESTRATION/, UTILITIES/ |
| 🔴 Poor | Deprecated, unmaintained, or being phased out | META/, legacy Desktop projects |

---

## Pass 3: Scorecard (System-wide metrics)

Rate on 12 dimensions (1-10):

| Dimension | What to Assess | Score Guide |
|-----------|---------------|-------------|
| **Modular cohesion** | Are modules well-grouped by purpose? | 7-10: Clear boundaries, 4-6: Some mixing, 1-3: Random |
| **Inter-module coupling** | Are dependencies manageable? | 7-10: Low coupling, 4-6: Moderate, 1-3: Tightly coupled |
| **Dependency hygiene** | Are shims and circular imports zero? | 10: No shims/no cycles, 5: Some shims, 1: Many |
| **Type safety** | What's the mypy error count? | 10: 0 errors, 7: <100, 4: <500, 1: 1000+ |
| **Test coverage** | What % of code is tested? | 10: >80%, 7: >50%, 4: >20%, 1: <10% |
| **Documentation** | Are skills, docs, module docstrings present? | 10: Complete, 7: Good, 4: Minimal, 1: None |
| **Build system** | Are builds reproducible? | 10: CI/CD, 7: Scripted, 4: Manual, 1: None |
| **3.14t readiness** | Does it work on free-threading? | 10: Tested, 7: Most packages, 4: Some issues, 1: Broken |
| **Shell injection safety** | Any shell=True with dynamic vars? | 10: None, 7: <3, 4: <10, 1: Many |
| **Package management** | Is it pip-installable? | 10: Published, 7: Scaffolded, 4: sys.path hacks, 1: Not |
| **Desktop integration** | Do Desktop projects connect? | 10: Full integration, 7: Some, 4: Minimal, 1: None |
| **Overall** | Weighted average of above | Calculate manually |

**Important:** If this scorecard adds new dimensions not previously scored (e.g., shell injection safety, package management), the overall score will be lower than previous ratings even if underlying quality is unchanged. Document this difference explicitly to avoid confusion.

---

## Cross-Referencing: Integrating Findings with Existing Plans

After the review, you'll have 10-15 new improvement items. These must be integrated with existing TODO documents without creating duplicates or conflicts.

### Classification Scheme

Each item gets one of three labels:

| Label | Meaning | Action |
|-------|---------|--------|
| ✅ **ADDITIVE** | Not covered by any existing Step | Add to roadmap as new item |
| ⚠️ **REINFORCES** | Overlaps an existing Step but adds new detail | Add as sub-item or note under existing Step |
| 🔴 **DUPLICATE** | Already fully covered | Skip — no action needed |

### Cross-Reference Table

```
| # | AR-ID | Action | Existing Step | Additive? |
|---|-------|--------|---------------|-----------|
| 1 | AR-1  | Fix shell=True usages | New | ✅ Additive |
| 2 | AR-11 | Fix mypy errors | Step 7 (perf opt) | ⚠️ Reinforces |
| 3 | AR-7  | Add pytest-cov | Step 3 (tests) | ⚠️ Reinforces |
```

### Track the Ratio

- **>50% additive** → The TODO was missing significant scope (review uncovered genuine gaps)
- **20-50% additive** → The TODO was moderately comprehensive (review validated + extended)
- **<20% additive** → The TODO was already comprehensive (review validated existing planning)

---

## Quality Scorecard Template

Copy this into the review document:

```markdown
## Architecture Quality Scorecard

| Dimension | Score (1-10) | Assessment | Key Improvement |
|-----------|-------------|------------|-----------------|
| **Modular cohesion** | 7.2 | Good — nature clusters have clear boundaries | N/A |
| **Inter-module coupling** | 5.5 | Poor — CORE/ is over-coupled | Split paths.py into domain modules |
| **Dependency hygiene** | 6.0 | Fair — X shims remain | Delete after verification |
| **Type safety** | 7.5 | Improving — X rounds of cleanup done | Fix remaining errors |
| **Test coverage** | 3.5 | Critical gap — <X% coverage | Add test reporting |
| **Documentation** | 6.0 | Fair — X skills, good docs | Add module docstrings |
| **Build system** | 7.0 | Good — X EXEs, build pipeline | Add smoke tests |
| **3.14t readiness** | 8.0 | Strong throughout | Monitor for wheel issues |
| **Shell injection safety** | 5.5 | X HIGH RISK usages | Refactor to subprocess.call |
| **Package management** | 4.0 | Scaffolded but unused | Switch to editable pip install |
| **Desktop integration** | 6.5 | All have run.py, no core integration | Evaluate key projects |
| **Overall** | **X.X/10** | | X improvement items |
```

---

## Improvement Items Template

```
| ID | Item | Effort | Impact | Priority |
|----|------|--------|--------|----------|
| AR-1 | Fix X shell=True HIGH RISK usages | 2h | 🔴 High | P0 |
| AR-2 | ... | ... | ... | ... |
```

**Priority guide:**
| Priority | Timeline | Criteria |
|----------|----------|----------|
| P0 | This session | Security risk or blocking |
| P1 | Next 3 sessions | Significant quality improvement |
| P2 | Within 5 sessions | Important but not urgent |
| P3 | Future | Nice-to-have or low impact |

---

## Companion Skills

- `azazael-todo-management` — Use this AFTER completing an architecture review to integrate findings into TODO documents
- `azazael-architecture` — Project layout and module organization
- `azazael-files` — Complete file index and import resolution
- `azazael-production` — Production readiness roadmap and gaps
- `azazael-sop` — Error recording and pre-session checklist
- `azazael-testing` — Validation commands and pre-commit checks

## Related Lessons

- Lesson #39 — Architecture Efficiency Ratings: Measure Before Refactoring (original 8-dimension scoring)
- Lesson #41 — Architecture Review Methodology (this skill's methodology in narrative form)
- Lesson #42 — TODO Document Versioning: Cross-Reference New Items Against Existing Plan Steps
