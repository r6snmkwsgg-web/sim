"""Shared helpers for batch h1 (scale gone wrong, giants): giantdesk, chairmountain, pencilforest, titanlamp."""
from lib import *
from kit_a import (rail, stair_rail, shelf, sh, chair, table, bulb, desk_lamp, candle, obox, beam, rot,
                   frustum, floor_lamp, navloop, tidy, ladder, stair_side)
from kit_g import seal, upper_sockets, door_cells, sloped
import random


# ---------------------------------------------------------------------------
# primitives
def cone(cx, cy, z0, z1, r0, r1, segs=16, side='tile', top='tile', bottom='tile', caps=True, a0=0.0):
    """A solid truncated cone (r1 may be 0: a point)."""
    g = Geo()
    ang = [a0 + 2 * math.pi * k / segs for k in range(segs)]
    b = [g.vert((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0)) for a in ang]
    if r1 > 1e-4:
        t = [g.vert((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)) for a in ang]
    else:
        tip = g.vert((cx, cy, z1)); t = None
    sl = math.hypot(r0 - r1, z1 - z0)
    for k in range(segs):
        j = (k + 1) % segs
        u0, u1 = ang[k] * r0, (ang[k] + 2 * math.pi / segs) * r0
        if t: g.face([b[k], b[j], t[j], t[k]], side, [(u0, 0), (u1, 0), (u1, sl), (u0, sl)])
        else: g.face([b[k], b[j], tip], side, [(u0, 0), (u1, 0), ((u0 + u1) / 2, sl)])
    if caps:
        g.face(list(reversed(b)), bottom, [(g.v[i][0], g.v[i][1]) for i in reversed(b)])
        if t: g.face(t, top, [(g.v[i][0], g.v[i][1]) for i in t])
    return g.fix()


