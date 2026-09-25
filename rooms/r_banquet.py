"""The Banquet: a vaulted hall of books with one table down the whole length of it, laid for sixty:
linen, plates, glasses, candles lit, the food still warm, every chair pushed back as if everybody stood
up at once. In the north wall one of the bookcases is a service door, and behind it is the kitchen,
where the stove is still going and a roast is half carved."""
from kit_h10 import *

W, D = 32.0, 16.0
YN = 12.4                        # the hall's north wall; the kitchen is behind it
YC = 6.4                         # the table's axis
TX0, TX1 = 4.2, 27.8             # the table's ends
TW = 0.7                         # half its width
JAMB, RISE = 4.7, 2.7
KX0, KX1, KY0, KY1, KH = 10.3, 21.7, 12.75, 15.6, 3.1    # the kitchen
FX0, FX1 = 15.4, 16.6                                     # the false bookcase


def make():
    R = Room('banquet', 2, 1, res=2048)
    R.sockets(floor='floor', wall='tile')
    c = (T + YN) / 2
    vault_cut(R, 'x', c, YN - T + 0.04, T - 0.02, W - T + 0.02, 0.0, JAMB, rise=RISE, m='plaster', floor='terrazzo', wall='tile')
    ribs(R, 'x', c, YN - T, [T + (W - 2 * T) * k / 8 for k in range(1, 8)], 0.0, JAMB, rise=RISE, d=0.3, t=0.4)
    tunnel_y(R, 8.0, YN - 0.05, D - T - 0.5, floor='terrazzo')
    tunnel_y(R, 24.0, YN - 0.05, D - T - 0.5, floor='terrazzo')
    walls(R)
    feast(R)
    kitchen(R)
    lights(R)
    navloop(R, [(2.2, 2.6), (9.0, 2.6), (16.0, 2.4), (23.0, 2.6), (29.8, 2.6), (30.4, 6.4), (29.8, 10.2), (23.0, 10.4),
                (16.0, 10.6), (9.0, 10.4), (2.2, 10.2), (1.6, 6.4)])
    secret(R, 16.0, 13.9, 0.0, 'The Kitchen',
           'Behind the service door the kitchen is still working: the stove lit, the pans hot, a roast half carved on the board. Whoever was cooking has only just stepped out, and has been only just stepping out for a very long time.')
    fx(R, 'dust', [TX0, YC - 2.5, 0.8, TX1, YC + 2.5, 5.0])
    fx(R, 'fog', [KX0, KY0, 0.0, KX1, KY1, KH], density=0.04)
    return done(R, 'The Banquet', weight=4, probe=(16.0, 10.0, 2.4),
                blurb='A table laid for sixty, down the whole length of the hall; the candles are lit, the food is hot, and every chair has been pushed back from it. You have missed something. You are always just missing it.')


