#!/usr/bin/env python3
r"""Compile the Vulcan-salute SVGs into Windows .cur/.ani and install a scheme.

The SVG masters are the source of truth; this only rasterises them (headless
Chrome, transparent background — the same renderer that produced the on-screen
swarm page) and packs the pixels into the containers Windows loads.

No third-party libraries: PNG is decoded and the ICO/CUR/RIFF-ACON containers
are written with struct+zlib, because the production interpreter (3.16t) has
neither Pillow nor cairosvg.

  python make_cursors.py --build            # out/cursors/*.cur, *.ani, preview.png
  python make_cursors.py --install          # copy into %LOCALAPPDATA%\...\Cursors
  python make_cursors.py --apply            # install + switch the live pointers
  python make_cursors.py --restore          # put the saved pointers back
  python make_cursors.py --uninstall        # remove files + scheme entry

Every file is verified before it is offered: Windows must hand back a non-null
HCURSOR from LoadCursorFromFileW, and a file that fails is reported, never
quietly installed.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile
import winreg
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
CURSORS = os.path.join(HERE, "cursors")
OUT = os.path.join(HERE, "out", "cursors")
CHROME_CANDIDATES = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
)
CURSOR_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft",
                          "Windows", "Cursors")
SCHEME_DIR = os.path.join(CURSOR_DIR, "vulcan-swarm")
SCHEME_NAME = "Vulcan Swarm"
CURSORS_KEY = r"Control Panel\Cursors"

# The 15 scheme slots, in the order Windows writes them.
SLOTS = ("Arrow", "Help", "AppStarting", "Wait", "Crosshair", "IBeam", "NWPen",
         "No", "SizeNS", "SizeWE", "SizeNWSE", "SizeNESW", "SizeAll", "UpArrow",
         "Hand")

# One animation frame per entry, in degrees, sampled from the CSS keyframes the
# on-screen page uses (0%%, 32%%, 66%%, 100%%) at eight steps and then widened.
# At the previous +/-6 degrees the palm travelled 3.05 px at 32 px, 10% of the
# glyph's ink height, which the eye reads as a tremble rather than a wave. At
# +/-14 it travels 6.24 px, 24% -- measured from the built frames, not predicted.
# The cost is that the arc no longer fits a 32 px tile by any placement: the
# union of the eight rotated ink boxes is 37.3 x 35.2 units against 32, because
# the glyph hangs 27 units below a pivot two units under its top. So the frames
# are rasterised on a larger canvas and box-filtered down -- widening the wave
# is a size problem before it is an animation problem.
WAVE = (0.0, -9.0, -14.0, -9.5, 0.0, 9.5, 13.5, 6.5)
JIF = 6  # frame duration in 1/60 s -> 100 ms per frame
BUSY_PX = 32       # the size the .ani ships as
BUSY_CANVAS = 96   # supersampled raster: an exact 3:1 box filter reduces it
BUSY_MARGIN = 2    # canvas pixels kept clear on every side of the arc

# ── the remaining slots, composed from the one master ────────────────────
#
# Windows asks for fifteen pointers and the salute ships two masters, so the
# other slots are composed here rather than drawn again: each is the same
# 32 px glyph moved, turned or hollowed inside a single 32-unit viewBox. Draw
# the master once and every salute slot follows it.
#
# GLYPH_CENTRE is the measured ink centre of vulcan_salute_32.svg (ink spans
# x 0..25, y 1..29), so a turn rotates the hand about itself instead of
# sweeping it out of the tile. A layer is (angle, dx, dy, scale): the glyph
# centre lands at (16+dx, 16+dy), scaled, then turned `angle` degrees
# clockwise. `hotspot` is "layer" when one hand carries the point (follow the
# master's own tip through the same matrix) and "centre" when the slot is
# symmetric and no single hand owns the click.
GLYPH_CENTRE = (12.5, 15.0)

DERIVED = (
    # Inverted salute: text wants a pointer that cannot be mistaken for the
    # arrow, and the fingertip down reads as one at a glance.
    dict(slot="IBeam", file="vulcan-text.cur", label="text (inverted)",
         layers=((180.0, 0.0, 0.0, 1.0),), hotspot="layer"),
    dict(slot="SizeAll", file="vulcan-move.cur", label="move (four ways)",
         layers=((0.0, 0.0, -7.0, 0.42), (90.0, 7.0, 0.0, 0.42),
                 (180.0, 0.0, 7.0, 0.42), (270.0, -7.0, 0.0, 0.42)),
         hotspot="centre"),
    dict(slot="SizeNS", file="vulcan-ns.cur", label="resize N-S",
         layers=((0.0, 0.0, -7.5, 0.48), (180.0, 0.0, 7.5, 0.48)),
         hotspot="centre"),
    dict(slot="SizeWE", file="vulcan-we.cur", label="resize E-W",
         layers=((90.0, 7.5, 0.0, 0.48), (270.0, -7.5, 0.0, 0.48)),
         hotspot="centre"),
    # One hand, not two, on the diagonals: a hand turned 45 degrees occupies a
    # diagonal band 39/32 of the tile wide, so a pair can only fit by shrinking
    # until the finger notch closes and the two merge into one smear (measured
    # at 0.40 shared scale). The single hand keeps its notch, and its fingertip
    # names the corner the resize runs toward.
    dict(slot="SizeNWSE", file="vulcan-nwse.cur", label="resize NW-SE",
         layers=((315.0, 0.0, 0.0, 0.66),), hotspot="centre"),
    dict(slot="SizeNESW", file="vulcan-nesw.cur", label="resize NE-SW",
         layers=((45.0, 0.0, 0.0, 0.66),), hotspot="centre"),
    # Unavailable: the same white hand every other slot uses, with a bar
    # through it. An outline-only hand was measured first and discarded: empty
    # of fill it keeps no silhouette at 16 px, so the slot read as a crossed-out
    # box rather than a crossed-out salute.
    dict(slot="No", file="vulcan-no.cur", label="unavailable",
         layers=((0.0, 0.0, 0.0, 1.0),), hotspot="layer", slash=True),
)

# Windows scheme slot -> the container installed for it. One table, because
# install and apply disagreeing about a slot is a pointer that changes on the
# scheme you save and not on the one you switch to.
PROGRAMS = {
    "Arrow": "vulcan-arrow.cur",
    "Hand": "vulcan-hand.cur",
    "AppStarting": "vulcan-busy.ani",
    "Wait": "vulcan-busy.ani",
}
for _spec in DERIVED:
    PROGRAMS[_spec["slot"]] = _spec["file"]


# ── png in, rgba out ─────────────────────────────────────────────────────

def decode_png(data):
    """(width, height, RGBA bytes). 8-bit, non-interlaced, as Chrome writes it."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("make_cursors: not a PNG")
    pos, idat, w = 8, [], None
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            w, h, depth, ctype, _comp, _filt, interlace = struct.unpack(
                ">IIBBBBB", body)
            if depth != 8 or interlace:
                raise SystemExit("make_cursors: PNG is %d-bit/interlaced" % depth)
        elif tag == b"IDAT":
            idat.append(body)
        elif tag == b"IEND":
            break
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(ctype)
    if channels is None:
        raise SystemExit("make_cursors: PNG colour type %d unsupported" % ctype)
    raw = zlib.decompress(b"".join(idat))
    stride = w * channels
    prev = bytearray(stride)
    rgba = bytearray(w * h * 4)
    p = 0
    for y in range(h):
        filt = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if filt == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif filt == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif filt == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif filt == 4:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                upleft = prev[i - channels] if i >= channels else 0
                up = prev[i]
                est = left + up - upleft
                pa, pb, pc = abs(est - left), abs(est - up), abs(est - upleft)
                pred = left if (pa <= pb and pa <= pc) else (up if pb <= pc else upleft)
                line[i] = (line[i] + pred) & 0xFF
        elif filt != 0:
            raise SystemExit("make_cursors: PNG filter %d unknown" % filt)
        for x in range(w):
            src = x * channels
            dst = (y * w + x) * 4
            if channels == 4:
                rgba[dst:dst + 4] = line[src:src + 4]
            elif channels == 3:
                rgba[dst:dst + 3] = line[src:src + 3]
                rgba[dst + 3] = 255
            elif channels == 1:
                rgba[dst] = rgba[dst + 1] = rgba[dst + 2] = line[src]
                rgba[dst + 3] = 255
            else:
                rgba[dst] = rgba[dst + 1] = rgba[dst + 2] = line[src]
                rgba[dst + 3] = line[src + 1]
        prev = line
    return w, h, bytes(rgba)


