"""The Mill Race: a channel of dark water runs through the middle of this hall from a culvert in the south
wall to one in the north, and in the middle of it turns a great undershot wheel whose paddles are
bookcases, still full, the books wet through. Two stone bridges cross the race. The wheel's axle goes
into a little stone mill house on the east bank; its door is on the water side, behind the wheel, off a
ledge you only find by walking where the wheel nearly touches you."""
from kit_h12 import *

W = D = 32.0
X0, X1 = 12.0, 17.0            # the race
WT, WB, PB = -0.3, -1.5, -1.9  # water top, the race's bed, the wheel pit
WX0, WX1 = 13.15, 15.95        # the wheel's rims
WY, WZ, WR = 16.0, 3.2, 4.2    # its axle, height, radius
HX0, HX1, HY0, HY1 = 17.0, 21.5, 12.5, 19.5    # the mill house
LX0 = 16.2                      # the ledge behind the wheel (x LX0..X1)
LY0, LY1 = 11.0, 21.0


def make():
    R = Room('waterwheel', 2, 2, res=2048)
    rs = rng(56)
    R.sockets(floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP - 0.1, 'tile', bottom='floor', top='plaster'))
    race(R)
    bridges(R)
    wheel_(R, rs)
    mill(R, rs)
    walls(R, rs)
    lamps(R)
    fx(R, 'dust', [X0 - 2, 10.0, 0.0, X1 + 1, 22.0, 7.0])
    P = {'w1': (1.6, 8.0), 'w2': (1.6, 24.0), 'e1': (30.4, 8.0), 'e2': (30.4, 24.0), 's1': (8.0, 1.6), 's2': (24.0, 1.6),
         'n1': (8.0, 30.4), 'n2': (24.0, 30.4), 'a': (8.0, 6.0), 'b': (8.0, 16.0), 'c': (8.0, 26.0), 'd': (24.0, 6.0), 'e': (24.0, 16.0),
         'f': (24.0, 26.0), 'g': (14.5, 6.0), 'h': (14.5, 26.0), 'i': (10.8, 16.0), 'j': (23.0, 11.0), 'k': (18.5, 11.0)}
    navgrid(R, P, [('w1', 'a'), ('a', 's1'), ('a', 'b'), ('b', 'c'), ('c', 'n1'), ('c', 'w2'), ('a', 'g'), ('g', 'd'), ('c', 'h'), ('h', 'f'),
                   ('d', 's2'), ('d', 'e1'), ('d', 'j'), ('j', 'e'), ('e', 'f'), ('f', 'n2'), ('f', 'e2'), ('b', 'i'), ('j', 'k')])
    secret(R, 19.2, 16.0, 0.0, 'The Mill House',
           'Behind the wheel, off a ledge the paddles nearly brush, the mill house door. Inside, the axle turns a pair of stones that grind nothing; a sack by the wall is full of loose letters, all the ones the water washed out of the books.', r=2.0)
    return finish(R, 'The Mill Race', weight=3, probe=(8.0, 16.0, 2.2), bot=PB,
                  blurb='The wheel turns, and the shelves on it go down into the water full and come up full and dripping, and none of the books is ever taken out. There is a smell of wet paper and of rivers.')


