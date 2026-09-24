"""The Tea Room: a palm court under a glass laylight. Little round tables, every one laid for two
and never used; a counter; a kiosk that pours whatever you like, as long as it is tea."""
from lib import *
from kit_b import *


def make():
    R = Room('tearoom', 1, 1, res=1024)
    H = 4.6
    shell(R, H, wall='ivory', floor='terrazzo', ceil='plaster')
    # the laylight: a deep coffer glazed with light, brass mullions
    R.cut(box(4.4, 4.4, H - 0.05, C - 4.4, C - 4.4, H + 0.9, 'plaster'))
    R.light(box(4.5, 4.5, H + 0.8, C - 4.5, C - 4.5, H + 0.83, 'e_sky'))
    for k in range(1, 6):
        p = 4.4 + k * (C - 8.8) / 6
        R.nocol.add(box(p - 0.04, 4.4, H + 0.7, p + 0.04, C - 4.4, H + 0.8, 'brass', skip=('+z',)))
        R.nocol.add(box(4.4, p - 0.04, H + 0.7, C - 4.4, p + 0.04, H + 0.8, 'brass', skip=('+z',)))
    # green dado with a brass rail, all round
    for (x0, y0, x1, y1) in ((T, T, C - T, T + 0.03), (T, C - T - 0.03, C - T, C - T), (T, T, T + 0.03, C - T), (C - T - 0.03, T, C - T, C - T)):
        for (a, b) in ((T, 6.45), (9.55, C - T)):
            if y1 - y0 < 0.1: xa, ya, xb, yb = a, y0, b, y1
            else: xa, ya, xb, yb = x0, a, x1, b
            R.nocol.add(box(xa, ya, 0, xb, yb, 1.1, 'green', skip=('-z',)))
            R.nocol.add(box(xa - 0.01, ya - 0.01, 1.1, xb + 0.01, yb + 0.01, 1.16, 'brass'))
    # the kiosk, glowing, against the north wall (as in the rest areas)
    kx = 12.7
    R.parts.add(box(kx - 0.8, C - T - 0.85, 0, kx + 0.8, C - T + 0.01, 2.35, 'kiosk', skip=('-z',)))
    R.parts.add(box(kx - 0.86, C - T - 0.9, 2.35, kx + 0.86, C - T + 0.01, 2.5, 'brass'))
    R.light(box(kx - 0.6, C - T - 0.87, 1.15, kx + 0.6, C - T - 0.85, 1.95, 'e_kiosk'))
    R.parts.add(box(kx - 0.35, C - T - 0.95, 0.75, kx + 0.35, C - T - 0.85, 0.95, 'black'))   # the slot
    R.spot('kiosk', kx, C - T - 0.9, 0, 0)
    # the counter along the north wall, west of the door, with cups and books behind it
    R.parts.add(box(0.9, C - T - 1.95, 0, 5.0, C - T - 1.35, 1.0, 'walnut', skip=('-z',)))
    R.parts.add(box(0.85, C - T - 2.0, 1.0, 5.05, C - T - 1.3, 1.06, 'terrazzo'))
    R.parts.add(box(0.9, C - T - 1.35, 0, 1.0, C - T, 1.0, 'walnut', skip=('-z',)))
    bshelf(R, 5.8, C - T, 0.0, 5.0, '-y', rows=8, frame='walnut')
    for k in range(8):   # cups on the counter, in a row
        x = 1.3 + k * 0.5
        R.nocol.add(cyl(x, C - T - 1.65, 1.06, 1.14, 0.05, 8, side='ivory', top='books', bottom='ivory'))
    R.nocol.add(cyl(3.3, C - T - 1.65, 1.06, 1.6, 0.22, 14, side='brass', top='brass', bottom='brass'))   # the urn
    R.nocol.add(sphere(3.3, C - T - 1.65, 1.62, 0.12, 10, 5, 'brass'))
    # tables for two, laid
    for x in (2.9, 5.3, 10.7, 13.1):
        for y in (2.9, 5.5, 10.5):
            if x > 10 and y > 10 and x > 12: continue
            round_table(R, x, y, 0.42, 0.74, 'walnut', top='ivory')
            chair(R, x - 0.72, y, 0.0, frame='walnut', seat='velvet')
            chair(R, x + 0.72, y, math.pi, frame='walnut', seat='velvet')
            for s in (-1, 1):
                R.nocol.add(cyl(x + s * 0.2, y - 0.08, 0.74, 0.8, 0.045, 8, side='ivory', top='books', bottom='ivory'))
                R.nocol.add(cyl(x + s * 0.2, y - 0.08, 0.74, 0.745, 0.09, 10, side='ivory', top='ivory', bottom='ivory'))
            R.nocol.add(cyl(x, y + 0.15, 0.74, 0.88, 0.08, 10, side='ivory', top='ivory', bottom='ivory'))
            candle(R, x, y + 0.3, 0.74, h=0.06, flame=0.03)
    # a round banquette in the middle round a palm
    R.parts.add(cyl(8, 8, 0, 0.45, 1.25, 32, side='velvet', top='velvet', bottom='velvet'))
    R.parts.add(cyl(8, 8, 0.45, 1.0, 0.6, 24, side='velvet', top='walnut', bottom='velvet'))
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        R.spot('sit', 8 + math.cos(a) * 1.0, 8 + math.sin(a) * 1.0, 0.45, a)
    palm(R, 8, 8, 1.0, 3.3, pot='brass', n=12)
    # shelves on the south and west walls
    wall_shelves(R, rows=8, frame='walnut', sides='SW')
    # lamps: globes on brass stems along the east wall, pendants over the tables
    for y in (2.0, 5.5, 10.5):
        R.parts.add(box(C - T - 0.12, y - 0.04, 1.8, C - T, y + 0.04, 2.0, 'brass'))
        R.light(sphere(C - T - 0.25, y, 2.05, 0.13, 12, 6, 'e_lamp'))
    for x in (4.1, 11.9):
        for y in (4.2, 11.8):
            pendant(R, x, y, 2.6, H, r=0.2, m='green')
    loop(R, [(2.0, 1.6), (8, 1.6), (C - 2.0, 1.6), (C - 1.6, 8), (C - 2.0, C - 2.2), (8, C - 1.6), (2.0, 8), (2.0, 4.2)])
    ring_ = loop(R, [(8 + 2.3 * math.cos(k * math.pi / 3), 8 + 2.3 * math.sin(k * math.pi / 3)) for k in range(6)])
    R.spot('probe', 8, 8, 2.4)
    R.meta.update(label='The Tea Room', weight=5,
                  blurb='Every table is laid for two. The tea is always hot. Nobody has ever been seen pouring it.')
    R.meta['box'] = [[T, 0, T], [C - T, H + 0.83, C - T]]
    return R
