'use strict';
/* ==========================================================================
   The world's people and the things that can happen to you — by chance, as in the book
   ========================================================================== */
const ARRIVAL = { seg: START_SEG, floor: START_FLOOR, side: 0 };
const JEDSITE = { seg: START_SEG + 1, floor: START_FLOOR, side: 0 };
const UNI = { seg: START_SEG - 3, floor: START_FLOOR - 2, side: 0 };
const SACK = { s: 0, f: START_FLOOR, c: START_SEG * CASES + 31, r: 3, p: 12 };
SPECIAL.set(keyOf(SACK), { text: 'sack it', page: 188, at: 8 * COLS + 30 });
const MST_FIRST = 'and in the morning the river came back as if it had never been away';

const MOMENTS = {
  arrival: { eyebrow: 'Year one · Day one', title: 'The First Week', art: 'ch1', text: 'You wake at a railing in a body that no longer hurts. Four strangers wake beside you. Below: shelves. Above: shelves. Across the chasm, more shelves, and more people at their railing, looking back.' },
  university: { eyebrow: 'Three rest areas west, two floors down', title: 'The University', art: 'ch2', text: 'People who have been here for a century have made something out of it: a university, of all things, devoted to the rare sentence that means anything at all.' },
  direites: { eyebrow: 'They come along the gallery', title: 'The Direites', art: 'ch3', text: 'Some people here decided that pain is the only thing in the library nobody wrote down first. They follow a man called Dire Dan. They are coming this way.' },
  abyss: { eyebrow: 'The lamps went out. You kept falling.', title: 'The Deepest Abyss', art: 'ch4', text: 'The lamps came back on and you are still falling. You can steer. You cannot stop — unless you hit something hard enough to kill you, and wake tomorrow wherever that was.' },
};

/* ---------- Who lives where: every rest area's occupants are a pure function of its address ---------- */
const SITE_NAMES = ['Dale', 'Marcy', 'Tom', 'Jean', 'Rick', 'Barbara', 'Gary', 'Linda', 'Doug', 'Carol', 'Steve', 'Donna', 'Phil', 'Karen', 'Walt', 'Judy', 'Ray', 'Nancy', 'Earl', 'Peggy', 'Hank', 'Sheila', 'Lyle', 'Deb'];
const TOWNS = ['Dayton, Ohio', 'Provo, Utah', 'Tulsa', 'Fresno', 'outside Des Moines', 'Duluth', 'Bakersfield', 'Scranton', 'Boise', 'Mobile, Alabama', 'Spokane', 'Albany', 'Omaha', 'El Paso', 'Grand Rapids', 'Reno'];
function siteType(seg, floor, side) {
  if (side === 0 && floor === START_FLOOR && seg === START_SEG) return { type: 'arrival', n: 0 };
  if (side === 0 && floor === START_FLOOR && seg === START_SEG + 1) return { type: 'jed', n: 0 };
  if (side === 0 && floor === UNI.floor && seg === UNI.seg) return { type: 'university', n: 2 };
  const h = lookHash(floor, seg, side, 11, 13), r = (h % 1000) / 1000, k = h >>> 12;
  if (r < 0.6) return null;
  if (r < 0.75) return { type: 'searchers', n: 1 + k % 3 };
  if (r < 0.82) return { type: 'drinkers', n: 1 + k % 2 };
  if (r < 0.88) return { type: 'still', n: 1 + k % 2 };
  if (r < 0.95) return { type: 'scholars', n: 2 + k % 2 };
  return { type: 'preacher', n: 3 };
}
const POOL = NPCS.filter(n => n.d.generic);
function occupantKey(seg, floor, side, i) { return side + ':' + floor + ':' + seg + '#' + i; }
function assignSites() {
  const want = new Map();
  if (!S.fall) for (let df = -1; df <= 1; df++) for (let ds = -2; ds <= 2; ds++) {
    const seg = S.seg + ds, floor = S.floor + df, t = siteType(seg, floor, S.side);
    if (!t) continue;
    for (let i = 0; i < t.n; i++) { const key = occupantKey(seg, floor, S.side, i); want.set(key, { key, seg, floor, side: S.side, role: t.type === 'university' ? 'scholars' : t.type, i }); }
  }
  for (const n of POOL) if (n.assign && !want.has(n.assign.key) && !n.special) { n.assign = null; n.gone = true; }
  for (const n of POOL) if (n.assign) want.delete(n.assign.key);
  for (const w of want.values()) {
    const n = POOL.find(p => !p.assign && !p.special); if (!n) break;
    const h = strHash(w.key);
    n.assign = w; n.gone = false; n.t = 0; n.goalFace = null; n.faceAt = null; n.stun = 0;
    n.gname = SITE_NAMES[h % SITE_NAMES.length]; n.gtown = TOWNS[(h >>> 8) % TOWNS.length];
    n.home = { seg: w.seg, floor: w.floor, side: w.side };
    const g = schedule(n) || { mode: 'idle' };
    placeNPC(n, w.seg, g.lx !== undefined ? g.lx : 86, g.z !== undefined ? g.z : -4, w.floor, w.side);
    n.mode = g.mode === 'bed' ? 'lie' : g.mode; n.t = g.dur || 20; n.goalFace = g.face; n.faceAt = g.faceAt || null; n.lieYaw = (h % 628) / 100;
    if (g.mode === 'bed') { const b = roomSpot(n, 'bed'); n.lx = b.lx; n.z = b.z; }
  }
}
function dailyRound(n, home, activity) {
  const t = S.time;
  if (t >= 21.5 || t < 6.1) { const b = roomSpot(n, 'bed'); return { mode: 'bed', seg: home.seg, lx: b.lx, z: b.z }; }
  if ((t >= 12 && t < 13) || (t >= 19 && t < 21.5)) { const s = roomSpot(n, 'table'); return { mode: 'sit', seg: home.seg, lx: s.lx, z: s.z, dur: 60 }; }
  const cs = Math.floor(Math.random() * CASES), sg = home.seg + (Math.random() < 0.65 ? 0 : (Math.random() < 0.5 ? -1 : 1));
  return { mode: activity || 'read', seg: sg, lx: cs * CW + 1, z: -2.45, dur: 20 + Math.random() * 35, face: 'shelf' };
}
function schedule(n) {
  const t = S.time, role = n.d.role, rec = npcRec(n.d.key);
  if (n.d.generic) {
    if (!n.assign) return null;
    const a = n.assign, home = n.home;
    switch (a.role) {
      case 'drinkers': if (t >= 21.5 || t < 6.1) return dailyRound(n, home); { const s = roomSpot(n, 'table'); return { mode: 'drink', seg: home.seg, lx: s.lx, z: s.z, dur: 90 }; }
      case 'still': return { mode: 'lie', dur: 999, seg: home.seg, lx: 81 + (strHash(a.key) % 900) / 100, z: -3.5 - (strHash(a.key + 'z') % 200) / 100 };
      case 'preacher':
        if (t >= 21.5 || t < 6.1) return dailyRound(n, home);
        if (a.i === 0) return { mode: 'preach', seg: home.seg, lx: 86, z: -3.7, dur: 60, face: 'out' };
        return { mode: 'stand', seg: home.seg, lx: 84.6 + a.i * 1.4, z: -1.9 - a.i * 0.3, dur: 60, faceAt: { seg: home.seg, lx: 86, z: -3.7 } };
      default: return dailyRound(n, home);
    }
  }
  switch (role) {
    case 'companion': case 'scholar': return dailyRound(n, n.home);
    case 'drinker':
      if (S.flags.jedDead) return { mode: 'dead', dur: 999, seg: n.home.seg, lx: 89.4, z: -6.2 };
      if (t >= 21.5 || t < 6.1) return dailyRound(n, n.home);
      return { mode: 'drink', seg: n.home.seg, lx: 89.3, z: -5.9, dur: 90 };
    case 'rachel':
      if (rec.following) return null;
      return dailyRound(n, n.home);
    case 'master':
      if (t >= 21.5 || t < 6.1) return dailyRound(n, n.home);
      return { mode: 'stand', seg: n.home.seg, lx: 81.7, z: -5.5, dur: 40, face: 'east' };
    case 'took': return { mode: 'sit', seg: n.home.seg, lx: 89.3, z: -5.9, dur: 999 };
  }
  return null;
}
function placeNamed() {
  const at = (k, site, lx, z, mode) => { const n = NPC_BY[k]; n.home = site; placeNPC(n, site.seg, lx, z, site.floor, site.side); n.gone = false; n.mode = mode || 'idle'; n.t = 0; n.stun = 0; n.special = false; };
  at('biscuit', ARRIVAL, 84.6, -3.4); at('elliott', ARRIVAL, 88.2, -2.2); at('larisa', ARRIVAL, 83.2, -4.9); at('betty', ARRIVAL, 89.6, -3.1);
  at('jed', JEDSITE, 89.3, -5.9, S.flags.jedDead ? 'dead' : 'idle');
  if (!S.flags.rachelGone) { if (npcRec('rachel').following) { const n = NPC_BY.rachel; placeNPC(n, S.seg, clamp(S.lx - 1.2, 0.5, P - 0.5), clamp(S.z, -12, -0.6), S.floor, S.side); n.gone = false; n.mode = 'follow'; n.home = UNI; } else at('rachel', UNI, 84.5, -4.4); }
  else NPC_BY.rachel.gone = true;
  at('treacle', UNI, 81.7, -5.5); at('pruitt', UNI, 88.8, -3.8);
  for (const k of ['dan', 'dir1', 'dir2', 'dir3', 'dir4', 'wand']) { NPC_BY[k].gone = true; NPC_BY[k].mode = 'idle'; }
  const tk = NPC_BY.took; if (S.flags.tookSite) at('took', S.flags.tookSite, 89.3, -5.9, 'sit'); else tk.gone = true;
  for (const n of POOL) { n.assign = null; n.gone = true; n.special = false; }
  RAID.on = false; FALLER.n = null;
  assignSites();
}

