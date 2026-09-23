'use strict';
/* ==========================================================================
   Audio — a procedural drone, echoing footsteps, pages, wind, the stillness at night
   ========================================================================== */
const AU = { ctx: null };
function noiseBuf(ctx, sec) { const b = ctx.createBuffer(1, Math.floor(ctx.sampleRate * sec), ctx.sampleRate), d = b.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; return b; }
function audioInit() {
  if (AU.ctx) { if (AU.ctx.state === 'suspended') AU.ctx.resume(); return; }
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)(); AU.ctx = ctx;
    AU.master = ctx.createGain(); AU.master.gain.value = S ? S.settings.vol : 0.8; AU.master.connect(ctx.destination);
    const rev = ctx.createConvolver(), len = ctx.sampleRate * 4, ir = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let ch = 0; ch < 2; ch++) { const d = ir.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6); }
    rev.buffer = ir; AU.rev = ctx.createGain(); AU.rev.gain.value = 0.55; AU.rev.connect(rev); rev.connect(AU.master);
    AU.noise = noiseBuf(ctx, 2);
    const dg = ctx.createGain(); dg.gain.value = 0.045; const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 260; lp.Q.value = 0.6;
    lp.connect(dg); dg.connect(AU.master); dg.connect(AU.rev); AU.drone = dg;
    [[55, 'sawtooth', 0.5], [82.6, 'sine', 0.9], [110.3, 'triangle', 0.35], [164.4, 'sine', 0.12]].forEach(([f, t, g]) => { const o = ctx.createOscillator(); o.type = t; o.frequency.value = f; const og = ctx.createGain(); og.gain.value = g; o.connect(og); og.connect(lp); o.start(); });
    const lfo = ctx.createOscillator(); lfo.frequency.value = 0.04; const lg = ctx.createGain(); lg.gain.value = 90; lfo.connect(lg); lg.connect(lp.frequency); lfo.start();
    const air = ctx.createBufferSource(); air.buffer = AU.noise; air.loop = true; const af = ctx.createBiquadFilter(); af.type = 'bandpass'; af.frequency.value = 500; af.Q.value = 0.4;
    AU.air = ctx.createGain(); AU.air.gain.value = 0.012; air.connect(af); af.connect(AU.air); AU.air.connect(AU.master); air.start();
    const w = ctx.createBufferSource(); w.buffer = AU.noise; w.loop = true; AU.windF = ctx.createBiquadFilter(); AU.windF.type = 'lowpass'; AU.windF.frequency.value = 300;
    AU.wind = ctx.createGain(); AU.wind.gain.value = 0; w.connect(AU.windF); AU.windF.connect(AU.wind); AU.wind.connect(AU.master); w.start();
  } catch (e) { AU.ctx = null; }
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
  step: soft => burst({ dur: 0.07, f: 600 + Math.random() * 500, q: 1.4, gain: soft ? 0.07 : 0.15, rev: 0.7 }),
  page: () => { burst({ dur: 0.22, type: 'highpass', f: 2600, q: 0.5, gain: 0.07, rev: 0.2, att: 0.03 }); setTimeout(() => burst({ dur: 0.12, type: 'highpass', f: 3400, q: 0.5, gain: 0.05, rev: 0.2 }), 90); },
  book: () => burst({ dur: 0.06, f: 380, q: 2, gain: 0.2, rev: 0.4 }),
  chime: () => { tone(660, 660, 1.2, 0.07); setTimeout(() => tone(990, 990, 1.4, 0.05), 140); },
  thunk: () => { tone(80, 32, 1.6, 0.35, 'sine', 0.9); burst({ dur: 0.5, type: 'lowpass', f: 200, gain: 0.3, rev: 0.9 }); },
  hit: () => { burst({ dur: 0.18, type: 'lowpass', f: 420, gain: 0.5, rev: 0.4 }); tone(120, 50, 0.25, 0.3); },
  impact: () => { burst({ dur: 0.6, type: 'lowpass', f: 300, gain: 0.9, rev: 1.0 }); tone(70, 25, 0.8, 0.6); },
  jump: () => burst({ dur: 0.1, f: 500, q: 1, gain: 0.07, rev: 0.4 }),
  drink: () => { burst({ dur: 0.3, type: 'bandpass', f: 1800, q: 3, gain: 0.08, rev: 0.3 }); tone(900, 1300, 0.15, 0.03, 'sine', 0.3); },
  scream: () => { tone(820, 380, 2.4, 0.05, 'sawtooth', 1.0); },
  chant: () => { tone(98, 96, 3.5, 0.06, 'sawtooth', 1.0); setTimeout(() => tone(110, 108, 3.0, 0.05, 'sawtooth', 1.0), 900); },
};

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
  if (e.repeat && ['KeyE', 'KeyR', 'KeyG', 'KeyF', 'KeyJ', 'KeyC', 'KeyZ', 'KeyQ'].includes(k)) return;
  if (MODE === 'play') {
    if (['Space', 'ArrowUp', 'ArrowDown', 'Tab'].includes(k)) e.preventDefault();
    if (k === 'KeyE') act('use'); else if (k === 'KeyR') act('read'); else if (k === 'KeyG') act('drop');
    else if (k === 'KeyF') act('shove'); else if (k === 'KeyJ') openJournal(); else if (k === 'KeyC') PL.crouch = !PL.crouch;
    else if (k === 'KeyZ') act('sleep'); else if (k === 'KeyQ') act('consume');
    else if (k === 'Space' && S.fall) act('sleep');
    else if (k === 'Escape' && !locked) openPause();
  } else if (MODE === 'ui') {
    if (k === 'Escape' || (k === 'KeyJ' && !$('#journal').hidden)) { e.preventDefault(); if (!$('#moment').hidden) closeMoment(); else closeOverlays(); }
    else if (!$('#reader').hidden && (k === 'ArrowRight' || k === 'ArrowLeft')) turnPage(k === 'ArrowRight' ? 1 : -1);
    else if (!$('#dialog').hidden && /^Digit[1-9]$/.test(k)) { const b = $('#d-opts').children[+k.slice(5) - 1]; if (b && !$('#d-opts').hidden) b.click(); }
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
  tb('#t-e', () => act('use')); tb('#t-r', () => act('read')); tb('#t-g', () => act('drop')); tb('#t-f', () => act('shove'));
  tb('#t-c', () => PL.crouch = !PL.crouch); tb('#t-sp', () => { if (S.fall) act('sleep'); else keys.TouchJump = true; }); tb('#t-z', () => act('sleep'));
  tb('#t-j', openJournal); tb('#t-p', openPause);
}

/* ==========================================================================
   The player
   ========================================================================== */
