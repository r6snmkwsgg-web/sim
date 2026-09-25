"""The Aurora Stacks: no ceiling, only a night sky with the northern lights in it; snow underfoot and
bookcases standing in it like old stones, two rows down an avenue with a dark stream running between,
stone gateways at either end with brass armillaries on their piers. In the north-west corner there is
a snow mound that is not a mound: someone has built a shelter out of books."""
from kit_h3 import *

W = D = 32.0
DOORS = ((8, 0), (24, 0), (8, D), (24, D), (0, 8), (0, 24), (W, 8), (W, 24))
IG = (5.0, 28.2)               # the book igloo
IR, IH = 2.0, 1.95             # its outer radius and height
EW = 0.9                       # its entrance: a short tunnel west, toward the wall
SX0, SX1 = 15.4, 16.6          # the stream
MONO = [(11.0, y) for y in (5.0, 10.4, 21.6, 27.0)] + [(21.0, y) for y in (5.0, 10.4, 21.6, 27.0)] + \
       [(11.0, 16.0), (21.0, 16.0)]
OUTER = [(5.2, 13.0), (5.2, 19.0), (26.8, 13.0), (26.8, 19.0), (26.8, 28.4), (26.4, 3.6), (5.2, 3.6)]


def snow(x, y):
    z = 0.12 + 0.07 * math.sin(x * 0.7 + y * 0.3) + 0.05 * math.sin(y * 1.3 - x * 0.4)
    # drifts against the stones
    for (mx, my) in MONO + OUTER:
        d = math.hypot((x - mx) / 1.2, (y - my) / 2.6)
        if d < 1: z = max(z, 0.65 * smooth_bump(d, 1.0))
    # the igloo sits in a drift of its own
    d = math.hypot(x - IG[0], y - IG[1])
    z = max(z, 0.55 * smooth_bump(max(0.0, d - IR + 0.3) / 1.8, 1.0))
    # along the walls
    for wd in (y - T, D - T - y, x - T, W - T - x):
        if wd < 1.4: z = max(z, 0.6 * smooth_bump(wd, 1.4))
    # a path trodden down the avenue and across it
    if 12.6 < x < 19.4: z = min(z, 0.06 + 0.05 * math.sin(y))
    if abs(y - 16) < 1.2 or abs(y - 8) < 1.2 or abs(y - 24) < 1.2: z = min(z, 0.08)
    for (cx, cy) in DOORS:
        dd = max(abs(x - cx), abs(y - cy))
        f = max(0.0, min(1.0, (dd - 2.3) / 2.0))
        z = -0.05 + (z + 0.05) * f
    return z


def make():
    R = Room('aurorastacks', 2, 2, res=2048)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP - 0.05, 'tile', bottom='slate', top='plaster'))
    sky(R)
    # the stream down the avenue, and two stone footbridges over it
    R.cut(box(SX0, 1.8, -0.35, SX1, D - 1.8, 0.2, 'slate', top='tile'))
    R.water.append(dict(x0=SX0, y0=1.8, x1=SX1, y1=D - 1.8, top=-0.08, bot=-0.35))
    for y in (8.0, 16.0, 24.0):
        R.parts.add(box(SX0 - 0.6, y - 0.9, 0, SX1 + 0.6, y + 0.9, 0.12, 'tile', skip=('-z',)))
        for x in (SX0 - 0.5, SX1 + 0.5):
            R.parts.add(box(x - 0.08, y - 0.9, 0.12, x + 0.08, y + 0.9, 0.45, 'tile'))
    inside = lambda x, y: math.hypot(x - IG[0], y - IG[1]) < IR - 0.05 or (IG[0] - IR - 1.3 < x < IG[0] - 0.5 and abs(y - IG[1]) < EW / 2 + 0.2)
    streambed = lambda x, y: SX0 - 0.05 < x < SX1 + 0.05 and 1.75 < y < D - 1.75
    R.parts.add(field(snow, T, T, W - T, D - T, 64, 64, m='bed', skip=lambda x, y: inside(x, y) or streambed(x, y)))
    for (x, y) in MONO:
        monolith(R, x, y, 3.2)
    for (x, y) in OUTER:
        monolith(R, x, y, 2.6, rows=6)
    for y in (2.6, D - 2.6):
        gateway(R, 16.0, y)
    lamps(R)
    igloo(R)
    fx(R, 'aurora', [T, T, 6.0, W - T, D - T, TOP])
    fx(R, 'snow', [T, T, 0, W - T, D - T, TOP], density=0.3)
    nv = navloop(R, [(13.4, 3.6), (13.4, 16), (13.4, 28.4), (18.6, 28.4), (18.6, 16), (18.6, 3.6)])
    side = navloop(R, [(8.0, 2.4), (8.0, 8.0), (8.0, 24.0), (8.0, 29.6), (24.0, 29.6), (24.0, 24.0), (24.0, 8.0), (24.0, 2.4)])
    R.link(side[1], R.navpt(2.4, 8.0)); R.link(side[2], R.navpt(2.4, 24.0)); R.link(side[5], R.navpt(29.6, 24.0)); R.link(side[6], R.navpt(29.6, 8.0))
    R.link(side[1], nv[0]); R.link(side[2], nv[2]); R.link(side[5], nv[3]); R.link(side[6], nv[5])
    for p in R.nav: p[2] = max(0.0, snow(p[0], p[1]))
    secret(R, IG[0], IG[1], 0.0, 'The Book Igloo',
           'Somebody built this out of books, course on course, and let the snow cover it. Inside it is warm, a lamp is burning, and every spine faces in.')
    return finish(R, 'The Aurora Stacks', weight=3, probe=(16.0, 12.0, 2.2),
                  blurb='There is no ceiling here, only sky, and the sky is doing something green and slow. The bookcases stand in the snow like stones, as if they were put here to mark the date.')


