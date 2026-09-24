// Walkability check for packed rooms: node rooms/tools/check.mjs <name> [more names...]
// Needs the game served at http://localhost:8812 (python3 -m http.server 8812 in game/).
// Prints a JSON report per room and saves a map to rooms/out/check/<name>.png
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'out', 'check');
mkdirSync(OUT, { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await (await b.newContext({ viewport: { width: 1100, height: 1400 }, ignoreHTTPSErrors: true })).newPage();
for (const name of process.argv.slice(2)) {
  let r = null;
  for (let t = 0; t < 3 && !r; t++) {
    try { await pg.goto(`http://localhost:8812/dev/check.html?room=${name}`, { timeout: 60000 }); } catch (e) { continue; }
    for (let i = 0; i < 400; i++) { r = await pg.evaluate(() => window.CHECK).catch(() => null); if (r) break; if (i === 20 && !(await pg.evaluate(() => typeof THREE !== 'undefined').catch(() => false))) break; await pg.waitForTimeout(500); }
    if (r && r.error && /THREE/.test(r.error)) r = null;
  }
  console.log(JSON.stringify(r).replace(/,"(?=[a-z_]+":)/g, ',\n "'));
  if (r && !r.error) await pg.locator('#maps').screenshot({ path: join(OUT, name + '.png') });
}
await b.close();
