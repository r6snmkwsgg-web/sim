"""The Rotunda of the Long Way Round: a domed rotunda inside an octagonal ambulatory. Walk the ambulatory
clockwise and it goes round like any other. Walk it anticlockwise and at the north-east there are two
arches close together, and passing the first you find you are walking back the way you came: so one way
round takes a minute and the other way takes for ever, or the long way. The rotunda's floor is inlaid
with rings that do not quite line up; the plinth at its centre has a low door, and a stair under the
medallion down to a crypt."""
from kit_h11 import *

W = D = 32.0
CX = CY = 16.0
RR = 8.0                      # the rotunda's inside
AI, AO = 8.6, 12.2            # the ambulatory's inner and outer faces (apothems of octagons)
AW = 0.4                      # the outer octagon wall's thickness
HZ = 5.0                      # ceiling of the ambulatory and the cloister
DZ, DR = 6.2, 1.2             # the rotunda's drum top and dome rise
UT = math.radians(45)         # the ambulatory's side with the turning arches
FS, FT_, FW, FH = 1.3, 0.3, 2.6, 3.2   # the arches: at s = +-FS, thickness, opening
PR_ = 2.2                     # the central plinth's radius
CZ = -3.2                     # the crypt's floor


def op(a, s, r):
    """A point on the octagon side facing plan angle a: s along it (anticlockwise), r out from the centre."""
    return (CX + math.cos(a) * r - math.sin(a) * s, CY + math.sin(a) * r + math.cos(a) * s)


def make():
    R = Room('rotunda5', 2, 2, res=2048, lo=-4.0)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.01, T - 0.01, 0, W - T + 0.01, D - T + 0.01, HZ, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(cyl(CX, CY, 0, DZ, RR, 64, side='tile', top='plaster', bottom='terrazzo'))
    R.cut(dome_cap(CX, CY, DZ, RR, DR, 64, 8, 'plaster', 'plaster'))
    outer_wall(R)
    inner_wall(R)
    turning(R)
    floor_rings(R)
    plinth(R)
    crypt(R)
    dressing(R)
    # the turn: the first arch (anticlockwise) sends you back out of the second, walking clockwise
    rm = (AI + AO) / 2
    pa, pb = op(UT, FS, rm), op(UT, -FS, rm)
    tn = (-math.sin(UT), math.cos(UT), 0.0)
    portal(R, P((pa[0], pa[1], 0.0), tn, FW, FH), P((pb[0], pb[1], 0.0), (-tn[0], -tn[1], 0.0), FW, FH))
    # walkers: the cloister, the ambulatory (clockwise), the rotunda
    navloop(R, [(2.4, 2.4), (8.0, 1.9), (16.0, 1.9), (24.0, 1.9), (29.6, 2.4), (30.1, 8.0), (30.1, 16.0), (30.1, 24.0), (29.6, 29.6),
                (24.0, 30.1), (16.0, 30.1), (8.0, 30.1), (2.4, 29.6), (1.9, 24.0), (1.9, 16.0), (1.9, 8.0)])
    ids = {k: R.navpt(*op(math.radians(45 * k), 0.0, rm)) for k in range(8) if k != 1}
    for k in range(2, 8):
        R.link(ids[k], ids[(k + 1) % 8])
    ro = navloop(R, [(CX + 3.8 * math.cos(math.radians(a)), CY + 3.8 * math.sin(math.radians(a))) for a in range(0, 360, 45)])
    for k in (0, 2, 4, 6):
        R.link(ro[k], ids[k])
    secret(R, 10.0, 16.0, CZ, 'The Crypt Under the Medallion',
           'Under the medallion at the centre of the rotunda, a stair goes down to a low crypt: niches of books, a stone table, candles that somebody keeps lit. On the table a book lies open at a plan of the ambulatory, with an arrow going round it one way only.', r=2.2)
    return done(R, 'The Rotunda of the Long Way Round', weight=3, probe=(CX, CY - 4.0, 2.5), top=DZ + DR,
                blurb='A domed rotunda in an octagonal ambulatory. Going round to the right takes a minute. Going round to the left, you keep finding yourself walking back the way you came.')


