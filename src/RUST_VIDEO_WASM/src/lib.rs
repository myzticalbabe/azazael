//! azazael-video-wasm — four ways to put a music video through Rust/WASM.
//!
//! The point of this crate is to make the difference measurable rather than
//! argued. Each mode answers "can a music video become Rust/WASM?" differently:
//!
//! * **A** `spectrum_bands` + `render_aurora` — Rust computes band energies from
//!   PCM and paints an additive visual field. The `<video>` element still decodes.
//! * **B** `frame_count` / `decode_frame_rgba` — the frames themselves live inside
//!   a WASM blob and are JPEG-decoded in-module. No media element, no streaming.
//! * **C** `process_frame_rgba` — the browser decodes, Rust owns every pixel
//!   (beat tint, edge glow, chroma shift).
//! * **D** `unpack_rgb_frame` — a packed RGB24 stream is parsed and converted to
//!   RGBA in-module. Genuine in-WASM frame extraction, with the honest caveat
//!   that H.264 entropy decoding is *not* implemented here.
//!
//! Every function is total: bad input returns an empty `Vec`, never a panic.

use js_sys::Float32Array;
use wasm_bindgen::prelude::*;

/// Blob container for mode B: JPEG frames plus an offset index.
const MAGIC_FRAMES: &[u8; 4] = b"AVFB";
/// Blob container for mode D: concatenated RGB24 frames.
const MAGIC_RAW: &[u8; 4] = b"AVRD";
/// magic(4) + count + width + height + fps, all little-endian u32.
const HEADER: usize = 20;

fn u32_at(buf: &[u8], off: usize) -> Option<u32> {
    buf.get(off..off + 4)
        .map(|s| u32::from_le_bytes([s[0], s[1], s[2], s[3]]))
}

fn header(blob: &[u8], magic: &[u8; 4]) -> Option<(usize, usize, usize, usize)> {
    if blob.len() < HEADER || &blob[0..4] != magic {
        return None;
    }
    let n = u32_at(blob, 4)? as usize;
    let w = u32_at(blob, 8)? as usize;
    let h = u32_at(blob, 12)? as usize;
    let fps = u32_at(blob, 16)? as usize;
    if w == 0 || h == 0 || n == 0 {
        return None;
    }
    Some((n, w, h, fps))
}

// ---------------------------------------------------------------- mode A: audio

fn hann(i: usize, n: usize) -> f32 {
    let x = core::f32::consts::PI * 2.0 * i as f32 / (n.max(2) - 1) as f32;
    0.5 - 0.5 * x.cos()
}

/// Magnitude of one DFT bin per band, normalised to the strongest band.
///
/// Naive DFT over a bounded window (1024 samples) so the cost is predictable in
/// WASM; the window bounds the work, not the fidelity. Returns `bands` values in
/// `0.0..=1.0`.
#[wasm_bindgen]
pub fn spectrum_bands(samples: &Float32Array, bands: usize) -> Vec<f32> {
    let bands = bands.clamp(1, 256);
    let n = samples.length() as usize;
    if n == 0 {
        return vec![0.0; bands];
    }
    let win = n.min(1024);

    let mut out = vec![0f32; bands];
    for (b, slot) in out.iter_mut().enumerate() {
        // Bin range for this band, mapped over the window's frequency axis.
        let lo = b * win / bands;
        let hi = (((b + 1) * win / bands).max(lo + 1)).min(win);
        let k = (lo + hi) / 2;
        // The phase must be reduced in INTEGER arithmetic first: 2*pi*k*i reaches
        // ~6.4e6 rad at k=1024, i=1024, where f32 resolves only ~0.5 rad and the
        // transform degenerates into noise. (k*i) % win is exact and cheap.
        // Accumulate in f64 so 1024 terms of cancellation do not eat the lobes.
        let (mut re, mut im) = (0f64, 0f64);
        for i in 0..win {
            let x = (samples.get_index(i as u32) * hann(i, win)) as f64;
            let turns = ((k * i) % win) as f64 / win as f64;
            let ang = -2.0 * std::f64::consts::PI * turns;
            re += x * ang.cos();
            im += x * ang.sin();
        }
        *slot = ((re * re + im * im).sqrt() / win as f64) as f32;
    }

    let peak = out.iter().cloned().fold(0f32, f32::max);
    if peak > 1e-9 {
        for v in out.iter_mut() {
            *v = (*v / peak).min(1.0);
        }
    }
    out
}

