"""The Waterfall Stair: a grand stair two floors tall with a river coming down beside it, basin by
basin, in stone channels either side of the treads. It falls from a spout high in the north wall into
a basin on the landing, and spreads across the floor at the foot. Moss has got into everything.
Behind the fall, a grotto."""
from lib import *
from kit_h4 import *

W = 32.0
N, RISE, RUN = 40, 0.2, 0.32
SY0 = 8.6; SY1 = SY0 + N * RUN          # the stair, climbing north, 0 -> 8
TX0, TX1 = 13.2, 18.8                   # treads
CH = ((12.0, 13.1), (18.9, 20.0))       # the two channels
PX = ((11.7, 12.0), (20.0, 20.3))       # parapets
BX0, BX1, BY0 = 10.5, 21.5, 26.0        # the source block in the north wall, upper floor
GW = 4.35                               # gallery depth


def slope_y(x0, x1, y0, y1, b0, b1, t0, t1, m, cap=None):
    """A slab along y whose bottom runs b0 -> b1 and top t0 -> t1 from y0 to y1."""
    return prism([(y0, b0), (y1, b1), (y1, t1), (y0, t0)], 'x', x0, x1, [m, m, cap or m, m], cap=m)


def nose(y):
    return (y - SY0) / RUN * RISE


