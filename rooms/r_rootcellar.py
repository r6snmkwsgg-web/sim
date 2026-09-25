"""The Root Cellar: a stone undercroft, a barrel-vaulted nave between two aisles, and something
enormous growing overhead. Pale roots as thick as a man come through the vault and the walls, wander
over the floor and grip the bookcases; the books have gone with them. A stream runs down the nave.
In the north-east corner, a root has made a tunnel through the wall, and at the end of it, a hollow."""
from lib import *
from kit_h4 import *

W = 32.0
NX0, NX1 = 10.5, 21.5                 # the nave
AW0, AE0 = 9.9, 22.1                  # the aisles' inner walls (piers between)
BX, BY = 26.5, 26.5                   # the north-east block the hollow is dug into
ARC = (4.0, 10.0, 16.0, 22.0, 28.0)   # arcade openings between nave and aisles


def aisle_vault(x0, x1, y0, y1, jamb=2.8, rise=2.6):
    pr = arch_profile((x0 + x1) / 2, x1 - x0, 0, jamb, 24, rise=min(rise, (x1 - x0) / 2))
    return prism(pr, 'y', y0, y1, arch_mats(len(pr), 'tile', 'slate'))


def root(R, pts, r0, r1, col=True, segs=9, m='root'):
    n = len(pts)
    g = tube(pts, [r0 + (r1 - r0) * (i / (n - 1)) ** 0.8 for i in range(n)], segs, m)
    (R.parts if col else R.nocol).add(g)


def make():
    R = Room('rootcellar', 2, 2, res=2048)
    R.sockets(floor='tile', wall='tile')
    rnd = random.Random(31)
    T_ = T - 0.02
    pr = arch_profile(16.0, NX1 - NX0, 0, 3.2, 32, rise=4.2)
    R.cut(prism(pr, 'y', T_, W - T_, arch_mats(len(pr), 'tile', 'slate')))
    R.cut(aisle_vault(T_, AW0, T_, W - T_))
    R.cut(aisle_vault(AE0, W - T_, T_, BY))
    R.cut(aisle_vault(AE0, BX, BY - 0.1, W - T_, jamb=2.8, rise=2.1))
    for y in ARC:
        ap = arch_profile(y, 3.4, 0, 2.2, 16)
        R.cut(prism(ap, 'x', AW0 - 0.05, NX0 + 0.05, arch_mats(len(ap), 'tile', 'slate')))
        R.cut(prism(ap, 'x', NX1 - 0.05, AE0 + 0.05, arch_mats(len(ap), 'tile', 'slate')))
    # stone ribs across the nave vault
    rib = arch_profile(16.0, NX1 - NX0 - 0.02, 0, 3.2, 32, rise=4.2)[2:-1]
    for y in (2.3, 8.3, 14.3, 20.3, 26.3):
        for p0, p1 in zip(rib, rib[1:]):
            R.nocol.add(bar((p0[0] * 0.985 + 16 * 0.015, y, p0[1] - 0.05), (p1[0] * 0.985 + 16 * 0.015, y, p1[1] - 0.05), 0.5, 0.28, 'tile'))

    stream(R, rnd)
    roots(R, rnd)
    books(R, rnd)
    hollow(R, rnd)
    lights(R, rnd)

    navloop(R, [(12.3, 2.2), (14.2, 8.0), (14.2, 16.0), (14.2, 24.0), (12.3, 30.0), (19.7, 30.0), (17.8, 24.0), (17.8, 16.0), (17.8, 8.0), (19.7, 2.2)])
    navloop(R, [(3.0, 2.2), (8.0, 2.2), (8.0, 16.0), (8.0, 29.8), (3.0, 29.8), (3.0, 16.0)])
    navloop(R, [(24.0, 2.2), (29.8, 2.2), (29.8, 16.0), (24.0, 24.5), (24.0, 29.8), (24.0, 16.0)])
    R.spot('probe', 16.0, 12.0, 3.0)
    R.meta.update(label='The Root Cellar', weight=4,
                  blurb='Something is growing above this room, and has been for a very long time. It reads, apparently: it has taken the books with it.')
    R.meta['box'] = [[T, 0, T], [W - T, 7.4, W - T]]
    fx(R, 'dust', [NX0, 1.0, 0.5, NX1, 31.0, 6.5])
    fx(R, 'fog', [T, T, -0.5, W - T, W - T, 0.6], density=0.04)
    secret(R, 29.0, 29.7, 0.0, 'The Hollow',
           'You crawled up the root to where it came from. It is dry in here, and warm, and something has been sleeping on the moss with a book open beside it.', r=1.6)
    return tidy(R)


