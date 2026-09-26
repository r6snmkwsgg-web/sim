// Portal check: walks through every portal door and checks you land on your feet. Needs the game served at
// http://localhost:8812 (python3 -m http.server 8812 in game/). node rooms/tools/portals.mjs <room>[:<door>] ...
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const rooms = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
const pg = await (await b.newContext({ viewport: { width: 480, height: 270 }, ignoreHTTPSErrors: true })).newPage();
let errs = []; pg.on('pageerror', e => errs.push(e.message + ' ' + (e.stack || '').split('\n')[1]));
for (let t = 0; t < 5; t++) { try { await pg.goto('http://localhost:8812/index.html', { timeout: 60000 }); } catch (e) { continue; } await pg.waitForTimeout(4000); if (await pg.evaluate(() => typeof freshState === 'function' && typeof THREE !== 'undefined' && typeof WORLD !== 'undefined').catch(() => false)) break; }
for (let i = 0; i < 120; i++) { if (await pg.evaluate(() => WORLD.ready)) break; await pg.waitForTimeout(1000); }
for (const spec of rooms) { const [room, kk] = spec.split(':');
  await pg.evaluate(async room => {
    const SBX = fdiv(START_CX, 2), SBZ = fdiv(START_CZ, 2), lvOff = mod(START_FLOOR, 2);
    const res = await fetch('rooms/' + room + '.json').then(r => r.json()); ROOM_SIZE[room] = [res.w, res.d, res.levels];
    PLAN_OVERRIDE.clear(); PLAN_OVERRIDE.set(`${SBX}:${SBZ}:${fdiv(START_FLOOR, 2)}`, { 0: put => { put(room, 0, 0, 0, 0, 0); }, 1: put => {} });
    PLAN_CACHE.clear();
    try { localStorage.clear(); } catch (e) {} S = freshState(); S.cx = SBX * 2; S.cz = SBZ * 2; S.floor = fdiv(START_FLOOR, 2) * 2; save(); startPlay(false); closeOverlays(); MODE = 'play';
  }, room);
  let ok = false;
  for (let i = 0; i < 60 && !ok; i++) { await pg.waitForTimeout(1000); ok = await pg.evaluate(room => [...WORLD.inst.values()].some(r => r.pf.name === room && r.doors && r.doors.length), room); }
  const out = await pg.evaluate(([room, kk]) => {
    MODE = 'pause';
    const inst = [...WORLD.inst.values()].find(r => r.pf.name === room);
    if (!inst) return room + ': not loaded';
    const doors = PORTAL.doors.filter(D => D.r === inst && !D.mirror), res = [];
    const c = new THREE.Vector3(), n = new THREE.Vector3(), T = new THREE.Matrix4();
    for (const [k, D] of doors.entries()) { if (kk !== undefined && k !== +kk) continue;
      const S0 = JSON.stringify(S);
      doorWorld(D, c, n, T);
      const h = new THREE.Vector3(n.x, 0, n.z); if (h.length() < 0.3) { res.push(k + ':floor/ceiling door skipped'); continue; } h.normalize();
      let crossed = false, dir = '';
      for (const sg of [1, -1]) {
        if (crossed) break;
        Object.assign(S, JSON.parse(S0));
        S.x = c.x - sg * h.x * 1.2; S.z = c.z - sg * h.z * 1.2; S.y = c.y; S.yaw = Math.atan2(-sg * h.x, -sg * h.z); PL.vx = PL.vz = PL.vy = 0;
        PORTAL.prevAbs = null; portalCross();
        for (let i = 0; i < 20 && !crossed; i++) { S.x += sg * h.x * 0.15; S.z += sg * h.z * 0.15; crossed = portalCross(); }
        if (crossed) dir = sg > 0 ? '+' : '-';
      }
      if (!crossed) { res.push(k + ':NO-CROSS'); Object.assign(S, JSON.parse(S0)); continue; }
      const y0 = S.y + S.floor * RLH;
      for (let i = 0; i < 90; i++) updatePlayer(1 / 30);
      const drop = y0 - (S.y + S.floor * RLH);
      res.push(k + dir + (drop > 2.5 ? ':FELL ' + drop.toFixed(1) + 'm' : !roomReadyAt(S.x, S.y + 0.5, S.z) ? ':NOT-READY' : !PL.onGround ? ':AIRBORNE' : ':ok'));
      Object.assign(S, JSON.parse(S0));
    }
    return room + ' (' + doors.length + ' doors) ' + res.join(' ');
  }, [room, kk]);
  console.log(out);
}
console.log('errors', errs); await b.close();
