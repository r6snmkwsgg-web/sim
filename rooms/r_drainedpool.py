"""The Drained Pool: a public swimming bath with the water let out, white tiles and dark lane lines,
daylight falling through a glass roof. Bookcases stand on the pool bottom, down the slope to the deep
end, with reading tables between them. At the deep end a very tall diving tower climbs the east wall
in three flights, a railed platform at every landing. In the deep end, one bookcase against the wall
is not there, and behind it is the pump room, where somebody has been reading by the filters."""
from kit_h9 import *

W, D = 32.0, 32.0
PX0, PX1, PY0, PY1 = 6.0, 26.0, 8.0, 24.0      # the pool
S0, S1 = 13.0, 19.0                             # the slope from the shallow to the deep end
ZS, ZD = -1.0, -1.9
TX0, TX1 = 30.2, 31.5                           # the tower's stair, against the east wall
FY = 9.7                                        # its foot
RUN, RISE, NS = 0.3, 0.2, 9                     # each flight: 9 steps of 0.2 = 1.8 m
LAND = 1.5
KX0, KX1, KY0, KY1, KZ = 26.4, 31.3, 12.6, 19.4, -1.95   # the pump room, under the east deck
HD0, HD1 = 15.0, 16.2                           # its door in the pool wall


def pool_z(x):
    if x <= S0: return ZS
    if x >= S1: return ZD
    return ZS + (ZD - ZS) * (x - S0) / (S1 - S0)


def slope_y(x0, x1, y0, y1, bot, top0, top1, m):
    """A solid along y whose top rises from top0 at y0 to top1 at y1."""
    g = slope_box(y0, y1, -x1, -x0, bot, bot, top0, top1, m)
    g.v = [(-b, a, c) for (a, b, c) in g.v]
    return g


