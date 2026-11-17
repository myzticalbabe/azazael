"""
Tests for M16 Clinical Integration Adapter (ClinicalCrosswalk).

These tests assert, not describe. Negative cases are mandatory per Sarah build rules.
"""

import pytest
from SARAH.clinical.crosswalk import ClinicalCrosswalk, FHIRClinicalAdapter


class TestClinicalCrosswalk:
    """Core crosswalk functionality tests."""
    
    def setup_method(self):
        self.crosswalk = ClinicalCrosswalk(version="2026-11-16")
    
    # ── Positive Cases ───────────────────────────────────────────────────────
    
    def test_seed_profile_autism_dsm5tr(self):
        """F84.0 (Autism) returns 4 axes with provenance."""
        result = self.crosswalk.seed_profile("F84.0", "DSM-5-TR")
        assert isinstance(result, dict)
        assert len(result) == 4
        expected_axes = {"sensory_gain", "recovery_latency", "interoception", "attention_span"}
        assert set(result.keys()) == expected_axes
        for axis, prov in result.items():
            assert "value" in prov
            assert "source" in prov
            assert "n" in prov
            assert "grade" in prov
            assert "version" in prov
            assert isinstance(prov["value"], float)
            assert 0.0 <= prov["value"] <= 1.0
            assert isinstance(prov["n"], int)
            assert prov["n"] > 0
            assert prov["grade"] in ("A", "B", "C", "D")
    
    def test_seed_profile_adhd_dsm5tr(self):
        """F90.0 (ADHD) returns 2 axes with provenance."""
        result = self.crosswalk.seed_profile("F90.0", "DSM-5-TR")
        assert len(result) == 2
        assert set(result.keys()) == {"attention_span", "initiation_cost"}
    
    def test_seed_profile_autism_icd11(self):
        """6A02 (ICD-11 Autism) mirrors DSM-5-TR F84.0."""
        dsm = self.crosswalk.seed_profile("F84.0", "DSM-5-TR")
        icd = self.crosswalk.seed_profile("6A02", "ICD-11")
        assert icd == dsm
    
    def test_seed_profile_dyslexia(self):
        """F81.0 (Dyslexia) returns processing_speed and wm_span."""
        result = self.crosswalk.seed_profile("F81.0", "DSM-5-TR")
        assert set(result.keys()) == {"processing_speed", "wm_span"}
    
    def test_seed_profile_dyscalculia(self):
        """F81.2 (Dyscalculia) returns time_discrimination and wm_span."""
        result = self.crosswalk.seed_profile("F81.2", "DSM-5-TR")
        assert set(result.keys()) == {"time_discrimination", "wm_span"}
    
    def test_seed_profile_alexithymia(self):
        """F84.5 (Alexithymia) returns interoception."""
        result = self.crosswalk.seed_profile("F84.5", "DSM-5-TR")
        assert set(result.keys()) == {"interoception"}
    
    def test_seed_profile_tourette(self):
        """F95.2 (Tourette) returns sensory_gain."""
        result = self.crosswalk.seed_profile("F95.2", "DSM-5-TR")
        assert set(result.keys()) == {"sensory_gain"}
    
    def test_seed_profile_dyspraxia(self):
        """F83 (Dyspraxia) returns initiation_cost and wm_span."""
        result = self.crosswalk.seed_profile("F83", "DSM-5-TR")
        assert set(result.keys()) == {"initiation_cost", "wm_span"}
    
    # ── Negative Cases (MANDATORY per build rules) ───────────────────────────
    
    def test_unknown_code_returns_empty_dict(self):
        """Unknown code returns empty dict (not a default profile)."""
        result = self.crosswalk.seed_profile("Z99.9", "DSM-5-TR")
        assert result == {}
    
    def test_unknown_code_icd11_returns_empty_dict(self):
        """Unknown ICD-11 code returns empty dict."""
        result = self.crosswalk.seed_profile("9999", "ICD-11")
        assert result == {}
    
    def test_unknown_system_returns_empty_dict(self):
        """Unknown system returns empty dict."""
        result = self.crosswalk.seed_profile("F84.0", "UNKNOWN")
        assert result == {}
    
    def test_provenance_fields_present_on_all_axes(self):
        """Every axis in result carries full provenance (source, n, grade, version)."""
        result = self.crosswalk.seed_profile("F84.0", "DSM-5-TR")
        for axis, prov in result.items():
            assert "source" in prov, f"Axis {axis} missing 'source'"
            assert "n" in prov, f"Axis {axis} missing 'n'"
            assert "grade" in prov, f"Axis {axis} missing 'grade'"
            assert "version" in prov, f"Axis {axis} missing 'version'"
            assert prov["source"] != "hypothesis" or prov["grade"] == "D"
    
    def test_no_diagnosis_gated_features(self):
        """Crosswalk never returns feature gates — only axis weights."""
        result = self.crosswalk.seed_profile("F84.0", "DSM-5-TR")
        # Should not contain any feature flags
        forbidden_keys = {"feature_gate", "enable", "disable", "mode", "toggle", "autism_mode", "adhd_mode"}
        for axis, prov in result.items():
            for key in forbidden_keys:
                assert key not in prov, f"Forbidden feature gate key '{key}' in {axis}"
    
    # ── Merge Tests ──────────────────────────────────────────────────────────
    
    def test_merge_user_override_wins(self):
        """User slider overrides seed value."""
        from SARAH.profile import SarahProfile
        
        # User profile with sensory_gain = 0.9
        user = SarahProfile(sensory_gain=0.9, processing_speed=0.5)
        seed = self.crosswalk.seed_profile("F84.0", "DSM-5-TR")  # sensory_gain=0.85 in seed
        merged = self.crosswalk.merge(user, seed)
        
        assert merged.sensory_gain == 0.9  # User wins
        # Unset axes filled from seed
        assert merged.recovery_latency == 0.72
    
    def test_merge_unset_axes_filled_from_seed(self):
        """Unset axes in user profile are filled from seed."""
        from SARAH.profile import SarahProfile
        
        # User profile with only sensory_gain set
        user = SarahProfile(sensory_gain=0.5)
        seed = self.crosswalk.seed_profile("F84.0", "DSM-5-TR")
        merged = self.crosswalk.merge(user, seed)
        
        # User value preserved
        assert merged.sensory_gain == 0.5
        # Unset axes filled from seed
        assert merged.recovery_latency == 0.72
        assert merged.interoception == 0.68
        assert merged.attention_span == 0.45
    
    def test_merge_multi_highest_weight_wins(self):
        """Multiple codes: highest weight per axis wins."""
        from SARAH.profile import SarahProfile
        
        # F84.0 (sensory_gain=0.85) + F90.1 (sensory_gain=0.70) → 0.85 wins
        user = SarahProfile()
        codes = [("F84.0", "DSM-5-TR"), ("F90.1", "DSM-5-TR")]
        merged = self.crosswalk.merge_multi(codes, user)
        
        assert merged.sensory_gain == 0.85
        # F90.1 has initiation_cost=0.72, F84.0 doesn't have it → 0.72
        assert merged.initiation_cost == 0.72
    
    def test_merge_multi_empty_codes_returns_user(self):
        """Empty codes list returns user profile unchanged."""
        from SARAH.profile import SarahProfile
        
        user = SarahProfile(sensory_gain=0.5)
        merged = self.crosswalk.merge_multi([], user)
        assert merged.sensory_gain == 0.5
    
    # ── Version Management ───────────────────────────────────────────────────
    
    def test_list_versions(self):
        """list_versions returns available versions."""
        versions = ClinicalCrosswalk.list_versions()
        assert "2026-11-16" in versions
    
    def test_load_table(self):
        """load_table returns raw table for version/system."""
        table = ClinicalCrosswalk.load_table("2026-11-16", "DSM-5-TR")
        assert "F84.0" in table
        assert len(table) >= 8  # At least the codes we defined
    
    def test_diff_versions(self):
        """diff_versions returns axis deltas (only one version exists, so empty)."""
        diff = ClinicalCrosswalk.diff_versions("2026-11-16", "2026-11-16", "DSM-5-TR")
        assert diff == {}


