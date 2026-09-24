"""The Long Gallery: a vaulted hall of pedestals, busts and urns under a line of skylights, bookcases
set between pilasters on both long walls. Every bust looks at the one opposite."""
from lib import *
from kit_e import *


def make():
    R = Room('longgallery', 2, 1, res=1024)
    R.sockets(floor='terrazzo')
    W, D = R.W, R.D
    cy = D / 2
    # the hall: walls to 5.0 m, then a shallow vault
    jamb, rise = 5.0, 2.45
    pr = arch_profile(cy, D - 2 * T + 0.04, 0, jamb, 40, rise=rise)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
    # a plaster band where the vault springs, and a cornice
    for (y0, y1) in ((T, T + 0.22), (D - T - 0.22, D - T)):
        R.parts.add(box(T, y0, jamb - 0.25, W - T, y1, jamb, 'plaster'))
    # skylights: a row of square wells up through the vault crown
    xs = [2.0 + 4.0 * k for k in range(8)]
    for x in xs:
        R.cut(box(x - 0.85, cy - 1.3, jamb + rise - 0.6, x + 0.85, cy + 1.3, R.hi + 0.6, 'plaster'))
        R.light(box(x - 0.85, cy - 1.3, R.hi - 0.09, x + 0.85, cy + 1.3, R.hi - 0.05, 'e_sky'))
    # pilasters along the long walls, bookcases between them
    P = [4.0, 6.25, 9.75, 12.0, 16.0, 20.0, 22.25, 25.75, 28.0]
    for x in P:
        pilaster(R, x, T, '+y', 0, jamb - 0.25, w=0.5, d=0.28)
        pilaster(R, x, D - T, '-y', 0, jamb - 0.25, w=0.5, d=0.28)
    bays = [(T + 0.05, 3.72), (4.28, 5.97), (10.03, 11.72), (12.28, 15.72), (16.28, 19.72), (20.28, 21.97), (26.03, 27.72), (28.28, W - T - 0.05)]
    for (a, b) in bays:
        R.shelf(a, T, 0, b - a, '+y', rows=9, frame='walnut', sides=False)
        R.shelf(b, D - T, 0, b - a, '-y', rows=9, frame='walnut', sides=False)
    # end walls: short cases either side of the doorways
    for (a, b) in ((T + 0.3, 6.0), (10.0, D - T - 0.3)):
        R.shelf(T, b, 0, b - a, '+x', rows=9, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=9, frame='walnut')
    # a runner down the middle
    R.parts.add(box(2.4, cy - 1.0, 0, W - 2.4, cy + 1.0, 0.015, 'carpet', skip=('-z',)))
    # pedestals: busts facing across the aisle, urns between them
    k = 0
    for x in (4.0, 12.0, 16.0, 20.0, 28.0):
        for (y, face) in ((cy - 3.1, math.pi / 2), (cy + 3.1, -math.pi / 2)):
            if (x in (4.0, 16.0, 28.0)):
                bust(R, x, y, face, ped='tile', stone='ivory')
            else:
                urn(R, x, y, 0, s=1.1, m='bronze', ped='tile', ph=1.0)
            k += 1
    for x in (8.0, 24.0):
        # in line with the cross doorways: a pair of tall urns on low plinths, set back from the path
        for y in (cy - 4.4, cy + 4.4):
            urn(R, x - 2.0, y, 0, s=0.8, m='bronze', ped='tile', ph=0.7)
            urn(R, x + 2.0, y, 0, s=0.8, m='bronze', ped='tile', ph=0.7)
    # plaques on two busts
    R.spot('plaque', 16.0, cy - 3.1 + 0.34, 0.9, math.pi / 2)
    R.spot('plaque', 16.0, cy + 3.1 - 0.34, 0.9, -math.pi / 2)
    # lamps: brass sconces on the pilasters, and small amber lamps at the foot of each bust (night)
    for x in P:
        for (y, s) in ((T + 0.28, 1), (D - T - 0.28, -1)):
            R.parts.add(box(x - 0.05, y, 3.0, x + 0.05, y + s * 0.3, 3.06, 'brass'))
            R.light(sphere(x, y + s * 0.34, 3.18, 0.11, 10, 6, 'e_lamp'))
    for x in (4.0, 16.0, 28.0):
        for (y, s) in ((cy - 3.1, 1), (cy + 3.1, -1)):
            R.light(box(x - 0.15, y + s * 0.31 - 0.02, 0.05, x + 0.15, y + s * 0.31 + 0.02, 0.1, 'e_amber'))
    # benches in the aisle, facing the busts
    for x in (10.0, 22.0):
        bench(R, x - 0.9, cy - 0.25, x + 0.9, cy + 0.25, m='walnut', seat='velvet', spots=False)
        R.spot('sit', x, cy, 0.45, -math.pi / 2)
    # walkers: the central aisle, the side aisles, and the cross axes
    mid = loop(R, [(2.0, cy), (6.0, cy + 1.6), (14.0, cy + 1.6), (18.0, cy + 1.6), (26.0, cy + 1.6), (W - 2.0, cy), (26.0, cy - 1.6), (18.0, cy - 1.6), (14.0, cy - 1.6), (6.0, cy - 1.6)])
    side = loop(R, [(2.2, 2.2), (8.0, 2.0), (14.0, 2.2), (24.0, 2.0), (W - 2.2, 2.2)], close=False)
    side2 = loop(R, [(2.2, D - 2.2), (8.0, D - 2.0), (14.0, D - 2.2), (24.0, D - 2.0), (W - 2.2, D - 2.2)], close=False)
    R.link(side[0], mid[0]); R.link(side[-1], mid[5]); R.link(side2[0], mid[0]); R.link(side2[-1], mid[5])
    a = R.navpt(8.0, cy - 1.6); R.link(side[1], a); b = R.navpt(8.0, cy + 1.6); R.link(side2[1], b); R.link(a, b)
    R.spot('probe', 16.0, cy, 2.2)
    R.meta.update(label='The Long Gallery', weight=8,
                  blurb='Busts on pedestals face each other across the aisle, all the way down. None of them is anyone you have heard of, and all of them are looking at you.')
    R.meta['box'] = [[T, 0, T], [W - T, R.hi, D - T]]
    return R
