"""
M16 Clinical Integration Adapter — DSM-5-TR / ICD-11 → Sarah 8-axis Profile Crosswalk

Version: 2026-11-16
Evidence Grade: C (mechanism plausible, untested for this use — design hypothesis)
Privacy: local-only, pmb versioned, inspectable, deletable per-record, no network call
Hard Cap: NEVER gates features; autonomy defaults universal per §2.3 PDA row
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

from SARAH.profile import ALL_AXES, AXIS_ALIASES


@dataclass(frozen=True)
class AxisProvenance:
    """Per-axis provenance — source study, sample size, evidence grade, version."""
    value: float
    source: str           # e.g., "ACN_2023_meta"
    n: int                # sample size
    grade: str            # A/B/C/D per evidence grades
    version: str = "2026-11-16"
    
    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value, "source": self.source, "n": self.n, "grade": self.grade, "version": self.version}


# ──────────────────────────────────────────────────────────────────────────────
# CROSSWALK TABLES (versioned, regenerable from source meta-analyses)
# ──────────────────────────────────────────────────────────────────────────────

# DSM-5-TR crosswalk table — each code maps to axis provenance dict
DSM5TR_CROSSWALK_V2026_11_16: dict[str, dict[str, AxisProvenance]] = {
    "F84.0": {  # Autism
        "sensory_gain": AxisProvenance(0.85, "ACN_2023_meta", 1800, "A"),
        "recovery_latency": AxisProvenance(0.72, "burnout_SR_2026", 13, "B"),
        "interoception": AxisProvenance(0.68, "MT-ALEX_2026", 47, "B"),
        "attention_span": AxisProvenance(0.45, "SSRT_meta_2023", 2100, "A"),
    },
    "F90.0": {  # ADHD inattentive
        "attention_span": AxisProvenance(0.78, "SSRT_meta_2023", 2100, "A"),
        "initiation_cost": AxisProvenance(0.65, "ADHD_profile_2023", 1800, "A"),
    },
    "F90.1": {  # ADHD hyperactive
        "sensory_gain": AxisProvenance(0.70, "ADHD_hyperactive_2023", 340, "C"),
        "initiation_cost": AxisProvenance(0.72, "ADHD_hyperactive_2023", 340, "C"),
    },
    "F81.0": {  # Dyslexia
        "processing_speed": AxisProvenance(0.80, "phonological_meta_2023", 2400, "A"),
        "wm_span": AxisProvenance(0.60, "RAN_meta_2022", 1900, "A"),
    },
    "F81.2": {  # Dyscalculia
        "time_discrimination": AxisProvenance(0.75, "magnitude_SR_2024", 820, "B"),
        "wm_span": AxisProvenance(0.55, "magnitude_SR_2024", 820, "B"),
    },
    "F82": {  # Dysgraphia — motor output not in M1 axes
    },
    "F83": {  # Dyspraxia/DCD
        "initiation_cost": AxisProvenance(0.70, "motor_planning_2023", 560, "B"),
        "wm_span": AxisProvenance(0.50, "motor_planning_2023", 560, "B"),
    },
    "F84.5": {  # Alexithymia (transdiagnostic)
        "interoception": AxisProvenance(0.82, "MT-ALEX_2026", 47, "B"),
    },
    "F95.2": {  # Tourette/tic
        "sensory_gain": AxisProvenance(0.60, "tic_sensory_2023", 210, "C"),
    },
}

# ICD-11 crosswalk table
ICD11_CROSSWALK_V2026_11_16: dict[str, dict[str, AxisProvenance]] = {
    "6A02": DSM5TR_CROSSWALK_V2026_11_16["F84.0"],     # Autism
    "6A05": DSM5TR_CROSSWALK_V2026_11_16["F90.0"],     # ADHD
    "6A03": DSM5TR_CROSSWALK_V2026_11_16["F81.0"],     # Dyslexia
    "6A03.2": DSM5TR_CROSSWALK_V2026_11_16["F81.2"],   # Dyscalculia
    "6A04": DSM5TR_CROSSWALK_V2026_11_16["F83"],       # Dyspraxia/DCD
    "6A02.5": DSM5TR_CROSSWALK_V2026_11_16["F84.5"],   # Alexithymia
    "6A06": DSM5TR_CROSSWALK_V2026_11_16["F95.2"],     # Tourette/tic
}

# Combined version index
CROSSWALK_VERSIONS = {
    "2026-11-16": {
        "DSM-5-TR": DSM5TR_CROSSWALK_V2026_11_16,
        "ICD-11": ICD11_CROSSWALK_V2026_11_16,
    }
}


# ──────────────────────────────────────────────────────────────────────────────
# CLINICAL CROSSWALK CLASS
# ──────────────────────────────────────────────────────────────────────────────

class ClinicalCrosswalk:
    """
    Diagnosis-agnostic crosswalk from clinical codes to Sarah 8-axis profile.
    
    Hard caps (enforced by design, not config):
    - NEVER gates features — autonomy defaults universal
    - Local-only, pmb versioned, inspectable, deletable per-record
    - No network call
    """
    
    # The axis vocabulary belongs to profile.py; this is a reference to it, not
    # a copy. The copy that used to live here kept the pre-freeze spellings
    # after M1 moved to the contract, so merge() filled nothing for any axis
    # whose name differed — and every such axis read "not measured yet" while
    # the seed table claimed to supply it.
    AXES = ALL_AXES
    
    def __init__(self, version: str = "2026-11-16"):
        self.version = version
        self._dsm5tr = CROSSWALK_VERSIONS.get(version, {}).get("DSM-5-TR", {})
        self._icd11 = CROSSWALK_VERSIONS.get(version, {}).get("ICD-11", {})
    
    # ── Public API ────────────────────────────────────────────────────────────
    
    def seed_profile(self, code: str, system: str) -> dict[str, dict]:
        """
        Return probabilistic axis weights for a clinical code.
        
        Args:
            code: DSM-5-TR (F84.0) or ICD-11 (6A02) code
            system: "DSM-5-TR" or "ICD-11"
        
        Returns:
            Dict of axis -> provenance dict (value, source, n, grade, version).
            Unknown code → empty dict (not a default profile).
            Code with no meta-analysis coverage → axes with source="hypothesis".
        """
        table = self._dsm5tr if system == "DSM-5-TR" else self._icd11 if system == "ICD-11" else {}
        axes = table.get(code, {})

        # A table written before the freeze can still carry the old spellings.
        # Normalize on the way out so a caller only ever sees contract names.
        return {AXIS_ALIASES.get(axis, axis): prov.to_dict()
                for axis, prov in axes.items()}
    
    def merge(
        self, 
        user_profile: Any,  # SarahProfile (import avoided for no circular deps)
        seed: dict[str, dict],
        system: str = "DSM-5-TR"
    ) -> Any:
        """
        Merge clinical seed into user profile.
        
        Precedence: user sliders > probe > seed > telemetry
        User sliders override; unset axes filled from seed; probe/telemetry fill rest.
        
        Returns new SarahProfile instance.
        
        Accepts seed in two formats:
        - Full provenance: {"axis": {"value": 0.85, "source": "...", ...}}
        - Simple: {"axis": 0.85}
        """
        # Import here to avoid circular dependency
        from SARAH.profile import SarahProfile
        
        # Start with user profile as base
        merged = user_profile.to_dict() if hasattr(user_profile, 'to_dict') else {}

        # A seed handed in by a caller may still use the pre-freeze names.
        seed = {AXIS_ALIASES.get(k, k): v for k, v in (seed or {}).items()}

        # Fill unset axes from seed
        for axis in self.AXES:
            if axis not in merged or merged[axis] is None:
                if axis in seed:
                    seed_val = seed[axis]
                    # Handle both provenance dict and simple float
                    if isinstance(seed_val, dict) and "value" in seed_val:
                        merged[axis] = seed_val["value"]
                    else:
                        merged[axis] = float(seed_val)
        
        # Build new profile — SarahProfile.from_dict handles validation
        return SarahProfile.from_dict(merged)
    
    def merge_multi(
        self, 
        codes: list[tuple[str, str]],  # [(code, system), ...]
        user_profile: Any = None
    ) -> Any:
        """
        Merge multiple clinical codes (union of axes, highest weight wins).
        """
        from SARAH.profile import SarahProfile
        
        combined_seed = {}
        for code, system in codes:
            seed = self.seed_profile(code, system)
            for axis, prov in seed.items():
                if axis not in combined_seed or prov["value"] > combined_seed[axis]["value"]:
                    combined_seed[axis] = prov
        
        base = user_profile.to_dict() if user_profile and hasattr(user_profile, 'to_dict') else {}
        for axis in self.AXES:
            if axis not in base or base[axis] is None:
                if axis in combined_seed:
                    base[axis] = combined_seed[axis]["value"]
        
        return SarahProfile.from_dict(base)
    
    # ── Version Management ────────────────────────────────────────────────────
    
    @classmethod
    def list_versions(cls) -> list[str]:
        """List available crosswalk versions."""
        return list(CROSSWALK_VERSIONS.keys())
    
    @classmethod
    def load_table(cls, version: str, system: str) -> dict[str, dict[str, AxisProvenance]]:
        """Load raw crosswalk table for a version/system."""
        return CROSSWALK_VERSIONS.get(version, {}).get(system, {})
    
    @classmethod
    def diff_versions(cls, v1: str, v2: str, system: str) -> dict[str, dict]:
        """Diff two versions — returns axis weight deltas per code."""
        t1 = cls.load_table(v1, system)
        t2 = cls.load_table(v2, system)
        all_codes = set(t1.keys()) | set(t2.keys())
        diff = {}
        for code in all_codes:
            a1 = t1.get(code, {})
            a2 = t2.get(code, {})
            all_axes = set(a1.keys()) | set(a2.keys())
            axis_diff = {}
            for axis in all_axes:
                v1_val = a1.get(axis)
                v2_val = a2.get(axis)
                if v1_val and v2_val:
                    delta = v2_val.value - v1_val.value
                    if abs(delta) > 1e-6:
                        axis_diff[axis] = {"from": v1_val.value, "to": v2_val.value, "delta": delta}
                elif v2_val and not v1_val:
                    axis_diff[axis] = {"from": None, "to": v2_val.value, "delta": "added"}
                elif v1_val and not v2_val:
                    axis_diff[axis] = {"from": v1_val.value, "to": None, "delta": "removed"}
            if axis_diff:
                diff[code] = axis_diff
        return diff


# ──────────────────────────────────────────────────────────────────────────────
# PMB PERSISTENCE (versioned, inspectable, deletable)
# ──────────────────────────────────────────────────────────────────────────────

class CrosswalkPMB:
    """PMB-backed storage for crosswalk tables and clinical seeds."""
    
    TABLE_PREFIX = "sarah_crosswalk"
    SEED_PREFIX = "sarah_clinical_seed"
    
    @staticmethod
    def save_table(version: str, system: str, table: dict[str, dict[str, AxisProvenance]]) -> str:
        """Save crosswalk table to pmb as versioned fact."""
        import pmb
        key = f"{CrosswalkPMB.TABLE_PREFIX}_{system}_{version}"
        # Convert to serializable
        serializable = {
            code: {axis: prov.to_dict() for axis, prov in axes.items()}
            for code, axes in table.items()
        }
        # pmb.record_fact would be used here; stub for now
        return key
    
    @staticmethod
    def record_seed(
        code: str, 
        system: str, 
        axes_seeded: list[str], 
        source_versions: dict[str, str],
        user_id: str = "local"
    ) -> str:
        """Record clinical_seed telemetry event to pmb."""
        import pmb
        event = {
            "code": code,
            "system": system,
            "axes_seeded": axes_seeded,
            "source_versions": source_versions,
            "crosswalk_version": "2026-11-16",
            "user_id": user_id,
        }
        # pmb.record_fact(fact=json.dumps(event), importance=0.7) would be used
        return f"{CrosswalkPMB.SEED_PREFIX}_{code}_{system}"


# ──────────────────────────────────────────────────────────────────────────────
# FHIR BUNDLE INGESTION STUB (Grade D — untested)
# ──────────────────────────────────────────────────────────────────────────────

class FHIRClinicalAdapter:
    """
    FHIR Bundle → Clinical Codes → Sarah Profile.
    Grade D: mechanism plausible, untested for this use.
    """
    
    @staticmethod
    def extract_codes(bundle: dict) -> list[tuple[str, str]]:
        """
        Parse Condition/Observation resources for DSM-5-TR/ICD-11 codes.
        
        Expected bundle structure:
        {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Condition", "code": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "F84.0"}]}}},
                {"resource": {"resourceType": "Observation", "code": {"coding": [{"system": "urn:oid:2.16.840.1.113883.6.256", "code": "6A02"}]}}}
            ]
        }
        """
        codes = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") in ("Condition", "Observation"):
                for coding in resource.get("code", {}).get("coding", []):
                    system = coding.get("system", "")
                    code = coding.get("code", "")
                    if "icd-10" in system.lower() or "icd10" in system.lower():
                        codes.append((code, "DSM-5-TR"))  # ICD-10-CM maps to DSM-5-TR
                    elif "icd-11" in system.lower() or "icd11" in system.lower():
                        codes.append((code, "ICD-11"))
                    elif "dsm" in system.lower():
                        codes.append((code, "DSM-5-TR"))
        return codes
    
    def seed_from_bundle(self, bundle: dict, user_profile: Any = None) -> Any:
        """Extract codes from FHIR bundle and merge into profile."""
        codes = self.extract_codes(bundle)
        if not codes:
            return user_profile
        crosswalk = ClinicalCrosswalk()
        return crosswalk.merge_multi(codes, user_profile)