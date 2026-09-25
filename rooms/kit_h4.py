"""Shared helpers for batch 4 of the Deep Stacks (water, ice and growth): waterfallstair, frozenwave,
breathinghall, rootcellar, orchard, coralarchive, mosscathedral, hive.

Organic things (roots, coral, branches, ribs, drips) are swept tubes along short polylines; ice and
wax masses are lofts between a few hand-drawn profiles. A few materials the library palette lacks
(moss, ice, coral, wax, honey, pale root, bark, leaf, grass) are added here: the room file carries its
albedo table, and the game draws any material it does not know as smooth paint of that colour."""
from lib import *
import lib
import random

# ---------------------------------------------------------------------------
# extra materials (albedo) and emitters, registered with the kit so the bake and the export see them
NEW_MATS = {
    'moss':   (0.10, 0.18, 0.05),   # thick green moss
    'mossdk': (0.06, 0.11, 0.035),   # moss in shadow / hanging strands
    'ice':    (0.34, 0.74, 0.78),   # turquoise ice
    'icedk':  (0.12, 0.46, 0.54),   # deep ice
    'coral':  (0.90, 0.36, 0.42),   # pink coral
    'coralw': (0.92, 0.88, 0.82),   # white coral
    'wax':    (0.86, 0.58, 0.16),   # golden comb wax
    'honey':  (0.78, 0.42, 0.04),   # dripping honey
    'root':   (0.78, 0.72, 0.60),   # pale roots
    'bark':   (0.30, 0.23, 0.16),
    'leaf':   (0.12, 0.25, 0.06),
    'grass':  (0.14, 0.26, 0.07),
    'foam':   (0.86, 0.92, 0.94),   # falling water
}
NEW_EMIT = {
    'e_ice':   ((0.40, 0.90, 1.00), 2.4),   # light inside ice
    'e_honey': ((1.00, 0.62, 0.18), 7.0),   # light through wax
    'e_deep':  ((0.25, 0.55, 1.00), 5.0),   # sea light
    'e_glow':  ((0.30, 0.65, 1.00), 3.0),   # bioluminescence: stays on at night
}
for _k, _v in NEW_MATS.items(): lib.MATS.setdefault(_k, _v)
for _k, _v in NEW_EMIT.items(): lib.EMIT.setdefault(_k, _v)
lib.NIGHT_ON.add('e_glow')

from kit_a import rot, beam, obox, stair_rail, chair as _chair, table as _table, desk_lamp, candle, floor_lamp, navloop, tidy, bulb
from kit_a import shelf as lshelf, sh, rail as arail
from kit_f import bar, rail_line, balus, rect_rails
from kit_e import ellipsoid, lathe


# ---------------------------------------------------------------------------
# vectors
def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _norm(a):
    L = math.sqrt(_dot(a, a)) or 1e-9
    return (a[0] / L, a[1] / L, a[2] / L)


def tube(pts, r, segs=8, m='root', caps=True, twist=0.0):
    """A tube swept along a 3D polyline (parallel-transport frames). r: one radius or one per point."""
    n = len(pts)
    rs = list(r) if isinstance(r, (list, tuple)) else [r] * n
    T_ = []
    for i in range(n):
        a = pts[max(0, i - 1)]; b = pts[min(n - 1, i + 1)]
        T_.append(_norm(_sub(b, a)))
    t0 = T_[0]
    ref = (0, 0, 1) if abs(t0[2]) < 0.9 else (1, 0, 0)
    nr = _norm(_cross(_cross(t0, ref), t0))
    g = Geo(); rings = []
    s = 0.0; ss = [0.0]
    for i in range(1, n): s += math.sqrt(_dot(_sub(pts[i], pts[i - 1]), _sub(pts[i], pts[i - 1]))); ss.append(s)
    for i in range(n):
        t = T_[i]
        nr = _norm(_sub(nr, _mul(t, _dot(nr, t))))
        bn = _cross(t, nr)
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs + twist * i
            d = _add(_mul(nr, math.cos(a)), _mul(bn, math.sin(a)))
            ring.append(g.vert(_add(pts[i], _mul(d, rs[i]))))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(segs):
            j = (k + 1) % segs
            u0, u1 = k / segs * 2 * math.pi * rs[i], (k + 1) / segs * 2 * math.pi * rs[i]
            g.face([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]], m, [(u0, ss[i]), (u1, ss[i]), (u1, ss[i + 1]), (u0, ss[i + 1])])
    if caps:
        g.face(list(reversed(rings[0])), m, [(0, 0)] * segs)
        g.face(list(rings[-1]), m, [(0, 0)] * segs)
        return g.fix()
    return g


