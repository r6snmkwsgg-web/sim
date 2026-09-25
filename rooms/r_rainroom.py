"""The Rain Room: a grand vaulted reading room where it always rains. The nave has no roof over its
crown, only a long slot of storm sky; the marble floor is wet and pooled, the books on the tables sit
under brass bells. At the north end a gutter has broken, and behind the water it pours is a dry room."""
from kit_h3 import *

W = D = 32.0
NX0, NX1 = 10.3, 21.7          # the nave
AX0, AX1 = 9.7, 22.3           # the aisles' inner walls
NY1 = 27.0                     # the nave's north end wall (the dry room is behind it)
AH = 5.0                       # aisle ceiling
JAMB, RISE = 4.6, 2.8          # the vault
DX0, DX1 = 17.9, 19.1          # the doorway behind the waterfall


def make():
    R = Room('rainroom', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    # aisles, full length
    R.cut(box(T - 0.02, T - 0.02, 0, AX0, D - T + 0.02, AH, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(AX1, T - 0.02, 0, W - T + 0.02, D - T + 0.02, AH, 'tile', bottom='terrazzo', top='plaster'))
    # the nave: a segmental barrel vault, open at the crown to the sky
    pr = arch_profile(16, NX1 - NX0, 0, JAMB, 32, rise=RISE)
    R.cut(prism(pr, 'y', T - 0.02, NY1, arch_mats(len(pr), 'terrazzo', 'plaster')))
    R.cut(box(14.4, T - 0.02, 7.0, 17.6, NY1, TOP - 0.02, 'tile', top='plaster'))
    R.light(box(14.4, T, TOP - 0.06, 17.6, NY1, TOP - 0.04, 'e_skydome', skip=('+z',)))
    for x in (14.4, 17.6):
        R.nocol.add(box(x - 0.08, T, 6.95, x + 0.08, NY1, 7.1, 'iron'))
    for k in range(12):
        y = T + 0.8 + k * (NY1 - T - 1.6) / 11
        R.nocol.add(box(14.4, y - 0.05, 7.2, 17.6, y + 0.05, 7.3, 'iron'))
    arcade(R)
    nave(R)
    aisles(R)
    dry_room(R)
    fx(R, 'rain', [NX0, T, 0, NX1, NY1, TOP])
    fx(R, 'rain', [DX0 - 0.3, NY1 - 0.5, 0, DX1 + 0.3, NY1 - 0.05, 5.2], density=3.0)
    # walking graph
    nv = navloop(R, [(16, 2.2), (20.5, 6), (20.5, 16), (20.5, 24.8), (16, 25.2), (11.5, 24.8), (11.5, 16), (11.5, 6)])
    wa = navloop(R, [(7.5, 2.0), (7.5, 11), (7.5, 21), (7.5, 30.0), (2.0, 30.0), (2.0, 24), (2.0, 8), (2.0, 2.0)])
    ea = navloop(R, [(24.5, 2.0), (24.5, 11), (24.5, 21), (24.5, 30.0), (30.0, 30.0), (30.0, 24), (30.0, 8), (30.0, 2.0)])
    R.link(wa[1], nv[7]); R.link(ea[1], nv[1]); R.link(wa[2], nv[6]); R.link(ea[2], nv[2])
    secret(R, 16.0, 29.5, 0.0, 'The Dry Room',
           'Behind the water it is perfectly dry: dust on the shelves, a warm lamp, a towel folded on the chair. Somebody has been waiting out the weather for a long time.')
    return finish(R, 'The Rain Room', weight=4, probe=(16, 14, 2.2),
                  blurb='It is raining in the reading room. It has always been raining in the reading room. The books have been put under glass, and nobody has thought to do anything else.')


def arcade(R):
    """Arches between nave and aisles, piers with pilasters, ribs over the vault."""
    for yc in (3.2, 7.2, 11.2, 15.2, 19.2, 23.2):
        for x0, x1 in ((AX0 - 0.1, NX0 + 0.1), (NX1 - 0.1, AX1 + 0.1)):
            arch_hole(R, 'x', yc, x0, x1, 3.0, 2.9, floor='terrazzo', wall='tile')
    for yp in (1.2, 5.2, 9.2, 13.2, 17.2, 21.2, 25.2):
        for x, s in ((NX0, 1), (NX1, -1)):
            # a pilaster on the nave face, up to the springing, and a rib over the vault
            R.parts.add(box(x - 0.02 if s > 0 else x - 0.28, yp - 0.35, 0, x + 0.28 if s > 0 else x + 0.02, yp + 0.35, JAMB, 'tile', skip=('-z',)))
            R.parts.add(box(x - 0.02 if s > 0 else x - 0.4, yp - 0.45, JAMB - 0.3, x + 0.4 if s > 0 else x + 0.02, yp + 0.45, JAMB, 'tile'))
        R.nocol.add(prism(arc_band(16, NX1 - NX0, JAMB, RISE, 0.0, 0.3, 32), 'y', yp - 0.3, yp + 0.3, 'tile', cap='tile'))
    # the stone gutters along the springing, where the vault meets the walls
    for x0, x1 in ((NX0, NX0 + 0.45), (NX1 - 0.45, NX1)):
        R.parts.add(box(x0, T, JAMB - 0.05, x1, NY1, JAMB + 0.25, 'tile'))
    # a gutter across the north end wall; broken over the dry room's doorway, pouring
    R.parts.add(box(NX0, NY1 - 0.45, 5.0, DX0 - 0.3, NY1, 5.3, 'tile'))
    R.parts.add(box(DX1 + 0.5, NY1 - 0.45, 5.0, NX1, NY1, 5.3, 'tile'))
    g = box(0, -0.45, 0, 0.9, 0, 0.3, 'tile'); rot(g, 'y', 0.5); g.xform(0, DX1 + 0.4, NY1, 4.6)
    R.nocol.add(g)                 # the broken end, hanging
    strands(R, DX0 - 0.25, NY1 - 0.32, DX1 + 0.3, NY1 - 0.32, 0.0, 5.05, 70, seed=3)
    strands(R, DX0 - 0.1, NY1 - 0.2, DX1 + 0.2, NY1 - 0.2, 0.0, 5.05, 40, seed=4, w=0.02)
    R.nocol.add(box(DX0 - 0.35, NY1 - 0.5, 4.95, DX1 + 0.45, NY1 - 0.05, 5.02, 'chrome'))


def nave(R):
    # the far end wall: bookcases either side of the pour, a tall window of storm above them
    sh(R, '-y', NY1, NX0 + 0.5, DX0 - 0.6, rows=10, frame='walnut')
    sh(R, '-y', NY1, DX1 + 0.6, NX1 - 0.5, rows=10, frame='walnut')
    window(R, 'N', 16, 5.4, 3.4, 0.4, wallpos=NY1, depth=0.3, em='e_skydome', mull=2, trans=0)
    # the south end wall: books and a clock of a window
    sh(R, '+y', T, NX0 + 0.5, NX1 - 0.5, rows=10, frame='walnut')
    # puddles in the marble (5 cm of water) and one under the pour
    pools = [(15.2, 5.0, 1.3), (17.2, 10.6, 1.8), (14.6, 15.8, 1.1), (16.9, 20.8, 1.5)]
    for (cx, cy, r) in pools:
        R.cut(cyl(cx, cy, -0.05, 0.3, r, 28, side='terrazzo', top='tile', bottom='terrazzo'))
        R.water.append(dict(cx=cx, cy=cy, r=r, top=-0.005, bot=-0.05))
    R.cut(box(DX0 - 0.6, NY1 - 1.5, -0.06, DX1 + 0.7, NY1 + 0.02, 0.3, 'terrazzo', top='tile'))
    R.water.append(dict(x0=DX0 - 0.6, y0=NY1 - 1.5, x1=DX1 + 0.7, y1=NY1, top=-0.005, bot=-0.06))
    # two rows of reading tables down the nave, every book under a bell
    k = 0
    for (tx0, tx1) in ((11.7, 12.9), (19.1, 20.3)):
        for y0 in (2.6, 7.4, 12.2, 17.0, 21.8):
            reading_table(R, tx0, y0, tx1, y0 + 3.2, lamps=2)
            for t in (0.25, 0.75):
                bell_jar(R, (tx0 + tx1) / 2, y0 + 3.2 * t, 0.78, book=('oxblood', 'green', 'leather')[k % 3]); k += 1
    # lamps hung from the ribs, low over the tables
    for yp in (5.2, 13.2, 21.2):
        for x in (12.3, 19.7):
            pendant(R, x, yp, 3.4, 7.0)
    for y in (1.6, NY1 - 0.9):
        pass


def aisles(R):
    """Side aisles under a flat ceiling: stacks out from the walls, books on the arcade piers."""
    rows = 11
    for (wx, dirn, sx0, sx1) in ((T, '+x', T + 0.4, 6.0), (W - T, '-x', 26.0, W - T - 0.4)):
        # wall cases between the doorways
        for (a, b) in ((0.6, 5.6), (10.4, 21.6), (26.4, D - 0.6)):
            sh(R, dirn, wx, a, b, rows=rows, frame='walnut')
        # stacks at right angles to the wall
        for yc in (12.2, 14.9, 17.6):
            stack(R, 'x', yc, sx0, sx1, rows=rows, frame='walnut')
        for yc in (2.4, D - 2.4):
            stack(R, 'x', yc, sx0 + 0.6, sx1 - 0.6, rows=7, frame='walnut')
    # a carrel under each arch on the aisle side, and lamps
    for yc in (7.2, 23.2):
        for (xx, a) in ((8.6, 0.0), (23.4, math.pi)):
            c = chair(xx - 0.6 * math.cos(a), yc, a); R.parts.add(c)
    for x in (4.6, 27.4):
        for y in (4.2, 11.0, 21.0, 27.8):
            pendant(R, x if y not in (11.0, 21.0) else (7.4 if x < 16 else 24.6), y, 3.2, AH, r=0.2)
    for (x, y) in ((1.2, 10.6), (W - 1.2, 21.4), (1.2, 26.0), (W - 1.2, 5.8)):
        R.nocol.add(cyl(x, y, 0, 1.3, 0.02, 6, side='brass', caps=False))
        R.light(sphere(x, y, 1.4, 0.1, 10, 5, 'e_amber'))
    # books piled in the south corners of the aisles, a few left out in the rain
    for (x, y, n, s) in ((8.9, 1.6, 7, 1), (23.1, 1.6, 5, 2), (13.5, 26.0, 6, 3)):
        book_pile(R, x, y, 0, n, seed=s)


def dry_room(R):
    """Behind the north end wall, reached only through the pour."""
    y0, y1 = NY1 + 0.6, D - T - 0.02
    R.cut(box(11.2, y0, 0, 20.8, y1, 3.3, 'damask', bottom='floor', top='plaster'))
    R.cut(box(DX0, NY1 - 0.05, 0, DX1, y0 + 0.05, 2.3, 'tile', bottom='floor', top='tile'))
    sh(R, '-y', y1, 11.4, 20.6, rows=7, frame='oak')
    sh(R, '+x', 11.2, y0 + 0.1, y1 - 0.1, rows=7, frame='oak')
    R.parts.add(box(11.9, y0 + 0.9, 0, 15.7, y1 - 0.6, 0.01, 'carpet'))
    armchair(R, 13.0, 29.4, 0.0)
    R.parts.add(box(12.75, 29.15, 0.42, 13.25, 29.65, 0.5, 'bed'))      # the towel
    R.parts.add(table(14.0, 28.8, 14.9, 30.0, 0.62, 'walnut'))
    open_book(R, 14.45, 29.4, 0.62, 0.2)
    floor_lamp(R, 12.1, 30.6, 1.6)
    R.parts.add(box(19.4, y0 + 0.3, 0, 20.6, y0 + 1.6, 0.9, 'walnut'))  # a chest of dry books
    book_pile(R, 20.0, y0 + 1.0, 0.9, 6, seed=9)
    R.light(sphere(19.9, y1 - 0.4, 2.2, 0.06, 8, 4, 'e_candle'))
    bulb(R, 16.8, 29.6, 2.6, r=0.1, m='e_dim', top=3.3)
    R.spot('read', 14.45, 29.4, 0.62, 0.0)
    R.spot('plaque', 16.0, y1 - 0.05, 1.5, -math.pi / 2, text='WET BOOKS WILL NOT BE ACCEPTED')
    a, b = R.navpt(18.5, 26.2), R.navpt(18.5, 28.6)
    R.link(a, b)