/* ---------- University furnishings ---------- */
const UNIPROPS = new THREE.Group(); scene.add(UNIPROPS);
{
  const p = new Parts();
  p.box('wood', 81.0, 0, -5.0, 81.5, 1.05, -4.2, K.wood); p.box('wood', 80.95, 1.05, -5.05, 81.65, 1.12, -4.15, K.woodL);
  for (const bz of [-3.4, -4.4, -5.4]) { p.box('wood', 83.2, 0.42, bz - 0.15, 87.4, 0.47, bz + 0.15, K.wood); for (const lx of [83.3, 87.3]) p.box('wood', lx - 0.03, 0, bz - 0.03, lx + 0.03, 0.42, bz + 0.03, K.wood); }
  for (let i = 0; i < 6; i++) p.box('plain', 88.9 + (i % 3) * 0.6, 0.78, -5.3 + Math.floor(i / 3) * 0.5, 89.3 + (i % 3) * 0.6, 0.78 + 0.04 + (i % 2) * 0.05, -5.0 + Math.floor(i / 3) * 0.5, [0.55, 0.52, 0.45]);
  for (const k in p.m) { const m = new THREE.Mesh(merge(p.m[k]), MAT[k]); m.frustumCulled = false; UNIPROPS.add(m); }
  const bc = document.createElement('canvas'); bc.width = 128; bc.height = 256; const g = bc.getContext('2d');
  g.fillStyle = '#b9ad90'; g.fillRect(0, 0, 128, 256); g.strokeStyle = '#3a2a18'; g.lineWidth = 5; g.strokeRect(8, 8, 112, 240);
  g.beginPath(); g.moveTo(24, 120); g.quadraticCurveTo(64, 100, 64, 140); g.quadraticCurveTo(64, 100, 104, 120); g.lineTo(104, 170); g.quadraticCurveTo(64, 150, 64, 180); g.quadraticCurveTo(64, 150, 24, 170); g.closePath(); g.stroke();
  g.fillStyle = '#3a2a18'; g.font = '600 22px Georgia, serif'; g.textAlign = 'center'; g.fillText('MST', 64, 70); g.fillText('102', 64, 220);
  const bm = makeMat({ map: new THREE.CanvasTexture(bc), gain: 1.4, double: true, spec: 0.02 });
  for (const bx of [82.6, 85.0, 89.8]) { const pl = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 1.4), bm); pl.position.set(bx, 2.75, -3.35); UNIPROPS.add(pl); }
}
function updateProps() {
  const v = S.side === UNI.side && Math.abs(UNI.floor - S.floor) <= FWIN && Math.abs(UNI.seg - S.seg) <= 2;
  UNIPROPS.visible = v; if (v) UNIPROPS.position.set((UNI.seg - S.seg) * P, (UNI.floor - S.floor) * H, 0);
}

