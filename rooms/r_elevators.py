"""The Lift Lobby: polished marble, twelve brass lift doors set into the walls, their call buttons lit,
their dials each stopped at a different floor. They never come. A directory board lists the floors."""
from lib import *
from kit_b import *


def lift(R, c, side):
    """A lift door centred at c along a west ('W') or east ('E') wall."""
    x = T if side == 'W' else C - T
    s = 1 if side == 'W' else -1            # into the room
    fx = lambda d: x + s * d                 # a distance into the room from the wall face
    lo = lambda a, b: (min(fx(a), fx(b)), max(fx(a), fx(b)))
    # recess cut into the wall, door panels at its back
    x0, x1 = lo(-0.22, 0.02)
    R.cut(box(x0, c - 0.7, 0, x1, c + 0.7, 2.55, 'brass', bottom='terrazzo'))
    a0, a1 = lo(-0.2, -0.17)
    R.parts.add(box(a0, c - 0.62, 0, a1, c - 0.01, 2.5, 'brass', skip=('-z',)))
    R.parts.add(box(a0, c + 0.01, 0, a1, c + 0.62, 2.5, 'brass', skip=('-z',)))
    for d in (-1, 1):   # a raised panel on each leaf
        b0, b1 = lo(-0.17, -0.15)
        R.nocol.add(box(b0, c + d * 0.31 - 0.2, 0.3, b1, c + d * 0.31 + 0.2, 2.2, 'bronze', skip=('-z',)))
    # the surround
    f0, f1 = lo(0.0, 0.08)
    R.parts.add(box(f0, c - 0.82, 0, f1, c - 0.7, 2.67, 'brass', skip=('-z',)))
    R.parts.add(box(f0, c + 0.7, 0, f1, c + 0.82, 2.67, 'brass', skip=('-z',)))
    R.parts.add(box(f0, c - 0.82, 2.55, f1, c + 0.82, 2.67, 'brass'))
    # the dial: a brass half-disc with a lamp at the floor it has stopped at
    pr = [(c + 0.42 * math.cos(math.pi * k / 12), 2.85 + 0.42 * math.sin(math.pi * k / 12)) for k in range(13)]
    d0, d1 = lo(0.0, 0.05)
    R.nocol.add(prism(pr, 'x', d0, d1, 'brass', cap='brass'))
    h = int(abs(math.sin(c * 12.9898 + (0 if side == 'W' else 3.1)) * 43758.5453) % 1 * 9)
    for k in range(9):
        a = math.pi * (k + 0.5) / 9
        py, pz = c - 0.33 * math.cos(a) * (1 if side == 'W' else -1), 2.85 + 0.33 * math.sin(a)
        ex = fx(0.055)
        if k == h: R.light(quad(py - 0.03, py + 0.03, ex, pz - 0.03, pz + 0.03, 'e_amber', '+x' if s > 0 else '-x'))
        else: R.nocol.add(quad(py - 0.02, py + 0.02, ex, pz - 0.02, pz + 0.02, 'black', '+x' if s > 0 else '-x'))
    # call buttons beside the door
    bp = c + 1.05 * (1 if side == 'W' else -1)
    b0, b1 = lo(0.0, 0.03)
    R.nocol.add(box(b0, bp - 0.08, 1.0, b1, bp + 0.08, 1.4, 'brass'))
    R.light(quad(bp - 0.035, bp + 0.035, fx(0.035), 1.25, 1.32, 'e_amber', '+x' if s > 0 else '-x'))
    R.nocol.add(quad(bp - 0.035, bp + 0.035, fx(0.035), 1.08, 1.15, 'black', '+x' if s > 0 else '-x'))


