#!/usr/bin/env python3
"""Does every lane config actually reach the KRAMPUS surface?

WHY THIS EXISTS
---------------
Measured 2026-11-12: KRAMPUS declares 8 members, gamora 7 selector pickers and
`src/CORE/inference/providers.py` 31 API connections -- and **zero** of them was
reachable from kilo, opencode or freebuff. The three lane files each configured
seven MCP servers and none was KRAMPUS. A composition nothing can call is a
composition nobody uses, and no gate was asking the question.

`tools/krampus_mcp.py` is the front door. This tool proves the door is in every
lane, enabled, and answering with the tools the surface needs. It asks the
question of the *configured command*, not of the file's shape: an entry whose
command does not exist, or that answers `tools/list` with the wrong tool set, is
a FAIL even though the config reads fine (HED-1: verify by running).

USAGE
-----
    python tools/krampus_conformance.py            # table + verdict
    python tools/krampus_conformance.py --json     # same, machine-readable
    python tools/krampus_conformance.py --no-probe # config-only, no spawn
    python tools/krampus_conformance.py --strict   # exit 1 on any gap

EXIT
----
    0  every lane reaches the whole surface
    1  a gap (missing / disabled / unspawnable / incomplete tool set)
    2  the surface itself could not be enumerated -- nothing audited, and
       nothing audited is not a pass (HED-11)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

TOOLS_DIR = Path(__file__).resolve().parent
REPO = TOOLS_DIR.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

SERVER_NAME = "krampus"
SERVER_SCRIPT = TOOLS_DIR / "krampus_mcp.py"

#: One lane row per config the gate knows about. `mcp_eight_verify` owns the
#: path table (and prefers the gate's constants), so read it from there rather
#: than re-deriving a second copy that can drift.
from mcp_eight_verify import LANES, command_of, read_jsonc, servers  # noqa: E402

OK, MISSING, DISABLED, BROKEN, PARTIAL = "OK", "MISSING", "DISABLED", "BROKEN", "PARTIAL"


def _surface() -> Tuple[List[dict], List[str], List[str]]:
    """(members, selectors, providers) read from the live producers."""
    sys.path.insert(0, str(REPO / "src"))
    from CORE.inference.providers import list_providers       # noqa: E402

    import krampus_mcp                                         # noqa: E402

    from krampus import load_manifest                          # noqa: E402

    members = list(load_manifest().get("members") or [])
    selectors = list(krampus_mcp.SELECTORS)
    providers = [row.get("id") for row in list_providers() if row.get("id")]
    return members, selectors, providers


def required_tools(selectors: Sequence[str]) -> List[str]:
    """The tool names a lane must see for the surface to be fully callable."""
    return (["krampus_members", "krampus_doctor", "krampus_select",
             "krampus_selectors", "providers_list", "provider_best"]
            + ["gamora_" + s for s in selectors])


def _entry_for(block: Dict[str, dict]) -> Tuple[Optional[str], Optional[dict]]:
    for name, entry in block.items():
        cmd = " ".join(command_of(entry))
        if name == SERVER_NAME or "krampus_mcp" in cmd:
            return name, entry
    return None, None


def _disabled(entry: dict) -> bool:
    if entry.get("disabled") is True or entry.get("enabled") is False:
        return True
    if entry.get("enabled") is not None and entry.get("enabled") is not True:
        return False
    return False


def check_lane(path: Path, wanted: Sequence[str], probe: bool) -> dict:
    doc, why = read_jsonc(path)
    if doc is None:
        return {"config": str(path), "state": MISSING,
                "detail": "config unreadable: %s" % why, "tools": []}
    block = servers(doc)
    name, entry = _entry_for(block)
    if entry is None:
        return {"config": str(path), "state": MISSING,
                "detail": "%d server(s), no %s entry" % (len(block), SERVER_NAME),
                "tools": []}
    if _disabled(entry):
        return {"config": str(path), "state": DISABLED,
                "detail": "%s configured but disabled" % name, "tools": []}
    cmd = command_of(entry)
    if not cmd:
        return {"config": str(path), "state": BROKEN,
                "detail": "%s has no command" % name, "tools": []}
    if not probe:
        return {"config": str(path), "state": OK,
                "detail": "%s configured (not probed)" % name, "tools": []}

    from mcp_eight_verify import probe_stdio                      # noqa: E402

    result = probe_stdio(cmd, cwd=str(REPO))
    if not result.ok:
        return {"config": str(path), "state": BROKEN,
                "detail": "%s: %s" % (name, result.detail),
                "stderr": (result.stderr or "")[-400:], "tools": []}
    tools = sorted(list(getattr(result, "tool_names", []) or []))
    if not tools:
        # A count with no names cannot answer "is the surface covered", so the
        # probe's own count is reported as the denominator it is.
        tools = []
    got = [t for t in wanted if t in tools]
    if tools and len(got) == len(wanted):
        state, detail = OK, "%s: %d/%d required tools" % (name, len(got), len(wanted))
    elif tools:
        state = PARTIAL
        detail = "%s: %d/%d required tools; missing %s" % (
            name, len(got), len(wanted), ", ".join(t for t in wanted if t not in tools))
    else:
        state = PARTIAL
        detail = "%s answered %s" % (name, result.detail)
    return {"config": str(path), "state": state, "detail": detail, "tools": tools}


def render(rows: Sequence[dict], members: Sequence[dict], selectors: Sequence[str],
           providers: Sequence[str]) -> None:
    print("KRAMPUS surface: %d members, %d selector pickers, %d API connections"
          % (len(members), len(selectors), len(providers)))
    print("  members:   %s" % ", ".join(str(m.get("name")) for m in members))
    print("  selectors: %s" % ", ".join(selectors))
    print()
    width = max(len(r["lane"]) for r in rows) if rows else 4
    for row in rows:
        print("%-*s  %-9s %s" % (width, row["lane"], row["state"], row["detail"]))
    print()


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine-readable verdict")
    ap.add_argument("--no-probe", action="store_true", help="config-only, spawn nothing")
    ap.add_argument("--strict", action="store_true", help="unused; exit is already strict")
    args = ap.parse_args(argv)

    try:
        members, selectors, providers = _surface()
    except Exception as exc:                      # enumeration is the audit's floor
        print("BLIND: surface could not be enumerated: %s: %s"
              % (type(exc).__name__, exc))
        return 2
    if not members or not selectors or not providers:
        print("BLIND: surface enumerated empty (members=%d selectors=%d providers=%d)"
              % (len(members), len(selectors), len(providers)))
        return 2

    wanted = required_tools(selectors)
    rows = []
    for lane, path in LANES.items():
        if not path.exists():
            continue
        row = check_lane(path, wanted, probe=not args.no_probe)
        row["lane"] = lane
        rows.append(row)

    gaps = [r for r in rows if r["state"] != OK]
    verdict = "PASS" if rows and not gaps else ("FAIL" if rows else "BLIND")

    if args.json:
        print(json.dumps({"verdict": verdict, "surface": {
            "members": [m.get("name") for m in members],
            "selectors": selectors, "providers": len(providers),
            "required_tools": wanted}, "lanes": rows}, indent=2))
    else:
        render(rows, members, selectors, providers)
        print("verdict: %s  (%d lane(s), %d gap(s))" % (verdict, len(rows), len(gaps)))
        for row in rows:
            print("  proof %-10s %s -> %s" % (row["lane"], row["config"], row["state"]))

    if not rows:
        return 2
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
