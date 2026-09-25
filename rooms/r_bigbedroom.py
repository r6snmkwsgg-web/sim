"""The Nursery: a child's bedroom built for a child the size of a house. The bed is twice your height
at the headboard, the drawers are a cliff, the rocking horse could carry you off; one whole wall is a
bookcase that goes on for ever (the end walls there are mirrors), rolling ladders leaning on it; the
window is full of dusk and a city far away. Under the bed, where the blanket hangs down, there is a
way into the floor, and a den where somebody small has been hiding with a torch."""
from kit_h10 import *

W = D = 32.0
H = 7.5
S = 2.0                                  # the scale of the child's things
BX0, BX1, BY0, BY1 = 14.9, 17.1, 11.2, 15.0          # the bed's footprint
BZ = 1.4                                             # the underside of the bed frame
SN, SR, SRUN = 10, 0.21, 0.3                         # the stair down under it (climbs -y)
SX0, SX1 = 15.45, 16.55
SY_TOP = 12.0                                        # where the stair starts down (z 0)
SY_FOOT = SY_TOP + SN * SRUN                         # its foot (z -2.1)
KZ = -2.1
KX0, KX1, KY0, KY1 = 13.2, 18.8, SY_FOOT - 1.0, 19.2


def make():
    R = Room('bigbedroom', 2, 2, res=2048, lo=-4.0)
    R.sockets(floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'damask', bottom='floor', top='plaster'))
    ceiling(R)
    bookcase(R)
    walls(R)
    bed(R)
    things(R)
    den(R)
    R.meta['mirrors'] = [{'c': [28.9, T + 0.03, 0.0], 'n': [0, 1, 0], 'w': 5.2, 'h': 7.2},
                         {'c': [28.9, D - T - 0.03, 0.0], 'n': [0, -1, 0], 'w': 5.2, 'h': 7.2}]
    navloop(R, [(3.0, 3.0), (16.0, 3.4), (25.0, 3.0), (25.0, 16.0), (25.0, 29.0), (16.0, 28.6), (3.0, 29.0), (3.0, 16.0)])
    a, b = R.navpt(12.0, 9.0), R.navpt(20.0, 9.0); R.link(a, b); R.link(1, a); R.link(b, 1)
    secret(R, 16.0, (KY0 + KY1) / 2, KZ, 'Under the Bed',
           'Under the bed, where the blanket hangs down, there is a way into the floor, and a den: cushions, a torch still on, drawings of monsters pinned up, and a book on how to be brave. Somebody small was here a moment ago, hiding from you.')
    fx(R, 'dust', [11.0, 20.0, 0.5, 21.0, D - 1.0, 7.0])
    return done(R, 'The Nursery', weight=4, probe=(9.0, 22.0, 2.4),
                blurb='A child\'s bedroom, but the child it was built for is enormous: you only come up to the top of the mattress. It is nearly bedtime. It is always nearly bedtime.')


# ---------------------------------------------------------------------------
def ceiling(R):
    g = Geo()
    for k in range(1, 8):
        x = T + (W - 2 * T) * k / 8
        g.add(box(x - 0.2, T, H - 0.5, x + 0.2, D - T, H, 'walnut', skip=('+z',)))
        y = T + (D - 2 * T) * k / 8
        g.add(box(T, y - 0.2, H - 0.4, W - T, y + 0.2, H, 'walnut', skip=('+z',)))
    R.nocol.add(g)
    R.parts.add(box(T, T, H - 0.8, W - T, T + 0.3, H - 0.5, 'walnut'))
    R.parts.add(box(T, D - T - 0.3, H - 0.8, W - T, D - T, H - 0.5, 'walnut'))


def bookcase(R):
    """The east wall: one bookcase, the whole height, the whole length, and on and on in the mirrors."""
    rows = 16
    for (a, b) in ((0.4, 6.1), (9.9, 22.1), (25.9, D - 0.4)):
        sh(R, '-x', W - T, a, b, rows=rows, row_h=0.42, frame='walnut')
    for c in (8.0, 24.0):
        sh(R, '-x', W - T, c - 1.9, c + 1.9, z=3.3, rows=9, frame='walnut')
    # a plinth of drawers along the bottom (a cornice at the top)
    g = Geo()
    g.add(box(W - T - 0.6, T, H - 0.5, W - T, D - T, H - 0.3, 'walnut'))
    R.parts.add(g)
    # rolling ladders on a brass rail
    R.nocol.add(box(W - T - 0.46, T, 6.1, W - T - 0.4, D - T, 6.16, 'brass'))
    for y in (4.0, 13.5, 19.0, 28.5):
        R.nocol.add(ladder(W - T - 0.42, y, math.pi, h=6.1, lean=1.6))
    # green lamps on long arms along the case
    for y in (3.4, 12.0, 20.0, 28.6):
        R.nocol.add(beam((W - T - 0.4, y, 3.0), (W - T - 0.9, y, 3.1), 0.03, 'brass'))
        R.nocol.add(box(W - T - 1.1, y - 0.2, 3.0, W - T - 0.7, y + 0.2, 3.12, 'green'))
        R.light(box(W - T - 1.05, y - 0.16, 2.99, W - T - 0.75, y + 0.16, 3.0, 'e_lamp'))


