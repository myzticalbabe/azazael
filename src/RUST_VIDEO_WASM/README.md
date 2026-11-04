# azazael-video-wasm — a music video, four ways through Rust/WASM

A `.mp4` cannot be handed to WASM the way an image can be handed to a JPEG
decoder. There is no single "video in Rust/WASM"; there is a choice about which
layer decodes and which layer owns the pixels. This crate implements all four
choices against the same track and measures each one, so the trade-offs are
readings instead of opinions.

| | who decodes | what Rust does | module | verdict |
|---|---|---|---|---|
| **A** browser + Rust | `<video>` (H.264/AAC) | 32-band DFT on PCM, 60 fps aurora | 118 KB | **the default.** Streams any length |
| **B** frames baked in | `jpeg-decoder` in-module | unpack + RGBA | 118 KB | works, wrong for songs (see size) |
| **C** pixel processing | the browser | every pixel, every frame | 118 KB | **the useful one** for effects |
| **D** packed stream | ffmpeg (offline) | RGB24 → RGBA in-module | 118 KB | correct container, honest limit |

## Measured, not estimated

Source: `C:/Users/clint/Music/In The End [Official HD Music Video] - Linkin Park.mp4`
— 28.69 MB, **AV1 + Opus**, 1280×712, 218.2 s. Re-encoded for the demo because a
browser may not carry whatever codec a download happened to use.

```
sample.mp4    19.35 MB   218.2 s   863x480   H.264 crf30 + AAC 96k, faststart
frames.bin     2.13 MB    12.0 s   320x180   145 JPEG frames @12fps   -> 0.18 MB/s
raw.bin        2.97 MB    12.0 s   160x90     72 RGB24 frames @6fps    -> 42 KB/frame
wasm            118 KB    both targets
```

Read the B row as the argument against B: 0.18 MB/s at a postage-stamp 320×180
means **≈38 MB to carry this one track**, roughly twice the 19.35 MB mp4 that
holds it at 480p — inter-frame prediction is doing real work, and baking stills
throws it away.

## Run it

```bash
cd src/RUST_VIDEO_WASM
wasm-pack build --target web    --out-dir pkg --release   # demo
wasm-pack build --target nodejs --out-dir pkg-node --release   # harness

python tools/make_assets.py "C:/Users/clint/Music/In The End [Official HD Music Video] - Linkin Park.mp4"
python tools/make_assets.py                                # or: synthesise a 6 s clip

node test.mjs                     # every export, real assets, exit 0
python -m http.server 8123 --bind 127.0.0.1
#  -> http://127.0.0.1:8123/demo/index.html
```

`python tools/make_assets.py <any.mp4>` is the whole swap-in: it re-encodes to
H.264/AAC and re-cooks both blobs. It needs only ffmpeg and Python's stdlib.

## The four architectures

**A — the browser decodes, Rust paints.** `<video>` handles the container,
H.264 and AAC, including seeking and buffering. Rust gets 1024 PCM samples from
an `AnalyserNode`, computes 32 band energies with a Hann-windowed DFT, smooths
them and renders an additive field composited with `mix-blend-mode: screen` so
black contributes nothing. This is the only architecture that streams a file of
any length, and it is the one to ship.

**B — frames baked into the module.** One `AVFB` blob: magic, count, w, h, fps,
an offset table, then concatenated JPEGs. `decode_frame_rgba` decodes in-module.
No media element, no network after load — and a payload that grows with every
frame rather than every shot.

**C — Rust owns every pixel.** `drawImage` → `getImageData` →
`process_frame_rgba` → `putImageData`. Three effects ship: beat tint, Sobel edge
glow, chroma split with scanlines; all amplitude-linked to the audio energy
measured by A. This is where Rust earns its place, because the work is per-pixel
and the browser is only a decoder. The measured demo runs at the display's 60 fps
at 480×270. Upgrade path: WebCodecs `VideoFrame` → `copyTo` removes both CPU
copies that `getImageData`/`putImageData` charge.

**D — a packed stream parsed in Rust.** `AVRD` blob: header plus contiguous
`w·h·3` RGB24 frames, parsed and widened to RGBA by `unpack_rgb_frame`.

### D's honest boundary

The container and pixel layout are Rust. **The decode is not.** Decoding H.264
inside the module needs a full entropy decoder, and there is no production-grade
pure-Rust one to depend on. The practical route is `ffmpeg.wasm` — C compiled to
WASM, roughly 25–30 MB, which is the entire payload budget before a single frame
is stored. That route is documented here as the path to full in-WASM decoding; it
is **not** implemented or tested in this crate, and nothing in this README should
be read as claiming otherwise.

## One defect this crate paid for, kept as a regression test

The first DFT normalised the phase as `-2π·k·i/win` in `f32`. At k≈1024, i≈1024
that angle reaches ~6.4e6 rad, where f32 resolves only ~0.5 rad — the transform
degenerated into noise: a 3 kHz tone peaked at band 30 of 32, and DC peaked at
band 22. It survived a "does it return numbers" check because an impulse has a
flat magnitude by construction, and flat looked correct.

The fix is an exact integer reduce, `(k*i) % win`, with `f64` accumulation.
`test.mjs` now carries the control that would have caught it: **DC must peak at
band 0**, and a 3 kHz tone must peak at band 2.

## Layout

```
Cargo.toml               crate azazael-video-wasm (cdylib + rlib, edition 2024)
src/lib.rs               all exports: spectrum_bands, render_aurora,
                         frame_count, frame_dims, decode_frame_rgba,
                         process_frame_rgba, raw_frame_count, raw_frame_dims,
                         unpack_rgb_frame
test.mjs                 node harness, real assets, exit status
tools/make_assets.py     ffmpeg pipeline + both blob packers (stdlib only)
tools/verify_demo.mjs    headless-Chrome CDP check: all four panels must paint
demo/index.html          the four-tab demo
```

`pkg/`, `pkg-node/`, `target/` and `demo/assets/` are generated and gitignored;
this README's numbers are produced by the commands above, not stored with them.

## A note on the source clip

The demo plays a licensed Linkin Park music video because that is the file in the
Music folder. Nothing from it is committed — `demo/assets/` is gitignored, and the
blob formats carry no copy-protection circumvention. Point `make_assets.py` at
your own file and the numbers re-measure.
