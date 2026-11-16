# DEEP DIVE — zero-error architecture under the hyper-edge defaults, and what happens to it when the tree moves

**Date:** 2026-11-05
**HEAD at write time:** `4b0ace17` (authored 2026-11-05 03:11:58 -0500) on `azazael-intel-ultra-9-evo`
**Predecessor document:** `docs/ZERO_ERROR_ARCHITECTURE_ARC_ESQUIRE_2026-11-05.md` (Z-1…Z-8), recovered byte-identically this session from the object store
**Status:** PROPOSAL, not canon. Nothing here is enrolled in a gate.

---

## §0 What this document answers

Two questions, asked together because the tree answered both at once:

1. **Forensic:** what happened to the work committed at `2ea4718c`, and what does the surviving evidence actually prove?
2. **Adaptive:** the zero-error architecture has eight articles that were each written in response to one failure. Which of them still hold when the *object they bind to* moves out from under them — a commit orphaned, a path renamed, a branch reset, a file that turned out to exist under a different name?

The second question is the one that matters, because every failure this canon was built from was a **relocation**: a path that moved (`deere`), a commit that was absorbed (the five files inside `ad5d7157`), a harvest row that was never written down. The architecture's ability to adapt is not a nice property; it is the property under test.

**What this document cannot see:** it cannot name the actor of the reset. `.git` records the *verb* (`reset: moving to …`), never the process that issued it. Every commit in this repository carries one identity, so authorship cannot distinguish lanes. Any sentence in §1 that sounds like an attribution would be a guess, and is omitted.

---

## §1 Forensic finding — the branch was reset backwards, orphaning fifteen commits

### 1.1 The evidence, in the order it was found

| # | command | result |
| --- | --- | --- |
| 1 | `git log --oneline -4` | HEAD is `4b0ace17`, not the `2ea4718c` this lane committed |
| 2 | `git merge-base --is-ancestor 2ea4718c HEAD` | `exit=1` — my commit is **not** on the branch |
| 3 | `git cat-file -t 2ea4718c` | `commit` — the object still exists |
| 4 | `git branch -a --contains 2ea4718c` | *empty* |
| 5 | `git for-each-ref --contains 2ea4718c` | *empty* — **no ref names it** |
| 6 | `git reflog --date=iso -n 15` | `10:29:38 rebase (abort): returning to refs/heads/azazael-intel-ultra-9-evo` (twice) → `10:29:50 reset: moving to c7f21b86^` → `10:30:11 reset: moving to 4b0ace17` |
| 7 | `git merge-base 4b0ace17 2ea4718c` | `4b0ace17` — the reset target is an **ancestor** of the discarded work |
| 8 | `git rev-list --count 4b0ace17..2ea4718c` | **15** |
| 9 | `git ls-tree -r HEAD \| grep ZERO_ERROR_ARCHITECTURE` | *empty* — the doc is in no tree at HEAD |
| 10 | `ls docs/ZERO_ERROR_ARCHITECTURE_ARC_ESQUIRE_2026-11-05.md` | `No such file or directory` — also gone from disk |
| 11 | `git show 2ea4718c:docs/… > /tmp` then `git hash-object` | `f77aa4c…` = committed blob sha; `4f7663e…` = committed blob sha — **byte-identical recovery** |

### 1.2 What this is, precisely

- The commits were **not destroyed**. They were **orphaned**: no ref reaches them, so `git gc` may now prune them, and nothing else has.
- The reset moved the branch **backwards onto its own history** (`4b0ace17` is an ancestor of `2ea4718c`), so this was not a rebase landing a rewritten series on a new base — it was a pointer moving to an earlier point and stopping.
- `git restore`/`checkout --` leave no reflog entry (recorded earlier today); **`reset` does**. The reflog is the only reason this is reconstructible at all.
- Worktree bytes were also removed by `reset --hard`. They were recoverable *only* because they had been committed 40 minutes earlier. This is the whole argument for committing early, expressed as a measurement rather than an exhortation.

### 1.3 The 15 commits

