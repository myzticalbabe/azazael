"""BM capture probe: pip freeze equivalent without needing pip.

Lists installed distributions as name==version lines (pip freeze format).
Stdlib only, Python 3.8+. Usage: python3 probe_pip.py > pip_14t.txt
(On BM the file must be named pip_14t.txt: the classifier reads it.)
"""

import importlib.metadata as m

import sys

seen = set()
rows = []
skipped = 0
for d in m.distributions():
    try:
        name = (d.metadata["Name"] or "").strip()
        ver = (d.version or "").strip()
    except Exception:
        skipped += 1
        continue
    if not name or name in seen:
        continue
    seen.add(name)
    rows.append(f"{name}=={ver}" if ver else name)

for r in sorted(rows, key=str.lower):
    print(r)
if skipped:
    print(f"probe_pip: skipped {skipped} unreadable distribution(s)", file=sys.stderr)
