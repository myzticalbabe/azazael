# coding: utf-8
"""
OMNI_WORM - Ultimate Self-Healing Worm
Diagnoses and fixes ALL Azazael module issues
"""

import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime

AZAAZEL_ROOT = Path(__file__).parent.parent.parent
VENV_PYTHON = AZAAZEL_ROOT / ".venv" / "Scripts" / "python.exe"


def fix_bom_files():
    print("\n[1/6] Scanning and fixing BOM characters...")
    fixed = 0
    for py_file in AZAAZEL_ROOT.rglob("*.py"):
        try:
            content = py_file.read_bytes()
            if content.startswith(b"\xef\xbb\xbf"):
                content = content[3:]
                py_file.write_bytes(content)
                print(f"      Fixed BOM: {py_file.relative_to(AZAAZEL_ROOT)}")
                fixed += 1
        except Exception:
            pass
    print(f"      Total BOM fixes: {fixed}")
    return fixed


def fix_syspath_imports():
    print("\n[2/6] Fixing sys.path imports...")
    fixed = 0

    pattern = rb"C:\\Users\\clint\\Desktop\\Azazael_UNIFIED"

    for py_file in AZAAZEL_ROOT.rglob("*.py"):
        try:
            content = py_file.read_bytes()
            if pattern in content:
                text = content.decode("utf-8-sig")

                if "ml_platforms" in str(py_file):
                    new_import = 'sys.path.insert(0, str(Path(__file__).parent / "ml_platforms"))'
                else:
                    new_import = 'sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))'

                old_pattern = (
                    r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)"
                )

                if re.search(old_pattern, text):
                    new_text = re.sub(old_pattern, new_import, text)
                    py_file.write_text(new_text, encoding="utf-8")
                    print(f"      Fixed: {py_file.relative_to(AZAAZEL_ROOT)}")
                    fixed += 1
        except Exception:
            pass

    print(f"      Total sys.path fixes: {fixed}")
    return fixed


def create_init_files():
    print("\n[3/6] Creating missing __init__.py files...")
    created = 0

    dirs = [
        AZAAZEL_ROOT / "CORE",
        AZAAZEL_ROOT / "CORE" / "WORMS",
        AZAAZEL_ROOT / "HYDRA",
        AZAAZEL_ROOT / "HYDRA" / "ml_platforms",
        AZAAZEL_ROOT / "META",
        AZAAZEL_ROOT / "UTILITIES",
        AZAAZEL_ROOT / "UTILITIES" / "TERENCE",
        AZAAZEL_ROOT / "UTILITIES" / "TARBABY",
        AZAAZEL_ROOT / "UTILITIES" / "KLINK",
        AZAAZEL_ROOT / "UTILITIES" / "PERSEPHONE",
        AZAAZEL_ROOT / "UTILITIES" / "POINDEXTER",
        AZAAZEL_ROOT / "ORCHESTRATION",
        AZAAZEL_ROOT / "ORCHESTRATION" / "ml_platforms",
        AZAAZEL_ROOT / "ORCHESTRATION" / "ml_platforms" / "improvements",
        AZAAZEL_ROOT / "ORCHESTRATION" / "scripts",
        AZAAZEL_ROOT / "ORCHESTRATION" / "TEST",
        AZAAZEL_ROOT / "CODEX",
        AZAAZEL_ROOT / "CODEX" / "TESTING",
        AZAAZEL_ROOT / "CODEX" / "TESTING" / "UNIT",
        AZAAZEL_ROOT / "CODEX" / "TESTING" / "PERFORMANCE",
        AZAAZEL_ROOT / "CODEX" / "TESTING" / "INTEGRATION",
        AZAAZEL_ROOT / "CODEX" / "DOCUMENTATION",
        AZAAZEL_ROOT / "CODEX" / "VIDEOS",
    ]

    init_content = '# coding: utf-8\n"""\nAuto-generated package init\n"""\n'

    for d in dirs:
        init_file = d / "__init__.py"
        if not init_file.exists():
            try:
                init_file.write_text(init_content, encoding="utf-8")
                print(f"      Created: {d.name}/__init__.py")
                created += 1
            except Exception:
                pass

    print(f"      Total created: {created}")
    return created


def test_imports():
    print("\n[4/6] Testing module imports...")

    test_code = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))

results = {}

tests = [
    ("HYDRA.hydra_launcher", "HYDRA Launcher"),
    ("META.HYDRAMETA", "HYDRA Meta"),
    ("CORE.WORMS.WORMZ", "WORMZ"),
    ("CORE.WORMS.SYSTEMZ", "SYSTEMZ"),
]

for mod, name in tests:
    try:
        exec(f"import {mod.replace('.', '_')}")
        results[name] = ("OK", "")
    except Exception as e:
        results[name] = ("FAIL", str(e)[:80])

print(str(results))
"""

    result = subprocess.run(
        [str(VENV_PYTHON), "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(AZAAZEL_ROOT / "HYDRA"),
    )

    if result.stdout:
        try:
            data = eval(result.stdout.strip())
            for name, (status, error) in data.items():
                icon = "[OK]" if status == "OK" else "[FAIL]"
                print(f"      {icon} {name}")
                if status == "FAIL" and error:
                    print(f"          -> {error}")
        except Exception as e:
            print(f"      Parse error: {e}")


def verify_ml():
    print("\n[5/6] Verifying ML frameworks...")

    code = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))

import tensorflow as tf
import torch
import sklearn
import numpy
import pandas

print(f"TensorFlow: {tf.__version__}")
print(f"PyTorch: {torch.__version__}")
print(f"sklearn: {sklearn.__version__}")
print(f"NumPy: {numpy.__version__}")
print(f"Pandas: {pandas.__version__}")
"""

    result = subprocess.run(
        [str(VENV_PYTHON), "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(AZAAZEL_ROOT),
    )

    if result.returncode == 0:
        for line in result.stdout.strip().split("\n"):
            print(f"      [OK] {line}")
    else:
        print(f"      [FAIL] {result.stderr[:100]}")


def create_bootstrap():
    print("\n[6/6] Creating bootstrapper...")

    bootstrap = '''# coding: utf-8
"""
Azazael Bootstrapper
Run this first to initialize all module paths
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
HYDRA_ML = ROOT / "HYDRA" / "ml_platforms"

if str(HYDRA_ML) not in sys.path:
    sys.path.insert(0, str(HYDRA_ML))

print(f"Azazael bootstrap complete. PYTHONPATH includes: {HYDRA_ML}")
'''

    boot_file = AZAAZEL_ROOT / "bootstrap.py"
    boot_file.write_text(bootstrap, encoding="utf-8")
    print(f"      Created: bootstrap.py")

    return True


def main():
    print("=" * 60)
    print("OMNI WORM - Ultimate Self-Healing")
    print("=" * 60)

    bom_fixes = fix_bom_files()
    syspath_fixes = fix_syspath_imports()
    init_creates = create_init_files()

    test_imports()
    verify_ml()
    create_bootstrap()

    print("\n" + "=" * 60)
    print("HEALING SUMMARY")
    print("=" * 60)
    print(f"\nBOM fixes: {bom_fixes}")
    print(f"sys.path fixes: {syspath_fixes}")
    print(f"__init__.py created: {init_creates}")
    print("\nTo use Azazael modules, run first:")
    print(f"  python {AZAAZEL_ROOT}/bootstrap.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
