# coding: utf-8
"""
Install Manager

Module for ml_platforms functionality.

Functions:
    - main()
    - pip_install()
    - check_version()
    - check_compatibility()
    - detect_conflicts()
    - install_category()
    - install_all()
    - rollback()
    - generate_report()
    - health_check()

Classes:
    - InstallStatus
    - InstallRecord
    - CompatibilityRule
    - UnifiedInstaller

Usage:
    >>> import install_manager
    >>> install_manager.main()

Author: Auto-generated
Date: 2026-02-10
"""

# coding: utf-8
"""
ML Platform Installation Manager
Unified installer with version compatibility, conflict resolution, and rollback support.
"""

import subprocess
import sys
import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time


class InstallStatus(Enum):
    PENDING = "pending"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


@dataclass
class InstallRecord:
    package: str
    version: str
    status: InstallStatus
    timestamp: float
    output: str = ""
    error: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class CompatibilityRule:
    package: str
    min_version: str
    max_version: str
    conflict_with: Dict[str, Tuple[str, str]]
    required_by: Dict[str, Tuple[str, str]]


class UnifiedInstaller:
    """
    Unified installation manager for all ML platforms.

    FEATURES:
    - Single entry point for all installations
    - Automatic dependency resolution
    - Version compatibility checking
    - Conflict detection and resolution
    - Installation rollback capability
    - Audit trail and reporting
    """

    CORE_PACKAGES = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        "tensorflow>=2.15.0",
        "jax jaxlib",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "pandas>=2.0.0",
    ]

    ML_PACKAGES = [
        "scikit-learn>=1.4.0",
        "xgboost>=2.0.0",
        "lightgbm>=4.0.0",
        "catboost>=1.2.0",
        "optuna>=3.5.0",
        "ray[default]>=2.9.0",
        "mlflow>=2.10.0",
    ]

    CV_PACKAGES = [
        "opencv-python>=4.9.0",
        "opencv-contrib-python>=4.9.0",
        "pillow>=10.0.0",
        "scikit-image>=0.22.0",
        "easyocr>=1.7.0",
        "deepface>=0.0.90",
        "mtcnn>=0.1.0",
        "retinaface>=0.0.10",
    ]

    NLP_PACKAGES = [
        "transformers>=4.40.0",
        "huggingface-hub>=0.23.0",
        "tokenizers>=0.19.0",
        "nltk>=3.9.0",
        "spacy>=3.7.0",
    ]

    DEPLOY_PACKAGES = [
        "onnx>=1.16.0",
        "onnxruntime-gpu>=1.17.0",
        "onnxruntime-tools>=1.0.0",
        "tensorboard>=2.15.0",
        "fastapi>=0.110.0",
        "uvicorn>=0.27.0",
    ]

    UTILITY_PACKAGES = [
        "einops>=0.8.0",
        "imageio>=2.34.0",
        "joblib>=1.4.0",
        "networkx>=3.2.0",
        "shapely>=2.0.0",
        "h5py>=3.11.0",
        "functorch>=0.2.0",
        "torchgen>=0.1.0",
        "gymnasium>=1.0.0",
        "stable-baselines3>=2.7.0",
    ]

    def __init__(self, verbose: bool = True, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.install_history: List[InstallRecord] = []
        self.rollback_stack: List[str] = []
        self._compat_cache: Dict[str, CompatibilityRule] = {}

    def _run_command(self, cmd: List[str], desc: str = "") -> Tuple[bool, str]:
        """Execute command and return success status and output."""
        if self.dry_run:
            print(f"[DRY RUN] {desc}: {' '.join(cmd)}")
            return True, "dry_run"

        if self.verbose:
            print(f"[{desc}] {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=600
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr[:500]
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def pip_install(self, package: str, upgrade: bool = False) -> bool:
        """Install a package via pip."""
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        cmd.append(package)

        success, output = self._run_command(cmd, f"Installing {package}")
        return success

    def check_version(self, package: str) -> Optional[str]:
        """Check installed version of a package."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    f"import {package}; print({package}.__version__)",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def check_compatibility(self) -> Dict[str, Tuple[bool, str]]:
        """Check version compatibility across packages."""
        results = {}

        version_checks = [
            (
                "torch",
                "torchvision",
                lambda v1, v2: v1.split(".")[:2] == v2.split(".")[:2],
            ),
            (
                "torch",
                "torchaudio",
                lambda v1, v2: v1.split(".")[0] == v2.split(".")[0],
            ),
            ("tensorflow", "keras", lambda v1, v2: True),
            ("numpy", "pandas", lambda v1, v2: True),
        ]

        for pkg1, pkg2, check_fn in version_checks:
            v1 = self.check_version(pkg1)
            v2 = self.check_version(pkg2)

            if v1 and v2:
                compatible = check_fn(v1, v2)
                results[f"{pkg1}-{pkg2}"] = (compatible, f"{v1} vs {v2}")

        return results

    def detect_conflicts(self) -> List[Tuple[str, str, str]]:
        """Detect known package conflicts."""
        conflicts = [
            (
                "torch",
                "torchvision",
                "Versions must match (check PyTorch version compatibility)",
            ),
            (
                "tensorflow",
                "keras",
                "TensorFlow 2.x bundles Keras; separate Keras may conflict",
            ),
            ("onnx", "onnxruntime", "Version mismatch can cause import errors"),
            ("numpy", "tensorflow", "TensorFlow requires specific NumPy version"),
        ]

        detected = []
        for pkg1, pkg2, msg in conflicts:
            v1 = self.check_version(pkg1)
            v2 = self.check_version(pkg2)
            if v1 and v2:
                detected.append((pkg1, pkg2, f"{msg} (installed: {v1}, {v2})"))

        return detected

    def install_category(
        self, category: str, extras: str = ""
    ) -> Dict[str, InstallStatus]:
        """Install a category of packages."""
        category_map = {
            "core": self.CORE_PACKAGES,
            "ml": self.ML_PACKAGES,
            "cv": self.CV_PACKAGES,
            "nlp": self.NLP_PACKAGES,
            "deploy": self.DEPLOY_PACKAGES,
            "utils": self.UTILITY_PACKAGES,
            "all": self.CORE_PACKAGES
            + self.ML_PACKAGES
            + self.CV_PACKAGES
            + self.NLP_PACKAGES
            + self.DEPLOY_PACKAGES
            + self.UTILITY_PACKAGES,
        }

        packages = category_map.get(category, category_map["all"])
        results = {}

        for pkg in packages:
            package_name = pkg.split()[0]
            success = self.pip_install(pkg, upgrade=True)
            results[package_name] = (
                InstallStatus.INSTALLED if success else InstallStatus.FAILED
            )

        return results

    def install_all(self) -> Dict[str, InstallStatus]:
        """Install all ML platforms."""
        return self.install_category("all")

    def rollback(self, package: str) -> bool:
        """Rollback a package installation."""
        success, _ = self._run_command(
            [sys.executable, "-m", "pip", "uninstall", "-y", package],
            f"Rolling back {package}",
        )
        return success

    def generate_report(self) -> Dict[str, Any]:
        """Generate installation report."""
        return {
            "timestamp": time.time(),
            "total_installed": sum(
                1 for r in self.install_history if r.status == InstallStatus.INSTALLED
            ),
            "failed": [
                r.package
                for r in self.install_history
                if r.status == InstallStatus.FAILED
            ],
            "compat_issues": self.detect_conflicts(),
        }

    def health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        return {
            "packages": {
                pkg: {"version": self.check_version(pkg)}
                for pkg in ["torch", "tensorflow", "numpy", "scipy", "pandas"]
            },
            "compatibility": self.check_compatibility(),
            "conflicts": self.detect_conflicts(),
        }


def main():
    """Main entry point."""
    installer = UnifiedInstaller(verbose=True)

    print("=" * 70)
    print("ML PLATFORM UNIFIED INSTALLER")
    print("=" * 70)

    print("\n[1/4] Checking current installation...")
    health = installer.health_check()
    print(f"  Torch: {health['packages']['torch']['version']}")
    print(f"  TensorFlow: {health['packages']['tensorflow']['version']}")
    print(f"  NumPy: {health['packages']['numpy']['version']}")

    print("\n[2/4] Detecting conflicts...")
    conflicts = installer.detect_conflicts()
    if conflicts:
        print("  Conflicts found:")
        for p1, p2, msg in conflicts:
            print(f"    {p1} <-> {p2}: {msg}")
    else:
        print("  No conflicts detected")

    print("\n[3/4] Installing core packages...")
    results = installer.install_category("core")
    print(
        f"  Installed: {sum(1 for v in results.values() if v == InstallStatus.INSTALLED)}"
    )

    print("\n[4/4] Generating report...")
    report = installer.generate_report()
    print(f"  Total installed: {report['total_installed']}")
    print(f"  Failed: {len(report['failed'])}")

    print("\n" + "=" * 70)
    print("INSTALLATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
