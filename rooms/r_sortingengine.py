"""The Sorting Engine: a hall-sized machine for putting books in order. Belts cross the floor on iron
frames, turntables at every crossing slowly turn, brass arms swing over the belts holding a book each,
and in the middle a tall iron column carries a carousel of shelves. At the top of the column, reached by
a service ladder nobody is meant to climb, the control booth."""
from kit_h6 import *

W = D = 32.0
BL = (9.0, 23.0)               # belt centre lines: x = BL (running N-S) and y = BL (running E-W)
BE = (4.2, 27.8)               # the belts run from BE[0] to BE[1]
BZ = 0.5                       # belt top
BW = 1.2                       # belt width
TR = 1.35                      # turntable radius
CX = CY = 16.0                 # the column
BF = 5.0                       # booth floor
BR = 2.3                       # booth radius


def make():
    R = Room('sortingengine', 2, 2, res=2048)
    hall(R, h=TOP - 0.1, wall='tile', floor='terrazzo', ceil='plaster')
    rs = rng(53)
    walls(R)
    for c in BL:
        belt(R, 'y', c, rs)
        belt(R, 'x', c, rs)
    for x in BL:
        for y in BL:
            turntable(R, x, y, rs)
    for (x, y, a, ph) in ((16.0, 7.3, math.pi / 2, 0.0), (16.0, 24.7, -math.pi / 2, 0.3), (7.3, 16.0, 0.0, 0.55), (24.7, 16.0, math.pi, 0.8),
                          (11.5, 16.0, math.pi, 0.15), (20.5, 16.0, 0.0, 0.65)):
        arm(R, x, y, a, ph, rs)
    for (x, y) in ((6.0, 9.0), (26.0, 23.0), (9.0, 26.0), (23.0, 6.0)):
        chute(R, x, y)
    column(R, rs)
    booth(R, rs)
    overhead(R, rs)
    racks(R, rs)
    lamps(R)
    fx(R, 'dust', [T, T, 0.5, W - T, D - T, 7.2])
    # walking graph: the perimeter walk and the centre, over the belts at the middle of each side
    p = navloop(R, [(3.2, 3.2), (16, 3.2), (28.8, 3.2), (28.8, 16), (28.8, 28.8), (16, 28.8), (3.2, 28.8), (3.2, 16)])
    c = navloop(R, [(13.0, 13.0), (16, 12.0), (19.0, 13.0), (19.3, 16), (19.0, 19.0), (16, 21.3), (13.0, 19.0), (12.7, 16)])
    return finish(R, 'The Sorting Engine', weight=3, probe=(16, 11.0, 2.6),
                  blurb='The books go round on belts, are turned on turntables, are lifted by brass arms and put down again a little further on. Nothing is ever finished being sorted.')


