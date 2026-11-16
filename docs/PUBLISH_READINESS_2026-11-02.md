# PUBLISH READINESS — Azazael → GitHub

**Date:** 2026-11-02
**Subject repo:** `C:/Azazael/azazael` (branch `deepseek-engram-813 [renamed to azazael-intel-ultra-9-evo 2026-11-04]`, 32,783 tracked files, pack 954.92 MiB)
**Verdict:** **NOT READY.** One blocker is fatal and cannot be fixed by committing. Everything else is hygiene that can be cleared.

Every claim below is either read from a file in this repo (cited `file:line`) or is a measurement
taken this session and quoted with its command. Nothing here is inferred from how the project
usually works.

---

## 0. The finding that comes before the table: there are TWO repositories

This is not a documentation nit. It changes which directory you publish.

| Path | What it is | README says |
|---|---|---|
| `C:/Azazael/azazael` | The codebase — this document's subject | `AZAZAEL — Self-Replicating AI Worm Ecosystem`, v1.0.0, Python 3.15t, Windows 64-bit, Beta |
| `C:/Users/clint` | **A second, separate git repo** — the Berks Counseling Center OSINT investigation | `Berks Counseling Center Investigation — Index`, EIN 23-2043478, "52 of 62 gaps open" |

Verified by reading both: `C:/Azazael/azazael/README.md:1` vs the working-directory `README.md:1`.
The shell's default cwd is `C:/Users/clint`, which is the *investigation* repo, and
`C:/Users/clint/.gitignore` ignores `src/`, `tests/`, `tools/`, `.github/` and `azazael/`.

**Why this is a publish blocker and not a curiosity:**

- The investigation repo's README declares that `COMPLAINT_LETTER.html` is "**FULL VERSION — access-controlled**" containing a "single-source, uncorroborated patient allegation" (CONCERN 8), and that `COMPLAINT_TODO_LIST.html` holds "17+ verified email addresses". A push of the wrong root publishes a patient allegation and a contact list of real people.
- The hazard is already documented inside this tree at
  `.agents/skills/azazael-kali-graph-protocol.md:26` — "Home-`.gitignore` leak: mirror nested under `C:/Users/clint/` (a git repo whose `.gitignore` lists `azazael/`, `Desktop/`, ...)" — and at `DEEPER_AUDIT_2026-09-29.md:278` — "the shell's default cwd is `C:/Users/clint`, a different repository."

**Remediation:** publish by explicit absolute path (`git -C C:/Azazael/azazael push ...`), never
`git push` from a shell whose cwd is the home directory. Treat "which repo am I in" as a step with
its own receipt.

---

## 1. Blockers

