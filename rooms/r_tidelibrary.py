"""The Tide Library: a long vaulted hall that the sea has got into. Stone causeways cross it dry, just;
everything between them stands in half a metre to a metre of still salt water, the lower shelves
furred with barnacles and weed, tall windows full of low sun. In the north bay a sump goes deeper,
and under the east causeway it opens into a passage you can only swim, up into a pocket of air."""
from kit_h3 import *

W, D = 32.0, 16.0
WT = -0.06                     # the water's surface
BOT = -0.9                     # the flooded aisles' floor
DEEP = -1.9                    # the sump and the passage
CW0, CW1 = 6.2, 9.8            # the east-west causeway
NS = ((6.5, 9.5), (22.5, 25.5))  # north-south causeways
PX0, PX1, PY0, PY1 = 20.6, 26.6, 11.9, 13.4       # the underwater passage (x runs east)
AX0, AY0 = 26.6, 10.4          # the air-pocket room: x AX0..W-T, y AY0..D-T


def make():
    R = Room('tidelibrary', 2, 1, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    # the hall under a barrel vault; its floor is the causeways, cut down between them
    pr = arch_profile(D / 2, D - 2 * T + 0.04, 0, 5.0, 28, rise=2.45)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
    for k in range(9):
        x = T + 1.6 + k * (W - 2 * T - 3.2) / 8
        R.nocol.add(prism(arc_band(D / 2, D - 2 * T, 5.0, 2.45, 0.0, 0.28, 28), 'x', x - 0.22, x + 0.22, 'tile', cap='tile'))
    # the flooded bays, stepped down at their edges like old quays
    xs = [(T, NS[0][0]), (NS[0][1], NS[1][0]), (NS[1][1], W - T)]
    ys = [(T, CW0), (CW1, D - T)]
    for (x0, x1) in xs:
        for (y0, y1) in ys:
            if x0 > 25 and y0 > 9: continue           # the north-east bay is the hidden room
            R.pool(x0 - 0.02 if x0 < 1 else x0, y0 - 0.02 if y0 < 1 else y0, x1 + 0.02 if x1 > 31 else x1, y1 + 0.02 if y1 > 15 else y1,
                   -BOT, m='slate', steps=True)
    R.water.append(dict(x0=T, y0=T, x1=W - T, y1=D - T, top=WT, bot=BOT))
    # a skirt of dark stone round the causeways' edges, just above the water
    for (x0, x1) in NS:
        for (a, b) in ((T, CW0), (CW1, D - T)):
            for x in (x0, x1):
                R.parts.add(box(x - 0.12, a, -0.02, x + 0.12, b, 0.04, 'slate'))
    for y in (CW0, CW1):
        R.parts.add(box(T, y - 0.12, -0.02, W - T, y + 0.12, 0.04, 'slate'))
    sump(R)
    air_pocket(R)
    windows(R)
    stacks(R)
    furniture(R)
    fx(R, 'dust', [T, CW0, 0.5, W - T, CW1, 5.0])
    # walking graph: the causeways
    m = navloop(R, [(1.6, 8), (8, 8), (16, 8), (24, 8), (30.4, 8)], close=False)
    s1, n1, s2, n2 = R.navpt(8, 1.8), R.navpt(8, 14.2), R.navpt(24, 1.8), R.navpt(24, 14.2)
    R.link(s1, m[1], n1); R.link(s2, m[3], n2)
    secret(R, 30.0, 13.0, 0.0, 'The Air Pocket',
           'You come up gasping into a dry stone room the sea never reached. Someone has kept it: the books are dry, the lamp is lit, and through the little window the tide is always about to turn.')
    return finish(R, 'The Tide Library', weight=4, probe=(16, 8, 1.8), top=7.45,
                  blurb='The sea has come into the library, quietly, and stayed. The water is warm and perfectly still, and the lower shelves have begun to grow barnacles.')


def sump(R):
    """In the north middle bay the floor steps down into a square of deep water that runs on east,
    under the causeway, as a flooded passage."""
    x0, x1, y0, y1 = 17.6, PX1, 11.0, 14.3
    z = BOT
    for k in range(4):     # steps down from the bay floor, from the west
        z -= 0.25
        R.cut(box(x0 + k * 0.4, y0 + k * 0.2, z, NS[1][0] + 0.02, y1 - k * 0.2, BOT + 0.1, 'slate', top='slate'))
    R.cut(box(PX0, PY0, DEEP, PX1, PY1, -0.45, 'slate', top='slate', bottom='slate'))
    R.water.append(dict(x0=x0, y0=y0, x1=W - T, y1=D - T, top=WT, bot=DEEP))
    # an iron grating half-open over the sump mouth, and a drowned lamp shining in the passage
    R.nocol.add(box(NS[1][0] - 0.05, PY0 - 0.1, -1.3, NS[1][0] + 0.02, PY0 + 0.4, -0.45, 'iron'))
    R.light(sphere(24.0, PY1 - 0.15, -1.1, 0.07, 8, 4, 'e_amber'))


def air_pocket(R):
    """Behind the causeway: a stone room with its own little pool, dry above it, lit."""
    x0, x1, y0, y1 = AX0, W - T, AY0, D - T
    # its walls and ceiling stand in the hall's vault: nobody sees them from outside for the books
    R.parts.add(box(NS[1][1] + 0.1, y0 - 0.3, 0, x1 + 0.02, y0, 7.5, 'tile'))
    R.parts.add(box(x0 - 0.3, y0 - 0.3, 0, x0, y1 + 0.02, 7.5, 'tile'))
    R.parts.add(box(x0 - 0.02, y0 - 0.02, 3.1, x1 + 0.02, y1 + 0.02, 3.4, 'plaster'))
    # the pool where the passage comes up, stepped on its east side
    R.cut(box(x0 - 0.02, PY0 - 0.6, DEEP, 28.2, PY1 + 0.6, 0.3, 'slate', top='slate'))
    for k in range(6):
        zt = DEEP + (k + 1) * 0.3
        R.parts.add(box(28.2 - (6 - k) * 0.28, PY0 - 0.6, DEEP, 28.2, PY1 + 0.6, min(zt, -0.02), 'slate'))
    for y in (PY0 - 0.66, PY1 + 0.66):
        rail(R, x0 + 0.05, y, 28.1, y, 0.0)
    # books: the dry wall, a bed, a lamp, a porthole
    sh(R, '-y', y1, 28.6, x1 - 0.3, rows=6, frame='oak')
    sh(R, '-x', x1, y0 + 0.3, PY0 - 0.4, rows=6, frame='oak')
    R.parts.add(box(29.0, y0 + 0.2, 0, x1 - 0.2, y0 + 1.1, 0.45, 'bed'))
    R.parts.add(box(29.0, y0 + 0.2, 0.45, 29.5, y0 + 1.1, 0.6, 'ivory'))
    R.spot('bed', 30.2, y0 + 0.65, 0.45, 0.0)
    R.parts.add(table(28.6, 13.6, 29.6, 14.6, 0.74, 'walnut'))
    open_book(R, 29.1, 14.1, 0.74, 0.3)
    desk_lamp(R, 29.4, 14.4, 0.74)
    c = chair(28.3, 14.1, 0.0); R.parts.add(c); R.spot('sit', 28.3, 14.1, 0.48, 0.0)
    R.parts.add(cyl(x0 + 0.5, y1 - 0.4, 0, 0.04, 0.12, 8, side='brass', top='brass'))
    candle(R, x0 + 0.5, y1 - 0.4, 0.04, h=0.2)
    # a porthole in the north wall onto the sea
    R.cut(box(29.45, y1 - 0.02, 1.25, 30.35, y1 + 0.3, 2.15, 'brass'))
    R.light(box(29.45, y1 + 0.26, 1.25, 30.35, y1 + 0.3, 2.15, 'e_skydome'))
    R.nocol.add(box(29.85, y1 + 0.2, 1.25, 29.95, y1 + 0.25, 2.15, 'brass'))
    R.nocol.add(box(29.45, y1 + 0.2, 1.65, 30.35, y1 + 0.25, 1.75, 'brass'))
    R.spot('plaque', 28.4, y1 - 0.05, 1.6, -math.pi / 2, text='HIGH WATER MARK, and a date nobody can read')
    bulb(R, 29.6, 12.6, 2.4, r=0.12, m='e_lamp', top=3.1)


def windows(R):
    for c in (3.4, 12.0, 16.0, 20.0, 28.6):
        window(R, 'S', c, 0.6, 2.2, 3.4, em='e_skydome', mull=2, trans=3)
        R.light(box(c - 1.1, 0.075, 0.6, c + 1.1, 0.085, 1.0, 'e_sky'))      # the low sun on the sea's rim
        if c < 26:
            window(R, 'N', c, 0.6, 2.2, 3.4, em='e_skydome', mull=2, trans=3)
            R.light(box(c - 1.1, D - 0.085, 0.6, c + 1.1, D - 0.075, 1.0, 'e_sky'))
    # the sun itself, low in the west-most south window
    R.light(sun_disc(3.9, 0.095, 1.25, 0.3))


def sun_disc(x, y, z, r, n=16):
    g = Geo()
    ids = [g.vert((x + r * math.cos(2 * math.pi * k / n), y, z + r * math.sin(2 * math.pi * k / n))) for k in range(n)]
    g.face(ids[::-1], 'e_lamp', [(0, 0)] * n)      # facing +y, into the room
    return g


def barnacles(R, x0, y0, x1, y1, z0, z1, n, seed):
    """Barnacles and weed on the lower part of a bookcase face (a strip from (x0,y0) to (x1,y1))."""
    rnd = random.Random(seed)
    g = Geo()
    for k in range(n):
        t = rnd.random(); z = z0 + (z1 - z0) * rnd.random() ** 1.6
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = rnd.uniform(0.04, 0.09)
        g.add(ellipsoid(x, y, z, r, r, r * 0.8, rnd.choice(('ivory', 'slate', 'plaster')), 6, 3))
    R.nocol.add(g)
    for k in range(n // 4):
        t = rnd.random(); x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        zt = z1 + rnd.uniform(-0.1, 0.35)
        R.nocol.add(box(x - 0.02, y - 0.02, z0, x + 0.02, y + 0.02, zt, 'green'))


def stacks(R):
    rows = 12
    k = 0
    # stacks standing in the water, out from the long walls, between the windows
    for x in (1.7, 5.1, 10.4, 14.0, 18.0, 21.6, 26.9, 30.3):
        for (a, b, face) in ((T + 0.05, CW0 - 1.2, 1), (CW1 + 1.2, D - T - 0.05, -1)):
            if x > 26 and face < 0: continue
            if 17.5 < x < 22 and face < 0: continue            # the sump
            stack(R, 'y', x, a, b, z=BOT, rows=rows, frame='walnut')
            for s in (-1, 1):
                barnacles(R, x + s * 0.37, a, x + s * 0.37, b, BOT, WT + 0.15, 34, seed=k); k += 1
    # the end walls
    for (a, b) in ((T + 0.3, CW0 - 0.5), (CW1 + 0.5, D - T - 0.3)):
        sh(R, '+x', T, a, b, z=BOT, rows=rows, frame='walnut')
        barnacles(R, T + 0.36, a, T + 0.36, b, BOT, WT + 0.2, 24, seed=k); k += 1
    sh(R, '-x', W - T, T + 0.3, CW0 - 0.5, z=BOT, rows=rows, frame='walnut')
    barnacles(R, W - T - 0.36, T + 0.3, W - T - 0.36, CW0 - 0.5, BOT, WT + 0.2, 24, seed=k)
    # the wall between the flooded hall and the air pocket: books on its hall side
    sh(R, '+y', AY0, NS[1][1] + 0.3, W - T - 0.3, z=0.0, rows=6, frame='walnut')


def furniture(R):
    """Reading tables that the water came in around, lamps still lit; lamps on posts along the causeway."""
    for (x0, y0) in ((11.0, 2.2), (15.0, 2.2), (19.0, 2.2)):
        g = table(x0, y0, x0 + 2.2, y0 + 1.0, 0.78 - BOT, 'walnut', top='leather'); g.xform(0, 0, 0, BOT); R.parts.add(g)
        desk_lamp(R, x0 + 0.6, y0 + 0.5, 0.78); desk_lamp(R, x0 + 1.6, y0 + 0.5, 0.78)
        for xx in (x0 + 0.6, x0 + 1.6):
            c = chair(xx, y0 + 1.45, -math.pi / 2); c.xform(0, 0, 0, BOT); R.parts.add(c)
        book_pile(R, x0 + 1.1, y0 + 0.3, 0.78, 4, seed=int(x0))
    for (x0, y0) in ((11.0, 12.6), (14.6, 12.6)):
        g = table(x0, y0, x0 + 2.2, y0 + 1.0, 0.78 - BOT, 'walnut', top='leather'); g.xform(0, 0, 0, BOT); R.parts.add(g)
        desk_lamp(R, x0 + 1.1, y0 + 0.5, 0.78)
        c = chair(x0 + 1.1, y0 - 0.45, math.pi / 2); c.xform(0, 0, 0, BOT); R.parts.add(c)
    for x in (4.0, 12.0, 20.0, 28.0):
        for y in (CW0 + 0.35, CW1 - 0.35):
            if x in (4.0, 28.0) and y > 8: continue
            lamp_post(R, x, y, 0, 2.4)
    for x in (8.0, 16.0, 24.0):
        pendant(R, x, 8.0, 4.4, 7.4, r=0.26)
    # a rowing boat's worth of floating books, drifting
    rnd = random.Random(5)
    for k in range(14):
        x, y = rnd.uniform(10.5, 21.5), rnd.uniform(4.2, 5.8)
        b = box(-0.12, -0.09, 0, 0.12, 0.09, 0.04, rnd.choice(('oxblood', 'green', 'leather'))); b.xform(rnd.uniform(0, 3), x, y, WT - 0.015)
        R.nocol.add(b)
