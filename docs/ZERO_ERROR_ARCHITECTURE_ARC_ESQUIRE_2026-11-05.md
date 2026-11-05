# ZERO-ERROR ARCHITECTURE FOR ARC + ESQUIRE — proposal

**Status: PROPOSAL. Not canon.** Written in article form so it can be adopted,
amended or refused without translation — the convention `ESQUIRE_ADMISSIBILITY_2026-11-04.md`
§6 used for its own E-10 proposal. The canon is not edited by this document.
**Measured at:** HEAD `ad5d7157`, 2026-11-05T10:20Z, worktree `C:/Azazael/azazael`
(`git status --porcelain | wc -l` → `0`).
**Expiry:** every count here re-measures after 2026-11-12. The articles do not
expire; the numbers do.

---

## 1. The premise, and why it is not "add more checks"

The tree already carries an unusually complete *admissibility* instrument for
claims about the world: `tools/esquire_admissibility.py` (1,041 lines, ten gates,
a record schema, a negative-control suite) and `docs/ESQUIRE_CANON_2026-11-03.md`
(553 lines, Articles E-1…E-11, each with a falsifier and a negative control).
It also carries `tools/claim_guard.py` (commit-message claims),
`tools/evidence_gate.py` (dead controls, wired claims, canon pre-check),
`tools/arc_provenance.py`, `tools/wire_evidence_audit.py`, `tools/arc_pin_audit.py`.

So the gap is not "no enforcement". The gap is **an object mismatch**: the
canon's discipline is applied to evidence about the world, and not to the lane's
own claims about the tree. All five failures recorded today were *tree-claims*,
and each one is a legal-shaped question the canon already answers — under
another name:

| today's tree-claim failure | canon article that already answers the shape |
| --- | --- |
| `19 D + 19 ??` read as destruction | **E-3** the shape test is not the trigger test |
| a restore read as "work destroyed" | **E-5** displacement is not extinguishment |
| a witness read from a source constant | **E-10.2/E-10.3** witness and authentication are independent |
| gzip bytes stored as the document | **E-7.2** tier is set by what was *read*, not by the fact that it was *found* |
| a claim carried by memory of a prior read | **E-7.3** agreement raises confidence, never raises tier |

The architectural move is therefore: **apply the canon's own discipline to the
lane's operational claims, and add exactly one capability** (protected work
before destructive work) that mirrors nothing.

---

## 2. The articles (proposed Z-1 … Z-8)

Each carries: the canon article it mirrors, the measured failure that bought it,
the enforcement that exists today, and its **blind spot** — because an
over-read instrument is the main risk of building one (admissibility §5).

### Z-1 — A claim carries the tier of the weakest instrument behind it

**Mirrors E-7.** Tiers for *operational* claims, not sources:

| tier | instrument | may carry |
| --- | --- | --- |
| A | a command run now, with exit status and the line it printed | a fact about the tree |
| B | `state/head.json` (`python tools/head_state.py --write`) | HEAD sha, test count, dirty count — *until its date* |
| C | a committed report, read after landing | a hypothesis about the tree; it answers for the tree it described |
| D | recall, a prior session's summary, a board row's prose | a lead, never a claim |

**Bought by:** today's deere claim, carried at tier D (a row's prose plus a diff
shape) and wrong. And by the `golden_arrow --file` overwrite already recorded in
`05_hyper_edge_defaults.md` HED-2: a one-file run answered for a 499-file reading.

**Enforcement today:** `tools/claim_guard.py` (message claims), PRECISION-NOT-BYPASS
(a rejected claim is repaired by scoping it, never by `ALLOW_CLAIM_GUARD=1`).
**Blind spot:** tier A says a command ran, not that it ran against the right
object (that is Z-2 and Z-6).

### Z-2 — Shape is not identity

**Mirrors E-3.** `19 D + 19 ??` is the shape of a move *and* the shape of a loss.
A deletion claim must carry `git show --name-status` (with rename detection) or
`git log --diff-filter=D -- <path>`, or it is a claim about a shape.

**Bought by:** `analysis/deere` reported lost at 09:56 and re-checked at 10:03:
`git show --name-status --format= 5e98e9d0` → `19 R100`. The work had landed;
the reading had not.

**Enforcement today:** none — this is a convention in §8.2 of
`TREE_CLEANUP_2026-11-05.md`.
**Cheapest gate:** a `done`-row evidence rule: a row asserting `D` without a
paired directory or a rename line is rejected by the poster. Cost: ~20 lines in
`C:/Users/clint/_board.py`; not built here.
**Blind spot:** a genuine deletion *and* a genuine move can coexist in one slice;
the check distinguishes them, it does not judge whether either was intended.

### Z-3 — The witness is supplied, never read