def make():
    R = Room('waterfallstair', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    rnd = random.Random(28)
    T_ = T - 0.02
    # ground floor, then the upper hall round the source block, then the void through the slab
    R.cut(box(T_, T_, 0, W - T_, W - T_, TOP, 'tile', bottom='terrazzo', top='plaster'))
    for (x0, y0, x1, y1) in ((T_, T_, BX0, W - T_), (BX1, T_, W - T_, W - T_), (BX0, T_, BX1, BY0)):
        R.cut(box(x0, y0, LH, x1, y1, R.hi - 0.2, 'tile', bottom='floor', top='plaster'))
    R.cut(box(GW, GW, TOP - 0.1, W - GW, SY1, LH + 0.1, 'tile', bottom='tile', top='tile'))
    # a long skylight over the stair
    R.cut(box(14.0, 7.0, R.hi - 0.25, 18.0, 21.0, R.hi + 0.5, 'plaster'))
    R.light(box(14.0, 7.0, R.hi - 0.08, 18.0, 21.0, R.hi - 0.05, 'e_sky'))
    for k in range(8):
        y = 7.0 + k * 2.0
        R.nocol.add(box(13.9, y - 0.06, R.hi - 0.26, 18.1, y + 0.06, R.hi - 0.05, 'iron'))
    # ceiling beams in the upper hall
    for k in range(9):
        y = 2.2 + k * 3.5
        if BY0 - 0.2 < y: break
        R.nocol.add(box(T, y - 0.14, R.hi - 0.55, W - T, y + 0.14, R.hi - 0.2, 'walnut'))

    stair(R, rnd)
    river(R, rnd)
    grotto(R, rnd)
    galleries(R, rnd)
    books(R, rnd)
    lights(R, rnd)

    # walkers
    navloop(R, [(2.2, 2.2), (8, 2.4), (16, 2.6), (24, 2.4), (W - 2.2, 2.2), (W - 2.2, 16), (W - 2.2, W - 2.2),
                (24, W - 2.4), (16, 24.5), (8, W - 2.4), (2.2, W - 2.2), (2.2, 16)])
    a, b = R.navpt(16, SY0 - 0.9 - 3.0), R.navpt(16, SY1 + 0.8, LH)
    R.link(a, b)
    navloop(R, [(2.2, 2.2), (16, 2.2), (W - 2.2, 2.2), (W - 2.2, 16), (W - 2.2, 23.0), (16, 22.3), (2.2, 23.0), (2.2, 16)], z=LH)
    R.spot('probe', 7.0, 14.0, 5.0)
    R.meta.update(label='The Waterfall Stair', weight=3,
                  blurb='Somebody left a tap running on the upper floor, a long time ago. The stair has made its peace with it; so has the moss.')
    R.meta['box'] = [[T, 0, T], [W - T, R.hi, W - T]]
    fx(R, 'fog', [10.5, 3.5, -0.3, 21.5, 10.5, 2.5], density=0.05)
    fx(R, 'fog', [11.0, 22.5, 8.0, 21.0, 26.5, 12.0], density=0.06)
    fx(R, 'dust', [13.5, 7.0, 1.0, 18.5, 21.0, 15.0])
    secret(R, 16.0, 29.0, LH, 'The Grotto Behind the Fall',
           'You walked through the waterfall. Behind it the roar goes soft, somebody has left a candle burning, and the book on the stone is dry.', r=2.0)
    return tidy(R)


def stair(R, rnd):
    R.flight(TX0, SY0, 0, TX1 - TX0, N, RISE, RUN, '+y', m='tile', riser='tile', side='tile')
    # parapets outside the channels, capped with moss; newels at both ends
    for (x0, x1) in PX:
        R.parts.add(slope_y(x0, x1, SY0, SY1, 0, 0, 1.05, LH + 1.05, 'tile'))
        R.parts.add(slope_y(x0 - 0.05, x1 + 0.05, SY0, SY1, 1.05, LH + 1.05, 1.12, LH + 1.12, 'tile'))
        R.nocol.add(slope_y(x0 - 0.08, x1 + 0.08, SY0, SY1, 1.12, LH + 1.12, 1.2, LH + 1.2, 'moss'))
        for (y, z) in ((SY0 - 0.25, 0.0), (SY1 + 0.25, LH)):
            cx = x0 - 0.1 if x0 < 16 else x1 + 0.1
            R.parts.add(box(cx - 0.4, y - 0.4, z, cx + 0.4, y + 0.4, z + 1.5, 'tile', skip=('-z',)))
            R.parts.add(box(cx - 0.48, y - 0.48, z + 1.5, cx + 0.48, y + 0.48, z + 1.62, 'tile'))
            R.parts.add(lathe(cx, y, [(0.0, 0), (0.18, 0), (0.12, 0.1), (0.3, 0.35), (0.32, 0.45), (0.0, 0.45)], 12, 'tile').xform(0, 0, 0, z + 1.62))
            R.nocol.add(blob(cx, y, z + 2.12, 0.34, 0.34, 0.2, 'moss', 10, 5))
            for k in range(5):
                a = rnd.uniform(0, 2 * math.pi)
                R.nocol.add(box(cx + 0.42 * math.cos(a) - 0.05, y + 0.42 * math.sin(a) - 0.05, z + 0.4 + rnd.uniform(0, 0.6), cx + 0.42 * math.cos(a) + 0.05, y + 0.42 * math.sin(a) + 0.05, z + 1.62, 'mossdk'))
        # moss spilling down the outside of the parapet
        for k in range(14):
            y = SY0 + 0.4 + rnd.uniform(0, SY1 - SY0 - 0.8); z = nose(y) + 1.1
            xo = x0 - 0.02 if x0 < 16 else x1 + 0.02
            d = rnd.uniform(0.5, 2.2)
            R.nocol.add(blob(xo, y, z - d / 2, 0.08, rnd.uniform(0.25, 0.6), d / 2 + 0.1, 'moss', 8, 4))
    # the lip between channel and treads
    for (xa, xb) in ((13.1, TX0), (TX1, 18.9)):
        R.parts.add(slope_y(xa, xb, SY0, SY1, 0, LH - 1.0, 0.25, LH + 0.05, 'tile'))


def river(R, rnd):
    # basins in the channels, four steps each, falling one into the next; foam at every weir
    nb = N // 4
    for (xa, xb) in CH:
        for k in range(nb):
            ya, yb = SY0 + k * 4 * RUN, SY0 + (k + 1) * 4 * RUN
            top = RISE * (4 * k + 1) - 0.1
            fl = top - 0.4
            if k == 0: R.cut(box(xa, ya - 0.02, fl, xb, yb, 0.3, 'tile', bottom='tile'))
            else: R.parts.add(box(xa, ya, 0.0, xb, yb, fl, 'tile', skip=('-z',)))
            water(R, xa, ya, xb, yb, top, fl)
            below = -0.06 if k == 0 else RISE * (4 * (k - 1) + 1) - 0.1
            R.nocol.add(box(xa + 0.04, ya - 0.05, below - 0.02, xb - 0.04, ya + 0.02, top + 0.03, 'foam'))
            R.nocol.add(box(xa + 0.04, ya - 0.3, below - 0.01, xb - 0.04, ya - 0.05, below + 0.04, 'foam'))
            if k % 3 == 1:   # step lights under the water
                R.light(box(xa + 0.3, yb - 0.03, fl + 0.08, xb - 0.3, yb - 0.01, fl + 0.18, 'e_pool'))
        # the rill across the landing from the fall basin, a weir at its end
        R.parts.add(box(xa - 0.15, SY1, LH, xa, 23.6, LH + 0.5, 'tile'))
        R.parts.add(box(xb, SY1, LH, xb + 0.15, 23.6, LH + 0.5, 'tile'))
        R.parts.add(box(xa, SY1, LH, xb, SY1 + 0.15, LH + 0.25, 'tile'))
        water(R, xa, SY1, xb, 23.6, LH + 0.36, LH)
        R.nocol.add(box(xa + 0.04, SY1 - 0.05, RISE * 37 - 0.12, xb - 0.04, SY1 + 0.02, LH + 0.28, 'foam'))
    # the pool at the foot, spreading across the floor
    R.pool(PX[0][0], 4.9, PX[1][1], SY0, 0.3, m='terrazzo')
    water(R, PX[0][0], 4.9, PX[1][1], SY0, -0.06, -0.3)
    for k in range(4):
        R.light(box(12.4 + k * 2.4, 4.91, -0.24, 13.0 + k * 2.4, 4.93, -0.12, 'e_pool'))
    # the fall basin on the landing, open where the rills leave it
    y0, y1 = 23.6, BY0
    x0, x1 = PX[0][0], PX[1][1]
    rim = 0.5
    for (a, b) in ((x0, CH[0][0]), (CH[0][1], CH[1][0]), (CH[1][1], x1)):
        R.parts.add(box(a, y0, LH, b, y0 + 0.3, LH + rim, 'tile'))
    R.parts.add(box(x0, y0, LH, x0 + 0.3, y1, LH + rim, 'tile'))
    R.parts.add(box(x1 - 0.3, y0, LH, x1, y1, LH + rim, 'tile'))
    water(R, x0 + 0.3, y0 + 0.3, x1 - 0.3, y1, LH + 0.4, LH)
    R.nocol.add(box(x0 - 0.05, y0 - 0.05, LH + rim, x0 + 1.4, y0 + 0.35, LH + rim + 0.07, 'moss'))
    R.nocol.add(box(x1 - 1.9, y0 - 0.05, LH + rim, x1 + 0.05, y0 + 0.35, LH + rim + 0.07, 'moss'))
    # the spout and the fall itself: streaks of foam from the lip down into the basin
    R.parts.add(box(13.0, BY0 - 0.7, 14.0, 19.0, BY0, 14.35, 'tile'))
    R.parts.add(box(12.8, BY0 - 0.8, 14.35, 19.2, BY0, 14.6, 'tile'))
    R.nocol.add(box(13.0, BY0 - 0.72, 14.6, 19.0, BY0, 14.66, 'moss'))
    x = 13.3
    while x < 18.7:
        w = rnd.uniform(0.18, 0.5)
        yo = BY0 - 0.62 - rnd.uniform(0, 0.12)
        zb = LH + 0.38
        g = Geo()
        pts = [(x + w / 2, yo, 14.0), (x + w / 2, yo - 0.18, 12.2), (x + w / 2, yo - 0.3, 10.2), (x + w / 2, yo - 0.34, zb)]
        for p0, p1 in zip(pts, pts[1:]):
            g.add(bar(p0, p1, w, 0.04, 'foam'))
        R.nocol.add(g)
        x += w * rnd.uniform(0.75, 1.0)
    R.nocol.add(box(13.0, BY0 - 1.3, LH + 0.36, 19.0, BY0 - 0.3, LH + 0.42, 'foam'))


def grotto(R, rnd):
    # the opening behind the fall, the chamber in the block, a spring in its floor
    pr = arch_profile(16.0, 3.0, LH, 1.8, 14)
    R.cut(prism(pr, 'y', BY0 - 0.1, 27.4, arch_mats(len(pr), 'tile', 'tile')))
    cx, cy, r = 16.0, 29.0, 2.55
    R.cut(cyl(cx, cy, LH, LH + 2.8, r, 24, side='tile', bottom='tile', top='tile'))
    R.cut(sphere(cx, cy, LH + 2.8, r, 24, 8, 'tile', lower=False).xform(0, 0, 0, 0))
    R.round_pool(cx + 1.3, cy + 0.9, 0.75, 0.3, m='terrazzo', segs=20)
    rwater(R, cx + 1.3, cy + 0.9, 0.75, LH - 0.04, LH - 0.3)
    # a stone bench, a lectern with the dry book, candles, moss on everything
    R.parts.add(box(cx - 2.1, cy - 0.9, LH, cx - 1.55, cy + 0.9, LH + 0.45, 'tile'))
    R.nocol.add(box(cx - 2.12, cy - 0.92, LH + 0.45, cx - 1.53, cy + 0.92, LH + 0.5, 'moss'))
    R.spot('sit', cx - 1.8, cy, LH + 0.5, 0.0)
    R.parts.add(box(cx - 0.25, cy + 0.9, LH, cx + 0.25, cy + 1.3, LH + 1.0, 'tile'))
    R.parts.add(box(cx - 0.35, cy + 0.8, LH + 1.0, cx + 0.35, cy + 1.35, LH + 1.08, 'tile'))
    open_book(R, cx, cy + 1.07, LH + 1.08, 0.0)
    R.spot('plaque', cx, cy + 0.5, LH, math.pi / 2, text='Everything that falls here arrives. Nothing that arrives here leaves. The water does not mind.')
    for (dx, dy) in ((-0.6, 1.9), (0.9, 2.0), (-1.9, 1.2)):
        candle(R, cx + dx, cy + dy, LH, h=0.22)
    sh(R, '-y', cy + r - 0.05, cx - 1.2, cx + 1.2, z=LH + 1.2, rows=3, frame='walnut', depth=0.28)
    for k in range(18):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.4, 2.3)
        R.nocol.add(blob(cx + d * math.cos(a), cy + d * math.sin(a), LH, rnd.uniform(0.25, 0.6), rnd.uniform(0.25, 0.6), 0.06, 'moss', 8, 3))
    R.light(sphere(cx, cy, LH + 4.4, 0.12, 8, 4, 'e_dim'))
    R.light(sphere(cx + 1.3, cy + 0.9, LH - 0.2, 0.1, 8, 4, 'e_pool'))


