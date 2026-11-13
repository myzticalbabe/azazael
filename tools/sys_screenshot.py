#!/usr/bin/env python3
"""sys_screenshot — expose the bare-metal screen as a file, on demand.

WHY THIS EXISTS
---------------
Before the reboot the operator needs eyes on the machine itself: a screenshot
capability that works headless, from a lane, with no GUI automation and no new
dependency. Windows already ships the whole stack (System.Windows.Forms +
System.Drawing); this tool is the one-command front door over it.

    python tools/sys_screenshot.py                 # shot now, path on stdout
    python tools/sys_screenshot.py --out DIR       # choose the landing directory
    python tools/sys_screenshot.py --pictures      # land where Win+PrtScr lands
    python tools/sys_screenshot.py --full          # also print size + timestamp

ON WIN+PRTSCR
------------
Win+PrtScr is an Explorer shell hotkey, not an API: Explorer listens for the
chord and writes Screenshot (n).png into %USERPROFILE%/Pictures/Screenshots.
A headless tool cannot press it through SendKeys (no Windows-key support), and
synthesising it via SendInput would capture the identical pixels through the
identical screen DC while adding a fragile moving part. --pictures therefore
honours the request the durable way: same folder, same Screenshot (n).png
naming, same pixels, no keystroke theatre.

The shot lands in C:\\Users\\clint\\screenshots\\ by default, named
shot_YYYYMMDDTHHMMSS.png. Exit 0 names a real file; anything else is BLIND or
a failure, never a silent pass.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DIR = Path(r"C:\Users\clint\screenshots")

PS_SNIP = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bmp.Save('{out}')
$g.Dispose()
$bmp.Dispose()
'{out}'
"""


def pictures_dir() -> Path:
    """Where Win+PrtScr lands: %USERPROFILE%\\Pictures\\Screenshots."""
    return Path(os.environ.get("USERPROFILE", r"C:\Users\clint")) / "Pictures" / "Screenshots"


def next_pictures_name(out_dir: Path) -> Path:
    """Windows' own naming: Screenshot.png, then Screenshot (n).png."""
    candidate = out_dir / "Screenshot.png"
    n = 1
    while candidate.exists():
        n += 1
        candidate = out_dir / f"Screenshot ({n}).png"
    return candidate


def take_screenshot(out_dir: Path, pictures_style: bool = False) -> Path:
    """Capture the virtual screen. Returns the path of a real PNG, or raises."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if pictures_style:
        out = next_pictures_name(out_dir)
    else:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        out = out_dir / f"shot_{stamp}.png"
    script = PS_SNIP.format(out=str(out))
    done = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                          capture_output=True, text=True, timeout=120, check=False)
    if done.returncode != 0:
        raise RuntimeError(f"screenshot backend failed: {done.stderr.strip()[-300:]}")
    if not out.exists() or out.stat().st_size == 0:
        raise RuntimeError("backend reported success but left no file")
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Screenshot the bare-metal screen to a PNG.")
    parser.add_argument("--out", default=str(DEFAULT_DIR), help="landing directory")
    parser.add_argument("--pictures", action="store_true",
                        help="land where Win+PrtScr lands, with its naming")
    parser.add_argument("--full", action="store_true", help="also print size + timestamp")
    args = parser.parse_args(argv)
    try:
        target = pictures_dir() if args.pictures and args.out == str(DEFAULT_DIR) else Path(args.out)
        shot = take_screenshot(target, pictures_style=args.pictures)
    except (RuntimeError, OSError) as exc:
        print(f"sys_screenshot: BLIND -- {exc}", file=sys.stderr)
        return 2
    size_kb = shot.stat().st_size / 1024
    print(str(shot))
    if args.full:
        print(f"{size_kb:.0f} KB  {datetime.now().isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
