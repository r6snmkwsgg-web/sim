"""The Ceiling Garden: a two-storey reading room whose ceiling is a garden, grass and gravel paths and
clipped hedges, benches and lamp posts, and old trees hanging from it with their crowns ten metres over
the reading tables. In the middle a fountain pours upward, a column of water climbing out of its basin
all the way to a stone bowl in the lawn overhead. Behind a bookcase in the west wall a stair climbs the
thickness of the wall to a balcony up among the roots, just under the grass."""
from kit_h8 import *
from kit_h3 import window, strands as water_threads
from kit_e import bench, lathe

W = D = 32.0
CT = 15.2
ZC = CT / 2
HX0 = 3.0                          # the hall's west wall (the stair runs inside the wall behind it)
CX, CY = (HX0 + W - T) / 2, 16.0   # the fountain
SX0, SX1 = 0.7, 2.7                # the stair channel
SY0, SY1 = 11.6, 29.6              # its foot and head
BZ = 12.0                          # the balcony


def make():
    R = Room('ceilinggarden', 2, 2, levels=2, res=2048)
    skip = [(s, i, 1) for s in 'SNWE' for i in range(2)]
    seal(R, skip, floor='marble', wall='tile')
    R.cut(box(HX0, T - 0.02, 0, W - T + 0.02, D - T + 0.02, CT, 'tile', bottom='marble', top='grass'))
    dp = arch_profile(0, DW, 0, DJ)
    for c in (8.0, 24.0):
        R.cut(prism([(p + c, q) for p, q in dp], 'x', T + 0.4, HX0 + 0.05, arch_mats(len(dp), 'marble', 'tile')))
    for c in (8.0, 16.0, 24.0):
        window(R, 'E', c, 8.6, 3.0, 3.8, em='e_skydome', mull=2, trans=2)
    garden(R)
    fountain(R)
    hall(R)
    stair(R)
    balcony(R)
    cx = CX
    g = navloop(R, [(5.2, 2.6), (cx, 2.6), (29, 2.6), (29, 29.4), (cx, 29.4), (5.2, 29.4), (5.2, 16)])
    a, b = R.navpt(cx - 4.2, CY), R.navpt(cx + 4.2, CY)
    R.link(g[1], a, g[4]); R.link(g[1], b, g[4])
    fx(R, 'dust', [HX0, T, 1, W - T, D - T, 12])
    secret(R, 5.0, 28.6, BZ, 'The Root Balcony',
           'At the top of the stair in the wall a balcony hangs just under the lawn, and the roots of the garden come down around you like rain that has stopped. From here the trees are the right way up, very nearly.')
    return finish(R, 'The Ceiling Garden', weight=3, probe=(CX, 8, 5.0), top=CT,
                  blurb='The garden is on the ceiling. The trees hang down over the reading tables, and the fountain has decided to go up.')


