"""The Penrose Balcony: a triangular balcony round a deep, book-lined well, stepping up on all three sides.
At the end of the third side it arrives over the start of the first, four and a half metres up, and a
plain opening there lets you step down onto the first step again without going down: it rises for ever.
The well below is lined with shelves in tiers, all the way to a floor nobody can reach. Under the second
landing a hatch lets you down into a room in the well wall, with a window onto the well."""
from kit_h11 import *

W = D = 32.0
CX, CY = 16.0, 15.2
RI, RO, RW = 4.6, 7.0, 7.4       # inner edge (the well), outer edge (the wall's face), wall back
UZ = 8.0                         # the upper floor, and the balcony's lowest point
HS = 1.5                         # rise per side
NST, RUNS = 10, 1.1              # steps per side
LF = NST * RUNS                  # a side's flight (11 m)
ZT = 2 * LH - 0.4                # the ceiling
GH = 2.6                         # the opening at the top
SQ3 = math.sqrt(3.0)
NRM = [(0.0, -1.0), (math.cos(math.pi / 6), math.sin(math.pi / 6)), (math.cos(5 * math.pi / 6), math.sin(5 * math.pi / 6))]
TAN = [(-n[1], n[0]) for n in NRM]
HAT = (-9.65, -5.9, 6.0, RO - 0.04)   # the hatch in corner 1's deck (side 1's strip): s0, s1, r0, r1
RZ = 7.0                          # the hidden room's floor
WIN = (-7.1, -6.2)   # its window onto the well (side 1's strip, s range)
X0, X1 = 6.2, 8.0                 # the way out at corner 1 (side 0's wall)


def sp(k, s, r):
    """A point in side k's strip frame: s along the way you walk, r out from the centre."""
    t, n = TAN[k], NRM[k]
    return (CX + t[0] * s + n[0] * r, CY + t[1] * s + n[1] * r)


def zc(j):
    """Height of corner j (0 = the start/end)."""
    return UZ + j * HS


def make():
    R = Room('penrose', 2, 2, levels=2, res=2048)
    skip = [(s, i, 0) for s in 'SN' for i in range(2)] + [(s, j, 0) for s in 'WE' for j in range(2)]
    seal(R, skip, floor='floor', wall='tile')
    R.cut(box(T - 0.01, T - 0.01, UZ, W - T + 0.01, D - T + 0.01, ZT, 'tile', bottom='floor', top='plaster'))
    tri = [sp(k, -SQ3 * RW, RW) for k in range(3)]
    R.cut(poly_prism(tri, 0.0, ZT, side='tile', top='plaster', bottom='terrazzo'))
    walls(R)
    balcony(R)
    well(R)
    hidden(R)
    upper_floor(R)
    # the portal: the top of the third side opens onto the foot of the first, 4.5 m below
    mid_a = sp(0, -LF / 2, (RI + RO) / 2)
    portal(R, P((mid_a[0], mid_a[1], zc(3)), (TAN[0][0], TAN[0][1], 0), RO - RI, GH), P((mid_a[0], mid_a[1], zc(0)), (TAN[0][0], TAN[0][1], 0), RO - RI, GH))
    # walkers: round the upper floor, and once round the balcony
    navloop(R, [(2.2, 2.2), (16.0, 2.6), (29.8, 2.2), (29.0, 16.0), (26.0, 29.5), (16.0, 31.0 - 0.8), (6.0, 29.5), (3.0, 16.0)], z=UZ)
    m = (RI + RO) / 2
    pts = [(sp(0, -4.3, m + 0.4), 8.2), (sp(0, LF / 2 + 0.6, m), zc(1)), (sp(1, -LF / 2 - 0.6, m), zc(1)),
           (sp(1, LF / 2 + 0.6, m), zc(2)), (sp(2, -LF / 2 - 0.6, m), zc(2)), (sp(2, LF / 2 + 0.6, m), zc(3))]
    ids = [R.navpt(p[0], p[1], z) for (p, z) in pts]
    R.link(*ids)
    g = R.navpt(sp(0, -4.3, RW + 1.6)[0], sp(0, -4.3, RW + 1.6)[1], UZ)
    R.link(g, ids[0])
    hc = sp(1, -7.6, RI + 0.8)
    secret(R, hc[0], hc[1], RZ, 'The Room in the Well Wall',
           'Under the second landing a hatch, and under the hatch a ladder, and at the foot of the ladder a room let into the wall of the well, with a desk at a little window. From here you can see the balcony going round above you, up and up and never higher.', r=1.8)
    fx(R, 'dust', [CX - 5.0, CY - 3.0, 0.5, CX + 5.0, CY + 6.0, 14.5])
    return done(R, 'The Penrose Balcony', weight=3, probe=(CX, CY, 10.0), top=ZT,
                blurb='A balcony goes round a deep well of books, and it climbs a step at a time on every side. After the third side you are back at the first. It is still climbing. So are you.')