/// Additive aurora field driven by band energies. Returns RGBA for one frame.
///
/// `bands` are expected pre-smoothed and normalised by the caller; `t` is
/// seconds since start. Alpha carries the glow so the result can be composited
/// over the video rather than replacing it.
#[wasm_bindgen]
pub fn render_aurora(width: usize, height: usize, bands: &Float32Array, t: f64) -> Vec<u8> {
    if width == 0 || height == 0 || width * height > 16_777_216 {
        return Vec::new();
    }
    let nb = bands.length() as usize;
    if nb == 0 {
        return vec![0u8; width * height * 4];
    }
    let t = t as f32;
    let mut out = vec![0u8; width * height * 4];
    let (fw, fh) = (width as f32, height as f32);

    for y in 0..height {
        let v = y as f32 / (fh - 1.0).max(1.0);
        for x in 0..width {
            let u = x as f32 / (fw - 1.0).max(1.0);
            let b = ((u * nb as f32) as usize).min(nb - 1);
            let e = bands.get_index(b as u32);

            let centre = 0.5 + 0.18 * (u * 9.42 + t * 1.2).sin();
            let width_band = 0.10 + 0.45 * e;
            let d = (v - centre).abs() / width_band.max(0.02);
            let glow = (-d * d * 3.0).exp() * (0.18 + e * 1.5);

            let scan = 0.05 * ((y as f32 * 0.55 + t * 40.0).sin() * 0.5 + 0.5);
            let r = (glow * 0.55 + scan).min(1.0);
            let g = (glow * 0.85 + scan * 0.6).min(1.0);
            let bl = (glow * 1.00 + scan * 0.3).min(1.0);
            let a = (glow * 1.2).min(1.0);

            let i = (y * width + x) * 4;
            out[i] = (r * 255.0) as u8;
            out[i + 1] = (g * 255.0) as u8;
            out[i + 2] = (bl * 255.0) as u8;
            out[i + 3] = (a * 255.0) as u8;
        }
    }
    out
}

// ------------------------------------------------------- mode B: frames in blob

#[wasm_bindgen]
pub fn frame_count(blob: &[u8]) -> u32 {
    header(blob, MAGIC_FRAMES).map(|(n, ..)| n as u32).unwrap_or(0)
}

/// `[width, height, fps]`, or empty when the blob is not a frames container.
#[wasm_bindgen]
pub fn frame_dims(blob: &[u8]) -> Vec<u32> {
    match header(blob, MAGIC_FRAMES) {
        Some((_, w, h, fps)) => vec![w as u32, h as u32, fps as u32],
        None => Vec::new(),
    }
}

/// JPEG-decode frame `index` inside the blob and return RGBA8.
#[wasm_bindgen]
pub fn decode_frame_rgba(blob: &[u8], index: u32) -> Vec<u8> {
    let Some((n, w, h, _)) = header(blob, MAGIC_FRAMES) else {
        return Vec::new();
    };
    let i = index as usize;
    if i >= n {
        return Vec::new();
    }
    let table = HEADER;
    let Some(start) = u32_at(blob, table + i * 4).map(|v| v as usize) else {
        return Vec::new();
    };
    let Some(end) = u32_at(blob, table + (i + 1) * 4).map(|v| v as usize) else {
        return Vec::new();
    };
    let Some(jpeg) = blob.get(start..end) else {
        return Vec::new();
    };

    let mut dec = jpeg_decoder::Decoder::new(jpeg);
    let Ok(pixels) = dec.decode() else {
        return Vec::new();
    };
    let Some(info) = dec.info() else {
        return Vec::new();
    };

    let mut out = vec![0u8; w * h * 4];
    match info.pixel_format {
        jpeg_decoder::PixelFormat::RGB24 => {
            for (px, chunk) in out.chunks_exact_mut(4).zip(pixels.chunks_exact(3)) {
                px[0] = chunk[0];
                px[1] = chunk[1];
                px[2] = chunk[2];
                px[3] = 255;
            }
        }
        jpeg_decoder::PixelFormat::L8 => {
            for (px, v) in out.chunks_exact_mut(4).zip(pixels.iter()) {
                px[0] = *v;
                px[1] = *v;
                px[2] = *v;
                px[3] = 255;
            }
        }
        _ => return Vec::new(),
    }
    out
}

// --------------------------------------------------- mode C: per-frame pixels

fn luma(r: u8, g: u8, b: u8) -> f32 {
    0.2126 * r as f32 + 0.7152 * g as f32 + 0.0722 * b as f32
}

