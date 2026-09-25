"""Shared helpers for batch 3 of the Deep Stacks (weather indoors): rainroom, snowstacks, tidelibrary,
cloudfloor, thunderatrium, desertroom, fogmaze, aurorastacks."""
import random
from lib import *
from kit_a import (shell, pointed_profile, obox, beam, rot, rail, stair_rail, shelf, sh, stack, ang_shelf, chair,
                   table, bulb, desk_lamp, candle, ladder, navloop, tidy, frustum, floor_lamp, open_flight)
from kit_f import dome_cap, dome_z


# ---------------------------------------------------------------------------
# bookkeeping
def secret(R, x, y, z, name, text, r=1.5):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, bx=None, **kw):
    d = {'type': kind}
    if bx is not None: d['box'] = [round(float(v), 2) for v in bx]
    for k, v in kw.items(): d[k] = [round(float(c), 2) for c in v] if isinstance(v, (list, tuple)) else v
    R.meta.setdefault('fx', []).append(d)


def finish(R, label, blurb, weight=4, probe=(16, 16, 1.8), top=TOP):
    R.spot('probe', *probe)
    R.meta.update(label=label, weight=weight, blurb=blurb)
    R.meta['box'] = [[T, 0, T], [R.W - T, top, R.D - T]]
    return tidy(R)


# ---------------------------------------------------------------------------
# soft ground: dunes, drifts, clouds
def field(fn, x0, y0, x1, y1, nx, ny, m='bed', floor=0.0, eps=0.015, skip=None):
    """An open heightfield surface z = fn(x, y) over a rectangle, faces up. Quads whose corners all
    sit at or below `floor` + eps are dropped (they would hide under the real floor)."""
    g = Geo()
    ids = {}
    def V(i, j):
        k = (i, j)
        if k not in ids:
            x = x0 + (x1 - x0) * i / nx; y = y0 + (y1 - y0) * j / ny
            ids[k] = g.vert((x, y, fn(x, y)))
        return ids[k]
    for i in range(nx):
        for j in range(ny):
            q = [V(i, j), V(i + 1, j), V(i + 1, j + 1), V(i, j + 1)]
            if all(g.v[v][2] <= floor + eps for v in q): continue
            if skip and skip(sum(g.v[v][0] for v in q) / 4, sum(g.v[v][1] for v in q) / 4): continue
            g.face(q, m, [(g.v[v][0], g.v[v][1]) for v in q])
    return g


def smooth_bump(d, r):
    """1 at d=0 falling smoothly to 0 at d=r."""
    if d >= r: return 0.0
    t = d / r
    return 0.5 * (1 + math.cos(math.pi * t))


def dist_seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - dx * t, py - ay - dy * t)


def ellipsoid(cx, cy, cz, rx, ry, rz, m='bed', segs=12, rings=6, lower=True):
    g = sphere(0, 0, 0, 1.0, segs, rings, m, lower=lower)
    g.v = [(x * rx + cx, y * ry + cy, z * rz + cz) for (x, y, z) in g.v]
    return g


def puffs(cx, cy, cz, r, n, m='bed', seed=0, flat=0.55, segs=10, rings=5):
    """A cloud: a cluster of squashed spheres (drawn, not collided)."""
    rnd = random.Random(seed)
    g = Geo()
    g.add(ellipsoid(cx, cy, cz, r, r, r * flat, m, segs, rings))
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.4, 0.9) * r
        rr = r * rnd.uniform(0.45, 0.75)
        g.add(ellipsoid(cx + math.cos(a) * d, cy + math.sin(a) * d, cz + rnd.uniform(-0.2, 0.35) * r, rr, rr, rr * flat * rnd.uniform(0.9, 1.3), m, segs, rings))
    return g


# ---------------------------------------------------------------------------
# architecture
def arc_band(c, w, jamb, rise, d0, d1, segs=24):
    """A closed (p, z) profile: the band between an arch offset inward by d0 and by d1 (a rib)."""
    a = arch_profile(c, w - 2 * d0, 0, jamb, segs, rise=rise - d0)
    b = arch_profile(c, w - 2 * d1, 0, jamb, segs, rise=rise - d1)
    return a[2:] + list(reversed(b[2:]))


