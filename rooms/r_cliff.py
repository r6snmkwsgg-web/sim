"""The Cliff: two walls of books fourteen metres high face each other across a canyon. Catwalks run
along them at four, eight and twelve metres, stairs climb between, and one thin bridge crosses at
the top. Above the bookcases there is a gap, and a glow, and then the ceiling."""
from lib import *
from kit_f import *


def make():
    R = Room('cliff', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    rr, ra, rs, ro = rot180(W)
    F = 6.3                                  # the west cliff's face (the east one is W - F)
    A1, B1 = 8.0, 9.5                        # catwalk band F..A1, stair band A1..B1
    R.cut(box(F, T - 0.02, 0, W - F, W - T + 0.02, R.hi - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, T - 0.02, 14.0, W - T + 0.02, W - T + 0.02, R.hi - 0.1, 'tile', bottom='tile', top='plaster'))
    pr0 = arch_profile(0, DW, 0, DJ, 18)
    for (y, z) in ((8.0, 0.0), (24.0, 0.0), (8.0, LH), (24.0, LH)):
        p = [(a + y, b + z) for a, b in pr0]
        mats = arch_mats(len(p), 'terrazzo' if z == 0 else 'floor', 'tile')
        R.cut(prism(p, 'x', T - 0.05, F + 0.1, mats))
        R.cut(prism(p, 'x', W - F - 0.1, W - T + 0.05, mats))
    # the two cliffs of books, in bands between the catwalks
    tun = [(6.4, 9.6), (22.4, 25.6)]
    bands = [(0.0, 8, True), (4.0, 8, True), (LH, 8, True), (12.0, 4, True)]   # gaps over the tunnels (and the walk checker's column limit)
    for (z, rows, gapped) in bands:
        spans = [(0.8, 6.3), (9.7, 22.3), (25.7, W - 0.8)] if gapped else [(0.8, W - 0.8)]
        for (a, b) in spans:
            R.shelf(F, b, z, b - a, '+x', rows=rows, frame='walnut')
            R.shelf(W - F, W - b, z, b - a, '-x', rows=rows, frame='walnut')
    for x in (F, W - F):   # a cornice on the cliff tops, and the glow above them
        x0, x1 = (T, F + 0.25) if x == F else (W - F - 0.25, W - T)
        R.parts.add(box(x0, T, 13.85, x1, W - T, 14.05, 'tile'))
        xa = F - 1.0 if x == F else W - F + 0.9
        R.light(box(xa, 1.0, 14.05, xa + 0.1, W - 1.0, 14.15, 'e_amber'))
    # catwalks (half the plan; the other half is the same turned through 180 degrees)
    decks = [   # (rect, z, rail opens on the canyon side (x = A1) as y intervals, extra rail sides)
        ((F, 2.6, A1, 29.4), 4.0, [(17.0, 19.0)], 'SN'),
        ((F, 2.8, A1, 29.2), LH, [(17.0, 18.5), (25.0, 26.5)], ''),
        ((F, T, B1 + 0.1, 2.8), LH, [], 'E'),              # landing at the south door
        ((F, 29.2, B1 + 0.1, W - T), LH, [], 'E'),         # and at the north door
        ((F, 2.6, A1, 29.4), 12.0, [(9.5, 11.0), (15.2, 16.8)], 'SN'),
    ]
    stairs_ = [   # (rect, axis, z0, z1)
        ((A1, 11.0, B1, 17.0), '+y', 0.0, 4.0),
        ((A1, 19.0, B1, 25.0), '+y', 4.0, LH),
        ((A1, 11.0, B1, 17.0), '-y', LH, 12.0),
    ]
    lands = [   # (rect, z, rail sides)
        ((A1, 17.0, B1, 19.0), 4.0, 'E'),
        ((A1, 25.0, B1, 26.5), LH, 'EN'),
        ((A1, 17.0, B1, 18.5), LH, 'EN'),
        ((A1, 9.5, B1, 11.0), 12.0, 'ES'),
    ]
    for half in range(2):
        for (rect, z, opens, extra) in decks:
            sides = 'E' + extra
            op = {'E': opens}
            if rect[3] - rect[1] < 3:        # door landings: their canyon edge north (or south) of the catwalk
                sides = 'E' + ('N' if rect[1] < 5 else 'S')
                op = {'N': [(F, A1)]} if rect[1] < 5 else {'S': [(F, A1)]}
            r = rect
            if half: r, op, sides = rr(rect), ro(op), rs(sides)
            deck(R, *r, z, th=0.3, top='oak', m='iron', bottom='iron')
            rect_rails(R, *r, z, opens=op, sides=sides, post='iron')
        for (rect, axis, z0, z1) in stairs_:
            r, ax = (rr(rect), ra(axis)) if half else (rect, axis)
            x0 = r[0]
            n = 20
            if ax[1] == 'y':
                fy = r[1] if ax == '+y' else r[3]
                flight_thin(R, x0, fy, z0, r[2] - r[0], n, (z1 - z0) / n, 0.3, ax, m='oak', side='iron', under='iron', thick=0.3,
                            fill=2.2 if z0 == 0 else 0)
                for xr in (r[0] + 0.06, r[2] - 0.06):
                    rail_line(R, xr, fy, z0 + 0.2, xr, fy + (6.0 if ax == '+y' else -6.0), z1, post='iron')
        for (rect, z, sides) in lands:
            r, sd = (rr(rect), rs(sides)) if half else (rect, sides)
            deck(R, *r, z, th=0.3, top='oak', m='iron', bottom='iron')
            rect_rails(R, *r, z, sides=sd, post='iron')
        # lamps under the catwalks
        for z in (4.0, LH, 12.0):
            for y in (5.0, 13.0, 21.0, 27.0):
                x, yy = ((F + A1) / 2, y) if not half else (W - (F + A1) / 2, W - y)
                lamp(R, x, yy, z - 0.75, 0.16, chain=z - 0.3)
    # the bridge across the top
    deck(R, A1, 15.2, W - A1, 16.8, 12.0, th=0.3, top='oak', m='iron', bottom='iron')
    rect_rails(R, A1, 15.2, W - A1, 16.8, 12.0, sides='SN', post='iron')
    # the canyon floor: a long table, lamps, and a runner
    R.parts.add(box(14.6, 6.0, 0.0, 17.4, 26.0, 0.012, 'carpet'))
    for y0 in (8.0, 18.0):
        R.parts.add(box(15.3, y0, 0.72, 16.7, y0 + 6.0, 0.78, 'walnut'))
        for y in (y0 + 0.3, y0 + 5.7):
            R.parts.add(box(15.4, y - 0.08, 0.012, 16.6, y + 0.08, 0.72, 'walnut', skip=('-z',)))
        for k in range(3):
            y = y0 + 1.0 + k * 2.0
            R.nocol.add(cyl(16, y, 0.78, 1.15, 0.02, 6, side='brass', caps=False))
            R.nocol.add(cyl(16, y, 1.1, 1.22, 0.2, 12, side='green', top='green', bottom='green'))
            R.light(cyl(16, y, 1.08, 1.1, 0.17, 12, side='e_candle', top='e_candle', bottom='e_candle'))
            R.spot('read', 15.0, y, 0, 0.0)
    R.light(box(11.0, 3.0, R.hi - 0.16, 21.0, W - 3.0, R.hi - 0.14, 'e_sky'))
    chandelier(R, 16, 8.0, 7.0, 1.4, n=10, chain=R.hi - 0.1, bulb=0.13)
    chandelier(R, 16, 24.0, 7.0, 1.4, n=10, chain=R.hi - 0.1, bulb=0.13)
    # walkers
    loop(R, ((12.0, 2.5), (20.0, 2.5), (20.0, 29.5), (12.0, 29.5)))
    loop(R, ((7.3, 4.0), (7.3, 28.0)), z=4.0, close=False)
    loop(R, ((7.3, 1.8), (7.3, 30.2)), z=LH, close=False)
    loop(R, ((W - 7.3, 1.8), (W - 7.3, 30.2)), z=LH, close=False)
    R.spot('probe', 16, 12, 6.0)
    R.meta.update(label='The Cliff', weight=5,
                  blurb='Two walls of books face each other across a gap, fourteen metres high. The catwalks were built for someone braver than you, and for someone who knew which book they wanted.')
    R.meta['box'] = [[T, 0, T], [W - T, R.hi - 0.1, W - T]]
    return R