def stream(R, rnd):
    x0, x1 = 15.35, 16.65
    R.cut(box(x0, 0.6, -0.45, x1, W - 0.6, 0.2, 'slate', bottom='slate'))
    water(R, x0, 0.6, x1, W - 0.6, -0.12, -0.45)
    # it comes out of a grating in the north wall and goes under one in the south
    for y in (T + 0.02, W - T - 0.06):
        for k in range(6):
            x = x0 + 0.1 + k * (x1 - x0 - 0.2) / 5
            R.nocol.add(box(x - 0.025, y, -0.45, x + 0.025, y + 0.04, 0.7, 'iron'))
        R.nocol.add(box(x0 - 0.1, y, 0.7, x1 + 0.1, y + 0.05, 0.8, 'iron'))
    # flagstone bridges where the aisles' arches line up
    for y in (4.0, 10.0, 16.0, 22.0, 28.0):
        R.parts.add(box(x0 - 0.35, y - 0.9, -0.08, x1 + 0.35, y + 0.9, 0.1, 'slate'))
    for k in range(4):
        R.light(box(x0 + 0.02, 5.0 + k * 7.0, -0.35, x0 + 0.04, 5.6 + k * 7.0, -0.25, 'e_pool'))


def roots(R, rnd):
    # the great roots: down through the nave vault, landing by the piers and spreading over the floor
    big = [((14.0, 5.0), (11.3, 3.4), (-1.0, 0.4), 0.62), ((18.4, 11.0), (20.7, 12.8), (1.0, -0.5), 0.72),
           ((13.2, 18.6), (11.3, 20.8), (-0.9, 0.2), 0.6), ((18.2, 25.4), (20.7, 27.6), (1.1, 0.3), 0.66),
           ((15.0, 29.5), (12.0, 31.0), (-0.6, 0.6), 0.45)]
    for (top, foot, bend, r) in big:
        p0 = (top[0], top[1], 8.2)
        p1 = (foot[0], foot[1], 0.35)
        mid = [(p0[0] + (p1[0] - p0[0]) * t + bend[0] * 4 * t * (1 - t) * 1.6 + math.sin(t * 7 + r * 10) * 0.25,
                p0[1] + (p1[1] - p0[1]) * t + bend[1] * 4 * t * (1 - t) * 1.6,
                p0[2] + (p1[2] - p0[2]) * (t ** 1.25)) for t in [k / 9 for k in range(10)]]
        root(R, mid, r * 0.8, r * 1.1)
        # the root flares into feet that grip the floor
        for k in range(4):
            a = rnd.uniform(0, 2 * math.pi)
            L = rnd.uniform(1.8, 3.8)
            pts = [(p1[0] + math.cos(a) * L * t + rnd.uniform(-0.2, 0.2) * t, p1[1] + math.sin(a) * L * t + rnd.uniform(-0.2, 0.2) * t,
                    0.3 * (1 - t) + 0.02) for t in (0, 0.3, 0.6, 1.0)]
            pts = [(min(max(x, 0.7), W - 0.7), min(max(y, 0.7), W - 0.7), z) for (x, y, z) in pts]
            if any(15.0 < x < 17.0 for (x, y, z) in pts[1:]): continue
            root(R, pts, r * 0.55, 0.05, col=True, segs=7)
        # and it keeps branching on its way down
        g = Geo()
        for k in range(3):
            t = rnd.uniform(0.25, 0.7); i = int(t * 9)
            branches(g, mid[i], (rnd.uniform(-1, 1), rnd.uniform(-1, 1), -0.6), 1.4, r * 0.35, 1, rnd, 'root', 6, 2, 0.8, -0.2)
        R.nocol.add(g)
    # a web of roots across the vaults, wall to wall, sagging
    vault = arch_profile(16.0, NX1 - NX0 - 0.5, 0, 3.2, 16, rise=3.95)[2:-1]
    for k in range(16):
        y = 1.0 + k * 1.95 + rnd.uniform(-0.5, 0.5)
        pts = [(p, y + math.sin(i * 1.3 + k) * 0.35, q - 0.1 - 0.5 * math.sin(math.pi * i / (len(vault) - 1)) * rnd.uniform(0.3, 1.0)) for i, (p, q) in enumerate(vault)]
        pts = [(x, yy, z) for (x, yy, z) in pts if z > 2.6]
        root(R, pts, rnd.uniform(0.12, 0.3), rnd.uniform(0.08, 0.2), col=False, segs=6)
    for (x0, x1, ymax) in ((T, AW0, W - T), (AE0, W - T, BY)):
        av = arch_profile((x0 + x1) / 2, x1 - x0 - 0.4, 0, 2.8, 12, rise=2.4)[2:-1]
        for k in range(int(ymax / 2.6)):
            y = 1.3 + k * 2.6 + rnd.uniform(-0.4, 0.4)
            pts = [(p, y + math.sin(i + k) * 0.3, q - 0.08 - 0.35 * math.sin(math.pi * i / (len(av) - 1))) for i, (p, q) in enumerate(av)]
            pts = [(x, yy, z) for (x, yy, z) in pts if z > 2.2]
            root(R, pts, rnd.uniform(0.1, 0.24), 0.08, col=False, segs=6)
    # more of the great roots, coming down in the aisles over the cases
    for (x, y, dx) in ((2.5, 12.5, 1), (7.5, 26.0, 1), (29.5, 6.5, -1), (24.5, 17.5, -1)):
        pts = [(x - dx * 1.2, y, 5.6), (x - dx * 0.4, y + 0.6, 4.0), (x, y + 0.2, 2.2), (x + dx * 0.3, y - 0.5, 0.8), (x + dx * 1.8, y - 0.8, 0.12)]
        root(R, pts, 0.42, 0.14)
        g = Geo()
        branches(g, pts[1], (dx * 0.3, rnd.uniform(-1, 1), -0.4), 1.6, 0.18, 1, rnd, 'root', 6, 2, 0.8, -0.2)
        R.nocol.add(g)
    # a root running the length of the vault's crown
    crown = [(16.0 + math.sin(k * 0.9) * 0.9, T + 0.2 + k * (W - 2 * T - 0.4) / 12, 6.95 - 0.35 * math.sin(k * 0.7) ** 2) for k in range(13)]
    root(R, crown, 0.42, 0.42, col=False, segs=10)
    # tangles on the aisle walls, gripping the bookcases
    for (x, s) in ((T + 0.42, 1), (W - T - 0.42, -1)):
        for y0 in (1.6, 3.6, 5.2, 10.6, 12.8, 14.9, 17.1, 19.4, 21.0, 26.6, 28.4, 30.0):
            if s < 0 and y0 > BY - 1: continue
            pts = []
            y, z = y0, 4.6 + rnd.uniform(-0.6, 0.6)
            pts.append((x - s * 0.6, y, z + 0.5))
            while z > 0.15:
                z -= rnd.uniform(0.5, 0.9); y += rnd.uniform(-0.7, 0.7)
                y = min(max(y, 0.8), W - 0.8)
                pts.append((x + s * rnd.uniform(-0.05, 0.1), y, max(0.12, z)))
            pts.append((x + s * 1.4, y + rnd.uniform(-0.8, 0.8), 0.05))
            root(R, pts, 0.3, 0.1, col=False, segs=7)
            for p in pts[1:-1]:
                if rnd.random() < 0.7:
                    R.nocol.add(book(p[0] + s * 0.18, p[1] + rnd.uniform(-0.3, 0.3), p[2] - 0.12, rnd.uniform(0, 3.1), rnd.choice(BOOKM), 0.17, 0.25, 0.05, rnd.uniform(-1.2, 1.2)))
    # roots across the S and N ends of the aisles and the pier faces, twigs everywhere
    for (x, y, dy) in ((3.0, T + 0.3, 1), (28.0, T + 0.3, 1), (4.0, W - T - 0.3, -1), (NX0 + 0.3, 13.0, 1), (NX1 - 0.3, 19.0, 1), (NX0 + 0.3, 25.0, 1)):
        g = Geo()
        branches(g, (x, y, 6.5 if abs(dy) else 4.0), (rnd.uniform(-0.5, 0.5), dy * 0.4, -1.0), 2.2, 0.28, 2, rnd, 'root', 7, 2, 0.9, -0.3)
        R.nocol.add(g)
    # moss in the damp
    for k in range(40):
        x, y = rnd.uniform(1.0, W - 1.0), rnd.uniform(1.0, W - 1.0)
        if 14.9 < x < 17.1 or (x > BX and y > BY): continue
        R.nocol.add(blob(x, y, 0.0, rnd.uniform(0.3, 1.1), rnd.uniform(0.3, 1.1), 0.035, 'moss', 8, 3, rnd.uniform(0, 3)))