class TestFHIRClinicalAdapter:
    """FHIR bundle ingestion stub tests (Grade D — untested)."""
    
    def test_extract_codes_condition_icd10(self):
        """Extract ICD-10 code from Condition resource."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [{
                "resource": {
                    "resourceType": "Condition",
                    "code": {
                        "coding": [{
                            "system": "http://hl7.org/fhir/sid/icd-10-cm",
                            "code": "F84.0"
                        }]
                    }
                }
            }]
        }
        adapter = FHIRClinicalAdapter()
        codes = adapter.extract_codes(bundle)
        assert ("F84.0", "DSM-5-TR") in codes
    
    def test_extract_codes_observation_icd11(self):
        """Extract ICD-11 code from Observation resource."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [{
                "resource": {
                    "resourceType": "Observation",
                    "code": {
                        "coding": [{
                            "system": "http://id.who.int/icd11/mms",
                            "code": "6A02"
                        }]
                    }
                }
            }]
        }
        adapter = FHIRClinicalAdapter()
        codes = adapter.extract_codes(bundle)
        assert ("6A02", "ICD-11") in codes
    
    def test_extract_codes_empty_bundle(self):
        """Empty bundle returns empty list."""
        adapter = FHIRClinicalAdapter()
        codes = adapter.extract_codes({"resourceType": "Bundle", "entry": []})
        assert codes == []
    
    def test_extract_codes_missing_entry(self):
        """Bundle without entry returns empty list."""
        adapter = FHIRClinicalAdapter()
        codes = adapter.extract_codes({"resourceType": "Bundle"})
        assert codes == []
    
    def test_seed_from_bundle_empty(self):
        """Empty bundle returns user profile unchanged."""
        from SARAH.profile import SarahProfile
        
        adapter = FHIRClinicalAdapter()
        user = SarahProfile(sensory_gain=0.5)
        result = adapter.seed_from_bundle({"resourceType": "Bundle", "entry": []}, user)
        assert result.sensory_gain == 0.5
    
    def test_seed_from_bundle_with_codes(self):
        """Bundle with codes merges into profile."""
        from SARAH.profile import SarahProfile
        
        adapter = FHIRClinicalAdapter()
        bundle = {
            "resourceType": "Bundle",
            "entry": [{
                "resource": {
                    "resourceType": "Condition",
                    "code": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "F84.0"}]}
                }
            }]
        }
        user = SarahProfile()
        result = adapter.seed_from_bundle(bundle, user)
        assert result.sensory_gain == 0.85
        assert result.recovery_latency == 0.72


