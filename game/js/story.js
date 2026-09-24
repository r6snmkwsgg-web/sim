'use strict';
/* ==========================================================================
   Presence: you are alone in the library, almost. Nobody to talk to; only the
   traces of other people. Footsteps and a cough a few rooms away. A book left
   open, a chair pulled out, a lamp still warm. Notes in the margins. And, very
   rarely, someone at the far end of a long room who is gone when you get there.
   ========================================================================== */

/* ---------- The rooms round your arrival are fixed; everything else is chance ---------- */
{
  const SBX = fdiv(START_CX, 2), SBZ = fdiv(START_CZ, 2), SBL = fdiv(START_FLOOR, 2), lvOff = mod(START_FLOOR, 2);
  COLUMN_OVERRIDE.set(SBX + ':' + SBZ, null);
  PLAN_OVERRIDE.set(`${SBX}:${SBZ}:${SBL}`, {
    [lvOff]: put => { put('rest', 0, 0, lvOff, 0, 0); put('crossing', 1, 0, lvOff, 0, 0); put('poolhall', 0, 1, lvOff, 0, 0); },
    [1 - lvOff]: put => { put('pillars', 0, 0, 1 - lvOff, 0, 0); },
  });
  // a spiral tower just west of the arrival room, and a well a little east
  COLUMN_OVERRIDE.set((SBX - 1) + ':' + SBZ, { type: 'tower', cell: [1, 0], rot: 0 });
  COLUMN_OVERRIDE.set((SBX + 1) + ':' + SBZ, { type: 'well', cell: [1, 1], rot: 0 });
}

/* ---------- Chapter cards ---------- */
const MOMENTS = {
  arrival: { eyebrow: 'Year one · Day one', title: 'The First Day', art: 'ch1', text: 'You wake beside a small stepped pit, in a body that no longer hurts. You are alone. Somewhere a long way off, someone coughs, and then nothing. Beyond the arches: stone, lamplight, shelves, and more arches, and more shelves, as far as anyone has ever walked.' },
  search: { eyebrow: 'Thirty rooms, and no end', title: 'The Search', art: 'ch2', text: 'Every room is different, and every room is the same: shelves, and books, and in every book the letters in an order nobody chose. Yours is here. It has to be. There is a lamp still warm on a table you have never seen before.' },
  someone: { eyebrow: 'At the far end of the hall', title: 'Someone Else', art: 'ch3', text: 'There was someone there. You are sure of it. When you got to where they stood there was nothing: no footprints, no warmth, no sound. Only the books, the same as everywhere.' },
  abyss: { eyebrow: 'The lights went out. You kept falling.', title: 'The Deepest Abyss', art: 'ch4', text: 'The lights came back on and you are still falling. You can steer. You cannot stop — unless you hit a floor hard enough to kill you, and wake tomorrow wherever that was.' },
};

/* ---------- Notes in the margins: a few books carry a line written by someone who read them before you ---------- */
const MARGINALIA = [
  'still here', 'I was here. Day 4,112.', 'if you are reading this, hello', 'not this one either',
  'page 212 has the word "mother". I cried for an hour.', 'is anyone reading this', 'I have stopped counting the days. It is better.',
  'the lamps in the Coil are on even at night', 'don\'t go down the stepwell after dark', 'I think I heard you. Was that you?',
  'three hundred years and I still check the first page first', 'the kiosk gave me my grandmother\'s soup today',
  'we could have been friends', 'this is the 90,000th book I have opened. It is not mine.', 'someone keeps putting these back',
  'ALREADY CHECKED', 'checked — 1 July, whatever year this is', 'there is a hidden room behind a bookcase two floors up. Push.',
  'I found a sentence. I have lost it again.', 'the Void Hall has a staircase to nowhere. I climbed it. There is a book at the top. Not mine.',
  'I fell for eleven years. Don\'t.', 'if you find a book with my name in it, leave it where it is', 'I love you, M.',
  'the corridor is 128 metres long. I have walked it 400 times.', 'you are not the only one', 'breathe',
  'I heard footsteps for a week. They never came closer.', 'whoever keeps leaving the lamps on: thank you',
  'we were here — 5 of us. Now 3.', 'the upside-down room makes me feel better, somehow', 'go back. no, keep going.',
  'is it worse to find it, or not to?', 'the sky in the Outside is painted. I touched it.', 'there is no mirror anywhere. Have you noticed?',
  'I am going to walk until I stop.', 'the numbers on the plaques are wrong', 'rest area three rooms north has the good beds',
  'every book is the book of someone who never lived', 'no.', 'I remember the colour of the kitchen. Yellow.',
];
const noteHash = (id, pg) => strHash(`note:${id.f}:${id.x}:${id.z}:${id.k}:${id.p}:${pg}`);
/* the note on this page of this book, or null: about one book in seventy has one, on one page */
function marginNote(id, pg) {
  const k = keyOf(id);
  if (TRACE.leftBooks[k] !== undefined) return pg === TRACE.leftBooks[k] ? MARGINALIA[noteHash(id, 0) % MARGINALIA.length] : null;
  const h = noteHash(id, -1);
  if (h % 70 !== 0) return null;
  return pg === (h >>> 8) % PAGES ? MARGINALIA[noteHash(id, pg) % MARGINALIA.length] : null;
}
function sawNote(text, id, pg) {
  if (!S.notes) S.notes = [];
  if (S.notes.some(n => n.text === text && n.addr === keyOf(id))) return;
  S.notes.push({ text, addr: keyOf(id), page: pg + 1, day: S.day });
  logJ(`Found a note in the margin of ${addrLine(id)}, page ${pg + 1}: “${text}”`);
  save();
}

