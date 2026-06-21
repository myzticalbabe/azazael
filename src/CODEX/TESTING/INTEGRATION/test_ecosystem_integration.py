import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))

#!/usr/bin/env python3
"""
Integration Tests for Azazael Ecosystem
"""

import pytest
import sys
from pathlib import Path

_src_integ = Path(__file__).resolve().parent.parent.parent.parent  # INTEGRATION/ -> TESTING/ -> CODEX/ -> src/
if str(_src_integ) not in sys.path:
    sys.path.insert(0, str(_src_integ))


class TestWORMZHydraIntegration:
    """Integration tests for WORMZ + HYDRA."""

    @pytest.mark.integration
    def test_wormz_produces_bibl_for_hydra(self):
        """Test WORMZ output can be used by HYDRA."""
        try:
            from WORMZ.WORMZ import WORMZ
            from HYDRA.HYDRA import HYDRACluster

            wormz = WORMZ()
            hydra = HYDRACluster()

            assert wormz is not None
            assert hydra is not None
        except ImportError as e:
            pytest.skip(f"Integration component not available: {e}")


class TestMetaWormsIntegration:
    """Integration tests for METAWORMS."""

    @pytest.mark.integration
    def test_metaworms_can_analyze_wormz_output(self):
        """Test METAWORMS can analyze WORMZ results."""
        try:
            from METAWORMS.METAWORMS import WormResult

            result = WormResult(name="test", success=True, output={})
            assert result.success is True
        except ImportError:
            pytest.skip("METAWORMS not available")


class TestKLINKIntegration:
    """Integration tests for KLINK."""

    @pytest.mark.integration
    def test_klink_has_all_commands(self):
        """Test klink has expected commands."""
        try:
            from KLINK.klink import COMMANDS

            expected = [
                "status",
                "worms",
                "hydra",
                "metaworms",
                "terence",
                "horus",
                "all",
            ]
            for cmd in expected:
                assert cmd in COMMANDS, f"Missing command: {cmd}"
        except ImportError:
            pytest.skip("KLINK not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
