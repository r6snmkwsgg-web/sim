"""The Clockwork Nave: a two-storey hall whose end walls are machinery, brass gears as tall as the room
turning into one another behind rails; a great pendulum swings from the vault. The middle of the floor
is a dial fifteen metres across, and it turns, slowly, carrying whoever stands on it round like the hand
of a clock. Galleries run along both sides of the upper floor, joined by a bridge over the dial. Under
the dial is the engine that turns it; a clock case in the north aisle hides the stair down."""
from kit_h12 import *

W = D = 32.0
H = 2 * LH - (LH - TOP)         # 15.6
CX = CY = 16.0
DR = 7.5                        # the dial
EZ = -1.95                      # the engine room floor (kept above -2: below that is the floor below's)
DZ = 1.2                        # the dial's top: it turns on a low dais
GW = 4.5                        # gallery depth (S and N walls)
BX0, BX1 = 14.8, 17.2           # the bridge
SEAL = [('W', 0, 1), ('W', 1, 1), ('E', 0, 1), ('E', 1, 1)]


def make():
    R = Room('clockwork', 2, 2, levels=2, res=2048)
    rs = rng(50)
    seal(R, SEAL, floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H - 0.1, 'tile', bottom='floor', top='plaster'))
    galleries(R, rs)
    stair(R)
    gears(R, rs)
    dial(R, rs)
    engine(R, rs)
    way_down(R, rs)
    lamps(R)
    fx(R, 'dust', [3.0, 5.0, 0.5, 29.0, 27.0, 14.0])
    P = {'w1': (1.6, 8.0), 'w2': (1.6, 24.0), 'e1': (30.4, 8.0), 'e2': (30.4, 24.0), 's1': (8.0, 1.6), 's2': (24.0, 1.6),
         'n1': (8.0, 30.4), 'n2': (24.0, 30.4), 'a': (5.0, 3.0), 'b': (16.0, 3.0), 'c': (27.0, 3.0), 'd': (27.0, 16.0), 'e': (27.0, 29.0),
         'f': (16.0, 29.0), 'g': (5.0, 29.0), 'h': (5.0, 16.0),
         'u1': (8.0, 2.5, 8.0), 'u2': (16.0, 2.5, 8.0), 'u3': (24.0, 2.5, 8.0), 'u4': (8.0, 29.5, 8.0), 'u5': (16.0, 29.5, 8.0), 'u6': (24.0, 29.5, 8.0),
         'v1': (16.0, 12.0, 8.0), 'v2': (16.0, 20.0, 8.0), 'k0': (10.0, 7.2), 'k1': (23.4, 5.4, 8.0)}
    navgrid(R, P, [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g'), ('g', 'h'), ('h', 'a'),
                   ('a', 's1'), ('c', 's2'), ('g', 'n1'), ('e', 'n2'), ('h', 'w1'), ('h', 'w2'), ('d', 'e1'), ('d', 'e2'),
                   ('u1', 'u2'), ('u2', 'u3'), ('u4', 'u5'), ('u5', 'u6'), ('u2', 'v1'), ('v1', 'v2'), ('v2', 'u5'), ('u3', 'k1')])
    secret(R, CX, CY + 4.5, EZ, 'The Engine Under the Dial',
           'Behind the clock in the north aisle a stair goes down, and under the turning floor is what turns it: a ring of teeth as wide as the room, three pinions, a flywheel, and no one minding any of it.', r=3.0)
    return finish(R, 'The Clockwork Nave', weight=3, probe=(CX, 7.6, 2.4), top=H - 0.1, bot=EZ,
                  blurb='The walls are gears and the floor is a clock, and the floor is going round. Stand still on it long enough and you will have been everywhere in the room without taking a step.')


