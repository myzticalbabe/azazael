"""Fusion status: one observability plane for Windows + WSL estates.

Reports Windows volumes, VHDX logical sizes, per-distro fs usage,
316t interpreter presence, and interop health (wsl.exe dispatch,
\\\\wsl$ reachability). Stdlib only. Numbers are measured live; a row
without a command behind it is not printed.

Usage:
    python tools/fusion_status.py            # text report
    python tools/fusion_status.py --json     # JSON report
"""

import json
import os
import shutil
import subprocess
import sys

VHDX = {
    "kali-linux": r"E:\Kali\ext4.vhdx",
    "Ubuntu-26.04": r"C:\wsl\Ubuntu-26.04\ext4.vhdx",
}
PY316T = {
    "windows": r"C:\Azazael\.venvs\py316t\Scripts\python.exe",
}
DISTRO_PY = ("/usr/local/bin/python3.16t", "/opt/python316t/bin/python3")


def gb(n: float) -> str:
    return f"{n / (1024 ** 3):.1f}GB"


def volumes() -> dict:
    out = {}
    for drive in ("C:", "E:", "G:"):
        try:
            u = shutil.disk_usage(drive + "\\")
            out[drive] = {"total": gb(u.total), "free": gb(u.free)}
        except OSError as e:
            out[drive] = {"error": str(e)[: 80]}
    return out


def vhdx() -> dict:
    out = {}
    for distro, path in VHDX.items():
        try:
            out[distro] = {"path": path, "logical": gb(os.path.getsize(path))}
        except OSError as e:
            out[distro] = {"path": path, "error": str(e)[: 80]}
    return out


def wsl_run(distro: str, argv: list) -> tuple:
    try:
        r = subprocess.run(
            ["wsl", "-d", distro] + argv,
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        tail = (r.stdout + r.stderr).strip().splitlines()
        return r.returncode, (tail[-1] if tail else "")
    except Exception as e:
        return -1, str(e)[: 100]


def distro_status(name: str) -> dict:
    d: dict = {"distro": name}
    rc, df = wsl_run(name, ["bash", "-c", "exec df -h / | tail -n 1"])
    d["df_root"] = df if rc == 0 else f"ERR rc={rc}: {df[: 60]}"
    found = []
    for p in DISTRO_PY:
        rc, _ = wsl_run(name, ["bash", "-c", f"exec test -x {p}"])
        if rc == 0:
            found.append(p)
    d["py316t"] = found or "absent"
    return d


def interop() -> dict:
    rc, _ = wsl_run("kali-linux", ["echo", "dispatch-ok"])
    out = {"wsl_dispatch_kali": "ok" if rc == 0 else f"ERR rc={rc}"}
    for unc in (r"\\wsl$\kali-linux", r"\\wsl$\Ubuntu-26.04"):
        out[unc] = "reachable" if os.path.isdir(unc) else "unreachable"
    win_py = PY316T["windows"]
    out["windows_316t"] = "present" if os.path.isfile(win_py) else "MISSING"
    return out


def main() -> None:
    report = {
        "volumes": volumes(),
        "vhdx_logical": vhdx(),
        "distros": [distro_status(d) for d in VHDX],
        "interop": interop(),
    }
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2))
        return
    print("== volumes ==")
    for k, v in report["volumes"].items():
        print(f"  {k} {v}")
    print("== vhdx (logical) ==")
    for k, v in report["vhdx_logical"].items():
        print(f"  {k} {v}")
    print("== distros ==")
    for d in report["distros"]:
        print(f"  {d['distro']}: {d['df_root']} | 316t={d['py316t']}")
    print("== interop ==")
    for k, v in report["interop"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
