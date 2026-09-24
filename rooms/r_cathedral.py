"""The Cathedral: a nave and a transept under pointed vaults fifteen metres up, crossing in a groin.
A rose window of stained glass burns at the north end over rows of pews; twin stairs climb the nave
to an organ loft with no organ, which joins the galleries over the aisles. Books in the aisles."""
from lib import *
from kit_f import *


def make():
    R = Room('cathedral', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    c = W / 2
    # nave (north-south) and transept (east-west): pointed vaults, crown at 15 m
    pr = pointed_profile(c, 12.0, 0.0, 8.5, 6.5, 14)
    mats = ['terrazzo', 'tile'] + ['plaster'] * (len(pr) - 3) + ['tile']
    R.cut(prism(pr, 'y', T - 0.02, W - T + 0.02, mats))
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, mats))
    q0, q1 = 9.4, W - 9.4            # the aisles (four corner quadrants) and their walls
    def quads(fn):
        for (sx, sy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            fn(sx, sy, (lambda x: W - x if sx else x), (lambda y: W - y if sy else y))
    def aisle(sx, sy, X, Y):
        xa, xb = sorted((X(T - 0.02), X(q0))); ya, yb = sorted((Y(T - 0.02), Y(q0)))
        R.cut(box(xa, ya, 0, xb, yb, 6.8, 'tile', bottom='terrazzo', top='plaster'))        # aisle below
        R.cut(box(xa, ya, LH, xb, yb, 12.6, 'tile', bottom='floor', top='plaster'))         # gallery room above
        # arcade arches from the aisle into the nave and the transept
        for m in (3.0, 7.0):
            p = arch_profile(0, 2.8, 0, 3.4, 16)
            xs = sorted((X(q0 - 0.1), X(10.1)))
            R.cut(prism([(Y(m) + a, b) for a, b in p], 'x', xs[0], xs[1], arch_mats(len(p), 'terrazzo', 'tile')))
            ys = sorted((Y(q0 - 0.1), Y(10.1)))
            R.cut(prism([(X(m) + a, b) for a, b in p], 'y', ys[0], ys[1], arch_mats(len(p), 'terrazzo', 'tile')))
        # triforium arches from the gallery rooms, railed
        p = arch_profile(0, 3.2, LH, 2.1, 16)
        xs = sorted((X(q0 - 0.1), X(10.9)))
        R.cut(prism([(Y(6.3) + a, b) for a, b in p], 'x', xs[0], xs[1], arch_mats(len(p), 'floor', 'tile')))
        balus(R, X(9.7), Y(4.7), X(9.7), Y(7.9), LH)
        ys = sorted((Y(q0 - 0.1), Y(10.9)))
        R.cut(prism([(X(6.3) + a, b) for a, b in p], 'y', ys[0], ys[1], arch_mats(len(p), 'floor', 'tile')))
        balus(R, X(4.7), Y(9.7), X(7.9), Y(9.7), LH)
        # passages from the gallery rooms onto the bridges (west/east bridges; the south loft)
        ys = sorted((Y(q0 - 0.1), Y(10.9))); xs2 = sorted((X(T - 0.02), X(3.4)))
        R.cut(box(xs2[0], ys[0], LH, xs2[1], ys[1], LH + 3.0, 'tile', bottom='floor', top='plaster'))
        if not sy:
            xs = sorted((X(q0 - 0.1), X(10.9))); ys2 = sorted((Y(T - 0.02), Y(3.4)))
            R.cut(box(xs[0], ys2[0], LH, xs[1], ys2[1], LH + 3.0, 'tile', bottom='floor', top='plaster'))
        # books in the aisles and the galleries
        for (z, rows) in ((0, 12), (LH, 9)):
            if sx == 0: R.shelf(T, 6.2 if not sy else W - 0.8, z, 5.4, '+x', rows=rows, frame='walnut')
            else: R.shelf(W - T, 0.8 if not sy else W - 6.2, z, 5.4, '-x', rows=rows, frame='walnut')
            if sy == 0: R.shelf(0.8 if not sx else W - 6.2, T, z, 5.4, '+y', rows=rows, frame='walnut')
            else: R.shelf(6.2 if not sx else W - 0.8, W - T, z, 5.4, '-y', rows=rows, frame='walnut')
        # lamps in the aisle and the gallery room
        for (x, y) in ((4.7, 4.7),):
            lamp(R, X(x), Y(y), 4.6, 0.26, chain=6.8)
            lamp(R, X(x), Y(y), LH + 3.1, 0.22, chain=12.6)
    quads(aisle)
    # the organ loft across the south end of the nave, bridges across the ends of the transept
    deck(R, 10.0, T, 22.0, 3.4, LH, th=0.4)
    for (x0, x1) in ((T, 3.4), (W - 3.4, W - T)):
        deck(R, x0, 10.0, x1, 22.0, LH, th=0.4)
    balus(R, 12.3, 3.3, 19.7, 3.3, LH)
    balus(R, 3.3, 10.0, 3.3, 22.0, LH)
    balus(R, W - 3.3, 10.0, W - 3.3, 22.0, LH)
    # twin stairs up the nave to the loft, their undersides open
    for x0 in (10.2, 19.8):
        flight_thin(R, x0, 15.4, 0.0, 2.0, 40, 0.2, 0.3, '-y', m='terrazzo', side='tile')
        for xr in (x0 + 0.06, x0 + 1.94):
            rail_line(R, xr, 15.4, 0.2, xr, 3.4, LH, h=0.95)
    # pews in the north arm, facing the rose
    for k in range(7):
        y = 23.6 + k * 0.95
        for (x0, x1) in ((10.9, 15.2), (16.8, 21.1)):
            R.parts.add(box(x0, y, 0.42, x1, y + 0.45, 0.47, 'walnut'))
            R.parts.add(box(x0, y - 0.06, 0.2, x1, y, 1.0, 'walnut'))
            for xe in (x0, x1 - 0.06):
                R.parts.add(box(xe, y - 0.06, 0, xe + 0.06, y + 0.45, 1.05, 'walnut', skip=('-z',)))
            if k % 2 == 0:
                R.spot('sit', (x0 + x1) / 2, y + 0.25, 0.47, math.pi / 2)
    # the reading desk at the crossing, a book open on it, candles
    R.parts.add(box(14.4, 19.2, 0, 17.6, 20.4, 0.95, 'tile', skip=('-z',)))
    R.parts.add(box(14.2, 19.0, 0.95, 17.8, 20.6, 1.05, 'tile'))
    R.parts.add(box(15.3, 19.5, 1.05, 16.7, 20.2, 1.12, 'ivory'))
    for x in (14.5, 17.5):
        R.parts.add(cyl(x, 19.8, 1.05, 1.5, 0.05, 8, side='ivory', top='ivory'))
        R.light(sphere(x, 19.8, 1.58, 0.06, 8, 4, 'e_candle'))
    R.spot('read', 16, 18.6, 0, math.pi / 2)
    # the rose window and lancets
    rr = 3.5
    circ = [(c + (rr + 0.2) * math.cos(2 * math.pi * k / 48), 11.2 + (rr + 0.2) * math.sin(2 * math.pi * k / 48)) for k in range(48)]
    R.cut(prism(circ, 'y', W - T - 0.02, W - 0.12, 'tile', cap='black'))
    rose(R, c, W - 0.13, 11.2, rr)
    R.parts.add(upright(ring(0, 0, 0, 0.08, rr - 0.02, rr + 0.3, 48, top='gilt', bottom='gilt', inner='gilt', outer='gilt'), c, W - T + 0.01, 11.2))
    def lancet(x, y, z0, h, w, face, m):
        p = arch_profile(0, w, z0, h, 12)
        if face in ('N', 'S'):
            ya = W - T - 0.02 if face == 'N' else 0.12
            R.cut(prism([(x + a, b) for a, b in p], 'y', ya, ya + T - 0.1, 'tile', cap='black'))
            yy = W - 0.13 if face == 'N' else 0.13
            R.light(prism([(x + a * 0.9, z0 + (b - z0) * 0.97) for a, b in p], 'y', yy - 0.02 if face == 'N' else yy, yy if face == 'N' else yy + 0.02, m, cap=m))
        else:
            xa = W - T - 0.02 if face == 'E' else 0.12
            R.cut(prism([(y + a, b) for a, b in p], 'x', xa, xa + T - 0.1, 'tile', cap='black'))
            xx = W - 0.13 if face == 'E' else 0.13
            R.light(prism([(y + a * 0.9, z0 + (b - z0) * 0.97) for a, b in p], 'x', xx - 0.02 if face == 'E' else xx, xx if face == 'E' else xx + 0.02, m, cap=m))
    for x in (12.4, 19.6):
        lancet(x, 0, 2.6, 4.0, 1.0, 'N', 'e_blue')
    for (x, m) in ((13.0, 'e_sky'), (16.0, 'e_sky'), (19.0, 'e_sky')):
        lancet(x, 0, 9.4, 3.2, 1.1, 'S', m)
    for (y, m) in ((13.2, 'e_blue'), (16.0, 'e_red'), (18.8, 'e_blue')):
        lancet(0, y, 9.4, 3.2, 1.1, 'W', m)
        lancet(0, y, 9.4, 3.2, 1.1, 'E', m)
    R.shelf(18.8, W - T, 0, 5.6, '-y', rows=10, frame='walnut')
    # tall cases on the transept end walls, under the bridges
    R.shelf(T, 21.4, 0, 10.8, '+x', rows=13, frame='walnut')
    R.shelf(W - T, 10.6, 0, 10.8, '-x', rows=13, frame='walnut')
    # ribs across the vaults
    arc = [p for p in pr if p[1] > 8.4]
    for s in (4.2, 7.4, W - 7.4, W - 4.2):
        for axis in ('x', 'y'):
            pts = [((cx - c) * 0.985 + c, (z - 8.5) * 0.985 + 8.5) for (cx, z) in arc]
            for p0, p1 in zip(pts, pts[1:]):
                if axis == 'y': R.nocol.add(bar((p0[0], s, p0[1]), (p1[0], s, p1[1]), 0.3, 0.22, 'tile'))
                else: R.nocol.add(bar((s, p0[0], p0[1]), (s, p1[0], p1[1]), 0.3, 0.22, 'tile'))
    # chandeliers
    chandelier(R, c, 26.5, 8.8, 1.8, n=12, chain=14.9, bulb=0.13, tiers=2)
    chandelier(R, c, c, 10.0, 2.4, n=16, chain=15.0, bulb=0.14, tiers=2)
    chandelier(R, c, 8.0, 9.8, 1.6, n=10, chain=14.9, bulb=0.13, tiers=1)
    # walkers
    loop(R, ((13.5, 5.5), (18.5, 5.5), (18.5, 12.8), (27.5, 12.8), (27.5, 19.2), (18.5, 19.2), (18.5, 22.6), (13.5, 22.6), (13.5, 19.2), (4.5, 19.2), (4.5, 12.8), (13.5, 12.8)))
    loop(R, ((3.0, 5.0), (3.0, 11.5)), close=False)
    loop(R, ((1.9, 5.0), (1.9, 16.0), (1.9, W - 5.0), (5.0, W - 5.0)), z=LH, close=False)
    loop(R, ((5.0, 1.9), (16.0, 1.9), (W - 5.0, 1.9), (W - 1.9, 5.0), (W - 1.9, 16), (W - 1.9, W - 5.0)), z=LH, close=False)
    R.spot('probe', c, 12.5, 4.0)
    R.meta.update(label='The Cathedral', weight=5,
                  blurb='A cathedral, and the light through the rose window is the colour of every sermon you ever slept through. The pews face the glass. There is no altar, only a book.')
    R.meta['box'] = [[T, 0, T], [W - T, 15.0, W - T]]
    return R
