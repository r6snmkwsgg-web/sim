"""The Little Theatre: a proscenium stage with heavy red curtains drawn back, footlights burning, and
on the stage one armchair under one light. Rows of seats face it. The north door comes in backstage."""
from lib import *
from kit_b import *


def pleats(R, x0, x1, y0, z0, z1, depth=0.22, w=0.3):
    """A curtain hanging in folds along x at y0 (it bulges toward -y)."""
    n = max(1, int((x1 - x0) / w))
    w = (x1 - x0) / n
    for k in range(n):
        d = depth if k % 2 == 0 else depth * 0.45
        R.nocol.add(box(x0 + k * w, y0 - d, z0, x0 + (k + 1) * w, y0, z1, 'velvet'))


def make():
    R = Room('theatre', 1, 1, res=1024)
    H = 7.2
    shell(R, H, wall='oxblood', floor='floor', ceil='plaster')
    SZ, Y0, Y1 = 0.76, 10.4, 13.4           # stage height, front edge, back edge
    # the stage
    R.parts.add(box(T, Y0, 0, C - T, Y1, SZ, 'walnut', top='floor'))
    # proscenium: a wall with a great opening, gilt edged
    PX0, PX1, PZ = 2.0, 14.0, 5.0
    R.parts.add(box(T, Y0 - 0.4, 0, PX0, Y0, H, 'oxblood', skip=('-z',)))
    R.parts.add(box(PX1, Y0 - 0.4, 0, C - T, Y0, H, 'oxblood', skip=('-z',)))
    R.parts.add(box(PX0, Y0 - 0.4, PZ, PX1, Y0, H, 'oxblood', bottom='gilt'))
    for (a, b) in ((PX0 - 0.15, PX0), (PX1, PX1 + 0.15)):
        R.nocol.add(box(a, Y0 - 0.46, 0, b, Y0 - 0.4, PZ + 0.15, 'gilt'))
    R.nocol.add(box(PX0 - 0.15, Y0 - 0.46, PZ, PX1 + 0.15, Y0 - 0.4, PZ + 0.15, 'gilt'))
    R.nocol.add(vdisk(8, Y0 - 0.45, PZ + 0.95, 0.55, 0.08, 'y', 'gilt', 20))       # a medallion, a mask with no face
    # the main curtains, drawn back, and a valance
    pleats(R, PX0, PX0 + 1.3, Y0 + 0.3, SZ, PZ)
    pleats(R, PX1 - 1.3, PX1, Y0 + 0.3, SZ, PZ)
    pleats(R, PX0, PX1, Y0 + 0.3, PZ - 0.9, PZ, depth=0.16, w=0.4)
    # the backdrop and the wings
    pleats(R, 4.6, 11.4, Y1 + 0.02, SZ, 6.2, depth=0.2)
    for x in (2.5, C - 2.5 - 1.3):
        pleats(R, x, x + 1.3, 12.0, SZ, 6.2, depth=0.18)
    # stairs: up to the stage at the front corners, down to backstage at the back corners
    for x in (3.4, C - 3.4 - 1.0):
        R.flight(x, Y0 - 1.25, 0, 1.0, 4, 0.19, 0.31, '+y', m='walnut', side='walnut')
    for x in (0.6, C - 0.6 - 1.4):
        R.flight(x, Y1 + 1.25, 0, 1.4, 4, 0.19, 0.31, '-y', m='walnut', side='walnut')
    # backstage: a low rail along the back of the stage between the stairs
    R.parts.add(balustrade(2.1, Y1, C - 2.1, Y1 + 0.12, SZ, 0.95, 'walnut', 'brass'))
    # footlights along the stage edge, and the one light on the chair
    for k in range(16):
        x = PX0 + 0.5 + k * (PX1 - PX0 - 1.0) / 15
        R.nocol.add(box(x - 0.14, Y0 + 0.02, SZ, x + 0.14, Y0 + 0.2, SZ + 0.1, 'brass', skip=('-z',)))
        R.light(box(x - 0.12, Y0 + 0.2, SZ + 0.02, x + 0.12, Y0 + 0.21, SZ + 0.1, 'e_pool'))
    armchair(R, 8, 11.9, -math.pi / 2, m='velvet')
    R.parts.add(cyl(9.1, 11.9, SZ, SZ + 0.04, 0.2, 12, side='brass', top='brass', bottom='brass'))
    R.nocol.add(cyl(9.1, 11.9, SZ + 0.04, SZ + 1.5, 0.02, 5, side='brass', caps=False))
    R.nocol.add(cyl(9.1, 11.9, SZ + 1.5, SZ + 1.72, 0.25, 14, side='green', top='green', bottom='green'))
    R.light(cyl(9.1, 11.9, SZ + 1.46, SZ + 1.5, 0.2, 14, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.nocol.add(box(-0.14, -0.1, SZ, 0.14, 0.1, SZ + 0.05, 'leather').xform(0.3, 7.3, 11.3))
    R.cut(cyl(8, 11.9, H - 0.05, H + 0.4, 0.5, 24, side='black', top='black', bottom='black'))
    R.light(cyl(8, 11.9, H + 0.3, H + 0.33, 0.45, 24, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # seats: five rows in two blocks, velvet
    for j in range(5):
        y = 3.2 + j * 1.05
        for (a, b) in ((2.6, 6.9), (9.1, 13.4)):
            R.parts.add(box(a, y - 0.25, 0, b, y + 0.25, 0.45, 'walnut', top='velvet', skip=('-z',)))
            R.parts.add(box(a, y - 0.35, 0.45, b, y - 0.25, 1.0, 'velvet', bottom='walnut'))
            n = int((b - a) / 0.54)
            for k in range(n + 1):
                x = a + k * (b - a) / n
                R.nocol.add(box(x - 0.03, y - 0.3, 0.45, x + 0.03, y + 0.22, 0.68, 'walnut'))
                if k < n: R.spot('sit', x + (b - a) / n / 2, y, 0.45, math.pi / 2)
    # a book left on one seat
    R.nocol.add(box(-0.14, -0.1, 0.45, 0.14, 0.1, 0.5, 'leather').xform(0.2, 4.4, 5.3))
    # books along the side walls of the house, and backstage
    for sd in 'WE':
        wall_shelves(R, rows=8, frame='walnut', sides=sd, segs=((0.6, 6.2),))
    wall_shelves(R, rows=8, frame='walnut', sides='N', segs=((2.4, 6.0), (10.0, C - 2.4)))
    # a chandelier over the seats, and sconces
    R.nocol.add(cyl(8, 5.3, 4.2, H, 0.02, 5, side='iron', caps=False))
    R.nocol.add(ring(8, 5.3, 4.15, 4.22, 0.8, 0.88, 24, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    for k in range(10):
        a = k * math.pi / 5
        bulb(R, 8 + math.cos(a) * 0.84, 5.3 + math.sin(a) * 0.84, 4.32, 0.06)
    for y in (2.4, 5.2):
        for x in (T + 0.12, C - T - 0.12):
            bulb(R, x, y, 3.9, 0.08, 'e_amber')
    loop(R, [(8, 1.8), (8, 8.9), (1.6, 8.6), (1.8, 1.8), (8, 1.8), (C - 1.8, 1.8), (C - 1.6, 8.6), (8, 8.9)], close=False)
    b = loop(R, [(8, C - 1.2), (4.8, C - 1.1), (C - 4.8, C - 1.1)], close=False)
    R.link(b[0], b[2])
    R.spot('probe', 8, 8.6, 2.0)
    R.meta.update(label='The Little Theatre', weight=4,
                  blurb='The house is dark and the footlights are up. There is an armchair on the stage, and a book on the armchair. You have the feeling you are expected to go on.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