def along(g, p0, p1):
    """g is modelled along +x from x=0 (its axis on y=0, z=0); lay it from point p0 toward p1."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    e = math.atan2(dz, math.hypot(dx, dy)); yaw = math.atan2(dy, dx)
    rot(g, 'y', -e); rot(g, 'z', yaw)
    g.v = [(x + p0[0], y + p0[1], z + p0[2]) for x, y, z in g.v]
    return g


def xcyl(L, r, segs=12, side='tile', caps=True, top=None, bottom=None, a0=0.0):
    """A cylinder along +x from 0 to L, radius r (for along())."""
    g = cyl(0, 0, 0, L, r, segs, side=side, top=top or side, bottom=bottom or side, caps=caps, a0=a0, a1=a0 + 2 * math.pi)
    rot(g, 'y', math.pi / 2)          # z -> +x ... (x' = z, z' = -x)
    return g


def xcone(L, r0, r1, segs=12, side='tile', a0=0.0):
    g = cone(0, 0, 0, L, r0, r1, segs, side=side, top=side, bottom=side, a0=a0)
    rot(g, 'y', math.pi / 2)
    return g


def hexcyl(cx, cy, z0, z1, r, side='tile', top=None, bottom=None, a0=0.0):
    """A hexagonal prism (a pencil standing up); r is the corner radius."""
    g = Geo()
    ang = [a0 + math.pi / 3 * k for k in range(6)]
    b = [g.vert((cx + r * math.cos(a), cy + r * math.sin(a), z0)) for a in ang]
    t = [g.vert((cx + r * math.cos(a), cy + r * math.sin(a), z1)) for a in ang]
    for k in range(6):
        j = (k + 1) % 6
        g.face([b[k], b[j], t[j], t[k]], side, [(k * r, z0), ((k + 1) * r, z0), ((k + 1) * r, z1), (k * r, z1)])
    g.face(list(reversed(b)), bottom or side, [(g.v[i][0], g.v[i][1]) for i in reversed(b)])
    g.face(t, top or side, [(g.v[i][0], g.v[i][1]) for i in t])
    return g.fix()


def spiral_band(cx, cy, a0, a1, r_in, r_out, z0, z1, segs, top='floor', side='tile', bottom='tile', thick=0.4, bank=0.0):
    """A path winding round a centre: angle a0->a1, the inner/outer radius functions of t (0..1) or numbers,
    rising from z0 to z1. thick: depth of the band under its top."""
    fr = (lambda f: f) if callable(r_in) else (lambda f: (lambda t: f))
    ri, ro = fr(r_in), fr(r_out)
    g = Geo()
    it, ot, ib, ob = [], [], [], []
    for k in range(segs + 1):
        t = k / segs; a = a0 + (a1 - a0) * t; z = z0 + (z1 - z0) * t
        c, s = math.cos(a), math.sin(a)
        it.append(g.vert((cx + ri(t) * c, cy + ri(t) * s, z)))
        ot.append(g.vert((cx + ro(t) * c, cy + ro(t) * s, z - bank)))
        ib.append(g.vert((cx + ri(t) * c, cy + ri(t) * s, z - thick)))
        ob.append(g.vert((cx + ro(t) * c, cy + ro(t) * s, z - thick - bank)))
    Ls = [0.0]
    for k in range(1, segs + 1):
        p, q = g.v[it[k]], g.v[it[k - 1]]
        Ls.append(Ls[-1] + math.dist(p, q))
    for k in range(segs):
        j = k + 1
        uv = [(Ls[k], 0), (Ls[j], 0), (Ls[j], 2), (Ls[k], 2)]
        g.face([ot[k], ot[j], it[j], it[k]], top, uv)
        g.face([ib[k], ib[j], ob[j], ob[k]], bottom, uv)
        g.face([ob[k], ob[j], ot[j], ot[k]], side, [(Ls[k], 0), (Ls[j], 0), (Ls[j], thick), (Ls[k], thick)])
        g.face([ib[j], ib[k], it[k], it[j]], side, [(Ls[j], 0), (Ls[k], 0), (Ls[k], thick), (Ls[j], thick)])
    g.face([ib[0], ob[0], ot[0], it[0]], side, [(0, 0), (1, 0), (1, 1), (0, 1)])
    g.face([ob[-1], ib[-1], it[-1], ot[-1]], side, [(0, 0), (1, 0), (1, 1), (0, 1)])
    return g.fix()


def poly_rail(R, pts, z, h=0.95, m='brass', post=1.1, closed=False):
    """A brass rail along a polyline of (x, y) (or (x, y, z) points, then z is ignored per point)."""
    P = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(P, P[1:]):
        za = a[2] if len(a) > 2 else z; zb = b[2] if len(b) > 2 else z
        if abs(za - zb) < 1e-3: rail(R, a[0], a[1], b[0], b[1], za, h=h, m=m, post=post)
        else: stair_rail(R, a[0], a[1], za, b[0], b[1], zb, h=h, m=m, post=post)


def secret(R, x, y, z, name, text, r=1.5):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, box_, **kw):
    d = {'type': kind, 'box': [round(v, 2) for v in box_]}; d.update(kw)
    R.meta.setdefault('fx', []).append(d)


# ---------------------------------------------------------------------------
# the normal-sized library round the edge of a giant room
GZ = 8.0          # gallery floor (the upper doorways' sill)
GW = 2.65         # gallery width, from the wall face


def gallery(R, gaps=(), wd=GW, z=GZ, th=0.55, top='floor', rail_m='brass', corbel=4.0, solid=False):
    """A walkway round all four walls at the upper doorways' level, railed on its inner edge.
    gaps: ((side, a, b), ...) stretches of the inner edge left open (for stairs and bridges); a, b
    along the wall (x for S/N, y for W/E)."""
    W, D = R.W, R.D
    e = T + wd
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, W - T + 0.02, e), (T - 0.02, D - e, W - T + 0.02, D - T + 0.02),
                             (T - 0.02, e, e, D - e), (W - e, e, W - T + 0.02, D - e)):
        R.parts.add(box(x0, y0, z - th, x1, y1, z, 'tile', top=top, bottom='plaster'))
    # a moulded lip and stone brackets under it
    for (x0, y0, x1, y1) in ((e - 0.12, e - 0.12, W - e + 0.12, e + 0.02), (e - 0.12, D - e - 0.02, W - e + 0.12, D - e + 0.12),
                             (e - 0.12, e, e + 0.02, D - e), (W - e - 0.02, e, W - e + 0.12, D - e)):
        R.parts.add(box(x0, y0, z - th - 0.18, x1, y1, z - th + 0.1, 'tile', skip=('+z',)))
    def along_wall(side, fn):
        L = W if side in 'SN' else D
        n = int((L - 2 * e) / corbel)
        for k in range(n + 1):
            p = e + (L - 2 * e) * k / n
            if abs(((p - C / 2) % C) - 0) < 2.0 or abs(((p - C / 2) % C) - C) < 2.0: continue   # not over a doorway
            fn(p)
    for side in 'SNWE':
        def cb(p, side=side):
            g = Geo()
            g.add(sloped('x', 0, wd - 0.2, -0.18, 0.18, z - th - 1.4, z - th - 0.3, z - th, z - th, 'tile'))
            a = {'S': math.pi / 2, 'N': -math.pi / 2, 'W': 0.0, 'E': math.pi}[side]
            x, y = {'S': (p, T), 'N': (p, D - T), 'W': (T, p), 'E': (W - T, p)}[side]
            R.parts.add(g.xform(a, x, y))
        along_wall(side, cb)
    # the rail on the inner edge, broken by the gaps
    runs = {'S': (e, W - e, lambda a: (a, e)), 'N': (e, W - e, lambda a: (a, D - e)),
            'W': (e, D - e, lambda a: (e, a)), 'E': (e, D - e, lambda a: (W - e, a))}
    for side, (a0, a1, P) in runs.items():
        cuts = sorted([(a, b) for (s, a, b) in gaps if s == side])
        segs, cur = [], a0
        for (a, b) in cuts:
            if a > cur: segs.append((cur, a))
            cur = max(cur, b)
        if cur < a1: segs.append((cur, a1))
        for (a, b) in segs:
            if b - a < 0.05: continue
            p, q = P(a), P(b)
            inset = 0.1
            if side == 'S': p, q = (p[0], p[1] - inset), (q[0], q[1] - inset)
            if side == 'N': p, q = (p[0], p[1] + inset), (q[0], q[1] + inset)
            if side == 'W': p, q = (p[0] - inset, p[1]), (q[0] - inset, q[1])
            if side == 'E': p, q = (p[0] + inset, p[1]), (q[0] + inset, q[1])
            if solid: balus(R, p[0], p[1], q[0], q[1], z)
            else: rail(R, p[0], p[1], q[0], q[1], z, m=rail_m)


def balus(R, x0, y0, x1, y1, z, h=1.0):
    """A stone balustrade: plinth, little pillars (drawn), a cap, and a solid collider."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.05: return
    a = math.atan2(y1 - y0, x1 - x0)
    g = Geo()
    g.add(box(0, -0.13, 0, L, 0.13, 0.16, 'tile', skip=('-z',)))
    g.add(box(-0.02, -0.16, h - 0.1, L + 0.02, 0.16, h, 'tile'))
    n = max(1, int(L / 0.32))
    for k in range(n):
        u = (k + 0.5) * L / n
        g.add(box(u - 0.05, -0.05, 0.16, u + 0.05, 0.05, h - 0.1, 'tile', skip=('-z', '+z')))
    R.nocol.add(g.xform(a, x0, y0, z))
    R.col.add(box(0, -0.1, 0, L, 0.1, h + 0.1, 'tile').xform(a, x0, y0, z))


