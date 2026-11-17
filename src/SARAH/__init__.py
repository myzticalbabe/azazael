"""
Project Sarah — Neurodivergent Immersion Engine

Build: B0-B9 per docs/SARAH_BUILD_INSTRUCTIONS_2026-11-16.md
Target: Python 3.16t free-threaded (py316t)
"""

__version__ = "2026-11-16"

# Core substrate (B1)
from .profile import SarahProfile, ProfileStore, Preview, ExitPort, ExitTicket, AXES

# Exit-Anywhere (B1, M7) — the named surface B1 states; delegates to profile.ExitPort
from .exit import assert_unscored, reachable_in_one_action, request

# Executive function (B4)
from .offload import Card, Offload, Step
from .initiate import Invitation, Initiate

# Sensory substrate (B2, B6)
from .sensory import Mixer, Pacing, Redundancy, Timer, Transitions

# Affect core (B3, B4, B5)
from .affect import (
    AffirmationEngine,
    Companion,
    Interocept,
    LoadMeter,
    TimeView,
)

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
    # Exit-Anywhere (M7)
    "request",
    "assert_unscored",
    "reachable_in_one_action",
    # Executive function (B4)
    "Offload",
    "Card",
    "Step",
    "Initiate",
    "Invitation",
    # Sensory (M2-M5, M15)
    "Mixer",
    "Pacing",
    "Redundancy",
    "Timer",
    "Transitions",
    # Affect (M8, M9, M12-M14)
    "AffirmationEngine",
    "Companion",
    "Interocept",
    "LoadMeter",
    "TimeView",
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