#!/usr/bin/env python3
"""drift_audit.py -- canon CONTENT drift per environment (heads are head_audit's).

head_audit owns refs: branches, worktrees, digests. This tool owns what the
bytes SAY: every generated `<!-- AO:<key> ... -->` canon block in every lane
instruction file, re-rendered from source and compared line by line, on each
environment that carries one. A block that matches its source in one
environment and not in another is the split-brain of 2026-10-31 (WSL lanes
starting without the protocol every Windows lane had) -- and a ref audit
cannot see it, because the refs all agree while the content disagrees.

Environments come from the developed inventory, never a new list:
agent_orders_sync.TARGETS (this host) and WSL_TARGETS (each distro, read over
`wsl.exe`, translated expectation via render_for_wsl). An unreachable distro
is `unreachable`, not a failure: a gate that fails on a stopped VM gets
switched off, and a switched-off gate protects nothing.

Exit: 0 when run (advisory findings print, like every other auditor), 1 with
--strict when any drift is open, 2 when the audit could not be performed.
`--include PATH --as-env NAME` audits one extra local file as its own
environment: the seam a seeded-drift self-test uses (/tmp, never the repo).

Measured anchors: the inventory it reads is the same TARGETS/WSL_TARGETS the
sync writes, so a block this tool calls drifted is a block `--check` would
rewrite -- no second definition of drift.
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import agent_orders_sync as aos          # noqa: E402  (developed inventory)


def _setting(key: str, fallback):
    try:
        import defaults_profile          # noqa: PLC0415
        return defaults_profile.read_default(key, fallback)
    except Exception:
        return fallback


def _blocks(text):
    """{key: block} for every AO block present, via the sync's own extract."""
    found = {}
    for key in aos.TARGETS:
        block = aos.extract(text, key)
        if block is not None:
            found[key] = block
    return found


def _first_diff(expected, actual):
    """(line_no, expected_line, actual_line) of the first difference, 1-based."""
    for no, (e, a) in enumerate(zip(expected.splitlines(),
                                   actual.splitlines()), 1):
        if e != a:
            return no, e[:120], a[:120]
    if len(expected.splitlines()) != len(actual.splitlines()):
        no = min(len(expected.splitlines()),
                 len(actual.splitlines())) + 1
        return no, "<end of block>", "<end of block>"
    return None


def _audit_local(env, paths, render):
    """Compare each local file's blocks to freshly rendered source."""
    seen, blocks, drifted, missing = set(), 0, [], []
    for key, (source, _targets) in aos.TARGETS.items():
        _ = _targets  # paths come from the caller, not the registry
        expected = aos.normalise(render(key, source)).rstrip("\n") + "\n"
        for path in paths.get(key, []):
            p = Path(path)
            if not p.exists():
                missing.append(str(p))
                continue
            seen.add(str(p))
            try:
                text = aos.normalise(p.read_text(encoding="utf-8",
                                                 errors="replace"))
            except OSError as exc:
                drifted.append("%s unreadable (%s)" % (p, exc))
                continue
            actual = aos.extract(text, key)
            if actual is None:
                drifted.append("%s: block %s absent" % (p, key))
                continue
            blocks += 1
            diff = _first_diff(expected, aos.normalise(actual).rstrip("\n")
                               + "\n")
            if diff is not None:
                no, exp, act = diff
                drifted.append("%s: block %s drifts at line %d\n    - %s\n    + %s"
                               % (p, key, no, exp, act))
    return {"env": env, "files": len(seen), "blocks": blocks,
            "drifted": drifted, "missing": missing}


