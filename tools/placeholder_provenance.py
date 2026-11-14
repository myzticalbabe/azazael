#!/usr/bin/env python3
# coding: utf-8
"""external_placeholders.json — what the store's import stubs actually were.

Why this exists (2026-11-14)
----------------------------
`build.py:96 _mint_external_stub` gives every import edge whose target has no
node a leaf placeholder (`external: true, source_file: ""`), so no endpoint
dangles. `ids.py:86 normalize_id` then casefolds and collapses every non-word
run to `_`, which is lossy: `concurrent.futures` and `Concurrent_Futures` both
become `concurrent_futures`, `PIL` becomes `pil`, and a Rust `HashMap` becomes
`hashmap`. After a rebuild nothing in the store can say whether `pil` was an
uninstalled third-party package or a stdlib module spelled oddly, so the
placeholder population cannot be audited.

This records that answer *beside* the store, derived from the importing
statements themselves (each edge carries `source_file` and `source_location`),
and never edits the store. It is a reading instrument, not a gate: the scope
guard decides whether a write may happen, this describes what was written.

Usage
-----
    python tools/placeholder_provenance.py                 # repo root inferred
    python tools/placeholder_provenance.py --repo-root .
    python tools/placeholder_provenance.py --print         # also dump the split

Exit 0 when a report was written. Exit 3 when no store exists — absence is not
an empty answer, so it is announced rather than written as `0 items`.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXIT_OK = 0
EXIT_NO_STORE = 3

PLACEHOLDER_REPORT = "external_placeholders.json"

_SCAN_SUFFIXES = {
    ".py": "python", ".pyi": "python",
    ".rs": "rust",
    ".c": "c", ".h": "c", ".cc": "c", ".cpp": "c", ".hpp": "c",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "javascript", ".tsx": "javascript", ".jsx": "javascript",
}

_SKIP_DIRS = {"graphify-out", "__pycache__", "node_modules", ".git", "build"}


def _norm_module(name: str) -> str:
    """``normalize_id``'s rule, so a module string can be matched to an id."""
    return re.sub(r"[^0-9A-Za-z]+", "_", name).strip("_").lower()


