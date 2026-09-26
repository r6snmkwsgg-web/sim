"""The Long Gallery (afterimage): a long, plain, vaulted reading hall of alcoves, busts at the ends of the
stacks, desks with green lamps between them. Walk it and pale copies of you follow a few seconds behind;
and one pale figure that is not you walks its own slow figure of eight down the hall, and at the east
end goes out through the little door under the window. The door opens for you too."""
from kit_h12 import *

W, D = 32.0, 16.0
XE = 26.4                      # the gallery's east end wall
SPRING, RISE = 4.6, 2.9
STX = (2.6, 5.2, 10.8, 13.5, 16.2, 18.9, 21.4)   # the alcove stacks
SL = 4.4                       # how far they reach in from the side walls
DY0, DY1, DH = 7.4, 8.6, 2.3   # the little door
VX1, VY0, VY1 = 28.7, 5.0, 11.9     # the passage behind it
CX0, CY0, CX1, CY1 = 26.7, 0.6, 31.65 - 0.05, 4.7   # the room at the end of the loop
CH = 3.0


def make():
    R = Room('afterimage', 2, 1, res=2048)
    rs = rng(45)
    R.sockets(floor='terrazzo', wall='tile')
    vault_x(R, T - 0.02, XE, D / 2, D - 2 * T, SPRING, RISE)
    east_block(R)
    stacks(R, rs)
    ends(R)
    lamps(R)
    hidden(R, rs)
    # the effect: the whole gallery. The box reaches past the east end so that the other figure's loop
    # (x from 0.12 to 0.88 of the box) ends exactly at the little door.
    x0 = T
    Wb = (XE + 0.2 - x0) / 0.88
    fx(R, 'afterimage', [x0, T, 0.0, x0 + Wb, D - T, TOP])
    fx(R, 'dust', [T, T, 0.5, XE, D - T, 7.0])
    ids = navgrid(R, {
        'w': (1.6, 8.0), 'a': (4.0, 6.0), 'b': (8.0, 6.0), 'c': (14.0, 6.0), 'd': (20.0, 6.0), 'e': (24.0, 6.0),
        'f': (24.0, 10.0), 'g': (20.0, 10.0), 'h': (14.0, 10.0), 'i': (8.0, 10.0), 'j': (4.0, 10.0),
        's1': (8.0, 1.6), 's2': (24.0, 1.6), 'n1': (8.0, 14.4), 'n2': (24.0, 14.4), 'k': (27.6, 14.0), 'm': (30.3, 13.0), 'e2': (30.3, 8.0)},
        [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g'), ('g', 'h'), ('h', 'i'), ('i', 'j'), ('j', 'a'),
         ('w', 'a'), ('w', 'j'), ('b', 's1'), ('e', 's2'), ('i', 'n1'), ('f', 'n2'), ('n2', 'k'), ('k', 'm'), ('m', 'e2')])
    secret(R, 29.0, 2.6, 0.0, 'Where It Goes',
           'The pale figure walks its figure of eight all day and goes out through the little door. This is where it goes: a narrow room, a bed made so tight nobody has ever been in it, a chair turned to the wall.', r=2.0)
    return finish(R, 'The Afterimage Gallery', weight=4, probe=(13.0, 8.0, 2.2), top=SPRING + RISE,
                  blurb='Something pale keeps pace a few steps behind you. When you turn, it is you, a little late. The other one, further off, is not.')


