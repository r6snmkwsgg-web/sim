'use strict';
/* ==========================================================================
   Renderer: HDR scene → bloom → filmic tone map, grade, grain
   ========================================================================== */
const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: 'high-performance', stencil: false });
renderer.outputEncoding = THREE.LinearEncoding;
renderer.toneMapping = THREE.NoToneMapping;
renderer.setSize(innerWidth, innerHeight);
$('#game').appendChild(renderer.domElement);
const GL2 = renderer.capabilities.isWebGL2;
const HALF = GL2 || renderer.extensions.has('OES_texture_half_float');
const FOG_LIN = new THREE.Color(0.0065, 0.0075, 0.0105);
const FOG_DEEP = new THREE.Color(0.002, 0.0028, 0.0055);
renderer.setClearColor(FOG_LIN, 1);
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(FOG_LIN, 0.02);
const camera = new THREE.PerspectiveCamera(72, innerWidth / innerHeight, 0.04, 360);
camera.rotation.order = 'YXZ';
scene.add(camera);

let AQ = 1; // automatic resolution scale, lowered if frames run long
let RT = null, BD = [], BU = [], RW = 1, RHh = 1;
function rtOpts(depth) { return { type: HALF ? THREE.HalfFloatType : THREE.UnsignedByteType, format: THREE.RGBAFormat, depthBuffer: depth, stencilBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter }; }
function makeTargets() {
  const pr = Math.min(window.devicePixelRatio || 1, 1.5) * (S ? S.settings.q : 1) * AQ;
  const w = Math.max(2, Math.floor(innerWidth * pr)), h = Math.max(2, Math.floor(innerHeight * pr));
  if (RT && RW === w && RHh === h) return;
  RW = w; RHh = h;
  [RT, ...BD, ...BU].forEach(t => t && t.dispose());
  if (GL2 && THREE.WebGLMultisampleRenderTarget) { RT = new THREE.WebGLMultisampleRenderTarget(w, h, rtOpts(true)); RT.samples = 4; }
  else RT = new THREE.WebGLRenderTarget(w, h, rtOpts(true));
  BD = []; BU = [];
  let bw = w >> 1, bh = h >> 1;
  for (let i = 0; i < 5; i++) { BD.push(new THREE.WebGLRenderTarget(Math.max(1, bw), Math.max(1, bh), rtOpts(false))); BU.push(new THREE.WebGLRenderTarget(Math.max(1, bw), Math.max(1, bh), rtOpts(false))); bw >>= 1; bh >>= 1; }
  renderer.setPixelRatio(pr); renderer.setSize(innerWidth, innerHeight);
}
function applyQuality() { RT && (RW = -1); makeTargets(); }

const fsCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const fsGeo = new THREE.BufferGeometry();
fsGeo.setAttribute('position', new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
fsGeo.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 2, 0, 0, 2], 2));
const fsMesh = new THREE.Mesh(fsGeo); fsMesh.frustumCulled = false;
const fsScene = new THREE.Scene(); fsScene.add(fsMesh);
const FS_VS = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';
const passMat = (fs, u) => new THREE.ShaderMaterial({ vertexShader: FS_VS, fragmentShader: fs, uniforms: u, depthTest: false, depthWrite: false });
const PM = {
  pre: passMat(`uniform sampler2D tSrc; uniform vec2 uTexel; uniform float uThresh; varying vec2 vUv;
    void main(){ vec3 c = texture2D(tSrc, vUv).rgb * 0.5;
      c += (texture2D(tSrc, vUv + uTexel * vec2(-1.0, -1.0)).rgb + texture2D(tSrc, vUv + uTexel * vec2(1.0, -1.0)).rgb + texture2D(tSrc, vUv + uTexel * vec2(-1.0, 1.0)).rgb + texture2D(tSrc, vUv + uTexel * vec2(1.0, 1.0)).rgb) * 0.125;
      #if __VERSION__ >= 300
        if (any(isnan(c)) || any(isinf(c))) c = vec3(0.0);
      #endif
      c = clamp(c, 0.0, 24.0);
      float br = max(c.r, max(c.g, c.b)); float soft = clamp(br - uThresh + 0.6, 0.0, 1.2); soft = soft * soft / 4.8;
      float k = max(soft, br - uThresh) / max(br, 1e-4);
      gl_FragColor = vec4(c * k, 1.0); }`, { tSrc: { value: null }, uTexel: { value: new THREE.Vector2() }, uThresh: { value: 1.0 } }),
  down: passMat(`uniform sampler2D tSrc; uniform vec2 uTexel; varying vec2 vUv;
    void main(){ vec2 o = uTexel; vec3 s = texture2D(tSrc, vUv).rgb * 4.0;
      s += texture2D(tSrc, vUv - o).rgb + texture2D(tSrc, vUv + o).rgb + texture2D(tSrc, vUv + vec2(o.x, -o.y)).rgb + texture2D(tSrc, vUv - vec2(o.x, -o.y)).rgb;
      gl_FragColor = vec4(s / 8.0, 1.0); }`, { tSrc: { value: null }, uTexel: { value: new THREE.Vector2() } }),
  up: passMat(`uniform sampler2D tSrc; uniform sampler2D tAdd; uniform vec2 uTexel; uniform float uAdd; varying vec2 vUv;
    void main(){ vec2 o = uTexel; vec3 s = vec3(0.0);
      s += texture2D(tSrc, vUv + vec2(-o.x * 2.0, 0.0)).rgb + texture2D(tSrc, vUv + vec2(o.x * 2.0, 0.0)).rgb + texture2D(tSrc, vUv + vec2(0.0, o.y * 2.0)).rgb + texture2D(tSrc, vUv + vec2(0.0, -o.y * 2.0)).rgb;
      s += (texture2D(tSrc, vUv + vec2(-o.x, o.y)).rgb + texture2D(tSrc, vUv + vec2(o.x, o.y)).rgb + texture2D(tSrc, vUv + vec2(o.x, -o.y)).rgb + texture2D(tSrc, vUv + vec2(-o.x, -o.y)).rgb) * 2.0;
      gl_FragColor = vec4(s / 12.0 + texture2D(tAdd, vUv).rgb * uAdd, 1.0); }`, { tSrc: { value: null }, tAdd: { value: null }, uTexel: { value: new THREE.Vector2() }, uAdd: { value: 1 } }),
  comp: passMat(`uniform sampler2D tScene; uniform sampler2D tBloom; uniform float uBloom; uniform float uExposure; uniform float uTime; uniform float uVig; uniform float uGrain; uniform float uCA; uniform float uDrunk; uniform float uHurt; uniform float uSpeed; varying vec2 vUv;
    vec3 aces(vec3 x){ return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
    void main(){
      vec2 uv = vUv;
      uv += uDrunk * 0.007 * vec2(sin(uTime * 1.3 + uv.y * 6.0), cos(uTime * 1.1 + uv.x * 5.0));
      vec2 dc = uv - 0.5; float r2 = dot(dc, dc);
      float ca = uCA * r2 * (1.0 + uDrunk * 4.0 + uSpeed * 2.0);
      vec3 col = vec3(texture2D(tScene, uv - dc * ca).r, texture2D(tScene, uv).g, texture2D(tScene, uv + dc * ca).b);
      if (uSpeed > 0.01) { vec3 acc = col; for (int i = 1; i <= 5; i++) { acc += texture2D(tScene, uv - dc * float(i) * 0.012 * uSpeed).rgb; } col = acc / 6.0; }
      col += texture2D(tBloom, uv).rgb * uBloom;
      #if __VERSION__ >= 300
        if (any(isnan(col)) || any(isinf(col))) col = vec3(0.0);
      #endif
      col = clamp(col, 0.0, 40.0) * uExposure;
      col = aces(col);
      float l = dot(col, vec3(0.2126, 0.7152, 0.0722));
      col = mix(vec3(l), col, 0.9);
      col += vec3(-0.003, 0.004, 0.012) * (1.0 - l) * (1.0 - l);
      col *= mix(vec3(1.0), vec3(1.05, 1.0, 0.92), smoothstep(0.2, 0.9, l));
      col = pow(max(col, 0.0), vec3(1.0 / 2.2));
      col = mix(col, col * vec3(1.0, 0.25, 0.2), uHurt * smoothstep(0.1, 0.7, sqrt(r2) * 1.4));
      col *= 1.0 - uVig * smoothstep(0.25, 0.95, sqrt(r2) * 1.38);
      float n = fract(sin(dot(gl_FragCoord.xy + fract(uTime) * 91.0, vec2(12.9898, 78.233))) * 43758.5453);
      col += (n - 0.5) * uGrain;
      gl_FragColor = vec4(col, 1.0); }`, { tScene: { value: null }, tBloom: { value: null }, uBloom: { value: 0.9 }, uExposure: { value: 1 }, uTime: { value: 0 }, uVig: { value: 0.55 }, uGrain: { value: 0.035 }, uCA: { value: 0.012 }, uDrunk: { value: 0 }, uHurt: { value: 0 }, uSpeed: { value: 0 } }),
};
function pass(mat, target) { fsMesh.material = mat; renderer.setRenderTarget(target); renderer.render(fsScene, fsCam); }
function renderFrame() {
  makeTargets();
  renderer.setRenderTarget(RT); renderer.clear(); renderer.render(scene, camera);
  const bloom = !S || S.settings.fx !== 0;
  if (bloom) {
    PM.pre.uniforms.tSrc.value = RT.texture; PM.pre.uniforms.uTexel.value.set(1 / RW, 1 / RHh); pass(PM.pre, BD[0]);
    for (let i = 1; i < BD.length; i++) { PM.down.uniforms.tSrc.value = BD[i - 1].texture; PM.down.uniforms.uTexel.value.set(1 / BD[i - 1].width, 1 / BD[i - 1].height); pass(PM.down, BD[i]); }
    let src = BD[BD.length - 1];
    for (let i = BD.length - 2; i >= 0; i--) { PM.up.uniforms.tSrc.value = src.texture; PM.up.uniforms.tAdd.value = BD[i].texture; PM.up.uniforms.uTexel.value.set(0.5 / src.width, 0.5 / src.height); pass(PM.up, BU[i]); src = BU[i]; }
    PM.comp.uniforms.tBloom.value = BU[0].texture;
  } else PM.comp.uniforms.tBloom.value = BD[BD.length - 1].texture;
  PM.comp.uniforms.uBloom.value = bloom ? 0.85 : 0;
  PM.comp.uniforms.tScene.value = RT.texture;
  pass(PM.comp, null);
}

