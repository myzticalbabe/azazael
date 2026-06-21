# coding: utf-8
"""
DIAGNOSTIC_WORM - Self-Healing Diagnostic Crawler
Identifies why Azazael modules are not activating correctly
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "HYDRA" / "ml_platforms"))

import os
import json
import subprocess
import traceback
from datetime import datetime
from typing import Dict, List, Any, Tuple

AZAAZEL_ROOT = Path(__file__).parent
VENV_PYTHON = AZAAZEL_ROOT / ".venv" / "Scripts" / "python.exe"


class DiagnosticWorm:
    def __init__(self):
        self.findings = []
        self.fixes_applied = []
        self.failed_imports = {}
        self.bom_files = []
        self.syntax_issues = []
        self.dead_imports = []

    def scan_all_modules(self) -> Dict[str, Any]:
        print("=" * 60)
        print("DIAGNOSTIC WORM - Self-Healing Analysis")
        print("=" * 60)
        print()

        results = {
            "timestamp": datetime.now().isoformat(),
            "bom_files": [],
            "syntax_issues": [],
            "failed_imports": {},
            "dead_imports": [],
            "circular_deps": [],
        }

        print("[1/5] Scanning for BOM characters...")
        for py_file in AZAAZEL_ROOT.rglob("*.py"):
            try:
                content = py_file.read_bytes()
                if content.startswith(b"\xef\xbb\xbf"):
                    results["bom_files"].append(str(py_file))
                    self.fix_bom(py_file)
            except Exception as e:
                pass

        print(f"      Found: {len(results['bom_files'])} BOM files")
        for f in results["bom_files"][:5]:
            print(f"        - {f.name}")

        print("\n[2/5] Testing module imports...")
        test_imports = [
            ("HYDRA.hydra_launcher", "HYDRA Launcher"),
            ("HYDRA.hydra_protocols", "HYDRA Protocols"),
            ("META.HYDRA_CONTAINER", "HYDRA Container"),
            ("META.HYDRAMETA", "HYDRA Meta"),
            ("CORE.WORMS.WORMZ", "WORMZ"),
            ("CORE.WORMS.SYSTEMZ", "SYSTEMZ"),
            ("CORE.WORMS.CLUSTERWORMS", "CLUSTERWORMS"),
            ("UTILITIES.TERENCE.TERENCE", "TERENCE"),
            ("UTILITIES.TARBABY.TARBABY", "TARBABY"),
        ]

        for module_name, desc in test_imports:
            success, error = self.test_import(module_name)
            results["failed_imports"][module_name] = {
                "description": desc,
                "success": success,
                "error": str(error) if error else None,
            }
            icon = "[OK]" if success else "[FAIL]"
            print(f"      {icon} {desc} ({module_name})")

        print("\n[3/5] Analyzing sys.path imports...")
        bad_syspath_files = self.scan_bad_syspath()
        results["bad_syspath"] = bad_syspath_files
        print(f"      Found: {len(bad_syspath_files)} files with bad sys.path")

        for f in bad_syspath_files[:5]:
            print(f"        - {f.name}")
            self.fix_bad_syspath(f)

        print("\n[4/5] Checking for circular dependencies...")
        results["circular_deps"] = self.check_circular_deps()

        print("\n[5/5] Generating diagnostics report...")
        return results

    def fix_bom(self, file_path: Path):
        try:
            content = file_path.read_bytes()
            if content.startswith(b"\xef\xbb\xbf"):
                content = content[3:]
                file_path.write_bytes(content)
                self.fixes_applied.append(f"BOM removed: {file_path.name}")
        except Exception as e:
            self.findings.append(f"BOM fix failed: {file_path} - {e}")

    def scan_bad_syspath(self) -> List[Path]:
        bad_files = []
        pattern = b"C:\\Users\\clint\\Desktop\\Azazael_UNIFIED"

        for py_file in AZAAZEL_ROOT.rglob("*.py"):
            try:
                content = py_file.read_bytes()
                if pattern in content:
                    bad_files.append(py_file)
            except Exception:
                pass

        return bad_files

    def fix_bad_syspath(self, file_path: Path):
        try:
            content = file_path.read_text(encoding="utf-8-sig")

            if "HYDRA\\ml_platforms" in str(file_path):
                new_pattern = (
                    'sys.path.insert(0, str(Path(__file__).parent / "ml_platforms"))'
                )
            elif "ml_platforms" in str(file_path):
                new_pattern = 'sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))'
            else:
                new_pattern = 'sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))'

            import re

            old_pattern = r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)"

            if re.search(old_pattern, content):
                new_content = re.sub(old_pattern, new_pattern, content)
                file_path.write_text(new_content, encoding="utf-8")
                self.fixes_applied.append(f"sys.path fixed: {file_path.name}")
                return True
            return False
        except Exception as e:
            self.findings.append(f"sys.path fix failed: {file_path} - {e}")
            return False

    def test_import(self, module_name: str) -> Tuple[bool, Exception]:
        try:
            code = f"import {module_name}"
            result = subprocess.run(
                [str(VENV_PYTHON), "-c", code],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(AZAAZEL_ROOT),
            )
            if result.returncode == 0:
                return True, None
            return False, Exception(result.stderr)
        except Exception as e:
            return False, e

    def check_circular_deps(self) -> List[str]:
        deps = []
        try:
            import networkx as nx

            G = nx.DiGraph()

            worm_files = [
                AZAAZEL_ROOT / "CORE" / "WORMS" / "WORMZ.py",
                AZAAZEL_ROOT / "CORE" / "WORMS" / "SYSTEMZ.py",
                AZAAZEL_ROOT / "CORE" / "WORMS" / "CLUSTERWORMS.py",
                AZAAZEL_ROOT / "HYDRA" / "hydra_launcher.py",
                AZAAZEL_ROOT / "META" / "HYDRAMETA.py",
            ]

            for wf in worm_files:
                if wf.exists():
                    content = wf.read_text()
                    for match in re.finditer(r"^import\s+(\w+)", content, re.MULTILINE):
                        G.add_edge(wf.name, match.group(1) + ".py")

            cycles = list(nx.simple_cycles(G))
            for cycle in cycles[:5]:
                deps.append(" -> ".join(cycle))
        except Exception as e:
            deps.append(f"Could not analyze: {e}")

        return deps

    def apply_healing(self, results: Dict):
        print("\n" + "=" * 60)
        print("APPLYING SELF-HEALING")
        print("=" * 60)

        healing_actions = []

        for module, status in results.get("failed_imports", {}).items():
            if not status["success"]:
                action = self.heal_module(module, status.get("error"))
                if action:
                    healing_actions.append(action)

        if healing_actions:
            print("\nHealing actions applied:")
            for action in healing_actions:
                print(f"  - {action}")
        else:
            print("\nNo healing actions needed")

        return healing_actions

    def heal_module(self, module: str, error: Exception) -> str:
        module_path = module.replace(".", "/") + ".py"
        full_path = AZAAZEL_ROOT / module_path

        if not full_path.exists():
            return f"Module not found: {module}"

        if error and "BOM" in str(error):
            self.fix_bom(full_path)
            return f"Fixed BOM in {module}"

        if error and "sys.path" in str(error):
            self.fix_bad_syspath(full_path)
            return f"Fixed sys.path in {module}"

        return None

    def save_report(self, results: Dict):
        report_path = (
            AZAAZEL_ROOT / "CODEX" / "DOCUMENTATION" / "DIAGNOSTIC_REPORT.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": results["timestamp"],
            "summary": {
                "bom_files_found": len(results.get("bom_files", [])),
                "failed_imports": sum(
                    1
                    for k, v in results.get("failed_imports", {}).items()
                    if not v["success"]
                ),
                "bad_syspath_files": len(results.get("bad_syspath", [])),
                "circular_deps": len(results.get("circular_deps", [])),
            },
            "details": results,
            "fixes_applied": self.fixes_applied,
        }

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nReport saved: {report_path}")
        return report_path


def main():
    worm = DiagnosticWorm()
    results = worm.scan_all_modules()
    worm.apply_healing(results)
    worm.save_report(results)

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
