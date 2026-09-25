"""The Room Inside Out: a dim hall with a great closed box standing in the middle of it, twelve metres
square and six high, its walls nothing but the backs of bookcases, boarded and strapped with iron. The
things that belong inside a room are on its outside: a painting, a clock, a light switch, chairs drawn
up to read the backs of the shelves. There is a door in it, and the door is painted on. The way in is
under the floor: a hatch behind the box, a crawl, and a hatch up into a warm room the right way round."""
from kit_h8 import *

W = D = 32.0
B0, B1 = 10.0, 22.0          # the box, x and y
BH = 5.9                     # its height
TW = 0.1                     # its wall: the planks (the bookcases stand against it inside)
TZ = -1.45                   # the crawl's floor
TY0, TY1 = 18.4, 19.6        # the crawl runs east-west
HX0, HX1 = 24.1, 25.78       # the hatch outside (the flight down, climbing +x)
IX0, IX1 = 18.72, 20.4       # the hatch inside
NSTEP, RUNS = 6, 0.28


def make():
    R = Room('insideout', 2, 2, res=2048)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP, 'tile', bottom='slate', top='plaster'))
    hall(R)
    the_box(R)
    crawl(R)
    inside(R)
    g = navloop(R, [(4.5, 4.5), (16, 4.5), (27.5, 4.5), (27.5, 16), (27.5, 27.5), (16, 27.5), (4.5, 27.5), (4.5, 16)])
    navloop(R, [(14, 12.2), (18, 12.2), (18, 15.2), (14, 15.2)])
    fx(R, 'dust', [B0 + TW, B0 + TW, 0.5, B1 - TW, B1 - TW, 5.0])
    secret(R, 16.0, 16.0, 0.0, 'The Right Way Round', r=3.0,
           text='You come up through the floor into the room the hall was keeping. Everything faces inward here, as it should: the books, the chairs, the lamp. It is very quiet and it is very warm.')
    return finish(R, 'The Room Inside Out', weight=3, probe=(5.0, 16, 2.5),
                  blurb='Someone has built a room inside out. You are outside it, with the backs of its bookcases, and the door is only painted on.')


def hall(R):
    """A dim arcaded hall: bookcases round the walls, reading tables with green lamps round the box."""
    wall_cases(R, rows=11, frame='walnut')
    # reading tables drawn up to the box, facing it, as if its walls were the shelves
    for (x0, y0, x1, y1, face, cxs) in ((12.5, 6.6, 19.5, 7.6, math.pi / 2, None), (12.5, 24.4, 19.5, 25.4, -math.pi / 2, None),
                                        (6.6, 12.5, 7.6, 17.5, 0.0, None)):
        table(R, x0, y0, x1, y1, h=0.76, top='leather')
        if x1 - x0 > y1 - y0:
            for x in (x0 + 1.2, (x0 + x1) / 2, x1 - 1.2):
                desk_lamp(R, x, (y0 + y1) / 2, 0.76, m='e_lamp' if x != (x0 + x1) / 2 else 'e_dim')
                chair(R, x, y0 - 0.5 if face > 0 else y1 + 0.5, face)
        else:
            for y in (y0 + 1.0, y1 - 1.0):
                desk_lamp(R, (x0 + x1) / 2, y, 0.76)
                chair(R, x0 - 0.5, y, face)
    for (x, y) in ((8, 8), (24, 8), (8, 24), (24, 24), (16, 3.2), (16, D - 3.2), (3.2, 16), (W - 3.2, 16)):
        pendant(R, x, y, 4.6, TOP, r=0.26, m='e_dim')
    for (x, y) in ((2.4, 2.4), (W - 2.4, 2.4), (2.4, D - 2.4), (W - 2.4, D - 2.4)):
        lamp_post(R, x, y, 0.0, 2.2, m='e_amber')


