# coding: utf-8
"""cradle -- the whole chain behind one command, for someone who has Python and a model.

WHAT CRADLE IS
--------------
Four parts that already existed and did not know about each other:

    FLAMING SWORD   sweeps a codebase: find -> queue -> fix -> prove -> land
    defender        takes a user prompt and writes the frame it must satisfy
    REAPER          (sentinel) reaps a frame whose claims do not resolve -- it refuses to
                    let the act happen, and it shows the claim that failed
    GRIMOIRE        (memory)   the written book: every lesson a failed verification
                    authored, recalled by the next frame, or reported UNMEMORED

CRADLE is the name for the composition, the launcher, and the one endpoint a user can
point their own model at. It adds no judgement of its own: every check it runs is one of
those four, called in the order that makes each answer meaningful.

THE NAMES, AND WHY THEY ARE NOT FILE NAMES
------------------------------------------
A cradle holds; a grimoire is the book kept in it; a reaper is what takes what does not
hold. Those are the true names, and they are vocabulary rather than paths: `sentinel.py`
and `lessons.jsonl` keep their file names because five gates, a task file and three
documents quote those paths, and renaming a path to match a story breaks the gates that
make the story worth telling. So the tool says REAPER where it means the reaper, and
GRIMOIRE where it means the book, and the disk says what it always said.

WHY A LAUNCHER AND NOT A RENAME
-------------------------------
The tools keep their paths because those paths are quoted in a preflight registry, a task
file and three documents; renaming files to match a product name would break the gates
that make the product trustworthy, which is a bad trade. So CRADLE is the front door: one
file to run, one document to read, and the machinery where the gates already point.

FOUR THINGS IT DOES
-------------------
    python cradle.py --doctor                 is this machine ready, and what is missing
    python cradle.py --demo                   prove the loop end to end, no model needed
    python cradle.py --grimoire               read THE GRIMOIRE back: what it learned
    python cradle.py --serve --model-url ...  serve the chain to your own model

`--doctor` is deliberately boring: it prints a line per requirement and exits 1 on any
failure. `--demo` runs the real tools against a real file in a temp state directory, and
it includes a DELIBERATE FAILED VERIFICATION so you can see a lesson being written -- a
demo that only shows the happy path teaches nothing about what the gates refuse.

USAGE
-----
    python cradle.py --doctor
    python cradle.py --demo [--json]
    python cradle.py --grimoire [--kind failed-verification] [--limit 0]
    python cradle.py --serve --model-url http://127.0.0.1:11434/v1 --model-name llama3.1

    # hardware with no local model yet (Ollama serves an OpenAI-compatible API):
    ollama pull llama3.1 && ollama serve
    python cradle.py --serve --model-url http://127.0.0.1:11434/v1 --model-name llama3.1
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
LOCAL_TOOLS = ROOT / "tools"
SWORD_TOOLS = REPO / "Project_FLAMING_SWORD" / "tools"

#: The four parts, with the path that must exist for the chain to be whole.
#: Prefers vendored tools in Project_CRADLE/tools/; falls back to external FLAMING_SWORD.
def _part_path(name: str) -> Path:
    # Map CRADLE's internal names to actual filenames
    filename_map = {
        "defender": "defender.py",
        "sentinel": "sentinel.py",
        "memory": "memory_bridge.py",
        "server": "chain_server.py",
        "sword": "sword.py",
    }
    filename = filename_map.get(name, f"{name}.py")
    local = LOCAL_TOOLS / filename
    if local.exists():
        return local
    external = SWORD_TOOLS / filename
    if external.exists():
        return external
    return SWORD_TOOLS / f"{name}.py"

PARTS = {name: _part_path(name) for name in
         ("defender", "sentinel", "memory", "server", "sword")}

#: The true names. A part keeps its file path and gains the name of what it does: the
#: sentinel REAPS a frame whose claims do not resolve, and the memory keeps the GRIMOIRE
#: -- the written book of lessons, one line per thing that failed or was refused.
NAMES = {
    "sword": ("FLAMING SWORD", "sweeps the codebase: find -> queue -> fix -> prove -> land"),
    "defender": ("defender", "a prompt becomes a frame that can be satisfied or refused"),
    "sentinel": ("REAPER", "reaps a frame whose claims do not resolve; shows the claim"),
    "memory": ("GRIMOIRE", "the written book of lessons; recalls, or says UNMEMORED"),
    "server": ("server", "one endpoint, in the shape your own model already speaks"),
}

MIN_PYTHON = (3, 9)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location("cradle_%s" % name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# --doctor: the question a new user actually has
# --------------------------------------------------------------------------- #

def doctor(model_url: str = "", json_out: bool = False) -> int:
    checks: List[Tuple[str, bool, str]] = []

    current = sys.version_info[:3]
    checks.append(("python", current >= MIN_PYTHON,
                   "%d.%d.%d (needs >= %d.%d; stdlib only, nothing to pip install)"
                   % (current + MIN_PYTHON)))

    # A standalone install of CRADLE contains vendored tools in Project_CRADLE/tools/.
    # External FLAMING_SWORD is optional and provides updates/alternatives.
    chain_installed = LOCAL_TOOLS.is_dir()
    external_available = SWORD_TOOLS.is_dir()
    for name, path in PARTS.items():
        if path.exists():
            source = "vendored" if str(path).startswith(str(LOCAL_TOOLS)) else "external"
            checks.append((name, True, "%s (%s)" % (path.relative_to(REPO), source)))
        elif chain_installed or external_available:
            checks.append((name, False, "MISSING: %s" % path))
        else:
            checks.append((name, None,
                           "not installed: FLAMING_SWORD is a separate project "
                           "(install it beside this tree to enable the chain)"))

    # The state directory is where frames, lessons and verifications land. A chain that
    # cannot write there is a chain that reports success and remembers nothing.
    try:
        with tempfile.TemporaryDirectory() as tmp:
            probe = Path(tmp) / "cradle-doctor.txt"
            probe.write_text("ok", encoding="utf-8")
        writable, detail = True, "writable (temp probe)"
    except OSError as exc:
        writable, detail = False, "NOT writable: %s" % exc
    checks.append(("state-writable", writable, detail))

    checks.append(("git", shutil.which("git") is not None,
                   shutil.which("git") or "MISSING: the sweep's land step needs git"))

    if model_url:
        ok, detail = _probe_model(model_url)
        checks.append(("model", ok, detail))
    else:
        # Stated, not failed: no model is a supported state and /ask says 503.
        checks.append(("model", True, "none configured -- --serve still works, /ask "
                                       "answers 503 with that reason"))

    failures = [name for name, ok, _detail in checks if ok is False]
    if json_out:
        print(json.dumps({"ok": not failures, "failures": failures,
                          "checks": [{"name": n, "ok": ok, "detail": d}
                                     for n, ok, d in checks]}, indent=1))
    else:
        print("CRADLE doctor")
        for name, ok, detail in checks:
            true_name, _role = NAMES.get(name, (name, ""))
            label = true_name if true_name == name else "%s (%s)" % (true_name, name)
            verdict = "PASS" if ok else ("N/A" if ok is None else "FAIL")
            print("  %-24s %-6s %s" % (label, verdict, detail))
        print("")
        if failures:
            print("NOT READY: %d check(s) failed (%s)" % (len(failures),
                                                          ", ".join(failures)))
            print("  each one is a real absence; none of them is fixed by reading "
                  "further")
        else:
            absent = [n for n, ok, _d in checks if ok is None]
            if absent:
                print("READY (standalone): %d chain part(s) not installed (%s)."
                      % (len(absent), ", ".join(absent)))
                print("  --demo needs them: install FLAMING_SWORD beside this tree first.")
            else:
                print("READY. next: python cradle.py --demo")
    return 0 if not failures else 1


def _probe_model(model_url: str) -> Tuple[bool, str]:
    """Ask the endpoint for its model list. A 404 here is a wrong URL, not a bad model."""
    url = model_url.rstrip("/") + "/models"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
        names = [entry.get("id") for entry in payload.get("data") or []
                 if isinstance(entry, dict)]
        return True, "%s -> %s" % (model_url, ", ".join(names[:3]) or "no models listed")
    except urllib.error.HTTPError as exc:
        return False, "%s answered HTTP %d (is the base URL right? it should end /v1)" % (
            url, exc.code)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return False, "%s did not answer: %s" % (url, exc)


# --------------------------------------------------------------------------- #
# --demo: the loop, including what it refuses
# --------------------------------------------------------------------------- #

def demo(json_out: bool = False) -> int:
    """Run the real chain in a throwaway state directory. Exit 1 if any step misbehaved."""
    missing = [name for name, path in PARTS.items() if not path.exists()]
    if missing:
        print("CANNOT DEMO: missing part(s): %s" % ", ".join(missing))
        print("  Install FLAMING_SWORD beside this tree, or ensure vendored tools are present.")
        return 1
    defender = _load("defender", PARTS["defender"])
    bridge = _load("memory_bridge", PARTS["memory"])
    steps: List[Dict[str, Any]] = []
    failures = 0

    with tempfile.TemporaryDirectory() as tmp:
        target = str(PARTS["sword"])
        # Evidence paths: prefer vendored, fall back to external
        evidence_path = Path("tests/test_defender.py")
        if not evidence_path.exists():
            evidence_path = Path("../Project_FLAMING_SWORD/tests/test_defender.py")
        must_not_break_path = evidence_path
        
        result = defender.to_aio(
            "refuse a shard whose golden run does not reproduce",
            target=target,
            acceptance="pytest -q exits 0 and prints 98 passed",
            evidence=str(evidence_path),
            defends=["the golden run's state_sha256 token"],
            must_not_break=[str(must_not_break_path)],
            control="flip one byte in state_sha256 and require a REFUSAL",
            memory=bridge.probe(),
            root=str(ROOT),
        )
        steps.append({"step": "frame+sentinel+memory -> AIO",
                      "state": result["state"],
                      "frame_id": result.get("frame", {}).get("frame_id"),
                      "ok": result["state"].startswith("READY"),
                      "detail": "%d chars of instruction" % len(result.get("aio", ""))})
        failures += 0 if steps[-1]["ok"] else 1

        if result.get("aio"):
            bridge.record(result["frame"], state_dir=tmp)
            steps.append({"step": "frame written",
                          "ok": (Path(tmp) / bridge.FRAMES_FILE).exists(),
                          "detail": bridge.FRAMES_FILE, "state": "WRITTEN"})
            failures += 0 if steps[-1]["ok"] else 1

        # A deliberate FAILURE. The demo's job is to show the loop learning, and a loop
        # only learns from the run that did not pass.
        written = bridge.record_verification(
            result.get("frame", {}).get("frame_id", "f-demo"),
            "pytest -q", 1, observed="2 failed, 96 passed -- this is deliberate",
            state_dir=tmp)
        steps.append({"step": "verification FAILED -> lesson written",
                      "state": written["verdict"], "ok": written["verdict"] == "FAILED"
                      and bool(written.get("lesson")), "detail": "recorded"})
        failures += 0 if steps[-1]["ok"] else 1

        recalled = bridge.recall("acceptance command exited", jsonl=str(
            Path(tmp) / bridge.LESSONS_FILE))
        steps.append({"step": "lesson recalled by the next frame",
                      "state": recalled["state"], "ok": bool(recalled["matches"]),
                      "detail": "%d match(es)" % len(recalled["matches"])})
        failures += 0 if steps[-1]["ok"] else 1

        # Evidence and break list are REAL here on purpose: the demo has to reach the
        # sentinel, not stop at the frame, or it would be demonstrating the wrong check.
        refused = defender.to_aio("refuse a shard whose golden run does not reproduce",
                                  target="tools/ghost.py",
                                  acceptance="pytest -q exits 0 and prints 98 passed",
                                  evidence="tests/test_defender.py",
                                  defends=["the golden run's state_sha256 token"],
                                  must_not_break=["tests/test_defender.py"],
                                  root=str(ROOT))
        steps.append({"step": "a ghost target is BLOCKED and renders no prompt",
                      "state": refused["state"],
                      "ok": refused["state"] == "BLOCKED" and not refused["aio"],
                      "detail": "no AIO"})
        failures += 0 if steps[-1]["ok"] else 1

    if json_out:
        print(json.dumps({"ok": not failures, "steps": steps}, indent=1))
    else:
        print("CRADLE demo -- the real chain, a throwaway directory, one deliberate "
              "failure")
        for step in steps:
            print("  %-6s %-46s %s" % ("PASS" if step["ok"] else "FAIL",
                                       step["step"], step["state"]))
            if step.get("detail"):
                print("         %s" % step["detail"])
        print("")
        print("DEMO %s" % ("OK -- frame, verification and lesson all landed" if not failures
                           else "FAILED -- %d step(s)" % failures))
    return 0 if not failures else 1


# --------------------------------------------------------------------------- #
# --grimoire: read the book back
# --------------------------------------------------------------------------- #

def grimoire(state_dir: Optional[str] = None, kind: str = "", limit: int = 20,
             json_out: bool = False) -> int:
    """Print THE GRIMOIRE -- the lessons a failed verification authored.

    WHY A READER AND NOT JUST A FILE: a book with a name and no reader is a directory.
    The ledger exists so the NEXT frame answers better, and the person who has to trust
    that is the one holding the machine. So this prints what was learned, when, and what
    made it -- and it distinguishes three states that used to look identical:

      no book yet      nothing has failed in this directory (a fresh install)
      empty book       the book exists and holds nothing (a writer that never wrote)
      unreadable       a line is malformed -- reported by line number, never skipped
    """
    if not PARTS["memory"].exists():
        print("CANNOT READ THE GRIMOIRE: %s is missing (install FLAMING_SWORD)" % PARTS["memory"])
        return 1
    bridge = _load("memory_bridge", PARTS["memory"])
    directory = Path(state_dir) if state_dir else Path.cwd() / bridge.STATE_DAY_DIR
    ledger = directory / bridge.GRIMOIRE
    if not ledger.exists():
        if json_out:
            print(json.dumps({"state": "NO-BOOK", "path": str(ledger), "lessons": []},
                             indent=1))
        else:
            print("THE GRIMOIRE: no book yet at %s" % ledger)
            print("  nothing has failed here, and a lesson is written by a failure --")
            print("  run `python Project_CRADLE/cradle.py --demo` to see one written")
        return 0

    records, error = bridge._read_jsonl(ledger)
    if error:
        # An unreadable line is a finding, not a line to skip: a book you cannot read
        # back is the same as no book, except that it lies about having one.
        print("THE GRIMOIRE IS UNREADABLE: %s" % error)
        print("  file: %s" % ledger)
        return 1

    wanted = [record for record in records
              if not kind or str(record.get("kind") or "") == kind]
    shown = wanted[-limit:] if limit > 0 else wanted
    if json_out:
        print(json.dumps({"state": "BOOK", "path": str(ledger),
                          "total": len(records), "shown": len(shown),
                          "lessons": shown}, indent=1))
        return 0

    print("THE GRIMOIRE %s" % ledger)
    if not records:
        print("  the book exists and holds nothing -- a writer that has not written,")
        print("  which is a finding, not a setting")
        return 0
    if kind:
        print("  %d lesson(s) in the book, %d of kind %r (newest %d shown):"
              % (len(records), len(wanted), kind, len(shown)))
    else:
        print("  %d lesson(s), newest %d:" % (len(records), len(shown)))
    for record in shown:
        print("  %s  %-20s %s" % (str(record.get("written_at") or "----------")[:10],
                                   str(record.get("kind") or "lesson")[:20],
                                   str(record.get("content") or "")[:110]))
        trigger = str(record.get("trigger") or "")
        if trigger:
            print("              because: %s" % trigger[:100])
    return 0


# --------------------------------------------------------------------------- #
# --serve: hand the chain to the user's own model
# --------------------------------------------------------------------------- #

def serve(passthrough: List[str]) -> int:
    if not PARTS["server"].exists():
        print("CANNOT SERVE: %s is missing (install FLAMING_SWORD)" % PARTS["server"])
        return 1
    server = _load("chain_server", PARTS["server"])
    return int(server.main(passthrough))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="CRADLE: FLAMING SWORD + defender + sentinel + memory, behind one "
                    "command.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--doctor", action="store_true", help="is this machine ready")
    mode.add_argument("--demo", action="store_true", help="prove the loop, no model")
    mode.add_argument("--serve", action="store_true", help="serve the chain to your model")
    mode.add_argument("--grimoire", action="store_true",
                      help="read THE GRIMOIRE: the lessons a failed verification wrote")
    parser.add_argument("--kind", default="", help="with --grimoire: only this kind")
    parser.add_argument("--limit", type=int, default=20,
                        help="with --grimoire: how many to show (0 = all)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--model-url", default="",
                        help="OpenAI-compatible base URL, e.g. "
                             "http://127.0.0.1:11434/v1 (Ollama)")
    parser.add_argument("--model-name", default="")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--state-dir", default=None)
    parser.add_argument("extra", nargs="*", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.serve:
        passthrough = ["--port", str(args.port), "--host", args.host]
        if args.model_url:
            passthrough += ["--model-url", args.model_url]
        if args.model_name:
            passthrough += ["--model-name", args.model_name]
        if args.state_dir:
            passthrough += ["--state-dir", args.state_dir]
        return serve(passthrough)
    if args.demo:
        return demo(json_out=args.json)
    if args.grimoire:
        return grimoire(state_dir=args.state_dir, kind=args.kind, limit=args.limit,
                        json_out=args.json)
    # --doctor is the default: a user who runs `python cradle.py` has a question.
    return doctor(model_url=args.model_url, json_out=args.json)


if __name__ == "__main__":
    sys.exit(main())
