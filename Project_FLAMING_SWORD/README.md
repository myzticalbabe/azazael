# Project FLAMING SWORD

Point it at a codebase it has never seen. It finds the classes of defect that a
review cannot find, queues them, fixes what is mechanically fixable in batches,
proves each batch with that project's own test command, and lands it — locally,
with the decision trail written down.

```bash
python tools/sword.py --brief                     # the protocol: decision blocks, 12 followups
python tools/sword.py --root /path/to/repo --scan
python tools/sword.py --root /path/to/repo --plan      # findings -> ordered queue
python tools/sword.py --root /path/to/repo --run --batch 5 --test "python -m pytest -q"
python tools/sword.py --root /path/to/repo --land
python tools/sword.py --self-test                 # seeded fixtures, both directions
```

Standard library and `git`. No network, no keys, no dependency to install.

## Why it exists

Every expensive failure in the estate it came from had one shape: **a statement
that was true once and drifted, where nothing re-read it.** A page told a reader to
run `tools/commgate.py`; that file had not existed for weeks. A page told an agent
to consume `src/CORE/accelerate`; that module was never built. A document quoted
"15 gates" while the registry printed a different count, and a floor threshold was
copied into two tools that could disagree while both looked correct.

None of those is a typo. Each was correct on the day it was written. A reviewer
cannot re-run a hundred claims per pull request, and an agent will not unless it is
told, so the sword makes the re-running the *first* step instead of the last.

## What it detects, and how honestly

| detector | severity | fixed mechanically | why it is trustworthy |
|---|---|---|---|
| `phantom-reference` | high | no | fenced code blocks only, and paths resolve from the document's directory before the root — 122 initial "findings" collapsed to the real ones once both rules were applied |
| `duplicate-constant` | high | no | **watchlist only**: scanning for every `NAME = number` produced 45 findings that were almost all two different settings sharing a name. A detector that noisy gets switched off, and a switched-off detector protects nothing |
| `hooks-unwired` | high | yes | `git config core.hooksPath`, reversible in one command |
| `two-interpreters` | medium | yes | the replacement is the literal interpreter already written in the same file, never a guess |
| `untested-ci` | medium | no | skipped when the workflow never checks the repository out: a labeler cannot run tests and is not a defect |
| `stale-claims` | high | no | runs the ledger's own command; requires `claims.command` in the config, and is **UNRUN** without it |
| `figure-without-command` | low | no | advisory by design — a figure may be a quotation, so it reports and never edits |

**UNRUN is not clean.** A detector that throws, is disabled, or lacks its
configuration is reported as UNRUN with the reason. This is the single most
important line in the project: "0 findings" from a detector that could not run is
the sentence that licenses a destructive remedy.

## The defender, which frames a change before it happens

A sweep that only scans finds what is wrong. It cannot tell a repair from a removal,
because nothing has stated what the thing being removed was defending: the test that
proved the old behaviour is "dead code", the gate that refused the bad state is
"simplified", and the run goes green. The defender is that statement, and it is
emitted *before* the change so it cannot become a rationalisation of work already done.

```
python tools/defender.py --intent "delete the dead duplicate-constant detector" \
    --target tools/sword.py                 # DRAFT: every hole marked <<FILL: ...>>
python tools/sword.py --defend "<intent>" --target <artefact> [--preserve]
```

It refuses a frame that cannot name **what survives** (`defends`), **what must still
pass** (`must_not_break`), **the finish line** (a command plus an outcome), **a mutation
that must be refused** (`control`), **what blocks the landing** (`refusal`) and **where
the proof lands** (`evidence`). `--preserve` adds posture, and posture is mandatory
rather than assumed: whose copy, `bytes_of_original` (an integer, and it must be 0), the
lawful route, the authority (`sony-v-connectix`, `owner-holds-copy`, and the rest of the
registered claims — an unverifiable authority is refused), and what is never carried.

Two modes, and the difference is visible instead of remembered: a **DRAFT** marks every
hole and says `--check` refuses it as it stands; a **frame** is accepted only when every
field bears weight, and a refused frame renders **no prompt at all**, so nothing
downstream can act on it. `python tools/defender.py --selftest` runs 12 controls.

A prompter does not make work lawful. It makes work say whose copy it is, which is the
part a prompter can enforce.

## The loop, and its three refusals

```
scan -> plan -> run (batch) -> verify -> land
```

1. **No verification command, no landing.** A commit asserting the project still
   works, with nothing that ran it, is a claim. The corpus this tool grew out of
   says claims are worth what their command is worth.