def the_box(R):
    """Its outside: plank backs of bookcases, iron straps and corner irons, a painted door."""
    b0, b1 = B0, B1
    t = TW
    for (x0, y0, x1, y1) in ((b0, b0, b1, b0 + t), (b0, b1 - t, b1, b1), (b0, b0 + t, b0 + t, b1 - t), (b1 - t, b0 + t, b1, b1 - t)):
        R.parts.add(box(x0, y0, 0, x1, y1, BH, 'wood', skip=('-z',)))
    R.parts.add(box(b0 + t, b0 + t, BH - 0.3, b1 - t, b1 - t, BH, 'wood', bottom='plaster'))
    R.parts.add(box(b0 - 0.08, b0 - 0.08, BH, b1 + 0.08, b1 + 0.08, BH + 0.18, 'walnut'))
    for (x0, y0, x1, y1) in ((b0 - 0.08, b0 - 0.08, b1 + 0.08, b0), (b0 - 0.08, b1, b1 + 0.08, b1 + 0.08), (b0 - 0.08, b0, b0, b1), (b1, b0, b1 + 0.08, b1)):
        R.parts.add(box(x0, y0, 0, x1, y1, 0.22, 'walnut', skip=('-z',)))
    g = Geo()
    L = b1 - b0
    for side in range(4):
        # battens (the shelf ends behind) and straps, laid out along +x then turned to the face
        f = Geo()
        k = 0
        while k * 1.2 <= L + 1e-6:
            u = k * 1.2
            f.add(box(u - 0.05, -0.04, 0.22, u + 0.05, 0.0, BH, 'walnut'))
            k += 1
        for z in (1.1, 2.9, 4.7):
            f.add(box(0, -0.06, z, L, -0.0, z + 0.12, 'iron'))
            for j in range(int(L / 1.2) + 1):
                f.add(box(j * 1.2 - 0.03, -0.08, z + 0.03, j * 1.2 + 0.03, -0.06, z + 0.09, 'iron'))
        ang = (0.0, math.pi / 2, math.pi, -math.pi / 2)[side]
        ox, oy = ((b0, b0), (b1, b0), (b1, b1), (b0, b1))[side]
        g.add(f.xform(ang, ox, oy, 0))
    # corner irons
    for (x, y) in ((b0, b0), (b1, b0), (b1, b1), (b0, b1)):
        g.add(box(x - 0.1, y - 0.1, 0.22, x + 0.1, y + 0.1, BH, 'iron'))
    R.nocol.add(g)
    # the painted door on the south face, with its handle; an exit sign over it that tells you nothing
    dx = 16.0
    R.nocol.add(box(dx - 0.75, b0 - 0.1, 0.22, dx + 0.75, b0 - 0.07, 2.5, 'walnut'))
    for (z0, z1) in ((0.4, 1.3), (1.5, 2.35)):
        R.nocol.add(box(dx - 0.6, b0 - 0.12, z0, dx + 0.6, b0 - 0.1, z1, 'wood'))
    R.nocol.add(box(dx + 0.45, b0 - 0.17, 1.2, dx + 0.55, b0 - 0.12, 1.26, 'brass'))
    R.light(box(dx - 0.3, b0 - 0.14, 2.75, dx + 0.3, b0 - 0.1, 2.95, 'e_exit'))
    # inside-out things: a painting, a clock, a light switch, a coat hook, a rug on the wall
    R.nocol.add(box(12.4, b0 - 0.12, 2.2, 14.2, b0 - 0.08, 3.4, 'gilt'))
    R.nocol.add(box(12.5, b0 - 0.13, 2.3, 14.1, b0 - 0.12, 3.3, 'green'))
    R.nocol.add(box(b1 + 0.08, 15.2, 1.1, b1 + 0.1, 15.3, 1.25, 'ivory'))
    R.nocol.add(cyl(b0 - 0.1, 17.0, 3.0, 3.05, 0.45, 20, side='brass', top='ivory', bottom='ivory').xform(0, 0, 0, 0))
    clock_face(R, b0 - 0.1, 17.0, 3.0)
    R.nocol.add(box(12.0, b1 + 0.08, 0.6, 20.0, b1 + 0.11, 3.2, 'carpet'))
    R.nocol.add(box(12.3, b1 + 0.11, 0.9, 19.7, b1 + 0.12, 2.9, 'velvet'))
    R.nocol.add(box(b1 + 0.08, 12.0, 1.7, b1 + 0.2, 12.06, 1.76, 'brass'))
    # a pendant hanging sideways out of the east face, still lit
    R.nocol.add(box(b1 + 0.08, 18.0, 3.4, b1 + 0.9, 18.02, 3.42, 'brass'))
    R.nocol.add(rot(frustum(0, 0, -0.1, 0.2, 0.3, 0.08, 12, 'green', inner='ivory'), 'y', -math.pi / 2).xform(0, b1 + 1.0, 18.0, 3.4))
    R.light(box(b1 + 0.88, 17.85, 3.25, b1 + 0.9, 18.15, 3.55, 'e_dim'))


def clock_face(R, x, y, z):
    """A clock face on the box's west wall (facing -x), stopped."""
    R.nocol.add(box(x - 0.06, y - 0.42, z - 0.42, x - 0.04, y + 0.42, z + 0.42, 'ivory'))
    R.nocol.add(box(x - 0.08, y - 0.02, z - 0.02, x - 0.06, y + 0.02, z + 0.3, 'iron'))
    R.nocol.add(box(x - 0.08, y - 0.02, z - 0.02, x - 0.06, y + 0.22, z + 0.02, 'iron'))


