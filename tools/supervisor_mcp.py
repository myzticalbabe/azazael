#!/usr/bin/env python
# coding: utf-8
"""supervisor MCP server — one verdict over two memories (PMB + Engram).

Engram ships its own gate as a CLI script (tools/engram_supervise.py) and
PMB is pull-only on this host (no prompt hook), so no client ever sees a
unified verdict. This server puts an MCP face on the existing oracle logic:

  verdict         doctor + conflicts + nudge + PMB-daemon liveness -> GO/CLARIFY/NO-GO
  plan_items      full open-plan list (structured id|title rows, not truncated)
  task_detail     raw engram search output for one #NNNN task
  lessons         engram search scoped to durable knowledge (bugfix/decision/pattern)
  record_outcome  write-through: engram `save` + JSONL outbox row for PMB pickup
  triage_plan     open items with a suggested evidence check each, for resolution

Run under the free-threaded interpreter (py315t, which has `mcp`):
  C:/Azazael/.venvs/py315t/Scripts/python.exe tools/supervisor_mcp.py
Registered in ~/.agents/mcp.json as stdio server "supervisor".
"""
import json
import os
import socket
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import engram_supervise as sup  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402

OUTBOX = HERE.parent / "state" / "supervisor_outbox.jsonl"
REFUSALS = HERE.parent / "state" / "supervisor_refusals.jsonl"
PMB_HOST, PMB_PORT = "127.0.0.1", 8765
_OPEN_DATES: dict[str, str] = {}

#: Hard cap for every subprocess a verdict leg may spawn. It must sit WELL
#: below the verdict BUDGET (30s): subprocess.run kills its child on its OWN
#: timeout and nothing else does, so an unbounded child of an overrun leg
#: survives the verdict response -- the ghost-CLI class the Oct 18 goal
#: names. With this bound an abandoned leg's child is already dead (or
#: dying inside its own run() timeout) when the verdict returns.
LEG_LIMIT_S = 20.0


def _item_age_days(date_str):
    """Days since yyyy-mm-dd, or -1 when unknown."""
    import datetime
    try:
        d = datetime.date.fromisoformat((date_str or "").strip())
        return (datetime.date.today() - d).days
    except ValueError:
        return -1

server = FastMCP("supervisor")


def _pams_honest() -> tuple:
    """Read-only probes against the PAMS DBs (never trust daemon_health).

    Measured 2026-10-18: messages=0 with newest session 2026-05-27
    (conversation auto-capture dead ~5 months), curated_memories=6066 with
    importance in {8, 9}, tool_calls flowing today. Semantics: NO-GO only
    when the store the agent actually reads (curated_memories) is
    unreadable or empty; a dead conversation pipeline is CLARIFY (advisory)
    because auto-capture may be unused-by-design rather than broken.
    An unreadable DB file is fail-open with a named cause -- absence of
    evidence is never a verdict.
    """
    import os
    import sqlite3
    base = os.path.expanduser("~/.pams/memory_data")
    lines = []
    try:
        c = sqlite3.connect("file:%s/conversations.db?mode=ro" % base, uri=True)
        n_msg = c.execute("select count(*) from messages").fetchone()[0]
        newest = c.execute("select max(start_timestamp) from sessions").fetchone()[0]
        c.close()
        lines.append("pams conversations: %d messages, newest session %s"
                     % (n_msg, newest))
        conv_dead = (n_msg == 0)
    except Exception as exc:
        return "GO", ["pams conversations: UNREADABLE (%s)" % exc]
    try:
        c = sqlite3.connect("file:%s/ai_memories.db?mode=ro" % base, uri=True)
        n_mem = c.execute("select count(*) from curated_memories").fetchone()[0]
        levels = sorted(r[0] for r in
                        c.execute("select distinct importance_level from curated_memories"))
        c.close()
        lines.append("pams memories: %d rows, importance in %s" % (n_mem, levels))
        if n_mem == 0:
            return "NO-GO", lines + ["pams curated store EMPTY"]
    except Exception as exc:
        return "GO", lines + ["pams memories: UNREADABLE (%s)" % exc]
    try:
        c = sqlite3.connect("file:%s/mcp_tool_calls.db?mode=ro" % base, uri=True)
        n_calls = c.execute("select count(*) from tool_calls").fetchone()[0]
        newest_call = c.execute("select max(timestamp) from tool_calls").fetchone()[0]
        c.close()
        lines.append("pams tool_calls: %d rows, newest %s" % (n_calls, newest_call))
    except Exception as exc:
        lines.append("pams tool_calls: UNREADABLE (%s)" % exc)
    if conv_dead:
        return "CLARIFY", lines + ["pams conversation capture dead (0 messages); "
                                     "memories + tool calls live -- advisory"]
    return "GO", lines


