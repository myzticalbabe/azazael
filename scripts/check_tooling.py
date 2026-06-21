#!/usr/bin/env python3
"""
check_tooling.py — Session startup tooling verification + auto-recorder.

MANDATORY: Run at the start of every Azazael session.
Records session_start and tooling_verify events in LocalMemoryStore.
See azazael-sop skill Rule 5 and azazael-startup skill Step 2.

Usage:
    python scripts/check_tooling.py

Auto-records (via CodebuffTracker):
    - session_start: One per session with environment context
    - tooling_verify: Each run with CLI tool availability data
"""

import os
import sys
import json
import subprocess
import shutil
import threading

# Add project src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _resolve_cmd(name: str) -> list:
    """Resolve a CLI command, handling Windows .CMD files via cmd.exe /c."""
    resolved = shutil.which(name)
    if resolved and resolved.lower().endswith('.cmd'):
        return ['cmd.exe', '/c', resolved]
    return [name]


def check_cli(name: str, version_flag: str = "--version") -> dict:
    """Check if a CLI tool is available and return its version."""
    try:
        cmd_path = _resolve_cmd(name)
        result = subprocess.run(
            cmd_path + [version_flag], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            return {"name": name, "available": True, "version": version.split("\n")[0]}
        return {"name": name, "available": False, "error": result.stderr.strip()}
    except FileNotFoundError:
        return {"name": name, "available": False, "error": "not found in PATH"}
    except Exception as e:
        return {"name": name, "available": False, "error": str(e)}


def _find_npm() -> str:
    """Find npm executable. Delegates to _resolve_cmd for .CMD handling."""
    npm_path = shutil.which("npm")
    if npm_path:
        return npm_path
    return "npm"


def check_npm_package(package: str) -> dict:
    """Check if an npm global package is installed."""
    try:
        npm_exe = _find_npm()
        # On Windows, .cmd files need cmd.exe /c wrapper, not shell=True
        if npm_exe.endswith('.cmd'):
            cmd = ['cmd.exe', '/c', npm_exe, 'list', '-g', package, '--depth=0']
        else:
            cmd = [npm_exe, 'list', '-g', package, '--depth=0']
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15
        )
        available = result.returncode == 0
        version = ""
        if available:
            for line in result.stdout.split("\n"):
                if f" {package}@" in line or f"{package}@" in line:
                    version = line.split("@")[-1].strip()
                    break
        return {
            "name": package,
            "available": available,
            "version": version or (result.stdout.strip()[:80] if result.stdout else ""),
        }
    except Exception as e:
        return {"name": package, "available": False, "error": str(e)}


def check_pip_package(name: str, import_name: str = None) -> dict:
    """Check if a pip package is available by trying to import it."""
    try:
        import importlib
        mod = importlib.import_module(import_name or name)
        ver = getattr(mod, "__version__", "installed")
        return {"name": name, "available": True, "version": str(ver)}
    except ImportError:
        return {"name": name, "available": False, "error": "not installed"}
    except Exception as e:
        return {"name": name, "available": False, "error": str(e)}


def _record_with_timeout(results: dict, timeout_seconds: int = 45) -> bool:
    """Record session events with a timeout guard.

    CodebuffTracker.get_tracker() triggers discover_worms() (~38s cold start
    on 3.14t). This wrapper prevents the tool from hanging indefinitely if
    worm discovery takes longer than expected.
    """
    result_holder = [False]
    exception_holder = [None]

    def _do_record():
        try:
            from CORE.codebuff_tracker import get_tracker
            tracker = get_tracker()
            tracker.record_tooling_verify(
                tools_found=results.get("tools_found", 0),
                tools_missing=results.get("tools_missing", 0),
                details={
                    "cli_tools": results.get("cli_tools", []),
                    "pip_packages": results.get("pip_packages", []),
                    "npm_packages": results.get("npm_packages", []),
                    "python_314t": results.get("python_314t", "not found"),
                },
            )
            result_holder[0] = True
        except Exception as e:
            exception_holder[0] = e

    t = threading.Thread(target=_do_record, daemon=True)
    t.start()
    t.join(timeout=timeout_seconds)

    if t.is_alive():
        # Timed out — worm registry discovery likely slow on cold start
        print(f"    [--] Session recording timed out after {timeout_seconds}s "
              f"(worm registry cold-start may be slow)")
        return False

    if exception_holder[0]:
        print(f"    [--] Session recording failed: {exception_holder[0]}")
        return False

    return result_holder[0]


