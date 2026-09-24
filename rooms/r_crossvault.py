"""The Nine Bays: a square hall of nine groin-vaulted bays on four piers, each bay a small library of its
own, with book-walls between them and a lamp hanging in every vault."""
from lib import *
from kit_c import *


def make():
    R = Room('crossvault', 1, 1, res=1024)
    R.sockets(floor='mosaic', wall='tile')
    cs = (2.9, 8.0, 13.1)                  # bay centres
    bw, js = 4.3, 3.4                      # vault span and springing height
    for c in cs:
        for axis in ('x', 'y'):
            pr = arch_profile(c, bw, 0, js, 28)
            R.cut(prism(pr, axis, T - 0.02, C - T + 0.02, arch_mats(len(pr), 'mosaic', 'tile')))
    crown = js + bw / 2
    piers = (5.45, 10.55)
    # pier bases and a moulding at the springing
    for x in piers:
        for y in piers:
            R.parts.add(box(x - 0.5, y - 0.5, 0, x + 0.5, y + 0.5, 0.3, 'tile', skip=('-z',)))
            R.parts.add(box(x - 0.52, y - 0.52, js - 0.18, x + 0.52, y + 0.52, js, 'tile'))
    # bookcase partitions between the outer bays, running in from the walls on the pier lines
    Lp, rows = 3.4, 7
    for p in piers:
        # from the south and north walls (faces east and west)
        R.parts.add(box(p - 0.03, T, 0, p + 0.03, T + Lp, rows * 0.42 + 0.17, 'walnut'))
        R.shelf(p + 0.03, T + Lp, 0, Lp, '+x', rows=rows, frame='walnut', back=False)
        R.shelf(p - 0.03, T, 0, Lp, '-x', rows=rows, frame='walnut', back=False)
        R.parts.add(box(p - 0.03, C - T - Lp, 0, p + 0.03, C - T, rows * 0.42 + 0.17, 'walnut'))
        R.shelf(p + 0.03, C - T, 0, Lp, '+x', rows=rows, frame='walnut', back=False)
        R.shelf(p - 0.03, C - T - Lp, 0, Lp, '-x', rows=rows, frame='walnut', back=False)
        # from the west and east walls (face north and south)
        R.parts.add(box(T, p - 0.03, 0, T + Lp, p + 0.03, rows * 0.42 + 0.17, 'walnut'))
        R.shelf(T, p + 0.03, 0, Lp, '+y', rows=rows, frame='walnut', back=False)
        R.shelf(T + Lp, p - 0.03, 0, Lp, '-y', rows=rows, frame='walnut', back=False)
        R.parts.add(box(C - T - Lp, p - 0.03, 0, C - T, p + 0.03, rows * 0.42 + 0.17, 'walnut'))
        R.shelf(C - T - Lp, p + 0.03, 0, Lp, '+y', rows=rows, frame='walnut', back=False)
        R.shelf(C - T, p - 0.03, 0, Lp, '-y', rows=rows, frame='walnut', back=False)
    # the corner bays: cases along both walls
    for (sx, sy) in ((0, 0), (1, 0), (1, 1), (0, 1)):
        a, b = 0.8, 5.0
        if sy == 0: R.shelf(a if sx == 0 else C - b, T, 0, b - a, '+y', rows=rows, frame='oak')
        else: R.shelf(b if sx == 0 else C - a, C - T, 0, b - a, '-y', rows=rows, frame='oak')
        if sx == 0: R.shelf(T, b if sy == 0 else C - a, 0, b - a, '+x', rows=rows, frame='oak')
        else: R.shelf(C - T, a if sy == 0 else C - b, 0, b - a, '-x', rows=rows, frame='oak')
    # the middle bay: a square tower of books
    h = 0.72
    R.parts.add(box(8 - h, 8 - h, 0, 8 + h, 8 + h, 3.1, 'walnut'))
    R.shelf(8 + h, 8 - h, 0, 2 * h, '-y', rows=rows, frame='walnut')
    R.shelf(8 - h, 8 + h, 0, 2 * h, '+y', rows=rows, frame='walnut')
    R.shelf(8 - h, 8 - h, 0, 2 * h, '-x', rows=rows, frame='walnut')
    R.shelf(8 + h, 8 + h, 0, 2 * h, '+x', rows=rows, frame='walnut')
    # a lamp hanging in every bay, and a reading chair in the corner bays
    for x in cs:
        for y in cs:
            hang_lamp(R, x, y, js + 0.2, crown, r=0.17)
    for (x, y, f) in ((2.7, 2.7, math.pi * 1.25), (C - 2.7, 2.7, -math.pi * 0.25), (C - 2.7, C - 2.7, math.pi * 0.25), (2.7, C - 2.7, math.pi * 0.75)):
        armchair(R, x, y, f + math.pi)
    for (x, y) in ((8, T + 0.1), (8, C - T - 0.1), (T + 0.1, 8), (C - T - 0.1, 8)):
        R.light(box(x - 0.12, y - 0.1, 4.35, x + 0.12, y + 0.1, 4.47, 'e_amber'))
    # walkers: the ring round the middle bay, out to every door
    ring = navloop(R, ((6.3, 6.3), (8, 6.3), (9.7, 6.3), (9.7, 8), (9.7, 9.7), (8, 9.7), (6.3, 9.7), (6.3, 8)))
    for k, (x, y) in ((1, (8, 1.4)), (3, (C - 1.4, 8)), (5, (8, C - 1.4)), (7, (1.4, 8))):
        R.link(ring[k], R.navpt(x, y))
    for k, (x, y) in ((0, (4.0, 4.0)), (2, (C - 4.0, 4.0)), (4, (C - 4.0, C - 4.0)), (6, (4.0, C - 4.0))):
        R.link(ring[k], R.navpt(x, y))
    R.spot('probe', 8, 5.45, 1.7)
    R.meta.update(label='The Nine Bays', weight=7,
                  blurb='Nine vaulted bays, each with its lamp and its books, each very like the last. You count them twice and get ten.')
    R.meta['box'] = [[T, 0, T], [C - T, crown, C - T]]
    return R
