'use strict';
/* ==========================================================================
   Things that move: people's materials, the book in your hand, books on the
   floor, books thrown down a well, and the streaks of a long fall
   ========================================================================== */
const AMB = { col: new THREE.Vector3(1, 1, 1), top: new THREE.Vector3(1, 1, 1) };   // light where you are, from the room's bake
const PROP_VS = `
varying vec3 vN; varying vec2 vUv; varying vec3 vW; varying vec3 vC;
#ifdef BOOK
attribute float aFace; attribute vec3 aStyle; varying float vFace; varying vec3 vStyle;
#endif
void main(){
  vec4 p = vec4(position, 1.0); vec3 n = normal;
  #ifdef USE_INSTANCING
    p = instanceMatrix * p; n = mat3(instanceMatrix) * n;
  #endif
  vec4 w = modelMatrix * p; vW = w.xyz; vN = normalize(mat3(modelMatrix) * n); vUv = uv; vC = vec3(1.0);
  #ifdef USE_INSTANCING_COLOR
    vC = instanceColor;
  #endif
  #ifdef BOOK
    vFace = aFace; vStyle = aStyle;
  #endif
  gl_Position = projectionMatrix * viewMatrix * w;
}`;
const PROP_FS = `
uniform vec3 uColor; uniform sampler2D uMap; uniform float uHasMap; uniform vec3 uAmb; uniform vec3 uTop; uniform float uGloss; uniform vec3 uFogCol; uniform float uFogD;
varying vec3 vN; varying vec2 vUv; varying vec3 vW; varying vec3 vC;
#ifdef BOOK
varying float vFace; varying vec3 vStyle;
#endif
float h11(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void main(){
  vec3 N = normalize(vN), V = normalize(cameraPosition - vW);
  vec3 base = uColor * vC; float ao = 1.0;
  if (uHasMap > 0.5) base *= pow(texture2D(uMap, vUv).rgb, vec3(2.2)) * 1.6;
  #ifdef BOOK
    if (vFace < 0.5) {
      float bv = vUv.y, bu = vUv.x;
      base *= (0.86 + 0.14 * h11(floor(vUv * vec2(5.0, 70.0)) + vStyle.z * 91.0)) * (0.8 + 0.2 * sin(bu * 3.14159));
      float b1 = smoothstep(0.085, 0.095, bv) - smoothstep(0.115, 0.125, bv) + smoothstep(0.875, 0.885, bv) - smoothstep(0.905, 0.915, bv);
      float band = vStyle.x < 0.5 ? b1 : 0.0;
      base = mix(base, vec3(0.5, 0.32, 0.08), clamp(band, 0.0, 1.0) * 0.9);
    } else if (vFace < 1.5) { base = mix(base * 0.8, vec3(0.56, 0.5, 0.38), step(0.09, vUv.x) * step(vUv.x, 0.91)); ao = 0.8; }
    else base *= 0.75;
  #endif
  // soft light from the room: mostly from above, a little bounced from the floor
  float up = N.y * 0.5 + 0.5;
  vec3 L = mix(uAmb * 0.55, uTop, up) * (0.75 + 0.25 * max(dot(N, V), 0.0));
  vec3 col = base * L * ao;
  float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0);
  col += uTop * rim * 0.08 * uGloss;
  float d = length(vW - cameraPosition);
  col = mix(col, uFogCol, 1.0 - exp(-d * uFogD));
  gl_FragColor = vec4(clamp(col, 0.0, 40.0), 1.0);
}`;
function propMat(o = {}) {
  const defines = {}; if (o.book) defines.BOOK = 1;
  return new THREE.ShaderMaterial({
    defines, side: o.double ? THREE.DoubleSide : THREE.FrontSide,
    uniforms: { uColor: { value: o.color instanceof THREE.Color ? o.color : new THREE.Color(o.color !== undefined ? o.color : 0xffffff) }, uMap: { value: o.map || null }, uHasMap: { value: o.map ? 1 : 0 },
      uAmb: { value: AMB.col }, uTop: { value: AMB.top }, uGloss: { value: o.gloss !== undefined ? o.gloss : 0.3 }, uFogCol: WU.uFogCol, uFogD: WU.uFogD },
    vertexShader: PROP_VS, fragmentShader: PROP_FS
  });
}
function lathe(pts, seg) { return new THREE.LatheGeometry(pts.map(p => new THREE.Vector2(p[0], p[1])), seg); }

