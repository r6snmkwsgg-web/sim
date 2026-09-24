"""The Cascade: the north half of the room is a stair of bookcases for giants, stepping down from
the ceiling to the floor like a waterfall of books, lit along its top lip. A narrow canyon between
two falls leads to the north door; at their foot, a dry plunge pool and books that have fallen."""
from lib import *
from kit_d import *
import random


def make():
    R = Room('bookfall', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    TP = TOP - 0.05
    y0, n, sh = 9.8, 6, 1.1                    # foot of the falls, number of steps, step height
    ds = (I1 - y0) / n
    cx0, cx1 = 6.0, 10.0                       # the canyon to the north door
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, y0, TP, 'tile', bottom='floor', top='plaster'))
    R.cut(box(cx0, y0 - 0.1, 0, cx1, C - T + 0.02, TP, 'tile', bottom='floor', top='plaster'))
    for k in range(n):
        ya, yb = y0 + k * ds, (y0 + (k + 1) * ds if k < n - 1 else C - T + 0.02)
        for (xa, xb) in ((T - 0.02, cx0 + 0.01), (cx1 - 0.01, C - T + 0.02)):
            R.cut(box(xa, ya, (k + 1) * sh, xb, yb, TP, 'tile', bottom='walnut', top='plaster'))
    R.meta['box'] = [[T, -0.6, T], [C - T, TOP, C - T]]
    # bookcases on every riser of the falls
    for k in range(n):
        yk = y0 + k * ds
        for (xa, xb) in ((I0 + 0.05, cx0 - 0.05), (cx1 + 0.05, I1 - 0.05)):
            wall_shelf(R, '-y', xa, xb, k * sh, rows=2, row_h=0.47, off=yk, frame='walnut', sides=False)
    # the canyon walls: tall cases the full height of the falls
    top = n * sh
    for (x, f) in ((cx0, '+x'), (cx1, '-x')):
        wall_shelf(R, f, y0 + 0.1, 13.3, 0, rows=15, off=x, frame='walnut')
    R.parts.add(box(cx0 - 0.02, y0 - 0.05, top - 0.25, cx1 + 0.02, 13.3, top, 'tile'))     # a lintel of stone over the canyon
    # light along the top lip: a slot in the ceiling above the highest step
    for (xa, xb) in ((I0, cx0 - 0.3), (cx1 + 0.3, I1)):
        R.cut(box(xa, I1 - ds - 0.2, TP - 0.05, xb, I1, TP + 0.3, 'plaster'))
        R.light(box(xa + 0.1, I1 - ds - 0.1, TP + 0.25, xb - 0.1, I1 - 0.05, TP + 0.27, 'e_sky', skip=('+z',)))
    # warm step-lights under the crown of every other riser (the spray)
    for k in (2, 4):
        yk = y0 + k * ds
        for (xa, xb) in ((I0 + 0.3, cx0 - 0.3), (cx1 + 0.3, I1 - 0.3)):
            R.light(box(xa, yk - 0.42, k * sh + 1.02, xb, yk - 0.38, k * sh + 1.05, 'e_pool'))
    # the dry plunge pool at the foot of the falls
    px0, py0, px1, py1 = 2.8, 3.0, 13.2, 8.0
    R.pool(px0, py0, px1, py1, 0.6, m='cobalt')
    for x in (4.5, 8.0, 11.5):
        R.light(box(x - 0.25, py1 - 0.49, -0.52, x + 0.25, py1 - 0.45, -0.4, 'e_pool'))
        R.light(box(x - 0.25, py0 + 0.45, -0.52, x + 0.25, py0 + 0.49, -0.4, 'e_pool'))
    # fallen books, in the pool and along the foot of the falls
    rnd = random.Random(31)
    mats = ('leather', 'oxblood', 'green', 'walnut', 'ivory')
    for k in range(34):
        if k < 22:
            x, y, z = rnd.uniform(px0 + 1.1, px1 - 1.1), rnd.uniform(py0 + 1.1, py1 - 1.1), -0.6
        else:
            x = rnd.choice((rnd.uniform(1.0, cx0 - 0.5), rnd.uniform(cx1 + 0.5, 15.0))); y, z = rnd.uniform(9.18, 9.3), 0.0
        stack = 1 if rnd.random() < 0.7 else rnd.randint(2, 4)
        for s in range(stack):
            book(R, x + rnd.uniform(-0.03, 0.03), y, z + s * 0.045, rnd.uniform(0, math.pi), m=rnd.choice(mats), t=0.045)
    # ceiling panels over the south half, a few lamps in the canyon
    for (x, y) in ((4.0, 3.0), (12.0, 3.0), (4.0, 7.5), (12.0, 7.5)):
        R.light(box(x - 0.9, y - 0.9, TP - 0.03, x + 0.9, y + 0.9, TP - 0.01, 'e_panel', skip=('+z',)))
    for y in (11.0, 13.0, 15.0):
        pendant(R, 8, y, 3.4, r=0.18, top=top - 0.25 if y < 13.3 else TP)
    loop(R, [(1.6, 1.6), (8, 1.6), (14.4, 1.6), (14.4, 8.55), (8, 8.55), (1.6, 8.55)])
    R.link(R.navpt(8, 8.55), R.navpt(8, 14.5))
    p = loop(R, [(4.5, 4.5), (11.5, 4.5), (11.5, 6.5), (4.5, 6.5)], z=-0.6)
    R.link(R.navpt(8, 1.6), R.navpt(8, 4.5, -0.6))
    R.spot('probe', 8, 5.5, 1.2)
    R.meta.update(label='The Cascade', weight=5,
                  blurb='The shelves come down from the ceiling in steps too tall to climb, as if the books were pouring out of somewhere. Some of them have landed.')
    return R