def arch_hole(R, axis, c, a0, a1, w, jamb, z0=0.0, floor='terrazzo', wall='tile', segs=14, rise=None):
    """Cut an arched opening through a wall: axis 'x' means the opening runs along x (wall in the y-z
    plane at c is crossed by walking along x)."""
    pr = arch_profile(c, w, z0, jamb, segs, rise=rise)
    R.cut(prism(pr, axis, a0, a1, arch_mats(len(pr), floor, wall)))


def window(R, side, c, z0, w, jamb, depth=0.3, em='e_skydome', frame='iron', mull=3, trans=2, wallpos=None, segs=12):
    """A tall arched window in a boundary wall: a recess `depth` into the wall with a glowing back
    (sky), iron mullions and transoms in front of it. side 'N','S','E','W'."""
    W_, D_ = R.W, R.D
    pos = {'S': T, 'N': D_ - T, 'W': T, 'E': W_ - T}[side] if wallpos is None else wallpos
    sgn = -1 if side in 'SW' else 1
    back = pos + sgn * depth
    axis = 'y' if side in 'SN' else 'x'
    pr = arch_profile(c, w, z0, jamb, segs)
    a0, a1 = (min(pos - sgn * 0.05, back), max(pos - sgn * 0.05, back))
    R.cut(prism(pr, axis, a0, a1, ['tile'] * len(pr), cap='tile'))
    # the glowing pane at the back
    pane = prism(pr, axis, back - sgn * 0.02 if sgn > 0 else back, back if sgn > 0 else back + 0.02, em, cap=em)
    R.light(pane)
    # iron glazing bars
    f = back - sgn * 0.06
    top = z0 + jamb + w / 2
    for k in range(1, mull + 1):
        p = c - w / 2 + w * k / (mull + 1)
        zt = z0 + jamb + math.sqrt(max(0.0, (w / 2) ** 2 - (p - c) ** 2))
        if axis == 'y': R.nocol.add(box(p - 0.03, f - 0.03, z0, p + 0.03, f + 0.03, zt, frame))
        else: R.nocol.add(box(f - 0.03, p - 0.03, z0, f + 0.03, p + 0.03, zt, frame))
    for k in range(1, trans + 1):
        z = z0 + jamb * k / (trans + 1)
        if axis == 'y': R.nocol.add(box(c - w / 2, f - 0.03, z - 0.03, c + w / 2, f + 0.03, z + 0.03, frame))
        else: R.nocol.add(box(f - 0.03, c - w / 2, z - 0.03, f + 0.03, c + w / 2, z + 0.03, frame))
    z = z0 + jamb
    if axis == 'y': R.nocol.add(box(c - w / 2, f - 0.03, z - 0.04, c + w / 2, f + 0.03, z + 0.04, frame))
    else: R.nocol.add(box(f - 0.03, c - w / 2, z - 0.04, f + 0.03, c + w / 2, z + 0.04, frame))
    # a stone sill
    s0, s1 = (pos - 0.12, pos + 0.02) if sgn > 0 else (pos - 0.02, pos + 0.12)
    s0, s1 = (min(s0, s1), max(s0, s1))
    if axis == 'y': R.parts.add(box(c - w / 2 - 0.15, s0 if sgn > 0 else s0, z0 - 0.12, c + w / 2 + 0.15, s1, z0, 'tile'))
    else: R.parts.add(box(s0, c - w / 2 - 0.15, z0 - 0.12, s1, c + w / 2 + 0.15, z0, 'tile'))


def pier(R, x, y, z0, z1, s=0.5, m='tile', base=True, cap=True):
    R.parts.add(box(x - s / 2, y - s / 2, z0, x + s / 2, y + s / 2, z1, m, skip=('-z',)))
    if base: R.parts.add(box(x - s / 2 - 0.08, y - s / 2 - 0.08, z0, x + s / 2 + 0.08, y + s / 2 + 0.08, z0 + 0.3, m, skip=('-z',)))
    if cap: R.parts.add(box(x - s / 2 - 0.1, y - s / 2 - 0.1, z1 - 0.25, x + s / 2 + 0.1, y + s / 2 + 0.1, z1, m))


