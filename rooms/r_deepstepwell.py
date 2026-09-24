"""The Deep Stepwell: each floor is a square funnel of terraces stepping down to a square hole, every
riser a shelf of books, little stairs zigzagging down. Through the hole, the funnel of the floor
below, and below that another. The underside of the funnel above hangs over you like a ceiling of steps."""
from lib import *
from kit_e import *


def frame(g, a, b, z0, z1, m='tile', top=None, bottom=None, cx=C / 2, cy=C / 2):
    """A square ring between half-widths a and b (four boxes, no overlaps)."""
    for bx in ((-b, -b, b, -a), (-b, a, b, b), (-b, -a, -a, a), (a, -a, b, a)):
        g.add(box(cx + bx[0], cy + bx[1], z0, cx + bx[2], cy + bx[3], z1, m, top=top, bottom=bottom))
    return g


def make():
    R = Room('deepstepwell', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets()
    cx = cy = C / 2
    w = [5.65, 4.3, 2.95, 1.5]                 # half-widths: rim edge, then each terrace's inner edge
    zt = [0.0, -0.7, -1.4, -2.1]             # rim, terraces 1..3
    thick = 1.3
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, TOP, 'tile', bottom='floor', top='plaster'))
    R.cut(box(cx - w[0], cy - w[0], -0.6, cx + w[0], cy + w[0], 0.1, 'tile'))        # the funnel goes through the slab
    # the terraces: square rings, each 1.3 m deep, so the underside steps like the top
    g = Geo()
    frame(g, w[0], w[0] + 0.3, -thick, -0.4, 'tile')                                   # a skirt under the rim's edge
    for k in range(1, 4):
        frame(g, w[k], w[k - 1], zt[k] - thick, zt[k], 'tile', top='terrazzo' if k == 3 else 'floor')
    R.parts.add(g)
    # light strips on the underside of every step (they light the floor below)
    for k in range(0, 4):
        a = w[k] + 0.08 if k else w[0] + 0.05
        zb = (zt[k] - thick) if k else -thick
        R.light(frame(Geo(), a, a + 0.2, zb - 0.03, zb - 0.005, 'e_panel'))
    # per side: the risers are shelves of books, and three little flights zigzag down
    fw, n, rs, rn = 0.6, 4, 0.175, 0.3
    L = n * rn
    for q in range(4):
        ang = q * math.pi / 2
        spans = {1: (0.1, 1.7), 2: (-1.7, -0.1), 3: (0.1, 1.7)}
        for k in (1, 2, 3):
            wk, z = w[k - 1], zt[k]
            if k in (1, 3): flight_rot(R, ang, 1.6, -wk, z, fw, n, rs, rn, '-x', m='terrazzo', side='tile')
            else:           flight_rot(R, ang, -1.6, -wk, z, fw, n, rs, rn, '+x', m='terrazzo', side='tile')
            f0, f1 = spans[k]
            for (u0, u1) in ((-wk + 0.36, f0), (f1, wk - 0.36)):
                if u1 - u0 < 0.5: continue
                bx, by = rot_pt(ang, u0, -wk)
                R.shelf(bx, by, z, u1 - u0, math.pi / 2 + ang, rows=1, row_h=0.5, frame='walnut', crown=False)
            # a step light at the foot of each flight
            lx, ly = rot_pt(ang, 1.75 if k != 2 else -1.75, -wk + 0.3)
            R.light(box(lx - 0.04, ly - 0.04, z + 0.02, lx + 0.04, ly + 0.04, z + 0.1, 'e_pool'))
    # the rail round the hole
    h = w[3] + 0.04
    rail(R, [(cx - h, cy - h, zt[3]), (cx + h, cy - h, zt[3]), (cx + h, cy + h, zt[3]), (cx - h, cy + h, zt[3]), (cx - h, cy - h, zt[3])])
    for (x, y) in ((cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)):
        R.parts.add(box(x - 0.06, y - 0.06, zt[3], x + 0.06, y + 0.06, zt[3] + 1.0, 'bronze', skip=('-z',)))
        R.light(sphere(x, y, zt[3] + 1.12, 0.09, 8, 4, 'e_amber'))
    # tall bookcases round the rim, lamps in the corners
    wall_shelves(R, rows=8, frame='wood', segs_x=CELL_SEGS, segs_y=CELL_SEGS, sides='SNWE')
    for (x, y) in ((1.4, 1.4), (C - 1.4, 1.4), (1.4, C - 1.4), (C - 1.4, C - 1.4)):
        R.light(cyl(x, y, TOP - 0.06, TOP - 0.03, 0.55, 24, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # walkers: the rim, and a loop on each terrace, joined by the flights of the south side
    def sq(v, z):
        pts = [(-v, -v), (0, -v), (v, -v), (v, 0), (v, v), (0, v), (-v, v), (-v, 0)]
        ids = [R.navpt(cx + a, cy + b, z) for (a, b) in pts]
        R.link(*ids, ids[0]); return ids
    rim = sq(6.6, 0.0); t1 = sq(4.6, zt[1]); t2 = sq(3.35, zt[2]); t3 = sq(1.95, zt[3])
    a = R.navpt(cx + 0.55, cy - 5.3, 0.0); b = R.navpt(cx + 1.9, cy - 5.0, zt[1]); R.link(rim[1], a, b, t1[1])
    a = R.navpt(cx - 0.55, cy - 3.95, zt[1]); b = R.navpt(cx - 1.9, cy - 3.65, zt[2]); R.link(t1[1], a, b, t2[1])
    a = R.navpt(cx + 0.55, cy - 2.6, zt[2]); b = R.navpt(cx + 1.9, cy - 2.3, zt[3]); R.link(t2[1], a, b, t3[1])
    for (x, y, f) in ((cx, cy - w[3] - 0.5, math.pi / 2), (cx, cy + w[3] + 0.5, -math.pi / 2), (cx - w[3] - 0.5, cy, 0), (cx + w[3] + 0.5, cy, math.pi)):
        R.spot('edge', x, y, zt[3], f)
    R.spot('probe', cx, cy, 1.5)
    R.meta.update(label='The Deep Stepwell', weight=30,
                  blurb='The floor steps down, shelf by shelf, to a square hole. Through it you can see the same steps going down to the same hole, and the underside of this one hanging over them.')
    R.meta['shaft'] = [cx - w[3], cy - w[3], cx + w[3], cy + w[3]]
    R.meta['box'] = [[T, zt[3], T], [C - T, TOP, C - T]]
    return R
