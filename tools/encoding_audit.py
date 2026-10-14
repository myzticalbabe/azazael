#!/usr/bin/env python3
# coding: utf-8
"""Encoding audit — find subprocess calls that decode with the OS codec.

The failure this detects, measured
----------------------------------
On Windows a `subprocess` call that captures output in TEXT mode without
`encoding=` lets the platform codec (cp1252) decode it. Non-ASCII output then
raises `UnicodeDecodeError` **inside subprocess's reader thread**, where it does
NOT propagate to the caller: the call appears to succeed and yields EMPTY
stdout. Measured 2026-10-13 during ratchet attribution work — a file with two
findings was scored as having zero, and a wrong per-file attribution was
reported from that phantom reading before the empty stdout was traced back to
the decode failure.

Why this parses instead of grepping
-----------------------------------
A same-line grep is not a valid detector, and this was measured too: grepping
`tools/` and `scripts/` for text-capture call sites reported 155 candidate
lines, but `encoding=` is frequently on a CONTINUATION line and is invisible to
a line-oriented match, while a `capture_output=True` call that never enables
text mode decodes nothing and cannot fail this way. Both errors point the same
direction — the question is about a call's KEYWORDS, so the source has to be
parsed. This tool walks the AST and inspects each call's kwargs.

What counts as decoding
-----------------------
`text=True` and `universal_newlines=True` decode. `encoding=` and `errors=`
only have an effect in text mode, so passing either IS text mode:
`subprocess.run(cmd, errors="replace")` decodes with the OS codec and that
handler, which is exactly the silent-truncation shape. A call that captures
bytes (`capture_output=True` with no text mode) is NOT reported — it decodes
nothing.

Known gaps, named rather than assumed
-------------------------------------
`subprocess.getoutput` / `getstatusoutput` always return `str` and take no
`encoding=`, so they cannot be fixed, only replaced by `subprocess.run(...)`.
Neither appears in `tools/` or `scripts/`, and `from subprocess import run`
appears only in archived vendored trees, so neither form is modelled here. If
one is introduced, this tool will not see it — re-check with
`grep -rn "getoutput\\|from subprocess import" tools/ scripts/` rather than
assume coverage. `import subprocess as _sp` IS modelled: it is the form in use
in `scripts/spine_cycle_apply.py`, and a bare `_sp.run(...)` is invisible to a
check that only looks for the literal name `subprocess`.

Usage
-----
    python tools/encoding_audit.py                 # report, exit 0
    python tools/encoding_audit.py --check         # gate: exit 1 on any finding
    python tools/encoding_audit.py --dir tools --dir scripts
    python tools/encoding_audit.py --json
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Scan roots when `--dir` is not given, repo-relative.
DEFAULT_DIRS = ("tools", "scripts")

#: subprocess entry points that accept the same text-mode kwargs.
ENTRY_POINTS = ("run", "Popen", "check_output", "check_call", "call")

#: Kwargs that turn text mode on by themselves; `encoding`/`errors` are inert
#: outside text mode, so their presence implies it (handled in `_decoding`).
TEXT_KWARGS = ("text", "universal_newlines")


def _iter_py_files(dirs: "list[str]") -> "list[Path]":
    """Every `.py` file under each `--dir` (a file argument is taken as-is)."""
    out: "list[Path]" = []
    for entry in dirs:
        base = Path(entry)
        base = base if base.is_absolute() else (ROOT / entry)
        if base.is_file():
            if base.suffix == ".py":
                out.append(base)
            continue
        if not base.is_dir():
            continue
        out.extend(sorted(p for p in base.rglob("*.py")
                          if "__pycache__" not in p.parts))
    return out


def _subprocess_names(tree: ast.AST) -> "tuple[set[str], set[str]]":
    """Return (names bound to the module, entry points imported from it).

    Both import forms are collected because a detector whose whole purpose is
    not missing a site cannot afford to understand only one spelling of it.
    """
    aliases: "set[str]" = set()
    from_names: "set[str]" = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    aliases.add(alias.asname or "subprocess")
        elif isinstance(node, ast.ImportFrom):
            if node.module == "subprocess":
                for alias in node.names:
                    if alias.name in ENTRY_POINTS:
                        from_names.add(alias.asname or alias.name)
    return aliases, from_names


def _entry_point(node: ast.Call, aliases: "set[str]",
                 from_names: "set[str]") -> "str | None":
    """The subprocess function this call invokes, or None if it is not one."""
    func = node.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        if func.value.id in aliases and func.attr in ENTRY_POINTS:
            return "subprocess.%s" % func.attr
        return None
    if isinstance(func, ast.Name) and func.id in from_names:
        return "subprocess.%s" % func.id
    return None


def _decoding(node: ast.Call) -> dict:
    """Classify one call's decoding kwargs.

    Three states, because conflating the last two is how a detector starts
    reporting things it has not checked:

      confirmed  — text mode is definitely on (literal `text=True`, or an
                   `encoding`/`errors` kwarg, whose presence implies text mode).
      undetermined — `**kwargs` could supply the text flags, or a text kwarg
                   holds a non-literal value, so a constant cannot settle it.
      clean      — bytes were captured, or `encoding=` is present.
    """
    kwargs: "dict[str, ast.expr]" = {}
    splat = False
    for kw in node.keywords:
        if kw.arg is None:
            splat = True
        else:
            kwargs[kw.arg] = kw.value

    def _literal_true(name: str) -> bool:
        value = kwargs.get(name)
        return isinstance(value, ast.Constant) and bool(value.value)

    symbolic = [name for name in TEXT_KWARGS
                if name in kwargs and not isinstance(kwargs[name], ast.Constant)]
    confirmed = (_literal_true("text") or _literal_true("universal_newlines")
                 or "encoding" in kwargs or "errors" in kwargs)
    return {"confirmed": confirmed, "has_encoding": "encoding" in kwargs,
            "splat": splat, "symbolic": symbolic,
            "unknown": bool(symbolic) or splat}


def scan_file(path: Path) -> dict:
    """Return the audit result for one file.

    A file that will not parse is REPORTED as skipped with its error rather than
    silently contributing zero sites -- an unreadable file and a clean file must
    not look the same in the output, which is the whole lesson of this tool.
    """
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"path": path, "scanned": False, "findings": [], "undetermined": [],
                "skipped": "line %s: %s" % (exc.lineno, exc.msg)}

    aliases, from_names = _subprocess_names(tree)
    lines = source.splitlines()
    findings: "list[dict]" = []
    undetermined: "list[dict]" = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        entry = _entry_point(node, aliases, from_names)
        if entry is None:
            continue
        info = _decoding(node)
        row = {"line": node.lineno, "call": entry,
               "source": (lines[node.lineno - 1].strip()[:120]
                          if node.lineno <= len(lines) else "")}
        if info["confirmed"] and not info["has_encoding"]:
            row["note"] = ("**kwargs may supply encoding" if info["splat"] else "")
            findings.append(row)
        elif info["unknown"]:
            row["note"] = ("**kwargs present" if info["splat"]
                           else "%s is not a literal" % ", ".join(info["symbolic"]))
            undetermined.append(row)
    return {"path": path, "scanned": True, "findings": findings,
            "undetermined": undetermined, "skipped": None}


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", action="append", default=None, metavar="PATH",
                    help="file or directory to scan, repeatable "
                         "(default: %s)" % " ".join(DEFAULT_DIRS))
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when any text-decoding call lacks encoding=")
    ap.add_argument("--json", action="store_true",
                    help="emit the same result as JSON")
    args = ap.parse_args()

    dirs = args.dir or list(DEFAULT_DIRS)
    files = _iter_py_files(dirs)

    by_file: "dict[str, list[dict]]" = {}
    undetermined: "dict[str, list[dict]]" = {}
    skipped: "list[str]" = []
    for path in files:
        result = scan_file(path)
        rel = _relative(path)
        if result["skipped"]:
            skipped.append("%s: %s" % (rel, result["skipped"]))
            continue
        if result["findings"]:
            by_file[rel] = result["findings"]
        if result["undetermined"]:
            undetermined[rel] = result["undetermined"]

    total = sum(len(rows) for rows in by_file.values())

    if args.json:
        print(json.dumps({"scanned": len(files), "dirs": dirs, "total": total,
                          "findings": by_file, "undetermined": undetermined,
                          "skipped": skipped}, indent=2))
        return 1 if (args.check and total) else 0

    print("encoding audit -- %s" % ", ".join(dirs))
    print("  scanned:  %d file(s)" % len(files))
    print("  missing:  %d text-decoding call(s) without encoding= in %d file(s)"
          % (total, len(by_file)))

    if by_file:
        print()
        print("  MISSING encoding= -- these decode with the OS codec, so non-ASCII")
        print("  output raises in the reader thread and leaves stdout EMPTY:")
        for rel, rows in sorted(by_file.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            print("    %5d  %s" % (len(rows), rel))
            for row in rows:
                print("          line %-6s %s%s"
                      % (row["line"], row["call"],
                         ("  (%s)" % row["note"]) if row["note"] else ""))

    if undetermined:
        print()
        print("  UNDETERMINED -- NOT counted above; the kwargs are not statically")
        print("  knowable, so these were neither cleared nor reported as findings:")
        for rel, rows in sorted(undetermined.items()):
            for row in rows:
                print("    %s:%s  %s  (%s)"
                      % (rel, row["line"], row["call"], row["note"]))

    if skipped:
        print()
        print("  SKIPPED -- could not be parsed, so nothing was checked in them:")
        for line in skipped:
            print("    %s" % line)

    if args.check:
        if total:
            print()
            print("FAIL: %d site(s) in %d file(s) decode without an explicit "
                  "encoding. Add encoding=\"utf-8\", errors=\"replace\"."
                  % (total, len(by_file)))
            return 1
        print()
        print("OK: every text-decoding subprocess call names its encoding.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
