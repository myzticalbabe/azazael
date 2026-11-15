"""
Azazael Project — Comprehensive Module Health Check
Tests all core modules and reports pass/fail status.
"""

import sys
import importlib
import time
from pathlib import Path

# This file lives in <repo>/tools/ and every module it checks lives under
# <repo>/src/. The line that used to be here pointed at
# `~/Desktop/azazael-project-e`, a directory that does not exist on this box,
# so every single import failed for a reason that had nothing to do with the
# module under test.
REPO = Path(__file__).resolve().parents[1]
for _sub in ("", "src", "src/ORCHESTRATION", "src/TOOLS"):
    _p = REPO / _sub if _sub else REPO
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# The status glyphs below cannot be encoded in cp1252, the default stdout
# codec here: the first FAIL raised UnicodeEncodeError and the run died before
# printing any summary. Degrade the glyph, keep the report.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

MODULES = [
    # Expected symbols were re-derived from `dir(module)` on 2026-11-15, not
    # carried over. Four of the old entries could never match: two were prose
    # ("FusionHealer class", "ML_ORCH class") and never resolved through
    # hasattr, and three named symbols that no longer exist (AdaptationType,
    # SystemInfo, SystemManagerApp). Each of those reported PASS anyway,
    # because the only thing checked was that the import succeeded.
    # Core framework
    ("ADLP_FusionCore", "ADLP_FusionCore", "FusionCore, CORE, TIER, LVL"),
    ("FusionHealer", "FusionHealer", "FusionHealer"),
    ("HYDRA", "HYDRA", "HYDRACluster, ProcessingStage, ClusterConfig"),
    # System tools
    ("SystemManager", "SystemManager", "SystemManager, SystemCrawler, SystemComponent"),
    ("SystemManagerGUI", "SystemManagerGUI", "SystemManagerGUI, WormCanvas"),
    ("SelfImprovingGUI", "SelfImprovingGUI", "SelfImprovingGUI, GUIStatus"),
    # Python mapper
    ("PythonMapper_Quick", "PythonMapper_Quick", "QuickMapper"),
    # Assistant protocol
    ("AssistantLogProtocol", "AssistantLogProtocol", "AssistantLogProtocol, LogEntry"),
    # ML orchestrator
    ("ADLP_MLOrchestrator", "ADLP_MLOrchestrator", "ML_ORCH, MLOrchestrator"),
    # System tools core
    ("ADLP_SystemTools", "ADLP_SystemTools", "SystemToolExecutor, SystemToolResult"),
]

PASSED = 0
FAILED = 0
WARNED = 0
RESULTS = []

# A declared symbol has to be a bare identifier. The table above used to hold
# "FusionHealer class" and "ML_ORCH class" -- prose that `hasattr` can never
# resolve -- so those two modules were graded on their import alone and
# reported PASS while exporting none of the names the line claimed. Refuse to
# run on an unusable expectation instead of quietly printing a green tick.
_BAD_EXPECTATIONS = [
    (mod_name, symbol)
    for mod_name, _import_name, contents in MODULES
    for symbol in (token.strip() for token in contents.split(","))
    if symbol and not symbol.isidentifier()
]
if _BAD_EXPECTATIONS:
    print("health check: %d unusable expected symbol(s):" % len(_BAD_EXPECTATIONS))
    for _mod, _sym in _BAD_EXPECTATIONS:
        print("  %-30s %r is not a Python identifier" % (_mod, _sym))
    raise SystemExit(2)

print("=" * 70)
print("  AZAZAEL PROJECT — COMPREHENSIVE HEALTH CHECK")
print("=" * 70)
print()

for mod_name, import_name, contents in MODULES:
    start = time.perf_counter()
    try:
        mod = importlib.import_module(import_name)
        elapsed = time.perf_counter() - start

        # Verify expected contents exist. PASS means every declared symbol is
        # present; an import that succeeds while exporting none of them is a
        # WARN naming what is gone, because that is the state that used to be
        # reported as a green tick.
        expected = [s.strip() for s in contents.split(",") if s.strip()]
        missing = [s for s in expected if not hasattr(mod, s)]
        if missing:
            status = "~ WARN"
            WARNED += 1
            detail = "%d/%d symbols; missing: %s" % (
                len(expected) - len(missing), len(expected), ", ".join(missing))
        else:
            status = "PASS"
            PASSED += 1
            detail = "%d/%d symbols found in %.2fs" % (len(expected), len(expected), elapsed)
    except Exception as e:
        elapsed = time.perf_counter() - start
        status = "FAIL"
        FAILED += 1
        detail = f"{type(e).__name__}: {e}"

    RESULTS.append((mod_name, status, detail))
    print(f"  {status}  {mod_name:<30s} {detail}")

TOTAL = PASSED + FAILED + WARNED
print()
print("=" * 70)
print("  SUMMARY:  %d/%d healthy, %d warned, %d failed (%.1f%%)" % (
    PASSED, TOTAL, WARNED, FAILED, PASSED / TOTAL * 100 if TOTAL else 0.0))
print("=" * 70)
print()