# ---------------------------------------------------------------------------
def walls(R):
    rows = 10
    for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, W - 0.6)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, 6.1), (9.9, FX0 - 0.05), (FX1 + 0.05, 22.1), (25.9, W - 0.6)):
        sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
    false_case(R, FX1, YN, FX1 - FX0, '-y', rows=rows, frame='walnut', h=2.3, depth=0.4, floor='floor')
    R.cut(box(FX0 + 0.05, YN - 0.1, 0, FX1 - 0.05, KY0 + 0.05, 2.3, 'wood', bottom='floor', top='wood'))
    for (a, b) in ((0.6, 4.4), (8.4, YN - 0.4)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    for cx in (8.0, 24.0):
        sh(R, '+y', T, cx - 1.9, cx + 1.9, z=3.6, rows=2, frame='walnut')
        sh(R, '-y', YN, cx - 1.9, cx + 1.9, z=3.6, rows=2, frame='walnut')
    sh(R, '+x', T, 4.4, 8.4, z=3.6, rows=2, frame='walnut')
    sh(R, '-x', W - T, 4.4, 8.4, z=3.6, rows=2, frame='walnut')
    # a cornice over the cases, and the long runner under the table
    for (x0, y0, x1, y1) in ((T, T, W - T, T + 0.5), (T, YN - 0.5, W - T, YN)):
        R.parts.add(box(x0, y0, 4.45, x1, y1, 4.6, 'walnut'))
    rug(R, TX0 - 1.2, YC - 2.2, TX1 + 1.2, YC + 2.2, m='carpet', border='gilt')


def feast(R):
    rs = rng(9)
    # the table and its cloth
    g = Geo()
    g.add(box(TX0, YC - TW, 0.72, TX1, YC + TW, 0.76, 'walnut', skip=('+z',)))
    g.add(box(TX0 - 0.03, YC - TW - 0.03, 0.5, TX1 + 0.03, YC + TW + 0.03, 0.77, 'cloth', skip=('-z',)))
    n = 8
    for k in range(n + 1):
        x = TX0 + 0.15 + (TX1 - TX0 - 0.3) * k / n
        for y in (YC - TW + 0.12, YC + TW - 0.12):
            g.add(box(x - 0.05, y - 0.05, 0, x + 0.05, y + 0.05, 0.5, 'walnut', skip=('-z', '+z')))
    R.parts.add(g)
    # places: plate, napkin, knife and fork, a glass; chairs pushed back
    pl = Geo(); cut = Geo(); gl = Geo(); ch = Geo(); nap = Geo()
    nplaces = 30
    for k in range(nplaces):
        x = TX0 + 0.4 + (TX1 - TX0 - 0.8) * (k + 0.5) / nplaces
        for side in (-1, 1):
            y = YC + side * (TW - 0.24)
            pl.add(hdisc(x, y, 0.772, 0.14, 10, 'ivory'))
            pl.add(hdisc(x, y, 0.776, 0.09, 8, 'bed'))
            cut.add(box(x - 0.2, y - 0.08, 0.77, x - 0.185, y + 0.1, 0.778, 'chrome'))
            cut.add(box(x + 0.185, y - 0.08, 0.77, x + 0.2, y + 0.1, 0.778, 'chrome'))
            if rs.random() < 0.75:
                nap.add(box(x - 0.06, y - 0.06, 0.778, x + 0.06, y + 0.06, 0.81, 'cloth', skip=('-z',)))
            else:
                nap.add(box(-0.12, -0.08, 0.0, 0.12, 0.08, 0.02, 'cloth', skip=('-z',)).xform(rs.uniform(0, 3), x + rs.uniform(-0.1, 0.1), y + side * 0.05, 0.77))
            gx, gy = x + 0.16, y - side * 0.2
            if rs.random() < 0.9:
                gl.add(cyl(gx, gy, 0.87, 0.97, 0.035, 6, side='chrome', caps=False))
                gl.add(hdisc(gx, gy, 0.93, 0.03, 6, 'fruit' if rs.random() < 0.5 else 'gilt'))
                gl.add(box(gx - 0.008, gy - 0.008, 0.77, gx + 0.008, gy + 0.008, 0.87, 'chrome', skip=('-z', '+z')))
                gl.add(hdisc(gx, gy, 0.772, 0.035, 6, 'chrome'))
            else:
                # knocked over
                gl.add(rot(cyl(0, 0, -0.05, 0.05, 0.035, 6, side='chrome', caps=False), 'x', math.pi / 2).xform(rs.uniform(0, 3), gx, gy, 0.81))
            # the chair, pushed back and turned a little
            back = rs.uniform(0.35, 1.0)
            cy = y + side * (0.5 + back)
            face = -side * math.pi / 2 + rs.uniform(-0.45, 0.45)
            ch.add(lchair(x + rs.uniform(-0.15, 0.15), cy, face, frame='walnut', seat='velvet', back_h=1.05))
            R.spot('sit', x, cy, 0.48, face)
    R.nocol.add(pl); R.nocol.add(cut); R.nocol.add(gl); R.nocol.add(nap)
    R.parts.add(ch)
    # candelabra down the middle, and the food between them
    fd = Geo()
    for k in range(13):
        x = TX0 + 1.0 + (TX1 - TX0 - 2.0) * k / 12
        candlestick(R, x, YC, 0.77, 0.55, arms=4 if k % 2 == 0 else 0, rs=rs)
        if k < 12:
            xm = x + (TX1 - TX0 - 2.0) / 24
            kind = k % 4
            fd.add(hdisc(xm, YC, 0.775, 0.3, 12, 'gilt'))
            if kind == 0:
                fd.add(blob(xm, YC, 0.8, 0.26, 0.17, 0.13, 10, 4, 'food'))
                for s_ in (-1, 1): fd.add(blob(xm + s_ * 0.24, YC + 0.1, 0.8, 0.06, 0.04, 0.03, 6, 3, 'ivory'))
            elif kind == 1:
                for j in range(9):
                    a = rs.uniform(0, 6.28); d = rs.uniform(0, 0.18)
                    fd.add(blob(xm + math.cos(a) * d, YC + math.sin(a) * d, 0.82 + rs.uniform(0, 0.08), 0.05, 0.05, 0.05, 6, 3, rs.choice(('fruit', 'grape', 'gilt', 'fruit'))))
            elif kind == 2:
                fd.add(cyl(xm, YC, 0.78, 0.86, 0.22, 12, side='food', top='oxblood'))
                fd.add(blob(xm - 0.34, YC - 0.35, 0.8, 0.14, 0.07, 0.06, 8, 3, 'food'))
            else:
                fd.add(cyl(xm - 0.1, YC, 0.78, 1.02, 0.07, 8, side='ivory', top='ivory'))
                fd.add(blob(xm + 0.14, YC + 0.05, 0.82, 0.14, 0.09, 0.07, 8, 3, 'food'))
    R.nocol.add(fd)
    # a chair knocked right over at the far end, and a napkin on the floor
    ov = lchair(0, 0, 0.0, frame='walnut', seat='velvet', back_h=1.05)
    rot(ov, 'y', math.pi / 2)
    R.nocol.add(ov.xform(0.7, TX1 + 1.1, YC + 0.9, 0.25))
    R.nocol.add(box(-0.15, -0.15, 0, 0.15, 0.15, 0.015, 'cloth').xform(0.3, TX0 - 0.6, YC - 0.8, 0.0))


def kitchen(R):
    R.cut(box(KX0, KY0, 0, KX1, KY1, KH, 'ivory', bottom='terrazzo', top='plaster'))
    # the range along the back wall, its hood, the fire in it
    g = Geo()
    g.add(box(KX0 + 1.0, KY1 - 0.75, 0, KX0 + 5.0, KY1, 0.9, 'iron'))
    g.add(box(KX0 + 0.9, KY1 - 0.8, 1.6, KX0 + 5.1, KY1, 1.75, 'bronze'))
    g.add(box(KX0 + 1.3, KY1 - 0.45, 1.75, KX0 + 4.7, KY1, KH, 'bronze', skip=('+z',)))
    for k in range(4):
        x = KX0 + 1.5 + k * 1.0
        g.add(cyl(x, KY1 - 0.4, 0.9, 1.08, 0.16, 10, side='bronze' if k % 2 else 'iron', top='iron'))
    g.add(box(KX0 + 1.3, KY1 - 0.77, 0.15, KX0 + 2.6, KY1 - 0.75, 0.6, 'black'))
    g.add(box(KX0 + 3.4, KY1 - 0.77, 0.15, KX0 + 4.7, KY1 - 0.75, 0.6, 'black'))
    R.parts.add(g)
    R.light(box(KX0 + 1.4, KY1 - 0.78, 0.2, KX0 + 2.5, KY1 - 0.77, 0.34, 'e_flame'))
    R.light(box(KX0 + 3.5, KY1 - 0.78, 0.2, KX0 + 4.6, KY1 - 0.77, 0.3, 'e_flame'))
    # the work table, the half-carved roast, a knife, bowls, a tower of clean plates
    R.parts.add(ltable(KX0 + 2.2, 13.55, KX1 - 2.0, 14.2, 0.88, 'steel', top='oak'))
    fd = Geo()
    fd.add(box(KX0 + 3.0, 13.6, 0.88, KX0 + 3.8, 14.15, 0.92, 'oak'))
    fd.add(blob(KX0 + 3.4, 13.88, 0.95, 0.28, 0.18, 0.14, 10, 4, 'food'))
    fd.add(box(KX0 + 3.75, 13.75, 0.92, KX0 + 4.05, 13.77, 0.95, 'chrome'))
    for k in range(4):
        fd.add(box(KX0 + 3.9 + k * 0.05, 13.95, 0.92 + k * 0.008, KX0 + 4.1 + k * 0.05, 14.08, 0.93 + k * 0.008, 'food'))
    for k in range(3):
        fd.add(cyl(KX0 + 5.2 + k * 0.55, 13.85, 0.88, 1.0, 0.16, 10, side='ivory', top='food' if k == 1 else 'ivory'))
    for k in range(14):
        fd.add(cyl(KX1 - 3.2, 13.85, 0.88 + k * 0.02, 0.9 + k * 0.02, 0.14, 10, side='ivory', top='ivory', bottom='ivory'))
    R.nocol.add(fd)
    # pans hanging on a rail over the table, shelves of jars, a sink, an apron on a hook
    R.nocol.add(box(KX0 + 2.2, 13.86, 2.4, KX1 - 2.0, 13.9, 2.44, 'iron'))
    pn = Geo()
    for k in range(12):
        x = KX0 + 2.5 + k * 0.6
        r = 0.1 + 0.05 * (k % 3)
        pn.add(box(x - 0.01, 13.87, 2.4 - 0.25, x + 0.01, 13.89, 2.4, 'iron'))
        pn.add(cyl(x, 13.88, 2.15 - 0.05, 2.15, r, 10, side='bronze', top='bronze', bottom='bronze').xform(0, 0, 0, 0))
    R.nocol.add(pn)
    sh(R, '-y', KY1, KX0 + 5.4, KX1 - 1.4, rows=5, frame='oak', depth=0.3)
    R.parts.add(box(KX1 - 1.3, KY1 - 0.7, 0, KX1, KY1, 0.9, 'slate', top='slate'))
    R.nocol.add(box(KX1 - 1.15, KY1 - 0.6, 0.75, KX1 - 0.15, KY1 - 0.1, 0.9, 'steel'))
    R.nocol.add(box(KX0 + 0.1, KY0 + 0.3, 0.9, KX0 + 0.14, KY0 + 0.8, 1.7, 'cloth'))
    R.parts.add(cyl(KX0 + 0.7, 13.3, 0, 0.65, 0.2, 10, side='oak', top='oak'))
    R.spot('sit', KX0 + 0.7, 13.3, 0.65, 0.0)
    bulb(R, KX0 + 4.0, 13.9, KH - 0.6, r=0.1, m='e_lamp', top=KH)
    bulb(R, KX1 - 3.0, 13.9, KH - 0.6, r=0.1, m='e_lamp', top=KH)
    a, b = R.navpt(KX0 + 1.0, 13.1), R.navpt(KX1 - 1.0, 13.1)
    R.link(a, b)


def lights(R):
    for x in (8.0, 16.0, 24.0):
        chandelier(R, x, YC, 4.4, 1.3, n=10, chain=7.2, bulb=0.12)
    # sconces on the walls between the cases, and a pair of amber night lamps at the ends
    for x in (4.4, 12.0, 20.0, 27.6):
        sconce(R, x, T + 0.4, 3.0, math.pi / 2, m='e_lamp')
        sconce(R, x, YN - 0.4, 3.0, -math.pi / 2, m='e_lamp')
    for x in (1.2, W - 1.2):
        floor_lamp(R, x, 1.2, 1.6, m='e_amber')
        floor_lamp(R, x, YN - 1.0, 1.6, m='e_amber')
