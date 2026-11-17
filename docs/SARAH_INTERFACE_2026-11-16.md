# Sarah Cognitive Profile — Frozen Interface Contract (B1)

**Frozen at:** 2026-11-17  
**HEAD:** `00101b49`  
**Authority:** Lane 1 (kilo) — sole execution authority for B1  
**Blocks:** Lane 2 (freebuff sensory), Lane 3 (opencode affect), Lane 4 (clinical)  
**Expiry:** 2026-11-21 — re-derive before starting if past this date

---

## Contract: `SarahProfile` (aliased as `Profile`)

The **frozen eight axes** in contract order (`AXES`):

| index | axis | range | low meaning | high meaning | source precedence |
|-------|------|-------|-------------|--------------|-------------------|
| 0 | `sensory_gain` | [0, 1] | low | high | user > probe > telemetry > clinical_seed |
| 1 | `processing_speed` | [0, 1] | slow | fast | user > probe > telemetry > clinical_seed |
| 2 | `attention_span` | [0, 1] | short | long | user > probe > telemetry > clinical_seed |
| 3 | `interoception` | [0, 1] | low | high | user > probe > telemetry > clinical_seed |
| 4 | `masking_load` | [0, 1] | low | high | user > probe > telemetry > clinical_seed |
| 5 | `recovery_latency` | [0, 1] | fast | slow | user > probe > telemetry > clinical_seed |
| 6 | `initiation_cost` | [0, 1] | low | high | user > probe > telemetry > clinical_seed |
| 7 | `prediction_need` | [0, 1] | low | high | user > probe > telemetry > clinical_seed |

**Extended axes** (outside freeze, declared not hidden):
- `wm_span` — working memory span (small → large)
- `time_discrimination` — time perception (poor → good)

**Pre-freeze aliases** (resolved on input):
- `sustained_attention` → `attention_span`
- `interoceptive_accuracy` → `interoception`
- `initiation_threshold` → `initiation_cost`

**Unknown axis contract:** Returns `None` from `canonical_axis()`; `explain()` says "not measured yet" — never silently 0.5.

---

## Public API (frozen — lanes 2, 3, 4 code against this)

```python
from SARAH.profile import SarahProfile, AXES, ALL_AXES, AXIS_MEANING, canonical_axis, Profile

# Type alias (contract name)
Profile = SarahProfile

# Frozen eight axes in contract order
AXES: tuple[str, ...]  # 8 items, order = contract order

# All axes this build carries (frozen + extended)
ALL_AXES: tuple[str, ...]  # AXES + ("wm_span", "time_discrimination")

# Human-readable meaning per axis
AXIS_MEANING: dict[str, tuple[str, str]]  # axis -> (low_label, high_label)

# Resolve alias or canonical name to contract field; None if unknown
canonical_axis(name: str) -> str | None

# Core type
@dataclass
class SarahProfile:
    # Frozen eight (None = not measured)
    sensory_gain: float | None
    processing_speed: float | None
    attention_span: float | None
    interoception: float | None
    masking_load: float | None
    recovery_latency: float | None
    initiation_cost: float | None
    prediction_need: float | None
    
    # Extended (outside freeze)
    wm_span: float | None
    time_discrimination: float | None
    
    # Validation: all values in [0, 1] or None
    def __post_init__(self): ...
    
    # Deterministic construction from signals
    @classmethod
    def from_signals(cls, signals: dict[str, float | None], source: str = "probe") -> SarahProfile: ...
    
    # Merge from dict (resolves aliases)
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SarahProfile: ...
    
    # Export all axes (frozen + extended)
    def to_dict(self) -> dict[str, float | None]: ...
    
    # Human-readable explanation
    def explain(self, axis: str) -> str: ...
    
    # Frozen eight names in contract order
    def axes(self) -> list[str]: ...
    
    # Frozen + extended
    def all_axes(self) -> list[str]: ...

# Source precedence for merging
SOURCE_PRECEDENCE: tuple[str, ...] = ("user", "probe", "telemetry", "clinical_seed")
```

---

## Validation Rules (enforced in `__post_init__`)

1. Every axis value is `float | None`
2. Non-None values must be in `[0.0, 1.0]`
3. Type error raised for non-numeric values
4. Value error raised for out-of-range values

---

## Acceptance Commands (each prints its own result)

```bash
# 1. Import and basic instantiation
PY=C:/Azazael/.venvs/py316t/Scripts/python.exe
$PY -c "from SARAH.profile import SarahProfile, AXES; p=SarahProfile(); print(len(AXES), p.axes())"   # 8, 8 axes

# 2. Validation rejects out-of-range
$PY -c "from SARAH.profile import SarahProfile; SarahProfile(sensory_gain=1.5)"   # ValueError

# 3. Validation rejects wrong type
$PY -c "from SARAH.profile import SarahProfile; SarahProfile(sensory_gain='high')"   # TypeError

# 4. None is accepted (not measured)
$PY -c "from SARAH.profile import SarahProfile; p=SarahProfile(sensory_gain=None); print(p.explain('sensory_gain'))"   # "not measured yet"

# 5. Alias resolution
$PY -c "from SARAH.profile import canonical_axis; print(canonical_axis('sustained_attention'))"   # attention_span

# 6. Unknown axis returns None
$PY -c "from SARAH.profile import canonical_axis; print(canonical_axis('unknown_axis'))"   # None

# 7. from_signals works
$PY -c "from SARAH.profile import SarahProfile; p=SarahProfile.from_signals({'sensory_gain': 0.8, 'attention_span': 0.6}, source='probe'); print(p.to_dict())"

# 8. from_dict resolves aliases
$PY -c "from SARAH.profile import SarahProfile; p=SarahProfile.from_dict({'sustained_attention': 0.7}); print(p.attention_span)"   # 0.7

# 9. to_dict includes extended axes
$PY -c "from SARAH.profile import SarahProfile; p=SarahProfile(wm_span=0.5); print('wm_span' in p.to_dict())"   # True

# 10. Profile alias works
$PY -c "from SARAH.profile import Profile; print(Profile is SarahProfile)"   # True
```

All 10 commands must print success (exit 0) for B1 to be FROZEN.

---

## Test File: `tests/test_sarah_profile.py`

Must contain tests for:
- AXES length and order
- Validation (range, type)
- `canonical_axis` alias resolution
- `from_signals`, `from_dict`, `to_dict`
- `explain` output format
- `Profile` alias
- Extended axes present in `to_dict`
- Unknown axis handling