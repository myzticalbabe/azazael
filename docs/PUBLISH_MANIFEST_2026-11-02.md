# PUBLISH MANIFEST — six standalone projects (2026-11-02)

Status: **PREPARATION ONLY. Nothing is pushed by this document.** Push is the last
step and requires the owner.

The decisions below were made by the owner and are recorded as settled. This
document does not re-open them; it turns them into literal commands.

---

## 0. The shape of the decision

The main codebase (`C:/Azazael/azazael`) **stays local and is not published.**
What publishes is a **subset of directories**, each as **its own standalone repo**,
each usable alone or composed with the others.

Two consequences follow, and both matter:

1. **The 100 MB blocker dissolves.** GitHub rejects a push on *blob size across
   history*. The two oversized blobs
   (`archived/2026-05-31/onnxruntime.tar.gz` at 272.339 MB and
   `archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz` at 228.847 MB)
   live only in the **monorepo's** history. A fresh repo seeded from one project
   directory has no such history, so it never uploads them. No `git filter-repo`,
   no SHA invalidation, no archaeology repair.
2. **The projects are standalone and do not depend on `src/CORE`.** Section 3 is
   the gate that decides whether that is true for a given tree. Where it is not
   true today, the tree does not publish yet.

---

## 1. The allowlist

Publish **only** what this table names.

| Project | Source path (relative to `C:/Azazael/azazael`) | What it is, in one line |
| --- | --- | --- |
| **FLAMING SWORD** | `Project_FLAMING_SWORD/` | The code-fixing project: point it at a repo it has never seen, find defect classes a review misses, queue, fix in batches, prove with that repo's own test command, land. |
| **FLAME** | `Project_FLAME/` | The game engine and shard conversion: schedules a simulation and turns a discontinued game into a playable shard. |
| **SHARDEX** | `Project_SHARDEX/` | Mirror a game's tree, shatter it into content-addressed shards, transubstantiate one into a playable FLAME arena with a golden state hash. L0–L3 BUILT, L4 NOT BUILT. |
| **CRADLE** | `Project_CRADLE/` | The launcher that holds the work and hands it to whatever model the owner already runs; adds no judgement of its own. |
| **NURSE RATCHET** | `Project_Nurse_Ratchet/` | The **therapeutic health agent**. |
| **ELIZA** | `Project_ELIZA/` | The **forensic investigation suite**. |

### Naming note — `REAPER` is not a missing directory

`THE REAPER` is a **named component**, not a tree: it is the sentinel,
`Project_FLAMING_SWORD/tools/sentinel.py`, and it is one of CRADLE's four parts
(sword / defender / sentinel / memory). Its contract: every path is `stat`ed,
every act comes from a closed vocabulary, and a frame that does not resolve is
taken out of play and the failing claim is named. Do not create a `Project_REAPER`
directory for it.

### Lineage note — ELIZA and NURSE RATCHET are different projects

Commit `f8c80428` ("Rename to Project Nurse Ratchet…") **renamed `Project_ELIZA`
into `Project_Nurse_Ratchet`**. That rename was an agent error: it conflated the
forensic investigation suite with the therapeutic health agent. ELIZA is restored
from `3fd0b463`; see `docs/ELIZA_LINEAGE_CORRECTION_2026-11-02.md`. The two
projects must not be re-merged, and neither depends on the other.

---

## 2. Per-project publish procedure

Run these **once per project**, substituting `NAME`. `$NAME` is the directory
name from Section 1, exactly.

```bash
SRC="C:/Azazael/azazael"
NAME="Project_CRADLE"                 # substitute per project
OUT="C:/Azazael/publish/$NAME"

# 1. a FRESH repo -- this is what dissolves the history blocker
git init "$OUT"

# 2. copy the tree, excluding VCS state and ephemeral caches.
#    --exclude '.git' is load-bearing: a copied .git would carry the monorepo's
#    history (and its 501 MB of tarballs) straight back into the new repo.
rsync -a \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '*.pyc' \
  "$SRC/$NAME/" "$OUT/"

# 3. verify the copy holds only this project
cd "$OUT"
find . -name '.git' -maxdepth 2          # must print nothing except $OUT/.git
du -sh .                                  # sanity: a project, not a monorepo

# 4. stage and CHECK before committing
git add .
git status --short                        # read this list. every path must belong
                                          # to $NAME. if anything else appears,
                                          # STOP -- the copy is wrong.

# 5. one commit
git commit -m "Publish $NAME as a standalone Apache-2.0 project"

# 6. conventional default branch
git branch -M main
```

