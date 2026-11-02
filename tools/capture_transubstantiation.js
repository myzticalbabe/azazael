// Capture a forged 3D transubstantiation scene to frames, and probe it from inside the page.
//
// Two jobs, and the second is the one that matters:
//   1. drive window.__step(tick) and screenshot each tick -> frames/frame_%04d.png
//   2. call the page's own __geo() and __state(tick) and write browser_probe.json, so
//      transubstantiate.py --verify can compare the browser's digest against Python's.
//      A golden run that only the Python side can produce proves the Python side agrees
//      with itself; the cross-language probe proves the two builds are the same tree.
//
// Frame index comes from the loop counter, never from the clock (YGGDRASIL_RENDER_PLAYBOOK).
// Run: NODE_PATH=C:/Users/clint/node_modules node tools/capture_transubstantiation.js <dir> [frames]
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

(async () => {
  const dir = process.argv[2];
  const FRAMES = parseInt(process.argv[3] || '240', 10);
  if (!dir) { console.error('usage: capture_transubstantiation.js <scene-dir> [frames]'); process.exit(2); }
  const scene = path.resolve(dir, 'flame3d.html');
  if (!fs.existsSync(scene)) { console.error('no scene at ' + scene); process.exit(2); }
  const framesDir = path.resolve(dir, 'frames');
  fs.mkdirSync(framesDir, { recursive: true });

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu', '--force-device-scale-factor=1',
           '--hide-scrollbars', '--disable-lcd-text'],
  });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
    await page.goto(pathToFileURL(scene).href, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction('typeof window.__step === "function"', { timeout: 20000 });

    const total = await page.evaluate(() => window.__TOTAL);
    const geo = await page.evaluate(() => window.__geo());
    const probeStates = {};
    // the same three fractions transubstantiate.py hashes, read back from golden3d.json so
    // the probe cannot drift from the golden definition
    const golden = JSON.parse(fs.readFileSync(path.resolve(dir, 'golden3d.json'), 'utf-8'));
    for (const key of Object.keys(golden.states)) {
      probeStates[key] = await page.evaluate((t) => window.__state(t), parseInt(key.slice(1), 10));
    }
    const probe = { geometry_sha256: geo.digest, segments: geo.segments, leaves: geo.leaves,
                    states: probeStates, total: total, errors: errors };
    fs.writeFileSync(path.resolve(dir, 'browser_probe.json'), JSON.stringify(probe, null, 1));
    console.log('probe: segments=' + geo.segments + ' leaves=' + geo.leaves +
                ' digest=' + geo.digest + ' errors=' + errors.length);

    for (let i = 0; i < FRAMES; i++) {
      const tick = Math.round((total * i) / FRAMES);
      const name = path.join(framesDir, 'frame_' + String(i).padStart(4, '0') + '.png');
      await page.evaluate((t) => window.__step(t), tick);
      await page.screenshot({ path: name, type: 'png', captureBeyondViewport: false });
      if (i % 40 === 0) console.log('frame ' + i + '/' + FRAMES + ' tick=' + tick);
    }
    console.log('captured ' + FRAMES + ' frames -> ' + framesDir);
    if (errors.length) { console.error('CONSOLE ERRORS: ' + errors.slice(0, 5).join(' | ')); process.exitCode = 1; }
  } finally {
    await browser.close();
  }
})();
