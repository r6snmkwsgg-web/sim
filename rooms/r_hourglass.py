"""The Hourglass: a hall two floors tall with an hourglass the size of a church in the middle, its
glass a cage of brass ribs, and instead of sand, books. From the gallery a bridge goes in through the
side of the upper bulb onto the slope of books pouring toward the neck; drop through the neck and you
land on the heap in the lower bulb. One panel of the plinth is not stone."""
from kit_h6 import *
from kit_f import flight_thin

W = D = 32.0
CX = CY = 16.0
GW = 3.0                      # gallery width
GZ = LH                       # gallery floor
PZ = 1.6                      # plinth top (the lower bulb's floor)
PR = 6.8                      # plinth radius (octagon)
PI_ = 4.2                     # plinth ring inner radius (the chamber inside)
CZ = -1.5                     # the chamber floor
UP = [(0.9, 8.4), (1.6, 8.9), (3.2, 9.7), (4.6, 10.5), (5.3, 11.4), (5.5, 12.3), (5.2, 13.3), (4.6, 14.2)]
LO = [(r, 16.0 - z) for (r, z) in UP]       # the lower bulb mirrors the upper about z = 8
CRZ0, CRR0 = 8.45, 0.9        # the crater of books in the upper bulb: from the neck ...
CRZ1, CRR1 = 11.4, 5.3        # ... to where it meets the glass
HEAP = 6.3                    # the heap in the lower bulb
TOPZ = 14.3                   # the cap


def make():
    R = Room('hourglass', 2, 2, levels=2, res=2048, lo=-2.2)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, T - 0.02, GZ, W - T + 0.02, D - T + 0.02, R.hi - 0.1, 'tile', bottom='floor', top='plaster'))
    R.cut(box(GW + T, GW + T, TOP - 0.2, W - GW - T, D - GW - T, GZ + 0.1, 'tile', bottom='terrazzo'))
    rs = rng(44)
    galleries(R)
    stair_up(R)
    bridge(R)
    plinth(R, rs)
    glass(R, rs)
    books(R, rs)
    chamber(R, rs)
    hall(R, rs)
    fx(R, 'dust', [CX - 6, CY - 6, 1.6, CX + 6, CY + 6, 15.0])
    fx(R, 'dust', [T, T, 0.3, W - T, D - T, 15.0])
    g = navloop(R, [(1.8, 1.8), (16.0, 1.8), (30.2, 1.8), (30.2, 16.0), (30.2, 30.2), (16.0, 30.2), (1.8, 30.2), (1.8, 16.0)])
    m = navloop(R, [(8.2, 8.2), (16.0, 7.6), (23.8, 8.2), (24.4, 16.0), (23.8, 23.8), (16.0, 26.0), (8.2, 23.8), (7.6, 16.0)])
    for k in range(0, 8, 2): R.link(g[k], m[k])
    navloop(R, [(1.8, 1.8), (16.0, 1.8), (30.2, 1.8), (30.2, 16.0), (30.2, 30.2), (16.0, 30.2), (1.8, 30.2), (1.8, 16.0)], z=GZ)
    return finish(R, 'The Hourglass', weight=3, probe=(16, 5.0, 3.0), top=R.hi,
                  blurb='An hourglass the size of a chapel, and running. It is not sand in it. The books pour through the neck one at a time and the heap below never grows.')


