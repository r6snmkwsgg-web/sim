"""The Stairwell: a square well of a room with a gallery of books running round all four walls
halfway up. A switchback stair climbs to it on the west side, and an identical one climbs down
again on the east, so you can go round and round for as long as you like."""
from lib import *
from kit_d import *

GZ = 4.2            # gallery floor
GD = 2.4            # gallery depth
RISE, RUN, NS = 0.175, 0.3, 12


def stair(R, s):
    """One switchback stair; s = +1 for the west one, -1 mirrors it to the east."""
    X = (lambda x: x) if s > 0 else (lambda x: C - x)
    def xs(a, b): return (min(X(a), X(b)), max(X(a), X(b)))
    w = 1.6
    yf, ym = 11.0, 11.0 - NS * RUN            # foot of the first flight, its top (the mid landing)
    a0, a1 = xs(3.0, 4.6)                     # first flight
    b0, b1 = xs(4.6, 6.2)                     # second flight
    l0, l1 = xs(3.0, 6.2)                     # mid landing
    gi = I1 - GD                              # the north gallery's inner edge
    R.flight(a0, yf, 0, w, NS, RISE, RUN, '-y', m='floor', side='tile')
    R.parts.add(box(l0, ym - w, 0, l1, ym, NS * RISE, 'tile', top='floor'))
    R.flight(b0, ym, NS * RISE, w, NS, RISE, RUN, '+y', m='floor', side='tile')
    R.parts.add(box(b0, yf, GZ - 0.3, b1, gi + 0.02, GZ, 'plaster', top='floor', sides='tile'))    # bridge to the gallery
    # the wall between the two flights, as high as the upper flight's rail
    wx0, wx1 = xs(4.55, 4.65)
    R.parts.add(slope_y(wx0, wx1, ym - 0.02, yf, 0, 0, NS * RISE + 1.0, GZ + 1.0, 'tile'))
    R.parts.add(slope_y(wx0 - 0.03, wx1 + 0.03, ym - 0.02, yf, NS * RISE + 1.0, GZ + 1.0, NS * RISE + 1.06, GZ + 1.06, 'brass'))
    R.parts.add(box(wx0, yf, GZ, wx1, gi, GZ + 1.0, 'tile', skip=('-z',)))
    R.parts.add(box(wx0 - 0.03, yf, GZ + 1.0, wx1 + 0.03, gi, GZ + 1.06, 'brass'))
    # rails: outside of the first flight, round the mid landing, outside of the second flight and bridge
    ox = X(3.0); ix = X(6.2)
    brass_rail(R, ox, yf, 0, ox, ym, NS * RISE)
    brass_rail(R, ox, ym, NS * RISE, ox, ym - w, NS * RISE)
    brass_rail(R, ox, ym - w, NS * RISE, ix, ym - w, NS * RISE)
    brass_rail(R, ix, ym - w, NS * RISE, ix, ym, NS * RISE)
    brass_rail(R, ix, ym, NS * RISE, ix, yf, GZ)
    brass_rail(R, ix, yf, GZ, ix, gi, GZ)
    # the solid landing's front gets a bookcase
    bookcase(R, l1 - 0.05, ym - w, 0, l1 - l0 - 0.1, '-y', 4, frame='walnut')
    # walkers
    p = [R.navpt(X(3.8), 12.2), R.navpt(X(3.8), yf - 0.2, 0.0), R.navpt(X(3.8), ym + 0.2, NS * RISE), R.navpt(X(4.6), ym - 0.8, NS * RISE),
         R.navpt(X(5.4), ym + 0.2, NS * RISE), R.navpt(X(5.4), yf - 0.2, GZ), R.navpt(X(5.4), I1 - 1.2, GZ)]
    R.link(*p)
    return p


