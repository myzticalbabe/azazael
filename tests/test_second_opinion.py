"""A retired provider is never a reviewer, and the refusal says why.

RULE 0B-C: a rule without a negative control is unvalidated. The positive case
here is that github's registry entry is refused; the negative case is that a
live provider in the same family is not -- otherwise the refusal could be
"screening everything" and still look correct.

Fixtures are transcribed from the producer (`src/CORE/inference/providers.py`
PROVIDER_REGISTRY), not invented here, because a fixture written by the test
author validates the test author's assumption rather than the registry.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import second_opinion as so  # noqa: E402


def _args(**kw) -> SimpleNamespace:
    base = dict(provider="", author_provider="", file="", diff=False,
                requirement="", model=None)
    base.update(kw)
    return SimpleNamespace(**base)


def test_retired_reason_is_blank_for_live_and_non_dict():
    assert so.retired_reason({"retired": False}) == ""
    assert so.retired_reason({}) == ""
    assert so.retired_reason(None) == ""


def test_retired_reason_names_the_date_and_cause():
    p = so._providers()
    cfg = p.PROVIDER_REGISTRY["github"]
    assert cfg.get("retired") is True
    reason = so.retired_reason(cfg)
    assert "2026-07-30" in reason
    assert "shut down" in reason


def test_candidates_marks_retired_github_ineligible():
    row = next(c for c in so.candidates("groq") if c["provider"] == "github")
    assert row["retired"], "retired provider must carry its reason"
    assert row["eligible"] is False, "retired provider must never be eligible"


def test_live_provider_in_same_family_stays_eligible():
    """Negative control: the rule screens retirement, not a whole family."""
    rows = so.candidates("gemini")  # google author; github is openai family
    github = next(c for c in rows if c["provider"] == "github")
    assert github["retired"], "control must share the retired flag"
    live = [c for c in rows if not c["retired"] and c["family"] != "google"]
    assert live, "at least one live cross-family provider must remain"
    assert any(c["eligible"] for c in live)


def test_review_refuses_a_named_retired_provider():
    out = so.review("x", _args(provider="github", author_provider="groq"))
    assert out["status"] == "refused"
    assert "retired" in out["reason"]
    assert "2026-07-30" in out["reason"]
