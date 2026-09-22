"""Per-function pre-flight auditor for the Azazael neural mesh architecture.

Walks the mesh modules, runs a fixed battery of static pre-flight probes against
every function, and emits a checkbox TODO so the audit can be worked through one
function at a time instead of by module.

The battery is deliberately mechanical: each probe answers a question that can
be decided from the source alone, so a PASS is evidence rather than opinion, and
every FAIL is actionable.  Probes that need judgement are listed as the manual
half of the checklist and are never auto-ticked.

Usage:
    python tools/mesh_function_preflight.py                # write the TODO
    python tools/mesh_function_preflight.py --stdout        # print, do not write
    python tools/mesh_function_preflight.py --summary       # counts only
    python tools/mesh_function_preflight.py --module spine  # one module
    python tools/mesh_function_preflight.py --verdict       # PF16 decisions

`--verdict` writes NEURAL_MESH_WIRE_OR_CUT.json: every function nothing in the
repo reaches, with a declared disposition. See `wire_or_cut`.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src"
MESH_DIR = SRC / "CORE" / "WORMS" / "expansion"
DEFAULT_OUT = REPO / "NEURAL_MESH_FUNCTION_TODO.md"

# ---------------------------------------------------------------------------
# Scope: what counts as "the neural mesh architecture"
# ---------------------------------------------------------------------------
#
# The fabric proper (transport, membership, consensus, immunity), the neural
# primitives it is built from, the learning/plasticity loop, and the operational
# subsystems that keep it alive.  Anything outside this list is a different
# architecture and is out of scope for this TODO.

FABRIC = [
    "mesh", "envmesh", "fabric_state", "servemesh", "communication",
    "spine", "consensus", "federated", "immune", "synapse", "engram",
]

NEURAL_PRIMITIVES = [
    "nerve", "axon", "dendrite", "glia", "thalamus", "loom", "chorus",
    "arena", "allocation", "cppn", "tensorgene", "xenomorph",
]

LEARNING = [
    "learning", "learning_ab", "learning_features", "learning_grpo",
    "learning_pipeline", "learning_replay", "learning_rl", "learning_versioner",
    "plasticity", "consolidation", "dreaming", "meta_cognition", "metabolic",
    "evolution", "morph", "oracle",
]

OPERATIONAL = [
    "driver", "scheduling", "container", "config", "security",
    "error_recovery", "evidence", "migration", "race_detector", "code_audit",
    "profiling", "backup", "chaos", "berks", "db_monitor", "threatmon",
    "visualization", "proteus_hooks", "exmachina", "exmachina_operators",
    "session_state", "telemetry",
]

SCOPE_GROUPS: list[tuple[str, list[str]]] = [
    ("Fabric", FABRIC),
    ("Neural primitives", NEURAL_PRIMITIVES),
    ("Learning and plasticity", LEARNING),
    ("Operational", OPERATIONAL),
]

# Modules that live outside the expansion package but are part of the mesh.
EXTRA_MODULES = [
    SRC / "CORE" / "spine_registry.py",
    SRC / "CORE" / "NeuralPipeline.py",
]

DEFAULT_EXCLUDES = ("__pycache__", ".venv", "venv", "generated")

# ---------------------------------------------------------------------------
# Pre-flight battery
# ---------------------------------------------------------------------------
#
# The battery is intentionally cheap and deterministic.  It is a *pre*-flight:
# it is meant to be run before anyone invests time reading a function, so that
# the reading time goes to the functions the probes cannot already clear.

EMOJI_RANGES = (
    (0x1F300, 0x1FAFF), (0x1F000, 0x1F2FF), (0x2600, 0x27BF),
    (0x2B00, 0x2BFF), (0xFE00, 0xFE0F), (0x1F1E6, 0x1F1FF),
)

# Built from parts so this file does not itself contain a hardcoded drive path.
DRIVE_RE = re.compile(r"\b[A-Za-z]:" + re.escape(chr(92)) )

BUILTIN_NAMES = frozenset(dir(builtins))

PROBE_HELP: list[tuple[str, str]] = [
    ("PF01", "parses as valid Python and the span is inside the file"),
    ("PF02", "has a docstring"),
    ("PF03", "has a return annotation"),
    ("PF04", "every parameter is annotated"),
    ("PF05", "no bare `except:`"),
    ("PF06", "no mutable default argument"),
    ("PF07", "no `os.system` / `shell=True` subprocess"),
    ("PF08", "no emoji in the source span"),
    ("PF09", "no hardcoded drive path in the source span"),
    ("PF10", "no backslash inside an f-string expression"),
    ("PF11", "does not shadow a builtin or import a wildcard"),
    ("PF12", "not an unimplemented stub"),
    ("PF13", "no constant-true `while` with no break, return or raise"),
    ("PF14", "catches a specific exception, not `Exception` alone"),
    ("PF15", "no bare `pass` in an except body"),
    ("PF16", "is referenced somewhere in the repo (reachability)"),
    ("PF17", "is referenced by a test (test coverage signal)"),
    ("PF18", "writes no module-level global (concurrency signal)"),
    ("PF19", "opens files with an explicit encoding"),
    ("PF20", "recursion is depth-guarded"),
    ("PF21", "progress-dependent loop body always advances the condition"),
]

MANUAL_CHECKS: list[tuple[str, str]] = [
    ("M1", "signature matches what callers actually pass"),
    ("M2", "return contract holds on every path (including early returns)"),
    ("M3", "error paths leave shared state consistent"),
    ("M4", "safe under free-threaded concurrent calls"),
    ("M5", "no silent data loss on partial failure"),
    ("M6", "the docstring is true"),
]

# Methods the interpreter invokes implicitly.  PF16 asks "does the bare name
# appear as a Name or Attribute anywhere?", which no correct explicit reference
# can satisfy for these: `__repr__` is reached by `repr()` and the debugger,
# `__bool__` by `bool()`, `__getattr__` by any attribute miss.  Flagging them is
# a *measured* false positive rather than dead code.  The evidence that forced
# this calibration: `nerve._LazyTorch.__bool__` was reported unreachable while
# `bool(_torch)` is called at four sites in the same file, and `_torch.xpu` /
# `_torch.Generator` / `_torch.nn` all dispatch through `_LazyTorch.__getattr__`.
#
# Calibrated here rather than silenced by adding a caller, because inventing a
# call site to satisfy a probe is exactly the anti-pattern the wire-or-cut table
# exists to prevent.  PF17 (test reference) shares this blind spot but is left
# alone deliberately: it is a coverage *signal*, not a disposition, and changing
# two probes at once would make the census diff unattributable.
PROTOCOL_METHODS = frozenset({
    "__repr__", "__str__", "__format__", "__bytes__",
    "__bool__", "__len__", "__length_hint__", "__index__",
    "__int__", "__float__", "__complex__", "__hash__",
    "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
    "__iter__", "__next__", "__reversed__", "__contains__",
    "__getattr__", "__getattribute__", "__setattr__", "__delattr__",
    "__enter__", "__exit__", "__await__", "__aiter__", "__anext__",
    "__call__", "__init_subclass__", "__class_getitem__",
    "__getnewargs__", "__reduce__", "__reduce_ex__",
})


@dataclass
class Func:
    """One function found in the mesh tree."""

    module: str
    qualname: str
    lineno: int
    end_lineno: int
    complexity: int
    params: int
    is_async: bool
    source: str
    seg: str
    node: ast.AST = field(repr=False, default=None)
    failures: list[str] = field(default_factory=list)
    prior: str = "P3"

    @property
    def label(self) -> str:
        return f"{self.module}:{self.qualname}"

    @property
    def lines(self) -> str:
        return f"L{self.lineno}-{self.end_lineno}"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for _, names in SCOPE_GROUPS:
        for name in names:
            p = MESH_DIR / f"{name}.py"
            if p.exists():
                files.append(p)
    for p in EXTRA_MODULES:
        if p.exists():
            files.append(p)
    return sorted(set(files))


def _complexity(node: ast.AST) -> int:
    branches = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try,
                ast.With, ast.AsyncWith, ast.BoolOp, ast.ExceptHandler,
                ast.IfExp, ast.Match)
    return sum(1 for n in ast.walk(node) if isinstance(n, branches))


def _collect(tree: ast.AST, module: str, source: str) -> list[Func]:
    out: list[Func] = []

    def walk(body: list[ast.stmt], prefix: str) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                walk(node.body, f"{prefix}{node.name}.")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                seg = ast.get_source_segment(source, node) or ""
                out.append(Func(
                    module=module,
                    qualname=f"{prefix}{node.name}",
                    lineno=node.lineno,
                    end_lineno=getattr(node, "end_lineno", node.lineno),
                    complexity=_complexity(node),
                    params=len(node.args.args) + len(node.args.kwonlyargs),
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    source=source,
                    seg=seg,
                    node=node,
                ))
                walk(node.body, f"{prefix}{node.name}.")

    walk(tree.body, "")
    return out


def _reference_index() -> tuple[set[str], set[str], set[str]]:
    """(used anywhere, used by tests, used OUTSIDE tests).

    The third set is the one PF16 must use, and the docstring has promised it
    since the probe was written without ever returning it -- so PF16 was reading
    a set that included ``tests/``. That made a test-only caller look like
    reachability, which contradicts the wire-or-cut table's own definition of
    `wired`: "a production caller exists (so PF16 must NOT fire)". A function
    called only from a test would have satisfied `wired` with no production
    caller at all.

    Measured, on this probe: adding a regression test that calls
    `MoEDispatcherWorm.dispatch_cascade` silently removed it from the PF16
    findings without any production caller existing. PF17 already covers test
    reference, so the two probes now measure different things instead of
    overlapping on the weaker one.
    """
    used: set[str] = set()
    test_used: set[str] = set()
    prod_used: set[str] = set()
    for base in ("src", "tests", "scripts", "tools"):
        root = REPO / base
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(x in path.parts for x in DEFAULT_EXCLUDES):
                continue
            try:
                tree = ast.parse(_read(path))
            except SyntaxError:
                continue
            names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
            allnames = names | attrs
            used |= allnames
            if base == "tests":
                test_used |= allnames
            else:
                prod_used |= allnames
    return used, test_used, prod_used


def _plain_true(test: ast.expr) -> bool:
    if isinstance(test, ast.Constant):
        return bool(test.value)
    if isinstance(test, ast.Name) and test.id in {"True", "true"}:
        return True
    return False


def _while_exits(loop: ast.While) -> list[ast.AST]:
    return [x for x in ast.walk(loop)
            if isinstance(x, (ast.Break, ast.Return, ast.Raise))]


def _has_unbounded_while(node: ast.AST) -> bool:
    """True only for the classic spin: `while True` with no way out.

    A `while <condition>` is bounded by that condition, so flagging every
    `while` produced nothing but noise -- `while i < n`, `while not stop.is_set()`
    and `while not stop.wait(1)` are all finite and all correct. Only a constant
    truthy test with no break, return or raise can actually spin.
    """
    for n in ast.walk(node):
        if isinstance(n, ast.While) and _plain_true(n.test) \
                and not _while_exits(n):
            return True
    return False


def _has_progress_loop(node: ast.AST) -> bool:
    """A loop that only ends when its body makes the condition false.

    `while len(buf) < target:` is correct and common, but it hangs if the body
    has any path that fails to extend the buffer. That is a real risk the pure
    bounded-loop rule cannot see, so it gets its own probe and stays advisory.
    """
    for n in ast.walk(node):
        if not isinstance(n, ast.While) or _plain_true(n.test):
            continue
        if _while_exits(n):
            continue
        for sub in ast.walk(n.test):
            # `ast.dump` prints `Call(func=Name(id='len'))`, so match the node,
            # not the rendered text.
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                    and sub.func.id == "len":
                return True
            if isinstance(sub, ast.Name) and sub.id in {
                    "count", "cursor", "offset", "attempts", "retries",
                    "remaining", "tries"}:
                return True
    return False


def _run_probes(fn: Func, used: set[str], test_used: set[str]) -> list[str]:
    fail: list[str] = []
    node = fn.node
    assert node is not None

    if not fn.seg:
        fail.append("PF01")

    if not ast.get_docstring(node):
        fail.append("PF02")

    if getattr(node, "returns", None) is None:
        fail.append("PF03")

    args = list(node.args.args) + list(node.args.kwonlyargs)
    if not all(a.annotation is not None for a in args):
        fail.append("PF04")

    for n in ast.walk(node):
        if isinstance(n, ast.ExceptHandler) and n.type is None:
            fail.append("PF05")
            break

    defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d]
    for d in defaults:
        if isinstance(d, (ast.List, ast.Dict, ast.Set)):
            fail.append("PF06")
            break

    if "os.system(" in fn.seg or "shell=True" in fn.seg:
        fail.append("PF07")

    for ch in fn.seg:
        cp = ord(ch)
        if any(a <= cp <= b for a, b in EMOJI_RANGES):
            fail.append("PF08")
            break

    if DRIVE_RE.search(fn.seg):
        fail.append("PF09")

    # f-string with a backslash inside the replacement field
    for n in ast.walk(node):
        if isinstance(n, ast.JoinedStr):
            for v in n.values:
                if isinstance(v, ast.FormattedValue):
                    piece = ast.get_source_segment(fn.source, v) or ""
                    if chr(92) in piece:
                        fail.append("PF10")
                        break
            else:
                continue
            break

    name = getattr(node, "name", "")
    if name in BUILTIN_NAMES:
        fail.append("PF11")
    for n in ast.walk(node):
        if isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names):
            fail.append("PF11")
            break

    body = [b for b in node.body
            if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]
    if not body:
        fail.append("PF12")
    elif len(body) == 1:
        only = body[0]
        if isinstance(only, ast.Pass):
            fail.append("PF12")
        elif isinstance(only, ast.Raise):
            exc = only.exc
            if isinstance(exc, ast.Call) and getattr(exc.func, "id", "") == "NotImplementedError":
                fail.append("PF12")
        elif isinstance(only, ast.Expr) and isinstance(only.value, ast.Constant) \
                and only.value.value is Ellipsis:
            fail.append("PF12")

    if _has_unbounded_while(node):
        fail.append("PF13")
    elif _has_progress_loop(node):
        fail.append("PF21")

    handlers = [n for n in ast.walk(node) if isinstance(n, ast.ExceptHandler)]
    for h in handlers:
        if isinstance(h.type, ast.Name) and h.type.id == "Exception":
            fail.append("PF14")
            break

    for h in handlers:
        stmts = [s for s in h.body
                 if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        if stmts and all(isinstance(s, ast.Pass) for s in stmts):
            fail.append("PF15")
            break
        if not stmts:
            fail.append("PF15")
            break

    if name and name not in PROTOCOL_METHODS and name not in used:
        fail.append("PF16")
    if name and name not in test_used:
        fail.append("PF17")

    if any(isinstance(n, (ast.Global, ast.Nonlocal)) for n in ast.walk(node)):
        fail.append("PF18")

    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id == "open":
            if not any(k.arg == "encoding" for k in n.keywords):
                fail.append("PF19")
                break


    # Recursion without a depth guard is the other way a function stops
    # returning. A self-call is only safe when it carries the depth down.
    fname = getattr(node, "name", "")
    if fname:
        self_calls = [n for n in ast.walk(node)
                      if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Name)
                      and n.func.id == fname]
        guards = {"depth", "_depth", "level", "limit", "max_depth",
                  "seen", "visited", "memo"}
        if self_calls:
            # A guard can be passed positionally and derived (`depth - 1`), so
            # read the call's own source rather than inspecting one AST node.
            carried = False
            for call in self_calls:
                piece = ast.get_source_segment(fn.source, call) or ""
                if any(g in piece for g in guards):
                    carried = True
                    break
            if not carried:
                fail.append("PF20")

    # de-duplicate, keep battery order
    seen: set[str] = set()
    ordered: list[str] = []
    for f in fail:
        if f not in seen:
            seen.add(f)
            ordered.append(f)
    return ordered


def _prioritise(fn: Func) -> str:
    hard = {"PF05", "PF07", "PF12", "PF13", "PF15", "PF18", "PF20"}
    if hard & set(fn.failures):
        return "P0"
    if {"PF09", "PF10", "PF14", "PF19", "PF16"} & set(fn.failures):
        return "P1"
    if fn.complexity >= 12 and fn.failures:
        return "P1"
    if fn.failures:
        return "P2"
    return "CLEAN"


def build(module_filter: str | None = None) -> tuple[list[Func], Counter]:
    files = _iter_files()
    _used, test_used, prod_used = _reference_index()
    funcs: list[Func] = []
    for path in files:
        module = path.stem
        if module_filter and module_filter.lower() not in module.lower():
            continue
        source = _read(path)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        found = _collect(tree, module, source)
        for fn in found:
            # PF16 = production reachability; PF17 = test reachability. Passing
            # `prod_used` here is what makes `wired` mean "a production caller
            # exists" rather than "something somewhere mentions it".
            fn.failures = _run_probes(fn, prod_used, test_used)
            fn.prior = _prioritise(fn)
            funcs.append(fn)
    counts = Counter()
    for fn in funcs:
        for f in fn.failures:
            counts[f] += 1
        counts[fn.prior] += 1
    return funcs, counts


def render(funcs: list[Func], counts: Counter, module_filter: str | None) -> str:
    total = len(funcs)
    clean = counts.get("CLEAN", 0)
    p0 = counts.get("P0", 0)
    p1 = counts.get("P1", 0)
    p2 = counts.get("P2", 0)

    out: list[str] = []
    out.append("# Neural Mesh Architecture - Per-Function Pre-Flight TODO")
    out.append("")
    out.append("Generated by `tools/mesh_function_preflight.py`. Re-run it after")
    out.append("changing a mesh function; the checklist is derived from the source,")
    out.append("so it cannot drift from the code it describes.")
    out.append("")
    out.append("Companion analysis - the reasoning behind every change made from this")
    out.append("list, plus the insights inferred from the census - lives in")
    out.append("`NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md`.")
    out.append("")
    if module_filter:
        out.append(f"Filter: modules matching `{module_filter}`")
        out.append("")
    out.append("## Scope")
    out.append("")
    out.append(f"- {total} functions across the fabric, neural primitives, learning")
    out.append("  and plasticity, and operational subsystems")
    out.append(f"- {clean} pass every automated probe; {total - clean} have at least one failure")
    out.append(f"- P0 {p0} / P1 {p1} / P2 {p2}")
    out.append("")
    out.append("## How to work this list")
    out.append("")
    out.append("For each function, in this order:")
    out.append("")
    out.append("1. Run the automated battery (below). A PASS is evidence, not a verdict.")
    out.append("2. Walk the manual checklist. This is the part that needs reading the")
    out.append("   callers, not just the body.")
    out.append("3. Only then tick the boxes.")
    out.append("4. Any probe you clear by *changing* the function gets recorded in")
    out.append("   `NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md`, with the")
    out.append("   reasoning, so the fix is reviewable later.")
    out.append("")
    out.append("## Automated pre-flight battery")
    out.append("")
    for pid, desc in PROBE_HELP:
        out.append(f"- **{pid}** {desc}")
    out.append("")
    out.append("## Manual pre-flight checklist")
    out.append("")
    for mid, desc in MANUAL_CHECKS:
        out.append(f"- **{mid}** {desc}")
    out.append("")

    out.append("## Failure census")
    out.append("")
    out.append("| probe | functions failing |")
    out.append("|---|---|")
    for pid, _ in PROBE_HELP:
        out.append(f"| {pid} | {counts.get(pid, 0)} |")
    out.append("")

    # Highest-value work first: P0, then P1 by complexity.
    out.append("## Triage - P0")
    out.append("")
    out.append("Probes in the P0 set (PF05, PF07, PF12, PF13, PF15, PF18, PF20) are the")
    out.append("ones that can lose data, hide an error, or spin forever. Clear these")
    out.append("first.")
    out.append("")
    p0_funcs = sorted((f for f in funcs if f.prior == "P0"),
                      key=lambda f: -f.complexity)
    if not p0_funcs:
        out.append("_None._")
        out.append("")
    for fn in p0_funcs:
        out.append(f"- [ ] `{fn.label}` {fn.lines} c={fn.complexity} "
                   f"fail={','.join(fn.failures)}")
        out.append(f"  - [ ] {'M1-M6 manual pass'}")
    out.append("")

    out.append("## Triage - P1")
    out.append("")
    p1_funcs = sorted((f for f in funcs if f.prior == "P1"),
                      key=lambda f: -f.complexity)
    for fn in p1_funcs:
        out.append(f"- [ ] `{fn.label}` {fn.lines} c={fn.complexity} "
                   f"fail={','.join(fn.failures)}")
    out.append("")

    out.append("## Full inventory")
    out.append("")
    out.append("Every function in scope, grouped by concern and module. Each row is")
    out.append("`- [ ]` battery pass, `- [ ]` manual pass.")
    out.append("")

    by_module: dict[str, list[Func]] = defaultdict(list)
    for fn in funcs:
        by_module[fn.module].append(fn)

    for group, names in SCOPE_GROUPS:
        out.append(f"### {group}")
        out.append("")
        for name in names:
            mods = by_module.get(name)
            if not mods:
                continue
            out.append(f"#### `{name}.py` - {len(mods)} functions")
            out.append("")
            for fn in sorted(mods, key=lambda f: f.lineno):
                flags = ",".join(fn.failures) if fn.failures else "OK"
                out.append(f"- [ ] `{fn.qualname}` {fn.lines} "
                           f"c={fn.complexity} p={fn.params} "
                           f"{'async ' if fn.is_async else ''}auto={flags}")
                out.append(f"  - [ ] manual M1-M6")
            out.append("")

    extras = [p.stem for p in EXTRA_MODULES if p.exists()]
    if extras:
        out.append("### Outside the expansion package")
        out.append("")
        for name in extras:
            mods = by_module.get(name)
            if not mods:
                continue
            out.append(f"#### `{name}.py` - {len(mods)} functions")
            out.append("")
            for fn in sorted(mods, key=lambda f: f.lineno):
                flags = ",".join(fn.failures) if fn.failures else "OK"
                out.append(f"- [ ] `{fn.qualname}` {fn.lines} "
                           f"c={fn.complexity} p={fn.params} "
                           f"{'async ' if fn.is_async else ''}auto={flags}")
                out.append(f"  - [ ] manual M1-M6")
            out.append("")

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Wire-or-cut verdict (PF16), as data
# ---------------------------------------------------------------------------
#
# PF16 is the probe that answers "does anything reach this function?" and it is
# the one whose findings cannot be fixed by editing the function: a function
# nothing calls cannot regress visibly, so it can neither be trusted nor repaired
# by observation. There are only two honest resolutions -- wire it to a caller,
# or retire it -- and that is a DECISION, not a patch.
#
# `evolution.py` already encodes exactly this for the v2 engines as
# `SERVED_ENGINES` / `UNSERVED_ENGINES`, with a test asserting no UNSERVED name
# is referenced. This generalises that pattern to every PF16 finding in the mesh
# so the decision is reviewable data instead of a silent 114-item blind spot.
#
# `pending` is a first-class status on purpose: an unreviewed function is not the
# same as a decided one, and collapsing the two is how a backlog becomes a lie.

VERDICT_OUT = REPO / "NEURAL_MESH_WIRE_OR_CUT.json"

#: Declared dispositions.
#:
#: * `wired`      -- a STATIC production caller exists (so PF16 must NOT fire)
#: * `retired`    -- it should be deleted (`reason` required)
#: * `dispatched` -- its only production reference is a STRING (name-based
#:                   lookup: `getattr`, a registry key, a dispatch table), so an
#:                   explicit reference cannot exist and PF16 cannot decide it.
#:                   Verified against `string_references()`, not asserted.
#: * `pending`    -- the decision has not been made
#:
#: `dispatched` exists because a triage measured it: of 164 findings, 62 are
#: named by a string literal in production code while PF16 (which reads
#: `ast.Name` / `ast.Attribute`) can see none of them. Before this status the
#: table could only say `pending` about a fact it had already measured, or lie --
#: `wired` fails its own contract test while PF16 still fires. This is the same
#: distinction as `PROTOCOL_METHODS` ("no explicit reference can ever satisfy
#: it"), kept as data rather than folded into the probe's filter.
VERDICT_STATUSES = ("wired", "retired", "dispatched", "pending")

#: Evidence classes for the `pending` backlog -- see `triage()`.
TRIAGE_CLASSES = ("test_reached_only", "no_reference_anywhere")

#: Where a name-based reference can come from: production only, because a string
#: in a test is test reachability and PF17 already measures that.
STRING_SCOPES = ("src", "scripts", "tools")

_STRING_REFS: dict[str, list[str]] | None = None

#: A literal that could name something: `deliver`, `Worm.deliver`. A sentence
#: (`"we deliver the mail"`) is not a dispatch site and is not counted.
_IDENTIFIER_LIKE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """`id()` of every docstring constant, so prose is not read as a reference."""
    out: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None) or []
        if body and isinstance(body[0], ast.Expr) \
                and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            out.add(id(body[0].value))
    return out


def string_references() -> dict[str, list[str]]:
    """name -> `["src/.../file.py:123"]` for every production string literal.

    Cached, because the wire-or-cut tests ask about one name at a time and the
    walk covers several thousand files.

    Only IDENTIFIER-LIKE literals count -- `"deliver"`, `"Worm.deliver"`, and
    docstrings are skipped -- because a sentence that happens to contain the
    word is not a dispatch site, and a docstring that names a function is a
    description of code, not a reference to it from code. Being conservative is
    the safe direction here: a miss leaves the entry `pending` (the truth being
    "not measured") whereas a false hit would claim reachability that does not
    exist.
    """
    global _STRING_REFS
    if _STRING_REFS is not None:
        return _STRING_REFS
    found: dict[str, list[str]] = defaultdict(list)
    for base in STRING_SCOPES:
        root = REPO / base
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(x in path.parts for x in DEFAULT_EXCLUDES):
                continue
            try:
                tree = ast.parse(_read(path))
            except SyntaxError:
                continue
            rel = path.relative_to(REPO).as_posix()
            docstrings = _docstring_nodes(tree)
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Constant)
                        and isinstance(node.value, str)):
                    continue
                if id(node) in docstrings:
                    continue
                literal = node.value
                if not _IDENTIFIER_LIKE.match(literal):
                    continue
                for token in {literal} | set(re.split(r"\.", literal)):
                    if token.isidentifier():
                        where = "%s:%d" % (rel, node.lineno)
                        if where not in found[token]:
                            found[token].append(where)
    _STRING_REFS = {k: sorted(v) for k, v in found.items()}
    return _STRING_REFS


def wire_or_cut(funcs: list[Func], declared: dict | None = None) -> dict:
    """The PF16 findings as a declaration table, preserving prior decisions.

    Passing the existing table in means a re-run never discards a decision
    someone already made and wrote down -- the same reason the TODO is
    regenerated rather than rewritten.
    """
    prior = dict(declared or {})
    entries: dict[str, dict] = {}
    for fn in funcs:
        if "PF16" not in fn.failures:
            continue
        key = fn.label
        old = prior.get(key) or {}
        entries[key] = {
            "module": fn.module,
            "qualname": fn.qualname,
            "line": fn.lineno,
            "status": str(old.get("status") or "pending"),
            "reason": str(old.get("reason") or ""),
        }
    tally = Counter(e["status"] for e in entries.values())
    return {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "probe": "PF16",
        "rule": ("Every unreferenced mesh function must be declared wired, "
                 "retired or pending. tests/test_mesh_wire_or_cut.py asserts "
                 "that no finding is undeclared, that no declaration is "
                 "stale, and that a `wired` declaration is actually wired."),
        "counts": {s: tally.get(s, 0) for s in VERDICT_STATUSES},
        "total": len(entries),
        "declared": dict(sorted(entries.items())),
    }


def propose(table: dict) -> dict:
    """Fill in the statuses the EVIDENCE decides, and leave the rest pending.

    Deliberately not a classifier that guesses: it sets exactly one status
    (`dispatched`, when the only production trace of a name is a string) and
    writes the measurement into `reason` for everything else, so the remaining
    backlog states what is missing instead of being a bare count. An existing
    `reason` is never overwritten -- a human's note outranks a probe's.

    Returns the table unchanged in shape, with `counts` recomputed.
    """
    refs = string_references()
    entries = table.get("declared") or {}
    for entry in entries.values():
        qualname = str(entry.get("qualname") or "")
        name = qualname.rsplit(".", 1)[-1]
        hits = refs.get(name) or refs.get(qualname) or []
        status = str(entry.get("status") or "pending")
        reason = str(entry.get("reason") or "")
        if hits and status == "pending":
            entry["status"] = "dispatched"
            if not reason:
                entry["reason"] = (
                    "only production reference is a string literal (%s), so a "
                    "static caller cannot exist; wire it explicitly or delete "
                    "it" % ", ".join(hits[:3]))
        # Evidence is re-derived for EVERY dispatched entry, not only the one
        # being flipped. `--propose` is meant to be re-runnable, and the first
        # version recorded the locations only on the transition: a second run
        # left every already-dispatched row with a reason and no evidence, which
        # `tests/test_mesh_wire_or_cut.py::
        # test_a_dispatched_declaration_states_where_and_why` correctly rejects.
        if hits and str(entry.get("status")) == "dispatched":
            entry["evidence"] = hits[:3]
        elif not hits and status == "pending" and not reason:
            entry["reason"] = (
                "no production reference of any kind -- not as a Name, an "
                "attribute, or a string; wire it or delete it (PF16)")
    tally = Counter(str(e.get("status")) for e in entries.values())
    table["counts"] = {s: tally.get(s, 0) for s in VERDICT_STATUSES}
    return table


# ---------------------------------------------------------------------------
# Triage of the `pending` backlog -- a class, not a disposition
# ---------------------------------------------------------------------------
# 102 findings have no production reference of any KIND: not a name, not an
# attribute, not a string literal. `status` cannot be set from that (a class is
# not a decision -- see VERDICT_STATUSES), but the NEXT ACTION can be, and the
# evidence for it is one cheap question: **does the test suite reach it?**
#
#  * `test_reached_only` -- a test calls it and production does not. The
#    decision is about intent: public API (wire a production caller) or
#    scaffolding (retire it). PF17 already measures test reachability, so this
#    is the same fact stated where the decision is made.
#  * `no_reference_anywhere` -- nothing in this repository reaches it at all.
#    That is the deletion queue, and it is a claim the probe can check.
#
# The label is stored in its own field (`triage`, `triage_evidence`) and never
# in `status`, so no review can mistake a measurement for a disposition.
TEST_SCOPES = ("tests",)

_test_refs: dict[str, list[str]] | None = None


def test_references() -> dict[str, list[str]]:
    """name -> `["tests/test_x.py:123"]` for every TEST-side mention.

    Counts whatever a test can use to reach a name: an `ast.Name`, an
    `ast.Attribute` (``profiler.profile_function()``), or an identifier-like
    string literal. Cached for the same reason as `string_references`.
    """
    global _test_refs
    if _test_refs is not None:
        return _test_refs

    found: dict[str, list[str]] = {}

    def note(name: str, where: str) -> None:
        if not name or name.startswith("__"):
            return
        bucket = found.setdefault(name, [])
        if len(bucket) < 8 and where not in bucket:
            bucket.append(where)

    for scope in TEST_SCOPES:
        root = REPO / scope
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
            except SyntaxError:
                continue
            docstrings = _docstring_nodes(tree)
            rel = path.relative_to(REPO).as_posix()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    note(node.id, "%s:%d" % (rel, node.lineno))
                elif isinstance(node, ast.Attribute):
                    note(node.attr, "%s:%d" % (rel, node.lineno))
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if id(node) in docstrings:
                        continue
                    text = node.value.strip()
                    if _IDENTIFIER_LIKE.match(text):
                        note(text.rsplit(".", 1)[-1], "%s:%d" % (rel, node.lineno))
    _test_refs = found
    return found


def triage(table: dict) -> dict:
    """Label the still-`pending` findings with the class that decides them.

    Never changes `status`: this is the ordering a reviewer needs, not a
    verdict, and collapsing the two is how a backlog becomes a lie.
    """
    refs = test_references()
    entries = table.get("declared") or {}
    tally: Counter = Counter()
    for entry in entries.values():
        if str(entry.get("status")) != "pending":
            continue
        qualname = str(entry.get("qualname") or "")
        hits = refs.get(qualname.rsplit(".", 1)[-1]) or refs.get(qualname) or []
        klass = "test_reached_only" if hits else "no_reference_anywhere"
        entry["triage"] = klass
        entry["triage_evidence"] = hits[:3]
        tally[klass] += 1
    table["triage_counts"] = {k: tally.get(k, 0) for k in TRIAGE_CLASSES}
    return table


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--module", default=None, help="filter to modules matching this")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    ap.add_argument("--summary", action="store_true", help="counts only")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--verdict", action="store_true",
                    help="write the PF16 wire-or-cut declaration table instead")
    ap.add_argument("--propose", action="store_true",
                    help="with --verdict: fill the statuses the evidence "
                         "decides (string-only references become `dispatched`) "
                         "and record the measurement for the rest")
    ap.add_argument("--triage", action="store_true",
                    help="with --verdict: label every still-`pending` finding with "
                         "the evidence class that decides its next action "
                         "(test-reached / no-reference-anywhere); status is NOT "
                         "changed, because a class is not a disposition")
    args = ap.parse_args()

    funcs, counts = build(args.module)
    if args.verdict:
        import json

        prior = {}
        if VERDICT_OUT.exists():
            try:
                prior = (json.loads(VERDICT_OUT.read_text(encoding="utf-8"))
                         or {}).get("declared") or {}
            except Exception:
                prior = {}
        table = wire_or_cut(funcs, prior)
        if args.propose:
            table = propose(table)
        if args.triage:
            table = triage(table)
        if args.stdout:
            sys.stdout.write(json.dumps(table, indent=1) + "\n")
            return 0
        VERDICT_OUT.write_text(json.dumps(table, indent=1), encoding="utf-8")
        print(f"wrote {VERDICT_OUT} ({table['total']} unreferenced: {table['counts']})")
        if args.triage:
            print(f"  pending triage: {table.get('triage_counts')}")
        return 0
    if args.summary:
        print(f"functions: {len(funcs)}")
        for pid, _ in PROBE_HELP:
            print(f"  {pid}: {counts.get(pid, 0)}")
        for pr in ("P0", "P1", "P2", "CLEAN"):
            print(f"  {pr}: {counts.get(pr, 0)}")
        return 0

    text = render(funcs, counts, args.module)
    if args.stdout:
        sys.stdout.write(text)
        return 0
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"wrote {args.out} ({len(text.splitlines())} lines, {len(funcs)} functions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
