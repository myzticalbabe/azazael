"""native_fn_audit.py -- missed-native-functions audit (Board-48992).

Three questions, answered from the tree itself:

1. referenced-but-not-built: a Python module name that looks native
   (.pyx source exists, or a native-only import pattern) with no built
   artifact (.so/.pyd) anywhere in the tree.
2. built-but-unreferenced: an artifact no Python file imports.
3. pyx-without-record: a .pyx with no build recipe naming it
   (tools/build_native.py only knows what it is told).

Read-only. Exit 0 = no gaps. Exit 1 = gaps listed. Exit 2 = tree
unreadable (never a false clean).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILD_TOOL = REPO / "tools" / "build_native.py"

#: import X / from X import ... / cimport X (X dotted, take last segment)
#: plus relative `from . import a, b` / `from .pkg import x` forms.
IMPORT_RE = re.compile(r"^\s*(?:import|from|cimport)\s+([A-Za-z_][\w.]*)", re.M)
REL_IMPORT_RE = re.compile(r"^\s*from\s+\.([\w.]*)\s+import\s+(.+)$", re.M)
#: dynamic references: quoted dotted names, e.g. the loader tuple in
#: native_replay.py (`for _mod in ("eve_unleashed._replay_cy", ...)`).
STRING_REF_RE = re.compile(r"['\"]([A-Za-z_][\w.]*)['\"]")
#: native-only import smells: ctypes binding to a local lib, cffi verify
NATIVE_SMELL_RE = re.compile(r"ctypes\.(CDLL|WinDLL)|cffi|__declspec|PyInit_", re.M)

#: Generated/vendored artifact trees: never repo-owned natives. build/
#: holds the CLUSTERWORMS dist (a vendored CPython+numpy), dist/ the
#: shipped bundles. pyx/py/artifact scans all skip these.
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".mypy_cache",
    "build",
    "dist",
    "dist-native",
}


def iter_py_files(root: Path):
    for p in root.rglob("*.py"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Audit native entry points.")
    ap.add_argument("--json", metavar="PATH", default=None)
    ap.add_argument("--root", default=str(REPO))
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"unreadable tree: {root}")
        return 2

    def _kept(p: Path) -> bool:
        return not any(part in SKIP_DIRS for part in p.parts)

    pyx = {p.stem: str(p.relative_to(root)) for p in root.rglob("*.pyx")
           if _kept(p)}
    artifacts: dict[str, str] = {}
    for ext in ("*.so", "*.pyd"):
        for p in root.rglob(ext):
            if not _kept(p):
                continue
            # stem strips one suffix: foo.cp314t-win_amd64.pyd -> keep full
            # tag-free base (foo) for the import-name match.
            artifacts.setdefault(p.name.split(".")[0],
                                 str(p.relative_to(root)))

    referenced: dict[str, set[str]] = {}
    smells: list[str] = []
    for fp in iter_py_files(root):
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(fp.relative_to(root))
        for m in IMPORT_RE.finditer(text):
            mod = m.group(1).split(".")[-1]
            referenced.setdefault(mod, set()).add(rel)
        for m in REL_IMPORT_RE.finditer(text):
            pkg, names = m.group(1), m.group(2)
            for name in re.split(r"[,\s]+", names):
                name = name.split(" as ")[0].strip().strip("()")
                if name and name != "*":
                    mod = name.split(".")[-1]
                    referenced.setdefault(mod, set()).add(rel)
            if pkg:
                referenced.setdefault(pkg.split(".")[-1], set()).add(rel)
        if NATIVE_SMELL_RE.search(text):
            smells.append(rel)

    # string-literal dynamic references (loader tuples, importlib names)
    known_mods = set(pyx) | set(artifacts)
    for fp in iter_py_files(root):
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(fp.relative_to(root))
        for m in STRING_REF_RE.finditer(text):
            mod = m.group(1).split(".")[-1]
            if mod in known_mods:
                referenced.setdefault(mod, set()).add(rel)

    known = set()
    try:
        tree = __import__("ast").parse(
            BUILD_TOOL.read_text(encoding="utf-8", errors="replace"))
        for node in __import__("ast").walk(tree):
            if isinstance(node, __import__("ast").Assign):
                for t in node.targets:
                    if getattr(t, "id", "") == "KNOWN_PYX":
                        known = set(
                            s.value for s in node.value.elts
                            if isinstance(s, __import__("ast").Constant))
    except (OSError, SyntaxError):
        pass

    missing_built = sorted(
        (mod, sorted(files)) for mod, files in referenced.items()
        if mod in pyx and mod not in artifacts
    )
    orphan_built = sorted(
        (mod, path) for mod, path in artifacts.items() if mod not in referenced
    )
    pyx_no_record = sorted(
        (mod, path) for mod, path in pyx.items()
        if not any(mod in k for k in known)
    )

    report = {
        "root": str(root),
        "counts": {
            "pyx": len(pyx),
            "artifacts": len(artifacts),
            "missing_built": len(missing_built),
            "orphan_built": len(orphan_built),
            "pyx_no_record": len(pyx_no_record),
            "native_smell_files": len(smells),
        },
        "missing_built": [{"module": m, "referenced_by": f}
                          for m, f in missing_built],
        "orphan_built": [{"module": m, "artifact": a}
                         for m, a in orphan_built],
        "pyx_no_record": [{"module": m, "pyx": p} for m, p in pyx_no_record],
        "native_smell_files": sorted(smells)[:50],
    }
    print(json.dumps(report["counts"], indent=1))
    for m, files in missing_built:
        print(f"MISSING-BUILT {m} referenced by {len(files)} file(s):"
              f" {', '.join(files[:3])}")
    for m, a in orphan_built:
        print(f"ORPHAN-BUILT {m} at {a}")
    for m, p in pyx_no_record:
        print(f"PYX-NO-RECORD {m} ({p})")
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1),
                                    encoding="utf-8")
    return 1 if (missing_built or orphan_built or pyx_no_record) else 0


if __name__ == "__main__":
    sys.exit(main())
