# coding: utf-8
"""
CLUSTER INSPECTOR - Multi-File Type Analysis System
Morphing worm cluster for checking .txt, .md, .ps1, .html files
Validates pathways, environmental variables, and installations
"""

import os
import sys
import re
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class InspectionResult:
    file_type: str
    file_path: str
    issues: List[Dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    valid: bool = True


class PathwayValidator:
    """Validates file paths and directories."""

    def __init__(self):
        self.valid_paths: Set[str] = set()
        self.invalid_paths: List[Dict] = []

    def check_path_exists(self, path: str, context: str = "") -> Optional[Dict]:
        if os.path.exists(path):
            return None
        return {
            "type": "MISSING_PATH",
            "path": path,
            "context": context,
            "severity": "HIGH",
        }

    def check_drive_exists(self, path: str) -> Optional[Dict]:
        if path.startswith("C:") and not os.path.exists("C:"):
            return {"type": "MISSING_DRIVE", "path": path, "severity": "CRITICAL"}
        return None

    def validate_windows_path(self, path: str, context: str = "") -> List[Dict]:
        issues = []
        if not path:
            return issues
        issues.append(self.check_drive_exists(path))
        issues.append(self.check_path_exists(path, context))
        return [i for i in issues if i]

    def extract_and_validate_paths(self, text: str) -> List[Dict]:
        issues = []
        path_patterns = [
            r'[A-Za-z]:\\[^\s<>"|?*]+',
            r"%[A-Z_]+%",
            r"\$[A-Za-z_]+",
        ]
        for pattern in path_patterns:
            for match in re.finditer(pattern, text):
                path = match.group()
                if path.startswith("%"):
                    env_var = path.strip("%")
                    if env_var not in os.environ:
                        issues.append(
                            {
                                "type": "MISSING_ENV_VAR",
                                "var": path,
                                "severity": "MEDIUM",
                            }
                        )
        return issues


class EnvironmentalVariableInspector:
    """Inspects and validates environmental variables."""

    def __init__(self):
        self.required_vars = {
            "PATH": "System PATH variable",
            "PYTHONPATH": "Python path",
            "HOMEPATH": "User home directory",
            "USERPROFILE": "User profile directory",
        }
        self.important_paths = [
            "C:\\Python314",
            "C:\\Users\\clint\\Desktop\\Azazael_UNIFIED",
        ]

    def check_required_vars(self) -> List[Dict]:
        issues = []
        for var, desc in self.required_vars.items():
            if var not in os.environ:
                issues.append(
                    {
                        "type": "MISSING_ENV_VAR",
                        "var": var,
                        "description": desc,
                        "severity": "HIGH",
                    }
                )
        return issues

    def check_path_directories(self) -> List[Dict]:
        issues = []
        path_var = os.environ.get("PATH", "")
        for expected in self.important_paths:
            if expected not in path_var:
                issues.append(
                    {
                        "type": "PATH_MISSING_DIR",
                        "directory": expected,
                        "severity": "LOW",
                    }
                )
        return issues

    def validate_python_installation(self) -> List[Dict]:
        issues = []
        python_paths = [
            "C:\\Python314\\python.exe",
            "C:\\Python313\\python.exe",
            "C:\\Python312\\python.exe",
        ]
        for pypath in python_paths:
            if os.path.exists(pypath):
                try:
                    result = subprocess.run(
                        [pypath, "--version"], capture_output=True, text=True, timeout=5
                    )
                    if result.returncode != 0:
                        issues.append(
                            {
                                "type": "PYTHON_VERSION_FAIL",
                                "path": pypath,
                                "severity": "MEDIUM",
                            }
                        )
                except Exception as e:
                    issues.append(
                        {
                            "type": "PYTHON_EXEC_FAIL",
                            "path": pypath,
                            "error": str(e),
                            "severity": "MEDIUM",
                        }
                    )
        return issues

    def run_inspection(self) -> Dict[str, Any]:
        results = {
            "timestamp": datetime.now().isoformat(),
            "env_vars": {},
            "issues": [],
            "warnings": [],
        }

        for var in list(os.environ.keys()):
            if "PATH" in var or "PYTHON" in var:
                results["env_vars"][var] = (
                    os.environ[var][:100] + "..."
                    if len(os.environ[var]) > 100
                    else os.environ[var]
                )

        results["issues"].extend(self.check_required_vars())
        results["issues"].extend(self.check_path_directories())
        results["issues"].extend(self.validate_python_installation())

        return results


class TextFileInspector:
    """Inspects .txt files for wrong information."""

    def __init__(self):
        self.path_validator = PathwayValidator()

    def inspect(self, file_path: Path) -> InspectionResult:
        result = InspectionResult(file_type=".txt", file_path=str(file_path))

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            result.issues.extend(
                self.path_validator.extract_and_validate_paths(content)
            )

        except Exception as e:
            result.issues.append(
                {"type": "READ_ERROR", "error": str(e), "severity": "LOW"}
            )
            result.valid = False

        return result


class MarkdownFileInspector:
    """Inspects .md files for wrong information."""

    def __init__(self):
        self.path_validator = PathwayValidator()

    def inspect(self, file_path: Path) -> InspectionResult:
        result = InspectionResult(file_type=".md", file_path=str(file_path))

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            result.issues.extend(
                self.path_validator.extract_and_validate_paths(content)
            )

            if file_path.name.lower() in ["readme.md", "readme.txt"]:
                if (
                    "azazael" in content.lower()
                    and "installation" not in content.lower()
                ):
                    result.warnings.append(
                        "Readme may be missing installation instructions"
                    )

        except Exception as e:
            result.issues.append(
                {"type": "READ_ERROR", "error": str(e), "severity": "LOW"}
            )
            result.valid = False

        return result


class PowerShellInspector:
    """Inspects .ps1 files for wrong pathways and issues."""

    def __init__(self):
        self.path_validator = PathwayValidator()

    def inspect(self, file_path: Path) -> InspectionResult:
        result = InspectionResult(file_type=".ps1", file_path=str(file_path))

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            path_patterns = [
                r"[A-Za-z]:\\[^\s]+",
                r"\\$Env:[A-Za-z_]+",
                r"\\$[A-Za-z_]+(?:\\[A-Za-z_]+)*",
            ]

            for pattern in path_patterns:
                for match in re.finditer(pattern, content):
                    path = match.group()
                    if not path.startswith("$"):
                        result.issues.extend(
                            self.path_validator.validate_windows_path(path)
                        )

            if "C:\\Python313" in content or "C:\\Python312" in content:
                if not os.path.exists("C:\\Python313") and not os.path.exists(
                    "C:\\Python312"
                ):
                    result.issues.append(
                        {"type": "REFERENCED_MISSING_PYTHON", "severity": "MEDIUM"}
                    )

        except Exception as e:
            result.issues.append(
                {"type": "READ_ERROR", "error": str(e), "severity": "LOW"}
            )
            result.valid = False

        return result


class HTMLInspector:
    """Inspects .html files for wrong information."""

    def __init__(self):
        self.path_validator = PathwayValidator()

    def inspect(self, file_path: Path) -> InspectionResult:
        result = InspectionResult(file_type=".html", file_path=str(file_path))

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            src_pattern = r'src=["\']([^"\']+)["\']'
            href_pattern = r'href=["\']([^"\']+)["\']'

            for pattern in [src_pattern, href_pattern]:
                for match in re.finditer(pattern, content):
                    ref = match.group(1)
                    if ref.startswith("http"):
                        continue
                    result.issues.extend(
                        self.path_validator.validate_windows_path(ref, "HTML reference")
                    )

        except Exception as e:
            result.issues.append(
                {"type": "READ_ERROR", "error": str(e), "severity": "LOW"}
            )
            result.valid = False

        return result


class ClusterInspector:
    """Main cluster that orchestrates all inspectors."""

    VERSION = "1.0.0"

    def __init__(self, root: str = None):
        self.root = Path(root or "C:/Users/clint/Desktop/Azazael_UNIFIED")
        self.inspectors = {
            ".txt": TextFileInspector(),
            ".md": MarkdownFileInspector(),
            ".ps1": PowerShellInspector(),
            ".html": HTMLInspector(),
        }
        self.env_inspector = EnvironmentalVariableInspector()
        self.stats = {
            "files_scanned": 0,
            "issues_found": 0,
            "warnings_found": 0,
            "valid_files": 0,
        }

    def find_files_by_type(self, extensions: List[str]) -> List[Path]:
        files = []
        for ext in extensions:
            files.extend(self.root.rglob(f"*{ext}"))
        return list(set(files))

    def run_env_inspection(self) -> Dict[str, Any]:
        print("=" * 70)
        print("ENVIRONMENTAL VARIABLE INSPECTION")
        print("=" * 70)
        print()

        results = self.env_inspector.run_inspection()

        print(f"Timestamp: {results['timestamp']}")
        print()
        print("Checked Environmental Variables:")
        for var, val in results["env_vars"].items():
            print(f"  {var}: {val}")
        print()

        if results["issues"]:
            print("ISSUES FOUND:")
            for issue in results["issues"]:
                print(
                    f"  [{issue['severity']}] {issue['type']}: {issue.get('var', issue.get('directory', issue.get('path', 'N/A')))}"
                )
        else:
            print("[✓] No environmental issues found")

        print()
        return results

    def run_file_inspection(
        self, extensions: List[str] = None
    ) -> List[InspectionResult]:
        extensions = extensions or [".txt", ".md", ".ps1", ".html"]

        print("=" * 70)
        print("FILE CLUSTER INSPECTION")
        print("=" * 70)
        print()

        files = self.find_files_by_type(extensions)
        print(f"[+] Found {len(files)} files to inspect")
        print()

        results: List[InspectionResult] = []

        for i, fp in enumerate(files):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(files)}")

            ext = fp.suffix.lower()
            if ext in self.inspectors:
                result = self.inspectors[ext].inspect(fp)
                results.append(result)
                self.stats["files_scanned"] += 1
                self.stats["issues_found"] += len(result.issues)
                self.stats["warnings_found"] += len(result.warnings)
                if result.valid and not result.issues:
                    self.stats["valid_files"] += 1

        print(f"  Final: {len(files)}/{len(files)}")
        print()

        return results

    def generate_report(
        self, file_results: List[InspectionResult], env_results: Dict
    ) -> Dict:
        report = {
            "timestamp": datetime.now().isoformat(),
            "root": str(self.root),
            "file_results": {
                "total_scanned": self.stats["files_scanned"],
                "issues": self.stats["issues_found"],
                "warnings": self.stats["warnings_found"],
                "valid": self.stats["valid_files"],
            },
            "env_results": {
                "issues": len(env_results.get("issues", [])),
            },
            "details": {"critical": [], "high": [], "medium": [], "low": []},
        }

        for result in file_results:
            for issue in result.issues:
                severity = issue.get("severity", "LOW")
                report["details"][severity].append(
                    {
                        "file": result.file_path,
                        "type": issue["type"],
                        "path": issue.get("path", issue.get("var", "N/A")),
                    }
                )

        return report

    def print_summary(self, file_results: List[InspectionResult], env_results: Dict):
        print("=" * 70)
        print("CLUSTER INSPECTION SUMMARY")
        print("=" * 70)
        print()

        print(f"Files scanned: {self.stats['files_scanned']}")
        print(f"Issues found: {self.stats['issues_found']}")
        print(f"Warnings: {self.stats['warnings_found']}")
        print(f"Valid files: {self.stats['valid_files']}")
        print()
        print(f"Environmental issues: {len(env_results.get('issues', []))}")
        print()

        critical = [
            r
            for r in file_results
            if any(i.get("severity") == "CRITICAL" for i in r.issues)
        ]
        if critical:
            print("CRITICAL ISSUES:")
            for r in critical[:5]:
                print(f"  {r.file_path}")
                for i in r.issues:
                    print(f"    [{i['severity']}] {i['type']}: {i.get('path', 'N/A')}")
        else:
            print("[✓] No critical file issues")

        print()
        high = sum(
            1 for r in file_results for i in r.issues if i.get("severity") == "HIGH"
        )
        medium = sum(
            1 for r in file_results for i in r.issues if i.get("severity") == "MEDIUM"
        )

        print(f"High priority issues: {high}")
        print(f"Medium priority issues: {medium}")
        print()

        env_issues = [
            i
            for i in env_results.get("issues", [])
            if i.get("severity") in ["HIGH", "CRITICAL"]
        ]
        if env_issues:
            print("ENVIRONMENTAL ISSUES:")
            for i in env_issues:
                print(
                    f"  [{i['severity']}] {i['type']}: {i.get('var', i.get('directory', 'N/A'))}"
                )
        else:
            print("[✓] No critical environmental issues")

        print()

    def run(self):
        print()
        print("=" * 70)
        print(f"CLUSTER INSPECTOR v{self.VERSION}")
        print(f"Root: {self.root}")
        print("=" * 70)
        print()

        env_results = self.run_env_inspection()
        file_results = self.run_file_inspection([".txt", ".md", ".ps1", ".html"])

        self.print_summary(file_results, env_results)

        report = self.generate_report(file_results, env_results)

        report_file = self.root / "CLUSTER_INSPECTION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved: {report_file}")

        return report


if __name__ == "__main__":
    inspector = ClusterInspector()
    inspector.run()
