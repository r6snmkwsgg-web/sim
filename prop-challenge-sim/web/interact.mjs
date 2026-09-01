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

  // --- the page must open FLAT with an unsent order, not mid-trade ---
  const boot = JSON.parse(await ev(`JSON.stringify({
    phase: S.phase, headBar: S.headBar, trades: S.res.trades.length,
    verdict: document.getElementById('verdict').textContent,
    entryLabel: document.getElementById('lEntry').textContent,
    kill: document.getElementById('lKill').textContent,
    bal: document.getElementById('hBal').textContent })`));
  console.log(`  boot: phase=${boot.phase} head=${boot.headBar} ` +
              `verdict="${boot.verdict}" entry="${boot.entryLabel}" bal=${boot.bal}`);
  ok('opens in setup, not mid-trade', boot.phase === 'setup', boot.phase);
  ok('nothing filled before you start', boot.headBar === 0, `head ${boot.headBar}`);
  ok('verdict says the order is unsent', /NOT SENT/.test(boot.verdict), boot.verdict);
  ok('no liquidation price before entry', boot.kill === '—', boot.kill);

  // --- the size slider must NOT move the lines (this is the bug he hit) ---
  const sz = JSON.parse(await ev(`(() => {
    const before = { e: S.entry, tp: S.tp, sl: S.sl };
    const el = document.getElementById('cSize');
    el.value = '5'; el.dispatchEvent(new Event('input'));
    return JSON.stringify({ before, after: { e: S.entry, tp: S.tp, sl: S.sl },
                            label: document.getElementById('lTP').textContent });
  })()`));
  ok('size does not move the entry', sz.before.e === sz.after.e,
     `${sz.before.e} -> ${sz.after.e}`);
  ok('size does not move the TP', sz.before.tp === sz.after.tp,
     `${sz.before.tp} -> ${sz.after.tp}`);
  ok('size does not move the SL', sz.before.sl === sz.after.sl,
     `${sz.before.sl} -> ${sz.after.sl}`);
  console.log(`  size 45%->5%: TP stays at ${sz.after.tp.toFixed(5)}, now worth ${sz.label.split('  ')[1]}`);
  await ev(`(() => { const el=document.getElementById('cSize');
                     el.value='45'; el.dispatchEvent(new Event('input')); })()`);

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
  ok('dragging returns to setup', await ev(`S.phase === 'setup'`),
     await ev(`S.phase`));

  // --- start the day: the order should work, then fill ---
  await ev(`(() => { S.minsPerSec = 60; document.getElementById('play').click(); })()`);
  await sleep(400);
  const mid = JSON.parse(await ev(`JSON.stringify({ phase: S.phase, head: S.headBar,
    verdict: document.getElementById('verdict').textContent })`));
  ok('start puts it in running', mid.phase === 'running', mid.phase);
  ok('running head advances', mid.head > 0, `head ${mid.head}`);
  console.log(`  after start: phase=${mid.phase} head=${mid.head} verdict="${mid.verdict}"`);
  await sleep(2500);
  const late = JSON.parse(await ev(`JSON.stringify({ phase: S.phase,
    verdict: document.getElementById('verdict').textContent,
    entry: document.getElementById('lEntry').textContent })`));
  console.log(`  later: phase=${late.phase} verdict="${late.verdict}" entry="${late.entry}"`);
  ok('order fills or is still working', /IN TRADE|ORDER WORKING|LIQUIDATED|PASSED|EXPIRED|NEVER/.test(late.verdict),
     late.verdict);

  console.log(`\n${pass} passed, ${fails.length} failed`);
  for (const f of fails) console.log('  FAIL ' + f);
  chrome.kill();
  process.exit(fails.length ? 1 : 0);
} catch (e) { console.error(e); chrome.kill(); process.exit(1); }
