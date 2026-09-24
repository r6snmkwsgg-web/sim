"""The Balcony Room: a gallery on columns runs all the way round at the height of the door tops, a
long stair climbs to it, books on both floors, reading tables in the well under a laylight."""
from lib import *
from kit_a import *

H = TOP - 0.1
GZ = 4.4           # gallery floor
GB = 4.13          # its underside (just clears the door arches)
E0, E1 = 2.85, C - 2.85   # the gallery's inner edge
SX0, SX1 = 2.95, 4.35     # the stair (climbing +y along the west side of the well)
N, RISE, RUN = 22, GZ / 22, 0.3
SY1 = 11.8
SY0 = SY1 - N * RUN


def make():
    R = Room('balcony', 1, 1, res=1024)
    shell(R, wall='tile', floor='floor', ceil='plaster', h=H)
    # the gallery slab
    for (x0, y0, x1, y1) in ((T, T, C - T, E0), (T, E1, C - T, C - T), (T, E0, E0, E1), (E1, E0, C - T, E1)):
        R.parts.add(box(x0, y0, GB, x1, y1, GZ, 'floor', bottom='plaster', sides='walnut'))
    R.parts.add(box(SX0 - 0.1, SY1, 0, SX1, E1, GZ, 'tile', top='floor'))   # the stair's landing
    # columns under the edge
    ps = (E0 - 0.25, 5.4, 10.6, E1 + 0.25)
    for p in ps:
        for (x, y) in ((p, E0 - 0.25), (p, E1 + 0.25), (E0 - 0.25, p), (E1 + 0.25, p)):
            R.nocol.add(cyl(x, y, 0.25, GB - 0.25, 0.2, 12, side='tile', caps=False))
            R.col.add(box(x - 0.2, y - 0.2, 0.25, x + 0.2, y + 0.2, GB - 0.25, 'tile'))
            R.parts.add(box(x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, 0.25, 'tile', skip=('-z',)))
            R.parts.add(box(x - 0.32, y - 0.32, GB - 0.25, x + 0.32, y + 0.32, GB, 'tile', skip=('+z',)))
    # balustrade round the gallery edge, open where the stair lands
    rail(R, E0, E0 + 0.1, E1, E0 + 0.1, GZ, h=1.0, solid=True)
    rail(R, E1 - 0.1, E0, E1 - 0.1, E1, GZ, h=1.0, solid=True)
    rail(R, SX1, E1 - 0.1, E1, E1 - 0.1, GZ, h=1.0, solid=True)
    rail(R, E0 - 0.1, E0, E0 - 0.1, SY1, GZ, h=1.0, solid=True)
    rail(R, SX1 - 0.1, SY1, SX1 - 0.1, E1 - 0.1, GZ, h=1.0, solid=True)
    # the stair: a solid stone string on the gallery side, a brass rail on the well side
    R.flight(SX0, SY0, 0, SX1 - SX0, N, RISE, RUN, '+y', m='floor', riser='walnut', side='tile')
    stair_side(R, SX0 - 0.02, SY0, SX0 - 0.02, SY1, 1.0, GZ + 1.0)
    stair_rail(R, SX1 - 0.05, SY0 + RUN, RISE, SX1 - 0.05, SY1, GZ)
    # books below and above
    for (a, b) in ((0.8, 6.2), (9.8, C - 0.8)):
        for (z, rows) in ((0.0, 8), (GZ, 6)):
            sh(R, '+y', T, a, b, z, rows=rows, frame='walnut')
            sh(R, '-y', C - T, a, b, z, rows=rows, frame='walnut')
            sh(R, '+x', T, a, b, z, rows=rows, frame='walnut')
            sh(R, '-x', C - T, a, b, z, rows=rows, frame='walnut')
    for (a, b) in ((6.4, 9.6),):   # upstairs there are no doors, so the cases run on over them
        for f, w in (('+y', T), ('-y', C - T), ('+x', T), ('-x', C - T)):
            sh(R, f, w, a, b, GZ, rows=6, frame='walnut')
    # the well: two long tables with green lamps
    for x in (6.3, 9.7):
        R.parts.add(table(x - 0.55, 4.6, x + 0.55, 11.4, 0.78, 'walnut', top='leather'))
        for y in (5.4, 7.2, 8.8, 10.6):
            desk_lamp(R, x, y, 0.78)
            for s in (-1, 1):
                R.nocol.add(chair(x + s * 0.95, y, math.pi if s > 0 else 0.0))
                R.col.add(box(x + s * 0.95 - 0.26, y - 0.25, 0, x + s * 0.95 + 0.26, y + 0.25, 0.5, 'tile'))
        R.spot('sit', x + 0.95, 7.2, 0.48, math.pi)
    # lamps under the gallery, and a laylight over the well
    lamps = [(p, q) for p in (4.6, 11.4) for q in (1.6, C - 1.6)] + [(q, p) for p in (4.6, 11.4) for q in (1.6, C - 1.6)] + [(1.6, 1.6), (C - 1.6, 1.6), (1.6, C - 1.6), (C - 1.6, C - 1.6)]
    for p in (0,):
        for (x, y) in lamps:
            R.light(sphere(x, y, GB - 0.25, 0.13, 8, 4, 'e_lamp'))
            R.nocol.add(cyl(x, y, GB - 0.15, GB, 0.012, 6, side='brass', caps=False))
    R.cut(box(E0 + 0.6, E0 + 0.6, H - 0.05, E1 - 0.6, E1 - 0.6, H + 0.02, 'plaster'))
    R.light(box(E0 + 0.6, E0 + 0.6, H, E1 - 0.6, E1 - 0.6, H + 0.01, 'e_sky'))
    for k in range(6):
        p = E0 + 0.6 + k * (E1 - E0 - 1.2) / 5
        R.nocol.add(box(p - 0.05, E0 + 0.6, H - 0.12, p + 0.05, E1 - 0.6, H, 'iron'))
        R.nocol.add(box(E0 + 0.6, p - 0.05, H - 0.12, E1 - 0.6, p + 0.05, H, 'iron'))
    # night: amber lamps on the balustrade corners
    for (x, y) in ((E0 + 0.1, E0 + 0.1), (E1 - 0.1, E0 + 0.1), (E1 - 0.1, E1 - 0.1)):
        R.parts.add(cyl(x, y, GZ + 1.06, GZ + 1.12, 0.1, 10, side='brass', top='brass'))
        R.light(sphere(x, y, GZ + 1.24, 0.12, 8, 4, 'e_amber'))
    navloop(R, [(1.6, 1.6), (8, 1.6), (C - 1.6, 1.6), (C - 1.6, 8), (C - 1.6, C - 1.6), (8, C - 1.6), (1.6, C - 1.6), (1.6, 8)])
    mid = navloop(R, [(5.0, 3.8), (11.0, 3.8), (11.0, 12.2), (5.0, 12.2)])
    R.link(1, mid[0]); R.link(5, mid[3]); R.link(3, mid[1])
    up = navloop(R, [(1.5, 1.5), (8, 1.5), (C - 1.5, 1.5), (C - 1.5, 8), (C - 1.5, C - 1.5), (8, C - 1.5), (1.5, C - 1.5), (1.5, 8)], z=GZ)
    R.spot('probe', 8, 8, 2.2)
    R.meta.update(label='The Balcony Room', weight=7,
                  blurb='A gallery runs all the way round, just above the doors. From up there the tables below look like a diagram of themselves.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
