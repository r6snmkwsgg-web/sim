"""Shared helpers for batch 5 of the Deep Stacks (mushroomstacks, growingstair, whaleribs, flowerindex,
frozenexplosion, daynight, ruinwing, clockroom2)."""
import random
from lib import *
from kit_a import *


# ---------------------------------------------------------------------------
# metadata
def secret(R, x, y, z, name, text, r=1.5):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, bx, **kw):
    d = {'type': kind, 'box': [round(float(c), 2) for c in bx]}
    d.update(kw)
    R.meta.setdefault('fx', []).append(d)


# ---------------------------------------------------------------------------
# solids
def cone(cx, cy, z0, z1, r0, r1, segs=12, m='tile', top=None, bottom=None, a0=0.0):
    """A closed frustum: radius r0 at z0, r1 at z1 (r1 may be ~0 for a point)."""
    g = Geo()
    ang = [a0 + 2 * math.pi * k / segs for k in range(segs)]
    b = [g.vert((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0)) for a in ang]
    t = [g.vert((cx + max(r1, 1e-3) * math.cos(a), cy + max(r1, 1e-3) * math.sin(a), z1)) for a in ang]
    for k in range(segs):
        j = (k + 1) % segs
        u0, u1 = ang[k] * r0, (ang[k] + 2 * math.pi / segs) * r0
        g.face([b[k], b[j], t[j], t[k]], m, [(u0, z0), (u1, z0), (u1, z1), (u0, z1)])
    g.face(list(reversed(b)), bottom or m, [(g.v[i][0], g.v[i][1]) for i in reversed(b)])
    g.face(t, top or m, [(g.v[i][0], g.v[i][1]) for i in t])
    return g.fix()


def blob(cx, cy, cz, rx, ry, rz, segs=8, rings=4, m='green', lower=True):
    """An ellipsoid (a squashed low-poly sphere)."""
    g = sphere(0, 0, 0, 1.0, segs, rings, m, lower=lower)
    g.v = [(cx + x * rx, cy + y * ry, cz + z * rz) for x, y, z in g.v]
    return g.fix()


def tilted(g, ax, ang, cx, cy, cz):
    return rot(g, ax, ang, cx, cy, cz)


def disc_v(cx, cy, cz, r, a, n=10, m='ivory', off=0.0):
    """A flat n-gon standing vertically, its face looking along plan angle a (radians). One face."""
    g = Geo()
    nx, ny = math.cos(a), math.sin(a)
    ux, uy = -ny, nx                      # the disc's horizontal axis
    cx += nx * off; cy += ny * off
    ids = []; uvs = []
    for k in range(n):
        t = 2 * math.pi * k / n
        p = (cx + ux * r * math.cos(t), cy + uy * r * math.cos(t), cz + r * math.sin(t))
        ids.append(g.vert(p)); uvs.append((r * math.cos(t), r * math.sin(t)))
    # winding: counter-clockwise seen from the front (along +n)
    g.face(ids, m, uvs)
    return g


def quad_v(cx, cy, cz, a, L, w, ang, m='iron', off=0.0):
    """A thin flat bar (a clock hand) in the vertical plane facing plan angle a, from (cx,cy,cz) along
    in-plane angle ang (0 = the plane's horizontal axis, pi/2 = up), length L, width w. One face."""
    g = Geo()
    nx, ny = math.cos(a), math.sin(a)
    ux, uy = -ny, nx
    cx += nx * off; cy += ny * off
    c, s = math.cos(ang), math.sin(ang)
    pts2 = [(s * w / 2, -c * w / 2), (c * L + s * w / 2, s * L - c * w / 2), (c * L - s * w / 2, s * L + c * w / 2), (-s * w / 2, c * w / 2)]
    ids = [g.vert((cx + ux * p, cy + uy * p, cz + q)) for p, q in pts2]
    g.face(ids, m, [(p, q) for p, q in pts2])
    return g


def hdisc(cx, cy, z, r, n=10, m='green', up=True, a0=0.0, a1=None):
    """A flat horizontal n-gon (or a sector of one), one face."""
    g = Geo()
    if a1 is None:
        ids = [g.vert((cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + r * math.sin(a0 + 2 * math.pi * k / n), z)) for k in range(n)]
    else:
        ids = [g.vert((cx, cy, z))] + [g.vert((cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n), z)) for k in range(n + 1)]
    if not up: ids = ids[::-1]
    g.face(ids, m, [(g.v[i][0], g.v[i][1]) for i in ids])
    return g


