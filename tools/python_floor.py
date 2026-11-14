"""Measure what each project root's tracked Python actually needs, and whether it says so.

The tree is asked to be "platform agnostic, native Python, all versions, back to
3.6".  That is three separate claims and only one of them is a matter of taste:

  * **floor** -- the highest syntax or runtime feature any tracked file in the
    root needs.  This is a measurement, not a policy.
  * **declared** -- the `requires-python` the root publishes.  This is a claim.
  * **coupling** -- OS-specific imports and absolute drive paths.  This is a
    measurement, and it is what makes "platform agnostic" checkable.

The defect classes are the two ways the claim and the measurement can disagree:

  under_declared   declared floor is LOWER than the code's floor.  The root
                   promises an interpreter on which it cannot import.
  over_declared    declared floor is HIGHER than the code's floor.  The root
                   refuses an interpreter its own source would run on -- this is
                   the class that blocks backward compatibility, and it is
                   fixable by editing one line, never by rewriting the code.
  undeclared       ships Python and publishes no floor at all, so packaging
                   tools assume "any" and pip will try it on 3.6.

Nothing here rewrites code.  Lowering a floor to what the code already proves it
can run is a declaration change; raising code's floor is a rewrite.  This tool
keeps those two operations distinct, which is the only way the ladder down to 3.6
can be walked without deleting language features to fake it.

Reads `git ls-files` (tracked surface only), so an untracked experiment cannot
move a project's floor.

  python tools/python_floor.py                # table
  python tools/python_floor.py --check        # exit 1 on any finding
  python tools/python_floor.py --strict-os    # OS coupling is a finding too
  python tools/python_floor.py --json out.json
  python tools/python_floor.py --target 3.6   # report distance to a target floor
  python tools/python_floor.py --only Project_ELIZA   # one tree, its own denominator
"""
import ast
import json
import re
import subprocess
import sys
from collections import defaultdict

#: path fragments whose contents are generated, vendored or historical
SKIP = (
    "/adopted/", "/archived", "/vendor/", "/site-packages/", "/node_modules/",
    ".pkg-archive", "/build/", "/dist/", "/__pycache__/",
)

#: OS-specific surfaces.  `os` and `sys` themselves are portable; only branching
#: on them, importing a platform module, or naming a drive is coupling.
COUPLING = re.compile(
    r"sys\.platform|os\.name\s*==|platform\.system|winreg|windll|WinDLL|msvcrt|"
    r"os\.startfile|AppData|[A-Za-z]:[\\/]|powershell(\.exe)?|\bcmd\.exe|"
    r"\bwsl\b|win32",
    re.IGNORECASE,
)

#: Version-bearing constructs, highest wins per file.
FEATURES = (
    # (label, version, predicate on a single AST node)
    # `type_params` exists on every function and class in 3.12+, as an EMPTY
    # list when unused.  `is not None` therefore matches every def in the tree
    # and reported the whole repo at a 3.12 floor -- truthiness, not presence.
    ("3.12 pep695", "3.12", lambda n: bool(getattr(n, "type_params", None))),
    ("3.12 type alias", "3.12", lambda n: n.__class__.__name__ == "TypeAlias"),
    ("3.12 itertools.batched", "3.12",
     lambda n: isinstance(n, ast.Attribute) and n.attr == "batched"),
    ("3.11 except*", "3.11", lambda n: n.__class__.__name__ == "TryStar"),
    ("3.11 tomllib", "3.11",
     lambda n: isinstance(n, (ast.Import, ast.ImportFrom))
     and "tomllib" in _imported(n)),
    ("3.13 sys._is_gil_enabled", "3.13",
     lambda n: isinstance(n, ast.Attribute) and n.attr == "_is_gil_enabled"),
    ("3.10 match", "3.10", lambda n: n.__class__.__name__ == "Match"),
    ("3.9 str.remove*prefix", "3.9",
     lambda n: isinstance(n, ast.Attribute)
     and n.attr in ("removeprefix", "removesuffix")),
    ("3.8 walrus", "3.8", lambda n: isinstance(n, ast.NamedExpr)),
    ("3.8 posonly", "3.8",
     lambda n: isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
     and bool(getattr(n.args, "posonlyargs", None))),
    ("3.7 future annotations", "3.7",
     lambda n: isinstance(n, ast.ImportFrom) and n.module == "__future__"
     and any(a.name == "annotations" for a in n.names)),
    ("3.7 dataclasses", "3.7",
     lambda n: isinstance(n, (ast.Import, ast.ImportFrom))
     and "dataclasses" in _imported(n)),
)

#: `f"{value=}"` needs 3.8 and is invisible to the AST walker.
DEBUG_FSTRING = re.compile(r"""\bf["'][^"']*\{[A-Za-z_][A-Za-z0-9_.]*=\}""")

