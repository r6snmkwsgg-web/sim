"""Shared helpers for batch 6 of the Deep Stacks (time II, machines): hourglass, candlehall, unfinished,
seasons, pneumatic, presses, sortingengine, typewriters."""
import random
import lib
from kit_h3 import *
from kit_h1 import along, xcyl, cone
from kit_h2 import climb_ladder, ramp, wall_col, hexa, railed_flight
from kit_h4 import tube, curve, loft, branches

# a few materials the library palette lacks (the room file carries the albedo; the game paints them)
NEW_MATS = {
    'tallow':    (0.88, 0.80, 0.64),   # candle wax, old and built up
    'newsprint': (0.82, 0.80, 0.74),   # paper off the presses
    'ink':       (0.03, 0.03, 0.05),   # printer's ink
    'blossom':   (0.93, 0.70, 0.76),   # cherry blossom
    'rust':      (0.72, 0.30, 0.07),   # autumn leaves
    'amberleaf': (0.84, 0.56, 0.12),
    'leafg':     (0.16, 0.30, 0.08),   # summer leaves
    'snow':      (0.90, 0.92, 0.95),
    'concrete':  (0.52, 0.52, 0.50),   # bare, unfinished
    'belt':      (0.10, 0.09, 0.08),   # conveyor rubber / canvas
}
NEW_EMIT = {
    'e_flame': ((1.00, 0.66, 0.30), 9.0),    # candle flames en masse: stays on at night
}
for _k, _v in NEW_MATS.items(): lib.MATS.setdefault(_k, _v)
for _k, _v in NEW_EMIT.items(): lib.EMIT.setdefault(_k, _v)
lib.NIGHT_ON.add('e_flame')


def rng(seed):
    return random.Random(seed)


# ---------------------------------------------------------------------------
# furniture
def typewriter(x, y, a=0.0, z=0.0, body='iron', keys='ivory', paper='newsprint', s=1.0, page=True):
    """An upright office typewriter (a few boxes) on a desk top at z, the typist facing angle a
    (the keyboard toward the typist). Drawn only (nocol)."""
    g = Geo()
    g.add(box(-0.23, -0.17, 0, 0.23, 0.15, 0.07, body, skip=('-z',)))
    g.add(slope_box(-0.17, 0.0, -0.21, 0.21, 0.07, 0.07, 0.10, 0.16, body).xform(math.pi / 2, 0, 0, 0))
    for k in range(3):                                  # three rows of keys
        yk = -0.15 + k * 0.05
        g.add(box(-0.19, yk, 0.10 + k * 0.02, 0.19, yk + 0.03, 0.125 + k * 0.02, keys, skip=('-z',)))
    g.add(box(-0.2, -0.0, 0.07, 0.2, 0.15, 0.2, body, skip=('-z',)))          # the body
    g.add(box(-0.27, 0.07, 0.2, 0.27, 0.15, 0.26, 'black', sides='chrome'))   # the carriage and platen
    g.add(box(-0.3, 0.09, 0.21, -0.27, 0.13, 0.25, 'chrome'))
    if page:
        p = box(-0.105, 0.105, 0.2, 0.105, 0.11, 0.5, paper)
        rot(p, 'x', -0.22, 0, 0.11, 0.24)
        g.add(p)
    if s != 1.0: g.v = [(px * s, py * s, pz * s) for (px, py, pz) in g.v]
    return g.xform(a - math.pi / 2, x, y, z)


def desk(x, y, a=0.0, w=1.1, d=0.66, h=0.76, m='walnut', top='leather'):
    """A plain writing desk centred at (x, y); the sitter faces angle a. Drawers on the left, a panel on the right."""
    g = Geo()
    g.add(box(-d / 2, -w / 2, h - 0.05, d / 2, w / 2, h, m, top=top))
    g.add(box(-d / 2 + 0.03, -w / 2 + 0.02, 0, d / 2 - 0.03, -w / 2 + 0.36, h - 0.05, m, skip=('-z', '+z')))
    g.add(box(-d / 2 + 0.03, w / 2 - 0.06, 0, d / 2 - 0.03, w / 2 - 0.02, h - 0.05, m, skip=('-z', '+z')))
    for k in range(3):   # drawer fronts toward the sitter
        zz = 0.08 + k * 0.22
        g.add(box(-d / 2 - 0.0, -w / 2 + 0.06, zz, -d / 2 + 0.03, -w / 2 + 0.32, zz + 0.17, 'oak', skip=('+x',)))
    return g.xform(a, x, y, 0)


