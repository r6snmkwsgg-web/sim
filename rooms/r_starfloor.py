"""The Star Floor: a long reading room whose floor is glass, and under the glass is the night sky, a long
way down (a box of painted sky under the room; the game draws the stars). The tables, lamps and chairs
stand on it calmly. In the south-east one pane is a hatch standing open: a ladder goes down to a little
railed deck hanging under the glass, among the stars, with a chair and a telescope pointing down."""
from kit_h7 import *

W = D = 32.0
GX0, GY0, GX1, GY1 = 3.0, 3.0, 29.0, 29.0       # the glass
ZS = -3.8                                        # the sky under it
PZ = -2.1                                        # the deck hung under the glass
HX0, HX1, HY0, HY1 = 25.7, 26.55, 5.6, 7.35      # the hatch (the ladder climbs +y through it)
LXC = 26.125                                     # the ladder's centre line
DX0, DX1, DY0, DY1 = 23.2, 28.6, 3.4, 8.2        # the deck


def make():
    R = Room('starfloor', 2, 2, res=2048, lo=-4.0)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(GX0, GY0, ZS, GX1, GY1, 0.02, 'black', bottom='black', top='black'))
    glass(R)
    furniture(R)
    walls(R)
    deck(R)
    fx(R, 'starfloor', [GX0, GY0, ZS, GX1, GY1, 0.0])
    navloop(R, [(1.9, 1.9), (16, 1.9), (30.1, 1.9), (30.1, 16), (30.1, 30.1), (16, 30.1), (1.9, 30.1), (1.9, 16)])
    navloop(R, [(16, 4.5), (19.5, 10), (19.5, 22), (16, 27.5), (12.5, 22), (12.5, 10)])
    R.link(1, 8); R.link(5, 11)
    return finish(R, 'The Star Floor', weight=3, probe=(16, 16, 1.8),
                  blurb='The floor is glass, and under the glass is the night sky, a very long way down. The readers do not look at it. You try not to either.')


def glass(R):
    """Invisible glass to walk on, brass glazing bars, and sky on every face of the box below."""
    # the glass itself: a collider, with the hatch left open
    for (x0, y0, x1, y1) in ((GX0, GY0, GX1, HY0), (GX0, HY1, GX1, GY1), (GX0, HY0, HX0, HY1), (HX1, HY0, GX1, HY1)):
        R.col.add(box(x0, y0, -0.06, x1, y1, 0.0, 'tile'))
    n = 10
    for k in range(n + 1):
        p = GX0 + (GX1 - GX0) * k / n
        R.nocol.add(box(p - 0.035, GY0, -0.05, p + 0.035, GY1, 0.004, 'brass'))
        q = GY0 + (GY1 - GY0) * k / n
        R.nocol.add(box(GX0, q - 0.035, -0.05, GX1, q + 0.035, 0.004, 'brass'))
    # a marble kerb round the glass
    for (x0, y0, x1, y1) in ((GX0 - 0.25, GY0 - 0.25, GX1 + 0.25, GY0), (GX0 - 0.25, GY1, GX1 + 0.25, GY1 + 0.25),
                             (GX0 - 0.25, GY0, GX0, GY1), (GX1, GY0, GX1 + 0.25, GY1)):
        R.nocol.add(box(x0, y0, -0.004, x1, y1, 0.006, 'brass'))
    # the sky: a deep black box full of stars at every depth (they drift past each other as you walk),
    # a faint band of milky light across it, and two nebulae glowing far down
    rnd = rng(65)
    stars = {'e_kiosk': Geo(), 'e_blue': Geo(), 'e_candle': Geo()}
    for k in range(900):
        x, y = rnd.uniform(GX0 + 0.1, GX1 - 0.1), rnd.uniform(GY0 + 0.1, GY1 - 0.1)
        z = -0.25 - (-0.3 - ZS) * rnd.random() ** 0.6
        if DX0 - 0.5 < x < DX1 + 0.5 and DY0 - 2.8 < y < DY1 + 0.5 and z > PZ - 0.5: continue
        # thicker along a diagonal band (the milky way)
        d = abs((x - GX0) - (y - GY0)) / 26.0
        if d > 0.25 and rnd.random() < 0.55: continue
        r = rnd.choice((0.012, 0.016, 0.02, 0.02, 0.028, 0.04)) * (1.4 if z < -2.5 else 1.0)
        m = 'e_kiosk' if rnd.random() < 0.8 else rnd.choice(('e_blue', 'e_candle'))
        stars[m].add(octa(x, y, z, r, m))
    for m, g in stars.items():
        if g.f: R.light(g)
    # nebulae: dense clouds of coloured stars far down
    for (cx, cy, rr, m, n) in ((10.0, 11.0, 3.4, 'e_blue', 160), (21.5, 20.0, 2.8, 'e_red', 110), (19.0, 9.0, 1.8, 'e_blue', 60), (8.0, 23.0, 2.2, 'e_candle', 60)):
        g = Geo()
        for k in range(n):
            a = rnd.uniform(0, 2 * math.pi); dd = rr * rnd.random() ** 0.7
            x, y = cx + dd * math.cos(a) * 1.3, cy + dd * math.sin(a) * 0.8
            z = ZS + 0.15 + rnd.uniform(0, 1.4) * (1 - dd / rr)
            g.add(octa(x, y, z, rnd.uniform(0.01, 0.035), m))
        R.light(g)


