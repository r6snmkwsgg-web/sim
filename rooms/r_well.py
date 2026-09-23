"""The Well: a square shaft through every floor, with a gallery of books round it on each level.
Jump the parapet and you fall, as long as you like."""
from lib import *


def make():
    R = Room('well', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets()
    s0, s1 = 4.2, C - 4.2                      # the shaft
    # the gallery: everything between the walls and the shaft, full height of the level
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, TOP, 'tile', bottom='floor', top='plaster'))
    R.cut(box(s0, s0, -LH, s1, s1, 2 * LH, 'tile'))
    # tiled parapet with a brass rail round the shaft
    pw, ph = 0.22, 0.86
    for (x0, y0, x1, y1) in ((s0 - pw, s0 - pw, s1 + pw, s0), (s0 - pw, s1, s1 + pw, s1 + pw), (s0 - pw, s0, s0, s1), (s1, s0, s1 + pw, s1)):
        R.parts.add(box(x0, y0, 0, x1, y1, ph, 'tile', skip=('-z',)))
    rr = 0.05
    for (x0, y0, x1, y1) in ((s0 - pw - rr, s0 - pw - rr, s1 + pw + rr, s0 - pw + 0.1), (s0 - pw - rr, s1 + pw - 0.1, s1 + pw + rr, s1 + pw + rr),
                             (s0 - pw - rr, s0 - pw, s0 - pw + 0.1, s1 + pw), (s1 + pw - 0.1, s0 - pw, s1 + pw + rr, s1 + pw)):
        R.parts.add(box(x0, y0, ph, x1, y1, ph + 0.07, 'brass'))
    # light coves under the ceiling round the shaft edge, and a lamp at each corner
    for (x0, y0, x1, y1) in ((s0 - 0.6, s0 - 0.6, s1 + 0.6, s0 - 0.25), (s0 - 0.6, s1 + 0.25, s1 + 0.6, s1 + 0.6),
                             (s0 - 0.6, s0 - 0.25, s0 - 0.25, s1 + 0.25), (s1 + 0.25, s0 - 0.25, s1 + 0.6, s1 + 0.25)):
        R.light(box(x0, y0, TOP - 0.06, x1, y1, TOP - 0.03, 'e_panel'))
    for (x, y) in ((1.4, 1.4), (C - 1.4, 1.4), (1.4, C - 1.4), (C - 1.4, C - 1.4)):
        R.light(cyl(x, y, TOP - 0.06, TOP - 0.03, 0.55, 24, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # tall bookcases on every wall, either side of the doors
    for (a, b) in ((0.75, 6.15), (9.85, C - 0.75)):
        R.shelf(a, T, 0, b - a, '+y', rows=8, frame='wood')
        R.shelf(b, C - T, 0, b - a, '-y', rows=8, frame='wood')
        R.shelf(T, b, 0, b - a, '+x', rows=8, frame='wood')
        R.shelf(C - T, a, 0, b - a, '-x', rows=8, frame='wood')
    # small lamps on the parapet corners (still lit after lights-out)
    for (x, y) in ((s0 - pw / 2, s0 - pw / 2), (s1 + pw / 2, s0 - pw / 2), (s0 - pw / 2, s1 + pw / 2), (s1 + pw / 2, s1 + pw / 2)):
        R.light(cyl(x, y, ph + 0.07, ph + 0.3, 0.08, 12, side='e_amber', top='e_amber', bottom='e_amber'))
    # walking round the gallery
    g = 2.3
    pts = [R.navpt(x, y) for (x, y) in ((g, g), (8, g), (C - g, g), (C - g, 8), (C - g, C - g), (8, C - g), (g, C - g), (g, 8))]
    R.link(*pts, pts[0])
    for (x, y, a) in ((8, s0 - 0.7, math.pi / 2), (8, s1 + 0.7, -math.pi / 2), (s0 - 0.7, 8, 0), (s1 + 0.7, 8, math.pi)):
        R.spot('edge', x, y, 0, a)
    R.spot('probe', 2.0, 8, 1.7)
    R.meta['label'] = 'The Well'
    R.meta['shaft'] = [s0, s0, s1, s1]
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]
    return R