| # | Blocker | Severity | Evidence | Remediation |
|---|---|---|---|---|
| B1 | **Two blobs exceed GitHub's 100 MB hard file limit** — the push is rejected outright, not warned | **BLOCKS-PUBLISH** | `git rev-list --objects --all \| git cat-file --batch-check` → `272.339 MB archived/2026-05-31/onnxruntime.tar.gz`, `228.847 MB archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz` (count=2, total 501.186 MB) | Must strip from **all history** (`git filter-repo --path archived/` then `--path-glob` as needed), or publish a fresh single-commit snapshot. History rewrite changes every SHA. See §4. |
| B2 | **No hosted remote exists** — `origin` is a directory on this machine | **BLOCKS-PUBLISH** | `git remote -v` → `origin C:\Users\clint\azazael (fetch)`; also stated in-repo at `.github/workflows/test-3.15t.yml:29` | Create the GitHub repo, then `git remote add github <url>` (add, do not replace `origin` until the local mirror is retired). |
| B3 | **The wrong-root hazard** (§0) | **BLOCKS-PUBLISH** | `README.md:1` differs by root; `C:/Users/clint/.gitignore` excludes `src/ tests/ tools/ .github/` | Push by absolute path; verify `git -C ... remote -v` before and after. |
| B4 | **No LICENSE file** | **BLOCKS-PUBLISH** | `glob LICENSE*` in `C:/Azazael/azazael` → **0 files** | **Owner decision — not mine to make.** Without a license the default is "all rights reserved": nobody may legally copy, modify or redistribute it. Choose before the repo is described as open. |
| B5 | **501 MB of the 955 MB pack is vendored tarballs** | **PRE-PUBLISH-HYGIENE** | same measurement as B1; `.gitignore` (Azazael) excludes `.archive/` and `archive/build_artifacts/` but **not** `archived/` | After B1 the pack drops to roughly 450 MB, which is inside GitHub's comfort zone. |
| B6 | **199 uncommitted changes** (114 untracked, 83 modified, 2 deleted) | **PRE-PUBLISH-HYGIENE** | `git status --porcelain \| wc -l` → 199 | Commit in coherent slices or stash. A publish from a dirty tree is unreviewable and the clean-clone build is untested. |
| B7 | **Default branch is `deepseek-engram-813 [renamed to azazael-intel-ultra-9-evo 2026-11-04]`** | **PRE-PUBLISH-HYGIENE** | `git rev-parse --abbrev-ref HEAD` | Publish to `main`; keep lane branches as branches. |
| B8 | **Username `clint` is hard-coded across tracked content** | **PRE-PUBLISH-HYGIENE** | `code_search "clint"` → 152 matches (tool output cap); examples: `MASTER_CAPABILITY_TODO.md:171` ("Username in paths — implement path sanitization for `C:\Users\clint\...`"), `docs/agent_orders/03_lane_queue.md:15`, `.agents/skills/azazael-deploy/SKILL.md:10` | This leaks a username, not a secret, but it is a permanent public artifact. Decide: sanitize, or accept. `MASTER_CAPABILITY_TODO.md:171` already lists it as an open P1. |

---

## 2. CI: two of five workflows cannot work as written

The repo already knows this. `.github/workflows/test-3.15t.yml:26-42` states in capitals:

> `# CI IS LOCAL-ONLY. NOTHING HERE FIRES TODAY.` … `origin C:\Users\clint\azazael (fetch) <-- a LOCAL PATH, not a host` … `# This file is kept because it is the correct definition of the job for the day a hosted remote is added -- not because it is the gate.`

| Workflow | Would it run on a hosted runner? | Evidence |
|---|---|---|
| `test-3.15t.yml` | **No** today (no hosted remote). Once a remote exists: **maybe** — it asks for `python-version: "3.15"` with `allow-prereleases: true`, and its own header warns setup-python "may not yet support 3.15t … on Windows" | `test-3.15t.yml:80-83`, `:20-24` |
| `compliance.yml` | **No** — `runs-on: ubuntu-latest` with `python-version: '3.15'`, and it invokes `python src/CORE/compliance/scanner.py` from the repo root. Ubuntu + a Windows-tuned 3.15t project is an untested combination; the version string is unlikely to resolve | `compliance.yml:20`, `:22-25`, `:39-41` |
| `build.yml`, `catchall-guard.yml`, `graph-semantic.yml` | **Unverified** — I did not read them; do not assume either way | not read |

Two further notes, both read from the files:

- `compliance.yml:80-83` records that the gate tests were wired into CI but their own tests were not, so "a broken instrument reported OK with nothing contradicting it."
- `test-3.15t.yml:159-162` records a defect where `path: *.log` "is not a glob to YAML — a leading `*` is an alias … this workflow had two independent reasons never to run."

**Remediation:** treat the first CI run as a discovery step, not a formality. Run each workflow with
`workflow_dispatch` on a branch before making the repo public, and either pin a Python that
setup-python actually serves (3.12/3.13) for the portable jobs or mark the 3.15t job
`continue-on-error` with a comment saying why, in the style this repo already uses.

---

## 3. README and docs

