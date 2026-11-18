#!/usr/bin/env python3
"""disclosure_audit.py -- section 3: name and locate credential material in the
untracked population, without ever printing a value.

`docs/GAP_ANALYSIS_2026-11-16.md` section 3 recorded credential-shaped files
sitting untracked in this worktree. Nobody disagreed with the finding and nothing
could re-check it, so the fact decayed into a sentence. This turns it into a
reading with a population and a denominator.

Scope is deliberate: the UNTRACKED population. A tracked secret has passed the
commit gates and is a different repair; an untracked one is one careless
`git add -A` away from landing, which is the risk section 3 named. The scope is
printed with the count, because a finding without its population is HED-9's lie.

Two detector families, and they answer different questions:

  name     the FILE is credential-shaped by its own name
  content  the file's BYTES contain a high-precision secret pattern

A matched VALUE is never printed, logged, or returned in --json. The datum is
"this file, this line, this detector" -- enough to act on, not enough to leak
into a transcript.

Exit: 0 when the audit ran (advisory -- a scanner red on day one is a scanner
switched off), 1 under --strict when anything is found, 2 when the population
could not be read. A run that read nothing is exit 2, never a clean pass.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- name detectors -------------------------------------------------------
# Each entry: (detector name, regex over the BASENAME, exclude-suffixes)
NAME_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("credentials-file", re.compile(
        r"(^|[._\-])(credentials?|secrets?|passwords?|passwd|apikey|api[._\-]?key)"
        r"s?([._\-]|$)", re.IGNORECASE)),
    ("env-file", re.compile(r"^\.env(\.[A-Za-z0-9]+)?$", re.IGNORECASE)),
    ("private-key", re.compile(
        r"(^id_(rsa|dsa|ecdsa|ed25519)$)|\.(pem|p12|pfx|key|jks|keystore)$",
        re.IGNORECASE)),
    ("token-file", re.compile(
        r"(^|[._\-])(token|auth|session)s?([._\-]|$)", re.IGNORECASE)),
]
# A file that is *about* secrets without being one. Reported, but labelled, so
# it is not confused with the real thing.
TEMPLATE_SUFFIXES = (".example", ".sample", ".template")

# --- content detectors ----------------------------------------------------
# High precision on purpose: a scanner that flags prose gets ignored. Every
# pattern here matches a shape that only real key material produces.
CONTENT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private-key-block", re.compile(
        r"-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws-access-key-id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("bearer-token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{24,}")),
    ("secret-assignment", re.compile(
        r"(?i)\b(password|passwd|secret|token|api[._\-]?key)\b\s*[:=]\s*"
        r"['\"][^'\"\s]{8,}['\"]")),
]

BINARY_SNIFF = 4096
DEFAULT_MAX_BYTES = 200_000


def _untracked() -> list[str]:
    """The population: untracked, not ignored. Raises when git cannot answer."""
    proc = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError("git ls-files rc=%d" % proc.returncode)
    return [p for p in (proc.stdout or "").split("\0") if p]


IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff")
TEMPLATE_STEMS = ("_template", "_example", "_sample", "-template", "-example",
                  "-sample")


def _is_template(basename: str) -> bool:
    low = basename.lower()
    if low.endswith(TEMPLATE_SUFFIXES) or ".example." in low:
        return True
    stem = low.split(".")[0]
    return stem.endswith(TEMPLATE_STEMS)


def _is_image(basename: str) -> bool:
    return basename.lower().endswith(IMAGE_SUFFIXES)


def _name_findings(rel: str) -> list[dict[str, object]]:
    base = Path(rel).name
    low = base.lower()
    # An env template is not a leak; it is the file that documents the leak.
    if low == ".env.example" or _is_template(base) and low.startswith(".env."):
        return []
    out: list[dict[str, object]] = []
    for name, pat in NAME_PATTERNS:
        if not pat.search(base):
            continue
        if _is_template(base):
            detail = "template (documents secrets, holds none)"
        elif _is_image(base):
            # A screenshot of a token page can carry the token itself. Kept and
            # labelled rather than filtered: visual disclosure is a real class.
            detail = "screenshot (visual disclosure risk -- open and check)"
        else:
            detail = "credential-shaped filename"
        out.append({"path": rel, "kind": "name", "detector": name,
                    "line": 0, "detail": detail})
        break
    return out


def _content_findings(rel: str, max_bytes: int) -> tuple[list[dict[str, object]], str]:
    """Content detections plus a skip reason when the file was not read."""
    path = ROOT / rel
    try:
        size = path.stat().st_size
    except OSError:
        return [], "unreadable"
    if size > max_bytes:
        return [], "skipped-large"
    try:
        blob = path.read_bytes()
    except OSError:
        return [], "unreadable"
    if b"\x00" in blob[:BINARY_SNIFF]:
        return [], "skipped-binary"
    text = blob.decode("utf-8", errors="replace")
    out: list[dict[str, object]] = []
    for name, pat in CONTENT_PATTERNS:
        for lineno, line in enumerate(text.splitlines(), 1):
            if not pat.search(line):
                continue
            # The matched text is intentionally discarded here. Only its
            # location survives.
            out.append({"path": rel, "kind": "content", "detector": name,
                        "line": lineno, "detail": "pattern matched"})
            break
    return out, "read"


def audit(max_bytes: int) -> tuple[list[dict[str, object]], dict[str, int]]:
    try:
        population = _untracked()
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print("disclosure_audit: cannot read the untracked population: %s" % exc)
        print("disclosure_audit: nothing audited, which is not a pass")
        raise SystemExit(2)

    findings: list[dict[str, object]] = []
    stats = {"listed": len(population), "scanned": 0,
             "skipped-large": 0, "skipped-binary": 0, "unreadable": 0}
    for rel in population:
        findings.extend(_name_findings(rel))
        rows, state = _content_findings(rel, max_bytes)
        findings.extend(rows)
        if state == "read":
            stats["scanned"] += 1
        elif state in stats:
            stats[state] += 1

    # One row per path, name findings first, content findings after.
    findings.sort(key=lambda r: (str(r["path"]), int(r["line"])))
    return findings, stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any credential-shaped file or value is found")
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                    help="per-file read cap (default %d)" % DEFAULT_MAX_BYTES)
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    ap.add_argument("--fail-on-template", action="store_true",
                    help="count template files as findings under --strict")
    ap.add_argument("--fail-on-images", action="store_true",
                    help="count screenshot files as findings under --strict")
    args = ap.parse_args(argv)

    findings, stats = audit(args.max_bytes)
    if args.json:
        print(json.dumps({"population": "untracked, not ignored",
                          "stats": stats, "findings": findings,
                          "values_printed": False}, indent=2))
    else:
        # Population and denominator FIRST, one row per hit after: the
        # hyper_edge leg quotes the first line, and `credentials-file name
        # add_passwords.py` as that line names one file while hiding that 540
        # were listed and 41 read. The count is part of the reading.
        print("disclosure_audit: population=untracked (not ignored) "
              "listed=%d scanned=%d skipped-large=%d skipped-binary=%d "
              "unreadable=%d"
              % (stats["listed"], stats["scanned"], stats["skipped-large"],
                 stats["skipped-binary"], stats["unreadable"]))
        print("disclosure_audit: %d finding(s); no matched value is printed"
              % len(findings))
        for r in findings:
            where = "%s:%s" % (r["path"], r["line"]) if r["line"] else str(r["path"])
            print("%-16s %-8s %-38s %s"
                  % (r["detector"], r["kind"], where, r["detail"]))

    if args.strict:
        def _counts(row: dict[str, object]) -> bool:
            detail = str(row["detail"])
            if "template" in detail:
                return args.fail_on_template
            if "screenshot" in detail:
                return args.fail_on_images
            return True

        strict_rows = [r for r in findings if _counts(r)]
        if strict_rows:
            print("disclosure_audit: STRICT FAIL -- %d finding(s)" % len(strict_rows))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
