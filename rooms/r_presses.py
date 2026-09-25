"""The Press Hall: printing presses the size of locomotives in a vaulted hall two floors tall, rollers
turning, and out of every press a river of paper running away down the aisles. Galleries of books
round the walls above. Under the biggest press, if you crawl between its legs, a hatch goes down to
the ink room."""
from kit_h6 import *
from kit_f import flight_thin, rose

W = D = 32.0
GW = 3.0                      # gallery width
GZ = LH                       # gallery floor
VJ = 11.2                     # the vault springs here
PB = (16.0, 16.0, 11.0, 5.0, 7.0)   # the biggest press: centre, length (x), width (y), height
BED = 1.25                    # its bed: you crawl under it
INK = (12.2, 13.9, 19.6, 18.1)      # the ink room below it
IZ = -2.15
HX = (14.1, 15.35, 16.65)     # the hatch: x start, y range


def make():
    R = Room('presses', 2, 2, levels=2, res=2048, lo=-2.2)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP, 'tile', bottom='slate', top='plaster'))
    R.cut(box(T - 0.02, T - 0.02, GZ, W - T + 0.02, D - T + 0.02, VJ, 'tile', bottom='floor', top='plaster'))
    R.cut(box(GW + T, GW + T, TOP - 0.2, W - GW - T, D - GW - T, VJ + 0.1, 'tile', bottom='slate'))
    pr = arch_profile(16, W - 2 * T - 0.1, VJ - 0.05, 0.05, 36, rise=4.1)
    R.cut(prism(pr, 'y', T - 0.02, D - T + 0.02, ['tile'] + ['plaster'] * (len(pr) - 1), cap='plaster'))
    rs = rng(52)
    for k in range(8):
        y = 2.0 + k * 4.0
        R.nocol.add(prism(arc_band(16, W - 2 * T - 0.1, VJ, 4.1, 0.0, 0.4, 28), 'y', y - 0.22, y + 0.22, 'tile', cap='tile'))
    galleries(R, rs)
    stairs_up(R)
    windows(R)
    press(R, 8.6, 5.6, 8.5, 4.0, 5.6, rs, flip=False)
    press(R, 23.4, 26.4, 8.5, 4.0, 5.6, rs, flip=True)
    press(R, *PB, rs, legs=True)
    rivers(R, rs)
    ink_room(R, rs)
    desks(R, rs)
    lamps(R)
    fx(R, 'dust', [GW + T, GW + T, 0.5, W - GW - T, D - GW - T, 15.0])
    fx(R, 'dust', [T, T, 0.2, W - T, D - T, 7.0])
    # walking graph
    g = navloop(R, [(1.8, 1.8), (16.0, 1.8), (30.2, 1.8), (30.2, 16.0), (30.2, 30.2), (16.0, 30.2), (1.8, 30.2), (1.8, 16.0)])
    m = navloop(R, [(7.4, 10.5), (16.0, 11.2), (24.0, 11.2), (27.4, 20.5), (24.0, 21.0), (16.0, 20.8), (7.4, 21.0)])
    R.link(g[7], m[0]); R.link(g[3], m[3]); R.link(g[1], R.navpt(16.0, 8.0), m[1])
    u = navloop(R, [(1.8, 1.8), (16.0, 1.8), (30.2, 1.8), (30.2, 16.0), (30.2, 30.2), (16.0, 30.2), (1.8, 30.2), (1.8, 16.0)], z=GZ)
    return finish(R, 'The Press Hall', weight=3, probe=(16, 10.0, 3.0), top=R.hi,
                  blurb='The presses are running. Nobody is feeding them and nobody is reading what they print, and the paper has been coming out for long enough to fill the aisles.')