const PL = { vy: 0, vx: 0, vz: 0, onGround: true, crouch: false, eye: 1.62, stepAcc: 0, bob: 0, railArm: 0, hurtT: 0, dead: false, falling: false, shake: 0 };
const WALLS = [
  [0, 80, -3.9, -2.94], [79.8, 80.0, -13.4, -2.9], [91.8, 92.0, -13.4, -2.9], [79.65, 80.25, -3.25, -2.85], [91.75, 92.35, -3.25, -2.85],
  [79.8, 92, -13.4, -13.2], [0, 92, 0.05, 0.3],
  [83.8, 88.2, -10.7, -10.5], [83.8, 84.0, -10.7, -6.3], [88.0, 88.2, -10.7, -6.3], [83.8, 85.4, -6.55, -6.25], [86.6, 88.2, -6.55, -6.25],
  [80.2, 83.8, -13.1, -10.95], [91.2, 91.85, -9.95, -8.05], [88.9, 91.1, -5.45, -4.35],
];
function pushCircle(pos, r) {
  const b0 = Math.floor(pos.x / P);
  for (let pass = 0; pass < 2; pass++) for (let k = b0 - 1; k <= b0 + 1; k++) for (const w of WALLS) {
    const x0 = w[0] + k * P, x1 = w[1] + k * P;
    const cx = clamp(pos.x, x0, x1), cz = clamp(pos.z, w[2], w[3]);
    const dx = pos.x - cx, dz = pos.z - cz, d2 = dx * dx + dz * dz;
    if (d2 >= r * r) continue;
    if (d2 > 1e-9) { const d = Math.sqrt(d2), s = (r - d) / d; pos.x += dx * s; pos.z += dz * s; }
    else { const pen = [pos.x - x0 + r, x1 - pos.x + r, pos.z - w[2] + r, w[3] - pos.z + r], m = Math.min(...pen), i = pen.indexOf(m); if (i === 0) pos.x = x0 - r; else if (i === 1) pos.x = x1 + r; else if (i === 2) pos.z = w[2] - r; else pos.z = w[3] + r; }
  }
  const lx = mod(pos.x, P);
  if (lx > 84.0 && lx < 88.0 && pos.z > -10.5 && pos.z < -6.5) {
    const ox = pos.x - lx + CX, dx = pos.x - ox, dz = pos.z - CZ, d = Math.hypot(dx, dz);
    if (d < SCOL) { const s = SCOL / Math.max(d, 1e-4); pos.x = ox + dx * s; pos.z = CZ + dz * s; }
    else if (d > SR && !(Math.abs(dx) < 0.58 && dz > 1.5)) { const s = SR / d; pos.x = ox + dx * s; pos.z = CZ + dz * s; }
  }
}
function inStair(x, z) { const lx = mod(x, P); return lx > 84.0 && lx < 88.0 && z > -10.5 && z < -6.5 && !(Math.abs(lx - CX) < 0.6 && z > -6.9); }
function helixH(x, z, near) {
  const lx = mod(x, P), th = Math.atan2(z - CZ, lx - CX);
  let t = (th - TH0) / (Math.PI * 2); t -= Math.floor(t);
  const h0 = t * H; let best = h0, bd = Math.abs(h0 - near);
  for (const c of [h0 - H, h0 + H]) { const d = Math.abs(c - near); if (d < bd) { bd = d; best = c; } }
  return best;
}
function groundAt(x, z, ly) { if (z > 0.3) return -Infinity; return inStair(x, z) ? helixH(x, z, ly) : 0; }
function moveInput() {
  const w = { x: 0, z: 0 };
  if (keys.KeyW || keys.ArrowUp) w.z -= 1; if (keys.KeyS || keys.ArrowDown) w.z += 1;
  if (keys.KeyA || keys.ArrowLeft) w.x -= 1; if (keys.KeyD || keys.ArrowRight) w.x += 1;
  w.x += joy.x; w.z += joy.y;
  const ml = Math.hypot(w.x, w.z); if (ml > 1) { w.x /= ml; w.z /= ml; }
  const sy = Math.sin(S.yaw), cy = Math.cos(S.yaw);
  return { x: w.x * cy + w.z * sy, z: -w.x * sy + w.z * cy, m: Math.min(ml, 1) };
}
function wrapPlayer() {
  let segMoved = false, fm = 0;
  while (S.lx >= P) { S.lx -= P; S.seg++; segMoved = true; }
  while (S.lx < 0) { S.lx += P; S.seg--; segMoved = true; }
  while (S.ly >= H) { S.ly -= H; S.floor++; fm++; }
  while (S.ly < -1e-4) { S.ly += H; S.floor--; fm--; }
  return { segMoved, fm };
}
function updatePlayer(dt) {
  if (!S.fall && S.z > 0.32) startFall(false);
  if (S.fall || PL.falling) { updateFalling(dt); return; }
  const mi = moveInput();
  const weak = S.hunger > 0.85 || S.thirst > 0.8;
  const sprint = (keys.ShiftLeft || keys.ShiftRight || (isTouch && mi.m > 0.97)) && !PL.crouch && !weak;
  const spd = PL.crouch ? 1.3 : sprint ? 6.4 : 2.7;
  let vx = mi.x * spd, vz = mi.z * spd;
  if (S.drunk > 0.4) { const t = performance.now() / 1000; vx += Math.sin(t * 1.3) * S.drunk * 0.8; vz += Math.cos(t * 0.9) * S.drunk * 0.5; }
  const pos = { x: S.lx + vx * dt, z: S.z + vz * dt };
  pushCircle(pos, 0.3); pushNPCs(pos);
  const moved = Math.hypot(pos.x - S.lx, pos.z - S.z);
  S.lx = pos.x; S.z = pos.z;
  const jumpKey = keys.Space || keys.TouchJump; keys.TouchJump = false;
  if (PL.onGround && jumpKey && !PL.crouch) { PL.vy = 4.3; PL.onGround = false; SFX.jump(); }
  PL.vy = Math.max(PL.vy - 12 * dt, -30);
  let ny = S.ly + PL.vy * dt;
  const g = groundAt(S.lx, S.z, S.ly);
  if (ny <= g + 0.001) { ny = g; if (PL.vy < -9) hurt(Math.round((-PL.vy - 9) * 8), 'the fall'); PL.vy = 0; PL.onGround = true; }
  else if (PL.onGround && ny - g < 0.45 && PL.vy <= 0) { ny = g; PL.vy = 0; }
  else PL.onGround = false;
  if (g > S.ly && g - S.ly < 0.5) { ny = Math.max(ny, g); PL.onGround = true; PL.vy = Math.max(PL.vy, 0); }
  S.ly = ny;
  const w = wrapPlayer();
  if (w.fm > 0) S.stats.climbed += w.fm;
  if (PL.onGround && moved > 0) {
    S.stats.dist += moved; PL.stepAcc += moved; PL.bob += moved * 2.3;
    if (PL.stepAcc > (sprint ? 1.6 : 0.85)) { PL.stepAcc = 0; SFX.step(PL.crouch); }
  }
  PL.eye += ((PL.crouch ? 1.0 : 1.62) - PL.eye) * Math.min(1, dt * 10);
  placeCamera();
}
function placeCamera() {
  const sh = PL.shake > 0 ? (Math.random() - 0.5) * PL.shake : 0;
  camera.position.set(S.lx + sh * 0.3, S.ly + PL.eye + (PL.onGround && !S.fall ? Math.sin(PL.bob) * 0.028 : 0) + sh * 0.3, S.z);
  camera.rotation.set(S.pitch + sh * 0.05, S.yaw, S.drunk > 0.3 ? Math.sin(performance.now() / 1400) * 0.05 * S.drunk : 0);
  const fovT = 72 + (S.fall ? clamp(-PL.vy / TERMINAL, 0, 1) * 14 : 0);
  if (Math.abs(camera.fov - fovT) > 0.05) { camera.fov += (fovT - camera.fov) * 0.1; camera.updateProjectionMatrix(); }
}
function startFall(tackled) {
  if (S.fall) return;
  S.fall = { startFloor: S.floor, days: 0, t: 0 };
  PL.falling = true; PL.onGround = false; PL.vy = tackled ? -1 : 0.5; PL.vz = 1.8; PL.vx = 0; PL.railArm = 0;
  S.z = Math.max(S.z, 0.7); S.ly = clamp(S.ly + 0.6, 0.5, 1.4);
  $('#fallhud').hidden = false;
  if (!tackled) logJ('Climbed over the railing and let go.');
  const rr = npcRec('rachel');
  if (rr.following) { rr.following = false; const r = NPC_BY.rachel; r.mode = 'idle'; r.t = 0; r.special = false; r.home = UNI; toast('Rachel stays at the rail. You watch her get smaller.'); }
  save();
}
function updateFalling(dt) {
  S.fall.t += dt;
  const mi = moveInput();
  const k = 1 - Math.exp(-dt * 2.2);
  PL.vx += (mi.x * 5.5 - PL.vx) * k;
  PL.vz += (mi.z * 5.5 - PL.vz) * (mi.m > 0.05 ? k : k * 0.4);
  PL.vy = Math.max(PL.vy - 9.8 * dt, -TERMINAL);
  S.lx += PL.vx * dt; S.z += PL.vz * dt; S.ly += PL.vy * dt;
  // the galleries: hit one and you land there — dead, and awake tomorrow on that floor
  if (S.z < 0.35 || S.z > CHASM - 0.35) {
    const opp = S.z > CHASM / 2, speed = -PL.vy;
    if (speed < 11) { landAlive(opp); return; }
    impact(opp); return;
  }
  const w = wrapPlayer();
  if (w.fm < 0) S.stats.fallen -= w.fm;
  if (w.segMoved || w.fm) updateGroundBooks();
  const sp = clamp(-PL.vy / TERMINAL, 0, 1);
  if (AU.ctx) { AU.wind.gain.value = sp * 0.35; AU.windF.frequency.value = 200 + sp * 1700; }
  PL.shake = sp * 0.06;
  placeCamera();
}
function toOppositeSide() { S.side = 1 - S.side; S.lx = P - S.lx; S.yaw += Math.PI; }
function landAlive(opp) {
  if (opp) toOppositeSide();
  S.z = -0.8; S.ly = 0; PL.vy = 0; PL.vx = 0; PL.vz = 0; PL.falling = false; PL.onGround = true;
  const fl = S.fall ? S.fall.startFloor - S.floor : 0; S.fall = null; $('#fallhud').hidden = true;
  if (AU.wind) AU.wind.gain.value = 0;
  toast(opp ? 'You catch the far railing and haul yourself over — onto the other gallery.' : 'You catch the railing and haul yourself back over.');
  logJ(opp ? `Caught the railing of the far gallery, floor ${fmt(S.floor)}.` : `Caught a railing on floor ${fmt(S.floor)} and climbed back over.`);
  updateWindow(true); updateGroundBooks(); void fl;
}
function impact(opp) {
  const fallen = S.fall.startFloor - S.floor;
  S.stats.maxFall = Math.max(S.stats.maxFall, fallen);
  const floor = S.ly > 2.7 ? S.floor + 1 : S.floor;
  S.landing = { side: opp ? 1 - S.side : S.side, seg: S.seg, lx: opp ? P - S.lx : S.lx, floor, fallen, flip: opp };
  SFX.impact(); PL.shake = 0.5;
  logJ(`Steered into the edge of floor ${fmt(floor)} at ${Math.round(-PL.vy)} m/s, after falling ${fmt(fallen)} floors.`);
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
  if (cause !== 'impact') logJ({ thirst: 'Died of thirst.', drink: 'Drank myself to death, like Jed.', 'the Direites': 'The Direites caught me. It took them a long time.', 'Dire Dan': 'Dire Dan kept his promise. He killed me as we fell.', 'the fall': 'Died of a fall.' }[cause] || `Died (${cause}).`);
  save();
  setTimeout(() => sleepNow('dead'), 900);
}

