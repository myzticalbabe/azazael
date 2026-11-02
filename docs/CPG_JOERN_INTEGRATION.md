# CPG Layer via Joern — Integration Design

**Task:** Board 46999 / YGGDRASIL-CLEAVE-K4
**Date:** 2026-11-02
**Author:** opencode lane (max reasoning)

## Problem

The codebase lacks a Code Property Graph (CPG) layer for pattern mining. Static
analysis is limited to AST-level queries. Joern provides CPGQL for multi-language
pattern detection.

## What is a CPG?

A Code Property Graph combines:
- **AST** (Abstract Syntax Tree): syntactic structure
- **CFG** (Control Flow Graph): execution paths
- **PDG** (Program Dependence Graph): data and control dependencies

Together, these enable queries like "find all functions that write to a global
variable without a lock" or "find all SQL queries built from string concatenation."

## Integration Plan

### Phase 1: Joern installation (Windows/WSL)

Joern runs on JVM. Install via:
```bash
# In WSL (Ubuntu)
curl -L https://github.com/joernio/joern/releases/latest/download/joern-cli.zip -o joern.zip
unzip joern.zip -d /opt/joern
export PATH=$PATH:/opt/joern/bin
```

### Phase 2: CPG generation

```bash
joern --src /root/azazael/src --output /root/azazael/cpg.bin
```

### Phase 3: CPGQL queries for common patterns

```scala
// Find all functions with more than 50 lines
cpg.method.filter(_.numberOfLines > 50).name

// Find all except: pass handlers
cpg.tryBlock.where(_.catches.exists(_.body.isPass)).location

// Find all global variable writes without lock
cpg.assignment.where(_.target.isIdentifier).filter(_.target.name.startsWith("self._"))

// Find all SQL string concatenations
cpg.call.name("execute").where(_.argument(0).code.contains("+"))
```

### Phase 4: Integration with azazael

- Add `tools/joern_cpg.py` wrapper that runs Joern and exports CPGQL results
- Add CPG queries to the evidence gate (replace AST-only checks)
- Add CPG-based pattern mining to the scanner

### Deliverable checklist

- [x] CPG concept documented
- [x] Joern installation plan (WSL)
- [x] CPGQL query examples
- [x] Integration plan with azazael
- [x] Tool wrapper specified (tools/joern_cpg.py)