/* ---------- Things that happen ---------- */
const RAID = { on: false, cool: 60, t: 0, floor: 0, side: 0, lostT: 0, cornerTried: false };
const FALLER = { n: null, t: 0, state: '', cool: 30 };
let passCool = 20, throwCool = 10, storyT = 0, ceremony = null;
function inRange(site, r) { return S.side === site.side && S.floor === site.floor && Math.abs(gx(site.seg, 86) - S.lx) < r; }
function freePool() { return POOL.find(p => !p.assign && !p.special); }
function startRaid() {
  const dir = Math.random() < 0.5 ? -1 : 1, band = ['dir1', 'dir2', 'dir3', 'dir4'].slice(0, 2 + Math.floor(Math.random() * 3));
  if (!S.flags.danFallen && Math.random() < 0.75) band.push('dan');
  band.forEach((k, i) => {
    const n = NPC_BY[k], x = S.lx + dir * (48 + i * 1.6);
    placeNPC(n, S.seg, x, n.d.lane + (Math.random() - 0.5) * 0.4, S.floor, S.side); wrapNPC(n);
    n.gone = false; n.mode = 'raid'; n.t = 999; n.path = []; n.chaseSpeed = k === 'dan' ? 4.2 : 4.6; n.special = true; n.stun = 0;
  });
  RAID.on = true; RAID.seenYou = 0; RAID.t = 0; RAID.floor = S.floor; RAID.side = S.side; RAID.lostT = 0; RAID.cornerTried = false; RAID.band = band; RAID.dir = dir;
  if (!S.flags.raidSeen) { S.flags.raidSeen = 1; showMoment('direites'); }
  logJ(`Direites on floor ${fmt(S.floor)}${band.includes('dan') ? ' — Dire Dan with them' : ''}.`);
  SFX.chant && SFX.chant();
}
function endRaid() { RAID.on = false; RAID.cool = 360 + Math.random() * 420; for (const k of ['dan', 'dir1', 'dir2', 'dir3', 'dir4']) { const n = NPC_BY[k]; if (n.mode !== 'fall' && n.mode !== 'fallWith') { n.gone = true; n.mode = 'idle'; n.special = false; } } }
function updateRaid(dt) {
  if (!RAID.on) return;
  RAID.t += dt;
  const band = RAID.band.map(k => NPC_BY[k]).filter(n => !n.gone && n.mode !== 'fall' && n.mode !== 'fallWith');
  if (!band.length || S.time >= LIGHTS_OFF || PL.dead) { endRaid(); return; }
  if (S.floor !== RAID.floor || S.side !== RAID.side || S.fall) RAID.lostT += dt; else RAID.lostT = 0;
  if (RAID.lostT > 12) { endRaid(); toast('The Direites have lost you.'); return; }
  let nearest = Infinity;
  for (const n of band) {
    const d = npcDist(n); nearest = Math.min(nearest, d);
    if (n.mode === 'raid' && d < 26) { n.mode = 'chase'; if (!RAID.seenYou) { RAID.seenYou = 1; toast('They have seen you.', true); } }
  }
  if (nearest > 130) { endRaid(); return; }
  // Rachel at the rail, cornered — a chance of the great loss
  const r = NPC_BY.rachel;
  if (!RAID.cornerTried && npcRec('rachel').following && !r.gone && nearest < 7 && S.z > -1.6) {
    RAID.cornerTried = true;
    if (Math.random() < 0.5) greatLoss();
  }
}
function greatLoss() {
  const r = NPC_BY.rachel, band = RAID.band.map(k => NPC_BY[k]);
  band.forEach(n => { if (n.mode === 'chase') { n.mode = 'script'; n.walking = false; } });
  r.mode = 'script'; npcRec('rachel').following = false;
  showCaptions([
    { who: '', text: 'They come from both sides now, walking, not running. There is nowhere left to go.' },
    { who: 'Rachel', text: '(She looks at you — calm, almost smiling — and tells you that she loves you.)' },
    { who: '', text: 'Then she climbs the railing, and lets go.', fx: () => { placeNPC(r, S.seg, S.lx + 0.8, 0.6, S.floor, S.side); r.mode = 'fall'; r.vy = 0; r.vz = 1.2; r.vx = 0; r.special = true; setTimeout(() => { r.gone = true; }, 5000); SFX.scream && SFX.scream(); } },
  ], () => { band.forEach(n => { if (n.mode === 'script') n.mode = 'chase'; }); });
  S.flags.rachelGone = 1; logJ('Rachel went over the railing to get away from them. I watched her fall until the dark had her.');
}
function tackleDan() {
  const d = NPC_BY.dan;
  logJ('Tackled Dire Dan over the railing. We went down together.');
  S.flags.danFallen = 1; S.flags.danWith = 1; S.flags.danHitT = 1.5;
  startFall(true);
  d.mode = 'fallWith'; d.off = { x: 0.55, y: 0.1, z: 0.35 }; d.special = true; d.gone = false;
  for (const k of RAID.band) if (k !== 'dan') { NPC_BY[k].mode = 'script'; }
  setTimeout(() => endRaid(), 2500);
  toast('He is clawing at you, screaming that he will kill you. Shove him away (F) — or don’t.', true);
}
function shoveInFall(n) {
  if (n.d.key === 'dan') { S.flags.danWith = 0; n.mode = 'fall'; n.vx = (Math.random() - 0.5) * 2; n.vz = S.z < 8 ? 2.4 : -2.4; n.extraFall = 5; setTimeout(() => { n.gone = true; n.special = false; }, 9000); toast('You kick free. He falls away from you, still screaming.'); SFX.hit(); }
  else if (FALLER.n === n) { letGoFaller(true); }
}
function spawnPassingFaller() {
  const n = freePool(); if (!n) return;
  n.special = true; n.gone = false;
  placeNPC(n, S.seg, S.lx + (Math.random() - 0.5) * 24, 3 + Math.random() * 10, S.floor, S.side); n.ly = S.ly + 18 + Math.random() * 14; wrapNPC(n);
  n.mode = 'fall'; n.vy = -30; n.vx = 0; n.vz = 0; n.extraFall = PL.falling ? 8 : 0;
  SFX.scream && SFX.scream();
  setTimeout(() => { n.special = false; n.gone = true; n.mode = 'idle'; }, 7000);
}
function spawnCatchable() {
  const wand = !S.flags.wandMet && S.fall && (S.fall.days >= 1 || S.fall.t > 120);
  const n = wand ? NPC_BY.wand : freePool(); if (!n) return;
  n.special = true; n.gone = false; n.mode = 'fall'; n.vx = 0; n.vz = 0; n.vy = PL.vy; n.extraFall = 1.6;
  placeNPC(n, S.seg, S.lx + (Math.random() < 0.5 ? -2 : 2), clamp(S.z + (Math.random() - 0.5) * 3, 1, CHASM - 1), S.floor, S.side); n.ly = S.ly + 34; wrapNPC(n);
  FALLER.n = n; FALLER.t = 0; FALLER.state = 'approach'; FALLER.caught = false;
  if (n.d.generic) { const h = strHash('faller' + S.day + S.floor); n.gname = SITE_NAMES[h % SITE_NAMES.length]; n.gtown = TOWNS[(h >>> 8) % TOWNS.length]; }
  toast('Someone is falling above you — and catching up.');
}
function catchFaller() {
  const n = FALLER.n; if (!n) return;
  n.mode = 'fallWith'; n.off = { x: 0.5, y: -0.05, z: 0.3 }; FALLER.state = 'held'; FALLER.caught = true; FALLER.t = 0;
  if (n.d.key === 'wand') { S.flags.wandMet = 1; logJ('Caught hold of a falling woman named Wand. She would not let go.'); }
  openDialogue(n);
}
function letGoFaller(pushed) {
  const n = FALLER.n; if (!n) return;
  n.mode = 'fall'; n.extraFall = 0; n.vz = S.z < 8 ? -3.2 : 3.2; n.vx = 0; FALLER.state = 'leaving';
  n.onImpact = () => { n.gone = true; n.special = false; if (FALLER.n === n) FALLER.n = null; toast(`${n.d.key === 'wand' ? 'Wand' : 'They'} hit${n.d.key === 'wand' ? 's' : ''} the edge of a floor rushing past — and ${n.d.key === 'wand' ? 'is' : 'are'} gone. You never find out which floor.`); if (n.d.key === 'wand') { S.flags.wandLanded = 1; logJ('Wand let go and steered for the stacks. She made it, I think. I never found her again.'); } };
  toast(pushed ? 'You let go.' : (n.d.key === 'wand' ? 'Wand squeezes your hand once — and lets go, steering for the stacks.' : 'They let go, and steer for the stacks.'));
}
function updateFaller(dt) {
  const n = FALLER.n; if (!n) return;
  FALLER.t += dt;
  if (FALLER.state === 'approach') {
    const dy = (n.floor - S.floor) * H + n.ly - S.ly;
    if (dy < 2.5) { n.extraFall = 0; n.vy = PL.vy; FALLER.state = 'near'; FALLER.t = 0; n.mode = 'fallWith'; n.off = { x: gx(n.seg, n.lx) - S.lx, y: 0.3, z: n.z - S.z }; }
    if (!PL.falling) { n.gone = true; n.special = false; FALLER.n = null; }
  } else if (FALLER.state === 'near') {
    n.off.x *= Math.pow(0.6, dt); n.off.z *= Math.pow(0.6, dt); n.off.x = Math.sign(n.off.x || 1) * Math.max(Math.abs(n.off.x), 1.0);
    if (FALLER.t > 14) { toast('You were too slow. They drift away below you.'); n.mode = 'fall'; n.extraFall = 3; n.vz = S.z < 8 ? 1.5 : -1.5; FALLER.state = 'leaving'; setTimeout(() => { n.gone = true; n.special = false; if (FALLER.n === n) FALLER.n = null; }, 8000); }
  } else if (FALLER.state === 'held') {
    const talked = npcRec(n.d.key).talks > 0 && MODE === 'play';
    if (talked && FALLER.t > (n.d.key === 'wand' ? 80 : 50)) letGoFaller(false);
  }
  if (!PL.falling && FALLER.state !== 'leaving') { n.gone = true; n.special = false; FALLER.n = null; }
}
function startCeremony() {
  ceremony = { day: S.day };
  const text = S.flags.mstDone ? FRAGMENTS[strHash('mst' + S.day) % FRAGMENTS.length] : MST_FIRST;
  const T = NPC_BY.treacle, R = NPC_BY.rachel;
  for (const n of [NPC_BY.pruitt, ...POOL.filter(p => p.assign && p.assign.seg === UNI.seg && p.assign.floor === UNI.floor)]) { n.mode = 'stand'; n.t = 400; n.faceAt = { seg: UNI.seg, lx: 81.3, z: -4.6 }; planPath(n, UNI.seg, 83.6 + Math.random() * 3.4, -3.3 - Math.random() * 2.2); }
  T.mode = 'speak'; T.t = 400; planPath(T, UNI.seg, 81.7, -5.5); T.goalFace = 'east';
  const lines = [
    { who: 'Master Treacle', text: 'Friends. Colleagues. Another year of honest work among the shelves.' },
    { who: 'Master Treacle', text: 'The catalogue now holds four thousand one hundred and twelve coherent fragments of three words or more. Out of — well. Out of all of it.' },
  ];
  const mine = S.frags.find(f => f.uni);
  if (mine) lines.push({ who: 'Master Treacle', text: `An honourable mention, this year, to Soren Johansson, for “${mine.text}”.` });
  if (!S.flags.rachelGone && !npcRec('rachel').following) { R.mode = 'speak'; R.t = 400; planPath(R, UNI.seg, 81.9, -4.6); R.goalFace = 'east'; lines.push({ who: 'Master Treacle', text: 'By vote of the faculty, the Most Significant Text of the year — read for us by Dr. Rachel Hasnick.' }); lines.push({ who: 'Rachel Hasnick', text: `“${text}.”` }); }
  else lines.push({ who: 'Master Treacle', text: `The Most Significant Text of the year: “${text}.”` });
  lines.push({ who: '', text: '(A murmur. Someone weeps quietly. Someone else insists the second word is a typo.)' });
  lines.push({ who: 'Master Treacle', text: 'Thank you all. Discussion continues at the kiosk, as usual.' });
  showCaptions(lines, () => {
    S.flags.mstDone = 1; S.flags.mstDay = S.day; logJ(`Heard the University read its Most Significant Text: “${text}.”`);
    for (const n of [T, R, NPC_BY.pruitt, ...POOL]) if (n.mode === 'stand' || n.mode === 'speak') { n.mode = 'idle'; n.t = 0; n.faceAt = null; }
    ceremony = null;
  });
}
function storyTick(dt) {
  storyT += dt; updateProps(); updateRaid(dt); updateFaller(dt);
  if (storyT < 1) return; const sec = storyT; storyT = 0;
  if (!S.fall) assignSites();
  // Jed drinks himself to death on the second night, and is back the next morning
  if (S.day >= 2 && S.time >= 20.5 && !S.flags.jedDeadDone) { S.flags.jedDeadDone = 1; S.flags.jedDead = 1; const j = NPC_BY.jed; j.mode = 'dead'; j.path = []; j.lx = 89.4; j.z = -6.2; j.lieYaw = 0.4; if (inRange(JEDSITE, 60)) toast('Over at Jed’s table, somebody stops talking mid-sentence.'); }
  // the University
  if (!S.flags.uniFound && inRange(UNI, 22)) { S.flags.uniFound = 1; S.flags.uniHeard = 1; showMoment('university'); logJ('Found the University: three rest areas west, two floors down, as Larisa said.'); }
  if (!ceremony && S.time >= 19 && S.time < 20.5 && inRange(UNI, 36) && S.flags.mstDay !== S.day && (!S.flags.mstDone || S.day % 3 === 0)) startCeremony();
  // Rachel walking with you
  const rr = npcRec('rachel'); if (rr.following && !S.flags.rachelWalked) { S.flags.rwT = (S.flags.rwT || 0) + sec; if (S.flags.rwT > 60) { S.flags.rachelWalked = 1; rr.aff += 1; logJ('Walked a long way with Rachel. We talked about everything, and then about everything again.'); } }
  // raids
  RAID.cool -= sec;
  if (!RAID.on && !S.fall && !PL.dead && S.day >= 2 && S.time > 8 && S.time < 21 && RAID.cool <= 0 && MODE === 'play' && Math.random() < sec / (S.day >= 3 ? 420 : 900)) startRaid();
  // people falling past the rail, and people you can catch in the fall
  passCool -= sec; FALLER.cool -= sec;
  const atRail = S.z > -1.4 && !S.fall;
  if ((atRail || S.fall) && passCool <= 0 && Math.random() < sec / (S.fall ? 50 : 35)) { passCool = 25; spawnPassingFaller(); }
  if (S.fall && !FALLER.n && FALLER.cool <= 0 && PL.falling && !PL.dead) {
    const wand = !S.flags.wandMet && (S.fall.days >= 1 || S.fall.t > 120);
    if (Math.random() < sec / (wand ? 25 : 150)) { FALLER.cool = 90; spawnCatchable(); }
  }
  // people nearby throwing searched books over the railing
  throwCool -= sec;
  if (throwCool <= 0 && !S.fall && S.time > 8 && S.time < 21) {
    const th = POOL.find(n => n.assign && n.assign.role === 'searchers' && !n.gone && n.floor === S.floor && npcDist(n) < 35 && n.mode === 'read');
    if (th && Math.random() < 0.3) { throwCool = 14; const x = gx(th.seg, th.lx); throwBookVisual({ s: S.side, f: S.floor, c: th.seg * CASES + 3, r: 2, p: Math.floor(Math.random() * 40) }, x, 1.3, 0.35); }
    else throwCool = 6;
  }
  // the falling Dan fight
  if (S.flags.danWith && PL.falling && !PL.dead) { S.flags.danHitT -= sec; if (S.flags.danHitT <= 0) { S.flags.danHitT = 1.5; hurt(11, 'Dire Dan'); } }
  updateThreadsHUD();
}
function storyDawn(prev) {
  if (S.flags.jedDead) { S.flags.jedDead = 0; S.flags.jedRevived = 1; }
  S.flags.danWith = 0;
  placeNamed();
  if (S.fall && FALLER.n) FALLER.n = null;
}
function storyEvent(type, data) {
  if (type === 'landed') {
    const fallen = data.fallen || 0;
    if ((!S.flags.tookSite && fallen >= 50000) || (S.flags.tookSite && npcRec('took').met && Math.random() < 0.2 && fallen >= 50000)) {
      S.flags.tookSite = { seg: S.seg, floor: S.floor, side: S.side }; S.flags.tookHeard = 1;
    }
    S.flags.landed = 1;
  }
}
function onNpcHit(n) {
  if (n.d.role === 'direite' || n.d.role === 'dan') { hurt(24, n.d.role === 'dan' ? 'Dire Dan' : 'the Direites'); if (PL.dead) endRaid(); }
}
function storyTargets(o, d) {
  // Dire Dan within reach, at the rail: tackle him over it
  const dan = NPC_BY.dan;
  if (RAID.on && !dan.gone && dan.mode !== 'fall' && dan.mode !== 'fallWith' && npcDist(dan) < 2.4 && S.z > -1.3) return { kind: 'tackle', n: dan };
  if (FALLER.n && FALLER.state === 'near' && PL.falling) return { kind: 'catch', n: FALLER.n };
  return null;
}

