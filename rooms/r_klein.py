"""The Klein Bottle: in a two-storey atrium stands a bottle of brass hoops the size of a house, lined with
books inside. Its neck rises from its crown, arcs over and comes down to the upper gallery: walk up the
neck from the gallery, and at the top of it a brass gate lets you out inside the bottle's own base, having
passed through its wall. The bottle's plinth holds a brass capsule of a reading room, behind a bookcase."""
from kit_h11 import *
from kit_h6 import cage_tube

W = D = 32.0
UZ = 8.0
ZT = 2 * LH - 0.4
V0, V1 = 5.0, 27.0            # the atrium
BX, BY = 16.0, 13.6           # the bottle's axis
PZ = 2.4                      # its floor (the plinth's top)
PR = 4.3                      # the plinth's radius
PROF = [(4.3, 2.4), (5.3, 3.3), (5.95, 4.6), (6.15, 6.1), (5.85, 7.6), (5.0, 8.9), (3.8, 9.9), (2.5, 10.5), (1.7, 10.9)]
GW, GH = 1.8, 2.6             # the gates
NZ = 12.0                     # the neck's top landing
NY0, NY1 = 20.4, 27.4         # the neck's flight (y), climbing south from the gallery
AY = 19.6                     # gate at the neck's top (you walk south into it)
BGY = 16.9                    # its twin, inside the bottle (you come out walking south)
CR = 2.5                      # the capsule's radius (inside the plinth)


