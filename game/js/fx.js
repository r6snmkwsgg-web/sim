'use strict';
/* ==========================================================================
   Room effects and secrets. Rooms declare, in their metadata:
     fx:      [{type: 'rain'|'snow'|'dust'|'embers'|'fog'|'lightning'|'aurora'|'beam', box: [x0,y0,z0,x1,y1,z1], ...}]
     secrets: [{at: [x,y,z], r, name, text}]
   in Blender axes (x east, y north, z up); here that is room-local (x, z, y).
   Particles live in the room's group, so they move with it; the GPU animates them from uTime.
   ========================================================================== */
const FX = { flash: 0, bolts: [], checkT: 0 };

const fxBox = b => ({ x0: Math.min(b[0], b[3]), x1: Math.max(b[0], b[3]), y0: Math.min(b[2], b[5]), y1: Math.max(b[2], b[5]), z0: Math.min(b[1], b[4]), z1: Math.max(b[1], b[4]) });   // -> local x, height y, z
const fxPt = p => new THREE.Vector3(p[0], p[2], p[1]);

const FX_VS_HEAD = `
uniform float uTime; uniform vec3 uMin; uniform vec3 uSize; attribute vec4 aSeed;
vec3 wrapIn(vec3 p) { return uMin + mod(p - uMin, uSize); }`;

/* falling streaks: two vertices per drop, the second a little above the first */
function rainFx(b, o) {
  const n = Math.min(3200, Math.max(200, Math.round((b.x1 - b.x0) * (b.z1 - b.z0) * 3.2)));
  const seed = new Float32Array(n * 8), end = new Float32Array(n * 2), pos = new Float32Array(n * 6);
  for (let i = 0; i < n; i++) {
    const s = [Math.random(), Math.random(), Math.random(), Math.random()];
    for (let k = 0; k < 2; k++) { seed.set(s, (i * 2 + k) * 4); end[i * 2 + k] = k; }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 4)); g.setAttribute('aEnd', new THREE.BufferAttribute(end, 1));
  const m = new THREE.ShaderMaterial({
    uniforms: { uTime: WU.uTime, uMin: { value: new THREE.Vector3(b.x0, b.y0, b.z0) }, uSize: { value: new THREE.Vector3(b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0) }, uSpeed: { value: o.speed || 9 } },
    vertexShader: FX_VS_HEAD + `
      uniform float uSpeed; attribute float aEnd; varying float vA;
      void main() {
        vec3 p = uMin + aSeed.xyz * uSize;
        p.y = uMin.y + mod(aSeed.y * uSize.y - uTime * uSpeed * (0.85 + 0.3 * aSeed.w), uSize.y) + aEnd * 0.42;
        p.x += aEnd * 0.03;
        vA = 1.0 - aEnd;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
      }`,
    fragmentShader: `varying float vA; void main() { gl_FragColor = vec4(vec3(0.75, 0.8, 0.88) * 0.45, 0.35 * (0.4 + 0.6 * vA)); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending
  });
  return new THREE.LineSegments(g, m);
}

/* soft round points: snow drifts down and sways; dust hangs and wanders; embers rise */
function pointFx(b, o, kind) {
  const vol = (b.x1 - b.x0) * (b.z1 - b.z0) * (b.y1 - b.y0);
  const n = kind === 'snow' ? Math.min(2600, Math.max(200, Math.round(vol * 0.35))) : kind === 'dust' ? Math.min(700, Math.max(80, Math.round(vol * 0.05))) : Math.min(500, Math.max(60, Math.round(vol * 0.04)));
  const seed = new Float32Array(n * 4), pos = new Float32Array(n * 3);
  for (let i = 0; i < n * 4; i++) seed[i] = Math.random();
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 4));
  const P = { snow: { fall: 0.9, sway: 0.5, size: 0.09, col: [0.95, 0.96, 1.0], a: 0.9, add: false },
              dust: { fall: 0.02, sway: 0.25, size: 0.018, col: [1.0, 0.9, 0.7], a: 0.55, add: true },
              embers: { fall: -0.6, sway: 0.35, size: 0.035, col: [1.0, 0.55, 0.2], a: 0.9, add: true } }[kind];
  const m = new THREE.ShaderMaterial({
    uniforms: { uTime: WU.uTime, uMin: { value: new THREE.Vector3(b.x0, b.y0, b.z0) }, uSize: { value: new THREE.Vector3(b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0) },
      uFall: { value: P.fall }, uSway: { value: P.sway }, uPt: { value: P.size }, uCol: { value: new THREE.Vector3(...P.col) }, uA: { value: P.a }, uScale: { value: renderer.domElement.height * 0.5 } },
    vertexShader: FX_VS_HEAD + `
      uniform float uFall; uniform float uSway; uniform float uPt; uniform float uScale; varying float vTw;
      void main() {
        vec3 p = uMin + aSeed.xyz * uSize;
        float t = uTime * (0.7 + 0.6 * aSeed.w);
        p.y -= t * uFall;
        p.x += sin(t * 0.9 + aSeed.w * 30.0) * uSway; p.z += cos(t * 0.7 + aSeed.x * 20.0) * uSway;
        p = wrapIn(p);
        vTw = 0.6 + 0.4 * sin(uTime * 2.0 + aSeed.z * 40.0);
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_PointSize = clamp(uPt * uScale / -mv.z, 1.0, 24.0);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: `uniform vec3 uCol; uniform float uA; varying float vTw;
      void main() { float d = length(gl_PointCoord - 0.5); if (d > 0.5) discard; gl_FragColor = vec4(uCol, uA * vTw * smoothstep(0.5, 0.1, d)); }`,
    transparent: true, depthWrite: false, blending: P.add ? THREE.AdditiveBlending : THREE.NormalBlending
  });
  return new THREE.Points(g, m);
}

