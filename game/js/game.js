'use strict';
/* ==========================================================================
   Audio — a procedural drone, echoing footsteps, water, pages, wind
   ========================================================================== */
const AU = { ctx: null };
function noiseBuf(ctx, sec) { const b = ctx.createBuffer(1, Math.floor(ctx.sampleRate * sec), ctx.sampleRate), d = b.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; return b; }
function audioInit() {
  if (AU.ctx) { if (AU.ctx.state === 'suspended') AU.ctx.resume(); return; }
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)(); AU.ctx = ctx;
    AU.out = ctx.createGain(); AU.out.gain.value = S ? S.settings.vol : 0.8; AU.out.connect(ctx.destination);
    AU.under = ctx.createBiquadFilter(); AU.under.type = 'lowpass'; AU.under.frequency.value = 20000; AU.under.connect(AU.out);
    AU.master = ctx.createGain(); AU.master.gain.value = 1; AU.master.connect(AU.under);
    const rev = ctx.createConvolver(), len = ctx.sampleRate * 5, ir = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let ch = 0; ch < 2; ch++) { const d = ir.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.2); }
    rev.buffer = ir; AU.rev = ctx.createGain(); AU.rev.gain.value = 0.7; AU.rev.connect(rev); rev.connect(AU.master);
    AU.noise = noiseBuf(ctx, 2);
    // the room tone: a soft chord that breathes, like a big tiled room with the water running somewhere
    const dg = ctx.createGain(); dg.gain.value = 0.03; const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 420; lp.Q.value = 0.5;
    lp.connect(dg); dg.connect(AU.master); dg.connect(AU.rev); AU.drone = dg;
    [[65.4, 'sine', 0.6], [98.0, 'sine', 0.45], [130.8, 'triangle', 0.18], [196.0, 'sine', 0.08], [246.9, 'sine', 0.05]].forEach(([f, t, g]) => { const o = ctx.createOscillator(); o.type = t; o.frequency.value = f; const og = ctx.createGain(); og.gain.value = g; o.connect(og); og.connect(lp); o.start(); });
    const lfo = ctx.createOscillator(); lfo.frequency.value = 0.03; const lg = ctx.createGain(); lg.gain.value = 140; lfo.connect(lg); lg.connect(lp.frequency); lfo.start();
    // water: filtered noise, louder near pools
    const wat = ctx.createBufferSource(); wat.buffer = AU.noise; wat.loop = true; const wf = ctx.createBiquadFilter(); wf.type = 'bandpass'; wf.frequency.value = 900; wf.Q.value = 0.35;
    AU.water = ctx.createGain(); AU.water.gain.value = 0; wat.connect(wf); wf.connect(AU.water); AU.water.connect(AU.master); AU.water.connect(AU.rev); wat.start();
    // fluorescent hum for the backrooms
    const hum = ctx.createOscillator(); hum.type = 'sawtooth'; hum.frequency.value = 120; const hf = ctx.createBiquadFilter(); hf.type = 'bandpass'; hf.frequency.value = 240; hf.Q.value = 6;
    AU.hum = ctx.createGain(); AU.hum.gain.value = 0; hum.connect(hf); hf.connect(AU.hum); AU.hum.connect(AU.master); hum.start();
    const w = ctx.createBufferSource(); w.buffer = AU.noise; w.loop = true; AU.windF = ctx.createBiquadFilter(); AU.windF.type = 'lowpass'; AU.windF.frequency.value = 300;
    AU.wind = ctx.createGain(); AU.wind.gain.value = 0; w.connect(AU.windF); AU.windF.connect(AU.wind); AU.wind.connect(AU.master); w.start();
  } catch (e) { AU.ctx = null; }
  startMusic();
}
function burst({ dur = 0.08, type = 'bandpass', f = 900, q = 1.2, gain = 0.25, rev = 0.5, att = 0.004 }) {
  const ctx = AU.ctx; if (!ctx) return;
  const t = ctx.currentTime, s = ctx.createBufferSource(); s.buffer = AU.noise; s.playbackRate.value = 0.8 + Math.random() * 0.4;
  const fl = ctx.createBiquadFilter(); fl.type = type; fl.frequency.value = f; fl.Q.value = q;
  const g = ctx.createGain(); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(gain, t + att); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  s.connect(fl); fl.connect(g); g.connect(AU.master); const rs = ctx.createGain(); rs.gain.value = rev; g.connect(rs); rs.connect(AU.rev);
  s.start(t, Math.random()); s.stop(t + dur + 0.05);
}
function tone(f0, f1, dur, gain, type = 'sine', rev = 0.4) {
  const ctx = AU.ctx; if (!ctx) return; const t = ctx.currentTime, o = ctx.createOscillator(), g = ctx.createGain();
  o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + dur);
  g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(gain, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g); g.connect(AU.master); const rs = ctx.createGain(); rs.gain.value = rev; g.connect(rs); rs.connect(AU.rev); o.start(t); o.stop(t + dur + 0.05);
}
const SFX = {
  // footsteps: a low thud of the heel, and on stone or marble a small click that rings off the vaults
  step: (soft, carpet) => {
    burst({ dur: 0.09, type: 'lowpass', f: carpet ? 140 : 200 + Math.random() * 60, q: 0.7, gain: carpet ? 0.12 : soft ? 0.14 : 0.24, rev: carpet ? 0.1 : 0.5, att: 0.006 });
    if (!carpet) tone(1500 + Math.random() * 500, 1100, 0.035, soft ? 0.006 : 0.012, 'triangle', 1.0);
  },
  land: hard => { burst({ dur: 0.16, type: 'lowpass', f: 150, q: 0.7, gain: hard ? 0.5 : 0.3, rev: 0.6, att: 0.005 }); tone(90, 50, 0.18, hard ? 0.18 : 0.1, 'sine', 0.5); },
  splash: () => { burst({ dur: 0.25, type: 'bandpass', f: 1400 + Math.random() * 800, q: 0.8, gain: 0.12, rev: 0.8, att: 0.01 }); },
  plunge: () => { burst({ dur: 0.7, type: 'lowpass', f: 900, gain: 0.35, rev: 1.0, att: 0.01 }); tone(300, 90, 0.5, 0.08, 'sine', 0.8); },
  page: () => { burst({ dur: 0.22, type: 'highpass', f: 2600, q: 0.5, gain: 0.07, rev: 0.2, att: 0.03 }); setTimeout(() => burst({ dur: 0.12, type: 'highpass', f: 3400, q: 0.5, gain: 0.05, rev: 0.2 }), 90); },
  book: () => burst({ dur: 0.06, f: 380, q: 2, gain: 0.2, rev: 0.6 }),
  chime: () => { tone(660, 660, 1.2, 0.07); setTimeout(() => tone(990, 990, 1.4, 0.05), 140); },
  thunk: () => { tone(80, 32, 1.6, 0.35, 'sine', 0.9); burst({ dur: 0.5, type: 'lowpass', f: 200, gain: 0.3, rev: 0.9 }); },
  hit: () => { burst({ dur: 0.18, type: 'lowpass', f: 420, gain: 0.5, rev: 0.4 }); tone(120, 50, 0.25, 0.3); },
  impact: () => { burst({ dur: 0.6, type: 'lowpass', f: 300, gain: 0.9, rev: 1.0 }); tone(70, 25, 0.8, 0.6); },
  jump: () => { burst({ dur: 0.07, type: 'lowpass', f: 180, q: 0.7, gain: 0.16, rev: 0.3, att: 0.004 }); tone(160, 110, 0.12, 0.04, 'sine', 0.3); },
  drink: () => { burst({ dur: 0.3, type: 'bandpass', f: 1800, q: 3, gain: 0.08, rev: 0.3 }); tone(900, 1300, 0.15, 0.03, 'sine', 0.3); },
  scream: () => { tone(820, 380, 2.4, 0.05, 'sawtooth', 1.0); },
  chant: () => { tone(98, 96, 3.5, 0.06, 'sawtooth', 1.0); setTimeout(() => tone(110, 108, 3.0, 0.05, 'sawtooth', 1.0), 900); },
};

/* ==========================================================================
   Music: a generative score, never the same twice. Slow pads walk a minor
   progression; a far-off piano drops single notes into the reverb.
   ========================================================================== */
const MUS = { on: false, t: 0, chord: 0, next: 0, timer: null };
const MUS_CHORDS = [   // MIDI notes, in D minor: Dm9, Bbmaj7, Gm6, A7sus, Fmaj7/C, Em7b5, Dm(add9)/A, C6
  [38, 50, 53, 57, 64], [34, 46, 50, 53, 57], [31, 43, 46, 50, 52], [33, 45, 50, 52, 55],
  [36, 48, 53, 57, 64], [40, 52, 55, 58, 62], [33, 45, 50, 53, 64], [36, 48, 52, 55, 57]];
const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
function musicLevel() { return S && S.settings.music !== undefined ? S.settings.music : 0.6; }
function startMusic() {
  const ctx = AU.ctx; if (!ctx || MUS.on) return;
  MUS.on = true;
  MUS.bus = ctx.createGain(); MUS.bus.gain.value = 0; MUS.bus.connect(AU.under);
  MUS.send = ctx.createGain(); MUS.send.gain.value = 0.9; MUS.bus.connect(MUS.send); MUS.send.connect(AU.rev);
  MUS.pf = ctx.createBiquadFilter(); MUS.pf.type = 'lowpass'; MUS.pf.frequency.value = 900; MUS.pf.Q.value = 0.3; MUS.pf.connect(MUS.bus);
  MUS.next = ctx.currentTime + 0.5; MUS.chord = Math.floor(Math.random() * MUS_CHORDS.length);
  musicMix(true); musicTick();
}
function musicMix(now) {
  if (!MUS.on) return;
  const ctx = AU.ctx, lv = musicLevel() * (dark ? 0.45 : 1) * (S && S.fall ? 0.6 : 1) * 0.55;
  MUS.bus.gain.setTargetAtTime(lv, ctx.currentTime, now ? 2.5 : 1.5);
  MUS.pf.frequency.setTargetAtTime(dark ? 520 : 900, ctx.currentTime, 3);
}
function padVoice(m, t0, dur, g) {
  const ctx = AU.ctx, f = mtof(m);
  const env = ctx.createGain(); env.gain.setValueAtTime(0, t0);
  env.gain.linearRampToValueAtTime(g, t0 + dur * 0.35); env.gain.setValueAtTime(g, t0 + dur * 0.6); env.gain.linearRampToValueAtTime(0, t0 + dur + 3);
  env.connect(MUS.pf);
  for (const [det, type] of [[-5, 'triangle'], [4, 'sine'], [0, 'sine']]) {
    const o = ctx.createOscillator(); o.type = type; o.frequency.value = f; o.detune.value = det + (Math.random() - 0.5) * 4;
    o.connect(env); o.start(t0); o.stop(t0 + dur + 3.2);
  }
}
function pianoNote(m, t0, g) {
  const ctx = AU.ctx, f = mtof(m), out = ctx.createGain(); out.gain.value = g; out.connect(MUS.bus);
  [[1, 1, 4.5], [2, 0.35, 2.2], [3, 0.12, 1.2], [4.02, 0.05, 0.7]].forEach(([h, a, d]) => {
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f * h;
    const e = ctx.createGain(); e.gain.setValueAtTime(0, t0); e.gain.linearRampToValueAtTime(a, t0 + 0.006); e.gain.exponentialRampToValueAtTime(0.0001, t0 + d);
    o.connect(e); e.connect(out); o.start(t0); o.stop(t0 + d + 0.1);
  });
}
function musicTick() {
  if (!MUS.on) return;
  const ctx = AU.ctx;
  while (MUS.next < ctx.currentTime + 1.0) {
    const t0 = MUS.next, dur = 11 + Math.random() * 6, ch = MUS_CHORDS[MUS.chord];
    const low = dark ? -12 : 0;
    padVoice(ch[0] + low, t0, dur, 0.05);
    for (let i = 1; i < ch.length; i++) if (Math.random() < 0.8) padVoice(ch[i] + low, t0 + Math.random() * 1.5, dur, 0.022);
    // the piano: a few notes from the chord, high and far away, not every bar
    const n = dark ? (Math.random() < 0.4 ? 1 : 0) : Math.floor(Math.random() * 4);
    let tp = t0 + 1.5 + Math.random() * 2;
    for (let k = 0; k < n; k++) {
      const m = ch[1 + Math.floor(Math.random() * (ch.length - 1))] + (Math.random() < 0.6 ? 24 : 12);
      pianoNote(m, tp, 0.05 + Math.random() * 0.03);
      if (Math.random() < 0.3) pianoNote(m + (Math.random() < 0.5 ? 2 : -3), tp + 0.45, 0.035);
      tp += 1.2 + Math.random() * 3;
    }
    // drift through the progression, sometimes stepping back, sometimes skipping
    const r = Math.random();
    MUS.chord = (MUS.chord + (r < 0.6 ? 1 : r < 0.8 ? 2 : MUS_CHORDS.length - 1)) % MUS_CHORDS.length;
    MUS.next = t0 + dur * 0.72;
  }
  MUS.timer = setTimeout(musicTick, 400);
}

