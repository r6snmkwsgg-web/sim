"""The Descent: a staircase as wide as the room goes down into a sunken reading floor, and another comes
up out of it on the far side. Down there, long tables and green lamps; up here, balustrades and books."""
from lib import *
from kit_c import *


def make():
    R = Room('sunkenstair', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    shell(R, TOP, floor='floor', ceil='plaster')
    x0, x1, y0, y1 = 2.6, C - 2.6, 2.6, C - 2.6
    n, rise, run = 10, 0.19, 0.3
    dep = n * rise
    for k in range(n):
        R.cut(box(x0, y0 + k * run, -(k + 1) * rise, x1, y1 - k * run, 0.3, 'tile', bottom='terrazzo', top='tile'))
    f0, f1 = y0 + n * run, y1 - n * run            # the sunken floor
    # step lights in a few risers
    for k in (2, 5, 8):
        for x in (4.0, 8.0, 12.0):
            for (y, z) in ((y0 + k * run + 0.005, -k * rise - 0.12), (y1 - k * run - 0.005, -k * rise - 0.12)):
                R.light(box(x - 0.18, y - 0.004, z - 0.05, x + 0.18, y + 0.004, z, 'e_pool'))
    # stone balustrades along both side ledges
    R.parts.add(balustrade(x0 - 0.22, y0, x0, y1, 0.0, h=0.95))
    R.parts.add(balustrade(x1, y0, x1 + 0.22, y1, 0.0, h=0.95))
    for y in (y0, y1):
        for x in (x0 - 0.11, x1 + 0.11):
            R.parts.add(box(x - 0.2, y - 0.2, 0, x + 0.2, y + 0.2, 1.15, 'tile', skip=('-z',)))
            R.light(sphere(x, y, 1.32, 0.14, 12, 6, 'e_lamp'))
    # books in the sunken floor's side walls
    R.shelf(x0, f1 - 0.1, -dep, f1 - f0 - 0.2, '+x', rows=4, frame='walnut')
    R.shelf(x1, f0 + 0.1, -dep, f1 - f0 - 0.2, '-x', rows=4, frame='walnut')
    # reading tables down on the floor
    for tx in (4.9, 8.0, 11.1):
        table_at(R, tx - 0.55, 6.9, tx + 0.55, 9.1, -dep, top='leather')
        for ty in (7.4, 8.6):
            desk_lamp(R, tx, ty, -dep + 0.76)
        for ty in (7.3, 8.7):
            chair(R, tx - 0.85, ty, 0.0, z=-dep); chair(R, tx + 0.85, ty, math.pi, z=-dep)
        pendant(R, tx, 8.0, -dep + 2.7, TOP, r=0.35)
    open_book(R, 4.9, 8.0, -dep + 0.76, 0.3)
    book_pile(R, 11.1, 7.9, -dep + 0.76, 6, seed=17)
    # a long skylight over the sunken floor
    for k in range(4):
        a = x0 + 0.3 + k * (x1 - x0 - 0.6) / 4
        g = (a + 0.15, f0 - 0.25, a + (x1 - x0 - 0.6) / 4 - 0.15, f1 + 0.25)
        R.cut(box(g[0], g[1], TOP - 0.2, g[2], g[3], R.hi + 0.5, 'plaster'))
        R.light(box(g[0], g[1], R.hi - 0.08, g[2], g[3], R.hi - 0.05, 'e_sky'))
    # books round the upper walls
    wall_shelves(R, rows=12, frame='walnut')
    # walkers: round the ledges, down the stairs and across the floor
    ring = std_nav(R, 1.4)
    R.link(ring[1], R.navpt(8, f0 + 0.6, -dep), R.navpt(8, f1 - 0.6, -dep), ring[5])
    R.link(R.navpt(3.5, f0 + 0.7, -dep), R.navpt(C - 3.5, f0 + 0.7, -dep))
    R.spot('probe', 8, 4.2, 0.2)
    R.meta.update(label='The Descent', weight=6,
                  blurb='A staircase as wide as the room goes down to a reading floor and comes up again on the other side. Nobody has ever gone down it and come up the same side.')
    R.meta['box'] = [[T, -dep, T], [C - T, TOP, C - T]]
    return R
