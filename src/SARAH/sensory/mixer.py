"""
M3 — Sensory Gain Mixer with one global contract (B2, lane 2)

One master intensity control scales **every** modality together; per-modality
trims sit underneath it. The contract's teeth clause is the declaration rule: a
sensory feature must declare its default here **before it ships**, and a
modality nobody declared cannot be read or driven — a feature that cannot be
turned down does not land.

Two behaviours are real rather than documented:

* `mute_non_critical()` implements XAUR REQ 3b — everything is muted except the
  critical set. It is reversible, and it never mutes the critical set, because
  a muted instruction the user needs in order to leave is not "less intensity".
* `level()` is the only read path, and it is always `master * trim`, so a new
  feature cannot ship with its own independent volume that the master misses.

No I/O, no clock, no model call: this is a value surface a renderer reads.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MIN_GAIN = 0.0
MAX_GAIN = 1.0

DEFAULT_MASTER = 0.6
"""Shipped default is the calm one, not full intensity."""

DEFAULT_TRIMS: dict[str, float] = {
    "audio": 0.8,
    "visual": 0.7,
    "haptic": 0.5,
    "motion": 0.6,
    "text": 1.0,
}
"""Declared defaults, in gain units, before the master scales them.

`text` ships at 1.0 because legibility is a floor rather than an effect: the
master may still turn it down, but the trim does not start quieter than full.
"""

CRITICAL_MODALITIES: tuple[str, ...] = ("text",)
"""Modalities `mute_non_critical()` (XAUR REQ 3b) leaves at their configured level.

Deliberately small and explicit: the set is the channels a user needs in order
to understand where they are and how to leave.
"""


class InvalidGain(ValueError):
    """A gain outside [0, 1]. A gain is authored, so it is refused, not clamped."""


class UndeclaredModality(KeyError):
    """A modality with no declared default — the feature may not ship."""

    def __str__(self) -> str:  # KeyError would quote-wrap the message
        return str(self.args[0]) if self.args else "undeclared modality"


@dataclass
class Mixer:
    """One master gain, per-modality trims, and a declaration register.

    `master` is the single control the user is offered. `trims` are authored
    per feature, and every read goes through `level()`, which multiplies the
    two — there is no second path by which a modality escapes the master.
    """

    master: float = DEFAULT_MASTER
    trims: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_TRIMS))
    _muted: frozenset[str] = field(default_factory=frozenset, init=False, repr=False)

    def __post_init__(self) -> None:
        self._check(self.master, "master")
        for modality, value in dict(self.trims).items():
            self._check(value, modality)

    # -- validation ---------------------------------------------------------

    @staticmethod
    def _check(value: float, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidGain(f"{name} must be a number in [0, 1], got {value!r}")
        if not MIN_GAIN <= float(value) <= MAX_GAIN:
            raise InvalidGain(f"{name} must be in [0, 1], got {value!r}")

    def _require(self, modality: str) -> float:
        if modality not in self.trims:
            raise UndeclaredModality(
                f"{modality!r} has no declared default; declare it before shipping "
                f"the feature (declared: {sorted(self.trims)})"
            )
        return float(self.trims[modality])

    # -- declaration register ----------------------------------------------

    def declare(self, modality: str, default: float) -> None:
        """Register a feature's default gain. Required before its first use."""
        self._check(default, modality)
        self.trims[modality] = float(default)

    def declared(self) -> tuple[str, ...]:
        """Every modality that may be driven, in stable order."""
        return tuple(sorted(self.trims))

    def is_declared(self, modality: str) -> bool:
        return modality in self.trims

    # -- control ------------------------------------------------------------

    def set_master(self, value: float) -> float:
        """Set the one global control. Out of range is refused, never clamped."""
        self._check(value, "master")
        self.master = float(value)
        return self.master

    def set_trim(self, modality: str, value: float) -> float:
        """Set one modality's trim; the modality must already be declared."""
        self._require(modality)
        self._check(value, modality)
        self.trims[modality] = float(value)
        if modality in self._muted:
            # Setting a trim on a muted modality un-mutes it: the caller just
            # asked for a level, and silently holding it at zero would make the
            # write unobservable.
            self._muted = frozenset(m for m in self._muted if m != modality)
        return self.trims[modality]

    def level(self, modality: str) -> float:
        """Effective gain: master times trim, or 0.0 while muted."""
        trim = self._require(modality)
        if modality in self._muted:
            return 0.0
        return round(self.master * trim, 6)

    def levels(self) -> dict[str, float]:
        """Effective gain for every declared modality."""
        return {modality: self.level(modality) for modality in self.declared()}

    # -- XAUR REQ 3b --------------------------------------------------------

    def mute_non_critical(self) -> dict[str, float]:
        """Mute every modality outside `CRITICAL_MODALITIES`; return the result."""
        muted = tuple(m for m in self.declared() if m not in CRITICAL_MODALITIES)
        self._muted = frozenset(muted)
        return self.levels()

    def unmute(self) -> dict[str, float]:
        """Restore every muted modality to `master * trim`."""
        self._muted = frozenset()
        return self.levels()

    # -- clinical seed (M16) ------------------------------------------------

    N_FACTOR_GAIN_FLOOR = 0.15
    """Quietest master an N factor may drive the gain to — never silence."""

    def master_gain_from_N_factor(self, n_factor: float | None = None) -> float:
        """Master gain for a neurodevelopmental spectrum factor (M16, reduce-only).

        A higher N means more sensory load from the same stimulus, so gain only
        falls. It can never rise above the current master, and it floors at
        `N_FACTOR_GAIN_FLOOR` because "less intensity" must not become "nothing
        on screen".
        """
        if n_factor is None:
            return float(self.master)
        if isinstance(n_factor, bool) or not isinstance(n_factor, (int, float)):
            raise InvalidGain(f"n_factor must be a number in [0, 1], got {n_factor!r}")
        if not 0.0 <= float(n_factor) <= 1.0:
            raise InvalidGain(f"n_factor must be in [0, 1], got {n_factor!r}")
        return max(self.N_FACTOR_GAIN_FLOOR, float(self.master) * (1.0 - 0.6 * float(n_factor)))

    def apply_N_factor(self, n_factor: float | None = None) -> float:
        """Set the master from an N factor and return it."""
        self.set_master(self.master_gain_from_N_factor(n_factor))
        return self.master

    def muted(self) -> tuple[str, ...]:
        return tuple(sorted(self._muted))

    # -- serialisation ------------------------------------------------------

    def to_dict(self) -> dict[str, object]:
        return {
            "master": self.master,
            "trims": dict(sorted(self.trims.items())),
            "muted": sorted(self._muted),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Mixer":
        trims = data.get("trims") or {}
        if not isinstance(trims, dict):
            raise InvalidGain(f"trims must be a mapping, got {type(trims)!r}")
        mixer = cls(master=float(data.get("master", DEFAULT_MASTER)), trims=dict(trims))
        muted = data.get("muted") or ()
        unknown = [m for m in muted if m not in mixer.trims]
        if unknown:
            raise UndeclaredModality(f"muted modality not declared: {unknown}")
        mixer._muted = frozenset(muted)
        return mixer