/* ==========================================================================
   Input
   ========================================================================== */
const keys = {};
let MODE = 'title', locked = false, mouseDrag = false, pauseSuppressed = false;
const isTouch = matchMedia('(pointer: coarse)').matches || ('ontouchstart' in window && navigator.maxTouchPoints > 0);
const joy = { x: 0, y: 0, id: null };
const canvas = renderer.domElement;
function requestLock() { if (isTouch) return; try { const p = canvas.requestPointerLock(); if (p && p.catch) p.catch(() => {}); } catch (e) {} }
document.addEventListener('pointerlockchange', () => {
  locked = document.pointerLockElement === canvas;
  if (!locked && MODE === 'play' && !pauseSuppressed) openPause();
  if (S && MODE === 'play') showClickHint();
});
canvas.addEventListener('mousedown', () => { audioInit(); if (MODE !== 'play') return; if (!locked) { requestLock(); mouseDrag = true; } });
addEventListener('mouseup', () => mouseDrag = false);
addEventListener('mousemove', e => {
  if (MODE !== 'play' || !S) return;
  if (locked || mouseDrag) { const s = 0.0022 * S.settings.sens; S.yaw -= e.movementX * s; S.pitch = clamp(S.pitch - e.movementY * s, -1.5, 1.5); }
});
addEventListener('keydown', e => {
  if (e.target && e.target.tagName === 'INPUT') { if (e.code === 'Escape') e.target.blur(); return; }
  const k = e.code; keys[k] = true;
  if (e.repeat && ['KeyE', 'KeyR', 'KeyG', 'KeyJ', 'KeyC', 'KeyZ', 'KeyQ'].includes(k)) return;
  if (MODE === 'play') {
    if (['Space', 'ArrowUp', 'ArrowDown', 'Tab'].includes(k)) e.preventDefault();
    if (k === 'KeyE') act('use'); else if (k === 'KeyR') act('read'); else if (k === 'KeyG') act('drop');
    else if (k === 'KeyJ') openJournal(); else if (k === 'KeyC') { if (!PL.swim) PL.crouch = !PL.crouch; }
    else if (k === 'KeyZ') act('sleep'); else if (k === 'KeyQ') act('consume');
    else if (k === 'Space' && S.fall) act('sleep');
    else if (k === 'Escape' && !locked) openPause();
  } else if (MODE === 'ui') {
    if (k === 'Escape' || (k === 'KeyJ' && !$('#journal').hidden)) { e.preventDefault(); if (!$('#moment').hidden) closeMoment(); else closeOverlays(); }
    else if (!$('#reader').hidden && (k === 'ArrowRight' || k === 'ArrowLeft')) turnPage(k === 'ArrowRight' ? 1 : -1);
    else if (!$('#moment').hidden && (k === 'Enter' || k === 'Space')) closeMoment();
  } else if (MODE === 'pause' && k === 'Escape') resume();
  else if (MODE === 'prologue' && (k === 'Enter' || k === 'Space')) $('#b-pro').click();
});
addEventListener('keyup', e => { keys[e.code] = false; });
addEventListener('blur', () => { for (const k in keys) keys[k] = false; });
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); applyQuality(); });
if (isTouch) {
  const J = $('#joy'), knob = J.querySelector('i');
  const moveJoy = e => { const r = J.getBoundingClientRect(), dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2), d = Math.min(1, Math.hypot(dx, dy) / 50), a = Math.atan2(dy, dx); joy.x = Math.cos(a) * d; joy.y = Math.sin(a) * d; knob.style.transform = `translate(${joy.x * 40}px,${joy.y * 40}px)`; };
  J.addEventListener('pointerdown', e => { joy.id = e.pointerId; J.setPointerCapture(e.pointerId); moveJoy(e); });
  J.addEventListener('pointermove', e => { if (e.pointerId === joy.id) moveJoy(e); });
  const endJ = e => { if (e.pointerId !== joy.id) return; joy.id = null; joy.x = joy.y = 0; knob.style.transform = ''; };
  J.addEventListener('pointerup', endJ); J.addEventListener('pointercancel', endJ);
  let look = null;
  canvas.addEventListener('pointerdown', e => { audioInit(); if (e.pointerType !== 'mouse') look = { id: e.pointerId, x: e.clientX, y: e.clientY }; });
  canvas.addEventListener('pointermove', e => { if (!look || e.pointerId !== look.id || MODE !== 'play') return; S.yaw -= (e.clientX - look.x) * 0.005 * S.settings.sens; S.pitch = clamp(S.pitch - (e.clientY - look.y) * 0.005 * S.settings.sens, -1.5, 1.5); look.x = e.clientX; look.y = e.clientY; });
  canvas.addEventListener('pointerup', e => { if (look && e.pointerId === look.id) look = null; });
  const tb = (id, fn) => $(id).addEventListener('pointerdown', e => { e.preventDefault(); audioInit(); if (MODE === 'play') fn(); });
  tb('#t-e', () => act('use')); tb('#t-r', () => act('read')); tb('#t-g', () => act('drop'));
  tb('#t-c', () => { if (PL.swim) keys.TouchDive = !keys.TouchDive; else PL.crouch = !PL.crouch; }); tb('#t-sp', () => { if (S.fall) act('sleep'); else keys.TouchJump = true; }); tb('#t-z', () => act('sleep'));
  tb('#t-j', openJournal); tb('#t-p', openPause);
}

/* ==========================================================================
   The player. Position is (S.x, S.y, S.z) metres inside cell (S.cx, S.cz) on
   floor S.floor; that cell's corner is the origin of everything drawn.
   ========================================================================== */
