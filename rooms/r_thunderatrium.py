"""The Thunder Atrium: a round, two-storey reading room under a glazed dome, and in the dome a storm
cloud that has got in and cannot get out: black, heavy, grumbling. On the great desk in the middle a
brass lightning rod stands ready. Behind the drum of the dome, above the upper gallery, runs a
narrow ring passage with slits that look into the weather."""
from kit_h3 import *

W = D = 32.0
CX = CY = 16.0
RV = 11.0                     # the central void
RC = 11.6                     # the ring of columns
UP = 8.0                      # upper gallery floor
UC = 12.4                     # upper ambulatory ceiling
DZ = 14.0                     # the dome springs here
PR0, PR1, PZ0, PZ1 = 11.35, 12.55, 12.6, 14.9    # the secret ring passage behind the drum
SC = 26.2                     # the stair room in the north-east corner of the upper level


def make():
    R = Room('thunderatrium', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    # lower ambulatory, the central void to the dome, upper ambulatory (not the NE corner)
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, 7.3, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(cyl(CX, CY, 0, DZ + 0.01, RV, 64, side='tile', top='plaster', bottom='terrazzo'))
    R.cut(dome_cap(CX, CY, DZ, RV, 1.5, 64, 10, m='plaster', bottom='plaster'))
    R.cut(box(T - 0.02, T - 0.02, UP, W - T + 0.02, SC, UC, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, SC - 0.05, UP, SC - 0.3, D - T + 0.02, UC, 'tile', bottom='terrazzo', top='plaster'))
    dome(R)
    columns(R)
    stairs_(R)
    shelves(R)
    floor_rings(R)
    central_desk(R)
    desks(R)
    secret_passage(R)
    fx(R, 'lightning', [CX - 6, CY - 6, 11.0, CX + 6, CY + 6, 15.2], at=[CX, CY, 5.6])
    fx(R, 'rain', [CX - 5, CY - 5, 10.0, CX + 5, CY + 5, 12.5], density=0.3)
    # walking graph: a ring round the desks and the ambulatory, and the upper gallery
    ring_ = navloop(R, [(CX + 8.2 * math.cos(a), CY + 8.2 * math.sin(a)) for a in [k * math.pi / 4 for k in range(8)]])
    outer = navloop(R, [(3.0, 3.0), (16, 3.2), (29, 3.0), (29, 16), (29, 29), (16, 28.8), (3, 29), (3, 16)])
    for k in range(4): R.link(outer[k * 2 + 1], ring_[(k * 2 + 6) % 8])
    up = navloop(R, [(2.5, 8.0), (2.5, 24.0), (8.0, 29.4), (24.0, 29.4), (24.5, 24.8), (29.4, 24.0), (29.4, 8.0), (24.0, 3.2), (8.0, 3.2)], z=UP)
    secret(R, CX + 12.0 * math.cos(-2.4), CY + 12.0 * math.sin(-2.4), PZ0, 'The Drum Passage',
           'A stone ring behind the dome, one person wide. Through the slits the storm is close enough to touch, and it smells of hot pennies. Someone has left a chair at every window.')
    return finish(R, 'The Thunder Atrium', weight=3, probe=(CX, CY - 6.5, 3.0), top=15.5,
                  blurb='A storm has got into the dome and cannot find its way out. It grumbles over the reading desks. Someone has put up a lightning rod, which seems to satisfy everyone.')


def dome(R):
    """Glazing on iron ribs (a painted night sky) and the storm cloud hanging under it."""
    # the glazing: a painted storm sky showing round the cloud's edge; dark glass behind it
    g = dome_cap(CX, CY, DZ - 0.02, RV - 0.02, 1.48, 48, 8, m='e_skydome', bottom='e_skydome')
    g.f = [tuple(reversed(f)) for f in g.f[:-1]]; g.m = g.m[:-1]; g.uv = [list(reversed(u)) for u in g.uv[:-1]]
    rim, mid = Geo(), Geo()
    for f, m, uv in zip(g.f, g.m, g.uv):
        r = max(math.hypot(g.v[v][0] - CX, g.v[v][1] - CY) for v in f)
        (rim if r > 7.2 else mid).face([rim.vert(g.v[v]) for v in f] if r > 7.2 else [mid.vert(g.v[v]) for v in f], 'e_skydome' if r > 7.2 else 'black', uv)
    R.light(rim)
    R.nocol.add(mid)
    for k in range(16):
        a = 2 * math.pi * k / 16
        pts = []
        for i in range(9):
            r = (RV - 0.1) * (1 - i / 8)
            pts.append((CX + r * math.cos(a), CY + r * math.sin(a), dome_z(r, RV, DZ, 1.5) - 0.12))
        for p0, p1 in zip(pts, pts[1:]):
            R.nocol.add(beam(p0, p1, 0.1, 'iron'))
    for r in (3.5, 7.0, 9.6):
        n = 32
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            z = dome_z(r, RV, DZ, 1.5) - 0.12
            R.nocol.add(beam((CX + r * math.cos(a0), CY + r * math.sin(a0), z), (CX + r * math.cos(a1), CY + r * math.sin(a1), z), 0.07, 'iron'))
    # the drum: a band of stone with a cornice, and slit windows (the passage behind)
    R.parts.add(ring(CX, CY, UC - 0.1, UC + 0.25, RV - 0.25, RV + 0.02, 64, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.parts.add(ring(CX, CY, DZ - 0.25, DZ, RV - 0.3, RV + 0.02, 64, top='gilt', bottom='tile', inner='gilt', outer='tile'))
    # the storm: black heavy lumps, lower in the middle
    rnd = random.Random(11)
    g = Geo()
    g.add(puffs(CX, CY, 12.6, 4.2, 7, 'black', seed=1, flat=0.5, segs=12, rings=6))
    for k in range(14):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(2.5, 8.0)
        x, y = CX + math.cos(a) * d, CY + math.sin(a) * d
        z = min(dome_z(d, RV, DZ, 1.5) - 1.0, 13.8) - rnd.uniform(0, 0.8) + d * 0.05
        g.add(puffs(x, y, z, rnd.uniform(1.6, 2.6), 4, rnd.choice(('black', 'black', 'slate')), seed=10 + k, flat=0.5, segs=10, rings=5))
    for k in range(6):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0, 2.0)
        g.add(puffs(CX + math.cos(a) * d, CY + math.sin(a) * d, 11.3 + rnd.uniform(-0.3, 0.3), 1.5, 3, 'black', seed=40 + k, flat=0.6, segs=10, rings=5))
    R.nocol.add(g)
    # the light inside the cloud (the lightning's afterglow, faint)
    R.light(sphere(CX + 1.2, CY - 0.8, 12.2, 0.5, 10, 5, 'e_blue'))
    R.light(sphere(CX - 2.5, CY + 1.5, 12.7, 0.35, 8, 4, 'e_blue'))


def columns(R):
    n = 16
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        x, y = CX + RC * math.cos(a), CY + RC * math.sin(a)
        R.parts.add(cyl(x, y, 0, 7.3, 0.34, 18, side='tile', caps=False))
        R.parts.add(box(x - 0.5, y - 0.5, 0, x + 0.5, y + 0.5, 0.4, 'tile', skip=('-z',)))
        R.parts.add(box(x - 0.5, y - 0.5, 6.9, x + 0.5, y + 0.5, 7.3, 'tile'))
        R.parts.add(cyl(x, y, UP, UC, 0.3, 16, side='tile', caps=False))
        R.parts.add(box(x - 0.42, y - 0.42, UC - 0.3, x + 0.42, y + 0.42, UC, 'tile'))
    # the gallery's edge: a moulded lip and a brass rail round the void
    R.parts.add(ring(CX, CY, 7.15, 7.3, RV - 0.12, RV + 0.5, 64, top='tile', bottom='gilt', inner='gilt', outer='tile'))
    m = 40
    for k in range(m):
        a0, a1 = 2 * math.pi * k / m, 2 * math.pi * (k + 1) / m
        r = RV + 0.15
        rail(R, CX + r * math.cos(a0), CY + r * math.sin(a0), CX + r * math.cos(a1), CY + r * math.sin(a1), UP, post=1.8)


def stairs_(R):
    """Two long flights against the south and north walls, each climbing through a slot in the gallery floor."""
    n, rise, run = 40, UP / 40, 0.28
    L = n * run
    for (y0, y1, x0, axis) in ((T + 0.05, T + 1.75, 10.2, '+x'), (D - T - 1.75, D - T - 0.05, W - 10.2, '-x')):
        R.cut(box(10.2 - 0.02 if axis == '+x' else W - 10.2 - L - 0.02, y0 - 0.02, 7.0, 10.2 + L + 0.02 if axis == '+x' else W - 10.2 + 0.02, y1 + 0.2, UP + 0.02, 'tile', bottom='terrazzo'))
        R.flight(x0, y0, 0, y1 - y0, n, rise, run, axis, m='terrazzo', riser='tile', side='tile')
        xa, xb = (x0, x0 + L) if axis == '+x' else (x0, x0 - L)
        # a stone string on the open side, a brass handrail, and a rail round the slot above
        ys = y1 + 0.1 if y0 < 8 else y0 - 0.1
        stair_rail(R, xa + (0.3 if axis == '+x' else -0.3), ys, rise, xb - (0.15 if axis == '+x' else -0.15), ys, UP)
        yr = y1 + 0.18 if y0 < 8 else y0 - 0.18
        xs = sorted((xa, xb - (1.2 if axis == '+x' else -1.2)))
        rail(R, xs[0], yr, xs[1], yr, UP)
        xe = xa - (0.05 if axis == '+x' else -0.05)
        rail(R, xe, yr, xe, y0 if y0 < 8 else y1, UP)


def shelves(R):
    rows = 16
    for (dirn, bk) in (('+y', T), ('-y', D - T)):
        for (a, b) in ((0.6, 5.8), (26.2, W - 0.6)):
            sh(R, dirn, bk, a, b, rows=rows, frame='walnut')
    for (dirn, bk) in (('+x', T), ('-x', W - T)):
        for (a, b) in ((0.6, 5.8), (10.2, 21.8), (26.2, D - 0.6)):
            sh(R, dirn, bk, a, b, rows=rows, frame='walnut')
    # upper gallery: walls of books, above the stair slots too
    rows2 = 9
    for (a, b) in ((0.6, 5.8), (26.2, W - 0.6)):
        sh(R, '+y', T, a, b, z=UP, rows=rows2, frame='walnut')
    for (a, b) in ((0.6, 5.8),):
        sh(R, '-y', D - T, a, b, z=UP, rows=rows2, frame='walnut')
    for (a, b) in ((0.6, 5.8), (10.2, 21.8), (26.2, D - 0.6)):
        sh(R, '+x', T, a, b, z=UP, rows=rows2, frame='walnut')
    for (a, b) in ((0.6, 5.8), (10.2, 21.8)):
        sh(R, '-x', W - T, a, b, z=UP, rows=rows2, frame='walnut')
    # the NE corner's walls, the false bookcase in the west one
    sh(R, '-y', SC - 0.05, 26.3, W - 0.6, z=UP, rows=rows2, frame='walnut')
    shelf(R, SC - 0.3, 26.45, UP, 1.5, '-x', rows=rows2, frame='walnut', solid=False)
    sh(R, '-x', SC - 0.3, 28.1, D - T - 2.6, z=UP, rows=rows2, frame='walnut')
    # lamps
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        pendant(R, CX + 13.6 * math.cos(a), CY + 13.6 * math.sin(a), 4.9, 7.3, r=0.22)
        R.light(sphere(CX + 13.4 * math.cos(a), CY + 13.4 * math.sin(a), UC - 0.6, 0.14, 10, 5, 'e_lamp'))
        R.nocol.add(cyl(CX + 13.4 * math.cos(a), CY + 13.4 * math.sin(a), UC - 0.5, UC, 0.01, 6, side='iron', caps=False))
    for (x, y) in ((1.4, 1.4), (W - 1.4, 1.4), (1.4, D - 1.4), (W - 1.4, D - 1.4)):
        R.nocol.add(cyl(x, y, 0, 1.3, 0.02, 6, side='brass', caps=False))
        R.light(sphere(x, y, 1.4, 0.1, 10, 5, 'e_amber'))


def floor_rings(R):
    """Inlaid rings of dark stone in the marble, a compass under the desk."""
    for (r0, r1) in ((2.9, 3.05), (6.6, 6.75), (9.9, 10.1)):
        R.nocol.add(ring(CX, CY, 0.0, 0.006, r0, r1, 64, top='slate', bottom='slate', inner='slate', outer='slate'))
    for k in range(8):
        a = k * math.pi / 4
        L = 9.9 if k % 2 == 0 else 6.6
        R.nocol.add(obox(CX + 3.05 * math.cos(a), CY + 3.05 * math.sin(a), CX + L * math.cos(a), CY + L * math.sin(a), 0.0, 0.006, 0.08, 'slate'))


def central_desk(R):
    """A round desk of dark wood, and on it the lightning rod: a brass mast, a ball, a coil, cables."""
    R.parts.add(ring(CX, CY, 0, 0.95, 1.6, 2.4, 40, top='leather', bottom='walnut', inner='walnut', outer='walnut'))
    R.parts.add(ring(CX, CY, 0.95, 1.0, 1.55, 2.45, 40, top='walnut', bottom='walnut', inner='walnut', outer='walnut'))
    R.parts.add(cyl(CX, CY, 0, 0.5, 0.6, 20, side='brass', top='brass'))
    R.parts.add(cyl(CX, CY, 0.5, 5.4, 0.06, 10, side='brass', caps=False))
    R.parts.add(sphere(CX, CY, 5.55, 0.18, 12, 6, 'brass'))
    R.nocol.add(cyl(CX, CY, 5.7, 6.4, 0.015, 6, side='brass', caps=False))
    R.light(sphere(CX, CY, 6.45, 0.05, 8, 4, 'e_blue'))
    for k in range(10):
        z = 1.2 + k * 0.12
        R.nocol.add(ring(CX, CY, z, z + 0.04, 0.09, 0.13, 16, top='bronze', bottom='bronze', inner='bronze', outer='bronze'))
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        R.nocol.add(beam((CX + 0.1 * math.cos(a), CY + 0.1 * math.sin(a), 0.5), (CX + 1.9 * math.cos(a), CY + 1.9 * math.sin(a), 0.97), 0.03, 'iron'))
    for k in range(6):
        a = k * math.pi / 3
        x, y = CX + 2.0 * math.cos(a), CY + 2.0 * math.sin(a)
        desk_lamp(R, x, y, 1.0)
        c = chair(CX + 2.85 * math.cos(a + 0.5), CY + 2.85 * math.sin(a + 0.5), a + 0.5 + math.pi); R.parts.add(c)
    book_pile(R, CX + 1.95 * math.cos(0.5), CY + 1.95 * math.sin(0.5), 1.0, 5, seed=3)
    open_book(R, CX + 1.95 * math.cos(2.6), CY + 1.95 * math.sin(2.6), 1.0, 2.6)


def desks(R):
    """Curved reading desks on a ring round the rod, green lamps; books under nothing at all."""
    for k in range(8):
        a0 = 2 * math.pi * k / 8 + 0.12; a1 = a0 + 2 * math.pi / 8 - 0.24
        R.parts.add(ring(CX, CY, 0.72, 0.78, 4.6, 5.5, 8, top='leather', bottom='walnut', inner='walnut', outer='walnut', a0=a0, a1=a1))
        for a in (a0 + 0.05, a1 - 0.05):
            for r in (4.7, 5.4):
                R.parts.add(box(CX + r * math.cos(a) - 0.04, CY + r * math.sin(a) - 0.04, 0, CX + r * math.cos(a) + 0.04, CY + r * math.sin(a) + 0.04, 0.72, 'walnut'))
        am = (a0 + a1) / 2
        desk_lamp(R, CX + 5.05 * math.cos(am), CY + 5.05 * math.sin(am), 0.78)
        for da in (-0.22, 0.22):
            c = chair(CX + 6.0 * math.cos(am + da), CY + 6.0 * math.sin(am + da), am + da + math.pi); R.parts.add(c)
            R.spot('sit', CX + 6.0 * math.cos(am + da), CY + 6.0 * math.sin(am + da), 0.48, am + da + math.pi)


def secret_passage(R):
    """Behind the false bookcase in the upper gallery's north-east corner: a dog-leg stair up the corner,
    a crawlway on the diagonal, and the ring passage behind the drum, with slits into the dome."""
    x0, y0 = SC, SC                      # the corner room
    x1, y1 = W - T, D - T
    R.cut(box(x0, y0 + 0.25, UP, x1, y1, PZ1, 'tile', bottom='oak', top='plaster'))
    R.cut(box(SC - 0.35, 27.95 - 1.5 + 0.05, UP, x0 + 0.05, 27.95 - 0.05, UP + 2.2, 'tile', bottom='oak', top='tile'))   # behind the false case
    n1, n2, rise, run = 12, 8, (PZ0 - UP) / 20, 0.28
    fy0, fy1 = y0 + 0.3, y0 + 1.55
    R.flight(x0 + 0.3, fy0, UP, fy1 - fy0, n1, rise, run, '+x', m='oak', riser='walnut', side='walnut')
    lx0 = x0 + 0.3 + n1 * run
    zl = UP + n1 * rise
    R.parts.add(box(lx0, fy0, UP, x1, fy1 + 0.1, zl, 'oak', sides='walnut'))
    R.flight(lx0, fy1 + 0.1, zl, x1 - lx0, n2, rise, run, '+y', m='oak', riser='walnut', side='walnut')
    ty = fy1 + 0.1 + n2 * run
    HY = 29.2
    R.parts.add(box(lx0, ty, UP, x1, y1, PZ0, 'oak', sides='walnut'))            # the head of the stair
    R.parts.add(box(x0, HY, UP, lx0, y1, PZ0, 'oak', sides='walnut'))            # and a landing across the corner
    stair_rail(R, lx0 - 0.04, fy1 + 0.1 + run, zl + rise, lx0 - 0.04, HY, zl + (HY - fy1 - 0.1) / run * rise)
    stair_rail(R, x0 + 0.5, fy1 + 0.06, UP + rise, lx0 - 0.3, fy1 + 0.06, zl - rise)
    rail(R, x0 + 0.02, HY - 0.05, lx0 - 0.02, HY - 0.05, PZ0)
    # a crawlway west out of the corner, then south-west to the ring passage
    ex, ey = CX + (PR0 + PR1) / 2 * math.cos(math.pi / 4), CY + (PR0 + PR1) / 2 * math.sin(math.pi / 4)
    R.cut(obox(27.0, 30.4, 24.6, 30.4, PZ0, PZ1 - 0.6, 1.2, 'tile', bottom='oak', top='plaster'))
    R.cut(obox(24.6, 31.0, ex, ey, PZ0, PZ1 - 0.6, 1.2, 'tile', bottom='oak', top='plaster'))
    # the ring passage and its slits
    R.cut(ring(CX, CY, PZ0, PZ1, PR0, PR1, 64, top='plaster', bottom='oak', inner='tile', outer='tile'))
    for k in range(24):
        aa = 2 * math.pi * (k + 0.5) / 24
        R.cut(obox(CX + (RV - 0.2) * math.cos(aa), CY + (RV - 0.2) * math.sin(aa), CX + (PR0 + 0.1) * math.cos(aa), CY + (PR0 + 0.1) * math.sin(aa),
                   DZ - 1.3 + 0.35, DZ - 0.3, 0.32, 'tile', bottom='tile', top='tile'))
    # a chair at some of the windows, a lamp, a candle, books
    for k in range(0, 24, 3):
        aa = 2 * math.pi * (k + 0.5) / 24
        x, y = CX + (PR0 + 0.72) * math.cos(aa), CY + (PR0 + 0.72) * math.sin(aa)
        c = chair(x, y, aa + math.pi); c.xform(0, 0, 0, PZ0); R.parts.add(c)
        R.spot('sit', x, y, PZ0 + 0.48, aa + math.pi)
        R.light(sphere(CX + (PR1 - 0.1) * math.cos(aa + 0.13), CY + (PR1 - 0.1) * math.sin(aa + 0.13), PZ0 + 1.9, 0.06, 6, 3, 'e_candle'))
    book_pile(R, 30.5, 30.5, PZ0, 6, seed=8)
    for k in range(0, 24, 4):
        aa = 2 * math.pi * (k + 2) / 24
        bulb(R, CX + (PR0 + PR1) / 2 * math.cos(aa), CY + (PR0 + PR1) / 2 * math.sin(aa), PZ1 - 0.5, r=0.08, m='e_dim', top=PZ1)
    bulb(R, 29.0, 29.0, PZ1 - 0.6, r=0.1, m='e_dim', top=PZ1)
    bulb(R, 29.0, 27.2, UP + 3.2, r=0.1, m='e_dim', top=PZ1)
    R.spot('plaque', CX + PR1 * math.cos(-2.4), CY + PR1 * math.sin(-2.4), PZ0 + 1.5, -2.4 + math.pi, text='DO NOT FEED THE WEATHER')