def make():
    R = Room('klein', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    halls(R)
    plinth(R)
    bottle(R)
    neck(R)
    capsule(R)
    stair(R)
    dressing(R)
    portal(R, P((BX, AY, NZ), (0, -1, 0), GW, GH), P((BX, BGY, PZ), (0, -1, 0), GW, GH))
    navloop(R, [(2.6, 2.6), (16.0, 2.6), (29.4, 2.6), (29.4, 16.0), (29.4, 29.4), (16.0, 29.4), (2.6, 29.4), (2.6, 16.0)])
    navloop(R, [(2.6, 2.6), (16.0, 2.6), (29.4, 2.6), (29.4, 16.0), (29.4, 29.4), (16.0, 29.4), (2.6, 29.4), (2.6, 16.0)], z=UZ)
    a, b, c = R.navpt(16.0, 3.6), R.navpt(16.0, 11.0, PZ), R.navpt(14.0, 14.5, PZ)
    R.link(a, b, c)
    d, e = R.navpt(16.0, 29.0, UZ), R.navpt(16.0, 21.2, NZ)
    R.link(d, e)
    secret(R, BX, BY, 0.0, 'The Brass Capsule',
           'Inside the bottle\'s plinth, behind a bookcase that swings like a page, a round brass room with a desk, a lamp and a chair, riveted all over like the inside of a diving bell. Above you, through the floor, you can hear people going round and round.', r=1.8)
    fx(R, 'dust', [BX - 6.0, BY - 6.0, 2.5, BX + 6.0, BY + 6.0, 13.5])
    return done(R, 'The Klein Bottle', weight=3, probe=(16.0, 6.0, 9.0), top=ZT,
                blurb='A bottle of brass hoops the size of a house stands in the atrium, lined with books inside. Its neck climbs out of its crown and comes down again to the gallery. If you walk up the neck, you come out inside the bottle. You never went through the wall. You went through the wall.')


def halls(R):
    R.cut(box(T - 0.01, T - 0.01, 0, W - T + 0.01, D - T + 0.01, TOP, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.01, T - 0.01, UZ, W - T + 0.01, D - T + 0.01, ZT, 'tile', bottom='floor', top='plaster'))
    R.cut(box(V0, V0, 0, V1, V1, ZT, 'tile', bottom='terrazzo', top='plaster'))
    # the gallery's edge: rail, open where the stair and the neck arrive
    rect_rails(R, V0, V0, V1, V1, UZ, opens={'W': [(10.4, 12.1)], 'N': [(BX - 1.0, BX + 1.0)]}, inset=-0.08)
    # piers under the gallery's edge, and a glass roof of brass and sky
    for t in (V0, 10.5, 21.5, V1):
        for (x, y) in ((t, V0 - 0.3), (t, V1 + 0.3), (V0 - 0.3, t), (V1 + 0.3, t)):
            R.parts.add(box(x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, TOP, 'tile', skip=('-z', '+z')))
    for i in range(5):
        for j in range(5):
            x0, y0 = V0 + 0.3 + i * 4.4, V0 + 0.3 + j * 4.4
            R.light(box(x0, y0, ZT - 0.03, x0 + 4.0, y0 + 4.0, ZT, 'e_sky'))
    for t in [V0 + 0.1 + i * 4.4 for i in range(6)]:
        R.nocol.add(box(t - 0.1, V0, ZT - 0.4, t + 0.1, V1, ZT, 'brass', skip=('+z',)))
        R.nocol.add(box(V0, t - 0.1, ZT - 0.4, V1, t + 0.1, ZT, 'brass', skip=('+z',)))


def plinth(R):
    """A round stone plinth (the capsule inside it), a flight up its south side, the bottle's floor on top."""
    n = 48
    # leave the way into the capsule (west) open: rebuild the ring in two arcs
    gap = math.asin(0.55 / CR)
    R.parts.add(ring(BX, BY, 0, PZ - 0.3, CR, PR, 40, top='tile', bottom='tile', inner='brass', outer='tile', a0=math.pi + gap, a1=3 * math.pi - gap))
    R.parts.add(cyl(BX, BY, PZ - 0.3, PZ, PR, n, side='tile', top='terrazzo', bottom='brass'))
    R.parts.add(cyl(BX, BY, PZ - 0.02, PZ, PR + 0.12, n, side='brass', top='brass', bottom='brass'))
    # the flight up the south side, railed
    R.flight(BX - 1.0, BY - PR - 4.2 + 0.1, 0.0, 2.0, 12, PZ / 12, 0.35, '+y', m='terrazzo', riser='tile', side='tile')
    for x in (BX - 0.94, BX + 0.94):
        seg_rail(R, (x, BY - PR - 4.1, PZ / 12), (x, BY - PR + 0.05, PZ), h=1.0)
    # the plinth's face: bookcases round it (one of them false, over the way into the capsule)
    for (a0, a1, solid) in ((math.pi * 0.62, math.pi * 0.9, True), (math.pi * 0.9, math.pi * 1.1, False), (math.pi * 1.1, math.pi * 1.4, True),
                            (-math.pi * 0.36, math.pi * 0.36, True)):
        k = max(1, int((a1 - a0) * PR / 1.4))
        for i in range(k):
            t0, t1 = a0 + (a1 - a0) * i / k, a0 + (a1 - a0) * (i + 1) / k
            p1 = (BX + (PR + 0.02) * math.cos(t1), BY + (PR + 0.02) * math.sin(t1))
            p0 = (BX + (PR + 0.02) * math.cos(t0), BY + (PR + 0.02) * math.sin(t0))
            L = math.dist(p0, p1) - 0.06
            tm = (t0 + t1) / 2
            shelf(R, p1[0], p1[1], 0.0, L, tm, rows=4, frame='walnut', solid=solid)


def bottle(R):
    """The brass cage of the bottle, books on its inside, and lamps hanging in it."""
    n = 16
    rib = Geo()
    for k in range(n):
        a = 2 * math.pi * k / n
        if abs(math.sin(a / 2 - math.pi / 4)) < 1e-9: pass
        ca, sa = math.cos(a), math.sin(a)
        pts = [(BX + r * ca, BY + r * sa, z) for (r, z) in PROF]
        skip_low = abs(a - 3 * math.pi / 2) < 0.3        # the way in (south) is open below 5 m
        for i in range(len(pts) - 1):
            if skip_low and pts[i + 1][2] < 5.0: continue
            rib.add(beam(pts[i], pts[i + 1], 0.09, 'brass', 0.14))
    # hoops of latitude
    for (r, z) in PROF[1:-1:2] + [PROF[-1]]:
        a0, a1 = (-math.pi / 2 + 0.33, 3 * math.pi / 2 - 0.33) if z < 5.0 else (0.0, 2 * math.pi)
        rib.add(ring(BX, BY, z - 0.05, z + 0.05, r - 0.06, r + 0.02, 40, top='brass', bottom='brass', inner='brass', outer='brass', a0=a0, a1=a1))
    R.nocol.add(rib)
    # books lining the inside of the cage, in bands between the hoops
    rs = rng(33)
    bands = {}
    for (i0, i1) in ((1, 2), (2, 3), (3, 4), (4, 5)):
        (r0, z0), (r1, z1) = PROF[i0], PROF[i1]
        for k in range(24):
            a = 2 * math.pi * (k + 0.5) / 24
            if z0 < 5.0 and abs(a - 3 * math.pi / 2) < 0.45: continue
            da = 2 * math.pi / 24 * 0.92
            ca, sa = math.cos(a - da / 2), math.sin(a - da / 2)
            p0 = (BX + (r0 - 0.08) * ca, BY + (r0 - 0.08) * sa, z0 + 0.06)
            q1 = (BX + (r0 - 0.08) * math.cos(a + da / 2), BY + (r0 - 0.08) * math.sin(a + da / 2), z0 + 0.06)
            du = [q1[i] - p0[i] for i in range(3)]; L = math.sqrt(sum(c * c for c in du)); du = [c / L for c in du]
            up = [(r1 - r0) * math.cos(a), (r1 - r0) * math.sin(a), z1 - z0]; lu = math.sqrt(sum(c * c for c in up)); dv = [c / lu for c in up]
            dn = [-math.cos(a), -math.sin(a), 0.0]
            # a board under each band
            merge_bands(bands, book_band(p0, du, dv, dn, L, min(0.9, lu * 0.9), rs, seg=(0.06, 0.2), depth=0.03))
    add_bands(R, bands)
    # bookcases round the bottle's floor, inside (leaving the way in and the gate clear)
    arc_shelf_(R, BX, BY, PR - 0.15, -math.pi / 2 + 0.55, math.pi / 2 - 0.45, 4, PZ, 5)
    arc_shelf_(R, BX, BY, PR - 0.15, math.pi / 2 + 0.45, 3 * math.pi / 2 - 0.55, 4, PZ, 5)
    gate(R, BX, BGY, PZ, math.pi / 2)
    # a chandelier inside, and a table
    chandelier(R, BX, BY, 7.6, 1.2, n=10, chain=10.9)
    R.parts.add(ltable(BX - 0.9, BY - 1.2, BX + 0.9, BY - 0.4, top='leather').xform(0, 0, 0, PZ))
    llamp(R, BX - 0.4, BY - 0.8, PZ + 0.76)
    open_book(R, BX + 0.3, BY - 0.8, PZ + 0.76)


def arc_shelf_(R, cx, cy, r, a0, a1, n, z, rows):
    for k in range(n):
        t0 = a0 + (a1 - a0) * k / n; t1 = a0 + (a1 - a0) * (k + 1) / n
        p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0)); p1 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
        L = math.dist(p0, p1) - 0.08
        tm = (t0 + t1) / 2
        face = tm + math.pi
        run = face - math.pi / 2
        shelf(R, p0[0] + math.cos(run) * 0.04, p0[1] + math.sin(run) * 0.04, z, L, face, rows=rows, frame='walnut')


