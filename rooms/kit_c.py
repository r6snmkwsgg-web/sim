"""Helpers shared by batch "c" rooms (furniture, rails, lamps, arches, wall runs)."""
from lib import *

D1, D2 = C / 2 - 2.2, C / 2 + 2.2          # wall stretches either side of a door: (0.6, D1), (D2, C - 0.6)


def shell(R, H=TOP, floor='floor', wall='tile', ceil='plaster', inset=T):
    H = min(H, TOP - 0.1)          # never cut through the top of the block
    R.cut(box(inset - 0.02, inset - 0.02, 0, C - inset + 0.02, C - inset + 0.02, H, wall, bottom=floor, top=ceil))


def wall_shelves(R, rows=7, frame='wood', z=0.0, a=0.6, b=D1, sides='SNWE', **kw):
    """Bookcases along the four walls either side of the doors."""
    for (p, q) in ((a, b), (C - b, C - a)):
        L = q - p
        if 'S' in sides: R.shelf(p, T, z, L, '+y', rows=rows, frame=frame, **kw)
        if 'N' in sides: R.shelf(q, C - T, z, L, '-y', rows=rows, frame=frame, **kw)
        if 'W' in sides: R.shelf(T, q, z, L, '+x', rows=rows, frame=frame, **kw)
        if 'E' in sides: R.shelf(C - T, p, z, L, '-x', rows=rows, frame=frame, **kw)


def shelf_line(R, x0, y0, x1, y1, z, rows, frame='wood', **kw):
    """A bookcase whose back runs from (x0,y0) to (x1,y1); it faces to the LEFT of that direction."""
    L = math.hypot(x1 - x0, y1 - y0)
    a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    return R.shelf(x0, y0, z, L, a, rows=rows, frame=frame, **kw)


