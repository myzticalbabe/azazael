import subprocess
import re
from collections import Counter

print("Running full-project pyright...")
result = subprocess.run(
    ["npx", "pyright", "src/"],
    capture_output=True, text=True, shell=True, timeout=300
)

dir_counts = Counter()
file_counts = Counter()

for line in result.stdout.splitlines():
    if "error:" not in line:
        continue
    
    # Extract top-level directory: src/DIR/...
    m = re.search(r"src[\\/]([^\\/]+)", line)
    if m:
        dir_counts[m.group(1)] += 1
    
    # Extract file path
    m = re.search(r"(src[\\/].+?\.py):", line)
    if m:
        file_counts[m.group(1)] += 1

print("=== Errors by directory ===")
for d, c in dir_counts.most_common():
    print(f"  {c:5d}: {d}")
print(f"  {'─' * 20}")
print(f"  {sum(dir_counts.values()):5d}: TOTAL")
print()

print("=== Top 20 files by error count ===")
for f, c in file_counts.most_common(20):
    print(f"  {c:4d}: {f}")
print(f"  {'─' * 20}")
print(f"  {sum(file_counts.values()):4d}: TOTAL in py files")

# Also show non-py files with errors
other_counts = Counter()
for line in result.stdout.splitlines():
    if "error:" not in line:
        continue
    m = re.search(r"(src[\\/].+?):\d+:", line)
    if m and not m.group(1).endswith(".py"):
        other_counts[m.group(1)] += 1

if other_counts:
    print()
    print("=== Non-py files with errors ===")
    for f, c in other_counts.most_common(10):
        print(f"  {c:4d}: {f}")
