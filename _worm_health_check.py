#!/usr/bin/env python
# coding: utf-8
"""
Azazael Worm Health Matrix - Full 93-worm health audit.

Checks: file exists, import ok, instantiate ok (subprocess isolation).
Uses pickle cache for fast loading. Outputs JSON + summary table.
"""
import os, sys, json, time, subprocess, tempfile

_P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_P, "azazael", "src"))

# Load registry via cache
print("Loading worm registry via pickle cache...", flush=True)
start = time.time()
try:
    from CORE.worm_registry_cache import load_registry
    registry = load_registry(force_rebuild=False)
except Exception as e:
    print("Cache load failed, falling back to full discovery...", flush=True)
    from CORE.worm_registry import discover_worms, WORM_REGISTRY
    discover_worms()
    registry = WORM_REGISTRY

elapsed = time.time() - start
print("Registry loaded: " + str(len(registry)) + " worms in " + str(round(elapsed, 2)) + "s", flush=True)

if not registry:
    print("FATAL: No worms found in registry. Aborting.")
    sys.exit(1)

# Write worker script to temp file (multi-line, proper syntax)
worker_code = """\
import os, sys, json, importlib

module_name = sys.argv[1]
class_name = sys.argv[2]
source_file = sys.argv[3]

# The registry stores bare module names for worms whose files were registered
# via @register_worm while scanning a package directory (e.g. src/CORE/WORMS/),
# but bare names only import if the file's own directory is on sys.path. The
# worker runs with azazael/src on PYTHONPATH, so resolve bare names to their
# package-qualified path from the recorded source_file location.
def resolve_module(raw, source_file):
    if "." in raw:
        # Package-qualified (e.g. worms.nmap_scanner from vermillion_lightfury):
        # the parent of the package dir must be on sys.path for the import to
        # resolve. PYTHONPATH already carries azazael/src; add the recorded
        # package parent when it is not already present.
        d = os.path.dirname(source_file or "")
        pkg_parent = os.path.dirname(d) if d else ""
        if pkg_parent and pkg_parent not in sys.path:
            sys.path.insert(0, pkg_parent)
        return raw
    d = os.path.dirname(source_file or "")
    if d.endswith("WORMS"):
        return "CORE.WORMS." + raw
    if d.endswith("CORE"):
        return "CORE." + raw
    return raw

module_name = resolve_module(module_name, source_file)

result = {
    "worm": class_name,
    "module": module_name,
    "file_exists": bool(source_file and os.path.exists(source_file)),
    "import_ok": False,
    "instantiate_ok": False,
    "error": None,
    "error_type": None,
    "version": "?",
}

try:
    mod = importlib.import_module(module_name)
    result["import_ok"] = True

    cls = getattr(mod, class_name, None)
    if cls is None:
        result["error"] = "Class not found in module"
        result["error_type"] = "ClassNotFound"
    elif not isinstance(cls, type):
        result["error"] = "Not a class"
        result["error_type"] = "NotAClass"
    else:
        instance = cls()
        result["instantiate_ok"] = True
        result["version"] = str(getattr(instance, "VERSION", getattr(cls, "VERSION", "?")))

except ImportError as e:
    result["error"] = str(e)[:200]
    result["error_type"] = "ImportError"
except ModuleNotFoundError as e:
    result["error"] = str(e)[:200]
    result["error_type"] = "ModuleNotFoundError"
except TypeError as e:
    msg = str(e)[:200]
    if "required positional" in msg or "missing" in msg.lower():
        result["error"] = "Needs args: " + msg
        result["error_type"] = "NeedsArgs"
    else:
        result["error"] = msg
        result["error_type"] = "TypeError"
except Exception as e:
    result["error"] = str(e)[:200]
    result["error_type"] = type(e).__name__

print(json.dumps(result))
"""

tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
tmp.write(worker_code)
tmp.close()
worker_path = tmp.name

# Iterate over all worms
results = []
total = len(registry)
start_all = time.time()
src_dir = os.path.join(_P, "azazael", "src")
env = os.environ.copy()
env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")

