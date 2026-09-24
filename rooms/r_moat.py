"""The Moat: a square island of bookcases and one reading desk, ringed by a dry sunken moat whose
outer edge steps down like a bath; two railed bridges cross it. Books line the island's walls below."""
from lib import *
from kit_c import *


def make():
    R = Room('moat', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    H = 6.0
    shell(R, H, floor='floor', ceil='plaster')
    o, i0, i1 = 2.6, 5.2, C - 5.2          # moat outer edge; island
    dep = 1.5
    # the moat: five steps of 0.3 down from the outer edge (runs 0.3), then the flat bottom
    for k in range(5):
        a = o + k * 0.3
        frame_cut(R, a, i0 + 0.01, -(k + 1) * 0.3, 0.3, 'tile', bottom='slate')
    # the island, a stone block standing in it
    R.parts.add(box(i0, i0, -dep, i1, i1, 0, 'tile', top='floor'))
    R.parts.add(box(i0 - 0.06, i0 - 0.06, -0.12, i1 + 0.06, i1 + 0.06, 0.0, 'tile', top='floor'))   # coping
    # books round the island's retaining wall, facing out into the moat (split under the bridges)
    bx0, bx1 = 7.2, 8.8
    for (p, q) in ((i0 + 0.15, bx0 - 0.1), (bx1 + 0.1, i1 - 0.15)):
        R.shelf(q, i0, -dep, q - p, '-y', rows=3, frame='walnut', crown=False)
        R.shelf(p, i1, -dep, q - p, '+y', rows=3, frame='walnut', crown=False)
    R.shelf(i0, i0 + 0.15, -dep, i1 - i0 - 0.3, '-x', rows=3, frame='walnut', crown=False)
    R.shelf(i1, i1 - 0.15, -dep, i1 - i0 - 0.3, '+x', rows=3, frame='walnut', crown=False)
    # glowing strips in the foot of the outer steps, lighting the books from below
    for k in range(5):
        p = 4.4 + k * 1.8
        for (x, y, ax) in ((p, 3.8, 'x'), (p, C - 3.8, 'x'), (3.8, p, 'y'), (C - 3.8, p, 'y')):
            if ax == 'x': R.light(box(x - 0.35, y - 0.03, -1.45, x + 0.35, y + 0.03, -1.36, 'e_pool'))
            else: R.light(box(x - 0.03, y - 0.35, -1.45, x + 0.03, y + 0.35, -1.36, 'e_pool'))
    # two bridges, north and south, with rails
    for (y0, y1) in ((o - 0.05, i0), (i1, C - o + 0.05)):
        R.parts.add(box(bx0, y0, -0.28, bx1, y1, 0.0, 'tile', top='floor'))
        rail(R, bx0 + 0.05, y0, bx0 + 0.05, y1 + (0.05 if y1 == i0 else 0))
        rail(R, bx1 - 0.05, y0, bx1 - 0.05, y1)
    # rail round the island, open at the bridges
    e = 0.06
    rail_poly(R, [(bx0 + 0.05, i0 + e), (i0 + e, i0 + e), (i0 + e, i1 - e), (bx0 + 0.05, i1 - e)])
    rail_poly(R, [(bx1 - 0.05, i0 + e), (i1 - e, i0 + e), (i1 - e, i1 - e), (bx1 - 0.05, i1 - e)])
    # on the island: tall cases at the four corners, facing in, and the desk in the middle
    L = 1.5
    for (cx, cy, sx, sy) in ((i0, i0, 1, 1), (i1, i0, -1, 1), (i1, i1, -1, -1), (i0, i1, 1, -1)):
        x, y = cx + sx * 0.4, cy + sy * 0.4
        xa, xb = (x + 0.36, x + L) if sx > 0 else (x - L, x - 0.36)
        if sy > 0: R.shelf(xa, y, 0, xb - xa, '+y', rows=9, frame='oak')
        else: R.shelf(xb, y, 0, xb - xa, '-y', rows=9, frame='oak')
        ya, yb = (y, y + L) if sy > 0 else (y - L, y)
        if sx > 0: R.shelf(x, yb, 0, L, '+x', rows=9, frame='oak')
        else: R.shelf(x, ya, 0, L, '-x', rows=9, frame='oak')
    table(R, 7.0, 7.55, 9.0, 8.45, m='walnut', top='leather')
    desk_lamp(R, 8.6, 8.1, 0.76)
    open_book(R, 7.8, 7.95, 0.76, 0.1)
    book_pile(R, 7.3, 8.2, 0.76, 6, seed=3)
    chair(R, 8.0, 7.0, math.pi / 2)
    rug(R, 6.3, 6.3, 9.7, 9.7)
    # the ceiling: a deep coffer over the island with a panel of light, a hanging lamp over the desk
    R.cut(box(i0, i0, H - 0.05, i1, i1, H + 0.9, 'plaster'))
    R.light(box(i0 + 0.6, i0 + 0.6, H + 0.84, i1 - 0.6, i1 - 0.6, H + 0.87, 'e_panel'))
    pendant(R, 8, 8, 2.3, H + 0.85, r=0.32)
    for (x, y) in ((1.5, 1.5), (C - 1.5, 1.5), (C - 1.5, C - 1.5), (1.5, C - 1.5)):
        hang_lamp(R, x, y, 3.4, H, r=0.14)
    # books round the room's walls
    wall_shelves(R, rows=7, frame='wood')
    # candles on the corners of the island coping, lit all night
    candle(R, 7.25, 8.3, 0.76)
    # walkers
    ring = std_nav(R, 1.5)
    isl = navloop(R, ((6.4, 6.4), (8, 6.4), (9.6, 6.4), (9.6, 9.6), (8, 9.6), (6.4, 9.6)))
    R.link(ring[1], isl[1]); R.link(ring[5], isl[4])
    moat = navloop(R, ((4.5, 4.5), (C - 4.5, 4.5), (C - 4.5, C - 4.5), (4.5, C - 4.5)), z=-dep)
    R.spot('read', 8, 7.0, 0, math.pi / 2)
    R.spot('probe', 8, 6.2, 1.7)
    R.meta.update(label='The Moat', weight=5,
                  blurb='An island with one desk on it, and a dry moat round it lined with books. Whoever built the bridges did not trust you to jump.')
    R.meta['box'] = [[T, -dep, T], [C - T, H + 0.9, C - T]]
    return R