/* ==========================================================================
   Shared GLSL: periodic lamplight, fog, analytic occlusion
   ========================================================================== */
const U = {
  uLamp: { value: 1 }, uAmb: { value: new THREE.Color(0.0065, 0.007, 0.0095) },
  uFog: { value: FOG_LIN }, uFogDeep: { value: FOG_DEEP }, uFogD: { value: 0.02 },
  uLampCol: { value: new THREE.Color(1.0, 0.62, 0.3) }, uTime: { value: 0 }, uCellOff: { value: new THREE.Vector2() },
};
const GLSL_COMMON = `
uniform float uLamp; uniform vec3 uAmb; uniform vec3 uFog; uniform vec3 uFogDeep; uniform float uFogD; uniform vec3 uLampCol; uniform float uTime; uniform vec2 uCellOff;
varying vec3 vW;
vec3 gV;
float h11(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float lampScale(vec2 cell){ float h = h11(cell + uCellOff); float s = 0.72 + 0.56 * h; float fl = step(0.993, h) * (0.5 + 0.5 * sin(uTime * 19.0 + h * 90.0) * sin(uTime * 2.3 + h)); return s * (1.0 - fl); }
void addLamp(vec3 lp, float pw, vec3 N, float gloss, inout float D, inout float Sp){
  vec3 d = lp - vW; float d2 = dot(d, d) + 1e-3; vec3 L = d * inversesqrt(d2);
  float ndl = dot(N, L); float att = pw / (1.0 + d2 * 0.5);
  D += (max(ndl * 0.8 + 0.2, 0.0) + 0.14) * att;
  vec3 hv = normalize(L + gV);
  Sp += pow(max(dot(N, hv), 0.0), gloss) * att * step(0.0, ndl) * (gloss + 8.0) * 0.04;
}
void lighting(vec3 N, float gloss, out float D, out float Sp){
  D = 0.0; Sp = 0.0;
  float fl = floor((vW.y + 0.02) / 4.0); float ly = fl * 4.0 + 3.15;
  float ix = floor(vW.x / 4.0);
  for (int i = -1; i <= 1; i++) {
    float cx = ix + float(i); float x = cx * 4.0 + 2.0;
    addLamp(vec3(x, ly, -1.5), lampScale(vec2(cx, fl)), N, gloss, D, Sp);
    addLamp(vec3(x, ly, 17.5), lampScale(vec2(cx + 313.0, fl)), N, gloss, D, Sp);
  }
  float rc = floor((vW.x - 86.0) / 92.0 + 0.5) * 92.0 + 86.0;
  if (abs(vW.x - rc) < 22.0 && vW.z < 3.0) {
    addLamp(vec3(rc - 4.0, ly, -9.5), 1.5, N, gloss, D, Sp);
    addLamp(vec3(rc + 4.0, ly, -9.5), 1.5, N, gloss, D, Sp);
    addLamp(vec3(rc - 0.45, fl * 4.0 + 2.6, -8.5), 0.8, N, gloss, D, Sp);
  }
  float rc2 = floor((vW.x - 6.0) / 92.0 + 0.5) * 92.0 + 6.0;
  if (abs(vW.x - rc2) < 22.0 && vW.z > 13.0) {
    addLamp(vec3(rc2 + 4.0, ly, 25.5), 1.5, N, gloss, D, Sp);
    addLamp(vec3(rc2 - 4.0, ly, 25.5), 1.5, N, gloss, D, Sp);
    addLamp(vec3(rc2 + 0.45, fl * 4.0 + 2.6, 24.5), 0.8, N, gloss, D, Sp);
  }
  D *= uLamp; Sp *= uLamp;
}
vec3 fogIt(vec3 col, float D){
  vec3 dv = vW - cameraPosition; float d = length(dv);
  float f = 1.0 - exp(-pow(d * uFogD, 2.0));
  float vy = abs(dv.y) / max(d, 1e-3);
  vec3 fc = mix(uFog, uFogDeep, smoothstep(0.35, 0.95, vy)) + uLampCol * min(D, 3.0) * 0.006 * uLamp;
  return mix(col, fc, clamp(f, 0.0, 1.0));
}
float archAO(vec3 N){
  float ao = 1.0;
  float lx = vW.x - floor(vW.x / 92.0) * 92.0;
  float ly = vW.y - floor((vW.y + 0.02) / 4.0) * 4.0;
  bool opp = vW.z > 8.0; float z = opp ? 16.0 - vW.z : vW.z; float lxo = opp ? 92.0 - lx : lx;
  if (N.y > 0.5) {
    if (z > -3.3) { if (lxo < 80.0) ao *= mix(0.42, 1.0, smoothstep(0.0, 0.8, z + 3.0)); ao *= mix(0.7, 1.0, smoothstep(0.0, 0.4, -z)); }
    else { ao *= mix(0.55, 1.0, smoothstep(0.0, 0.7, z + 13.2)); ao *= mix(0.6, 1.0, smoothstep(0.0, 0.6, lxo - 80.0)) * mix(0.6, 1.0, smoothstep(0.0, 0.6, 92.0 - lxo)); }
  } else if (N.y < -0.5) {
    ao *= mix(0.5, 1.0, smoothstep(0.0, 0.9, min(z + 3.0, 0.3 - z)));
  } else {
    ao *= mix(0.5, 1.0, smoothstep(0.0, 0.5, ly)) * mix(0.72, 1.0, smoothstep(0.0, 0.45, 3.7 - ly));
  }
  return ao;
}
vec3 bumpN(vec3 N, float h, float s){
  vec3 dpx = dFdx(vW), dpy = dFdy(vW); float hx = dFdx(h), hy = dFdy(h);
  vec3 r1 = cross(dpy, N), r2 = cross(N, dpx); float det = dot(dpx, r1);
  if (abs(det) < 1e-12) return N;
  vec3 nn = abs(det) * N - s * sign(det) * (hx * r1 + hy * r2); float l = length(nn);
  return l > 1e-20 ? nn / l : N;
}
vec3 safeCol(vec3 c){
  #if __VERSION__ >= 300
    if (any(isnan(c)) || any(isinf(c))) return vec3(0.0);
  #endif
  return clamp(c, 0.0, 14.0);
}
`;
const WORLD_VS = `
varying vec3 vW; varying vec3 vN; varying vec2 vUv; varying vec3 vC;
#ifdef BOOK
attribute float aFace; attribute vec3 aStyle; varying float vFace; varying vec3 vStyle;
#endif
void main(){
  vec4 p = vec4(position, 1.0); vec3 n = normal;
  #ifdef USE_INSTANCING
    p = instanceMatrix * p; n = mat3(instanceMatrix) * n;
  #endif
  vec4 w = modelMatrix * p; vW = w.xyz; vN = mat3(modelMatrix) * n; vUv = uv; vC = vec3(1.0);
  #ifdef USE_COLOR
    vC *= color;
  #endif
  #ifdef USE_INSTANCING_COLOR
    vC *= instanceColor;
  #endif
  #ifdef BOOK
    vFace = aFace; vStyle = aStyle;
  #endif
  gl_Position = projectionMatrix * viewMatrix * w;
}`;
const WORLD_FS = `
uniform sampler2D uMap; uniform vec2 uRep; uniform float uTriS; uniform vec3 uColor; uniform float uGloss; uniform float uSpec; uniform float uBump; uniform float uTexGain; uniform float uEmis;
varying vec3 vN; varying vec2 vUv; varying vec3 vC;
#ifdef BOOK
varying float vFace; varying vec3 vStyle;
#endif
${GLSL_COMMON}
void main(){
  vec3 N = normalize(vN); gV = normalize(cameraPosition - vW);
  #ifdef DOUBLE
    if (!gl_FrontFacing) N = -N;
  #endif
  vec3 base = uColor * vC; float em = step(1.01, max(vC.r, max(vC.g, vC.b)));
  float spec = uSpec, gloss = uGloss, ao = 1.0;
  #ifdef TRI
    vec3 an = pow(abs(N), vec3(4.0)); an /= (an.x + an.y + an.z);
    vec3 t = texture2D(uMap, vW.zy * uTriS).rgb * an.x + texture2D(uMap, vW.xz * uTriS).rgb * an.y + texture2D(uMap, vW.xy * uTriS).rgb * an.z;
    t = pow(t, vec3(2.2));
    float hg = dot(t, vec3(0.3333));
    base *= t * uTexGain;
    N = bumpN(N, hg * 3.0, uBump);
    spec *= 0.35 + hg * 3.0;
  #endif
  #ifdef UVMAP
    base *= pow(texture2D(uMap, vUv * uRep).rgb, vec3(2.2)) * uTexGain;
  #endif
  #ifdef BOOK
    if (vFace < 0.5) {
      float bv = vUv.y, bu = vUv.x;
      N = normalize(N + vec3((bu - 0.5) * 1.1, 0.0, 0.0));
      float grain = h11(floor(vUv * vec2(5.0, 70.0)) + vStyle.z * 91.0);
      base *= (0.86 + 0.14 * grain) * (0.78 + 0.22 * sin(bu * 3.14159));
      float b1 = smoothstep(0.085, 0.095, bv) - smoothstep(0.115, 0.125, bv) + smoothstep(0.875, 0.885, bv) - smoothstep(0.905, 0.915, bv);
      float b2 = smoothstep(0.2, 0.21, bv) - smoothstep(0.225, 0.235, bv) + smoothstep(0.765, 0.775, bv) - smoothstep(0.79, 0.8, bv);
      float band = vStyle.x < 0.5 ? b1 : (vStyle.x < 1.5 ? b1 + b2 : 0.0);
      if (vStyle.x > 1.5) base *= 0.88 + 0.12 * step(0.5, fract(bv * 6.0 + 0.25));
      band = clamp(band, 0.0, 1.0);
      base = mix(base, vec3(0.42, 0.26, 0.06), band * 0.9); spec = mix(0.12, 1.4, band); gloss = mix(18.0, 80.0, band);
      if (vStyle.y > 0.5) { float lab = step(0.56, bv) * step(bv, 0.7) * step(0.2, bu) * step(bu, 0.8); base = mix(base, vec3(0.33, 0.29, 0.21), lab * 0.9); }
      base *= 1.0 - 0.3 * vStyle.z * (smoothstep(0.36, 0.5, abs(bu - 0.5)) + smoothstep(0.43, 0.5, abs(bv - 0.5)));
      ao *= mix(0.55, 1.0, smoothstep(0.0, 0.14, bv));
    } else if (vFace < 1.5) {
      vec3 pg = vec3(0.42, 0.36, 0.25) * (0.88 + 0.12 * sin(vUv.x * 420.0));
      base = mix(base * 0.8, pg, step(0.09, vUv.x) * step(vUv.x, 0.91));
      ao *= mix(0.35, 1.0, vUv.y);
    } else { base *= 0.7; ao *= 0.7; }
    float rly = vW.y - floor((vW.y + 0.02) / 4.0) * 4.0; float rv = mod(rly - 0.12, 0.46);
    ao *= mix(0.5, 1.0, smoothstep(0.0, 0.12, 0.43 - rv));
  #else
    ao *= archAO(N);
  #endif
  float D, Sp; lighting(N, gloss, D, Sp);
  vec3 col = base * (uAmb * (0.55 + 0.45 * N.y) * ao + uLampCol * D * ao) + uLampCol * Sp * spec * ao;
  col = safeCol(col);
  col = mix(col, vC * uLampCol * uEmis * uLamp, em);
  gl_FragColor = vec4(fogIt(col, D), 1.0);
}`;
function makeMat(o = {}) {
  const defines = {};
  if (o.tri) defines.TRI = 1; else if (o.map) defines.UVMAP = 1;
  if (o.book) defines.BOOK = 1;
  if (o.double) defines.DOUBLE = 1;
  return new THREE.ShaderMaterial({
    defines, vertexColors: !!o.vc, side: o.double ? THREE.DoubleSide : THREE.FrontSide, extensions: { derivatives: true },
    uniforms: Object.assign({}, U, {
      uMap: { value: o.map || null }, uRep: { value: new THREE.Vector2(o.rep ? o.rep[0] : 1, o.rep ? o.rep[1] : 1) },
      uTriS: { value: o.triS || 0.5 }, uColor: { value: o.color instanceof THREE.Color ? o.color : new THREE.Color(o.color !== undefined ? o.color : 0xffffff) },
      uGloss: { value: o.gloss || 20 }, uSpec: { value: o.spec !== undefined ? o.spec : 0.15 }, uBump: { value: o.bump || 0 },
      uTexGain: { value: o.gain || 1 }, uEmis: { value: o.emis || 5 }
    }),
    vertexShader: WORLD_VS, fragmentShader: WORLD_FS
  });
}

