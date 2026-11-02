# Zero-shot briefs — 2026-11-02

Ready-to-paste tasks for a model that has read **only** the lane prompt and none of
the canon. Every brief is self-contained: it carries the state it may trust, the
observation that would prove it wrong, and the command that produces the evidence.
Nothing here asks the reader to go and read 1.12 MB first.

**How to use.** Paste one brief and nothing else. If the model asks a question the
brief answers, the brief is at fault — fix the brief. If the model invents a result
the brief demands, follow §6.

Each brief is shaped by the same six fields. Keep the shape when writing new ones;
a brief without a **TEST** is a wish with a heading.

| field | what it must contain |
| --- | --- |
| **ACT** | one imperative sentence, one deliverable |
| **STATE** | facts that may be trusted, each with its date |
| **TEST** | the observation that makes the claim false |
| **EVIDENCE** | a command and the exact line it must print |
| **REFUSE WHEN** | the honest stop, stated before work starts |
| **NEVER** | the trap that has already cost a cycle here |

All briefs assume: repo `C:/Azazael/azazael`, interpreter
`C:/Azazael/.venvs/py315t/Scripts/python.exe`, and the two universal rules — stage
by path (never `git add -A`), and a commit is not landed until
`git log --oneline -1` names it.

---

## §1 SHARDEX — capability, not features

### 1.1 — Prove a golden hash survives a stranger

**ACT** Write a third implementation that reproduces one SHARDEX golden hash from
the artifact alone.
**STATE** `docs/METTHEW/reference-shards/highend_duel` forges to golden
`1c045e596f950543`; the browser and Python agree on it (measured 2026-11-02). Both
implementations were written by the same author, so a shared misreading passes both
— three earlier defects were *ruler* disagreements, not logic, and only the digest
found them.
**TEST** The new implementation never imports `Project_SHARDEX/shardex.py` and never
reads the generated page JS; if it cannot reproduce the hash from `shard.json`, the
**specification** is incomplete — not the port.
**EVIDENCE** `python -m pytest Project_SHARDEX/tests -q -k third_impl` and the spec
field it had to guess, named.
**REFUSE WHEN** the artifact omits the quantisation, expression order, or tick
clock. Report the missing field; do not infer it from either existing port.
**NEVER** "verified" as a conclusion when the second implementation is yours.

### 1.2 — Make an extracted rule falsifiable

**ACT** Add a perturb-and-predict scorer to `Project_SHARDEX/transubstantiate.py`.
**STATE** Each of the five extracted rules records the source line that proves it
(clock, phase constants, seed, entity table, branch law). A line proves the rule is
*present*; nothing today shows it is the rule that made the source move.
**TEST** Perturb each extracted constant, state the observable change it should
cause in the original animation, then measure the original. A rule whose prediction
cannot miss is a label.
**EVIDENCE** `python Project_SHARDEX/transubstantiate.py --predict <rules.json>`
printing `verified k/5`; exit non-zero below 3/5.
**REFUSE WHEN** a rule has no measurable counterpart in the source — report it as
`PRESENT-BUT-UNFALSIFIED` rather than scoring it.
**NEVER** count a rule as verified because its citation resolves.

### 1.3 — Find where the intake actually breaks

**ACT** Run the documented SHARDEX intake against one real game tree and record the
numbers.
**STATE** The ceilings are 24 files and 2 MiB per shard; the selftest fixture is
four files. Real-tree behaviour is unmeasured.
**TEST** A second `--shatter` run must produce byte-identical shard ids. If it does
not, the pipeline is reading something it does not declare.
**EVIDENCE** `python Project_SHARDEX/shardex.py --mirror <tree> --out .shardex`
then `--shatter --mirror-file .shardex/mirror.json --out .shardex` twice, and
`diff` of the id lists; plus files/bytes seen, groups, shards refused with byte
counts.
**REFUSE WHEN** a shard is refused only because the tree is large — that is the
ceiling working, not a bug to fix by raising it.
**NEVER** raise `--per-shard` or `--payload-cap` to make a tree fit.

### 1.4 — Define the law when two arenas share a space

