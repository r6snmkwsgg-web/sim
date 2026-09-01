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
  entry: null, tp: null, sl: null, res: null,
  // 'setup'   -- flat, your order rests in front of the market, nothing filled
  // 'running' -- the day is playing forward
  // 'done'    -- decided; the whole attempt is on screen
  phase: 'setup',
  // Replay clock.  headBar is the last completed minute; headFrac walks
  // through the bar that is still forming, which is what makes it read as a
  // market rather than a slideshow.
  headBar: 0, headFrac: 1, playing: false, lastT: 0,
  tf: 5,            // minutes per candle
  bw: 8,            // pixels per candle
  minsPerSec: 5,    // replay speed in market minutes per wall second
  follow: true, panCandles: 0,
  hover: null, drag: null, raf: 0, lastTick: 0, tickDir: 0,
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

/** Only on a new window or a direction flip.  Never on a size change: moving
    somebody's lines because they touched a slider is how you lose their
    order. */
function resetLevels() {
  const px = BARS.close[S.i0];
  S.entry = px - S.dir * 0.0004;          // a resting limit, 4 pips in front
  const dpp = dollarsPerPrice(S.entry, S.size);
  S.tp = S.entry + S.dir * (1500 / dpp);
  S.sl = S.entry - S.dir * (250 / dpp);
}

/** What kind of order the entry line currently is, relative to the price the
    day opens at. */
function orderKind() {
  const px = BARS.close[S.i0];
  const side = S.dir > 0 ? 'BUY' : 'SELL';
  if (Math.abs(S.entry - px) < 1e-6) return side + ' MARKET';
  const below = S.entry < px;
  return side + ' ' + ((S.dir > 0) === below ? 'LIMIT' : 'STOP');
}

function setPhase(p) {
  S.phase = p;
  if (p === 'setup') { S.headBar = 0; S.headFrac = 1; S.panCandles = 0; }
  if (p === 'done') { S.headBar = exitBar(); S.headFrac = 1; }
  const play = $('play');
  play.textContent = p === 'running' ? '■ Stop'
    : p === 'done' ? '▶ Replay again' : '▶ Start the day';
  $('pause').disabled = p !== 'running';
  $('hint').innerHTML = p === 'setup'
    ? 'place your order — drag the entry, TP and SL by their handles, then press start'
    : 'drag any line to re-arm the order &nbsp;·&nbsp; scroll to zoom';
}

/** Bar at which the attempt is decided -- the replay ends here, because
    nothing after it is your trade. */
function exitBar() {
  return Math.max(0, S.res.curveEq.length - 1);
}

function runDay() {
  const cfg = config();
  S.res = runChallenge(BARS,
                       terminalStrategy(S.dir, S.size, S.entry, S.tp, S.sl),
                       INST, COSTS, cfg, rng(1), S.i0, null, true);
  if (S.phase === 'done') { S.headBar = exitBar(); S.headFrac = 1; }
  else if (S.phase === 'setup') { S.headBar = 0; S.headFrac = 1; }
  paintHUD();
}

/* ============================== chart ==================================== */

const cv = $('chart');
const ctx2 = cv.getContext('2d');
let W = 0, H = 0, PRICE_H = 0, EQ_H = 0;
const PADR = 92, PADB = 24, PADT = 10, GAP = 26, RIGHT_GAP = 62;

function resize() {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  W = cv.clientWidth;
  H = Math.max(430, Math.min(640, Math.round(W * 0.48)));
  cv.style.height = H + 'px';
  cv.width = Math.round(W * dpr);
  cv.height = Math.round(H * dpr);
  ctx2.setTransform(dpr, 0, 0, dpr, 0, 0);
  PRICE_H = Math.round((H - PADB - GAP) * 0.72);
  EQ_H = H - PADB - GAP - PRICE_H;
  draw();
}

/**
 * Where price plausibly went inside a one-minute bar.
 *
 * OHLC records four numbers and no order.  An up bar is drawn as
 * open -> low -> high -> close and a down bar as open -> high -> low -> close,
 * with the fraction spread along the path by distance so the tick speed is
 * even.  This is a rendering convention for the forming candle only -- the
 * engine never uses it, and its drawdown checks still mark the true extremes.
 */
