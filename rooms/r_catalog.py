"""The Card Catalogue: long rows of card-catalogue cabinets taller than a man, thousands of little
drawers with brass pulls, rolling ladders. Every drawer holds cards for books you will never find."""
from lib import *
from kit_a import *

H = TOP - 0.1
CH = 2.95           # cabinet height
DD = 0.42           # half depth of a double-sided cabinet


def cabinet(R, c, a, b, pulled=()):
    """A double-sided catalogue cabinet on x = c running along y from a to b."""
    R.parts.add(box(c - DD, a, 0.0, c + DD, b, 0.16, 'walnut', skip=('-z',)))          # plinth
    R.parts.add(box(c - DD + 0.03, a, 0.16, c + DD - 0.03, b, CH, 'walnut'))
    R.parts.add(box(c - DD - 0.04, a - 0.04, CH, c + DD + 0.04, b + 0.04, CH + 0.1, 'walnut'))  # cornice
    R.parts.add(box(c - 0.02, a + 0.05, CH + 0.1, c + 0.02, b - 0.05, CH + 0.14, 'brass'))       # ladder rail
    ncol = max(1, int((b - a - 0.06) / 0.6)); cw = (b - a - 0.06) / ncol
    nrow = 8; z0, z1 = 0.24, CH - 0.1; rh = (z1 - z0) / nrow
    for s in (-1, 1):
        xf = c + s * (DD - 0.03)
        sk = ('-x' if s > 0 else '+x', '-z', '+z', '-y', '+y')
        # the drawer grid: raised oak rails and stiles on the walnut carcass
        for j in range(nrow + 1):
            zz = z0 + j * rh
            x0_, x1_ = sorted((xf, xf + s * 0.02))
            R.nocol.add(box(x0_, a + 0.03, zz - 0.012, x1_, b - 0.03, zz + 0.012, 'walnut', skip=sk))
        for i in range(ncol + 1):
            yy = a + 0.03 + i * cw
            x0_, x1_ = sorted((xf, xf + s * 0.02))
            R.nocol.add(box(x0_, yy - 0.012, z0, x1_, yy + 0.012, z1, 'walnut', skip=sk))
        # a drawer front panel per face, and one brass pull (a single quad) per drawer
        x0_, x1_ = sorted((xf, xf + s * 0.008))
        R.nocol.add(box(x0_, a + 0.03, z0, x1_, b - 0.03, z1, 'oak', skip=sk[:1]))
        g = Geo()
        xp = xf + s * 0.028
        for i in range(ncol):
            ym = a + 0.03 + (i + 0.5) * cw
            for j in range(nrow):
                if (s, i, j) in pulled: continue
                zz = z0 + j * rh + rh * 0.38
                for (y0, y1, za, zb, m) in ((ym - 0.05, ym + 0.05, zz, zz + 0.03, 'gilt'),):
                    P = [(xp, y0, za), (xp, y1, za), (xp, y1, zb), (xp, y0, zb)]
                    if s < 0: P = P[::-1]
                    ids = [g.vert(p) for p in P]
                    g.face(ids, m, [(p[1], p[2]) for p in P])
        R.nocol.add(g)
        for (ss, i, j) in pulled:
            if ss != s: continue
            y0 = a + 0.03 + i * cw; zz = z0 + j * rh
            x0_, x1_ = sorted((xf, xf + s * 0.25))
            R.parts.add(box(x0_, y0 + 0.012, zz + 0.012, x1_, y0 + cw - 0.012, zz + rh - 0.012, 'oak'))
            xq = xf + s * 0.25
            R.parts.add(box(min(xq, xq + s * 0.025), y0 + cw / 2 - 0.04, zz + rh * 0.38, max(xq, xq + s * 0.025), y0 + cw / 2 + 0.04, zz + rh * 0.38 + 0.025, 'brass'))


