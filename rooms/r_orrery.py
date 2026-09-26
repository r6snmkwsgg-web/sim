"""The Orrery: a round domed hall with a painted night sky, and in it a great orrery. The sun is a
hollow ball of gold sitting in the middle; the planets are globes of bound books on brass arms that
turn round it, each at its own pace. The two lowest arms carry walkways, a step off the floor, that
you can step onto and ride. The sun has a door. Inside it a little round room turns, slower than any
of them, and its own door only comes round to the sun's once a minute."""
from kit_h12 import *
from kit_h7 import lathe

W = D = 32.0
CX = CY = 16.0
PZ = 0.6                       # the ring platform round the sun
PR0, PR1 = 2.9, 5.2
SUNZ, SUNR = 2.4, 2.8           # the sun: centre height, radius
DOOR_A = -math.pi / 2           # the sun's door faces south
DR0, DR1 = 1.95, 2.1           # the turning room's wall
SH = 2.9                        # door height
DOME_R, DOME_S, DOME_TOP = 15.0, 5.0, 7.5
lib.EMIT.setdefault('e_sun', ((1.00, 0.76, 0.42), 5.0))


def make():
    R = Room('orrery', 2, 2, res=2048)
    rs = rng(55)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, 4.4, 'tile', bottom='terrazzo', top='plaster'))
    dome(R)
    walls(R, rs)
    platform(R)
    sun(R, rs)
    inner_room(R, rs)
    arms(R, rs)
    furnish(R, rs)
    # walking graph: round the outside, in to the platform on the four axes
    ring = []
    for k in range(16):
        a = 2 * math.pi * k / 16
        ring.append(R.navpt(CX + 14.0 * math.cos(a), CY + 14.0 * math.sin(a)))
    R.link(*ring); R.link(ring[-1], ring[0])
    inner = []
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        inner.append(R.navpt(CX + 4.0 * math.cos(a), CY + 4.0 * math.sin(a), PZ))
    R.link(*inner); R.link(inner[-1], inner[0])
    for k in range(4):
        a = 2 * math.pi * k / 4
        m = R.navpt(CX + 7.0 * math.cos(a), CY + 7.0 * math.sin(a))
        R.link(ring[k * 4], m)
    for (x, y, k) in ((8.0, 1.6, 11), (24.0, 1.6, 13), (8.0, 30.4, 5), (24.0, 30.4, 3), (1.6, 8.0, 9), (1.6, 24.0, 7), (30.4, 8.0, 15), (30.4, 24.0, 1)):
        R.link(ring[k], R.navpt(x, y))
    secret(R, CX, CY, PZ, 'Inside the Sun',
           'The sun\'s door opens once a minute, and inside is a small round room that turns, with a chair and a lamp and a view of the planets going round, the right way up, for ever.', r=1.5)
    return finish(R, 'The Orrery', weight=3, probe=(CX, 9.0, 2.2), top=DOME_TOP,
                  blurb='The planets are made of books and they go round the sun, which is made of gold, under a sky that is made of paint. The arms come round low enough to step on. Everyone does.')


