"""The Aqueduct: a stone causeway on arches runs the length of a vaulted hall, two metres up, over a
sunken floor where the bookcases stand. It carries nothing; it goes from one staircase to another."""
from lib import *
from kit_e import *


def make():
    R = Room('aqueduct', 2, 1, res=1024)
    R.sockets(floor='terrazzo')
    W, D = R.W, R.D
    cy = D / 2
    dz = 2.0                                  # the deck
    ya, yb = cy - 1.2, cy + 1.2               # the causeway's width
    xa, xb = 6.0, W - 6.0                     # where it stands on arches
    sz = -1.2                                 # the sunken floor
    ry0, ry1 = 2.4, D - 2.4                   # retaining walls of the sunken floor
    # the hall above the deck: walls and a shallow vault
    jamb, rise = 3.2, 2.2
    pr = arch_profile(cy, D - 2 * T + 0.04, dz, jamb, 40, rise=rise)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
    # below the deck: the floor either side of the causeway, and the two ends
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, ya, dz + 0.05, 'tile', bottom='terrazzo'))
    R.cut(box(T - 0.02, yb, 0, W - T + 0.02, D - T + 0.02, dz + 0.05, 'tile', bottom='terrazzo'))
    R.cut(box(T - 0.02, ya - 0.1, 0, xa, yb + 0.1, dz + 0.05, 'tile', bottom='terrazzo'))
    R.cut(box(xb, ya - 0.1, 0, W - T + 0.02, yb + 0.1, dz + 0.05, 'tile', bottom='terrazzo'))
    # the sunken floor, with steps down at both ends
    ns, sr = 4, 0.45
    for (y0, y1) in ((ry0, ya + 0.02), (yb - 0.02, ry1)):
        R.cut(box(xa + ns * sr, y0, sz, xb - ns * sr, y1, 0.1, 'tile', bottom='mosaic'))
        for k in range(ns):
            z = -0.3 * (k + 1)
            R.cut(box(xa + k * sr, y0, z, xa + (k + 1) * sr + 0.01, y1, 0.1, 'tile', bottom='terrazzo'))
            R.cut(box(xb - (k + 1) * sr - 0.01, y0, z, xb - k * sr, y1, 0.1, 'tile', bottom='terrazzo'))
    # the arches under the causeway, in line with the cross doorways
    for x in (8.0, 12.0, 16.0, 20.0, 24.0):
        pa = arch_profile(x, 2.6, sz, 1.6, 20)
        R.cut(prism(pa, 'y', ya - 0.05, yb + 0.05, arch_mats(len(pa), 'mosaic', 'tile')))
    # skylights along the crown of the vault
    for k in range(7):
        x = 4.0 + 4.0 * k
        R.cut(box(x - 0.7, cy - 1.0, dz + jamb + rise - 0.5, x + 0.7, cy + 1.0, R.hi + 0.5, 'plaster'))
        R.light(box(x - 0.7, cy - 1.0, R.hi - 0.09, x + 0.7, cy + 1.0, R.hi - 0.05, 'e_sky'))
    # staircases up to the deck from both ends, walled in stone
    n, rs, rn = 10, dz / 10, 0.32
    L = n * rn
    R.flight(xa - L, ya, 0, yb - ya, n, rs, rn, '+x', m='terrazzo', side='tile')
    R.flight(xb + L, ya, 0, yb - ya, n, rs, rn, '-x', m='terrazzo', side='tile')
    ph = 0.95
    for (y0, y1) in ((ya, ya + 0.22), (yb - 0.22, yb)):
        R.parts.add(slope_box(xa - L - 0.25, xa, y0, y1, 0, 0, ph + 0.2, dz + ph, 'tile', cap='tile'))
        R.parts.add(slope_box(xb, xb + L + 0.25, y0, y1, 0, 0, dz + ph, ph + 0.2, 'tile', cap='tile'))
        R.parts.add(slope_box(xa - L - 0.25, xa, y0 - 0.03, y1 + 0.03, ph + 0.2, dz + ph, ph + 0.26, dz + ph + 0.06, 'brass'))
        R.parts.add(slope_box(xb, xb + L + 0.25, y0 - 0.03, y1 + 0.03, dz + ph, ph + 0.2, dz + ph + 0.06, ph + 0.26, 'brass'))
        # the deck's parapets
        R.parts.add(balustrade(xa, y0, xb, y1, dz, ph, 'tile', 'brass'))
    # lamp standards on the parapets, over every pier
    for x in (xa + 0.35, 10.0, 14.0, 18.0, 22.0, xb - 0.35):
        for y in (ya + 0.11, yb - 0.11):
            R.parts.add(cyl(x, y, dz + ph + 0.06, dz + 2.3, 0.035, 8, side='iron', caps=False))
            R.parts.add(cyl(x, y, dz + 2.28, dz + 2.34, 0.09, 10, side='iron', top='iron', bottom='iron'))
            R.light(sphere(x, y, dz + 2.5, 0.17, 12, 6, 'e_lamp'))
    # a runner along the deck
    R.parts.add(box(xa - 0.05, cy - 0.5, dz, xb + 0.05, cy + 0.5, dz + 0.012, 'carpet', skip=('-z',)))
    # the sunken floor: rails along the retaining walls, low cases against them, tall stacks between
    for (y, s) in ((ry0, -1), (ry1, 1)):
        rail(R, [(xa, y + s * 0.06, 0), (xb, y + s * 0.06, 0)])
    R.shelf(xa + ns * sr + 0.1, ry0, sz, (xb - xa) - 2 * ns * sr - 0.2, '+y', rows=2, frame='wood')
    R.shelf(xb - ns * sr - 0.1, ry1, sz, (xb - xa) - 2 * ns * sr - 0.2, '-y', rows=2, frame='wood')
    for x in (10.0, 14.0, 18.0, 22.0):
        for (y0, y1) in ((ry0 + 0.5, ya - 1.2), (yb + 1.2, ry1 - 0.5)):
            R.shelf(x + 0.01, y1, sz, y1 - y0, '+x', rows=7, frame='wood', back=True)
            R.shelf(x - 0.01, y0, sz, y1 - y0, '-x', rows=7, frame='wood', back=True)
    for x in (9.0, 13.0, 17.0, 21.0, 25.0 - 1.0):
        for y in (ry0 + 0.02, ry1 - 0.02):
            R.light(box(x - 0.2, y - 0.03, sz + 0.85, x + 0.2, y + 0.03, sz + 0.95, 'e_pool'))
    # books on the hall walls, above the upper floor and at the ends
    wall_shelves(R, rows=10, frame='walnut', sides='SN')
    for (a, b) in ((T + 0.25, 6.2), (9.8, D - T - 0.25)):
        R.shelf(T, b, 0, b - a, '+x', rows=10, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=10, frame='walnut')
    # walkers: the upper floor round the edge, the deck, the sunken floor
    top = loop(R, [(1.4, 1.4), (8.0, 1.4), (16.0, 1.4), (24.0, 1.4), (W - 1.4, 1.4), (W - 1.4, D - 1.4), (24.0, D - 1.4), (16.0, D - 1.4), (8.0, D - 1.4), (1.4, D - 1.4)])
    w0 = R.navpt(1.5, cy); w1 = R.navpt(W - 1.5, cy)
    R.link(top[0], w0, top[9]); R.link(top[4], w1, top[5])
    s0 = R.navpt(xa - L - 0.6, cy); d0 = R.navpt(xa + 0.8, cy, dz); d1 = R.navpt(xb - 0.8, cy, dz); s1 = R.navpt(xb + L + 0.6, cy)
    R.link(w0, s0, d0, d1, s1, w1)
    for (yy, t0, t1) in ((ya - 0.6, top[0], top[4]), (yb + 0.6, top[9], top[5])):
        e0 = R.navpt(xa - 0.8, yy); a_ = R.navpt(xa + ns * sr + 0.6, yy, sz)
        e1 = R.navpt(xb + 0.8, yy); b_ = R.navpt(xb - ns * sr - 0.6, yy, sz)
        R.link(t0, e0, a_, b_, e1, t1)
    for x in (8.0, 16.0, 24.0):
        p = R.navpt(x, 5.4, sz); q = R.navpt(x, D - 5.4, sz); R.link(p, q)
    R.spot('probe', 16.0, cy, dz + 2.0)
    R.meta.update(label='The Aqueduct', weight=7,
                  blurb='A causeway on stone arches crosses the hall two metres above the books. It carries no water and leads from one staircase to another, and people walk it anyway, slowly, as if it went somewhere.')
    R.meta['box'] = [[T, sz, T], [W - T, R.hi, D - T]]
    return R