def encode_png(w, h, rgba):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgba[y * w * 4:(y + 1) * w * 4]

    def chunk(tag, body):
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ── rasterise the masters ────────────────────────────────────────────────

def chrome():
    for path in CHROME_CANDIDATES:
        if os.path.exists(path):
            return path
    raise SystemExit("make_cursors: Chrome not found; the SVG masters need a "
                     "rasteriser and PIL/cairosvg are absent from this venv")


def rasterise(svg_markup, native, hotspot, target, angles, workdir,
              offset=(0.0, 0.0), glyph=None):
    """One screenshot of N tiles -> N RGBA frames at `target` px.

    `offset` is where the glyph's box sits inside its tile, in target pixels,
    and `glyph` is how large that box is drawn (the whole tile by default). A
    swinging frame needs headroom the tile does not have, and no later pass can
    put back pixels the renderer cut, so the busy frames are drawn smaller than
    their canvas; the hotspot moves with the glyph so the reported point stays
    on the salute tip.
    """
    box = float(target if glyph is None else glyph)
    scale = box / float(native)
    ox = hotspot[0] * scale
    oy = hotspot[1] * scale
    tiles = "".join(
        '<div class="tile"><div class="rot" style="transform:rotate(%.2fdeg)">%s</div></div>'
        % (a, svg_markup) for a in angles)
    page = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:transparent;overflow:hidden}