/* ---------- Things left behind: in some rooms, today, someone was just here ---------- */
const TRACE = { props: new Map(), leftBooks: {}, soundT: 40 + Math.random() * 60, fig: null, figCool: 240 + Math.random() * 240, figSeen: 0 };
const TMAT = {
  wood: propMat({ color: new THREE.Color(0.23, 0.14, 0.08), gloss: 0.3 }),
  cover: propMat({ color: new THREE.Color(0.32, 0.09, 0.07), gloss: 0.2 }),
  page: propMat({ color: new THREE.Color(0.82, 0.77, 0.64), gloss: 0.05 }),
  brass: propMat({ color: new THREE.Color(0.7, 0.52, 0.25), gloss: 0.8 }),
  shade: new THREE.MeshBasicMaterial({ color: new THREE.Color(1.6, 1.15, 0.6) }),
};
function chairMesh() {
  const g = new THREE.Group(), m = TMAT.wood;
  const add = (w, h, d, x, y, z) => { const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); b.position.set(x, y, z); g.add(b); };
  add(0.44, 0.04, 0.42, 0, 0.45, 0); add(0.44, 0.5, 0.04, 0, 0.72, -0.2);
  for (const [x, z] of [[-0.19, -0.18], [0.19, -0.18], [-0.19, 0.18], [0.19, 0.18]]) add(0.04, 0.45, 0.04, x, 0.225, z);
  return g;
}
function openBookMesh() {
  const g = new THREE.Group();
  const cov = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.012, 0.25), TMAT.cover); cov.position.y = 0.006; g.add(cov);
  for (const s of [-1, 1]) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.165, 0.025, 0.23), TMAT.page); p.position.set(s * 0.086, 0.024, 0); p.rotation.z = -s * 0.1; g.add(p); }
  return g;
}
function lampMesh() {
  const g = new THREE.Group();
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.12, 0.04, 14), TMAT.brass); base.position.y = 0.02; g.add(base);
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.25, 6), TMAT.brass); stem.position.y = 0.66; g.add(stem);
  const shade = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.2, 0.22, 16, 1, true), TMAT.shade); shade.position.y = 1.3; g.add(shade);
  g.userData.shade = shade; return g;
}
const TRACE_TEXT = {
  book: 'A book left open. The pages are still warm.',
  chair: 'A chair pulled out, as if someone had just stood up.',
  lamp: 'A reading lamp, still on. The shade is warm to the touch.',
};
/* called for every room as it is placed: decide (by room and day) whether someone was just here */
function traceRoom(inst) {
  if (!inst.pf || inst.pf.meta.repeat || inst.slot !== undefined || !S) return;
  const h = strHash(`trace:${inst.key}:${S.year}:${S.day}`);
  if (h % 100 >= 13) return;
  const M = inst.pf.meta, nav = M.nav || [], seats = M.spots.filter(s => s.k === 'sit' || s.k === 'read');
  if (!nav.length) return;
  const R = sfc32(h, h ^ 0x5bd1e995, 7, 11); for (let i = 0; i < 6; i++) R();
  const p = nav[Math.floor(R() * nav.length)], grp = new THREE.Group(), items = [];
  const kind = R();
  // a little reading camp: a chair, a lamp beside it, the book on the floor or the seat
  if (kind < 0.45) {
    const c = chairMesh(); c.position.set(p[0], p[1], p[2]); c.rotation.y = R() * 6.28; grp.add(c); items.push({ k: 'chair', at: [p[0], p[1] + 0.6, p[2]] });
    const a = R() * 6.28, l = lampMesh(); l.position.set(p[0] + Math.cos(a) * 0.7, p[1], p[2] + Math.sin(a) * 0.7); grp.add(l); items.push({ k: 'lamp', at: [l.position.x, p[1] + 1.2, l.position.z], mesh: l });
    const b = openBookMesh(); b.position.set(p[0] + Math.cos(a + 1.4) * 0.55, p[1], p[2] + Math.sin(a + 1.4) * 0.55); b.rotation.y = R() * 6.28; grp.add(b); items.push({ k: 'book', at: [b.position.x, p[1] + 0.05, b.position.z] });
  } else if (kind < 0.7 && seats.length) {   // a book left open on a seat
    const s = seats[Math.floor(R() * seats.length)], b = openBookMesh(); b.position.set(s.p[0], s.p[1] + 0.02, s.p[2]); b.rotation.y = R() * 6.28; grp.add(b); items.push({ k: 'book', at: [s.p[0], s.p[1] + 0.06, s.p[2]] });
  } else if (kind < 0.85) {
    const c = chairMesh(); c.position.set(p[0], p[1], p[2]); c.rotation.set(0, R() * 6.28, 0); grp.add(c); items.push({ k: 'chair', at: [p[0], p[1] + 0.6, p[2]] });
  } else {
    const l = lampMesh(); l.position.set(p[0], p[1], p[2]); grp.add(l); items.push({ k: 'lamp', at: [p[0], p[1] + 1.2, p[2]], mesh: l });
  }
  // the book that was left open: a real one from the room's own shelves, open at the page with the note
  for (const it of items) if (it.k === 'book') {
    const a = instAddr(inst), id = { f: a.f, x: a.x, z: a.z, k: Math.floor(R() * Math.max(1, M.slabs.length)), p: Math.floor(R() * 30) };
    it.id = id; const pg = Math.floor(R() * PAGES); it.page = pg; TRACE.leftBooks[keyOf(id)] = pg;
  }
  inst.grp.add(grp);
  TRACE.props.set(inst.key, { inst, grp, items });
}
function dropTraces() { for (const [k, t] of TRACE.props) if (WORLD.inst.get(k) !== t.inst) { t.inst.grp.remove(t.grp); TRACE.props.delete(k); } }
function resetTraces() {
  for (const t of TRACE.props.values()) t.inst.grp.remove(t.grp);
  TRACE.props.clear(); TRACE.leftBooks = {};
  for (const r of WORLD.inst.values()) traceRoom(r);
}
WORLD.onPlace = r => traceRoom(r);
const _tp = new THREE.Vector3();
/* what you are looking at, among the things left behind */
function traceTarget() {
  let best = null, bt = 2.6;
  const o = camera.getWorldPosition(new THREE.Vector3()), d = camera.getWorldDirection(new THREE.Vector3());
  for (const t of TRACE.props.values()) for (const it of t.items) {
    _tp.set(it.at[0], it.at[1], it.at[2]).applyMatrix4(t.inst.m);
    const ox = o.x - _tp.x, oy = o.y - _tp.y, oz = o.z - _tp.z, b = ox * d.x + oy * d.y + oz * d.z, c = ox * ox + oy * oy + oz * oz - 0.3 * 0.3, h = b * b - c;
    if (h < 0) continue; const tt = -b - Math.sqrt(h);
    if (tt > 0 && tt < bt) { bt = tt; best = { kind: 'trace', it }; }
  }
  if (best && rayHit(o, d, bt + 0.05) < bt - 0.05) return null;   // behind a wall
  return best;
}