# ---------------------------------------------------------------------------
# living things
def mushroom(R, x, y, z, h, r, cap='e_blue', stalk='ivory', lean=0.0, lean_dir=0.0, segs=8, gills=None):
    """A mushroom: a stalk (drawn, not collided) and a domed glowing cap."""
    tx, ty = x + math.cos(lean_dir) * lean * h, y + math.sin(lean_dir) * lean * h
    R.nocol.add(beam((x, y, z), (tx, ty, z + h), max(0.012, r * 0.28), stalk))
    capg = blob(tx, ty, z + h - r * 0.08, r, r, r * 0.55, segs, 3, cap, lower=False)
    R.light(capg)
    if gills:
        R.nocol.add(hdisc(tx, ty, z + h - r * 0.1, r * 0.92, segs, gills, up=False))


def shrooms_on_slabs(R, ids, rng, per=0.5, big=0.0, cap='e_blue'):
    """Grow little mushrooms out of the front lip of some shelf rows (slab ids from sh/shelf)."""
    for i in ids:
        s = R.slabs[i]
        if rng.random() > per: continue
        o, u, n = s['o'], s['u'], s['n']
        k = rng.randint(1, 4)
        t0 = rng.random()
        for j in range(k):
            t = min(0.97, max(0.03, t0 + rng.uniform(-0.08, 0.08)))
            px = o[0] + u[0] * t + n[0] * 0.03
            py = o[1] + u[1] * t + n[1] * 0.03
            hh = rng.uniform(0.07, 0.2) + big * rng.random()
            rr = rng.uniform(0.035, 0.09) + big * 0.4 * rng.random()
            mushroom(R, px, py, o[2] - 0.01, hh, rr, cap=cap, lean=rng.uniform(0.1, 0.5),
                     lean_dir=math.atan2(n[1], n[0]) + rng.uniform(-0.6, 0.6), segs=6)


def leaves(R, cx, cy, cz, r, n, rng, m='damask', flat=0.6, light=None):
    """A cluster of leafy blobs round (cx, cy, cz)."""
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi); d = r * math.sqrt(rng.random())
        s = rng.uniform(0.45, 0.8) * r
        R.nocol.add(blob(cx + math.cos(a) * d, cy + math.sin(a) * d, cz + rng.uniform(-0.4, 0.4) * r * flat,
                         s, s * rng.uniform(0.7, 1.1), s * flat, 7, 3, m))


def vine(R, x, y, z0, z1, rng, m='damask', w=0.03, a=0.0):
    """A hanging strand of ivy (drawn, not collided): a thin stem with flat leaves along it."""
    R.nocol.add(box(x - w / 2, y - w / 2, z0, x + w / 2, y + w / 2, z1, 'walnut', skip=('-z', '+z')))
    g = Geo()
    z = z1 - 0.1
    while z > z0:
        s = rng.uniform(0.1, 0.18)
        b = rng.uniform(0, 2 * math.pi); c, sn = math.cos(b), math.sin(b)
        px, py = x + c * 0.03, y + sn * 0.03
        tip = (px + c * s * 1.4, py + sn * s * 1.4, z - s * 0.5)
        side = (-sn * s * 0.5, c * s * 0.5)
        mid = (px + c * s * 0.6, py + sn * s * 0.6, z - s * 0.1)
        leaf_poly(g, [(px, py, z), (mid[0] + side[0], mid[1] + side[1], mid[2] + 0.03), tip, (mid[0] - side[0], mid[1] - side[1], mid[2] + 0.03)], m, off=0.003)
        z -= rng.uniform(0.1, 0.22)
    R.nocol.add(g)


# ---------------------------------------------------------------------------
# bits and pieces
def book_geo(w=0.2, t=0.05, h=0.28, m='oxblood', page='ivory'):
    """A closed book centred on the origin (spine along -x), lying flat."""
    g = box(-w / 2, -h / 2, -t / 2, w / 2, h / 2, t / 2, page)
    g.add(box(-w / 2 - 0.006, -h / 2 - 0.006, t / 2, w / 2 + 0.006, h / 2 + 0.006, t / 2 + 0.008, m))
    g.add(box(-w / 2 - 0.006, -h / 2 - 0.006, -t / 2 - 0.008, w / 2 + 0.006, h / 2 + 0.006, -t / 2, m))
    g.add(box(-w / 2 - 0.014, -h / 2 - 0.006, -t / 2 - 0.008, -w / 2, h / 2 + 0.006, t / 2 + 0.008, m))
    return g


