'use strict';
/* ==========================================================================
   World: the dream rooms. Geometry and light are baked in Blender (see
   rooms/); here they get their tiles, grout, reflections, water and books.
   ========================================================================== */
const RC = 16, RLH = 8;   // cell size and level height, metres
const ASSET_BASE = location.pathname.includes('/dev/') ? '../' : '';

const SHAFT_U = { tDepth: { value: null }, uRes: { value: new THREE.Vector2() }, uProjInv: { value: new THREE.Matrix4() }, uStr: { value: 0.14 } };
const WU = {   // shared by every room material
  uDay: { value: 1 }, uTime: { value: 0 }, uFogCol: { value: new THREE.Color(0.5, 0.52, 0.55) }, uFogD: { value: 0.006 },
  uProbeOn: { value: 1 }, uCaus: { value: 1 }
};
const MAX_ANISO = renderer.capabilities.getMaxAnisotropy();

/* Per-material look. k: shader family. Albedo comes from the room file (the same numbers the bake used). */
const KINDS = {
  tile:     { k: 0, size: 0.15, grout: 0.006, jit: 0.07, gloss: 1.0, f0: 0.045, rough: 0.05 },
  floor:    { k: 0, size: 0.25, grout: 0.007, jit: 0.09, gloss: 0.8, f0: 0.04, rough: 0.1 },
  pink:     { k: 0, size: 0.15, grout: 0.006, jit: 0.08, gloss: 1.0, f0: 0.045, rough: 0.05 },
  mint:     { k: 0, size: 0.15, grout: 0.006, jit: 0.08, gloss: 1.0, f0: 0.045, rough: 0.05 },
  mosaic:   { k: 1, size: 0.025, grout: 0.003, gloss: 0.7, f0: 0.04, rough: 0.12, pal: [[0.30, 0.64, 0.72], [0.20, 0.50, 0.66], [0.46, 0.77, 0.80], [0.84, 0.88, 0.86]] },
  cobalt:   { k: 1, size: 0.025, grout: 0.003, gloss: 0.7, f0: 0.04, rough: 0.12, pal: [[0.12, 0.24, 0.58], [0.10, 0.18, 0.46], [0.20, 0.36, 0.70], [0.80, 0.84, 0.86]] },
  plaster:  { k: 2, gloss: 0.0, f0: 0.02, rough: 0.6 },
  terrazzo: { k: 3, gloss: 0.55, f0: 0.04, rough: 0.14 },
  paper:    { k: 4, gloss: 0.0, f0: 0.02, rough: 0.6 },
  carpet:   { k: 5, gloss: 0.0, f0: 0.0, rough: 1.0 },
  ceiltile: { k: 6, gloss: 0.0, f0: 0.02, rough: 0.6 },
  wood:     { k: 7, gloss: 0.3, f0: 0.04, rough: 0.25 },
  oak:      { k: 7, gloss: 0.3, f0: 0.04, rough: 0.25 },
  paint:    { k: 8, gloss: 0.45, f0: 0.04, rough: 0.18 },
  bed:      { k: 8, gloss: 0.0, f0: 0.02, rough: 0.8 },
  kiosk:    { k: 8, gloss: 0.7, f0: 0.05, rough: 0.08 },
  black:    { k: 8, gloss: 0.5, f0: 0.04, rough: 0.1 },
  brass:    { k: 9, gloss: 1.0, f0: 1.0, rough: 0.12 },
  chrome:   { k: 9, gloss: 1.0, f0: 1.0, rough: 0.04 },
  books:    { k: 10, gloss: 0.0, f0: 0.0, rough: 1.0 },
  // the library palette
  stone:    { k: 11, gloss: 0.18, f0: 0.03, rough: 0.35 },
  parquet:  { k: 12, gloss: 0.55, f0: 0.04, rough: 0.14 },
  marble:   { k: 13, gloss: 1.0, f0: 0.045, rough: 0.04 },
  green:    { k: 8, gloss: 0.35, f0: 0.04, rough: 0.2 },
  oxblood:  { k: 8, gloss: 0.35, f0: 0.04, rough: 0.2 },
  damask:   { k: 4, gloss: 0.0, f0: 0.02, rough: 0.6 },
  iron:     { k: 9, gloss: 0.8, f0: 1.0, rough: 0.3 },
  bronze:   { k: 9, gloss: 1.0, f0: 1.0, rough: 0.2 },
  gilt:     { k: 9, gloss: 1.0, f0: 1.0, rough: 0.1 },
  velvet:   { k: 5, gloss: 0.0, f0: 0.0, rough: 1.0 },
  slate:    { k: 11, gloss: 0.3, f0: 0.04, rough: 0.2 },
  blackboard: { k: 8, gloss: 0.1, f0: 0.03, rough: 0.5 },
  leather:  { k: 8, gloss: 0.3, f0: 0.04, rough: 0.3 },
  ivory:    { k: 8, gloss: 0.4, f0: 0.04, rough: 0.2 },
  walnut:   { k: 7, gloss: 0.4, f0: 0.04, rough: 0.2 },
};

const ROOM_VS = `
attribute vec2 uv2;
varying vec3 vL; varying vec3 vN; varying vec2 vUv; varying vec2 vUv2; varying vec3 vCam;
void main(){
  vec3 p = position;
  #ifdef KIND
  #if KIND == 10
    p -= normal * 0.035;
  #endif
  #endif
  vL = p; vN = normal; vUv = uv; vUv2 = uv2;
  vCam = (inverse(modelMatrix) * vec4(cameraPosition, 1.0)).xyz;
  gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
}`;

const ROOM_COMMON = `
uniform sampler2D tLMd; uniform sampler2D tLMn; uniform float uDay; uniform float uTime;
uniform samplerCube tProbe; uniform samplerCube tProbeN; uniform vec3 uProbeP; uniform vec3 uBoxMin; uniform vec3 uBoxMax; uniform float uProbeOn;
uniform vec3 uFogCol; uniform float uFogD; uniform float uCaus;
uniform vec4 uWat[4]; uniform vec2 uWatH[4];
float hash21(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash21(i), hash21(i + vec2(1.0, 0.0)), f.x), mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), f.x), f.y); }
vec3 decodeLM(vec3 y){ vec3 v = pow(y, vec3(2.2)); return v / max(1.0 - v, 0.003); }
vec3 lightmap(vec2 uv){ return mix(decodeLM(texture2D(tLMn, uv).rgb), decodeLM(texture2D(tLMd, uv).rgb), uDay); }
mat3 tbn(vec3 N, vec3 p, vec2 uv){
  vec3 dp1 = dFdx(p), dp2 = dFdy(p); vec2 du1 = dFdx(uv), du2 = dFdy(uv);
  vec3 dp2p = cross(dp2, N), dp1p = cross(N, dp1);
  vec3 T = dp2p * du1.x + dp1p * du2.x, B = dp2p * du1.y + dp1p * du2.y;
  float im = inversesqrt(max(max(dot(T, T), dot(B, B)), 1e-20));
  return mat3(T * im, B * im, N);
}
vec3 probe(vec3 P, vec3 R, float rough){
  vec3 Rs = R + vec3(1e-5);
  vec3 a = (uBoxMax - P) / Rs, b = (uBoxMin - P) / Rs, m = max(a, b);
  float t = min(min(m.x, m.y), m.z);
  vec3 d = P + R * max(t, 0.0) - uProbeP;
  vec3 dayC = textureCube(tProbe, d, rough * 7.0).rgb;
  if (uDay > 0.99) return dayC;
  return mix(textureCube(tProbeN, d, rough * 7.0).rgb, dayC, uDay);
}
/* Water: which volume holds this point, and how deep under its surface */
float underwater(vec3 P, out float top){
  top = -1e5; float best = 0.0;
  for (int i = 0; i < 4; i++) {
    vec4 w = uWat[i]; vec2 h = uWatH[i];
    if (h.x <= h.y) continue;
    bool inside = w.w > 0.0 ? length(P.xz - w.xy) < w.w + 0.02 : (P.x > w.x - 0.02 && P.x < -w.w + 0.02 && P.z > w.y - 0.02 && P.z < w.z + 0.02);
    if (inside && P.y < h.x && P.y > h.y - 0.05) { top = h.x; best = h.x - P.y; }
  }
  return best;
}
/* light bounced off a pool's surface onto what is above and around it */
float poolReflect(vec3 P, vec3 N){
  float best = 0.0;
  for (int i = 0; i < 4; i++) {
    vec4 w = uWat[i]; vec2 h = uWatH[i];
    if (h.x <= h.y) continue;
    float d = w.w > 0.0 ? max(length(P.xz - w.xy) - w.w, 0.0) : length(max(max(vec2(w.x, w.y) - P.xz, P.xz - vec2(-w.w, w.z)), 0.0));
    float up = P.y - h.x;
    if (up < 0.02 || up > 7.0) continue;
    float k = (1.0 - smoothstep(0.0, 3.5, d)) * (1.0 - smoothstep(1.0, 7.0, up)) * (0.4 + 0.6 * max(-N.y, 0.0) + 0.3 * (1.0 - abs(N.y)));
    best = max(best, k);
  }
  return best;
}
float causticsAt(vec2 p, float t){
  float c = 0.0; vec2 q = p * 1.7;
  for (int i = 0; i < 3; i++) {
    float fi = float(i);
    vec2 w = q * (1.0 + fi * 0.6) + vec2(t * (0.23 + fi * 0.07), -t * (0.17 + fi * 0.05));
    vec2 g = vec2(vnoise(w), vnoise(w + 7.3)) * 6.2831;
    c += pow(0.5 + 0.5 * sin(q.x * (2.3 + fi) + g.x + t * 0.9) * sin(q.y * (2.1 + fi * 0.8) + g.y - t * 0.7), 6.0);
  }
  return c;
}
vec3 safeCol(vec3 c){
  #if __VERSION__ >= 300
    if (any(isnan(c)) || any(isinf(c))) return vec3(0.0);
  #endif
  return clamp(c, 0.0, 60.0);
}`;