### Why `git add .` is correct here and forbidden in the monorepo

The two rules are not in conflict, because the cwd differs:

- **Inside `$OUT`** (the fresh repo), `.` is the project directory. `git add .`
  cannot reach anything outside it.
- **Inside `C:/Azazael/azazael`** (the monorepo), `git add .` and `git add -A`
  **are forbidden**. That root carries `PEOPLE_DOSSIER.html`,
  `_990_FY2016.html`/`_990_FY2017.html`/`_990_FY2018.html`, `BCC_*.html`,
  `bcc_*.json`, `bcc_sna_output/` and `memory_store.db`. None of those may be
  published, and a bare `git add .` from that root stages them.

### Creating the remote (owner action, last)

```bash
# owner only, and only after Section 3 and Section 4 pass:
gh repo create <org>/<repo> --public --source "$OUT" --remote github --push
```

Using `git -C "$OUT"` with an absolute path is deliberate: the shell's default
cwd on this host is a **different git repository** (the BCC investigation), so an
unqualified `git push` can publish the wrong tree entirely.

---

## 3. The standalone gate

A project does **not** publish until this passes. It is a gate, not a formality:
it is the check that the owner's "they don't need the core" decision is true in
code rather than in intent.

```bash
cd "$OUT"

# (a) no production reference to the monorepo core
grep -rn --include='*.py' -E '(^|[^A-Za-z0-9_])(from +CORE|import +CORE|from +src\.CORE|import +src\.CORE|CORE\.)' .
#    EXPECTED: no matches.
#    If matches: the project imports the core path. Fix or vendor the dependency,
#    then re-run. Do not publish with the import present.

# (b) it imports and runs with the core absent
python -c "import <entrymodule>"
python -m pytest tests -q

# (c) no machine-absolute paths in what will ship
grep -rn -E 'C:/Users/clint|C:\\Users\\clint|C:/Azazael|C:\\Azazael' . \
  --exclude-dir=.git
#    EXPECTED: no matches. A leaked home path is a permanent public artifact.
```

**The failure mode, named.** If step (a) finds a `from CORE…` / `import CORE`
statement, or step (b) raises `ImportError: No module named 'CORE'`, the project
is **not standalone yet** and **does not publish**. That is a finding to record,
not a reason to add `CORE` to the shipped tree — bundling the core would
contradict the owner's decision and drag the monorepo into the public history.

### Per-project entry points

| Project | Import / self-test | Tests |
| --- | --- | --- |
| FLAMING SWORD | `python tools/sword.py --self-test` | `python -m pytest tests -q` |
| FLAME | `python -m pytest tools -q` if no self-test exists — entry point **UNKNOWN**, read `Project_FLAME/README.md` before publishing | `python -m pytest tests -q` (no `tests/` dir today) |
| SHARDEX | `python shardex.py --selftest` (13 checks) | `python -m pytest tests -q` |
| CRADLE | `python cradle.py --doctor` | `python -m pytest tests -q` |
| NURSE RATCHET | `python -m pytest tests -q` | `python -m pytest tests -q` |
| ELIZA | `python tools/eliza_release_gate.py` | `python -m pytest tests -q` |

Where an entry point is marked **UNKNOWN**, that is an honest gap, not a pass.
Confirm it from the project's own README before publishing that project.

---

## 4. Per-project pre-publish checklist

Every row must be a **verified yes** — checked by running the command, not by
remembering. A row you did not check is not a pass.