/* ==========================================================================
   Day and night, and dawn — when everything resets
   ========================================================================== */
let nightBusy = false, dark = false, momentAfter = null, exposure = 1;
function fadeMsg(t, s) { $('#fade-t').textContent = t; $('#fade-s').textContent = s || ''; $('#fade').classList.add('on'); }
function sleepNow(reason) {
  if (nightBusy) return; nightBusy = true;
  const lines = {
    bed: ['You lie down on the narrow bed.', 'Somewhere, far above or below, someone is still talking. Then there is nothing.'],
    floor: ['You lie down where you are.', 'The stone is cool. Sleep comes the way it always does here: all at once.'],
    dark: ['The lamps are out. You feel your way to the floor.', 'You sleep where you lie. Everyone does.'],
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
    const fl = Math.round(hours * 3600 * TERMINAL / H);
    S.floor -= fl; S.stats.fallen += fl; S.fall.days++; S.stats.daysFalling++;
    S.stats.maxFall = Math.max(S.stats.maxFall, S.fall.startFloor - S.floor);
  }
  if (!S.dead) { S.thirst = clamp(S.thirst + hours / 60, 0, 0.97); S.hunger = clamp(S.hunger + hours / 120, 0, 0.97); }
  S.day++; S.time = LIGHTS_ON + 0.02;
  // dawn: every book that is not being held goes back to its shelf; wounds heal; the dead wake
  const moved = Object.keys(S.over).length + S.ground.length;
  S.over = {}; S.ground = []; recountOver();
  S.hp = 100; S.drunk = 0;
  let sub = 'The lamps come on. The shelves have not moved.'; const wasDead = !!S.dead;
  if (moved) { sub = 'Every book you moved is back on its shelf.'; if (!S.flags.sawReset) { S.flags.sawReset = 1; logJ('At dawn every book we had moved — even the ones we threw into the chasm — was back on its shelf, exactly where it had been.'); } }
  if (S.dead) {
    S.hunger = 0.08; S.thirst = 0.08;
    if (S.dead.cause === 'impact' && S.landing) {
      const L = S.landing;
      S.side = L.side; S.seg = L.seg; S.lx = clamp(L.lx, 0.5, P - 0.5); S.floor = L.floor; S.z = -0.8; S.ly = 0; if (L.flip) S.yaw += Math.PI;
      S.fall = null; PL.falling = false; $('#fallhud').hidden = true;
      sub = `You wake on floor ${fmt(S.floor)}, whole, on the walkway where you hit.`;
      logJ(`Woke on floor ${fmt(S.floor)}${L.flip ? ', on the far gallery' : ''}. ${fmt(L.fallen)} floors below where I jumped.`);
      storyEvent('landed', { fallen: L.fallen });
    } else if (deadInFall) { PL.falling = true; PL.vy = -TERMINAL; sub = 'You wake whole, and still falling.'; logJ('Woke whole — still falling.'); }
    else { sub = 'You wake whole, where you died.'; logJ('Woke whole, where I died.'); }
    S.dead = null; S.landing = null; PL.dead = false;
  }
  if (!S.fall) { PL.vy = 0; PL.vx = 0; PL.vz = 0; PL.onGround = true; PL.falling = false; }
  if (S.fall) { PL.falling = true; PL.vy = -TERMINAL; $('#fallhud').hidden = false; if (!S.flags.abyss) { S.flags.abyss = 1; momentAfter = 'abyss'; } if (!wasDead) sub = 'The lamps come on. You are still falling.'; }
  dark = false;
  storyDawn();
  updateWindow(true); updateGroundBooks(); updateCarry(); showHeld(S.carried ? parseKey(S.carried) : null);
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
  if (S.time >= LIGHTS_OFF - 0.25 && S.time < LIGHTS_OFF) { lampT = 0.75 + 0.25 * Math.sin(performance.now() * 0.03) * Math.sin(performance.now() * 0.011); if (S.flags.dimWarn !== S.day) { S.flags.dimWarn = S.day; toast('The lamps are dimming. The dark is a few minutes away.'); } }
  if (S.time >= LIGHTS_OFF) {
    lampT = 0;
    if (!dark) { dark = true; SFX.thunk(); toast(S.fall ? 'The lamps go out. You fall in total darkness.' : 'The lamps go out, all of them, all at once. Utter stillness. Find a bed (E) or lie down (Z).', true); if (S.fall) setTimeout(() => sleepNow('fall'), 2500); }
    if (S.time >= LIGHTS_OFF + 1) sleepNow('dark');
  }
  U.uLamp.value += (lampT - U.uLamp.value) * Math.min(1, dt * (lampT < U.uLamp.value ? 3 : 1));
  if (GLOW) GLOW.material.opacity = U.uLamp.value;
  if (AU.drone) AU.drone.gain.value = 0.045 * (0.15 + 0.85 * U.uLamp.value);
}

/* ==========================================================================
   What's under the crosshair
   ========================================================================== */