def gallery_cases(R, z=GZ, rows=13, frame='walnut', gap=2.0, skip=(), row_h=0.42):
    """Bookcases on the walls above the gallery, broken at each doorway; skip: (side, k) cell edges to leave bare."""
    W, D = R.W, R.D
    e0 = T + 0.02
    for k in range(R.w):
        for (a, b) in ((k * C + (0.9 if k == 0 else 0.3), k * C + C / 2 - gap), (k * C + C / 2 + gap, (k + 1) * C - (0.9 if k == R.w - 1 else 0.3))):
            if ('S', k) not in skip: shelf(R, a, e0, z, b - a, '+y', rows=rows, frame=frame, row_h=row_h)
            if ('N', k) not in skip: shelf(R, b, D - e0, z, b - a, '-y', rows=rows, frame=frame, row_h=row_h)
    for k in range(R.d):
        for (a, b) in ((k * C + (0.9 if k == 0 else 0.3), k * C + C / 2 - gap), (k * C + C / 2 + gap, (k + 1) * C - (0.9 if k == R.d - 1 else 0.3))):
            if ('W', k) not in skip: shelf(R, e0, b, z, b - a, '+x', rows=rows, frame=frame, row_h=row_h)
            if ('E', k) not in skip: shelf(R, W - e0, a, z, b - a, '-x', rows=rows, frame=frame, row_h=row_h)


