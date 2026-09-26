"""The Repeating Door: a corridor of identical doorways, one after another, a single book lying on the floor
between each pair. The last doorway opens onto the first (a portal), so through it the corridor goes on
for ever, a book in every stretch. One plain side door lets you out again; one bookcase, identical to all
the others, is not a bookcase, and behind it is a reading room that is not in the loop."""
from kit_h11 import *

W, D = 32.0, 16.0
CY0, CY1 = 6.0, 10.0          # the corridor's walls
CH = 5.2                      # its ceiling
FX = [6.0 + 3.6 * k for k in range(6)]   # the doorways (frame centres)
FT = 0.25                     # half a frame's thickness
OW, OH = 2.0, 3.2             # the openings
SEG = [(FX[k] + FT, FX[k + 1] - FT) for k in range(5)]
EX0, EX1 = 17.9, 19.3         # the side door out (segment 3, south wall)
RX0, RX1, RY0 = 9.8, 20.2, 10.4   # the reading room


def make():
    R = Room('loopcorridor', 2, 1, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    halls(R)
    corridor(R)
    reading_room(R)
    strips(R)
    # the portal: the last doorway (its west face) opens onto the first
    portal(R, P((FX[5] - FT, 8.0, 0.0), (1, 0, 0), OW, OH), P((FX[0] - FT, 8.0, 0.0), (1, 0, 0), OW, OH))
    # walkers: round the strips and vestibules, and along the corridor as far as the last door
    navloop(R, [(2.5, 2.5), (8.0, 2.8), (16.0, 2.8), (24.0, 2.8), (29.0, 2.8), (29.0, 8.0), (29.0, 13.0), (24.0, 13.2),
                (29.0, 8.0), (29.0, 2.8), (16.0, 2.8), (2.5, 2.8), (2.5, 8.0), (2.5, 13.0), (7.5, 13.2), (2.5, 13.0)], close=False)
    c = [R.navpt(x, 8.0) for x in (3.5, 7.8, 11.4, 15.0, 18.6, 22.0)]
    R.link(*c)
    s0, s1 = R.navpt(18.6, 7.0), R.navpt(18.6, 3.5)
    R.link(c[4], s0, s1)
    secret(R, 15.0, 13.0, 0.0, 'The Reading Room Outside the Loop',
           'Behind the bookcase that is the same as every other bookcase there is a quiet room, and in it nothing repeats: one chair, one lamp, one book open at a page you have not read. You sit for a while. The corridor goes on without you.', r=2.2)
    fx(R, 'dust', [6.0, CY0, 0.3, 25.0, CY1, CH - 0.2])
    return done(R, 'The Repeating Door', weight=4, probe=(16.0, 3.0, 2.2), top=7.4,
                blurb='A doorway, and beyond it a doorway, and beyond that one another, each with a single book lying on the floor in front of it. You pick up the book. The next doorway has one too.')


def halls(R):
    """The vestibules at each end and the stack halls either side of the corridor."""
    for (x0, y0, x1, y1) in ((T, T, 5.5, D - T), (T, T, W - T, CY0 - 0.4), (T, CY1 + 0.4, RX0 - 0.4, D - T),
                             (RX1 + 0.4, CY1 + 0.4, W - T, D - T), (25.6, T, W - T, D - T)):
        R.cut(box(x0 - 0.01, y0 - 0.01, 0, x1 + 0.01, y1 + 0.01, 7.4, 'tile', bottom='terrazzo', top='plaster'))
    # coffers: plaster beams across the strips
    for x in range(4, 31, 4):
        R.parts.add(box(x - 0.2, T, 6.9, x + 0.2, CY0 - 0.4, 7.4, 'plaster', skip=('+z',)))
        if x < RX0 - 0.4 or x > RX1 + 0.4:
            R.parts.add(box(x - 0.2, CY1 + 0.4, 6.9, x + 0.2, D - T, 7.4, 'plaster', skip=('+z',)))


def corridor(R):
    R.cut(box(5.4, CY0, 0, 25.2, CY1, CH, 'tile', bottom='terrazzo', top='plaster'))
    # the side door out, in segment 3's south wall
    R.cut(box(EX0, CY0 - 0.45, 0, EX1, CY0 + 0.02, 2.5, 'tile', bottom='terrazzo', top='plaster'))
    for face, yy in ((math.pi / 2, CY0), (-math.pi / 2, CY0 - 0.4)):
        R.parts.add(local(architrave(EX1 - EX0, 2.5, bw=0.16, depth=0.08), face, (EX0 + EX1) / 2, yy, 0))
    # the doorways: walls across the corridor with an opening, and a walnut surround on both faces
    for k, x in enumerate(FX):
        g = Geo()
        g.add(box(x - FT, CY0, 0, x + FT, 8.0 - OW / 2, CH, 'tile', skip=('-y', '+z')))
        g.add(box(x - FT, 8.0 + OW / 2, 0, x + FT, CY1, CH, 'tile', skip=('+y', '+z')))
        g.add(box(x - FT, 8.0 - OW / 2, OH, x + FT, 8.0 + OW / 2, CH, 'tile', skip=('+z',)))
        R.parts.add(g)
        for face, xx in ((math.pi, x - FT), (0.0, x + FT)):
            R.parts.add(local(architrave(OW, OH, 'walnut', bw=0.26, depth=0.1), face, xx, 8.0, 0))
            R.parts.add(local(box(-0.32, 0, 4.25, 0.32, 0.14, 4.7, 'walnut'), face, xx, 8.0, 0))   # a carved block over the cornice
        # a green lamp on a pedestal either side, on the approach (west) face
        for y in (CY0 + 0.45, CY1 - 0.45):
            R.parts.add(box(x - FT - 0.75, y - 0.2, 0, x - FT - 0.35, y + 0.2, 1.05, 'walnut', skip=('-z',)))
            llamp(R, x - FT - 0.55, y, 1.05, a=math.pi / 2)
    # each stretch between two doorways: bookcases both sides, a lamp above, a book on the floor
    for k, (a, b) in enumerate(SEG):
        if k != 3:
            sh(R, '+y', CY0, a + 0.05, b - 0.05, rows=9, frame='walnut')
        else:
            sh(R, '+y', CY0, a + 0.05, EX0 - 0.35, rows=9, frame='walnut') if EX0 - 0.35 - a > 0.6 else None
            sh(R, '+y', CY0, EX1 + 0.35, b - 0.05, rows=9, frame='walnut') if b - EX1 - 0.35 > 0.6 else None
        if k == 1:
            # the false bookcase, and the way through the wall behind it
            shelf(R, b - 0.05, CY1, 0, (b - a) - 0.1, '-y', rows=9, frame='walnut', solid=False)
            R.cut(box(a + 0.3, CY1 - 0.05, 0, b - 0.3, RY0 + 0.05, 2.3, 'tile', bottom='terrazzo', top='plaster'))
        else:
            sh(R, '-y', CY1, a + 0.05, b - 0.05, rows=9, frame='walnut')
        m = (a + b) / 2
        pendant(R, m, 8.0, 3.6, CH, r=0.22)
        floor_book(R, m + 0.15, 7.85, 0.0, a=0.35, m='green')
    # ceiling mouldings along the corridor
    for y in (CY0, CY1 - 0.3):
        R.parts.add(box(5.5, y, CH - 0.3, 25.2, y + 0.3, CH, 'plaster', skip=('+z',)))
    # beyond the last doorway (only its recess is ever seen): a short stretch and a blank wall
    R.parts.add(box(FX[5] + 0.8, CY0, 0, FX[5] + 0.85, CY1, CH, 'walnut'))


def reading_room(R):
    R.cut(box(RX0, RY0, 0, RX1, D - T, 4.2, 'damask', bottom='floor', top='plaster'))
    rug(R, 11.0, 11.4, 19.0, 15.0)
    for (x0, x1) in ((RX0 + 0.1, 12.6), (13.4, 16.6), (17.4, RX1 - 0.1)):
        sh(R, '-y', D - T, x0, x1, rows=7, frame='walnut')
    sh(R, '+x', RX0, RY0 + 1.6, D - T - 0.1, rows=7, frame='walnut')
    sh(R, '-x', RX1, RY0 + 0.3, D - T - 0.1, rows=7, frame='walnut')
    armchair(R, 14.2, 13.2, -math.pi / 2)
    R.parts.add(ltable(15.0, 12.7, 16.4, 13.7, top='leather'))
    llamp(R, 15.3, 13.4, 0.76)
    open_book(R, 15.9, 13.1, 0.76, ang=0.2)
    floor_lamp(R, 13.3, 14.4, 1.7)
    R.spot('plaque', 16.0, D - T - 0.4, 1.4, -math.pi / 2, text='Nothing here happens twice.')
    candles(R, [(16.2, 12.85, 0.76)], rng(5))


def strips(R):
    # bookcases round the vestibules and strips (clear of the doorways)
    rows = 14
    sh(R, '+y', T, 0.8, 6.4, rows=rows); sh(R, '+y', T, 9.6, 22.4, rows=rows); sh(R, '+y', T, 25.6, W - 0.8, rows=rows)
    sh(R, '-y', D - T, 0.8, 6.4, rows=rows); sh(R, '-y', D - T, 25.6, W - 0.8, rows=rows)
    sh(R, '+x', T, 0.8, 6.4, rows=rows); sh(R, '+x', T, 9.6, D - 0.8, rows=rows)
    sh(R, '-x', W - T, 0.8, 6.4, rows=rows); sh(R, '-x', W - T, 9.6, D - 0.8, rows=rows)
    # the corridor's outer walls, from the strips
    sh(R, '-y', CY0 - 0.4, 6.0, EX0 - 0.4, rows=rows); sh(R, '-y', CY0 - 0.4, EX1 + 0.4, 25.2, rows=rows)
    sh(R, '+y', CY1 + 0.4, 5.6, RX0 - 0.5, rows=rows); sh(R, '+y', CY1 + 0.4, RX1 + 0.5, 25.4, rows=rows)
    # the reading room's outer walls
    sh(R, '-x', RX0 - 0.4, CY1 + 0.5, D - 0.6, rows=rows); sh(R, '+x', RX1 + 0.4, CY1 + 0.5, D - 0.6, rows=rows)
    # the ends of the corridor block, seen from the vestibules
    # reading tables down the south strip, lamps over them
    for x in (12.0, 16.0, 20.0):
        R.parts.add(ltable(x - 1.1, 2.3, x + 1.1, 3.3, top='leather'))
        llamp(R, x, 2.8, 0.76)
        for s in (-0.6, 0.6):
            R.nocol.add(lchair(x + s, 1.75, math.pi / 2)); R.nocol.add(lchair(x + s, 3.85, -math.pi / 2))
        pendant(R, x, 2.8, 5.2, 7.4, r=0.3)
    for (x, y) in ((3.0, 3.0), (3.0, 13.0), (28.6, 3.0), (28.6, 13.0), (8.0, 13.0), (24.0, 13.0), (6.0, 3.0), (26.0, 3.0)):
        pendant(R, x, y, 5.0, 7.4, r=0.3)
    # night lights by the doors
    for (x, y) in ((1.0, 6.0), (1.0, 10.0), (W - 1.0, 6.0), (W - 1.0, 10.0)):
        lantern(R, x, y, 2.6)
    R.light(box(EX0 + 0.3, CY0 - 0.43, 2.62, EX1 - 0.3, CY0 - 0.41, 2.82, 'e_exit'))
