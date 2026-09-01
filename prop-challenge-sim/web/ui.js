/* ==========================================================================
   Terminal UI: candlestick chart, draggable position lines, day replay,
   and the Monte Carlo panel.  Everything runs against the same engine the
   Python suite tests -- the chart is a view of runChallenge(), not a
   re-implementation of it.
   ========================================================================== */

const $ = (id) => document.getElementById(id);
const pct = (x, d = 2) => (x * 100).toFixed(d) + '%';
const money = (x, d = 0) => (x < 0 ? '−$' : '$') +
  Math.abs(x).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
const px5 = (p) => p.toFixed(5);
const utc = (ms, withDate) => {
  const d = new Date(ms);
  const hm = String(d.getUTCHours()).padStart(2, '0') + ':' +
             String(d.getUTCMinutes()).padStart(2, '0');
  return withDate ? `${d.getUTCDate()} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getUTCMonth()]} ${hm}` : hm;
};
const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

const BARS = decodePackedBars(REAL_BARS);
const INST = INSTRUMENTS.EURUSD;
const COSTS = Object.assign({}, DEFAULT_COSTS.EURUSD);
const DAY_MS = 86400000;

const S = {
  i0: 0, n: 0, dir: 1, size: 0.45, ddMode: 'trailing_equity',
  entry: null, tp: null, sl: null, res: null, reveal: 0, playing: false,
  view0: 0, view1: 0, hover: null, drag: null, dragFrom: null, raf: 0,
  speed: 3,
};

const config = () => defaultConfig({ drawdownMode: S.ddMode, exposureBasis: 'margin' });

/* -- the strategy the terminal drives: one position, your levels ---------- */
function terminalStrategy(dir, size, entry, tpPrice, slPrice) {
  let done = false;
  return {
    onStart() { done = false; },
    onBar(ctx) {
      if (done || ctx.position) return null;
      const i = ctx.i;
      // A resting limit: it only fills on a bar that actually trades through it.
      if (entry < ctx.low[i] || entry > ctx.high[i]) return null;
      done = true;
      return { direction: dir, sizing: 'margin_pct', size, tpPrice, slPrice,
               fillPrice: entry };
    },
  };
}

const unitsAt = (price, size) =>
  size * 20000 * INST.leverage / (price * INST.pointValue);
const dollarsPerPrice = (price, size) => unitsAt(price, size) * INST.pointValue;

/* -- pick a real 24h window with a full trading day in it ----------------- */
function pickWindow(seed) {
  const r = rng(seed);
  const horizon = 24 * 3600000;
  const top = validStartRange(BARS, config());
  for (let tries = 0; tries < 400; tries++) {
    const i = Math.floor(r() * top);
    let j = i;
    while (j < BARS.ts.length && BARS.ts[j] < BARS.ts[i] + horizon) j++;
    if (j - i >= 1000) return { i0: i, n: j - i };
  }
  return { i0: 0, n: 1440 };
}

function resetLevels() {
  S.entry = BARS.close[S.i0];
  const dpp = dollarsPerPrice(S.entry, S.size);
  S.tp = S.entry + S.dir * (1500 / dpp);
  S.sl = S.entry - S.dir * (250 / dpp);
}

function runDay() {
  const cfg = config();
  S.res = runChallenge(BARS,
                       terminalStrategy(S.dir, S.size, S.entry, S.tp, S.sl),
                       INST, COSTS, cfg, rng(1), S.i0, null, true);
  if (!S.playing) S.reveal = S.n - 1;
  paintHUD();
}

/* ============================== chart ==================================== */

const cv = $('chart');
const ctx2 = cv.getContext('2d');
let W = 0, H = 0, PRICE_H = 0, EQ_H = 0;
const PADR = 92, PADB = 24, PADT = 10, GAP = 26;

function resize() {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  W = cv.clientWidth;
  H = Math.max(420, Math.min(620, Math.round(W * 0.46)));
  cv.style.height = H + 'px';
  cv.width = Math.round(W * dpr);
  cv.height = Math.round(H * dpr);
  ctx2.setTransform(dpr, 0, 0, dpr, 0, 0);
  PRICE_H = Math.round((H - PADB - GAP) * 0.74);
  EQ_H = H - PADB - GAP - PRICE_H;
  draw();
}

/* Display candles are aggregated from 1-minute bars so the chart reads like a
   chart: 1,440 one-pixel candles is a smear, not a price history. */
function aggregate() {
  const a = S.view0, b = S.view1;
  const span = b - a;
  const target = Math.max(60, Math.min(190, Math.round(W / 7)));
  const step = Math.max(1, Math.round(span / target));
  const out = [];
  for (let i = a; i < b; i += step) {
    const end = Math.min(b, i + step);
    let o = BARS.open[i], h = -Infinity, l = Infinity, c = BARS.close[end - 1];
    for (let k = i; k < end; k++) {
      if (BARS.high[k] > h) h = BARS.high[k];
      if (BARS.low[k] < l) l = BARS.low[k];
    }
    out.push({ i, end, ts: BARS.ts[i], o, h, l, c });
  }
  return { cands: out, step };
}