def race(R):
    """The channel: a bed at WB, a stepped pit under the wheel, culverts at both ends, stone copings,
    rails along both edges (except the bathing steps and the gap onto the ledge), the water."""
    R.cut(box(X0, T - 0.3, WB, X1, D - T + 0.3, 0.02, 'tile', bottom='slate'))
    R.cut(box(X0 + 0.3, WY - 5.0, WB - 0.2, X1 - 0.3, WY + 5.0, WB, 'tile', bottom='slate'))
    R.cut(box(X0 + 0.6, WY - 4.6, PB, X1 - 0.6, WY + 4.6, WB - 0.2, 'tile', bottom='slate'))
    # the culverts: dark arches where the water comes in and goes out
    pr = arch_profile((X0 + X1) / 2, X1 - X0, WB, 1.6, 16)
    for (a0, a1) in ((-0.1, T + 0.02), (D - T - 0.02, D + 0.1)):
        R.cut(prism(pr, 'y', a0, a1, ['slate'] * len(pr), cap='slate'))
    for y in (T - 0.08, D - T + 0.08):
        R.nocol.add(box(X0, y - 0.02, WB, X1, y + 0.02, 1.6 + WB + 2.5, 'black', skip=('-z',)))
    # the water
    for (y0, y1, bot) in ((T, WY - 5.0, WB), (WY - 5.0, WY + 5.0, PB), (WY + 5.0, D - T, WB)):
        R.water.append(dict(x0=X0, y0=y0, x1=X1, y1=y1, top=WT, bot=bot))
    R.meta['water_tint'] = [0.05, 0.1, 0.09]
    # copings
    for x in (X0, X1):
        R.parts.add(box(x - 0.25, T, -0.12, x + 0.25, D - T, 0.08, 'tile', top='slate'))
    # bathing steps: south-west corner going down north, north-east corner going down south
    for (x0, y0, ax) in ((X0, 1.2, '+y'), (X1 - 1.4, D - 1.2, '-y')):
        n = 5
        for k in range(n):
            z = -0.3 * (k + 1)
            if ax == '+y': R.parts.add(box(x0, y0 + k * 0.4, WB, x0 + 1.4, y0 + (k + 1) * 0.4, z + 0.3 - 0.0, 'tile'))
            else: R.parts.add(box(x0, y0 - (k + 1) * 0.4, WB, x0 + 1.4, y0 - k * 0.4, z + 0.3, 'tile'))
    # rails
    gaps_w = [(1.0, 2.4)]
    gaps_e = [(D - 2.4, D - 1.0), (LY0, HY1)]
    for (x, gaps, s) in ((X0 - 0.12, gaps_w, -1), (X1 + 0.12, gaps_e, 1)):
        ys = [T + 0.1]
        for (a, b) in sorted(gaps): ys += [a, b]
        ys.append(D - T - 0.1)
        for k in range(0, len(ys), 2):
            a, b = ys[k], ys[k + 1]
            # the bridges interrupt the rails
            for (c0, c1) in ((a, b),):
                segs = [(c0, c1)]
                for (bb0, bb1) in ((4.75, 7.25), (24.75, 27.25)):
                    segs2 = []
                    for (u0, u1) in segs:
                        if u1 <= bb0 or u0 >= bb1: segs2.append((u0, u1))
                        else:
                            if u0 < bb0: segs2.append((u0, bb0))
                            if u1 > bb1: segs2.append((bb1, u1))
                    segs = segs2
                for (u0, u1) in segs:
                    if u1 - u0 > 0.2: brass_rail(R, x, u0, x, u1, 0.08, h=0.95)


def bridges(R):
    """Two stone bridges over the race, with parapets."""
    for yc in (6.0, 26.0):
        y0, y1 = yc - 1.25, yc + 1.25
        R.parts.add(box(X0 - 0.3, y0, -0.35, X1 + 0.3, y1, 0.0, 'tile', top='floor'))
        for y in (y0, y1 - 0.25):
            R.parts.add(box(X0 - 0.3, y, 0.0, X1 + 0.3, y + 0.25, 1.0, 'tile', skip=('-z',)))
            R.parts.add(box(X0 - 0.33, y - 0.03, 1.0, X1 + 0.33, y + 0.28, 1.06, 'brass'))


def wheel_(R, rs):
    """The wheel: two iron-bound oak rims, spokes, a hub on an iron axle, and twelve bookcase paddles
    between the rims, turning (drawn only; the race's rails keep people off it)."""
    M = R.mover('spin', pivot=(0.0, WY, WZ), axis='x', speed=-0.14)
    for x in (WX0, WX1):
        M.nocol.add(wheel(x, WY, WZ, WR, axis='x', spokes=12, rim=0.28, w=0.16, m='oak', hub='iron', segs=40))
        M.nocol.add(wheel(x + (0.09 if x > 15 else -0.09), WY, WZ, WR + 0.02, axis='x', spokes=0, rim=0.06, w=0.03, m='iron', hub='iron', segs=40))
    M.nocol.add(solid_tube((WX0 - 0.1, WY, WZ), (WX1 + 0.1, WY, WZ), 0.45, 'oak', 14))
    n = 12
    for k in range(n):
        th = 2 * math.pi * k / n
        cs = fake_case(rs, WX1 - WX0 - 0.16, 3, row_h=0.38, depth=0.3, frame='walnut', top=True)
        # stand it on the rim: its height along the radius (from r 2.9 outward), its face toward the turn
        u = (math.cos(th), math.sin(th)); v = (-math.sin(th), math.cos(th))
        cs.v = [(WX0 + 0.08 + x, WY + (2.95 + z) * u[0] + (y - 0.15) * v[0], WZ + (2.95 + z) * u[1] + (y - 0.15) * v[1]) for (x, y, z) in cs.v]
        M.nocol.add(cs)
    # the axle: iron, from beyond the west rim into the mill house wall, on a stone pier to the west
    R.nocol.add(solid_tube((X0 + 0.4, WY, WZ), (HX0 + 0.4, WY, WZ), 0.16, 'iron', 12))
    # an iron A-frame carrying the west end of the axle, its feet in the race
    for s in (-1, 1):
        R.nocol.add(beam((X0 + 0.35, WY + s * 1.4, WB), (X0 + 0.35, WY + s * 0.12, WZ - 0.15), 0.16, 'iron'))
    R.nocol.add(box(X0 + 0.15, WY - 0.3, WZ - 0.3, X0 + 0.55, WY + 0.3, WZ - 0.12, 'iron'))
    R.nocol.add(beam((X0 + 0.35, WY - 1.0, 0.9), (X0 + 0.35, WY + 1.0, 0.9), 0.1, 'iron'))
    # the ledge behind the wheel, against the mill house (and past it both ways)
    R.parts.add(box(LX0, LY0, WB, X1, LY1, -0.08, 'tile', top='slate'))


