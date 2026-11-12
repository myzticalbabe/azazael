#!/usr/bin/env python3
"""KRAMPUS as an MCP surface: every selector picker and API connection.

WHY THIS EXISTS
---------------
Measured 2026-11-12: PROJECT KRAMPUS (myzticalbabe/krampus 0.2.2) declares
eight members -- madi, eve, mellifluousml, lillith, gamora, berzerker,
cradle, jaeger -- and `krampus doctor` resolved all eight READY on this box.
Nine selectors exist in gamora's parser (lilith, eve, cradle, lucy, swarm,
inject, berzerker + doctor), and `src/CORE/inference/providers.py` registers
31 API connections. **None of them was reachable from any lane config**: the
three lane files (kilo, opencode, freebuff) configure seven MCP servers each
and not one exposed a KRAMPUS member, selector or provider.

A composition nothing can call is a composition nobody uses. This server is
the one front door that makes the whole surface callable from every lane,
which is what "one front door per capability" in the manifest's own doctrine
asks for.

TOOLS
-----
    krampus_members          the manifest, as rows
    krampus_doctor           READY / MISSING / SKIP per member (+ exit code rule)
    krampus_selectors        every selector picker this server exposes
    krampus_select           the picker: route any selector by name
    gamora_<selector>        one tool per selector (lilith, eve, cradle,
                             lucy, swarm, inject, berzerker)
    providers_list           all 31 API connections with key status
    provider_best            the picker: which API connection is live now

Stdlib only. Every call is a bounded subprocess, so a wedged selector is a
named timeout, never a hung server. A selector that cannot run returns its
stderr in the result: a report, never a traceback.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SERVER_NAME = "krampus"
SERVER_VERSION = "0.3.0"
PROTOCOL_VERSION = "2024-11-05"

TOOLS_DIR = Path(__file__).resolve().parent
REPO = TOOLS_DIR.parent                      # C:/Azazael/azazael
HOST = REPO.parent                           # C:/Azazael
PYTHON = Path("C:/Azazael/.venvs/py316t/Scripts/python.exe")
GAMORA = REPO / "Project_GAMORA" / "gamora.py"
PROVIDERS = REPO / "src" / "CORE" / "inference" / "providers.py"

# The selectors gamora's argparse defines. Kept as data because a tool list
# must be answerable without importing gamora (that import costs ~350 ms and
# a tools/list has a deadline); `--selftest` cross-checks this list against
# the parser so the two cannot drift silently.
SELECTORS = ("lilith", "eve", "cradle", "lucy", "swarm", "inject", "berzerker")

#: Bare-metal passthrough selections. WSL2 (Ubuntu and Kali alike) runs on the
#: Microsoft virtual kernel, so /dev/kmsg, /dev/dri and eBPF are the VIRTUAL set.
#: `BarePassthroughWorm` (src/CORE/WORMS/expansion/envmesh.py) probes the three
#: real paths in order; these are its selections, exposed here so a lane can ask
#: "am I on bare metal, and if not, which path gets me there" without importing
#: the worm registry itself.
METAL_SELECTIONS = ("local", "ssh", "vsock", "all")
METAL_WORM = "CORE.WORMS.expansion.envmesh:BarePassthroughWorm"

TIMEOUT_SELECTOR = 120
TIMEOUT_PROVIDERS = 90
TIMEOUT_METAL = 90


def _python() -> str:
    return str(PYTHON) if PYTHON.exists() else sys.executable


def _run(cmd, timeout):
    """(ok, text) for a bounded subprocess; never raises."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, cwd=str(REPO),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except subprocess.TimeoutExpired:
        return False, "timeout after %ss: %s" % (timeout, " ".join(map(str, cmd)))
    except OSError as exc:
        return False, "could not start: %s" % exc
    text = (proc.stdout or "").strip()
    if proc.returncode != 0:
        err = (proc.stderr or "").strip() or text
        return False, "exit %d: %s" % (proc.returncode, err[:2000])
    return True, text