#: Bound on the listing, so a wedged git cannot hang the gate.
LIST_TIMEOUT = 120

#: A finding that PROVES the tree lies about itself, and fails `--check`.
#: Everything else is debt the run prints but does not fail on, because a
#: declaration being wider than the code is a deployment choice (this tree runs
#: production on 3.16t) rather than a false claim -- it becomes a finding only
#: under --strict, where it is the measurement the 3.6 ladder is walked with.
HARD = ("under_declared", "unparsed")

FLOOR_RE = re.compile(
    r"""requires[-_]python["'\s]*[=:]\s*["']?([<>=!~^,\s]*)(\d+\.\d+)""",
    re.IGNORECASE,
)


def _imported(node):
    """Every module name an import node names, flattened to one string."""
    names = []
    for alias in node.names:
        names.append(alias.name)
    module = getattr(node, "module", None)
    if module:
        names.append(module)
    return " ".join(names)


def _ver(text):
    """'3.10' -> (3, 10).  A version this tool cannot parse sorts lowest."""
    try:
        major, minor = text.split(".")[:2]
        return (int(major), int(minor))
    except (ValueError, AttributeError):
        return (0, 0)


def file_floor(tree, text):
    """The highest Python version this one file's source needs, and why."""
    found = ["3.6"]
    why = []
    for node in ast.walk(tree):
        for label, version, test in FEATURES:
            try:
                hit = test(node)
            except (AttributeError, TypeError):
                hit = False
            if hit:
                found.append(version)
                why.append(label)
    if DEBUG_FSTRING.search(text):
        found.append("3.8")
        why.append("3.8 f-string debug")
    return max(found, key=_ver), why


def root_of(path):
    """The publishing unit a tracked path belongs to."""
    parts = path.split("/")
    if parts[0] == "src" and len(parts) > 1:
        return "src/" + parts[1]
    if parts[0] in ("tests", "tools", "scripts"):
        return parts[0]
    return parts[0]


MANIFESTS = ("pyproject.toml", "setup.cfg", "setup.py")


def read_declared(repo, tracked, unreadable, missing=None):
    """{root: (declared_version, source_file)} for every root that declares one.

    `git ls-files "pyproject.toml"` is a pathspec with no wildcard, so it
    matches the file at the repo root and NOT one at any depth -- measured
    2026-11-14: it returned 1 of the 15 manifests, and the tool then reported
    `0 declaring a floor` as if the tree were silent.  One listing, filtered
    here, so the denominator is whatever git actually tracks.
    """
    declared = {}
    for rel in tracked:
        if rel.rsplit("/", 1)[-1] not in MANIFESTS:
            continue
        try:
            text = (repo / rel).read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            # Tracked but absent from the worktree: a deletion or a stale index.
            # That is a different fact from "cannot be read", and reporting it
            # as unreadable sends the reader hunting a permission problem that
            # does not exist.  Keep the two apart wherever a reader can tell.
            (unreadable if missing is None else missing).append(rel)
            continue
        except OSError:
            # A manifest that cannot be read is a root whose claim is unknown,
            # not a root that makes none.  Name it rather than skipping it.
            unreadable.append(rel)
            continue
        match = FLOOR_RE.search(text)
        if not match:
            continue
        root = root_of(rel)
        floor = match.group(2)
        previous = declared.get(root)
        # A root with several manifests keeps the strictest claim it makes.
        if previous is None or _ver(floor) > _ver(previous[0]):
            declared[root] = (floor, rel)
    return declared


def root_default(declared):
    """The repo-root declaration, which covers every root that makes none.

    Without this the tool reported `134 undeclared`, which reads as "no project
    says what Python it needs" -- wrong on the facts, because the root
    `pyproject.toml` declares one floor for the whole tree.  A root that states
    nothing is governed by that floor; only a root with no declaration anywhere
    is genuinely silent, and the two need different repairs.
    """
    for key in MANIFESTS:
        if key in declared:
            return declared[key]
    return None


