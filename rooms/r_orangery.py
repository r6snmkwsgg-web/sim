"""The Orangery: a long glasshouse vault on iron ribs over a painted sky, potted trees in rows,
benches, a great tree in a round planter in the middle. A few shelves, for form's sake."""
from lib import *
from kit_e import *


def arc_band(c, w, jamb, rise, d0, d1, segs=24):
    """A closed (p, z) profile: the band between the vault's arc offset inward by d0 and by d1."""
    a = arch_profile(c, w - 2 * d0, 0, jamb, segs, rise=rise - d0)
    b = arch_profile(c, w - 2 * d1, 0, jamb, segs, rise=rise - d1)
    return a[2:] + list(reversed(b[2:]))       # east spring up round to the west spring, and back


def make():
    R = Room('orangery', 2, 1, res=1024)
    R.sockets(floor='terrazzo')
    W, D = R.W, R.D
    cy = D / 2
    jamb, rise = 4.6, 2.85
    w = D - 2 * T + 0.04
    pr = arch_profile(cy, w, 0, jamb, 40, rise=rise)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
    # the painted sky just under the vault, and the iron that holds the glass
    R.light(prism(arc_band(cy, w, jamb, rise, 0.0, 0.03, 40), 'x', T, W - T, 'e_skydome', cap='e_skydome'))
    for k in range(16):
        x = T + 0.05 + k * (W - 2 * T - 0.1) / 15
        R.parts.add(prism(arc_band(cy, w, jamb, rise, 0.03, 0.2), 'x', x - 0.05, x + 0.05, 'iron', cap='iron'))
    band = arch_profile(cy, w - 0.1, 0, jamb, 40, rise=rise - 0.05)[2:-1]
    for i in range(0, len(band), 4):
        p, q = band[i]
        R.parts.add(box(T, p - 0.03, q - 0.1, W - T, p + 0.03, q - 0.03, 'iron'))
    # a cornice where the glass begins, and a gallery of pilasters on the walls
    for (y0, y1) in ((T, T + 0.3), (D - T - 0.3, D - T)):
        R.parts.add(box(T, y0, jamb - 0.3, W - T, y1, jamb, 'ivory'))
    for x in (4.0, 12.0, 16.0, 20.0, 28.0):
        pilaster(R, x, T, '+y', 0, jamb - 0.3, w=0.5, d=0.2, m='ivory')
        pilaster(R, x, D - T, '-y', 0, jamb - 0.3, w=0.5, d=0.2, m='ivory')
    # a few bookcases, between the middle pilasters
    for (a, b) in ((12.3, 15.7), (16.3, 19.7)):
        R.shelf(a, T, 0, b - a, '+y', rows=6, frame='oak')
        R.shelf(b, D - T, 0, b - a, '-y', rows=6, frame='oak')
    for (a, b) in ((T + 1.0, 6.0), (10.0, D - T - 1.0)):
        R.shelf(T, b, 0, b - a, '+x', rows=5, frame='oak')
        R.shelf(W - T, a, 0, b - a, '-x', rows=5, frame='oak')
    # paths: a runner of mosaic down the middle, crossed at the doors
    R.parts.add(box(1.0, cy - 1.3, 0, W - 1.0, cy + 1.3, 0.01, 'marble', skip=('-z',)))
    # the trees, in two rows
    k = 0
    for x in (3.4, 12.0, 20.0, 28.6):
        for y in (4.0, D - 4.0):
            tree(R, x, y, 0, h=3.6 + 0.3 * math.sin(k * 1.7), r=1.15, seed=k); k += 1
    for x in (5.6, 10.4, 21.6, 26.4):
        for y in (2.2, D - 2.2):
            tree(R, x, y, 0, h=2.3, r=0.65, seed=40 + k); k += 1
    # the great tree in a round planter, with a bench round it
    cx = W / 2
    R.parts.add(cyl(cx, cy, 0, 0.45, 1.7, 40, side='tile', top='tile', bottom='tile'))
    R.parts.add(cyl(cx, cy, 0.45, 0.5, 1.5, 40, side='slate', top='slate', bottom='slate'))
    R.parts.add(cyl(cx, cy, 0.5, 4.8, 0.2, 12, side='walnut', caps=False))
    for (dx, dy, z, r) in ((0, 0, 5.2, 1.7), (1.1, 0.5, 4.8, 1.1), (-1.0, -0.6, 4.9, 1.2), (0.3, -1.1, 4.6, 1.0), (-0.5, 1.1, 5.5, 1.1)):
        R.nocol.add(sphere(cx + dx, cy + dy, z, r, 14, 7, 'green'))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        R.spot('sit', cx + math.cos(a) * 1.55, cy + math.sin(a) * 1.55, 0.45, a)
    # benches between the tree rows, facing the middle
    for x in (10.0, 22.0):
        for (y, f) in ((cy - 2.4, math.pi / 2), (cy + 2.4, -math.pi / 2)):
            bench(R, x - 1.0, y - 0.25, x + 1.0, y + 0.25, m='iron', seat='oak', spots=False)
            for dx in (-0.5, 0.5):
                R.spot('sit', x + dx, y, 0.45, f)
    # lamp posts along the path (their small lamps stay on at night)
    for x in (4.5, 12.4, 19.6, 27.5):
        for y in (cy - 1.6, cy + 1.6):
            R.parts.add(cyl(x, y, 0, 0.15, 0.16, 10, side='iron', top='iron', bottom='iron'))
            R.parts.add(cyl(x, y, 0.15, 2.7, 0.04, 8, side='iron', caps=False))
            R.light(sphere(x, y, 2.9, 0.16, 12, 6, 'e_amber'))
    # walkers
    m = loop(R, [(1.2, cy), (6.0, cy - 0.9), (13.0, cy - 0.9), (16.0, cy - 2.3), (19.0, cy - 0.9), (26.0, cy - 0.9), (W - 1.2, cy),
                 (26.0, cy + 0.9), (19.0, cy + 0.9), (16.0, cy + 2.3), (13.0, cy + 0.9), (6.0, cy + 0.9)])
    for (x, i, j) in ((8.0, 1, 11), (24.0, 5, 7)):
        s = R.navpt(x, 1.3); n = R.navpt(x, D - 1.3)
        a = R.navpt(x, cy - 0.9); b = R.navpt(x, cy + 0.9)
        R.link(s, a, b, n); R.link(m[i], a); R.link(b, m[j])
    R.spot('probe', 16.0, 5.0, 2.0)
    R.meta.update(label='The Orangery', weight=5,
                  blurb='A glasshouse, and above the glass, a sky. The trees are in good health and have never fruited. Nobody waters them.')
    R.meta['box'] = [[T, 0, T], [W - T, jamb + rise, D - T]]
    return R