def stool(x, y, a=0.0, m='walnut', seat='leather', back=True):
    g = Geo()
    g.add(box(-0.2, -0.2, 0.42, 0.2, 0.2, 0.47, seat, sides=m))
    g.add(box(-0.18, -0.18, 0, -0.14, 0.18, 0.42, m, skip=('-z', '+z')))
    g.add(box(0.14, -0.18, 0, 0.18, 0.18, 0.42, m, skip=('-z', '+z')))
    if back: g.add(box(-0.22, -0.18, 0.47, -0.18, 0.18, 0.95, m, skip=('-z',)))
    return g.xform(a, x, y, 0)


def sheet(x, y, z, a=0.0, w=0.21, l=0.3, m='newsprint', tilt=0.0):
    """A loose page lying on something."""
    g = box(-l / 2, -w / 2, 0, l / 2, w / 2, 0.004, m, skip=('-z',))
    if tilt: rot(g, 'x', tilt)
    return g.xform(a, x, y, z)


def plank(p0, p1, w=0.25, t=0.05, m='oak'):
    """A flat board between two 3D points (lying flat, w wide)."""
    return beam(p0, p1, w, m, t)


def wheel(cx, cy, cz, r, axis='x', spokes=6, rim=0.08, w=0.12, m='iron', hub=None, segs=20):
    """A spoked wheel (a flywheel, a gear) standing in the plane normal to `axis` ('x' or 'y')."""
    g = Geo()
    g.add(ring(0, 0, -w / 2, w / 2, r - rim, r, segs, top=m, bottom=m, inner=m, outer=m))
    g.add(cyl(0, 0, -w * 0.8, w * 0.8, rim * 1.3, 10, side=hub or m, top=hub or m, bottom=hub or m))
    for k in range(spokes):
        an = 2 * math.pi * k / spokes
        g.add(obox(0, 0, math.cos(an) * (r - rim * 0.5), math.sin(an) * (r - rim * 0.5), -w * 0.3, w * 0.3, rim * 0.6, m))
    # stand it up: the wheel lies in x-y about z; turn its axis to `axis`
    if axis == 'x': rot(g, 'y', math.pi / 2)
    else: rot(g, 'x', math.pi / 2)
    g.v = [(a + cx, b + cy, c + cz) for a, b, c in g.v]
    return g


def gear(cx, cy, cz, r, teeth=16, axis='x', w=0.15, m='brass', spokes=5):
    g = Geo()
    g.add(ring(0, 0, -w / 2, w / 2, r * 0.78, r, max(teeth, 12), top=m, bottom=m, inner=m, outer=m))
    for k in range(teeth):
        an = 2 * math.pi * (k + 0.5) / teeth
        tw = 2 * math.pi * r / teeth * 0.45
        t = box(r - 0.02, -tw / 2, -w / 2, r + r * 0.12, tw / 2, w / 2, m, skip=('-x',))
        g.add(t.xform(an, 0, 0, 0))
    g.add(cyl(0, 0, -w * 0.9, w * 0.9, r * 0.14, 10, side=m, top=m, bottom=m))
    for k in range(spokes):
        an = 2 * math.pi * k / spokes
        g.add(obox(0, 0, math.cos(an) * r * 0.8, math.sin(an) * r * 0.8, -w * 0.3, w * 0.3, r * 0.08, m))
    if axis == 'x': rot(g, 'y', math.pi / 2)
    else: rot(g, 'x', math.pi / 2)
    g.v = [(a + cx, b + cy, c + cz) for a, b, c in g.v]
    return g


def roller(x0, x1, y, z, r, m='iron', segs=14, axis='x'):
    """A horizontal cylinder from x0 to x1 (axis 'x') or y0..y1 (axis 'y', then the first two args are y's and y is x)."""
    g = xcyl(x1 - x0, r, segs, side=m)
    if axis == 'x':
        g.v = [(a + x0, b + y, c + z) for a, b, c in g.v]
    else:
        g.v = [(y + b, a + x0, c + z) for a, b, c in g.v]
    return g