def books(R, rnd):
    # aisle walls: low cases under the vault, between the doors
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        sh(R, '+x', T, a, b, rows=7, frame='walnut')
        if b < BY - 0.4: sh(R, '-x', W - T, a, b, rows=7, frame='walnut')
        elif a < BY: sh(R, '-x', W - T, a, 22.2, rows=7, frame='walnut')
    for (a, b) in ((0.8, 6.2),):
        sh(R, '+y', T, a, b, rows=11, frame='walnut'); sh(R, '-y', W - T, a, b, rows=11, frame='walnut')
    sh(R, '+y', T, 25.8, W - 0.8, rows=11, frame='walnut')
    # the nave faces of the piers
    piers = [(T + 0.2, 2.3), (5.7, 8.3), (11.7, 14.3), (17.7, 20.3), (23.7, 26.3), (29.7, W - T - 0.2)]
    for (a, b) in piers:
        sh(R, '+x', NX0, a + 0.1, b - 0.1, rows=9, frame='walnut')
        sh(R, '-x', NX1, a + 0.1, b - 0.1, rows=9, frame='walnut')
        sh(R, '-x', AW0, a + 0.1, b - 0.1, rows=6, frame='walnut')
        if b < BY or a > BY: sh(R, '+x', AE0, a + 0.1, b - 0.1, rows=6, frame='walnut')
    # the block's faces in the east aisle
    sh(R, '+x', BX, BY + 0.3, W - T - 2.2, rows=6, frame='walnut')
    # reading desks in the aisles, lamps on them
    for (x, y) in ((5.0, 16.0), (26.0, 12.0), (5.0, 3.6)):
        table(R, x - 1.0, y - 0.5, x + 1.0, y + 0.5, top='leather')
        desk_lamp(R, x - 0.5, y, 0.76); chair(R, x + 0.2, y - 0.95, math.pi / 2)
        book_pile(R, x + 0.5, y + 0.1, 0.76, 4, rnd)
    # books fallen and left on the flags
    for k in range(18):
        x, y = rnd.uniform(1.0, W - 1.0), rnd.uniform(1.0, W - 1.0)
        if 14.9 < x < 17.1 or (x > BX and y > BY): continue
        R.nocol.add(book(x, y, 0.0, rnd.uniform(0, 3.1), rnd.choice(BOOKM)))


