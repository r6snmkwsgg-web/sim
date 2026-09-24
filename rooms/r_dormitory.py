"""The Dormitory: three low barrel vaults side by side on squat arcades, a cross vault through the
middle, and narrow iron beds in rows under them, each with its night light and its shelf of books."""
from lib import *
from kit_b import *


def lunette(c, w, z0, y0, y1, m, axis='y', segs=14):
    r = w / 2
    pr = [(c + r * math.cos(math.pi * k / segs), z0 + r * math.sin(math.pi * k / segs)) for k in range(segs + 1)]
    return prism(pr, axis, y0, y1, m, cap=m)


def bed(R, x0, yc, head):
    """A narrow iron bed along x starting at x0 (the head end if head < 0 is at x0)."""
    L, Wb = 1.95, 0.82
    xa, xb = (x0, x0 + L) if head < 0 else (x0 - L, x0)
    R.parts.add(box(xa, yc - Wb / 2, 0.22, xb, yc + Wb / 2, 0.44, 'bed', skip=('-z',)))
    R.nocol.add(box(xa + (0.55 if head < 0 else 0), yc - Wb / 2 - 0.02, 0.3, xb - (0 if head < 0 else 0.55), yc + Wb / 2 + 0.02, 0.47, 'damask', skip=('-z',)))
    px = xa + 0.1 if head < 0 else xb - 0.5
    R.nocol.add(box(px, yc - 0.3, 0.44, px + 0.4, yc + 0.3, 0.55, 'bed', skip=('-z',)))
    for x in (xa, xb):
        hh = 1.05 if (x == xa) == (head < 0) else 0.75
        for s in (-1, 1):
            R.nocol.add(box(x - 0.03, yc + s * Wb / 2 - 0.03, 0, x + 0.03, yc + s * Wb / 2 + 0.03, hh, 'iron', skip=('-z',)))
        R.nocol.add(box(x - 0.02, yc - Wb / 2, hh - 0.06, x + 0.02, yc + Wb / 2, hh - 0.02, 'iron', skip=('-z',)))
        R.nocol.add(box(x - 0.02, yc - Wb / 2, 0.3, x + 0.02, yc + Wb / 2, 0.34, 'iron', skip=('-z',)))
    R.spot('bed', (xa + xb) / 2, yc, 0.5, math.pi / 2 if head > 0 else -math.pi / 2)


