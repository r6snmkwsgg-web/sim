"""The Written Stair: a long stone stair between two floors of the library, in a deep slot of a stairwell,
and every surface of it, walls, treads, risers, written on by hand. Names, dates, sums, apologies, lists,
in a hundred inks, one over another. Half way up there is a landing, and on the landing a slot in the
wall, and behind the slot the one room nobody has written in, where somebody left the first pen."""
from kit_h10 import *

W = D = 32.0
CX0, CX1 = 13.8, 18.2               # the stair's width inside the stairwell
WX0, WX1 = 12.5, 19.5               # the stairwell's outer walls
Y0 = 6.0                            # the foot of the stair
N1, RISE, RUN = 20, 0.2, 0.3        # two flights of 20
LY0 = Y0 + N1 * RUN                 # the half landing (z 4)
LY1 = LY0 + 2.0
TY = LY1 + N1 * RUN                 # the top of the stair (z 8)
TY1 = TY + 2.0                      # the end of the top landing
ZL = N1 * RISE                      # the landing's height (4.0)
UZ = LH                             # the upper floor
BX0, BX1, BY0, BY1 = 19.5, 24.2, 10.4, 16.2    # the solid block beside the stairwell (the landing room is in it)
KX0, KX1, KY0, KY1, KZ1 = 19.0, 23.7, LY0 - 0.5, LY1 + 0.3, 7.25
SLY0, SLY1 = LY0 + 0.55, LY0 + 1.35  # the slot from the landing into it
INKS = ('e_ink', 'e_ink', 'e_ink', 'e_inkb', 'e_ink', 'e_inkb', 'e_inkr', 'e_inks')


def zstair(y):
    """Height of the stair's treads at y (the pitch line)."""
    if y <= Y0: return 0.0
    if y <= LY0: return (y - Y0) / RUN * RISE
    if y <= LY1: return ZL
    if y <= TY: return ZL + (y - LY1) / RUN * RISE
    return UZ


def make():
    R = Room('graffitistair', 2, 2, levels=2, res=2048)
    R.sockets(floor='floor', wall='tile')
    halls(R)
    stairwell(R)
    landing_room(R)
    write_all(R)
    lights(R)
    # walkers: round the lower hall, round the upper hall, and up the stair between them
    lo = navloop(R, [(3.0, 3.0), (16.0, 3.0), (29.0, 3.0), (29.0, 16.0), (29.0, 29.0), (16.0, 29.0), (3.0, 29.0), (3.0, 16.0)])
    up = navloop(R, [(3.0, 3.0), (16.0, 3.0), (29.0, 3.0), (29.0, 16.0), (29.0, 29.0), (16.0, 29.0), (3.0, 29.0), (3.0, 16.0)], z=UZ)
    a, b, c, d = R.navpt(16.0, Y0 - 1.0), R.navpt(16.0, LY0 + 1.0, ZL), R.navpt(16.0, TY + 1.0, UZ), R.navpt(16.0, TY1 + 1.5, UZ)
    R.link(lo[1], a, b, c, d, up[5])
    secret(R, (KX0 + KX1) / 2 + 0.6, (KY0 + KY1) / 2, ZL, 'The Unwritten Room',
           'Behind the slot on the landing there is a room with clean walls, the only clean walls in this part of the library: a desk, a lamp, an inkwell, and one pen, laid down. Nobody has written anything here yet. It is waiting for you to begin.')
    fx(R, 'dust', [CX0, Y0, 0.5, CX1, TY1, 15.0])
    return done(R, 'The Written Stair', weight=4, probe=(16.0, LY0 + 1.0, ZL + 2.0), top=2 * LH - 0.4,
                blurb='A stair, and on every inch of it somebody has written something: a name, a date, I was here, I am still here, forgive me. The oldest writing is at the bottom. You look for your own hand. You find it.')


