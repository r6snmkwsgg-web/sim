"""The Study: somebody's private study, a fire lit in a stone fireplace, leather armchairs, a big
desk with its lamp on, rugs, and shelves from the floor to the ceiling on every wall. All of it
perfectly cosy, except that the room is four times too big and has no windows."""
from lib import *
from kit_d import *


def rug(R, x0, y0, x1, y1, m='carpet', border='oxblood'):
    R.nocol.add(box(x0, y0, 0, x1, y1, 0.012, border, skip=('-z',)))
    R.nocol.add(box(x0 + 0.25, y0 + 0.25, 0.012, x1 - 0.25, y1 - 0.25, 0.018, m, skip=('-z',)))


def floor_lamp(R, x, y, h=1.65):
    R.parts.add(cyl(x, y, 0, 0.04, 0.2, 10, side='brass', top='brass', caps=True))
    R.parts.add(box(x - 0.02, y - 0.02, 0.04, x + 0.02, y + 0.02, h, 'brass', skip=('-z', '+z')))
    R.nocol.add(cyl(x, y, h - 0.05, h + 0.25, 0.28, 12, side='ivory', caps=False))
    R.light(cyl(x, y, h - 0.02, h + 0.02, 0.12, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))


def make():
    R = Room('study', 1, 1, res=1024)
    shell(R, TOP, floor='floor', wall='damask', top='walnut')
    H = TOP - 0.05
    # the fireplace on the north wall, east of the door: a stone surround, a mantel, no chimney
    fx0, fx1, fd = 10.3, 14.9, 0.7            # surround span, depth into the room
    yb = I1 - fd
    R.parts.add(box(fx0, yb, 0, fx0 + 0.9, I1, 2.5, 'tile', skip=('-z',)))              # jambs
    R.parts.add(box(fx1 - 0.9, yb, 0, fx1, I1, 2.5, 'tile', skip=('-z',)))
    R.parts.add(box(fx0 + 0.9, yb, 1.9, fx1 - 0.9, I1, 2.5, 'tile'))                    # lintel
    R.parts.add(box(fx0 - 0.15, yb - 0.15, 2.5, fx1 + 0.15, I1, 2.68, 'tile'))            # mantel shelf
    R.parts.add(box(fx0 - 0.3, yb - 1.0, 0, fx1 + 0.3, I1, 0.12, 'slate', skip=('-z',)))  # hearth
    R.parts.add(box(fx0 + 0.9, I1 - 0.08, 0.12, fx1 - 0.9, I1, 1.9, 'slate', skip=('-z',)))  # blackened back
    cx = (fx0 + fx1) / 2
    # grate, logs and embers
    R.parts.add(box(cx - 0.9, yb + 0.15, 0.12, cx + 0.9, yb + 0.55, 0.2, 'iron'))
    for k, (dx, a) in enumerate(((-0.35, 0.15), (0.3, -0.2), (0.0, 0.05))):
        R.parts.add(box(-0.45, -0.07, 0, 0.45, 0.07, 0.14, 'walnut').xform(a, cx + dx, yb + 0.33, 0.2 + (0.12 if k == 2 else 0)))
    R.light(box(cx - 0.8, yb + 0.18, 0.2, cx + 0.8, yb + 0.52, 0.26, 'e_amber'))
    for (dx, dy, s) in ((-0.5, 0.05, 0.12), (0.45, 0.0, 0.1), (0.05, 0.12, 0.15), (-0.15, -0.08, 0.08)):
        R.light(box(cx + dx - s, yb + 0.33 + dy - s / 2, 0.26, cx + dx + s, yb + 0.33 + dy + s / 2, 0.36 + s, 'e_amber'))
    # candlesticks and a clock on the mantel
    for dx in (-1.9, 1.9):
        R.nocol.add(cyl(cx + dx, yb + 0.25, 2.68, 2.98, 0.03, 8, side='brass', caps=False))
        R.light(cyl(cx + dx, yb + 0.25, 2.98, 3.08, 0.02, 6, side='e_candle', top='e_candle', bottom='e_candle'))
    R.nocol.add(box(cx - 0.2, yb + 0.1, 2.68, cx + 0.2, yb + 0.3, 3.1, 'walnut'))
    # books over the fireplace, all the way up
    wall_shelf(R, '-y', fx0 - 0.1, fx1 + 0.1, 2.72, rows=10, frame='walnut', sides=True)
    # floor-to-ceiling shelves everywhere else
    rows = 17
    wall_shelf(R, '-y', 0.8, 6.2, 0, rows=rows, frame='walnut')
    for (a, b) in ((0.8, 6.2), (9.8, 15.2)):
        wall_shelf(R, '+y', a, b, 0, rows=rows, frame='walnut')
        wall_shelf(R, '+x', a, b, 0, rows=rows, frame='walnut')
        wall_shelf(R, '-x', a, b, 0, rows=rows, frame='walnut')
    # the fireside: a rug, three armchairs, a low table
    rug(R, 9.6, 9.0, 15.0, 13.4)
    armchair(R, 10.6, 11.4, math.pi / 2 - 0.5)
    armchair(R, 14.0, 11.2, math.pi / 2 + 0.55)
    armchair(R, 12.3, 10.0, math.pi / 2)
    table(R, 11.7, 11.4, 12.9, 12.1, h=0.45, m='walnut')
    book(R, 12.1, 11.75, 0.45, 0.3, 'oxblood'); book(R, 12.5, 11.8, 0.45, 1.2, 'green', open_=True)
    floor_lamp(R, 9.9, 10.0)
    # the desk, on its own rug, facing the fire across the room
    rug(R, 1.8, 2.0, 7.0, 6.4, m='velvet', border='carpet')
    R.parts.add(box(2.6, 3.6, 0.72, 5.4, 4.8, 0.78, 'walnut'))
    R.nocol.add(box(2.9, 3.8, 0.78, 5.1, 4.6, 0.785, 'leather', skip=('-z',)))
    for (x0, x1) in ((2.65, 3.35), (4.65, 5.35)):     # pedestals of drawers
        R.parts.add(box(x0, 3.65, 0, x1, 4.75, 0.72, 'walnut', skip=('-z', '+z')))
    armchair(R, 4.0, 3.0, math.pi / 2, m='leather')
    R.parts.add(cyl(4.9, 4.4, 0.785, 0.81, 0.09, 8, side='brass', top='brass'))
    R.parts.add(box(4.88, 4.38, 0.81, 4.92, 4.42, 1.15, 'brass', skip=('-z',)))
    R.nocol.add(cyl(4.9, 4.4, 1.12, 1.24, 0.14, 8, side='green', top='green', bottom='green'))
    R.light(box(4.78, 4.28, 1.1, 5.02, 4.52, 1.12, 'e_lamp', skip=('+z',)))
    book(R, 3.3, 4.2, 0.785, 0.1, 'leather', open_=True)
    for k in range(5):
        book(R, 2.95, 4.5, 0.785 + k * 0.05, 0.2 * k, ('oxblood', 'green', 'leather', 'walnut', 'ivory')[k], t=0.05)
    # a dim chandelier far overhead, sconces between the shelves
    for (x, y) in ((8, 8),):
        R.nocol.add(box(x - 0.015, y - 0.015, 5.2, x + 0.015, y + 0.015, H, 'iron', skip=('-z', '+z')))
        R.nocol.add(ring(x, y, 5.1, 5.2, 0.8, 0.9, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
        for k in range(8):
            a = k * math.pi / 4
            R.light(cyl(x + 0.85 * math.cos(a), y + 0.85 * math.sin(a), 5.2, 5.32, 0.03, 6, side='e_candle', top='e_candle', bottom='e_candle'))
    for p in (6.6, 9.4):
        for (x, y) in ((p, I0 + 0.08), (I0 + 0.08, p), (I1 - 0.08, p)):
            R.light(cyl(x, y, 2.3, 2.5, 0.08, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    loop(R, [(1.5, 1.5), (8, 1.5), (14.5, 1.5), (14.5, 8), (8.4, 13.0), (8, 14.5), (1.5, 14.5), (1.5, 8)])
    R.link(R.navpt(8, 1.5), R.navpt(8, 8), R.navpt(8, 14.5))
    R.link(R.navpt(1.5, 8), R.navpt(8, 8), R.navpt(14.5, 8))
    R.spot('probe', 8, 7.0, 1.7)
    R.spot('read', 4.0, 3.0, 0.44, math.pi / 2)
    R.meta.update(label='The Study', weight=6,
                  blurb='A fire, a deep chair, a lamp on the desk: everything a study should have, spread across a room the size of a church. The fire has been lit for you.')
    return R
