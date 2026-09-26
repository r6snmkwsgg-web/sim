"""The Folded Corridor: a ring of corridors folded like paper, all creases and slanted planes, doors set in
sideways. At two of the creases the corridor folds for real: walk straight through and you have turned a
corner, into a leg that is somewhere else entirely, so the corridor turns right, then left, and you are
back where you began without ever having turned round. In the crease of the first fold, facing the wrong
way, there is a narrow door into the only flat room."""
from kit_h11 import *

W, D = 32.0, 16.0
BW = 3.6                       # the corridors' width
A0, A1 = T, T + BW             # south leg (y)
B0, B1 = D - T - BW, D - T     # north leg (y)
WX0, WX1 = T, T + BW           # west leg (x)
EX0, EX1 = W - T - BW, W - T   # east leg (x)
CH = 4.8                       # ceiling
OW, OH = 2.4, 3.0              # the folds' openings
FT = 0.25                      # half a fold's thickness
F1X, F1Y = 12.0, 11.0          # fold 1: in the south leg at x 12 -> out of the west leg at y 11, heading south
F2X, F2Y = 20.0, 5.0           # fold 2: in the north leg at x 20 (heading west) -> out of the east leg at y 5, heading north
SR = (12.6, 5.0, 18.8, 10.9)   # the flat room, in the block the ring goes round


def make():
    R = Room('folded', 2, 1, res=2048)
    R.sockets(floor='floor', wall='tile')
    ring(R)
    folds(R)
    creases(R)
    flat_room(R)
    dressing(R)
    ac, wc = (A0 + A1) / 2, (WX0 + WX1) / 2
    bc, ec = (B0 + B1) / 2, (EX0 + EX1) / 2
    portal(R, P((F1X - FT, ac, 0.0), (1, 0, 0), OW, OH), P((wc, F1Y + FT, 0.0), (0, -1, 0), OW, OH))
    portal(R, P((F2X + FT, bc, 0.0), (-1, 0, 0), OW, OH), P((ec, F2Y - FT, 0.0), (0, 1, 0), OW, OH))
    # walkers: round the ring
    navloop(R, [(wc, ac), (8.0, ac), (16.0, ac), (24.0, ac), (ec, ac), (ec, 8.0), (ec, bc), (24.0, bc), (16.0, bc), (8.0, bc), (wc, bc), (wc, 8.0)])
    secret(R, 16.0, 8.0, 0.0, 'The Flat Room',
           'In the crease of the fold, facing the way nobody walks, a narrow door, and behind it the only room here with four square walls and a level ceiling. On the table somebody has been trying to flatten a sheet of paper under books. It will not lie flat.', r=2.2)
    return done(R, 'The Folded Corridor', weight=3, probe=(16.0, (A0 + A1) / 2, 2.2), top=CH,
                blurb='A corridor folded like paper: creases in the ceiling, walls leaning in, doors set on their sides. You turn right at a fold, and then left at a corner, and you are back where you started. You have not turned round. You check.')


def ring(R):
    for (x0, y0, x1, y1) in ((T, A0, W - T, A1), (T, B0, W - T, B1), (WX0, T, WX1, D - T), (EX0, T, EX1, D - T)):
        R.cut(box(x0 - 0.01, y0 - 0.01, 0, x1 + 0.01, y1 + 0.01, CH, 'ivory', bottom='floor', top='plaster'))