# ---------------------------------------------------------------------------
def halls(R):
    # the lower hall round the stairwell's walls and the solid block beside them
    for (a, b, c, d) in rects_minus(T - 0.02, T - 0.02, W - T + 0.02, D - T + 0.02, [(WX0, Y0 - 0.2, WX1, TY1), (BX0, BY0, BX1, BY1)]):
        R.cut(box(a - 0.01, b - 0.01, 0, c + 0.01, d + 0.01, TOP, 'tile', bottom='floor', top='plaster'))
    # the upper hall round the stairwell's walls (which close over its south end up here)
    for (a, b, c, d) in rects_minus(T - 0.02, T - 0.02, W - T + 0.02, D - T + 0.02, [(WX0, Y0 - 0.2, WX1, TY1)]):
        R.cut(box(a - 0.01, b - 0.01, UZ, c + 0.01, d + 0.01, 2 * LH - 0.5, 'tile', bottom='floor', top='plaster'))
    # books: lower hall walls, the stairwell's outer faces, the block; upper hall walls
    for z, rows in ((0.0, 12), (UZ, 12)):
        for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, D - 0.6)):
            sh(R, '+x', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-x', W - T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '+y', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-y', D - T, a, b, z=z, rows=rows, frame='walnut')
        for (x, face) in ((WX0, '-x'), (WX1, '+x')):
            if face == '+x' and z == 0.0:
                sh(R, face, x, Y0, BY0 - 0.2, z=z, rows=rows, frame='walnut')
                sh(R, face, x, BY1 + 0.2, TY1 - 0.2, z=z, rows=rows, frame='walnut')
            else:
                sh(R, face, x, Y0, TY1 - 0.2, z=z, rows=rows, frame='walnut')
    sh(R, '+x', BX1, BY0 + 0.2, BY1 - 0.2, rows=12, frame='walnut')
    sh(R, '-y', BY0, BX0 + 0.2, BX1 - 0.2, rows=12, frame='walnut')
    sh(R, '+y', BY1, BX0 + 0.2, BX1 - 0.2, rows=12, frame='walnut')
    # reading tables in both halls
    for z in (0.0, UZ):
        for (x0, y0) in ((4.0, 10.0), (4.0, 20.0), (25.5, 20.0), (25.5, 24.5)):
            R.parts.add(ltable(x0, y0, x0 + 2.4, y0 + 1.0, 0.78, 'walnut', top='leather').xform(0, 0, 0, z))
            llamp(R, x0 + 1.2, y0 + 0.5, z + 0.78, 0.0, lit=True, m='e_lamp')
            for k in range(2):
                for (yy, a) in ((y0 - 0.4, math.pi / 2), (y0 + 1.4, -math.pi / 2)):
                    R.parts.add(lchair(x0 + 0.6 + k * 1.2, yy, a).xform(0, 0, 0, z))


def stairwell(R):
    # the slot: open from the lower floor to the vault over the upper one
    R.cut(box(CX0, Y0 - 0.25, 0, CX1, LY0 + 0.01, TOP, 'tile', bottom='floor', top='tile'))
    R.cut(box(CX0, Y0 + 1.0, TOP - 0.1, CX1, TY1 + 0.02, 2 * LH - 0.5, 'tile', bottom='floor', top='plaster'))
    R.cut(box(CX0, LY0, ZL, CX1, TY1 + 0.02, 2 * LH - 0.5, 'tile', bottom='floor', top='plaster'))
    # the flights and the half landing (solid stone), a brass rail up the west wall
    R.flight(CX0, Y0, 0.0, CX1 - CX0, N1, RISE, RUN, '+y', m='tile', riser='tile', side='tile')
    R.parts.add(box(CX0, LY0, 0, CX1, LY1, ZL, 'tile'))
    R.flight(CX0, LY1, ZL, CX1 - CX0, N1, RISE, RUN, '+y', m='tile', riser='tile', side='tile')
    R.parts.add(box(CX0, TY, ZL, CX1, TY1, UZ, 'tile'))
    for (ya, za, yb, zb) in ((Y0 + RUN, RISE, LY0, ZL), (LY1 + RUN, ZL + RISE, TY, UZ)):
        stair_rail(R, CX0 + 0.12, ya, za, CX0 + 0.12, yb, zb, m='brass')
    # a skylight down the length of the vault
    R.light(box(CX0 + 1.0, Y0 + 2.0, 2 * LH - 0.52, CX1 - 1.0, TY1 - 1.0, 2 * LH - 0.5, 'e_sky', skip=('+z',)))


