#!/usr/bin/env python3
"""sync_diff_audit.py — Compare Windows sync sources against WSL2 synced files."""

import sys, os, hashlib, glob, subprocess
sys.stdout.reconfigure(encoding="utf-8")

WIN_ROOT = "C:/Users/clint/azazael"

# Pattern definitions from sync_all.py
SYNC_PATTERNS = {
    "code": [
        "src/CORE/WORMS/expansion/*.py",
        "src/CORE/WORMS/CLUSTERWORMS.py",
        "src/CORE/WORMS/METACLUSTER.py",
        "src/CORE/WORMS/NETWORK_DIAG.py",
        "src/CORE/WORMS/CODEX_TOOLS.py",
        "src/CORE/WORMS/CROSS_NATURE_ROUTER.py",
        "src/ORCHESTRATION/hydra_bridge.py",
        "tests/test_neural_advancement.py",
        "tests/test_p0_worms.py",
    ],
    "docs": [
        "docs/*.md",
        "docs/scripts/*.py",
        "LESSONS_*.md",
        "MEMORIES*.md",
        "MASTER_TASKS.md",
    ],
    "scripts": [
        "scripts/sync_all.py",
        "scripts/build_all_concurrent.py",
    ],
}

# ── Collect Windows files ──
win_files = {}
for cat, patterns in SYNC_PATTERNS.items():
    for pattern in patterns:
        full_pattern = os.path.join(WIN_ROOT, pattern).replace("\\", "/")
        for f in sorted(glob.glob(full_pattern)):
            rel = os.path.relpath(f, WIN_ROOT).replace("\\", "/")
            h = hashlib.md5(open(f, "rb").read()).hexdigest()
            sz = os.path.getsize(f)
            win_files[rel] = (h, sz, cat)

print(f"Windows files matching sync patterns: {len(win_files)}")
print()

# ── Collect WSL2 files (bytes mode for encoding safety) ──
res = subprocess.run(
    ["wsl", "-d", "Ubuntu-26.04", "-e", "bash", "-c",
     "cd /root/azazael && find . -type f -exec md5sum {} \\; 2>/dev/null"],
    capture_output=True, timeout=120,
)
rc = res.returncode
stdout = res.stdout.decode("utf-8", errors="replace")
stderr = res.stderr.decode("utf-8", errors="replace")

wsl_files = {}
if rc == 0:
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            h, path = parts
            rel = path[2:] if path.startswith("./") else path
            rel = rel.replace("\\", "/")
            wsl_files[rel] = h
    print(f"WSL2 files found (total): {len(wsl_files)}")
else:
    print(f"WSL2 listing FAILED: {stderr[:300]}")
    sys.exit(1)
print()

# ── Sync coverage by category ──
print("=== Sync Coverage by Category ===")
print(f"{'Category':<20} {'Windows':<10} {'WSL2':<12} {'Notes'}")
print("-" * 55)
for cat in ["code", "docs", "scripts"]:
    win_paths = {p for p, (h, s, c) in win_files.items() if c == cat}
    wsl_has = {p for p in win_paths if p in wsl_files}
    missing = win_paths - wsl_has
    common = wsl_has & win_paths
    mismatches = [p for p in common if win_files[p][0] != wsl_files[p]]
    notes = []
    if missing:
        notes.append(f"{len(missing)} missing")
    if mismatches:
        notes.append(f"{len(mismatches)} hash mismatch")
    print(f"{cat:<20} {len(win_paths):<10} {len(wsl_has):<12} {', '.join(notes) if notes else 'OK'}")

print()

# ── Missing files ──
all_expected = set(win_files.keys())
all_present = set(wsl_files.keys()) & all_expected
missing_all = sorted(all_expected - all_present)
print(f"=== MISSING Files ({len(missing_all)}) ===")
if missing_all:
    for p in missing_all:
        h, sz, cat = win_files[p]
        print(f"  [{cat:7}] {p} ({sz:,} bytes)")
else:
    print("  (none - all files present)")
print()

# ── Hash mismatches ──
common = all_present
mismatches = sorted([p for p in common if win_files[p][0] != wsl_files[p]])
print(f"=== HASH MISMATCHES ({len(mismatches)}) ===")
if mismatches:
    for p in mismatches:
        wh, ws, cat = win_files[p]
        wslh = wsl_files[p]
        print(f"  [{cat:7}] {p}")
        print(f"          WIN:  {wh}")
        print(f"          WSL2: {wslh}")
else:
    print("  (none - all synced files match)")
print()

# ── Extra WSL2-only files ──
extra = sorted(set(wsl_files.keys()) - all_expected)
print(f"=== EXTRA WSL2 Files ({len(extra)}) ===")
if extra:
    root_md = [p for p in extra if p.endswith(".md") and "/" not in p]
    if root_md:
        print(f"  Root .md files ({len(root_md)}):")
        for p in root_md:
            print(f"    {p}")
    other = [p for p in extra if p not in root_md]
    if other:
        print(f"  Other files ({len(other)}):")
        for p in other[:15]:
            print(f"    {p}")
        if len(other) > 15:
            print(f"    ... and {len(other) - 15} more")
    if not root_md and not other:
        print("  (no extra files of note)")
else:
    print("  (none)")
print()

# ── Summary ──
res2 = subprocess.run(
    ["wsl", "-d", "Ubuntu-26.04", "-e", "bash", "-c",
     "ls /root/azazael/docs/*.md 2>/dev/null | wc -l"],
    capture_output=True, timeout=10,
)
out2 = res2.stdout.decode("utf-8", errors="replace") if res2.returncode == 0 else "?"
res3 = subprocess.run(
    ["wsl", "-d", "Ubuntu-26.04", "-e", "bash", "-c",
     "find /root/azazael/src -name '*.py' 2>/dev/null | wc -l"],
    capture_output=True, timeout=10,
)
out3 = res3.stdout.decode("utf-8", errors="replace") if res3.returncode == 0 else "?"

print("=== SYNC FIDELITY SUMMARY ===")
print(f"Files in sync patterns:  {len(win_files)}")
print(f"Present in WSL2:         {len(all_present)}")
print(f"Missing from WSL2:       {len(missing_all)}")
print(f"Hash mismatches:         {len(mismatches)}")
print(f"Extra WSL2-only files:   {len(extra)}")
print(f"docs/*.md in WSL2:       {out2.strip() if out2 != '?' else '?'}")
print(f".py files in WSL2 src:   {out3.strip() if out3 != '?' else '?'}")

status = "PASS" if len(missing_all) == 0 and len(mismatches) == 0 else "ISSUES FOUND"
print(f"\nOverall: {status}")