# ---------------------------------------------------------------------------
# furniture
def bell_jar(R, x, y, z, r=0.2, h=0.42, m='brass', book='oxblood', ribs=8, segs=3):
    """Books under a bell: a brass base, a book inside, a cage of fine brass ribs with a knob on top
    (there is no glass in this library: the ribs read as a jar's leading)."""
    R.parts.add(cyl(x, y, z, z + 0.03, r + 0.03, 16, side=m, top=m, bottom=m))
    R.parts.add(box(x - 0.11, y - 0.08, z + 0.03, x + 0.11, y + 0.08, z + 0.07, book))
    R.parts.add(box(x - 0.1, y - 0.075, z + 0.07, x + 0.1, y + 0.075, z + 0.11, 'leather'))
    zs = z + h - r
    for k in range(ribs):
        a = 2 * math.pi * k / ribs
        pts = [(x + r * math.cos(a), y + r * math.sin(a), z + 0.03)]
        pts.append((x + r * math.cos(a), y + r * math.sin(a), zs))
        for s in range(1, segs + 1):
            t = (math.pi / 2) * s / segs
            rr = r * math.cos(t)
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a), zs + r * math.sin(t)))
        for p0, p1 in zip(pts, pts[1:]):
            R.nocol.add(beam(p0, p1, 0.008, m))
    R.nocol.add(cyl(x, y, zs, zs + 0.01, r, 16, side=m, caps=False))
    R.nocol.add(sphere(x, y, z + h + 0.02, 0.025, 6, 3, m))


def reading_table(R, x0, y0, x1, y1, lamps=2, chairs=True, top='leather', lamp_m='e_lamp', z=0.0, axis=None):
    """A long reading table (legs at its corners) with green lamps down its middle and chairs on both sides."""
    g = table(x0, y0, x1, y1, 0.78, 'walnut', top=top)
    g.xform(0, 0, 0, z)
    R.parts.add(g)
    along_x = (x1 - x0) >= (y1 - y0) if axis is None else axis == 'x'
    for k in range(lamps):
        t = (k + 0.5) / lamps
        if along_x: desk_lamp(R, x0 + (x1 - x0) * t, (y0 + y1) / 2, z + 0.78, lamp_m)
        else:
            lx, ly = (x0 + x1) / 2, y0 + (y1 - y0) * t
            R.parts.add(cyl(lx, ly, z + 0.78, z + 0.81, 0.08, 12, side='brass', top='brass'))
            R.parts.add(cyl(lx, ly, z + 0.81, z + 1.14, 0.012, 6, side='brass', caps=False))
            R.parts.add(obox(lx, ly - 0.17, lx, ly + 0.17, z + 1.14, z + 1.22, 0.13, 'green'))
            R.light(obox(lx, ly - 0.15, lx, ly + 0.15, z + 1.125, z + 1.14, 0.09, lamp_m))
    if chairs:
        L = (x1 - x0) if along_x else (y1 - y0)
        n = max(1, int(L / 1.1))
        for k in range(n):
            t = (k + 0.5) / n
            if along_x:
                xx = x0 + (x1 - x0) * t
                for (yy, a) in ((y0 - 0.45, math.pi / 2), (y1 + 0.45, -math.pi / 2)):
                    c = chair(xx, yy, a); c.xform(0, 0, 0, z); R.parts.add(c)
            else:
                yy = y0 + (y1 - y0) * t
                for (xx, a) in ((x0 - 0.45, 0.0), (x1 + 0.45, math.pi)):
                    c = chair(xx, yy, a); c.xform(0, 0, 0, z); R.parts.add(c)


def pendant(R, x, y, z, top, r=0.22, m='e_lamp', shade='green'):
    """A hanging green-shaded library lamp on a rod."""
    R.nocol.add(cyl(x, y, z + 0.2, top, 0.012, 6, side='brass', caps=False))
    R.nocol.add(frustum(x, y, z - 0.02, z + 0.22, r * 1.6, r * 0.4, 14, shade, inner='ivory'))
    R.light(cyl(x, y, z + 0.02, z + 0.06, r * 0.7, 10, side=m, top=m, bottom=m))


def lamp_post(R, x, y, z=0.0, h=2.6, m='e_lamp', shade='green'):
    """A tall iron standard with a green shade: a street lamp for the stacks."""
    R.parts.add(cyl(x, y, z, z + 0.12, 0.18, 10, side='iron', top='iron', bottom='iron'))
    R.parts.add(cyl(x, y, z + 0.12, z + h, 0.035, 8, side='iron', caps=False))
    R.nocol.add(frustum(x, y, z + h - 0.02, z + h + 0.2, 0.34, 0.1, 12, shade, inner='ivory'))
    R.light(cyl(x, y, z + h - 0.02, z + h + 0.04, 0.2, 10, side=m, top=m, bottom=m))


