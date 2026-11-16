"""Fusion status: one observability plane for Windows + WSL estates.

Reports Windows volumes, VHDX logical sizes, per-distro fs usage,
316t interpreter presence, and interop health (wsl.exe dispatch,
\\\\wsl$ reachability). Stdlib only. Numbers are measured live; a row
without a command behind it is not printed.

Usage:
    python tools/fusion_status.py            # text report
    python tools/fusion_status.py --json     # JSON report
    python tools/fusion_status.py --strict   # findings decide the exit

Exit contract: 0 clean, or findings printed but advisory; 1 findings under
--strict; 2 when not one row could be measured. A leg that prints UNREACHABLE
and exits 0 is a verdict nothing acted on, so --strict is the switch deep_dive's
ratchet pulls once this leg has run clean -- and it is passed in-process, not
as a subprocess flag.
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


def findings(report: dict) -> list:
    """Every row that measured a problem, one line each.

    A finding is a measurement that came back wrong, not one that came back
    absent: an unreachable distro, a volume or VHDX that raised, no 3.16t on
    either side, interop that did not answer. The report prints these lines
    either way; this list is what --strict turns into an exit status, and it
    is the only thing that can, because the printed row alone never decided
    anything.
    """
    out = []
    for name, row in report["volumes"].items():
        if "error" in row:
            out.append("volume %s %s" % (name, row["error"]))
    for name, row in report["vhdx_logical"].items():
        if "error" in row:
            out.append("vhdx %s %s" % (name, row["error"]))
    for row in report["distros"]:
        root = str(row.get("df_root", ""))
        if not root.startswith("/dev/"):
            out.append("%s: root fs not measured (%s)" % (row["distro"], root))
        if row.get("py316t") == "absent":
            out.append("%s: no 3.16t interpreter" % row["distro"])
    interop_rows = report["interop"]
    if interop_rows.get("wsl_dispatch_kali") != "ok":
        out.append("wsl dispatch: %s" % interop_rows.get("wsl_dispatch_kali"))
    for name, row in interop_rows.items():
        if name.startswith("\\\\") and row != "reachable":
            out.append("%s: %s" % (name, row))
    if interop_rows.get("windows_316t") != "present":
        out.append("windows 3.16t interpreter: %s"
                   % interop_rows.get("windows_316t"))
    return out


def measured(report: dict) -> int:
    """Rows that produced a number -- the denominator the verdict needs.

    Blind is not "some rows failed": it is not one row measured. Counting it
    here keeps the report from saying `clean` over a report it never read, and
    a zero here is the only path to exit 2.
    """
    rows = sum(1 for row in report["volumes"].values() if "error" not in row)
    rows += sum(1 for row in report["vhdx_logical"].values()
                if "error" not in row)
    rows += sum(1 for row in report["distros"]
                if str(row.get("df_root", "")).startswith("/dev/"))
    rows += 1 if report["interop"].get("windows_316t") == "present" else 0
    return rows


BUDGET_S = 60.0  # measured ~5s (2 VHDX stats + wsl probes); 12x headroom


def main(argv=None) -> int:
    """Hyper-edge auditor entry: accepts the runner's argv list, returns exit.

    The exit status is the reading, not the report: findings alone are
    advisory (the leg runs on a tree that carries known debt), --strict makes
    them the exit, and a report with no denominator at all is 2 -- could not
    judge, which is never a pass.
    """
    args = list(argv) if argv is not None else sys.argv[1:]
    strict = "--strict" in args
    report = {
        "volumes": volumes(),
        "vhdx_logical": vhdx(),
        "distros": [distro_status(d) for d in VHDX],
        "interop": interop(),
    }
    bad = findings(report)
    rows = measured(report)
    if "--json" in args:
        report["findings"] = bad
        print(json.dumps(report, indent=2))
        if not rows:
            return 2
        return 1 if (bad and strict) else 0
    states = ", ".join(
        "%s %s" % (d["distro"],
                     "reachable" if str(d.get("df_root", "")).startswith("/dev/")
                     else "UNREACHABLE")
        for d in report["distros"])
    print("fusion: %s | windows_316t=%s | %d finding(s)"
          % (states, report["interop"].get("windows_316t", "?"), len(bad)))
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
    print("== findings ==")
    if bad:
        for line in bad:
            print("  DEFECT   %s" % line)
    else:
        print("  none     every row measured and read clean")
    print("fusion      %d row(s) measured, %d finding(s)%s"
          % (rows, len(bad),
             "" if strict else " (advisory; --strict fails the run)"))
    if not rows:
        print("fusion: BLIND -- not one row produced a number, and a run that "
              "cannot measure is not a pass")
        return 2
    if bad and strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
