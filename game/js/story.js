'use strict';
/* ==========================================================================
   The world's people and the things that can happen to you — by chance, as in the book
   ========================================================================== */
/* ---------- Places that matter. The rooms around your arrival are fixed; everything else is chance. ---------- */
const ARRIVAL = { cx: START_CX, cz: START_CZ, floor: START_FLOOR };
const JEDSITE = { cx: START_CX + 2, cz: START_CZ, floor: START_FLOOR };
const UNI = { cx: START_CX - 6, cz: START_CZ, floor: START_FLOOR - 3 };
const SACK = { f: START_FLOOR, x: START_CX + 1, z: START_CZ, k: 9, p: 12 };
SPECIAL.set(keyOf(SACK), { text: 'sack it', page: 188, at: 8 * COLS + 30 });
const MST_FIRST = 'and in the morning the river came back as if it had never been away';
{
  const SBX = fdiv(START_CX, 2), SBZ = fdiv(START_CZ, 2), SBL = fdiv(START_FLOOR, 2), lvOff = mod(START_FLOOR, 2);
  COLUMN_OVERRIDE.set(SBX + ':' + SBZ, null);
  PLAN_OVERRIDE.set(`${SBX}:${SBZ}:${SBL}`, {
    [lvOff]: put => { put('rest', 0, 0, lvOff, 0, 0); put('crossing', 1, 0, lvOff, 0, 0); put('poolhall', 0, 1, lvOff, 0, 0); },
    [1 - lvOff]: put => { put('pillars', 0, 0, 1 - lvOff, 0, 0); },
  });
  // a spiral tower just west of the arrival room, and a well past Jed's rest area
  COLUMN_OVERRIDE.set((SBX - 1) + ':' + SBZ, { type: 'tower', cell: [1, 0], rot: 0 });
  COLUMN_OVERRIDE.set((SBX + 1) + ':' + SBZ, { type: 'well', cell: [1, 1], rot: 0 });
  PLAN_OVERRIDE.set(`${SBX + 1}:${SBZ}:${SBL}`, { [lvOff]: put => { put('rest', 0, 0, lvOff, 1, 0); put('crossing', 1, 0, lvOff, 0, 0); put('crossing', 0, 1, lvOff, 2, 0); } });
  // the University keeps the great hall three floors down, six rooms west
  const UB = fdiv(UNI.cx, 2), UL = fdiv(UNI.floor, 2);
  COLUMN_OVERRIDE.set(UB + ':' + SBZ, null);
  PLAN_OVERRIDE.set(`${UB}:${SBZ}:${UL}`, { full: put => put('grand', 0, 0, 0, 0, 0) });
}

const MOMENTS = {
  arrival: { eyebrow: 'Year one · Day one', title: 'The First Week', art: 'ch1', text: 'You wake beside a small round pool, in a body that no longer hurts. Four strangers wake beside you. Beyond the arches: tile, water, shelves, and more arches, and more shelves, as far as anyone has walked.' },
  university: { eyebrow: 'Six rooms west, three floors down', title: 'The University', art: 'ch2', text: 'People who have been here for a century have made something out of it: a university, of all things, in a great hall of books — devoted to the rare sentence that means anything at all.' },
  direites: { eyebrow: 'They come through the arches', title: 'The Direites', art: 'ch3', text: 'Some people here decided that pain is the only thing in the library nobody wrote down first. They follow a man called Dire Dan. They are coming this way.' },
  abyss: { eyebrow: 'The lights went out. You kept falling.', title: 'The Deepest Abyss', art: 'ch4', text: 'The lights came back on and you are still falling. You can steer. You cannot stop — unless you hit a floor hard enough to kill you, and wake tomorrow wherever that was.' },
};
const placeIs = (pl, site) => pl && site && roomAt(site.cx, site.cz, site.floor) === pl;
const siteRoom = site => roomAt(site.cx, site.cz, site.floor);

