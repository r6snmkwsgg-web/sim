'use strict';
/* ==========================================================================
   Core: the shape of Hell, hashing, the books themselves, saved state
   ========================================================================== */
const H = 8;                 // one floor, floor to floor, metres (see world.js: RLH)
const PAGES = 410, LINES = 40, COLS = 80, PAGE_CH = LINES * COLS;
const HOUR_SEC = 24;         // real seconds per game hour
const LIGHTS_ON = 6, LIGHTS_OFF = 22;
const TERMINAL = 52;         // m/s, falling
const LOG10_BOOKS = 1312000 * Math.log10(95);
const DIGITS = Math.floor(LOG10_BOOKS) + 1;
const FRAG_RATE = 60;        // one book in 60 carries a readable fragment (the game's one mercy)
const START_FLOOR = 7302118441, START_CX = 311206, START_CZ = -48214;

const fmt = n => Math.round(n).toLocaleString('en-US');
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const mod = (a, n) => ((a % n) + n) % n;
const srgb = h => { const c = new THREE.Color(h); return [Math.pow(c.r, 2.2), Math.pow(c.g, 2.2), Math.pow(c.b, 2.2)]; };

/* Book cloth colours (sRGB in, linear out) — shared by the 3D books and the procedural far shelves */
const PALETTE = ['#6f2e28', '#3e5a44', '#2e3e5c', '#9a7a3a', '#5b4636', '#56606a', '#5a3f56', '#2f5654', '#8e7a5c', '#2a2826'].map(srgb);
const AVG_BOOK = PALETTE.reduce((a, c) => [a[0] + c[0] / PALETTE.length, a[1] + c[1] / PALETTE.length, a[2] + c[2] / PALETTE.length], [0, 0, 0]);

/* 32-bit hashing, identical in JS and GLSL */
function mix(h) { h ^= h >>> 16; h = Math.imul(h, 0x7feb352d); h ^= h >>> 15; h = Math.imul(h, 0x846ca68b); h ^= h >>> 16; return h >>> 0; }
const lo32 = n => mod(n, 4294967296);
const hi32 = n => Math.floor(n / 4294967296) >>> 0;
function lookHash(f, x, z, k, p) {
  let h = mix((lo32(f) ^ 0x51ed270b) >>> 0);
  h = mix((h ^ hi32(f)) >>> 0);
  h = mix((h ^ lo32(x)) >>> 0);
  h = mix((h ^ hi32(x) ^ 0xa5a5a5a5) >>> 0);
  h = mix((h ^ lo32(z)) >>> 0);
  h = mix((h ^ hi32(z) ^ 0x2545f491) >>> 0);
  h = mix((h ^ ((k * 131 + p * 7919) >>> 0)) >>> 0);
  return h;
}
function bookLook(id) {
  const h = lookHash(id.f, id.x, id.z, id.k, id.p), pc = PALETTE[h % PALETTE.length];
  const j = 0.78 + ((h >>> 8) & 255) / 255 * 0.4;
  const st = mix((h ^ 0x9e3779b9) >>> 0);
  return {
    col: [pc[0] * j, pc[1] * j, pc[2] * j],
    h: 0.26 + ((h >>> 16) & 255) / 255 * 0.11,
    d: 0.19 + ((h >>> 24) & 255) / 255 * 0.07,
    w: 0.034 + ((st >>> 24) & 255) / 255 * 0.028,
    band: st % 3, label: (st >>> 4) % 3 === 0 ? 1 : 0, wear: ((st >>> 8) & 255) / 255, out: ((st >>> 16) & 255) / 255 * 0.012
  };
}
const cssCol = c => `rgb(${c.map(v => Math.round(clamp(Math.pow(v, 1 / 2.2) * 1.15, 0, 1) * 255)).join(',')})`;

/* Text hashing for pages */
function hnum(h, n) { h = mix((h ^ lo32(n)) >>> 0); return mix((h ^ hi32(n) ^ 0x9e3779b9) >>> 0); }
function textHash(id, salt) { let h = mix(((salt * 0x2545F491) >>> 0) ^ 0x1234567); h = hnum(h, id.f); h = hnum(h, id.x); h = hnum(h, id.z); return mix((h ^ (id.k * 131 + id.p * 7919)) >>> 0); }
function strHash(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return mix(h >>> 0); }
function sfc32(a, b, c, d) { return function () { a >>>= 0; b >>>= 0; c >>>= 0; d >>>= 0; let t = (a + b) | 0; a = b ^ (b >>> 9); b = (c + (c << 3)) | 0; c = (c << 21) | (c >>> 11); d = (d + 1) | 0; t = (t + d) | 0; c = (c + t) | 0; return (t >>> 0) / 4294967296; }; }
const keyOf = id => id.f + ':' + id.x + ':' + id.z + ':' + id.k + ':' + id.p;
const parseKey = k => { const a = k.split(':').map(Number); return { f: a[0], x: a[1], z: a[2], k: a[3], p: a[4] }; };
const sameId = (a, b) => a && b && a.f === b.f && a.x === b.x && a.z === b.z && a.k === b.k && a.p === b.p;

