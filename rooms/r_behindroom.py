"""Behind the Room: an ordinary reading room, panelled, lamplit, bookcases round the walls. One of the
bookcases in the north wall is not there when you walk into it: behind it is the narrow, dusty world
behind the shelves, a slot of a passage between the bookcase backs and the old stone, full of pipes
and cables, where somebody has made a bed. A ladder at its end climbs to an iron catwalk that runs over
the doorways and round inside the east wall, to a stool at a slit where you can watch the reading room."""
from kit_h9 import *

W, D = 32.0, 16.0
XE, YN, H = 29.6, 13.6, 6.0              # the hall's east and north walls, its ceiling
CX0, CX1, CY0, CY1 = 10.4, 21.6, 14.0, 15.5   # the passage behind the north wall
UZ = 4.6                                 # the catwalk
EX0, EX1, EY0 = 29.95, 31.55, 1.0        # the catwalk inside the east wall
FX0, FX1 = 15.1, 16.5                    # the false bookcase


def make():
    R = Room('behindroom', 2, 1, res=2048)
    R.sockets(floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, XE, YN, H, 'damask', bottom='floor', top='plaster'))
    tunnel_y(R, 8.0, YN - 0.05, D - T - 0.5)
    tunnel_y(R, 24.0, YN - 0.05, D - T - 0.5)
    tunnel_x(R, 8.0, XE - 0.05, W - T - 0.5)
    hall(R)
    passage(R)
    catwalk(R)
    secret(R, 11.4, 14.8, 0.0, 'Behind the Shelves',
           'Behind the bookcase there is a whole other room, one person wide, that the reading room does not know about. Somebody sleeps here, between the pipes, with the backs of the books for a wall.')
    secret(R, 30.75, 2.0, UZ, 'The Watcher\'s Stool',
           'A stool, a notebook, and a slit in the wall at the height of the lamps. The notebook is a list of everyone who has ever sat in the reading room below, and the last line is you.')
    fx(R, 'dust', [CX0, CY0, 0.3, CX1, CY1, 4.0])
    fx(R, 'dust', [EX0, EY0, UZ, EX1, CY1, UZ + 2.6])
    return finish(R, 'The Reading Room', weight=6, probe=(14, 7, 1.8),
                  blurb='A reading room, quite normal: lamps, tables, bookcases round the walls. It is so normal that you find yourself looking at the bookcases, and wondering what is behind them.')