def curve(p0, p1, bend=(0, 0, 0), n=5, sag=0.0):
    """Points from p0 to p1 bowed by `bend` (a vector, at the middle) and sagging by `sag` (down)."""
    out = []
    for k in range(n):
        t = k / (n - 1); w = 4 * t * (1 - t)
        out.append((p0[0] + (p1[0] - p0[0]) * t + bend[0] * w, p0[1] + (p1[1] - p0[1]) * t + bend[1] * w,
                    p0[2] + (p1[2] - p0[2]) * t + bend[2] * w - sag * w))
    return out


def loft(rings, m='ice', caps=True, cap_m=None):
    """Skin a list of closed rings (lists of 3D points, all the same length) with quads, capping the ends."""
    g = Geo(); ids = []
    for ring in rings: ids.append([g.vert(p) for p in ring])
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            a, b = rings[i][k], rings[i + 1][k]
            g.face([ids[i][k], ids[i][j], ids[i + 1][j], ids[i + 1][k]], m,
                   [(a[0] + a[1], a[2]), (rings[i][j][0] + rings[i][j][1], rings[i][j][2]), (rings[i + 1][j][0] + rings[i + 1][j][1], rings[i + 1][j][2]), (b[0] + b[1], b[2])])
    if caps:
        cm = cap_m or m
        g.face(list(reversed(ids[0])), cm, [(p[0], p[2]) for p in reversed(rings[0])])
        g.face(list(ids[-1]), cm, [(p[0], p[2]) for p in rings[-1]])
        return g.fix()
    return g


def blob(cx, cy, cz, rx, ry, rz, m='coral', segs=10, rings=6, ang=0.0):
    g = ellipsoid(0, 0, 0, rx, ry, rz, m, segs, rings)
    return g.xform(ang, cx, cy, cz)


def cone(x, y, z0, z1, r0, r1, segs=6, m='honey'):
    """A tapered upright (or hanging, z1 < z0) spike from radius r0 at z0 to r1 at z1."""
    lo, hi = (z0, z1) if z0 < z1 else (z1, z0)
    ra, rb = (r0, r1) if z0 < z1 else (r1, r0)
    return lathe(x, y, [(0.0, lo), (max(ra, 0.004), lo), (max(rb, 0.004), hi), (0.0, hi)], segs, m)


def branches(g, p, d, L, r, depth, rnd, m='coral', segs=6, kids=2, spread=0.7, up=0.35, shrink=0.72, rshrink=0.62, wob=0.25, tip=None):
    """Recursive branching growth (coral, twigs, roots): a bent tube from p along d, then `kids` branches."""
    d = _norm(d)
    perp = _norm(_cross(d, (0, 0, 1) if abs(d[2]) < 0.95 else (1, 0, 0)))
    bendv = _mul(_add(_mul(perp, rnd.uniform(-1, 1)), _mul(_cross(d, perp), rnd.uniform(-1, 1))), L * wob)
    end = _add(p, _mul(d, L))
    pts = curve(p, end, bendv, 4)
    r1 = r * rshrink if depth > 0 else (tip if tip is not None else r * 0.35)
    g.add(tube(pts, [r + (r1 - r) * k / 3 for k in range(4)], segs, m))
    if depth <= 0: return
    dd = _norm(_sub(pts[-1], pts[-2]))
    for k in range(kids):
        rv = (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))
        nd = _norm(_add(_add(dd, _mul(_norm(_sub(rv, _mul(dd, _dot(rv, dd)))), spread)), (0, 0, up)))
        branches(g, pts[-1], nd, L * shrink * rnd.uniform(0.8, 1.15), r1, depth - 1, rnd, m, max(4, segs - 1), kids, spread, up, shrink, rshrink, wob, tip)


def hexpts(cx, cz, r, flat=True, a0=None):
    """Hexagon corners (p, z) round (cx, cz): flat=True puts a flat edge at the bottom (a floor)."""
    a0 = (0.0 if flat else math.pi / 6) if a0 is None else a0
    return [(cx + r * math.cos(a0 + k * math.pi / 3), cz + r * math.sin(a0 + k * math.pi / 3)) for k in range(6)]


# ---------------------------------------------------------------------------
# furniture and fittings (thin wrappers so every room uses the same pieces)
def chair(R, x, y, face, z=0.0, frame='walnut', seat='leather', spot=True):
    R.parts.add(_chair(0, 0, face, frame, seat).xform(0, x, y, z))
    if spot: R.spot('sit', x, y, z + 0.48, face)


def table(R, x0, y0, x1, y1, z=0.0, h=0.76, m='walnut', top=None):
    R.parts.add(_table(x0, y0, x1, y1, h, m, top).xform(0, 0, 0, z))