def garden(R):
    rnd = random.Random(76)

    def build():
        # gravel paths in a cross, clipped hedges along them, beds of flowers
        R.parts.add(box(CX - 1.2, T, 0, CX + 1.2, D - T, 0.03, 'tile'))
        R.parts.add(box(HX0, CY - 1.2, 0, W - T, CY + 1.2, 0.03, 'tile'))
        R.parts.add(cyl(CX, CY, 0, 0.035, 4.4, 32, side='tile', top='tile'))
        for (x0, y0, x1, y1) in ((HX0 + 1.5, CY + 1.5, CX - 5.0, CY + 2.3), (HX0 + 1.5, CY - 2.3, CX - 5.0, CY - 1.5),
                                 (CX + 5.0, CY + 1.5, W - 2.0, CY + 2.3), (CX + 5.0, CY - 2.3, W - 2.0, CY - 1.5),
                                 (CX - 2.3, 2.0, CX - 1.5, CY - 5.0), (CX + 1.5, 2.0, CX + 2.3, CY - 5.0),
                                 (CX - 2.3, CY + 5.0, CX - 1.5, D - 2.0), (CX + 1.5, CY + 5.0, CX + 2.3, D - 2.0)):
            R.parts.add(box(x0, y0, 0, x1, y1, 0.9, 'leaf'))
            R.nocol.add(box(x0 - 0.05, y0 - 0.05, 0.8, x1 + 0.05, y1 + 0.05, 1.0, 'grass'))
        # benches facing each other across the paths, lamp posts beside them
        for (x0, y0, x1, y1) in ((CX - 3.8, CY + 1.3, CX - 2.2, CY + 1.8), (CX + 2.2, CY - 1.8, CX + 3.8, CY - 1.3),
                                 (CX + 1.3, CY + 2.2, CX + 1.8, CY + 3.8), (CX - 1.8, CY - 3.8, CX - 1.3, CY - 2.2)):
            bench(R, x0, y0, x1, y1, m='walnut', spots=False)
        for (x, y) in ((CX - 4.6, CY + 1.6), (CX + 4.6, CY - 1.6), (CX + 1.6, CY + 4.6), (CX - 1.6, CY - 4.6),
                       (CX - 1.6, 5.0), (CX + 1.6, 27.0), (8.0, CY + 1.6), (27.5, CY - 1.6)):
            lamp_post(R, x, y, 0.0, 2.8, m='e_lamp')
        # the upside-down fountain's bowl: a stone basin on a stem, standing in the lawn
        R.parts.add(lathe(CX, CY, [(0.0, 0.0), (0.9, 0.0), (0.9, 0.2), (0.35, 0.4), (0.3, 1.1), (0.5, 1.3), (1.5, 1.45), (1.7, 1.75), (1.55, 1.8), (0.0, 1.55)], 24, 'tile'))
        R.nocol.add(cyl(CX, CY, 1.55, 1.7, 1.52, 24, side='foam', top='foam', bottom='foam'))
        # trees
        for (x, y, h) in ((9.5, 8.0, 7.2), (26.0, 8.5, 6.6), (10.5, 23.0, 6.8), (25.5, 24.0, 7.4), (CX + 5.5, CY + 6.5, 5.6), (CX - 6.0, CY - 6.5, 5.4)):
            tree_geo(R, x, y, rnd, h=h, spread=3.3, crown=1.5)
    inverted(R, build, ZC)
    # ivy down the upper walls
    for k in range(70):
        side = rnd.choice('SNE')
        t = rnd.uniform(HX0 + 0.5 if side in 'SN' else T + 0.5, W - T - 0.5 if side in 'SN' else D - T - 0.5)
        if side == 'E' and any(abs(t - c) < 1.8 for c in (8.0, 16.0, 24.0)): continue
        x, y = (t, T + 0.04) if side == 'S' else (t, D - T - 0.04) if side == 'N' else (W - T - 0.04, t)
        vine(R, x, y, CT - rnd.uniform(1.5, 6.0), CT, rnd, m='leaf')


