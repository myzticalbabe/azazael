"""Tests for AP-5 permission-seeking guard.

Negative controls are transcribed from real sources, not invented:
- POSITIVE controls are sentences actually emitted this session.
- NEGATIVE controls are real canon text and real quoted anti-pattern examples
  that must NOT fire, because a guard that flags canon quoting AP-5 is a guard
  nobody can use.

A validator that only proves it fires is half a validator. These tests are
written so that a regression which makes the guard fire on ANYTHING fails
here rather than in production.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from permission_seeking_guard import scan, strip_quoted  # noqa: E402

# --- POSITIVE CONTROLS: actually emitted this session, must fire -------------

MUST_FIRE = [
    # The exact violation, verbatim from the #990 split reply.
    "Say the word and I'll mint A, B, and C as separate records.",
    "Say the word and I'll mint #988.",
    "Give the word and I will land it.",
    "Let me fix the predicate before we proceed.",
    "Shall I apply the merge now?",
    "Want me to run the sweep?",
    "Would you like me to mint the three tasks?",
    "Do you want me to delete them?",
    "Should I go ahead and quarantine?",
    "If you'd like, I can run the manifest first.",
    # An UNTERMINATED fence is not a code block. A malformed message is more
    # likely than a deliberate sample, and AP-5 is CRITICAL per instance, so
    # ambiguity resolves toward flagging.
    "```text\nSay the word and I'll fix it\n",
]

# --- NEGATIVE CONTROLS: must NOT fire ---------------------------------------

MUST_NOT_FIRE = [
    # Canon quoting AP-5 verbatim. This is the case that makes or breaks the
    # guard: SYSTEM_INSTRUCTIONS.md and MEMORIES.md both cite these strings.
    'Using "Let me [action]" for a required action frames it as optional.',
    'The assistant SHALL NOT use permission-seeking language ("Let me...") '
    "for actions that are already MANDATED by established rules.",
    'BAD: "It is nearly right. Let me fix one more field first."',
    '<p><strong>AI Manifestation:</strong> "Let me try something new!" '
    "(scope creep)</p>",
    # Genuine operator questions are legitimate. The guard gates mandated
    # actions, not conversation.
    "Which environment should I use - free-threaded or GIL sidecar?",
    "Do you want the strict or the relaxed threshold?",
    "Should we cut the ledger rows or leave them for review?",
    "Let me know if you want anything else.",
    # Prose discussing the rule without constructing the violation.
    "AP-5 forbids offering to perform a mandated action.",
    "Permission-seeking language was the failure point in this process.",
    "I logged err-18 as a violation of AP-5 rather than a new lesson.",
    # Markdown blockquote citing the anti-pattern.
    "> Let me fix one more field first.",
    # TRANSCRIBED from .agents/skills/azazael-no-permission-language/SKILL.md
    # lines 53-55 -- the "Before: Violation Pattern" fenced block. Found by
    # running the guard over its own canon; the first version did not strip
    # fenced blocks and fired on the document that catalogues the violation.
    "### Before: Violation Pattern\n```text\nLet me spawn the code reviewer "
    "to review the changes.\n```\n",
    # Tilde fence.
    "~~~text\nLet me fix x\n~~~\n",
]

# --- EDGE CASES: (text, expected_count, expected_name, expected_line) -------

EDGE = [
    # Quote-stripping must NOT shift line numbers. The quoted violation on
    # line 2 is correctly ignored; the bare one on line 3 must be reported
    # AS LINE 3, which is the property that matters.
    ('Intro line\n"Let me fix x"\nLet me fix y\n', 1, "let_me_action", 3),
    # Empty and whitespace input must not crash or fabricate findings.
    ("", 0, None, None),
    ("   \n\n\t\n", 0, None, None),
]


def _run() -> int:
    failures: list[str] = []

    for text in MUST_FIRE:
        if not scan(text):
            failures.append(f"MISSED (should fire): {text!r}")

    for text in MUST_NOT_FIRE:
        hits = scan(text)
        if hits:
            names = ", ".join(f"{h.name}@{h.line}" for h in hits)
            failures.append(f"FALSE POSITIVE ({names}): {text!r}")

    for text, want_count, want_name, want_line in EDGE:
        hits = scan(text)
        if len(hits) != want_count:
            failures.append(
                f"EDGE count: expected {want_count} got {len(hits)} for {text!r}"
            )
            continue
        if want_name and hits[0].name != want_name:
            failures.append(
                f"EDGE name: expected {want_name} got {hits[0].name} for {text!r}"
            )
        if want_line is not None and hits[0].line != want_line:
            failures.append(
                f"EDGE line: expected {want_line} got {hits[0].line} for {text!r}"
            )

    # Quote stripping must preserve line numbering exactly.
    quoted = 'a\n"Let me fix"\nb\n'
    stripped = strip_quoted(quoted)
    if len(stripped.splitlines()) != 3:
        failures.append("strip_quoted changed line count")

    total = len(MUST_FIRE) + len(MUST_NOT_FIRE) + len(EDGE)
    if failures:
        print(f"FAIL {len(failures)}/{total}", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(
        f"PASS {total}/{total} "
        f"(fires={len(MUST_FIRE)} clean={len(MUST_NOT_FIRE)} edge={len(EDGE)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_run())