def gallery_lamps(R, z=GZ, every=8.0, m='e_lamp', night=4, skip=None):
    """Little green desk-lamp glows on brass stands along the gallery rail (the normal-sized library)."""
    W, D = R.W, R.D
    e = T + GW - 0.35
    pts = []
    for k in range(R.w * 2):
        x = k * C / 2 + C / 4
        pts += [(x, e, 'S'), (x, D - e, 'N')]
    for k in range(R.d * 2):
        y = k * C / 2 + C / 4
        pts += [(e, y, 'W'), (W - e, y, 'E')]
    for i, (x, y, s) in enumerate(pts):
        if skip and skip(x, y): continue
        R.parts.add(cyl(x, y, z, z + 0.04, 0.14, 10, side='brass', top='brass'))
        R.parts.add(cyl(x, y, z + 0.04, z + 1.25, 0.02, 6, side='brass', caps=False))
        R.nocol.add(frustum(x, y, z + 1.22, z + 1.42, 0.24, 0.1, 12, m='green', inner='ivory'))
        R.light(cyl(x, y, z + 1.2, z + 1.23, 0.21, 10, side=m, top=m, bottom=m))
        if i % night == 0: R.light(sphere(x, y, z + 1.3, 0.05, 6, 3, 'e_amber'))


def wall_flight(R, side, a, z0=0.0, z1=GZ, wd=2.2, off=None, rise=0.2, run=0.3, m='tile', tread='floor', up=+1, land=None):
    """A masonry stair against the inner edge of the gallery, climbing along the wall from floor to gallery.
    side: which wall; a: where its foot starts along the wall; up=+1 climbs toward +x/+y. Returns the
    gallery gap (side, a0, a1) where its landing meets the gallery."""
    W, D = R.W, R.D
    off = T + GW if off is None else off
    n = int(round((z1 - z0) / rise)); rise = (z1 - z0) / n
    L = n * run
    land = wd if land is None else land
    U = {'W': (0, up), 'E': (0, up), 'S': (up, 0), 'N': (up, 0)}[side]
    V = {'W': (1, 0), 'E': (-1, 0), 'S': (0, 1), 'N': (0, -1)}[side]
    O = {'W': (off, a), 'E': (W - off, a), 'S': (a, off), 'N': (a, D - off)}[side]
    P = lambda u, v: (O[0] + u * U[0] + v * V[0], O[1] + u * U[1] + v * V[1])
    def bx(u0, v0, u1, v1, za, zb, mm, g=None, **kw):
        p, q = P(u0, v0), P(u1, v1)
        return box(min(p[0], q[0]), min(p[1], q[1]), za, max(p[0], q[0]), max(p[1], q[1]), zb, mm, **kw)
    axis = ('+' if up > 0 else '-') + ('y' if side in 'WE' else 'x')
    p, q = P(0, 0), P(0, wd)
    if side in 'WE': fx, fy = min(p[0], q[0]), p[1]
    else: fx, fy = p[0], min(p[1], q[1])
    R.flight(fx, fy, z0, wd, n, rise, run, axis, m=tread, riser=m, side=m)
    # the stair's body, collided
    p, q = P(0, 0), P(L, wd)
    if side in 'WE': R.col.add(sloped('y', min(p[1], q[1]), max(p[1], q[1]), min(p[0], q[0]), max(p[0], q[0]), z0, z0,
                                      z0 if up > 0 else z1 - rise, z1 - rise if up > 0 else z0, 'tile'))
    else: R.col.add(sloped('x', min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1]), z0, z0,
                           z0 if up > 0 else z1 - rise, z1 - rise if up > 0 else z0, 'tile'))
    R.parts.add(bx(L, 0, L + land, wd, z0, z1, m, top=tread))
    for v in (0.1, wd - 0.1):
        s0, s1 = P(0.25, v), P(L, v)
        stair_balus(R, s0[0], s0[1], z0 + rise, s1[0], s1[1], z1)
    e0, e1 = P(L + land - 0.12, 0.0), P(L + land - 0.12, wd)
    balus(R, e0[0], e0[1], e1[0], e1[1], z1)
    e0, e1 = P(L, wd - 0.1), P(L + land - 0.12, wd - 0.1)
    balus(R, e0[0], e0[1], e1[0], e1[1], z1)
    ga, gb = sorted((P(L + 0.1, 0)[1 if side in 'WE' else 0], P(L + land, 0)[1 if side in 'WE' else 0]))
    return (side, ga, gb)


