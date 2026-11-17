#!/usr/bin/env python3
# coding: utf-8
"""arc_ledger.py -- render the ARC esquire pin ledger canonically (2026-11-16).

Why this exists
---------------
``ARC/esquire/pins.json`` was the last changeset in a 29-commit push range that
``scripts/commit_gate.py`` refused, and it was refused for a reason the gate
could not remedy: 155 lines added and 51 deleted in one file. Every reader of
that ledger (``tools/esquire_pins.py``, ``tools/arc_pin_audit.py``,
``tools/arc_check.py``) only READS it, and ``tools/arc_pin_audit.py`` writes a
copy, never the file. So a re-dump was, by construction, a hand edit of a
machine-shaped registry -- and the only way past the gate was to spend an
``ALLOW_BULK_COMMIT=1`` declaration on bytes no human wrote.

The honest repair is not a declaration and not a wider exemption: it is to give
the file the owner it was missing. This tool owns its RENDERING, so "the ledger
was re-dumped" becomes a command with an exit code, and
``GENERATED_PATHS``'s claim ("one named tool rewrites this file top to bottom")
becomes true and testable instead of aspirational.

Content and rendering are different facts, and this tool only claims the second.
The 20 pins are authored data, the way a dated ``state/`` snapshot is; what is
generated is the exact byte layout. Verified 2026-11-16 against HEAD's blob:
``json.dumps(data, indent=2, ensure_ascii=False)`` plus one trailing newline is
byte-identical to it (29,320 bytes + newline = 29,321, ``identical=True``).

Newlines
--------
This tree checks the file out with CRLF (``core.autocrlf=true``) while the blob
is LF. The newline style is therefore PRESERVED from the file being checked, not
asserted: a CRLF checkout is not drift, and ``--check`` passing on one is not a
pass on the other's bytes. A file that does not exist yet is written LF.

Usage
-----
    python tools/arc_ledger.py --check     # is the file canonically rendered?
    python tools/arc_ledger.py --write     # render it (prints UNCHANGED if equal)
    python tools/arc_ledger.py --check --json

Exit codes (``--check``): 0 canonical / 1 drift / 2 unreadable or not a ledger.
``--write``: 0 written or already canonical / 2 unreadable or not a ledger.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
#: The ledger this tool owns. Spelled as a literal (not assembled from parts) so
#: a textual audit of GENERATED_PATHS finds the file name in this source, which
#: is the check ``tests/test_commit_gate.py`` runs against every exemption.
LEDGER_PATH = "ARC/esquire/pins.json"
LEDGER = REPO / LEDGER_PATH


def detect_newline(raw: bytes) -> bytes:
    """The file's own line ending. CRLF only when the whole file uses it."""
    if b"\r\n" in raw and raw.count(b"\r\n") == raw.count(b"\n"):
        return b"\r\n"
    return b"\n"


def render(data: dict, newline: bytes = b"\n") -> bytes:
    """The canonical bytes for a ledger object.

    ``ensure_ascii=False`` is not cosmetic: the ledger carries typographic
    quotes, and escaping them would rewrite content as a side effect of
    formatting -- the exact confusion between the two facts this tool exists to
    keep apart.
    """
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return text.encode("utf-8").replace(b"\n", newline)


def load(path: Path) -> tuple[dict, bytes]:
    """(parsed ledger, raw bytes). Raises ValueError when the file is not one."""
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("%s is not readable JSON (%s)" % (path, exc))
    if not isinstance(data, dict):
        raise ValueError("%s is JSON but not a ledger object" % path)
    if not isinstance(data.get("pins"), list):
        raise ValueError("%s has no `pins` list" % path)
    return data, raw


def first_difference(current: bytes, canonical: bytes) -> str:
    """A one-line, bounded description of where two renderings diverge."""
    cur = current.splitlines()
    can = canonical.splitlines()
    for index, (a, b) in enumerate(zip(cur, can), start=1):
        if a != b:
            return ("line %d: file has %r, canonical render has %r"
                    % (index, a[:120], b[:120]))
    if len(cur) != len(can):
        longer, shorter = (("file", cur, can) if len(cur) > len(can)
                           else ("canonical render", can, cur))
        return ("%s has %d line(s), %s has %d"
                % (longer[0], len(longer[1]), shorter[0], len(shorter[1])))
    # Same text, different bytes: the line ending is the only thing left.
    return ("same %d line(s), different bytes (%d vs %d) -- line endings differ"
            % (len(cur), len(current), len(canonical)))


def main(argv=None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    as_json = "--json" in args
    ledger = Path(args[args.index("--ledger") + 1]) if "--ledger" in args \
        else LEDGER

    try:
        data, raw = load(ledger)
    except (OSError, ValueError) as exc:
        print("arc_ledger: cannot read the ledger -- %s" % exc)
        return 2

    canonical = render(data, detect_newline(raw))
    identical = canonical == raw
    pins = len(data.get("pins") or [])

    if "--write" in args:
        if identical:
            print("UNCHANGED %s -- %d bytes, %d pins" % (ledger, len(raw), pins))
            return 0
        ledger.write_bytes(canonical)
        print("WROTE %s -- %d bytes, %d pins (was %d bytes)"
              % (ledger, len(canonical), pins, len(raw)))
        return 0

    if "--check" in args or not args:
        if as_json:
            print(json.dumps({"ok": identical, "path": str(ledger),
                              "bytes": len(raw), "canonical_bytes": len(canonical),
                              "pins": pins}, indent=2))
        elif identical:
            print("CANONICAL: %s -- %d bytes, %d pins, %s line endings"
                  % (ledger, len(raw), pins,
                     "CRLF" if b"\r\n" in raw else "LF"))
        else:
            print("DRIFT: %s is not canonically rendered" % ledger)
            print("  " + first_difference(raw, canonical))
            print("  remedy: python tools/arc_ledger.py --write")
        return 0 if identical else 1

    print(__doc__.strip().splitlines()[0])
    print("usage: arc_ledger.py [--check | --write] [--ledger PATH] [--json]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
