"""The Stepped Hall: the floor goes down in long terraces toward the middle of the hall, a metre and
a half, and comes up again the other side. Every riser is a shelf of books. Reading tables at the bottom."""
from lib import *
from kit_e import *


def make():
    R = Room('steppedhall', 2, 1, res=1024)
    R.sockets()
    W, D = R.W, R.D
    cy = D / 2
    H = 7.2
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='floor', top='plaster'))
    # coffers, and a long lantern over the pit
    for k in range(8):
        x = 2.0 + 4.0 * k
        for y in (2.0, D - 2.0):
            R.cut(box(x - 1.5, y - 1.3, H - 0.05, x + 1.5, y + 1.3, H + 0.3, 'plaster'))
    R.cut(box(4.0, cy - 3.4, H - 0.05, W - 4.0, cy + 3.4, R.hi + 0.5, 'plaster'))
    for k in range(6):
        x = 6.0 + 4.0 * k
        R.light(box(x - 1.7, cy - 3.2, R.hi - 0.09, x + 1.7, cy + 3.2, R.hi - 0.05, 'e_sky'))
    for k in range(7):
        x = 4.0 + 4.0 * k
        R.parts.add(box(x - 0.15, cy - 3.4, H - 0.05, x + 0.15, cy + 3.4, R.hi, 'plaster'))
    # the terraces: three steps of 0.5 m, each 1.3 m wide
    x0, y0, x1, y1 = 2.6, 2.6, W - 2.6, D - 2.6
    step, rise, n = 1.3, 0.5, 3
    for k in range(n):
        i = k * step
        R.cut(box(x0 + i, y0 + i, -(k + 1) * rise, x1 - i, y1 - i, 0.2, 'tile', bottom='terrazzo' if k == n - 1 else 'floor'))
    bot = -n * rise
    # every riser is a low bookcase (except where the little stairs come down)
    gaps_x = ((15.2, 16.8),)
    gaps_y = ((7.3, 8.7),)
    for k in range(n):
        i = k * step
        z = -(k + 1) * rise
        xa, xb, ya, yb = x0 + i, x1 - i, y0 + i, y1 - i
        runs = [(xa + 0.02, gaps_x[0][0]), (gaps_x[0][1], xb - 0.02)]
        for (a, b) in runs:
            R.shelf(a, ya, z, b - a, '+y', rows=1, row_h=0.38, top_gap=0.06, frame='walnut', crown=False, sides=False)
            R.shelf(b, yb, z, b - a, '-y', rows=1, row_h=0.38, top_gap=0.06, frame='walnut', crown=False, sides=False)
        for (a, b) in ((ya + 0.36, gaps_y[0][0]), (gaps_y[0][1], yb - 0.36)):
            R.shelf(xa, b, z, b - a, '+x', rows=1, row_h=0.38, top_gap=0.06, frame='walnut', crown=False, sides=False)
            R.shelf(xb, a, z, b - a, '-x', rows=1, row_h=0.38, top_gap=0.06, frame='walnut', crown=False, sides=False)
    for k in range(n):
        i = k * step
        ztop = -k * rise
        xa, xb, ya, yb = x0 + i, x1 - i, y0 + i, y1 - i
        # a flight goes down from ztop to ztop - rise: two steps of 0.25
        R.nocol.add(stairs(15.2, ya + 0.64, ztop - rise, 1.6, 2, rise / 2, 0.32, '-y', m='terrazzo', side='tile'))
        R.nocol.add(stairs(15.2, yb - 0.64, ztop - rise, 1.6, 2, rise / 2, 0.32, '+y', m='terrazzo', side='tile'))
        R.nocol.add(stairs(xa + 0.64, 7.3, ztop - rise, 1.4, 2, rise / 2, 0.32, '-x', m='terrazzo', side='tile'))
        R.nocol.add(stairs(xb - 0.64, 7.3, ztop - rise, 1.4, 2, rise / 2, 0.32, '+x', m='terrazzo', side='tile'))
        # warm step lights along the risers (they stay on at night)
        for x in (6.0, 10.0, 22.0, 26.0):
            if xa + 0.5 < x < xb - 0.5:
                R.light(box(x - 0.3, ya - 0.02 + 0.345, ztop - 0.07, x + 0.3, ya + 0.36, ztop - 0.03, 'e_pool'))
                R.light(box(x - 0.3, yb - 0.36, ztop - 0.07, x + 0.3, yb + 0.02 - 0.345, ztop - 0.03, 'e_pool'))
    # reading tables down the bottom terrace, a gap at the middle
    for (xa, xb) in ((7.0, 14.6), (17.4, 25.0)):
        table(R, xa, cy - 0.5, xb, cy + 0.5, m='walnut', top='leather', z=bot)
        nc = 6
        for j in range(nc):
            x = xa + 0.6 + j * (xb - xa - 1.2) / (nc - 1)
            chair(R, x, cy - 0.95, math.pi / 2, z=bot)
            chair(R, x, cy + 0.95, -math.pi / 2, z=bot)
        for x in (xa + 1.8, xb - 1.8):
            table_lamp(R, x, cy, bot + 0.76)
    # books on the walls round the upper walk
    wall_shelves(R, rows=12, frame='walnut')
    for x in (9.0, 12.6, 19.4, 23.0):
        pendant(R, x, cy, bot + 2.5, H, r=0.3)
    # walkers: round the top, down the middle stairs, round the bottom
    top = loop(R, [(1.4, 1.4), (8.0, 1.4), (16.0, 1.4), (24.0, 1.4), (W - 1.4, 1.4), (W - 1.4, cy), (W - 1.4, D - 1.4), (24.0, D - 1.4), (16.0, D - 1.4),
                   (8.0, D - 1.4), (1.4, D - 1.4), (1.4, cy)])
    b = loop(R, [(6.2, 6.2, bot), (16.0, 6.2, bot), (25.8, 6.2, bot), (25.8, cy, bot), (25.8, D - 6.2, bot), (16.0, D - 6.2, bot), (6.2, D - 6.2, bot), (6.2, cy, bot)])
    R.link(top[2], b[1]); R.link(top[8], b[5]); R.link(top[11], b[7]); R.link(top[5], b[3])
    R.spot('probe', 16.0, cy, 1.0)
    R.meta.update(label='The Stepped Hall', weight=6,
                  blurb='The floor steps down toward the middle of the hall, shelf by shelf, and up again the other side. The reading tables are at the bottom, where the quiet collects.')
    R.meta['box'] = [[T, bot, T], [W - T, R.hi, D - T]]
    return R
