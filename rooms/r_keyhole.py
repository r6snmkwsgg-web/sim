"""The Keyhole: on the upper floor, a hall whose north wall is a gilt escutcheon with a keyhole in it,
big enough to walk through. Beyond, a canyon whose cross-section is the keyhole's: a round vault over
two galleries, and below them a narrow slot lined with books that steps down eight metres to the floor
below. Halfway down, one of the bookcases is not a bookcase."""
from lib import *
from kit_h2 import *

YK, YK2 = 11.6, 12.6        # the keyhole wall
CX0, CX1 = 6.0, 26.0        # the canyon's upper width (the round of the keyhole)
SX0, SX1 = 12.0, 20.0       # the slot (the keyhole's stem)
YL = 15.1                   # the landing's north edge: the stair starts here
KZ = 8.0 + 4.6              # the keyhole circle's centre
KR = 2.2
NST, RISE, RUN = 8, 0.25, 0.3
LAND = 1.0
LAND2 = 2.6
WX1, EX0 = 9.0, 23.0        # the lower side halls stop here (the slot walls are thick)
LR = (9.25, 11.95, 20.0, 24.6)   # the ledge room (x0, x1, y0, y1) at z = 4


def flights():
    """[(y0, z0), ...] of the four flights stepping down north; returns the list and the bottom y."""
    out = []; y = YL; z = 8.0
    for k in range(4):
        out.append((y, z))
        y += NST * RUN; z -= NST * RISE
        if k < 3: y += LAND if k != 1 else LAND2
    return out, y


def make():
    R = Room('keyhole', 2, 2, levels=2, res=2048)
    W, D = R.W, R.D
    R.sockets(floor='terrazzo', wall='tile')
    lower(R, W, D)
    upper(R, W, D)
    keyhole(R)
    canyon(R, W, D)
    ledge(R)
    R.spot('probe', 16.0, 6.0, 9.8)
    R.meta.update(label='The Keyhole', weight=3,
                  blurb='The north wall of the upper hall is a lock, and the lock is open. Through the keyhole the library goes down, and down.')
    R.meta['box'] = [[T, 0, T], [W - T, 15.5, D - T]]
    return tidy(R)


