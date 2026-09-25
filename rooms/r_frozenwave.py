"""The Frozen Wave: a reading room two floors tall with a breaking wave of turquoise ice stopped over
it, mid-curl. The reading tables run on under the barrel; the light in there is the colour of the
inside of a glacier. Ice steps from the east gallery climb the wave's back to a cave in its crest."""
from lib import *
from kit_h4 import *
from kit_h4 import _norm, _cross, _sub, _dot

W = 32.0
AX = 26.0                      # the wave scales about this line on the floor
# the wave's section (x, z): the back from its foot up over the crest to the lip, then the barrel back down
OUTER = [(28.3, 0.0), (28.2, 1.6), (27.2, 3.6), (25.6, 6.6), (23.8, 9.6), (21.6, 12.4), (19.0, 14.3), (16.0, 15.0),
         (12.6, 14.7), (9.6, 13.4), (7.2, 11.2), (5.6, 8.4), (4.9, 5.6), (5.2, 3.4), (5.9, 2.6)]
INNER = [(6.6, 3.4), (6.9, 5.4), (7.9, 7.6), (9.8, 9.4), (12.4, 10.6), (15.6, 11.0), (18.4, 10.4), (20.7, 8.8),
         (22.2, 6.4), (23.2, 3.8), (23.6, 1.6), (23.7, 0.0)]
CAVE = (22.39, 14.3, 11.4, 13.7)          # mouth x, back x, floor, ceiling
NOTCH = [(22.39, 11.4), (14.3, 11.4), (14.3, 13.7), (19.82, 13.7)]
CY0, CY1 = 12.4, 17.6                      # the cave's extent along the wave
SX0, SY0, SN, SRUN = 0.36, 10.4, 40, 0.28  # the stair up the west wall
HOLE = 17.8                                 # the gallery floor is open over the stair from here
GW = 4.35


def prof(notch=False):
    o = list(OUTER)
    if notch:
        i = o.index((21.6, 12.4)); o = o[:i] + NOTCH + o[i + 1:]
    return o + INNER