def dome(R):
    """A shallow dome on a drum over the middle, painted as a night sky."""
    Rs = (DOME_R ** 2 + (DOME_TOP - DOME_S) ** 2) / (2 * (DOME_TOP - DOME_S))
    zc = DOME_TOP - Rs
    prof = [(0.05, 4.3), (DOME_R, 4.3), (DOME_R, DOME_S)]
    n = 16
    for k in range(1, n):
        r = DOME_R * (1 - k / n)
        prof.append((max(0.05, r), zc + math.sqrt(max(0.0, Rs * Rs - r * r))))
    prof.append((0.05, DOME_TOP))
    R.cut(lathe(CX, CY, prof, 48, ['plaster', 'tile', 'tile'] + ['plaster'] * (len(prof) - 3)))
    # the painted sky: an inward-facing cap just inside the plaster, over the middle
    g = Geo()
    rings_ = 10; segs = 40; r0 = DOME_R - 1.2
    pts = []
    for i in range(rings_ + 1):
        r = r0 * (1 - i / rings_)
        z = zc + math.sqrt(max(0.0, Rs * Rs - r * r)) - 0.04
        pts.append([(CX + r * math.cos(2 * math.pi * k / segs), CY + r * math.sin(2 * math.pi * k / segs), z) for k in range(segs)])
    for i in range(rings_):
        for k in range(segs):
            j = (k + 1) % segs
            ids = [g.vert(pts[i][k]), g.vert(pts[i + 1][k]), g.vert(pts[i + 1][j]), g.vert(pts[i][j])]
            g.face(ids, 'e_skydome', [(0, 0)] * 4)
    R.light(g.fix())
    # brass meridians over the sky, a cornice at the drum
    for k in range(12):
        a = 2 * math.pi * k / 12
        prev = None
        for i in range(11):
            r = (DOME_R - 0.4) * (1 - i / 10)
            z = zc + math.sqrt(max(0.0, Rs * Rs - r * r)) - 0.08
            p = (CX + r * math.cos(a), CY + r * math.sin(a), z)
            if prev: R.nocol.add(beam(prev, p, 0.1, 'brass'))
            prev = p
    R.nocol.add(ring(CX, CY, 4.3, 4.45, DOME_R - 0.3, DOME_R + 0.02, 48, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))


def walls(R, rs):
    """Two tiers of cases round the walls, broken at the doorways; a gallery rail between the tiers."""
    segs = [(0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)]
    for (a, b) in segs:
        sh(R, '+y', T, a, b, rows=9, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=9, frame='walnut')
        sh(R, '+x', T, a, b, rows=9, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=9, frame='walnut')
    for (x0, y0, x1, y1) in ((T, T, W - T, T + 0.5), (T, D - T - 0.5, W - T, D - T), (T, T, T + 0.5, D - T), (W - T - 0.5, T, W - T, D - T)):
        R.parts.add(box(x0, y0, 3.95, x1, y1, 4.05, 'walnut'))


def platform(R):
    """The ring platform round the sun: two steps up, a brass rim, the orbit track inlaid in the floor."""
    R.parts.add(ring(CX, CY, 0.0, PZ, 0.5, PR1, 64, top='terrazzo', bottom='terrazzo', inner='tile', outer='tile'))
    R.parts.add(ring(CX, CY, 0.0, PZ / 2, PR1, PR1 + 0.4, 64, top='terrazzo', bottom='terrazzo', inner='tile', outer='tile'))
    R.nocol.add(ring(CX, CY, PZ, PZ + 0.01, PR1 - 0.12, PR1 - 0.04, 64, top='brass', bottom='brass', inner='brass', outer='brass'))
    for r in (9.3, 13.4):
        R.nocol.add(ring(CX, CY, 0.0, 0.008, r - 0.05, r + 0.05, 96, top='brass', bottom='brass', inner='brass', outer='brass'))
    # zodiac marks round the platform
    for k in range(12):
        a = 2 * math.pi * k / 12
        R.nocol.add(obox(CX + math.cos(a) * 3.3, CY + math.sin(a) * 3.3, CX + math.cos(a) * 4.8, CY + math.sin(a) * 4.8, PZ, PZ + 0.008, 0.06, 'gilt'))