/* ---------- Threads: what you have heard, what you might do ---------- */
const THREADS = [
  { id: 'meet', text: () => 'Talk to the four who arrived with you', show: () => true, done: () => ['biscuit', 'elliott', 'larisa', 'betty'].every(k => npcRec(k).met) },
  { id: 'kiosk', text: () => 'See what the kiosk will give you', show: () => true, done: () => S.flags.usedKiosk },
  { id: 'sack', text: () => `Biscuit’s book: floor ${fmt(SACK.f)}, case ${fmt(SACK.c)}, shelf 4, book 13 — page 189`, show: () => S.flags.sackTold, done: () => S.flags.sackFound },
  { id: 'throw', text: () => 'Elliott wants searched books thrown over the railing (G at the rail)', show: () => S.flags.elliottPlan, done: () => S.stats.thrown > 0 },
  { id: 'reset', text: () => 'See what dawn does to the books you threw', show: () => S.stats.thrown > 0, done: () => S.flags.sawReset },
  { id: 'jed', text: () => 'Jed is drinking at the next rest area east', show: () => S.flags.jedHeard || npcRec('jed').met, done: () => S.flags.jedBack },
  { id: 'uni', text: () => 'A university, they say: three rest areas west, two floors down', show: () => S.flags.uniHeard, done: () => S.flags.uniFound },
  { id: 'mst', text: () => 'The University reads its Most Significant Text at 19:00', show: () => S.flags.uniFound, done: () => S.flags.mstDone },
  { id: 'frag', text: () => 'Bring Master Treacle a readable fragment', show: () => S.flags.uniFound, done: () => S.flags.uniFrag },
  { id: 'rachel', text: () => 'Walk with Rachel Hasnick', show: () => npcRec('rachel').met && !S.flags.rachelGone, done: () => S.flags.rachelWalked },
  { id: 'direites', text: () => 'The Direites raid these floors. Run — or meet Dire Dan at the rail.', show: () => S.flags.raidSeen, done: () => S.flags.danFallen },
  { id: 'stacks', text: () => 'While falling, steer into a railing: you’ll wake tomorrow on that floor', show: () => S.flags.fallHint || S.fall, done: () => S.flags.landed },
  { id: 'took', text: () => 'Someone far, far below has done the arithmetic', show: () => S.flags.tookHeard, done: () => npcRec('took').met },
];
function activeThreads() { return THREADS.filter(t => t.show() && !t.done()); }
function updateThreadsHUD() { const a = activeThreads(); const el = $('#h-thread'); if (!el) return; el.hidden = !a.length || !S.settings.hints; if (a.length) el.textContent = a[a.length - 1].text(); }