**Mirrors E-10.2/E-10.3** (a witness and an authentication record answer
different questions) and **E-11** (a machine is heard only through a record a
court can test).

A `witness` field that defaults from a module constant is not evidence of who
ran a thing — it is evidence of who *wrote the constant*. It must be an input:
`--witness` supplied by the caller, or the literal `UNATTRIBUTED`.

**Bought by:** `cain_marks.json` was attributed to kilo because both files read
`"witness": "KILO-NEMOTRON-3-ULTRA-2026-11-05T02:30:00Z"` — which
`cain_obsolescence_cli.py` showed to be its own `CAIN_WITNESS` constant. The
attribution was retracted in `13cc87b3`, which also refuses to write
`marks/` into a repository root.

**Enforcement today:** the CLI contract (`--witness` → `CAIN_WITNESS` →
`UNATTRIBUTED`), 15 tests green.
**Blind spot:** supplied ≠ true. A caller who names another lane is
indistinguishable from a caller who *is* that lane; only the *absence* of a
witness is detectable. Stated, not fixed.

### Z-4 — Displacement is not destruction

**Mirrors E-5.** Name the verb, because the remedy differs:

| verb | what it does | recovery |
| --- | --- | --- |
| `git restore <path>` / `git checkout -- <path>` | **displaces** a tracked edit back to HEAD | the edit is gone unless committed; a `git restore` writes **no reflog entry** |
| `git clean -fd` | **extinguishes** untracked files | none, ever |
| `git reset --hard` | displaces the index and worktree | reflog for commits, nothing for worktree |

**Bought by:** the 09:56 event — tracked edits displaced (rewritten, green),
untracked CAIN marks and two harvest rows extinguished. The two rows were
**never committed** (absent at `git show HEAD:state/bake_harvest_freebuff_2026-11-04.jsonl`
too), which is the whole difference between "recoverable" and "gone".

**Enforcement today:** the refusal list (§5 of `TREE_CLEANUP_2026-11-05.md`),
the HALT broadcast (board row 47684), and the incident record.
**Blind spot:** a lane that runs the verb anyway is not blocked by any hook —
`.githooks/pre-commit` never sees a restore.

### Z-5 — Store what was served, not what arrived

**Mirrors E-7.2.** A fetch that stores gzip bytes and records "200 OK" has
recorded the *transfer*, not the document. `FetchResult.encoding` must be
recorded, the stored sha must be over the **decoded** body, and an unsupported
encoding must raise rather than be persisted.

**Bought by:** `Project_ELIZA/tools/bcc_bypass.py` advertised `br` while the 3.15t
venv has `brotli False, brotlicffi False` (measured) and stored whatever arrived.
Fixed by `_accept_encoding()` (advertise only what can be decoded),
`_decode_body()` (gzip/deflate/identity, `ValueError` otherwise), and 7 tests —
including a live `ThreadingHTTPServer` serving gzip through
`BCCFetchEngine(raw_dir=…)`, asserting the stored bytes equal the document.

**Enforcement today:** `tests/test_bcc_bypass_encoding.py` — `7 passed in 0.89s`,
exit 0 (re-run at the committed state, `logs/bcc_recheck.log`).
**Blind spot:** a server that serves a *different* document than it claims is not
detectable by any decode check; that is a tier question (Z-1), not an encoding one.

### Z-6 — Absence is not contradiction, and a no-op is not a refusal

**Mirrors admissibility §4.1** ("Absence is not contradiction, in any posture").