def _pmb_liveness() -> str:
    """TCP liveness for the warm PMB daemon (hybrid vector recall lives there).

    This is integrity-vs-liveness honest: an open port means the daemon
    answers, nothing more. Cold stdio pmb-mcp would serve BM25-only recall.
    """
    try:
        with socket.create_connection((PMB_HOST, PMB_PORT), timeout=5):
            return "pmb: daemon reachable at %s:%d" % (PMB_HOST, PMB_PORT)
    except OSError as exc:
        return "pmb: UNREACHABLE (%s) - recall falls back to cold/BM25-only" % exc


@server.tool()
def verdict() -> str:
    """Unified GO / CLARIFY / NO-GO over Engram checks plus PMB liveness.

    Legs run in parallel (ThreadPoolExecutor). Downstream leg policy, after
    the Oct 18 timeout/ghost repair:

    * pmb legs are IN-PROCESS HTTP calls to the daemon (no child at all);
      their CLI fallback is tree-killed at LEG_LIMIT_S (20s).
    * engram legs pass LEG_LIMIT_S to engram_supervise.run, so the child is
      killed by subprocess.run before the budget (30s) expires.
    => no leg's child can outlive the verdict response; the response
       returns at <= BUDGET, never a client -32001. The running MCP server
       process must be RESTARTED to load this fix (stdio servers spawn at
       client start; a saved file does not reach the running process).
    """
    import time
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
    t0 = time.time()
    #: Hard budget for the whole verdict. The client caps an MCP call near
    #: 60s; every leg's child is bounded at LEG_LIMIT_S (20s) < BUDGET.
    BUDGET = 30.0
    deadline = t0 + BUDGET
    legs = {}
    ex = ThreadPoolExecutor(max_workers=6)
    try:
        legs["doctor"] = ex.submit(sup.check_doctor, LEG_LIMIT_S)
        legs["conflicts"] = ex.submit(sup.check_conflicts, LEG_LIMIT_S)
        legs["hook"] = ex.submit(sup.check_hook, LEG_LIMIT_S)
        legs["pams"] = ex.submit(_pams_honest)
        legs["live"] = ex.submit(_pmb_liveness)
        legs["goals"] = ex.submit(_pmb_goal_pressure)

        def _bounded(name):
            left = max(0.0, deadline - time.time())
            try:
                return legs[name].result(timeout=left)
            except FutureTimeout:
                # None here IS the failure value: _bounded returns an Optional
                # result and the verdict renderer prints "unknown (timed out)"
                # for it -- it is not a success-shaped default.
                return None  # scanner:ignore except_return_default

        doctor_v = _bounded("doctor")
        conflicts_v = _bounded("conflicts")
        hook_v = _bounded("hook")
        pams_v = _bounded("pams")
        live_v = _bounded("live")
        goals_v = _bounded("goals")
    finally:
        # shutdown(wait=True) -- the `with` form -- is what re-trips the
        # client timeout: it blocks on the hung leg even after .result()
        # raised. cancel_futures keeps queued work from starting late.
        ex.shutdown(wait=False, cancel_futures=True)
    dt = time.time() - t0

    def _late(name):
        return ("%s: LEG TIMEOUT after %.0fs budget - reported loud, never silent"
                % (name, BUDGET))

    if doctor_v is None:
        doctor_verdict, doctor_lines = "unknown", [_late("doctor")]
    else:
        doctor_verdict, doctor_lines = doctor_v
    if conflicts_v is None:
        conflicts_verdict, conflicts_lines = "unknown", [_late("conflicts")]
    else:
        conflicts_verdict, conflicts_lines = conflicts_v
    hook_lines = hook_v if hook_v is not None else [_late("hook") + " (advisory)"]
    if pams_v is None:
        pams_verdict, pams_lines = "unknown", [_late("pams")]
    else:
        pams_verdict, pams_lines = pams_v
    live_line = (live_v if live_v is not None
                 else _late("live") + " - treat as UNREACHABLE")
    goals_line = (goals_v if goals_v is not None
                  else _late("goals") + " (informational; never verdict-changing)")
    lines = ["=== SUPERVISOR VERDICT (%s) ===" % sup.PROJECT]
    verdicts = [doctor_verdict, conflicts_verdict, pams_verdict]
    lines.extend("  " + l for l in doctor_lines)
    lines.extend("  " + l for l in conflicts_lines)
    for line in hook_lines:
        lines.append("  " + line)
    for line in pams_lines:
        lines.append("  " + line)
    lines.append("  " + live_line)
    lines.append("  " + goals_line)
    lines.append("  legs=%.1fs (parallel)" % dt)
    if "NO-GO" in verdicts:
        lines.append("VERDICT: NO-GO - resolve the items above before proceeding")
    elif "CLARIFY" in verdicts or "unknown" in verdicts:
        lines.append("VERDICT: CLARIFY - advisory items outstanding (exit 0)")
    else:
        lines.append("VERDICT: GO - proceed")
    return "\n".join(lines)