def open_book(w=0.2, h=0.28, open_ang=0.5, m='oxblood', page='ivory'):
    """An open book, spine along y at the origin, its two leaves raised open_ang from flat (a V)."""
    g = Geo()
    right = box(0, -h / 2, -0.012, w, h / 2, 0.012, page, bottom=m)
    g.add(rot(right, 'y', -open_ang))
    left = box(-w, -h / 2, -0.012, 0, h / 2, 0.012, page, bottom=m)
    g.add(rot(left, 'y', open_ang))
    return g


def orient(g, yaw=0.0, pitch=0.0, roll=0.0, x=0.0, y=0.0, z=0.0):
    """Tumble a piece built round the origin: roll about x, pitch about y, yaw about z; then move it."""
    if roll: rot(g, 'x', roll)
    if pitch: rot(g, 'y', pitch)
    if yaw: rot(g, 'z', yaw)
    g.v = [(a + x, b + y, c + z) for a, b, c in g.v]
    return g


def rubble(R, cx, cy, r, h, rng, n=18, m=('tile', 'plaster', 'slate'), solid=True, segs=10):
    """A heap of fallen stone: a cone you can walk on (if low enough) under tumbled blocks."""
    if solid:
        R.parts.add(cone(cx, cy, 0, h, r, r * 0.25, segs, m[0]))
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi); d = r * math.sqrt(rng.random()) * 0.9
        zz = max(0.0, h * (1 - d / r)) - 0.1
        s = rng.uniform(0.15, 0.55) * (0.6 + 0.4 * r / 2)
        b = box(-s, -s * 0.7, -s * 0.4, s, s * 0.7, s * 0.4, m[k % len(m)])
        orient(b, rng.uniform(0, 6.28), rng.uniform(-0.5, 0.5), rng.uniform(-0.4, 0.4), cx + math.cos(a) * d, cy + math.sin(a) * d, zz)
        R.nocol.add(b)


def lantern(R, x, y, z, m='e_amber', frame='brass', s=1.0):
    """A small hanging or standing lantern: a glowing core in a brass cage."""
    R.light(box(x - 0.07 * s, y - 0.07 * s, z, x + 0.07 * s, y + 0.07 * s, z + 0.2 * s, m))
    R.nocol.add(box(x - 0.1 * s, y - 0.1 * s, z + 0.2 * s, x + 0.1 * s, y + 0.1 * s, z + 0.24 * s, frame))
    R.nocol.add(box(x - 0.1 * s, y - 0.1 * s, z - 0.03 * s, x + 0.1 * s, y + 0.1 * s, z, frame))
    for (px, py) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        R.nocol.add(box(x + px * 0.09 * s - 0.01, y + py * 0.09 * s - 0.01, z, x + px * 0.09 * s + 0.01, y + py * 0.09 * s + 0.01, z + 0.2 * s, frame, skip=('-z', '+z')))


def lectern_lamp(R, x, y, a=0.0, h=1.05):
    """A pedestal lectern with a green banker's lamp on it."""
    R.parts.add(box(x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, 0.12, 'walnut'))
    R.parts.add(box(x - 0.18, y - 0.18, 0.12, x + 0.18, y + 0.18, h - 0.06, 'walnut'))
    R.parts.add(box(x - 0.34, y - 0.34, h - 0.06, x + 0.34, y + 0.34, h, 'walnut', top='leather'))
    desk_lamp(R, x, y, h)


# ---------------------------------------------------------------------------
# paper flowers
def leaf_poly(g, pts, m, off=0.004):
    """A flat polygon drawn both ways (so it shows from either side), the back nudged along its normal."""
    a = [g.vert(p) for p in pts]
    # normal
    ux, uy, uz = [pts[1][i] - pts[0][i] for i in range(3)]
    vx, vy, vz = [pts[-1][i] - pts[0][i] for i in range(3)]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    nx, ny, nz = nx / L * off, ny / L * off, nz / L * off
    b = [g.vert((p[0] - nx, p[1] - ny, p[2] - nz)) for p in pts]
    uv = [(p[0] + p[2], p[1] + p[2]) for p in pts]
    g.face(a, m, uv)
    g.face(b[::-1], m, uv[::-1])