# ---------------------------------------------------------------------------
def galleries(R, rs):
    """Galleries along the south and north walls at the upper floor, a bridge between them over the dial;
    cases on the walls of both floors."""
    for (y0, y1, s) in ((T, GW, 1), (D - GW, D - T, -1)):
        R.parts.add(box(T, y0, LH - 0.4, W - T, y1, LH, 'walnut', top='floor', bottom='plaster'))
        edge = y1 if s > 0 else y0
        R.parts.add(box(T, edge - 0.15, LH - 0.7, W - T, edge + 0.15, LH - 0.4, 'walnut'))
        # the rail, with gaps for the bridge and (south) the stair landing
        gaps = [(BX0, BX1)] + ([(22.2, 23.8)] if s > 0 else [])
        xs = [T + 0.05]
        for (a, b) in sorted(gaps): xs += [a, b]
        xs.append(W - T - 0.05)
        for k in range(0, len(xs), 2):
            brass_rail(R, xs[k], edge - s * 0.06, xs[k + 1], edge - s * 0.06, LH, h=1.0)
        # brackets under the edge
        for x in [2.0 + 4.0 * k for k in range(8)]:
            R.nocol.add(beam((x, edge - s * 1.2, LH - 1.6), (x, edge - s * 0.05, LH - 0.45), 0.14, 'walnut'))
        # cases on the walls, both floors (the upper ones behind the gallery)
        wy = T if s > 0 else D - T
        for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
            sh(R, '+y' if s > 0 else '-y', wy, a, b, rows=9, frame='walnut')
            sh(R, '+y' if s > 0 else '-y', wy, a, b, z=LH, rows=10, frame='walnut')
    # the bridge
    R.parts.add(box(BX0, GW - 0.05, LH - 0.35, BX1, D - GW + 0.05, LH, 'walnut', top='floor', bottom='iron'))
    for x in (BX0 + 0.06, BX1 - 0.06):
        brass_rail(R, x, GW, x, D - GW, LH, h=1.0)
    for y in (GW + 2.0, D - GW - 2.0):
        R.nocol.add(box(BX0 - 0.1, y - 0.1, LH - 0.8, BX1 + 0.1, y + 0.1, LH - 0.35, 'iron'))
    # under the bridge, iron trusses
    R.nocol.add(beam((CX, GW, LH - 1.4), (CX, D - GW, LH - 1.4), 0.12, 'iron'))
    for k in range(12):
        y = GW + (D - 2 * GW) * (k + 0.5) / 12
        R.nocol.add(beam((CX, y - 0.8, LH - 0.36), (CX, y, LH - 1.4), 0.06, 'iron'))
        R.nocol.add(beam((CX, y + 0.8, LH - 0.36), (CX, y, LH - 1.4), 0.06, 'iron'))


def stair(R):
    """A long hung flight up the south side of the nave, climbing east to the south gallery."""
    n, rise, run = 40, LH / 40, 0.3
    x0, y0, wd = 10.2, GW + 0.1, 1.6
    rflight(R, x0, y0, 0.0, wd, n, rise, run, '+x', m='oak', riser='walnut', side='walnut', soffit='walnut')
    x1 = x0 + n * run
    R.parts.add(box(x1, GW - 0.02, LH - 0.35, x1 + 1.6, y0 + wd, LH, 'walnut', top='floor'))
    for yy in (y0 + 0.03, y0 + wd - 0.03):
        stair_rail(R, x0, yy, rise, x1, yy, LH)
    brass_rail(R, x1 + 1.6, GW, x1 + 1.6, y0 + wd, LH, h=1.0)
    brass_rail(R, x1, y0 + wd, x1 + 1.6, y0 + wd, LH, h=1.0)