def crawl(R):
    """The hatch behind the box, a crawl under the floor, a hatch up inside."""
    rise = -TZ / NSTEP
    R.cut(box(IX0 - 0.02, TY0, TZ, HX1 + 0.02, TY1, -0.15, 'slate', bottom='slate', top='wood'))
    for (x0, x1) in ((HX0, HX1), (IX0, IX1)):
        R.cut(box(x0, TY0, TZ, x1, TY1, 0.3, 'slate', bottom='slate', top='tile'))
    R.flight(HX0, TY0, TZ, TY1 - TY0, NSTEP, rise, RUNS, '+x', m='oak', side='slate')
    R.flight(IX1, TY0, TZ, TY1 - TY0, NSTEP, rise, RUNS, '-x', m='oak', side='slate')
    # rails round both hatches, open at the head of the steps
    for (x0, x1, head) in ((HX0, HX1, 'E'), (IX0, IX1, 'W')):
        brass_rail(R, x0, TY0 - 0.05, x1, TY0 - 0.05, 0.0)
        brass_rail(R, x0, TY1 + 0.05, x1, TY1 + 0.05, 0.0)
        xe = x0 - 0.05 if head == 'E' else x1 + 0.05
        brass_rail(R, xe, TY0 - 0.05, xe, TY1 + 0.05, 0.0)
        # the trap's leaf, standing open
        R.nocol.add(box(x0, TY0 - 0.16, 0, x1, TY0 - 0.12, TY1 - TY0, 'oak', sides='walnut'))
        R.nocol.add(box(x0 + 0.3, TY0 - 0.2, 0.5, x0 + 0.4, TY0 - 0.16, 0.56, 'iron'))
    # the crawl: rough boards overhead, a candle on the floor halfway
    for k in range(9):
        x = IX1 + 0.3 + k * 0.42
        if x > HX0 - 0.1: break
        R.nocol.add(box(x, TY0, -0.3, x + 0.1, TY1, -0.15, 'wood'))
    R.parts.add(cyl(22.2, TY1 - 0.25, TZ, TZ + 0.03, 0.08, 8, side='brass', top='brass'))
    candle(R, 22.2, TY1 - 0.25, TZ + 0.03, h=0.12, r=0.02)
    # a folded-back rug that half hides the outer hatch
    R.parts.add(box(HX1 + 0.1, 17.4, 0, HX1 + 2.6, 20.6, 0.02, 'carpet'))
    R.nocol.add(box(HX1 + 0.1, 17.4, 0.02, HX1 + 0.5, 20.6, 0.14, 'velvet'))


def inside(R):
    """The room the right way round: bookcases facing in on every wall, a rug, a table, a lamp, a window."""
    inner(R, B0 + TW, B1 - TW)


def inner(R, a0, a1):
    rows = 12
    for (lo, hi) in ((a0 + 0.1, a1 - 0.1),):
        R.shelf(lo, a0, 0, hi - lo, '+y', rows=rows, frame='walnut')
        R.shelf(hi, a1, 0, hi - lo, '-y', rows=rows, frame='walnut')
        R.shelf(a1, lo, 0, hi - lo, '-x', rows=rows, frame='walnut')
        R.shelf(a0, hi, 0, 4.0, '+x', rows=rows, frame='walnut')
        R.shelf(a0, lo + 4.0, 0, 4.0, '+x', rows=rows, frame='walnut')
    # a window in the west wall between the cases, full of afternoon
    wy0, wy1 = a0 + 4.3, a1 - 4.3
    R.light(box(a0 - 0.02, wy0, 1.0, a0, wy1, 4.4, 'e_sky'))
    for y in (wy0, (wy0 + wy1) / 2, wy1):
        R.nocol.add(box(a0, y - 0.05, 1.0, a0 + 0.08, y + 0.05, 4.4, 'oak'))
    for z in (1.0, 2.7, 4.4):
        R.nocol.add(box(a0, wy0, z - 0.05, a0 + 0.08, wy1, z + 0.05, 'oak'))
    R.nocol.add(box(a0, wy0 - 0.3, 0.9, a0 + 0.3, wy1 + 0.3, 1.0, 'oak'))
    R.parts.add(box(a0 + 1.6, a0 + 1.4, 0, a1 - 3.0, 18.0, 0.02, 'carpet'))
    table(R, 12.6, 17.3, 16.6, 18.7, h=0.76, top='leather')
    desk_lamp(R, 13.4, 18.0, 0.76); desk_lamp(R, 15.8, 18.0, 0.76)
    open_book(R, 14.6, 17.8, 0.76, 0.1)
    book_pile(R, 16.1, 17.6, 0.76, 4, seed=3)
    for x in (13.4, 15.8):
        chair(R, x, 17.3 - 0.5, math.pi / 2)
    armchair(R, 19.6, 13.0, math.pi * 0.75)
    armchair(R, 12.2, 13.0, math.pi * 0.25)
    floor_lamp(R, 20.4, 12.0, 1.7)
    chandelier(R, 16.0, 16.0, BH - 1.6, 1.0, n=10, chain=BH - 0.3)
