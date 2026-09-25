"""The Lake Overhead: a reading room whose ceiling is a lake. A stone basin twenty metres square hangs
from the vault with two metres of still green water in it and nothing under the water but air: you
read under its belly, the light coming down through it, the fish going over. A rope ladder is pegged to
the floor and slants up into the water. Swim up, and in the lake's north-east corner, where a lamp burns
under the lid, there is a pocket of air and a stone ledge to climb out on; from it a passage and a stair
inside the east wall come down behind a bookcase."""
from kit_h8 import *

W = D = 32.0
L0, L1 = 5.3, 26.7              # the lake, inside its basin (x and y)
BT = 0.3                        # the basin's wall
WB, WT = 3.6, 5.6               # the water's underside and surface
LID = 6.0                       # the lake bed, overhead
PX0, PY0, PY1 = 23.2, 18.4, 21.8  # the air pocket: x PX0..L1, y PY0..PY1
LX0 = 24.6                      # the pocket's ledge starts here
QY0, QY1 = 20.2, 21.4           # the passage east from the pocket, and the stair's top landing
EX = 28.5                       # the east pier's face (the stair is inside it)
EY0, EY1 = 10.3, 21.7
FX0, FX1 = 29.95, 31.25         # the stair
FY0 = 11.8                      # its foot (it climbs +y to QY0 at WT)


def make():
    R = Room('waterceiling', 2, 2, res=2048)
    R.sockets(floor='marble', wall='tile')
    for (x0, y0, x1, y1) in ((T, T, EX, D - T), (EX - 0.02, T, W - T, EY0), (EX - 0.02, EY1, W - T, D - T)):
        R.cut(box(x0 - 0.02, y0 - 0.02, 0, x1 + 0.02, y1 + 0.02, TOP, 'tile', bottom='marble', top='plaster'))
    basin(R)
    lake(R)
    ladder(R)
    pocket(R)
    east_stair(R)
    hall(R)
    g = navloop(R, [(8.5, 8.5), (16, 8.5), (23.5, 8.5), (23.5, 23.5), (16, 23.5), (8.5, 23.5)])
    h = navloop(R, [(2.4, 2.4), (16, 2.4), (29.6, 2.4), (29.6, 8.0), (26.0, 16), (29.6, 24.0), (29.6, 29.6), (16, 29.6), (2.4, 29.6), (2.4, 16)])
    R.link(g[1], h[1]); R.link(g[4], h[7])
    fx(R, 'dust', [L0, L0, 0.4, L1, L1, WB - 0.2])
    secret(R, 25.6, 20.1, WT, 'The Air Pocket',
           'You come up out of the lake into a pocket of air under its bed, a stone ledge and a lamp and a chair. Someone swam up here with a book and a towel, and meant to stay.')
    return finish(R, 'The Lake Overhead', weight=3, probe=(16, 16, 1.8),
                  blurb='The ceiling is a lake. It hangs there, green and perfectly still, and fish go over. A rope ladder goes up into it, for anyone who wants to.')