def landing_room(R):
    """In the block beside the stairwell, level with the half landing: the one clean room."""
    R.cut(box(KX0, KY0, ZL, KX1, KY1, KZ1, 'plaster', bottom='oak', top='plaster'))
    # the slot from the landing: in, then a turn (from the stair you only see a shadow)
    R.cut(box(CX1 - 0.05, SLY0, ZL, KX0 + 0.05, SLY1, ZL + 2.2, 'tile', bottom='oak', top='tile'))
    # a desk, a chair, a lamp, an inkwell and the pen; a blank book open; shelves of blank books
    x0 = KX1 - 1.7
    R.parts.add(ltable(x0, KY0 + 0.6, x0 + 1.4, KY0 + 1.4, 0.78, 'walnut', top='leather').xform(0, 0, 0, ZL))
    R.parts.add(lchair_legs(x0 + 0.7, KY0 + 1.85, -math.pi / 2).xform(0, 0, 0, ZL))
    R.spot('sit', x0 + 0.7, KY0 + 1.85, ZL + 0.48, -math.pi / 2)
    llamp(R, x0 + 0.2, KY0 + 1.1, ZL + 0.78, 0.3, lit=True, m='e_lamp')
    bulb(R, (KX0 + KX1) / 2, (KY0 + KY1) / 2, KZ1 - 0.6, r=0.09, m='e_lamp', top=KZ1)
    ob = box(-0.22, -0.16, 0, 0.0, 0.16, 0.03, 'ivory', sides='leather'); ob.add(box(0.0, -0.16, 0, 0.22, 0.16, 0.03, 'ivory', sides='leather'))
    R.nocol.add(ob.xform(0.0, x0 + 0.75, KY0 + 1.0, ZL + 0.78))
    R.nocol.add(cyl(x0 + 1.15, KY0 + 0.8, ZL + 0.78, ZL + 0.84, 0.04, 8, side='black', top='ink'))
    R.nocol.add(beam((x0 + 0.95, KY0 + 1.05, ZL + 0.79), (x0 + 1.12, KY0 + 1.2, ZL + 0.79), 0.012, 'ink'))
    R.spot('plaque', x0 + 0.75, KY0 + 1.0, ZL + 0.8, math.pi / 2, text='Begin here.')
    sh(R, '-y', KY1, KX0 + 1.2, KX1 - 0.2, z=ZL, rows=6, frame='oak', depth=0.28)
    R.light(sphere(KX0 + 1.0, KY1 - 0.4, ZL + 2.2, 0.06, 6, 3, 'e_candle'))
    a, b = R.navpt(KX0 + 0.9, (SLY0 + SLY1) / 2, ZL), R.navpt(KX1 - 1.0, KY0 + 2.5, ZL)
    R.link(a, b)


# ---------------------------------------------------------------------------
# the writing: each word is one flat quad of ink, drawn unlit (an emitter that barely emits), so the
# thousands of strokes cost nothing in the lightmap
def line_strip(g, P0, U, V, N, L, rs, ink, stroke, off):
    """A line of handwriting from P0 along U (unit), L long; V the up direction in the plane; N the normal."""
    us = [0.0]; mats = []
    u = rs.uniform(0.0, 0.08)
    if u > 0: us.append(u); mats.append('gap')
    while u < L:
        a = rs.uniform(0.02, 0.13)
        if u + a > L: break
        u += a; us.append(u); mats.append('ink')
        b = rs.uniform(0.008, 0.025) if rs.random() < 0.75 else rs.uniform(0.05, 0.1)
        if u + b > L: break
        u += b; us.append(u); mats.append('gap')
    if len(us) < 2: return
    if mats and mats[-1] == 'gap': us.pop(); mats.pop()
    if not mats: return
    wob = rs.uniform(-0.3, 0.3) * stroke
    bot, top = [], []
    for uu in us:
        c = [P0[i] + U[i] * uu + N[i] * off + V[i] * wob * math.sin(uu * 7.0) for i in range(3)]
        bot.append(g.vert([c[i] - V[i] * stroke / 2 for i in range(3)]))
        top.append(g.vert([c[i] + V[i] * stroke / 2 for i in range(3)]))
    cr = (U[1] * V[2] - U[2] * V[1], U[2] * V[0] - U[0] * V[2], U[0] * V[1] - U[1] * V[0])
    flip = cr[0] * N[0] + cr[1] * N[1] + cr[2] * N[2] < 0
    for k, m in enumerate(mats):
        if m != 'ink': continue
        f = [bot[k], bot[k + 1], top[k + 1], top[k]]
        if flip: f = f[::-1]
        g.face(f, ink, [(0, 0), (1, 0), (1, 1), (0, 1)])


def patch(g, O, U, V, N, w, h, rs, spacing=None, stroke=None, off=0.004, tilt=0.0):
    """A block of handwriting on a flat surface: lines `spacing` apart filling w x h from origin O."""
    ink = rs.choice(INKS)
    spacing = spacing or rs.uniform(0.06, 0.1)
    stroke = stroke or spacing * rs.uniform(0.2, 0.28)
    if tilt:
        c, s = math.cos(tilt), math.sin(tilt)
        U, V = [U[i] * c + V[i] * s for i in range(3)], [V[i] * c - U[i] * s for i in range(3)]
    n = int(h / spacing)
    for k in range(n):
        v = h - (k + 0.6) * spacing
        L = w * rs.uniform(0.55, 1.0) if rs.random() < 0.4 else w
        P0 = [O[i] + V[i] * v for i in range(3)]
        line_strip(g, P0, U, V, N, L, rs, ink, stroke, off)