/* Textures */
const maxAniso = renderer.capabilities.getMaxAnisotropy();
function fallbackCanvas(kind) {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  g.fillStyle = { wood: '#4a3325', floor: '#8a847a', carpet: '#5a1d18' }[kind] || '#6b6863'; g.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(20,16,12,${Math.random() * 0.12})`; g.fillRect(Math.random() * 128, Math.random() * 128, kind === 'wood' ? 30 : 3, kind === 'wood' ? 1 : 3); }
  return c;
}
function loadTex(url, kind) {
  const t = new THREE.TextureLoader().load(url, undefined, undefined, () => { t.image = fallbackCanvas(kind); t.needsUpdate = true; });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = Math.min(8, maxAniso);
  return t;
}
const TEX = { stone: loadTex('assets/stone.jpg', 'stone'), wood: loadTex('assets/wood.jpg', 'wood'), floor: loadTex('assets/floor.jpg', 'floor'), carpet: loadTex('assets/carpet.jpg', 'carpet') };

/* Materials — texture periods divide the 92 m segment and 4 m floor, so the floating origin never shows a seam */
const MAT = {
  stone: makeMat({ tri: true, map: TEX.stone, triS: 0.5, vc: true, gain: 5.2, bump: 0.012, spec: 0.08, gloss: 24 }),
  floor: makeMat({ tri: true, map: TEX.floor, triS: 0.25, vc: true, gain: 2.3, bump: 0.006, spec: 0.55, gloss: 90 }),
  carpet: makeMat({ tri: true, map: TEX.carpet, triS: 0.5, vc: true, gain: 2.2, bump: 0.02, spec: 0.02, gloss: 8 }),
  wood: makeMat({ tri: true, map: TEX.wood, triS: 1.0, vc: true, gain: 3.2, bump: 0.01, spec: 0.35, gloss: 45 }),
  brass: makeMat({ vc: true, color: new THREE.Color(0.62, 0.4, 0.14), spec: 2.2, gloss: 70 }),
  plain: makeMat({ vc: true, spec: 0.12, gloss: 16, emis: 7 }),
  book: makeMat({ book: true, spec: 0.12, gloss: 18 }),
};

/* ==========================================================================
   Procedural far shelves — the same books, drawn by the GPU from their addresses
   ========================================================================== */
const SHELF_U = Object.assign({}, U, {
  uFloorW: { value: new THREE.Vector4() }, uCaseW: { value: new THREE.Vector4() }, uSide: { value: 0 },
  uNearX: { value: new THREE.Vector2(1e9, -1e9) }, uPal: { value: PALETTE.map(c => new THREE.Vector3(c[0], c[1], c[2])) },
  uAvg: { value: new THREE.Vector3(AVG_BOOK[0], AVG_BOOK[1], AVG_BOOK[2]) }, uWoodT: { value: TEX.wood },
});
const HASH_GLSL = GL2 ? `
uint mixu(uint h){ h ^= h >> 16u; h *= 0x7feb352du; h ^= h >> 15u; h *= 0x846ca68bu; h ^= h >> 16u; return h; }
uint lookH(uint fLo, uint fHi, uint cLo, uint cHi, uint side, uint r, uint p){
  uint h = mixu(fLo ^ 0x51ed270bu); h = mixu(h ^ fHi); h = mixu(h ^ cLo);
  h = mixu(h ^ cHi ^ (side == 1u ? 0xa5a5a5a5u : 0x2545f491u)); h = mixu(h ^ (r * 131u + p * 7919u)); return h; }
void bookInfo(float fRel, float segRel, float sideRel, float jc, float row, float pos, out vec3 col, out float hb){
  uint fLo = uint(uFloorW.x) | (uint(uFloorW.y) << 16u); uint fHi = uint(uFloorW.z) | (uint(uFloorW.w) << 16u);
  int k = int(fRel); uint nlo, nhi;
  if (k >= 0) { uint a = uint(k); nlo = fLo + a; nhi = fHi + (nlo < fLo ? 1u : 0u); } else { uint a = uint(-k); nlo = fLo - a; nhi = fHi - (fLo < a ? 1u : 0u); }
  uint cLo = uint(uCaseW.x) | (uint(uCaseW.y) << 16u); uint cHi = uint(uCaseW.z) | (uint(uCaseW.w) << 16u);
  uint add = uint((segRel + 2.0) * 40.0 + jc); uint clo2 = cLo + add; uint chi2 = cHi + (clo2 < cLo ? 1u : 0u);
  uint side = uint(abs(uSide - sideRel) + 0.5);
  uint h = lookH(nlo, nhi, clo2, chi2, side, uint(row), uint(pos));
  vec3 pc = vec3(0.0); int pi = int(h % 10u);
  for (int i = 0; i < 10; i++) if (i == pi) pc = uPal[i];
  col = pc * (0.78 + float((h >> 8u) & 255u) / 255.0 * 0.4);
  hb = 0.26 + float((h >> 16u) & 255u) / 255.0 * 0.11;
}` : `
void bookInfo(float fRel, float segRel, float sideRel, float jc, float row, float pos, out vec3 col, out float hb){
  float h = fract(sin(dot(vec4(fRel + uFloorW.x, segRel * 40.0 + jc + uCaseW.x, row + sideRel * 7.0, pos), vec4(12.9898, 78.233, 37.719, 4.581))) * 43758.5453);
  int pi = int(h * 10.0); vec3 pc = vec3(0.0); for (int i = 0; i < 10; i++) if (i == pi) pc = uPal[i];
  col = pc * (0.78 + fract(h * 91.0) * 0.4); hb = 0.26 + fract(h * 413.0) * 0.11;
}`;
const SHELF_VS = `
attribute vec3 aInfo; varying vec3 vInfo; varying vec2 vLoc; varying vec3 vW; varying vec3 vN; varying vec3 vT;
void main(){ vec4 p = instanceMatrix * vec4(position, 1.0); vec4 w = modelMatrix * p; vW = w.xyz;
  vN = mat3(modelMatrix) * (mat3(instanceMatrix) * normal); vT = mat3(modelMatrix) * (mat3(instanceMatrix) * vec3(1.0, 0.0, 0.0));
  vLoc = position.xy; vInfo = aInfo; gl_Position = projectionMatrix * viewMatrix * w; }`;
const SHELF_FS = `
uniform vec4 uFloorW; uniform vec4 uCaseW; uniform float uSide; uniform vec2 uNearX; uniform vec3 uPal[10]; uniform vec3 uAvg; uniform sampler2D uWoodT;
varying vec3 vInfo; varying vec2 vLoc; varying vec3 vN; varying vec3 vT;
${GLSL_COMMON}
${HASH_GLSL}
void main(){
  if (vInfo.y == 0.0 && vInfo.z == 0.0 && vW.x > uNearX.x && vW.x < uNearX.y) discard;
  vec3 N = normalize(vN); vec3 T = normalize(vT); gV = normalize(cameraPosition - vW);
  float lx = vLoc.x, ly = vLoc.y;
  float fw = max(fwidth(lx), fwidth(ly));
  float jc = floor(lx / 2.0); float u = lx - jc * 2.0;
  float row = floor((ly - 0.12) / 0.46); float v = ly - 0.12 - row * 0.46;
  vec3 wood = pow(texture2D(uWoodT, vec2(lx * 0.5, ly * 0.5)).rgb, vec3(2.2)) * 2.6;
  vec3 base; float spec = 0.1, gloss = 20.0, ao = 1.0;
  float detail = 1.0 - smoothstep(0.012, 0.045, fw);
  if (ly < 0.12 || ly > 3.34 || u < 0.06 || u > 1.94) {
    base = wood * 1.1; spec = 0.3; gloss = 40.0;
    if (u < 0.06 || u > 1.94) { float e = min(u, 2.0 - u); N = normalize(N + T * (u < 1.0 ? -1.0 : 1.0) * (1.0 - e / 0.06) * 0.5 * detail); }
  } else if (v > 0.43) {
    base = wood * 1.2; spec = 0.3; gloss = 40.0; ao *= mix(0.8, 1.0, smoothstep(0.43, 0.46, v));
  } else {
    float pos = clamp(floor((u - 0.05) / 0.0475), 0.0, 39.0);
    float bu = (u - 0.05) / 0.0475 - pos;
    vec3 bc; float hb; bookInfo(vInfo.y, vInfo.x, vInfo.z, jc, row, pos, bc, hb);
    hb = mix(0.315, hb, detail);
    if (v < hb) {
      float bv = v / hb;
      float band = detail * clamp(smoothstep(0.085, 0.095, bv) - smoothstep(0.115, 0.125, bv) + smoothstep(0.875, 0.885, bv) - smoothstep(0.905, 0.915, bv), 0.0, 1.0);
      base = mix(uAvg, bc, detail) * mix(1.0, 0.78 + 0.22 * sin(bu * 3.14159), detail);
      base = mix(base, vec3(0.42, 0.26, 0.06), band * 0.85); spec = mix(0.1, 1.2, band); gloss = mix(18.0, 70.0, band);
      N = normalize(N + T * (bu - 0.5) * 1.1 * detail);
      ao *= mix(0.6, 1.0, smoothstep(0.0, 0.1, bv));
      ao *= mix(0.5, 1.0, smoothstep(0.0, 0.12, 0.43 - v));
    } else { base = bc * 0.06 + vec3(0.004); ao *= 0.4; }
  }
  float D, Sp; lighting(N, gloss, D, Sp);
  vec3 col = base * (uAmb * ao + uLampCol * D * ao) + uLampCol * Sp * spec * ao;
  vec3 farAlb = uAvg * 0.62 + wood * 0.12;
  col = mix(col, farAlb * (uAmb + uLampCol * D) * 0.85, smoothstep(0.06, 0.2, fw));
  gl_FragColor = vec4(fogIt(safeCol(col), D), 1.0);
}`;
const shelfMat = new THREE.ShaderMaterial({ uniforms: SHELF_U, vertexShader: SHELF_VS, fragmentShader: SHELF_FS, extensions: { derivatives: true } });

/* Procedural balustrade for far railings (real turned balusters near you) */
const RAIL_FS = `
uniform sampler2D uWoodT; varying vec3 vInfo; varying vec2 vLoc; varying vec3 vN; varying vec3 vT;
${GLSL_COMMON}
float prof(float y){
  if (y < 0.1) return 0.045;
  if (y < 0.14) return 0.028;
  if (y > 0.94) return 0.036;
  float t = (y - 0.14) / 0.8;
  return 0.016 + 0.024 * exp(-pow((t - 0.28) / 0.16, 2.0)) + 0.006 * step(0.72, t) * step(t, 0.8);
}
void main(){
  if (vInfo.y == 0.0 && vInfo.z == 0.0 && abs(vInfo.x) <= 1.0) discard;
  float x = vLoc.x, y = vLoc.y;
  float k = floor(x / 0.35); float t = (x - k * 0.35) - 0.175;
  float r = prof(y);
  float fw = fwidth(x);
  float cov = 1.0 - smoothstep(r - fw, r + fw, abs(t));
  if (y < 0.06) cov = 1.0;
  if (cov < 0.02) discard;
  vec3 N = normalize(vN); if (!gl_FrontFacing) N = -N;
  vec3 T = normalize(vT); gV = normalize(cameraPosition - vW);
  float s = clamp(t / max(r, 1e-3), -1.0, 1.0);
  N = normalize(N * sqrt(max(1.0 - s * s, 0.0)) + T * s);
  vec3 base = pow(texture2D(uWoodT, vec2(x * 1.3, y * 0.7)).rgb, vec3(2.2)) * 3.0;
  float D, Sp; lighting(N, 50.0, D, Sp);
  vec3 col = base * (uAmb + uLampCol * D) + uLampCol * Sp * 0.3;
  gl_FragColor = vec4(fogIt(safeCol(col), D), cov);
}`;
const railMat = new THREE.ShaderMaterial({ uniforms: Object.assign({}, U, { uWoodT: { value: TEX.wood } }), vertexShader: SHELF_VS, fragmentShader: RAIL_FS, side: THREE.DoubleSide, extensions: { derivatives: true }, transparent: false, alphaTest: 0.02 });
railMat.alphaToCoverage = true;

/* ==========================================================================
   Geometry: one segment of one floor, merged per material, instanced across the window
   ========================================================================== */
function boxG(x0, y0, z0, x1, y1, z1) { const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0); g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); return g; }
function merge(parts) {
  if (!parts.length) return null;
  let n = 0; const gs = parts.map(p => { const g = p.g.index ? p.g.toNonIndexed() : p.g; n += g.attributes.position.count; return [g, p.c || [1, 1, 1]]; });
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), uv = new Float32Array(n * 2), col = new Float32Array(n * 3); let o = 0;
  for (const [g, c] of gs) {
    const cnt = g.attributes.position.count;
    pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3);
    if (g.attributes.uv) uv.set(g.attributes.uv.array, o * 2);
    for (let i = 0; i < cnt; i++) { col[(o + i) * 3] = c[0]; col[(o + i) * 3 + 1] = c[1]; col[(o + i) * 3 + 2] = c[2]; }
    o += cnt;
  }
  const m = new THREE.BufferGeometry();
  m.setAttribute('position', new THREE.BufferAttribute(pos, 3)); m.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  m.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); m.setAttribute('color', new THREE.BufferAttribute(col, 3));
  m.computeBoundingSphere(); return m;
}
class Parts {
  constructor() { this.m = {}; }
  add(mat, g, c) { (this.m[mat] || (this.m[mat] = [])).push({ g, c }); }
  box(mat, x0, y0, z0, x1, y1, z1, c) { this.add(mat, boxG(x0, y0, z0, x1, y1, z1), c); }
}
const K = {
  stone: [0.95, 0.9, 0.84], stoneD: [0.62, 0.58, 0.54], dark: [0.2, 0.18, 0.17], floorB: [0.5, 0.46, 0.42], floor: [1, 1, 1],
  wood: [1, 1, 1], woodL: [1.0, 0.92, 0.82], brass: [1, 1, 1], globe: [3.2, 2.3, 1.35], screen: [1.4, 1.35, 1.1], linen: [0.62, 0.58, 0.5],
  blanket: [0.22, 0.12, 0.1], blanket2: [0.12, 0.16, 0.2], slot: [0.01, 0.01, 0.01], clockBox: [0.03, 0.03, 0.03]
};
function lathe(pts, seg) { return new THREE.LatheGeometry(pts.map(p => new THREE.Vector2(p[0], p[1])), seg); }
const BALUSTER_PTS = [[0.001, 0], [0.045, 0], [0.045, 0.1], [0.028, 0.12], [0.022, 0.16], [0.034, 0.26], [0.04, 0.36], [0.032, 0.46], [0.018, 0.56], [0.016, 0.72], [0.022, 0.76], [0.016, 0.8], [0.018, 0.92], [0.036, 0.95], [0.036, 1.02], [0.001, 1.02]];
function moduleParts(detail) {
  const p = new Parts();
  // structure: slab, floor surface, carpet runner, chasm fascia
  p.box('stone', 0, -0.3, -3.0, 80, -0.02, 0.0, K.stone);
  p.box('stone', 80, -0.3, -13.2, 92, -0.02, 0.0, K.stone);
  p.box('floor', 0, -0.02, -3.0, 80, 0, 0.0, K.floor);
  p.box('floor', 80, -0.02, -6.3, 92, 0, 0.0, K.floor);
  p.box('floor', 80, -0.02, -13.2, 92, 0, -10.7, K.floor);
  p.box('floor', 80, -0.02, -10.7, 83.8, 0, -6.3, K.floor);
  p.box('floor', 88.2, -0.02, -10.7, 92, 0, -6.3, K.floor);
  if (detail) p.box('carpet', 0, 0, -2.35, 92, 0.008, -0.85, K.floor);
  p.box('stone', 0, -0.5, 0.0, 92, 0.05, 0.28, K.stoneD);
  if (detail) p.box('stone', 0, -0.56, -0.02, 92, -0.48, 0.34, K.stone);
  // shelf wall back, cornice, plinth
  p.box('stone', 0, 0, -3.9, 80, 3.7, -3.4, K.dark);
  p.box('wood', 0, 3.42, -3.12, 80, 3.5, -2.9, K.wood);
  p.box('wood', 0, 3.5, -3.05, 80, 3.62, -2.84, K.wood);
  p.box('stone', 0, 3.62, -3.1, 80, 3.7, -2.8, K.stone);
  // rest area: walls, entrance lintel and jambs
  p.box('stone', 79.8, 0, -13.4, 80.0, 3.7, -2.9, K.stone);
  p.box('stone', 91.8, 0, -13.4, 92.0, 3.7, -2.9, K.stone);
  p.box('stone', 79.8, 0, -13.4, 92.0, 3.7, -13.2, K.stone);
  p.box('stone', 79.7, 3.15, -3.25, 92.1, 3.7, -2.85, K.stone);
  p.box('stone', 79.65, 0, -3.25, 80.25, 3.15, -2.85, K.stone);
  p.box('stone', 91.75, 0, -3.25, 92.35, 3.15, -2.85, K.stone);
  // railing: handrail and base rail (balusters are drawn separately)
  p.box('wood', 0, 1.02, 0.07, 92, 1.1, 0.23, K.woodL);
  p.box('stone', 0, 0.0, 0.08, 92, 0.06, 0.22, K.stoneD);
  if (detail) {
    for (let x = 0; x <= 92; x += 4) p.box('wood', x - 0.06, 0, 0.05, x + 0.06, 1.14, 0.25, K.woodL); // newel posts
    // coffered ceiling beams
    for (let x = 0; x <= 92; x += 4) p.box('stone', x - 0.1, -0.54, -3.0, x + 0.1, -0.3, 0.0, K.stoneD);
    p.box('stone', 0, -0.54, -3.0, 92, -0.3, -2.8, K.stoneD);
    // pendant lamps: chain, brass cap, glass globe, finial
    for (let x = 2; x < 92; x += 4) {
      p.box('brass', x - 0.008, 3.32, -1.508, x + 0.008, 3.7, -1.492, K.brass);
      const cap = lathe([[0.001, 0.0], [0.13, 0.0], [0.1, 0.05], [0.04, 0.1], [0.001, 0.13]], 8); cap.translate(x, 3.2, -1.5); p.add('brass', cap, K.brass);
      const gl = new THREE.SphereGeometry(0.11, 8, 5); gl.translate(x, 3.12, -1.5); p.add('plain', gl, K.globe);
      p.box('brass', x - 0.015, 2.98, -1.515, x + 0.015, 3.02, -1.485, K.brass);
    }
    // rest-area chandeliers
    for (const rx of [82, 90]) {
      p.box('brass', rx - 0.01, 3.1, -9.51, rx + 0.01, 3.7, -9.49, K.brass);
      const cap = lathe([[0.001, 0], [0.3, 0], [0.26, 0.05], [0.08, 0.12], [0.001, 0.14]], 12); cap.translate(rx, 3.12, -9.5); p.add('brass', cap, K.brass);
      for (let i = 0; i < 5; i++) { const a = i / 5 * Math.PI * 2, gg = new THREE.SphereGeometry(0.07, 8, 6); gg.translate(rx + Math.cos(a) * 0.24, 3.08, -9.5 + Math.sin(a) * 0.24); p.add('plain', gg, K.globe); }
    }
    // stair shaft: enclosure with an arched door, stone steps with wooden nosing, column, brass handrail
    p.box('stone', 83.8, 0, -10.7, 88.2, 3.7, -10.5, K.stone); p.box('stone', 83.8, 0, -10.7, 84.0, 3.7, -6.3, K.stone);
    p.box('stone', 88.0, 0, -10.7, 88.2, 3.7, -6.3, K.stone);
    p.box('stone', 83.8, 0, -6.5, 85.35, 3.7, -6.3, K.stone); p.box('stone', 86.65, 0, -6.5, 88.2, 3.7, -6.3, K.stone);
    p.box('stone', 85.35, 2.35, -6.5, 86.65, 3.7, -6.3, K.stone);
    p.box('wood', 85.25, 0, -6.55, 85.4, 2.45, -6.25, K.wood); p.box('wood', 86.6, 0, -6.55, 86.75, 2.45, -6.25, K.wood); p.box('wood', 85.25, 2.35, -6.55, 86.75, 2.5, -6.25, K.wood);
    for (let i = 0; i < 16; i++) {
      const th = TH0 + (i + 0.5) / 16 * Math.PI * 2, h = (i + 0.5) / 16 * H;
      const g = new THREE.BoxGeometry(1.62, 0.1, 0.86); g.translate(0.3 + 0.81, 0, 0); g.rotateY(-th); g.translate(CX, h - 0.06, CZ); p.add('stone', g, K.stone);
      const nose = new THREE.BoxGeometry(1.64, 0.035, 0.06); nose.translate(0.3 + 0.82, 0.0, 0); nose.rotateY(-(th - Math.PI / 16)); nose.translate(CX, h - 0.01, CZ); p.add('wood', nose, K.woodL);
    }
    const col = new THREE.CylinderGeometry(0.3, 0.3, H, 16, 1, true); col.translate(CX, H / 2, CZ); p.add('stone', col, K.stone);
    const hel = []; for (let i = 0; i <= 48; i++) { const a = TH0 + i / 48 * Math.PI * 2; hel.push(new THREE.Vector3(CX + Math.cos(a) * 1.9, i / 48 * H + 0.92, CZ + Math.sin(a) * 1.9)); }
    p.add('brass', new THREE.TubeGeometry(new THREE.CatmullRomCurve3(hel), 48, 0.028, 6, false), K.brass);
    const bulb = new THREE.SphereGeometry(0.07, 8, 6); bulb.translate(CX - 0.4, 2.6, CZ); p.add('plain', bulb, K.globe);
    // beds: frames, mattresses, blankets, pillows
    [80.25, 81.55, 82.85].forEach((bx, i) => {
      p.box('wood', bx, 0, -13.05, bx + 0.9, 0.32, -10.95, K.wood);
      p.box('wood', bx - 0.02, 0, -13.1, bx + 0.92, 0.85, -12.98, K.wood);
      p.box('plain', bx + 0.05, 0.32, -12.95, bx + 0.85, 0.46, -11.0, K.linen);
      p.box('plain', bx + 0.04, 0.46, -12.2, bx + 0.86, 0.5, -10.98, i === 1 ? K.blanket2 : K.blanket);
      p.box('plain', bx + 0.14, 0.46, -12.9, bx + 0.76, 0.56, -12.5, K.linen);
    });
    // kiosk: wooden cabinet, brass trim, glowing screen, hatch
    p.box('wood', 91.25, 0, -9.9, 91.8, 1.45, -8.1, K.wood);
    p.box('brass', 91.2, 1.45, -9.95, 91.82, 1.52, -8.05, K.brass);
    p.box('brass', 91.22, 0.72, -9.72, 91.25, 1.3, -8.28, K.brass);
    p.box('plain', 91.2, 0.8, -9.62, 91.23, 1.22, -8.38, K.screen);
    p.box('plain', 91.2, 0.42, -9.3, 91.24, 0.6, -8.7, K.slot);
    // table and benches
    p.box('wood', 88.9, 0.72, -5.45, 91.1, 0.78, -4.35, K.wood);
    for (const [lx, lz] of [[89.0, -5.35], [91.0, -5.35], [89.0, -4.45], [91.0, -4.45]]) p.box('wood', lx - 0.04, 0, lz - 0.04, lx + 0.04, 0.72, lz + 0.04, K.wood);
    p.box('wood', 88.9, 0.42, -6.05, 91.1, 0.47, -5.75, K.wood); p.box('wood', 88.9, 0.42, -4.05, 91.1, 0.47, -3.75, K.wood);
    for (const bz of [-5.9, -3.9]) for (const lx of [89.0, 91.0]) p.box('wood', lx - 0.03, 0, bz - 0.03, lx + 0.03, 0.42, bz + 0.03, K.wood);
    // bathroom door on the side wall
    p.box('wood', 80.0, 0, -9.45, 80.06, 2.2, -7.55, K.wood); p.box('wood', 80.0, 2.2, -9.55, 80.1, 2.3, -7.45, K.woodL);
    p.box('brass', 80.06, 1.0, -7.8, 80.1, 1.06, -7.7, K.brass);
    // the slot under the sign
    p.box('brass', 89.6, 0.95, -13.2, 90.4, 1.15, -13.1, K.brass); p.box('plain', 89.7, 1.03, -13.1, 90.3, 1.06, -13.09, K.slot);
  }
  const out = {}; for (const k in p.m) out[k] = merge(p.m[k]); return out;
}
function nearWindowParts() {
  const p = new Parts();
  for (let k = -1; k <= 1; k++) {
    const o = k * P;
    p.box('wood', o, 0, -3.4, o + 80, RY, -2.99, K.wood);
    for (let j = 1; j <= ROWS; j++) { const yt = RY + j * RH; p.box('wood', o, yt - 0.03, -3.4, o + 80, j === ROWS ? 3.42 : yt, -2.985, K.wood); }
    p.box('stone', o, RY, -3.42, o + 80, 3.4, -3.39, K.dark);
    for (let i = 0; i <= CASES; i++) {
      const x = o + i * CW;
      p.box('wood', x - 0.06, 0.12, -3.4, x + 0.06, 3.3, -2.94, K.woodL);
      p.box('wood', x - 0.085, 0, -3.4, x + 0.085, 0.22, -2.92, K.woodL);
      p.box('wood', x - 0.085, 3.28, -3.4, x + 0.085, 3.42, -2.92, K.woodL);
    }
  }
  const out = {}; for (const k in p.m) out[k] = merge(p.m[k]); return out;
}

const MODS = { near: [], far: [], all: [] };
function modMatrix(s, f, side) {
  const m = new THREE.Matrix4();
  if (side === 0) m.makeTranslation(s * P, f * H, 0);
  else { m.makeRotationY(Math.PI); m.setPosition(s * P + P, f * H, CHASM); }
  return m;
}
for (let f = -FWIN; f <= FWIN; f++) for (let s = -2; s <= 2; s++) for (let side = 0; side < 2; side++) {
  const e = { m: modMatrix(s, f, side), s, f, side };
  MODS.all.push(e); (Math.abs(f) <= 1 ? MODS.near : MODS.far).push(e);
}
function instanced(geo, mat, list) {
  const im = new THREE.InstancedMesh(geo, mat, list.length);
  list.forEach((e, i) => im.setMatrixAt(i, e.m || e));
  im.frustumCulled = false; im.instanceMatrix.needsUpdate = true; scene.add(im); return im;
}
{
  const gN = moduleParts(true), gF = moduleParts(false);
  for (const k in gN) if (gN[k]) instanced(gN[k], MAT[k], MODS.near);
  for (const k in gF) if (gF[k]) instanced(gF[k], MAT[k], MODS.far);
  const gW = nearWindowParts();
  for (const k in gW) { const m = new THREE.Mesh(gW[k], MAT[k]); m.frustumCulled = false; scene.add(m); }
  // procedural shelf faces and balustrades on every module
  const info = new Float32Array(MODS.all.length * 3); MODS.all.forEach((e, i) => { info[i * 3] = e.s; info[i * 3 + 1] = e.f; info[i * 3 + 2] = e.side; });
  const sg = new THREE.PlaneGeometry(80, 3.42, 1, 1); sg.translate(40, 1.71, 0); sg.translate(0, 0, -2.996); sg.setAttribute('aInfo', new THREE.InstancedBufferAttribute(info, 3));
  instanced(sg, shelfMat, MODS.all);
  const rg = new THREE.PlaneGeometry(92, 1.02, 1, 1); rg.translate(46, 0.51, 0.15); rg.setAttribute('aInfo', new THREE.InstancedBufferAttribute(info.slice(), 3));
  instanced(rg, railMat, MODS.all);
  // real turned balusters on your own gallery, near you
  const bg = lathe(BALUSTER_PTS, 7); const bm = [];
  for (let k = -1; k <= 1; k++) for (let x = 0.175; x < 92; x += 0.35) bm.push(new THREE.Matrix4().makeTranslation(k * P + x, 0, 0.15));
  instanced(bg, MAT.wood, bm);
}

/* Lamp glows for far floors (bloom turns them into halos) */
{
  const pts = [];
  for (const e of MODS.far) { for (let x = 2; x < 92; x += 4) { const v = new THREE.Vector3(x, 3.12, -1.5).applyMatrix4(e.m); pts.push(v.x, v.y, v.z); } }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  const gc = document.createElement('canvas'); gc.width = gc.height = 64; const x = gc.getContext('2d'), gr = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, 64, 64);
  var GLOW = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.55, map: new THREE.CanvasTexture(gc), color: new THREE.Color(3.2, 2.0, 1.0), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: true }));
  GLOW.frustumCulled = false; scene.add(GLOW);
}

/* Light shafts under the lamps near you */
const coneMat = new THREE.ShaderMaterial({
  uniforms: Object.assign({}, U), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `varying vec3 vW; varying vec3 vN; varying float vT; varying vec3 vApex;
    void main(){ vec4 p = instanceMatrix * vec4(position, 1.0); vec4 w = modelMatrix * p; vW = w.xyz; vN = mat3(modelMatrix) * (mat3(instanceMatrix) * normal);
      vT = clamp((position.y - 0.07) / 3.05, 0.0, 1.0); vApex = (modelMatrix * instanceMatrix * vec4(0.0, 3.12, 0.0, 1.0)).xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `${GLSL_COMMON} varying vec3 vN; varying float vT; varying vec3 vApex;
    void main(){ vec3 V = normalize(cameraPosition - vW); float fr = abs(dot(normalize(vN), V));
      float a = pow(vT, 1.8) * smoothstep(0.05, 0.75, fr) * 0.045 * uLamp;
      a *= lampScale(vec2(floor(vApex.x / 4.0) + (vApex.z > 8.0 ? 313.0 : 0.0), floor((vApex.y + 0.02) / 4.0)));
      float d = length(vW - cameraPosition); a *= exp(-pow(d * uFogD, 2.0)) * smoothstep(0.3, 1.5, d);
      gl_FragColor = vec4(uLampCol * a, 1.0); }`
});
{
  const cg = new THREE.ConeGeometry(1.55, 3.05, 20, 1, true); cg.translate(0, 3.12 - 1.525, 0);
  const ms = [];
  for (let f = -1; f <= 1; f++) for (let s = -1; s <= 1; s++) for (let x = 2; x < 92; x += 4) {
    ms.push(new THREE.Matrix4().makeTranslation(s * P + x, f * H, -1.5));
    ms.push(new THREE.Matrix4().makeTranslation(s * P + (P - x), f * H, CHASM + 1.5));
  }
  const cm = instanced(cg, coneMat, ms); cm.renderOrder = 2;
}