def walls(R):
    rows = 15
    for (a, b) in ((0.7, 6.3), (9.7, 13.2), (18.8, 22.3), (25.7, D - 0.7)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
    # in the middle of every wall, a flywheel turning in an iron frame behind a rail
    for (x, y, ax, s) in ((T, 16.0, 'x', 1), (W - T, 16.0, 'x', -1), (16.0, T, 'y', 1), (16.0, D - T, 'y', -1)):
        flywheel(R, x, y, ax, s)
    for c in (8.0, 24.0):
        sh(R, '+y', T, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
        sh(R, '-y', D - T, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
        sh(R, '+x', T, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
        sh(R, '-x', W - T, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
    # a gallery rail and rolling ladders on the walls
    for (x, y, a) in ((T + 0.4, 12.0, 0.0), (W - T - 0.4, 20.0, math.pi), (12.0, T + 0.4, math.pi / 2), (20.0, D - T - 0.4, -math.pi / 2)):
        R.nocol.add(ladder(x - math.cos(a) * 0.05, y - math.sin(a) * 0.05, a, h=5.4, lean=1.0))


def flywheel(R, x, y, ax, s):
    """A great spoked wheel in a wall bay, turning (a spin mover about a level axis: drawn only)."""
    z = 3.4
    off = 0.75
    cx, cy = (x + s * off, y) if ax == 'x' else (x, y + s * off)
    # the bay: dark iron plates on the wall, a frame, a drive shaft up to the ceiling
    if ax == 'x':
        R.nocol.add(box(min(x, x + s * 0.05), y - 2.6, 0, max(x, x + s * 0.05), y + 2.6, TOP - 0.1, 'slate'))
        for yy in (y - 0.45, y + 0.45):
            R.parts.add(box(min(x, cx + s * 0.2), yy - 0.08, 0, max(x, cx + s * 0.2), yy + 0.08, z + 0.15, 'iron', skip=('-z',)))
        rail(R, x + s * 1.85, y - 2.5, x + s * 1.85, y + 2.5, 0.0)
    else:
        R.nocol.add(box(x - 2.6, min(y, y + s * 0.05), 0, x + 2.6, max(y, y + s * 0.05), TOP - 0.1, 'slate'))
        for xx in (x - 0.45, x + 0.45):
            R.parts.add(box(xx - 0.08, min(y, cy + s * 0.2), 0, xx + 0.08, max(y, cy + s * 0.2), z + 0.15, 'iron', skip=('-z',)))
        rail(R, x - 2.5, y + s * 1.85, x + 2.5, y + s * 1.85, 0.0)
    M = R.mover('spin', pivot=(cx, cy, z), axis=ax, speed=0.35 * s)
    M.nocol.add(wheel(cx, cy, z, 2.3, axis=ax, spokes=8, rim=0.16, w=0.2, m='iron', hub='brass', segs=28))
    M.nocol.add(gear(cx + (s * 0.25 if ax == 'x' else 0), cy + (s * 0.25 if ax == 'y' else 0), z, 0.8, 14, axis=ax, w=0.12, m='brass'))
    # the belt from the small gear up to a shaft under the ceiling
    for d in (-0.75, 0.75):
        if ax == 'x': R.nocol.add(beam((cx + s * 0.3, cy + d, z), (cx + s * 0.3, cy + d * 0.3, TOP - 0.45), 0.06, 'belt', 0.03))
        else: R.nocol.add(beam((cx + d, cy + s * 0.3, z), (cx + d * 0.3, cy + s * 0.3, TOP - 0.45), 0.06, 'belt', 0.03))
    if ax == 'x': R.nocol.add(roller(T, W - T, cy, TOP - 0.45, 0.1, 'iron', 10, axis='y') if False else solid_tube((cx + s * 0.3, T, TOP - 0.45), (cx + s * 0.3, D - T, TOP - 0.45), 0.09, 'iron', 10))
    else: R.nocol.add(solid_tube((T, cy + s * 0.3, TOP - 0.45), (W - T, cy + s * 0.3, TOP - 0.45), 0.09, 'iron', 10))


def overhead(R, rs):
    """A ring of belts on iron trestles at 3.4 m round the room, books shunting along it, fed by the chutes."""
    z = 3.4
    o0, o1 = 4.8, W - 4.8
    for (x0, y0, x1, y1, ax) in ((o0 - 0.5, o0 - 0.5, o1 + 0.5, o0 + 0.5, 'x'), (o0 - 0.5, o1 - 0.5, o1 + 0.5, o1 + 0.5, 'x'),
                                 (o0 - 0.5, o0 + 0.5, o0 + 0.5, o1 - 0.5, 'y'), (o1 - 0.5, o0 + 0.5, o1 + 0.5, o1 - 0.5, 'y')):
        R.nocol.add(box(x0, y0, z - 0.14, x1, y1, z, 'belt', sides='iron', bottom='iron'))
        for s_ in (0, 1):
            if ax == 'x': R.nocol.add(box(x0, (y0 - 0.05) if s_ == 0 else y1, z - 0.3, x1, (y0 if s_ == 0 else y1 + 0.05), z + 0.12, 'brass'))
            else: R.nocol.add(box((x0 - 0.05) if s_ == 0 else x1, y0, z - 0.3, (x0 if s_ == 0 else x1 + 0.05), y1, z + 0.12, 'brass'))
        L = (x1 - x0) if ax == 'x' else (y1 - y0)
        M = R.mover('slide', delta=((1.2, 0, 0) if ax == 'x' else (0, 1.2, 0)), period=8.0, pause=1.5, phase=rs.random())
        t = 0.6
        while t < L - 1.8:
            bk = box(-0.14, -0.1, 0, 0.14, 0.1, rs.uniform(0.05, 0.09), rs.choice(('oxblood', 'green', 'leather', 'walnut')), skip=('-z',))
            if ax == 'x': bk.xform(rs.uniform(-0.3, 0.3), x0 + t, (y0 + y1) / 2, z)
            else: bk.xform(math.pi / 2 + rs.uniform(-0.3, 0.3), (x0 + x1) / 2, y0 + t, z)
            M.nocol.add(bk)
            t += rs.uniform(0.8, 1.4)
        # trestles: pairs of legs, clear of the floor belts
        n = int(L / 4.6) + 1
        for k in range(n + 1):
            u = 0.3 + (L - 0.6) * k / n
            px, py = (x0 + u, (y0 + y1) / 2) if ax == 'x' else ((x0 + x1) / 2, y0 + u)
            if any(abs((px if ax == 'x' else py) - c) < 1.3 for c in BL + (16.0,)): continue
            for d in (-0.45, 0.45):
                qx, qy = (px, py + d) if ax == 'x' else (px + d, py)
                R.parts.add(box(qx - 0.05, qy - 0.05, 0, qx + 0.05, qy + 0.05, z - 0.14, 'iron', skip=('-z',)))
            R.nocol.add(box(px - (0.06 if ax == 'x' else 0.5), py - (0.5 if ax == 'x' else 0.06), z - 0.4, px + (0.06 if ax == 'x' else 0.5), py + (0.5 if ax == 'x' else 0.06), z - 0.14, 'iron'))
    # hangers from the ceiling
    for (x, y) in ((o0, o0), (o1, o0), (o1, o1), (o0, o1)):
        R.nocol.add(box(x - 0.04, y - 0.04, z, x + 0.04, y + 0.04, TOP - 0.1, 'iron'))


def racks(R, rs):
    """Pigeonhole racks round the column: short cases of cubbies, a book or two in each."""
    for (x, y, a) in ((11.0, 11.0, math.pi / 4), (21.0, 11.0, 3 * math.pi / 4), (21.0, 21.0, -3 * math.pi / 4), (11.0, 21.0, -math.pi / 4)):
        ang_shelf(R, x, y, a, 2.4, rows=4, frame='oak')


def belt(R, ax, c, rs):
    """One belt on its iron frame, between the turntables; books lying on it shunt along (a slide mover)."""
    segs = [(BE[0], BL[0] - TR - 0.05), (BL[0] + TR + 0.05, BL[1] - TR - 0.05), (BL[1] + TR + 0.05, BE[1])]
    for (a, b) in segs:
        if ax == 'y': x0, y0, x1, y1 = c - BW / 2, a, c + BW / 2, b
        else: x0, y0, x1, y1 = a, c - BW / 2, b, c + BW / 2
        R.parts.add(box(x0, y0, BZ - 0.08, x1, y1, BZ, 'belt', sides='iron', bottom='iron'))
        # side frames, lips and legs
        for s in (0, 1):
            if ax == 'y':
                xs = x0 - 0.06 if s == 0 else x1
                R.parts.add(box(xs, y0, 0.12, xs + 0.06, y1, BZ + 0.06, 'iron'))
            else:
                ys = y0 - 0.06 if s == 0 else y1
                R.parts.add(box(x0, ys, 0.12, x1, ys + 0.06, BZ + 0.06, 'iron'))
        L = b - a
        n = max(2, int(L / 1.6) + 1)
        for k in range(n):
            t = a + 0.15 + (L - 0.3) * k / (n - 1)
            if ax == 'y': R.parts.add(box(x0, t - 0.06, 0, x1, t + 0.06, 0.12, 'iron', skip=('-z',)))
            else: R.parts.add(box(t - 0.06, y0, 0, t + 0.06, y1, 0.12, 'iron', skip=('-z',)))
        # rollers showing at the ends
        for t in (a + 0.06, b - 0.06):
            if ax == 'y': R.nocol.add(roller(x0, x1, t, BZ - 0.1, 0.07, 'chrome', 10))
            else: R.nocol.add(roller(y0, y1, t, BZ - 0.1, 0.07, 'chrome', 10, axis='y'))
        # the books riding it
        step = 1.6 if L > 6 else 1.3
        M = R.mover('slide', delta=((0, step * 0.8, 0) if ax == 'y' else (step * 0.8, 0, 0)), period=7.0 + rs.uniform(-0.5, 0.5), pause=1.2, phase=rs.random())
        k = 0
        t = a + 0.5
        while t < b - 0.5 - step * 0.8:
            wv, lv = rs.uniform(0.18, 0.26), rs.uniform(0.25, 0.34)
            hh = rs.uniform(0.04, 0.09)
            bk = box(-lv / 2, -wv / 2, 0, lv / 2, wv / 2, hh, rs.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet')), skip=('-z',))
            bk.add(box(-lv / 2 + 0.01, -wv / 2 - 0.004, 0.008, lv / 2 - 0.01, wv / 2 - 0.02, hh - 0.008, 'ivory', skip=('-z',)))
            ang = rs.uniform(-0.3, 0.3) + (math.pi / 2 if ax == 'y' else 0)
            if ax == 'y': bk.xform(ang, c + rs.uniform(-0.2, 0.2), t, BZ)
            else: bk.xform(ang, t, c + rs.uniform(-0.2, 0.2), BZ)
            M.nocol.add(bk)
            t += step * rs.uniform(0.7, 1.0)
            k += 1


def turntable(R, x, y, rs):
    """A brass-rimmed disc at a crossing, turning slowly: stand on it and it takes you round."""
    R.parts.add(cyl(x, y, 0, BZ - 0.1, TR - 0.1, 24, side='iron', top='iron', bottom='iron'))
    M = R.mover('spin', pivot=(x, y, 0), axis='z', speed=0.12 * (1 if (x + y) % 2 == 0 else -1))
    M.parts.add(cyl(x, y, BZ - 0.1, BZ, TR, 28, side='brass', top='belt', bottom='iron'))
    M.nocol.add(ring(x, y, BZ, BZ + 0.012, TR - 0.12, TR - 0.05, 28, top='brass', bottom='brass', inner='brass', outer='brass'))
    M.nocol.add(ring(x, y, BZ, BZ + 0.012, 0.25, 0.32, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
    for k in range(3):
        a = 2 * math.pi * k / 3 + rs.uniform(0, 1)
        bk = box(-0.15, -0.1, 0, 0.15, 0.1, 0.06, rs.choice(('oxblood', 'green', 'leather')), skip=('-z',))
        M.nocol.add(bk.xform(a + 1.2, x + math.cos(a) * 0.8, y + math.sin(a) * 0.8, BZ))


def arm(R, x, y, a, ph, rs):
    """A brass arm on an iron post beside a belt: shoulder, elbow, a gripper holding a book, swinging
    slowly over the belt (drawn only, high enough to walk under)."""
    R.parts.add(cyl(x, y, 0, 0.12, 0.35, 12, side='iron', top='iron'))
    R.parts.add(cyl(x, y, 0.12, 3.4, 0.12, 10, side='iron', caps=False))
    R.nocol.add(cyl(x, y, 3.4, 3.7, 0.22, 12, side='brass', top='brass', bottom='brass'))
    M = R.mover('swing', pivot=(x, y, 3.5), axis='z', amp=0.55, period=9.0 + rs.uniform(-1, 1), phase=ph)
    ca, sa = math.cos(a), math.sin(a)
    sh_ = (x, y, 3.55)
    el = (x + ca * 1.4, y + sa * 1.4, 4.3)
    wr = (x + ca * 2.4, y + sa * 2.4, 3.2)
    M.nocol.add(beam(sh_, el, 0.14, 'brass', 0.18))
    M.nocol.add(beam(el, wr, 0.1, 'brass', 0.12))
    M.nocol.add(sphere(el[0], el[1], el[2], 0.16, 10, 5, 'brass'))
    M.nocol.add(sphere(wr[0], wr[1], wr[2], 0.1, 8, 4, 'brass'))
    M.nocol.add(cyl(wr[0], wr[1], 2.75, wr[2], 0.04, 6, side='chrome', caps=False))
    # the gripper and its book
    for s in (-1, 1):
        px, py = wr[0] - sa * 0.14 * s, wr[1] + ca * 0.14 * s
        M.nocol.add(box(px - 0.02, py - 0.02, 2.45, px + 0.02, py + 0.02, 2.78, 'brass'))
    bk = box(-0.1, -0.12, 0, 0.1, 0.12, 0.28, rs.choice(('oxblood', 'green', 'leather')))
    M.nocol.add(bk.xform(a, wr[0], wr[1], 2.42))
    R.nocol.add(cyl(x, y, 3.7, TOP - 0.1, 0.03, 6, side='iron', caps=False))


def chute(R, x, y):
    """A brass trumpet from the ceiling, dropping books onto the belt ends."""
    R.nocol.add(frustum(x, y, 2.8, 3.6, 0.55, 0.28, 16, 'brass', inner='brass'))
    R.nocol.add(cyl(x, y, 3.6, TOP - 0.1, 0.28, 14, side='brass', caps=False))
    for z in (4.6, 6.0):
        R.nocol.add(ring(x, y, z, z + 0.08, 0.28, 0.33, 14, top='brass', bottom='brass', inner='brass', outer='brass'))


def column(R, rs):
    """The iron column in the middle, a two-tier carousel of shelves turning round it."""
    R.parts.add(cyl(CX, CY, 0, TOP - 0.1, 0.55, 16, side='iron', top='iron'))
    R.parts.add(cyl(CX, CY, 0, 0.35, 1.0, 20, side='iron', top='iron'))
    for z in (1.2, 2.2, 3.2, 4.2):
        R.nocol.add(ring(CX, CY, z, z + 0.1, 0.55, 0.64, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
    M = R.mover('spin', pivot=(CX, CY, 0), axis='z', speed=0.08)
    for (z0, r) in ((2.3, 1.7),):
        M.nocol.add(ring(CX, CY, z0, z0 + 0.06, 0.6, r, 32, top='iron', bottom='iron', inner='iron', outer='iron'))
        M.nocol.add(ring(CX, CY, z0 + 1.3, z0 + 1.36, 0.6, r, 32, top='iron', bottom='iron', inner='iron', outer='iron'))
        for k in range(8):
            a = 2 * math.pi * k / 8
            # radial bookcase fins with books on both faces
            g = Geo()
            g.add(box(0.6, -0.02, z0 + 0.06, r, 0.02, z0 + 1.3, 'walnut'))
            for j in range(3):
                zz = z0 + 0.06 + j * 0.42
                g.add(box(0.62, -0.17, zz, r - 0.02, 0.17, zz + 0.03, 'walnut'))
                n = 5
                for i in range(n):
                    u = 0.66 + (r - 0.72) * i / n
                    for s in (-1, 1):
                        hb = rs.uniform(0.26, 0.36)
                        g.add(box(u, s * 0.02, zz + 0.03, u + (r - 0.72) / n * 0.9, s * 0.15, zz + 0.03 + hb,
                                  rs.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet', 'bronze')), skip=('-z',)))
            M.nocol.add(g.xform(a, CX, CY, 0))
    # the ladder up the column's north side to the booth
    climb_ladder(R, CX, CY + BR * math.cos(math.pi / 8) + 0.07, 0.0, BF, math.pi / 2, run=2.3, w=0.6, m='iron', rails='iron')


def booth(R, rs):
    """The control booth round the top of the column: an octagonal walnut cabin with windows all round,
    a ring of levers and dials, a stool, a lamp, the log."""
    n = 8
    pts = [(CX + BR * math.cos(2 * math.pi * (k + 0.5) / n), CY + BR * math.sin(2 * math.pi * (k + 0.5) / n)) for k in range(n)]
    R.parts.add(poly_prism(pts, BF - 0.06, BF, side='brass', top='floor', bottom='iron'))
    R.nocol.add(poly_prism([(CX + (BR - 0.35) * math.cos(2 * math.pi * (k + 0.5) / n), CY + (BR - 0.35) * math.sin(2 * math.pi * (k + 0.5) / n)) for k in range(n)],
                           BF - 0.35, BF - 0.06, side='iron', top='iron', bottom='iron'))
    # iron brackets under it
    for k in range(4):
        a = 2 * math.pi * (k + 0.5) / 4
        R.nocol.add(beam((CX + math.cos(a) * 0.55, CY + math.sin(a) * 0.55, BF - 1.2), (CX + math.cos(a) * BR * 0.9, CY + math.sin(a) * BR * 0.9, BF - 0.3), 0.12, 'iron'))
    # walls: a parapet on every side but the one the ladder comes up, posts, a band, a roof
    top = TOP - 0.1
    for k in range(n):
        p0, p1 = pts[k], pts[(k + 1) % n]
        mid_a = math.atan2((p0[1] + p1[1]) / 2 - CY, (p0[0] + p1[0]) / 2 - CX)
        gap = abs(math.sin(mid_a) - 1.0) < 0.1
        spans = [(p0, p1)] if not gap else [(p0, (p0[0] + (p1[0] - p0[0]) * 0.2, p0[1] + (p1[1] - p0[1]) * 0.2)),
                                            ((p0[0] + (p1[0] - p0[0]) * 0.8, p0[1] + (p1[1] - p0[1]) * 0.8), p1)]
        for (q0, q1) in spans:
            R.parts.add(obox(q0[0], q0[1], q1[0], q1[1], BF, BF + 1.05, 0.1, 'walnut'))
            R.nocol.add(obox(q0[0], q0[1], q1[0], q1[1], BF + 1.05, BF + 1.1, 0.16, 'brass'))
        R.nocol.add(obox(p0[0], p0[1], p1[0], p1[1], BF + 2.1, BF + 2.35, 0.1, 'walnut'))
        R.nocol.add(box(p0[0] - 0.06, p0[1] - 0.06, BF, p0[0] + 0.06, p0[1] + 0.06, BF + 2.35, 'walnut', skip=('-z',)))
    R.nocol.add(poly_prism([(CX + (BR + 0.25) * math.cos(2 * math.pi * (k + 0.5) / n), CY + (BR + 0.25) * math.sin(2 * math.pi * (k + 0.5) / n)) for k in range(n)],
                           BF + 2.35, BF + 2.5, side='walnut', top='walnut', bottom='plaster'))
    # the control ring: a desk round the column with levers and dials
    R.parts.add(ring(CX, CY, BF, BF + 0.95, 0.55, 1.05, 24, top='leather', bottom='walnut', inner='walnut', outer='walnut'))
    for k in range(10):
        a = 2 * math.pi * k / 10 + 0.3
        if abs(math.sin(a) - 1) < 0.25: continue
        x, y = CX + math.cos(a) * 0.9, CY + math.sin(a) * 0.9
        R.nocol.add(beam((x, y, BF + 0.95), (x + math.cos(a) * 0.12, y + math.sin(a) * 0.12, BF + 1.3), 0.025, 'brass'))
        R.nocol.add(sphere(x + math.cos(a) * 0.12, y + math.sin(a) * 0.12, BF + 1.32, 0.04, 6, 3, 'oxblood'))
        xd, yd = CX + math.cos(a + 0.3) * 0.8, CY + math.sin(a + 0.3) * 0.8
        R.nocol.add(cyl(xd, yd, BF + 0.95, BF + 0.97, 0.09, 12, side='brass', top='ivory'))
    R.parts.add(stool(CX + 0.4, CY - 1.5, math.pi / 2, back=False))
    R.light(sphere(CX - 1.2, CY - 1.2, BF + 1.9, 0.08, 8, 4, 'e_amber'))
    for k in range(3):
        a = 2 * math.pi * k / 3 + 1.0
        pendant(R, CX + math.cos(a) * 1.6, CY + math.sin(a) * 1.6, BF + 1.85, BF + 2.35, r=0.14)
    R.nocol.add(cyl(CX - 1.2, CY - 1.2, BF + 1.95, BF + 2.35, 0.01, 4, side='iron', caps=False))
    R.light(obox(CX - 0.3, CY - 0.8, CX + 0.3, CY - 0.8, BF + 0.97, BF + 0.99, 0.2, 'e_green'))
    open_book(R, CX + 0.8, CY - 0.4, BF + 0.95, 1.2)
    R.spot('plaque', CX, CY - 1.5, BF, -math.pi / 2,
           text='OPERATOR\'S LOG. Day unknown. Sorted by colour, then by weight, then by the first letter of the last word. '
                'Tomorrow, by how sad they are. It is all the same order in the end.')
    secret(R, CX + 0.2, CY - 1.6, BF, 'The Control Booth',
           'Up the ladder, round the top of the column, a booth where someone sat and ran the engine. The levers still move. None of them is connected to anything.')


def lamps(R):
    for c in BL:
        for t in (5.6, 12.6, 19.4, 26.4):
            pendant(R, c, t, 3.8, TOP - 0.1, r=0.22)
            pendant(R, t, c, 3.8, TOP - 0.1, r=0.22)
    for (x, y) in ((3.0, 3.0), (29.0, 3.0), (29.0, 29.0), (3.0, 29.0)):
        R.light(sphere(x, y, 2.4, 0.09, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, y, 2.45, TOP - 0.1, 0.01, 4, side='iron', caps=False))
