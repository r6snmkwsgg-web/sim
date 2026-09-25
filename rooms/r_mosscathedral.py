"""The Moss Cathedral: a nave fifteen metres high under a pointed vault, galleries over the aisles,
stained glass at the north end over a raised chancel; and moss over all of it, thick as a carpet on
the pews and the flags, hanging in beards from the galleries. The altar is a book. Behind it, a stair
goes down through the chancel floor to the crypt."""
from lib import *
from kit_h4 import *
from kit_a import pointed_profile, frustum

W = 32.0
NX0, NX1 = 10.0, 22.0          # the nave
GX0, GX1 = 9.7, 22.3           # aisle / gallery inner walls
CY = 24.0                      # the chancel starts here, raised
CZ = 1.2
AH = 6.8                       # aisle ceiling
GZ1 = 12.6                     # gallery ceiling
SY0, SN, SRUN = 10.2, 40, 0.28 # the stair to the west gallery, against the west wall
HOLE = 17.8
CRX0, CRX1 = 13.0, 17.2        # the crypt stair (climbs -x), its hole behind the altar
CRY0, CRY1 = 30.2, 31.3


def make():
    R = Room('mosscathedral', 2, 2, levels=2, res=2048)
    R.sockets(floor='tile', wall='tile')
    rnd = random.Random(34)
    T_ = T - 0.02
    # the nave: pointed vault; the chancel end raised
    pr = pointed_profile(16.0, NX1 - NX0, 0.0, 8.5, 6.5, 14)
    mats = ['tile', 'tile'] + ['plaster'] * (len(pr) - 3) + ['tile']
    R.cut(prism(pr, 'y', T_, CY, mats))
    pr2 = pointed_profile(16.0, NX1 - NX0, CZ, 8.5 - CZ, 6.5, 14)
    R.cut(prism(pr2, 'y', CY - 0.02, W - T_, mats))
    # aisles and the galleries above them
    for (x0, x1) in ((T_, GX0), (GX1, W - T_)):
        R.cut(box(x0, T_, 0.0, x1, W - T_, AH, 'tile', bottom='tile', top='plaster'))
        R.cut(box(x0, T_, LH, x1, W - T_, GZ1, 'tile', bottom='floor', top='plaster'))
    # arcade arches from the aisles into the nave, triforium arches from the galleries
    for y in (4.0, 10.0, 16.0, 21.0):
        ap = arch_profile(y, 3.0, 0.0, 3.4, 16)
        for (a, b) in ((GX0 - 0.05, NX0 + 0.05), (NX1 - 0.05, GX1 + 0.05)):
            R.cut(prism(ap, 'x', a, b, arch_mats(len(ap), 'tile', 'tile')))
    for y in (7.0, 13.0, 19.0, 25.0):
        ap = arch_profile(y, 3.2, LH, 2.1, 16)
        for (a, b, xr) in ((GX0 - 0.05, NX0 + 0.05, GX0 + 0.15), (NX1 - 0.05, GX1 + 0.05, GX1 - 0.15)):
            R.cut(prism(ap, 'x', a, b, arch_mats(len(ap), 'floor', 'tile')))
            balus(R, xr, y - 1.6, xr, y + 1.6, LH, h=1.0)
            moss_slab(R, xr - 0.13, y - 1.6, xr + 0.13, y + 1.6, LH + 1.06, 0.07, 0.03)
            strands(R, xr + (0.15 if xr < 16 else -0.15), y - 1.4, xr + (0.15 if xr < 16 else -0.15), y + 1.4, LH - 0.2, 7, 3.0, rnd)
    # the organ loft across the south end, joined to both galleries
    R.parts.add(box(NX0, T, TOP, NX1, 3.4, LH, 'tile', top='floor'))
    balus(R, NX0, 3.3, NX1, 3.3, LH, h=1.0)
    moss_slab(R, NX0, 3.17, NX1, 3.43, LH + 1.06, 0.07, 0.03)
    strands(R, NX0 + 0.3, 3.45, NX1 - 0.3, 3.45, TOP, 22, 3.4, rnd)
    for (a, b) in ((GX0 - 0.1, NX0 + 0.1), (NX1 - 0.1, GX1 + 0.1)):
        R.cut(box(a, T_, LH, b, 3.4, LH + 3.0, 'tile', bottom='floor', top='tile'))

    overgrowth(R, rnd)
    windows(R, rnd)
    stair(R, rnd)
    chancel(R, rnd)
    crypt(R, rnd)
    pews(R, rnd)
    books(R, rnd)
    lights(R, rnd)

    a = navloop(R, [(16.0, 2.0), (16.0, 12.0), (16.0, 21.5)], close=False)
    b = navloop(R, [(12.0, 25.5), (16.0, 26.3), (20.0, 25.5)], z=CZ, close=False)
    R.link(a[-1], b[1])
    navloop(R, [(5.0, 2.0), (5.0, 16.0), (5.0, 30.0), (27.0, 30.0), (27.0, 16.0), (27.0, 2.0)])
    a = R.navpt(5.0, 4.0); b = R.navpt(12.0, 4.0); R.link(a, b)
    navloop(R, [(2.0, 2.0), (5.0, 12.0), (5.0, 30.0), (27.0, 30.0), (27.0, 2.0), (16.0, 2.0)], z=LH)
    R.spot('probe', 16.0, 12.0, 5.0)
    R.meta.update(label='The Moss Cathedral', weight=3,
                  blurb='Nobody has preached here in a long time, and the congregation is moss. It sits very still, in every pew, and listens.')
    R.meta['box'] = [[T, 0, T], [W - T, 15.0, W - T]]
    fx(R, 'dust', [NX0, 3.0, 0.5, NX1, 30.0, 14.0])
    fx(R, 'fog', [T, T, 0.0, W - T, W - T, 1.0], density=0.04)
    secret(R, 15.0, 27.5, -1.8, 'The Crypt',
           'Behind the altar a stair goes down under the floor. The dead are shelved here like everyone else, and someone keeps their candles lit.', r=2.5)
    return tidy(R)