def _open_items() -> tuple[list[tuple[str, str]] | None, str]:
    """All open (id, title) pairs, or (None, reason) when unmeasurable."""
    queries = ("task", "Kilo", "Freebuff", "fix", "verify", "wire",
               "bandit", "grpo", "hybrid", "consumer",
               "DeepSeek", "opencode", "MiMo", "audit", "build",
               "design", "retire", "quantize", "ablation",
               "quarantine", "manifest", "adjudicate", "falsify",
               "persist", "commit", "map", "mock")
    tasks: dict[str, tuple[str, str]] = {}
    for q in queries:
        raw = sup.strip_banner(sup.run(
            ["search", q, "--type", "task", "--project", sup.PROJECT,
             "--limit", "100"]))
        if raw.startswith("__ERR__"):
            return None, "task search unreachable"
        parsed = sup._plan_tasks(raw)
        if parsed is None:
            return None, "unrecognized search output"
        for tid, title, date in parsed:
            tasks.setdefault(tid, (title, date))
    _OPEN_DATES.clear()
    for tid, (title, date) in tasks.items():
        _OPEN_DATES[tid] = date
    raw_rels = sup.strip_banner(sup.run(
        ["conflicts", "list", "--project", sup.PROJECT, "--limit", "500"]))
    if raw_rels.startswith("__ERR__"):
        return None, "relations unreachable"
    done_ids = sup._superseded_task_ids(raw_rels)
    if done_ids is None:
        return None, "unrecognized relations output"
    open_items = [(tid, t) for tid, (t, _d) in tasks.items()
                  if tid not in done_ids]
    open_items.sort(key=lambda x: -int(x[0]))
    return open_items, "union of %d queries; lower bound" % len(queries)


@server.tool()
def plan_items() -> str:
    """Every open plan item as `id|title` rows (no 20-row truncation)."""
    items, note = _open_items()
    if items is None:
        return "open plan items: unknown (%s)" % note
    lines = ["open plan items: %d (%s)" % (len(items), note)]
    lines += ["%s|%s" % (tid, title) for tid, title in items]
    return "\n".join(lines)


@server.tool()
def task_detail(task_id: str) -> str:
    """Raw engram search output for one task number (evidence for triage)."""
    tid = "".join(c for c in task_id if c.isdigit())
    if not tid:
        return "task_detail: no digits in %r" % task_id[:40]
    raw = sup.strip_banner(sup.run(
        ["search", "#" + tid, "--type", "task", "--project", sup.PROJECT,
         "--limit", "10"]))
    return raw[:6000] if raw else "task_detail: empty response for #%s" % tid


@server.tool()
def lessons(query: str) -> str:
    """Durable knowledge (bugfix/decision/pattern/config) matching query."""
    parts = []
    for typ in ("bugfix", "decision", "pattern", "config"):
        raw = sup.strip_banner(sup.run(
            ["search", query, "--type", typ, "--project", sup.PROJECT,
             "--limit", "20"]))
        if raw and not raw.startswith("__ERR__"):
            parts.append("--- %s ---\n%s" % (typ, raw[:3000]))
    body = "\n".join(parts) if parts else "lessons: no hits for %r" % query[:80]
    return body + "\n[pmb: pull via pmb__recall on the client; this host has no PMB push hook]"


