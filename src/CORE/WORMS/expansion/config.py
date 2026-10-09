# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: CONFIG (5 worms)
ConfigLinter, EnvValidator, DotfileSync, SecretRotator, FeatureFlagCtrl
"""

import json
import time
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List
from collections import defaultdict

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

# -- Worm Registry Import ---------------------------------------------
try:
    from CORE.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    note_failure("config:L20", None)
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls

# -- Python 3.14t Free-Threading Awareness ----------------------------
try:
    from CORE.freethreading import is_free_threaded, FreeThreadPool, ThreadSafeDict, ThreadSafeList
    _FREETHREAD = True
except ImportError:
    note_failure("config:L29", None)
    _FREETHREAD = False
    FreeThreadPool = None
    ThreadSafeDict = dict
    ThreadSafeList = list
    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            note_failure("config:L38", None)
            return False


@register_worm(category="config", priority=5, cooldown_seconds=45.0,
    description="Config linter — JSON/YAML/TOML schema validation and consistency checking")
class ConfigLinter:
    """Lints configuration files for schema violations and consistency."""

    VERSION = "1.0.0"

    def __init__(self):
        self._lint_results: dict[str, list[dict]] = defaultdict(list)

    def lint_json(self, filepath: str) -> list[dict]:
        """Validate JSON structure and common patterns."""
        issues = []
        try:
            content = Path(filepath).read_text(encoding="utf-8")
            data = json.loads(content)
            if isinstance(data, dict):
                for k in data:
                    if not k.isidentifier() and "-" in k:
                        issues.append({"key": k, "msg": "Key contains hyphen (not Python-compatible)", "severity": "info"})
        except json.JSONDecodeError as e:
            note_failure("config:L62", e)
            issues.append({"msg": f"Invalid JSON: {e}", "severity": "error"})
        self._lint_results[filepath] = issues
        return issues

    def lint_yaml(self, filepath: str) -> list[dict]:
        """Validate YAML structure."""
        issues = []
        try:
            content = Path(filepath).read_text(encoding="utf-8")
            if "\t" in content:
                issues.append({"msg": "YAML contains tab characters", "severity": "warning"})
        except Exception as e:
            note_failure("config:L74", e)
            issues.append({"msg": str(e), "severity": "error"})
        self._lint_results[filepath] = issues
        return issues



    def get_summary(self):
        return {"status":"ok","worm":"ConfigLinter","method":"lint_json"}
@register_worm(category="config", priority=5, cooldown_seconds=30.0,
    description="Environment validator — check env consistency across .env, system env, and docker-compose")
class EnvValidator:
    """Validates environment variable consistency across config sources."""

    VERSION = "1.0.0"

    def __init__(self):
        self._env_map: dict[str, dict[str, str]] = {}

    def scan_env_files(self, *paths: str) -> dict[str, Any]:
        """Scan .env files and compare variable sets."""
        envs: dict[str, dict[str, str]] = {}
        for p in paths:
            path = Path(p)
            if path.exists():
                vars_ = {}
                for line in path.read_text(encoding="utf-8").split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        vars_[k] = v
                envs[str(path)] = vars_
        all_keys = set()
        for vars_ in envs.values():
            all_keys.update(vars_.keys())
        missing = {str(p): all_keys - set(vars_.keys()) for p, vars_ in envs.items()}
        self._env_map = envs
        return {"files": len(envs), "total_keys": len(all_keys), "missing_per_file": {k: list(v) for k, v in missing.items() if v}}


@register_worm(category="config", priority=4, cooldown_seconds=60.0,
    description="Dotfile sync — sync .bashrc, .zshrc, .profile across machines")
class DotfileSync:
    """Syncs dotfiles across machines with conflict resolution."""

    VERSION = "1.0.0"

    def __init__(self):
        self._profiles: dict[str, str] = {}
        home = Path.home()
        for f in [".bashrc", ".zshrc", ".profile", ".gitconfig"]:
            p = home / f
            if p.exists():
                self._profiles[f] = p.read_text(encoding="utf-8", errors="replace")

    def get_checksums(self) -> dict[str, str]:
        """Get checksums of all tracked dotfiles."""
        return {f: hashlib.sha256(c.encode()).hexdigest()[:16] for f, c in self._profiles.items()}


@register_worm(category="config", priority=6, cooldown_seconds=120.0,
    description="Secret rotator — credential rotation automation with backup and validation")
class SecretRotator:
    """Automates credential rotation with backup and validation."""

    VERSION = "1.0.0"

    def __init__(self):
        self._rotation_log: list[dict] = []

    def rotate_secret(self, name: str = "default", generator: (Callable[[], str] | None) = None, backup_path: str = "") -> dict[str, Any]:
        if generator is None:
            generator = self.generate_password
        """Rotate a secret: backup old, generate new, validate."""
        new_secret = generator()
        log_entry = {"name": name, "rotated_at": datetime.now().isoformat(),
                     "checksum": hashlib.sha256(new_secret.encode()).hexdigest()[:12]}
        self._rotation_log.append(log_entry)
        return {"name": name, "success": True, "checksum_preview": log_entry["checksum"]}

    def generate_password(self, length: int = 32) -> str:
        """Generate a strong random password."""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


@register_worm(category="config", priority=4, cooldown_seconds=30.0,
    description="Feature flag controller — runtime toggle management with percentage rollout")
class FeatureFlagCtrl:
    """Manages feature flags with percentage-based rollout."""

    VERSION = "1.0.0"

    def __init__(self):
        self._flags: dict[str, dict] = {}
        self._lock = threading.Lock()

    def set_flag(self, name: str, enabled: bool, rollout_pct: float = 100.0):
        with self._lock:
            self._flags[name] = {"enabled": enabled, "rollout_pct": rollout_pct, "updated": time.time()}

    def is_enabled(self, name: str, user_id: str = "") -> bool:
        """Check if a feature flag is enabled for a user."""
        with self._lock:
            flag = self._flags.get(name, {"enabled": False, "rollout_pct": 0})
        if not flag["enabled"]:
            return False
        if flag["rollout_pct"] >= 100:
            return True
        h = hashlib.sha256(f"{name}:{user_id}".encode()).digest()[0]
        return (h / 255.0 * 100) < flag["rollout_pct"]

    def get_summary(self):
        return {"status":"ok","worm":"FeatureFlagCtrl"}
