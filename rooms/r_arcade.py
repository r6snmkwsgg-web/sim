"""The Arcade: a tall nave between two arcades of round arches, two tiers high, receding to a point;
a lamp hangs in every arch. The outer aisles are lined with books."""
from lib import *
from kit_e import *


def make():
    R = Room('arcade', 2, 1, res=1024)
    R.sockets(floor='terrazzo')
    W, D = R.W, R.D
    cy = D / 2
    H = 7.1
    a0, a1 = 4.6, 5.5                                # the south arcade wall (mirrored for the north)
    # the nave, and the two aisles
    R.cut(box(T - 0.02, a1, 0, W - T + 0.02, D - a1, H, 'tile', bottom='terrazzo', top='plaster'))
    for (y0, y1) in ((T - 0.02, a0), (D - a0, D - T + 0.02)):
        R.cut(box(T - 0.02, y0, 0, W - T + 0.02, y1, H, 'tile', bottom='floor', top='plaster'))
    # nave ceiling coffers between the bays
    for k in range(8):
        x = 2.0 + 4.0 * k
        R.cut(box(x - 1.55, a1 + 0.35, H - 0.05, x + 1.55, D - a1 - 0.35, H + 0.4, 'plaster'))
        R.light(box(x - 0.9, cy - 1.2, H + 0.34, x + 0.9, cy + 1.2, H + 0.37, 'e_panel'))
    # the two arcades: big arches below, twin small arches above, all on the same 4 m rhythm
    xs = [4.0 * k for k in range(1, 8)]
    for (y0, y1) in ((a0 - 0.05, a1 + 0.05), (D - a1 - 0.05, D - a0 + 0.05)):
        for x in xs:
            pa = arch_profile(x, 3.0, 0, 3.5, 20)
            R.cut(prism(pa, 'y', y0, y1, arch_mats(len(pa), 'terrazzo', 'tile')))
            for dx in (-0.8, 0.8):
                pb = arch_profile(x + dx, 1.0, 5.55, 0.8, 12)
                R.cut(prism(pb, 'y', y0, y1, arch_mats(len(pb), 'tile', 'tile')))
        # the half-bays against the end walls
        for x in (1.5, W - 1.5):
            pb = arch_profile(x, 1.0, 5.55, 0.8, 12)
            R.cut(prism(pb, 'y', y0, y1, arch_mats(len(pb), 'tile', 'tile')))
    # a string course between the tiers, both faces of each arcade
    for (y0, y1) in ((a0 - 0.15, a0), (a1, a1 + 0.15), (D - a1 - 0.15, D - a1), (D - a0, D - a0 + 0.15)):
        R.parts.add(box(T, y0, 5.1, W - T, y1, 5.32, 'plaster'))
    # a lamp hanging in the crown of every arch
    for x in xs:
        for y in ((a0 + a1) / 2, D - (a0 + a1) / 2):
            globe(R, x, y, 3.95, 5.0, r=0.17)
    # aisle lamps: a pendant in each aisle bay, and transverse ribs
    for k in range(8):
        x = 2.0 + 4.0 * k
        for y in ((T + a0) / 2, D - (T + a0) / 2):
            pendant(R, x, y, 3.3, H, r=0.24)
    for x in xs:
        for (y0, y1) in ((T, a0), (D - a0, D - T)):
            R.parts.add(box(x - 0.2, y0, H - 0.35, x + 0.2, y1, H, 'plaster', skip=('+z',)))
    # books along the outer walls of the aisles (between the doorways), and at the aisle ends
    wall_shelves(R, rows=12, frame='walnut', sides='SN')
    for (y0, y1) in ((T + 0.1, a0 - 0.1), (D - a0 + 0.1, D - T - 0.1)):
        R.shelf(T, y1, 0, y1 - y0, '+x', rows=12, frame='walnut')
        R.shelf(W - T, y0, 0, y1 - y0, '-x', rows=12, frame='walnut')
    # benches down the nave, and amber night lamps on the pier bases
    for x in (12.0, 20.0):
        bench(R, x - 1.1, cy - 0.25, x + 1.1, cy + 0.25, m='walnut', seat='leather', spots=False)
        R.spot('sit', x - 0.5, cy, 0.45, math.pi / 2); R.spot('sit', x + 0.5, cy, 0.45, -math.pi / 2)
    for x in [2.0 + 4.0 * k for k in range(8)]:
        for (y, s) in ((a1, 1), (D - a1, -1)):
            R.light(box(x - 0.12, y + s * 0.0, 0.25, x + 0.12, y + s * 0.03, 0.4, 'e_amber'))
    # walkers: both aisles, the nave, joined through the arches
    nave = loop(R, [(2.0, cy - 1.2), (W - 2.0, cy - 1.2), (W - 2.0, cy + 1.2), (2.0, cy + 1.2)])
    sa = loop(R, [(1.5, 2.4), (8.0, 2.4), (16.0, 2.4), (24.0, 2.4), (W - 1.5, 2.4)], close=False)
    na = loop(R, [(1.5, D - 2.4), (8.0, D - 2.4), (16.0, D - 2.4), (24.0, D - 2.4), (W - 1.5, D - 2.4)], close=False)
    for i, x in ((1, 8.0), (2, 16.0), (3, 24.0)):
        p = R.navpt(x, cy - 1.2); q = R.navpt(x, cy + 1.2)
        R.link(sa[i], p, q, na[i])
    R.spot('probe', 16.0, cy, 2.5)
    R.meta.update(label='The Arcade', weight=9,
                  blurb='Two rows of arches run away from you to a point, a lamp hung in every one. Count them if you like. You will get a different number coming back.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    return R
