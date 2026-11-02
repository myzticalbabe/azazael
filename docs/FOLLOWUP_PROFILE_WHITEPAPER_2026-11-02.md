# The followup profile — a mandate the operator can reword

**Status:** implemented 2026-11-02. Rule: RULE 0Z-B v4. Tool: `tools/followup_profile.py`.
Data: `config/followup_profile.json`. Tests: `tests/test_followup_profile.py` (7).

---

## 1. The problem this solves

RULE 0Z-B began as "11 followups at all times" (Jun 12, 2026). It became 13,
then 14, on Nov 2, 2026, with two directives in one turn:

> "13 FOLLOWUPS IS A BAKERS DOZEN."
>
> "#14 OF THE SUGGESTED FOLLOWUPS WILL BE CALLED ZERO-SHOT REASONING. ALL OF
> THE 13 STEPS BEFORE IT WILL PROVIDE ALL THE EVIDENCE NEEDED TO CRAFT
> OPUS-LEVEL ZERO-SHOT PROMPTING BY DEFAULT."

The count is a property of the *operator's attention budget*, not of the code
base. That has two consequences the earlier form got wrong:

1. **A fixed list reads the same to everyone.** The eleven canonical examples
   ("write unit tests for governance.py", "extract the 15-layer VLP") were
   written for one tree at one time. An operator who cares about evidence
   provenance and not about VLP layers gets ten cards they will never click.
   A card nobody clicks is indistinguishable from a card that does not exist:
   the number is satisfied, the mandate is not.
2. **Taste changes. Wording must be cheap to change.** Editing a canonical
   markdown file to reword a suggestion is the wrong cost — it drags canon
   review into a preference, and it makes the count and the prose diverge
   every time somebody edits one without the other.

So the count stays in canon and the **wording moves into data**.

## 2. What is the rule, and what is the taste

The split is the whole design, and it is enforced, not documented:

| Belongs to the rule (not editable) | Belongs to the operator (editable) |
| --- | --- |
| The count: **14** | Every card's name and prompt text, including the locked three |
| Which slots are **locked**: 12, 13, 14 | The order *within* 1–11 |
| That slot 14 is **last** — it reasons over the thirteen | Whose profile it is (`--operator`) |
| That the abyss card exists at all | How the abyss card is phrased |

`locked` in this tool means **cannot be deleted or renumbered**, never
"cannot be reworded". That distinction is deliberate: the operator asked to
tune the suggestions to individual taste, and a lock that also froze the words
would be a rule about phrasing, which is not what was mandated.

The three locked slots and why:

- **12 — hyper-edge adaptive upgrade.** The set must contain one card that
  names a capability the project does not have yet. Without it, "13 hyper-edge
  cards" degrades into "13 chores", which satisfies the count and defeats it.
- **13 — Build, land, in the abyss.** One click takes a dirty tree to a green
  gate and a clean commit. Planning, building, verifying and committing are one
  unit of work in this tree; splitting them across turns is how it rots.
- **14 — Zero-shot reasoning, last.** The thirteen are its evidence. Placed
  anywhere else it is a guess: there is nothing behind it yet. This is also why
  the card is the one that most needs a *shape* rule (question, evidence,
  answer, no worked example) — see §5.

## 3. The data

`config/followup_profile.json`, seeded by `--init`:

```json
{
  "version": 1,
  "rule": "0Z-B",
  "count": 14,
  "operator": "clint",
  "note": "wording is yours; the count and the three locked slots are the rule. Locked slots may be reworded, never deleted.",
  "cards": [
    {"slot": 1, "card": "Architecture", "prompt": "Add session-scoped filtering to DualLedgerValidator", "locked": false},
    ...
    {"slot": 13, "card": "Build, land, in the abyss", "prompt": "Plan, build, verify and commit clean: ...", "locked": true},
    {"slot": 14, "card": "Zero-shot reasoning", "prompt": "Reason zero-shot from the evidence the previous thirteen cards produced: ...", "locked": true}
  ]
}
```

Plain JSON on purpose: it is readable in a diff, editable in Notepad, and it
needs no dependency. A `.toml` or a YAML profile would buy comments and cost a
parser on every machine that runs the gate.

## 4. The scripts

```bash
python tools/followup_profile.py --init --operator <name>   # seed, refuses to overwrite
python tools/followup_profile.py --show                    # the 14, marked [locked]
python tools/followup_profile.py --emit                    # slot|card|prompt rows, paste-ready
python tools/followup_profile.py --set 3 --prompt "Write the migration test for the quota path"
python tools/followup_profile.py --set 13 --card "Land it, then say what broke"
python tools/followup_profile.py --remove 4                 # free slots only; renumbers
python tools/followup_profile.py --add --card "X" --prompt "Y"   # only under the count
python tools/followup_profile.py --check                    # exit 1 on any defect
python tools/followup_profile.py --reset                    # shipped default
python tools/followup_profile.py --json                     # machine-readable
```