def fold_frame(R, cx, cy, ang):
    """A crease across a corridor: a wall with an opening, its faces broken into slanted paper planes.
    ang is the plan angle of the corridor's axis (the frame spans across it). Built in local coords:
    x along the axis, y across."""
    g = Geo()
    hw = BW / 2 + 0.02
    g.add(box(-FT, -hw, 0, FT, -OW / 2, CH, 'ivory', skip=('+z', '-y')))
    g.add(box(-FT, OW / 2, 0, FT, hw, CH, 'ivory', skip=('+z', '+y')))
    g.add(box(-FT, -OW / 2, OH, FT, OW / 2, CH, 'ivory', skip=('+z',)))
    # paper planes on both faces: triangles leaning out from the crease
    for sx in (-1, 1):
        x0 = sx * FT
        for (p, q, r) in (((-hw, 0.0), (-OW / 2, 0.0), (-hw, CH * 0.8)), ((OW / 2, 0.0), (hw, 0.0), (hw, CH * 0.8)),
                          ((-OW / 2 - 0.1, OH + 0.05), (OW / 2 + 0.1, OH + 0.05), (0.0, CH))):
            P0 = (x0, p[0], p[1]); P1 = (x0, q[0], q[1]); P2 = (x0 + sx * 0.45, (p[0] + q[0] + r[0]) / 3, (p[1] + q[1] + r[1]) / 3)
            P3 = (x0, r[0], r[1])
            for tri in ((P0, P1, P2), (P1, P3, P2), (P3, P0, P2)):
                t = Geo(); ids = [t.vert(v) for v in tri]
                A = [tri[1][i] - tri[0][i] for i in range(3)]; B = [tri[2][i] - tri[0][i] for i in range(3)]
                cr = (A[1] * B[2] - A[2] * B[1])
                if cr * sx < 0: ids = ids[::-1]
                t.face(ids, 'walnut' if tri[0] is P0 and tri[1] is P1 else 'ivory', [(0, 0), (1, 0), (0, 1)])
                g.add(t)
        # an oak edge round the opening
        g.add(box(x0 - 0.06 if sx < 0 else x0, -OW / 2 - 0.12, 0, x0 if sx < 0 else x0 + 0.06, -OW / 2, OH + 0.12, 'oak'))
        g.add(box(x0 - 0.06 if sx < 0 else x0, OW / 2, 0, x0 if sx < 0 else x0 + 0.06, OW / 2 + 0.12, OH + 0.12, 'oak'))
        g.add(box(x0 - 0.06 if sx < 0 else x0, -OW / 2, OH, x0 if sx < 0 else x0 + 0.06, OW / 2, OH + 0.12, 'oak'))
    R.parts.add(g.xform(ang, cx, cy, 0))


def folds(R):
    ac, wc, bc, ec = (A0 + A1) / 2, (WX0 + WX1) / 2, (B0 + B1) / 2, (EX0 + EX1) / 2
    fold_frame(R, F1X, ac, 0.0)                 # south leg, crossing x
    fold_frame(R, wc, F1Y, math.pi / 2)         # west leg, crossing y
    fold_frame(R, F2X, bc, 0.0)                 # north leg
    fold_frame(R, ec, F2Y, math.pi / 2)         # east leg