const PL = { vy: 0, vx: 0, vz: 0, onGround: true, crouch: false, eye: 1.62, stepAcc: 0, bob: 0, edgeArm: 0, hurtT: 0, dead: false, falling: false, shake: 0, camY: null, lastT: 0, peak: 0, swim: false, wade: 0, under: false, room: null, wasWet: false };
const _pp = new THREE.Vector3(), _sp = new THREE.Vector3();
const absX = () => S.cx * RC + S.x, absY = () => S.floor * RLH + S.y, absZ = () => S.cz * RC + S.z;
function moveInput() {
  const w = { x: 0, z: 0 };
  if (keys.KeyW || keys.ArrowUp) w.z -= 1; if (keys.KeyS || keys.ArrowDown) w.z += 1;
  if (keys.KeyA || keys.ArrowLeft) w.x -= 1; if (keys.KeyD || keys.ArrowRight) w.x += 1;
  w.x += joy.x; w.z += joy.y;
  const ml = Math.hypot(w.x, w.z); if (ml > 1) { w.x /= ml; w.z /= ml; }
  const sy = Math.sin(S.yaw), cy = Math.cos(S.yaw);
  return { x: w.x * cy + w.z * sy, z: -w.x * sy + w.z * cy, m: Math.min(ml, 1) };
}
let lastShift = new THREE.Vector3();
function wrapPlayer(fast) {
  let dcx = 0, dcz = 0, fm = 0;
  while (S.x >= RC) { S.x -= RC; S.cx++; dcx++; } while (S.x < 0) { S.x += RC; S.cx--; dcx--; }
  while (S.z >= RC) { S.z -= RC; S.cz++; dcz++; } while (S.z < 0) { S.z += RC; S.cz--; dcz--; }
  while (S.y >= RLH - 2) { S.y -= RLH; S.floor++; fm++; } while (S.y < -2) { S.y += RLH; S.floor--; fm--; }
  if (dcx || dcz || fm) {
    if (PL.camY !== null) PL.camY -= fm * RLH;
    PL.peak -= fm * RLH;
    lastShift.set(dcx * RC, fm * RLH, dcz * RC);
    worldOrigin(S.cx, S.cz, S.floor);
    updateWorld(S.x, S.y, S.z, fast);
    updateThrown(0, lastShift);
    if (!fast) { updateGroundBooks(); refreshBooks(); }
  }
  return { moved: !!(dcx || dcz), fm };
}
/* the body is three spheres: the lower two only push sideways (so steps and slopes stay walkable), the head pushes every way */
function collideBody(pos, height) {
  for (let it = 0; it < 2; it++) {
    for (const h of [0.82, Math.min(1.2, height - 0.36)]) { _sp.set(pos.x, pos.y + h, pos.z); pushSphere(_sp, 0.3, true); pos.x = _sp.x; pos.z = _sp.z; }
    const hy = pos.y + height - 0.3; _sp.set(pos.x, hy, pos.z); pushSphere(_sp, 0.3, false);
    pos.x = _sp.x; pos.z = _sp.z;
    if (_sp.y < hy - 1e-4) { pos.y += _sp.y - hy; if (PL.vy > 0) PL.vy = 0; }
  }
}
function updatePlayer(dt) {
  if (!roomReadyAt(S.x, S.y + 0.5, S.z)) { PL.vy = 0; return; }   // the room under you is still arriving
  if (S.fall) { updateFalling(dt); return; }
  const mi = moveInput();
  const wat = waterAt(S.x, S.y + 0.3, S.z), depth = wat ? wat.top - S.y : 0;
  const swim = !!wat && depth > 1.3, wade = !!wat && depth > 0.1 && !swim;
  if (swim && !PL.swim) { SFX.plunge(); PL.crouch = false; if (!S.flags.swam) { S.flags.swam = 1; logJ('Swam in one of the pools. The water is exactly the temperature of nothing.'); } }
  PL.swim = swim; PL.wade = wade ? depth : 0;
  const weak = S.hunger > 0.85 || S.thirst > 0.8;
  const sprint = (keys.ShiftLeft || keys.ShiftRight || (isTouch && mi.m > 0.97)) && !PL.crouch && !weak;
  let spd = PL.crouch ? 1.3 : sprint ? 6.2 : 2.8;
  if (wade) spd *= clamp(1.05 - depth * 0.55, 0.45, 1);
  if (swim) spd = sprint ? 2.5 : 1.7;
  let tvx = mi.x * spd, tvz = mi.z * spd;
  if (S.drunk > 0.4) { const t = performance.now() / 1000; tvx += Math.sin(t * 1.3) * S.drunk * 0.8; tvz += Math.cos(t * 0.9) * S.drunk * 0.5; }
  const k = PL.onGround || swim ? 1 - Math.exp(-dt * (swim ? 3 : 14)) : 1 - Math.exp(-dt * 1.4);
  PL.vx += (tvx - PL.vx) * k; PL.vz += (tvz - PL.vz) * k;
  const jumpKey = keys.Space || keys.TouchJump; keys.TouchJump = false;
  if (swim) {
    const float = wat.top - 1.45, dive = keys.KeyC || keys.ControlLeft || keys.TouchDive;
    const ty = dive ? Math.max(wat.bot + 0.1, S.y - 1.5) : jumpKey ? float + 0.5 : float;
    PL.vy += ((ty - S.y) * 3.5 - PL.vy) * Math.min(1, dt * 3.5);
    PL.onGround = false;
  } else {
    if (PL.onGround && jumpKey && !PL.crouch) { PL.vy = wade ? 3.3 : 4.7; PL.onGround = false; SFX.jump(); }
    PL.vy = Math.max(PL.vy - 12.5 * dt, -TERMINAL);
  }
  // at the edge of a pool, pull yourself out
  if ((swim || wade) && mi.m > 0.3) {
    const fx = S.x + mi.x / mi.m * 0.6, fz = S.z + mi.z / mi.m * 0.6;
    const g = groundAt(fx, wat.top + 0.7, fz, 0.1, 1.1);
    if (g > -Infinity && g >= wat.top - 0.15 && g < wat.top + 0.9 && g > S.y + 0.45) {
      _sp.set(fx, g + 0.9, fz); pushSphere(_sp, 0.25, true);
      if (Math.hypot(_sp.x - fx, _sp.z - fz) < 0.05) { S.x = fx; S.z = fz; S.y = g; PL.vy = 0; PL.onGround = true; PL.swim = false; SFX.splash(); placeCamera(dt); return; }
    }
  }
  const ox = S.x, oz = S.z, wasGround = PL.onGround, vyIn = PL.vy;
  const pos = _pp.set(S.x + PL.vx * dt, S.y + PL.vy * dt, S.z + PL.vz * dt);
  { const ix = pos.x, iz = pos.z;
    collideBody(pos, PL.crouch ? 1.15 : 1.78);
    // squeezed between two things, the pushes can add up past a wall's thickness and out the far side: refuse that
    if (Math.hypot(pos.x - ix, pos.z - iz) > 0.3) { pos.x = S.x; pos.z = S.z; collideBody(pos, PL.crouch ? 1.15 : 1.78); if (Math.hypot(pos.x - S.x, pos.z - S.z) > 0.3) { pos.x = S.x; pos.z = S.z; } } }
  const g = footing(pos.x, pos.y, pos.z, 0.56, PL.onGround ? 0.45 : Math.max(0.06, -PL.vy * dt + 0.06));
  if (g > -Infinity && pos.y <= g + 0.02 && PL.vy <= 0.01 && !(swim && PL.vy > 0.2)) {   // never land while still rising (at high frame rates a jump's first step is tiny)
    if (!wasGround && vyIn < -9.5 && !wat) hurt(Math.round((-vyIn - 9.5) * 8), 'the fall');
    if (!wasGround && vyIn < -2 && !wat) SFX.land(vyIn < -7);
    pos.y = g; PL.vy = 0; PL.onGround = !swim;
  } else if (wasGround && g > -Infinity && pos.y - g < 0.45 && PL.vy <= 0 && !swim) { pos.y = g; PL.vy = 0; PL.onGround = true; }
  else PL.onGround = false;
  S.x = pos.x; S.y = pos.y; S.z = pos.z;
  if (PL.onGround || swim) PL.peak = S.y; else PL.peak = Math.max(PL.peak, S.y);
  if (PL.onGround && PL.room) PL.safe = { cx: S.cx, cz: S.cz, floor: S.floor, x: S.x, y: S.y, z: S.z };
  // a room's floor is its floor: dropping out through the bottom of an ordinary room (a crack in the
  // geometry) puts you back where you last stood. Wells and towers are meant to be fallen through.
  if (PL.onGround) PL.gInst = PL.room;
  else if (PL.gInst && PL.safe && !PL.gInst.pf.meta.repeat && WORLD.inst.get(PL.gInst.key) === PL.gInst && S.y < PL.gInst.box[1] - 0.05) {
    const s0 = PL.safe; S.cx = s0.cx; S.cz = s0.cz; S.floor = s0.floor; S.x = s0.x; S.y = s0.y; S.z = s0.z; PL.vy = 0; PL.onGround = true; PL.peak = S.y;
    worldOrigin(S.cx, S.cz, S.floor); updateWorld(S.x, S.y, S.z, false);
  }
  if (!PL.onGround && !swim && PL.peak - S.y > 4.2) { startFall(false); return; }
  const moved = Math.hypot(S.x - ox, S.z - oz);
  const w = wrapPlayer();
  if (w.fm > 0) S.stats.climbed += w.fm;
  if ((PL.onGround || swim) && moved > 0) {
    S.stats.dist += moved; if (swim) S.stats.swum += moved; PL.stepAcc += moved; PL.bob += moved * 2.3;
    if (PL.stepAcc > (swim ? 1.2 : sprint ? 1.6 : 0.85)) { PL.stepAcc = 0; if (wade || swim) SFX.splash(); else SFX.step(PL.crouch, PL.room && PL.room.pf.name === 'backrooms'); }
  }
  PL.eye += ((PL.crouch ? 1.0 : 1.62) - PL.eye) * Math.min(1, dt * 10);
  placeCamera(dt);
}
function placeCamera(dt) {
  const sh = PL.shake > 0 ? (Math.random() - 0.5) * PL.shake : 0;
  dt = dt || 0.016;
  const ty = S.y + PL.eye + (PL.swim ? Math.sin(performance.now() / 700) * 0.04 : 0);
  if (PL.camY === null || S.fall || Math.abs(ty - PL.camY) > 1.2) PL.camY = ty; else PL.camY += (ty - PL.camY) * Math.min(1, dt * 13);
  camera.position.set(S.x + sh * 0.3, PL.camY + (PL.onGround && !S.fall ? Math.sin(PL.bob) * 0.026 : 0) + sh * 0.3, S.z);
  camera.rotation.set(S.pitch + sh * 0.05, S.yaw, S.drunk > 0.3 ? Math.sin(performance.now() / 1400) * 0.05 * S.drunk : 0);
  const fovT = 72 + (S.fall ? clamp(-PL.vy / TERMINAL, 0, 1) * 14 : 0);
  if (Math.abs(camera.fov - fovT) > 0.05) { camera.fov += (fovT - camera.fov) * 0.1; camera.updateProjectionMatrix(); }
  // under the surface?
  const w = PL.swim || PL.wade ? waterAt(camera.position.x, camera.position.y, camera.position.z) : null;
  PL.under = !!w && camera.position.y < w.top - 0.02;
}
/* A shaft beside you: the well's square, or the tower's open core, in world space */
function shaftNear() {
  const r = PL.room; if (!r) return null;
  const m = r.pf.meta.meta;
  _v.set(S.x, S.y, S.z).applyMatrix4(r.inv);
  if (m.shaft) {
    const [x0, z0, x1, z1] = m.shaft, lx = clamp(_v.x, x0, x1), lz = clamp(_v.z, z0, z1), d = Math.hypot(_v.x - lx, _v.z - lz);
    const inside = _v.x > x0 && _v.x < x1 && _v.z > z0 && _v.z < z1;
    return { inside, d, cx: (x0 + x1) / 2, cz: (z0 + z1) / 2, edge: [lx, lz], room: r };
  }
  if (m.core) {
    const [cx, cz, rr] = m.core, d = Math.hypot(_v.x - cx, _v.z - cz);
    const a = Math.atan2(_v.z - cz, _v.x - cx);
    return { inside: d < rr, d: Math.abs(d - rr), cx, cz, edge: [cx + Math.cos(a) * rr, cz + Math.sin(a) * rr], room: r };
  }
  return null;
}
function startFall(tackled, pushIn) {
  if (S.fall) return;
  S.fall = { startFloor: S.floor, days: 0, t: 0 };
  PL.falling = true; PL.onGround = false; PL.swim = false; PL.edgeArm = 0;
  if (pushIn) {
    const sh = shaftNear();
    if (sh) {
      const r = sh.room, dx = sh.cx - sh.edge[0], dz = sh.cz - sh.edge[1], dl = Math.hypot(dx, dz) || 1;
      _v.set(sh.edge[0] + dx / dl * 0.6, 0, sh.edge[1] + dz / dl * 0.6).applyMatrix4(r.m);
      S.x = _v.x; S.z = _v.z; S.y += 1.0;
      _w.set(dx / dl, 0, dz / dl).transformDirection(r.m);
      PL.vx = _w.x * 1.6; PL.vz = _w.z * 1.6;
    }
    PL.vy = tackled ? -1 : 0.6;
  }
  $('#fallhud').hidden = false;
  if (!tackled) logJ(pushIn ? 'Climbed over the parapet and let go.' : 'Went over the edge.');
  save();
}
function updateFalling(dt) {
  S.fall.t += dt;
  const mi = moveInput();
  const k = 1 - Math.exp(-dt * 2.2);
  PL.vx += (mi.x * 5.5 - PL.vx) * k; PL.vz += (mi.z * 5.5 - PL.vz) * (mi.m > 0.05 ? k : k * 0.4);
  PL.vy = Math.max(PL.vy - 9.8 * dt, -TERMINAL);
  const n = Math.max(1, Math.ceil(Math.abs(PL.vy * dt) / 0.3));
  for (let i = 0; i < n; i++) {
    const h = dt / n, y0 = S.y;
    const pos = _pp.set(S.x + PL.vx * h, S.y + PL.vy * h, S.z + PL.vz * h);
    collideBody(pos, 1.7);
    S.x = pos.x; S.z = pos.z;
    const g = groundAt(S.x, y0 + 0.05, S.z, 0.05, Math.max(0, y0 - pos.y) + 0.12);
    if (g > -Infinity && pos.y <= g + 0.01) {
      S.y = g;
      const wat = waterAt(S.x, S.y + 0.3, S.z);
      if (-PL.vy < 11 || (wat && wat.top - S.y > 1.2 && -PL.vy < 25)) { landAlive(!!wat); return; }
      impact(); return;
    }
    S.y = pos.y;
    const w = wrapPlayer(-PL.vy > 20);
    if (w.fm < 0) S.stats.fallen -= w.fm;
  }
  // a safety net: falling somewhere that is not a well or a tower means we slipped out of the world
  if (!instAt(S.x, S.y + 0.5, S.z)) { PL.voidT = (PL.voidT || 0) + dt; if (PL.voidT > 0.6 && PL.safe) { const s0 = PL.safe; S.cx = s0.cx; S.cz = s0.cz; S.floor = s0.floor; S.x = s0.x; S.y = s0.y; S.z = s0.z; S.fall = null; PL.falling = false; PL.vy = 0; PL.onGround = true; PL.voidT = 0; $('#fallhud').hidden = true; worldOrigin(S.cx, S.cz, S.floor); updateWorld(S.x, S.y, S.z, false); refreshBooks(true); return; } } else PL.voidT = 0;
  const sp = clamp(-PL.vy / TERMINAL, 0, 1);
  if (AU.ctx) { AU.wind.gain.value = sp * 0.35; AU.windF.frequency.value = 200 + sp * 1700; }
  PL.shake = sp * 0.06;
  placeCamera(dt);
}
function landAlive(wet) {
  PL.vy = 0; PL.vx *= 0.3; PL.vz *= 0.3; PL.falling = false; PL.onGround = true; PL.peak = S.y;
  const fl = S.fall ? S.fall.startFloor - S.floor : 0; S.fall = null; $('#fallhud').hidden = true;
  if (AU.wind) AU.wind.gain.value = 0;
  if (wet) SFX.plunge(); else SFX.step(false);
  if (fl > 0) { toast(wet ? 'You hit the water hard, and come up gasping — alive.' : 'You land hard, and roll, and are somehow still alive.'); logJ(`Fell ${fmt(fl)} floor${fl === 1 ? '' : 's'} and lived, on floor ${fmt(S.floor)}.`); }
  wrapPlayer(); updateWorld(S.x, S.y, S.z, false); refreshBooks();
}
function impact() {
  const fallen = S.fall.startFloor - S.floor;
  S.stats.maxFall = Math.max(S.stats.maxFall, fallen);
  S.landing = { cx: S.cx, cz: S.cz, floor: S.floor, x: S.x, y: S.y, z: S.z, fallen };
  SFX.impact(); PL.shake = 0.5;
  logJ(`Hit the floor of level ${fmt(S.floor)} at ${Math.round(-PL.vy)} m/s, after falling ${fmt(fallen)} floors.`);
  die('impact');
}
function hurt(n, by) {
  if (n <= 0 || PL.dead) return;
  S.hp -= n; PL.hurtT = 1; SFX.hit();
  if (S.hp <= 0) die(by);
}
function die(cause) {
  if (PL.dead) return;
  PL.dead = true; S.stats.deaths++;
  const falling = !!S.fall && cause !== 'impact';
  S.dead = { cause, falling };
  if (cause === 'impact') { S.fall = null; PL.falling = false; }
  if (S.carried) { S.carried = null; showHeld(null); updateCarry(); }
  if (cause !== 'impact') logJ({ thirst: 'Died of thirst.', drink: 'Drank myself to death.', 'the Direites': 'The Direites caught me. It took them a long time.', 'Dire Dan': 'Dire Dan kept his promise. He killed me as we fell.', 'the fall': 'Died of a fall.', drowned: 'Drowned. It was quieter than I expected.' }[cause] || `Died (${cause}).`);
  save();
  setTimeout(() => sleepNow('dead'), 900);
}

