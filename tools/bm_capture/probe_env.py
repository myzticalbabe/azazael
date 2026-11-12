"""BM capture probe: console/gui entry points + install locations.

Emits {"entry_points": {dist: {"console": [...], "gui": [...]}},
"locations": {dist: path}}. Entry-points API differs across 3.8/3.10/3.12;
all three shapes are handled. Locations use locate_file with a spec
fallback; "" means unknown (tool then treats the dist as legacy).
Stdlib only.

Usage: python3 probe_env.py > env.json, then split, or:
  python3 probe_env.py entry_points > entry_points.json
  python3 probe_env.py locations > locations.json
"""

import importlib.metadata as m
import json
import sys


def entry_points_of(dist):
    try:
        eps = dist.entry_points
    except Exception:
        return [], []
    console, gui = [], []
    try:
        groups = eps.groups if hasattr(eps, "groups") else None
    except Exception:
        groups = None
    if groups:  # 3.10+ EntryPoints
        for ep in eps.select(group="console_scripts"):
            console.append(ep.name)
        for ep in eps.select(group="gui_scripts"):
            gui.append(ep.name)
    else:  # 3.8/3.9 iterable of EntryPoint
        for ep in eps:
            if getattr(ep, "group", "") == "console_scripts":
                console.append(ep.name)
            elif getattr(ep, "group", "") == "gui_scripts":
                gui.append(ep.name)
    return sorted(console), sorted(gui)


def location_of(dist, name, failures):
    for attempt in (
        lambda: str(dist.locate_file("")),
        lambda: str(dist._path.parent if hasattr(dist, "_path") else ""),
    ):
        try:
            v = attempt()
        except Exception as e:
            failures.append(f"{name}: location attempt failed ({e})")
            continue
        if v:
            return v
    try:
        import importlib.util as u

        top = (dist.read_text("top_level.txt") or "").split()
        for mod in top:
            spec = u.find_spec(mod.split("/")[0].split(".")[0])
            if spec and spec.origin:
                return spec.origin
    except Exception as e:
        failures.append(f"{name}: top_level fallback failed ({e})")
    return ""


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    eps, locs = {}, {}
    skipped = 0
    failures = []
    for d in m.distributions():
        try:
            name = (d.metadata["Name"] or "").strip()
        except Exception:
            skipped += 1
            continue
        if not name:
            skipped += 1
            continue
        c, g = entry_points_of(d)
        if c or g:
            eps[name] = {"console": c, "gui": g}
        locs[name] = location_of(d, name, failures)
    if skipped:
        print(f"probe_env: skipped {skipped} unreadable distribution(s)", file=sys.stderr)
    for f in failures:
        print(f"probe_env: {f}", file=sys.stderr)
    if which == "entry_points":
        print(json.dumps(eps, indent=1))
    elif which == "locations":
        print(json.dumps(locs, indent=1))
    else:
        print(json.dumps({"entry_points": eps, "locations": locs}, indent=1))


if __name__ == "__main__":
    main()
