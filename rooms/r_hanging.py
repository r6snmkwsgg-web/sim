"""The Hanging Shelves: bookcases hung from the ceiling on iron chains at different heights over an
open floor, some low enough to duck your head under, one hanging just above the floor."""
from lib import *
from kit_a import *

H = TOP - 0.1


def hung(R, axis, c, a, b, z, rows, frame='walnut'):
    """A double-faced bookcase hanging on four chains from the ceiling, bottom at z."""
    stack(R, axis, c, a, b, z, rows, depth=0.3, frame=frame)
    top = z + rows * 0.42 + 0.035 + 0.08 + 0.06
    if axis == 'x':
        R.parts.add(box(a - 0.06, c - 0.33, z - 0.05, b + 0.06, c + 0.33, z, frame))
        pts = [(a + 0.1, c - 0.2), (a + 0.1, c + 0.2), (b - 0.1, c - 0.2), (b - 0.1, c + 0.2)]
    else:
        R.parts.add(box(c - 0.33, a - 0.06, z - 0.05, c + 0.33, b + 0.06, z, frame))
        pts = [(c - 0.2, a + 0.1), (c + 0.2, a + 0.1), (c - 0.2, b - 0.1), (c + 0.2, b - 0.1)]
    for (x, y) in pts:
        R.nocol.add(cyl(x, y, top, H, 0.016, 4, side='iron', caps=False))
        R.nocol.add(box(x - 0.05, y - 0.05, top, x + 0.05, y + 0.05, top + 0.05, 'iron', skip=('-z',)))
        R.nocol.add(cyl(x, y, H - 0.06, H, 0.07, 6, side='iron', bottom='iron', top='iron'))


def make():
    R = Room('hanging', 1, 1, res=1024)
    shell(R, wall='plaster', floor='floor', ceil='plaster', h=H)
    cases = [('x', 4.0, 2.6, 6.6, 2.3, 4), ('y', 12.0, 2.4, 6.4, 3.3, 5), ('x', 11.7, 9.4, 13.6, 2.2, 3),
             ('y', 4.0, 9.4, 13.4, 4.3, 5), ('x', 8.0, 5.8, 10.2, 5.2, 4), ('y', 10.4, 7.0, 10.0, 0.75, 3),
             ('x', 14.2, 11.2, 14.4, 2.6, 4), ('y', 7.2, 3.2, 5.8, 3.9, 3), ('x', 7.2, 11.0, 12.8, 2.25, 2)]
    for (ax, c, a, b, z, rows) in cases:
        hung(R, ax, c, a, b, z, rows)
    # tall cases round the walls, broken at the doors
    for (a, b) in ((0.6, 6.2), (9.8, C - 0.6)):
        for f, w in (('+y', T), ('-y', C - T), ('+x', T), ('-x', C - T)):
            sh(R, f, w, a, b, rows=10, frame='walnut')
    # the ceiling glows between oak beams; bulbs hang at every height among the cases
    for k in range(1, 6):
        p = T + k * (C - 2 * T) / 6
        R.nocol.add(box(p - 0.12, T, H - 0.35, p + 0.12, C - T, H, 'oak'))
    for k in range(6):
        x0 = T + k * (C - 2 * T) / 6 + 0.12
        x1 = T + (k + 1) * (C - 2 * T) / 6 - 0.12
        R.light(box(x0 + 0.3, T + 0.5, H - 0.02, x1 - 0.3, C - T - 0.5, H - 0.005, 'e_panel'))
    for (x, y, z) in ((2.2, 8.0, 3.0), (6.6, 8.6, 2.6), (9.4, 3.6, 4.4), (13.6, 8.4, 3.4), (7.8, 13.6, 4.0), (13.4, 1.8, 2.8)):
        bulb(R, x, y, z, r=0.12, m='e_lamp', top=H)
    for (x, y) in ((1.6, 1.6), (C - 1.6, C - 1.6)):
        bulb(R, x, y, 2.4, r=0.1, m='e_amber', top=H)
    navloop(R, [(2.0, 2.0), (8, 2.0), (14.0, 2.0), (14.0, 8), (14.0, 12.4), (8, 14.0), (2.0, 14.0), (2.0, 8)])
    a, b = R.navpt(6.5, 8.0), R.navpt(8.8, 8.0)
    R.link(7, a, b); R.link(1, a); R.link(b, 5)
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Hanging Shelves', weight=4,
                  blurb='The bookcases hang on chains, some high, some low. The chains creak. You would rather not know what they are fixed to.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