.tile{width:%dpx;height:%dpx;position:relative;overflow:hidden;float:left}
.rot{position:absolute;left:%.3fpx;top:%.3fpx;width:%.3fpx;height:%.3fpx;
     transform-origin:%.4fpx %.4fpx}
.rot svg{display:block;width:%.3fpx;height:%.3fpx}
</style></head><body>%s</body></html>""" % (
        target, target, offset[0], offset[1], box, box, ox, oy,
        box, box, tiles)
    html = os.path.join(workdir, "r%d.html" % target)
    png = os.path.join(workdir, "r%d.png" % target)
    with open(html, "w", encoding="utf-8") as fh:
        fh.write(page)
    cmd = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", "--default-background-color=00000000",
           "--virtual-time-budget=1500",
           "--window-size=%d,%d" % (target * len(angles), target),
           "--screenshot=%s" % png, "file:///" + html.replace("\\", "/")]
    subprocess.run(cmd, check=True, capture_output=True, timeout=90)
    w, _h, rgba = decode_png(open(png, "rb").read())
    if w < target * len(angles):
        raise SystemExit("make_cursors: %d px tile run came back %d px wide"
                         % (target, w))
    frames = []
    for i in range(len(angles)):
        x0 = i * target
        frame = bytearray(target * target * 4)
        for y in range(target):
            row = (y * w + x0) * 4
            frame[y * target * 4:(y + 1) * target * 4] = rgba[row:row + target * 4]
        frames.append(bytes(frame))
    return frames


def alpha_bbox(rgba, size):
    """(x0, y0, x1, y1) of the painted pixels, right/bottom exclusive.

    Measured from a frame the renderer produced rather than from a box someone
    wrote down while reading the drawing: the wave layout is only as honest as
    the ink it was told to fit.
    """
    xs, ys = [], []
    for y in range(size):
        row = y * size * 4
        for x in range(size):
            if rgba[row + x * 4 + 3]:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise SystemExit("make_cursors: a rendered frame is blank")
    return (float(min(xs)), float(min(ys)),
            float(max(xs) + 1), float(max(ys) + 1))


def wave_layout(ink, hotspot, angles, canvas, margin, native):
    """Glyph size, translate and hotspot for a swing too wide to sit in a tile.

    The pivot is two units below the top of the glyph and the ink is flush left,
    so a wide swing throws pixels out on three sides at once. This solves for
    the largest square glyph whose whole arc fits `canvas` with `margin` to
    spare, returns the translate that centres that arc, and the hotspot that
    rides with the glyph. Returns (glyph_px, (left, top), (hotspot_x, hotspot_y))
    with the last pair already in canvas pixels.
    """
    x0, y0, x1, y1 = ink
    px, py = hotspot
    xs, ys = [], []
    for angle in angles:
        rad = math.radians(angle)
        cos, sin = math.cos(rad), math.sin(rad)
        for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            dx, dy = x - px, y - py
            xs.append(px + dx * cos - dy * sin)
            ys.append(py + dx * sin + dy * cos)
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    scale = (canvas - 2.0 * margin) / span
    off = (canvas / 2.0 - scale * (min(xs) + max(xs)) / 2.0,
           canvas / 2.0 - scale * (min(ys) + max(ys)) / 2.0)
    return native * scale, off, (off[0] + scale * px, off[1] + scale * py)


def assert_unclipped(frame, size, angle):
    """A frame whose outer ring carries ink was cut by the renderer, not by art."""
    ring = [frame[(size - 1) * size * 4 + i * 4 + 3] for i in range(size)]
    ring += [frame[i * size * 4 + 3] for i in range(size)]
    ring += [frame[(i * size + size - 1) * 4 + 3] for i in range(size)]
    ring += [frame[i * 4 + 3] for i in range(size)]
    if any(ring):
        raise SystemExit("make_cursors: the %+.1f degree busy frame reaches its "
                         "canvas edge; raise BUSY_MARGIN or lower WAVE" % angle)


def downsample(rgba, src, dst):
    """Exact integer box filter, alpha-weighted so edges keep their colour."""
    if src % dst or src < dst:
        raise SystemExit("make_cursors: %d -> %d is not an integer box filter"
                         % (src, dst))
    k = src // dst
    area = k * k
    out = bytearray(dst * dst * 4)
    for y in range(dst):
        for x in range(dst):
            r = g = b = a = 0
            for yy in range(y * k, y * k + k):
                row = yy * src
                for xx in range(x * k, x * k + k):
                    o = (row + xx) * 4
                    al = rgba[o + 3]
                    if al:
                        r += rgba[o] * al
                        g += rgba[o + 1] * al
                        b += rgba[o + 2] * al
                        a += al
            o = (y * dst + x) * 4
            if a:
                out[o], out[o + 1], out[o + 2], out[o + 3] = (
                    r // a, g // a, b // a, a // area)
    return bytes(out)


# ── containers ───────────────────────────────────────────────────────────

def bmp_entry(rgba, size):
    """A 32bpp bottom-up DIB plus the 1bpp AND mask legacy shells still read."""
    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, 0,
                         0, 0, 0, 0)
    pixels = bytearray()
    for y in range(size - 1, -1, -1):
        for x in range(size):
            o = (y * size + x) * 4
            r, g, b, a = rgba[o], rgba[o + 1], rgba[o + 2], rgba[o + 3]
            pixels += bytes((b, g, r, a))
    stride = ((size + 31) // 32) * 4
    mask = bytearray(stride * size)
    for y in range(size):
        for x in range(size):
            if rgba[(y * size + x) * 4 + 3] == 0:
                row = size - 1 - y
                mask[row * stride + (x >> 3)] |= 0x80 >> (x & 7)
    return header + bytes(pixels) + bytes(mask)


def cur_file(images):
    """images: [(size, hotspot_x, hotspot_y, dib_bytes)] -> .cur bytes."""
    count = len(images)
    directory, body = b"", b""
    offset = 6 + 16 * count
    for size, hx, hy, dib in images:
        directory += struct.pack("<BBBBHHII", size & 0xFF, size & 0xFF, 0, 0,
                                 hx, hy, len(dib), offset)
        body += dib
        offset += len(dib)
    return struct.pack("<HHH", 0, 2, count) + directory + body


def riff_chunk(tag, body):
    pad = b"\x00" if len(body) & 1 else b""
    return tag + struct.pack("<I", len(body)) + body + pad


def ani_file(name, frames, size, hotspot):
    """frames: list of 32bpp RGBA at `size`. Each frame is a whole .cur."""
    curs = [cur_file([(size, hotspot[0], hotspot[1], bmp_entry(f, size))])
            for f in frames]
    # iSteps must equal iFrames. The spec lets 0 mean "same as iFrames", but
    # Windows does not: measured 2026-11-14, LoadCursorFromFileW returned NULL
    # with GetLastError=87 (ERROR_INVALID_PARAMETER) for steps=0 on an
    # otherwise correct file, and loaded at once with steps=len(frames).
    anih = riff_chunk(b"anih", struct.pack("<IIIIIIIII", 36, len(curs),
                                           len(curs), size, size, 32, 1,
                                           JIF, 1))
    rate = riff_chunk(b"rate", struct.pack("<%dI" % len(curs), *([JIF] * len(curs))))
    info = riff_chunk(b"LIST", b"INFO" + riff_chunk(b"INAM", name.encode() + b"\x00"))
    fram = riff_chunk(b"LIST", b"fram" + b"".join(riff_chunk(b"icon", c) for c in curs))
    body = b"ACON" + info + anih + rate + fram
    return b"RIFF" + struct.pack("<I", len(body)) + body


# ── verify / install ─────────────────────────────────────────────────────

def windows_loads(path):
    """Non-null HCURSOR, or the reason. Absence of a handle is never a pass."""
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.LoadCursorFromFileW.argtypes = (ctypes.c_wchar_p,)
        user32.LoadCursorFromFileW.restype = ctypes.c_void_p
        handle = user32.LoadCursorFromFileW(path)
        if not handle:
            return False, "LoadCursorFromFileW error %d" % ctypes.get_last_error()
        return True, "HCURSOR 0x%x" % handle
    except OSError as exc:
        return False, "user32 unavailable: %s" % exc


def read_scheme():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY) as key:
        out = {}
        for i in range(winreg.QueryInfoKey(key)[1]):
            name, value, _kind = winreg.EnumValue(key, i)
            out[name] = value
        return out


def backup_path():
    return os.path.join(OUT, "cursors_backup.json")


def load_masters(reg):
    """{role: {size: (markup, hotspot)}} — the registry is the only source.

    The SVG's own `data-hotspot` must agree with the registry: a disagreement is
    a cursor whose click point sits somewhere the artist never drew, which no
    later pass can see. The roles are kept apart because pointer and link each
    ship a 16 and a 32 — a flat size-keyed map would let one overwrite the other.
    """
    roles = {}
    for entry in reg["cursors"]:
        with open(os.path.join(CURSORS, entry["file"]), encoding="utf-8") as fh:
            markup = fh.read()
        found = re.search(r'data-hotspot="([\d.]+),([\d.]+)"', markup)
        if not found:
            raise SystemExit("make_cursors: %s declares no data-hotspot"
                             % entry["file"])
        declared = (float(found.group(1)), float(found.group(2)))
        listed = tuple(float(v) for v in entry["hotspot"])
        if declared != listed:
            raise SystemExit("make_cursors: registry says %s hotspots %s, the SVG "
                             "says %s" % (entry["file"], listed, declared))
        roles.setdefault(entry.get("role", "pointer"), {})[entry["size"]] = (
            markup, declared)
    return roles


def build_images(masters, work):
    """One role's static .cur images: 16 and 32 native, 48 from the biggest."""
    images, painted = [], []
    for size in sorted(set([min(masters), 32, 48])):
        native = size if size in masters else max(masters)
        markup, hotspot = masters[native]
        frames = rasterise(markup, native, hotspot, size, (0.0,), work)
        hx = int(round(hotspot[0] * size / float(native)))
        hy = int(round(hotspot[1] * size / float(native)))
        images.append((size, min(hx, size - 1), min(hy, size - 1),
                       bmp_entry(frames[0], size)))
        painted.append((size, frames[0]))
    return images, painted