/* ---------- Who lives where: every room's occupants are a pure function of its address ---------- */
const SITE_NAMES = ['Dale', 'Marcy', 'Tom', 'Jean', 'Rick', 'Barbara', 'Gary', 'Linda', 'Doug', 'Carol', 'Steve', 'Donna', 'Phil', 'Karen', 'Walt', 'Judy', 'Ray', 'Nancy', 'Earl', 'Peggy', 'Hank', 'Sheila', 'Lyle', 'Deb'];
const TOWNS = ['Dayton, Ohio', 'Provo, Utah', 'Tulsa', 'Fresno', 'outside Des Moines', 'Duluth', 'Bakersfield', 'Scranton', 'Boise', 'Mobile, Alabama', 'Spokane', 'Albany', 'Omaha', 'El Paso', 'Grand Rapids', 'Reno'];
function siteType(pl) {
  if (placeIs(pl, ARRIVAL)) return { type: 'arrival', n: 0 };
  if (placeIs(pl, JEDSITE)) return { type: 'jed', n: 0 };
  if (placeIs(pl, UNI)) return { type: 'university', n: 3 };
  if (COLUMN_ROOMS[pl.pf]) return null;
  const h = hashN(0x5173, pl.cx, pl.cz, pl.lv), r = (h % 1000) / 1000, k = h >>> 12;
  const pf = pfOf(pl), wet = pf && pf.meta.water.length;
  if (r < 0.52) return null;
  if (wet && r < 0.62) return { type: 'swimmers', n: 1 + k % 2 };
  if (r < 0.74) return { type: 'searchers', n: 1 + k % 3 };
  if (r < 0.81) return { type: 'drinkers', n: 1 + k % 2 };
  if (r < 0.87) return { type: 'still', n: 1 + k % 2 };
  if (r < 0.95) return { type: 'scholars', n: 2 + k % 2 };
  return { type: 'preacher', n: 3 };
}
const POOL = NPCS.filter(n => n.d.generic);
function occupantKey(pl, i) { return placeKey(pl) + '#' + i; }
function nearbyPlacements(R) {
  const out = new Map(), pcx = S.cx + Math.floor(S.x / RC), pcz = S.cz + Math.floor(S.z / RC);
  for (let dz = -R; dz <= R; dz++) for (let dx = -R; dx <= R; dx++) { const pl = roomAt(pcx + dx, pcz + dz, S.floor); if (pl) out.set(placeKey(pl), pl); }
  return [...out.values()];
}
function assignSites() {
  const want = new Map();
  if (!S.fall) for (const pl of nearbyPlacements(1)) {
    const t = siteType(pl); if (!t) continue;
    for (let i = 0; i < t.n; i++) { const key = occupantKey(pl, i); want.set(key, { key, pl, role: t.type === 'university' ? 'scholars' : t.type, i }); }
  }
  for (const n of POOL) if (n.assign && !want.has(n.assign.key) && !n.special) { n.assign = null; n.gone = true; }
  for (const n of POOL) if (n.assign) want.delete(n.assign.key);
  for (const w of want.values()) {
    const n = POOL.find(p => !p.assign && !p.special); if (!n) break;
    const h = strHash(w.key);
    n.assign = w; n.gone = false; n.t = 0; n.goalYaw = null; n.faceAt = null; n.stun = 0; n.pool = null; n.onBed = false;
    n.gname = SITE_NAMES[h % SITE_NAMES.length]; n.gtown = TOWNS[(h >>> 8) % TOWNS.length];
    n.home = w.pl; n.look = (h % 628) / 100;
    const g = schedule(n) || { mode: 'idle' };
    const at = g.x !== undefined ? g : (g.path && g.path.length ? g.path[g.path.length - 1] : localToAbs(w.pl, [RC / 2, 0, RC / 2]));
    placeNPC(n, at.x, at.y, at.z);
    n.mode = g.mode === 'bed' ? 'lie' : g.mode; n.t = g.dur || 20; n.goalYaw = g.yaw; n.faceAt = g.faceAt || null; n.lieYaw = (h % 628) / 100;
    if (g.mode === 'bed') n.onBed = !!g.onBed;
  }
}
/* a day in the life: read at the shelves, eat at the rest area at noon and in the evening, sleep at night */
function bedFor(n, home) {
  const beds = roomSpots(home, 'bed');
  if (beds.length) { const b = beds[strHash(n.d.key + (n.assign ? n.assign.key : '')) % beds.length]; return { mode: 'bed', x: b.x, y: b.y, z: b.z, onBed: true, dur: 60 }; }
  const pf = pfOf(home), nav = pf ? pf.meta.nav : [];
  const p = nav.length ? localToAbs(home, nav[strHash(n.d.key + 'bed') % nav.length]) : localToAbs(home, [RC / 2, 0, RC / 2]);
  return { mode: 'bed', x: p.x + ((strHash(n.d.key) % 100) / 100 - 0.5), y: p.y, z: p.z, dur: 60 };
}
function dailyRound(n, home, activity) {
  const t = S.time;
  if (t >= 21.5 || t < 6.1) return bedFor(n, home);
  if ((t >= 12 && t < 13) || (t >= 19 && t < 21.5)) {
    const seats = roomSpots(home, 'sit').concat(roomSpots(home, 'read'));
    if (seats.length) { const s = seats[strHash(n.d.key + S.day) % seats.length]; return { mode: 'sit', x: s.x, y: s.y, z: s.z, yaw: s.yaw, dur: 60 }; }
  }
  const pf = pfOf(home);
  if (pf && Math.random() < 0.25 && pf.meta.nav.length) {
    const to = Math.floor(Math.random() * pf.meta.nav.length);
    return { mode: 'idle', path: navPath(home, n.ax, n.az, to), dur: 8 + Math.random() * 10 };
  }
  const r = readSpot(home, Math.floor(Math.random() * 1e6));
  if (!r) return { mode: 'idle', dur: 20 };
  const to = nearestNode(home, r.x, r.z), path = to >= 0 ? navPath(home, n.ax, n.az, to) : [];
  path.push({ x: r.x, y: r.y, z: r.z });
  return { mode: activity || 'read', path, yaw: r.yaw, dur: 20 + Math.random() * 35 };
}
function schedule(n) {
  const t = S.time, role = n.d.role, rec = npcRec(n.d.key);
  if (n.d.generic) {
    if (!n.assign) return null;
    const a = n.assign, home = n.home;
    switch (a.role) {
      case 'drinkers': {
        if (t >= 21.5 || t < 6.1) return dailyRound(n, home);
        const seats = roomSpots(home, 'sit').concat(roomSpots(home, 'read'));
        const s = seats.length ? seats[strHash(a.key) % seats.length] : localToAbs(home, [RC / 2, 0, RC / 2]);
        return { mode: seats.length ? 'sit' : 'drink', x: s.x, y: s.y, z: s.z, yaw: s.yaw, dur: 90 };
      }
      case 'still': { const pf = pfOf(home), nav = pf ? pf.meta.nav : []; const p = nav.length ? localToAbs(home, nav[strHash(a.key) % nav.length]) : localToAbs(home, [RC / 2, 0, RC / 2]); return { mode: 'lie', x: p.x + 0.4, y: p.y, z: p.z - 0.3, dur: 999 }; }
      case 'swimmers': {
        if (t >= 21.5 || t < 6.1) return dailyRound(n, home);
        const pf = pfOf(home), w = pf && pf.meta.water[strHash(a.key) % Math.max(1, pf.meta.water.length)];
        if (!w) return dailyRound(n, home);
        const c = w.r !== undefined ? [w.cx, w.top, w.cz] : [(w.x0 + w.x1) / 2, w.top, (w.z0 + w.z1) / 2];
        const r = w.r !== undefined ? w.r * 0.7 : Math.min(w.x1 - w.x0, w.z1 - w.z0) * 0.35;
        const p = localToAbs(home, c);
        n.pool = { x: p.x, z: p.z, r, top: p.y };
        return { mode: 'swim', x: p.x + (strHash(a.key) % 100 / 100 - 0.5) * r, y: p.y - 1.3, z: p.z, dur: 999 };
      }
      case 'preacher': {
        if (t >= 21.5 || t < 6.1) return dailyRound(n, home);
        const c = localToAbs(home, [RC / 2 + 1.2, 0, RC / 2 + 3.6]);
        if (a.i === 0) return { mode: 'preach', x: c.x, y: c.y, z: c.z, dur: 60 };
        return { mode: 'stand', x: c.x + Math.cos(a.i * 2) * 2.2, y: c.y, z: c.z + Math.sin(a.i * 2) * 2.2, dur: 60, faceAt: { x: c.x, z: c.z } };
      }
      default: return dailyRound(n, home);
    }
  }
  switch (role) {
    case 'companion': case 'scholar': return dailyRound(n, n.home);
    case 'drinker': {
      const seats = roomSpots(n.home, 'sit'), s = seats[1] || seats[0] || localToAbs(n.home, [8, 0, 8]);
      if (S.flags.jedDead) return { mode: 'dead', x: s.x, y: s.y, z: s.z, dur: 999 };
      if (t >= 21.5 || t < 6.1) return dailyRound(n, n.home);
      return { mode: 'drink', x: s.x, y: s.y, z: s.z, yaw: s.yaw, dur: 90 };
    }
    case 'rachel':
      if (rec.following) return null;
      return dailyRound(n, n.home);
    case 'master': {
      if (t >= 21.5 || t < 6.1) return dailyRound(n, n.home);
      const p = localToAbs(n.home, [16, 0, 10.6]);
      return { mode: 'stand', x: p.x, y: p.y, z: p.z, dur: 40, faceAt: localToAbs(n.home, [16, 0, 6]) };
    }
    case 'took': { const seats = roomSpots(n.home, 'sit').concat(roomSpots(n.home, 'read')); const s = seats[0] || localToAbs(n.home, [8, 0, 8]); return { mode: 'sit', x: s.x, y: s.y, z: s.z, yaw: s.yaw, dur: 999 }; }
  }
  return null;
}
function placeNamed() {
  const at = (k, site, local, mode) => {
    const n = NPC_BY[k], pl = siteRoom(site); if (!pl) { n.gone = true; return; }
    const p = localToAbs(pl, local); n.home = pl; placeNPC(n, p.x, p.y, p.z); n.gone = false; n.mode = mode || 'idle'; n.t = 0; n.stun = 0; n.special = false; n.goalYaw = null; n.faceAt = null; n.onBed = false;
  };
  at('biscuit', ARRIVAL, [6.0, 0, 5.9]); at('elliott', ARRIVAL, [10.3, 0, 6.4]); at('larisa', ARRIVAL, [5.8, 0, 10.2]); at('betty', ARRIVAL, [10.1, 0, 10.4]);
  at('jed', JEDSITE, [10.4, 0, 10.4], S.flags.jedDead ? 'dead' : 'idle');
  if (!S.flags.rachelGone) {
    if (npcRec('rachel').following) { const n = NPC_BY.rachel, b = behindYou(1.2); n.home = siteRoom(UNI); placeNPC(n, b.x, absY(), b.z); n.gone = false; n.mode = 'follow'; }
    else at('rachel', UNI, [6.8, 0, 16.5]);
  } else NPC_BY.rachel.gone = true;
  at('treacle', UNI, [16, 0, 10.6]); at('pruitt', UNI, [25.5, 0, 16.0]);
  for (const k of ['dan', 'dir1', 'dir2', 'dir3', 'dir4', 'wand']) { NPC_BY[k].gone = true; NPC_BY[k].mode = 'idle'; }
  const tk = NPC_BY.took; if (S.flags.tookSite) at('took', S.flags.tookSite, [8, 0, 8], 'sit'); else tk.gone = true;
  for (const n of POOL) { n.assign = null; n.gone = true; n.special = false; }
  RAID.on = false; FALLER.n = null;
  assignSites();
}

