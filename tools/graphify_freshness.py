#!/usr/bin/env python3
# coding: utf-8
"""graphify_freshness — prove the codegraph still describes HEAD, with evidence.

Why this exists (2026-11-16)
----------------------------
``mcp_startup_gate.py``'s ``codegraph-staleness`` leg fails when the store's
``built_at_commit`` is behind HEAD and ``git diff <built>..HEAD -- src`` is not
empty. That is the right question, and it had no reachable answer for a whole
class of commit:

* ``graphify update <path>`` compares topology first (watch.py:2081-2103) and,
  when nothing structural changed, returns **before** the write, printing
  ``No code-graph topology changes detected; outputs left untouched.``
* ``built_at_commit`` is written only by ``export.to_json`` (export.py:411),
  which that early return never reaches.
* ``--force`` does not change this: it only overrides the "fewer nodes" guard,
  and the run still returns at the same place.

Measured on this tree, 2026-11-16: graph built at ``4b072b40``, HEAD
``5445cae3``, the only ``src/`` change in the range was
``src/PSYCHE/data/female_needs_hyperedges.json`` (0 code files). Both
``update src`` and ``update src --force`` printed the no-change line, so the
gate stayed red with a remedy that cannot execute. Editing ``graph.json`` by
hand would clear it by asserting a build that did not happen -- the exact
falsification the gate exists to prevent.

The rule
--------
The gate will not take our word for it; it takes a **receipt** that only this
tool can mint, and only after running graphify:

    update exits 0
    AND its output carries "No code-graph topology changes detected"
    AND the store is byte-identical before and after (sha256)
    AND HEAD did not move while the update ran

Only then is ``src/graphify-out/freshness.json`` written, recording the HEAD,
the ``built_at_commit`` it justifies, and the store hash the verdict is about.

``mcp_startup_gate.py`` accepts it when, and only when, all of these agree:

    receipt["head"]             == HEAD
    receipt["built_at_commit"]  == the store's own built_at_commit
    receipt["graph_sha256"]     == sha256(graph.json) now
    (implicitly) the diff the receipt was minted for is the diff being judged

So a later commit, a rebuilt store, or a hand-edited receipt all fail closed,
and a receipt never stands in for a code change the graph does not contain:
if the update *does* change topology it writes the store, which advances
``built_at_commit`` and makes the receipt unnecessary.

Usage
-----
    python tools/graphify_freshness.py --stamp     # run the proof, write it
    python tools/graphify_freshness.py --check     # judge as the gate would
    python tools/graphify_freshness.py --json      # the same, machine-readable

Exit codes: 0 the store is fresh (or was just proved fresh), 1 stale, 2 the
proof could not be performed. ``2`` is not a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
STORE = REPO_ROOT / "src" / "graphify-out" / "graph.json"
RECEIPT = STORE.parent / "freshness.json"
WRAPPER = REPO_ROOT / "scripts" / "graphify_bin.sh"

# The line graphify prints when its own topology comparison found nothing to
# write (watch.py:2094-2103, three variants: regenerated html, removed html,
# outputs untouched). Any of them proves the extraction ran and agreed.
NO_CHANGE_MARKERS = (
    "No code-graph topology changes detected",
)

_RECEIPT_VERSION = 1


class ProofError(RuntimeError):
    """The proof could not be performed. Never a pass, never a staleness claim."""


#: A hung git must refuse the proof, never hang the gate that called it.
GIT_TIMEOUT_S = 120


def _git(*args: str) -> Tuple[int, str]:
    """Bounded git, so a wedged repository refuses instead of waiting forever.

    Every caller already treats a non-zero status as a refusal, so a timeout
    that raised through the callers as an empty result would be indistinguishable
    from a clean empty answer. It raises ProofError with the reason instead.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT)] + list(args),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=GIT_TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProofError("git %s could not run: %s" % (" ".join(args), exc)) from exc
    return proc.returncode, proc.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_built_commit(store: Path) -> str:
    """`built_at_commit` from the store's tail (the key is near the end)."""
    try:
        size = store.stat().st_size
        with open(store, "rb") as handle:
            handle.seek(max(0, size - 65536))
            tail = handle.read().decode("utf-8", "replace")
    except OSError as exc:
        raise ProofError("store unreadable: %s" % exc) from exc
    hits = re.findall(r'"built_at_commit"\s*:\s*"([0-9a-fA-F]{7,40})"', tail)
    if hits:
        return hits[-1].lower()
    try:
        with open(store, "r", encoding="utf-8", errors="replace") as handle:
            doc = json.load(handle)
    except (OSError, ValueError) as exc:
        raise ProofError("no built_at_commit in the tail and full parse failed (%s)" % exc) from exc
    sha = doc.get("built_at_commit") if isinstance(doc, dict) else None
    if not sha:
        raise ProofError("store records no built_at_commit")
    return str(sha).lower()