def walls(R):
    # the far wall: the window full of dusk and a city on the horizon
    cx = 16.0
    window(R, 'N', cx, 0.6, 5.4, 4.2, depth=0.4, em='e_dusk', frame='iron', mull=4, trans=5)
    rs = rng(5)
    g = Geo()
    x = cx - 2.7
    while x < cx + 2.7:
        w = rs.uniform(0.12, 0.4); h = rs.uniform(0.2, 1.1)
        g.add(box(x, D - T + 0.25, 0.6, min(x + w, cx + 2.7), D - T + 0.3, 0.6 + h, 'black', skip=('-z',)))
        x += w
    g.add(box(cx + 0.7, D - T + 0.24, 0.6, cx + 0.84, D - T + 0.3, 2.6, 'black'))
    R.nocol.add(g)
    # curtains either side, velvet, floor to ceiling
    for s_ in (-1, 1):
        x0 = cx + s_ * 2.9
        R.nocol.add(pleats(min(x0, x0 + s_ * 1.3), max(x0, x0 + s_ * 1.3), D - T - 0.25, 0.0, H - 0.8, 6, 0.14, 'velvet', face=-1))
    R.nocol.add(box(cx - 4.5, D - T - 0.3, H - 0.9, cx + 4.5, D - T - 0.22, H - 0.84, 'brass'))
    # books along the other walls, not so high; pictures over them
    for (a, b) in ((0.6, 6.1), (9.9, 22.1)):
        sh(R, '+x', T, a, b, rows=6, frame='walnut')
    sh(R, '+x', T, 25.9, 27.0, rows=6, frame='walnut')
    for (a, b) in ((0.6, 6.1), (9.9, 22.1)):
        sh(R, '+y', T, a, b, rows=6, frame='walnut')
    for (a, b) in ((0.6, 6.1), (9.9, 12.8), (19.2, 22.1)):
        sh(R, '-y', D - T, a, b, rows=6, frame='walnut')
    for (x, y, face, w, h) in ((T, 12.0, 0.0, 2.4, 1.8), (T, 20.0, 0.0, 1.6, 2.2), (12.0, T, math.pi / 2, 2.0, 1.5)):
        picture(R, x, y, 4.6, face, w, h)
    # mirrors' gilt frames at the ends of the bookcase wall
    for (y, s_) in ((T, 1), (D - T, -1)):
        fr = Geo()
        y0, y1 = (y, y + 0.08) if s_ > 0 else (y - 0.08, y)
        fr.add(box(26.1, y0, 0, 26.3, y1, H - 0.3, 'gilt'))
        fr.add(box(26.1, y0, H - 0.3, W - T - 0.6, y1, H - 0.1, 'gilt'))
        R.parts.add(fr)
        R.parts.add(box(26.3, min(y, y + s_ * 0.01), 0, W - T - 0.6, max(y, y + s_ * 0.01), H - 0.3, 'black'))


def picture(R, x, y, z, face, w, h):
    g = Geo()
    g.add(box(0, -w / 2, -h / 2, 0.06, w / 2, h / 2, 'gilt'))
    g.add(box(0.06, -w / 2 + 0.12, -h / 2 + 0.12, 0.07, w / 2 - 0.12, h / 2 - 0.12, rng(int(x + y)).choice(('damask', 'oxblood', 'green', 'wool'))))
    R.nocol.add(g.xform(face, x, y, z))