# ---------------------------------------------------------------------------
def hall(R):
    rows = 9
    # wainscot and cornice
    for (x0, y0, x1, y1) in ((T, T, XE, T + 0.04), (T, YN - 0.04, XE, YN), (T, T, T + 0.04, YN), (XE - 0.04, T, XE, YN)):
        R.parts.add(box(x0, y0, H - 0.35, x1, y1, H, 'ivory'))
    # bookcases round the walls, broken at the doorways
    for (a, b) in ((0.6, 6.0), (10.0, 22.0), (26.0, XE - 0.3)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, 6.0), (10.0, FX0 - 0.05), (FX1 + 0.05, 22.0), (26.0, XE - 0.3)):
        sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
    # the one that is not there
    shelf(R, FX1, YN, 0, FX1 - FX0, '-y', rows=rows, frame='walnut', solid=False)
    R.cut(box(FX0 + 0.05, YN - 0.1, 0, FX1 - 0.05, CY0 + 0.05, 2.2, 'wood', bottom='slate', top='wood'))
    for (a, b) in ((0.6, 6.0), (10.0, YN - 0.3)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', XE, a, b, rows=rows, frame='walnut')
    # over the doorways, a short row
    for c in (8.0, 24.0):
        sh(R, '+y', T, c - 2.0, c + 2.0, z=4.3, rows=2, frame='walnut')
        sh(R, '-y', YN, c - 2.0, c + 2.0, z=4.3, rows=2, frame='walnut')
    sh(R, '+x', T, 6.0, 10.0, z=4.3, rows=2, frame='walnut')
    sh(R, '-x', XE, 6.0, 10.0, z=4.3, rows=2, frame='walnut')
    # a couple of books have come out of the false case, as if somebody went through in a hurry
    rnd = random.Random(3)
    g = Geo()
    for (x, y, a) in ((15.4, 12.9, 0.4), (16.1, 12.6, 1.9), (15.8, 13.05, 2.6)):
        g.add(book(x, y, 0.0, a, rnd.choice(BOOKM)))
    R.nocol.add(g)
    # the rug and two long reading tables
    rug(R, 5.0, 4.2, 26.0, 9.8, m='carpet', border='gilt')
    for (x0, x1) in ((6.2, 13.8), (17.8, 25.4)):
        R.parts.add(table(x0, 6.4, x1, 7.6, 0.78, 'walnut', top='leather'))
        for k in range(3):
            desk_lamp(R, x0 + (x1 - x0) * (k + 0.5) / 3, 7.0, 0.78)
        for k in range(6):
            xx = x0 + (x1 - x0) * (k + 0.5) / 6
            for (yy, a) in ((5.9, math.pi / 2), (8.1, -math.pi / 2)):
                if (k * 7 + int(yy)) % 5 == 1: continue          # a few chairs missing
                R.parts.add(chair(xx, yy, a)); R.spot('sit', xx, yy, 0.48, a)
    open_book_(R, 9.1, 7.05, 0.78, 0.2)
    book_pile(R, 21.0, 6.8, 0.78, 4, random.Random(8), 0.4)
    # pendant lamps and corner lamps (these stay on at night)
    for x in (6.0, 12.0, 18.0, 24.0):
        pendant(R, x, 7.0, 3.3, H)
    for (x, y) in ((1.4, 1.4), (XE - 1.1, 1.4), (1.4, YN - 1.1), (XE - 1.1, YN - 1.1)):
        floor_lamp(R, x, y, 1.6, m='e_amber')
    # coffers on the ceiling
    for k in range(1, 7):
        x = T + k * (XE - T) / 7
        R.nocol.add(box(x - 0.1, T, H - 0.3, x + 0.1, YN, H, 'ivory'))
    for y in (4.9, 9.4):
        R.nocol.add(box(T, y - 0.1, H - 0.3, XE, y + 0.1, H, 'ivory'))
    # walkers
    navloop(R, [(3.0, 3.0), (16.0, 3.0), (28.0, 3.0), (28.0, 11.0), (16.0, 11.0), (3.0, 11.0)])
    a, b = R.navpt(1.6, 8.0), R.navpt(15.8, 8.2)
    R.link(0, a, 5); R.link(1, b, 4)


def open_book_(R, x, y, z, ang):
    g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, 'leather')
    g.add(box(-0.19, -0.13, 0.02, -0.005, 0.13, 0.05, 'ivory'))
    g.add(box(0.005, -0.13, 0.02, 0.19, 0.13, 0.05, 'ivory'))
    R.nocol.add(g.xform(ang, x, y, z))


# ---------------------------------------------------------------------------
def backs(R, x0, x1, y, z0, z1, face):
    """The backs of the bookcases seen from behind: rough planks and braces."""
    g = Geo()
    n = int((x1 - x0) / 1.2)
    for k in range(n):
        a = x0 + (x1 - x0) * k / n; b = x0 + (x1 - x0) * (k + 1) / n
        g.add(box(a + 0.01, y - 0.02, z0, b - 0.01, y + 0.02, z1, 'wood' if k % 2 else 'oak'))
        g.add(obox(a + 0.1, y + 0.03 * face, b - 0.1, y + 0.03 * face, z0, z0 + 0.08, 0.04, 'walnut').xform(0, 0, 0, 0))
        R.nocol.add(beam((a + 0.1, y + 0.04 * face, z0 + 0.2), (b - 0.1, y + 0.04 * face, min(z1, 3.9) - 0.2), 0.08, 'walnut', 0.03))
    for z in (0.9, 2.1, 3.3):
        g.add(box(x0, y + 0.02 * face - 0.02, z, x1, y + 0.02 * face + 0.02, z + 0.1, 'walnut'))
    R.nocol.add(g)


def pipes_along(R, x0, x1, y, zs, rs, mats, brackets=2.4):
    for z, r, m in zip(zs, rs, mats):
        R.nocol.add(xtube(x0, x1, y, z, r, 10, m))
        n = int((x1 - x0) / brackets)
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / max(n, 1)
            R.nocol.add(box(x - 0.04, y - r - 0.02, z - r - 0.04, x + 0.04, y + r + 0.1, z - r, 'iron'))
            R.nocol.add(cyl(x + 0.3, y, z - r - 0.01, z + r + 0.01, r + 0.025, 10, side='brass', caps=False))


def cable(R, p0, p1, sag, r=0.018, m='black'):
    R.nocol.add(tube(curve(p0, p1, (0, 0, 0), 7, sag), r, 5, m))


