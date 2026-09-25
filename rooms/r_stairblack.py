"""The Black Stair: from a lamplit gallery a stair eight metres wide goes down, and down: past a landing
between two great piers, onto a dark floor, and on into a pit whose bottom only one weak bulb has ever
seen. No lamp is lit below halfway. Halfway down, in the east pier, a door stands ajar with candlelight
behind it."""
from kit_h8 import *

W = D = 32.0
X0, X1 = 12.0, 20.0             # the stair's width
N, RISE, RUN = 20, 0.2, 0.3
PX0, PX1, PY1 = 10.4, 21.6, 8.0  # the pit
ZB = -4.0                        # the pit floor
PIER_Y0, PIER_Y1 = 14.8, 18.2
LZ = 4.0                         # the landing, halfway down
DY0, DY1 = 16.0, 17.0            # the landing door in the east pier
TOPV = 15.2


def make():
    R = Room('stairblack', 2, 2, levels=2, res=2048, lo=-6.0)
    skip = [('S', 0, 1), ('S', 1, 1), ('W', 0, 1), ('E', 0, 1)]
    seal(R, skip, floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOPV, 'tile', bottom='slate', top='plaster'))
    R.cut(box(PX0, T - 0.02, ZB, PX1, PY1, 0.3, 'tile', bottom='slate', top='tile'))
    upper(R)
    stair(R)
    piers(R)
    books(R)
    lights(R)
    secret_room(R)
    # walkers: round the deck, down the stair, round the dark floor
    d = navloop(R, [(6, 27), (16, 27), (26, 27), (26, 30), (6, 30)], z=8.0)
    a, b, c, e = R.navpt(16, 16.8, LZ), R.navpt(16, 8.9, 0), R.navpt(16, 1.2, ZB), R.navpt(16, 25.0, 8.0)
    R.link(d[1], e, a, b, c)
    g = navloop(R, [(3, 8.9), (3, 29), (29, 29), (29, 8.9)])
    R.link(g[0], b, g[3])
    fx(R, 'fog', [T, T, ZB, W - T, D - T, 2.5], density=0.07)
    fx(R, 'dust', [X0, 18, 7.5, X1, 31, 12])
    secret(R, 21.8, 16.5, LZ, 'The Landing Door',
           'Halfway down, where the lamps give up, a door in the pier was open all along. Someone sits up here with a candle so as not to have to go any further.')
    return finish(R, 'The Black Stair', weight=3, probe=(16, 20, 10.0), top=TOPV, bot=ZB,
                  blurb='A grand stair goes down from the lamps into a dark the lamps do not reach. The handrail is warm at the top, and colder with every step.')


def upper(R):
    """The lamplit top: a deck along the north wall and two galleries running down the side walls."""
    R.parts.add(box(T - 0.02, 24.0, 7.55, W - T + 0.02, D - T + 0.02, 8.0, 'tile', top='terrazzo', bottom='plaster'))
    for (x0, x1) in ((T - 0.02, 4.35), (W - 4.35, W - T + 0.02)):
        R.parts.add(box(x0, 14.0, 7.55, x1, 24.0, 8.0, 'tile', top='terrazzo', bottom='plaster'))
    y = 24.07
    stone_rail(R, 4.28, y, X0, y, 8.0); stone_rail(R, X1, y, W - 4.28, y, 8.0)
    stone_rail(R, 4.28, 14.0, 4.28, y, 8.0); stone_rail(R, W - 4.28, 14.0, W - 4.28, y, 8.0)
    stone_rail(R, T, 14.07, 4.35, 14.07, 8.0); stone_rail(R, W - 4.35, 14.07, W - T, 14.07, 8.0)
    # corbels under the galleries
    for yy in (15.0, 18.0, 21.0):
        for (x0, x1) in ((T, 1.2), (W - 1.2, W - T)):
            R.parts.add(box(x0, yy - 0.3, 5.8, x1, yy + 0.3, 7.55, 'tile'))


def stair(R):
    for (y0, z0) in ((18.0, LZ), (9.6, 0.0), (2.0, ZB)):
        rflight(R, X0, y0, z0, X1 - X0, N, RISE, RUN, '+y', m='terrazzo', side='tile')
        flight_rail(R, X0, y0, z0, X1 - X0, N, RISE, RUN, '+y', which=(0, 1), m='tile', cap='brass', h=1.0)
    R.parts.add(box(X0, 15.6, LZ - 0.45, X1, 18.02, LZ, 'tile', top='terrazzo', bottom='plaster'))
    # the pit's rim
    stone_rail(R, PX0 - 0.07, T, PX0 - 0.07, PY1 + 0.14, 0.0)
    stone_rail(R, PX1 + 0.07, T, PX1 + 0.07, PY1 + 0.14, 0.0)
    stone_rail(R, PX0 - 0.14, PY1 + 0.07, X0, PY1 + 0.07, 0.0)
    stone_rail(R, X1, PY1 + 0.07, PX1 + 0.14, PY1 + 0.07, 0.0)
    # newels with brass balls at the top and at the landing
    for x in (X0 + 0.07, X1 - 0.07):
        R.parts.add(box(x - 0.22, 23.7, 7.9, x + 0.22, 24.2, 9.25, 'tile'))
        R.nocol.add(sphere(x, 23.95, 9.4, 0.14, 10, 5, 'brass'))