`--emit` is the bridge to the turn: it validates first, then prints the cards
in slot order. A profile that fails `--check` cannot emit, so a broken profile
fails at the tool instead of producing fourteen plausible cards with the abyss
slot silently missing.

### Failure modes it refuses, by name

- `REFUSED: slot 13 is 'Build, land, in the abyss' -- locked slots may be
  reworded with --set, never deleted`
- `REFUSED: no slot 21 in this profile (1..14)`
- `REFUSED: the mandate is 14 cards; remove one before adding another`
- `DEFECT: the mandate is 14 cards; this profile has 13`
- `DEFECT: duplicate slot number(s): [7]`
- `DEFECT: locked slot 14 (Zero-shot reasoning) is missing`
- `DEFECT: slot 5 has an empty prompt`
- `DEFECT: count says 15 but there are 14 card(s)`
- `config/followup_profile.json is not valid JSON: Expecting ',' delimiter ...`

## 5. The reasoning card, and what "opus-level zero-shot" means here

The operator's phrase does two things at once: it names a *position* (14th,
after the evidence), and a *standard* (zero-shot, no worked example). The
profile carries the position; the standard is carried by four requirements on
the card's content, checked by a human because no parser can check them:

1. **A question, not a theme.** "Think about reliability" is a theme.
2. **Evidence named by path or command.** The thirteen prior cards are the
   evidence base; "the context" is not evidence.
3. **An answer shape** — a decision, a number, a ranked set, a diff. Something
   a reader can disagree with.
4. **No worked example.** Supplying one converts the card into retrieval and
   hides whether the reasoning could stand alone.

This is the one card the tool deliberately does not machine-check, and the
white paper says so rather than implying a checker exists: a heuristic that
scored "is this prompt good" would pass eloquent emptiness, which is the exact
failure mode the card exists to prevent.

## 6. What enforces the count

| Layer | Enforces | Fails how |
| --- | --- | --- |
| `src/SCRIPTS/request_auth.py` (`FOLLOWUP_COUNT = 14`) | the tool call | refuses a `suggest_followups` call whose count is not 14 |
| `tools/followup_profile.py --check` | the profile | exit 1 with a named defect |
| `tools/bible_ship.py` (`FOLLOWUP_COUNT = 14`) | the shipped prompt block | prints the count and the two named slots |
| `Project_FLAMING_SWORD/aio/flaming_sword.aio.json` → `protocol.followups` | the sword's brief | `tools/sword.py --brief` prints count, slots, edge test, counting rule |
| `MANDATES.md` §RULE 0Z-B, `SYSTEM_INSTRUCTIONS.md`, `skills/azazael-hyper-edge-followups.md` | the agent | rule text; skill is synced to `.agents/skills/` and checked by `canon_drift_check.py` |

None of these can make an agent call the tool. That gap is real and is stated
here rather than papered over: the count is checked *at the call*, so an
omitted call is a process violation that no file in this repository can catch.

## 7. Evidence from the implementation (measured 2026-11-02)

- `python tools/followup_profile.py --check` → `OK: 14 cards, locked slots
  [12, 13, 14] present`
- `python tools/followup_profile.py --emit | wc -l` → `14`
- `python -m pytest -q tests/test_followup_profile.py` → `7 passed`
- `python -m pytest -q Project_FLAMING_SWORD/tests/test_sword.py
  tests/test_bible_ship.py tests/test_request_auth.py` → `54 passed`
- `python Project_FLAMING_SWORD/tools/sword.py --brief` prints
  `exactly 14`, slots 14/13/12 in that order, the three edge tests and the
  counting rule.
- `python tools/canon_drift_check.py --check` → `OK: source corpus and load
  path agree` (204 skills).

## 8. What is deliberately not done

- **No database, no service.** One JSON file and one script; a profile that
  needs a daemon to read is a profile that will be read wrong on a cold start.
- **No automatic rewriting of the 11 free slots.** The tool never invents a
  card to fix a count; that is the operator's judgement, and a profile that
  renumbers its own missing card hides the fact that one was removed.
- **No canon edit from the tool.** `MANDATES.md` and the skill carry the rule;
  the profile carries the words. A tool that rewrites canon to match a
  preference is how a rule stops meaning anything.

## 9. Next, if it earns it

- A `--diff` that shows a profile against the shipped default, so a review can
  see what taste changed.
- Per-project profiles (`config/followup_profile.<project>.json`) once more
  than one operator is really using this.
- Nothing else. The point of the tool is to be boring: data in, prompts out.
