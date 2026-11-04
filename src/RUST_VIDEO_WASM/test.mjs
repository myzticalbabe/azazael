// Run every WASM export against the generated assets. No browser needed.
//   node test.mjs
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const wasm = require("./pkg-node/azazael_video_wasm.js");

let fails = 0;
const check = (name, cond, detail = "") => {
  if (!cond) fails++;
  console.log(`${cond ? "PASS" : "FAIL"}  ${name}${detail ? "  " + detail : ""}`);
};

const frames = readFileSync("demo/assets/frames.bin");
const raw = readFileSync("demo/assets/raw.bin");
const mp4 = readFileSync("demo/assets/sample.mp4");

// ---- mode B: frames baked into the blob
const nB = wasm.frame_count(frames);
const dimsB = wasm.frame_dims(frames);
check("B frame_count", nB > 0, `${nB} frames`);
check("B frame_dims", dimsB[0] === 320 && dimsB[1] === 180, `${dimsB.join("x")}`);

const f0 = wasm.decode_frame_rgba(frames, 0);
check("B decode size", f0.length === 320 * 180 * 4, `${f0.length} bytes`);
const fmid = wasm.decode_frame_rgba(frames, Math.floor(nB / 2));
let differ = 0;
for (let i = 0; i < Math.min(f0.length, fmid.length); i += 4) if (f0[i] !== fmid[i]) differ++;
check("B decodes distinct frames", differ > 100, `${differ} differing red samples`);
check("B rejects out-of-range index", wasm.decode_frame_rgba(frames, nB).length === 0);

// ---- mode D: packed RGB24 stream
const nD = wasm.raw_frame_count(raw);
check("D raw_frame_count", nD > 0, `${nD} frames`);
const d0 = wasm.unpack_rgb_frame(raw, 0);
check("D unpack size", d0.length === 160 * 90 * 4, `${d0.length} bytes`);
check("D alpha opaque", d0[3] === 255);

// ---- mode A: spectrum + aurora
const N = 1024, sr = 48000, hz = 3000; // bin 64 of 1024 == 3000 Hz
const pcm = new Float32Array(N);
for (let i = 0; i < N; i++) pcm[i] = Math.sin((2 * Math.PI * hz * i) / sr);
const bands = wasm.spectrum_bands(pcm, 32);
const peak = bands.indexOf(Math.max(...bands));
check("A spectrum peaks at the right band", peak === 2, `peak band ${peak} (expected 2)`);
check("A bands normalised", Math.abs(Math.max(...bands) - 1) < 1e-6 && Math.min(...bands) >= 0);

// Negative control for the f32-phase bug fixed on 2026-11-03: DC must peak in
// band 0. Before the integer-modulo fix this peaked at band 22.
const dc = new Float32Array(1024).fill(1.0);
const dcBands = Array.from(wasm.spectrum_bands(dc, 32));
check("A DC peaks at band 0", dcBands.indexOf(Math.max(...dcBands)) === 0,
  `peak band ${dcBands.indexOf(Math.max(...dcBands))}`);

const aurora = wasm.render_aurora(128, 72, new Float32Array(bands), 0.5);
check("A aurora size", aurora.length === 128 * 72 * 4, `${aurora.length} bytes`);
let lit = 0;
for (let i = 3; i < aurora.length; i += 4) if (aurora[i] > 8) lit++;
check("A aurora glows", lit > 200, `${lit} lit pixels`);

// ---- mode C: per-frame processing
const snapshot = wasm.decode_frame_rgba(frames, 0);
for (const mode of [0, 1, 2]) {
  const buf = new Uint8Array(snapshot);
  wasm.process_frame_rgba(buf, 320, 180, mode, 1.0, 0.8);
  let changed = 0;
  for (let i = 0; i < buf.length; i++) if (buf[i] !== snapshot[i]) changed++;
  check(`C mode ${mode} mutates the frame`, changed > 1000, `${changed} bytes changed`);
}

// ---- size reality check: report rates, never a total-vs-total ratio.
// The blob and the mp4 can cover different spans (the blob is cooked from an
// excerpt), so only bytes-per-second is a like-for-like number.
const blobSec = nB / dimsB[2];
const blobRate = frames.length / blobSec;
check("payload: assets are real", mp4.length > 1000 && frames.length > 1000,
  `mp4 ${(mp4.length / 1048576).toFixed(2)} MB total, blob ${(frames.length / 1048576).toFixed(2)} MB for ${blobSec.toFixed(0)}s`);
console.log(`INFO  baked frames cost ${(blobRate / 1048576).toFixed(2)} MB/s at 320x180/12fps ` +
  `(${((blobRate / 1048576) * 218).toFixed(0)} MB for a 3m38s track)`);

console.log(fails === 0 ? "\nALL CHECKS PASSED" : `\n${fails} CHECK(S) FAILED`);
process.exit(fails === 0 ? 0 : 1);