def bed(R):
    """The child's bed at twice the size: a wooden frame on tall legs, the blue blanket hanging down."""
    g = Geo()
    L = 0.06 * S
    for (px, py) in ((BX0 + 0.08, BY0 + 0.08), (BX1 - 0.08, BY0 + 0.08), (BX1 - 0.08, BY1 - 0.08), (BX0 + 0.08, BY1 - 0.08)):
        g.add(box(px - L, py - L, 0, px + L, py + L, BZ, 'walnut', skip=('-z',)))
    g.add(box(BX0, BY0, BZ, BX1, BY1, BZ + 0.2, 'walnut'))
    g.add(box(BX0 + 0.04, BY0 + 0.04, BZ + 0.2, BX1 - 0.04, BY1 - 0.04, BZ + 0.55, 'bed', skip=('-z',)))
    # headboard (north end) and footboard, with round knobs
    g.add(box(BX0 - 0.06, BY1, 0, BX1 + 0.06, BY1 + 0.12, 3.3, 'walnut'))
    g.add(box(BX0 - 0.06, BY0 - 0.12, 0, BX1 + 0.06, BY0, 2.3, 'walnut'))
    for x in (BX0 - 0.02, BX1 + 0.02):
        g.add(sphere(x, BY1 + 0.06, 3.45, 0.16, 10, 5, 'walnut'))
        g.add(sphere(x, BY0 - 0.06, 2.45, 0.16, 10, 5, 'walnut'))
    # pillow
    g.add(box(BX0 + 0.25, BY1 - 0.9, BZ + 0.55, BX1 - 0.25, BY1 - 0.1, BZ + 0.85, 'bed', skip=('-z',)))
    R.parts.add(g)
    # the blanket: over the top and hanging down both sides (drawn only: you can push through it)
    b = Geo()
    b.add(box(BX0 - 0.1, BY0 + 0.1, BZ + 0.5, BX1 + 0.1, BY1 - 1.0, BZ + 0.62, 'wool'))
    for x0, x1 in ((BX0 - 0.12, BX0 - 0.1), (BX1 + 0.1, BX1 + 0.12)):
        b.add(box(x0, BY0 + 0.1, 0.25, x1, BY1 - 1.0, BZ + 0.62, 'wool'))
    b.add(box(BX0 - 0.1, BY0 + 0.08, 0.35, BX1 + 0.1, BY0 + 0.1, BZ + 0.62, 'wool'))
    R.nocol.add(b)
    R.spot('bed', 16.0, 13.0, BZ + 0.55, -math.pi / 2)
    # the hole under the bed, and the stair down (it climbs -y from the den to the room)
    R.cut(box(SX0, SY_TOP - 0.05, KZ, SX1, BY1 - 0.1, 0.05, 'oak', bottom='floor', top='oak'))
    R.flight(SX0, SY_FOOT, KZ, SX1 - SX0, SN, SR, SRUN, '-y', m='oak', riser='walnut', side='tile')
    R.nocol.add(box(SX0 - 0.08, SY_TOP - 0.13, 0, SX1 + 0.08, SY_TOP - 0.05, 0.02, 'oak'))
    # a slipper, dropped
    R.nocol.add(box(-0.14, -0.06, 0, 0.14, 0.06, 0.08, 'oxblood').xform(0.6, 14.2, 10.4, 0))


