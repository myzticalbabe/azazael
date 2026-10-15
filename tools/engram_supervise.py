#!/usr/bin/env python
# coding: utf-8
"""Engram live supervisor gate (run at each turn boundary).

Engram's own live supervision is a per-prompt hook (UserPromptSubmit nudge,
PreToolUse gating) plus a nudge appended to MCP tool responses. This client
exposes no hook surface, so supervision is delivered here as an explicit gate
that consults engram's own supervisory outputs and prints a verdict:

  doctor     -> store invariants; blocked/errors is a NO-GO
  conflicts  -> unjudged contradiction pairs: pending -> CLARIFY (advisory);
                an ORPHANED relation -> NO-GO
  hook       -> the nudge / required first action engram would have pushed
  plan       -> open plan + mandate items still owed

Usage: python tools/engram_supervise.py [project]
Exit 0 = GO, or CLARIFY (unjudged conflict pairs are outstanding - advisory,
         not a block), or supervisor unavailable (fail-open to avoid deadlock).
Exit 1 = NO-GO (doctor blocked/errors, or an orphaned relation whose endpoint
         observation is missing - a structurally broken relation).

Why CLARIFY and not NO-GO for unjudged pairs: the store creates candidates by
itself (every `mem_save` spawns pairs for comparison), so hard-blocking on them
refuses the next tool call until they are judged - and judging is one of the
calls being refused, so the block can only be cleared by doing the thing it
forbids. NO-GO stays reserved for breakage, and the outstanding count is still
printed in full.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = os.environ.get("ENGRAM_PROJECT", "azazael")
ENGRAM_BIN = os.environ.get("ENGRAM_BIN") or shutil.which("engram") or str(
    Path.home() / "go" / "bin" / "engram.exe"
)


def run(args, stdin_data=None):
    """Run engram, returning stdout. Never raises."""
    try:
        r = subprocess.run(
            [ENGRAM_BIN] + args, input=stdin_data,
            timeout=60, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(HERE.parent))
        return r.stdout or ""
    except Exception as e:
        return f"__ERR__ {e}"


def strip_banner(text):
    """Drop engram's update-available banner and blank filler."""
    out = []
    skip = 0
    for line in text.splitlines():
        if line.startswith("Update available:"):
            skip = 3
            continue
        if skip:
            skip -= 1
            continue
        out.append(line)
    return "\n".join(out).strip()


def check_doctor():
    text = strip_banner(run(["doctor"]))
    if text.startswith("__ERR__"):
        return "unknown", ["doctor unreachable: " + text]
    head = text.splitlines()[0] if text else ""
    blocked = errors = 0
    for line in text.splitlines():
        if line.startswith("Checks:"):
            for part in line.replace("Checks:", "").split():
                if "=" in part:
                    k, v = part.split("=", 1)
                    if k in ("blocked", "errors"):
                        try:
                            n = int(v)
                        except ValueError:
                            n = 0
                        if k == "blocked":
                            blocked = n
                        else:
                            errors = n
    detail = []
    for line in text.splitlines():
        if line.startswith("[") and not line.startswith("[ok]"):
            detail.append(line[:160])
    if blocked or errors:
        return "NO-GO", [f"doctor: {head}"] + detail
    return "GO", [f"doctor: {head}"]


def _judgment_status_counts(text):
    """Counts from the `By judgment_status:` section ONLY.

    The same payload carries a `By relation type:` section whose keys
    (related / compatible / supersedes / scoped) hold unrelated numbers. A
    parser that accepts any `key: digit` line from the whole document can let a
    relation count masquerade as a judgment count, so this walks section by
    section: a new `By ...` header switches the block and `Deferred`/`Dead` end
    it. Blank lines do NOT end a block - the real payload indents its entries
    directly under the header with no separator.
    """
    counts = {}
    in_block = False
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("by "):
            in_block = low.startswith("by judgment_status")
            continue
        if low.startswith("deferred") or low.startswith("dead"):
            in_block = False
            continue
        if not in_block or ":" not in s:
            continue
        k, v = s.split(":", 1)
        v = v.strip()
        if v.isdigit():
            counts[k.strip().lower()] = int(v)
    return counts