Three states that look identical and are not: *nothing to stage* (content already
in HEAD), *staging refused* (ignored path, exit 1), *staged and swept* (another
lane's index write). `git add` exits 0 for the first and second-to-last.

**Bought by:** today. Five files staged for this lane's own commit were absorbed
by `ad5d7157` (1,588 files, a message about `.audit/` hygiene). The next
`git add` exited 0 and changed nothing; `git diff --cached` read 0. Only
`git ls-tree HEAD -- <paths>` showed all five blobs present.

**Enforcement today:** none automated. The rule is §8.4(9) of
`TREE_CLEANUP_2026-11-05.md`.
**Blind spot:** landing proof tells you the bytes are in HEAD, never that the
commit message describes them. Attribution stays a human act.

### Z-7 — A checker that cannot run says BLIND

**Mirrors HED-6** and the exit-code contract of `golden_arrow.py` (`0` clean,
`1` new defect, `2` could not run — and `2` is never a pass).

**Bought by:** `cain_obsolescence_cli.py`'s no-command path returned `1` from
`main()` — a *value* its caller discarded — while the test documented
`SystemExit(1)`. The production code contradicted its own test's contract; the
fix was `sys.exit(1)` in production, not a weakened assertion.

**Enforcement today:** the test (`tests/test_cain_obsolescence_cli.py`, 15 green).
**Blind spot:** a tool that runs and reports the wrong *reading* still exits 0
(HED-3's `py=` vs `parsed=` undercount).

### Z-8 — Protected work before destructive work *(the one new capability)*

Nothing in the canon mirrors this; it is the only article bought purely by
operational loss.

`python tools/worktree_snapshot.py --snapshot` → sha256 manifest under
`.worktree-snapshots/` (gitignored); `--restore <STAMP>` → bytes back;
`--verify` → re-hash; `--list` → what is held. Caps: 25 MB per file, 512 MB total
(this disk measured 9.7 GB free, 99%). **Files outside the caps, and files
ignored by `.gitignore`, are named in the output** — the first smoke missed its
own test artifact because `.gitignore:51:*.tmp` made it invisible, which is
exactly why the tool prints what it did not capture instead of implying totality.

**Blind spot, stated:** a snapshot protects what it captured and nothing else. It
is not a substitute for committing work, and a snapshot directory on the same
disk at 99% is not a backup.

---

## 3. What this architecture cannot see

Mirroring admissibility §5, because an over-read instrument is the risk:

- **Truth.** Every check tests the paperwork. A perfectly assembled record can
  describe a fabrication and be called READY. Same for a manifest: sha256 proves
  the bytes are the bytes, never that the claim about them is honest.
- **Prose that never becomes an artifact.** No hook receives assistant output
  (`AGENTS.md`, "ENFORCEMENT SURFACES"). A false claim stated in chat and never
  written has no gate to fail; enforcement is downstream, on the durable artifact.
- **Attribution.** Z-3 makes a witness an input; it cannot make the input true.
- **The largest artifacts.** Caps exclude them by design at 99% disk. The
  exclusion is printed, which converts a silent hole into a stated one.
- **Retroactivity.** Nothing here recovers the two harvest rows. Architecture
  that only points forward is honest; architecture that claims to repair the past
  is not.

---

## 4. Gaps, costed, in the order I would pay them

| # | gap | article | cost | why first / not first |
| --- | --- | --- | --- | --- |
| 1 | `done`-row evidence refuses a `D` claim with no `--name-status` | Z-2 | ~20 lines in `_board.py` (untracked, outside the repo) | cheapest; today's wrong claim was a board row |
| 2 | a `git_safe` wrapper that snapshots before `restore`/`clean`/`reset` | Z-4, Z-8 | ~40 lines, shell + `worktree_snapshot.py` | no hook can see these verbs; a wrapper is the only interception point |
| 3 | `head_state.py --write` freshness gate (refuse to quote a `head.json` older than HEAD) | Z-1 | ~15 lines | converts B-tier quotes into A-tier or refuses them |
| 4 | marks-file check: `witness == module constant` ⇒ record INVALID | Z-3 | ~15 lines + 2 tests | closes the exact defect that produced a retraction |
| 5 | CI leg asserting fetch/store round-trip for any engine that advertises an encoding | Z-5 | existing test generalised | already covered for `bcc_bypass`; generalising is optional |

Not proposed: a new gate framework. There are already ten admissibility gates,
eleven hook stanzas and a unified registry; adding an eleventh surface before the
five above are paid would be the failure mode this document is about.

---

## 5. Verification ledger (what was actually run)

```
git rev-parse --short HEAD                          -> ad5d7157
git status --porcelain | wc -l                      -> 0
git show --name-status --format= 5e98e9d0           -> 19 R100
git ls-tree HEAD -- <the five absorbed paths>        -> 5 blobs present
git diff --stat HEAD -- <the five paths>             -> (empty)
pytest tests/test_bcc_bypass_encoding.py -q --timeout=120
                                                    -> exit 0, "7 passed in 0.89s"
pytest tests/test_cain_obsolescence_cli.py (13cc87b3) -> 15 passed
board: claim freebuff -> 47684 retired -> NO OPEN TASKS; report -> row 47695 read back
```

Two earlier claims were **retracted** in the incident record rather than left
standing: the deere loss (§8.2) and the kilo attribution (§1.1). A document that
keeps a falsified claim because it was once written is the artifact this
architecture exists to prevent.

---

## 6. Provenance

Derived from `docs/ESQUIRE_CANON_2026-11-03.md` (Articles E-3, E-5, E-7, E-8,
E-9, E-11), `docs/ESQUIRE_ADMISSIBILITY_2026-11-04.md` (§4.1, §5, §6),
`docs/INCIDENT_2026-11-05_WORKTREE_RESTORE.md`, `docs/TREE_CLEANUP_2026-11-05.md`
§8, and this session's own measurements at `ad5d7157`, 2026-11-05.
The article numbering here is parallel to, and does not extend, the E-series: a
Z-article is an operational claim rule and may not be quoted as a legal one.