def basin(R):
    """The basin's four walls hang from the vault to the water's underside; a bronze lip runs round the bottom."""
    o0, o1 = L0 - BT, L1 + BT
    for (x0, y0, x1, y1) in ((o0, o0, o1, L0), (o0, L1, o1, o1), (o0, L0, L0, L1)):
        R.parts.add(box(x0, y0, WB, x1, y1, TOP + 0.02, 'tile'))
    # the east wall, open where the passage leaves the pocket
    R.parts.add(box(L1, L0, WB, o1, QY0, TOP + 0.02, 'tile'))
    R.parts.add(box(L1, QY1, WB, o1, L1, TOP + 0.02, 'tile'))
    R.parts.add(box(L1, QY0, WB, o1, QY1, WT - 0.3, 'tile'))
    for (x0, y0, x1, y1) in ((o0 - 0.06, o0 - 0.06, o1 + 0.06, o0 + 0.1), (o0 - 0.06, o1 - 0.1, o1 + 0.06, o1 + 0.06),
                             (o0 - 0.06, o0, o0 + 0.1, o1), (o1 - 0.1, o0, o1 + 0.06, o1)):
        R.parts.add(box(x0, y0, WB - 0.16, x1, y1, WB, 'bronze'))
    # the lid: the lake bed, overhead, everywhere but the pocket
    for (x0, y0, x1, y1) in ((L0, L0, L1, PY0), (L0, PY1, L1, L1), (L0, PY0, PX0, PY1)):
        R.parts.add(box(x0, y0, LID, x1, y1, TOP + 0.02, 'slate', bottom='slate'))
    # bookcases hung on the basin's outer faces, above the heads of the readers underneath
    o = BT + 0.02
    for (a0, a1) in ((L0 + 0.4, 15.4), (16.6, L1 - 0.4)):
        sh(R, '-y', L0 - o, a0, a1, z=WB + 0.05, rows=8, frame='walnut')
        sh(R, '+y', L1 + o, a0, a1, z=WB + 0.05, rows=8, frame='walnut')
        sh(R, '-x', L0 - o, a0, a1, z=WB + 0.05, rows=8, frame='walnut')
    sh(R, '+x', L1 + o, L0 + 0.4, QY0 - 0.5, z=WB + 0.05, rows=8, frame='walnut')
    # lamps hung from the basin's lip over the margins
    for k in range(6):
        t = L0 + 1.8 + k * (L1 - L0 - 3.6) / 5
        for (x, y) in ((t, L0 - 1.6), (t, L1 + 1.6), (L0 - 1.6, t), (L1 + 1.6, t)):
            if x > EX - 0.5: continue
            pendant(R, x, y, 4.2, TOP, r=0.24, m='e_lamp')
    # consoles under the lip at the corners and middles
    for (x, y) in ((o0, o0), (o1, o0), (o0, o1), (o1, o1), (16, o0), (16, o1), (o0, 16), (o1, 16)):
        R.parts.add(box(x - 0.35, y - 0.35, WB - 0.9, x + 0.35, y + 0.35, WB - 0.16, 'tile'))
        R.parts.add(cone(x, y, WB - 1.6, WB - 0.9, 0.05, 0.3, 8, m='tile'))