def hollow(R, rnd):
    # the crawl: under the tangle on the block's south face, up into the hollow
    tx0, tx1 = 28.3, 29.4
    R.cut(box(tx0, BY - 0.05, 0.0, tx1, 28.4, 1.25, 'root', bottom='root', top='root'))
    cx, cy, r = 29.0, 29.65, 1.75
    R.cut(cyl(cx, cy, 0.0, 2.4, r, 20, side='root', bottom='bark', top='root'))
    R.cut(sphere(cx, cy, 2.4, r, 20, 6, 'root', lower=False))
    # roots lining the tunnel and the hollow's walls, meeting overhead
    for k in range(5):
        y = BY + 0.2 + k * 0.4
        root(R, [(tx0 + 0.05, y, 0.0), (tx0 + 0.1, y + 0.1, 0.9), ((tx0 + tx1) / 2, y, 1.22), (tx1 - 0.1, y - 0.1, 0.9), (tx1 - 0.05, y, 0.0)], 0.07, 0.07, col=False, segs=6)
    for k in range(9):
        a = 2 * math.pi * k / 9
        pts = [(cx + (r - 0.05) * math.cos(a + 0.2 * t), cy + (r - 0.05) * math.sin(a + 0.2 * t), 0.0 + 2.4 * t) for t in (0, 0.33, 0.66, 1.0)]
        pts.append((cx + 0.3 * math.cos(a), cy + 0.3 * math.sin(a), 2.4 + r * 0.95))
        root(R, pts, 0.12, 0.05, col=False, segs=6)
    # the root that made it comes down in front of the way in, with a curtain of hair roots
    root(R, [(tx1 + 0.8, BY - 0.2, 5.4), (tx1 + 0.9, BY - 0.9, 3.5), (tx1 + 0.4, BY - 0.8, 1.6), (tx1 + 0.2, BY - 0.5, 0.2), (tx1 - 0.6, BY - 1.1, 0.05)], 0.45, 0.25)
    strands(R, tx0 - 0.5, BY - 0.25, tx1 + 0.1, BY - 0.25, 4.2, 14, 3.3, rnd, m='root', w=0.04)
    # inside: a bed of moss, a lantern, the open book
    R.parts.add(blob(cx + 0.5, cy + 0.5, 0.0, 0.8, 1.1, 0.25, 'moss', 12, 4))
    R.spot('bed', cx + 0.5, cy + 0.5, 0.22, 0.0)
    open_book(R, cx - 0.7, cy - 0.3, 0.0, 0.8)
    book_pile(R, cx - 0.9, cy + 0.8, 0.0, 6, rnd)
    candle(R, cx - 0.2, cy - 0.9, 0.0, h=0.2)
    R.light(sphere(cx, cy, 3.1, 0.07, 8, 4, 'e_dim'))
    R.nocol.add(cyl(cx + 0.9, cy - 0.6, 1.9, 3.3, 0.01, 4, side='iron', caps=False))
    R.light(sphere(cx + 0.9, cy - 0.6, 1.85, 0.1, 8, 4, 'e_lamp'))
    R.spot('plaque', cx - 0.4, cy - 0.6, 0.0, 0.0, text='The tree does not know it is in a library. It thinks the books are a kind of weather.')


