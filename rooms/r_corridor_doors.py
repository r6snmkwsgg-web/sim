"""The Hall of Doors: a tall vaulted corridor lined both sides with doors, and above them a second
row of smaller doors nobody could reach. None of them open. Light shows under a few. Exit signs over others."""
from lib import *
from kit_b import *

X0, X1 = 5.5, 10.5          # the hall's side walls


def door(R, y, side, z=0.0, s=1.0, sign=False, glow=False, num=None):
    """A false door on the west (side=-1) or east (side=+1) wall of the hall, centred at y."""
    x = X0 if side < 0 else X1
    d = -side                   # into the hall
    g = Geo()
    w, h = 0.5 * s, 2.2 * s
    # casing, leaf, raised panels, a knob (built facing +x at x=0, then mirrored if needed)
    g.add(box(0, -w - 0.12 * s, z, 0.07, -w, z + h + 0.12 * s, 'walnut', skip=('-x',)))
    g.add(box(0, w, z, 0.07, w + 0.12 * s, z + h + 0.12 * s, 'walnut', skip=('-x',)))
    g.add(box(0, -w - 0.12 * s, z + h, 0.07, w + 0.12 * s, z + h + 0.14 * s, 'walnut', skip=('-x',)))
    g.add(box(0, -w, z, 0.035, w, z + h, 'oak', skip=('-x',)))
    for (z0, z1) in ((0.2, 0.95), (1.2, 2.0)):
        for (a, b) in ((-w + 0.1 * s, -0.04 * s), (0.04 * s, w - 0.1 * s)):
            g.add(box(0.035, a, z + z0 * s, 0.05, b, z + z1 * s, 'oak', skip=('-x',)))
    g.add(box(0.035, w - 0.14 * s, z + 1.02 * s, 0.09, w - 0.08 * s, z + 1.1 * s, 'brass'))
    if num:
        g.add(box(0.035, -0.08 * s, z + 1.6 * s, 0.045, 0.08 * s, z + 1.7 * s, 'brass', skip=('-x',)))
    if side > 0: g.xform(math.pi, 0, 0)
    g.xform(0, x, y)
    R.nocol.add(g)
    if sign:
        xa, xb = (x, x + 0.03) if d > 0 else (x - 0.03, x)
        R.light(box(xa, y - 0.18 * s, z + h + 0.22 * s, xb, y + 0.18 * s, z + h + 0.36 * s, 'e_exit'))
    if glow:   # light leaking under the door
        R.light(quad(y - w + 0.02, y + w - 0.02, x + d * 0.04, z + 0.0, z + 0.025, 'e_amber', '+x' if d > 0 else '-x'))


def make():
    R = Room('corridor_doors', 1, 1, res=1024)
    R.sockets(floor='floor', wall='plaster')
    H = 4.4
    pr = arch_profile(8, X1 - X0, 0, H, 24)
    R.cut(prism(pr, 'y', T - 0.02, C - T + 0.02, arch_mats(len(pr), 'floor', 'plaster')))
    # the side passages to the east and west doors, lined with books
    R.cut(box(T - 0.02, 6.5, 0, X0 + 0.05, 9.5, 3.4, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(X1 - 0.05, 6.5, 0, C - T + 0.02, 9.5, 3.4, 'plaster', bottom='floor', top='plaster'))
    for (a, b) in ((0.9, X0 - 0.3), (X1 + 0.3, C - 0.9)):
        bshelf(R, a, 6.5, 0, b - a, '+y', rows=7, frame='walnut')
        bshelf(R, b, 9.5, 0, b - a, '-y', rows=7, frame='walnut')
        pendant(R, (a + b) / 2, 8, 2.6, 3.4, r=0.16, m='brass', em='e_amber')
    # doors, two rows: full size below, half size above
    k = 0
    for side in (-1, 1):
        for y in (1.25, 2.75, 4.25, 5.75, 10.25, 11.75, 13.25, 14.75):
            door(R, y, side, 0.0, 1.0, sign=(k % 5 == 2), glow=(k % 7 == 3), num=True)
            door(R, y, side, 2.95, 0.55, sign=(k % 6 == 1), glow=False)
            k += 1
        for y in (0.5, 2.0, 3.5, 5.0, 11.0, 12.5, 14.0, 15.5):
            x = X0 + 0.02 if side < 0 else X1 - 0.02
            bulb(R, x, y, 2.3, 0.07, 'e_lamp')
    # a carpet runner with brass rods, and hanging lamps down the vault
    R.nocol.add(box(7.0, T, 0, 9.0, C - T, 0.012, 'carpet'))
    for k in range(9):
        y = 0.9 + k * 1.8
        R.nocol.add(box(6.95, y - 0.015, 0, 9.05, y + 0.015, 0.03, 'brass'))
    for y in (2.0, 5.0, 11.0, 14.0):
        pendant(R, 8, y, 3.7, H + 2.5, r=0.2, m='brass', em='e_lamp')
    a = loop(R, [(8, 1.2), (8, 7.0), (8, 9.0), (8, C - 1.2)], close=False)
    loop(R, [(1.2, 8), (6.6, 8.2), (9.4, 8.2), (C - 1.2, 8)], close=False)
    R.link(a[1], 5); R.link(a[2], 6)
    R.spot('probe', 8, 4.0, 1.8)
    R.meta.update(label='The Hall of Doors', weight=5,
                  blurb='Thirty-two doors and not one of them opens. The exit signs are very sure of themselves. Light shows under some of the doors, and once, you think, a shadow.')
    R.meta['box'] = [[T, 0, T], [C - T, H + 2.5, C - T]]
    return R