def _body(markup):
    """The master's drawable body: its paths, without the <title>/<desc>."""
    inner = re.search(r"<svg\b[^>]*>(.*)</svg>", markup, re.S)
    if not inner:
        raise SystemExit("make_cursors: a master is not an <svg> document")
    return re.sub(r"<(title|desc)\b.*?</\1>", "", inner.group(1), flags=re.S).strip()


SLASH = ('<path d="M 5 29 L 27 3" fill="none" stroke="#101010"'
         ' stroke-width="5.4" stroke-linecap="round"/>'
         '<path d="M 5 29 L 27 3" fill="none" stroke="#ffffff"'
         ' stroke-width="2.6" stroke-linecap="round"/>')


def _hotspot(spec, hotspot):
    """Where the click lands once the glyph has been moved and turned."""
    if spec["hotspot"] == "centre":
        return (16.0, 16.0)
    angle, dx, dy, scale = spec["layers"][0]
    rad = math.radians(angle)
    px = hotspot[0] - GLYPH_CENTRE[0]
    py = hotspot[1] - GLYPH_CENTRE[1]
    return (16.0 + dx + scale * (px * math.cos(rad) - py * math.sin(rad)),
            16.0 + dy + scale * (px * math.sin(rad) + py * math.cos(rad)))


def compose(spec, markup, hotspot):
    """(markup, hotspot) for one derived slot, built from the 32 px master."""
    body = _body(markup)
    layers = "".join(
        '<g transform="translate(%.2f,%.2f) scale(%.3f) rotate(%.2f)'
        ' translate(%.2f,%.2f)">%s</g>'
        % (16.0 + dx, 16.0 + dy, scale, angle,
           -GLYPH_CENTRE[0], -GLYPH_CENTRE[1], body)
        for angle, dx, dy, scale in spec["layers"])
    if spec.get("slash"):
        layers += SLASH
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"'
            ' viewBox="0 0 32 32" data-role="derived" data-name="%s">%s</svg>'
            % (spec["slot"], layers), _hotspot(spec, hotspot))


