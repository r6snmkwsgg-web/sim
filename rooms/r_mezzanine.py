"""The Mezzanine: two galleries float along the long walls at 3.6 m on posts too thin to hold them.
Four stairs rise from the ends. Books above, books below."""
from lib import *
from kit_e import *


def make():
    R = Room('mezzanine', 2, 1, res=1024)
    R.sockets()
    W, D = R.W, R.D
    cy = D / 2
    H = 7.3
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='floor', top='plaster'))
    # skylights down the middle
    for k in range(7):
        x = 4.0 + 4.0 * k
        R.cut(box(x - 1.5, cy - 2.5, H - 0.05, x + 1.5, cy + 2.5, R.hi + 0.5, 'plaster'))
        R.light(box(x - 1.5, cy - 2.5, R.hi - 0.09, x + 1.5, cy + 2.5, R.hi - 0.05, 'e_sky'))
    gz, gd = 3.6, 3.0                 # gallery deck height; front edge at y = gd (and D - gd)
    th = 0.14
    sx0, sx1 = 0.4, 1.6               # the flights run along the end walls in x = sx0..sx1
    n, rs, rn = 16, gz / 16, 0.3
    L = n * rn
    yl = 1.5                          # where the flights arrive (the landing at the wall is y < yl)
    for side in (0, 1):
        f = (lambda y: y) if side == 0 else (lambda y: D - y)
        Y = lambda a, b: tuple(sorted((f(a), f(b))))
        # the deck: full length, less the two holes the flights come up through
        y0, y1 = Y(T, gd)
        R.parts.add(box(sx1, y0, gz - th, W - sx1, y1, gz, 'iron', top='oak'))
        for (xa, xb) in ((T, sx1), (W - sx1, W - T)):
            ya, yb = Y(T, yl)
            R.parts.add(box(xa, ya, gz - th, xb, yb, gz, 'iron', top='oak'))
        # thin iron posts along the front edge
        for k in range(11):
            x = sx1 + 0.4 + k * (W - 2 * sx1 - 0.8) / 10
            R.parts.add(cyl(x, f(gd - 0.08), 0, gz - th, 0.04, 8, side='iron', caps=False))
        # the rail along the front edge
        rail(R, [(sx1 + 0.03, f(gd - 0.03), gz), (W - sx1 - 0.03, f(gd - 0.03), gz)])
        # the flights, one at each end, rising toward this gallery's wall
        foot = f(yl + L)
        for (x0, xs) in ((sx0, sx1 + 0.03), (W - sx1, W - sx1 - 0.03)):
            R.flight(x0, foot, 0, sx1 - sx0, n, rs, rn, '-y' if side == 0 else '+y', m='oak', side='walnut')
            # rail on the open side, and a stringer wall under it so nobody walks beneath
            rail(R, [(xs, foot, 0), (xs, f(yl), gz)])
            xw = sx1 + 0.03 if x0 < W / 2 else W - sx1 - 0.03
            R.parts.add(wedge((xw, foot), (xw, f(yl)), 0.06, 0, 0, 0.0, gz - 0.25, 'walnut'))
            # rails round the landing hole's inner edge (where the deck overhangs the flight)
            rail(R, [(xs, f(yl), gz), (xs, f(gd - 0.03), gz)], h=0.95)
    # shelves: below the galleries, and on the galleries
    for (a, b) in LONG_SEGS:
        R.shelf(a, T, 0, b - a, '+y', rows=7, frame='walnut')
        R.shelf(b, D - T, 0, b - a, '-y', rows=7, frame='walnut')
    for (a, b) in ((sx1 + 0.1, 15.7), (16.3, W - sx1 - 0.1)):
        R.shelf(a, T, gz, b - a, '+y', rows=8, frame='walnut')
        R.shelf(b, D - T, gz, b - a, '-y', rows=8, frame='walnut')
    # lamps: under the galleries, over the middle
    for k in range(8):
        x = 2.0 + 4.0 * k
        for y in ((T + gd) / 2, D - (T + gd) / 2):
            R.light(cyl(x, y, gz - th - 0.04, gz - th - 0.01, 0.25, 16, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    for x in (6.0, 12.0, 20.0, 26.0):
        pendant(R, x, cy, 3.4, H, r=0.35)
    # long tables down the middle
    for (xa, xb) in ((5.0, 11.0), (13.0, 19.0), (21.0, 27.0)):
        for yc in (cy - 2.6, cy + 2.6):
            table(R, xa, yc - 0.45, xb, yc + 0.45, m='oak', top='leather')
            for j in range(4):
                x = xa + 0.8 + j * (xb - xa - 1.6) / 3
                chair(R, x, yc - 0.9, math.pi / 2, frame='oak', seat='green')
                chair(R, x, yc + 0.9, -math.pi / 2, frame='oak', seat='green')
            table_lamp(R, (xa + xb) / 2, yc, 0.76)
    # amber lamps on the gallery rails for the night
    for x in (4.0, 12.0, 20.0, 28.0):
        for y in (gd - 0.03, D - gd + 0.03):
            R.light(sphere(x, y, gz + 1.05, 0.07, 8, 4, 'e_amber'))
    # walkers
    fl = loop(R, [(2.4, cy), (4.0, 4.2), (16.0, 3.8), (28.0, 4.2), (W - 2.4, cy), (28.0, D - 4.2), (16.0, D - 3.8), (4.0, D - 4.2)])
    for side in (0, 1):
        f = (lambda y: y) if side == 0 else (lambda y: D - y)
        g = [R.navpt(x, f(1.6), gz) for x in (2.6, 8.0, 16.0, 24.0, W - 2.6)]
        R.link(*g)
        for (x, gi, fi) in ((1.0, 0, 0), (W - 1.0, 4, 4)):
            a = R.navpt(x, f(yl + L + 0.6)); b = R.navpt(x, f(0.9), gz)
            R.link(fl[fi], a, b, g[gi])
    R.spot('probe', 16.0, cy, 2.5)
    R.meta.update(label='The Mezzanine', weight=7,
                  blurb='Two galleries hang along the walls on posts no thicker than a broom handle. They have held so far.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    return R
