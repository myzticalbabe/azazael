# coding: utf-8
"""
HEALING_WORM - Self-Healing Module Activation
Fixes import paths and activates all Azazael modules
"""

import sys
import subprocess
import re
from pathlib import Path

AZAAZEL_ROOT = Path(__file__).parent.parent.parent


def run_healing():
    print("=" * 60)
    print("HEALING WORM - Self-Healing Module Activation")
    print("=" * 60)
    print()

    fixes = []

    print("[1/4] Creating __init__.py files for all packages...")

    init_files = [
        AZAAZEL_ROOT / "CORE" / "__init__.py",
        AZAAZEL_ROOT / "CORE" / "WORMS" / "__init__.py",
        AZAAZEL_ROOT / "HYDRA" / "__init__.py",
        AZAAZEL_ROOT / "HYDRA" / "ml_platforms" / "__init__.py",
        AZAAZEL_ROOT / "META" / "__init__.py",
        AZAAZEL_ROOT / "UTILITIES" / "__init__.py",
        AZAAZEL_ROOT / "UTILITIES" / "TERENCE" / "__init__.py",
        AZAAZEL_ROOT / "UTILITIES" / "TARBABY" / "__init__.py",
        AZAAZEL_ROOT / "UTILITIES" / "KLINK" / "__init__.py",
        AZAAZEL_ROOT / "UTILITIES" / "PERSEPHONE" / "__init__.py",
        AZAAZEL_ROOT / "UTILITIES" / "POINDEXTER" / "__init__.py",
        AZAAZEL_ROOT / "ORCHESTRATION" / "__init__.py",
        AZAAZEL_ROOT / "ORCHESTRATION" / "ml_platforms" / "__init__.py",
        AZAAZEL_ROOT
        / "ORCHESTRATION"
        / "ml_platforms"
        / "improvements"
        / "__init__.py",
        AZAAZEL_ROOT / "ORCHESTRATION" / "scripts" / "__init__.py",
        AZAAZEL_ROOT / "ORCHESTRATION" / "TEST" / "__init__.py",
        AZAAZEL_ROOT / "CODEX" / "__init__.py",
        AZAAZEL_ROOT / "CODEX" / "TESTING" / "__init__.py",
        AZAAZEL_ROOT / "CODEX" / "TESTING" / "UNIT" / "__init__.py",
        AZAAZEL_ROOT / "CODEX" / "TESTING" / "PERFORMANCE" / "__init__.py",
        AZAAZEL_ROOT / "CODEX" / "TESTING" / "INTEGRATION" / "__init__.py",
        AZAAZEL_ROOT / "CODEX" / "DOCUMENTATION" / "__init__.py",
        AZAAZEL_ROOT / "CODEX" / "VIDEOS" / "__init__.py",
    ]

    for init_file in init_files:
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text("# coding: utf-8\n", encoding="utf-8")
            fixes.append(f"Created: {init_file.relative_to(AZAAZEL_ROOT)}")

    print(f"      Created: {len(fixes)} __init__.py files")

    print("\n[2/4] Fixing module imports...")

    modules_to_fix = {
        "HYDRA/hydra_launcher.py": [
            (
                r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)",
                'sys.path.insert(0, str(Path(__file__).parent / "ml_platforms"))',
            ),
        ],
        "HYDRA/hydra_protocols.py": [
            (
                r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)",
                'sys.path.insert(0, str(Path(__file__).parent / "ml_platforms"))',
            ),
        ],
        "META/HYDRA_CONTAINER.py": [
            (
                r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)",
                'sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))',
            ),
        ],
        "META/HYDRAMETA.py": [
            (
                r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)",
                'sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))',
            ),
        ],
        "CORE/WORMS/WORMZ.py": [
            (
                r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)",
                'sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))',
            ),
        ],
        "CORE/WORMS/SYSTEMZ.py": [
            (
                r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)",
                'sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))',
            ),
        ],
        "CORE/WORMS/CLUSTERWORMS.py": [
            (
                r"sys\.path\.insert\(0, str\(C:\\\\Users.*?ml_platforms\)\)",
                'sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))',
            ),
        ],
    }

    for rel_path, replacements in modules_to_fix.items():
        file_path = AZAAZEL_ROOT / rel_path
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8-sig")
                original = content
                for old_pat, new_pat in replacements:
                    content = re.sub(old_pat, new_pat, content)
                if content != original:
                    file_path.write_text(content, encoding="utf-8")
                    fixes.append(f"Fixed imports: {rel_path}")
            except Exception as e:
                fixes.append(f"Error fixing {rel_path}: {e}")

    print(f"      Fixed {len([f for f in fixes if 'Fixed' in f])} modules")

    print("\n[3/4] Testing module imports...")

    # Use system Python instead of venv
    test_code = f'''
import sys
from pathlib import Path
ROOT = Path(r"{AZAAZEL_ROOT}")
# Add correct paths for Azazael modules
sys.path.insert(0, str(ROOT / "HYDRA"))
sys.path.insert(0, str(ROOT / "HYDRA" / "ml_platforms"))
sys.path.insert(0, str(ROOT / "CORE" / "WORMS"))
sys.path.insert(0, str(ROOT / "UTILITIES"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "META"))

results = {{}}
try:
    import hydra_launcher
    results["HYDRA.hydra_launcher"] = "OK"
except Exception as e:
    results["HYDRA.hydra_launcher"] = str(e)[:50]

try:
    import hydra_protocols
    results["HYDRA.hydra_protocols"] = "OK"
except Exception as e:
    results["HYDRA.hydra_protocols"] = str(e)[:50]

try:
    import WORMZ
    results["CORE.WORMS.WORMZ"] = "OK"
except Exception as e:
    results["CORE.WORMS.WORMZ"] = str(e)[:50]

try:
    import SYSTEMZ
    results["CORE.WORMS.SYSTEMZ"] = "OK"
except Exception as e:
    results["CORE.WORMS.SYSTEMZ"] = str(e)[:50]

print(results)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code], capture_output=True, text=True, timeout=30
    )

    print("      Module status:")
    if result.stdout:
        try:
            module_results = eval(result.stdout.strip())
            for mod, status in module_results.items():
                icon = "[OK]" if status == "OK" else "[FAIL]"
                print(f"        {icon} {mod}: {status}")
        except Exception as e:
            print(f"      Parse error: {e}")

    print("\n[4/4] Verifying ML frameworks...")

    ml_test = f'''
import sys
from pathlib import Path
ROOT = Path(r"{AZAAZEL_ROOT}")
sys.path.insert(0, str(ROOT / "HYDRA" / "ml_platforms"))

import tensorflow as tf
import torch
import sklearn
print(f"TensorFlow: {{tf.__version__}}")
print(f"PyTorch: {{torch.__version__}}")
print(f"sklearn: {{sklearn.__version__}}")
'''

    result = subprocess.run(
        [sys.executable, "-c", ml_test], capture_output=True, text=True, timeout=30
    )

    if result.returncode == 0:
        print("      ML Frameworks:")
        for line in result.stdout.strip().split("\n"):
            print(f"        [OK] {line}")

    print("\n" + "=" * 60)
    print("HEALING COMPLETE")
    print("=" * 60)
    print(f"\nTotal fixes: {len(fixes)}")
    for fix in fixes[:15]:
        print(f"  - {fix}")

    return fixes


if __name__ == "__main__":
    run_healing()