/* Dust drifting in the lamplight */
const dustMat = new THREE.ShaderMaterial({
  uniforms: Object.assign({}, U, { uSize: { value: 1 } }), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  vertexShader: `uniform float uTime; uniform float uLamp; uniform float uSize; varying float vA;
    void main(){ vec3 c = cameraPosition; vec3 q = fract(position + vec3(0.013, -0.004, 0.009) * uTime + 0.03 * sin(uTime * 0.3 + position.zxy * 40.0) - c / 14.0);
      vec3 w = c + (q - 0.5) * 14.0; float fl = floor((w.y + 0.02) / 4.0); float lx = floor(w.x / 4.0) * 4.0 + 2.0;
      vec3 d = w - vec3(lx, fl * 4.0 + 3.1, -1.5); float d2 = dot(d, d);
      vA = uLamp * (0.08 + 1.4 / (1.0 + d2 * 0.9)) * smoothstep(7.0, 3.0, length(w - c));
      vec4 mv = viewMatrix * vec4(w, 1.0); gl_PointSize = uSize * 5.0 / max(-mv.z, 0.2); gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform vec3 uLampCol; varying float vA; void main(){ vec2 p = gl_PointCoord - 0.5; float a = smoothstep(0.5, 0.0, length(p)) * vA; gl_FragColor = vec4(uLampCol * a * 0.9, 1.0); }`
});
{
  const n = 700, a = new Float32Array(n * 3); for (let i = 0; i < n * 3; i++) a[i] = Math.random();
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(a, 3));
  var DUST = new THREE.Points(g, dustMat); DUST.frustumCulled = false; scene.add(DUST);
}

