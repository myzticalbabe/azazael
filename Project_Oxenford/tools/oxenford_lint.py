"""OXENFORD lint — check a project against the seven-stage evolution paradigm.

A paradigm that lives only in prose is a hope. This reads a project's own
declaration (oxenford.json) and checks the stages that can be checked
mechanically, then runs the project's measurement selftest so the declaration
cannot outrun behaviour.

Checks, in stage order:

    O1 REGISTRY    the door list exists and every door names id, url, category
    O2 MEASURE     the probe runs live (--run) and writes the declared artifact
    O3 CLASSIFY    the probe can be held to expectations (--expect)
    O4 ADAPT       the runtime reads the measured artifact
    O5 GUARD       the probe carries negative controls (>= 2 CONTROL markers)
    O6 VERIFY      the probe's own --selftest runs and exits 0
    O7 RECORD      the limitation document exists and names its limitations

Exit codes: 0 every check passed; 1 a check failed; 2 no declaration, so nothing
could be checked. `--selftest` builds a conforming fixture (must pass) and a
violating fixture (must fail) — a lint without a negative control is the defect
it was written to catch.

Stdlib only. No network.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

ARTIFACT_KEYS = ("registry", "tool", "census", "runtime", "docs")


def read_text(path: Path) -> Optional[str]:
    """None means unreadable, which is not the same as empty.

    Returning "" here made an unreadable file indistinguishable from an empty
    one, and the caller then reported the wrong reason for the failure.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"  [WARN] cannot read {path.name}: {exc.__class__.__name__}")
        return None


def check_registry(root: Path, rel: str):
    path = root / rel
    if not path.exists():
        return False, f"{rel}: missing"
    text = read_text(path)
    if text is None:
        return False, f"{rel}: unreadable"
    try:
        blob = json.loads(text)
    except Exception as exc:
        return False, f"{rel}: not valid JSON ({exc.__class__.__name__})"
    entries = blob.get("portals") or blob.get("entries") or (blob if isinstance(blob, list) else [])
    if not entries:
        return False, f"{rel}: no doors listed"
    bad = [e for e in entries if not all(str(e.get(k) or "").strip() for k in ("id", "url", "category"))]
    if bad:
        ids = ", ".join(str(e.get("id", "<no id>")) for e in bad[:3])
        return False, f"{rel}: {len(bad)} door(s) without id/url/category ({ids})"
    cats = sorted({e["category"] for e in entries})
    return True, f"{rel}: {len(entries)} doors in {len(cats)} categories"


def check_probe(root: Path, tool_rel: str, census_rel: str):
    path = root / tool_rel
    if not path.exists():
        return False, f"{tool_rel}: missing"
    src = read_text(path)
    if src is None:
        return False, f"{tool_rel}: unreadable"
    missing = [flag for flag in ("--run", "--expect") if flag not in src]
    if missing:
        return False, f"{tool_rel}: no live-run flag ({', '.join(missing)})"
    if Path(census_rel).name not in src:
        return False, (f"{tool_rel}: never names {Path(census_rel).name} — "
                       f"the run writes nothing the runtime can read")
    return True, f"{tool_rel}: live run + expectations, writes {Path(census_rel).name}"


def check_controls(root: Path, tool_rel: str):
    src = read_text(root / tool_rel)
    if src is None:
        return False, f"{tool_rel}: unreadable"
    count = src.upper().count("CONTROL")
    if count < 2:
        return False, f"{tool_rel}: {count} negative control(s), need >= 2"
    return True, f"{tool_rel}: {count} negative-control markers"


def check_consumed(root: Path, runtime_rel: str, census_rel: str):
    src = read_text(root / runtime_rel)
    if src is None:
        return False, f"{runtime_rel}: missing"
    name = Path(census_rel).name
    if name not in src and Path(census_rel).stem not in src:
        return False, (f"{runtime_rel}: never reads {name} — the measurement is a "
                       f"report, not an adaptation")
    return True, f"{runtime_rel}: reads {name}"


def check_docs(root: Path, docs_rel: str):
    path = root / docs_rel
    if not path.exists():
        return False, f"{docs_rel}: missing"
    raw = read_text(path)
    if raw is None:
        return False, f"{docs_rel}: unreadable"
    text = raw.lower()
    if "limitation" not in text:
        return False, f"{docs_rel}: names no limitation — an incomplete artifact"
    return True, f"{docs_rel}: records limitations"


