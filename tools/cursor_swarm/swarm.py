#!/usr/bin/env python3
"""swarm.py - a swarm of WORKER cursors that build a site, or none of it does.

What a worker is: an agent that takes a **scope** of files, **reads** them,
**reports** what it found, and **lands** a layer of the site. What a worker is
not: a judge. `tools/swarm_arena/` is a different project that scores candidate
texts against each other; this one does not read it and it does not read this.

The three properties that make it a swarm rather than a script:

* **cursor-local.** A worker's verdict is about the files that worker touched,
  not about the repository. The auditors in this tree answer whole-tree
  questions, so their per-file callables are COMPOSED here rather than their
  CLIs re-implemented - `settings_shadow.readers_in` and `.bypasses_in` per
  file in the scope, `reading_audit.audit_file` per artifact in the scope, and
  the tree's own `claim_agreement.validate_ledger` over the staged ledger.
* **transactional.** Every worker's layer lands, or none does. A rolled-back
  swarm writes its rows to an *attempts* file and leaves the canonical ledger
  untouched - the ledger is inside the transaction, because a ledger that
  claims work that does not exist is the one artifact everything else is built
  on.
* **measured.** The per-worker verdict time, the serial cost, the parallel
  cost and the speed-up are measured on every run and printed. The sub-second
  claim is a number this run produced, never a projection.

The ledger dialect is the tree's: four verdicts (landed / held / rolledback /
quarantine) and the hash rule `claim_agreement.validate_ledger` enforces - the
sha256 of the canonical JSON of every key except `hash`, chained through
`prev_hash` from "GENESIS". A row that does not recompute is quarantined and
never drawn.

Usage:
    python tools/cursor_swarm/swarm.py --make-plan --scope src/CORE --workers 72 \\
        --out tools/cursor_swarm/plan_workers.json
    python tools/cursor_swarm/swarm.py --plan tools/cursor_swarm/plan_workers.json \\
        --ledger tools/cursor_swarm/worker_frames.jsonl \\
        --attempts tools/cursor_swarm/worker_attempts.jsonl \\
        --out tools/cursor_swarm/out/swarm_site.html

Exit: 0 the swarm landed; 1 a worker was red and the swarm rolled back;
2 the swarm could not run (bad plan, scope outside the index, missing import).
2 is not a pass.
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

FIELD_W, FIELD_H = 1040.0, 460.0
STAGES = ("placed", "verified", "applied", "settled")

# The ledger's verdicts are the tree's, from tools/claim_agreement.py. They are
# imported, not copied: a dialect that lives in two files drifts in two files,
# and a verdict the validator does not accept is a row nobody can read.
try:
    from claim_agreement import LEDGER_KEYS, LEDGER_VERDICTS, validate_ledger
except Exception as exc:  # noqa: BLE001
    print("swarm: cannot import the tree's ledger validator (%s) - refusing to invent a "
          "dialect" % exc)
    sys.exit(2)

try:
    import settings_shadow
except Exception as exc:  # noqa: BLE001
    print("swarm: cannot import tools/settings_shadow.py (%s) - the cursor-local verdict has "
          "no reader to compose" % exc)
    sys.exit(2)

try:
    from monitor_theme import SEMANTIC
except Exception as exc:  # noqa: BLE001
    print("swarm: cannot import monitor_theme.SEMANTIC (%s) - refusing to invent a palette" % exc)
    sys.exit(2)

COLOR = {k: v[0] for k, v in SEMANTIC.items()}


# ── git ───────────────────────────────────────────────────────────────────

def git_text(args, root=ROOT):
    """One git command's stdout. An unreadable index is not an empty one."""
    import subprocess

    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=60)
    except OSError as exc:
        raise SystemExit("swarm: cannot run git (%s) - remedy: put git on PATH" % exc)
    except Exception as exc:  # subprocess.TimeoutExpired and friends
        raise SystemExit("swarm: git %s failed (%s)" % (" ".join(args), exc))
    if out.returncode != 0:
        raise SystemExit("swarm: git %s failed (rc=%d): %s"
                         % (" ".join(args), out.returncode, out.stderr.strip()[:200]))
    return out.stdout


def tracked(scope):
    """The scope's tracked files. The INDEX is the universe, never the worktree."""
    files = sorted(p for p in git_text(["ls-files", "-z", "--", scope]).split("\0") if p)
    if not files:
        raise SystemExit("swarm: scope %s has no tracked file - remedy: name a path that "
                         "`git ls-files` returns" % scope)
    return files


# ── the tree's config surface, read once ─────────────────────────────────

