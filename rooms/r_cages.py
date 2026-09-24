"""The Archive Cages: ranges of shelves locked in iron cages, narrow walkways between them, bare
bulbs in wire guards. In the middle a spiral stair in a cage of its own climbs to a hatch that is painted on."""
from lib import *
from kit_b import *


def bars_x(R, x0, x1, y, z0, z1, step=0.3, t=0.035):
    """A row of thin bars along x at y (each bar two faces, front and back)."""
    n = max(1, int(round((x1 - x0) / step)))
    for k in range(n + 1):
        x = x0 + k * (x1 - x0) / n
        R.nocol.add(quad(x - t / 2, x + t / 2, y - t / 2, z0, z1, 'iron', '-y'))
        R.nocol.add(quad(x - t / 2, x + t / 2, y + t / 2, z0, z1, 'iron', '+y'))


def bars_y(R, y0, y1, x, z0, z1, step=0.3, t=0.035):
    n = max(1, int(round((y1 - y0) / step)))
    for k in range(n + 1):
        y = y0 + k * (y1 - y0) / n
        R.nocol.add(quad(y - t / 2, y + t / 2, x - t / 2, z0, z1, 'iron', '-x'))
        R.nocol.add(quad(y - t / 2, y + t / 2, x + t / 2, z0, z1, 'iron', '+x'))


def cage(R, x0, y0, x1, y1, h=3.0, rows=5, open_side=None):
    # shelves back to back down the middle
    xm = (x0 + x1) / 2
    L = y1 - y0 - 0.3
    R.shelf(xm - 0.01, y0 + 0.15, 0, L, '-x', rows=rows, frame='walnut', depth=0.32, solid=False, crown=False)
    R.shelf(xm + 0.01, y0 + 0.15 + L, 0, L, '+x', rows=rows, frame='walnut', depth=0.32, solid=False, crown=False, sides=False)
    # the cage
    bars_y(R, y0, y1, x0, 0.05, h)
    bars_y(R, y0, y1, x1, 0.05, h)
    bars_x(R, x0, x1, y0, 0.05, h)
    bars_x(R, x0, x1, y1, 0.05, h)
    for z in (0.0, h - 0.06):
        for (a, b, c, d) in ((x0 - 0.03, y0 - 0.03, x0 + 0.03, y1 + 0.03), (x1 - 0.03, y0 - 0.03, x1 + 0.03, y1 + 0.03),
                             (x0, y0 - 0.03, x1, y0 + 0.03), (x0, y1 - 0.03, x1, y1 + 0.03)):
            R.nocol.add(box(a, b, z, c, d, z + 0.06, 'iron', skip=('-z',)))
    # a lid of bars
    n = int((y1 - y0) / 0.7)
    for k in range(1, n):
        y = y0 + k * (y1 - y0) / n
        R.nocol.add(box(x0, y - 0.02, h - 0.04, x1, y + 0.02, h, 'iron', skip=('-z', '+x', '-x')))
    # a padlock on the end
    R.nocol.add(box(xm - 0.07, y0 - 0.08, 1.1, xm + 0.07, y0 - 0.03, 1.28, 'brass'))
    R.col.add(box(x0 - 0.03, y0 - 0.03, 0, x1 + 0.03, y1 + 0.03, h, 'iron'))