def overgrowth(R, rnd):
    """Moss climbing the nave walls and piers, carpeting the flags, bearding every ledge."""
    for k in range(70):
        side = rnd.choice((0, 1))
        x = NX0 + 0.03 if side == 0 else NX1 - 0.03
        y = rnd.uniform(3.6, W - 0.6)
        z = rnd.uniform(0.0, 7.5) ** 1.0
        ry, rz = rnd.uniform(0.5, 1.6), rnd.uniform(0.5, 2.2)
        R.nocol.add(blob(x, y, z, 0.1, ry, rz, rnd.choice(('moss', 'moss', 'mossdk')), 8, 4))
    for k in range(40):
        x = rnd.choice((rnd.uniform(0.6, GX0 - 0.3), rnd.uniform(GX1 + 0.3, W - 0.6)))
        y = rnd.choice((T + 0.03, W - T - 0.03))
        R.nocol.add(blob(x, y, rnd.uniform(0.0, 6.0), rnd.uniform(0.5, 1.4), 0.1, rnd.uniform(0.6, 1.8), 'moss', 8, 4))
    for k in range(45):
        x, y = rnd.uniform(NX0 + 0.3, NX1 - 0.3), rnd.uniform(3.6, CY - 2.0)
        R.nocol.add(blob(x, y, 0.0, rnd.uniform(0.6, 1.6), rnd.uniform(0.6, 1.6), 0.05, 'moss', 8, 3, rnd.uniform(0, 3)))
    for k in range(20):
        x, y = rnd.uniform(NX0 + 0.5, NX1 - 0.5), rnd.uniform(CY + 0.3, W - 0.8)
        if 14.0 < x < 18.0 and y > 27.0: continue
        R.nocol.add(blob(x, y, CZ, rnd.uniform(0.5, 1.3), rnd.uniform(0.5, 1.3), 0.05, 'moss', 8, 3, rnd.uniform(0, 3)))
    # beards off the triforium sills and the gallery floor edges into the nave
    for x in (NX0 - 0.05, NX1 + 0.05):
        strands(R, x, 4.0, x, W - 1.0, TOP - 0.1, 40, 4.5, rnd, m='mossdk', w=0.09)
        strands(R, x, 4.0, x, W - 1.0, TOP - 0.1, 30, 2.5, rnd, m='moss', w=0.07)