def piers(R):
    """Two great square piers stand either side of the landing. The east one is hollow."""
    x0, x1 = 8.4, X0
    R.parts.add(box(x0, PIER_Y0, 0, x1, PIER_Y1, 9.4, 'tile', skip=('-z',)))
    ex0, ex1 = X1, 23.6
    R.parts.add(box(ex0, PIER_Y0, 0, ex1, PIER_Y1, LZ, 'tile', top='oak', skip=('-z',)))
    t = 0.3
    R.parts.add(box(ex1 - t, PIER_Y0, LZ, ex1, PIER_Y1, 9.4, 'tile'))
    R.parts.add(box(ex0, PIER_Y0, LZ, ex1 - t, PIER_Y0 + t, 9.4, 'tile'))
    R.parts.add(box(ex0, PIER_Y1 - t, LZ, ex1 - t, PIER_Y1, 9.4, 'tile'))
    R.parts.add(box(ex0, PIER_Y0 + t, LZ, ex0 + t, DY0, 9.4, 'tile'))
    R.parts.add(box(ex0, DY1, LZ, ex0 + t, PIER_Y1 - t, 9.4, 'tile'))
    R.parts.add(box(ex0, DY0, LZ + 2.2, ex0 + t, DY1, 9.4, 'tile'))
    R.parts.add(box(ex0 + t, PIER_Y0 + t, 6.95, ex1 - t, PIER_Y1 - t, 9.4, 'tile', bottom='plaster'))
    for (a, b) in ((x0, x1), (ex0, ex1)):
        R.parts.add(box(a - 0.15, PIER_Y0 - 0.15, 9.4, b + 0.15, PIER_Y1 + 0.15, 9.7, 'tile'))
        R.parts.add(box(a - 0.1, PIER_Y0 - 0.1, 0, b + 0.1, PIER_Y1 + 0.1, 0.4, 'tile', skip=('-z',)))


def books(R):
    rows = 12
    wall_cases(R, z=0.0, rows=rows, frame='walnut', sides='NWE')
    for (a, b) in ((0.6, 6.2), (25.8, W - 0.6)):
        R.shelf(a, T, 0.0, b - a, '+y', rows=rows, frame='walnut')
    # the pit is lined with books all the way down
    sh(R, '+y', T, PX0 + 0.1, PX1 - 0.1, z=ZB, rows=9, frame='walnut')
    sh(R, '+x', PX0, T + 0.4, PY1 - 0.1, z=ZB, rows=9, frame='walnut')
    sh(R, '-x', PX1, T + 0.4, PY1 - 0.1, z=ZB, rows=9, frame='walnut')
    # the upper floor: the north wall and the galleries
    for (a, b) in ((0.6, 6.2), (9.8, 22.2), (25.8, W - 0.6)):
        R.shelf(b, D - T, 8.0, b - a, '-y', rows=13, frame='walnut')
    for (a, b) in ((14.3, 22.2), (25.8, D - 0.6)):
        R.shelf(T, b, 8.0, b - a, '+x', rows=13, frame='walnut')
        R.shelf(W - T, a, 8.0, b - a, '-x', rows=13, frame='walnut')
    # the piers: books on the faces toward the landing and toward the dark
    sh(R, '-x', 8.4, PIER_Y0 + 0.2, PIER_Y1 - 0.2, z=0.0, rows=11, frame='walnut')
    sh(R, '+x', X0, PIER_Y0 + 0.2, PIER_Y1 - 0.2, z=LZ, rows=8, frame='walnut')
    sh(R, '+x', 23.6, PIER_Y0 + 0.2, PIER_Y1 - 0.2, z=0.0, rows=11, frame='walnut')
    sh(R, '-x', X1, PIER_Y0 + 0.35, DY0 - 0.2, z=LZ, rows=8, frame='walnut')
    sh(R, '-x', X1, DY1 + 0.2, PIER_Y1 - 0.2, z=LZ, rows=8, frame='walnut')
    for (a, b) in ((8.4, X0), (X1, 23.6)):
        sh(R, '-y', PIER_Y0, a + 0.2, b - 0.2, z=0.0, rows=8, frame='walnut')