def lake(R):
    """One big volume of water, and a thin one at its underside so the belly of the lake shows as a surface."""
    R.water.append(dict(x0=L0, y0=L0, x1=L1, y1=L1, top=WT, bot=WB))
    R.water.append(dict(x0=L0, y0=L0, x1=L1, y1=L1, top=WB, bot=WB - 0.02))
    rnd = random.Random(78)
    # the bed overhead: weed, stones, drowned books lying on it upside down, and drowned lamps still lit
    for k in range(60):
        x, y = rnd.uniform(L0 + 0.5, L1 - 0.5), rnd.uniform(L0 + 0.5, L1 - 0.5)
        if PX0 - 0.5 < x and PY0 - 0.5 < y < PY1 + 0.5: continue
        if k % 3 == 0:
            R.nocol.add(blob(x, y, LID, rnd.uniform(0.2, 0.5), rnd.uniform(0.2, 0.5), 0.12, segs=7, rings=3, m=rnd.choice(('slate', 'tile'))))
        elif k % 3 == 1:
            for j in range(rnd.randint(2, 5)):
                h = rnd.uniform(0.3, 1.3)
                R.nocol.add(tube([(x, y, LID), (x + rnd.uniform(-0.15, 0.15), y + rnd.uniform(-0.15, 0.15), LID - h * 0.5), (x + rnd.uniform(-0.3, 0.3), y + rnd.uniform(-0.3, 0.3), LID - h)], [0.04, 0.03, 0.01], 4, 'moss'))
                x += rnd.uniform(-0.3, 0.3); y += rnd.uniform(-0.3, 0.3)
        else:
            b = box(-0.14, -0.1, -0.04, 0.14, 0.1, 0.0, rnd.choice(('oxblood', 'green', 'leather', 'walnut')))
            R.nocol.add(b.xform(rnd.uniform(0, 3.1), x, y, LID))
    for (x, y) in ((9.0, 9.0), (22.0, 10.0), (10.0, 21.0), (16.0, 16.0), (20.0, 23.0)):
        R.nocol.add(cyl(x, y, LID - 0.6, LID, 0.02, 6, side='brass', caps=False))
        R.light(sphere(x, y, LID - 0.7, 0.14, 10, 5, 'e_glow'))
    # the fish: two slow shoals going round, one each way
    for (sp, zr, n, seed) in ((0.06, (4.1, 4.8), 34, 1), (-0.045, (4.6, 5.3), 26, 2)):
        M = R.mover('spin', pivot=(16.0, 16.0, 0.0), axis='z', speed=sp)
        fr = random.Random(seed)
        for k in range(n):
            a = fr.uniform(0, 2 * math.pi); d = fr.uniform(3.0, 9.5)
            x, y = 16 + d * math.cos(a), 16 + d * math.sin(a)
            face = a + (math.pi / 2 if sp > 0 else -math.pi / 2) + fr.uniform(-0.2, 0.2)
            big = fr.random() < 0.15
            M.nocol.add(fish(x, y, fr.uniform(*zr), face, L=fr.uniform(0.9, 1.5) if big else fr.uniform(0.35, 0.6),
                             m='fish' if fr.random() < 0.7 else 'slate', fin='fishred' if fr.random() < 0.4 else 'fish'))