```
2ea4718c docs: correct the cleanup instruction, and apply the canon's discipline to tree claims
ad5d7157 chore: remove .audit/ from index (index hygiene)
13cc87b3 CAIN marks: a witness must name its caller, and marks stop landing at the root
5e98e9d0 chore: move ARC/deere to analysis/deere (19 files)
b16ee559 Lane set: accept the two lanes the reader already advertised
35c0954a docs: name the three lanes the board actually accepts
034dfc29 docs: attribute the cleanup inventory to the evidence, not to the shape of the file
e6818a19 docs: one cleanup contract for every lane, measured against this worktree
6579f565 docs: handoff for the ARC evidence session
bdcd24ae arc: retain the esquire readings a court could re-examine
2874ad6e eliza gate: ask the publication question about the tree that ships
202bfa50 arc: grade evidence legs against what the tool read, not what it claims
73f01b9d arc: pin eliza's three published figures, and grade backing in the pin audit
c7f21b86 feat: NeuroSym-WSP — Neurosymbolic Weight-Space Programming for Azazael worms
8a4517be feat: NeuroSym-WSP — Neurosymbolic Weight-Space Programming for Azazael worms
```

The rebase was plainly about the two `NeuroSym-WSP` commits (`reset: moving to c7f21b86^` names the parent of one as an intermediate target). Whatever the intent, the executed sequence left `ad5d7157`…`2ea4718c` — thirteen commits of arc, cain, eliza and lane work — unreachable.

### 1.4 What was done about it, and what was deliberately not done

**Done (additive, reversible):**

- `git update-ref refs/backup/orphaned-2026-11-05 2ea4718c` → `exit=0`; `git for-each-ref refs/backup/` now lists `refs/backup/orphaned-2026-11-05 2ea4718c`; `git rev-list --count 4b0ace17..refs/backup/orphaned-2026-11-05` → `15`. **Naming the tip removes the thirty-day deadline** — the objects are now reachable from a ref, so no `gc` can treat them as garbage.
- The two documents were restored to the worktree and verified byte-identical by blob sha (§1.1 row 11), then re-landed as a **new commit on top of the current HEAD** rather than by moving the branch.

**Not done, on purpose:** the branch was **not** reset forward to `2ea4718c`. Moving a shared branch is a decision about what HEAD means for every lane, and the reset may have been deliberate. Both endpoints are now named (`refs/heads/azazael-intel-ultra-9-evo` at `4b0ace17`, `refs/backup/orphaned-2026-11-05` at `2ea4718c`), so the owning decision can be made later with one command and no loss either way:

```bash
git reset --hard refs/backup/orphaned-2026-11-05   # adopt the orphaned series
# or leave HEAD where it is; the ref keeps the work alive either way
```

---

## §2 Retraction — one of my own claims died in this event

The previous session ended with: *"`git merge-base --is-ancestor 2ea4718c HEAD` exit 0 ON_BRANCH."*

That was true when it was read. It was false 40 minutes later. The claim was **correct and useless**, because it anchored to `HEAD` — a moving pointer — while dressing as a statement about the work. Nothing about the work changed; only the pointer did.

This is the central finding of the whole dive, and it is not a subtle one:

> **A claim anchored to a mutable pointer expires silently. A claim anchored to a content hash survives relocation.**

The verified form of the same fact, read after the reset, still holds:

```bash
git rev-parse 2ea4718c:docs/ZERO_ERROR_ARCHITECTURE_ARC_ESQUIRE_2026-11-05.md   # f77aa4c…
git hash-object <recovered file>                                              # f77aa4c…   identical
```

The first claim needed `HEAD`. The second needed only the object, which is why it is still true.

---

## §3 The eight hyper-edge defaults, graded against today's evidence

The defaults (`docs/agent_orders/05_hyper_edge_defaults.md`, generated block `HYPER-EDGE-DEFAULTS-v1`) claim to be "the practice that runs without being asked". Graded honestly:

| # | default | verdict today | evidence | what it did **not** cover |
| --- | --- | --- | --- | --- |
| HED-1 | verify by running, never by importing | **held** | `deep_dive --offline` caught the evidence leg failing at runtime; an import sweep would not | — |
| HED-2 | every test file, every time, one file per process | **held, by witness** | `golden_arrow_status`: 537 files, 531 passed, 6 failed, **0 hung** | the 6 failures are named debt, not a pass |
| HED-3 | AST audit by default | **held** | `ast_audit`: 5,534 `.py` parsed, **0 syntax errors**, 114 bare-except, 3,789 orphan modules | orphan modules are counted, not adjudicated |
| HED-4 | deep dive by default | **held, and it failed** | `verdict: FAIL`, 3 legs in 40.7 s; `evidence_gate` → `dead_control` | the dive reads the tree it was pointed at; it cannot see a pointer move |
| HED-5 | one settings surface, must show what is OFF | **not exercised** | no `defaults_profile.py --show` in this turn | — |
| HED-6 | robust fallback, never silent success | **held** | three legs reported `ok`/`error`/`ok` and the run still produced readings; exit 1 named the failing leg | — |
| HED-7 | a claim needs its command | **held, and this is the one that caught me** | the ON_BRANCH claim *had* its command — and still expired (§2) | a command is not a timestamp; a claim needs its object sha too |
| HED-8 | extend the default, do not shadow it | **not exercised** | no new knob added | — |