def jbox(R, x, y, z, face=-1, w=0.5, h=0.6, m='iron'):
    R.nocol.add(box(x - w / 2, y + (0.0 if face < 0 else -0.18), z, x + w / 2, y + (0.18 if face < 0 else 0.0), z + h, m))
    R.nocol.add(box(x - w / 2 + 0.05, y + (-0.02 if face < 0 else 0.0), z + 0.05, x + w / 2 - 0.05, y + (0.0 if face < 0 else 0.02), z + h - 0.05, 'bronze'))


def passage(R):
    """Behind the north wall: a slot one person wide and the whole height of the building."""
    R.cut(box(CX0, CY0, 0, CX1, CY1, TOP - 0.2, 'tile', bottom='slate', top='plaster'))
    backs(R, CX0, CX1, CY0 + 0.02, 0.0, 6.2, 1)
    # the stone side: pipes, cables, boxes
    pipes_along(R, CX0, CX1, CY1 - 0.14, (2.3, 2.62, 5.4, 6.3), (0.07, 0.05, 0.11, 0.06), ('iron', 'bronze', 'iron', 'rust'))
    for x in (12.9, 17.3, 20.6):
        R.nocol.add(ztube(0.0, TOP - 0.2, x, CY1 - 0.12, 0.06, 10, 'iron'))
        R.nocol.add(cyl(x, CY1 - 0.12, 1.1, 1.14, 0.1, 10, side='brass', top='brass', bottom='brass'))
    R.nocol.add(ztube(0.0, TOP - 0.2, 14.6, CY1 - 0.1, 0.1, 12, 'rust'))
    for (x, z) in ((13.8, 1.3), (16.6, 1.5), (19.4, 1.2)):
        jbox(R, x, CY1, z, -1)
        cable(R, (x, CY1 - 0.12, z), (x + 1.6, CY1 - 0.1, 2.9), 0.4)
    wheel_valve(R, 17.3, CY1 - 0.24, 1.6)
    cable(R, (CX0, CY1 - 0.1, 3.4), (CX1, CY1 - 0.1, 3.3), 0.6)
    cable(R, (CX0, CY1 - 0.08, 3.6), (CX1, CY1 - 0.08, 3.7), 0.9, 0.025, 'iron')
    # the bed, a crate with a candle, a rug, some books, a mug
    cot(R, CX0 + 0.1, CY1 - 0.9, CX0 + 2.1, CY1 - 0.04, 0.0, h=0.4, frame='iron', blanket='green', pillow='bed')
    rug(R, CX0 + 2.4, CY0 + 0.1, CX1 - 3.2, CY1 - 0.1, m='velvet', border='oxblood')
    R.parts.add(box(CX0 + 2.2, CY1 - 0.6, 0, CX0 + 2.75, CY1 - 0.08, 0.5, 'oak'))
    R.nocol.add(box(CX0 + 2.2, CY1 - 0.62, 0.06, CX0 + 2.75, CY1 - 0.58, 0.14, 'walnut'))
    candle(R, CX0 + 2.5, CY1 - 0.35, 0.5, h=0.12, r=0.025)
    rnd = random.Random(11)
    book_pile(R, CX0 + 2.35, CY1 - 0.4, 0.5, 3, rnd, 0.3)
    R.nocol.add(cyl(CX0 + 2.62, CY1 - 0.2, 0.5, 0.6, 0.04, 8, side='ivory', top='ivory', bottom='ivory'))
    for (x, n) in ((13.2, 9), (13.5, 6), (18.2, 11), (18.5, 5)):
        book_pile(R, x, CY0 + 0.3, 0.0, n, rnd, rnd.uniform(0, 3))
    # a line of books along a board on the stone, over the bed
    shelf(R, CX0 + 0.1 + 3.6, CY1, 1.3, 3.6, '-y', rows=2, frame='oak', depth=0.22, sides=False, crown=False)
    # lamps: bare bulbs on flex, far apart
    for (x, m) in ((12.2, 'e_dim'), (16.0, 'e_dim'), (20.0, 'e_dim')):
        bulb(R, x, (CY0 + CY1) / 2, 3.0, r=0.07, m=m, top=TOP - 0.2)
    # the ladder at the east end, up to the catwalk
    L = UZ / math.tan(math.radians(60))
    ladder_up(R, CX1 - L, (CY0 + CY1) / 2, 0.0, UZ, '+x', w=0.62, m='iron', rail='iron')
    ym = (CY0 + CY1) / 2
    rail(R, CX1 + 0.05, CY0 + 0.02, CX1 + 0.05, ym - 0.42, UZ, m='iron')
    rail(R, CX1 + 0.05, ym + 0.42, CX1 + 0.05, CY1 - 0.02, UZ, m='iron')
    a, b = R.navpt(CX0 + 3.0, ym), R.navpt(CX1 - L - 0.8, ym)
    R.link(a, b)


