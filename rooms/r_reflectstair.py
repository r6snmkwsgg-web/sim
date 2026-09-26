"""The Mirror Stair: a grand stone stair climbs a tall hall to a landing, and at the top of it, where the stair
looks, a tall gilded mirror: you see yourself arrive. Beside it hangs an identical frame, and in that one
too a grand stair goes down, lamps and books either side; but you are not in it. It is not a mirror. Step
in and you are at the top of a second stair, which goes down to the floor below. Halfway down it there is a
landing, and on the landing a bookcase that opens."""
from kit_h11 import *

W = D = 32.0
UZ = 8.0
ZT = 2 * LH - 0.4
HX0, HX1, HY0, HY1 = 8.5, 23.5, 3.0, 18.0      # the stair hall (open through both floors)
SX0, SX1 = 9.5, 14.5                           # the grand stair
SCY0, SCY1 = 22.0, 22.6                        # the screen wall on the landing
MX, PX = 12.0, 20.0                            # the mirror and the frame beside it
FW, FH = 3.2, 4.6                              # both frames' openings
TX0, TX1 = 25.0, 28.4                          # the second stair (its shaft)
TY0, TY1 = 8.0, 22.4                           # its foot, and the south face of its screen
BY1 = 23.0                                     # its screen's north face (where the portal comes out)
KX0, KX1, KY0, KY1 = 28.8, W - T, 13.4, 17.2   # the room off its landing (z 4)