def main():
    print("=" * 60)
    print("  Azazael — Tooling Verification (with auto-recording)")
    print("=" * 60)

    results = {
        "cli_tools": [],
        "pip_packages": [],
        "npm_packages": [],
        "tools_found": 0,
        "tools_missing": 0,
        "python_314t": "not checked",
    }

    # -- 1. CLI tools --
    print("\n  [1] CLI Tools:")
    tools = [
        ("python"), ("git"), ("node"), ("npm"), ("freebuff"),
    ]
    for name in tools:
        info = check_cli(name)
        status = "[OK]" if info["available"] else "[--]"
        version = info.get("version", info.get("error", "?"))
        print(f"    {status} {name}: {version}")
        results["cli_tools"].append(info)
        if info["available"]:
            results["tools_found"] += 1
        else:
            results["tools_missing"] += 1

    # -- 2. pip packages --
    print("\n  [2] pip Packages (Python dependencies):")
    pip_packages = [
        ("Pillow", "PIL"),
        ("psutil", None),
        ("psycopg2-binary", "psycopg2"),
        ("numpy", "numpy"),
    ]
    for name, import_name in pip_packages:
        info = check_pip_package(name, import_name)
        status = "[OK]" if info["available"] else "[--]"
        note = info.get("version", info.get("error", "?"))
        if name == "psycopg2-binary" and not info["available"]:
            note = "broken on 3.14t (cp314t wheel missing libpq DLLs)"
        print(f"    {status} {name}: {note}")
        pkg_info = {"name": name, "available": info["available"]}
        if info.get("version"):
            pkg_info["version"] = note
        results["pip_packages"].append(pkg_info)

    # -- 3. npm global packages --
    print("\n  [3] npm Global Packages:")
    npm_packages = ["freebuff", "pnpm", "node-gyp"]
    for pkg in npm_packages:
        info = check_npm_package(pkg)
        status = "[OK]" if info["available"] else "[--]"
        print(f"    {status} {pkg}: {info.get('version', info.get('error', '?'))}")
        results["npm_packages"].append(info)

    # -- 4. Python 3.14t check --
    print("\n  [4] Python 3.14t:")
    python314_paths = [
        r"C:\Users\clint\AppData\Local\Programs\Python\Python314\python3.14t.exe",
        os.path.expanduser("~/.local/bin/python3.14t.exe"),
    ]
    found_314t = False
    for p in python314_paths:
        if os.path.exists(p):
            try:
                result = subprocess.run(
                    [p, "--version"], capture_output=True, text=True, timeout=10
                )
                print(f"    [OK] {p}")
                print(f"          {result.stdout.strip()}")
                found_314t = True
                results["python_314t"] = result.stdout.strip()
            except Exception:
                print(f"    [--] {p} (exists but failed)")
    if not found_314t:
        print("    [??] python3.14t not found at expected paths")

    # -- 5. LocalMemoryStore schema check --
    print("\n  [5] LocalMemoryStore Schema:")
    try:
        from CORE.local_memory import get_memory_store
        store = get_memory_store()
        ic = store.integrity_check()
        ok = ic.get("ok", ic.get("passed", False))
        print(f"    [{'OK' if ok else '--'}] integrity: passed={ok}")
        for k, v in ic.items():
            if k in ("ok", "passed", "errors"):
                continue
            if isinstance(v, (int, float, str, bool)):
                print(f"         {k}: {v}")
        if ic.get("errors"):
            for e in ic["errors"][:3]:
                print(f"         error: {e}")
    except Exception as e:
        print(f"    [--] integrity check failed: {e}")

    # -- 6. azazael-core & Nuitka build prerequisites --
    print("\n  [6] azazael-core Package & Nuitka Build:")
    core_path = os.path.join(os.path.dirname(__file__), "..", "packages", "azazael-core")
    if os.path.exists(core_path):
        cli_path = os.path.join(core_path, "src", "azazael_core", "cli.py")
        readme = os.path.join(core_path, "README.md")
        print(f"    [OK] azazael-core dir: {core_path}")
        print(f"         CLI source exists: {os.path.exists(cli_path)}")
        print(f"         README exists: {os.path.exists(readme)}")
    else:
        print(f"    [--] azazael-core not found at {core_path}")

    try:
        import importlib
        nuitka_mod = importlib.import_module("nuitka")
        nuitka_ver = getattr(nuitka_mod, "__version__", "installed")
        print(f"    [OK] Nuitka: {nuitka_ver}")
    except ImportError:
        print(f"    [--] Nuitka: not installed (for build: pip install nuitka)")

    try:
        result = subprocess.run(
            ["python", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
            capture_output=True, text=True, timeout=10
        )
        pyver = result.stdout.strip()
        print(f"    [OK] Python (default): {pyver}")
        major = int(pyver.split(".")[0])
        minor = int(pyver.split(".")[1])
        if major == 3 and minor == 14:
            print(f"         Nuitka-ready: YES (Python {pyver} is the build Python, patches applied via patch_nuitka_314t.py)")
        elif major == 3 and minor == 13:
            print(f"         Nuitka-ready: check (Python {pyver} - use 3.14t for builds)")
        else:
            print(f"         Nuitka-ready: check (Python {pyver} - builds require 3.14t)")
    except Exception as e:
        print(f"    [--] Python version check: {e}")

    # -- 7. freebuff_ready events in memory --
    print("\n  [7] freebuff_ready Events (LocalMemoryStore):")
    events = []
    try:
        from CORE.local_memory import get_memory_store
        store = get_memory_store()
        events = store.query_memories(event_type="freebuff_ready", limit=5)
    except Exception:
        pass
    if events:
        for ev in events:
            data = ev.get("data", {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    data = {}
            pm = data.get("package_manager", data.get("install_method", "?"))
            ver = data.get("version", "?")
            print(f"    [OK] id={ev.get('id')} v{ver} pm={pm}")
    else:
        print("    [??] No freebuff_ready events found")

    # -- 8. Auto-record session events (Rule 5 mandate) --
    # Uses timeout guard: get_tracker() triggers discover_worms() (~38s cold)
    print("\n  [8] Session Recording (mandatory):")
    recorded = _record_with_timeout(results, timeout_seconds=60)
    if recorded:
        print("    [OK] session_start + tooling_verify recorded in LocalMemoryStore")
    else:
        print("    [--] Session recording skipped (timeout or unavailable)")
        print("         Run 'python scripts/check_tooling.py' again after registry warms up")

    print("\n" + "=" * 60)
    print("  Tooling check complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
