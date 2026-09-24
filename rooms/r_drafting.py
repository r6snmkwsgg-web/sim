"""The Drafting Room: rows of tilted drafting tables, every one with its stool and its lamp on an
arm, every one with the same unfinished plan pinned to it. High windows all round, plan chests
under them, and bookcases between the doors."""
from lib import *
from kit_d import *


def drafting_table(R, x0, yc):
    """A drafting table facing +x: the board rises away from the stool at x0 - 0.5."""
    d, w = 0.8, 1.1
    y0, y1 = yc - w / 2, yc + w / 2
    R.parts.add(slope_box(x0, x0 + d, y0, y1, 0.84, 1.12, 0.88, 1.16, 'oak'))
    R.parts.add(slope_box(x0 + 0.08, x0 + d - 0.12, y0 + 0.12, y1 - 0.22, 0.885, 1.13, 0.892, 1.137, 'ivory'))
    for yy in (y0 + 0.06, y1 - 0.12):
        R.parts.add(box(x0 + 0.1, yy, 0, x0 + d - 0.1, yy + 0.06, 0.84, 'walnut', skip=('-z',)))
    R.parts.add(box(x0 + 0.35, y0 + 0.12, 0.2, x0 + 0.45, y1 - 0.12, 0.28, 'walnut', skip=('-y', '+y')))
    # the lamp on its arm: a post at the back corner, an arm over the board, a shade
    px, py = x0 + d + 0.05, y1 - 0.05
    R.parts.add(box(px - 0.02, py - 0.02, 0, px + 0.02, py + 0.02, 1.75, 'iron', skip=('-z',)))
    lx, ly = x0 + 0.45, yc + 0.1
    g = Geo(); P = [(px, py - 0.015, 1.72), (lx, ly - 0.015, 1.58), (lx, ly + 0.015, 1.58), (px, py + 0.015, 1.72)]
    P += [(p[0], p[1], p[2] + 0.03) for p in P]
    ids = [g.vert(p) for p in P]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        g.face([ids[i] for i in f], 'iron', [(0, 0)] * 4)
    R.nocol.add(g.fix())
    R.nocol.add(cyl(lx, ly, 1.46, 1.6, 0.13, 8, side='green', top='green', caps=False))
    R.light(box(lx - 0.08, ly - 0.08, 1.49, lx + 0.08, ly + 0.08, 1.5, 'e_lamp', skip=('+z', '-x', '+x', '-y', '+y')))
    # the stool
    sx = x0 - 0.45
    R.parts.add(box(sx - 0.03, yc - 0.03, 0, sx + 0.03, yc + 0.03, 0.66, 'iron', skip=('-z', '+z')))
    R.parts.add(cyl(sx, yc, 0.66, 0.72, 0.19, 10, side='leather', top='leather', bottom='leather'))
    R.parts.add(cyl(sx, yc, 0.0, 0.03, 0.22, 10, side='iron', top='iron', caps=True))
    R.spot('sit', sx, yc, 0.72, 0.0)


def make():
    R = Room('drafting', 1, 1, res=1024)
    shell(R, TOP, floor='floor', wall='plaster', top='plaster')
    # clerestory: tall windows high up in every wall
    zw0, zw1 = 5.2, 6.9
    for p in (2.0, 4.0, 6.0, 10.0, 12.0, 14.0):
        for side in 'SNWE':
            if side == 'S':   x0, y0, x1, y1, e = p - 0.5, 0.05, p + 0.5, I0 + 0.02, (p - 0.45, 0.07, p + 0.45, 0.08)
            elif side == 'N': x0, y0, x1, y1, e = p - 0.5, I1 - 0.02, p + 0.5, C - 0.05, (p - 0.45, C - 0.08, p + 0.45, C - 0.07)
            elif side == 'W': x0, y0, x1, y1, e = 0.05, p - 0.5, I0 + 0.02, p + 0.5, (0.07, p - 0.45, 0.08, p + 0.45)
            else:             x0, y0, x1, y1, e = I1 - 0.02, p - 0.5, C - 0.05, p + 0.5, (C - 0.08, p - 0.45, C - 0.07, p + 0.45)
            R.cut(box(x0, y0, zw0, x1, y1, zw1, 'plaster', bottom='tile'))
            R.light(box(e[0], e[1], zw0 + 0.05, e[2], e[3], zw1 - 0.05, 'e_sky'))
    # a cornice under the windows
    for (x0, y0, x1, y1) in ((I0, I0, I1, I0 + 0.12), (I0, I1 - 0.12, I1, I1), (I0, I0, I0 + 0.12, I1), (I1 - 0.12, I0, I1, I1)):
        R.parts.add(box(x0, y0, zw0 - 0.25, x1, y1, zw0 - 0.1, 'tile'))
    # rows of drafting tables, all facing east
    for x0 in (2.4, 4.4, 10.2, 12.2):
        for yc in (2.4, 4.15, 5.9, 10.1, 11.85, 13.6):
            drafting_table(R, x0, yc)
    # plan chests under the west and east windows
    for (a, b) in ((0.8, 6.2), (9.8, 15.2)):
        for (xa, xb, fx) in ((I0, I0 + 0.9, I0 + 0.9), (I1 - 0.9, I1, I1 - 0.9)):
            R.parts.add(box(xa, a, 0, xb, b, 1.0, 'walnut', top='oak'))
            s = 1 if fx < 8 else -1
            for k in range(5):
                z = 0.14 + k * 0.18
                R.nocol.add(box(min(fx, fx + s * 0.02), a + 0.1, z, max(fx, fx + s * 0.02), b - 0.1, z + 0.015, 'brass', skip=('-z',)))
            # rolled plans lying on top
            for k in range(3):
                yy = a + 0.8 + k * 1.7
                xm = (xa + xb) / 2 + (k % 2) * 0.15
                R.nocol.add(box(xm - 0.05, yy - 0.4, 1.0, xm + 0.05, yy + 0.4, 1.09, 'ivory', skip=('-z',)))
    # bookcases between the doors on the north and south walls
    for (a, b) in ((0.8, 6.2), (9.8, 15.2)):
        wall_shelf(R, '+y', a, b, 0, rows=9, frame='oak')
        wall_shelf(R, '-y', a, b, 0, rows=9, frame='oak')
    # a few pendant lamps down the centre aisle
    for y in (4.0, 8.0, 12.0):
        pendant(R, 8, y, 3.2, r=0.22)
    loop(R, [(1.6, 1.6), (8, 1.6), (14.4, 1.6), (14.4, 8), (14.4, 14.4), (8, 14.4), (1.6, 14.4), (1.6, 8)])
    R.link(R.navpt(8, 1.6), R.navpt(8, 8), R.navpt(8, 14.4))
    R.link(R.navpt(1.6, 8), R.navpt(8, 8), R.navpt(14.4, 8))
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Drafting Room', weight=5,
                  blurb='Every table has the same plan pinned to it, a building with no doors, and every one is exactly as unfinished as the last.')
    return R
