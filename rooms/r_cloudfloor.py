"""The Cloud Floor: the floor of this hall is cloud, lumpy and white and a little over knee deep, and
the bookcases ride on it like ships, hulls down in the vapour. A colonnade holds up nothing much;
past it, and overhead, there is only sky. In the middle, where the cloud is thickest, there is a gap,
and a steep stair goes down through it to a room under the weather."""
from kit_h3 import *

W = D = 32.0
EH = 6.0                                  # the entablature round the walls
SX0, SX1, SY0, SY1 = 13.6, 18.6, 14.2, 18.2   # the room under the cloud (floor at -1.9)
RZ = -1.9
STX0, STX1, STY0, STY1 = 10.9, 14.02, 15.4, 16.6   # the stair down (descending east)
SLAB = 0.8
# the ships: centre, heading, length
SHIPS = [(6.5, 16.0, 0.35, 6.0), (16.0, 6.0, 1.75, 6.5), (25.5, 15.5, -0.3, 6.0), (16.5, 26.0, 1.4, 6.0),
         (6.0, 4.8, 0.9, 4.2), (27.0, 27.0, 0.6, 4.2), (26.8, 4.6, -0.8, 4.0), (5.0, 27.2, -0.7, 4.0)]
PIERS = ((10.4, 10.4), (21.6, 10.4), (10.4, 21.6), (21.6, 21.6))
DOORS = ((8, 0), (24, 0), (8, D), (24, D), (0, 8), (0, 24), (W, 8), (W, 24))


def cloud(x, y):
    """The walkable top of the cloud."""
    z = 0.75 + 0.22 * math.sin(x * 0.9 + y * 0.35) * math.cos(y * 0.8 - x * 0.2) + 0.12 * math.sin(x * 2.3 + 1.0) * math.sin(y * 1.9)
    z += 0.35 * smooth_bump(math.hypot(x - 16, y - 16), 6.0)
    # thicker over the room below and the stair head, so the slab stays hidden
    if SX0 - 0.6 < x < SX1 + 0.6 and SY0 - 0.6 < y < SY1 + 0.6: z = max(z, 1.12)
    if STX0 - 1.4 < x < STX1 and STY0 - 0.8 < y < STY1 + 0.8: z = max(z, 1.02 if x < STX0 + 0.2 else 1.12)
    # dips down to the floor at every doorway, so you can walk in
    for (cx, cy) in DOORS:
        d = max(abs(x - cx), abs(y - cy))
        f = max(0.0, min(1.0, (d - 2.3) / 2.4))
        z = -0.05 + (z + 0.05) * f
    return z


def make():
    R = Room('cloudfloor', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP - 0.05, 'tile', bottom='terrazzo', top='plaster'))
    sky(R)
    colonnade(R)
    # the cloud: a walkable lumpy surface, with a gap over the stair
    gap = lambda x, y: STX0 - 0.05 < x < STX1 + 0.3 and STY0 - 0.05 < y < STY1 + 0.05
    R.parts.add(field(cloud, T, T, W - T, D - T, 64, 64, m='bed', skip=gap))
    puffs_over(R)
    for (x, y) in PIERS:
        great_pier(R, x, y)
    for k, s in enumerate(SHIPS):
        ship(R, *s, seed=k)
    under_room(R)
    fx(R, 'dust', [T, T, 0.5, W - T, D - T, 5.0])
    nv = navloop(R, [(8, 2.2), (13.0, 9.0), (19, 9.0), (24, 2.2), (29.8, 8), (24.0, 13.0), (29.8, 24), (24, 29.8), (19, 23.0), (13, 23.0), (8, 29.8), (2.2, 24), (8.0, 19.0), (2.2, 8)], z=0.0)
    for i in range(len(nv)):
        p = R.nav[nv[i]]; p[2] = max(0.0, cloud(p[0], p[1]))
    secret(R, 16.2, 16.2, RZ, 'The Room Under the Weather',
           'Under the cloud it is dim and dry and smells of rain that has not fallen yet. A bed, a lamp, a shelf of books about the sky, and the soft white ceiling pressing down.')
    return finish(R, 'The Cloud Floor', weight=4, probe=(16, 11.5, 2.6),
                  blurb='The floor is cloud. It holds you, mostly. The bookcases ride on it like boats at anchor, and the sky goes on past the columns for ever.')