def creases(R):
    """The folded-plate ceilings: zigzag planes across every leg, and slanted planes on the walls."""
    def zig(x0, x1, y0, y1, along, n, lo=CH - 0.75, hi=CH - 0.05, m='ivory'):
        g = Geo()
        for k in range(n):
            t0, t1, tm = k / n, (k + 1) / n, (k + 0.5) / n
            if along == 'x':
                a0, a1, am = x0 + (x1 - x0) * t0, x0 + (x1 - x0) * t1, x0 + (x1 - x0) * tm
                pts = [((a0, y0, hi), (am, y0, lo), (am, y1, lo), (a0, y1, hi)), ((am, y0, lo), (a1, y0, hi), (a1, y1, hi), (am, y1, lo))]
            else:
                a0, a1, am = y0 + (y1 - y0) * t0, y0 + (y1 - y0) * t1, y0 + (y1 - y0) * tm
                pts = [((x0, a0, hi), (x0, am, lo), (x1, am, lo), (x1, a0, hi)), ((x0, am, lo), (x0, a1, hi), (x1, a1, hi), (x1, am, lo))]
            for q in pts:
                t = Geo(); ids = [t.vert(v) for v in q]
                A = [q[1][i] - q[0][i] for i in range(3)]; B = [q[2][i] - q[0][i] for i in range(3)]
                if A[0] * B[1] - A[1] * B[0] > 0: ids = ids[::-1]     # face down
                t.face(ids, m, [(0, 0), (1, 0), (1, 1), (0, 1)])
                g.add(t)
        R.nocol.add(g)
    zig(WX1, EX0, A0, A1, 'x', 12)
    zig(WX1, EX0, B0, B1, 'x', 12)
    zig(WX0, WX1, T, D - T, 'y', 7)
    zig(EX0, EX1, T, D - T, 'y', 7)
    # slanted planes leaning off the walls high up, some with books on them, some with a door lying on its side
    rs = rng(7)
    bands = {}
    specs = [('S', 5.0), ('S', 16.5), ('S', 27.0), ('N', 4.5), ('N', 13.5), ('N', 25.5), ('Ni', 8.0), ('Ni', 16.0), ('Si', 20.5), ('Si', 25.0)]
    for (wall, x) in specs:
        if wall == 'S': y, nrm = A0, 1
        elif wall == 'Si': y, nrm = A1, -1
        elif wall == 'N': y, nrm = B1, -1
        else: y, nrm = B0, 1
        L = 2.6
        tilt = 0.5
        z0, z1 = 2.7, 4.3
        yb = y + nrm * 0.02
        yt = y + nrm * (z1 - z0) * math.tan(tilt)
        q = [(x - L / 2, yb, z0), (x + L / 2, yb, z0), (x + L / 2, yt, z1), (x - L / 2, yt, z1)]
        # a thick board: front face toward the corridor
        g = Geo(); ids = [g.vert(v) for v in q]
        A = [q[1][i] - q[0][i] for i in range(3)]; B = [q[2][i] - q[0][i] for i in range(3)]
        cr = (A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0])
        if cr[1] * nrm < 0: ids = ids[::-1]
        g.face(ids, 'walnut', [(0, 0), (L, 0), (L, 1), (0, 1)])
        R.nocol.add(g)
        # the plane's front normal and its up direction
        dv = [0.0, (yt - yb) / math.hypot(yt - yb, z1 - z0), (z1 - z0) / math.hypot(yt - yb, z1 - z0)]
        dn = [0.0, nrm * dv[2], -nrm * dv[1] * nrm * nrm]
        dn = [0.0, nrm * math.cos(tilt), -math.sin(tilt)]
        if rs.random() < 0.6:
            for r in range(3):
                p0 = [x - L / 2 + 0.08, yb + dv[1] * (0.08 + r * 0.5), z0 + dv[2] * (0.08 + r * 0.5)]
                p0 = [p0[0] + dn[0] * 0.01, p0[1] + dn[1] * 0.01, p0[2] + dn[2] * 0.01]
                merge_bands(bands, book_band(p0, [1, 0, 0], dv, dn, L - 0.16, 0.42, rs, seg=(0.08, 0.3)))
        else:
            # a door lying on its side in the plane
            c = [x, yb + dv[1] * 0.8 + dn[1] * 0.02, z0 + dv[2] * 0.8 + dn[2] * 0.02]
            pts = [[c[0] - 1.0, c[1] - dv[1] * 0.42, c[2] - dv[2] * 0.42], [c[0] + 1.0, c[1] - dv[1] * 0.42, c[2] - dv[2] * 0.42],
                   [c[0] + 1.0, c[1] + dv[1] * 0.42, c[2] + dv[2] * 0.42], [c[0] - 1.0, c[1] + dv[1] * 0.42, c[2] + dv[2] * 0.42]]
            gg = Geo(); ids = [gg.vert(tuple(v)) for v in pts]
            if cr[1] * nrm < 0: ids = ids[::-1]
            gg.face(ids, 'oak', [(0, 0), (2, 0), (2, 0.84), (0, 0.84)])
            R.nocol.add(gg)
            kn = [c[0] + 0.8 + dn[0] * 0.03, c[1] + dn[1] * 0.03, c[2] + dn[2] * 0.03]
            R.nocol.add(box(kn[0] - 0.04, kn[1] - 0.04, kn[2] - 0.04, kn[0] + 0.04, kn[1] + 0.04, kn[2] + 0.04, 'brass'))
    add_bands(R, bands)


