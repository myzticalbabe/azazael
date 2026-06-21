# coding: utf-8
"""
TERENCE - Error Resolution Protocol
Auto-fixes common Python errors with pattern matching and fixes.

Usage:
    >>> from TERENCE import TERENCE
    >>> t = TERENCE()
    >>> t.VERSION
    '1.0.0'
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
# from typing import Dict, List, Optional  # removed — all names have native equivalents
from dataclasses import dataclass
from collections import defaultdict
import argparse

__all__ = ["TERENCE", "Fix", "FixStats"]


@dataclass
class Fix:
    """Single fix for an error."""

    file: str
    line: int
    error_type: str
    original: str
    fixed: str
    description: str


@dataclass
class FixStats:
    """Fix statistics."""

    files_scanned: int = 0
    errors_found: int = 0
    fixes_applied: int = 0
    fixes_previewed: int = 0
    errors_remaining: int = 0
    duration_ms: float = 0.0


class TERENCE:
    """Error Resolution Protocol."""

    VERSION = "1.0.0"

    def __init__(self):
        self.fixes: list[Fix] = []
        self.stats = FixStats()

    # === ERROR PATTERNS AND FIXES ===

    FIXES = [
        # Bare except -> Specific exception
        {
            "pattern": r"except\s*:",
            "fix": "except Exception as e:",
            "desc": "Replace bare except with Exception handling",
        },
        # print(x) -> logging
        {
            "pattern": r"print\s*\(\s*(?![\"'])",
            "match": "Pattern matching - Python 3.10+ 'print('",
            "fix": "# print(  # Debug",
            "desc": "Comment out print statement",
        },
        # Tab indentation -> Spaces
        {
            "pattern": r"^\t+",
            "match": "Pattern matching - Python 3.10+ tab",
            "fix": "    ",
            "desc": "Replace tabs with 4 spaces",
        },
        # Return outside function -> Pass statement
        {
            "pattern": r"^\s+return\s+(?![^,\s])",
            "match": "Pattern matching - Python 3.10+ return",
            "fix": "# return  # TODO: Move to function",
            "desc": "Comment out return outside function",
        },
        # Continue/break outside loop
        {
            "pattern": r"^\s+(continue|break)\s*$",
            "match": "Pattern matching - Python 3.10+ continue/break",
            "fix": "# TODO: Move to loop",
            "desc": "Comment out continue/break outside loop",
        },
        # Empty try block
        {
            "pattern": r"try\s*:\s*\n\s*(?:pass|\n|$)",
            "match": "Pattern matching - Python 3.10+ try: pass",
            "fix": "try:\n    # TODO: Add exception handling\nexcept Exception as e:\n    pass",
            "desc": "Add exception handling to empty try",
        },
        # assert without message
        {
            "pattern": r"assert\s+(?![^\(]*,)",
            "match": "Pattern matching - Python 3.10+ assert x",
            "fix": "assert ",
            "desc": "Add message to assert",
        },
        # isinstance with single type
        {
            "pattern": r"isinstance\s*\(\s*\w+\s*,\s*\w+\s*\)",
            "match": "isinstance(x, str)",
            "fix": "isinstance(x, (str,))",
            "desc": "Use tuple for isinstance",
        },
        # None comparison
        {
            "pattern": r"==\s*None|!=\s*None",
            "match": "== None",
            "fix": "is None",
            "desc": "Use 'is None' instead of '== None'",
        },
        # eval() usage
        {
            "pattern": r"eval\s*\(",
            "match": "eval(",
            "fix": "# eval(  # Security risk",
            "desc": "Comment out eval()",
        },
        # exec() usage
        {
            "pattern": r"exec\s*\(",
            "match": "exec(",
            "fix": "# exec(  # Security risk",
            "desc": "Comment out exec()",
        },
        # __import__() usage
        {
            "pattern": r"__import__\s*\(",
            "match": "__import__(",
            "fix": "# __import__(  # Use importlib",
            "desc": "Replace __import__ with importlib",
        },
        # Wildcard import
        {
            "pattern": r"import\s+\*\s*$",
            "match": "import *",
            "fix": "# import specific modules  # Avoid wildcard",
            "desc": "Replace wildcard import",
        },
        # from x import *
        {
            "pattern": r"from\s+\w+\s+import\s+\*",
            "match": "from x import *",
            "fix": "# from x import specific  # Avoid wildcard",
            "desc": "Replace wildcard from import",
        },
        # Open without context manager
        {
            "pattern": r"open\s*\(\s*[^,\)]+\s*\)",
            "match": "open(file)",
            "fix": "with open(file) as f:",
            "desc": "Use context manager for open()",
        },
        # .get() without default
        {
            "pattern": r"\.get\s*\(\s*\)",
            "match": ".get()",
            "fix": ".get(key, default)",
            "desc": "Add default to dict.get()",
        },
        # list() on dict.keys()
        {
            "pattern": r"list\s*\(\s*\.keys\s*\(\s*\)\s*\)",
            "match": "list(d.keys())",
            "fix": "list(d.keys())  # Or use list(d)",
            "desc": "Simplify list(d.keys())",
        },
        # str(list) instead of ', '.join()
        {
            "pattern": r"str\s*\(\s*\w+\.keys\s*\(\s*\)\s*\)",
            "match": "str(d.keys())",
            "fix": "', '.join(d.keys())",
            "desc": "Use join for string conversion",
        },
        # Using + for string concatenation
        {
            "pattern": r"\"[^\"]*\"\s*\+\s*\"[^\"]*\"",
            "match": "concat example",
            "fix": "use concatenation",
            "desc": "Consider string formatting",
        },
        # for i in range(len(x))
        {
            "pattern": r"for\s+\w+\s+in\s+range\s*\(\s*len\s*\(\s*\w+\s*\)\s*\)\s*:",
            "match": "for i in range(len(x))",
            "fix": "for i, item in enumerate(x):",
            "desc": "Use enumerate() instead of range(len())",
        },
        # x[0] == y instead of x[0] is y for None check
        {
            "pattern": r"==\s*True|==\s*False",
            "match": "== True",
            "fix": "is True",
            "desc": "Use 'is' for boolean comparison",
        },
        # Using mutable default arguments
        {
            "pattern": r"def\s+\w+\s*\([^)]*=\s*\[\s*\]",
            "match": "def f(x=[])",
            "fix": "def f(x=None):\n    if x is None:\n        x = []",
            "desc": "Replace mutable default argument",
        },
        # Shadowing builtins
        {
            "pattern": r"^(?!def\s)\s*(list|dict|str|int|float|bool|set|sum|min|max)\s*=",
            "match": "list = ",
            "fix": "# list =  # Shadowing builtin",
            "desc": "Don't shadow builtins",
        },
        # Magic numbers
        {
            "pattern": r"(?<![.\w])(\d{3,})(?![.\w])",
            "match": "1000",
            "fix": "# 1000  # TODO: Replace magic number",
            "desc": "Replace magic numbers with constants",
        },
        # Long lines
        {
            "pattern": r".{121,}",
            "match": "Long line",
            "fix": "# Line too long - split",
            "desc": "Split long lines (>120 chars)",
        },
        # Deprecated assert_ equals
        {
            "pattern": r"assertEquals|assert_",
            "match": "assertEquals",
            "fix": "assertEqual",
            "desc": "Use modern unittest methods",
        },
    ]

    # === MAIN FUNCTIONS ===

    def scan(self) -> FixStats:
        """Scan files for errors that can be fixed."""
        print("=" * 70)
        print("  TERENCE - Error Resolution Protocol")
        print("=" * 70)
        print(f"Start: {datetime.now().isoformat()}")
        print()

        start = time.time()
        self.fixes = []
        files_scanned = 0

        # Determine root from env var or auto-detect
        root = os.environ.get("AZAZAEL_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        target_folders = [
            os.path.join(root, "ORCHESTRATION"),
            os.path.join(root, "src"),
            os.path.join(root, "UTILITIES"),
            os.path.join(root, "META"),
            os.path.join(root, "CORE"),
        ]

        for folder in target_folders:
            p = Path(folder)
            if not p.exists():
                continue

            folder_name = p.name
            file_count = 0
            fix_count = 0

            for f in p.rglob("*.py"):
                if any(s in str(f) for s in ["__pycache__", ".git", ".venv"]):
                    continue

                file_count += 1
                fixes = self._scan_file(f)
                fix_count += len(fixes)
                self.fixes.extend(fixes)

            if fix_count > 0:
                print(f"{folder_name}: {file_count} files, {fix_count} potential fixes")

        self.stats.files_scanned = files_scanned
        self.stats.errors_found = len(self.fixes)
        self.stats.duration_ms = (time.time() - start) * 1000

        self._print_summary()

        return self.stats

    def _scan_file(self, file_path: Path) -> list[Fix]:
        """Scan a single file for fixable errors."""
        fixes = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for fix_rule in self.FIXES:
                    if re.search(fix_rule["pattern"], line):
                        fixes.append(
                            Fix(
                                file=str(file_path),
                                line=line_num,
                                error_type=fix_rule["desc"],
                                original=line.strip()[:50],
                                fixed=fix_rule["fix"],
                                description=fix_rule["desc"],
                            )
                        )
        except Exception:
            pass

        return fixes

    def _print_summary(self):
        """Print scan summary."""
        print()
        print("=" * 70)
        print("  SCAN SUMMARY")
        print("=" * 70)
        print()
        print(f"Errors Found:    {self.stats.errors_found}")
        print(f"Duration:        {self.stats.duration_ms:.0f}ms")
        print()

        if self.fixes:
            # Group by error type
            by_type = defaultdict(int)
            for fix in self.fixes:
                by_type[fix.error_type] += 1

            print("Top Fixable Issues:")
            for error_type, count in sorted(
                by_type.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                print(f"  {error_type}: {count}")

            print()
            print("Preview fixes with: terence.preview()")
            print("Apply fixes with: terence.fix_all()")

        print()
        print("=" * 70)

    def preview(self, file_filter: (str | None) = None) -> int:
        """Preview fixes without applying."""
        print()
        print("=" * 70)
        print("  FIX PREVIEW")
        print("=" * 70)
        print()

        count = 0
        for fix in self.fixes:
            if file_filter and file_filter not in fix.file:
                continue

            count += 1
            print(f"File: {fix.file}")
            print(f"Line: {fix.line}")
            print(f"Type: {fix.error_type}")
            print(f"Original: {fix.original}")
            print(f"Fixed:    {fix.fixed}")
            print("-" * 50)

        self.stats.fixes_previewed = count
        print()
        print(f"Total fixes previewed: {count}")
        print("=" * 70)

        return count

    def fix_all(self, apply: bool = False) -> int:
        """Apply all fixes (or just count if apply=False)."""
        print()
        print("=" * 70)
        print("  APPLYING FIXES" if apply else "  WOULD APPLY FIXES")
        print("=" * 70)
        print()

        applied = 0
        skipped = 0

        for fix in self.fixes:
            if apply:
                try:
                    lines = []
                    with open(fix.file, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                    if fix.line <= len(lines):
                        lines[fix.line - 1]
                        # Simple line replacement
                        lines[fix.line - 1] = lines[fix.line - 1].replace(
                            fix.original, fix.fixed, 1
                        )

                        with open(fix.file, "w", encoding="utf-8") as f:
                            f.writelines(lines)

                        applied += 1
                        print(f"[APPLIED] {fix.file}:{fix.line} - {fix.error_type}")
                    else:
                        skipped += 1
                except Exception as e:
                    skipped += 1
                    print(f"[SKIPPED] {fix.file}:{fix.line} - {str(e)[:50]}")
            else:
                print(f"[WOULD FIX] {fix.file}:{fix.line} - {fix.error_type}")
                applied += 1

        self.stats.fixes_applied = applied

        print()
        if apply:
            print(f"Fixes Applied: {applied}")
            print(f"Fixes Skipped: {skipped}")
        else:
            print(f"Total fixes that would be applied: {applied}")
            print("Use fix_all(apply=True) to actually apply")

        print("=" * 70)

        return applied

    def status(self) -> dict:
        """Show current status."""
        return {
            "version": self.VERSION,
            "errors_found": self.stats.errors_found,
            "fixes_applied": self.stats.fixes_applied,
            "fixes_previewed": self.stats.fixes_previewed,
            "duration_ms": self.stats.duration_ms,
        }

    def fix_syntax_error(self, file_path: str, line_num: int, error_msg: str) -> bool:
        """Fix a specific syntax error."""
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            # Common syntax fixes
            if "was never closed" in error_msg:
                # Missing closing bracket
                if "(" in error_msg:
                    lines.append(")\n")
                elif "[" in error_msg:
                    lines.append("]\n")
                elif "{" in error_msg:
                    lines.append("}\n")

            with open(file_path, "w") as f:
                f.writelines(lines)

            return True
        except Exception:
            return False

    def run_quick_fix(self):
        """Run quick auto-fix on common errors."""
        print("=" * 70)
        print("  TERENCE Quick Fix")
        print("=" * 70)
        print()

        # Scan the local project for quick fixes
        root = os.environ.get("AZAZAEL_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        checked = 0
        for py_file in Path(root).rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                issues = []
                if "open(" in content and "with open" not in content:
                    issues.append("open() without context manager")
                if "except:" in content and "except Exception" not in content:
                    issues.append("bare except clause")
                if issues:
                    print(f"  {py_file.name}: {', '.join(issues)}")
                    checked += 1
            except Exception:
                pass

        print()
        print(f"Quick check: {checked} files with potential issues")
        print("Run 'terence.scan()' for full analysis")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="TERENCE - Error Resolution Protocol")
    parser.add_argument("--scan", action="store_true", help="Scan for errors")
    parser.add_argument("--preview", action="store_true", help="Preview fixes")
    parser.add_argument("--fix", action="store_true", help="Apply fixes")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--quick", action="store_true", help="Quick fix check")

    args = parser.parse_args()

    terence = TERENCE()

    if args.scan:
        terence.scan()
    elif args.preview:
        terence.scan()
        terence.preview()
    elif args.fix:
        terence.scan()
        terence.fix_all(apply=True)
    elif args.status:
        print(json.dumps(terence.status(), indent=2))
    elif args.quick:
        terence.run_quick_fix()
    else:
        print("TERENCE - Error Resolution Protocol")
        print()
        print("Usage:")
        print("  python TERENCE.py --scan    Scan for errors")
        print("  python TERENCE.py --preview Preview fixes")
        print("  python TERENCE.py --fix     Apply fixes")
        print("  python TERENCE.py --status  Show status")
        print("  python TERENCE.py --quick   Quick fix check")
        print()
        print("Python API:")
        print("  >>> import terence")
        print("  >>> terence.scan()")
        print("  >>> terence.fix_all(apply=True)")


if __name__ == "__main__":
    main()
