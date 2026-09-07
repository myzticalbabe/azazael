#!/usr/bin/env python
# coding: utf-8
"""
Azazael Worm Execution Matrix — 93-worm runtime execution audit.

Executes every worm in subprocess isolation with 60s timeout, captures
runtime output, and produces a pass/fail matrix.

Category ordering (lightest first):
  utility(1) -> sync(2) -> diagnostic(3) -> all others(4)

Per RULE 0N: "Runtime worm output is the ONLY trusted basis for analysis."
This script IS the RULE 0N enforcement mechanism.

Method discovery happens INSIDE the worker subprocess (not in parent),
so cache-loaded registry class objects don't affect method resolution.
The worker: imports -> instantiates -> discovers method -> calls it -> outputs.

Output:
  - worm_execution_matrix.json — full results with runtime output
  - ASCII summary table printed to stdout

Usage:
  python azazael/_worm_execution_matrix.py
  python azazael/_worm_execution_matrix.py --timeout 30   # custom timeout
  python azazael/_worm_execution_matrix.py --limit 10      # first N worms only
  python azazael/_worm_execution_matrix.py --output-html   # generate HTML report
  python azazael/_worm_execution_matrix.py --cluster       # use ClusterWORMZ path
"""
import os, sys, json, time, subprocess, tempfile, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import groupby

_P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(_P, "azazael", "src")
sys.path.insert(0, SRC_DIR)

# ---- Category weight (lower = execute first) ----
CATEGORY_WEIGHT = {
    "utility": 1,
    "sync": 2,
    "diagnostic": 3,
}
DEFAULT_WEIGHT = 4

# ---- Worker script (runs in subprocess per worm) ----
# Method discovery happens INSIDE the worker, after a fresh import,
# so cache-loaded registry class objects don't affect results.
WORKER_CODE = r"""
import os, sys, json, importlib, time as _time

module_name = sys.argv[1]
class_name = sys.argv[2]

# ---- Method discovery (internal, after fresh import) ----
_METHOD_CANDIDATES = ("execute", "run", "scan", "get_summary", "get_status")

def _discover_method(cls):
    # Check explicit __summary_method__ declaration (BaseWormMixin)
    sm = getattr(cls, "__summary_method__", "")
    if sm and hasattr(cls, sm) and callable(getattr(cls, sm, None)):
        return sm
    # Fallback chain
    for candidate in _METHOD_CANDIDATES:
        if hasattr(cls, candidate) and callable(getattr(cls, candidate, None)):
            return candidate
    return "get_status"

# ---- Execution ----
result = {
    "worm": class_name,
    "module": module_name,
    "resolved_module": module_name,
    "method_called": "?",
    "execute_ok": False,
    "runtime_output": None,
    "error": None,
    "error_type": None,
    "version": "?",
    "duration_ms": 0,
}

t0 = _time.time()

def _resolve_module(raw_module):
    # Resolve short module names to full dotted paths.
    # 28 of 93 worms use short names like 'WORMZ', 'CLOCKZ' stored at
    # CORE/WORMS/<name>.py. 65 use full dotted paths.
    if '.' in raw_module:
        return raw_module  # Already a dotted path
    # Try CORE.WORMS.<name> as the standard location
    return f"CORE.WORMS.{raw_module}"

try:
    resolved = _resolve_module(module_name)
    result["resolved_module"] = resolved
    mod = importlib.import_module(resolved)
    cls = getattr(mod, class_name, None)

    if cls is None:
        result["error"] = "Class not found in module"
        result["error_type"] = "ClassNotFound"
    elif not isinstance(cls, type):
        result["error"] = "Not a class"
        result["error_type"] = "NotAClass"
    else:
        # Discover method (fresh import, no cache artifacts)
        method_name = _discover_method(cls)
        result["method_called"] = method_name

        # Instantiate
        try:
            instance = cls()
        except TypeError as e:
            msg = str(e)[:200]
            if "required positional" in msg or "missing" in msg.lower():
                result["error"] = "Needs constructor args: " + msg
                result["error_type"] = "NeedsArgs"
            else:
                result["error"] = msg
                result["error_type"] = "TypeError"
            result["duration_ms"] = round((_time.time() - t0) * 1000)
            print(json.dumps(result))
            sys.exit(0)
        except Exception as e:
            result["error"] = str(e)[:200]
            result["error_type"] = type(e).__name__
            result["duration_ms"] = round((_time.time() - t0) * 1000)
            print(json.dumps(result))
            sys.exit(0)

        result["version"] = str(getattr(instance, "VERSION", getattr(cls, "VERSION", "?")))

        # Call the discovered method
        method = getattr(instance, method_name, None)
        if method is None or not callable(method):
            result["error"] = "Method not found or not callable: " + method_name
            result["error_type"] = "MethodNotFound"
        else:
            try:
                output = method()
                result["execute_ok"] = True
                # Serialize output safely
                if hasattr(output, "__dict__"):
                    result["runtime_output"] = str(output.__dict__)[:500]
                elif isinstance(output, (dict, list, str, int, float, bool, type(None))):
                    result["runtime_output"] = json.dumps(output, default=str)[:500]
                else:
                    result["runtime_output"] = str(output)[:500]
            except Exception as e:
                result["error"] = str(e)[:200]
                result["error_type"] = type(e).__name__

except ImportError as e:
    result["error"] = str(e)[:200]
    result["error_type"] = "ImportError"
except ModuleNotFoundError as e:
    result["error"] = str(e)[:200]
    result["error_type"] = "ModuleNotFoundError"
except Exception as e:
    result["error"] = str(e)[:200]
    result["error_type"] = type(e).__name__

result["duration_ms"] = round((_time.time() - t0) * 1000)
print(json.dumps(result))
"""


