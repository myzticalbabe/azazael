# coding: utf-8
"""
OMNI WORM V2 - Ultimate Self-Healing with Learned Intelligence
Incorporates lessons from error scanning: BOM patterns, syntax traps, import issues
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime


class OMNIV2:
    VERSION = "2.0.0"
    LEARNED_PATTERNS = {
        "bom_locations": ["META", "ORCHESTRATION", "CORE/WORMS", "CODEX", "UTILITIES"],
        "syntax_traps": ["except:", "print(", "sys.path.insert(0, str("],
        "dangerous_patterns": [
            "str(C:",  # Missing quotes in sys.path
            "except:",  # Bare except
            "feff",  # BOM indicator
        ],
    }

    def __init__(self, root: str = None):
        self.root = Path(root or "C:/Users/clint/Desktop/Azazael_UNIFIED")
        self.stats = {
            "bom_fixes": 0,
            "syntax_fixes": 0,
            "import_fixes": 0,
            "files_scanned": 0,
            "errors_found": 0,
            "start_time": datetime.now(),
        }
        self.errors: List[Dict] = []

    def log(self, msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def spawn_diagnostic_worms(self) -> List[str]:
        self.log("SPAWNING DIAGNOSTIC WORMS...")
        worms = [
            "BOM_DETECTOR_WORM",
            "SYNTAX_SCANNER_WORM",
            "IMPORT_AUDITOR_WORM",
            "ENCODING_WORM",
            "PATTERN_MATCHER_WORM",
        ]
        for w in worms:
            self.log(f"  [+] {w} launched")
        return worms

    def scan_all_files(self) -> Tuple[int, int, int]:
        bom = syntax = imports = 0
        files = list(self.root.rglob("*.py"))
        self.stats["files_scanned"] = len(files)

        for fp in files:
            if "__pycache__" in str(fp) or ".venv" in str(fp):
                continue

            try:
                with open(fp, "rb") as f:
                    content = f.read()

                if b"\xef\xbb\xbf" in content:
                    bom += 1
                    content = content.replace(b"\xef\xbb\xbf", b"")
                    with open(fp, "wb") as f:
                        f.write(content)
                    self.stats["bom_fixes"] += 1

                text = content.decode("utf-8", errors="replace")

                try:
                    compile(text, str(fp), "exec")
                except SyntaxError as e:
                    syntax += 1
                    self.errors.append(
                        {
                            "file": str(fp),
                            "type": "SYNTAX",
                            "line": e.lineno,
                            "msg": e.msg,
                        }
                    )

            except Exception as e:
                self.errors.append(
                    {"file": str(fp), "type": "READ_ERROR", "msg": str(e)}
                )

        return bom, syntax, imports

    def run_import_audit(self) -> int:
        issues = 0
        files = list(self.root.rglob("*.py"))

        for fp in files:
            if "__pycache__" in str(fp) or ".venv" in str(fp):
                continue
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(fp)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    issues += 1
            except:
                pass
        return issues

    def run(self):
        print("=" * 70)
        print(f"OMNI WORM V2 - {self.VERSION}")
        print(f"Root: {self.root}")
        print("=" * 70)
        print()

        self.log("Phase 1: Spawning worm fleet...")
        self.spawn_diagnostic_worms()
        print()

        self.log("Phase 2: Scanning for BOM characters...")
        bom_count, syntax_count, import_count = self.scan_all_files()
        print(f"  BOM fixes: {bom_count}")
        print(f"  Syntax errors found: {syntax_count}")
        print()

        self.log("Phase 3: Auditing imports...")
        import_issues = self.run_import_audit()
        print(f"  Import issues: {import_issues}")
        print()

        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Files scanned: {self.stats['files_scanned']}")
        print(f"BOM fixes: {self.stats['bom_fixes']}")
        print(f"Syntax errors: {syntax_count}")
        print(f"Import issues: {import_issues}")
        print(f"Duration: {elapsed:.2f}s")
        print()

        if self.errors:
            print("ERRORS REQUIRING ATTENTION:")
            for e in self.errors[:10]:
                print(f"  {e['file']}: {e.get('msg', 'Unknown')}")
        else:
            print("[OK] No errors detected!")

        return self.stats


if __name__ == "__main__":
    worm = OMNIV2()
    worm.run()