def octa(x, y, z, r, m):
    g = Geo()
    P = [(x + r, y, z), (x - r, y, z), (x, y + r, z), (x, y - r, z), (x, y, z + r), (x, y, z - r)]
    ids = [g.vert(p) for p in P]
    for (a, b, c) in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
        g.face([ids[a], ids[b], ids[c]], m, [(0, 0), (1, 0), (0, 1)])
    return g.fix()


def furniture(R):
    """Two rows of long reading tables standing on the glass, green lamps, chairs; busts at the ends."""
    for xc in (9.2, 22.8):
        for (y0, y1) in ((5.0, 9.6), (11.2, 15.8), (17.4, 22.0), (23.6, 28.2)):
            if xc > 16 and y0 < 6: continue          # the hatch is over there
            reading_table(R, xc - 0.75, y0, xc + 0.75, y1, lamps=2, axis='y')
            book_pile(R, xc + 0.3, y0 + 1.2, 0.78, 3, seed=int(xc * y0))
    for (x, y) in ((9.2, 3.8), (9.2, 29.2), (22.8, 29.2)):
        bust(R, x, y)
    # a lamp standard or two on the glass
    for (x, y) in ((16.0, 8.0), (16.0, 24.0)):
        lamp_post(R, x, y, h=2.8)
    # pendant lamps
    for x in (9.2, 22.8):
        for y in (7.3, 13.5, 19.7, 25.9):
            pendant(R, x, y, 3.4, TOP - 0.1, r=0.24)
    for y in (4.0, 12.0, 20.0, 28.0):
        bulb(R, 16.0, y, 5.6, r=0.18, m='e_lamp', top=TOP - 0.1)


def bust(R, x, y, a=0.0):
    R.parts.add(box(x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, 1.15, 'tile', top='marble'))
    R.parts.add(box(x - 0.36, y - 0.36, 1.1, x + 0.36, y + 0.36, 1.2, 'tile'))
    R.nocol.add(box(x - 0.2, y - 0.13, 1.2, x + 0.2, y + 0.13, 1.45, 'ivory'))
    R.nocol.add(ellipsoid(x, y, 1.62, 0.13, 0.15, 0.19, 'ivory', 10, 5))


def walls(R):
    """Tall cases on every wall between the doors; a brass rail along the kerb of the glass on the long sides."""
    wall_cases(R, rows=13, frame='walnut')
    for (x, y) in ((1.4, 1.4), (W - 1.4, 1.4), (1.4, D - 1.4), (W - 1.4, D - 1.4)):
        R.nocol.add(cyl(x, y, 0, 1.3, 0.02, 6, side='brass', caps=False))
        R.light(sphere(x, y, 1.4, 0.1, 10, 5, 'e_amber'))