def stair_balus(R, x0, y0, z0, x1, y1, z1, h=1.0):
    """A sloping stone balustrade along a flight (drawn) with a sloped invisible wall and a brass cap."""
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(L / 0.45))
    for k in range(n + 1):
        t = k / n; x, y, z = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        R.nocol.add(box(x - 0.05, y - 0.05, z - 0.25, x + 0.05, y + 0.05, z + h - 0.08, 'tile', skip=('-z', '+z')))
    R.nocol.add(beam((x0, y0, z0 + h - 0.04), (x1, y1, z1 + h - 0.04), 0.24, 'tile', 0.1))
    R.nocol.add(beam((x0, y0, z0 + h + 0.02), (x1, y1, z1 + h + 0.02), 0.08, 'brass', 0.03))
    g = Geo()
    dx, dy = x1 - x0, y1 - y0; nx, ny = -dy / L * 0.06, dx / L * 0.06
    P = [(x0 - nx, y0 - ny, z0 - 0.4), (x1 - nx, y1 - ny, z1 - 0.4), (x1 + nx, y1 + ny, z1 - 0.4), (x0 + nx, y0 + ny, z0 - 0.4)]
    P += [(p[0], p[1], p[2] + h + 0.55) for p in P]
    ids = [g.vert(p) for p in P]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        g.face([ids[i] for i in f], 'tile', [(0, 0)] * 4)
    R.col.add(g.fix())


def lower_cases(R, rows=9, frame='walnut', gap=2.2, row_h=0.42, sides='SNWE', every=1):
    """Bookcases on the lower walls, broken at each doorway."""
    W, D = R.W, R.D
    e0 = T + 0.02
    for k in range(R.w):
        if k % every: continue
        for (a, b) in ((k * C + (0.9 if k == 0 else 0.3), k * C + C / 2 - gap), (k * C + C / 2 + gap, (k + 1) * C - (0.9 if k == R.w - 1 else 0.3))):
            if 'S' in sides: shelf(R, a, e0, 0, b - a, '+y', rows=rows, frame=frame, row_h=row_h)
            if 'N' in sides: shelf(R, b, D - e0, 0, b - a, '-y', rows=rows, frame=frame, row_h=row_h)
    for k in range(R.d):
        if k % every: continue
        for (a, b) in ((k * C + (0.9 if k == 0 else 0.3), k * C + C / 2 - gap), (k * C + C / 2 + gap, (k + 1) * C - (0.9 if k == R.d - 1 else 0.3))):
            if 'W' in sides: shelf(R, e0, b, 0, b - a, '+x', rows=rows, frame=frame, row_h=row_h)
            if 'E' in sides: shelf(R, W - e0, a, 0, b - a, '-x', rows=rows, frame=frame, row_h=row_h)