def make():
    R = Room('cages', 1, 1, res=1024)
    H = TOP - 0.1
    shell(R, H, wall='tile', floor='slate', ceil='plaster')
    # eight cages in four columns, a cross aisle between the pairs
    for (x0, x1) in ((1.6, 2.8), (4.0, 5.2), (10.8, 12.0), (13.2, 14.4)):
        for (y0, y1) in ((1.3, 6.2), (9.8, 14.7)):
            cage(R, x0, y0, x1, y1)
    # shelves on the west and east walls
    wall_shelves(R, rows=9, frame='walnut', sides='WE')
    # the caged spiral stair in the middle, all the way to the ceiling
    cx = cy = 8.0
    turns = (H - 0.3) / 2.5
    R.nocol.add(helix(cx, cy, 0.14, 1.2, 0.3, 2.5, 0.0, turns * 2 * math.pi, 0.12, int(turns * 20), top='iron', side='iron', bottom='iron'))
    R.nocol.add(cyl(cx, cy, 0, H, 0.12, 10, side='iron', caps=False))
    for k in range(24):
        a = k * 2 * math.pi / 24
        R.nocol.add(box(-0.015, -0.015, 0, 0.015, 0.015, H, 'iron', skip=('-z', '+z')).xform(a, cx + math.cos(a) * 1.5, cy + math.sin(a) * 1.5))
    for z in (0.0, 2.7, 5.2):
        R.nocol.add(ring(cx, cy, z, z + 0.06, 1.46, 1.54, 20, top='iron', bottom='iron', inner='iron', outer='iron'))
    R.col.add(cyl(cx, cy, 0, H, 1.55, 16, side='iron', top='iron', bottom='iron'))
    # the hatch at the top: a brass-edged square that is only painted
    R.nocol.add(box(cx - 0.6, cy - 0.6, H - 0.02, cx + 0.6, cy + 0.6, H, 'brass'))
    R.nocol.add(box(cx - 0.5, cy - 0.5, H - 0.03, cx + 0.5, cy + 0.5, H - 0.02, 'walnut'))
    R.nocol.add(box(cx - 0.62, cy - 1.55, 0.95, cx - 0.5, cy - 1.5, 1.95, 'brass'))   # a gate, locked
    # bare bulbs in wire guards over the walkways, and a few hung high
    for x in (1.0, 3.4, 5.85, 10.15, 12.6, 15.0):
        for y in (2.5, 5.0, 11.0, 13.5):
            if x in (1.0, 15.0): continue
            R.nocol.add(cyl(x, y, 3.25, H, 0.01, 4, side='iron', caps=False))
            bulb(R, x, y, 3.15, 0.07, 'e_lamp')
            R.nocol.add(cyl(x, y, 3.05, 3.25, 0.11, 6, side='iron', caps=False))
    for (x, y) in ((3.4, 8.0), (12.6, 8.0), (8.0, 3.0), (8.0, 13.0)):
        R.nocol.add(cyl(x, y, 4.2, H, 0.01, 4, side='iron', caps=False))
        bulb(R, x, y, 4.1, 0.1, 'e_amber')
    R.light(box(cx - 0.3, cy - 0.3, H - 0.05, cx + 0.3, cy + 0.3, H - 0.03, 'e_dim'))
    # a trolley of books left in the aisle
    R.parts.add(box(3.1, 3.2, 0.3, 3.7, 4.2, 0.36, 'iron'))
    R.parts.add(box(3.1, 3.2, 0.8, 3.7, 4.2, 0.86, 'iron'))
    for k in range(6):
        R.nocol.add(box(3.15, 3.25 + k * 0.16, 0.86, 3.65, 3.38 + k * 0.16, 1.1 + 0.03 * (k % 3), 'leather'))
    for (x, y) in ((3.12, 3.22), (3.62, 3.22), (3.12, 4.12), (3.62, 4.12)):
        R.nocol.add(box(x, y, 0.1, x + 0.05, y + 0.05, 0.86, 'iron'))
        R.nocol.add(cyl(x + 0.025, y + 0.025, 0, 0.1, 0.05, 6, side='black', caps=True))
    loop(R, [(3.4, 7.8), (3.4, 1.0), (5.85, 1.0), (5.85, 5.5), (5.85, 6.3), (3.4, 7.8)], close=False)
    loop(R, [(1.2, 8.0), (3.4, 8.0), (6.0, 8.0), (6.2, 10.0), (8.0, 10.2), (10.0, 10.0), (10.2, 8.0), (12.6, 8.0), (C - 1.2, 8.0)], close=False)
    loop(R, [(8.0, 1.2), (8.0, 5.8), (10.0, 6.0), (10.2, 8.0)], close=False)
    loop(R, [(8.0, C - 1.2), (8.0, 10.2)], close=False)
    loop(R, [(6.0, 8.0), (6.0, 6.0), (8.0, 5.8)], close=False)
    R.spot('probe', 8, 3.2, 2.0)
    R.meta.update(label='The Archive Cages', weight=5,
                  blurb='The books here are kept behind bars, for their protection or for yours. Nobody has the keys. The stair in the middle goes all the way up to a hatch that is only painted on.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
