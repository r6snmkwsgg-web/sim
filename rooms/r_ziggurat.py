"""The Ziggurat: a stepped pyramid of stone and books fills the room, every riser a row of spines;
four stairs climb its faces to a lectern under a square of sky. Lamps burn at its corners."""
from lib import *
from kit_c import *


def make():
    R = Room('ziggurat', 1, 1, res=1024)
    R.sockets(floor='terrazzo', wall='tile')
    shell(R, TOP, floor='terrazzo', ceil='plaster')
    cx = cy = 8.0
    n, rh = 7, 0.45                       # tiers, riser
    s0, st = 5.5, 1.5                     # half-size of the base and of the top
    tr = (s0 - st) / (n - 1)
    w = 1.3                               # stair width
    hw = w / 2
    bd = 0.3                              # book depth
    cap = 0.07
    for k in range(n - 1):
        s = s0 - k * tr
        z0, z1 = k * rh, (k + 1) * rh
        for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            xa, xb = sorted((cx + sx * s, cx + sx * hw)); ya, yb = sorted((cy + sy * s, cy + sy * hw))
            # the core, set back from the two outer faces for the books
            ca, cb = (xa + bd, xb) if sx < 0 else (xa, xb - bd)
            da, db = (ya + bd, yb) if sy < 0 else (ya, yb - bd)
            R.parts.add(box(ca, da, z0, cb, db, z1 - cap, 'tile', skip=('-z', '+z')))
            R.parts.add(box(xa, ya, z1 - cap, xb, yb, z1, 'tile', top='tile', skip=('-z',)))
            px = xa if sx < 0 else xb - bd; py = ya if sy < 0 else yb - bd
            R.parts.add(box(px, py, z0, px + bd, py + bd, z1 - cap, 'tile', skip=('-z', '+z')))
            # a row of books in each outer riser
            L = (xb - xa) - bd - 0.04
            hb = rh - cap
            if sy < 0: book_riser(R, (xa + bd if sx < 0 else xa) + L + 0.02, da, L, z0, hb, '-y', depth=bd)
            else: book_riser(R, (xa + bd if sx < 0 else xa) + 0.02, db, L, z0, hb, '+y', depth=bd)
            Ly = (yb - ya) - bd - 0.04
            if sx < 0: book_riser(R, ca, (ya + bd if sy < 0 else ya) + 0.02, Ly, z0, hb, '-x', depth=bd)
            else: book_riser(R, cb, (ya + bd if sy < 0 else ya) + Ly + 0.02, Ly, z0, hb, '+x', depth=bd)
    # the summit
    top = n * rh
    R.parts.add(box(cx - st, cy - st, 0, cx + st, cy + st, top, 'tile', top='mosaic', skip=('-z',)))
    # four stairs up the middle of the faces
    ns = 14
    run = (s0 - st) / ns
    ri = top / ns
    R.flight(cx - hw, cy - s0, 0, w, ns, ri, run, '+y', m='tile', side='tile')
    R.flight(cx - hw, cy + s0, 0, w, ns, ri, run, '-y', m='tile', side='tile')
    R.flight(cx - s0, cy - hw, 0, w, ns, ri, run, '+x', m='tile', side='tile')
    R.flight(cx + s0, cy - hw, 0, w, ns, ri, run, '-x', m='tile', side='tile')
    # the lectern on top, candles round it, and the sky over it
    lectern(R, cx, cy + 0.2, math.pi / 2, z=top)
    for (x, y) in ((cx - 1.1, cy - 1.1), (cx + 1.1, cy - 1.1), (cx + 1.1, cy + 1.1), (cx - 1.1, cy + 1.1)):
        candle_stand(R, x, y, top, h=0.9)
    R.cut(box(cx - 1.6, cy - 1.6, TOP - 0.2, cx + 1.6, cy + 1.6, R.hi + 0.5, 'plaster'))
    R.light(box(cx - 1.6, cy - 1.6, R.hi - 0.08, cx + 1.6, cy + 1.6, R.hi - 0.05, 'e_sky'))
    # lamps on the pyramid's corners, on bronze standards standing on the third tier
    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        c = s0 - 2 * tr - 0.3
        x, y, z = cx + sx * c, cy + sy * c, 3 * rh
        R.parts.add(box(x - 0.2, y - 0.2, z, x + 0.2, y + 0.2, z + 0.2, 'bronze', skip=('-z',)))
        R.parts.add(cyl(x, y, z + 0.2, z + 2.0, 0.045, 8, side='bronze', caps=False))
        R.parts.add(cyl(x, y, z + 2.0, z + 2.08, 0.22, 12, side='bronze', top='bronze', bottom='bronze'))
        R.light(sphere(x, y, z + 2.28, 0.2, 12, 6, 'e_lamp'))
    # tall cases round the walls, and small night lamps over the doors
    wall_shelves(R, rows=11, frame='walnut')
    for (x, y) in ((8, T + 0.1), (8, C - T - 0.1), (T + 0.1, 8), (C - T - 0.1, 8)):
        R.light(box(x - 0.12, y - 0.1, 4.4, x + 0.12, y + 0.1, 4.52, 'e_amber'))
    # walkers: round the foot, and over the top by the stairs
    ring = std_nav(R, 1.5)
    s_ = R.navpt(cx, cy - st + 0.4, top); n_ = R.navpt(cx, cy + st - 0.4, top)
    w_ = R.navpt(cx - st + 0.4, cy, top); e_ = R.navpt(cx + st - 0.4, cy, top)
    R.link(ring[1], s_, w_, n_, e_, s_); R.link(n_, ring[5]); R.link(w_, ring[7]); R.link(e_, ring[3])
    R.spot('read', cx, cy - 0.4, top, math.pi / 2)
    R.spot('probe', 3.0, 3.0, 1.7)
    R.meta.update(label='The Ziggurat', weight=5,
                  blurb='Someone stacked the books into a pyramid and climbed it, and left the book at the top open. The page is blank on both sides.')
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]
    return R