**The gap HED-7 exposes:** "a claim needs its command" answers *was this measured?* It does not answer *is it still true?* A command run against a mutable pointer produces a fact with a short half-life and no expiry printed on it. HED-7 needs the object identity next to the command, e.g. `… exit 0 (measured on 2ea4718c:blob f77aa4c)`, so the claim can be re-tested after any move without re-deriving what it was about.

---

## §4 Prior art — what other disciplines already solved, and which parts transfer

Researched this session. Each entry is listed with what it actually says, not with what it is usually summarised as.

### 4.1 Poka-yoke — the tiering, and the honest limit

Mistake-proofing (Shingo) distinguishes **prevention** (the error is impossible: a keyed part cannot load backwards, an interlocked press cannot cycle early) from **detection** (the error happens and is made immediately obvious at the station). The literature is unusually blunt about the limit: *"It does not prove zero defects"* — a poka-yoke control is *"a tested mechanism for one defined error mode"*, and prevention beats detection, detection at the station beats detection downstream, and everything beats end-of-line inspection.

**Transfers directly.** This tree's controls are almost all **end-of-line inspection**: eleven stanzas in `pre-commit`, a preflight backstop, a golden-arrow run. Inspection filters what the process already produced. The high-yield prevention controls are the ones that make the bad state unrepresentable *before* the verb runs — and for the destructive verbs (`reset --hard`, `restore`, `clean`, `checkout --`) the tree has **no hook at all**, because no hook sees them.

### 4.2 Certificate Transparency (RFC 6962 / RFC 9162) — append-only plus independent witnesses

CT logs are append-only Merkle trees; Merkle *consistency proofs* let anyone verify that a later tree is a superset of an earlier one. The design's stated purpose is precise and modest: *"The logs do not themselves prevent misissuance, but they ensure that interested parties … can detect such misissuance."* Sigstore's Rekor spec adds the part usually dropped: *"It is antithetical to the design of transparency systems to trust the contents of the log … A transparency service MUST be monitored by Witnesses that independently verify the integrity and append-only properties."*

**Transfers, and this tree already owns the machinery.** `AGENTS.md` describes a hash-chained `.audit/` JSONL trail with Merkle anchors. Today's event is exactly the case that trail exists for — *except* the reset happened, so no claim was ever appended that contradicted it. The missing piece is not cryptography; it is that **lane claims are not in the chain**. A `done` row that says "committed, ON_BRANCH" is a claim about a pointer and is never re-checked by anything.

### 4.3 Metamorphic testing — the oracle problem, which is the adaptability question in disguise

The oracle problem: for many systems you cannot cheaply decide whether an output is *correct*. Metamorphic testing sidesteps it by asserting a **relation across executions** instead of an absolute expected value — the canonical example is testing `sin` via `sin(x) = sin(π − x)`, which needs no oracle for `sin(12)` at all. The CockroachDB write-up makes the distinction sharp: property-based testing asserts *each output satisfies a property*; metamorphic testing asserts *the same input through differently-configured implementations produces equivalent outputs*.

**This is the answer to "adaptability", stated in another field's vocabulary.** An absolute assertion ("the file is at `docs/X.md`") breaks on relocation. A metamorphic relation ("the bytes at the new location hash to the bytes at the old one") does not — it is invariant under the transformation by construction. §5 applies this to the Z-articles one at a time.

### 4.4 Hypergraph provenance (PROV-DM, container provenance, hyperedge lineage)

A hyperedge connects an arbitrary set of vertices, so an n-ary event — one commit touching 1,588 files, one prescription with doctor, patient, drug and pharmacy — is a single edge rather than a fan of pairs. Container-provenance work (SRI, TaPP) uses exactly this to model *"higher-order relationships … easily modeled as hypergraphs at the shared substrate"*, and PROV-DM supplies the interchange vocabulary (`Entity`, `Activity`, `Agent`, `wasDerivedFrom`, `wasGeneratedBy`).

**Transfers as a modelling correction.** A commit is an n-ary hyperedge: {author, tree, parents, message, timestamp} → {new tree}. Today's loss is invisible in a pairwise model, because the pairwise facts all stayed true — the blobs existed, the commit existed, the tree existed. What changed was the **membership of one hyperedge**: `refs/heads/…` no longer contains `2ea4718c`. That is a *set-membership* fact, and set-membership facts are the ones a pairwise "does X exist?" check structurally cannot see.

