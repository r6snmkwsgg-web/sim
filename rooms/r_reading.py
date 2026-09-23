"""The Reading Room: the one warm room. Oak bookcases to the cornice on every wall, long tables with
green-shaded lamps, a coffered plaster ceiling and a chandelier of small lights."""
from lib import *


def make():
    R = Room('reading', 1, 1, res=1024)
    R.sockets(floor='terrazzo', wall='plaster')
    H = 4.8
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, H, 'plaster', bottom='terrazzo', top='plaster'))
    # coffers: a 3 x 3 grid, the middle one deeper, with the chandelier under it
    for i in range(3):
        for j in range(3):
            x, y = 3.2 + i * 4.8, 3.2 + j * 4.8
            R.cut(box(x - 1.9, y - 1.9, H - 0.05, x + 1.9, y + 1.9, H + (0.7 if i == j == 1 else 0.3), 'plaster'))
    for k in range(10):
        a = k * math.pi / 5
        R.light(sphere(8 + math.cos(a) * 0.9, 8 + math.sin(a) * 0.9, H - 0.9 + 0.12 * math.sin(3 * a), 0.07, 12, 6, 'e_lamp'))
    R.light(sphere(8, 8, H - 0.75, 0.12, 14, 7, 'e_lamp'))
    R.parts.add(cyl(8, 8, H - 0.8, H + 0.6, 0.02, 8, side='brass', caps=False))
    # bookcases on every wall, floor to cornice, either side of the doors
    for (a, b) in ((0.6, 6.2), (9.8, C - 0.6)):
        R.shelf(a, T, 0, b - a, '+y', rows=9, frame='oak')
        R.shelf(b, C - T, 0, b - a, '-y', rows=9, frame='oak')
        R.shelf(T, b, 0, b - a, '+x', rows=9, frame='oak')
        R.shelf(C - T, a, 0, b - a, '-x', rows=9, frame='oak')
    # two long tables, lamps with green shades
    for ty in (5.3, 10.7):
        R.parts.add(box(3.4, ty - 0.55, 0.74, 12.6, ty + 0.55, 0.8, 'wood'))
        for x in (3.6, 12.4):
            for dy in (-0.45, 0.45):
                R.parts.add(box(x - 0.05, ty + dy - 0.05, 0, x + 0.05, ty + dy + 0.05, 0.74, 'wood', skip=('-z',)))
        for x in (5.0, 8.0, 11.0):
            R.parts.add(cyl(x, ty, 0.8, 1.15, 0.018, 8, side='brass', caps=False))
            R.parts.add(cyl(x, ty, 1.15, 1.26, 0.2, 16, side='mint', top='mint', bottom='mint'))
            R.light(cyl(x, ty, 1.1, 1.15, 0.15, 16, side='e_lamp', top='e_lamp', bottom='e_lamp'))
        for x in (4.5, 6.5, 9.5, 11.5):
            for s in (-1, 1):
                cy = ty + s * 1.0
                R.parts.add(box(x - 0.22, cy - 0.22, 0.44, x + 0.22, cy + 0.22, 0.49, 'wood'))
                R.parts.add(box(x - 0.22, cy + s * 0.18 - 0.03, 0.49, x + 0.22, cy + s * 0.18 + 0.03, 0.95, 'wood'))
                R.spot('sit', x, cy, 0.46, -s * math.pi / 2)
    # a brass ladder leaning on the east wall's shelves
    R.parts.add(box(C - T - 0.55, 12.1, 0, C - T - 0.5, 12.15, 3.9, 'brass'))
    R.parts.add(box(C - T - 0.55, 12.75, 0, C - T - 0.5, 12.8, 3.9, 'brass'))
    for k in range(12):
        R.parts.add(box(C - T - 0.56, 12.12, 0.3 + k * 0.3, C - T - 0.49, 12.78, 0.33 + k * 0.3, 'brass'))
    pts = [R.navpt(x, y) for (x, y) in ((2.2, 2.2), (8, 2.2), (C - 2.2, 2.2), (C - 2.2, 8), (C - 2.2, C - 2.2), (8, C - 2.2), (2.2, C - 2.2), (2.2, 8))]
    R.link(*pts, pts[0])
    R.spot('probe', 8, 8, 1.7)
    R.meta['label'] = 'The Reading Room'
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