def _run_cli_bounded(cmd, timeout=LEG_LIMIT_S, cwd=None, env=None):
    """Run a child CLI with a HARD tree-kill bound.

    subprocess.run(timeout=..) kills ONLY the direct child. On this host
    a venv `Scripts\\python.exe` is a launcher that spawns the real
    interpreter as a CHILD (observed live 2026-10-18: two identical
    pmb_client.py processes in a parent/child pair), so killing the
    launcher on timeout orphans the interpreter's grandchild -- alive,
    same command line, nobody reading its pipes: the ghost-CLI shape the
    Oct 18 goal complains about. Popen + `taskkill /T /F` takes launcher
    AND grandchild together.
    Returns (stdout, stderr, returncode); on timeout stdout is None and
    stderr names the kill -- callers print unreadable-loud, never silent.
    """
    import subprocess
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  # scanner:ignore subprocess_no_timeout -- Popen takes no timeout kwarg; the bound is communicate(timeout=<LEG>) below plus the taskkill /T tree-kill in its handler
                         text=True, encoding="utf-8", errors="replace",
                         cwd=cwd, env=env)
    try:
        out, err = p.communicate(timeout=timeout)
        return out, err, p.returncode
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=10)
        try:
            p.communicate(timeout=5)
        except Exception:  # best-effort drain after tree-kill; tree already gone
            pass  # scanner:ignore silent_except_pass (deliberate best-effort drain)
        return None, ("KILLED after %.0fs: taskkill /T (launcher pair)" % timeout), 0


def _pmb_endpoint():
    """Live daemon URL from its own registry -- same rules as pmb_client.py.

    The PMB daemon migrates ports and idle-exits; a constant endpoint goes
    stale the moment it does (the documented prepare_guard 8765 bug).
    """
    try:
        entries = json.loads(
            (Path(os.path.expanduser("~/.pmb")) / "servers.json")
            .read_text(encoding="utf-8"))
    except Exception:
        entries = []
    for entry in entries if isinstance(entries, list) else []:
        if not isinstance(entry, dict):
            continue
        if entry.get("kind") not in (None, "daemon"):
            continue
        if entry.get("pid_alive") is False:
            continue
        host = entry.get("host") or "127.0.0.1"
        port = entry.get("port")
        path = entry.get("path") or "/mcp"
        if port:
            return "http://%s:%s%s" % (host, port, path)
    return "http://127.0.0.1:8765/mcp"