def things(R):
    rs = rng(2)
    rug(R, 9.0, 7.0, 23.0, 21.0, m='carpet', border='gilt')
    rug(R, 3.0, 23.0, 12.0, 30.0, m='velvet', border='oxblood')
    # the nightstand with its lamp, at twice the size
    x, y = 18.4, 14.3
    R.parts.add(box(x - 0.45, y - 0.4, 0, x + 0.45, y + 0.4, 1.3, 'walnut', top='oak'))
    R.parts.add(box(x - 0.36, y - 0.41, 0.7, x + 0.36, y - 0.4, 1.05, 'oak'))
    g = Geo()
    g.add(box(-0.16, -0.12, 0, 0.16, 0.12, 0.06, 'brass'))
    g.add(box(-0.025, -0.025, 0.06, 0.025, 0.025, 0.7, 'brass', skip=('-z', '+z')))
    g.add(box(-0.36, -0.14, 0.7, 0.36, 0.14, 0.88, 'green', bottom='ivory'))
    R.parts.add(g.xform(0.2, x, y, 1.3))
    R.light(box(-0.32, -0.1, 0.68, 0.32, 0.1, 0.7, 'e_lamp').xform(0.2, x, y, 1.3))
    R.nocol.add(box(x - 0.3, y - 0.3, 1.3, x + 0.1, y - 0.0, 1.42, 'oxblood'))
    # a chest of drawers like a cliff, a toy boat on it
    x0, y0 = T + 0.05, 27.2
    R.parts.add(box(x0, y0, 0, x0 + 1.3, y0 + 3.6, 3.2, 'walnut', top='oak'))
    for k in range(4):
        z = 0.3 + k * 0.72
        R.nocol.add(box(x0 + 1.3, y0 + 0.15, z, x0 + 1.33, y0 + 3.45, z + 0.6, 'oak'))
        for yy in (y0 + 0.9, y0 + 2.7):
            R.nocol.add(sphere(x0 + 1.38, yy, z + 0.3, 0.06, 6, 3, 'brass'))
    boat(R, x0 + 0.65, y0 + 1.8, 3.2)
    # the rocking horse
    horse(R, 7.0, 10.0, 0.4)
    # alphabet blocks, a spinning top, a ball, a teddy the size of a man
    for (bx, by, bz, a, m) in ((21.5, 18.0, 0.0, 0.2, 'oxblood'), (22.4, 18.3, 0.0, 0.9, 'green'), (21.9, 18.1, 0.8, 0.5, 'wool'), (23.4, 16.6, 0.0, 0.4, 'gilt')):
        cube = box(-0.4, -0.4, 0, 0.4, 0.4, 0.8, 'ivory')
        cube.add(box(-0.3, -0.41, 0.1, 0.3, -0.4, 0.7, m)); cube.add(box(-0.3, 0.4, 0.1, 0.3, 0.41, 0.7, m))
        cube.add(box(-0.41, -0.3, 0.1, -0.4, 0.3, 0.7, m)); cube.add(box(0.4, -0.3, 0.1, 0.41, 0.3, 0.7, m))
        R.parts.add(cube.xform(a, bx, by, bz))
    R.parts.add(cone(11.0, 17.5, 0.0, 0.6, 0.02, 0.5, 12, 'oxblood'))
    R.parts.add(cone(11.0, 17.5, 0.6, 0.9, 0.5, 0.08, 12, 'gilt'))
    R.nocol.add(cyl(11.0, 17.5, 0.9, 1.3, 0.04, 6, side='walnut', top='walnut'))
    R.parts.add(sphere(20.5, 24.5, 0.6, 0.6, 14, 7, 'wool'))
    teddy(R, 6.5, 26.5, -0.6)
    # a globe on a stand, a small (to it) chair
    R.parts.add(cyl(24.0, 26.0, 0, 0.1, 0.5, 12, side='walnut', top='walnut'))
    R.parts.add(cyl(24.0, 26.0, 0.1, 1.5, 0.07, 8, side='walnut', caps=False))
    R.nocol.add(sphere(24.0, 26.0, 2.2, 0.75, 16, 8, 'green'))
    R.nocol.add(ring(24.0, 26.0, 2.15, 2.25, 0.78, 0.84, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    g = lchair(0, 0, 0.0, frame='walnut', seat='velvet', back_h=0.95, s=S)
    R.parts.add(g.xform(-2.4, 12.4, 25.0, 0))
    # a night light by the bed that stays on
    R.light(sphere(13.8, 15.4, 0.3, 0.14, 10, 5, 'e_amber'))
    R.nocol.add(cyl(13.8, 15.4, 0, 0.18, 0.12, 10, side='brass', top='brass'))
    # standard lamps in the corners, very dim
    for (x, y) in ((2.0, 2.0), (2.0, 21.0), (22.0, 2.0)):
        floor_lamp(R, x, y, 2.2, m='e_dim', scale=1.4)


def boat(R, x, y, z):
    g = Geo()
    g.add(box(-0.18, -0.7, 0.0, 0.18, 0.7, 0.3, 'oxblood', top='oak'))
    g.add(box(-0.02, -0.02, 0.3, 0.02, 0.02, 1.6, 'walnut'))
    R.nocol.add(g.xform(0, x, y, z))
    sail = quad([(x, y - 0.05, z + 0.4), (x, y - 0.6, z + 0.4), (x, y - 0.05, z + 1.5)], 'bed')
    sail.add(quad([(x + 0.005, y - 0.05, z + 0.4), (x + 0.005, y - 0.05, z + 1.5), (x + 0.005, y - 0.6, z + 0.4)], 'bed'))
    R.nocol.add(sail)


def horse(R, x, y, a):
    """A rocking horse, twice the size."""
    g = Geo()
    for s_ in (-0.35, 0.35):
        pts = []
        for k in range(13):
            t = -1.0 + 2.0 * k / 12
            pts.append((t * 1.6, s_, 0.35 * t * t))
        for p, q in zip(pts, pts[1:]):
            g.add(beam(p, q, 0.12, 'walnut', 0.12))
    for (px, s_) in ((-0.9, -0.3), (-0.9, 0.3), (0.9, -0.3), (0.9, 0.3)):
        g.add(beam((px, s_ * 1.1, 0.4), (px * 0.7, s_ * 0.5, 1.4), 0.12, 'ivory'))
    g.add(blob(0, 0, 1.6, 0.95, 0.35, 0.35, 10, 5, 'ivory'))
    g.add(beam((0.8, 0, 1.7), (1.25, 0, 2.5), 0.28, 'ivory'))
    g.add(blob(1.45, 0, 2.55, 0.42, 0.2, 0.2, 8, 4, 'ivory'))
    g.add(box(-0.35, -0.37, 1.8, 0.25, 0.37, 1.95, 'oxblood'))
    g.add(beam((0.9, 0, 2.1), (1.25, 0, 2.8), 0.1, 'walnut', 0.18))
    g.add(beam((-0.95, 0, 1.7), (-1.4, 0, 1.0), 0.1, 'walnut', 0.14))
    R.nocol.add(g.xform(a, x, y, 0))
    R.col.add(box(-1.6, -0.45, 0, 1.6, 0.45, 2.0, 'tile').xform(a, x, y, 0))


def teddy(R, x, y, a):
    g = Geo()
    g.add(blob(0, 0, 0.55, 0.6, 0.55, 0.6, 12, 6, 'food'))
    g.add(blob(0, 0, 1.45, 0.42, 0.4, 0.4, 12, 6, 'food'))
    for s_ in (-1, 1):
        g.add(blob(0.05, s_ * 0.32, 1.8, 0.14, 0.1, 0.14, 8, 4, 'food'))
        g.add(blob(0.25, s_ * 0.55, 0.9, 0.18, 0.3, 0.18, 8, 4, 'food'))
        g.add(blob(0.5, s_ * 0.35, 0.18, 0.35, 0.2, 0.18, 8, 4, 'food'))
    g.add(blob(0.36, 0, 1.38, 0.14, 0.14, 0.1, 8, 4, 'leather'))
    R.nocol.add(g.xform(a, x, y, 0))
    R.col.add(box(-0.6, -0.7, 0, 0.8, 0.7, 1.8, 'tile').xform(a, x, y, 0))


def den(R):
    """The den under the floor, below the bed."""
    zc = -0.3
    R.cut(box(KX0, KY0, KZ, KX1, KY1, zc, 'oak', bottom='floor', top='oak'))
    # cushions, a torch still on, drawings pinned up, a book
    rs = rng(9)
    g = Geo()
    for k in range(8):
        g.add(blob(rs.uniform(KX0 + 0.6, KX0 + 2.4), rs.uniform(KY1 - 1.8, KY1 - 0.5), KZ + 0.15, rs.uniform(0.3, 0.45), rs.uniform(0.25, 0.4), 0.15, 8, 3,
                   rs.choice(('velvet', 'wool', 'green', 'oxblood'))))
    R.nocol.add(g)
    R.nocol.add(box(KX1 - 1.3, KY1 - 1.0, KZ, KX1 - 1.0, KY1 - 0.9, KZ + 0.1, 'iron'))
    R.light(box(KX1 - 1.0, KY1 - 0.99, KZ + 0.02, KX1 - 0.98, KY1 - 0.91, KZ + 0.08, 'e_amber'))
    for k in range(7):
        x = KX0 + 0.5 + k * 0.7
        R.nocol.add(box(x, KY1 - 0.02, KZ + 0.7 + (k % 2) * 0.3, x + 0.4, KY1 - 0.01, KZ + 1.2 + (k % 2) * 0.3, rs.choice(('ivory', 'bed', 'plaster'))))
    ob = box(-0.2, -0.14, 0, 0.0, 0.14, 0.03, 'ivory', sides='oxblood'); ob.add(box(0.0, -0.14, 0, 0.2, 0.14, 0.03, 'ivory', sides='oxblood'))
    R.nocol.add(ob.xform(0.4, KX0 + 3.2, KY1 - 1.2, KZ))
    R.spot('read', KX0 + 3.2, KY1 - 1.2, KZ + 0.03, 0.4)
    sh(R, '+x', KX0, KY0 + 0.3, KY1 - 0.2, z=KZ, rows=3, frame='oak', depth=0.26)
    R.light(sphere(KX1 - 0.4, KY0 + 0.4, KZ + 1.4, 0.06, 6, 3, 'e_candle'))
    a, b = R.navpt(16.0, KY0 + 0.9, KZ), R.navpt(KX0 + 3.0, KY1 - 2.2, KZ)
    R.link(a, b)
