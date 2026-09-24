"""The Low Room: a ceiling you could touch, held up by a grid of squat columns that goes on too long.
Only a few bays have a lamp. The doorways alone are tall, and the ceiling steps up to meet them."""
from lib import *
from kit_c import *


def make():
    R = Room('lowroom', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    H = 2.3
    shell(R, H, floor='floor', ceil='plaster')
    # the ceiling steps up round each doorway, twice, to let the arch in
    steps = ((2.3, 3.6, 3.2), (1.9, 2.3, 4.25))      # (half width, depth, height)
    for (hw, dp, h) in steps:
        R.cut(box(8 - hw, T - 0.02, 0, 8 + hw, T + dp, h, 'plaster', bottom='floor'))
        R.cut(box(8 - hw, C - T - dp, 0, 8 + hw, C - T + 0.02, h, 'plaster', bottom='floor'))
        R.cut(box(T - 0.02, 8 - hw, 0, T + dp, 8 + hw, h, 'plaster', bottom='floor'))
        R.cut(box(C - T - dp, 8 - hw, 0, C - T + 0.02, 8 + hw, h, 'plaster', bottom='floor'))
    # lamps in the tall vestibules
    for (x, y) in ((8, T + 1.4), (8, C - T - 1.4), (T + 1.4, 8), (C - T - 1.4, 8)):
        R.light(box(x - 0.5, y - 0.5, 4.2, x + 0.5, y + 0.5, 4.23, 'e_panel'))
    # the grid of squat columns, every 2 m, except in the vestibules
    def in_vest(x, y):
        for (px, py) in ((8, 0), (8, C), (0, 8), (C, 8)):
            if abs(x - px) < 1.5 and abs(y - py) < 4.6 and px == 8: return True
            if abs(y - py) < 1.5 and abs(x - px) < 4.6 and py == 8: return True
        return False
    cols = []
    for i in range(8):
        for j in range(8):
            x, y = 1.0 + 2 * i, 1.0 + 2 * j
            if in_vest(x, y): continue
            cols.append((x, y))
            R.parts.add(box(x - 0.42, y - 0.42, 0, x + 0.42, y + 0.42, 0.22, 'tile', skip=('-z',)))
            R.parts.add(cyl(x, y, 0.22, H - 0.36, 0.3, 16, side='tile', caps=False))
            R.parts.add(box(x - 0.4, y - 0.4, H - 0.36, x + 0.4, y + 0.4, H - 0.2, 'tile'))
            R.parts.add(box(x - 0.55, y - 0.55, H - 0.2, x + 0.55, y + 0.55, H, 'tile', skip=('+z',)))
    # a few lamps, one every few bays, in shallow coffers
    for (x, y) in ((2, 10), (10, 4), (12, 12), (4, 4), (8, 8)):
        R.cut(box(x - 0.6, y - 0.6, H - 0.02, x + 0.6, y + 0.6, H + 0.18, 'plaster'))
        R.light(box(x - 0.35, y - 0.35, H + 0.14, x + 0.35, y + 0.35, H + 0.16, 'e_dim'))
    # low bookcases along the walls (between the vestibules), and a few between columns
    for (x, y, d) in ((3, 11, 'x'), (11, 3, 'x'), (11, 9, 'y'), (3, 3, 'y'), (11, 11, 'y'), (5, 9, 'x'), (3, 5, 'x'), (11, 13, 'x'), (5, 11, 'y'), (13, 5, 'y'), (5, 5, 'y'), (9, 5, 'x')):
        # a double-faced case spanning from one column to the next
        if d == 'x':
            R.shelf(x + 0.45, y, 0, 1.1, '+y', rows=4, frame='walnut', back=True)
            R.shelf(x + 1.55, y, 0, 1.1, '-y', rows=4, frame='walnut', back=False)
        else:
            R.shelf(x, y + 1.55, 0, 1.1, '+x', rows=4, frame='walnut')
            R.shelf(x, y + 0.45, 0, 1.1, '-x', rows=4, frame='walnut', back=False)
    # one chair, in a lit bay, facing a column
    chair(R, 10.0, 4.4, math.pi / 2)
    book_pile(R, 10.5, 3.7, 0, 4, seed=7)
    # exit signs over two doors that are really doors
    for (x, y) in ((8, T + 0.06), (T + 0.06, 8)):
        R.light(box(x - 0.2 if y < 1 else x - 0.03, y - 0.03 if y < 1 else y - 0.2, 4.35, x + 0.2 if y < 1 else x + 0.03, y + 0.03 if y < 1 else y + 0.2, 4.5, 'e_exit'))
    for (x, y) in ((2, 10), (12, 12)):
        R.light(box(x - 0.08, y - 0.08, 0.0, x + 0.08, y + 0.08, 0.03, 'e_amber'))
    # walkers along the aisles between columns
    ring = navloop(R, ((2, 2), (8, 2), (14, 2), (14, 8), (14, 14), (8, 14), (2, 14), (2, 8)))
    c = R.navpt(8, 8)
    R.link(ring[1], c, ring[5]); R.link(ring[7], c, ring[3])
    R.spot('probe', 6.0, 8.0, 1.2)
    R.meta.update(label='The Low Room', weight=5,
                  blurb='The ceiling is just above your head and stays there. The columns go on in every direction, and most of the lamps are off.')
    R.meta['box'] = [[T, 0, T], [C - T, 4.25, C - T]]
    return R