def fountain(R):
    """A round basin on the floor, shallow water in it, and a column of water pouring up to the lawn."""
    r = 2.6
    R.parts.add(ring(CX, CY, 0, 0.5, r, r + 0.35, 40, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.parts.add(cyl(CX, CY, 0, 0.02, r, 40, side='slate', top='slate'))
    R.water.append(dict(cx=CX, cy=CY, r=r - 0.02, top=0.34, bot=0.02))
    # the pedestal and its bowl, the column springing from it
    R.parts.add(lathe(CX, CY, [(0.0, 0.0), (0.6, 0.0), (0.4, 0.3), (0.25, 0.9), (0.9, 1.1), (1.05, 1.3), (0.0, 1.25)], 20, 'tile'))
    R.col.add(cyl(CX, CY, 0, 3.0, 1.0, 12))
    top = CT - 1.7
    for (rr, m, segs) in ((0.3, 'foam', 14), (0.22, 'chrome', 10)):
        R.nocol.add(cyl(CX, CY, 1.2, top, rr, segs, side=m, caps=False))
    R.nocol.add(cone(CX, CY, 1.2, 2.2, 0.75, 0.3, 14, m='foam'))
    R.nocol.add(cone(CX, CY, top - 0.8, top, 0.3, 0.9, 14, m='foam'))
    water_threads(R, CX - 0.45, CY, CX + 0.45, CY, 1.3, top, 14, seed=3, m='chrome')
    water_threads(R, CX, CY - 0.45, CX, CY + 0.45, 1.3, top, 14, seed=4, m='chrome')
    for k in range(10):
        a = 2 * math.pi * k / 10
        R.light(box(CX + (r - 0.03) * math.cos(a) - 0.1, CY + (r - 0.03) * math.sin(a) - 0.1, 0.05, CX + (r - 0.03) * math.cos(a) + 0.1, CY + (r - 0.03) * math.sin(a) + 0.1, 0.12, 'e_pool'))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        x, y = CX + 4.2 * math.cos(a), CY + 4.2 * math.sin(a)
        g = Geo(); b0 = box(-0.9, -0.25, 0.4, 0.9, 0.25, 0.47, 'walnut')
        for s in (-0.8, 0.8): b0.add(box(s - 0.05, -0.2, 0, s + 0.05, 0.2, 0.4, 'walnut'))
        g.add(b0); g.xform(a + math.pi / 2, x, y, 0); R.parts.add(g)
        R.spot('sit', x, y, 0.47, a + math.pi)


def hall(R):
    """Bookcases round the lower walls, reading tables with green lamps between the garden's shadows."""
    rows = 12
    for (a, b) in ((HX0 + 0.3, 6.2), (9.8, 15.4), (16.6, 22.2), (25.8, W - 0.6)):
        R.shelf(a, T, 0, b - a, '+y', rows=rows, frame='walnut')
        R.shelf(b, D - T, 0, b - a, '-y', rows=rows, frame='walnut')
    wall_cases(R, rows=rows, frame='walnut', sides='E')
    for (a, b) in ((0.6, 6.0), (12.0, 22.0), (26.0, D - 0.6)):
        R.shelf(HX0, b, 0, b - a, '+x', rows=rows, frame='walnut')
    R.shelf(HX0, 11.5, 0, 1.4, '+x', rows=rows, frame='walnut', solid=False)       # the way in to the stair
    for (x0, y0, x1, y1) in ((7.0, 5.2, 13.0, 6.4), (21.0, 5.2, 27.0, 6.4), (7.0, 25.6, 13.0, 26.8), (21.0, 25.6, 27.0, 26.8)):
        reading_table(R, x0, y0, x1, y1, lamps=3)


def stair(R):
    """The stair inside the west wall: a narrow slot from a vestibule behind the false bookcase to the balcony."""
    prof = [(9.95, 0.0), (SY0, 0.0), (SY1, BZ), (D - T - 0.05, BZ), (D - T - 0.05, 14.8), (SY1 - 2.0, 14.8), (SY0, 3.0), (9.95, 3.0)]
    R.cut(prism(prof, 'x', SX0, SX1, ['floor', 'tile', 'floor', 'tile', 'plaster', 'plaster', 'plaster', 'tile'], cap='tile'))
    R.cut(box(SX1 - 0.02, 10.05, 0, HX0 + 0.02, 11.55, 2.6, 'tile', bottom='floor', top='plaster'))
    R.flight(SX0 + 0.05, SY0, 0.0, SX1 - SX0 - 0.1, 60, BZ / 60, (SY1 - SY0) / 60, '+y', m='oak', riser='walnut', side='tile')
    R.cut(box(SX1 - 0.02, SY1 - 0.1, BZ, HX0 + 0.02, D - T - 0.05, 14.8, 'tile', bottom='floor', top='plaster'))
    for k in range(6):
        y = SY0 + 1.5 + k * 3.0
        z = (y - SY0) * BZ / (SY1 - SY0) + 1.6
        R.light(sphere(SX0 + 0.12, y, z, 0.06, 8, 4, 'e_candle'))
        R.nocol.add(box(SX0, y - 0.06, z - 0.2, SX0 + 0.08, y + 0.06, z - 0.08, 'brass'))
    R.nocol.add(box(SX0, 10.4, 0.0, SX0 + 0.3, 11.2, 0.9, 'walnut'))
    candle(R, SX0 + 0.15, 10.8, 0.9, h=0.15)


def balcony(R):
    """Up among the roots: a railed balcony just under the lawn, a bench and a lantern on it."""
    x0, y0, x1, y1 = HX0, 25.2, 7.4, D - T
    R.parts.add(box(x0 - 0.02, y0, BZ - 0.4, x1, y1 + 0.02, BZ, 'oak', sides='walnut', bottom='walnut'))
    for k in range(3):
        R.parts.add(box(x0, y0 + 0.4 + k * 2.6, BZ - 1.6, x0 + 0.4, y0 + 0.8 + k * 2.6, BZ - 0.4, 'walnut'))
    iron_rail(R, x1 - 0.05, y0, x1 - 0.05, y1, BZ)
    iron_rail(R, x0, y0 + 0.05, x1, y0 + 0.05, BZ)
    bench(R, x0 + 0.2, 27.2, x0 + 0.7, 29.2, m='walnut', face=0.0, z=BZ)
    lamp_post(R, 6.6, 30.8, BZ, 1.5, m='e_amber')
    open_book(R, x0 + 0.45, 27.8, BZ + 0.45, 1.2)
    # roots hanging round it from the lawn
    rnd = random.Random(12)
    for k in range(60):
        x, y = rnd.uniform(x0 + 0.2, x1 + 3.5), rnd.uniform(y0 - 3.0, y1 - 0.2)
        inside = x < x1 and y > y0
        L = rnd.uniform(0.4, 1.2) if inside else rnd.uniform(1.5, 4.5)
        p0 = (x, y, CT)
        p1 = (x + rnd.uniform(-0.3, 0.3), y + rnd.uniform(-0.3, 0.3), CT - L * 0.5)
        p2 = (x + rnd.uniform(-0.4, 0.4), y + rnd.uniform(-0.4, 0.4), CT - L)
        R.nocol.add(tube([p0, p1, p2], [0.05, 0.03, 0.01], 5, 'root'))
    R.spot('plaque', x0 + 0.05, 30.4, BZ + 1.5, 0.0, text='Please keep off the grass.')