/* ---------- Somebody else, somewhere: footsteps and a cough a few rooms off ---------- */
function farSound(kind) {
  const ctx = AU.ctx; if (!ctx || !AU.noise) return;
  const t0 = ctx.currentTime, pan = ctx.createStereoPanner(); pan.pan.value = (Math.random() * 2 - 1) * 0.8;
  const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900;
  const out = ctx.createGain(); out.gain.value = 1;
  pan.connect(lp); lp.connect(out); out.connect(AU.master); const rs = ctx.createGain(); rs.gain.value = 1.6; out.connect(rs); rs.connect(AU.rev);
  const hit = (t, f, dur, g, type = 'bandpass', q = 1) => {
    const s = ctx.createBufferSource(); s.buffer = AU.noise; s.playbackRate.value = 0.8 + Math.random() * 0.4;
    const fl = ctx.createBiquadFilter(); fl.type = type; fl.frequency.value = f; fl.Q.value = q;
    const e = ctx.createGain(); e.gain.setValueAtTime(0, t); e.gain.linearRampToValueAtTime(g, t + 0.01); e.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    s.connect(fl); fl.connect(e); e.connect(pan); s.start(t, Math.random()); s.stop(t + dur + 0.05);
  };
  if (kind === 'steps') {   // someone walking, a few rooms away, going the other way
    const n = 7 + Math.floor(Math.random() * 8), gap = 0.5 + Math.random() * 0.15, g0 = 0.05 + Math.random() * 0.03;
    for (let i = 0; i < n; i++) hit(t0 + i * gap + Math.random() * 0.03, 170 + Math.random() * 40, 0.09, g0 * (1 - i / (n + 2)), 'lowpass', 0.7);
    lp.frequency.setValueAtTime(900, t0); lp.frequency.linearRampToValueAtTime(350, t0 + n * gap);
  } else if (kind === 'cough') {
    const f = 700 + Math.random() * 500, g = 0.07;
    hit(t0, f, 0.16, g, 'bandpass', 1.3); hit(t0 + 0.24, f * 0.9, 0.2, g * 0.8, 'bandpass', 1.3);
    if (Math.random() < 0.5) hit(t0 + 0.55, f * 1.05, 0.14, g * 0.6, 'bandpass', 1.3);
  } else if (kind === 'book') {   // a book dropped, far off, and then the quiet
    hit(t0, 220, 0.18, 0.08, 'lowpass', 0.7); hit(t0 + 0.02, 2600, 0.08, 0.015, 'highpass', 0.5);
  } else if (kind === 'chair') {   // a chair scraping back
    const s = ctx.createOscillator(); s.type = 'sawtooth'; s.frequency.setValueAtTime(95, t0); s.frequency.linearRampToValueAtTime(70, t0 + 0.5);
    const e = ctx.createGain(); e.gain.setValueAtTime(0, t0); e.gain.linearRampToValueAtTime(0.012, t0 + 0.05); e.gain.linearRampToValueAtTime(0, t0 + 0.5);
    s.connect(e); e.connect(pan); s.start(t0); s.stop(t0 + 0.55);
  }
}