def make():
    R = Room('drainedpool', 2, 2, res=2048)
    R.sockets(floor='wtile', wall='wtile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP - 0.1, 'wtile', bottom='wtile', top='plaster'))
    hall(R)
    pool(R)
    stacks(R)
    tower(R)
    pump_room(R)
    fx(R, 'dust', [PX0, PY0, ZD, PX1, PY1, 7.0])
    navloop(R, [(3.0, 3.0), (16.0, 4.0), (29.0, 3.0), (28.0, 16.0), (29.0, 29.0), (16.0, 28.0), (3.0, 29.0), (3.0, 16.0)])
    p = [R.navpt(x, y, pool_z(x)) for (x, y) in ((7.2, 12.8), (10.2, 12.8), (16.0, 14.6), (22.8, 14.2))]
    R.link(*p)
    secret(R, 28.6, 16.0, KZ, 'The Pump Room',
           'Behind the bookcase in the deep end: the pump room, warm and humming, the filters thick with pages. On the workbench is a logbook of the water level, kept daily, and the last entry says: still empty. Still reading.')
    return finish(R, 'The Drained Pool', weight=3, probe=(16, 16, 1.0), top=TOP - 0.1,
                  blurb='A swimming bath with the water let out. The tiles are dry, the lane lines run down the slope to the deep end, and at the bottom, where the swimmers should be, are the bookcases.')


# ---------------------------------------------------------------------------
def hall(R):
    # a stone band above the tiles, and high arched windows in the long walls
    for (x0, y0, x1, y1) in ((T, T, W - T, T + 0.03), (T, D - T - 0.03, W - T, D - T), (T, T, T + 0.03, D - T), (W - T - 0.03, T, W - T, D - T)):
        R.nocol.add(box(x0, y0, 2.4, x1, y1, TOP - 0.1, 'tile'))
        R.nocol.add(box(x0, y0, 2.3, x1, y1, 2.4, 'slate'))
    for c in (4.0, 12.0, 16.0, 20.0, 28.0):
        window(R, 'S', c, 3.4, 2.2, 2.6, em='e_sky', mull=2, trans=2)
        window(R, 'N', c, 3.4, 2.2, 2.6, em='e_sky', mull=2, trans=2)
    # the glass roof over the pool: panes of sky in an iron grid
    zc = TOP - 0.12
    R.light(panel_z(zc, PX0 - 1.0, PY0 - 1.0, PX1 + 1.0, PY1 + 1.0, 'e_sky', up=False))
    for k in range(12):
        x = PX0 - 1.0 + k * (PX1 - PX0 + 2.0) / 11
        R.nocol.add(box(x - 0.06, PY0 - 1.0, zc - 0.25, x + 0.06, PY1 + 1.0, zc, 'iron'))
    for k in range(10):
        y = PY0 - 1.0 + k * (PY1 - PY0 + 2.0) / 9
        R.nocol.add(box(PX0 - 1.0, y - 0.05, zc - 0.18, PX1 + 1.0, y + 0.05, zc, 'iron'))
    # books round the deck, broken at the doorways
    rows = 9
    segs = [(0.6, 6.2), (9.8, 22.2), (25.8, W - 0.6)]
    for (a, b) in segs:
        sh(R, '+y', T, a, b, rows=rows, frame='walnut', depth=0.32)
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut', depth=0.32)
        sh(R, '+x', T, a, b, rows=rows, frame='walnut', depth=0.32)
    sh(R, '-x', W - T, 25.8, W - 0.6, rows=rows, frame='walnut', depth=0.32)
    sh(R, '-x', W - T, 0.6, 6.2, rows=rows, frame='walnut', depth=0.32)
    # benches and green lamps on the deck
    for (x, y, a) in ((3.2, 12.0, 0.0), (3.2, 20.0, 0.0), (12.0, 5.2, math.pi / 2), (20.0, 5.2, math.pi / 2), (12.0, 26.8, -math.pi / 2), (20.0, 26.8, -math.pi / 2)):
        g = box(-0.9, -0.22, 0.42, 0.9, 0.22, 0.47, 'oak')
        for s in (-0.7, 0.7): g.add(box(s - 0.05, -0.2, 0, s + 0.05, 0.2, 0.42, 'wtile'))
        R.parts.add(g.xform(a + math.pi / 2, x, y, 0))
        R.spot('sit', x, y, 0.47, a)
    for (x, y) in ((1.4, 1.4), (W - 1.4, 1.4), (1.4, D - 1.4), (W - 1.4, D - 1.4), (16.0, 1.4), (16.0, D - 1.4)):
        floor_lamp(R, x, y, 1.7, m='e_amber')
    # a lifeguard's chair on the south side
    g = Geo()
    for (dx, dy) in ((-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)):
        g.add(beam((17.0 + dx, 6.6 + dy, 0.0), (17.0 + dx * 0.6, 6.8 + dy * 0.6, 1.9), 0.06, 'wtile'))
    g.add(box(16.6, 6.4, 1.9, 17.4, 7.2, 1.98, 'oak'))
    g.add(box(16.6, 6.4, 1.98, 17.4, 6.5, 2.6, 'oak'))
    R.parts.add(g)


def pool(R):
    R.cut(box(PX0, PY0, ZS, S0 + 0.01, PY1, 0.1, 'wtile', bottom='wtile'))
    R.cut(slope_box(S0, S1, PY0, PY1, ZS, ZD, 0.1, 0.1, 'wtile'))
    R.cut(box(S1 - 0.01, PY0, ZD, PX1, PY1, 0.1, 'wtile', bottom='wtile'))
    # a dark band at the coping, lane lines down the floor, crosses on the end walls
    for (x0, y0, x1, y1) in ((PX0 - 0.3, PY0 - 0.3, PX1 + 0.3, PY0), (PX0 - 0.3, PY1, PX1 + 0.3, PY1 + 0.3), (PX0 - 0.3, PY0, PX0, PY1), (PX1, PY0, PX1 + 0.3, PY1)):
        R.nocol.add(box(x0, y0, 0.0, x1, y1, 0.006, 'slate'))
    for k in range(1, 8):
        y = PY0 + k * (PY1 - PY0) / 8
        R.nocol.add(box(PX0 + 1.5, y - 0.12, ZS, S0, y + 0.12, ZS + 0.008, 'slate'))
        R.nocol.add(slope_box(S0, S1, y - 0.12, y + 0.12, ZS, ZD, ZS + 0.008, ZD + 0.008, 'slate'))
        R.nocol.add(box(S1, y - 0.12, ZD, PX1 - 1.5, y + 0.12, ZD + 0.008, 'slate'))
        R.nocol.add(box(PX1 - 1.5, y - 0.45, ZD, PX1 - 1.26, y + 0.45, ZD + 0.008, 'slate'))
        for (x, f) in ((PX0, 1), (PX1, -1)):
            zb = ZS if f > 0 else ZD
            xa, xb = sorted((x, x + 0.008 * f))
            R.nocol.add(box(xa, y - 0.12, zb + 0.3, xb, y + 0.12, -0.25, 'slate'))
            R.nocol.add(box(xa, y - 0.4, -0.55, xb, y + 0.4, -0.31, 'slate'))
    # steps down at both corners of the shallow end, and one flight out of the deep end
    for y0 in (PY0 + 0.25, PY1 - 2.65):
        R.flight(PX0 + 1.5, y0, ZS, 2.4, 5, 0.2, 0.3, '-x', m='wtile', side='wtile')
        for y in (y0 - 0.05, y0 + 2.45):
            stair_rail(R, PX0 + 1.4, y, ZS + 0.2, PX0 + 0.1, y, -0.05, m='brass')
    R.flight(PX1 - 10 * 0.3, PY0 + 0.05, ZD, 1.5, 10, 0.19, 0.3, '+x', m='wtile', side='wtile')
    stair_rail(R, PX1 - 2.9, PY0 + 1.58, ZD + 0.19, PX1 - 0.1, PY0 + 1.58, -0.1, m='brass')
    R.parts.add(slope_box(PX1 - 3.0, PX1, PY0 + 1.55, PY0 + 1.62, ZD, ZD, ZD + 0.1, 0.0, 'wtile'))
    # brass rails round the deep part of the pool, open at the steps
    rail_line(R, S0, PY0 - 0.12, 0.0, PX1 + 0.12, PY0 - 0.12, 0.0, m='brass', post='brass', spacing=1.2, mid=True)
    rail_line(R, S0, PY1 + 0.12, 0.0, PX1 + 0.12, PY1 + 0.12, 0.0, m='brass', post='brass', spacing=1.2, mid=True)
    rail_line(R, PX1 + 0.12, PY0 + 1.7, 0.0, PX1 + 0.12, PY1 + 0.12, 0.0, m='brass', post='brass', spacing=1.2, mid=True)
    # pool ladders (to look at: nobody climbs them)
    for (x, y, f) in ((10.0, PY0, 1), (22.0, PY0 + 0.0, 1), (10.0, PY1, -1), (22.0, PY1, -1)):
        zb = pool_z(x)
        for dx in (-0.25, 0.25):
            R.nocol.add(tube([(x + dx, y - 0.25 * f, 0.9), (x + dx, y - 0.25 * f, 0.05), (x + dx, y + 0.05 * f, -0.1), (x + dx, y + 0.08 * f, zb + 0.2)], 0.025, 6, 'chrome'))
        for k in range(int((0 - zb) / 0.3)):
            z = -0.2 - k * 0.3
            R.nocol.add(box(x - 0.25, min(y, y + 0.14 * f), z - 0.02, x + 0.25, max(y, y + 0.14 * f), z + 0.02, 'chrome'))


def stacks(R):
    """Bookcases standing on the bottom of the pool, down the slope; tables between."""
    for (x, a, b) in ((8.8, 11.2, 14.4), (8.8, 17.6, 20.8), (11.6, 11.2, 14.4), (11.6, 17.6, 20.8),
                      (21.6, 10.4, 13.6), (21.6, 18.4, 21.6), (24.4, 10.8, 13.6), (24.4, 18.4, 21.2)):
        stack(R, 'y', x, a, b, z=pool_z(x), rows=5, frame='walnut')
        top = pool_z(x) + 5 * 0.42 + 0.14 + 0.06
        desk_lamp(R, x + 0.25, (a + b) / 2, top)
    for (x0, x1, y0, y1) in ((9.3, 11.1, 15.2, 16.8), (22.0, 24.0, 15.0, 17.0)):
        z = pool_z(x0)
        R.parts.add(table(x0, y0, x1, y1, 0.76, 'walnut', top='leather').xform(0, 0, 0, z))
        desk_lamp(R, (x0 + x1) / 2, (y0 + y1) / 2, z + 0.76)
        for (xx, a) in ((x0 - 0.45, 0.0), (x1 + 0.45, math.pi)):
            for yy in ((y0 + y1) / 2 - 0.4, (y0 + y1) / 2 + 0.4):
                R.parts.add(chair(xx, yy, a).xform(0, 0, 0, z)); R.spot('sit', xx, yy, z + 0.48, a)
    rnd = random.Random(86)
    for (x, y, n) in ((14.5, 15.0, 7), (18.2, 17.2, 4), (17.0, 10.6, 5), (15.2, 21.4, 9)):
        book_pile(R, x, y, pool_z(x), n, rnd, rnd.uniform(0, 3))


# ---------------------------------------------------------------------------
def tower(R):
    """The diving tower: three flights up the east wall, a railed platform at each landing."""
    y = FY
    lvl = []
    for i in range(3):
        z0 = i * NS * RISE
        R.flight(TX0, y, z0, TX1 - TX0, NS, RISE, RUN, '+y', m='concrete', side='concrete')
        L = NS * RUN
        R.parts.add(slope_y(TX0, TX1, y, y + L, 0.0, max(z0, 0.02), z0 + NS * RISE - RISE, 'concrete'))
        stair_rail(R, TX0 + 0.05, y + 0.3, z0 + RISE, TX0 + 0.05, y + L, z0 + NS * RISE, m='brass')
        y += L
        z = z0 + NS * RISE
        lvl.append((y, z))
        R.parts.add(box(TX0, y, 0.0, TX1, y + LAND, z, 'concrete'))
        y += LAND
    # the platforms, reaching out over the pool
    for i, (ya, z) in enumerate(lvl):
        x0 = PX1 - 1.2 - 0.4 * i
        yb = ya + LAND
        R.parts.add(box(x0, ya, z - 0.3, TX0, yb, z, 'concrete', top='wtile'))
        for x in (27.4, 29.0):
            R.parts.add(box(x - 0.2, ya + 0.35, 0.0, x + 0.2, ya + 0.75, z - 0.3, 'concrete'))
        rail(R, x0 + 0.06, ya + 0.06, x0 + 0.06, yb - 0.06, z, m='brass', post=0.8)
        rail(R, x0 + 0.06, ya + 0.06, TX0, ya + 0.06, z, m='brass', post=1.0)
        rail(R, x0 + 0.06, yb - 0.06, TX0 - 0.06, yb - 0.06, z, m='brass', post=1.0)
        # a diving board past the rail
        R.nocol.add(box(x0 - 2.2, ya + 0.45, z - 0.08, x0, ya + LAND - 0.45, z, 'oak'))
        R.light(sphere(TX0 - 0.3, ya + 0.3, z + 1.9, 0.09, 8, 4, 'e_lamp'))
    # the rails at the stair's far side: the landing's open edges
    y_top, z_top = lvl[-1]
    rail(R, TX0 + 0.06, y_top + LAND - 0.06, TX1 - 0.06, y_top + LAND - 0.06, z_top, m='brass', post=1.0)


def pump_room(R):
    """Under the east deck, behind a bookcase in the deep end."""
    R.cut(box(KX0, KY0, KZ, KX1, KY1, -0.25, 'wtile', bottom='concrete', top='concrete'))
    R.cut(box(PX1 - 0.05, HD0, ZD, KX0 + 0.05, HD1, -0.4, 'iron', bottom='concrete', top='iron'))
    shelf(R, PX1, HD0 - 0.25, ZD, HD1 - HD0 + 0.5, '-x', rows=3, frame='walnut', solid=False)
    # pumps, filters, pipes into the pool wall, valves, gauges
    for (y, m) in ((13.6, 'green'), (18.4, 'green')):
        g = cyl(0, 0, 0, 1.8, 0.4, 14, side=m, top='iron', bottom='iron')
        rot(g, 'y', math.pi / 2)
        R.parts.add(g.xform(0, 27.6, y, KZ + 0.55))
        R.parts.add(box(27.5, y - 0.3, KZ, 29.5, y + 0.3, KZ + 0.15, 'iron'))
    for (x, y) in ((30.6, 13.3), (30.6, 14.4), (30.6, 17.6), (30.6, 18.7)):
        R.parts.add(cyl(x, y, KZ, KZ + 1.45, 0.42, 14, side='oxblood', top='iron', bottom='iron'))
        R.nocol.add(cyl(x - 0.42, y, KZ + 1.0, KZ + 1.04, 0.1, 10, side='brass', top='ivory', bottom='ivory').xform(0, 0, 0, 0))
    for z, r in ((-0.55, 0.1), (-0.8, 0.07)):
        R.nocol.add(xtube(KX0, KX1 - 0.2, KY0 + 0.25, z, r, 10, 'iron'))
        R.nocol.add(xtube(KX0, KX1 - 0.2, KY1 - 0.25, z, r, 10, 'iron'))
    for y in (13.6, 18.4):
        R.nocol.add(tube([(PX1 + 0.1, y, ZD + 0.5), (27.6, y, KZ + 0.55)], 0.12, 10, 'iron'))
    # a workbench with a lamp and the logbook, a stool, a shelf of manuals, a cot
    R.parts.add(table(28.0, 15.2, 29.9, 16.8, 0.8, 'oak', top='leather').xform(0, 0, 0, KZ))
    desk_lamp(R, 29.5, 15.5, KZ + 0.8)
    g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, 'green'); g.add(box(-0.19, -0.13, 0.02, 0.19, 0.13, 0.05, 'ivory'))
    R.nocol.add(g.xform(1.4, 28.9, 16.1, KZ + 0.8))
    R.parts.add(cyl(27.6, 16.0, KZ, KZ + 0.5, 0.18, 10, side='oak', top='oak', bottom='oak'))
    R.spot('sit', 27.6, 16.0, KZ + 0.5, 0.0)
    sh(R, '-x', KX1, 15.0, 17.0, z=KZ, rows=3, frame='iron', depth=0.3)
    bulb(R, 28.8, 16.0, -0.7, r=0.08, m='e_lamp', top=-0.25)
    bulb(R, 29.5, 13.9, -0.7, r=0.06, m='e_dim', top=-0.25)
    bulb(R, 29.5, 18.1, -0.7, r=0.06, m='e_dim', top=-0.25)
    R.light(box(PX1 + 0.1, HD0 + 0.2, -0.55, PX1 + 0.14, HD1 - 0.2, -0.45, 'e_amber'))
