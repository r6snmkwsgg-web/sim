"""The Great Stair: a hall 64 m square and 31 m high, filled by one monumental staircase. A broad
flight climbs north to a landing; two flights turn back south to a U-shaped gallery round three walls;
a second broad flight climbs north again, above the first, to a landing, and a bridge crosses the
void to the gallery on the north wall. A skylight over it all."""
from lib import *
from kit_g import *


def make():
    R = Room('greatstair', 4, 4, levels=4, res=2048)
    W, D = R.W, R.D
    keep = [(s, i, 2) for s in 'SWE' for i in range(4)] + [('N', i, 3) for i in range(4)]
    seal(R, upper_sockets(R, keep), floor='terrazzo', wall='tile')
    ceil = R.hi - 0.4
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, ceil, 'tile', bottom='terrazzo', top='plaster'))
    # a skylight well over the middle
    R.cut(box(22, 22, ceil - 0.1, 42, 42, ceil + 0.3, 'plaster'))
    R.light(box(22.3, 22.3, ceil + 0.26, 41.7, 41.7, ceil + 0.28, 'e_sky'))
    n, rise, run = 50, 0.16, 0.32              # 8 m up in 16 m
    g0 = 6.0                                    # depth of the galleries at 16 m
    ax0, aw = 27.0, 10.0                        # the broad flights
    # A: floor to the first landing
    flight(R, ax0, g0, 0, aw, n, rise, run, '+y', m='terrazzo', riser='tile')
    flight_rail(R, ax0, g0, 0, aw, n, rise, run, '+y')
    # the first landing (8 m)
    R.parts.add(box(17, 22, 7.4, 47, 28, 8, 'tile', top='terrazzo', bottom='plaster'))
    z = 8
    rail(R, 23, 22.07, 27, 22.07, z); rail(R, 37, 22.07, 41, 22.07, z)
    rail(R, 17, 27.93, 47, 27.93, z); rail(R, 17.07, 22, 17.07, 28, z); rail(R, 46.93, 22, 46.93, 28, z)
    # B: two flights back south to the gallery (16 m)
    for bx in (17.0, 41.0):
        flight(R, bx, 22, 8, 6, n, rise, run, '-y', m='terrazzo', riser='tile')
        flight_rail(R, bx, 22, 8, 6, n, rise, run, '-y')
    # the U gallery at 16 m: south, west and east walls
    z = 16
    R.parts.add(box(T - 0.02, T - 0.02, z - 0.6, W - T + 0.02, g0, z, 'tile', top='terrazzo', bottom='plaster'))
    R.parts.add(box(T - 0.02, g0, z - 0.6, g0, D - T + 0.02, z, 'tile', top='terrazzo', bottom='plaster'))
    R.parts.add(box(W - g0, g0, z - 0.6, W - T + 0.02, D - T + 0.02, z, 'tile', top='terrazzo', bottom='plaster'))
    y = g0 - 0.07
    for (a, b) in ((g0, 17), (23, 27), (37, 41), (47, W - g0)):
        rail(R, a, y, b, y, z)
    rail(R, g0 - 0.07, g0, g0 - 0.07, D - T, z); rail(R, W - g0 + 0.07, g0, W - g0 + 0.07, D - T, z)
    # piers under the gallery edges
    for (px, py) in ((16, g0 - 0.6), (48, g0 - 0.6), (g0 - 0.6, 16), (g0 - 0.6, 48), (W - g0 + 0.6, 16), (W - g0 + 0.6, 48)):
        R.parts.add(box(px - 0.6, py - 0.6, 0, px + 0.6, py + 0.6, z - 0.6, 'tile', skip=('-z', '+z')))
    # C: the second broad flight, above the first
    flight(R, ax0, g0, 16, aw, n, rise, run, '+y', m='terrazzo', riser='tile')
    flight_rail(R, ax0, g0, 16, aw, n, rise, run, '+y')
    # the top landing (24 m), a bridge north, the north gallery
    z = 24
    R.parts.add(box(24, 22, z - 0.6, 40, 28, z, 'tile', top='terrazzo', bottom='plaster'))
    R.parts.add(box(29, 28, z - 0.6, 35, D - g0, z, 'tile', top='terrazzo', bottom='plaster'))
    R.parts.add(box(T - 0.02, D - g0, z - 0.6, W - T + 0.02, D - T + 0.02, z, 'tile', top='terrazzo', bottom='plaster'))
    rail(R, 24, 22.07, 27, 22.07, z); rail(R, 37, 22.07, 40, 22.07, z)
    rail(R, 24.07, 22, 24.07, 28, z); rail(R, 39.93, 22, 39.93, 28, z)
    rail(R, 24, 27.93, 29, 27.93, z); rail(R, 35, 27.93, 40, 27.93, z)
    rail(R, 29.07, 28, 29.07, D - g0, z); rail(R, 34.93, 28, 34.93, D - g0, z)
    y = D - g0 + 0.07
    rail(R, T, y, 29, y, z); rail(R, 35, y, W - T, y, z)
    # lamps: brass posts on the landing corners, big lamps hanging in the void
    for (lx, ly, lz) in ((17.07, 27.93, 8), (46.93, 27.93, 8), (24.07, 22.07, 24), (39.93, 22.07, 24),
                         (29.07, D - g0 + 0.07, 24), (34.93, D - g0 + 0.07, 24), (17, g0 - 0.07, 16), (47, g0 - 0.07, 16),
                         (23, g0 - 0.07, 16), (41, g0 - 0.07, 16)):
        R.parts.add(box(lx - 0.1, ly - 0.1, lz + 1.06, lx + 0.1, ly + 0.1, lz + 1.1, 'brass'))
        R.light(cyl(lx, ly, lz + 1.1, lz + 1.45, 0.11, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    for (hx, hy, hz) in ((12, 30, 11.0), (52, 30, 11.0), (20, 46, 14.0), (44, 46, 14.0), (32, 44, 4.5)):
        if hx == 32:
            hanging(R, hx, hy, z - 0.6, hz, r=0.45, e='e_lamp', segs=12)
        else:
            hanging(R, hx, hy, ceil, hz, r=0.45, e='e_lamp', segs=12)
    R.light(box(31.4, 22.3, 7.35, 32.6, 23.5, 7.4, 'e_candle'))          # a night light under the landing
    # bookcases: the ground walls, the galleries' walls
    wall_cases(R, rows=12, frame='walnut')
    wall_cases(R, z=16, rows=10, frame='walnut', sides='SWE')
    wall_cases(R, z=24, rows=10, frame='walnut', sides='N')
    # walkers
    lo = [R.navpt(x, y) for (x, y) in ((3.5, 3.5), (W - 3.5, 3.5), (W - 3.5, D - 3.5), (3.5, D - 3.5))]
    R.link(*lo, lo[0])
    up = [R.navpt(x, y, 16) for (x, y) in ((3, 3), (W - 3, 3), (W - 3, D - 3), (3, D - 3))]
    R.link(up[3], up[0], up[1], up[2])
    R.spot('probe', 14, 40, 3.0)
    R.meta.update(label='The Great Stair', weight=3,
                  blurb='A staircase built for a procession that never arrived. It climbs, turns, climbs again, and delivers you with great ceremony to more shelves.')
    R.meta['box'] = [[T, 0, T], [W - T, ceil, D - T]]
    return R
