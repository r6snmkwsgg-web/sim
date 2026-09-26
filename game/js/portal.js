'use strict';
/* ==========================================================================
   Portals: a rectangle in a room that shows, and leads to, another rectangle
   in the same room. Rooms declare them in their metadata (Blender axes):
     portals: [{a: {c: [x,y,z], n: [x,y,z], w, h}, b: {...}}]
   c is the middle of the rectangle's bottom edge, n the way you walk when you
   go in at a (and the way you come out at b), w and h its size. Every pair
   works both ways. The nearest two in view are rendered each frame from a
   virtual camera; each samples its own previous frame, so portals seen
   through portals recurse.
   ========================================================================== */
const PORTAL = { doors: [], slots: [], vcam: new THREE.PerspectiveCamera(), prev: null, prevCell: '' };
const PORTAL_MAX = 3;

const pv3 = p => new THREE.Vector3(p[0], p[2], p[1]);
function portalFrame(c, n, up) {
  const Z = n.clone().normalize();
  let Y = (up || new THREE.Vector3(0, 1, 0)).clone().normalize();
  if (Math.abs(Y.dot(Z)) > 0.99) Y = new THREE.Vector3(0, 0, -1);   // a floor or ceiling rectangle: its "up" runs along the room
  const X = new THREE.Vector3().crossVectors(Y, Z).normalize(); Y.crossVectors(Z, X);
  return new THREE.Matrix4().makeBasis(X, Y, Z).setPosition(c);
}
const PORTAL_FS = `uniform sampler2D tP; uniform vec2 uRes; uniform float uOn; uniform vec3 uFog;
void main() { vec3 c = texture2D(tP, gl_FragCoord.xy / uRes).rgb; gl_FragColor = vec4(mix(uFog, c, uOn), 1.0); }`;
const PORTAL_VS = `void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

function doorMesh(r, D, z) {
  const g = new THREE.PlaneGeometry(D.w, D.h); g.translate(0, D.h / 2, z);
  D.mat = new THREE.ShaderMaterial({ uniforms: { tP: { value: null }, uRes: { value: new THREE.Vector2(1, 1) }, uOn: { value: 0 }, uFog: { value: WU.uFogCol.value } },
    vertexShader: PORTAL_VS, fragmentShader: PORTAL_FS, side: THREE.DoubleSide });
  D.mesh = new THREE.Mesh(g, D.mat); D.mesh.matrixAutoUpdate = false; D.mesh.matrix.copy(D.F);
  r.grp.add(D.mesh); r.doors.push(D); PORTAL.doors.push(D);
}
function portalPlace(r) {
  r.doors = [];
  const M = r.pf.meta.meta || {};
  // mirrors: n faces the viewer; the door's frame looks into the glass, and its transform reflects through it
  for (const P of M.mirrors || []) {
    const F = portalFrame(pv3(P.c), pv3(P.n).negate(), P.up && pv3(P.up));
    const T = F.clone().multiply(new THREE.Matrix4().makeScale(1, 1, -1)).multiply(F.clone().invert());
    const D = { r, F, Fi: F.clone().invert(), T, w: P.w, h: P.h, mirror: true, floor: Math.abs(P.n[2]) > 0.5 };
    D.pair = D;
    doorMesh(r, D, -0.01);
  }
  const list = M.portals; if (!list) return;
  for (const P of list) {
    const Fa = portalFrame(pv3(P.a.c), pv3(P.a.n), P.a.up && pv3(P.a.up)), Fb = portalFrame(pv3(P.b.c), pv3(P.b.n), P.b.up && pv3(P.b.up));
    const T = Fb.clone().multiply(Fa.clone().invert());
    const flip = new THREE.Matrix4().makeRotationY(Math.PI);
    const A = { r, F: Fa, T, w: P.a.w, h: P.a.h }, B = { r, F: Fb.clone().multiply(flip), T: T.clone().invert(), w: P.b.w || P.a.w, h: P.b.h || P.a.h };
    A.pair = B; B.pair = A;
    for (const D of [A, B]) { D.Fi = D.F.clone().invert(); doorMesh(r, D, 0.02); }
  }
}
function portalDrop(r) {
  if (!r.doors) return;
  for (const D of r.doors) { r.grp.remove(D.mesh); D.mesh.geometry.dispose(); D.mat.dispose(); if (D.slot) D.slot.door = null; }
  PORTAL.doors = PORTAL.doors.filter(D => D.r !== r);
  r.doors = null;
}

function portalSlot(i) {
  let s = PORTAL.slots[i];
  const w = Math.max(64, Math.round(RW * 0.6)), h = Math.max(36, Math.round(RHh * 0.6));
  if (s && s.w === w && s.h === h) return s;
  if (s) s.rt.forEach(t => t.dispose());
  const o = { type: HALF ? THREE.HalfFloatType : THREE.UnsignedByteType, format: THREE.RGBAFormat, depthBuffer: true, stencilBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter };
  s = PORTAL.slots[i] = { w, h, rt: [new THREE.WebGLRenderTarget(w, h, o), new THREE.WebGLRenderTarget(w, h, o)], cur: 0, door: s ? s.door : null };
  return s;
}

const _pc = new THREE.Vector3(), _pn = new THREE.Vector3(), _pT = new THREE.Matrix4(), _pl = new THREE.Plane(), _pq = new THREE.Vector4(), _pcl = new THREE.Vector4(), _ptp = new THREE.Vector3();
const _frus = new THREE.Frustum(), _pvm = new THREE.Matrix4(), _psph = new THREE.Sphere();
/* the door's world placement: its bottom-centre, the way in, and the world transform through it */
function doorWorld(D, c, n, Tw) {
  c.setFromMatrixPosition(D.F).applyMatrix4(D.r.m);
  n.set(0, 0, 1).transformDirection(D.F).transformDirection(D.r.m);
  if (Tw) Tw.copy(D.r.m).multiply(D.T).multiply(D.r.inv);
}

/* before the main render: draw the nearest doors' views */
function portalRender() {
  const doors = PORTAL.doors; if (!doors.length) return;
  camera.updateMatrixWorld();
  _pvm.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse); _frus.setFromProjectionMatrix(_pvm);
  const cand = [];
  for (const D of doors) {
    doorWorld(D, _pc, _pn);
    const d = _ptp.copy(camera.position).sub(_pc);
    D.mesh.visible = d.dot(_pn) <= 0.05;
    if (!D.mesh.visible) continue;          // from behind it is just an opening
    const dist = d.length(); if (dist > 48) { D.mat.uniforms.uOn.value = 0; continue; }
    _psph.center.copy(_pc).addScaledVector(new THREE.Vector3(0, 1, 0), D.h / 2); _psph.radius = Math.hypot(D.w, D.h) / 2 + 0.1;
    if (!_frus.intersectsSphere(_psph)) continue;
    cand.push([dist, D]);
  }
  cand.sort((a, b) => a[0] - b[0]);
  const use = cand.slice(0, PORTAL_MAX).map(c => c[1]);
  for (const D of doors) if (!use.includes(D) && !cand.some(c => c[1] === D)) D.mat.uniforms.uOn.value = 0;
  for (const c of cand.slice(PORTAL_MAX)) c[1].mat.uniforms.uOn.value = 0;
  const vc = PORTAL.vcam;
  for (let i = 0; i < use.length; i++) {
    const D = use[i], S_ = portalSlot(i);
    // keep a door in the slot it had, so its previous frame is its own
    if (S_.door !== D) { S_.door = D; }
    doorWorld(D, _pc, _pn, _pT);
    vc.matrixAutoUpdate = false;
    if (D.mirror) vc.matrix.copy(camera.matrixWorld); else vc.matrix.multiplyMatrices(_pT, camera.matrixWorld);
    vc.updateMatrixWorld(true);
    vc.projectionMatrix.copy(camera.projectionMatrix);
    // oblique near plane on the exit (for a mirror: its own plane, keeping what lies behind the glass)
    const exitC = D.mirror ? _ptp.copy(_pc) : _ptp.copy(_pc).applyMatrix4(_pT), exitN = D.mirror ? _pn.clone() : _pn.clone().transformDirection(_pT);
    _pl.setFromNormalAndCoplanarPoint(exitN, exitC.addScaledVector(exitN, -0.03)).applyMatrix4(vc.matrixWorldInverse);
    _pcl.set(_pl.normal.x, _pl.normal.y, _pl.normal.z, _pl.constant);
    const P = vc.projectionMatrix.elements;
    _pq.x = (Math.sign(_pcl.x) + P[8]) / P[0]; _pq.y = (Math.sign(_pcl.y) + P[9]) / P[5]; _pq.z = -1; _pq.w = (1 + P[10]) / P[14];
    _pcl.multiplyScalar(2 / _pcl.dot(_pq));
    P[2] = _pcl.x; P[6] = _pcl.y; P[10] = _pcl.z + 1; P[14] = _pcl.w;
    vc.projectionMatrixInverse.copy(vc.projectionMatrix).invert();
    const tgt = S_.rt[S_.cur ^ 1];
    D.pair.mesh.visible = false;
    if (D.mirror) { scene.matrixAutoUpdate = false; scene.matrix.copy(_pT); scene.updateMatrixWorld(true); if (D.floor) WU.uNoClip.value = 1; }
    renderer.setRenderTarget(tgt); renderer.clear(); renderer.render(scene, vc);
    if (D.mirror) { scene.matrix.identity(); scene.updateMatrixWorld(true); WU.uNoClip.value = 0; }
    D.pair.mesh.visible = true;
    S_.cur ^= 1;
    D.mat.uniforms.tP.value = tgt.texture; D.mat.uniforms.uRes.value.set(RW, RHh); D.mat.uniforms.uOn.value = 1;
  }
}

/* after the player moves: walked through a door? */
function portalCross() {
  // remember where you were in absolute terms, so a step that also crosses into the next cell or floor still counts
  const now = new THREE.Vector3(S.x, S.y + 1.0, S.z);
  const abs = [S.cx * RC + S.x, S.floor * RLH + S.y + 1.0, S.cz * RC + S.z];
  const pa = PORTAL.prevAbs;
  const prev = pa ? new THREE.Vector3(pa[0] - S.cx * RC, pa[1] - S.floor * RLH, pa[2] - S.cz * RC) : null;
  PORTAL.prevAbs = abs;
  if (!prev || prev.distanceTo(now) > 3 || !PORTAL.doors.length) return false;
  for (const D of PORTAL.doors) {
    if (D.mirror) continue;
    doorWorld(D, _pc, _pn, _pT);
    const s0 = _ptp.copy(prev).sub(_pc).dot(_pn), s1 = _ptp.copy(now).sub(_pc).dot(_pn);
    if (!(s0 < 0 && s1 >= 0)) continue;
    const k = s0 / (s0 - s1), hit = prev.clone().lerp(now, k);
    const loc = hit.applyMatrix4(D.r.inv).applyMatrix4(D.Fi);
    if (Math.abs(loc.x) > D.w / 2 || loc.y < -1.2 || loc.y > D.h) continue;
    // through: carry position, heading and velocity
    const p = new THREE.Vector3(S.x, S.y, S.z).applyMatrix4(_pT), dy = p.y - S.y;
    const f = new THREE.Vector3(-Math.sin(S.yaw), 0, -Math.cos(S.yaw)).transformDirection(_pT);
    const v = new THREE.Vector3(PL.vx || 0, 0, PL.vz || 0).transformDirection(_pT).multiplyScalar(Math.hypot(PL.vx || 0, PL.vz || 0));
    S.x = p.x; S.y = p.y; S.z = p.z; S.yaw = Math.atan2(-f.x, -f.z); PL.vx = v.x; PL.vz = v.z;
    if (PL.camY !== null) PL.camY += dy;
    PL.peak += dy;
    PORTAL.prevAbs = null;
    wrapPlayer(false); updateWorld(S.x, S.y, S.z, false); refreshBooks(true);
    return true;
  }
  return false;
}

beforeScene = portalRender;
