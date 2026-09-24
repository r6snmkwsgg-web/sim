// Screenshots of a packed room: node rooms/tools/shots.mjs <name> [cams-json] [--night]
// cams-json: [[x, y, z, yaw, pitch], ...] in game space (x east, y up, z = Blender's y), yaw 0 looks toward -z.
// Without cams: views from each corner of every level toward the far corner, and one from high up.
// Saves rooms/out/shots/<name>_<k>.png and a contact sheet rooms/out/shots/<name>.jpg
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { mkdirSync, readFileSync } from 'fs';
import { spawnSync } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'out', 'shots'); mkdirSync(OUT, { recursive: true });
const name = process.argv[2], night = process.argv.includes('--night');
const meta = JSON.parse(readFileSync(join(ROOT, '..', 'game', 'rooms', name + '.json'), 'utf8'));
const W = meta.w * 16, D = meta.d * 16;
let cams = process.argv[3] && process.argv[3].startsWith('[') ? JSON.parse(process.argv[3]) : null;
if (!cams) {
  cams = [];
  const e = 1.4, look = (x, z, tx, tz) => Math.atan2(-(tx - x), -(tz - z));
  for (let L = 0; L < meta.levels; L++) {
    const y = L * 8 + 1.7;
    for (const [x, z] of [[e, e], [W - e, e], [W - e, D - e], [e, D - e]]) cams.push([x, y, z, look(x, z, W - x, D - z), 0.05]);
  }
  cams.push([W * 0.2, meta.levels * 8 - 1.2, D * 0.2, look(W * 0.2, D * 0.2, W, D), -0.45]);
}
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await (await b.newContext({ viewport: { width: 640, height: 360 }, ignoreHTTPSErrors: true })).newPage();
const errs = []; pg.on('pageerror', e => errs.push(e.message));
for (let t = 0; t < 4; t++) {   // the three.js download is sometimes flaky here: retry
  try { await pg.goto(`http://localhost:8812/dev/viewer.html?room=${name}${night ? '&night=1' : ''}`, { timeout: 60000 }); } catch (e) { continue; }
  let r = null;
  for (let i = 0; i < 240; i++) { r = await pg.evaluate(() => window.VIEW && (window.VIEW.ready || window.VIEW.err)).catch(() => null); if (r) break; if (i === 20 && !(await pg.evaluate(() => typeof THREE !== 'undefined').catch(() => false))) break; await pg.waitForTimeout(500); }
  if (r === true) break;
}
const files = [];
let k = 0;
for (const c of [cams[0], ...cams]) {   // the first view twice: the exposure settles on it
  await pg.evaluate(c => { camera.position.set(c[0], c[1], c[2]); camera.rotation.set(c[4] || 0, c[3] || 0, 0, 'YXZ'); }, c);
  await pg.waitForTimeout(3000);
  if (k > 0) { const f = join(OUT, `${name}_${k - 1}.png`); await pg.screenshot({ path: f, timeout: 180000 }); files.push(f); }
  k++;
}
await b.close();
spawnSync('python3', ['-c', `
import sys
from PIL import Image
fs = sys.argv[2:]; ims = [Image.open(f) for f in fs]; w, h = ims[0].size; n = len(ims); cols = 3; rows = (n + cols - 1) // cols
s = Image.new('RGB', (w * cols, h * rows))
for i, im in enumerate(ims): s.paste(im, ((i % cols) * w, (i // cols) * h))
s.thumbnail((1800, 1800)); s.save(sys.argv[1], quality=85)`, join(OUT, name + '.jpg'), ...files]);
console.log(JSON.stringify({ sheet: join(OUT, name + '.jpg'), views: files.length, errors: errs.slice(0, 5) }));