def candles_on(R, x0, y0, x1, y1, z, n, rs, hmin=0.12, hmax=0.4, rmin=0.025, rmax=0.05, m='tallow', fm='e_candle', segs=6):
    """A scatter of candles standing on a surface (drawn only), each with its flame."""
    for _ in range(n):
        x, y = rs.uniform(x0, x1), rs.uniform(y0, y1)
        h, r = rs.uniform(hmin, hmax), rs.uniform(rmin, rmax)
        R.nocol.add(taper(x, y, z, z + h, r, r * 0.9, segs, m))
        flame(R, x, y, z + h + 0.005, r * 0.35, 0.025 + r * 0.9, fm)


def cage_tube(p0, p1, r, m='brass', ribs=6, hoops=None, segs=16, hoop_w=0.06):
    """A 'glass' tube as the library builds one: brass hoops and fine ribs round an open core (drawn)."""
    g = Geo()
    L = math.dist(p0, p1)
    n = hoops if hoops is not None else max(2, int(L / 1.2) + 1)
    for k in range(n):
        t = k / (n - 1)
        h = cyl(0, 0, -hoop_w / 2, hoop_w / 2, r, segs, side=m, caps=False)
        hi = cyl(0, 0, -hoop_w / 2, hoop_w / 2, r - 0.03, segs, side=m, caps=False)
        hi.f = [tuple(reversed(f)) for f in hi.f]; hi.uv = [list(reversed(u)) for u in hi.uv]
        h.add(hi)
        rot(h, 'y', math.pi / 2)
        h.v = [(a + L * t, b, c) for a, b, c in h.v]
        g.add(h)
    for k in range(ribs):
        an = 2 * math.pi * k / ribs
        b = box(0, -0.012, -0.012, L, 0.012, 0.012, m)
        b.v = [(a, bb + math.cos(an) * (r - 0.015), c + math.sin(an) * (r - 0.015)) for a, bb, c in b.v]
        g.add(b)
    return along(g, p0, p1)


def solid_tube(p0, p1, r, m='brass', segs=16, caps=True):
    return along(xcyl(math.dist(p0, p1), r, segs, side=m, caps=caps), p0, p1)


def hall(R, x0=None, y0=None, x1=None, y1=None, h=TOP - 0.1, wall='tile', floor='floor', ceil='plaster', skip=(), z=0.0, level=None):
    """Doorways plus a main hall box, for rooms of any size. When the hall is inset from the shell
    (thick walls), each doorway's tunnel is carried through the extra thickness."""
    W, D = R.W, R.D
    x0 = T if x0 is None else x0; y0 = T if y0 is None else y0
    x1 = W - T if x1 is None else x1; y1 = D - T if y1 is None else y1
    if level is None or level == 0:
        R.sockets(floor=floor, wall=wall, skip=skip)
    R.cut(box(x0 - 0.02, y0 - 0.02, z, x1 + 0.02, y1 + 0.02, z + h, wall, bottom=floor, top=ceil))
    tunnels(R, x0, y0, x1, y1, z=z, floor=floor, wall=wall, skip=skip)


def tunnels(R, x0, y0, x1, y1, z=0.0, floor='floor', wall='tile', skip=()):
    """Carry the doorways on the level at z through walls thicker than the shell, to a hall edge."""
    W, D = R.W, R.D
    L = int(round(z / LH))
    pr = arch_profile(0, DW, 0, DJ)
    for i in range(R.w):
        c = i * C + C / 2
        for side, a, b in (('S', T, y0 + 0.05), ('N', y1 - 0.05, D - T)):
            if (side, i, L) in skip or b - a < 0.62: continue
            R.cut(prism([(p + c, q + z) for p, q in pr], 'y', a, b, arch_mats(len(pr), floor, wall)))
    for j in range(R.d):
        c = j * C + C / 2
        for side, a, b in (('W', T, x0 + 0.05), ('E', x1 - 0.05, W - T)):
            if (side, j, L) in skip or b - a < 0.62: continue
            R.cut(prism([(p + c, q + z) for p, q in pr], 'x', a, b, arch_mats(len(pr), floor, wall)))


