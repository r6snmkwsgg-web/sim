"""The Lecture Theatre: two banks of steep stepped seating falling toward a stage and blackboards
the size of the wall, still covered in someone's working. A trench of an aisle runs between the banks."""
from lib import *
from kit_a import *

H = TOP - 0.1
Y_FRONT = 10.6           # front of the lowest tier
NT, TD, TR = 8, 1.0, 0.42   # tiers, tier depth, tier rise


def make():
    R = Room('lecture', 1, 1, res=1024)
    shell(R, wall='ivory', floor='floor', ceil='plaster', h=H)
    banks = ((2.6, 6.4, +1), (9.6, 13.4, -1))   # x0, x1, which side the stepped walk strip is on (+1: east edge)
    for (x0, x1, s) in banks:
        wx0, wx1 = (x1 - 0.9, x1) if s > 0 else (x0, x0 + 0.9)     # walk strip
        bx0, bx1 = (x0 + 0.1, wx0) if s > 0 else (wx1, x1 - 0.1)    # benches
        for k in range(1, NT + 1):
            ya = Y_FRONT - TD * k; yb = ya + TD; z = TR * k
            y_lo = T if k == NT else ya
            R.parts.add(box(x0, y_lo, 0, x1, yb, z, 'oak', top='floor', skip=('-z',)))
            # a half step in the walk strip so the climb is 0.21 at a time
            zp = TR * (k - 1)
            R.parts.add(box(wx0, yb, zp, wx1, yb + 0.5, zp + TR / 2, 'oak', top='floor', skip=('-z',)))
            # the bench at the back of the tier, the desk at its front edge
            if True:
                R.parts.add(box(bx0, ya + 0.05, z, bx1, ya + 0.45, z + 0.44, 'walnut', top='leather'))
                R.parts.add(box(bx0, ya, z, bx1, ya + 0.05, z + 0.9, 'walnut'))
                R.parts.add(box(bx0, yb - 0.32, z, bx1, yb - 0.02, z + 0.74, 'walnut', top='oak'))
                R.spot('sit', (bx0 + bx1) / 2, ya + 0.25, z + 0.44, math.pi / 2)
            # rails on both long edges of the bank, stepping down with the tiers
            ylo = T + 0.1 if k == NT else ya
            for xe in (x0 + 0.06, x1 - 0.06):
                rail(R, xe, ylo, xe, yb, z, post=1.05)
    # books stepping up the flanks of the banks, along the side corridors and the aisle
    for (x0, x1, s) in banks:
        for k in range(1, NT + 1):
            ya = Y_FRONT - TD * k; yb = ya + TD; z = TR * k
            rows = int((z - 0.12) / 0.42)
            if rows < 1: continue
            spans = [(ya, yb)] + ([(T + 0.1, ya)] if k == NT else [])
            for (a, b) in spans:
                if b < 6.3 or a > 9.7:
                    sh(R, '-x' if s > 0 else '+x', x0 if s > 0 else x1, a + 0.02, b - 0.02, rows=rows, depth=0.3, frame='walnut', crown=False)
                if a >= 2.6:
                    sh(R, '+x' if s > 0 else '-x', x1 if s > 0 else x0, a + 0.02, b - 0.02, rows=rows, depth=0.3, frame='walnut', crown=False)
    # the stage: a raised lip and a long bench-desk, blackboards covering the north wall
    yN = C - T
    R.parts.add(box(3.0, 12.0, 0, 6.2, 12.8, 0.92, 'walnut', top='oak'))
    R.parts.add(box(9.8, 12.0, 0, 13.0, 12.8, 0.92, 'walnut', top='oak'))
    boards = [(1.0, 5.8, 0.9, 4.0), (10.2, 15.0, 0.9, 4.0), (1.0, 15.0, 4.45, 7.15)]
    for (a, b, z0, z1) in boards:
        R.parts.add(box(a - 0.08, yN - 0.06, z0 - 0.08, b + 0.08, yN, z1 + 0.08, 'oak'))
        R.parts.add(box(a, yN - 0.08, z0, b, yN - 0.06, z1, 'blackboard'))
        R.parts.add(box(a, yN - 0.18, z0 - 0.1, b, yN - 0.06, z0 - 0.06, 'oak'))
    # someone's working, in chalk: lines of short strokes, a boxed result, a diagram
    import random
    rnd = random.Random(7)
    for (a, b, z0, z1) in boards:
        z = z1 - 0.25
        while z > z0 + 0.25:
            x = a + 0.2 + rnd.random() * 0.4
            while x < b - 0.5:
                L = 0.05 + rnd.random() * 0.25
                if rnd.random() < 0.85:
                    R.nocol.add(box(x, yN - 0.085, z - 0.012, x + L, yN - 0.08, z + 0.012, 'ivory', skip=('+y', '-x', '+x', '-z', '+z')))
                    if rnd.random() < 0.25: R.nocol.add(box(x + L * 0.4, yN - 0.085, z - 0.06, x + L * 0.4 + 0.02, yN - 0.08, z + 0.06, 'ivory', skip=('+y', '-x', '+x', '-z', '+z')))
                x += L + 0.06 + (0.3 if rnd.random() < 0.12 else 0)
                if rnd.random() < 0.08: break
            z -= 0.3 + (0.25 if rnd.random() < 0.2 else 0)
    cx, cz = 12.3, 5.8        # a large circle and its radius on the upper board
    R.nocol.add(xz_plate(circle_pts(cx, cz, 0.93, 40), yN - 0.083, yN - 0.081, 'ivory'))
    R.nocol.add(xz_plate(circle_pts(cx, cz, 0.9, 40), yN - 0.086, yN - 0.082, 'blackboard'))
    R.nocol.add(xz_plate(quad_poly(cx, cz, 0.9, 0.025, 0.6), yN - 0.09, yN - 0.086, 'ivory'))
    # the lights: a strip over the boards, globes over the banks, lamps along the side walls
    R.parts.add(box(1.0, yN - 1.0, H - 0.5, 15.0, yN - 0.8, H - 0.42, 'brass'))
    R.light(box(1.05, yN - 0.98, H - 0.52, 14.95, yN - 0.82, H - 0.5, 'e_fluor'))
    for x in (1.0, 15.0):
        R.nocol.add(box(x - 0.02, yN - 0.92, H - 0.42, x + 0.02, yN - 0.88, H, 'brass'))
    for (x0, x1, s) in banks:
        for y in (3.4, 6.4, 9.4):
            bulb(R, (x0 + x1) / 2, y, 5.0, r=0.2, m='e_lamp', shade=None)
    for y in (4.0, 12.0):
        bulb(R, 1.5, y, 3.2, r=0.14)
        bulb(R, C - 1.5, y, 3.2, r=0.14)
    desk_lamp(R, 4.2, 12.4, 0.92); desk_lamp(R, 11.8, 12.4, 0.92)
    # books along the side corridors and at the back behind the top tier
    for xw, f in ((T, '+x'), (C - T, '-x')):
        sh(R, f, xw, 0.9, 5.9, rows=12, frame='walnut')
        sh(R, f, xw, 10.1, 14.6, rows=12, frame='walnut')
    # the exit signs over the two side doors, glowing at night
    for (x, f) in ((T + 0.02, 1), (C - T - 0.02, -1)):
        R.parts.add(box(min(x, x + f * 0.1), 7.6, 4.3, max(x, x + f * 0.1), 8.4, 4.55, 'black'))
        R.light(box(min(x, x + f * 0.12), 7.65, 4.33, max(x, x + f * 0.12), 8.35, 4.52, 'e_exit'))
    navloop(R, [(1.6, 2.4), (1.6, 8), (1.6, 12.2), (8, 11.2), (C - 1.6, 12.2), (C - 1.6, 8), (C - 1.6, 2.4)])
    a = R.navpt(8, 2.2); b = R.navpt(8, 7.0); R.link(a, b, 3)
    R.navpt(8, 14.0); R.link(3, 9)
    R.spot('probe', 8, 11.5, 2.2)
    R.meta.update(label='The Lecture Theatre', weight=5,
                  blurb='The lecture has just ended, or is about to begin. The boards are full, and the proof on them goes on past the edge.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