def changed_under_src(built: str, head: str) -> list:
    rc, out = _git("diff", "--name-only", "%s..%s" % (built, head), "--", "src")
    if rc != 0:
        raise ProofError("git diff %s..%s failed" % (built[:8], head[:8]))
    return [line for line in out.splitlines() if line.strip()]


def bash_exe() -> str:
    """A bash that can see Windows paths: Git Bash, never WSL's System32 shim.

    `subprocess.run(["bash", ...])` resolves through CreateProcess, which finds
    `C:\\WINDOWS\\system32\\bash.exe` (WSL) before Git on this box. Measured
    2026-11-16: exit 127, `/bin/bash: C:/Azazael/...: No such file or
    directory` -- the WSL shim cannot read a `C:/` path at all. Shell `which`
    finds Git's bash, which is why the same command worked by hand and failed
    from here.
    """
    candidates = [shutil.which("bash"),
                  r"C:\Program Files\Git\bin\bash.exe",
                  r"C:\Program Files\Git\usr\bin\bash.exe"]
    for cand in candidates:
        if not cand or not Path(cand).exists():
            continue
        if "system32" in str(cand).lower():
            continue
        return str(cand)
    raise ProofError("no Git Bash found (only the System32/WSL shim is on PATH)")


def run_update(timeout: int = 600) -> Tuple[int, str]:
    """Run the documented build command and return (rc, combined output)."""
    if not WRAPPER.exists():
        raise ProofError("build wrapper missing: %s" % WRAPPER)
    # Git Bash eats the backslashes in a Windows path (`C:\Azazael\...` arrives
    # as `C:Azazael...` and exits 127), so the wrapper is passed POSIX-style.
    wrapper = str(WRAPPER).replace("\\", "/")
    try:
        proc = subprocess.run(
            [bash_exe(), wrapper, "update", "src"],
            cwd=str(REPO_ROOT), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProofError("update could not run: %s" % exc) from exc
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def receipt_verdict(store: Path, head: str, built: str) -> Tuple[bool, str]:
    """(fresh, why) -- the same judgement the startup gate makes.

    Fails closed on every mismatch, and names which one it was: a receipt that
    cannot be read is not a pass, and "no receipt" is reported as the absence
    it is rather than being mistaken for a stale graph.
    """
    path = Path(store).parent / "freshness.json"
    if not path.exists():
        return False, "no freshness receipt at %s" % path
    try:
        doc: Any = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError) as exc:
        return False, "receipt unreadable (%s)" % exc
    if not isinstance(doc, dict):
        return False, "receipt is not a JSON object"
    r_head = str(doc.get("head") or "").lower()
    r_built = str(doc.get("built_at_commit") or "").lower()
    r_sha = str(doc.get("graph_sha256") or "").lower()
    if r_head != head.lower():
        return False, "receipt proves %s, HEAD is %s" % (r_head[:8] or "?", head[:8])
    if r_built != built.lower():
        return False, "receipt describes build %s, store records %s" % (
            r_built[:8] or "?", built[:8])
    if not r_sha:
        return False, "receipt records no store hash"
    try:
        actual = sha256_file(store)
    except OSError as exc:
        return False, "store unreadable (%s)" % exc
    if actual != r_sha:
        return False, "store changed since the receipt (sha %s.. != %s..)" % (
            actual[:12], r_sha[:12])
    evidence = str(doc.get("evidence") or "").strip()
    return True, evidence or "re-extraction at %s found no topology change" % head[:8]