def krampus_members() -> str:
    """The composition manifest, one row per member."""
    code = ("import json,os;from krampus import load_manifest;"
            "d=load_manifest();"
            "print(json.dumps([{k:m.get(k) for k in "
            "('name','kind','role','package','repo','required')} "
            "for m in d['members']]))")
    ok, text = _run([_python(), "-c", code], 60)
    if not ok:
        return "krampus not importable: " + text
    try:
        rows = json.loads(text.splitlines()[-1])
    except (ValueError, IndexError):
        return text
    return "\n".join("%-14s %-7s %-6s %s" % (
        r["name"], r["kind"], "req" if r.get("required") else "opt",
        r["role"]) for r in rows)


def krampus_doctor() -> str:
    """READY / MISSING / SKIP for every member, with the exit rule applied."""
    env = dict(os.environ)
    env.setdefault("AZAZAEL_ROOT", str(REPO))
    try:
        proc = subprocess.run(
            [_python(), "-c",
             "import sys;from krampus import main;sys.exit(main(['doctor']))"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120, cwd=str(REPO), env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.TimeoutExpired) as exc:
        return "doctor could not run: %s" % exc
    body = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return "%s\ndoctor exit=%d (0 = no required member MISSING)" % (
        body, proc.returncode)


def gamora_selector(selector: str, extra: str = "") -> str:
    """Run one gamora selector. Returns stdout, or the named failure."""
    if selector not in SELECTORS:
        return "unknown selector %r; known: %s" % (
            selector, ", ".join(SELECTORS))
    if not GAMORA.exists():
        return "gamora missing: %s" % GAMORA
    cmd = [_python(), str(GAMORA), selector]
    if extra.strip():
        cmd.extend(extra.split())
    ok, text = _run(cmd, TIMEOUT_SELECTOR)
    return text or ("%s: no output (ok=%s)" % (selector, ok))


def providers_list() -> str:
    """Every API connection the platform registers, with key status."""
    code = ("import json,sys;sys.path.insert(0,%r);"
            "from CORE.inference.providers import list_providers;"
            "print(json.dumps(list_providers()))" % str(REPO / "src"))
    ok, text = _run([_python(), "-c", code], TIMEOUT_PROVIDERS)
    if not ok:
        return "providers unavailable: " + text
    try:
        rows = json.loads(text.splitlines()[-1])
    except (ValueError, IndexError):
        return text
    keyed = [r for r in rows if r.get("has_api_key")]
    body = "\n".join("%-22s %-6s %2d models  %s" % (
        r["id"], "key" if r.get("has_api_key") else "-",
        r.get("models") or 0, r.get("name", "")) for r in rows)
    return "%d API connections (%d with a key), %d models total\n%s" % (
        len(rows), len(keyed), sum(r.get("models") or 0 for r in rows), body)


def provider_best() -> str:
    """The picker: which API connection answers right now."""
    code = ("import sys;sys.path.insert(0,%r);"
            "from CORE.inference.providers import get_best_provider;"
            "p=get_best_provider();print(type(p).__name__, getattr(p,'name',"
            "''), getattr(p,'base_url',''))" % str(REPO / "src"))
    ok, text = _run([_python(), "-c", code], TIMEOUT_PROVIDERS)
    return text if ok else "no live provider: " + text


def krampus_selectors() -> str:
    """Every selector picker this server exposes."""
    lines = ["%s -> gamora_%s" % (s, s) for s in SELECTORS]
    lines += ["%s -> %s" % (s, "krampus_" + s)
              for s in ("members", "doctor", "select", "selectors",
                        "providers_list", "provider_best")]
    lines += ["metal:%s -> metal_probe" % s for s in METAL_SELECTIONS]
    return "\n".join(lines)


def krampus_select(selector: str, extra: str = "") -> str:
    """The picker: route any selector by name (gamora, metal or krampus scope)."""
    sel = (selector or "").strip()
    if sel in ("members", "doctor", "selectors", "providers_list",
               "provider_best", "metal_list"):
        return globals()["krampus_" + sel]()
    if sel in METAL_SELECTIONS:
        return metal_probe(sel)
    if sel in ("", "metal"):
        return metal_list()
    return gamora_selector(sel, extra)


def metal_list() -> str:
    """The bare-metal passthrough selections and what each one proves."""
    rows = (("local", "this process's own kernel",
             "always runs; Windows/WSL answer with their virtual kernel"),
            ("ssh", "a non-microsoft kernel over SSH",
             "needs AZAZAEL_BARE_SSH=user@bare-host"),
            ("vsock", "a host service reachable at 127.0.0.1:8420",
             "h5/vsock bridge or TCP fallback; closed is a named failure"),
            ("all", "the first path that actually reaches bare metal",
             "probes local -> ssh -> vsock in that order"))
    body = "\n".join("%-6s %-38s %s" % r for r in rows)
    return ("bare-metal passthrough selections (%d): local, ssh, vsock, all\n%s\n"
            "pick one with metal_probe, or krampus_select(\"metal\"/\"ssh\"...)"
            % (len(METAL_SELECTIONS), body))


def metal_probe(selection: str = "all") -> str:
    """Run one BarePassthroughWorm selection and report its own dict.

    The worm lives behind the same bounded subprocess as every other tool, so a
    slow SSH handshake is a named timeout rather than a wedged server, and the
    server process never imports the worm registry.
    """
    sel = (selection or "all").strip().lower()
    if sel not in METAL_SELECTIONS:
        return "unknown metal selection %r; known: %s" % (
            selection, ", ".join(METAL_SELECTIONS))
    mod, _, cls = METAL_WORM.partition(":")
    method = {"all": "probe"}.get(sel, "probe_" + sel)
    code = ("import json,sys;sys.path.insert(0,%r);"
            "from %s import %s;w=%s();print(json.dumps(w.%s()))"
            % (str(REPO / "src"), mod, cls, cls, method))
    ok, text = _run([_python(), "-c", code], TIMEOUT_METAL)
    if not ok:
        return "metal %s could not run: %s" % (sel, text)
    try:
        payload = json.loads(text.splitlines()[-1])
    except (ValueError, IndexError):
        return text
    return "metal %s (%s)\n%s" % (sel, method, json.dumps(payload, indent=2))


def _tool(name, description, props=None, required=None):
    schema = {"type": "object", "properties": props or {},
              "additionalProperties": False}
    if required:
        schema["required"] = required
    return {"name": name, "description": description, "inputSchema": schema}


_SELECT_PROPS = {
    "selector": {"type": "string",
                 "description": "one of: " + ", ".join(SELECTORS)},
    "extra": {"type": "string",
              "description": "extra args passed to the selector, space separated"},
}


def tool_list():
    tools = [
        _tool("krampus_members", "List the KRAMPUS composition members."),
        _tool("krampus_doctor",
              "Resolve every KRAMPUS member: READY / MISSING / SKIP."),
        _tool("krampus_selectors", "List every selector picker available."),
        _tool("krampus_select",
              "Picker: route any KRAMPUS or gamora selector by name.",
              _SELECT_PROPS, ["selector"]),
        _tool("providers_list",
              "List all API connections with model counts and key status."),
        _tool("provider_best",
              "Picker: name the API connection that is live right now."),
        _tool("krampus_metal_list",
              "Bare-metal passthrough selections: local, ssh, vsock, all."),
        _tool("krampus_metal_probe",
              "Picker: run one bare-metal passthrough selection and report it.",
              {"selection": {"type": "string",
                             "description": "one of: "
                                            + ", ".join(METAL_SELECTIONS)}},
              ["selection"]),
    ]
    for sel in SELECTORS:
        tools.append(_tool("gamora_" + sel,
                           "Run the gamora %r selector." % sel,
                           {"extra": {"type": "string",
                                      "description": "extra arguments"}}))
    return tools


def call_tool(name, args):
    args = args or {}
    if name == "krampus_members":
        return krampus_members()
    if name == "krampus_doctor":
        return krampus_doctor()
    if name == "krampus_selectors":
        return krampus_selectors()
    if name == "krampus_select":
        return krampus_select(str(args.get("selector", "")),
                              str(args.get("extra", "")))
    if name == "providers_list":
        return providers_list()
    if name == "provider_best":
        return provider_best()
    if name == "krampus_metal_list":
        return metal_list()
    if name == "krampus_metal_probe":
        return metal_probe(str(args.get("selection", "all")))
    if name.startswith("gamora_"):
        return gamora_selector(name[len("gamora_"):],
                               str(args.get("extra", "")))
    raise ValueError("unknown tool: %s" % name)


def _respond(msg_id, result=None, error=None):
    frame = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        frame["error"] = {"code": -32000, "message": str(error)[:1000]}
    else:
        frame["result"] = result
    sys.stdout.write(json.dumps(frame) + "\n")
    sys.stdout.flush()


def serve(stdin=None, stdout=None):
    """Newline-delimited JSON-RPC over stdio, per the MCP stdio transport."""
    src = stdin or sys.stdin
    for line in src:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError as exc:
            # A malformed frame is dropped, but never silently: the client sees a
            # stderr line rather than a server that appears to ignore requests.
            sys.stderr.write("krampus_mcp: unparsable frame (%s): %r\n"
                             % (exc, line[:120]))
            sys.stderr.flush()
            continue
        method = msg.get("method")
        msg_id = msg.get("id")
        if method == "initialize":
            _respond(msg_id, {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME,
                               "version": SERVER_VERSION},
            })
        elif method == "tools/list":
            _respond(msg_id, {"tools": tool_list()})
        elif method == "tools/call":
            params = msg.get("params") or {}
            try:
                text = call_tool(params.get("name"),
                                 params.get("arguments") or {})
                _respond(msg_id, {"content": [{"type": "text", "text": text}],
                                  "isError": False})
            except Exception as exc:      # a tool error is a result, not a crash
                _respond(msg_id, {"content": [{"type": "text",
                                               "text": "tool failed: %s" % exc}],
                                  "isError": True})
        elif method == "notifications/initialized":
            continue
        elif method == "ping":
            _respond(msg_id, {})
        elif msg_id is not None:
            _respond(msg_id, error="method not found: %s" % method)
    return 0