def write_wall(g, x, face, y0, y1, zlo, zhi, rs, density=1.0, layer=0):
    """Cover a wall x=const (facing +x or -x) between y0 and y1, from zlo(y) up to zhi(y), in patches."""
    N = (face, 0.0, 0.0)
    U = (0.0, 1.0, 0.0)
    y = y0
    while y < y1 - 0.2:
        w = rs.uniform(0.6, 1.6)
        w = min(w, y1 - y)
        z0 = max(zlo(y), zlo(y + w)) + rs.uniform(0.05, 0.3)
        z1 = min(zhi(y), zhi(y + w))
        z = z0
        while z < z1 - 0.3:
            h = min(rs.uniform(0.5, 1.4), z1 - z)
            if rs.random() < density:
                patch(g, (x, y + rs.uniform(0, 0.08), z), U, (0.0, 0.0, 1.0), N, w - 0.08, h, rs,
                      off=0.004 + 0.003 * ((layer + int(y * 3 + z * 5)) % 3), tilt=rs.uniform(-0.06, 0.06))
            z += h + rs.uniform(-0.1, 0.12)
        y += w + rs.uniform(-0.15, 0.05)


def write_all(R):
    rs = rng(99)
    g = Geo()
    lo = lambda y: zstair(y)
    hi = lambda y: zstair(y) + 3.4
    top = lambda y: min(2 * LH - 0.8, zstair(y) + 7.0)
    for (x, face) in ((CX0, 1.0), (CX1, -1.0)):
        write_wall(g, x, face, Y0 - 0.1, TY1, lo, hi, rs, 1.0)
        write_wall(g, x, face, Y0 + 0.5, TY1, hi, top, rs, 0.25, layer=1)
    # the treads and risers: a line or two on each
    for (ya, za) in ((Y0, 0.0), (LY1, ZL)):
        for k in range(N1):
            yt = ya + k * RUN; zt = za + (k + 1) * RISE
            # riser (faces -y) at yt, from zt - RISE to zt
            if rs.random() < 0.85:
                line_strip(g, (CX0 + rs.uniform(0.1, 0.8), yt - 0.003, zt - RISE * 0.5), (1, 0, 0), (0, 0, 1), (0, -1, 0),
                           rs.uniform(2.0, CX1 - CX0 - 1.0), rs, rs.choice(INKS), 0.03, 0.0)
            # tread (faces up)
            for j in range(rs.randint(0, 2)):
                line_strip(g, (CX0 + rs.uniform(0.1, 1.0), yt + 0.08 + j * 0.1, zt + 0.003), (1, 0, 0), (0, 1, 0), (0, 0, 1),
                           rs.uniform(1.0, CX1 - CX0 - 1.2), rs, rs.choice(INKS), 0.025, 0.0)
    # the landings' floors
    for (ya, yb, z) in ((LY0, LY1, ZL), (TY, TY1, UZ)):
        yy = ya + 0.15
        while yy < yb - 0.1:
            line_strip(g, (CX0 + rs.uniform(0.1, 0.6), yy, z + 0.003), (1, 0, 0), (0, 1, 0), (0, 0, 1), rs.uniform(2.0, 3.8), rs, rs.choice(INKS), 0.025, 0.0)
            yy += rs.uniform(0.1, 0.18)
    # round the stairwell's mouth in the lower hall and the top in the upper, a little spill of writing
    R.light(g)
    print('writing faces', len(g.f))


def lights(R):
    # green-shaded lamps on brackets up both walls of the stairwell
    y = Y0 + 1.0
    while y < TY1 - 0.5:
        z = zstair(y) + 2.6
        for (x, face) in ((CX0, 0.0), (CX1, math.pi)):
            nx = math.cos(face)
            R.nocol.add(beam((x, y, z), (x + nx * 0.5, y, z + 0.25), 0.03, 'brass'))
            R.nocol.add(frustum(x + nx * 0.5, y, z - 0.05, z + 0.2, 0.2, 0.06, 10, 'green', inner='ivory'))
            R.light(cyl(x + nx * 0.5, y, z - 0.03, z, 0.13, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
        y += 3.2
    for z in (0.0, UZ):
        for (x, y) in ((6.0, 6.0), (26.0, 6.0), (6.0, 26.0), (26.0, 26.0), (16.0, 27.5)):
            pendant(R, x, y, z + 4.4, z + TOP - 0.2 if z == 0 else 2 * LH - 0.5, r=0.3)
        for (x, y) in ((6.0, 16.0), (26.0, 16.0), (10.0, 29.0), (22.0, 29.0), (10.0, 2.5), (22.0, 2.5)):
            pendant(R, x, y, z + 4.4, z + TOP - 0.2 if z == 0 else 2 * LH - 0.5, r=0.3)
