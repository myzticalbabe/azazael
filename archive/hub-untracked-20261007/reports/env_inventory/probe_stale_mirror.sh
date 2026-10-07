#!/bin/bash
# Is the 67 GB /mnt/g directory (ext4, not the G: drive) still needed?
# Evidence: size, age, uniqueness vs the real drive, and whether anything in it
# is referenced by the project.
echo "=== SIZE PER TOP-LEVEL ENTRY ==="
du -sh /mnt/g/* 2>/dev/null | sort -hr | head -20

echo
echo "=== AGE (mtime) PER ENTRY ==="
find /mnt/g -maxdepth 1 -mindepth 1 -printf '%TY-%Tm-%Td %TH:%TM  %p\n' 2>/dev/null | sort | head -20

echo
echo "=== SCALE ==="
echo "  files: $(find /mnt/g -type f 2>/dev/null | wc -l)"
echo "  dirs:  $(find /mnt/g -type d 2>/dev/null | wc -l)"
echo "  symlinks: $(find /mnt/g -type l 2>/dev/null | wc -l)"
echo "  newest file: $(find /mnt/g -type f -printf '%TY-%Tm-%Td %p\n' 2>/dev/null | sort | tail -1)"

echo
echo "=== IS ANYTHING UNIQUE?  (compare against the real drive mount) ==="
if [ -d /mnt/gdrive ]; then
  for e in /mnt/g/*; do
    n=$(basename "$e")
    if [ -e "/mnt/gdrive/$n" ]; then echo "  also on real G:  $n"; else echo "  ONLY-IN-WSL:     $n"; fi
  done
else
  echo "  (real drive not mounted at /mnt/gdrive)"
fi

echo
echo "=== ANY PREVIOUSLY BUILT cp314t WHEELS IN THERE? ==="
find /mnt/g -name "*.whl" 2>/dev/null | head -20
echo "  whl count: $(find /mnt/g -name '*.whl' 2>/dev/null | wc -l)"

echo
echo "=== WHAT IS archived-wheels / nuitka-314t / AZAZAEL_EXE? ==="
for d in /mnt/g/archived-wheels /mnt/g/nuitka-314t /mnt/g/AZAZAEL_EXE /mnt/g/standalone; do
  [ -d "$d" ] || continue
  echo "-- $d ($(du -sh "$d" 2>/dev/null | cut -f1)) --"
  ls -1 "$d" 2>/dev/null | head -8
done