/* ---------- The figure at the end of the hall ---------- */
function figureMesh() {
  const g = new THREE.Group(), m = propMat({ color: new THREE.Color(0.035, 0.032, 0.03), gloss: 0.05 });
  const robe = new THREE.Mesh(lathe([[0.001, 0.02], [0.3, 0.02], [0.27, 0.4], [0.22, 0.95], [0.21, 1.25], [0.23, 1.4], [0.12, 1.5], [0.001, 1.52]], 12), m); g.add(robe);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 10), m); head.position.y = 1.65; head.scale.set(0.95, 1.1, 1); g.add(head);
  g.visible = false; scene.add(g); return g;
}
const FIG = { mesh: null, on: false, ax: 0, ay: 0, az: 0, t: 0, unseen: 0 };
function trySpawnFigure() {
  const o = camera.getWorldPosition(new THREE.Vector3()), f = camera.getWorldDirection(new THREE.Vector3());
  for (let k = 0; k < 6; k++) {
    const a = Math.atan2(f.x, f.z) + (Math.random() - 0.5) * 0.7, d = new THREE.Vector3(Math.sin(a), 0, Math.cos(a));
    const far = rayHit(o, d, 60);
    if (far < 20) continue;
    const dist = Math.min(far - 2, 20 + Math.random() * 20);
    const x = o.x + d.x * dist, z = o.z + d.z * dist, g = footing(x, S.y + 1.5, z, 0.2, 3);
    if (g === -Infinity || Math.abs(g - S.y) > 2.5) continue;
    FIG.mesh = FIG.mesh || figureMesh();
    FIG.ax = absX() + (x - S.x); FIG.ay = S.floor * RLH + g; FIG.az = absZ() + (z - S.z);
    FIG.on = true; FIG.t = 0; FIG.unseen = 0; FIG.mesh.visible = true;
    return true;
  }
  return false;
}
function updateFigure(dt) {
  if (!FIG.on) {
    TRACE.figCool -= dt;
    if (TRACE.figCool <= 0 && !S.fall && !dark && MODE === 'play') { if (trySpawnFigure()) TRACE.figCool = 420 + Math.random() * 600; else TRACE.figCool = 20; }
    return;
  }
  FIG.t += dt;
  const x = FIG.ax - S.cx * RC, y = FIG.ay - S.floor * RLH, z = FIG.az - S.cz * RC;
  FIG.mesh.position.set(x, y, z); FIG.mesh.rotation.y = Math.atan2(S.x - x, S.z - z);
  const dist = Math.hypot(x - S.x, z - S.z);
  // are they in view?
  const v = _tp.set(x, y + 1, z).project(camera), inView = Math.abs(v.x) < 1 && Math.abs(v.y) < 1 && v.z < 1;
  FIG.unseen = inView ? 0 : FIG.unseen + dt;
  if (dist < 12 || FIG.unseen > 1.2 || FIG.t > 45 || dark || S.fall || Math.abs(y - S.y) > 4) {
    FIG.on = false; FIG.mesh.visible = false;
    if (FIG.t > 1.5) {
      TRACE.figSeen++;
      logJ(TRACE.figSeen === 1 ? 'Saw someone standing at the far end of a long room. When I got there, nobody.' : 'Saw the figure again, far off. Gone again.');
      if (!S.flags.someone) { S.flags.someone = 1; setTimeout(() => { if (MODE === 'play') showMoment('someone'); }, 1500); }
    }
  }
}