def galleries(R, rnd):
    g = GW
    # balustrades on the void edges (the stair arrives between its parapets on the north)
    for (x0, y0, x1, y1) in ((g - 0.1, g - 0.1, g - 0.1, SY1 + 0.1), (W - g + 0.1, g - 0.1, W - g + 0.1, SY1 + 0.1),
                             (g - 0.2, g - 0.1, W - g + 0.2, g - 0.1), (g - 0.2, SY1 + 0.1, PX[0][0] - 0.4, SY1 + 0.1),
                             (PX[1][1] + 0.4, SY1 + 0.1, W - g + 0.2, SY1 + 0.1)):
        balus(R, x0, y0, x1, y1, LH, h=1.0)
        if abs(y1 - y0) < 1e-6: moss_slab(R, min(x0, x1), y0 - 0.13, max(x0, x1), y0 + 0.13, LH + 1.06, 0.06, 0.0)
        else: moss_slab(R, x0 - 0.13, min(y0, y1), x0 + 0.13, max(y0, y1), LH + 1.06, 0.06, 0.0)
    # the slab edges: a moulded fascia, moss hanging off it
    for (x0, y0, x1, y1) in ((g - 0.12, g, g + 0.02, SY1), (W - g - 0.02, g, W - g + 0.12, SY1), (g - 0.12, g - 0.12, W - g + 0.12, g + 0.02),
                             (g - 0.12, SY1 - 0.02, PX[0][0], SY1 + 0.12), (PX[1][1], SY1 - 0.02, W - g + 0.12, SY1 + 0.12)):
        R.parts.add(box(x0, y0, TOP - 0.45, x1, y1, LH + 0.02, 'tile'))
    strands(R, g + 0.05, g + 0.3, g + 0.05, SY1 - 0.3, TOP - 0.45, 26, 2.8, rnd)
    strands(R, W - g - 0.05, g + 0.3, W - g - 0.05, SY1 - 0.3, TOP - 0.45, 26, 2.8, rnd)
    strands(R, g + 0.3, g + 0.05, W - g - 0.3, g + 0.05, TOP - 0.45, 34, 2.4, rnd)
    strands(R, g + 0.3, SY1 - 0.05, PX[0][0] - 0.2, SY1 - 0.05, TOP - 0.45, 10, 3.2, rnd)
    strands(R, PX[1][1] + 0.2, SY1 - 0.05, W - g - 0.3, SY1 - 0.05, TOP - 0.45, 10, 3.2, rnd)
    # columns under the gallery edges, moss climbing them
    cols = [(g - 0.1, y) for y in (4.2, 9.0, 13.8, 18.6)] + [(W - g + 0.1, y) for y in (4.2, 9.0, 13.8, 18.6)] + \
           [(x, g - 0.1) for x in (11.0, 16.0, 21.0)] + [(g - 0.1, SY1 - 0.1), (W - g + 0.1, SY1 - 0.1)]
    for (x, y) in cols:
        x = min(max(x, g - 0.1), W - g + 0.1)
        R.parts.add(cyl(x, y, 0.3, TOP - 0.45, 0.32, 16, side='tile', caps=False))
        R.parts.add(box(x - 0.45, y - 0.45, 0, x + 0.45, y + 0.45, 0.3, 'tile', skip=('-z',)))
        R.parts.add(box(x - 0.48, y - 0.48, TOP - 0.75, x + 0.48, y + 0.48, TOP - 0.45, 'tile'))
        for k in range(4):
            a = rnd.uniform(0, 2 * math.pi); h = rnd.uniform(0.5, 1.6); z = rnd.uniform(0.2, 3.5)
            R.nocol.add(blob(x + 0.3 * math.cos(a), y + 0.3 * math.sin(a), z + h / 2, 0.07, 0.07, h / 2, rnd.choice(('moss', 'mossdk')), 6, 4, a))
        R.nocol.add(ring(x, y, 0.3, 0.42, 0.3, 0.36, 16, top='moss', bottom='moss', inner='moss', outer='moss'))
        R.nocol.add(ring(x, y, TOP - 0.75, TOP - 0.6, 0.3, 0.52, 16, top='moss', bottom='mossdk', inner='moss', outer='mossdk'))


