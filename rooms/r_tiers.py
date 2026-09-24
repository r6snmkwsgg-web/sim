"""The Tiers: two storeys of balconies round a square void, the lower one deeper than the upper, so
from the floor they step back like the boxes of a theatre. Stairs climb inside the void. Shelves on
every balcony; a chandelier hangs in the middle of it all."""
from lib import *
from kit_f import *


def make():
    R = Room('tiers', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, R.hi - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    rr, ra, rs, ro = rot180(W)
    Z1, Z2 = 4.5, LH
    d1, d2 = 7.5, 4.0                        # depth of each balcony from the wall
    # the balconies: square rings of slab
    for (d, z, th) in ((d1, Z1, 0.35), (d2, Z2, 0.4)):
        for (x0, y0, x1, y1) in ((T, T, W - T, d), (T, W - d, W - T, W - T), (T, d, d, W - d), (W - d, d, W - T, W - d)):
            R.parts.add(box(x0, y0, z - th, x1, y1, z, 'tile', top='floor', bottom='plaster'))
        R.parts.add(box(d - 0.12, d - 0.12, z - th - 0.25, W - d + 0.12, d + 0.0, z - th, 'tile', skip=('+z',)))       # fascia beams
        R.parts.add(box(d - 0.12, W - d, z - th - 0.25, W - d + 0.12, W - d + 0.12, z - th, 'tile', skip=('+z',)))
        R.parts.add(box(d - 0.12, d, z - th - 0.25, d, W - d, z - th, 'tile', skip=('+z',)))
        R.parts.add(box(W - d, d, z - th - 0.25, W - d + 0.12, W - d, z - th, 'tile', skip=('+z',)))
    # stairs: floor to the first balcony inside the void (two, turned through 180 degrees)
    n1 = 22
    fA = (10.0, d1, 10.0 + n1 * 0.3, d1 + 2.2)
    landA = (fA[2], d1, fA[2] + 2.2, d1 + 2.2)
    # first balcony to the second, on the balcony along the side walls
    n2 = 17
    fB = (d2, 12.0, d2 + 1.8, 12.0 + n2 * 0.3)
    landB = (d2, fB[3], d2 + 1.8, fB[3] + 1.8)
    open1 = {'S': [], 'N': [], 'W': [], 'E': []}
    open2 = {'S': [], 'N': [], 'W': [], 'E': []}
    for half in range(2):
        f1, l1, f2, l2 = fA, landA, fB, landB
        ax1, ax2 = '+x', '+y'
        if half:
            f1, l1, f2, l2 = rr(fA), rr(landA), rr(fB), rr(landB)
            ax1, ax2 = ra(ax1), ra(ax2)
        fx = f1[0] if ax1 == '+x' else f1[2]
        flight_thin(R, fx, f1[1], 0.0, f1[3] - f1[1], n1, Z1 / n1, 0.3, ax1, m='terrazzo', side='tile')
        for yy in (f1[1] + 0.06, f1[3] - 0.06):
            rail_line(R, fx, yy, Z1 / n1, fx + (1 if ax1 == '+x' else -1) * n1 * 0.3, yy, Z1)
        deck(R, *l1, Z1, th=0.35)
        rect_rails(R, *l1, Z1, sides=('NE' if not half else 'SW'))
        (open1['S'] if not half else open1['N']).append((l1[0], l1[2]))
        flight_rect(R, f2, ax2, Z1, Z2)
        deck(R, *l2, Z2, th=0.4)
        rect_rails(R, *l2, Z2, sides=('EN' if not half else 'WS'))
        (open2['W'] if not half else open2['E']).append((l2[1], l2[3]))
        # the first flight's landing leaves a gap in the balcony rail
    # balustrades round the void at both levels
    for (d, z, op) in ((d1, Z1, open1), (d2, Z2, open2)):
        rect_rails(R, d - 0.25, d - 0.25, W - d + 0.25, W - d + 0.25, z, opens=op, kind='stone', inset=0.12)
    # books: ground floor, first balcony (all round), second balcony (between the doorways)
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), z=0, rows=8, frame='walnut')
    wall_shelves(R, ((0.8, W - 0.8),), z=Z1, rows=6, frame='walnut')
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), z=Z2, rows=11, frame='walnut')
    # a sunken court on the floor of the void
    R.pool(12.0, 12.0, W - 12.0, W - 12.0, 0.6, m='mosaic')
    for x in (14.0, 18.0):
        for y in (12.01, W - 12.01):
            R.light(box(x - 0.2, y - 0.03, -0.28, x + 0.2, y + 0.03, -0.15, 'e_pool'))
    # reading tables either side of it
    for (x, y, a) in ((16, 10.8, 0), (16, W - 10.8, 0), (10.8, 16, math.pi / 2), (W - 10.8, 16, math.pi / 2)):
        R.parts.add(box(-1.6, -0.5, 0.72, 1.6, 0.5, 0.78, 'walnut').xform(a, x, y))
        for s in (-1.3, 1.3):
            R.parts.add(box(s - 0.08, -0.4, 0, s + 0.08, 0.4, 0.72, 'walnut', skip=('-z',)).xform(a, x, y))
        R.light(sphere(x, y, 0.95, 0.1, 8, 4, 'e_candle'))
    # the chandelier, three rings, and lamps under the balconies
    chandelier(R, 16, 16, 9.5, 3.2, n=18, chain=R.hi - 0.1, bulb=0.16, tiers=3)
    for k in range(8):
        p = 2.4 + k * (W - 4.8) / 7
        for (x, y) in ((p, 2.2), (p, W - 2.2), (2.2, p), (W - 2.2, p)):
            R.light(cyl(x, y, Z1 - 0.62, Z1 - 0.58, 0.3, 12, side='e_lamp', top='e_lamp', bottom='e_lamp'))
            R.light(cyl(x, y, Z2 - 0.67, Z2 - 0.63, 0.3, 12, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.light(box(10.0, 10.0, R.hi - 0.16, W - 10.0, W - 10.0, R.hi - 0.14, 'e_sky'))
    # walkers on every level
    loop(R, ((2.2, 2.2), (16, 2.2), (W - 2.2, 2.2), (W - 2.2, 16), (W - 2.2, W - 2.2), (16, W - 2.2), (2.2, W - 2.2), (2.2, 16)))
    loop(R, ((2.4, 2.4), (16, 2.4), (W - 2.4, 2.4), (W - 2.4, 16), (W - 2.4, W - 2.4), (16, W - 2.4), (2.4, W - 2.4), (2.4, 16)), z=Z1)
    loop(R, ((2.2, 2.2), (16, 2.2), (W - 2.2, 2.2), (W - 2.2, 16), (W - 2.2, W - 2.2), (16, W - 2.2), (2.2, W - 2.2), (2.2, 16)), z=Z2)
    R.spot('probe', 16, 16, 5.5)
    R.meta.update(label='The Tiers', weight=8,
                  blurb='Balconies above balconies, all of them lined with books, all of them empty. From the top one you can see everything except who is on the one below.')
    R.meta['box'] = [[T, -0.6, T], [W - T, R.hi - 0.1, W - T]]
    return R