# ---------------------------------------------------------------------------
# giant stationery
def pencil_up(R, cx, cy, z0, L, r, body='gilt', wood='oak', lead='slate', a0=0.0, coll=True, band='brass', rubber='oxblood',
              point=True, hollow=False):
    """A pencil standing on its end (the rubber down, the point up). L includes the cone."""
    cl = r * 2.6                                   # the sharpened cone's length
    dst = R.parts if coll else R.nocol
    zb = z0
    if rubber:
        dst.add(hexcyl(cx, cy, zb, zb + r * 0.9, r * 0.96, side=rubber, a0=a0)); zb += r * 0.9
        dst.add(cyl(cx, cy, zb, zb + r * 0.7, r * 0.99, 12, side=band, top=band, bottom=band)); zb += r * 0.7
    zt = z0 + L - cl
    if not hollow:
        dst.add(hexcyl(cx, cy, zb, zt, r, side=body, top=body, bottom=body, a0=a0))
    if point:
        dst.add(cone(cx, cy, zt, zt + cl * 0.82, r * 0.86, r * 0.22, 6, side=wood, top=lead, bottom=wood, a0=a0))
        dst.add(cone(cx, cy, zt + cl * 0.82, zt + cl, r * 0.22, 0.0, 6, side=lead, a0=a0))
        # the painted scallops where the sharpener stopped
        R.nocol.add(cone(cx, cy, zt - 0.01, zt + cl * 0.12, r * 1.0, r * 0.84, 6, side=body, top=body, bottom=body, a0=a0))
    return zt


def pencil_lying(R, p0, p1, r, body='gilt', wood='oak', lead='slate', coll=True, spin=0.0):
    """A pencil lying from p0 (rubber end) to p1 (point), both (x, y, z) of its axis."""
    L = math.dist(p0, p1)
    cl = r * 2.6
    dst = R.parts if coll else R.nocol
    g = Geo()
    g.add(hexcyl(0, 0, 0, r * 0.9, r * 0.96, side='oxblood', a0=spin))
    g.add(cyl(0, 0, r * 0.9, r * 1.6, r * 0.99, 12, side='brass', top='brass', bottom='brass'))
    g.add(hexcyl(0, 0, r * 1.6, L - cl, r, side=body, a0=spin))
    g.add(cone(0, 0, L - cl, L - cl * 0.18, r * 0.86, r * 0.22, 6, side=wood, top=lead, bottom=wood, a0=spin))
    g.add(cone(0, 0, L - cl * 0.18, L, r * 0.22, 0.0, 6, side=lead, a0=spin))
    rot(g, 'y', math.pi / 2)
    dst.add(along(g, p0, p1))


def book_block(R, x0, y0, x1, y1, z0, z1, cover='oxblood', pages='ivory', ang=0.0, cx=None, cy=None, spine='-x', coll=True, over=0.18):
    """A closed hardback lying flat: two boards overhanging a page block, a spine on one side.
    Axis-aligned in its own frame, then rotated by ang about (cx, cy)."""
    g = Geo()
    ct = min(0.12, (z1 - z0) * 0.14)
    g.add(box(x0, y0, z0, x1, y1, z0 + ct, cover))
    g.add(box(x0, y0, z1 - ct, x1, y1, z1, cover))
    px0, py0, px1, py1 = x0 + over, y0 + over, x1 - over, y1 - over
    if spine == '-x': px0 = x0
    elif spine == '+x': px1 = x1
    elif spine == '-y': py0 = y0
    else: py1 = y1
    g.add(box(px0, py0, z0 + ct, px1, py1, z1 - ct, pages, skip=('-z', '+z')))
    # the spine
    if spine in ('-x', '+x'):
        xs = x0 if spine == '-x' else x1 - 0.02
        g.add(box(xs - 0.02, y0, z0, xs + 0.04, y1, z1, cover))
    else:
        ys = y0 if spine == '-y' else y1 - 0.02
        g.add(box(x0, ys - 0.02, z0, x1, ys + 0.04, z1, cover))
    if ang:
        cx = (x0 + x1) / 2 if cx is None else cx; cy = (y0 + y1) / 2 if cy is None else cy
        g.v = [(x - cx, y - cy, z) for x, y, z in g.v]
        g.xform(ang, cx, cy)
    (R.parts if coll else R.nocol).add(g)
    return g