const ROOM_FS = `
uniform vec3 uAlb; uniform float uSize; uniform float uGrout; uniform float uJit; uniform float uGloss; uniform float uF0; uniform float uRough;
uniform vec3 uP0; uniform vec3 uP1; uniform vec3 uP2; uniform vec3 uP3; uniform sampler2D tTex;
varying vec3 vL; varying vec3 vN; varying vec2 vUv; varying vec2 vUv2; varying vec3 vCam;
${ROOM_COMMON}
void tiles(vec2 uv, float size, float grout, vec3 alb, float jit, out vec3 A, out vec2 bump, out float gm){
  vec2 p = uv / size; vec2 c = floor(p); vec2 f = p - c;
  vec2 w = fwidth(p);
  float g = grout / size * 0.5;
  vec2 e = min(f, 1.0 - f);
  vec2 gg = 1.0 - smoothstep(vec2(g) - w * 0.75, vec2(g) + w * 0.75, e);
  gm = max(gg.x, gg.y);
  float far = smoothstep(0.06, 0.3, max(w.x, w.y));
  gm = mix(gm, min(1.0, 4.0 * g), far);
  float h = hash21(c + 17.0), h2 = hash21(c + 91.0);
  vec3 t = alb * (1.0 + (h - 0.5) * jit) * (1.0 + (h2 - 0.5) * jit * vec3(0.4, 0.2, -0.3));
  A = mix(t, alb * 0.5, gm);
  vec2 bv = (1.0 - smoothstep(vec2(g), vec2(g + 0.09), e)) * sign(f - 0.5);
  bump = bv * 0.6 * (1.0 - far) * (1.0 - gm);
  // glaze: a slight waviness in every tile catches the reflections
  bump += (vec2(vnoise(p * 3.1 + h * 40.0), vnoise(p * 3.1 + 11.0 + h * 40.0)) - 0.5) * 0.06 * (1.0 - far);
}
void main(){
  vec3 N = normalize(vN);
  #if KIND == 10
    if (!gl_FrontFacing) N = -N;
  #endif
  vec3 V = normalize(vL - vCam);
  vec3 A = uAlb; float gloss = uGloss, rough = uRough, gm = 0.0, ao = 1.0; vec2 bump = vec2(0.0); float metal = 0.0;
  #if KIND == 0
    tiles(vUv, uSize, uGrout, uAlb, uJit, A, bump, gm);
    gloss *= 1.0 - gm;
  #elif KIND == 1
    vec2 p = vUv / uSize; vec2 c = floor(p); vec2 f = p - c; vec2 w = fwidth(p);
    float h = hash21(c);
    vec3 t = h < 0.45 ? uP0 : h < 0.78 ? uP1 : h < 0.95 ? uP2 : uP3;
    vec3 avg = uP0 * 0.45 + uP1 * 0.33 + uP2 * 0.17 + uP3 * 0.05;
    float far = smoothstep(0.1, 0.45, max(w.x, w.y));
    vec2 e = min(f, 1.0 - f); float g = uGrout / uSize * 0.5;
    vec2 gg = 1.0 - smoothstep(vec2(g) - w * 0.75, vec2(g) + w * 0.75, e);
    gm = mix(max(gg.x, gg.y), 0.2, far);
    A = mix(mix(t, avg, far), vec3(0.62, 0.66, 0.64), gm * 0.8) * (uAlb / max(avg, vec3(0.05)));
    gloss *= 1.0 - gm;
  #elif KIND == 2
    float n = vnoise(vUv * 3.0) * 0.5 + vnoise(vUv * 11.0) * 0.3 + vnoise(vUv * 37.0) * 0.2;
    A *= 0.93 + 0.1 * n;
  #elif KIND == 3
    float s = hash21(floor(vUv * 90.0)), s2 = hash21(floor(vUv * 37.0) + 3.0);
    A *= 0.94 + 0.1 * vnoise(vUv * 2.0);
    A = mix(A, vec3(0.32, 0.30, 0.28), step(0.93, s) * 0.8);
    A = mix(A, vec3(0.86, 0.62, 0.52), step(0.96, s2) * 0.6);
  #elif KIND == 4
    float stripe = smoothstep(0.02, 0.0, abs(fract(vUv.x / 0.26) - 0.5) - 0.44);
    float motif = smoothstep(0.42, 0.38, length(fract(vUv * vec2(1.0 / 0.26, 1.0 / 0.34)) - 0.5));
    A *= 0.9 + 0.08 * vnoise(vUv * 5.0);
    A = mix(A, A * 0.82, stripe * 0.7 + motif * 0.25);
    A *= 1.0 - 0.18 * smoothstep(0.6, 1.0, vnoise(vUv * 0.7 + 3.0));   // water stains
  #elif KIND == 5
    float n = vnoise(vUv * 40.0) * 0.4 + vnoise(vUv * 160.0) * 0.4 + vnoise(vUv * 3.0) * 0.4;
    A *= 0.72 + 0.4 * n;
    A *= 1.0 - 0.22 * smoothstep(0.55, 0.9, vnoise(vUv * 0.5 + 9.0));
    A = mix(A, vec3(dot(A, vec3(0.333))), 0.25) * 0.8;
  #elif KIND == 6
    vec2 g = abs(fract(vUv / 0.6) - 0.5);
    float edge = smoothstep(0.475, 0.49, max(g.x, g.y));
    float dots = step(0.82, hash21(floor(vUv * 70.0)));
    A *= (1.0 - edge * 0.35) * (1.0 - dots * 0.12);
  #elif KIND == 7
    vec3 wt = pow(texture2D(tTex, vUv * vec2(0.5, 2.0)).rgb, vec3(2.2));
    A = uAlb * wt / max(dot(wt, vec3(0.333)), 0.05) * 0.95;
  #elif KIND == 8
    A *= 0.96 + 0.06 * vnoise(vUv * 9.0);
  #elif KIND == 9
    metal = 1.0;
    A *= 0.9 + 0.12 * vnoise(vUv * vec2(3.0, 60.0));
  #elif KIND == 10
    // the far shelves: spines drawn from a hash of their slot, in the same cloth colours as the real books
    float bw = 0.047; float u = vUv.x / bw; float bi = floor(u); float fu = u - bi;
    float h = hash21(vec2(bi, floor(vL.y * 3.0) + 7.0)), h2 = hash21(vec2(bi + 17.0, floor(vL.y * 3.0)));
    vec3 pal[6]; pal[0] = vec3(0.16, 0.03, 0.022); pal[1] = vec3(0.05, 0.1, 0.057); pal[2] = vec3(0.027, 0.045, 0.107); pal[3] = vec3(0.32, 0.19, 0.04); pal[4] = vec3(0.1, 0.057, 0.036); pal[5] = vec3(0.09, 0.11, 0.14);
    int pi = int(floor(h * 6.0)); vec3 bc = pal[0];
    for (int i = 1; i < 6; i++) if (i == pi) bc = pal[i];
    bc *= 0.8 + 0.45 * h2;
    float top = 0.74 + 0.24 * hash21(vec2(bi, 3.0));
    float bookm = step(vUv.y, top * 0.36) * smoothstep(0.0, 0.08, fu) * smoothstep(1.0, 0.92, fu);
    float band = smoothstep(0.02, 0.0, abs(vUv.y - top * 0.36 * 0.12)) + smoothstep(0.02, 0.0, abs(vUv.y - top * 0.36 * 0.88));
    A = mix(vec3(0.035), mix(bc, vec3(0.5, 0.32, 0.08), clamp(band, 0.0, 1.0) * 0.7) * (0.85 + 0.25 * sin(fu * 3.14159)), bookm);
    float bw2 = fwidth(u); A = mix(A, vec3(0.08, 0.06, 0.05), smoothstep(0.35, 1.2, bw2));
  #elif KIND == 11
    // limestone in courses: 0.9 x 0.42 m blocks, running bond, fine joints, every block its own shade
    vec2 bs = vec2(0.9, 0.42); vec2 p = vUv / bs; p.x += 0.5 * mod(floor(p.y), 2.0);
    vec2 c = floor(p); vec2 f = p - c; vec2 em = min(f, 1.0 - f) * bs; vec2 fw = fwidth(vUv);
    vec2 gg = 1.0 - smoothstep(vec2(0.004) - fw, vec2(0.004) + fw, em);
    float far = smoothstep(0.02, 0.08, max(fw.x, fw.y));
    gm = mix(max(gg.x, gg.y), 0.08, far);
    float h = hash21(c + 5.0);
    A = uAlb * (0.88 + 0.22 * h) * (0.9 + 0.14 * vnoise(vUv * 5.0 + h * 9.0)) * (0.95 + 0.08 * vnoise(vUv * 43.0));
    A = mix(A, uAlb * 0.55, gm);
    bump = (1.0 - smoothstep(vec2(0.004), vec2(0.03), em)) * sign(f - 0.5) * 0.35 * (1.0 - far);
    gloss *= 1.0 - gm;
  #elif KIND == 12
    // oak planks 14 cm wide, staggered ends, the grain from the wood texture
    vec2 ps = vec2(1.1, 0.14); vec2 p = vUv / ps; float row = floor(p.y); p.x += hash21(vec2(row, 3.0)) * 2.0;
    vec2 c = floor(p); vec2 f = p - c; vec2 em = min(f, 1.0 - f) * ps; vec2 fw = fwidth(vUv);
    vec2 gg = 1.0 - smoothstep(vec2(0.0015) - fw, vec2(0.0015) + fw, em);
    float far = smoothstep(0.02, 0.08, max(fw.x, fw.y));
    gm = mix(max(gg.x, gg.y), 0.05, far);
    float h = hash21(c + 31.0);
    vec3 wt = pow(texture2D(tTex, vec2(vUv.x * 0.45 + h * 5.3, vUv.y * 1.7 + h * 3.1)).rgb, vec3(2.2));
    A = uAlb * mix(wt / max(dot(wt, vec3(0.333)), 0.05), vec3(1.0), 0.35) * (0.78 + 0.44 * h);
    A = mix(A, uAlb * 0.3, gm);
    gloss *= 1.0 - gm;
  #elif KIND == 13
    // polished marble, cream and near-black in 60 cm squares, veined
    float sq = 0.6; vec2 p = vUv / sq; vec2 c = floor(p); vec2 f = p - c; vec2 fw = fwidth(vUv);
    float chk = mod(c.x + c.y, 2.0);
    vec3 cream = vec3(0.80, 0.76, 0.68), dark = vec3(0.10, 0.11, 0.10), avg = (cream + dark) * 0.5;
    vec3 base = chk > 0.5 ? dark : cream;
    float v = vnoise(vUv * 1.6 + c * 7.13) * 0.65 + vnoise(vUv * 5.0 + c * 3.1) * 0.35;
    float vein = 1.0 - smoothstep(0.0, 0.01 + fw.x * 1.5, abs(v - 0.52));
    base = mix(base, chk > 0.5 ? vec3(0.34, 0.33, 0.30) : vec3(0.58, 0.55, 0.50), vein * 0.4);
    base *= 0.94 + 0.1 * vnoise(vUv * 9.0 + c);
    vec2 em = min(f, 1.0 - f) * sq;
    vec2 gg = 1.0 - smoothstep(vec2(0.0015) - fw, vec2(0.0015) + fw, em);
    gm = mix(max(gg.x, gg.y), 0.02, smoothstep(0.02, 0.08, max(fw.x, fw.y)));
    A = mix(base, vec3(0.3, 0.28, 0.25), gm) * (uAlb / avg);
    gloss *= 1.0 - gm;
  #endif
  if (dot(bump, bump) > 0.0) { mat3 M = tbn(N, vL, vUv); N = normalize(M * vec3(bump, 1.0)); }
  vec3 L = lightmap(vUv2);
  float wtop; float uw = underwater(vL, wtop);
  if (uCaus > 0.5) {
    if (uw > 0.0) {
      float c = causticsAt(vL.xz + N.xz * 0.3, uTime);
      float k = smoothstep(0.0, 0.25, uw) * (0.35 + 0.65 * max(N.y, 0.25));
      L *= mix(vec3(1.0), vec3(0.72, 0.9, 0.98) + c * vec3(0.55, 0.75, 0.8), k);
    } else {
      float r = poolReflect(vL, N);
      if (r > 0.001) { float c = causticsAt(vL.xz * 0.6 + vL.y * 0.35, uTime * 0.8); L += lightmap(vUv2) * vec3(0.55, 0.85, 0.9) * c * r * 0.22 + vec3(0.02, 0.07, 0.08) * r * (1.0 - uDay); }
    }
  }
  float ndv = clamp(dot(-V, N), 0.0, 1.0);
  vec3 F0 = mix(vec3(uF0), A, metal);
  vec3 F = F0 + (1.0 - F0) * pow(1.0 - ndv, 5.0);
  vec3 col = A * L * (1.0 - metal) * (1.0 - F * gloss);
  if (gloss > 0.0 && uProbeOn > 0.5) {
    vec3 R = reflect(V, N);
    vec3 rc = probe(vL, R, rough);
    col += rc * F * gloss * ao;
  } else if (metal > 0.5) col += A * L * 0.6;
  float d = length(vL - vCam);
  col = mix(col, uFogCol, 1.0 - exp(-d * uFogD));
  gl_FragColor = vec4(safeCol(col), 1.0);
}`;