| # | Check | Command / evidence |
| --- | --- | --- |
| 1 | `LICENSE` present, **Apache-2.0** | `head -3 LICENSE` → "Apache License / Version 2.0" |
| 2 | `NOTICE` present and names the project | `cat NOTICE` |
| 3 | `README` states what the project is **and what it refuses to claim** | read it; quote the refusal line |
| 4 | Tests pass | `python -m pytest tests -q` |
| 5 | Standalone gate passes (Section 3) | no `CORE` import; imports clean |
| 6 | No machine-absolute paths in shipped files | grep in Section 3 (c) is empty |
| 7 | No secrets, keys or `.env` | `ls -a`; grep for `KEY=` / `TOKEN=` / `SECRET=` |
| 8 | No build artefacts or caches staged | `git status --short` after `git add .` |
| 9 | `PUBLIC_MANIFEST.json` / `MANIFEST_NOTES.md` updated if present | compare to the tree |
| 10 | The commit contains only this project | the staged list from step 4 of Section 2 |

### License precedent — Apache-2.0 everywhere

ELIZA already shipped **Apache License 2.0**, with `LICENSE` and `NOTICE`
(`CITATION.cff` records `license: Apache-2.0`, version `0.1.0`, released
2026-11-01). Using Apache-2.0 for every project is therefore **consistency with
existing precedent**, not a new choice. Where a tree lacks the files, copy the
canonical text rather than retyping it:

```bash
cp "$SRC/Project_Nurse_Ratchet/LICENSE" "$OUT/LICENSE"
cp "$SRC/Project_Nurse_Ratchet/NOTICE"  "$OUT/NOTICE"   # then edit the project name
```

### Current file state, measured 2026-11-02

| Project | LICENSE | NOTICE | tests/ |
| --- | --- | --- | --- |
| FLAMING SWORD | **missing** | **missing** | present |
| FLAME | **missing** | **missing** | **absent** |
| SHARDEX | **missing** | **missing** | present |
| CRADLE | **missing** | **missing** | present |
| NURSE RATCHET | present | present | present |
| ELIZA (restored) | present | present | present |

Only Nurse Ratchet and ELIZA satisfy checklist rows 1–2 as of this date. The other
four need the two files added before they publish.

---

## 5. Explicitly NOT in scope

**Never published, from any command in this document:**

- The monorepo root `C:/Azazael/azazael` — it stays local.
- `PEOPLE_DOSSIER.html`, `PEOPLE_NETWORK_CARD.html`, `PEOPLE_NETWORK_SCROLL.html`
- `_990_FY2016.html`, `_990_FY2017.html`, `_990_FY2018.html`
- `BCC_LEAD_FINDINGS.html`, `BCC_RECORD_LINKAGE.html`, `BCC_SPLINK_LINKAGE.html`,
  `BCC_TWO_SPHERE_NETWORK.html`, `INVESTIGATION_GAPS.html`, `DEEP_DIVE_HARM.html`,
  and every other `BCC_*` / `bcc_*` file
- `bcc_sna_output/`, `bcc_990_xmls/`, `bcc_5500_hits/`, `BCC_COSMOS/`,
  `BCC_Investigation_Corpus/`, `BCC_Graph_Input/`
- `memory_store.db` (and any `*.db`, `*.sqlite`) — memory contents, not source
- `archived/` — holds the two >100 MB onnxruntime tarballs that a push rejects
- `chromedriver.exe`, `swarm_results.json`, `src/META/reports/*.json`,
  `NEURAL_MESH_WIRE_OR_CUT.json`, and other run artefacts
- The main codebase directories: `src/`, `tools/`, `docs/`, `skills/`, `tests/`,
  `config/`, `data/`, `.agents/`, `.github/` — **except** a project's own copies
  of those names, which travel inside that project's directory

**Separate tree, not part of this manifest:**

- `C:/Azazael/azazael-forensics` — a standalone portable forensic tree with its
  **own `.git`** ("Yggdrasil Cleave #11", landed 2026-10-28). It is a publish
  candidate in its own right, but it is outside this manifest and needs its own
  decision. Note it contains no occurrence of the string `ELIZA`.

**Not a directory:**

- `REAPER` — the sentinel component described in Section 1.

---

## 6. Order of work

1. Add `LICENSE` + `NOTICE` to the four trees lacking them (Section 4).
2. Run the standalone gate (Section 3) on each tree and record the result. Any
   `CORE` import fails that project until fixed.
3. Confirm the entry point for FLAME (currently **UNKNOWN**).
4. Run `git init` / copy / staged-list review per project (Section 2).
5. **Owner** creates the remotes and pushes, last, by absolute path.

Nothing in steps 1–4 publishes anything. Step 5 is the owner's.
