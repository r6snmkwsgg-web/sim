"""The Symmetrical Hall: a long vaulted reading hall that is the same on both sides of its aisle and the
same at both ends, every case, every bust, every lamp matched by its twin; tall mirrors either side of
both end doors carry it on into the distance. One thing does not match: on the north side a bust has
turned its head, and the bookcase it is looking at has no lamp over it. That bookcase is a door. Behind
it, in the thickness of the wall, is where the leftovers go: the one crooked room in the hall."""
from kit_h8 import *
from kit_h3 import arc_band
from kit_h4 import sconce
from kit_e import bust

W, D = 32.0, 16.0
Y0, Y1 = 2.85, 13.15              # the hall between its thick side walls
HW = Y1 - Y0
JAMB, RISE = 5.0, 2.4
CASES = [(0.6, 5.9), (10.1, 12.6), (12.9, 15.4), (16.6, 19.1), (19.4, 21.9), (26.1, 31.4)]
SEC = (12.9, 15.4)                # the one on the north wall that is a door
SX0, SX1, SY0 = 10.4, 21.6, Y1 + 0.3   # the hidden room: x SX0..SX1, y SY0..D-T
SH = 3.2


def make():
    R = Room('symmetry', 2, 1, res=2048)
    R.sockets(floor='tile', wall='tile')
    pr = arch_profile(D / 2, HW, 0, JAMB, 28, rise=RISE)
    mats = ['tile', 'tile'] + ['plaster'] * (len(pr) - 3) + ['tile']
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, mats, cap='tile'))
    # the doorways through the thick side walls
    dp = arch_profile(0, DW, 0, DJ)
    for c in (8.0, 24.0):
        R.cut(prism([(p + c, q) for p, q in dp], 'y', T + 0.4, Y0 + 0.05, arch_mats(len(dp), 'tile', 'tile')))
        R.cut(prism([(p + c, q) for p, q in dp], 'y', Y1 - 0.05, D - T - 0.4, arch_mats(len(dp), 'tile', 'tile')))
    vault(R)
    cases(R)
    furnish(R)
    ends(R)
    hidden(R)
    g = navloop(R, [(2.8, 7.1), (16, 7.1), (29.2, 7.1), (29.2, 8.9), (16, 8.9), (2.8, 8.9)])
    a, b = R.navpt(8, 3.8), R.navpt(24, 3.8)
    R.link(g[0], a, g[1], b, g[2])
    c, d = R.navpt(8, 12.2), R.navpt(24, 12.2)
    R.link(g[5], c, g[4], d, g[3])
    secret(R, 14.2, 14.6, 0.0, 'The Leftovers',
           'Behind the bookcase that had no twin is a narrow room where nothing matches: the shelves lean, the chairs are odd, the books are stacked any way. It is a great relief.')
    return finish(R, 'The Symmetrical Hall', weight=4, probe=(16, 8, 2.5), top=7.45,
                  blurb='Everything here has a twin across the aisle, down to the books. You find yourself walking exactly down the middle, and you are not sure you chose to.')


def vault(R):
    """Ribs across the vault over every pilaster, and a spine of skylights."""
    for k in range(9):
        x = 16.0 + (k - 4) * 3.6
        R.nocol.add(prism(arc_band(D / 2, HW, JAMB, RISE, 0.0, 0.3, 28), 'x', x - 0.2, x + 0.2, 'tile', cap='tile'))
    for k in range(4):
        x = 16.0 + (k - 1.5) * 7.2
        R.cut(box(x - 1.0, D / 2 - 0.45, 7.2, x + 1.0, D / 2 + 0.45, 7.6, 'plaster'))
        R.light(box(x - 1.0, D / 2 - 0.45, 7.56, x + 1.0, D / 2 + 0.45, 7.58, 'e_sky'))


def cases(R):
    """Bookcases down both long walls, in mirrored pairs, with a brass sconce over each; busts between."""
    for (a, b) in CASES:
        R.shelf(a, Y0, 0, b - a, '+y', rows=10, frame='walnut')
        sconce(R, (a + b) / 2, Y0 + 0.05, 4.75, math.pi / 2)
        if (a, b) == SEC:
            R.shelf(b, Y1, 0, b - a, '-y', rows=10, frame='walnut', solid=False)
        else:
            R.shelf(b, Y1, 0, b - a, '-y', rows=10, frame='walnut')
            sconce(R, (a + b) / 2, Y1 - 0.05, 4.75, -math.pi / 2)
    # a moulded cornice over the cases, carried over the door arches
    for (y0, y1) in ((Y0, Y0 + 0.5), (Y1 - 0.5, Y1)):
        R.parts.add(box(T, y0, 4.4, W - T, y1, 4.55, 'tile'))
    # pilasters at the case ends
    for x in (0.45, 5.95, 10.05, 12.75, 15.45, 16.55, 19.25, 21.95, 26.05, W - 0.45):
        for (y0, y1) in ((Y0, Y0 + 0.42), (Y1 - 0.42, Y1)):
            R.parts.add(box(x - 0.14, y0, 0, x + 0.14, y1, 4.4, 'tile', skip=('-z', '+z')))
    # busts on pedestals, all looking at the aisle; all but one
    for x in (12.75, 16.0, 19.25):
        bust(R, x, Y0 + 0.75, math.pi / 2)
        bust(R, x, Y1 - 0.75, 0.25 if x == 12.75 else -math.pi / 2)