def wheel_valve(R, x, y, z, r=0.2):
    g = Geo()
    n = 10
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        g.add(beam((x + r * math.cos(a0), y, z + r * math.sin(a0)), (x + r * math.cos(a1), y, z + r * math.sin(a1)), 0.03, 'brass'))
    for k in range(3):
        a = math.pi * k / 3
        g.add(beam((x - r * math.cos(a), y, z - r * math.sin(a)), (x + r * math.cos(a), y, z + r * math.sin(a)), 0.02, 'brass'))
    R.nocol.add(g)


def catwalk(R):
    """Over the doorway, inside the east wall: an iron catwalk to a stool at a slit."""
    R.cut(box(CX1 - 0.02, CY0, UZ, EX1, CY1, TOP - 0.2, 'tile', bottom='iron', top='plaster'))
    R.cut(box(EX0, EY0, UZ, EX1, CY1, TOP - 0.2, 'tile', bottom='iron', top='plaster'))
    # grating bars on the floor
    for k in range(int((EX1 - CX1) / 0.5)):
        x = CX1 + 0.25 + k * 0.5
        R.nocol.add(box(x - 0.02, CY0, UZ, x + 0.02, CY1, UZ + 0.015, 'rust'))
    for k in range(int((CY0 - EY0) / 0.5)):
        y = EY0 + 0.25 + k * 0.5
        R.nocol.add(box(EX0, y - 0.02, UZ, EX1, y + 0.02, UZ + 0.015, 'rust'))
    backs(R, CX1 + 0.05, EX0 - 0.05, CY0 + 0.02, UZ, TOP - 0.2, 1)
    pipes_along(R, CX1, EX1, CY1 - 0.14, (UZ + 1.1, UZ + 2.4), (0.08, 0.06), ('iron', 'bronze'))
    g = Geo()
    for (z, r, m) in ((UZ + 2.0, 0.08, 'iron'), (UZ + 2.35, 0.05, 'rust')):
        g.add(ytube(EY0, CY1 - 0.2, EX1 - 0.14, z, r, 10, m))
    R.nocol.add(g)
    cable(R, (EX1 - 0.1, EY0, UZ + 2.6), (EX1 - 0.1, CY0, UZ + 2.5), 0.7)
    cable(R, (CX1, CY1 - 0.1, UZ + 2.7), (EX1 - 0.1, CY1 - 0.1, UZ + 2.6), 0.5)
    # narrow shelves on the outer wall, stuffed
    shelf(R, EX1, 3.3, UZ, 9.6, '-x', rows=5, frame='oak', depth=0.22)
    # the slit into the reading room, at lamp height
    R.cut(box(XE - 0.05, 1.8, UZ + 0.9, EX0 + 0.05, 3.4, UZ + 1.15, 'wood', bottom='wood', top='wood'))
    # the stool, a crate with a notebook and a candle
    R.parts.add(cyl(30.55, 2.3, UZ, UZ + 0.55, 0.18, 10, side='oak', top='oak', bottom='oak'))
    R.spot('sit', 30.55, 2.3, UZ + 0.55, math.pi)
    R.parts.add(box(30.6, EY0 + 0.05, UZ, 31.4, EY0 + 0.75, UZ + 0.6, 'oak'))
    open_book_(R, 31.0, EY0 + 0.4, UZ + 0.6, 1.4)
    candle(R, 31.25, EY0 + 0.15, UZ + 0.6, h=0.1, r=0.025)
    bulb(R, 30.75, 8.0, UZ + 2.0, r=0.06, m='e_dim', top=TOP - 0.2)
    bulb(R, 26.5, (CY0 + CY1) / 2, UZ + 2.0, r=0.06, m='e_dim', top=TOP - 0.2)
    a, b, c = R.navpt(CX1 + 0.8, (CY0 + CY1) / 2, UZ), R.navpt(30.75, 14.75, UZ), R.navpt(30.75, 3.2, UZ)
    R.link(a, b, c)