/* ==========================================================================
   Day and night, and dawn — when everything resets
   ========================================================================== */
let nightBusy = false, dark = false, momentAfter = null, dayK = 1;
function fadeMsg(t, s) { $('#fade-t').textContent = t; $('#fade-s').textContent = s || ''; $('#fade').classList.add('on'); }
function sleepNow(reason) {
  if (nightBusy) return; nightBusy = true;
  const lines = {
    bed: ['You lie down on the narrow bed.', 'The lamps make slow shapes on the ceiling. Then there is nothing.'],
    floor: ['You lie down where you are.', 'The floor is cool. Sleep comes the way it always does here: all at once.'],
    dark: ['The lights are out. Only the little step lamps still glow.', 'You sleep where you lie. Everyone does.'],
    fall: ['You close your eyes. The wind keeps its one long note.', 'You sleep, somehow, still falling.'],
    dead: ['It is dark for a long time.', 'If you are killed, you will be restored the following day.'],
  }[reason] || ['You sleep.', ''];
  pauseSuppressed = true; if (document.pointerLockElement) document.exitPointerLock();
  SFX.thunk();
  fadeMsg(lines[0], lines[1]);
  setTimeout(dawn, 3600);
}
function dawn() {
  const hours = mod(LIGHTS_ON - S.time, 24) || 24;
  const deadInFall = S.dead && S.dead.falling;
  if (S.fall && (!S.dead || deadInFall)) {
    const fl = Math.round(hours * 3600 * TERMINAL / RLH);
    S.floor -= fl; S.stats.fallen += fl; S.fall.days++; S.stats.daysFalling++;
    S.stats.maxFall = Math.max(S.stats.maxFall, S.fall.startFloor - S.floor);
  }
  if (!S.dead) { S.thirst = clamp(S.thirst + hours / 60, 0, 0.97); S.hunger = clamp(S.hunger + hours / 120, 0, 0.97); }
  S.day++; S.time = LIGHTS_ON + 0.02;
  const moved = Object.keys(S.over).length + S.ground.length;
  S.over = {}; S.ground = []; recountOver();
  S.hp = 100; S.drunk = 0;
  let sub = 'The lights come on. The shelves have not moved.'; const wasDead = !!S.dead;
  if (moved) { sub = 'Every book you moved is back on its shelf.'; if (!S.flags.sawReset) { S.flags.sawReset = 1; logJ('At dawn every book we had moved — even the ones we dropped down the well — was back on its shelf, exactly where it had been.'); } }
  if (S.dead) {
    S.hunger = 0.08; S.thirst = 0.08;
    if (S.dead.cause === 'impact' && S.landing) {
      const L = S.landing;
      S.cx = L.cx; S.cz = L.cz; S.floor = L.floor; S.x = L.x; S.y = L.y; S.z = L.z;
      S.fall = null; PL.falling = false; $('#fallhud').hidden = true;
      sub = `You wake on floor ${fmt(S.floor)}, whole, where you hit.`;
      logJ(`Woke on floor ${fmt(S.floor)}, ${fmt(L.fallen)} floors below where I jumped.`);
      storyEvent('landed', { fallen: L.fallen });
    } else if (deadInFall) { PL.falling = true; PL.vy = -TERMINAL; sub = 'You wake whole, and still falling.'; logJ('Woke whole — still falling.'); }
    else { sub = 'You wake whole, where you died.'; logJ('Woke whole, where I died.'); }
    S.dead = null; S.landing = null; PL.dead = false;
  }
  if (!S.fall) { PL.vy = 0; PL.vx = 0; PL.vz = 0; PL.onGround = true; PL.falling = false; PL.peak = S.y; }
  if (S.fall) { PL.falling = true; PL.vy = -TERMINAL; $('#fallhud').hidden = false; if (!S.flags.abyss) { S.flags.abyss = 1; momentAfter = 'abyss'; } if (!wasDead) sub = 'The lights come on. You are still falling.'; }
  dark = false;
  worldOrigin(S.cx, S.cz, S.floor); updateWorld(S.x, S.y, S.z, !!S.fall); refreshBooks(true);
  storyDawn();
  updateGroundBooks(); updateCarry(); showHeld(S.carried ? parseKey(S.carried) : null);
  save();
  $('#fade-t').textContent = dateLine(); $('#fade-s').textContent = sub;
  setTimeout(() => {
    $('#fade').classList.remove('on'); nightBusy = false; pauseSuppressed = false; $('#hurt').style.opacity = 0;
    if (momentAfter) { const m = momentAfter; momentAfter = null; showMoment(m); }
    else if (MODE === 'play') showClickHint();
  }, 2300);
}
function updateTime(dt) {
  if (nightBusy || PL.dead) return;
  S.time += dt / HOUR_SEC;
  const hrs = dt / HOUR_SEC;
  S.thirst = clamp(S.thirst + hrs / 60, 0, 1); S.hunger = clamp(S.hunger + hrs / 120, 0, 1);
  S.drunk = Math.max(0, S.drunk - hrs * 0.12);
  if (S.thirst >= 1) { die('thirst'); return; }
  if (S.drunk >= 1.6) { die('drink'); return; }
  if (S.hp < 100) S.hp = Math.min(100, S.hp + dt * 1.2);
  let lampT = 1;
  if (S.time >= LIGHTS_OFF - 0.25 && S.time < LIGHTS_OFF) { lampT = 0.8 + 0.2 * Math.sin(performance.now() * 0.03) * Math.sin(performance.now() * 0.011); if (S.flags.dimWarn !== S.day) { S.flags.dimWarn = S.day; toast('The lights are flickering. The dark is a few minutes away.'); } }
  if (S.time >= LIGHTS_OFF) {
    lampT = 0;
    if (!dark) { dark = true; SFX.thunk(); toast(S.fall ? 'The lights go out. You fall in total darkness.' : 'The lights go out, all of them, all at once. Only the step lamps still glow. Find a bed (E) or lie down (Z).', true); if (S.fall) setTimeout(() => sleepNow('fall'), 2500); }
    if (S.time >= LIGHTS_OFF + 1) sleepNow('dark');
  }
  dayK += (lampT - dayK) * Math.min(1, dt * (lampT < dayK ? 4 : 1));
}

/* ==========================================================================
   Books on the shelves around you: filled from their addresses
   ========================================================================== */
function instAddr(inst) { return { f: inst.lv, x: inst.pl.cx, z: inst.pl.cz }; }
function fillRoomBooks(inst, near) {
  const a = instAddr(inst), over = roomHasOver(a.f, a.x, a.z);
  fillShelves(inst, (si, p) => {
    const home = { f: a.f, x: a.x, z: a.z, k: si, p }, L = bookLook(home);
    let show = L;
    if (over) { const c = slotContent(home); show = c ? (sameId(c, home) ? L : bookLook(c)) : null; }
    return { w: L.w, L: show };
  }, near);
  inst.booksFor = a.f + ':' + a.x + ':' + a.z;
}
/* real books on the shelves within reach (re-filled as you walk); painted spines beyond */
function refreshBooks(force) {
  const R = WORLD.bookR;
  for (const inst of WORLD.inst.values()) {
    const b = inst.box, dx = Math.max(b[0] - S.x, 0, S.x - b[3]), dz = Math.max(b[2] - S.z, 0, S.z - b[5]);
    const sameLevel = S.y + 1 > b[1] + 1.5 && S.y + 1 < b[4];
    const near = Math.hypot(dx, dz) < R && sameLevel && !(S.fall && -PL.vy > 15);
    const a = instAddr(inst), key = a.f + ':' + a.x + ':' + a.z;
    if (!near) { if (inst.books) clearShelves(inst); continue; }
    _v.set(S.x, S.y, S.z).applyMatrix4(inst.inv);
    const moved = !inst.fillAt || Math.hypot(_v.x - inst.fillAt.x, _v.z - inst.fillAt.z) > 2.5 || Math.abs(_v.y - inst.fillAt.y) > 2;
    if (!inst.books || inst.booksFor !== key || force || moved) {
      clearShelves(inst);
      inst.fillAt = { x: _v.x, y: _v.y, z: _v.z, r: R };
      fillRoomBooks(inst, inst.fillAt);
    }
  }
}
function refreshSlot(id) {
  for (const inst of WORLD.inst.values()) {
    if (!inst.books) continue;
    const a = instAddr(inst);
    if (a.f !== id.f || a.x !== id.x || a.z !== id.z) continue;
    const c = slotContent(id);
    setBook(inst, id.k, id.p, c ? bookLook(c) : null);
  }
}

/* ==========================================================================
   What's under the crosshair
   ========================================================================== */