function intrabarPath(b) {
  const o = BARS.open[b], h = BARS.high[b], l = BARS.low[b], c = BARS.close[b];
  const up = c >= o;
  const pts = up ? [o, l, h, c] : [o, h, l, c];
  const legs = [];
  let total = 0;
  for (let k = 0; k < 3; k++) {
    const d = Math.abs(pts[k + 1] - pts[k]);
    legs.push(d); total += d;
  }
  return { pts, legs, total };
}

function intrabarPrice(b, f) {
  const { pts, legs, total } = intrabarPath(b);
  if (total <= 0) return pts[3];
  let want = f * total;
  for (let k = 0; k < 3; k++) {
    if (want <= legs[k] || k === 2) {
      const t = legs[k] > 0 ? Math.min(1, want / legs[k]) : 1;
      return pts[k] + (pts[k + 1] - pts[k]) * t;
    }
    want -= legs[k];
  }
  return pts[3];
}

/** High/low traced so far inside the forming bar. */
function intrabarExtremes(b, f) {
  const { pts, legs, total } = intrabarPath(b);
  let hi = pts[0], lo = pts[0];
  if (total <= 0) return [hi, lo];
  let want = f * total;
  for (let k = 0; k < 3; k++) {
    const t = legs[k] > 0 ? Math.max(0, Math.min(1, want / legs[k])) : 1;
    const p = pts[k] + (pts[k + 1] - pts[k]) * t;
    hi = Math.max(hi, p); lo = Math.min(lo, p);
    want -= legs[k];
    if (want <= 0) break;
  }
  return [hi, lo];
}

/** Fractional position of the replay head, measured in candles. */
const headCandleF = () => (S.headBar + S.headFrac) / S.tf;
const livePrice = () => S.headFrac >= 1
  ? BARS.close[S.i0 + S.headBar]
  : intrabarPrice(S.i0 + S.headBar, S.headFrac);

let LAYOUT = { lo: null, hi: null, eqLo: null, eqHi: null, first: 0, last: 0 };

/* x is anchored to the head so the whole chart slides continuously left as
   the forming bar fills -- not in one-candle jumps. */
function xOfCandle(j) {
  return (W - PADR) - RIGHT_GAP - (headCandleF() - S.panCandles - j) * S.bw;
}
function candleAtX(x) {
  return headCandleF() - S.panCandles - ((W - PADR) - RIGHT_GAP - x) / S.bw;
}
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

/** Aggregate one candle index into OHLC, honouring the replay head. */
function candleAt(j) {
  const a = j * S.tf;
  if (a > S.headBar) return null;
  if (S.i0 + a < 0) return null;               // before the dataset begins
  const bEnd = Math.min(S.n - 1, S.headBar, (j + 1) * S.tf - 1);
  let o = BARS.open[S.i0 + a], h = -Infinity, l = Infinity;
  for (let k = a; k <= bEnd; k++) {
    if (BARS.high[S.i0 + k] > h) h = BARS.high[S.i0 + k];
    if (BARS.low[S.i0 + k] < l) l = BARS.low[S.i0 + k];
  }
  let c = BARS.close[S.i0 + bEnd];
  const forming = bEnd === S.headBar && S.headFrac < 1;
  if (forming) {
    // Re-derive the head bar from the partial path instead of its finished OHLC.
    h = -Infinity; l = Infinity;
    for (let k = a; k < S.headBar; k++) {
      if (BARS.high[S.i0 + k] > h) h = BARS.high[S.i0 + k];
      if (BARS.low[S.i0 + k] < l) l = BARS.low[S.i0 + k];
    }
    const [ph, pl] = intrabarExtremes(S.i0 + S.headBar, S.headFrac);
    h = Math.max(h === -Infinity ? ph : h, ph);
    l = Math.min(l === Infinity ? pl : l, pl);
    c = intrabarPrice(S.i0 + S.headBar, S.headFrac);
  }
  return { j, o, h, l, c, forming, ts: BARS.ts[S.i0 + a] };
}