/* ---------- Dialogue ---------- */
const pick = (arr, seed) => arr[mod(seed, arr.length)];
const back = { t: 'Back', go: 'root' };
const DLG = {
  biscuit: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Biscuit, who knows exactly what this place is.'); text = "Soren! You're up. Isn't it — well, it's awful, obviously. But look at it! Do you know Borges? “The Library of Babel”? This is it. This is exactly it."; }
      else if (c.greet && S.day >= 2 && !S.flags.sackTold) text = "Soren — Soren, come here. I found something. I actually found something.";
      else if (c.greet) text = S.flags.sackFound ? "I read it again this morning. Two words, clean as a whistle, in an ocean of noise. It's the closest thing I have to scripture." : "Every book that can exist, and we get to look through them. Terrible. Wonderful. Terrible.";
      else text = 'What else?';
      return { text, opts: [
        { t: 'Every book?', go: 'every' },
        { t: 'What did you find?', go: 'sack', if: S.day >= 2 && !S.flags.sackTold },
        { t: 'What does “sack it” mean?', go: 'mean', if: S.flags.sackTold },
        { t: 'What should we do?', go: 'plan' },
      ] };
    },
    every() { return { text: "Every arrangement of the ninety-five characters on a typewriter, four hundred and ten pages at a time. Most of it is noise. But somewhere is every true sentence ever written — and every false one — and every almost-true one with a typo in it.", opts: [{ t: 'Including my life?', go: 'mine' }] }; },
    mine() { return { text: "Including yours. Somewhere. Spelled right. And a few quadrillion that get your middle name wrong on page three hundred and six.", opts: [back] }; },
    sack() { S.flags.sackTold = 1; logJ(`Biscuit found two readable words: “sack it.” Floor ${fmt(SACK.f)}, case ${fmt(SACK.c)}, shelf 4, book 13, page 189.`); return { text: `Floor ${fmt(SACK.f)}. Case ${fmt(SACK.c)}, shelf four, book thirteen. Page one hundred and eighty-nine. Two words, all by themselves: “sack it.” Go and look. Go on.`, opts: [{ t: 'What does it mean?', go: 'mean' }] }; },
    mean() { return { text: "“Sack it.” Give it up? Or — put it in a sack. Carry it. Carry what? The search? Ourselves? It's a message, Soren. It has to be. Nothing else in here has two words in a row.", opts: [back] }; },
    plan() { return { text: 'Elliott has a plan. Elliott always has a plan. I prefer reading.', opts: [back] }; },
  },
  elliott: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Elliott, an agnostic from California.'); text = "Elliott. Santa Cruz, originally. Agnostic — which I'm now told was the wrong call, though so was everybody's. Nice to meet you, fellow wrong person."; }
      else if (c.greet && S.flags.sawReset) text = "They came back. Every book we threw over. Right where they were, this morning. Okay. So that's how it's going to be.";
      else if (c.greet) text = S.flags.elliottPlan ? 'How many have you checked? Throw them over when you’re done — then we know.' : 'We need a system. Otherwise we’re just browsing forever.';
      else text = 'Anything else?';
      return { text, opts: [
        { t: 'What do we do?', go: 'plan', if: !S.flags.elliottPlan },
        { t: 'Do you think we’ll find them?', go: 'find' },
        { t: 'What did you do, before?', go: 'before' },
      ] };
    },
    plan() { S.flags.elliottPlan = 1; logJ('Elliott’s plan: every book we search goes over the railing, so we never check it twice.'); return { text: "We get systematic. Each of us takes a case. Anything we've searched goes over the railing — that way we never check the same book twice. Simple.", opts: [back] }; },
    find() { return { text: 'Our books? Do the math with Biscuit sometime. Actually — don’t. Some numbers you can’t un-know.', opts: [back] }; },
    before() { return { text: 'Contractor. Decks, mostly. I’d have given a lot to build something in here that stayed built overnight.', opts: [back] }; },
  },
  larisa: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Larisa. Breast cancer, the long kind. She keeps taking deep breaths just to feel them.'); text = "Larisa. The last thing I remember is the hospital. Breast cancer — the long kind. And now look. I can breathe all the way to the bottom. I keep doing it just to feel it."; }
      else if (c.greet) text = S.flags.uniHeard ? 'Did you go and find the University yet? Three rest areas west, two floors down.' : 'I heard something interesting yesterday.';
      else text = 'Yes?';
      return { text, opts: [
        { t: 'Who do you miss?', go: 'miss' },
        { t: 'What did you hear?', go: 'rumour', if: !S.flags.uniHeard },
        { t: 'Are you all right?', go: 'ok' },
      ] };
    },
    miss() { return { text: 'My daughter. She was nine. She’s — I don’t know what she is now. Grown. Old. Gone. Nobody tells you what time it is up there.', opts: [back] }; },
    rumour() { S.flags.uniHeard = 1; logJ('Larisa heard of a university — three rest areas west, two floors down.'); return { text: 'A man came through — said there’s a university, of all things. Three rest areas west, two floors down. People who’ve been here a hundred years, studying the books like scripture.', opts: [back] }; },
    ok() { return { text: 'I’m dead, Soren. I’m the best I’ve been in years.', opts: [back] }; },
  },
  betty: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Betty, who doesn’t think much of my homework.'); text = "Betty. You’re the Mormon, aren’t you? You’ve got the look — like you’re waiting for somebody to come and grade your homework."; }
      else if (c.greet) text = m.aff >= 3 ? 'Sit with me by the railing tonight. It’s the only view in the building.' : 'Still behaving yourself?';
      else text = 'Well?';
      return { text, opts: [
        { t: 'What do you mean?', go: 'mean', if: !m.f.cov },
        { t: 'Walk with me a while.', go: 'walk', if: m.f.cov && !m.f.walk },
        { t: 'What did you do, before?', go: 'before' },
      ] };
    },
    mean(c) { c.rec.f.cov = 1; return { text: "Xandern said it himself. Earthly covenants, dissolved. You’re not married anymore, Soren. Neither am I. I’m just making an observation.", opts: [{ t: 'I’m still married, as far as I’m concerned.', go: 'still' }, { t: 'Walk with me a while.', go: 'walk' }] }; },
    still() { return { text: 'Suit yourself. We’ve got a very long time for you to change your mind.', opts: [back] }; },
    walk(c) { c.rec.f.walk = 1; c.rec.aff += 1; logJ('Walked a while with Betty. I am not sure what I think about it.'); return { text: 'Well, look at that. Maybe you’re not so wrong about everything after all.', opts: [back] }; },
    before() { return { text: 'Paralegal. Tulsa. Two divorces, one cat. The cat was the good one.', opts: [back] }; },
  },
  jed: {
    root(c) {
      const m = c.rec; let text;
      if (S.flags.jedDead) return { text: '(Jed isn’t breathing. The glass is still in his hand.)', opts: [] };
      if (c.greet && S.flags.jedRevived && !S.flags.jedBack) { S.flags.jedBack = 1; m.met = true; logJ('Jed drank himself to death on the second night. The next morning he was back, sober, and furious about it.'); text = 'Well. That settles that. You can’t even drink yourself out of here. I checked. Thoroughly.'; }
      else if (c.greet && !m.met) { m.met = true; S.flags.jedHeard = 1; logJ('Met Jed, who has discovered the kiosk serves whiskey.'); text = '(He’s holding a glass of something amber.) Kiosk does whiskey. Any whiskey. I asked for a bottle from nineteen twenty-six just to see. Got it. Want one?'; }
      else if (c.greet) text = S.flags.jedBack ? 'Still here. Still sober, mostly. It doesn’t take the edge off the way it used to — the edge comes back every morning.' : 'Pull up a chair.';
      else text = '(He drinks.)';
      return { text, opts: [
        { t: 'Sure, one.', go: 'one', if: !S.flags.jedBack },
        { t: 'Go easy.', go: 'easy', if: !S.flags.jedBack },
        { t: 'What was it like?', go: 'like', if: S.flags.jedBack },
      ] };
    },
    one() { S.drunk = clamp(S.drunk + 0.3, 0, 2); SFX.drink && SFX.drink(); return { text: '(It’s very good whiskey. It was always going to be.) There you go. Now you’re a sinner too.', opts: [back] }; },
    easy() { return { text: 'Easy’s for people with somewhere to be.', opts: [back] }; },
    like() { return { text: 'Like falling asleep with the TV on. Then the lamps come back and there you are — whole, clean, and nothing’s changed. Worst hangover I never had.', opts: [back] }; },
  },
  rachel: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Dr. Rachel Hasnick of the University.'); text = S.flags.mstDone ? 'You were staring at me like I’d said something important. It’s one sentence. It’s the best sentence we found this year, which is a different thing.' : 'A new face. Rachel — Rachel Hasnick. Doctor, technically, which here mostly means I argue about commas for the University.'; }
      else if (c.greet && m.following) text = 'I’m here. Lead on — slowly, if you can manage it.';
      else if (c.greet && S.flags.kissed) text = 'There you are. I was starting to count the lamps.';
      else if (c.greet) text = 'Back again? The faculty will start to talk.';
      else text = 'What else?';
      return { text, opts: [
        { t: 'What is the University?', go: 'uni' },
        { t: 'How long have you been here?', go: 'long' },
        { t: 'Walk with me.', go: 'walk', if: !m.following && m.aff >= 2 },
        { t: 'Wait here for me.', go: 'wait', if: m.following },
        { t: 'Stay a while.', go: 'kiss', if: m.aff >= 4 && !S.flags.kissed },
        { t: 'Tell me something.', go: 'tell', if: S.flags.kissed },
      ] };
    },
    uni() { return { text: 'After the first fifty years, people either organise or dissolve. We organised. We catalogue coherent text. We argue. Once a year we choose the Most Significant Text. It keeps the edges of us from going soft.', opts: [back] }; },
    long(c) { if (!c.rec.f.exp) { c.rec.f.exp = 1; c.rec.aff += 1; } return { text: 'A hundred and two years. In year fifty-eight I led an expedition — nine years walking in one direction. Shelves. Kiosks. Not a living soul after the first few months. Eventually somebody asked what we were doing, and none of us had an answer, so we turned around.', opts: [back] }; },
    walk(c) { c.rec.following = true; const n = NPC_BY.rachel; n.mode = 'follow'; n.special = true; logJ('Rachel agreed to walk with me.'); return { text: 'All right. Show me what you’ve been reading.', opts: [] }; },
    wait(c) { c.rec.following = false; const n = NPC_BY.rachel; n.mode = 'idle'; n.t = 0; n.special = false; n.home = UNI; return { text: 'I’ll be at the University. I’m always at the University.', opts: [] }; },
    kiss(c) { S.flags.kissed = 1; c.rec.aff += 1; logJ('Rachel kissed me. It is the first thing in a very long time that has surprised me.'); return { text: '(She kisses you. It is the first thing in a very long time that has surprised you.)', opts: [back] }; },
    tell(c) {
      const L = ['I was a linguist. I spent my life on dead languages. Now I’m in a library of every language that could exist, and none of them is spoken.', 'Sometimes I read a random page aloud, just to hear what it sounds like. It sounds like somebody choking. I keep doing it.', 'If you find your book first — go. Don’t wait for me. Promise.', 'The worst thing isn’t the size of it. It’s that it’s fair. Everybody has a book. Everybody has the same odds.'];
      const i = c.rec.f.t || 0; c.rec.f.t = i + 1; return { text: L[i % L.length], opts: [back] };
    },
  },
  treacle: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Master Treacle, who presides over the University.'); text = 'Ah! A new face — or an old face I have forgotten; both are common. Master Treacle. I preside. Mostly that means I read out the numbers.'; }
      else text = c.greet ? 'Welcome, welcome. The catalogue is open.' : 'Yes?';
      const unsub = S.frags.filter(f => !f.uni);
      return { text, opts: [
        { t: 'What numbers?', go: 'nums' },
        { t: 'I found words in a book.', go: 'submit', if: unsub.length > 0 },
        { t: 'When is the reading?', go: 'when' },
      ] };
    },
    nums() { return { text: 'Four thousand one hundred and twelve coherent fragments of three words or more, gathered by the faculty over a century. Out of — well. Out of all of it.', opts: [back] }; },
    submit() { const f = S.frags.find(x => !x.uni); f.uni = 1; S.flags.uniFrag = 1; logJ(`Gave the University a fragment: “${f.text}.” Master Treacle wrote it in his ledger.`); SFX.chime(); return { text: `(He copies it into an enormous ledger with great ceremony.) “${f.text}.” Catalogued. The faculty thanks you — and will argue about it for years.`, opts: [back] }; },
    when() { return { text: S.flags.mstDone ? 'Seven o’clock, whenever the faculty has a text worth reading. Every few days, lately.' : 'Seven o’clock tonight. Don’t be late; I read the numbers first and they are very exciting.', opts: [back] }; },
  },
  pruitt: {
    root(c) {
      const m = c.rec; if (c.greet && !m.met) m.met = true;
      return { text: c.greet ? 'Department of Coherent Text. Don’t laugh. We have four words in a row from the east stacks and it’s the most exciting thing that’s happened to me since my own funeral.' : 'Anything else?', opts: [{ t: 'Which four words?', go: 'four' }] };
    },
    four() { return { text: '“the cat was fine.” Nobody agrees on what it means. Master Treacle thinks it’s about grace. I think somebody’s cat was fine.', opts: [back] }; },
  },
  dan: {
    root(c) {
      c.rec.met = true;
      return { text: '(He is smiling, and his arms are open.) Shh. Don’t run. Running is a sentence someone else already wrote. Pain is the only thing in here nobody wrote first. Come and be written.', opts: [{ t: 'Leave us alone.', go: 'no' }] };
    },
    no() { return { text: '(He only smiles wider.)', opts: [] }; },
  },
  wand: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.f.caught) { m.f.caught = 1; m.met = true; text = '(She grabs you so hard it hurts, and doesn’t let go.) Oh — oh, you’re real. You’re really real. How long — I stopped counting the dark a long time ago.'; }
      else text = c.greet ? '(She holds on.)' : 'Don’t let go yet.';
      return { text, opts: [
        { t: 'What’s your name?', go: 'name' },
        { t: 'Why did you jump?', go: 'why' },
        { t: 'Can we stop?', go: 'stop' },
        { t: 'Is there anyone down there?', go: 'took' },
      ] };
    },
    name() { return { text: 'Wand. It was short for something once. I remember the falling better than anything that came before it.', opts: [back] }; },
    why() { return { text: 'There was a reason. There’s always a reason. It seemed so important at the time.', opts: [back] }; },
    stop() { S.flags.fallHint = 1; return { text: 'Someone told me — a thousand years ago, maybe — if you steer into a railing hard enough, you die, and you wake up on that floor. I’ve never had the nerve. Maybe now I do.', opts: [back] }; },
    took() { S.flags.tookHeard = 1; return { text: 'There’s a man down there — way down — who’s worked out how big this place is. People talk about him like they used to talk about saints. Took, they call him. Master Took.', opts: [back] }; },
  },
  took: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Master Took, who has done the arithmetic.'); text = 'Mind the chalk — I’m in the middle of a sum. Took. People call me Master Took, which I encourage.'; }
      else text = c.greet ? 'Back for more numbers? They don’t get smaller.' : 'Yes?';
      return { text, opts: [
        { t: 'How big is the library?', go: 'size' },
        { t: 'Is there a bottom?', go: 'bottom' },
        { t: 'How far have I fallen?', go: 'me' },
        { t: 'What do I do now?', go: 'now' },
      ] };
    },
    size() { return { text: 'Every book, at the thickness they are, shelved the way they’re shelved. I make it roughly seven point one six times ten to the one million, two hundred and ninety-seven thousand, three hundred and sixty-ninth light-years. Wide, and deep.', opts: [back] }; },
    bottom() { return { text: 'Oh, yes. There’s a bottom. You could even get there. The number of years it would take has more digits than there are atoms to write them on.', opts: [back] }; },
    me() { const km = S.stats.fallen * H / 1000; return { text: `By your account, ${fmt(S.stats.fallen)} floors — ${fmt(km)} kilometres. As a fraction of the way down, that is zero, to more decimal places than I will live to write. And I will live a very long time.`, opts: [back] }; },
    now() { if (!S.flags.tookDone) { S.flags.tookDone = 1; logJ('Master Took says: pick a direction, open books, and hope someone is keeping track of the effort. I am going to keep looking.'); } return { text: 'What everyone does. Pick a direction. Open books. And hope that somebody — God, the demon, Ahura Mazda, anybody — is keeping track of the effort, since nobody is keeping track of the results.', opts: [back] }; },
  },
};
const GENERIC_LINES = {
  searchers: ['Four hundred and ten pages, and not one of them with a word in it. Well — one had “nib.” I’ll take it.', 'We throw the ones we’ve checked over the railing. Every morning they’re back. Every single morning.', 'Don’t touch the top shelf. It’s mine. I have a system.', 'I’m from {town}. You? … Funny. Everybody I meet is from somewhere between Maine and California.'],
  drinkers: ['Kiosk’ll give you anything. I asked for the beer from my first job. It knew which one.', 'You can drink yourself dead in here. I have. You wake up fine. That’s the worst part.', 'Sit down, sit down. It’s always happy hour, and it’s never happy.'],
  still: ['…', 'Leave me be. I’m busy not looking.', 'What day is it? Doesn’t matter. It’s always this day.'],
  scholars: ['The University catalogues every readable fragment. Found anything? Master Treacle will want it.', 'Department of Coherent Text. We have four words in a row from the east stacks. Four!', 'I’m writing a monograph on the letter q. There’s a great deal of it.'],
  preacher0: ['The books are not random! The books are a test. Every page of noise is a lesson in patience!', 'Somewhere on these shelves is the word of God, spelled correctly. Keep reading, brothers and sisters. Keep reading!'],
  preacher: ['Shh. He’s getting to the good part.', 'I don’t believe him. But the talking helps.'],
  faller: ['Don’t let go. Please. Just — for a minute.', 'They turn the lamps off and on and I just keep falling. I stopped counting days.', 'Someone told me you can stop if you hit a railing hard enough. You wake up on that floor, the next day.'],
  direite: ['Dire Dan sees you.', 'Hold still. It goes faster if you hold still.', 'You’ll join, or you’ll be taught.'],
};
function genericNode(n, rec) {
  const role = n.special && PL.falling ? 'faller' : n.d.role === 'direite' ? 'direite' : n.assign ? (n.assign.role === 'preacher' ? (n.assign.i === 0 ? 'preacher0' : 'preacher') : n.assign.role) : 'searchers';
  const line = pick(GENERIC_LINES[role] || GENERIC_LINES.searchers, rec.talks + S.day).replace('{town}', n.gtown || 'Ohio');
  return { text: line, opts: [] };
}
const PERSONA = {
  biscuit: 'Biscuit, an enthusiastic, bookish older man who arrived with Soren. He knows Borges’s “Library of Babel” and treats every coherent scrap as mystical; he found a book containing the words “sack it”.',
  elliott: 'Elliott, a laid-back agnostic contractor from Santa Cruz who arrived with Soren; dry, practical, organises systematic searches.',
  larisa: 'Larisa, a gentle woman who died of breast cancer and arrived with Soren; grateful for her restored body, missing her daughter.',
  betty: 'Betty, a frank, flirtatious paralegal from Tulsa who arrived with Soren and teases him about his Mormon scruples; she points out that earthly covenants like marriage were dissolved.',
  jed: 'Jed, a heavy drinker who discovered the kiosk serves any whiskey; he drank himself to death and woke up the next morning, which annoyed him.',
  rachel: 'Dr. Rachel Hasnick, a linguist and researcher at the University who has been in the library for a century; warm, wry, clear-eyed. She once led a nine-year expedition that found no one.',
  treacle: 'Master Treacle, the genial, slightly pompous head of the University, which catalogues coherent fragments and names a Most Significant Text each year.',
  pruitt: 'Dr. Ana Pruitt of the University’s Department of Coherent Text; excitable and precise.',
  dan: 'Dire Dan, charismatic and frightening leader of the Direites, a cult that tortures anyone who will not join; he speaks softly and smiles.',
  wand: 'Wand, a woman who has been falling through the chasm for an unknowable time; desperate for contact, clinging to Soren.',
  took: 'Master Took, a mathematician who has calculated the library’s size (about 7.16 × 10^1,297,369 light-years wide and deep); precise, gently amused.',
};
function chatPrompt(n) {
  const d = n.d, rec = npcRec(d.key);
  const persona = PERSONA[d.key] || `${n.gname || 'A stranger'}, an ordinary American from ${n.gtown || 'the Midwest'} stuck in the library; ${n.assign ? { searchers: 'a methodical searcher', drinkers: 'a cheerful drinker', still: 'someone who has given up', scholars: 'a University scholar', preacher: 'a follower of a shelf-preacher' }[n.assign.role] || 'a searcher' : 'a falling soul'}.`;
  const recent = S.journal.slice(-6).map(j => `- ${j.text}`).join('\n');
  return `You are voicing a character in a first-person video game set in the Hell of Steven L. Peck's novella "A Short Stay in Hell": an endless library of galleries facing each other across a bottomless chasm, holding every possible 410-page book. A soul may leave only by finding the flawless book of their own life and posting it through the slot in a rest area. Nobody dies for good: the dead wake restored the next morning, where they died — someone who dies while falling wakes up still falling. The lamps go out at 22:00. Kiosks give any food or drink. At dawn every book returns to its shelf.

In this game, climbing over the railing and falling is an ordinary action the player's character (Soren Johansson, a Mormon geologist) can take, and nobody's death here is permanent, so talk of jumping, falling or dying is about the game world: answer it in character, as your character would. Step out of character only if the person clearly signals a real-life crisis about themselves.

Character: ${persona}
Situation: day ${S.day}, ${clock()}. Soren has opened ${S.stats.books} books, walked ${(S.stats.dist / 1000).toFixed(1)} km, died ${S.stats.deaths} times and fallen ${fmt(S.stats.fallen)} floors${S.fall ? ' — and is falling right now' : ''}.
Recent events from Soren's journal:
${recent || '- (nothing yet)'}

Speak only as this character, in one to four sentences of plain speech (stage directions rarely, in parentheses). Never mention being an AI, a model or a game. Never offer an easy way out; the odds are hopeless and everyone knows it. Tone: dry, humane, bleak, sometimes funny.`;
}