def check_selftest(root: Path, tool_rel: str):
    path = root / tool_rel
    if not path.exists():
        return False, f"{tool_rel}: missing"
    src = read_text(path)
    if src is None:
        return False, f"{tool_rel}: unreadable"
    if "--selftest" not in src:
        return False, f"{tool_rel}: no --selftest, so nothing is exercised"
    try:
        proc = subprocess.run([sys.executable, str(path), "--selftest"],
                              cwd=str(root), capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return False, f"{tool_rel} --selftest: HUNG past 180s"
    if proc.returncode != 0:
        tail = (proc.stdout or proc.stderr).strip().splitlines()[-1:] or ["<no output>"]
        return False, f"{tool_rel} --selftest: exit {proc.returncode} — {tail[0][:90]}"
    return True, f"{tool_rel} --selftest: exit 0"


def lint(root: Path) -> int:
    decl_path = root / "oxenford.json"
    if not decl_path.exists():
        print(f"OXENFORD BLIND: no oxenford.json in {root}")
        print("  declare registry/tool/census/runtime/docs, then re-run")
        return 2
    decl_text = read_text(decl_path)
    if decl_text is None:
        print("OXENFORD BLIND: oxenford.json unreadable")
        return 2
    try:
        decl = json.loads(decl_text)
    except Exception as exc:
        print(f"OXENFORD BLIND: oxenford.json unreadable ({exc!r})")
        return 2
    absent = [k for k in ARTIFACT_KEYS if not decl.get(k)]
    if absent:
        print(f"OXENFORD BLIND: oxenford.json does not declare {', '.join(absent)}")
        return 2

    checks = [
        ("O1 REGISTRY", *check_registry(root, decl["registry"])),
        ("O2 MEASURE", *check_probe(root, decl["tool"], decl["census"])),
        ("O5 GUARD", *check_controls(root, decl["tool"])),
        ("O6 VERIFY", *check_selftest(root, decl["tool"])),
        ("O4 ADAPT", *check_consumed(root, decl["runtime"], decl["census"])),
        ("O7 RECORD", *check_docs(root, decl["docs"])),
    ]
    failures = [name for name, ok, _ in checks if not ok]
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:12s} {detail}")
    print(f"\nOXENFORD {'PASS' if not failures else 'FAIL'}: "
          f"{len(checks) - len(failures)}/{len(checks)} stages held"
          + (f"; failed: {', '.join(failures)}" if failures else ""))
    return 1 if failures else 0


CONFORMING_PROBE = '''"""Fixture probe."""
import sys
if "--selftest" in sys.argv:
    print("  [selftest] CONTROL: a search panel is not a form")
    print("  [selftest] CONTROL: a newsletter box is not a form")
    print("  [selftest] clean")
    sys.exit(0)
print("--expect doors.json --run writes doors_probe.json")
'''

VIOLATING_PROBE = '''"""Fixture probe with no controls and a failing selftest."""
import sys
if "--selftest" in sys.argv:
    sys.exit(3)
print("--selftest")
'''


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def selftest() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "good"
        _write(good, "oxenford.json", json.dumps({
            "registry": "data/doors.json", "tool": "tools/probe.py",
            "census": "data/doors_probe.json", "runtime": "app.py",
            "docs": "docs/NOTES.md"}))
        _write(good, "data/doors.json", json.dumps({"portals": [
            {"id": "one", "url": "https://a.invalid", "category": "cat_a"},
            {"id": "two", "url": "https://b.invalid", "category": "cat_b"}]}))
        _write(good, "tools/probe.py", CONFORMING_PROBE)
        _write(good, "app.py", "CENSUS = 'data/doors_probe.json'\n")
        _write(good, "docs/NOTES.md", "# Notes\n\n## Limitations\n- none yet\n")
        rc = lint(good)
        ok = rc == 0
        failures += 0 if ok else 1
        print(f"  [selftest] conforming fixture: {'ok' if ok else f'FAIL (exit {rc})'}")

    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad"
        _write(bad, "oxenford.json", json.dumps({
            "registry": "data/doors.json", "tool": "tools/probe.py",
            "census": "data/doors_probe.json", "runtime": "app.py",
            "docs": "docs/NOTES.md"}))
        _write(bad, "data/doors.json", json.dumps({"portals": [
            {"id": "one", "url": "https://a.invalid"}]}))
        _write(bad, "tools/probe.py", VIOLATING_PROBE)
        _write(bad, "app.py", "print('no census read')\n")
        _write(bad, "docs/NOTES.md", "# Notes\n\nAll good.\n")
        rc = lint(bad)
        ok = rc == 1
        failures += 0 if ok else 1
        print(f"  [selftest] violating fixture caught: {'ok' if ok else f'FAIL (exit {rc})'}")

    with tempfile.TemporaryDirectory() as tmp:
        rc = lint(Path(tmp))
        ok = rc == 2
        failures += 0 if ok else 1
        print(f"  [selftest] no declaration is BLIND, not a pass: {'ok' if ok else f'FAIL (exit {rc})'}")

    print(f"  [selftest] {'clean' if not failures else str(failures) + ' failed'}")
    return 1 if failures else 0


def main(argv) -> int:
    parser = argparse.ArgumentParser(prog="oxenford_lint")
    parser.add_argument("--project", help="project directory holding oxenford.json")
    parser.add_argument("--selftest", action="store_true", help="check the lint itself")
    args = parser.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if not args.project:
        parser.print_help()
        return 2
    return lint(Path(args.project).resolve())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