def make():
    R = Room('elevators', 1, 1, res=1024)
    H = 6.0
    R.sockets(floor='terrazzo', wall='slate')
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, H, 'slate', bottom='terrazzo', top='plaster'))
    # coffered ceiling with a cove of light round a raised centre
    R.cut(box(2.5, 2.5, H - 0.05, C - 2.5, C - 2.5, H + 0.6, 'plaster'))
    R.light(box(2.55, 2.55, H + 0.02, C - 2.55, 2.62, H + 0.08, 'e_fluor'))
    R.light(box(2.55, C - 2.62, H + 0.02, C - 2.55, C - 2.55, H + 0.08, 'e_fluor'))
    R.light(box(2.55, 2.62, H + 0.02, 2.62, C - 2.62, H + 0.08, 'e_fluor'))
    R.light(box(C - 2.62, 2.62, H + 0.02, C - 2.55, C - 2.62, H + 0.08, 'e_fluor'))
    # marble cornice and a brass band at door height
    for (x0, y0, x1, y1) in ((T, T, C - T, T + 0.1), (T, C - T - 0.1, C - T, C - T), (T, T, T + 0.1, C - T), (C - T - 0.1, T, C - T, C - T)):
        R.nocol.add(box(x0, y0, H - 0.4, x1, y1, H, 'terrazzo'))
    # six lifts on each side wall
    for c in (1.6, 3.4, 5.2, 10.8, 12.6, 14.4):
        lift(R, c, 'W')
        lift(R, c, 'E')
    # the directory board on the north wall, west of the door; books to the east
    R.parts.add(box(1.0, C - T - 0.08, 0.9, 5.8, C - T, 4.6, 'walnut'))
    R.nocol.add(box(1.15, C - T - 0.1, 1.05, 5.65, C - T - 0.08, 4.45, 'slate', skip=('+y',)))
    for j in range(22):
        z = 1.2 + j * 0.145
        for i in range(2):
            x = 1.35 + i * 2.2
            L = 1.1 + 0.6 * abs(math.sin(j * 1.7 + i * 2.1))
            R.nocol.add(quad(x, x + L, C - T - 0.105, z, z + 0.05, 'ivory', '-y'))
            R.nocol.add(quad(x + 1.9, x + 2.0, C - T - 0.105, z, z + 0.05, 'ivory', '-y'))
    R.light(box(1.2, C - T - 0.5, 4.75, 5.6, C - T - 0.42, 4.8, 'e_lamp'))
    R.nocol.add(box(1.15, C - T - 0.55, 4.8, 5.65, C - T, 4.86, 'brass'))
    bshelf(R, C - 0.6, C - T, 0, 5.6, '-y', rows=9, frame='walnut')
    wall_shelves(R, rows=9, frame='walnut', sides='S')
    # the island: marble benches round a planter with a palm
    R.parts.add(box(6.3, 6.3, 0, 9.7, 9.7, 0.45, 'terrazzo', skip=('-z',)))
    R.parts.add(box(6.8, 6.8, 0.45, 9.2, 9.2, 0.75, 'slate'))
    R.nocol.add(box(6.25, 6.25, 0.4, 9.75, 9.75, 0.46, 'brass', skip=('-z',)))
    palm(R, 8, 8, 0.75, 3.6, pot='brass', n=11, seed=0.4)
    for k in range(4):
        a = k * math.pi / 2
        for d in (-1.0, 0.0, 1.0):
            px, py = 8 + math.cos(a) * 1.5 - math.sin(a) * d, 8 + math.sin(a) * 1.5 + math.cos(a) * d
            R.spot('sit', px, py, 0.45, a)
    # benches along the lifts, facing them
    for y0, y1 in ((2.0, 4.8), (11.2, 14.0)):
        for x, f in ((3.3, math.pi), (C - 3.3, 0.0)):
            bench(R, x - 0.25, y0, x + 0.25, y1, 'walnut', spots=False)
            for k in range(3):
                R.spot('sit', x, y0 + 0.47 + k * (y1 - y0 - 0.94) / 2, 0.45, f)
    # tall lamps at the corners of the island
    for (x, y) in ((5.0, 5.0), (11.0, 5.0), (5.0, 11.0), (11.0, 11.0)):
        R.parts.add(cyl(x, y, 0, 0.06, 0.25, 12, side='brass', top='brass', bottom='brass'))
        R.parts.add(cyl(x, y, 0.06, 2.3, 0.03, 6, side='brass', caps=False))
        R.light(sphere(x, y, 2.5, 0.2, 12, 6, 'e_lamp'))
    loop(R, [(4.4, 4.4), (8, 4.4), (C - 4.4, 4.4), (C - 4.4, 8), (C - 4.4, C - 4.4), (8, C - 4.4), (4.4, C - 4.4), (4.4, 8)])
    loop(R, [(1.5, 8), (4.4, 8)], close=False)
    loop(R, [(C - 1.5, 8), (C - 4.4, 8)], close=False)
    R.link(R.navpt(8, 1.6), 1)
    R.link(R.navpt(8, C - 1.6), 5)
    R.spot('probe', 8, 4.0, 1.8)
    R.meta.update(label='The Lift Lobby', weight=4,
                  blurb='You press the button. It lights. Somewhere far above, or below, something begins to move, and keeps moving, and never arrives.')
    R.meta['box'] = [[T, 0, T], [C - T, H + 0.6, C - T]]
    return R
