"""The Ruin Wing: six rooms in a row, each a thousand years older than the one before. Polished, worn,
dusty, cracked, fallen in, and in the last a tree has come up through the floor. Under its rubble a
stair goes down."""
from kit_h5 import *

W, D = 2 * C, C
H = TOP - 0.1
BAYS = [(T, 5.6), (5.6, 11.0), (11.0, 16.2), (16.2, 21.4), (21.4, 26.8), (26.8, W - T)]
PW = 0.3                       # half a partition wall
AW, AJ = 3.6, 3.4              # the arches between the rooms
# the crypt stair, in the last room: from the floor down to the crypt, descending south
SX0, SX1 = PW + 26.8 + 0.3, 28.75
SY1, NS, SR, SU = 6.0, 17, 0.2, 0.28
SY0 = SY1 - NS * SU
CZ = -NS * SR                  # the crypt floor
CY0, CY1 = 0.6, 4.8
CX0, CX1 = 20.8, 31.2


def make():
    R = Room('ruinwing', 2, 1, res=2048, lo=-4.0)
    rng = random.Random(42)
    R.sockets(floor='floor', wall='tile')
    mats = [('terrazzo', 'tile', 'plaster'), ('floor', 'tile', 'plaster'), ('floor', 'plaster', 'plaster'),
            ('slate', 'plaster', 'plaster'), ('slate', 'tile', 'slate'), ('damask', 'tile', 'slate')]
    for k, (x0, x1) in enumerate(BAYS):
        f, w, c = mats[k]
        R.cut(box(x0 + (PW if k else -0.02), T - 0.02, 0, x1 - (PW if k < 5 else -0.02), D - T + 0.02, H, w, bottom=f, top=c))
    # arches between the rooms, wider as the walls give up
    for k in range(1, 6):
        x = BAYS[k][0]
        w = AW + (0.0, 0.0, 0.3, 0.8, 2.0)[k - 1]
        pr = arch_profile(8.0, w, 0, AJ + (0, 0, 0, 0.3, 0.9)[k - 1], 16)
        R.cut(prism(pr, 'x', x - PW - 0.05, x + PW + 0.05, arch_mats(len(pr), mats[k][0], 'tile'), cap='tile'))
    bay1(R, rng); bay2(R, rng); bay3(R, rng); bay4(R, rng); bay5(R, rng); bay6(R, rng)
    crypt(R, rng)
    navloop(R, [(2.2, 8), (8, 8), (13.6, 8), (18.8, 8), (24, 8), (29.8, 8)], close=False)
    a = R.navpt(8, 2.2); b = R.navpt(8, 13.8); c = R.navpt(24, 2.6); d = R.navpt(24, 13.4)
    R.link(a, 1, b); R.link(c, 4, d)
    R.spot('probe', 13.6, 8, 2.2)
    R.meta.update(label='The Ruin Wing', weight=3,
                  blurb='Each doorway takes you a thousand years further on. Nobody has come to fix anything. The books have not been returned.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    fx(R, 'dust', [16.2, 0, T, W - T, H, D - T])
    return tidy(R)


def walls_of_books(R, x0, x1, rows, skip_door=None, frame='walnut', gaps=0.0, rng=None):
    """Bookcases along both long walls of a room, broken for a door if there is one."""
    ids = []
    runs = [(x0 + 0.3, x1 - 0.3)]
    if skip_door:
        runs = [(x0 + 0.3, skip_door - 2.0), (skip_door + 2.0, x1 - 0.3)]
    for (a, b) in runs:
        if b - a < 0.8: continue
        for (f, bk) in (('+y', T), ('-y', D - T)):
            ids += sh(R, f, bk, a, b, rows=rows, frame=frame)
    return ids


def crack(R, x0, x1, y, zc, rng, facing, w=0.04, steps=10):
    """A zigzag crack drawn on a wall at y (facing +-y) from x0 to x1 around height zc."""
    a = math.pi / 2 if facing == '+y' else -math.pi / 2
    x, z = x0, zc
    for k in range(steps):
        nx = x0 + (x1 - x0) * (k + 1) / steps
        nz = zc + rng.uniform(-0.6, 0.6)
        L = math.hypot(nx - x, nz - z)
        ang = math.atan2(nz - z, nx - x) if facing == '-y' else math.atan2(nz - z, -(nx - x))
        cx_ = x
        g = quad_v(cx_, y, z, a, L, w * rng.uniform(0.6, 1.6), ang, 'black', off=0.01)
        R.nocol.add(g)
        x, z = nx, nz


def bay1(R, rng):
    """New: a polished room, every book in place, the lamps lit."""
    x0, x1 = BAYS[0]
    walls_of_books(R, x0, x1 - PW, 14)
    for s in (-1, 1):   # books either side of the next arch, on the partition
        sh(R, '-x', x1 - PW, 8 + s * 2.0 + (0 if s > 0 else -3.8), 8 + s * 2.0 + (3.8 if s > 0 else 0), rows=14, frame='walnut')
    R.parts.add(table(2.2, 4.3, 3.8, 5.2, 0.78, 'walnut', top='leather'))
    desk_lamp(R, 3.0, 4.75, 0.78)
    R.parts.add(chair(3.0, 3.7, math.pi / 2)); R.spot('sit', 3.0, 3.7, 0.48, math.pi / 2)
    R.parts.add(table(2.2, 10.8, 3.8, 11.7, 0.78, 'walnut', top='leather'))
    desk_lamp(R, 3.0, 11.25, 0.78)
    R.parts.add(chair(3.0, 12.3, -math.pi / 2)); R.spot('sit', 3.0, 12.3, 0.48, -math.pi / 2)
    bust(R, 4.6, 13.2)
    R.light(cyl(3.0, 8.0, H - 0.08, H - 0.04, 0.9, 24, side='e_panel', top='e_panel', bottom='e_panel'))
    R.nocol.add(ring(3.0, 8.0, H - 0.1, H, 0.9, 1.05, 24, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    candle(R, 3.5, 4.55, 0.78, h=0.12)


def bust(R, x, y, broken=0):
    R.parts.add(box(x - 0.22, y - 0.22, 0, x + 0.22, y + 0.22, 1.2, 'tile', skip=('-z',)))
    if broken < 2:
        R.nocol.add(blob(x, y, 1.42, 0.25, 0.2, 0.24, 10, 5, 'ivory'))
    if broken < 1:
        R.nocol.add(blob(x, y, 1.72, 0.13, 0.15, 0.19, 10, 5, 'ivory'))


def bay2(R, rng):
    """Worn: the parquet scuffed, a few gaps on the shelves, the lamps dimmer."""
    x0, x1 = BAYS[1]
    for (a, b) in ((1.0, 6.0), (10.0, 15.0)):
        sh(R, '+x', x0 + PW, a, b, rows=13, frame='walnut')
    for s in (-1, 1):
        sh(R, '-x', x1 - PW, 8 + (2.0 if s > 0 else -5.8), 8 + (5.8 if s > 0 else -2.0), rows=12, frame='walnut')
    R.nocol.add(box(7.0, 4.0, 0, 10.0, 12.0, 0.01, 'carpet'))
    for k in range(7):
        b = book_geo(0.2, 0.05, 0.27, rng.choice(('oxblood', 'green', 'leather')))
        orient(b, rng.uniform(0, 6), 0, 0, rng.uniform(6.5, 10.2), rng.choice((rng.uniform(1.0, 3.0), rng.uniform(13.2, 15.0))), 0.026)
        R.nocol.add(b)
    for (y, m) in ((4.0, 'e_dim'), (12.0, 'e_lamp')):
        bulb(R, 8.3, y, 4.0, r=0.14, m=m, top=H)
    R.light(sphere(x1 - PW - 0.3, 5.6, 1.4, 0.08, 8, 4, 'e_amber'))
    R.parts.add(box(x1 - PW - 0.35, 5.5, 0, x1 - PW, 5.7, 1.3, 'walnut'))


def bay3(R, rng):
    """Dusty: plaster flaking, a bookcase leaning on its neighbour, books slid off onto the floor."""
    x0, x1 = BAYS[2]
    walls_of_books(R, x0 + PW, x1 - PW, 12, frame='wood')
    # a freestanding case, leaning
    g = Geo(); save = R.nocol; R.nocol = g
    shelf(R, 0, 0, 0, 2.4, '+y', rows=6, frame='wood', solid=False)
    R.nocol = save
    rot(g, 'y', 0.0); rot(g, 'x', -0.22)
    g.xform(0, 12.4, 10.6, 0)
    R.nocol.add(g)
    R.col.add(box(12.3, 10.4, 0, 14.9, 11.4, 2.4))
    for k in range(18):
        b = book_geo(0.19, 0.05, 0.26, rng.choice(('oxblood', 'green', 'leather', 'walnut')))
        orient(b, rng.uniform(0, 6), rng.uniform(-0.3, 0.3), 0, rng.uniform(11.8, 15.4), rng.choice((rng.uniform(0.8, 2.6), rng.uniform(11.5, 13.2), rng.uniform(13.4, 15.2))), 0.03 + 0.05 * (k % 3))
        R.nocol.add(b)
    # dust drifts in the corners, flakes of ceiling
    for (x, y) in ((x0 + 0.6, 1.0), (x1 - 0.6, 1.0), (x0 + 0.6, 15.0), (x1 - 0.6, 15.0)):
        R.nocol.add(blob(x, y, 0, 0.9, 0.6, 0.12, 8, 2, 'plaster', lower=False))
    for k in range(10):
        s = rng.uniform(0.2, 0.5)
        g = box(-s, -s * 0.7, 0, s, s * 0.7, 0.02, 'plaster')
        orient(g, rng.uniform(0, 6), rng.uniform(-0.1, 0.1), 0, rng.uniform(x0 + 0.8, x1 - 0.8), rng.uniform(3, 13), 0.0)
        R.nocol.add(g)
    for k in range(6):
        s = rng.uniform(0.3, 0.8)
        R.nocol.add(box(0, 0, H - 0.03, s, s * 0.7, H - 0.005, 'tile').xform(rng.uniform(0, 6), rng.uniform(x0 + 1, x1 - 1), rng.uniform(2, 14), 0))
    bust(R, x1 - PW - 0.5, 13.4, broken=1)
    bulb(R, 13.6, 8.0, 4.6, r=0.12, m='e_dim', top=H)
    bulb(R, 13.6, 3.0, 4.2, r=0.1, m='e_dim', top=H)


def bay4(R, rng):
    """Cracked: the walls split, a slab of floor heaved up, a case fallen flat, light through the ceiling."""
    x0, x1 = BAYS[3]
    walls_of_books(R, x0 + PW, x1 - PW, 10, frame='wood')
    for (y, f) in ((T + 0.36, '+y'), (D - T - 0.36, '-y')):
        crack(R, x0 + 0.5, x1 - 0.5, y, 5.4, rng, f)
    # the heaved slab: a tilted piece of floor you can walk over
    R.parts.add(slope_box(17.2, 20.4, 3.0, 5.4, 0, 0, 0.02, 0.42, 'slate'))
    R.nocol.add(slope_box(17.15, 20.45, 2.95, 5.45, -0.01, -0.01, 0.0, 0.43, 'black'))
    # a case lying on its face across the floor
    R.parts.add(box(16.9, 10.8, 0, 20.3, 11.4, 0.45, 'wood'))
    for k in range(12):
        b = book_geo(0.19, 0.05, 0.26, rng.choice(('oxblood', 'green', 'leather')))
        orient(b, rng.uniform(0, 6), rng.uniform(-0.4, 0.4), rng.uniform(-0.3, 0.3), rng.uniform(16.8, 20.8), rng.uniform(9.6, 12.4), 0.04)
        R.nocol.add(b)
    # the ceiling split: a crack of sky
    pts = [(17.0, 6.5), (18.2, 7.1), (19.1, 7.0), (20.6, 8.2), (20.8, 8.6), (19.2, 7.6), (18.1, 7.6), (16.9, 7.0)]
    R.light(poly_prism(pts, H - 0.03, H - 0.01, side='e_sky', top='e_sky', bottom='e_sky'))
    rubble(R, 18.8, 7.4, 0.9, 0.0, rng, n=10, solid=False)
    bust(R, x0 + PW + 0.5, 13.4, broken=2)
    bulb(R, 18.8, 3.0, 4.2, r=0.1, m='e_dim', top=H)


def bay5(R, rng):
    """Fallen in: half the ceiling is on the floor and the sky is where it was."""
    x0, x1 = BAYS[4]
    # a few broken shelves left on the walls
    sh(R, '+x', x0 + PW, 1.0, 5.6, rows=5, frame='wood')
    sh(R, '+x', x0 + PW, 10.4, 12.6, rows=7, frame='wood')
    for (y, f) in ((T + 0.36, '+y'), (D - T - 0.36, '-y')):
        crack(R, x0 + 0.5, x1 - 0.5, y, 4.4, rng, f, w=0.07)
    # the sky
    R.light(box(x0 + PW, 3.2, H - 0.02, x1 - PW, 13.4, H, 'e_skydome'))
    for k in range(6):
        y = 2.2 + k * 2.3
        L = rng.uniform(0.6, 2.2)
        R.nocol.add(box(x0 + PW, y - 0.1, H - 0.4, x0 + PW + L, y + 0.1, H - 0.1, 'walnut'))
        L2 = rng.uniform(0.4, 1.8)
        R.nocol.add(box(x1 - PW - L2, y - 0.1, H - 0.4, x1 - PW, y + 0.1, H - 0.1, 'walnut'))
    # heaps of what came down (low enough to walk over), and a broken column
    rubble(R, 22.6, 5.2, 1.3, 0.8, rng, n=16)
    rubble(R, 25.6, 11.2, 1.4, 1.0, rng, n=18)
    rubble(R, 23.0, 11.6, 0.9, 0.5, rng, n=9)
    R.parts.add(cyl(25.8, 4.6, 0, 2.3, 0.35, 12, side='tile', top='tile'))
    col = cyl(0, 0, 0, 2.6, 0.33, 12, side='tile', top='tile')
    rot(col, 'y', 1.45); col.xform(0.4, 22.6, 12.9, 0.35)
    R.nocol.add(col)
    for k in range(10):
        vine(R, rng.uniform(x0 + 0.6, x1 - 0.6), rng.choice((T + 0.4, D - T - 0.4)), rng.uniform(2, 5), H - 0.1, rng)


def bay6(R, rng):
    """The last room: the roof is gone, grass on the floor, and a tree has grown up through it all."""
    x0, x1 = BAYS[5]
    R.light(box(x0 + PW, T, H - 0.02, x1, D - T, H, 'e_skydome'))
    # the tree
    tx, ty = 29.6, 12.2
    R.parts.add(cone(tx, ty, 0, 6.0, 1.15, 0.7, 16, 'walnut'))
    for k in range(9):   # roots
        a = 2 * math.pi * k / 9 + 0.3
        L = rng.uniform(1.6, 2.8)
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L
        ex = min(max(ex, x0 + PW + 0.3), x1 - 0.2); ey = min(max(ey, T + 0.2), D - T - 0.2)
        R.nocol.add(beam((tx + math.cos(a) * 0.8, ty + math.sin(a) * 0.8, 0.5), (ex, ey, -0.02), 0.32, 'walnut', 0.24))
    # boughs spreading under the open sky, over this room and the last one
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.5
        reach = rng.uniform(2.4, 4.2) if math.cos(a) > 0.3 else rng.uniform(3.0, 6.5)
        p0 = (tx, ty, rng.uniform(3.8, 5.4))
        p1 = (tx + math.cos(a) * reach, ty + math.sin(a) * reach * 0.8, 6.2 + rng.uniform(-0.3, 0.8))
        p1 = (min(max(p1[0], 22.0), x1 - 0.2), min(max(p1[1], T + 0.3), D - T - 0.3), min(p1[2], 7.1))
        R.nocol.add(beam(p0, p1, 0.36, 'walnut', 0.3))
        leaves(R, p1[0], p1[1], min(6.9, p1[2]), 1.7, 8, rng)
    leaves(R, tx, ty, 6.6, 2.2, 12, rng)
    for k in range(6):
        vine(R, tx + rng.uniform(-2.5, 1.5), ty + rng.uniform(-2.5, 2.5), rng.uniform(2.6, 4.0), 6.4, rng)
    # grass tufts and ferns, a rotten case against the north wall, vines everywhere
    for k in range(40):
        x, y = rng.uniform(x0 + PW + 0.3, x1 - 0.3), rng.uniform(T + 0.3, D - T - 0.3)
        leaves(R, x, y, 0.05, rng.uniform(0.15, 0.35), 1, rng, flat=0.5)
    g = Geo(); save = R.nocol; R.nocol = g
    shelf(R, 30.9, D - T, 0, 2.6, '-y', rows=6, frame='wood', solid=False)
    R.nocol = save
    rot(g, 'x', 0.12, 0, D - T, 0)
    R.nocol.add(g)
    R.col.add(box(28.2, D - T - 0.5, 0, 31.0, D - T, 2.7))
    for k in range(14):
        vine(R, rng.uniform(x0 + 0.6, x1 - 0.6), rng.choice((T + 0.4, D - T - 0.4)), rng.uniform(1, 4), H - 0.1, rng)
    # the rubble over the stair: a ridge along its east side, a pile at its foot, and a fallen slab
    # of ceiling leaning over its head so you have to stoop to find it
    R.parts.add(box(SX1, SY0 - 0.9, 0, SX1 + 0.9, SY1 + 0.2, 1.15, 'tile', top='slate'))
    R.parts.add(box(SX0 - 0.3, T, 0, SX1 + 0.9, SY0 + 0.1, 1.15, 'tile', top='slate'))
    rubble(R, SX1 + 0.45, SY0 + 2.0, 1.2, 1.3, rng, n=14, solid=False)
    rubble(R, (SX0 + SX1) / 2, SY0 - 0.4, 1.0, 1.4, rng, n=10, solid=False)
    slab = box(-1.2, -0.9, -0.12, 1.2, 0.9, 0.0, 'slate', top='plaster')
    rot(slab, 'x', -0.35)
    slab.xform(0, (SX0 + SX1) / 2 + 0.3, SY1 + 0.7, 1.55)
    R.nocol.add(slab)
    R.col.add(box(SX0 - 0.3, SY1 - 0.1, 1.35, SX1 + 0.9, SY1 + 1.5, 1.9))
    R.nocol.add(box(SX1 + 0.1, SY1 + 1.1, 0, SX1 + 0.4, SY1 + 1.4, 1.4, 'tile'))
    R.parts.add(box(SX1 + 0.05, SY1 - 0.1, 0, SX1 + 0.9, SY1 + 1.6, 1.35, 'tile', top='slate'))
    # the stair itself
    R.cut(box(SX0, SY0 - 0.02, CZ, SX1, SY1, 0.3, 'tile', bottom='slate'))
    stair_down(R)


def stair_down(R):
    """The flight from the floor down to the crypt, descending south: visible steps plus the ramp."""
    # the kit's flight climbs; build it from the bottom (at SY0, crypt floor) climbing north
    R.flight(SX0, SY0, CZ, SX1 - SX0, NS, SR, SU, '+y', m='slate', riser='tile', side='tile')


def crypt(R, rng):
    """Under the last room: a low vault of old books and candles, roots coming through its ceiling."""
    pr = arch_profile((CY0 + CY1) / 2, CY1 - CY0, CZ, 1.8, 16, rise=0.95)
    R.cut(prism(pr, 'x', CX0, CX1, arch_mats(len(pr), 'slate', 'tile'), cap='tile'))
    # niches of books down both sides
    for k in range(6):
        x = CX0 + 0.8 + k * 1.3
        if x + 1.0 > SX0 - 0.1: break
        for (y, f) in ((CY0, '+y'), (CY1, '-y')):
            sh(R, f, y, x, x + 1.0, z=CZ + 0.3, rows=3, frame='walnut', depth=0.28)
    # a sarcophagus of stone with a book on it
    sx, sy = CX0 + 3.8, (CY0 + CY1) / 2
    R.parts.add(box(sx - 1.1, sy - 0.5, CZ, sx + 1.1, sy + 0.5, CZ + 0.85, 'tile', top='slate'))
    R.nocol.add(box(sx - 1.15, sy - 0.55, CZ + 0.85, sx + 1.15, sy + 0.55, CZ + 0.95, 'slate'))
    ob = open_book(0.22, 0.3, 0.2, 'leather'); orient(ob, 0, 0, 0, sx, sy, CZ + 0.97)
    R.nocol.add(ob)
    R.spot('plaque', sx, sy, CZ + 0.97)
    for (dx, dy) in ((-1.4, -0.9), (1.4, -0.9), (-1.4, 0.9), (1.4, 0.9)):
        candle(R, sx + dx, sy + dy, CZ, h=0.3, stand=0.9)
    # roots through the vault
    for k in range(9):
        x = rng.uniform(CX0 + 3, CX1 - 0.5); y = rng.uniform(CY0 + 0.3, CY1 - 0.3)
        R.nocol.add(beam((x, y, CZ + 3.2), (x + rng.uniform(-0.5, 0.5), y + rng.uniform(-0.4, 0.4), CZ + rng.uniform(1.8, 2.5)), 0.08, 'wood'))
    R.light(sphere(CX0 + 0.5, (CY0 + CY1) / 2, CZ + 1.6, 0.08, 8, 4, 'e_amber'))
    bulb(R, sx, sy, CZ + 2.3, r=0.1, m='e_dim', top=CZ + 2.75)
    secret(R, sx, sy, CZ, 'The Crypt',
           'Under the rubble the wing goes on, older still. Whoever was buried here was buried with their library, and the candles are somehow still lit.', r=2.2)