def windows(R, rnd):
    def lancet(x, z0, h, w, face, m, depth=None):
        p = arch_profile(0, w, z0, h, 12)
        if face == 'N':
            R.cut(prism([(x + a, b) for a, b in p], 'y', W - T - 0.02, W - 0.12, 'tile', cap='black'))
            R.light(prism([(x + a * 0.9, z0 + (b - z0) * 0.97) for a, b in p], 'y', W - 0.15, W - 0.13, m, cap=m))
        else:
            R.cut(prism([(x + a, b) for a, b in p], 'y', 0.12, T + 0.02, 'tile', cap='black'))
            R.light(prism([(x + a * 0.9, z0 + (b - z0) * 0.97) for a, b in p], 'y', 0.13, 0.15, m, cap=m))
        # leading: a few bars across
        for k in range(1, 4):
            zz = z0 + h * k / 4
            yy = W - 0.2 if face == 'N' else 0.2
            R.nocol.add(box(x - w / 2, yy - 0.02, zz - 0.02, x + w / 2, yy + 0.02, zz + 0.02, 'iron'))
    for (x, m, h) in ((13.3, 'e_blue', 4.2), (16.0, 'e_red', 5.2), (18.7, 'e_green', 4.2)):
        lancet(x, LH + 1.2, h, 1.8, 'N', m)
    for (x, m) in ((13.6, 'e_sky'), (16.0, 'e_sky'), (18.4, 'e_sky')):
        lancet(x, LH + 3.4, 2.6, 1.2, 'S', m)
    # a rose over the chancel lancets
    rr = 1.3
    circ = [(16.0 + rr * math.cos(2 * math.pi * k / 24), LH + 5.85 + rr * math.sin(2 * math.pi * k / 24)) for k in range(24)]
    R.cut(prism(circ, 'y', W - T - 0.02, W - 0.12, 'tile', cap='black'))
    for k in range(6):
        a0 = 2 * math.pi * k / 6
        pts = [(16.0, LH + 5.85)] + [(16.0 + (rr - 0.08) * math.cos(a0 + (math.pi / 3) * j / 4), LH + 5.85 + (rr - 0.08) * math.sin(a0 + (math.pi / 3) * j / 4)) for j in range(5)]
        m = ('e_red', 'e_blue', 'e_green')[k % 3]
        R.light(prism(pts, 'y', W - 0.15, W - 0.13, m, cap=m))
    # moss creeping round the glass
    for k in range(10):
        x = rnd.uniform(12.0, 20.0)
        R.nocol.add(blob(x, W - T - 0.05, LH + rnd.uniform(0.8, 1.2), rnd.uniform(0.4, 1.0), 0.1, rnd.uniform(0.2, 0.5), 'moss', 8, 4))


def stair(R, rnd):
    top_y = SY0 + SN * SRUN
    x1 = T + 1.9
    R.flight(T + 0.01, SY0, 0, 1.9, SN, 0.2, SRUN, '+y', m='tile', riser='tile', side='tile')
    R.cut(box(T - 0.02, HOLE, AH - 0.1, x1, top_y, LH + 0.1, 'tile', bottom='tile', top='tile'))
    stair_rail(R, x1 - 0.03, SY0 + SRUN, 0.2, x1 - 0.03, HOLE + 0.1, 0.2 + (HOLE + 0.1 - SY0 - SRUN) / SRUN * 0.2)
    balus(R, x1 + 0.1, HOLE - 0.2, x1 + 0.1, top_y, LH)
    balus(R, T, HOLE - 0.1, x1 + 0.2, HOLE - 0.1, LH)
    for k in range(6):
        y = rnd.uniform(SY0 + 1.0, top_y - 1.0)
        R.nocol.add(blob(x1 - 0.05, y, (y - SY0) / SRUN * 0.2 - 0.3, 0.12, rnd.uniform(0.3, 0.7), 0.35, 'moss', 8, 4))