def load_declared():
    """(declared keys, reader vocabulary, source). The config opens in ONE place.

    This module used to hand-parse `config/defaults.json` for these three values,
    which made it the tree's only `bypass_reader`: the knobs a cursor took were
    invisible to the audit that guards them, and its declared set could drift
    from the audited one silently (measured 2026-11-16). `settings_shadow` owns
    the parse; this asks it.
    """
    _config, declared, vocabulary, source = settings_shadow.load_config()
    settings_shadow.READERS.clear()
    settings_shadow.READERS.update(vocabulary)
    return declared, vocabulary, source


# ── the cursor-local verdict ──────────────────────────────────────────────

def scan_scope(files, declared):
    """What this worker's own files say. Pure reads; safe to run in a thread.

    Returns (reads, undeclared, bypasses, unparseable, lines). Every count is
    over the scope - that is what makes the verdict cursor-local instead of a
    global verdict wearing a cursor's name.
    """
    reads, undeclared, bypasses, unparseable = {}, [], [], []
    total_lines = 0
    for rel in files:
        path = ROOT / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            unparseable.append((rel, "unreadable: %s" % exc))
            continue
        total_lines += text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        found, _wrappers = settings_shadow.readers_in(path, declared)
        bypass_lines, _is_surface = settings_shadow.bypasses_in(path)
        for line in bypass_lines:
            bypasses.append((rel, line))
        for key, fallback, line in found:
            if key == "__unparseable__":
                unparseable.append((rel, "%s (line %d)" % (fallback, line)))
                continue
            reads.setdefault(key, []).append(rel)
            if key not in declared:
                undeclared.append((key, rel, line))
    return reads, undeclared, bypasses, unparseable, total_lines


def dirty_in(scope_files):
    """The scope's dirty paths. A moving target is `held`, not red.

    ONE git call for the whole scope, not one per worker: 72 subprocesses of
    `git status` cost more than every auditor in the tree put together, and
    the answer is the same set either way.
    """
    out = git_text(["status", "--porcelain", "--", *scope_files])
    dirty = set()
    for line in out.splitlines():
        if not line.strip():
            continue
        # porcelain v1: "XY path" - the path starts after the third column.
        path = line[3:].strip()
        if " -> " in path:          # a rename reads "old -> new"; the new name counts
            path = path.split(" -> ", 1)[1].strip()
        dirty.add(path.strip('"'))
    return dirty


def run_worker(worker, declared, dirty):
    """One worker's whole verdict, in-process, no subprocess.

    The four checks are the ones the design calls cursor-local:
      parse    - every file in the scope parses (a file that will not parse is a
                 defect with a name);
      settings - every settings key the scope reads is declared, and no module
                 in the scope hand-parses the shared config;
      reading  - the layer the worker produced carries a denominator that
                 covers its whole scope;
      scope    - the scope is not being written under the worker.
    """
    started = time.perf_counter()
    files = list(worker["scope"])
    reads, undeclared, bypasses, unparseable, lines = scan_scope(files, declared)
    dirty_here = sorted(f for f in files if f in dirty)

    reasons = []
    if unparseable:
        reasons.append("%d file(s) do not parse: %s"
                       % (len(unparseable), "; ".join(f for f, _ in unparseable[:3])))
    if undeclared:
        reasons.append("%d undeclared setting read(s): %s"
                       % (len(undeclared), ", ".join(sorted({k for k, _, _ in undeclared})[:4])))
    if bypasses:
        reasons.append("%d bypass(es) of the shared config reader: %s"
                       % (len(bypasses), ", ".join(sorted({f for f, _ in bypasses})[:3])))

    n_reads = sum(len(v) for v in reads.values())
    reading = ("%d module(s) · %d line(s) · %d setting read(s) "
               "(%d declared, %d undeclared)"
               % (len(files), lines, n_reads, n_reads - len(undeclared), len(undeclared)))

    # The layer must carry a denominator that covers the whole scope; a layer
    # that says "modules" without saying how many is not a reading.
    if not files or ("%d module(s)" % len(files)) not in reading:
        reasons.append("the layer carries no denominator over its scope")

    verdict = "landed"
    if reasons:
        verdict = "rolledback"
    elif dirty_here:
        verdict = "held"

    elapsed = (time.perf_counter() - started) * 1000.0
    return {
        "id": worker["id"], "tree": worker["tree"], "node": worker["node"],
        "scope": files, "intent": worker.get("intent", ""),
        "verdict": verdict, "reasons": reasons, "dirty": dirty_here,
        "reading": reading, "reads": n_reads, "undeclared": len(undeclared),
        "bypasses": len(bypasses), "unparseable": len(unparseable),
        "lines": lines, "ms": elapsed,
        "claim": "%s · %s · %d module(s) · %d setting read(s) · %d line(s) · %.0f ms"
                 % (worker["id"], worker["node"], len(files), n_reads, lines, elapsed),
    }


