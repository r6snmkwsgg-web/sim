"""Shared helpers for batch "e" rooms (long rooms and shafts)."""
from lib import *

W2, D2 = 2 * C, C                                   # the long room: 32 x 16
LONG_SEGS = ((0.6, 6.2), (9.8, 22.2), (25.8, 31.4))  # wall stretches along a 32 m wall, clear of the doors
END_SEGS = ((0.6, 6.2), (9.8, C - 0.6))              # along a 16 m wall
CELL_SEGS = END_SEGS


def long_shell(R, H=TOP, wall='tile', floor='floor', ceil='plaster'):
    R.sockets(floor=floor, wall=wall)
    R.cut(box(T - 0.02, T - 0.02, 0, R.W - T + 0.02, R.D - T + 0.02, H, wall, bottom=floor, top=ceil))


def wall_shelves(R, rows=7, frame='wood', sides='SNWE', z=0.0, inset=T, segs_x=LONG_SEGS, segs_y=END_SEGS, **kw):
    """Bookcases along the room's walls, between the doorways."""
    W, D = R.W, R.D
    if 'S' in sides or 'N' in sides:
        for (a, b) in segs_x:
            if 'S' in sides: R.shelf(a, inset, z, b - a, '+y', rows=rows, frame=frame, **kw)
            if 'N' in sides: R.shelf(b, D - inset, z, b - a, '-y', rows=rows, frame=frame, **kw)
    for (a, b) in segs_y:
        if 'W' in sides: R.shelf(inset, b, z, b - a, '+x', rows=rows, frame=frame, **kw)
        if 'E' in sides: R.shelf(W - inset, a, z, b - a, '-x', rows=rows, frame=frame, **kw)


def beam(p0, p1, w, h, m='brass', top=None):
    """A bar from p0 to p1 (3D points on its bottom centre line), w wide, h tall, sides kept vertical."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    if L < 1e-9: nx, ny = w / 2, 0.0
    else: nx, ny = -dy / L * w / 2, dx / L * w / 2
    g = Geo()
    P = [(p0[0] + nx, p0[1] + ny, p0[2]), (p0[0] - nx, p0[1] - ny, p0[2]), (p1[0] - nx, p1[1] - ny, p1[2]), (p1[0] + nx, p1[1] + ny, p1[2])]
    P += [(x, y, z + h) for (x, y, z) in P]
    ids = [g.vert(p) for p in P]
    uv = lambda i: (P[i][0] + P[i][1], P[i][2])
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        mm = top if (top and f == (4, 5, 6, 7)) else m
        g.face([ids[i] for i in f], mm, [uv(i) for i in f])
    return g.fix()


def wedge(p0, p1, w, bot0, bot1, top0, top1, m='tile'):
    """A wall from p0 to p1 (x, y), w thick, whose bottom and top run linearly from (bot0, top0) to (bot1, top1)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    g = Geo()
    P = [(p0[0] + nx, p0[1] + ny, bot0), (p0[0] - nx, p0[1] - ny, bot0), (p1[0] - nx, p1[1] - ny, bot1), (p1[0] + nx, p1[1] + ny, bot1),
         (p0[0] + nx, p0[1] + ny, top0), (p0[0] - nx, p0[1] - ny, top0), (p1[0] - nx, p1[1] - ny, top1), (p1[0] + nx, p1[1] + ny, top1)]
    ids = [g.vert(p) for p in P]
    uv = lambda i: (P[i][0] + P[i][1], P[i][2])
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        g.face([ids[i] for i in f], m, [uv(i) for i in f])
    return g.fix()


def rail(R, pts, h=0.95, m='brass', post='iron', spacing=1.1, mid=True, col=True, end_posts=True):
    """An open rail following a polyline of (x, y, z) floor points: a top bar at h, posts at most
    `spacing` apart, a middle bar, and an invisible wall under it so nobody slips through."""
    V = R.nocol if col else R.parts             # the drawn rail; an invisible wall does the stopping
    for (p0, p1) in zip(pts, pts[1:]):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        V.add(beam((p0[0], p0[1], p0[2] + h), (p1[0], p1[1], p1[2] + h), 0.06, 0.05, m))
        if mid: V.add(beam((p0[0], p0[1], p0[2] + h * 0.5), (p1[0], p1[1], p1[2] + h * 0.5), 0.03, 0.03, post))
        n = max(1, int(math.ceil(L / spacing)))
        for k in range(0 if end_posts else 1, n + (1 if end_posts else 0)):
            t = k / n
            x, y, z = (p0[i] + (p1[i] - p0[i]) * t for i in range(3))
            V.add(box(x - 0.022, y - 0.022, z, x + 0.022, y + 0.022, z + h, post, skip=('-z',)))
        if col: R.col.add(beam((p0[0], p0[1], p0[2] - 0.05), (p1[0], p1[1], p1[2] - 0.05), 0.08, h + 0.1, 'iron'))


