"""The Hall of Mirrors: a long vaulted corridor of bookcases where two great mirrors face each other
across the aisle, so the shelves and the lamps go on for ever in both directions. At each end, beside
the door, a narrow mirror in a gilt frame. The one at the west end is not a mirror: it is a way into
the room on the other side of the glass, where everything is the wrong way round and nobody is
looking back."""
from kit_h12 import *

W, D = 32.0, 16.0
X0, X1 = 2.0, 30.0            # the corridor's end walls
Y0, Y1 = 4.0, 12.0            # its side walls
SPRING, RISE = 5.0, 2.4
MX0, MX1 = 11.8, 20.2         # the great mirrors, both long walls
MZ0, MZ1 = 0.35, 4.85
FL = (4.35, 6.15)             # the narrow end mirrors, south of each end door
FH = 3.2
SX0, SX1 = 10.2, 21.9         # the room behind the glass (north zone)
SY0, SY1 = 12.45, 15.3
SH_ = 3.4
BX = 11.2                      # where you come out in it


def make():
    R = Room('mirrorhall', 2, 1, res=2048)
    rs = rng(72)
    R.sockets(floor='terrazzo', wall='tile')
    vault_x(R, X0 - 0.02, X1 + 0.02, (Y0 + Y1) / 2, Y1 - Y0, SPRING, RISE)
    tunnels(R, X0, Y0, X1, Y1, floor='terrazzo', wall='tile')
    ribs(R)
    walls(R, rs)
    ends(R)
    furnish(R, rs)
    behind(R, rs)
    lamps(R)
    # the two great mirrors, face to face
    mirror(R, (16.0, Y0 + 0.001, MZ0), (0, 1, 0), MX1 - MX0, MZ1 - MZ0)
    mirror(R, (16.0, Y1 - 0.001, MZ0), (0, -1, 0), MX1 - MX0, MZ1 - MZ0)
    # the narrow one at the east end is a mirror; its twin at the west end is a way through
    mirror(R, (X1 - 0.001, (FL[0] + FL[1]) / 2, 0.0), (-1, 0, 0), FL[1] - FL[0], FH)
    portal(R, {'c': [X0, (FL[0] + FL[1]) / 2, 0.0], 'n': [-1, 0, 0], 'w': FL[1] - FL[0], 'h': FH},
              {'c': [BX + 0.3, (SY0 + SY1) / 2, 0.0], 'n': [1, 0, 0], 'w': FL[1] - FL[0], 'h': FH})
    # walking graph: two lanes down the corridor, spurs to the doors
    ids = navgrid(R, {
        'a': (3.2, 6.4), 'b': (8.0, 6.4), 'c': (16.0, 6.0), 'd': (24.0, 6.4), 'e': (28.8, 6.4),
        'f': (28.8, 9.6), 'g': (24.0, 9.6), 'h': (16.0, 10.0), 'i': (8.0, 9.6), 'j': (3.2, 9.6),
        's1': (8.0, 2.2), 's2': (24.0, 2.2), 'n1': (8.0, 13.8), 'n2': (24.0, 13.8), 'w': (1.2, 8.0), 'e2': (30.8, 8.0)},
        [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g'), ('g', 'h'), ('h', 'i'), ('i', 'j'), ('j', 'a'),
         ('b', 's1'), ('d', 's2'), ('i', 'n1'), ('g', 'n2'), ('j', 'w'), ('f', 'e2')])
    secret(R, 16.0, (SY0 + SY1) / 2, 0.0, 'The Other Side of the Glass',
           'Behind the narrow mirror is the hall again, the wrong way round and much too small. The chair faces the glass. Nobody has ever been reflected in it.', r=2.2)
    return finish(R, 'The Hall of Mirrors', weight=4, probe=(16, 8, 2.4), top=SPRING + RISE,
                  blurb='Two mirrors face each other across the aisle, and the hall goes on in both of them for ever. In every copy you are a little further away.')