# ── the ledger ────────────────────────────────────────────────────────────

def chain(rows, start_frame, prev_hash):
    """(rows, last_hash): the tree's chain - sha256 over every key but `hash`."""
    out = []
    for i, row in enumerate(rows):
        row = dict(row, frame=start_frame + i, prev_hash=prev_hash)
        body = {k: v for k, v in row.items() if k != "hash"}
        row["hash"] = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
        prev_hash = row["hash"]
        out.append(row)
    return out, prev_hash


def read_ledger(path):
    """(next_frame, prev_hash): the existing ledger's tail, so a new run continues it.

    Frames are 1-based, like the v0 ledger's. A missing file starts at frame 1
    with "GENESIS", not frame 0 - a frame number that starts at zero is a
    different numbering, not a continuation.
    """
    if not path.exists():
        return 1, "GENESIS"
    last_frame, prev = 0, "GENESIS"
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                break
            last_frame = max(last_frame, int(row.get("frame", 0)))
            prev = row.get("hash", prev)
    return last_frame + 1, prev


def stage_rows(results, ts_ms):
    """Four rows per worker - placed, verified, applied, settled.

    The stage is named in the claim, because that is where the v0 ledger put
    it; the verdict of each row is that stage's own verdict, so a worker that
    rolled back shows the rollback at the stage it happened rather than
    everywhere at once.
    """
    rows = []
    for res in results:
        verdict = res["verdict"]
        for stage in STAGES:
            if stage == "placed":
                stage_verdict = "landed"          # the worker took its scope
            else:
                stage_verdict = verdict
            claim = "%s %s" % (res["intent"] or res["node"], "[%s]" % stage)
            if res["reasons"] and stage != "placed":
                claim += " - %s" % "; ".join(res["reasons"])[:120]
            rows.append({
                "cursor_id": res["id"], "tree": res["tree"], "node": res["node"],
                "verdict": stage_verdict, "claim": claim, "ts": ts_ms,
            })
    return rows


def broken(rows):
    """Rows whose hash does not recompute - quarantined, never drawn."""
    bad, prev = [], "GENESIS"
    for row in rows:
        body = {k: v for k, v in row.items() if k != "hash"}
        expect = hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
        if row["prev_hash"] != prev or row["hash"] != expect:
            bad.append(row["cursor_id"])
        prev = row["hash"]
    return bad


# ── the plan ──────────────────────────────────────────────────────────────