let TARGET = null;
const _o = new THREE.Vector3(), _d = new THREE.Vector3();
function raySphere(cx, cy, cz, r) { const ox = _o.x - cx, oy = _o.y - cy, oz = _o.z - cz, b = ox * _d.x + oy * _d.y + oz * _d.z, c = ox * ox + oy * oy + oz * oz - r * r, h = b * b - c; if (h < 0) return Infinity; const t = -b - Math.sqrt(h); return t > 0 ? t : Infinity; }
function findTarget() {
  if (PL.dead) return null;
  camera.getWorldPosition(_o); camera.getWorldDirection(_d);
  const st = storyTargets(); if (st) return st;
  if (S.fall) return null;
  let best = null, bt = 3.2;
  if (_d.z < -1e-3 && S.ly < 0.5) {
    const t = (SHELF_Z - _o.z) / _d.z;
    if (t > 0 && t < 2.8) {
      const x = _o.x + _d.x * t, y = _o.y + _d.y * t, k = Math.floor(x / P), lxs = x - k * P;
      if (lxs < RA0 && y > RY && y < RY + ROWS * RH) {
        const i = Math.floor(lxs / CW), u = lxs - i * CW;
        if (u > 0.06 && u < 1.94) {
          const p = clamp(Math.floor((u - 0.05) / BT), 0, PER - 1), r = clamp(Math.floor((y - RY) / RH), 0, ROWS - 1);
          const slot = { s: S.side, f: S.floor, c: (S.seg + k) * CASES + i, r, p };
          if (t < bt) { bt = t; best = { kind: 'slot', slot, book: slotContent(slot) }; }
        }
      }
    }
  }
  for (const n of NPCS) {
    if (n.gone || !n.mesh.visible || n.floor !== S.floor || n.side !== S.side) continue;
    const lying = n.mode === 'lie' || n.mode === 'dead';
    const t = raySphere(n.mesh.position.x, n.mesh.position.y + (lying ? 0.2 : 1.3), n.mesh.position.z + (lying && n.z < -10 ? -0.8 : 0), lying ? 0.75 : 0.5);
    if (t < bt && t < 3.2) { bt = t; best = { kind: 'npc', n }; }
  }
  for (const gb of S.ground) { if (!gb._m || !gb._m.visible) continue; const p = gb._m.position, t = raySphere(p.x, p.y, p.z, 0.28); if (t < bt) { bt = t; best = { kind: 'ground', gb }; } }
  if (S.ly < 0.5) for (const ox of [0, -P]) {
    const probes = [['kiosk', 91.4, 1.0, -9.0, 0.8], ['bed', 80.7, 0.45, -12.0, 0.85], ['bed', 82.0, 0.45, -12.0, 0.85], ['bed', 83.3, 0.45, -12.0, 0.85], ['bath', 80.15, 1.1, -8.5, 0.7], ['sign', 90.0, 1.4, -13.1, 0.95]];
    for (const [kind, x, y, z, r] of probes) { const t = raySphere(ox + x, y, z, r); if (t < bt) { bt = t; best = { kind }; } }
  }
  if (S.z > -0.85 && _d.z > 0.15 && _d.y < 0.5 && S.ly < 0.5) { const t = (0.12 - _o.z) / _d.z; if (t < bt) { bt = t; best = { kind: 'rail' }; } }
  return best;
}
function npcName(n) { const rec = npcRec(n.d.key); if (n.d.generic) return n.gname || 'A stranger'; if (n.d.role === 'direite') return 'A Direite'; return rec.met || n.d.key === 'dan' ? n.d.name : 'A stranger'; }
function describeTarget(t) {
  const P_ = $('#prompt'), ch = $('#crosshair');
  ch.classList.toggle('hot', !!t);
  if (!t) { P_.innerHTML = PL.railArm > 0 ? '<div class="k">[E] again to let go · step back to stay</div>' : dark && !S.fall ? '<div class="k">[Z] Lie down and sleep</div>' : ''; return; }
  let a = '', b = '';
  if (t.kind === 'slot') {
    if (t.book) {
      const out = !sameId(t.book, t.slot);
      a = esc(addrLine(t.book)) + (out ? '<br><span class="warm">out of place — it will go home at dawn</span>' : '');
      b = S.carried ? 'Your hands are full · G to drop the book you hold' : '[E] Take it and read';
    } else { a = 'An empty slot · ' + esc(addrLine(t.slot)); b = S.carried ? '[E] Put the book you hold here' : 'Someone took this one. It will be back at dawn.'; }
  } else if (t.kind === 'npc') {
    const n = t.n, lying = n.mode === 'lie' || n.mode === 'dead';
    a = `<span class="n">${esc(npcName(n))}</span>`;
    b = n.mode === 'dead' ? '[E] Look' : lying && S.time >= 21.5 ? 'Asleep' : '[E] Talk' + (n.mode === 'chase' ? ' · [F] Shove' : '');
  } else if (t.kind === 'ground') { a = esc(addrLine(parseKey(t.gb.id))) + '<br>lying on the floor'; b = S.carried ? 'Your hands are full' : '[E] Pick it up'; }
  else if (t.kind === 'kiosk') { a = 'A kiosk'; b = '[E] Ask for food or drink'; }
  else if (t.kind === 'bed') { a = 'A narrow bed'; b = S.time >= 17 || dark ? '[E] Sleep until the lamps come on' : 'Beds are for the evening (after 17:00).'; }
  else if (t.kind === 'bath') { a = 'The bathroom'; b = '[E] Go in'; }
  else if (t.kind === 'sign') { a = 'A brass plaque, and a slot beneath it'; b = S.carried ? '[E] Post the book you hold through the slot' : '[E] Read the plaque'; }
  else if (t.kind === 'rail') { a = 'The railing. Below it, nothing — for as far as anyone has fallen.'; b = PL.railArm > 0 ? '[E] again to let go · step back to stay' : '[E] Climb over' + (S.carried ? ' · [G] Throw the book over' : ''); }
  else if (t.kind === 'tackle') { a = '<span class="n">Dire Dan</span>'; b = '[E] Tackle him over the railing'; }
  else if (t.kind === 'catch') { a = `<span class="n">${esc(t.n.d.key === 'wand' ? 'A falling woman' : 'Someone falling')}</span>`; b = '[E] Catch hold'; }
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
    if (dark || S.time >= 21) { sleepNow('floor'); return; }
    toast('You aren’t tired. Nobody sleeps before the lamps go out here — there is too much day to get through.'); return;
  }
  if (kind === 'drop') {
    if (!S.carried) return;
    const id = parseKey(S.carried);
    if (S.fall) { toast('It tumbles away from you and is gone. At dawn it will be back on its shelf.'); S.carried = null; showHeld(null); updateCarry(); return; }
    if (S.z > -0.95 && _d.z > 0.1) {
      throwBookVisual(id, S.lx - Math.sin(S.yaw) * 0.4, S.ly + 1.3, 0.35);
      S.carried = null; S.stats.thrown++; showHeld(null); updateCarry(); SFX.book();
      if (S.stats.thrown === 1) { logJ('Threw a searched book over the railing, as Elliott said. It fell until the dark had it.'); toast('It falls end over end until the dark takes it. Dawn will put it back on its shelf.'); }
      save(); return;
    }
    const fx = -Math.sin(S.yaw) * 0.6, fz = -Math.cos(S.yaw) * 0.6;
    const pos = { x: S.lx + fx, z: clamp(S.z + fz, -12.8, -0.35) }; pushCircle(pos, 0.12);
    const gy = groundAt(pos.x, pos.z, S.ly);
    S.ground.push({ id: S.carried, seg: S.seg, lx: pos.x, z: pos.z, floor: S.floor, side: S.side, ly: gy === -Infinity ? 0 : gy, yaw: Math.random() * 6 });
    if (S.ground.length > 120) S.ground.shift();
    S.carried = null; SFX.book(); showHeld(null); updateCarry(); updateGroundBooks(); save(); return;
  }
  if (kind === 'shove') {
    if (t && (t.kind === 'npc' || t.kind === 'tackle' || t.kind === 'catch')) {
      const n = t.n;
      if (n.mode === 'fallWith' || S.fall) { shoveInFall(n); return; }
      n.stun = 2.4; n.hitCd = 2.4; SFX.hit();
      const x = gx(n.seg, n.lx), dx = x - S.lx, dz = n.z - S.z, d = Math.hypot(dx, dz) || 1, pos = { x: x + dx / d * 0.9, z: n.z + dz / d * 0.9 };
      pushCircle(pos, 0.28); n.lx = pos.x - (n.seg - S.seg) * P; n.z = pos.z;
      if (n.mode !== 'chase') toast(`${npcName(n)} stumbles and stares at you.`);
    } else if (S.flags.danWith) shoveInFall(NPC_BY.dan);
    return;
  }
  if (!t) { if (PL.railArm > 0) goOver(); return; }
  if (t.kind === 'tackle') { tackleDan(); return; }
  if (t.kind === 'catch') { catchFaller(); return; }
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
  if (t.kind === 'npc') { openDialogue(t.n); return; }
  if (t.kind === 'kiosk') { openKiosk(); return; }
  if (t.kind === 'bed') { if (S.time < 17 && !dark) { toast('You aren’t tired yet.'); return; } sleepNow('bed'); return; }
  if (t.kind === 'bath') { S.flags.bath = (S.flags.bath || 0) + 1; toast(['A clean white room. The water is cold and perfect. There is no mirror.', 'You wash your face. The towel is fresh. It is always fresh.', 'Somebody has written on the wall in pencil: “still here.” By morning it will be gone.'][S.flags.bath % 3]); return; }
  if (t.kind === 'sign') {
    if (S.carried) {
      const id = parseKey(S.carried); S.carried = null; showHeld(null); updateCarry(); SFX.book();
      S.flags.slotted = (S.flags.slotted || 0) + 1;
      toast(S.flags.slotted === 1 ? 'You post the book through the slot. It is swallowed with a soft click. You wait. Nothing happens. Nothing at all.' : 'The slot takes it with a soft click. Nothing happens.');
      logJ(`Posted ${addrLine(id)} through the slot. It was not my life.`); save(); return;
    }
    openSign(); return;
  }
  if (t.kind === 'rail') {
    if (PL.railArm > 0) { goOver(); return; }
    PL.railArm = 3; toast('You swing a leg over the rail. The air below is cool. [E] again to let go.'); return;
  }
}
function goOver() { PL.railArm = 0; startFall(false); }

