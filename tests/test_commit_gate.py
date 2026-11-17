"""Tests for scripts/commit_gate.py.

Mostly pure bulk-detection logic (evaluate()/is_generated()). The two scope
questions -- "how big is my index" vs "how big is the commit I am pushing" --
are exercised against a throwaway repo, because the difference between them is
the whole point of --base and cannot be seen in a pure function.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import commit_gate as cg


def test_small_changeset_passes():
    rows = [(5, 2, "src/a.py"), (10, 0, "src/b.py")]
    assert cg.evaluate(rows, 150, 8) == []


def test_big_file_blocked():
    rows = [(200, 60, "src/CORE/local_memory.py")]
    problems = cg.evaluate(rows, 150, 8)
    assert len(problems) == 1
    assert "local_memory.py" in problems[0]


def test_too_many_files_blocked():
    rows = [(1, 1, "f%d.py" % i) for i in range(9)]
    problems = cg.evaluate(rows, 150, 8)
    assert any("9 staged files" in p for p in problems)


def test_binary_counted_not_measured():
    rows = [(-1, -1, "asset.ppm")]
    assert cg.evaluate(rows, 150, 8) == []


def test_new_files_exempt_from_line_cap():
    rows = [(400, 0, "research/NEW_DESIGN.md")]
    # Untracked-origin unknown: flagged (created set not consulted).
    assert cg.evaluate(rows, 150, 8) != []
    assert cg.evaluate(rows, 150, 8, created=set()) != []
    assert cg.evaluate(rows, 150, 8,
                       created={"research/NEW_DESIGN.md"}) == []


def test_new_files_still_count_toward_file_tally():
    rows = [(-1, -1, "n%d.bin" % i) for i in range(9)]
    assert any("9 staged files" in p for p in cg.evaluate(rows, 150, 8))


def test_generated_classification():
    assert cg.is_generated("output/matrix_frames/frame_1.ppm")
    assert cg.is_generated("graphify-out/2026-09-28/graph.json")
    assert cg.is_generated("dashboard/monitor_x.html")
    assert not cg.is_generated("scripts/chain_controller.py")
    assert not cg.is_generated("src/CORE/local_memory.py")


def test_generated_exempt_from_both_tallies():
    # Graph rebuild + render artifacts: huge, but no human wrote a line.
    rows = [(900, 0, "graphify-out/graph.json"),
            (5000, 10, "output/render/frames.log")]
    assert cg.evaluate(rows, 150, 8) == []


def test_generated_path_is_an_owned_whole_file_artifact():
    # 2026-11-14: regenerating the index touched 218 lines of a generated file
    # and needed ALLOW_BULK_COMMIT=1 to land -- a declaration spent on a
    # non-event, and the reason this rule exists.
    assert cg.is_generated("docs/INDEX.md")
    assert cg.evaluate([(200, 18, "docs/INDEX.md")], 150, 8) == []

    # The claim is verified against the GENERATOR's source, not this table:
    # an entry whose tool stopped writing the file fails here instead of
    # quietly exempting a hand-edited document forever.
    for path, generator in cg.GENERATED_PATHS.items():
        source = (ROOT / generator).read_text(encoding="utf-8")
        assert Path(path).name in source, (path, generator)

    # Exact paths only: siblings and case variants stay judged like source.
    assert not cg.is_generated("docs/HANDOFF_2026-11-14.md")
    assert not cg.is_generated("docs/index.md")
    assert not cg.is_generated("docs/INDEX.md.bak")
    assert cg.evaluate([(200, 18, "docs/HANDOFF_2026-11-14.md")], 150, 8) != []


def test_state_snapshot_classification():
    # Harness improvement #4 (2026-11-06): dated machine snapshots under
    # state/ are regenerated whole by engines -- a 300-line proffer rewrite
    # is the file doing its job, not hidden dirt.
    assert cg.is_generated("state/oxenford-proffer-2026-11-06.json")
    assert cg.is_generated("state/adopt-recipes-2026-11-06.json")
    assert not cg.is_generated("state/head.json")
    assert cg.is_generated("state/bake_harvest_freebuff_2026-11-06.jsonl")  # .jsonl suffix already exempt
    assert not cg.is_generated("state/notes.json")
    assert not cg.is_generated("src/CORE/local_memory.py")


def test_state_snapshot_regeneration_passes_line_cap():
    rows = [(300, 33, "state/oxenford-proffer-2026-11-06.json"),
            (150, 35, "state/oxenford-wheelhouse-manifest-2026-11-06.json")]
    assert cg.evaluate(rows, 150, 8) == []


def test_state_snapshot_cannot_rescue_blocked_source():
    # Negative control: the exemption covers snapshots only -- 9 source
    # files stay blocked next to regenerated snapshots.
    rows = [(1, 1, "src/f%d.py" % i) for i in range(9)]
    rows += [(300, 33, "state/oxenford-proffer-2026-11-06.json")]
    problems = cg.evaluate(rows, 150, 8)
    assert any("9 staged files" in p for p in problems)


def test_generated_cannot_rescue_blocked_changeset():
    # Negative control: exempting generated rows must not weaken the cap
    # on source rows -- 9 source files stay blocked next to 40 generated.
    rows = [(1, 1, "src/f%d.py" % i) for i in range(9)]
    rows += [(400, 0, "graphify-out/g%d.json" % i) for i in range(40)]
    problems = cg.evaluate(rows, 150, 8)
    assert any("9 staged files" in p for p in problems)


def test_generated_line_flood_still_blocked_for_tracked_source():
    # A tracked source file over the line cap is judged alone, even when
    # generated rows dominate the changeset numerically.
    rows = [(200, 60, "src/CORE/local_memory.py"),
            (3000, 0, "graphify-out/graph.html")]
    problems = cg.evaluate(rows, 150, 8)
    assert len(problems) == 1
    assert "local_memory.py" in problems[0]


# ── scope wording ──────────────────────────────────────────────────────────
# "Stage a focused set" is correct advice about an index and useless advice
# about a commit that is already written: the operator goes looking for a
# staging mistake that does not exist. Both directions are asserted, because a
# remedy that silently disappears from the index path is a regression too.

def test_index_scope_refusal_still_says_stage():
    rows = [(1, 1, "f%d.py" % i) for i in range(9)]
    assert any("Stage a focused set" in p for p in cg.evaluate(rows, 150, 8))


def test_commit_scope_refusal_names_the_commit_not_the_index():
    rows = [(1, 1, "f%d.py" % i) for i in range(9)]
    problems = cg.evaluate(
        rows, 150, 8,
        changeset="files in base..HEAD",
        remedy="Declare the bulk op in a commit message.",
        file_remedy="Split the commit.")
    assert any("files in base..HEAD" in p for p in problems)
    assert not any("Stage a focused set" in p for p in problems)


def test_commit_scope_file_cap_does_not_tell_a_commit_to_stage():
    rows = [(200, 60, "src/CORE/local_memory.py")]
    problems = cg.evaluate(rows, 150, 8,
                           file_remedy="Split the commit.")
    assert problems and "Split the commit." in problems[0]
    assert "ALLOW_BULK_COMMIT=1" not in problems[0]


# ── the bulk declaration authorises ONE commit, not a range ────────────────

def _repo(tmp_path, monkeypatch):
    """A throwaway repo with two commits, frozen config, no inherited hooks."""
    monkeypatch.chdir(tmp_path)

    def run(*args):
        subprocess.run(["git", *args], check=True, capture_output=True,
                       text=True, timeout=60)

    run("init", "-q")
    run("config", "user.email", "gate@example.invalid")
    run("config", "user.name", "gate test")
    run("config", "commit.gpgsign", "false")
    run("config", "core.hooksPath", str(tmp_path / "no-hooks"))
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    run("add", "a.txt")
    run("commit", "-q", "-m", "first")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    run("add", "b.txt")
    run("commit", "-q", "-m", "second, no declaration")
    return run, tmp_path


def test_undeclared_commit_is_not_authorised(tmp_path, monkeypatch):
    _repo(tmp_path, monkeypatch)
    assert cg.single_commit_bulk_declaration("HEAD~1") is None


def test_declared_commit_authorises_itself(tmp_path, monkeypatch):
    run, p = _repo(tmp_path, monkeypatch)
    (p / "c.txt").write_text("c", encoding="utf-8")
    run("add", "c.txt")
    run("commit", "-q", "-m", "untrack: ALLOW_BULK_COMMIT=1 (frame sweep)")
    head = cg._git("rev-parse", "HEAD").strip()
    assert cg.single_commit_bulk_declaration("HEAD~1") == head


def test_declaration_does_not_authorise_a_wider_range(tmp_path, monkeypatch):
    """NEGATIVE CONTROL for the narrowing (2026-11-03).

    The first version accepted a declaration from any commit in the range. Over
    a real history that is always true (28 of 90 sampled commits declared
    something), so the range check could never fail. A commit message describes
    the commit it hangs on, so a declaring commit inside a multi-commit range
    authorises nothing.
    """
    run, p = _repo(tmp_path, monkeypatch)
    (p / "c.txt").write_text("c", encoding="utf-8")
    run("add", "c.txt")
    run("commit", "-q", "-m", "untrack: ALLOW_BULK_COMMIT=1 (frame sweep)")
    assert cg.single_commit_bulk_declaration("HEAD~1") is not None
    assert cg.single_commit_bulk_declaration("HEAD~2") is None


# ── per commit, not per range (2026-11-16) ─────────────────────────────────
# The caps are per-commit numbers (8 files, 150 changed lines in one file) and
# this gate applied them to `git diff base HEAD`, the UNION of the push range.
# A 29-commit push therefore read as one 1,215-file changeset with 24 oversized
# files, and the only way through was ALLOW_BULK_COMMIT=1 -- a declaration spent
# on work that had already been split correctly. The union also has no message,
# which is why the "own message" rule had already needed a narrowing in 2026-11.
#
# These tests execute git, not a fixture of my own integers: the union rows that
# fail are produced by `git diff --numstat base HEAD`, which is the exact
# command the removed code ran.

def _numstat(text):
    rows = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            rows.append((int(parts[0]), int(parts[1]), parts[2]))
    return rows


def _branch():
    return subprocess.run(["git", "symbolic-ref", "--short", "HEAD"],
                          capture_output=True, text=True, check=True,
                          timeout=60).stdout.strip()


def _lines(prefix, count=200):
    return "".join("%s%d\n" % (prefix, i) for i in range(count))


def test_a_range_of_small_commits_is_not_one_changeset(tmp_path, monkeypatch):
    run, p = _repo(tmp_path, monkeypatch)
    for i in range(12):
        (p / ("s%d.txt" % i)).write_text("x\n", encoding="utf-8")
        run("add", "s%d.txt" % i)
        run("commit", "-q", "-m", "small %d" % i)
    base = cg._git("rev-parse", "HEAD~12").strip()

    # Negative control: the union really does exceed the cap that every commit
    # in it satisfies. Without this line the test passes on a range that could
    # never have failed, which proves nothing.
    union = _numstat(subprocess.run(["git", "diff", "--numstat", base, "HEAD"],
                                    capture_output=True, text=True, check=True,
                                    timeout=60).stdout)
    assert len(union) == 12
    assert cg.evaluate(union, 150, 8) != []

    problems, judged, declared, merges, evil, _gen = cg.commit_violations(
        base, 150, 8)
    assert problems == []
    assert (judged, declared, merges, evil) == (12, 0, 0, 0)


def test_an_oversized_commit_is_named_by_its_own_sha(tmp_path, monkeypatch):
    run, p = _repo(tmp_path, monkeypatch)
    (p / "big.txt").write_text("x\n", encoding="utf-8")
    run("add", "big.txt")
    run("commit", "-q", "-m", "track big")
    (p / "big.txt").write_text(_lines("line"), encoding="utf-8")
    run("add", "big.txt")
    run("commit", "-q", "-m", "sweep 200 lines")

    sha = cg._git("rev-parse", "HEAD").strip()[:8]
    problems, judged, declared, _m, _e, _gen = cg.commit_violations(
        "HEAD~1", 150, 8)
    assert (judged, declared) == (1, 0)
    assert len(problems) == 1
    # A refusal that does not name the commit to fix is not actionable on a
    # 29-commit push: it is the whole reason the union was unusable.
    assert sha in problems[0]
    assert "big.txt" in problems[0]


def test_a_declaration_authorises_only_its_own_commit(tmp_path, monkeypatch):
    run, p = _repo(tmp_path, monkeypatch)
    (p / "bulk.txt").write_text("x\n", encoding="utf-8")
    (p / "quiet.txt").write_text("x\n", encoding="utf-8")
    run("add", "bulk.txt", "quiet.txt")
    run("commit", "-q", "-m", "track both")

    (p / "bulk.txt").write_text(_lines("a"), encoding="utf-8")
    run("add", "bulk.txt")
    run("commit", "-q", "-m", "sweep: ALLOW_BULK_COMMIT=1 (frame untrack)")
    (p / "quiet.txt").write_text(_lines("b"), encoding="utf-8")
    run("add", "quiet.txt")
    run("commit", "-q", "-m", "quiet 200 lines")

    declared_sha = cg._git("rev-parse", "HEAD~1").strip()[:8]
    loud_sha = cg._git("rev-parse", "HEAD").strip()[:8]
    problems, judged, declared, _m, _e, _gen = cg.commit_violations(
        "HEAD~2", 150, 8)
    # The declaring commit is excused and never judged; its neighbour is judged
    # and refused. Both halves matter: excusing the neighbour is the 2026-11-03
    # defect, and refusing the declarer is the 2026-11-16 one.
    assert (judged, declared) == (1, 1)
    assert len(problems) == 1
    assert loud_sha in problems[0]
    assert declared_sha not in problems[0]


def test_a_clean_merge_is_skipped_and_counted(tmp_path, monkeypatch):
    run, p = _repo(tmp_path, monkeypatch)
    main = _branch()
    run("checkout", "-q", "-b", "side")
    (p / "side.txt").write_text("s\n", encoding="utf-8")
    run("add", "side.txt")
    run("commit", "-q", "-m", "side work")
    run("checkout", "-q", main)
    (p / "main.txt").write_text("m\n", encoding="utf-8")
    run("add", "main.txt")
    run("commit", "-q", "-m", "main work")
    run("merge", "-q", "--no-ff", "-m", "merge side", "side")

    problems, judged, declared, merges, evil, _gen = cg.commit_violations(
        "HEAD~2", 150, 8)
    # diff-tree prints nothing for a merge; that is its default, not a clean
    # bill of health. The merge is COUNTED as skipped so a 29-commit push report
    # cannot claim it judged something it never read.
    assert problems == []
    assert (judged, declared, merges, evil) == (2, 0, 1, 0)


def test_an_evil_merge_is_counted_and_named(tmp_path, monkeypatch, capsys):
    run, p = _repo(tmp_path, monkeypatch)
    main = _branch()
    (p / "shared.txt").write_text("base\n", encoding="utf-8")
    run("add", "shared.txt")
    run("commit", "-q", "-m", "shared base")
    run("checkout", "-q", "-b", "t1")
    (p / "shared.txt").write_text("theirs\n", encoding="utf-8")
    run("add", "shared.txt")
    run("commit", "-q", "-m", "theirs")
    run("checkout", "-q", main)
    (p / "shared.txt").write_text("ours\n", encoding="utf-8")
    run("add", "shared.txt")
    run("commit", "-q", "-m", "ours")
    conflict = subprocess.run(["git", "merge", "t1"], capture_output=True,
                              text=True, timeout=60)
    # Fixture self-check: no conflict means no evil merge, and this test would
    # otherwise pass while exercising nothing.
    assert conflict.returncode != 0
    (p / "shared.txt").write_text("resolved by hand\n", encoding="utf-8")
    run("add", "shared.txt")
    run("commit", "-q", "-m", "merge t1")

    sha = cg._git("rev-parse", "HEAD").strip()[:8]
    problems, judged, declared, merges, evil, _gen = cg.commit_violations(
        "HEAD~1", 150, 8)
    assert (merges, evil) == (0, 1)
    assert problems == []          # one hand-resolved file is within the caps
    assert sha in capsys.readouterr().out   # but it is never skipped silently