# ---------------------------------------------------------------------------
# wax
def wax_spire(R, x, y, z, h, r, rs, m='tallow', col=True, segs=8, lit=True, flame_m='e_candle'):
    """One built-up candle: a tapering column of wax with a guttered lip and a flame on top."""
    g = taper(x, y, z, z + h, r, r * rs.uniform(0.45, 0.7), segs, m)
    (R.parts if col else R.nocol).add(g)
    rt = r * 0.55
    if lit:
        fr = min(0.05, rt * 0.4)
        flame(R, x, y, z + h + 0.01, fr, 0.03 + fr * 2.4, flame_m)


def wax_mound(R, x, y, r, h, rs, n=None, m='tallow', z=0.0, col=True, flames=True):
    """A stalagmite of wax: a lumpy guttered foot, a crowd of spires of different heights leaning into
    each other, drips down their sides, candles burning on every top."""
    foot = lambda: cone(x, y, z, z + min(h * 0.16, 0.45), r, r * 0.72, 12, side=m, top=m, bottom=m)
    (R.parts if col else R.nocol).add(foot())
    for k in range(3):   # lumps round the foot
        a = rs.uniform(0, 2 * math.pi); d = r * rs.uniform(0.55, 0.9)
        R.nocol.add(cone(x + math.cos(a) * d, y + math.sin(a) * d, z, z + rs.uniform(0.12, 0.3), r * 0.35, r * 0.18, 7, side=m, top=m, bottom=m))
    n = n or max(5, int(r * 9))
    wax_spire(R, x, y, z, h, r * 0.32, rs, m, False, 8)
    if col: R.col.add(cyl(x, y, z, z + h * 0.8, r * 0.55, 8, side='tile', top='tile', bottom='tile'))
    for k in range(n):
        a = rs.uniform(0, 2 * math.pi); d = rs.uniform(0.15, 0.8) * r
        hh = h * rs.uniform(0.3, 0.92) * (1 - d / r * 0.55)
        rr = r * rs.uniform(0.1, 0.22)
        wax_spire(R, x + math.cos(a) * d, y + math.sin(a) * d, z, max(0.25, hh), rr, rs, m, False, 6, lit=flames)
        # drips running down the spire: a thin rivulet and a bead at its foot
        if hh > 0.8 and rs.random() < 0.4:
            px, py = x + math.cos(a) * (d + rr * 0.9), y + math.sin(a) * (d + rr * 0.9)
            R.nocol.add(tube([(px, py, z + hh * 0.95), (px + math.cos(a) * 0.02, py + math.sin(a) * 0.02, z + hh * 0.5), (px + math.cos(a) * 0.05, py + math.sin(a) * 0.05, z + hh * rs.uniform(0.1, 0.35))],
                             [0.012, 0.03, 0.04], 4, m))


def icicle(x, y, ztop, L, r, segs=4, m='tallow', a0=0.0):
    """A hanging point: a ring at ztop narrowing to a tip L below (open at the top, a few faces)."""
    g = Geo()
    ring_ = [g.vert((x + r * math.cos(a0 + 2 * math.pi * k / segs), y + r * math.sin(a0 + 2 * math.pi * k / segs), ztop)) for k in range(segs)]
    tip = g.vert((x, y, ztop - L))
    for k in range(segs):
        j = (k + 1) % segs
        g.face([ring_[j], ring_[k], tip], m, [(k * r, 0), ((k + 1) * r, 0), ((k + 0.5) * r, -L)])
    return g


def taper(x, y, z0, z1, r0, r1, segs=5, m='tallow'):
    """An upright tapering stick without a bottom (a candle, a spire): segs sides and a top."""
    g = Geo()
    b = [g.vert((x + r0 * math.cos(2 * math.pi * k / segs), y + r0 * math.sin(2 * math.pi * k / segs), z0)) for k in range(segs)]
    t = [g.vert((x + r1 * math.cos(2 * math.pi * k / segs), y + r1 * math.sin(2 * math.pi * k / segs), z1)) for k in range(segs)]
    for k in range(segs):
        j = (k + 1) % segs
        g.face([b[k], b[j], t[j], t[k]], m, [(k * r0, z0), ((k + 1) * r0, z0), ((k + 1) * r0, z1), (k * r0, z1)])
    g.face(t, m, [(g.v[i][0], g.v[i][1]) for i in t])
    return g


