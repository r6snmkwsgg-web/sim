"""The Chair: a hall so big and so dark that its walls are only rumours, colonnades and bookcases half
seen at the edge of the light. In the middle, under the only lamp, a wooden chair with a book on it.
In the far corner, where nothing is lit but one weak bulb, a black door in the black wall: behind it,
all the chairs that were taken away so this one could be alone."""
from kit_h8 import *

W = D = 32.0
CX, CY = 16.0, 14.5                 # the chair
BX, BY = 26.4, 26.4                 # the hidden room fills the corner north-east of here
DX0, DX1 = 28.4, 29.5               # its door, in its south face


def make():
    R = Room('singlechair', 2, 2, res=2048)
    R.sockets(floor='slate', wall='black')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP, 'black', bottom='slate', top='black'))
    colonnades(R)
    the_chair(R)
    hidden(R)
    g = navloop(R, [(8.5, 5), (23.5, 5), (23.5, 23.5), (8.5, 23.5)])
    a = R.navpt(CX, CY - 1.6); R.link(g[0], a, g[1])
    fx(R, 'fog', [T, T, 0, W - T, D - T, TOP], density=0.05)
    fx(R, 'dust', [CX - 1.5, CY - 1.5, 0.3, CX + 1.5, CY + 1.5, 4.0])
    secret(R, 29.2, 29.0, 0.0, 'Where the Chairs Went',
           'Behind the black door are all the other chairs, hundreds of them, heaped to the ceiling. One stands upright in the middle, facing the door, as if it had been waiting for you to find it.')
    return finish(R, 'The Chair', weight=2, probe=(CX, CY + 3, 2.2),
                  blurb='There is one chair, and one lamp, and a great deal of dark. The chair is facing away from you. There is a book on it.')


def colonnades(R):
    """Square black piers down both sides, bookcases between them, reading desks whose lamps are almost out."""
    for x in (5.2, W - 5.2):
        for k in range(7):
            y = 4.0 + k * 4.0
            if x > 16 and y > BY - 1: continue
            R.parts.add(box(x - 0.4, y - 0.4, 0, x + 0.4, y + 0.4, TOP, 'slate', skip=('-z', '+z')))
            R.parts.add(box(x - 0.55, y - 0.55, 0, x + 0.55, y + 0.55, 0.45, 'slate', skip=('-z',)))
            R.parts.add(box(x - 0.55, y - 0.55, 5.6, x + 0.55, y + 0.55, 5.9, 'slate'))
            if k < 6 and k % 2 == 1 and not (x > 16 and y > BY - 5):
                s_ = -1 if x < 16 else 1
                table(R, x - 0.55, y + 1.3, x + 0.55, y + 2.7, h=0.76, m='walnut', top='leather')
                desk_lamp(R, x, y + 2.0, 0.76, m='e_dim' if k in (1, 5) else 'e_candle')
                chair(R, x - s_ * 0.9, y + 2.0, 0.0 if s_ > 0 else math.pi, spot=True)
    # the walls themselves: books, black on black
    wall_cases(R, rows=13, frame='walnut', sides='SW')
    for (a, b) in ((0.6, 6.2), (9.8, 15.4), (16.6, 22.2)):
        R.shelf(b, D - T, 0, b - a, '-y', rows=13, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=13, frame='walnut')
    # a faint arcade line high up: black arches on the piers
    for x in (5.2, W - 5.2):
        R.parts.add(box(x - 0.3, 3.6, 5.9, x + 0.3, 28.4 if x < 16 else 24.4, 6.3, 'slate'))