def flat_room(R):
    """The flat room, in the block the ring goes round, and the narrow door to it in the crease of fold 1
    (on the fold's far side, where you only ever arrive walking west)."""
    x0, y0, x1, y1 = SR
    R.cut(box(x0, y0, 0, x1, y1, 3.2, 'plaster', bottom='floor', top='plaster'))
    # the door: in the south leg's north wall just east of fold 1, and a passage north to the room
    dx0, dx1 = F1X + FT + 0.55, F1X + FT + 1.35
    R.cut(box(dx0, A1 - 0.02, 0, dx1, y0 + 0.02, 2.2, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(dx0, y0 - 0.02, 0, x0 + 0.02, y0 + 1.0, 2.2, 'plaster', bottom='floor', top='plaster')) if dx1 < x0 else None
    R.parts.add(box(dx0 - 0.08, A1 - 0.1, 0, dx0, A1, 2.3, 'oak'))
    R.parts.add(box(dx1, A1 - 0.1, 0, dx1 + 0.08, A1, 2.3, 'oak'))
    R.parts.add(box(dx0 - 0.08, A1 - 0.1, 2.2, dx1 + 0.08, A1, 2.3, 'oak'))
    # inside: square, level, quiet
    rug(R, x0 + 1.0, y0 + 1.2, x1 - 1.0, y1 - 1.2, m='green')
    R.parts.add(ltable(15.0, 7.4, 17.4, 8.6, top='leather'))
    llamp(R, 15.3, 8.35, 0.76)
    for (bx, by) in ((16.0, 7.9), (16.7, 8.1)):
        book_pile(R, bx, by, 0.76, 3, rng(int(bx * 10)))
    R.nocol.add(panel_z(0.772, 15.7, 7.6, 16.9, 8.5, 'ivory'))
    R.parts.add(lchair(16.2, 6.8, math.pi / 2)); R.spot('sit', 16.2, 6.8, 0.48, math.pi / 2)
    for (face, bk, a, b) in (('-y', y1, x0 + 0.2, x1 - 0.2), ('+x', x0, y0 + 1.2, y1 - 0.2), ('-x', x1, y0 + 0.2, y1 - 0.2)):
        sh(R, face, bk, a, b, rows=6, frame='walnut')
    bulb(R, 16.2, 8.0, 2.4, r=0.1, m='e_lamp', top=3.2)
    R.spot('plaque', 16.0, y1 - 0.45, 1.4, -math.pi / 2, text='Everything here is square. Everything here is level. It took some doing.')


def dressing(R):
    ac, wc, bc, ec = (A0 + A1) / 2, (WX0 + WX1) / 2, (B0 + B1) / 2, (EX0 + EX1) / 2
    rows = 7
    # bookcases on the legs' walls, in runs between the doorways, folds and the flat room's door
    runs = [('+y', A0, [(1.0, 6.2), (9.8, 11.3), (12.9, 22.2), (25.8, 31.0)]),
            ('-y', A1, [(WX1 + 0.3, 11.3), (F1X + FT + 1.7, EX0 - 0.3)]),
            ('-y', B1, [(1.0, 6.2), (9.8, 19.5), (20.6, 22.2), (25.8, 31.0)]),
            ('+y', B0, [(WX1 + 0.3, 19.5), (20.6, EX0 - 0.3)]),
            ('+x', WX0, [(1.0, 6.2), (9.8, 10.5), (11.6, 15.0)]),
            ('-x', WX1, [(A1 + 0.3, 10.5), (11.6, B0 - 0.3)]),
            ('-x', EX1, [(1.0, 4.4), (5.6, 6.2), (9.8, 15.0)]),
            ('+x', EX0, [(A1 + 0.3, 4.4), (5.6, B0 - 0.3)])]
    for (face, bk, spans) in runs:
        for (a, b) in spans:
            if b - a > 0.7:
                sh(R, face, bk, a, b, rows=rows, frame='oak')
    # desks and green lamps in the corners, sconces along the legs
    for (x, y, a) in ((wc, ac, 0.0), (ec, bc, 0.0), (ec, ac, 0.0), (wc, bc, 0.0)):
        R.parts.add(ltable(x - 0.6, y - 0.4, x + 0.6, y + 0.4, top='leather'))
        llamp(R, x, y, 0.76)
        R.parts.add(lchair(x, y - 0.8, math.pi / 2))
    for x in (6.0, 10.0, 15.0, 18.0, 22.0, 26.0):
        pendant(R, x, ac, 3.4, CH - 0.1, r=0.2)
        pendant(R, x, bc, 3.4, CH - 0.1, r=0.2)
    for y in (3.0, 8.0, 13.0):
        pendant(R, wc, y, 3.4, CH - 0.1, r=0.2)
        pendant(R, ec, y, 3.4, CH - 0.1, r=0.2)
    for (x, y) in ((1.0, 1.0), (W - 1.0, D - 1.0), (W - 1.0, 1.0), (1.0, D - 1.0)):
        lantern(R, x, y, 0.0)