def east_block(R):
    """Past the gallery's east end: the east doorway's passage, which turns north and comes back into the
    gallery's north-east corner."""
    R.cut(box(29.0, 6.5, 0, W - T + 0.02, 15.3, 3.4, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(XE - 0.05, 12.6, 0, 29.02, 15.3, 3.4, 'tile', bottom='terrazzo', top='plaster'))
    pr = arch_profile(0, DW, 0, DJ)
    R.cut(prism([(p + 8.0, q) for p, q in pr], 'x', 29.0, W - T + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
    # a few cases along the passage, a lamp at the corner
    sh(R, '-x', W - T, 10.6, 15.0, rows=7, frame='walnut')
    sh(R, '+y', 12.6, 26.6, 28.8, rows=7, frame='walnut')
    R.light(sphere(30.3, 14.3, 2.9, 0.1, 8, 4, 'e_amber'))
    R.nocol.add(cyl(30.3, 14.3, 3.0, 3.4, 0.01, 4, side='iron', caps=False))


def stacks(R, rs):
    """Double-sided stacks reaching in from both long walls (the alcoves), a bust on a pedestal at each
    stack's end, a reading desk with a green lamp in every alcove."""
    for x in STX:
        for (y0, y1, face) in ((T, T + SL, 1), (D - T - SL, D - T, -1)):
            sh(R, '+x', x + 0.01, y0 + 0.02, y1, rows=8, frame='walnut')
            sh(R, '-x', x - 0.01, y0 + 0.02, y1, rows=8, frame='walnut')
            # a cornice and a little balustrade on top (the gallery that is never reached)
            R.parts.add(box(x - 0.42, y0, 3.46, x + 0.42, y1, 3.58, 'walnut'))
            for yy in [y0 + 0.2 + k * 0.3 for k in range(int((y1 - y0 - 0.2) / 0.3))]:
                R.nocol.add(cyl(x, yy, 3.58, 4.0, 0.045, 6, side='walnut', caps=False))
            R.nocol.add(box(x - 0.08, y0, 4.0, x + 0.08, y1, 4.06, 'walnut'))
            # the bust at the end
            ye = y1 + 0.3 if face > 0 else y0 - 0.3
            R.parts.add(box(x - 0.3, ye - 0.3, 0, x + 0.3, ye + 0.3, 1.15, 'tile', top='white'))
            bust(R, x, ye, 1.15, math.pi / 2 if face > 0 else -math.pi / 2)
    # desks in the alcoves between stacks
    for (a, b) in zip(STX, STX[1:]):
        if b - a > 4: continue
        xc = (a + b) / 2
        for (yd, face) in ((1.6, 1), (D - 1.6, -1)):
            R.parts.add(table_geo(xc - 0.55, yd - 0.8, xc + 0.55, yd + 0.8, 0.76, 'walnut', top='leather'))
            desk_lamp(R, xc, yd, 0.76)
            R.parts.add(chair_geo(xc, yd + face * 1.3, -face * math.pi / 2))
            R.spot('sit', xc, yd + face * 1.3, 0.48, -face * math.pi / 2)
    # between the doors along the side walls, cases
    for (a, b) in ((T + 0.1, 2.2), ):
        pass
    # long walls between stacks: dark panelling up to the cornice
    for y, s in ((T, 1), (D - T, -1)):
        R.nocol.add(box(T, min(y, y + s * 0.04), 0, XE, max(y, y + s * 0.04), 0.9, 'walnut'))
    # the runner down the middle
    R.nocol.add(box(1.8, 7.0, 0, XE - 1.2, 9.0, 0.012, 'slate'))


def bust(R, x, y, z, a):
    """A plain marble bust on a plinth top, looking along a."""
    g = Geo()
    g.add(box(-0.18, -0.13, 0, 0.18, 0.13, 0.08, 'white'))
    g.add(sphere(0, 0, 0.25, 0.2, 10, 5, 'white', lower=True))
    g.add(cyl(0, 0, 0.3, 0.45, 0.07, 8, side='white', caps=False))
    g.add(sphere(0.02, 0, 0.56, 0.12, 10, 6, 'white'))
    R.nocol.add(g.xform(a, x, y, z))


def ends(R):
    """The west end: the door and a round window over it. The east end: a tall arched window, and under it
    the little door the pale figure uses."""
    # windows
    for (x, s) in ((T, 1), (XE, -1)):
        pr = arch_profile(8.0, 2.6, 3.9, 1.8, 14)
        a0, a1 = (x - 0.3, x + 0.02) if s > 0 else (x - 0.02, x + 0.3)
        R.cut(prism(pr, 'x', a0, a1, arch_mats(len(pr), 'tile', 'tile'), cap='tile'))
        xw = x - 0.28 if s > 0 else x + 0.28
        em = 'e_sky' if s < 0 else 'e_dim'
        R.light(prism(pr, 'x', min(xw, xw + 0.02), max(xw, xw + 0.02), [em] * len(pr), cap=em))
        for k in (-1, 0, 1):
            R.nocol.add(box(min(x, x - s * 0.2) , 8.0 + k * 0.65 - 0.03, 3.9, max(x, x - s * 0.2), 8.0 + k * 0.65 + 0.03, 6.8, 'iron'))
        R.nocol.add(box(min(x, x - s * 0.2), 6.7, 5.3, max(x, x - s * 0.2), 9.3, 5.36, 'iron'))
    # the little door: a panelled walnut leaf you walk through, in a stone surround
    R.cut(box(XE - 0.05, DY0, 0, VX1, DY1, DH, 'walnut', bottom='terrazzo', top='walnut'))
    leaf = Geo()
    leaf.add(box(XE - 0.06, DY0, 0, XE - 0.02, DY1, DH, 'walnut'))
    for (z0, z1) in ((0.2, 1.0), (1.2, 2.1)):
        leaf.add(box(XE - 0.08, DY0 + 0.12, z0, XE - 0.06, DY1 - 0.12, z1, 'oak'))
    leaf.add(sphere(XE - 0.11, DY1 - 0.15, 1.0, 0.035, 6, 3, 'brass'))
    R.nocol.add(leaf)
    R.nocol.add(frame_rect('x', XE, DY0, DY1, 0.0, DH, -1, w=0.18, d=0.08, m='tile'))
    R.nocol.add(box(XE - 0.12, DY0 - 0.3, DH + 0.18, XE, DY1 + 0.3, DH + 0.3, 'tile'))


def hidden(R, rs):
    """Behind the little door: a passage south, and a narrow room with a made bed."""
    R.cut(box(XE - 0.02, VY0, 0, VX1, VY1, CH, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(CX0, CY0, 0, CX1, CY1 + 0.02, CH, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(CX0, CY1 - 0.02, 0, VX1, VY0 + 0.02, 2.3, 'plaster', bottom='floor', top='plaster'))
    # the bed along the south wall, made tight
    x0, x1 = 28.9, 30.95
    R.parts.add(box(x0, CY0 + 0.05, 0, x1, CY0 + 0.95, 0.45, 'walnut', top='bed'))
    R.nocol.add(box(x0 + 0.05, CY0 + 0.1, 0.45, x1 - 0.05, CY0 + 0.9, 0.5, 'bed'))
    R.nocol.add(box(x1 - 0.5, CY0 + 0.2, 0.5, x1 - 0.1, CY0 + 0.8, 0.6, 'white'))
    R.nocol.add(box(x0, CY0 + 0.05, 0.45, x0 + 0.06, CY0 + 0.95, 0.95, 'walnut'))
    R.spot('bed', (x0 + x1) / 2, CY0 + 0.5, 0.5, 0.0)
    # a chair turned to the wall; a hook with a coat; a candle
    R.parts.add(chair_geo(CX1 - 0.5, 3.4, 0.0))
    R.nocol.add(box(27.2, CY1 - 0.06, 1.7, 27.3, CY1, 1.75, 'brass'))
    R.nocol.add(box(26.95, CY1 - 0.2, 0.6, 27.55, CY1 - 0.08, 1.7, 'slate'))
    R.parts.add(box(27.0, 1.0, 0, 27.6, 1.6, 0.7, 'walnut'))
    candle(R, 27.3, 1.3, 0.7, h=0.18)
    open_book(R, 27.3, 1.45, 0.7, 0.0)
    R.spot('plaque', 27.3, 1.3, 0.0, 0.0,
           text='On the table, a book open at a page with only one line on it, in pencil: I walk it so you will know how.')
    sh(R, '+y', CY0, 26.8, 28.6, rows=6, frame='walnut')
    R.light(sphere(27.8, 8.5, 2.6, 0.07, 8, 4, 'e_candle'))


def lamps(R):
    for x in (3.0, 7.0, 11.0, 15.0, 19.0, 23.0):
        pendant(R, x, 8.0, 3.6, SPRING + RISE - 0.1, r=0.24)
    for x in STX:
        R.light(sphere(x, 5.0, 3.9, 0.07, 8, 4, 'e_amber'))
        R.light(sphere(x, D - 5.0, 3.9, 0.07, 8, 4, 'e_amber'))
