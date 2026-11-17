"""
M8, M9, M12-M14 — Affect Core (Lane 3)

B3: Interoception Bridge (M8), Affirmation Engine (M14)
B4: Time Scaffolding (M9), Masking-Load Meter (M12), Companion Contract (M13)
"""
from __future__ import annotations

# M8 - Interoception Bridge
from .interocept import Interocept, BodySignal, InteroceptVocabulary

# M9 - Time Scaffolding
from .timeview import TimeView, TimeRibbon, TimeUnit, RibbonStyle, remaining_ribbon, create_time_view

# M12 - Masking-Load Meter
from .load import LoadMeter, LoadEvent, SessionLoad, LoadDomain, create_load_meter, quick_should_stop

# M13 - Companion Contract
from .companion import Companion, SessionCap, CompanionSession, ReplyVerdict, create_companion, quick_allowed_reply

# M14 - Affirmation Engine
from .affirmation import AffirmationEngine, ValueStatement, AffirmationMode, create_affirmation_engine, quick_affirm

__all__ = [
    # M8 - Interoception Bridge
    "Interocept",
    "BodySignal",
    "InteroceptVocabulary",
    # M9 - Time Scaffolding
    "TimeView",
    "TimeRibbon",
    "TimeUnit",
    "RibbonStyle",
    "remaining_ribbon",
    "create_time_view",
    # M12 - Masking-Load Meter
    "LoadMeter",
    "LoadEvent",
    "SessionLoad",
    "LoadDomain",
    "create_load_meter",
    "quick_should_stop",
    # M13 - Companion Contract
    "Companion",
    "SessionCap",
    "CompanionSession",
    "ReplyVerdict",
    "create_companion",
    "quick_allowed_reply",
    # M14 - Affirmation Engine
    "AffirmationEngine",
    "ValueStatement",
    "AffirmationMode",
    "create_affirmation_engine",
    "quick_affirm",
]