**ACT** Give `Project_SHARDEX/launch.py` a composition mode: two shards, one space.
**STATE** `run_round()` computes each entry's golden hash; a "tournament" today
ranks verifiable configs and never puts two arenas in the same world.
**TEST** A round whose hash depends on **both** golden hashes, reproducible from
the scripted input log alone — change either shard and the round hash must move.
**EVIDENCE** `python Project_SHARDEX/launch.py --bracket <a> <b> --compose` printing
one hash that both inputs determine, then the same command again for the same hash.
**REFUSE WHEN** the interaction needs a rule the two shards disagree about (e.g.
different `gravity`); state the resolution as an explicit, hashed parameter — never
average it silently.
**NEVER** present a shared viewport as shared physics.

### 1.5 — Make the op log an addressable program

**ACT** Promote `Project_SHARDEX/meshscene.py`'s applied-op log to `shardscript.json`
and verify it independently.
**STATE** Five pure operators (`warp`, `sprout`, `prune`, `palette`, `extrude`) each
have a digest, applied mid-flight between frames and replayed in Python; the chain
digest `d23155c2...` identifies nothing a third party can be handed.
**TEST** A third party given `field.json` + `shardscript.json` reproduces every
digest; a hand-edited op is REFUSED rather than silently re-digested.
**EVIDENCE** `python Project_SHARDEX/meshscene.py --verify-program <shardscript.json>`
→ every digest listed, exit 0; then edit one op and watch it exit 2.
**REFUSE WHEN** the program names an operator the page does not implement — that is
a port, not a program.
**NEVER** treat more operators as more capability: the ceiling is addressability.

---

## §2 Gate honesty — the gate must be able to fail

### 2.1 — Prove the prompt gate actually blocks

**ACT** Demonstrate that `tools/prompt_check.py` refuses a real commit.
**STATE** The gate is registered in `tools/preflight_all.py`, runs in
`.githooks/pre-commit`, and has an executable control that drives it on a stale and
a healthy fixture (2026-11-02). What has not been shown is the hook refusing a
*commit attempt*.
**TEST** Introduce a stale count into one lane prompt, attempt a commit, and require
the hook to exit non-zero naming the file and line; revert and require a clean pass.
**EVIDENCE** the blocked commit's `[Prompt] BLOCKED` line plus the reverted run's
`clean -- 7 prompt(s), 0 defect(s)`.
**REFUSE WHEN** the demonstration needs a real commit to land first — use
`ALLOW_PROMPT_STALE=1` only to prove the override path, and say so.
**NEVER** leave the stale line in a lane prompt when the experiment ends.

### 2.2 — Stop `--verify` trusting its own inputs

**ACT** Harden `Project_SHARDEX/meshscene.py --verify` (row `imp2-verify-inputs`).
**STATE** `mesh.json`, `field.json` and the applied-op log could be edited
consistently and verify would still pass — the same defect class as the pick hole,
one level up.
**TEST** Edit `field.json` and `mesh.json` together, consistently; verify must
REFUSE. Then restore and require VERIFIED.
**EVIDENCE** two runs of `python Project_SHARDEX/meshscene.py --verify <dir>`, one
exit 2 one exit 0, with the base digest and field sha256 reported by the page in
`browser_probe.json`.
**REFUSE WHEN** the page cannot report the base digest — that is the missing piece,
report it, do not hash the files instead.
**NEVER** accept "the digests match" when both sides of the comparison are the
files under test.

### 2.3 — Resolve a standing exemption

**ACT** Settle the failure-evidence exemption at `tools/unified_cli.py:68`
(row `unified-cli-exemption`).
**STATE** `tools/failure_evidence_gate.py --check` reports OK with one declared
exemption: a foreground dispatcher on inherited stdio, where a bound "cannot kill
the server's process group and would orphan it".
**TEST** Either the bound can be expressed (watchdog thread, signal forwarding) and
the exemption disappears, or it cannot, and the exemption gets a date and the reason
it cannot be lifted.
**EVIDENCE** `python tools/failure_evidence_gate.py --check` before and after; the
exemption list is either shorter or carries a dated justification.
**REFUSE WHEN** removing the exemption changes dispatcher semantics for every
caller — then the deliverable is the dated reason, not a code change.
**NEVER** delete the exemption to make the list shorter.

---

## §3 Claim discipline — a claim carries its receipt

### 3.1 — A claim names its task

