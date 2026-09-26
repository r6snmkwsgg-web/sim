"""The Endless Stair: four flights climb round a square court of shelves, two metres each, and the fourth
comes out eight metres up, exactly over the foot of the first. Step through the stone gate at the top and
you are at the foot again, with the first flight in front of you: you can climb for ever. The stair also
simply joins the two floors. On the third landing a short spur ends at a bookcase that is a door."""
from kit_h11 import *

W = D = 32.0
V0, V1 = 8.4, 23.6            # the atrium (open through both floors)
C0, C1 = 12.0, 20.0           # the court the stair climbs round
O0, O1 = 9.8, 22.2            # the stair's outer edge
N_, RISE, RUN = 10, 0.2, 0.32
F0, F1 = 14.4, 14.4 + N_ * RUN   # where the flights sit on each side (17.6)
GH = 2.6                      # the gate's opening
UZ = 8.0
KX0, KX1, KY0, KY1 = 17.0, 21.8, 25.2, 29.6   # the room off the spur (floor at z 4)


def make():
    R = Room('escherloop', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    halls(R)
    stair(R)
    gates(R)
    spur_room(R)
    dressing(R)
    # the portal: the gate on the top landing (z 8) opens onto the gate at the foot (z 0), 8 m below
    portal(R, P((C0, 10.9, UZ), (1, 0, 0), 2.2, GH), P((C0, 10.9, 0.0), (1, 0, 0), 2.2, GH))
    # walkers
    navloop(R, [(3.0, 3.0), (16.0, 3.0), (29.0, 3.0), (29.0, 16.0), (29.0, 29.0), (16.0, 29.0), (3.0, 29.0), (3.0, 16.0)])
    navloop(R, [(3.5, 3.5), (16.0, 4.2), (28.5, 3.5), (28.0, 16.0), (28.5, 28.5), (16.0, 28.0), (3.5, 28.5), (4.2, 16.0)], z=UZ)
    navloop(R, [(14.0, 14.0), (18.0, 14.0), (18.0, 18.0), (14.0, 18.0)])
    s = [R.navpt(13.6, 14.0), R.navpt(13.5, 10.9), R.navpt(18.8, 10.9, 2.0), R.navpt(21.1, 13.2, 2.0), R.navpt(21.1, 18.8, 4.0),
         R.navpt(18.8, 21.1, 4.0), R.navpt(13.2, 21.1, 6.0), R.navpt(10.9, 18.8, 6.0), R.navpt(10.9, 13.2, UZ), R.navpt(10.9, 10.9, UZ), R.navpt(6.0, 10.9, UZ)]
    R.link(*s)
    secret(R, (KX0 + KX1) / 2, (KY0 + KY1) / 2 + 0.6, 4.0, 'The Room on the Second Lap',
           'The spur off the third landing ends at a bookcase, and the bookcase opens. Behind it is a small room hung between the floors, with a desk and a lamp and a ledger in which somebody has counted the flights: four, eight, twelve, then a long column of numbers, then nothing.', r=2.0)
    fx(R, 'dust', [C0, C0, 0.5, C1, C1, 14.0])
    return done(R, 'The Endless Stair', weight=3, probe=(16.0, 16.0, 9.0), top=2 * LH - 0.6,
                blurb='A stair climbs round a court of books, flight after flight, and at the top of the fourth flight a stone gate. Through the gate is the foot of the first flight. You have climbed eight metres. You are where you started.')


def halls(R):
    R.cut(box(T - 0.01, T - 0.01, 0, W - T + 0.01, D - T + 0.01, TOP, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.01, T - 0.01, UZ, W - T + 0.01, D - T + 0.01, 2 * LH - 0.6, 'tile', bottom='floor', top='plaster'))
    R.cut(box(V0, V0, 0, V1, V1, 2 * LH - 0.6, 'tile', bottom='terrazzo', top='plaster'))
    # piers round the atrium on the ground floor, holding the gallery's edge
    for t in (V0, 12.2, 16.0, 19.8, V1):
        for (x, y) in ((t, V0 - 0.3), (t, V1 + 0.3), (V0 - 0.3, t), (V1 + 0.3, t)):
            R.parts.add(box(x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, TOP, 'tile', skip=('-z', '+z')))
    # the gallery's edge: a stone fascia and a rail (open where the bridges come in)
    R.parts.add(box(V0 - 0.3, V0 - 0.3, TOP - 0.5, V1 + 0.3, V0, UZ, 'tile', skip=('+z',)))
    rect_rails(R, V0, V0, V1, V1, UZ, opens={'S': [(O0, C0)], 'W': [(O0, C0)]}, inset=-0.08)
    # skylight: a grid of glowing panes over the atrium
    for i in (1, 2):
        for j in (1, 2):
            x0, y0 = V0 + 0.4 + i * 3.8, V0 + 0.4 + j * 3.8
            R.light(box(x0 + 0.6, y0 + 0.6, 2 * LH - 0.62, x0 + 2.8, y0 + 2.8, 2 * LH - 0.6, 'e_sky'))
    for t in [V0 + 0.2 + k * 3.8 for k in range(5)]:
        R.nocol.add(box(t - 0.1, V0, 2 * LH - 0.85, t + 0.1, V1, 2 * LH - 0.6, 'iron', skip=('+z',)))
        R.nocol.add(box(V0, t - 0.1, 2 * LH - 0.85, V1, t + 0.1, 2 * LH - 0.6, 'iron', skip=('+z',)))


def stair(R):
    w = O1 - C1          # 2.2
    # the four flights
    flight(R, F0, O0, 0.0, w, N_, RISE, RUN, '+x', m='terrazzo', rails='')
    flight(R, C1, F0, 2.0, w, N_, RISE, RUN, '+y', m='terrazzo', rails='')
    flight(R, F1, C1, 4.0, w, N_, RISE, RUN, '-x', m='terrazzo', rails='')
    flight(R, O0, F1, 6.0, w, N_, RISE, RUN, '-y', m='terrazzo', rails='')
    # the flats and landings between them
    deck(R, F1, O0, O1, C0, 2.0, th=2.0)            # south, after flight 1, and the SE landing (solid below)
    deck(R, C1, C0, O1, F0, 2.0, th=2.0)            # east, before flight 2
    R.parts.add(box(C1, F0, 0, O1, F1, 2.0, 'tile', skip=('+z',)))   # under flight 2
    deck(R, C1, F1, O1, O1, 4.0)                    # east after flight 2 and the NE landing
    deck(R, F1, C1, C1, O1, 4.0)                    # north before flight 3
    deck(R, O0, C1, F0, O1, 6.0)                    # north after flight 3 and the NW landing
    deck(R, O0, F1, C0, C1, 6.0)                    # west before flight 4
    deck(R, O0, O0, C0, F0, UZ)                     # west after flight 4 and the SW landing (top)
    deck(R, V0, O0, O0, C0, UZ); deck(R, O0, V0, C0, O0, UZ)   # bridges to the gallery
    for (x, y, z) in ((O1 - 0.3, F1 + 0.3, 4.0), (O1 - 0.3, O1 - 0.3, 4.0), (C1 + 0.3, O1 - 0.3, 4.0), (F1 - 0.3, O1 - 0.3, 4.0),
                      (O0 + 0.3, O1 - 0.3, 6.0), (F0 - 0.3, O1 - 0.3, 6.0), (O0 + 0.3, F1 - 0.3, 6.0), (C0 - 0.3, F1 - 0.3, 6.0),
                      (O0 + 0.3, O0 + 0.3, UZ), (C0 - 0.3, O0 + 0.3, UZ), (O0 + 0.3, F0 - 0.3, UZ), (C0 - 0.3, F0 - 0.3, UZ)):
        pier(R, x, y, 0.0, z - 0.3, 0.2)
    # rails: the court side and the outer side, sloping with the flights
    inner = [((F0, C0, 0.0), (F1, C0, 2.0)), ((F1, C0, 2.0), (C1, C0, 2.0)),
             ((C1, C0, 2.0), (C1, F0, 2.0)), ((C1, F0, 2.0), (C1, F1, 4.0)), ((C1, F1, 4.0), (C1, C1, 4.0)),
             ((C1, C1, 4.0), (F1, C1, 4.0)), ((F1, C1, 4.0), (F0, C1, 6.0)), ((F0, C1, 6.0), (C0, C1, 6.0)),
             ((C0, C1, 6.0), (C0, F1, 6.0)), ((C0, F1, 6.0), (C0, F0, UZ)), ((C0, F0, UZ), (C0, C0, UZ))]
    outer = [((F0, O0, 0.0), (F1, O0, 2.0)), ((F1, O0, 2.0), (O1, O0, 2.0)),
             ((O1, O0, 2.0), (O1, F0, 2.0)), ((O1, F0, 2.0), (O1, F1, 4.0)), ((O1, F1, 4.0), (O1, O1, 4.0)),
             ((O1, O1, 4.0), (21.5, O1, 4.0)), ((20.1, O1, 4.0), (F1, O1, 4.0)), ((F1, O1, 4.0), (F0, O1, 6.0)), ((F0, O1, 6.0), (O0, O1, 6.0)),
             ((O0, O1, 6.0), (O0, F1, 6.0)), ((O0, F1, 6.0), (O0, F0, UZ)), ((O0, F0, UZ), (O0, C0, UZ)),
             ((V0, O0, UZ), (O0, O0, UZ)), ((V0, C0, UZ), (O0, C0, UZ)), ((O0, V0, UZ), (O0, O0, UZ)), ((C0, V0, UZ), (C0, O0, UZ))]
    for (p0, p1) in inner + outer:
        # nudge the rail onto the walking side of the edge
        cx, cy = (C0 + C1) / 2, (C0 + C1) / 2
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        on_inner = (p0, p1) in inner
        # inner rails step outward (away from the court), outer rails step inward (toward it)
        tx, ty = (mx - cx, my - cy) if on_inner else (cx - mx, cy - my)
        s = 0.07 if nx * tx + ny * ty > 0 else -0.07
        a = (p0[0] + nx * s, p0[1] + ny * s, p0[2] + (0.12 if p0[2] != p1[2] else 0))
        b = (p1[0] + nx * s, p1[1] + ny * s, p1[2])
        seg_rail(R, a, b, h=1.0)


def gates(R):
    """Two identical stone gates: at the foot of the first flight (z 0) and on the top landing (z 8)."""
    for z in (0.0, UZ):
        R.parts.add(local(architrave(2.2, GH, 'tile', bw=0.3, depth=0.16), math.pi, C0, 10.9, z))
        R.parts.add(local(box(-0.4, 0, GH + 0.55, 0.4, 0.3, GH + 1.0, 'gilt'), math.pi, C0, 10.9, z))
    R.parts.add(local(architrave(2.2, GH, 'tile', bw=0.3, depth=0.16), 0.0, C0, 10.9, 0.0))
    R.parts.add(local(architrave(2.2, GH, 'tile', bw=0.3, depth=0.16), 0.0, C0 + 1.3, 10.9, UZ))
    # behind the upper gate: the recess the portal needs, closed in so nothing falls out
    R.parts.add(deck_geo(C0, O0, C0 + 1.1, C0, UZ))
    R.parts.add(box(C0, O0 - 0.3, UZ - 0.3, C0 + 1.2, O0, UZ + GH + 0.4, 'tile'))
    R.parts.add(box(C0, C0, UZ - 0.3, C0 + 1.2, C0 + 0.3, UZ + GH + 0.4, 'tile'))
    R.parts.add(box(C0 + 1.1, O0, UZ - 0.3, C0 + 1.3, C0, UZ + GH + 0.4, 'tile'))
    R.parts.add(box(C0, O0, UZ + GH, C0 + 1.2, C0, UZ + GH + 0.4, 'tile'))
    # and behind the lower gate too (a portal must never be seen from behind): its twin recess, closed
    R.parts.add(box(C0 - 1.2, O0 - 0.3, 0.0, C0, O0, GH + 0.4, 'tile'))
    R.parts.add(box(C0 - 1.2, C0, 0.0, C0, C0 + 0.3, GH + 0.4, 'tile'))
    R.parts.add(box(C0 - 1.3, O0 - 0.3, 0.0, C0 - 1.1, C0 + 0.3, GH + 0.4, 'tile'))
    R.parts.add(box(C0 - 1.2, O0, GH, C0, C0, GH + 0.4, 'tile'))
    # a lamp over each gate
    for z in (0.0, UZ):
        lantern(R, C0 - 0.35, 10.9, z + GH + 1.1)


def deck_geo(x0, y0, x1, y1, z, th=0.3):
    return box(x0, y0, z - th, x1, y1, z, 'tile', top='terrazzo', bottom='plaster')


def spur_room(R):
    """A spur off the NE landing (z 4) north to a bookcase, and the room behind it."""
    deck(R, 20.1, O1, 21.5, KY0, 4.0)
    rail(R, 20.16, O1, 20.16, KY0 - 0.05, z=4.0, h=1.0)
    rail(R, 21.44, O1, 21.44, KY0 - 0.05, z=4.0, h=1.0)
    pier(R, 20.8, KY0 - 0.9, 0.0, 3.7, 0.18)
    # the block the room sits on (books round it on the ground floor), and the room
    R.parts.add(box(KX0, KY0, 0, KX1, KY1, 4.0, 'tile', skip=('-z',)))
    R.parts.add(box(KX0, KY0, 4.0, 20.2, KY0 + 0.3, TOP, 'tile'))
    R.parts.add(box(21.4, KY0, 4.0, KX1, KY0 + 0.3, TOP, 'tile'))
    R.parts.add(box(20.2, KY0, 6.3, 21.4, KY0 + 0.3, TOP, 'tile'))
    R.parts.add(box(KX0, KY1 - 0.3, 4.0, KX1, KY1, TOP, 'tile'))
    R.parts.add(box(KX0, KY0, 4.0, KX0 + 0.3, KY1, TOP, 'tile'))
    R.parts.add(box(KX1 - 0.3, KY0, 4.0, KX1, KY1, TOP, 'tile'))
    shelf(R, 21.45, KY0, 4.0, 1.3, '-y', rows=5, frame='walnut', solid=False)
    sh(R, '-y', KY0, KX0 + 0.1, 20.1, z=4.0, rows=5, frame='walnut')
    sh(R, '-y', KY0, 21.5, KX1 - 0.1, z=4.0, rows=5, frame='walnut')
    for (face, bk, a, b) in (('+x', KX1, KY0 + 0.3, KY1 - 0.3), ('-x', KX0, KY0 + 0.3, KY1 - 0.3), ('+y', KY1, KX0 + 0.3, KX1 - 0.3)):
        sh(R, face, bk, a, b, rows=9, frame='walnut')
    # inside: floor, desk, lamp, ledger
    R.nocol.add(box(KX0 + 0.3, KY0 + 0.3, 4.0, KX1 - 0.3, KY1 - 0.3, 4.012, 'carpet'))
    R.parts.add(ltable(18.2, 27.6, 19.8, 28.5, top='leather').xform(0, 0, 0, 4.0))
    llamp(R, 18.5, 28.25, 4.76, m='e_amber')
    open_book(R, 19.2, 27.95, 4.76, ang=0.0)
    R.parts.add(lchair(19.0, 27.1, math.pi / 2).xform(0, 0, 0, 4.0))
    pendant(R, 19.4, 27.2, 6.4, TOP, r=0.24)
    sh(R, '+x', KX0 + 0.3, KY0 + 0.4, KY1 - 0.4, z=4.0, rows=7, frame='walnut')
    sh(R, '-x', KX1 - 0.3, KY0 + 0.4, KY1 - 0.4, z=4.0, rows=7, frame='walnut')
    R.spot('plaque', 19.4, KY1 - 0.7, 5.4, -math.pi / 2, text='Lap 1: 8 m. Lap 2: 16 m. Lap 3: 24 m.')


def dressing(R):
    # books on the outer walls of both floors (clear of the doorways)
    for z, rows in ((0.0, 16), (UZ, 16)):
        for (a, b) in ((0.8, 6.3), (9.7, 22.3), (25.7, W - 0.8)):
            sh(R, '+y', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-y', D - T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '+x', T, a, b, z=z, rows=rows, frame='walnut')
            sh(R, '-x', W - T, a, b, z=z, rows=rows, frame='walnut')
    # the court: shelves on the inner faces of the stair's solid parts, tables and lamps on the floor
    sh(R, '+y', C0, F1 + 0.2, C1 - 0.1, rows=4, frame='walnut')
    sh(R, '-x', C1, C0 + 0.1, F0 - 0.1, rows=4, frame='walnut')
    sh(R, '-x', C1, F0 + 0.1, F1 - 0.1, rows=4, frame='walnut')
    for (x, y) in ((14.5, 16.5), (17.5, 16.5)):
        R.parts.add(ltable(x - 0.9, y - 0.5, x + 0.9, y + 0.5, top='leather'))
        llamp(R, x, y, 0.76)
        R.parts.add(lchair(x, y - 0.95, math.pi / 2)); R.parts.add(lchair(x, y + 0.95, -math.pi / 2))
    # the spur room's block, dressed with books on the ground floor
    sh(R, '-y', KY0, KX0 + 0.1, KX1 - 0.1, rows=8, frame='walnut')
    sh(R, '-x', KX0, KY0 + 0.1, KY1 - 0.1, rows=8, frame='walnut')
    # ground floor: reading tables under the gallery, lamps
    for (x, y, a) in ((4.2, 11.0, 0), (4.2, 21.0, 0), (27.8, 11.0, 0), (27.8, 21.0, 0), (11.0, 4.2, 1), (21.0, 4.2, 1)):
        if a: R.parts.add(ltable(x - 1.4, y - 0.5, x + 1.4, y + 0.5, top='leather')); llamp(R, x, y, 0.76)
        else: R.parts.add(ltable(x - 0.5, y - 1.4, x + 0.5, y + 1.4, top='leather')); llamp(R, x, y, 0.76, a=math.pi / 2)
    for (x, y) in ((4.2, 4.2), (27.8, 4.2), (4.2, 27.8), (27.8, 27.8), (4.2, 16.0), (27.8, 16.0), (16.0, 4.2), (10.0, 27.8)):
        pendant(R, x, y, 5.2, TOP, r=0.3)
        pendant(R, x, y, UZ + 5.0, 2 * LH - 0.6, r=0.3)
    for (x, y) in ((16.0, 27.8), (22.0, 27.8)):
        pendant(R, x, y, UZ + 5.0, 2 * LH - 0.6, r=0.3)
    # gallery tables
    for (x, y) in ((4.2, 11.0), (27.8, 21.0), (11.0, 27.8), (21.0, 4.2)):
        R.parts.add(ltable(x - 0.8, y - 0.8, x + 0.8, y + 0.8, top='leather').xform(0, 0, 0, UZ))
        llamp(R, x, y, UZ + 0.76, m='e_amber')
    for (x, y) in ((C0 + 0.3, C0 + 0.3), (C1 - 0.3, C1 - 0.3)):
        candlestick(R, x, y, 0.0, h=1.2)
