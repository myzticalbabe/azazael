#!/usr/bin/env python3
"""
krampus_mcp.py -- MCP server wrapper for PROJECT KRAMPUS composition verifier.

Exposes krampus doctor and members commands as MCP tools.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

# Add krampus to path
KRAMPUS_ROOT = os.environ.get("KRAMPUS_ROOT", "C:/Azazael/krampus")
sys.path.insert(0, KRAMPUS_ROOT)

# EveUnleashed owns the `eve_unleashed` top-level package (KRAMPUS manifest:
# package eve-unleashed>=3.16.0, repo myzticalbabe/EveUnleashed). This venv also
# installs azazael (editable), whose src/ carries a legacy 1.1.0 copy of the
# same top-level name; its .pth sorts first, so the shadow wins and
# eve_unleashed.mcml / eve_unleashed.trainer resolve MISSING. Prefer the real
# checkout so the composition check verifies the real members, not the shadow.
# Diagnosis: sys.path order + tracked-file counts, measured 2026-11-21.
_EVE_SRC = os.environ.get("EVEUNLEASHED_SRC", "C:/Azazael/EveUnleashed/src")
if os.path.isdir(_EVE_SRC):
    if _EVE_SRC in sys.path:
        sys.path.remove(_EVE_SRC)
    sys.path.insert(0, _EVE_SRC)

from krampus.cli import load_manifest, check_member, doctor as krampus_doctor_cli

mcp = FastMCP("krampus")


@mcp.tool()
def krampus_doctor(as_json: bool = False) -> dict[str, Any]:
    """
    Run krampus composition verification.

    Checks every manifest member and reports READY / MISSING / SKIP per member.
    Exit code 0 iff no required member is MISSING.

    Args:
        as_json: Return machine-readable JSON instead of formatted text

    Returns:
        Dict with results and exit code
    """
    results, code = krampus_doctor_cli()
    if as_json:
        return {"results": results, "exit_code": code}
    # Format as text
    lines = []
    for r in results:
        extra = f" ({r['version']})" if r["version"] else ""
        lines.append(f"{r['name']:<14} {r['state']:<7} {r['detail']}{extra}")
    return {"results": results, "exit_code": code, "text": "\n".join(lines)}


@mcp.tool()
def krampus_members() -> dict[str, Any]:
    """
    List all KRAMPUS manifest members.

    Returns:
        Dict with member list
    """
    manifest = load_manifest()
    members = []
    for m in manifest["members"]:
        members.append({
            "name": m["name"],
            "kind": m["kind"],
            "role": m["role"],
            "required": m.get("required", False)
        })
    return {"members": members}


@mcp.tool()
def krampus_check_member(name: str) -> dict[str, Any]:
    """
    Check a single KRAMPUS manifest member by name.

    Args:
        name: Member name to check

    Returns:
        Member check result
    """
    manifest = load_manifest()
    by_name = {m["name"]: m for m in manifest["members"]}
    if name not in by_name:
        return {"error": f"Member '{name}' not found in manifest"}
    result = check_member(by_name[name])
    return result


@mcp.tool()
def krampus_status() -> dict[str, Any]:
    """
    Get overall KRAMPUS status summary.

    Returns:
        Status summary with counts
    """
    result = krampus_doctor(as_json=True)
    results = result["results"]
    code = result["exit_code"]
    counts = {"READY": 0, "MISSING": 0, "SKIP": 0}
    required_missing = []
    for r in results:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
        if r["state"] == "MISSING":
            manifest = load_manifest()
            by_name = {m["name"]: m for m in manifest["members"]}
            if by_name[r["name"]].get("required"):
                required_missing.append(r["name"])

    return {
        "project": "KRAMPUS",
        "version": "0.2.1",
        "exit_code": code,
        "counts": counts,
        "required_missing": required_missing,
        "healthy": code == 0
    }


if __name__ == "__main__":
    mcp.run()