def mill(R, rs):
    """The mill house: a stone house on the east bank with a pitched roof; its door faces the race, off the
    ledge. Inside, the axle turns a pit wheel; the pit wheel turns a wallower and the runner stone."""
    t = 0.3
    Hh = 4.6
    for bx in ((HX0, HY0, HX0 + t, 15.0), (HX0, 16.2, HX0 + t, HY1), (HX1 - t, HY0, HX1, HY1), (HX0, HY0, HX1, HY0 + t), (HX0, HY1 - t, HX1, HY1)):
        R.parts.add(box(bx[0], bx[1], 0, bx[2], bx[3], Hh, 'tile', skip=('-z',)))
    R.parts.add(box(HX0, 15.0, 2.3, HX0 + t, 16.2, Hh, 'tile'))
    R.parts.add(box(HX0 - 0.1, HY0 - 0.1, Hh, HX1 + 0.1, HY1 + 0.1, Hh + 0.2, 'walnut', bottom='plaster'))
    # a pitched roof (ridge along y)
    pr = [(HX0 - 0.3, Hh + 0.2), (HX1 + 0.3, Hh + 0.2), ((HX0 + HX1) / 2, Hh + 1.9)]
    R.nocol.add(prism(pr, 'y', HY0 - 0.3, HY1 + 0.3, ['walnut', 'slate', 'slate'], cap='tile'))
    R.nocol.add(box(HX0 - 0.1, 14.9, 2.3, HX0 + 0.02, 16.3, 2.45, 'walnut'))
    R.nocol.add(frame_rect('x', HX0, 15.0, 16.2, 0.0, 2.3, -1, w=0.1, d=0.05, m='walnut'))
    R.light(sphere(HX0 - 0.3, 16.7, 2.5, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(box(HX0 - 0.3, 16.66, 2.55, HX0, 16.74, 2.6, 'iron'))
    # windows in the east wall (dim light from nowhere)
    for y in (14.0, 18.0):
        R.nocol.add(box(HX1 + 0.01, y - 0.5, 2.0, HX1 + 0.03, y + 0.5, 3.2, 'black'))
    # inside: the axle through the wall, the pit wheel turning with the wheel
    R.nocol.add(solid_tube((HX0, WY, WZ), (HX0 + 1.6, WY, WZ), 0.16, 'iron', 12))
    M = R.mover('spin', pivot=(0.0, WY, WZ), axis='x', speed=-0.14)
    M.nocol.add(gear(HX0 + 1.3, WY, WZ, 1.15, 24, axis='x', w=0.18, m='oak', spokes=6))
    # the wallower (a horizontal gear) on an upright shaft, and the runner stone, turning about z
    sx, sy = HX0 + 1.3 + 1.2, WY
    M2 = R.mover('spin', pivot=(sx, sy, 0), axis='z', speed=0.35)
    wg = Geo()
    wg.add(ring(sx, sy, WZ - 0.25, WZ - 0.1, 0.35, 0.6, 16, top='oak', bottom='oak', inner='oak', outer='oak'))
    for k in range(12):
        a = 2 * math.pi * k / 12
        wg.add(box(sx + math.cos(a) * 0.6 - 0.04, sy + math.sin(a) * 0.6 - 0.04, WZ - 0.1, sx + math.cos(a) * 0.6 + 0.04, sy + math.sin(a) * 0.6 + 0.04, WZ + 0.05, 'oak'))
    wg.add(cyl(sx, sy, 0.95, Hh, 0.1, 10, side='oak', caps=False))
    wg.add(cyl(sx, sy, 0.75, 0.95, 0.7, 20, side='tile', top='tile', bottom='tile'))
    M2.nocol.add(wg)
    R.parts.add(cyl(sx, sy, 0, 0.72, 0.85, 20, side='walnut', top='tile'))
    R.parts.add(cyl(sx, sy, 0.72, 0.75, 0.75, 20, side='tile', top='tile'))
    # a hopper over the stones, a sack of letters, a desk with the ledger
    R.nocol.add(frustum(sx, sy, 1.2, 1.7, 0.12, 0.45, 10, 'oak', inner='oak'))
    for (x, y) in ((HX1 - 0.6, HY0 + 0.7), (HX1 - 1.2, HY0 + 0.6), (HX1 - 0.6, HY0 + 1.3)):
        R.parts.add(cyl(x, y, 0, 0.7, 0.28, 10, side='bed', top='bed'))
    for _ in range(40):
        x, y = HX1 - rs.uniform(0.4, 1.8), HY0 + rs.uniform(0.4, 2.0)
        R.nocol.add(box(x, y, 0.004, x + 0.05, y + 0.06, 0.008, 'ivory').xform(rs.uniform(0, 3), 0, 0, 0))
    R.parts.add(table_geo(HX1 - 1.2, HY1 - 1.3, HX1 - 0.4, HY1 - 0.4, 0.78, 'walnut', top='leather'))
    open_book(R, HX1 - 0.8, HY1 - 0.85, 0.78, math.pi)
    R.parts.add(stool(HX1 - 0.8, HY1 - 1.7, math.pi / 2, back=False))
    R.light(sphere(19.5, 18.0, 3.4, 0.08, 8, 4, 'e_candle'))
    R.nocol.add(cyl(19.5, 18.0, 3.46, Hh, 0.01, 4, side='iron', caps=False))
    R.spot('plaque', HX1 - 0.8, HY1 - 0.85, 0.0, math.pi / 2,
           text='The miller\'s ledger. Every day the same entry: Ground nothing. Water high. Still turning.')


def walls(R, rs):
    segs = [(0.8, 6.2), (9.8, 11.3), (17.8, 22.2), (25.8, W - 0.8)]
    for (a, b) in segs:
        sh(R, '+y', T, a, b, rows=9, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=9, frame='walnut')
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, D - 0.8)):
        sh(R, '+x', T, a, b, rows=9, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=9, frame='walnut')
    # clerestory windows over the side cases
    for y in (4.0, 12.0, 20.0, 28.0):
        for (x, s) in ((T, 1), (W - T, -1)):
            R.cut(box(min(x, x - s * 0.3), y - 1.2, 4.6, max(x, x - s * 0.3) + (0.02 if s > 0 else 0), y + 1.2, 7.0, 'tile'))
            xw = x - s * 0.28
            R.light(box(min(xw, xw + 0.02), y - 1.2, 4.6, max(xw, xw + 0.02), y + 1.2, 7.0, 'e_sky'))
            for k in (-1, 0, 1):
                R.nocol.add(box(min(x, x - s * 0.25), y + k * 0.6 - 0.03, 4.6, max(x, x - s * 0.25), y + k * 0.6 + 0.03, 7.0, 'iron'))
    # reading tables on both banks, away from the race
    for (x0, x1) in ((3.0, 9.5), (22.5, 29.0)):
        for yc in (12.0, 20.0):
            reading_table(R, x0 + 0.5, yc - 0.5, x1 - 0.5, yc + 0.5, lamps=3, chairs=True)


def lamps(R):
    for y in (3.0, 10.0, 22.0, 29.0):
        for x in (X0 - 0.6, X1 + 0.6):
            lamp_post(R, x, y, 0.0, h=2.8)
    for (x, y) in ((6.0, 6.0), (26.0, 6.0), (6.0, 26.0), (26.0, 26.0), (6.0, 16.0), (26.0, 16.0)):
        pendant(R, x, y, 3.8, TOP - 0.1, r=0.24)