def gate(R, x, y, z, face):
    """A brass gate: a rectangular opening in a ring of hoops."""
    R.parts.add(local(frame_geo(GW, GH, bw=0.14, depth=0.12, m='brass', crest=0.5, sill=False), face, x, y, z))
    g = Geo()
    g.add(ring(0, 0, -0.06, 0.06, 1.75, 1.85, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    rot(g, 'x', math.pi / 2)
    g.v = [(a, b, c + GH / 2 + 0.2) for (a, b, c) in g.v]
    R.nocol.add(local(g, face, x, y, z))


def neck(R):
    """The neck: a flight climbing south from the north gallery up to a landing over the bottle's crown,
    with the gate at its end; a cage of brass hoops round it, running on down into the crown."""
    x0 = BX - GW / 2 - 0.05
    w = GW + 0.1
    R.flight(x0, NY1, UZ, w, 20, (NZ - UZ) / 20, (NY1 - NY0) / 20, '-y', m='oak', riser='walnut', side='walnut')
    R.parts.add(box(x0, AY - 0.9, NZ - 0.3, x0 + w, NY0, NZ, 'walnut', top='oak'))
    for x in (x0 + 0.06, x0 + w - 0.06):
        seg_rail(R, (x, NY1, UZ + 0.2), (x, NY0, NZ), h=1.0)
        seg_rail(R, (x, NY0, NZ), (x, AY, NZ), h=1.0)
    # the recess behind the gate, closed in
    R.parts.add(box(x0 - 0.2, AY - 0.95, NZ - 0.3, x0, AY, NZ + GH + 0.2, 'brass'))
    R.parts.add(box(x0 + w, AY - 0.95, NZ - 0.3, x0 + w + 0.2, AY, NZ + GH + 0.2, 'brass'))
    R.parts.add(box(x0 - 0.2, AY - 1.1, NZ - 0.3, x0 + w + 0.2, AY - 0.9, NZ + GH + 0.2, 'brass'))
    R.parts.add(box(x0, AY - 0.95, NZ + GH, x0 + w, AY, NZ + GH + 0.2, 'brass'))
    gate(R, BX, AY, NZ, math.pi / 2)
    # the cage round the neck: up from the gallery, over, and down into the crown
    ctrl = [(BX, 28.2, 9.5), (BX, 24.5, 11.6), (BX, 20.5, 13.5), (BX, 17.0, 13.6), (BX, 14.6, 12.2), (BX, BY, 11.0)]
    pts = []
    for k in range(25):
        t = k / 24
        # a Catmull-Rom through the control points
        s = t * (len(ctrl) - 1); i = min(int(s), len(ctrl) - 2); u = s - i
        p0, p1, p2, p3 = ctrl[max(0, i - 1)], ctrl[i], ctrl[i + 1], ctrl[min(len(ctrl) - 1, i + 2)]
        pts.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in range(3)))
    cage = Geo()
    for i in range(len(pts) - 1):
        cage.add(cage_tube(pts[i], pts[i + 1], 1.6 if i < 18 else 1.6 - (i - 17) * 0.02, m='brass', ribs=8, hoops=2 if i % 2 == 0 else 0, segs=20, hoop_w=0.08))
    R.nocol.add(cage)
    for (y, z) in ((25.5, 12.2), (22.5, 13.6)):
        lantern(R, BX, y, z)


