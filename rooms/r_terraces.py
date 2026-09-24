"""The Terraces: the floor climbs in broad terraces, square, then turned diamond-wise, then square again,
to a dais with a reading table; every riser is a row of books. The ceiling climbs the same way, upside down."""
from lib import *
from kit_c import *


def make():
    R = Room('terraces', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    H = 5.2
    shell(R, H, floor='floor', ceil='plaster')
    cx = cy = 8.0
    rh, cap, bd = 0.45, 0.07, 0.3
    sq1, dia, sq3 = 5.4, 5.0, 2.0          # half-size of the first square, half-diagonal of the diamond, dais
    def diamond(r):
        return [(cx + r, cy), (cx, cy + r), (cx - r, cy), (cx, cy - r)]
    # terrace 1: a square
    z0 = 0.0
    R.parts.add(box(cx - sq1 + bd, cy - sq1 + bd, z0, cx + sq1 - bd, cy + sq1 - bd, z0 + rh - cap, 'tile', skip=('-z', '+z')))
    R.parts.add(box(cx - sq1, cy - sq1, z0 + rh - cap, cx + sq1, cy + sq1, z0 + rh, 'tile', top='terrazzo', skip=('-z',)))
    # terrace 2: a diamond
    z1 = rh
    R.parts.add(poly_prism(diamond(dia - bd * math.sqrt(2)), z1, z1 + rh - cap, side='tile', top='tile', bottom='tile'))
    R.parts.add(poly_prism(diamond(dia), z1 + rh - cap, z1 + rh, side='tile', top='floor', bottom='tile'))
    # the dais: a square again
    z2 = 2 * rh
    R.parts.add(box(cx - sq3 + bd, cy - sq3 + bd, z2, cx + sq3 - bd, cy + sq3 - bd, z2 + rh - cap, 'tile', skip=('-z', '+z')))
    R.parts.add(box(cx - sq3, cy - sq3, z2 + rh - cap, cx + sq3, cy + sq3, z2 + rh, 'tile', top='terrazzo', skip=('-z',)))
    top = 3 * rh
    # books in every riser
    hb = rh - cap
    for (s, z, tr) in ((sq1, z0, 0.02), (sq3, z2, 0.02)):
        L = 2 * (s - bd) - 2 * tr
        a0, a1 = cx - s + bd + tr, cx + s - bd - tr
        book_riser(R, a1, cy - s + bd, L, z, hb, '-y')
        book_riser(R, a0, cy + s - bd, L, z, hb, '+y')
        book_riser(R, cx - s + bd, a0, L, z, hb, '-x')
        book_riser(R, cx + s - bd, a1, L, z, hb, '+x')
        for (px, py) in ((cx - s, cy - s), (cx + s - bd, cy - s), (cx + s - bd, cy + s - bd), (cx - s, cy + s - bd)):
            R.parts.add(box(px, py, z, px + bd, py + bd, z + hb, 'tile', skip=('-z', '+z')))
    ri = dia - bd * math.sqrt(2)
    V = diamond(ri)
    for k in range(4):
        p, q = V[k], V[(k + 1) % 4]
        # outward normal of the edge p->q (counter-clockwise polygon): to the right of the direction
        d = math.atan2(q[1] - p[1], q[0] - p[0])
        face = d - math.pi / 2
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        tr = 0.55
        ux, uy = math.cos(d), math.sin(d)
        # a shelf facing `face` starts at its left end seen from the front, i.e. toward q
        sx, sy = q[0] - ux * tr, q[1] - uy * tr
        book_riser(R, sx, sy, L - 2 * tr, z1, hb, face)
    # fill the pockets at the diamond's corners
    O = diamond(dia)
    for k in range(4):
        I, Oo = V[k], O[k]
        for nb in ((k + 1) % 4, (k + 3) % 4):
            ux, uy = V[nb][0] - I[0], V[nb][1] - I[1]; l = math.hypot(ux, uy); ux, uy = ux / l * 0.56, uy / l * 0.56
            quad = [I, (I[0] + ux, I[1] + uy), (Oo[0] + ux, Oo[1] + uy), Oo]
            ar = sum(quad[i][0] * quad[(i + 1) % 4][1] - quad[(i + 1) % 4][0] * quad[i][1] for i in range(4))
            if ar < 0: quad = quad[::-1]
            R.parts.add(poly_prism(quad, z1, z1 + hb, side='tile', top='tile', bottom='tile'))
    # on the dais: a reading table, lamps, chairs
    table_at(R, cx - 1.1, cy - 0.5, cx + 1.1, cy + 0.5, top, top='leather')
    desk_lamp(R, cx - 0.6, cy, top + 0.76); desk_lamp(R, cx + 0.6, cy, top + 0.76)
    open_book(R, cx, cy - 0.15, top + 0.76, 0.05)
    book_pile(R, cx + 0.2, cy + 0.25, top + 0.76, 4, seed=21)
    for x in (cx - 0.55, cx + 0.55):
        chair(R, x, cy - 0.95, math.pi / 2, z=top); chair(R, x, cy + 0.95, -math.pi / 2, z=top)
    # the ceiling climbs the same terraces, inverted, to a skylight
    R.cut(box(cx - sq1, cy - sq1, H - 0.05, cx + sq1, cy + sq1, H + rh, 'plaster'))
    R.cut(poly_prism(diamond(dia), H + rh - 0.05, H + 2 * rh, side='plaster', top='plaster', bottom='plaster'))
    R.cut(box(cx - sq3, cy - sq3, H + 2 * rh - 0.05, cx + sq3, cy + sq3, H + 3 * rh, 'plaster'))
    R.light(box(cx - sq3 + 0.15, cy - sq3 + 0.15, H + 3 * rh - 0.04, cx + sq3 - 0.15, cy + sq3 - 0.15, H + 3 * rh - 0.01, 'e_sky'))
    for (x, y) in ((cx, cy - 4.2), (cx, cy + 4.2), (cx - 4.2, cy), (cx + 4.2, cy)):
        hang_lamp(R, x, y, H - 0.6 + 2 * rh, H + 2 * rh, r=0.16)
    # books round the walls, and night lights on the dais corners
    wall_shelves(R, rows=11, frame='walnut')
    for (x, y) in ((cx - sq3 + 0.15, cy - sq3 + 0.15), (cx + sq3 - 0.15, cy - sq3 + 0.15), (cx + sq3 - 0.15, cy + sq3 - 0.15), (cx - sq3 + 0.15, cy + sq3 - 0.15)):
        candle(R, x, y, top, h=0.2, r=0.04)
    # walkers
    ring_ = std_nav(R, 1.5)
    t1 = navloop(R, ((3.2, 3.2), (C - 3.2, 3.2), (C - 3.2, C - 3.2), (3.2, C - 3.2)), z=rh)
    t2 = navloop(R, ((cx, cy - 4.3), (cx + 4.3, cy), (cx, cy + 4.3), (cx - 4.3, cy)), z=2 * rh)
    R.link(ring_[0], t1[0]); R.link(ring_[4], t1[2])
    R.link(t1[0], R.navpt(5.9, 5.9, rh), t2[0])
    R.spot('probe', 3.0, 8.0, 2.0)
    R.meta.update(label='The Terraces', weight=6,
                  blurb='The floor climbs in terraces to a table at the top, and every step is a shelf of books. The ceiling climbs the same way, as if the room had been folded in half.')
    R.meta['box'] = [[T, 0, T], [C - T, H + 3 * rh, C - T]]
    return R
