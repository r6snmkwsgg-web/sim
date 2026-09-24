"""The Benches: a tall plain hall full of pews, every one facing a great blank screen wall with a
single green exit sign on it, over no door. Hymn-book racks on the backs of the pews."""
from lib import *
from kit_d import *


def pew(R, x0, x1, y, books=True):
    """A pew along x, its front edge at y, facing +y (towards the blank wall)."""
    d = 0.5
    R.parts.add(box(x0, y - d, 0.28, x1, y, 0.46, 'walnut'))                 # seat
    R.parts.add(box(x0, y - d, 0.46, x1, y - d + 0.07, 0.98, 'walnut'))      # back
    R.parts.add(box(x0, y - d, 0.98, x1, y - d + 0.1, 1.02, 'walnut'))       # back rail
    for xe in (x0, x1 - 0.07):                                              # ends
        R.parts.add(box(xe, y - d - 0.02, 0, xe + 0.07, y + 0.02, 1.05, 'walnut', skip=('-z',)))
    if books:   # a book rack on the back, for the row behind
        R.shelf(x1 - 0.08, y - d, 0.62, x1 - x0 - 0.16, '-y', rows=1, row_h=0.26, depth=0.14, frame='walnut', crown=False)
    n = int((x1 - x0) / 0.7)
    for k in range(n):
        R.spot('sit', x0 + 0.35 + k * (x1 - x0) / n, y - 0.25, 0.46, math.pi / 2)


def make():
    R = Room('benches', 1, 1, res=1024)
    shell(R, TOP, floor='floor', wall='green', top='plaster')
    # the screen: a blank wall across the room, 6 m tall, free on both ends
    sy0, sy1 = 12.2, 12.7
    R.parts.add(box(2.6, sy0, 0, 13.4, sy1, 6.2, 'ivory', top='tile'))
    R.parts.add(box(2.5, sy0 - 0.05, 0, 13.5, sy1 + 0.05, 0.25, 'tile'))              # plinth
    R.parts.add(box(2.5, sy0 - 0.06, 6.2, 13.5, sy1 + 0.06, 6.35, 'tile'))           # coping
    exit_sign(R, 8, sy0, 2.75, '-y', w=0.7, h=0.26)
    # its back is all bookcases, facing the north door
    wall_shelf(R, '+y', 2.8, 7.9, 0, rows=13, off=sy1, frame='oak')
    wall_shelf(R, '+y', 8.1, 13.2, 0, rows=13, off=sy1, frame='oak')
    # pews, in two blocks, with a centre aisle and a cross aisle to the side doors
    rows = (1.7, 3.0, 4.3, 5.6, 10.0, 11.3)
    for y in rows:
        pew(R, 1.5, 6.6, y)
        pew(R, 9.4, 14.5, y)
    # tall bookcases down the side walls, clear of the side doors
    for (a, b) in ((0.8, 6.0), (10.0, 15.2)):
        wall_shelf(R, '+x', a, b, 0, rows=14, frame='oak')
        wall_shelf(R, '-x', a, b, 0, rows=14, frame='oak')
    # a row of hanging lamps over each aisle, and a wash of light on the blank wall
    for y in (2.4, 4.6, 8.0, 10.6):
        for x in (3.9, 12.1):
            pendant(R, x, y, 3.6, r=0.2)
    for x in (4.0, 6.0, 8.0, 10.0, 12.0):
        R.light(box(x - 0.6, 10.9, TOP - 0.1, x + 0.6, 11.3, TOP - 0.08, 'e_panel'))
    for x in (2.2, 13.8):
        R.light(cyl(x, 14.2, TOP - 0.1, TOP - 0.07, 0.4, 16, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # candles on the pew ends by the aisle, for the night
    for y in rows:
        for x in (6.55, 9.45):
            R.light(cyl(x, y - 0.25, 1.05, 1.17, 0.025, 8, side='e_candle', top='e_candle', bottom='e_candle'))
    loop(R, [(8, 1.3), (8, 8), (8, 11.6), (1.5, 11.6), (1.5, 14.6), (14.5, 14.6), (14.5, 11.6), (8, 11.6)], close=False)
    loop(R, [(1.5, 8), (14.5, 8)], close=False)
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Benches', weight=4,
                  blurb='Everyone here is facing the same blank wall and the one green sign on it. You sit down to wait, like everyone else.')
    return R