def qprism(pts, z0, z1, mats, top='tile', bottom='tile'):
    """A vertical prism on a convex 2D polygon (counter-clockwise), one material per edge."""
    g = Geo()
    n = len(pts)
    b = [g.vert((x, y, z0)) for x, y in pts]
    t = [g.vert((x, y, z1)) for x, y in pts]
    s = 0.0
    for k in range(n):
        j = (k + 1) % n
        L = math.dist(pts[k], pts[j])
        m = mats[k] if isinstance(mats, (list, tuple)) else mats
        g.face([b[k], b[j], t[j], t[k]], m, [(s, z0), (s + L, z0), (s + L, z1), (s, z1)])
        s += L
    g.face(list(reversed(b)), bottom, [pts[k] for k in reversed(range(n))])
    g.face(t, top, list(pts))
    return g.fix()


def hex_shell(R, cx, cy, r, t, z0, z1, outer='gilt', inner='oak', a0=0.0, gaps=(), top=None, faces=range(6)):
    """The six walls of a hollow hexagonal prism (corner radius r, wall t thick). gaps: (face, u0, u1, zg0, zg1)
    openings cut through a face (u along the face from 0 to 1)."""
    ri = r - t / math.cos(math.pi / 6)
    O = [(cx + r * math.cos(a0 + k * math.pi / 3), cy + r * math.sin(a0 + k * math.pi / 3)) for k in range(6)]
    I = [(cx + ri * math.cos(a0 + k * math.pi / 3), cy + ri * math.sin(a0 + k * math.pi / 3)) for k in range(6)]
    lerp = lambda p, q, u: (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
    for k in range(6):
        j = (k + 1) % 6
        if k not in faces: continue
        def piece(u0, u1, za, zb):
            if u1 - u0 < 1e-3 or zb - za < 1e-3: return
            pts = [lerp(O[k], O[j], u0), lerp(O[k], O[j], u1), lerp(I[k], I[j], u1), lerp(I[k], I[j], u0)]
            # counter-clockwise: outer edge runs with increasing angle, so the order above is CCW? make sure
            area = sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4))
            mats = [outer, inner if u1 >= 1 else inner, inner, inner]
            if area < 0:
                pts = list(reversed(pts)); mats = [inner, inner, inner, outer]
                # reversed: edges are (i3,i2),(i2,o1),(o1,o0),(o0,i3) -> outer edge is the third
                mats = [inner, inner, outer, inner]
            R.parts.add(qprism(pts, za, zb, mats, top=top or inner, bottom=inner))
        gs = [g for g in gaps if g[0] == k]
        if not gs:
            piece(0, 1, z0, z1); continue
        (_, u0, u1, zg0, zg1) = gs[0]
        piece(0, u0, z0, z1); piece(u1, 1, z0, z1)
        if zg0 > z0: piece(u0, u1, z0, zg0)
        if zg1 < z1: piece(u0, u1, zg1, z1)
    return O, I


