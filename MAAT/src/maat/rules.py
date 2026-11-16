"""Q1 lane — rule extraction as first-class output (rules-as-data).

The deliverable defined BEFORE code (positioning doc §5) is the *format*:

RULE FORMAT `Q1R1` (a ruleset is a versioned JSON-able dict):
    {
      "rule_format": "Q1R1",          # format version, first thing checked
      "version": "YYYY-MM-DD[a-z]",   # ruleset version (date + disambiguator)
      "source": {                     # provenance of WHAT was extracted
        "media": "2d" | "3d" | "text",
        "ref": <str>,                 # projectile ref: url / file path / id
        "content_sha256": <64 hex>,   # hash of the exact source bytes
        "measured_on": "<ISO date>",
      },
      "rules": [
        {
          "id": "R<ordinal>",           # unique inside the ruleset
          "when": [<fact predicate>...],   # conditions, ALL of which must hold
          "then": {                       # declarative effect in a target kernel
            "kernel": "mesh" | "arena" | "render",
            "effect": <kernel-declared operation name>,
            "args": { ... },              # effect-specific data
          },
          "weight": 0.0..1.0,           # extraction confidence
        } ...
      ],
    }

Invariants (asserted, so a caller cannot slip a bad ruleset through):
  - rule_format must equal RULE_FORMAT before anything else is trusted;
  - `when` facts and `then.kernel` effects come from the seeded vocabularies
    FACTS / EFFECTS below — nothing freeform, so kernel consumers (Q2's
    mutation loop, Q3's arena) can validate by name;
  - the same source bytes always yield the same ruleset (extract() is total
    and deterministic — same input hash, same output, no drift).

The extractor below is the honest skeleton: it lifts a fixed, declared set of
matches (token -> fact) out of content and emits ~20 seeded rules; running the
real model behind it is a change to `extract()`, never to the format.
"""
from __future__ import annotations

import datetime
import hashlib
import pathlib
import re

RULE_FORMAT = "Q1R1"
KERNELS = ("mesh", "arena", "render")

# The fact vocabulary `when` may draw on (Q1R1 keeps predicates closed).
FACTS = (
    "mirror", "shatter", "forge", "weave", "pulse", "nest", "drift", "anchor",
    "split", "bind", "loop", "edge", "veil", "cast",
)

# The effect vocabulary `then.kernel` + `then.effect` may draw on. Kernel
# consumers register by (kernel, effect) — a name not declared here is a
# validation error, not a warning.
EFFECTS: dict[str, tuple[str, ...]] = {
    "mesh": ("recolor", "rescale", "displace", "shatter"),
    "arena": ("spawn", "retire", "promote", "forbid"),
    "render": ("retime", "overlay", "fade", "hold"),
}

# Seeded token -> fact lifts (the declared match set the skeleton knows).
_TOKEN_FACTS: dict[str, str] = {
    "mirror": "mirror", "reflect": "mirror", "echo": "mirror",
    "shatter": "shatter", "break": "shatter", "fracture": "shatter",
    "forge": "forge", "build": "forge", "anvil": "forge",
    "weave": "weave", "braid": "weave",
    "pulse": "pulse", "beat": "pulse",
    "nest": "nest", "burrow": "nest",
    "drift": "drift", "float": "drift",
    "anchor": "anchor", "pin": "anchor",
    "split": "split", "cleave": "split",
    "bind": "bind", "knot": "bind",
    "loop": "loop", "cycle": "loop",
    "edge": "edge", "rim": "edge",
    "veil": "veil", "hide": "veil",
    "cast": "cast", "throw": "cast",
}

_KERNEL_EFFECT = {
    "mirror": ("render", "overlay"),
    "shatter": ("mesh", "shatter"),
    "forge": ("mesh", "displace"),
    "pulse": ("arena", "promote"),
    "nest": ("arena", "spawn"),
    "drift": ("arena", "retire"),
    "veil": ("arena", "forbid"),
}


