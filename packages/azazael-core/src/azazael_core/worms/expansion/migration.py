# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: MIGRATION (5 worms)
CodeMigrator, DepUpgrader, SchemaVersioner, ImportPathFixWorm, LegacyShimGen
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

# ── Worm Registry Import ─────────────────────────────────────────────
try:
    from azazael_core.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls

# ── Python 3.14t Free-Threading Awareness ────────────────────────────
try:
    from azazael_core.freethreading import is_free_threaded, FreeThreadPool, ThreadSafeDict, ThreadSafeList
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
    FreeThreadPool = None
    ThreadSafeDict = dict
    ThreadSafeList = list
    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False


@register_worm(category="migration", priority=6, cooldown_seconds=120.0,
    description="Code migrator — automated Python 2→3 migration with lib2to3 fixers")
class CodeMigrator:
    """Automated code migration for Python version upgrades."""

    VERSION = "1.0.0"

    def __init__(self):
        self._migrations: List[Dict] = []

    def detect_python2_patterns(self, filepath: str) -> List[Dict]:
        """Detect Python 2 patterns in a file."""
        patterns = []
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
        checks = [
            ("print ", "Python 2 print statement", "Use print()"),
            ("except Exception, e:", "Python 2 except syntax", "Use 'except Exception as e:'"),
            ("xrange(", "Python 2 xrange", "Use range()"),
            ("unicode(", "Python 2 unicode", "Use str"),
            (".has_key(", "Python 2 dict.has_key", "Use 'in' operator"),
        ]
        for pattern, msg, fix in checks:
            if pattern in content:
                patterns.append({"pattern": pattern, "message": msg, "fix": fix})
        return patterns

    def run_2to3(self, filepath: str, dry_run: bool = True) -> Dict[str, Any]:
        """Run lib2to3 on a file."""
        try:
            cmd = [sys.executable, "-m", "lib2to3", "-n"]
            if not dry_run:
                cmd.append("-w")
            cmd.append(filepath)
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
            return {"success": True, "dry_run": dry_run, "output": r.stdout[:500]}
        except Exception as e:
            return {"success": False, "error": str(e)}


@register_worm(category="migration", priority=5, cooldown_seconds=90.0,
    description="Dependency upgrader — auto-upgrade requirements.txt with compatibility testing")
class DepUpgrader:
    """Automated dependency version upgrades with compatibility checks."""

    VERSION = "1.0.0"

    def __init__(self):
        self._upgrade_log: List[Dict] = []

    def parse_requirements(self, req_path: str) -> Dict[str, str]:
        """Parse requirements.txt into {package: version}."""
        deps = {}
        path = Path(req_path)
        if path.exists():
            for line in path.read_text(encoding="utf-8").split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    if "==" in line:
                        pkg, ver = line.split("==", 1)
                        deps[pkg.strip()] = ver.strip()
                    elif ">=" in line:
                        pkg, ver = line.split(">=", 1)
                        deps[pkg.strip()] = f">={ver.strip()}"
                    else:
                        deps[line] = "latest"
        return deps

    def check_outdated(self, req_path: str) -> List[Dict]:
        """Check for outdated packages using pip list --outdated."""
        try:
            r = subprocess.run([sys.executable, "-m", "pip", "list", "--outdated", "--format", "json"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
            if r.returncode == 0:
                return json.loads(r.stdout)
        except Exception:
            pass
        return []


@register_worm(category="migration", priority=4, cooldown_seconds=60.0,
    description="Schema versioner — track JSON/YAML schema versions and detect breaking changes")
class SchemaVersioner:
    """Tracks schema versions and detects breaking changes."""

    VERSION = "1.0.0"

    def __init__(self):
        self._schemas: Dict[str, List[Dict]] = {}

    def register_schema(self, name: str, schema: Dict[str, Any]):
        version = len(self._schemas.get(name, [])) + 1
        entry = {"version": version, "schema": schema, "date": datetime.now().isoformat()}
        if name not in self._schemas:
            self._schemas[name] = []
        self._schemas[name].append(entry)

    def detect_breaking_changes(self, schema_name: str) -> List[str]:
        """Compare latest schema to previous and detect removed/renamed keys."""
        schemas = self._schemas.get(schema_name, [])
        if len(schemas) < 2:
            return []
        old, new = schemas[-2]["schema"], schemas[-1]["schema"]
        removed = set(old.keys()) - set(new.keys())
        type_changed = [k for k in (set(old) & set(new)) if type(old[k]) != type(new[k])]
        return [f"Removed: {r}" for r in removed] + [f"Type changed: {t}" for t in type_changed]


@register_worm(category="migration", priority=4, cooldown_seconds=45.0,
    description="Import path fixer — update import paths after file moves/renames")
class ImportPathFixWorm:
    """Fixes import paths after file moves or renames."""

    VERSION = "1.0.0"

    def __init__(self):
        self._mappings: Dict[str, str] = {}
        self._lock = threading.Lock()

    def add_mapping(self, old_path: str, new_path: str):
        with self._lock:
            self._mappings[old_path] = new_path

    def fix_file(self, filepath: str) -> int:
        """Apply import path mappings to a file."""
        path = Path(filepath)
        if not path.exists():
            return 0
        content = path.read_text(encoding="utf-8")
        fixed = 0
        with self._lock:
            for old, new in self._mappings.items():
                count = content.count(old)
                if count:
                    content = content.replace(old, new)
                    fixed += count
        if fixed:
            path.write_text(content, encoding="utf-8")
        return fixed


@register_worm(category="migration", priority=3, cooldown_seconds=60.0,
    description="Legacy shim generator — create backward-compatibility wrappers for renamed APIs")
class LegacyShimGen:
    """Generates backward-compatibility shims for renamed functions/classes."""

    VERSION = "1.0.0"

    def __init__(self):
        self._shims: Dict[str, str] = {}

    def generate_shim(self, old_name: str, new_name: str, module_path: str) -> str:
        """Generate a shim that re-exports old name from new location."""
        shim = f'''"""
Auto-generated backward-compatibility shim.
{old_name} → {new_name}
"""
from {module_path} import {new_name}
{old_name} = {new_name}
'''
        self._shims[old_name] = shim
        return shim

    def write_shim(self, old_name: str, output_dir: str):
        """Write a shim file to disk."""
        if old_name in self._shims:
            path = Path(output_dir) / f"{old_name}_shim.py"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self._shims[old_name], encoding="utf-8")
            return str(path)
        return ""