def sky(R):
    """Sky overhead, and sky between the columns: painted, warm at the horizon, with a low sun."""
    R.light(box(T, T, TOP - 0.1, W - T, D - T, TOP - 0.08, 'e_skydome', skip=('+z',)))
    e = 0.012
    for side in 'SNWE':
        for (a, b) in ((T, 6.4), (9.6, 22.4), (25.6, W - T)):
            _panel(R, side, a, b, 0.0, EH, 'e_skydome', e)
        for c in (8.0, 24.0):
            _panel(R, side, c - 1.6, c + 1.6, 4.3, EH, 'e_skydome', e)
        for (a, b) in ((T, 6.4), (9.6, 22.4), (25.6, W - T)):
            _panel(R, side, a, b, 0.6, 2.0, 'e_sky', e * 2)            # the glow along the horizon
        _panel(R, side, T, W - T, EH + 0.6, TOP - 0.1, 'e_skydome', e)
    # the sun, low in the west, between the doorways
    g = Geo(); n = 20
    ids = [g.vert((T + 0.04, 16 + 1.3 * math.cos(2 * math.pi * k / n), 2.6 + 1.3 * math.sin(2 * math.pi * k / n))) for k in range(n)]
    g.face(ids, 'e_lamp', [(0, 0)] * n)
    R.light(g)


def _panel(R, side, a, b, z0, z1, m, e):
    if side == 'S': R.light(box(a, T, z0, b, T + e, z1, m, skip=('-y',)))
    elif side == 'N': R.light(box(a, D - T - e, z0, b, D - T, z1, m, skip=('+y',)))
    elif side == 'W': R.light(box(T, a, z0, T + e, b, z1, m, skip=('-x',)))
    else: R.light(box(W - T - e, a, z0, W - T, b, z1, m, skip=('+x',)))


def colonnade(R):
    """Round columns along the walls, flanking every doorway, carrying an entablature round the room."""
    cols = [T + 0.9, 5.6, 10.4, 13.6, 18.4, 21.6, 26.4, W - T - 0.9]
    for p in cols:
        for (x, y) in ((p, T + 0.9), (p, D - T - 0.9), (T + 0.9, p), (W - T - 0.9, p)):
            R.parts.add(cyl(x, y, 0, EH, 0.42, 20, side='tile', caps=False))
            R.parts.add(box(x - 0.6, y - 0.6, EH - 0.35, x + 0.6, y + 0.6, EH, 'tile'))
            R.parts.add(cyl(x, y, 0, 0.35, 0.58, 20, side='tile', top='tile'))
    for (x0, y0, x1, y1) in ((T, T + 0.3, W - T, T + 1.5), (T, D - T - 1.5, W - T, D - T - 0.3),
                             (T + 0.3, T + 1.5, T + 1.5, D - T - 1.5), (W - T - 1.5, T + 1.5, W - T - 0.3, D - T - 1.5)):
        R.parts.add(box(x0, y0, EH, x1, y1, EH + 0.6, 'tile', bottom='plaster'))
    for (x0, y0, x1, y1) in ((T, T + 0.2, W - T, T + 1.6), (T, D - T - 1.6, W - T, D - T - 0.2),
                             (T + 0.2, T + 1.6, T + 1.6, D - T - 1.6), (W - T - 1.6, T + 1.6, W - T - 0.2, D - T - 1.6)):
        R.parts.add(box(x0, y0, EH + 0.6, x1, y1, EH + 0.72, 'gilt'))


def puffs_over(R):
    """Soft puffs heaped on the cloud's surface (drawn, not collided: you wade through their tops)."""
    rnd = random.Random(7)
    g = Geo()
    n = 0
    while n < 70:
        x, y = rnd.uniform(1.5, W - 1.5), rnd.uniform(1.5, D - 1.5)
        if any(max(abs(x - cx), abs(y - cy)) < 3.2 for (cx, cy) in DOORS): continue
        if STX0 - 0.8 < x < STX1 + 0.8 and STY0 - 0.8 < y < STY1 + 0.8: continue
        z = cloud(x, y)
        r = rnd.uniform(0.7, 1.4)
        g.add(puffs(x, y, z - 0.15, r, 3, 'bed', seed=n, flat=0.62, segs=12, rings=5))
        n += 1
    # a rim of puffs round the gap, to hide its edges
    for k in range(10):
        a = 2 * math.pi * k / 10
        x = (STX0 + STX1) / 2 + math.cos(a) * 2.1; y = (STY0 + STY1) / 2 + math.sin(a) * 1.25
        g.add(puffs(x, y, cloud(x, y) - 0.15, 0.55, 2, 'bed', seed=100 + k, flat=0.5, segs=10, rings=4))
    R.nocol.add(g)