/// Process RGBA in place. `mode` 0 = beat tint, 1 = edge glow, 2 = chroma split
/// plus scanlines. `energy` is the current band energy in `0.0..=1.0`.
#[wasm_bindgen]
pub fn process_frame_rgba(buf: &mut [u8], w: usize, h: usize, mode: u32, strength: f32, energy: f32) {
    if w == 0 || h == 0 || buf.len() < w * h * 4 {
        return;
    }
    let s = strength.clamp(0.0, 4.0);
    let e = energy.clamp(0.0, 1.0);
    let n = w * h;

    match mode {
        0 => {
            // Warm push on the beat, cool between; keeps luminance stable.
            let gain_r = 1.0 + s * e * 0.55;
            let gain_b = 1.0 - s * e * 0.35;
            for i in 0..n {
                let p = i * 4;
                buf[p] = ((buf[p] as f32) * gain_r).min(255.0) as u8;
                buf[p + 2] = ((buf[p + 2] as f32) * gain_b).max(0.0) as u8;
            }
        }
        1 => {
            // Sobel on luma, added back as a glow.
            let src: Vec<f32> = (0..n)
                .map(|i| {
                    let p = i * 4;
                    luma(buf[p], buf[p + 1], buf[p + 2])
                })
                .collect();
            for y in 1..h.saturating_sub(1) {
                for x in 1..w.saturating_sub(1) {
                    let at = |dx: isize, dy: isize| -> f32 {
                        let xx = (x as isize + dx) as usize;
                        let yy = (y as isize + dy) as usize;
                        src[yy * w + xx]
                    };
                    let gx = -at(-1, -1) - 2.0 * at(-1, 0) - at(-1, 1)
                        + at(1, -1)
                        + 2.0 * at(1, 0)
                        + at(1, 1);
                    let gy = -at(-1, -1) - 2.0 * at(0, -1) - at(1, -1)
                        + at(-1, 1)
                        + 2.0 * at(0, 1)
                        + at(1, 1);
                    let edge = ((gx * gx + gy * gy).sqrt() / 4.0) * s * (0.35 + e);
                    let p = (y * w + x) * 4;
                    for c in 0..3 {
                        buf[p + c] = (buf[p + c] as f32 + edge).min(255.0) as u8;
                    }
                }
            }
        }
        2 => {
            // Horizontal chroma split plus scanlines, amplitude follows energy.
            let shift = ((1.0 + e * 3.0) * s) as usize;
            let src = buf.to_vec();
            for y in 0..h {
                let scan = if y % 3 == 0 { 1.0 - 0.22 * s.min(1.0) } else { 1.0 };
                for x in 0..w {
                    let p = (y * w + x) * 4;
                    let xr = x.saturating_sub(shift);
                    let xb = (x + shift).min(w - 1);
                    let pr = (y * w + xr) * 4;
                    let pb = (y * w + xb) * 4;
                    buf[p] = (src[pr] as f32 * scan).min(255.0) as u8;
                    buf[p + 1] = (src[p + 1] as f32 * scan).min(255.0) as u8;
                    buf[p + 2] = (src[pb + 2] as f32 * scan).min(255.0) as u8;
                }
            }
        }
        _ => {}
    }
}

// ------------------------------------------------------- mode D: packed RGB24

#[wasm_bindgen]
pub fn raw_frame_count(blob: &[u8]) -> u32 {
    header(blob, MAGIC_RAW).map(|(n, ..)| n as u32).unwrap_or(0)
}

/// `[width, height, fps]` for a packed RGB24 stream.
#[wasm_bindgen]
pub fn raw_frame_dims(blob: &[u8]) -> Vec<u32> {
    match header(blob, MAGIC_RAW) {
        Some((_, w, h, fps)) => vec![w as u32, h as u32, fps as u32],
        None => Vec::new(),
    }
}

/// Unpack RGB24 frame `index` from the stream into RGBA8.
///
/// This is the honest boundary of mode D: the container and pixel layout are
/// parsed in Rust, but the H.264 entropy decode that produced these bytes ran in
/// ffmpeg, not in this module.
#[wasm_bindgen]
pub fn unpack_rgb_frame(blob: &[u8], index: u32) -> Vec<u8> {
    let Some((n, w, h, _)) = header(blob, MAGIC_RAW) else {
        return Vec::new();
    };
    let i = index as usize;
    if i >= n {
        return Vec::new();
    }
    let stride = w * h * 3;
    let start = HEADER + i * stride;
    let Some(rgb) = blob.get(start..start + stride) else {
        return Vec::new();
    };
    let mut out = vec![0u8; w * h * 4];
    for (px, chunk) in out.chunks_exact_mut(4).zip(rgb.chunks_exact(3)) {
        px[0] = chunk[0];
        px[1] = chunk[1];
        px[2] = chunk[2];
        px[3] = 255;
    }
    out
}
