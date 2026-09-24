"""The Heap: every bookcase in the room is empty, because every book is here, in one mountain in the
middle, under a skylight. It can be climbed. At the top someone has put an armchair and a lamp."""
import random
from lib import *
from kit_b import *

COVERS = ('leather', 'books', 'oxblood', 'green', 'velvet', 'walnut', 'leather', 'slate')


def make():
    R = Room('heap', 1, 1, res=1024)
    rnd = random.Random(7)
    H = TOP - 0.1
    shell(R, H, wall='tile', floor='floor', ceil='plaster')
    cx, cy = 8.0, 8.2
    # terraces of books: irregular twelve-sided steps, 0.4 m each, their risers real rows of spines
    NL, NS, STEP = 7, 12, 0.4
    rng = [rnd.uniform(-0.18, 0.18) for _ in range(NS)]
    for k in range(NL):
        z0, z1 = k * STEP, (k + 1) * STEP
        r = 5.1 - k * 0.64
        ox, oy = cx + 0.25 * math.sin(k * 1.3), cy + 0.2 * math.cos(k * 0.9)
        pts = []
        for i in range(NS):
            a = (i + 0.5 * (k % 2)) * 2 * math.pi / NS
            rr = r + rng[(i + k) % NS] * (1.0 if k < NL - 1 else 0.3)
            pts.append((ox + rr * math.cos(a), oy + rr * math.sin(a)))
        m = rnd.choice(('leather', 'oxblood', 'books'))
        R.parts.add(poly_prism(pts, z0 - (0.02 if k else 0.0), z1, side='books', top=m, bottom='books'))
        for i in range(NS):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % NS]
            L = math.hypot(x1 - x0, y1 - y0)
            fa = math.atan2(y1 - y0, x1 - x0) - math.pi / 2          # outward (polygon is counter-clockwise)
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            nx, ny = math.cos(fa), math.sin(fa)
            d = 0.26
            # back-left corner seen from the front = the end the shelf runs from, set back into the step
            bx, by = x1 - nx * (d - 0.03), y1 - ny * (d - 0.03)
            R.shelf(bx - ux * 0.06, by - uy * 0.06, z0 - 0.035, L - 0.12, fa, rows=1, row_h=STEP, depth=d + 0.02, frame='books', back=False, sides=False, crown=False, solid=False)
        # loose books lying about on the tread
        for j in range(int(9 - k)):
            a = rnd.uniform(0, 2 * math.pi)
            rr = r - 0.35 if k < NL - 1 else rnd.uniform(0.9, 1.2)
            x, y = ox + rr * math.cos(a), oy + rr * math.sin(a)
            t = rnd.choice((0.04, 0.05, 0.07))
            n = rnd.choice((1, 1, 2, 3))
            for q in range(n):
                R.nocol.add(box(-0.15, -0.1, z1 + q * t, 0.15, 0.1, z1 + (q + 1) * t, rnd.choice(COVERS), sides='ivory', skip=('-z',)).xform(a + rnd.uniform(-0.6, 0.6), x, y))
    # the summit: an armchair and a lamp
    tx, ty, tz = cx + 0.25 * math.sin((NL - 1) * 1.3), cy + 0.2 * math.cos((NL - 1) * 0.9), NL * STEP
    g = Geo()
    g.add(box(-0.42, -0.42, 0, 0.42, 0.42, 0.44, 'velvet', skip=('-z',)))
    g.add(box(-0.42, -0.42, 0.44, -0.24, 0.42, 1.05, 'velvet'))
    g.add(box(-0.24, -0.42, 0.44, 0.4, -0.28, 0.66, 'velvet'))
    g.add(box(-0.24, 0.28, 0.44, 0.4, 0.42, 0.66, 'velvet'))
    fa = -math.pi / 2 - 0.3
    R.nocol.add(g.xform(fa, tx, ty, tz))
    R.col.add(box(-0.42, -0.42, 0, 0.42, 0.42, 0.44, 'tile').xform(fa, tx, ty, tz))
    R.spot('sit', tx, ty, tz + 0.44, fa)
    lx, ly = tx + 0.55, ty + 0.35
    R.nocol.add(cyl(lx, ly, tz, tz + 1.55, 0.02, 5, side='brass', caps=False))
    R.nocol.add(cyl(lx, ly, tz + 1.55, tz + 1.8, 0.26, 14, side='green', top='green', bottom='green'))
    R.light(cyl(lx, ly, tz + 1.51, tz + 1.55, 0.2, 14, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.light(cyl(lx, ly, tz + 1.3, tz + 1.36, 0.05, 6, side='e_amber', top='e_amber', bottom='e_amber'))
    # the skylight over it
    R.cut(box(cx - 2.6, cy - 2.6, H - 0.05, cx + 2.6, cy + 2.6, H + 0.1, 'plaster'))
    R.light(box(cx - 2.5, cy - 2.5, H + 0.05, cx + 2.5, cy + 2.5, H + 0.08, 'e_sky'))
    # empty bookcases round the walls: frames only, not a book on them
    for (a, b) in SEGS:
        for (x0, y0, ang) in ((a, T, math.pi / 2), (b, C - T, -math.pi / 2), (T, b, 0.0), (C - T, a, math.pi)):
            gg = Geo()
            L, HH = b - a, 8 * 0.42 + 0.1
            gg.add(box(0, 0, 0, L, 0.02, HH, 'walnut', skip=('-y',)))
            for k in range(9):
                gg.add(box(0, 0.02, k * 0.42, L, 0.35, k * 0.42 + 0.035, 'walnut', skip=('-z',) if k == 0 else ()))
            for u in (0.0, L / 2, L):
                gg.add(box(u - 0.03, 0, 0, u + 0.03, 0.37, HH, 'walnut', skip=('-z',)))
            R.nocol.add(gg.xform(ang - math.pi / 2, x0, y0))
            R.col.add(box(0, 0, 0, L, 0.37, HH, 'tile').xform(ang - math.pi / 2, x0, y0))
    # two books left on the empty shelves, so it is not quite all of them
    R.shelf(4.0, T, 3 * 0.42 + 0.035, 0.3, '+y', rows=1, row_h=0.38, depth=0.3, frame='walnut', back=False, sides=False, crown=False)
    # lamps in the corners, low
    for (x, y) in ((1.6, 1.6), (C - 1.6, 1.6), (1.6, C - 1.6), (C - 1.6, C - 1.6)):
        pendant(R, x, y, 2.8, H, r=0.2, m='brass', em='e_lamp')
    loop(R, [(1.7, 1.7), (8, 1.7), (C - 1.7, 1.7), (C - 1.7, 8), (C - 1.7, C - 1.7), (8, C - 1.7), (1.7, C - 1.7), (1.7, 8)])
    R.spot('probe', 8, 2.0, 2.0)
    R.meta.update(label='The Heap', weight=4,
                  blurb='All the books from all the shelves, in one pile. It is quite stable. There is an armchair on the top, which raises the question of who carried it up.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
