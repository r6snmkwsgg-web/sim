"""The Mirror Lake: the floor of this hall is a still black mirror, a man's height down, and a grid of stone
causeways crosses it from door to door on the lines of the doorways. The vault, its ribs, the shelves and
the lamps hang in it upside down, as deep again. Two stairs go down onto the glass. In the wall under the
west causeway, shadowed by its lip, there is a low door; from the causeways you only see it in the
reflection."""
from kit_h12 import *

W = D = 32.0
ZB = -1.8                     # the mirror floor
RIM = 3.0                     # the walkway round the walls
CW = 1.5                      # causeway half width
BANDS = [(RIM, 8 - CW), (8 + CW, 24 - CW), (24 + CW, W - RIM)]
SPRING, RISE = 4.8, 2.6
SX0, SX1, SY0, SY1 = 6.8, 9.2, 12.4, 19.6     # the room under the west causeway
SZ = ZB


def make():
    R = Room('mirrorlake', 2, 2, res=2048)
    rs = rng(71)
    R.sockets(floor='terrazzo', wall='tile')
    vault_y(R, T - 0.02, D - T + 0.02, W / 2, W - 2 * T, SPRING, RISE)
    ribs(R)
    pools(R)
    walls(R, rs)
    flights(R)
    lamps(R)
    under(R, rs)
    mirror(R, (16.0, RIM, ZB + 0.004), (0, 0, 1), W - 2 * RIM, D - 2 * RIM, up=(0, 1, 0))
    P = {}
    for i, x in enumerate((1.7, 8.0, 16.0, 24.0, 30.3)):
        for j, y in enumerate((1.7, 8.0, 16.0, 24.0, 30.3)):
            if i in (0, 4) or j in (0, 4) or x in (8.0, 24.0) or y in (8.0, 24.0):
                if not (i in (0, 4) and j in (0, 4)) and not (x == 16.0 and y == 16.0): P[(i, j)] = (x, y)
    for (i, j) in ((0, 0), (4, 0), (0, 4), (4, 4)): P[(i, j)] = ((1.7, 30.3)[i // 4], (1.7, 30.3)[j // 4])
    L = []
    for (i, j) in P:
        for (di, dj) in ((1, 0), (0, 1)):
            if (i + di, j + dj) in P: L.append(((i, j), (i + di, j + dj)))
    P['q0'] = (11.9, 8.7); P['q1'] = (11.9, 10.1); P['q2'] = (15.7, 10.1, ZB); P['p'] = (16.0, 16.0, ZB)
    P['r0'] = (20.1, 23.3); P['r1'] = (20.1, 21.9); P['r2'] = (16.3, 21.9, ZB)
    L += [((2, 1), 'q0'), ('q0', 'q1'), ('q1', 'q2'), ('q2', 'p'), ('p', 'r2'), ('r2', 'r1'), ('r1', 'r0'), ('r0', (2, 3))]
    navgrid(R, P, L)
    secret(R, 8.0, 17.8, SZ, 'Under the Causeway',
           'The door in the reflection is real. Inside the causeway, at the level of the glass, a long low dry room: a mattress, a candle, a pane of black mirror in the ceiling looking up at nothing.', r=2.0)
    return finish(R, 'The Mirror Lake', weight=3, probe=(16.0, 5.0, 2.4), top=SPRING + RISE, bot=SZ,
                  blurb='The floor is a black mirror a man\'s height down, and the whole hall stands on its own reflection. The causeways are the only thing holding you up. They are enough. Probably.')


def ribs(R):
    for y in (4.0, 12.0, 20.0, 28.0):
        R.nocol.add(prism(arc_band(W / 2, W - 2 * T, SPRING, RISE, 0.0, 0.35, 40), 'y', y - 0.25, y + 0.25, 'tile', cap='tile'))
        for x in (T, W - T):
            s = 1 if x < 16 else -1
            R.parts.add(box(min(x, x + s * 0.4), y - 0.35, 0, max(x, x + s * 0.4), y + 0.35, SPRING, 'tile', skip=('-z',)))
    for y in (8.0, 16.0, 24.0):
        R.cut(box(14.8, y - 1.6, SPRING + RISE - 0.3, 17.2, y + 1.6, SPRING + RISE + 0.17, 'plaster'))
        R.light(box(14.8, y - 1.6, SPRING + RISE + 0.13, 17.2, y + 1.6, SPRING + RISE + 0.14, 'e_sky'))


def pools(R):
    """Nine basins between the causeways, a black floor (the mirror lies on it), stone lips, brass rails."""
    for (x0, x1) in BANDS:
        for (y0, y1) in BANDS:
            R.cut(box(x0, y0, ZB, x1, y1, 0.02, 'slate', bottom='black'))
            # lips: a moulded stone edge proud of the wall, deeper on the west side of the middle basin
            for (side, a, b) in (('S', x0, x1), ('N', x0, x1), ('W', y0, y1), ('E', y0, y1)):
                lip = 0.9 if (side == 'W' and x0 == 8 + CW and y0 == 8 + CW) else 0.28
                if side == 'S': g = box(a, y0, -0.22, b, y0 + lip, 0.0, 'tile')
                elif side == 'N': g = box(a, y1 - lip, -0.22, b, y1, 0.0, 'tile')
                elif side == 'W': g = box(x0, a, -0.22, x0 + lip, b, 0.0, 'tile')
                else: g = box(x1 - lip, a, -0.22, x1, b, 0.0, 'tile')
                R.parts.add(g)
            # rails round the basin, on the walkway edge; gaps where the stairs come up
            gaps = []
            if (x0, y0) == (8 + CW, 8 + CW): gaps = [('S', 11.3, 12.5), ('N', 19.5, 20.7)]
            for (side, p0, p1) in (('S', (x0, y0), (x1, y0)), ('N', (x0, y1), (x1, y1)), ('W', (x0, y0), (x0, y1)), ('E', (x1, y0), (x1, y1))):
                segs = [(p0, p1)]
                for (gs, g0, g1) in gaps:
                    if gs == side:
                        segs = [(p0, (g0, p0[1])), ((g1, p0[1]), p1)]
                off = {'S': (0, -0.08), 'N': (0, 0.08), 'W': (-0.08, 0), 'E': (0.08, 0)}[side]
                for (a, b) in segs:
                    brass_rail(R, a[0] + off[0], a[1] + off[1], b[0] + off[0], b[1] + off[1], 0.0, h=0.95)


def flights(R):
    """Two stairs down onto the glass in the middle basin: along its south wall going east, along its north
    wall going west, each from a little landing at the causeway's edge."""
    y0 = 8 + CW
    # south-west: landing x 11.3..12.5, then down east to x 15.2
    R.parts.add(box(11.3, y0, ZB, 12.5, y0 + 1.2, 0.0, 'tile', top='terrazzo'))
    R.flight(12.5 + 9 * 0.3, y0, ZB, 1.2, 9, 0.2, 0.3, '-x', m='terrazzo', riser='tile', side='tile')
    R.parts.add(slope_box(12.5, 15.2, y0, y0 + 1.2, ZB, ZB, 0.0, ZB + 0.2, 'tile'))
    stair_rail(R, 11.3, y0 + 1.25, 0.0, 12.5, y0 + 1.25, 0.0)
    stair_rail(R, 12.5, y0 + 1.25, 0.0, 15.2, y0 + 1.25, ZB + 0.2)
    # north-east: landing x 19.5..20.7, down west to x 16.8
    y1 = 24 - CW
    R.parts.add(box(19.5, y1 - 1.2, ZB, 20.7, y1, 0.0, 'tile', top='terrazzo'))
    R.flight(19.5 - 9 * 0.3, y1 - 1.2, ZB, 1.2, 9, 0.2, 0.3, '+x', m='terrazzo', riser='tile', side='tile')
    R.parts.add(slope_box(16.8, 19.5, y1 - 1.2, y1, ZB, ZB, ZB + 0.2, 0.0, 'tile'))
    stair_rail(R, 20.7, y1 - 1.25, 0.0, 19.5, y1 - 1.25, 0.0)
    stair_rail(R, 19.5, y1 - 1.25, 0.0, 16.8, y1 - 1.25, ZB + 0.2)


def walls(R, rs):
    """Tall cases along the rim, between the doorways and the ribs' piers; reading desks by them."""
    segs = [(0.8, 3.55), (4.45, 6.2), (9.8, 11.55), (12.45, 15.6), (16.4, 19.55), (20.45, 22.2), (25.8, 27.55), (28.45, W - 0.8)]
    for (a, b) in segs:
        sh(R, '+y', T, a, b, rows=10, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=10, frame='walnut')
        sh(R, '+x', T, a, b, rows=10, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=10, frame='walnut')
    R.parts.add(box(T, T, 4.35, W - T, T + 0.45, 4.5, 'walnut'))
    R.parts.add(box(T, D - T - 0.45, 4.35, W - T, D - T, 4.5, 'walnut'))
    R.parts.add(box(T, T, 4.35, T + 0.45, D - T, 4.5, 'walnut'))
    R.parts.add(box(W - T - 0.45, T, 4.35, W - T, D - T, 4.5, 'walnut'))


def lamps(R):
    """Green standards at every causeway crossing and along the rim; pendants from the ribs."""
    for x in (8.0, 24.0):
        for y in (8.0, 24.0):
            for (dx, dy) in ((-1.2, -1.2), (1.2, 1.2)):
                lamp_post(R, x + dx, y + dy, 0.0, h=2.4)
    for t in (16.0,):
        for (x, y) in ((t, 8 - 1.2), (t, 24 + 1.2), (8 - 1.2, t), (24 + 1.2, t)):
            lamp_post(R, x, y, 0.0, h=2.4)
    for y in (4.0, 12.0, 20.0, 28.0):
        for x in (8.0, 16.0, 24.0):
            pendant(R, x, y, 4.2, SPRING + RISE - 0.5, r=0.22)
    for (x, y) in ((2.0, 2.0), (30.0, 2.0), (2.0, 30.0), (30.0, 30.0)):
        R.light(sphere(x, y, 2.4, 0.09, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, y, 2.45, SPRING - 0.2, 0.01, 4, side='iron', caps=False))


def under(R, rs):
    """The low door in the west wall of the middle basin, under the deep lip; behind it a long low room
    inside the causeway, at the level of the glass (you go in on your knees)."""
    xw = 8 + CW                                    # the basin's west wall
    R.cut(box(SX1 - 0.02, 15.45, ZB, xw + 0.02, 16.55, ZB + 1.3, 'slate', bottom='terrazzo', top='slate'))
    R.nocol.add(frame_rect('x', xw, 15.45, 16.55, ZB, ZB + 1.3, 1, w=0.1, d=0.04, m='walnut'))
    R.cut(box(SX0, SY0, SZ, SX1, SY1, -0.35, 'damask', bottom='carpet', top='plaster'))
    # a mattress, a lamp, low shelves, a writing slope, and a 'window' in the ceiling of black glass
    R.parts.add(box(SX0 + 0.1, 17.3, SZ, SX0 + 1.0, SY1 - 0.1, SZ + 0.2, 'bed'))
    R.nocol.add(box(SX0 + 0.2, SY1 - 0.55, SZ + 0.2, SX0 + 0.9, SY1 - 0.15, SZ + 0.3, 'white'))
    R.spot('bed', SX0 + 0.55, 18.4, SZ + 0.2, math.pi / 2)
    sh(R, '+x', SX0, 12.6, 16.9, z=SZ, rows=2, frame='walnut')
    sh(R, '-x', SX1, 12.6, 15.2, z=SZ, rows=2, frame='walnut')
    R.parts.add(box(7.8, 12.7, SZ, 8.8, 13.3, SZ + 0.35, 'walnut', top='leather'))
    open_book(R, 8.3, 13.0, SZ + 0.35, math.pi)
    candle(R, 8.65, 12.85, SZ + 0.35, h=0.12)
    R.light(sphere(8.0, 18.6, -0.6, 0.06, 8, 4, 'e_candle'))
    R.nocol.add(box(7.2, 17.8, -0.37, 8.8, 19.2, -0.35, 'black'))
    R.spot('plaque', 8.3, 13.0, SZ, -math.pi / 2,
           text='A note on the writing slope: The lake is not deep. It is exactly as deep as the room above it. I have measured.')