def flame(R, x, y, z, s=0.012, h=0.045, m='e_candle'):
    """A candle flame: a little three-sided point of light."""
    g = Geo()
    b = [g.vert((x + s * 1.2 * math.cos(a), y + s * 1.2 * math.sin(a), z)) for a in (0.3, 2.4, 4.5)]
    t = g.vert((x, y, z + h))
    for k in range(3):
        g.face([b[k], b[(k + 1) % 3], t], m, [(0, 0), (s, 0), (s / 2, h)])
    g.face([b[2], b[1], b[0]], m, [(0, 0), (s, 0), (s / 2, s)])
    R.light(g)


def drips(R, x0, y0, x1, y1, z, n, rs, Lmin=0.08, Lmax=0.9, rmin=0.02, rmax=0.07, m='tallow', segs=4):
    """Wax hanging in icicles from an edge between two points at height z (drawn only)."""
    for _ in range(n):
        t = rs.random()
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        L = Lmin + (Lmax - Lmin) * rs.random() ** 2
        r = rs.uniform(rmin, rmax) * (1 + L)
        R.nocol.add(icicle(x, y, z + 0.02, L + 0.02, r, segs, m, rs.uniform(0, 1.5)))


def wax_fall(R, y0, y1, xb, ztop, rs, depth=0.35, bulge=0.5, foot=0.9, face=1, m='tallow', col=True, n=14, zbot=0.0):
    """A frozen waterfall of wax down a wall facing +x (face=1) or -x (face=-1): a rippled sheet whose
    back stands at x=xb, bulging out as it falls, with a pooled foot on the floor."""
    rings = []
    zs = [ztop, ztop - 0.4, ztop * 0.7, ztop * 0.45, ztop * 0.22, 0.5, 0.18, zbot]
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        e = math.sin(math.pi * k / n) ** 0.5                     # thin at the edges
        rip = 0.09 * math.sin(y * 6.3 + 1.3) + 0.05 * math.sin(y * 13.1)
        front = []
        for j, z in enumerate(zs):
            f = (ztop - z) / max(ztop - zbot, 1e-6)
            out = depth * 0.3 + bulge * f ** 1.5 + (foot if j == len(zs) - 1 else foot * 0.45 if j == len(zs) - 2 else 0)
            front.append((xb + face * (0.02 + e * out + rip * e), y, z))
        back = [(xb, y, zbot), (xb, y, ztop)]
        rings.append(front + back)
    g = loft(rings, m, caps=True)
    (R.parts if col else R.nocol).add(g)
    # rivulets down its face: ridges following the front, fattening as they fall
    for k in range(1, n):
        for off in ((0.0,) if k % 2 else ()):
            kk = k + off
            if kk >= n: continue
            i0, i1 = int(kk), min(n, int(kk) + 1)
            t = kk - i0
            fr = [tuple(a[q] + (b[q] - a[q]) * t for q in range(3)) for a, b in zip(rings[i0][:len(zs)], rings[i1][:len(zs)])]
            L = rs.randint(3, len(zs) - 1)
            pts = [(p[0] + face * 0.02, p[1], p[2]) for p in fr[:L + 1]]
            R.nocol.add(tube(pts, [0.05 + 0.1 * j / len(pts) * rs.uniform(0.6, 1.3) for j in range(len(pts))], 5, m, caps=True))
    # icicles off the lip at the top
    drips(R, xb + face * 0.1, y0, xb + face * 0.1, y1, ztop, int((y1 - y0) * 5), rs, 0.1, 0.6)
    return g