let TARGET = null;
const _o = new THREE.Vector3(), _d = new THREE.Vector3(), _sv = new THREE.Vector3();
function raySphere(cx, cy, cz, r) { const ox = _o.x - cx, oy = _o.y - cy, oz = _o.z - cz, b = ox * _d.x + oy * _d.y + oz * _d.z, c = ox * ox + oy * oy + oz * oz - r * r, h = b * b - c; if (h < 0) return Infinity; const t = -b - Math.sqrt(h); return t > 0 ? t : Infinity; }
const SPOT_R = { kiosk: [1.1, 0.75], bed: [0.35, 0.8], bath: [1.1, 0.7], plaque: [1.6, 0.8] };
function findTarget() {
  if (PL.dead) return null;
  camera.getWorldPosition(_o); camera.getWorldDirection(_d);
  const st = storyTargets(); if (st) return st;
  if (S.fall) return null;
  const wall = rayHit(_o, _d, 3.4);
  let best = null, bt = Math.min(3.0, wall + 0.1);
  const b = bookRay(_o, _d, bt);
  if (b) {
    bt = b.t; const a = instAddr(b.inst), slot = { f: a.f, x: a.x, z: a.z, k: b.si, p: b.p };
    best = { kind: 'slot', slot, book: slotContent(slot), inst: b.inst };
  }
  for (const gb of S.ground) { if (!gb._m || !gb._m.visible) continue; const p = gb._m.position, t = raySphere(p.x, p.y, p.z, 0.28); if (t < bt) { bt = t; best = { kind: 'ground', gb }; } }
  for (const inst of WORLD.inst.values()) {
    const bx = inst.box; if (S.x < bx[0] - 3 || S.x > bx[3] + 3 || S.z < bx[2] - 3 || S.z > bx[5] + 3 || S.y < bx[1] - 3 || S.y > bx[4]) continue;
    for (const sp of inst.pf.meta.spots) {
      const R = SPOT_R[sp.k]; if (!R) continue;
      instPoint(inst, sp.p, _sv);
      const t = raySphere(_sv.x, _sv.y + R[0], _sv.z, R[1]);
      if (t < bt && t < 3.0) { bt = t; best = { kind: sp.k, inst, spot: sp }; }
    }
  }
  const sh = shaftNear();
  if (sh && !sh.inside && sh.d < 1.5) {
    _v.set(S.x, S.y, S.z).applyMatrix4(sh.room.inv);
    const ld = _w.copy(_d).transformDirection(sh.room.inv), tx = sh.edge[0] - _v.x, tz = sh.edge[1] - _v.z, tl = Math.hypot(tx, tz) || 1;
    if ((ld.x * tx + ld.z * tz) / tl > 0.45 && ld.y < 0.35) best = { kind: 'edge' };
  }
  return best;
}
function describeTarget(t) {
  const P_ = $('#prompt'), ch = $('#crosshair');
  ch.classList.toggle('hot', !!t);
  if (!t) { P_.innerHTML = PL.edgeArm > 0 ? '<div class="k">[E] again to let go · step back to stay</div>' : dark && !S.fall ? '<div class="k">[Z] Lie down and sleep</div>' : PL.swim ? '<div class="k">Space: rise · C: dive</div>' : ''; return; }
  let a = '', b = '';
  if (t.kind === 'slot') {
    if (t.book) {
      const out = !sameId(t.book, t.slot);
      a = esc(addrLine(t.book)) + (out ? '<br><span class="warm">out of place — it will go home at dawn</span>' : '');
      b = S.carried ? 'Your hands are full · G to drop the book you hold' : '[E] Take it and read';
    } else { a = 'An empty slot · ' + esc(addrLine(t.slot)); b = S.carried ? '[E] Put the book you hold here' : 'Someone took this one. It will be back at dawn.'; }
  } else if (t.kind === 'ground') { a = esc(addrLine(parseKey(t.gb.id))) + '<br>lying on the floor'; b = S.carried ? 'Your hands are full' : '[E] Pick it up'; }
  else if (t.kind === 'kiosk') { a = 'A kiosk, glowing softly'; b = '[E] Ask for food or drink'; }
  else if (t.kind === 'bed') { a = 'A narrow bed in an alcove'; b = S.time >= 17 || dark ? '[E] Sleep until the lights come on' : 'Beds are for the evening (after 17:00).'; }
  else if (t.kind === 'bath') { a = 'The washroom'; b = '[E] Go in'; }
  else if (t.kind === 'plaque') { a = 'A brass plaque, and a slot beneath it'; b = S.carried ? '[E] Post the book you hold through the slot' : '[E] Read the plaque'; }
  else if (t.kind === 'edge') { a = 'The parapet. Below it, the shaft goes down past every floor anyone has counted.'; b = PL.edgeArm > 0 ? '[E] again to let go · step back to stay' : '[E] Climb over' + (S.carried ? ' · [G] Drop the book in' : ''); }
  else if (t.kind === 'trace') { a = TRACE_TEXT[t.it.k]; b = t.it.k === 'book' ? (S.carried ? 'Your hands are full' : '[E] Read where they left off') : ''; }
  P_.innerHTML = `<div class="t">${a}</div><div class="k">${b}</div>`;
}

/* ==========================================================================
   Actions
   ========================================================================== */
function act(kind) {
  if (PL.dead || nightBusy) return;
  const t = TARGET;
  if (kind === 'read') { if (S.carried) openReader(parseKey(S.carried)); else toast('You aren’t holding a book. Look at one and press E.'); return; }
  if (kind === 'consume') { if (S.item) consumeItem(S.item); return; }
  if (kind === 'sleep') {
    if (S.fall) { sleepNow('fall'); return; }
    if (PL.swim) { toast('Not in the water.'); return; }
    if (dark || S.time >= 21) { sleepNow('floor'); return; }
    toast('You aren’t tired. Nobody sleeps before the lights go out here — there is too much day to get through.'); return;
  }
  if (kind === 'drop') {
    if (!S.carried) return;
    const id = parseKey(S.carried);
    if (S.fall) { toast('It tumbles away from you and is gone. At dawn it will be back on its shelf.'); S.carried = null; showHeld(null); updateCarry(); return; }
    if (t && t.kind === 'edge') {
      const sh = shaftNear(); const dir = new THREE.Vector3();
      if (sh) { dir.set(sh.cx - sh.edge[0], 0, sh.cz - sh.edge[1]).normalize().transformDirection(sh.room.m); }
      throwBookVisual(id, S.x - Math.sin(S.yaw) * 0.5, S.y + 1.3, S.z - Math.cos(S.yaw) * 0.5, dir.x * 2.5, dir.z * 2.5);
      S.carried = null; S.stats.thrown++; showHeld(null); updateCarry(); SFX.book();
      if (S.stats.thrown === 1) { logJ('Dropped a searched book down the well. It fell until the dark had it.'); toast('It falls end over end until the dark takes it. Dawn will put it back on its shelf.'); }
      save(); return;
    }
    const fx = -Math.sin(S.yaw) * 0.55, fz = -Math.cos(S.yaw) * 0.55;
    const p = _pp.set(S.x + fx, S.y + 0.4, S.z + fz); pushSphere(p, 0.15, true);
    const gy = groundAt(p.x, S.y + 0.4, p.z, 0.2, 2.0);
    if (gy === -Infinity) { toast('There is nowhere to put it down there.'); return; }
    S.ground.push({ id: S.carried, cx: S.cx, cz: S.cz, floor: S.floor, x: p.x, y: gy, z: p.z, yaw: Math.random() * 6 });
    if (S.ground.length > 120) S.ground.shift();
    S.carried = null; SFX.book(); showHeld(null); updateCarry(); updateGroundBooks(); save(); return;
  }
  if (!t) { if (PL.edgeArm > 0) goOver(); return; }
  if (t.kind === 'trace') {
    if (t.it.k === 'book' && !S.carried) { openReader(t.it.id); RD.pg = t.it.page; renderPage(); }
    else toast(TRACE_TEXT[t.it.k]);
    return;
  }
  if (t.kind === 'slot') {
    if (t.book) {
      if (S.carried) { toast('You can only carry one book. Put yours in an empty slot, or drop it with G.'); return; }
      S.over[keyOf(t.slot)] = ''; S.carried = keyOf(t.book); recountOver(); refreshSlot(t.slot); SFX.book(); updateCarry(); showHeld(t.book);
      if (!S.flags.firstBook) { S.flags.firstBook = 1; logJ(`Took my first book from the shelves: ${addrLine(t.book)}.`); }
      openReader(t.book); save();
    } else if (S.carried) {
      const cid = parseKey(S.carried), own = sameId(cid, t.slot);
      if (own) delete S.over[keyOf(t.slot)]; else S.over[keyOf(t.slot)] = S.carried;
      S.carried = null; recountOver(); refreshSlot(t.slot); SFX.book(); updateCarry(); showHeld(null); save();
      if (!own) toast('Shelved out of place. At dawn it will be back where it belongs.');
    }
    return;
  }
  if (t.kind === 'ground') {
    if (S.carried) { toast('Your hands are full.'); return; }
    S.carried = t.gb.id; S.ground.splice(S.ground.indexOf(t.gb), 1); SFX.book(); updateCarry(); updateGroundBooks(); showHeld(parseKey(S.carried)); openReader(parseKey(S.carried)); save(); return;
  }
  if (t.kind === 'kiosk') { openKiosk(); return; }
  if (t.kind === 'bed') { if (S.time < 17 && !dark) { toast('You aren’t tired yet.'); return; } sleepNow('bed'); return; }
  if (t.kind === 'bath') { S.flags.bath = (S.flags.bath || 0) + 1; toast(['A clean white room, tiled to the ceiling. The water is cold and perfect. There is no mirror.', 'You wash your face. The towel is fresh. It is always fresh.', 'Somebody has written on the tiles in pencil: “still here.” By morning it will be gone.'][S.flags.bath % 3]); return; }
  if (t.kind === 'plaque') {
    if (S.carried) {
      const id = parseKey(S.carried); S.carried = null; showHeld(null); updateCarry(); SFX.book();
      S.flags.slotted = (S.flags.slotted || 0) + 1;
      toast(S.flags.slotted === 1 ? 'You post the book through the slot. It is swallowed with a soft click. You wait. Nothing happens. Nothing at all.' : 'The slot takes it with a soft click. Nothing happens.');
      logJ(`Posted ${addrLine(id)} through the slot. It was not my life.`); save(); return;
    }
    openSign(); return;
  }
  if (t.kind === 'edge') {
    if (PL.edgeArm > 0) { goOver(); return; }
    PL.edgeArm = 3; toast('You swing a leg over the parapet. The air below is cool. [E] again to let go.'); return;
  }
}
function goOver() { PL.edgeArm = 0; startFall(false, true); }

/* ==========================================================================
   HUD
   ========================================================================== */
