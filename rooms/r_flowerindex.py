"""The Flower Index: a glasshouse inside the library. Paper flowers grow in the beds, every petal
printed; in the iron pavilion at the centre the card catalogue has taken root. In the corner, a wall
of ivy that is not quite a wall."""
from kit_h5 import *

W = D = 2 * C
H = TOP - 0.1
SX, SY = 26.6, 26.6          # the potting shed fills the north-east corner beyond these
SZ = 3.1
SD0, SD1 = 28.5, 29.7        # its hidden doorway, in its west wall


def make():
    R = Room('flowerindex', 2, 2, res=2048)
    rng = random.Random(39)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    roof(R)
    # bookcases round the walls between the doors (not in the shed's corner)
    rows = 13
    for (a, b) in ((0.7, 5.8), (10.2, 21.8), (26.2, W - 0.7)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.7, 5.8), (10.2, 21.8)):
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    # flower beds in the blocks between the aisles
    for (x0, y0, x1, y1) in ((11.0, 1.6, 21.0, 5.2), (11.0, 26.8, 21.0, 30.4), (1.6, 11.0, 5.2, 21.0), (26.8, 11.0, 30.4, 21.0)):
        bed_of_flowers(R, x0, y0, x1, y1, rng, hmin=0.4, hmax=1.6, lmin=0.2, lmax=0.45, dens=0.3)
        # giants: three in each bed, taller than you
        long_x = x1 - x0 > y1 - y0
        for t in (0.2, 0.5, 0.8):
            fx_ = x0 + (x1 - x0) * t if long_x else (x0 + x1) / 2 + rng.uniform(-0.6, 0.6)
            fy_ = (y0 + y1) / 2 + rng.uniform(-0.6, 0.6) if long_x else y0 + (y1 - y0) * t
            flower(R, fx_, fy_, 0.5, rng.uniform(2.2, 3.8), rng.uniform(0.8, 1.4), rng, text=True, lean=0.2)
    # corner blocks: reading tables under green lamps (south-west, south-east, north-west)
    for (cx, cy) in ((3.4, 3.4), (28.6, 3.4), (3.4, 28.6)):
        R.parts.add(table(cx - 1.4, cy - 0.5, cx + 1.4, cy + 0.5, 0.78, 'walnut', top='leather'))
        for dx in (-0.7, 0.7):
            desk_lamp(R, cx + dx, cy, 0.78)
            for s in (-1, 1):
                R.parts.add(chair(cx + dx, cy + s * 0.85, -s * math.pi / 2))
                R.spot('sit', cx + dx, cy + s * 0.85, 0.48, -s * math.pi / 2)
        for k in range(3):
            ob = book_geo(0.2, 0.05, 0.27, ('green', 'oxblood', 'leather')[k]); orient(ob, rng.uniform(0, 3), 0, 0, cx + rng.uniform(-1.1, 1.1), cy + rng.uniform(-0.3, 0.3), 0.81 + 0.0)
            R.nocol.add(ob)
    # urns of flowers on pedestals at the aisle crossings' corners
    for (x, y) in ((10.4, 10.4), (21.6, 10.4), (10.4, 21.6), (21.6, 21.6), (5.6, 5.6), (26.4, 5.6), (5.6, 26.4)):
        R.parts.add(box(x - 0.35, y - 0.35, 0, x + 0.35, y + 0.35, 0.8, 'tile', skip=('-z',)))
        R.parts.add(cone(x, y, 0.8, 1.35, 0.18, 0.42, 12, 'tile', top='leather'))
        for k in range(5):
            a = 2 * math.pi * k / 5
            flower(R, x + math.cos(a) * 0.2, y + math.sin(a) * 0.2, 1.3, rng.uniform(0.3, 0.8), rng.uniform(0.15, 0.3), rng, lean=0.5)
        leaves(R, x, y, 1.45, 0.4, 3, rng)
    pavilion(R, rng)
    shed(R, rng)
    # ivy up the walls here and there
    for k in range(34):
        side = k % 4
        t = rng.uniform(1.0, 31.0)
        if min(abs(t - 8), abs(t - 24)) < 2.4: continue
        if side == 0: x, y = t, T + 0.4
        elif side == 1: x, y = t, D - T - 0.4
        elif side == 2: x, y = T + 0.4, t
        else: x, y = W - T - 0.4, t
        if x > SX - 0.3 and y > SY - 0.3: continue
        vine(R, x, y, rng.uniform(2.5, 5.0), H - 0.1, rng)
    # night: amber lanterns hung from the roof trusses
    for (x, y) in ((8, 8), (24, 8), (8, 24), (24, 24), (16, 3.4), (3.4, 16), (28.6, 16), (16, 28.6)):
        R.nocol.add(cyl(x, y, 4.5, H - 0.6, 0.008, 4, side='iron', caps=False))
        lantern(R, x, y, 4.25, s=1.4)
    navloop(R, [(8, 2.5), (8, 8), (8, 16), (8, 24), (8, 29.5), (16, 24.3), (24, 24), (24, 16), (24, 8), (24, 2.5), (16, 7.7)])
    a = R.navpt(2.5, 8); b = R.navpt(29.5, 8); c = R.navpt(2.5, 24); d = R.navpt(29.5, 24)
    R.link(a, 1); R.link(8, b); R.link(c, 3); R.link(6, d)
    R.spot('probe', 16, 8.0, 2.2)
    R.meta.update(label='The Flower Index', weight=4,
                  blurb='A glasshouse where the flowers are made of paper and every petal is printed. You could read a whole bed of them, if you knew what order to pick them in.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    fx(R, 'dust', [T, 0, T, W - T, H - 0.5, D - T])
    return tidy(R)


def roof(R):
    """A glass roof on iron trusses: the painted sky behind a grid of iron."""
    R.light(box(T, T, H - 0.02, W - T, D - T, H, 'e_skydome'))
    for k in range(9):
        y = T + 0.2 + k * (D - 2 * T - 0.4) / 8
        R.nocol.add(box(T, y - 0.05, H - 0.14, W - T, y + 0.05, H - 0.02, 'iron'))
    for k in range(17):
        x = T + k * (W - 2 * T) / 16
        R.nocol.add(box(x - 0.03, T, H - 0.1, x + 0.03, D - T, H - 0.02, 'iron'))
    # arched trusses springing from the side walls
    for k in range(1, 8):
        y = k * 4.0
        n = 16
        pts = []
        for j in range(n + 1):
            t = j / n
            x = T + (W - 2 * T) * t
            z = 5.2 + (H - 0.2 - 5.2) * math.sin(math.pi * t) ** 0.6
            pts.append((x, y, z))
        for p, q in zip(pts, pts[1:]):
            R.nocol.add(beam(p, q, 0.09, 'iron', 0.22))
        for j in range(1, n):
            p = pts[j]
            if p[2] < H - 0.25:
                R.nocol.add(box(p[0] - 0.02, y - 0.02, p[2], p[0] + 0.02, y + 0.02, H - 0.1, 'iron', skip=('-z', '+z')))
        for x in (T + 0.12, W - T - 0.12):
            R.nocol.add(box(x - 0.1, y - 0.12, 4.9, x + 0.1, y + 0.12, 5.25, 'iron'))


def pavilion(R, rng):
    """The iron pavilion in the middle: open arches, a stone step, and inside the card catalogue in
    flower."""
    x0, y0, x1, y1 = 12.2, 12.2, 19.8, 19.8
    hz = 4.6
    R.parts.add(box(x0 - 0.5, y0 - 0.5, 0, x1 + 0.5, y1 + 0.5, 0.18, 'tile', top='terrazzo', skip=('-z',)))
    # posts and arches on every side, open between
    for k in range(5):
        t = k / 4
        for (px, py) in ((x0 + (x1 - x0) * t, y0), (x0 + (x1 - x0) * t, y1), (x0, y0 + (y1 - y0) * t), (x1, y0 + (y1 - y0) * t)):
            R.parts.add(box(px - 0.07, py - 0.07, 0.18, px + 0.07, py + 0.07, hz, 'iron'))
    for (ax, a0, a1, c) in (('x', x0, x1, y0), ('x', x0, x1, y1), ('y', y0, y1, x0), ('y', y0, y1, x1)):
        for k in range(4):
            s0 = a0 + (a1 - a0) * k / 4; s1 = s0 + (a1 - a0) / 4
            n = 8
            for j in range(n):
                t0, t1 = math.pi * j / n, math.pi * (j + 1) / n
                u0, u1 = (s0 + s1) / 2 - (s1 - s0) / 2 * math.cos(t0), (s0 + s1) / 2 - (s1 - s0) / 2 * math.cos(t1)
                z0, z1 = 3.2 + 0.7 * math.sin(t0), 3.2 + 0.7 * math.sin(t1)
                p, q = ((u0, c, z0), (u1, c, z1)) if ax == 'x' else ((c, u0, z0), (c, u1, z1))
                R.nocol.add(beam(p, q, 0.05, 'iron', 0.08))
        p, q = ((a0, c, hz), (a1, c, hz)) if ax == 'x' else ((c, a0, hz), (c, a1, hz))
        R.nocol.add(beam(p, q, 0.14, 'iron', 0.14))
    # the pavilion's roof: iron ribs rising to a lantern
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (cx, y0), (cx, y1), (x0, cy), (x1, cy)):
        R.nocol.add(beam((px, py, hz), (cx + (px - cx) * 0.15, cy + (py - cy) * 0.15, 6.6), 0.07, 'iron', 0.1))
    R.nocol.add(cyl(cx, cy, 6.55, 6.75, 0.7, 12, side='iron', top='iron', bottom='iron'))
    R.light(cyl(cx, cy, 6.1, 6.5, 0.3, 10, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # the card catalogue: a long walnut cabinet of drawers, some pulled open with flowers growing out
    kx0, kx1, ky0, ky1 = cx - 1.8, cx + 1.8, cy - 0.45, cy + 0.45
    R.parts.add(box(kx0, ky0, 0.18, kx1, ky1, 1.35, 'walnut'))
    for s in (-1, 1):
        fy = cy + s * 0.45
        for i in range(8):
            for j in range(4):
                x = kx0 + 0.1 + i * 0.44; z = 0.3 + j * 0.26
                op = rng.random() < 0.25
                if op:
                    d = rng.uniform(0.2, 0.45)
                    y_a, y_b = (fy, fy + d) if s > 0 else (fy - d, fy)
                    R.nocol.add(box(x, y_a, z, x + 0.38, y_b, z + 0.22, 'oak', top='leather'))
                    flower(R, x + 0.19, (y_a + y_b) / 2, z + 0.22, rng.uniform(0.2, 0.7), rng.uniform(0.1, 0.22), rng, lean=0.6)
                else:
                    R.nocol.add(box(x, fy - 0.01 if s < 0 else fy, z, x + 0.38, fy + 0.01 if s > 0 else fy, z + 0.22, 'oak'))
                R.nocol.add(box(x + 0.16, fy + s * 0.01 - 0.01, z + 0.08, x + 0.22, fy + s * 0.03, z + 0.12, 'brass'))
    # the tallest flowers, in round beds at the pavilion's corners
    for (px, py) in ((x0 + 1.3, y0 + 1.3), (x1 - 1.3, y0 + 1.3), (x0 + 1.3, y1 - 1.3), (x1 - 1.3, y1 - 1.3)):
        R.parts.add(cyl(px, py, 0.18, 0.62, 0.8, 16, side='tile', top='green'))
        flower(R, px, py, 0.62, rng.uniform(2.6, 3.4), rng.uniform(0.8, 1.1), rng, text=True, lean=0.25)
        for k in range(4):
            a = rng.uniform(0, 6.28)
            flower(R, px + math.cos(a) * 0.5, py + math.sin(a) * 0.5, 0.62, rng.uniform(0.4, 1.0), rng.uniform(0.15, 0.3), rng)
    for x in (cx - 1.4, cx + 1.4):
        R.spot('read', x, cy - 1.0, 0.18, math.pi / 2)
    vine(R, x0, y0 + 0.1, 1.5, hz, rng); vine(R, x1, y1 - 0.1, 2.0, hz, rng); vine(R, x1 - 0.1, y0, 1.2, hz, rng)


def shed(R, rng):
    """The potting shed in the north-east corner: plank walls under a curtain of ivy. The west wall's
    door is hidden in the ivy; you walk through the leaves."""
    x0, y0, x1, y1 = SX, SY, W - T, D - T
    tw = 0.18
    # walls (the west one with its doorway), a plank roof
    R.parts.add(box(x0, y0, 0, x1, y0 + tw, SZ, 'oak'))
    R.parts.add(box(x0, y0 + tw, 0, x0 + tw, SD0, SZ, 'oak'))
    R.parts.add(box(x0, SD1, 0, x0 + tw, y1, SZ, 'oak'))
    R.parts.add(box(x0, SD0, 2.2, x0 + tw, SD1, SZ, 'oak'))
    R.parts.add(box(x0 - 0.15, y0 - 0.15, SZ, x1, y1, SZ + 0.14, 'walnut', bottom='oak'))
    for k in range(9):
        R.nocol.add(box(x0 - 0.15, y0 - 0.15 + k * 0.6, SZ + 0.14, x1, y0 - 0.1 + k * 0.6, SZ + 0.2, 'walnut'))
    # ivy over the outside of both walls, thick over the doorway
    for k in range(28):
        t = k / 27
        vine(R, x0 - 0.06, y0 + 0.1 + (y1 - y0 - 0.2) * t, rng.uniform(0.05, 0.9) if SD0 - 0.2 < y0 + (y1 - y0) * t < SD1 + 0.2 else rng.uniform(0.4, 1.6), SZ, rng, w=0.06)
        vine(R, x0 + 0.1 + (x1 - x0 - 0.2) * t, y0 - 0.06, rng.uniform(0.4, 1.6), SZ, rng, w=0.06)
    for k in range(10):
        leaves(R, x0 - 0.2, y0 + 0.4 + k * 0.5, rng.uniform(2.2, 3.1), 0.5, 2, rng)
        leaves(R, x0 + 0.4 + k * 0.5, y0 - 0.2, rng.uniform(2.2, 3.1), 0.5, 2, rng)
    # inside: the potting bench along the east wall, pots, seedlings, a shelf of seed catalogues
    bx0 = x1 - 0.75
    R.parts.add(table(bx0, y0 + 0.6, x1 - 0.02, y1 - 0.5, 0.9, 'oak'))
    for k in range(6):
        py = y0 + 0.9 + k * 0.6
        R.nocol.add(cone(bx0 + 0.35, py, 0.9, 1.12, 0.1, 0.14, 10, 'oxblood', top='leather'))
        flower(R, bx0 + 0.35, py, 1.1, rng.uniform(0.1, 0.3), rng.uniform(0.05, 0.12), rng, lean=0.4)
    for k in range(4):
        R.nocol.add(cone(x0 + 0.6 + k * 0.5, y1 - 0.3, 0, 0.3, 0.14, 0.2, 10, 'oxblood', top='leather'))
    sh(R, '-y', y1, x0 + 0.4, x1 - 0.9, z=1.3, rows=3, frame='oak', depth=0.28)
    R.parts.add(cyl(x0 + 1.6, y0 + 1.5, 0, 0.55, 0.2, 10, side='oak', top='oak'))
    R.spot('sit', x0 + 1.6, y0 + 1.5, 0.55, 0.0)
    ob = open_book(0.18, 0.26, 0.25, 'green'); orient(ob, 1.57, 0, 0, bx0 + 0.4, y0 + 3.6, 0.92)
    R.nocol.add(ob)
    R.spot('plaque', bx0 + 0.4, y0 + 3.6, 0.92)
    # a watering can
    R.nocol.add(cyl(x0 + 0.5, y0 + 0.6, 0.0, 0.3, 0.13, 10, side='brass', top='brass'))
    R.nocol.add(beam((x0 + 0.6, y0 + 0.6, 0.15), (x0 + 0.85, y0 + 0.6, 0.35), 0.03, 'brass'))
    bulb(R, (x0 + x1) / 2, (y0 + y1) / 2, SZ - 0.5, r=0.1, m='e_lamp', top=SZ, shade='green')
    R.light(sphere(bx0 + 0.3, y1 - 0.8, 1.05, 0.06, 8, 4, 'e_candle'))
    secret(R, (x0 + x1) / 2, (y0 + y1) / 2, 0, 'The Potting Shed',
           'Behind the ivy, somebody keeps the seeds. The catalogue on the bench lists every flower in the glasshouse, and a few that have not come up yet.', r=1.6)
