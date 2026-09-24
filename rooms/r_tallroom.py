"""The Narrow Room: the room is almost all solid. What is left is a canyon two metres wide and seven
and a half tall, walled with books to the top, that wanders in an S between the doors under slits of sky."""
from lib import *
from kit_c import *


def make():
    R = Room('tallroom', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    H = 7.3
    h = 1.36                                   # half the canyon's width, wall to wall
    e = 0.02
    segs = [((8, T), (8, 3.5)), ((8, 3.5), (12.5, 3.5)), ((12.5, 3.5), (12.5, 8)), ((T, 8), (C - T, 8)),
            ((3.5, 8), (3.5, 12.5)), ((3.5, 12.5), (8, 12.5)), ((8, 12.5), (8, C - T))]
    rects = []
    for (a, b) in segs:
        x0, x1 = sorted((a[0], b[0])); y0, y1 = sorted((a[1], b[1]))
        rects.append((max(T - e, x0 - h), max(T - e, y0 - h), min(C - T + e, x1 + h), min(C - T + e, y1 + h)))
    hv = 1.9
    rects += [(8 - hv, T - e, 8 + hv, 2.6), (8 - hv, C - 2.6, 8 + hv, C - T + e), (T - e, 8 - hv, 2.6, 8 + hv), (C - 2.6, 8 - hv, C - T + e, 8 + hv)]
    for r in rects:
        R.cut(box(r[0], r[1], 0, r[2], r[3], H, 'tile', bottom='floor', top='plaster'))
    # slits of sky along the middle of every stretch
    for (a, b) in segs:
        x0, x1 = sorted((a[0], b[0])); y0, y1 = sorted((a[1], b[1]))
        if x0 == x1: g = (x0 - 0.16, max(y0, T + 0.6), x1 + 0.16, min(y1, C - T - 0.6))
        else: g = (max(x0, T + 0.6), y0 - 0.16, min(x1, C - T - 0.6), y1 + 0.16)
        R.cut(box(g[0], g[1], H - 0.05, g[2], g[3], R.hi + 0.5, 'plaster'))
        R.light(box(g[0], g[1], R.hi - 0.08, g[2], g[3], R.hi - 0.05, 'e_sky'))
    # books on every wall of the canyon, to the top
    for run in wall_runs(rects):
        x0, y0, x1, y1, f = run
        if (f == '+y' and y0 < T + 0.1) or (f == '-y' and y0 > C - T - 0.1) or (f == '+x' and x0 < T + 0.1) or (f == '-x' and x0 > C - T - 0.1):
            continue
        run_shelf(R, run, 0, 9, frame='walnut', trim=0.37, minlen=1.0, row_h=0.62)
    # two rolling ladders, and small lamps at head height where the canyon turns
    for (x, y, ax) in ((10.2, 3.5 - h + 0.36, 'x'), (3.5 - h + 0.36, 10.6, 'y')):
        for k in (0, 1):
            if ax == 'x': R.parts.add(box(x + k * 0.5, y + 0.25, 0, x + k * 0.5 + 0.04, y + 0.29, 4.4, 'brass'))
            else: R.parts.add(box(x + 0.25, y + k * 0.5, 0, x + 0.29, y + k * 0.5 + 0.04, 4.4, 'brass'))
        for j in range(14):
            z = 0.3 + j * 0.3
            if ax == 'x': R.parts.add(box(x, y + 0.25, z, x + 0.54, y + 0.29, z + 0.03, 'brass'))
            else: R.parts.add(box(x + 0.25, y, z, x + 0.29, y + 0.54, z + 0.03, 'brass'))
    for (x, y) in ((8, 3.5), (12.5, 3.5), (12.5, 8), (3.5, 8), (3.5, 12.5), (8, 12.5)):
        hang_lamp(R, x, y, 3.6, H, r=0.13)
    # walkers along the S
    p = [R.navpt(x, y) for (x, y) in ((8, 1.2), (8, 3.5), (12.5, 3.5), (12.5, 8), (3.5, 8), (3.5, 12.5), (8, 12.5), (8, C - 1.2))]
    R.link(*p)
    R.link(R.navpt(1.2, 8), p[4]); R.link(p[3], R.navpt(C - 1.2, 8))
    R.spot('probe', 12.5, 8, 2.0)
    R.meta.update(label='The Narrow Room', weight=5,
                  blurb='The walls are books and they go up and up, and the sky is a crack. It is a very tall room with nowhere in it.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