def _thin_outer(t=0.32):
    """The outer curve of a thin sheet of ice lying on the barrel: the inner curve, reversed and pushed out."""
    rv = INNER[::-1]
    L = [0.0]
    for p, q in zip(rv, rv[1:]): L.append(L[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    Lo = [0.0]
    for p, q in zip(OUTER, OUTER[1:]): Lo.append(Lo[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    out = []
    for f in Lo:
        d = f / Lo[-1] * L[-1]
        k = max(0, min(len(rv) - 2, next((i for i in range(len(L) - 1) if L[i + 1] >= d), len(L) - 2)))
        u = (d - L[k]) / max(1e-6, L[k + 1] - L[k])
        x = rv[k][0] + (rv[k + 1][0] - rv[k][0]) * u; z = rv[k][1] + (rv[k + 1][1] - rv[k][1]) * u
        tx, tz = rv[k + 1][0] - rv[k][0], rv[k + 1][1] - rv[k][1]; tl = math.hypot(tx, tz) or 1
        out.append((x + tz / tl * t, max(0.0, z - tx / tl * t)))
    out[0] = (out[0][0], 0.0)
    return out


THIN = None


def ring(p, y, s=1.0, dz=0.0, wob=0.0, lift=0.0, thin=0.0, jit=None):
    global THIN
    if THIN is None: THIN = _thin_outer()
    p = list(p)
    if thin > 0:
        for i in range(len(OUTER)):
            p[i] = (p[i][0] + (THIN[i][0] - p[i][0]) * thin, p[i][1] + (THIN[i][1] - p[i][1]) * thin)
    out = []
    for i, (x, z) in enumerate(p):
        if jit is not None and z > 0.5 and i not in (len(OUTER) - 1, len(OUTER)):
            x += jit.uniform(-0.28, 0.28); z += jit.uniform(-0.22, 0.22)
        out.append((AX + s * (x - AX) + wob * z / 15.0, y, s * z + dz + lift * max(0.0, z - 5.0) / 10.0))
    return out


def make():
    R = Room('frozenwave', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    rnd = random.Random(29)
    T_ = T - 0.02
    R.cut(box(T_, T_, 0, W - T_, W - T_, R.hi - 0.2, 'tile', bottom='terrazzo', top='plaster'))
    # a coffered ceiling: dark beams both ways
    for k in range(1, 8):
        p = k * 4.0
        R.nocol.add(box(T, p - 0.12, R.hi - 0.6, W - T, p + 0.12, R.hi - 0.2, 'walnut'))
        R.nocol.add(box(p - 0.12, T, R.hi - 0.6, p + 0.12, W - T, R.hi - 0.2, 'walnut'))

    wave(R, rnd)
    cave(R, rnd)
    galleries(R, rnd)
    reading(R, rnd)

    navloop(R, [(2.4, 2.4), (8, 2.4), (16, 2.4), (24, 2.4), (29.9, 2.4), (29.9, 16), (29.9, 29.6), (24, 29.6), (16, 29.6), (8, 29.6), (2.4, 29.6), (2.4, 16)])
    navloop(R, [(15.0, 5.0), (18.6, 5.0), (18.6, 27.0), (15.0, 27.0)])
    a, b = R.navpt(1.3, SY0 - 0.5), R.navpt(1.3, SY0 + SN * SRUN + 0.8, LH)
    R.link(a, b)
    navloop(R, [(2.2, 2.2), (16, 2.2), (W - 2.2, 2.2), (W - 2.2, 16), (W - 2.2, W - 2.2), (16, W - 2.2), (2.2, W - 2.2), (2.2, 16)], z=LH)
    R.spot('probe', 16.0, 8.0, 3.0)
    R.meta.update(label='The Frozen Wave', weight=3,
                  blurb='The wave came in over the reading room and stopped, and nobody has mentioned it since. Under the curl the light is green and cold and very good for reading.')
    R.meta['box'] = [[T, 0, T], [W - T, R.hi, W - T]]
    fx(R, 'dust', [8.0, 5.0, 0.5, 24.0, 27.0, 9.0])
    fx(R, 'fog', [T, T, 0.0, W - T, W - T, 1.2], density=0.03)
    secret(R, 18.0, 15.0, CAVE[2], 'The Cave in the Crest',
           'You climbed the back of the wave. Inside its crest there is a chair, a lamp and a blanket, and the whole reading room far below, blue through the ice.', r=2.2)
    return tidy(R)


def wave(R, rnd):
    P = prof(); PN = prof(True)
    A = [ring(P, 5.0, 0.8, 0, 0.3, 0.0, 1.0), ring(P, 6.4, 0.86, 0, 0.4, 0.2, 0.55, rnd), ring(P, 8.2, 0.92, 0, 0.2, -0.3, 0.2, rnd),
         ring(P, 10.3, 0.97, 0, -0.1, 0.1, 0.0, rnd), ring(P, CY0)]
    C = [ring(P, CY1), ring(P, 19.8, 0.97, 0, -0.3, 0.3, 0.0, rnd), ring(P, 22.0, 0.93, 0, 0.25, -0.2, 0.1, rnd),
         ring(P, 24.6, 0.87, 0, -0.1, 0.2, 0.5, rnd), ring(P, 27.0, 0.8, 0, 0.2, 0.0, 1.0)]
    R.parts.add(loft(A, 'ice', cap_m='icedk'))
    R.parts.add(loft(C, 'ice', cap_m='icedk'))
    g = loft([ring(PN, CY0), ring(PN, CY1)], 'ice')
    g.f = g.f[:-2]; g.m = g.m[:-2]; g.uv = g.uv[:-2]        # its ends are the other sections' faces
    R.parts.add(g)
    # the barrel glows: patches of light just proud of the inner face
    no = len(OUTER)
    for sec in (A, C):
        for i in range(len(sec) - 1):
            for k in list(range(no, no + len(INNER) - 2)) + list(range(3, no - 3)):
                if rnd.random() < (0.45 if k >= no else 0.8): continue
                q = [sec[i][k], sec[i][k + 1], sec[i + 1][k + 1], sec[i + 1][k]]
                c = [sum(p[j] for p in q) / 4 for j in range(3)]
                t = rnd.uniform(0.2, 0.45)
                q = [tuple(c[j] + (p[j] - c[j]) * (1 - t) for j in range(3)) for p in q]
                to = _norm((16.0 - c[0], 0.0, 4.0 - c[2])) if k >= no else _norm((c[0] - 16.0, 0.0, c[2] - 4.0))
                q = [tuple(p[j] + to[j] * 0.05 for j in range(3)) for p in q]
                if rnd.random() < 0.5: q = q[:3]
                elif rnd.random() < 0.5: q = [q[0], q[2], q[3]]
                e = Geo(); ids = [e.vert(p) for p in q]
                n = _cross(_sub(q[1], q[0]), _sub(q[2], q[0]))
                if _dot(n, to) < 0: ids = ids[::-1]
                e.face(ids, 'e_ice', [(0, 0), (1, 0), (1, 1), (0, 1)][:len(ids)])
                R.light(e)
    # shards on the back and crest, icicles along the lip
    for sec in (A[1:], C[:-1]):
        for i in range(len(sec) - 1):
            for n_ in range(10):
                k = rnd.randrange(2, no - 1); t = rnd.random()
                p0, p1 = sec[i][k], sec[i + 1][k]
                c = tuple(p0[j] + (p1[j] - p0[j]) * t for j in range(3))
                if c[2] < 2.5: continue
                L = rnd.uniform(0.4, 1.3)
                s = box(-L / 2, -L * 0.25, -L * 0.2, L / 2, L * 0.25, L * 0.35, rnd.choice(('ice', 'icedk', 'ice')))
                rot(s, 'x', rnd.uniform(-0.8, 0.8)); rot(s, 'y', rnd.uniform(-0.8, 0.8))
                R.nocol.add(s.xform(rnd.uniform(0, math.pi), c[0], c[1], c[2]))
    for sec in (A[1:], C[:-1]):
        for i in range(len(sec) - 1):
            p0, p1 = sec[i][no - 1], sec[i + 1][no - 1]
            n_ = int(abs(p1[1] - p0[1]) / 0.35)
            for m in range(n_):
                t = (m + rnd.random()) / n_
                x, y, z = (p0[j] + (p1[j] - p0[j]) * t for j in range(3))
                if z < 3.0: continue
                L = rnd.uniform(0.3, 1.6)
                R.nocol.add(cone(x + rnd.uniform(-0.1, 0.35), y, z + 0.1, z - L, rnd.uniform(0.05, 0.14), 0.005, 5, 'ice'))


def cave(R, rnd):
    x0, x1, zf, zc = CAVE[1], CAVE[0], CAVE[2], CAVE[3]
    # the ice stair from the east gallery up the back of the wave to the cave mouth
    n, rise, run = 17, 0.2, 0.32
    xs = W - GW + 0.05
    y0, wdt = 13.3, 3.4
    L = n * run
    R.flight(xs, y0, LH, wdt, n, rise, run, '-x', m='ice', riser='icedk', side='icedk')
    for yy in (y0 - 0.3, y0 + wdt):
        R.parts.add(slope_box(xs - L, xs + 0.3, yy, yy + 0.3, zf - 1.2, LH - 0.4, zf + 1.05, LH + 1.05 + 0.2, 'ice'))
    R.parts.add(box(xs - L - 0.3, CY0, zf, xs - L + 0.05, y0 - 0.3, zf + 1.05, 'ice'))
    R.parts.add(box(xs - L - 0.3, y0 + wdt + 0.3, zf, xs - L + 0.05, CY1, zf + 1.05, 'ice'))
    # inside: a rug, a chair, a lamp, a book, a blanket; light through the walls
    cx = 18.0
    R.nocol.add(box(15.2, 13.2, zf, 20.6, 16.8, zf + 0.02, 'carpet'))
    R.parts.add(box(15.0, 13.0, zf, 16.9, 14.2, zf + 0.3, 'velvet', top='bed'))
    R.spot('bed', 15.95, 13.6, zf + 0.3, 0.0)
    table(R, 17.0, 15.9, 18.4, 16.7, zf, top='leather')
    desk_lamp(R, 17.4, 16.3, zf + 0.76)
    open_book(R, 18.0, 16.3, zf + 0.76, 0.2)
    chair(R, 17.7, 15.3, math.pi / 2, zf)
    R.spot('plaque', 19.4, 15.0, zf, 0.0, text='WAIT, said the sea, and everything did.')
    book_pile(R, 15.4, 16.9, zf, 6, rnd)
    book_pile(R, 19.9, 13.0, zf, 4, rnd)
    R.light(box(14.35, 13.6, zf + 0.6, 14.38, 16.4, zc - 0.4, 'e_ice'))
    candle(R, 16.6, 14.0, zf + 0.3, h=0.18)


def galleries(R, rnd):
    top_y = SY0 + SN * SRUN
    x1 = SX0 + 1.9
    deck = lambda x0, y0, x1_, y1: R.parts.add(box(x0, y0, TOP, x1_, y1, LH, 'wood', top='floor', bottom='plaster'))
    deck(T, T, GW, HOLE); deck(x1, HOLE, GW, top_y); deck(T, top_y, GW, W - T)
    deck(W - GW, T, W - T, W - T); deck(GW, T, W - GW, GW); deck(GW, W - GW, W - GW, W - T)
    # rails on every edge, open where the ice stair leaves the east gallery
    rl = lambda x0, y0, x1_, y1: balus(R, x0, y0, x1_, y1, LH, h=1.0, m='wood', cap='brass')
    rl(GW - 0.1, GW + 0.1, GW - 0.1, W - GW - 0.1)
    rl(W - GW + 0.1, GW + 0.1, W - GW + 0.1, 13.0); rl(W - GW + 0.1, 17.0, W - GW + 0.1, W - GW - 0.1)
    rl(GW - 0.2, GW - 0.1, W - GW + 0.2, GW - 0.1); rl(GW - 0.2, W - GW + 0.1, W - GW + 0.2, W - GW + 0.1)
    rl(x1 + 0.1, HOLE - 0.2, x1 + 0.1, top_y); rl(T, HOLE - 0.1, x1 + 0.2, HOLE - 0.1)
    # the stair up the west wall, railed on its open side
    R.flight(SX0, SY0, 0, 1.9, SN, 0.2, SRUN, '+y', m='terrazzo', riser='tile', side='tile')
    stair_rail(R, x1 - 0.03, SY0 + SRUN, 0.2, x1 - 0.03, top_y, LH)
    # books round the walls, both floors
    spans = ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8))
    for (a, b) in spans:
        for (z, rows) in ((0.0, 16), (LH, 14)):
            sh(R, '+y', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-y', W - T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-x', W - T, a, b, z=z, rows=rows, frame='walnut')
            if a > 9 and z == 0: continue
            if a > 9: sh(R, '+x', T, a, HOLE - 0.3, z=z, rows=rows, frame='walnut'); continue
            sh(R, '+x', T, a, b, z=z, rows=rows, frame='walnut')
    # lamps under and over the galleries
    for k in range(6):
        p = 3.2 + k * (W - 6.4) / 5
        for (x, y) in ((2.2, p), (W - 2.0, p), (p, 2.0), (p, W - 2.0)):
            bulb(R, x, y, 6.2, r=0.15, top=TOP)
            bulb(R, x, y, LH + 4.2, r=0.2, top=R.hi - 0.6, m='e_lamp')
    for (x, y) in ((GW - 0.1, 8.0), (GW - 0.1, 24.0), (W - GW + 0.1, 8.0), (W - GW + 0.1, 24.0), (10.0, GW - 0.1), (22.0, GW - 0.1), (10.0, W - GW + 0.1), (22.0, W - GW + 0.1)):
        R.light(sphere(x, y, LH + 1.28, 0.1, 8, 4, 'e_amber'))


def reading(R, rnd):
    for x in (9.2, 13.0, 16.8, 20.4):
        for (ya, yb) in ((7.0, 10.0), (11.5, 14.5), (16.0, 19.0), (20.5, 23.5)):
            table(R, x - 0.55, ya, x + 0.55, yb, top='leather')
            for y in (ya + 0.8, yb - 0.8):
                desk_lamp(R, x, y, 0.76)
                chair(R, x - 0.95, y, 0.0); chair(R, x + 0.95, y, math.pi)
            if rnd.random() < 0.5: open_book(R, x - 0.2, (ya + yb) / 2, 0.76, rnd.uniform(-0.3, 0.3))
            else: book_pile(R, x + 0.1, (ya + yb) / 2, 0.76, rnd.randint(2, 5), rnd)
    # a runner of marble down the middle, and night lamps on posts between the rows
    for (x, y) in ((11.1, 11.0), (11.1, 20.0), (18.6, 11.0), (18.6, 20.0), (7.5, 15.2), (22.3, 15.2)):
        post_lamp(R, x, y, 0, 2.4)