/* the book in your hands */
const heldGeo = bookGeometry(true);
const heldMat = propMat({ book: true, gloss: 0.2 });
const HELD = new THREE.Mesh(heldGeo, heldMat); HELD.visible = false; HELD.frustumCulled = false; camera.add(HELD);
function styleGeo(g, L) { const a = g.attributes.aStyle.array; for (let i = 0; i < a.length; i += 3) { a[i] = L.band; a[i + 1] = L.label; a[i + 2] = L.wear; } g.attributes.aStyle.needsUpdate = true; }
function showHeld(id) {
  if (!id) { HELD.visible = false; return; }
  const L = bookLook(id); styleGeo(heldGeo, L);
  heldMat.uniforms.uColor.value.setRGB(L.col[0], L.col[1], L.col[2]);
  HELD.scale.set(0.05, L.h, L.d); HELD.position.set(0.27, -0.26, -0.5); HELD.rotation.set(0.25, -0.55, 0.12); HELD.visible = true;
}
/* books lying where someone put them down: { id, cx, cz, floor, x, y, z, yaw } */
const groundPool = [];
for (let i = 0; i < 30; i++) { const g = bookGeometry(true), m = new THREE.Mesh(g, propMat({ book: true })); m.visible = false; m.frustumCulled = false; scene.add(m); groundPool.push(m); }
function updateGroundBooks() {
  let n = 0;
  for (const gb of S.ground) {
    gb._m = null;
    if (n >= groundPool.length) continue;
    const dx = (gb.cx - S.cx) * RC + gb.x, dz = (gb.cz - S.cz) * RC + gb.z, dy = (gb.floor - S.floor) * RLH + gb.y;
    if (Math.abs(dx) > 60 || Math.abs(dz) > 60 || Math.abs(dy) > 20) continue;
    const m = groundPool[n++], id = parseKey(gb.id), L = bookLook(id);
    styleGeo(m.geometry, L); m.material.uniforms.uColor.value.setRGB(L.col[0], L.col[1], L.col[2]);
    m.visible = true; m.scale.set(L.w, L.h, L.d); m.position.set(dx, dy + L.w / 2, dz); m.rotation.set(0, gb.yaw, Math.PI / 2); gb._m = m;
  }
  for (let i = n; i < groundPool.length; i++) groundPool[i].visible = false;
}
/* a book dropped into a shaft, tumbling out of sight */
const THROWN = [];
function throwBookVisual(id, x, y, z, vx, vz) {
  const g = bookGeometry(true), m = new THREE.Mesh(g, propMat({ book: true })), L = bookLook(id);
  styleGeo(g, L); m.material.uniforms.uColor.value.setRGB(L.col[0], L.col[1], L.col[2]); m.scale.set(L.w, L.h, L.d);
  m.position.set(x, y, z); m.frustumCulled = false; scene.add(m);
  THROWN.push({ m, vy: 1.5, vx: vx || 0, vz: vz || 0, spin: new THREE.Vector3(Math.random() * 6, Math.random() * 6, Math.random() * 6), t: 0 });
}
function updateThrown(dt, shift) {
  for (let i = THROWN.length - 1; i >= 0; i--) {
    const b = THROWN[i]; b.t += dt; b.vy -= 9.8 * dt;
    if (shift) b.m.position.sub(shift);
    b.m.position.x += b.vx * dt; b.m.position.y += b.vy * dt; b.m.position.z += b.vz * dt; b.vx *= Math.pow(0.4, dt); b.vz *= Math.pow(0.4, dt);
    b.m.rotation.x += b.spin.x * dt; b.m.rotation.y += b.spin.y * dt; b.m.rotation.z += b.spin.z * dt;
    if (b.t > 8) { scene.remove(b.m); b.m.geometry.dispose(); THROWN.splice(i, 1); }
  }
}
/* speed lines while falling */
const STREAK_N = 160;
const streakGeo = new THREE.BufferGeometry(); streakGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(STREAK_N * 6), 3));
const streakMat = new THREE.LineBasicMaterial({ color: new THREE.Color(1.4, 1.5, 1.6), transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
const STREAKS = new THREE.LineSegments(streakGeo, streakMat); STREAKS.frustumCulled = false; scene.add(STREAKS);
const streakSeed = Array.from({ length: STREAK_N }, () => [Math.random(), Math.random(), Math.random()]);
function updateStreaks(speed) {
  const k = clamp((speed - 12) / 30, 0, 1); streakMat.opacity = k * 0.35;
  STREAKS.visible = k > 0.01; if (!STREAKS.visible) return;
  const a = streakGeo.attributes.position.array, cp = camera.position, t = performance.now() / 1000;
  for (let i = 0; i < STREAK_N; i++) {
    const s = streakSeed[i], ang = s[0] * Math.PI * 2, r = 1.2 + s[1] * 5;
    const y = mod(s[2] * 40 + t * speed * 0.9, 40) - 20, len = 1 + k * 4;
    const x = cp.x + Math.cos(ang) * r, z = cp.z + Math.sin(ang) * r;
    a[i * 6] = x; a[i * 6 + 1] = cp.y + y; a[i * 6 + 2] = z; a[i * 6 + 3] = x; a[i * 6 + 4] = cp.y + y - len; a[i * 6 + 5] = z;
  }
  streakGeo.attributes.position.needsUpdate = true;
}
