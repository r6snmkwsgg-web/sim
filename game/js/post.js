'use strict';
/* ==========================================================================
   Renderer: HDR scene (4x MSAA, 24-bit depth) → water → ambient occlusion
   → bloom → filmic tone map, grade, grain
   ========================================================================== */
const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: 'high-performance', stencil: false });
renderer.outputEncoding = THREE.LinearEncoding;
renderer.toneMapping = THREE.NoToneMapping;
renderer.autoClear = false;
renderer.setSize(innerWidth, innerHeight);
document.querySelector('#game').appendChild(renderer.domElement);
const GL2 = renderer.capabilities.isWebGL2;
const HALF = GL2 || renderer.extensions.has('OES_texture_half_float');
renderer.setClearColor(0x000000, 1);
const scene = new THREE.Scene();          // opaque world
const waterScene = new THREE.Scene();     // drawn second, reading the opaque colour and depth
const camera = new THREE.PerspectiveCamera(72, innerWidth / innerHeight, 0.04, 420);
camera.rotation.order = 'YXZ';
scene.add(camera);
const gfxSettings = () => (typeof S !== 'undefined' && S && S.settings) ? S.settings : { q: 1, gfx: 2 };

let AQ = 1; // automatic resolution scale, lowered if frames run long
let RT = null, BD = [], BU = [], RW = 1, RHh = 1, AOA = null, AOB = null;
const LUM = new THREE.WebGLRenderTarget(48, 27, rtOpts(false)), EXA = new THREE.WebGLRenderTarget(1, 1, rtOpts(false)), EXB = new THREE.WebGLRenderTarget(1, 1, rtOpts(false));
LUM.texture.minFilter = LUM.texture.magFilter = THREE.NearestFilter;
let expoPing = 0, expoReset = true;
function rtOpts(depth) { return { type: HALF ? THREE.HalfFloatType : THREE.UnsignedByteType, format: THREE.RGBAFormat, depthBuffer: depth, stencilBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter }; }
function makeTargets() {
  const pr = Math.min(window.devicePixelRatio || 1, 1.5) * (gfxSettings().q || 1) * AQ;
  const w = Math.max(2, Math.floor(innerWidth * pr)), h = Math.max(2, Math.floor(innerHeight * pr));
  if (RT && RW === w && RHh === h) return;
  RW = w; RHh = h;
  [RT, ...BD, ...BU, AOA, AOB].forEach(t => t && t.dispose());
  if (GL2 && THREE.WebGLMultisampleRenderTarget) { RT = new THREE.WebGLMultisampleRenderTarget(w, h, rtOpts(true)); RT.samples = 4; }
  else RT = new THREE.WebGLRenderTarget(w, h, rtOpts(true));
  if (GL2) { RT.depthTexture = new THREE.DepthTexture(w, h, THREE.UnsignedIntType); RT.depthTexture.format = THREE.DepthFormat; }
  const hw = Math.max(1, w >> 1), hh = Math.max(1, h >> 1);
  AOA = new THREE.WebGLRenderTarget(hw, hh, rtOpts(false)); AOB = new THREE.WebGLRenderTarget(hw, hh, rtOpts(false));
  BD = []; BU = [];
  let bw = w >> 1, bh = h >> 1;
  for (let i = 0; i < 6; i++) { BD.push(new THREE.WebGLRenderTarget(Math.max(1, bw), Math.max(1, bh), rtOpts(false))); BU.push(new THREE.WebGLRenderTarget(Math.max(1, bw), Math.max(1, bh), rtOpts(false))); bw >>= 1; bh >>= 1; }
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

const VPOS_GLSL = `
uniform sampler2D tDepth; uniform mat4 uProjInv; uniform mat4 uProj; uniform vec2 uTexel;
vec3 vpos(vec2 uv){ float d = texture2D(tDepth, uv).x; vec4 p = uProjInv * vec4(uv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0); return p.xyz / p.w; }
vec3 vnorm(vec2 uv, vec3 P){
  vec3 px = vpos(uv + vec2(uTexel.x, 0.0)), nx = vpos(uv - vec2(uTexel.x, 0.0));
  vec3 py = vpos(uv + vec2(0.0, uTexel.y)), ny = vpos(uv - vec2(0.0, uTexel.y));
  vec3 dx = abs(px.z - P.z) < abs(nx.z - P.z) ? px - P : P - nx;
  vec3 dy = abs(py.z - P.z) < abs(ny.z - P.z) ? py - P : P - ny;
  return normalize(cross(dx, dy));
}
float hash12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }`;

const PM = {
  lum: passMat(`uniform sampler2D tSrc; varying vec2 vUv;
    void main(){ float s = 0.0, m = 0.0;
      for (int y = 0; y < 4; y++) for (int x = 0; x < 4; x++) {
        vec2 uv = vUv + (vec2(float(x), float(y)) - 1.5) / vec2(48.0 * 4.0, 27.0 * 4.0);
        vec3 c = texture2D(tSrc, uv).rgb;
        float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
        s += log(max(l, 1e-4)); m += min(l, 12.0);
      }
      // weight the middle of the view more than the edges
      vec2 d = vUv - 0.5; float w = 1.0 - 0.6 * dot(d, d) * 2.0;
      gl_FragColor = vec4(s / 16.0 * w, w, m / 16.0 * w, 1.0); }`, { tSrc: { value: null } }),
  adapt: passMat(`uniform sampler2D tLum; uniform sampler2D tPrev; uniform float uK; uniform float uKey; uniform float uLo; uniform float uHi; varying vec2 vUv;
    void main(){ float s = 0.0, w = 0.0, m = 0.0;
      for (int y = 0; y < 27; y++) for (int x = 0; x < 48; x++) { vec4 t = texture2D(tLum, (vec2(float(x), float(y)) + 0.5) / vec2(48.0, 27.0)); s += t.x; w += t.y; m += t.z; }
      // meter between the log-average and the plain average, so bright white rooms stay white but don't blow out
      float avg = exp(0.35 * (s / max(w, 1e-4)) + 0.65 * log(max(m / max(w, 1e-4), 1e-4)));
      float target = clamp(uKey / max(avg, 1e-4), uLo, uHi);
      float prev = texture2D(tPrev, vec2(0.5)).r;
      float e = uK >= 1.0 ? target : exp(mix(log(max(prev, 1e-4)), log(target), uK));
      gl_FragColor = vec4(e, avg, 0.0, 1.0); }`, { tLum: { value: null }, tPrev: { value: null }, uK: { value: 1 }, uKey: { value: 0.22 }, uLo: { value: 0.05 }, uHi: { value: 6 } }),
  pre: passMat(`uniform sampler2D tSrc; uniform vec2 uTexel; uniform float uThresh; uniform float uExpo; uniform sampler2D tExpo; varying vec2 vUv;
    void main(){ vec3 c = texture2D(tSrc, vUv).rgb * 0.5;
      c += (texture2D(tSrc, vUv + uTexel * vec2(-1.0, -1.0)).rgb + texture2D(tSrc, vUv + uTexel * vec2(1.0, -1.0)).rgb + texture2D(tSrc, vUv + uTexel * vec2(-1.0, 1.0)).rgb + texture2D(tSrc, vUv + uTexel * vec2(1.0, 1.0)).rgb) * 0.125;
      #if __VERSION__ >= 300
        if (any(isnan(c)) || any(isinf(c))) c = vec3(0.0);
      #endif
      c = clamp(c, 0.0, 60.0) * uExpo * texture2D(tExpo, vec2(0.5)).r;
      float br = max(c.r, max(c.g, c.b)); float soft = clamp(br - uThresh + 0.5, 0.0, 1.0); soft = soft * soft / 4.0;
      float k = max(soft, br - uThresh) / max(br, 1e-4);
      gl_FragColor = vec4(c * k, 1.0); }`, { tSrc: { value: null }, uTexel: { value: new THREE.Vector2() }, uThresh: { value: 2.2 }, uExpo: { value: 1 }, tExpo: { value: null } }),
  down: passMat(`uniform sampler2D tSrc; uniform vec2 uTexel; varying vec2 vUv;
    void main(){ vec2 o = uTexel; vec3 s = texture2D(tSrc, vUv).rgb * 4.0;
      s += texture2D(tSrc, vUv - o).rgb + texture2D(tSrc, vUv + o).rgb + texture2D(tSrc, vUv + vec2(o.x, -o.y)).rgb + texture2D(tSrc, vUv - vec2(o.x, -o.y)).rgb;
      gl_FragColor = vec4(s / 8.0, 1.0); }`, { tSrc: { value: null }, uTexel: { value: new THREE.Vector2() } }),
  up: passMat(`uniform sampler2D tSrc; uniform sampler2D tAdd; uniform vec2 uTexel; uniform float uAdd; varying vec2 vUv;
    void main(){ vec2 o = uTexel; vec3 s = vec3(0.0);
      s += texture2D(tSrc, vUv + vec2(-o.x * 2.0, 0.0)).rgb + texture2D(tSrc, vUv + vec2(o.x * 2.0, 0.0)).rgb + texture2D(tSrc, vUv + vec2(0.0, o.y * 2.0)).rgb + texture2D(tSrc, vUv + vec2(0.0, -o.y * 2.0)).rgb;
      s += (texture2D(tSrc, vUv + vec2(-o.x, o.y)).rgb + texture2D(tSrc, vUv + vec2(o.x, o.y)).rgb + texture2D(tSrc, vUv + vec2(o.x, -o.y)).rgb + texture2D(tSrc, vUv + vec2(-o.x, -o.y)).rgb) * 2.0;
      gl_FragColor = vec4(s / 12.0 + texture2D(tAdd, vUv).rgb * uAdd, 1.0); }`, { tSrc: { value: null }, tAdd: { value: null }, uTexel: { value: new THREE.Vector2() }, uAdd: { value: 1 } }),
  ao: passMat(`varying vec2 vUv; ${VPOS_GLSL}
    void main(){
      float d = texture2D(tDepth, vUv).x; vec3 P = vpos(vUv); float ao = 1.0;
      if (d < 1.0 && P.z > -40.0) {
        vec3 N = vnorm(vUv, P);
        float rnd = hash12(floor(gl_FragCoord.xy)) * 6.2831853;
        vec3 rv = vec3(cos(rnd), sin(rnd), 0.37); vec3 T = normalize(rv - N * dot(rv, N)); vec3 B = cross(N, T);
        float radius = mix(0.28, 0.8, clamp(-P.z / 22.0, 0.0, 1.0)), occ = 0.0;
        for (int i = 0; i < 12; i++) {
          float fi = float(i), z = (fi + 0.5) / 12.0, r = sqrt(1.0 - z * z), a = fi * 2.3999632 + rnd;
          vec3 k = vec3(cos(a) * r, sin(a) * r, z) * mix(0.2, 1.0, (fi + 1.0) / 12.0);
          vec3 Sx = P + (T * k.x + B * k.y + N * k.z) * radius;
          vec4 c = uProj * vec4(Sx, 1.0); vec2 suv = c.xy / c.w * 0.5 + 0.5;
          float sz = vpos(suv).z;
          occ += step(Sx.z + 0.02, sz) * smoothstep(0.0, 1.0, radius / max(abs(P.z - sz), 1e-3));
        }
        ao = clamp(1.0 - occ / 12.0 * 1.25, 0.0, 1.0);
      }
      gl_FragColor = vec4(0.0, 0.0, 0.0, ao);
    }`, { tDepth: { value: null }, uProjInv: { value: new THREE.Matrix4() }, uProj: { value: new THREE.Matrix4() }, uTexel: { value: new THREE.Vector2() } }),
  blur: passMat(`uniform sampler2D tSrc; uniform sampler2D tDepth; uniform mat4 uProjInv; uniform vec2 uStep; varying vec2 vUv;
    float lz(vec2 uv){ float d = texture2D(tDepth, uv).x; vec4 p = uProjInv * vec4(uv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0); return p.z / p.w; }
    void main(){
      float z0 = lz(vUv); vec4 sum = vec4(0.0); float ws = 0.0;
      for (int y = -1; y <= 2; y++) for (int x = -1; x <= 2; x++) {
        vec2 uv = vUv + (vec2(float(x), float(y)) - 0.5) * uStep;
        float w = exp(-abs(lz(uv) - z0) / max(-z0 * 0.04, 0.03));
        sum += texture2D(tSrc, uv) * w; ws += w;
      }
      gl_FragColor = sum / max(ws, 1e-4);
    }`, { tSrc: { value: null }, tDepth: { value: null }, uProjInv: { value: new THREE.Matrix4() }, uStep: { value: new THREE.Vector2() } }),
  comp: passMat(`uniform sampler2D tScene; uniform sampler2D tBloom; uniform float uBloom; uniform sampler2D tAO; uniform float uAOOn; uniform float uExposure; uniform float uTime; uniform float uVig; uniform float uGrain; uniform float uCA;
    uniform float uNeg; uniform float uDrunk; uniform float uHurt; uniform float uSpeed; uniform float uWet; uniform vec3 uTint; uniform sampler2D tExpo; varying vec2 vUv;
    vec3 aces(vec3 x){ return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
    void main(){
      vec2 uv = vUv;
      uv += uDrunk * 0.007 * vec2(sin(uTime * 1.3 + uv.y * 6.0), cos(uTime * 1.1 + uv.x * 5.0));
      uv += uWet * 0.004 * vec2(sin(uTime * 2.1 + uv.y * 18.0), cos(uTime * 1.7 + uv.x * 15.0));
      vec2 dc = uv - 0.5; float r2 = dot(dc, dc);
      float ca = uCA * r2 * (1.0 + uDrunk * 4.0 + uSpeed * 2.0);
      vec3 col = vec3(texture2D(tScene, uv - dc * ca).r, texture2D(tScene, uv).g, texture2D(tScene, uv + dc * ca).b);
      if (uSpeed > 0.01) { vec3 acc = col; for (int i = 1; i <= 5; i++) { acc += texture2D(tScene, uv - dc * float(i) * 0.012 * uSpeed).rgb; } col = acc / 6.0; }
      if (uAOOn > 0.5) col *= mix(1.0, texture2D(tAO, uv).a, 0.85);
      #if __VERSION__ >= 300
        if (any(isnan(col)) || any(isinf(col))) col = vec3(0.0);
      #endif
      col = clamp(col, 0.0, 80.0) * uExposure * texture2D(tExpo, vec2(0.5)).r * uTint + texture2D(tBloom, uv).rgb * (uBloom / 5.0);
      col = aces(col);
      col = mix(col, col * col * (3.0 - 2.0 * col), 0.35);   // a little more contrast in the mid-tones
      float l = dot(col, vec3(0.2126, 0.7152, 0.0722));
      col = mix(vec3(l), col, 1.12);
      col += vec3(-0.006, 0.004, 0.014) * (1.0 - l) * (1.0 - l);
      col *= mix(vec3(0.98, 1.0, 1.02), vec3(1.06, 1.0, 0.93), smoothstep(0.25, 0.95, l));
      col = pow(max(col, 0.0), vec3(1.0 / 2.2));
      col = mix(col, col * vec3(1.0, 0.25, 0.2), uHurt * smoothstep(0.1, 0.7, sqrt(r2) * 1.4));
      col *= 1.0 - uVig * smoothstep(0.3, 0.95, sqrt(r2) * 1.38);
      float n = fract(sin(dot(gl_FragCoord.xy + fract(uTime) * 91.0, vec2(12.9898, 78.233))) * 43758.5453);
      col += (n - 0.5) * uGrain;
      col = mix(col, vec3(1.0) - col, uNeg);
      gl_FragColor = vec4(col, 1.0); }`, { tScene: { value: null }, tBloom: { value: null }, uBloom: { value: 0.6 }, uExposure: { value: 1 }, uTime: { value: 0 }, uVig: { value: 0.42 }, uGrain: { value: 0.03 }, uCA: { value: 0.01 }, uDrunk: { value: 0 }, uHurt: { value: 0 }, uSpeed: { value: 0 }, uWet: { value: 0 }, uTint: { value: new THREE.Vector3(1, 1, 1) }, uNeg: { value: 0 }, tAO: { value: null }, uAOOn: { value: 0 }, tExpo: { value: null } }),
};
function pass(mat, target) { fsMesh.material = mat; renderer.setRenderTarget(target); renderer.render(fsScene, fsCam); }
function blurInto(src, dst) { const u = PM.blur.uniforms; u.tSrc.value = src.texture; u.tDepth.value = RT.depthTexture; u.uProjInv.value.copy(camera.projectionMatrixInverse); u.uStep.value.set(1 / src.width, 1 / src.height); pass(PM.blur, dst); }
let beforeWater = null;   // hook: the world sets water uniforms that need this frame's targets
let beforeScene = null;   // hook: portals draw their views before the main pass
function renderFrame() {
  makeTargets();
  camera.updateMatrixWorld();
  if (beforeScene) beforeScene();
  renderer.setRenderTarget(RT); renderer.clear(); renderer.render(scene, camera);
  const deep = !!RT.depthTexture, gfx = gfxSettings().gfx !== undefined ? gfxSettings().gfx : 2;
  if (deep && waterScene.children.length) {
    if (beforeWater) beforeWater(RT);
    renderer.setRenderTarget(RT); renderer.render(waterScene, camera);
  }
  const aoOn = deep && gfx >= 1;
  if (aoOn) {
    const u = PM.ao.uniforms; u.tDepth.value = RT.depthTexture; u.uProjInv.value.copy(camera.projectionMatrixInverse); u.uProj.value.copy(camera.projectionMatrix); u.uTexel.value.set(1 / RW, 1 / RHh);
    pass(PM.ao, AOA); blurInto(AOA, AOB);
  }
  PM.comp.uniforms.tAO.value = AOB.texture; PM.comp.uniforms.uAOOn.value = aoOn ? 1 : 0;
  // eye adaptation: log-average luminance of the frame drives exposure, eased over time
  PM.lum.uniforms.tSrc.value = RT.texture; pass(PM.lum, LUM);
  const prev = expoPing ? EXB : EXA, next = expoPing ? EXA : EXB; expoPing ^= 1;
  const au = PM.adapt.uniforms; au.tLum.value = LUM.texture; au.tPrev.value = prev.texture;
  au.uK.value = expoReset ? 1 : 1 - Math.exp(-(renderFrame.dt || 0.016) * 1.6); expoReset = false;
  pass(PM.adapt, next);
  PM.pre.uniforms.tExpo.value = next.texture; PM.comp.uniforms.tExpo.value = next.texture;
  PM.pre.uniforms.uExpo.value = PM.comp.uniforms.uExposure.value; PM.pre.uniforms.tSrc.value = RT.texture; PM.pre.uniforms.uTexel.value.set(1 / RW, 1 / RHh); pass(PM.pre, BD[0]);
  for (let i = 1; i < BD.length; i++) { PM.down.uniforms.tSrc.value = BD[i - 1].texture; PM.down.uniforms.uTexel.value.set(1 / BD[i - 1].width, 1 / BD[i - 1].height); pass(PM.down, BD[i]); }
  let src = BD[BD.length - 1];
  for (let i = BD.length - 2; i >= 0; i--) { PM.up.uniforms.tSrc.value = src.texture; PM.up.uniforms.tAdd.value = BD[i].texture; PM.up.uniforms.uTexel.value.set(0.5 / src.width, 0.5 / src.height); pass(PM.up, BU[i]); src = BU[i]; }
  PM.comp.uniforms.tBloom.value = BU[0].texture;
  PM.comp.uniforms.tScene.value = RT.texture;
  pass(PM.comp, null);
}
