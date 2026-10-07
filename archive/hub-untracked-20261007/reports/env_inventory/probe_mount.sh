#!/bin/bash
# Determine the most reliable predicate for "this directory is the real Windows
# drive, not the WSL ext4 root".
echo "=== mount-detection predicates ==="
for d in /mnt/g /mnt/gwin /mnt/c /; do
  printf "  %-12s findmnt=%-8s statT=%-10s mountpoint=%s\n" "$d" \
    "$(findmnt -no FSTYPE --target "$d" 2>/dev/null)" \
    "$(stat -f -c %T "$d" 2>/dev/null)" \
    "$(mountpoint -q "$d" && echo yes || echo no)"
done
echo "-- mount entry for the real drive --"
findmnt -no SOURCE,FSTYPE,TARGET --target /mnt/gwin 2>/dev/null || echo "  (none)"
echo "-- sentinel on the real drive --"
ls -d /mnt/gwin/AZAZAEL/cp314t_wheels 2>&1
echo "-- cargo on PATH? --"
if echo "$PATH" | tr ':' '\n' | grep -q cargo; then
  echo "  yes: $(command -v cargo)"
else
  echo "  no - build would need PATH+=/root/.cargo/bin"
fi
echo "-- free space at each candidate --"
df -h /mnt/g /mnt/gwin 2>/dev/null | tail -3