def ladder(R):
    """A rope ladder pegged to the floor, slanting up into the water and on to a ring in the lake bed."""
    x, y = 12.0, 14.0
    ang = math.radians(60)
    L = WB / math.tan(ang)
    ladder_up(R, x, y, 0.0, WB - 0.05, '+x', w=0.7, visual=False, ang=ang)
    Lt = LID / math.tan(ang)
    g = Geo()
    for s in (-0.35, 0.35):
        g.add(beam((0, s, 0.0), (Lt, s, LID), 0.04, 'rope', 0.04))
    n = int(LID / 0.3)
    for k in range(1, n):
        t = k / n
        g.add(box(Lt * t - 0.03, -0.38, LID * t - 0.02, Lt * t + 0.03, 0.38, LID * t + 0.02, 'oak'))
    g.xform(0, x, y, 0)
    R.nocol.add(g)
    for s in (-0.35, 0.35):
        R.parts.add(cyl(x - 0.1, y + s, 0, 0.12, 0.08, 8, side='brass', top='brass'))
    R.nocol.add(ring(x + Lt, y, LID - 0.12, LID - 0.06, 0.1, 0.16, 12, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.spot('plaque', x - 0.3, y - 0.8, 1.2, 0.0, text='SWIMMERS ONLY. The lake is not responsible for anything it contains.')


def pocket(R):
    """A pocket of air under the lake bed: a ledge at the waterline, a lamp, a chair, towels; and the way out."""
    z = WT
    R.parts.add(box(LX0, PY0, z - 0.3, L1, PY1, z, 'tile', top='oak'))
    # the passage east through the basin wall to the stair, a stone box across the gap
    R.parts.add(box(L1 - 0.02, QY0, z - 0.3, EX + 0.02, QY1, z, 'tile', top='oak'))
    R.parts.add(box(L1 + BT, QY0 - 0.2, z - 0.3, EX, QY0, TOP + 0.02, 'tile'))
    R.parts.add(box(L1 + BT, QY1, z - 0.3, EX, QY1 + 0.2, TOP + 0.02, 'tile'))
    R.parts.add(box(L1 + BT, QY0 - 0.2, z - 0.55, EX, QY1 + 0.2, z - 0.3, 'bronze'))
    # a rail along the water side of the ledge, open where you climb out
    # railed along the water, but for a gap over a drowned step where you haul yourself out
    brass_rail(R, LX0 + 0.04, PY0, LX0 + 0.04, 19.6, z, h=0.95, post=1.0)
    brass_rail(R, LX0 + 0.04, 20.8, LX0 + 0.04, PY1, z, h=0.95, post=1.0)
    R.parts.add(box(LX0 - 0.9, 19.6, WB + 0.15, LX0, 20.8, WB + 0.4, 'tile'))
    for yy in (19.62, 20.78):
        R.nocol.add(cyl(LX0 + 0.04, yy, z, z + 1.1, 0.04, 8, side='brass', top='brass'))
    for (y0, y1) in ((PY0 - 0.05, PY0), (PY1, PY1 + 0.05)):
        R.col.add(box(LX0, y0, z, L1, y1, LID + 0.05, 'tile'))
    chair(R, 26.1, 18.9, math.pi / 2, z=z)
    R.parts.add(box(25.4, 21.2, z, 26.5, 21.7, z + 0.1, 'bed'))
    R.parts.add(box(25.5, 21.25, z + 0.1, 26.4, 21.65, z + 0.2, 'ivory'))
    book_pile(R, 26.3, 20.0, z, 5, seed=9)
    open_book(R, 25.4, 19.1, z + 0.02, 0.8)
    R.parts.add(cyl(24.9, 21.5, z, z + 0.05, 0.1, 8, side='brass', top='brass'))
    candle(R, 24.9, 21.5, z + 0.05, h=0.14)
    bulb(R, 25.5, 20.2, TOP - 0.55, r=0.1, m='e_lamp', top=TOP, shade='green')
    R.spot('plaque', L1 - 0.05, 19.6, z + 1.5, math.pi, text='HIGH WATER. It has never been higher. It has never been lower, either.')


def east_stair(R):
    """Inside the east pier: from the passage's end a stair comes down to a bookcase that is not one."""
    prof = [(10.6, 0.0), (FY0, 0.0), (QY0, WT), (QY1, WT), (QY1, 7.5), (QY0 - 0.6, 7.5), (FY0, 2.6), (10.6, 2.6)]
    R.cut(prism(prof, 'x', FX0 - 0.05, FX1 + 0.05, ['floor', 'tile', 'floor', 'tile', 'plaster', 'plaster', 'plaster', 'tile'], cap='tile'))
    R.cut(box(EX - 0.05, QY0, WT, FX1 + 0.05, QY1, 7.5, 'tile', bottom='floor', top='plaster'))
    R.cut(box(EX - 0.05, 10.6, 0, FX1 + 0.05, FY0 + 0.02, 2.6, 'tile', bottom='floor', top='plaster'))
    R.flight(FX0, FY0, 0.0, FX1 - FX0, 28, WT / 28, (QY0 - FY0) / 28, '+y', m='oak', riser='walnut', side='tile')
    for k in range(3):
        y = FY0 + 1.5 + k * 2.6
        zz = (y - FY0) * WT / (QY0 - FY0) + 1.7
        R.light(sphere(FX1 + 0.02, y, zz, 0.05, 8, 4, 'e_candle'))
    # the pier's face: tall bookcases, and at its south end a low one you can walk through, a tall one over it
    sh(R, '-x', EX, 12.2, QY0 - 0.25, rows=16, frame='walnut')
    sh(R, '-x', EX, QY1 + 0.25, EY1 - 0.1, rows=12, frame='walnut')
    sh(R, '-x', EX, 10.5, 12.1, rows=6, frame='walnut', solid=False)
    sh(R, '-x', EX, 10.5, 12.1, z=2.63, rows=10, frame='walnut')


def hall(R):
    """Tall bookcases round the walls with rolling ladders; reading tables under the lake."""
    rows = 16
    for (a, b) in ((0.6, 6.2), (9.8, 15.4), (16.6, 22.2), (25.8, W - 0.6)):
        R.shelf(a, T, 0, b - a, '+y', rows=rows, frame='walnut')
        R.shelf(b, D - T, 0, b - a, '-y', rows=rows, frame='walnut')
        R.shelf(T, b, 0, b - a, '+x', rows=rows, frame='walnut')
    for (a, b) in ((0.6, 6.2), (25.8, W - 0.6)):
        R.shelf(W - T, a, 0, b - a, '-x', rows=rows, frame='walnut')
    for (x, y, a) in ((3.0, T + 0.34, math.pi / 2), (20.0, D - T - 0.34, -math.pi / 2), (T + 0.34, 13.0, 0.0)):
        R.nocol.add(ladder_geo(x, y, a))
    # reading tables under the lake, a globe, a compass rose in the floor
    for (x0, y0, x1, y1) in ((7.5, 7.0, 13.5, 8.2), (18.5, 7.0, 24.5, 8.2), (7.5, 23.8, 13.5, 25.0), (18.5, 23.8, 24.5, 25.0), (21.0, 12.0, 22.2, 19.0)):
        reading_table(R, x0, y0, x1, y1, lamps=3)
    R.parts.add(cyl(9.0, 18.5, 0, 0.9, 0.08, 8, side='brass', top='brass'))
    R.nocol.add(sphere(9.0, 18.5, 1.3, 0.4, 16, 8, 'ivory'))
    R.nocol.add(ring(9.0, 18.5, 1.28, 1.32, 0.44, 0.48, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.col.add(cyl(9.0, 18.5, 0, 1.8, 0.5, 8))
    rose = Geo()
    for k in range(8):
        a = math.pi * k / 4; L = 3.2 if k % 2 == 0 else 1.9
        pts = [(16 + L * math.cos(a), 16 + L * math.sin(a)), (16 + 0.35 * math.cos(a + 0.8), 16 + 0.35 * math.sin(a + 0.8)),
               (16, 16), (16 + 0.35 * math.cos(a - 0.8), 16 + 0.35 * math.sin(a - 0.8))]
        rose.add(poly_prism(pts, 0, 0.004 + 0.001 * k, 'slate' if k % 2 else 'brass', 'slate' if k % 2 else 'brass', 'slate'))
    R.parts.add(rose)
    R.parts.add(ring(16, 16, 0, 0.003, 3.3, 3.45, 48, top='brass', bottom='brass', inner='brass', outer='brass'))
    for (x, y, f) in ((T + 0.1, 3.0, 0.0), (T + 0.1, 29.0, 0.0), (3.0, D - T - 0.1, -math.pi / 2), (29.0, T + 0.1, math.pi / 2)):
        R.nocol.add(box(x - 0.08, y - 0.08, 5.6, x + 0.08, y + 0.08, 5.9, 'brass'))
        R.light(sphere(x + 0.3 * math.cos(f), y + 0.3 * math.sin(f), 6.0, 0.13, 8, 4, 'e_lamp'))


def ladder_geo(x, y, a, h=6.4, lean=0.9):
    """A rolling library ladder against a bookcase face (drawn only)."""
    g = Geo()
    for s in (-0.25, 0.25):
        g.add(beam((lean, s, 0.08), (0.05, s, h), 0.06, 'oak', 0.04))
    for k in range(1, int(h / 0.3)):
        t = k / int(h / 0.3)
        g.add(box(lean + (0.05 - lean) * t - 0.03, -0.25, h * t - 0.015, lean + (0.05 - lean) * t + 0.03, 0.25, h * t + 0.015, 'oak'))
    g.add(box(-0.02, -0.35, h - 0.03, 0.06, 0.35, h + 0.02, 'brass'))
    return g.xform(a, x, y, 0)