const EMIT_FS = `
uniform vec3 uEmit; uniform float uOn; uniform vec3 uFogCol; uniform float uFogD;
varying vec3 vL; varying vec3 vN; varying vec2 vUv; varying vec2 vUv2; varying vec3 vCam;
void main(){
  float d = length(vL - vCam);
  vec3 col = uEmit * uOn;
  col = mix(col, uFogCol, 1.0 - exp(-d * uFogD));
  gl_FragColor = vec4(col, 1.0);
}`;

/* A painted sky for the rooms that pretend to be outside: gradient, slow clouds, and stars after lights-out */
const SKY_FS = `
uniform vec3 uEmit; uniform float uOn; uniform vec3 uFogCol; uniform float uFogD; uniform float uTime; uniform float uDay;
varying vec3 vL; varying vec3 vN; varying vec2 vUv; varying vec2 vUv2; varying vec3 vCam;
float h2(vec2 p){ vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float n2(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(h2(i), h2(i + vec2(1, 0)), f.x), mix(h2(i + vec2(0, 1)), h2(i + vec2(1, 1)), f.x), f.y); }
float fbm(vec2 p){ float a = 0.5, s = 0.0; for (int i = 0; i < 5; i++) { s += a * n2(p); p = p * 2.03 + 11.7; a *= 0.5; } return s; }
void main(){
  vec3 d = normalize(vL - vCam);
  float e = clamp(d.y, 0.0, 1.0);
  float k = max(dot(uEmit, vec3(0.333)), 0.001);
  vec3 zen = vec3(0.28, 0.45, 0.78), hor = vec3(0.95, 0.82, 0.66);
  vec3 sky = mix(hor, zen, pow(e, 0.55));
  vec2 cp = d.xz / (d.y + 0.25) * 1.6 + vec2(uTime * 0.004, uTime * 0.002);
  float c = smoothstep(0.48, 0.82, fbm(cp));
  sky = mix(sky, vec3(1.0, 0.96, 0.9) * (0.85 + 0.2 * fbm(cp * 2.0)), c * 0.8 * smoothstep(0.0, 0.25, e));
  vec3 night = mix(vec3(0.02, 0.025, 0.05), vec3(0.05, 0.06, 0.1), 1.0 - e);
  night += vec3(step(0.9985, h2(floor(d.xz / (d.y + 0.3) * 400.0)))) * 0.8 * smoothstep(0.05, 0.3, e);
  vec3 col = mix(night, sky * min(k, 1.2), uDay);
  gl_FragColor = vec4(col, 1.0);
}`;

/* Water: reflections are traced through the depth buffer (falling back to the room's probe);
   what's under the surface is the opaque frame, bent and tinted by how deep it is. */
const WATER_VS = `
varying vec3 vL; varying vec3 vCam; varying vec3 vV; varying vec3 vNX; varying vec3 vNY; varying vec3 vNZ;
void main(){
  vL = position; vCam = (inverse(modelMatrix) * vec4(cameraPosition, 1.0)).xyz;
  vec4 mv = modelViewMatrix * vec4(position, 1.0); vV = mv.xyz;
  vNX = normalMatrix * vec3(1.0, 0.0, 0.0); vNY = normalMatrix * vec3(0.0, 1.0, 0.0); vNZ = normalMatrix * vec3(0.0, 0.0, 1.0);
  gl_Position = projectionMatrix * mv;
}`;
const WATER_FS = `
uniform sampler2D tScene; uniform sampler2D tDepth; uniform vec2 uRes; uniform mat4 uProj; uniform mat4 uProjInv;
uniform vec3 uDeep; uniform float uGlow; uniform float uSSR;
varying vec3 vL; varying vec3 vCam; varying vec3 vV; varying vec3 vNX; varying vec3 vNY; varying vec3 vNZ;
${ROOM_COMMON}
vec3 vpos(vec2 uv){ float d = texture2D(tDepth, uv).x; vec4 p = uProjInv * vec4(uv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0); return p.xyz / p.w; }
float wh(vec2 p, float t){
  return vnoise(p * 1.3 + vec2(t * 0.31, t * 0.17)) * 0.5 + vnoise(p * 2.9 - vec2(t * 0.23, -t * 0.29)) * 0.3 + vnoise(p * 7.0 + vec2(-t * 0.5, t * 0.4)) * 0.12;
}
void main(){
  vec2 suv = gl_FragCoord.xy / uRes;
  vec2 p = vL.xz; float e = 0.04, t = uTime;
  float h0 = wh(p, t);
  vec3 n = normalize(vec3(-(wh(p + vec2(e, 0.0), t) - h0) / e * 0.09, 1.0, -(wh(p + vec2(0.0, e), t) - h0) / e * 0.09));
  bool below = vCam.y < vL.y;
  if (below) n = -n;
  vec3 V = normalize(vL - vCam);
  vec3 nv = normalize(vNX * n.x + vNY * n.y + vNZ * n.z);
  float ndv = clamp(dot(-V, n), 0.0, 1.0);
  float F = below ? 0.0 : 0.02 + 0.98 * pow(1.0 - ndv, 5.0);
  if (below && ndv < 0.66) F = 1.0;   // total internal reflection
  // what lies under (or above) the surface
  float wz = -vV.z;
  vec2 ruv = suv + nv.xy * 0.035 * clamp(4.0 / wz, 0.2, 1.0);
  vec3 bp = vpos(ruv);
  if (-bp.z < wz) { ruv = suv; bp = vpos(suv); }
  float thick = max(-bp.z - wz, 0.0) * (below ? 0.0 : 1.0);
  vec3 refr = texture2D(tScene, ruv).rgb;
  vec3 absorb = exp(-thick * vec3(0.95, 0.24, 0.17));
  refr = refr * absorb + uDeep * (1.0 - absorb) * (0.5 + 0.5 * uDay) + uDeep * uGlow * (1.0 - absorb);
  // reflection
  vec3 refl = probe(vL, reflect(V, n), 0.03);
  if (uSSR > 0.5 && F > 0.01) {
    vec3 P = vV; vec3 R = normalize(reflect(normalize(P), nv));
    float s = 0.1, sp = 0.0; vec2 huv = vec2(-1.0);
    for (int i = 0; i < 28; i++) {
      vec3 X = P + R * s; vec4 c = uProj * vec4(X, 1.0); vec2 u = c.xy / c.w * 0.5 + 0.5;
      if (u.x < 0.0 || u.x > 1.0 || u.y < 0.0 || u.y > 1.0 || X.z > -0.05) break;
      float dz = vpos(u).z - X.z;
      if (dz > 0.0 && dz < 0.35 + s * 0.1) {
        float a = sp, b = s;
        for (int j = 0; j < 5; j++) { float m = 0.5 * (a + b); vec3 M = P + R * m; vec4 cm = uProj * vec4(M, 1.0); vec2 mu = cm.xy / cm.w * 0.5 + 0.5; if (vpos(mu).z - M.z > 0.0) b = m; else a = m; }
        vec4 ch = uProj * vec4(P + R * b, 1.0); huv = ch.xy / ch.w * 0.5 + 0.5; break;
      }
      sp = s; s = s * 1.25 + 0.05;
    }
    if (huv.x >= 0.0) {
      vec2 ed = smoothstep(0.0, 0.12, huv) * smoothstep(1.0, 0.88, huv);
      refl = mix(refl, texture2D(tScene, huv).rgb, ed.x * ed.y);
    }
  }
  vec3 col = mix(refr, refl, F);
  float d = length(vL - vCam);
  col = mix(col, uFogCol, 1.0 - exp(-d * uFogD));
  gl_FragColor = vec4(safeCol(col), 1.0);
}`;