/* ==========================================================================
   HUD
   ========================================================================== */
function toast(text, bad) { const el = document.createElement('div'); el.className = 'toast' + (bad ? ' bad' : ''); el.textContent = text; $('#toasts').appendChild(el); setTimeout(() => el.remove(), 5600); while ($('#toasts').children.length > 3) $('#toasts').firstChild.remove(); }
function updateCarry() {
  const el = $('#carry');
  if (!S.carried && !S.item) { el.hidden = true; return; }
  el.hidden = false; let h = '';
  if (S.carried) { const id = parseKey(S.carried), L = bookLook(id); h += `<div class="spine" style="background:${cssCol(L.col)}"></div><div class="ct">Holding a book<br><span>${esc(addrLine(id))}</span><br><span>R read · G drop (at the rail: throw) · E into an empty slot</span></div>`; }
  if (S.item) h += `<div class="ct"${S.carried ? ' style="border-left:1px solid var(--edge);padding-left:10px"' : ''}>${esc(S.item.name)}<br><span>Q ${S.item.drink ? 'drink' : 'eat'} it</span></div>`;
  el.innerHTML = h;
}
let hudT = 0;
function updateHUD(dt) {
  hudT -= dt; if (hudT > 0) return; hudT = 0.1;
  $('#h-floor').textContent = fmt(S.floor) + (S.side ? ' (far side)' : '');
  const lxs = S.lx;
  let where;
  if (S.fall) where = 'In the chasm';
  else if (lxs < RA0 && S.z > -3.5) where = `Case <b>${fmt(S.seg * CASES + clamp(Math.floor(lxs / CW), 0, CASES - 1))}</b>`;
  else where = (inStair(S.lx, S.z) ? 'On the spiral stair' : 'Rest area') + ` · after case <b>${fmt(S.seg * CASES + CASES - 1)}</b>`;
  if (TARGET && TARGET.kind === 'slot') where += ` · Shelf <b>${TARGET.slot.r + 1}</b> · Book <b>${TARGET.slot.p + 1}</b>`;
  $('#h-case').innerHTML = where;
  $('#h-walk').innerHTML = `Walked <b>${S.stats.dist < 1000 ? fmt(S.stats.dist) + ' m' : (S.stats.dist / 1000).toFixed(2) + ' km'}</b>`;
  $('#h-day').textContent = dateLine();
  $('#h-clock').textContent = clock();
  $('#h-lamps').textContent = dark ? 'Lamps out' : S.time > LIGHTS_OFF - 0.25 ? 'Lamps dimming' : 'Lamps out at 22:00';
  const bar = (id, v, label) => { const e = $(id); e.querySelector('i').style.width = (v * 100) + '%'; e.querySelector('i').style.background = v > 0.8 ? 'var(--oxide)' : 'var(--lamp)'; e.title = label; };
  bar('#h-hunger', S.hunger, S.hunger > 0.85 ? 'Starving' : S.hunger > 0.5 ? 'Hungry' : 'Fed');
  bar('#h-thirst', S.thirst, S.thirst > 0.8 ? 'Parched — you will die of thirst' : S.thirst > 0.5 ? 'Thirsty' : 'Not thirsty');
  if (S.fall) {
    const fl = S.fall.startFloor - S.floor;
    $('#f-floors').textContent = fmt(fl) + (fl === 1 ? ' floor' : ' floors');
    $('#f-sub').textContent = `${Math.round(-PL.vy)} m/s · day ${S.fall.days + 1} of the fall · WASD steer — hit a gallery to land · ${isTouch ? 'Jump' : 'Space'}: sleep till the lamps come on`;
  }
  describeTarget(TARGET);
}
function showClickHint() { $('#clickhint').hidden = isTouch || locked || MODE !== 'play'; }

/* ==========================================================================
   Reader
   ========================================================================== */