def gears(R, rs):
    """On each end wall: a gear eleven metres across and two smaller ones meshed with it, turning, drawn
    only, behind a rail; a smaller train on the south and north walls under the galleries."""
    for (xw, s) in ((T, 1), (W - T, -1)):
        x = xw + s * 0.55
        train = [(16.0, 7.8, 5.5, 0.05), (16.0 + 5.3, 7.8 + 5.6, 2.2, None), (16.0 - 5.2, 7.8 + 5.3, 1.5, None)]
        w1 = train[0][3] * s
        for k, (y, z, r, _) in enumerate(train):
            sp = w1 if k == 0 else -w1 * train[0][2] / r
            M = R.mover('spin', pivot=(x, y, z), axis='x', speed=round(sp, 4), phase=rs.uniform(0, 1))
            M.nocol.add(gear(x, y, z, r, max(10, int(r * 6)), axis='x', w=0.3, m='brass', spokes=6 if r > 2 else 4))
            # the arbor and a boss on the wall
            R.nocol.add(solid_tube((xw, y, z), (x + s * 0.3, y, z), r * 0.12, 'iron', 12))
        # iron plates on the wall behind the train
        R.nocol.add(box(min(xw, xw + s * 0.04), 9.8, 1.8, max(xw, xw + s * 0.04), 22.2, H - 0.3, 'slate'))
        rx = xw + s * 2.1
        brass_rail(R, rx, 9.9, rx, 22.1, 0.0, h=1.0)
        for (y0, y1) in ((9.9, 9.9), (22.1, 22.1)):
            brass_rail(R, xw, y0, rx, y1, 0.0, h=1.0)
    # under the galleries: a train on each long wall, between the doorways
    for (yw, s) in ((T, 1), (D - T, -1)):
        y = yw + s * 0.5
        for (x, z, r, sp) in ((16.0, 3.4, 2.6, 0.08), (16.0 + 4.3, 4.9, 1.6, -0.08 * 2.6 / 1.6), (16.0 - 4.4, 4.6, 1.7, -0.08 * 2.6 / 1.7)):
            M = R.mover('spin', pivot=(x, y, z), axis='y', speed=round(sp * s, 4), phase=rs.uniform(0, 1))
            M.nocol.add(gear(x, y, z, r, max(10, int(r * 6)), axis='y', w=0.25, m='brass', spokes=5))
        ry = yw + s * 1.6
        brass_rail(R, 10.2, ry, 21.8, ry, 0.0, h=1.0)
        for x in (10.2, 21.8):
            brass_rail(R, x, yw, x, ry, 0.0, h=1.0)
    # the great pendulum, from the vault, swinging across the bridge
    M = R.mover('swing', pivot=(CX, CY, H - 0.3), axis='y', amp=0.28, period=8.0)
    M.nocol.add(beam((CX, CY, H - 0.3), (CX, CY, 12.2), 0.08, 'brass'))
    g = cyl(0, 0, -0.12, 0.12, 0.8, 24, side='gilt', top='gilt', bottom='gilt'); rot(g, 'x', math.pi / 2); g.xform(0, CX, CY, 11.4)
    M.nocol.add(g)
    R.nocol.add(box(CX - 0.6, CY - 0.6, H - 0.4, CX + 0.6, CY + 0.6, H, 'brass'))