/* aurora: a few tall curtains of light near the top of the box */
function auroraFx(b) {
  const grp = new THREE.Group();
  const m = new THREE.ShaderMaterial({
    uniforms: { uTime: WU.uTime },
    vertexShader: `varying vec2 vUv; uniform float uTime;
      void main() { vUv = uv; vec3 p = position; p.z += sin(p.x * 0.12 + uTime * 0.15) * 3.0 + sin(p.x * 0.31 - uTime * 0.23) * 1.2;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0); }`,
    fragmentShader: `varying vec2 vUv; uniform float uTime;
      void main() {
        float band = 0.5 + 0.5 * sin(vUv.x * 40.0 + uTime * 0.4 + sin(vUv.x * 9.0 - uTime * 0.2) * 3.0);
        float fold = pow(band, 3.0) * (0.35 + 0.65 * (0.5 + 0.5 * sin(vUv.x * 7.0 - uTime * 0.3)));
        float v = smoothstep(0.0, 0.25, vUv.y) * (1.0 - smoothstep(0.3, 1.0, vUv.y));
        vec3 c = mix(vec3(0.15, 1.0, 0.45), vec3(0.55, 0.25, 0.9), smoothstep(0.35, 1.0, vUv.y));
        gl_FragColor = vec4(c * fold * v * 0.9, 1.0);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide
  });
  const W = b.x1 - b.x0, H = Math.max(4, (b.y1 - b.y0) * 0.6);
  for (let k = 0; k < 3; k++) {
    const g = new THREE.PlaneGeometry(W * 1.2, H, 64, 1);
    const mesh = new THREE.Mesh(g, m);
    mesh.position.set((b.x0 + b.x1) / 2, b.y1 - H / 2 - k * 1.5, b.z0 + (b.z1 - b.z0) * (0.25 + k * 0.25));
    grp.add(mesh);
  }
  return grp;
}

/* a lighthouse beam turning about a point */
function beamFx(o) {
  const at = fxPt(o.at), L = o.r || 30;
  const g = new THREE.ConeGeometry(L * 0.12, L, 24, 1, true); g.translate(0, -L / 2, 0); g.rotateZ(Math.PI / 2);
  const m = new THREE.ShaderMaterial({
    uniforms: { uL: { value: L } },
    vertexShader: `varying float vD; uniform float uL; void main() { vD = clamp(position.x / uL, 0.0, 1.0); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `varying float vD; void main() { gl_FragColor = vec4(vec3(1.0, 0.92, 0.7) * 0.22 * pow(1.0 - vD, 1.6), 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide
  });
  const piv = new THREE.Group(); piv.position.copy(at);
  const a = new THREE.Mesh(g, m), b2 = new THREE.Mesh(g, m); b2.rotation.y = Math.PI;
  piv.add(a, b2); piv.userData.spin = o.speed || 0.5;
  return piv;
}

/* lightning: a jagged bolt from the top of the box to where it strikes, drawn for a moment */
function boltMesh(b, at) {
  const top = new THREE.Vector3(at.x + (Math.random() - 0.5) * 3, b.y1, at.z + (Math.random() - 0.5) * 3);
  const pts = [], n = 12;
  for (let i = 0; i <= n; i++) {
    const p = top.clone().lerp(at, i / n);
    if (i > 0 && i < n) { p.x += (Math.random() - 0.5) * 0.9; p.z += (Math.random() - 0.5) * 0.9; }
    pts.push(p);
  }
  const g = new THREE.BufferGeometry().setFromPoints(pts);
  return new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0xe8f0ff, transparent: true, blending: THREE.AdditiveBlending }));
}

/* build a placed room's effects (called when a room instance is made) */
function fxPlace(r) {
  const M = r.pf.meta;
  r.fx = [];
  for (const o of M.fx || []) {
    let obj = null;
    const b = o.box ? fxBox(o.box) : null;
    if (o.type === 'rain' && b) obj = rainFx(b, o);
    else if ((o.type === 'snow' || o.type === 'dust' || o.type === 'embers') && b) obj = pointFx(b, o, o.type);
    else if (o.type === 'aurora' && b) obj = auroraFx(b);
    else if (o.type === 'beam' && o.at) obj = beamFx(o);
    else if (o.type === 'lightning' && b) r.fx.push({ o, b, at: o.at ? fxPt(o.at) : new THREE.Vector3((b.x0 + b.x1) / 2, b.y0, (b.z0 + b.z1) / 2), t: 4 + Math.random() * 8 });
    else if (o.type === 'fog' && b) r.fx.push({ o, b, fog: o.density || 0.05 });
    if (obj) { obj.frustumCulled = false; obj.renderOrder = 6; r.grp.add(obj); r.fx.push({ o, obj }); }
  }
}
function fxDrop(r) {
  for (const f of r.fx || []) if (f.obj) {
    r.grp.remove(f.obj);
    f.obj.traverse(c => { if (c.geometry) c.geometry.dispose(); if (c.material) c.material.dispose(); });
  }
  r.fx = null;
}

const _fxP = new THREE.Vector3();
/* per frame: spin beams, strike lightning in the room you are in, thicken fog inside fog boxes, notice secrets */
function fxTick(dt) {
  FX.flash = Math.max(0, FX.flash - dt * 5);
  for (let i = FX.bolts.length - 1; i >= 0; i--) {
    const bo = FX.bolts[i]; bo.t -= dt;
    bo.line.material.opacity = Math.max(0, bo.t / 0.25);
    if (bo.t <= 0) { bo.r.grp.remove(bo.line); bo.line.geometry.dispose(); bo.line.material.dispose(); FX.bolts.splice(i, 1); }
  }
  const here = PL.room;
  let fogD = 0;
  if (here) _fxP.set(S.x, S.y + 1.6, S.z).applyMatrix4(here.inv);
  for (const r of WORLD.inst.values()) {
    if (!r.fx) continue;
    for (const f of r.fx) {
      if (f.obj && f.obj.userData.spin) f.obj.rotation.y += dt * f.obj.userData.spin;
      if (f.o.type === 'lightning' && r === here) {
        f.t -= dt;
        if (f.t <= 0) {
          f.t = 6 + Math.random() * 12;
          const line = boltMesh(f.b, f.at); r.grp.add(line); FX.bolts.push({ r, line, t: 0.25 });
          FX.flash = 1.2;
          const d = 0.4 + Math.random() * 1.2;
          setTimeout(() => { if (AU.ctx) { burst({ dur: 2.2, type: 'lowpass', f: 180, gain: 0.8, rev: 1.2 }); tone(45, 30, 1.8, 0.35); } }, d * 1000);
        }
      }
      if (f.fog && r === here) {
        const b = f.b;
        if (_fxP.x > b.x0 && _fxP.x < b.x1 && _fxP.z > b.z0 && _fxP.z < b.z1 && _fxP.y > b.y0 - 1 && _fxP.y < b.y1 + 1) fogD = Math.max(fogD, f.fog);
      }
    }
  }
  if (fogD > 0) { WU.uFogD.value = fogD; WU.uFogCol.value.setRGB(0.42, 0.42, 0.43).multiplyScalar(Math.min(1, 0.4 + dayK * 0.6)); }
  FX.checkT -= dt;
  if (FX.checkT <= 0) { FX.checkT = 0.25; checkSecrets(); }
}

function checkSecrets() {
  const r = PL.room; if (!r || !r.pf.meta.secrets) return;
  for (const s of r.pf.meta.secrets) {
    const key = 'sec:' + r.pf.name + ':' + s.name;
    if (S.flags[key]) continue;
    _fxP.copy(fxPt(s.at)).applyMatrix4(r.m);
    const dx = S.x - _fxP.x, dz = S.z - _fxP.z, dy = S.y - _fxP.y;
    if (dx * dx + dz * dz < (s.r || 1.5) * (s.r || 1.5) && Math.abs(dy) < 2.2) {
      S.flags[key] = S.day;
      S.stats.secrets = (S.stats.secrets || 0) + 1;
      SFX.chime();
      toast(`Secret: ${s.name}. ${s.text || ''}`.trim());
      logJ(`Found a secret place: ${s.name}${s.text ? '. ' + s.text : '.'}`);
      save();
    }
  }
}
