"""The Stair Hall: a tall square hall. A wide stair climbs round all four sides, a flight and a long
landing on each, a quarter of the way up each time, and arrives at the gallery that joins the upper
doorways. A great chandelier hangs in the middle of the void."""
from lib import *
from kit_f import *


def make():
    R = Room('stairhall', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, R.hi - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    g, b = 3.6, 6.6                     # gallery depth, stair band's inner edge
    B = W - b; G = W - g
    Z = LH
    # the gallery ring at 8 m
    for (x0, y0, x1, y1) in ((T, T, W - T, g), (T, G, W - T, W - T), (T, g, g, G), (G, g, W - T, G)):
        deck(R, x0, y0, x1, y1, Z, th=0.4, top='floor', m='tile')
    # the stair: a flight and a landing on each side, climbing clockwise from the south-west
    zS, zE, zN = 2.6, 4.4, 6.2
    run = 0.3
    # south: flight from the floor, then a long landing to the south-east corner
    flight_thin(R, b, g, 0.0, b - g, 13, zS / 13, run, '+x', m='terrazzo', side='tile')
    xs = b + 13 * run
    deck(R, xs, g, G, b, zS, th=0.3)
    # east: flight, then the landing up to the north-east corner
    ye = b + 9 * run
    flight_thin(R, B, b, zS, G - B, 9, (zE - zS) / 9, run, '+y', m='terrazzo', side='tile', fill=0)
    deck(R, B, ye, G, G, zE, th=0.3)
    # north: flight going west, landing to the north-west corner
    xn = B - 9 * run
    flight_thin(R, B, B, zE, G - B, 9, (zN - zE) / 9, run, '-x', m='terrazzo', side='tile', fill=0)
    deck(R, g, B, xn, G, zN, th=0.3)
    # west: the last flight going south, then a broad landing that is part of the gallery
    yw = B - 9 * run
    flight_thin(R, g, B, zN, b - g, 9, (Z - zN) / 9, run, '-y', m='terrazzo', side='tile', fill=0)
    deck(R, g, g, b, yw, Z, th=0.4, top='floor', m='tile')
    # rails: flights
    def frails(x0, y0, x1, y1, za, zb, along):
        e = 0.06
        if along == 'x':
            for y in (y0 + e, y1 - e): rail_line(R, x0, y, za, x1, y, zb)
        else:
            for x in (x0 + e, x1 - e): rail_line(R, x, y0, za, x, y1, zb)
    frails(b, g, xs, b, 0.2, zS, 'x')
    frails(B, b, G, ye, zS + 0.2, zE, 'y')
    frails(xn, B, B, G, zN, zE + 0.2, 'x')
    frails(g, yw, b, B, Z, zN + 0.2, 'y')
    # rails: landings
    rect_rails(R, xs, g, G, b, zS, sides='SNE', opens={'N': [(B, G)]})
    rect_rails(R, B, ye, G, G, zE, sides='WEN', opens={'W': [(B, G)]})
    rect_rails(R, g, B, xn, G, zN, sides='SNW', opens={'S': [(g, b)]})
    rect_rails(R, g, g, b, yw, Z, sides='E', kind='stone', inset=0.12)
    # rails: the gallery's inner edge
    balus(R, b, g - 0.12, G, g - 0.12, Z)
    balus(R, G + 0.12, g, G + 0.12, G, Z)
    balus(R, g - 0.12, G + 0.12, G, G + 0.12, Z)
    balus(R, g - 0.12, yw, g - 0.12, G, Z)
    # piers under the landings
    for (x, y, z) in ((xs + 0.3, b - 0.3, zS), (15.0, b - 0.3, zS), (21.0, b - 0.3, zS), (B + 0.3, 14.0, zE), (B + 0.3, 20.0, zE), (B + 0.3, B - 0.3, zE),
                      (xn - 0.3, B + 0.3, zN), (16.0, B + 0.3, zN), (10.0, B + 0.3, zN), (b - 0.3, 18.0, Z), (b - 0.3, 12.0, Z), (b - 0.3, b - 0.3, Z)):
        pier(R, x, y, 0, z - (0.4 if z == Z else 0.3), 0.2)
    # books on every wall, both levels; a square of low stacks in the middle of the floor
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), z=0, rows=12, frame='walnut')
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), z=Z, rows=12, frame='walnut')
    for (x0, y0, x1, y1) in ((11.0, 10.0, 21.0, 10.0), (11.0, 22.0, 21.0, 22.0), (10.0, 11.0, 10.0, 21.0), (22.0, 11.0, 22.0, 21.0)):
        stack2_ax(R, x0, y0, x1, y1, 0, 5, frame='oak', crown='walnut', ends='walnut')
    R.parts.add(cyl(16, 16, 0, 0.74, 0.18, 12, side='walnut', caps=False))
    R.parts.add(cyl(16, 16, 0.74, 0.8, 1.3, 32, side='walnut', top='leather', bottom='walnut'))
    for k in range(6):
        a = k * math.pi / 3
        R.parts.add(box(-0.22, -0.22, 0, 0.22, 0.22, 0.45, 'velvet', skip=('-z',)).xform(a, 16 + 1.9 * math.cos(a), 16 + 1.9 * math.sin(a)))
        R.spot('sit', 16 + 1.9 * math.cos(a), 16 + 1.9 * math.sin(a), 0.45, a + math.pi)
    R.light(sphere(16, 16, 0.95, 0.12, 8, 4, 'e_candle'))
    # light: the chandelier, lamps under the gallery and the landings, a skylight, high windows
    chandelier(R, 16, 16, 9.0, 3.4, n=20, chain=R.hi - 0.1, bulb=0.17, tiers=3)
    for k in range(8):
        p = 2.2 + k * (W - 4.4) / 7
        for (x, y) in ((p, 1.9), (p, W - 1.9), (1.9, p), (W - 1.9, p)):
            R.light(cyl(x, y, Z - 0.46, Z - 0.43, 0.3, 12, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.light(box(11.0, 11.0, R.hi - 0.16, W - 11.0, W - 11.0, R.hi - 0.14, 'e_sky'))
    for p in (16.0,):
        for (x0, y0, x1, y1) in ((p - 2.5, T + 0.01, p + 2.5, T + 0.03), (p - 2.5, W - T - 0.03, p + 2.5, W - T - 0.01)):
            R.light(box(x0, y0, 13.2, x1, y1, 14.8, 'e_sky'))
        for (x0, y0, x1, y1) in ((T + 0.01, p - 2.5, T + 0.03, p + 2.5), (W - T - 0.03, p - 2.5, W - T - 0.01, p + 2.5)):
            R.light(box(x0, y0, 13.2, x1, y1, 14.8, 'e_sky'))
    # walkers
    loop(R, ((2.0, 2.0), (16, 2.0), (W - 2.0, 2.0), (W - 2.0, 16), (W - 2.0, W - 2.0), (16, W - 2.0), (2.0, W - 2.0), (2.0, 16)))
    loop(R, ((8.0, 8.0), (24.0, 8.0), (24.0, 24.0), (8.0, 24.0)))
    loop(R, ((2.0, 2.0), (16, 2.0), (W - 2.0, 2.0), (W - 2.0, 16), (W - 2.0, W - 2.0), (16, W - 2.0), (2.0, W - 2.0), (2.0, 16)), z=Z)
    loop(R, ((14.0, 5.1), (24.0, 5.1)), z=zS, close=False)
    R.spot('probe', 16, 12, 5.0)
    R.meta.update(label='The Stair Hall', weight=7,
                  blurb='A stair goes round the walls of a tall hall, one side at a time, and arrives at a gallery lined with books. It is a long way round for one floor.')
    R.meta['box'] = [[T, 0, T], [W - T, R.hi - 0.1, W - T]]
    return R
