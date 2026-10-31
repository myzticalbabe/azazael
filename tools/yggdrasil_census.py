#!/usr/bin/env python3
# coding: utf-8
"""YGGDRASIL census — the cleave ledger as a measurement, not a paragraph.

The 2026-10-30 analysis recorded 19 trees, 8 cleave-clean, 32 shim edges and 6
blocking cycles. Sixty days of file growth later the numbers were stale and
nothing noticed, because the measurement existed only as prose. This tool is
that measurement: run it, get the same answer, diff it against the last run.

Definitions, stated once so the numbers mean something:

* **tree** — a directory directly under ``src/`` holding at least one ``.py``.
  Loose modules at ``src/`` root are counted separately, never as trees.
* **module-level import** — an ``import``/``from`` statement in ``Module.body``
  (col_offset 0, i.e. executed at import time).
* **any-import edge** — any ``import``/``from`` anywhere in the file, including
  function bodies. This is the honest cleave metric: a function-local import
  still breaks when the tree is lifted out.
* **cycle** — a direct mutual import pair (``A -> B`` and ``B -> A``) at module
  level. Longer cycles are not reported (see ``limits`` in the JSON).
* **clean** — a tree that nothing outside it imports.

Usage::

    python tools/yggdrasil_census.py            # human report
    python tools/yggdrasil_census.py --json     # machine-readable ledger
    python tools/yggdrasil_census.py --json --out census.json
    python tools/yggdrasil_census.py --selftest # negative controls on the scanner

Exit codes: 0 = scanned, 2 = root missing, 3 = self-test failed.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

SCHEMA = 2

#: The shard grammar the SHARD_01 artefact states: limb -> 24 shards -> sapling.
SHARDS_PER_LIMB = 24

#: Source languages counted per tree. The cleave grammar was written for Python
#: only, so a tree that is a Rust extension, a Go service or a TS front-end was
#: invisible to every number in the ledger -- it had 0 "modules" and therefore
#: 0 saplings, which reads as "no code" rather than "code this instrument cannot
#: see". Extension -> language; anything unmapped is reported as "other".
LANGUAGES: Dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".rs": "rust", ".go": "go", ".zig": "zig",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp",
    ".hpp": "cpp", ".cuh": "cuda", ".cu": "cuda",
    ".java": "java", ".kt": "kotlin", ".cs": "dotnet", ".jl": "julia",
    ".m": "objc", ".swift": "swift", ".rb": "ruby", ".sh": "shell",
    # The driver layer is not .sh here: 58 .bat + 18 .ps1 were uncounted, and
    # those files are exactly where python is invoked from outside python.
    ".bat": "batch", ".cmd": "batch", ".ps1": "powershell",
    ".html": "html", ".htm": "html",
}

#: Directories that hold generated or vendored output, not authored shards.
SKIP_DIRS = {"__pycache__", "node_modules", "target", ".venv", "venv", "dist",
              "build", ".git", "graphify-out", ".mypy_cache", ".pytest_cache"}

#: A tree is a STUB when nothing imports it, it holds at most this many Python
#: modules, and none of them define a function or class. Measured 2026-10-31:
#: `SHORTCUTS` (1 module, 1 line) and `RENDERING` (3 modules of prompt dicts)
#: both counted as cleave-ready trees purely because nothing imported them, which
#: is why the analysis' own caveat about stubs needs to be a rule and not a note.
STUB_MAX_PY = 5

#: Seams that cross the language boundary. A Python package with a maturin
#: pyproject, a Cargo.toml beside it, or ctypes/cffi use is coupled to native code
#: that the import graph cannot see, so its "clean cut" is not clean.
SEAM_MARKERS = ("maturin", "ctypes", "cffi", "pyo3", "wasmtime", "grpc")

#: Non-python reference syntax followed for cross-language edges. Each pattern
#: names a real join the AST graph cannot see.
_JS_IMPORT_RE = re.compile(
    r"""(?:\bfrom\s*|\brequire\(\s*|\bimport\(\s*)['"]([^'"\n]+)['"]""")
_HTML_SRC_RE = re.compile(r"""<script[^>]+src\s*=\s*['"]([^'"\n]+)['"]""", re.I)
_PY_CALL_RE = re.compile(r"""\bpython[0-9.]*(?:\.exe)?\s+['"]?([^'"\s|>;&]+\.py)""", re.I)

#: Hubs that make up the shared "mycelium". Token matched case-folded.
HUBS = ("audit", "inference", "paths", "pams", "worm_registry", "memorybus")

#: CORE is the trunk by measurement, not a candidate sapling.
TRUNK = "CORE"


# --------------------------------------------------------------------------
# scanning
# --------------------------------------------------------------------------

def _imported_roots(node: ast.AST) -> List[str]:
    """Absolute module roots named by one import statement.

    ``import a.b, c`` -> ["a", "c"]; ``from a.b import x`` -> ["a"].
    Relative imports (``from . import x``) name no root: skip them.
    """
    if isinstance(node, ast.Import):
        return [a.name.split(".")[0] for a in node.names if a.name]
    if isinstance(node, ast.ImportFrom):
        if getattr(node, "level", 0):
            return []
        return [(node.module or "").split(".")[0]]
    return []


def _walk_imports(tree: ast.AST, module_level_only: bool) -> Iterable[str]:
    if module_level_only:
        for stmt in tree.body:
            yield from _imported_roots(stmt)
    else:
        for node in ast.walk(tree):
            yield from _imported_roots(node)


# --------------------------------------------------------------------------
# non-python graphs: analyse the other languages, do not just count them
# --------------------------------------------------------------------------

#: Extensions a JS/TS relative import can resolve to, plus the directory-index
#: forms node and bundlers accept (`./panel` -> `./panel/index.ts`).
_JS_SUFFIXES = ("", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".json")
_JS_INDEX = ("index.js", "index.mjs", "index.ts", "index.tsx", "index.jsx")

#: `python -m pkg.mod` and the `py` launcher: the two forms a batch driver uses
#: to reach python without naming a .py file.
_PY_M_RE = re.compile(r"\bpython[0-9.]*(?:\.exe)?\s+-m\s+([\w.]+)")
_PY_LAUNCHER_RE = re.compile(r"(?:^|[&|(\s])py(?:\.exe)?(?:\s+-[0-9.]+)?\s+['\"]?([^\"'\s|>;&]+\.py)",
                            re.I | re.M)

#: Batch/PowerShell prefixes that name the script's own directory. `%~dp0` is the
#: commonest way a .bat reaches a sibling .py, and stripping it is what turns
#: "target-not-found" into a real edge when the sibling is under src.
_SHELL_PREFIX_RE = re.compile(r"^(?:%~dp0|%CD%|%cd%|\$PSScriptRoot[\\/]|\.\\)", re.I)


def _resolve_ref(src: Path, base: Path, ref: str,
                 suffixes: Tuple[str, ...] = _JS_SUFFIXES,
                 index_names: Tuple[str, ...] = _JS_INDEX) -> Optional[Path]:
    """Resolve one reference string to a real file under ``src``, or None.

    Order matters and is the one every toolchain uses: the literal path first,
    then the extension candidates, then the directory index. A resolver that
    guesses (basename matching anywhere in the tree) manufactures edges, so an
    unresolved reference stays unresolved and is counted as such.
    """
    ref = ref.strip().strip("'\"").replace("\\", "/")
    if not ref or ref.startswith(("http://", "https://", "data:", "#")):
        return None
    rp = Path(ref)
    roots: List[Path] = [rp] if rp.is_absolute() else [base / ref, src / ref]
    # The literal path is ALWAYS tried first. Passing `suffixes=(".py",)` for a
    # shell call used to test only `f.py.py`, so `python ../FFF/f.py` resolved to
    # nothing and was reported as outside-src -- a resolver bug wearing the
    # costume of a finding.
    candidates = ("",) + tuple(s for s in suffixes if s)
    for cand in roots:
        for suffix in candidates:
            path = Path(str(cand) + suffix)
            if path.suffix and not path.is_file():
                continue
            if not path.is_file():
                continue
            try:
                path.resolve().relative_to(src.resolve())
            except (OSError, ValueError):
                continue
            return path
        for index_name in index_names:
            path = cand / index_name
            if path.is_file():
                try:
                    path.resolve().relative_to(src.resolve())
                except (OSError, ValueError):
                    continue
                return path
    return None


#: Paths a resolver reached that are not under src. Counted, not swallowed: a
#: rising number means the graph is being asked about a tree it does not own.
_OUTSIDE_SRC: Counter[str] = Counter()


def _tree_of(src: Path, path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        rel = path.resolve().relative_to(src.resolve())
    except (OSError, ValueError):
        _OUTSIDE_SRC[str(path)] += 1
        return None
    return rel.parts[0] if len(rel.parts) > 1 else None


def _rel_posix(src: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(src.resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)


def _read_capped(path: Path, cap: int = 400_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:cap]
    except OSError as exc:
        print("[census] unreadable %s: %s" % (path, exc), file=sys.stderr)
        return ""


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _graph_cycles(edges: Iterable[Tuple[str, str]]) -> List[List[str]]:
    """Direct mutual pairs. Same definition as the python cycle rule, so the two
    graphs are comparable rather than merely both non-empty."""
    pairs = set(edges)
    out = {tuple(sorted(p)) for p in pairs if (p[1], p[0]) in pairs and p[0] != p[1]}
    return [list(p) for p in sorted(out)]


def build_js_graph(src: Path, js_files: List[Path]) -> Dict[str, Any]:
    """The js/ts module graph: file -> file, resolved through import/require.

    Counting 62 javascript files and calling it coverage is what this replaces.
    An external package (`require('puppeteer')`) is a dependency, not an edge, and
    is counted separately; only a specifier that resolves to a file under src is
    an edge.
    """
    edges: Counter[Tuple[str, str]] = Counter()
    tree_pairs: Counter[Tuple[str, str]] = Counter()
    tree_out: Counter[str] = Counter()
    tree_in: Counter[str] = Counter()
    external: Counter[str] = Counter()
    unresolved: Counter[str] = Counter()
    detail: List[Dict[str, Any]] = []

    for path in js_files:
        text = _read_capped(path)
        if not text:
            continue
        base = path.parent
        here_file = _rel_posix(src, path)
        here_tree = _tree_of(src, path)
        for m in _JS_IMPORT_RE.finditer(text):
            ref = m.group(1)
            if not ref.startswith("."):
                external[ref.split("/")[0]] += 1
                continue
            target = _resolve_ref(src, base, ref)
            if target is None:
                unresolved["target-not-found"] += 1
                if len(detail) < 30:
                    detail.append({"from": here_file, "line": _line_of(text, m.start()),
                                   "ref": ref, "result": "unresolved"})
                continue
            there_file = _rel_posix(src, target)
            edges[(here_file, there_file)] += 1
            there_tree = _tree_of(src, target)
            if here_tree:
                tree_out[here_tree] += 1
            if there_tree:
                tree_in[there_tree] += 1
            if here_tree and there_tree and here_tree != there_tree:
                tree_pairs[(here_tree, there_tree)] += 1
            if len(detail) < 30:
                detail.append({"from": here_file, "line": _line_of(text, m.start()),
                               "to": there_file, "ref": ref})

    return {
        "language": "javascript",
        "files": len(js_files),
        "statements": sum(edges.values()),
        "file_pairs": len(edges),
        "tree_pairs": [{"from": a, "to": b, "refs": n}
                       for (a, b), n in sorted(tree_pairs.items())],
        "cycles": _graph_cycles(edges),
        "per_tree": {t: {"out": tree_out[t], "in": tree_in[t]}
                     for t in sorted(set(tree_out) | set(tree_in))},
        "external_packages": dict(external.most_common(12)),
        "external_statements": sum(external.values()),
        "unresolved": dict(sorted(unresolved.items())),
        "detail": detail,
        "note": ("only a specifier resolving to a file under src is an edge; a bare "
                 "package name is a dependency and is counted separately"),
    }


def build_shell_graph(src: Path, script_files: List[Path]) -> Dict[str, Any]:
    """The shell/batch -> python call graph.

    This is the join the cleave actually trips on: 58 .bat and 15 .ps1 drive the
    python tree, and none of them is an import. Three forms are followed --
    `python <file>`, `python -m <module>` and the `py` launcher -- and each call
    is resolved to a real file or a module path, never guessed from a name.
    """
    calls: Counter[Tuple[str, str]] = Counter()
    tree_pairs: Counter[Tuple[str, str]] = Counter()
    tree_out: Counter[str] = Counter()
    tree_in: Counter[str] = Counter()
    forms: Counter[str] = Counter()
    unresolved: Counter[str] = Counter()
    missing: Counter[str] = Counter()
    detail: List[Dict[str, Any]] = []

    for path in script_files:
        text = _read_capped(path)
        if not text:
            continue
        here_file = _rel_posix(src, path)
        here_tree = _tree_of(src, path)
        base = path.parent
        found: List[Tuple[str, str, int]] = []
        for m in _PY_CALL_RE.finditer(text):
            found.append((m.group(1), "file", _line_of(text, m.start())))
        for m in _PY_LAUNCHER_RE.finditer(text):
            found.append((m.group(1), "launcher", _line_of(text, m.start())))
        for m in _PY_M_RE.finditer(text):
            found.append((m.group(1), "module", _line_of(text, m.start())))
        for ref, form, line in found:
            forms[form] += 1
            target: Optional[Path] = None
            stem = _SHELL_PREFIX_RE.sub("", ref)
            tail = re.sub(r"^[%$][\w]+[%$]?", "", stem) or ref
            if form == "module":
                mod_path = tail.replace(".", "/")
                target = _resolve_ref(src, base, mod_path,
                                      suffixes=(".py",), index_names=("__init__.py",))
            else:
                target = _resolve_ref(src, base, tail,
                                      suffixes=(".py",), index_names=("__init__.py",))
            if target is None:
                reason = ("variable-unresolved" if tail != stem or stem != ref
                          else "outside-src" if Path(ref).is_absolute()
                          or ref.replace("\\", "/").startswith("..")
                          # `python -m pip install ...` names an installed
                          # package, not a shard: reporting it as a missing file
                          # put "pip" at the top of the broken-launcher list.
                          else "external-module" if form == "module"
                          else "target-not-found")
                unresolved[reason] += 1
                if reason == "target-not-found":
                    # The useful form: WHICH file the driver wanted. A launcher
                    # pointing at a path that exists nowhere in the repo is a
                    # broken launcher, not a resolution gap.
                    missing[ref.strip().strip("'\"").replace("\\", "/")] += 1
                if len(detail) < 30:
                    detail.append({"from": here_file, "line": line, "ref": ref,
                                   "form": form, "result": reason})
                continue
            there_file = _rel_posix(src, target)
            calls[(here_file, there_file)] += 1
            there_tree = _tree_of(src, target)
            if here_tree:
                tree_out[here_tree] += 1
            if there_tree:
                tree_in[there_tree] += 1
            if here_tree and there_tree and here_tree != there_tree:
                tree_pairs[(here_tree, there_tree)] += 1
            if len(detail) < 30:
                detail.append({"from": here_file, "line": line, "to": there_file,
                               "form": form, "ref": ref})

    return {
        "language": "shell",
        "files": len(script_files),
        "statements": sum(calls.values()),
        "file_pairs": len(calls),
        "by_form": dict(sorted(forms.items())),
        "per_tree": {t: {"out": tree_out[t], "in": tree_in[t]}
                     for t in sorted(set(tree_out) | set(tree_in))},
        "tree_pairs": [{"from": a, "to": b, "refs": n}
                       for (a, b), n in sorted(tree_pairs.items())],
        "targets": dict(Counter(t for (_, t) in calls).most_common(12)),
        "missing_targets": dict(missing.most_common(15)),
        "missing_target_count": len(missing),
        "unresolved": dict(sorted(unresolved.items())),
        "detail": detail,
        "note": ("`python <file>`, `python -m <module>` and the `py` launcher; "
                 "%VAR%/`$VAR` prefixes are stripped before resolution and a call "
                 "that still does not resolve is counted by reason"),
    }


def build_html_graph(src: Path, html_files: List[Path]) -> Dict[str, Any]:
    """html -> asset edges (`<script src>`).

    142 html files made html the second-largest language here and none of it was
    analysed: a template that loads a recorder script is a join like any other.
    """
    edges: Counter[Tuple[str, str]] = Counter()
    tree_pairs: Counter[Tuple[str, str]] = Counter()
    tree_out: Counter[str] = Counter()
    tree_in: Counter[str] = Counter()
    unresolved: Counter[str] = Counter()
    external: Counter[str] = Counter()
    for path in html_files:
        text = _read_capped(path)
        if not text:
            continue
        here_file = _rel_posix(src, path)
        here_tree = _tree_of(src, path)
        for m in _HTML_SRC_RE.finditer(text):
            ref = m.group(1)
            if re.match(r"^(https?:)?//", ref) or ref.startswith("data:"):
                external[ref.split("/")[0][:40]] += 1
                continue
            target = _resolve_ref(src, path.parent, ref)
            if target is None:
                unresolved["target-not-found"] += 1
                continue
            there_file = _rel_posix(src, target)
            edges[(here_file, there_file)] += 1
            there_tree = _tree_of(src, target)
            if here_tree:
                tree_out[here_tree] += 1
            if there_tree:
                tree_in[there_tree] += 1
            if here_tree and there_tree and here_tree != there_tree:
                tree_pairs[(here_tree, there_tree)] += 1
    return {
        "language": "html",
        "files": len(html_files),
        "statements": sum(edges.values()),
        "file_pairs": len(edges),
        "tree_pairs": [{"from": a, "to": b, "refs": n}
                       for (a, b), n in sorted(tree_pairs.items())],
        "external_assets": sum(external.values()),
        "unresolved": dict(sorted(unresolved.items())),
        "note": "<script src> only; inline <script> bodies are not parsed",
    }


def census(src: Path, archive: Optional[Path] = None,
           extras: Optional[List[Path]] = None) -> Dict[str, Any]:
    """Measure one ``src`` tree (and optionally an archive) into a dict.

    `extras` are roots OUTSIDE ``src`` that still ship production code --
    ``tools/``, ``scripts/``, a crate directory. They are counted by language and
    scanned for seams only: they are not trees of the cleave, but a ledger that
    says "0 rust" while the repo holds a Cargo crate is measuring the wrong
    directory and reporting the answer as a fact.
    """
    src = Path(src)
    if not src.is_dir():
        raise FileNotFoundError(f"not a directory: {src}")

    files = sorted(p for p in src.rglob("*.py") if "__pycache__" not in p.parts)
    trees = sorted({p.relative_to(src).parts[0] for p in files
                    if len(p.relative_to(src).parts) > 1
                    and (src / p.relative_to(src).parts[0]).is_dir()})
    tree_set = set(trees)

    per_tree: Dict[str, Dict[str, Any]] = {
        t: {"py": 0, "lines": 0, "exec_units": 0, "langs": {}, "seams": [],
            "parse_fail": 0}
        for t in trees
    }
    loose: Dict[str, Any] = {"py": 0, "lines": 0, "langs": {}}
    parse_failures: List[Dict[str, Any]] = []

    edges_mod: Counter[Tuple[str, str]] = Counter()
    edges_any: Counter[Tuple[str, str]] = Counter()

    for f in files:
        rel = f.relative_to(src)
        here = rel.parts[0] if len(rel.parts) > 1 else None
        bucket = per_tree[here] if here in tree_set else loose
        bucket["py"] += 1
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            parse_failures.append({"file": str(f), "error": f"read: {exc}"})
            if isinstance(bucket, dict) and "parse_fail" in bucket:
                bucket["parse_fail"] += 1
            continue
        bucket["lines"] += text.count("\n")
        bucket.setdefault("langs", {})["python"] = (
            bucket.setdefault("langs", {}).get("python", 0) + 1)
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            parse_failures.append({"file": str(f), "line": exc.lineno,
                                   "error": "SyntaxError"})
            if isinstance(bucket, dict) and "parse_fail" in bucket:
                bucket["parse_fail"] += 1
            continue
        # Executable behaviour, not line count: a tree of dict literals is data.
        exec_units = sum(1 for n in ast.walk(tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                           ast.ClassDef)))
        if isinstance(bucket, dict) and "exec_units" in bucket:
            bucket["exec_units"] += exec_units
        if here not in tree_set:
            continue
        for root in _walk_imports(tree, module_level_only=False):
            if root in tree_set and root != here:
                edges_any[(here, root)] += 1
        for root in _walk_imports(tree, module_level_only=True):
            if root in tree_set and root != here:
                edges_mod[(here, root)] += 1

    # --- other languages + cross-language seams ----------------------------
    # Python was the only language this ledger could see. Every other source
    # file was invisible: a Rust extension or a TS front-end contributed 0
    # modules, hence 0 shards and 0 saplings, which reads as "empty" instead of
    # "not counted". Counted here per tree, by extension, with lines by byte
    # scan (no parser needed for a line count).
    lang_totals: Dict[str, int] = {}
    lang_lines: Dict[str, int] = {}
    lang_files: List[Tuple[Path, str]] = []
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        ext = f.suffix.lower()
        if ext == ".py" or ext not in LANGUAGES:
            continue
        rel = f.relative_to(src)
        bucket = per_tree.get(rel.parts[0]) if len(rel.parts) > 1 else None
        lang = LANGUAGES[ext]
        lang_totals[lang] = lang_totals.get(lang, 0) + 1
        try:
            with f.open("rb") as fh:
                n = fh.read(4_000_000).count(b"\n")
        except OSError:
            n = 0
        lang_lines[lang] = lang_lines.get(lang, 0) + n
        if isinstance(bucket, dict):
            bucket.setdefault("langs", {})[lang] = bucket["langs"].get(lang, 0) + 1
        lang_files.append((f, lang))

    # --- cross-language edges, resolved rather than asserted ----------------
    # `edges_any` can only ever hold python -> python, so a shell driver that
    # runs ``python src/CODEX/x.py`` and a TS front-end that imports ./panel
    # were both invisible: the ledger printed "0 cross-language seams", which
    # reads as "no coupling" when it meant "nothing looked". These are followed
    # through their real reference syntax (import/require/require(), script src,
    # ``python <file>``) and resolved to a tree, so the count is a measurement.
    cross_edges: Counter[Tuple[str, str]] = Counter()
    cross_pair: Counter[str] = Counter()
    cross_inbound: Dict[str, Counter] = defaultdict(Counter)
    cross_detail: List[Dict[str, Any]] = []
    # A zero that does not name its universe reads as "no coupling". Every
    # reference that could not be resolved is counted with its reason, so
    # "0 edges" can be told apart from "0 references looked at".
    cross_unresolved: Counter[str] = Counter()
    cross_unresolved_samples: List[Dict[str, str]] = []

    def _note_unresolved(reason: str, rel_from: Path, ref: str, lang: str) -> None:
        cross_unresolved[reason] += 1
        if len(cross_unresolved_samples) < 20:
            cross_unresolved_samples.append(
                {"from": rel_from.as_posix(), "ref": ref, "lang": lang,
                 "reason": reason})

    def _map_target(ref: str, base: Path) -> Optional[Tuple[str, str]]:
        ref = ref.strip().strip("'\"").replace("\\", "/")
        if not ref or ref.startswith(("http://", "https://", "data:", "#")):
            return None
        cands: List[Path] = []
        rp = Path(ref)
        if rp.is_absolute():
            cands.append(rp)
        else:
            cands.append((base / ref))
            cands.append((src / ref))
        for c in cands:
            for suffix in ("", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".py"):
                cand = Path(str(c) + suffix)
                try:
                    if not cand.is_file():
                        continue
                    rel = cand.resolve().relative_to(src.resolve())
                except (OSError, ValueError):
                    continue
                if len(rel.parts) < 2:
                    continue
                return rel.parts[0], cand.suffix.lower()
        return None

    for f, lang in lang_files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")[:400_000]
        except OSError:
            continue
        base = f.parent
        refs: List[str] = []
        if lang in ("javascript", "typescript"):
            refs += [m.group(1) for m in _JS_IMPORT_RE.finditer(text)]
        if lang in ("html",):
            refs += [m.group(1) for m in _HTML_SRC_RE.finditer(text)]
        if lang in ("shell", "batch"):
            refs += [m.group(1) for m in _PY_CALL_RE.finditer(text)]
        try:
            rel_from = f.relative_to(src)
        except ValueError:
            continue
        for ref in refs:
            via_var = None
            hit = _map_target(ref, base)
            stripped = re.sub(r"^[%$][\w]+[%$]?", "", ref.strip().strip("'\""))
            if not hit and stripped != ref and stripped:
                # `%SCRIPT_DIR%run.py` / `$HERE/run.py`: the variable is the
                # file's own directory in every one of these drivers, so the
                # tail is resolved relative to it -- and labelled, not hidden.
                hit = _map_target(stripped, base)
                via_var = stripped if hit else None
            if not hit:
                raw = ref.strip().strip("'\"")
                if lang in ("javascript", "typescript") and not raw.startswith("."):
                    # require('puppeteer') / from 'node:fs' name a package, not a
                    # shard. Counting them as "not found" made 200 real package
                    # imports look like 200 broken paths.
                    _note_unresolved("external-package", rel_from, ref, lang)
                elif re.search(r"[%$][\w]+[%$]?", raw):
                    _note_unresolved("variable-unresolved", rel_from, ref, lang)
                elif Path(raw).is_absolute() or raw.replace("\\", "/").startswith(".."):
                    _note_unresolved("outside-src", rel_from, ref, lang)
                else:
                    _note_unresolved("target-not-found", rel_from, ref, lang)
                continue
            tree_to, ext = hit
            tree_from = rel_from.parts[0] if len(rel_from.parts) > 1 else None
            if tree_from is None:
                continue
            to_lang = LANGUAGES.get(ext, "python" if ext == ".py" else "other")
            cross_edges[(tree_from, tree_to)] += 1
            cross_pair[f"{lang}->{to_lang}"] += 1
            if tree_from != tree_to:
                cross_inbound[tree_to][tree_from] += 1
            if len(cross_detail) < 40:
                cross_detail.append({"from": rel_from.as_posix(), "to": hit[0],
                                    "pair": f"{lang}->{to_lang}", "ref": ref,
                                    "via_variable": bool(via_var)})

    # --- per-language graphs, not per-language counts -----------------------
    # A count says "62 javascript modules". These say which module imports which,
    # which js module is imported by another tree, and which batch driver calls
    # which python file -- the joins that break when a shard is lifted out.
    js_files = [f for f, lg in lang_files if lg in ("javascript", "typescript")]
    shell_files = [f for f, lg in lang_files if lg in ("shell", "batch", "powershell")]
    html_files = [f for f, lg in lang_files if lg == "html"]
    graphs = {
        "javascript": build_js_graph(src, js_files),
        "shell": build_shell_graph(src, shell_files),
        "html": build_html_graph(src, html_files),
    }

    # Per-tree non-python coupling, so a tree's verdict can carry it. Counts ALL
    # edges whose endpoints are known, not only cross-tree ones: an intra-tree
    # edge still means the limb holds a real module graph and is not a flat pile
    # of scripts, which is what `0 edges` was hiding for CODEX's 61 js files.
    for gname, g in graphs.items():
        for tree, counts in (g.get("per_tree") or {}).items():
            if tree not in per_tree:
                continue
            rec = per_tree[tree].setdefault("nonpython", {})
            if counts.get("out"):
                out = rec.setdefault("out", {"total": 0, "by_language": {}})
                out["total"] += counts["out"]
                out["by_language"][gname] = out["by_language"].get(gname, 0) + counts["out"]
            if counts.get("in"):
                inn = rec.setdefault("in", {"total": 0, "by_language": {}})
                inn["total"] += counts["in"]
                inn["by_language"][gname] = inn["by_language"].get(gname, 0) + counts["in"]
        for tp in g.get("tree_pairs") or []:
            src_t, dst_t, n = tp["from"], tp["to"], tp["refs"]
            if src_t in per_tree:
                per_tree[src_t].setdefault("nonpython", {}).setdefault(
                    "cross_out", {})[dst_t] = n
            if dst_t in per_tree:
                per_tree[dst_t].setdefault("nonpython", {}).setdefault(
                    "cross_in", {})[src_t] = n

    # Seams: native or string-level coupling the AST graph cannot follow.
    for f in src.rglob("*"):
        if not f.is_file() or any(part in SKIP_DIRS for part in f.parts):
            continue
        rel = f.relative_to(src)
        if len(rel.parts) < 2:
            continue
        bucket = per_tree.get(rel.parts[0])
        if bucket is None:
            continue
        name = f.name.lower()
        if name == "cargo.toml":
            bucket["seams"].append(f"cargo:{rel.as_posix()}")
        elif name == "build.rs":
            bucket["seams"].append(f"build.rs:{rel.as_posix()}")
        elif f.suffix.lower() in (".pyd", ".so", ".dll", ".dylib"):
            bucket["seams"].append(f"native:{rel.as_posix()}")
        elif name in ("pyproject.toml", "setup.py"):
            try:
                text = f.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
            hit = [m for m in SEAM_MARKERS if m in text]
            if hit:
                bucket["seams"].append(f"{rel.as_posix()}:{','.join(hit)}")

    # --- periphery: production code that is not under src/ -----------------
    periphery: Dict[str, Any] = {}
    for extra in (extras or []):
        ep = Path(extra)
        if not ep.is_dir():
            periphery[str(ep)] = {"exists": False}
            continue
        lang: Dict[str, int] = {}
        seams: List[str] = []
        n_files = 0
        for f in ep.rglob("*"):
            if not f.is_file() or any(part in SKIP_DIRS for part in f.parts):
                continue
            n_files += 1
            lg = LANGUAGES.get(f.suffix.lower())
            if lg:
                lang[lg] = lang.get(lg, 0) + 1
            name = f.name.lower()
            if name == "cargo.toml" or name == "build.rs":
                seams.append(f"{name}:{f.relative_to(ep).as_posix()}")
            elif f.suffix.lower() in (".pyd", ".so", ".dll", ".dylib"):
                seams.append(f"native:{f.relative_to(ep).as_posix()}")
        periphery[str(ep)] = {"exists": True, "files": n_files,
                              "languages": dict(sorted(lang.items())),
                              "seams": seams[:40], "seam_count": len(seams)}

    inbound_any: Dict[str, Dict[str, int]] = defaultdict(dict)
    inbound_mod: Dict[str, Dict[str, int]] = defaultdict(dict)
    for (a, b), n in edges_any.items():
        inbound_any[b][a] = n
    for (a, b), n in edges_mod.items():
        inbound_mod[b][a] = n

    # --- tiers -------------------------------------------------------------
    def _is_stub(t: str) -> bool:
        # An unparseable module is NOT a stub: its `exec_units` is 0 only because
        # the parser never got to look. The first run of this rule classified
        # the fixture's `BAD` (one broken file) as a stub, which is the same
        # class of error as reading a parse failure as an empty file.
        return (not inbound_any.get(t)
                and per_tree[t]["py"] > 0
                and per_tree[t]["parse_fail"] == 0
                and per_tree[t]["py"] <= STUB_MAX_PY
                and per_tree[t]["exec_units"] == 0)

    def _other_langs(t: str) -> Dict[str, int]:
        return {k: v for k, v in (per_tree[t].get("langs") or {}).items()
                if k != "python"}

    stub_trees = [t for t in trees if _is_stub(t)]
    clean = [t for t in trees if not inbound_any.get(t) and not _is_stub(t)]
    # A clean PYTHON cut of a tree that is mostly another language is not a clean
    # cut of the tree. Measured 2026-10-31: CODEX is 87 python + 61 javascript
    # modules, and the ledger called it cleave-today because it only ever
    # imported-analyzed the python half.
    tier_a = [t for t in clean if not _other_langs(t)]
    tier_a_unaudited = [t for t in clean if _other_langs(t)]
    tier_b = [t for t in trees if inbound_any.get(t)]
    # A clean python cut that another LANGUAGE references is still a cut whose
    # join breaks: report it beside tier A rather than inside it, because a
    # shell wrapper is not an import and must not be miscounted as one.
    tier_a_cross = [t for t in tier_a if cross_inbound.get(t)]
    cycles = sorted({tuple(sorted((a, b))) for (a, b) in edges_mod
                     if (b, a) in edges_mod})
    cycle_blocked = sorted({t for pair in cycles for t in pair})

    # --- mycelium ----------------------------------------------------------
    hub_sites: Dict[str, Dict[str, int]] = {}
    hub_tokens: Dict[str, Set[str]] = {h: set() for h in HUBS}
    tree_text: Dict[str, str] = {t: "" for t in trees}
    for f in files:
        rel = f.relative_to(src)
        if len(rel.parts) < 2 or rel.parts[0] not in tree_set:
            continue
        try:
            tree_text[rel.parts[0]] += f.read_text(
                encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
    for hub in HUBS:
        files_hit = sites = 0
        for t, text in tree_text.items():
            n = text.count(hub)
            if n:
                files_hit += 1
                sites += n
                hub_tokens[hub].add(t)
        hub_sites[hub] = {"trees": files_hit, "sites": sites}
    speaking = {t for ts in hub_tokens.values() for t in ts}

    # --- saplings ----------------------------------------------------------
    src_modules = sum(v["py"] for v in per_tree.values()) + loose["py"]
    archive_modules = 0
    archive_trees = 0
    if archive is not None and Path(archive).is_dir():
        arch = Path(archive)
        archive_modules = sum(1 for p in arch.rglob("*.py")
                              if "__pycache__" not in p.parts)
        archive_trees = sum(1 for d in arch.iterdir()
                            if d.is_dir() and any(d.rglob("*.py")))

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(src),
        "definitions": {
            "tree": "directory directly under src/ holding >=1 .py",
            "any_import_edge": "import anywhere in the file (incl. function bodies)",
            "module_level_edge": "import executed at module import time",
            "clean": "no tree outside it imports it",
            "cycle": "direct mutual module-level import pair",
        },
        "totals": {
            "trees": len(trees),
            "modules_src": src_modules,
            "modules_archive": archive_modules,
            "archive_trees": archive_trees,
            "loose_modules": loose["py"],
            "lines_src": sum(v["lines"] for v in per_tree.values()) + loose["lines"],
            "parse_failures": len(parse_failures),
        },
        "trees": {
            t: {
                **per_tree[t],
                "inbound_any": inbound_any.get(t, {}),
                "inbound_module": inbound_mod.get(t, {}),
                "inbound_any_count": len(inbound_any.get(t, {})),
                "inbound_module_count": len(inbound_mod.get(t, {})),
                "is_trunk": t == TRUNK,
                "exec_units": per_tree[t]["exec_units"],
                "langs": per_tree[t]["langs"],
                "seams": sorted(set(per_tree[t]["seams"])),
                "is_stub": t in stub_trees,
                "nonpython": per_tree[t].get("nonpython") or {},
                "hubs": sorted(h for h, ts in hub_tokens.items() if t in ts),
            }
            for t in trees
        },
        "edges": {
            "module_level_pairs": len(edges_mod),
            "any_import_pairs": len(edges_any),
            "module_level_statements": sum(edges_mod.values()),
            "any_import_statements": sum(edges_any.values()),
        },
        "tiers": {
            "A_cleave_today": tier_a,
            "A_cross_language": [
                {"tree": t, "by": dict(sorted(cross_inbound[t].items()))}
                for t in tier_a_cross
            ],
            "A_mixed_unaudited": [
                {"tree": t, "py": per_tree[t]["py"],
                 "other": _other_langs(t)}
                for t in tier_a_unaudited
            ],
            "B_needs_shim": [
                {"tree": t, "inbound_any": len(inbound_any.get(t, {})),
                 "inbound_module": len(inbound_mod.get(t, {})),
                 "importers": sorted(inbound_any.get(t, {}))}
                for t in sorted(tier_b, key=lambda t: (-len(inbound_any[t]), t))
            ],
            "C_cycle_blocked": cycle_blocked,
            "D_stub": stub_trees,
        },
        "module_level_cycles": [list(c) for c in cycles],
        "cycles_real": len(cycles),
        "mycelium": {
            "hubs": hub_sites,
            "total_sites": sum(v["sites"] for v in hub_sites.values()),
            "trees_speaking": len(speaking),
            "trees_silent": sorted(set(trees) - speaking),
        },
        "saplings": {
            "shards_per_limb": SHARDS_PER_LIMB,
            "from_src": src_modules // SHARDS_PER_LIMB,
            "from_src_plus_archive": (src_modules + archive_modules) // SHARDS_PER_LIMB,
            "shard_slots_src": len(trees) * SHARDS_PER_LIMB,
            "remainder_src": src_modules % SHARDS_PER_LIMB,
            "by_language": {lang: n // SHARDS_PER_LIMB
                            for lang, n in sorted(lang_totals.items())},
            "pending_by_language": {lang: n % SHARDS_PER_LIMB
                                    for lang, n in sorted(lang_totals.items())},
        },
        "cross_language": {
            "pairs_by_language": dict(sorted(cross_pair.items())),
            "tree_pairs": [{"from": a, "to": b, "refs": n}
                           for (a, b), n in sorted(cross_edges.items())],
            "statements": sum(cross_edges.values()),
            "inbound": {t: dict(sorted(c.items())) for t, c in cross_inbound.items()},
            "detail": cross_detail,
            "unresolved": dict(sorted(cross_unresolved.items())),
            "unresolved_samples": cross_unresolved_samples,
            "note": ("shell/batch -> python by `python <file>`, js/ts -> js/ts by "
                     "import/require, html -> asset by <script src>; resolved to a "
                     "tree, not guessed from a filename match. `unresolved` counts "
                     "the references this pass could not place, by reason"),
        },
        "graphs": graphs,
        "periphery": periphery,
        "languages": {
            "modules": dict(sorted(lang_totals.items())),
            "lines": dict(sorted(lang_lines.items())),
            "python_modules": src_modules,
            "other_modules": sum(lang_totals.values()),
            "instrumented": ["python"],
            "note": ("only python is import-analysed; other languages are COUNTED "
                     "(modules, lines, per tree) but their edges are not resolved, "
                     "so a mixed tree's clean-cut verdict rests on the python half"),
        },
        "parse_failure_detail": parse_failures[:20],
        "limits": [
            "static scan: importlib/__import__ and string-based plugin loading "
            "(the worm registry) are invisible, so runtime coupling is higher",
            "cycle detection covers direct mutual pairs only, not A->B->C->A",
            "archive is counted, never import-analysed",
        ],
    }


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def render(led: Dict[str, Any]) -> str:
    t = led["totals"]
    out: List[str] = []
    add = out.append
    add(f"YGGDRASIL census — {led['root']}")
    add(f"generated {led['generated_at']}")
    add("")
    add(f"trees {t['trees']}  modules {t['modules_src']}  lines {t['lines_src']:,}"
        f"  parse failures {t['parse_failures']}"
        + (f"  archive modules {t['modules_archive']}" if t["modules_archive"] else ""))
    add("")
    add(f"TIER A — cleave today, python-audited ({len(led['tiers']['A_cleave_today'])})")
    add("  " + ", ".join(led["tiers"]["A_cleave_today"]))
    mixed = led["tiers"].get("A_mixed_unaudited") or []
    add("")
    add(f"TIER A-MIXED — python-clean, other languages UNAUDITED ({len(mixed)})")
    if not mixed:
        add("  — none")
    for row in mixed:
        other = ", ".join(f"{k} {v}" for k, v in row["other"].items())
        add(f"  {row['tree']:<16}{row['py']:>4} py + {other} — cut verdict rests on the python half")
    add("")
    cross = led.get("cross_language") or {}
    xa = led["tiers"].get("A_cross_language") or []
    add(f"TIER A-CROSS — python-clean but referenced from another language ({len(xa)})")
    if not xa:
        add("  — none")
    for row in xa:
        by = ", ".join(f"{k} {v} ref(s)" for k, v in row["by"].items())
        add(f"  {row['tree']:<16}{by}")
    add("")
    add("LANGUAGE GRAPHS — resolved file by file, not counted")
    for key, g in (led.get("graphs") or {}).items():
        ext = g.get("external_statements", g.get("external_assets", 0))
        cycles = len(g.get("cycles") or [])
        add(f"  {key:<11}{g['files']:>4} file(s) {g['statements']:>5} edge(s) "
            f"{g['file_pairs']:>4} pair(s)  {len(g.get('tree_pairs') or []):>2} tree pair(s)"
            f"  {cycles} cycle(s)  {ext} external"
            + (f"  forms {g['by_form']}" if g.get("by_form") else ""))
        unres = g.get("unresolved") or {}
        if unres:
            add("    unresolved: " + ", ".join(f"{k} {v}" for k, v in unres.items()))
    add("")
    add(f"CROSS-LANGUAGE — {cross.get('statements', 0)} reference(s) between "
        f"{len(cross.get('tree_pairs') or [])} tree pair(s)")
    for pair, n in (cross.get("pairs_by_language") or {}).items():
        add(f"  {pair:<24}{n:>5}")
    unres = cross.get("unresolved") or {}
    if unres:
        add("  unresolved (universe for the count above): "
            + ", ".join(f"{k} {v}" for k, v in unres.items()))
    add(f"TIER B — needs a shim ({len(led['tiers']['B_needs_shim'])} trees, "
        f"{led['edges']['any_import_pairs']} tree-pairs, "
        f"{led['edges']['any_import_statements']} import statements)")
    for row in led["tiers"]["B_needs_shim"]:
        trunk = "  (trunk)" if row["tree"] == TRUNK else ""
        add(f"  {row['tree']:<16}{row['inbound_any']:>3} in   "
            f"{row['inbound_module']:>3} at module level{trunk}")
    add("")
    add(f"TIER C — cycle-blocked ({led['cycles_real']})"
        + (": " + ", ".join(" <-> ".join(c) for c in led["module_level_cycles"])
           if led["module_level_cycles"] else " — none"))
    add("")
    stub = led["tiers"]["D_stub"]
    add(f"TIER D — stub, not a cleave ({len(stub)})"
        + (" (nothing imports it, <=%d modules, no function or class)" % STUB_MAX_PY
           if stub else " — none"))
    for name in stub:
        row = led["trees"][name]
        add(f"  {name:<16}{row['py']:>3} modules  {row['lines']:>6} lines  "
            f"exec units {row['exec_units']}")
    add("")
    myc = led["mycelium"]
    add(f"MYCELIUM — {myc['trees_speaking']}/{t['trees']} trees speak >=1 hub, "
        f"{myc['total_sites']} sites; silent: "
        + (", ".join(myc["trees_silent"]) or "none"))
    for hub, v in myc["hubs"].items():
        add(f"  {hub:<15}{v['trees']:>4} trees {v['sites']:>7} sites")
    add("")
    s = led["saplings"]
    add(f"SAPLINGS — {s['from_src']} from src alone, "
        f"{s['from_src_plus_archive']} with the archive "
        f"({s['shards_per_limb']} shards/limb, remainder {s['remainder_src']})")
    langs = led["languages"]["modules"]
    if langs:
        add("")
        add("LANGUAGES — counted, not import-analysed")
        lines = led["languages"]["lines"]
        for lang, n in sorted(langs.items(), key=lambda kv: -kv[1]):
            add(f"  {lang:<12}{n:>6} modules {lines.get(lang, 0):>9,} lines "
                f"{n // s['shards_per_limb']:>3} saplings")
        add(f"  python       {s['from_src']:>6} saplings across {led['totals']['trees']} trees "
            f"(import-analysed)")
    peri = led.get("periphery") or {}
    if peri:
        add("")
        add("PERIPHERY — production code outside src/ (counted, never import-analysed)")
        for path, rec in peri.items():
            if not rec.get("exists"):
                add(f"  {path} — missing")
                continue
            langs = ", ".join(f"{k} {v}" for k, v in (rec["languages"] or {}).items()) or "none"
            add(f"  {path} — {rec['files']:,} files; {langs}; "
                f"{rec['seam_count']} seam marker(s)")
            for s in rec["seams"][:4]:
                add(f"      {s}")
    seams = [(t, r["seams"]) for t, r in led["trees"].items() if r.get("seams")]
    if seams:
        add("")
        add(f"CROSS-LANGUAGE SEAMS — {len(seams)} tree(s) coupled outside the AST graph")
        for t, ss in sorted(seams):
            add(f"  {t:<16}{len(ss):>3} marker(s)  e.g. {ss[0][:70]}")
    if t["parse_failures"]:
        add("")
        add("PARSE FAILURES")
        for row in led["parse_failure_detail"]:
            add(f"  {row['file']}:{row.get('line')} {row['error']}")
    return "\n".join(out)


# --------------------------------------------------------------------------
# shard plan: the same limb -> 24 shards grammar, per language, as data
# --------------------------------------------------------------------------

def module_inventory(src: Path) -> Dict[str, List[str]]:
    """Every source file under ``src`` by language. Python first if present."""
    src = Path(src)
    out: Dict[str, List[str]] = {}
    for f in src.rglob("*"):
        if not f.is_file() or any(p in SKIP_DIRS for p in f.parts):
            continue
        ext = f.suffix.lower()
        lang = "python" if ext == ".py" else LANGUAGES.get(ext)
        if not lang:
            continue
        out.setdefault(lang, []).append(f.relative_to(src).as_posix())
    return {k: sorted(v) for k, v in sorted(out.items())}


def shard_plan(src: Path, shard_size: int = SHARDS_PER_LIMB) -> Dict[str, Any]:
    """Assign every module of every language to exactly one shard.

    The cleave grammar (limb -> 24 shards -> sapling) was written for Python,
    where a shard is a directory of importable modules. Counting JS/TS/shell
    modules produces a *number*, not a shard: nothing says which files belong
    to which. This assigns them, ordered by tree and path so a shard stays
    inside one limb wherever the arithmetic allows, and reports the shards that
    still straddle a tree -- a straddling shard cannot be lifted out cleanly in
    any language, python included.
    """
    inv = module_inventory(src)
    langs: Dict[str, Any] = {}
    for lang, mods in inv.items():
        # Two allocations, measured together. `continuous` is the naive global
        # 24-chunk: cheap, but a chunk that spans two trees is a shard nobody
        # can lift out. `limb_aligned` chunks inside each tree, which removes
        # straddling at the cost of underfilled shards. Both numbers are
        # reported so the choice is a decision, not an assumption.
        keyed = sorted(mods, key=lambda p: (p.split("/")[0], p))
        cont = [keyed[i:i + shard_size] for i in range(0, len(keyed), shard_size)]
        cont_straddle = sum(1 for c in cont if len({p.split("/")[0] for p in c}) > 1)

        by_tree: Dict[str, List[str]] = {}
        for p in keyed:
            by_tree.setdefault(p.split("/")[0], []).append(p)
        shards: List[Dict[str, Any]] = []
        for tree, members in by_tree.items():
            for j in range(0, len(members), shard_size):
                chunk = members[j:j + shard_size]
                shards.append({"id": f"{lang[:3]}-{tree.lower()}-{j // shard_size:02d}",
                               "tree": tree, "trees": [tree], "straddles": False,
                               "size": len(chunk), "modules": chunk})
        langs[lang] = {
            "modules": len(keyed),
            "shards": len(shards),
            "saplings": len(shards) // shard_size,
            "pending": len(keyed) % shard_size,
            "instrumented": lang == "python",
            "straddling_shards": sum(1 for s in shards if s["straddles"]),
            "underfilled": sum(1 for s in shards if s["size"] < shard_size // 2),
            "wasted_slots": len(shards) * shard_size - len(keyed),
            "continuous": {"shards": len(cont), "straddling": cont_straddle},
            "detail": shards,
        }
    return {"schema": "azazael.shard_plan/2",
            "root": str(src), "shard_size": shard_size,
            "mode": "limb_aligned (a shard never spans two trees)",
            "languages": langs,
            "totals": {"modules": sum(v["modules"] for v in langs.values()),
                       "shards": sum(v["shards"] for v in langs.values()),
                       "straddling_shards": sum(v["straddling_shards"]
                                                 for v in langs.values()),
                       "continuous_straddling": sum(v["continuous"]["straddling"]
                                                     for v in langs.values()),
                       "wasted_slots": sum(v["wasted_slots"]
                                           for v in langs.values())}}


# --------------------------------------------------------------------------
# self-test: a scanner that has never been proven wrong is not an oracle
# --------------------------------------------------------------------------

def selftest() -> int:
    """Negative controls: known-shaped fixtures the scanner MUST classify right."""
    import tempfile

    failures: List[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "src"
        (root / "AAA").mkdir(parents=True)
        (root / "BBB").mkdir()
        (root / "CCC").mkdir()
        (root / "DDD").mkdir()
        # AAA imports BBB at module level; BBB imports AAA inside a function.
        (root / "AAA" / "a.py").write_text(
            "import BBB.b\nfrom CCC import c\nprint('audit')\n", encoding="utf-8")
        (root / "BBB" / "b.py").write_text(
            "def f():\n    from AAA import a\n    return a\n", encoding="utf-8")
        (root / "CCC" / "c.py").write_text("c = 1\n", encoding="utf-8")
        (root / "DDD" / "d.py").write_text("import BBB.b\n", encoding="utf-8")
        (root / "loose.py").write_text("x = 1\n", encoding="utf-8")
        (root / "BAD").mkdir()
        (root / "BAD" / "broken.py").write_text("def (:\n", encoding="utf-8")
        # EEE: python-clean but carries a TS module the ledger cannot analyse.
        (root / "EEE").mkdir()
        (root / "EEE" / "e.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (root / "EEE" / "x.ts").write_text("export const x = 1;\n", encoding="utf-8")
        # FFF is python-clean, but a shell driver runs one of its files: the
        # join is real and the AST graph cannot see it.
        (root / "FFF").mkdir()
        (root / "FFF" / "f.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (root / "GGG").mkdir()
        (root / "GGG" / "run.sh").write_text("#!/bin/sh\npython ../FFF/f.py\n",
                                             encoding="utf-8")
        (root / "GGG" / "mod.sh").write_text("#!/bin/sh\npython -m FFF.f\n",
                                             encoding="utf-8")
        # A js graph with one real edge, one cross-tree import and one external
        # package: the three outcomes must not be collapsed into "imports: 3".
        (root / "III").mkdir()
        (root / "III" / "widget.js").write_text("export const w = 1;\n", encoding="utf-8")
        (root / "III" / "use.js").write_text(
            "import { w } from './widget.js';\nexport default w;\n", encoding="utf-8")
        (root / "III" / "tool.js").write_text(
            "const p = require('puppeteer');\nmodule.exports = p;\n", encoding="utf-8")
        (root / "HHH").mkdir()
        (root / "HHH" / "app.js").write_text(
            "const { w } = require('../III/widget.js');\n", encoding="utf-8")

        led = census(root)
        tiers = led["tiers"]
        b_trees = [r["tree"] for r in tiers["B_needs_shim"]]

        # Nobody imports BAD (unparseable) or DDD; AAA and CCC are imported,
        # CCC at module level by AAA and AAA by BBB from inside a function.
        # BAD is unparseable and DDD is a data stub: neither is a cleave, and
        # BAD must be excluded from the stub tier too (unknown != empty).
        if tiers["A_cleave_today"] != ["BAD", "FFF"]:
            failures.append(f"tier A = {tiers['A_cleave_today']!r}, expected ['BAD', 'FFF']")
        # The exact error the 2026-10-30 analysis made: a function-local
        # back-import must NOT register as a cycle.
        if led["cycles_real"] != 0:
            failures.append(f"function-local back-import counted as a cycle: "
                            f"{led['module_level_cycles']!r}")
        # ...but it MUST keep AAA out of tier A, because the edge still breaks
        # when the tree is lifted out.
        if "AAA" not in b_trees:
            failures.append(f"function-local importer AAA missing from tier B: {b_trees!r}")
        if "CCC" not in b_trees:
            failures.append("CCC (module-level import by AAA) missing from tier B")
        if led["trees"]["AAA"]["inbound_module_count"] != 0:
            failures.append("AAA counted as module-level inbound, expected 0")
        if led["totals"]["loose_modules"] != 1:
            failures.append(f"loose modules = {led['totals']['loose_modules']}, expected 1")
        if led["totals"]["parse_failures"] != 1:
            failures.append(f"parse failures = {led['totals']['parse_failures']}, expected 1")
        if led["mycelium"]["trees_silent"] != ["BAD", "BBB", "CCC", "DDD", "EEE", "FFF"]:
            failures.append(f"silent trees = {led['mycelium']['trees_silent']!r}")
        cross = led.get("cross_language") or {}
        if cross.get("pairs_by_language", {}).get("shell->python") != 1:
            failures.append(f"cross-language shell->python = "
                            f"{cross.get('pairs_by_language')!r}, expected 1")
        across = [r["tree"] for r in led["tiers"].get("A_cross_language") or []]
        if across != ["FFF"]:
            failures.append(f"A-CROSS = {across!r}, expected ['FFF']")
        if "FFF" not in led["tiers"]["A_cleave_today"]:
            failures.append("a shell reference must not evict FFF from tier A")
        g = led.get("graphs") or {}
        js = g.get("javascript") or {}
        # Two internal edges (use->widget, HHH/app->widget). tool->puppeteer is a
        # dependency, so counting it here would be the old bug in a new function.
        if js.get("statements") != 2:
            failures.append("js graph statements = %r, expected 2 internal edges"
                            % js.get("statements"))
        if js.get("external_packages", {}).get("puppeteer") != 1:
            failures.append("js external package not isolated: %r"
                            % (js.get("external_packages"),))
        if {"from": "HHH", "to": "III", "refs": 1} not in (js.get("tree_pairs") or []):
            failures.append("js cross-tree edge HHH->III missing: %r"
                            % (js.get("tree_pairs"),))
        sh = g.get("shell") or {}
        if sh.get("by_form") != {"file": 1, "module": 1}:
            failures.append("shell call forms = %r, expected {'file': 1, 'module': 1}"
                            % (sh.get("by_form"),))
        if sh.get("statements") != 2:
            failures.append("shell graph statements = %r, expected 2" % sh.get("statements"))
        plan = shard_plan(root)
        for lang, blk in plan["languages"].items():
            flat = [m for s in blk["detail"] for m in s["modules"]]
            if len(flat) != len(set(flat)) or len(flat) != blk["modules"]:
                failures.append(f"shard plan {lang}: modules duplicated or dropped")
            if any(len(s["modules"]) > plan["shard_size"] for s in blk["detail"]):
                failures.append(f"shard plan {lang}: shard over shard_size")
        if led["saplings"]["from_src"] != 0:
            failures.append(f"saplings below one shard should be 0: "
                            f"{led['saplings']['from_src']}")
        # A tree of dict literals that nothing imports must NOT be offered as a
        # cleave candidate: without this control, adding 3 files of prompt data
        # silently grew Tier A from 9 to 10 (measured 2026-10-31).
        if led["tiers"]["D_stub"] != ["DDD"]:
            failures.append(f"stub tier = {led['tiers']['D_stub']!r}, expected ['DDD'] "
                            f"(1 module, no defs, nothing imports it)")
        if "DDD" in led["tiers"]["A_cleave_today"]:
            failures.append("stub tree DDD leaked into tier A")
        # A tree with an unanalysed TS module must be reported as mixed, never
        # certified as a clean python cut.
        mixed = [r["tree"] for r in led["tiers"].get("A_mixed_unaudited") or []]
        if mixed != ["EEE"]:
            failures.append(f"mixed tier = {mixed!r}, expected ['EEE']")
        if "EEE" in led["tiers"]["A_cleave_today"]:
            failures.append("mixed tree EEE leaked into tier A")

    if failures:
        print("SELFTEST FAILED", file=sys.stderr)
        for f in failures:
            print("  - " + f, file=sys.stderr)
        return 3
    print("SELFTEST OK — 19 controls (tier list, cycle filter, tier B membership, "
          "loose modules, parse failure, hub silence, stub tier, no stub in tier A, "
          "mixed-language tier, no mixed tree in tier A, cross-language edge, "
          "A-CROSS membership, shell does not evict a tree, shard plan partitions, "
          "js edge count, js external isolation, js cross-tree edge, shell call "
          "forms, shell statement count)")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None,
                    help="src directory to scan (default: ../src next to this tool)")
    ap.add_argument("--archive", default=None,
                    help="archive directory to count (default: ../archived_unified)")
    ap.add_argument("--extra-root", action="append", default=None,
                    help="root outside src/ to count by language (repeatable, e.g. tools scripts)")
    ap.add_argument("--json", action="store_true", help="emit the ledger as JSON")
    ap.add_argument("--out", default=None, help="write JSON to this path as well")
    ap.add_argument("--selftest", action="store_true", help="run scanner controls")
    ap.add_argument("--plan", default=None,
                    help="write the per-language shard plan JSON to this path")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    here = Path(__file__).resolve().parent
    root = Path(args.root) if args.root else here.parent / "src"
    archive = Path(args.archive) if args.archive else here.parent / "archived_unified"

    try:
        extras = [Path(p) for p in (args.extra_root or [])]
        if not args.extra_root:
            # Default: the two places production code actually lives outside src/.
            extras = [root.parent / "tools", root.parent / "scripts"]
        ledger = census(root, archive, extras)
    except FileNotFoundError as exc:
        print(f"yggdrasil_census: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(ledger, indent=2, sort_keys=False) if args.json else render(ledger)
    print(text)
    if args.plan:
        plan = shard_plan(root)
        Path(args.plan).write_text(json.dumps(plan, indent=1), encoding="utf-8")
        lb = plan["languages"]
        print("\nSHARD PLAN — " + ", ".join(
            f"{k} {v['modules']} mod / {v['shards']} shards / "
            f"{v['underfilled']} underfilled / cont-straddle "
            f"{v['continuous']['straddling']}" for k, v in lb.items()),
              file=sys.stderr)
        print(f"  totals: {plan['totals']}", file=sys.stderr)
        print(f"wrote {args.plan}", file=sys.stderr)

    if args.out:
        Path(args.out).write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
