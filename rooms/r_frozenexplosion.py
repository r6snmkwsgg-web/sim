"""The Held Breath: a reading room a split second after something went off in the middle of it. Books,
chairs, glass and smoke hang where they were thrown. Some of the heavier pieces will take your weight;
they climb, in a ragged spiral, to the still centre of the blast."""
from kit_h5 import *

W = D = 2 * C
H = TOP - 0.1
BX, BY = 16.0, 16.5          # the centre of the blast
PZ = 4.0                     # the calm: a floating disc at the heart of it
PR = 1.7
CALM = 3.0                   # nothing hangs inside this radius of the centre


def make():
    R = Room('frozenexplosion', 2, 2, res=2048)
    rng = random.Random(40)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    # coffered ceiling
    for k in range(1, 8):
        R.nocol.add(box(T, k * 4.0 - 0.12, H - 0.35, W - T, k * 4.0 + 0.12, H, 'walnut', bottom='gilt'))
        R.nocol.add(box(k * 4.0 - 0.12, T, H - 0.35, k * 4.0 + 0.12, D - T, H, 'walnut', bottom='gilt'))
    # tall windows down the east wall, their glass blown in
    for (y0, y1) in ((1.4, 5.6), (10.6, 14.0), (18.0, 21.4), (26.4, 30.6)):
        R.cut(box(W - T - 0.1, y0, 0.9, W - T + 0.3, y1, 6.9, 'tile'))
        R.light(box(W - T + 0.25, y0, 0.9, W - T + 0.3, y1, 6.9, 'e_sky'))
        n = int((y1 - y0) / 0.7)
        for k in range(n + 1):
            y = y0 + (y1 - y0) * k / n
            R.nocol.add(box(W - T + 0.12, y - 0.03, 0.9, W - T + 0.2, y + 0.03, 6.9, 'iron'))
        for z in (2.4, 3.9, 5.4):
            R.nocol.add(box(W - T + 0.12, y0, z - 0.03, W - T + 0.2, y1, z + 0.03, 'iron'))
    # bookcases on the other walls
    rows = 14
    for (a, b) in ((0.7, 6.0), (10.0, 22.0), (26.0, 31.3)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
    # amber sconces that stay lit
    for (x, y) in ((T + 0.5, 8.0 - 2.2), (T + 0.5, 8.0 + 2.2), (T + 0.5, 24.0 - 2.2), (T + 0.5, 24.0 + 2.2)):
        R.nocol.add(box(T, y - 0.08, 2.3, T + 0.3, y + 0.08, 2.4, 'brass'))
        R.light(sphere(x, y, 2.55, 0.1, 8, 4, 'e_amber'))
    tables(R, rng)
    stones(R, rng)
    debris(R, rng)
    navloop(R, [(2.5, 8), (8, 8), (8, 2.5), (24, 2.5), (24, 8), (29.5, 8), (29.5, 24), (24, 24), (24, 29.5), (8, 29.5), (8, 24), (2.5, 24)])
    R.spot('probe', 8, 16, 2.0)
    R.meta.update(label='The Held Breath', weight=3,
                  blurb='Something went off in the middle of the reading room, and then time stopped to look. Nothing has landed yet.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    fx(R, 'dust', [T, 0, T, W - T, H, D - T])
    return tidy(R)


def rdist(x, y):
    return math.hypot(x - BX, y - BY)


def tables(R, rng):
    """Reading tables in rows. Far from the blast they stand; nearer, they are shoved and tipped; nearest,
    they have left the floor."""
    for y in (3.2, 12.0, 20.0, 28.8):
        for x in (4.2, 11.4, 20.6, 27.8):
            d = rdist(x, y)
            push = max(0.0, 7.0 - d) * 0.35
            ux, uy = (x - BX) / max(d, 0.1), (y - BY) / max(d, 0.1)
            tx, ty = x + ux * push, y + uy * push
            yaw = push * 0.25 * (1 if rng.random() < 0.5 else -1)
            if d < 9.5 and d > 5.5:
                # shoved and skewed, still on the floor
                t = table(-1.3, -0.5, 1.3, 0.5, 0.78, 'walnut', top='leather').xform(yaw, tx, ty, 0)
                R.parts.add(t)
                desk_lamp_at(R, tx, ty, yaw, lit=rng.random() < 0.5)
            elif d >= 9.5:
                R.parts.add(table(x - 1.3, y - 0.5, x + 1.3, y + 0.5, 0.78, 'walnut', top='leather'))
                desk_lamp(R, x - 0.6, y, 0.78); desk_lamp(R, x + 0.6, y, 0.78)
                for dx in (-0.6, 0.6):
                    for s in (-1, 1):
                        R.parts.add(chair(x + dx, y + s * 0.85, -s * math.pi / 2))
                        R.spot('sit', x + dx, y + s * 0.85, 0.48, -s * math.pi / 2)
            # chairs thrown from the nearer tables
            if d < 9.5:
                for k in range(3):
                    c = chair(0, 0, 0)
                    z = rng.uniform(2.4, 5.5)
                    orient(c, rng.uniform(0, 6.28), rng.uniform(-1.2, 1.2), rng.uniform(-1.2, 1.2),
                           tx + ux * rng.uniform(1, 3) + rng.uniform(-1, 1), ty + uy * rng.uniform(1, 3) + rng.uniform(-1, 1), z)
                    R.nocol.add(c)


def desk_lamp_at(R, x, y, yaw, lit=True):
    c, s = math.cos(yaw), math.sin(yaw)
    for dx in (-0.6, 0.6):
        if lit: desk_lamp(R, x + c * dx, y + s * dx, 0.78)
        else:
            g = Geo()
            g.add(cyl(0, 0, 0, 0.03, 0.08, 10, side='brass', top='brass'))
            g.add(obox(-0.17, 0, 0.17, 0, 0.0, 0.08, 0.13, 'green'))
            orient(g, yaw, 1.4, 0, x + c * dx, y + s * dx, 0.84)
            R.nocol.add(g)


def stones(R, rng):
    """The heavy debris that holds: a ragged spiral of floating tabletops, folios and fallen shelves,
    each a step higher, ending at the calm disc in the middle."""
    # a pile of dropped folios to start on, then round the blast at a steady radius, a step higher each time
    a = math.radians(200)
    r = 4.7
    k = 0
    while True:
        z = min(PZ - 0.42, 0.45 * (k + 1))
        x, y = BX + math.cos(a) * r, BY + math.sin(a) * r
        yaw = a + math.pi / 2 + rng.uniform(-0.08, 0.08)
        kind = ('pile', 'table', 'folio', 'shelf', 'table', 'folio', 'drawers', 'table')[k % 8]
        stone(R, rng, kind, x, y, z, yaw)
        k += 1
        if z >= PZ - 0.42 - 1e-6:
            break
        a += 1.05 / r
    # the last piece: a bookcase blown flat, pointing in to the calm
    a += 0.2 / r
    mx, my = BX + math.cos(a) * (PR + 1.25), BY + math.sin(a) * (PR + 1.25)
    stone(R, rng, 'plank', mx, my, PZ - 0.2, a)
    # the calm: a round reading table's top, level, with a lamp that has not gone out
    R.parts.add(cyl(BX, BY, PZ - 0.1, PZ, PR, 28, side='walnut', top='carpet', bottom='walnut'))
    R.nocol.add(ring(BX, BY, PZ - 0.1, PZ + 0.01, PR - 0.12, PR, 28, top='gilt', bottom='walnut', inner='gilt', outer='gilt'))
    R.parts.add(chair(BX + 0.3, BY - 0.6, math.pi / 2).xform(0, 0, 0, PZ))
    R.spot('sit', BX + 0.3, BY - 0.6, PZ + 0.48, math.pi / 2)
    R.parts.add(table(BX - 0.1, BY - 0.1, BX + 0.9, BY + 0.5, 0.72, 'walnut').xform(0, 0, 0, PZ))
    desk_lamp(R, BX + 0.6, BY + 0.25, PZ + 0.72)
    ob = open_book(0.2, 0.28, 0.12, 'oxblood'); orient(ob, 0.3, 0, 0, BX + 0.3, BY + 0.2, PZ + 0.74)
    R.nocol.add(ob)
    R.spot('plaque', BX + 0.3, BY + 0.2, PZ + 0.74)
    R.light(sphere(BX - 0.8, BY + 0.6, PZ + 0.15, 0.06, 8, 4, 'e_candle'))
    R.nocol.add(cyl(BX - 0.8, BY + 0.6, PZ, PZ + 0.1, 0.03, 6, side='ivory'))
    secret(R, BX, BY, PZ, 'The Still Centre',
           'At the heart of it everything is quiet. The lamp is still lit and the page is still open, at the line somebody was reading when it happened.', r=1.6)


def stone(R, rng, kind, x, y, z, yaw):
    if kind == 'pile':
        for i in range(5):
            b = book_geo(1.0 - i * 0.06, 0.09, 0.7 - i * 0.03, ('oxblood', 'green', 'leather')[i % 3])
            orient(b, yaw + rng.uniform(-0.2, 0.2), 0, 0, x, y, i * 0.09 + 0.045)
            R.nocol.add(b)
        R.col.add(box(-0.55, -0.4, 0, 0.55, 0.4, z, 'tile').xform(yaw, x, y, 0))
        return
    if kind == 'table':
        g = box(-0.8, -0.5, -0.06, 0.8, 0.5, 0, 'walnut', top='leather')
        for (px, py) in ((-0.7, -0.4), (0.7, -0.4), (0.7, 0.4), (-0.7, 0.4)):
            g.add(beam((px, py, -0.06), (px * 1.15, py * 1.3, -0.75), 0.07, 'walnut'))
        R.parts.add(g.xform(yaw, x, y, z))
    elif kind == 'folio':
        g = book_geo(1.25, 0.16, 0.9, rng.choice(('oxblood', 'green', 'leather')))
        R.parts.add(g.xform(yaw, x, y, z - 0.086))
    elif kind == 'plank':
        g = box(-1.45, -0.5, -0.3, 1.45, 0.5, 0, 'walnut', top='oak')
        for i in range(1, 6):
            g.add(box(-1.45 + i * 0.48 - 0.02, -0.5, 0, -1.45 + i * 0.48 + 0.02, 0.5, 0.025, 'walnut'))
        R.parts.add(g.xform(yaw, x, y, z))
    elif kind == 'shelf':
        g = box(-1.0, -0.5, -0.35, 1.0, 0.5, 0, 'walnut')
        for i in range(1, 5):
            g.add(box(-1.0 + i * 0.4 - 0.02, -0.5, 0, -1.0 + i * 0.4 + 0.02, 0.5, 0.03, 'walnut'))
        R.parts.add(g.xform(yaw, x, y, z))
        for i in range(4):
            bk = book_geo(0.18, 0.05, 0.26, rng.choice(('oxblood', 'green', 'leather')))
            orient(bk, rng.uniform(0, 6), rng.uniform(-1, 1), rng.uniform(-1, 1), x + rng.uniform(-1, 1), y + rng.uniform(-0.5, 0.5), z + rng.uniform(0.3, 1.2))
            R.nocol.add(bk)
    else:   # a block of catalogue drawers
        g = box(-0.6, -0.5, -0.7, 0.6, 0.5, 0, 'walnut')
        for i in range(3):
            for j in range(2):
                g.add(box(-0.55 + i * 0.37, -0.52, -0.62 + j * 0.3, -0.22 + i * 0.37, -0.5, -0.36 + j * 0.3, 'oak'))
        R.parts.add(g.xform(yaw, x, y, z))


def debris(R, rng):
    """Everything else, hanging still: books, loose pages, shards of window glass, splinters and smoke."""
    def pos(rmin, rmax, zmin, zmax):
        for _ in range(30):
            a = rng.uniform(0, 2 * math.pi)
            r = rmin + (rmax - rmin) * rng.random() ** 1.4
            x, y = BX + math.cos(a) * r, BY + math.sin(a) * r
            z = rng.uniform(zmin, zmax)
            if T + 0.6 < x < W - T - 0.6 and T + 0.6 < y < D - T - 0.6 and math.hypot(r, (z - PZ) * 1.3) > CALM:
                return x, y, z, a
        return None
    for k in range(260):
        p = pos(CALM, 14.0, 2.2, H - 0.5)
        if not p: continue
        x, y, z, a = p
        roll = rng.random()
        if roll < 0.4:
            g = book_geo(rng.uniform(0.16, 0.26), rng.uniform(0.03, 0.07), rng.uniform(0.22, 0.32), rng.choice(('oxblood', 'green', 'leather', 'walnut')))
        elif roll < 0.62:
            g = open_book(rng.uniform(0.16, 0.24), rng.uniform(0.22, 0.32), rng.uniform(0.1, 0.9), rng.choice(('oxblood', 'green', 'leather')))
        else:
            g = Geo()
            leaf_poly(g, [(0, 0, 0), (0.21, 0, 0), (0.21, 0.29, 0), (0, 0.29, 0)], 'ivory', off=0.003)
        orient(g, rng.uniform(0, 6.28), rng.uniform(-1.4, 1.4), rng.uniform(-1.4, 1.4), x, y, z)
        R.nocol.add(g)
    # whole cases and chairs tumbling in the air, books spilling out of the cases
    for (a, r, z) in ((0.4, 6.5, 5.2), (2.3, 7.5, 4.6), (4.0, 6.0, 5.6)):
        x, y = BX + math.cos(a) * r, BY + math.sin(a) * r
        g = Geo(); save = R.nocol; R.nocol = g
        shelf(R, -1.1, 0, -1.0, 2.2, '+y', rows=5, frame='walnut', solid=False)
        R.nocol = save
        R.slabs = R.slabs[:-5]
        orient(g, a + rng.uniform(-0.5, 0.5), rng.uniform(-0.8, 0.8), rng.uniform(0.6, 1.4), x, y, z)
        R.nocol.add(g)
        for k in range(14):
            b = book_geo(0.19, 0.05, 0.26, rng.choice(('oxblood', 'green', 'leather')))
            d = rng.uniform(0.5, 2.5)
            orient(b, rng.uniform(0, 6), rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), x + math.cos(a) * d + rng.uniform(-0.6, 0.6), y + math.sin(a) * d + rng.uniform(-0.6, 0.6), z + rng.uniform(-1.2, 1.0))
            R.nocol.add(b)
    for k in range(10):
        p = pos(CALM + 0.5, 9.0, 2.4, 6.2)
        if not p: continue
        x, y, z, a = p
        c = chair(0, 0, 0)
        orient(c, rng.uniform(0, 6.28), rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), x, y, z)
        R.nocol.add(c)
    # glass: shards from the east windows, blown in toward the centre
    for k in range(150):
        y = rng.choice((rng.uniform(1.4, 5.6), rng.uniform(10.6, 14.0), rng.uniform(18.0, 21.4), rng.uniform(26.4, 30.6)))
        x = W - T - rng.uniform(0.3, 9.0) ** 1.0
        z = rng.uniform(1.0, 6.8)
        s = rng.uniform(0.08, 0.35)
        g = Geo()
        leaf_poly(g, [(0, 0, 0), (s, rng.uniform(-0.3, 0.3) * s, 0), (rng.uniform(0.2, 0.8) * s, s * rng.uniform(0.8, 1.6), 0)], 'chrome', off=0.002)
        orient(g, rng.uniform(0, 6.28), rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), x, y, z)
        R.nocol.add(g)
    # splinters and smoke round the calm
    for k in range(60):
        p = pos(CALM, 8.0, 1.0, H - 0.6)
        if not p: continue
        x, y, z, a = p
        L = rng.uniform(0.3, 1.2)
        R.nocol.add(beam((x, y, z), (x + math.cos(a) * L, y + math.sin(a) * L, z + rng.uniform(-0.3, 0.3)), rng.uniform(0.03, 0.08), 'walnut'))
    for k in range(18):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(CALM + 0.2, CALM + 3.0)
        z = PZ + rng.uniform(-1.2, 2.8)
        if z < 2.3: z = 2.3 + rng.random()
        s = rng.uniform(0.25, 0.6)
        R.nocol.add(blob(BX + math.cos(a) * r, BY + math.sin(a) * r, z, s, s * 0.9, s * 0.8, 12, 6, 'plaster'))
    # the chandelier that was over the centre, its crystals flung outward
    for k in range(36):
        a = 2 * math.pi * k / 36 + rng.uniform(-0.05, 0.05); r = rng.uniform(CALM + 0.3, CALM + 2.5)
        z = 6.2 + rng.uniform(-0.8, 0.8)
        R.nocol.add(blob(BX + math.cos(a) * r, BY + math.sin(a) * r, z, 0.05, 0.05, 0.12, 6, 3, 'chrome'))
    for k in range(6):
        a = 2 * math.pi * k / 6
        r = CALM + 0.8
        x, y = BX + math.cos(a) * r, BY + math.sin(a) * r
        R.nocol.add(beam((x, y, 6.6), (x + math.cos(a) * 0.9, y + math.sin(a) * 0.9, 6.9), 0.05, 'brass'))
        R.light(sphere(x + math.cos(a) * 0.9, y + math.sin(a) * 0.9, 6.95, 0.1, 8, 4, 'e_lamp'))
    R.nocol.add(cyl(BX, BY, 6.9, H, 0.015, 6, side='iron', caps=False))
    R.nocol.add(cyl(BX, BY, 6.7, 6.9, 0.25, 12, side='brass', top='brass', bottom='brass'))