/* ---------- Things that happen ---------- */
const RAID = { on: false, cool: 60, t: 0, floor: 0, lostT: 0, cornerTried: false };
const FALLER = { n: null, t: 0, state: '', cool: 30 };
let passCool = 20, throwCool = 10, storyT = 0, ceremony = null;
function inRoom(site) { return PL.room && roomAt(site.cx, site.cz, site.floor) === PL.room.pl && S.floor >= site.floor && S.floor < site.floor + footprint(PL.room.pl)[2]; }
function freePool() { return POOL.find(p => !p.assign && !p.special); }
/* the doorways of the room you are in, as absolute points just inside them */
function roomDoors(pl) {
  const f = footprint(pl), out = [];
  for (let i = 0; i < f[0]; i++) { out.push({ x: (pl.cx + i) * RC + RC / 2, z: pl.cz * RC + 1.2 }); out.push({ x: (pl.cx + i) * RC + RC / 2, z: (pl.cz + f[1]) * RC - 1.2 }); }
  for (let j = 0; j < f[1]; j++) { out.push({ x: pl.cx * RC + 1.2, z: (pl.cz + j) * RC + RC / 2 }); out.push({ x: (pl.cx + f[0]) * RC - 1.2, z: (pl.cz + j) * RC + RC / 2 }); }
  return out;
}
function startRaid() {
  if (!PL.room) return;
  const band = ['dir1', 'dir2', 'dir3', 'dir4'].slice(0, 2 + Math.floor(Math.random() * 3));
  if (!S.flags.danFallen && Math.random() < 0.75) band.push('dan');
  const doors = roomDoors(PL.room.pl).sort((a, b) => Math.hypot(b.x - absX(), b.z - absZ()) - Math.hypot(a.x - absX(), a.z - absZ()));
  const door = doors[0];
  band.forEach((k, i) => {
    const n = NPC_BY[k];
    placeNPC(n, door.x + (i % 3 - 1) * 0.8, absY(), door.z + (Math.floor(i / 3) - 0.5) * 0.8);
    n.gone = false; n.mode = 'raid'; n.t = 999; n.path = []; n.chaseSpeed = k === 'dan' ? 4.2 : 4.6; n.special = true; n.stun = 0; n.stuck = 0; n.lostT = 0;
  });
  RAID.on = true; RAID.seenYou = 0; RAID.t = 0; RAID.floor = S.floor; RAID.lostT = 0; RAID.cornerTried = false; RAID.band = band;
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
  if (S.floor !== RAID.floor || S.fall) RAID.lostT += dt; else RAID.lostT = 0;
  if (RAID.lostT > 12) { endRaid(); toast('The Direites have lost you.'); return; }
  let nearest = Infinity;
  for (const n of band) {
    const d = npcDist(n); nearest = Math.min(nearest, d);
    if (n.mode === 'raid') { n.mode = 'chase'; if (!RAID.seenYou) { RAID.seenYou = 1; toast('They have seen you.', true); } }
  }
  if (RAID.t > 240) { endRaid(); toast('The Direites drift away, looking for someone else.'); return; }
  const r = NPC_BY.rachel, sh = shaftNear();
  if (!RAID.cornerTried && npcRec('rachel').following && !r.gone && nearest < 7 && sh && sh.d < 2) {
    RAID.cornerTried = true;
    if (Math.random() < 0.5) greatLoss(sh);
  }
}
function greatLoss(sh) {
  const r = NPC_BY.rachel, band = RAID.band.map(k => NPC_BY[k]);
  band.forEach(n => { if (n.mode === 'chase') { n.mode = 'script'; n.walking = false; } });
  r.mode = 'script'; npcRec('rachel').following = false;
  showCaptions([
    { who: '', text: 'They come from both sides now, walking, not running. There is nowhere left to go.' },
    { who: 'Rachel', text: '(She looks at you — calm, almost smiling — and tells you that she loves you.)' },
    { who: '', text: 'Then she climbs the parapet, and lets go.', fx: () => { const p = localToAbs(sh.room.pl, [sh.cx, 1.0, sh.cz]); placeNPC(r, p.x, absY() + 1, p.z); r.mode = 'fall'; r.vy = 0; r.vz = 0; r.vx = 0; r.special = true; setTimeout(() => { r.gone = true; }, 5000); SFX.scream && SFX.scream(); } },
  ], () => { band.forEach(n => { if (n.mode === 'script') n.mode = 'chase'; }); });
  S.flags.rachelGone = 1; logJ('Rachel went over the parapet to get away from them. I watched her fall until the dark had her.');
}
function tackleDan() {
  const d = NPC_BY.dan;
  logJ('Tackled Dire Dan over the parapet. We went down together.');
  S.flags.danFallen = 1; S.flags.danWith = 1; S.flags.danHitT = 1.5;
  startFall(true, true);
  d.mode = 'fallWith'; d.off = { x: 0.55, y: 0.1, z: 0.35 }; d.special = true; d.gone = false;
  for (const k of RAID.band) if (k !== 'dan') { NPC_BY[k].mode = 'script'; }
  setTimeout(() => endRaid(), 2500);
  toast('He is clawing at you, screaming that he will kill you. Shove him away (F) — or don’t.', true);
}
function shoveInFall(n) {
  if (n.d.key === 'dan') { S.flags.danWith = 0; n.mode = 'fall'; n.vx = (Math.random() - 0.5) * 2; n.vz = (Math.random() - 0.5) * 2; n.extraFall = 5; setTimeout(() => { n.gone = true; n.special = false; }, 9000); toast('You kick free. He falls away from you, still screaming.'); SFX.hit(); }
  else if (FALLER.n === n) { letGoFaller(true); }
}
function shaftCentreAbs() {
  const sh = shaftNear(); if (!sh) return null;
  const p = localToAbs(sh.room.pl, [sh.cx, 0, sh.cz]);
  return { x: p.x, z: p.z, r: sh.room.pf.meta.meta.core ? 1.2 : 2.6 };
}
function spawnPassingFaller() {
  const c = shaftCentreAbs(); if (!c) return;
  const n = freePool(); if (!n) return;
  n.special = true; n.gone = false;
  placeNPC(n, c.x + (Math.random() - 0.5) * c.r, absY() + 20 + Math.random() * 14, c.z + (Math.random() - 0.5) * c.r);
  n.mode = 'fall'; n.vy = -30; n.vx = 0; n.vz = 0; n.extraFall = PL.falling ? 8 : 0;
  SFX.scream && SFX.scream();
  setTimeout(() => { n.special = false; n.gone = true; n.mode = 'idle'; }, 7000);
}
function spawnCatchable() {
  const wand = !S.flags.wandMet && S.fall && (S.fall.days >= 1 || S.fall.t > 120);
  const n = wand ? NPC_BY.wand : freePool(); if (!n) return;
  n.special = true; n.gone = false; n.mode = 'fall'; n.vx = 0; n.vz = 0; n.vy = PL.vy; n.extraFall = 1.6;
  placeNPC(n, absX() + (Math.random() < 0.5 ? -1.6 : 1.6), absY() + 34, absZ() + (Math.random() - 0.5) * 2);
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
  n.mode = 'fall'; n.extraFall = 0; n.vx = (Math.random() - 0.5) * 2.5; n.vz = (Math.random() - 0.5) * 2.5; FALLER.state = 'leaving'; n.fallT = 4;
  n.onImpact = () => { n.gone = true; n.special = false; if (FALLER.n === n) FALLER.n = null; toast(`${n.d.key === 'wand' ? 'Wand' : 'They'} hit${n.d.key === 'wand' ? 's' : ''} the edge of a floor rushing past — and ${n.d.key === 'wand' ? 'is' : 'are'} gone. You never find out which floor.`); if (n.d.key === 'wand') { S.flags.wandLanded = 1; logJ('Wand let go and steered for a floor. She made it, I think. I never found her again.'); } };
  toast(pushed ? 'You let go.' : (n.d.key === 'wand' ? 'Wand squeezes your hand once — and lets go, steering for the edge.' : 'They let go, and steer for the edge.'));
}
function updateFaller(dt) {
  const n = FALLER.n; if (!n) return;
  FALLER.t += dt;
  if (FALLER.state === 'approach') {
    const dy = n.ay - absY();
    if (dy < 2.5) { n.extraFall = 0; n.vy = PL.vy; FALLER.state = 'near'; FALLER.t = 0; n.mode = 'fallWith'; n.off = { x: n.ax - absX(), y: 0.3, z: n.az - absZ() }; }
    if (!PL.falling) { n.gone = true; n.special = false; FALLER.n = null; }
  } else if (FALLER.state === 'near') {
    n.off.x *= Math.pow(0.6, dt); n.off.z *= Math.pow(0.6, dt); n.off.x = Math.sign(n.off.x || 1) * Math.max(Math.abs(n.off.x), 1.0);
    if (FALLER.t > 14) { toast('You were too slow. They drift away below you.'); n.mode = 'fall'; n.extraFall = 3; FALLER.state = 'leaving'; setTimeout(() => { n.gone = true; n.special = false; if (FALLER.n === n) FALLER.n = null; }, 8000); }
  } else if (FALLER.state === 'held') {
    const talked = npcRec(n.d.key).talks > 0 && MODE === 'play';
    if (talked && FALLER.t > (n.d.key === 'wand' ? 80 : 50)) letGoFaller(false);
  }
  if (!PL.falling && FALLER.state !== 'leaving') { n.gone = true; n.special = false; FALLER.n = null; }
}
function startCeremony() {
  ceremony = { day: S.day };
  const text = S.flags.mstDone ? FRAGMENTS[strHash('mst' + S.day) % FRAGMENTS.length] : MST_FIRST;
  const T = NPC_BY.treacle, R = NPC_BY.rachel, home = siteRoom(UNI);
  const podium = localToAbs(home, [16, 0, 10.6]), look = localToAbs(home, [16, 0, 6]);
  for (const n of [NPC_BY.pruitt, ...POOL.filter(p => p.assign && p.assign.pl === home)]) { n.mode = 'stand'; n.t = 400; n.faceAt = podium; const q = localToAbs(home, [12 + Math.random() * 8, 0, 7.3 + Math.random() * 2.1]); n.path = [q]; }
  T.mode = 'speak'; T.t = 400; T.path = [podium]; T.faceAt = look;
  const lines = [
    { who: 'Master Treacle', text: 'Friends. Colleagues. Another year of honest work among the shelves.' },
    { who: 'Master Treacle', text: 'The catalogue now holds four thousand one hundred and twelve coherent fragments of three words or more. Out of — well. Out of all of it.' },
  ];
  const mine = S.frags.find(f => f.uni);
  if (mine) lines.push({ who: 'Master Treacle', text: `An honourable mention, this year, to Soren Johansson, for “${mine.text}”.` });
  if (!S.flags.rachelGone && !npcRec('rachel').following) { R.mode = 'speak'; R.t = 400; R.path = [localToAbs(home, [17.3, 0, 10.4])]; R.faceAt = look; lines.push({ who: 'Master Treacle', text: 'By vote of the faculty, the Most Significant Text of the year — read for us by Dr. Rachel Hasnick.' }); lines.push({ who: 'Rachel Hasnick', text: `“${text}.”` }); }
  else lines.push({ who: 'Master Treacle', text: `The Most Significant Text of the year: “${text}.”` });
  lines.push({ who: '', text: '(A murmur. Someone weeps quietly. Someone else insists the second word is a typo.)' });
  lines.push({ who: 'Master Treacle', text: 'Thank you all. Discussion continues at the pool, as usual.' });
  showCaptions(lines, () => {
    S.flags.mstDone = 1; S.flags.mstDay = S.day; logJ(`Heard the University read its Most Significant Text: “${text}.”`);
    for (const n of [T, R, NPC_BY.pruitt, ...POOL]) if (n.mode === 'stand' || n.mode === 'speak') { n.mode = 'idle'; n.t = 0; n.faceAt = null; }
    ceremony = null;
  });
}
function storyTick(dt) {
  storyT += dt; updateRaid(dt); updateFaller(dt);
  if (storyT < 1) return; const sec = storyT; storyT = 0;
  if (!S.fall) assignSites();
  // Jed drinks himself to death on the second night, and is back the next morning
  if (S.day >= 2 && S.time >= 20.5 && !S.flags.jedDeadDone) { S.flags.jedDeadDone = 1; S.flags.jedDead = 1; const j = NPC_BY.jed; j.mode = 'dead'; j.path = []; j.lieYaw = 0.4; if (Math.abs(absX() - (JEDSITE.cx * RC + 8)) < 50 && S.floor === JEDSITE.floor) toast('Over at Jed’s table, somebody stops talking mid-sentence.'); }
  // the University
  if (!S.flags.uniFound && inRoom(UNI)) { S.flags.uniFound = 1; S.flags.uniHeard = 1; showMoment('university'); logJ('Found the University: six rooms west, three floors down, in a great hall of books, as Larisa said.'); }
  if (!ceremony && S.time >= 19 && S.time < 20.5 && inRoom(UNI) && S.flags.mstDay !== S.day && (!S.flags.mstDone || S.day % 3 === 0)) startCeremony();
  // Rachel walking with you
  const rr = npcRec('rachel'); if (rr.following && !S.flags.rachelWalked) { S.flags.rwT = (S.flags.rwT || 0) + sec; if (S.flags.rwT > 60) { S.flags.rachelWalked = 1; rr.aff += 1; logJ('Walked a long way with Rachel. We talked about everything, and then about everything again.'); } }
  // raids
  RAID.cool -= sec;
  if (!RAID.on && !S.fall && !PL.dead && S.day >= 2 && S.time > 8 && S.time < 21 && RAID.cool <= 0 && MODE === 'play' && Math.random() < sec / (S.day >= 3 ? 420 : 900)) startRaid();
  // people falling down the shaft beside you, and people you can catch in the fall
  passCool -= sec; FALLER.cool -= sec;
  const sh = !S.fall && shaftNear(), atEdge = sh && !sh.inside && sh.d < 4;
  if ((atEdge || S.fall) && passCool <= 0 && Math.random() < sec / (S.fall ? 50 : 30)) { passCool = 25; if (S.fall) { const n = freePool(); if (n) { n.special = true; n.gone = false; placeNPC(n, absX() + (Math.random() - 0.5) * 3, absY() + 30, absZ() + (Math.random() - 0.5) * 3); n.mode = 'fall'; n.vy = -30; n.extraFall = 8; setTimeout(() => { n.special = false; n.gone = true; n.mode = 'idle'; }, 7000); } } else spawnPassingFaller(); }
  if (S.fall && !FALLER.n && FALLER.cool <= 0 && PL.falling && !PL.dead) {
    const wand = !S.flags.wandMet && (S.fall.days >= 1 || S.fall.t > 120);
    if (Math.random() < sec / (wand ? 25 : 150)) { FALLER.cool = 90; spawnCatchable(); }
  }
  // searchers dropping checked books down the well
  throwCool -= sec;
  if (throwCool <= 0 && atEdge && S.time > 8 && S.time < 21) {
    const c = shaftCentreAbs();
    if (c && Math.random() < 0.35) { throwCool = 14; const id = { f: S.floor, x: S.cx, z: S.cz, k: Math.floor(Math.random() * 40), p: Math.floor(Math.random() * 40) }; throwBookVisual(id, c.x - S.cx * RC + (Math.random() - 0.5) * 2, S.y + 8 + Math.random() * 6, c.z - S.cz * RC + (Math.random() - 0.5) * 2, 0, 0); }
    else throwCool = 6;
  }
  // the falling Dan fight
  if (S.flags.danWith && PL.falling && !PL.dead) { S.flags.danHitT -= sec; if (S.flags.danHitT <= 0) { S.flags.danHitT = 1.5; hurt(11, 'Dire Dan'); } }
  updateThreadsHUD();
}
function storyDawn() {
  if (S.flags.jedDead) { S.flags.jedDead = 0; S.flags.jedRevived = 1; }
  S.flags.danWith = 0;
  placeNamed();
  if (S.fall && FALLER.n) FALLER.n = null;
}
function storyEvent(type, data) {
  if (type === 'landed') {
    const fallen = data.fallen || 0;
    if ((!S.flags.tookSite && fallen >= 50000) || (S.flags.tookSite && npcRec('took').met && Math.random() < 0.2 && fallen >= 50000)) {
      S.flags.tookSite = { cx: S.cx + Math.floor(S.x / RC), cz: S.cz + Math.floor(S.z / RC), floor: S.floor }; S.flags.tookHeard = 1;
    }
    S.flags.landed = 1;
  }
}
function onNpcHit(n) {
  if (n.d.role === 'direite' || n.d.role === 'dan') { hurt(24, n.d.role === 'dan' ? 'Dire Dan' : 'the Direites'); if (PL.dead) endRaid(); }
}
function storyTargets() {
  const dan = NPC_BY.dan, sh = shaftNear();
  if (RAID.on && !dan.gone && dan.mode !== 'fall' && dan.mode !== 'fallWith' && npcDist(dan) < 2.4 && sh && !sh.inside && sh.d < 1.6) return { kind: 'tackle', n: dan };
  if (FALLER.n && FALLER.state === 'near' && PL.falling) return { kind: 'catch', n: FALLER.n };
  return null;
}