def open_book(R, x, y, z, ang=0.0, m='leather'):
    g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, m)
    g.add(box(-0.19, -0.13, 0.02, -0.005, 0.13, 0.05, 'ivory'))
    g.add(box(0.005, -0.13, 0.02, 0.19, 0.13, 0.05, 'ivory'))
    R.nocol.add(g.xform(ang, x, y, z))


BOOKM = ('oxblood', 'green', 'leather', 'walnut', 'velvet', 'ivory', 'slate')


def book(x, y, z, ang=0.0, m='leather', w=0.17, l=0.25, t=0.05, tilt=0.0, rnd=None):
    """A closed book lying (or, with tilt, leaning); returns Geo (add to nocol)."""
    g = box(-l / 2, -w / 2, 0, l / 2, w / 2, t, m)
    g.add(box(-l / 2 + 0.01, -w / 2 + 0.01, 0.006, l / 2 - 0.003, w / 2 - 0.01, t - 0.006, 'ivory'))
    if tilt: rot(g, 'x', tilt)
    return g.xform(ang, x, y, z)


def book_pile(R, x, y, z, n, rnd, ang=0.0):
    g = Geo(); h = 0.0
    for i in range(n):
        t = rnd.uniform(0.035, 0.07)
        g.add(book(0, 0, h, rnd.uniform(-0.3, 0.3), rnd.choice(BOOKM), rnd.uniform(0.14, 0.2), rnd.uniform(0.2, 0.3), t))
        h += t
    R.nocol.add(g.xform(ang, x, y, z))
    return h


def green_lamp(R, x, y, z):
    desk_lamp(R, x, y, z)


def post_lamp(R, x, y, z=0.0, h=2.6, m='e_amber', pole='iron'):
    R.parts.add(cyl(x, y, z, z + 0.12, 0.16, 10, side=pole, top=pole, bottom=pole))
    R.parts.add(cyl(x, y, z + 0.12, z + h, 0.035, 6, side=pole, caps=False))
    R.light(sphere(x, y, z + h + 0.14, 0.15, 10, 5, m))


def sconce(R, x, y, z, face, m='e_lamp', r=0.1):
    """A small wall lamp: a brass arm out from the wall toward `face` (radians) and a glowing globe."""
    dx, dy = math.cos(face), math.sin(face)
    R.nocol.add(beam((x, y, z - 0.15), (x + dx * 0.3, y + dy * 0.3, z - 0.05), 0.03, 'brass'))
    R.nocol.add(cyl(x, y, z - 0.3, z + 0.0, 0.06, 8, side='brass', top='brass', bottom='brass'))
    R.light(sphere(x + dx * 0.32, y + dy * 0.32, z + 0.05, r, 8, 4, m))


def ladder_up(R, x, y, z0, z1, dirn, w=0.62, m='oak', rail='brass', ang=math.radians(60), visual=True):
    """A steep ladder you can walk up: rungs and stiles, over an invisible ramp at `ang`.
    (x, y) is the middle of its foot; dirn '+x','-x','+y','-y' the way it climbs."""
    H = z1 - z0; L = H / math.tan(ang)
    a = {'+x': 0.0, '+y': math.pi / 2, '-x': math.pi, '-y': -math.pi / 2}[dirn]
    g = Geo()
    if visual:
        for s in (-w / 2, w / 2):
            g.add(beam((0, s, z0 - 0.02), (L + 0.12, s, z1 + 0.95), 0.06, m, 0.05))
        n = int(H / 0.28)
        for k in range(1, n + 1):
            t = k / (n + 0.4)
            g.add(box(L * t - 0.025, -w / 2, z0 + H * t - 0.02, L * t + 0.025, w / 2, z0 + H * t + 0.02, rail))
        R.nocol.add(g.xform(a, x, y, 0))
    c = Geo()
    q = [(-0.02, -w / 2 - 0.05, z0), (L, -w / 2 - 0.05, z1), (L, w / 2 + 0.05, z1), (-0.02, w / 2 + 0.05, z0)]
    ids = [c.vert(p) for p in q]; c.face(ids, 'floor', [(0, 0)] * 4)
    if dirn in ('-x', '+y'): pass
    c.xform(a, x, y, 0)
    A = _sub(c.v[1], c.v[0]); B = _sub(c.v[2], c.v[0])
    if _cross(A, B)[2] < 0: c.f = [tuple(reversed(f)) for f in c.f]
    R.col.add(c)
    # side walls so nobody walks off the ramp's edge halfway up
    for s in (-w / 2 - 0.08, w / 2 + 0.08):
        R.col.add(beam((0, s, z0 + 0.2), (L, s, z1 + 0.2), 0.04, 'tile', 1.0).xform(a, x, y, 0))
    return L


