"""The Reading Plain: a room 128 m square and 3.4 m high, set with long reading tables in rows to the
horizon, each with its green-shaded lamps and its chairs, all empty. Bookcases round the edges only:
from the middle you cannot see a single book."""
from lib import *
from kit_g import *


def make():
    R = Room('readingplain', 8, 8, levels=2, res=2048)
    W, D = R.W, R.D
    H = 3.4
    seal(R, upper_sockets(R), floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='floor', top='plaster'))
    th, tw = 0.76, 0.6                       # table height, half width
    lamp_n = 0
    for j in range(R.d):
        for yc in (j * C + 4.0, j * C + 12.0):
            for i in range(R.w - 1):
                x0, x1 = i * C + 10.5, i * C + 21.5
                g = Geo()
                g.add(box(x0, yc - tw, th - 0.05, x1, yc + tw, th, 'walnut', top='leather'))
                for xt in (x0 + 0.4, (x0 + x1) / 2, x1 - 0.4):
                    g.add(box(xt - 0.05, yc - tw + 0.12, 0, xt + 0.05, yc + tw - 0.12, th - 0.05, 'walnut', skip=('-z', '+z')))
                g.add(box(x0 + 0.4, yc - 0.05, 0.25, x1 - 0.4, yc + 0.05, 0.35, 'walnut'))
                # banker's lamps down the middle
                for k in range(4):
                    lx = x0 + 1.4 + k * (x1 - x0 - 2.8) / 3
                    g.add(box(lx - 0.02, yc - 0.02, th, lx + 0.02, yc + 0.02, th + 0.36, 'brass', skip=('-z',)))
                    g.add(box(lx - 0.07, yc - 0.3, th + 0.36, lx + 0.07, yc + 0.3, th + 0.48, 'green'))
                    R.light(box(lx - 0.06, yc - 0.28, th + 0.3, lx + 0.06, yc + 0.28, th + 0.36, 'e_lamp', skip=('+z',)))
                    lamp_n += 1
                R.parts.add(g)
                # chairs, pulled in, both sides: a seat cantilevered off a solid back
                c = Geo()
                for k in range(4):
                    cx = x0 + 1.4 + k * (x1 - x0 - 2.8) / 3
                    for s in (-1, 1):
                        cy = yc + s * (tw + 0.25)
                        c.add(box(cx - 0.22, cy - 0.21, 0.41, cx + 0.22, cy + 0.21, 0.46, 'walnut', top='leather', skip=(('+y',) if s > 0 else ('-y',))))
                        by = cy + s * 0.21
                        c.add(box(cx - 0.22, min(by, by - s * 0.05), 0, cx + 0.22, max(by, by - s * 0.05), 0.98, 'walnut', skip=('-z',)))
                        if (i + k) % 3 == 0 and s < 0: R.spot('sit', cx, cy, 0.46, math.pi / 2)
                R.parts.add(c)
    # a lamp or two in the doorway aisles, low and amber, for the night
    for j in range(R.d):
        for i in range(R.w):
            if (i + j) % 2: continue
            R.light(box(i * C + C / 2 - 0.35, j * C + C / 2 - 0.35, H - 0.03, i * C + C / 2 + 0.35, j * C + C / 2 + 0.35, H - 0.01, 'e_amber', skip=('+z',)))
    # bookcases round the edges only
    wall_cases(R, rows=7, frame='walnut')
    # walkers: the doorway aisles
    pts = {}
    for i in (1, 3, 5):
        for j in (1, 3, 5):
            pts[(i, j)] = R.navpt(i * C + C / 2, j * C + C / 2)
    for i in (1, 3, 5):
        R.link(pts[(i, 1)], pts[(i, 3)], pts[(i, 5)])
        R.link(pts[(1, i)], pts[(3, i)], pts[(5, i)])
    R.spot('probe', 3 * C + C / 2, 3 * C + C / 2, 1.7)
    R.meta.update(label='The Reading Plain', weight=3,
                  blurb='Reading tables to the horizon, every lamp lit, every chair pushed in. Nobody reads here. Perhaps they all found what they were looking for.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    return R