### 4.5 Reflog durability — the recovery window is a number, not a promise

Origin commit objects survive a hard reset *only* while a reflog entry names them: reachable entries expire after **90 days**, **unreachable** entries after **30** (`gc.reflogExpireUnreachable`), and loose objects are protected for a 14-day minimum. Once pruned, recovery is over. The standard advice is to name the commit before investigating (`git branch recovered HEAD@{1}`), precisely because a name is what stops the clock.

**Transfers as a control, and it is the one control actually used in this session** (§1.4): `refs/backup/orphaned-2026-11-05` was created before any other work, converting a 30-day exposure into a durable fact.

---

## §5 Adaptability analysis — which Z-articles survive relocation

Each Z-article is graded on one question: **when the object it binds to moves, does the article still hold, or does it silently become false?** The column that matters is *anchor* — whether the article is pinned to a **position** (path, branch, index state, URL) or to a **content identity** (blob sha, byte count, hash).

| article | asserts | anchor | survives relocation? | metamorphic form it needs | cost |
| --- | --- | --- | --- | --- | --- |
| **Z-1** claim tiers | a claim carries its evidence tier | evidence read at claim time | **no** — tier freezes, object moves | tier **+ object sha + measured-at** | 15 lines |
| **Z-2** shape ≠ identity | `D`/`R`/`??` is not proof of what happened | `git status` (index+worktree) | **no** — status is a snapshot of two mutable things | pair every status row with `--name-status` **content** evidence | 20 lines |
| **Z-3** witness supplied, not read | a witness must come from outside | witness *value* | **yes, and that is the defect** — a constant witness survives everything | witness must name **its caller** (already landed in `13cc87b3`, orphaned) | 0 |
| **Z-4** displacement ≠ destruction | moved is not deleted | object reachability | **yes** — its whole point | reachability must be read from **refs**, never from `HEAD` | 5 lines |
| **Z-5** store what was served | store the bytes, not the reference | served bytes | **yes** — bytes are content-addressed | none; it is already metamorphic | 0 |
| **Z-6** absence ≠ contradiction | a null result needs its universe | declared universe | **yes** — the universe is part of the claim | none | 0 |
| **Z-7** BLIND ≠ PASS | four states, never collapsed | leg status enum | **yes** — states are about the run, not the object | none | 0 |
| **Z-8** protected work first | snapshot before a destructive verb | the snapshot | **yes** — a snapshot is bytes | none | 0 |

**Result: four of eight survive, four do not — and all four that fail share one defect.** Z-1, Z-2, Z-3 and Z-5 are all pinned to a **position** where they should be pinned to **content**. That is a single structural repair, not four:

> **Z-9 (new) — an identity anchor.** Any claim about the tree records the **blob or tree sha** it is about, plus the timestamp it was measured. A claim that names only a path, a branch, or `HEAD` is a LEAD, not a VERIFIED claim, no matter how green its command was.

Today's event is the clean demonstration: the claim *"`2ea4718c` is on branch"* was positional and died; the claim *"blob `f77aa4c` is the document"* was content-anchored and survived the same reset, byte for byte.

### 5.1 Three more articles the prior art argues for

**Z-10 — metamorphic claims (from §4.3).** Where a claim depends on a transformation (move, rename, rewrite, reset, rebase), state it as a relation across the transformation rather than an absolute fact about one end. *"`19 R100` in `5e98e9d0` means the deere files moved and are byte-identical"* is a metamorphic claim; it stays true under any later rearrangement, and it is checkable with `git diff -M`. *"deere is at `analysis/deere`"* is absolute and expires at the next move.

**Z-11 — name both endpoints before a destructive verb (from §4.5).** The reflog shows the *target* of each reset and nothing about what was left. A destructive verb should be preceded by a ref at the current tip and a ref at the target: two names, so the operation is reversible in one command whichever way it was meant. The one control this session actually deployed.

**Z-12 — tier the control, not just the claim (from §4.1).** Every control declares its tier: **prevention** (the bad state cannot be represented), **detection at the station** (the verb refuses), **end-of-line inspection** (the hook catches it later). The eleven commit stanzas are tier 3. `_board.py done` refusing an evidence-free claim is tier 2. A ref that must exist before `reset --hard` is tier 1. A canon that treats all green as equivalent cannot say which failures are still possible.

---

## §6 Why this is an architecture and not a checklist

