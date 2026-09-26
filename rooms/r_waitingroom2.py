"""The Waiting Room: a tall nave full of chairs, hundreds of them, in rows, all facing one door at the far
end with a number over it in green light. Everybody has taken a ticket. Nobody is here. The door is
open a crack, and behind it there is a very small office, and another door, and another number."""
from kit_h10 import *

W = D = 32.0
YN = 27.6                         # the nave's north wall; the office is behind it
NX0, NX1 = 6.3, 25.7              # the nave between the arcades
JAMB, RISE = 5.0, 2.5
AZ = 4.8                          # the side aisles' ceiling
DW2, DH = 1.5, 4.0                # each leaf of the Door
OX0, OX1, OY0, OY1, OH = 12.6, 19.4, YN + 0.3, D - T - 0.05, 3.6   # the office


def make():
    R = Room('waitingroom2', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    vault_cut(R, 'y', 16.0, NX1 - NX0 + 0.04, T - 0.02, YN, 0.0, JAMB, rise=RISE, m='plaster', floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, NX0 + 0.1, YN, AZ, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(NX1 - 0.1, T - 0.02, 0, W - T + 0.02, YN, AZ, 'tile', bottom='terrazzo', top='plaster'))
    ribs(R, 'y', 16.0, NX1 - NX0, [4.0 * k for k in range(1, 7)], 0.0, JAMB, rise=RISE, d=0.3, t=0.4)
    tunnel_y(R, 8.0, YN - 0.05, D - T - 0.5, floor='terrazzo')
    tunnel_y(R, 24.0, YN - 0.05, D - T - 0.5, floor='terrazzo')
    arcades(R)
    aisles(R)
    chairs(R)
    door(R)
    office(R)
    lights(R)
    navloop(R, [(16.0, 2.2), (16.0, 14.0), (16.0, 25.8), (10.0, 26.0), (3.0, 24.0), (3.0, 16.0), (3.0, 8.0), (3.0, 2.2), (10.0, 2.4)])
    a = R.navpt(29.0, 8.0); b = R.navpt(29.0, 24.0); c = R.navpt(22.0, 26.0); d = R.navpt(22.0, 2.4)
    R.link(0, d, a, b, c, 2)
    secret(R, 16.0, 29.8, 0.0, 'Behind the Door',
           'Behind the door everybody is waiting for there is a small office: a desk, a bell, a roll of tickets, a lever to change the number. And another door, with another number over it, one less.')
    fx(R, 'dust', [NX0, 4.0, 1.0, NX1, 24.0, 6.5])
    return done(R, 'The Waiting Room', weight=5, probe=(16.0, 5.0, 2.4),
                blurb='Hundreds of chairs, all facing one door, and over the door a number in green light. You look down: you are holding a ticket. It is not your number. It is never your number.')


# ---------------------------------------------------------------------------
def arcades(R):
    for x in (NX0, NX1):
        for k in range(8):
            y = 1.6 + k * 3.6
            if y > YN - 1.0: break
            R.parts.add(box(x - 0.35, y - 0.35, 0, x + 0.35, y + 0.35, AZ, 'tile', skip=('-z', '+z')))
            R.parts.add(box(x - 0.45, y - 0.45, 0, x + 0.45, y + 0.45, 0.4, 'tile', skip=('-z',)))
            R.parts.add(box(x - 0.48, y - 0.48, AZ - 0.35, x + 0.48, y + 0.48, AZ, 'tile', skip=('+z',)))
            sconce(R, x + (0.36 if x < 16 else -0.36), y, 2.9, 0.0 if x < 16 else math.pi, m='e_lamp')
        # the wall over the arcade: a cornice
        R.parts.add(box(x - 0.4, T, AZ - 0.1, x + 0.4, YN, AZ + 0.25, 'tile'))


def aisles(R):
    rows = 10
    for (x, face) in ((T, '+x'), (W - T, '-x')):
        for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, YN - 0.3)):
            sh(R, face, x, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, NX0 - 0.5), (NX1 + 0.5, W - 0.6)):
        sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
    # reading desks along the aisles with green lamps, each with its own chair
    for x0 in (2.1, W - 3.2):
        for y in (4.0, 12.0, 16.0, 20.0):
            R.parts.add(ltable(x0, y - 0.9, x0 + 1.1, y + 0.9, 0.78, 'walnut', top='leather'))
            llamp(R, x0 + 0.55, y, 0.78, math.pi / 2, lit=(y != 16.0), m='e_lamp')
            cx = x0 + 1.6 if x0 < 16 else x0 - 0.5
            R.parts.add(lchair(cx, y, math.pi if x0 < 16 else 0.0))
            R.spot('sit', cx, y, 0.48, math.pi if x0 < 16 else 0.0)
    # over the south doors a short run of books, over the nave's back wall a gilt clock
    sh(R, '+y', T, 9.9, 22.1, rows=6, frame='walnut')
    sh(R, '+y', T, 6.1, 9.9, z=3.8, rows=2, frame='walnut')
    sh(R, '+y', T, 22.1, 25.9, z=3.8, rows=2, frame='walnut')


