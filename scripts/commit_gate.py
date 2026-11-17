#!/usr/bin/env python3
"""commit_gate.py -- bulk-diff gate for commits (2026-09-28).

Why this exists: three straight forensic-fix commits swept pre-existing
worktree dirt into their messages (260-line local_memory.py for a 6-line
hunk, dead .bats, 470-line retention files). Nothing broke, but a commit
message that describes 5 lines while carrying 400 is a lie in the ledger,
and the ledger is load-bearing here.

Two parts:
  1. `commit_gate.py --hook` (pre-commit): fail when the STAGED changeset
     exceeds bulk thresholds unless ALLOW_BULK_COMMIT=1. Small focused
     commits always pass; deliberate bulk ops (frame untracking, snapshots)
     pass by declaring intent in the env.
  1b. `commit_gate.py --hook --base REV` (push): judge each commit in
     `REV..HEAD` ON ITS OWN CHANGESET, not the union of the range. Two scopes
     are kept apart here and neither answers the other. (a) The index is not the
     range: at push time it holds whatever a concurrent lane staged, so an
     index-scoped run refuses a push over files the commit never touched
     (measured 2026-11-03: a 2-file commit blocked by 7 forensic files staged
     by another lane). (b) The range is not the commit: the caps are per-commit
     numbers, so `git diff REV HEAD` charges 29 focused commits as one
     1,215-file changeset with 24 oversized files and demands
     `ALLOW_BULK_COMMIT=1` for work that was already split (measured
     2026-11-16). A commit's message authorises that commit only; a clean merge
     is skipped and counted, a merge that edited files relative to every parent
     is counted in the file tally, and each refusal names the sha to fix.
  2. `commit_gate.py review`: interactive worktree review -- groups changed
     files (source vs generated), shows per-file +/- and lets the operator
     stage exactly what the commit message will describe.

Thresholds via env: COMMIT_GATE_MAX_LINES (default 150 changed lines in one
file), COMMIT_GATE_MAX_FILES (default 8 staged files).

Exit codes: 0 pass / 1 block (--hook) or user abort (review).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_LINES = 150
DEFAULT_MAX_FILES = 8

REPO = Path(__file__).resolve().parents[1]
#: The same tool `tools/preflight_all.py` registers as `soulforge-selftest`, so
#: the command this hook runs is the command the evidence tier runs.
#:
#: SPELLED AS A STRING, NOT ASSEMBLED. This path was `REPO / "tools" /
#: "soulforge_gate.py"` until 2026-11-16, which is correct at runtime and
#: invisible to every textual audit: the wiring check in
#: `tests/test_preflight_gate_wiring.py` looks for a literal `tools/<name>.py`
#: on an executed line, so a real invocation read as an unwired gate for weeks.
#: The string is the single place the path is written; the argv below is built
#: from it and `cwd` is `REPO`, so the relative name resolves to the same file.
SOULFORGE_GATE_PATH = "tools/soulforge_gate.py"
SOULFORGE_GATE = REPO / SOULFORGE_GATE_PATH
#: Bounded below the hook's own `timeout 300` around this file: a wedged exe
#: must be named by the gate, not inherited by the commit.
SOULFORGE_BUDGET = 280

GENERATED_SUFFIXES = (".ppm", ".png", ".log", ".jsonl", ".html")
GENERATED_DIRS = ("output/", "graphify-out/", "backup/")
#: Dated machine snapshots: state/<name>-YYYY-MM-DD.json. These are
#: regenerated whole by engines (proffer, manifests, recipe snapshots), so a
#: 300-line regeneration is the file doing its job, not hidden dirt --
#: harness improvement #4 (2026-11-06; the corporate commit's proffer
#: rewrite tripped the per-file cap). Narrow on purpose: bare state/*.json
#: and undated names stay judged like source.
STATE_SNAPSHOT_RE = re.compile(
    r"^state/[A-Za-z0-9_][A-Za-z0-9_.-]*-\d{4}-\d{2}-\d{2}\.json$")

#: Whole-file generators, keyed by the exact repo-relative path they OWN.
#:
#: An entry is a claim that one named tool rewrites this file top to bottom, so
#: a large diff is the generator doing its job rather than hidden dirt -- the
#: same reasoning as STATE_SNAPSHOT_RE, measured 2026-11-14: regenerating
#: ``docs/INDEX.md`` touched 218 lines of a file no human edited and needed
#: ``ALLOW_BULK_COMMIT=1`` to land, which is a declaration spent on a non-event.
#:
#: **Exact paths only.** No globs, no suffixes: ``docs/*.md`` would exempt every
#: hand-written document in the tree, and a suffix rule would exempt the next
#: one silently. The generator is named so tests/test_commit_gate.py can verify
#: the claim against that tool's own source instead of trusting this table.
GENERATED_PATHS = {
    "docs/INDEX.md": "tools/docs_index.py",
    # 2026-11-14: same shape, different owner. `shard_intake.py` rewrites the
    # index top to bottom (`INDEX.write_text(render_index(...))`), so a
    # regeneration of it measured 43,345 lines against a 150/file cap -- a
    # declaration demanded for bytes no human wrote. Canon already names
    # SHARD_INDEX.json among the files nobody hand-edits.
    "Project_ELIZA/shards/SHARD_INDEX.json": "Project_ELIZA/tools/shard_intake.py",
    # 2026-11-16: the two basedpyright artifacts are written by
    # `tools/type_check_gate.py` (BASELINE / REPORT at lines 97-98) on every
    # run, so a re-baseline of either is machine bytes, not hidden dirt.
    "logs/basedpyright_report.json": "tools/type_check_gate.py",
    "logs/basedpyright_baseline.json": "tools/type_check_gate.py",
    # 2026-11-16: `ARC/esquire/pins.json` was the LAST commit the push range
    # refused -- 155/51 lines in one file, and every reader of it is read-only
    # (`esquire_pins.py`, `arc_pin_audit.py`, `arc_check.py`), so a re-dump was
    # by construction a hand edit of a machine-shaped registry. The repair was
    # to give the file the owner it lacked, not to widen this table:
    # `tools/arc_ledger.py` renders it and reproduces HEAD's blob byte for byte
    # (verified: 29,320 bytes + newline = 29,321, identical=True).
    "ARC/esquire/pins.json": "tools/arc_ledger.py",
}


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       timeout=60, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr[:200]))
    return r.stdout


def staged_numstat() -> list[tuple[int, int, str]]:
    """[(added, deleted, path)] for the index. Binary files report -/-."""
    rows = []
    for line in _git("diff", "--cached", "--numstat").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        try:
            added, deleted = int(parts[0]), int(parts[1])
        except ValueError:
            added, deleted = -1, -1  # binary
        rows.append((added, deleted, parts[2]))
    return rows


def staged_statuses() -> dict[str, str]:
    """path -> XY status for staged entries (A = newly created)."""
    out: dict[str, str] = {}
    for line in _git("status", "--short").splitlines():
        if len(line) > 3 and line[0] != " " and line[0] != "?":
            out[line[3:].strip()] = line[:2]
    return out


def commits_in_range(base: str) -> list[tuple[str, list[str], str]]:
    """[(sha, parents, message)] oldest-first for `base..HEAD`.

    One `git log` for the whole range, with the parents carried in the format:
    the loop below needs to know which commits are merges, and asking that per
    commit would spend a subprocess per commit to learn one word.
    """
    raw = _git("log", "--reverse", "--format=%H%x1f%P%x1f%B%x1e",
               "%s..HEAD" % base)
    out = []
    for chunk in raw.split("\x1e"):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        sha, _, rest = chunk.partition("\x1f")
        parents, _, message = rest.partition("\x1f")
        out.append((sha.strip(), parents.split(), message))
    return out


def _numstat_rows(raw: str) -> list[tuple[int, int, str]]:
    rows = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        try:
            added, deleted = int(parts[0]), int(parts[1])
        except ValueError:
            added, deleted = -1, -1  # binary
        rows.append((added, deleted, parts[2]))
    return rows


def commit_numstat(rev: str) -> list[tuple[int, int, str]]:
    """[(added, deleted, path)] for ONE commit's own changeset.

    `--root` makes a root commit report its whole tree as additions instead of
    an empty diff (it has no parent to differ from), so the first commit of a
    range is judged like any other.

    A MERGE PRINTS NOTHING HERE, and that is diff-tree's default rather than a
    failure: a merge differs from two parents at once, so "the diff" has no
    single answer. `merge_extra_rows` asks the only question left.
    """
    return _numstat_rows(_git("diff-tree", "--no-commit-id", "--numstat", "-r",
                              "--root", rev))


def commit_statuses(rev: str) -> dict[str, str]:
    """path -> status letter for ONE commit (A = that commit created it)."""
    out: dict[str, str] = {}
    for line in _git("diff-tree", "--no-commit-id", "--name-status", "-r",
                     "--root", rev).splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            out[parts[-1].strip()] = parts[0].strip()
    return out


def merge_extra_rows(rev: str) -> list[tuple[int, int, str]]:
    """Paths a MERGE changed relative to EVERY parent -- its own hand edits.

    `--cc` prints only files that differ from all parents at once, which is
    exactly an evil-merge resolution: a clean merge prints no rows. `-m` is
    wrong here -- it prints each parent's diff and so counts every merged-in
    file as if the merge had edited it (measured 2026-11-16). A combined diff
    carries no line counts, so these are counted like binary rows: in the file
    tally, out of the line tally.
    """
    rows = []
    for line in _git("diff-tree", "--no-commit-id", "--cc", "--raw", "-r",
                     rev).splitlines():
        if "\t" not in line:
            continue
        head, path = line.split("\t", 1)
        fields = head.split()
        status = fields[-1] if fields else ""
        if path.strip() and any(ch not in "." for ch in status):
            rows.append((-1, -1, path.strip()))
    return rows


def _subject(message: str) -> str:
    """First non-blank line of a message, for naming a commit in a refusal."""
    for line in (message or "").splitlines():
        if line.strip():
            return line.strip()
    return "(no message)"


def commit_violations(base: str, max_lines: int, max_files: int
                      ) -> tuple[list[str], int, int, int, int, int]:
    """Judge `base..HEAD` ONE COMMIT AT A TIME.

    Returns (problems, judged, declared, clean_merges, evil_merges, generated).

    WHY PER COMMIT AND NOT PER RANGE (2026-11-16). The caps are per-commit
    numbers -- 8 files, 150 changed lines in one file -- and this gate applied
    them to `git diff base HEAD`: the UNION of the whole range. A push of 29
    focused commits therefore read as one 1,215-file changeset carrying 24
    oversized files, and the only way through was `ALLOW_BULK_COMMIT=1`: a
    declaration spent on work that had already been split correctly, which is
    what that constant is explicitly not for.

    The union had a second defect, worse than the arithmetic. It has no
    message, so "the commit's own message declares bulk" had already needed a
    narrowing (2026-11-03) to survive contact with a range at all. Judging each
    commit restores the rule instead of special-casing it: a commit's message
    authorises that commit, and nothing else in the range.
    """
    problems: list[str] = []
    judged = declared = clean_merges = evil_merges = generated = 0
    for sha, parents, message in commits_in_range(base):
        short = sha[:8]
        if declares_bulk(message):
            declared += 1
            print("commit-gate: %s declares bulk in its own message -- excused "
                  "(its neighbours are still judged)" % short)
            continue
        if len(parents) > 1:
            rows = merge_extra_rows(sha)
            if not rows:
                clean_merges += 1
                continue
            evil_merges += 1
            created: set[str] = set()
            print("commit-gate: %s is a MERGE that changed %d path(s) relative "
                  "to every parent -- counted, not skipped: %s"
                  % (short, len(rows), ", ".join(r[2] for r in rows[:6])))
        else:
            rows = commit_numstat(sha)
            created = {p for p, s in commit_statuses(sha).items() if "A" in s}
        judged += 1
        if not rows:
            continue
        generated += len([r for r in rows if r[2] and is_generated(r[2])])
        problems.extend(evaluate(
            rows, max_lines, max_files, created,
            changeset="files in %s (%s)" % (short, _subject(message)[:64]),
            remedy="Declare the bulk op in the message of %s -- a commit "
                   "message authorises that commit only -- or split it."
                   % short,
            file_remedy="Split %s, or declare the bulk op in its own message."
                        % short))
    return problems, judged, declared, clean_merges, evil_merges, generated


def declares_bulk(message: str) -> bool:
    """True when a commit message carries the bulk declaration.

    AGENTS.md names the commit MESSAGE as the place to declare a bulk operation
    ("never rebaseline a scanner finding ... or declare ALLOW_BULK_COMMIT=1 in
    the message"). Pre-commit honoured only the env var, and that was enough
    while the push never re-judged the commit. Commit mode re-judges it, so a
    commit that was deliberately declared bulk would be refused on the way out
    by a gate that cannot see the declaration -- measured 2026-11-03 on
    12e47073, whose message declares it and whose 5,750-line generated ledger
    the range check then flagged.
    """
    return "ALLOW_BULK_COMMIT=1" in (message or "")


def single_commit_bulk_declaration(base: str) -> str | None:
    """The pushed commit's sha if it is exactly one commit that declares bulk.

    NARROW ON PURPOSE. The first version accepted a declaration from ANY commit
    in the range, and over a normal history every range contains one (28 of the
    last 90 commits declared something), so the range check could no longer fail
    at all -- a gate that answers PASS to everything is the defect this file
    exists to catch, not a feature. A commit message describes the commit it is
    attached to, so the declaration counts only when the range IS that commit
    (`base..HEAD` = 1). A multi-commit push has no single message describing it
    and is judged by the caps like anything else.
    """
    commits = commits_in_range(base)
    if len(commits) != 1:
        return None
    sha, _parents, message = commits[0]
    return sha if declares_bulk(message) else None


def worktree_status() -> list[tuple[str, str]]:
    """[(xy, path)] for worktree + index (porcelain)."""
    rows = []
    for line in _git("status", "--short").splitlines():
        if len(line) > 3:
            rows.append((line[:2].strip(), line[3:].strip()))
    return rows


def is_generated(path: str) -> bool:
    p = path.replace("\\", "/")
    if p in GENERATED_PATHS:
        return True
    if any(p.startswith(d) for d in GENERATED_DIRS):
        return True
    if STATE_SNAPSHOT_RE.match(p):
        return True
    return p.lower().endswith(GENERATED_SUFFIXES)


def evaluate(rows: list[tuple[int, int, str]], max_lines: int,
             max_files: int, created: set[str] | None = None,
             changeset: str = "staged files",
             remedy: str = "Stage a focused set, or set "
                          "ALLOW_BULK_COMMIT=1 to declare a bulk op.",
             file_remedy: str = "Split it, or set ALLOW_BULK_COMMIT=1."
             ) -> list[str]:
    """Bulk violations, human-readable. Empty means pass.

    `changeset` names what the rows are ("staged", or a `base..HEAD` range). It
    is only wording, but a refusal that says "staged" over a commit range names
    the wrong desk -- the operator goes looking for a staging mistake that does
    not exist. The count is the same either way; only the noun changes. The
    same goes for `remedy`/`file_remedy`: "stage a focused set" is not
    actionable advice about a commit that is already written, and an operator
    who follows it will find nothing to unstage.

    Newly created files are exempt from the per-file line cap: a create
    carries no hidden dirt (everything in it is new by definition), while
    a 400-line modification to a tracked file is exactly the sweep this
    gate exists to catch. Creates still count toward the file tally.

    Generated artifacts (is_generated) are exempt from BOTH tallies: the
    advisory `review` command already reports them separately, so the
    blocking path must not demand a bulk declaration for bytes no human
    wrote. Generated files cannot rescue an otherwise-blocked changeset --
    the source rows are judged exactly as if the generated rows were
    absent.
    """
    created = created or set()
    problems = []
    tracked = [r for r in rows if r[2] and not r[2].startswith("(")]
    tracked = [r for r in tracked if not is_generated(r[2])]
    if len(tracked) > max_files:
        problems.append(
            "%d %s exceed the bulk limit (%d). %s"
            % (len(tracked), changeset, max_files, remedy))
    for added, deleted, path in tracked:
        if added < 0:
            continue  # binary: counted in the file tally, not line tally
        if path in created:
            continue  # new file: nothing hidden inside
        if added + deleted > max_lines:
            problems.append(
                "%s changes %d lines (limit %d/file). %s"
                % (path, added + deleted, max_lines, file_remedy))
    return problems


def soulforge_proof() -> int:
    """Prove SOULFORGE from the built binary when this commit touches it.

    WHY IT IS DELEGATED AND NOT INLINED. `.githooks/pre-commit` runs this file as
    its first check, which makes `cmd_hook` the one surface that executes before
    every commit -- so a proof placed here cannot be skipped by a lane that never
    reads the tier. The proof itself lives in `tools/soulforge_gate.py` because
    the tier registers the same file: one implementation, two callers. A second
    copy here would drift, and the tier would keep certifying a binary the commit
    path had stopped checking.

    A MISSING SCRIPT PASSES LOUD, like every other unreadable gate in this file:
    refusing all commits because an untracked helper is absent would block the
    very commit that adds it. The tool returns 0 with a printed skip when the
    index touches nothing under `tools/swarm_arena/`, so an unrelated commit
    pays one subprocess and one line.
    """
    if not SOULFORGE_GATE.is_file():
        print("commit-gate: %s is absent -- the SOULFORGE proof did not run"
              % SOULFORGE_GATE)
        return 0
    try:
        result = subprocess.run(
            [sys.executable, SOULFORGE_GATE_PATH, "--staged"],
            cwd=str(REPO), capture_output=True, text=True, timeout=SOULFORGE_BUDGET,
            encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("commit-gate: the SOULFORGE proof could not finish (%s)" % exc)
        return 1
    for line in (result.stdout or "").strip().splitlines():
        print("  %s" % line)
    if result.returncode == 0:
        return 0
    print("  Fix: python tools/swarm_arena/build_soulforge.py"
          " (a stale or missing binary has to be rebuilt, not declared)")
    return 1


def cmd_hook(base: str | None = None) -> int:
    """Judge a changeset. `base` names a commit (`base..HEAD`); None = the index.

    The two scopes are different questions. Pre-commit asks "is what I am about
    to commit too big"; a push asks "is the commit I am leaving with too big",
    and the index cannot answer the second: it also holds whatever another lane
    staged while this one worked. So a named base replaces the index rather than
    adding to it -- a run that judged both would still be refused by the
    neighbour's desk drawer, which is the defect --base exists to remove.
    """
    # Before the bulk checks and before ALLOW_BULK_COMMIT: declaring a bulk op
    # makes a changeset big, it does not make a stale binary proved. A push
    # range (`base`) is left to the tier's own row, which proves the same binary
    # from the tree -- the index at push time also holds whatever another lane
    # staged, and this proof must be about the commit's paths.
    if base is None:
        soulforge = soulforge_proof()
        if soulforge:
            return soulforge
    max_lines = int(os.environ.get("COMMIT_GATE_MAX_LINES",
                                   str(DEFAULT_MAX_LINES)))
    max_files = int(os.environ.get("COMMIT_GATE_MAX_FILES",
                                   str(DEFAULT_MAX_FILES)))
    if os.environ.get("ALLOW_BULK_COMMIT") == "1":
        print("commit-gate: bulk declared via ALLOW_BULK_COMMIT=1, passing")
        return 0
    scope = "%s..HEAD" % base if base else "the staged index"
    if base:
        # ONE COMMIT, ALREADY AUTHORISED: the fast path, kept because "the
        # range's message" is unambiguous in exactly this case. It answers the
        # same question as the loop below and authorises nothing wider.
        try:
            declared = single_commit_bulk_declaration(base)
        except Exception as exc:  # noqa: BLE001 - a named range must be readable
            print("commit-gate: cannot read the messages of %s (%s) -- refusing "
                  "to pass on a range that was not read" % (scope, exc))
            return 1
        if declared:
            print("commit-gate: bulk declared in the message of %s, passing "
                  "(%s)" % (declared[:8], scope))
            return 0
        try:
            problems, judged, declared_n, merges, evil, gen = commit_violations(
                base, max_lines, max_files)
        except Exception as exc:
            # A NAMED base that cannot be read is a caller error, not a broken
            # gate: passing loud here would go green on a range never read (a
            # typo, or a ref this clone does not have).
            print("commit-gate: cannot read %s (%s) -- refusing to pass on a "
                  "range that was not read" % (scope, exc))
            return 1
        if judged + declared_n + merges == 0:
            # An empty range is a wrong base far more often than a clean one.
            print("commit-gate: %s is empty -- nothing to judge" % scope)
            return 0
        if gen:
            print("commit-gate: %d generated file(s) across %s -- exempt from "
                  "bulk caps (review: python scripts/commit_gate.py review)"
                  % (gen, scope))
        if problems:
            print("commit-gate: BULK CHANGESET BLOCKED")
            for p in problems:
                print("  - " + p)
            print("  Judged per commit: %d commit(s) on their own changeset, "
                  "%d excused by their own message, %d clean merge(s) skipped, "
                  "%d merge(s) with their own edits."
                  % (judged, declared_n, merges, evil))
            print("  Review with: git show --stat <the sha named above>")
            return 1
        print("commit-gate: %d commit(s) in %s judged on their own changeset, "
              "each within the caps (%d excused by their own message, %d clean "
              "merge(s) skipped, %d merge(s) with their own edits)"
              % (judged, scope, declared_n, merges, evil))
        return 0
    try:
        rows = staged_numstat()
        statuses = staged_statuses()
    except Exception as exc:
        # A broken gate must never block all commits; be loud instead.
        print("commit-gate: cannot read staged diff (%s) -- passing loud" % exc)
        return 0
    if not rows:
        return 0
    created = {p for p, s in statuses.items() if "A" in s}
    gen_count = len([r for r in rows if r[2] and is_generated(r[2])])
    if gen_count:
        print("commit-gate: %d generated file(s) in %s -- exempt from bulk "
              "caps (review: python scripts/commit_gate.py review)"
              % (gen_count, scope))
    problems = evaluate(rows, max_lines, max_files, created)
    if not problems:
        return 0
    print("commit-gate: BULK CHANGESET BLOCKED")
    for p in problems:
        print("  - " + p)
    print("  Review with: python scripts/commit_gate.py review")
    return 1


def cmd_review() -> int:
    rows = worktree_status()
    if not rows:
        print("worktree clean")
        return 0
    src = [(s, p) for s, p in rows if not is_generated(p)]
    gen = [(s, p) for s, p in rows if is_generated(p)]
    print("=== source (%d) ===" % len(src))
    for s, p in src:
        print("  [%s] %s" % (s or "?", p))
    if gen:
        print("=== generated (%d, never stage these) ===" % len(gen))
        for s, p in gen[:15]:
            print("  [%s] %s" % (s or "?", p))
        if len(gen) > 15:
            print("  ... and %d more" % (len(gen) - 15))
    print()
    print("Stage exactly what your message will describe, e.g.:")
    print("  git add <file> ... && git commit -m \"...\"")
    print("Bulk ops: ALLOW_BULK_COMMIT=1 git commit ...")
    return 0


def main(argv=None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    base = None
    if "--base" in args:
        at = args.index("--base")
        if at + 1 >= len(args):
            print("commit_gate.py: --base needs a revision")
            return 2
        base = args[at + 1]
        del args[at:at + 2]
    if "--hook" in args:
        return cmd_hook(base)
    if "review" in args:
        return cmd_review()
    print(__doc__.strip().splitlines()[0])
    print("usage: commit_gate.py [--hook [--base REV] | review]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
