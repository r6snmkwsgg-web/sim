"""The Dumbwaiters: one wall of this room is hatches, dozens of them, little cupboards with their shutters
open, a shelf of books and sometimes a lamp in each. Four at the bottom are bigger: dumbwaiter cars, big
enough to crouch in, that rise four metres to the gallery and come down again. A stair goes up too. One
car goes somewhere else; and so does one of the hatches on the gallery."""
from kit_h12 import *

W = D = 16.0
FY = 11.0                    # the face of the hatch wall
SY0, SY1 = 11.3, 12.7        # the shafts
LIFTS = (2.0, 4.4, 11.4, 13.8)
HW = 0.62                    # cars' half width
CF = 0.3                     # a car's floor top, at rest
GZ = 4.4                     # the gallery
GY = 9.2                     # its edge
RX0, RX1, RY0, RY1 = 10.0, 15.5, 13.0, 15.3    # the room behind


def make():
    R = Room('dumbwaiters', 1, 1, res=1024)
    rs = rng(59)
    R.sockets(floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, FY - 0.3, TOP, 'tile', bottom='floor', top='plaster'))
    tunnels(R, T, T, W - T, FY, floor='floor', wall='tile')
    gallery(R)
    hatches(R, rs)
    for k, x in enumerate(LIFTS):
        lift(R, x, k, rs)
    hidden(R, rs)
    furnish(R, rs)
    ids = navgrid(R, {'a': (3.0, 3.0), 'b': (8.0, 3.0), 'c': (13.5, 3.0), 'd': (13.5, 8.0), 'e': (8.0, 8.5), 'f': (3.0, 8.0),
                      's': (8.0, 1.2), 'w': (1.2, 8.0), 'x': (14.8, 8.0), 'n': (8.0, 13.0), 'g': (11.0, 2.2)},
                     [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'a'), ('b', 's'), ('f', 'w'), ('d', 'x'), ('e', 'n')])
    secret(R, 12.6, 14.2, GZ, 'The Operator\'s Room',
           'Behind the hatches, over the room, a cramped attic where somebody sat at the top of the shafts and sent things down. The last request is still clipped to the board.', r=1.8)
    return finish(R, 'The Dumbwaiters', weight=4, probe=(8.0, 5.0, 2.2),
                  blurb='A wall of little doors, all open, all with books inside. Some of them are going up and down. You get the feeling they are being sent somewhere, and that you could be too.')


def gallery(R):
    R.parts.add(box(T, GY, GZ - 0.3, W - T, FY + 0.02, GZ, 'walnut', top='floor', bottom='plaster'))
    R.parts.add(box(T, GY - 0.12, GZ - 0.42, W - T, GY + 0.02, GZ - 0.3, 'walnut'))
    for (a, b) in ((T, 10.4), (11.6, W - T)):
        brass_rail(R, a, GY + 0.06, b, GY + 0.06, GZ, h=0.95)
    for x in (T + 0.1, 3.2, 5.7, 10.3, 12.6, W - T - 0.1):
        if abs(x - 10.3) < 0.01: continue
        R.parts.add(box(x - 0.1, GY + 0.05, 0, x + 0.1, GY + 0.25, GZ - 0.3, 'walnut', skip=('-z',)))
    # the stair up: a ribbon flight along x 10.4..11.6, from y 2.8
    n, rise, run = 22, GZ / 22, 0.3
    rflight(R, 10.4, GY - n * run, 0.0, 1.2, n, rise, run, '+y', m='oak', riser='walnut', side='walnut', soffit='walnut')
    for xx in (10.42, 11.58):
        stair_rail(R, xx, GY - n * run, rise, xx, GY, GZ)


def hatches(R, rs):
    """The little cupboards over the whole wall face in a grid: most open (a shelf of books, a lamp in some),
    a few shut; over the shafts only their doors (shut)."""
    R.cut(box(T - 0.02, FY - 0.6, 0, W - T + 0.02, FY, TOP, 'walnut', bottom='floor', top='plaster'))
    k = 0
    for i in range(19):
        x = 0.75 + i * 0.8
        for z in (0.45, 1.4, 2.35, 3.3, 4.75, 5.7, 6.65):
            w, h = 0.6, 0.7
            if z < 4.2 and 6.2 < x < 9.8: continue                       # the north doorway
            if 14.5 < x + w / 2 and x - w / 2 < 15.7 and GZ - 0.1 < z < GZ + 1.4: continue   # the crawl hatch
            lift_hatch = any(abs(x - lx) < 0.55 + w / 2 and ((z < 1.7) or (GZ - 0.2 < z < GZ + 1.4)) for lx in LIFTS)
            if lift_hatch: continue
            over_shaft = any(abs(x - lx) < 0.75 + w / 2 for lx in LIFTS)
            if over_shaft or rs.random() < 0.18:
                shut(R, x, z, w, h, rs)
            else:
                hatch(R, x, z, rs, w=w, h=h, lamp=(k % 3 == 0))
                k += 1