def _panel(R, side, a, b, z0, z1, m, e=0.012):
    if side == 'S': R.light(box(a, T, z0, b, T + e, z1, m, skip=('-y',)))
    elif side == 'N': R.light(box(a, D - T - e, z0, b, D - T, z1, m, skip=('+y',)))
    elif side == 'W': R.light(box(T, a, z0, T + e, b, z1, m, skip=('-x',)))
    else: R.light(box(W - T - e, a, z0, W - T, b, z1, m, skip=('+x',)))


def sky(R):
    """Night sky overhead and down the walls to a low stone parapet; bookcases along the parapet."""
    R.light(box(T, T, TOP - 0.1, W - T, D - T, TOP - 0.08, 'e_skydome', skip=('+z',)))
    PZ = 1.6
    for side in 'SNWE':
        for (a, b) in ((T, 6.5), (9.5, 22.5), (25.5, W - T)):
            _panel(R, side, a, b, PZ + 0.1, TOP - 0.1, 'e_skydome')
        for c in (8.0, 24.0):
            _panel(R, side, c - 1.5, c + 1.5, 4.2, TOP - 0.1, 'e_skydome')
    # the parapet: a coped stone wall to 1.6 m with low bookcases in front of it
    for (a, b) in ((T, 6.4), (9.6, 22.4), (25.6, W - T)):
        R.parts.add(box(a, T, 0, b, T + 0.3, PZ, 'tile', skip=('-z',)))
        R.parts.add(box(a, D - T - 0.3, 0, b, D - T, PZ, 'tile', skip=('-z',)))
        R.parts.add(box(T, a, 0, T + 0.3, b, PZ, 'tile', skip=('-z',)))
        R.parts.add(box(W - T - 0.3, a, 0, W - T, b, PZ, 'tile', skip=('-z',)))
        R.parts.add(box(a, T, PZ, b, T + 0.4, PZ + 0.1, 'tile'))
        R.parts.add(box(a, D - T - 0.4, PZ, b, D - T, PZ + 0.1, 'tile'))
        R.parts.add(box(T, a, PZ, T + 0.4, b, PZ + 0.1, 'tile'))
        R.parts.add(box(W - T - 0.4, a, PZ, W - T, b, PZ + 0.1, 'tile'))
    # door piers: the doorways stand in the parapet as gates
    for c in (8.0, 24.0):
        for s in (-1, 1):
            p = c + s * 1.85
            for (x0, y0, x1, y1) in ((p - 0.35, T, p + 0.35, T + 0.6), (p - 0.35, D - T - 0.6, p + 0.35, D - T),
                                     (T, p - 0.35, T + 0.6, p + 0.35), (W - T - 0.6, p - 0.35, W - T, p + 0.35)):
                R.parts.add(box(x0, y0, 0, x1, y1, 4.4, 'tile', skip=('-z',)))
        for (x0, y0, x1, y1) in ((c - 2.2, T, c + 2.2, T + 0.6), (c - 2.2, D - T - 0.6, c + 2.2, D - T),
                                 (T, c - 2.2, T + 0.6, c + 2.2), (W - T - 0.6, c - 2.2, W - T, c + 2.2)):
            R.parts.add(box(x0, y0, 4.1, x1, y1, 4.5, 'tile'))
    for (a, b) in ((T + 0.4, 6.0), (10.0, 22.0), (26.0, W - T - 0.4)):
        sh(R, '+y', T + 0.3, a, b, rows=3, frame='walnut')
        sh(R, '-y', D - T - 0.3, a, b, rows=3, frame='walnut')
    for (a, b) in ((1.1, 6.0), (10.0, 22.0), (26.0, 30.9)):
        if a > 25: continue                       # the igloo's corner: a clear way round behind it
        sh(R, '+x', T + 0.3, a, b, rows=3, frame='walnut')
    for (a, b) in ((1.1, 6.0), (10.0, 22.0), (26.0, 30.9)):
        sh(R, '-x', W - T - 0.3, a, b, rows=3, frame='walnut')


