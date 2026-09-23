'use strict';
/* ==========================================================================
   People: robed figures with painted faces, schedules, and a few scripted modes
   ========================================================================== */
const SKIN = { fair: [0.62, 0.43, 0.33], ruddy: [0.66, 0.4, 0.3], olive: [0.52, 0.36, 0.24], tan: [0.5, 0.33, 0.22], pale: [0.66, 0.5, 0.42] };
const NPC_DEFS = [
  // the four who arrived with you, and Jed next door
  { key: 'biscuit', name: 'Biscuit', por: 'biscuit', role: 'companion', cloth: [0.2, 0.19, 0.17], skin: SKIN.fair, hair: [0.55, 0.55, 0.53], style: 'wild', glasses: 1, lane: -1.3 },
  { key: 'elliott', name: 'Elliott', por: 'elliott', role: 'companion', cloth: [0.17, 0.18, 0.19], skin: SKIN.tan, hair: [0.45, 0.33, 0.17], style: 'short', stubble: 1, lane: -2.2 },
  { key: 'larisa', name: 'Larisa', por: 'larisa', role: 'companion', cloth: [0.21, 0.21, 0.22], skin: SKIN.pale, hair: [0.55, 0.54, 0.52], style: 'bob', lane: -0.9, h: 0.95 },
  { key: 'betty', name: 'Betty', por: 'betty', role: 'companion', cloth: [0.22, 0.17, 0.16], skin: SKIN.fair, hair: [0.32, 0.09, 0.04], style: 'curly', lane: -1.8, h: 0.96 },
  { key: 'jed', name: 'Jed', por: 'jed', role: 'drinker', cloth: [0.17, 0.16, 0.15], skin: SKIN.ruddy, hair: [0.09, 0.07, 0.05], style: 'messy', stubble: 1, lane: -1.6 },
  // the University
  { key: 'rachel', name: 'Rachel Hasnick', por: 'rachel', role: 'rachel', cloth: [0.2, 0.2, 0.22], skin: SKIN.fair, hair: [0.07, 0.05, 0.04], style: 'long', lane: -1.2, h: 0.97 },
  { key: 'treacle', name: 'Master Treacle', por: 'treacle', role: 'master', cloth: [0.24, 0.2, 0.15], skin: SKIN.ruddy, hair: [0.8, 0.79, 0.76], style: 'fringe', beard: 'short', lane: -1.5, wide: 1.12 },
  { key: 'pruitt', name: 'Dr. Ana Pruitt', por: 'scholar', role: 'scholar', cloth: [0.19, 0.2, 0.23], skin: SKIN.pale, hair: [0.2, 0.1, 0.06], style: 'bun', glasses: 1, lane: -2.1, h: 0.95 },
  // Dire Dan and his Direites — they come on raids
  { key: 'dan', name: 'Dire Dan', por: 'dan', role: 'dan', cloth: [0.16, 0.15, 0.14], skin: SKIN.fair, hair: [0.06, 0.05, 0.04], style: 'long', beard: 'short', bones: 1, lane: -1.6, h: 1.03 },
  { key: 'dir1', name: 'A Direite', por: 'direite1', role: 'direite', cloth: [0.13, 0.12, 0.12], skin: SKIN.ruddy, hair: [0.05, 0.05, 0.05], style: 'short', stubble: 1, bones: 1, lane: -2.3, wide: 1.12, minor: true },
  { key: 'dir2', name: 'A Direite', por: 'direite2', role: 'direite', cloth: [0.18, 0.17, 0.16], skin: SKIN.fair, hair: [0.4, 0.35, 0.3], style: 'buzz', bones: 1, lane: -0.8, h: 0.97, minor: true },
  { key: 'dir3', name: 'A Direite', role: 'direite', cloth: [0.14, 0.13, 0.12], skin: SKIN.olive, hair: [0.08, 0.06, 0.05], style: 'messy', bones: 1, lane: -1.2, minor: true },
  { key: 'dir4', name: 'A Direite', role: 'direite', cloth: [0.15, 0.14, 0.13], skin: SKIN.tan, hair: [0.1, 0.07, 0.05], style: 'short', beard: 'short', bones: 1, lane: -2.0, minor: true },
  // people you only meet by falling
  { key: 'wand', name: 'Wand', por: 'wand', role: 'faller', cloth: [0.2, 0.2, 0.21], skin: SKIN.pale, hair: [0.16, 0.1, 0.06], style: 'long', lane: 0, h: 0.95 },
  { key: 'took', name: 'Master Took', por: 'took', role: 'took', cloth: [0.22, 0.2, 0.18], skin: SKIN.fair, hair: [0.42, 0.4, 0.37], style: 'short', beard: 'long', lane: -1.4 },
];
/* Everyone else: a pool of strangers placed wherever the library happens to have people. */
{
  const clothes = [[0.22, 0.2, 0.17], [0.16, 0.18, 0.21], [0.24, 0.23, 0.2], [0.18, 0.15, 0.13], [0.2, 0.2, 0.2], [0.15, 0.17, 0.15], [0.23, 0.18, 0.16], [0.12, 0.13, 0.15]];
  const hairs = [[0.08, 0.06, 0.05], [0.3, 0.2, 0.1], [0.55, 0.42, 0.22], [0.45, 0.44, 0.42], [0.18, 0.1, 0.05], [0.7, 0.68, 0.64], [0.12, 0.09, 0.07]];
  const skins = Object.values(SKIN);
  for (let i = 0; i < 18; i++) {
    const r = sfc32(i * 7919 + 13, 77, 3, 9), pk = a => a[Math.floor(r() * a.length)], fem = r() < 0.5;
    NPC_DEFS.push({ key: 'g' + i, name: 'A stranger', generic: true, minor: true, role: 'generic', cloth: pk(clothes), skin: pk(skins), hair: pk(hairs),
      style: fem ? pk(['long', 'bob', 'curly', 'bun']) : pk(['short', 'messy', 'fringe', 'buzz', 'short']), beard: !fem && r() < 0.3 ? 'short' : 0, stubble: !fem && r() < 0.4 ? 1 : 0,
      glasses: r() < 0.18 ? 1 : 0, h: fem ? 0.94 + r() * 0.04 : 0.98 + r() * 0.06, lane: -0.8 - r() * 1.7, fem });
  }
}

