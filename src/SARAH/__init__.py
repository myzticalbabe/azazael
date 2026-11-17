"""
Project Sarah — Neurodivergent Immersion Engine

Build: B0-B9 per docs/SARAH_BUILD_INSTRUCTIONS_2026-11-16.md
Target: Python 3.16t free-threaded (py316t)
"""

__version__ = "2026-11-16"

# Core substrate (B1)
from .profile import SarahProfile, ProfileStore, Preview, ExitPort, ExitTicket, AXES

# Executive function (B4)
from .offload import Card, Offload, Step
from .initiate import Invitation, Initiate

# Sensory substrate (B2) - to be implemented
# from .sensory import Mixer, Transitions, Pacing, Timer, Redundancy

# Affect core (B3) - to be implemented  
# from .affect import Interocept, Affirmation, TimeView, LoadMeter, Companion

# Clinical integration (B8)
from .clinical import ClinicalCrosswalk, FHIRClinicalAdapter, CrosswalkPMB, AxisProvenance

# Telemetry (B7)
from .telemetry import (
    EVENTS,
    SarahEvent,
    TelemetrySink,
    emit_profile_set,
    emit_demand_change,
    emit_exit_requested,
    emit_pause,
    emit_resume,
    emit_affirmation,
    emit_session_end,
    emit_clinical_seed,
    get_session_events,
)

__all__ = [
    # Profile
    "SarahProfile",
    "ProfileStore", 
    "Preview",
    "ExitPort",
    "ExitTicket",
    "AXES",
    # Executive function (B4)
    "Offload",
    "Card",
    "Step",
    "Initiate",
    "Invitation",
    # Clinical
    "ClinicalCrosswalk",
    "FHIRClinicalAdapter",
    "CrosswalkPMB",
    "AxisProvenance",
    # Telemetry
    "EVENTS",
    "SarahEvent",
    "TelemetrySink",
    "emit_profile_set",
    "emit_demand_change",
    "emit_exit_requested",
    "emit_pause",
    "emit_resume",
    "emit_affirmation",
    "emit_session_end",
    "emit_clinical_seed",
    "get_session_events",
]