class TestCrosswalkInvariants:
    """Invariants that must always hold."""
    
    def test_all_axes_in_0_1_range(self):
        """All axis values in [0, 1]."""
        crosswalk = ClinicalCrosswalk()
        for code in ["F84.0", "F90.0", "F81.0", "F81.2", "F83", "F84.5", "F95.2"]:
            for system in ["DSM-5-TR", "ICD-11"]:
                result = crosswalk.seed_profile(code, system)
                for prov in result.values():
                    assert 0.0 <= prov["value"] <= 1.0, f"{code} {system} {prov['value']} out of range"
    
    def test_no_axis_missing_source(self):
        """Every axis has a source study."""
        crosswalk = ClinicalCrosswalk()
        for code in ["F84.0", "F90.0", "F81.0", "F81.2", "F83", "F84.5", "F95.2"]:
            result = crosswalk.seed_profile(code, "DSM-5-TR")
            for prov in result.values():
                assert prov["source"] != ""
                assert prov["source"] is not None
    
    def test_version_consistency(self):
        """All axes in a version share the same version string."""
        crosswalk = ClinicalCrosswalk(version="2026-11-16")
        result = crosswalk.seed_profile("F84.0", "DSM-5-TR")
        versions = {prov["version"] for prov in result.values()}
        assert len(versions) == 1
        assert "2026-11-16" in versions


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])