def petal(g, x, y, z, yaw, tilt, L, w, m='ivory', text=False):
    """A petal from (x, y, z) outward along yaw, raised by tilt (radians above horizontal)."""
    c, s = math.cos(yaw), math.sin(yaw)
    ct, st = math.cos(tilt), math.sin(tilt)
    def P(u, v, lift=0.0):
        # u along the petal, v across; the petal cups a little (lift at the edges)
        px, pz = u * ct - lift * st, u * st + lift * ct
        return (x + px * c - v * s, y + px * s + v * c, z + pz)
    cup = w * 0.12
    pts = [P(0, 0), P(0.45 * L, -w / 2, cup), P(L, -w * 0.12, cup * 0.5), P(L, w * 0.12, cup * 0.5), P(0.45 * L, w / 2, cup)]
    leaf_poly(g, pts, m)
    if text:
        for k in range(3):
            u = (0.3 + 0.14 * k) * L; hw = w * (0.3 - 0.03 * k)
            q = [P(u - 0.006, -hw, cup + 0.006), P(u + 0.006, -hw, cup + 0.006), P(u + 0.006, hw, cup + 0.006), P(u - 0.006, hw, cup + 0.006)]
            ids = [g.vert(p) for p in q]
            g.face(ids, 'black', [(0, 0), (1, 0), (1, 1), (0, 1)])


def flower(R, x, y, z, h, L, rng, m=None, n=None, text=None, lean=0.15):
    """A paper flower: a green stem, two leaves, two rings of printed petals and a gilt heart."""
    m = m or rng.choice(('ivory', 'bed', 'ivory', 'plaster'))
    n = n or rng.randint(6, 9)
    text = (L > 0.6) if text is None else text
    la = rng.uniform(0, 2 * math.pi)
    hx, hy, hz = x + math.cos(la) * lean * h * 0.3, y + math.sin(la) * lean * h * 0.3, z + h
    R.nocol.add(beam((x, y, z), (hx, hy, hz), max(0.02, L * 0.06), 'green'))
    g = Geo()
    for k in range(2):
        a = rng.uniform(0, 2 * math.pi); zz = z + h * rng.uniform(0.2, 0.55)
        petal(g, x, y, zz, a, 0.3, L * 1.1, L * 0.45, 'green')
    a0 = rng.uniform(0, 2 * math.pi)
    for k in range(n):
        petal(g, hx, hy, hz, a0 + 2 * math.pi * k / n, rng.uniform(0.25, 0.55), L, L * 0.62, m, text)
    for k in range(max(3, n - 3)):
        petal(g, hx, hy, hz + 0.01, a0 + math.pi / n + 2 * math.pi * k / max(3, n - 3), rng.uniform(0.9, 1.2), L * 0.6, L * 0.45, m, False)
    R.nocol.add(g)
    R.nocol.add(blob(hx, hy, hz + L * 0.05, L * 0.16, L * 0.16, L * 0.1, 8, 3, rng.choice(('gilt', 'oxblood', 'gilt'))))


def bed_of_flowers(R, x0, y0, x1, y1, rng, hmin=0.5, hmax=1.6, lmin=0.18, lmax=0.45, dens=0.7, z=0.45, edge='tile'):
    """A raised bed (stone kerb, dark soil) planted with paper flowers."""
    R.parts.add(box(x0, y0, 0, x1, y1, z, edge, top='green', skip=('-z',)))
    R.nocol.add(box(x0 - 0.05, y0 - 0.05, z, x1 + 0.05, y1 + 0.05, z + 0.06, edge, skip=('-z',)))
    R.nocol.add(box(x0 + 0.1, y0 + 0.1, z + 0.06, x1 - 0.1, y1 - 0.1, z + 0.08, 'leather', skip=('-z',)))
    n = int((x1 - x0) * (y1 - y0) * dens)
    for k in range(n):
        fx_, fy_ = rng.uniform(x0 + 0.3, x1 - 0.3), rng.uniform(y0 + 0.3, y1 - 0.3)
        flower(R, fx_, fy_, z + 0.06, rng.uniform(hmin, hmax), rng.uniform(lmin, lmax), rng)
    for k in range(int(n * 0.4)):
        leaves(R, rng.uniform(x0 + 0.3, x1 - 0.3), rng.uniform(y0 + 0.3, y1 - 0.3), z + 0.2, 0.4, 2, rng)