def build_derived(spec, markup, hotspot, work):
    """One composed slot's images; the 32-unit composition is the native size."""
    composed, spot = compose(spec, markup, hotspot)
    images, painted = [], []
    for size in (16, 32, 48):
        frame = rasterise(composed, 32, spot, size, (0.0,), work)[0]
        hx = int(round(spot[0] * size / 32.0))
        hy = int(round(spot[1] * size / 32.0))
        images.append((size, min(hx, size - 1), min(hy, size - 1),
                       bmp_entry(frame, size)))
        painted.append((size, frame))
    return images, painted


def do_build(args):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(CURSORS, "registry.json"), encoding="utf-8") as fh:
        roles = load_masters(json.load(fh))
    if "link" not in roles:
        raise SystemExit("make_cursors: the registry holds no role=link masters; "
                         "the link pointer refuses to fall back to the arrow's "
                         "pixels")
    pointer, link = roles["pointer"], roles["link"]

    work = tempfile.mkdtemp(prefix="vulcan-cursors-")
    built = []

    # Static arrow: every size its masters can serve natively, plus 48 from 32.
    images, painted = build_images(pointer, work)
    # The 32 px render measures the ink the wave has to fit -- see the busy slot.
    arrow_ink = alpha_bbox(dict(painted)[32], 32)
    arrow = os.path.join(OUT, "vulcan-arrow.cur")
    with open(arrow, "wb") as fh:
        fh.write(cur_file(images))
    built.append((arrow, "static arrow", painted))

    # Hand (link select): its own masters and its own hotspot, so a clickable
    # link is visibly a different gesture from the arrow rather than a copy.
    images, painted = build_images(link, work)
    hand = os.path.join(OUT, "vulcan-hand.cur")
    with open(hand, "wb") as fh:
        fh.write(cur_file(images))
    built.append((hand, "link select", painted))

    # Busy / working-in-background: the salute waves, tip pinned to the hotspot.
    # Drawn on BUSY_CANVAS with the glyph sized by wave_layout, then filtered
    # down to BUSY_PX: the arc is wider than the pointer it ships as, and the
    # ring check below proves no frame lost ink to the canvas edge.
    markup, hotspot = pointer[max(pointer)]
    native = float(max(pointer))
    box, offset, frame_hot = wave_layout(
        tuple(v * native / 32.0 for v in arrow_ink), hotspot, WAVE,
        BUSY_CANVAS, BUSY_MARGIN, native)
    wide = rasterise(markup, native, hotspot, BUSY_CANVAS, WAVE, work,
                     offset=offset, glyph=box)
    frames = []
    for angle, frame in zip(WAVE, wide):
        assert_unclipped(frame, BUSY_CANVAS, angle)
        frames.append(downsample(frame, BUSY_CANVAS, BUSY_PX))
    shrink = BUSY_PX / float(BUSY_CANVAS)
    bhot = (min(int(round(frame_hot[0] * shrink)), BUSY_PX - 1),
            min(int(round(frame_hot[1] * shrink)), BUSY_PX - 1))
    busy = os.path.join(OUT, "vulcan-busy.ani")
    with open(busy, "wb") as fh:
        fh.write(ani_file(SCHEME_NAME, frames, BUSY_PX, bhot))
    built.append((busy, "busy (%d frames)" % len(frames),
                  [(BUSY_PX, f) for f in frames]))

    # The other seven Windows slots, all composed from that same master.
    pmarkup, phot = pointer[max(pointer)]
    for spec in DERIVED:
        images, painted = build_derived(spec, pmarkup, phot, work)
        path = os.path.join(OUT, spec["file"])
        with open(path, "wb") as fh:
            fh.write(cur_file(images))
        built.append((path, spec["label"], painted))

    preview = os.path.join(OUT, "preview.png")
    with open(preview, "wb") as fh:
        fh.write(make_preview(built))
    return built, preview


