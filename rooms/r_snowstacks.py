"""The Snow Stacks: snow falling between tall bookcases under a vault, drifted smooth against every
stack end, and at the far end of the long avenue a fire, lit. In the north-east corner the snow has
piled higher than a man, and someone has dug into it."""
from kit_h3 import *

W = D = 32.0
AV0, AV1 = 13.4, 18.6                     # the long avenue, south to north
ROWS = 13                                 # 5.6 m stacks
# stacks run east-west: (centre y, x from, x to)
YS = (3.0, 5.4, 11.2, 13.6, 16.0, 18.4, 20.8, 27.4, 29.8)
XB = ((1.1, 6.3), (9.7, AV0 - 0.1), (AV1 + 0.1, 22.3), (25.7, 30.9))
CAVE = (28.9, 29.3)                       # the snow cave, in the north-east corner
MOUND = (29.4, 29.8, 4.3, 5.2, 3.5)       # big drift: centre, radii, height


def stacks():
    out = []
    for y in YS:
        for (a, b) in XB:
            if y > 26 and a > 24: continue           # the big drift is there
            if y > 26 and a < 2 and y > 29: continue
            out.append((y, a, b))
    return out


def make():
    R = Room('snowstacks', 2, 2, res=2048)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, 6.2, 'tile', bottom='slate', top='plaster'))
    # a pointed vault over the avenue, rising above the flat ceiling
    pr = pointed_profile(16, AV1 - AV0 + 1.2, 0, 5.4, 2.1, 10)
    R.cut(prism(pr, 'y', T - 0.02, D - T + 0.02, ['slate'] + ['plaster'] * (len(pr) - 1), cap='tile'))
    for k in range(8):
        y = 1.6 + k * 4.1
        R.nocol.add(prism(pointed_ring(16, AV1 - AV0 + 1.2, 5.4, 2.1), 'y', y - 0.18, y + 0.18, 'tile', cap='tile'))
    # windows: a great one over the fireplace, and tall ones along the south wall and the side walls
    window(R, 'N', 16, 4.2, 3.2, 1.2, em='e_skydome', mull=3, trans=1)
    for c in (3.7, 12.0, 20.0, 28.3):
        window(R, 'S', c, 3.0, 1.6, 1.8, em='e_skydome', mull=1, trans=1)
    # the stacks, snow on their tops, green lamps on desks at their ends
    for (y, a, b) in stacks():
        stack(R, 'x', y, a, b, rows=ROWS, frame='walnut')
        blanket(R, a - 0.06, y - 0.4, b + 0.06, y + 0.4, ROWS * 0.42 + 0.15, t=0.08)
    k = 0
    for (y, a, b) in stacks():
        for (x, s) in ((a, -1), (b, 1)):
            if not (abs(x - AV0) < 0.3 or abs(x - AV1) < 0.3): continue
            k += 1
            if k % 2: continue
            dx = x + s * 0.55
            R.parts.add(table(dx - 0.3, y - 0.45, dx + 0.3, y + 0.45, 0.78, 'walnut'))
            desk_lamp(R, dx, y + 0.2, 0.78)
            blanket(R, dx - 0.32, y - 0.47, dx + 0.32, y - 0.05, 0.78, t=0.04)
    wall_cases(R)
    fireplace(R)
    drifts(R)
    snow_cave(R)
    # lamps down the avenue and in the cross aisles
    for y in (4.2, 12.4, 19.6, 27.8):
        pendant(R, 16, y, 4.4, 7.5, r=0.26)
    for (x, y) in ((8.0, 8.0), (24.0, 8.0), (8.0, 24.0), (24.0, 24.0), (4.0, 8.0), (28.0, 8.0), (4.0, 24.0)):
        pendant(R, x, y, 4.0, 6.2, r=0.2)
    for (x, y) in ((AV0 - 0.3, 8.0), (AV1 + 0.3, 24.0)):
        lamp_post(R, x, y, 0, 2.6, m='e_amber')
    fx(R, 'snow', [T, T, 0, W - T, D - T, 7.4])
    fx(R, 'embers', [14.8, 30.0, 0.3, 17.2, 31.3, 3.0])
    nv = navloop(R, [(16, 1.8), (16, 8), (16, 16), (16, 24), (16, 29.6), (21, 24), (24, 24), (24, 16), (24, 8), (21, 8), (11, 8), (8, 8), (8, 16), (8, 24), (11, 24)], close=False)
    R.link(nv[-1], nv[3]); R.link(nv[9], nv[1]); R.link(nv[10], nv[1])
    a, b, c = R.navpt(8, 2.0), R.navpt(24, 2.0), R.navpt(8, 30.0)
    R.link(a, nv[11]); R.link(b, nv[8]); R.link(c, nv[13])
    secret(R, CAVE[0], CAVE[1], 0.0, 'The Snow Cave',
           'Inside the drift it is blue and quiet and nearly warm. Someone dug this out with their hands, lined it with books, and left a candle burning.')
    return finish(R, 'The Snow Stacks', weight=4, probe=(16, 16, 2.2),
                  blurb='Snow is falling between the stacks. It drifts against the shelves and does not melt, and at the end of the long aisle a fire is burning for nobody.')


