# coding: utf-8
"""
Azazael Bootstrapper v2.0 - With Dynamic Logging
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
HYDRA_ML = ROOT / "HYDRA" / "ml_platforms"

if str(HYDRA_ML) not in sys.path:
    sys.path.insert(0, str(HYDRA_ML))

sys.path.insert(0, str(ROOT / "UTILITIES"))

try:
    from AzazaelDynamicLogger import log, info, success, section
    section("AZAZAEL BOOTSTRAP")
    info(f"Root: {ROOT}")
    info(f"ML Platform: {HYDRA_ML}")
    success("Dynamic logging initialized")
    print(f"Bootstrap complete. Dynamic logging active.")
except Exception as e:
    print(f"Bootstrap warning: {e}")