def verdict_from_conflicts_stats(text):
    """Pure verdict for one `conflicts stats` payload -> (verdict, lines).

    verdict is "GO" | "CLARIFY" | "NO-GO" | "unknown". Split out from the
    subprocess call so the parsing is pinned against text transcribed from a
    real run rather than against whatever the parser happens to expect.
    """
    # An unrecognized response (bad flag, usage dump, schema change) must NOT
    # be silently read as healthy - that is the fail-open trap.
    if "Conflicts Stats" not in text and "No relations found" not in text:
        first = (text.splitlines() or ["<empty>"])[0][:120]
        return "unknown", ["conflicts: unrecognized output, treated as unknown: " + first]
    if "No relations found" in text:
        return "GO", ["conflicts: 0 unresolved"]
    stats = _judgment_status_counts(text)
    pending = stats.get("pending", 0)
    orphaned = stats.get("orphaned", 0)
    judged = (stats.get("accepted", 0) + stats.get("rejected", 0)
              + stats.get("judged", 0))
    if orphaned:
        return "NO-GO", [
            f"conflicts: {orphaned} orphaned relation(s) - endpoint observation is missing",
            f"  (pending={pending}, judged={judged})",
        ]
    if pending:
        # CLARIFY, not NO-GO: these pairs are created by the store itself, so a
        # hard block here refuses every later tool call until they are judged -
        # and judging is one of the calls being refused. The count is printed.
        return "CLARIFY", [
            f"conflicts: {pending} unjudged pair(s) outstanding "
            f"(judgment_status=pending) - judge them; not blocking",
            f"  (judged={judged}, orphaned={orphaned})",
        ]
    return "GO", [f"conflicts: 0 unresolved (judged={judged})"]


def check_conflicts():
    """Fetch engram's REAL `conflicts stats` and hand it to the pure parser.

    There is NO `Total:` line in `stats` - `conflicts list` prints Total,
    `stats` does not (cmd/engram/conflicts.go:146 vs :259-291). Gating on a
    fabricated `total` key fails open: it reports GO on a store full of
    unresolved contradictions. Verified against the Go source.
    """
    text = strip_banner(run(["conflicts", "stats", "--project", PROJECT]))
    if text.startswith("__ERR__"):
        return "unknown", ["conflicts unreachable: " + text]
    return verdict_from_conflicts_stats(text)


def check_hook():
    payload = json.dumps({"session_id": "supervisor", "cwd": str(HERE.parent)})
    text = run(["hook", "codex-user-prompt-submit"], stdin_data=payload)
    msg = ""
    parse_error = ""
    try:
        msg = (json.loads(text.strip().splitlines()[-1]) or {}).get("systemMessage", "")
    except Exception as exc:
        # A hook whose output cannot be READ is not a hook with nothing to
        # say. Collapsing the two would report a broken supervisor as "none
        # due" - the failure shown as a clean verdict.
        parse_error = "%s: %s" % (type(exc).__name__, exc)
    if parse_error:
        return ["nudge: UNREADABLE (" + parse_error[:160] + ")"]
    if not msg:
        return ["nudge: none due"]
    first = msg.splitlines()[0][:200]
    return ["nudge: " + first]


def check_plan():
    text = strip_banner(run(["context", PROJECT]))
    items = []
    for line in text.splitlines():
        if "[topic:plan/" in line:
            title = line.split("**")[1] if line.count("**") >= 2 else line[:60]
            items.append("  - " + title)
    return ["open plan items: " + str(len(items))] + items


def main() -> int:
    if not (Path(ENGRAM_BIN).exists() or shutil.which(ENGRAM_BIN)):
        print("engram_supervise: engram binary not found; fail-open (exit 0)")
        return 0

    verdicts = []
    print("=== ENGRAM SUPERVISOR (" + PROJECT + ") ===")
    for fn in (check_doctor, check_conflicts):
        verdict, lines = fn()
        verdicts.append(verdict)
        for l in lines:
            print("  " + l)
    for l in check_hook():
        print("  " + l)
    for l in check_plan():
        print(l)

    nogos = [v for v in verdicts if v == "NO-GO"]
    if nogos:
        print("VERDICT: NO-GO - resolve the items above before proceeding")
        return 1
    clarifies = [v for v in verdicts if v == "CLARIFY"]
    if clarifies:
        print("VERDICT: CLARIFY - unjudged conflict pair(s) outstanding; judge "
              "them when convenient. Advisory, not a block (exit 0).")
        return 0
    print("VERDICT: GO - proceed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