# ---------------------------------------------------------------------------
def walls(R):
    """The triangle's outer wall (with the way in at corner 0) and the solid under the balcony."""
    for k in range(3):
        a0, a1 = -SQ3 * RO, SQ3 * RO
        if k == 0:
            # the way in: an opening in side 0's wall near corner 0
            e0, e1 = -LF / 2 + 0.3, -LF / 2 + 2.1
            for (s0, s1) in ((-SQ3 * RW, e0), (e1, X0), (X1, SQ3 * RW)):
                R.parts.add(poly_prism([sp(k, s0 if s0 > -SQ3 * RW else -SQ3 * RO, RO), sp(k, s1 if s1 < SQ3 * RW else SQ3 * RO, RO),
                                        sp(k, s1, RW), sp(k, s0, RW)], 0.0, ZT, side='tile', top='tile', bottom='tile'))
            R.parts.add(poly_prism([sp(k, e0, RO), sp(k, e1, RO), sp(k, e1, RW), sp(k, e0, RW)], UZ + GH + 0.2, ZT))
            R.parts.add(poly_prism([sp(k, e0, RO), sp(k, e1, RO), sp(k, e1, RW), sp(k, e0, RW)], 0.0, UZ))
            R.parts.add(local(architrave(e1 - e0, GH + 0.2, 'walnut', bw=0.2, depth=0.1), math.atan2(NRM[0][1], NRM[0][0]), *sp(0, (e0 + e1) / 2, RW), UZ))
            # the way out, from corner 1 (z 9.5): a door, a landing and a few steps down outside
            z1 = zc(1)
            R.parts.add(poly_prism([sp(k, X0, RO), sp(k, X1, RO), sp(k, X1, RW), sp(k, X0, RW)], z1 + 2.4, ZT))
            R.parts.add(poly_prism([sp(k, X0, RO), sp(k, X1, RO), sp(k, X1, RW), sp(k, X0, RW)], 0.0, z1))
            R.parts.add(local(architrave(X1 - X0, 2.4, 'walnut', bw=0.2, depth=0.1), math.atan2(NRM[0][1], NRM[0][0]), *sp(0, (X0 + X1) / 2, RW), z1))
            ox0, oy1 = sp(0, X0 - 0.3, RW)
            ox1 = ox0 + 2.5
            R.parts.add(box(ox0, oy1 - 2.3, UZ, ox1, oy1, z1, 'tile', top='terrazzo'))
            flight(R, ox1 + 8 * 0.3, oy1 - 2.3, UZ, 2.3, 8, HS / 8, 0.3, '-x', m='terrazzo', rails='L')
            rail(R, ox0 + 0.06, oy1 - 2.24, ox1, oy1 - 2.24, z=z1, h=1.0)
            rail(R, ox0 + 0.06, oy1 - 2.24, ox0 + 0.06, oy1, z=z1, h=1.0)
        else:
            R.parts.add(poly_prism([sp(k, a0, RO), sp(k, a1, RO), sp(k, SQ3 * RW, RW), sp(k, -SQ3 * RW, RW)], 0.0, ZT, side='tile', top='tile', bottom='tile'))


def strip_poly(k, s0, s1, r0, r1):
    return [sp(k, s0, r0), sp(k, s1, r0), sp(k, s1, r1), sp(k, s0, r1)]


def piece_a(k, r0=RI, r1=RO, s_from=LF / 2):
    """The end of side k's strip beyond its flight, up to the bisector at the next corner."""
    return [sp(k, s_from, r0), sp(k, SQ3 * r0, r0), sp(k, SQ3 * r1, r1), sp(k, s_from, r1)]


def piece_b(k, r0=RI, r1=RO, s_to=-LF / 2):
    """The start of side k's strip before its flight, back to the bisector at its first corner."""
    return [sp(k, -SQ3 * r0, r0), sp(k, s_to, r0), sp(k, s_to, r1), sp(k, -SQ3 * r1, r1)]


