"""The Lantern Hall: a dark, tall room walled with books, and dozens of little iron lanterns hung
on chains at every height, from far overhead down to where you have to duck round them."""
from lib import *
from kit_d import *
import random


def lantern(R, x, y, z, s=1.0, top=TOP, solid=False):
    """An iron lantern hanging from the ceiling, its bottom at z; its glass glows."""
    w, h = 0.11 * s, 0.3 * s
    g = Geo()
    g.add(box(x - w - 0.02, y - w - 0.02, z, x + w + 0.02, y + w + 0.02, z + 0.03, 'iron'))                   # base
    g.add(box(x - w - 0.03, y - w - 0.03, z + h, x + w + 0.03, y + w + 0.03, z + h + 0.04, 'iron'))           # lid
    g.add(box(x - w * 0.5, y - w * 0.5, z + h + 0.04, x + w * 0.5, y + w * 0.5, z + h + 0.1, 'iron', skip=('-z',)))
    for (px, py) in ((x - w, y - w), (x + w, y - w), (x + w, y + w), (x - w, y + w)):
        g.add(box(px - 0.012, py - 0.012, z + 0.03, px + 0.012, py + 0.012, z + h, 'iron', skip=('-z', '+z')))
    g.add(box(x - 0.008, y - 0.008, z + h + 0.1, x + 0.008, y + 0.008, top, 'iron', skip=('-z', '+z')))        # chain
    (R.parts if solid else R.nocol).add(g)
    R.light(box(x - w + 0.012, y - w + 0.012, z + 0.03, x + w - 0.012, y + w - 0.012, z + h, 'e_candle', skip=('-z', '+z')))


def make():
    R = Room('lanterns', 1, 1, res=1024)
    shell(R, TOP, floor='slate', wall='green', top='walnut')
    # books all round, tall, with a brass rail at the top
    for (a, b) in ((0.8, 6.2), (9.8, C - 0.8)):
        for f in ('+y', '-y', '+x', '-x'):
            wall_shelf(R, f, a, b, 0, rows=13, frame='walnut')
    # dark ceiling beams
    for p in (4.0, 8.0, 12.0):
        R.parts.add(box(p - 0.15, I0, TOP - 0.45, p + 0.15, I1, TOP - 0.05, 'walnut', skip=('+z',)))
    # the lanterns: a jittered grid, heights all over the place; the low ones are in your way
    rnd = random.Random(4242)
    k = 0
    for i in range(8):
        for j in range(8):
            x = 1.4 + i * 13.2 / 7 + rnd.uniform(-0.45, 0.45)
            y = 1.4 + j * 13.2 / 7 + rnd.uniform(-0.45, 0.45)
            if rnd.random() < 0.18: continue
            near_door = (abs(x - 8) < 2.0 and (y < 3.0 or y > 13.0)) or (abs(y - 8) < 2.0 and (x < 3.0 or x > 13.0))
            lo = 2.4 if near_door else 1.55
            z = lo + (6.6 - lo) * rnd.random() ** 1.6
            top = TOP - 0.45 if min(abs(x - p) for p in (4.0, 8.0, 12.0)) < 0.15 else TOP - 0.05
            lantern(R, x, y, z, s=rnd.uniform(0.85, 1.25), top=top, solid=z < 2.2)
            k += 1
    # a round table in the middle with a few books on it, and chairs
    R.parts.add(cyl(8, 8, 0, 0.72, 0.1, 10, side='walnut', caps=False))
    R.parts.add(cyl(8, 8, 0.72, 0.77, 0.9, 20, side='walnut', top='walnut', bottom='walnut'))
    book(R, 7.8, 8.2, 0.77, 0.4, 'oxblood'); book(R, 7.82, 8.18, 0.81, 0.9, 'green'); book(R, 8.3, 7.7, 0.77, 1.1, 'leather', open_=True)
    for a in (0.3, 2.4, 4.3):
        chair(R, 8 + 1.35 * math.cos(a), 8 + 1.35 * math.sin(a), a + math.pi)
    lantern(R, 8.05, 7.95, 1.25, s=1.3, top=TOP - 0.45, solid=True)
    loop(R, [(1.5, 1.5), (8, 1.5), (14.5, 1.5), (14.5, 8), (14.5, 14.5), (8, 14.5), (1.5, 14.5), (1.5, 8)])
    loop(R, [(5.5, 5.5), (10.5, 5.5), (10.5, 10.5), (5.5, 10.5)])
    R.link(R.navpt(8, 1.5), R.navpt(8, 5.5))
    R.spot('probe', 8, 5.2, 1.7)
    R.meta.update(label='The Lantern Hall', weight=5,
                  blurb='Someone lit every one of these lanterns and hung them at every height they could think of. The candles do not burn down.')
    return R