def books(R, rnd):
    # the ground floor: tall cases between the doorways; the upper floor again
    spans = ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8))
    for (a, b) in spans:
        sh(R, '+y', T, a, b, rows=16, frame='walnut')
        sh(R, '+x', T, a, b, rows=16, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=16, frame='walnut')
        sh(R, '-y', W - T, a, b, rows=16, frame='walnut')
        sh(R, '+y', T, a, b, z=LH, rows=14, frame='walnut')
        sh(R, '+x', T, a, b, z=LH, rows=14, frame='walnut')
        sh(R, '-x', W - T, a, b, z=LH, rows=14, frame='walnut')
        if b < BX0 or a > BX1: sh(R, '-y', W - T, a, b, z=LH, rows=14, frame='walnut')
    # the source block's face, either side of the fall: cases, with moss on their crowns
    strands(R, BX0 + 0.1, BY0 - 0.05, 13.0, BY0 - 0.05, R.hi - 0.3, 12, 4.5, rnd, m='moss')
    strands(R, 19.0, BY0 - 0.05, BX1 - 0.1, BY0 - 0.05, R.hi - 0.3, 12, 4.5, rnd, m='moss')
    sh(R, '+x', BX1, BY0 + 0.3, W - T - 0.6, z=LH, rows=13, frame='walnut')
    sh(R, '-x', BX0, BY0 + 0.3, W - T - 0.6, z=LH, rows=13, frame='walnut')
    for (x0, x1) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        moss_slab(R, x0, T, x1, T + 0.4, LH + 6.0, 0.08, 0.0, 0.8, rnd)
        moss_slab(R, x0, T, x1, T + 0.4, 6.84, 0.08, 0.0, 0.6, rnd)
    # reading tables in the undercroft and on the landing, green lamps
    for (x0, y0, z) in ((2.6, 26.5, 0.0), (22.6, 26.5, 0.0), (2.6, 26.0, LH), (25.4, 26.0, LH)):
        table(R, x0, y0, x0 + 3.6, y0 + 1.0, z, top='leather')
        desk_lamp(R, x0 + 1.0, y0 + 0.5, z + 0.76); desk_lamp(R, x0 + 2.6, y0 + 0.5, z + 0.76)
        chair(R, x0 + 1.0, y0 - 0.5, math.pi / 2, z); chair(R, x0 + 2.6, y0 + 1.5, -math.pi / 2, z)
    # books left out on the wet steps of the foot pool, moss on the floor edges
    for k in range(10):
        x = rnd.uniform(2.0, 30.0); y = rnd.uniform(2.0, 30.0)
        if 10.5 < x < 21.5 and 3.5 < y < 23: continue
        R.nocol.add(blob(x, y, 0.0, rnd.uniform(0.4, 1.2), rnd.uniform(0.4, 1.2), 0.04, 'moss', 8, 3))