def chancel(R, rnd):
    # six steps up to the chancel, moss in their corners
    R.flight(NX0, CY - 6 * 0.3, 0.0, NX1 - NX0, 6, CZ / 6, 0.3, '+y', m='tile', riser='tile', side='tile')
    R.nocol.add(box(NX0, CY - 1.8, 0.0, NX0 + 1.0, CY, 0.05, 'moss'))
    R.nocol.add(box(NX1 - 1.3, CY - 1.8, 0.0, NX1, CY, 0.05, 'moss'))
    # the altar: a stone table under a cushion of moss, a great book open on it
    ax0, ax1, ay0, ay1 = 14.2, 17.8, 27.6, 29.0
    R.parts.add(box(ax0, ay0, CZ, ax1, ay1, CZ + 1.0, 'tile', skip=('-z',)))
    R.parts.add(box(ax0 - 0.15, ay0 - 0.15, CZ + 1.0, ax1 + 0.15, ay1 + 0.15, CZ + 1.12, 'tile'))
    moss_slab(R, ax0 - 0.15, ay0 - 0.15, ax1 + 0.15, ay1 + 0.15, CZ + 1.12, 0.08, 0.05, 0.7, rnd)
    g = box(-0.55, -0.4, 0.0, 0.55, 0.4, 0.06, 'leather')
    g.add(box(-0.52, -0.37, 0.06, -0.01, 0.37, 0.14, 'ivory')); g.add(box(0.01, -0.37, 0.06, 0.52, 0.37, 0.14, 'ivory'))
    rot(g, 'x', -0.25)
    R.nocol.add(g.xform(0, 16.0, 28.1, CZ + 1.28))
    R.spot('read', 16.0, 27.0, CZ, math.pi / 2)
    for x in (14.4, 17.6):
        R.parts.add(cyl(x, 28.3, CZ + 1.2, CZ + 1.7, 0.05, 8, side='ivory', top='ivory'))
        R.light(sphere(x, 28.3, CZ + 1.78, 0.06, 8, 4, 'e_candle'))
    for x in (12.2, 19.8):
        R.parts.add(cyl(x, 26.0, CZ, CZ + 1.5, 0.06, 8, side='brass', top='brass'))
        R.parts.add(cyl(x, 26.0, CZ, CZ + 0.05, 0.25, 10, side='brass', top='brass'))
        R.light(sphere(x, 26.0, CZ + 1.62, 0.1, 8, 4, 'e_candle'))
    # the way down: an opening behind the altar, railed
    R.cut(box(CRX0 - 0.1, CRY0, -0.6, CRX1 + 0.1, CRY1 + 0.05, CZ + 0.3, 'tile', bottom='tile', top='tile'))
    arail(R, CRX0 + 0.8, CRY0 - 0.08, CRX1 + 0.18, CRY0 - 0.08, CZ, m='iron')
    arail(R, CRX1 + 0.18, CRY0 - 0.08, CRX1 + 0.18, CRY1 + 0.05, CZ, m='iron')
    R.nocol.add(box(CRX1 + 0.3, CRY0 - 0.5, CZ, 20.8, W - T, CZ + 0.05, 'moss'))