def ribs(R):
    """Transverse ribs over the vault at every pilaster, and a skylight spine."""
    for x in (X0 + 0.25, 6.2, 10.1, MX0 - 0.35, 16.0, MX1 + 0.35, 21.9, 25.8, X1 - 0.25):
        R.nocol.add(prism(arc_band((Y0 + Y1) / 2, Y1 - Y0, SPRING, RISE, 0.0, 0.28, 28), 'x', x - 0.18, x + 0.18, 'tile', cap='tile'))
        for y in (Y0, Y1):
            s = 1 if y == Y0 else -1
            R.parts.add(box(x - 0.2, min(y, y + s * 0.3), 0, x + 0.2, max(y, y + s * 0.3), SPRING, 'tile', skip=('-z',)))
    for x in (8.0, 24.0):
        R.cut(box(x - 1.4, 7.55, SPRING + RISE - 0.4, x + 1.4, 8.45, SPRING + RISE + 0.15, 'plaster'))
        R.light(box(x - 1.4, 7.55, SPRING + RISE + 0.1, x + 1.4, 8.45, SPRING + RISE + 0.12, 'e_sky'))


def walls(R, rs):
    """Tall bookcases along both long walls between the pilasters; the great mirrors in the middle bay."""
    segs = [(X0 + 0.45, 6.0), (10.3, MX0 - 0.55), (MX1 + 0.55, 21.7), (26.0, X1 - 0.45)]
    for (a, b) in segs:
        sh(R, '+y', Y0, a, b, rows=10, frame='walnut')
        sh(R, '-y', Y1, a, b, rows=10, frame='walnut')
    # a cornice over the cases, at the springing
    for (y0, y1) in ((Y0, Y0 + 0.45), (Y1 - 0.45, Y1)):
        R.parts.add(box(X0, y0, 4.45, X1, y1, 4.6, 'walnut'))
        R.parts.add(box(X0, y0, SPRING - 0.12, X1, y1, SPRING, 'tile'))
    # the mirror bays: a gilt frame, a dark wainscot under it
    for (y, s) in ((Y0, 1), (Y1, -1)):
        R.nocol.add(frame_rect('y', y, MX0, MX1, MZ0, MZ1, s, w=0.18, d=0.1))
        R.parts.add(box(MX0 - 0.2, min(y, y + s * 0.12), 0, MX1 + 0.2, max(y, y + s * 0.12), MZ0 - 0.18, 'walnut'))
        # a green-lamped console under each mirror
        c0, c1 = (y + s * 0.05, y + s * 0.6)
        R.parts.add(box(13.0, min(c0, c1), 0.78, 19.0, max(c0, c1), 0.84, 'walnut', top='leather'))
        for x in (13.1, 18.9):
            R.parts.add(box(x - 0.05, min(c0, c1), 0, x + 0.05, max(c0, c1), 0.78, 'walnut'))
        for x in (14.2, 17.8):
            desk_lamp(R, x, (c0 + c1) / 2, 0.84)
        book_pile(R, 16.0, (c0 + c1) / 2, 0.84, n=4, seed=int(y))
    # doorway surrounds: dark architraves
    for x in (8.0, 24.0):
        for (y, s) in ((Y0, 1), (Y1, -1)):
            R.nocol.add(frame_rect('y', y, x - 1.5, x + 1.5, 0.0, 3.2, s, w=0.22, d=0.06, m='walnut'))


def ends(R):
    """Each end wall: the door in the middle, a tall case to the north, a narrow gilt mirror to the south.
    At the west end the 'mirror' is a doorway with a recess behind it."""
    for (x, s) in ((X0, 1), (X1, -1)):
        # north flank: a case
        if s > 0: sh(R, '+x', x, 9.8, Y1 - 0.25, rows=10, frame='walnut')
        else: sh(R, '-x', x, 9.8, Y1 - 0.25, rows=10, frame='walnut')
        # the frame of the narrow mirror (identical at both ends)
        R.nocol.add(frame_rect('x', x, FL[0], FL[1], 0.0, FH, s, w=0.16, d=0.1))
        R.nocol.add(box(min(x, x + s * 0.14), FL[0] - 0.3, FH + 0.16, max(x, x + s * 0.14), FL[1] + 0.3, FH + 0.5, 'gilt'))
        sconce(R, x, FL[0] - 0.02, 2.6, math.pi / 2 if False else (0.0 if s > 0 else math.pi))
        R.nocol.add(frame_rect('x', x, 6.5, 9.5, 0.0, 3.2, s, w=0.22, d=0.06, m='walnut'))
    # the recess behind the false mirror at the west end: 1.1 m deep, a dark lining
    R.cut(box(X0 - 1.15, FL[0], 0.0, X0 + 0.02, FL[1], FH, 'walnut', bottom='terrazzo', top='walnut'))