def chairs(R):
    rs = rng(31)
    g = Geo()
    y = 4.6
    row = 0
    while y < 24.2:
        for (a, b) in ((NX0 + 0.8, 15.1), (16.9, NX1 - 0.8)):
            n = int((b - a) / 0.68)
            for k in range(n):
                x = a + (b - a) * (k + 0.5) / n
                j = rs.uniform(-0.03, 0.03)
                g.add(lchair(x + j, y + j, math.pi / 2 + rs.uniform(-0.04, 0.04), frame='walnut', seat='green', back_h=1.0))
        y += 1.08; row += 1
    R.parts.add(g)
    for (x, y) in ((10.0, 4.6), (21.4, 13.24), (16.9 + 0.3, 20.8)):
        R.spot('sit', x, y, 0.48, math.pi / 2)
    # tickets dropped in the aisle, and the machine that gives them out by the south doors
    tk = Geo()
    for k in range(14):
        tk.add(box(-0.05, -0.03, 0, 0.05, 0.03, 0.003, 'ivory').xform(rs.uniform(0, 3), rs.uniform(15.3, 16.7), rs.uniform(3.0, 25.0), 0.0))
    R.nocol.add(tk)
    R.parts.add(box(12.9, 2.6, 0, 13.3, 3.0, 1.3, 'oxblood'))
    R.parts.add(box(12.85, 2.55, 1.3, 13.35, 3.05, 1.36, 'brass'))
    R.light(box(12.95, 3.0, 1.0, 13.25, 3.02, 1.1, 'e_digit'))
    R.nocol.add(box(12.98, 3.0, 0.82, 13.22, 3.06, 0.86, 'ivory'))


def door(R):
    """The Door, at the head of the nave: tall, double, one leaf open a crack; the number over it."""
    cx = 16.0
    R.cut(box(cx - DW2 - 0.02, YN - 0.1, 0, cx + DW2 + 0.02, OY0 + 0.05, DH, 'walnut', bottom='terrazzo', top='walnut'))
    # the frame: columns either side, a pediment, the number box
    g = Geo()
    for s_ in (-1, 1):
        x = cx + s_ * (DW2 + 0.35)
        g.add(box(x - 0.3, YN - 0.5, 0, x + 0.3, YN, 0.4, 'tile', skip=('-z',)))
        g.add(cyl(x, YN - 0.25, 0.4, DH + 0.6, 0.22, 16, side='tile', caps=False))
        g.add(box(x - 0.3, YN - 0.5, DH + 0.6, x + 0.3, YN, DH + 0.85, 'tile'))
    g.add(box(cx - DW2 - 0.7, YN - 0.55, DH + 0.85, cx + DW2 + 0.7, YN, DH + 1.15, 'tile'))
    g.add(box(cx - DW2 - 0.1, YN - 0.12, DH, cx + DW2 + 0.1, YN, DH + 0.2, 'walnut'))
    # the display: a black box, green digits
    g.add(box(cx - 1.0, YN - 0.3, DH + 1.3, cx + 1.0, YN, DH + 2.2, 'black'))
    g.add(box(cx - 1.08, YN - 0.32, DH + 1.24, cx + 1.08, YN - 0.28, DH + 2.26, 'brass'))
    R.parts.add(g)
    for i, ch in enumerate('482'):
        seg_digit(R, cx - 0.78 + i * 0.55, YN - 0.33, DH + 1.42, ch, -math.pi / 2, s=0.62)
    # the leaves: the right one shut, the left one standing open into the office
    for s_ in (-1, 1):
        lf = door_leaf(DW2 - 0.02, DH - 0.02, 'walnut', 'oak')
        if s_ < 0:
            rot(lf, 'z', 1.15)                                  # swung in, hinged at the west jamb
            lf.xform(0, cx - DW2, YN + 0.1, 0.0)
        else:
            lf.xform(0, cx + 0.01, YN + 0.05, 0.0)
        R.parts.add(lf)


