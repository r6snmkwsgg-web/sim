"""The Staircase Gallery: a grand staircase climbs from each end of the hall to a landing in the
middle, three and a half metres up, and that is all. The landing stands on three arches."""
from lib import *
from kit_e import *


def make():
    R = Room('grandstair', 2, 1, res=1024)
    R.sockets(floor='terrazzo')
    W, D = R.W, R.D
    cy = D / 2
    lz = 3.5                                   # the landing
    ya, yb = cy - 2.2, cy + 2.2                # outer faces of the balustrades
    bw = 0.24
    n, rs, rn = 20, lz / 20, 0.4
    L = n * rn
    xs0, xs1 = 2.6, W - 2.6                    # feet of the flights
    la, lb = xs0 + L, xs1 - L                  # the landing, 10.6 .. 21.4
    # the hall above the landing, and round it below
    HC = 7.15
    R.cut(box(T - 0.02, T - 0.02, lz, W - T + 0.02, D - T + 0.02, HC, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, ya, lz + 0.05, 'tile', bottom='terrazzo'))
    R.cut(box(T - 0.02, yb, 0, W - T + 0.02, D - T + 0.02, lz + 0.05, 'tile', bottom='terrazzo'))
    R.cut(box(T - 0.02, ya - 0.1, 0, la, yb + 0.1, lz + 0.05, 'tile', bottom='terrazzo'))
    R.cut(box(lb, ya - 0.1, 0, W - T + 0.02, yb + 0.1, lz + 0.05, 'tile', bottom='terrazzo'))
    # three arches through the landing's base
    for x in (12.8, 16.0, 19.2):
        pa = arch_profile(x, 2.2, 0, 1.9, 18)
        R.cut(prism(pa, 'y', ya - 0.05, yb + 0.05, arch_mats(len(pa), 'terrazzo', 'tile')))
    # coffered ceiling, a laylight over the landing
    for k in range(8):
        x = 2.0 + 4.0 * k
        for y in (3.0, D - 3.0):
            R.cut(box(x - 1.5, y - 1.8, HC - 0.05, x + 1.5, y + 1.8, HC + 0.35, 'plaster'))
            R.light(box(x - 0.9, y - 1.1, HC + 0.3, x + 0.9, y + 1.1, HC + 0.33, 'e_sky'))
    R.cut(box(la + 0.3, ya + 0.2, HC - 0.05, lb - 0.3, yb - 0.2, HC + 0.42, 'plaster'))
    R.light(box(la + 2.0, cy - 0.5, HC + 0.36, lb - 2.0, cy + 0.5, HC + 0.39, 'e_sky'))
    # the flights, walled in with stone balustrades
    R.flight(xs0, ya + bw, 0, yb - ya - 2 * bw, n, rs, rn, '+x', m='terrazzo', side='tile')
    R.flight(xs1, ya + bw, 0, yb - ya - 2 * bw, n, rs, rn, '-x', m='terrazzo', side='tile')
    ph = 1.0
    for (y0, y1) in ((ya, ya + bw), (yb - bw, yb)):
        R.parts.add(slope_box(xs0 - 0.4, la, y0, y1, 0, 0, ph, lz + ph, 'tile'))
        R.parts.add(slope_box(xs0 - 0.43, la, y0 - 0.03, y1 + 0.03, ph, lz + ph, ph + 0.07, lz + ph + 0.07, 'brass'))
        R.parts.add(slope_box(lb, xs1 + 0.4, y0, y1, 0, 0, lz + ph, ph, 'tile'))
        R.parts.add(slope_box(lb, xs1 + 0.43, y0 - 0.03, y1 + 0.03, lz + ph, ph, lz + ph + 0.07, ph + 0.07, 'brass'))
        R.parts.add(balustrade(la, y0, lb, y1, lz, ph, 'tile', 'brass'))
    # newel posts with lamps: at the feet and at the landing's corners
    for (x, z) in ((xs0 - 0.4, 0.0), (xs1 + 0.4, 0.0), (la, lz), (lb, lz)):
        for y in (ya + bw / 2, yb - bw / 2):
            R.parts.add(box(x - 0.2, y - 0.2, z, x + 0.2, y + 0.2, z + ph + 0.25, 'tile', skip=('-z',)))
            R.parts.add(cyl(x, y, z + ph + 0.25, z + ph + 1.4, 0.04, 8, side='bronze', caps=False))
            R.light(sphere(x, y, z + ph + 1.55, 0.18, 12, 6, 'e_lamp'))
    # the chandelier over the landing
    cx = W / 2
    R.parts.add(cyl(cx, cy, 5.6, HC + 0.4, 0.02, 6, side='iron', caps=False))
    R.parts.add(ring(cx, cy, 5.55, 5.62, 1.1, 1.18, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
    for k in range(10):
        a = 2 * math.pi * k / 10
        R.light(sphere(cx + math.cos(a) * 1.14, cy + math.sin(a) * 1.14, 5.72, 0.09, 8, 4, 'e_lamp'))
    # a single chair on the landing, facing west, and a lamp that stays on at night
    chair(R, cx + 1.2, cy + 1.2, math.pi, frame='walnut', seat='velvet', z=lz)
    R.light(sphere(cx + 1.2, cy + 1.75, lz + 0.1, 0.08, 8, 4, 'e_amber'))
    # books on every wall
    wall_shelves(R, rows=14, frame='walnut', sides='SN')
    for (a, b) in ((T + 0.1, 6.2), (9.8, D - T - 0.1)):
        R.shelf(T, b, 0, b - a, '+x', rows=14, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=14, frame='walnut')
    # low amber lights along the base of the balustrades (night)
    for x in (4.0, 8.0, 24.0, 28.0):
        for (y, s) in ((ya, -1), (yb, 1)):
            R.light(box(x - 0.2, y + s * 0.02, 0.1, x + 0.2, y + s * 0.05, 0.2, 'e_amber'))
    # pendants over the floor either side
    for x in (6.0, 12.0, 20.0, 26.0):
        for y in (3.0, D - 3.0):
            pendant(R, x, y, 4.2, HC + 0.3, r=0.3)
    # walkers
    fl = loop(R, [(1.4, cy), (2.0, 2.2), (8.0, 1.8), (16.0, 2.2), (24.0, 1.8), (W - 2.0, 2.2), (W - 1.4, cy), (W - 2.0, D - 2.2), (24.0, D - 1.8),
                  (16.0, D - 2.2), (8.0, D - 1.8), (2.0, D - 2.2)])
    s0 = R.navpt(xs0 - 0.8, cy); p0 = R.navpt(la + 1.0, cy, lz); p1 = R.navpt(lb - 1.0, cy, lz); s1 = R.navpt(xs1 + 0.8, cy)
    R.link(fl[0], s0, p0, p1, s1, fl[6])
    u = R.navpt(16.0, ya - 1.0); v = R.navpt(16.0, yb + 1.0); R.link(fl[3], u, v, fl[9])
    R.spot('probe', 16.0, cy, lz + 2.0)
    R.meta.update(label='The Staircase Gallery', weight=6,
                  blurb='Two grand staircases climb to a landing in the middle of the hall. There is nothing up there but a chair, which is facing the wrong way.')
    R.meta['box'] = [[T, 0, T], [W - T, TOP, D - T]]
    return R