def furnish(R, rs):
    """Reading tables down the aisle, between the mirrors, so they go on for ever too; a runner."""
    R.nocol.add(box(X0 + 0.6, 7.3, 0, X1 - 0.6, 8.7, 0.012, 'carpet'))
    for s in (-1, 1):
        R.nocol.add(box(X0 + 0.6, 8 + s * 0.7 - 0.04, 0, X1 - 0.6, 8 + s * 0.7 + 0.04, 0.014, 'gilt'))
    for (x0, x1) in ((3.4, 6.6), (12.4, 15.2), (16.8, 19.6), (25.4, 28.6)):
        reading_table(R, x0, 7.55, x1, 8.45, lamps=2, chairs=True)
    for (x, y, a) in ((4.4, Y0 + 0.9, math.pi / 2), (27.6, Y1 - 0.9, -math.pi / 2)):
        armchair(R, x, y, a)


def behind(R, rs):
    """The room behind the glass: a narrow copy of the hall, the wrong way round, too small, one chair
    facing the way you came. It is also reachable (by anyone who pushes on the right bookcase) from
    the north-east doorway passage."""
    R.cut(box(SX0 - 0.02, SY0, 0.0, SX1, SY1, SH_, 'tile', bottom='terrazzo', top='plaster'))
    # the way in from the doorway passage: a false case in its west wall
    R.cut(box(SX1 - 0.05, 13.25, 0.0, 22.55, 14.75, 2.4, 'walnut', bottom='terrazzo', top='walnut'))
    R.shelf(22.5, 14.9, 0.0, 1.8, '+x', rows=6, frame='walnut', solid=False)
    # cases on the north side (on the south side in the hall), lamps, the wrong way round
    sh(R, '-y', SY1, 12.4, 15.8, rows=7, frame='walnut')
    sh(R, '-y', SY1, 16.6, 20.8, rows=7, frame='walnut')
    sh(R, '+y', SY0, 13.6, 17.4, rows=7, frame='walnut')
    sh(R, '+y', SY0, 18.2, 21.0, rows=4, frame='walnut')
    # the chair, facing the glass; a table with a lamp; one book open
    c = chair_geo(12.8, 13.9, math.pi); R.parts.add(c)
    R.spot('sit', 12.8, 13.9, 0.48, math.pi)
    R.parts.add(table_geo(13.4, 13.4, 14.3, 14.4, 0.76, 'walnut', top='leather'))
    desk_lamp(R, 13.85, 14.2, 0.76)
    open_book(R, 13.85, 13.75, 0.76, -math.pi / 2)
    R.nocol.add(box(SX0 + 0.8, 13.45, 0, SX1 - 0.4, 14.3, 0.012, 'carpet'))
    for x in (14.0, 17.5, 20.5):
        pendant(R, x, 13.9, 2.5, SH_, r=0.18)
    R.spot('plaque', 19.0, 13.9, 0.0, math.pi,
           text='A card in a frame, written backwards, which in here reads forwards: THIS SIDE IS THE ORIGINAL.')
    # the way back: the glass stands in a wall across the west end, a recess behind it
    yc = (SY0 + SY1) / 2
    b0, b1 = yc - (FL[1] - FL[0]) / 2, yc + (FL[1] - FL[0]) / 2
    R.parts.add(box(BX, SY0 - 0.02, 0, BX + 0.3, b0, SH_, 'tile'))
    R.parts.add(box(BX, b1, 0, BX + 0.3, SY1 + 0.02, SH_, 'tile'))
    R.parts.add(box(BX, b0, FH, BX + 0.3, b1, SH_, 'tile', skip=('+z',)))
    R.nocol.add(frame_rect('x', BX + 0.3, b0, b1, 0.0, FH, 1, w=0.16, d=0.1))
    R.nocol.add(box(BX + 0.3, b0 - 0.3, FH + 0.16, BX + 0.44, b1 + 0.3, FH + 0.5, 'gilt'))


def lamps(R):
    """Green pendants down the aisle; amber night lamps by the doors."""
    for x in (4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0):
        pendant(R, x, 8.0, 3.2, SPRING + RISE - 0.1, r=0.24)
    for x in (6.2, 9.8, 22.2, 25.8):
        for y in (Y0 + 0.02, Y1 - 0.02):
            R.light(sphere(x, y + (0.12 if y < 8 else -0.12), 3.5, 0.08, 8, 4, 'e_amber'))
