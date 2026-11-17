"""
M16 Clinical Integration Adapter — DSM-5-TR / ICD-11 → Sarah 8-axis Profile Crosswalk

Exports:
- ClinicalCrosswalk: main crosswalk class
- FHIRClinicalAdapter: FHIR bundle ingestion stub (Grade D)
- CrosswalkPMB: PMB persistence layer
"""

from .crosswalk import ClinicalCrosswalk, FHIRClinicalAdapter, CrosswalkPMB, AxisProvenance

__all__ = [
    "ClinicalCrosswalk",
    "FHIRClinicalAdapter", 
    "CrosswalkPMB",
    "AxisProvenance",
]

__version__ = "2026-11-16"