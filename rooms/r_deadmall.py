"""The Mall: a two-storey shopping mall inside the library, closed for ever. An atrium under skylights,
a fountain still running, escalators crossing the air (switched off: you walk up them), and all round
both floors shops, dozens of shops, every one of them fitted out with shelves and every shelf full of
books. One shop's grille is down. Behind the shop next door, a false bookcase lets you into the service
corridor, and the corridor into the staff room, where somebody's coat is on the chair."""
from kit_h10 import *

W = D = 64.0
SB = 6.0                          # the depth of the band of shops round the edge
A0, A1 = 18.0, 46.0               # the atrium (open to the skylights)
UZ = LH                           # the gallery floor
H0 = TOP                          # lower concourse ceiling
H1 = 13.2                         # upper gallery ceiling
HA = 2 * LH - 0.5                 # atrium ceiling (skylights)
SH0, SH1 = 4.4, UZ + 4.4          # shop ceilings (lower, upper)
SEGS = ((10.4, 21.6), (26.4, 37.6), (42.4, 53.6))       # shopfront stretches between the doorways
ESC = ((22.0, 30.0, -1), (40.6, 34.0, +1))              # escalators: (x0, foot y, direction)
EN, ER, ERUN, EW = 40, 0.2, 0.3, 1.4
# the secret: behind the shop at x 42..48 on the south side, lower floor
CY0, CY1 = 0.45, 1.6              # the service corridor
SA0, SA1 = 42.4, 47.9             # the shop in front of it
SB0, SB1 = 48.1, 53.6             # the shuttered shop: the staff room
FX0, FX1 = 44.4, 45.6             # the false bookcase in shop A's back wall


