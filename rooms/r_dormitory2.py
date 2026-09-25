"""The Dormitory: a long vaulted hall of beds, four rows of them, every one made, sheets folded down,
a lamp on every nightstand; moonlight in the high windows. One bed is not made. It has been dragged out
of its row, and where it stood there is an open trapdoor, and a ladder down to a room where one more
bed is made up, very neatly, with a lamp still lit."""
from kit_h10 import *

W, D = 32.0, 16.0
JAMB, RISE = 4.9, 2.6
BW, BL = 0.95, 2.0                  # a bed
WALL_X = [1.9, 4.4, 11.2, 13.6, 16.0, 18.4, 20.8, 27.6, 30.0]
MID_X = [5.2 + 2.4 * k for k in range(10)]
UX = 18.4                           # the unmade bed's slot (north wall row)
HX0, HX1, HY0, HY1 = UX - 0.5, UX + 0.5, 13.45, 15.35     # the trapdoor
KZ = -2.1                                                 # the room underneath
KX0, KX1, KY0, KY1 = 15.4, 21.6, 10.6, 15.6


def make():
    R = Room('dormitory2', 2, 1, res=2048, lo=-4.0)
    R.sockets(floor='floor', wall='tile')
    vault_cut(R, 'x', D / 2, D - 2 * T + 0.04, T - 0.02, W - T + 0.02, 0.0, JAMB, rise=RISE, m='plaster', floor='floor', wall='tile')
    ribs(R, 'x', D / 2, D - 2 * T, [T + (W - 2 * T) * k / 8 for k in range(1, 8)], 0.0, JAMB, rise=RISE, d=0.28, t=0.35)
    walls(R)
    beds(R)
    below(R)
    lamps(R)
    navloop(R, [(1.6, 4.0), (8.0, 4.0), (16.0, 4.0), (24.0, 4.0), (30.4, 4.0), (30.4, 8.0), (30.4, 12.0), (24.0, 12.0),
                (16.0, 12.0), (8.0, 12.0), (1.6, 12.0), (1.6, 8.0)])
    secret(R, (KX0 + KX1) / 2, 12.6, KZ, 'The Bed Under the Bed',
           'Under the unmade bed there was a trapdoor, and under the trapdoor a room with one more bed in it, made so neatly the corners are sharp enough to cut. The lamp is on. The sheets are warm.')
    fx(R, 'dust', [2.0, 1.0, 0.5, 30.0, 4.0, 6.0])
    fx(R, 'dust', [2.0, 12.0, 0.5, 30.0, 15.0, 6.0])
    return done(R, 'The Dormitory', weight=5, probe=(16.0, 4.0, 2.4),
                blurb='Beds, made, as far down the hall as you can see, a lamp on at every one, and nobody in any of them. They are all waiting for somebody to be tired.')


# ---------------------------------------------------------------------------
def walls(R):
    # bookcases along both long walls behind the bed heads, broken at the doorways
    for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, W - 0.6)):
        sh(R, '+y', T, a, b, rows=6, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=6, frame='walnut')
    for (a, b) in ((0.6, 6.1), (9.9, D - 0.6)):
        sh(R, '+x', T, a, b, rows=9, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=9, frame='walnut')
    # high windows on both long walls with moonlight in them
    for x in (4.0, 12.0, 16.0, 20.0, 28.0):
        window(R, 'S', x, 3.1, 1.5, 2.3, depth=0.3, em='e_moon', frame='iron', mull=1, trans=2)
        window(R, 'N', x, 3.1, 1.5, 2.3, depth=0.3, em='e_moon', frame='iron', mull=1, trans=2)
    # the low spine of bookcases down the middle, beds' heads against it
    stack(R, 'x', D / 2, 4.0, 28.0, rows=3, frame='walnut')
    R.parts.add(box(3.9, D / 2 - 0.4, 1.4, 28.1, D / 2 + 0.4, 1.46, 'walnut'))
    # a long runner down each aisle
    for (y0, y1) in ((3.4, 4.6), (11.4, 12.6)):
        R.nocol.add(box(2.4, y0, 0, 29.6, y1, 0.012, 'green', skip=('-z',)))