def slab(R, pts, z, th=0.3, fill_to=None):
    z0 = z - th if fill_to is None else fill_to
    R.parts.add(poly_prism(pts, z0, z, side='tile', top='terrazzo', bottom='plaster'))


def balcony(R):
    rs = rng(11)
    for k in range(3):
        z0 = zc(k)
        # the flight (solid below), running the middle of the side
        x, y = sp(k, -LF / 2, (RI + RO) / 2)
        ang = math.atan2(TAN[k][1], TAN[k][0])
        flight_at(R, x, y, z0, ang, RO - RI, NST, HS / NST, RUNS, m='terrazzo', side='tile', solid_to=0.0)
        # landings: the end of this side (piece a) belongs to the next corner
        if k == 1:
            slab(R, piece_a(1), zc(2), fill_to=0.0)
        if k == 2:
            slab(R, piece_b(2), zc(2), fill_to=0.0)
        # bookcases on the outer wall, one per step
        for i in range(NST):
            s0 = -LF / 2 + i * RUNS + 0.05
            zz = z0 + (i + 1) * HS / NST
            p = sp(k, s0, RO)
            shelf(R, p[0], p[1], zz, RUNS - 0.1, math.atan2(-NRM[k][1], -NRM[k][0]), rows=7, frame='walnut')
        # rails on the well side: flat, sloped, flat
        rin = RI + 0.07
        seg_rail(R, (*sp(k, -LF / 2, rin), z0 + HS / NST), (*sp(k, LF / 2, rin), z0 + HS), h=1.0)
        seg_rail(R, (*sp(k, LF / 2, rin), zc(k + 1)), (*sp(k, SQ3 * RI + 0.12, rin), zc(k + 1)), h=1.0)
        if k != 0:
            seg_rail(R, (*sp(k, -SQ3 * RI - 0.12, rin), z0), (*sp(k, -LF / 2, rin), z0), h=1.0)
        # a lamp over every third step
        for s in (-LF / 2 + 1.5, 0.0, LF / 2 - 1.5):
            p = sp(k, s, RO - 0.25)
            sconce(R, p[0], p[1], z0 + HS * (s + LF / 2) / LF + 3.3, math.atan2(-NRM[k][1], -NRM[k][0]))
    # corner 0, lower: where you come in (solid below); upper: over it, the end of the third side
    slab(R, piece_b(0), zc(0), fill_to=0.0)
    slab(R, piece_a(2, s_from=LF / 2), zc(0), fill_to=0.0)
    slab(R, piece_a(2), zc(3))
    slab(R, piece_b(0), zc(3))
    # past the opening at the top: the recess, closed in (over the first steps of the first side)
    rec = strip_poly(0, -LF / 2, -LF / 2 + 1.1, RI, RO)
    slab(R, rec, zc(3))
    R.parts.add(poly_prism(strip_poly(0, -LF / 2, -LF / 2 + 1.3, RI - 0.3, RI), zc(3) - 0.3, zc(3) + GH + 0.4))
    R.parts.add(poly_prism(strip_poly(0, -LF / 2 + 1.1, -LF / 2 + 1.3, RI, RO), zc(3) - 0.3, zc(3) + GH + 0.4))
    R.parts.add(poly_prism(strip_poly(0, -LF / 2, -LF / 2 + 1.3, RI, RO), zc(3) + GH, zc(3) + GH + 0.4))
    # the opening's surround, the same at the top and at the foot
    fa = math.atan2(-TAN[0][1], -TAN[0][0])
    for z in (zc(0), zc(3)):
        R.parts.add(local(architrave(RO - RI, GH, 'walnut', bw=0.18, depth=0.08, cornice=False), fa, *sp(0, -LF / 2, (RI + RO) / 2), z))
    R.parts.add(local(architrave(RO - RI, GH, 'walnut', bw=0.18, depth=0.08, cornice=False), fa + math.pi, *sp(0, -LF / 2, (RI + RO) / 2), zc(0)))
    # rails round the corner-0 landings (both levels) on the well side
    rin = RI + 0.07
    seg_rail(R, (*sp(0, -SQ3 * RI - 0.12, rin), zc(3)), (*sp(0, -LF / 2, rin), zc(3)), h=1.0)
    # the lower landing is closed in: a portal must never be seen from behind, and this is behind the foot's
    R.parts.add(poly_prism(strip_poly(0, -SQ3 * (RI + 0.25) - 0.05, -LF / 2, RI, RI + 0.25), zc(0), zc(3) - 0.3))
    R.parts.add(poly_prism(strip_poly(2, LF / 2, SQ3 * (RI + 0.25) + 0.05, RI, RI + 0.25), zc(0), zc(3) - 0.3))
    # the upper landing at corner 0 is a hanging slab: brackets under it
    for s in (-LF / 2 - 0.6, -SQ3 * RI):
        p = sp(0, s, RO - 0.15)
        R.parts.add(box(p[0] - 0.15, p[1] - 0.15, zc(3) - 1.4, p[0] + 0.15, p[1] + 0.15, zc(3) - 0.3, 'tile'))