def lights(R):
    """Bright at the top; dimmer at the landing; below halfway, nothing but one weak bulb at the bottom."""
    for x in (X0 + 0.07, X1 - 0.07):
        green_standard(R, x, 23.95, 9.53, h=0.75)
    for k in range(6):
        x = 5.6 + k * 4.16
        if X0 - 1 < x < X1 + 1: continue
        green_standard(R, x, 24.07, 9.06, h=0.6)
    for yy in (16.0, 20.0):
        green_standard(R, 4.28, yy, 9.06, h=0.6)
        green_standard(R, W - 4.28, yy, 9.06, h=0.6)
    for (x, y) in ((8, 28), (16, 28), (24, 28)):
        pendant(R, x, y, 11.5, TOPV, r=0.3)
    for (x, y) in ((4, 17), (W - 4, 17), (4, 21), (W - 4, 21)):
        pass
    # the landing: two dim lamps on the piers' caps and sconces facing the stair
    for x in ((8.4 + X0) / 2, (X1 + 23.6) / 2):
        green_standard(R, x, (PIER_Y0 + PIER_Y1) / 2, 9.7, h=0.8, m='e_dim')
    for (x, f) in ((X0 + 0.05, 0.0), (X1 - 0.05, math.pi)):
        R.nocol.add(box(x - 0.05, 15.05, 6.2, x + 0.05, 15.35, 6.6, 'brass'))
        R.light(sphere(x + 0.2 * math.cos(f), 15.2, 6.7, 0.08, 8, 4, 'e_dim'))
    # the bottom of the pit: a weak bulb over a chair nobody sits in
    bulb(R, 16.0, 1.3, ZB + 2.6, r=0.07, m='e_dim', top=0.0)
    chair(R, 16.0, 0.9, math.pi / 2, z=ZB)
    # green exit signs over the ground-floor doors, and a few night lights low on the dark walls
    for (sd, c) in (('N', 8), ('N', 24), ('S', 8), ('S', 24), ('W', 8), ('W', 24), ('E', 8), ('E', 24)):
        if sd in 'NS':
            y = T + 0.05 if sd == 'S' else D - T - 0.05
            R.light(box(c - 0.3, y - 0.04, 4.35, c + 0.3, y + 0.04, 4.55, 'e_exit'))
        else:
            x = T + 0.05 if sd == 'W' else W - T - 0.05
            R.light(box(x - 0.04, c - 0.3, 4.35, x + 0.04, c + 0.3, 4.55, 'e_exit'))


def secret_room(R):
    """Inside the east pier, at the landing: a cell 3 m square with a candle, a chair, a cot and books."""
    x0, x1, y0, y1 = X1 + 0.3, 23.3, PIER_Y0 + 0.3, PIER_Y1 - 0.3
    z = LZ
    # the door, standing ajar into the cell
    door = box(0, 0, 0, 0.04, DY1 - DY0 - 0.04, 2.15, 'walnut')
    door.add(box(0.04, 0.1, 0.2, 0.06, DY1 - DY0 - 0.14, 1.0, 'wood'))
    door.add(box(0.04, 0.1, 1.15, 0.06, DY1 - DY0 - 0.14, 2.0, 'wood'))
    door.xform(-1.2, 0, 0, 0); door.xform(0, X1 + 0.32, DY0 + 0.02, z)
    R.nocol.add(door)
    R.nocol.add(box(X1 - 0.08, DY0 - 0.1, z + 2.2, X1, DY1 + 0.1, z + 2.35, 'walnut'))
    # candlelight under and round it
    table(R, 22.2, y1 - 0.8, x1 - 0.05, y1 - 0.05, z=z, h=0.74, top='leather')
    candle(R, 22.5, y1 - 0.3, z + 0.74, h=0.18)
    candle(R, 22.8, y1 - 0.5, z + 0.74, h=0.12)
    open_book(R, 22.7, y1 - 0.45, z + 0.74, 0.4)
    chair(R, 21.7, y1 - 0.45, 0.0, z=z)
    R.parts.add(box(x0 + 0.05, y0 + 0.05, z, x0 + 2.0, y0 + 0.85, z + 0.4, 'bed'))
    R.parts.add(box(x0 + 0.05, y0 + 0.05, z + 0.4, x0 + 0.45, y0 + 0.85, z + 0.52, 'ivory'))
    R.spot('bed', x0 + 1.1, y0 + 0.45, z + 0.4, 0.0)
    sh(R, '-x', x1, y0 + 0.9, y1 - 0.9, z=z, rows=6, frame='walnut', depth=0.28)
    sh(R, '+y', y0, x0 + 2.1, x1 - 0.05, z=z, rows=6, frame='walnut', depth=0.28)
    bulb(R, 21.8, 16.6, z + 2.3, r=0.06, m='e_candle', top=6.95)
    R.spot('plaque', x1 - 0.05, y1 - 0.9, z + 1.6, math.pi, text='I have been down. There is a chair.')
