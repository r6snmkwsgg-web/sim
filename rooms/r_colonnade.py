"""The Colonnade: thin stone columns in rows too close together, a forest of them, carrying a lattice of
beams; warm light falls through some of the bays. Bookcases stand between some of the pairs."""
from lib import *
from kit_c import *
import random


def make():
    R = Room('colonnade', 1, 1, res=1024)
    R.sockets(floor='terrazzo', wall='tile')
    H, hc = 5.9, 4.5                      # ceiling; top of the columns
    shell(R, H, floor='terrazzo', ceil='plaster')
    sp = 1.4
    P = [1.0 + sp * k for k in range(11)]
    def door_zone(x, y):
        for (dx, dy) in ((8, 0), (8, C), (0, 8), (C, 8)):
            if dx == 8 and abs(x - 8) < 2.2 and abs(y - dy) < 2.6: return True
            if dy == 8 and abs(y - 8) < 2.2 and abs(x - dx) < 2.6: return True
        return False
    cols = set()
    for x in P:
        for y in P:
            if door_zone(x, y): continue
            cols.add((round(x, 2), round(y, 2)))
            R.parts.add(cyl(x, y, 0.0, hc - 0.14, 0.13, 7, side='tile', caps=False))
            R.parts.add(box(x - 0.19, y - 0.19, hc - 0.14, x + 0.19, y + 0.19, hc, 'tile'))
    # a lattice of beams on the columns, wall to wall
    bh = 0.32
    for p in P:
        R.parts.add(box(T, p - 0.12, hc, C - T, p + 0.12, hc + bh, 'tile'))
        R.parts.add(box(p - 0.12, T, hc, p + 0.12, C - T, hc + bh, 'tile'))
    # light falls through some of the bays
    rnd = random.Random(4)
    for i in range(12):
        for j in range(12):
            x0 = T if i == 0 else P[i - 1] + 0.12
            x1 = C - T if i == 11 else P[i] - 0.12
            y0 = T if j == 0 else P[j - 1] + 0.12
            y1 = C - T if j == 11 else P[j] - 0.12
            if 0 < i < 11 and 0 < j < 11 and rnd.random() < 0.26:
                R.cut(box(x0, y0, H - 0.05, x1, y1, R.hi + 0.5, 'plaster'))
                R.light(box(x0, y0, R.hi - 0.08, x1, y1, R.hi - 0.05, 'e_sky'))
    # bookcases between some pairs of columns (double-faced)
    rnd = random.Random(9)
    placed = 0
    for (x, y) in sorted(cols):
        for (dx, dy) in ((sp, 0), (0, sp)):
            q = (round(x + dx, 2), round(y + dy, 2))
            if q not in cols or rnd.random() > 0.04: continue
            if door_zone(x + dx / 2, y + dy / 2): continue
            L = sp - 0.3
            if dy == 0:
                R.shelf(x + 0.15, y, 0, L, '+y', rows=5, frame='walnut')
                R.shelf(x + 0.15 + L, y, 0, L, '-y', rows=5, frame='walnut', back=False)
            else:
                R.shelf(x, y + 0.15 + L, 0, L, '+x', rows=5, frame='walnut')
                R.shelf(x, y + 0.15, 0, L, '-x', rows=5, frame='walnut', back=False)
            placed += 1
    # a few low lamps for the night, on the floor by the doors
    for (x, y) in ((6.2, 1.2), (C - 6.2, C - 1.2), (1.2, C - 6.2), (C - 1.2, 6.2)):
        R.light(cyl(x, y, 0, 0.3, 0.08, 10, side='e_amber', top='e_amber', bottom='e_amber'))
    # walkers: the aisles
    a, b = P[1] + sp / 2, P[-2] - sp / 2
    ring = navloop(R, ((a, a), (8.0 - sp / 2, a), (b, a), (b, 8.0 - sp / 2), (b, b), (8.0 - sp / 2, b), (a, b), (a, 8.0 - sp / 2)))
    R.spot('probe', 8.0 - sp / 2, 8.0 - sp / 2, 1.8)
    R.meta.update(label='The Colonnade', weight=6,
                  blurb='Columns, and more columns, too close together, like trees planted by someone who had only read about forests. The light comes down between them.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