const R = { id: null, pg: 0, hl: null };
function openReader(id) {
  R.id = id; R.hl = null; R.pg = 0;
  const k = keyOf(id);
  if (!S.seen[k]) { S.seen[k] = 1; S.stats.books++; const ks = Object.keys(S.seen); if (ks.length > 3000) delete S.seen[ks[0]]; }
  $('#r-title').textContent = `Floor ${fmt(id.f)}, case ${fmt(id.c)}`;
  $('#r-addr').innerHTML = `Shelf <b>${id.r + 1}</b> · Book <b>${id.p + 1}</b>${id.s ? ' · far gallery' : ''}<br>410 pages · 40 lines · 80 characters<br>One of 10<sup>${fmt(LOG10_BOOKS)}</sup> books.`;
  $('#r-results').innerHTML = ''; $('#r-qnote').textContent = ''; $('#r-q').value = '';
  if (sameId(id, SACK)) { R.pg = 188; }
  openOverlay('#reader'); renderPage(); SFX.page();
}
function renderPage() {
  const id = R.id, s = pageText(id, R.pg), fr = fragOf(id), frHere = fr && fr.page === R.pg;
  const marks = [];
  if (frHere) marks.push([fr.at, fr.at + fr.text.length, 'frag']);
  if (R.hl && R.hl.pg === R.pg) marks.push([R.hl.at, R.hl.at + R.hl.len, '']);
  marks.sort((a, b) => a[0] - b[0]);
  let out = '';
  for (let line = 0; line < LINES; line++) {
    const a = line * COLS, b = a + COLS; let pos = a, row = '';
    for (const [m0, m1, cls] of marks) { const s0 = Math.max(m0, a), s1 = Math.min(m1, b); if (s0 >= s1 || s0 < pos) continue; row += esc(s.slice(pos, s0)) + `<mark${cls ? ' class="' + cls + '"' : ''}>` + esc(s.slice(s0, s1)) + '</mark>'; pos = s1; }
    row += esc(s.slice(pos, b)); out += row + (line < LINES - 1 ? '\n' : '');
  }
  $('#page').innerHTML = out;
  $('#r-pg').value = R.pg + 1;
  $('#r-ph-l').textContent = `Floor ${fmt(id.f)} · case ${fmt(id.c)} · shelf ${id.r + 1} · book ${id.p + 1}`;
  $('#r-ph-r').textContent = `${R.pg + 1}`;
  const fbox = $('#r-frag');
  if (frHere) {
    const have = S.frags.some(f => f.addr === keyOf(id));
    fbox.innerHTML = `<div class="fragbox"><div class="eyebrow">Words, out of the noise</div><q>${esc(fr.text)}</q><div><button class="btn primary" id="r-rec" ${have ? 'disabled' : ''}>${have ? 'Recorded in your journal' : 'Record in journal'}</button></div></div>`;
    if (!have) $('#r-rec').onclick = () => { S.frags.push({ text: fr.text, addr: keyOf(id), page: fr.page + 1, day: S.day }); logJ(`Found words in a book: “${fr.text}” (${addrLine(id)}, page ${fr.page + 1}).`); SFX.chime(); renderPage(); save(); };
    if (sameId(id, SACK) && !S.flags.sackFound) { S.flags.sackFound = 1; logJ('Found Biscuit’s book. “sack it.” Two words, alone in the noise, exactly where he said.'); }
    if (!S.flags['saw' + keyOf(id)]) { S.flags['saw' + keyOf(id)] = 1; SFX.chime(); }
  } else fbox.innerHTML = '';
  S.stats.pages++;
}
function turnPage(d) { R.pg = mod(R.pg + d, PAGES); renderPage(); SFX.page(); }
$('#r-prev').onclick = () => turnPage(-1); $('#r-next').onclick = () => turnPage(1);
$('#r-pg').addEventListener('change', () => { const v = parseInt($('#r-pg').value, 10); if (v >= 1 && v <= PAGES) { R.pg = v - 1; renderPage(); SFX.page(); } else $('#r-pg').value = R.pg + 1; });
$('#r-pg').addEventListener('keydown', e => { if (e.key === 'Enter') e.target.blur(); });
function runSearch() {
  const q = $('#r-q').value; if (!q) return;
  S.stats.searches++;
  const res = []; let total = 0;
  for (let pg = 0; pg < PAGES; pg++) { const s = pageText(R.id, pg); let i = s.indexOf(q); while (i !== -1) { total++; if (res.length < 200) res.push({ pg, at: i }); i = s.indexOf(q, i + 1); } }
  const expect = 1312000 / Math.pow(95, q.length);
  $('#r-qnote').textContent = `${fmt(total)} match${total === 1 ? '' : 'es'} in 410 pages. By chance alone you'd expect ${expect >= 0.01 ? 'about ' + expect.toFixed(expect < 1 ? 2 : 1) : 'one in ' + fmt(1 / expect) + ' books'}.`;
  $('#r-results').innerHTML = res.slice(0, 60).map((r, i) => `<button data-i="${i}">page ${r.pg + 1}, line ${Math.floor(r.at / COLS) + 1}</button>`).join('');
  [...$('#r-results').children].forEach(b => b.onclick = () => { const r = res[+b.dataset.i]; R.pg = r.pg; R.hl = { pg: r.pg, at: r.at, len: q.length }; renderPage(); SFX.page(); });
}
$('#r-go').onclick = runSearch; $('#r-q').addEventListener('keydown', e => { if (e.key === 'Enter') runSearch(); });

/* ==========================================================================
   Kiosk — "any food or drink you name"; the bathroom; the plaque
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
   Dialogue
   ========================================================================== */
const D = { n: null, chat: [], ctl: null };
let SAMPLE = null;
(async () => { try { if (window.claude && window.claude.use) SAMPLE = await window.claude.use('sample'); } catch (e) { SAMPLE = null; } })();
function openDialogue(n) {
  D.n = n; D.chat = []; n.attend = 12;
  const rec = npcRec(n.d.key);
  if (rec.last !== S.day) { rec.last = S.day; rec.aff = (rec.aff || 0) + 1; }
  rec.talks = (rec.talks || 0) + 1;
  const por = n.d.por;
  $('#d-por').style.backgroundImage = por ? `url(assets/${por}.jpg)` : '';
  $('#d-por').innerHTML = por ? '' : `<div class="sil">${esc(npcName(n).replace(/^A /, '').charAt(0))}</div>`;
  $('#d-fac').hidden = true;
  $('#d-chat').hidden = true; $('#d-opts').hidden = false; $('#d-text').hidden = false;
  openOverlay('#dialog');
  if (n.mode === 'dead' && !DLG[n.d.key]) { $('#d-name').textContent = npcName(n); renderNode({ text: '(They are not breathing. They will be back in the morning.)', opts: [] }, true); return; }
  if (DLG[n.d.key]) gotoNode('root', true);
  else { rec.met = true; renderNode(genericNode(n, rec)); }
}
function gotoNode(name, greet) {
  const def = DLG[D.n.d.key], rec = npcRec(D.n.d.key);
  const node = def[name]({ rec, greet: !!greet, n: D.n });
  renderNode(node);
}
function renderNode(node, noChat) {
  const n = D.n;
  $('#d-name').textContent = npcName(n);
  const role = n.d.generic ? (n.assign ? { searchers: 'Searcher', drinkers: 'Drinker', still: 'One of the Still', scholars: 'The University', preacher: n.assign.i === 0 ? 'Shelf-preacher' : 'Listener' }[n.assign.role] : 'Falling') : { rachel: 'The University', master: 'The University', scholar: 'The University', dan: 'The Direites', direite: 'The Direites', companion: 'Arrived with you', drinker: 'Next rest area east', faller: 'Falling', took: 'Mathematician' }[n.d.role];
  const fc = $('#d-fac'); fc.hidden = !role; fc.textContent = role || ''; fc.className = 'chip' + (n.d.role === 'dan' || n.d.role === 'direite' ? ' hostile' : '');
  $('#d-text').textContent = node.text;
  const opts = (node.opts || []).filter(o => !('if' in o) || o.if);
  if (SAMPLE && !noChat) opts.push({ t: 'Speak freely…', soft: true, fx: openChat });
  opts.push({ t: 'Leave.', soft: true, fx: closeOverlays });
  const box = $('#d-opts'); box.innerHTML = '';
  opts.forEach((o, i) => { const b = document.createElement('button'); b.innerHTML = `<span class="n">${i + 1}</span>${esc(o.t)}`; if (o.soft) b.className = 'soft'; b.onclick = () => { if (o.fx) o.fx(); if (o.go) gotoNode(o.go); save(); }; box.appendChild(b); });
  save();
}
function openChat() { $('#d-opts').hidden = true; $('#d-text').hidden = true; $('#d-chat').hidden = false; $('#d-log').innerHTML = ''; D.chat = []; setTimeout(() => $('#d-in').focus(), 30); }
async function sendChat() {
  const inp = $('#d-in'), text = inp.value.trim(); if (!text || !SAMPLE || D.ctl) return;
  inp.value = '';
  const logEl = $('#d-log'), me = document.createElement('div'); me.className = 'me'; me.textContent = text; logEl.appendChild(me);
  const them = document.createElement('div'); them.className = 'them'; them.textContent = 'Thinking…'; logEl.appendChild(them); logEl.scrollTop = logEl.scrollHeight;
  D.chat.push({ role: 'user', content: text }); if (D.chat.length > 12) D.chat.splice(0, 2);
  D.ctl = new AbortController(); $('#d-stop').hidden = false; $('#d-send').disabled = true;
  try {
    const r = await SAMPLE([{ role: 'user', content: chatPrompt(D.n) }, ...D.chat], { modelTier: 'quick', cache: false, signal: D.ctl.signal, onText: ({ text }) => { them.textContent = text; logEl.scrollTop = logEl.scrollHeight; } });
    D.chat.push({ role: 'assistant', content: r.text });
  } catch (e) {
    D.chat.pop();
    const c = e && e.code; them.textContent = e && e.text ? e.text : '';
    if (['not_granted', 'sampling_disabled', 'capability_disabled', 'not_declared'].includes(c)) { them.textContent = '(They look at you as if you hadn’t spoken. Free conversation is turned off for this page.)'; SAMPLE = null; }
    else if (c === 'rate_limited') them.textContent = '(They seem tired of talking. Try again in a little while.)';
    else if (c !== 'cancelled' && !them.textContent) them.textContent = '(They open their mouth, then close it again. Something interrupted them — try again.)';
  } finally { D.ctl = null; $('#d-stop').hidden = true; $('#d-send').disabled = false; }
}
$('#d-send').onclick = sendChat; $('#d-in').addEventListener('keydown', e => { if (e.key === 'Enter') sendChat(); });
$('#d-stop').onclick = () => D.ctl && D.ctl.abort();
$('#d-back').onclick = () => { if (D.ctl) D.ctl.abort(); $('#d-chat').hidden = true; $('#d-opts').hidden = false; $('#d-text').hidden = false; if (DLG[D.n.d.key]) gotoNode('root'); else renderNode(genericNode(D.n, npcRec(D.n.d.key))); };