def make():
    R = Room('deadmall', 4, 4, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    halls(R)
    shops(R)
    atrium(R)
    for spec in ESC:
        escalator(R, *spec)
    fountain(R)
    secret_rooms(R)
    lights(R)
    navs(R)
    secret(R, 51.0, 3.0, 0.0, 'The Staff Room',
           'Behind the shelves of the shop next door, the service corridor, and at the end of it the staff room: lockers, a kettle, a rota on the wall with every shift filled in for ever. A coat is on the back of a chair. Somebody is on their break. Somebody is always on their break.')
    fx(R, 'dust', [A0, A0, 1.0, A1, A1, HA - 0.5])
    return done(R, 'The Mall', weight=3, probe=(32.0, 22.0, 3.0), top=HA,
                blurb='A shopping mall, two floors of it, under skylights: a fountain, escalators, and shop after shop after shop, all open, all lit, all selling the same thing. Books. There is nobody behind any of the counters.')


# ---------------------------------------------------------------------------
def halls(R):
    # the lower concourse inside the band of shops, under the gallery; the atrium goes up to the skylights
    R.cut(box(SB, SB, 0, W - SB, D - SB, H0, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(A0, A0, 0, A1, A1, HA, 'tile', bottom='terrazzo', top='plaster'))
    # the upper gallery round the atrium
    R.cut(box(SB, SB, UZ, W - SB, D - SB, H1, 'tile', bottom='terrazzo', top='plaster'))
    # passages through the band of shops to every doorway, both floors
    for z, h in ((0.0, 4.6), (UZ, UZ + 4.6)):
        for c in (8.0, 24.0, 40.0, 56.0):
            R.cut(box(c - 2.0, T - 0.02, z, c + 2.0, SB + 0.05, h, 'tile', bottom='terrazzo', top='plaster'))
            R.cut(box(c - 2.0, D - SB - 0.05, z, c + 2.0, D - T + 0.02, h, 'tile', bottom='terrazzo', top='plaster'))
            R.cut(box(T - 0.02, c - 2.0, z, SB + 0.05, c + 2.0, h, 'tile', bottom='terrazzo', top='plaster'))
            R.cut(box(W - SB - 0.05, c - 2.0, z, W - T + 0.02, c + 2.0, h, 'tile', bottom='terrazzo', top='plaster'))
    # the floor of the concourse: a border of dark marble round the atrium
    g = Geo()
    for (x0, y0, x1, y1) in ((A0 - 0.8, A0 - 0.8, A1 + 0.8, A0 - 0.4), (A0 - 0.8, A1 + 0.4, A1 + 0.8, A1 + 0.8),
                             (A0 - 0.8, A0 - 0.4, A0 - 0.4, A1 + 0.4), (A1 + 0.4, A0 - 0.4, A1 + 0.8, A1 + 0.4)):
        g.add(box(x0, y0, 0, x1, y1, 0.008, 'slate', skip=('-z',)))
    R.nocol.add(g)
    # the gallery's edge: a thick slab face, and a solid parapet with a brass rail (gaps where escalators land)
    for (y, face, gx) in ((A0, 'S', ESC[0][0]), (A1, 'N', ESC[1][0])):
        for (a, b) in ((A0, gx - 0.1), (gx + EW + 0.1, A1)):
            glass_rail(R, a, y + (-0.12 if face == 'S' else 0.12), b, y + (-0.12 if face == 'S' else 0.12), UZ, 1.0, 'tile', 'brass')
    for x in (A0, A1):
        glass_rail(R, x + (-0.12 if x == A0 else 0.12), A0, x + (-0.12 if x == A0 else 0.12), A1, UZ, 1.0, 'tile', 'brass')
    # square piers under the gallery edge and up to its ceiling
    for k in range(5):
        p = A0 + (A1 - A0) * k / 4
        for (x, y) in ((p, A0 - 0.6), (p, A1 + 0.6), (A0 - 0.6, p), (A1 + 0.6, p)):
            if any(abs(y - (A0 - 0.6 if s_ < 0 else A1 + 0.6)) < 0.1 and x0 - 1.0 < x < x0 + EW + 1.0 for (x0, fy, s_) in ESC): continue
            R.parts.add(box(x - 0.45, y - 0.45, 0, x + 0.45, y + 0.45, H0, 'tile', skip=('-z', '+z')))
            R.parts.add(box(x - 0.45, y - 0.45, UZ, x + 0.45, y + 0.45, H1, 'tile', skip=('-z', '+z')))


def shopfront(R, side, a, b, z, h, rs, grille=0.0):
    """Pilasters, a fascia with a dead sign, and a low stall board along the front of a shop."""
    def P(u, v):   # u along the front, v inward from the front line (into the concourse is -v)
        if side == 'S': return (u, SB - v)
        if side == 'N': return (u, D - SB + v)
        if side == 'W': return (SB - v, u)
        return (W - SB + v, u)
    def B(u0, u1, v0, v1, z0, z1, m, **kw):
        p0, p1 = P(u0, v0), P(u1, v1)
        return box(min(p0[0], p1[0]), min(p0[1], p1[1]), z0, max(p0[0], p1[0]), max(p0[1], p1[1]), z1, m, **kw)
    g = Geo()
    for u in (a, b):
        g.add(B(u - 0.18, u + 0.18, -0.12, 0.25, z, z + h, 'walnut', skip=('-z',)))
    g.add(B(a, b, -0.18, 0.25, z + h - 0.7, z + h, 'walnut'))
    g.add(B(a + 0.4, b - 0.4, -0.2, -0.18, z + h - 0.6, z + h - 0.1, rs.choice(('black', 'black', 'green', 'oxblood'))))
    R.parts.add(g)
    if grille > 0:
        # a roller grille pulled part way down: iron slats (drawn), and the box it rolls into
        gg = Geo()
        zb = z + h - 0.7 - grille
        n = int((b - a) / 0.25)
        for k in range(int(grille / 0.12)):
            zz = z + h - 0.75 - k * 0.12
            gg.add(B(a + 0.18, b - 0.18, 0.02, 0.05, zz - 0.06, zz, 'iron'))
        R.nocol.add(gg)
    return P, B


def shop(R, side, a, b, z, rs, upper=False, back_v=None, grille=0.0, gap=None):
    """One shop between a and b along a side: shelves round its walls, a stack in the middle, a counter."""
    h = SH0 if z == 0 else SH1 - UZ
    back = back_v if back_v is not None else SB - T      # depth from the front line to the back wall
    P, B = shopfront(R, side, a, b, z, h, rs, grille)
    # the shop's own box
    p0, p1 = P(a + 0.1, -0.05), P(b - 0.1, back)
    R.cut(box(min(p0[0], p1[0]), min(p0[1], p1[1]), z, max(p0[0], p1[0]), max(p0[1], p1[1]), z + h, 'ivory', bottom='floor', top='plaster'))
    rows = 7 if not upper else 6
    ang = {'S': '+y', 'N': '-y', 'W': '+x', 'E': '-x'}[side]
    bk = P(a, back)                   # the back wall
    if side in 'SN':
        yb = bk[1]
        spans = [(a + 0.5, b - 0.5)] if gap is None else [(a + 0.5, gap[0] - 0.05), (gap[1] + 0.05, b - 0.5)]
        fr = rs.choice(('walnut', 'oak', 'wood'))
        for (p, q) in spans:
            sh(R, ang, yb, p, q, z=z, rows=rows, frame=fr)
    else:
        xb = bk[0]
        sh(R, ang, xb, a + 0.5, b - 0.5, z=z, rows=rows, frame=rs.choice(('walnut', 'oak', 'wood')))
    # side walls (only downstairs)
    if not upper:
        for (u, face) in ((a + 0.1, 1), (b - 0.1, -1)):
            q0, q1 = P(u, 1.0), P(u, back - 0.5)
            if side in 'SN':
                sh(R, '+x' if face > 0 else '-x', q0[0], min(q0[1], q1[1]), max(q0[1], q1[1]), z=z, rows=rows, frame='walnut')
            else:
                sh(R, '+y' if face > 0 else '-y', q0[1], min(q0[0], q1[0]), max(q0[0], q1[0]), z=z, rows=rows, frame='walnut')
    # a stack in the middle (a table of books upstairs), a counter by the door
    m0, m1 = P((a + b) / 2 - 1.1, 2.3), P((a + b) / 2 + 1.1, 2.3)
    if not upper:
        if side in 'SN': stack(R, 'x', m0[1], min(m0[0], m1[0]), max(m0[0], m1[0]), z=z, rows=4, frame='walnut')
        else: stack(R, 'y', m0[0], min(m0[1], m1[1]), max(m0[1], m1[1]), z=z, rows=4, frame='walnut')
    else:
        R.parts.add(B((a + b) / 2 - 1.0, (a + b) / 2 + 1.0, 1.8, 2.8, z, z + 0.85, 'walnut', top='oak'))
        tb = Geo()
        for k in range(5):
            u = (a + b) / 2 - 0.8 + k * 0.4; pp = P(u, 2.3)
            book_row_flat(tb, pp[0], pp[1], z + 0.85, rs.uniform(0, 3), rs, rs.randint(1, 4))
        R.nocol.add(tb)
    R.parts.add(B(b - 1.6, b - 0.3, 0.5, 1.1, z, z + 1.0, 'walnut', top='oak'))
    return P, B


def shops(R):
    rs = rng(3)
    for side in 'SNWE':
        for (a, b) in SEGS:
            for (u0, u1) in ((a, (a + b) / 2 - 0.1), ((a + b) / 2 + 0.1, b)):
                for z in (0.0, UZ):
                    upper = z > 0
                    if side == 'S' and not upper and abs(u0 - SA0) < 0.01:
                        shop(R, side, u0, u1, z, rs, back_v=SB - CY1 - 0.3, gap=(FX0, FX1))
                        continue
                    if side == 'S' and not upper and abs(u0 - SB0) < 0.01:
                        shopfront(R, side, u0, u1, z, SH0, rs)
                        continue
                    gr = 0.0
                    r = rs.random()
                    if r < 0.15: gr = rs.uniform(0.6, 2.2)
                    shop(R, side, u0, u1, z, rs, upper=upper, grille=gr)
    # facade over the lower shops: a cornice, and the gallery's balustrade line upstairs
    g = Geo()
    for (x0, y0, x1, y1) in ((SB, SB - 0.3, W - SB, SB), (SB, D - SB, W - SB, D - SB + 0.3), (SB - 0.3, SB, SB, D - SB), (W - SB, SB, W - SB + 0.3, D - SB)):
        g.add(box(x0, y0, SH0 + 0.4, x1, y1, SH0 + 0.7, 'gilt'))
        g.add(box(x0, y0, UZ + SH0 - UZ * 0 + 0.4, x1, y1, UZ + SH0 + 0.7, 'gilt'))
    R.parts.add(g)


def atrium(R):
    # skylights: four wells of painted sky between iron beams
    g = Geo()
    for i in range(2):
        for j in range(2):
            x0, y0 = A0 + 1.0 + i * 13.5, A0 + 1.0 + j * 13.5
            R.light(box(x0, y0, HA - 0.03, x0 + 12.5, y0 + 12.5, HA - 0.01, 'e_skydome', skip=('+z',)))
            for k in range(6):
                t = k / 5
                g.add(box(x0 + 12.5 * t - 0.08, y0, HA - 0.35, x0 + 12.5 * t + 0.08, y0 + 12.5, HA - 0.03, 'iron'))
                g.add(box(x0, y0 + 12.5 * t - 0.08, HA - 0.3, x0 + 12.5, y0 + 12.5 * t + 0.08, HA - 0.03, 'iron'))
    R.nocol.add(g)
    # planters with ferns, benches, and lamp posts round the fountain
    rs = rng(8)
    for (x, y) in ((42.0, 22.0), (22.0, 42.0), (20.5, 36.0), (43.5, 28.0), (32.0, 20.5), (32.0, 43.5)):
        R.parts.add(box(x - 1.2, y - 1.2, 0, x + 1.2, y + 1.2, 0.7, 'walnut', top='leather'))
        leaves_(R, x, y, 1.1, rs)
    for (x, y, a) in ((27.0, 22.0, 0.0), (37.0, 22.0, 0.0), (27.0, 42.0, math.pi), (37.0, 42.0, math.pi), (21.0, 32.0, -math.pi / 2), (43.0, 32.0, math.pi / 2)):
        bench_(R, x, y, a)
    for (x, y) in ((27.5, 27.5), (36.5, 27.5), (27.5, 36.5), (36.5, 36.5)):
        lamp_post(R, x, y, 0.0, 3.4, m='e_lamp')
    # a directory board by the south entrance, the you-are-here dot lit
    R.parts.add(box(31.0, 12.0, 0, 33.0, 12.3, 2.2, 'walnut'))
    R.parts.add(box(31.1, 11.98, 0.6, 32.9, 12.0, 2.1, 'ivory'))
    R.light(box(31.9, 11.96, 1.2, 32.0, 11.98, 1.3, 'e_red'))
    R.spot('plaque', 32.0, 12.0, 1.4, -math.pi / 2, text='YOU ARE HERE.')


def leaves_(R, x, y, r, rs):
    g = Geo()
    for k in range(7):
        a = rs.uniform(0, 6.28); d = rs.uniform(0, r * 0.6)
        g.add(blob(x + math.cos(a) * d, y + math.sin(a) * d, 0.9 + rs.uniform(0, 0.5), rs.uniform(0.35, 0.6), rs.uniform(0.35, 0.6), rs.uniform(0.25, 0.45), 7, 3, 'leaf'))
    R.nocol.add(g)


def bench_(R, x, y, a):
    g = Geo()
    g.add(box(-1.0, -0.25, 0.4, 1.0, 0.25, 0.48, 'oak'))
    for s_ in (-0.85, 0.85): g.add(box(s_ - 0.05, -0.22, 0, s_ + 0.05, 0.22, 0.4, 'iron'))
    g.add(box(-1.0, 0.2, 0.48, 1.0, 0.26, 0.95, 'oak'))
    R.parts.add(g.xform(a, x, y))
    R.spot('sit', x, y, 0.48, a - math.pi / 2)


def escalator(R, x0, fy, s_):
    """An escalator (stopped) from the concourse floor up to the gallery edge: steel steps between solid
    steel sides with black handrails, hanging on its sloped underside."""
    L = EN * ERUN
    ty = fy + s_ * L                     # the top end, at the gallery edge
    axis = '+y' if s_ > 0 else '-y'
    save = R.nocol; R.nocol = Geo()
    R.flight(x0, fy, 0.0, EW, EN, ER, ERUN, axis)      # only its invisible ramp
    R.nocol = save
    # the steps as a ribbon (sawtooth top, sloped soffit), along local +x then turned
    from kit_h2 import ribbon_stair
    g = ribbon_stair(EN, ER, ERUN, EW, th=0.6, m='steel', riser='steel', side='steel', under='steel')
    if s_ > 0: g.xform(math.pi / 2, x0 + EW, fy, 0.0)
    else: g.xform(-math.pi / 2, x0, fy, 0.0)
    R.parts.add(g)
    # the sides: sloped slabs from below the soffit to a metre above the steps, black handrail on top
    for x in (x0 - 0.12, x0 + EW):
        # a slab: bottom edge along the soffit, top edge 1 m above the pitch line; flat runs at each end
        prof = [(fy - s_ * 0.8, -0.0), (fy - s_ * 0.8, 1.0), (fy, 1.0), (ty, UZ + 1.0), (ty + s_ * 0.6, UZ + 1.0),
                (ty + s_ * 0.6, UZ - 0.5), (ty, UZ - 0.9), (fy + s_ * 1.2, -0.0)]
        if s_ < 0: prof = prof[::-1]
        pr = [(p, q) for (p, q) in prof]
        side = prism(pr, 'x', x, x + 0.12, ['steel'] * len(pr), cap='steel')
        R.parts.add(side)
        xm = x + 0.06
        R.nocol.add(beam((xm, fy - s_ * 0.8, 1.02), (xm, fy, 1.02), 0.1, 'black', 0.06))
        R.nocol.add(beam((xm, fy, 1.02), (xm, ty, UZ + 1.02), 0.1, 'black', 0.06))
        R.nocol.add(beam((xm, ty, UZ + 1.02), (xm, ty + s_ * 0.6, UZ + 1.02), 0.1, 'black', 0.06))
    # comb plates at both ends
    for (y, z) in ((fy, 0.0), (ty, UZ)):
        R.nocol.add(box(x0, min(y, y - s_ * 0.5), z, x0 + EW, max(y, y - s_ * 0.5), z + 0.01, 'brass') if z == 0 else
                    box(x0, min(y, y + s_ * 0.5), z, x0 + EW, max(y, y + s_ * 0.5), z + 0.01, 'brass'))


def fountain(R):
    cx = cy = 32.0
    R.cut(cyl(cx, cy, -0.5, 0.3, 5.0, 40, side='mosaic', bottom='mosaic', top='tile'))
    rwater(R, cx, cy, 5.0, -0.1, -0.5)
    R.parts.add(ring(cx, cy, 0, 0.3, 5.0, 5.5, 40, top='terrazzo', bottom='tile', inner='tile', outer='tile'))
    R.parts.add(ring(cx, cy, -0.5, -0.15, 4.55, 5.0, 40, top='mosaic', bottom='tile', inner='mosaic', outer='tile'))
    R.parts.add(cyl(cx, cy, -0.5, 1.3, 0.5, 16, side='tile', top='tile'))
    R.parts.add(cyl(cx, cy, 1.3, 1.6, 1.8, 24, side='tile', top='mosaic', bottom='tile'))
    R.parts.add(cyl(cx, cy, 1.6, 2.6, 0.25, 12, side='tile', top='tile'))
    R.parts.add(cyl(cx, cy, 2.6, 2.8, 0.9, 16, side='tile', top='mosaic', bottom='tile'))
    R.nocol.add(cyl(cx, cy, 2.8, 3.8, 0.06, 6, side='foam', top='foam'))
    # water falling from the basins: thin sheets
    for k in range(10):
        a = 2 * math.pi * k / 10
        for (r, z0, z1) in ((1.82, -0.1, 1.45), (0.92, 1.6, 2.7)):
            R.nocol.add(box(-0.02, -0.25, z0, 0.02, 0.25, z1, 'foam').xform(a, cx + math.cos(a) * r, cy + math.sin(a) * r, 0))
    R.light(ring(cx, cy, 0.31, 0.34, 5.1, 5.4, 40, top='e_pool', bottom='e_pool', inner='e_pool', outer='e_pool'))


def secret_rooms(R):
    """The service corridor behind shop A (south side, lower floor), and the staff room in the shuttered shop."""
    z = 0.0
    # the shuttered shop's grille, right down and locked (solid)
    R.parts.add(box(SB0 + 0.2, SB - 0.05, 0, SB1 - 0.2, SB + 0.02, SH0 - 0.7, 'iron'))
    g = Geo()
    for k in range(int((SH0 - 0.7) / 0.12)):
        g.add(box(SB0 + 0.2, SB + 0.02, k * 0.12 + 0.02, SB1 - 0.2, SB + 0.05, k * 0.12 + 0.08, 'iron'))
    R.nocol.add(g)
    R.nocol.add(box((SB0 + SB1) / 2 - 0.15, SB + 0.05, 0.3, (SB0 + SB1) / 2 + 0.15, SB + 0.1, 0.45, 'brass'))
    # the corridor behind shop A, and the staff room
    R.cut(box(SA0 + 0.3, CY0, z, SB0 + 0.2, CY1, 2.8, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(SB0 + 0.1, CY0, z, SB1 - 0.1, SB - 0.1, 3.2, 'ivory', bottom='floor', top='plaster'))
    # the false bookcase in shop A's back wall
    yb = CY1 + 0.3
    false_case(R, FX0, yb, FX1 - FX0, '+y', rows=7, frame='walnut', h=2.3, depth=0.35, floor='floor')
    R.cut(box(FX0 + 0.05, CY1 - 0.05, 0, FX1 - 0.05, yb + 0.05, 2.3, 'wood', bottom='floor', top='wood'))
    # corridor: boxes of stock, a bulb
    rs = rng(12)
    for k in range(6):
        crate(R, SA0 + 0.9 + k * 0.5, CY0 + 0.35, 0.0, s=0.45, m='oak', ang=rs.uniform(-0.2, 0.2), col=False)
    bulb(R, SA0 + 3.0, (CY0 + CY1) / 2, 2.2, r=0.06, m='e_dim', top=2.8)
    # staff room: lockers, a table, chairs, a coat on one, a kettle, a rota, a sofa, a clock
    x0, x1, y0, y1 = SB0 + 0.1, SB1 - 0.1, CY0, SB - 0.1
    for k in range(6):
        R.parts.add(box(x0 + 0.1 + k * 0.5, y0 + 0.02, 0, x0 + 0.55 + k * 0.5, y0 + 0.5, 1.9, 'green'))
        R.nocol.add(box(x0 + 0.45 + k * 0.5, y0 + 0.5, 1.0, x0 + 0.48 + k * 0.5, y0 + 0.52, 1.15, 'brass'))
    R.parts.add(ltable(x0 + 1.2, y0 + 2.0, x0 + 2.6, y0 + 3.0, 0.76, 'oak', top='oak'))
    for (x, y, a) in ((x0 + 1.9, y0 + 1.5, math.pi / 2), (x0 + 1.9, y0 + 3.5, -math.pi / 2)):
        R.parts.add(lchair_legs(x, y, a))
        R.spot('sit', x, y, 0.48, a)
    from kit_h2 import hexa
    cx, cy = x0 + 1.9, y0 + 3.5
    R.nocol.add(hexa([(cx - 0.22, cy + 0.18, 0.35), (cx + 0.22, cy + 0.18, 0.35), (cx + 0.22, cy + 0.3, 0.35), (cx - 0.22, cy + 0.3, 0.35),
                      (cx - 0.2, cy + 0.2, 1.02), (cx + 0.2, cy + 0.2, 1.02), (cx + 0.2, cy + 0.3, 1.02), (cx - 0.2, cy + 0.3, 1.02)], 'coat6'))
    R.nocol.add(cyl(x0 + 1.6, y0 + 2.5, 0.76, 0.86, 0.04, 8, side='ivory', top='food'))
    R.parts.add(box(x1 - 0.7, y0 + 0.1, 0, x1 - 0.05, y0 + 0.7, 0.9, 'walnut', top='oak'))
    R.nocol.add(cyl(x1 - 0.4, y0 + 0.4, 0.9, 1.1, 0.1, 10, side='chrome', top='chrome'))
    R.nocol.add(box(x1 - 0.02, y0 + 1.5, 1.2, x1, y0 + 2.4, 1.9, 'ivory'))
    R.parts.add(box(x1 - 0.9, y1 - 2.2, 0, x1 - 0.05, y1 - 0.2, 0.45, 'velvet'))
    R.parts.add(box(x1 - 0.3, y1 - 2.2, 0.45, x1 - 0.05, y1 - 0.2, 0.9, 'velvet'))
    R.spot('sit', x1 - 0.5, y1 - 1.2, 0.45, math.pi)
    llamp(R, x0 + 2.3, y0 + 2.5, 0.76, 0.5, lit=True, m='e_amber')
    bulb(R, (x0 + x1) / 2, (y0 + y1) / 2, 2.5, r=0.08, m='e_dim', top=3.2)
    R.spot('plaque', x1 - 0.05, y0 + 1.95, 1.5, math.pi, text='ROTA. Every shift: you.')
    a, b = R.navpt(SA0 + 1.0, (CY0 + CY1) / 2), R.navpt(x0 + 0.6, y0 + 1.8)
    R.link(a, b)


def lights(R):
    # panels in the concourse ceiling and the gallery ceiling, a few of them out
    rs = rng(5)
    for z in (H0, H1):
        for k in range(8):
            t = SB + 2.0 + (W - 2 * SB - 4.0) * k / 7
            for (x, y) in ((t, SB + 3.0), (t, D - SB - 3.0), (SB + 3.0, t), (W - SB - 3.0, t)):
                if rs.random() < 0.2: continue
                R.light(box(x - 0.8, y - 0.8, z - 0.03, x + 0.8, y + 0.8, z - 0.01, 'e_panel', skip=('+z',)))
    # a green lamp in every other shop, on the counter, and exit signs over the doorway passages
    for side in 'SNWE':
        for c in (8.0, 24.0, 40.0, 56.0):
            for z in (0.0, UZ):
                if side == 'S': p, a = (c, SB + 0.1), -math.pi / 2
                elif side == 'N': p, a = (c, D - SB - 0.1), math.pi / 2
                elif side == 'W': p, a = (SB + 0.1, c), math.pi
                else: p, a = (W - SB - 0.1, c), 0.0
                g = box(-0.3, -0.03, 0, 0.3, 0.03, 0.2, 'e_exit').xform(a + math.pi / 2, p[0], p[1], z + 4.8)
                R.light(g)


def navs(R):
    lo = navloop(R, [(SB + 2.0, SB + 2.0), (32.0, SB + 2.0), (W - SB - 2.0, SB + 2.0), (W - SB - 2.0, 32.0),
                     (W - SB - 2.0, D - SB - 2.0), (32.0, D - SB - 2.0), (SB + 2.0, D - SB - 2.0), (SB + 2.0, 32.0)])
    up = navloop(R, [(SB + 2.0, SB + 2.0), (32.0, SB + 2.0), (W - SB - 2.0, SB + 2.0), (W - SB - 2.0, 32.0),
                     (W - SB - 2.0, D - SB - 2.0), (32.0, D - SB - 2.0), (SB + 2.0, D - SB - 2.0), (SB + 2.0, 32.0)], z=UZ)
    rg = navloop(R, [(32.0 + 8.5 * math.cos(k * math.pi / 4), 32.0 + 8.5 * math.sin(k * math.pi / 4)) for k in range(8)])
    R.link(lo[1], rg[6]); R.link(lo[5], rg[2])
    for (x0, fy, s_) in ESC:
        ty = fy + s_ * EN * ERUN
        a, b = R.navpt(x0 + EW / 2, fy - s_ * 1.2), R.navpt(x0 + EW / 2, ty + s_ * 1.5, UZ)
        R.link(a, b)
        R.link(rg[0] if x0 > 32 else rg[4], a)
        R.link(b, up[5] if s_ > 0 else up[1])