def census(repo, only=None):
    """Measure every tracked Python file and fold it into its root.

    `only` restricts the census to one tree (a directory prefix), so a CI job
    can report on its own subtree.  Without it the measurement is repo-wide and
    a per-tree job would either re-measure all roots or quote a repo number as
    its own -- the denominator defect the report header exists to prevent.
    """
    try:
        listed = subprocess.run(
            ["git", "ls-files"], cwd=str(repo), timeout=LIST_TIMEOUT,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        print("python_floor: BLIND -- git ls-files exceeded %ds" % LIST_TIMEOUT)
        raise SystemExit(2)
    if listed.returncode != 0:
        raise SystemExit("python_floor: git ls-files failed (rc=%d)" % listed.returncode)
    tracked = [p for p in listed.stdout.splitlines()
               if p and not any(s in "/" + p for s in SKIP)]
    if only:
        prefix = only.strip("/") + "/"
        in_scope = [p for p in tracked if p.startswith(prefix)]
    else:
        in_scope = tracked
    paths = [p for p in in_scope if p.endswith(".py")]

    roots = defaultdict(lambda: {
        "files": 0, "unparsed": 0, "floor": "3.6", "above": defaultdict(int),
        "coupled": 0, "hits": 0, "drivers": defaultdict(int),
    })
    unparsed = []
    unreadable = []
    missing = []
    coupled = []
    for rel in paths:
        try:
            text = (repo / rel).read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            # Tracked but absent from the worktree.  It still belongs to the
            # denominator, and it is not the same finding as a file that exists
            # and cannot be opened, so it is counted apart from `unreadable`.
            missing.append(rel)
            continue
        except OSError:
            # Tracked but unreadable: it still belongs to the denominator, and
            # leaving it out silently would report a cleaner tree than exists.
            unreadable.append(rel)
            continue
        row = roots[root_of(rel)]
        row["files"] += 1
        try:
            tree = ast.parse(text)
        except SyntaxError:
            row["unparsed"] += 1
            unparsed.append(rel)
            continue
        floor, why = file_floor(tree, text)
        for label in why:
            row["drivers"][label] += 1
        for version in set(why):
            row["above"][version] += 1
        if _ver(floor) > _ver(row["floor"]):
            row["floor"] = floor
        hits = COUPLING.findall(text)
        if hits:
            row["coupled"] += 1
            row["hits"] += len(hits)
            coupled.append((rel, len(hits)))
    return dict(roots), unparsed, unreadable, missing, coupled, in_scope, tracked


def classify(roots, declared, strict_os):
    """Every disagreement between a root's claim and its measurement."""
    findings = []
    inherited = root_default(declared)
    for name in sorted(roots):
        row = roots[name]
        claim = declared.get(name)
        scope = "own"
        if claim is None and inherited is not None:
            claim = inherited
            scope = "inherited"
        measured = row["floor"]
        if claim is None:
            findings.append({
                "root": name, "class": "undeclared", "measured": measured,
                "declared": None, "detail": "%d tracked file(s), floor %s, no "
                                           "requires-python published" % (row["files"], measured),
            })
        elif scope == "inherited" and _ver(claim[0]) <= _ver(measured):
            # A repo-wide floor the root does not contradict is not a finding.
            pass
        elif _ver(claim[0]) < _ver(measured):
            findings.append({
                "root": name, "class": "under_declared", "measured": measured,
                "declared": claim[0],
                "detail": "%s says %s but its source needs %s (%s)" % (
                    claim[1], claim[0], measured,
                    ", ".join(sorted(row["above"], key=_ver) or ["-"])),
            })
        elif _ver(claim[0]) > _ver(measured):
            findings.append({
                "root": name, "class": "over_declared", "measured": measured,
                "declared": claim[0],
                "detail": "%s%s says %s; the source needs only %s -- %d file(s) "
                          "already run below that" % (
                              "" if scope == "own" else "(inherited) ", claim[1],
                              claim[0], measured, row["files"]),
            })
        if row["unparsed"]:
            findings.append({
                "root": name, "class": "unparsed", "measured": measured,
                "declared": claim[0] if claim else None,
                "detail": "%d file(s) in this root do not parse" % row["unparsed"],
            })
        if strict_os and row["coupled"]:
            findings.append({
                "root": name, "class": "os_coupled", "measured": measured,
                "declared": claim[0] if claim else None,
                "detail": "%d of %d file(s) branch on the OS (%d hit(s))" % (
                    row["coupled"], row["files"], row["hits"]),
            })
    return findings


def report(roots, declared, findings, total_files, target, strict_flag=()):
    out = []
    inherited = root_default(declared)
    own = len([n for n in roots if n in declared])
    out.append("python_floor: %d root(s), %d tracked file(s), %d declaring a floor, "
               "%d inheriting the repo-root floor"
               % (len(roots), total_files, own, len(roots) - own))
    out.append("")
    out.append("%-34s %6s %7s %9s %8s  %s"
               % ("root", "files", "floor", "declared", "coupled", "verdict"))
    for name in sorted(roots, key=lambda n: -roots[n]["files"]):
        row = roots[name]
        claim = declared.get(name)
        shown = claim[0] if claim else ("(%s)" % inherited[0] if inherited else "-")
        classes = sorted({f["class"] for f in findings if f["root"] == name})
        verdict = ",".join(classes) if classes else "ok"
        out.append("%-34s %6d %7s %9s %8d  %s"
                   % (name, row["files"], row["floor"], shown, row["coupled"], verdict))

    by_class = defaultdict(list)
    for finding in findings:
        by_class[finding["class"]].append(finding)
    out.append("")
    for cls in ("under_declared", "over_declared", "undeclared", "unparsed", "os_coupled"):
        rows = by_class.get(cls, [])
        if not rows:
            continue
        out.append("%s (%d):" % (cls, len(rows)))
        for finding in rows[:40]:
            out.append("  %-32s %s" % (finding["root"], finding["detail"]))
        if len(rows) > 40:
            out.append("  ... %d more (see --json)" % (len(rows) - 40))
        out.append("")

    if target:
        reachable = [n for n in roots if _ver(roots[n]["floor"]) <= _ver(target)]
        blocked = [n for n in roots if _ver(roots[n]["floor"]) > _ver(target)]
        out.append("distance to a %s floor: %d of %d root(s) already meet it, "
                   "%d do not" % (target, len(reachable), len(roots), len(blocked)))
        for name in sorted(blocked, key=lambda n: -roots[n]["files"])[:15]:
            row = roots[name]
            top = sorted(row["drivers"].items(), key=lambda kv: -kv[1])[:3]
            out.append("  %-32s floor %-5s %s" % (
                name, row["floor"], ", ".join("%s x%d" % kv for kv in top)))
        out.append("")

    hard = [f for f in findings if f["class"] in HARD]
    soft = [f for f in findings if f["class"] not in HARD]
    strict = "--strict" in strict_flag
    failing = bool(hard) or (strict and bool(soft))
    note = "" if not strict else " (--strict: advisory findings fail too)"
    if not soft:
        note = ""
    out.append("verdict: %s -- %d hard finding(s), %d advisory%s, across %d measured "
               "root(s) (denominator: every root in the table above)"
               % ("FAIL" if failing else "PASS", len(hard), len(soft), note, len(roots)))
    return "\n".join(out)


def main(argv):
    repo = None
    for index, arg in enumerate(argv):
        if arg == "--repo" and index + 1 < len(argv):
            repo = argv[index + 1]
    if repo is None:
        here = __file__.replace("\\", "/").rsplit("/tools/", 1)[0]
        from pathlib import Path
        repo = Path(here)
    else:
        from pathlib import Path
        repo = Path(repo)

    target = None
    json_out = None
    only = None
    for index, arg in enumerate(argv):
        if arg == "--target" and index + 1 < len(argv):
            target = argv[index + 1]
        if arg == "--json" and index + 1 < len(argv):
            json_out = argv[index + 1]
        if arg == "--only" and index + 1 < len(argv):
            only = argv[index + 1]

    if not (repo / ".git").exists():
        print("python_floor: BLIND -- %s is not a git work tree" % repo)
        return 2

    (roots, unparsed, unreadable, missing, coupled, tracked,
     declared_source) = census(repo, only)
    total = len(tracked)
    if only:
        print("python_floor: scoped to %s" % only.strip("/"))
    # Declarations are read from the whole tracked tree even when the census is
    # scoped: the repo-root `pyproject.toml` governs every root that states no
    # floor of its own, and scoring only the scope reported 69 roots as
    # `undeclared` under `--only src` -- a finding created by the filter.
    declared = read_declared(repo, declared_source, unreadable, missing)
    findings = classify(roots, declared, "--strict-os" in argv)
    print(report(roots, declared, findings, total, target, argv))
    if missing:
        print("\nmissing from the worktree (tracked, not on disk), so their claim "
              "is UNKNOWN not absent: %d -- %s"
              % (len(missing), ", ".join(missing[:10])))
    if unreadable:
        print("\nunreadable, so their claim is UNKNOWN not absent: %d -- %s"
              % (len(unreadable), ", ".join(unreadable[:10])))

    if json_out:
        from pathlib import Path
        Path(json_out).write_text(json.dumps({
            "roots": {n: {"files": r["files"], "floor": r["floor"],
                          "coupled": r["coupled"], "hits": r["hits"],
                          "unparsed": r["unparsed"],
                          "drivers": dict(r["drivers"])}
                      for n, r in roots.items()},
            "declared": {n: list(v) for n, v in declared.items()},
            "findings": findings,
            "unparsed_files": unparsed,
            "missing_files": missing,
            "coupled_files": coupled[:200],
            "total_files": total,
        }, indent=1, sort_keys=True), encoding="utf-8")
        print("\nwrote %s" % json_out)

    hard = [f for f in findings if f["class"] in HARD]
    strict = "--strict" in argv
    if not hard and not strict:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
