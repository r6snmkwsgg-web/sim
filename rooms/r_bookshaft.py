"""The Book Shaft: a shaft whose four walls are bookcases from bottom to top, however far that is.
A narrow iron walkway rings each floor; lamps hang in the void on cords that never end."""
from lib import *
from kit_e import *


def make():
    R = Room('bookshaft', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets()
    cx = cy = C / 2
    f = T + 0.36                                 # the face of the bookcases
    v = C / 2 - (f + 1.3)                        # half-width of the void (walkway 1.3 m)
    vd = v - 0.8                                 # at the doors the walkway widens into a landing
    R.cut(box(T - 0.02, T - 0.02, -LH, C - T + 0.02, C - T + 0.02, 2 * LH, 'tile'))
    # the walkway: an iron grating ring, landings at the doors
    g = Geo()
    for (x0, y0, x1, y1) in ((T, T, C - T, cy - v), (T, cy + v, C - T, C - T), (T, cy - v, cx - v, cy + v), (cx + v, cy - v, C - T, cy + v)):
        g.add(box(x0, y0, -0.18, x1, y1, 0.0, 'iron', top='oak'))
    hw = 1.8
    for (x0, y0, x1, y1) in ((cx - hw, cy - v, cx + hw, cy - vd), (cx - hw, cy + vd, cx + hw, cy + v), (cx - v, cy - hw, cx - vd, cy + hw), (cx + vd, cy - hw, cx + v, cy + hw)):
        g.add(box(x0, y0, -0.18, x1, y1, 0.0, 'iron', top='oak'))
    R.parts.add(g)
    # the rail round the void, stepping out round the landings
    pts = [(cx - v, cy - v), (cx - hw, cy - v), (cx - hw, cy - vd), (cx + hw, cy - vd), (cx + hw, cy - v), (cx + v, cy - v),
           (cx + v, cy - hw), (cx + vd, cy - hw), (cx + vd, cy + hw), (cx + v, cy + hw), (cx + v, cy + v),
           (cx + hw, cy + v), (cx + hw, cy + vd), (cx - hw, cy + vd), (cx - hw, cy + v), (cx - v, cy + v),
           (cx - v, cy + hw), (cx - vd, cy + hw), (cx - vd, cy - hw), (cx - v, cy - hw), (cx - v, cy - v)]
    # pull the rail a hair inside the walkway edge
    def inset(p):
        return (p[0] + (0.04 if p[0] < cx else -0.04), p[1] + (0.04 if p[1] < cy else -0.04), 0.0)
    rail(R, [inset(p) for p in pts], h=1.0)
    # light strips under the walkway's edge, lighting the books below
    for (x0, y0, x1, y1) in ((f, cy - v - 0.35, C - f, cy - v - 0.15), (f, cy + v + 0.15, C - f, cy + v + 0.35),
                             (cx - v - 0.35, cy - v, cx - v - 0.15, cy + v), (cx + v + 0.15, cy - v, cx + v + 0.35, cy + v)):
        R.light(box(x0, y0, -0.21, x1, y1, -0.18, 'e_panel'))
    # the walls: bookcases the full height of the floor, so they run on unbroken above and below
    sx = ((f, 6.3), (9.7, C - f))
    sy = ((T, 6.3), (9.7, C - T))
    full = dict(rows=18, row_h=0.44, top_gap=0.045, crown=False, frame='walnut')
    wall_shelves(R, sides='SN', segs_x=sx, segs_y=(), **full)
    wall_shelves(R, sides='WE', segs_x=(), segs_y=sy, **full)
    over = dict(rows=8, row_h=0.44, top_gap=0.145, crown=False, frame='walnut')
    wall_shelves(R, sides='SN', segs_x=((6.3, 9.7),), segs_y=(), z=4.3, **over)
    wall_shelves(R, sides='WE', segs_x=(), segs_y=((6.3, 9.7),), z=4.3, **over)
    # rolling ladders leaning on the shelves here and there (they go nowhere)
    for (x, y, s, ax) in ((4.0, f, 1, 'y'), (12.5, C - f, -1, 'y'), (f, 11.5, 1, 'x'), (C - f, 3.8, -1, 'x')):
        gg = Geo()
        for d in (-0.24, 0.24):
            if ax == 'y': gg.add(beam((x + d, y + s * 0.7, 0.0), (x + d, y + s * 0.05, 4.2), 0.05, 0.06, 'oak'))
            else:         gg.add(beam((x + s * 0.7, y + d, 0.0), (x + s * 0.05, y + d, 4.2), 0.05, 0.06, 'oak'))
        for k in range(1, 14):
            t = k / 14
            if ax == 'y': gg.add(box(x - 0.24, y + s * 0.7 * (1 - t) - 0.02, 4.2 * t, x + 0.24, y + s * 0.7 * (1 - t) + 0.02, 4.2 * t + 0.035, 'oak'))
            else:         gg.add(box(x + s * 0.7 * (1 - t) - 0.02, y - 0.24, 4.2 * t, x + s * 0.7 * (1 - t) + 0.02, y + 0.24, 4.2 * t + 0.035, 'oak'))
        R.nocol.add(gg)
    # lamps hanging in the void on endless cords, a lamp on each cord every floor
    k = 0
    for gx in (-3.6, 0.0, 3.6):
        for gy in (-3.6, 0.0, 3.6):
            x, y = cx + gx, cy + gy
            R.nocol.add(cyl(x, y, -0.4, 7.6, 0.012, 5, side='iron', caps=False))
            z = 3.4 + 1.3 * ((k * 5) % 3) / 2
            R.nocol.add(cyl(x, y, z + 0.18, z + 0.32, 0.12, 12, side='brass', top='brass', bottom='brass'))
            R.light(sphere(x, y, z, 0.2, 12, 6, 'e_lamp' if (gx, gy) != (0.0, 0.0) else 'e_amber'))
            k += 1
    # small night lamps on the rail at each landing
    for (x, y) in ((cx - hw + 0.04, cy - vd + 0.04), (cx + hw - 0.04, cy + vd - 0.04), (cx - vd + 0.04, cy + hw - 0.04), (cx + vd - 0.04, cy - hw + 0.04)):
        R.light(sphere(x, y, 1.12, 0.07, 8, 4, 'e_amber'))
    # walkers: round the ring
    m = f + 0.65
    loop(R, [(m, m), (cx, m), (C - m, m), (C - m, cy), (C - m, C - m), (cx, C - m), (m, C - m), (m, cy)])
    for (x, y, fa) in ((cx, cy - vd - 0.6, math.pi / 2), (cx, cy + vd + 0.6, -math.pi / 2), (cx - vd - 0.6, cy, 0), (cx + vd + 0.6, cy, math.pi)):
        R.spot('edge', x, y, 0, fa)
    R.spot('probe', 2.6, 2.6, 1.7)
    R.meta.update(label='The Book Shaft', weight=35,
                  blurb='Four walls of books, straight up and straight down, and a narrow walkway round each floor. Somewhere in there is the one you want. It is probably not on this floor.')
    R.meta['shaft'] = [cx - v, cy - v, cx + v, cy + v]
    R.meta['box'] = [[T, 0, T], [C - T, LH, C - T]]
    return R
