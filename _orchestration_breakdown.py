import subprocess
import re
from collections import Counter

result = subprocess.run(
    ["npx", "pyright", "src/ORCHESTRATION/"],
    capture_output=True, text=True, shell=True, timeout=120
)

file_counts = Counter()
dir_counts = Counter()

for line in result.stdout.splitlines():
    if "error:" not in line:
        continue
    # Extract file path relative to ORCHESTRATION/
    m = re.search(r"ORCHESTRATION[\\/](.+?):\d+:", line)
    if m:
        fpath = m.group(1)
        file_counts[fpath] += 1
        # Also count by subdirectory
        parts = fpath.replace("\\", "/").split("/")
        if len(parts) > 1:
            dir_counts[parts[0]] += 1
        else:
            dir_counts["(root)"] += 1

print("=== By subdirectory ===")
for d, c in dir_counts.most_common():
    print(f"  {c:5d}: {d}")
print(f"  {'-'*5}")
print(f"  {sum(dir_counts.values()):5d}: TOTAL")
print()

print("=== Top 20 files by error count ===")
for f, c in file_counts.most_common(20):
    print(f"  {c:4d}: {f}")