/* Streaks while falling */
const STREAK_N = 160;
const streakGeo = new THREE.BufferGeometry(); streakGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(STREAK_N * 6), 3));
const streakMat = new THREE.LineBasicMaterial({ color: new THREE.Color(1.6, 1.0, 0.55), transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
const STREAKS = new THREE.LineSegments(streakGeo, streakMat); STREAKS.frustumCulled = false; scene.add(STREAKS);
const streakSeed = Array.from({ length: STREAK_N }, () => [Math.random(), Math.random(), Math.random()]);
function updateStreaks(speed) {
  streakMat.opacity = clamp((speed - 8) / 40, 0, 0.55);
  STREAKS.visible = streakMat.opacity > 0.01;
  if (!STREAKS.visible) return;
  const a = streakGeo.attributes.position.array, c = camera.position, len = speed * 0.05, t = performance.now() / 1000;
  for (let i = 0; i < STREAK_N; i++) {
    const s = streakSeed[i]; const x = c.x + (s[0] - 0.5) * 30, z = clamp(c.z + (s[2] - 0.5) * 20, -1, 17);
    const y = c.y + (mod(s[1] * 60 + t * speed, 60) - 30);
    a[i * 6] = x; a[i * 6 + 1] = y; a[i * 6 + 2] = z; a[i * 6 + 3] = x; a[i * 6 + 4] = y - len; a[i * 6 + 5] = z;
  }
  streakGeo.attributes.position.needsUpdate = true;
}

/* Digital clocks on the cornices — "readouts mark the time" */
const clockCanvas = document.createElement('canvas'); clockCanvas.width = 256; clockCanvas.height = 96;
const clockTex = new THREE.CanvasTexture(clockCanvas); clockTex.minFilter = THREE.LinearFilter;
const SEG7 = { 0: 'abcdef', 1: 'bc', 2: 'abdeg', 3: 'abcdg', 4: 'bcfg', 5: 'acdfg', 6: 'acdefg', 7: 'abc', 8: 'abcdefg', 9: 'abcdfg' };
function drawClock(t) {
  const g = clockCanvas.getContext('2d'); g.fillStyle = '#050303'; g.fillRect(0, 0, 256, 96);
  const s = clock(t).replace(':', '');
  const dx = [22, 76, 142, 196], w = 38, hh = 64, y0 = 16, th = 7;
  const segs = (d, x) => {
    const on = SEG7[d];
    const r = { a: [x + 4, y0, w - 8, th], b: [x + w - th, y0 + 4, th, hh / 2 - 6], c: [x + w - th, y0 + hh / 2 + 2, th, hh / 2 - 6], d: [x + 4, y0 + hh - th, w - 8, th], e: [x, y0 + hh / 2 + 2, th, hh / 2 - 6], f: [x, y0 + 4, th, hh / 2 - 6], g: [x + 4, y0 + hh / 2 - th / 2, w - 8, th] };
    for (const k in r) { g.fillStyle = on.includes(k) ? '#ff6a2a' : 'rgba(255,90,40,.07)'; g.fillRect(...r[k]); }
  };
  for (let i = 0; i < 4; i++) segs(s[i], dx[i]);
  g.fillStyle = '#ff6a2a'; g.fillRect(124, 36, 8, 8); g.fillRect(124, 60, 8, 8);
  clockTex.needsUpdate = true;
}
const clockMat = new THREE.ShaderMaterial({
  uniforms: Object.assign({}, U, { uTex: { value: clockTex } }),
  vertexShader: `varying vec3 vW; varying vec2 vUv; void main(){ vec4 w = modelMatrix * instanceMatrix * vec4(position, 1.0); vW = w.xyz; vUv = uv; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `${GLSL_COMMON} uniform sampler2D uTex; varying vec2 vUv; void main(){ vec3 c = pow(texture2D(uTex, vUv).rgb, vec3(2.2)) * 7.0; gl_FragColor = vec4(fogIt(c, 0.0), 1.0); }`
});
{
  const pg = new THREE.PlaneGeometry(0.42, 0.16); pg.translate(0, 3.56, -2.83);
  const bg = boxG(-0.24, 3.47, -2.86, 0.24, 3.65, -2.82);
  const ms = [];
  for (const e of MODS.near) for (const x of [10, 30, 50, 70]) ms.push(new THREE.Matrix4().makeTranslation(x, 0, 0).premultiply(e.m));
  instanced(pg, clockMat, ms);
  instanced(merge([{ g: bg, c: K.clockBox }]), MAT.plain, ms);
  drawClock(8);
}

/* The rules, engraved on a brass plaque in every rest area */
const signCanvas = document.createElement('canvas'); signCanvas.width = 768; signCanvas.height = 512;
function drawSign() {
  const g = signCanvas.getContext('2d'), gr = g.createLinearGradient(0, 0, 768, 512);
  gr.addColorStop(0, '#8a6a30'); gr.addColorStop(0.5, '#b08a44'); gr.addColorStop(1, '#6e5224'); g.fillStyle = gr; g.fillRect(0, 0, 768, 512);
  g.strokeStyle = 'rgba(40,26,8,.8)'; g.lineWidth = 10; g.strokeRect(18, 18, 732, 476);
  g.fillStyle = '#2a1a08'; g.textAlign = 'center';
  g.font = '600 44px "IM Fell English SC", Georgia, serif'; g.fillText('Notice', 384, 92);
  g.font = '34px "IM Fell English", Georgia, serif';
  const lines = ['When you wish to leave, find the book', 'that tells your earthly life without', 'a single error, and post it through', 'the slot below.', '', 'The killed are restored the following day.', 'Kindly avoid dying where possible.'];
  lines.forEach((l, i) => g.fillText(l, 384, 160 + i * 44));
  signTex.needsUpdate = true;
}
const signTex = new THREE.CanvasTexture(signCanvas);
{
  const pg = new THREE.PlaneGeometry(2.4, 1.6); pg.translate(90.0, 1.9, -13.18);
  const m = makeMat({ map: signTex, gain: 2.2, spec: 1.2, gloss: 50 });
  instanced(pg, m, MODS.near.map(e => e.m));
  drawSign(); if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawSign);
}

/* ==========================================================================
   The near books: a sliding window of 25 bookcases around you, 7,000 real books
   ========================================================================== */
const WIN = 25, WIN_R = 12, NBOOK = WIN * ROWS * PER;
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
const nearBookGeo = bookGeometry(false);
nearBookGeo.setAttribute('aStyle', new THREE.InstancedBufferAttribute(new Float32Array(NBOOK * 3), 3));
const BOOKS = new THREE.InstancedMesh(nearBookGeo, MAT.book, NBOOK);
BOOKS.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(NBOOK * 3), 3);
BOOKS.frustumCulled = false; scene.add(BOOKS);
const WINDOW = { anchor: 0, floor: null, side: null, cases: new Array(WIN).fill(null), center: null };
function caseX(c, anchor) { const sg = Math.floor(c / CASES), j = mod(c, CASES); return (sg - anchor) * P + j * CW; }
function writeCase(c) {
  const slot = mod(c, WIN), f = S.floor, side = S.side, has = overFloors.has(side + ':' + f);
  const M = BOOKS.instanceMatrix.array, Cc = BOOKS.instanceColor.array, St = nearBookGeo.attributes.aStyle.array;
  const x0 = caseX(c, WINDOW.anchor);
  for (let r = 0; r < ROWS; r++) for (let p = 0; p < PER; p++) {
    const idx = (slot * ROWS + r) * PER + p, o = idx * 16;
    const home = { s: side, f, c, r, p }, id = has ? slotContent(home) : home;
    if (!id) { for (let j = 0; j < 16; j++) M[o + j] = 0; continue; }
    const L = bookLook(id);
    M[o] = BT * 0.93; M[o + 1] = 0; M[o + 2] = 0; M[o + 3] = 0; M[o + 4] = 0; M[o + 5] = L.h; M[o + 6] = 0; M[o + 7] = 0;
    M[o + 8] = 0; M[o + 9] = 0; M[o + 10] = L.d; M[o + 11] = 0;
    M[o + 12] = x0 + 0.05 + p * BT + BT / 2; M[o + 13] = RY + r * RH + L.h / 2; M[o + 14] = SHELF_Z - 0.006 - L.d / 2 + L.out; M[o + 15] = 1;
    Cc[idx * 3] = L.col[0]; Cc[idx * 3 + 1] = L.col[1]; Cc[idx * 3 + 2] = L.col[2];
    St[idx * 3] = L.band; St[idx * 3 + 1] = L.label; St[idx * 3 + 2] = L.wear;
  }
  WINDOW.cases[slot] = c;
}
function playerCase() { return S.seg * CASES + clamp(Math.floor(S.lx / CW), 0, CASES - 1) + (S.lx >= RA0 ? 0.5 : 0); }
function updateWindow(force) {
  const center = Math.round(playerCase());
  if (force || WINDOW.floor !== S.floor || WINDOW.side !== S.side || Math.abs(WINDOW.anchor - S.seg) > 40) {
    WINDOW.anchor = S.seg; WINDOW.floor = S.floor; WINDOW.side = S.side; WINDOW.cases.fill(null); WINDOW.center = null;
  }
  if (WINDOW.center === center && !force) { BOOKS.position.x = (WINDOW.anchor - S.seg) * P; return; }
  WINDOW.center = center;
  let dirty = false;
  for (let c = center - WIN_R; c <= center + WIN_R; c++) if (WINDOW.cases[mod(c, WIN)] !== c) { writeCase(c); dirty = true; }
  if (dirty) { BOOKS.instanceMatrix.needsUpdate = true; BOOKS.instanceColor.needsUpdate = true; nearBookGeo.attributes.aStyle.needsUpdate = true; }
  BOOKS.position.x = (WINDOW.anchor - S.seg) * P;
  const x0 = caseX(center - WIN_R, S.seg) - 0.02, x1 = caseX(center + WIN_R, S.seg) + CW + 0.02;
  SHELF_U.uNearX.value.set(x0, x1);
}
function refreshSlot(id) {
  if (id.f !== S.floor || id.s !== S.side) return;
  const slot = mod(id.c, WIN); if (WINDOW.cases[slot] !== id.c) return;
  writeCase(id.c); BOOKS.instanceMatrix.needsUpdate = true; BOOKS.instanceColor.needsUpdate = true; nearBookGeo.attributes.aStyle.needsUpdate = true;
}
function words(n) { const lo = lo32(n), hi = hi32(n); return [lo & 0xffff, lo >>> 16, hi & 0xffff, hi >>> 16]; }
function updateWorldUniforms(t) {
  SHELF_U.uFloorW.value.set(...words(S.floor));
  SHELF_U.uCaseW.value.set(...words((S.seg - 2) * CASES));
  SHELF_U.uSide.value = S.side;
  U.uCellOff.value.set(mod(S.seg * 23, 9973), mod(S.floor, 9973));
  U.uTime.value = t;
}

/* A book in your hands, and books on floors */
const heldGeo = bookGeometry(true);
const heldMat = makeMat({ book: true, spec: 0.12, gloss: 18 });
const HELD = new THREE.Mesh(heldGeo, heldMat); HELD.visible = false; HELD.frustumCulled = false; camera.add(HELD);
function styleGeo(g, L) { const a = g.attributes.aStyle.array; for (let i = 0; i < a.length; i += 3) { a[i] = L.band; a[i + 1] = L.label; a[i + 2] = L.wear; } g.attributes.aStyle.needsUpdate = true; }
function showHeld(id) {
  if (!id) { HELD.visible = false; return; }
  const L = bookLook(id); styleGeo(heldGeo, L);
  heldMat.uniforms.uColor.value.setRGB(L.col[0], L.col[1], L.col[2]);
  HELD.scale.set(0.05, L.h, L.d); HELD.position.set(0.27, -0.26, -0.5); HELD.rotation.set(0.25, -0.55, 0.12); HELD.visible = true;
}
const groundPool = [];
for (let i = 0; i < 30; i++) { const g = bookGeometry(true), m = new THREE.Mesh(g, makeMat({ book: true, spec: 0.12, gloss: 18 })); m.visible = false; m.frustumCulled = false; scene.add(m); groundPool.push(m); }
function updateGroundBooks() {
  let n = 0;
  for (const gb of S.ground) {
    if (n >= groundPool.length) break;
    const df = gb.floor - S.floor, ds = gb.seg - S.seg;
    if (gb.side !== S.side || Math.abs(df) > 6 || Math.abs(ds) > 2) { gb._m = null; continue; }
    const m = groundPool[n++], id = parseKey(gb.id), L = bookLook(id);
    styleGeo(m.geometry, L); m.material.uniforms.uColor.value.setRGB(L.col[0], L.col[1], L.col[2]);
    m.visible = true; m.scale.set(BT, L.h, L.d); m.position.set(ds * P + gb.lx, df * H + gb.ly + BT / 2, gb.z); m.rotation.set(0, gb.yaw, Math.PI / 2); gb._m = m;
  }
  for (let i = n; i < groundPool.length; i++) groundPool[i].visible = false;
}
/* A thrown book, tumbling into the chasm */
const THROWN = [];
function throwBookVisual(id, x, y, z) {
  const g = bookGeometry(true), m = new THREE.Mesh(g, makeMat({ book: true })), L = bookLook(id);
  styleGeo(g, L); m.material.uniforms.uColor.value.setRGB(L.col[0], L.col[1], L.col[2]); m.scale.set(BT, L.h, L.d);
  m.position.set(x, y, z); m.frustumCulled = false; scene.add(m);
  THROWN.push({ m, vy: 1.5, vz: 2.2, spin: new THREE.Vector3(Math.random() * 6, Math.random() * 6, Math.random() * 6), t: 0 });
}
function updateThrown(dt) {
  for (let i = THROWN.length - 1; i >= 0; i--) {
    const b = THROWN[i]; b.t += dt; b.vy -= 9.8 * dt; b.m.position.y += b.vy * dt; b.m.position.z += b.vz * dt; b.vz *= Math.pow(0.5, dt);
    b.m.rotation.x += b.spin.x * dt; b.m.rotation.y += b.spin.y * dt; b.m.rotation.z += b.spin.z * dt;
    if (b.t > 6) { scene.remove(b.m); b.m.geometry.dispose(); THROWN.splice(i, 1); }
  }
}
