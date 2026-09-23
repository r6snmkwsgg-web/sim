"""The Pillar Forest: a hypostyle hall. Slender stone columns on a 3.2 m grid stand on a sunken
marble floor; some columns are square towers of books. Light falls in a checkerboard."""
from lib import *


def make():
    R = Room('pillars', 2, 2, res=2048)
    R.sockets(wall='tile')
    W, H = R.W, 5.4
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, H, 'tile', bottom='floor', top='tile'))
    R.pool(2.4, 2.4, W - 2.4, W - 2.4, 0.4, m='mosaic')
    g = 3.2
    for i in range(1, 10):
        for j in range(1, 10):
            x, y = i * g, j * g
            if i % 2 == 1 and j % 2 == 1:
                R.cut(box(x + 0.35, y + 0.35, H - 0.05, x + g - 0.35, y + g - 0.35, H + 0.45, 'tile'))
                if x + g < W - 1 and y + g < W - 1:
                    R.light(box(x + 0.5, y + 0.5, H + 0.38, x + g - 0.5, y + g - 0.5, H + 0.41, 'e_sky'))
            tower = (i % 3 == 2 and j % 3 == 2)
            z0 = -0.4 if 2.4 < x < W - 2.4 and 2.4 < y < W - 2.4 else 0.0
            if tower:   # a square column clad in books on all four sides
                s = 0.62
                R.parts.add(box(x - s, y - s, z0, x + s, y + s, H, 'wood', skip=('-z', '+z')))
                for (bx, by, f) in ((x - s + 0.02, y + s, '+y'), (x + s, y + s - 0.02, '+x'), (x + s - 0.02, y - s, '-y'), (x - s, y - s + 0.02, '-x')):
                    R.shelf(bx, by, z0 + 0.05, 2 * s - 0.04, f, rows=9, frame='wood', back=False, row_h=0.42, sides=False, crown=False)
            else:
                R.parts.add(cyl(x, y, z0, H, 0.3, 24, side='tile', caps=False))
                R.parts.add(cyl(x, y, H - 0.35, H, 0.4, 24, side='tile', caps=False))     # capital
    for x in (6.4, 16.0, 25.6):
        for (y, a) in ((2.41, 0), (W - 2.41, 0)):
            R.light(box(x - 0.2, y - 0.04, -0.25, x + 0.2, y + 0.04, -0.12, 'e_pool'))
    # books along the outer walls
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        R.shelf(a, T, 0, b - a, '+y', rows=6, frame='paint')
        R.shelf(b, W - T, 0, b - a, '-y', rows=6, frame='paint')
        R.shelf(T, b, 0, b - a, '+x', rows=6, frame='paint')
        R.shelf(W - T, a, 0, b - a, '-x', rows=6, frame='paint')
    pts = {}
    for i in range(5):
        for j in range(5):
            pts[(i, j)] = R.navpt(1.4 + i * (W - 2.8) / 4, 1.4 + j * (W - 2.8) / 4)
    for (i, j), p in pts.items():
        if i < 4 and j in (0, 4): R.link(p, pts[(i + 1, j)])
        if j < 4 and i in (0, 4): R.link(p, pts[(i, j + 1)])
    R.spot('probe', 16, 16, 1.7)
    R.meta['label'] = 'The Pillar Forest'
    R.meta['box'] = [[T, -0.4, T], [W - T, H, W - T]]
    return R