def shaving(r0, r1, h, sweep, segs=7, wood='oak', paint='gilt'):
    """A pencil shaving: a frilled conical skirt from radius r0 (up at h) to r1 (at 0), open by sweep radians,
    with a painted band at its outer edge. Two-sided. Modelled at the origin."""
    g = Geo()
    ang = [sweep * k / segs for k in range(segs + 1)]
    rm = r1 - (r1 - r0) * 0.12
    for k in range(segs):
        a, b = ang[k], ang[k + 1]
        wob = lambda a_: 1.0 + 0.08 * math.sin(a_ * 5.0)
        p = [(r0 * math.cos(a), r0 * math.sin(a), h), (r0 * math.cos(b), r0 * math.sin(b), h),
             (rm * wob(b) * math.cos(b), rm * wob(b) * math.sin(b), h * 0.12), (rm * wob(a) * math.cos(a), rm * wob(a) * math.sin(a), h * 0.12)]
        q = [(rm * wob(a) * math.cos(a), rm * wob(a) * math.sin(a), h * 0.12), (rm * wob(b) * math.cos(b), rm * wob(b) * math.sin(b), h * 0.12),
             (r1 * wob(b) * math.cos(b), r1 * wob(b) * math.sin(b), 0.0), (r1 * wob(a) * math.cos(a), r1 * wob(a) * math.sin(a), 0.0)]
        for pts, m in ((p, wood), (q, paint)):
            ids = [g.vert(v) for v in pts]
            uv = [(v[0], v[1]) for v in pts]
            g.face(ids, m, uv)
            ids2 = [g.vert(v) for v in reversed(pts)]
            g.face(ids2, m, list(reversed(uv)))
    return g


def ribbon(inner, outer, thick=0.3, top='floor', side='tile', bottom='tile'):
    """A band between two sampled edges (lists of (x, y, z) top points, same length), thick deep."""
    g = Geo()
    n = len(inner)
    it = [g.vert(p) for p in inner]; ot = [g.vert(p) for p in outer]
    ib = [g.vert((p[0], p[1], p[2] - thick)) for p in inner]; ob = [g.vert((p[0], p[1], p[2] - thick)) for p in outer]
    L = [0.0]
    for k in range(1, n):
        L.append(L[-1] + math.dist(inner[k][:2], inner[k - 1][:2]))
    w = math.dist(inner[0][:2], outer[0][:2])
    for k in range(n - 1):
        j = k + 1
        uv = [(L[k], 0), (L[j], 0), (L[j], w), (L[k], w)]
        g.face([it[k], it[j], ot[j], ot[k]], top, uv)
        g.face([ob[k], ob[j], ib[j], ib[k]], bottom, uv)
        g.face([ot[k], ot[j], ob[j], ob[k]], side, [(L[k], 0), (L[j], 0), (L[j], thick), (L[k], thick)])
        g.face([ib[k], ib[j], it[j], it[k]], side, [(L[k], 0), (L[j], 0), (L[j], thick), (L[k], thick)])
    g.face([it[0], ot[0], ob[0], ib[0]], side, [(0, 0), (w, 0), (w, thick), (0, thick)])
    g.face([ib[-1], ob[-1], ot[-1], it[-1]], side, [(0, 0), (w, 0), (w, thick), (0, thick)])
    # make the top face up
    a, b, c = g.v[it[0]], g.v[it[1]], g.v[ot[0]]
    nz = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if nz < 0:
        g.f = [tuple(reversed(f)) for f in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    return g


def col_fence(R, pts, h=1.1, below=0.3):
    """An invisible wall along a polyline of (x, y, z) points, from z - below to z + h."""
    g = Geo()
    for a, b in zip(pts, pts[1:]):
        ids = [g.vert((a[0], a[1], a[2] - below)), g.vert((b[0], b[1], b[2] - below)),
               g.vert((b[0], b[1], b[2] + h)), g.vert((a[0], a[1], a[2] + h))]
        g.face(ids, 'tile', [(0, 0)] * 4)
    R.col.add(g)


def tilted_chair(rnd, frame=None, seat=None, scale=1.0, tilt=0.5):
    """A chair at the origin, knocked about: random frame and seat, tilted up to `tilt` radians."""
    frame = frame or rnd.choice(['walnut', 'oak', 'wood', 'walnut', 'leather'])
    seat = seat or rnd.choice(['leather', 'velvet', 'green', 'oxblood', 'oak', 'leather'])
    g = chair(0, 0, 0.0, frame=frame, seat=seat, back_h=rnd.choice([0.95, 1.0, 1.1, 1.25]))
    if scale != 1.0: g.v = [(x * scale, y * scale, z * scale) for x, y, z in g.v]
    if tilt:
        rot(g, 'x', rnd.uniform(-tilt, tilt)); rot(g, 'y', rnd.uniform(-tilt, tilt))
    return g