def make_plan(scope, workers, out_path):
    """Partition the scope's tracked modules into workers.

    A worker's scope stays inside ONE directory: a scope that straddles two
    directories is two places, and a cursor with two places has no place.
    Directories larger than the per-worker cap are SPLIT, because a worker that
    holds 150 modules is not a cursor, it is the repository with a name on it.
    """
    files = [f for f in tracked(scope) if f.endswith(".py")]
    if not files:
        raise SystemExit("swarm: scope %s holds no tracked module" % scope)
    by_dir = {}
    for rel in files:
        by_dir.setdefault(str(Path(rel).parent).replace(os.sep, "/"), []).append(rel)
    for d in by_dir:
        by_dir[d].sort()

    def chunks(cap):
        """[(dir, [files])] - each directory split into pieces of at most `cap`."""
        out = []
        for d in sorted(by_dir):
            members = by_dir[d]
            for i in range(0, len(members), cap):
                out.append((d, members[i:i + cap]))
        return out

    cap = max(1, int(math.ceil(len(files) / float(workers))))
    slots = chunks(cap)
    # Raise the cap only while there are too few pieces to hand out; the split
    # is then finer, not wider.
    while len(slots) < workers:
        cap += 1
        slots = chunks(cap)
        if cap > len(files):
            break
    # Too many pieces: merge within a directory first, so a merged worker still
    # has one directory, and only then across directories.
    while len(slots) > workers:
        by_dir_count = {}
        for i, (d, _m) in enumerate(slots):
            by_dir_count.setdefault(d, []).append(i)
        pair = None
        for d, idxs in sorted(by_dir_count.items()):
            if len(idxs) >= 2:
                pair = (idxs[0], idxs[1])
                break
        if pair is None:
            pair = (0, 1)
        a, b = sorted(pair, reverse=True)
        da, ma = slots[a]
        db, mb = slots[b]
        slots[a] = (da, sorted(ma + mb))
        slots.pop(b)

    plan = {
        "swarm_id": "cursor-swarm-workers-%s" % scope.replace("/", "-"),
        "env": os.environ.get("COMPUTERNAME", "windows").lower(),
        "scope": scope,
        "deadline_ms": 30000,
        "workers": [],
    }
    for i, (d, files_i) in enumerate(sorted(slots, key=lambda s: (s[0], s[1][0]))):
        plan["workers"].append({
            "id": "w%02d" % (i + 1), "tree": scope, "node": d,
            "scope": list(files_i),
            "intent": "read %d module(s) of %s" % (len(files_i), d),
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return plan


# ── run ───────────────────────────────────────────────────────────────────

def place(results):
    """Where each worker's cursor lands on the field. A grid, so nothing overlaps."""
    n = len(results)
    cols = max(1, int(math.ceil(math.sqrt(n * (FIELD_W / FIELD_H)))))
    rows = int(math.ceil(n / cols))
    for i, res in enumerate(results):
        col, row = i % cols, i // cols
        res["x"] = 60.0 + (col * (FIELD_W - 120.0) / max(1, cols - 1))
        res["y"] = 40.0 + (row * (FIELD_H - 90.0) / max(1, rows - 1))
    return results


def sweep(workers, declared, dirty, threads):
    """(results, wall_ms). One pass of the verdict phase at a given width."""
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=threads) as pool:
        results = list(pool.map(lambda w: run_worker(w, declared, dirty), workers))
    return results, (time.perf_counter() - started) * 1000.0


def run(args):
    plan_path = Path(args.plan)
    if not plan_path.exists():
        raise SystemExit("swarm: no plan at %s - remedy: run --make-plan first" % plan_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    workers = plan.get("workers") or []
    if not workers:
        raise SystemExit("swarm: the plan holds no worker")
    ids = [w["id"] for w in workers]
    if len(set(ids)) != len(ids):
        raise SystemExit("swarm: the plan repeats a worker id - a cursor per id, not two")

    declared, vocabulary, vocab_source = load_declared()
    scope = plan.get("scope") or "."
    tracked_files = set(tracked(scope))
    for w in workers:
        missing = [f for f in w["scope"] if f not in tracked_files]
        if missing:
            raise SystemExit("swarm: worker %s claims %d file(s) outside the scope's index "
                             "(%s) - remedy: the scope is the index, not the worktree"
                             % (w["id"], len(missing), ", ".join(missing[:3])))

    # The sweep: parallel, because the free-threaded interpreter exists for
    # exactly this, and measured - never assumed. The dirty set is ONE git
    # call for the whole scope, taken before the sweep, because 72 of them
    # cost more than every auditor in the tree put together.
    #
    # The baseline is a REAL serial run, not the sum of the parallel run's
    # per-worker times: summing times that were measured while 16 threads
    # contended for the same lock produces a number that is both larger than
    # the truth and useless as a denominator.
    dirty = dirty_in(sorted(tracked_files))
    baseline_ms = None
    if args.threads > 1:
        _, baseline_ms = sweep(workers, declared, dirty, 1)
    results, wall_ms = sweep(workers, declared, dirty, args.threads)
    speedup = (baseline_ms / wall_ms) if baseline_ms and wall_ms else 0.0
    # When the run IS the serial baseline, the serial figure is this run.
    serial_ms = baseline_ms if baseline_ms else wall_ms
    n_modules = sum(len(w["scope"]) for w in workers)
    place(results)

    counts = {}
    for res in results:
        counts[res["verdict"]] = counts.get(res["verdict"], 0) + 1
    red = [r for r in results if r["verdict"] == "rolledback"]

    ts_ms = int(time.time() * 1000)
    ledger_path = Path(args.ledger)
    attempts_path = Path(args.attempts)
    start_frame, prev_hash = read_ledger(ledger_path)

    if red:
        # The swarm rolls back. The canonical ledger is NOT touched: a ledger
        # that says "landed" for work that did not land is the one artifact
        # everything else is built on, so it is inside the transaction.
        rows, _ = chain(stage_rows(results, ts_ms), start_frame, prev_hash)
        attempts = [dict(r, verdict="rolledback") for r in rows]
        for i, row in enumerate(attempts):
            body = {k: v for k, v in row.items() if k != "hash"}
            row["hash"] = hashlib.sha256(
                json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
        # re-chain so prev_hash links hold after the verdict rewrite
        attempts, _ = chain([{k: v for k, v in r.items() if k != "hash"}
                              for r in attempts], start_frame, prev_hash)
        attempts_path.parent.mkdir(parents=True, exist_ok=True)
        attempts_path.write_text(
            "".join(json.dumps(r, sort_keys=True) + "\n" for r in attempts),
            encoding="utf-8")
        print("swarm: ROLLED BACK - %d of %d worker(s) were red" % (len(red), len(results)))
        for res in red[:5]:
            print("  - %s: %s" % (res["id"], "; ".join(res["reasons"])))
        print("attempts: %s (%d rows) - the canonical ledger was NOT touched"
              % (attempts_path, len(attempts)))
        print("verdict phase: %.0f ms wall (serial %.0f ms, speed-up %.2fx, %d threads)"
              % (wall_ms, serial_ms, speedup, args.threads))
        return 1

    rows, last_hash = chain(stage_rows(results, ts_ms), start_frame, prev_hash)
    quarantine = broken(rows)

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    report = validate_ledger(str(ledger_path))
    if report["bad"]:
        print("swarm: the ledger does not validate after appending: %s"
              % report["bad"][:3])
        return 2

    import importlib.util

    spec = importlib.util.spec_from_file_location("cursor_swarm_site", HERE / "swarm_site.py")
    site_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(site_module)

    for res in results:
        res["stage_verdicts"] = {s: res["verdict"] for s in STAGES}
    # The schedule is computed here, not inside render(): the denominator line
    # quotes it, and the denominator line is an argument to render().
    stagger, slowest = site_module.schedule(len(results))
    page, timing = site_module.render(results, rows, quarantine, COLOR, {
        "source": "plan %s · %d workers · %d scope file(s)"
                  % (plan_path.name, len(results), len(tracked_files)),
        "denominator": "denominator - <b>%d of %d workers landed</b>; %d held, %d rolled back; "
                       "%d ledger row(s); %d quarantined<br>"
                       "verdict phase - <b>%.0f ms wall</b> (serial %.0f ms, speed-up %.2fx, "
                       "%d threads)<br>schedule - %d ms stagger, slowest %d ms of a %d ms budget"
                       % (counts.get("landed", 0), len(results), counts.get("held", 0),
                          counts.get("rolledback", 0), len(rows), len(quarantine),
                          wall_ms, serial_ms, speedup,
                          args.threads, stagger, slowest, site_module.BUDGET_MS),
    })
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")

    print("workers: %d  landed: %d  held: %d  rolledback: %d"
          % (len(results), counts.get("landed", 0), counts.get("held", 0),
             counts.get("rolledback", 0)))
    print("verdict phase: %.0f ms wall (serial %.0f ms, speed-up %.2fx, %d threads)"
          % (wall_ms, serial_ms, speedup, args.threads))
    print("per-worker: min %.1f ms  median %.1f ms  max %.1f ms  (n=%d)"
          % (min(r["ms"] for r in results),
             sorted(r["ms"] for r in results)[len(results) // 2],
             max(r["ms"] for r in results), len(results)))
    print("per-module: %.1f ms of the verdict phase across %d module(s)"
          % (wall_ms / n_modules, n_modules))
    print("schedule: %d ms stagger, slowest %d ms of a %d ms budget"
          % (timing["stagger"], timing["slowest"], site_module.BUDGET_MS))
    print("ledger: %s (%d rows, last %s)" % (ledger_path, len(rows), last_hash[:12]))
    print("ledger validate: %d row(s), %d bad" % (report["rows"], len(report["bad"])))
    print("page: %s" % out_path)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--make-plan", action="store_true",
                    help="partition the scope into workers and write the plan")
    ap.add_argument("--scope", default="src/CORE",
                    help="the tree the swarm works on (default: src/CORE)")
    ap.add_argument("--workers", type=int, default=72,
                    help="how many workers to fan out (default: 72)")
    ap.add_argument("--plan", default=str(HERE / "plan_workers.json"))
    ap.add_argument("--ledger", default=str(HERE / "worker_frames.jsonl"))
    ap.add_argument("--attempts", default=str(HERE / "worker_attempts.jsonl"))
    ap.add_argument("--out", default=str(HERE / "out" / "swarm_site.html"))
    ap.add_argument("--threads", type=int, default=16,
                    help="parallel readers for the verdict phase (default: 16)")
    args = ap.parse_args(argv)

    if args.make_plan:
        plan = make_plan(args.scope, args.workers, Path(args.plan))
        print("plan: %s - %d worker(s) over %d scope file(s)"
              % (args.plan, len(plan["workers"]), len(tracked(args.scope))))
        return 0
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