/* Painted faces: a 512×256 canvas wrapped around the head sphere, face centred at u = 0.25 (+z) */
function faceTexture(d) {
  const c = document.createElement('canvas'); c.width = 512; c.height = 256; const g = c.getContext('2d');
  const sk = d.skin.map(v => Math.round(Math.pow(v, 1 / 2.2) * 255)), hr = d.hair.map(v => Math.round(Math.pow(v, 1 / 2.2) * 255));
  const skin = `rgb(${sk})`, hair = `rgb(${hr})`, dark = `rgb(${sk.map(v => v * 0.55 | 0)})`;
  g.fillStyle = skin; g.fillRect(0, 0, 512, 256);
  const cx = 128;
  // cheeks and shading
  for (const s of [-1, 1]) { const gr = g.createRadialGradient(cx + s * 38, 150, 2, cx + s * 38, 150, 30); gr.addColorStop(0, 'rgba(170,70,60,.22)'); gr.addColorStop(1, 'rgba(170,70,60,0)'); g.fillStyle = gr; g.fillRect(0, 0, 512, 256); }
  const sh = g.createRadialGradient(cx, 130, 30, cx, 130, 120); sh.addColorStop(0, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(0,0,0,.25)'); g.fillStyle = sh; g.fillRect(0, 0, 512, 256);
  // eyes
  for (const s of [-1, 1]) {
    const ex = cx + s * 25, ey = 118;
    g.fillStyle = dark; g.beginPath(); g.ellipse(ex, ey - 1, 12, 7, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#e9e1d4'; g.beginPath(); g.ellipse(ex, ey, 10, 5, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = d.key === 'xandern' ? '#c9a21a' : '#3a2a1c'; g.beginPath(); g.arc(ex + s * 0.5, ey, 4.2, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#0c0806'; g.beginPath(); g.arc(ex + s * 0.5, ey, 2, 0, Math.PI * 2); g.fill();
    g.strokeStyle = 'rgba(30,18,12,.9)'; g.lineWidth = 2.5; g.beginPath(); g.ellipse(ex, ey + 1, 11, 6.5, 0, Math.PI * 1.08, Math.PI * 1.92); g.stroke();
    g.strokeStyle = hair; g.lineWidth = 5; g.lineCap = 'round'; g.beginPath(); g.moveTo(ex - s * 11, ey - 13); g.quadraticCurveTo(ex, ey - 19, ex + s * 12, ey - 14); g.stroke();
    if (d.glasses) { g.strokeStyle = 'rgba(120,90,40,.95)'; g.lineWidth = 2; g.beginPath(); g.arc(ex, ey, 13, 0, Math.PI * 2); g.stroke(); }
  }
  if (d.glasses) { g.beginPath(); g.moveTo(cx - 12, 118); g.lineTo(cx + 12, 118); g.stroke(); }
  // nose and mouth
  g.strokeStyle = 'rgba(60,30,20,.45)'; g.lineWidth = 3; g.beginPath(); g.moveTo(cx + 3, 124); g.quadraticCurveTo(cx + 7, 142, cx + 2, 147); g.stroke();
  g.fillStyle = 'rgba(60,30,20,.4)'; g.beginPath(); g.ellipse(cx - 6, 148, 3, 2, 0, 0, 7); g.ellipse(cx + 6, 148, 3, 2, 0, 0, 7); g.fill();
  g.strokeStyle = d.role === 'dan' ? 'rgba(90,30,25,.95)' : 'rgba(110,50,45,.85)'; g.lineWidth = 4; g.beginPath();
  if (d.role === 'dan' || d.key === 'betty' || d.key === 'biscuit') { g.moveTo(cx - 15, 162); g.quadraticCurveTo(cx, 172, cx + 15, 162); } else { g.moveTo(cx - 13, 165); g.quadraticCurveTo(cx, 167, cx + 13, 165); }
  g.stroke();
  // hair on the scalp and around the back
  g.fillStyle = hair;
  if (d.style !== 'fringe' && d.style !== 'buzz') { g.fillRect(0, 0, 512, 62); g.beginPath(); g.moveTo(cx - 60, 62); g.quadraticCurveTo(cx, 44, cx + 60, 62); g.fill(); g.fillRect(cx + 70, 0, 512 - cx - 140, 150); }
  if (d.style === 'buzz') { g.globalAlpha = 0.6; g.fillRect(0, 0, 512, 70); g.globalAlpha = 1; }
  if (d.style === 'fringe') { g.fillRect(cx + 80, 70, 512 - cx - 160, 90); }
  if (d.style === 'long' || d.style === 'curly' || d.style === 'bob') g.fillRect(cx + 62, 0, 512 - cx - 124, 200);
  if (d.beard) { g.globalAlpha = 0.95; g.beginPath(); g.moveTo(cx - 48, 140); g.quadraticCurveTo(cx - 40, d.beard === 'long' ? 250 : 215, cx, d.beard === 'long' ? 256 : 222); g.quadraticCurveTo(cx + 40, d.beard === 'long' ? 250 : 215, cx + 48, 140); g.quadraticCurveTo(cx, 170, cx - 48, 140); g.fill(); g.globalAlpha = 1; }
  if (d.stubble) { g.globalAlpha = 0.28; g.beginPath(); g.ellipse(cx, 175, 46, 36, 0, 0, Math.PI * 2); g.fill(); g.globalAlpha = 1; }
  const t = new THREE.CanvasTexture(c); t.anisotropy = 4; return t;
}
const shadowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(0,0,0,.75)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
const shadowMat = new THREE.MeshBasicMaterial({ map: shadowTex, transparent: true, depthWrite: false, color: 0x000000 });
const ROBE = lathe([[0.001, 0.03], [0.29, 0.03], [0.28, 0.25], [0.25, 0.6], [0.21, 0.95], [0.195, 1.05], [0.21, 1.22], [0.23, 1.36], [0.215, 1.44], [0.12, 1.5], [0.055, 1.53], [0.001, 1.53]], 14);
function buildFigure(d) {
  const g = new THREE.Group(); g.rotation.order = 'YXZ';
  const cloth = propMat({ color: new THREE.Color(...d.cloth).multiplyScalar(1.6), gloss: 0.1 });
  const skin = propMat({ color: new THREE.Color(...d.skin), gloss: 0.3 });
  const hairM = propMat({ color: new THREE.Color(...d.hair), gloss: 0.5 });
  const face = propMat({ map: faceTexture(d), color: 0x9a9a9a, gloss: 0.25 });
  const dark = propMat({ color: new THREE.Color(0.03, 0.028, 0.025), gloss: 0.5 });
  const body = new THREE.Group(); g.add(body);
  const mk = (geo, mat, x, y, z, parent) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); (parent || body).add(m); return m; };
  const robe = mk(ROBE, cloth, 0, 0, 0); robe.scale.set(d.wide || 1, 1, 0.72 * (d.wide || 1));
  mk(new THREE.CylinderGeometry(0.045, 0.052, 0.12, 8), skin, 0, 1.55, 0);
  const head = new THREE.Group(); head.position.set(0, 1.665, 0); body.add(head);
  const hm = mk(new THREE.SphereGeometry(0.115, 20, 14), face, 0, 0, 0, head); hm.scale.set(0.92, 1.08, 0.98);
  // hair: a crown cap that stops at the hairline, and a back piece that never crosses the face
  const crown = (r, tl) => { const m = mk(new THREE.SphereGeometry(r, 16, 6, 0, Math.PI * 2, 0, Math.PI * tl), hairM, 0, 0.004, -0.008, head); m.rotation.x = -0.28; return m; };
  const backH = (r, tl, sx) => { const m = mk(new THREE.SphereGeometry(r, 14, 8, Math.PI * 0.94, Math.PI * 1.12, 0, Math.PI * tl), hairM, 0, 0.0, -0.004, head); m.scale.set(sx || 1, 1, 1); return m; };
  const st = d.style;
  if (st === 'short' || st === 'messy') { crown(0.121, 0.34); backH(0.12, 0.58); if (st === 'messy') for (let i = 0; i < 5; i++) mk(new THREE.SphereGeometry(0.034, 7, 5), hairM, (i - 2) * 0.04, 0.1 + (i % 2) * 0.012, -0.02 - Math.abs(i - 2) * 0.01, head); }
  if (st === 'buzz') { crown(0.117, 0.32); backH(0.116, 0.55); }
  if (st === 'long' || st === 'bob' || st === 'bun') { crown(0.123, 0.36); backH(0.124, st === 'bob' ? 0.72 : 0.66, 1.04); }
  if (st === 'long') { const b = mk(new THREE.BoxGeometry(0.2, 0.34, 0.05), hairM, 0, -0.2, -0.085, head); b.rotation.x = 0.12; }
  if (st === 'bun') mk(new THREE.SphereGeometry(0.05, 10, 8), hairM, 0, 0.06, -0.12, head);
  if (st === 'curly' || st === 'wild') {
    crown(0.13, 0.38); backH(0.132, 0.64, 1.08);
    for (let i = 0; i < 9; i++) { const a = Math.PI * (1.02 + i / 8 * 0.96), y = 0.02 + (i % 3) * 0.03; mk(new THREE.SphereGeometry(st === 'wild' ? 0.052 : 0.045, 8, 6), hairM, -Math.cos(a) * 0.12, y, Math.sin(a) * 0.11, head); }
    if (st === 'wild') for (const sx of [-1, 1]) mk(new THREE.SphereGeometry(0.05, 8, 6), hairM, sx * 0.12, 0.05, -0.01, head);
  }
  if (st === 'fringe') { const t = mk(new THREE.TorusGeometry(0.106, 0.024, 6, 16, Math.PI * 1.1), hairM, 0, -0.005, 0, head); t.rotation.set(Math.PI / 2, 0, Math.PI * 1.45); }
  if (d.beard) { const b = mk(new THREE.SphereGeometry(0.075, 12, 8), hairM, 0, -0.085, 0.045, head); b.scale.set(1.15, d.beard === 'long' ? 1.9 : 1.1, 0.9); }
  if (d.bones) { const bm = propMat({ color: new THREE.Color(0.62, 0.58, 0.48) }), bg = new THREE.CylinderGeometry(0.008, 0.008, 0.05, 5); for (let i = 0; i < 9; i++) { const a = Math.PI * 0.15 + (i / 8) * Math.PI * 0.7; mk(bg, bm, Math.cos(a) * 0.12, 1.42 - Math.sin(a) * 0.06, Math.sin(a) * 0.1); } }
  const arm = s => {
    const sh = new THREE.Group(); sh.position.set(s * 0.225 * (d.wide || 1), 1.42, 0); body.add(sh);
    const ua = new THREE.CylinderGeometry(0.058, 0.05, 0.3, 8); ua.translate(0, -0.15, 0); mk(ua, cloth, 0, 0, 0, sh);
    const el = new THREE.Group(); el.position.set(0, -0.29, 0); sh.add(el);
    const fa = new THREE.CylinderGeometry(0.052, 0.058, 0.26, 8); fa.translate(0, -0.13, 0); mk(fa, cloth, 0, 0, 0, el);
    mk(new THREE.SphereGeometry(0.043, 8, 6), skin, 0, -0.28, 0.005, el);
    return { sh, el };
  };
  const aL = arm(-1), aR = arm(1);
  const foot = s => { const f = mk(new THREE.BoxGeometry(0.09, 0.07, 0.22), dark, s * 0.09, 0.035, 0.05); return f; };
  const fL = foot(-1), fR = foot(1);
  const book = mk(new THREE.BoxGeometry(0.2, 0.26, 0.05), propMat({ color: new THREE.Color(0.3, 0.1, 0.07) }), 0, 1.2, 0.3); book.visible = false;
  const shadow = new THREE.Mesh(new THREE.CircleGeometry(0.42, 16), shadowMat); shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.012; g.add(shadow);
  const s = d.h || 1; g.scale.set(s, s, s);
  g.userData = { body, head, aL, aR, fL, fR, book, shadow, robe };
  scene.add(g); return g;
}

