"""The Card Catalogue: one cabinet of index-card drawers, fourteen metres tall and fifty-five long, down
the middle of a marble hall. Brass pulls the size of door handles, label frames you could post a
letter through, rolling ladders on a rail, an iron walkway along its face at the upper floor. One
drawer at the bottom has been pulled out and its front let down like a drawbridge: you can walk in
among the cards. It goes back further than a drawer should."""
from lib import *
from kit_h2 import *

NCOL, NROW = 14, 8
DWID, DHT = 3.9, 1.75
CY0, CY1 = 13.0, 19.0          # the cabinet's south and north faces
CH = NROW * DHT                # its height
OC = 4                         # the open drawer's column
GAL = 3.0                      # the south gallery's depth
WZ = LH                        # walkway and gallery floor
WY = CY0 - 1.4                 # the walkway's outer edge
TUN = (15.5 - 1.1, 15.5 + 1.1)  # the tunnel inside the cabinet (y range)
RR = (43.0, 49.6, 13.7, 18.3)  # the reading room at the end of it
RRH = 3.2


def cab_x(W):
    x0 = (W - NCOL * DWID) / 2
    return x0, x0 + NCOL * DWID


def make():
    R = Room('cardcatalogue', 4, 2, levels=2, res=2048)
    W, D = R.W, R.D
    keep = [('S', i, 1) for i in range(4)]
    seal_sockets(R, all_sockets_except(R, keep=keep), floor='marble', wall='tile')
    X0, X1 = cab_x(W)
    HT = R.hi - 0.2
    # the hall round the cabinet, and thin cutters that give the cabinet its walnut faces
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, W - T + 0.02, CY0 - 0.15), (T - 0.02, CY1 + 0.15, W - T + 0.02, D - T + 0.02),
                             (T - 0.02, T - 0.02, X0 - 0.15, D - T + 0.02), (X1 + 0.15, T - 0.02, W - T + 0.02, D - T + 0.02)):
        R.cut(box(x0, y0, 0, x1, y1, HT, 'tile', bottom='marble', top='plaster'))
    for (x0, y0, x1, y1) in ((X0 - 0.3, CY0 - 0.3, X1 + 0.3, CY0), (X0 - 0.3, CY1, X1 + 0.3, CY1 + 0.3),
                             (X0 - 0.3, CY0 - 0.3, X0, CY1 + 0.3), (X1, CY0 - 0.3, X1 + 0.3, CY1 + 0.3)):
        R.cut(box(x0, y0, 0, x1, y1, HT, 'walnut', bottom='marble', top='plaster'))
    R.cut(box(X0 - 0.3, CY0 - 0.3, CH, X1 + 0.3, CY1 + 0.3, HT, 'plaster', bottom='walnut'))
    cabinet(R, X0, X1)
    open_drawer(R, X0)
    tunnel(R, X0)
    upper(R, W, D, X0, X1)
    hall(R, W, D, X0, X1, HT)
    R.spot('probe', 30.0, 6.0, 3.0)
    R.meta.update(label='The Card Catalogue', weight=3,
                  blurb='Somewhere in these drawers is a card for every book in the library, including yours. The drawers are the size of cars. One of them has been left open.')
    R.meta['box'] = [[T, 0, T], [W - T, HT, D - T]]
    return tidy(R)