def _version_stamp(day: str | None) -> str:
    d = day or datetime.date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        raise ValueError(f"version date must be ISO YYYY-MM-DD, got {d!r}")
    return d


def ruleset(version: str, source: dict, rules: list[dict]) -> dict:
    """Assemble a Q1R1 ruleset (format check happens in validate())."""
    return {
        "rule_format": RULE_FORMAT,
        "version": _version_stamp(version),
        "source": dict(source),
        "rules": rules,
    }


def validate(rs: dict) -> list[str]:
    """Return the list of Q1R1 violations; empty means the ruleset is conformant."""
    errs: list[str] = []
    if rs.get("rule_format") != RULE_FORMAT:
        errs.append(f"rule_format must be {RULE_FORMAT!r}, got {rs.get('rule_format')!r}")
    src = rs.get("source") or {}
    if not re.fullmatch(r"[0-9a-f]{64}", str(src.get("content_sha256") or "")):
        errs.append("source.content_sha256 must be 64 lowercase hex chars")
    for k in ("media", "ref", "measured_on"):
        if not str(src.get(k) or "").strip():
            errs.append(f"source.{k} is required")
    seen: set[str] = set()
    for i, r in enumerate(rs.get("rules") or []):
        prefix = f"rules[{i}]"
        rid = str(r.get("id") or "")
        if not re.fullmatch(r"R\d+", rid):
            errs.append(f"{prefix}: rule id must look like 'R1', got {rid!r}")
        elif rid in seen:
            errs.append(f"{prefix}: duplicate rule id {rid!r}")
        seen.add(rid)
        when = r.get("when")
        if not isinstance(when, list) or not when:
            errs.append(f"{prefix}: 'when' must be a non-empty fact list")
        else:
            for f in when:
                if f not in FACTS:
                    errs.append(f"{prefix}: unknown fact {f!r}")
        then = r.get("then") or {}
        if then.get("kernel") not in KERNELS:
            errs.append(f"{prefix}: then.kernel must be one of {KERNELS}")
        elif then.get("effect") not in EFFECTS[then["kernel"]]:
            errs.append(f"{prefix}: unknown effect {then.get('effect')!r} for {then['kernel']}")
        w = r.get("weight")
        if not isinstance(w, (int, float)) or not (0.0 <= float(w) <= 1.0):
            errs.append(f"{prefix}: weight must be 0.0..1.0")
    return errs


def extract(text: str, *, ref: str, media: str = "2d", version: str | None = None,
            measured_on: str | None = None) -> dict:
    """Deterministically lift rules from `text` content.

    Same input bytes -> same content_sha256 -> same ruleset. The seeded
    vocabulary order (FACTS) fixes rule ordering, so output is total.
    """
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    day = version or datetime.date.today().isoformat()
    measured_on = measured_on or day
    hits = [f for f in FACTS
            if re.search(rf"\b{re.escape(f)}\b", text, re.IGNORECASE)
            or any(re.search(rf"\b{re.escape(t)}\b", text, re.IGNORECASE)
                   for t, fact in _TOKEN_FACTS.items() if fact == f)]
    rules = []
    for n, fact in enumerate(hits, start=1):
        kernel, effect = _KERNEL_EFFECT.get(fact, ("render", "overlay"))
        rules.append({
            "id": f"R{n}",
            "when": [fact],
            "then": {"kernel": kernel, "effect": effect, "args": {"fact": fact}},
            "weight": 0.2 + 0.05 * ((n - 1) % 12),
        })
    return ruleset(day, {
        "media": media, "ref": ref, "content_sha256": sha,
        "measured_on": measured_on,
    }, rules)


def load(path: str | pathlib.Path) -> dict:
    """Load a ruleset file and validate it; raises on the first violation."""
    import json

    rs = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    errs = validate(rs)
    if errs:
        raise ValueError(f"not a conformant {RULE_FORMAT} ruleset: "
                         + "; ".join(errs[:5]))
    return rs
