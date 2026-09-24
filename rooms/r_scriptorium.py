"""The Scriptorium: rows of slanted writing desks under tall lancet windows, each desk with its stool,
its candle, its inkwell and its book open at the same page. A great lectern in the middle."""
from lib import *
from kit_b import *


def desk(R, cx, cy, w=1.3):
    """A slanted writing desk for a scribe facing +y; cy is the desk's middle."""
    y0, y1 = cy - 0.3, cy + 0.3
    pr = [(y0, 0.0), (y1, 0.0), (y1, 1.02), (y1 - 0.12, 1.02), (y0, 0.8)]
    R.parts.add(prism(pr, 'x', cx - w / 2, cx + w / 2, 'walnut', cap='walnut'))
    # the open book on the slope: two pages
    for s in (-1, 1):
        a0, a1 = (cx + 0.02, cx + 0.3) if s > 0 else (cx - 0.3, cx - 0.02)
        pp = [(y0 + 0.08, 0.8 - 0.0 + 0.08 * 0.22 / 0.48 + 0.005), (y0 + 0.4, 0.8 + 0.4 * 0.22 / 0.48 + 0.005),
              (y0 + 0.4, 0.8 + 0.4 * 0.22 / 0.48 + 0.02), (y0 + 0.08, 0.8 + 0.08 * 0.22 / 0.48 + 0.02)]
        R.nocol.add(prism(pp, 'x', a0, a1, 'ivory', cap='ivory'))
    # inkwell and candle on the flat ledge at the back
    R.nocol.add(cyl(cx + 0.45, y1 - 0.06, 1.02, 1.08, 0.035, 6, side='black', top='black', bottom='black'))
    candle(R, cx - 0.45, y1 - 0.06, 1.02, h=0.16)
    # the stool
    R.parts.add(cyl(cx, cy - 0.72, 0, 0.6, 0.19, 10, side='walnut', top='leather', bottom='walnut'))
    R.spot('sit', cx, cy - 0.72, 0.6, math.pi / 2)


def lancet(R, side, c, z0=4.7, w=0.8, jamb=1.7):
    pr = arch_profile(0, w, z0, jamb, 10)
    m = arch_mats(len(pr), 'tile', 'tile')
    if side in 'WE':
        x0, x1 = (0.08, T + 0.02) if side == 'W' else (C - T - 0.02, C - 0.08)
        R.cut(prism([(p + c, q) for p, q in pr], 'x', x0, x1, m))
        xe = 0.1 if side == 'W' else C - 0.1
        R.light(prism([(p * 0.98 + c, q) for p, q in pr], 'x', xe - 0.01, xe + 0.01, 'e_sky', cap='e_sky'))
    else:
        y0, y1 = (0.08, T + 0.02) if side == 'S' else (C - T - 0.02, C - 0.08)
        R.cut(prism([(p + c, q) for p, q in pr], 'y', y0, y1, m))
        ye = 0.1 if side == 'S' else C - 0.1
        R.light(prism([(p * 0.98 + c, q) for p, q in pr], 'y', ye - 0.01, ye + 0.01, 'e_sky', cap='e_sky'))


def make():
    R = Room('scriptorium', 1, 1, res=1024)
    H = TOP - 0.1
    shell(R, H, wall='tile', floor='slate', ceil='plaster')
    # dark beams across the ceiling
    for k in range(7):
        y = 1.6 + k * 2.13
        R.parts.add(box(T, y - 0.14, H - 0.45, C - T, y + 0.14, H, 'walnut', skip=('+z',)))
    # tall lancet windows high on every wall
    for side in 'SNWE':
        for c in (2.2, 5.1, 8.0, 10.9, 13.8):
            lancet(R, side, c)
    # bookcases round the walls, below the windows
    wall_shelves(R, rows=8, frame='walnut')
    # the desks: four rows of four, all facing north
    for y in (3.3, 5.2, 11.0, 12.9):
        for x in (2.9, 5.0, 11.0, 13.1):
            desk(R, x, y)
    # the great lectern, with a book as big as a door
    cx, cy = 8.0, 8.4
    R.parts.add(cyl(cx, cy, 0, 0.12, 0.6, 16, side='walnut', top='walnut', bottom='walnut'))
    R.parts.add(cyl(cx, cy, 0.12, 1.1, 0.14, 10, side='walnut', caps=False))
    pr = [(cy - 0.55, 1.1), (cy + 0.55, 1.1), (cy + 0.55, 1.62), (cy - 0.55, 1.28)]
    R.parts.add(prism(pr, 'x', cx - 0.8, cx + 0.8, 'walnut', cap='walnut'))
    for s in (-1, 1):
        a0, a1 = (cx + 0.02, cx + 0.72) if s > 0 else (cx - 0.72, cx - 0.02)
        k = (1.62 - 1.28) / 1.1
        pp = [(cy - 0.48, 1.28 + 0.07 * k + 0.01), (cy + 0.48, 1.28 + 1.03 * k + 0.01), (cy + 0.48, 1.28 + 1.03 * k + 0.05), (cy - 0.48, 1.28 + 0.07 * k + 0.05)]
        R.nocol.add(prism(pp, 'x', a0, a1, 'ivory', cap='ivory'))
    R.spot('read', cx, cy - 0.9, 0, math.pi / 2)
    for (x, y) in ((6.6, 7.2), (9.4, 7.2), (6.6, 9.6), (9.4, 9.6)):
        candelabrum(R, x, y, 1.6)
    # small lecterns at the ends of the rows
    for (x, y) in ((8.0, 3.9), (8.0, 12.2)):
        R.parts.add(cyl(x, y, 0, 1.15, 0.07, 8, side='walnut', top='walnut', bottom='walnut'))
        R.parts.add(prism([(y - 0.25, 1.1), (y + 0.25, 1.1), (y + 0.25, 1.35), (y - 0.25, 1.2)], 'x', x - 0.3, x + 0.3, 'walnut', cap='walnut'))
    # hanging lamps between the beams
    for x in (4.0, 12.0):
        for y in (4.25, 11.9):
            pendant(R, x, y, 3.2, H - 0.45, r=0.2, m='iron', em='e_lamp')
    loop(R, [(1.6, 1.6), (8, 1.6), (C - 1.6, 1.6), (C - 1.6, 8), (C - 1.6, C - 1.6), (8, C - 1.6), (1.6, C - 1.6), (1.6, 8)])
    a, b = R.navpt(6.6, 8.0), R.navpt(9.6, 8.0)
    R.link(7, a); R.link(b, 3)
    R.spot('probe', 8, 6.3, 2.0)
    R.meta.update(label='The Scriptorium', weight=6,
                  blurb='Sixteen desks, sixteen candles, sixteen books open at the same page. The ink in every well is still wet.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