def make_preview(built):
    """Contact sheet: every built frame on a light and a dark half.

    Each frame is drawn at SHOW px by nearest-neighbour, so the 16 px glyph is
    judged at the size the eye needs — pixels shown, not smoothed away.
    """
    SHOW, cell, pad = 56, 64, 12
    rows, cols = len(built), max(len(b[2]) for b in built)
    w = pad + cols * (cell + pad)
    h = 2 * (pad + rows * (cell + pad))
    rgba = bytearray(w * h * 4)
    for y in range(h):
        value = 244 if y < h // 2 else 24
        for x in range(w):
            o = (y * w + x) * 4
            rgba[o] = rgba[o + 1] = rgba[o + 2] = value
            rgba[o + 3] = 255
    for r, (_path, _label, frames) in enumerate(built):
        for c, (size, src) in enumerate(frames):
            for half in (0, 1):
                base_y = half * (h // 2) + pad + r * (cell + pad)
                base_x = pad + c * (cell + pad)
                for dy in range(SHOW):
                    sy = dy * size // SHOW
                    for dx in range(SHOW):
                        sx = dx * size // SHOW
                        so = (sy * size + sx) * 4
                        if src[so + 3] == 0:
                            continue
                        do = ((base_y + dy) * w + base_x + dx) * 4
                        rgba[do:do + 4] = src[so:so + 4]
    return encode_png(w, h, rgba)


def do_install(args):
    built, preview = do_build(args)
    os.makedirs(SCHEME_DIR, exist_ok=True)
    rows = []
    for path, label, _images in built:
        ok, detail = windows_loads(path)
        rows.append((path, label, os.path.getsize(path), ok, detail))
    bad = [r for r in rows if not r[3]]
    for path, label, size, ok, detail in rows:
        print("%-12s %6d B  %-18s %s  %s"
              % (label, size, os.path.basename(path),
                 "OK" if ok else "REJECTED", detail))
    if bad:
        raise SystemExit("make_cursors: %d artefact(s) Windows would not load; "
                         "nothing installed" % len(bad))
    for path, _label, _images in built:
        with open(path, "rb") as src, open(os.path.join(SCHEME_DIR,
                                                        os.path.basename(path)),
                                           "wb") as dst:
            dst.write(src.read())
    scheme = ",".join(
        os.path.join(SCHEME_DIR, PROGRAMS[slot]) if slot in PROGRAMS else ""
        for slot in SLOTS)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY + r"\Schemes") as key:
        winreg.SetValueEx(key, SCHEME_NAME, 0, winreg.REG_EXPAND_SZ, scheme)
    print("scheme      %s -> %s" % (SCHEME_NAME, SCHEME_DIR))
    print("preview     %s" % preview)
    return built