def lathe(cx, cy, prof, segs=16, m='tile'):
    """A solid of revolution from [(r, z), ...] bottom to top (r=0 ends are closed points)."""
    g = Geo()
    rings = []
    for (r, z) in prof:
        if r < 1e-6: rings.append([g.vert((cx, cy, z))])
        else: rings.append([g.vert((cx + r * math.cos(2 * math.pi * k / segs), cy + r * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)])
    for i in range(len(prof) - 1):
        A, B = rings[i], rings[i + 1]
        for k in range(segs):
            j = (k + 1) % segs
            u0, u1 = k / segs * 2, (k + 1) / segs * 2
            v0, v1 = prof[i][1], prof[i + 1][1]
            if len(A) == 1 and len(B) == 1: continue
            if len(A) == 1: g.face([A[0], B[j], B[k]], m, [(u0, v0), (u1, v1), (u0, v1)])
            elif len(B) == 1: g.face([A[k], A[j], B[0]], m, [(u0, v0), (u1, v0), (u0, v1)])
            else: g.face([A[k], A[j], B[j], B[k]], m, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    if len(rings[0]) > 1: g.face(list(reversed(rings[0])), m, [(0, 0)] * segs)
    if len(rings[-1]) > 1: g.face(rings[-1], m, [(0, 0)] * segs)
    return g.fix()


def pendant(R, x, y, z, top, r=0.18, m='brass', em='e_lamp'):
    """A hanging lamp: a cord from `top` down to a shade at z with a glowing disc under it."""
    R.parts.add(cyl(x, y, z + 0.2, top, 0.012, 6, side='iron', caps=False))
    R.parts.add(cyl(x, y, z + 0.05, z + 0.2, r, 16, side=m, top=m, bottom=m))
    R.light(cyl(x, y, z, z + 0.05, r * 0.8, 16, side=em, top=em, bottom=em))


def globe(R, x, y, z, top, r=0.16, em='e_lamp'):
    """A glowing glass globe hung on a rod."""
    R.parts.add(cyl(x, y, z + r * 0.9, top, 0.015, 6, side='iron', caps=False))
    R.parts.add(cyl(x, y, z + r * 0.8, z + r * 1.05, 0.05, 8, side='brass', top='brass', bottom='brass'))
    R.light(sphere(x, y, z, r, 12, 6, em))


def table_lamp(R, x, y, z, shade='green', r=0.16):
    R.parts.add(cyl(x, y, z, z + 0.03, 0.08, 10, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(x, y, z + 0.03, z + 0.36, 0.015, 6, side='brass', caps=False))
    R.parts.add(cyl(x, y, z + 0.36, z + 0.46, r, 14, side=shade, top=shade, bottom=shade))
    R.light(cyl(x, y, z + 0.33, z + 0.36, r * 0.8, 14, side='e_lamp', top='e_lamp', bottom='e_lamp'))


def table(R, x0, y0, x1, y1, h=0.76, m='walnut', top=None, z=0.0):
    R.parts.add(box(x0, y0, z + h - 0.05, x1, y1, z + h, m, top=top))
    for (a, b) in ((x0 + 0.06, y0 + 0.06), (x1 - 0.12, y0 + 0.06), (x0 + 0.06, y1 - 0.12), (x1 - 0.12, y1 - 0.12)):
        R.parts.add(box(a, b, z, a + 0.06, b + 0.06, z + h - 0.05, m, skip=('-z',)))


def chair(R, x, y, face, frame='walnut', seat='leather', h=0.46, spot=True, z=0.0):
    """A chair whose sitter faces `face` (radians)."""
    g = Geo()
    g.add(box(-0.22, -0.22, 0, 0.22, 0.22, h, frame, top=seat, skip=('-z',)))
    g.add(box(-0.24, -0.22, h, -0.18, 0.22, h + 0.5, frame))
    R.parts.add(g.xform(face, x, y, z))
    if spot: R.spot('sit', x, y, z + h, face)


def bench(R, x0, y0, x1, y1, m='walnut', h=0.45, seat=None, spots=True, face=None, z=0.0):
    R.parts.add(box(x0, y0, z + h - 0.07, x1, y1, z + h, m, top=seat))
    for (a, b) in ((x0 + 0.05, y0 + 0.05), (x1 - 0.13, y0 + 0.05), (x0 + 0.05, y1 - 0.13), (x1 - 0.13, y1 - 0.13)):
        R.parts.add(box(a, b, z, a + 0.08, b + 0.08, z + h - 0.07, m, skip=('-z',)))
    if spots:
        if x1 - x0 > y1 - y0:
            n = max(1, int((x1 - x0) / 0.8))
            for k in range(n):
                R.spot('sit', x0 + (k + 0.5) * (x1 - x0) / n, (y0 + y1) / 2, z + h, math.pi / 2 if face is None else face)
        else:
            n = max(1, int((y1 - y0) / 0.8))
            for k in range(n):
                R.spot('sit', (x0 + x1) / 2, y0 + (k + 0.5) * (y1 - y0) / n, z + h, 0.0 if face is None else face)


def pilaster(R, x, y, dirn, z0=0.0, z1=TOP, w=0.6, d=0.25, m='tile'):
    """A flat pilaster on a wall at (x, y); dirn is the way it faces: '+y', '-y', '+x', '-x'."""
    if dirn in ('+y', '-y'):
        s = 1 if dirn == '+y' else -1
        y0, y1 = sorted((y, y + s * d))
        R.parts.add(box(x - w / 2, y0, z0, x + w / 2, y1, z1, m, skip=('-z',)))
        b0, b1 = sorted((y, y + s * (d + 0.06)))
        R.parts.add(box(x - w / 2 - 0.06, b0, z0, x + w / 2 + 0.06, b1, z0 + 0.3, m, skip=('-z',)))
    else:
        s = 1 if dirn == '+x' else -1
        x0, x1 = sorted((x, x + s * d))
        R.parts.add(box(x0, y - w / 2, z0, x1, y + w / 2, z1, m, skip=('-z',)))


def bust(R, x, y, face, z=0.0, ped='tile', stone='ivory', h=1.15):
    """A stone bust on a square pedestal, looking toward `face`."""
    R.parts.add(box(x - 0.3, y - 0.3, z, x + 0.3, y + 0.3, z + 0.12, ped, skip=('-z',)))
    R.parts.add(box(x - 0.22, y - 0.22, z + 0.12, x + 0.22, y + 0.22, z + h - 0.1, ped))
    R.parts.add(box(x - 0.3, y - 0.3, z + h - 0.1, x + 0.3, y + 0.3, z + h, ped))
    b = z + h
    g = Geo()
    g.add(lathe(0, 0, [(0.12, 0), (0.14, 0.04), (0.08, 0.1), (0.07, 0.12)], 12, stone))
    g.add(ellipsoid(-0.01, 0, 0.2, 0.13, 0.26, 0.17, stone))
    g.add(cyl(0, 0, 0.3, 0.42, 0.065, 10, side=stone, top=stone, bottom=stone))
    g.add(ellipsoid(0.01, 0, 0.55, 0.12, 0.105, 0.15, stone, 14, 8))
    R.parts.add(g.xform(face, x, y, b))


def ellipsoid(cx, cy, cz, rx, ry, rz, m='tile', segs=14, rings=8):
    g = sphere(0, 0, 0, 1.0, segs, rings, m)
    g.v = [(x * rx + cx, y * ry + cy, z * rz + cz) for (x, y, z) in g.v]
    return g


def urn(R, x, y, z=0.0, s=1.0, m='bronze', ped='tile', ph=0.9):
    R.parts.add(box(x - 0.28, y - 0.28, z, x + 0.28, y + 0.28, z + ph, ped, skip=('-z',)))
    R.parts.add(lathe(x, y, [(0.0, 0), (0.13 * s, 0), (0.14 * s, 0.04 * s), (0.07 * s, 0.1 * s), (0.2 * s, 0.3 * s), (0.25 * s, 0.45 * s),
                             (0.2 * s, 0.6 * s), (0.12 * s, 0.7 * s), (0.17 * s, 0.76 * s), (0.0, 0.76 * s)], 16, m).xform(0, 0, 0, z + ph))


def tree(R, x, y, z=0.0, h=3.2, r=1.1, seed=0):
    """A potted tree: a big pot, a trunk, a canopy of green spheres."""
    import random
    rnd = random.Random(seed)
    R.parts.add(lathe(x, y, [(0.0, 0), (0.34, 0), (0.46, 0.62), (0.52, 0.68), (0.52, 0.76), (0.0, 0.76)], 16, 'oxblood').xform(0, 0, 0, z))
    R.parts.add(cyl(x, y, z + 0.72, z + 0.74, 0.46, 16, side='slate', top='slate', bottom='slate'))
    R.parts.add(cyl(x, y, z + 0.7, z + h - r * 0.6, 0.08, 8, side='walnut', caps=False))
    for k in range(5):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.2, 0.55) * r if k else 0
        rr = r * rnd.uniform(0.55, 0.8) if k else r * 0.8
        R.nocol.add(sphere(x + math.cos(a) * d, y + math.sin(a) * d, z + h - r * 0.4 + rnd.uniform(-0.25, 0.3) * r, rr, 10, 5, 'green'))


def loop(R, pts, close=True, z=0.0):
    ids = [R.navpt(p[0], p[1], p[2] if len(p) > 2 else z) for p in pts]
    R.link(*(ids + ([ids[0]] if close else [])))
    return ids


def zpw(keys, a):
    """Piecewise-linear height at angle a from keys [(angle, z), ...] (angles increasing)."""
    if a <= keys[0][0]: return keys[0][1]
    for (a0, z0), (a1, z1) in zip(keys, keys[1:]):
        if a <= a1: return z0 + (z1 - z0) * (a - a0) / (a1 - a0)
    return keys[-1][1]


def spiral(cx, cy, r0, r1, keys, thick=0.3, step=math.radians(3), top='floor', side='tile', bottom='plaster', dz=0.0, a0=None, a1=None):
    """A band between radii r0 and r1 whose top follows zpw(keys, angle) + dz, from a0 to a1."""
    a0 = keys[0][0] if a0 is None else a0
    a1 = keys[-1][0] if a1 is None else a1
    n = max(1, int(math.ceil((a1 - a0) / step)))
    angs = [a0 + (a1 - a0) * k / n for k in range(n + 1)]
    for (ka, _) in keys:
        if a0 < ka < a1 and all(abs(ka - x) > 1e-6 for x in angs): angs.append(ka)
    angs.sort()
    g = Geo()
    zt = [zpw(keys, a) + dz for a in angs]
    P = lambda r, a, z: (cx + r * math.cos(a), cy + r * math.sin(a), z)
    it = [g.vert(P(r0, a, z)) for a, z in zip(angs, zt)]; ot = [g.vert(P(r1, a, z)) for a, z in zip(angs, zt)]
    ib = [g.vert(P(r0, a, z - thick)) for a, z in zip(angs, zt)]; ob = [g.vert(P(r1, a, z - thick)) for a, z in zip(angs, zt)]
    rm = (r0 + r1) / 2
    L = [(a - a0) * rm for a in angs]
    for k in range(len(angs) - 1):
        j = k + 1
        g.face([ot[k], ot[j], it[j], it[k]], top, [(L[k], r1), (L[j], r1), (L[j], r0), (L[k], r0)])
        g.face([ib[k], ib[j], ob[j], ob[k]], bottom, [(L[k], r0), (L[j], r0), (L[j], r1), (L[k], r1)])
        g.face([ob[k], ob[j], ot[j], ot[k]], side, [(L[k], zt[k] - thick), (L[j], zt[j] - thick), (L[j], zt[j]), (L[k], zt[k])])
        g.face([ib[j], ib[k], it[k], it[j]], side, [(L[j], zt[j] - thick), (L[k], zt[k] - thick), (L[k], zt[k]), (L[j], zt[j])])
    g.face([ib[0], ob[0], ot[0], it[0]], side, [(r0, 0), (r1, 0), (r1, thick), (r0, thick)])
    g.face([ob[-1], ib[-1], it[-1], ot[-1]], side, [(r1, 0), (r0, 0), (r0, thick), (r1, thick)])
    return g.fix()


def arc_rail(R, cx, cy, r, a0, a1, zf, h=0.95, m='brass', post='iron', spacing=1.1, step=math.radians(6), mid=True):
    """A rail along an arc at radius r from angle a0 to a1; zf(angle) gives the floor height under it."""
    L = abs(a1 - a0) * r
    n = max(1, int(math.ceil(abs(a1 - a0) / step)))
    angs = [a0 + (a1 - a0) * k / n for k in range(n + 1)]
    pts = [(cx + r * math.cos(a), cy + r * math.sin(a), zf(a)) for a in angs]
    V = R.nocol
    for (p0, p1) in zip(pts, pts[1:]):
        V.add(beam((p0[0], p0[1], p0[2] + h), (p1[0], p1[1], p1[2] + h), 0.06, 0.05, m))
        if mid: V.add(beam((p0[0], p0[1], p0[2] + h * 0.5), (p1[0], p1[1], p1[2] + h * 0.5), 0.03, 0.03, post))
        R.col.add(beam((p0[0], p0[1], p0[2] - 0.05), (p1[0], p1[1], p1[2] - 0.05), 0.08, h + 0.1, 'iron'))
    np_ = max(1, int(math.ceil(L / spacing)))
    for k in range(np_ + 1):
        a = a0 + (a1 - a0) * k / np_
        x, y, z = cx + r * math.cos(a), cy + r * math.sin(a), zf(a)
        V.add(box(x - 0.022, y - 0.022, z, x + 0.022, y + 0.022, z + h, post, skip=('-z',)))


def rot_pt(ang, x, y, cx=C / 2, cy=C / 2):
    """Local (x, y) about the centre -> world, turned by ang."""
    c, s = math.cos(ang), math.sin(ang)
    return (cx + x * c - y * s, cy + x * s + y * c)


def flight_rot(R, ang, x0, y0, z0, width, n, rise, run, axis, m='floor', riser=None, side='tile', cx=C / 2, cy=C / 2):
    """R.flight in a local frame centred on (cx, cy) and turned by ang (radians)."""
    R.nocol.add(stairs(x0, y0, z0, width, n, rise, run, axis, m, riser, side).xform(ang, cx, cy))
    L, Hh = n * run, n * rise
    if axis == '+y':   q = [(x0, y0 - 0.02, z0), (x0 + width, y0 - 0.02, z0), (x0 + width, y0 + L, z0 + Hh), (x0, y0 + L, z0 + Hh)]
    elif axis == '-y': q = [(x0, y0 + 0.02, z0), (x0, y0 - L, z0 + Hh), (x0 + width, y0 - L, z0 + Hh), (x0 + width, y0 + 0.02, z0)]
    elif axis == '+x': q = [(x0 - 0.02, y0, z0), (x0 + L, y0, z0 + Hh), (x0 + L, y0 + width, z0 + Hh), (x0 - 0.02, y0 + width, z0)]
    else:              q = [(x0 + 0.02, y0, z0), (x0 + 0.02, y0 + width, z0), (x0 - L, y0 + width, z0 + Hh), (x0 - L, y0, z0 + Hh)]
    g = Geo(); ids = [g.vert(p) for p in q]; g.face(ids, 'floor', [(0, 0)] * 4)
    a = [q[1][i] - q[0][i] for i in range(3)]; b = [q[2][i] - q[0][i] for i in range(3)]
    if a[0] * b[1] - a[1] * b[0] < 0: g.f = [tuple(reversed(f)) for f in g.f]
    R.col.add(g.xform(ang, cx, cy))


def flight_x(R, x0, y0, z0, width, n, rise, run, sgn, m='floor', side='tile', soffit=0.3):
    """A free-standing flight climbing along +x (sgn=1) or -x (sgn=-1) from its foot at x0, with a
    sloping soffit instead of a solid wedge, and the invisible ramp the feet ride."""
    L, H = n * run, n * rise
    prof = [(0.0, -soffit), (L, H - soffit), (L, H)]
    for i in range(n - 1, -1, -1):
        prof.append((i * run, (i + 1) * rise))
        if i > 0: prof.append((i * run, i * rise))
    prof.append((0.0, 0.0))
    mats = [side, side] + [m if k % 2 == 0 else side for k in range(len(prof) - 2)]
    mats[-1] = side
    pr = [(x0 + sgn * s, z0 + z) for s, z in prof]
    R.nocol.add(prism(pr, 'y', y0, y0 + width, mats, cap=side))
    q = [(x0 - sgn * 0.02, y0, z0), (x0 + sgn * L, y0, z0 + H), (x0 + sgn * L, y0 + width, z0 + H), (x0 - sgn * 0.02, y0 + width, z0)]
    g = Geo(); ids = [g.vert(p) for p in q]; g.face(ids, 'floor', [(0, 0)] * 4)
    a = [q[1][i] - q[0][i] for i in range(3)]; b = [q[2][i] - q[0][i] for i in range(3)]
    if a[0] * b[1] - a[1] * b[0] < 0: g.f = [tuple(reversed(f)) for f in g.f]
    R.col.add(g)
    return L, H
