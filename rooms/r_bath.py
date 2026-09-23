"""The Sunken Court: a marble floor stepping down on every side, ringed by stone columns under a
coffered ceiling, a great square skylight above it, books in arched niches round the walls."""
from lib import *


def make():
    R = Room('bath', 1, 1, res=1024)
    R.sockets()
    H, W0 = 5.6, 0.9                  # thick walls, so the niches have somewhere to go
    R.cut(box(W0 - 0.02, W0 - 0.02, 0, C - W0 + 0.02, C - W0 + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    # the stepped basin: three steps of 0.3 m, then the floor of the bath
    for a, z in ((4.0, -0.3), (4.3, -0.6), (4.6, -0.9), (4.9, -1.2)):
        R.cut(box(a, a, z, C - a, C - a, 0.3, 'cobalt', top='tile'))
    for x in (6.0, 8.0, 10.0):
        for y in (4.91, C - 4.91):
            R.light(box(x - 0.2, y - 0.04, -1.12, x + 0.2, y + 0.04, -0.98, 'e_pool'))
    # the skylight over the court, in a deep coffer
    R.cut(box(5.0, 5.0, H - 0.05, C - 5.0, C - 5.0, H + 1.4, 'plaster'))
    R.light(box(5.3, 5.3, H + 1.3, C - 5.3, C - 5.3, H + 1.33, 'e_sky'))
    # coffers round the edge of the ceiling
    for (x, y) in ((2.2, 2.2), (C - 2.2, 2.2), (2.2, C - 2.2), (C - 2.2, C - 2.2)):
        R.cut(box(x - 1.1, y - 1.1, H - 0.05, x + 1.1, y + 1.1, H + 0.35, 'plaster'))
        R.light(box(x - 0.8, y - 0.8, H + 0.28, x + 0.8, y + 0.8, H + 0.31, 'e_panel'))
    # columns round the court
    for i in range(4):
        for j in range(4):
            if 0 < i < 3 and 0 < j < 3: continue
            x, y = 3.35 + i * 3.1, 3.35 + j * 3.1
            R.parts.add(cyl(x, y, 0, H, 0.26, 24, side='tile', caps=False))
            R.parts.add(cyl(x, y, 0, 0.25, 0.36, 24, side='tile', top='tile', caps=True))
            R.parts.add(cyl(x, y, H - 0.3, H, 0.36, 24, side='tile', caps=False))
    # arched niches with books, either side of every door
    nw, nd = 2.2, 0.5
    npr = arch_profile(0, nw, 0.3, 2.2, 16)
    for c in (3.3, C - 3.3):
        R.cut(prism([(p + c, q) for p, q in npr], 'y', W0 - nd, W0 + 0.05, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(c + nw / 2 - 0.08, W0 - nd, 0.3, nw - 0.16, '+y', rows=5, frame='paint', sides=False, back=False)
        R.cut(prism([(p + c, q) for p, q in npr], 'y', C - W0 - 0.05, C - W0 + nd, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(c - nw / 2 + 0.08, C - W0 + nd, 0.3, nw - 0.16, '-y', rows=5, frame='paint', sides=False, back=False)
        R.cut(prism([(p + c, q) for p, q in npr], 'x', W0 - nd, W0 + 0.05, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(W0 - nd, c + nw / 2 - 0.08, 0.3, nw - 0.16, '+x', rows=5, frame='paint', sides=False, back=False)
        R.cut(prism([(p + c, q) for p, q in npr], 'x', C - W0 - 0.05, C - W0 + nd, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(C - W0 + nd, c - nw / 2 + 0.08, 0.3, nw - 0.16, '-x', rows=5, frame='paint', sides=False, back=False)
    ring = [R.navpt(x, y) for (x, y) in ((2.0, 2.0), (8, 2.0), (C - 2.0, 2.0), (C - 2.0, 8), (C - 2.0, C - 2.0), (8, C - 2.0), (2.0, C - 2.0), (2.0, 8))]
    R.link(*ring, ring[0])
    for (x, y, a) in ((8, 3.2, math.pi / 2), (8, C - 3.2, -math.pi / 2), (3.2, 8, 0), (C - 3.2, 8, math.pi)):
        R.spot('sit', x, y, 0.0, a)
    R.spot('probe', 8, 8, 1.6)
    R.meta['label'] = 'The Sunken Court'
    R.meta['box'] = [[W0, -1.2, W0], [C - W0, H, C - W0]]
    return R