def bed(g, x, y, face, made=True, rs=None, blanket='green'):
    """A bed centred at (x, y); its head toward angle face+pi (the sleeper's feet point along face)."""
    b = Geo()
    # frame, legs, head and foot boards (walnut); local: head at -x, foot at +x
    b.add(box(-BL / 2, -BW / 2, 0.22, BL / 2, BW / 2, 0.36, 'walnut'))
    for (px, py) in ((-BL / 2 + 0.05, -BW / 2 + 0.05), (BL / 2 - 0.05, -BW / 2 + 0.05), (BL / 2 - 0.05, BW / 2 - 0.05), (-BL / 2 + 0.05, BW / 2 - 0.05)):
        b.add(box(px - 0.035, py - 0.035, 0, px + 0.035, py + 0.035, 0.22, 'walnut', skip=('-z', '+z')))
    b.add(box(-BL / 2 - 0.06, -BW / 2 - 0.02, 0, -BL / 2, BW / 2 + 0.02, 1.15, 'walnut'))
    b.add(box(BL / 2, -BW / 2 - 0.02, 0, BL / 2 + 0.06, BW / 2 + 0.02, 0.75, 'walnut'))
    b.add(box(-BL / 2 - 0.08, -BW / 2 - 0.04, 1.15, -BL / 2 + 0.02, BW / 2 + 0.04, 1.2, 'walnut'))
    b.add(box(-BL / 2 + 0.02, -BW / 2 + 0.02, 0.36, BL / 2 - 0.02, BW / 2 - 0.02, 0.52, 'bed', skip=('-z',)))
    if made:
        b.add(box(-0.35, -BW / 2 - 0.03, 0.4, BL / 2 - 0.0, BW / 2 + 0.03, 0.55, blanket, skip=('-z',)))
        b.add(box(-0.5, -BW / 2 - 0.035, 0.42, -0.35, BW / 2 + 0.035, 0.57, 'bed', skip=('-z',)))
        b.add(box(-BL / 2 + 0.08, -BW / 2 + 0.1, 0.52, -BL / 2 + 0.45, BW / 2 - 0.1, 0.64, 'bed', skip=('-z',)))
    else:
        # rumpled: the sheet thrown back in heaps, the blanket half on the floor, the pillow askew
        for k in range(6):
            b.add(blob(rs.uniform(-0.7, 0.8), rs.uniform(-0.3, 0.3), 0.55, rs.uniform(0.25, 0.4), rs.uniform(0.18, 0.3), rs.uniform(0.06, 0.12), 7, 3, 'bed'))
        b.add(box(0.1, BW / 2 - 0.1, 0.5, 0.95, BW / 2 + 0.05, 0.6, blanket).xform(0.0))
        dr = box(0.0, 0.0, 0.0, 0.8, 0.04, 0.5, blanket)
        rot(dr, 'x', 0.35)
        b.add(dr.xform(0, 0.1, BW / 2 + 0.05, 0.05))
        b.add(box(0.2, BW / 2 + 0.2, 0.0, 1.1, BW / 2 + 0.95, 0.06, blanket))
        pl = box(-0.2, -0.3, 0.0, 0.2, 0.3, 0.13, 'bed')
        b.add(pl.xform(0.6, -BL / 2 + 0.35, -0.1, 0.52))
    g.add(b.xform(face, x, y, 0))


def nightstand(R, g, x, y, lit, rs):
    g.add(box(x - 0.22, y - 0.2, 0, x + 0.22, y + 0.2, 0.62, 'walnut', top='oak', skip=('-z',)))
    g.add(box(x - 0.18, y - 0.205, 0.38, x + 0.18, y - 0.2, 0.52, 'oak'))
    llamp(R, x, y + 0.02, 0.62, rs.uniform(-0.3, 0.3), lit=lit, m='e_amber')
    if rs.random() < 0.4:
        g.add(box(x - 0.1, y - 0.14, 0.62, x + 0.1, y - 0.0, 0.66, rs.choice(BOOKM)))


def beds(R):
    rs = rng(5)
    g = Geo()
    # along the walls: heads at the wall shelves
    for (yh, face) in ((T + 0.36, math.pi / 2), (D - T - 0.36, -math.pi / 2)):
        yc = yh + math.sin(face) * (BL / 2 + 0.08)
        for x in WALL_X:
            if face < 0 and abs(x - UX) < 0.1:
                continue
            bed(g, x, yc, face)
            R.spot('bed', x, yc, 0.52, face)
        for x0, x1 in zip(WALL_X, WALL_X[1:]):
            if x1 - x0 < 3.0:
                nightstand(R, g, (x0 + x1) / 2, yh + math.sin(face) * 0.3, rs.random() < 0.8, rs)
    # the two middle rows, heads against the low spine
    for (yh, face) in ((D / 2 - 0.36, -math.pi / 2), (D / 2 + 0.36, math.pi / 2)):
        yc = yh + math.sin(face) * (BL / 2 + 0.08)
        for x in MID_X:
            bed(g, x, yc, face)
            R.spot('bed', x, yc, 0.52, face)
        for x0, x1 in zip(MID_X, MID_X[1:]):
            nightstand(R, g, (x0 + x1) / 2, yh + math.sin(face) * 0.3, rs.random() < 0.7, rs)
    # the unmade one: dragged out of its row, turned, scuff marks where its feet went
    bed(g, 16.3, 11.95, -math.pi / 2 - 0.45, made=False, rs=rs)
    R.parts.add(g)
    # invisible blocks over each row of beds and nightstands, so nobody drops into the gaps between them
    for (x0, x1) in ((1.35, 4.95), (10.65, 21.35), (27.05, 30.55)):
        R.col.add(box(x0, T, 0, x1, T + 2.55, 0.62, 'tile'))
    for (x0, x1) in ((1.35, 4.95), (10.65, HX0 - 0.05), (HX1 + 0.05, 21.35), (27.05, 30.55)):
        R.col.add(box(x0, D - T - 2.55, 0, x1, D - T, 0.62, 'tile'))
    R.col.add(box(MID_X[0] - 0.56, D / 2 - 2.55, 0, MID_X[-1] + 0.56, D / 2 + 2.55, 0.62, 'tile'))
    sc = Geo()
    for dx in (-0.42, 0.42):
        sc.add(obox(UX + dx, 13.3, UX + dx - 1.9, 12.3, 0.0, 0.004, 0.06, 'walnut'))
    R.nocol.add(sc)


