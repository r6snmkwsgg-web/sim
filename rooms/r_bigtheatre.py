"""The Theatre: a red velvet theatre two floors high, the stalls raked down to a stage; the house curtain
rises and falls on its own. On the stage, lit, the set is a library room exactly like the ones outside:
bookcases, a fireplace, a desk with two green lamps, an arch with a corridor going away through it for
ever (it goes back about three metres). One bookcase in the set is a way through: backstage, the wings,
the ghost light, and a very long ladder up to the fly gallery, where the ropes are."""
from kit_h10 import *

W = D = 32.0
HT = 2 * LH - 0.5                 # the house's ceiling
NR = 11                           # rows of stalls, each 0.15 lower than the last
Y_ROWS = 5.0                      # the back of the rows
ZF = -0.15 * (NR + 1)             # the front floor (-1.8)
YF0, YF1 = Y_ROWS + NR + 1.0, 18.5   # the front floor, before the stage
ZS = ZF + 1.0                     # the stage deck (-0.8)
YP0, YP1 = 20.1, 20.7             # the proscenium wall
PX0, PX1, PZ = 6.0, 26.0, 9.0     # its opening
YB = 27.0                         # the set's back wall
FX0, FX1 = 9.4, 10.6              # the false bookcase in it
GX0, GX1, GZ = 28.6, W - T, LH    # the fly gallery (east wing, high up)


def make():
    R = Room('bigtheatre', 2, 2, levels=2, res=2048, lo=-3.0)
    skip = upper_sockets(R) + [('N', 0, 0), ('N', 1, 0), ('W', 1, 0), ('E', 1, 0)]
    seal(R, skip, floor='carpet', wall='tile')
    house(R)
    seats(R)
    stage(R)
    the_set(R)
    backstage(R)
    fly_gallery(R)
    curtain(R)
    lights(R)
    def zf(y):
        k = int(y - Y_ROWS)
        return 0.0 if k < 1 else (ZF if k > NR else -0.15 * k)
    pts = [(4.0, 2.4), (16.0, 2.4), (28.0, 2.4), (29.5, 10.5), (29.5, 17.5), (16.0, YF0 + 0.7), (2.5, 17.5), (2.5, 10.5)]
    ids = [R.navpt(x, y, zf(y)) for (x, y) in pts]
    R.link(*ids); R.link(ids[-1], ids[0])
    a, b = R.navpt(16.0, 5.5), R.navpt(16.0, 15.0, -1.5)
    R.link(1, a, b, 5)
    secret(R, 20.0, 29.5, ZS, 'Backstage',
           'Through the bookcase in the set, the back of everything: canvas flats propped on each other, ropes, sandbags, and the ghost light, a single bulb on a stand, left burning so nobody falls in the dark. The show is about you. You never did learn your lines.')
    secret(R, 30.0, 27.0, GZ, 'The Fly Gallery',
           'At the top of the ladder, the fly gallery: the ropes that raise and lower the heavens tied off on a brass rail, a stool, a flask of tea gone cold. From up here the library on the stage looks very small, and very convincing.')
    fx(R, 'dust', [PX0, YP1, ZS + 0.5, PX1, YB, PZ])
    return done(R, 'The Theatre', weight=3, probe=(16.0, 8.0, 3.0), top=HT,
                blurb='A theatre, all red velvet and gilt, and every seat empty. The curtain is up. On the stage is a room of the library, perfectly made, lit and waiting for the actors. It dawns on you that you are the only one here who could go on.')


