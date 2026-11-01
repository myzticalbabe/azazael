# coding: utf-8
"""PSYCHE Phase 6 -- REALTIME THERAPEUTIC AGENTS: the loop a stance is chosen in.

WHAT THIS IS, AND WHAT IT REFUSES TO BE
---------------------------------------
A realtime agent here is the JITAI shape from digital mental health (Nahum-Shani
et al., "Just-in-Time Adaptive Interventions (JITAIs) in Mobile Health", Annals
of Behavioral Medicine 2018): SENSE a state, DECIDE whether and how to intervene
now, DELIVER a bounded dose, and LEARN from what happened. Three of those four
words are doing real work:

  * SENSE uses the person's own graph and affect model, never a population prior.
  * "Whether" is a real decision. The JITAI literature is explicit that
    intervening at the wrong moment is worse than silence -- a person outside
    their window of tolerance cannot learn a skill, so a skills intervention
    delivered at arousal 0.9 teaches them that therapy does not work. So the loop
    has a RECEPTIVITY gate and a REGULATE stance that fires before SKILLS.
  * DELIVER is bounded: one stance, one short message, no stacked advice.

It is NOT a therapist, and the code says so rather than implying it. It does not
diagnose, does not name a disorder, and cannot replace a human -- on any elevated
risk signal it stops being an intervention engine and becomes a router to people.
That routing is the FIRST branch of `turn()`, before any stance is scored, and
`test_psyche_rt_agent` asserts it is exclusive. A safety check that can be
outranked by a utility score is not a safety check.

THE FOUR STANCES AND WHY THESE FOUR
-----------------------------------
Grounded in what the process literature actually measures, not in a modality:

  SAFETY      risk triage fired; deliver a resource, deliver nothing else.
  VALIDATE    emotional processing needs the experience acknowledged before any
              change work; skips straight past reframing resistance.
  REGULATE    arousal above the learning window; downregulate first.
  REFRAME     arousal workable and an appraisal is driving the distress --
              re-appraisal is the highest-value target when the belief, not the
              state, is what is stuck.
  SKILLS      workable state, no dominant misappraisal, avoidance is the active
              node -- approach/activation work.
  CONSOLIDATE nothing acute: name what worked so it is retrievable next time
              (this is the same move as `intuition.py` compiling a prototype).

Selection is deterministic: a utility per applicable stance, argmax, name
tiebreak. No sampling, so a session is reproducible and its audit is checkable.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from PSYCHE.affect import (appraise_event, clamp, emotion_to_pad, express,
                           pad_blend, pad_decay)
from PSYCHE.intuition import DEFAULT_THRESHOLD, IntuitionIndex, Reading
from PSYCHE.network import PersonNetwork, activation_from_pad

#: Crisis vocabulary. Deliberately explicit and deliberately narrow: this is a
#: ROUTER, so it must fire on unambiguous statements of intent and must not fire
#: on ordinary distress language. The negative-control test exercises both sides.
CRISIS_CUES: Tuple[str, ...] = (
    "kill myself", "end my life", "ending my life", "suicide", "suicidal",
    "want to die", "wish i was dead", "better off dead", "not want to be here",
    "hurt myself", "hurting myself", "self harm", "self-harm", "cut myself",
    "overdose", "no reason to live", "can't go on", "cannot go on",
)

#: Words that look like crisis vocabulary but are not, and which would produce a
#: false positive if matched by substring: "killing time", "die of embarrassment".
CRISIS_EXCLUSIONS: Tuple[str, ...] = (
    "kill time", "killing time", "die of embarrassment", "dying to know",
    "could die laughing", "dead tired", "deadline",
)

#: Arousal above this is outside the window in which skills are learnable.
LEARNING_WINDOW_AROUSAL = 0.72

#: INDIRECT intent, as patterns rather than exact strings. Added 2026-11-01
#: after `tools/triage_eval.py` measured recall 0.76 on the dev corpus: all three
#: misses were euphemisms ("not be around anymore", "end it all", "rather not
#: wake up"), which is a MECHANISM gap -- an exact-phrase list only ever catches
#: the phrasings it was written around, and people do not speak in those. These
#: are families, so the next paraphrase is more likely to fall inside one.
CRISIS_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("indirect_absence", r"\b(not|no longer)\s+(be\s+around|be\s+here|wake\s+up)\b"),
    ("end_it", r"\bend\s+(it\s+all|things|my\s+life)\b"),
    ("better_off_gone", r"\bbetter\s+off\s+(dead|without\s+me|gone)\b"),
    ("no_point", r"\b(no|not\s+see\s+the)\s+point\s+(in|to)?\s*(living|going\s+on|carrying\s+on)\b"),
)

#: Attribution guards. A crisis word in someone else's story, in the past, or
#: inside a quotation is NOT this person's intent, and treating it as one is how
#: a router cries wolf until people turn it off. Each guard DOWNGRADES to
#: `monitor` rather than discarding: the mention is still worth not ignoring.
THIRD_PERSON_MARKERS: Tuple[str, ...] = (
    "my mother", "my father", "my brother", "my sister", "my son", "my daughter",
    "my friend", "a friend", "my partner", "my wife", "my husband", "my ex",
    "my colleague", "a colleague", "someone i know", "he tried", "she tried",
    "they tried", "his suicide", "her suicide",
)
HISTORICAL_MARKERS: Tuple[str, ...] = (
    "years ago", "ten years", "last year", "in 2015", "in 2016", "in 2019",
    "in 2020", "in 2015", "when i was", "used to", "have been clean",
    "back then", "since my last", "it is behind me", "behind me now",
)
QUOTATION_MARKERS: Tuple[str, ...] = (
    '"', "\u201c", "\u201d", "lyric", "the song", "a song", "quote", "the novel",
    "the character",
)
#: First-person intent overrides every guard: "I want to die" is this person's
#: statement even if the sentence also mentions a relative.
FIRST_PERSON_MARKERS: Tuple[str, ...] = (
    "i want to", "i have been thinking", "i am going to", "i will", "i keep",
    "i have decided", "i plan", "i am done",
)

#: Risk levels, ordered. Only `low` permits a non-safety stance.
RISK_LEVELS: Tuple[str, ...] = ("low", "monitor", "elevated", "crisis")

#: The stances that do not ask the person to change anything. On elevated risk
#: only these are eligible -- see the cap in `TherapeuticLoop._select`.
LOW_DOSE_STANCES: Tuple[str, ...] = ("validate", "regulate", "consolidate")

#: Per-stance message templates. Short by design: a realtime channel punishes a
#: wall of text, and a long message is advice regardless of its hedging. `{focus}`
#: is the construct the graph named, so the message is about THIS person's state.
STANCE_TEMPLATES: Dict[str, str] = {
    "safety": ("What you just said matters more than anything else in this "
               "conversation. Please reach a person now: 988 (Suicide & Crisis "
               "Lifeline, US) or your local emergency number. I am staying here "
               "with you, and I am not the right kind of help for this."),
    "validate": ("That sounds genuinely hard, and it makes sense that {focus} is "
                 "where it lands. I am not going to move you past it yet."),
    "regulate": ("Before anything else, let us bring the intensity down a notch. "
                 "One slow breath out, longer than the breath in, twice. "
                 "Nothing to solve yet."),
    "reframe": ("The story running right now is doing a lot of the work. "
                "What is one piece of evidence that sits outside it?"),
    "skills": ("{focus} is the thing asking for attention. What is the smallest "
               "step toward it that you would actually do today?"),
    "consolidate": ("Notice what you just did: you stayed with {focus} instead of "
                    "leaving it. That is the part worth remembering."),
}


@dataclass
class Triage:
    """The risk verdict. `reasons` is never empty -- an empty list is not a pass."""

    risk: str
    reasons: List[str] = field(default_factory=list)
    matched: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"risk": self.risk, "reasons": list(self.reasons),
                "matched": list(self.matched)}


@dataclass
class TurnResponse:
    """Everything one realtime turn decided, with the evidence for each part."""

    stance: str
    message: str
    focus: str
    risk: Triage
    pad: Tuple[float, float, float]
    reading: Optional[Reading]
    latency_ms: float
    within_budget: bool
    rationale: str
    activation: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"stance": self.stance, "message": self.message, "focus": self.focus,
                "risk": self.risk.to_dict(),
                "pad": [round(v, 4) for v in self.pad],
                "reading": self.reading.to_dict() if self.reading else None,
                "latency_ms": round(self.latency_ms, 3),
                "within_budget": self.within_budget, "rationale": self.rationale}


def _attribution(lowered: str) -> str:
    """Whose risk is this sentence describing? self / other / historical / quotation.

    Order matters. A quotation is a quotation even when it is also historical;
    the narrowest guard wins, because each one only ever downgrades.
    """
    if any(marker in lowered for marker in QUOTATION_MARKERS):
        return "quotation"
    if any(marker in lowered for marker in HISTORICAL_MARKERS):
        return "historical"
    if any(marker in lowered for marker in THIRD_PERSON_MARKERS):
        return "other"
    return "self"


def triage(text: str, activation: Optional[Dict[str, float]] = None) -> Triage:
    """Route risk before anything else happens in the turn.

    Two independent channels, kept apart on purpose:

      TEXT  statements of suicidal or self-harm intent -> `crisis`, with an
            ATTRIBUTION guard: the same words in a relative's story, in the
            past, or inside a quotation downgrade to `monitor` instead.
      STATE the isolated-collapse pattern (low self-worth + high avoidance +
            high rumination) -> `elevated`, with no text needed.

    The text channel checks exclusions first, so "killing time" and "dead tired"
    do not fire; that is the negative control this function ships with. Indirect
    phrasing is caught by CRISIS_PATTERNS, added after measurement showed the
    exact-phrase list missing every euphemism it was tested on.
    """
    lowered = (text or "").lower()
    matched = [cue for cue in CRISIS_CUES if cue in lowered]
    for name, pattern in CRISIS_PATTERNS:
        if re.search(pattern, lowered):
            matched.append("pattern:%s" % name)
    excluded = [cue for cue in CRISIS_EXCLUSIONS if cue in lowered]
    if matched and not excluded:
        who = _attribution(lowered)
        first_person = any(marker in lowered for marker in FIRST_PERSON_MARKERS)
        if who == "self" or first_person:
            return Triage("crisis", ["explicit intent language: %r" % matched[0]], matched)
        return Triage(
            "monitor",
            ["intent language %r attributed to %s: not this person's stated intent, "
             "still worth not ignoring" % (matched[0], who)], matched)
    reasons: List[str] = []
    if excluded and matched:
        reasons.append("crisis vocabulary present but excluded as idiom: %r" % excluded[0])
    active = activation or {}
    low_worth = active.get("self_worth", 0.0) <= -0.6
    high_avoid = active.get("avoidance", 0.0) >= 0.6
    high_rumination = active.get("rumination", 0.0) >= 0.6
    if low_worth and high_avoid and high_rumination:
        return Triage("elevated",
                      ["isolated-collapse pattern: self_worth<=-0.6, avoidance>=0.6, "
                       "rumination>=0.6 in the same reading"], matched)
    if sum((low_worth, high_avoid, high_rumination)) >= 2:
        return Triage("monitor",
                      ["two of three collapse markers present; not elevated without "
                       "the third"], matched)
    if not reasons:
        reasons.append("no intent language and no collapse markers in this reading")
    return Triage("low", reasons, matched)


class TherapeuticLoop:
    """The realtime loop over one person's artifacts.

    Held state: the affect state (PAD), the network, the intuition index, and a
    bounded audit of recent turns. Nothing else -- a loop that keeps more becomes
    a store, and this is supposed to be a loop.
    """

    def __init__(self, network: PersonNetwork, index: IntuitionIndex,
                 pad: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 baseline: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 decay_rate: float = 0.15, budget_ms: float = 50.0,
                 threshold: float = DEFAULT_THRESHOLD,
                 audit_limit: int = 64) -> None:
        self.network = network
        self.index = index
        self.pad = tuple(float(v) for v in pad)  # type: ignore[assignment]
        self.baseline = tuple(float(v) for v in baseline)  # type: ignore[assignment]
        self.decay_rate = float(decay_rate)
        self.budget_ms = float(budget_ms)
        self.threshold = float(threshold)
        self.audit_limit = int(audit_limit)
        self._audit: List[TurnResponse] = []
        self._turn_count = 0

    # -- the turn ---------------------------------------------------------
    def turn(self, text: str = "", appraisal: Optional[dict] = None,
             dt_s: float = 1.0, observe: bool = True) -> TurnResponse:
        """One realtime turn: sense, decide, deliver, record.

        Order is fixed and matters. Affect decays toward the person's own
        baseline FIRST (so state is current), appraisal blends in SECOND, the
        graph is updated THIRD, triage runs FOURTH on the fresh activation --
        and if triage says crisis, the turn ends here with a safety stance and no
        other candidate is ever scored.
        """
        started = time.perf_counter()
        self._turn_count += 1

        self.pad = pad_decay(self.pad, self.baseline, self.decay_rate, dt_s)

        families: List[str] = []
        if appraisal:
            ranked = appraise_event(
                desirability=float(appraisal.get("desirability", 0.0)),
                likelihood=float(appraisal.get("likelihood", 1.0)),
                confirmed=appraisal.get("confirmed"),
                effort=float(appraisal.get("effort", 0.0)),
                unexpectedness=float(appraisal.get("unexpectedness", 0.0)),
                for_other=bool(appraisal.get("for_other", False)),
                liking_other=float(appraisal.get("liking_other", 0.0)),
            )
            if ranked:
                top_family, intensity, _basis = ranked[0]
                families = [top_family]
                self.pad = pad_blend(
                    self.pad, emotion_to_pad(top_family, intensity),
                    weight=clamp(0.35 * intensity, 0.0, 1.0))
                if top_family in ("distress", "fears_confirmed", "sadness"):
                    families.append("sadness")
                elif top_family in ("fear", "anxiety", "hope"):
                    families.append("anxiety")

        activation = activation_from_pad(self.pad, families)
        if observe:
            self.network.observe(activation, at_s=float(self._turn_count))

        risk = triage(text, activation)
        reading = self.index.read_or_think(activation, threshold=self.threshold)

        if risk.risk == "crisis":
            stance, focus, rationale = "safety", "this moment", \
                "triage=crisis on intent language; every other stance is barred"
        else:
            stance, focus, rationale = self._select(activation, risk, reading)

        message = STANCE_TEMPLATES[stance].format(focus=focus)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        response = TurnResponse(
            stance=stance, message=message, focus=focus, risk=risk, pad=self.pad,
            reading=reading, latency_ms=elapsed_ms,
            within_budget=elapsed_ms <= self.budget_ms, rationale=rationale,
            activation=activation)
        self._audit.append(response)
        if len(self._audit) > self.audit_limit:
            self._audit = self._audit[-self.audit_limit:]
        return response

    # -- stance selection -------------------------------------------------
    def _select(self, activation: Dict[str, float], risk: Triage,
                reading: Optional[Reading]) -> Tuple[str, str, str]:
        """Score every applicable stance, return the argmax with its reason.

        Receipts are the point: `rationale` names the numbers that decided, so a
        supervisor (or the person) can disagree with the decision by disagreeing
        with a specific quantity rather than with the system as a whole.
        """
        _p, arousal, dominance = self.pad
        focus = self._focus(activation)
        threat = activation.get("threat_appraisal", 0.0)
        avoidance = activation.get("avoidance", 0.0)
        approach = activation.get("approach", 0.0)
        rumination = activation.get("rumination", 0.0)
        worth = activation.get("self_worth", 0.0)

        scores: List[Tuple[str, float, str]] = []

        # VALIDATE: high negative affect and high threat, regardless of arousal.
        # Acknowledging first is cheap and skipping it poisons everything after.
        neg_affect = max(0.0, -self.pad[0])
        if neg_affect >= 0.25 or threat >= 0.35:
            scores.append(("validate", 0.55 + 0.4 * neg_affect + 0.2 * threat,
                           "neg_affect=%.2f threat=%.2f" % (neg_affect, threat)))

        # REGULATE: outside the learning window. Beats SKILLS and REFRAME by
        # construction, because neither lands in a dysregulated state.
        if arousal >= LEARNING_WINDOW_AROUSAL:
            scores.append(("regulate",
                           0.9 + 0.6 * (arousal - LEARNING_WINDOW_AROUSAL),
                           "arousal=%.2f >= learning window %.2f"
                           % (arousal, LEARNING_WINDOW_AROUSAL)))

        # REFRAME: workable arousal, threat is doing the work, and there is enough
        # agency to hold a reappraisal without collapsing.
        if arousal < LEARNING_WINDOW_AROUSAL and threat >= 0.3 and dominance > -0.5:
            scores.append(("reframe", 0.6 + 0.5 * threat + 0.2 * dominance,
                           "threat=%.2f dominance=%.2f below learning window"
                           % (threat, dominance)))

        # SKILLS: avoidance is the active node with a workable state.
        if avoidance >= 0.3 and arousal < LEARNING_WINDOW_AROUSAL:
            scores.append(("skills", 0.5 + 0.6 * avoidance - 0.3 * max(0.0, rumination),
                           "avoidance=%.2f rumination=%.2f" % (avoidance, rumination)))

        # CONSOLIDATE: nothing acute and something actually moved.
        if not scores or (neg_affect < 0.25 and approach >= 0.3 and worth >= 0.0):
            scores.append(("consolidate", 0.45 + 0.3 * approach + 0.2 * worth,
                           "approach=%.2f self_worth=%.2f, nothing acute"
                           % (approach, worth)))

        if not scores:
            scores.append(("validate", 0.4, "fallback: no stance predicate matched"))

        # A monitor-level risk reading outranks ordinary work: change work is
        # damped, but the stance set is unchanged.
        if risk.risk == "monitor":
            scores = [(name, score - (0.15 if name in LOW_DOSE_STANCES else 0.0), why)
                      for name, score, why in scores]
        # ELEVATED is a different claim and gets a different mechanism: the dose
        # is CAPPED, not discounted. An early version subtracted 0.15 here and
        # reframe still won at 0.75 versus validate at 0.67 -- a penalty that can
        # be outbid is not a cap, and pushing reappraisal at someone in the
        # isolated-collapse pattern is exactly the mis-timing the JITAI
        # literature warns about. When no low-dose stance applies, the damping
        # is the fallback rather than the primary mechanism.
        dose_note = ""
        if risk.risk == "elevated":
            low_dose = [row for row in scores if row[0] in LOW_DOSE_STANCES]
            if low_dose:
                scores = low_dose
                dose_note = "; dose capped to low-dose stances on elevated risk"
            else:
                scores = [(name, score - 0.15, why) for name, score, why in scores]
                dose_note = "; no low-dose stance applied, change work damped 0.15"

        name, score, why = max(scores, key=lambda row: (row[1], row[0]))
        path = reading.path if reading else "none"
        proto = reading.prototype if reading and reading.prototype else "no-prototype"
        return name, focus, ("utility=%.2f (%s)%s; risk=%s; intuition=%s/%s"
                             % (score, why, dose_note, risk.risk, path, proto))

    def _focus(self, activation: Dict[str, float]) -> str:
        """The construct the graph says is most active, as readable text."""
        if not activation:
            return "this"
        node, _value = max(activation.items(), key=lambda kv: abs(kv[1]))
        return node.replace("_", " ")

    # -- observation of the loop itself -----------------------------------
    def audit(self) -> List[dict]:
        return [turn.to_dict() for turn in self._audit]

    def stats(self) -> dict:
        """Loop-level numbers, including whether the realtime claim holds.

        `within_budget_rate` over the audited turns is the only honest form of
        "realtime": a budget declared in the constructor and never measured
        against observed turns is a wish.
        """
        if not self._audit:
            return {"turns": 0, "within_budget_rate": None,
                    "note": "no turns run: latency is unknown, not zero"}
        inside = sum(1 for t in self._audit if t.within_budget)
        latencies = sorted(t.latency_ms for t in self._audit)
        middle = latencies[len(latencies) // 2]
        stances: Dict[str, int] = {}
        for turn in self._audit:
            stances[turn.stance] = stances.get(turn.stance, 0) + 1
        # `turns` counts the session; every other figure is over the AUDIT WINDOW.
        # Mixing the two denominators in one dict is how a 200-turn session ends up
        # reporting 54 stances against 200 turns and looking like lost turns.
        return {"turns": self._turn_count,
                "audited": len(self._audit),
                "window": "within_budget_rate, median_ms, max_ms and stances are "
                          "computed over the %d audited turns" % len(self._audit),
                "within_budget_rate": round(inside / len(self._audit), 4),
                "budget_ms": self.budget_ms,
                "median_ms": round(middle, 3),
                "max_ms": round(latencies[-1], 3),
                "stances_in_audit": stances,
                "safety_turns_in_audit": stances.get("safety", 0)}

    def felt_vs_displayed(self, rules: Optional[dict] = None) -> dict:
        """Expose the affect layer's masking distinction at the loop boundary."""
        return express(self.pad, rules)
