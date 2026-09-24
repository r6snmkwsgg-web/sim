"""The Twin Naves: two identical vaulted naves side by side, joined by an arcade, a skylight slot in
each vault. Identical down to the last chair, nearly."""
from lib import *
from kit_e import *


def make():
    R = Room('twinnaves', 2, 1, res=1024)
    R.sockets(floor='terrazzo')
    W, D = R.W, R.D
    cy = D / 2
    a0, a1 = cy - 0.4, cy + 0.4               # the arcade wall
    jamb, rise = 4.2, 3.0
    naves = ((T, a0), (a1, D - T))
    for (y0, y1) in naves:
        pr = arch_profile((y0 + y1) / 2, y1 - y0 + 0.04, 0, jamb, 36, rise=rise)
        R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
        yc = (y0 + y1) / 2
        R.cut(box(3.0, yc - 0.55, jamb + rise - 0.35, W - 3.0, yc + 0.55, R.hi + 0.5, 'plaster'))
        R.light(box(3.0, yc - 0.55, R.hi - 0.09, W - 3.0, yc + 0.55, R.hi - 0.05, 'e_sky'))
        # transverse ribs across the vault every 4 m
        for k in range(1, 8):
            x = 4.0 * k
            pa = arch_profile(yc, y1 - y0 + 0.04, 0, jamb, 36, rise=rise)
            pb = arch_profile(yc, y1 - y0 - 0.5, 0, jamb, 36, rise=rise - 0.22)
            outer = [(p, q) for p, q in pa[2:]]            # the curve from the east spring round to the west
            inner = [(p, q) for p, q in pb[2:]]
            prof = outer + list(reversed(inner))
            R.parts.add(prism(prof, 'x', x - 0.18, x + 0.18, 'plaster', cap='plaster'))
    # the ends of the arcade stand open, full height of the walls
    for (xa, xb) in ((T - 0.02, 3.5), (W - 3.5, W - T + 0.02)):
        R.cut(box(xa, a0 - 0.05, 0, xb, a1 + 0.05, jamb, 'tile', bottom='terrazzo'))
    # the arcade: an arch every 4 m, between piers at x = 4, 8, ... 28
    for k in range(6):
        x = 6.0 + 4.0 * k
        pa = arch_profile(x, 3.0, 0, 2.9, 20)
        R.cut(prism(pa, 'y', a0 - 0.05, a1 + 0.05, arch_mats(len(pa), 'terrazzo', 'tile')))
    # sconces on both faces of every pier, amber lamps at their feet
    for k in range(7):
        x = 4.0 + 4.0 * k
        for (y, s) in ((a0, -1), (a1, 1)):
            R.parts.add(box(x - 0.04, y + s * 0.0, 3.2, x + 0.04, y + s * 0.28, 3.26, 'brass'))
            R.light(sphere(x, y + s * 0.3, 3.36, 0.12, 10, 6, 'e_lamp'))
            R.light(box(x - 0.14, y + s * 0.0, 0.18, x + 0.14, y + s * 0.03, 0.3, 'e_amber'))
    # books along the outer walls and at the nave ends
    wall_shelves(R, rows=9, frame='walnut', sides='SN')
    for (a, b) in ((T + 0.2, 6.2), (9.8, D - T - 0.2)):
        R.shelf(T, b, 0, b - a, '+x', rows=9, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=9, frame='walnut')
    # identical reading tables down both naves
    for (yc, side) in (((T + a0) / 2, 0), ((a1 + D - T) / 2, 1)):
        for (xa, xb, nc) in ((3.4, 8.6, 4), (11.4, 20.6, 7), (23.4, 28.6, 4)):
            table(R, xa, yc - 0.45, xb, yc + 0.45, m='walnut', top='leather')
            for i in range(nc):
                x = xa + 0.7 + i * (xb - xa - 1.4) / (nc - 1)
                if side == 1 and xa == 11.4 and i == 4:
                    # the one difference: a chair pushed back and turned away
                    chair(R, x + 0.3, yc + 1.25, -math.pi / 2 + 0.6, frame='walnut', seat='velvet')
                else:
                    chair(R, x, yc + 0.8, -math.pi / 2, frame='walnut', seat='velvet')
                chair(R, x, yc - 0.8, math.pi / 2, frame='walnut', seat='velvet')
            for x in ((xa + xb) / 2,) if nc == 4 else (xa + 1.6, (xa + xb) / 2, xb - 1.6):
                table_lamp(R, x, yc, 0.76)
    # walkers: a loop down each nave, joined through the arches and round the ends
    s = loop(R, [(1.5, 2.2), (8.0, 2.2), (16.0, 2.2), (24.0, 2.2), (W - 1.5, 2.2), (W - 1.5, cy), (W - 1.5, D - 2.2), (24.0, D - 2.2), (16.0, D - 2.2),
                 (8.0, D - 2.2), (1.5, D - 2.2), (1.5, cy)])
    for x in (10.0, 22.0):
        a = R.navpt(x, 2.2); b = R.navpt(x, D - 2.2); R.link(a, b)
        R.link(s[1], a, s[2]) if x < 16 else R.link(s[2], a, s[3])
        R.link(s[9], b, s[8]) if x < 16 else R.link(s[8], b, s[7])
    R.spot('probe', 16.0, cy, 2.0)
    R.meta.update(label='The Twin Naves', weight=7,
                  blurb='Two naves, side by side, the same in every particular. Stand in the arcade between them and try to remember which one you came in by.')
    R.meta['box'] = [[T, 0, T], [W - T, R.hi, D - T]]
    return R