def below(R):
    """The trapdoor where the bed stood, and the room under it."""
    R.cut(box(HX0, HY0, -0.6, HX1, HY1, 0.05, 'oak', bottom='oak', top='oak'))
    # the frame round the hole and the leaf flung open on the floor
    for (x0, y0, x1, y1) in ((HX0 - 0.08, HY0 - 0.08, HX1 + 0.08, HY0), (HX0 - 0.08, HY1, HX1 + 0.08, HY1 + 0.08),
                             (HX0 - 0.08, HY0, HX0, HY1), (HX1, HY0, HX1 + 0.08, HY1)):
        R.nocol.add(box(x0, y0, 0, x1, y1, 0.02, 'iron'))
    L = HY1 - HY0
    leaf = box(HX0, HY0 - 0.04 - L, 0.0, HX1, HY0 - 0.04, 0.05, 'walnut', top='oak')
    leaf.add(box(HX0 + 0.1, HY0 - 0.34, 0.05, HX1 - 0.1, HY0 - 0.24, 0.07, 'iron'))
    R.parts.add(leaf)
    # the room underneath
    zc = -0.3
    R.cut(box(KX0, KY0, KZ, KX1, KY1, zc, 'plaster', bottom='floor', top='plaster'))
    # a steep stair down from the trap's south edge (it climbs -y from the room below)
    R.flight(HX0 + 0.05, HY0 + 8 * 0.25, KZ, HX1 - HX0 - 0.1, 8, -KZ / 8, 0.25, '-y', m='oak', riser='walnut', side='walnut')
    # one bed, made perfectly, a lamp lit, a chair, a rug, books
    g = Geo()
    bed(g, KX0 + 1.3, KY0 + 1.0, 0.0, blanket='wool')
    R.parts.add(g.xform(0, 0, 0, KZ))
    R.spot('bed', KX0 + 1.3, KY0 + 1.0, KZ + 0.52, 0.0)
    rug(R, KX0 + 0.6, KY0 + 2.0, KX0 + 3.8, KY0 + 3.8, z=KZ, m='carpet', border='gilt')
    R.parts.add(box(KX0 + 0.1, KY0 + 1.7, KZ, KX0 + 0.55, KY0 + 2.15, KZ + 0.62, 'walnut', top='oak'))
    llamp(R, KX0 + 0.32, KY0 + 1.92, KZ + 0.62, 1.0, lit=True, m='e_amber')
    R.parts.add(lchair_legs(KX1 - 1.1, KY0 + 2.6, math.pi).xform(0, 0, 0, KZ))
    R.spot('sit', KX1 - 1.1, KY0 + 2.6, KZ + 0.48, math.pi)
    sh(R, '+y', KY0, KX0 + 3.0, KX1 - 0.2, z=KZ, rows=6, frame='walnut')
    sh(R, '-x', KX1, KY0 + 0.6, KY0 + 3.6, z=KZ, rows=6, frame='walnut')
    R.nocol.add(box(KX0 + 1.1, KY0 + 0.95, KZ + 0.66, KX0 + 1.35, KY0 + 1.12, KZ + 0.68, 'ivory'))
    bulb(R, (KX0 + KX1) / 2, KY0 + 2.5, zc - 0.6, r=0.07, m='e_dim', top=zc)
    a, b = R.navpt(KX0 + 2.0, KY0 + 2.8, KZ), R.navpt(KX1 - 2.0, KY0 + 2.2, KZ)
    R.link(a, b)


def lamps(R):
    # lanterns on long chains down both aisles, dim; they stay on
    for x in (6.0, 12.0, 20.0, 26.0):
        for y in (4.0, 12.0):
            lantern(R, x, y, 3.2, m='e_amber')
            R.nocol.add(cyl(x, y, 3.44, JAMB + 1.5, 0.01, 4, side='iron', caps=False))
    for x in (2.0, 30.0):
        R.light(sphere(x, D / 2, 3.4, 0.14, 8, 4, 'e_dim'))
        R.nocol.add(cyl(x, D / 2, 3.5, JAMB + 2.2, 0.01, 4, side='iron', caps=False))