def book_pile(R, x, y, z, n=5, seed=0, col=True):
    rnd = random.Random(seed)
    g = Geo()
    zz = z
    for i in range(n):
        w, d, t = rnd.uniform(0.2, 0.3), rnd.uniform(0.15, 0.21), rnd.uniform(0.03, 0.06)
        b = box(-w / 2, -d / 2, 0, w / 2, d / 2, t, rnd.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet')))
        b.xform(rnd.uniform(-0.4, 0.4), x + rnd.uniform(-0.03, 0.03), y + rnd.uniform(-0.03, 0.03), zz)
        g.add(b); zz += t
    (R.parts if col else R.nocol).add(g)
    return zz


def open_book(R, x, y, z, ang=0.0, m='leather'):
    g = Geo()
    g.add(box(-0.2, -0.14, 0, 0.2, 0.14, 0.015, m))
    g.add(rot(box(-0.19, -0.13, 0.0, 0.0, 0.13, 0.02, 'ivory'), 'y', -0.08, 0, 0, 0.015))
    g.add(rot(box(0.0, -0.13, 0.0, 0.19, 0.13, 0.02, 'ivory'), 'y', 0.08, 0, 0, 0.015))
    g.xform(ang, x, y, z)
    R.nocol.add(g)


def armchair(R, x, y, face, m='velvet', frame='walnut', z=0.0):
    g = Geo()
    g.add(box(-0.4, -0.4, 0, 0.4, 0.4, 0.42, m, sides=frame))
    g.add(box(-0.45, -0.4, 0, -0.3, 0.4, 1.0, m))
    g.add(box(-0.4, -0.48, 0, 0.35, -0.38, 0.65, m))
    g.add(box(-0.4, 0.38, 0, 0.35, 0.48, 0.65, m))
    g.xform(face, x, y, z)
    R.parts.add(g)
    R.spot('sit', x, y, z + 0.42, face)


def strands(R, x0, y0, x1, y1, z0, z1, n, seed=1, m='chrome', w=0.012):
    """A curtain of falling water: thin glinting threads (drawn, not collided) between two points in plan."""
    rnd = random.Random(seed)
    for k in range(n):
        t = rnd.random()
        x, y = x0 + (x1 - x0) * t + rnd.uniform(-0.05, 0.05), y0 + (y1 - y0) * t + rnd.uniform(-0.05, 0.05)
        zb = z0 + rnd.uniform(0, 0.2)
        R.nocol.add(box(x - w, y - w, zb, x + w, y + w, z1 - rnd.uniform(0, 0.15), m))


def blanket(R, x0, y0, x1, y1, z, t=0.05, m='bed', col=False):
    """A thin blanket of snow or sand over something flat."""
    (R.parts if col else R.nocol).add(box(x0, y0, z, x1, y1, z + t, m))


def fill_under(R, fn, x0, y0, st, nx, ny, skip=None, minh=1.1, q=0.5, gap=0.1):
    """Invisible solid under a heightfield (dunes, drifts), so there are no hollow pockets under it that
    a body could fit in: runs of grid cells along x, each a collider box from the floor up to the
    surface (quantised down by q)."""
    for j in range(ny):
        ya, yb = y0 + j * st, y0 + (j + 1) * st
        run = None
        for i in range(nx + 1):
            lvl = 0.0
            if i < nx:
                xa, xb = x0 + i * st, x0 + (i + 1) * st
                if not (skip and skip((xa + xb) / 2, (ya + yb) / 2)):
                    h = min(fn(xa, ya), fn(xb, ya), fn(xa, yb), fn(xb, yb), fn((xa + xb) / 2, (ya + yb) / 2)) - gap
                    if h >= minh: lvl = math.floor(h / q) * q
            if run and run[1] != lvl:
                R.col.add(box(run[0], ya, 0, x0 + i * st, yb, run[1], 'tile', skip=('-z',)))
                run = None
            if lvl > 0 and not run: run = [x0 + i * st, lvl]
