import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))

#!/usr/bin/env python3
"""
Unit Test Configuration and Conftest
"""

import sys
from pathlib import Path

# Add ecosystem paths
ECOSYSTEM_ROOT = Path("C:/Users/clint/Desktop")
sys.path.insert(0, str(ECOSYSTEM_ROOT))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "Azazael"))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "HYDRA"))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "WORMZ"))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "METAWORMS"))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "HORUS"))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "TERENCE"))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "KLINK"))


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "unit: mark as unit test")
    config.addinivalue_line("markers", "integration: mark as integration test")
    config.addinivalue_line("markers", "performance: mark as performance test")