def great_pier(R, x, y):
    """A square pier wrapped in books to the sky, rising out of the cloud."""
    s = 1.1
    R.parts.add(box(x - s, y - s, 0, x + s, y + s, TOP - 0.05, 'tile'))
    R.parts.add(box(x - s - 0.15, y - s - 0.15, EH, x + s + 0.15, y + s + 0.15, EH + 0.5, 'tile'))
    for (dirn, bx, by, L) in (('+x', x + s, y + s - 0.1, 2 * s - 0.2), ('-x', x - s, y - s + 0.1, 2 * s - 0.2),
                              ('+y', x - s + 0.1, y + s, 2 * s - 0.2), ('-y', x + s - 0.1, y - s, 2 * s - 0.2)):
        shelf(R, bx, by, 0.9, L, dirn, rows=11, frame='walnut')


def ship(R, cx, cy, head, L, seed=0):
    """A double-sided bookcase on a boat's hull, floating in the cloud."""
    z0 = cloud(cx, cy) + 0.05
    c, s = math.cos(head), math.sin(head)
    rows = 5
    # hull: a prism along the ship, a rounded V in section, with pointed ends
    g = Geo()
    hw, hd = 0.75, 0.9
    prof = [(-hw, 0.0), (-hw * 0.8, -hd * 0.55), (-hw * 0.35, -hd * 0.9), (0.0, -hd), (hw * 0.35, -hd * 0.9), (hw * 0.8, -hd * 0.55), (hw, 0.0)]
    n = 7
    stations = [(-L / 2 - 0.9, 0.05), (-L / 2, 1.0), (L / 2, 1.0), (L / 2 + 0.9, 0.05)]
    rings_ = []
    for (u, k) in stations:
        rings_.append([g.vert((u, p * k, q * (0.4 + 0.6 * k))) for (p, q) in prof])
    for i in range(len(rings_) - 1):
        for j in range(n - 1):
            a, b, cc, d = rings_[i][j], rings_[i][j + 1], rings_[i + 1][j + 1], rings_[i + 1][j]
            g.face([a, d, cc, b], 'walnut', [(0, 0), (1, 0), (1, 1), (0, 1)])
    deck = [rings_[0][0]] + [rings_[i][n - 1] for i in range(4)] + [rings_[i][0] for i in (3, 2, 1)]
    g.face(deck, 'oak', [(g.v[v][0], g.v[v][1]) for v in deck])
    g.face([rings_[0][j] for j in range(n)], 'walnut', [(0, 0)] * n)
    g.face([rings_[3][j] for j in reversed(range(n))], 'walnut', [(0, 0)] * n)
    g.fix()
    g.xform(head, cx, cy, z0)
    R.parts.add(g)
    # a brass rail round the deck edge
    R.nocol.add(obox(cx - c * (L / 2 + 0.6), cy - s * (L / 2 + 0.6), cx + c * (L / 2 + 0.6), cy + s * (L / 2 + 0.6), z0 + 0.02, z0 + 0.06, 0.08, 'gilt'))
    # the bookcase on deck, both faces
    for side in (-1, 1):
        th = head + (math.pi / 2 if side > 0 else -math.pi / 2)
        ox, oy = cx + math.cos(th) * 0.01, cy + math.sin(th) * 0.01
        bx, by = ox - c * L / 2 * side, oy - s * L / 2 * side
        shelf(R, bx, by, z0, L, th, rows=rows, frame='walnut')
    top = z0 + rows * 0.42 + 0.15
    for t in (-0.35, 0.35):
        x, y = cx + c * L * t, cy + s * L * t
        R.parts.add(cyl(x, y, top, top + 0.03, 0.08, 12, side='brass', top='brass'))
        R.parts.add(cyl(x, y, top + 0.03, top + 0.36, 0.012, 6, side='brass', caps=False))
        R.parts.add(obox(x - c * 0.17, y - s * 0.17, x + c * 0.17, y + s * 0.17, top + 0.36, top + 0.44, 0.13, 'green'))
        R.light(obox(x - c * 0.15, y - s * 0.15, x + c * 0.15, y + s * 0.15, top + 0.345, top + 0.36, 0.09, 'e_lamp'))
    book_pile(R, cx, cy, top, 4, seed=seed)
    # a mast of a lamp standard at the bow
    bx, by = cx + c * (L / 2 + 0.4), cy + s * (L / 2 + 0.4)
    R.parts.add(cyl(bx, by, z0, z0 + 2.8, 0.04, 6, side='brass', caps=False))
    R.light(sphere(bx, by, z0 + 2.9, 0.13, 10, 5, 'e_amber'))