/* ---------- The engine the game calls ---------- */
let storyT = 0;
function storyTick(dt) {
  updateFigure(dt);
  for (const t of TRACE.props.values()) for (const it of t.items) if (it.mesh && it.mesh.userData.shade) it.mesh.userData.shade.material.color.setScalar(1).setRGB(1.5 + Math.sin(performance.now() / 180 + it.at[0]) * 0.08, 1.1, 0.58);
  storyT += dt; if (storyT < 1) return; const sec = storyT; storyT = 0;
  dropTraces();
  // sounds from elsewhere
  if (!S.fall && MODE === 'play') {
    TRACE.soundT -= sec;
    if (TRACE.soundT <= 0) { TRACE.soundT = 70 + Math.random() * 130; const r = Math.random(); farSound(r < 0.5 ? 'steps' : r < 0.75 ? 'cough' : r < 0.9 ? 'book' : 'chair'); }
  }
  if (S.stats.rooms >= 30 && !S.flags.searchCard) { S.flags.searchCard = 1; showMoment('search'); }
  updateThreadsHUD();
}
function storyDawn() { resetTraces(); }
function storyEvent(type, data) { if (type === 'landed') S.flags.landed = 1; }
function storyTargets() { return S.fall ? null : traceTarget(); }
function placeNamed() { resetTraces(); }

/* ---------- Threads: gentle hints, nothing more ---------- */
const THREADS = [
  { id: 'kiosk', text: () => 'See what the kiosk will give you', show: () => true, done: () => S.flags.usedKiosk },
  { id: 'open', text: () => 'Open a book (E on a shelf)', show: () => true, done: () => S.flags.firstBook },
  { id: 'rooms', text: () => 'Walk. See how far the rooms go', show: () => S.flags.firstBook, done: () => S.stats.rooms >= 30 },
  { id: 'frag', text: () => 'Find words in the noise: a sentence in one of the books', show: () => S.stats.books >= 3, done: () => S.frags.length > 0 },
  { id: 'note', text: () => 'Someone has written in the margins of some books', show: () => S.flags.firstBook && S.stats.books >= 10, done: () => (S.notes || []).length > 0 },
  { id: 'stacks', text: () => 'While falling, steer into a floor: you’ll wake tomorrow where you hit', show: () => S.flags.fallHint || S.fall, done: () => S.flags.landed },
];
function activeThreads() { return THREADS.filter(t => t.show() && !t.done()); }
function updateThreadsHUD() { const a = activeThreads(); const el = $('#h-thread'); if (!el) return; el.hidden = !a.length || !S.settings.hints; if (a.length) el.textContent = a[a.length - 1].text(); }
