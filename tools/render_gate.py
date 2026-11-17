#!/usr/bin/env python
"""tools/render_gate.py -- the gate the five savers did not have.

Why this file exists
--------------------
On 2026-11-16 five 1920x1080 savers were rendered to mp4. Every check that
mattered was performed by hand, five times: the frame count, the frame rate, the
duration, and whether a decoded frame was actually the saver's colour or a black
canvas. Two of those hand-checks found real defects (a resize that cleared the
canvas; a clip that drew a frame in 18.8 s), and neither defect had an instrument
-- they were found by looking. A tree that can only find defects by looking finds
them once.

The four faces below are the four things that were done by hand:

  contract <html>...   static: does the saver declare the five-point capture
                       contract (a saver missing the resize guard renders BLACK)
  pilot <html>         measured: what will this render cost, which renderer is
                       actually rasterizing, and does the first frame have
                       pixels in it -- asked BEFORE the long job. A projection
                       taken on SwiftShader is 31.5x the truth (measured
                       2026-11-16), so software raster is a finding, not a note.
  verify <mp4>...      measured: frames / fps / duration / decoded colour against
                       stated expectations
  ratchet [<mp4>...]   the baseline of verified clips, so a regeneration that
                       changes a reading is visible instead of silent

Exit codes, matching the tree's convention
------------------------------------------
  0  ran, and no finding
  1  ran, and found something (for `ratchet`: only under --strict -- baseline
     drift is debt, and a gate red on day one is a gate someone switches off)
  2  could not run (no ffmpeg, no node, no puppeteer, unreadable file).
     A reading that was not taken is never a pass.

What the static contract face cannot do
---------------------------------------
It reads text. A guard that is present but compares the wrong thing passes it.
`pilot` is the measured version of the same question -- it loads the page in the
same Chrome the renderer uses and reports whether `__step` is a real function and
what the first frame's pixels actually are. Run both; believe `pilot`.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "tools" / "capture_yggdrasil.js"
DEFAULT_BASELINE = ROOT / "logs" / "render_gate_baseline.json"

EXIT_OK, EXIT_FINDING, EXIT_CANNOT = 0, 1, 2

# A decode or a probe is seconds of work. This is not a performance knob: it is
# the difference between a gate that reports and a gate that never returns.
BIN_TIMEOUT_S = 120.0
PILOT_TIMEOUT_S = 900.0  # N frames + one PNG; a 300-frame forecast is minutes

# The contract every saver must carry to be capturable at a fixed rate.
# Each entry is (name, pattern, why). Order is the order they are checked.
CONTRACT = [
    ("capture flag", r"window\.__capture",
     "reads window.__capture so the timeline steps instead of the clock"),
    ("timeline total", r"window\.__TOTAL\s*=",
     "declares the timeline length the driver turns into a frame count"),
    ("step hook", r"window\.__step\s*=\s*function",
     "declares window.__step(ms), resolved after two painted frames"),
    ("same-box resize guard", r"if\s*\(\s*[A-Za-z_$][\w$]*\s*===?\s*(?:cv|canvas)\.width",
     "bails out BEFORE assigning canvas.width -- the assignment clears the "
     "surface even when the box is unchanged, which is what made every frame black"),
    ("last-clock repaint", r"lastMs\s*!==\s*null",
     "repaints from the last stepped clock when a resize does change the box"),
]


# --------------------------------------------------------------------------- #
# pure helpers (the tested surface -- no subprocess, no files)
# --------------------------------------------------------------------------- #
def check_contract(text: str) -> list[dict]:
    """Every contract point, with the line it was found on (1-based)."""
    lines = text.splitlines()
    out = []
    for name, pattern, why in CONTRACT:
        rx = re.compile(pattern)
        line = next((i + 1 for i, ln in enumerate(lines) if rx.search(ln)), None)
        out.append({"name": name, "ok": line is not None, "line": line, "why": why})
    return out


_RATE_RX = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(?:/\s*(\d+(?:\.\d+)?))?\s*$")


def parse_rate(value: str) -> float | None:
    """"30/1" -> 30.0. None on anything unparseable rather than guessing.

    Validated by shape, not by exception: the first version caught ValueError in
    two single-statement handlers, which the staged scanner rightly reads as a
    swallowed failure -- and in a metering helper a rate that silently became
    None is indistinguishable from a probe that failed a frame later.
    """
    m = _RATE_RX.match(value or "")
    if m is None:
        return None
    n = float(m.group(1))
    d = float(m.group(2)) if m.group(2) else 1.0
    return n / d if d else None


def mean_luma(rgb) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def luma_is_black(rgb, floor: float) -> bool:
    """A clip of a dark scene is not a black clip; the floor is per saver."""
    return mean_luma(rgb) < floor


def evaluate(readings: dict, expect: dict) -> list[dict]:
    """Compare one clip's measured readings against stated expectations.

    Pure on purpose: every case that used to need a renderer (300 frames, 30 fps,
    10 s, a colour that is not black) is a dict comparison a test can drive.
    """
    checks: list[dict] = []

    def ck(name, ok, got, want):
        checks.append({"name": name, "ok": bool(ok), "got": got, "want": want})

    if expect.get("frames") is not None:
        ck("frames", readings.get("frames") == expect["frames"],
           readings.get("frames"), expect["frames"])
    if expect.get("fps") is not None:
        fps = readings.get("fps")
        ck("fps", fps is not None and abs(fps - expect["fps"]) < 0.01,
           fps, expect["fps"])
    if expect.get("seconds") is not None:
        secs = readings.get("seconds")
        ck("seconds", secs is not None and abs(secs - expect["seconds"]) < 0.02,
           None if secs is None else round(secs, 6), expect["seconds"])
    if expect.get("size") is not None:
        ck("size", readings.get("size") == expect["size"], readings.get("size"),
           expect["size"])
    rgb = readings.get("rgb")
    floor = expect.get("min_luma")
    if floor is not None:
        ck("not black", rgb is not None and not luma_is_black(rgb, floor),
           None if rgb is None else {"rgb": list(rgb), "luma": round(mean_luma(rgb), 2)},
           "luma >= %.1f" % floor)
    palette = expect.get("palette")
    if palette is not None:
        tol = expect.get("tol", 45)
        dist = None if rgb is None else max(abs(a - b) for a, b in zip(rgb, palette))
        ck("palette", dist is not None and dist <= tol,
           None if dist is None else {"rgb": list(rgb), "max_delta": dist},
           {"rgb": list(palette), "tol": tol})
    return checks


def judge_pilot(payload: dict, budget_s: float | None, min_luma: float,
                rgb=None, allow_software_raster: bool = False) -> list[dict]:
    """Turn a driver pilot into findings: projected cost, and is frame 1 black.

    A pilot run on SwiftShader measures the wrong job. Measured 2026-11-16 on
    ORCHID_NEBULA: 35539 ms/frame software vs 1128 ms/frame on the GPU -- the
    projection is 31.5x the truth, so a budget it passes is not a budget met.
    The renderer is recorded by the driver and checked here, because a silent
    fallback raises nothing.
    """
    checks = []
    # Three states, all recorded (HED-11): software-fail, software-waived,
    # hardware-ok. A driver that does not report the field has measured nothing,
    # so it gets no check rather than an invented pass.
    if "software_raster" in payload:
        renderer = payload.get("renderer") or "not reported"
        if not payload.get("software_raster"):
            checks.append({"name": "hardware raster", "ok": True,
                           "got": renderer, "want": "a GPU renderer"})
        elif allow_software_raster:
            checks.append({"name": "hardware raster", "ok": True,
                           "got": renderer, "want": "waived by --allow-software-raster"})
        else:
            checks.append({"name": "hardware raster", "ok": False, "got": renderer,
                           "want": "a GPU renderer (a software projection is not this job)"})
    proj = payload.get("projected_s")
    if budget_s is not None:
        checks.append({
            "name": "projected <= budget", "ok": proj is not None and proj <= budget_s,
            "got": None if proj is None else round(proj, 1), "want": budget_s,
        })
    if not payload.get("contract", {}).get("step"):
        checks.append({"name": "step hook (live)", "ok": False, "got": "missing",
                       "want": "typeof window.__step === 'function'"})
    else:
        checks.append({"name": "step hook (live)", "ok": True, "got": "function",
                       "want": "typeof window.__step === 'function'"})
    if rgb is None:
        checks.append({"name": "first frame has pixels", "ok": False,
                       "got": "no sample png measured", "want": "luma >= %.1f" % min_luma})
    else:
        checks.append({
            "name": "first frame has pixels",
            "ok": not luma_is_black(rgb, min_luma),
            "got": {"rgb": list(rgb), "luma": round(mean_luma(rgb), 2)},
            "want": "luma >= %.1f" % min_luma,
        })
    return checks


def compare_baseline(baseline: dict, current: dict, tol: int = 45) -> list[dict]:
    """Drift between a recorded clip reading and a freshly measured one.

    Returns drift ONLY -- an empty list means every clip still reads what the
    baseline recorded. The first version also returned a colour check that had
    passed, which made "nothing moved" unrepresentable (`== []` was impossible)
    and would have made the summary count drift it did not have.
    """
    findings = []
    for clip, now in current.items():
        was = baseline.get(clip)
        if was is None:
            findings.append({"name": "new clip", "clip": clip, "ok": False,
                             "got": "not in baseline", "want": "a recorded reading"})
            continue
        for key in ("frames", "fps", "seconds", "size"):
            if was.get(key) != now.get(key):
                findings.append({"name": key, "clip": clip, "ok": False,
                                 "got": now.get(key), "want": was.get(key)})
        if was.get("rgb") and now.get("rgb"):
            dist = max(abs(a - b) for a, b in zip(was["rgb"], now["rgb"]))
            if dist > tol:
                findings.append({"name": "colour", "clip": clip, "ok": False,
                                 "got": {"rgb": now["rgb"], "max_delta": dist},
                                 "want": {"rgb": was["rgb"], "tol": tol}})
    return findings


# --------------------------------------------------------------------------- #
# measured faces (subprocess)
# --------------------------------------------------------------------------- #
def _run(cmd: list[str], binary: str) -> tuple[bool, bytes, str]:
    """One bounded child. A probe that outlives BIN_TIMEOUT_S is wedged, not
    slow -- an unbounded run here is how a gate hangs forever instead of
    reporting, and a gate that never returns protects nothing."""
    if shutil.which(binary) is None:
        return False, b"", "%s not on PATH" % binary
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=BIN_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        msg = "%s exceeded the %.0fs bound" % (binary, BIN_TIMEOUT_S)
        return False, b"", msg
    err = r.stderr.decode("utf-8", "replace").strip()
    return r.returncode == 0, r.stdout, err


def probe_clip(path: Path) -> tuple[dict | None, str]:
    """ffprobe -> readings. Frame count comes from --count_frames, never nb_frames:
    a container header can state a count its stream does not hold."""
    ok, out, err = _run([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries",
        "stream=width,height,r_frame_rate,nb_read_frames:format=duration,size",
        "-of", "json", str(path),
    ], "ffprobe")
    if not ok:
        return None, err or "ffprobe failed"
    try:
        data = json.loads(out.decode("utf-8", "replace") or "{}")
    except json.JSONDecodeError as exc:
        return None, "ffprobe json: %s" % exc
    streams = data.get("streams") or []
    if not streams:
        return None, "no video stream"
    s, fmt = streams[0], data.get("format") or {}
    try:
        frames = int(s.get("nb_read_frames"))
    except (TypeError, ValueError):
        return None, "nb_read_frames missing (a header count is not a reading)"
    return {
        "frames": frames,
        "fps": parse_rate(s.get("r_frame_rate", "")),
        "seconds": float(fmt["duration"]) if fmt.get("duration") else None,
        "size": "%sx%s" % (s.get("width"), s.get("height")),
        "bytes": int(fmt["size"]) if fmt.get("size") else None,
    }, ""


def frame_rgb(path: Path, at_seconds: float) -> tuple[tuple[int, int, int] | None, str]:
    """Decode one frame and reduce it to its mean colour (scale=1:1 + rgb24)."""
    ok, out, err = _run([
        "ffmpeg", "-v", "error", "-ss", "%.3f" % at_seconds, "-i", str(path),
        "-frames:v", "1", "-vf", "scale=1:1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ], "ffmpeg")
    if not ok:
        return None, err or "ffmpeg failed"
    if len(out) < 3:
        return None, "ffmpeg decoded %d bytes, expected 3" % len(out)
    return (out[0], out[1], out[2]), ""


def read_rgb(path: Path) -> tuple[tuple[int, int, int] | None, str]:
    ok, out, err = _run([
        "ffmpeg", "-v", "error", "-i", str(path), "-vf", "scale=1:1",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ], "ffmpeg")
    if not ok:
        return None, err or "ffmpeg failed"
    return ((out[0], out[1], out[2]) if len(out) >= 3 else None), ""


# --------------------------------------------------------------------------- #
# faces
# --------------------------------------------------------------------------- #
def face_contract(paths: list[Path]) -> int:
    bad = 0
    for p in paths:
        if not p.exists():
            print("COULD NOT RUN  %s -- no such file" % p)
            return EXIT_CANNOT
        checks = check_contract(p.read_text(encoding="utf-8", errors="replace"))
        missed = [c for c in checks if not c["ok"]]
        bad += 1 if missed else 0
        print("%s  %s" % ("PASS" if not missed else "FAIL", p.name))
        for c in checks:
            print("  [%s] %-24s %s%s" % (
                "PASS" if c["ok"] else "MISSING", c["name"],
                "line %s" % c["line"] if c["ok"] else "",
                "" if c["ok"] else " -- " + c["why"]))
    print("-" * 72)
    print("  %d of %d savers carry the full contract" % (len(paths) - bad, len(paths)))
    return EXIT_FINDING if bad else EXIT_OK


def face_verify(paths: list[Path], expect: dict) -> int:
    bad = 0
    for p in paths:
        if not p.exists():
            print("COULD NOT RUN  %s -- no such file" % p)
            return EXIT_CANNOT
        readings, err = probe_clip(p)
        if readings is None:
            print("COULD NOT RUN  %s -- %s" % (p.name, err))
            return EXIT_CANNOT
        at = (readings.get("seconds") or 0) / 2
        rgb, rgb_err = frame_rgb(p, at)
        if rgb is None:
            print("COULD NOT RUN  %s -- mid frame: %s" % (p.name, rgb_err))
            return EXIT_CANNOT
        readings["rgb"] = rgb
        checks = evaluate(readings, expect)
        missed = [c for c in checks if not c["ok"]]
        bad += 1 if missed else 0
        print("%s  %s" % ("PASS" if not missed else "FAIL", p.name))
        for c in checks:
            print("  [%s] %-11s got=%s want=%s" % (
                "PASS" if c["ok"] else "FAIL", c["name"], c["got"], c["want"]))
        print("  ...  %s frames @ %s fps, %s s, %s" % (
            readings["frames"], readings["fps"],
            None if readings["seconds"] is None else round(readings["seconds"], 3),
            readings["size"]))
    print("-" * 72)
    print("  %d of %d clips verified" % (len(paths) - bad, len(paths)))
    return EXIT_FINDING if bad else EXIT_OK


def face_pilot(html: Path, frames: int, fps: int, budget_s: float,
               min_luma: float, keep_shot: bool,
               allow_software_raster: bool = False) -> int:
    if shutil.which("node") is None:
        print("COULD NOT RUN  node is not on PATH")
        return EXIT_CANNOT
    if not DRIVER.exists():
        print("COULD NOT RUN  driver missing: %s" % DRIVER)
        return EXIT_CANNOT
    shot = html.with_suffix(".pilot.png")
    try:
        r = subprocess.run(
            ["node", str(DRIVER), "--pilot", str(html),
             "--frames", str(frames), "--fps", str(fps), "--shot", str(shot)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=PILOT_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print("COULD NOT RUN  pilot exceeded %.0fs" % PILOT_TIMEOUT_S)
        return EXIT_CANNOT
    line = next((ln for ln in (r.stdout or "").splitlines()
                 if ln.startswith("PILOT ")), None)
    if line is None:
        print("COULD NOT RUN  driver printed no PILOT line (exit %s)" % r.returncode)
        detail = (r.stderr or r.stdout or "").strip().splitlines()
        if detail:
            print("  " + detail[-1])
        return EXIT_CANNOT
    payload = json.loads(line[len("PILOT "):])
    rgb = None
    if shot.exists():
        rgb, _ = read_rgb(shot)
    checks = judge_pilot(payload, budget_s, min_luma, rgb, allow_software_raster)
    missed = [c for c in checks if not c["ok"]]
    print("%s  pilot %s" % ("PASS" if not missed else "FAIL", html.name))
    print("  raster: %s" % (payload.get("renderer") or "not reported"))
    print("  canvas %s, timeline %s ms -> %s frames @ %s fps" % (
        payload.get("canvas"), payload.get("total_timeline_ms"),
        payload.get("planned_frames"), payload.get("fps")))
    print("  per frame: step %s ms + shot %s ms = %s ms  (%s samples)" % (
        payload.get("step_ms"), payload.get("shot_ms"), payload.get("ms_per_frame"),
        len(payload.get("samples") or [])))
    for c in checks:
        print("  [%s] %-22s got=%s want=%s" % (
            "PASS" if c["ok"] else "FAIL", c["name"], c["got"], c["want"]))
    if not keep_shot and shot.exists():
        shot.unlink()
    print("-" * 72)
    return EXIT_FINDING if missed else EXIT_OK


def face_ratchet(paths: list[Path], baseline_path: Path, write: bool,
                 strict: bool, tol: int) -> int:
    current = {}
    for p in paths:
        readings, err = probe_clip(p)
        if readings is None:
            print("COULD NOT RUN  %s -- %s" % (p.name, err))
            return EXIT_CANNOT
        rgb, err = frame_rgb(p, (readings.get("seconds") or 0) / 2)
        if rgb is None:
            print("COULD NOT RUN  %s -- mid frame: %s" % (p.name, err))
            return EXIT_CANNOT
        readings["rgb"] = list(rgb)
        readings["verified_at"] = _dt.datetime.now().isoformat(timespec="seconds")
        current[str(p)] = readings
    baseline = {}
    if baseline_path.exists():
        try:
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print("COULD NOT RUN  baseline unreadable: %s" % exc)
            return EXIT_CANNOT
    if write:
        baseline.update(current)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(baseline, indent=1, sort_keys=True),
                                 encoding="utf-8")
        print("WROTE  %s -- %d clip(s) recorded" % (baseline_path, len(current)))
        return EXIT_OK
    findings = compare_baseline(baseline, current, tol)
    for f in findings:
        print("  [DRIFT] %-8s %s" % (f["name"], Path(f["clip"]).name))
        print("          got=%s want=%s" % (f["got"], f["want"]))
    print("-" * 72)
    drift = findings
    print("  %d of %d clips match the baseline" % (
        len(current) - len({f["clip"] for f in drift}), len(current)))
    if drift and strict:
        return EXIT_FINDING
    return EXIT_OK


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="render_gate.py",
        description="Contract, pilot, verify and ratchet for fixed-rate renders.",
        epilog="exit 0 ran clean, 1 found something, 2 could not run")
    sub = ap.add_subparsers(dest="face", required=True)

    c = sub.add_parser("contract", help="static check of the five-point saver contract")
    c.add_argument("html", nargs="+")

    v = sub.add_parser("verify", help="measured check of a rendered clip")
    v.add_argument("mp4", nargs="+")
    v.add_argument("--frames", type=int, default=300)
    v.add_argument("--fps", type=float, default=30.0)
    v.add_argument("--seconds", type=float, default=10.0)
    v.add_argument("--size", default="1920x1080")
    v.add_argument("--min-luma", type=float, default=8.0)
    v.add_argument("--palette", default=None,
                   help="R,G,B the enabled palette should average to")
    v.add_argument("--tol", type=int, default=45)

    p = sub.add_parser("pilot", help="measure cost and first-frame pixels before rendering")
    p.add_argument("html")
    p.add_argument("--frames", type=int, default=5)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--budget", type=float, default=1800.0,
                   help="seconds the full render may be projected to take")
    p.add_argument("--min-luma", type=float, default=8.0)
    p.add_argument("--keep-shot", action="store_true")
    p.add_argument("--allow-software-raster", action="store_true",
                   help="accept a SwiftShader projection (31x slow, measured) -- say why in the report")

    r = sub.add_parser("ratchet", help="record or compare the verified-clip baseline")
    r.add_argument("mp4", nargs="*")
    r.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    r.add_argument("--write", action="store_true")
    r.add_argument("--strict", action="store_true")
    r.add_argument("--tol", type=int, default=45)

    args = ap.parse_args(argv)

    if args.face == "contract":
        return face_contract([Path(x) for x in args.html])
    if args.face == "verify":
        palette = None
        if args.palette:
            try:
                palette = tuple(int(x) for x in args.palette.split(","))
            except ValueError:
                print("COULD NOT RUN  --palette wants R,G,B")
                return EXIT_CANNOT
            if len(palette) != 3:
                print("COULD NOT RUN  --palette wants R,G,B")
                return EXIT_CANNOT
        expect = {"frames": args.frames, "fps": args.fps, "seconds": args.seconds,
                  "size": args.size, "min_luma": args.min_luma,
                  "palette": palette, "tol": args.tol}
        return face_verify([Path(x) for x in args.mp4], expect)
    if args.face == "pilot":
        return face_pilot(Path(args.html), args.frames, args.fps, args.budget,
                          args.min_luma, args.keep_shot,
                          args.allow_software_raster)
    if args.face == "ratchet":
        paths = [Path(x) for x in args.mp4]
        if not paths and not args.write:
            print("COULD NOT RUN  ratchet needs at least one clip to compare")
            return EXIT_CANNOT
        if args.write and not paths:
            print("COULD NOT RUN  --write needs the clips to record")
            return EXIT_CANNOT
        return face_ratchet(paths, Path(args.baseline), args.write, args.strict,
                            args.tol)
    return EXIT_CANNOT


if __name__ == "__main__":
    sys.exit(main())
