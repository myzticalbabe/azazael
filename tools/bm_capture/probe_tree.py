"""BM capture probe: third-party imports used by a source tree.

Walks a repo checkout, AST-parses every .py file, emits the sorted set
of top-level imported module names as JSON. Stdlib names are excluded
via sys.stdlib_module_names when available (3.10+), else a minimal
fallback list. Stdlib only.

Usage: python3 probe_tree.py /path/to/repo > tree_imports.json
"""

import ast
import json
import sys

try:
    STDLIB = set(sys.stdlib_module_names)
except AttributeError:  # Python < 3.10
    STDLIB = {
        "os", "sys", "re", "json", "ast", "io", "shutil", "subprocess",
        "pathlib", "typing", "collections", "itertools", "functools",
        "threading", "multiprocessing", "asyncio", "logging", "argparse",
        "unittest", "http", "urllib", "email", "sqlite3", "datetime",
        "time", "math", "random", "hashlib", "hmac", "secrets", "socket",
        "ssl", "select", "struct", "codecs", "locale", "traceback",
        "warnings", "contextlib", "copy", "pickle", "csv", "configparser",
        "tempfile", "glob", "fnmatch", "gzip", "zipfile", "tarfile",
    }


def top_names(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, UnicodeError, OSError):
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.add(node.module.split(".")[0])
    return out


def main():
    from pathlib import Path

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    found = set()
    for f in root.rglob("*.py"):
        if ".git" in f.parts or "__pycache__" in f.parts:
            continue
        found |= top_names(f)
    print(json.dumps(sorted(n for n in found if n not in STDLIB)))


if __name__ == "__main__":
    main()