def sun(R, rs):
    """The sun: a glowing gold ball with a door; the doorway lined in brass; an invisible drum round it."""
    rings_, segs = 16, 40
    g = Geo()
    da = 0.62 / SUNR * 2.2
    for i in range(rings_):
        p0 = -math.pi / 2 + math.pi * i / rings_
        p1 = -math.pi / 2 + math.pi * (i + 1) / rings_
        for k in range(segs):
            a0 = 2 * math.pi * k / segs; a1 = 2 * math.pi * (k + 1) / segs
            am = (a0 + a1) / 2; zm = SUNZ + SUNR * math.sin((p0 + p1) / 2)
            d = math.atan2(math.sin(am - DOOR_A), math.cos(am - DOOR_A))
            if abs(d) < da and PZ - 0.2 < zm < SH + PZ - 0.1: continue
            if zm < PZ - 0.3: continue
            P = lambda p, a: (CX + SUNR * math.cos(p) * math.cos(a), CY + SUNR * math.cos(p) * math.sin(a), SUNZ + SUNR * math.sin(p))
            ids = [g.vert(P(p0, a0)), g.vert(P(p0, a1)), g.vert(P(p1, a1)), g.vert(P(p1, a0))]
            g.face(ids, 'e_sun', [(0, 0)] * 4)
    R.light(g.fix())
    # inside: a gilt lining facing in
    gi = sphere(CX, CY, SUNZ, SUNR - 0.08, 32, 14, 'gilt')
    gi.f = [tuple(reversed(f)) for f in gi.f]; gi.uv = [list(reversed(u)) for u in gi.uv]
    R.nocol.add(gi)
    R.light(sphere(CX, CY, 4.4, 0.25, 10, 5, 'e_candle'))
    # the equator band the arms come out of
    R.nocol.add(ring(CX, CY, 2.95, 3.9, SUNR - 0.2, SUNR - 0.02, 40, top='bronze', bottom='bronze', inner='bronze', outer='bronze'))
    # the doorway: a short passage from the platform through the shell, brass lined
    ca, sa = math.cos(DOOR_A), math.sin(DOOR_A)
    px, py = -sa, ca
    for s in (-1, 1):
        a = (CX + ca * DR1 + px * s * 0.68, CY + sa * DR1 + py * s * 0.68)
        b = (CX + ca * (PR0 + 0.05) + px * s * 0.68, CY + sa * (PR0 + 0.05) + py * s * 0.68)
        R.parts.add(obox(a[0], a[1], b[0], b[1], PZ, PZ + SH, 0.12, 'brass'))
    a = (CX + ca * DR1, CY + sa * DR1); b = (CX + ca * (PR0 + 0.05), CY + sa * (PR0 + 0.05))
    R.parts.add(obox(a[0], a[1], b[0], b[1], PZ + SH, PZ + SH + 0.15, 1.5, 'brass'))
    # the invisible drum round it at walking height (the glow is not solid)
    n = 40
    for k in range(n):
        a0 = 2 * math.pi * k / n; a1 = 2 * math.pi * (k + 1) / n
        d = math.atan2(math.sin((a0 + a1) / 2 - DOOR_A), math.cos((a0 + a1) / 2 - DOOR_A))
        if abs(d) < 0.62 / DR1 + 0.1: continue
        for r in (DR1 + 0.08, PR0 - 0.02):
            R.col.add(obox(CX + r * math.cos(a0), CY + r * math.sin(a0), CX + r * math.cos(a1), CY + r * math.sin(a1), PZ, PZ + 3.0, 0.06, 'tile'))
    # a brass cradle under it, and the sun's column up to the dome with the high arms' collars
    for k in range(8):
        a = 2 * math.pi * k / 8 + 0.2
        R.nocol.add(beam((CX + math.cos(a) * PR0, CY + math.sin(a) * PR0, PZ), (CX + math.cos(a) * 2.2, CY + math.sin(a) * 2.2, SUNZ + 0.6), 0.12, 'brass'))
    R.nocol.add(cyl(CX, CY, SUNZ + SUNR - 0.1, DOME_TOP, 0.18, 12, side='brass', caps=False))