# ---------------------------------------------------------------------------
# trees and ground litter
def tree(R, x, y, h, cr, rs, bark='walnut', leaf=('leafg',), snow=False, bare=False, z=0.0, n=6, puff=0.9, col=True, flat=0.6):
    """A tree: a trunk, n limbs spreading from the top of the bole, a crown of leaf clusters at the limb
    ends (or bare twigs, snow along their tops). The trunk is collided, the rest drawn."""
    bole = h * 0.45
    R.nocol.add(tube([(x, y, z), (x + rs.uniform(-0.1, 0.1), y + rs.uniform(-0.1, 0.1), z + bole * 0.5), (x, y, z + bole)], [0.24, 0.2, 0.17], 8, bark))
    if col: R.col.add(box(x - 0.2, y - 0.2, z, x + 0.2, y + 0.2, z + bole, 'tile'))
    g = Geo()
    tips = []
    for k in range(n):
        a = 2 * math.pi * k / n + rs.uniform(-0.3, 0.3)
        d = (math.cos(a) * 0.8, math.sin(a) * 0.8, rs.uniform(0.6, 1.1))
        L = math.hypot(cr * 0.8, h - bole) * rs.uniform(0.55, 0.8)
        if bare:
            branches(g, (x, y, z + bole - 0.1), d, L * 0.6, 0.12, 2, rs, bark, 5, 2, 0.8, 0.25, 0.7, 0.5, 0.2)
        else:
            end = (x + d[0] * L * 0.7, y + d[1] * L * 0.7, z + bole + d[2] * L * 0.55)
            g.add(tube(curve((x, y, z + bole - 0.1), end, (0, 0, 0.2), 4), [0.13, 0.1, 0.07, 0.05], 5, bark))
            tips.append(end)
    R.nocol.add(g)
    if snow:
        # snow lying along the limbs: pale boxes on the upper side of every branch segment
        s = Geo()
        for i in range(0, len(g.f), 5):
            f = g.f[i]
            p = [g.v[j] for j in f]
            cx, cy, cz = sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p), max(q[2] for q in p)
            if rs.random() < 0.35: s.add(box(cx - 0.07, cy - 0.07, cz - 0.01, cx + 0.07, cy + 0.07, cz + 0.035, 'snow', skip=('-z',)))
        R.nocol.add(s)
    for k, (tx, ty, tz) in enumerate(tips):
        R.nocol.add(puffs(tx, ty, tz, puff * rs.uniform(0.75, 1.05), 3, leaf[k % len(leaf)], seed=rs.randint(0, 9999), flat=flat, segs=9, rings=4))
    if tips and not bare:
        R.nocol.add(puffs(x, y, z + h - puff * 0.6, puff * 1.15, 5, leaf[0], seed=rs.randint(0, 9999), flat=flat, segs=9, rings=4))


def litter(R, x0, y0, x1, y1, n, rs, mats=('rust',), z=0.0, s=(0.05, 0.1), skip=None, t=0.004):
    """Leaves, petals or pages lying scattered on a floor (drawn only): one upward face each."""
    g = Geo()
    for _ in range(n):
        x, y = rs.uniform(x0, x1), rs.uniform(y0, y1)
        if skip and skip(x, y): continue
        a = rs.uniform(0, math.pi); w = rs.uniform(*s)
        q = Geo(); zz = z + t + rs.uniform(0.0, 0.01)
        ids = [q.vert(p) for p in ((-w, -w * 0.6, zz), (w, -w * 0.6, zz), (w, w * 0.6, zz), (-w, w * 0.6, zz))]
        q.face(ids, rs.choice(mats), [(0, 0), (w, 0), (w, w), (0, w)])
        g.add(q.xform(a, x, y, 0))
    R.nocol.add(g)


def blade(x, y, z, h, w, a, m, lean=0.0):
    """A two-sided vertical sliver (a grass blade, a hanging page): two faces."""
    g = Geo()
    c, s_ = math.cos(a) * w / 2, math.sin(a) * w / 2
    P = [(x - c, y - s_, z), (x + c, y + s_, z), (x + c + lean, y + s_, z + h), (x - c + lean, y - s_, z + h)]
    ids = [g.vert(p) for p in P]
    g.face(ids, m, [(0, 0), (w, 0), (w, h), (0, h)])
    g.face(list(reversed(ids)), m, [(0, h), (w, h), (w, 0), (0, 0)])
    return g