def well(R):
    """The well: tiers of shelves on its three walls down to a floor far below."""
    rs = rng(4)
    tiers = [(0.0, 6), (2.75, 6), (5.5, 5)]
    for k in range(3):
        a = math.atan2(-NRM[k][1], -NRM[k][0])       # facing into the well
        L = 2 * SQ3 * RI
        n = 4
        for (z, rows) in tiers:
            for i in range(n):
                s0 = -L / 2 + 0.9 + i * (L - 1.8) / n
                p = sp(k, s0 + 0.08, RI)
                shelf(R, p[0], p[1], z, (L - 1.8) / n - 0.16, a, rows=rows, frame='walnut')
            if z > 0:
                # a narrow ledge with a brass rail in front of each tier (seen from above)
                R.parts.add(poly_prism(strip_poly(k, -L / 2 + 0.5, L / 2 - 0.5, RI - 0.75, RI), z - 0.15, z, side='walnut', top='oak', bottom='walnut'))
                p0, p1 = sp(k, -L / 2 + 0.6, RI - 0.7), sp(k, L / 2 - 0.6, RI - 0.7)
                R.nocol.add(obox(p0[0], p0[1], p1[0], p1[1], z + 0.9, z + 0.95, 0.05, 'brass'))
                for t in range(9):
                    q = sp(k, -L / 2 + 0.6 + (L - 1.2) * t / 8, RI - 0.7)
                    R.nocol.add(box(q[0] - 0.02, q[1] - 0.02, z, q[0] + 0.02, q[1] + 0.02, z + 0.9, 'brass', skip=('-z', '+z')))
                for s in (-L / 4, L / 4):
                    q = sp(k, s, RI - 0.2)
                    lantern(R, q[0], q[1], z + 0.05, m='e_amber')
    # the floor of the well: a star of marble and a lamp, far down
    R.nocol.add(poly_prism([(CX + 2.2 * math.cos(a), CY + 2.2 * math.sin(a)) for a in (math.pi / 2, math.pi / 2 + 2.094, math.pi / 2 + 4.189)], 0.0, 0.01, side='gilt', top='gilt', bottom='gilt'))
    R.parts.add(ltable(CX - 0.8, CY - 0.4, CX + 0.8, CY + 0.4, top='leather'))
    llamp(R, CX, CY, 0.76)
    R.nocol.add(lchair(CX, CY - 0.9, math.pi / 2))
    candles(R, [(CX + 1.6, CY + 0.5, 0.0), (CX - 1.5, CY + 0.9, 0.0), (CX + 0.2, CY - 1.9, 0.0)], rs, 0.2, 0.5, 0.03, 0.05)
    # light from above: a skylight over the well
    tri = [sp(k, -SQ3 * (RI - 0.5), RI - 0.5) for k in range(3)]
    R.light(poly_prism(tri, ZT - 0.03, ZT, side='e_sky', top='e_sky', bottom='e_sky'))
    tri2 = [sp(k, -SQ3 * (RI + 1.2), RI + 1.2) for k in range(3)]
    R.nocol.add(poly_prism(tri2, ZT - 0.5, ZT, side='plaster', top='plaster', bottom='plaster'))


