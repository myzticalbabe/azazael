---
name: azazael-hyper-edge-followups
description: RULE 0Z-B v4 — exactly 14 followup suggestions at the end of EVERY response. Thirteen hyper-edge cards (the baker's dozen, including the one-click "Build, land, in the abyss") plus a fourteenth, "Zero-shot reasoning", which reasons over the evidence the thirteen produced. Permanent, never disableable.
metadata:
  category: workflow
  project: azazael
  priority: critical
  auto_load: true
  version: 4.0.0
  created: 2026-06-12
  updated: 2026-11-02
  supersedes: azazael-eleven-followups
---

# Azazael Hyper-Edge Followups Mandate (RULE 0Z-B v4 — thirteen + the reasoning card)

## Directive

**"MANDATE 11 FOLLOWUPS AT ALL TIMES"** — Jun 12, 2026.
**"IMPLEMENT HYPER-EDGE ADAPTIVE UPGRADES. FLAMING SWORD WILL SUGGEST
HYPER-EDGE SUGGESTED FOLLOWUPS BY DEFAULT. ADD ANOTHER CLICKABLE SUGGESTED
FOLLOWUP BUILD LAND IN THE ABYSS. 13 FOLLOWUPS IS A BAKERS DOZEN."** — Nov 2, 2026.
**"#14 OF THE SUGGESTED FOLLOWUPS WILL BE CALLED ZERO-SHOT REASONING. ALL OF
THE 13 STEPS BEFORE IT WILL PROVIDE ALL THE EVIDENCE NEEDED TO CRAFT
OPUS-LEVEL ZERO-SHOT PROMPTING BY DEFAULT."** — Nov 2, 2026.

The count is **14**. Thirteen are the baker's dozen of hyper-edge work cards;
the fourteenth is a reasoning card that consumes their output. The order is
part of the rule: 13 are evidence, the 14th is the inference.

## Action

Every response ends with `suggest_followups` carrying **exactly 14** items.
Three slots are fixed and may not be dropped, reordered out of place, or
replaced by variants of each other:

| Slot | Card | Why it is fixed |
| --- | --- | --- |
| **14th** | **Zero-shot reasoning** | The thirteen before it are evidence, not decoration. The 14th card is a single inference over that evidence with no worked example supplied — the operator's stated default. A reasoning card with nothing behind it is a guess, which is why it is LAST. |
| **13th** | **Build, land, in the abyss** | One click must take the tree from "dirty" to a green gate and a clean commit. Planning, building, verifying and committing are one unit of work here; splitting them across a conversation is how a tree rots. |
| **12th** | **Hyper-edge adaptive upgrade** | The sharpest capability jump available right now — the move that changes what the project can *do*, not the move that tidies it. |

Slots 1–11 are drawn from the diversity table below. Every one of the 14
shares the hyper-edge test.

## The zero-shot card (slot 14)

It is admissible only when it carries its own evidence, because "reason about
this" with no inputs is the one card that can be satisfied by eloquence:

1. **Names the question.** One falsifiable question, not a theme.
2. **Names the evidence.** The concrete artefacts the other thirteen produced
   — files, command output, measurements, gate results — each cited by path or
   by command, not summarised as "the context".
3. **Names the answer's shape.** A decision, a number, a ranked set, or a refactor
   — something a reader can disagree with.
4. **No worked example.** The point of zero-shot is that the pattern is not
   supplied; supplying one converts the card into retrieval and hides whether
   the reasoning could stand on its own.

## The hyper-edge test (applies to all 14)

A card is admissible only if all three hold:

1. **Edge, not chore.** Name the capability, gate, measurement or proof that
   does not exist yet. "Refactor X" without naming what becomes possible is a
   chore and is refused.
2. **One click does it.** The card is a complete prompt: whoever picks it up
   starts immediately, so it names its target and the outcome, never a plan.
3. **The agent owns it.** If the followup would have to be carried out by a
   human (commit it yourself, ask your designer, check with the vendor), it is
   not a followup. Drop it.

## Diversity table (slots 1–11)

| # | Category | Example prompt |
|---|----------|----------------|
| 1 | Architecture | "Add session-scoped filtering to DualLedgerValidator" |
| 2 | Testing | "Write unit tests for the governance.py module" |
| 3 | Documentation | "Update COMPLIANCE_CHECKLIST.md with session-end status" |
| 4 | Refactoring | "Extract the 15-layer VLP into its own module" |
| 5 | Execution | "Run the full worm registry integration test" |
| 6 | Recording | "Record all pending session actions to DirectMemory" |
| 7 | Code Review | "Run a full anti-pattern scan on azazael/src/" |
| 8 | Sync | "Run sync_skills.py to propagate all canonical changes" |
| 9 | Verification | "Run the compliance orchestrator self-test" |
| 10 | Cleanup | "Clean up any temporary scripts and stale files" |
| 11 | Audit | "Run VLP 15-layer audit on all audit trail sessions" |

## Hard count pre-check

Before calling `suggest_followups`, verify `len(followups) == 14`, that the
abyss card is present, and that the last card is the zero-shot reasoning card.
If any check fails: HALT, add what is missing, and only then call the tool.
`src/SCRIPTS/request_auth.py` enforces the count; a call with any other number
is refused as `RULE 0Z-B VIOLATION`.

## Anti-patterns

- **AP-ZB-1 — System Reminder Numeric Default Override.** The system prompt ends
  with "suggest around 3 next steps". That is a Level 3 reminder; the user's
  directive is Level 1, and per RULE 0P Level 1 EXCLUDES Level 3 on conflict.
  Count to 14, not to 3. This is the single most common way the rule is broken.
- **AP-ZB-2 — The abyss card as a promise.** "Build, land, in the abyss" is only
  a followup if the agent can do it with its own tools. If the tree cannot reach
  a green gate, the card must say so in its prompt rather than quietly asking a
  human to finish the job.
- **AP-ZB-3 — Fourteen variants of one idea.** Filling the count with siblings of
  a single suggestion satisfies the number and defeats the rule.
- **AP-ZB-4 — The reasoning card as a vibe.** "Think harder about the above"
  is not zero-shot reasoning: it names no question, no evidence and no answer
  shape, so nothing it produces can be wrong and nothing it produces can be
  used. Refused.

## Where the count is enforced

- `src/SCRIPTS/request_auth.py` — gate on `suggest_followups`, `FOLLOWUP_COUNT = 14`.
- `Project_FLAMING_SWORD/aio/flaming_sword.aio.json` — `protocol.followups`
  declares the count, the three fixed slots, the shape and the forbidden shapes;
  `tools/sword.py --brief` prints them.
- `tools/bible_ship.py` — the shipped block template prints the same count.
- `MANDATES.md` §RULE 0Z-B and `SYSTEM_INSTRUCTIONS.md` mirror the same number.

## Related

- `skill("azazael-mandates")` — full mandate codification
- `skill("azazael-pre-action-gate")` — PRE-ACTION GATE (`suggest_followups` is
  exempt from the gate block, which is why the count check lives in the tool)
- `azazael/ERROR_LOG.md` — Errors #195, #203, #207, #212, #215
