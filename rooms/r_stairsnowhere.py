"""Stairs to Nowhere: flights of stairs climb to landings against blank walls, railed, patient, and
one goes down into a narrow well that ends at a wall."""
from lib import *
from kit_a import *

H = TOP - 0.1


def make():
    R = Room('stairsnowhere', 1, 1, res=1024, lo=-4.0)
    shell(R, wall='tile', floor='terrazzo', ceil='plaster', h=H)
    # 1. along the south wall, climbing west to a landing in the corner
    w1, n1, r1, u1 = 1.3, 16, 0.2, 0.3
    x0, y0 = 6.1, T + 0.05
    R.flight(x0, y0, 0, w1, n1, r1, u1, '-x', m='terrazzo', riser='tile', side='tile')
    z1 = n1 * r1; xl = x0 - n1 * u1
    R.parts.add(box(T, T, 0, xl, y0 + w1, z1, 'tile', top='terrazzo'))
    stair_rail(R, x0 - u1, y0 + w1 - 0.04, r1, xl, y0 + w1 - 0.04, z1)
    rail(R, xl, y0 + w1 - 0.04, T, y0 + w1 - 0.04, z1)
    # 3. along the north wall, climbing west, steeper and higher
    w3, n3, r3, u3 = 1.3, 16, 0.22, 0.29
    x0b, y0b = 5.9, C - T - 0.05 - w3
    R.flight(x0b, y0b, 0, w3, n3, r3, u3, '-x', m='terrazzo', riser='tile', side='tile')
    z3 = n3 * r3; xl3 = x0b - n3 * u3
    R.parts.add(box(T, y0b, 0, xl3, C - T, z3, 'tile', top='terrazzo'))
    stair_rail(R, x0b - u3, y0b + 0.04, r3, xl3, y0b + 0.04, z3)
    rail(R, xl3, y0b + 0.04, T, y0b + 0.04, z3)
    # 2. the long one, freestanding, climbing north almost to the ceiling; books along its flanks
    w2, n2, r2, u2 = 1.4, 25, 0.2, 0.3
    sx0, sy0 = 11.0, 6.6
    R.flight(sx0, sy0, 0, w2, n2, r2, u2, '+y', m='terrazzo', riser='tile', side='tile')
    z2 = n2 * r2; yl = sy0 + n2 * u2
    R.parts.add(box(sx0, yl, 0, sx0 + w2, C - T, z2, 'tile', top='terrazzo'))
    for x in (sx0 + 0.04, sx0 + w2 - 0.04):
        stair_rail(R, x, sy0 + u2, r2, x, yl, z2)
        rail(R, x, yl, x, C - T, z2)
    for s, xb in ((-1, sx0), (1, sx0 + w2)):
        y = sy0 + 1.2
        while y + 1.4 < C - T - 0.2:
            zt = min(z2, (y - sy0) / u2 * r2) - 0.1
            rows = int((zt - 0.12) / 0.42)
            if rows >= 1:
                sh(R, '+x' if s > 0 else '-x', xb, y, y + 1.4, rows=rows, frame='walnut')
            y += 1.45
    # 4. the well: a slot in the floor, a stair down, and at the bottom a wall
    wx0, wx1 = 14.05, C - T
    n4, r4, u4 = 15, 0.2, 0.3
    wd = n4 * r4
    wy1 = 5.9
    wy_foot = wy1 - n4 * u4
    R.cut(box(wx0, T - 0.02, -wd, wx1 + 0.02, wy1, 0.05, 'tile', bottom='slate'))
    R.flight(wx0, wy_foot, -wd, wx1 - wx0, n4, r4, u4, '+y', m='slate', riser='tile', side='tile')
    rail(R, wx0 - 0.1, T, wx0 - 0.1, wy1 + 0.1, 0, solid=True)
    for k in range(0, n4, 3):
        y = wy_foot + k * u4 + 0.15
        R.light(box(wx0 + 0.02, y - 0.12, -wd + k * r4 + 0.06, wx0 + 0.04, y + 0.12, -wd + k * r4 + 0.12, 'e_pool'))
    R.parts.add(box(14.6, T, -wd + 1.6, 15.1, T + 0.05, -wd + 1.9, 'brass'))   # a plaque, blank
    R.light(sphere(14.85, T + 0.2, -wd + 2.3, 0.08, 12, 6, 'e_amber'))
    R.parts.add(box(14.8, T, -wd + 2.3, 14.9, T + 0.2, -wd + 2.33, 'brass'))
    # lamps over each landing, and globes on the ceiling
    for (x, y, z) in ((T + 0.1, 1.0, z1 + 1.9), (T + 0.1, C - 1.0, z3 + 1.7), (sx0 + w2 / 2, C - T - 0.1, z2 + 1.6)):
        R.light(sphere(x + (0.1 if x < 2 else 0), y - (0.1 if y > 15 else 0), z, 0.12, 12, 6, 'e_lamp'))
    for (x, y) in ((3.6, 5.0), (3.6, 10.8), (8.0, 8.0), (12.0, 3.4), (13.8, 11.6)):
        bulb(R, x, y, 4.6, r=0.17, top=H)
    # books on the free walls
    sh(R, '+x', T, 2.2, 6.2, rows=10, frame='walnut')
    sh(R, '+x', T, 9.8, C - T - 1.5, rows=10, frame='walnut')
    sh(R, '-x', C - T, 9.8, C - T - 0.1, rows=14, frame='walnut')
    sh(R, '+y', T, 12.0, 15.2, rows=14, frame='walnut')
    navloop(R, [(2.5, 3.4), (8, 2.6), (13.2, 6.9), (13.2, 13.0), (8.9, 13.4), (8.4, 8.0), (2.5, 12.2), (1.6, 8)])
    # the landings, for the walkers who like to climb
    for (fx, fy, lx, ly, lz) in ((x0 + 0.5, y0 + w1 / 2, T + 0.6, y0 + w1 / 2, z1), (x0b + 0.5, y0b + w3 / 2, T + 0.6, y0b + w3 / 2, z3),
                                 (sx0 + w2 / 2, sy0 - 0.5, sx0 + w2 / 2, C - T - 0.6, z2)):
        a, b = R.navpt(fx, fy), R.navpt(lx, ly, lz)
        R.link(a, b)
    R.spot('probe', 7.2, 8.0, 1.7)
    R.meta.update(label='Stairs to Nowhere', weight=4,
                  blurb='Every stair here is well made, handsomely railed, and goes nowhere. Climb one anyway. Everyone does.')
    R.meta['box'] = [[T, -3.0, T], [C - T, H, C - T]]
    return tidy(R)