def shut(R, x, z, w, h, rs):
    """A closed hatch: two little doors flush on the wall, a brass pull."""
    for s in (-1, 1):
        a, b = (x - w / 2, x) if s < 0 else (x, x + w / 2)
        R.nocol.add(box(a + 0.01, FY - 0.03, z, b - 0.01, FY + 0.04, z + h, 'walnut', top='walnut'))
        R.nocol.add(box(a + 0.06, FY - 0.045, z + 0.08, b - 0.06, FY - 0.03, z + h - 0.08, 'oak'))
    R.nocol.add(box(x - 0.03, FY - 0.07, z + h * 0.45, x + 0.03, FY - 0.03, z + h * 0.55, 'brass'))


def hatch(R, x, z, rs, w=0.7, h=0.75, depth=0.45, lamp=False, cut=True):
    if cut: R.cut(box(x - w / 2, FY - 0.02, z, x + w / 2, FY + depth, z + h, 'walnut', bottom='oak', top='walnut'))
    kshelf(R, x + w / 2 - 0.02, FY + depth - 0.02, z, w - 0.04, '-y', rows=1, row_h=min(0.42, h - 0.05), depth=depth - 0.08,
           frame='oak', sides=False, crown=False, back=False)
    R.nocol.add(frame_rect('y', FY, x - w / 2, x + w / 2, z, z + h, -1, w=0.05, d=0.04, m='walnut'))
    for s in (-1, 1):
        a = s * rs.uniform(1.2, 1.9)
        hx = x + s * (w / 2 + 0.03)
        leaf = box(0, -0.015, 0, w / 2 - 0.02, 0.015, h - 0.04, 'walnut')
        leaf.add(box(0.05, -0.03, 0.08, w / 2 - 0.07, -0.015, h - 0.12, 'oak'))
        th = -abs(a) if s > 0 else math.pi + abs(a)
        R.nocol.add(leaf.xform(th, hx, FY - 0.03, z + 0.02))
    R.light(box(x - w / 2 + 0.06, FY + depth - 0.12, z + h - 0.03, x + w / 2 - 0.06, FY + depth - 0.06, z + h - 0.01, 'e_dim'))
    if lamp:
        R.nocol.add(frustum(x, FY + depth * 0.5, z + h - 0.16, z + h - 0.08, 0.07, 0.03, 8, 'green', inner='ivory'))
        R.light(sphere(x, FY + depth * 0.5, z + h - 0.15, 0.03, 6, 3, 'e_lamp'))