function visibleCandles() {
  const out = [];
  const jHead = Math.floor(headCandleF() - S.panCandles);
  const span = Math.ceil(((W - PADR) - RIGHT_GAP) / S.bw) + 2;
  // Setup has no future to draw, so fill the pane with real history; while
  // running, keep the lead-in short so the price scale stays on the trade.
  const HISTORY = S.phase === 'setup' ? span : 34;
  for (let j = Math.max(jHead - span, -HISTORY); j <= jHead; j++) {
    const c = candleAt(j);
    if (c) out.push(c);
  }
  return out;
}

function draw() {
  if (!S.res) return;
  const plotW = W - PADR;
  const cands = visibleCandles();
  LAYOUT.cands = cands;

  let lo = Infinity, hi = -Infinity;
  for (const c of cands) { if (c.l < lo) lo = c.l; if (c.h > hi) hi = c.h; }
  const must = S.playing ? [S.entry] : [S.entry, S.tp, S.sl];
  for (const v of must) if (isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  const upto = Math.min(S.headBar, S.res.curveFloorPx.length - 1);
  for (let q = Math.max(0, upto - 600); q <= upto; q++) {
    const v = S.res.curveFloorPx[q];
    if (isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  }
  if (!isFinite(lo)) { lo = BARS.close[S.i0] * 0.999; hi = BARS.close[S.i0] * 1.001; }
  const padp = (hi - lo) * 0.12 || 0.0005;
  const tLo = lo - padp, tHi = hi + padp;
  if (S.playing && LAYOUT.lo != null) {
    LAYOUT.lo += (tLo - LAYOUT.lo) * 0.12;
    LAYOUT.hi += (tHi - LAYOUT.hi) * 0.12;
  } else { LAYOUT.lo = tLo; LAYOUT.hi = tHi; }

  const eq = S.res.curveEq, fl = S.res.curveFloor;
  const from = Math.max(0, Math.floor((headCandleF() - S.panCandles) * S.tf) -
                           Math.ceil(plotW / S.bw) * S.tf);
  const to = Math.min(eq.length - 1, S.headBar);
  let eLo = Infinity, eHi = -Infinity;
  for (let q = Math.max(0, from); q <= to; q++) {
    eLo = Math.min(eLo, eq[q], fl[q]); eHi = Math.max(eHi, eq[q], fl[q]);
  }
  if (!isFinite(eLo)) { eLo = 19700; eHi = 20050; }
  if (!S.playing) { eLo = Math.min(eLo, 19650); eHi = Math.max(eHi, 20200); }
  const epad = Math.max(25, (eHi - eLo) * 0.14);
  const teLo = eLo - epad, teHi = eHi + epad;
  if (S.playing && LAYOUT.eqLo != null) {
    LAYOUT.eqLo += (teLo - LAYOUT.eqLo) * 0.12;
    LAYOUT.eqHi += (teHi - LAYOUT.eqHi) * 0.12;
  } else { LAYOUT.eqLo = teLo; LAYOUT.eqHi = teHi; }

  const g = ctx2;
  g.clearRect(0, 0, W, H);
  g.fillStyle = cssVar('--panel');
  g.fillRect(0, 0, W, H);
  drawGrid(g, plotW);
  drawCandles(g, cands);
  drawLevels(g, plotW);
  drawEquity(g, plotW, from);
  drawTimeAxis(g, cands);
  drawLivePrice(g, plotW);
  drawCrosshair(g, plotW);
}

function drawGrid(g, plotW) {
  const grid = cssVar('--grid');
  g.strokeStyle = grid; g.lineWidth = 1;
  g.fillStyle = cssVar('--faint'); g.font = '10px ' + cssVar('--mono');
  g.textAlign = 'left'; g.textBaseline = 'middle';
  for (let t = 0; t <= 6; t++) {
    const p = LAYOUT.lo + (LAYOUT.hi - LAYOUT.lo) * t / 6;
    const y = Math.round(yOf(p)) + 0.5;
    g.beginPath(); g.moveTo(0, y); g.lineTo(plotW, y); g.stroke();
    g.fillText(p.toFixed(5), plotW + 8, y);
  }
  const eqSpan = LAYOUT.eqHi - LAYOUT.eqLo;
  const eqStep = eqSpan > 1400 ? 500 : eqSpan > 700 ? 250 : eqSpan > 300 ? 100 : 50;
  for (let v = Math.ceil(LAYOUT.eqLo / eqStep) * eqStep; v <= LAYOUT.eqHi; v += eqStep) {
    const y = Math.round(yEq(v)) + 0.5;
    g.beginPath(); g.moveTo(0, y); g.lineTo(plotW, y); g.stroke();
    g.fillText(eqStep >= 250 ? (v / 1000).toFixed(1) + 'k'
                             : '$' + v.toLocaleString('en-US'), plotW + 8, y);
  }
}

function drawCandles(g, cands) {
  const upB = cssVar('--up-body'), up = cssVar('--up');
  const dnB = cssVar('--down-body'), dn = cssVar('--down');
  const bodyW = Math.max(1, Math.min(13, S.bw * 0.68));
  const exit = exitBar();
  for (const c of cands) {
    const x = xOfCandle(c.j);
    if (x < -S.bw || x > W - PADR + S.bw) continue;
    // Dim what is not your trade: history before the window, and anything
    // after the account was decided.
    g.globalAlpha = (c.j * S.tf > exit || c.j < 0) ? 0.32 : 1;
    const rising = c.c >= c.o;
    g.strokeStyle = rising ? up : dn;
    g.lineWidth = 1;
    g.beginPath();
    g.moveTo(Math.round(x) + 0.5, yOf(c.h));
    g.lineTo(Math.round(x) + 0.5, yOf(c.l));
    g.stroke();
    const yo = yOf(c.o), yc = yOf(c.c);
    const top = Math.min(yo, yc), hgt = Math.max(1, Math.abs(yc - yo));
    g.fillStyle = rising ? upB : dnB;
    g.fillRect(Math.round(x - bodyW / 2), Math.round(top), Math.round(bodyW), Math.round(hgt));
    g.strokeRect(Math.round(x - bodyW / 2) + 0.5, Math.round(top) + 0.5,
                 Math.round(bodyW) - 1, Math.round(hgt) - 1);
  }
  g.globalAlpha = 1;
}

function tag(g, x, y, text, color, bold) {
  g.font = (bold ? '600 ' : '') + '10px ' + cssVar('--mono');
  const w = g.measureText(text).width + 10;
  g.fillStyle = color;
  g.fillRect(x, y - 8, w, 16);
  g.fillStyle = cssVar('--panel');
  g.textAlign = 'left'; g.textBaseline = 'middle';
  g.fillText(text, x + 5, y + 0.5);
}

function grip(g, x, y, color) {
  g.save();
  g.fillStyle = color;
  const w = 22, h = 13;
  g.beginPath();
  if (g.roundRect) g.roundRect(x - w, y - h / 2, w, h, 3); else g.rect(x - w, y - h / 2, w, h);
  g.fill();
  g.fillStyle = cssVar('--panel');
  for (let k = -1; k <= 1; k++) g.fillRect(x - w / 2 + k * 4 - 0.5, y - 3, 1.5, 6);
  g.restore();
}

function lastFloorPx(k) {
  const fp = S.res.curveFloorPx;
  for (let j = Math.min(k, fp.length - 1); j >= 0; j--)
    if (isFinite(fp[j])) return fp[j];
  return BARS.close[S.i0];
}

function drawLevels(g, plotW) {
  const entry = S.entry;
  const dpp = dollarsPerPrice(entry, S.size);
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

  // Liquidation price, stepped: a trailing floor only ever ratchets.
  const fp = S.res.curveFloorPx;
  g.save();
  g.strokeStyle = cssVar('--kill'); g.lineWidth = 2; g.setLineDash([6, 4]);
  g.beginPath();
  let started = false;
  const upto = S.phase === 'setup' ? -1 : Math.min(S.headBar, fp.length - 1);
  const firstSrc = Math.max(0, upto - Math.ceil(plotW / S.bw) * S.tf - S.tf);
  for (let q = firstSrc; q <= upto; q++) {
    const v = fp[q];
    if (!isFinite(v)) { started = false; continue; }
    const x = xOfCandle(q / S.tf), y = yOf(v);
    if (!started) { g.moveTo(x, y); started = true; } else { g.lineTo(x, y); }
  }
  g.stroke(); g.restore();

  const clampY = (y) => Math.max(PADT + 7, Math.min(PRICE_H - 7, y));
  const arr = (y) => y < PADT ? ' ▲' : (y > PRICE_H ? ' ▼' : '');
  tag(g, plotW, clampY(yE), px5(entry) + arr(yE), cssVar('--muted'));
  tag(g, plotW, clampY(yT), px5(S.tp) + arr(yT), cssVar('--tp'));
  tag(g, plotW, clampY(yS), px5(S.sl) + arr(yS), cssVar('--sl'));
  const lastFloor = lastFloorPx(S.headBar);
  if (S.phase !== 'setup')
    tag(g, plotW, clampY(yOf(lastFloor)), px5(lastFloor), cssVar('--kill'));

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
  if (S.phase !== 'setup' && Math.abs(yOf(lastFloor) - yS) > 15)
    g.fillText('LIQUIDATION', 7, yOf(lastFloor) - 4);
  g.fillStyle = cssVar('--muted');
  if (Math.abs(yE - yOf(lastFloor)) > 22 && Math.abs(yE - yS) > 22)
    g.fillText(S.phase === 'setup' ? orderKind()
               : S.res.trades.length ? 'ENTRY  filled' : 'ENTRY  never filled',
               7, yE - 4);
}

/** The live price tag and the countdown to this candle's close -- the two
    things that make a chart feel like it is running. */
function drawLivePrice(g, plotW) {
  const p = livePrice();
  const y = Math.max(PADT + 7, Math.min(PRICE_H - 7, yOf(p)));
  const col = S.tickDir > 0 ? cssVar('--up') : S.tickDir < 0 ? cssVar('--kill') : cssVar('--ink-2');
  g.save();
  g.strokeStyle = col; g.lineWidth = 1; g.setLineDash([2, 3]); g.globalAlpha = 0.7;
  g.beginPath(); g.moveTo(0, Math.round(yOf(p)) + 0.5);
  g.lineTo(plotW, Math.round(yOf(p)) + 0.5); g.stroke();
  g.restore();
  tag(g, plotW, y, px5(p), col, true);

  if (S.playing) {
    const leftMin = S.tf - (S.headBar % S.tf) - S.headFrac;   // market minutes
    const mm = Math.floor(leftMin);
    const ss = Math.max(0, Math.floor((leftMin - mm) * 60));
    g.font = '10px ' + cssVar('--mono');
    g.fillStyle = cssVar('--muted');
    g.textAlign = 'left'; g.textBaseline = 'middle';
    g.fillText(`${mm}:${String(ss).padStart(2, '0')}`, plotW + 8, y + 16);
  }
}

function drawEquity(g, plotW, from) {
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

  const upto = S.phase === 'setup' ? -1 : Math.min(S.headBar, eq.length - 1);
  const start = Math.max(0, from);
  if (21500 >= LAYOUT.eqLo && 21500 <= LAYOUT.eqHi) {
    g.save();
    g.strokeStyle = cssVar('--tp'); g.setLineDash([4, 4]); g.lineWidth = 1;
    const yT = yEq(21500);
    g.beginPath(); g.moveTo(0, yT); g.lineTo(plotW, yT); g.stroke();
    g.restore();
  }
  const trace = (series, color, width) => {
    g.save(); g.strokeStyle = color; g.lineWidth = width;
    g.beginPath();
    for (let q = start; q <= upto; q++) {
      const x = xOfCandle(q / S.tf), y = yEq(series[q]);
      q === start ? g.moveTo(x, y) : g.lineTo(x, y);
    }
    g.stroke(); g.restore();
  };
  trace(fl, cssVar('--kill'), 1.75);
  trace(eq, cssVar('--ink'), 1.75);

  if (upto >= start) {
    const x = xOfCandle(upto / S.tf), y = yEq(eq[upto]);
    const done = upto >= eq.length - 1;
    const col = done && S.res.outcome === 'FAIL_DRAWDOWN' ? cssVar('--kill')
              : done && S.res.outcome === 'PASS' ? cssVar('--pass') : cssVar('--ink');
    g.fillStyle = col;
    g.beginPath(); g.arc(x, y, 3.5, 0, Math.PI * 2); g.fill();
    tag(g, plotW, Math.max(top + 8, Math.min(top + EQ_H - 8, y)), money(eq[upto]), col, true);
  }
}

function drawTimeAxis(g, cands) {
  g.font = '10px ' + cssVar('--mono');
  g.fillStyle = cssVar('--faint');
  g.textAlign = 'center'; g.textBaseline = 'top';
  const y = H - PADB + 5;
  const perLabel = Math.max(1, Math.round(76 / S.bw));
  for (const c of cands) {
    if (c.j % perLabel) continue;
    const x = xOfCandle(c.j);
    if (x < 22 || x > W - PADR - 22) continue;
    g.fillText(utc(c.ts, false), x, y);
  }
}

function readout(c) {
  if (!c) return;
  $('ohlc').innerHTML = [['O', c.o], ['H', c.h], ['L', c.l], ['C', c.c]]
    .map(([k, v]) => `<span>${k} <b>${px5(v)}</b></span>`).join('');
}

function drawCrosshair(g, plotW) {
  if (S.hover === null || S.playing) return;
  const { x, y } = S.hover;
  if (x > plotW) return;
  g.save();
  g.strokeStyle = cssVar('--rule-2'); g.lineWidth = 1; g.setLineDash([2, 3]);
  g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H - PADB); g.stroke();
  g.beginPath(); g.moveTo(0, y); g.lineTo(plotW, y); g.stroke();
  g.restore();
  if (y < PRICE_H) tag(g, plotW, y, px5(priceAt(y)), cssVar('--rule-2'));
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

  if (S.drag && S.drag.kind === 'pan') {
    S.panCandles = S.drag.from + (S.drag.x - x) / S.bw;
    S.panCandles = Math.max(0, S.panCandles);
    draw();
    return;
  }
  if (S.drag) {
    const p = priceAt(y);
    const minGap = 0.00005;
    if (S.drag.kind === 'entry') {
      const d = p - S.entry;
      S.entry = p; S.tp += d; S.sl += d;
    } else if (S.drag.kind === 'tp') {
      S.tp = S.dir > 0 ? Math.max(p, S.entry + minGap) : Math.min(p, S.entry - minGap);
    } else {
      S.sl = S.dir > 0 ? Math.min(p, S.entry - minGap) : Math.max(p, S.entry + minGap);
    }
    if (!S.raf) S.raf = requestAnimationFrame(() => {
      S.raf = 0;
      if (S.phase !== 'setup') setPhase('setup');
      runDay(); draw();
    });
    return;
  }

  S.hover = { x, y };
  const onLine = y < PRICE_H && nearestLine(y);
  cv.style.cursor = onLine ? 'grab' : (y < PRICE_H ? 'crosshair' : 'default');
  const j = Math.round(candleAtX(x));
  const c = candleAt(j);
  if (c) { readout(c); $('clock').textContent = utc(c.ts, true) + ' UTC'; }
  if (!S.playing) draw();
});
cv.addEventListener('pointerleave', () => { S.hover = null; if (!S.playing) draw(); });
cv.addEventListener('pointerdown', (e) => {
  const r = cv.getBoundingClientRect();
  const x = e.clientX - r.left, y = e.clientY - r.top;
  const hit = y < PRICE_H ? nearestLine(y) : null;
  if (hit) {
    S.drag = { kind: hit };
    cv.style.cursor = 'grabbing';
  } else {
    S.drag = { kind: 'pan', from: S.panCandles, x };
    cv.style.cursor = 'grabbing';
  }
  cv.setPointerCapture(e.pointerId);
});
cv.addEventListener('pointerup', (e) => {
  if (!S.drag) return;
  const wasLine = S.drag.kind !== 'pan';
  S.drag = null;
  cv.releasePointerCapture(e.pointerId);
  cv.style.cursor = 'crosshair';
  if (wasLine) { rearm(); }
  draw();
});
cv.addEventListener('wheel', (e) => {
  e.preventDefault();
  S.bw = Math.max(2.2, Math.min(28, S.bw * (e.deltaY > 0 ? 0.88 : 1.14)));
  draw();
}, { passive: false });