/* ==========================================================================
   Captions (for things that happen around you) and moments (chapter cards)
   ========================================================================== */
let CAP = null;
function showCaptions(lines, done) {
  CAP = { lines, i: -1, t: 0, done };
  nextCaption();
}
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
  else if (jTab === 'frags') h = S.frags.length ? `<div class="frags">${S.frags.map(f => `<blockquote><q>${esc(f.text)}</q><cite>${esc(addrLine(parseKey(f.addr)))} · page ${f.page} · day ${f.day}${f.uni ? ' · catalogued by the University' : ''}</cite></blockquote>`).join('')}</div>` : '<p class="note" style="max-width:52ch">No readable words yet. Most pages are noise from edge to edge. When a sentence surfaces, record it here — the University will want it.</p>';
  else if (jTab === 'souls') {
    const met = NPC_DEFS.filter(d => !d.generic && !d.minor && npcRec(d.key).met);
    h = `<div class="souls">${met.map(d => `<div class="soul"><div class="p" style="background-image:url(assets/${d.por}.jpg)"></div><div><div class="nm">${esc(d.name)}</div><div class="ds">${esc(soulNote(d.key))}</div></div><div class="ds">${npcRec(d.key).talks || 0} talks</div></div>`).join('') || '<p class="note">You haven’t introduced yourself to anyone yet.</p>'}</div>`;
  } else if (jTab === 'nums') {
    const st = S.stats, items = [['Days', S.day], ['Books opened', st.books], ['Pages read', st.pages], ['Books thrown over', st.thrown], ['Fragments found', S.frags.length], ['Walked', st.dist < 1000 ? fmt(st.dist) + ' m' : (st.dist / 1000).toFixed(2) + ' km'], ['Floors climbed', st.climbed], ['Floors fallen', st.fallen], ['Longest fall', fmt(st.maxFall) + ' fl.'], ['Days spent falling', st.daysFalling], ['Deaths', st.deaths]];
    h = `<div class="stats">${items.map(([k, v]) => `<div class="stat"><div class="v">${typeof v === 'number' ? fmt(v) : v}</div><div class="k">${k}</div></div>`).join('')}</div>`;
  } else if (jTab === 'odds') {
    const n = Math.max(S.stats.books, 1), frac = LOG10_BOOKS - Math.log10(n), lb = lifeBook(), sent = 20 * Math.log10(95) - Math.log10(1312000);
    h = `<div class="odds">
      <p>Books in the library: <span class="num">95<sup>1,312,000</sup></span> — about <span class="num">10<sup>${fmt(LOG10_BOOKS)}</sup></span>. Written out, that number has <span class="num">${fmt(DIGITS)}</span> digits.</p>
      <p>You have opened <span class="num">${fmt(S.stats.books)}</span>. That is roughly one book in <span class="num">10<sup>${fmt(frac)}</sup></span> — the same as none, to every decimal place anyone could print.</p>
      <p>Master Took puts the library at about <span class="num">7.16 × 10<sup>1,297,369</sup></span> light-years, wide and deep.</p>
      <p>The chance that the next book you open is yours: <span class="num">1 in 10<sup>${fmt(LOG10_BOOKS)}</sup></span>. Opening one book a second since the Big Bang would change that exponent by about 17.</p>
      <h3>Where this game lies to you</h3>
      <p>In a truly random library, a particular twenty-character sentence turns up about once in <span class="num">10<sup>${Math.round(sent)}</sup></span> books. Here, one book in ${FRAG_RATE} carries a readable fragment. That is the game’s one mercy, and you should know it is one. Short strings are honest: search any book for a three-letter word and you will usually find one or two, just as chance predicts.</p>
      <p class="note">For the record, your own book is on a floor whose number begins ${lb.lead}… and runs to about ${fmt(lb.digits)} digits. Nobody here could tell you that; the game can.</p>
    </div>`;
  }
  pane.innerHTML = h;
}
function soulNote(k) {
  const r = npcRec(k);
  if (k === 'rachel') return S.flags.rachelGone ? 'Went over the railing to escape the Direites.' : r.following ? 'Walking with you.' : 'The University.';
  if (k === 'jed') return S.flags.jedBack ? 'Drank himself to death. Came back.' : 'Drinks at the next rest area east.';
  if (k === 'dan') return S.flags.danFallen ? 'You took him over the railing with you.' : 'Leads the Direites.';
  if (k === 'wand') return S.flags.wandLanded ? 'Let go, and steered for the stacks.' : 'Met falling.';
  return { biscuit: 'Arrived with you. Found “sack it.”', elliott: 'Arrived with you. Has a system.', larisa: 'Arrived with you.', betty: 'Arrived with you.', treacle: 'Presides over the University.', pruitt: 'Department of Coherent Text.', took: 'Has done the arithmetic.' }[k] || '';
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
  if (D.ctl) D.ctl.abort();
  document.querySelectorAll('.overlay').forEach(o => o.hidden = true);
  MODE = 'play'; save(); $('#touch').hidden = !isTouch; showClickHint();
}
document.querySelectorAll('[data-close]').forEach(b => b.onclick = () => { closeOverlays(); requestLock(); });
document.querySelectorAll('.overlay').forEach(o => o.addEventListener('mousedown', e => { if (e.target === o && o.id !== 'moment') closeOverlays(); }));
function openPause() {
  if (MODE !== 'play') return;
  $('#s-sens').value = S.settings.sens; $('#s-vol').value = S.settings.vol; $('#s-q').value = S.settings.q; $('#s-fx').checked = S.settings.fx !== 0; $('#s-hints').checked = S.settings.hints !== 0; syncOut();
  $('#confirm-reset').hidden = true;
  document.querySelectorAll('.overlay').forEach(o => o.hidden = true);
  $('#pause').hidden = false; MODE = 'pause'; $('#touch').hidden = true;
}
function resume() { $('#pause').hidden = true; MODE = 'play'; $('#touch').hidden = !isTouch; requestLock(); showClickHint(); }
function syncOut() { $('#o-sens').textContent = (+S.settings.sens).toFixed(1); $('#o-vol').textContent = Math.round(S.settings.vol * 100); $('#o-q').textContent = Math.round(S.settings.q * 100) + '%'; }
$('#s-sens').oninput = e => { S.settings.sens = +e.target.value; syncOut(); save(); };
$('#s-vol').oninput = e => { S.settings.vol = +e.target.value; if (AU.master) AU.master.gain.value = S.settings.vol; syncOut(); save(); };
$('#s-q').oninput = e => { S.settings.q = +e.target.value; applyQuality(); syncOut(); save(); };
$('#s-fx').onchange = e => { S.settings.fx = e.target.checked ? 1 : 0; save(); };
$('#s-hints').onchange = e => { S.settings.hints = e.target.checked ? 1 : 0; updateThreadsHUD(); save(); };
$('#p-resume').onclick = resume;
$('#p-journal').onclick = () => { $('#pause').hidden = true; MODE = 'play'; openJournal(); };
$('#p-title').onclick = () => { save(); $('#pause').hidden = true; showTitle(); };
$('#p-reset').onclick = () => { $('#confirm-reset').hidden = false; };
$('#p-reset-no').onclick = () => { $('#confirm-reset').hidden = true; };
$('#p-reset-yes').onclick = () => { try { localStorage.removeItem(SAVE_KEY); } catch (e) {} S = null; $('#pause').hidden = true; showTitle(); };
function showTitle() {
  MODE = 'title'; NPCS.forEach(n => n.mesh.visible = false); UNIPROPS.visible = false; $('#captions').hidden = true; CAP = null; $('#title').hidden = false; $('#hud').hidden = true; $('#touch').hidden = true; $('#prologue').hidden = true;
  const sv = S || loadSave(); $('#b-continue').hidden = !sv;
  if (sv) $('#b-continue').textContent = `Continue — year ${fmt(sv.year)}, day ${fmt(sv.day)}`;
}
const PRO = [
  { who: '', text: 'You died. The cancer did what the doctors said it would, more or less on schedule.' },
  { who: '', text: 'Then: a waiting room. Fluorescent light. Plastic chairs. Four strangers beside you, just as lost as you are.' },
  { who: 'Xandern', text: 'Welcome. I’m Xandern. I’ll be processing you today. Please keep your paperwork in order and your screaming to a minimum.' },
  { who: 'Xandern', text: 'I’m afraid the true religion was Zoroastrianism. Nobody is ever pleased to hear it. It’s nothing personal.' },
  { who: '', text: 'He calls Lester first — a Christian, certain of everything — and sends him through a door you are glad you cannot see beyond. Then Julia, an atheist, who seems mostly annoyed to be wrong.' },
  { who: 'Xandern', text: 'You five are going somewhere else. Three things. One: if you die, you will be brought back. Two: your earthly covenants — marriage included — are dissolved.' },
  { who: 'Xandern', text: 'Three: find the book that tells your life, every word of it, without a single error, and post it through the slot. Then you may go. It is meant to teach you something. It is a punishment. It is not forever.' },
  { who: '', text: 'Then you are standing at a railing, in a body that doesn’t hurt anymore.' },
];
let proI = 0;
$('#b-new').onclick = () => { audioInit(); $('#title').hidden = true; $('#prologue').hidden = false; MODE = 'prologue'; proI = 0; showPro(); };
$('#b-continue').onclick = () => { audioInit(); S = S || loadSave(); startPlay(false); };
function showPro() {
  const L = PRO[proI], t = $('#pro-t'); t.style.animation = 'none'; void t.offsetWidth; t.style.animation = '';
  t.textContent = L.text; $('#pro-who').textContent = L.who || ''; $('#pro-por').hidden = !L.who;
  $('#b-pro').textContent = proI === PRO.length - 1 ? 'Wake up' : 'Go on';
}
$('#b-pro').onclick = () => {
  if (proI < PRO.length - 1) { proI++; showPro(); return; }
  S = freshState(); logJ('Died of cancer. Was processed by a demon named Xandern. The true religion was Zoroastrianism.'); logJ('Woke at a railing in the library, with four others who arrived when I did. I can remember every day of my life, exactly. That should make my book easy to recognise. It does not make it easier to find.');
  save(); startPlay(true);
};
function startPlay(first) {
  S.settings = Object.assign({ sens: 1, vol: 0.8, q: 1, fx: 1, hints: 1 }, S.settings);
  recountOver(); applyQuality();
  PL.dead = false; PL.vy = 0; PL.vx = 0; PL.vz = 0; $('#hurt').style.opacity = 0; nightBusy = false; dark = S.time >= LIGHTS_OFF;
  PL.falling = !!S.fall; $('#fallhud').hidden = !S.fall; if (S.fall) PL.vy = -TERMINAL;
  if (S.dead) { S.dead = null; S.landing = null; }
  if (!S.fall && S.ly !== 0 && !inStair(S.lx, S.z)) S.ly = 0;
  placeNamed(); updateWindow(true); updateGroundBooks(); updateCarry(); showHeld(S.carried ? parseKey(S.carried) : null);
  $('#title').hidden = true; $('#prologue').hidden = true; $('#hud').hidden = false; $('#touch').hidden = !isTouch;
  MODE = 'play'; if (AU.master) AU.master.gain.value = S.settings.vol;
  U.uLamp.value = dark ? 0 : 1;
  if (first) showMoment('arrival'); else { requestLock(); showClickHint(); }
}