def pointed_ring(c, w, jamb, rise, t=0.3):
    """A rib under the pointed vault: the band between the vault profile and one t smaller."""
    a = pointed_profile(c, w, 0, jamb, rise, 10)
    b = pointed_profile(c, w - 2 * t, 0, jamb, rise - t, 10)
    return a[2:-1] + list(reversed(b[2:-1]))


def wall_cases(R):
    for (a, b) in ((0.6, 5.6), (10.4, 21.6), (26.4, D - 0.6)):
        if b > 30 and True:
            pass
        sh(R, '+x', T, a, b, rows=ROWS, frame='walnut')
        if a < 26: sh(R, '-x', W - T, a, b, rows=ROWS, frame='walnut')
    sh(R, '-y', D - T, 0.6, 5.6, rows=ROWS, frame='walnut')
    sh(R, '-y', D - T, 10.4, 13.0, rows=ROWS, frame='walnut')
    sh(R, '-y', D - T, 19.0, 21.6, rows=ROWS, frame='walnut')


def fireplace(R):
    """A great stone chimneypiece at the end of the avenue, the fire lit."""
    y0, y1 = D - T - 1.1, D - T
    x0, x1 = 13.9, 18.1
    R.parts.add(box(x0, y0, 0, x0 + 0.7, y1, 2.4, 'tile', skip=('-z',)))       # jambs
    R.parts.add(box(x1 - 0.7, y0, 0, x1, y1, 2.4, 'tile', skip=('-z',)))
    R.parts.add(box(x0 - 0.15, y0 - 0.1, 2.4, x1 + 0.15, y1, 2.9, 'tile'))     # lintel and mantel
    R.parts.add(box(x0 - 0.3, y0 - 0.3, 2.9, x1 + 0.3, y1, 3.05, 'tile'))
    R.parts.add(box(x0 + 0.3, y0 + 0.4, 3.05, x1 - 0.3, y1, 4.1, 'tile'))      # the breast, up to the window sill
    R.parts.add(box(x0 + 0.7, y1 - 0.12, 0, x1 - 0.7, y1, 2.4, 'black'))       # the back of the firebox
    R.parts.add(box(x0 - 0.5, y0 - 0.9, 0, x1 + 0.5, y0, 0.08, 'slate'))       # hearth stone
    # logs and fire
    for (a, b, z) in ((14.9, 17.1, 0.1), (15.1, 16.9, 0.28)):
        R.parts.add(obox(a, y1 - 0.55, b, y1 - 0.55, z, z + 0.18, 0.18, 'walnut'))
    R.parts.add(box(14.8, y1 - 0.9, 0.0, 17.2, y1 - 0.2, 0.1, 'iron'))
    for (x, h, r) in ((15.4, 0.7, 0.16), (16.0, 1.0, 0.22), (16.6, 0.8, 0.17), (15.75, 0.55, 0.12), (16.3, 0.6, 0.13)):
        R.light(cyl(x, y1 - 0.55, 0.3, 0.3 + h * 0.3, r, 8, side='e_candle', top='e_candle', bottom='e_candle'))
        R.light(cyl(x, y1 - 0.55, 0.3 + h * 0.3, 0.3 + h, r * 0.45, 6, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # two armchairs drawn up to it, and candlesticks on the mantel
    armchair(R, 14.3, 28.6, math.pi / 2 - 0.35)
    armchair(R, 17.7, 28.6, math.pi / 2 + 0.35)
    for x in (13.7, 18.3):
        candle(R, x, y0 - 0.12, 3.05, h=0.3, stand=0.2)


def drifts(R):
    """Smooth walkable drifts: heaped against each stack end on the avenues, low ridges along the
    aisles, and one great drift in the north-east corner."""
    ends = []
    for (y, a, b) in stacks():
        for x in (a, b):
            if any(abs(x - v) < 0.4 for v in (AV0, AV1, 9.7, 6.3, 22.3, 25.7)):
                ends.append((x, y, 0.9 + 0.35 * math.sin(x * 1.3 + y * 0.7)))
    lines = [(a, y, b, y) for (y, a, b) in stacks()]
    mx, my, rx, ry, mh = MOUND

    def fn(x, y):
        z = -0.05
        for (ex, ey, h) in ends:
            d = math.hypot((x - ex) / 1.9, (y - ey) / 1.3)
            if d < 1: z = max(z, h * smooth_bump(d, 1.0))
        for (ax, ay, bx, by) in lines:
            d = dist_seg(x, y, ax, ay, bx, by)
            if d < 1.1: z = max(z, 0.32 * smooth_bump(d, 1.1) + 0.05 * math.sin(x * 2.1))
        d = math.hypot((x - mx) / rx, (y - my) / ry)
        if d < 1: z = max(z, mh * smooth_bump(d, 1.0) + 0.15 * math.sin(x * 1.7 + y))
        # drifts along the walls, under the windows
        for wd in (y - T, D - T - y, x - T, W - T - x):
            if wd < 0.9: z = max(z, 0.4 * smooth_bump(wd, 0.9))
        # keep the doorways clear, fading the snow out round them
        for (cx, cy) in ((8, 0), (24, 0), (8, D), (24, D), (0, 8), (0, 24), (W, 8), (W, 24)):
            f = max(0.0, min(1.0, (max(abs(x - cx), abs(y - cy)) - 2.4) / 1.4))
            z = -0.05 + (z + 0.05) * f
        return z
    R._drift = fn
    # the grid is laid so the tunnel's sides fall on its lines (0.25 m)
    st = 0.3125
    g0 = TX0 - 88 * st
    ym = g0 + st * math.ceil((TY0 - 0.4 - g0) / st)
    while fn((TX0 + TX1) / 2, ym) < 1.4 or min(fn(TX0, ym), fn(TX1, ym)) < 1.3: ym += st
    R._mouth = ym
    skip = lambda x, y: TX0 < x < TX1 and y < ym
    R.parts.add(field(fn, g0, g0, g0 + 101 * st, g0 + 101 * st, 101, 101, m='bed', skip=skip))


TX0, TX1, TY0, TY1 = 27.95, 29.2, 25.2, 27.95     # the tunnel into the cave (along +y)



def snow_cave(R):
    cx, cy = CAVE
    # the cave: an inward-facing dome under the great drift
    g = ellipsoid(cx, cy, 0.0, 1.9, 1.9, 1.75, 'bed', 28, 8, lower=False)
    g.f = g.f[:-1]; g.m = g.m[:-1]; g.uv = g.uv[:-1]           # no floor disc
    keep = []                                                  # and a hole where the tunnel comes in
    for i, f in enumerate(g.f):
        c = [sum(g.v[v][k] for v in f) / len(f) for k in range(3)]
        if TX0 - 0.1 < c[0] < TX1 + 0.1 and c[1] < TY1 + 0.3 and c[2] < 1.35: continue
        keep.append(i)
    g.f = [g.f[i] for i in keep]; g.m = [g.m[i] for i in keep]; g.uv = [g.uv[i] for i in keep]
    g.f = [tuple(reversed(f)) for f in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    R.parts.add(g)
    # the tunnel: a crawl, 1.25 m high, walls and roof facing in
    h = 1.25
    fn = R._drift
    ym = R._mouth
    # close the gap over the mouth, between the tunnel's roof and the drift
    n = 5
    for k in range(n):
        xa, xb = TX0 + (TX1 - TX0) * k / n, TX0 + (TX1 - TX0) * (k + 1) / n
        gg = Geo(); q = [gg.vert(p) for p in ((xa, ym, h), (xb, ym, h), (xb, ym, fn(xb, ym)), (xa, ym, fn(xa, ym)))]
        gg.face(q, 'bed', [(xa, h), (xb, h), (xb, 2), (xa, 2)])
        R.parts.add(gg)
    t = box(TX0, ym, 0, TX1, TY1 + 0.3, h, 'bed', skip=('-z', '-y', '+y'))
    t.f = [tuple(reversed(f)) for f in t.f]; t.uv = [list(reversed(u)) for u in t.uv]
    R.parts.add(t)
    # the trench walls where the tunnel runs out of the drift, following the snow down
    for x in (TX0, TX1):
        ya = ym
        while ya > 1.0:
            yb = ya; ya = yb - 0.3125
            za, zb = max(0.0, fn(x, ya)), max(0.0, fn(x, yb))
            if za < 0.02 and zb < 0.02: continue
            gg = Geo(); q = [gg.vert(p) for p in ((x, ya, 0), (x, yb, 0), (x, yb, zb), (x, ya, za))]
            gg.face(q if x == TX0 else q[::-1], 'bed', [(ya, 0), (yb, 0), (yb, zb), (ya, za)])
            R.parts.add(gg)
    # inside: books stacked into a bench and a wall, a candle, a blanket
    for k in range(5):
        a = math.pi * (0.15 + 0.7 * k / 4) + math.pi / 2
        book_pile(R, cx + math.cos(a) * 1.35, cy + math.sin(a) * 1.35, 0.0, 9, seed=20 + k)
    R.parts.add(box(cx + 0.3, cy - 0.3, 0, cx + 1.3, cy + 0.9, 0.35, 'leather'))
    R.parts.add(box(cx + 0.35, cy - 0.25, 0.35, cx + 1.25, cy + 0.85, 0.4, 'velvet'))
    R.spot('sit', cx + 0.8, cy + 0.3, 0.4, math.pi)
    R.parts.add(box(cx - 0.35, cy + 0.2, 0, cx - 0.05, cy + 0.5, 0.3, 'walnut'))
    candle(R, cx - 0.2, cy + 0.35, 0.3, h=0.18)
    open_book(R, cx + 0.8, cy - 0.05, 0.4, 0.4)
    R.light(sphere(cx - 0.2, cy + 0.35, 0.62, 0.05, 6, 3, 'e_candle'))
    a, b = R.navpt((TX0 + TX1) / 2, TY0 - 1.2), R.navpt((TX0 + TX1) / 2, TY1 - 0.4)
    R.link(a, b)