| Item | State | Evidence |
|---|---|---|
| States what the project is | **Yes**, strongly — trunk/Tree-of-Life framing, architecture tree, CRADLE commands | `README.md:1-30` |
| Architecture / module map | **Yes** — ~60 lines of annotated tree | `README.md:18-90` |
| Install for a clean machine | **Not verified present** — `BUILD.md` and `CONTRIBUTING.md` exist at root and may cover it; the README itself opens by pinning `C:\Azazael\.venvs\py315t`, an absolute path | `README.md:3` |
| Declares what it refuses to claim | Partly — "Beta", "reference build is tuned to this box" | `README.md:3-6` |
| License statement | **Absent** (no LICENSE anywhere) | `glob LICENSE*` → 0 |
| Security / disclosure contact | **Not verified** | — |

The README is candid in a way that is unusual and worth keeping: it names the reference machine
(Intel Core Ultra 9 285H / Arc 140T) and tells a foreign box to start at
`docs/platforms/README.md` and run `python tools/box_profile.py`. That honesty is the right posture
for a public repo; it just needs an install path that does not begin with the author's home directory.

---

## 4. The B1 remediation, stated plainly

Removing a >100 MB blob is **not** a `git rm`. The blob stays in every commit that ever contained
it, and GitHub rejects the push on the blob, not the working tree. Two honest routes:

**Route A — rewrite history (keeps all 151 commits).**
`git filter-repo --path archived/ --invert-paths`, then force-push. Consequences that must be
accepted before starting: every commit SHA changes; the 4 tags must be re-pointed; the 6 remote
branches (`master`, `deepseek-engram-813 [renamed to azazael-intel-ultra-9-evo 2026-11-04]`, `lane-813-recovery`, `migration/baseline-20261001`,
`r15/wiring-gate-perf-calibration`, `sync/running-20261011`) must be re-pushed; and any document,
board row, ledger or audit that quotes a short SHA becomes a dangling reference. This tree quotes
SHAs constantly (e.g. `docs/RESTART_HANDOFF_2026-11-02.md` cites `eb10a862`, `7a6a2da3`), so the
cost is real and should be priced before it is paid.

**Route B — publish a snapshot.**
Push a single fresh commit ("public snapshot 2026-11-02") to a new repo, leaving this machine's full
history intact and private. Cheaper, reversible, and loses nothing that a reader of the public repo
would have used — but the public repo will have no history, which some readers treat as a
credibility signal.

**Neither route is reversible in the sense that matters** (a force-push is, a published history is
not). Both need the owner's explicit go-ahead. This document does not execute either.

---

## 5. What I did not check

Named so nobody mistakes absence for a pass:

- `build.yml`, `catchall-guard.yml`, `graph-semantic.yml` — unread.
- `docs/` — not swept for absolute paths; the 152-match count is a whole-repo sample, not a doc census.
- Whether `memory_store.db` (present at repo root) is **tracked** despite the `*.db` ignore rule — it holds memory records and should be confirmed untracked before publishing.
- Secret scanning is a separate instrument and is not this document's claim.
- `code_search -l` returned 0 for a token that `code_search` without `-l` found 152 times, so the `-l` flag is unreliable here; no count in this document rests on it.

## 6. Suggested order

1. Owner decides B4 (license) and B1 route (rewrite vs snapshot) — both are decisions, not tasks.
2. If Route A: rewrite on a **copy** first, verify the pack size and that `tests/` still imports, then force-push.
3. Create the GitHub repo; `git remote add github`.
4. Commit or stash the 199 changes (B6); move default to `main` (B7).
5. First/public push **by absolute path** (B3), then confirm from a fresh clone that the tree builds.
6. Turn CI on with `workflow_dispatch` before announcing anything.

---

*Prepared from this tree on 2026-11-02. Measurements quoted in place; file claims cited by line.
No licence was chosen, no history was rewritten, and nothing was pushed.*
