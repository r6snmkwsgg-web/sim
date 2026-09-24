"""The Carriages: the inside of a train that is not going anywhere, laid out in a hall. Two rows of
compartments either side of a corridor, benches facing, luggage racks full of books, and windows
that look out onto more books."""
from lib import *
from kit_e import *


def make():
    R = Room('carriages', 2, 1, res=1024)
    R.sockets(rect=2.5)
    W, D = R.W, R.D
    cy = D / 2
    # a low carriage roof over the whole hall
    jamb, rise = 2.75, 0.85
    pr = arch_profile(cy, D - 2 * T + 0.04, 0, jamb, 32, rise=rise)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'floor', 'damask')))
    # roof lanterns: a clerestory slot down the middle
    R.cut(box(1.5, cy - 0.6, jamb + rise - 0.2, W - 1.5, cy + 0.6, jamb + rise + 0.5, 'plaster'))
    R.light(box(1.5, cy - 0.45, jamb + rise + 0.44, W - 1.5, cy + 0.45, jamb + rise + 0.47, 'e_panel'))
    for k in range(9):
        x = 1.5 + k * (W - 3.0) / 8
        R.parts.add(box(x - 0.06, cy - 0.62, jamb + rise - 0.25, x + 0.06, cy + 0.62, jamb + rise + 0.5, 'walnut'))
    # the compartments: 2.667 m bays, two rows. Bays at x=8 and 24 are open vestibules.
    P = 8.0 / 3.0
    xs = [P * k for k in range(1, 12)]            # bay centres 2.67 .. 29.33
    c0, c1, hc = 3.5, cy - 1.5, 2.45                # south row from y=c0 to c1 (mirrored north); wall height
    wt = 0.09
    for side in (0, 1):
        f = (lambda y: y) if side == 0 else (lambda y: D - y)
        Y = lambda a, b: tuple(sorted((f(a), f(b))))
        ys_back, ys_front = Y(c0 - wt, c0), Y(c1, c1 + wt)
        face = math.pi / 2 if side == 0 else -math.pi / 2       # looking toward the corridor
        for i, x in enumerate(xs):
            xa, xb = x - P / 2, x + P / 2
            vest = abs(x - 8.0) < 0.1 or abs(x - 24.0) < 0.1
            if vest:
                # open vestibule: just a lintel front and back
                for (y0, y1) in (ys_back, ys_front):
                    R.parts.add(box(xa, y0, 2.15, xb, y1, hc, 'walnut'))
                R.parts.add(box(xa + 0.05, *Y(c0, c1)[0:1], 0, xb - 0.05, Y(c0, c1)[1], 0.012, 'carpet', skip=('-z',)))
                continue
            # back wall with a window onto the outer corridor
            y0, y1 = ys_back
            R.parts.add(box(xa, y0, 0, xb, y1, 0.95, 'walnut'))
            R.parts.add(box(xa, y0, 2.0, xb, y1, hc, 'walnut'))
            R.parts.add(box(xa, y0, 0.95, xa + 0.45, y1, 2.0, 'walnut'))
            R.parts.add(box(xb - 0.45, y0, 0.95, xb, y1, 2.0, 'walnut'))
            R.parts.add(box(xa + 0.4, y0 - 0.05, 0.92, xb - 0.4, y1 + 0.05, 0.97, 'brass'))
            R.parts.add(box(x - 0.02, y0 + 0.02, 0.95, x + 0.02, y1 - 0.02, 2.0, 'brass'))
            # front wall with a sliding door, pushed half open
            y0, y1 = ys_front
            dx0, dx1 = x - 0.1, x + 0.75
            R.parts.add(box(xa, y0, 0, dx0, y1, hc, 'walnut'))
            R.parts.add(box(dx1, y0, 0, xb, y1, hc, 'walnut'))
            R.parts.add(box(dx0, y0, 2.1, dx1, y1, hc, 'walnut'))
            s = -1 if side == 0 else 1       # the door leaf slides on the corridor side
            yl = (y1 + 0.005, y1 + 0.05) if side == 0 else (y0 - 0.05, y0 - 0.005)
            R.parts.add(box(dx0 - 0.55, yl[0], 0.02, dx0 + 0.12, yl[1], 2.08, 'walnut'))
            R.parts.add(box(dx0 - 0.45, yl[0] - 0.005, 1.0, dx0 + 0.02, yl[1] + 0.005, 1.9, 'brass'))
            # facing benches along the partitions, luggage racks of books above them
            for (bx, fa) in ((xa + 0.05, 0.0), (xb - 0.05, math.pi)):
                sx = 1 if fa == 0 else -1
                ya_, yb_ = Y(c0 + 0.05, c0 + 1.9)
                R.parts.add(box(min(bx, bx + sx * 0.55), ya_, 0, max(bx, bx + sx * 0.55), yb_, 0.44, 'velvet', skip=('-z',)))
                R.parts.add(box(min(bx, bx + sx * 0.14), ya_, 0.44, max(bx, bx + sx * 0.14), yb_, 1.15, 'velvet'))
                for k in range(2):
                    R.spot('sit', bx + sx * 0.33, (ya_ + yb_) / 2 + (k - 0.5) * 0.8, 0.44, fa)
                # the rack: one shelf row of books on brass brackets
                if fa == 0: R.shelf(bx, yb_, 1.75, yb_ - ya_, '+x', rows=1, row_h=0.36, depth=0.36, frame='brass', back=False, crown=False)
                else:       R.shelf(bx, ya_, 1.75, yb_ - ya_, '-x', rows=1, row_h=0.36, depth=0.36, frame='brass', back=False, crown=False)
                # a little lamp on the partition over the bench
                ly = yb_ + 0.25 if side == 0 else ya_ - 0.25
                R.parts.add(box(min(bx, bx + sx * 0.08), ly - 0.05, 1.45, max(bx, bx + sx * 0.08), ly + 0.05, 1.6, 'brass'))
                R.light(sphere(bx + sx * 0.12, ly, 1.62, 0.06, 8, 4, 'e_amber'))
            # a ceiling light in each compartment, hung from the partition tops
            R.parts.add(box(xa, f(0.5 * (c0 + c1)) - 0.03, hc - 0.05, xb, f(0.5 * (c0 + c1)) + 0.03, hc, 'brass'))
            R.light(cyl(x, f(0.5 * (c0 + c1)), hc - 0.12, hc - 0.05, 0.18, 14, side='e_lamp', top='e_lamp', bottom='e_lamp'))
            # a small table under the window
            ty0, ty1 = Y(c0, c0 + 0.4)
            R.parts.add(box(x - 0.3, ty0, 0.68, x + 0.3, ty1, 0.72, 'walnut'))
        for k in range(12):
            xp = P / 2 + k * P
            R.parts.add(box(xp - 0.045, *Y(c0 - wt, c1 + wt)[0:1], 0, xp + 0.045, Y(c0 - wt, c1 + wt)[1], hc + 0.03, 'walnut'))
    # outer corridors: bookcases along the outer walls, between the doorways; lamps along them
    wall_shelves(R, rows=6, frame='walnut', sides='SN')
    for k in range(12):
        x = 1.33 + k * P
        for y in ((T + c0) / 2, D - (T + c0) / 2):
            R.light(cyl(x, y, 2.66, 2.7, 0.2, 14, side='e_panel', top='e_panel', bottom='e_panel'))
    # carpet down the middle corridor
    R.parts.add(box(2.0, cy - 0.7, 0, W - 2.0, cy + 0.7, 0.012, 'carpet', skip=('-z',)))
    # a green exit sign over the far door that goes nowhere different
    for (x0, x1) in ((T + 0.02, T + 0.06), (W - T - 0.06, W - T - 0.02)):
        R.light(box(x0, cy - 0.35, 2.62, x1, cy + 0.35, 2.82, 'e_exit'))
    # end walls: short cases beside the corridor
    for (a, b) in ((T + 0.2, 2.9), (D - 2.9, D - T - 0.2)):
        R.shelf(T, b, 0, b - a, '+x', rows=5, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=5, frame='walnut')
    # walkers
    mid = loop(R, [(1.2, cy), (8.0, cy), (16.0, cy), (24.0, cy), (W - 1.2, cy)], close=False)
    so = loop(R, [(1.0, 1.9), (8.0, 1.9), (16.0, 1.9), (24.0, 1.9), (W - 1.0, 1.9)], close=False)
    no = loop(R, [(1.0, D - 1.9), (8.0, D - 1.9), (16.0, D - 1.9), (24.0, D - 1.9), (W - 1.0, D - 1.9)], close=False)
    R.link(so[1], mid[1], no[1]); R.link(so[3], mid[3], no[3])
    R.link(so[0], mid[0], no[0]); R.link(so[-1], mid[-1], no[-1])
    R.spot('probe', 16.0, cy, 1.7)
    R.meta.update(label='The Carriages', weight=6,
                  blurb='Compartments either side of a corridor, like a night train. The windows look out onto bookshelves. Nobody checks your ticket; nobody has one.')
    R.meta['box'] = [[T, 0, T], [W - T, jamb + rise + 0.5, D - T]]
    return R
