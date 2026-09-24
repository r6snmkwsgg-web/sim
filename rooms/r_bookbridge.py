"""The Book Bridge: two raised platforms, west and east, each with its stair and its desk, joined by a
railed walkway that runs along the top of a row of bookcases. The books under your feet are shelved too."""
from lib import *
from kit_c import *


def make():
    R = Room('bookbridge', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    shell(R, TOP, floor='floor', ceil='plaster')
    ph = 1.5                                  # platform height
    py0, py1 = 4.0, 12.0
    plats = ((2.6, 5.0), (C - 5.0, C - 2.6))
    for (x0, x1) in plats:
        R.parts.add(box(x0, py0, 0, x1, py1, ph, 'tile', top='floor', skip=('-z',)))
        R.parts.add(box(x0 - 0.05, py0 - 0.05, ph - 0.1, x1 + 0.05, py1 + 0.05, ph, 'tile', top='floor'))
    # books round the platforms' sides (below the walkway level)
    R.shelf(2.6, py0 + 0.1, 0, py1 - py0 - 0.2, '-x', rows=3, frame='walnut', crown=False)
    R.shelf(C - 2.6, py1 - 0.1, 0, py1 - py0 - 0.2, '+x', rows=3, frame='walnut', crown=False)
    R.shelf(2.6 + 0.1, py1, 0, 2.2, '+y', rows=3, frame='walnut', crown=False)
    R.shelf(C - 2.6 - 0.1, py0, 0, 2.2, '-y', rows=3, frame='walnut', crown=False)
    # the bridge: a row of double-faced bookcases, and the walkway on top of them
    bx0, bx1, by0, by1 = 5.0, C - 5.0, 7.4, 8.6
    R.shelf(bx1, 8.0, 0, bx1 - bx0, '-y', rows=3, frame='oak', crown=False)
    R.shelf(bx0, 8.0, 0, bx1 - bx0, '+y', rows=3, frame='oak', crown=False, back=False)
    R.parts.add(box(bx0, by0, ph - 0.1, bx1, by1, ph, 'oak', top='floor'))
    rail(R, bx0, by0 + 0.04, bx1, by0 + 0.04, ph)
    rail(R, bx0, by1 - 0.04, bx1, by1 - 0.04, ph)
    # stairs: the west one climbs north onto the west platform, the east one climbs south onto the east
    n, rise, run, sw = 8, ph / 8, 0.3, 1.2
    L = n * run
    R.flight(2.9, py0 - L, 0, sw, n, rise, run, '+y', m='floor', side='tile')
    R.flight(C - 2.9 - sw, py1 + L, 0, sw, n, rise, run, '-y', m='floor', side='tile')
    for x in (2.9 + 0.03, 2.9 + sw - 0.03):
        stair_rail(R, x, py0 - L, 0, x, py0, ph)
    for x in (C - 2.9 - 0.03, C - 2.9 - sw + 0.03):
        stair_rail(R, x, py1 + L, 0, x, py1, ph)
    # rails round the platforms (open at the stair heads and the bridge); tall cases on the outer edges
    e = 0.06
    W0, W1 = plats[0]
    rail(R, 2.9 + sw, py0 + e, W1 - e, py0 + e, ph)
    rail_poly(R, [(W1 - e, py0 + e), (W1 - e, by0)], ph)
    rail_poly(R, [(W1 - e, by1), (W1 - e, py1 - e), (W0 + 0.4, py1 - e)], ph)
    R.shelf(W0 + 0.02, py1 - 0.02, ph, py1 - py0 - 0.04, '+x', rows=8, frame='walnut')
    E0, E1 = plats[1]
    rail(R, C - 2.9 - sw, py1 - e, E0 + e, py1 - e, ph)
    rail_poly(R, [(E0 + e, py1 - e), (E0 + e, by1)], ph)
    rail_poly(R, [(E0 + e, by0), (E0 + e, py0 + e), (E1 - 0.4, py0 + e)], ph)
    R.shelf(E1 - 0.02, py0 + 0.02, ph, py1 - py0 - 0.04, '-x', rows=8, frame='walnut')
    rail(R, W0 + 0.02, py0 + e, 2.9, py0 + e, ph)
    rail(R, E1 - 0.02, py1 - e, C - 2.9, py1 - e, ph)
    # a desk on each platform
    for (xc, f, s) in ((4.1, 0.0, 1), (C - 4.1, math.pi, -1)):
        table_at(R, xc - 0.45, 9.6 if s > 0 else 5.4, xc + 0.45, 11.0 if s > 0 else 6.8, ph, top='leather')
        yc = 10.3 if s > 0 else 6.1
        desk_lamp(R, xc, yc + 0.35 * s, ph + 0.76)
        open_book(R, xc, yc - 0.2 * s, ph + 0.76, math.pi / 2)
        chair(R, xc - 0.75 * s, yc, f, z=ph)
    # light: a slot of sky over the bridge, lamps over the platforms
    R.cut(box(bx0, 7.1, TOP - 0.2, bx1, 8.9, R.hi + 0.5, 'plaster'))
    R.light(box(bx0, 7.1, R.hi - 0.08, bx1, 8.9, R.hi - 0.05, 'e_sky'))
    for (x, y) in ((3.8, 6.0), (3.8, 10.3), (C - 3.8, 5.7), (C - 3.8, 10.0)):
        hang_lamp(R, x, y, ph + 2.6, TOP, r=0.15)
    wall_shelves(R, rows=12, frame='walnut', sides='SN')
    wall_shelves(R, rows=12, frame='walnut', sides='WE', a=0.6, b=5.8)
    for (x, y) in ((8, T + 0.1), (8, C - T - 0.1)):
        R.light(box(x - 0.12, y - 0.1, 4.3, x + 0.12, y + 0.1, 4.42, 'e_amber'))
    # walkers
    ring = navloop(R, ((1.4, 1.4), (8, 2.2), (C - 1.4, 1.4), (C - 1.4, 8), (C - 1.4, C - 1.4), (8, C - 2.2), (1.4, C - 1.4), (1.4, 8)))
    up = [R.navpt(3.5, 1.2), R.navpt(3.5, 4.8, ph), R.navpt(3.9, 8.0, ph), R.navpt(C - 3.9, 8.0, ph), R.navpt(C - 3.5, 11.2, ph), R.navpt(C - 3.5, C - 1.2)]
    R.link(*up)
    R.link(ring[0], up[0]); R.link(up[5], ring[4])
    R.spot('probe', 8, 5.0, 2.2)
    R.meta.update(label='The Book Bridge', weight=5,
                  blurb='Two platforms, and between them a walkway laid along the top of a row of bookcases. You are walking on a shelf. The shelf does not seem to mind.')
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]
    return R
