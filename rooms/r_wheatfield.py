"""The Wheat Field: four library walls, bookcases seven metres high, and between them a field of ripe
wheat, chest high, rustling with no wind. Beaten paths come in from the doorways. In the far wall a
gap opens on a low sun going down over more wheat. In the middle, on a gentle rise, a writing desk,
its lamp lit. Under the desk a trapdoor lies open on a cellar of seed and books."""
from kit_h9 import *

W, D = 32.0, 32.0
YN = 28.8                         # the field's north wall (the sunset is set into it)
HX, HY, HH, HR = 16.0, 16.0, 0.75, 11.0     # the rise in the middle
AX0, AX1, AZ = 11.0, 21.0, 5.2   # the gap onto the sunset
KX0, KX1, KY0, KY1, KZ = 12.5, 19.5, 14.6, 19.8, -1.9    # the cellar
TX0, TX1, TY0, TY1 = 15.5, 16.5, 16.0, 18.0                # the hatch
PATHS_X = (8.0, 24.0)
PATHS_Y = (8.0, 24.0)
PW = 0.8                          # half a path's width


def ground(x, y):
    return HH * smooth_bump(math.hypot(x - HX, y - HY), HR)


def on_path(x, y):
    return any(abs(x - p) < PW for p in PATHS_X) or any(abs(y - p) < PW for p in PATHS_Y) or math.hypot(x - HX, y - HY) < 2.9