/* Light shafts under the skylights: a box of hazy air, marched per pixel and clipped by the depth buffer */
const SHAFT_VS = `
varying vec3 vL; varying vec3 vCam;
void main(){ vL = position; vCam = (inverse(modelMatrix) * vec4(cameraPosition, 1.0)).xyz; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const SHAFT_FS = `
uniform sampler2D tDepth; uniform vec2 uRes; uniform mat4 uProjInv; uniform vec3 uBmin; uniform vec3 uBmax; uniform float uStr; uniform float uDay; uniform float uTime;
varying vec3 vL; varying vec3 vCam;
float h21(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h21(i), h21(i + vec2(1.0, 0.0)), f.x), mix(h21(i + vec2(0.0, 1.0)), h21(i + vec2(1.0, 1.0)), f.x), f.y); }
void main(){
  if (uDay < 0.01) discard;
  vec3 ro = vCam, rd = normalize(vL - vCam);
  vec3 t0 = (uBmin - ro) / rd, t1 = (uBmax - ro) / rd, tn = min(t0, t1);
  float tin = max(max(tn.x, tn.y), max(tn.z, 0.0));
  float tout = length(vL - vCam);
  vec2 suv = gl_FragCoord.xy / uRes;
  float d = texture2D(tDepth, suv).x; vec4 pp = uProjInv * vec4(suv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0);
  tout = min(tout, length(pp.xyz / pp.w));
  if (tout <= tin) discard;
  float acc = 0.0, dt = (tout - tin) / 10.0, j = h21(gl_FragCoord.xy);
  for (int i = 0; i < 10; i++) {
    vec3 q = ro + rd * (tin + (float(i) + j) * dt);
    vec3 b = (q - uBmin) / (uBmax - uBmin);
    vec2 e = min(b.xz, 1.0 - b.xz);
    float dens = smoothstep(0.0, 0.3, min(e.x, e.y)) * pow(clamp(b.y, 0.0, 1.0), 1.4);
    dens *= 0.75 + 0.5 * vn(q.xz * 0.9 + vec2(q.y * 0.3, uTime * 0.03));
    acc += dens;
  }
  gl_FragColor = vec4(vec3(0.86, 0.93, 1.0) * acc * dt * uStr * uDay, 1.0);
}`;
/* skylight emitters, clustered into boxes */
function shaftBoxes(meshes) {
  const out = [];
  for (const m of meshes) {
    if (m.name !== 'e_sky') continue;
    const pos = m.geo.attributes.position.array, idx = m.geo.index.array, n = idx.length / 3, boxes = [];
    for (let t = 0; t < n; t++) {
      let b = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9];
      for (let k = 0; k < 3; k++) { const v = idx[t * 3 + k] * 3; for (let a = 0; a < 3; a++) { b[a] = Math.min(b[a], pos[v + a]); b[a + 3] = Math.max(b[a + 3], pos[v + a]); } }
      boxes.push(b);
    }
    const parent = boxes.map((_, i) => i), find = i => parent[i] === i ? i : (parent[i] = find(parent[i]));
    for (let i = 0; i < n; i++) for (let k = i + 1; k < n; k++) {
      const a = boxes[i], b = boxes[k];
      if (a[0] <= b[3] + 0.05 && b[0] <= a[3] + 0.05 && a[1] <= b[4] + 0.05 && b[1] <= a[4] + 0.05 && a[2] <= b[5] + 0.05 && b[2] <= a[5] + 0.05) parent[find(i)] = find(k);
    }
    const groups = new Map();
    boxes.forEach((b, i) => { const r = find(i); const g = groups.get(r); if (!g) groups.set(r, b.slice()); else for (let a = 0; a < 3; a++) { g[a] = Math.min(g[a], b[a]); g[a + 3] = Math.max(g[a + 3], b[a + 3]); } });
    for (const g of groups.values()) if (g[3] - g[0] > 0.2 && g[5] - g[2] > 0.2) out.push([g[0] + 0.05, 0.0, g[2] + 0.05, g[3] - 0.05, g[1], g[5] - 0.05]);
  }
  return out;
}

/* Books on shelves: one instance per book, lit from the lightmap texel behind its spine */
const BOOK_VS = `
attribute float aFace; attribute vec3 aStyle; attribute vec4 aLM;
varying vec3 vL; varying vec3 vN; varying vec2 vUv; varying vec2 vLM; varying vec3 vCol; varying vec3 vStyle; varying float vFace; varying vec3 vCam;
void main(){
  vec4 p = instanceMatrix * vec4(position, 1.0);
  vL = p.xyz; vN = normalize(mat3(instanceMatrix) * normal); vUv = uv; vFace = aFace; vStyle = aStyle; vCol = instanceColor;
  vLM = mix(aLM.xy, aLM.zw, position.y + 0.5);
  vCam = (inverse(modelMatrix) * vec4(cameraPosition, 1.0)).xyz;
  gl_Position = projectionMatrix * viewMatrix * modelMatrix * p;
}`;
const BOOK_FS = `
varying vec3 vL; varying vec3 vN; varying vec2 vUv; varying vec2 vLM; varying vec3 vCol; varying vec3 vStyle; varying float vFace; varying vec3 vCam;
${ROOM_COMMON}
void main(){
  vec3 base = vCol, N = normalize(vN); float ao = 1.0, gl = 0.0;
  if (vFace < 0.5) {
    float bv = vUv.y, bu = vUv.x;
    float grain = hash21(floor(vUv * vec2(5.0, 70.0)) + vStyle.z * 91.0);
    base *= (0.86 + 0.14 * grain) * (0.8 + 0.2 * sin(bu * 3.14159));
    float b1 = smoothstep(0.085, 0.095, bv) - smoothstep(0.115, 0.125, bv) + smoothstep(0.875, 0.885, bv) - smoothstep(0.905, 0.915, bv);
    float b2 = smoothstep(0.2, 0.21, bv) - smoothstep(0.225, 0.235, bv) + smoothstep(0.765, 0.775, bv) - smoothstep(0.79, 0.8, bv);
    float band = vStyle.x < 0.5 ? b1 : (vStyle.x < 1.5 ? b1 + b2 : 0.0);
    if (vStyle.x > 1.5) base *= 0.88 + 0.12 * step(0.5, fract(bv * 6.0 + 0.25));
    band = clamp(band, 0.0, 1.0);
    base = mix(base, vec3(0.5, 0.32, 0.08), band * 0.9); gl = band;
    if (vStyle.y > 0.5) { float lab = step(0.56, bv) * step(bv, 0.7) * step(0.2, bu) * step(bu, 0.8); base = mix(base, vec3(0.5, 0.45, 0.34), lab * 0.9); }
    base *= 1.0 - 0.3 * vStyle.z * (smoothstep(0.36, 0.5, abs(bu - 0.5)) + smoothstep(0.43, 0.5, abs(bv - 0.5)));
    ao *= mix(0.6, 1.0, smoothstep(0.0, 0.1, bv));
  } else if (vFace < 1.5) {
    vec3 pg = vec3(0.56, 0.5, 0.38) * (0.88 + 0.12 * sin(vUv.x * 420.0));
    base = mix(base * 0.8, pg, step(0.09, vUv.x) * step(vUv.x, 0.91));
    ao *= mix(0.3, 0.9, vUv.y);
  } else { base *= 0.75; ao *= 0.55; }
  vec3 L = lightmap(vLM);
  vec3 V = normalize(vL - vCam);
  vec3 col = base * L * ao;
  if (gl > 0.01 && uProbeOn > 0.5) col += probe(vL, reflect(V, N), 0.2) * base * gl * 1.4;
  float d = length(vL - vCam);
  col = mix(col, uFogCol, 1.0 - exp(-d * uFogD));
  gl_FragColor = vec4(safeCol(col), 1.0);
}`;

function bookGeometry(perVertexStyle) {
  const pos = [], nor = [], uv = [], face = [];
  const quad = (a, b, c, d, n, f, uvs) => { for (const i of [0, 1, 2, 0, 2, 3]) { pos.push(...[a, b, c, d][i]); nor.push(...n); uv.push(...uvs[i]); face.push(f); } };
  const q = [[0, 0], [1, 0], [1, 1], [0, 1]];
  quad([-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5], [0, 0, 1], 0, q);             // spine
  quad([-0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5], [0, 1, 0], 1, [[0, 1], [1, 1], [1, 0], [0, 0]]); // page tops
  quad([-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, 0.5, -0.5], [-1, 0, 0], 2, q);        // left cover
  quad([0.5, -0.5, 0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5], [1, 0, 0], 2, q);             // right cover
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setAttribute('aFace', new THREE.Float32BufferAttribute(face, 1));
  if (perVertexStyle) g.setAttribute('aStyle', new THREE.Float32BufferAttribute(new Array(face.length * 3).fill(0), 3));
  return g;
}

/* ==========================================================================
   Room prefabs: loaded once, placed many times
   ========================================================================== */
const PREFABS = new Map();
const texLoader = new THREE.TextureLoader();
let WOOD_TEX = null;
function woodTex() {
  if (WOOD_TEX) return WOOD_TEX;
  WOOD_TEX = texLoader.load(ASSET_BASE + 'assets/wood.jpg'); WOOD_TEX.wrapS = WOOD_TEX.wrapT = THREE.RepeatWrapping; WOOD_TEX.anisotropy = Math.min(8, MAX_ANISO);
  return WOOD_TEX;
}
function loadLM(url) {
  return new Promise((res) => {
    texLoader.load(url, t => { t.minFilter = THREE.LinearFilter; t.magFilter = THREE.LinearFilter; t.generateMipmaps = false; res(t); },
      undefined, () => { const d = new THREE.DataTexture(new Uint8Array([150, 150, 150, 255]), 1, 1); d.needsUpdate = true; res(d); });
  });
}
function waterUniforms(meta) {
  const W = [], Hh = [];
  for (let i = 0; i < 4; i++) {
    const w = meta.water[i];
    if (!w) { W.push(new THREE.Vector4(0, 0, 0, 0)); Hh.push(new THREE.Vector2(-1, 0)); continue; }
    if (w.r !== undefined) W.push(new THREE.Vector4(w.cx, w.cz, 0, w.r));
    else W.push(new THREE.Vector4(w.x0, w.z0, w.z1, -w.x1));
    Hh.push(new THREE.Vector2(w.top, w.bot));
  }
  return { W, Hh };
}
async function inflateB64(b64) {
  const raw = atob(b64), u = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) u[i] = raw.charCodeAt(i);
  return new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('deflate'))).arrayBuffer();
}
/* drop a prefab nobody is standing near: its meshes, textures and probes */
function disposePrefab(name) {
  const pf = PREFABS.get(name); if (!pf || pf instanceof Promise) return;
  for (const m of pf.meshes) m.geo.dispose();
  for (const k in pf.mats) pf.mats[k].dispose();
  pf.lmd.dispose(); pf.lmn.dispose(); pf.cube.dispose(); pf.cubeN.dispose();
  if (pf.bookMat) pf.bookMat.dispose(); if (pf.waterMat) pf.waterMat.dispose();
  for (const w of pf.waters) w.dispose(); for (const sh of pf.shafts) { sh.g.dispose(); sh.m.dispose(); }
  PREFABS.delete(name);
}
async function loadPrefab(name) {
  if (PREFABS.has(name)) return PREFABS.get(name);
  const p = (async () => {
    const base = name.includes('/') ? name : 'rooms/' + name;
    const get = async u => { const r = await fetch(u); if (!r.ok) throw new Error(u + ': ' + r.status); return r; };
    const meta = await (await get(base + '.json')).json();
    // meshes travel quantized and deflated, as base64 inside the JSON; lightmaps as embedded WebP
    const bin = await inflateB64(meta.zbin); delete meta.zbin;
    if (meta.sl) {   // shelf rows travel as 18 floats each
      const F = new Float32Array(bin, meta.sl.off, meta.sl.n * 18); meta.slabs = [];
      for (let i = 0; i < meta.sl.n; i++) {
        const f = F.subarray(i * 18, i * 18 + 18);
        meta.slabs.push({ o: [f[0], f[1], f[2]], u: [f[3], f[4], f[5]], n: [f[6], 0, f[7]], len: Math.hypot(f[3], f[4], f[5]), h: f[8], depth: f[9],
          lm: [[f[10], f[11]], [f[12], f[13]], [f[14], f[15]], [f[16], f[17]]] });
      }
    }
    const lmUrl = k => 'data:image/webp;base64,' + meta.lm[k];
    const [lmd, lmn] = await Promise.all([loadLM(lmUrl('day')), loadLM(lmUrl(meta.lm.night ? 'night' : 'day'))]);
    delete meta.lm;
    const Q = meta.q, qlo = Q.lo, qst = Q.step;
    const deq = (off, n) => { const a = new Uint16Array(bin, off, n * 3), f = new Float32Array(n * 3); for (let i = 0; i < n; i++) for (let k = 0; k < 3; k++) f[i * 3 + k] = qlo[k] + a[i * 3 + k] * qst[k]; return f; };
    const probeP = (meta.spots.find(s => s.k === 'probe') || { p: [meta.w * RC / 2, 1.7, meta.d * RC / 2] }).p;
    const box = { min: new THREE.Vector3(0.3, -2, 0.3), max: new THREE.Vector3(meta.w * RC - 0.3, meta.levels * RLH - 0.4, meta.d * RC - 0.3) };
    if (meta.meta.box) { box.min.fromArray(meta.meta.box[0]); box.max.fromArray(meta.meta.box[1]); }
    const cubeOpts = { type: HALF ? THREE.HalfFloatType : THREE.UnsignedByteType, generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter };
    const cube = new THREE.WebGLCubeRenderTarget(128, cubeOpts), cubeN = new THREE.WebGLCubeRenderTarget(64, cubeOpts);
    const wat = waterUniforms(meta);
    const common = {
      tLMd: { value: lmd }, tLMn: { value: lmn }, tProbe: { value: cube.texture }, tProbeN: { value: cubeN.texture },
      uProbeP: { value: new THREE.Vector3().fromArray(probeP) }, uBoxMin: { value: box.min }, uBoxMax: { value: box.max },
      uWat: { value: wat.W }, uWatH: { value: wat.Hh },
      uDay: WU.uDay, uTime: WU.uTime, uFogCol: WU.uFogCol, uFogD: WU.uFogD, uProbeOn: WU.uProbeOn, uCaus: WU.uCaus
    };
    const mats = {}, meshes = [];
    for (const g of meta.groups) {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(deq(g.p, g.n), 3));
      geo.setAttribute('normal', new THREE.BufferAttribute(new Int8Array(bin, g.nr, g.n * 3), 3, true));
      { const a = new Int16Array(bin, g.u0, g.n * 2), f = new Float32Array(g.n * 2); for (let i = 0; i < f.length; i++) f[i] = a[i] * Q.uv; geo.setAttribute('uv', new THREE.BufferAttribute(f, 2)); }
      geo.setAttribute('uv2', new THREE.BufferAttribute(new Uint16Array(bin, g.u1, g.n * 2), 2, true));
      geo.setIndex(new THREE.BufferAttribute(g.i32 ? new Uint32Array(bin, g.ix, g.i) : new Uint16Array(bin, g.ix, g.i), 1));
      geo.computeBoundingSphere();
      let mat = mats[g.mat];
      if (!mat) {
        if (g.emit) {
          const e = meta.emit[g.mat];
          mat = new THREE.ShaderMaterial({ uniforms: { uEmit: { value: new THREE.Vector3(e[0][0] * e[1], e[0][1] * e[1], e[0][2] * e[1]) }, uOn: { value: 1 }, uFogCol: WU.uFogCol, uFogD: WU.uFogD },
            vertexShader: ROOM_VS, fragmentShader: EMIT_FS });
          mat.userData.night = (meta.night_on || ['e_pool', 'e_amber', 'e_kiosk', 'e_portal']).includes(g.mat);
          if (g.mat === 'e_skydome') { mat.fragmentShader = SKY_FS; mat.uniforms.uTime = WU.uTime; mat.uniforms.uDay = WU.uDay; }
        } else {
          const K = KINDS[g.mat] || KINDS.paint, alb = meta.albedo[g.mat] || [0.6, 0.6, 0.6];
          const pal = K.pal || [[0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, 0.5, 0.5]];
          mat = new THREE.ShaderMaterial({
            defines: { KIND: K.k }, extensions: { derivatives: true }, side: K.k === 10 ? THREE.DoubleSide : THREE.FrontSide,
            uniforms: Object.assign({}, common, {
              uAlb: { value: new THREE.Vector3().fromArray(alb) }, uSize: { value: K.size || 0.15 }, uGrout: { value: K.grout || 0.005 }, uJit: { value: K.jit || 0.05 },
              uGloss: { value: K.gloss }, uF0: { value: K.f0 }, uRough: { value: K.rough },
              uP0: { value: new THREE.Vector3().fromArray(pal[0]) }, uP1: { value: new THREE.Vector3().fromArray(pal[1]) }, uP2: { value: new THREE.Vector3().fromArray(pal[2]) }, uP3: { value: new THREE.Vector3().fromArray(pal[3]) },
              tTex: { value: K.k === 7 || K.k === 12 ? woodTex() : null }
            }),
            vertexShader: ROOM_VS, fragmentShader: ROOM_FS
          });
        }
        mats[g.mat] = mat;
      }
      meshes.push({ geo, mat, name: g.mat, emit: !!g.emit });
    }
    // collision triangles, in room space
    const C_ = meta.col, cv = deq(C_.v, C_.nv), ci = C_.i32 ? new Uint32Array(bin, C_.ix, C_.nt * 3) : new Uint16Array(bin, C_.ix, C_.nt * 3);
    const col = new Float32Array(C_.nt * 9);
    for (let i = 0; i < ci.length; i++) { const v = ci[i] * 3; col[i * 3] = cv[v]; col[i * 3 + 1] = cv[v + 1]; col[i * 3 + 2] = cv[v + 2]; }
    meta.col = { n: C_.nt };
    // water surfaces
    const waterMat = new THREE.ShaderMaterial({
      uniforms: Object.assign({}, common, { tScene: { value: null }, tDepth: { value: null }, uRes: { value: new THREE.Vector2() }, uProj: { value: new THREE.Matrix4() }, uProjInv: { value: new THREE.Matrix4() },
        uDeep: { value: new THREE.Vector3(0.05, 0.3, 0.36) }, uGlow: { value: 0 }, uSSR: { value: 1 } }),
      vertexShader: WATER_VS, fragmentShader: WATER_FS, extensions: { derivatives: true }, side: THREE.DoubleSide, depthWrite: false
    });
    const waters = meta.water.map(w => {
      let g;
      if (w.r !== undefined) { g = new THREE.CircleGeometry(w.r, 64); g.rotateX(-Math.PI / 2); g.translate(w.cx, w.top, w.cz); }
      else { g = new THREE.PlaneGeometry(w.x1 - w.x0, w.z1 - w.z0, 1, 1); g.rotateX(-Math.PI / 2); g.translate((w.x0 + w.x1) / 2, w.top, (w.z0 + w.z1) / 2); }
      return g;
    });
    const shafts = shaftBoxes(meshes).map(b => {
      const g = new THREE.BoxGeometry(b[3] - b[0], b[4] - b[1], b[5] - b[2]); g.translate((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2);
      const m = new THREE.ShaderMaterial({ uniforms: { tDepth: SHAFT_U.tDepth, uRes: SHAFT_U.uRes, uProjInv: SHAFT_U.uProjInv, uBmin: { value: new THREE.Vector3(b[0], b[1], b[2]) }, uBmax: { value: new THREE.Vector3(b[3], b[4], b[5]) }, uStr: SHAFT_U.uStr, uDay: WU.uDay, uTime: WU.uTime },
        vertexShader: SHAFT_VS, fragmentShader: SHAFT_FS, side: THREE.BackSide, transparent: true, depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending });
      return { g, m };
    });
    const pf = { name, meta, meshes, mats, col, waters, waterMat, shafts, cube, cubeN, lmd, lmn, common, grid: buildColGrid(col), bookMat: null, probeDone: false };
    pf.bookMat = new THREE.ShaderMaterial({ uniforms: Object.assign({}, common), vertexShader: BOOK_VS, fragmentShader: BOOK_FS, extensions: { derivatives: true } });
    PREFABS.set(name, pf);
    return pf;
  })();
  PREFABS.set(name, p);
  return p;
}

/* A room's reflection probes: the room alone, seen from its probe point, by day and by night, captured once */
function captureProbe(pf) {
  if (pf.probeDone) return;
  const sc = new THREE.Scene();
  for (const m of pf.meshes) if (m.name !== 'books') sc.add(new THREE.Mesh(m.geo, m.mat));
  const at = (pf.meta.spots.find(s => s.k === 'probe') || { p: [8, 1.7, 8] }).p;
  const fog = WU.uFogD.value, on = WU.uProbeOn.value, caus = WU.uCaus.value, day = WU.uDay.value;
  WU.uFogD.value = 0; WU.uProbeOn.value = 0; WU.uCaus.value = 0;
  const prev = renderer.getRenderTarget(), ons = [];
  for (const k in pf.mats) { const m = pf.mats[k]; if (m.uniforms.uOn) ons.push([m, m.uniforms.uOn.value]); }
  for (const [rt, d] of [[pf.cube, 1], [pf.cubeN, 0]]) {
    WU.uDay.value = d;
    for (const [m] of ons) m.uniforms.uOn.value = m.userData.night ? 1 : d;
    const cam = new THREE.CubeCamera(0.05, 200, rt); cam.position.fromArray(at); sc.add(cam);
    cam.update(renderer, sc); sc.remove(cam);
  }
  for (const [m, v] of ons) m.uniforms.uOn.value = v;
  renderer.setRenderTarget(prev);
  WU.uFogD.value = fog; WU.uProbeOn.value = on; WU.uCaus.value = caus; WU.uDay.value = day;
  pf.probeDone = true;
}

/* Collision: a uniform grid of triangles per prefab (2 m cells), queried in room space */
function buildColGrid(col) {
  const n = col.length / 9, cs = 2, grid = new Map();
  for (let t = 0; t < n; t++) {
    const o = t * 9;
    const x0 = Math.min(col[o], col[o + 3], col[o + 6]), x1 = Math.max(col[o], col[o + 3], col[o + 6]);
    const y0 = Math.min(col[o + 1], col[o + 4], col[o + 7]), y1 = Math.max(col[o + 1], col[o + 4], col[o + 7]);
    const z0 = Math.min(col[o + 2], col[o + 5], col[o + 8]), z1 = Math.max(col[o + 2], col[o + 5], col[o + 8]);
    for (let i = Math.floor(x0 / cs); i <= Math.floor(x1 / cs); i++) for (let j = Math.floor(y0 / cs); j <= Math.floor(y1 / cs); j++) for (let k = Math.floor(z0 / cs); k <= Math.floor(z1 / cs); k++) {
      const key = i + ',' + j + ',' + k; let a = grid.get(key); if (!a) grid.set(key, a = []); a.push(t);
    }
  }
  return { cs, grid };
}

/* ==========================================================================
   Placing rooms and filling their shelves
   ========================================================================== */
const BOOK_GEO = bookGeometry(false);
function roomInstance(pf) {
  const grp = new THREE.Group(), water = new THREE.Group();
  for (const m of pf.meshes) {
    const mesh = new THREE.Mesh(m.geo, m.mat); grp.add(mesh);
    if (m.name === 'books') grp.userData.slabs = mesh;
  }
  for (const g of pf.waters) water.add(new THREE.Mesh(g, pf.waterMat));
  if (pf.shafts) for (const sh of pf.shafts) { const m = new THREE.Mesh(sh.g, sh.m); m.renderOrder = 5; m.frustumCulled = true; water.add(m); }
  return { pf, grp, water, books: null };
}
/* slotFn(slab, p) -> { w, L } for the p-th slot on a slab: w is the slot's width, L the look of the
   book standing in it (null when the slot is empty). Slots run until the slab is full. */
function writeBook(inst, i, L) {
  const mesh = inst.books, M = mesh.instanceMatrix.array, Cc = mesh.instanceColor.array, st = mesh.geometry.attributes.aStyle.array;
  const [si, p, x, w] = mesh.userData.list[i], s = inst.pf.meta.slabs[si], o = i * 16;
  if (!L) { for (let j = 0; j < 16; j++) M[o + j] = 0; return; }
  const ul = s.len, ux = s.u[0] / ul, uz = s.u[2] / ul, nx = s.n[0], nz = s.n[2];
  const h = Math.min(L.h, s.h - 0.01), d = Math.min(L.d, s.depth), ww = w * 0.97;
  const cx = s.o[0] + ux * (x + w / 2) - nx * (d / 2 - L.out), cy = s.o[1] + h / 2, cz = s.o[2] + uz * (x + w / 2) - nz * (d / 2 - L.out);
  M[o] = ux * ww; M[o + 1] = 0; M[o + 2] = uz * ww; M[o + 3] = 0;
  M[o + 4] = 0; M[o + 5] = h; M[o + 6] = 0; M[o + 7] = 0;
  M[o + 8] = nx * d; M[o + 9] = 0; M[o + 10] = nz * d; M[o + 11] = 0;
  M[o + 12] = cx; M[o + 13] = cy; M[o + 14] = cz; M[o + 15] = 1;
  Cc[i * 3] = L.col[0]; Cc[i * 3 + 1] = L.col[1]; Cc[i * 3 + 2] = L.col[2];
  st[i * 3] = L.band; st[i * 3 + 1] = L.label; st[i * 3 + 2] = L.wear;
  const q = (x + w / 2) / ul, c = s.lm, lm = mesh.geometry.attributes.aLM.array;
  const at = t => [c[0][0] + (c[1][0] - c[0][0]) * q + ((c[3][0] + (c[2][0] - c[3][0]) * q) - (c[0][0] + (c[1][0] - c[0][0]) * q)) * t,
                   c[0][1] + (c[1][1] - c[0][1]) * q + ((c[3][1] + (c[2][1] - c[3][1]) * q) - (c[0][1] + (c[1][1] - c[0][1]) * q)) * t];
  const a = at(0.06), b = at(Math.min(0.97, h / s.h));
  lm[i * 4] = a[0]; lm[i * 4 + 1] = a[1]; lm[i * 4 + 2] = b[0]; lm[i * 4 + 3] = b[1];
}
function fillShelves(inst, slotFn, near) {
  const pf = inst.pf, SL = pf.meta.slabs, list = [], slabX = [];
  for (let si = 0; si < SL.length; si++) {
    const s = SL[si], xs = []; let x = 0.012, p = 0;
    if (near) { const cx = s.o[0] + s.u[0] / 2 - near.x, cz = s.o[2] + s.u[2] / 2 - near.z, cy = s.o[1] - near.y; if (Math.hypot(cx, cz) > near.r + s.len / 2 || cy < -4 || cy > 6) { slabX.push(xs); continue; } }
    for (;;) { const r = slotFn(si, p); if (x + r.w > s.len - 0.012) break; list.push([si, p, x, r.w, r.L]); xs.push([x, r.w]); x += r.w + 0.0012; p++; }
    slabX.push(xs);
  }
  const n = list.length, geo = BOOK_GEO.clone();
  geo.setAttribute('aStyle', new THREE.InstancedBufferAttribute(new Float32Array(n * 3), 3));
  geo.setAttribute('aLM', new THREE.InstancedBufferAttribute(new Float32Array(n * 4), 4));
  const mesh = new THREE.InstancedMesh(geo, pf.bookMat, n);
  mesh.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(n * 3), 3);
  mesh.userData.list = list;
  inst.books = mesh; inst.slabX = slabX; inst.bookStart = [];
  let k = 0; for (let si = 0; si < SL.length; si++) { inst.bookStart.push(k); k += slabX[si].length; }
  inst.bookSlots = slabX.map(x => x.length);
  for (let i = 0; i < n; i++) writeBook(inst, i, list[i][4]);
  const mw = pf.meta.w * RC, md = pf.meta.d * RC, mh = pf.meta.levels * RLH;
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(mw / 2, mh / 2, md / 2), Math.hypot(mw, md, mh) / 2 + 1);
  mesh.frustumCulled = true;
  inst.grp.add(mesh);
  return mesh;
}
function setBook(inst, si, p, L) {
  if (!inst.books || !inst.bookStart) return;
  if (p >= inst.bookSlots[si]) return;
  const i = inst.bookStart[si] + p; if (i >= inst.books.count) return;
  writeBook(inst, i, L);
  inst.books.instanceMatrix.needsUpdate = true; inst.books.instanceColor.needsUpdate = true;
  inst.books.geometry.attributes.aStyle.needsUpdate = true; inst.books.geometry.attributes.aLM.needsUpdate = true;
}
function clearShelves(inst) {
  if (!inst.books) return;
  inst.grp.remove(inst.books); inst.books.geometry.dispose(); inst.books = null; inst.slabX = null;
}

/* ==========================================================================
   The layout: an endless grid of 16 m cells, 8 m levels. Space is cut into
   2 x 2 cell x 2 level superblocks; each one's rooms are a pure function of
   its address. Some superblock columns hold a well or a spiral tower that
   runs through every level.
   ========================================================================== */
const ROOM_SIZE = { crossing: [1, 1, 1], rest: [1, 1, 1], bath: [1, 1, 1], reading: [1, 1, 1], well: [1, 1, 1], tower: [1, 1, 1], poolhall: [2, 1, 1], stacks: [2, 1, 1], backrooms: [2, 2, 1], pillars: [2, 2, 1], grand: [2, 2, 2] };
const COLUMN_ROOMS = { well: 1, tower: 1 };
/* the catalogue (rooms/index.json): every room's size, kind (single, long, quad, tall, column, giant),
   weight, label and blurb. The layout draws from it; rooms load only when you come near them. */
const CATALOG = {}, KIND_LIST = {};
async function loadCatalog() {
  const r = await fetch(ASSET_BASE + 'rooms/index.json'); if (!r.ok) throw new Error('rooms/index.json: ' + r.status);
  const idx = await r.json();
  for (const k in KIND_LIST) delete KIND_LIST[k];
  for (const [n, e] of Object.entries(idx)) {
    CATALOG[n] = e; ROOM_SIZE[n] = e.size;
    if (e.kind === 'column') COLUMN_ROOMS[n] = 1;
    (KIND_LIST[e.kind] = KIND_LIST[e.kind] || []).push([n, e.weight]);
  }
  PLAN_CACHE.clear(); GIANT_CACHE.clear();
}
function pickKind(kind, r, fallback) {
  const L = KIND_LIST[kind]; if (!L || !L.length) return fallback;
  let t = 0; for (const e of L) t += e[1];
  let x = r * t; for (const e of L) { if ((x -= e[1]) < 0) return e[0]; }
  return L[L.length - 1][0];
}
/* Giants: a few 8 x 8 cell x 4 level megablocks hold one enormous room, laid over whole superblocks.
   Megablock columns that may hold giants have no wells or towers anywhere in them. */
const GIANT_CACHE = new Map();
const giantColumn = (mx, mz) => !!(KIND_LIST.giant && KIND_LIST.giant.length) && (hashN(0x61a7, mx, mz) % 1000) / 1000 < 0.3;
function giantIn(mx, mz, ml) {
  const key = mx + ':' + mz + ':' + ml;
  if (GIANT_CACHE.has(key)) return GIANT_CACHE.get(key);
  let res = null;
  if (giantColumn(mx, mz)) {
    const h = hashN(0x7c3d, mx, mz, ml), R = sfc32(h, h ^ 0x9e3779b9, mix(h ^ 0x4321), mix((h + 17) >>> 0));
    for (let i = 0; i < 10; i++) R();
    if (R() < 0.3) {
      const name = pickKind('giant', R()), s = ROOM_SIZE[name];
      const rot = s[0] === s[1] ? Math.floor(R() * 4) : (R() < 0.5 ? 0 : 2), mir = R() < 0.5 ? 1 : 0;
      const fw = s[0] / 2, fd = s[1] / 2, fl = s[2] / 2;
      if (fw <= 4 && fd <= 4 && fl <= 2) {
        const bx0 = mx * 4 + Math.floor(R() * (5 - fw)), bz0 = mz * 4 + Math.floor(R() * (5 - fd)), bl0 = ml * 2 + Math.floor(R() * (3 - fl));
        let clash = false;
        for (let bx = bx0 - 1; bx <= bx0 + fw && !clash; bx++) for (let bz = bz0 - 1; bz <= bz0 + fd && !clash; bz++) {
          if (COLUMN_OVERRIDE.has(bx + ':' + bz)) clash = true;
          for (let bl = bl0 - 1; bl <= bl0 + fl; bl++) if (PLAN_OVERRIDE.has(bx + ':' + bz + ':' + bl)) clash = true;
        }
        if (!clash) res = { pl: { pf: name, cx: bx0 * 2, cz: bz0 * 2, lv: bl0 * 2, rot, mir }, b: [bx0, bz0, bl0, bx0 + fw, bz0 + fd, bl0 + fl] };
      }
    }
  }
  if (GIANT_CACHE.size > 400) GIANT_CACHE.delete(GIANT_CACHE.keys().next().value);
  GIANT_CACHE.set(key, res);
  return res;
}
function giantAt(bx, bz, bl) {
  const g = giantIn(fdiv(bx, 4), fdiv(bz, 4), fdiv(bl, 2));
  return g && bx >= g.b[0] && bx < g.b[3] && bz >= g.b[1] && bz < g.b[4] && bl >= g.b[2] && bl < g.b[5] ? g.pl : null;
}
function hashN(salt, ...vals) {
  let h = mix((salt ^ 0x9e3779b9) >>> 0);
  for (const v of vals) { h = mix((h ^ lo32(v)) >>> 0); h = mix((h ^ hi32(v) ^ 0x85ebca6b) >>> 0); }
  return h;
}
const fdiv = (a, b) => Math.floor(a / b);
/* superblock column: a well or tower through every level, or nothing */
function columnAt(bx, bz) {
  const o = COLUMN_OVERRIDE.get(bx + ':' + bz); if (o !== undefined) return o;
  if (giantColumn(fdiv(bx, 4), fdiv(bz, 4))) return null;
  const h = hashN(0x51a7, bx, bz), r = (h % 1000) / 1000;
  const cell = [(h >>> 10) & 1, (h >>> 11) & 1], rot = (h >>> 12) & 3;
  if (r < 0.36) return { type: pickKind('column', (hashN(0x3c1d, bx, bz) % 100000) / 100000, 'well'), cell, rot };
  return null;
}
const COLUMN_OVERRIDE = new Map(), PLAN_OVERRIDE = new Map();
const PLAN_CACHE = new Map();
/* place(pf, ci, cj, level, rot, mirror) with ci/cj relative to the superblock */
function planAt(bx, bz, bl) {
  const key = bx + ':' + bz + ':' + bl;
  let p = PLAN_CACHE.get(key); if (p) return p;
  const gp = giantAt(bx, bz, bl);
  if (gp) { p = [gp]; PLAN_CACHE.set(key, p); return p; }
  p = [];
  const put = (pf, ci, cj, lv, rot, mir) => { p.push({ pf, cx: bx * 2 + ci, cz: bz * 2 + cj, lv: bl * 2 + lv, rot: rot & 3, mir: mir ? 1 : 0 }); };
  const col = columnAt(bx, bz);
  const ov = PLAN_OVERRIDE.get(key);
  const h = hashN(0x2f1b, bx, bz, bl);
  const R = sfc32(h, h ^ 0x51ed270b, mix(h ^ 0x1234), mix((bl & 0xffff) ^ h));
  for (let i = 0; i < 10; i++) R();
  const one = () => pickKind('single', R(), 'rest');
  const long = () => pickKind('long', R(), 'poolhall');
  if (ov && ov.full) ov.full(put, col, R);
  else if (!ov && !col && R() < 0.13) put(pickKind('tall', R(), 'grand'), 0, 0, 0, Math.floor(R() * 4), R() < 0.5);
  else for (let lv = 0; lv < 2; lv++) {
    if (ov && ov[lv]) { ov[lv](put, col, R); continue; }
    const free = [[0, 0], [1, 0], [0, 1], [1, 1]].filter(c => !col || c[0] !== col.cell[0] || c[1] !== col.cell[1]);
    const r = R();
    if (!col && r < 0.3) { put(pickKind('quad', R(), 'pillars'), 0, 0, lv, Math.floor(R() * 4), R() < 0.5); continue; }
    if (!col && r < 0.6) {       // two long rooms, side by side
      const alongX = R() < 0.5;
      for (let k = 0; k < 2; k++) {
        const pf = long(), flip = R() < 0.5;
        if (alongX) put(pf, 0, k, lv, flip ? 2 : 0, R() < 0.5); else put(pf, k, 0, lv, flip ? 3 : 1, R() < 0.5);
      }
      continue;
    }
    if (r < (col ? 0.6 : 0.8)) { // one long room and whatever is left in singles
      const opts = [];
      for (const [a, b] of [[[0, 0], [1, 0]], [[0, 1], [1, 1]], [[0, 0], [0, 1]], [[1, 0], [1, 1]]])
        if (free.some(c => c[0] === a[0] && c[1] === a[1]) && free.some(c => c[0] === b[0] && c[1] === b[1])) opts.push([a, b]);
      const [a, b] = opts[Math.floor(R() * opts.length)];
      const pf = long(), flip = R() < 0.5;
      if (a[1] === b[1]) put(pf, 0, a[1], lv, flip ? 2 : 0, R() < 0.5); else put(pf, a[0], 0, lv, flip ? 3 : 1, R() < 0.5);
      for (const c of free) if (!(c[0] === a[0] && c[1] === a[1]) && !(c[0] === b[0] && c[1] === b[1])) put(one(), c[0], c[1], lv, Math.floor(R() * 4), R() < 0.5);
      continue;
    }
    for (const c of free) put(one(), c[0], c[1], lv, Math.floor(R() * 4), R() < 0.5);
  }
  if (col) for (let lv = 0; lv < 2; lv++) put(col.type, col.cell[0], col.cell[1], lv, col.rot, 0);
  if (PLAN_CACHE.size > 600) PLAN_CACHE.delete(PLAN_CACHE.keys().next().value);
  PLAN_CACHE.set(key, p);
  return p;
}
/* the placement covering a cell, with its footprint */
function footprint(pl) { const s = ROOM_SIZE[pl.pf]; return (pl.rot & 1) ? [s[1], s[0], s[2]] : [s[0], s[1], s[2]]; }
function roomAt(cx, cz, lv) {
  const bx = fdiv(cx, 2), bz = fdiv(cz, 2), bl = fdiv(lv, 2);
  for (const pl of planAt(bx, bz, bl)) {
    const f = footprint(pl);
    if (cx >= pl.cx && cx < pl.cx + f[0] && cz >= pl.cz && cz < pl.cz + f[1] && lv >= pl.lv && lv < pl.lv + f[2]) return pl;
  }
  return null;
}
const placeKey = pl => pl.pf + '@' + pl.cx + ',' + pl.cz + ',' + pl.lv;

/* local room space -> world (relative to the origin cell): mirror, then turn in 90 degree steps */
function placeMatrix(pl, ox, oy, oz, m) {
  const s = ROOM_SIZE[pl.pf], W = s[0] * RC, D = s[1] * RC;
  m = m || new THREE.Matrix4();
  const tx = (pl.cx - ox) * RC, ty = (pl.lv - oy) * RLH, tz = (pl.cz - oz) * RC;
  const mx = pl.mir ? -1 : 1, mo = pl.mir ? W : 0;
  // x_m = mx * x + mo ; then rotate (x_m, z)
  let a, b, c, d, e, f;   // x' = a*x_m + b*z + e ; z' = c*x_m + d*z + f
  switch (pl.rot) {
    case 0: a = 1; b = 0; c = 0; d = 1; e = 0; f = 0; break;
    case 1: a = 0; b = -1; c = 1; d = 0; e = D; f = 0; break;
    case 2: a = -1; b = 0; c = 0; d = -1; e = W; f = D; break;
    default: a = 0; b = 1; c = -1; d = 0; e = 0; f = W; break;
  }
  m.set(a * mx, 0, b, a * mo + e + tx,
        0, 1, 0, ty,
        c * mx, 0, d, c * mo + f + tz,
        0, 0, 0, 1);
  return m;
}

/* ==========================================================================
   Streaming: rooms around you are placed; far ones are dropped
   ========================================================================== */
const WORLD = { inst: new Map(), origin: [0, 0, 0], radius: 3, colK: 6, ready: false, bookR: 14, onPlace: null, pinned: new Set() };
function worldOrigin(cx, cz, lv) { WORLD.origin = [cx, lv, cz]; }
function makeInst(pl, slot) {
  const pf = PREFABS.get(pl.pf);
  if (!pf || pf instanceof Promise || !pf.meshes) return null;
  const r = roomInstance(pf);
  r.pl = pl; r.slot = slot; r.m = new THREE.Matrix4(); r.inv = new THREE.Matrix4(); r.key = placeKey(pl) + (slot !== undefined ? '#' + slot : '');
  r.grp.matrixAutoUpdate = false; r.water.matrixAutoUpdate = false;
  scene.add(r.grp); waterScene.add(r.water);
  if (!pf.probeDone) captureProbe(pf);
  return r;
}
function dropInst(r) {
  scene.remove(r.grp); waterScene.remove(r.water);
  if (r.books) { r.books.geometry.dispose(); r.grp.remove(r.books); r.books = null; }
}
function positionInst(r) {
  const [ox, oy, oz] = WORLD.origin;
  const pl = r.slot !== undefined ? Object.assign({}, r.pl, { lv: oy + r.slot }) : r.pl;
  placeMatrix(pl, ox, oy, oz, r.m); r.inv.copy(r.m).invert();
  r.grp.matrix.copy(r.m); r.grp.matrixWorldNeedsUpdate = true;
  r.water.matrix.copy(r.m); r.water.matrixWorldNeedsUpdate = true;
  r.lv = pl.lv;
  const f = footprint(r.pl);
  r.box = [(pl.cx - ox) * RC, (pl.lv - oy) * RLH - 2, (pl.cz - oz) * RC, (pl.cx - ox + f[0]) * RC, (pl.lv - oy + f[2]) * RLH, (pl.cz - oz + f[1]) * RC];
}
function updateWorld(px, py, pz, fastFall) {
  const [ox, oy, oz] = WORLD.origin, want = new Map(), R = WORLD.radius;
  // the level you are on: feet may be a little below its floor (in a pool) or up to 6 m above it (on a ramp)
  const pcx = ox + Math.floor(px / RC), pcz = oz + Math.floor(pz / RC), plv = oy + Math.floor((py + 2) / RLH);
  if (!fastFall) for (let dz = -R; dz <= R; dz++) for (let dx = -R; dx <= R; dx++) {
    const pl = roomAt(pcx + dx, pcz + dz, plv);
    if (pl && !COLUMN_ROOMS[pl.pf]) want.set(placeKey(pl), [pl, undefined]);
  }
  // wells and towers: a stack of copies above and below you
  for (let dz = -2; dz <= 2; dz++) for (let dx = -2; dx <= 2; dx++) {
    const cx = pcx + dx, cz = pcz + dz, col = columnAt(fdiv(cx, 2), fdiv(cz, 2));
    if (!col || mod(cx, 2) !== col.cell[0] || mod(cz, 2) !== col.cell[1]) continue;
    if (fastFall && (Math.abs(dx) > 0 || Math.abs(dz) > 0)) continue;
    const base = { pf: col.type, cx, cz, lv: 0, rot: col.rot, mir: 0 };
    const K = Math.abs(dx) + Math.abs(dz) === 0 ? WORLD.colK : 2;
    for (let s = -K; s <= K; s++) want.set(col.type + '@' + cx + ',' + cz + '#' + s, [base, s]);
  }
  for (const [k, r] of WORLD.inst) if (!want.has(k)) { dropInst(r); WORLD.inst.delete(k); }
  const keep = new Set();
  for (const [k, [pl, s]] of want) {
    keep.add(pl.pf);
    let r = WORLD.inst.get(k);
    if (!r) { r = makeInst(pl, s); if (!r) { requestPrefab(pl.pf); continue; } WORLD.inst.set(k, r); if (WORLD.onPlace) WORLD.onPlace(r); }
    positionInst(r);
  }
  // fetch what is a little further off, so it is ready before you get there
  if (!fastFall) for (const n of roomsNear(pcx, pcz, plv, R + 1, 0)) { keep.add(n); requestPrefab(n); }
  evictPrefabs(keep);
}
const PENDING = new Set();
function requestPrefab(name) {
  if (PREFABS.has(name) || PENDING.has(name) || !ROOM_SIZE[name]) return;
  PENDING.add(name);
  loadPrefab(name).then(() => PENDING.delete(name), e => { console.error(e); PENDING.delete(name); PREFABS.delete(name); });
}
/* every room within r cells (and dl levels) of a cell, columns included */
function roomsNear(cx0, cz0, lv0, r, dl) {
  const out = new Set();
  for (let lv = lv0 - dl; lv <= lv0 + dl; lv++) for (let dz = -r; dz <= r; dz++) for (let dx = -r; dx <= r; dx++) {
    const pl = roomAt(cx0 + dx, cz0 + dz, lv); if (pl) out.add(pl.pf);
  }
  for (let dz = -r; dz <= r; dz++) for (let dx = -r; dx <= r; dx++) {
    const cx = cx0 + dx, cz = cz0 + dz, col = columnAt(fdiv(cx, 2), fdiv(cz, 2));
    if (col && mod(cx, 2) === col.cell[0] && mod(cz, 2) === col.cell[1]) out.add(col.type);
  }
  return out;
}
const PREFAB_KEEP = 26;
function evictPrefabs(keep) {
  let n = 0; for (const v of PREFABS.values()) if (!(v instanceof Promise)) n++;
  if (n <= PREFAB_KEEP) return;
  for (const [name, v] of PREFABS) {
    if (n <= PREFAB_KEEP) break;
    if (v instanceof Promise || keep.has(name) || WORLD.pinned.has(name)) continue;
    disposePrefab(name); n--;
  }
}
/* is the room under this point loaded yet? (the player waits for it rather than falling into nothing) */
function roomReadyAt(px, py, pz) {
  const [ox, oy, oz] = WORLD.origin;
  const cx = ox + Math.floor(px / RC), cz = oz + Math.floor(pz / RC), lv = oy + Math.floor((py + 2) / RLH);
  let pl = roomAt(cx, cz, lv);
  if (!pl) { const col = columnAt(fdiv(cx, 2), fdiv(cz, 2)); if (col && mod(cx, 2) === col.cell[0] && mod(cz, 2) === col.cell[1]) pl = { pf: col.type }; }
  if (!pl) return true;
  const v = PREFABS.get(pl.pf);
  if (!v || v instanceof Promise) { requestPrefab(pl.pf); return false; }
  // loaded, but maybe not placed yet (placement runs every half second): place it now
  if (!instAt(px, py, pz)) { updateWorld(px, py - 0.5, pz, false); return !!instAt(px, py, pz); }
  return true;
}
/* the room instance you are standing in */
function instAt(x, y, z) {
  let best = null;
  for (const r of WORLD.inst.values()) {
    const b = r.box;
    if (x >= b[0] && x < b[3] && z >= b[2] && z < b[5] && y >= b[1] && y < b[4] + 0.5) { if (!best || (r.slot === 0 || r.slot === undefined)) best = r; }
  }
  return best;
}

/* ==========================================================================
   Collision against the baked geometry (in each room's own space)
   ========================================================================== */
const _v = new THREE.Vector3(), _w = new THREE.Vector3();
function triNormals(pf) {
  if (pf.nrm) return pf.nrm;
  const c = pf.col, n = new Float32Array(c.length / 3);
  for (let t = 0, o = 0; o < c.length; t++, o += 9) {
    const ax = c[o + 3] - c[o], ay = c[o + 4] - c[o + 1], az = c[o + 5] - c[o + 2], bx = c[o + 6] - c[o], by = c[o + 7] - c[o + 1], bz = c[o + 8] - c[o + 2];
    let nx = ay * bz - az * by, ny = az * bx - ax * bz, nz = ax * by - ay * bx; const l = Math.hypot(nx, ny, nz) || 1;
    n[t * 3] = nx / l; n[t * 3 + 1] = ny / l; n[t * 3 + 2] = nz / l;
  }
  return pf.nrm = n;
}
function closestOnTri(px, py, pz, c, o, out) {
  const ax = c[o], ay = c[o + 1], az = c[o + 2], bx = c[o + 3], by = c[o + 4], bz = c[o + 5], cx = c[o + 6], cy = c[o + 7], cz = c[o + 8];
  const abx = bx - ax, aby = by - ay, abz = bz - az, acx = cx - ax, acy = cy - ay, acz = cz - az, apx = px - ax, apy = py - ay, apz = pz - az;
  const d1 = abx * apx + aby * apy + abz * apz, d2 = acx * apx + acy * apy + acz * apz;
  if (d1 <= 0 && d2 <= 0) { out[0] = ax; out[1] = ay; out[2] = az; return; }
  const bpx = px - bx, bpy = py - by, bpz = pz - bz, d3 = abx * bpx + aby * bpy + abz * bpz, d4 = acx * bpx + acy * bpy + acz * bpz;
  if (d3 >= 0 && d4 <= d3) { out[0] = bx; out[1] = by; out[2] = bz; return; }
  const vc = d1 * d4 - d3 * d2;
  if (vc <= 0 && d1 >= 0 && d3 <= 0) { const v = d1 / (d1 - d3); out[0] = ax + abx * v; out[1] = ay + aby * v; out[2] = az + abz * v; return; }
  const cpx = px - cx, cpy = py - cy, cpz = pz - cz, d5 = abx * cpx + aby * cpy + abz * cpz, d6 = acx * cpx + acy * cpy + acz * cpz;
  if (d6 >= 0 && d5 <= d6) { out[0] = cx; out[1] = cy; out[2] = cz; return; }
  const vb = d5 * d2 - d1 * d6;
  if (vb <= 0 && d2 >= 0 && d6 <= 0) { const w = d2 / (d2 - d6); out[0] = ax + acx * w; out[1] = ay + acy * w; out[2] = az + acz * w; return; }
  const va = d3 * d6 - d5 * d4;
  if (va <= 0 && (d4 - d3) >= 0 && (d5 - d6) >= 0) { const w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); out[0] = bx + (cx - bx) * w; out[1] = by + (cy - by) * w; out[2] = bz + (cz - bz) * w; return; }
  const den = 1 / (va + vb + vc), v = vb * den, w = vc * den;
  out[0] = ax + abx * v + acx * w; out[1] = ay + aby * v + acy * w; out[2] = az + abz * v + acz * w;
}
const _cp = [0, 0, 0], _seen = new Set();
function gridTris(pf, x0, y0, z0, x1, y1, z1, fn) {
  const G = pf.grid, cs = G.cs; _seen.clear();
  for (let i = Math.floor(x0 / cs); i <= Math.floor(x1 / cs); i++) for (let j = Math.floor(y0 / cs); j <= Math.floor(y1 / cs); j++) for (let k = Math.floor(z0 / cs); k <= Math.floor(z1 / cs); k++) {
    const a = G.grid.get(i + ',' + j + ',' + k); if (!a) continue;
    for (const t of a) { if (_seen.has(t)) continue; _seen.add(t); fn(t); }
  }
}
/* Push a sphere (world space) out of the rooms near it. Returns the push, and a floor normal if it touched one. */
function pushSphere(p, r, onlyWalls, info) {
  for (const inst of WORLD.inst.values()) {
    const b = inst.box;
    if (p.x < b[0] - r || p.x > b[3] + r || p.z < b[2] - r || p.z > b[5] + r || p.y < b[1] - r - 1 || p.y > b[4] + r + 1) continue;
    const pf = inst.pf, c = pf.col, nrm = triNormals(pf);
    _v.copy(p).applyMatrix4(inst.inv);
    const lx = _v.x, ly = _v.y, lz = _v.z;
    let mx = 0, my = 0, mz = 0;
    gridTris(pf, lx - r, ly - r, lz - r, lx + r, ly + r, lz + r, t => {
      const ny = nrm[t * 3 + 1];
      if (onlyWalls && ny > 0.7) return;
      closestOnTri(lx + mx, ly + my, lz + mz, c, t * 9, _cp);
      const dx = lx + mx - _cp[0], dy = ly + my - _cp[1], dz = lz + mz - _cp[2], d2 = dx * dx + dy * dy + dz * dz;
      if (d2 >= r * r) return;
      const d = Math.sqrt(d2);
      let ux, uy, uz;
      if (d > 1e-5) { ux = dx / d; uy = dy / d; uz = dz / d; } else { ux = nrm[t * 3]; uy = ny; uz = nrm[t * 3 + 2]; }
      const pen = r - d;
      if (onlyWalls) { const hl = Math.hypot(ux, uz); if (hl < 1e-4) return; mx += ux / hl * pen; mz += uz / hl * pen; }
      else { mx += ux * pen; my += uy * pen; mz += uz * pen; }
      if (info && uy > 0.7) info.floor = true;
      if (info && uy < -0.7) info.ceil = true;
    });
    if (mx || my || mz) {
      _w.set(mx, my, mz).transformDirection(inst.m).multiplyScalar(Math.hypot(mx, my, mz));
      p.x += _w.x; p.y += _w.y; p.z += _w.z;
    }
  }
}
/* Highest walkable surface under (x, z) between y - down and y + up (world space); -Infinity if none. */
function groundAt(x, y, z, up, down) {
  let best = -Infinity;
  for (const inst of WORLD.inst.values()) {
    const b = inst.box;
    if (x < b[0] - 0.1 || x > b[3] + 0.1 || z < b[2] - 0.1 || z > b[5] + 0.1) continue;
    if (y + up < b[1] - 1 || y - down > b[4] + 1) continue;
    const pf = inst.pf, c = pf.col, nrm = triNormals(pf);
    _v.set(x, y, z).applyMatrix4(inst.inv);
    const lx = _v.x, ly = _v.y, lz = _v.z, oyw = y - ly;   // rooms never tilt, so world y = local y + offset
    gridTris(pf, lx - 0.01, ly - down, lz - 0.01, lx + 0.01, ly + up, lz + 0.01, t => {
      if (nrm[t * 3 + 1] < 0.35) return;
      const o = t * 9;
      const ax = c[o], az = c[o + 2], bx = c[o + 3], bz = c[o + 5], cx = c[o + 6], cz = c[o + 8];
      const d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz); if (Math.abs(d) < 1e-9) return;
      const u = ((bz - cz) * (lx - cx) + (cx - bx) * (lz - cz)) / d, v = ((cz - az) * (lx - cx) + (ax - cx) * (lz - cz)) / d, w = 1 - u - v;
      if (u < -1e-4 || v < -1e-4 || w < -1e-4) return;
      const h = u * c[o + 1] + v * c[o + 4] + w * c[o + 7];
      if (h <= ly + up && h >= ly - down && h + oyw > best) best = h + oyw;
    });
  }
  return best;
}
/* Ground under a small foot: the highest of the centre and a ring 12 cm out, so a crack narrower than
   a shoe (a gap between a landing and a gallery) cannot swallow you */
function footing(x, y, z, up, down) {
  let g = groundAt(x, y, z, up, down);
  // the ring only keeps you from dropping through a crack: it never lifts you (or you could climb a rail's thin bar)
  for (const [dx, dz] of [[0.12, 0], [-0.12, 0], [0, 0.12], [0, -0.12]]) { const r = groundAt(x + dx, y, z + dz, up, down); if (r > g && r <= y + 0.05) g = r; }
  return g;
}
/* Water: the volume holding a point (world), as { top, bot } in world y, or null */
function waterAt(x, y, z) {
  for (const inst of WORLD.inst.values()) {
    const b = inst.box;
    if (x < b[0] || x > b[3] || z < b[2] || z > b[5] || y < b[1] - 2 || y > b[4]) continue;
    _v.set(x, y, z).applyMatrix4(inst.inv);
    const oyw = y - _v.y;
    for (const w of inst.pf.meta.water) {
      const inside = w.r !== undefined ? Math.hypot(_v.x - w.cx, _v.z - w.cz) < w.r : (_v.x > w.x0 && _v.x < w.x1 && _v.z > w.z0 && _v.z < w.z1);
      if (inside && _v.y < w.top + 2.5 && _v.y > w.bot - 0.5) return { top: w.top + oyw, bot: w.bot + oyw };
    }
  }
  return null;
}

/* ---------- rays: the first bit of room a ray hits, and the book under your crosshair ---------- */
function rayHit(o, d, maxT) {
  let best = maxT;
  for (const inst of WORLD.inst.values()) {
    const b = inst.box;
    // ray vs box
    let t0 = 0, t1 = best;
    for (let a = 0; a < 3; a++) {
      const oo = a === 0 ? o.x : a === 1 ? o.y : o.z, dd = a === 0 ? d.x : a === 1 ? d.y : d.z, lo = b[a], hi = b[a + 3];
      if (Math.abs(dd) < 1e-9) { if (oo < lo || oo > hi) { t0 = 1; t1 = 0; } continue; }
      let ta = (lo - oo) / dd, tb = (hi - oo) / dd; if (ta > tb) { const q = ta; ta = tb; tb = q; }
      t0 = Math.max(t0, ta); t1 = Math.min(t1, tb);
    }
    if (t0 > t1) continue;
    const pf = inst.pf, c = pf.col;
    const lo = _v.copy(o).applyMatrix4(inst.inv), ld = _w.copy(d).transformDirection(inst.inv);
    const ex = lo.x + ld.x * best, ey = lo.y + ld.y * best, ez = lo.z + ld.z * best;
    gridTris(pf, Math.min(lo.x, ex), Math.min(lo.y, ey), Math.min(lo.z, ez), Math.max(lo.x, ex), Math.max(lo.y, ey), Math.max(lo.z, ez), t => {
      const q = t * 9;
      const e1x = c[q + 3] - c[q], e1y = c[q + 4] - c[q + 1], e1z = c[q + 5] - c[q + 2], e2x = c[q + 6] - c[q], e2y = c[q + 7] - c[q + 1], e2z = c[q + 8] - c[q + 2];
      const px = ld.y * e2z - ld.z * e2y, py = ld.z * e2x - ld.x * e2z, pz = ld.x * e2y - ld.y * e2x, det = e1x * px + e1y * py + e1z * pz;
      if (Math.abs(det) < 1e-9) return;
      const inv = 1 / det, sx = lo.x - c[q], sy = lo.y - c[q + 1], sz = lo.z - c[q + 2], u = (sx * px + sy * py + sz * pz) * inv; if (u < 0 || u > 1) return;
      const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x, v = (ld.x * qx + ld.y * qy + ld.z * qz) * inv; if (v < 0 || u + v > 1) return;
      const tt = (e2x * qx + e2y * qy + e2z * qz) * inv;
      if (tt > 1e-4 && tt < best) best = tt;
    });
  }
  return best;
}
function bookRay(o, d, maxT) {
  let best = null, bt = maxT;
  for (const inst of WORLD.inst.values()) {
    if (!inst.books || !inst.slabX) continue;
    const b = inst.box;
    if (o.x < b[0] - 4 || o.x > b[3] + 4 || o.z < b[2] - 4 || o.z > b[5] + 4 || o.y < b[1] - 4 || o.y > b[4] + 4) continue;
    const lo = _v.copy(o).applyMatrix4(inst.inv), ld = _w.copy(d).transformDirection(inst.inv);
    const SL = inst.pf.meta.slabs;
    for (let si = 0; si < SL.length; si++) {
      const s = SL[si], n = s.n, den = ld.x * n[0] + ld.z * n[2];
      if (den > -1e-3) continue;
      const t = ((s.o[0] - lo.x) * n[0] + (s.o[2] - lo.z) * n[2]) / den;
      if (t < 0 || t >= bt) continue;
      const hx = lo.x + ld.x * t - s.o[0], hy = lo.y + ld.y * t - s.o[1], hz = lo.z + ld.z * t - s.o[2];
      if (hy < 0 || hy > s.h) continue;
      const su = (hx * s.u[0] + hz * s.u[2]) / s.len;
      if (su < 0 || su > s.len) continue;
      const xs = inst.slabX[si]; if (!xs || !xs.length) continue;
      let lo_ = 0, hi_ = xs.length - 1;
      while (lo_ < hi_) { const m = (lo_ + hi_ + 1) >> 1; if (xs[m][0] <= su) lo_ = m; else hi_ = m - 1; }
      const [x0, w] = xs[lo_]; if (su > x0 + w + 0.002) continue;
      bt = t; best = { t, inst, si, p: lo_ };
    }
  }
  return best;
}
/* where a local point of a placed room lands in world (render) space */
function instPoint(inst, p, out) { return (out || new THREE.Vector3()).fromArray(p).applyMatrix4(inst.m); }
/* the water pass reads this frame's opaque colour and depth */
beforeWater = rt => {
  SHAFT_U.tDepth.value = rt.depthTexture; SHAFT_U.uRes.value.set(RW, RHh); SHAFT_U.uProjInv.value.copy(camera.projectionMatrixInverse);
  for (const pf of PREFABS.values()) {
    if (!pf || !pf.waterMat) continue;
    const u = pf.waterMat.uniforms; u.tScene.value = rt.texture; u.tDepth.value = rt.depthTexture; u.uRes.value.set(RW, RHh);
    u.uProj.value.copy(camera.projectionMatrix); u.uProjInv.value.copy(camera.projectionMatrixInverse);
  }
};
