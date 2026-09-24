"""The Lamp Forest: a dark room grown over with standing lamps in green shades, some as tall as
trees, each making its own small pool of light; low bookcases stand about among them like undergrowth."""
from lib import *
from kit_a import *
import random

H = TOP - 0.1
DOORS = ((8, T), (8, C - T), (T, 8), (C - T, 8))


def clear_of_doors(x, y, d=2.7):
    return all(math.hypot(x - dx, y - dy) > d for dx, dy in DOORS)


def make():
    R = Room('lampforest', 1, 1, res=1024)
    shell(R, wall='damask', floor='walnut', ceil='green', h=H)
    rnd = random.Random(5)
    # low bookcases scattered at odd angles: the undergrowth
    cases = [(4.2, 4.6, 0.5, 2.2), (11.4, 3.9, -0.3, 2.0), (12.2, 11.6, 1.1, 2.4), (4.6, 11.8, -0.9, 2.0),
             (8.7, 5.3, 1.35, 1.6), (6.6, 9.3, 0.1, 1.6), (10.5, 8.6, -1.2, 1.4), (2.3, 6.6, 1.5, 1.2), (13.6, 5.9, 0.2, 1.3)]
    occupied = []
    for (x, y, a, L) in cases:
        rows = rnd.choice((2, 3))
        ang_shelf(R, x + math.cos(a) * 0.01, y + math.sin(a) * 0.01, a, L, rows=rows, frame='walnut', depth=0.3)
        ang_shelf(R, x - math.cos(a) * 0.01, y - math.sin(a) * 0.01, a + math.pi, L, rows=rows, frame='walnut', depth=0.3)
        occupied.append((x, y, L / 2 + 0.5))
    # the lamps: a jittered grid, trunks of every height
    lamps = []
    for i in range(7):
        for j in range(7):
            x = 1.4 + i * 2.2 + rnd.uniform(-0.75, 0.75)
            y = 1.4 + j * 2.2 + rnd.uniform(-0.75, 0.75)
            x = min(max(x, 0.9), C - 0.9); y = min(max(y, 0.9), C - 0.9)
            if not clear_of_doors(x, y): continue
            if any(math.hypot(x - ox, y - oy) < r for ox, oy, r in occupied): continue
            if any(math.hypot(x - lx, y - ly) < 1.3 for lx, ly, _ in lamps): continue
            h = rnd.choice((1.55, 1.7, 1.9, 2.3, 2.8, 3.4, 4.2, 5.0, 5.9, 6.6))
            lamps.append((x, y, h))
    for (x, y, h) in lamps:
        s = 0.8 + 0.5 * (h - 1.5) / 5.1
        r = rnd.random()
        m = 'e_amber' if r < 0.25 else 'e_lamp' if r > 0.8 else 'e_dim'
        floor_lamp(R, x, y, h, shade='green', m=m, scale=s)
    # a few armchairs, each under its own lamp
    for (x, y, a) in ((7.0, 3.2, 1.9), (10.2, 12.9, -1.2), (3.2, 9.3, 0.3)):
        R.parts.add(box(-0.4, -0.4, 0, 0.4, 0.4, 0.42, 'leather', skip=('-z',)).xform(a, x, y, 0))
        R.parts.add(box(-0.4, -0.4, 0.42, -0.22, 0.4, 1.0, 'leather').xform(a, x, y, 0))
        for s in (-1, 1):
            R.parts.add(box(-0.4, s * 0.4 - 0.1, 0.42, 0.4, s * 0.4 + 0.1, 0.66, 'leather').xform(a, x, y, 0))
        R.spot('sit', x, y, 0.45, a)
        floor_lamp(R, x - math.cos(a) * 0.75 + math.sin(a) * 0.5, y - math.sin(a) * 0.75 - math.cos(a) * 0.5, 1.75, m='e_lamp', scale=0.85)
    navloop(R, [(2.2, 2.2), (8, 1.8), (13.8, 2.2), (14.2, 8), (13.8, 13.8), (8, 14.2), (2.2, 13.8), (1.8, 8)])
    a = R.navpt(8.2, 7.4); R.link(1, a, 5)
    R.spot('probe', 8.2, 7.4, 1.7)
    R.meta.update(label='The Lamp Forest', weight=5,
                  blurb='Somebody left all the lamps on, and then the lamps grew. It is dark between them, and quiet, the way a wood is quiet.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