2. **No landing on red.** The project's own command runs before the commit; a
   non-zero exit means the batch is not landed, whatever the detector says.
3. **No push.** Landing is local. Pushing is the one step a local `git revert`
   cannot undo, so it stays a separate, declared act.

A batch also re-runs the detectors that produced it. **A fix whose own detector
still fires is a failed fix**, even when the test suite is green — that is how
"fixed" and "passes" become the same word by accident.

## Every error becomes a task, at the moment it is seen

An error that is seen and not written is an error nobody disposes of. The sweep
writes a row to `.flaming_sword/tasks.jsonl` the instant it meets one: a detector
that raised, a detector that could not run, a fix that failed, a fix whose own
detector still fires, a landing refused (no command / red / nothing touched /
already landed), a deletion housekeeping could not make.

```bash
python tools/sword.py --root <repo> --tasks            # what is waiting for a decision
python tools/sword.py --root <repo> --tasks --all      # including closed ones
python tools/sword.py --root <repo> --dispose t-0003 --as fixed --note "added the ledger"
```

Dispositions are `fixed`, `wontfix`, `duplicate`, `deferred`, `external`, and a
task cannot be closed twice into two different stories. The rule the ledger exists
for is *encounter time*: the detail — which command, which exit code, which file —
is gone by the end of a session, and reconstructing it over-weights whatever is
still salient.

**One error, one row — with one deliberate exception.** Identity is
`stage + kind + subject`, not the message, so a count inside a message ("3 item(s)
failed") does not fork the row. A re-encounter increments `seen` and moves
`last_seen` instead of adding a twin, because a scan every minute would otherwise
produce a thousand identical rows and the queue stops being readable — which is how
a queue dies. A recurrence **after** a disposition is a new row: the error came
back, so it is a new fact about the tree, not a reopened opinion.

The class of defect this caught immediately: `stale-claims` returned `ran=True,
0 findings` when no `claims.command` was configured — a guard that never ran,
reporting itself clean. It is now UNRUN, and that UNRUN is a task.

## The protocol it carries

`aio/flaming_sword.aio.json` is the instruction object; `--brief` prints it in the
form an agent can follow:

- a **decision block** before any state-changing action (`target`, `evidence`,
  `blast`, `verify`, `rollback`) and another before landing a batch;
- exactly **12 followups** at the end of a turn, each naming its target, none of
  them a chore the agent cannot do itself;
- the claim rule, mechanised in the commit message as a `Verified:` line.

## Research stage: deep, and recorded rather than pretended

The sweep can also be an *improvement* pass, not only a repair. The runner has no
network client and no API key, so it does not pretend to browse: the **agent**
runs the deep search, and `--record-research` validates and queues what it finds
as proposals that are never auto-applied.

Tiers, and what each one licenses:

| tier | evidence | adopt? |
|---|---|---|
| A | primary docs, source, reproducible benchmark | yes, with a measured before/after |
| B | official index or changelog | identity only, never a capability claim |
| C | credible secondary write-up | only paired with an A source |
| D | blog, thread, snippet | a pointer, never a basis for changing working code |

Adaptation rules that survive contact with a real repo: adopt only what **replaces**
a component the project already has (a new component must retire one), no dependency
without a licence check, and a proposal that cannot name its verification command is
a wish rather than a proposal.

## Limits

- It reads documents and Python source. It does not execute the target's code
  except through the verification command you give it.
- Archives, vendored trees and `.agents/skills` are skipped by name: proposing edits
  to history produces findings that can never be fixed.
- Two mechanical fixers exist. Everything else is a queue entry with a remedy and a
  human decision, and the report says so rather than inventing a patch.

## Status

`0.1.0` — seven detectors, two fixers, the loop, the research contract and a
self-test that seeds five defects into a throwaway repository and asserts the clean
one stays silent.

Measured on its home tree (`--root C:/Azazael/azazael --scan`, 2026-11-01): **149
findings across 4 detectors** — 95 `phantom-reference`, 50
`figure-without-command` (advisory), 2 `two-interpreters`, 2 `untested-ci` — plus
`duplicate-constant` honestly **UNRUN**, because no watchlist is declared for that
tree yet. `stale-claims` is UNRUN for the same reason: no `claims.command`.

State lives in `.flaming_sword/` beside the swept tree and is disposable: deleting
it re-derives everything from one scan. `--scan` writes `findings.jsonl` and
`--plan` adds `queue.jsonl`; a scan that finds nothing UNRUN removes a stale
`unrun.txt` rather than leaving a detector reported blind after it started seeing.
