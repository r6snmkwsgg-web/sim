"""The Great Hall: two floors tall. A colonnaded gallery runs round the upper level, two long
stairs climb to it, a reflecting pool lies down the middle, and a coffered vault with a skylight
spine closes it all. Books from the floor to the vault."""
from lib import *


def make():
    R = Room('grand', 2, 2, levels=2, res=2048)
    R.sockets(wall='tile')
    W = R.W
    gw = 4.35                                  # gallery depth from the wall (void edge at gw)
    v0, v1 = gw, W - gw
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, TOP, 'tile', bottom='terrazzo', top='plaster'))          # ground floor
    R.cut(box(T - 0.02, T - 0.02, LH, W - T + 0.02, W - T + 0.02, LH + 4.2, 'tile', bottom='terrazzo', top='plaster'))    # gallery level
    R.cut(box(v0, v0, TOP - 0.2, v1, v1, LH + 4.3, 'tile'))                                                                 # the void through the slab
    spring = LH + 4.2
    pr = arch_profile(W / 2, v1 - v0, spring - 0.1, 0.1, 40, rise=3.3)
    R.cut(prism(pr, 'x', v0, v1, arch_mats(len(pr), 'tile', 'plaster')))
    # skylight spine in the vault
    R.cut(box(v0 + 2.0, W / 2 - 0.7, spring + 2.8, v1 - 2.0, W / 2 + 0.7, R.hi + 0.5, 'plaster'))
    R.light(box(v0 + 2.0, W / 2 - 0.7, R.hi - 0.08, v1 - 2.0, W / 2 + 0.7, R.hi - 0.05, 'e_sky'))
    # colonnade under the gallery edge
    st_x0_, st_x1_ = 8.8, 8.8 + 44 * 0.3
    for k in range(6):
        p = v0 + 0.4 + k * (v1 - v0 - 0.8) / 5
        for (x, y) in ((p, v0 + 0.35), (p, v1 - 0.35), (v0 + 0.35, p), (v1 - 0.35, p)):
            if y in (v0 + 0.35, v1 - 0.35) and st_x0_ - 0.6 < x < st_x1_ + 2.8: continue   # keep the stairs clear
            R.parts.add(cyl(x, y, 0, TOP - 0.18, 0.3, 24, side='tile', caps=False))
            R.parts.add(box(x - 0.42, y - 0.42, TOP - 0.45, x + 0.42, y + 0.42, TOP - 0.18, 'tile', skip=('+z',)))
    # gallery balustrade (with openings where the stairs arrive)
    ph = 1.0
    st_w, st_x0, rise, run, n = 2.2, 8.8, 8.0 / 44, 0.3, 44
    st_x1 = st_x0 + n * run
    def rail(x0, y0, x1, y1):
        R.parts.add(box(x0, y0, LH, x1, y1, LH + ph, 'tile', skip=('-z',)))
        R.parts.add(box(x0 - 0.03, y0 - 0.03, LH + ph, x1 + 0.03, y1 + 0.03, LH + ph + 0.06, 'brass'))
    rail(v0 - 0.2, v0 - 0.2, st_x1, v0)                          # south, broken where the stair lands
    rail(st_x1 + 2.2, v0 - 0.2, v1 + 0.2, v0)
    rail(v0 - 0.2, v1, st_x1, v1 + 0.2)
    rail(st_x1 + 2.2, v1, v1 + 0.2, v1 + 0.2)
    rail(v0 - 0.2, v0, v0, v1); rail(v1, v0, v1 + 0.2, v1)
    # two long flights, south and north, climbing east; each ends on a landing joined to the gallery
    for (y0, side) in ((v0 + 0.05, 1), (v1 - 0.05 - st_w, -1)):
        R.nocol.add(stairs(st_x0, y0, 0, st_w, n, rise, run, '+x', m='terrazzo', side='tile'))
        R.parts.add(box(st_x1, y0, TOP - 0.4, st_x1 + 2.2, y0 + st_w, LH, 'terrazzo', sides='tile'))
        # rails round the landing's two sides that face the void
        if side > 0:
            rail(st_x1, y0 + st_w - 0.2, st_x1 + 2.2, y0 + st_w)
            rail(st_x1 + 2.0, v0, st_x1 + 2.2, y0 + st_w - 0.2)
        else:
            rail(st_x1, y0, st_x1 + 2.2, y0 + 0.2)
            rail(st_x1 + 2.0, y0 + 0.2, st_x1 + 2.2, v1)
        # the ramp the feet actually use
        g = Geo()
        a, b = (st_x0 - 0.02, y0), (st_x1, y0 + st_w)
        ids = [g.vert(p) for p in ((a[0], a[1], 0.0), (b[0], a[1], LH), (b[0], b[1], LH), (a[0], b[1], 0.0))]
        g.face(ids, 'floor', [(0, 0)] * 4)
        R.col.add(g)
        # a tiled parapet, capped in brass, on the side over the aisle under the gallery
        ya, yb = (y0 - 0.02, y0 + 0.13) if side > 0 else (y0 + st_w - 0.13, y0 + st_w + 0.02)
        R.parts.add(slope_box(st_x0, st_x1, ya, yb, 0.0, LH - 0.3, rise + ph, LH + rise + ph, 'tile'))
        R.parts.add(slope_box(st_x0 - 0.03, st_x1, ya - 0.03, yb + 0.03, rise + ph, LH + rise + ph, rise + ph + 0.06, LH + rise + ph + 0.06, 'brass'))
        # a handrail on the side over the void
        yy = y0 + st_w if side > 0 else y0
        for k in range(0, n, 4):
            x = st_x0 + k * run + run / 2
            R.parts.add(box(x - 0.025, yy - 0.025, (k + 1) * rise, x + 0.025, yy + 0.025, (k + 1) * rise + 0.95, 'brass'))
        g = Geo()
        h0, h1 = rise + 0.95, LH + 0.95
        ids = [g.vert(p) for p in ((st_x0, yy - 0.04, h0), (st_x1, yy - 0.04, h1), (st_x1, yy + 0.04, h1), (st_x0, yy + 0.04, h0),
                                   (st_x0, yy - 0.04, h0 + 0.06), (st_x1, yy - 0.04, h1 + 0.06), (st_x1, yy + 0.04, h1 + 0.06), (st_x0, yy + 0.04, h0 + 0.06))]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            g.face([ids[i] for i in f], 'brass', [(0, 0)] * 4)
        R.parts.add(g.fix())
    # reflecting pool down the middle of the ground floor
    R.pool(9.0, 12.4, W - 9.0, W - 12.4, 0.45, m='cobalt')
    for x in (12.0, 16.0, 20.0):
        R.light(box(x - 0.2, 12.41, -0.34, x + 0.2, 12.45, -0.2, 'e_pool'))
        R.light(box(x - 0.2, W - 12.45, -0.34, x + 0.2, W - 12.41, -0.2, 'e_pool'))
    # lamps under the gallery
    for k in range(8):
        p = 2.2 + k * (W - 4.4) / 7
        for (x, y) in ((p, 2.2), (p, W - 2.2), (2.2, p), (W - 2.2, p)):
            R.light(cyl(x, y, TOP - 0.24, TOP - 0.21, 0.32, 20, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # books: tall cases on the ground floor walls, and again round the gallery
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        for (z, rows) in ((0, 12), (LH, 8)):
            R.shelf(a, T, z, b - a, '+y', rows=rows, frame='wood')
            R.shelf(b, W - T, z, b - a, '-y', rows=rows, frame='wood')
            R.shelf(T, b, z, b - a, '+x', rows=rows, frame='wood')
            R.shelf(W - T, a, z, b - a, '-x', rows=rows, frame='wood')
    # walkers
    ring0 = [R.navpt(x, y) for (x, y) in ((2.2, 2.2), (16, 2.2), (W - 2.2, 2.2), (W - 2.2, 16), (W - 2.2, W - 2.2), (16, W - 2.2), (2.2, W - 2.2), (2.2, 16))]
    R.link(*ring0, ring0[0])
    mid = [R.navpt(x, y) for (x, y) in ((7.0, 10.5), (W - 7.0, 10.5), (W - 7.0, W - 10.5), (7.0, W - 10.5))]
    R.link(*mid, mid[0]); R.link(ring0[7], mid[0]); R.link(ring0[3], mid[1])
    ring1 = [R.navpt(x, y, LH) for (x, y) in ((2.2, 2.2), (16, 2.2), (W - 2.2, 2.2), (W - 2.2, 16), (W - 2.2, W - 2.2), (16, W - 2.2), (2.2, W - 2.2), (2.2, 16))]
    R.link(*ring1, ring1[0])
    R.spot('probe', 16, 16, 4.0)
    R.meta['label'] = 'The Great Hall'
    R.meta['box'] = [[T, -0.45, T], [W - T, R.hi, W - T]]
    return R