function toast(text, bad) { const el = document.createElement('div'); el.className = 'toast' + (bad ? ' bad' : ''); el.textContent = text; $('#toasts').appendChild(el); setTimeout(() => el.remove(), 5600); while ($('#toasts').children.length > 3) $('#toasts').firstChild.remove(); }
function updateCarry() {
  const el = $('#carry');
  if (!S.carried && !S.item) { el.hidden = true; return; }
  el.hidden = false; let h = '';
  if (S.carried) { const id = parseKey(S.carried), L = bookLook(id); h += `<div class="spine" style="background:${cssCol(L.col)}"></div><div class="ct">Holding a book<br><span>${esc(addrLine(id))}</span><br><span>R read · G drop (at a parapet: let it fall) · E into an empty slot</span></div>`; }
  if (S.item) h += `<div class="ct"${S.carried ? ' style="border-left:1px solid var(--edge);padding-left:10px"' : ''}>${esc(S.item.name)}<br><span>Q ${S.item.drink ? 'drink' : 'eat'} it</span></div>`;
  el.innerHTML = h;
}
let hudT = 0;
function updateHUD(dt) {
  hudT -= dt; if (hudT > 0) return; hudT = 0.1;
  $('#h-floor').textContent = fmt(S.floor);
  const r = PL.room;
  let where;
  if (S.fall) where = r ? `Falling through ${esc(r.pf.meta.meta.label)}` : 'Falling';
  else if (r) where = `${esc(r.pf.meta.meta.label)} · Room <b>${esc(roomName(r.pl.cx, r.pl.cz))}</b>`;
  else where = 'Between rooms';
  if (TARGET && TARGET.kind === 'slot') where += ` · Shelf <b>${TARGET.slot.k + 1}</b> · Book <b>${TARGET.slot.p + 1}</b>`;
  $('#h-case').innerHTML = where;
  $('#h-walk').innerHTML = `Walked <b>${S.stats.dist < 1000 ? fmt(S.stats.dist) + ' m' : (S.stats.dist / 1000).toFixed(2) + ' km'}</b>` + (S.stats.rooms ? ` · <b>${fmt(S.stats.rooms)}</b> rooms` : '');
  $('#h-day').textContent = dateLine();
  $('#h-clock').textContent = clock();
  $('#h-lamps').textContent = dark ? 'Lights out' : S.time > LIGHTS_OFF - 0.25 ? 'Lights flickering' : 'Lights out at 22:00';
  const bar = (id, v, label) => { const e = $(id); e.querySelector('i').style.width = (v * 100) + '%'; e.querySelector('i').style.background = v > 0.8 ? 'var(--oxide)' : 'var(--lamp)'; e.title = label; };
  bar('#h-hunger', S.hunger, S.hunger > 0.85 ? 'Starving' : S.hunger > 0.5 ? 'Hungry' : 'Fed');
  bar('#h-thirst', S.thirst, S.thirst > 0.8 ? 'Parched — you will die of thirst' : S.thirst > 0.5 ? 'Thirsty' : 'Not thirsty');
  if (S.fall) {
    const fl = S.fall.startFloor - S.floor;
    $('#f-floors').textContent = fmt(fl) + (fl === 1 ? ' floor' : ' floors');
    $('#f-sub').textContent = `${Math.round(-PL.vy)} m/s · day ${S.fall.days + 1} of the fall · WASD steer — hit a floor to stop · ${isTouch ? 'Jump' : 'Space'}: sleep till the lights come on`;
  }
  describeTarget(TARGET);
}
function showClickHint() { $('#clickhint').hidden = isTouch || locked || MODE !== 'play'; }

/* ==========================================================================
   Reader
   ========================================================================== */
const RD = { id: null, pg: 0, hl: null };
function openReader(id) {
  RD.id = id; RD.hl = null; RD.pg = 0;
  const k = keyOf(id);
  if (!S.seen[k]) { S.seen[k] = 1; S.stats.books++; const ks = Object.keys(S.seen); if (ks.length > 3000) delete S.seen[ks[0]]; }
  $('#r-title').textContent = `Floor ${fmt(id.f)}, room ${roomName(id.x, id.z)}`;
  $('#r-addr').innerHTML = `Shelf <b>${id.k + 1}</b> · Book <b>${id.p + 1}</b><br>410 pages · 40 lines · 80 characters<br>One of 10<sup>${fmt(LOG10_BOOKS)}</sup> books.`;
  $('#r-results').innerHTML = ''; $('#r-qnote').textContent = ''; $('#r-q').value = '';
  openOverlay('#reader'); renderPage(); SFX.page();
}
function renderPage() {
  const id = RD.id, s = pageText(id, RD.pg), fr = fragOf(id), frHere = fr && fr.page === RD.pg;
  const marks = [];
  if (frHere) marks.push([fr.at, fr.at + fr.text.length, 'frag']);
  if (RD.hl && RD.hl.pg === RD.pg) marks.push([RD.hl.at, RD.hl.at + RD.hl.len, '']);
  marks.sort((a, b) => a[0] - b[0]);
  let out = '';
  for (let line = 0; line < LINES; line++) {
    const a = line * COLS, b = a + COLS; let pos = a, row = '';
    for (const [m0, m1, cls] of marks) { const s0 = Math.max(m0, a), s1 = Math.min(m1, b); if (s0 >= s1 || s0 < pos) continue; row += esc(s.slice(pos, s0)) + `<mark${cls ? ' class="' + cls + '"' : ''}>` + esc(s.slice(s0, s1)) + '</mark>'; pos = s1; }
    row += esc(s.slice(pos, b)); out += row + (line < LINES - 1 ? '\n' : '');
  }
  $('#page').innerHTML = out;
  $('#r-pg').value = RD.pg + 1;
  $('#r-ph-l').textContent = `Floor ${fmt(id.f)} · room ${roomName(id.x, id.z)} · shelf ${id.k + 1} · book ${id.p + 1}`;
  $('#r-ph-r').textContent = `${RD.pg + 1}`;
  const fbox = $('#r-frag');
  if (frHere) {
    const have = S.frags.some(f => f.addr === keyOf(id));
    fbox.innerHTML = `<div class="fragbox"><div class="eyebrow">Words, out of the noise</div><q>${esc(fr.text)}</q><div><button class="btn primary" id="r-rec" ${have ? 'disabled' : ''}>${have ? 'Recorded in your journal' : 'Record in journal'}</button></div></div>`;
    if (!have) $('#r-rec').onclick = () => { S.frags.push({ text: fr.text, addr: keyOf(id), page: fr.page + 1, day: S.day }); logJ(`Found words in a book: “${fr.text}” (${addrLine(id)}, page ${fr.page + 1}).`); SFX.chime(); renderPage(); save(); };
    if (!S.flags['saw' + keyOf(id)]) { S.flags['saw' + keyOf(id)] = 1; SFX.chime(); }
  } else fbox.innerHTML = '';
  // someone else read this book before you, and wrote in the margin
  const note = marginNote(id, RD.pg), nb = $('#r-note');
  nb.hidden = !note; if (note) { nb.textContent = note; sawNote(note, id, RD.pg); }
  S.stats.pages++;
}
function turnPage(d) { RD.pg = mod(RD.pg + d, PAGES); renderPage(); SFX.page(); }
$('#r-prev').onclick = () => turnPage(-1); $('#r-next').onclick = () => turnPage(1);
$('#r-pg').addEventListener('change', () => { const v = parseInt($('#r-pg').value, 10); if (v >= 1 && v <= PAGES) { RD.pg = v - 1; renderPage(); SFX.page(); } else $('#r-pg').value = RD.pg + 1; });
$('#r-pg').addEventListener('keydown', e => { if (e.key === 'Enter') e.target.blur(); });
function runSearch() {
  const q = $('#r-q').value; if (!q) return;
  S.stats.searches++;
  const res = []; let total = 0;
  for (let pg = 0; pg < PAGES; pg++) { const s = pageText(RD.id, pg); let i = s.indexOf(q); while (i !== -1) { total++; if (res.length < 200) res.push({ pg, at: i }); i = s.indexOf(q, i + 1); } }
  const expect = 1312000 / Math.pow(95, q.length);
  $('#r-qnote').textContent = `${fmt(total)} match${total === 1 ? '' : 'es'} in 410 pages. By chance alone you'd expect ${expect >= 0.01 ? 'about ' + expect.toFixed(expect < 1 ? 2 : 1) : 'one in ' + fmt(1 / expect) + ' books'}.`;
  $('#r-results').innerHTML = res.slice(0, 60).map((r, i) => `<button data-i="${i}">page ${r.pg + 1}, line ${Math.floor(r.at / COLS) + 1}</button>`).join('');
  [...$('#r-results').children].forEach(b => b.onclick = () => { const r = res[+b.dataset.i]; RD.pg = r.pg; RD.hl = { pg: r.pg, at: r.at, len: q.length }; renderPage(); SFX.page(); });
}
$('#r-go').onclick = runSearch; $('#r-q').addEventListener('keydown', e => { if (e.key === 'Enter') runSearch(); });

/* ==========================================================================
   Kiosk — "any food or drink you name"; the washroom; the plaque
   ========================================================================== */
let kioskItem = null;
const SUGG = ['Water', 'Coffee', 'Bread and butter', 'Hot soup', 'Whiskey', 'Milk', 'Pancakes', 'My mother’s pot roast'];
$('#k-sugg').innerHTML = SUGG.map(s => `<button>${esc(s)}</button>`).join('');
[...$('#k-sugg').children].forEach(b => b.onclick = () => { $('#k-in').value = b.textContent; kioskAsk(); });
function openKiosk() { $('#k-out').textContent = ''; $('#k-food').hidden = true; $('#k-in').value = ''; openOverlay('#kiosk'); setTimeout(() => $('#k-in').focus(), 30); }
function classify(q) {
  const s = q.toLowerCase();
  const alcohol = /(whisk|bourbon|scotch|vodka|gin\b|rum\b|tequila|beer|ale\b|lager|wine|champagne|brandy|cognac|sake|mead|cider|martini|margarita|cocktail|liquor|schnapps|absinthe|moonshine)/.test(s);
  const coffee = /(coffee|espresso|latte|cappuccino|americano|mocha)/.test(s);
  const drink = alcohol || coffee || /(water|tea\b|milk|juice|soda|cola|pop\b|lemonade|drink|cocoa|chocolate milk|smoothie|shake|broth)/.test(s);
  return { drink, alcohol, coffee };
}
function kioskAsk() {
  const q = $('#k-in').value.trim(); if (!q) return;
  const c = classify(q); kioskItem = { name: q.charAt(0).toUpperCase() + q.slice(1), ...c };
  SFX.chime(); S.flags.usedKiosk = 1;
  const tails = ['exactly as you remember it.', 'perfect, in the way nothing was perfect before.', 'on a plain white plate.', 'and it smells like a kitchen you once stood in.', 'warm, or cold, just as it should be.'];
  $('#k-out').textContent = `A small hatch slides open. ${kioskItem.name}, ${tails[strHash(q + S.day) % tails.length]}`;
  $('#k-eat').textContent = c.drink ? 'Drink it' : 'Eat it';
  $('#k-food').hidden = false; $('#k-keep').disabled = !!S.item;
}
function consumeItem(it) {
  if (it.drink) { S.thirst = Math.max(0, S.thirst - (it.alcohol ? 0.25 : it.coffee ? 0.45 : 0.9)); SFX.drink(); } else S.hunger = Math.max(0, S.hunger - 0.7);
  if (it.alcohol) { S.drunk += 0.38; if (!S.flags.firstDrink) { S.flags.firstDrink = 1; logJ(`Had a drink: ${it.name}. Another commandment I used to keep.`); } }
  if (it.coffee && !S.flags.coffee) { S.flags.coffee = 1; logJ('Asked for coffee. Fifty years of not drinking it, and my first cup is in Hell. It was very good — which felt like one more thing I had been wrong about.'); toast('Your first coffee. It is very good. That feels like one more thing you were wrong about.'); }
  if (S.item === it) S.item = null;
  updateCarry(); save();
}
$('#k-ask').onclick = kioskAsk; $('#k-in').addEventListener('keydown', e => { if (e.key === 'Enter') kioskAsk(); });
$('#k-eat').onclick = () => { consumeItem(kioskItem); $('#k-out').textContent = kioskItem.drink ? (kioskItem.alcohol ? (S.drunk > 1.1 ? 'The room tilts, and keeps tilting.' : 'It goes down warm.') : 'You drink. It is very good. It is always very good.') : 'You eat. It is very good. It is always very good.'; $('#k-food').hidden = true; };
$('#k-keep').onclick = () => { S.item = kioskItem; $('#k-out').textContent = 'You take it with you. (Q to have it later.)'; $('#k-food').hidden = true; updateCarry(); save(); };
function openSign() { $('#k-out').textContent = ''; showPlaque(); }
function showPlaque() { openOverlay('#plaque'); }

/* ==========================================================================
   Captions (for things that happen around you) and moments (chapter cards)
   ========================================================================== */