def crypt(R, rnd):
    zf = -1.8
    cp = arch_profile(28.05, 6.9, zf, 1.6, 20, rise=1.1)
    R.cut(prism(cp, 'x', 11.0, 21.0, arch_mats(len(cp), 'slate', 'tile')))
    R.flight(CRX1, CRY0, zf, CRY1 - CRY0, 15, 0.2, (CRX1 - CRX0) / 15, '-x', m='tile', riser='tile', side='tile')
    stair_rail(R, CRX1 - 0.28, CRY0 + 0.03, zf + 0.2, CRX0 + 0.3, CRY0 + 0.03, CZ - 0.2, m='iron')
    # tombs down the middle, each with a book on its lid; shelves of the dead along the walls
    for (x, a) in ((13.6, 0), (16.4, 0), (19.2, 0)):
        R.parts.add(box(x - 0.55, 26.0, zf, x + 0.55, 28.2, zf + 0.75, 'tile'))
        R.parts.add(box(x - 0.62, 25.93, zf + 0.75, x + 0.62, 28.27, zf + 0.85, 'slate'))
        R.nocol.add(book(x, 27.1, zf + 0.85, rnd.uniform(-0.3, 0.3), rnd.choice(BOOKM)))
        R.nocol.add(blob(x + rnd.uniform(-0.3, 0.3), 26.4, zf + 0.85, 0.35, 0.3, 0.05, 'moss', 8, 3))
    sh(R, '+y', 24.6, 11.4, 20.6, z=zf, rows=4, frame='walnut', depth=0.3)
    sh(R, '+x', 11.0, 25.0, 29.8, z=zf, rows=4, frame='walnut', depth=0.3)
    sh(R, '-x', 21.0, 25.0, 29.8, z=zf, rows=4, frame='walnut', depth=0.3)
    for (x, y) in ((12.0, 25.3), (20.0, 25.3), (11.5, 29.8), (20.5, 29.8), (16.0, 25.2)):
        candle(R, x, y, zf, h=0.25, stand=0.9)
    R.spot('plaque', 16.0, 28.8, zf, math.pi / 2, text='HERE LIE THE READERS WHO FINISHED. There are not very many of them.')
    R.light(sphere(16.0, 28.0, 0.35, 0.08, 8, 4, 'e_dim'))
    for x in (13.0, 19.0):
        R.nocol.add(cyl(x, 26.4, -0.3, 0.6, 0.01, 4, side='iron', caps=False))
        R.light(sphere(x, 26.4, -0.35, 0.1, 8, 4, 'e_lamp'))


