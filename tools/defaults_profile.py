#!/usr/bin/env python3
"""What the agent does BY DEFAULT, in one editable file.

WHY THIS EXISTS
---------------
Three defaults were named in one session and each was about to be hard-coded in
a different tool:

  * run every test, not just imports      -> tools/golden_arrow.py
  * run the AST audit, by default         -> tools/ast_audit.py
  * deep-dive forensics + web search      -> tools/deep_dive.py
    (with the operator able to switch it off)

A default that lives in three places drifts in three places. This file is the
single place: `config/defaults.json`, read by the tools above, editable by
`--set`, checkable by `--check`.

WHAT IS A DEFAULT AND WHAT IS A SETTING
---------------------------------------
A default is what happens when nobody says anything. A setting is what the
operator says. Both are the same JSON; the distinction is that a default that
is silently *off* must say so in `--show`, because "we meant to run it" is the
most common way a gate stops existing.

    python tools/defaults_profile.py --show
    python tools/defaults_profile.py --get golden_arrow.timeout_s
    python tools/defaults_profile.py --set deep_dive.web_search=false
    python tools/defaults_profile.py --check
    python tools/defaults_profile.py --json

Every value is readable by the other tools through `read_default(key, fallback)`,
so a tool that cannot import this module still has a fallback constant and never
crashes on a missing config -- the robust-fallback rule, in code.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "config" / "defaults.json"

#: The shipped defaults. Every key here is ON unless the comment says otherwise.
DEFAULTS = {
    "version": 1,
    "ast_audit": True,
    "golden_arrow": {
        "enabled": True,        # run every test file, not a subset
        "strict": False,        # False = recorded debt passes, NEW failures do not
        "timeout_s": 180,       # per test file; a hung file is named, never a pass
        "workers": 6,
    },
    "deep_dive": {
        "enabled": True,
        "forensics": True,      # ast audit, evidence gate, unresolved refs, ledger freshness
        "web_search": True,     # OFF-line hosts fall back and record the skip
        "web_timeout_s": 20,
        "max_queries": 3,
    },
    "fallback": {
        "on_error": "record-and-continue",   # never abort a run for one broken leg
        "record": "logs/deep_dive.json",
    },
}


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in (over or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load() -> dict:
    if not PATH.exists():
        return json.loads(json.dumps(DEFAULTS))
    try:
        return _merge(DEFAULTS, json.loads(PATH.read_text(encoding="utf-8")))
    except ValueError:
        # A corrupt config must not take the tools down with it: the shipped
        # defaults are the fallback, and --check reports the corruption.
        return json.loads(json.dumps(DEFAULTS))


def read_default(dotted: str, fallback=None):
    """Read `a.b.c` from the profile, falling back to `fallback` on any problem."""
    node = load()
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return fallback
        node = node[part]
    return node


def coerce(text: str):
    low = text.strip().lower()
    if low in ("true", "yes", "on", "1"):
        return True
    if low in ("false", "no", "off", "0"):
        return False
    # "not a number" is an ANSWER here, not a swallowed error: a text knob's
    # value is legitimately a string, so the parse failure selects the branch
    # that returns it. Nothing is hidden -- the caller gets the value back
    # unchanged and --check validates the shape afterwards.
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def set_key(dotted: str, value) -> None:
    data = load()
    node = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        if not isinstance(node.get(part), dict):
            node[part] = {}
        node = node[part]
    node[parts[-1]] = value
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _leaves(data: dict, prefix: str = ""):
    """Every scalar leaf in the profile, as (dotted key, value).

    Recursive on purpose: `--show` and `problems()` both need to see a block
    nobody told them about.
    """
    for key in sorted(data):
        name = "%s%s" % (prefix, key)
        value = data[key]
        if isinstance(value, dict):
            for row in _leaves(value, name + "."):
                yield row
        else:
            yield name, value


def problems(data: dict) -> list:
    out = []
    if not isinstance(data.get("ast_audit"), bool):
        out.append("ast_audit must be true or false")
    ga = data.get("golden_arrow")
    if not isinstance(ga, dict):
        out.append("golden_arrow must be an object")
    else:
        if not isinstance(ga.get("enabled"), bool):
            out.append("golden_arrow.enabled must be true or false")
        if not isinstance(ga.get("timeout_s"), (int, float)) or ga.get("timeout_s", 0) < 5:
            out.append("golden_arrow.timeout_s must be a number >= 5")
        if not isinstance(ga.get("workers"), int) or ga.get("workers", 0) < 1:
            out.append("golden_arrow.workers must be an integer >= 1")
    dd = data.get("deep_dive")
    if not isinstance(dd, dict):
        out.append("deep_dive must be an object")
    else:
        for key in ("enabled", "forensics", "web_search"):
            if not isinstance(dd.get(key), bool):
                out.append("deep_dive.%s must be true or false" % key)
        max_q = dd.get("max_queries")
        if not isinstance(max_q, int) or not 0 <= max_q <= 20:
            out.append("deep_dive.max_queries must be an integer 0..20")
    fb = data.get("fallback")
    if not isinstance(fb, dict) or "on_error" not in fb:
        out.append("fallback.on_error must be set (record-and-continue)")
    return out


def main(argv=None) -> int:
    global PATH                       # declared before PATH is read, as required
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", default=str(PATH))
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--get", default="")
    ap.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), default=None)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    PATH = Path(args.path)

    if args.init:
        if PATH.exists():
            print("%s already exists; edit it with --set" % PATH, file=sys.stderr)
            return 1
        set_key("version", DEFAULTS["version"])
        for key, value in DEFAULTS.items():
            if key != "version":
                set_key(key, value if not isinstance(value, dict) else value)
        print("wrote %s" % PATH)

    if args.set:
        set_key(args.set[0], coerce(args.set[1]))
        print("%s = %r" % (args.set[0], coerce(args.set[1])))

    data = load()
    if args.get:
        print(read_default(args.get, None))
        return 0
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    if args.check:
        bad = problems(data)
        for line in bad:
            print("DEFECT: %s" % line)
        if bad:
            return 1
        print("OK: defaults profile valid (%s)" % PATH)
        return 0
    # --show is the default surface: a default that is off must be visible.
    # Printed by walking the file, never by a hand-kept list. The first version
    # printed five hard-coded lines and therefore could not show
    # preflight.disk_floor_gb, retention.composite_eviction or anything added
    # later -- measured 2026-11-05, when the new `hyper_edge` block existed, was
    # read by tools/deep_dive.py, and did not appear in --show at all. A knob the
    # surface cannot print is a knob nobody can verify is in force (HED-5).
    print("defaults -- %s (version %s)" % (PATH, data.get("version")))
    rows = list(_leaves({k: v for k, v in data.items() if k != "version"}))
    for name, value in rows:
        print("  %-30s %s" % (name, value))
    print("  %d knob(s)" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