def inner_room(R, rs):
    """The turning room inside the sun: a drum with one door, a chair, a table, a lamp; it goes round once
    a minute, and when its door meets the sun's you can walk in (or out)."""
    M = R.mover('spin', pivot=(CX, CY, 0), axis='z', speed=0.1)
    M.parts.add(cyl(CX, CY, PZ, PZ + 0.05, DR1 - 0.02, 32, side='brass', top='carpet', bottom='brass'))
    half = 0.62 / DR1
    g = Geo()
    a0, a1 = DOOR_A + half, DOOR_A + 2 * math.pi - half
    g.add(ring(CX, CY, PZ, PZ + SH, DR0, DR1, 36, top='brass', bottom='brass', inner='gilt', outer='brass', a0=a0, a1=a1))
    M.parts.add(g)
    M.parts.add(ring(CX, CY, PZ + SH, PZ + SH + 0.1, DR0, DR1, 36, top='brass', bottom='brass', inner='brass', outer='brass'))
    M.nocol.add(ring(CX, CY, PZ + 0.05, PZ + 0.06, 0.4, 1.4, 32, top='oxblood', bottom='oxblood', inner='oxblood', outer='oxblood'))
    # furniture (moving with it): an armchair facing the door, a round table, a lamp, books
    ca, sa = math.cos(DOOR_A + math.pi), math.sin(DOOR_A + math.pi)
    c = chair_geo(CX + ca * 1.2, CY + sa * 1.2, DOOR_A, frame='walnut', seat='velvet'); c.xform(0, 0, 0, PZ + 0.05)
    M.parts.add(c)
    tb = table_geo(CX - 0.35, CY - 0.35, CX + 0.35, CY + 0.35, 0.7, 'walnut', top='leather'); tb.xform(0, 0, 0, PZ + 0.05)
    M.parts.add(tb)
    lg = Geo()
    lg.add(cyl(CX + 0.1, CY + 0.1, PZ + 0.75, PZ + 0.78, 0.07, 10, side='brass', top='brass'))
    lg.add(cyl(CX + 0.1, CY + 0.1, PZ + 0.78, PZ + 1.1, 0.012, 6, side='brass', caps=False))
    lg.add(frustum(CX + 0.1, CY + 0.1, PZ + 1.05, PZ + 1.2, 0.17, 0.06, 10, 'green', inner='ivory'))
    M.nocol.add(lg)
    bk = Geo()
    for k in range(5):
        a = DOOR_A + math.pi * 0.6 + k * 0.28
        book_row_geo(bk, rs, -0.4, 0.4, 0.0, 0.0, depth=0.22)
    # a short curved case on the drum wall, opposite the door
    for k in range(3):
        a = DOOR_A + math.pi + (k - 1) * 0.5
        cs = fake_case(rs, 0.9, 4, row_h=0.4, depth=0.26)
        cs.xform(a + math.pi / 2, CX + math.cos(a) * (DR0 - 0.02) - math.cos(a + math.pi / 2) * 0.45, CY + math.sin(a) * (DR0 - 0.02) - math.sin(a + math.pi / 2) * 0.45, PZ + 0.05)
        M.nocol.add(cs)
    R.spot('plaque', CX, CY, PZ, 0.0, text='Engraved on the table: THE OBSERVER IS AT REST. EVERYTHING ELSE IS GOING ROUND.')


def arms(R, rs):
    """The planets. Two low arms carry walkways you can ride; four high ones carry the big planets."""
    # arm 1: girder at z 3.0, walkway r 5.3..9.0 at z PZ; its planet on a post at r 8.1
    arm(R, rs, speed=0.06, a0=0.9, zg=3.0, deck=(5.3, 9.0, PZ), prad=0.85, pr=8.1, pz=4.65, ring_=False, w=1.7)
    # arm 2: girder at z 3.5, walkway r 9.6..13.0 just off the floor; its planet at r 12.5, ringed
    arm(R, rs, speed=-0.035, a0=3.6, zg=3.5, deck=(9.6, 13.0, 0.35), prad=0.9, pr=12.5, pz=4.6, ring_=True, w=1.8)
    # high arms: drawn only, under the dome, planets hanging from them
    arm(R, rs, speed=0.09, a0=2.1, zg=6.3, deck=None, prad=0.5, pr=5.5, pz=5.4, ring_=False, w=0.0, high=True)
    arm(R, rs, speed=0.025, a0=4.9, zg=6.05, deck=None, prad=0.9, pr=10.0, pz=5.15, ring_=False, w=0.0, high=True)


