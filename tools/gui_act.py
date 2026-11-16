#!/usr/bin/env python3
"""gui_act — see the desktop, prove focus from pixels, and only then touch it.

WHY THIS EXISTS
---------------
Humans verify alongside AI through the rendered UI: a screenshot is a claim,
and a click is an act. The 2026-09-04 incident proved the act needs a gate —
blind automation leaked keystrokes into a Facebook/Messenger window because
nothing verified which window would receive them. The standing rules live in
`.agents/skills/desktop-automation-safety.md`; this tool is those rules as code:

  Rule 1  one process, minimize the world, Win32 foreground dance, restore end
  Rule 2  content-verified focus (screenshot + OCR of the target chrome) before
          ANY keystroke — a foreground-title check alone is not proof
  Rule 3  leak protocol: abort on lost focus, keep the captures, say so loudly
  Rule 4  one DPI space: per-monitor-v2 awareness, live rects, never cached
  Rule 5  evidence: every stage screenshotted under evidence/, keepers OCR'd

Zero new dependencies by design: synthetic input via ctypes SendInput (no
pyautogui import to smuggle in DPI side-effects), OCR via the tesseract binary
already on this box, pixels via the same screen-DC path as sys_screenshot.py.

    python tools/gui_act.py --probe                    # observe only: windows, rects, OCR
    python tools/gui_act.py --plan TARGET --do ACTIONS # print the plan, touch nothing
    python tools/gui_act.py --plan TARGET --do ACTIONS --confirm-live
        # the real thing: gate printed, focus proven, actions run, world restored

ACTIONS is a ';'-separated list: click X Y | type TEXT | hotkey K1 K2 ... |
wait SECONDS. Without --confirm-live nothing is pressed, moved, or typed —
the tool observes and plans, and says so. Exit 0 clean, 2 blind/refused,
3 aborted mid-run with the desktop restored.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

EVIDENCE = Path(r"C:\Users\clint\evidence\gui_act")

# --------------------------------------------------------------------------
# Win32 via ctypes — no pyautogui, no DPI side-effects smuggled in by import.
# --------------------------------------------------------------------------

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

DPI_AWARE = False
DPI_NOTE = ""
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor v2: physical px
    DPI_AWARE = True
except OSError as exc:
    # Older Windows: coordinates stay logical. Rule 4 is then NOT met, and the
    # probe says so rather than letting a silent fallback double every click.
    DPI_NOTE = f"DPI awareness unavailable ({exc}); coordinates stay logical"

SW_MINIMIZE, SW_RESTORE = 6, 9
INPUT_MOUSE, INPUT_KEYBOARD = 0, 1
KEYEVENTF_KEYUP = 0x0002
VK = {"ctrl": 0x11, "alt": 0x12, "shift": 0x10, "win": 0x5B, "enter": 0x0D,
      "tab": 0x09, "esc": 0x1B, "prtscr": 0x2C}


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_void_p)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]


def _send(*inputs: INPUT) -> None:
    arr = (INPUT * len(inputs))(*inputs)
    if user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT)) != len(inputs):
        raise RuntimeError("SendInput delivered partial input — aborting")


def _key(vk: int, down: bool) -> INPUT:
    ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=0 if down else KEYEVENTF_KEYUP,
                    time=0, dwExtraInfo=None)
    return INPUT(type=INPUT_KEYBOARD, u=INPUT._U(ki=ki))


def list_windows() -> list[dict]:
    """Visible top-level windows: handle, title, rect. Observation only."""
    out: list[dict] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum(hwnd, _lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            out.append({"hwnd": hwnd, "title": buf.value,
                        "rect": (rect.left, rect.top, rect.right, rect.bottom)})
        return True

    user32.EnumWindows(enum, 0)
    return out


def foreground_title() -> str:
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def minimize_all(except_hwnds: set[int]) -> list[int]:
    """Minimize every visible top-level window outside the keep set (Rule 1)."""
    minimized = []
    for win in list_windows():
        if win["hwnd"] in except_hwnds or not win["title"].strip():
            continue
        if user32.IsIconic(win["hwnd"]):
            continue
        user32.ShowWindow(win["hwnd"], SW_MINIMIZE)
        minimized.append(win["hwnd"])
    return minimized


def restore_all(hwnds: list[int]) -> None:
    for hwnd in hwnds:
        user32.ShowWindow(hwnd, SW_RESTORE)


def bring_to_front(hwnd: int) -> None:
    """The Win32 foreground dance (Rule 1): restore, attach, top, set, detach."""
    user32.ShowWindow(hwnd, SW_RESTORE)
    fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
    cur_thread = ctypes.windll.kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(cur_thread, fg_thread, True)
    try:
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        user32.AttachThreadInput(cur_thread, fg_thread, False)
    time.sleep(0.4)


# --------------------------------------------------------------------------
# pixels + OCR: focus is proven from the screen, never from a title alone.
# --------------------------------------------------------------------------

def screenshot_region(path: Path, rect: tuple[int, int, int, int] | None = None) -> Path:
    from PIL import ImageGrab  # noqa  -- preferred when present
    img = ImageGrab.grab(bbox=rect) if rect else ImageGrab.grab()
    img.save(path)
    return path


def screenshot_region_net(path: Path, rect: tuple[int, int, int, int] | None = None) -> Path:
    """Fallback pixel path: the same screen-DC route as sys_screenshot.py."""
    if rect:
        x, y, r, b = rect
        w, h = r - x, b - y
    else:
        x = y = 0
        w = user32.GetSystemMetrics(78)
        h = user32.GetSystemMetrics(79)
    ps = (f"Add-Type -AssemblyName System.Windows.Forms;"
          f"Add-Type -AssemblyName System.Drawing;"
          f"$b=New-Object System.Drawing.Bitmap({w},{h});"
          f"$g=[System.Drawing.Graphics]::FromImage($b);"
          f"$g.CopyFromScreen({x},{y},0,0,$b.Size);"
          f"$b.Save('{path}');$g.Dispose();$b.Dispose()")
    done = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=120, check=False)
    if done.returncode != 0 or not path.exists():
        raise RuntimeError(f"pixel capture failed: {done.stderr.strip()[-200:]}")
    return path


def grab(path: Path, rect=None) -> Path:
    try:
        return screenshot_region(path, rect)
    except ImportError:
        return screenshot_region_net(path, rect)


def ocr_text(image: Path) -> str:
    tesseract = shutil.which("tesseract")
    if not tesseract:
        raise RuntimeError("tesseract binary not found — Rule 2 cannot be met")
    done = subprocess.run([tesseract, str(image), "stdout", "--psm", "6"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=120, check=False)
    if done.returncode != 0:
        raise RuntimeError(f"tesseract failed: {done.stderr.strip()[-200:]}")
    return done.stdout


def focus_proven(target: str, evidence_dir: Path) -> tuple[bool, str]:
    """Rule 2: foreground title AND OCR of the top strip must name the target."""
    title = foreground_title()
    if target.lower() not in title.lower():
        return False, f"foreground title {title!r} does not name {target!r}"
    shot = grab(evidence_dir / f"focus_{int(time.time())}.png")
    try:
        text = ocr_text(shot)
    except RuntimeError as exc:
        return False, str(exc)
    top = "\n".join(text.splitlines()[:8])
    if target.lower() not in top.lower():
        return False, (f"title matched but pixels do not: top strip lacks {target!r} "
                       f"(see {shot.name})")
    return True, f"title + pixels agree on {target!r} ({shot.name})"


# --------------------------------------------------------------------------
# actions — each burst re-proves focus first (Rule 2), aborts otherwise (Rule 3)
# --------------------------------------------------------------------------

def do_click(x: int, y: int) -> None:
    user32.SetCursorPos(x, y)
    time.sleep(0.15)
    flags_down, flags_up = 0x0002, 0x0004
    _send(INPUT(type=INPUT_MOUSE,
                u=INPUT._U(mi=MOUSEINPUT(x, y, 0, flags_down, 0, None))))
    _send(INPUT(type=INPUT_MOUSE,
                u=INPUT._U(mi=MOUSEINPUT(x, y, 0, flags_up, 0, None))))


def do_type(text: str) -> None:
    for char in text:
        vk = user32.VkKeyScanW(ord(char)) & 0xFF
        _send(_key(vk, True), _key(vk, False))
        time.sleep(0.01)


def do_hotkey(*names: str) -> None:
    vks = []
    for name in names:
        key = name.lower()
        if key in VK:
            vks.append(VK[key])
        elif len(key) == 1:
            vks.append(ord(key.upper()))
        else:
            raise ValueError(f"unknown key {name!r}")
    for vk in vks:
        _send(_key(vk, True))
    for vk in reversed(vks):
        _send(_key(vk, False))


def run_plan(target: str, actions: list[str], evidence_dir: Path) -> int:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    minimized = minimize_all(set())
    print(f"minimized {len(minimized)} window(s); restoring at end", flush=True)
    try:
        candidates = [w for w in list_windows() if target.lower() in w["title"].lower()]
        if not candidates:
            print(f"no window names {target!r} — aborting before any input", flush=True)
            return 3
        bring_to_front(candidates[0]["hwnd"])
        for step in actions:
            ok, proof = focus_proven(target, evidence_dir)
            print(f"focus: {proof}", flush=True)
            if not ok:
                print("FOCUS LOST — aborting per Rule 3, captures kept", flush=True)
                return 3
            parts = step.split()
            verb = parts[0].lower()
            if verb == "click":
                do_click(int(parts[1]), int(parts[2]))
            elif verb == "type":
                do_type(" ".join(parts[1:]))
            elif verb == "hotkey":
                do_hotkey(*parts[1:])
            elif verb == "wait":
                time.sleep(float(parts[1]))
            else:
                print(f"unknown action {verb!r} — aborting", flush=True)
                return 3
            grab(evidence_dir / f"after_{int(time.time())}.png")
        print(f"plan complete; evidence in {evidence_dir}", flush=True)
        return 0
    finally:
        restore_all(minimized)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Safe synthetic GUI input, gated by pixels.")
    parser.add_argument("--probe", action="store_true", help="list windows only; touch nothing")
    parser.add_argument("--plan", default="", help="target window substring")
    parser.add_argument("--do", default="", help="';'-separated actions (plan only without --confirm-live)")
    parser.add_argument("--confirm-live", action="store_true", help="actually press, move, type")
    args = parser.parse_args(argv)

    if args.probe or (not args.plan and not args.do):
        print(f"dpi-aware: {DPI_AWARE}{' -- ' + DPI_NOTE if DPI_NOTE else ''}")
        for win in list_windows():
            if win["title"].strip():
                print(f"{win['hwnd']:>10}  {win['rect']}  {win['title'][:80]}")
        return 0

    actions = [s.strip() for s in args.do.split(";") if s.strip()]
    if not actions:
        print("gui_act: nothing to do (empty --do)", file=sys.stderr)
        return 2
    if not args.confirm_live:
        print(f"PLAN for {args.plan!r} (nothing pressed, moved, or typed):")
        for step in actions:
            print(f"  - {step}")
        print("re-run with --confirm-live to execute under the Rule 1-5 harness")
        return 0
    return run_plan(args.plan, actions, EVIDENCE / datetime.now().strftime("%Y%m%dT%H%M%S"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