def cabinet(R, X0, X1):
    """Drawer fronts on both long faces: a lattice of walnut stiles and rails, a brass label frame
    and pull on each drawer; plinth and cornice; brass rails for the ladders."""
    for (yf, sgn) in ((CY0, -1), (CY1, 1)):
        xs = []
        for c in range(NCOL + 1):
            x = X0 + c * DWID; xs += [x - 0.07, x + 0.07]
        xs[0] = X0; xs[-1] = X1
        zs = []
        for r in range(NROW + 1):
            z = r * DHT; zs += [max(0.0, z - 0.06), min(CH, z + 0.06)]
        hole = lambda i, j: (i % 2 == 1 and j % 2 == 1) or (sgn < 0 and (i // 2 == OC) and i % 2 == 1 and j <= 1)
        R.parts.add(lattice(xs, zs, hole, yf + sgn * 0.06, 'walnut', facing=sgn))
        g = Geo()
        # the stiles' and rails' edges: one strip each way, drawn once per line
        for x in xs[1:-1:2]:
            pass
        for c in range(NCOL):
            for r in range(NROW):
                if sgn < 0 and c == OC and r == 0: continue
                xc = X0 + (c + 0.5) * DWID; zc = r * DHT
                # label frame and card, pull
                y = yf + sgn * 0.06
                lab = box(xc - 0.5, min(y, y + sgn * 0.04), zc + 1.05, xc + 0.5, max(y, y + sgn * 0.04), zc + 1.42, 'brass', skip=('-z',) if False else ())
                g.add(lab)
                g.add(box(xc - 0.4, min(y + sgn * 0.04, y + sgn * 0.045), zc + 1.1, xc + 0.4, max(y + sgn * 0.04, y + sgn * 0.045), zc + 1.37, 'ivory'))
                g.add(box(xc - 0.28, min(y, y + sgn * 0.16), zc + 0.62, xc + 0.28, max(y, y + sgn * 0.16), zc + 0.78, 'brass', skip=('+y' if sgn < 0 else '-y',)))
        R.parts.add(g)
        # plinth, cornice, ladder rails
        R.parts.add(box(X0 - 0.1, min(yf, yf + sgn * 0.2), CH - 0.3, X1 + 0.1, max(yf, yf + sgn * 0.2), CH, 'walnut'))
        R.parts.add(box(X0 - 0.2, min(yf, yf + sgn * 0.35), CH, X1 + 0.2, max(yf, yf + sgn * 0.35), CH + 0.25, 'walnut'))
        R.nocol.add(box(X0, min(yf, yf + sgn * 0.42), CH - 0.55, X1, min(yf, yf + sgn * 0.42) + 0.06, CH - 0.49, 'brass'))
        for x in (X0 + 0.1, X1 - 0.1):
            pass
    # the ends: plain walnut with a brass plate
    for (x, sgn) in ((X0, -1), (X1, 1)):
        R.parts.add(box(min(x, x + sgn * 0.05), 14.4, 6.0, max(x, x + sgn * 0.05), 17.6, 7.6, 'brass'))
        R.parts.add(box(min(x, x + sgn * 0.08), 14.8, 6.3, max(x, x + sgn * 0.08), 17.2, 7.3, 'ivory'))
    # rolling ladders leaning on the south face, below and above the walkway
    for (x, z0, h) in ((9.5, 0.0, 7.5), (17.0, 0.0, 7.5), (31.0, 0.0, 7.5), (46.0, 0.0, 7.5), (14.0, WZ, 5.6), (27.5, WZ, 5.6), (40.0, WZ, 5.6), (52.0, WZ, 5.6)):
        g = ladder(x, CY0 - 0.08 if z0 > 0 else CY0 - 0.08, -math.pi / 2, h=h, lean=1.1 if z0 == 0 else 0.9)
        g.v = [(a, b, c + z0) for a, b, c in g.v]
        R.nocol.add(g)
    for (x, h) in ((12.0, 13.4), (36.0, 13.4), (50.0, 13.4)):
        R.nocol.add(ladder(x, CY1 + 0.08, math.pi / 2, h=h, lean=2.4))


def open_drawer(R, X0):
    """The open drawer: pulled five metres out, its front let down onto the floor. Cards the size of
    doors stand in two blocks with a way between them, down the rod."""
    xa = X0 + OC * DWID + 0.1; xb = xa + DWID - 0.2
    out = 5.2
    y0 = CY0 - out
    # the drawer's sides and floor (open front)
    g = Geo()
    g.add(box(xa, y0, 0, xb, CY0, 0.12, 'walnut', top='oak', skip=('-z',)))
    for (x0, x1) in ((xa, xa + 0.1), (xb - 0.1, xb)):
        g.add(box(x0, y0, 0.12, x1, CY0 + 0.1, 1.6, 'walnut', top='oak', skip=('-z',)))
    R.parts.add(weld(g))
    # the front, let down: lying on the floor as a ramp in
    R.parts.add(hexa([(xa, y0 - 1.65, 0.0), (xb, y0 - 1.65, 0.0), (xb, y0, 0.0), (xa, y0, 0.0),
                      (xa, y0 - 1.65, 0.04), (xb, y0 - 1.65, 0.04), (xb, y0, 0.12), (xa, y0, 0.12)], 'walnut', top='walnut'))
    xc = (xa + xb) / 2
    R.nocol.add(box(xc - 0.5, y0 - 1.2, 0.05, xc + 0.5, y0 - 0.85, 0.07, 'brass'))
    R.nocol.add(box(xc - 0.3, y0 - 0.6, 0.05, xc + 0.3, y0 - 0.42, 0.12, 'brass'))
    # the cards: two blocks with the rod's way between them
    rnd = random.Random(15)
    cards = Geo()
    pw = 1.1
    for (c0, c1) in ((xa + 0.12, xc - pw / 2), (xc + pw / 2, xb - 0.12)):
        y = y0 + 0.5
        R.col.add(box(c0, y0 + 0.4, 0.12, c1, CY0 - 0.3, 2.4, 'tile'))
        while y < CY0 - 0.4:
            lean = (rnd.random() - 0.5) * 0.12
            h = 2.15 + rnd.random() * 0.1
            card = box(c0, -0.012, 0, c1, 0.012, h, 'ivory', skip=('-z',))
            card.add(box(c0, -0.014, h - 0.25, c1, 0.014, h - 0.22, 'oxblood', skip=('-z', '+z', '-x', '+x')))
            if rnd.random() < 0.18:   # a guide card with a tab
                tx = c0 + rnd.random() * (c1 - c0 - 0.5)
                card.add(box(tx, -0.014, h, tx + 0.45, 0.014, h + 0.2, 'leather'))
            rot(card, 'x', lean)
            card.v = [(a, b + y, c + 0.12) for a, b, c in card.v]
            cards.add(card)
            y += 0.22 + rnd.random() * 0.08
    R.nocol.add(cards)
    # a brass rod down the middle of the way, at the floor
    R.nocol.add(box(xc - 0.03, y0 + 0.2, 0.12, xc + 0.03, CY0 + 1.0, 0.18, 'brass'))
    R.meta.setdefault('_nav', {})['drawer'] = (xc, y0 - 2.3, y0 + 1.0)


def tunnel(R, X0):
    """Into the cabinet: the drawer's slot goes back, turns, and runs on between walls of cards to a
    reading room somebody made in the middle of the catalogue."""
    xa = X0 + OC * DWID + 0.1; xb = xa + DWID - 0.2
    xc = (xa + xb) / 2
    # the drawer's slot in the cabinet, and the tunnel east
    R.cut(box(xa + 0.1, CY0 - 0.35, 0.12, xb - 0.1, CY0 + 0.35, DHT - 0.06, 'walnut', bottom='oak', top='walnut'))
    R.cut(box(xa, CY0 + 0.3, 0.12, xb, TUN[1], 2.5, 'ivory', bottom='oak', top='walnut'))
    R.cut(box(xb - 0.1, TUN[0], 0.12, RR[0] + 0.05, TUN[1], 2.5, 'ivory', bottom='oak', top='walnut'))
    # the walls of cards: guide cards standing out every so often, the card tops overhead
    g = Geo(); lamps = Geo()
    x = xb + 0.6
    k = 0
    while x < RR[0] - 0.4:
        for (y, s) in ((TUN[0], 1), (TUN[1], -1)):
            g.add(box(x - 0.015, min(y, y + s * 0.25), 0.12, x + 0.015, max(y, y + s * 0.25), 2.5, 'leather', skip=('-z', '+z')))
            if k % 3 == 0:
                g.add(box(x - 0.2, min(y, y + s * 0.02), 1.9, x + 0.25, max(y, y + s * 0.02), 2.2, 'oxblood', skip=('-z', '+z')))
        if k % 4 == 1:
            lamps.add(box(x - 0.1, 15.45, 2.38, x + 0.1, 15.55, 2.44, 'e_dim'))
        x += 1.3; k += 1
    # red rules along the card walls
    for (y, s) in ((TUN[0], 1), (TUN[1], -1)):
        g.add(box(xb, min(y, y + s * 0.01), 1.55, RR[0], max(y, y + s * 0.01), 1.58, 'oxblood', skip=('-x', '+x')))
        for kk in range(4):
            z = 0.5 + kk * 0.25
            g.add(box(xb, min(y, y + s * 0.006), z, RR[0], max(y, y + s * 0.006), z + 0.012, 'green', skip=('-x', '+x')))
    R.nocol.add(g); R.light(lamps)
    # the reading room
    x0, x1, y0, y1 = RR
    R.cut(box(x0, y0, 0, x1, y1, RRH, 'walnut', bottom='carpet', top='plaster'))
    R.parts.add(box(x0, y0, 0, x1, y0 + 0.04, 1.0, 'oak', skip=('-z',)))
    # little drawers all round (a catalogue inside the catalogue), a desk, a lamp, a chair, a cot
    g = Geo()
    for (yb, s, face) in ((y1, -1, '-y'),):
        for c in range(12):
            for r in range(5):
                xx = x0 + 0.4 + c * 0.48; zz = 1.0 + r * 0.36
                g.add(box(xx, yb - 0.03, zz, xx + 0.44, yb, zz + 0.32, 'oak', skip=('+y',)))
                g.add(box(xx + 0.17, yb - 0.06, zz + 0.12, xx + 0.27, yb - 0.03, zz + 0.16, 'brass', skip=('+y',)))
    R.parts.add(g)
    desk(R, x0 + 2.2, y0 + 1.2, x0 + 4.0, y0 + 2.1, h=0.76)
    green_lamp(R, x0 + 3.6, y0 + 1.65, 0.76, math.pi / 2)
    open_book_prop(R, x0 + 2.9, y0 + 1.65, 0.76)
    for k in range(3):
        R.nocol.add(box(x0 + 2.4 + k * 0.1, y0 + 1.35 + k * 0.05, 0.76 + k * 0.004, x0 + 2.55 + k * 0.1, y0 + 1.45 + k * 0.05, 0.764 + k * 0.004, 'ivory'))
    seat(R, x0 + 3.0, y0 + 0.75, math.pi / 2)
    R.parts.add(box(x1 - 0.95, y0 + 0.1, 0, x1 - 0.1, y0 + 2.2, 0.42, 'bed', sides='walnut'))
    R.nocol.add(box(x1 - 0.85, y0 + 0.2, 0.42, x1 - 0.2, y0 + 0.6, 0.52, 'ivory'))
    R.spot('bed', x1 - 0.5, y0 + 1.2, 0.42, math.pi / 2)
    bulb(R, (x0 + x1) / 2, (y0 + y1) / 2, RRH - 0.7, r=0.14, m='e_lamp', top=RRH, shade='brass')
    candle(R, x1 - 0.5, y0 + 2.6, 0.0, h=0.2, stand=0.9)
    R.spot('plaque', x0 + 1.0, y1 - 0.1, 1.5, -math.pi / 2)
    secret(R, (x0 + x1) / 2, (y0 + y1) / 2, 0.0, 'The Room in the Catalogue',
           'The drawer went back twenty metres further than the cabinet is deep. At the end of it somebody has set up a desk and a bed, and has been writing out cards of their own.', r=2.5)
    a = R.navpt(xc, CY0 + 0.8, 0.12); b = R.navpt(xc, 15.5, 0.12); c = R.navpt(30.0, 15.5, 0.12); d = R.navpt(RR[0] - 0.6, 15.5, 0.12)
    e = R.navpt(x0 + 1.2, 15.8, 0.0)
    R.link(a, b, c, d, e)
    R.meta['_nav']['tun'] = a


def upper(R, W, D, X0, X1):
    """The south gallery at the upper floor, a stair up to it, two bridges to the iron walkway on the
    cabinet's face."""
    z = WZ
    R.parts.add(box(T, T, z - 0.4, W - T, T + GAL, z, 'plaster', top='oak'))
    SN = 40; SX0 = 30.0; SX1 = SX0 + SN * 0.3; SY0, SY1 = T + GAL + 0.05, T + GAL + 1.85
    railed_flight(R, SX0, SY0, 0.0, SY1 - SY0, SN, z / SN, 0.3, '+x', m='oak', riser='walnut', side='walnut')
    R.parts.add(box(SX1, T + GAL - 0.05, z - 0.4, SX1 + 1.8, SY1, z, 'plaster', top='oak'))
    rail(R, SX1 + 1.75, T + GAL, SX1 + 1.75, SY1, z)
    rail(R, SX1, SY1 - 0.04, SX1 + 1.75, SY1 - 0.04, z)
    # the walkway on the cabinet's south face, on iron brackets
    R.parts.add(box(X0, WY, z - 0.25, X1, CY0 - 0.02, z, 'iron', top='oak'))
    for k in range(NCOL + 1):
        x = X0 + k * DWID
        R.parts.add(beam((x, CY0 - 0.02, z - 1.8), (x, WY + 0.1, z - 0.25), 0.1, 'iron'))
    # bridges
    BR = (10.0, 54.0)
    for bx in BR:
        R.parts.add(box(bx - 0.8, T + GAL - 0.05, z - 0.25, bx + 0.8, WY + 0.05, z, 'iron', top='oak'))
        rail(R, bx - 0.76, T + GAL, bx - 0.76, WY, z, m='brass')
        rail(R, bx + 0.76, T + GAL, bx + 0.76, WY, z, m='brass')
    # rails: gallery edge (open at the bridges and the stair), walkway edge (open at the bridges)
    gy = T + GAL - 0.04
    cuts = sorted([(bx - 0.8, bx + 0.8) for bx in BR] + [(SX1, SX1 + 1.8)])
    xa = T
    for (a, b) in cuts:
        rail(R, xa, gy, a, gy, z); xa = b
    rail(R, xa, gy, W - T, gy, z)
    xa = X0
    for bx in BR:
        rail(R, xa, WY + 0.04, bx - 0.8, WY + 0.04, z); xa = bx + 0.8
    rail(R, xa, WY + 0.04, X1, WY + 0.04, z)
    rail(R, X0 + 0.04, WY, X0 + 0.04, CY0, z); rail(R, X1 - 0.04, WY, X1 - 0.04, CY0, z)
    # books along the gallery wall and above it
    for (a, b) in ((0.7, 6.0), (10.0, 22.0), (26.0, 38.0), (42.0, 54.0), (58.0, W - 0.7)):
        sh(R, '+y', T, a, b, z=z, rows=15, frame='walnut')
    # desks and lamps on the walkway
    for x in (21.0, 37.0):
        desk(R, x - 0.8, CY0 - 0.52, x + 0.8, CY0 - 0.12, z=z, h=0.95)
        green_lamp(R, x, CY0 - 0.32, z + 0.95)
    ids = navloop(R, [(1.6, 1.6), (10.0, 1.6), (24.0, 1.6), (40.0, 1.6), (54.0, 1.6), (W - 1.6, 1.6)], z=z, close=False)
    wk = navloop(R, [(X0 + 0.6, CY0 - 0.95), (10.0, CY0 - 0.95), (32.0, CY0 - 0.95), (54.0, CY0 - 0.95), (X1 - 0.6, CY0 - 0.95)], z=z, close=False)
    R.link(ids[1], wk[1]); R.link(ids[4], wk[3])
    a, b = R.navpt(SX0 - 0.7, (SY0 + SY1) / 2, 0.0), R.navpt(SX1 + 0.9, (SY0 + SY1) / 2 - 0.3, z)
    c = R.navpt(SX1 + 0.9, 1.6, z)
    R.link(a, b, c, ids[3])
    R.meta['_nav']['stair'] = a


def hall(R, W, D, X0, X1, HT):
    rows = 17
    for (a, b) in ((0.7, 6.0), (10.0, 22.0), (26.0, 38.0), (42.0, 54.0), (58.0, W - 0.7)):
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, z=WZ, rows=15, frame='walnut')
    for (a, b) in ((GAL + 1.0, 6.0), (10.0, 22.0), (26.0, 30.0 - 0.5)):
        sh(R, '+y', T, a, b, rows=7, frame='walnut', depth=0.3)
    # reading desks along the north aisle, green lamps
    for k in range(6):
        x = 8.0 + k * 9.6
        R.parts.add(table(x - 1.6, 23.0, x + 1.6, 24.4, 0.78, 'walnut', top='leather'))
        green_lamp(R, x - 0.8, 23.7, 0.78); green_lamp(R, x + 0.8, 23.7, 0.78)
        for s in (-1, 1):
            R.parts.add(chair(x + s * 0.8, 22.4, math.pi / 2)); R.spot('sit', x + s * 0.8, 22.4, 0.48, math.pi / 2)
    # high windows in the end walls, lay-lights over the aisles
    for (x0, x1, xl) in ((T - 0.2, T + 0.02, T - 0.14), (W - T - 0.02, W - T + 0.2, W - T + 0.12)):
        for y in (10.5, 21.5):
            pr = arch_profile(y, 2.2, 9.5, 3.2, 12)
            R.cut(prism(pr, 'x', x0, x1, 'tile'))
            R.light(prism(pr, 'x', xl, xl + 0.02, 'e_sky', cap='e_sky'))
    for (y0, y1) in ((5.0, 9.5), (22.5, 27.5)):
        for k in range(4):
            x = 8.0 + k * 16.0
            R.cut(box(x - 5.0, y0, HT - 0.05, x + 5.0, y1, HT + 0.18, 'plaster'))
            R.light(box(x - 4.6, y0 + 0.4, HT + 0.12, x + 4.6, y1 - 0.4, HT + 0.14, 'e_sky', skip=('+z',)))
    for (x, y) in ((3.8, 12.0), (W - 3.8, 12.0), (3.8, 20.0), (W - 3.8, 20.0)):
        floor_lamp(R, x, y, 1.7)
    for (x, y) in ((1.0, 16.0), (W - 1.0, 16.0)):
        R.light(sphere(x, y, 2.2, 0.1, 10, 5, 'e_amber'))
        R.parts.add(box(x - 0.1, y - 0.1, 2.0, x + 0.1, y + 0.1, 2.08, 'brass'))
    nv = R.meta.pop('_nav')
    s = navloop(R, [(2.2, 6.0), (10.0, 7.5), (nv['drawer'][0], 7.5), (40.0, 7.5), (54.0, 7.5), (W - 2.2, 6.0), (W - 2.2, 16.0), (W - 2.2, 27.0),
                    (40.0, 27.0), (24.0, 27.0), (8.0, 27.0), (2.2, 27.0), (2.2, 16.0)])
    a = R.navpt(nv['drawer'][0], nv['drawer'][1]); b = R.navpt(nv['drawer'][0], nv['drawer'][2], 0.12)
    R.link(s[2], a, b, nv['tun'])
    R.link(s[2], nv['stair'])