def load_registry():
    """Load worm registry via pickle cache with fallback to full discovery."""
    print("Loading worm registry...", flush=True)
    t0 = time.time()
    try:
        from CORE.worm_registry_cache import load_registry as load_cache
        registry = load_cache(force_rebuild=False)
    except Exception:
        from CORE.worm_registry import discover_worms, WORM_REGISTRY
        discover_worms()
        registry = WORM_REGISTRY

    elapsed = time.time() - t0
    print("Registry loaded: " + str(len(registry)) + " worms in " + str(round(elapsed, 2)) + "s", flush=True)
    return registry


def sort_worms(registry):
    """Sort worms by category weight (lightest first), then by name."""
    def sort_key(item):
        name, info = item
        cat = info.get("category", "utility")
        weight = CATEGORY_WEIGHT.get(cat, DEFAULT_WEIGHT)
        return (weight, name)
    return sorted(registry.items(), key=sort_key)


def generate_html_report(results, summary, output_path):
    """Generate a self-contained sortable/filterable HTML report."""
    categories = summary.get("category_order", [])
    worms_json = json.dumps(results, default=str, indent=2)
    summary_json = json.dumps(summary, default=str, indent=2)

    html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Worm Execution Matrix</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}
h1{color:#58a6ff;margin-bottom:8px}
.summary{display:flex;gap:16px;flex-wrap:wrap;margin:16px 0}
.stat{background:#161b22;border-radius:8px;padding:12px 20px;border:1px solid #30363d}
.stat .label{font-size:12px;color:#8b949e;text-transform:uppercase}
.stat .value{font-size:24px;font-weight:700}
.pass{color:#3fb950}.fail{color:#f85149}.timeout{color:#d29922}.args{color:#58a6ff}
.controls{display:flex;gap:12px;margin:16px 0;flex-wrap:wrap;align-items:center}
.controls select,.controls input{padding:8px 12px;border-radius:6px;border:1px solid #30363d;background:#0d1117;color:#c9d1d9;font-size:14px}
.controls select:focus,.controls input:focus{outline:none;border-color:#58a6ff}
table{width:100%;border-collapse:collapse;margin-top:8px}
th{background:#161b22;padding:10px 14px;text-align:left;font-size:13px;font-weight:600;color:#8b949e;cursor:pointer;user-select:none;position:sticky;top:0;border-bottom:2px solid #30363d}
th:hover{color:#58a6ff}
th .sort-arrow{font-size:10px;margin-left:4px;opacity:.4}
th.sorted .sort-arrow{opacity:1;color:#58a6ff}
td{padding:8px 14px;font-size:13px;border-bottom:1px solid #21262d}
tr:hover{background:#1c2128}
tr.pass-row{border-left:3px solid #3fb950}tr.pass-row td:first-child{padding-left:11px}
tr.fail-row{border-left:3px solid #f85149}tr.fail-row td:first-child{padding-left:11px}
tr.timeout-row{border-left:3px solid #d29922}tr.timeout-row td:first-child{padding-left:11px}
tr.args-row{border-left:3px solid #58a6ff}tr.args-row td:first-child{padding-left:11px}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
.badge-ok{background:#1b3a1b;color:#3fb950}
.badge-fail{background:#3a1b1b;color:#f85149}
.badge-timeout{background:#3a301b;color:#d29922}
.badge-args{background:#1b2b3a;color:#58a6ff}
.error-cell{max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.error-cell:hover{white-space:normal;overflow:visible}
.filter-count{font-size:12px;color:#8b949e}
</style>
</head>
<body>
<h1>Worm Execution Matrix</h1>
<div id="summary"></div>
<div class="controls">
  <label>Filter category:
    <select id="catFilter"><option value="all">All Categories</option></select>
  </label>
  <label>Filter result:
    <select id="resultFilter">
      <option value="all">All Results</option>
        <option value="ok">Pass</option>
        <option value="fail">Fail</option>
        <option value="timeout">Timeout</option>
        <option value="args">Needs Args</option>
    </select>
  </label>
  <label>Search:
    <input id="searchBox" type="text" placeholder="Filter worms...">
  </label>
  <span class="filter-count" id="filterCount"></span>
</div>
<table>
<thead>
<tr>
  <th onclick="sortTable(0)"># <span class="sort-arrow">⇅</span></th>
  <th onclick="sortTable(1)">Worm <span class="sort-arrow">⇅</span></th>
  <th onclick="sortTable(2)">Category <span class="sort-arrow">⇅</span></th>
  <th onclick="sortTable(3)">Result <span class="sort-arrow">⇅</span></th>
  <th onclick="sortTable(4)">Method <span class="sort-arrow">⇅</span></th>
  <th onclick="sortTable(5)">Dur(ms) <span class="sort-arrow">⇅</span></th>
  <th onclick="sortTable(6)">Version <span class="sort-arrow">⇅</span></th>
  <th>Error</th>
</tr>
</thead>
<tbody id="tbody"></tbody>
</table>
<script>
const DATA = ''' + worms_json + r''';
const SUMMARY = ''' + summary_json + r''';
const CAT_ORDER = ''' + json.dumps(categories) + r''';

let sortCol = 0, sortAsc = true;

function rowClass(r) {
  if (r.execute_ok) return 'pass-row';
  if (r.error_type === 'Timeout') return 'timeout-row';
  if (r.error_type === 'NeedsArgs') return 'args-row';
  return 'fail-row';
}

function resultBadge(r) {
  if (r.execute_ok) return '<span class="badge badge-ok">OK</span>';
  if (r.error_type === 'Timeout') return '<span class="badge badge-timeout">TIMEOUT</span>';
  if (r.error_type === 'NeedsArgs') return '<span class="badge badge-args">ARGS</span>';
  return '<span class="badge badge-fail">FAIL</span>';
}

function resultKey(r) {
  if (r.execute_ok) return 'ok';
  if (r.error_type === 'Timeout') return 'timeout';
  if (r.error_type === 'NeedsArgs') return 'args';
  return 'fail';
}

function escape(s) { const d=document.createElement('div');d.textContent=s;return d.innerHTML; }

function renderSummary() {
  const s = SUMMARY;
  document.getElementById('summary').innerHTML =
    '<div class="summary">' +
    '<div class="stat"><div class="label">Total</div><div class="value">' + s.total_worms + '</div></div>' +
    '<div class="stat"><div class="label">Pass</div><div class="value pass">' + s.execute_ok + ' (' + s.pass_rate_pct + '%)</div></div>' +
    '<div class="stat"><div class="label">Failed</div><div class="value fail">' + s.failed + '</div></div>' +
    '<div class="stat"><div class="label">Timeouts</div><div class="value timeout">' + (s.timed_out||0) + '</div></div>' +
    '<div class="stat"><div class="label">Needs Args</div><div class="value args">' + (s.needs_constructor_args||0) + '</div></div>' +
    '<div class="stat"><div class="label">Elapsed</div><div class="value">' + (s.elapsed_seconds||0).toFixed(1) + 's</div></div>' +
    '</div>';

  const sel = document.getElementById('catFilter');
  CAT_ORDER.forEach(c => { const o=document.createElement('option');o.value=c;o.textContent=c;sel.appendChild(o); });
}

function renderTable() {
  const cf = document.getElementById('catFilter').value;
  const rf = document.getElementById('resultFilter').value;
  const q = document.getElementById('searchBox').value.toLowerCase();
  const tbody = document.getElementById('tbody');

  let rows = DATA.map((r,i) => ({...r,_idx:i}));

  if (cf !== 'all') rows = rows.filter(r => r.category === cf);
  if (rf !== 'all') rows = rows.filter(r => resultKey(r) === rf);
  if (q) rows = rows.filter(r => r.worm.toLowerCase().includes(q) || (r.error||'').toLowerCase().includes(q));

  // sort
  const cols = ['_idx','worm','category','_result','method_called','duration_ms','version'];
  const col = cols[sortCol];
  rows.sort((a,b) => {
    let va = col==='_result' ? resultKey(a) : (a[col]??'');
    let vb = col==='_result' ? resultKey(b) : (b[col]??'');
    if (typeof va === 'number' && typeof vb === 'number') return sortAsc ? va-vb : vb-va;
    va=String(va).toLowerCase(); vb=String(vb).toLowerCase();
    return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
  });

  tbody.innerHTML = rows.map((r,i) =>
    '<tr class="' + rowClass(r) + '">' +
    '<td>' + (r._idx+1) + '</td>' +
    '<td><strong>' + escape(r.worm) + '</strong></td>' +
    '<td>' + escape(r.category||'?') + '</td>' +
    '<td>' + resultBadge(r) + '</td>' +
    '<td>' + escape(r.method_called||'?') + '</td>' +
    '<td>' + (r.duration_ms||0) + '</td>' +
    '<td>' + escape(r.version||'?') + '</td>' +
    '<td class="error-cell" title="' + escape(r.error||'') + '">' + escape((r.error||'').substring(0,80)) + '</td>' +
    '</tr>'
  ).join('');

  document.getElementById('filterCount').textContent = 'Showing ' + rows.length + ' of ' + DATA.length + ' worms';
}

function sortTable(col) {
  if (sortCol === col) sortAsc = !sortAsc; else { sortCol = col; sortAsc = true; }
  document.querySelectorAll('th').forEach((th,i) => th.classList.toggle('sorted', i===col));
  renderTable();
}

document.getElementById('catFilter').addEventListener('change', renderTable);
document.getElementById('resultFilter').addEventListener('change', renderTable);
document.getElementById('searchBox').addEventListener('input', renderTable);

renderSummary();
renderTable();
</script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n  HTML report: " + output_path, flush=True)
    return output_path


def _append_history(summary, mode, history_path):
    """Append a summary line to the worm_execution_history.jsonl timeline."""
    from datetime import datetime
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "total": summary["total_worms"],
        "ok": summary["execute_ok"],
        "failed": summary["failed"],
        "pass_rate_pct": summary["pass_rate_pct"],
        "needs_args": summary.get("needs_constructor_args", 0),
        "timed_out": summary.get("timed_out", 0),
        "crashed": summary.get("crashed", 0),
        "import_errors": summary.get("import_errors", 0),
        "not_found": summary.get("not_found", 0),
        "runtime_errors": summary.get("runtime_errors", 0),
        "elapsed_seconds": summary["elapsed_seconds"],
        "timeout_seconds": summary["timeout_seconds"],
    }
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")
    print("  History appended: " + history_path, flush=True)


def _run_discover_only(sorted_worms):
    """Print the method discovery chain for each worm without execution.

    Traces: __summary_method__ -> execute -> run -> scan -> get_summary -> get_status
    Shows which candidates exist on each class and which one would be selected.
    """
    import importlib

    _METHOD_CANDIDATES = ("execute", "run", "scan", "get_summary", "get_status")
    _DISCOVER_KEY_MAP = {"execute": "by_execute", "run": "by_run",
                         "scan": "by_scan", "get_summary": "by_get_summary",
                         "get_status": "by_get_status"}

    print()
    print("=" * 130)
    print("  METHOD DISCOVERY CHAIN — " + str(len(sorted_worms)) + " worms")
    print("  Chain: __summary_method__  ->  execute  ->  run  ->  scan  ->  get_summary  ->  get_status")
    print("=" * 130)
    hdr = (" " + "#".rjust(3) + " " + "Worm".ljust(30) + " " + "Category".ljust(12) +
           " " + "__summary_method__".ljust(22) +
           " e".ljust(3) + " r".ljust(3) + " sc".ljust(3) + " gs".ljust(3) + " st".ljust(3) +
           "  SELECTED")
    print(hdr)
    print("-" * 130)

    # Stats
    stats = {"total": 0, "by_summary": 0, "by_execute": 0, "by_run": 0,
             "by_scan": 0, "by_get_summary": 0, "by_get_status": 0,
             "by_default": 0, "class_not_found": 0, "import_error": 0}

    for i, (worm_name, info) in enumerate(sorted_worms, 1):
        module_name = info.get("module", "?")
        category = info.get("category", "?")
        resolved = module_name if "." in module_name else f"CORE.WORMS.{module_name}"

        # Default: all candidates unknown/missing
        sm_val = ""
        has_chain = {"e": "-", "r": "-", "sc": "-", "gs": "-", "st": "-"}
        selected = "?"
        how = "?"

        try:
            mod = importlib.import_module(resolved)
            cls = getattr(mod, worm_name, None)

            if cls is None:
                selected = "N/A"
                how = "ClassNotFound"
                stats["class_not_found"] += 1
            elif not isinstance(cls, type):
                selected = "N/A"
                how = "NotAClass"
                stats["class_not_found"] += 1
            else:
                # Check __summary_method__ (consolidated: one getattr for both display + check)
                sm = getattr(cls, "__summary_method__", "")
                sm_val = str(sm)[:20]
                if sm and hasattr(cls, sm) and callable(getattr(cls, sm, None)):
                    selected = sm
                    how = "__summary_method__"
                    stats["by_summary"] += 1
                else:
                    # Fallback chain: execute -> run -> scan -> get_summary -> get_status
                    for candidate in _METHOD_CANDIDATES:
                        has_attr = hasattr(cls, candidate) and callable(getattr(cls, candidate, None))
                        if has_attr:
                            selected = candidate
                            how = _DISCOVER_KEY_MAP.get(candidate, "by_default")
                            stats[how] += 1
                            break
                    else:
                        selected = "get_status"
                        how = "by_default (fallback)"
                        stats["by_default"] += 1

                # Mark which candidates exist
                for candidate, abbr in [("execute", "e"), ("run", "r"), ("scan", "sc"),
                                        ("get_summary", "gs"), ("get_status", "st")]:
                    if hasattr(cls, candidate) and callable(getattr(cls, candidate, None)):
                        has_chain[abbr] = "+"
                    else:
                        has_chain[abbr] = "·"

        except (ImportError, ModuleNotFoundError):
            selected = "N/A"
            how = "ImportError"
            stats["import_error"] += 1
        except Exception as e:
            selected = "N/A"
            how = type(e).__name__[:14]
            stats["import_error"] += 1

        stats["total"] += 1

        print(" " + str(i).rjust(3) + " " + worm_name[:30].ljust(30) + " " + category[:12].ljust(12) +
              " " + sm_val[:22].ljust(22) +
              " " + has_chain["e"] + "  " + has_chain["r"] + "  " + has_chain["sc"] +
              "  " + has_chain["gs"] + "  " + has_chain["st"] +
              "  " + selected[:18].ljust(18) + "(" + how + ")")

    print("-" * 130)
    print("  LEGEND:  + = candidate exists & callable    - = does not exist    e=execute r=run sc=scan gs=get_summary st=get_status")
    print()
    print("  Discovery Summary:")
    print("    Total worms:          " + str(stats["total"]))
    print("    Via __summary_method__: " + str(stats["by_summary"]))
    print("    Via execute:          " + str(stats["by_execute"]))
    print("    Via run:              " + str(stats["by_run"]))
    print("    Via scan:             " + str(stats["by_scan"]))
    print("    Via get_summary:      " + str(stats["by_get_summary"]))
    print("    Via get_status:       " + str(stats["by_get_status"]))
    print("    Default fallback:     " + str(stats["by_default"]))
    print("    Class not found:      " + str(stats["class_not_found"]))
    print("    Import error:         " + str(stats["import_error"]))
    print("=" * 130)


def _record_to_memory(results, summary, mode):
    """Record worm execution results via DirectMemory (CD1 spec).

    Per-worm: dm.record('worm_executed', {...}) with worm entry data.
    Summary:  dm.milestone('Worm Execution Matrix Complete', summary).

    CD1 fields (correlation_id, audit_hash, schema_version) are auto-generated
    by DirectMemory.record(). Gracefully skips if DirectMemory is unavailable.
    """
    try:
        from CORE.direct_memory import get_dm
        dm = get_dm()
    except Exception as e:
        print("  [record-memory] DirectMemory unavailable: " + str(e)[:80], flush=True)
        return

    recorded = 0
    skipped = 0
    for worm_entry in results:
        try:
            dm.record("worm_executed", {
                "worm": worm_entry.get("worm", "?"),
                "module": worm_entry.get("module", "?"),
                "resolved_module": worm_entry.get("resolved_module", "?"),
                "category": worm_entry.get("category", "?"),
                "method_called": worm_entry.get("method_called", "?"),
                "execute_ok": worm_entry.get("execute_ok", False),
                "error_type": worm_entry.get("error_type") or "",
                "error": (worm_entry.get("error") or "")[:200],
                "version": str(worm_entry.get("version", "?"))[:20],
                "duration_ms": worm_entry.get("duration_ms", 0),
                "execution_mode": mode,
            }, severity="warning" if not worm_entry.get("execute_ok") else "info",
               tags=["worm", "worm-execution", "matrix", worm_entry.get("category", "unknown")])
            recorded += 1
        except Exception:
            skipped += 1

    # Record summary as milestone
    try:
        dm.milestone("Worm Execution Matrix Complete", {
            "total_worms": summary["total_worms"],
            "execute_ok": summary["execute_ok"],
            "failed": summary["failed"],
            "pass_rate_pct": summary["pass_rate_pct"],
            "needs_args": summary.get("needs_constructor_args", 0),
            "timed_out": summary.get("timed_out", 0),
            "crashed": summary.get("crashed", 0),
            "import_errors": summary.get("import_errors", 0),
            "not_found": summary.get("not_found", 0),
            "runtime_errors": summary.get("runtime_errors", 0),
            "elapsed_seconds": summary["elapsed_seconds"],
            "execution_mode": mode,
        })
    except Exception:
        pass

    print("  [record-memory] " + str(recorded) + " worm_executed events recorded" +
          (" (" + str(skipped) + " skipped)" if skipped else "") +
          " + summary milestone", flush=True)

    # Explicitly close the session (preferred over relying on atexit alone)
    try:
        dm.end({"source": "worm_execution_matrix", "events_recorded": recorded,
                 "events_skipped": skipped})
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Azazael Worm Execution Matrix")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per worm in seconds (default: 60)")
    parser.add_argument("--limit", type=int, default=0, help="Limit to first N worms (default: all)")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only, no ASCII table")
    parser.add_argument("--concurrent", action="store_true", help="Execute worms within each category in parallel")
    parser.add_argument("--cluster", action="store_true", help="Execute via NatureClusterManager instead of subprocess isolation")
    parser.add_argument("--workers", type=int, default=0, help="Max parallel workers (default: auto = min(8, category_size))")
    parser.add_argument("--output-html", action="store_true", help="Generate color-coded sortable HTML report")
    parser.add_argument("--append-history", action="store_true", help="Append summary to worm_execution_history.jsonl")
    parser.add_argument("--discover-only", action="store_true", help="Print method discovery chain without executing worms")
    parser.add_argument("--record-memory", action="store_true", help="Record per-worm events and summary milestone via DirectMemory CD1")
    parser.add_argument("--retry", type=int, default=0, metavar="N", help="Retry failed worms up to N times (cluster mode only)")
    args = parser.parse_args()

    # Load registry
    registry = load_registry()
    if not registry:
        print("FATAL: No worms found in registry.", flush=True)
        sys.exit(1)

    # Sort by category weight (lightest first)
    sorted_worms = sort_worms(registry)
    if args.limit > 0:
        sorted_worms = sorted_worms[:args.limit]

    # ---- DISCOVER-ONLY MODE: trace method discovery chain, no execution ----
    if args.discover_only:
        _run_discover_only(sorted_worms)
        return

    total = len(sorted_worms)
    timeout = args.timeout

    # Write worker script to temp file
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(WORKER_CODE)
    tmp.close()
    worker_path = tmp.name

    # Set up subprocess environment
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    # ---- Single-worm executor (factored out for parallel reuse) ----
    def _run_one_worm(worm_name, info):
        """Execute one worm in subprocess isolation. Returns (worm_name, entry_dict)."""
        module_name = info.get("module", "?")
        category = info.get("category", "?")
        version = info.get("version", "?")

        try:
            proc = subprocess.run(
                [sys.executable, worker_path, module_name, worm_name],
                capture_output=True, text=True, timeout=timeout,
                cwd=SRC_DIR, env=env,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                entry = json.loads(proc.stdout.strip())
            else:
                stderr_text = (proc.stderr or "")[:200]
                entry = {
                    "worm": worm_name, "module": module_name, "category": category,
                    "method_called": "?",
                    "execute_ok": False,
                    "runtime_output": None,
                    "error": "Exit " + str(proc.returncode) + ": " + stderr_text,
                    "error_type": "ExitCode" + str(proc.returncode),
                    "version": version, "duration_ms": 0,
                }
        except subprocess.TimeoutExpired:
            entry = {
                "worm": worm_name, "module": module_name, "category": category,
                "method_called": "?",
                "execute_ok": False,
                "runtime_output": None,
                "error": "Timed out after " + str(timeout) + "s",
                "error_type": "Timeout",
                "version": version, "duration_ms": timeout * 1000,
            }
        except Exception as e:
            entry = {
                "worm": worm_name, "module": module_name, "category": category,
                "method_called": "?",
                "execute_ok": False,
                "runtime_output": None,
                "error": str(e)[:200],
                "error_type": type(e).__name__,
                "version": version, "duration_ms": 0,
            }

        entry.setdefault("category", category)
        return (worm_name, entry)

    # ---- Execute all worms (sequential categories, parallel within category) ----
    results = []
    category_order = []
    seen_categories = set()
    start_all = time.time()

    mode = "cluster" if args.cluster else ("concurrent" if args.concurrent else "sequential")
    if args.concurrent:
        workers = args.workers if args.workers > 0 else None  # None = auto

    ncm = None
    if args.cluster:
        from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        print("NatureClusterManager: " + str(len(ncm.clusters)) + " natures discovered", flush=True)

    print("\nExecuting " + str(total) + " worms (mode=" + mode + ", timeout=" + str(timeout) + "s)...", flush=True)
    print("-" * 70, flush=True)

    # Group by category (preserving category weight order)
    for category, group in groupby(sorted_worms, key=lambda x: x[1].get("category", "?")):
        group_list = list(group)
        cat_size = len(group_list)

        if category not in seen_categories:
            seen_categories.add(category)
            category_order.append(category)

        if args.cluster and ncm is not None:
            # ---- CLUSTER MODE: execute via NatureClusterManager (production path) ----
            parallel = args.concurrent
            print("  [" + category + "] " + str(cat_size) + " worms (cluster, parallel=" + str(parallel) + ")...", flush=True)

            # Build lookup for module/version info
            info_map = {wn: wi for wn, wi in group_list}

            try:
                nature_res = ncm.execute_nature(category, parallel=parallel)
                if nature_res and nature_res.worm_results:
                    for worm_name in info_map:
                        wr = nature_res.worm_results.get(worm_name, {})
                        info = info_map[worm_name]
                        raw_module = info.get("module", "?")
                        resolved = raw_module if "." in raw_module else f"CORE.WORMS.{raw_module}"
                        success = wr.get("success", False)
                        entry = {
                            "worm": worm_name,
                            "module": raw_module,
                            "resolved_module": resolved,
                            "category": category,
                            "method_called": wr.get("method", "?"),
                            "execute_ok": success,
                            "runtime_output": str(wr.get("result", ""))[:500] if success else None,
                            "error": str(wr.get("error", ""))[:200] if not success else None,
                            "error_type": "ClusterFailed" if not success else None,
                            "version": info.get("version", "?"),
                            "duration_ms": wr.get("duration_ms", 0),
                        }
                        results.append(entry)
                else:
                    # Nature had no results — mark all worms as errored
                    for worm_name, info in group_list:
                        raw_mod = info.get("module", "?")
                        entry = {
                            "worm": worm_name,
                            "module": raw_mod,
                            "resolved_module": raw_mod if "." in raw_mod else f"CORE.WORMS.{raw_mod}",
                            "category": category,
                            "method_called": "?",
                            "execute_ok": False,
                            "runtime_output": None,
                            "error": "NatureCluster returned no results",
                            "error_type": "ClusterFailed",
                            "version": info.get("version", "?"),
                            "duration_ms": 0,
                        }
                        results.append(entry)
            except Exception as e:
                # NCM crashed — mark all worms in this category
                for worm_name, info in group_list:
                    raw_mod = info.get("module", "?")
                    entry = {
                        "worm": worm_name,
                        "module": raw_mod,
                        "resolved_module": raw_mod if "." in raw_mod else f"CORE.WORMS.{raw_mod}",
                        "category": category,
                        "method_called": "?",
                        "execute_ok": False,
                        "runtime_output": None,
                        "error": str(e)[:200],
                        "error_type": "ClusterError",
                        "version": info.get("version", "?"),
                        "duration_ms": 0,
                    }
                    results.append(entry)

            print("  [" + category + "] done.", flush=True)

        elif args.concurrent and cat_size > 1:
            # Parallel execution within category
            n_workers = workers if workers else min(8, cat_size)
            print("  [" + category + "] " + str(cat_size) + " worms (parallel, " + str(n_workers) + " workers)...", flush=True)
            with ThreadPoolExecutor(max_workers=n_workers) as pool:
                futures = {pool.submit(_run_one_worm, wn, wi): wn for wn, wi in group_list}
                for future in as_completed(futures):
                    _, entry = future.result()
                    results.append(entry)
            print("  [" + category + "] done.", flush=True)
        else:
            # Sequential execution (single worm or --concurrent not set)
            for worm_name, info in group_list:
                _, entry = _run_one_worm(worm_name, info)
                results.append(entry)
                # Progress indicator
                n_done = len(results)
                pct = n_done * 100 // total
                label = worm_name[:30] + " (" + category[:10] + ")"
                print("\r  [" + str(n_done).rjust(3) + "/" + str(total) + " " + str(pct).rjust(2) + "%] " + label.ljust(45), end="", flush=True)

    if not args.concurrent and not args.cluster:
        print()  # Final newline for progress line

    # Sort results to match category order (stable output regardless of mode)
    if args.concurrent or args.cluster:
        def _result_sort_key(r):
            cat = r.get("category", "")
            return (CATEGORY_WEIGHT.get(cat, DEFAULT_WEIGHT), r.get("worm", ""))
        results.sort(key=_result_sort_key)

    # ---- RETRY: re-run failed worms up to N times (cluster mode only) ----
    if args.retry > 0 and args.cluster and ncm is not None:
        _RETRYABLE_ERRS = {"ClusterFailed", "ClusterError"}  # cluster-mode error types only
        _retried_total = 0
        _passed_on_retry = 0

        for attempt in range(1, args.retry + 1):
            # Collect worms that failed AND are retryable (skip NeedsArgs, ImportError, etc.)
            failed_entries = [
                r for r in results
                if not r["execute_ok"]
                and r.get("error_type") in _RETRYABLE_ERRS
                and r.get("retry_count", 0) < attempt
            ]
            if not failed_entries:
                break

            # Group by category
            failed_by_cat = {}
            for fe in failed_entries:
                cat = fe.get("category", "?")
                failed_by_cat.setdefault(cat, []).append(fe)

            print("\n  [retry " + str(attempt) + "/" + str(args.retry) + "] " +
                  str(len(failed_entries)) + " worms across " + str(len(failed_by_cat)) +
                  " categories...", flush=True)

            for cat, cat_entries in failed_by_cat.items():
                worm_names = [e["worm"] for e in cat_entries]
                print("    [" + cat + "] retrying " + str(len(worm_names)) + "...", flush=True)
                try:
                    nature_res = ncm.execute_nature(cat, parallel=True)
                    if nature_res and nature_res.worm_results:
                        for entry in cat_entries:
                            worm_name = entry["worm"]
                            wr = nature_res.worm_results.get(worm_name, {})
                            success = wr.get("success", False)
                            entry["retry_count"] = attempt
                            if success:
                                entry["execute_ok"] = True
                                entry["passed_on_retry"] = True
                                entry["method_called"] = wr.get("method", entry.get("method_called", "?"))
                                entry["runtime_output"] = str(wr.get("result", ""))[:500]
                                entry["error"] = None
                                entry["error_type"] = None
                                entry["duration_ms"] = wr.get("duration_ms", entry.get("duration_ms", 0))
                                _passed_on_retry += 1
                            else:
                                entry["passed_on_retry"] = False
                                entry["error"] = str(wr.get("error", entry.get("error", "")))[:200]
                            _retried_total += 1
                    else:
                        for entry in cat_entries:
                            entry["retry_count"] = attempt
                            entry["passed_on_retry"] = False
                            _retried_total += 1
                except Exception as e:
                    print("      retry error: " + str(e)[:80], flush=True)
                    for entry in cat_entries:
                        entry["retry_count"] = attempt
                        entry["passed_on_retry"] = False
                        _retried_total += 1

            # Re-sort after retries
            results.sort(key=_result_sort_key)

        # Mark persistent failures (retried at least once, never passed)
        _persistent_fail = sum(
            1 for r in results
            if not r["execute_ok"] and r.get("retry_count", 0) > 0 and not r.get("passed_on_retry")
        )
        print("  [retry] done: " + str(_passed_on_retry) + " passed on retry, " +
              str(_persistent_fail) + " persistent failures", flush=True)
    else:
        _retried_total = 0
        _passed_on_retry = 0
        _persistent_fail = 0

    # Cleanup worker
    try:
        os.unlink(worker_path)
    except OSError:
        pass

    # Final newline after progress
    print()
    elapsed_all = time.time() - start_all

    # ---- Summary with explicit categorization ----
    total_ok = sum(1 for r in results if r["execute_ok"])
    total_fail = total - total_ok

    # Categorize failures explicitly (not subtraction arithmetic)
    needs_args = 0
    timed_out = 0
    crashed = 0
    import_errs = 0
    not_found = 0
    runtime_errs = 0
    unknown = 0

    _IMPORT_ERRS = {"ImportError", "ModuleNotFoundError"}
    _NOT_FOUND_ERRS = {"ClassNotFound", "MethodNotFound", "NotAClass", "NotCallable"}

    for r in results:
        if r["execute_ok"]:
            continue
        et = r.get("error_type") or ""
        if et == "NeedsArgs":
            needs_args += 1
        elif et == "Timeout":
            timed_out += 1
        elif et.startswith("ExitCode"):
            crashed += 1
        elif et in _IMPORT_ERRS:
            import_errs += 1
        elif et in _NOT_FOUND_ERRS:
            not_found += 1
        elif et in ("TypeError", "ClusterFailed", "ClusterError"):
            runtime_errs += 1
        else:
            # Catch-all for any unexpected error types
            runtime_errs += 1

    summary = {
        "total_worms": total,
        "execute_ok": total_ok,
        "failed": total_fail,
        "pass_rate_pct": round(total_ok / max(total, 1) * 100, 1),
        "needs_constructor_args": needs_args,
        "timed_out": timed_out,
        "crashed": crashed,
        "import_errors": import_errs,
        "not_found": not_found,
        "runtime_errors": runtime_errs,
        "elapsed_seconds": round(elapsed_all, 1),
        "timeout_seconds": timeout,
        "category_order": category_order,
    }

    # Retry stats (only meaningful when --retry is used)
    if args.retry > 0:
        summary["retry_count"] = args.retry
        summary["retry_attempts"] = _retried_total
        summary["passed_on_retry"] = _passed_on_retry
        summary["persistent_fail"] = _persistent_fail
    else:
        summary["retry_count"] = 0
        summary["retry_attempts"] = 0
        summary["passed_on_retry"] = 0
        summary["persistent_fail"] = 0

    # DirectMemory CD1 recording (per-worm events + summary milestone)
    if args.record_memory:
        _record_to_memory(results, summary, mode)

    # JSON output
    json_path = os.path.join(_P, "azazael", "worm_execution_matrix.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "worms": results}, f, indent=2, default=str)

    # HTML report
    if args.output_html:
        html_path = os.path.join(_P, "azazael", "worm_execution_matrix.html")
        generate_html_report(results, summary, html_path)

    # Append to history JSONL
    if args.append_history:
        history_path = os.path.join(_P, "azazael", "worm_execution_history.jsonl")
        _append_history(summary, mode, history_path)

    if args.json_only:
        print(json.dumps({"summary": summary}, indent=2, default=str))
        return

    # ---- ASCII Summary Table ----
    print()
    print("=" * 110)
    print("  AZAZAEL WORM EXECUTION MATRIX — " + str(total) + " worms  |  " +
          str(round(elapsed_all, 1)) + "s  |  timeout=" + str(timeout) + "s")
    print("=" * 110)
    hdr = (" " + "#".rjust(3) + " " + "Worm".ljust(32) + " " + "Category".ljust(14) +
           " " + "Result".rjust(8) + " " + "Method".ljust(14) +
           " " + "Dur(ms)".rjust(8) + " " + "Version".ljust(8) + "  Error")
    print(hdr)
    print("-" * 110)

    for i, r in enumerate(results, 1):
        if r["execute_ok"]:
            if r.get("passed_on_retry"):
                result_str = "RETRY_OK"
            else:
                result_str = "OK"
        elif r.get("error_type") == "NeedsArgs":
            result_str = "ARGS"
        elif r.get("error_type") == "Timeout":
            result_str = "TIMEOUT"
        elif (r.get("error_type") or "").startswith("ExitCode"):
            result_str = "CRASH"
        else:
            result_str = "FAIL"

        name = str(r["worm"])[:32]
        cat = str(r.get("category", "?"))[:14]
        method = str(r.get("method_called", "?"))[:14]
        dur = str(r.get("duration_ms", 0))[:8]
        ver = str(r.get("version", "?"))[:8]
        err = (r.get("error") or "")[:28]

        flag = ""
        if not r["execute_ok"]:
            flag = " !! " + (r.get("error_type") or "FAIL")

        print(" " + str(i).rjust(3) + " " + name.ljust(32) + " " + cat.ljust(14) +
              " " + result_str.rjust(8) + " " + method.ljust(14) +
              " " + dur.rjust(8) + " " + ver.ljust(8) + " " + err[:26] + flag)

    print("-" * 110)
    print("  PASS: " + str(total_ok) + "/" + str(total) + " (" + str(summary["pass_rate_pct"]) + "%)" +
          ("  |  RETRY_OK: " + str(summary.get("passed_on_retry", 0)) if args.retry > 0 else "") +
          ("  |  PERSISTENT: " + str(summary.get("persistent_fail", 0)) if args.retry > 0 else ""))
    print("  NEEDS_ARGS: " + str(needs_args) + "  |  TIMEOUT: " + str(timed_out) +
          "  |  CRASHED: " + str(crashed))
    print("  IMPORT_ERR: " + str(import_errs) + "  |  NOT_FOUND: " + str(not_found) +
          "  |  RUNTIME_ERR: " + str(runtime_errs))
    print("  JSON: " + json_path)
    print("=" * 110)

    # Category breakdown
    print()
    print("  Category Breakdown:")
    cat_counts = {}
    for r in results:
        cat = r.get("category", "?")
        if cat not in cat_counts:
            cat_counts[cat] = {"total": 0, "ok": 0}
        cat_counts[cat]["total"] += 1
        if r["execute_ok"]:
            cat_counts[cat]["ok"] += 1

    for cat in category_order:
        c = cat_counts.get(cat, {"total": 0, "ok": 0})
        pct = round(c["ok"] / max(c["total"], 1) * 100, 1)
        print("    " + cat.ljust(18) + str(c["ok"]).rjust(2) + "/" +
              str(c["total"]).ljust(4) + " (" + str(pct) + "%)")


if __name__ == "__main__":
    main()