def make():
    R = Room('reflectstair', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    halls(R)
    grand_stair(R)
    screens(R)
    second_stair(R)
    landing_room(R)
    dressing(R)
    mirror(R, (MX, SCY0, UZ), (0, -1, 0), FW, FH)
    portal(R, P((PX, SCY0, UZ), (0, 1, 0), FW, FH), P(((TX0 + TX1) / 2, BY1, UZ), (0, -1, 0), FW, FH))
    # walkers: round both floors, up the grand stair, down the second
    navloop(R, [(3.5, 3.5), (16.0, 1.6), (28.5, 3.5), (30.4, 11.0), (30.4, 21.0), (28.5, 28.5), (16.0, 29.0), (3.5, 28.5), (4.5, 16.0)])
    navloop(R, [(3.5, 1.8), (16.0, 1.8), (29.0, 1.8), (30.2, 16.0), (29.0, 29.0), (16.0, 29.0), (3.5, 29.0), (3.5, 16.0)], z=UZ)
    g = [R.navpt(12.0, 2.5), R.navpt(12.0, 11.0, 4.0), R.navpt(12.0, 19.5, UZ), R.navpt(16.0, 19.8, UZ), R.navpt(7.0, 19.8, UZ), R.navpt(3.5, 19.8, UZ)]
    R.link(*g)
    s = [R.navpt(26.7, 25.0, UZ), R.navpt(26.7, 15.2, 4.0), R.navpt(26.7, 6.5), R.navpt(22.0, 6.0)]
    R.link(*s)
    secret(R, (KX0 + KX1) / 2, (KY0 + KY1) / 2, 4.0, 'The Room on the Half Landing',
           'Halfway down the stair that is not in the mirror, a bookcase opens on a small room with a chair facing the wall. On the wall is a mirror the size of a hand. You look. You are there. You are almost relieved.', r=1.6)
    fx(R, 'dust', [HX0, HY0, 1.0, HX1, HY1, 14.0])
    return done(R, 'The Mirror Stair', weight=3, probe=(16.0, 10.0, 9.0), top=ZT,
                blurb='At the top of the grand stair a tall gilded mirror, and you in it, climbing. Beside it another frame, and another stair in it, going down. You are not in that one.')


def halls(R):
    R.cut(box(T - 0.01, T - 0.01, 0, W - T + 0.01, D - T + 0.01, TOP, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.01, T - 0.01, UZ, W - T + 0.01, D - T + 0.01, ZT, 'tile', bottom='floor', top='plaster'))
    R.cut(box(HX0, HY0, 0, HX1, HY1, ZT, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(TX0, TY0, 0, TX1, TY1, ZT, 'tile', bottom='terrazzo', top='plaster'))
    # rails round the stair hall on the upper floor (open where the grand stair arrives)
    rect_rails(R, HX0, HY0, HX1, HY1, UZ, opens={'N': [(SX0, SX1)]}, inset=-0.08, kind='stone')
    # rails round the second stair's shaft up there (open at its screen)
    rail(R, TX0 - 0.08, TY0 - 0.08, TX1 + 0.08, TY0 - 0.08, z=UZ, h=1.0)
    # the hall's lanterns: a ceiling of coffers with a skylight over the stair hall
    for i in range(3):
        for j in range(3):
            x0, y0 = HX0 + 0.8 + i * 4.7, HY0 + 0.8 + j * 4.7
            R.light(box(x0 + 0.9, y0 + 0.9, ZT - 0.03, x0 + 3.2, y0 + 3.2, ZT, 'e_sky'))
    for t in [HX0 + 0.4 + i * 4.7 for i in range(4)]:
        R.nocol.add(box(t - 0.2, HY0, ZT - 0.5, t + 0.2, HY1, ZT, 'plaster', skip=('+z',)))
    for t in [HY0 + 0.4 + i * 4.7 for i in range(4)]:
        R.nocol.add(box(HX0, t - 0.2, ZT - 0.5, HX1, t + 0.2, ZT, 'plaster', skip=('+z',)))


def parapet(R, x, ya, yb, za, zb, h=1.0, t=0.24, m='tile'):
    """A solid stone parapet along y (x is its centre line) from (ya, za) to (yb, zb): the walking level
    at each end; the top follows the slope."""
    g = slope_box(ya, yb, -t / 2, t / 2, min(za, zb) - 0.3 if za == zb else za - 1.2, zb - 1.2 if za != zb else min(za, zb) - 0.3,
                  za + h, zb + h, m, cap='brass')
    g.v = [(y + x, xx, z) for (xx, y, z) in g.v]
    g.fix()
    R.parts.add(g)


def grand_stair(R):
    w = SX1 - SX0
    R.flight(SX0, 4.0, 0.0, w, 20, 0.2, 0.3, '+y', m='terrazzo', riser='tile', side='tile')
    R.parts.add(box(SX0, 10.0, 0, SX1, 12.0, 4.0, 'tile', top='terrazzo'))
    R.flight(SX0, 12.0, 4.0, w, 20, 0.2, 0.3, '+y', m='terrazzo', riser='tile', side='tile')
    R.parts.add(box(SX0, 12.0, 0, SX1, HY1, 4.0, 'tile', skip=('+z',)))
    # the landing at the top is the upper floor itself (y > HY1); stone parapets up both sides
    for x in (SX0 + 0.12, SX1 - 0.12):
        parapet(R, x, 4.0, 10.0, 0.0, 4.0)
        parapet(R, x, 10.0, 12.0, 4.0, 4.0)
        parapet(R, x, 12.0, HY1, 4.0, UZ)
        # newel posts with green lamps
        for (y, z) in ((4.0, 0.0), (10.0, 4.0), (12.0, 4.0), (HY1 - 0.1, UZ)):
            R.parts.add(box(x - 0.2, y - 0.2, z - 0.1, x + 0.2, y + 0.2, z + 1.25, 'tile'))
            llamp(R, x, y, z + 1.25, a=math.pi / 2)


def screens(R):
    """The screen across the landing: the mirror in it, and the portal frame beside it (an opening with a
    closed recess behind); and the identical screen and frame at the top of the second stair."""
    z = UZ
    top = z + FH + 1.6
    # the landing's screen, in pieces round the portal's opening
    R.parts.add(box(HX0, SCY0, z, PX - FW / 2, SCY1, top, 'tile'))
    R.parts.add(box(PX + FW / 2, SCY0, z, HX1, SCY1, top, 'tile'))
    R.parts.add(box(PX - FW / 2, SCY0, z + FH, PX + FW / 2, SCY1, top, 'tile'))
    # the recess behind the frame: floor, sides, back, roof
    R.parts.add(box(PX - FW / 2 - 0.2, SCY1, z, PX - FW / 2, SCY1 + 0.9, z + FH + 0.2, 'tile'))
    R.parts.add(box(PX + FW / 2, SCY1, z, PX + FW / 2 + 0.2, SCY1 + 0.9, z + FH + 0.2, 'tile'))
    R.parts.add(box(PX - FW / 2 - 0.2, SCY1 + 0.9, z, PX + FW / 2 + 0.2, SCY1 + 1.1, z + FH + 0.2, 'tile'))
    R.parts.add(box(PX - FW / 2, SCY1, z + FH, PX + FW / 2, SCY1 + 0.9, z + FH + 0.2, 'tile'))
    # the second stair's screen
    R.parts.add(box(TX0 - 0.4, TY1, z, TX0 + (TX1 - TX0 - FW) / 2, BY1, top, 'tile'))
    R.parts.add(box(TX1 - (TX1 - TX0 - FW) / 2, TY1, z, TX1 + 0.4, BY1, top, 'tile'))
    R.parts.add(box(TX0 - 0.4, TY1, z + FH, TX1 + 0.4, BY1, top, 'tile'))
    # the three gilded frames (mirror, portal, and the portal's twin), identical; the twin has one each side
    tc = (TX0 + TX1) / 2
    for (x, y, face) in ((MX, SCY0, -math.pi / 2), (PX, SCY0, -math.pi / 2), (tc, TY1, -math.pi / 2), (tc, BY1, math.pi / 2)):
        R.parts.add(local(frame_geo(FW, FH, bw=0.3, depth=0.2, m='gilt', crest=1.3, sill=False), face, x, y, z))
    # lamps either side of each frame
    for (x, y, s) in ((MX, SCY0, -1), (PX, SCY0, -1), (tc, TY1, -1)):
        for dx in (-FW / 2 - 0.75, FW / 2 + 0.75):
            if TX0 - 0.4 < x + dx < TX1 + 0.4 and y == TY1:
                continue
            sconce(R, x + dx, y + 0.02 * s, z + 2.6, -math.pi / 2)


def second_stair(R):
    w = TX1 - TX0
    R.flight(TX0, TY0, 0.0, w, 20, 0.2, 0.3, '+y', m='terrazzo', riser='tile', side='tile')
    R.parts.add(box(TX0, TY0 + 6.0, 0, TX1, TY0 + 8.4, 4.0, 'tile', top='terrazzo'))
    R.flight(TX0, TY0 + 8.4, 4.0, w, 20, 0.2, 0.3, '+y', m='terrazzo', riser='tile', side='tile')
    R.parts.add(box(TX0, TY0 + 8.4, 0, TX1, TY1, 4.0, 'tile', skip=('+z',)))
    # the shaft's walls, both floors high (a gap in the east one at the landing, behind a bookcase)
    ly0, ly1 = TY0 + 6.0, TY0 + 8.4
    R.parts.add(box(TX0 - 0.4, TY0, 0, TX0, TY1, ZT, 'tile'))
    R.parts.add(box(TX1, TY0, 0, TX1 + 0.4, ly0 + 0.4, ZT, 'tile'))
    R.parts.add(box(TX1, ly1 - 0.4, 0, TX1 + 0.4, TY1, ZT, 'tile'))
    R.parts.add(box(TX1, ly0 + 0.4, 0, TX1 + 0.4, ly1 - 0.4, 4.0, 'tile'))
    R.parts.add(box(TX1, ly0 + 0.4, 6.3, TX1 + 0.4, ly1 - 0.4, ZT, 'tile'))
    shelf(R, TX1, ly0 + 0.35, 4.0, ly1 - ly0 - 0.7, '-x', rows=5, frame='walnut', solid=False)
    # books all the way down both walls of the shaft, stepping with the stair
    for (y0, z) in [(TY0 + k * 1.2, min(4.0, k * 1.2 / 0.3 * 0.2)) for k in range(5)] + [(TY0 + 8.4 + k * 1.2, 4.0 + k * 0.8) for k in range(5)]:
        sh(R, '+x', TX0, y0 + 0.05, y0 + 1.15, z=z + 0.2, rows=7, frame='walnut')
        sh(R, '-x', TX1, y0 + 0.05, y0 + 1.15, z=z + 0.2, rows=7, frame='walnut')
    for y in (TY0 + 3.0, TY0 + 7.2, TY0 + 11.4):
        pendant(R, (TX0 + TX1) / 2, y, (4.0 if y > TY0 + 8 else 2.0) + 4.4, ZT, r=0.25)


def landing_room(R):
    R.parts.add(box(KX0, KY0, 0, KX1 + 0.01, KY1, 4.0, 'tile', top='floor', skip=('-z',)))
    R.parts.add(box(KX0, KY0, 4.0, KX1 + 0.01, KY0 + 0.25, TOP, 'tile'))
    R.parts.add(box(KX0, KY1 - 0.25, 4.0, KX1 + 0.01, KY1, TOP, 'tile'))
    R.nocol.add(box(KX0 + 0.2, KY0 + 0.45, 4.0, KX1 - 0.2, KY1 - 0.45, 4.012, 'carpet'))
    R.parts.add(lchair(KX1 - 0.9, (KY0 + KY1) / 2, 0.0).xform(0, 0, 0, 4.0))
    R.spot('sit', KX1 - 0.9, (KY0 + KY1) / 2, 4.48, 0.0)
    mirror(R, (KX1 - 0.005, (KY0 + KY1) / 2, 5.3), (-1, 0, 0), 0.26, 0.34)
    R.parts.add(local(frame_geo(0.26, 0.34, bw=0.06, depth=0.04, m='gilt'), math.pi, KX1, (KY0 + KY1) / 2, 5.3))
    R.nocol.add(box(KX1 - 0.012, (KY0 + KY1) / 2 - 0.13, 5.3, KX1, (KY0 + KY1) / 2 + 0.13, 5.64, 'chrome'))
    sh(R, '+y', KY0 + 0.25, KX0 + 0.2, KX1 - 0.3, z=4.0, rows=7, frame='walnut')
    sh(R, '-y', KY1 - 0.25, KX0 + 0.2, KX1 - 0.3, z=4.0, rows=7, frame='walnut')
    candlestick(R, KX1 - 0.5, KY0 + 0.8, 4.0, h=1.0)
    R.spot('plaque', KX1 - 0.3, KY1 - 0.9, 5.4, math.pi, text='This one is only a mirror.')


def dressing(R):
    rows = 16
    for z in (0.0, UZ):
        for (a, b) in ((0.8, 6.3), (9.7, 22.3), (25.7, W - 0.8)):
            sh(R, '+y', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-y', D - T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '+x', T, a, b, z=z, rows=rows, frame='walnut')
            if not (z == 0.0 and a > 9):
                sh(R, '-x', W - T, a, b, z=z, rows=rows, frame='walnut')
    sh(R, '-x', W - T, 9.7, KY0 - 0.2, rows=rows, frame='walnut')
    sh(R, '-x', W - T, KY1 + 0.2, 22.3, rows=rows, frame='walnut')
    # the stair hall's walls on the ground floor: books under the gallery's edge
    # tables on both floors
    for z in (0.0, UZ):
        for (x, y) in ((4.5, 10.0), (4.5, 24.0), (16.0, 27.0), (21.0, 27.0)):
            R.parts.add(ltable(x - 0.6, y - 1.2, x + 0.6, y + 1.2, top='leather').xform(0, 0, 0, z))
            llamp(R, x, y, z + 0.76, a=math.pi / 2)
    for (x, y) in ((18.0, 8.0), (18.0, 13.0)):
        R.parts.add(ltable(x - 1.4, y - 0.6, x + 1.4, y + 0.6, top='leather'))
        llamp(R, x, y, 0.76)
        for dx in (-0.7, 0.7):
            R.parts.add(lchair(x + dx, y - 0.95, math.pi / 2)); R.parts.add(lchair(x + dx, y + 0.95, -math.pi / 2))
    for z in (0.0, UZ):
        for (x, y) in ((4.5, 4.5), (4.5, 16.0), (4.5, 27.5), (16.0, 27.5), (27.5, 27.5), (30.0, 4.5), (22.0, 1.8)):
            pendant(R, x, y, z + 5.0, z + (TOP if z == 0 else ZT - UZ), r=0.3)
    chandelier(R, 16.0, 10.5, 11.0, 1.4, n=12, chain=ZT)
    for (x, y) in ((1.2, 1.2), (W - 1.2, D - 1.2)):
        lantern(R, x, y, 0.0)
        lantern(R, x, y, UZ)
