# TREE REPAIR BEFORE THE D:\ BACKUP CLONE — 2026-11-05

**Who this is for:** every lane (freebuff, kilo, opencode, crush, agy, beam), in every
environment (Windows, WSL Ubuntu, Kali, and any lane working on `G:` or a clone).
**What it is:** the ordered repair each lane runs in its own tree *before* anyone
clones a fresh tree to the `D:\` USB as a backup.
**Pin:** HEAD `e2bfa3c6` on `azazael-intel-ultra-9-evo`, written 2026-11-05. The pin is
**advisory** — re-derive with `git log --oneline -3` and `git status --porcelain`
before you trust any number below. A figure in this file that disagrees with your tree
is a defect in this file.

---

## 0. What was measured, and what is instruction only

A backup clone copies **commits**. It does not copy your worktree, your stashes, your
claims, or your `.audit/`. So "the tree is ready to clone" means something narrower
than "the tree is fine", and this section says which is which.

| environment | reachable this session | what was measured | what is instruction only |
| --- | --- | --- | --- |
| Windows `C:/Azazael` | **yes** | HEAD, branch, 12 hook stanzas tiered, orphan ref, D: space | — |
| `D:` USB target | **yes** | 115 G total, 6.3 G used, **109 G avail**, 6 % | — |
| `G:` archive | **yes** (`/mnt/g`) | contains `AZAZAEL/ubuntu_archive` only; **not a git repo** | which copy is authoritative |
| WSL `Ubuntu-26.04` | **no — Stopped** | `wsl.exe -l -v`: default distro, state `Stopped` | §3.2 commands, unrun |
| WSL `kali-linux` | **no — Stopped** | same enumeration, state `Stopped` | §3.3 commands, unrun |
| `docker-desktop` | **no — Stopped** | enumerated, state `Stopped` | not a lane tree |

**Nothing in §3.2 or §3.3 has been executed.** They are procedures written from the
Windows-measured tree, not results. A lane that runs them is the first to measure them,
and it owes the next lane the output.

---

## 1. The invariant every lane must satisfy before a clone

Six conditions. Each is a command with an expected result, not a feeling.

1. **The stack gate answers PASS for your lane.**
   `python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix` → exit 0, every line
   `[PASS]`. `[BLOCKED]` means a client restart is owed and you must say so in your
   first sentence; working around a stdio child serving old code is not repair.

2. **No backup ref is holding commits your branch does not reach.**
   `python tools/orphan_watch.py` → exit 0. **Exit 1 is the interesting case**, not a
   failure to hide: it means a `refs/backup/*` ref holds work the branch lost. Adopt or
   drop it deliberately (`git_safe.py reset --hard <ref>` or
   `git update-ref -d <ref>`), then re-run. Measured on Windows at `e2bfa3c6`:
   `refs/backup/orphaned-2026-11-05` holds **15 commits** HEAD does not reach.

3. **Every blocking hook stanza invokes a script that exists.**
   `python tools/control_tiers.py --check` → `PASS -- every blocking stanza invokes an
   existing script`. The hook guards most stanzas with `if [ -f ... ]`, so a deleted gate
   is a **silent skip**: from the commit log it is indistinguishable from a gate that ran
   and passed. Measured on Windows: 12 stanzas, 10 blocking, `T1=8, T2=4`, `T4=0`.

4. **The evidence gate passes on new debt.**
   `python tools/evidence_gate.py` → `GATE: PASS`. Known debt prints as
   `(N known/accepted at baseline)`; only *new* offenders fail. Do not rebaseline to get
   a commit through.

5. **`state/head.json` describes the HEAD you are looking at.**
   `python tools/head_state.py --write` then read it back. Measured defect on Windows
   before this session wrote it: `state/head.json` said `272a4f7c` / `2026-11-04T20:47`
   while HEAD was `e2bfa3c6`. That is exactly the stale-artifact class — a cached
   reading answering for a tree it no longer describes. **A stale `head.json` is a defect
   to record, not a number to quote.**

6. **Your own dirt is either landed or explicitly parked.**
   `git status --porcelain` → you can name every row and say why it is not committed.
   Never `git add -A`; stage by pathspec; `git show --stat HEAD` after every commit,
   because an `add` that did not land makes `git commit` succeed empty.

---

## 2. Per-lane repair procedure (identical in every environment)

Run in this order. Do not skip 2.2 — a repair performed on a tree you have not measured
is a repair of the tree you remember.

```bash
# 2.1 stack gate
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix          # want: exit 0, all [PASS]

# 2.2 measure your own tree (4 instruments, 4 readings)
cd C:/Azazael/azazael
python tools/orphan_watch.py                 # want: exit 0    (1 = decide: adopt|drop)
python tools/control_tiers.py --check        # want: PASS      (T4 = a stanza that gates nothing)
python tools/evidence_gate.py                # want: PASS      (new debt only)
python tools/head_state.py --write           # then: git show --stat HEAD

# 2.3 claim the work by id -- never by memory of what was pending
python C:/Users/clint/_board.py claim <your-lane> 10

# 2.4 land or park, by explicit pathspec, in bursts of <= 8 files
git add <paths>            # NOT -A
git show --stat HEAD       # an empty stat means the add did not land
#    commit in the BACKGROUND: the pre-commit hook takes ~3 min
#    (claim guard, mesh ledger, agent-orders sync, preflight)

# 2.5 retire every claimed row in the same turn
python C:/Users/clint/_board.py done <id> "<command + exit code + the line it printed>"
python C:/Users/clint/_board.py block <id> "<the exact blocker>"

# 2.6 report, then read the row back (a post you cannot read back did not land)
python C:/Users/clint/_board.py report <your-lane> <status> "<command, exit, output line>"

# 2.7 record the turn
#    pmb__record_batch(items=[...]) -- one atomic batch, absolute dates
#    errors are recorded at ENCOUNTER time via tools/harvest_now.py, not here
```

**A claim you cannot retire did not happen.** If 2.3 hands you work that is out of scope
for your turn, `release` it — do not sit on the 30-minute lease.

---

## 3. Per-environment specifics

### 3.1 Windows (`C:/Azazael/azazael`) — measured

Facts at `e2bfa3c6`, all from this session:

- branch `azazael-intel-ultra-9-evo`; other local branches present and **not yours to
  reset**: `lane-813-recovery`, `main`, `migration/baseline-20261001`.
- interpreter `C:/Azazael/.venvs/py315t/Scripts/python.exe` (3.15t, GIL disabled).
  Bare `python` is 3.14.7 **with** GIL — wrong for the suite.
- hook: 12 stanzas, all resolving; 4 bypass vars in the hook
  (`ALLOW_AGENT_ORDERS_DRIFT`, `ALLOW_PREFLIGHT`, `ALLOW_PROMPT_STALE`,
  `ALLOW_SUPERVISOR_NOGO`) and **5 more hidden inside the target scripts**
  (`ALLOW_BULK_COMMIT`, `ALLOW_STALE_INDEX`, `ALLOW_EVIDENCE_GATE`,
  `ALLOW_SHARD_INTAKE`). A list of escape hatches built from hook text alone
  under-reports; `control_tiers.py` prints both.
- board store `C:\Users\clint\.azazael\telemetry_store.db`, 36 954 112 bytes,
  45 288 queue rows. If `_board.py store` shows a **small file with 0 rows**, you are on
  the wrong store and every `stats` reading is meaningless — see the lane-queue canon.

### 3.2 WSL `Ubuntu-26.04` — NOT MEASURED (distro Stopped)

```powershell
wsl.exe -d Ubuntu-26.04 -u root -- bash -lc 'cd /root/azazael && git rev-parse --short HEAD && git status --porcelain | wc -l'
```

Expected findings, from the canon and *not* verified here: the Linux mirror lives at
`/root/azazael`; the board store must be the symlink
`~/.azazael/telemetry_store.db -> /mnt/c/Users/clint/.azazael/telemetry_store.db`, and a
real 32 KB file in that place is the failure mode that makes every `stats` reading lie.
Repair:

```bash
ln -sf /mnt/c/Users/clint/.azazael/telemetry_store.db ~/.azazael/telemetry_store.db
python /root/azazael/tools/orphan_watch.py
python /root/azazael/tools/control_tiers.py --check
```

Then run §2 with `python3` resolved to the Linux 3.15t interpreter, **not** to
`python3` on PATH.

### 3.3 Kali (`kali-linux`) — NOT MEASURED (distro Stopped)

Same shape as §3.2. Two environment-specific rules that are not optional:

- the board store symlink is the same repair and the same failure mode;
- a domain atlas rendered from Kali's chromium against another environment's data must
  say so in the descriptor's `atlas` field. A figure measured on one environment and
  labelled as another is a falsification, not a rendering choice.

### 3.4 `G:` — measured, and it is not a tree to repair

`/mnt/g/AZAZAEL` contains `ubuntu_archive` **only**, and
`git -C /mnt/g/AZAZAEL rev-parse` → `fatal: not a git repository`. So `G:` is an
**archive of data**, not a worktree: there is nothing there to tier, gate, or clone. If a
lane reports "G: is fixed", ask which path it measured.

### 3.5 `D:` — measured, and it is the backup target

115 G total, 6.3 G used, **109 G avail, 6 % used**. Room for a full clone plus a bundle.
`D:` already holds unrelated material (`BCC_data`, `azazael_embeddings`,
`azazael_graph_archive_2026-09-11`, media). **Clone into a new dated directory; never
into an existing one.**

---

## 4. The six defects this session found, and the shape each lane must check for

Each is stated as *the shape*, because the specific name will differ in your tree.

1. **Two enum members sharing one value are silently one member.**
   `DEERE_CAIN = "cain"` and `SONOS_CAIN = "cain"` alongside `MICROSOFT_CAIN = "cain"`
   made Python aliases: iterating the enum yielded **5** members where the source
   declared 7, and a test asserting 7 failed for a reason no reader of the source could
   see. Fixed by giving each member its own value (`"deere_cain"`, `"sonos_cain"`), not
   by relaxing the test. **Check:** for every enum, `len(list(E)) == len(E.__members__)`;
   if not, the aliases are a bug or a deliberate alias with a comment.

2. **A hook stanza can name its remediation as its gate.**
   Stanza 8 *runs* `supervisor_mcp.py --verdict` and *names* `supervisor_doctor.py --fix`
   in an echo. A resolver that takes the first `tools/*.py` in the body tiers the
   remediation pointer. Fixed by skipping comment/echo lines and preferring the invoked
   script, reporting `target_source=invoked|mention`. **Check:** for each stanza, the
   script you tier is the one on the executing line.

3. **`dead_control` was blind to dispatch, not to reachability.**
   `gate_claims_are_pinned` is registered in `GATES = {"claims-are-pinned": ...}` and
   dispatched by `GATES.get(name)`. No call graph sees that call, so the gate reported a
   live gate as dead and pushed a reader toward deleting it. Fixed in the **scanner**
   (T2 credit: a function reference in a module-level registry that the same file reads),
   not with a baseline entry — and the credit is printed as its own count
   (`8 dispatch-registered (T2)`) so it cannot hide. **Check:** when a reviewer says
   "unreachable", ask which dispatch mechanism the check models.

4. **`state/head.json` can describe a HEAD you are not on.**
   Stale reading: `272a4f7c` while HEAD was `e2bfa3c6`. **Check:** `head.json.short`
   equals `git rev-parse --short HEAD`, and `written_at` is today.

5. **The tool that took a snapshot is not on the tree.**
   `.worktree-snapshots/20261105T101046/tools/worktree_snapshot.py` exists, but
   `git ls-files tools/worktree_snapshot.py` → no match: the snapshotter lives **inside**
   its own snapshot. That is a snapshot you cannot reproduce. **Check:** every tool whose
   output you rely on is itself tracked (`git ls-files <tool>` non-empty).

6. **A validator scoped to all history fails forever on old debt.**
   `harvest_now.py --agent <lane> --validate` (the `--agent` is required; a bare
   `--validate` exits 2 with a usage error, which is not a clean lane) scanned every lane file and reported **27 defective rows**
   — all dated 2026-10-19, written before `item_id` was required. A gate that fails from
   day one gets switched off, so the default now validates **today's** lane file and
   `--all-dates` prints the history. **Check:** your validator's default scope is the
   rows a commit would actually merge.

---

## 5. Pre-clone checklist

Every line must be run in the tree being cloned. Copy the expected result, not the
feeling.

```bash
cd <tree>
git rev-parse --short HEAD                          # record it in the backup manifest
git status --porcelain | wc -l                      # must be explainable, not necessarily 0
python tools/mcp_startup_gate.py --fix              # exit 0, all [PASS]
python tools/orphan_watch.py                        # exit 0, or 1 ONLY when the one
                                                    # stranded ref is the declared backup
                                                    # ref with an adoption queue named
python tools/control_tiers.py --check               # PASS
python tools/evidence_gate.py                       # GATE: PASS
python tools/agent_orders_sync.py --check --wsl     # blocks byte-identical incl. distros
C:/Azazael/.venvs/py315t/Scripts/python.exe -u -m pytest \
    --tb=short -r f --timeout=120 -q                # xdist -n auto from pytest.ini
python tools/head_state.py --write && python tools/head_state.py --show
git bundle create ../azazael-<date>.bundle --all    # --all carries refs/backup too
```

**The bundle line matters more than it looks.** A plain `git clone` does not carry
`refs/backup/*`, so a clone is not a backup of the work an orphaned ref is holding —
which is the one thing this session found at risk. `--all` includes it.

**A clone does not carry uncommitted bytes.** If `git status` is not clean, the clone is
a backup of a tree you did not have. Either land the work first (§2.4) or snapshot the
dirty bytes explicitly and put the snapshot in the backup directory beside the clone.

---

## 6. The `D:` backup procedure

```bash
STAMP=$(date +%Y%m%d)
DEST="/d/AZAZAEL_BACKUP_$STAMP"
mkdir -p "$DEST"

# 6.1 bundle first: this is the artifact that survives if the clone is wrong
git bundle create "$DEST/azazael-$STAMP.bundle" --all
git bundle verify "$DEST/azazael-$STAMP.bundle"          # want: "is okay"

# 6.2 clone from the bundle, not from the worktree -- a bundle is immutable and
#     verifiable, a live worktree is not
git clone "$DEST/azazael-$STAMP.bundle" "$DEST/azazael"
git -C "$DEST/azazael" rev-parse --short HEAD            # must equal 6.1's HEAD

# 6.3 dirty bytes, if any, land BESIDE the clone -- never inside it
#     git_safe.py already snapshots them as blobs; copy the record + the worktree copy
cp -r .audit/preverb "$DEST/preverb-records" 2>/dev/null || true

# 6.4 the manifest is what makes the backup auditable a month from now
{
  echo "head: $(git rev-parse HEAD)"
  echo "branch: $(git rev-parse --abbrev-ref HEAD)"
  echo "dirty_paths: $(git status --porcelain | wc -l)"
  echo "bundle_sha256: $(sha256sum "$DEST/azazael-$STAMP.bundle" | cut -d' ' -f1)"
  echo "tests_collected: $(python -m pytest --collect-only -q 2>/dev/null | tail -1)"
  echo "written_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$DEST/MANIFEST.txt"
```

**Verify the backup by restoring from it, not by reading the manifest.** A clone that
opens is not a clone that works:

```bash
git -C "$DEST/azazael" status --porcelain | wc -l        # 0
python "$DEST/azazael/tools/control_tiers.py" --check    # PASS, run FROM the clone
```

If `control_tiers.py --check` fails inside the clone, the clone is missing a tracked
file and the bundle is incomplete — do not ship it.

---

## 7. What "fixed" means

`done`, `fixed`, `passes`, `verified`, `landed` are claims, and each carries the command
behind it. The acceptance for this repair, per lane, per environment:

- `orphan_watch.py` → exit 0, or a recorded decision naming the ref and the choice;
- `control_tiers.py --check` → PASS, with the tier counts quoted;
- `evidence_gate.py` → PASS, with the known/new numbers quoted;
- `head_state.py --show` → `short` equals `git rev-parse --short HEAD`;
- every claimed board row → `done` or `block` printed, and the status row reads back;
- the backup → `git bundle verify` says `is okay`, and the clone's own
  `control_tiers.py --check` passes **from inside the clone**.

A lane that cannot run one of these says which one and why. **An unrun check is not a
pass**, and a `2`/`BLIND` from any instrument is neither a pass nor a failure — it is the
thing to fix first.

---

## 8. Limitations of this document

- §3.2, §3.3 unrun: both WSL distros were `Stopped`. Their commands are transcribed from
  canon, not measured. First lane to run them owns correcting this file.
- `G:` was measured as an archive, not as a tree. If another lane has a git worktree on
  `G:` that this session could not see, its repair is entirely unmeasured.
- The 12-stanza tier table describes **this** hook at `e2bfa3c6`. A lane whose hook has
  more or fewer stanzas must re-run the tool, never quote this table.
- `df -h /mnt/g` returned the Git Bash root filesystem, not `G:` — mount points inside
  this shell do not all answer `df` correctly, so no free-space figure for `G:` is given
  here at all.