def capsule(R):
    """The capsule in the plinth: brass all round, a desk, a lamp, a porthole of sky."""
    for k in range(12):
        a = 2 * math.pi * k / 12
        R.nocol.add(box(-0.02, -0.02, 0.1, 0.02, 0.02, PZ - 0.45, 'bronze').xform(a, BX + (CR - 0.03) * math.cos(a), BY + (CR - 0.03) * math.sin(a), 0))
    R.parts.add(ltable(BX + 0.4, BY - 0.6, BX + 1.5, BY + 0.6, top='leather'))
    llamp(R, BX + 1.1, BY + 0.35, 0.76, m='e_amber')
    open_book(R, BX + 0.9, BY - 0.1, 0.76, ang=math.pi / 2)
    R.parts.add(lchair(BX - 0.2, BY, 0.0))
    R.spot('sit', BX - 0.2, BY, 0.48, 0.0)
    R.light(box(BX + CR - 0.06, BY - 0.25, 1.05, BX + CR - 0.02, BY + 0.25, 1.55, 'e_skydome'))
    R.nocol.add(box(-0.02, -0.02, 0, 0.02, 0.02, 0.02, 'brass'))
    R.spot('plaque', BX + CR - 0.3, BY - 0.9, 1.4, math.pi, text='Pressure: one atmosphere. Depth: none.')


def stair(R):
    """A plain long stair on the atrium's west side, joining the floors."""
    x0, w = V0 + 0.5, 2.4
    R.flight(x0, 24.1, 0.0, w, 40, 0.2, 0.3, '-y', m='terrazzo', riser='tile', side='tile')
    R.parts.add(box(V0, 10.4, UZ - 0.3, x0 + w, 12.1, UZ, 'tile', top='floor', bottom='plaster'))
    for x in (x0 + 0.06, x0 + w - 0.06):
        seg_rail(R, (x, 24.1, 0.2), (x, 12.1, UZ), h=1.0)
    rail(R, x0 + w - 0.06, 10.4, x0 + w - 0.06, 12.1, z=UZ, h=1.0)
    rail(R, V0, 10.46, x0 + w, 10.46, z=UZ, h=1.0)


def dressing(R):
    rows = 16
    for z in (0.0, UZ):
        for (a, b) in ((0.8, 6.3), (9.7, 22.3), (25.7, W - 0.8)):
            sh(R, '+y', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-y', D - T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '+x', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-x', W - T, a, b, z=z, rows=rows, frame='walnut')
    for z in (0.0, UZ):
        for (x, y) in ((2.6, 11.0), (29.4, 11.0), (2.6, 21.0), (29.4, 21.0)):
            R.parts.add(ltable(x - 0.5, y - 1.2, x + 0.5, y + 1.2, top='leather').xform(0, 0, 0, z))
            llamp(R, x, y, z + 0.76, a=math.pi / 2)
        for (x, y) in ((2.6, 2.6), (29.4, 2.6), (2.6, 29.4), (29.4, 29.4), (16.0, 2.6), (16.0, 29.4), (2.6, 16.0), (29.4, 16.0)):
            pendant(R, x, y, z + 5.0, z + (TOP if z == 0 else ZT - UZ), r=0.3)
    for (x, y) in ((1.2, 1.2), (W - 1.2, D - 1.2)):
        lantern(R, x, y, 0.0); lantern(R, x, y, UZ)
    # the ground floor of the atrium: tables either side of the bottle
    for (x, y) in ((9.0, 8.0), (23.0, 8.0), (9.0, 21.0), (23.0, 21.0)):
        R.parts.add(ltable(x - 1.2, y - 0.5, x + 1.2, y + 0.5, top='leather'))
        llamp(R, x, y, 0.76)