def arm(R, rs, speed, a0, zg, deck, prad, pr, pz, ring_, w, high=False):
    M = R.mover('spin', pivot=(CX, CY, 0), axis='z', speed=speed, phase=0.0)
    ca, sa = math.cos(a0), math.sin(a0)
    P = lambda r, z: (CX + ca * r, CY + sa * r, z)
    # the girder: a brass box beam from inside the sun to the planet, a curved brace under it
    r_in = 2.3 if not high else 0.2
    M.nocol.add(beam(P(r_in, zg), P(pr, zg), 0.16, 'brass', 0.14))
    M.nocol.add(beam(P(r_in, zg - 0.35), P(pr * 0.6, zg - 0.05), 0.08, 'brass'))
    if high:
        M.nocol.add(cyl(CX, CY, zg - 0.12, zg + 0.12, 0.28, 12, side='brass', top='brass', bottom='brass'))
    # the planet on a post (or hanging)
    M.nocol.add(beam(P(pr, zg), P(pr, pz), 0.06, 'brass'))
    g = book_globe(0, 0, 0, prad, rs)
    g.xform(a0 + rs.uniform(0, 3), *P(pr, pz))
    M.nocol.add(g)
    if ring_:
        rg = ring(0, 0, -0.02, 0.02, prad * 1.3, prad * 1.7, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt')
        rot(rg, 'x', 0.35)
        rg.xform(a0, *P(pr, pz))
        M.nocol.add(rg)
    # a moon on a little arm
    mp = (P(pr, pz)[0] + ca * 0.0 - sa * (prad + 0.6), P(pr, pz)[1] + sa * 0.0 + ca * (prad + 0.6), pz + 0.3)
    M.nocol.add(beam(P(pr, pz + 0.1), mp, 0.03, 'brass'))
    M.nocol.add(book_globe(mp[0], mp[1], mp[2], 0.22, rs, bands=4, segs=8))
    if deck is None: return
    r0, r1, zd = deck
    px, py = -sa, ca
    # the walkway: an oak deck with brass edges, hung from the girder on rods
    d = Geo()
    L = r1 - r0
    d.add(box(0, -w / 2, zd - 0.12, L, w / 2, zd, 'oak', sides='brass', bottom='iron'))
    for s in (-1, 1):
        d.add(box(0, s * w / 2 - 0.04, zd, L, s * w / 2 + 0.04, zd + 0.06, 'brass'))
    d.xform(a0, *P(r0, 0.0))
    M.parts.add(d)
    for r in (r0 + 0.3, (r0 + r1) / 2, r1 - 0.3):
        for s in (-1, 1):
            p = P(r, 0.0)
            q = (p[0] + px * s * (w / 2 + 0.05), p[1] + py * s * (w / 2 + 0.05))
            M.nocol.add(beam((q[0], q[1], zd), (q[0] - px * s * (w / 2 - 0.1), q[1] - py * s * (w / 2 - 0.1), zg), 0.035, 'brass'))
    # a bench on the outer walkway, a lamp standard (unlit brass) at its end
    if r1 > 12:
        b = Geo()
        b.add(box(-0.5, -0.2, 0, 0.5, 0.2, 0.45, 'walnut', top='leather'))
        b.xform(a0 + math.pi / 2, *P(r1 - 1.0, zd))
        M.parts.add(b)


def furnish(R, rs):
    """Reading tables in the corners (outside the planets' track), lamp standards round the outside."""
    for (x, y) in ((4.2, 4.2), (27.8, 4.2), (4.2, 27.8), (27.8, 27.8)):
        a = math.atan2(CY - y, CX - x)
        R.parts.add(table_geo(x - 0.9, y - 0.5, x + 0.9, y + 0.5, 0.78, 'walnut', top='leather').xform(0, 0, 0, 0))
        desk_lamp(R, x - 0.4, y, 0.78); desk_lamp(R, x + 0.4, y, 0.78)
        for s in (-1, 1):
            R.parts.add(chair_geo(x + s * 0.45, y - 0.9, math.pi / 2))
            R.parts.add(chair_geo(x + s * 0.45, y + 0.9, -math.pi / 2))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        lamp_post(R, CX + 14.4 * math.cos(a), CY + 14.4 * math.sin(a), 0.0, h=2.6)
    for k in range(8):
        a = 2 * math.pi * k / 8
        R.light(sphere(CX + 5.4 * math.cos(a), CY + 5.4 * math.sin(a), 0.35, 0.06, 6, 3, 'e_amber'))