The four surviving articles (Z-4, Z-5, Z-6, Z-7) and the five that must be repaired share a shape: the survivors all describe **states of a thing** (bytes stored, universe declared, leg status recorded, snapshot taken), while the casualties all describe **positions in a container** (at this path, on this branch, in this index, at this URL). States travel; positions do not.

That is the adaptability property, stated once: **bind claims to state, not to position.** It is also why the architecture does not need new machinery. `tools/worktree_snapshot.py` already takes byte snapshots; `.audit/` already hash-chains; `git` already content-addresses everything. The missing piece is a convention that refuses a positional claim the status of a verified one — which costs lines, not subsystems, and is exactly why this document proposes articles and not a framework.

---

## §7 What this cannot see

- **Who reset the branch.** The reflog records verbs, not actors. Every commit here carries one identity, so authorship does not partition lanes.
- **Whether the reset was accidental.** A clean intent and a mistake produce identical reflog lines. §1.3's inference ("plainly about NeuroSym-WSP") rests on the intermediate target `c7f21b86^` and nothing else.
- **Anything about objects already pruned.** Not applicable today (the backup ref was created first), but the 30-day unreachable window is the horizon on which this analysis would become unreconstructible.
- **The six `golden_arrow` failures.** Recorded as debt, not diagnosed here; `--strict` would fail on them and this document did not run it.
- **The `evidence_gate` failure.** `dead_control`: *"no successful rotation is recorded; that is absence of evidence, not evidence that credentials are fresh."* Named and left standing — it is a real finding, and repairing it is not this document's turf.

---

## §8 Costed gaps, in payment order

| # | gap | article | lines | why first |
| --- | --- | --- | --- | --- |
| 1 | `_board.py done` refuses a claim with no `--name-status` or blob sha | Z-2, Z-9 | ~20 | cheapest tier-2 control; the board is the delivery plane |
| 2 | destructive-verb wrapper: refs at both endpoints, then the verb | Z-11 | ~15 | the one control that would have made today reversible without forensics |
| 3 | claims record `object_sha` + `measured_at`; re-derivable in one command | Z-1, Z-9 | ~15 | turns an expiring claim into a re-testable one |
| 4 | marks-file INVALID when witness == module constant | Z-3 | ~10 | already written and orphaned in `13cc87b3`; re-land, do not rewrite |
| 5 | tier label on every hook stanza and board verb | Z-12 | ~40 | needs the eleven stanzas read one at a time; last because it is documentation of controls that exist |

Total ≈ 100 lines. None of it is a new subsystem, and item 4 may be a `git cherry-pick` rather than a fix.

---

## §9 Verification ledger

| claim | command | result |
| --- | --- | --- |
| HEAD is `4b0ace17` | `git log --oneline -4` | `4b0ace17 arc: bind eliza's claims to the tree…` |
| 15 commits orphaned | `git rev-list --count 4b0ace17..2ea4718c` | `15` |
| the reset is in the reflog | `git reflog --date=iso -n 15` | `10:30:11 reset: moving to 4b0ace17` |
| no ref held the tip | `git for-each-ref --contains 2ea4718c` | *empty* |
| backup ref created | `git update-ref` + `for-each-ref refs/backup/` | `exit=0`; `refs/backup/orphaned-2026-11-05 2ea4718c` |
| docs recovered byte-identically | `git rev-parse 2ea4718c:<path>` vs `git hash-object <file>` | `f77aa4c…`=`f77aa4c…`, `4f7663e…`=`4f7663e…` |
| deep dive ran and failed honestly | `py315t tools/deep_dive.py --offline` | `exit=1`, `verdict: FAIL`, 3 legs / 40.7 s |
| AST leg clean | `ast_audit` leg of the same run | `5534 .py parsed, 0 syntax error(s)` |
| suite status | `golden_arrow_status` leg | `537 file(s), 531 passed, 6 failed, 0 hung` |
| evidence leg failing | `evidence_gate` leg | `dead_control: no successful rotation is recorded` |

Logs: `logs/deep_dive_zedive.log`, `logs/deep_dive.json`.

---

## §10 Expiry

- **Numbers** (HEAD, 15, 537/531/6, 5534) are true at `4b0ace17`, 2026-11-05. Re-measure after any further branch movement; the HEAD figure specifically must be read, never quoted.
- **The backup ref** keeps the 15 commits alive indefinitely while it exists. If a later session decides the series is dead, delete the ref *deliberately* — it is the only thing standing between those commits and a `gc`.
- **Re-review after 2026-11-12**, or immediately if a claim in §5 is contradicted by a live read.

*Provenance: every figure above was produced by a command in this session; the prior-art summaries are cited in §4 and were read from the sources named there, not recalled.*