def make():
    R = Room('catalog', 1, 1, res=1024)
    shell(R, wall='damask', floor='terrazzo', ceil='plaster', h=H)
    xs = (2.3, 4.7, 8.0, 11.3, 13.7)
    segs = ((2.8, 6.5), (9.5, 13.2))
    import random
    rnd = random.Random(3)
    for c in xs:
        for (a, b) in segs:
            pulled = set()
            for _ in range(2):
                pulled.add((rnd.choice((-1, 1)), rnd.randrange(0, 9), rnd.randrange(2, 8)))
            cabinet(R, c, a, b, pulled)
            # a reading slide at the end facing the cross aisle
            ye = b if a < 8 else a
            s = 1 if a < 8 else -1
            R.parts.add(box(c - 0.3, min(ye, ye + s * 0.34), 0.98, c + 0.3, max(ye, ye + s * 0.34), 1.02, 'oak'))
    # rolling ladders leaning on the cabinets
    for (c, y, s) in ((4.7, 11.2, -1), (8.0, 5.2, -1), (11.3, 3.9, 1)):
        R.nocol.add(ladder(c + s * DD, y, 0 if s > 0 else math.pi, h=CH + 0.1, lean=0.75))
    # books floor to ceiling round the walls, with more ladders
    rows = 14
    for (a, b) in ((0.6, 6.3), (9.7, C - 0.6)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', C - T, a, b, rows=rows, frame='walnut')
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', C - T, a, b, rows=rows, frame='walnut')
    for (x, y, a) in ((T + 0.36, 3.0, 0), (C - T - 0.36, 12.6, math.pi)):
        R.nocol.add(ladder(x, y, a, h=6.0, lean=1.15))
    # a brass picture rail at the top of the wall cases, for the ladders
    R.nocol.add(box(T + 0.36, T + 0.36, 6.32, C - T - 0.36, T + 0.4, 6.36, 'brass'))
    R.nocol.add(box(T + 0.36, C - T - 0.4, 6.32, C - T - 0.36, C - T - 0.36, 6.36, 'brass'))
    # green-shaded lamps hanging down every aisle
    for x in (1.1, 6.35, 9.65, 14.9):
        for y in (4.6, 11.4):
            bulb(R, x, y, 3.6, r=0.1, m='e_lamp', shade='green')
    for x in (6.35, 9.65):
        bulb(R, x, 8.0, 3.6, r=0.1, m='e_lamp', shade='green')
    for x in (3.5, 12.5):
        bulb(R, x, 8.0, 4.4, r=0.14, m='e_lamp', shade='green')
    # coffered ceiling: a grid of oak beams
    for k in range(1, 8):
        p = T + k * (C - 2 * T) / 8
        R.nocol.add(box(p - 0.1, T, H - 0.3, p + 0.1, C - T, H, 'oak'))
        R.nocol.add(box(T, p - 0.1, H - 0.3, C - T, p + 0.1, H, 'oak'))
    for k in range(8):
        for j in range(8):
            if (k + j) % 3 == 0:
                x = T + (k + 0.5) * (C - 2 * T) / 8; y = T + (j + 0.5) * (C - 2 * T) / 8
                R.light(box(x - 0.35, y - 0.35, H - 0.03, x + 0.35, y + 0.35, H - 0.01, 'e_panel'))
    navloop(R, [(1.1, 1.8), (6.35, 1.8), (9.65, 1.8), (14.9, 1.8), (14.9, 8), (14.9, 14.2), (9.65, 14.2), (6.35, 14.2), (1.1, 14.2), (1.1, 8)])
    m = [R.navpt(x, 8) for x in (3.5, 6.35, 9.65, 12.5)]
    R.link(9, m[0], m[1], m[2], m[3], 4); R.link(1, m[1], 7); R.link(2, m[2], 6)
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Card Catalogue', weight=7,
                  blurb='Every drawer is full of cards, and every card is for a book. None of them is in order. Some of them are about you.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