const NPCS = NPC_DEFS.map(d => ({ d, ax: 0, ay: 0, az: 0, yaw: 0, path: [], mode: 'idle', t: 0, phase: Math.random() * 6, stun: 0, hitCd: 0, gone: true, mesh: buildFigure(d), speed: 1.2, vy: 0, vz: 0, vx: 0, look: 0 }));
const NPC_BY = Object.fromEntries(NPCS.map(n => [n.d.key, n]));
/* people live in absolute coordinates (metres from the library's origin); they are drawn relative to you */
const rX = n => n.ax - S.cx * RC, rY = n => n.ay - S.floor * RLH, rZ = n => n.az - S.cz * RC;
function localToAbs(pl, p) {
  const s = ROOM_SIZE[pl.pf], W = s[0] * RC, D = s[1] * RC, xm = pl.mir ? W - p[0] : p[0], z = p[2];
  let X, Z;
  switch (pl.rot) { case 0: X = xm; Z = z; break; case 1: X = D - z; Z = xm; break; case 2: X = W - xm; Z = D - z; break; default: X = z; Z = W - xm; }
  return { x: pl.cx * RC + X, y: pl.lv * RLH + p[1], z: pl.cz * RC + Z };
}
function dirToAbs(pl, dx, dz) { const xm = pl.mir ? -dx : dx; switch (pl.rot) { case 0: return [xm, dz]; case 1: return [-dz, xm]; case 2: return [-xm, -dz]; default: return [dz, -xm]; } }
function pfOf(pl) { const p = PREFABS.get(pl.pf); return p && p.meta ? p : null; }
function roomSpots(pl, kind) { const pf = pfOf(pl); if (!pf) return []; return pf.meta.spots.filter(s => s.k === kind).map(s => { const a = localToAbs(pl, s.p), d = dirToAbs(pl, Math.cos(s.f), Math.sin(s.f)); return { x: a.x, y: a.y, z: a.z, yaw: Math.atan2(d[0], d[1]) }; }); }
function navAdj(pf) {
  if (pf.adj) return pf.adj;
  const adj = pf.meta.nav.map(() => []);
  for (const [a, b] of pf.meta.links) { adj[a].push(b); adj[b].push(a); }
  return pf.adj = adj;
}
function nearestNode(pl, ax, az) {
  const pf = pfOf(pl); if (!pf || !pf.meta.nav.length) return -1;
  let best = -1, bd = Infinity;
  pf.meta.nav.forEach((p, i) => { const a = localToAbs(pl, p), d = Math.hypot(a.x - ax, a.z - az); if (d < bd) { bd = d; best = i; } });
  return best;
}
function navPath(pl, fromX, fromZ, toI) {
  const pf = pfOf(pl); if (!pf) return [];
  const adj = navAdj(pf), s = nearestNode(pl, fromX, fromZ); if (s < 0) return [];
  const prev = new Map([[s, -1]]), q = [s];
  while (q.length) { const a = q.shift(); if (a === toI) break; for (const b of adj[a]) if (!prev.has(b)) { prev.set(b, a); q.push(b); } }
  if (!prev.has(toI)) return [localToAbs(pl, pf.meta.nav[toI])];
  const out = []; for (let i = toI; i !== -1; i = prev.get(i)) out.unshift(localToAbs(pl, pf.meta.nav[i]));
  return out;
}
/* a place to stand and read: in front of one of the room's shelves, near where people walk */
function readSpot(pl, seed) {
  const pf = pfOf(pl); if (!pf || !pf.meta.slabs.length) return null;
  const SL = pf.meta.slabs;
  for (let tries = 0; tries < 8; tries++) {
    const s = SL[(seed + tries * 7919) % SL.length];
    if (s.o[1] > 1.2 || s.o[1] < -0.3) continue;
    const lx = s.o[0] + s.u[0] / 2 + s.n[0] * 0.75, lz = s.o[2] + s.u[2] / 2 + s.n[2] * 0.75, ly = Math.max(0, s.o[1] - 0.05);
    const a = localToAbs(pl, [lx, ly, lz]), d = dirToAbs(pl, -s.n[0], -s.n[2]);
    return { x: a.x, y: a.y, z: a.z, yaw: Math.atan2(d[0], d[1]) };
  }
  return null;
}
function placeNPC(n, ax, ay, az) { n.ax = ax; n.ay = ay; n.az = az; n.path = []; n.vy = 0; n.vx = 0; n.vz = 0; }
function npcDist(n) { if (n.gone) return Infinity; return Math.hypot(rX(n) - S.x, (rY(n) - S.y) * 0.5, rZ(n) - S.z); }
function pushNPCs(pos) {
  for (const n of NPCS) {
    if (n.gone || !n.mesh.visible || ['lie', 'bed', 'dead', 'fall', 'fallWith', 'swim'].includes(n.mode)) continue;
    const x = rX(n), z = rZ(n), dx = pos.x - x, dz = pos.z - z, d = Math.hypot(dx, dz), m = 0.52 * (n.d.wide || 1);
    if (d < m && d > 1e-4 && Math.abs(rY(n) - pos.y) < 1.5) { pos.x = x + dx / d * m; pos.z = z + dz / d * m; }
  }
}
function moveTo(n, x, z, spd, dt, want) {
  const dx = x - n.ax, dz = z - n.az, d = Math.hypot(dx, dz);
  if (d <= (want || 0.05)) { n.walking = false; return true; }
  const st = Math.min(spd * dt, d - (want || 0));
  n.ax += dx / d * st; n.az += dz / d * st; n.walking = true; n.yaw = Math.atan2(dx, dz);
  return false;
}
const _np = new THREE.Vector3();
/* chasing and following: straight at you, sliding along walls */
function steer(n, spd, dt, want) {
  const tx = absX(), tz = absZ(), dx = tx - n.ax, dz = tz - n.az, d = Math.hypot(dx, dz);
  if (d <= want) { n.walking = false; return d; }
  const st = Math.min(spd * dt, d - want);
  _np.set(rX(n) + dx / d * st, rY(n), rZ(n) + dz / d * st);
  _sp.set(_np.x, _np.y + 0.6, _np.z); pushSphere(_sp, 0.3, true); _np.x = _sp.x; _np.z = _sp.z;
  _sp.set(_np.x, _np.y + 1.2, _np.z); pushSphere(_sp, 0.3, true); _np.x = _sp.x; _np.z = _sp.z;
  const moved = Math.hypot(_np.x - rX(n), _np.z - rZ(n));
  n.ax = _np.x + S.cx * RC; n.az = _np.z + S.cz * RC; n.walking = moved > 1e-3; n.yaw = Math.atan2(dx, dz);
  n.stuck = moved < st * 0.2 ? (n.stuck || 0) + dt : 0;
  return d;
}
function snapGround(n) {
  const x = rX(n), z = rZ(n), y = rY(n);
  if (Math.abs(x - S.x) > 40 || Math.abs(z - S.z) > 40 || Math.abs(y - S.y) > 10) return;
  const g = groundAt(x, y + 0.6, z, 0.3, 1.5);
  if (g > -Infinity) n.ay = g + S.floor * RLH;
}
function updateNPCs(dt) {
  for (const n of NPCS) {
    const m = n.mesh, R = m.userData;
    if (n.gone) { m.visible = false; continue; }
    const far = Math.abs(rX(n) - S.x) > 90 || Math.abs(rZ(n) - S.z) > 90 || Math.abs(rY(n) - S.y) > 80;
    n.t -= dt; n.hitCd -= dt; if (n.stun > 0) n.stun -= dt;
    n.walking = false;
    if (n.mode === 'fall' || n.mode === 'fallWith') {
      if (n.mode === 'fallWith' && PL.falling) {
        const o = n.off || { x: 0.7, y: -0.2, z: 0.5 };
        n.ax = absX() + o.x + Math.sin(performance.now() / 900 + n.phase) * 0.08; n.ay = absY() + o.y; n.az = absZ() + o.z;
      } else {
        n.vy = Math.max(n.vy - 12 * dt, -TERMINAL - (n.extraFall || 0)); n.ay += n.vy * dt; n.ax += n.vx * dt; n.az += n.vz * dt;
        if (n.onImpact && n.fallT !== undefined && (n.fallT -= dt) <= 0) { const f = n.onImpact; n.onImpact = null; f(n); }
      }
    } else if (n.mode === 'swim') {
      n.phase += dt * 0.6; n.ax += Math.cos(n.phase * 0.3 + n.look) * dt * 0.25; n.az += Math.sin(n.phase * 0.23 + n.look) * dt * 0.25;
      if (n.pool) { const dx = n.ax - n.pool.x, dz = n.az - n.pool.z, d = Math.hypot(dx, dz); if (d > n.pool.r) { n.ax = n.pool.x + dx / d * n.pool.r; n.az = n.pool.z + dz / d * n.pool.r; } }
    } else if (!far && n.stun <= 0) {
      if (n.mode === 'follow' || n.mode === 'chase') {
        const d = Math.hypot(rX(n) - S.x, rZ(n) - S.z), dy = Math.abs(rY(n) - S.y);
        if ((d > 26 || dy > 3 || (n.stuck || 0) > 4) && !PL.falling) {
          n.lostT = (n.lostT || 0) + dt;
          if (n.lostT > (n.mode === 'chase' ? 5 : 3)) { const b = behindYou(1.4); placeNPC(n, b.x, absY(), b.z); n.lostT = 0; n.stuck = 0; }
        } else {
          n.lostT = 0;
          const want = n.mode === 'follow' ? 1.7 : 0.85;
          const spd = n.mode === 'chase' ? (n.chaseSpeed || 4.8) : d > 6 ? 4.2 : d > 3 ? 2.8 : 2.0;
          steer(n, spd, dt, want); snapGround(n);
          if (n.mode === 'chase' && d < 1.25 && n.hitCd <= 0 && !PL.dead && !PL.falling && typeof onNpcHit === 'function') { n.hitCd = 1.1; onNpcHit(n); }
        }
      } else if (n.path.length) {
        const w = n.path[0];
        if (moveTo(n, w.x, w.z, n.speed, dt)) { n.path.shift(); }
        n.walking = n.path.length > 0; snapGround(n);
      } else if (n.mode !== 'script' && n.mode !== 'dead' && n.t <= 0) {
        const g = schedule(n);
        if (g) {
          n.mode = g.mode; n.goalYaw = g.yaw; n.t = g.dur || 20; n.faceAt = g.faceAt || null;
          if (g.path) n.path = g.path.slice(); else if (g.x !== undefined) n.path = [{ x: g.x, y: g.y, z: g.z }];
        } else n.t = 5;
      }
      if (n.path.length === 0 && n.mode === 'bed') n.mode = 'lie';
    }
    // pose
    const x = rX(n), y = rY(n), z = rZ(n);
    const vis = !far && Math.abs(y - S.y) < 60 && Math.hypot(x - S.x, z - S.z) < 70;
    m.visible = vis; if (!vis) continue;
    n.phase += dt * (n.walking ? (n.mode === 'chase' || n.mode === 'follow' ? 9 : 6.2) : 1.1);
    const sw = n.walking ? Math.sin(n.phase) : 0;
    R.aL.sh.rotation.set(-sw * 0.45, 0, -0.06); R.aR.sh.rotation.set(sw * 0.45, 0, 0.06);
    R.aL.el.rotation.set(-0.25 - Math.max(0, -sw) * 0.3, 0, 0); R.aR.el.rotation.set(-0.25 - Math.max(0, sw) * 0.3, 0, 0);
    R.fL.position.z = 0.05 + sw * 0.16; R.fR.position.z = 0.05 - sw * 0.16;
    R.body.position.y = n.walking ? Math.abs(Math.cos(n.phase)) * 0.035 : Math.sin(n.phase * 0.8) * 0.004;
    R.body.rotation.set(0, 0, n.walking ? Math.sin(n.phase) * 0.025 : 0);
    R.robe.scale.y = 1; R.book.visible = false; R.shadow.visible = true; R.head.rotation.set(0, 0, 0);
    let px = x, py = y, pz = z;
    if (!n.walking) {
      if (n.goalYaw !== undefined && n.goalYaw !== null && !n.faceAt) n.yaw = n.goalYaw;
      if (n.mode === 'read') { R.aL.sh.rotation.set(-0.95, 0, -0.25); R.aR.sh.rotation.set(-0.95, 0, 0.25); R.aL.el.rotation.x = -0.9; R.aR.el.rotation.x = -0.9; R.book.visible = true; R.book.position.set(0, 1.22, 0.3); R.head.rotation.x = 0.25; }
      if (n.faceAt) n.yaw = Math.atan2(n.faceAt.x - n.ax, n.faceAt.z - n.az);
      if (n.attend > 0 && !['lie', 'dead', 'sit', 'swim'].includes(n.mode)) {
        n.attend -= dt; if (n.mode === 'read') { R.book.visible = false; R.aL.sh.rotation.set(0, 0, -0.06); R.aR.sh.rotation.set(0, 0, 0.06); R.aL.el.rotation.x = R.aR.el.rotation.x = -0.25; R.head.rotation.x = 0; }
        const want = Math.atan2(S.x - x, S.z - z); let da = want - (n.faceYaw !== undefined ? n.faceYaw : n.yaw); da = Math.atan2(Math.sin(da), Math.cos(da));
        n.faceYaw = (n.faceYaw !== undefined ? n.faceYaw : n.yaw) + da * Math.min(1, dt * 5); n.yaw = n.faceYaw;
      } else n.faceYaw = undefined;
      if (n.mode === 'sit') { R.robe.scale.y = 0.62; R.body.position.y = -0.4; R.fL.position.z = R.fR.position.z = 0.32; }
      if (n.mode === 'preach' || n.mode === 'speak') { const k = Math.sin(n.phase * 2.2); R.aR.sh.rotation.set(-0.9 - k * 0.2, 0, 0.3); R.aL.sh.rotation.set(-0.4 + k * 0.1, 0, -0.2); }
      if (n.mode === 'drink') { R.aR.sh.rotation.set(-1.4, 0, 0.2); R.aR.el.rotation.x = -1.6; }
      const dxp = S.x - x, dzp = S.z - z, dp = Math.hypot(dxp, dzp);
      if (dp < 4 && Math.abs(y - S.y) < 2 && !['lie', 'dead', 'swim'].includes(n.mode)) { let a = Math.atan2(dxp, dzp) - n.yaw; a = Math.atan2(Math.sin(a), Math.cos(a)); R.head.rotation.y = clamp(a, -1.1, 1.1); }
    }
    if (n.mode === 'fall' || n.mode === 'fallWith') {
      R.aL.sh.rotation.set(-2.6, 0, -0.5); R.aR.sh.rotation.set(-2.5, 0, 0.5); R.shadow.visible = false;
      R.body.rotation.set(Math.sin(n.phase * 0.7) * 0.3, 0, Math.cos(n.phase * 0.5) * 0.3);
      m.rotation.set(0, n.yaw + performance.now() / 4000, 0);
    } else if (n.mode === 'swim') {
      R.aL.sh.rotation.set(-2.9 + Math.sin(n.phase * 3) * 0.6, 0, -0.3); R.aR.sh.rotation.set(-2.9 - Math.sin(n.phase * 3) * 0.6, 0, 0.3); R.shadow.visible = false;
      m.rotation.set(-1.25, n.yaw, 0); n.yaw += dt * 0.1; py = (n.pool ? n.pool.top - S.floor * RLH : y) - 0.25;
    } else if ((n.mode === 'lie' || n.mode === 'dead') && !n.walking) {
      m.rotation.set(-Math.PI / 2, n.lieYaw !== undefined ? n.lieYaw : Math.PI / 2, 0);
      py += n.onBed ? 0.46 : 0.14; R.shadow.visible = false;
    } else m.rotation.set(0, n.yaw, n.stun > 0 ? 0.35 : 0);
    if (n.mode === 'sit') py += 0.02;
    m.position.set(px, py, pz);
  }
}
/* a point a little behind you, clear of walls */
function behindYou(dist) {
  const bx = S.x + Math.sin(S.yaw) * dist, bz = S.z + Math.cos(S.yaw) * dist;
  _sp.set(bx, S.y + 0.9, bz); pushSphere(_sp, 0.35, true);
  return { x: _sp.x + S.cx * RC, z: _sp.z + S.cz * RC };
}
