"""The Hypostyle: a dense forest of square pillars, each one a bookcase on all four faces, under a
low coffered ceiling. Most coffers are dark; a few hold a lamp, so the light lies in scattered pools.
In the middle the pillars stop and a light well opens upward."""
from lib import *
from kit_f import *
import random


def make():
    R = Room('hypostyle', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W, H = R.W, 4.2
    rnd = random.Random(4471)
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    # beams on a 4 m grid (x, y = 2, 6, ... 30); pillars where they cross, from 6 to 26
    lines = [2.0 + 4 * k for k in range(8)]
    c0, c1 = 11.0, 21.0                                       # the light well over the clearing
    R.cut(box(c0, c0, H - 0.02, c1, c1, H + 0.9, 'tile', top='plaster'))
    R.cut(box(c0 + 1.3, c0 + 1.3, H + 0.88, c1 - 1.3, c1 - 1.3, TOP - 0.1, 'plaster'))
    R.light(box(c0 + 1.3, c0 + 1.3, TOP - 0.14, c1 - 1.3, c1 - 1.3, TOP - 0.11, 'e_sky'))
    for i in range(7):
        for j in range(7):
            x0, y0 = lines[i], lines[j]
            if 2 <= i <= 4 and 2 <= j <= 4: continue
            a0x, a0y, a1x, a1y = x0 + 0.5, y0 + 0.5, x0 + 3.5, y0 + 3.5
            R.cut(box(a0x, a0y, H - 0.02, a1x, a1y, H + 0.3, 'tile', top='plaster'))
            R.cut(box(a0x + 0.35, a0y + 0.35, H + 0.28, a1x - 0.35, a1y - 0.35, H + 0.62, 'plaster'))
            if rnd.random() < 0.3 or (i, j) in ((1, 0), (5, 0), (0, 1), (0, 5), (1, 6), (5, 6), (6, 1), (6, 5)):
                R.light(box(a0x + 0.75, a0y + 0.75, H + 0.59, a1x - 0.75, a1y - 0.75, H + 0.61, 'e_panel'))
    # the pillars: books on all four faces up to head height, stone above
    missing = {(10, 22), (26, 14)}
    for x in lines[1:-1]:
        for y in lines[1:-1]:
            if 13 < x < 19 and 13 < y < 19: continue
            if (x, y) in missing:
                R.parts.add(box(x - 0.85, y - 0.85, 0, x + 0.85, y + 0.85, 0.12, 'tile', skip=('-z',)))
            else:
                book_pillar(R, x, y, 0, 0.55, 5, z_top=H, frame='walnut', core='tile', cap='walnut')
            R.parts.add(box(x - 0.8, y - 0.8, H - 0.35, x + 0.8, y + 0.8, H, 'tile', skip=('+z',)))
    # the clearing: a long reading table with green-shaded lamps, benches either side
    cx = cy = W / 2
    R.parts.add(box(cx - 3.0, cy - 0.6, 0.72, cx + 3.0, cy + 0.6, 0.78, 'walnut'))
    for x in (cx - 2.7, cx + 2.7):
        R.parts.add(box(x - 0.08, cy - 0.5, 0, x + 0.08, cy + 0.5, 0.72, 'walnut', skip=('-z',)))
    for y in (cy - 1.25, cy + 1.25):
        R.parts.add(box(cx - 2.8, y - 0.2, 0.42, cx + 2.8, y + 0.2, 0.47, 'walnut'))
        for x in (cx - 2.5, cx + 2.5):
            R.parts.add(box(x - 0.06, y - 0.16, 0, x + 0.06, y + 0.16, 0.42, 'walnut', skip=('-z',)))
        for k in range(4):
            R.spot('sit', cx - 2.1 + k * 1.4, y, 0.47, math.pi / 2 if y < cy else -math.pi / 2)
    for k in range(3):
        x = cx - 2.0 + k * 2.0
        R.nocol.add(cyl(x, cy, 0.78, 1.15, 0.02, 6, side='brass', caps=False))
        R.nocol.add(cyl(x, cy, 1.1, 1.22, 0.2, 12, side='green', top='green', bottom='green'))
        R.light(cyl(x, cy, 1.08, 1.1, 0.17, 12, side='e_candle', top='e_candle', bottom='e_candle'))
    # books along the outer walls
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), rows=6, frame='walnut')
    # night: little amber lamps low on some pillars
    for (x, y) in ((6, 6), (26, 6), (6, 26), (26, 26), (10, 18), (22, 10)):
        R.light(box(x + 0.85, y - 0.12, 2.5, x + 0.89, y + 0.12, 2.7, 'e_amber'))
    # walkers: the perimeter aisle and a cross through the clearing
    loop(R, ((1.6, 1.6), (8, 1.6), (W - 1.6, 1.6), (W - 1.6, 8), (W - 1.6, W - 1.6), (8, W - 1.6), (1.6, W - 1.6), (1.6, 8)))
    a = loop(R, ((8, 8), (24, 8), (24, 24), (8, 24)))
    R.link(a[0], R.navpt(8, 4.0)); R.link(a[2], R.navpt(24, 28.0))
    R.spot('probe', 16, 16, 1.7)
    R.meta.update(label='The Hypostyle', weight=8,
                  blurb='Pillars of books, three metres apart, in every direction you look. Some of the lamps in the ceiling have not been lit for a very long time.')
    R.meta['box'] = [[T, 0, T], [W - T, TOP - 0.1, W - T]]
    return R