/* ============================== replay =================================== */

let rafId = 0;

function fitAll() {
  const total = S.phase === 'setup'
    ? 96                                   // a screen of history to place against
    : (exitBar() + 1) / S.tf + 14;
  S.bw = Math.max(2.2, Math.min(16, ((W - PADR) - RIGHT_GAP) / total));
  S.panCandles = 0;
}

function play() {
  if (S.playing) return;
  S.playing = true;
  setPhase('running');
  S.headBar = 0; S.headFrac = 0;
  S.panCandles = 0;
  S.bw = 9;
  S.lastT = performance.now();
  S.lastTick = livePrice();
  $('pause').textContent = '❚❚';
  rafId = requestAnimationFrame(step);
}

function step(t) {
  if (!S.playing) return;
  const dt = Math.min(0.12, (t - S.lastT) / 1000);
  S.lastT = t;
  S.headFrac += S.minsPerSec * dt;
  while (S.headFrac >= 1) { S.headFrac -= 1; S.headBar += 1; }

  const end = exitBar();
  if (S.headBar >= end) { S.headBar = end; S.headFrac = 1; finish(); return; }

  const p = livePrice();
  S.tickDir = p > S.lastTick ? 1 : p < S.lastTick ? -1 : S.tickDir;
  S.lastTick = p;

  paintHUD(); draw();
  rafId = requestAnimationFrame(step);
}