def galleries(R, rs):
    """The gallery round all four walls at the upper floor, balustraded, books all round it."""
    g0, g1 = GW + T, W - GW - T
    lz = GZ
    for (x0, y0, x1, y1) in ((g0 - 0.2, g0 - 0.2, g1 + 0.2, g0), (g0 - 0.2, g1, g1 + 0.2, g1 + 0.2), (g0 - 0.2, g0, g0, 16.0 - 1.2), (g0 - 0.2, 16.0 + 1.2, g0, g1),
                             (g1, g0, g1 + 0.2, 16.0 - 1.2), (g1, 16.0 + 1.2, g1 + 0.2, g1)):
        R.parts.add(box(x0, y0, lz, x1, y1, lz + 1.0, 'tile', skip=('-z',)))
        R.parts.add(box(x0 - 0.03, y0 - 0.03, lz + 1.0, x1 + 0.03, y1 + 0.03, lz + 1.06, 'brass'))
    # corbels under the gallery edge
    for k in range(9):
        p = g0 + (g1 - g0) * k / 8
        for (x, y) in ((p, g0), (p, g1), (g0, p), (g1, p)):
            R.parts.add(box(x - 0.25, y - 0.25, TOP - 1.2, x + 0.25, y + 0.25, TOP - 0.2, 'tile'))
    # bookcases on the upper walls, broken at the doorways
    rows = 7
    for (a, b) in ((0.7, 6.3), (9.7, 22.3), (25.7, D - 0.7)):
        sh(R, '+x', T, a, b, z=GZ, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, z=GZ, rows=rows, frame='walnut')
        sh(R, '+y', T, a, b, z=GZ, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, z=GZ, rows=rows, frame='walnut')
    # and on the lower walls
    rows = 12
    for (a, b) in ((0.7, 6.3), (9.7, 22.3), (25.7, D - 0.7)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')


def stairs_up(R):
    """Two long flights up to the gallery: one on the east side climbing north, one on the west
    climbing south, each landing in a gap in the balustrade."""
    n, rise, run, w = 40, GZ / 40, 0.3, 2.0
    g0, g1 = GW + T, W - GW - T
    # east: climbs +y, its top at y = 16 - 1.2 .. landing to 16 + 1.2
    x0 = g1 - w - 0.05
    ytop = 16.0 - 1.2
    y0 = ytop - n * run
    flight_thin(R, x0, y0, 0.0, w, n, rise, run, '+y', m='slate', riser='tile', side='tile', under='plaster')
    R.parts.add(box(x0, ytop, TOP - 0.25, g1 + 0.02, 16.0 + 1.2, GZ, 'slate', sides='tile', bottom='plaster'))
    stair_rail(R, x0 + 0.05, y0 + run, rise, x0 + 0.05, ytop, GZ)
    stair_rail(R, x0 + w - 0.05, y0 + run, rise, x0 + w - 0.05, ytop, GZ)
    rail(R, x0 + 0.05, ytop, x0 + 0.05, 16.0 + 1.2, GZ)
    rail(R, x0 + 0.05, 16.0 + 1.2 - 0.05, g1, 16.0 + 1.2 - 0.05, GZ)
    # west: climbs -y from the north
    x0w = g0 + 0.05
    ytop_w = 16.0 + 1.2
    y0w = ytop_w + n * run
    flight_thin(R, x0w, y0w, 0.0, w, n, rise, run, '-y', m='slate', riser='tile', side='tile', under='plaster')
    R.parts.add(box(g0 - 0.02, 16.0 - 1.2, TOP - 0.25, x0w + w, ytop_w, GZ, 'slate', sides='tile', bottom='plaster'))
    stair_rail(R, x0w + 0.05, y0w - run, rise, x0w + 0.05, ytop_w, GZ)
    stair_rail(R, x0w + w - 0.05, y0w - run, rise, x0w + w - 0.05, ytop_w, GZ)
    rail(R, x0w + w - 0.05, ytop_w, x0w + w - 0.05, 16.0 - 1.2, GZ)
    rail(R, g0, 16.0 - 1.2 + 0.05, x0w + w - 0.05, 16.0 - 1.2 + 0.05, GZ)


def windows(R):
    """Tall lancets high in the end walls, a rose in the north wall: the light falls in shafts."""
    for c in (8.0, 24.0):
        window(R, 'N', c, GZ + 1.6, 2.2, 3.2, em='e_sky', mull=2, trans=2)
        window(R, 'S', c, GZ + 1.6, 2.2, 3.2, em='e_sky', mull=2, trans=2)
    for c in (8.0, 16.0, 24.0):
        window(R, 'E', c, VJ - 0.6, 1.4, 1.2, em='e_sky', mull=1, trans=0)
        window(R, 'W', c, VJ - 0.6, 1.4, 1.2, em='e_sky', mull=1, trans=0)
    rose(R, 16.0, D - T - 0.05, 12.6, 1.8)


def press(R, cx, cy, L, Wd, H, rs, flip=False, legs=False):
    """A printing press the size of a locomotive: an iron bed, cast side frames, a stack of rollers
    turning, a flywheel, a paper roll feeding one end. The paper comes out of the other end (+x, or -x
    when flipped)."""
    x0, x1 = cx - L / 2, cx + L / 2
    y0, y1 = cy - Wd / 2, cy + Wd / 2
    s = -1 if flip else 1
    bz = BED if legs else 0.0
    # the bed
    if legs:
        for x in (x0 + 0.3, cx - L / 4, cx + L / 4, x1 - 0.3):
            for y in (y0 + 0.3, y1 - 0.3):
                if abs(x - cx) < 0.5: continue
                R.parts.add(box(x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, bz, 'iron', skip=('-z',)))
                R.parts.add(box(x - 0.4, y - 0.4, 0, x + 0.4, y + 0.4, 0.12, 'iron', skip=('-z',)))
        R.parts.add(box(x0, y0, bz, x1, y1, bz + 1.0, 'iron', bottom='iron'))
        # a fringe of iron skirts, leaving a gap on the south side to crawl in by
        for (a, b) in ((x0, cx - 0.9), (cx + 0.9, x1)):
            R.nocol.add(box(a, y0 - 0.02, bz - 0.35, b, y0 + 0.02, bz, 'iron'))
        R.nocol.add(box(x0, y1 - 0.02, bz - 0.35, x1, y1 + 0.02, bz, 'iron'))
    else:
        R.parts.add(box(x0, y0, 0, x1, y1, 1.1, 'iron', skip=('-z',)))
        R.parts.add(box(x0 - 0.15, y0 - 0.15, 0, x1 + 0.15, y1 + 0.15, 0.2, 'iron', skip=('-z',)))
        bz = 0.1
    top = bz + 1.0
    # side frames: cast plates with columns and a cornice
    for y in (y0 + 0.1, y1 - 0.1):
        for k in range(5):
            x = x0 + 0.5 + (L - 1.0) * k / 4
            R.parts.add(box(x - 0.22, y - 0.22, top, x + 0.22, y + 0.22, top + H - 1.4, 'iron'))
            R.nocol.add(box(x - 0.3, y - 0.3, top + H - 1.4, x + 0.3, y + 0.3, top + H - 1.25, 'brass'))
        R.nocol.add(box(x0 + 0.3, y - 0.12, top + H - 1.25, x1 - 0.3, y + 0.12, top + H - 0.95, 'iron'))
        R.nocol.add(box(x0 + 0.3, y - 0.08, top + 0.9, x1 - 0.3, y + 0.08, top + 1.1, 'iron'))
        for k in range(4):
            x = x0 + 0.5 + (L - 1.0) * (k + 0.5) / 4
            R.nocol.add(beam((x - (L - 1.0) / 8, y, top + 1.1), (x + (L - 1.0) / 8, y, top + H - 1.25), 0.1, 'iron', 0.1))
    # a platform on top with a rail, the ink ducts
    R.nocol.add(box(x0 + 0.3, y0, top + H - 0.95, x1 - 0.3, y1, top + H - 0.85, 'iron'))
    for k in range(6):
        x = x0 + 0.8 + (L - 1.6) * k / 5
        R.nocol.add(solid_tube((x, y0 + 0.4, top + H - 0.85), (x, y1 - 0.4, top + H - 0.85), 0.12, 'brass', 8))
    # the rollers, turning
    zs = [top + 0.7, top + 1.6, top + 2.6, top + 3.5, top + 1.2, top + 2.1]
    xs = [cx - L * 0.3, cx - L * 0.1, cx + L * 0.1, cx + L * 0.3, cx + L * 0.2, cx - L * 0.2]
    for k, (x, z) in enumerate(zip(xs, zs)):
        r = 0.42 if k < 4 else 0.3
        M = R.mover('spin', pivot=(x, cy, z), axis='y', speed=(0.9 if k % 2 else -0.9) * s * (0.42 / r))
        M.nocol.add(roller(y0 + 0.3, y1 - 0.3, x, z, r, 'chrome' if k % 3 == 0 else 'iron', 16, axis='y'))
        for yy in (y0 + 0.35, y1 - 0.35):
            M.nocol.add(box(x - r * 0.9, yy - 0.03, z - 0.04, x + r * 0.9, yy + 0.03, z + 0.04, 'brass'))
    # the flywheel on the south face, and a gear train
    fx_ = cx - s * L * 0.28
    M = R.mover('spin', pivot=(fx_, y0 - 0.45, top + 1.9), axis='y', speed=0.5 * s)
    M.nocol.add(wheel(fx_, y0 - 0.45, top + 1.9, 1.9, axis='y', spokes=8, rim=0.14, w=0.18, m='iron', hub='brass', segs=28))
    M = R.mover('spin', pivot=(fx_ + s * 2.3, y0 - 0.3, top + 1.2), axis='y', speed=-0.9 * s)
    M.nocol.add(gear(fx_ + s * 2.3, y0 - 0.3, top + 1.2, 0.8, 16, axis='y', w=0.14, m='brass'))
    R.nocol.add(solid_tube((fx_, y0 - 0.6, top + 1.9), (fx_, y1 + 0.3, top + 1.9), 0.12, 'brass', 10))
    R.col.add(box(fx_ - 2.0, y0 - 0.75, 0, fx_ + 3.2, y0, 2.2, 'tile'))
    R.parts.add(box(fx_ - 2.0, y0 - 0.75, 0, fx_ + 3.2, y0 - 0.65, 0.9, 'iron', top='brass') if not legs else
                box(fx_ - 2.0, y0 - 0.75, 0, fx_ - 1.1, y0 - 0.65, 0.9, 'iron', top='brass'))
    if legs:
        R.parts.add(box(cx + 0.9, y0 - 0.75, 0, fx_ + 3.2, y0 - 0.65, 0.9, 'iron', top='brass'))
    # the paper roll feeding the input end
    rx = x0 - 1.1 if not flip else x1 + 1.1
    for yy in (y0 + 0.4, y1 - 0.4):
        R.parts.add(box(rx - 0.15, yy - 0.15, 0, rx + 0.15, yy + 0.15, top + 0.8, 'iron'))
    M = R.mover('spin', pivot=(rx, cy, top + 0.8), axis='y', speed=0.25 * s)
    M.nocol.add(roller(y0 + 0.6, y1 - 0.6, rx, top + 0.8, 1.0, 'newsprint', 20, axis='y'))
    M.nocol.add(roller(y0 + 0.55, y1 - 0.55, rx, top + 0.8, 0.2, 'iron', 10, axis='y'))
    # the web of paper from the roll up into the rollers and out over the top roller
    xin, xout = (x0, x1) if not flip else (x1, x0)
    web = [(rx + s * 0.9, top + 1.2), (xin + s * 0.4, top + 2.2), (cx, top + 3.95), (xout - s * 0.4, top + 3.95), (xout + s * 0.6, top + 3.3)]
    for (a, b) in zip(web, web[1:]):
        R.nocol.add(sheet_band((a[0], y0 + 0.7, a[1]), (b[0], y0 + 0.7, b[1]), Wd - 1.4))
    R.press_out = getattr(R, 'press_out', []) + [((xout + s * 0.6, cy, top + 3.3), s, Wd - 1.4)]
    # a hood light over the feed end
    R.light(box(rx - 0.3, cy - 0.3, top + 3.0, rx + 0.3, cy + 0.3, top + 3.04, 'e_lamp'))
    R.nocol.add(frustum(rx, cy, top + 3.0, top + 3.3, 0.5, 0.15, 12, 'green', inner='ivory'))
    R.nocol.add(cyl(rx, cy, top + 3.3, 12.0, 0.015, 4, side='iron', caps=False))
    R.col.add(box(rx - 1.0, y0 + 0.4, 0, rx + 1.0, y1 - 0.4, top + 1.8, 'tile'))


def sheet_band(p0, p1, w, m='newsprint', t=0.012):
    """A band of paper w wide (along +y from p0) between two points in an x-z plane."""
    g = Geo()
    P = [(p0[0], p0[1], p0[2]), (p1[0], p1[1], p1[2]), (p1[0], p1[1] + w, p1[2]), (p0[0], p0[1] + w, p0[2])]
    top = [g.vert(p) for p in P]
    bot = [g.vert((p[0], p[1], p[2] - t)) for p in P]
    g.face(top, m, [(p[0], p[1]) for p in P])
    g.face(list(reversed(bot)), m, [(p[0], p[1]) for p in reversed(P)])
    for (i, j) in ((0, 1), (1, 2), (2, 3), (3, 0)):
        g.face([top[j], top[i], bot[i], bot[j]], m, [(0, 0), (1, 0), (1, t), (0, t)])
    return g.fix()


def ribbon_path(R, pts, w, rs, z=0.0, m='newsprint', col=True, wave=0.04):
    """A river of paper lying on the floor along a polyline, gently rucked up: walkable."""
    g = Geo()
    # resample every 0.5 m
    P = []
    for (a, b) in zip(pts, pts[1:]):
        L = math.dist(a, b); n = max(1, int(L / 0.5))
        for k in range(n): P.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    P.append(pts[-1])
    L_ = []
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]; b = P[min(len(P) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        zz = z + 0.02 + wave * (0.5 + 0.5 * math.sin(i * 0.9 + rs.uniform(0, 0.4)))
        L_.append(((p[0] + nx * w / 2, p[1] + ny * w / 2, zz), (p[0] - nx * w / 2, p[1] - ny * w / 2, zz)))
    ids = [(g.vert(l), g.vert(r)) for (l, r) in L_]
    for i in range(len(ids) - 1):
        (a, b), (c, d) = ids[i], ids[i + 1]
        g.face([b, d, c, a], m, [(0, i * 0.5), (0, i * 0.5 + 0.5), (w, i * 0.5 + 0.5), (w, i * 0.5)])
    # the edges: a thin rim so the sheet has a thickness when seen low
    for i in range(len(ids) - 1):
        for side in (0, 1):
            p0, p1 = L_[i][side], L_[i + 1][side]
            e = Geo(); q = [e.vert(p0), e.vert(p1), e.vert((p1[0], p1[1], z)), e.vert((p0[0], p0[1], z))]
            e.face(q if side == 1 else list(reversed(q)), m, [(0, 0), (0.5, 0), (0.5, 0.02), (0, 0.02)])
            g.add(e)
    (R.parts if col else R.nocol).add(g)
    return g


def rivers(R, rs):
    """Paper out of each press: down off the top roller to the floor and away along the aisles, into
    drifts against the walls; loops of it hung up over rollers high in the vault."""
    outs = R.press_out
    # A (south-west press) -> east along the south aisle, then north up the east side into a drift
    (ox, oy, oz), s, w = outs[0]
    R.nocol.add(sheet_band((ox, oy - w / 2, oz), (ox + 1.4, oy - w / 2, 0.03), w))
    ribbon_path(R, [(ox + 1.4, oy), (17.0, oy + 0.2), (20.5, 8.4), (24.5, 9.8), (25.3, 12.5), (25.2, 19.0), (26.4, 21.4)], 2.2, rs)
    paper_drift(R, 27.0, 22.0, 1.6, 0.5, rs)
    # C (north-east press) -> west along the north aisle, then south down the west side
    (ox, oy, oz), s, w = outs[1]
    R.nocol.add(sheet_band((ox - 1.4, oy - w / 2, 0.03), (ox, oy - w / 2, oz), w))
    ribbon_path(R, [(ox - 1.4, oy), (15.0, oy - 0.3), (11.2, 23.6), (7.2, 22.4), (6.4, 19.5), (5.9, 13.5), (5.4, 11.0)], 2.2, rs)
    paper_drift(R, 5.2, 10.4, 1.6, 0.45, rs)
    # B (the big one) -> east, then a wide river north and one south round its end
    (ox, oy, oz), s, w = outs[2]
    R.nocol.add(sheet_band((ox, oy - w / 2, oz), (ox + 1.8, oy - w / 2, 0.03), w))
    ribbon_path(R, [(ox + 1.8, oy), (24.6, 16.2), (25.0, 17.8), (24.0, 21.0), (19.0, 21.5), (13.5, 20.6), (8.0, 19.8), (6.9, 16.0), (7.4, 12.6)], 2.8, rs)
    # festoons: loops of paper hung high over rollers in the vault
    for (x, y) in ((12.0, 9.8), (20.0, 9.8), (16.0, 22.5)):
        R.nocol.add(roller(x - 1.3, x + 1.3, y, 13.6, 0.2, 'iron', 10))
        R.nocol.add(hang(x, y, 13.4, 8.9, 2.2))


def hang(x, y, ztop, zbot, w, m='newsprint'):
    """A loop of paper hanging from a roller at ztop: two sheets down to a curl at zbot."""
    g = Geo()
    n = 10
    pts = []
    for k in range(n + 1):
        a = math.pi * k / n
        pts.append((y + 0.6 * math.cos(a), zbot + 0.6 - 0.6 * math.sin(a)))
    prof = [(y + 0.6, ztop)] + pts + [(y - 0.6, ztop)]
    for (a, b) in zip(prof, prof[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        oy, oz = -(b[1] - a[1]) / L * 0.012, (b[0] - a[0]) / L * 0.012
        for sgn in (1, -1):
            q = Geo()
            P = [(x - w / 2, a[0] + oy * sgn, a[1] + oz * sgn), (x + w / 2, a[0] + oy * sgn, a[1] + oz * sgn),
                 (x + w / 2, b[0] + oy * sgn, b[1] + oz * sgn), (x - w / 2, b[0] + oy * sgn, b[1] + oz * sgn)]
            ids = [q.vert(p) for p in P]
            q.face(ids if sgn > 0 else list(reversed(ids)), m, [(0, 0), (w, 0), (w, 1), (0, 1)])
            g.add(q)
    return g


def paper_drift(R, x, y, r, h, rs):
    """A heap of spoiled sheets: a low mound under loose pages."""
    R.parts.add(cone(x, y, 0, h, r, r * 0.3, 14, side='newsprint', top='newsprint', bottom='newsprint'))
    for _ in range(40):
        a = rs.uniform(0, 2 * math.pi); d = rs.uniform(0, r * 1.1)
        zz = max(0.0, h * (1 - d / r)) + 0.01
        p = box(-0.15, -0.1, 0, 0.15, 0.1, 0.006, 'newsprint')
        rot(p, 'x', rs.uniform(-0.4, 0.4))
        R.nocol.add(p.xform(rs.uniform(0, 6.3), x + math.cos(a) * d, y + math.sin(a) * d, zz))


def ink_room(R, rs):
    """Under the big press: the ink room. Vats of it, barrels, the type cases, a ledger, one lamp."""
    x0, y0, x1, y1 = INK
    R.cut(box(x0, y0, IZ, x1, y1, -0.25, 'slate', bottom='slate', top='iron'))
    # the hatch and the stair down (climbing -x from its foot in the room)
    hx0, ya, yb = HX
    n, rise, run = 11, -IZ / 11, 0.28
    foot = hx0 + n * run
    R.cut(box(hx0, ya, IZ, foot + 0.05, yb, 0.02, 'slate', bottom='slate', top='slate'))
    R.flight(foot, ya, IZ, yb - ya, n, rise, run, '-x', m='oak', riser='walnut', side='slate')
    R.nocol.add(box(hx0 - 0.1, ya - 0.1, 0, hx0, yb + 0.1, 0.03, 'brass'))
    hatch = box(0, 0, 0, 0.9, yb - ya, 0.05, 'oak')
    rot(hatch, 'y', -1.3)
    R.nocol.add(hatch.xform(0, hx0 - 0.05, ya, 0.03))
    # vats of ink: black basins with a sheen, a paddle in one
    for (vx, vy) in ((13.2, 17.0), (14.6, 17.3)):
        R.parts.add(cyl(vx, vy, IZ, IZ + 0.9, 0.55, 16, side='bronze', top='ink', bottom='bronze'))
        R.nocol.add(ring(vx, vy, IZ + 0.9, IZ + 0.96, 0.5, 0.58, 16, top='bronze', bottom='bronze', inner='bronze', outer='bronze'))
    R.nocol.add(beam((13.2, 17.0, IZ + 0.8), (13.6, 16.6, IZ + 1.9), 0.04, 'oak'))
    for (bx, by) in ((18.9, 14.5), (18.9, 15.2), (18.2, 14.5)):
        R.parts.add(cyl(bx, by, IZ, IZ + 0.85, 0.3, 12, side='oak', top='ink', bottom='oak'))
        for z in (0.15, 0.7):
            R.nocol.add(ring(bx, by, IZ + z, IZ + z + 0.05, 0.3, 0.32, 12, top='iron', bottom='iron', inner='iron', outer='iron'))
    # the type cases: a cabinet of shallow drawers
    R.parts.add(box(x1 - 0.6, 16.3, IZ, x1, y1 - 0.1, IZ + 1.3, 'walnut'))
    for k in range(8):
        R.nocol.add(box(x1 - 0.62, 16.4, IZ + 0.1 + k * 0.15, x1 - 0.6, y1 - 0.2, IZ + 0.2 + k * 0.15, 'oak'))
    R.parts.add(table(12.5, 14.2, 14.1, 15.0, 0.8, 'walnut').xform(0, 0, 0, IZ))
    R.nocol.add(box(12.6, 14.3, IZ + 0.8, 14.0, 14.9, IZ + 0.805, 'ink'))
    R.parts.add(stool(13.3, 15.5, -math.pi / 2).xform(0, 0, 0, IZ))
    open_book(R, 13.3, 14.6, IZ + 0.81, 0.0)
    R.light(sphere(15.8, 15.0, IZ + 1.7, 0.08, 8, 4, 'e_amber'))
    desk_lamp(R, 13.9, 14.45, IZ + 0.8)
    R.light(box(17.4, 16.9, -0.3, 18.6, 17.5, -0.27, 'e_panel'))
    R.nocol.add(cyl(15.8, 15.0, IZ + 1.95, -0.3, 0.01, 4, side='iron', caps=False))
    R.spot('plaque', 13.3, 14.6, IZ + 0.8, math.pi / 2,
           text='INK RECEIVED: enough for every book. INK USED: exactly that much, and not one drop over. There is no such thing as a spare letter.')
    secret(R, 16.2, 16.0, IZ, 'The Ink Room',
           'Under the biggest press, down through a hatch between its legs: the room where the ink is kept. It smells of iron and night. The vats are full, and they are always full.')
    # the dribble of ink from the press bed down into a vat, seen from the stair
    R.nocol.add(box(14.58, 17.28, IZ + 0.9, 14.62, 17.32, -0.25, 'ink'))


def desks(R, rs):
    """Reading desks down the east side, proofs spread on them, green lamps."""
    for (x0, y0, x1, y1) in ((20.2, 2.8, 22.8, 4.4), (12.2, 26.8, 14.8, 28.6)):
        reading_table(R, x0, y0, x1, y1, lamps=2, chairs=True)
        for k in range(4):
            R.nocol.add(sheet(x0 + 0.4 + k * 0.6, (y0 + y1) / 2 + rs.uniform(-0.2, 0.2), 0.785, rs.uniform(-0.3, 0.3), w=0.35, l=0.5))


def lamps(R):
    for (x, y) in ((8.0, 10.8), (24.0, 10.8), (8.0, 21.0), (24.0, 21.0), (16.0, 3.6), (16.0, 28.4)):
        pendant(R, x, y, 4.6, 14.1, r=0.3)
    for k in range(8):
        p = 4.0 + k * (24.0 / 7)
        for (x, y) in ((p, 1.6), (p, D - 1.6), (1.6, p), (W - 1.6, p)):
            if k % 2: R.light(sphere(x, y, GZ + 2.6, 0.1, 8, 4, 'e_lamp'))
            else: R.light(sphere(x, y, GZ + 2.6, 0.08, 8, 4, 'e_amber'))
    for (x, y) in ((2.0, 2.0), (30.0, 2.0), (30.0, 30.0), (2.0, 30.0)):
        R.light(sphere(x, y, 2.5, 0.09, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, y, 2.55, TOP - 0.2, 0.01, 4, side='iron', caps=False))
