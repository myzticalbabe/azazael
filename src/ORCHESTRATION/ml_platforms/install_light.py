# coding: utf-8
"""
Install Light

Module for ml_platforms functionality.

Functions:
    - install()
    - main()

Usage:
    >>> import install_light
    >>> install_light.install()

Author: Auto-generated
Date: 2026-02-10
"""

#!/usr/bin/env python3
"""
Lightweight install - only essential packages
Run: python install_light.py
"""

import subprocess
import sys

ESSENTIALS = [
    ("mlflow", "MLflow tracking"),
    ("ray", "Distributed computing"),
    ("onnx", "ONNX export"),
    ("onnxruntime", "ONNX inference"),
]


def install(pkg, desc):
    print(f"Installing {pkg}...")
    subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
    print(f"  [OK] {desc}")


def main():
    print("=" * 60)
    print("INSTALLING ESSENTIAL IMPROVEMENTS")
    print("=" * 60)
    for pkg, desc in ESSENTIALS:
        install(pkg, desc)
        print()
        print("Optional frameworks (manual install):")
        print("  pip install torch tensorflow jax")
        print("  pip install tensorrt coremltools")
        print("=" * 60)


if __name__ == "__main__":
    main()