# ---------------------------------------------------------------------------
def lower(R, W, D):
    """The ground floor: a hall along the south, two long halls either side of the slot."""
    H = TOP - 0.1
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, 11.5, H, 'tile', bottom='terrazzo', top='plaster'))
    for (x0, x1) in ((T - 0.02, WX1), (EX0, W - T + 0.02)):
        R.cut(box(x0, 11.4, 0, x1, D - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    # widen at the north end to take the doorways
    R.cut(box(T - 0.02, 27.6, 0, 10.4, D - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(21.6, 27.6, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    # bookcases
    rows = 14
    for (a, b) in ((0.6, 6.0), (10.0, 22.0), (26.0, W - 0.6)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, 6.0), (10.0, 22.0), (26.0, 27.3)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    sh(R, '-x', WX1, 12.0, 27.3, rows=rows, frame='walnut')
    sh(R, '+x', EX0, 12.0, 27.3, rows=rows, frame='walnut')
    sh(R, '-y', 11.5, 9.6, 22.4, rows=rows, frame='walnut')
    # reading tables down the south hall
    for x0 in (4.0, 18.5):
        R.parts.add(table(x0, 5.2, x0 + 9.5, 6.4, 0.78, 'walnut', top='leather'))
        for k in range(3):
            x = x0 + 1.4 + k * 3.4
            desk_lamp(R, x, 5.8, 0.78)
            R.parts.add(chair(x + 0.8, 4.6, math.pi / 2)); R.spot('sit', x + 0.8, 4.6, 0.48, math.pi / 2)
    for (x, y) in ((8.0, 3.0), (24.0, 3.0), (8.0, 9.0), (24.0, 9.0), (4.7, 16.0), (27.3, 16.0), (4.7, 24.0), (27.3, 24.0)):
        bulb(R, x, y, 4.6, r=0.18, m='e_lamp', top=H, shade='brass')
    for (x, y) in ((1.4, 11.0), (W - 1.4, 11.0)):
        R.light(sphere(x, y, 2.4, 0.1, 10, 5, 'e_amber'))
        R.parts.add(box(x - 0.08, y - 0.2, 2.2, x + 0.08, y + 0.2, 2.3, 'brass'))
    ids = navloop(R, [(2.0, 2.0), (8.0, 2.0), (16.0, 2.0), (24.0, 2.0), (30.0, 2.0), (30.0, 10.0), (24.0, 10.0), (16.0, 10.0), (8.0, 10.0), (2.0, 10.0)])
    w = navloop(R, [(4.7, 13.0), (4.7, 20.0), (4.7, 29.5)], close=False)
    e = navloop(R, [(27.3, 13.0), (27.3, 20.0), (27.3, 29.5)], close=False)
    R.link(ids[9], w[0]); R.link(ids[5], e[0])
    NAV['wb'], NAV['eb'] = w[2], e[2]


NAV = {}


def upper(R, W, D):
    """The upper floor: the anteroom along the south, and corridors in from the W1/E1 doorways."""
    z = LH; H = 15.2
    R.cut(box(T - 0.02, T - 0.02, z, W - T + 0.02, YK, H, 'tile', bottom='terrazzo', top='plaster'))
    for (x0, x1) in ((T - 0.02, CX0 + 0.05), (CX1 - 0.05, W - T + 0.02)):
        pr = arch_profile(24.0, 3.0, z, 2.8, 12)
        R.cut(prism(pr, 'x', x0, x1, arch_mats(len(pr), 'terrazzo', 'tile')))
    # coffers with lay-lights
    for k in range(3):
        x = 5.5 + k * 10.5
        R.cut(box(x - 3.5, 2.0, H - 0.05, x + 3.5, 9.6, H + 0.3, 'plaster'))
        R.light(box(x - 3.0, 2.5, H + 0.24, x + 3.0, 9.1, H + 0.26, 'e_sky', skip=('+z',)))
    rows = 15
    for (a, b) in ((0.6, 6.0), (10.0, 22.0), (26.0, W - 0.6)):
        sh(R, '+y', T, a, b, z=z, rows=rows, frame='walnut')
    sh(R, '+x', T, 0.6, 6.0, z=z, rows=rows, frame='walnut'); sh(R, '+x', T, 10.0, YK - 0.1, z=z, rows=rows, frame='walnut')
    sh(R, '-x', W - T, 0.6, 6.0, z=z, rows=rows, frame='walnut'); sh(R, '-x', W - T, 10.0, YK - 0.1, z=z, rows=rows, frame='walnut')
    sh(R, '-y', YK, 0.6, 10.2, z=z, rows=rows, frame='walnut'); sh(R, '-y', YK, 21.8, W - 0.6, z=z, rows=rows, frame='walnut')
    # benches facing the keyhole
    for x in (11.5, 20.5):
        R.parts.add(box(x - 1.2, 5.6, z + 0.42, x + 1.2, 6.1, z + 0.48, 'walnut'))
        R.parts.add(box(x - 1.1, 5.65, z, x + 1.1, 6.05, z + 0.42, 'walnut', skip=('-z',)))
        R.spot('sit', x, 5.85, z + 0.48, math.pi / 2)
    ids = navloop(R, [(2.0, 2.0), (8.0, 2.0), (16.0, 3.0), (24.0, 2.0), (30.0, 2.0), (30.0, 9.5), (20.5, 9.0), (16.0, 9.5), (11.5, 9.0), (2.0, 9.5)], z=z)
    NAV['up'] = ids[7]


def keyhole(R):
    """The keyhole through the wall, its reveal in brass, set in a gilt escutcheon on both faces."""
    z = LH
    # the escutcheon: a shallow gilt recess, round-topped, on each face
    for (y0, y1) in ((YK - 0.05, YK + 0.08), (YK2 - 0.08, YK2 + 0.05)):
        pr = arch_profile(16.0, 7.4, z, 3.2, 24)
        R.cut(prism(pr, 'y', y0, y1, ['terrazzo'] + ['gilt'] * (len(pr) - 1), cap='gilt'))
    # the keyhole: a circle and a flared stem
    circ = circle_pts(16.0, KZ, KR, 40)
    R.cut(prism(circ, 'y', YK - 0.1, YK2 + 0.1, 'brass', cap='brass'))
    hw_top = 1.1; zt = KZ - math.sqrt(KR * KR - hw_top * hw_top) + 0.05
    stem = [(16.0 - 1.6, z), (16.0 + 1.6, z), (16.0 + hw_top, zt), (16.0 - hw_top, zt)]
    R.cut(prism(stem, 'y', YK - 0.1, YK2 + 0.1, ['terrazzo', 'brass', 'brass', 'brass'], cap='brass'))
    # a raised brass rim round the hole, and scrolls, on both faces
    for (yf, sgn) in ((YK + 0.08, -1), (YK2 - 0.08, 1)):
        g = Geo()
        n = 40
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            if math.sin((a0 + a1) / 2) < -0.45: continue          # open at the bottom where the stem is
            q = [(16 + (KR) * math.cos(a0), KZ + KR * math.sin(a0)), (16 + (KR + 0.3) * math.cos(a0), KZ + (KR + 0.3) * math.sin(a0)),
                 (16 + (KR + 0.3) * math.cos(a1), KZ + (KR + 0.3) * math.sin(a1)), (16 + KR * math.cos(a1), KZ + KR * math.sin(a1))]
            g.add(prism(q, 'y', min(yf, yf + sgn * 0.16), max(yf, yf + sgn * 0.16), 'brass', cap='brass'))
        for s in (-1, 1):
            q = [(16 + s * 1.6, z), (16 + s * 1.9, z), (16 + s * (hw_top + 0.3), zt + 0.1), (16 + s * hw_top, zt)]
            if s < 0: q = q[::-1]
            g.add(prism(q, 'y', min(yf, yf + sgn * 0.16), max(yf, yf + sgn * 0.16), 'brass', cap='brass'))
        # scrollwork: rings of gilt about the escutcheon
        for (cx, cz, r) in ((12.9, z + 1.2, 0.5), (19.1, z + 1.2, 0.5), (13.0, z + 4.4, 0.62), (19.0, z + 4.4, 0.62),
                            (14.3, z + 6.3, 0.45), (17.7, z + 6.3, 0.45), (16.0, z + 6.8, 0.35)):
            for i in range(16):
                a0, a1 = 2 * math.pi * i / 16, 2 * math.pi * (i + 1) / 16
                q = [(cx + r * math.cos(a0), cz + r * math.sin(a0)), (cx + (r + 0.12) * math.cos(a0), cz + (r + 0.12) * math.sin(a0)),
                     (cx + (r + 0.12) * math.cos(a1), cz + (r + 0.12) * math.sin(a1)), (cx + r * math.cos(a1), cz + r * math.sin(a1))]
                g.add(prism(q, 'y', min(yf, yf + sgn * 0.08), max(yf, yf + sgn * 0.08), 'gilt', cap='gilt'))
        R.parts.add(weld(g))
    # a light in the keyhole's crown, so the brass shines
    R.light(box(15.6, YK - 0.02, KZ + KR - 0.12, 16.4, YK2 + 0.02, KZ + KR - 0.06, 'e_lamp'))


def canyon(R, W, D):
    z = LH
    # the round of the keyhole: a vault over two galleries
    R.cut(box(CX0, YK2 - 0.02, z, CX1, D - T + 0.02, z + 3.0, 'tile', bottom='terrazzo', top='plaster'))
    pr = arch_profile(16.0, CX1 - CX0, z + 2.99, 0.01, 32, rise=4.35)
    R.cut(prism(pr, 'y', YK2 - 0.02, D - T + 0.02, ['tile'] + ['plaster'] * (len(pr) - 1)))
    # a skylight down the crown
    R.cut(box(15.0, YK2 + 0.6, 15.2, 17.0, D - T - 0.6, 15.5, 'plaster'))
    R.light(box(15.0, YK2 + 0.6, 15.46, 17.0, D - T - 0.6, 15.48, 'e_sky', skip=('+z',)))
    # the stem of the keyhole: the slot, down to the floor below
    R.cut(box(SX0, YL, 0, SX1, D - T + 0.02, z + 0.05, 'tile', bottom='terrazzo', top='tile'))
    # it opens at the bottom into the halls either side
    for (x0, x1) in ((WX1 - 0.1, SX0 + 0.05), (SX1 - 0.05, EX0 + 0.1)):
        pr = arch_profile(30.0, 2.8, 0, 2.4, 12)
        R.cut(prism(pr, 'x', x0, x1, arch_mats(len(pr), 'terrazzo', 'tile')))
    # the stair: four flights, stepping down north, full width of the slot
    fl, yb = flights()
    for k, (y0, z0) in enumerate(fl):
        # a flight descending north = a flight climbing south from its foot
        yf = y0 + NST * RUN; zf = z0 - NST * RISE
        R.flight(SX0, yf, zf, SX1 - SX0, NST, RISE, RUN, '-y', m='terrazzo', riser='tile', side='tile')
        # fill under the flight (solid, so nothing shows through)
        R.parts.add(slope_y(SX0, SX1, y0, yf, 0.0, 0.0, z0, zf))
        if k < 3:
            ly1 = yf + (LAND if k != 1 else LAND2)
            R.parts.add(box(SX0, yf, 0, SX1, ly1, zf, 'tile', top='terrazzo', skip=('-z',)))
    R.parts.add(box(SX0, YL - 0.02, 0, SX1, fl[0][0] + 0.02, z, 'tile', top='terrazzo', skip=('-z',)))
    # bookcases lining the slot, stepping down with it
    for k, (y0, z0) in enumerate(fl):
        yf = y0 + NST * RUN; zf = z0 - NST * RISE
        ly1 = yf + (LAND if k != 1 else LAND2) if k < 3 else D - T
        for (xb, face) in ((SX0, '+x'), (SX1, '-x')):
            if z - z0 >= 0.9:      # along the flight, from its upper end
                sh(R, face, xb, y0 + 0.05, yf - 0.05, z=z0, rows=int((z - z0) / 0.42), frame='walnut')
            rows = int((z - zf) / 0.42)
            if k == 1 and face == '+x':
                # the landing: three cases, the middle one false
                fa, fb = LR[2] + 1.45, LR[2] + 2.95
                sh(R, face, xb, yf + 0.05, fa - 0.05, z=zf, rows=rows, frame='walnut')
                sh(R, face, xb, fa, fb, z=zf, rows=rows, frame='walnut', solid=False)
                sh(R, face, xb, fb + 0.05, ly1 - 0.05, z=zf, rows=rows, frame='walnut')
                continue
            if k == 3:
                sh(R, face, xb, yf + 0.05, 28.4, z=zf, rows=rows, frame='walnut')
            else:
                sh(R, face, xb, yf + 0.05, ly1 - 0.05, z=zf, rows=rows, frame='walnut')
    # the bottom: a floor of terrazzo, a table, a lamp that has been left on
    R.parts.add(table(14.4, yb + 0.5, 17.6, yb + 1.3, 0.78, 'walnut', top='leather'))
    desk_lamp(R, 16.0, yb + 0.9, 0.78)
    bulb(R, 16.0, yb - 3.0, 5.5, r=0.2, m='e_lamp', top=z, shade='brass')
    bulb(R, 16.0, 20.0, 9.5, r=0.2, m='e_lamp', top=15.0, shade='brass')
    # the galleries along the rim: balustrades, desks with green lamps, books on the canyon walls
    for (xe, sgn) in ((SX0, -1), (SX1, 1)):
        rail(R, xe + sgn * 0.12, YL, xe + sgn * 0.12, D - T - 0.2, z, h=1.0, solid=True, mat='tile')
    for (xb, face) in ((CX0, '+x'), (CX1, '-x')):
        sh(R, face, xb, YK2 + 0.2, 22.3, z=z, rows=6, frame='walnut')
        sh(R, face, xb, 25.7, D - T - 0.4, z=z, rows=6, frame='walnut')
    for y in (18.0, 23.5, 28.5):
        for (x0, x1) in ((CX0 + 1.4, CX0 + 3.0), (CX1 - 3.0, CX1 - 1.4)):
            desk(R, x0, y - 1.0, x1, y + 1.0, z=z, h=0.78)
            desk_lamp(R, (x0 + x1) / 2, y, z + 0.78)
    # hanging lamps down the canyon
    for y in (17.0, 22.0, 27.0):
        for x in (9.0, 23.0):
            bulb(R, x, y, 12.2, r=0.16, m='e_lamp', top=14.6)
    # nav: through the keyhole, round the galleries, down the stair
    k0 = R.navpt(16.0, YK2 + 1.2, z)
    R.link(NAV['up'], k0)
    gw = navloop(R, [(9.0, YK2 + 1.2), (9.0, 22.0), (9.0, 30.0)], z=z, close=False)
    ge = navloop(R, [(23.0, YK2 + 1.2), (23.0, 22.0), (23.0, 30.0)], z=z, close=False)
    R.link(k0, gw[0]); R.link(k0, ge[0])
    st = [R.navpt(16.0, fl[0][0] + 0.3, z)]
    for k, (y0, z0) in enumerate(fl):
        yf = y0 + NST * RUN; zf = z0 - NST * RISE
        st.append(R.navpt(16.0, yf + 0.3, zf))
    R.link(k0, *st)
    b = R.navpt(10.5, 30.0, 0.0); c = R.navpt(21.5, 30.0, 0.0)
    R.link(st[-1], b, NAV['wb']); R.link(st[-1], c, NAV['eb'])


def slope_y(x0, x1, y0, y1, zb0, zb1, zt0, zt1, m='tile'):
    return hexa([(x0, y0, zb0), (x1, y0, zb0), (x1, y1, zb1), (x0, y1, zb1), (x0, y0, zt0), (x1, y0, zt0), (x1, y1, zt1), (x0, y1, zt1)], m)


def ledge(R):
    """Halfway down, behind a false bookcase, a narrow room in the thickness of the slot's wall."""
    x0, x1, y0, y1 = LR
    fl, _ = flights()
    zl = fl[1][1] - NST * RISE             # the second landing
    R.cut(box(x0, y0, zl, x1, y1, zl + 2.7, 'plaster', bottom='floor', top='walnut'))
    R.cut(box(x1 - 0.05, y0 + 1.45, zl, SX0 + 0.05, y0 + 2.95, zl + 2.3, 'walnut', bottom='floor', top='walnut'))
    R.parts.add(box(x0 + 0.1, y0 + 0.15, zl, x0 + 1.0, y0 + 2.2, zl + 0.4, 'bed', sides='walnut'))
    R.nocol.add(box(x0 + 0.2, y0 + 0.25, zl + 0.4, x0 + 0.9, y0 + 0.65, zl + 0.5, 'ivory'))
    desk(R, x0 + 0.2, y1 - 1.3, x0 + 1.3, y1 - 0.2, z=zl, h=0.76)
    desk_lamp(R, x0 + 0.75, y1 - 0.5, zl + 0.76)
    open_book_prop(R, x0 + 0.75, y1 - 0.9, zl + 0.76, math.pi / 2)
    seat(R, x0 + 1.8, y1 - 0.75, math.pi, z=zl)
    sh(R, '+x', x0, y0 + 2.4, y1 - 1.6, z=zl, rows=5, frame='walnut', depth=0.28)
    candle(R, x0 + 0.4, y0 + 2.4, zl + 0.4, h=0.2)
    bulb(R, (x0 + x1) / 2, (y0 + y1) / 2, zl + 2.1, r=0.08, m='e_dim', top=zl + 2.7)
    R.spot('plaque', x0 + 0.1, (y0 + y1) / 2, zl + 1.5, 0.0)
    secret(R, (x0 + x1) / 2, y0 + 2.2, zl, 'The Ledge Room',
           'Halfway down the keyhole, a room one bed wide inside the wall. Someone slept here with the whole canyon of books on the other side of a bookcase.', r=1.6)
    a = R.navpt(16.0, y0 + 2.2, zl); b = R.navpt((x0 + x1) / 2 + 0.2, y0 + 2.2, zl)
    R.link(a, b)