def outer_wall(R):
    """The ambulatory's outer octagon, with arches out to the cloister on three of its diagonals."""
    t = math.tan(math.radians(22.5))
    for k in range(8):
        a = math.radians(45 * k)
        si, so = AO * t, (AO + AW) * t
        opening = k in (3, 5, 7)
        pieces = [(-1.0, 1.0)] if not opening else [(-1.0, -0.3), (0.3, 1.0)]
        for (f0, f1) in pieces:
            q = [op(a, f0 * si, AO), op(a, f1 * si, AO), op(a, f1 * so, AO + AW), op(a, f0 * so, AO + AW)]
            R.parts.add(poly_prism(q, 0.0, HZ, side='tile', top='tile', bottom='tile'))
        if opening:
            q = [op(a, -0.3 * si, AO), op(a, 0.3 * si, AO), op(a, 0.3 * so, AO + AW), op(a, -0.3 * so, AO + AW)]
            R.parts.add(poly_prism(q, 3.4, HZ, side='tile', top='tile', bottom='tile'))
            for (r_, face) in ((AO, a + math.pi), (AO + AW, a)):
                p = op(a, 0.0, r_)
                R.parts.add(local(architrave(0.6 * si, 3.4, 'walnut', bw=0.2, depth=0.08), face, p[0], p[1], 0))


def inner_wall(R):
    """Between the rotunda's round inside and the ambulatory's octagon: arches on the four axes."""
    for k in range(8):
        a = math.radians(45 * k)
        n = 10
        for i in range(n):
            f0, f1 = -22.5 + 45 * i / n, -22.5 + 45 * (i + 1) / n
            opening = (k % 2 == 0) and -9.1 < (f0 + f1) / 2 < 9.1
            r0a, r0b = math.radians(f0), math.radians(f1)
            q = [(CX + RR * math.cos(a + r0a), CY + RR * math.sin(a + r0a)), (CX + RR * math.cos(a + r0b), CY + RR * math.sin(a + r0b)),
                 op(a, AI * math.tan(r0b), AI), op(a, AI * math.tan(r0a), AI)]
            R.parts.add(poly_prism(q, 3.4 if opening else 0.0, HZ, side='tile', top='tile', bottom='tile'))
        if k % 2 == 0:
            p = op(a, 0.0, AI)
            R.parts.add(local(architrave(2 * AI * math.tan(math.radians(9.0)), 3.4, 'walnut', bw=0.2, depth=0.08), a, p[0], p[1], 0))


def turning(R):
    """Two identical arches across the north-east side of the ambulatory, and books symmetrical about the
    middle between them (it has to look the same turned round)."""
    rm = (AI + AO) / 2
    for s in (FS, -FS - FT_):
        g = Geo()
        # local: x along the side (s), y out (r)
        g.add(box(s, AI, 0, s + FT_, rm - FW / 2, HZ, 'tile', skip=('+z',)))
        g.add(box(s, rm + FW / 2, 0, s + FT_, AO, HZ, 'tile', skip=('+z',)))
        g.add(box(s, rm - FW / 2, FH, s + FT_, rm + FW / 2, HZ, 'tile', skip=('+z',)))
        g.v = [op(UT, x, y) + (z,) for (x, y, z) in g.v]
        g.fix()
        R.parts.add(g)
        for (ss, face) in ((s, UT + math.pi / 2 + math.pi), (s + FT_, UT + math.pi / 2)):
            p = op(UT, ss, rm)
            R.parts.add(local(frame_geo(FW, FH, bw=0.22, depth=0.12, m='walnut', crest=0.8, sill=False), face, p[0], p[1], 0))
    # books on both walls, the same either side of the middle
    for (s0, s1) in ((FS + FT_ + 0.3, 3.2), (-3.2, -FS - FT_ - 0.3)):
        p = op(UT, s1, AO)
        shelf(R, p[0], p[1], 0.0, s1 - s0, UT + math.pi, rows=9, frame='walnut')
        p = op(UT, s0, AI)
        shelf(R, p[0], p[1], 0.0, s1 - s0, UT, rows=9, frame='walnut')
    for s in (-FS - 0.9, 0.0, FS + 0.9):
        p = op(UT, s, rm)
        pendant(R, p[0], p[1], 3.6, HZ, r=0.22)