def hidden(R):
    """Corner 1's landing, built round a room: a hatch in its deck, a ladder down, a window on the well."""
    z1 = zc(1)
    # the room's floor (solid below), walls on the well side with a window, the deck above with a hatch
    slab(R, piece_b(1), RZ, fill_to=0.0)
    s_lo = -SQ3 * RI
    wall = [(-SQ3 * (RI + 0.4), WIN[0]), (WIN[1], -LF / 2)]
    for (a, b) in wall:
        R.parts.add(poly_prism(strip_poly(1, a, b, RI, RI + 0.35), RZ, z1 - 0.3))
    R.parts.add(poly_prism(strip_poly(1, WIN[0], WIN[1], RI, RI + 0.35), RZ, RZ + 0.9))
    R.parts.add(poly_prism(strip_poly(1, WIN[0], WIN[1], RI, RI + 0.35), RZ + 1.7, z1 - 0.3))
    # corner 1's other half (the end of side 0) stays solid up to the deck, closing the room's end
    slab(R, piece_a(0), z1, fill_to=0.0)
    # the bisector wall between the two halves is the solid of piece a; the deck over piece b with a hole
    s0, s1, r0, r1 = HAT
    for pts in (piece_b(1, s_to=s0), strip_poly(1, s0, -LF / 2, RI, r0), strip_poly(1, s0, -LF / 2, r1, RO), strip_poly(1, s1, -LF / 2, r0, r1)):
        slab(R, pts, z1)
    # a narrow stair down through the hatch, along the outer wall, with a rail on its open side
    n_ = 13
    top = flight_at(R, *sp(1, s1 - n_ * 0.28, (r0 + r1) / 2), RZ, math.atan2(TAN[1][1], TAN[1][0]), r1 - r0, n_, (z1 - RZ) / n_, 0.28, m='oak', side='walnut')
    seg_rail(R, (*sp(1, s1 - n_ * 0.28 + 0.1, r0 + 0.06), RZ + 0.25), (*sp(1, s1, r0 + 0.06), z1), h=1.0)
    seg_rail(R, (*sp(1, s1, r0 - 0.06), z1), (*sp(1, s0 + 0.9, r0 - 0.06), z1), h=1.0)
    # the hatch's lid, folded back against the wall
    lid = strip_poly(1, s1 - 1.0, s1 - 0.1, RO - 0.1, RO - 0.04)
    R.parts.add(poly_prism(lid, z1, z1 + 0.85, side='brass', top='brass', bottom='brass'))
    # inside: a desk at the window, a lamp, a chair
    fa = math.atan2(-NRM[1][1], -NRM[1][0])
    sc = (WIN[0] + WIN[1]) / 2
    dk = sp(1, sc, RI + 0.62)
    R.parts.add(ltable(-0.45, -0.25, 0.45, 0.25, top='leather').xform(fa - math.pi / 2, dk[0], dk[1], RZ))
    llamp(R, *sp(1, sc + 0.25, RI + 0.55), RZ + 0.76, a=fa - math.pi / 2, m='e_amber')
    open_book(R, *sp(1, sc - 0.15, RI + 0.65), RZ + 0.76, ang=fa - math.pi / 2)
    ch = sp(1, sc, RI + 1.15)
    R.parts.add(lchair(ch[0], ch[1], fa).xform(0, 0, 0, RZ))
    R.spot('sit', ch[0], ch[1], RZ + 0.48, fa)
    R.spot('plaque', *sp(1, -8.2, RI + 0.4), RZ + 1.4, fa, text='Every step up. Count them if you like.')
    bl = sp(1, -7.8, RI + 0.6)
    bulb(R, bl[0], bl[1], z1 - 0.8, r=0.07, m='e_dim', top=z1 - 0.3)


def upper_floor(R):
    """The floor round the triangle: books on the room's walls and the triangle's faces, tables, lamps."""
    rows = 15
    for (a, b) in ((0.8, 6.3), (9.7, 22.3), (25.7, W - 0.8)):
        sh(R, '+y', T, a, b, z=UZ, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, z=UZ, rows=rows, frame='walnut')
        sh(R, '+x', T, a, b, z=UZ, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, z=UZ, rows=rows, frame='walnut')
    for k in (1, 2):
        a = math.atan2(NRM[k][1], NRM[k][0])
        for (s0, s1) in ((-9.5, -2.0), (2.0, 9.5)):
            p = sp(k, s1, RW)
            shelf(R, p[0], p[1], UZ, s1 - s0, a, rows=12, frame='walnut')
    for (x, y) in ((6.0, 3.6), (26.0, 3.6), (4.0, 22.0), (28.0, 22.0)):
        R.parts.add(ltable(x - 1.0, y - 0.5, x + 1.0, y + 0.5, top='leather').xform(0, 0, 0, UZ))
        llamp(R, x, y, UZ + 0.76)
    for (x, y) in ((4.0, 3.2), (16.0, 3.2), (28.0, 3.2), (3.5, 16.0), (28.5, 16.0), (8.0, 28.0), (24.0, 28.0)):
        pendant(R, x, y, UZ + 5.0, ZT, r=0.3)
    for (x, y) in ((1.2, 1.2), (W - 1.2, 1.2)):
        lantern(R, x, y, UZ)