def lights(R, rnd):
    for (x, y) in ((10.9, 7.4), (21.1, 7.4), (10.9, 3.0), (21.1, 3.0)):
        floor_lamp(R, x, y, 1.9)
    for (x, y) in ((8.8, SY1 + 1.2), (23.2, SY1 + 1.2), (8.8, 29.5), (23.2, 29.5)):
        R.parts.add(cyl(x, y, LH, LH + 1.4, 0.03, 6, side='brass', caps=False))
        R.parts.add(cyl(x, y, LH, LH + 0.04, 0.2, 10, side='brass', top='brass'))
        R.light(sphere(x, y, LH + 1.5, 0.13, 10, 5, 'e_amber'))
    # lamps under the galleries
    for k in range(6):
        p = 3.0 + k * (W - 6.0) / 5
        for (x, y) in ((2.2, p), (W - 2.2, p), (p, 2.2)):
            bulb(R, x, y, 5.9, r=0.16, top=TOP)
    for (x, y) in ((6.0, 27.0), (16.0, 24.0), (26.0, 27.0), (16.0, 29.5)):
        bulb(R, x, y, 5.6, r=0.18, top=TOP)
    for (x, y) in ((2.0, 6.0), (2.0, 16.0), (W - 2.0, 6.0), (W - 2.0, 16.0), (16.0, 2.0), (6.0, 2.0), (26.0, 2.0)):
        bulb(R, x, y, LH + 4.8, r=0.15, top=R.hi - 0.2)
    for (x, y) in ((6.0, 27.5), (26.0, 27.5), (2.0, 27.5), (W - 2.0, 27.5)):
        bulb(R, x, y, LH + 4.6, r=0.17, top=R.hi - 0.2)