def ramp(R, pts):
    """An invisible walking surface (4 corners), made to face up."""
    g = Geo(); ids = [g.vert(p) for p in pts]; g.face(ids, 'floor', [(0, 0)] * 4)
    A = _sub(pts[1], pts[0]); B = _sub(pts[2], pts[0])
    if _cross(A, B)[2] < 0: g.f = [tuple(reversed(f)) for f in g.f]
    R.col.add(g)


def moss_slab(R, x0, y0, x1, y1, z, t=0.08, over=0.05, drape=0.0, rnd=None, m='moss', col=False):
    """A cushion of moss on a flat top (a little proud of its edges), optional strands hanging off it."""
    g = box(x0 - over, y0 - over, z, x1 + over, y1 + over, z + t, m)
    (R.parts if col else R.nocol).add(g)
    if drape > 0 and rnd is not None:
        for (ax, ay, bx, by, nx, ny) in ((x0, y0 - over, x1, y0 - over, 0, -1), (x0, y1 + over, x1, y1 + over, 0, 1)):
            L = math.hypot(bx - ax, by - ay); n = int(L / 0.35)
            for k in range(n):
                if rnd.random() < 0.45: continue
                t_ = (k + rnd.random()) / max(1, n)
                px, py = ax + (bx - ax) * t_, ay + (by - ay) * t_
                d = drape * rnd.uniform(0.3, 1.0)
                R.nocol.add(box(px - 0.05, py - 0.02 * ny - 0.01, z - d, px + 0.05, py + 0.01, z + t, 'mossdk' if rnd.random() < 0.5 else m))


def strands(R, x0, y0, x1, y1, z, n, L, rnd, m='mossdk', w=0.07):
    """Hanging strands (moss, roots) along a line at height z."""
    for k in range(n):
        t = (k + rnd.random()) / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d = L * rnd.uniform(0.3, 1.0)
        R.nocol.add(box(x - w / 2, y - w / 2, z - d, x + w / 2, y + w / 2, z, m, skip=('+z',)))


def secret(R, x, y, z, name, text, r=1.6):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, box_, **kw):
    d = {'type': kind, 'box': [round(v, 2) for v in box_]}; d.update(kw)
    R.meta.setdefault('fx', []).append(d)


def water(R, x0, y0, x1, y1, top, bot):
    R.water.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, top=top, bot=bot))


def rwater(R, cx, cy, r, top, bot):
    R.water.append(dict(cx=cx, cy=cy, r=r, top=top, bot=bot))


def pillar(R, x, y, z0, z1, r=0.35, m='tile', segs=16, base=True, cap=True):
    R.parts.add(cyl(x, y, z0, z1, r, segs, side=m, caps=False))
    if base: R.parts.add(box(x - r - 0.12, y - r - 0.12, z0, x + r + 0.12, y + r + 0.12, z0 + 0.3, m, skip=('-z',)))
    if cap: R.parts.add(box(x - r - 0.14, y - r - 0.14, z1 - 0.3, x + r + 0.14, y + r + 0.14, z1, m))


def row_case(R, x, y, z, length, dirn, row_h=0.42, depth=0.34, frame='walnut', top=False, solid=True, ends=False, back=True):
    """One row of books on its own board: bottom board, back, optional top board and end boards, and
    the slab the game fills. Stack these (each offset as you like) for warped or leaning bookcases."""
    a = {'+y': math.pi / 2, '-y': -math.pi / 2, '+x': 0.0, '-x': math.pi}[dirn] if isinstance(dirn, str) else dirn
    th = a - math.pi / 2
    bd = 0.035
    g = Geo()
    g.add(box(0, 0.0, 0, length, depth + 0.01, bd, frame))
    if back: g.add(box(0, 0, bd, length, 0.02, row_h, frame, skip=('-z', '+z')))
    if top: g.add(box(0, 0.0, row_h, length, depth + 0.01, row_h + bd, frame))
    if ends:
        for (x0, x1) in ((-0.04, 0.0), (length, length + 0.04)):
            g.add(box(x0, 0, 0, x1, depth + 0.02, row_h + (bd if top else 0.0), frame))
    g.xform(th, x, y, z)
    R.nocol.add(g)
    if solid: R.col.add(box(-0.02, 0, 0, length + 0.02, depth + 0.02, row_h, 'tile').xform(th, x, y, z))
    c, s_ = math.cos(th), math.sin(th)
    rot_ = lambda p: (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c, p[2])
    h0 = bd; h1 = row_h - 0.03
    o = rot_((0, depth - 0.02, h0)); o = (o[0] + x, o[1] + y, o[2] + z)
    R.slabs.append({'o': o, 'u': list(rot_((length, 0, 0))), 'v': [0, 0, h1 - h0], 'n': [math.cos(a), math.sin(a), 0],
                    'len': length, 'h': h1 - h0, 'depth': depth - 0.04, 'ghost': not solid})
    return len(R.slabs) - 1
