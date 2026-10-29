#!/usr/bin/env python3
"""Polyglot router + golden self-test (arena-64n shard_node shape).

`run_shard(lang)` executes the golden snippet for one language through the
INTERPRETERS dispatcher and returns a JSON-serializable result (no weights,
no handles across the boundary). `self_test()` cold-recomputes every
available toolchain and asserts stdout agreement on the golden token.
A missing toolchain is a clean skip, never a failure.

Golden contract: the snippet prints exactly AZAZAEL-GOLDEN-OK on stdout
and exits 0. stdout agreement across languages IS the test.
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

from INTERPRETERS import run_code, supported_languages
from SHARDS.registry import LANG_ORDER, SHARDS, route_lang

GOLDEN_TOKEN = "AZAZAEL-GOLDEN-OK"

GOLDEN_SNIPPETS: dict = {
    "python": 'print("AZAZAEL-GOLDEN-OK")',
    "go": ('package main\nimport "fmt"\n'
            'func main(){fmt.Println("AZAZAEL-GOLDEN-OK")}'),
    "rust": 'fn main(){println!("AZAZAEL-GOLDEN-OK");}',
    "javascript": 'console.log("AZAZAEL-GOLDEN-OK");',
    "powershell": 'Write-Output "AZAZAEL-GOLDEN-OK"',
    "bash": "echo AZAZAEL-GOLDEN-OK",
}


def supported_shard_langs() -> list:
    """Languages with golden snippets (subset actually runs: toolchain-gated)."""
    return [lang for lang in LANG_ORDER if lang in GOLDEN_SNIPPETS]


def run_shard(lang: str) -> dict:
    """Run one language golden; JSON-serializable result, no handles."""
    key = (lang or "").lower()
    if key not in GOLDEN_SNIPPETS:
        return {"lang": key, "status": "unknown-language", "ok": False}
    result = run_code(key, GOLDEN_SNIPPETS[key])
    if not result.success and "not found" in (result.stderr or ""):
        detail = (result.stderr or "").strip().split("\n")[0][:120]
        return {"lang": key, "status": "skipped", "ok": True,
                "detail": f"toolchain missing: {detail}"}
    token_ok = GOLDEN_TOKEN in (result.stdout or "")
    ok = bool(result.success and token_ok)
    return {"lang": key, "status": "pass" if ok else "fail", "ok": ok,
            "success": result.success, "token": token_ok,
            "stdout": (result.stdout or "").strip()[:200],
            "stderr": (result.stderr or "").strip()[:300] if not ok else "",
            "duration_ms": round(result.duration_ms, 1)}


def self_test() -> bool:
    """Cold recompute across every golden language; True when all pass/skip."""
    results = [run_shard(lang) for lang in supported_shard_langs()]
    ran = [r for r in results if r["status"] in ("pass", "fail")]
    ok = all(r["ok"] for r in results)
    # Agreement: every language that ran emitted the same token.
    tokens = {r["stdout"] for r in ran}
    agree = len(tokens) <= 1
    report = {"self_test": "PASS" if (ok and agree) else "FAIL",
              "dispatcher_langs": sorted(supported_languages()),
              "ran": len(ran), "skipped": len(results) - len(ran),
              "agree": agree, "results": results}
    print(json.dumps(report, indent=1))
    return bool(ok and agree)


def sweep(n: int = 10) -> dict:
    """Measure every golden language n times; write sweep.json; print table.

    Cold recompute per iteration (no caching — a gate that passes without
    re-running proves nothing). Compiled languages pay full compile cost
    every iteration; the table reports that honestly."""
    medians: dict = {}
    samples: dict = {}
    rows = []
    for lang in supported_shard_langs():
        durations = []
        ok_all = True
        for _ in range(max(1, n)):
            res = run_shard(lang)
            if res["status"] == "skipped":
                ok_all = False
                break
            ok_all = ok_all and res["ok"]
            durations.append(res["duration_ms"])
        if not durations:
            rows.append({"lang": lang, "status": "skipped"})
            continue
        medians[lang] = round(statistics.median(durations), 1)
        samples[lang] = [round(d, 1) for d in durations]
        rows.append({"lang": lang, "status": "pass" if ok_all else "fail",
                     "n": len(durations), "median_ms": medians[lang],
                     "min_ms": round(min(durations), 1),
                     "max_ms": round(max(durations), 1)})
    report = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "n": n, "medians_ms": medians, "rows": rows}
    Path(__file__).with_name("sweep.json").write_text(
        json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"{'lang':<12}{'n':>4}  median      min/max  status")
    for row in sorted(rows, key=lambda r: r.get("median_ms", float("inf"))):
        if row["status"] == "skipped":
            print(f"{row['lang']:<12}   -  skipped (toolchain missing)")
        else:
            print(f"{row['lang']:<12}{row['n']:>4}  "
                  f"median={row['median_ms']:.1f}ms "
                  f"min={row['min_ms']:.1f} max={row['max_ms']:.1f} "
                  f"{row['status']}")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Azazael polyglot shard router")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--lang", default=None, choices=sorted(GOLDEN_SNIPPETS))
    ap.add_argument("--budget", default="balanced",
                    choices=["fast", "balanced", "peak"])
    ap.add_argument("--shard", default=None)
    args = ap.parse_args(argv)

    if args.list:
        print(json.dumps(
            {"langs": supported_shard_langs(),
             "shards": {k: {"langs": v["langs"], "canonical": v["canonical"],
                             "notes": v["notes"]} for k, v in SHARDS.items()}},
            indent=1))
        return 0
    if args.self_test:
        return 0 if self_test() else 1
    if args.sweep:
        sweep(args.n)
        return 0
    if args.shard:
        print(route_lang(args.shard, args.budget))
        return 0
    if args.run:
        if not args.lang:
            print(json.dumps(run_shard("python"), indent=1))
            return 0
        res = run_shard(args.lang)
        print(json.dumps(res, indent=1))
        return 0 if res["ok"] else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