def pews(R, rnd):
    for k in range(15):
        y = 5.0 + k * 1.05
        for (x0, x1) in ((NX0 + 0.5, 15.1), (16.9, NX1 - 0.5)):
            R.parts.add(box(x0, y, 0.42, x1, y + 0.45, 0.48, 'walnut'))
            R.parts.add(box(x0, y - 0.06, 0.2, x1, y, 1.0, 'walnut'))
            for xe in (x0, x1 - 0.06):
                R.parts.add(box(xe, y - 0.06, 0, xe + 0.06, y + 0.45, 1.05, 'walnut', skip=('-z',)))
            # the moss: a cushion on the seat, a ridge on the back, beards down the ends
            R.nocol.add(box(x0 + 0.02, y + 0.02, 0.48, x1 - 0.02, y + 0.44, 0.48 + rnd.uniform(0.05, 0.12), 'moss'))
            R.nocol.add(box(x0 - 0.02, y - 0.1, 1.0, x1 + 0.02, y + 0.04, 1.0 + rnd.uniform(0.06, 0.14), 'moss'))
            for xe in (x0 - 0.04, x1 + 0.0):
                if rnd.random() < 0.6:
                    R.nocol.add(box(xe, y - 0.05, rnd.uniform(0.1, 0.5), xe + 0.04, y + 0.4, 1.05, 'mossdk'))
            if k % 2 == 0: R.spot('sit', (x0 + x1) / 2, y + 0.25, 0.48, math.pi / 2)
        if k % 3 == 1:
            for x in (15.25, 16.75):
                R.parts.add(cyl(x, y + 0.2, 0.0, 1.2, 0.03, 6, side='brass', caps=False))
                R.parts.add(cyl(x, y + 0.2, 0.0, 0.04, 0.14, 8, side='brass', top='brass'))
                R.nocol.add(frustum(x, y + 0.2, 1.08, 1.3, 0.22, 0.07, 10, 'green', inner='ivory'))
                R.light(cyl(x, y + 0.2, 1.12, 1.14, 0.1, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # the aisle down the middle: flagstones through a carpet of moss
    for (x0, x1) in ((NX0, 15.1), (16.9, NX1)):
        R.nocol.add(box(x0 + 0.05, 3.5, 0.0, x1 - 0.05, CY - 1.9, 0.04, 'moss'))
    for k in range(20):
        y = 3.6 + k * 0.95
        R.nocol.add(box(15.3 + rnd.uniform(-0.1, 0.1), y, 0.0, 16.7 + rnd.uniform(-0.1, 0.1), y + 0.8, 0.02, 'slate'))
        R.nocol.add(box(15.1, y + 0.8, 0.0, 16.9, y + 0.95, 0.03, 'moss'))


def books(R, rnd):
    # aisles: tall cases on the outer walls; galleries: again; the arcade piers facing the nave
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        if a < 9: sh(R, '+x', T, a, b, rows=15, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=15, frame='walnut')
        if a > 9: sh(R, '+x', T, a, HOLE - 0.3, z=LH, rows=10, frame='walnut')
        else: sh(R, '+x', T, a, b, z=LH, rows=10, frame='walnut')
        sh(R, '-x', W - T, a, b, z=LH, rows=10, frame='walnut')
        moss_slab(R, W - T - 0.4, a, W - T, b, 6.54, 0.08, 0.02, 0.9, rnd)
        moss_slab(R, W - T - 0.4, a, W - T, b, LH + 4.34, 0.08, 0.02, 0.6, rnd)
    for (y0, y1) in ((5.6, 8.4), (11.6, 14.4), (17.6, 19.4)):
        sh(R, '+x', NX0, y0 + 0.1, y1 - 0.1, rows=13, frame='walnut')
        sh(R, '-x', NX1, y0 + 0.1, y1 - 0.1, rows=13, frame='walnut')
        for x in (NX0 + 0.2, NX1 - 0.2):
            moss_slab(R, x - 0.22, y0 + 0.1, x + 0.22, y1 - 0.1, 13 * 0.42 + 0.18, 0.1, 0.04, 1.2, rnd)
    # the south and north ends of the aisles, both floors
    for (x0, x1) in ((0.8, 6.2), (25.8, W - 0.8)):
        sh(R, '+y', T, x0, x1, rows=15, frame='walnut'); sh(R, '-y', W - T, x0, x1, rows=15, frame='walnut')
        sh(R, '+y', T, x0, x1, z=LH, rows=10, frame='walnut'); sh(R, '-y', W - T, x0, x1, z=LH, rows=10, frame='walnut')
    # moss on the floors of the aisles, the galleries
    for k in range(50):
        x = rnd.choice((rnd.uniform(1.0, GX0 - 0.5), rnd.uniform(GX1 + 0.5, W - 1.0)))
        y = rnd.uniform(1.0, W - 1.0); z = rnd.choice((0.0, LH))
        R.nocol.add(blob(x, y, z, rnd.uniform(0.4, 1.3), rnd.uniform(0.4, 1.3), 0.04, 'moss', 8, 3, rnd.uniform(0, 3)))


def lights(R, rnd):
    def chandelier(x, y, z, top, r=1.3, n=10):
        R.nocol.add(cyl(x, y, z + 0.1, top, 0.02, 6, side='iron', caps=False))
        R.nocol.add(ring(x, y, z, z + 0.08, r - 0.06, r + 0.06, 24, top='iron', bottom='iron', inner='iron', outer='iron'))
        for k in range(n):
            a = 2 * math.pi * k / n
            R.nocol.add(cyl(x + r * math.cos(a), y + r * math.sin(a), z + 0.08, z + 0.26, 0.03, 6, side='ivory', caps=False))
            R.light(sphere(x + r * math.cos(a), y + r * math.sin(a), z + 0.32, 0.07, 6, 3, 'e_candle'))
        strands(R, x - r, y, x + r, y, z, 6, 0.9, rnd)
    for y in (8.0, 16.0, 24.5):
        chandelier(16.0, y, 7.2, 14.8)
    for (x0, x1) in ((T, GX0), (GX1, W - T)):
        for y in (4.0, 12.0, 20.0, 28.0):
            bulb(R, (x0 + x1) / 2, y, 5.0, r=0.16, top=AH)
            bulb(R, (x0 + x1) / 2, y, LH + 3.4, r=0.14, top=GZ1, m='e_dim')
    for (x, y) in ((2.0, 3.0), (W - 2.0, 3.0), (2.0, W - 3.0), (W - 2.0, W - 3.0)):
        R.light(sphere(x, y, 2.4, 0.1, 8, 4, 'e_amber'))
        R.parts.add(cyl(x, y, 0.0, 2.3, 0.03, 6, side='iron', caps=False))