def lift(R, x, k, rs):
    """A dumbwaiter: its shaft behind the wall, a hatch at the bottom and one at the gallery, a car that
    goes up and down between them. The fourth one's upper hatch opens on the far side, into the room."""
    to_room = (k == 3)
    R.cut(box(x - 0.7, SY0, 0, x + 0.7, SY1, 7.3, 'oak', bottom='floor', top='walnut'))
    R.cut(box(x - 0.55, FY - 0.02, 0, x + 0.55, SY0 + 0.02, 1.62, 'walnut', bottom='floor', top='walnut'))
    if to_room:
        R.cut(box(x - 0.55, SY1 - 0.02, GZ, x + 0.55, RY0 + 0.02, GZ + 1.35, 'walnut', bottom='floor', top='walnut'))
    else:
        R.cut(box(x - 0.55, FY - 0.02, GZ, x + 0.55, SY0 + 0.02, GZ + 1.35, 'walnut', bottom='floor', top='walnut'))
    # brass surrounds and a number plate on both hatches
    for z0, z1 in ((0.0, 1.62), (GZ, GZ + 1.35)):
        if to_room and z0 > 0: continue
        R.nocol.add(frame_rect('y', FY, x - 0.55, x + 0.55, z0, z1, -1, w=0.08, d=0.05, m='brass'))
        R.nocol.add(box(x - 0.14, FY - 0.06, z1 + 0.12, x + 0.14, FY - 0.03, z1 + 0.3, 'ivory'))
    # a pulley at the top of the shaft
    R.nocol.add(wheel(x, (SY0 + SY1) / 2, 6.9, 0.3, axis='x', spokes=5, rim=0.05, w=0.06, m='iron', hub='brass', segs=14))
    # the car
    P, pa = 14.0, 3.0
    M = R.mover('slide', delta=(0, 0, GZ - CF), period=P, pause=pa, phase=0.13 + 0.27 * k)
    y0, y1 = SY0 + 0.04, SY1 - 0.04
    M.parts.add(box(x - HW, y0, CF - 0.12, x + HW, y1, CF, 'oak', sides='brass', bottom='iron'))
    for s in (-1, 1):
        M.parts.add(box(x + s * HW - (0.05 if s > 0 else 0), y0, CF, x + s * HW + (0.05 if s < 0 else 0), y1, CF + 0.9, 'walnut'))
    if not to_room:
        M.parts.add(box(x - HW, y1 - 0.05, CF, x + HW, y1, CF + 0.9, 'walnut'))
        g = Geo(); book_row_geo(g, rs, x - HW + 0.08, x + HW - 0.08, y1 - 0.05, CF + 0.5, depth=0.18, face=-1)
        g.add(box(x - HW, y1 - 0.25, CF + 0.48, x + HW, y1 - 0.05, CF + 0.5, 'oak'))
        M.nocol.add(g)
    # a brass frame over it, and hooks for the (cut) rope
    for s in (-1, 1):
        M.nocol.add(box(x + s * (HW - 0.03) - 0.02, (y0 + y1) / 2 - 0.02, CF + 0.9, x + s * (HW - 0.03) + 0.02, (y0 + y1) / 2 + 0.02, CF + 1.3, 'brass'))
    M.nocol.add(box(x - HW, (y0 + y1) / 2 - 0.03, CF + 1.3, x + HW, (y0 + y1) / 2 + 0.03, CF + 1.36, 'brass'))
    M.nocol.add(box(x - 0.02, (y0 + y1) / 2 - 0.02, CF + 1.36, x + 0.02, (y0 + y1) / 2 + 0.02, CF + 1.9, 'iron'))