def _scan_imports(
    text: str, suffix: str, skipped: Counter[str], where: str = ""
) -> dict[str, str]:
    """``normalised token -> the module string it was written as``.

    A file that will not parse is *recorded* in ``skipped`` rather than
    silently yielding no match, so an audit can tell "this importer had no
    matching import" apart from "this importer was never read".
    """
    found: dict[str, str] = {}

    def add(raw: str) -> None:
        raw = raw.strip().strip("'\"")
        if not raw:
            return
        keys = {_norm_module(raw)}
        segs = [s for s in re.split(r"[.:/\\]+", raw) if s and s != "*"]
        if segs:
            keys.add(_norm_module(segs[0]))
            keys.add(_norm_module(segs[-1]))
        for key in keys:
            if key:
                found.setdefault(key, raw)

    try:
        if suffix in (".py", ".pyi"):
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        add(alias.name)
                elif (isinstance(node, ast.ImportFrom) and node.level == 0
                      and node.module):
                    add(node.module)
        elif suffix == ".rs":
            for m in re.finditer(
                    r"^\s*(?:pub(?:\([^)]*\))?\s+)?use\s+([A-Za-z_][\w:]*)",
                    text, re.MULTILINE):
                add(m.group(1).rstrip(":"))
        elif suffix in (".c", ".h", ".cc", ".cpp", ".hpp"):
            for m in re.finditer(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]',
                                 text, re.MULTILINE):
                base = m.group(1).rsplit("/", 1)[-1].rsplit(".", 1)[0]
                add(base)
        else:
            for m in re.finditer(r"(?:require\(\s*['\"]|from\s+['\"])([^'\"]+)['\"]",
                                 text):
                raw = m.group(1)
                base = raw.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                add(base if raw.startswith(".") else raw)
                add("ref_" + _norm_module(base))
    except (SyntaxError, ValueError, RecursionError) as exc:
        # An unparseable importer proves nothing -- but the skip is counted,
        # because "no match" and "never read" are different answers.
        skipped["unparseable_importer"] += 1
        print(f"placeholder provenance: skipped {where or '<text>'}: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
    return found


def _in_tree_names(*roots: Path) -> set[str]:
    """Module and package names that exist in the repo right now.

    ``src`` alone is not enough: the Aether auditors (``reading_audit``,
    ``leg_ledger``) are imported by bare name from ``src/eve_unleashed/well.py``
    but live in ``tools/``, so a src-only scan called two in-tree modules
    third-party (measured 2026-11-14).
    """
    names: set[str] = set()
    for root in roots:
        for _dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for d in dirnames:
                names.add(d.lower())
            for f in filenames:
                if f.endswith((".py", ".pyi")):
                    names.add(f.rsplit(".", 1)[0].lower())
    return names


def _source_path(repo_root: Path, rel: str) -> Path | None:
    """Resolve an edge's ``source_file``, which is relative to the watch path."""
    if not rel:
        return None
    for base in (repo_root / "src", repo_root):
        cand = (base / rel)
        if cand.is_file():
            return cand
    return None


def record_placeholders(repo_root: Path) -> tuple[Path | None, dict[str, object]]:
    """Write ``external_placeholders.json`` beside the canonical store."""
    store = repo_root / "src" / "graphify-out"
    graph = store / "graph.json"
    if not graph.is_file():
        return None, {}
    try:
        data = json.loads(graph.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"placeholder provenance: cannot read {graph}: {exc}",
              file=sys.stderr)
        return None, {}

    external = {n.get("id") for n in (data.get("nodes") or [])
                if n.get("external")}
    importers: dict[str, set[str]] = {}
    suffixes: dict[str, set[str]] = {}
    for edge in (data.get("links") or []):
        target = edge.get("target")
        if target not in external:
            continue
        rel = edge.get("source_file") or ""
        if rel:
            importers.setdefault(target, set()).add(rel)
            suffixes.setdefault(target, set()).add(Path(rel).suffix.lower())

    scans: dict[str, dict[str, str]] = {}
    skipped: Counter[str] = Counter()
    for rel in {r for rels in importers.values() for r in rels}:
        path = _source_path(repo_root, rel)
        if path is None or path.suffix.lower() not in _SCAN_SUFFIXES:
            skipped["unresolved_or_unsupported_importer"] += 1
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            # No evidence is not the same as no import: count the gap.
            skipped["unreadable_importer"] += 1
            print(f"placeholder provenance: cannot read importer {rel}: {exc}",
                  file=sys.stderr)
            continue
        scans[rel] = _scan_imports(text, path.suffix.lower(), skipped, rel)

    in_tree = _in_tree_names(repo_root / "src", repo_root / "tools")
    stdlib = set(sys.stdlib_module_names)
    origin_counts: Counter[str] = Counter()
    language_counts: Counter[str] = Counter()
    items: list[dict[str, object]] = []
    for pid in sorted(p for p in external if p):
        real = None
        for rel in importers.get(pid, ()):
            if pid in scans.get(rel, {}):
                real = scans[rel][pid]
                break
        langs = {_SCAN_SUFFIXES.get(s, "unknown") for s in suffixes.get(pid, ())}
        language = langs.pop() if len(langs) == 1 else ("mixed" if langs else "unknown")
        head = _norm_module((real or pid).split(".")[0])
        if language not in ("python", "unknown"):
            origin = "non_python"
        elif head in stdlib or pid in stdlib:
            origin = "stdlib"
        elif pid in in_tree or head in in_tree:
            origin = "in_tree"
        else:
            origin = "third_party"
        origin_counts[origin] += 1
        language_counts[language] += 1
        items.append({
            "id": pid,
            "module": real,
            "language": language,
            "origin": origin,
            "importers": len(importers.get(pid, ())),
            "matched": real is not None,
        })

    payload: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "store": str(graph),
        "store_built_at_commit": data.get("built_at_commit"),
        "placeholders": len(items),
        "by_origin": dict(sorted(origin_counts.items())),
        "by_language": dict(sorted(language_counts.items())),
        "skipped_importers": dict(sorted(skipped.items())),
        "items": items,
    }
    report = store / PLACEHOLDER_REPORT
    tmp = report.with_suffix(report.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, report)
    return report, payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=None,
                        help="repository root (default: this file's parents[1])")
    parser.add_argument("--print", dest="dump", action="store_true",
                        help="print the origin/language split after writing")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else \
        Path(__file__).resolve().parents[1]
    try:
        repo_root = repo_root.resolve()
    except OSError as exc:
        print(f"placeholder provenance: cannot resolve repo root: {exc}",
              file=sys.stderr)
        return EXIT_NO_STORE

    written, payload = record_placeholders(repo_root)
    if written is None:
        print(
            f"placeholder provenance: no store at "
            f"{repo_root / 'src' / 'graphify-out'} -- nothing recorded "
            f"(absence is not an empty answer).",
            file=sys.stderr,
        )
        return EXIT_NO_STORE

    print(f"placeholder provenance: recorded {payload['placeholders']} "
          f"external placeholder(s) -> {written}")
    if args.dump:
        print(f"  by_origin  : {payload['by_origin']}")
        print(f"  by_language: {payload['by_language']}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