# ---------------------------------------------------------------------------
# clocks
def clock(R, x, y, z, r, a, rng, style=None, face='ivory', rim='brass'):
    """A wall clock centred at (x, y, z) on a wall, facing plan angle a.
    style: 'round' (a brass rim), 'case' (a walnut box), 'pend' (a case with a pendulum under it)."""
    style = style or rng.choice(('round', 'round', 'case', 'pend', 'round'))
    n = 10 if r < 0.3 else 14
    nx, ny = math.cos(a), math.sin(a)
    g = Geo()
    if style == 'round':
        o = 0.0
        g.add(disc_v(x, y, z, r * 1.12, a, n, rim, off=0.02))
    else:
        o = 0.1
        hh = r * (1.3 if style == 'case' else 3.4)
        c = box(0.0, -r * 1.2, -hh, 0.1, r * 1.2, r * 1.3, 'walnut', skip=('-x',))
        g.add(c.xform(a, x, y, z))
        g.add(disc_v(x, y, z, r * 1.08, a, n, rim, off=o + 0.005))
        if style == 'pend':
            L = hh - r * 1.3
            top = z - r * 1.1
            bz = top - L * 0.8
            pg = Geo()
            pg.add(beam((x + nx * 0.11, y + ny * 0.11, top), (x + nx * 0.11, y + ny * 0.11, bz), 0.012, 'brass'))
            pg.add(disc_v(x, y, bz, r * 0.28, a, 8, 'brass', off=0.12))
            pendulum(R, pg, (x + nx * 0.11, y + ny * 0.11, top), a, rng)
    g.add(disc_v(x, y, z, r, a, n, face, off=o + 0.015))
    hr, mn = rng.uniform(0, 12), rng.uniform(0, 60)
    for (frac, L, w) in ((hr / 12, r * 0.55, r * 0.09), (mn / 60, r * 0.85, r * 0.055)):
        ang = math.pi / 2 - 2 * math.pi * frac
        g.add(quad_v(x, y, z, a, L, max(0.008, w), ang, 'black', off=o + 0.025))
    R.nocol.add(g)


def grandfather(R, x, y, a, h, rng, w=0.62, d=0.42, lit=False):
    """A longcase clock standing with its back at (x, y), facing plan angle a, h tall. Collided."""
    g = Geo()
    g.add(box(0, -w / 2, 0, d, w / 2, 0.35, 'walnut'))
    g.add(box(0.03, -w / 2 + 0.06, 0.35, d - 0.03, w / 2 - 0.06, h - w - 0.25, 'walnut'))
    g.add(box(0, -w / 2 - 0.02, h - w - 0.25, d + 0.02, w / 2 + 0.02, h - 0.12, 'walnut'))
    g.add(box(-0.02, -w / 2 - 0.05, h - 0.12, d + 0.05, w / 2 + 0.05, h, 'walnut', top='gilt'))
    # the trunk door's glass and a still pendulum bob behind it
    g.add(box(d - 0.03, -w / 2 + 0.12, 0.6, d - 0.02, w / 2 - 0.12, h - w - 0.4, 'black'))
    g.xform(a, x, y, 0)
    R.parts.add(g)
    nx, ny = math.cos(a), math.sin(a)
    fz = h - w / 2 - 0.18
    fx_, fy_ = x + nx * (d + 0.02), y + ny * (d + 0.02)
    clock(R, fx_ - nx * 0.04, fy_ - ny * 0.04, fz, w * 0.36, a, rng, style='round', rim='gilt')
    bz = 0.6 + (h - w - 1.0) * 0.35
    pg = Geo()
    pg.add(disc_v(fx_, fy_, bz, 0.1, a, 10, 'brass', off=0.0))
    pg.add(quad_v(fx_, fy_, bz, a, (h - w - 0.45) - bz, 0.02, math.pi / 2, 'brass', off=-0.002))
    pendulum(R, pg, (fx_, fy_, h - w - 0.45), a, rng, amp=0.08)


PEND_MAX = 40


def pendulum(R, g, pivot, a, rng, amp=None, period=None):
    """A pendulum that really swings (a nocol swing mover) in the plane of a wall facing plan angle a;
    past PEND_MAX movers per room it is drawn still instead."""
    n = getattr(R, '_pends', 0)
    if n >= PEND_MAX:
        R.nocol.add(g); return
    R._pends = n + 1
    axis = 'y' if abs(math.sin(a)) > abs(math.cos(a)) else 'x'
    L = max(0.2, pivot[2] - min(p[2] for p in g.v))
    per = period or 2 * math.pi * math.sqrt(L / 9.81) * rng.uniform(0.95, 1.05)
    M = R.mover('swing', pivot=tuple(round(c, 3) for c in pivot), axis=axis, amp=amp or rng.uniform(0.12, 0.2),
                period=round(per, 2), phase=round(rng.random(), 2))
    M.nocol.add(g)
