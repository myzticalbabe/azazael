#!/usr/bin/env bash
for p in /usr/bin/python3 /usr/bin/python3.13 /usr/bin/python3.14 /usr/local/bin/python3.14 /usr/local/python314t/bin/python3; do
  [ -x "$p" ] || continue
  echo "$p -> $("$p" -c 'import sys,platform;print(sys.version.split()[0], platform.python_implementation(), "gil_enabled=" + str(getattr(sys,"_is_gil_enabled",lambda:True)()))' 2>&1 | tail -1)"
done