def make():
    R = Room('dormitory', 1, 1, res=1024)
    R.sockets(floor='floor', wall='ivory')
    # three parallel barrel vaults, running north-south
    for (c, w, j) in ((2.725, 4.75, 2.1), (8.0, 5.2, 2.5), (C - 2.725, 4.75, 2.1)):
        pr = arch_profile(c, w, 0, j, 24)
        R.cut(prism(pr, 'y', T - 0.02, C - T + 0.02, arch_mats(len(pr), 'floor', 'ivory')))
    # a cross vault through the middle, east-west
    pr = arch_profile(8, 3.4, 0, 2.5, 18)
    R.cut(prism(pr, 'x', T - 0.02, C - T + 0.02, arch_mats(len(pr), 'floor', 'ivory')))
    # squat arcades between them
    for xw in (5.25, C - 5.25):
        for y in (1.75, 4.55, 11.45, 14.25):
            pa = arch_profile(y, 1.9, 0, 1.15, 12)
            R.cut(prism(pa, 'x', xw - 0.3, xw + 0.3, arch_mats(len(pa), 'floor', 'ivory')))
    # a band of green paint to shoulder height, on every wall
    for (x0, y0, x1, y1) in ((T, T, C - T, T + 0.02), (T, C - T - 0.02, C - T, C - T), (T, T, T + 0.02, C - T), (C - T - 0.02, T, C - T, C - T)):
        for (a, b) in ((0.3, 6.45), (9.55, 15.7)):
            if y1 - y0 < 0.1: R.nocol.add(box(max(x0, a), y0, 0, min(x1, b), y1, 1.3, 'green', skip=('-z',)))
            else: R.nocol.add(box(x0, max(y0, a), 0, x1, min(y1, b), 1.3, 'green', skip=('-z',)))
    # lunette windows at the ends of the side vaults
    for c in (2.725, C - 2.725):
        for (y0, y1) in ((T - 0.01, T + 0.01), (C - T - 0.01, C - T + 0.01)):
            R.light(lunette(c, 3.4, 2.35, y0, y1, 'e_sky'))
    # the beds: heads to the outer walls in the side vaults, heads to the arcade in the middle one
    ys = (1.3, 2.75, 4.2, 5.65, 10.35, 11.8, 13.25, 14.7)
    for y in ys:
        bed(R, T + 0.05, y, -1)
        bed(R, C - T - 0.05, y, +1)
    for y in ys:
        # a small shelf over each head, with a night light below it
        bshelf(R, T, y + 0.4, 1.2, 0.8, '+x', rows=2, depth=0.24, frame='oak')
        bshelf(R, C - T, y - 0.4, 1.2, 0.8, '-x', rows=2, depth=0.24, frame='oak')
    for y in (2.025, 3.475, 4.925, 11.075, 12.525, 13.975):
        for (xx, sg) in ((T + 0.25, 1), (C - T - 0.25, -1)):
            R.parts.add(box(xx - 0.2, y - 0.2, 0, xx + 0.2, y + 0.2, 0.55, 'walnut', skip=('-z',)))
            candle(R, xx, y, 0.55, h=0.08, flame=0.04)
    for (y, xs) in ((3.2, (5.45, 10.55)), (4.3, (5.45, 10.55)), (11.7, (5.45, 10.55)), (12.8, (5.45, 10.55))):
        bed(R, xs[0], y, -1)
        bed(R, xs[1], y, +1)
    for y in (3.75, 12.25):
        for (xx, sg) in ((5.7, 1), (C - 5.7, -1)):
            R.parts.add(box(xx - 0.18, y - 0.18, 0, xx + 0.18, y + 0.18, 0.55, 'walnut', skip=('-z',)))
            candle(R, xx, y, 0.55, h=0.08, flame=0.04)
    # dim lamps down the crowns
    for y in (1.6, 4.4, 11.6, 14.4):
        pendant(R, 2.725, y, 3.3, 4.47, r=0.14, em='e_dim')
        pendant(R, C - 2.725, y, 3.3, 4.47, r=0.14, em='e_dim')
    for y in (2.2, 5.4, 10.6, 13.8):
        pendant(R, 8, y, 3.6, 5.1, r=0.16, em='e_lamp')
    for x in (4.0, 12.0):
        pendant(R, x, 8, 3.2, 4.2, r=0.16, em='e_amber')
    # tall bookcases on the end walls of the middle vault, beside the doors
    bshelf(R, 5.55, T, 0, 0.9, '+y', rows=5, frame='oak')
    bshelf(R, C - 5.55 - 0.9, T, 0, 0.9, '+y', rows=5, frame='oak')
    bshelf(R, 5.55 + 0.9, C - T, 0, 0.9, '-y', rows=5, frame='oak')
    bshelf(R, C - 5.55, C - T, 0, 0.9, '-y', rows=5, frame='oak')
    # walks: the middle aisle, the cross aisle and the side aisles
    m = loop(R, [(8, 1.6), (8, 8), (8, C - 1.6)], close=False)
    w = loop(R, [(1.6, 8), (3.4, 8), (3.4, 1.4), (3.4, C - 1.4)], close=False)
    e = loop(R, [(C - 1.6, 8), (C - 3.4, 8), (C - 3.4, 1.4), (C - 3.4, C - 1.4)], close=False)
    R.link(w[1], m[1], e[1])
    R.link(R.navpt(3.4, C - 1.4), w[1])
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Dormitory', weight=6,
                  blurb='Beds, made. Every one of them made, and a book on every pillow-shelf. Someone expects a lot of guests.')
    R.meta['box'] = [[T, 0, T], [C - T, 5.1, C - T]]
    return R
