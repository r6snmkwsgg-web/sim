"""The Shrine of Lost Things: a small vaulted chapel of books with a stepped altar in the middle, every
step crowded with candles and with the things people lose: shoes, spectacles, keys, gloves, umbrellas,
photographs, a bear. Its front is hung with a velvet cloth; behind the cloth a low opening goes into the
hollow altar, and a stair goes down from there to the Lost Property office underneath, where somebody
keeps the ledger."""
from kit_h10 import *

W = D = 16.0
CX, CY = 8.4, 8.0              # the altar
RISE = 0.32
HX = [3.4, 2.9, 2.4, 1.9, 1.5]   # half sizes of the tiers (west, north, south sides step in)
HY = [3.0, 2.5, 2.0, 1.5, 1.05]
XF = CX + 1.9                    # the altar's upright east front
HOL = (CX - 1.35, CY - 0.8, CX + 1.35, CY + 0.8)     # the hollow inside
ENT = (CX + 1.35, CY - 0.6, XF + 0.01, CY + 0.6)     # the way into it, behind the cloth
ZH = 4 * RISE                                        # the hollow's ceiling (1.28)
# the stair down to the crypt: climbs +x from its foot (x=SX0, z=-3.0) up to (SX1, 0) inside the hollow
SN, SR, SRUN = 10, 0.21, 0.3
SX1 = CX + 1.2
SX0 = SX1 - SN * SRUN
SY0, SY1 = CY - 0.55, CY + 0.55
KZ = -2.1                                             # the crypt floor
KX0, KX1, KY0, KY1 = 1.0, SX0 + 0.02, 4.2, 11.8


def make():
    R = Room('lostshrine', 1, 1, res=1024, lo=-4.0)
    R.sockets(floor='floor', wall='tile')
    vault_cut(R, 'y', W / 2, W - 2 * T + 0.04, T - 0.02, D - T + 0.02, 0.0, 4.6, rise=2.8, m='plaster', floor='floor', wall='tile')
    ribs(R, 'y', W / 2, W - 2 * T, (4.0, 8.0, 12.0), 0.0, 4.6, rise=2.8, d=0.3, t=0.35, m='tile')
    walls(R)
    altar(R)
    crypt(R)
    lights(R)
    navloop(R, [(2.6, 2.6), (8.0, 2.4), (13.4, 2.6), (13.6, 8.0), (13.4, 13.4), (8.0, 13.6), (2.6, 13.4), (2.4, 8.0)])
    secret(R, (KX0 + KX1) / 2, 8.0, KZ, 'Lost Property',
           'Under the altar is the office where lost things are kept: a ledger of everything anyone ever put down and forgot. Your name is in it, many times, and the last entry is still blank.')
    secret(R, CX, CY, 0.0, 'Inside the Altar', 'Behind the cloth the altar is hollow, and smells of candle smoke and old leather. A stair goes down.', r=1.2)
    fx(R, 'dust', [CX - 3.5, CY - 3.2, 0.5, CX + 3.5, CY + 3.2, 5.0])
    fx(R, 'dust', [KX0, KY0, KZ, KX1, KY1, KZ + 2.4])
    return done(R, 'The Shrine of Lost Things', weight=5, probe=(3.2, 12.6, 2.2),
                  blurb='Candles, hundreds of them, and among the candles everything anybody ever lost: one glove, one shoe, their glasses, their keys. Somebody lights them all, every day, and you never see who.')