def dial(R, rs):
    """The turning floor: a disc 15 m across, flush with the floor, inlaid as a clock face, turning once
    every two and a half minutes. Benches and lecterns ride on it; a brass column at its middle."""
    for (r0, r1, z) in ((DR + 0.05, DR + 0.6, DZ), (DR + 0.6, DR + 1.1, DZ - 0.4), (DR + 1.1, DR + 1.6, DZ - 0.8)):
        R.parts.add(ring(CX, CY, 0.0, z, r0, r1, 64, top='terrazzo', bottom='terrazzo', inner='brass' if r0 < DR + 0.1 else 'tile', outer='tile'))
    M = R.mover('spin', pivot=(CX, CY, 0), axis='z', speed=0.04)
    M.parts.add(cyl(CX, CY, DZ - 0.3, DZ, DR, 64, side='brass', top='terrazzo', bottom='iron'))
    # the face: rings, hour marks, two hands
    for (r0, r1, m) in ((DR - 0.25, DR - 0.1, 'brass'), (DR - 1.9, DR - 1.8, 'brass'), (2.1, 2.2, 'brass'), (0.9, 1.4, 'walnut')):
        M.nocol.add(ring(CX, CY, DZ, DZ + 0.006, r0, r1, 64, top=m, bottom=m, inner=m, outer=m))
    for k in range(60):
        a = 2 * math.pi * k / 60
        L0 = DR - 1.75 if k % 5 == 0 else DR - 0.95
        w = 0.14 if k % 5 == 0 else 0.04
        M.nocol.add(obox(CX + math.cos(a) * L0, CY + math.sin(a) * L0, CX + math.cos(a) * (DR - 0.3), CY + math.sin(a) * (DR - 0.3), DZ, DZ + 0.007, w, 'gilt' if k % 5 == 0 else 'walnut'))
    for (a, L, w) in ((0.6, DR - 2.4, 0.35), (2.3, DR - 1.2, 0.2)):
        M.nocol.add(obox(CX, CY, CX + math.cos(a) * L, CY + math.sin(a) * L, DZ, DZ + 0.009, w, 'bronze'))
        tip = (CX + math.cos(a) * L, CY + math.sin(a) * L)
        M.nocol.add(cyl(tip[0], tip[1], DZ, DZ + 0.009, w * 1.1, 10, side='bronze', top='bronze'))
    # the column in the middle (turns with it)
    M.parts.add(cyl(CX, CY, DZ, DZ + 0.3, 1.0, 20, side='brass', top='brass'))
    M.parts.add(cyl(CX, CY, DZ + 0.3, DZ + 3.4, 0.35, 16, side='brass', top='brass'))
    for z in (1.2, 2.2, 3.1):
        M.nocol.add(ring(CX, CY, DZ + z, DZ + z + 0.1, 0.35, 0.75 - 0.15 * (z - 1.2), 20, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    M.nocol.add(sphere(CX, CY, DZ + 3.6, 0.3, 12, 6, 'gilt'))
    # benches and lecterns riding round
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        bx, by = CX + math.cos(a) * 4.2, CY + math.sin(a) * 4.2
        b = Geo()
        b.add(box(-0.9, -0.22, 0.0, 0.9, 0.22, 0.45, 'walnut', top='leather'))
        b.add(box(-0.9, 0.18, 0.45, 0.9, 0.24, 0.9, 'walnut'))
        M.parts.add(b.xform(a + math.pi / 2, bx, by, DZ))
        la = a + math.pi / 4
        lx, ly = CX + math.cos(la) * 5.8, CY + math.sin(la) * 5.8
        l = Geo()
        l.add(box(-0.08, -0.08, 0.0, 0.08, 0.08, 1.0, 'walnut'))
        l.add(box(-0.3, -0.22, 1.0, 0.3, 0.22, 1.08, 'walnut', top='leather'))
        M.parts.add(l.xform(la, lx, ly, DZ))
        ob = Geo(); book_row_geo(ob, rs, -0.2, 0.2, -0.1, 1.08, depth=0.18, hmin=0.03, hmax=0.05)
        M.nocol.add(ob.xform(la, lx, ly, DZ))


def engine(R, rs):
    """Under the dial: a round chamber; the dial's ring of teeth and its trusses overhead (turning with it),
    three pinions meshed with the ring, a flywheel and its belt."""
    R.cut(cyl(CX, CY, EZ, 0.02, DR - 0.2, 48, side='tile', top='iron', bottom='floor'))
    M = R.mover('spin', pivot=(CX, CY, 0), axis='z', speed=0.04)       # (moves with the dial)
    M.nocol.add(ring(CX, CY, DZ - 0.75, DZ - 0.3, DR - 0.9, DR - 0.5, 64, top='brass', bottom='brass', inner='brass', outer='brass'))
    for k in range(72):
        a = 2 * math.pi * (k + 0.5) / 72
        M.nocol.add(obox(CX + math.cos(a) * (DR - 1.15), CY + math.sin(a) * (DR - 1.15), CX + math.cos(a) * (DR - 0.88), CY + math.sin(a) * (DR - 0.88), DZ - 0.72, DZ - 0.33, 0.14, 'brass'))
    for k in range(8):
        a = 2 * math.pi * k / 8
        M.nocol.add(beam((CX + math.cos(a) * 0.5, CY + math.sin(a) * 0.5, DZ - 0.55), (CX + math.cos(a) * (DR - 0.9), CY + math.sin(a) * (DR - 0.9), DZ - 0.55), 0.18, 'iron', 0.45))
    M.parts.add(cyl(CX, CY, EZ, DZ - 0.3, 0.5, 16, side='iron', top='iron', bottom='iron'))
    M.nocol.add(cyl(CX, CY, EZ + 0.4, EZ + 0.7, 0.9, 20, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(CX, CY, EZ, EZ + 0.4, 1.2, 20, side='slate', top='slate'))
    # pinions on their own shafts, meshed with the ring (turning faster the other way)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        px, py = CX + math.cos(a) * (DR - 1.9), CY + math.sin(a) * (DR - 1.9)
        P = R.mover('spin', pivot=(px, py, 0), axis='z', speed=round(0.04 * (DR - 1.0) / 0.75, 4))
        pg = Geo()
        pg.add(ring(px, py, DZ - 0.7, DZ - 0.35, 0.15, 0.62, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
        for j in range(10):
            b = 2 * math.pi * j / 10
            pg.add(obox(px + math.cos(b) * 0.58, py + math.sin(b) * 0.58, px + math.cos(b) * 0.8, py + math.sin(b) * 0.8, DZ - 0.7, DZ - 0.35, 0.12, 'brass'))
        pg.add(cyl(px, py, EZ + 0.6, DZ - 0.35, 0.12, 10, side='iron', caps=False))
        P.nocol.add(pg)
        R.parts.add(cyl(px, py, EZ, EZ + 0.6, 0.35, 12, side='iron', top='iron'))
        R.parts.add(box(px - 0.5, py - 0.5, EZ, px + 0.5, py + 0.5, EZ + 0.15, 'slate'))
    # a flywheel on the chamber floor, with a belt up to the nearest pinion
    fx_, fy_ = CX - 3.4, CY + 2.2
    F = R.mover('spin', pivot=(fx_, fy_, EZ + 1.3), axis='y', speed=0.6)
    F.nocol.add(wheel(fx_, fy_, EZ + 1.3, 1.1, axis='y', spokes=6, rim=0.14, w=0.18, m='iron', hub='brass', segs=24))
    for s in (-1, 1):
        R.parts.add(box(fx_ - 0.1 + s * 0.0, fy_ + s * 0.3 - 0.06, EZ, fx_ + 0.1, fy_ + s * 0.3 + 0.06, EZ + 1.35, 'iron'))
    R.parts.add(box(fx_ - 1.4, fy_ - 0.5, EZ, fx_ + 1.4, fy_ + 0.5, EZ + 0.18, 'slate'))
    R.col.add(box(fx_ - 1.5, fy_ - 0.6, EZ, fx_ + 1.5, fy_ + 0.6, EZ + 2.5, 'tile'))
    # the engineer's corner: a desk, a lamp, a chair, a log
    dx, dy = CX + 3.0, CY + 4.2
    R.parts.add(table_geo(dx - 0.7, dy - 0.4, dx + 0.7, dy + 0.4, 0.76, 'walnut', top='leather').xform(0, 0, 0, EZ))
    R.parts.add(chair_geo(dx, dy - 0.8, math.pi / 2).xform(0, 0, 0, EZ))
    desk_lamp(R, dx - 0.4, dy + 0.1, EZ + 0.76)
    open_book(R, dx + 0.1, dy - 0.05, EZ + 0.76, math.pi / 2)
    R.spot('plaque', dx, dy, EZ, -math.pi / 2,
           text='The engineer\'s log, last page: Wound it. It does not need winding. Wound it anyway. It is something to do down here.')
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.2
        R.light(sphere(CX + math.cos(a) * (DR - 0.5), CY + math.sin(a) * (DR - 0.5), EZ + 2.2, 0.08, 8, 4, 'e_amber'))


def way_down(R, rs):
    """In the north aisle, a tall clock case against a closet whose south face is a false bookcase; behind
    it a stair goes down and a low passage runs south under the floor into the engine room."""
    cx0, cx1, cy0, cy1 = 10.0, 15.2, 28.2, 30.5
    # the closet (walls standing in the aisle, under the gallery)
    for bx in ((cx0 - 0.25, cy0 - 0.25, cx0, cy1 + 0.25), (cx1, cy0 - 0.25, cx1 + 0.25, cy1 + 0.25), (cx0, cy1, cx1, cy1 + 0.25),
               (11.6, cy0 - 0.25, cx1, cy0)):
        R.parts.add(box(bx[0], bx[1], 0, bx[2], bx[3], 3.2, 'walnut', top='walnut', skip=('-z',)))
    R.parts.add(box(cx0 - 0.25, cy0 - 0.25, 3.2, cx1 + 0.25, cy1 + 0.25, 3.35, 'walnut'))
    R.parts.add(box(cx0, cy0 - 0.25, 2.3, 11.6, cy0, 3.2, 'walnut'))
    R.shelf(11.6, cy0 - 0.25, 0, 1.55, '-y', rows=5, frame='walnut', solid=False)
    sh(R, '-y', cy0 - 0.25, 11.7, cx1, rows=7, frame='walnut')
    # the clock case beside it, taller than the closet
    ck = Geo()
    ck.add(box(15.5, 29.0, 0, 16.7, 30.1, 4.4, 'walnut'))
    ck.add(box(15.4, 28.9, 4.4, 16.8, 30.2, 4.6, 'walnut'))
    R.parts.add(ck)
    dialg = cyl(0, 0, -0.03, 0.03, 0.5, 24, side='brass', top='ivory', bottom='ivory'); rot(dialg, 'x', math.pi / 2); dialg.xform(0, 16.1, 28.98, 3.7)
    R.nocol.add(dialg)
    R.nocol.add(box(15.75, 28.95, 0.5, 16.45, 29.0, 2.8, 'gilt'))
    # the stairwell: top landing x 10.0..11.6 (y 28.2..29.35), flight 1 down east, landing, flight 2 down west
    R.cut(box(cx0, cy0, EZ, cx1, cy1, 0.02, 'tile', bottom='floor', top='plaster'))
    R.parts.add(box(cx0, cy0, -0.3, 11.6, 29.35, 0.0, 'floor', sides='tile'))
    n, rise, run = 10, -EZ / 10, 0.28
    R.flight(11.6 + n * run, cy0, EZ, 1.15, n, rise, run, '-x', m='oak', riser='walnut', side='tile')
    # rails: the top landing's north edge, the flight's north side
    brass_rail(R, cx0, 29.4, 11.6, 29.4, 0.0, h=1.0)
    stair_rail(R, 11.6, 29.38, 0.0, 11.6 + n * run, 29.38, EZ + rise)
    # the passage south from the foot of the stair, under the aisle floor, into the engine room
    R.cut(box(14.3, 22.6, EZ, 15.5, cy0 + 0.02, -0.1, 'tile', bottom='floor', top='plaster'))
    R.light(sphere(14.9, 25.5, -0.35, 0.06, 8, 4, 'e_amber'))
    R.light(sphere(12.5, 29.9, 0.6, 0.06, 8, 4, 'e_amber'))


def lamps(R):
    """Pendants from the galleries, lamp standards round the dial, a rose window in the vault."""
    for x in (4.0, 10.0, 22.0, 28.0):
        for y in (GW + 0.8, D - GW - 0.8):
            if y < 16 and 9 < x < 24: continue
            pendant(R, x, y, 5.6, LH - 0.4, r=0.24)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        lamp_post(R, CX + (DR + 2.2) * math.cos(a), CY + (DR + 2.2) * math.sin(a), 0.0, h=2.8)
    for (x, y) in ((2.5, 2.5), (29.5, 2.5), (2.5, 29.5), (29.5, 29.5)):
        R.light(sphere(x, y, 2.6, 0.08, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, y, 2.66, LH - 0.4, 0.01, 4, side='iron', caps=False))
    # the rose in the ceiling
    R.cut(cyl(CX, CY, H - 0.4, H - 0.03, 3.2, 32, side='plaster', top='plaster', bottom='plaster'))
    R.light(cyl(CX, CY, H - 0.07, H - 0.05, 3.2, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    for k in range(12):
        a = 2 * math.pi * k / 12
        R.nocol.add(obox(CX, CY, CX + math.cos(a) * 3.2, CY + math.sin(a) * 3.2, H - 0.3, H, 0.12, 'iron'))
    R.nocol.add(ring(CX, CY, H - 0.3, H, 1.4, 1.55, 32, top='iron', bottom='iron', inner='iron', outer='iron'))
    for y in (8.0, 24.0):
        for x in (8.0, 24.0):
            R.nocol.add(cyl(x, y, 12.0, H, 0.012, 4, side='brass', caps=False))
            R.light(sphere(x, y, 11.9, 0.22, 10, 5, 'e_lamp'))