def galleries(R):
    g0, g1 = GW + T, W - GW - T
    lz = GZ
    for (x0, y0, x1, y1) in ((g0 - 0.2, g0 - 0.2, g1 + 0.2, g0), (g0 - 0.2, g1, g1 + 0.2, g1 + 0.2),
                             (g0 - 0.2, g0, g0, 16.0 - 0.9), (g0 - 0.2, 16.0 + 0.9, g0, g1),
                             (g1, g0, g1 + 0.2, 16.0 - 1.2), (g1, 16.0 + 1.2, g1 + 0.2, g1)):
        R.parts.add(box(x0, y0, lz, x1, y1, lz + 1.0, 'tile', skip=('-z',)))
        R.parts.add(box(x0 - 0.03, y0 - 0.03, lz + 1.0, x1 + 0.03, y1 + 0.03, lz + 1.06, 'brass'))
    for k in range(9):
        p = g0 + (g1 - g0) * k / 8
        for (x, y) in ((p, g0), (p, g1), (g0, p), (g1, p)):
            R.parts.add(box(x - 0.25, y - 0.25, TOP - 1.2, x + 0.25, y + 0.25, TOP - 0.2, 'tile'))
    for (a, b) in ((0.7, 6.3), (9.7, 22.3), (25.7, D - 0.7)):
        sh(R, '+x', T, a, b, z=GZ, rows=9, frame='walnut')
        sh(R, '-x', W - T, a, b, z=GZ, rows=9, frame='walnut')
        sh(R, '+y', T, a, b, z=GZ, rows=9, frame='walnut')
        sh(R, '-y', D - T, a, b, z=GZ, rows=9, frame='walnut')
        sh(R, '+x', T, a, b, rows=12, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=12, frame='walnut')
        sh(R, '+y', T, a, b, rows=12, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=12, frame='walnut')
    # windows high in the walls, an oculus over the hourglass
    for c in (8.0, 16.0, 24.0):
        for s_ in 'NSEW':
            window(R, s_, c, GZ + 4.4, 1.4, 1.6, em='e_sky', mull=1, trans=1)
    R.cut(cyl(CX, CY, R.hi - 0.6, R.hi - 0.05, 2.6, 32, side='plaster', top='plaster', bottom='plaster'))
    R.light(cyl(CX, CY, R.hi - 0.1, R.hi - 0.08, 2.6, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    R.nocol.add(ring(CX, CY, R.hi - 0.35, R.hi - 0.1, 2.6, 3.0, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))


def stair_up(R):
    """A long flight up the east side to the gallery, landing in a gap in the east balustrade."""
    n, rise, run, w = 40, GZ / 40, 0.3, 2.0
    g1 = W - GW - T
    x0 = g1 - w - 0.05
    ytop = 16.0 - 1.2
    y0 = ytop - n * run
    flight_thin(R, x0, y0, 0.0, w, n, rise, run, '+y', m='terrazzo', riser='tile', side='tile', under='plaster')
    R.parts.add(box(x0, ytop, TOP - 0.25, g1 + 0.02, 16.0 + 1.2, GZ, 'terrazzo', sides='tile', bottom='plaster'))
    stair_rail(R, x0 + 0.05, y0 + run, rise, x0 + 0.05, ytop, GZ)
    stair_rail(R, x0 + w - 0.05, y0 + run, rise, x0 + w - 0.05, ytop, GZ)
    rail(R, x0 + 0.05, ytop, x0 + 0.05, 16.0 + 1.2, GZ)
    rail(R, x0 + 0.05, 16.0 + 1.2 - 0.05, g1, 16.0 + 1.2 - 0.05, GZ)


BZ = CRZ1                     # the bridge deck
BX0 = GW + T                  # from the west gallery edge
NB = int(round((BZ - GZ) / 0.2))
BX1 = BX0 + NB * 0.3          # top of its flight
BX2 = CX - CRR1 + 0.35        # its end, inside the bulb


def bridge(R):
    """From the west gallery a railed flight climbs to a bridge that goes in through the upper bulb."""
    w, y0 = 1.6, 16.0 - 0.8
    R.flight(BX0, y0, GZ, w, NB, (BZ - GZ) / NB, 0.3, '+x', m='oak', riser='walnut', side='walnut')
    R.nocol.add(slope_box(BX0, BX1, y0, y0 + w, GZ - 0.35, BZ - 0.35, GZ, BZ, 'walnut'))
    R.parts.add(box(BX1, y0, BZ - 0.3, BX2, y0 + w, BZ, 'oak', sides='walnut', bottom='walnut'))
    for y in (y0 + 0.04, y0 + w - 0.04):
        stair_rail(R, BX0 + 0.3, y, GZ + 0.2, BX1, y, BZ)
        rail(R, BX1, y, CX - 5.1, y, BZ)
    # iron hangers from the ceiling
    for x in (BX1 - 1.5, BX1 + 0.6):
        for y in (y0 + 0.02, y0 + w - 0.02):
            R.nocol.add(box(x - 0.02, y - 0.02, BZ - 0.3 if x > BX1 else GZ + (x - BX0) / 0.3 * 0.2 - 0.35, x + 0.02, y + 0.02, R.hi - 0.1, 'iron'))


def octagon(r, cx=CX, cy=CY, a0=math.pi / 8):
    return [(cx + r * math.cos(a0 + k * math.pi / 4), cy + r * math.sin(a0 + k * math.pi / 4)) for k in range(8)]


def clip(poly, nx, ny, c):
    """Keep the part of a convex polygon where nx*x + ny*y <= c."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        dp, dq = nx * p[0] + ny * p[1] - c, nx * q[0] + ny * q[1] - c
        if dp <= 0: out.append(p)
        if (dp < 0) != (dq < 0) and abs(dp - dq) > 1e-9:
            t = dp / (dp - dq); out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def plinth(R, rs):
    """An octagonal stone plinth, hollow: a ring of stone round the chamber, roofed by the lower bulb's
    floor; a slot through the ring on the south side behind a false panel; steps up on the north."""
    outer = octagon(PR)
    sx0, sx1 = CX - 0.55, CX + 0.55                     # the slot
    # the ring: outer octagon minus inner octagon, in convex pieces (8 trapezoids), the south one split by the slot
    inner = octagon(PI_ / math.cos(math.pi / 8))
    for k in range(8):
        a, b = outer[k], outer[(k + 1) % 8]
        c, d = inner[(k + 1) % 8], inner[k]
        piece = [a, b, c, d]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if mid[1] < CY - 3 and abs(mid[0] - CX) < 1.0:
            for (nx, cc) in ((1, sx0), (-1, -sx1)):
                pp = clip(piece, nx, 0, cc)
                if len(pp) >= 3: R.parts.add(poly_prism(pp, 0, PZ - 0.3, side='tile', top='tile', bottom='tile'))
        else:
            R.parts.add(poly_prism(piece, 0, PZ - 0.3, side='tile', top='tile', bottom='tile'))
    # the roof: the lower bulb's floor, marble, and a moulded rim
    R.parts.add(poly_prism(outer, PZ - 0.3, PZ, side='tile', top='terrazzo', bottom='plaster'))
    R.nocol.add(poly_prism(octagon(PR + 0.08), PZ - 0.12, PZ + 0.02, side='gilt', top='gilt', bottom='gilt'))
    # panels on the plinth's faces; the south one is the false one
    for k in range(8):
        a, b = outer[k], outer[(k + 1) % 8]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        ang = math.atan2(mid[1] - CY, mid[0] - CX)
        L = math.dist(a, b) * 0.6
        ux, uy = -math.sin(ang), math.cos(ang)
        px, py = mid[0] + math.cos(ang) * 0.03, mid[1] + math.sin(ang) * 0.03
        R.nocol.add(obox(px - ux * L / 2, py - uy * L / 2, px + ux * L / 2, py + uy * L / 2, 0.25, 1.15, 0.05, 'tile'))
        R.nocol.add(obox(px - ux * L / 2, py - uy * L / 2, px + ux * L / 2, py + uy * L / 2, 0.25, 0.3, 0.08, 'gilt'))
        R.nocol.add(obox(px - ux * L / 2, py - uy * L / 2, px + ux * L / 2, py + uy * L / 2, 1.1, 1.15, 0.08, 'gilt'))
    # the false panel fills the slot's mouth (drawn only: you walk through it)
    ys = CY - PR * math.cos(math.pi / 8)
    R.nocol.add(box(sx0, ys - 0.02, 0, sx1, ys + 0.02, PZ - 0.3, 'tile'))
    # steps up on the north side, a balustrade round the terrace with a gap for them
    n, rise, run = 8, PZ / 8, 0.3
    yt = CY + PR * math.cos(math.pi / 8)
    R.flight(CX - 1.0, yt + n * run, 0, 2.0, n, rise, run, '-y', m='terrazzo', riser='tile', side='tile')
    ob = octagon(PR - 0.12)
    for k in range(8):
        a, b = ob[k], ob[(k + 1) % 8]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if mid[1] > CY + 3 and abs(mid[0] - CX) < 1.0:
            # split round the stair
            xa, xb = min(a[0], b[0]), max(a[0], b[0])
            yy = a[1]
            rail(R, xa, yy, CX - 1.05, yy, PZ, solid=True, m='brass', mat='tile')
            rail(R, CX + 1.05, yy, xb, yy, PZ, solid=True, m='brass', mat='tile')
        else:
            rail(R, a[0], a[1], b[0], b[1], PZ, solid=True, m='brass', mat='tile')
    for s_ in (-1, 1):
        stair_rail(R, CX + s_ * 0.95, yt + n * run - 0.3, rise, CX + s_ * 0.95, yt, PZ)


def profile_pts(prof, a):
    return [(CX + r * math.cos(a), CY + r * math.sin(a), z) for (r, z) in prof]


def glass(R, rs):
    """The two bulbs as a cage of brass ribs and hoops (the library has no glass), a brass collar at
    the neck, turned oak pillars, a cap; invisible walls where the glass would stop you."""
    nrib = 28
    door_up = math.pi            # where the bridge comes in (west)
    door_lo = math.pi / 2        # the lower bulb's doorway (north)
    for k in range(nrib):
        a = 2 * math.pi * k / nrib
        for (prof, door, zlo, zhi) in ((UP, door_up, CRZ1 - 0.1, CRZ1 + 2.3), (LO, door_lo, PZ - 0.1, PZ + 2.3)):
            pts = profile_pts(prof, a)
            if abs(math.remainder(a - door, 2 * math.pi)) < 0.2:
                pts = [p for p in pts if not (zlo < p[2] < zhi)]
                # split into runs above and below the doorway
                lo_ = [p for p in pts if p[2] <= zlo]; hi_ = [p for p in pts if p[2] >= zhi]
                for run in (lo_, hi_):
                    if len(run) >= 2: R.nocol.add(tube(run, 0.035, 5, 'brass', caps=True))
                continue
            R.nocol.add(tube(pts, 0.035, 5, 'brass', caps=True))
    # hoops
    for (prof, zs) in ((UP, (8.9, 9.7, 10.5, 13.3, 14.2)), (LO, (7.1, 6.3, 5.5, 3.7, 2.7))):
        for z in zs:
            r = interp(prof, z)
            R.nocol.add(ring(CX, CY, z - 0.04, z + 0.04, r - 0.03, r + 0.05, 40, top='brass', bottom='brass', inner='brass', outer='brass'))
    # collar at the neck, the cap and base rims
    R.nocol.add(ring(CX, CY, 7.55, 8.45, 0.92, 1.25, 24, top='gilt', bottom='gilt', inner='brass', outer='gilt'))
    R.nocol.add(cyl(CX, CY, TOPZ, TOPZ + 0.5, 5.3, 40, side='walnut', top='walnut', bottom='walnut'))
    R.nocol.add(cyl(CX, CY, TOPZ + 0.5, TOPZ + 0.62, 5.5, 40, side='gilt', top='gilt', bottom='gilt'))
    R.nocol.add(ring(CX, CY, PZ, PZ + 0.18, 4.4, 4.8, 40, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    R.col.add(cyl(CX, CY, TOPZ, TOPZ + 0.6, 5.5, 20, side='tile', top='tile', bottom='tile'))
    # pillars: turned oak, four of them
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        x, y = CX + 6.2 * math.cos(a), CY + 6.2 * math.sin(a)
        R.parts.add(cyl(x, y, PZ, TOPZ + 0.5, 0.26, 16, side='walnut', top='walnut', bottom='walnut'))
        for z in (PZ + 0.3, 5.0, 8.0, 11.0, TOPZ - 0.3):
            R.nocol.add(sphere(x, y, z, 0.42, 14, 7, 'walnut'))
            R.nocol.add(ring(x, y, z - 0.5, z - 0.42, 0.26, 0.36, 16, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
        R.parts.add(cyl(x, y, PZ, PZ + 0.5, 0.45, 16, side='walnut', top='walnut'))
    # invisible walls: the upper bulb above the crater, the lower bulb round its floor
    col_ring(R, CRR1 - 0.1, CRZ1 - 0.3, TOPZ, door_up, 0.056)
    col_ring(R, interp(LO, PZ) - 0.1, PZ, 4.2, door_lo, 0.2)
    for z0, z1 in ((4.2, 7.4),):
        col_ring(R, 4.6, z0, z1, None, 0)


def interp(prof, z):
    pts = sorted(prof, key=lambda p: p[1])
    for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
        if z0 <= z <= z1: return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return pts[0][0] if z < pts[0][1] else pts[-1][0]


def col_ring(R, r, z0, z1, gap_a, gap_w, n=32):
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        if gap_a is not None and abs(math.remainder((a0 + a1) / 2 - gap_a, 2 * math.pi)) < gap_w + math.pi / n: continue
        R.col.add(obox(CX + r * math.cos(a0), CY + r * math.sin(a0), CX + r * math.cos(a1), CY + r * math.sin(a1), z0, z1, 0.08, 'tile'))


def book_geo(rs, s=1.0, pages=True):
    w, l, t = rs.uniform(0.15, 0.24) * s, rs.uniform(0.22, 0.32) * s, rs.uniform(0.04, 0.08) * s
    g = box(-l / 2, -w / 2, 0, l / 2, w / 2, t, rs.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet', 'damask', 'bronze')), skip=('-z',))
    if pages: g.add(box(-l / 2 + 0.01, -w / 2 - 0.003, 0.006, l / 2 - 0.01, w / 2 - 0.015, t - 0.006, 'ivory', skip=('-y', '-z', '+z')))
    return g


def books(R, rs):
    """The books: a crater of them in the upper bulb running down to the neck, a stream falling
    through it, a heap in the lower bulb."""
    # the crater surface, walkable, and its underside
    n = 36
    rings_ = [(CRR0 + (CRR1 - CRR0) * i / 6, CRZ0 + (CRZ1 - CRZ0) * i / 6) for i in range(7)]
    g = Geo(); gu = Geo()
    for i in range(len(rings_) - 1):
        (r0, z0), (r1, z1) = rings_[i], rings_[i + 1]
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            P = [(CX + r0 * math.cos(a0), CY + r0 * math.sin(a0), z0), (CX + r0 * math.cos(a1), CY + r0 * math.sin(a1), z0),
                 (CX + r1 * math.cos(a1), CY + r1 * math.sin(a1), z1), (CX + r1 * math.cos(a0), CY + r1 * math.sin(a0), z1)]
            ids = [g.vert(p) for p in P]; g.face(list(reversed(ids)), 'leather', [(p[0], p[1]) for p in reversed(P)])
            idu = [gu.vert((p[0], p[1], p[2] - 0.15)) for p in P]; gu.face(idu, 'brass', [(p[0], p[1]) for p in P])
    R.parts.add(g); R.nocol.add(gu)
    # books lying all over it
    for _ in range(900):
        r = CRR0 + 0.15 + (CRR1 - CRR0 - 0.2) * math.sqrt(rs.random())
        a = rs.uniform(0, 2 * math.pi)
        z = CRZ0 + (r - CRR0) / (CRR1 - CRR0) * (CRZ1 - CRZ0)
        b = book_geo(rs, 1.35, rs.random() < 0.5)
        rot(b, 'y', math.atan((CRZ1 - CRZ0) / (CRR1 - CRR0)) * rs.uniform(0.6, 1.1))
        b.xform(a + rs.uniform(-0.4, 0.4), 0, 0, 0)
        R.nocol.add(b.xform(0, CX + r * math.cos(a), CY + r * math.sin(a), z))
    # the stream through the neck
    for k in range(26):
        z = HEAP + 0.2 + (8.6 - HEAP) * k / 26
        b = book_geo(rs)
        rot(b, 'x', rs.uniform(-1.4, 1.4)); rot(b, 'y', rs.uniform(-1.4, 1.4))
        R.nocol.add(b.xform(rs.uniform(0, 6.28), CX + rs.uniform(-0.3, 0.3), CY + rs.uniform(-0.3, 0.3), z))
    # the heap in the lower bulb
    hr = 3.8
    R.parts.add(cone(CX, CY, PZ, HEAP, hr, 0.25, 32, side='leather', top='leather', bottom='leather'))
    for _ in range(620):
        r = hr * math.sqrt(rs.random()) * 0.98
        a = rs.uniform(0, 2 * math.pi)
        z = PZ + (HEAP - PZ) * (1 - (r - 0.25) / (hr - 0.25)) if r > 0.25 else HEAP
        b = book_geo(rs, 1.35, rs.random() < 0.5)
        rot(b, 'y', -math.atan((HEAP - PZ) / hr) * rs.uniform(0.5, 1.0))
        b.xform(a + rs.uniform(-0.5, 0.5), 0, 0, 0)
        R.nocol.add(b.xform(0, CX + r * math.cos(a), CY + r * math.sin(a), z))
    # a few that bounced out onto the terrace
    for _ in range(18):
        a = rs.uniform(0, 2 * math.pi); r = rs.uniform(3.9, 4.3)
        R.nocol.add(book_geo(rs).xform(rs.uniform(0, 6.28), CX + r * math.cos(a), CY + r * math.sin(a), PZ))
    # light inside the bulbs
    R.light(sphere(CX, CY, 13.4, 0.25, 12, 6, 'e_lamp'))
    R.nocol.add(cyl(CX, CY, 13.6, TOPZ, 0.02, 6, side='brass', caps=False))
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        R.light(sphere(CX + 4.0 * math.cos(a), CY + 4.0 * math.sin(a), PZ + 3.4, 0.14, 10, 5, 'e_amber'))
        R.nocol.add(cyl(CX + 4.0 * math.cos(a), CY + 4.0 * math.sin(a), PZ + 3.5, 7.4, 0.012, 4, side='brass', caps=False))


def chamber(R, rs):
    """Inside the plinth: through the slot, down a short stair, the chamber under the hourglass where the
    mechanism for turning it is kept. It has never been used."""
    R.cut(cyl(CX, CY, CZ, 0.02, PI_ - 0.2, 24, side='tile', top='tile', bottom='slate'))
    sx0, sx1 = CX - 0.55, CX + 0.55
    ys = CY - PR * math.cos(math.pi / 8)
    n, rise, run = 8, -CZ / 8, 0.3
    ytop = CY - PI_ + 0.1
    foot = ytop + n * run
    R.cut(box(sx0, ytop - 0.05, CZ, sx1, foot + 0.05, 0.02, 'tile', bottom='slate', top='tile'))
    R.flight(sx0, foot, CZ, sx1 - sx0, n, rise, run, '-y', m='oak', riser='walnut', side='tile')
    # the crank: a great wheel on an iron shaft that would turn the glass over, chained up
    R.nocol.add(wheel(CX + 2.4, CY + 1.2, CZ + 1.3, 1.1, axis='x', spokes=6, rim=0.08, w=0.1, m='iron', hub='brass'))
    R.parts.add(box(CX + 2.3, CY + 0.9, CZ, CX + 2.5, CY + 1.5, CZ + 1.3, 'iron'))
    R.nocol.add(cyl(CX + 2.4, CY + 1.2, CZ + 1.3, PZ - 0.3, 0.12, 10, side='iron', caps=False))
    for k in range(6):
        R.nocol.add(box(CX + 2.35, CY + 0.2 + k * 0.1, CZ + 0.4 + k * 0.15, CX + 2.45, CY + 0.28 + k * 0.1, CZ + 0.5 + k * 0.15, 'brass'))
    # a cot, a stool, a lamp; tally marks on the wall; the log
    R.parts.add(box(CX - 3.0, CY - 0.8, CZ, CX - 1.4, CY + 0.2, CZ + 0.4, 'walnut', top='bed'))
    R.spot('bed', CX - 2.2, CY - 0.3, CZ + 0.4, 0.0)
    R.parts.add(table(CX - 1.0, CY + 1.6, CX + 0.6, CY + 2.4, 0.78, 'walnut').xform(0, 0, 0, CZ))
    R.parts.add(stool(CX - 0.2, CY + 1.1, math.pi / 2).xform(0, 0, 0, CZ))
    open_book(R, CX - 0.2, CY + 2.0, CZ + 0.78, 0.0)
    R.light(sphere(CX - 0.8, CY + 2.2, CZ + 1.0, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(cyl(CX - 0.8, CY + 2.2, CZ + 0.78, CZ + 0.95, 0.02, 6, side='brass', caps=False))
    bulb(R, CX + 0.8, CY - 0.5, CZ + 2.3, r=0.1, m='e_lamp', top=PZ - 0.3)
    bulb(R, CX - 1.8, CY + 1.4, CZ + 2.2, r=0.08, m='e_amber', top=PZ - 0.3)
    candles_on(R, CX - 0.9, CY + 1.7, CX + 0.5, CY + 2.3, CZ + 0.78, 5, rs, 0.1, 0.3)
    candles_on(R, CX - 2.6, CY + 2.4, CX - 1.6, CY + 3.0, CZ, 7, rs, 0.15, 0.5)
    for k in range(18):
        a = math.pi * 0.95 + k * 0.035
        x, y = CX + (PI_ - 0.21) * math.cos(a), CY + (PI_ - 0.21) * math.sin(a)
        stroke = box(-0.01, -0.01, 0, 0.01, 0.01, 0.4, 'slate')
        if k % 5 == 4: rot(stroke, 'y', 1.1, 0, 0, 0.2)
        R.nocol.add(stroke.xform(a, x, y, CZ + 1.1))
    R.spot('plaque', CX - 0.2, CY + 2.0, CZ + 0.78, math.pi / 2,
           text='WHEN THE LAST BOOK HAS FALLEN, TURN THE GLASS. It has been falling since before this was written. There are, by the count on the wall, a great many books left.')
    secret(R, CX, CY + 0.2, CZ, 'The Plinth',
           'One panel of the plinth is not stone. Behind it, under the hourglass, the chamber of the one whose job is to turn it over, when it runs out. It has not run out.')


def hall(R, rs):
    """The floor of the hall: reading tables round the hourglass, globes of light on standards."""
    for (x0, y0, x1, y1) in ((4.8, 9.6, 6.2, 13.4), (4.8, 18.6, 6.2, 22.4), (25.8, 18.6, 27.2, 22.4), (9.6, 26.0, 13.4, 27.4), (18.6, 26.0, 22.4, 27.4), (9.6, 4.6, 13.4, 6.0)):
        reading_table(R, x0, y0, x1, y1, lamps=2, chairs=True)
    for (x, y) in ((8.0, 8.0), (24.0, 8.0), (24.0, 24.0), (8.0, 24.0)):
        lamp_post(R, x + (0.9 if x < 16 else -0.9), y + (0.9 if y < 16 else -0.9), 0, 3.0, m='e_lamp')
    for (x, y) in ((2.0, 2.0), (30.0, 2.0), (30.0, 30.0), (2.0, 30.0)):
        R.light(sphere(x, y, 2.5, 0.09, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, y, 2.55, TOP - 0.2, 0.01, 4, side='iron', caps=False))
    for k in range(8):
        p = 4.0 + k * (24.0 / 7)
        for (x, y) in ((p, 1.6), (p, D - 1.6), (1.6, p), (W - 1.6, p)):
            R.light(sphere(x, y, GZ + 2.6, 0.09, 8, 4, 'e_lamp' if k % 2 else 'e_amber'))