/* ---------- Threads: what you have heard, what you might do ---------- */
const THREADS = [
  { id: 'meet', text: () => 'Talk to the four who arrived with you', show: () => true, done: () => ['biscuit', 'elliott', 'larisa', 'betty'].every(k => npcRec(k).met) },
  { id: 'kiosk', text: () => 'See what the kiosk will give you', show: () => true, done: () => S.flags.usedKiosk },
  { id: 'sack', text: () => `Biscuit’s book: floor ${fmt(SACK.f)}, the domed room next door (${roomName(SACK.x, SACK.z)}), shelf ${SACK.k + 1}, book ${SACK.p + 1} — page 189`, show: () => S.flags.sackTold, done: () => S.flags.sackFound },
  { id: 'throw', text: () => 'Elliott wants searched books dropped down a well (G at the parapet)', show: () => S.flags.elliottPlan, done: () => S.stats.thrown > 0 },
  { id: 'reset', text: () => 'See what dawn does to the books you dropped', show: () => S.stats.thrown > 0, done: () => S.flags.sawReset },
  { id: 'jed', text: () => 'Jed is drinking at the rest area two rooms east', show: () => S.flags.jedHeard || npcRec('jed').met, done: () => S.flags.jedBack },
  { id: 'uni', text: () => 'A university, they say: six rooms west, three floors down (the spiral tower is next door, to the west)', show: () => S.flags.uniHeard, done: () => S.flags.uniFound },
  { id: 'mst', text: () => 'The University reads its Most Significant Text at 19:00', show: () => S.flags.uniFound, done: () => S.flags.mstDone },
  { id: 'frag', text: () => 'Bring Master Treacle a readable fragment', show: () => S.flags.uniFound, done: () => S.flags.uniFrag },
  { id: 'rachel', text: () => 'Walk with Rachel Hasnick', show: () => npcRec('rachel').met && !S.flags.rachelGone, done: () => S.flags.rachelWalked },
  { id: 'direites', text: () => 'The Direites raid these floors. Run — or meet Dire Dan at a parapet.', show: () => S.flags.raidSeen, done: () => S.flags.danFallen },
  { id: 'stacks', text: () => 'While falling, steer into a floor: you’ll wake tomorrow where you hit', show: () => S.flags.fallHint || S.fall, done: () => S.flags.landed },
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
    sack() { S.flags.sackTold = 1; logJ(`Biscuit found two readable words: “sack it.” The domed room next door, shelf ${SACK.k + 1}, book ${SACK.p + 1}, page 189.`); return { text: `The room with the dome, right next door. Shelf ${SACK.k + 1} — in one of the niches — book ${SACK.p + 1}. Page one hundred and eighty-nine. Two words, all by themselves: “sack it.” Go and look. Go on.`, opts: [{ t: 'What does it mean?', go: 'mean' }] }; },
    mean() { return { text: "“Sack it.” Give it up? Or — put it in a sack. Carry it. Carry what? The search? Ourselves? It's a message, Soren. It has to be. Nothing else in here has two words in a row.", opts: [back] }; },
    plan() { return { text: 'Elliott has a plan. Elliott always has a plan. I prefer reading.', opts: [back] }; },
  },
  elliott: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Elliott, an agnostic from California.'); text = "Elliott. Santa Cruz, originally. Agnostic — which I'm now told was the wrong call, though so was everybody's. Nice to meet you, fellow wrong person."; }
      else if (c.greet && S.flags.sawReset) text = "They came back. Every book we dropped. Right where they were, this morning. Okay. So that's how it's going to be.";
      else if (c.greet) text = S.flags.elliottPlan ? 'How many have you checked? Drop them down the well when you’re done — then we know.' : 'We need a system. Otherwise we’re just browsing forever.';
      else text = 'Anything else?';
      return { text, opts: [
        { t: 'What do we do?', go: 'plan', if: !S.flags.elliottPlan },
        { t: 'Do you think we’ll find them?', go: 'find' },
        { t: 'What did you do, before?', go: 'before' },
      ] };
    },
    plan() { S.flags.elliottPlan = 1; logJ('Elliott’s plan: every book we search goes down the well, so we never check it twice.'); return { text: "We get systematic. Each of us takes a shelf. Anything we've searched goes down the well past Jed's place — that way we never check the same book twice. Simple.", opts: [back] }; },
    find() { return { text: 'Our books? Do the math with Biscuit sometime. Actually — don’t. Some numbers you can’t un-know.', opts: [back] }; },
    before() { return { text: 'Contractor. Decks, mostly. I’d have given a lot to build something in here that stayed built overnight.', opts: [back] }; },
  },
  larisa: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Larisa. Breast cancer, the long kind. She keeps taking deep breaths just to feel them.'); text = "Larisa. The last thing I remember is the hospital. Breast cancer — the long kind. And now look. I can breathe all the way to the bottom. I keep doing it just to feel it."; }
      else if (c.greet) text = S.flags.uniHeard ? 'Did you go and find the University yet? Six rooms west, three floors down. Take the spiral next door.' : 'I heard something interesting yesterday.';
      else text = 'Yes?';
      return { text, opts: [
        { t: 'Who do you miss?', go: 'miss' },
        { t: 'What did you hear?', go: 'rumour', if: !S.flags.uniHeard },
        { t: 'Are you all right?', go: 'ok' },
      ] };
    },
    miss() { return { text: 'My daughter. She was nine. She’s — I don’t know what she is now. Grown. Old. Gone. Nobody tells you what time it is up there.', opts: [back] }; },
    rumour() { S.flags.uniHeard = 1; logJ('Larisa heard of a university — six rooms west, three floors down, in a great hall.'); return { text: 'A man came through — said there’s a university, of all things. Six rooms west, three floors down, in a hall so tall it has its own weather. The spiral tower next door goes down. People who’ve been here a hundred years, studying the books like scripture.', opts: [back] }; },
    ok() { return { text: 'I’m dead, Soren. I’m the best I’ve been in years.', opts: [back] }; },
  },
  betty: {
    root(c) {
      const m = c.rec; let text;
      if (c.greet && !m.met) { m.met = true; logJ('Met Betty, who doesn’t think much of my homework.'); text = "Betty. You’re the Mormon, aren’t you? You’ve got the look — like you’re waiting for somebody to come and grade your homework."; }
      else if (c.greet) text = m.aff >= 3 ? 'Sit with me by the pool tonight, when the lights go out. It glows. It’s the only thing in here that looks like it’s alive.' : 'Still behaving yourself?';
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
    stop() { S.flags.fallHint = 1; return { text: 'Someone told me — a thousand years ago, maybe — if you steer into a floor hard enough, you die, and you wake up there. I’ve never had the nerve. Maybe now I do.', opts: [back] }; },
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
  searchers: ['Four hundred and ten pages, and not one of them with a word in it. Well — one had “nib.” I’ll take it.', 'We drop the ones we’ve checked down the well. Every morning they’re back. Every single morning.', 'Don’t touch the top shelf. It’s mine. I have a system.', 'I’m from {town}. You? … Funny. Everybody I meet is from somewhere between Maine and California.'],
  drinkers: ['Kiosk’ll give you anything. I asked for the beer from my first job. It knew which one.', 'You can drink yourself dead in here. I have. You wake up fine. That’s the worst part.', 'Sit down, sit down. It’s always happy hour, and it’s never happy.'],
  still: ['…', 'Leave me be. I’m busy not looking.', 'What day is it? Doesn’t matter. It’s always this day.'],
  scholars: ['The University catalogues every readable fragment. Found anything? Master Treacle will want it.', 'Department of Coherent Text. We have four words in a row from the east stacks. Four!', 'I’m writing a monograph on the letter q. There’s a great deal of it.'],
  preacher0: ['The books are not random! The books are a test. Every page of noise is a lesson in patience!', 'Somewhere on these shelves is the word of God, spelled correctly. Keep reading, brothers and sisters. Keep reading!'],
  preacher: ['Shh. He’s getting to the good part.', 'I don’t believe him. But the talking helps.'],
  faller: ['Don’t let go. Please. Just — for a minute.', 'They turn the lights off and on and I just keep falling. I stopped counting days.', 'Someone told me you can stop if you hit a floor hard enough. You wake up there, the next day.'],
  swimmers: ['It’s the only thing that feels like before. Floating. Nobody can hand you a book in here.', 'Come in. It’s always the right temperature. It’s always the right everything.', 'I’ve counted the tiles on the bottom. Four thousand and six. Don’t check.'],
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
  wand: 'Wand, a woman who has been falling down one of the wells for an unknowable time; desperate for contact, clinging to Soren.',
  took: 'Master Took, a mathematician who has calculated the library’s size (about 7.16 × 10^1,297,369 light-years wide and deep); precise, gently amused.',
};
function chatPrompt(n) {
  const d = n.d, rec = npcRec(d.key);
  const persona = PERSONA[d.key] || `${n.gname || 'A stranger'}, an ordinary American from ${n.gtown || 'the Midwest'} stuck in the library; ${n.assign ? { searchers: 'a methodical searcher', drinkers: 'a cheerful drinker', still: 'someone who has given up', scholars: 'a University scholar', preacher: 'a follower of a shelf-preacher' }[n.assign.role] || 'a searcher' : 'a falling soul'}.`;
  const recent = S.journal.slice(-6).map(j => `- ${j.text}`).join('\n');
  return `You are voicing a character in a first-person video game set in the Hell of Steven L. Peck's novella "A Short Stay in Hell": an endless library holding every possible 410-page book. In this game the library is dreamlike: endless tiled rooms with still pools, vaulted halls, a yellow maze like the backrooms, spiral towers, and square wells that drop through every floor. A soul may leave only by finding the flawless book of their own life and posting it through the slot in a rest area. Nobody dies for good: the dead wake restored the next morning, where they died — someone who dies while falling wakes up still falling. The lights go out at 22:00; only the pools keep glowing. Kiosks give any food or drink. At dawn every book returns to its shelf.

In this game, climbing over a parapet into a well and falling is an ordinary action the player's character (Soren Johansson, a Mormon geologist) can take, and nobody's death here is permanent, so talk of jumping, falling or dying is about the game world: answer it in character, as your character would. Step out of character only if the person clearly signals a real-life crisis about themselves.

Character: ${persona}
Situation: day ${S.day}, ${clock()}. Soren has opened ${S.stats.books} books, walked ${(S.stats.dist / 1000).toFixed(1)} km, died ${S.stats.deaths} times and fallen ${fmt(S.stats.fallen)} floors${S.fall ? ' — and is falling right now' : ''}.
Recent events from Soren's journal:
${recent || '- (nothing yet)'}

Speak only as this character, in one to four sentences of plain speech (stage directions rarely, in parentheses). Never mention being an AI, a model or a game. Never offer an easy way out; the odds are hopeless and everyone knows it. Tone: dry, humane, bleak, sometimes funny.`;
}