def _audit_wsl(distro, remote_paths):
    """One wsl call per distro; unreachable is a state, never a failure."""
    script = ("for f in %s; do echo '==FILE=='; echo \"$f\"; "
              "if [ -f \"$f\" ]; then cat \"$f\"; else echo '==MISSING=='; fi; done"
              % " ".join("'%s'" % p for p in remote_paths))
    try:
        rc, out = aos._wsl(distro, script, timeout=60)
    except Exception as exc:
        return {"env": "wsl:" + distro, "unreachable": "%s: %s"
                % (type(exc).__name__, str(exc)[:120])}
    if rc != 0 or not out:
        return {"env": "wsl:" + distro, "unreachable": "rc=%s" % rc}
    chunks = out.split("==FILE==")
    texts = {}
    for chunk in chunks[1:]:
        # Skip LEADING blanks only (the path line): stripping blanks from the
        # body would rewrite the block and manufacture drift on every file.
        raw = chunk.splitlines()
        i = 0
        while i < len(raw) and not raw[i].strip():
            i += 1
        if i >= len(raw):
            continue
        texts[raw[i].strip()] = "\n".join(raw[i + 1:])
    seen, blocks, drifted, missing = set(), 0, [], []
    for key, (source, _targets) in aos.TARGETS.items():
        expected = aos.normalise(aos.render_for_wsl(key, source)).rstrip("\n") + "\n"
        for path in remote_paths:
            if path not in texts:
                continue
            body = texts[path]
            if body.strip() == "==MISSING==":
                missing.append("%s:%s" % (distro, path))
                continue
            seen.add(path)
            actual = aos.extract(aos.normalise(body), key)
            if actual is None:
                drifted.append("%s:%s: block %s absent" % (distro, path, key))
                continue
            blocks += 1
            diff = _first_diff(expected, aos.normalise(actual).rstrip("\n")
                               + "\n")
            if diff is not None:
                no, exp, act = diff
                drifted.append("%s:%s: block %s drifts at line %d"
                               % (distro, path, key, no))
    return {"env": "wsl:" + distro, "files": len(seen), "blocks": blocks,
            "drifted": drifted, "missing": missing}


def _summarise(rep):
    if "unreachable" in rep:
        return "%s: unreachable (%s)" % (rep["env"], rep["unreachable"])
    base = "%s: %d file(s), %d block(s)" % (rep["env"], rep["files"],
                                           rep["blocks"])
    if not rep["drifted"]:
        extra = "" if not rep["missing"] else " (%d missing, not drift)" \
            % len(rep["missing"])
        return base + ", all match" + extra
    return base + ", DRIFT: " + " | ".join(rep["drifted"][:3])


def audit(extra=None):
    """Run every environment. extra = [(env, path)] local seed files."""
    reps = []
    win = {}
    for key, (_source, paths) in aos.TARGETS.items():
        win[key] = [str(p) for p in paths]
    reps.append(_audit_local("windows", win, aos.render))
    if extra:
        for env, path in extra:
            reps.append(_audit_local(env,
                                    {k: [path] for k in aos.TARGETS},
                                    aos.render))
    for distro, remote_paths in aos.WSL_TARGETS.items():
        reps.append(_audit_wsl(distro, remote_paths))
    return reps


# Self-proof budget (slice 6): boots two stopped WSL distros; measured
# well under a minute 2026-11-12. Headroom for slow boots.
BUDGET_S = 240.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="drift_audit.py",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--include", default=None,
                    help="extra local file to audit (seed self-test)")
    ap.add_argument("--as-env", default="seed",
                    help="environment name for --include")
    args = ap.parse_args(argv)
    try:
        reps = audit(extra=[(args.as_env, args.include)] if args.include
                     else None)
    except Exception as exc:
        print("drift_audit: BLIND -- %s: %s" % (type(exc).__name__, exc))
        return 2
    lines = [_summarise(r) for r in reps]
    print("drift_audit: " + "; ".join(lines))
    drifted = [r for r in reps if r.get("drifted")]
    if _setting("hyper_edge.drift_audit", True) is False:
        print("drift_audit: knob hyper_edge.drift_audit=false, advisory only")
        return 0
    if args.strict and drifted:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