def deck(R):
    """The hatch, its lid standing open, the ladder, and the deck hung under the glass among the stars."""
    # the frame and the open lid
    hatch_frame(R, HX0, HY0, HX1, HY1, 0.0, m='brass', t=0.06)
    lid = box(0, 0, 0, HX1 - HX0, 0.04, HY1 - HY0, 'brass')
    lid.add(box(0.05, 0.04, 0.05, HX1 - HX0 - 0.05, 0.05, HY1 - HY0 - 0.05, 'iron'))
    rot(lid, 'x', -0.35)
    lid.xform(0, HX0, HY0 - 0.06, 0.0)
    R.nocol.add(lid)
    # rails round the hatch (not on its north side, where the ladder comes up)
    rail(R, HX0 - 0.1, HY1, HX0 - 0.1, HY0 - 0.1, 0.0)
    rail(R, HX0 - 0.1, HY0 - 0.1, HX1 + 0.1, HY0 - 0.1, 0.0)
    rail(R, HX1 + 0.1, HY0 - 0.1, HX1 + 0.1, HY1, 0.0)
    # the ladder, from the deck up through the hatch
    L = ladder_up(R, LXC, HY1 - 0.02 - (0.0 - PZ) / math.tan(math.radians(60)), PZ, 0.0, '+y', w=0.8, m='oak', rail='brass')
    # the deck: oak boards on brass hangers from the glazing bars above
    R.parts.add(box(DX0, DY0, PZ - 0.2, DX1, DY1, PZ, 'oak', bottom='walnut', sides='walnut'))
    for (x, y) in ((DX0 + 0.1, DY0 + 0.1), (DX1 - 0.1, DY0 + 0.1), (DX0 + 0.1, DY1 - 0.1), (DX1 - 0.1, DY1 - 0.1)):
        R.nocol.add(cyl(x, y, PZ, -0.05, 0.02, 6, side='brass', caps=False))
    # rails round the deck, open on the west side of the south edge for a few steps down onto the sky
    rail_line(R, [(DX0 + 0.05, DY0 + 0.05), (DX0 + 0.05, DY1 - 0.05), (DX1 - 0.05, DY1 - 0.05), (DX1 - 0.05, DY0 + 0.05), (DX0 + 1.3, DY0 + 0.05)], PZ, h=0.95, m='brass')
    # the steps down to the floor of the sky, off the deck's south-west corner (the sky goes all the way down,
    # but the box it is painted on has a floor)
    n = 8
    rise = (PZ - ZS) / n
    R.flight(DX0 + 0.12, DY0 - n * 0.28, ZS, 1.1, n, rise, 0.28, '+y', m='oak', riser='walnut', side='walnut')
    for x in (DX0 + 0.1, DX0 + 1.24):
        stair_rail(R, x, DY0 - n * 0.28 + 0.28, ZS + rise, x, DY0, PZ, m='brass')
    # things on the deck: a chair, a little table, a candle, a telescope pointing down at the stars
    R.parts.add(chair(DX0 + 1.4, DY1 - 1.2, -math.pi / 4))
    R.spot('sit', DX0 + 1.4, DY1 - 1.2, PZ + 0.48, -math.pi / 4)
    tb = table(DX0 + 2.0, DY1 - 1.0, DX0 + 2.7, DY1 - 0.4, 0.7, 'walnut', top='leather')
    tb.xform(0, 0, 0, PZ); R.parts.add(tb)
    candle(R, DX0 + 2.2, DY1 - 0.7, PZ + 0.7, h=0.14)
    open_book(R, DX0 + 2.5, DY1 - 0.7, PZ + 0.7, 0.2)
    tx, ty = DX1 - 1.4, DY0 + 1.8
    for k in range(3):
        a = k * 2 * math.pi / 3
        R.nocol.add(beam((tx, ty, PZ + 1.1), (tx + 0.45 * math.cos(a), ty + 0.45 * math.sin(a), PZ), 0.03, 'walnut'))
    tube = cyl(0, 0, -0.5, 0.7, 0.08, 12, side='brass', top='black', bottom='brass')
    tube.add(cyl(0, 0, -0.75, -0.5, 0.11, 12, side='brass', top='brass', bottom='black'))
    rot(tube, 'x', 0.9)
    tube.xform(0.3, tx, ty, PZ + 1.15)
    R.nocol.add(tube)
    R.col.add(box(tx - 0.5, ty - 0.5, PZ, tx + 0.5, ty + 0.5, PZ + 1.2, 'tile'))
    R.light(sphere(DX0 + 0.3, DY1 - 0.3, PZ + 1.2, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(cyl(DX0 + 0.3, DY1 - 0.3, PZ + 1.25, -0.05, 0.01, 4, side='brass', caps=False))
    R.spot('plaque', DX0 + 2.8, DY1 - 0.06, PZ + 1.3, -math.pi / 2, text='THE STARS ARE NOT FOR READING. PLEASE DO NOT LEAN ON THE SKY.')
    secret(R, DX0 + 2.0, DY0 + 2.4, PZ, 'The Deck Under the Glass',
           'Under the open pane a ladder, and under the ladder a little deck hung in the night. The readers\' chair legs stand on the glass above you. Someone has left a telescope pointing down.', r=1.8)