/* ==========================================================================
   Main loop
   ========================================================================== */
let last = performance.now(), saveT = 0, perfT = 0, perfN = 0, perfSum = 0, lastClock = '';
const TITLE_S = freshState();
function frame(now) {
  requestAnimationFrame(frame);
  const raw = (now - last) / 1000, dt = Math.min(0.05, raw); last = now;
  const t = now / 1000;
  if (MODE === 'play' && !document.hidden && raw < 0.5) {
    perfSum += raw; perfN++; perfT += raw;
    if (perfT > 2.5) { const avg = perfSum / perfN; if (avg > 0.021 && AQ > 0.5) { AQ = Math.max(0.5, AQ - 0.12); applyQuality(); } perfT = perfSum = perfN = 0; }
  }
  const live = S && MODE !== 'title' && MODE !== 'prologue';
  const Sv = live ? S : TITLE_S;
  if (!live) { const k = t * 0.04; TITLE_S.lx = 30 + Math.sin(k) * 10; TITLE_S.time = 12; }
  const bk = S; S = Sv; updateWorldUniforms(t); S = bk;
  if (live) {
    if (MODE === 'play' && !nightBusy && !PL.dead) {
      updatePlayer(dt); updateTime(dt); storyTick(dt); updateNPCs(dt); updateCaptions(dt);
      if (PL.railArm > 0) { PL.railArm -= dt; if (S.z < -0.95) PL.railArm = 0; }
      TARGET = findTarget(); updateHUD(dt);
      if (TARGET && TARGET.kind === 'npc' && npcDist(TARGET.n) < 3) TARGET.n.attend = Math.max(TARGET.n.attend || 0, 1.5);
      PL.hurtT = Math.max(0, PL.hurtT - dt * 1.5);
      saveT += dt; if (saveT > 8) { saveT = 0; save(); }
    } else if (MODE === 'play' && S.fall && (nightBusy || PL.dead)) {
      // the body keeps falling in the dark
      S.ly += PL.vy * dt; wrapPlayer(); placeCamera();
    } else placeCamera();
    updateWindow(); updateThrown(dt); updateStreaks(S.fall && PL.falling ? -PL.vy : 0);
    const ck = clock(); if (ck !== lastClock) { lastClock = ck; drawClock(S.time); }
    PL.shake = Math.max(0, PL.shake - dt * 0.8);
  } else {
    const k = t * 0.04; camera.position.set(TITLE_S.lx, 1.6, 7.5); camera.rotation.set(0.04 + Math.sin(k * 1.3) * 0.05, Math.PI * 0.5 + Math.sin(k) * 0.4, 0);
    S = TITLE_S; updateWindow(); S = bk;
  }
  // exposure: the eye adapts to the dark
  const target = live && dark ? 3.2 : 1.0;
  exposure += (target - exposure) * (1 - Math.exp(-dt / (target > exposure ? 5 : 0.6)));
  PM.comp.uniforms.uExposure.value = exposure;
  PM.comp.uniforms.uTime.value = t;
  PM.comp.uniforms.uDrunk.value = live ? clamp(S.drunk, 0, 1.3) : 0;
  PM.comp.uniforms.uHurt.value = live ? Math.max(PL.hurtT, 1 - S.hp / 100) * 0.8 : 0;
  PM.comp.uniforms.uSpeed.value = live && S.fall ? clamp((-PL.vy - 20) / 40, 0, 1) : 0;
  renderFrame();
}
{ const sv = loadSave(); if (sv) { $('#b-continue').hidden = false; $('#b-continue').textContent = `Continue — year ${fmt(sv.year)}, day ${fmt(sv.day)}`; } }
{ const bk = S; S = TITLE_S; recountOver(); updateWindow(true); S = bk; }
requestAnimationFrame(frame);
addEventListener('beforeunload', save);