def under_room(R):
    """Below the cloud: a stair down through the gap, and a low room with a bed."""
    # the stairwell (cut down through the floor) and the room
    R.cut(box(STX0, STY0, RZ, STX1 + 0.02, STY1, 0.05, 'damask', bottom='oak', top='oak'))
    R.cut(box(SX0, SY0, RZ, SX1, SY1, 0.05, 'damask', bottom='floor', top='plaster'))
    n, rise, run = 12, (1.02 - RZ) / 12, 0.26
    R.flight(STX1, STY0, RZ, STY1 - STY0, n, rise, run, '-x', m='oak', riser='walnut', side='walnut')
    # walls of the stairwell and the room above the floor, and the room's ceiling (all under the cloud)
    R.parts.add(box(STX0 - 0.1, STY0 - 0.12, 0, STX1, STY0, 1.0, 'damask'))
    R.parts.add(box(STX0 - 0.1, STY1, 0, STX1, STY1 + 0.12, 1.0, 'damask'))
    R.parts.add(box(STX0 - 0.12, STY0 - 0.12, -0.3, STX0, STY1 + 0.12, 0.98, 'damask'))
    for (x0, y0, x1, y1) in ((SX0 - 0.12, SY0 - 0.12, SX1 + 0.12, SY0), (SX0 - 0.12, SY1, SX1 + 0.12, SY1 + 0.12), (SX1, SY0, SX1 + 0.12, SY1)):
        R.parts.add(box(x0, y0, 0, x1, y1, SLAB, 'damask'))
    for (y0, y1) in ((SY0 - 0.12, STY0), (STY1, SY1 + 0.12)):
        R.parts.add(box(SX0 - 0.12, y0, 0, SX0, y1, SLAB, 'damask'))
    R.parts.add(box(SX0 - 0.12, SY0 - 0.12, SLAB, SX1 + 0.12, SY1 + 0.12, SLAB + 0.12, 'plaster'))
    # furnishings
    sh(R, '-y', SY1, SX0 + 1.4, SX1 - 0.2, z=RZ, rows=6, frame='oak')
    sh(R, '-x', SX1, SY0 + 0.2, SY1 - 0.5, z=RZ, rows=6, frame='oak')
    R.parts.add(box(SX0 + 1.2, SY0 + 0.15, RZ, SX0 + 3.2, SY0 + 1.1, RZ + 0.45, 'bed'))
    R.parts.add(box(SX0 + 2.7, SY0 + 0.2, RZ + 0.45, SX0 + 3.15, SY0 + 1.05, RZ + 0.58, 'ivory'))
    R.spot('bed', SX0 + 2.2, SY0 + 0.62, RZ + 0.45, 0.0)
    R.parts.add(table(SX1 - 1.6, SY0 + 1.6, SX1 - 0.6, SY0 + 2.4, 0.74, 'walnut').xform(0, 0, 0, RZ))
    open_book(R, SX1 - 1.1, SY0 + 2.0, RZ + 0.74, 1.2)
    desk_lamp(R, SX1 - 0.8, SY0 + 2.2, RZ + 0.74)
    c = chair(SX1 - 1.1, SY0 + 1.2, math.pi / 2); c.xform(0, 0, 0, RZ); R.parts.add(c)
    R.spot('sit', SX1 - 1.1, SY0 + 1.2, RZ + 0.48, math.pi / 2)
    R.parts.add(box(SX0 + 0.8, SY0 + 1.5, RZ, SX0 + 3.8, SY1 - 1.0, RZ + 0.01, 'carpet'))
    bulb(R, 16.4, 16.4, SLAB - 0.55, r=0.14, m='e_lamp', top=SLAB)
    bulb(R, 12.4, 16.0, 0.3, r=0.1, m='e_amber', top=0.98)
    R.light(sphere(SX0 + 0.35, SY1 - 0.35, RZ + 1.1, 0.05, 6, 3, 'e_candle'))
    R.nocol.add(cyl(SX0 + 0.35, SY1 - 0.35, RZ, RZ + 1.05, 0.02, 6, side='brass', caps=False))
    a, b, c2 = R.navpt(STX0 - 0.6, 16.0, 1.02), R.navpt(STX1 + 0.4, 16.0, RZ), R.navpt(16.8, 16.6, RZ)
    R.link(a, b, c2)