# ---------------------------------------------------------------------------
def house(R):
    # the foyer and the rows, stepping down toward the stage, the front floor, the apron
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, Y_ROWS + 1.0, HT, 'damask', bottom='carpet', top='plaster'))
    for k in range(1, NR + 1):
        y0 = Y_ROWS + k
        R.cut(box(T - 0.02, y0, -0.15 * k, W - T + 0.02, y0 + 1.0, HT, 'damask', bottom='carpet', top='plaster'))
    R.cut(box(T - 0.02, YF0, ZF, W - T + 0.02, YP0, HT, 'damask', bottom='floor', top='plaster'))
    # the apron: the stage comes out through the proscenium; stairs up at either side
    R.parts.add(box(4.4, YF1, ZF, 27.6, YP0, ZS, 'walnut', top='floor'))
    for x in (2.8, 27.6):
        R.flight(x, YF1 - 1.5, ZF, 1.6, 5, 0.2, 0.3, '+y', m='carpet', riser='walnut', side='walnut')
        R.parts.add(box(x, YF1, ZF, x + 1.6, YP0, ZS, 'walnut', top='floor'))
    # footlights along the apron's edge
    R.light(box(6.0, YF1 + 0.05, ZS, 26.0, YF1 + 0.15, ZS + 0.06, 'e_pool', skip=('-z',)))
    # a platform at the side doors so they open onto a level floor
    for x0, x1 in ((T - 0.02, 2.4), (W - 2.4, W - T + 0.02)):
        R.parts.add(box(x0, 6.2, -1.0, x1, 9.8, 0.0, 'walnut', top='carpet'))
    # boxes on the side walls, two tiers: gilt fronts, velvet inside, a candle in each (for the look)
    for (x, s_) in ((T, 1), (W - T, -1)):
        for z in (3.2, 6.4):
            for k in range(4):
                y = 9.6 + k * 2.3
                g = Geo()
                xa, xb = (x, x + s_ * 1.3)
                g.add(box(min(xa, xb), y, z - 0.3, max(xa, xb), y + 2.0, z, 'gilt', bottom='plaster'))
                g.add(box(min(x + s_ * 1.2, x + s_ * 1.3), y, z, max(x + s_ * 1.2, x + s_ * 1.3), y + 2.0, z + 1.0, 'gilt'))
                g.add(box(min(x, x + s_ * 0.05), y + 0.1, z, max(x, x + s_ * 0.05), y + 1.9, z + 2.4, 'velvet'))
                g.add(box(min(xa, xb), y, z + 2.5, max(xa, xb), y + 2.0, z + 2.7, 'gilt'))
                R.parts.add(g)
                st, fl = lcandle(x + s_ * 0.6, y + 1.0, z + 1.0, 0.18, 0.03)
                R.nocol.add(st); R.light(fl)
                R.nocol.add(box(min(x + s_ * 0.45, x + s_ * 0.75), y + 0.85, z + 0.94, max(x + s_ * 0.45, x + s_ * 0.75), y + 1.15, z + 1.0, 'gilt'))
    # the proscenium: a thick wall, gilt frame round the opening, a painted crest over it
    R.parts.add(box(T, YP0, ZF, PX0, YP1, HT, 'tile', skip=('+z',)))
    R.parts.add(box(PX1, YP0, ZF, W - T, YP1, HT, 'tile', skip=('+z',)))
    R.parts.add(box(PX0, YP0, PZ, PX1, YP1, HT, 'tile', skip=('+z',)))
    g = Geo()
    g.add(box(PX0 - 0.6, YP0 - 0.15, ZS, PX0, YP0, PZ + 0.6, 'gilt'))
    g.add(box(PX1, YP0 - 0.15, ZS, PX1 + 0.6, YP0, PZ + 0.6, 'gilt'))
    g.add(box(PX0 - 0.6, YP0 - 0.15, PZ, PX1 + 0.6, YP0, PZ + 0.6, 'gilt'))
    g.add(box(14.5, YP0 - 0.2, PZ + 0.8, 17.5, YP0, PZ + 2.8, 'gilt'))
    R.parts.add(g)
    R.parts.add(box(15.4, YP0 - 0.24, PZ + 1.3, 16.6, YP0 - 0.2, PZ + 2.3, 'oxblood'))
    # the ceiling: a great gilt rose, a chandelier on a long chain
    R.nocol.add(ring(16.0, 11.0, HT - 0.3, HT, 4.0, 4.6, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    R.nocol.add(ring(16.0, 11.0, HT - 0.2, HT, 1.2, 1.6, 24, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    R.nocol.add(cyl(16.0, 11.0, HT - 0.05, HT - 0.01, 4.0, 32, side='damask', top='damask', bottom='damask'))
    chandelier(R, 16.0, 11.0, 9.5, 2.0, n=16, chain=HT - 0.2, bulb=0.13, tiers=3)
    # a few bookcases in the foyer (this is still the library)
    for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, W - 0.6)):
        sh(R, '+y', T, a, b, rows=8, frame='walnut')


def seats(R):
    rs = rng(4)
    g = Geo()
    for k in range(1, NR + 1):
        y = Y_ROWS + k + 0.5
        z = -0.15 * k
        for (a, b) in ((4.6, 15.2), (16.8, 27.4)):
            n = int((b - a) / 0.6)
            for i in range(n):
                x = a + (b - a) * (i + 0.5) / n
                c = lchair(x, y, math.pi / 2, frame='velvet', seat='velvet', back_h=1.05)
                g.add(c.xform(0, 0, 0, z))
                if rs.random() < 0.01:
                    R.spot('sit', x, y, z + 0.48, math.pi / 2)
    R.parts.add(g)
    for (x, k) in ((10.0, 3), (22.0, 7)):
        R.spot('sit', x, Y_ROWS + k + 0.5, -0.15 * k + 0.48, math.pi / 2)
    # a programme left on a seat
    R.nocol.add(box(-0.1, -0.14, 0, 0.1, 0.14, 0.006, 'ivory').xform(0.3, 12.3, Y_ROWS + 4.5, -0.6 + 0.49))


def stage(R):
    # the stage house: deck, wings, backstage, the fly tower over it all
    R.cut(box(T - 0.02, YP1 - 0.02, ZS, W - T + 0.02, D - T + 0.02, HT, 'tile', bottom='floor', top='plaster'))
    R.cut(box(PX0, YP0 - 0.05, ZS, PX1, YP1 + 0.05, PZ, 'tile', bottom='floor', top='tile'))
    # battens across the stage with lamps on them, ropes up to the grid
    for y in (21.5, 23.3, 25.1):
        R.nocol.add(box(PX0 - 0.5, y - 0.04, 10.5, PX1 + 0.5, y + 0.04, 10.58, 'iron'))
        for k in range(6):
            x = PX0 + 1.5 + k * (PX1 - PX0 - 3.0) / 5
            R.nocol.add(box(x - 0.14, y - 0.12, 10.1, x + 0.14, y + 0.12, 10.5, 'black'))
            R.light(box(x - 0.1, y - 0.1, 10.08, x + 0.1, y + 0.1, 10.1, 'e_lamp', skip=('+z',)))
        for x in (PX0, 16.0, PX1):
            R.nocol.add(box(x - 0.01, y - 0.01, 10.58, x + 0.01, y + 0.01, HT, 'oak'))


def the_set(R):
    """On the stage, the set: a room of the library, three walls of canvas and timber, perfectly made."""
    z = ZS
    # the flats: side walls and the back wall, painted limestone, full of real bookcases
    R.parts.add(box(PX0 + 0.2, YP1, z, PX0 + 0.35, YB, z + 7.0, 'tile', skip=('-z',)))
    R.parts.add(box(PX1 - 0.35, YP1, z, PX1 - 0.2, YB, z + 7.0, 'tile', skip=('-z',)))
    ax0, ax1 = 14.6, 17.4                      # the arch in the back flat
    for (a, b) in ((PX0 + 0.35, FX0), (FX1, ax0), (ax1, PX1 - 0.35)):
        R.parts.add(box(a, YB, z, b, YB + 0.15, z + 7.0, 'tile', skip=('-z',)))
    R.parts.add(box(FX0, YB, z + 2.35, FX1, YB + 0.15, z + 7.0, 'tile'))
    R.parts.add(box(ax0, YB, z + 3.4, ax1, YB + 0.15, z + 7.0, 'tile'))
    # the false bookcase in the back flat
    shelf(R, FX1, YB, z, FX1 - FX0, '-y', rows=5, frame='walnut', solid=False)
    for (a, b) in ((PX0 + 0.6, FX0 - 0.1), (FX1 + 0.1, ax0 - 0.3), (ax1 + 0.3, PX1 - 0.6)):
        sh(R, '-y', YB, a, b, z=z, rows=12, frame='walnut')
    for (x, face) in ((PX0 + 0.35, '+x'), (PX1 - 0.35, '-x')):
        sh(R, face, x, YP1 + 1.0, 23.0, z=z, rows=12, frame='walnut')
    # a fireplace, a portrait over it, a desk with two lamps, armchairs, a globe, the rug
    fx0 = PX1 - 0.35
    R.parts.add(box(fx0 - 0.5, 23.6, z, fx0, 25.6, z + 1.5, 'tile'))
    R.parts.add(box(fx0 - 0.62, 23.4, z + 1.5, fx0, 25.8, z + 1.62, 'tile'))
    R.parts.add(box(fx0 - 0.52, 24.0, z, fx0 - 0.5, 25.2, z + 1.0, 'black'))
    R.light(box(fx0 - 0.5, 24.2, z + 0.02, fx0 - 0.35, 25.0, z + 0.25, 'e_flame'))
    g = Geo()
    g.add(box(fx0 - 0.08, 23.8, z + 2.2, fx0, 25.4, z + 4.2, 'gilt'))
    g.add(box(fx0 - 0.09, 23.95, z + 2.35, fx0 - 0.08, 25.25, z + 4.05, 'damask'))
    R.nocol.add(g)
    R.parts.add(ltable(12.0, 23.4, 15.2, 24.4, 0.78, 'walnut', top='leather').xform(0, 0, 0, z))
    for x in (12.6, 14.6):
        llamp(R, x, 23.9, z + 0.78, 0.0, lit=True, m='e_lamp')
    R.parts.add(lchair_legs(13.6, 22.9, math.pi / 2).xform(0, 0, 0, z))
    armchair(R, 18.6, 23.8, math.pi, z=z)
    armchair(R, 10.4, 23.6, 0.2, z=z)
    R.parts.add(cyl(20.6, 25.6, z, z + 0.1, 0.35, 12, side='walnut', top='walnut'))
    R.parts.add(cyl(20.6, 25.6, z + 0.1, z + 0.9, 0.05, 8, side='walnut', caps=False))
    R.nocol.add(sphere(20.6, 25.6, z + 1.35, 0.45, 14, 7, 'green'))
    rug(R, 9.0, 21.6, 22.5, 26.2, z=z, m='carpet', border='gilt')
    # through the arch: a corridor going away for ever (forced perspective, three metres deep)
    n = 7
    for k in range(n + 1):
        t = k / n
        y = YB + 0.15 + t * 3.2
        w = (ax1 - ax0) * (1 - 0.72 * t)
        h = 3.4 * (1 - 0.7 * t)
        zf = z + 0.6 * t
        cx = (ax0 + ax1) / 2
        if k < n:
            y2 = YB + 0.15 + (k + 1) / n * 3.2
            w2 = (ax1 - ax0) * (1 - 0.72 * (k + 1) / n); h2 = 3.4 * (1 - 0.7 * (k + 1) / n); zf2 = z + 0.6 * (k + 1) / n
            from kit_h2 import hexa
            # floor, walls and ceiling of this bay
            R.nocol.add(quad([(cx - w / 2, y, zf), (cx + w / 2, y, zf), (cx + w2 / 2, y2, zf2), (cx - w2 / 2, y2, zf2)], 'terrazzo'))
            R.nocol.add(quad([(cx - w / 2, y, zf), (cx - w2 / 2, y2, zf2), (cx - w2 / 2, y2, zf2 + h2), (cx - w / 2, y, zf + h)], 'tile', flip=True))
            R.nocol.add(quad([(cx + w / 2, y, zf), (cx + w2 / 2, y2, zf2), (cx + w2 / 2, y2, zf2 + h2), (cx + w / 2, y, zf + h)], 'tile'))
            R.nocol.add(quad([(cx - w / 2, y, zf + h), (cx - w2 / 2, y2, zf2 + h2), (cx + w2 / 2, y2, zf2 + h2), (cx + w / 2, y, zf + h)], 'plaster', flip=True))
        # an arch rib at each step, and a tiny lamp
        R.nocol.add(box(cx - w / 2 - 0.05, y - 0.03, zf + h - 0.08 * (1 - t), cx + w / 2 + 0.05, y + 0.03, zf + h, 'walnut'))
        if k % 2 == 1:
            R.light(box(cx - 0.05 * (1 - t) - 0.02, y, zf + h - 0.25, cx + 0.05 * (1 - t) + 0.02, y + 0.02, zf + h - 0.2, 'e_lamp'))
    R.parts.add(box(ax0 - 0.2, YB + 3.4, z, ax1 + 0.2, YB + 3.5, z + 3.0, 'black'))
    R.light(box(15.75, YB + 3.38, z + 0.7, 16.25, YB + 3.4, z + 1.4, 'e_lamp'))
    R.col.add(box(ax0, YB + 0.1, z, ax1, YB + 0.2, z + 3.4, 'tile'))


def backstage(R):
    """Behind the set: flats, ropes, sandbags, a costume rail, the ghost light."""
    z = ZS
    rs = rng(7)
    # the backs of the flats: timber frames
    g = Geo()
    for x in range(7, 26, 2):
        g.add(box(x - 0.05, YB + 0.15, z, x + 0.05, YB + 0.25, z + 7.0, 'oak'))
    g.add(box(PX0 + 0.35, YB + 0.15, z + 2.5, PX1 - 0.35, YB + 0.25, z + 2.6, 'oak'))
    g.add(box(PX0 + 0.35, YB + 0.15, z + 5.0, PX1 - 0.35, YB + 0.25, z + 5.1, 'oak'))
    R.nocol.add(g)
    # flats leaning against the back wall
    for k in range(5):
        x = 2.0 + k * 0.25
        f = box(0, 0, 0, 3.5, 0.06, 5.0, rs.choice(('tile', 'damask', 'plaster', 'green')), sides='oak')
        rot(f, 'x', 0.12)
        R.nocol.add(f.xform(0, x + 20.5, D - T - 0.7 - k * 0.1, z))
    R.col.add(box(22.4, D - T - 1.3, z, 26.2, D - T, z + 5.0, 'tile'))
    # the costume rail
    R.parts.add(box(3.0, 29.2, z, 3.06, 29.26, z + 1.9, 'iron'))
    R.parts.add(box(6.0, 29.2, z, 6.06, 29.26, z + 1.9, 'iron'))
    R.parts.add(box(3.0, 29.2, z + 1.85, 6.06, 29.26, z + 1.9, 'iron'))
    from kit_h2 import hexa
    for k in range(9):
        x = 3.2 + k * 0.32; m = rs.choice(('velvet', 'coat5', 'gilt', 'coat2', 'ivory'))
        R.nocol.add(hexa([(x - 0.05, 28.95, z + 0.5), (x + 0.05, 28.95, z + 0.5), (x + 0.05, 29.5, z + 0.5), (x - 0.05, 29.5, z + 0.5),
                          (x - 0.04, 29.05, z + 1.8), (x + 0.04, 29.05, z + 1.8), (x + 0.04, 29.4, z + 1.8), (x - 0.04, 29.4, z + 1.8)], m))
    # sandbags and a prop table
    for k in range(6):
        R.nocol.add(blob(9.0 + k * 0.45, D - T - 0.4, z + 0.15, 0.25, 0.18, 0.15, 7, 3, 'food'))
    R.parts.add(ltable(12.0, 29.6, 14.0, 30.4, 0.8, 'oak', top='oak').xform(0, 0, 0, z))
    for (x, m) in ((12.4, 'gilt'), (12.9, 'oxblood'), (13.5, 'chrome')):
        R.nocol.add(cyl(x, 30.0, z + 0.8, z + 1.0, 0.07, 8, side=m, top=m))
    # the ghost light: a bare bulb on a stand in the middle of the stage
    R.parts.add(cyl(16.0, 23.0 - 1.4, z, z + 0.08, 0.25, 10, side='iron', top='iron'))
    R.parts.add(cyl(16.0, 21.6, z + 0.08, z + 1.6, 0.03, 6, side='iron', caps=False))
    R.light(sphere(16.0, 21.6, z + 1.75, 0.12, 10, 5, 'e_amber'))
    for k in range(6):
        a = k * math.pi / 3
        R.nocol.add(beam((16.0, 21.6, z + 1.6), (16.0 + 0.16 * math.cos(a), 21.6 + 0.16 * math.sin(a), z + 1.9), 0.012, 'iron'))
    bulb(R, 20.0, 29.6, z + 3.5, r=0.08, m='e_dim', top=HT)
    bulb(R, 3.0, 24.0, z + 3.5, r=0.08, m='e_dim', top=HT)
    a, b, c = R.navpt(10.0, 28.5, z), R.navpt(20.0, 28.8, z), R.navpt(29.5, 22.5, z)
    R.link(a, b, c)


def fly_gallery(R):
    """High in the east wing: the fly gallery, reached by a long ladder up the wall."""
    z0 = ZS
    # the gallery: an iron deck along the east wall, railed on its open side, a hatch where the ladder comes up
    HX0, HX1, HY0, HY1 = 29.6, 30.6, 26.2, 27.5
    g = Geo()
    solid_minus(g, GX0, YP1 + 0.1, GX1, D - T, GZ - 0.25, GZ, [(HX0, HY0, HX1, HY1)], 'iron', top='oak')
    R.parts.add(g)
    rail(R, GX0 + 0.05, YP1 + 0.2, GX0 + 0.05, D - T - 0.05, GZ, m='iron')
    rail(R, GX0, YP1 + 0.15, GX1, YP1 + 0.15, GZ, m='iron')
    rail(R, HX0 - 0.04, HY1, HX0 - 0.04, HY0 - 0.04, GZ, m='iron')
    rail(R, HX0 - 0.04, HY0 - 0.04, HX1 + 0.04, HY0 - 0.04, GZ, m='iron')
    rail(R, HX1 + 0.04, HY0 - 0.04, HX1 + 0.04, HY1, GZ, m='iron')
    # the ladder: from the wing floor up through the hatch (walked as a steep ramp)
    H = GZ - z0
    ang = math.radians(62)
    L = H / math.tan(ang)
    ladder_up(R, (HX0 + HX1) / 2, HY1 - L, z0, GZ, '+y', w=0.62, m='oak', rail='iron', ang=ang)
    # the pin rail with the ropes tied off and going up to the grid, a stool, a flask
    R.parts.add(box(W - T - 0.25, YP1 + 0.5, GZ + 0.9, W - T - 0.1, D - T - 0.5, GZ + 1.05, 'brass'))
    rs = rng(11)
    g = Geo()
    y = YP1 + 0.8
    while y < D - T - 0.6:
        g.add(box(W - T - 0.2, y - 0.012, GZ + 0.2, W - T - 0.176, y + 0.012, HT, 'oak'))
        y += rs.uniform(0.18, 0.4)
    R.nocol.add(g)
    R.parts.add(cyl(29.6, 29.8, GZ, GZ + 0.6, 0.18, 10, side='oak', top='oak'))
    R.spot('sit', 29.6, 29.8, GZ + 0.6, math.pi)
    R.nocol.add(cyl(30.2, 30.6, GZ, GZ + 0.3, 0.05, 8, side='green', top='chrome'))
    bulb(R, 30.0, 26.0, GZ + 2.2, r=0.07, m='e_dim', top=HT)
    a, b = R.navpt(30.0, 23.5, GZ), R.navpt(30.0, 30.2, GZ)
    R.link(a, b)


def curtain(R):
    """The house curtain: rises and falls by itself (a slow slide mover); baked where it hangs, up."""
    up = 6.2
    M = R.mover('slide', delta=(0.0, 0.0, -up), period=90.0, pause=30.0, phase=0.3)
    c = pleats(PX0 - 0.1, PX1 + 0.1, YP1 + 0.25, ZS + up, PZ + up, 24, 0.2, 'velvet', face=-1)
    M.nocol.add(c)
    M.nocol.add(box(PX0 - 0.1, YP1 + 0.2, ZS + up, PX1 + 0.1, YP1 + 0.5, ZS + up + 0.12, 'gilt'))
    # the fixed pelmet and legs in front of it
    R.nocol.add(pleats(PX0, PX1, YP1 + 0.05, PZ - 1.4, PZ, 30, 0.15, 'velvet', face=-1))
    R.nocol.add(box(PX0, YP1 - 0.02, PZ - 1.5, PX1, YP1 + 0.2, PZ - 1.4, 'gilt'))
    for (a, b) in ((PX0, PX0 + 1.1), (PX1 - 1.1, PX1)):
        R.nocol.add(pleats(a, b, YP1 + 0.05, ZS, PZ - 1.4, 4, 0.18, 'velvet', face=-1))


def lights(R):
    for (x, s_) in ((T, 1), (W - T, -1)):
        for y in (3.0, 6.5, 19.0):
            sconce(R, x + s_ * 0.1, y, 3.2, 0.0 if s_ > 0 else math.pi, m='e_candle', r=0.08)
    for x in (4.0, 16.0, 28.0):
        R.light(sphere(x, 1.2, 3.8, 0.12, 8, 4, 'e_amber'))