let CAP = null;
function showCaptions(lines, done) { CAP = { lines, i: -1, t: 0, done }; nextCaption(); }
function nextCaption() {
  if (!CAP) return;
  CAP.i++;
  const el = $('#captions');
  if (CAP.i >= CAP.lines.length) { el.hidden = true; const d = CAP.done; CAP = null; if (d) d(); return; }
  const L = CAP.lines[CAP.i]; if (L.fx) L.fx();
  el.hidden = false; el.innerHTML = (L.who ? `<b>${esc(L.who)}</b>` : '') + `<span>${esc(L.text)}</span>`;
  CAP.t = 2.2 + L.text.length * 0.045;
}
function updateCaptions(dt) { if (!CAP) return; CAP.t -= dt; if (CAP.t <= 0) nextCaption(); }
function showMoment(key) {
  const m = MOMENTS[key]; if (!m) return;
  $('#m-art').style.backgroundImage = `url(assets/${m.art}.jpg)`;
  $('#m-eye').textContent = m.eyebrow; $('#m-title').textContent = m.title; $('#m-text').textContent = m.text;
  openOverlay('#moment');
}
function closeMoment() { closeOverlays(); requestLock(); }
$('#m-go').onclick = closeMoment;

/* ==========================================================================
   Journal
   ========================================================================== */
