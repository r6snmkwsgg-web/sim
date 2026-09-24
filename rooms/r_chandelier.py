"""The Chandelier: a ballroom with nobody in it. A brass chandelier of four tiers and a hundred small
flames fills the dome; below it, a polished marble floor for dancing; books all round the walls."""
from lib import *
from kit_c import *


def make():
    R = Room('chandelier', 1, 1, res=1024)
    R.sockets(floor='terrazzo', wall='tile')
    H = 5.2
    shell(R, H, floor='terrazzo', ceil='plaster')
    cx = cy = 8.0
    R.cut(sphere(cx, cy, 1.0, 6.45, 40, 12, 'plaster', lower=False))
    rb = math.sqrt(6.45 ** 2 - (H - 1.0) ** 2)
    R.parts.add(ring(cx, cy, H - 0.22, H - 0.02, rb - 0.02, rb + 0.25, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    # the floor: inlaid bands of dark stone and brass
    R.parts.add(ring(cx, cy, 0, 0.006, 3.3, 4.6, 40, top='slate', bottom='slate', inner='slate', outer='slate'))
    for k in range(8):   # a star in the middle
        a = k * math.pi / 4
        L = 1.6 if k % 2 == 0 else 0.9
        g = Geo(); ids = [g.vert(p) for p in ((0, -0.18, 0), (L, 0, 0), (0, 0.18, 0), (0, -0.18, 0.006), (L, 0, 0.006), (0, 0.18, 0.006))]
        for f, m in (((0, 2, 1), 'slate'), ((3, 4, 5), 'slate'), ((0, 1, 4, 3), 'slate'), ((1, 2, 5, 4), 'slate'), ((2, 0, 3, 5), 'slate')):
            g.face([ids[i] for i in f], 'slate' if k % 2 else 'brass', [(0, 0)] * len(f))
        R.parts.add(g.fix().xform(a, cx, cy))
    # the chandelier
    top = TOP + 0.05
    R.parts.add(cyl(cx, cy, 3.3, top, 0.05, 10, side='brass', caps=False))
    R.parts.add(sphere(cx, cy, 3.5, 0.32, 12, 6, 'brass'))
    R.parts.add(cyl(cx, cy, 3.0, 3.3, 0.06, 10, side='brass', top='brass', bottom='brass'))
    R.parts.add(sphere(cx, cy, 3.0, 0.09, 10, 5, 'brass'))
    R.parts.add(cyl(cx, cy, 7.2, top, 0.45, 20, side='gilt', top='gilt', bottom='gilt'))   # ceiling rose
    tiers = ((3.9, 2.6, 22), (4.6, 1.95, 16), (5.3, 1.3, 10), (5.95, 0.7, 6))
    for (z, r, n) in tiers:
        R.parts.add(ring(cx, cy, z - 0.035, z, r - 0.05, r + 0.05, 20, top='brass', bottom='brass', inner='brass', outer='brass'))
        R.parts.add(ring(cx, cy, z - 0.25, z - 0.21, r * 0.6 - 0.03, r * 0.6 + 0.03, 10, top='brass', bottom='brass', inner='brass', outer='brass'))
        for k in range(6):   # spokes from the stem
            a = k * math.pi / 3 + z
            R.parts.add(box(0.04, -0.018, z - 0.03, r, 0.018, z - 0.005, 'brass').xform(a, cx, cy))
            R.parts.add(slope_box(0.04, r * 0.6, -0.015, 0.015, z - 0.5, z - 0.25, z - 0.47, z - 0.22, 'brass').xform(a, cx, cy))
        for k in range(n):
            a = 2 * math.pi * (k + 0.5) / n
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            R.parts.add(cyl(x, y, z, z + 0.16, 0.024, 4, side='ivory', caps=False))
            R.light(sphere(x, y, z + 0.2, 0.05, 5, 3, 'e_lamp'))
            # a crystal drop between each pair of flames
            a2 = 2 * math.pi * k / n
            dx, dy = cx + r * math.cos(a2), cy + r * math.sin(a2)
            if k % 2 == 0:
                R.parts.add(cyl(dx, dy, z - 0.2, z - 0.035, 0.006, 3, side='chrome', caps=False))
                R.parts.add(sphere(dx, dy, z - 0.24, 0.035, 4, 2, 'chrome'))
    for k in range(4):   # chains to the ceiling
        a = k * math.pi / 2 + math.pi / 4
        x, y = cx + 2.55 * math.cos(a), cy + 2.55 * math.sin(a)
        Lh = 2.55 - 0.3
        R.nocol.add(slope_box(0, Lh, -0.012, 0.012, 3.9, 7.2, 3.93, 7.23, 'brass').xform(a + math.pi, x, y))
    # books all round, to the cornice
    wall_shelves(R, rows=11, frame='walnut')
    # gilt chairs round the edge of the floor, waiting
    for k in range(4):
        base = math.pi / 4 + k * math.pi / 2
        for da in (-0.2, 0.0, 0.2):
            a = base + da
            chair(R, cx + 5.3 * math.cos(a), cy + 5.3 * math.sin(a), a + math.pi, m='gilt', seat='velvet')
    # lamps over the doors, lit at night
    for (x, y) in ((8, T + 0.1), (8, C - T - 0.1), (T + 0.1, 8), (C - T - 0.1, 8)):
        R.light(box(x - 0.12, y - 0.1, 4.35, x + 0.12, y + 0.1, 4.47, 'e_amber'))
    # walkers: round the floor, and across it
    ring_ = navloop(R, [(cx + 4.2 * math.cos(k * math.pi / 4), cy + 4.2 * math.sin(k * math.pi / 4)) for k in range(8)])
    R.link(ring_[0], ring_[4]); R.link(ring_[2], ring_[6])
    for k, (x, y) in enumerate(((C - 1.4, 8), (8, C - 1.4), (1.4, 8), (8, 1.4))):
        R.link(ring_[k * 2], R.navpt(x, y))
    R.spot('probe', 8, 6.0, 1.7)
    R.meta.update(label='The Chandelier', weight=5,
                  blurb='A ballroom, with the chandelier lit and the chairs set out, and nobody. The floor has been polished for a dance that has been going to start for a very long time.')
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]
    return R