def floor_rings(R):
    """The rotunda's floor: rings of dark and light marble, each turned a little further than the last,
    so the pattern swirls and does not meet itself."""
    gd, gl = Geo(), Geo()
    nr = 7
    for i in range(nr):
        r0, r1 = PR_ + 0.3 + i * 0.78, PR_ + 0.3 + (i + 1) * 0.78 - 0.05
        off = i * 0.21 + 0.05 * i * i
        n = 12
        for j in range(n):
            a0 = off + 2 * math.pi * j / n
            a1 = a0 + 2 * math.pi / n
            g = gd if j % 2 == 0 else gl
            g.add(ring(CX, CY, 0.0, 0.004 + 0.001 * (i % 2), r0, r1, 4, top='slate' if j % 2 == 0 else 'ivory', bottom='slate', inner='slate', outer='slate', a0=a0, a1=a1))
    R.nocol.add(gd); R.nocol.add(gl)
    R.nocol.add(ring(CX, CY, 0.0, 0.006, RR - 0.35, RR - 0.05, 64, top='brass', bottom='brass', inner='brass', outer='brass'))


def plinth(R):
    """The plinth at the centre: a low round block with a medallion on top, split by a slot from a low door
    on its east side: the stair under the medallion goes down it."""
    y0, y1 = CY - 0.5, CY + 0.5
    xw = CX - 1.7                  # the slot's closed west end
    H = 1.6
    # the two halves either side of the slot, as prisms of the circle's segments
    for (sgn, yy) in ((-1, y0), (1, y1)):
        dy = abs(yy - CY)
        a0 = math.asin(dy / PR_)
        pts = []
        for k in range(21):
            t = (math.pi - 2 * a0) * k / 20 + a0
            ang = t if sgn > 0 else -t
            pts.append((CX + PR_ * math.cos(ang), CY + PR_ * math.sin(ang)))
        R.parts.add(poly_prism(pts, 0.0, H, side='tile', top='tile', bottom='tile'))
    # the west cap across the slot, and the roof over the slot
    xc = CX - math.sqrt(PR_ * PR_ - 0.25)
    R.parts.add(box(xc, y0, 0, xw, y1, H, 'tile'))
    R.parts.add(box(xw, y0, 1.35, CX + math.sqrt(PR_ * PR_ - 0.25), y1, H, 'tile', bottom='tile'))
    # the medallion on top, and a low bronze door-frame on the east
    R.parts.add(cyl(CX, CY, H, H + 0.06, PR_ - 0.15, 32, side='gilt', top='gilt', bottom='gilt'))
    R.parts.add(cyl(CX, CY, H + 0.06, H + 0.16, 0.6, 16, side='bronze', top='bronze', bottom='bronze'))
    R.parts.add(local(architrave(1.0, 1.35, 'bronze', bw=0.08, depth=0.05, cornice=False), 0.0, CX + PR_ - 0.02, CY, 0))
    # the hole and the stair down (under the medallion), and the passage on to the crypt
    R.cut(box(xw, y0, CZ, CX + PR_ + 0.05, y1, 0.05, 'tile', bottom='floor', top='tile'))
    R.cut(box(CX - 4.6, y0, CZ, xw + 0.01, y1, -0.25, 'tile', bottom='floor', top='tile'))
    R.flight(CX + PR_ - 16 * 0.3, y0, CZ, 1.0, 16, -CZ / 16, 0.3, '+x', m='tile', riser='tile', side='tile')