function finish() {
  S.playing = false;
  cancelAnimationFrame(rafId);
  setPhase('done');
  fitAll();
  paintHUD(); draw();
}

/** Any change to the order takes you back to a flat, pre-trade chart -- the
    result on screen belonged to the old order. */
function rearm() {
  if (S.playing) { S.playing = false; cancelAnimationFrame(rafId); }
  setPhase('setup');
  runDay();
  fitAll();
  draw();
}

function stop() { if (S.playing) finish(); }

$('pause').onclick = () => {
  if (!S.playing) {                       // resume
    if (S.headBar >= exitBar()) return;
    S.playing = true;
    S.lastT = performance.now();
    $('pause').textContent = '❚❚';
    rafId = requestAnimationFrame(step);
  } else {                                // pause, keeping the head where it is
    S.playing = false;
    cancelAnimationFrame(rafId);
    $('pause').textContent = '▶';
    draw();
  }
};

function paintHUD() {
  const r = S.res, cfg = config();
  const setup = S.phase === 'setup';
  const k = setup ? 0 : Math.min(S.headBar, r.curveEq.length - 1);
  const eq = setup ? cfg.startingBalance : r.curveEq[k];
  const fl = setup ? cfg.startingBalance - cfg.maxDrawdown : r.curveFloor[k];
  const done = S.phase === 'done';

  $('hBal').textContent = money(done ? r.finalBalance : eq, 0);
  $('hEq').textContent = money(eq, 0);
  const room = eq - fl;
  $('hRoom').textContent = money(room, 0);
  $('hRoom').style.color = room < 100 ? 'var(--kill)' : 'var(--ink)';
  const togo = cfg.startingBalance + cfg.profitTarget - eq;
  $('hTarget').textContent = togo <= 0 ? 'reached' : money(togo, 0);

  const entry = S.entry;
  const dpp = dollarsPerPrice(entry, S.size);
  // Has the order actually filled *by the point on screen*?
  const filled = !setup && r.trades.length &&
                 k >= (r.trades[0].entryIndex - S.i0);
  $('lEntry').textContent = px5(entry) + (setup ? '  ' + orderKind().toLowerCase()
                                                : filled ? '  filled' : '  working');
  $('lTP').textContent = `${px5(S.tp)}  +${money(Math.abs(S.tp - entry) * dpp)}`;
  $('lSL').textContent = `${px5(S.sl)}  −${money(Math.abs(S.sl - entry) * dpp)}`;
  $('lKill').textContent = setup ? '—' : px5(lastFloorPx(S.headBar));

  const v = $('verdict');
  if (setup) { v.className = 'tag live'; v.textContent = orderKind() + ' — NOT SENT'; }
  else if (!done) {
    v.className = 'tag live';
    v.textContent = filled ? 'IN TRADE' : 'ORDER WORKING';
  } else if (!r.trades.length) {
    v.className = 'tag fail'; v.textContent = 'NEVER FILLED  ' + money(-cfg.entryFee);
  } else if (r.outcome === 'PASS') { v.className = 'tag pass'; v.textContent = 'PASSED  +$5,000'; }
  else if (r.outcome === 'FAIL_DRAWDOWN') {
    v.className = 'tag fail'; v.textContent = 'LIQUIDATED  ' + money(-cfg.entryFee);
  } else { v.className = 'tag fail'; v.textContent = '24H EXPIRED  ' + money(-cfg.entryFee); }
}

