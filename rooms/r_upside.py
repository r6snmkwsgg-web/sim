"""The Upside-Down Room: a reading room fixed to the ceiling, bookcases, a long table, chairs and
the rug all hanging head-down; the chandelier stands up from the floor like a plant."""
from lib import *
from kit_a import *

H = 5.4


def flip(g, h=H):
    """Mirror a piece top to bottom about the room's mid-height (so things made for the floor sit on the ceiling)."""
    g.v = [(x, y, h - z) for x, y, z in g.v]
    g.f = [tuple(reversed(f)) for f in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    return g


def make():
    R = Room('upside', 1, 1, res=1024)
    shell(R, wall='damask', floor='plaster', ceil='floor', h=H)
    # skirting at the top of the walls, cornice at the bottom
    for (a, b) in ((T, 6.45), (9.55, C - T)):
        for (x0, y0, x1, y1) in ((a, T, b, T + 0.04), (a, C - T - 0.04, b, C - T), (T, a, T + 0.04, b), (C - T - 0.04, a, C - T, b)):
            R.parts.add(box(x0, y0, 0, x1, y1, 0.2, 'ivory', skip=('-z',)))
    for (x0, y0, x1, y1) in ((T, T, C - T, T + 0.04), (T, C - T - 0.04, C - T, C - T), (T, T, T + 0.04, C - T), (C - T - 0.04, T, C - T, C - T)):
        R.parts.add(box(x0, y0, H - 0.22, x1, y1, H, 'walnut'))
        R.parts.add(box(x0, y0, H - 1.1, x1, y1, H - 1.06, 'oak'))   # a dado rail, upside down
    # bookcases hanging from the ceiling round the walls
    for (a, b) in ((0.6, 6.2), (9.8, C - 0.6)):
        inv_shelf(R, a, T, H, b - a, '+y', rows=6, frame='walnut')
        inv_shelf(R, b, C - T, H, b - a, '-y', rows=6, frame='walnut')
        inv_shelf(R, T, b, H, b - a, '+x', rows=6, frame='walnut')
        inv_shelf(R, C - T, a, H, b - a, '-x', rows=6, frame='walnut')
    # the rug, the long table and its chairs, all on the ceiling
    R.parts.add(box(4.2, 5.6, H - 0.018, 11.8, 10.4, H, 'carpet'))
    tb = table(5.2, 7.35, 10.8, 8.65, 0.78, 'walnut', top='leather')
    R.parts.add(flip(tb))
    for x in (5.9, 7.3, 8.7, 10.1):
        for s in (-1, 1):
            R.parts.add(flip(chair(x, 8.0 + s * 1.05, -s * math.pi / 2, frame='walnut', seat='velvet')))
    for x in (4.6, 11.4):
        R.parts.add(flip(chair(x, 8.0, 0 if x < 8 else math.pi, frame='walnut', seat='velvet')))
    # things left lying on the table, stuck there: books, an inkwell, a lamp that shines up at you
    zt = H - 0.78
    for (x, y, a, c) in ((6.2, 7.7, 0.3, 'oxblood'), (6.35, 7.72, 0.25, 'green'), (9.4, 8.3, -0.5, 'leather')):
        R.parts.add(flip(box(-0.13, -0.09, 0.78, 0.13, 0.09, 0.82, c).xform(a, x, y, 0)))
    R.parts.add(cyl(8.0, 8.1, zt - 0.08, zt, 0.05, 10, side='black', top='black', bottom='black'))
    lx, ly = 7.2, 7.85
    R.parts.add(cyl(lx, ly, zt - 0.03, zt, 0.08, 12, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(lx, ly, zt - 0.36, zt - 0.03, 0.012, 6, side='brass', caps=False))
    R.parts.add(obox(lx - 0.17, ly, lx + 0.17, ly, zt - 0.44, zt - 0.36, 0.13, 'green'))
    R.light(obox(lx - 0.15, ly, lx + 0.15, ly, zt - 0.36, zt - 0.345, 0.09, 'e_lamp'))
    # the chandelier, standing up from a rose in the floor: its chain rises, its arms droop, its candles
    # burn downward
    cx, cy = 8.0, 8.0
    R.parts.add(cyl(cx, cy, 0, 0.06, 0.5, 24, side='ivory', top='ivory'))
    R.parts.add(ring(cx, cy, 0, 0.1, 0.5, 0.62, 24, top='ivory', bottom='ivory', inner='ivory', outer='ivory'))
    R.parts.add(cyl(cx, cy, 0.06, 2.0, 0.03, 8, side='brass', caps=False))
    for k in range(7):
        R.nocol.add(ring(cx, cy, 0.18 + k * 0.24, 0.24 + k * 0.24, 0.02, 0.06, 8, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.nocol.add(sphere(cx, cy, 2.2, 0.3, 16, 8, 'brass'))
    R.nocol.add(cyl(cx, cy, 2.45, 2.9, 0.05, 8, side='brass', top='brass'))
    R.nocol.add(sphere(cx, cy, 2.95, 0.09, 10, 5, 'brass'))
    for (zr, rr, n, cl) in ((2.05, 0.95, 10, 0.3), (2.55, 0.55, 6, 0.24)):
        for k in range(n):
            a = k * 2 * math.pi / n + (0.3 if n == 6 else 0)
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            mx, my = cx + rr * 0.55 * math.cos(a), cy + rr * 0.55 * math.sin(a)
            R.nocol.add(beam((cx + 0.2 * math.cos(a), cy + 0.2 * math.sin(a), zr + 0.15), (mx, my, zr + 0.25), 0.03, 'brass'))
            R.nocol.add(beam((mx, my, zr + 0.25), (x, y, zr), 0.03, 'brass'))
            R.nocol.add(cyl(x, y, zr - 0.05, zr, 0.065, 10, side='brass', top='brass', bottom='brass'))
            R.nocol.add(cyl(x, y, zr - 0.05 - cl, zr - 0.05, 0.022, 6, side='ivory', bottom='ivory'))
            R.light(box(x - 0.018, y - 0.018, zr - 0.13 - cl, x + 0.018, y + 0.018, zr - 0.06 - cl, 'e_candle'))
            R.nocol.add(cyl(x, y, zr + 0.02, zr + 0.3, 0.01, 4, side='chrome', caps=False))   # crystal drops, hanging up
    R.col.add(cyl(cx, cy, 0, 3.0, 1.0, 8, side='tile', top='tile', bottom='tile'))
    R.light(sphere(cx, cy, 1.75, 0.16, 10, 5, 'e_lamp'))
    # the floor is dressed as a ceiling: a moulded border and a ring of plaster round the rose
    for (x0, y0, x1, y1) in ((2.2, 2.2, 13.8, 2.3), (2.2, 13.7, 13.8, 13.8), (2.2, 2.3, 2.3, 13.7), (13.7, 2.3, 13.8, 13.7)):
        R.parts.add(box(x0, y0, 0, x1, y1, 0.03, 'ivory', skip=('-z',)))
    R.parts.add(ring(cx, cy, 0, 0.03, 2.3, 2.42, 40, top='ivory', bottom='ivory', inner='ivory', outer='ivory'))
    # two standing lamps, standing on the ceiling, shining up into the furniture
    for (x, y) in ((4.6, 6.6), (11.4, 9.4)):
        save = (R.parts, R.nocol, R.emit, R.col)
        R.parts, R.nocol, R.emit, R.col = Geo(), Geo(), Geo(), Geo()
        floor_lamp(R, x, y, 1.9, m='e_lamp', scale=1.0)
        g = (R.parts, R.nocol, R.emit, R.col)
        R.parts, R.nocol, R.emit, R.col = save
        R.parts.add(flip(g[0])); R.nocol.add(flip(g[1])); R.emit.add(flip(g[2])); R.col.add(flip(g[3]))
    # wall sconces, upside down, shining down the walls
    for (x, y) in ((T + 0.12, 3.4), (T + 0.12, 12.6), (C - T - 0.12, 3.4), (C - T - 0.12, 12.6), (3.4, T + 0.12), (12.6, T + 0.12), (3.4, C - T - 0.12), (12.6, C - T - 0.12)):
        R.parts.add(box(x - 0.06, y - 0.06, 2.15, x + 0.06, y + 0.06, 2.4, 'brass'))
        R.light(cyl(x, y, 1.95, 2.15, 0.08, 10, side='e_amber', top='e_amber', bottom='e_amber'))
    # a painting hung upside down over the south door, and another opposite
    for (y0, y1) in ((T, T + 0.05), (C - T - 0.05, C - T)):
        R.parts.add(box(6.6, y0, 4.4, 9.4, y1, 5.1, 'gilt'))
    R.parts.add(box(6.72, T + 0.05, 4.5, 9.28, T + 0.06, 5.0, 'green'))
    R.parts.add(box(6.72, C - T - 0.06, 4.5, 9.28, C - T - 0.05, 5.0, 'oxblood'))
    navloop(R, [(2.0, 2.0), (8, 2.0), (14.0, 2.0), (14.0, 8), (14.0, 14.0), (8, 14.0), (2.0, 14.0), (2.0, 8)])
    a, b = R.navpt(5.5, 8.0), R.navpt(10.5, 8.0)
    R.link(7, a); R.link(b, 3); R.link(a, 1); R.link(b, 5)
    R.spot('probe', 8, 5.2, 1.7)
    R.meta.update(label='The Upside-Down Room', weight=3,
                  blurb='Someone has furnished the ceiling. The books stay on their shelves out of politeness. Try not to look up for too long.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