def make():
    R = Room('stairwell', 1, 1, res=1024)
    shell(R, TOP, floor='terrazzo', wall='tile', top='plaster')
    H = TOP - 0.05
    g0, g1 = I0 + GD, I1 - GD
    # the gallery: a slab round all four walls
    for (x0, y0, x1, y1) in ((I0, I0, I1, g0), (I0, g1, I1, I1), (I0, g0, g0, g1), (g1, g0, I1, g1)):
        R.parts.add(box(x0, y0, GZ - 0.3, x1, y1, GZ, 'plaster', top='floor', sides='tile'))
    # its balustrade, open where the two bridges land
    def bal(x0, y0, x1, y1): R.parts.add(balustrade(x0, y0, x1, y1, GZ, 1.0, 'tile', 'brass'))
    bal(g0 - 0.2, g0 - 0.2, g1 + 0.2, g0)
    bal(g0 - 0.2, g0, g0, g1)
    bal(g1, g0, g1 + 0.2, g1)
    bal(g0 - 0.2, g1, 4.6, g1 + 0.2)
    bal(6.2, g1, 9.8, g1 + 0.2)
    bal(11.4, g1, g1 + 0.2, g1 + 0.2)
    # a stone column under each inner corner of the gallery
    for (x, y) in ((g0, g0), (g1, g0), (g0, g1), (g1, g1)):
        R.parts.add(box(x - 0.25, y - 0.25, 0, x + 0.25, y + 0.25, GZ - 0.3, 'tile', skip=('-z', '+z')))
    wst = stair(R, 1); est = stair(R, -1)
    # books: under the gallery, and all round the gallery
    for (a, b) in ((0.8, 6.2), (9.8, C - 0.8)):
        for f in ('+y', '-y', '+x', '-x'):
            wall_shelf(R, f, a, b, 0, rows=8, frame='walnut')
    for f in ('+y', '-y', '+x', '-x'):
        wall_shelf(R, f, I0 + 0.45, I1 - 0.45, GZ, rows=7, frame='walnut')
    # light: a skylight over the well, lamps under the gallery, lamps along the gallery wall
    R.cut(box(g0 + 1.0, g0 + 1.0, H - 0.05, g1 - 1.0, g1 - 1.0, H + 0.35, 'plaster'))
    R.light(box(g0 + 1.1, g0 + 1.1, H + 0.3, g1 - 1.1, g1 - 1.1, H + 0.31, 'e_sky', skip=('+z', '-x', '+x', '-y', '+y')))
    for p in (2.0, 5.5, 10.5, 14.0):
        for (x, y) in ((p, 1.6), (p, C - 1.6), (1.6, p), (C - 1.6, p)):
            R.light(box(x - 0.18, y - 0.18, GZ - 0.32, x + 0.18, y + 0.18, GZ - 0.31, 'e_lamp', skip=('+z', '-x', '+x', '-y', '+y')))
    for p in (4.0, 8.0, 12.0):
        for (x, y) in ((p, I0 + 0.4), (p, I1 - 0.4), (I0 + 0.4, p), (I1 - 0.4, p)):
            pendant(R, x, y, GZ + 2.4, r=0.14, m='e_amber', top=H)
    # walkers: round the ground, round the gallery
    gl = loop(R, [(1.5, 1.5), (8, 1.5), (14.5, 1.5), (14.5, 8), (14.5, 12.2), (8, 12.2), (1.5, 12.2), (1.5, 8)])
    up = loop(R, [(1.2, 1.2), (8, 1.2), (14.8, 1.2), (14.8, 8), (14.8, 14.6), (10.6, 14.6), (5.4, 14.6), (1.2, 14.6), (1.2, 8)], z=GZ)
    R.link(wst[0], gl[6]); R.link(est[0], gl[4])
    R.link(wst[-1], up[6]); R.link(est[-1], up[5])
    R.link(R.navpt(8, 1.5), R.navpt(8, 8), R.navpt(8, 12.2))
    R.spot('probe', 8, 5.0, 2.0)
    R.meta.update(label='The Stairwell', weight=5,
                  blurb='Up one stair, round the gallery, down the other, and you are back where you began. It is very good exercise, if you have forever.')
    return R