def make():
    R = Room('wheatfield', 2, 2, res=2048)
    R.sockets(floor='earth', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, YN, TOP - 0.1, 'tile', bottom='earth', top='damask'))
    tunnel_y(R, 8.0, YN - 0.05, D - T - 0.5, floor='earth')
    tunnel_y(R, 24.0, YN - 0.05, D - T - 0.5, floor='earth')
    walls(R)
    sunset(R)
    rise(R)
    wheat(R)
    desk(R)
    cellar(R)
    fx(R, 'dust', [T, T, 0.3, W - T, YN, 4.0])
    # walkers: the paths
    for (a, b) in (((8.0, 1.6), (8.0, 27.8)), ((24.0, 1.6), (24.0, 27.8)), ((1.6, 8.0), (30.4, 8.0)), ((1.6, 24.0), (30.4, 24.0))):
        R.link(R.navpt(a[0], a[1], ground(*a)), R.navpt((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, ground((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)), R.navpt(b[0], b[1], ground(*b)))
    secret(R, 16.0, 18.9, KZ, 'The Seed Cellar',
           'Under the desk, down the ladder: a cellar of sacks and jars and seed catalogues, every one a different wheat. Someone has been planting the field from the books, a row at a time, for a very long while.')
    return finish(R, 'The Wheat Field', weight=3, probe=(16, 12, 2.0), top=TOP - 0.1,
                  blurb='Between the bookcases, where the floor should be, there is a field of wheat, ripe and gold and shoulder high. It moves as if in a wind. There is no wind.')


# ---------------------------------------------------------------------------
def walls(R):
    rows = 17
    segs = lambda n: [(k * C + 0.6, k * C + C / 2 - 1.8) for k in range(n)] + [(k * C + C / 2 + 1.8, (k + 1) * C - 0.6) for k in range(n)]
    for (a, b) in segs(2):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '+x', T, a, min(b, YN - 0.3), rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, min(b, YN - 0.3), rows=rows, frame='walnut')
    for (a, b) in ((0.6, 6.2), (9.8, AX0 - 0.6), (AX1 + 0.6, 22.2), (25.8, W - 0.6)):
        sh(R, '-y', YN, a, b, rows=14, frame='walnut')
    for c in (8.0, 24.0):
        sh(R, '+y', T, c - 1.8, c + 1.8, z=4.4, rows=7, frame='walnut')
        sh(R, '-y', YN, c - 1.8, c + 1.8, z=4.4, rows=4, frame='walnut')
        sh(R, '+x', T, c - 1.8, c + 1.8, z=4.4, rows=7, frame='walnut')
        sh(R, '-x', W - T, c - 1.8, c + 1.8, z=4.4, rows=7, frame='walnut')
    # stone piers between the bookcases, green lamps on them
    for t in (16.0,):
        for (x, y, f, g) in ((t, T, 0, 1), (T, t, 1, 0), (W - T, t, -1, 0)) + (((t, YN, 0, -1),) if not (AX0 - 0.6 < t < AX1 + 0.6) else ()):
            if y > YN: continue
            x0, x1 = (x - 0.3, x + 0.3) if f == 0 else sorted((x, x + 0.5 * f))
            y0, y1 = (y - 0.3, y + 0.3) if g == 0 else sorted((y, y + 0.5 * g))
            R.parts.add(box(x0, y0, 0, x1, y1, TOP - 0.1, 'tile'))
            lx, ly = x + 0.62 * f, y + 0.62 * g
            for z in (3.2, 6.2):
                R.nocol.add(frustum(lx, ly, z - 0.1, z + 0.12, 0.2, 0.07, 10, 'green', inner='ivory'))
                R.light(cyl(lx, ly, z - 0.06, z - 0.03, 0.1, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # a dark coffered ceiling far overhead, and a clerestory of evening light along the top of the north wall
    for k in range(1, 8):
        x = T + k * (W - 2 * T) / 8
        R.nocol.add(box(x - 0.15, T, TOP - 0.45, x + 0.15, YN, TOP - 0.1, 'walnut'))
        y = T + k * (YN - T) / 8
        R.nocol.add(box(T, y - 0.15, TOP - 0.45, W - T, y + 0.15, TOP - 0.1, 'walnut'))
    for (a, b) in ((1.0, 6.8), (9.2, 22.8), (25.2, W - 1.0)):
        R.cut(box(a, YN - 0.3, 6.5, b, YN + 0.3, 7.2, 'tile', bottom='tile', top='tile'))
        R.light(panel_y(YN + 0.28, a, b, 6.5, 7.2, 'e_dusk', face=-1))
        for x in range(int(a) + 1, int(b), 1):
            R.nocol.add(box(x - 0.04, YN - 0.1, 6.5, x + 0.04, YN, 7.2, 'walnut'))
    # rolling ladders leaning here and there
    R.nocol.add(ladder_on(T + 0.34, 4.0, 0.0, 5.5))
    R.nocol.add(ladder_on(W - T - 0.34, 19.0, math.pi, 5.5))


def ladder_on(x, y, a, h):
    from kit_a import ladder
    return ladder(x, y, a, h=h, lean=0.9)


def sunset(R):
    """The gap in the north wall: more wheat going down to a horizon, a low sun, an orange sky."""
    yb = D - T - 0.02
    R.cut(box(AX0, YN - 0.05, 0.0, AX1, D - T, AZ, 'tile', bottom='earth', top='tile'))
    R.parts.add(box(AX0 - 0.3, YN - 0.3, AZ, AX1 + 0.3, YN, AZ + 0.6, 'walnut'))
    for x in (AX0 - 0.3, AX1):
        R.parts.add(box(x, YN - 0.3, 0.0, x + 0.3, YN, AZ, 'walnut'))
    R.light(panel_y(yb, AX0, AX1, 1.25, 1.45, 'e_sun', face=-1))
    R.light(panel_y(yb, AX0, AX1, 1.45, 2.4, 'e_dusk', face=-1))
    R.light(panel_y(yb, AX0, AX1, 2.4, AZ, 'e_skydome', face=-1))
    R.nocol.add(panel_y(yb - 0.01, AX0, AX1, 0.0, 1.25, 'wheatdk', face=-1))
    # the sun, half down behind the far field
    g = Geo(); n = 16; cx, cz, r = 15.2, 1.25, 0.62
    ids = [g.vert((cx + r * math.cos(math.pi * k / n), yb - 0.03, cz + r * math.sin(math.pi * k / n))) for k in range(n + 1)]
    g.face(ids[::-1], 'e_sun', [(0, 0)] * (n + 1))
    R.light(g)
    # rows of wheat in the gap, smaller and smaller toward the horizon
    rnd = random.Random(77)
    for k, y in enumerate((29.2, 29.8, 30.35, 30.8, 31.15, 31.4)):
        s = 1.0 - k * 0.15
        wheat_row(R, AX0 + 0.05, AX1 - 0.05, y, rnd, lambda x, y: 0.0, h0=0.9 * s, ear=0.22 * s, step=0.1 * s + 0.02, m='wheat' if k % 2 else 'wheatdk')


def mfield(fn, mf, x0, y0, x1, y1, nx, ny, skip=None):
    """A heightfield sheet (faces up) whose material comes from mf(x, y)."""
    g = Geo(); ids = {}
    def V(i, j):
        if (i, j) not in ids:
            x = x0 + (x1 - x0) * i / nx; y = y0 + (y1 - y0) * j / ny
            ids[(i, j)] = g.vert((x, y, fn(x, y)))
        return ids[(i, j)]
    for i in range(nx):
        for j in range(ny):
            cx = x0 + (x1 - x0) * (i + 0.5) / nx; cy = y0 + (y1 - y0) * (j + 0.5) / ny
            if skip and skip(cx, cy): continue
            q = [V(i, j), V(i + 1, j), V(i + 1, j + 1), V(i, j + 1)]
            if all(g.v[v][2] < 0.004 for v in q): continue
            g.face(q, mf(cx, cy), [(g.v[v][0], g.v[v][1]) for v in q])
    return g


def rise(R):
    """The low rise in the middle of the field, with the hatch in it."""
    hole = lambda x, y: TX0 < x < TX1 and TY0 < y < TY1
    R.parts.add(mfield(ground, lambda x, y: 'path' if on_path(x, y) else 'earth', HX - HR, HY - HR, HX + HR, HY + HR, 44, 44, skip=hole))
    # the paths on the flat, beyond the rise
    for p in PATHS_X:
        R.nocol.add(box(p - PW, T, 0.0, p + PW, YN, 0.006, 'path'))
    for p in PATHS_Y:
        R.nocol.add(box(T, p - PW, 0.0, W - T, p + PW, 0.006, 'path'))
    R.nocol.add(box(AX0, YN, 0.0, AX1, D - T, 0.006, 'earth'))


def wheat_row(R, x0, x1, y, rnd, gfn, h0=0.9, ear=0.25, step=0.13, m='wheat', seg=3.0):
    """A row of wheat: a thin sheet with a ragged top of ears (both faces drawn, not collided)."""
    x = x0
    while x < x1 - 0.2:
        xe = min(x1, x + seg)
        top = []
        t = x
        while t < xe:
            b = h0 * rnd.uniform(0.78, 1.0)
            w = step * rnd.uniform(0.7, 1.3)
            lean = rnd.uniform(-0.25, 0.25) * w
            top.append((t, b)); top.append((min(xe, t + w * 0.5 + lean), b + ear * rnd.uniform(0.35, 1.25)))
            t += w
        top.append((xe, h0 * 0.85))
        yy = y + rnd.uniform(-0.1, 0.1)
        nb = max(2, int((xe - x) / 0.6))
        bot = [(x + (xe - x) * k / nb, -0.05) for k in range(nb + 1)]
        P = [(px, yy, gfn(px, yy) + pz) for (px, pz) in bot] + [(px, yy, gfn(px, yy) + pz) for (px, pz) in reversed(top)]
        g = Geo()
        ids = [g.vert(p) for p in P]
        g.face(ids, m, [(p[0], p[2]) for p in P])
        ids2 = [g.vert((p[0], p[1] + 0.015, p[2])) for p in P]
        g.face(ids2[::-1], m, [(p[0], p[2]) for p in P[::-1]])
        R.nocol.add(g)
        x = xe


def wheat(R):
    rnd = random.Random(84)
    y = T + 0.9
    k = 0
    while y < YN - 0.8:
        if not any(abs(y - p) < PW + 0.15 for p in PATHS_Y):
            # break the row at the paths and the clearing round the desk
            cuts = [(p - PW - 0.1, p + PW + 0.1) for p in PATHS_X]
            dy = abs(y - HY)
            if dy < 2.9:
                dx = math.sqrt(2.9 ** 2 - dy ** 2)
                cuts.append((HX - dx, HX + dx))
            if TY0 - 0.3 < y < TY1 + 0.6: cuts.append((TX0 - 0.6, TX1 + 0.6))
            for (a, b) in spans_(1.2, W - 1.2, cuts):
                wheat_row(R, a, b, y, rnd, ground, h0=rnd.uniform(0.86, 1.0), ear=0.3, m='wheat' if k % 3 else 'wheatdk')
        y += 0.62
        k += 1
    # a few poppies and cornflowers
    for i in range(60):
        x, yy = rnd.uniform(1.5, W - 1.5), rnd.uniform(1.5, YN - 1.5)
        if on_path(x, yy): continue
        z = ground(x, yy) + rnd.uniform(0.7, 1.0)
        R.nocol.add(sphere(x, yy, z, 0.045, 6, 3, 'hutred' if i % 3 else 'ivory'))


def spans_(a, b, cut):
    segs = [(a, b)]
    for (c0, c1) in cut:
        nxt = []
        for (s0, s1) in segs:
            if c1 <= s0 or c0 >= s1: nxt.append((s0, s1)); continue
            if c0 > s0: nxt.append((s0, c0))
            if c1 < s1: nxt.append((c1, s1))
        segs = nxt
    return [s for s in segs if s[1] - s[0] > 0.3]


def desk(R):
    z = ground(HX, HY)
    x0, x1, y0, y1 = HX - 0.9, HX + 0.9, HY - 0.45, HY + 0.45
    R.parts.add(box(x0, y0, z + 0.72, x1, y1, z + 0.78, 'walnut', top='leather'))
    for (px, py) in ((x0 + 0.08, y0 + 0.08), (x1 - 0.08, y0 + 0.08), (x1 - 0.08, y1 - 0.08), (x0 + 0.08, y1 - 0.08)):
        R.parts.add(box(px - 0.05, py - 0.05, z - 0.1, px + 0.05, py + 0.05, z + 0.72, 'walnut'))
    for (a, b) in ((x0 + 0.1, x0 + 0.5), (x1 - 0.5, x1 - 0.1)):   # two drawers
        R.parts.add(box(a, y0 + 0.05, z + 0.55, b, y1 - 0.05, z + 0.72, 'walnut'))
    desk_lamp(R, x1 - 0.3, HY + 0.1, z + 0.78)
    g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, 'leather'); g.add(box(-0.19, -0.13, 0.02, -0.005, 0.13, 0.05, 'ivory')); g.add(box(0.005, -0.13, 0.02, 0.19, 0.13, 0.05, 'ivory'))
    R.nocol.add(g.xform(0.1, HX - 0.1, HY - 0.1, z + 0.78))
    book_pile(R, x0 + 0.25, HY + 0.1, z + 0.78, 5, random.Random(5), 0.3)
    R.nocol.add(cyl(HX + 0.3, HY + 0.25, z + 0.78, z + 0.84, 0.035, 8, side='black', top='black', bottom='black'))
    R.parts.add(chair(HX, HY - 0.9, math.pi / 2).xform(0, 0, 0, ground(HX, HY - 0.9))); R.spot('sit', HX, HY - 0.9, z + 0.48, math.pi / 2)
    R.spot('read', HX, HY - 0.9, z + 0.48, math.pi / 2)


def cellar(R):
    """Down through the hatch: a low cellar of sacks, jars and seed catalogues."""
    R.cut(box(KX0, KY0, KZ, KX1, KY1, 0.02, 'tile', bottom='oak', top='oak'))
    # its ceiling: planks on beams, with the hatch opening through it and a frame up to the ground
    for (a0, b0, a1, b1) in ((KX0, KY0, KX1, TY0), (KX0, TY1, KX1, KY1), (KX0, TY0, TX0, TY1), (TX1, TY0, KX1, TY1)):
        R.parts.add(box(a0, b0, 0.0, a1, b1, 0.2, 'oak', bottom='oak'))
    for k in range(6):
        x = KX0 + 0.5 + k * (KX1 - KX0 - 1.0) / 5
        if TX0 - 0.2 < x < TX1 + 0.2: continue
        R.nocol.add(box(x - 0.1, KY0, -0.22, x + 0.1, KY1, 0.0, 'walnut'))
    zt = lambda x, y: ground(x, y) + 0.03
    for (a0, b0, a1, b1) in ((TX0 - 0.08, TY0 - 0.08, TX1 + 0.08, TY0), (TX0 - 0.08, TY1, TX1 + 0.08, TY1 + 0.08), (TX0 - 0.08, TY0, TX0, TY1), (TX1, TY0, TX1 + 0.08, TY1)):
        R.parts.add(box(a0, b0, 0.0, a1, b1, zt((a0 + a1) / 2, (b0 + b1) / 2), 'oak'))
    # the trapdoor, thrown open flat on the ground beside the hole
    leaf = Geo()
    n = 4
    for k in range(n):
        y0 = TY0 + (TY1 - TY0) * k / n; y1 = TY0 + (TY1 - TY0) * (k + 1) / n
        x0, x1 = TX1 + 0.25, TX1 + 0.25 + (TX1 - TX0)
        leaf.add(box(x0, y0, ground(x1, y1) + 0.02, x1, y1 - 0.01, ground(x1, y1) + 0.07, 'oak'))
    for y in (TY0 + 0.3, TY1 - 0.3):
        leaf.add(box(TX1 + 0.3, y - 0.05, ground(TX1 + 0.8, y) + 0.07, TX1 + 1.2, y + 0.05, ground(TX1 + 0.8, y) + 0.1, 'iron'))
    R.nocol.add(leaf)
    # rails either side of the hole (you come and go at its north end)
    for x in (TX0 - 0.12, TX1 + 0.12):
        rail_line(R, x, TY0 + 0.45, ground(x, TY0 + 0.45), x, TY1 + 0.05, ground(x, TY1), h=0.9, m='oak', post='walnut', spacing=0.8, mid=True)
    # the ladder down
    L = (0.0 - KZ + ground(HX, TY1)) / math.tan(math.radians(60))
    ladder_up(R, HX, TY1 - L, KZ, ground(HX, TY1), '+y', w=0.9, m='oak', rail='iron')
    # sacks, jars, books; a cot; a lantern
    rnd = random.Random(19)
    sh(R, '+y', KY0, KX0 + 0.2, KX1 - 0.2, z=KZ, rows=4, frame='oak', depth=0.3)
    sh(R, '-y', KY1, KX0 + 0.2, KX1 - 2.4, z=KZ, rows=4, frame='oak', depth=0.3)
    sh(R, '+x', KX0, KY0 + 0.4, KY1 - 0.4, z=KZ, rows=4, frame='oak', depth=0.3)
    for i in range(8):
        x, y = KX1 - 0.5 - (i % 3) * 0.55, KY0 + 1.6 + (i // 3) * 0.6
        R.parts.add(ellipsoid(x, y, KZ + 0.32, 0.28, 0.24, 0.34, 'oak' if i % 2 else 'bed', 8, 4))
    cot(R, KX1 - 2.2, KY1 - 0.9, KX1 - 0.1, KY1 - 0.1, KZ, h=0.4, frame='oak', blanket='oxblood')
    R.parts.add(table(13.4, 17.2, 14.6, 18.2, 0.74, 'oak', top='leather').xform(0, 0, 0, KZ))
    g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, 'green'); g.add(box(-0.19, -0.13, 0.02, 0.19, 0.13, 0.04, 'ivory'))
    R.nocol.add(g.xform(0.4, 14.0, 17.7, KZ + 0.74))
    for i in range(7):
        R.nocol.add(cyl(13.55 + i * 0.15, 17.35, KZ + 0.74, KZ + 0.92, 0.05, 8, side='ivory', top='wheat', bottom='ivory'))
    candle(R, 14.4, 18.0, KZ + 0.74, h=0.14, r=0.03)
    R.parts.add(chair(14.0, 18.7, -math.pi / 2).xform(0, 0, 0, KZ)); R.spot('sit', 14.0, 18.7, KZ + 0.48, -math.pi / 2)
    bulb(R, 17.6, 18.0, KZ + 1.45, r=0.1, m='e_amber', top=-0.22)
    bulb(R, 13.8, 16.2, KZ + 1.45, r=0.13, m='e_lamp', top=-0.22)
    bulb(R, 18.4, 15.6, KZ + 1.45, r=0.12, m='e_lamp', top=-0.22)