def furnish(R):
    """Two rows of reading tables with green lamps, a central aisle inlaid in slate."""
    for (x0, x1) in ((3.2, 6.8), (9.6, 14.6), (17.4, 22.4), (25.2, 28.8)):
        for (y0, y1) in ((4.35, 5.45), (10.55, 11.65)):
            reading_table(R, x0, y0, x1, y1, lamps=2 if x1 - x0 < 4 else 3)
    for y in (6.3, 9.7):
        R.parts.add(box(T, y - 0.06, 0, W - T, y + 0.06, 0.004, 'slate'))
    for k in range(7):
        x = 16.0 + (k - 3) * 4.4
        R.parts.add(poly_prism([(x, 7.5), (x + 0.5, 8.0), (x, 8.5), (x - 0.5, 8.0)], 0, 0.004, 'slate', 'slate', 'slate'))


def ends(R):
    """Each end wall: a round window over the door, and a tall mirror either side of it."""
    circ = [(8.0 + 1.1 * math.cos(2 * math.pi * k / 24), 5.7 + 1.1 * math.sin(2 * math.pi * k / 24)) for k in range(24)]
    mir = []
    for (x0, x1, xl, n) in ((-0.05, T + 0.02, 0.08, 1), (W - T - 0.02, W + 0.05, W - 0.08, -1)):
        R.cut(prism(circ, 'x', x0, x1, 'tile', cap='tile'))
        g = Geo(); ids = [g.vert((xl, p, q)) for p, q in circ]; g.face(ids if n > 0 else ids[::-1], 'e_sky', circ if n > 0 else circ[::-1])
        R.light(g)
        for k in range(4):
            a = math.pi * k / 4
            R.nocol.add(beam((xl + n * 0.05, 8.0 - 1.1 * math.cos(a), 5.7 - 1.1 * math.sin(a)), (xl + n * 0.05, 8.0 + 1.1 * math.cos(a), 5.7 + 1.1 * math.sin(a)), 0.05, 'iron'))
        xw = T if n > 0 else W - T
        for yc in (4.55, 11.45):
            mir.append({'c': [round(xw + n * 0.03, 3), yc, 0.25], 'n': [n, 0, 0], 'w': 2.9, 'h': 4.0})
            for (a0, a1, b0, b1) in ((yc - 1.55, yc + 1.55, 0.0, 0.25), (yc - 1.55, yc + 1.55, 4.25, 4.45), (yc - 1.55, yc - 1.45, 0.25, 4.25), (yc + 1.45, yc + 1.55, 0.25, 4.25)):
                R.parts.add(box(min(xw, xw + n * 0.12), a0, b0, max(xw, xw + n * 0.12), a1, b1, 'gilt'))
            R.parts.add(box(min(xw, xw + n * 0.02), yc - 1.45, 0.25, max(xw, xw + n * 0.02), yc + 1.45, 4.25, 'black'))
    R.meta['mirrors'] = mir


def hidden(R):
    """In the thickness of the north wall: a narrow room, crooked in every way the hall is not."""
    R.cut(box(SX0, SY0, 0, SX1, D - T, SH, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(SEC[0] + 0.15, Y1 - 0.05, 0, SEC[1] - 0.15, SY0 + 0.05, 2.5, 'plaster', bottom='floor', top='plaster'))
    rnd = random.Random(77)
    yb = D - T
    # leaning shelves, none square to anything
    for (x, a, L) in ((11.2, -math.pi / 2 + 0.12, 1.4), (17.0, -math.pi / 2 - 0.09, 1.8), (19.6, -math.pi / 2 + 0.2, 1.2)):
        g0 = len(R.slabs)
        kshelf(R, x, yb - 0.05, 0, L, a, rows=6, frame='oak', depth=0.28)
    R.parts.add(box(SX1 - 1.3, SY0 + 0.1, 0, SX1 - 0.1, SY0 + 0.7, 1.0, 'walnut'))
    for k in range(9):
        yy = rnd.choice((SY0 + 0.3, yb - 0.3))
        book_pile(R, rnd.uniform(SX0 + 0.5, SX1 - 1.6), yy, 0.0, rnd.randint(3, 9), seed=k, col=False)
    table(R, 16.8, yb - 0.8, 18.2, yb - 0.1, h=0.74, m='oak')
    desk_lamp(R, 17.1, yb - 0.4, 0.74)
    open_book(R, 17.7, yb - 0.45, 0.74, 0.5)
    chair(R, 18.65, yb - 0.45, math.pi + 0.3, frame='oak', seat='velvet')
    g = chair_geo(0, 0, 0, 'walnut', 'leather'); g = orient(g, 0.4, 0, 1.45, 20.9, 14.7, 0.25)
    R.nocol.add(g)
    bulb(R, 13.4, 14.4, 2.4, r=0.08, m='e_candle', top=SH, shade='green')
    bulb(R, 19.0, 14.6, 2.2, r=0.07, m='e_dim', top=SH)
    R.spot('plaque', SX0 + 0.05, 14.4, 1.6, 0.0, text='Everything out there has a twin. This is where the others went.')