def rail(R, x0, y0, x1, y1, z=0.0, h=0.95, m='brass', gap=1.1, mid=True, col=True, post='brass'):
    """A brass handrail on posts (at most `gap` apart) with an invisible wall under it."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1e-3: return
    a = math.atan2(y1 - y0, x1 - x0)
    g = Geo()
    g.add(box(-0.02, -0.03, h - 0.06, L + 0.02, 0.03, h, m))
    if mid: g.add(box(0, -0.012, 0.45, L, 0.012, 0.47, m))
    n = max(1, int(math.ceil(L / gap)))
    for k in range(n + 1):
        s = L * k / n
        g.add(box(s - 0.02, -0.02, 0, s + 0.02, 0.02, h - 0.06, post, skip=('-z',)))
    R.parts.add(g.xform(a, x0, y0, z))
    if col: R.col.add(box(0, -0.05, 0, L, 0.05, h + 0.05, 'tile').xform(a, x0, y0, z))


def rail_poly(R, pts, z=0.0, **kw):
    for p, q in zip(pts, pts[1:]): rail(R, p[0], p[1], q[0], q[1], z, **kw)


def hang_lamp(R, x, y, z, ceil, r=0.16, m='e_lamp', rod='brass', cap=True):
    R.light(sphere(x, y, z, r, 10, 5, m))
    R.parts.add(cyl(x, y, z + r * 0.8, ceil + 0.05, 0.012, 4, side=rod, caps=False))
    if cap: R.parts.add(cyl(x, y, z + r * 0.7, z + r * 1.1, r * 0.55, 8, side=rod, top=rod, bottom=rod))


def pendant(R, x, y, z, ceil, r=0.3, m='e_lamp', shade='brass'):
    """A wide lamp with a brass shade over a glowing disc."""
    R.parts.add(cyl(x, y, z + 0.05, z + 0.3, r, 16, side=shade, top=shade, bottom=shade, caps=False))
    R.parts.add(cyl(x, y, z + 0.3, z + 0.34, r * 0.3, 10, side=shade, top=shade, bottom=shade))
    R.light(cyl(x, y, z + 0.05, z + 0.1, r * 0.92, 16, side=m, top=m, bottom=m))
    R.parts.add(cyl(x, y, z + 0.34, ceil + 0.05, 0.012, 6, side='iron', caps=False))


def table(R, x0, y0, x1, y1, h=0.76, m='walnut', top=None):
    R.parts.add(box(x0, y0, h - 0.06, x1, y1, h, top or m, sides=m, bottom=m))
    i = 0.08
    for (x, y) in ((x0 + i, y0 + i), (x1 - i, y0 + i), (x1 - i, y1 - i), (x0 + i, y1 - i)):
        R.parts.add(box(x - 0.04, y - 0.04, 0, x + 0.04, y + 0.04, h - 0.06, m, skip=('-z', '+z')))


def table_at(R, x0, y0, x1, y1, z, h=0.76, m='walnut', top=None):
    R.parts.add(box(x0, y0, z + h - 0.06, x1, y1, z + h, top or m, sides=m, bottom=m))
    i = 0.08
    for (x, y) in ((x0 + i, y0 + i), (x1 - i, y0 + i), (x1 - i, y1 - i), (x0 + i, y1 - i)):
        R.parts.add(box(x - 0.04, y - 0.04, z, x + 0.04, y + 0.04, z + h - 0.06, m, skip=('-z', '+z')))


def chair(R, x, y, face, z=0.0, m='walnut', seat='leather', spot=True):
    """A chair whose sitter looks toward angle `face`."""
    g = Geo()
    g.add(box(-0.22, -0.22, 0.42, 0.22, 0.22, 0.48, seat, sides=m, bottom=m))
    for (a, b) in ((-0.18, -0.18), (0.18, -0.18), (0.18, 0.18), (-0.18, 0.18)):
        g.add(box(a - 0.025, b - 0.025, 0, a + 0.025, b + 0.025, 0.42, m, skip=('-z', '+z')))
    g.add(box(-0.24, -0.22, 0.48, -0.19, 0.22, 1.0, m))
    R.parts.add(g.xform(face, x, y, z))
    if spot: R.spot('sit', x, y, z + 0.46, face)


def armchair(R, x, y, face, z=0.0, m='walnut', cloth='velvet', spot=True):
    g = Geo()
    g.add(box(-0.4, -0.42, 0.0, 0.4, 0.42, 0.44, cloth, sides=m, skip=('-z',)))
    g.add(box(-0.4, -0.42, 0.44, -0.22, 0.42, 1.05, cloth))
    g.add(box(-0.22, -0.42, 0.44, 0.4, -0.3, 0.68, cloth))
    g.add(box(-0.22, 0.3, 0.44, 0.4, 0.42, 0.68, cloth))
    R.parts.add(g.xform(face, x, y, z))
    if spot: R.spot('sit', x, y, z + 0.46, face)


def desk_lamp(R, x, y, z, shade='green', m='e_lamp'):
    R.parts.add(cyl(x, y, z, z + 0.03, 0.09, 8, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(x, y, z + 0.03, z + 0.38, 0.014, 4, side='brass', caps=False))
    R.parts.add(cyl(x, y, z + 0.38, z + 0.48, 0.19, 10, side=shade, top=shade, bottom=shade, caps=False))
    R.light(cyl(x, y, z + 0.37, z + 0.4, 0.14, 10, side=m, top=m, bottom=m))


def candle(R, x, y, z, h=0.25, r=0.03, m='e_candle'):
    R.parts.add(cyl(x, y, z, z + h, r, 6, side='ivory', top='ivory', bottom='ivory'))
    R.light(sphere(x, y, z + h + 0.035, 0.025, 5, 3, m))


def candle_stand(R, x, y, z=0.0, h=1.3):
    R.parts.add(cyl(x, y, z, z + 0.04, 0.16, 10, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(x, y, z + 0.04, z + h, 0.022, 6, side='brass', caps=False))
    R.parts.add(cyl(x, y, z + h, z + h + 0.03, 0.08, 10, side='brass', top='brass', bottom='brass'))
    candle(R, x, y, z + h + 0.03, 0.22, 0.035)


def lectern(R, x, y, face, z=0.0, m='walnut', book=True):
    """A lectern whose reader stands looking toward `face`."""
    g = Geo()
    g.add(box(-0.25, -0.3, 0, 0.25, 0.3, 0.06, m))
    g.add(box(-0.08, -0.12, 0.06, 0.08, 0.12, 1.0, m))
    # sloped desk: a wedge
    s = Geo()
    ids = [s.vert(p) for p in ((-0.3, -0.34, 1.0), (0.12, -0.34, 1.0), (0.12, 0.34, 1.0), (-0.3, 0.34, 1.0),
                               (-0.3, -0.34, 1.02), (0.12, -0.34, 1.26), (0.12, 0.34, 1.26), (-0.3, 0.34, 1.02))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        s.face([ids[i] for i in f], m, [(0, 0), (1, 0), (1, 1), (0, 1)])
    g.add(s.fix())
    R.parts.add(g.xform(face + math.pi, x, y, z))
    if book:
        b = Geo()
        ids = [b.vert(p) for p in ((-0.24, -0.26, 1.045), (0.08, -0.26, 1.235), (0.08, 0.26, 1.235), (-0.24, 0.26, 1.045),
                                   (-0.24, -0.26, 1.075), (0.08, -0.26, 1.265), (0.08, 0.26, 1.265), (-0.24, 0.26, 1.075))]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            b.face([ids[i] for i in f], 'ivory' if f == (4, 5, 6, 7) else 'leather', [(0, 0), (1, 0), (1, 1), (0, 1)])
        R.parts.add(b.fix().xform(face + math.pi, x, y, z))
    R.spot('read', x - math.cos(face) * 0.6, y - math.sin(face) * 0.6, z, face)


def open_book(R, x, y, z, ang=0.0):
    g = Geo()
    g.add(box(-0.17, -0.12, 0, 0.17, 0.12, 0.012, 'leather'))
    g.add(box(-0.16, -0.11, 0.012, -0.005, 0.11, 0.03, 'ivory'))
    g.add(box(0.005, -0.11, 0.012, 0.16, 0.11, 0.03, 'ivory'))
    R.parts.add(g.xform(ang, x, y, z))


def book_pile(R, x, y, z, n=5, seed=0, w=0.26, d=0.19):
    import random
    rnd = random.Random(seed)
    zz = z
    for k in range(n):
        h = rnd.uniform(0.03, 0.06)
        a = rnd.uniform(-0.5, 0.5)
        m = rnd.choice(('leather', 'oxblood', 'green', 'walnut', 'velvet'))
        ww, dd = w * rnd.uniform(0.8, 1.15), d * rnd.uniform(0.8, 1.15)
        R.parts.add(box(-ww / 2, -dd / 2, 0, ww / 2, dd / 2, h, m).xform(a, x + rnd.uniform(-0.02, 0.02), y + rnd.uniform(-0.02, 0.02), zz))
        zz += h


def rug(R, x0, y0, x1, y1, z=0.0, m='carpet', border='oxblood'):
    R.parts.add(box(x0, y0, z, x1, y1, z + 0.012, border, skip=('-z',)))
    R.parts.add(box(x0 + 0.15, y0 + 0.15, z + 0.012, x1 - 0.15, y1 - 0.15, z + 0.016, m, skip=('-z',)))


def navloop(R, pts, z=0.0, close=True):
    ids = [R.navpt(x, y, z) for (x, y) in pts]
    R.link(*(ids + [ids[0]] if close else ids))
    return ids


def std_nav(R, e=2.0):
    return navloop(R, ((e, e), (8, e), (C - e, e), (C - e, 8), (C - e, C - e), (8, C - e), (e, C - e), (e, 8)))


def arch_ring(axis, a0, a1, c, w, zs, t, m='tile', segs=12, top=None):
    """Voussoirs of a round arch (radius w/2, springing at zs) as convex quad prisms along `axis`
    from a0 to a1. t: radial thickness. top: if given, fill the spandrels up to this height instead."""
    g = Geo()
    r = w / 2
    for k in range(segs):
        t0, t1 = math.pi * k / segs, math.pi * (k + 1) / segs
        p0 = (c + r * math.cos(t0), zs + r * math.sin(t0)); p1 = (c + r * math.cos(t1), zs + r * math.sin(t1))
        if top is None:
            q0 = (c + (r + t) * math.cos(t0), zs + (r + t) * math.sin(t0)); q1 = (c + (r + t) * math.cos(t1), zs + (r + t) * math.sin(t1))
            prof = [p1, p0, q0, q1]
        else:
            prof = [p1, p0, (p0[0], top), (p1[0], top)]
        # make the profile counter-clockwise
        ar = sum(prof[i][0] * prof[(i + 1) % 4][1] - prof[(i + 1) % 4][0] * prof[i][1] for i in range(4))
        if ar < 0: prof = prof[::-1]
        g.add(prism(prof, axis, a0, a1, m, cap=m))
    return g


def wall_runs(rects, eps=0.01):
    """Exposed wall segments of a union of axis-aligned rectangles (the open space).
    Returns (x0, y0, x1, y1, facing) with facing the direction INTO the open space."""
    def inside(x, y):
        return any(r[0] < x < r[2] and r[1] < y < r[3] for r in rects)
    out = []
    for r in rects:
        x0, y0, x1, y1 = r
        for side in ('S', 'N', 'W', 'E'):
            if side in 'SN':
                yy = y0 if side == 'S' else y1
                probe = yy - eps if side == 'S' else yy + eps
                a, b, fixed, axis = x0, x1, yy, 'x'
            else:
                xx = x0 if side == 'W' else x1
                probe = xx - eps if side == 'W' else xx + eps
                a, b, fixed, axis = y0, y1, xx, 'y'
            # sample along the side and collect the exposed pieces
            cuts = sorted({a, b} | {v for o in rects for v in ((o[0], o[2]) if axis == 'x' else (o[1], o[3])) if a < v < b})
            for u, v in zip(cuts, cuts[1:]):
                m = (u + v) / 2
                if (inside(m, probe) if axis == 'x' else inside(probe, m)): continue
                face = {'S': '+y', 'N': '-y', 'W': '+x', 'E': '-x'}[side]
                if axis == 'x': out.append((u, fixed, v, fixed, face))
                else: out.append((fixed, u, fixed, v, face))
    # merge collinear neighbours
    out.sort()
    merged = []
    for s in out:
        if merged:
            p = merged[-1]
            if p[4] == s[4] and ((s[4] in ('+y', '-y') and abs(p[1] - s[1]) < 1e-6 and abs(p[2] - s[0]) < 1e-6) or
                                 (s[4] in ('+x', '-x') and abs(p[0] - s[0]) < 1e-6 and abs(p[3] - s[1]) < 1e-6)):
                merged[-1] = (p[0], p[1], s[2], s[3], p[4]); continue
        merged.append(s)
    return merged


def run_shelf(R, run, z, rows, frame='wood', trim=0.4, minlen=0.8, **kw):
    """Put a bookcase against a wall run from wall_runs(), trimmed at both ends."""
    x0, y0, x1, y1, f = run
    if f in ('+y', '-y'):
        a, b = x0 + trim, x1 - trim
        if b - a < minlen: return
        if f == '+y': R.shelf(a, y0, z, b - a, '+y', rows=rows, frame=frame, **kw)
        else: R.shelf(b, y0, z, b - a, '-y', rows=rows, frame=frame, **kw)
    else:
        a, b = y0 + trim, y1 - trim
        if b - a < minlen: return
        if f == '+x': R.shelf(x0, b, z, b - a, '+x', rows=rows, frame=frame, **kw)
        else: R.shelf(x0, a, z, b - a, '-x', rows=rows, frame=frame, **kw)


def book_riser(R, x0, y0, L, z, h, dirn, frame='walnut', depth=0.3):
    """One row of books in a riser of height h (a crownless shelf); (x0, y0) as for R.shelf."""
    board = 0.035
    row_h = h - board - 0.02
    R.shelf(x0, y0, z, L, dirn, rows=1, row_h=row_h, frame=frame, crown=False, back=False, top_gap=0.02, depth=depth)


def frame_cut(R, a, b, z0, z1, m='tile', bottom='floor', top='tile', c0=0.0, c1=C):
    """Cut the square ring between the squares [a, c1-a] and [b, c1-b] (b > a): a moat or trench round an island."""
    for (x0, y0, x1, y1) in ((a, a, c1 - a, b), (a, c1 - b, c1 - a, c1 - a), (a, b, b, c1 - b), (c1 - b, b, c1 - a, c1 - b)):
        R.cut(box(x0, y0, z0, x1, y1, z1, m, bottom=bottom, top=top))


def stair_rail(R, x0, y0, z0, x1, y1, z1, h=0.95, m='brass', gap=1.0):
    """A sloping handrail from (x0,y0) at floor height z0 to (x1,y1) at z1, on posts, with a collider."""
    L = math.hypot(x1 - x0, y1 - y0)
    a = math.atan2(y1 - y0, x1 - x0)
    g = Geo()
    g.add(slope_box(-0.02, L + 0.02, -0.03, 0.03, z0 + h - 0.06, z1 + h - 0.06, z0 + h, z1 + h, m))
    n = max(1, int(math.ceil(L / gap)))
    for k in range(n + 1):
        s = L * k / n; z = z0 + (z1 - z0) * s / L
        g.add(box(s - 0.02, -0.02, z - 0.3, s + 0.02, 0.02, z + h - 0.06, m))
    R.parts.add(g.xform(a, x0, y0))
    R.col.add(slope_box(0, L, -0.05, 0.05, z0 - 0.3, z1 - 0.3, z0 + h + 0.05, z1 + h + 0.05, 'tile').xform(a, x0, y0))