for i, (worm_name, info) in enumerate(registry.items(), 1):
    module_name = info.get("module", "?")
    source_file = info.get("source_file", "")
    category = info.get("category", "?")
    version = info.get("version", "?")

    print("\r[" + str(i).rjust(3) + "/" + str(total) + "] " + worm_name[:40].ljust(40), end="", flush=True)

    try:
        proc = subprocess.run(
            [sys.executable, worker_path, module_name, worm_name, source_file],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
            cwd=src_dir, env=env,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            entry = json.loads(proc.stdout.strip())
        else:
            stderr = (proc.stderr or "")[:200]
            entry = {
                "worm": worm_name, "module": module_name, "category": category,
                "file_exists": bool(source_file and os.path.exists(source_file)),
                "import_ok": False, "instantiate_ok": False,
                "error": "Exit " + str(proc.returncode) + ": " + stderr,
                "error_type": "ExitCode" + str(proc.returncode),
                "version": version,
            }
    except subprocess.TimeoutExpired:
        entry = {
            "worm": worm_name, "module": module_name, "category": category,
            "file_exists": bool(source_file and os.path.exists(source_file)),
            "import_ok": False, "instantiate_ok": False,
            "error": "Timed out after 15s",
            "error_type": "Timeout", "version": version,
        }
    except Exception as e:
        entry = {
            "worm": worm_name, "module": module_name, "category": category,
            "file_exists": bool(source_file and os.path.exists(source_file)),
            "import_ok": False, "instantiate_ok": False,
            "error": str(e)[:200], "error_type": type(e).__name__,
            "version": version,
        }

    entry.setdefault("category", category)
    results.append(entry)

# Cleanup worker
try:
    os.unlink(worker_path)
except OSError:
    pass

print()
elapsed_all = time.time() - start_all

# Summary
file_ok = sum(1 for r in results if r["file_exists"])
import_ok = sum(1 for r in results if r["import_ok"])
instantiate_ok = sum(1 for r in results if r["instantiate_ok"])
needs_args = sum(1 for r in results if r.get("error_type") == "NeedsArgs")
timeout_n = sum(1 for r in results if r.get("error_type") == "Timeout")
crashed = sum(1 for r in results if (r.get("error_type") or "").startswith("ExitCode"))

summary = {
    "total_worms": len(results),
    "file_exists": file_ok,
    "import_ok": import_ok,
    "instantiate_ok": instantiate_ok,
    "needs_constructor_args": needs_args,
    "timed_out": timeout_n,
    "crashed": crashed,
    "elapsed_seconds": round(elapsed_all, 1),
}

# JSON output
json_path = os.path.join(_P, "azazael", "worm_health_matrix.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"summary": summary, "worms": results}, f, indent=2, default=str)

# Print matrix
print()
print("=" * 105)
print("  AZAZAEL WORM HEALTH MATRIX - " + str(len(results)) + " worms  |  " + str(round(elapsed_all, 1)) + "s")
print("=" * 105)
hdr = " " + "#".rjust(3) + " " + "Worm".ljust(38) + " " + "Category".ljust(16) + " " + "File".rjust(5) + " " + "Import".rjust(7) + " " + "Inst".rjust(5) + " " + "Version".ljust(8) + "  Error"
print(hdr)
print("-" * 105)

for i, r in enumerate(results, 1):
    f_ok = "OK" if r["file_exists"] else "MISS"
    i_ok = "OK" if r["import_ok"] else "FAIL"
    if r["instantiate_ok"]:
        t_ok = "OK"
    elif r.get("error_type") == "NeedsArgs":
        t_ok = "ARGS"
    else:
        t_ok = "FAIL"
    ver = str(r.get("version", "?"))[:8]
    err = (r.get("error") or "")[:30]
    cat = str(r.get("category", "?"))[:16]
    name = str(r["worm"])[:38]

    flag = ""
    if not r["file_exists"]:
        flag = " !!FILE"
    elif not r["import_ok"]:
        flag = " !!IMPORT"
    elif not r["instantiate_ok"] and r.get("error_type") != "NeedsArgs":
        flag = " !!INST"

    print(" " + str(i).rjust(3) + " " + name.ljust(38) + " " + cat.ljust(16) + " " + f_ok.rjust(5) + " " + i_ok.rjust(7) + " " + t_ok.rjust(5) + " " + ver.ljust(8) + " " + err[:28] + flag)

print("-" * 105)
print("  FILE: " + str(file_ok) + "/" + str(total) + "  |  IMPORT: " + str(import_ok) + "/" + str(total) + "  |  INSTANTIATE: " + str(instantiate_ok) + "/" + str(total))
print("  NEEDS_ARGS: " + str(needs_args) + "  |  TIMEOUT: " + str(timeout_n) + "  |  CRASHED: " + str(crashed))
print("  JSON: " + json_path)
print("=" * 105)
