"""The Busts: a sculpture gallery under a skylight. Stone heads on pedestals stand in rows, and every one
of them is turned to the wall, as if reading the shelves, or ashamed, or waiting for you to leave."""
from lib import *
from kit_c import *


def bust(R, x, y, face, m='ivory', ped='slate'):
    """A pedestal with a head and shoulders on it, looking toward angle `face`."""
    g = Geo()
    g.add(box(-0.3, -0.3, 0, 0.3, 0.3, 0.12, ped, skip=('-z',)))
    g.add(box(-0.22, -0.22, 0.12, 0.22, 0.22, 1.02, ped, skip=('-z', '+z')))
    g.add(box(-0.28, -0.28, 1.02, 0.28, 0.28, 1.1, ped))
    b = Geo()
    b.add(box(-0.1, -0.12, 1.1, 0.1, 0.12, 1.16, m, skip=('-z', '+z')))                 # socle
    b.add(box(-0.12, -0.25, 1.16, 0.11, 0.25, 1.3, m))              # chest
    b.add(box(-0.1, -0.23, 1.3, 0.09, 0.23, 1.37, m))               # shoulders
    b.add(cyl(0.0, 0, 1.37, 1.48, 0.06, 6, side=m, caps=False))      # neck
    b.add(sphere(0.0, 0, 1.58, 0.12, 9, 5, m))                      # head
    b.add(box(0.1, -0.016, 1.53, 0.14, 0.016, 1.59, m, skip=('-x',)))           # nose
    g.add(b)
    R.parts.add(g.xform(face, x, y))


def make():
    R = Room('gallerybust', 1, 1, res=1024)
    R.sockets(floor='mosaic', wall='tile')
    H = 6.0
    shell(R, H, floor='mosaic', ceil='plaster')
    # a deep coffer with the skylight, and a moulded frame round it
    R.cut(box(4.0, 4.0, H - 0.05, C - 4.0, C - 4.0, H + 0.8, 'plaster'))
    R.cut(box(4.6, 4.6, H + 0.75, C - 4.6, C - 4.6, R.hi + 0.5, 'plaster'))
    R.light(box(4.6, 4.6, R.hi - 0.08, C - 4.6, C - 4.6, R.hi - 0.05, 'e_sky'))
    for (x0, y0, x1, y1) in ((3.8, 3.8, C - 3.8, 4.0), (3.8, C - 4.0, C - 3.8, C - 3.8), (3.8, 4.0, 4.0, C - 4.0), (C - 4.0, 4.0, C - 3.8, C - 4.0)):
        R.parts.add(box(x0, y0, H - 0.25, x1, y1, H, 'tile'))
    # books round every wall
    wall_shelves(R, rows=10, frame='walnut')
    # busts along the walls, each an arm's length from the shelves and facing them
    for p in (2.7, 4.9, C - 4.9, C - 2.7):
        bust(R, p, 1.55, -math.pi / 2)
        bust(R, p, C - 1.55, math.pi / 2)
        bust(R, 1.55, p, math.pi)
        bust(R, C - 1.55, p, 0.0)
    # four in the middle, back to back, facing out to the corners
    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        bust(R, 8 + sx * 1.3, 8 + sy * 1.3, math.atan2(sy, sx))
    # a bench under the skylight, for looking at the backs of heads
    for (x0, y0, x1, y1) in ((5.2, 7.75, 6.3, 8.25), (C - 6.3, 7.75, C - 5.2, 8.25)):
        R.parts.add(box(x0, y0, 0.0, x1, y1, 0.45, 'walnut', top='velvet', skip=('-z',)))
    R.spot('sit', 5.75, 8.0, 0.45, 0.0); R.spot('sit', C - 5.75, 8.0, 0.45, math.pi)
    # small lamps over the doors and in the corners, for the night
    for (x, y) in ((8, T + 0.1), (8, C - T - 0.1), (T + 0.1, 8), (C - T - 0.1, 8)):
        R.light(box(x - 0.12, y - 0.1, 4.35, x + 0.12, y + 0.1, 4.47, 'e_amber'))
    for (x, y) in ((1.4, 1.4), (C - 1.4, 1.4), (C - 1.4, C - 1.4), (1.4, C - 1.4)):
        hang_lamp(R, x, y, 3.4, H, r=0.14)
    # walkers
    ring = navloop(R, ((3.2, 3.2), (8, 3.0), (C - 3.2, 3.2), (C - 3.0, 8), (C - 3.2, C - 3.2), (8, C - 3.0), (3.2, C - 3.2), (3.0, 8)))
    for k, (x, y) in ((1, (8, 1.2)), (3, (C - 1.2, 8)), (5, (8, C - 1.2)), (7, (1.2, 8))):
        R.link(ring[k], R.navpt(x, y))
    R.spot('probe', 8, 5.0, 1.7)
    R.meta.update(label='The Busts', weight=4,
                  blurb='A gallery of stone heads on pedestals, and every one has turned to face the wall. You do not see any of them move. You check.')
    R.meta['box'] = [[T, 0, T], [C - T, H + 0.8, C - T]]
    return R
