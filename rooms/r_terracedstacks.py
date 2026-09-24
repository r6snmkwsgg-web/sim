"""The Terraces of Stacks: the floor goes down in four broad steps toward the north, like a vineyard of
bookcases, with a railed walk round the rim. Stairs go down between the tiers; low shelves line
each edge."""
from lib import *
from kit_f import *


def make():
    R = Room('terracedstacks', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, TOP - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    rim = 3.35                                     # the raised walk round the west, north and east
    edges = [9.0, 15.0, 21.0]                      # where each tier starts (north of the edge is lower)
    dz = 0.6
    N0 = W - rim
    for k, e in enumerate(edges):
        R.cut(box(rim, e, -dz * (k + 1), W - rim, N0, 0.05, 'tile', bottom='floor'))
    tiers = [(T + 0.3, 0.0, edges[0]), (edges[0], -dz, edges[1]), (edges[1], -2 * dz, edges[2]), (edges[2], -3 * dz, N0)]
    # stairs between tiers: a wide one in the middle and two narrow ones on the door lines
    stairs_x = [(14.0, 18.0), (7.0, 9.0), (23.0, 25.0)]
    for k, e in enumerate(edges):
        zl = -dz * (k + 1)
        for (a, b) in stairs_x:
            R.flight(a, e + 0.9, zl, b - a, 3, 0.2, 0.3, '-y', m='terrazzo', side='tile')
        # low bookcases along each edge (on the upper side, facing the way down the room is not)
        zu = zl + dz
        spans = [(rim + 0.1, 6.9), (9.1, 13.9), (18.1, 22.9), (25.1, W - rim - 0.1)]
        for (a, b) in spans:
            R.shelf(b, e, zu, b - a, '-y', rows=2, frame='walnut', crown=True)
    # the grand stair from the north rim down to the lowest tier
    flight(R, 14.0, N0 - 2.7, -3 * dz, 4.0, 9, 0.2, 0.3, '+y', m='terrazzo', side='tile', rails='LR')
    # the rim's balustrade
    for (a, b) in ((edges[0], N0),):
        balus(R, rim - 0.12, a, rim - 0.12, N0 + 0.1, 0.0)
        balus(R, W - rim + 0.12, a, W - rim + 0.12, N0 + 0.1, 0.0)
    balus(R, rim - 0.12, N0 + 0.12, 14.0, N0 + 0.12, 0.0)
    balus(R, 18.0, N0 + 0.12, W - rim + 0.12, N0 + 0.12, 0.0)
    # stacks on each tier, running down the slope, with aisles on the door lines
    for (y0, z, y1) in tiers:
        a, b = y0 + 1.1, y1 - 1.1
        if y0 < 1: a = 3.2
        if y1 > N0 - 1: b = N0 - 3.4
        for x in (5.6, 10.4, 21.6, 26.4):
            stack2_ax(R, x, a, x, b, z, 6, frame='oak', crown='walnut', ends='walnut')
        # a lamp over each aisle
        for x in (8.0, 16.0, 24.0):
            lamp(R, x, (y0 + y1) / 2, 4.2, 0.24, chain=TOP - 0.1)
    # skylights over the tiers
    for (y0, z, y1) in tiers:
        yc = (y0 + y1) / 2
        R.light(box(6.0, yc - 0.8, TOP - 0.16, W - 6.0, yc + 0.8, TOP - 0.14, 'e_sky'))
    # books on the rim walls
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), rows=9, frame='walnut')
    # lights that stay on: step lights at the stairs
    for k, e in enumerate(edges):
        zl = -dz * (k + 1)
        for (a, b) in stairs_x:
            for x in (a + 0.1, b - 0.1):
                R.light(box(x - 0.05, e + 0.35, zl + 0.05, x + 0.05, e + 0.55, zl + 0.12, 'e_pool'))
    # walkers: round the rim, and down the middle
    loop(R, ((1.8, 2.0), (8, 2.0), (16, 2.0), (24, 2.0), (W - 1.8, 2.0), (W - 1.8, 16), (W - 1.8, W - 1.8), (16, W - 1.8), (1.8, W - 1.8), (1.8, 16)))
    mid = [R.navpt(16, 5.0, 0.0), R.navpt(16, 12.0, -dz), R.navpt(16, 18.0, -2 * dz), R.navpt(16, 24.0, -3 * dz), R.navpt(16, W - 1.8, 0.0)]
    R.link(*mid)
    R.link(R.navpt(16, 2.0), mid[0])
    R.spot('probe', 16, 12, 1.2)
    R.meta.update(label='The Terraces of Stacks', weight=6,
                  blurb='The floor goes down in steps, and the shelves go down with it, the way a hillside goes down to a river. There is no river.')
    R.meta['box'] = [[T, -1.8, T], [W - T, TOP - 0.1, W - T]]
    return R