const FRAGMENTS = [
  "the lamps were already lit when i arrived", "we kept a garden once", "nobody told me it would be this quiet",
  "she said my name like it was a question", "i remember rain", "forgive the reader", "the kettle is still on",
  "somewhere a door is open", "you have read this far", "this sentence is not about you", "turn back", "keep going",
  "there was an orchard behind the house", "i was happy and did not know it", "all the clocks agree",
  "the answer is on another floor", "he never learned to swim", "mercy is a long hallway",
  "the dog waited by the gate", "the snow came early that year", "light a lamp for me",
  "no one is keeping score", "hold the rail", "the ink is still wet", "salt, bread, a window", "tell them i tried",
  "it was a tuesday", "every book is a letter to someone", "the stairs go on", "almost", "we laughed until the neighbours knocked",
  "under the floorboards, a key", "ask again tomorrow", "a small boat on a calm lake", "i kept your letters",
  "nothing here is lost, only mislaid", "breathe", "you left the porch light on", "i am still here", "there is no hurry",
  "the river remembers", "read slowly", "one more floor", "a warm kitchen and a radio", "the bells at noon",
  "she planted tulips every autumn", "the bus was late again", "call your sister", "the light through the curtains"
];
/* Books that matter to the story are pure functions too — just not random ones. Filled in by story.js. */
const SPECIAL = new Map();
function fragOf(id) {
  const sp = SPECIAL.get(keyOf(id)); if (sp) return sp;
  const h = textHash(id, 97);
  if (h % FRAG_RATE !== 0) return null;
  const text = FRAGMENTS[mix(h ^ 0xabc) % FRAGMENTS.length];
  const page = mix(h ^ 0x11) % PAGES, line = mix(h ^ 0x22) % LINES, col = mix(h ^ 0x33) % (COLS - text.length);
  return { text, page, at: line * COLS + col };
}
const pageCache = new Map();
function pageText(id, pg) {
  const ck = keyOf(id) + '#' + pg;
  const hit = pageCache.get(ck); if (hit) return hit;
  const rnd = sfc32(textHash(id, 11), mix((pg * 0x9E3779B1) >>> 0 ^ 0x51ed27), textHash(id, 23) ^ pg, 0xC0FFEE ^ pg);
  for (let i = 0; i < 12; i++) rnd();
  const a = new Uint8Array(PAGE_CH);
  for (let i = 0; i < PAGE_CH; i++) a[i] = 32 + ((rnd() * 95) | 0);
  let s = String.fromCharCode.apply(null, a);
  const fr = fragOf(id);
  if (fr && fr.page === pg) s = s.slice(0, fr.at) + fr.text + s.slice(fr.at + fr.text.length);
  if (pageCache.size > 80) pageCache.delete(pageCache.keys().next().value);
  pageCache.set(ck, s);
  return s;
}
function roomName(x, z) { return `${x < 0 ? 'W' : 'E'}${fmt(Math.abs(x))} ${z < 0 ? 'S' : 'N'}${fmt(Math.abs(z))}`; }
function addrLine(id) { return `Floor ${fmt(id.f)} · Room ${roomName(id.x, id.z)} · Shelf ${id.k + 1} · Book ${id.p + 1}`; }

/* ==========================================================================
   Saved state
   ========================================================================== */
const SAVE_KEY = 'short-stay-in-hell-v3';
let S = null;
function freshState() {
  return {
    v: 3, name: 'Soren Johansson', act: 1, year: 1, day: 1, time: 7.25,
    cx: START_CX, cz: START_CZ, floor: START_FLOOR, x: 8, y: 0, z: 5.2, yaw: Math.PI, pitch: -0.06,
    hunger: 0.1, thirst: 0.1, hp: 100, drunk: 0,
    carried: null, item: null,
    over: {}, ground: [], seen: {},
    stats: { dist: 0, books: 0, pages: 0, deaths: 0, fallen: 0, climbed: 0, searches: 0, maxFall: 0, thrown: 0, daysFalling: 0, rooms: 0, swum: 0 },
    journal: [], frags: [], npc: {}, flags: {}, done: {},
    fall: null, dead: null, landing: null,
    settings: { sens: 1, vol: 0.8, music: 0.6, q: 1, gfx: 2, hints: 1 }
  };
}
function save() { if (!S) return; try { localStorage.setItem(SAVE_KEY, JSON.stringify(S)); } catch (e) {} }
function loadSave() { try { const t = localStorage.getItem(SAVE_KEY); if (!t) return null; const s = JSON.parse(t); return s && s.v === 3 ? s : null; } catch (e) { return null; } }
function clock(t) { if (t === undefined) t = S.time; t = mod(t, 24); const h = Math.floor(t), m = Math.floor((t - h) * 60); return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0'); }
function dateLine() { return S.act >= 4 && S.fall ? `Year ${fmt(S.year)} · falling, day ${fmt(S.fall.days + 1)}` : `Year ${fmt(S.year)} · Day ${fmt(S.day)}`; }
function logJ(text) { S.journal.push({ y: S.year, d: S.day, t: clock(), text }); if (S.journal.length > 500) S.journal.shift(); }
function npcRec(k) { return S.npc[k] || (S.npc[k] = { met: false, aff: 0, last: -1, f: {}, talks: 0 }); }
let overFloors = new Map();
function recountOver() { overFloors = new Map(); for (const k in S.over) { const a = k.split(':'); const key = a[0] + ':' + a[1] + ':' + a[2]; overFloors.set(key, (overFloors.get(key) || 0) + 1); } }
const roomHasOver = (f, x, z) => overFloors.has(f + ':' + x + ':' + z);
function slotContent(id) { const o = S.over[keyOf(id)]; if (o === undefined) return id; return o === '' ? null : parseKey(o); }
function lifeBook() {
  const r = sfc32(strHash(S ? S.name : 'Soren Johansson'), 0x1f2e3d, 0xbeef, 7);
  let d = String(1 + Math.floor(r() * 9)); for (let i = 0; i < 17; i++) d += Math.floor(r() * 10);
  return { lead: d.replace(/\B(?=(\d{3})+(?!\d))/g, ','), digits: DIGITS - 3 - Math.floor(r() * 40) };
}