def lights(R, rnd):
    def lantern(x, y, z, top, m='e_lamp'):
        R.nocol.add(cyl(x, y, z + 0.35, top, 0.012, 5, side='iron', caps=False))
        R.nocol.add(cyl(x, y, z + 0.28, z + 0.36, 0.2, 8, side='brass', top='brass', bottom='brass'))
        R.nocol.add(cyl(x, y, z - 0.3, z - 0.26, 0.17, 8, side='brass', top='brass', bottom='brass'))
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            R.nocol.add(box(x + 0.16 * math.cos(a) - 0.015, y + 0.16 * math.sin(a) - 0.015, z - 0.28, x + 0.16 * math.cos(a) + 0.015, y + 0.16 * math.sin(a) + 0.015, z + 0.3, 'brass'))
        R.light(cyl(x, y, z - 0.18, z + 0.18, 0.11, 8, side=m, top=m, bottom=m))
    for y in (5.0, 13.0, 19.0, 27.0):
        lantern(16.0, y, 4.3, 7.4)
    for y in (4.0, 12.0, 20.0, 28.0):
        lantern(5.1, y, 3.0, 5.4, 'e_amber' if y in (12.0, 28.0) else 'e_lamp')
    for y in (4.0, 12.0, 20.0):
        lantern(27.3, y, 3.0, 5.4, 'e_amber' if y == 20.0 else 'e_lamp')
    lantern(24.3, 29.0, 3.0, 4.9, 'e_amber')