def stamp(store: Path, run: bool = True, timeout: int = 600) -> Dict[str, Any]:
    """Perform the proof and write the receipt. Raises ProofError to refuse."""
    if not store.exists():
        raise ProofError("graph store missing: %s" % store)
    rc, head = _git("rev-parse", "HEAD")
    if rc != 0 or not head:
        raise ProofError("git rev-parse HEAD failed in %s" % REPO_ROOT)
    built_before = read_built_commit(store)
    if head.startswith(built_before) or built_before.startswith(head):
        return {"stamped": False, "reason": "store already built at HEAD %s" % head[:8],
                "head": head, "built_at_commit": built_before}
    changed = changed_under_src(built_before, head)
    if not changed:
        return {"stamped": False,
                "reason": "no src/ change since the build; the gate already passes",
                "head": head, "built_at_commit": built_before}

    sha_before = sha256_file(store)
    if not run:
        raise ProofError("refusing to stamp without running the extraction (run=True)")

    rc, output = run_update(timeout=timeout)
    if rc != 0:
        raise ProofError("graphify update exited %d; last line: %s" % (
            rc, (output.strip().splitlines() or ["<no output>"])[-1]))
    marker = next((m for m in NO_CHANGE_MARKERS if m in output), None)
    if marker is None:
        raise ProofError(
            "update did not report a no-topology-change result, so there is "
            "nothing to stamp; if it rewrote the store, built_at_commit has "
            "advanced and the gate reads it directly")

    sha_after = sha256_file(store)
    if sha_after != sha_before:
        raise ProofError("update changed the store (%s.. -> %s..); the store's "
                         "own built_at_commit is the authority" % (
                             sha_before[:12], sha_after[:12]))

    built_after = read_built_commit(store)
    if built_after != built_before:
        raise ProofError("built_at_commit moved during the run (%s -> %s); "
                         "nothing to stamp" % (built_before[:8], built_after[:8]))

    rc, head_after = _git("rev-parse", "HEAD")
    if rc != 0 or head_after != head:
        raise ProofError("HEAD moved while the proof ran (%s -> %s); re-run" % (
            head[:8], head_after[:8] or "?"))

    # The diff the receipt is minted for must be the diff it describes.
    still = changed_under_src(built_after, head_after)
    if still != changed:
        raise ProofError("the src/ diff changed while the proof ran; re-run")

    doc = {
        "version": _RECEIPT_VERSION,
        "head": head,
        "built_at_commit": built_after,
        "graph_sha256": sha_after,
        "graph_bytes": store.stat().st_size,
        "changed_src": changed,
        "evidence": marker,
        "method": "scripts/graphify_bin.sh update src",
        "stamped_at": datetime.now(timezone.utc).isoformat(),
    }
    target = Path(store).parent / "freshness.json"
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)
    doc["stamped"] = True
    doc["receipt"] = str(target)
    return doc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--stamp", action="store_true",
                       help="run the extraction, prove no topology change, write the receipt")
    group.add_argument("--check", action="store_true",
                       help="judge the store exactly as the startup gate does")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--timeout", type=int, default=600,
                        help="seconds allowed for the extraction (default 600)")
    args = parser.parse_args(argv)

    try:
        if args.stamp:
            result = stamp(STORE, run=True, timeout=args.timeout)
            if args.json:
                print(json.dumps(result, indent=2))
            elif result.get("stamped"):
                print("stamped %s" % result["receipt"])
                print("  head            %s" % result["head"][:8])
                print("  built_at_commit %s (unchanged)" % result["built_at_commit"][:8])
                print("  evidence        %s" % result["evidence"])
                print("  changed_src     %d file(s): %s" % (
                    len(result["changed_src"]), ", ".join(result["changed_src"])))
            else:
                print("not stamped: %s" % result["reason"])
            return 0

        # --check and the bare invocation both judge; judging never writes.
        built = read_built_commit(STORE)
        rc, head = _git("rev-parse", "HEAD")
        if rc != 0 or not head:
            raise ProofError("git rev-parse HEAD failed")
        fresh, why = receipt_verdict(STORE, head, built)
        changed = changed_under_src(built, head)
        if head.startswith(built) or built.startswith(head) or not changed:
            verdict, detail = "fresh", "store describes HEAD (or src/ unchanged)"
        elif fresh:
            verdict, detail = "fresh", "receipt: %s" % why
        else:
            verdict, detail = "stale", why
        if args.json:
            print(json.dumps({"verdict": verdict, "detail": detail, "head": head,
                              "built_at_commit": built, "changed_src": changed},
                             indent=2))
        else:
            print("%s: %s" % (verdict.upper(), detail))
            if verdict == "stale":
                print("  remedy: python tools/graphify_freshness.py --stamp")
        return 0 if verdict == "fresh" else 1
    except ProofError as exc:
        print("BLIND: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
