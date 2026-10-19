"""AP-5 permission-seeking guard.

Detects assistant text that frames an already-MANDATED action as optional.

Canon: SYSTEM_INSTRUCTIONS.md:2046 (AP-5), MEMORIES.md:258 (anti-pattern #16),
MANDATES.md:150, SKILLS_CATALOG.md:87. Catalogued CRITICAL process violation
per instance.

Why this exists: AP-5 was codified in four places and enforced in none of
them. Compliance reduced to recall, and recall failed. See
tools/permission_seeking_guard.py tests for the negative controls that keep
this validator from becoming its own false-green instrument.

Single rulebook, many sources: this module is the ONLY place AP-5 patterns
live. tools/transcript_ap5_gate.py applies `scan()` to EVERY registered
transcript source (its SOURCE_REGISTRY rows) through its shared
`_findings_for`; per-source work is packaged there, detection semantics
change only here, so no source can silently fork the rulebook.

Usage:
    python tools/permission_seeking_guard.py --file draft.md
    type draft.md | python tools/permission_seeking_guard.py
Exit 0 = clean, 1 = permission-seeking language present.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

# Each pattern is (name, regex). Patterns are deliberately narrow: AP-5 is a
# CRITICAL-per-instance rule, so a false positive costs real work and trains
# the reader to ignore the gate. Prefer missing a phrase over flagging a
# genuine operator question.
PATTERNS: list[tuple[str, str]] = [
    (
        "let_me_action",
        r"\bLet me (?=(?:fix|add|run|mint|apply|land|record|commit|edit|"
        r"write|spawn|call|check|verify|do|perform|execute|create|update|"
        r"start|begin|write|save|merge|split|delete|remove|install|"
        r"generate|build|deploy|test|scan|grep|search|inspect|read)\b)",
    ),
    (
        "say_the_word",
        r"\b(?:Say the word|Give the word|At your word|On your (?:word|go|"
        r"signal))\b[^.]{0,120}\b(?:I(?:'ll| will)|I'll)\b",
    ),
    (
        "shall_i",
        r"\bShall I (?=(?:fix|add|run|mint|apply|land|record|commit|edit|"
        r"write|spawn|call|check|verify|do|perform|execute|create|update|"
        r"split|delete|remove|install|generate|build|deploy|test|scan|"
        r"inspect|read)\b)",
    ),
    (
        "want_me_to",
        r"\b(?:Want me to|Would you like me to|Do you want me to|"
        r"Should I(?:'| a)? (?:go ahead|proceed|apply|run|fix|make|write|"
        r"land|mint|record|commit|edit|execute|start))\b",
    ),
    (
        "if_you_want_i_can",
        r"\b(?:If you(?:'d| would) like[,.].{0,60}\bI can|"
        r"Happy to\b[^.]{0,60}\b(?:should I|want me|shall I)\b)",
    ),
]

# Quoted spans are excluded. AP-5's canonical counter-example appears verbatim
# in quotation marks AND fenced code blocks across CODEX generators, skills and
# canon; flagging a document that *cites* the anti-pattern would make the guard
# unusable on canon itself. Fences come FIRST in the alternation so a ``` block
# is consumed whole rather than leaving its contents to be scanned.
_QUOTE_PATTERNS = [
    r"```[\s\S]*?```",  # fenced code block
    r"~~~[\s\S]*?~~~",  # alt fence
    r'"[^"\n]*"',
    r"'[^'\n]*'",
    r"`[^`\n]*`",
    r"^\s*>.*$",  # markdown blockquote
]

_QUOTE_RE = re.compile("|".join(_QUOTE_PATTERNS), re.MULTILINE)


@dataclass
class Finding:
    name: str
    line: int
    match: str


def _blank(match_text: str) -> str:
    """Blank a matched span, preserving length AND line structure.

    Blanking with a plain run of spaces preserves character offsets but
    collapses newlines, so a multi-line fenced block merges with the prose
    that follows it and the reported line number becomes the fence opener
    rather than the line that actually matched. Keeping the newlines keeps
    `text.count("\\n")` and every subsequent line number exact.
    """
    return "".join("\n" if ch == "\n" else " " for ch in match_text)


def strip_quoted(text: str) -> str:
    """Replace quoted spans with blanks, preserving length and line numbers."""
    return _QUOTE_RE.sub(lambda m: _blank(m.group(0)), text)


def scan(text: str) -> list[Finding]:
    """Return permission-seeking findings. Quoted spans are ignored."""
    findings: list[Finding] = []
    cleaned = strip_quoted(text)
    for name, pattern in PATTERNS:
        for m in re.finditer(pattern, cleaned, re.IGNORECASE):
            findings.append(
                Finding(
                    name=name,
                    line=cleaned[: m.start()].count("\n") + 1,
                    match=m.group(0),
                )
            )
    findings.sort(key=lambda f: (f.line, f.name))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", help="path to check; omit to read stdin")
    ap.add_argument(
        "--allow",
        default="",
        help="semicolon-separated finding names to suppress (documented "
        "exceptions only; never a blanket bypass)",
    )
    args = ap.parse_args(argv)

    if args.file:
        try:
            with open(args.file, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print(
                f"AP-5: cannot read {args.file!r}: {exc}",
                file=sys.stderr,
            )
            return 2
    else:
        text = sys.stdin.read()

    allowed = {n.strip() for n in args.allow.split(";") if n.strip()}
    findings = [f for f in scan(text) if f.name not in allowed]

    if not findings:
        print("AP-5: clean")
        return 0

    print(f"AP-5: {len(findings)} permission-seeking construction(s)", file=sys.stderr)
    for f in findings:
        print(f"  line {f.line}: [{f.name}] {f.match!r}", file=sys.stderr)
    print(
        "\nMandated actions are NOT requests (SYSTEM_INSTRUCTIONS.md:2046). "
        "Execute, then report. If the action is genuinely blocked, say what "
        "blocks it - do not offer to do the work.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())