let jTab = 'threads';
function openJournal() { renderJournal(); openOverlay('#journal'); }
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => { jTab = b.dataset.tab; renderJournal(); });
function renderJournal() {
  document.querySelectorAll('.tabs button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === jTab));
  $('#j-eye').textContent = `${S.name} · ${dateLine()} · ${clock()}`;
  const pane = $('#j-pane'); let h = '';
  if (jTab === 'threads') {
    const act = activeThreads(), done = THREADS.filter(t => t.show() && t.done());
    h = `<ul class="threads">${act.map(t => `<li>${esc(t.text())}</li>`).join('') || '<li class="dim">Nothing pressing. There is only the search.</li>'}</ul>`;
    if (done.length) h += `<h3 class="jh">Done</h3><ul class="threads done">${done.map(t => `<li>${esc(t.text())}</li>`).join('')}</ul>`;
  } else if (jTab === 'log') h = `<ol class="log">${S.journal.slice().reverse().map(e => `<li><span>Day ${fmt(e.d)}<br>${e.t}</span><div>${esc(e.text)}</div></li>`).join('') || '<li><span></span><div>Nothing yet.</div></li>'}</ol>`;
  else if (jTab === 'frags') h = S.frags.length ? `<div class="frags">${S.frags.map(f => `<blockquote><q>${esc(f.text)}</q><cite>${esc(addrLine(parseKey(f.addr)))} · page ${f.page} · day ${f.day}</cite></blockquote>`).join('')}</div>` : '<p class="note" style="max-width:52ch">No readable words yet. Most pages are noise from edge to edge. When a sentence surfaces, record it here — the University will want it.</p>';
  else if (jTab === 'notes') {
    const ns = S.notes || [];
    h = ns.length ? `<div class="frags">${ns.map(n => `<blockquote class="hand"><q>${esc(n.text)}</q><cite>${esc(addrLine(parseKey(n.addr)))} · page ${n.page} · day ${n.day}</cite></blockquote>`).join('')}</div>` : '<p class="note">No one has written to you yet. Some books have notes in their margins, left by whoever read them before.</p>';
  } else if (jTab === 'nums') {
    const st = S.stats, items = [['Days', S.day], ['Books opened', st.books], ['Pages read', st.pages], ['Books dropped down a well', st.thrown], ['Fragments found', S.frags.length], ['Walked', st.dist < 1000 ? fmt(st.dist) + ' m' : (st.dist / 1000).toFixed(2) + ' km'], ['Rooms seen', st.rooms || 0], ['Swum', fmt(st.swum || 0) + ' m'], ['Floors climbed', st.climbed], ['Floors fallen', st.fallen], ['Longest fall', fmt(st.maxFall) + ' fl.'], ['Days spent falling', st.daysFalling], ['Deaths', st.deaths]];
    h = `<div class="stats">${items.map(([k, v]) => `<div class="stat"><div class="v">${typeof v === 'number' ? fmt(v) : v}</div><div class="k">${k}</div></div>`).join('')}</div>`;
  } else if (jTab === 'odds') {
    const n = Math.max(S.stats.books, 1), frac = LOG10_BOOKS - Math.log10(n), lb = lifeBook(), sent = 20 * Math.log10(95) - Math.log10(1312000);
    h = `<div class="odds">
      <p>Books in the library: <span class="num">95<sup>1,312,000</sup></span> — about <span class="num">10<sup>${fmt(LOG10_BOOKS)}</sup></span>. Written out, that number has <span class="num">${fmt(DIGITS)}</span> digits.</p>
      <p>You have opened <span class="num">${fmt(S.stats.books)}</span>. That is roughly one book in <span class="num">10<sup>${fmt(frac)}</sup></span> — the same as none, to every decimal place anyone could print.</p>
      <p>Master Took puts the library at about <span class="num">7.16 × 10<sup>1,297,369</sup></span> light-years, wide and deep. Every room you have walked through is a rounding error on a rounding error.</p>
      <p>The chance that the next book you open is yours: <span class="num">1 in 10<sup>${fmt(LOG10_BOOKS)}</sup></span>. Opening one book a second since the Big Bang would change that exponent by about 17.</p>
      <h3>Where this game lies to you</h3>
      <p>In a truly random library, a particular twenty-character sentence turns up about once in <span class="num">10<sup>${Math.round(sent)}</sup></span> books. Here, one book in ${FRAG_RATE} carries a readable fragment. That is the game’s one mercy, and you should know it is one. Short strings are honest: search any book for a three-letter word and you will usually find one or two, just as chance predicts.</p>
      <p>The book’s library is one gallery, repeated forever. This one dreams: vaults, towers, wells, sunken courts and labyrinths, rearranging themselves as you walk. The books are the same books.</p>
      <p class="note">For the record, your own book is on a floor whose number begins ${lb.lead}… and runs to about ${fmt(lb.digits)} digits. Nobody here could tell you that; the game can.</p>
    </div>`;
  }
  pane.innerHTML = h;
}

/* ==========================================================================
   Overlays, pause, title, prologue
   ========================================================================== */
function openOverlay(sel) {
  document.querySelectorAll('.overlay').forEach(o => o.hidden = true);
  $(sel).hidden = false; MODE = 'ui'; pauseSuppressed = true;
  if (document.pointerLockElement) document.exitPointerLock();
  setTimeout(() => { pauseSuppressed = false; }, 60);
  $('#touch').hidden = true;
}
function closeOverlays() {
  document.querySelectorAll('.overlay').forEach(o => o.hidden = true);
  MODE = 'play'; save(); $('#touch').hidden = !isTouch; showClickHint();
}
document.querySelectorAll('[data-close]').forEach(b => b.onclick = () => { closeOverlays(); requestLock(); });
document.querySelectorAll('.overlay').forEach(o => o.addEventListener('mousedown', e => { if (e.target === o && o.id !== 'moment') closeOverlays(); }));
function openPause() {
  if (MODE !== 'play') return;
  $('#s-sens').value = S.settings.sens; $('#s-vol').value = S.settings.vol; $('#s-mus').value = musicLevel(); $('#s-q').value = S.settings.q; $('#s-gfx').value = S.settings.gfx; $('#s-hints').checked = S.settings.hints !== 0; syncOut();
  $('#confirm-reset').hidden = true;
  document.querySelectorAll('.overlay').forEach(o => o.hidden = true);
  $('#pause').hidden = false; MODE = 'pause'; $('#touch').hidden = true;
}
function resume() { $('#pause').hidden = true; MODE = 'play'; $('#touch').hidden = !isTouch; requestLock(); showClickHint(); }
function syncOut() { $('#o-sens').textContent = (+S.settings.sens).toFixed(1); $('#o-vol').textContent = Math.round(S.settings.vol * 100); $('#o-mus').textContent = Math.round(musicLevel() * 100); $('#o-q').textContent = Math.round(S.settings.q * 100) + '%'; $('#o-gfx').textContent = ['Low', 'Medium', 'High'][S.settings.gfx]; }
$('#s-sens').oninput = e => { S.settings.sens = +e.target.value; syncOut(); save(); };
$('#s-vol').oninput = e => { S.settings.vol = +e.target.value; if (AU.out) AU.out.gain.value = S.settings.vol; syncOut(); save(); };
$('#s-mus').oninput = e => { S.settings.music = +e.target.value; musicMix(); syncOut(); save(); };
$('#s-q').oninput = e => { S.settings.q = +e.target.value; applyQuality(); syncOut(); save(); };
$('#s-gfx').oninput = e => { S.settings.gfx = +e.target.value; applyGfx(); syncOut(); save(); };
$('#s-hints').onchange = e => { S.settings.hints = e.target.checked ? 1 : 0; updateThreadsHUD(); save(); };
$('#p-resume').onclick = resume;
$('#p-journal').onclick = () => { $('#pause').hidden = true; MODE = 'play'; openJournal(); };
$('#p-title').onclick = () => { save(); $('#pause').hidden = true; showTitle(); };
$('#p-reset').onclick = () => { $('#confirm-reset').hidden = false; };
$('#p-reset-no').onclick = () => { $('#confirm-reset').hidden = true; };
$('#p-reset-yes').onclick = () => { try { localStorage.removeItem(SAVE_KEY); } catch (e) {} S = null; $('#pause').hidden = true; showTitle(); };
function applyGfx() {
  const g = gfxSettings().gfx;
  WU.uProbeOn.value = g >= 1 ? 1 : 0;
  for (const pf of PREFABS.values()) if (pf && pf.waterMat) pf.waterMat.uniforms.uSSR.value = g >= 2 ? 1 : 0;
  WORLD.radius = g >= 2 ? 3 : 2; WORLD.bookR = g >= 2 ? 9 : g >= 1 ? 7 : 5;
}
function showTitle() {
  MODE = 'title'; $('#captions').hidden = true; CAP = null; $('#title').hidden = false; $('#hud').hidden = true; $('#touch').hidden = true; $('#prologue').hidden = true;
  const sv = S || loadSave(); $('#b-continue').hidden = !sv;
  if (sv) $('#b-continue').textContent = `Continue — year ${fmt(sv.year)}, day ${fmt(sv.day)}`;
  titleWorld();
}
const PRO = [
  { who: '', text: 'You died. The cancer did what the doctors said it would, more or less on schedule.' },
  { who: '', text: 'Then: a waiting room. Fluorescent light. Plastic chairs. Other people, just as lost as you are.' },
  { who: 'Xandern', text: 'Welcome. I’m Xandern. I’ll be processing you today. Please keep your paperwork in order and your screaming to a minimum.' },
  { who: 'Xandern', text: 'I’m afraid the true religion was Zoroastrianism. Nobody is ever pleased to hear it. It’s nothing personal.' },
  { who: '', text: 'He calls Lester first — a Christian, certain of everything — and sends him through a door you are glad you cannot see beyond. Then Julia, an atheist, who seems mostly annoyed to be wrong.' },
  { who: 'Xandern', text: 'You are going somewhere else. Three things. One: if you die, you will be brought back. Two: your earthly covenants — marriage included — are dissolved.' },
  { who: 'Xandern', text: 'Three: find the book that tells your life, every word of it, without a single error, and post it through the slot. Then you may go. It is meant to teach you something. It is a punishment. It is not forever.' },
  { who: '', text: 'Then there is warm stone, and lamplight, and shelves, and a body that doesn’t hurt anymore.' },
];
let proI = 0;
$('#b-new').onclick = () => { if (!WORLD.ready) return; audioInit(); $('#title').hidden = true; $('#prologue').hidden = false; MODE = 'prologue'; proI = 0; showPro(); };
$('#b-continue').onclick = () => { if (!WORLD.ready) return; audioInit(); S = S || loadSave(); startPlay(false); };
function showPro() {
  const L = PRO[proI], t = $('#pro-t'); t.style.animation = 'none'; void t.offsetWidth; t.style.animation = '';
  t.textContent = L.text; $('#pro-who').textContent = L.who || ''; $('#pro-por').hidden = !L.who;
  $('#b-pro').textContent = proI === PRO.length - 1 ? 'Wake up' : 'Go on';
}
$('#b-pro').onclick = () => {
  if (proI < PRO.length - 1) { proI++; showPro(); return; }
  S = freshState(); logJ('Died of cancer. Was processed by a demon named Xandern. The true religion was Zoroastrianism.'); logJ('Woke alone beside a small stepped pit in a green room. I can remember every day of my life, exactly. That should make my book easy to recognise. It does not make it easier to find.');
  save(); startPlay(true);
};
function startPlay(first) {
  S.settings = Object.assign({ sens: 1, vol: 0.8, q: 1, gfx: 2, hints: 1 }, S.settings); PL.camY = null;
  recountOver(); applyQuality(); applyGfx();
  PL.dead = false; PL.vy = 0; PL.vx = 0; PL.vz = 0; PL.swim = false; $('#hurt').style.opacity = 0; nightBusy = false; dark = S.time >= LIGHTS_OFF;
  PL.falling = !!S.fall; $('#fallhud').hidden = !S.fall; if (S.fall) PL.vy = -TERMINAL;
  if (S.dead) { S.dead = null; S.landing = null; }
  worldOrigin(S.cx, S.cz, S.floor); updateWorld(S.x, S.y, S.z, !!S.fall);
  if (!S.fall) { const g = groundAt(S.x, S.y + 1, S.z, 1.2, 4); if (g > -Infinity) S.y = g; PL.onGround = true; PL.peak = S.y; }
  refreshBooks(true);
  placeNamed(); updateGroundBooks(); updateCarry(); showHeld(S.carried ? parseKey(S.carried) : null);
  $('#title').hidden = true; $('#prologue').hidden = true; $('#hud').hidden = false; $('#touch').hidden = !isTouch;
  MODE = 'play'; if (AU.out) AU.out.gain.value = S.settings.vol;
  dayK = dark ? 0 : 1; expoReset = true;
  if (first) showMoment('arrival'); else { requestLock(); showClickHint(); }
}
/* behind the title: the arrival room, a slow look round */
const TITLE_S = freshState();
function titleWorld() {
  worldOrigin(TITLE_S.cx, TITLE_S.cz, TITLE_S.floor);
  updateWorld(8, 1, 8, false);
  const bk = S; S = TITLE_S; S.x = 8; S.y = 0; S.z = 8; recountOver(); refreshBooks(true); S = bk;
}

/* ==========================================================================
   Main loop
   ========================================================================== */
let last = performance.now(), saveT = 0, perfT = 0, perfN = 0, perfSum = 0, bookT = 0, roomKeyNow = '';
function syncRoom() {
  const r = instAt(S.x, S.y + 0.5, S.z);
  PL.room = r;
  const k = r ? placeKey(r.pl) + (r.slot !== undefined ? '@' + (S.floor) : '') : '';
  if (k && k !== roomKeyNow) {
    roomKeyNow = k;
    if (!S.seen['room:' + k]) { S.seen['room:' + k] = 1; S.stats.rooms = (S.stats.rooms || 0) + 1; }
    if (r && !S.flags['saw' + r.pf.name]) { S.flags['saw' + r.pf.name] = 1; roomFirst(r.pf.name); }
  }
  // light where you stand, for the people and loose books; a little haze tinted by the room
  const av = r ? (dayK * (r.pf.meta.avg.day || 1) + (1 - dayK) * (r.pf.meta.avg.night || 0.05)) : 0.5;
  AMB.top.set(av * 1.15, av * 1.13, av * 1.1); AMB.col.set(av * 0.7, av * 0.72, av * 0.75);
  const fog = r && r.pf.name === 'backrooms' ? [0.36, 0.3, 0.22] : r && (r.pf.name === 'well' || r.pf.name === 'tower') ? [0.36, 0.32, 0.27] : [0.46, 0.41, 0.34];
  WU.uFogCol.value.setRGB(fog[0] * av, fog[1] * av, fog[2] * av);
  WU.uFogD.value = r && (r.pf.name === 'well' || r.pf.name === 'tower') ? 0.012 : r && r.pf.name === 'backrooms' ? 0.02 : 0.006;
  if (AU.ctx) {
    AU.hum.gain.value = 0;
    const mk = dark + ':' + !!S.fall; if (mk !== MUS.k) { MUS.k = mk; musicMix(); }
    AU.water.gain.value = r && r.pf.meta.water.length ? 0.006 + (PL.wade || PL.swim ? 0.01 : 0) : 0;
    AU.under.frequency.value = PL.under ? 600 : 20000;
  }
}
function roomFirst(name) {
  const t = {
    poolhall: 'A long stone hall with a canal of books sunk down its middle. The shelves go below your feet.',
    stacks: 'The floor drops two steps and the bookcases stand in rows below you, under squares of light.',
    backrooms: 'Green damask. Red carpet. Low ceilings and one more turn, and one more. You have been here before, somehow, in a dream.',
    pillars: 'A forest of stone columns on a sunken marble floor, and light falling in squares.',
    well: 'A square shaft through the middle of everything. Look down: floors, and floors, and floors.',
    tower: 'A stone ramp winds up and down a round tower, one turn to a floor. The middle is open.',
    grand: 'A great hall two floors tall, books from the floor to the vault.',
    crossing: 'Four stone vaults meet under a dome. Light comes through the eye of it, down into a stepped pit.',
    bath: 'A sunken court of black and white marble, with steps down on every side, and columns all round.',
    reading: 'A reading room: oak, lamplight, green shades. It smells like a library you once loved.',
  }[name] || (CATALOG[name] && CATALOG[name].blurb);
  if (t && MODE === 'play') toast(t);
}
function frame(now) {
  requestAnimationFrame(frame);
  const raw = (now - last) / 1000, dt = Math.min(0.05, raw); last = now;
  const t = now / 1000;
  renderFrame.dt = dt;
  if (AU.wind && !(S && S.fall) && AU.wind.gain.value > 0) AU.wind.gain.setTargetAtTime(0, AU.ctx.currentTime, 0.15);   // the rush of air stops whenever the fall does, however it ended
  if (MODE === 'play' && !document.hidden && raw < 0.5) {
    perfSum += raw; perfN++; perfT += raw;
    if (perfT > 2.5) {
      const avg = perfSum / perfN;
      if (avg > 0.021 && AQ > 0.6) { AQ = Math.max(0.6, AQ - 0.1); applyQuality(); }
      else if (avg > 0.024 && S && S.settings.gfx > 0 && !S.flags.autoGfx) { S.flags.autoGfx = 1; S.settings.gfx--; applyGfx(); toast('Lowered the graphics level to keep things smooth. You can change it in Pause.'); }
      perfT = perfSum = perfN = 0;
    }
  }
  const live = S && MODE !== 'title' && MODE !== 'prologue' && WORLD.ready;
  WU.uTime.value = t;
  if (live) {
    if (MODE === 'play' && !nightBusy && !PL.dead) {
      updatePlayer(dt); updateTime(dt); syncRoom(); storyTick(dt); updateCaptions(dt);
      if (PL.edgeArm > 0) { PL.edgeArm -= dt; const sh = shaftNear(); if (!sh || sh.d > 1.8) PL.edgeArm = 0; }
      TARGET = findTarget(); updateHUD(dt);
      PL.hurtT = Math.max(0, PL.hurtT - dt * 1.5);
      saveT += dt; if (saveT > 8) { saveT = 0; save(); }
      bookT -= dt; if (bookT <= 0) { bookT = 0.5; if (!S.fall || -PL.vy < 15) { updateWorld(S.x, S.y, S.z, S.fall && -PL.vy > 20); refreshBooks(); } }
    } else if (MODE === 'play' && S.fall && (nightBusy || PL.dead)) {
      S.y += PL.vy * dt; wrapPlayer(true); placeCamera(dt);
    } else placeCamera(dt);
    updateThrown(dt); updateStreaks(S.fall && PL.falling ? -PL.vy : 0);
    PL.shake = Math.max(0, PL.shake - dt * 0.8);
  } else if (WORLD.ready) {
    const k = t * 0.05; camera.position.set(8 + Math.sin(k) * 2.6, 1.65, 8 + Math.cos(k * 0.8) * 2.2); camera.rotation.set(0.1 + Math.sin(k * 1.3) * 0.05, k * 0.6, 0);
    dayK = 1;
  }
  WU.uDay.value = dayK;
  for (const pf of PREFABS.values()) if (pf && pf.mats) for (const k in pf.mats) { const m = pf.mats[k]; if (m.uniforms.uOn) m.uniforms.uOn.value = m.userData.night ? 1 : dayK; }
  PM.comp.uniforms.uTime.value = t;
  PM.comp.uniforms.uDrunk.value = live ? clamp(S.drunk, 0, 1.3) : 0;
  PM.comp.uniforms.uHurt.value = live ? Math.max(PL.hurtT, 1 - S.hp / 100) * 0.8 : 0;
  PM.comp.uniforms.uSpeed.value = live && S.fall ? clamp((-PL.vy - 20) / 40, 0, 1) : 0;
  PM.comp.uniforms.uWet.value = live && PL.under ? 1 : 0;
  PM.comp.uniforms.uTint.value.set(live && PL.under ? 0.55 : 1, live && PL.under ? 0.95 : 1, live && PL.under ? 1.1 : 1);
  renderer.setClearColor(WU.uFogCol.value, 1);   // beyond the rooms that are loaded: haze, not black
  renderFrame();
}
/* load the catalogue, then the rooms around where you will wake; the rest stream in as you walk */
(async () => {
  const bar = $('#t-load'); if (bar) bar.textContent = 'Building the library…';
  await loadCatalog();
  const sv = loadSave();
  const at = sv && sv.cx !== undefined ? [sv.cx + Math.floor((sv.x || 8) / RC), sv.cz + Math.floor((sv.z || 8) / RC), sv.floor + Math.floor(((sv.y || 0) + 2) / RLH)] : [START_CX, START_CZ, START_FLOOR];
  const names = new Set([...roomsNear(START_CX, START_CZ, START_FLOOR, WORLD.radius + 1, 1), ...roomsNear(at[0], at[1], at[2], WORLD.radius + 1, 1)]);
  let done = 0;
  if (bar) bar.textContent = `Building the library… 0 / ${names.size}`;
  await Promise.all([...names].map(n => loadPrefab(n).then(() => { done++; if (bar) bar.textContent = `Building the library… ${done} / ${names.size}`; })));
  for (const n of names) { const pf = PREFABS.get(n); if (pf && !pf.probeDone) captureProbe(pf); }
  WORLD.ready = true; if (bar) bar.hidden = true; $('#title').classList.add('live');
  document.querySelectorAll('#b-new, #b-continue').forEach(b => b.disabled = false);
  if (MODE === 'title') titleWorld();
})().catch(e => { console.error(e); const bar = $('#t-load'); if (bar) bar.textContent = 'The library would not load. Check your connection and reload.'; });
{ const sv = loadSave(); if (sv) { $('#b-continue').hidden = false; $('#b-continue').textContent = `Continue — year ${fmt(sv.year)}, day ${fmt(sv.day)}`; } }
requestAnimationFrame(frame);
addEventListener('beforeunload', save);
