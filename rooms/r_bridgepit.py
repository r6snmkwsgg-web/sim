"""The Chasm: a dark slot 1.9 m deep and 3 m wide splits the room, lit only from its floor. Steps go
down into it at both ends; a narrow railed bridge crosses it. Its walls are shelved, at the bottom."""
from lib import *
from kit_c import *


def make():
    R = Room('bridgepit', 1, 1, res=1024)
    R.sockets(floor='floor', wall='damask')
    shell(R, TOP, floor='floor', wall='damask', ceil='plaster')
    y0, y1 = 10.3, 13.3                 # the chasm
    a = 2.6                             # where it starts, from the east and west walls
    n, rise, run = 10, 0.19, 0.28
    dep = n * rise
    for k in range(n):
        R.cut(box(a + k * run, y0, -(k + 1) * rise, C - a - k * run, y1, 0.3, 'slate', bottom='slate', top='slate'))
    xb0, xb1 = a + n * run, C - a - n * run      # the flat bottom
    # the bridge
    bx0, bx1 = 7.45, 8.55
    R.parts.add(box(bx0, y0 - 0.1, -0.22, bx1, y1 + 0.1, 0.0, 'tile', top='floor'))
    R.parts.add(box(bx0 + 0.1, y0 + 0.2, -0.34, bx1 - 0.1, y1 - 0.2, -0.22, 'iron', skip=()))
    rail(R, bx0 + 0.03, y0 - 0.1, bx0 + 0.03, y1 + 0.1)
    rail(R, bx1 - 0.03, y0 - 0.1, bx1 - 0.03, y1 + 0.1)
    # rails along both lips (over the stairs too)
    for yy in (y0 - 0.04, y1 + 0.04):
        rail(R, a + 0.02, yy, bx0 + 0.03, yy)
        rail(R, bx1 - 0.03, yy, C - a - 0.02, yy)
    # books down in the chasm, both walls, split under the bridge; a glow at their feet
    for (p, q) in ((xb0 + 0.1, bx0 - 0.15), (bx1 + 0.15, xb1 - 0.1)):
        R.shelf(p, y0, -dep, q - p, '+y', rows=4, frame='walnut')
        R.shelf(q, y1, -dep, q - p, '-y', rows=4, frame='walnut')
        for yy in (y0 + 0.42, y1 - 0.42):
            R.light(box(p + 0.1, yy - 0.03, -dep, q - 0.1, yy + 0.03, -dep + 0.035, 'e_pool'))
    # candles on the stair ends of the bottom
    for x in (xb0 + 0.2, xb1 - 0.2):
        for y in (y0 + 0.25, y1 - 0.25):
            candle(R, x, y, -dep, h=0.3, r=0.04)
    # the room above: dim reading tables in the south, a long case on the north ledge
    for tx in (3.6, C - 3.6):
        table(R, tx - 1.2, 4.4, tx + 1.2, 5.4)
        desk_lamp(R, tx, 4.9, 0.76, m='e_dim')
        chair(R, tx - 0.6, 3.8, math.pi / 2); chair(R, tx + 0.6, 6.0, -math.pi / 2)
        open_book(R, tx - 0.5, 4.75, 0.76, 0.2)
    book_pile(R, 3.9, 5.1, 0.76, 5, seed=2)
    wall_shelves(R, rows=12, frame='walnut', sides='SN')
    R.shelf(T, 6.2, 0, 5.6, '+x', rows=12, frame='walnut')
    R.shelf(C - T, 0.6, 0, 5.6, '-x', rows=12, frame='walnut')
    # night lights over the doors
    for (x, y) in ((8, T + 0.1), (8, C - T - 0.1), (T + 0.1, 8), (C - T - 0.1, 8)):
        R.light(box(x - 0.12, y - 0.1, 4.3, x + 0.12, y + 0.1, 4.42, 'e_amber'))
    # walkers: the south floor, the north ledge, over the bridge and through the chasm
    s = navloop(R, ((1.5, 1.5), (8, 1.5), (C - 1.5, 1.5), (C - 1.5, 8), (C - 1.5, 9.3), (8, 9.3), (1.5, 9.3), (1.5, 8)))
    nth = navloop(R, ((1.5, 14.5), (8, 14.5), (C - 1.5, 14.5)), close=False)
    R.link(s[6], nth[0]); R.link(s[4], nth[2]); R.link(s[5], nth[1])
    bot = navloop(R, ((xb0 + 0.6, 11.8), (xb1 - 0.6, 11.8)), z=-dep, close=False)
    R.link(R.navpt(1.5, 11.8), R.navpt(a + 0.4, 11.8), bot[0]); R.link(bot[1], R.navpt(C - a - 0.4, 11.8), R.navpt(C - 1.5, 11.8))
    R.spot('probe', 8, 7.5, 1.7)
    R.meta.update(label='The Chasm', weight=4,
                  blurb='A crack runs through the floor, lit from somewhere below. There are books down there too. There are always books down there.')
    R.meta['box'] = [[T, -dep, T], [C - T, TOP, C - T]]
    return R
