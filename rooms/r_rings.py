"""The Rings: three concentric rings of bookcases, each broken by gaps that never line up with the
next, so the middle is a small round maze. Rings of light on the ceiling trace it. An armchair waits in the centre."""
from lib import *
from kit_b import *


def make():
    R = Room('rings', 1, 1, res=1024)
    H = 4.6
    shell(R, H, wall='tile', floor='floor', ceil='plaster')
    cx = cy = 8.0
    rows = 4
    rings = ((5.6, [0, 90, 180, 270], 17.0),
             (3.9, [45, 225], 13.0),
             (2.2, [135], 21.0))
    for (r, gaps, gh) in rings:
        n = max(6, int(round(2 * math.pi * r / 2.0)))
        for k in range(n):
            t0, t1 = k * 360.0 / n, (k + 1) * 360.0 / n
            tm = (t0 + t1) / 2
            if any(abs((tm - g + 180) % 360 - 180) < gh for g in gaps): continue
            a0, a1 = math.radians(t0), math.radians(t1)
            p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
            p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
            L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            fa = math.radians(tm)            # faces outward
            # shelf faces fa, extends along (sin fa, -cos fa): from p1 to p0
            bshelf(R, p1[0], p1[1], 0, L, fa, rows=rows, frame='walnut', depth=0.3, sides=False)
            # a plain panelled back on the inside
            R.nocol.add(box(0, -0.05, 0, L, 0.0, rows * 0.42 + 0.12, 'walnut', skip=('-z', '+y')).xform(fa - math.pi / 2, p1[0], p1[1]))
        # a ring of light over each ring's corridor
        rr = r + 0.85
        if r < 5: R.light(ring(cx, cy, H - 0.03, H - 0.01, rr - 0.05, rr + 0.05, 48, top='e_fluor', bottom='e_fluor', inner='e_fluor', outer='e_fluor'))
    R.light(ring(cx, cy, H - 0.03, H - 0.01, 6.55, 6.65, 48, top='e_fluor', bottom='e_fluor', inner='e_fluor', outer='e_fluor'))
    # the centre: a round rug, an armchair, a lamp, a single book on a small table
    R.nocol.add(cyl(cx, cy, 0, 0.012, 1.7, 32, side='carpet', top='carpet', bottom='carpet'))
    armchair(R, cx - 0.35, cy - 0.35, math.pi / 4, m='velvet')
    round_table(R, cx + 0.6, cy + 0.25, 0.3, 0.6, 'walnut')
    R.nocol.add(box(-0.12, -0.09, 0.6, 0.12, 0.09, 0.65, 'leather').xform(0.4, cx + 0.6, cy + 0.25))
    R.parts.add(cyl(cx - 0.9, cy + 0.6, 0, 0.04, 0.2, 12, side='brass', top='brass', bottom='brass'))
    R.nocol.add(cyl(cx - 0.9, cy + 0.6, 0.04, 1.5, 0.02, 5, side='brass', caps=False))
    R.nocol.add(cyl(cx - 0.9, cy + 0.6, 1.5, 1.75, 0.28, 16, side='green', top='green', bottom='green'))
    R.light(cyl(cx - 0.9, cy + 0.6, 1.46, 1.5, 0.22, 16, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.cut(cyl(cx, cy, H - 0.05, H + 0.6, 1.4, 40, side='plaster', top='plaster', bottom='plaster'))
    R.light(cyl(cx, cy, H + 0.52, H + 0.55, 1.4, 40, side='e_sky', top='e_sky', bottom='e_sky'))
    # shelves on the walls, round the outside
    wall_shelves(R, rows=8, frame='walnut', segs=((0.6, 5.0), (11.0, C - 0.6)))
    for (x, y) in ((1.7, 1.7), (C - 1.7, 1.7), (1.7, C - 1.7), (C - 1.7, C - 1.7)):
        pendant(R, x, y, 3.0, H, r=0.2, m='brass')
    # walks round the outermost corridor and outside the rings
    loop(R, [(cx + 6.75 * math.cos(k * math.pi / 4), cy + 6.75 * math.sin(k * math.pi / 4)) for k in range(8)])
    R.spot('probe', cx, cy + 4.7, 1.7)
    R.meta.update(label='The Rings', weight=5,
                  blurb='A maze, but a polite one: the shelves are low enough to see the middle, and the middle has a chair. Getting there is another matter.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
