# coding: utf-8
import subprocess, io, collections
REPO = r"C:\Azazael\azazael"

def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True)
    return r.stdout.decode("utf-8", "replace")

def head_text(path):
    r = subprocess.run(["git", "show", "HEAD:" + path], cwd=REPO, capture_output=True)
    return None if r.returncode != 0 else r.stdout.decode("utf-8", "replace")

def work_text(path):
    try:
        with io.open(REPO + "\\" + path.replace("/", "\\"), "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None

status = git("status", "--porcelain", "Project_ELIZA")
mod, dele, unt = [], [], []
for line in status.splitlines():
    if len(line) < 4: continue
    code, path = line[:2].strip(), line[3:].strip().strip('"')
    if code.startswith("M"): mod.append(path)
    elif code.startswith("D"): dele.append(path)
    elif code.startswith("??"): unt.append(path)

WIRE = "import_module('adopted."
REFUSE = "is an intake stub"
b = {"wiring_lost": [], "wiring_kept": [], "other": []}
for p in mod:
    w, h = work_text(p), head_text(p)
    if w is None: b["other"].append(p); continue
    if REFUSE in w and h and WIRE in h: b["wiring_lost"].append(p)
    elif WIRE in w: b["wiring_kept"].append(p)
    else: b["other"].append(p)

print("modified tracked :", len(mod))
print("  wiring_lost    :", len(b["wiring_lost"]))
print("  wiring_kept    :", len(b["wiring_kept"]))
print("  other          :", len(b["other"]))
print("deleted tracked  :", len(dele))
print("untracked        :", len(unt))
print("\n-- other modified (first 8) --")
for p in b["other"][:8]: print("   ", p)
print("\n-- untracked (first 8) --")
for p in unt[:8]: print("   ", p)
print("\n-- deleted (first 8) --")
for p in dele[:8]: print("   ", p)

kinds = collections.Counter()
for p in b["other"][:40]:
    for ln in git("diff", "--unified=0", "--", p).splitlines():
        if ln.startswith("+") and not ln.startswith("+++"): kinds["added"] += 1
        elif ln.startswith("-") and not ln.startswith("---"): kinds["removed"] += 1
print("\nother[0:40] diff line totals:", dict(kinds))

with io.open(REPO + r"\.tmp_shardtest\lost.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(b["wiring_lost"]))
print("\nwrote lost.txt with", len(b["wiring_lost"]), "paths")