# ---------------------------------------------------------------------------
def walls(R):
    rows = 10
    for (a, b) in ((0.6, 6.1), (9.9, W - 0.6)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    for c in (8.0,):
        sh(R, '+y', T, c - 1.9, c + 1.9, z=3.9, rows=1, frame='walnut')
        sh(R, '-y', D - T, c - 1.9, c + 1.9, z=3.9, rows=1, frame='walnut')
        sh(R, '+x', T, c - 1.9, c + 1.9, z=3.9, rows=1, frame='walnut')
        sh(R, '-x', W - T, c - 1.9, c + 1.9, z=3.9, rows=1, frame='walnut')
    # a runner up to the altar's front from the east door, and kneelers
    rug(R, XF + 0.5, CY - 0.7, W - 2.6, CY + 0.7, m='carpet', border='gilt')
    g = Geo()
    for y in (CY - 1.6, CY + 1.6):
        g.add(box(XF + 1.4, y - 0.7, 0, XF + 1.75, y + 0.7, 0.22, 'velvet', sides='walnut'))
        g.add(box(XF + 2.3, y - 0.8, 0, XF + 2.55, y + 0.8, 0.9, 'walnut'))
    R.parts.add(g)


def altar(R):
    g = Geo()
    for k in range(4):
        z0, z1 = k * RISE, (k + 1) * RISE
        holes = [HOL] + ([ENT] if True else [])
        solid_minus(g, CX - HX[k], CY - HY[k], XF, CY + HY[k], z0, z1, holes, 'tile', top='tile')
    # the top: an altar table covering the hollow
    g.add(box(CX - HX[4], CY - HY[4], ZH, XF + 0.08, CY + HY[4], ZH + RISE, 'tile', top='oak'))
    g.add(box(CX - HX[4] - 0.06, CY - HY[4] - 0.06, ZH + RISE, XF + 0.12, CY + HY[4] + 0.06, ZH + RISE + 0.06, 'oak'))
    # the upright front's frame over the opening
    R.parts.add(g)
    # the frontal: a velvet cloth over the front, the middle part hanging free (you can push through it)
    zt = ZH + RISE + 0.06
    cl = pleats(CY - 1.5, CY + 1.5, 0.0, 0.03, zt, 9, 0.05, 'velvet', face=1)
    cl.v = [(XF + 0.1 + b, a, c) for a, b, c in cl.v]         # turn it into the y-z plane at the front
    cl.f = [tuple(reversed(f)) for f in cl.f]
    R.nocol.add(cl)
    R.nocol.add(box(XF + 0.1, CY - 1.52, zt - 0.14, XF + 0.16, CY + 1.52, zt, 'gilt'))
    # a gilt cross-stitched hem
    R.nocol.add(box(XF + 0.12, CY - 1.5, 0.03, XF + 0.17, CY + 1.5, 0.12, 'gilt'))
    # the altar's side walls of the east front (stone, either side of the cloth)
    # inside the hollow: floor worn, a candle stub, and the stair going down
    R.cut(box(SX0 - 0.02, SY0, KZ, SX1 + 0.02, SY1, 0.05, 'tile', bottom='floor', top='tile'))
    R.flight(SX0, SY0, KZ, SY1 - SY0, SN, SR, SRUN, '+x', m='oak', riser='walnut', side='tile')
    # a stub of candle on the hollow floor
    st, fl = lcandle(CX - 1.0, CY + 0.62, 0.0, 0.08, 0.03)
    R.nocol.add(st); R.light(fl)
    things(R)
    # on the top: a lectern with the book of names, a tall candelabrum, a gilt frame with nothing in it
    zt2 = ZH + RISE + 0.06
    R.parts.add(box(CX - 0.3, CY - 0.25, zt2, CX + 0.3, CY + 0.25, zt2 + 1.0, 'walnut'))
    R.parts.add(box(CX - 0.42, CY - 0.34, zt2 + 1.0, CX + 0.42, CY + 0.34, zt2 + 1.06, 'walnut', top='leather'))
    ob = box(-0.22, -0.16, 0, 0.0, 0.16, 0.03, 'ivory', sides='leather'); ob.add(box(0.0, -0.16, 0, 0.22, 0.16, 0.03, 'ivory', sides='leather'))
    R.nocol.add(ob.xform(0.0, CX, CY, zt2 + 1.07))
    for s_ in (-1, 1):
        candlestick(R, CX + 0.1, CY + s_ * 0.8, zt2, 0.9, arms=4, rs=rng(40 + s_))
    fr = Geo()
    fr.add(box(CX - 1.1, CY - 0.9, zt2 + 1.2, CX - 1.0, CY + 0.9, zt2 + 1.32, 'gilt'))
    fr.add(box(CX - 1.1, CY - 0.9, zt2 + 2.9, CX - 1.0, CY + 0.9, zt2 + 3.02, 'gilt'))
    fr.add(box(CX - 1.1, CY - 0.9, zt2 + 1.2, CX - 1.0, CY - 0.78, zt2 + 3.02, 'gilt'))
    fr.add(box(CX - 1.1, CY + 0.78, zt2 + 1.2, CX - 1.0, CY + 0.9, zt2 + 3.02, 'gilt'))
    fr.add(box(CX - 1.14, CY - 0.78, zt2 + 1.32, CX - 1.1, CY + 0.78, zt2 + 2.9, 'damask'))
    fr.add(box(CX - 1.25, CY - 0.1, zt2, CX - 1.05, CY + 0.1, zt2 + 1.25, 'walnut'))
    R.nocol.add(fr)


def things(R):
    """Candles and lost things on every tread (the west, north and south sides of the steps)."""
    rs = rng(7)
    pts = []
    L = Geo()        # the lost things, merged
    for k in range(5):
        z = (k + 1) * RISE if k < 4 else ZH + RISE + 0.06
        if k < 4:
            # the tread of tier k: between its footprint and the next one's
            xo0, yo0, yo1 = CX - HX[k], CY - HY[k], CY + HY[k]
            xi0, yi0, yi1 = CX - HX[k + 1], CY - HY[k + 1], CY + HY[k + 1]
            spots = []
            n = 20 - 3 * k
            for i in range(n):
                t = rs.random()
                side = rs.choice(('W', 'N', 'S', 'W'))
                if side == 'W': x, y = rs.uniform(xo0 + 0.06, xi0 - 0.06), rs.uniform(yo0 + 0.1, yo1 - 0.1)
                elif side == 'N': x, y = rs.uniform(xo0 + 0.1, XF - 0.1), rs.uniform(yi1 + 0.06, yo1 - 0.06)
                else: x, y = rs.uniform(xo0 + 0.1, XF - 0.1), rs.uniform(yo0 + 0.06, yi0 - 0.06)
                spots.append((x, y, side))
            for (x, y, side) in spots:
                if rs.random() < 0.55:
                    pts.append((x, y, z))
                else:
                    lost(L, x, y, z, side, rs)
        else:
            for i in range(10):
                x, y = rs.uniform(CX - HX[4] + 0.1, XF - 0.1), rs.uniform(CY - HY[4] + 0.1, CY + HY[4] - 0.1)
                if abs(y - CY) < 0.5 and abs(x - CX) < 0.5: continue
                pts.append((x, y, z))
    # on the floor round the foot too
    for i in range(28):
        a = rs.uniform(0, 2 * math.pi)
        x, y = CX + math.cos(a) * rs.uniform(3.6, 4.4), CY + math.sin(a) * rs.uniform(3.2, 4.0)
        if x > XF + 0.3 and abs(y - CY) < 1.9: continue
        if rs.random() < 0.6: pts.append((x, y, 0.0))
        else: lost(L, x, y, 0.0, 'W', rs)
    candles(R, pts, rs, 0.08, 0.42, 0.018, 0.045)
    R.nocol.add(L)


def lost(g, x, y, z, side, rs):
    kind = rs.choice(('shoe', 'shoe', 'glasses', 'keys', 'book', 'book', 'glove', 'umbrella', 'photo', 'watch', 'bear', 'cup'))
    a = rs.uniform(0, 2 * math.pi)
    if kind == 'shoe':
        for s_ in (-0.07, 0.07):
            p = Geo()
            p.add(box(-0.14, -0.045, 0, 0.14, 0.045, 0.07, rs.choice(('shoe', 'leather', 'black')), skip=('-z',)))
            p.add(box(-0.14, -0.045, 0.07, -0.02, 0.045, 0.13, 'shoe', skip=('-z',)))
            g.add(p.xform(a + rs.uniform(-0.3, 0.3), x + math.cos(a + 1.57) * s_, y + math.sin(a + 1.57) * s_, z))
    elif kind == 'glasses':
        p = Geo()
        for s_ in (-0.035, 0.035):
            p.add(box(s_ - 0.03, -0.004, 0.0, s_ + 0.03, 0.004, 0.035, 'iron'))
        p.add(box(-0.075, 0.0, 0.02, -0.07, 0.12, 0.028, 'iron')); p.add(box(0.07, 0.0, 0.02, 0.075, 0.12, 0.028, 'iron'))
        g.add(p.xform(a, x, y, z))
    elif kind == 'keys':
        p = box(-0.03, -0.03, 0, 0.03, 0.03, 0.01, 'brass')
        for k in range(3):
            b = k * 0.7
            p.add(box(0.03, -0.006, 0, 0.1, 0.006, 0.006, 'brass').xform(b))
        g.add(p.xform(a, x, y, z))
    elif kind == 'book':
        h = 0.0
        for i in range(rs.randint(1, 4)):
            t = rs.uniform(0.03, 0.06)
            g.add(box(-0.12, -0.085, h, 0.12, 0.085, h + t, rs.choice(BOOKM), top='ivory' if rs.random() < 0.2 else None, skip=('-z',)).xform(a + rs.uniform(-0.3, 0.3), x, y, z))
            h += t
    elif kind == 'glove':
        p = box(-0.1, -0.045, 0, 0.06, 0.045, 0.02, rs.choice(('leather', 'oxblood', 'coat3')), skip=('-z',))
        for k in range(4):
            p.add(box(0.06, -0.04 + k * 0.022, 0, 0.12 + 0.01 * (k % 2), -0.026 + k * 0.022, 0.016, 'leather', skip=('-z',)))
        g.add(p.xform(a, x, y, z))
    elif kind == 'umbrella':
        p = beam((-0.45, 0, 0.03), (0.35, 0, 0.03), 0.02, 'iron')
        p.add(box(-0.35, -0.05, 0.0, 0.25, 0.05, 0.08, rs.choice(('black', 'coat2', 'coat5')), skip=('-z',)))
        p.add(box(0.35, -0.03, 0.0, 0.42, 0.03, 0.05, 'walnut'))
        g.add(p.xform(a, x, y, z))
    elif kind == 'photo':
        p = box(-0.07, -0.01, 0, 0.07, 0.01, 0.19, 'gilt')
        p.add(box(-0.055, -0.012, 0.02, 0.055, -0.01, 0.17, 'ivory'))
        rot(p, 'x', -0.2)
        g.add(p.xform(a, x, y, z))
    elif kind == 'watch':
        p = box(-0.02, -0.02, 0, 0.02, 0.02, 0.012, 'brass')
        p.add(box(-0.09, -0.008, 0, 0.09, 0.008, 0.004, 'leather'))
        g.add(p.xform(a, x, y, z))
    elif kind == 'bear':
        g.add(blob(x, y, z + 0.1, 0.07, 0.06, 0.1, 6, 3, 'food'))
        g.add(blob(x, y, z + 0.24, 0.055, 0.055, 0.05, 6, 3, 'food'))
    else:
        g.add(cyl(x, y, z, z + 0.09, 0.04, 6, side='ivory', top='coat3', caps=True))


def crypt(R):
    """Lost Property: under the floor, west of the altar."""
    zc = -0.3
    R.cut(box(KX0, KY0, KZ, KX1, KY1, zc, 'plaster', bottom='floor', top='plaster'))
    # racks of lost property all round (the books are what was handed in)
    sh(R, '+y', KY0, KX0 + 0.1, KX1 - 0.3, z=KZ, rows=3, frame='walnut')
    sh(R, '-y', KY1, KX0 + 0.1, KX1 - 0.3, z=KZ, rows=3, frame='walnut')
    sh(R, '+x', KX0, KY0 + 0.4, 6.9, z=KZ, rows=3, frame='walnut')
    sh(R, '+x', KX0, 9.1, KY1 - 0.4, z=KZ, rows=3, frame='walnut')
    rs = rng(21); g = Geo()
    for k in range(9):
        x, y = rs.uniform(KX0 + 0.4, KX1 - 0.6), rs.choice((KY0 + 0.6, KY1 - 0.6))
        lost(g, x, y, KZ, 'W', rs)
    R.nocol.add(g)
    # the desk with the ledger, a lamp, a chair, one small shoe
    x0 = KX0 + 0.5
    R.parts.add(ltable(x0, 7.2, x0 + 0.8, 8.8, 0.78, 'walnut', top='leather').xform(0, 0, 0, KZ))
    R.parts.add(lchair_legs(x0 + 1.25, 8.0, math.pi).xform(0, 0, 0, KZ))
    R.spot('sit', x0 + 1.25, 8.0, KZ + 0.48, math.pi)
    llamp(R, x0 + 0.3, 8.55, KZ + 0.78, math.pi / 2, m='e_amber')
    ob = box(-0.22, -0.16, 0, 0.0, 0.16, 0.03, 'ivory', sides='leather'); ob.add(box(0.0, -0.16, 0, 0.22, 0.16, 0.03, 'ivory', sides='leather'))
    R.nocol.add(ob.xform(math.pi / 2, x0 + 0.45, 7.95, KZ + 0.78))
    R.nocol.add(box(x0 + 0.3, 7.35, KZ + 0.78, x0 + 0.42, 7.44, KZ + 0.84, 'wool'))
    R.spot('plaque', x0 + 0.45, 7.95, KZ + 0.8, 0.0, text='LOST PROPERTY. Everything is here. Nothing is ever claimed.')
    # the stair's foot opens here; a lamp over it
    bulb(R, (KX0 + KX1) / 2 + 0.6, 8.0, zc - 0.5, r=0.08, m='e_dim', top=zc)
    a, b = R.navpt(x0 + 1.6, 8.9, KZ), R.navpt(KX1 - 0.5, 8.0, KZ)
    R.link(a, b)


def lights(R):
    # a corona of candles over the altar, and lanterns on chains in the corners
    rs = rng(3)
    zc = 4.6
    R.nocol.add(ring(CX, CY, zc - 0.05, zc + 0.05, 1.5, 1.62, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        R.nocol.add(beam((CX + 1.56 * math.cos(a), CY + 1.56 * math.sin(a), zc), (CX, CY, 7.2), 0.02, 'iron'))
    pts = [(CX + 1.56 * math.cos(2 * math.pi * k / 16), CY + 1.56 * math.sin(2 * math.pi * k / 16), zc + 0.05) for k in range(16)]
    candles(R, pts, rs, 0.2, 0.28, 0.03, 0.035)
    R.light(ring(CX, CY, zc - 0.12, zc - 0.06, 1.5, 1.62, 24, top='e_candle', bottom='e_candle', inner='e_candle', outer='e_candle'))
    for (x, y) in ((2.2, 2.2), (13.8, 2.2), (2.2, 13.8), (13.8, 13.8)):
        lantern(R, x, y, 3.6, m='e_amber')
        R.nocol.add(cyl(x, y, 3.84, 7.0, 0.01, 4, side='iron', caps=False))
    for (x, y) in ((8.0, 1.3), (8.0, 14.7)):
        bulb(R, x, y, 5.6, r=0.14, m='e_dim', top=7.2)