def do_apply(args):
    os.makedirs(OUT, exist_ok=True)
    current = read_scheme()
    with open(backup_path(), "w", encoding="utf-8") as fh:
        json.dump(current, fh, indent=1)
    print("backup      %s (%d values)" % (backup_path(), len(current)))
    do_install(args)
    live = {slot: os.path.join(SCHEME_DIR, name)
            for slot, name in PROGRAMS.items()}
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY, 0,
                        winreg.KEY_SET_VALUE) as key:
        for slot, path in live.items():
            winreg.SetValueEx(key, slot, 0, winreg.REG_EXPAND_SZ, path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, SCHEME_NAME)
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    if not user32.SystemParametersInfoW(0x57, 0, None, 0):
        raise SystemExit("make_cursors: SPI_SETCURSORS failed (error %d)"
                         % ctypes.get_last_error())
    now = read_scheme()
    for slot in live:
        print("live        %-11s %s" % (slot, now.get(slot, "<missing>")))
    print("scheme      %s" % now.get("", ""))


def do_restore(args):
    path = backup_path()
    if not os.path.exists(path):
        raise SystemExit("make_cursors: no backup at %s" % path)
    with open(path, encoding="utf-8") as fh:
        saved = json.load(fh)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY, 0,
                        winreg.KEY_SET_VALUE) as key:
        for name, value in saved.items():
            winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
    ctypes.WinDLL("user32", use_last_error=True).SystemParametersInfoW(0x57, 0, None, 0)
    print("restored    %d values from %s" % (len(saved), path))


def do_uninstall(args):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY + r"\Schemes", 0,
                        winreg.KEY_SET_VALUE) as key:
        try:
            winreg.DeleteValue(key, SCHEME_NAME)
        except FileNotFoundError as exc:
            print("uninstall   scheme value was not registered: %s" % exc)
    removed = 0
    if os.path.isdir(SCHEME_DIR):
        for name in os.listdir(SCHEME_DIR):
            os.remove(os.path.join(SCHEME_DIR, name))
            removed += 1
        os.rmdir(SCHEME_DIR)
    print("uninstalled %d file(s); scheme entry removed" % removed)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--restore", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args()
    if args.restore:
        return do_restore(args)
    if args.uninstall:
        return do_uninstall(args)
    if args.apply:
        return do_apply(args)
    if args.install:
        return do_install(args)
    built, preview = do_build(args)
    for path, label, _images in built:
        print("%-12s %6d B  %s" % (label, os.path.getsize(path), path))
    print("preview     %s" % preview)


if __name__ == "__main__":
    main()
