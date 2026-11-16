"""BM capture probe: in-environment reverse dependencies.

For every installed dist, lists which other installed dists declare a
requirement on it (Requires-Dist, names normalized). Emits
{dist: [requirers]} as JSON. Stdlib only, Python 3.8+.

Usage: python3 probe_revdeps.py > revdeps.json
"""

import importlib.metadata as m
import json
import re
import sys


def norm(s):
    return re.sub(r"[-_.]+", "-", s).lower()


def req_name(req):
    return norm(req.split(";")[0].split("[")[0].split()[0].strip())


def main():
    dists = {}
    skipped = 0
    for d in m.distributions():
        try:
            name = (d.metadata["Name"] or "").strip()
        except Exception:
            skipped += 1
            continue
        if name:
            dists[norm(name)] = d
    if skipped:
        print(f"probe_revdeps: skipped {skipped} unreadable distribution(s)", file=sys.stderr)
    rev = {n: [] for n in dists}
    for n, d in dists.items():
        try:
            reqs = d.requires or []
        except Exception:
            reqs = []
        for r in reqs:
            target = req_name(r)
            if target in rev and n != target:
                rev[target].append(n)
    for v in rev.values():
        v.sort()
    print(json.dumps(rev, indent=1))


if __name__ == "__main__":
    main()