**ACT** Implement guard G1: a completion claim carries `Task: Board-<n>` or is
refused (specified in `docs/SUBAGENT_GUARDS_2026-11-02.md` §4).
**STATE** Board rows exist and `done <id> "<evidence>"` refuses an unclaimed id
(measured 2026-11-02). Nothing ties prose in a chat to a row.
**TEST** A claim written without the trailer fails the guard; the same claim with a
real id passes. The negative control is a claim citing a retired id.
**EVIDENCE** `python -m pytest tests -q -k claim_trailer` and the guard's own output
on both fixtures.
**REFUSE WHEN** the id does not exist on the board — that is the guard working.
**NEVER** accept a trailer whose id is retired, it proves the claim is stale.

### 3.2 — A completion carries a receipt

**ACT** Implement guard G2: `command`, `exit_code`, `stdout_sha256`
(`docs/SUBAGENT_GUARDS_2026-11-02.md` §4).
**STATE** Every gate in this tree prints the line it judged by; prose completions
carry none of it. G2 is ~40 lines and the cheapest real gain available.
**TEST** A completion with no `command` is refused; with a command whose
`stdout_sha256` does not match the recorded output it is refused; a matching one
passes.
**EVIDENCE** `python -m pytest tests -q -k receipt` plus one real completion through
the guard, showing the sha it computed.
**REFUSE WHEN** the command cannot be re-run (destructive or network-dependent) —
then the receipt must say `UNREPRODUCIBLE` and why, never be omitted.
**NEVER** accept an exit code without the command that produced it.

---

## §4 Evidence — a figure without a command is a rumour

### 4.1 — Re-derive a figure that was never fetched

**ACT** Re-derive the 415 TWh (2024) / 945 TWh (2030) figures in
`docs/DJT_PROSE_AUDIT_2026-11-02.md` §7 from the report body (row
`djt-iea-rederive`).
**STATE** Both numbers are tier **C/P** in the audit: carried from secondary
reporting, report body never fetched.
**TEST** The PDF's own table yields the numbers, or the numbers are corrected, or
they are downgraded with the reason. A figure that survives all three without a
page number is not evidence.
**EVIDENCE** the fetch command, the page number, the table cell, and the tier moving
from C to A or the number changing.
**REFUSE WHEN** the report is behind a paywall — record `gated-unverified` and stop;
do not substitute a secondary source silently.
**NEVER** keep a tier-C figure and an A-tier neighbour in the same table without the
tier column visible.

### 4.2 — Make a prose instrument report everything it computes

**ACT** Fix the prose instrument: a guarded sentence splitter and a `--compare` that
prints all twelve metrics (row `prose-splitter`).
**STATE** The instrument computes twelve metrics and prints five; the splitter
breaks on abbreviations and lowercase rejoin (measured 2026-11-02).
**TEST** Two sentences separated by `Dr.` count as two, not three; `--compare`
prints twelve named metrics. A deliberately wrong split must change at least one
metric.
**EVIDENCE** `python -m pytest tests/test_prose_forensics.py -q` (currently 6 pass)
plus one `--compare` run showing twelve lines.
**REFUSE WHEN** a metric cannot be computed on the input — print `UNRUN` with the
reason, never 0.
**NEVER** report a metric you did not compute.

---

## §5 Cold start — when the brief is "carry on"

**ACT** Pick up whatever is claimable and retire it in the same turn.
**STATE** The board is the queue: `python C:/Users/clint/_board.py claim freebuff 10`
hands out oldest-first, `stats` reports availability. A claim expires in 30 minutes.
**TEST** The row you report as done must have been claimed by you, and `done` must
print `retired`; a `done` that prints `never claimed` means the work was not yours or
the id is wrong.
**EVIDENCE** `_board.py claim` output, the command you ran, and `_board.py done`
printing `retired`. Then a `lane.freebuff.status` row, read back.
**REFUSE WHEN** the queue is empty and the request is unclear — say
`NO OPEN TASKS` and ask for one line of direction; do not invent work.
**NEVER** post a row and call the work done because it is now on the board.

---

## §6 When a brief is wrong

Three cases, and none of them is "push through":

1. **The brief's STATE contradicts the tree.** Run its EVIDENCE command; if it
   disagrees, the brief is stale. Do the work the tree says, and record the
   disagreement in one line at the end.
2. **The TEST cannot be run here** (no browser, no network, no shard). Stop and
   report `UNTESTABLE HERE: <the exact obstacle>`. A brief marked done without its
   test is the defect this estate keeps paying for.
3. **The work needs a different design than the brief implies.** Do not redesign
   silently: state the two readings, their difference in size, and ask. That is the
   one case where more work is the wrong answer.