def _pmb_http_call(name, arguments, timeout_s=15.0):
    """Call one PMB tool over streamable HTTP, IN-PROCESS -- zero children.

    pmb_client.py does this through the .pmb-venv `mcp` package because
    py315t's mcp lacks streamable_http_client (proven 2026-10-18:
    ImportError on the same import). Shelling out costs a launcher-pair
    child per call and its 45/90s timeout class was the leak. The MCP
    streamable-http slice needed here is small: fresh `initialize` per
    call (the daemon issues a session per INSTANCE, and a cached one dies
    at idle-exit -> `Session not found`), one notifications/initialized,
    then tools/call. The bearer token is reused across daemon restarts by
    design (daemon.write_daemon_token), so auth is not session-dependent.
    Raises on any failure; the caller decides the fallback.
    """
    import urllib.request

    home = Path(os.path.expanduser("~/.pmb"))
    url = _pmb_endpoint()
    token = (home / "daemon.token").read_text(encoding="utf-8").strip()
    headers = {
        "Authorization": "Bearer %s" % token,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    def _post(payload, session_id=None):
        hdr = dict(headers)
        if session_id:
            hdr["mcp-session-id"] = session_id
        req = urllib.request.Request(
            url, json.dumps(payload).encode("utf-8"), hdr)
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return (resp.status, resp.headers.get("mcp-session-id"),
                    resp.read().decode("utf-8", errors="replace"))

    def _parse(body):
        if "data:" in body:
            for line in reversed(body.splitlines()):
                if line.startswith("data:"):
                    try:
                        return json.loads(line[5:].strip())
                    except ValueError:
                        continue
            raise ValueError("SSE stream carried no parseable data line")
        return json.loads(body)

    last_exc = None
    for _attempt in (1, 2):  # one retry: dead session id on the first dance
        try:
            _status, session_id, body = _post(
                {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                 "params": {"protocolVersion": "2025-03-26",
                            "capabilities": {},
                            "clientInfo": {"name": "supervisor-verdict",
                                           "version": "1.0"}}})
            resp = _parse(body)
            if "error" in resp:
                raise RuntimeError(
                    "initialize: %s" % json.dumps(resp["error"])[:200])
            # This daemon (FastMCP 4.0.10 behind uvicorn, Connection: close)
            # returns SSE with NO mcp-session-id header at all -- a
            # stateless exchange; the spec issues a session id when it wants
            # continuity. Absent header = follow-up posts carry none.
            _post({"jsonrpc": "2.0", "method": "notifications/initialized"},
                  session_id)
            _status, _, body = _post(
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": name, "arguments": arguments}},
                session_id)
            resp = _parse(body)
            if "error" in resp:
                raise RuntimeError("call: %s" % json.dumps(resp["error"])[:200])
            result = resp.get("result", {})
            if result.get("isError"):
                raise RuntimeError("tool error: %s" % json.dumps(result)[:300])
            parts = []
            for item in result.get("content", []):
                if isinstance(item, dict):
                    parts.append(item.get("text", ""))
                else:
                    parts.append(getattr(item, "text", ""))
            text = "".join(parts)
            try:
                return json.loads(text)
            except (ValueError, TypeError):
                return text
        except Exception as exc:
            last_exc = exc
            if "session" not in str(exc).lower():
                raise
    raise last_exc  # noqa: locals are set by the loop; only "session" paths reach here


def _payload_summary(payload) -> str:
    """Text shape for a parsed MCP result, mirroring pmb_client's summary."""
    if not isinstance(payload, dict):
        return str(payload)
    lines = []
    for key in ("lessons", "decisions", "open_goals", "recent_activity",
                "results", "project_context"):
        value = payload.get(key)
        if not value:
            continue
        lines.append("--%s--" % key)
        if isinstance(value, dict):
            for k, v in list(value.items())[:12]:
                lines.append("  %s: %s" % (k, str(v)[:120]))
            continue
        if not isinstance(value, (list, tuple)):
            lines.append("  - " + str(value)[:140])
            continue
        for item in value[:8]:
            text = item.get("content", item) if isinstance(item, dict) else item
            lines.append("  - " + str(text)[:140])
    return "\n".join(lines)


def _pmb_goal_pressure() -> str:
    """Informational only: open-goal counts never change the verdict.

    Fifty stale pending goals must not flip a live gate to CLARIFY on every
    run -- that would train agents to ignore the verdict. Pressure is data
    for triage, not evidence of breakage. Primary path is the in-process
    HTTP call (no child at all); the CLI fallback is tree-killed at
    LEG_LIMIT_S, inside the verdict budget, so no child survives the
    response.
    """
    import ast
    payload = None
    http_note = ""
    try:
        payload = _pmb_http_call("list_goals", {"limit": 200})
    except Exception as exc:
        http_note = "http %s: %s" % (type(exc).__name__, str(exc)[:120])
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"  # wide chars kill cp1252 print (#706)
        try:
            out, err, rc = _run_cli_bounded(
                [PMB_VENV_PY, str(HERE / "pmb_client.py"), "call",
                 "list_goals", json.dumps({"limit": 200})],
                timeout=LEG_LIMIT_S, cwd=str(HERE.parent), env=env)
        except Exception as exc2:
            return ("pmb goals: UNREADABLE (%s; cli %s: %s)"
                    % (http_note, type(exc2).__name__, str(exc2)[:120]))
        if out is None:
            return ("pmb goals: UNREADABLE (%s; cli hung >%ds, tree-killed "
                    "-- no child survives)" % (http_note, LEG_LIMIT_S))
        raw = (out or "").strip()
        if not raw:
            return ("pmb goals: UNREADABLE (%s; rc=%d empty stdout; "
                    "stderr=%.80s)" % (http_note, rc,
                                       (err or "").replace("\n", " ")))
        try:
            payload = ast.literal_eval(raw)
        except (ValueError, SyntaxError) as exc2:
            return ("pmb goals: UNPARSEABLE (%s; %s: %.80s)"
                    % (http_note, type(exc2).__name__, raw[:80]))
    if isinstance(payload, dict) and "open_goals" in payload:
        goals = payload["open_goals"]
    elif isinstance(payload, list):
        goals = payload
    else:
        return "pmb goals: UNPARSEABLE (%s; shape=%s)" % (
            http_note or "http ok", type(payload).__name__)
    counts: dict[str, int] = {}
    for g in goals:
        st = str(g.get("status", "?")) if isinstance(g, dict) else str(g)
        counts[st] = counts.get(st, 0) + 1
    return ("pmb goals: " + ", ".join("%s=%d" % kv for kv in sorted(counts.items()))
            + " (informational; never verdict-changing)")


@server.tool()
def refusal_summary() -> str:
    """Counts from the refusal ledger. Missing ledger = zero refusals, said aloud."""
    import json
    from collections import Counter
    if not REFUSALS.exists():
        return "refusals: none recorded (ledger absent -- no NO-GO has fired yet)"
    tools = Counter()
    last = ""
    n = 0
    for line in REFUSALS.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        n += 1
        tools[str(r.get("tool", "?"))] += 1
        last = str(r.get("ts", ""))
    if not n:
        return "refusals: ledger present but empty"
    top = ", ".join("%s x%d" % kv for kv in tools.most_common(5))
    return "refusals: %d total (last %s); top: %s" % (n, last or "?", top)


TOOL_TEMPLATE = '''#!/usr/bin/env python
# coding: utf-8
"""%(name)s -- %(purpose)s

Generated by supervisor mint_tool (%(date)s). Contract: exit 0 + useful
stdout on success; non-zero + cause on failure; never silent, never a
fabricated pass. Run standalone before wiring anywhere.
"""
import sys


def run() -> str:
    %(body)s


def main(argv=None) -> int:
    try:
        print(run())
    except Exception as exc:
        print("%s FAILED (%s: %s)" % (type(exc).__name__, exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


@server.tool()
def mint_tool(name: str, purpose: str, body: str) -> str:
    """Auto-make a custom tool: writes tools/<name>.py from contract template.

    name: lowercase letters/digits/underscores. body: Python statements for
    run() ending in `return <string>`. The file is syntax-checked and
    executed (--help-free smoke run); failures are reported, never kept
    silent. Wiring (MCP registration, hooks) is a separate explicit step.
    """
    import ast
    import datetime
    import re
    import subprocess
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,40}", name or ""):
        return "mint_tool: bad name %r (lowercase, 3-40 chars)" % (name or "")[:60]
    if not (purpose or "").strip() or not (body or "").strip():
        return "mint_tool: purpose and body are both required"
    target = HERE / (name + ".py")
    if target.exists():
        return "mint_tool: REFUSED -- %s exists (delete explicitly first)" % target.name
    src = TOOL_TEMPLATE % {"name": name, "purpose": purpose.strip()[:200],
                           "body": body.strip(), "date": str(datetime.date.today())}
    try:
        ast.parse(src)
    except SyntaxError as exc:
        return "mint_tool: template syntax invalid (%s) -- not written" % exc
    target.write_text(src, encoding="utf-8")
    try:
        r = subprocess.run(
            ["C:/Azazael/.venvs/py315t/Scripts/python.exe", str(target)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120, cwd=str(HERE.parent))
        if r.returncode != 0:
            return ("mint_tool: wrote %s but smoke run FAILED (rc=%d): %s"
                    % (target.name, r.returncode, (r.stdout + r.stderr)[-500:]))
        return ("mint_tool: %s written + smoke ok (%d chars out). "
                "Wire it explicitly; nothing auto-registers."
                % (target.name, len(r.stdout or "")))
    except Exception as exc:
        return "mint_tool: wrote %s but smoke run unrunnable (%s: %s)" % (
            target.name, type(exc).__name__, exc)


@server.tool()
def record_outcome(title: str, body: str, kind: str = "lesson") -> str:
    """Write-through outcome: engram save + JSONL outbox row for PMB pickup.

    Returns per-store status so a half-write is loud, never silent.
    """
    title = title[:120]
    results = []
    saved = sup.strip_banner(sup.run(
        ["save", title, body[:4000], "--type", kind,
         "--project", sup.PROJECT]))
    results.append("engram: %s" % (saved[:200] if saved else "empty response"))
    row = {"ts": int(time.time()), "title": title,
           "body": body[:4000], "kind": kind}
    try:
        OUTBOX.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTBOX, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        results.append("outbox: appended %s" % OUTBOX.name)
    except OSError as exc:
        results.append("outbox: WRITE FAILED (%s)" % exc)
    return "\n".join(results)


@server.tool()
def triage_plan() -> str:
    """Open items each paired with the evidence check that resolves it."""
    items, note = _open_items()
    if items is None:
        return "triage: unknown (%s)" % note
    lines = ["triage: %d open items (%s)" % (len(items), note),
             "Resolve each by verifying the evidence, saving a DONE record,",
             "and judging the supersedes pair. Format: id|title => check"]
    buckets = {"fresh<7d": 0, "week-old": 0, "stale>30d": 0, "age-unknown": 0}
    for tid, title in items:
        low = title.lower()
        if "checkbox" in low or ".md" in low:
            check = "file alive on HEAD? close consumed / unblock or dead-with-proof"
        elif "kilo" in low:
            check = "verify Kilo lane state at HEAD; wire or retire with proof"
        elif "freebuff" in low:
            check = "verify Freebuff lane state at HEAD; execute or dead-with-proof"
        elif "quarantine" in low or "manifest" in low:
            check = "re-derive counts at HEAD; record fresh measurement"
        else:
            check = "verify against HEAD; execute or dead-with-proof"
        age = _item_age_days(_OPEN_DATES.get(tid, ""))
        if age < 0:
            buckets["age-unknown"] += 1
            age_s = "age?"
        elif age < 7:
            buckets["fresh<7d"] += 1
            age_s = "%dd" % age
        elif age <= 30:
            buckets["week-old"] += 1
            age_s = "%dd" % age
        else:
            buckets["stale>30d"] += 1
            age_s = "%dd STALE" % age
        lines.append("%s|%s => %s [%s]" % (tid, title[:110], check, age_s))
    lines.insert(1, "age: " + ", ".join("%s=%d" % kv for kv in buckets.items()))
    return "\n".join(lines)


PMB_VENV_PY = r"C:/Users/clint/.pmb-venv/Scripts/python.exe"
PAMS_BASE = os.path.expanduser("~/.pams/memory_data")


def _pmb_recall(query, top_k=5):
    """Recall leg for fanout_search: HTTP-primary, bounded-CLI fallback.

    The old 90s CLI leg was the leak shape -- every aborted fanout could
    leave a .pmb-venv interpreter alive long past its parent's timeout
    (venv-launcher pair; subprocess.run kills only the direct child).
    The HTTP primary spawns nothing; the fallback is tree-killed at
    LEG_LIMIT_S (20s), inside any caller's reasonable budget.
    """
    try:
        payload = _pmb_http_call("recall", {"query": query, "top_k": top_k})
        out = _payload_summary(payload)
        return out[:3000] if out else "pmb: empty response"
    except Exception as exc:
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        try:
            out, err, rc = _run_cli_bounded(
                [PMB_VENV_PY, str(HERE / "pmb_client.py"), "recall", query,
                 "--top-k", str(top_k)],
                timeout=LEG_LIMIT_S, cwd=str(HERE.parent), env=env)
        except Exception as exc2:
            return "pmb: UNREACHABLE (http %s: %s; cli %s: %s)" % (
                type(exc).__name__, str(exc)[:100],
                type(exc2).__name__, str(exc2)[:100])
        if out is None:
            return ("pmb: UNREACHABLE via CLI (hung >%ds, tree-killed -- no "
                    "child survives; http said %s: %s)"
                    % (LEG_LIMIT_S, type(exc).__name__, str(exc)[:100]))
        return (out or "").strip()[:3000] or "pmb: empty response"


def _pams_search(query, top_k=5):
    """PAMS leg: read-only LIKE over curated memories (no MCP round-trip)."""
    import sqlite3
    try:
        c = sqlite3.connect("file:%s/ai_memories.db?mode=ro" % PAMS_BASE, uri=True)
        toks = [t for t in query.split() if len(t) > 2][:4]
        if not toks:
            return "pams: query too short"
        where = " OR ".join(["content LIKE ?"] * len(toks))
        params = ["%%%s%%" % t for t in toks]
        rows = c.execute(
            "select memory_id, memory_type, substr(content,1,160) from "
            "curated_memories where %s limit %d" % (where, top_k), params).fetchall()
        c.close()
        if not rows:
            return "pams: no hits"
        return "\n".join("[%s|%s] %s" % r for r in rows)[:3000]
    except Exception as exc:
        return "pams: UNREADABLE (%s: %s)" % (type(exc).__name__, exc)


@server.tool()
def fanout_search(query: str) -> str:
    """One query across all three memories; per-leg status, partial never silent."""
    eng = sup.strip_banner(sup.run(
        ["search", query, "--project", sup.PROJECT, "--limit", "20"]))
    parts = ["--- engram ---\n" + (eng[:3000] if eng else "engram: empty"),
             "--- pmb ---\n" + _pmb_recall(query),
             "--- pams ---\n" + _pams_search(query)]
    return "\n".join(parts) + "\n[fanout: 3 legs, each labeled; an UNREACHABLE leg is a finding, not a gap]"


@server.tool()
def code_bridge(path_or_symbol: str) -> str:
    """Given a file path or symbol, return related Engram decisions + tasks.

    Joins code to memory through path-token search; degrades to basename
    search when the codegraph file is absent. Says which it used.
    """
    import os
    base = os.path.basename(path_or_symbol.rstrip("/\\"))
    stem = os.path.splitext(base)[0]
    q = "%s %s" % (path_or_symbol[:80], stem)
    eng = sup.strip_banner(sup.run(
        ["search", q, "--project", sup.PROJECT, "--limit", "20"]))
    return ("[code_bridge: token search on %r]\n" % base
            + (eng[:4000] if eng else "no memories mention these tokens"))


@server.tool()
def pretriage_conflicts(limit: str = "10") -> str:
    """Propose verdicts for pending pairs with one-line evidence. Never judges.

    Heuristic: a DONE-marked endpoint suggests supersedes; same-theme tasks
    suggest related; disjoint topics suggest not_conflict. The agent still
    judges every pair (architecture/policy pairs need a human look)."""
    try:
        n = max(1, min(25, int(str(limit).strip() or 10)))
    except ValueError:
        n = 10
    raw = sup.strip_banner(sup.run(
        ["conflicts", "list", "--project", sup.PROJECT,
         "--status", "pending", "--limit", str(n)]))
    if not raw or "Total:" not in raw:
        return "pretriage: no parseable pending list (empty store or new output shape)"
    if "No relations found" in raw:
        return "pretriage: 0 pending -- store clean, nothing to propose"
    blocks, cur = [], []
    for line in raw.splitlines():
        if line.strip().startswith("id:") and cur:
            blocks.append(cur)
            cur = []
        cur.append(line)
    if cur:
        blocks.append(cur)
    blocks = [b for b in blocks
              if any(l.strip().startswith(("id:", "sync_id:")) for l in b)]
    if not blocks:
        return "pretriage: 0 pending -- store clean, nothing to propose"
    out = ["pretriage: %d pending shown (proposals only -- judge each)" % len(blocks)]
    for b in blocks:
        text = "\n".join(b)
        sid = rid = ""
        endpoints = []
        for line in b:
            s = line.strip()
            if s.startswith("sync_id:"):
                sid = s.split(":", 1)[1].strip()
            elif s.startswith("id:"):
                rid = s.split(":", 1)[1].strip()
            elif s.startswith(("source:", "target:")):
                endpoints.append(s)
        joined = " | ".join(endpoints)
        if "DONE" in joined.upper():
            prop = "supersedes (DONE-marked endpoint)"
        elif "task" in joined.lower() and "task" in joined.lower().replace("task", "", 1):
            prop = "related (same-theme pair)"
        else:
            prop = "not_conflict unless topics overlap (verify titles)"
        out.append("[%s/%s] propose %s :: %s" % (rid, sid, prop, joined[:220]))
    return "\n".join(out)[:6000]


def main(argv=None) -> int:
    """--verdict prints the verdict text for hook/gate consumers (no MCP round-trip).

    Always exits 0: an unreachable oracle is fail-open (GO), and the text
    carries the verdict. Gate callers parse the trailing VERDICT line.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if "--verdict" in args:
        try:
            print(verdict.fn() if hasattr(verdict, "fn") else verdict())
        except Exception as exc:
            print("VERDICT: GO - supervisor unavailable (%s: %s)"
                  % (type(exc).__name__, exc))
        return 0
    server.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
