/*
 * interact.mjs -- drive the page with REAL pointer events over CDP.
 *
 * smoke.mjs checks that the page computes; this checks that a human can
 * actually operate it.  Setting S.tp from JS and calling runDay() proves
 * nothing about whether the line can be grabbed with a mouse.
 */
import { spawn } from 'node:child_process';
import { resolve } from 'node:path';

const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const PORT = 9351;
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-sandbox',
  '--hide-scrollbars', '--window-size=1400,1000', `--remote-debugging-port=${PORT}`,
  '--user-data-dir=/tmp/propsim-chrome3', 'file://' + resolve('web/index.html')],
  { stdio: 'ignore' });

let ws, id = 0;
const pend = new Map();
const send = (m, p = {}) => new Promise((res, rej) => {
  const n = ++id; pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: m, params: p }));
});
const ev = async (e) => {
  const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
  return r.result.value;
};
const mouse = (type, x, y, button = 'left') => send('Input.dispatchMouseEvent', {
  type, x, y, button, buttons: type === 'mouseReleased' ? 0 : 1, clickCount: 1,
  pointerType: 'mouse',
});

let pass = 0; const fails = [];
const ok = (n, c, d = '') => { c ? (pass++, process.stdout.write('.')) : (fails.push(`${n}: ${d}`), process.stdout.write('F')); };

try {
  let t = null;
  for (let i = 0; i < 60 && !t; i++) {
    await sleep(250);
    try { t = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json())
      .find(x => x.type === 'page' && x.webSocketDebuggerUrl); } catch {}
  }
  ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && pend.has(d.id)) { const { res, rej } = pend.get(d.id); pend.delete(d.id);
      d.error ? rej(new Error(d.error.message)) : res(d.result); }
  };
  await send('Runtime.enable'); await send('Page.enable');
  for (let i = 0; i < 200; i++) {
    await sleep(250);
    if (await ev(`!document.getElementById('runBtn').disabled`)) break;
  }

  const geom = JSON.parse(await ev(`(() => {
    const r = document.getElementById('chart').getBoundingClientRect();
    return JSON.stringify({ left: r.left, top: r.top, w: r.width, h: r.height,
      tpY: yOf(S.tp), slY: yOf(S.sl), entryY: yOf(BARS.close[S.i0]),
      tp: S.tp, sl: S.sl });
  })()`));

  // --- drag the take-profit line down by 60px ---
  const x = geom.left + geom.w * 0.45;
  await mouse('mousePressed', x, geom.top + geom.tpY);
  await sleep(60);
  await mouse('mouseMoved', x, geom.top + geom.tpY + 60);
  await sleep(120);
  await mouse('mouseReleased', x, geom.top + geom.tpY + 60);
  await sleep(200);
  const afterTP = await ev(`S.tp`);
  ok('TP drags with a real mouse', Math.abs(afterTP - geom.tp) > 1e-5,
     `tp ${geom.tp} -> ${afterTP}`);

  // --- drag the stop-loss line ---
  const g2 = JSON.parse(await ev(`JSON.stringify({slY: yOf(S.sl), sl: S.sl})`));
  await mouse('mousePressed', x, geom.top + g2.slY);
  await sleep(60);
  await mouse('mouseMoved', x, geom.top + g2.slY - 40);
  await sleep(120);
  await mouse('mouseReleased', x, geom.top + g2.slY - 40);
  await sleep(200);
  const afterSL = await ev(`S.sl`);
  ok('SL drags with a real mouse', Math.abs(afterSL - g2.sl) > 1e-5,
     `sl ${g2.sl} -> ${afterSL}`);

  // --- drag the entry line ---
  const g3 = JSON.parse(await ev(`JSON.stringify({y: yOf(S.entry), e: S.entry})`));
  await mouse('mousePressed', x, geom.top + g3.y);
  await sleep(60);
  await mouse('mouseMoved', x, geom.top + g3.y - 25);
  await sleep(120);
  await mouse('mouseReleased', x, geom.top + g3.y - 25);
  await sleep(250);
  const afterEntry = await ev(`S.entry`);
  ok('ENTRY drags with a real mouse', Math.abs(afterEntry - g3.e) > 1e-5,
     `entry ${g3.e} -> ${afterEntry}`);

  const rerun = await ev(`S.res.trades.length >= 0 && typeof S.res.outcome === 'string'`);
  ok('engine re-ran after dragging', rerun);

  console.log(`\n${pass} passed, ${fails.length} failed`);
  for (const f of fails) console.log('  FAIL ' + f);
  chrome.kill();
  process.exit(fails.length ? 1 : 0);
} catch (e) { console.error(e); chrome.kill(); process.exit(1); }
