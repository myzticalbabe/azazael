#!/bin/bash
# Probe: are the blocker packages actually unavailable as binary wheels, or was
# that a mis-diagnosis? Also: is a source build even possible here?
echo "=== HOST: $(hostname) / $(. /etc/os-release 2>/dev/null; echo "$PRETTY_NAME") ==="

echo "--- candidate free-threaded interpreters ---"
for PY in /usr/local/python314t/bin/python3 python3.14t python3.14 /usr/local/bin/python3.14t; do
  if command -v "$PY" >/dev/null 2>&1; then
    "$PY" -c 'import sys; print("  ", sys.executable, "| ver", sys.version.split()[0], "| gil", getattr(sys,"_is_gil_enabled",lambda:True)())' 2>&1 | head -2
  fi
done

echo "--- toolchain ---"
echo "  g++:   $(g++ --version 2>&1 | head -1)"
command -v cargo >/dev/null 2>&1 && echo "  cargo: $(cargo --version 2>&1)" || echo "  cargo: MISSING"
command -v rustc >/dev/null 2>&1 && echo "  rustc: $(rustc --version 2>&1)" || echo "  rustc: MISSING"

echo "--- mounts the wheel builder depends on ---"
for d in /mnt/g /mnt/d /mnt/c; do
  if mount | grep -q " $d "; then echo "  $d MOUNTED"; else echo "  $d not mounted"; fi
done
ls -d /mnt/g/AZAZAEL 2>/dev/null && echo "  /mnt/g/AZAZAEL reachable" || echo "  /mnt/g/AZAZAEL UNREACHABLE"

echo "--- sys.path site-packages order (shadow check) ---"
python3 -c 'import sys; [print("  ", p) for p in sys.path if "site-packages" in p]' 2>&1 | head -6

echo "--- binary wheel availability (--only-binary=:all:, no deps) ---"
T=$(mktemp -d)
for spec in tokenizers==0.23.0 click==8.5.0 charset-normalizer==3.5.1 transformers==5.17.0; do
  NAME="${spec%%=*}"
  if pip download "$spec" --no-deps --only-binary=:all: -d "$T" -q >/dev/null 2>&1; then
    W=$(ls "$T" 2>/dev/null | grep -i "^${NAME//-/[-_]}" | head -1)
    echo "  HAVE-BIN  $spec  -> ${W:-(dir?)}"
  else
    echo "  NO-BIN    $spec"
  fi
done
rm -rf "$T"

echo "--- what the resolver would pick (is backtracking the real cause?) ---"
pip index versions click 2>&1 | head -2
pip index versions charset-normalizer 2>&1 | head -2