def crypt(R):
    x0, x1, y0, y1 = 7.6, CX - 4.5, 12.6, 19.4
    R.cut(box(x0, y0, CZ, x1, y1, -0.5, 'tile', bottom='floor', top='plaster'))
    for (face, bk, a, b) in (('+x', x0, y0 + 0.2, y1 - 0.2), ('+y', y0, x0 + 0.2, x1 - 0.2), ('-y', y1, x0 + 0.2, x1 - 0.2)):
        sh(R, face, bk, a, b, z=CZ, rows=5, frame='walnut')
    R.parts.add(box(9.3, 15.3, CZ, 10.9, 16.7, CZ + 0.85, 'tile', top='slate'))
    open_book(R, 10.1, 16.0, CZ + 0.85, ang=math.pi / 2)
    candles(R, [(9.5, 15.5, CZ + 0.85), (10.7, 16.5, CZ + 0.85), (9.45, 16.55, CZ + 0.85), (8.0, 13.0, CZ), (8.0, 19.0, CZ)], rng(7), 0.15, 0.45, 0.025, 0.05)
    R.spot('plaque', 9.0, 16.0, CZ + 1.4, 0.0, text='This way round only.')
    R.parts.add(lchair(11.5, 16.0, math.pi)); R.spot('sit', 11.5, 16.0, CZ + 0.48, math.pi)


def dressing(R):
    rows = 11
    # the cloister's outer walls
    for (a, b) in ((0.8, 6.3), (9.7, 22.3), (25.7, W - 0.8)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut'); sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
        sh(R, '+x', T, a, b, rows=rows, frame='walnut'); sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    # the ambulatory: books on the outer wall (where there is no arch), lamps
    t = math.tan(math.radians(22.5))
    for k in range(8):
        a = math.radians(45 * k)
        if k == 1:
            continue
        L = AO * t
        spans = [(-L + 0.3, -1.9 - 0.3), (1.9 + 0.3, L - 0.3)] if k in (3, 5, 7) else [(-L + 0.3, L - 0.3)]
        for (s0, s1) in spans:
            p = op(a, s1, AO)
            shelf(R, p[0], p[1], 0.0, s1 - s0, a + math.pi, rows=9, frame='walnut')
        p = op(a, 0.0, (AI + AO) / 2)
        if k != 1:
            pendant(R, p[0], p[1], 3.6, HZ, r=0.22)
    # the rotunda: books round the drum between the arches, tables, lamps, an oculus
    for k in (1, 3, 5, 7):
        a = math.radians(45 * k)
        for i in range(3):
            t0, t1 = a - math.radians(34) + math.radians(68) * i / 3, a - math.radians(34) + math.radians(68) * (i + 1) / 3
            p0 = (CX + (RR - 0.02) * math.cos(t0), CY + (RR - 0.02) * math.sin(t0))
            p1 = (CX + (RR - 0.02) * math.cos(t1), CY + (RR - 0.02) * math.sin(t1))
            L = math.dist(p0, p1) - 0.08
            tm = (t0 + t1) / 2
            face = tm + math.pi
            shelf(R, p0[0] + math.cos(face - math.pi / 2) * 0.04, p0[1] + math.sin(face - math.pi / 2) * 0.04, 0.0, L, face, rows=12, frame='walnut')
    R.light(cyl(CX, CY, DZ + DR - 0.04, DZ + DR - 0.01, 1.3, 24, side='e_sky', top='e_sky', bottom='e_sky'))
    chandelier(R, CX, CY, 4.3, 1.6, n=12, chain=DZ + DR - 0.05)
    for k in (1, 3, 5, 7):
        a = math.radians(45 * k)
        x, y = CX + 5.4 * math.cos(a), CY + 5.4 * math.sin(a)
        R.parts.add(ltable(-1.0, -0.45, 1.0, 0.45, top='leather').xform(a + math.pi / 2, x, y, 0))
        for dx in (-0.5, 0.5):
            llamp(R, x + math.cos(a + math.pi / 2) * dx, y + math.sin(a + math.pi / 2) * dx, 0.76, a=a + math.pi / 2)
    for (x, y) in ((2.4, 2.4), (29.6, 2.4), (2.4, 29.6), (29.6, 29.6)):
        pendant(R, x, y, 3.6, HZ, r=0.26)
        lantern(R, x + (0.8 if x < 16 else -0.8), y, 0.0)
    for (x, y) in ((16.0, 1.9), (16.0, 30.1), (1.9, 16.0), (30.1, 16.0)):
        pendant(R, x, y, 3.6, HZ, r=0.26)
