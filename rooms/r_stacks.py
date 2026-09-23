"""The Sunken Stacks: rows of bookcases standing in a floor sunk two steps deep, under a grid of
skylights; oxblood walls, a walkway of parquet round the edge."""
from lib import *


def make():
    R = Room('stacks', 2, 1, res=2048)
    R.sockets(wall='pink')
    W, D, H = R.W, R.D, 6.4
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'pink', bottom='terrazzo', top='plaster'))
    # coffered skylights on a 4 m grid
    for x in range(4, int(W), 4):
        for y in (4, 8, 12):
            R.cut(box(x - 0.95, y - 0.95, H - 0.05, x + 0.95, y + 0.95, H + 0.5, 'plaster'))
            R.light(box(x - 0.8, y - 0.8, H + 0.44, x + 0.8, y + 0.8, H + 0.47, 'e_sky'))
    # the sunken floor: everything but a walkway round the walls
    px0, py0, px1, py1, depth = 2.3, 2.3, W - 2.3, D - 2.3, 0.5
    R.pool(px0, py0, px1, py1, depth, m='mosaic')
    for x in (4.0, 12.0, 20.0, 28.0):
        for (y, a) in ((py0 + 0.01, 0), (py1 - 0.01, 0)):
            R.light(box(x - 0.2, y - 0.04, -0.25, x + 0.2, y + 0.04, -0.12, 'e_pool'))
    # the stacks: double-sided bookcases on the sunken floor, a cross-aisle down the middle
    zb = -depth
    for x in (5.2, 8.6, 12.0, 15.4, 18.8, 22.2, 25.6):
        for (a, b) in ((3.4, 7.05), (8.95, D - 3.4)):
            R.shelf(x + 0.01, b, zb, b - a, '+x', rows=8, frame='wood', back=True)
            R.shelf(x - 0.01, a, zb, b - a, '-x', rows=8, frame='wood', back=True)
    # a few reading tables on the walkway
    for (x, y) in ((6.0, 1.3), (26.0, 1.3), (6.0, D - 1.3), (26.0, D - 1.3)):
        R.parts.add(box(x - 0.9, y - 0.4, 0.72, x + 0.9, y + 0.4, 0.78, 'wood'))
        for (dx, dy) in ((-0.8, -0.3), (0.8, -0.3), (-0.8, 0.3), (0.8, 0.3)):
            R.parts.add(box(x + dx - 0.03, y + dy - 0.03, 0, x + dx + 0.03, y + dy + 0.03, 0.72, 'wood', skip=('-z',)))
    # walkers: the walkway round the edge, and the sunken cross-aisle
    ring = [R.navpt(x, y) for (x, y) in ((1.3, 1.3), (8, 1.3), (16, 1.3), (24, 1.3), (W - 1.3, 1.3), (W - 1.3, 8), (W - 1.3, D - 1.3),
                                         (24, D - 1.3), (16, D - 1.3), (8, D - 1.3), (1.3, D - 1.3), (1.3, 8))]
    R.link(*ring, ring[0])
    mid = [R.navpt(x, 8) for x in (3.5, 10.3, 17.1, 23.9, W - 3.5)]
    R.link(ring[11], *mid, ring[5])
    R.spot('probe', 16, 8, 1.7)
    R.meta['label'] = 'The Sunken Stacks'
    R.meta['box'] = [[T, -0.5, T], [W - T, H, D - T]]
    return R