/* ============================== controls ================================= */

function newWindow(seed) {
  const w = pickWindow(seed);
  S.i0 = w.i0; S.n = w.n;
  S.panCandles = 0;
  resetLevels();
  setPhase('setup');
  runDay();
  fitAll();
  const a = BARS.ts[S.i0], b = BARS.ts[Math.min(S.i0 + S.n - 1, BARS.ts.length - 1)];
  $('windowNote').textContent =
    `${utc(a, true)} → ${utc(b, true)} UTC · ${S.n.toLocaleString()} one-minute bars`;
  draw();
  readout(candleAt(Math.floor(headCandleF())));
  $('clock').textContent = utc(BARS.ts[S.i0], true) + ' UTC';
}

$('play').onclick = () => { S.playing ? finish() : play(); };
$('shuffle').onclick = () => {
  if (S.playing) { S.playing = false; cancelAnimationFrame(rafId); }
  newWindow((Math.random() * 1e9) | 0);
};
$('dLong').onclick = () => setDir(1);
$('dShort').onclick = () => setDir(-1);
function setDir(d) {
  if (d === S.dir) return;
  S.dir = d;
  $('dLong').setAttribute('aria-pressed', String(d === 1));
  $('dShort').setAttribute('aria-pressed', String(d === -1));
  // Flip the exits around the entry rather than throwing them away.
  const tp = S.tp, sl = S.sl;
  S.tp = 2 * S.entry - tp;
  S.sl = 2 * S.entry - sl;
  rearm();
}
$('cDD').onchange = () => { S.ddMode = $('cDD').value; rearm(); };
$('cSize').oninput = () => {
  // Size changes what your levels are WORTH, never where they are.
  S.size = +$('cSize').value / 100;
  $('vSize').textContent = $('cSize').value + '%';
  rearm();
};
for (const b of document.querySelectorAll('[data-speed]')) {
  b.onclick = () => {
    S.minsPerSec = +b.dataset.speed;
    $('vSpeed').textContent = S.minsPerSec + ' min/s';
    for (const o of document.querySelectorAll('[data-speed]'))
      o.setAttribute('aria-pressed', String(o === b));
  };
}
for (const b of document.querySelectorAll('[data-tf]')) {
  b.onclick = () => {
    S.tf = +b.dataset.tf;
    for (const o of document.querySelectorAll('[data-tf]'))
      o.setAttribute('aria-pressed', String(o === b));
    if (!S.playing) fitAll();
    draw();
  };
}

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
  $('bigRate').style.color = s.passRate >= be ? 'var(--pass)' : 'var(--ink)';
  $('bigSub').innerHTML = s.passRate >= be
    ? 'pass rate — <b style="color:var(--pass)">above</b> the 10% breakeven'
    : 'pass rate — you need <b>10%</b> to break even on the $500 fee';
  $('meterFill').style.width = Math.min(100, s.passRate / top * 100) + '%';
  $('meterFill').style.background = s.passRate >= be ? 'var(--pass)' : 'var(--dd)';
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
    // Search with the same default order the page actually opens with.
    const entry = BARS.close[w.i0] - 0.0004;
    const dpp = dollarsPerPrice(entry, S.size);
    const res = runChallenge(BARS,
      terminalStrategy(1, S.size, entry, entry + 1500 / dpp, entry - 250 / dpp),
      INST, COSTS, cfg, rng(1), w.i0, null, true);
    if (!res.trades.length) continue;               // never filled: not useful
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