def armillary(R, x, y, z, r=0.35):
    R.parts.add(cyl(x, y, z, z + 0.25, 0.05, 8, side='brass', top='brass'))
    zc = z + 0.25 + r
    for (ax, ang) in (('x', math.pi / 2), ('y', math.pi / 2), ('x', 0.4)):
        g = ring(0, 0, -0.02, 0.02, r - 0.03, r, 24, top='brass', bottom='brass', inner='brass', outer='brass')
        rot(g, ax, ang)
        g.xform(0, x, y, zc)
        R.nocol.add(g)
    R.nocol.add(ring(x, y, zc - 0.02, zc + 0.02, r - 0.03, r, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.nocol.add(sphere(x, y, zc, 0.07, 8, 4, 'gilt'))


def monolith(R, x, y, L, rows=8):
    """A standing stone of books: a double-sided case between two stone piers, capped, snow on top."""
    y0, y1 = y - L / 2, y + L / 2
    ph = rows * 0.42 + 0.9
    for yy in (y0 - 0.35, y1 + 0.35):
        R.parts.add(box(x - 0.42, yy - 0.35, 0, x + 0.42, yy + 0.35, ph, 'tile', skip=('-z',)))
        R.parts.add(box(x - 0.5, yy - 0.43, ph, x + 0.5, yy + 0.43, ph + 0.18, 'tile'))
        blanket(R, x - 0.5, yy - 0.43, x + 0.5, yy + 0.43, ph + 0.18, t=0.07)
        armillary(R, x, yy, ph + 0.18, r=0.3 if rows > 6 else 0.24)
    R.parts.add(box(x - 0.4, y0, 0, x + 0.4, y1, 0.3, 'tile', skip=('-z',)))
    stack(R, 'y', x, y0 + 0.02, y1 - 0.02, z=0.3, rows=rows, frame='walnut')
    blanket(R, x - 0.42, y0, x + 0.42, y1, 0.3 + rows * 0.42 + 0.15, t=0.08)


def gateway(R, x, y):
    """A trilithon over the avenue."""
    for s in (-1, 1):
        px = x + s * 3.3
        R.parts.add(box(px - 0.55, y - 0.55, 0, px + 0.55, y + 0.55, 5.2, 'tile', skip=('-z',)))
        armillary(R, px, y, 6.1, r=0.4)
    R.parts.add(box(x - 4.0, y - 0.6, 5.2, x + 4.0, y + 0.6, 6.1, 'tile'))
    blanket(R, x - 4.0, y - 0.6, x + 4.0, y + 0.6, 6.1, t=0.1)
    R.light(sphere(x, y - 0.8, 4.4, 0.12, 10, 5, 'e_amber'))
    R.nocol.add(cyl(x, y - 0.8, 4.5, 5.2, 0.012, 6, side='iron', caps=False))


def lamps(R):
    for y in (3.0, 8.0, 13.2, 18.8, 24.0, 29.0):
        for x in (13.0, 19.0):
            if (y in (8.0, 24.0)) and x == 19.0: continue
            lamp_post(R, x, y, 0, 2.5)
    for (x, y) in ((8.0, 12.0), (24.0, 20.0), (8.0, 20.0), (24.0, 12.0)):
        lamp_post(R, x, y, 0, 2.3, m='e_amber')
    # reading desks by the stones, snow on them
    for (x, y, a) in ((12.3, 13.2, 0.0), (19.7, 18.8, math.pi), (12.3, 24.3, 0.0), (19.7, 7.7, math.pi)):
        R.parts.add(table(x - 0.4, y - 0.6, x + 0.4, y + 0.6, 0.78, 'walnut'))
        blanket(R, x - 0.42, y - 0.62, x + 0.42, y + 0.1, 0.78, t=0.04)
        book_pile(R, x, y + 0.3, 0.78, 3, seed=int(x * y))
        R.parts.add(chair(x + 0.75 * math.cos(a), y, a + math.pi))


def igloo(R):
    """A dome of books laid in courses, snow over its crown, a low tunnel facing the wall; a lamp inside."""
    cx, cy = IG
    rnd = random.Random(2)
    g = Geo()
    course = 0.11
    n_c = int(IH / course)
    cols = ('oxblood', 'green', 'leather', 'walnut', 'velvet', 'ivory')
    for k in range(n_c):
        z0 = k * course
        t = (z0 + course / 2) / IH
        r = IR * math.sqrt(max(0.0, 1 - t * t))
        if r < 0.25: break
        n = max(5, int(2 * math.pi * r / 0.3))
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * (k % 2)) / n
            if abs(math.atan2(math.sin(a - math.pi), math.cos(a - math.pi))) < (EW / 2 + 0.08) / r and z0 < 1.25: continue   # the doorway
            bw = 2 * math.pi * r / n - 0.01
            b = box(-0.14, -bw / 2, 0, 0.14, bw / 2, course - 0.008, rnd.choice(cols))
            b.xform(a, cx + math.cos(a) * (r - 0.14), cy + math.sin(a) * (r - 0.14), z0)
            g.add(b)
    R.nocol.add(g)
    # the snow on its crown and shoulders
    cap = ellipsoid(cx, cy, 0.0, IR + 0.06, IR + 0.06, IH + 0.08, 'bed', 20, 7, lower=False)
    keep = [i for i, f in enumerate(cap.f[:-1]) if min(cap.v[v][2] for v in f) > 0.95]
    cap.f = [cap.f[i] for i in keep]; cap.m = [cap.m[i] for i in keep]; cap.uv = [cap.uv[i] for i in keep]
    R.nocol.add(cap)
    # collider: a many-sided wall and a roof, open at the doorway
    n = 20
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        if abs(math.atan2(math.sin(am - math.pi), math.cos(am - math.pi))) < 0.35: continue
        R.col.add(obox(cx + IR * math.cos(a0), cy + IR * math.sin(a0), cx + IR * math.cos(a1), cy + IR * math.sin(a1), 0, IH, 0.3, 'tile'))
    R.col.add(cyl(cx, cy, 1.5, IH + 0.1, IR, 16, side='tile', top='tile', bottom='tile'))
    # the tunnel: two walls of stacked books and a lintel of them
    tx0, tx1 = cx - IR - 1.1, cx - IR + 0.35
    for s in (-1, 1):
        yy = cy + s * (EW / 2 + 0.15)
        for k in range(11):
            b = box(tx0, yy - 0.15, k * course, tx1, yy + 0.15, (k + 1) * course - 0.008, cols[(k + (s > 0)) % 6])
            R.nocol.add(b)
        R.col.add(box(tx0, yy - 0.15, 0, tx1, yy + 0.15, 1.3, 'tile'))
    R.parts.add(box(tx0, cy - EW / 2 - 0.3, 1.21, tx1, cy + EW / 2 + 0.3, 1.33, 'leather'))
    blanket(R, tx0 - 0.05, cy - EW / 2 - 0.35, tx1, cy + EW / 2 + 0.35, 1.33, t=0.12)
    # inside: furs, a lamp, a pile of books to sit on, an open book
    R.parts.add(cyl(cx + 0.4, cy, 0, 0.12, 0.8, 14, side='velvet', top='velvet'))
    R.spot('bed', cx + 0.4, cy, 0.12, 0.0)
    book_pile(R, cx - 0.2, cy + 1.2, 0.0, 9, seed=31)
    book_pile(R, cx - 0.6, cy - 1.1, 0.0, 7, seed=32)
    R.parts.add(cyl(cx + 1.1, cy - 0.9, 0, 0.35, 0.18, 10, side='walnut', top='walnut'))
    R.parts.add(cyl(cx + 1.1, cy - 0.9, 0.35, 0.38, 0.08, 10, side='brass', top='brass'))
    R.nocol.add(frustum(cx + 1.1, cy - 0.9, 0.62, 0.8, 0.16, 0.07, 10, 'green', inner='ivory'))
    R.nocol.add(cyl(cx + 1.1, cy - 0.9, 0.38, 0.62, 0.012, 6, side='brass', caps=False))
    R.light(cyl(cx + 1.1, cy - 0.9, 0.62, 0.66, 0.1, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.light(sphere(cx + 0.9, cy + 1.0, 0.35, 0.04, 6, 3, 'e_candle'))
    R.light(sphere(cx, cy, IH - 0.55, 0.1, 8, 4, 'e_amber'))
    R.nocol.add(cyl(cx, cy, IH - 0.47, IH, 0.01, 6, side='iron', caps=False))
    R.nocol.add(cyl(cx + 0.9, cy + 1.0, 0.0, 0.3, 0.03, 6, side='ivory', top='ivory'))
    open_book(R, cx + 0.5, cy + 0.2, 0.12, 0.5)
    R.spot('read', cx + 0.5, cy + 0.2, 0.12, 0.0)
    a, b = R.navpt(cx - IR - 1.8, cy), R.navpt(cx, cy)
    R.link(a, b)