def selftest() -> int:
    """Offline contract check: tool names, selector coverage, picker routing."""
    names = {t["name"] for t in tool_list()}
    problems = []
    for sel in SELECTORS:
        if "gamora_" + sel not in names:
            problems.append("selector %r has no tool" % sel)
    for required in ("krampus_members", "krampus_doctor", "krampus_selectors",
                     "krampus_select", "providers_list", "provider_best",
                     "krampus_metal_list", "krampus_metal_probe"):
        if required not in names:
            problems.append("missing tool %r" % required)
    for sel in METAL_SELECTIONS:
        if "metal:%s" % sel not in krampus_selectors():
            problems.append("metal selection %r is not listed" % sel)
    if "unknown metal selection" not in metal_probe("not-a-path"):
        problems.append("unknown metal selection is not refused by name")
    routed = krampus_select("selectors")
    if "gamora_eve" not in routed:
        problems.append("picker does not list gamora selectors")
    if "unknown selector" not in gamora_selector("not-a-selector"):
        problems.append("unknown selector is not refused by name")
    print("krampus_mcp selftest: %d tools, %d selectors, %d problem(s)"
          % (len(names), len(SELECTORS), len(problems)))
    for p in problems:
        print("  FAIL " + p)
    return 1 if problems else 0


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in args:
        return selftest()
    if "--list" in args:
        for tool in tool_list():
            print("%-20s %s" % (tool["name"], tool["description"]))
        return 0
    return serve()


if __name__ == "__main__":
    sys.exit(main())