def office(R):
    R.cut(box(OX0, OY0, 0, OX1, OY1, OH, 'damask', bottom='floor', top='plaster'))
    # the desk facing the door, the chair behind it, the bell, the roll of tickets, the lever
    R.parts.add(ltable(14.9, 30.3, 17.1, 31.0, 0.78, 'walnut', top='leather'))
    R.parts.add(lchair_legs(16.0, 31.2, -math.pi / 2))
    R.spot('sit', 16.0, 31.2, 0.48, -math.pi / 2)
    R.nocol.add(cyl(15.3, 30.55, 0.78, 0.8, 0.06, 10, side='brass', top='brass'))
    R.nocol.add(sphere(15.3, 30.55, 0.82, 0.045, 8, 4, 'brass', lower=False))
    R.nocol.add(cyl(16.6, 30.6, 0.78, 0.9, 0.09, 10, side='ivory', top='ivory'))
    llamp(R, 16.1, 30.8, 0.78, 0.0, lit=True, m='e_amber')
    R.parts.add(box(OX1 - 0.5, 30.9, 0, OX1 - 0.3, 31.1, 1.0, 'iron'))
    R.nocol.add(beam((OX1 - 0.4, 31.0, 1.0), (OX1 - 0.55, 30.8, 1.6), 0.05, 'brass'))
    R.nocol.add(sphere(OX1 - 0.55, 30.8, 1.62, 0.07, 8, 4, 'oxblood'))
    # pigeonholes of tickets, a clock, the second door with its number
    sh(R, '+x', OX0, OY0 + 0.3, OY1 - 0.2, rows=7, frame='walnut', depth=0.3)
    g = Geo()
    g.add(box(OX1 - 0.06, 29.2, 0, OX1, 30.4, 2.2, 'walnut'))
    g.add(box(OX1 - 0.1, 29.1, 2.2, OX1, 30.5, 2.3, 'walnut'))
    g.add(box(OX1 - 0.25, 29.3, 2.45, OX1, 30.3, 2.95, 'black'))
    g.add(box(OX1 - 0.09, 30.2, 1.0, OX1 - 0.06, 30.28, 1.06, 'brass'))
    R.parts.add(g)
    for i, ch in enumerate('481'):
        seg_digit(R, OX1 - 0.26, 30.2 - i * 0.3, 2.55, ch, math.pi, s=0.32)
    rug(R, 14.0, 28.4, 18.0, 30.0, m='carpet', border='gilt')
    bulb(R, 16.0, 29.4, OH - 0.6, r=0.08, m='e_lamp', top=OH)
    R.spot('plaque', 16.0, 30.6, 0.8, -math.pi / 2, text='NOW SERVING 482. Please wait until your number is called.')
    a, b = R.navpt(14.0, 29.0), R.navpt(18.0, 29.0)
    R.link(a, b)


def lights(R):
    for y in (6.0, 12.0, 18.0, 23.0):
        for x in (11.0, 21.0):
            pendant(R, x, y, 4.2, JAMB + 1.8, r=0.24)
    for (x, y) in ((1.6, 1.6), (W - 1.6, 1.6), (1.6, YN - 1.2), (W - 1.6, YN - 1.2)):
        floor_lamp(R, x, y, 1.6, m='e_amber')