def hidden(R, rs):
    """The operator's attic behind the hatch wall at gallery height: reached by the fourth car, or by the
    hatch at the east end of the gallery, which has no back."""
    R.cut(box(RX0, RY0, GZ, RX1, RY1, 7.2, 'plaster', bottom='floor', top='plaster'))
    # the crawlway from the gallery hatch (x 14.75..15.45), a hatch like the others but open to the floor
    R.cut(box(14.65, FY - 0.02, GZ, 15.55, RY0 + 0.02, GZ + 1.25, 'walnut', bottom='floor', top='walnut'))
    R.nocol.add(frame_rect('y', FY, 14.65, 15.55, GZ, GZ + 1.25, -1, w=0.06, d=0.04, m='walnut'))
    for s in (-1, 1):
        leaf = box(0, -0.015, 0, 0.38, 0.015, 1.2, 'walnut')
        leaf.add(box(0.05, -0.03, 0.08, 0.33, -0.015, 1.1, 'oak'))
        th = -1.5 if s > 0 else math.pi + 1.5
        R.nocol.add(leaf.xform(th, 15.1 + s * 0.47, FY - 0.03, GZ + 0.02))
    # inside: a stool at a board of pigeonholes, speaking tubes, a ledger, a cot
    R.parts.add(box(RX0 + 0.1, RY1 - 0.5, GZ, RX0 + 3.2, RY1 - 0.05, GZ + 0.9, 'walnut', top='leather'))
    for i in range(10):
        for j in range(3):
            xx = RX0 + 0.25 + i * 0.29
            R.nocol.add(box(xx, RY1 - 0.3, GZ + 1.1 + j * 0.3, xx + 0.26, RY1 - 0.05, GZ + 1.12 + j * 0.3, 'oak'))
            if rs.random() < 0.6:
                R.nocol.add(box(xx + 0.03, RY1 - 0.25, GZ + 1.12 + j * 0.3, xx + 0.23, RY1 - 0.08, GZ + 1.12 + j * 0.3 + 0.2, rs.choice(BOOKC)))
    R.parts.add(stool(11.6, RY1 - 1.0, math.pi / 2, back=True))
    for xx in (10.6, 11.0, 11.4):
        R.nocol.add(solid_tube((xx, RY1 - 0.1, GZ + 0.9), (xx, RY1 - 0.1, 7.2), 0.04, 'brass', 8))
        R.nocol.add(cyl(xx, RY1 - 0.1, GZ + 0.9, GZ + 1.0, 0.07, 8, side='brass', top='black'))
    open_book(R, 12.2, RY1 - 0.3, GZ + 0.9, math.pi / 2)
    R.parts.add(box(13.4, RY1 - 0.8, GZ, RX1 - 0.05, RY1 - 0.05, GZ + 0.4, 'walnut', top='bed'))
    R.spot('bed', 14.3, RY1 - 0.42, GZ + 0.4, 0.0)
    R.light(sphere(12.4, 14.1, 6.6, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(cyl(12.4, 14.1, 6.66, 7.2, 0.01, 4, side='iron', caps=False))
    R.spot('plaque', 12.0, RY1 - 0.4, GZ, math.pi / 2,
           text='Clipped to the board, the last request: SEND UP THE BOOK WITH MY NAME IN IT. Under it, in another hand: WHICH ONE.')


def furnish(R, rs):
    """A sorting table, book trolleys, lamps."""
    reading_table(R, 2.6, 4.0, 7.4, 5.0, lamps=2, chairs=True)
    for (x, y, a) in ((4.0, 8.9, 0.0), (13.0, 4.6, 0.4)):
        trolley(R, x, y, a, rs)
    for x in (3.0, 8.0, 13.0):
        pendant(R, x, 6.5, 3.6, TOP - 0.1, r=0.22)
    for x in (3.0, 8.0, 13.0):
        R.light(sphere(x, 10.0, GZ + 2.2, 0.06, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, 10.0, GZ + 2.26, TOP - 0.1, 0.01, 4, side='iron', caps=False))
    sh(R, '+y', T, 0.8, 6.2, rows=10, frame='walnut')
    sh(R, '+y', T, 9.8, 15.2, rows=10, frame='walnut')
    sh(R, '+x', T, 0.8, 6.2, rows=8, frame='walnut')
    sh(R, '-x', W - T, 0.8, 6.2, rows=8, frame='walnut')
    # an upper tier over the cornice, never reached
    for (a, b) in ((0.8, 6.2), (9.8, 15.2)):
        sh(R, '+y', T, a, b, z=4.6, rows=6, frame='walnut')
    sh(R, '+x', T, 0.8, 8.8, z=4.6, rows=6, frame='walnut')
    sh(R, '-x', W - T, 0.8, 8.8, z=4.6, rows=6, frame='walnut')
    for (x0, y0, x1, y1) in ((T, T, W - T, T + 0.45), (T, T, T + 0.45, GY), (W - T - 0.45, T, W - T, GY)):
        R.parts.add(box(x0, y0, 4.35, x1, y1, 4.5, 'walnut'))
    # a laylight over the middle of the room
    R.cut(box(4.0, 3.0, TOP - 0.25, 12.0, 8.0, TOP + 0.2, 'plaster'))
    R.light(box(4.0, 3.0, TOP + 0.1, 12.0, 8.0, TOP + 0.12, 'e_sky'))
    for x in (6.0, 8.0, 10.0):
        R.nocol.add(box(x - 0.04, 3.0, TOP - 0.2, x + 0.04, 8.0, TOP + 0.1, 'iron'))
    for y in (4.66, 6.33):
        R.nocol.add(box(4.0, y - 0.04, TOP - 0.2, 12.0, y + 0.04, TOP + 0.1, 'iron'))


def trolley(R, x, y, a, rs):
    g = Geo()
    g.add(box(-0.45, -0.22, 0.25, 0.45, 0.22, 0.28, 'walnut'))
    g.add(box(-0.45, -0.22, 0.75, 0.45, 0.22, 0.78, 'walnut'))
    for (px, py) in ((-0.42, -0.19), (0.42, -0.19), (0.42, 0.19), (-0.42, 0.19)):
        g.add(box(px - 0.02, py - 0.02, 0.08, px + 0.02, py + 0.02, 0.95, 'brass'))
        g.add(cyl(px, py, 0, 0.08, 0.05, 6, side='iron', top='iron'))
    book_row_geo(g, rs, -0.4, 0.4, -0.1, 0.78, depth=0.2)
    book_row_geo(g, rs, -0.4, 0.4, -0.1, 0.28, depth=0.2)
    R.parts.add(g.xform(a, x, y, 0))