def the_chair(R):
    chair(R, CX, CY, math.pi / 2, frame='oak', seat='oak')
    g = Geo()
    g.add(box(-0.13, -0.1, 0, 0.13, 0.1, 0.05, 'green'))
    g.add(box(-0.12, -0.095, 0.005, 0.125, 0.095, 0.045, 'ivory'))
    g.xform(0.3, CX + 0.02, CY - 0.02, 0.48)
    R.nocol.add(g)
    # the lamp on its long cord, a green enamel shade
    z = 2.9
    R.nocol.add(cyl(CX, CY, z + 0.3, TOP, 0.01, 6, side='iron', caps=False))
    R.nocol.add(cyl(CX, CY, z + 0.22, z + 0.34, 0.05, 8, side='brass', top='brass', bottom='brass'))
    R.nocol.add(frustum(CX, CY, z - 0.08, z + 0.26, 0.5, 0.08, 16, 'green', inner='ivory'))
    R.light(cyl(CX, CY, z + 0.0, z + 0.06, 0.34, 16, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.nocol.add(sphere(CX, CY, z + 0.03, 0.02, 4, 2, 'brass'))
    # the doorways each keep a candle, very small, for after the lights go out
    for (x, y) in ((5.8, 1.0), (21.8, 1.0), (10.2, D - 1.0), (1.0, 10.2), (1.0, 21.8), (W - 1.0, 5.8)):
        R.parts.add(cyl(x, y, 0, 0.04, 0.1, 8, side='brass', top='brass'))
        candle(R, x, y, 0.04, h=0.1, r=0.02)


def hidden(R):
    """The corner room: its walls black and full height, like the hall's; a door ajar in its south face."""
    t = 0.3
    R.parts.add(box(BX, BY, 0, BX + t, D - T + 0.02, TOP, 'black', sides='black'))
    R.parts.add(box(BX + t, BY, 0, DX0, BY + t, TOP, 'black'))
    R.parts.add(box(DX1, BY, 0, W - T + 0.02, BY + t, TOP, 'black'))
    R.parts.add(box(DX0, BY, 2.15, DX1, BY + t, TOP, 'black'))
    R.parts.add(box(BX + t, BY + t, 3.3, W - T + 0.02, D - T + 0.02, 3.5, 'black', bottom='plaster'))
    # the door: a black leaf standing a little open, a thin brass line of a frame, one weak bulb over it
    leaf = box(0, 0, 0, DX1 - DX0 - 0.04, 0.04, 2.1, 'black')
    leaf.add(box(DX1 - DX0 - 0.18, -0.03, 0.95, DX1 - DX0 - 0.12, 0.0, 1.01, 'brass'))
    leaf.xform(0.9, DX0 + 0.02, BY + t + 0.02, 0)
    R.nocol.add(leaf)
    for (x0, x1, z0, z1) in ((DX0 - 0.05, DX0, 0, 2.2), (DX1, DX1 + 0.05, 0, 2.2), (DX0 - 0.05, DX1 + 0.05, 2.15, 2.2)):
        R.nocol.add(box(x0, BY - 0.01, z0, x1, BY + 0.01, z1, 'brass'))
    R.nocol.add(box((DX0 + DX1) / 2 - 0.05, BY - 0.25, 2.5, (DX0 + DX1) / 2 + 0.05, BY, 2.58, 'brass'))
    R.light(sphere((DX0 + DX1) / 2, BY - 0.28, 2.45, 0.05, 8, 4, 'e_dim'))
    # inside: the chairs, heaped against the walls, one upright in the middle facing the door
    rnd = random.Random(8)
    x0, y0, x1, y1 = BX + t, BY + t, W - T, D - T
    piles = [(x0, y0 + 2.2, x0 + 1.4, y1), (x0 + 1.4, y1 - 1.3, x1, y1), (x1 - 1.3, y0 + 1.3, x1, y1 - 1.3), (x0, y0, x0 + 0.9, y0 + 2.2)]
    for (a0, b0, a1, b1) in piles:
        R.col.add(box(a0, b0, 0, a1, b1, 2.6, 'tile'))
        n = int((a1 - a0) * (b1 - b0) * 5)
        for k in range(n):
            px, py = rnd.uniform(a0 + 0.25, a1 - 0.25), rnd.uniform(b0 + 0.25, b1 - 0.25)
            pz = rnd.uniform(0, 2.4) * (0.4 + 0.6 * rnd.random())
            c = chair_geo(0, 0, rnd.uniform(0, 6.3), rnd.choice(('walnut', 'oak', 'wood')), rnd.choice(('leather', 'oak', 'velvet')))
            c.xform(0, 0, 0, -0.5)
            c = orient(c, 0, rnd.uniform(-1.4, 1.4), rnd.uniform(-1.4, 1.4), px, py, pz + 0.5)
            R.nocol.add(c)
    mx, my = 29.4, 29.2
    chair(R, mx, my, -math.pi / 2, frame='oak', seat='oak')
    bulb(R, mx, my - 0.3, 2.3, r=0.07, m='e_dim', top=3.3)
    R.spot('plaque', x0 + 0.05, y0 + 1.2, 1.5, 0.0, text='RETURNED CHAIRS. Please do not sit.')
