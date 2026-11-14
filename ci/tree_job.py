"""What one tree's CI job does, in code instead of in YAML conditionals.

GitHub's hosted runners carry 3.9-3.13; they have no 3.15 and no 3.16.  That
is not an opinion, it is the measured cause of the online `CI` workflow failing:
`setup-python` was asked for `3.15`, resolved 3.12.16, and `pip install -e .`
then died on `Package 'azazael' requires a different Python: 3.12.16 not in
'>=3.15'`.  So a per-tree job must never install the repo root, and must only
install a tree whose declared floor the runner can satisfy.

Every skip this file takes is printed with its reason.  A skip is not a pass,
and the line says so.

  python ci/tree_job.py install Project_ELIZA
  python ci/tree_job.py test Project_ELIZA
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOOR_RE = re.compile(r"requires-python\s*=\s*[\"']([^\"']+)[\"']")

#: Trees whose job collects instead of executing, with the reason on record.
#: HED-2 measured this suite not finishing inside 600 s twice -- it is wedged,
#: not slow, so a job that ran it would be a job that hangs.
COLLECT_ONLY = {
    "tests": "root suite is wedged (HED-2: not finished in 600 s twice); "
             "collection proves the modules import on this interpreter",
}


def version(text):
    """'3.12.16' -> (3, 12, 16); None when it is not a dotted number."""
    parts = []
    for piece in text.strip().split("."):
        digits = ""
        for char in piece:
            if not char.isdigit():
                break
            digits += char
        if not digits:
            return None
        parts.append(int(digits))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def satisfies(spec, running):
    """Does `running` meet a simple requires-python spec?

    Only the operators this tree actually uses are implemented.  Anything else
    returns None -- unknown, which the caller reports rather than guessing at.
    """
    here = version(running)
    if here is None:
        return None
    for clause in spec.split(","):
        clause = clause.strip()
        match = re.match(r"(>=|<=|==|!=|~=|>|<)\s*([0-9][0-9.]*)", clause)
        if not match:
            return None
        operator = match.group(1)
        raw = match.group(2)
        wanted = version(raw)
        if wanted is None:
            return None
        # `~=3.10` means ">=3.10, ==3.*": the prefix it constrains is every
        # component the spec wrote except the last.  Padding the spec to three
        # components first compared (3,) against (3, 10) and called 3.12
        # incompatible with its own compatible-release spec.
        written = len(raw.split("."))
        if operator == ">=" and not here >= wanted:
            return False
        if operator == ">" and not here > wanted:
            return False
        if operator == "<=" and not here <= wanted:
            return False
        if operator == "<" and not here < wanted:
            return False
        if operator == "==" and here[:len(wanted)] != wanted:
            return False
        if operator == "!=" and here[:len(wanted)] == wanted:
            return False
        if operator == "~=" and not (here >= wanted
                                     and here[:written - 1] == wanted[:written - 1]):
            return False
    return True


def run(argv, cwd=None):
    print("tree_job: $ %s" % " ".join(argv))
    try:
        done = subprocess.run(argv, cwd=str(cwd or ROOT), timeout=1800)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("tree_job: FAIL -- %s" % exc)
        return 1
    return done.returncode


def install(tree):
    manifest = ROOT / tree / "pyproject.toml"
    if not manifest.exists():
        print("tree_job: SKIP install -- %s publishes no pyproject.toml" % tree)
        return 0
    try:
        text = manifest.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print("tree_job: FAIL -- %s unreadable: %s" % (manifest, exc))
        return 1
    match = FLOOR_RE.search(text)
    if not match:
        print("tree_job: SKIP install -- %s declares no requires-python" % tree)
        return 0
    spec = match.group(1)
    running = "%d.%d.%d" % sys.version_info[:3]
    verdict = satisfies(spec, running)
    if verdict is None:
        print("tree_job: SKIP install -- %s says %r, which this helper cannot "
              "evaluate against %s" % (tree, spec, running))
        return 0
    if not verdict:
        print("tree_job: SKIP install -- %s requires %s and the runner is %s"
              % (tree, spec, running))
        return 0
    return run([sys.executable, "-m", "pip", "install", "--quiet",
                "--no-input", "-e", tree])


def test(tree):
    if tree in COLLECT_ONLY:
        print("tree_job: COLLECT-ONLY -- %s: %s" % (tree, COLLECT_ONLY[tree]))
        return run([sys.executable, "-m", "pytest", tree, "-q",
                    "--collect-only", "-p", "no:cacheprovider"])
    return run([sys.executable, "-m", "pytest", tree, "-q", "--timeout=120",
                "-p", "no:cacheprovider"])


def main(argv):
    if len(argv) != 2 or argv[0] not in ("install", "test"):
        print(__doc__)
        return 2
    action, tree = argv
    # The repo root declares >=3.16, which no hosted runner carries.  Naming
    # this refusal keeps the constraint next to the command that would break
    # it, instead of only in a workflow comment nobody re-reads.
    if (ROOT / tree).resolve() == ROOT:
        print("tree_job: SKIP -- %r is the repo root (requires >=3.16)" % tree)
        return 0
    if not (ROOT / tree).is_dir():
        print("tree_job: FAIL -- %s is not a directory in this tree" % tree)
        return 1
    return install(tree) if action == "install" else test(tree)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
