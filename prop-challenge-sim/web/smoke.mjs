/*
 * smoke.mjs -- drive the built page in real Chromium over CDP.
 *
 * The page computes everything on load, so "does it parse" is not enough: this
 * waits for the run to actually finish, then reads the numbers back out of the
 * DOM and screenshots the result.  No dependencies -- node 22 ships fetch and
 * WebSocket.  Usage: node web/smoke.mjs [--shot out.png]
 */

import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const PORT = 9333;
const PAGE = 'file://' + resolve('web/index.html');
const shotArg = process.argv.indexOf('--shot');
const SHOT = shotArg > -1 ? process.argv[shotArg + 1] : null;

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
  '--force-color-profile=srgb', '--window-size=1280,1400',
  `--remote-debugging-port=${PORT}`, '--user-data-dir=/tmp/propsim-chrome',
  PAGE,
], { stdio: 'ignore' });

let ws, id = 0;
const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => {
  const n = ++id;
  pending.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method, params }));
});
const evaluate = async (expr) => {
  const r = await send('Runtime.evaluate', {
    expression: expr, returnByValue: true, awaitPromise: true,
  });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + ' ' +
    (r.exceptionDetails.exception?.description || ''));
  return r.result.value;
};

const fail = (msg) => { console.error('SMOKE FAIL: ' + msg); chrome.kill(); process.exit(1); };