let LAYOUT = { cands: [], step: 1, bw: 6, lo: 0, hi: 1 };

function xOf(k) { return k * LAYOUT.bw + LAYOUT.bw / 2; }
function yOf(p) {
  const { lo, hi } = LAYOUT;
  return PADT + (PRICE_H - PADT) * (1 - (p - lo) / (hi - lo));
}
function priceAt(y) {
  const { lo, hi } = LAYOUT;
  return lo + (hi - lo) * (1 - (y - PADT) / (PRICE_H - PADT));
}
const eqTop = () => PRICE_H + GAP;
function yEq(v) {
  const { eqLo, eqHi } = LAYOUT;
  return eqTop() + EQ_H * (1 - (v - eqLo) / (eqHi - eqLo));
}

function draw() {
  if (!S.res) return;
  // During replay the chart tracks the head like a live feed, instead of
  // sitting still while a static window fills in.
  if (S.playing) {
    const head = S.i0 + S.reveal;
    const span = Math.max(140, Math.min(S.n, 460));
    S.view1 = Math.min(S.i0 + S.n, head + Math.round(span * 0.16));
    S.view0 = Math.max(S.i0, S.view1 - span);
  }
  const { cands, step } = aggregate();
  const plotW = W - PADR;
  LAYOUT.cands = cands; LAYOUT.step = step;
  LAYOUT.bw = plotW / cands.length;

  // Price scale is fixed to the whole visible window, including the levels, so
  // replay never makes the chart jump under the cursor.
  let lo = Infinity, hi = -Infinity;
  for (const c of cands) { if (c.l < lo) lo = c.l; if (c.h > hi) hi = c.h; }
  // Always keep the entry and the kill line in frame.  A far-off target is
  // allowed off-screen while replaying and gets an edge marker instead --
  // otherwise the candles are squeezed into a band and nothing reads.
  const must = S.playing ? [S.entry] : [S.entry, S.tp, S.sl];
  for (const v of must) if (isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  const upto = Math.min(S.reveal, S.res.curveFloorPx.length - 1);
  for (let q = 0; q <= upto; q++) {
    const v = S.res.curveFloorPx[q];
    if (isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  }
  const padp = (hi - lo) * 0.10 || 0.001;
  const tLo = lo - padp, tHi = hi + padp;
  if (S.playing && LAYOUT.lo != null && isFinite(LAYOUT.lo)) {
    LAYOUT.lo += (tLo - LAYOUT.lo) * 0.18;
    LAYOUT.hi += (tHi - LAYOUT.hi) * 0.18;
  } else { LAYOUT.lo = tLo; LAYOUT.hi = tHi; }

  const eq = S.res.curveEq, fl = S.res.curveFloor;
  const from = Math.max(0, S.view0 - S.i0);
  const to = Math.min(eq.length - 1, Math.min(S.reveal, S.view1 - S.i0));
  let eLo = Infinity, eHi = -Infinity;
  for (let q = from; q <= to; q++) {
    eLo = Math.min(eLo, eq[q], fl[q]); eHi = Math.max(eHi, eq[q], fl[q]);
  }
  if (!isFinite(eLo)) { eLo = 19700; eHi = 20000; }
  if (!S.playing) { eLo = Math.min(eLo, 19650); eHi = Math.max(eHi, 21550); }
  const epad = Math.max(30, (eHi - eLo) * 0.12);
  const teLo = eLo - epad, teHi = eHi + epad;
  if (S.playing && LAYOUT.eqLo != null && isFinite(LAYOUT.eqLo)) {
    LAYOUT.eqLo += (teLo - LAYOUT.eqLo) * 0.18;
    LAYOUT.eqHi += (teHi - LAYOUT.eqHi) * 0.18;
  } else { LAYOUT.eqLo = teLo; LAYOUT.eqHi = teHi; }

  const g = ctx2;
  g.clearRect(0, 0, W, H);
  g.fillStyle = cssVar('--panel');
  g.fillRect(0, 0, W, H);

  drawGrid(g, plotW);
  drawCandles(g, cands, step);
  drawLevels(g, plotW);
  drawEquity(g, plotW);
  drawTimeAxis(g, cands);
  drawCrosshair(g, plotW);
}

function drawGrid(g, plotW) {
  const ink = cssVar('--faint'), grid = cssVar('--grid');
  g.strokeStyle = grid; g.lineWidth = 1;
  g.fillStyle = ink; g.font = '10px ' + cssVar('--mono');
  g.textAlign = 'left'; g.textBaseline = 'middle';
  const ticks = 6;
  for (let t = 0; t <= ticks; t++) {
    const p = LAYOUT.lo + (LAYOUT.hi - LAYOUT.lo) * t / ticks;
    const y = Math.round(yOf(p)) + 0.5;
    g.beginPath(); g.moveTo(0, y); g.lineTo(plotW, y); g.stroke();
    g.fillText(p.toFixed(5), plotW + 8, y);
  }
  const eqSpan = LAYOUT.eqHi - LAYOUT.eqLo;
  const eqStep = eqSpan > 1400 ? 500 : eqSpan > 700 ? 250 : eqSpan > 300 ? 100 : 50;
  const first = Math.ceil(LAYOUT.eqLo / eqStep) * eqStep;
  for (let v = first; v <= LAYOUT.eqHi; v += eqStep) {
    const y = Math.round(yEq(v)) + 0.5;
    g.beginPath(); g.moveTo(0, y); g.lineTo(plotW, y); g.stroke();
    g.fillText(eqStep >= 250 ? (v / 1000).toFixed(1) + 'k'
                             : '$' + v.toLocaleString('en-US'), plotW + 8, y);
  }
}

function drawCandles(g, cands, step) {
  const upB = cssVar('--up-body'), up = cssVar('--up');
  const dnB = cssVar('--down-body'), dn = cssVar('--down');
  const bodyW = Math.max(1, Math.min(11, LAYOUT.bw * 0.66));
  const revealAbs = S.i0 + S.reveal;
  const exitAbs = S.i0 + S.res.curveEq.length - 1;
  for (let k = 0; k < cands.length; k++) {
    const c = cands[k];
    if (c.i > revealAbs) break;
    g.globalAlpha = c.i > exitAbs ? 0.3 : 1;
    // The candle straddling the replay head forms from the bars seen so far.
    let o = c.o, h = c.h, l = c.l, cl = c.c;
    if (c.end - 1 > revealAbs) {
      h = -Infinity; l = Infinity;
      for (let q = c.i; q <= revealAbs; q++) {
        if (BARS.high[q] > h) h = BARS.high[q];
        if (BARS.low[q] < l) l = BARS.low[q];
      }
      cl = BARS.close[revealAbs];
    }
    const rising = cl >= o;
    const x = xOf(k);
    g.strokeStyle = rising ? up : dn;
    g.lineWidth = 1;
    g.beginPath();
    g.moveTo(Math.round(x) + 0.5, yOf(h));
    g.lineTo(Math.round(x) + 0.5, yOf(l));
    g.stroke();
    const yo = yOf(o), yc = yOf(cl);
    const top = Math.min(yo, yc), hgt = Math.max(1, Math.abs(yc - yo));
    g.fillStyle = rising ? upB : dnB;
    g.fillRect(Math.round(x - bodyW / 2), Math.round(top), Math.round(bodyW), Math.round(hgt));
    g.strokeStyle = rising ? up : dn;
    g.strokeRect(Math.round(x - bodyW / 2) + 0.5, Math.round(top) + 0.5,
                 Math.round(bodyW) - 1, Math.round(hgt) - 1);
  }
  g.globalAlpha = 1;
}

function tag(g, x, y, text, color, align) {
  g.font = '600 10px ' + cssVar('--mono');
  const w = g.measureText(text).width + 10;
  const bx = align === 'right' ? x : x - w;
  g.fillStyle = color;
  g.fillRect(bx, y - 8, w, 16);
  g.fillStyle = cssVar('--panel');
  g.textAlign = 'left'; g.textBaseline = 'middle';
  g.fillText(text, bx + 5, y + 0.5);
}

function grip(g, x, y, color) {
  g.save();
  g.fillStyle = color;
  const w = 22, h = 13;
  g.beginPath();
  if (g.roundRect) g.roundRect(x - w, y - h / 2, w, h, 3);
  else g.rect(x - w, y - h / 2, w, h);
  g.fill();
  g.fillStyle = cssVar('--panel');
  for (let k = -1; k <= 1; k++) g.fillRect(x - w / 2 + k * 4 - 0.5, y - 3, 1.5, 6);
  g.restore();
}

function drawLevels(g, plotW) {
  const entry = S.entry;
  const dpp = dollarsPerPrice(entry, S.size);

  // Position box, TradingView style: the profit leg and the risk leg shaded.
  const yE = yOf(entry), yT = yOf(S.tp), yS = yOf(S.sl);
  g.fillStyle = cssVar('--tp'); g.globalAlpha = 0.09;
  g.fillRect(0, Math.min(yE, yT), plotW, Math.abs(yT - yE));
  g.fillStyle = cssVar('--sl'); g.globalAlpha = 0.09;
  g.fillRect(0, Math.min(yE, yS), plotW, Math.abs(yS - yE));
  g.globalAlpha = 1;

  const line = (y, color, dash, width) => {
    g.save(); g.strokeStyle = color; g.lineWidth = width || 1.5;
    g.setLineDash(dash || []);
    g.beginPath(); g.moveTo(0, Math.round(y) + 0.5); g.lineTo(plotW, Math.round(y) + 0.5);
    g.stroke(); g.restore();
  };
  line(yE, cssVar('--muted'), [5, 3], 1.5);
  line(yT, cssVar('--tp'), [], 1.5);
  line(yS, cssVar('--sl'), [], 1.5);

  // The liquidation price: stepped, because a trailing floor only ever ratchets.
  const fp = S.res.curveFloorPx;
  g.save();
  g.strokeStyle = cssVar('--kill'); g.lineWidth = 2; g.setLineDash([6, 4]);
  g.beginPath();
  let started = false;
  const cands = LAYOUT.cands;
  for (let k = 0; k < cands.length; k++) {
    const src = Math.min(cands[k].i - S.i0, S.reveal);
    if (src < 0 || cands[k].i - S.i0 > S.reveal) break;
    const v = fp[src];
    if (!isFinite(v)) { started = false; continue; }
    const x = xOf(k), y = yOf(v);
    if (!started) { g.moveTo(x, y); started = true; } else { g.lineTo(x, y); }
  }
  g.stroke(); g.restore();

  const clampY = (y) => Math.max(PADT + 7, Math.min(PRICE_H - 7, y));
  const arrow = (y, real) => real < PADT ? ' ▲' : (real > PRICE_H ? ' ▼' : '');
  tag(g, plotW, clampY(yE), px5(entry) + arrow(yE, yE), cssVar('--muted'), 'right');
  tag(g, plotW, clampY(yT), px5(S.tp) + arrow(yT, yT), cssVar('--tp'), 'right');
  tag(g, plotW, clampY(yS), px5(S.sl) + arrow(yS, yS), cssVar('--sl'), 'right');
  const lastFloor = lastFloorPx(S.reveal);
  tag(g, plotW, clampY(yOf(lastFloor)), px5(lastFloor), cssVar('--kill'), 'right');

  // Grab handles.  The lines were draggable before, but with nothing to show
  // for it -- which is the same as not being draggable.
  const gx = plotW - 8;
  if (yE > PADT && yE < PRICE_H) grip(g, gx, yE, cssVar('--muted'));
  if (yT > PADT && yT < PRICE_H) grip(g, gx, yT, cssVar('--tp'));
  if (yS > PADT && yS < PRICE_H) grip(g, gx, yS, cssVar('--sl'));

  g.font = '600 10px ' + cssVar('--mono');
  g.textAlign = 'left'; g.textBaseline = 'bottom';
  g.fillStyle = cssVar('--tp');
  g.fillText(`TAKE PROFIT  +${money(Math.abs(S.tp - entry) * dpp)}`, 7, yT - 4);
  g.fillStyle = cssVar('--sl');
  g.fillText(`STOP  −${money(Math.abs(S.sl - entry) * dpp)}`, 7, yS - 4);
  g.fillStyle = cssVar('--kill');
  if (Math.abs(yOf(lastFloor) - yS) > 13)
    g.fillText('LIQUIDATION', 7, yOf(lastFloor) - 4);
  g.fillStyle = cssVar('--muted');
  if (Math.abs(yE - yOf(lastFloor)) > 15 && Math.abs(yE - yS) > 15)
    g.fillText(S.res.trades.length ? 'ENTRY  filled' : 'ENTRY  limit — not filled',
               7, yE - 4);
}

function drawEquity(g, plotW) {
  const eq = S.res.curveEq, fl = S.res.curveFloor;
  const top = eqTop();
  g.save();
  g.strokeStyle = cssVar('--rule'); g.lineWidth = 1;
  g.beginPath(); g.moveTo(0, top - GAP / 2); g.lineTo(plotW, top - GAP / 2); g.stroke();
  g.restore();

  g.font = '9.5px ' + cssVar('--mono');
  g.fillStyle = cssVar('--muted');
  g.textAlign = 'left'; g.textBaseline = 'top';
  g.fillText('ACCOUNT EQUITY', 4, top - GAP / 2 + 5);

  const xForSrc = (s) => xOf((S.i0 + s - S.view0) / LAYOUT.step);
  const upto = Math.min(S.reveal, eq.length - 1);
  const from = Math.max(0, S.view0 - S.i0);   // scrolled off the left

  if (21500 >= LAYOUT.eqLo && 21500 <= LAYOUT.eqHi) {
    g.save();
    g.strokeStyle = cssVar('--tp'); g.setLineDash([4, 4]); g.lineWidth = 1;
    const yT = yEq(21500);
    g.beginPath(); g.moveTo(0, yT); g.lineTo(plotW, yT); g.stroke();
    g.restore();
  }

  const trace = (series, color, width) => {
    g.save();
    g.strokeStyle = color; g.lineWidth = width;
    g.beginPath();
    for (let q = from; q <= upto; q++) {
      const x = xForSrc(q), y = yEq(series[q]);
      q === from ? g.moveTo(x, y) : g.lineTo(x, y);
    }
    g.stroke(); g.restore();
  };
  trace(fl, cssVar('--kill'), 1.75);
  trace(eq, cssVar('--ink'), 1.75);

  if (upto >= from) {
    const x = xForSrc(upto), y = yEq(eq[upto]);
    const dead = S.res.outcome === 'FAIL_DRAWDOWN' && upto >= eq.length - 1;
    const won = S.res.outcome === 'PASS' && upto >= eq.length - 1;
    g.fillStyle = dead ? cssVar('--kill') : won ? cssVar('--pass') : cssVar('--ink');
    g.beginPath(); g.arc(x, y, 3.5, 0, Math.PI * 2); g.fill();
    tag(g, plotW, y, money(eq[upto]), g.fillStyle, 'right');
  }
}

function readout(c) {
  if (!c) return;
  $('ohlc').innerHTML = [['O', c.o], ['H', c.h], ['L', c.l], ['C', c.c]]
    .map(([k, v]) => `<span>${k} <b>${px5(v)}</b></span>`).join('');
}

function drawTimeAxis(g, cands) {
  g.font = '10px ' + cssVar('--mono');
  g.fillStyle = cssVar('--faint');
  g.textAlign = 'center'; g.textBaseline = 'top';
  const y = H - PADB + 5;
  const every = Math.max(1, Math.round(cands.length / 8));
  for (let k = 0; k < cands.length; k += every) {
    const x = xOf(k);
    if (x < 22 || x > W - PADR - 22) continue;
    g.fillText(utc(cands[k].ts, false), x, y);
  }
}

function drawCrosshair(g, plotW) {
  if (S.hover === null) return;
  const { x, y } = S.hover;
  if (x > plotW) return;
  g.save();
  g.strokeStyle = cssVar('--rule-2'); g.lineWidth = 1; g.setLineDash([2, 3]);
  g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H - PADB); g.stroke();
  g.beginPath(); g.moveTo(0, y); g.lineTo(plotW, y); g.stroke();
  g.restore();
  if (y < PRICE_H) tag(g, plotW, y, px5(priceAt(y)), cssVar('--rule-2'), 'right');
}

/* ============================ interaction ================================ */

function nearestLine(y) {
  const c = [['tp', yOf(S.tp)], ['sl', yOf(S.sl)], ['entry', yOf(S.entry)]]
    .map(([k, ly]) => [k, Math.abs(y - ly)])
    .sort((a, b) => a[1] - b[1])[0];
  return c && c[1] < 11 ? c[0] : null;
}

cv.addEventListener('pointermove', (e) => {
  const r = cv.getBoundingClientRect();
  const x = e.clientX - r.left, y = e.clientY - r.top;
  S.hover = { x, y };

  if (S.drag) {
    const p = priceAt(y);
    const minGap = 0.00005;
    if (S.drag === 'entry') {
      // Move the whole position, the way a position tool does: the target and
      // the stop keep the distances you set.
      const d = p - S.entry;
      S.entry = p; S.tp += d; S.sl += d;
    } else if (S.drag === 'tp') {
      S.tp = S.dir > 0 ? Math.max(p, S.entry + minGap) : Math.min(p, S.entry - minGap);
    } else {
      S.sl = S.dir > 0 ? Math.min(p, S.entry - minGap) : Math.max(p, S.entry + minGap);
    }
    if (!S.raf) S.raf = requestAnimationFrame(() => { S.raf = 0; runDay(); draw(); });
    return;
  }
  cv.style.cursor = y < PRICE_H && nearestLine(y) ? 'grab' : 'crosshair';

  const k = Math.max(0, Math.min(LAYOUT.cands.length - 1, Math.floor(x / LAYOUT.bw)));
  const c = LAYOUT.cands[k];
  if (c) { readout(c); $('clock').textContent = utc(c.ts, true) + ' UTC'; }
  draw();
});
cv.addEventListener('pointerleave', () => { S.hover = null; draw(); });
cv.addEventListener('pointerdown', (e) => {
  const r = cv.getBoundingClientRect();
  const y = e.clientY - r.top;
  const hit = y < PRICE_H ? nearestLine(y) : null;
  if (hit) { S.drag = hit; cv.style.cursor = 'grabbing';
             cv.setPointerCapture(e.pointerId); }
});
cv.addEventListener('pointerup', (e) => {
  if (S.drag) { S.drag = null; cv.releasePointerCapture(e.pointerId); runDay(); draw(); }
});
cv.addEventListener('wheel', (e) => {
  e.preventDefault();
  const span = S.view1 - S.view0;
  const f = e.deltaY > 0 ? 1.18 : 0.85;
  const next = Math.max(60, Math.min(S.n, Math.round(span * f)));
  const r = cv.getBoundingClientRect();
  const frac = Math.max(0, Math.min(1, (e.clientX - r.left) / (W - PADR)));
  const anchor = S.view0 + span * frac;
  S.view0 = Math.max(S.i0, Math.round(anchor - next * frac));
  S.view1 = Math.min(S.i0 + S.n, S.view0 + next);
  S.view0 = Math.max(S.i0, S.view1 - next);
  draw();
}, { passive: false });

/* ============================== replay =================================== */

let playTimer = 0;
function play() {
  if (S.playing) { stop(); return; }
  S.playing = true;
  S.reveal = 0;
  $('play').textContent = '■ Stop';
  const total = S.n - 1;
  const t0 = performance.now();
  const dur = 10000 / S.speed;
  const tick = (t) => {
    if (!S.playing) return;
    const f = Math.min(1, (t - t0) / dur);
    S.reveal = Math.round(total * f);
    paintHUD(); draw();
    if (f < 1) playTimer = requestAnimationFrame(tick); else stop();
  };
  playTimer = requestAnimationFrame(tick);
}
function stop() {
  S.playing = false;
  cancelAnimationFrame(playTimer);
  S.reveal = S.n - 1;
  $('play').textContent = '▶ Replay the day';
  paintHUD(); draw();
}

/** Last finite liquidation price at or before ``k`` -- it is NaN while flat,
    but "where the account would have died" is exactly what stays interesting
    after the position closes. */
function lastFloorPx(k) {
  const fp = S.res.curveFloorPx;
  for (let j = Math.min(k, fp.length - 1); j >= 0; j--)
    if (isFinite(fp[j])) return fp[j];
  return BARS.close[S.i0];
}

function paintHUD() {
  const r = S.res, k = Math.min(S.reveal, r.curveEq.length - 1);
  const eq = r.curveEq[k], fl = r.curveFloor[k];
  const cfg = config();
  const bal = k >= r.curveEq.length - 1 ? r.finalBalance : eq;
  $('hBal').textContent = money(bal, 0);
  $('hEq').textContent = money(eq, 0);
  const room = eq - fl;
  $('hRoom').textContent = money(room, 0);
  $('hRoom').style.color = room < 100 ? cssVar('--kill') : cssVar('--ink');
  const togo = cfg.startingBalance + cfg.profitTarget - eq;
  $('hTarget').textContent = togo <= 0 ? 'reached' : money(togo, 0);

  const entry = S.entry;
  const dpp = dollarsPerPrice(entry, S.size);
  $('lEntry').textContent = px5(entry) +
    (r.trades.length ? '  filled' : '  waiting');
  $('lTP').textContent = `${px5(S.tp)}  +${money(Math.abs(S.tp - entry) * dpp)}`;
  $('lSL').textContent = `${px5(S.sl)}  −${money(Math.abs(S.sl - entry) * dpp)}`;
  $('lKill').textContent = px5(lastFloorPx(k));

  const done = k >= r.curveEq.length - 1;
  const v = $('verdict');
  if (!done) { v.className = 'tag live'; v.textContent = 'IN TRADE'; }
  else if (r.outcome === 'PASS') { v.className = 'tag pass'; v.textContent = 'PASSED  +$5,000'; }
  else if (r.outcome === 'FAIL_DRAWDOWN') {
    v.className = 'tag fail';
    v.textContent = 'LIQUIDATED  ' + money(-cfg.entryFee);
  } else { v.className = 'tag fail'; v.textContent = '24H EXPIRED  ' + money(-cfg.entryFee); }
}

/* ============================== controls ================================= */

function newWindow(seed) {
  const w = pickWindow(seed);
  S.i0 = w.i0; S.n = w.n;
  S.view0 = S.i0; S.view1 = S.i0 + S.n;
  resetLevels();
  runDay();
  $('clock').textContent = utc(BARS.ts[S.i0], true) + ' UTC';
  const a = BARS.ts[S.i0], b = BARS.ts[Math.min(S.i0 + S.n - 1, BARS.ts.length - 1)];
  $('windowNote').textContent =
    `${utc(a, true)} → ${utc(b, true)} UTC · ${S.n.toLocaleString()} one-minute bars`;
  draw();
  readout(LAYOUT.cands[LAYOUT.cands.length - 1]);
}

$('play').onclick = play;
$('shuffle').onclick = () => { stop(); newWindow((Math.random() * 1e9) | 0); };
$('dLong').onclick = () => setDir(1);
$('dShort').onclick = () => setDir(-1);
function setDir(d) {
  S.dir = d;
  $('dLong').setAttribute('aria-pressed', String(d === 1));
  $('dShort').setAttribute('aria-pressed', String(d === -1));
  resetLevels(); runDay(); stop();
}
$('cDD').onchange = () => { S.ddMode = $('cDD').value; runDay(); stop(); };
for (const b of document.querySelectorAll('[data-speed]')) {
  b.onclick = () => {
    S.speed = +b.dataset.speed;
    for (const o of document.querySelectorAll('[data-speed]'))
      o.setAttribute('aria-pressed', String(o === b));
  };
}
$('cSize').oninput = () => {
  S.size = +$('cSize').value / 100;
  $('vSize').textContent = $('cSize').value + '%';
  resetLevels(); runDay(); draw(); paintHUD();
};

/* ============================ monte carlo ================================ */

const ATTEMPTS = [1000, 2500, 5000, 10000];
const mc = () => ({
  strat: $('mStrat').value, sl: +$('mSL').value, tp: +$('mTP').value,
  n: ATTEMPTS[+$('mN').value - 1],
});
function syncMC() {
  const c = mc();
  $('vSL2').textContent = '$' + c.sl + (c.sl >= 300 ? ' — unreachable' : '');
  $('vTP2').textContent = '$' + c.tp;
  $('vN').textContent = c.n.toLocaleString('en-US');
}
['mSL', 'mTP', 'mN'].forEach(id => { $(id).oninput = syncMC; });

function chunked(total, step, work, done, onProgress) {
  let i = 0;
  const tick = () => {
    const end = Math.min(total, i + step);
    work(i, end); i = end;
    if (onProgress) onProgress(i / total);
    if (i < total) requestAnimationFrame(tick); else done();
  };
  requestAnimationFrame(tick);
}

function monteCarlo(cfg, name, params, n, seed, onProgress, done, boot = 800) {
  const { starts, rejected } = sampleStarts(BARS, cfg, n, seed, 240);
  const hs = halfSpreadSeries(BARS, COSTS);
  const strategy = STRATEGIES[name](params);
  const attempts = [];
  chunked(starts.length, 400, (a, b) => {
    for (let k = a; k < b; k++) {
      const r = runChallenge(BARS, strategy, INST, COSTS, cfg,
                             rng(seed * 1000003 + k), starts[k], hs, false);
      attempts.push({ outcome: r.outcome, startTs: r.startTs,
                      maxDrawdown: r.maxDrawdownReached,
                      totalCosts: r.totalCosts, nTrades: r.trades.length });
    }
  }, () => done(summarise(attempts, cfg, rejected, independentWindows(BARS, cfg), boot)),
     onProgress);
}

function renderSummary(s) {
  const be = s.breakeven;
  const top = Math.max(0.2, s.passRate * 1.35, be * 1.6);
  $('bigRate').textContent = pct(s.passRate);
  $('bigRate').style.color = s.passRate >= be ? cssVar('--pass') : cssVar('--ink');
  $('bigSub').innerHTML = s.passRate >= be
    ? 'pass rate — <b style="color:var(--pass)">above</b> the 10% breakeven'
    : 'pass rate — you need <b>10%</b> to break even on the $500 fee';
  $('meterFill').style.width = Math.min(100, s.passRate / top * 100) + '%';
  $('meterFill').style.background = s.passRate >= be ? cssVar('--pass') : cssVar('--dd');
  $('meterBE').style.left = (be / top * 100) + '%';
  $('meterMax').textContent = pct(top, 0);
  $('stack').innerHTML = [['nPass', '--pass'], ['nDD', '--dd'], ['nTO', '--timeout']]
    .map(([k, c]) => {
      const share = s.n ? s[k] / s.n : 0;
      return `<div style="flex:${Math.max(share, 0.001)} 1 0; background:var(${c})">` +
             `${share > 0.09 ? pct(share, 1) : ''}</div>`;
    }).join('');
  $('stats').innerHTML = [
    ['EV per $500 attempt', money(s.ev), s.ev >= 0 ? 'var(--pass)' : 'var(--dd)'],
    ['95% interval', `${pct(s.cluster[0], 1)} – ${pct(s.cluster[1], 1)}`, ''],
    ['Failed on drawdown', pct(s.n ? s.nDD / s.n : 0, 1), ''],
    ['Ran out of time', pct(s.n ? s.nTO / s.n : 0, 1), ''],
    ['Median max drawdown', money(s.medianDD), ''],
    ['Mean costs paid', '$' + s.meanCosts.toFixed(2), ''],
    ['Mean trades', s.meanTrades.toFixed(1), ''],
    ['Independent windows', s.indepWindows.toLocaleString('en-US'), ''],
  ].map(([k, v, col]) => `<div><dt>${k}</dt><dd${col ? ` style="color:${col}"` : ''}>${v}</dd></div>`).join('');
}

function busy(on, label) {
  $('runBtn').disabled = on;
  $('runBtn').textContent = on ? (label || 'Simulating…') : 'Run Monte Carlo';
  $('prog').parentElement.classList.toggle('on', on);
  if (!on) $('prog').style.width = '0';
}
const setProgress = (f) => { $('prog').style.width = (f * 100) + '%'; };

function runMC(then) {
  const c = mc();
  const cfg = defaultConfig({ drawdownMode: S.ddMode, exposureBasis: 'margin' });
  const params = { size: S.size, tpDollars: c.tp, slDollars: c.sl,
                   entriesPerDay: 8, lookback: 30 };
  busy(true);
  monteCarlo(cfg, c.strat, params, c.n, 12345, setProgress, (s) => {
    renderSummary(s); busy(false); if (then) then();
  });
}
$('runBtn').onclick = () => runMC();

/* ---- the rulebook table, computed on the same real data ---- */
const RULE_ROWS = [
  ['Buy and hold', 'buy_and_hold', { size: 0.45 }],
  ['Fixed TP/SL', 'fixed_tp_sl', { size: 0.45, tpDollars: 900, slDollars: 150, entriesPerDay: 8 }],
  ['Momentum', 'momentum', { size: 0.45, tpDollars: 900, slDollars: 150, lookback: 30 }],
];
function buildTable(done) {
  const jobs = [];
  for (const [label, name, p] of RULE_ROWS)
    for (const [mode, ml] of [['trailing_equity', 'Trailing equity'], ['static', 'Static $19,700']])
      jobs.push({ label, name, p, mode, ml });
  const rows = [];
  let k = 0;
  const step = () => {
    if (k >= jobs.length) { $('ruleBody').innerHTML = rows.join(''); return done(); }
    const j = jobs[k++];
    monteCarlo(defaultConfig({ drawdownMode: j.mode, exposureBasis: 'margin' }),
      j.name, j.p, 2500, 2024, null, (s) => {
        const hot = s.passRate >= s.breakeven;
        rows.push(`<tr class="${hot ? 'hot' : ''}"><td>${j.label}</td><td>${j.ml}</td>` +
          `<td style="font-weight:600;color:${hot ? 'var(--pass)' : 'var(--ink)'}">${pct(s.passRate)}</td>` +
          `<td style="color:var(--muted)">${pct(s.cluster[0], 1)} – ${pct(s.cluster[1], 1)}</td>` +
          `<td>${pct(s.nDD / s.n, 1)}</td><td>${pct(s.nTO / s.n, 1)}</td>` +
          `<td style="color:${s.ev >= 0 ? 'var(--pass)' : 'var(--dd)'}">${money(s.ev)}</td></tr>`);
        $('ruleBody').innerHTML = rows.join('');
        step();
      }, 600);
  };
  step();
}

/* ================================ boot =================================== */

/** Find a starting window that ends the way most of them do: liquidated, after
    long enough in the trade for the ratchet to be visible on the chart. */
function representativeWindow() {
  const cfg = config();
  for (let seed = 1; seed < 400; seed++) {
    const w = pickWindow(seed * 7919);
    const entry = BARS.close[w.i0];
    const dpp = dollarsPerPrice(entry, S.size);
    const res = runChallenge(BARS,
      terminalStrategy(1, S.size, entry, entry + 1500 / dpp, entry - 250 / dpp),
      INST, COSTS, cfg, rng(1), w.i0, null, true);
    if (res.outcome === 'FAIL_DRAWDOWN' && res.curveEq.length > 220 &&
        res.curveEq.length < 900) return seed * 7919;
  }
  return 20240117;
}

function boot() {
  const days = (BARS.ts[BARS.ts.length - 1] - BARS.ts[0]) / DAY_MS;
  const first = new Date(BARS.ts[0]), last = new Date(BARS.ts[BARS.ts.length - 1]);
  const fmt = (d) => `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
  $('srcMeta').textContent =
    `${BARS.ts.length.toLocaleString('en-US')} real 1-minute bars · ${fmt(first)} to ${fmt(last)}`;
  $('dsDays').textContent = Math.round(days);
  syncMC();
  resize();
  newWindow(representativeWindow());
  busy(true, 'Simulating…');
  runMC(() => { busy(true, 'Building table…'); buildTable(() => busy(false)); });
}

window.addEventListener('resize', () => { resize(); });
matchMedia('(prefers-color-scheme:dark)').addEventListener('change', draw);
boot();