try {
  let target = null;
  for (let i = 0; i < 60 && !target; i++) {
    await sleep(250);
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      target = list.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
    } catch { /* not up yet */ }
  }
  if (!target) fail('chrome never exposed a page target');

  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  const consoleErrors = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { res, rej } = pending.get(m.id);
      pending.delete(m.id);
      m.error ? rej(new Error(m.error.message)) : res(m.result);
    } else if (m.method === 'Runtime.exceptionThrown') {
      consoleErrors.push(m.params.exceptionDetails.text + ' ' +
        (m.params.exceptionDetails.exception?.description || ''));
    } else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
      consoleErrors.push(m.params.args.map(a => a.value ?? a.description).join(' '));
    }
  };
  await send('Runtime.enable');
  await send('Page.enable');

  // Wait for the page to finish its own boot pipeline.
  const t0 = Date.now();
  let done = false;
  for (let i = 0; i < 240 && !done; i++) {
    await sleep(250);
    done = await evaluate(
      `!document.getElementById('runBtn').disabled &&
       document.querySelectorAll('#ruleBody tr').length === 6`);
  }
  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
  if (!done) {
    const state = await evaluate(`JSON.stringify({
      btn: document.getElementById('runBtn').textContent,
      rows: document.querySelectorAll('#ruleBody tr').length,
      rate: document.getElementById('bigRate').textContent })`);
    fail(`boot pipeline did not finish in 60s -- ${state}`);
  }

  const report = await evaluate(`(() => {
    const t = (s) => (document.querySelector(s)||{}).textContent?.trim() || '';
    const rows = [...document.querySelectorAll('#ruleBody tr')].map(tr =>
      [...tr.children].map(td => td.textContent.trim()));
    const stats = [...document.querySelectorAll('#stats div')].map(d =>
      [d.querySelector('dt').textContent, d.querySelector('dd').textContent]);
    // Confirm the canvas actually painted rather than sitting blank.
    const cv = document.getElementById('chart');
    const g = cv.getContext('2d');
    const px = g.getImageData(0, 0, cv.width, Math.floor(cv.height / 2)).data;
    const seen = new Set();
    for (let p = 0; p < px.length; p += 4 * 97)
      seen.add(px[p] + ',' + px[p+1] + ',' + px[p+2]);
    return JSON.stringify({
      chip: t('.src'), rate: t('#bigRate'), sub: t('#bigSub'),
      verdict: t('#verdict'), rows, stats,
      bars: REAL_BARS.n, windowNote: t('#windowNote'),
      lTP: t('#lTP'), lSL: t('#lSL'), lKill: t('#lKill'),
      hud: ['hBal','hEq','hRoom','hTarget'].map(i => t('#'+i)),
      distinctColors: seen.size,
      canvasW: cv.width, canvasH: cv.height,
      scrollX: document.documentElement.scrollWidth > window.innerWidth + 1,
      height: document.documentElement.scrollHeight,
    });
  })()`);
  const r = JSON.parse(report);

  console.log(`  booted and completed in ${elapsed}s`);
  console.log(`  data      ${r.chip}`);
  console.log(`  headline  ${r.rate}  (${r.sub})`);
  console.log(`  chart     ${r.canvasW}x${r.canvasH}, ${r.distinctColors} distinct colours painted`);
  console.log(`  verdict   ${r.verdict}`);
  console.log(`  window    ${r.windowNote}`);
  console.log(`  lines     TP ${r.lTP} | SL ${r.lSL} | kill ${r.lKill}`);
  console.log(`  hud       ${r.hud.join('  ')}`);
  console.log(`  page      ${r.height}px tall, horizontal overflow: ${r.scrollX}`);
  console.log('\n  rulebook table');
  for (const row of r.rows) console.log('    ' + row.map(c => c.padStart(13)).join(''));
  console.log('\n  stat tiles');
  for (const [k, v] of r.stats) console.log(`    ${k.padEnd(24)} ${v}`);

  const problems = [];
  console.log('');
  if (r.rows.length !== 6) problems.push(`expected 6 rulebook rows, got ${r.rows.length}`);
  if (r.distinctColors < 8) problems.push(`chart looks blank (${r.distinctColors} colours)`);
  if (!/^1\.\d{4}/.test(r.lTP)) problems.push(`TP line not priced: "${r.lTP}"`);
  if (!/^1\.\d{4}/.test(r.lKill)) problems.push(`liquidation price not drawn: "${r.lKill}"`);
  if (!/^\d/.test(r.rate)) problems.push(`headline pass rate not rendered: "${r.rate}"`);
  if (r.stats.length !== 8) problems.push(`expected 8 stat tiles, got ${r.stats.length}`);

  if (r.scrollX) problems.push('page scrolls horizontally');
  if (consoleErrors.length) problems.push('console errors: ' + consoleErrors.join(' | '));

  // Exercise the replay: it must advance the reveal head and then settle back
  // on the finished day.
  const replay = await evaluate(`(async () => {
    const before = S.reveal;
    document.getElementById('play').click();
    await new Promise(r => setTimeout(r, 600));
    const during = S.reveal;
    const label = document.getElementById('play').textContent;
    document.getElementById('play').click();
    await new Promise(r => setTimeout(r, 120));
    return JSON.stringify({ before, during, after: S.reveal, label,
                            playing: S.playing });
  })()`);
  const rp = JSON.parse(replay);
  console.log(`  replay    reveal ${rp.before} -> ${rp.during} -> ${rp.after}` +
              `  (button read "${rp.label}")`);
  if (!(rp.during > 0 && rp.during < rp.before)) problems.push('replay did not advance');
  if (rp.playing) problems.push('replay did not stop');

  // And that dragging a line re-runs the engine.
  const drag = await evaluate(`(() => {
    const before = { tp: S.tp, outcome: S.res.outcome };
    S.tp = BARS.close[S.i0] + (S.tp - BARS.close[S.i0]) * 0.25;
    runDay();
    return JSON.stringify({ before, after: { tp: S.tp, outcome: S.res.outcome } });
  })()`);
  const dg = JSON.parse(drag);
  console.log(`  drag      TP ${dg.before.tp.toFixed(5)} -> ${dg.after.tp.toFixed(5)}` +
              `   outcome ${dg.before.outcome} -> ${dg.after.outcome}`);
  if (dg.before.tp === dg.after.tp) problems.push('TP did not move');

  if (SHOT) {
    await send('Emulation.setDeviceMetricsOverride', {
      width: 1280, height: Math.min(r.height, 16000), deviceScaleFactor: 1,
      mobile: false,
    });
    await sleep(400);
    const img = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    writeFileSync(SHOT, Buffer.from(img.data, 'base64'));
    console.log(`\n  screenshot -> ${SHOT}`);
  }

  if (problems.length) { for (const p of problems) console.error('  PROBLEM: ' + p); fail(`${problems.length} problem(s)`); }
  console.log('\n  smoke test passed');
  chrome.kill();
  process.exit(0);
} catch (e) {
  console.error(e);
  chrome.kill();
  process.exit(1);
}
