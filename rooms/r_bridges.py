"""The Bridges: a room two storeys deep, crossed at the upper doorways' height by four railed
walkways that meet in a square. From the middle of one a grand stair divides and comes down to a
floor of bookcases eight metres below."""
from lib import *
from kit_f import *


def make():
    R = Room('bridges', 2, 2, levels=2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, R.hi - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    Z = LH
    bw = 1.2                                # half width of a bridge
    lines = (8.0, 24.0)
    # the bridges: two north-south, two east-west
    for c in lines:
        deck(R, c - bw, T, c + bw, W - T, Z, th=0.4, top='floor', m='tile')
    for c in lines:   # east-west pieces between the north-south bridges (so the junctions are not doubled)
        for (a, b) in ((T, lines[0] - bw), (lines[0] + bw, lines[1] - bw), (lines[1] + bw, W - T)):
            deck(R, a, c - bw, b, c + bw, Z, th=0.4, top='floor', m='tile')
    # stair opening in the south east-west bridge's north rail
    st0, st1 = 15.0, 17.0
    # rails
    gaps = [(l - bw, l + bw) for l in lines]
    for c in lines:
        for s in (-1, 1):
            x = c + s * (bw - 0.07)
            for (a, b) in _pieces(T, W - T, gaps):
                rail_line(R, x, a, Z, x, b, Z, h=1.0, m='brass', post='iron')
            y = c + s * (bw - 0.07)
            op = gaps + ([(st0, st1)] if (c == lines[0] and s == 1) else [])
            for (a, b) in _pieces(T, W - T, op):
                rail_line(R, a, y, Z, b, y, Z, h=1.0, m='brass', post='iron')
    # the grand stair: one flight down from the south bridge to a landing, two flights back down to the floor
    yb = lines[0] + bw
    n = 20
    zl = 4.0
    L = n * 0.3
    flight_thin(R, st0, yb + L, zl, st1 - st0, n, (Z - zl) / n, 0.3, '-y', m='terrazzo', side='tile', fill=0)
    for xr in (st0 + 0.06, st1 - 0.06):
        rail_line(R, xr, yb + L, zl + 0.2, xr, yb, Z, h=1.0, post='iron')
    ly0, ly1 = yb + L, yb + L + 2.4
    lx0, lx1 = 11.2, 20.8
    deck(R, lx0, ly0, lx1, ly1, zl, th=0.35, top='terrazzo')
    rect_rails(R, lx0, ly0, lx1, ly1, zl, opens={'S': [(lx0, 13.2), (st0, st1), (18.8, lx1)]}, post='iron')
    for (x0, x1) in ((lx0, 13.2), (18.8, lx1)):
        flight_thin(R, x0, yb, 0.0, x1 - x0, n, zl / n, 0.3, '+y', m='terrazzo', side='tile')
        for xr in (x0 + 0.06, x1 - 0.06):
            rail_line(R, xr, yb, 0.2, xr, yb + L, zl, h=1.0, post='iron')
    for x in (lx0 + 0.25, lx1 - 0.25):
        pier(R, x, ly1 - 0.25, 0, zl - 0.35, 0.2)
    # bookcases on the floor far below, on a grid with aisles on the doorway lines
    for x in (4.0, 12.0, 20.0, 28.0):
        for (y0, y1) in ((2.9, 6.3), (9.9, 14.3), (17.9, 22.1), (25.7, 29.1)):
            if x in (12.0, 20.0) and y0 == 9.9: continue
            stack2_ax(R, x, y0, x, y1, 0, 7, frame='walnut', crown='walnut', ends='walnut')
    # giant cases on the walls, far taller than anyone could reach
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), z=0, rows=14, frame='walnut')
    # light: lamps under the bridges, a chandelier over the landing, skylights in the four bays
    for c in lines:
        for p in (4.0, 16.0, 28.0):
            lamp(R, c, p, Z - 1.0, 0.24, chain=Z - 0.4)
            lamp(R, p, c, Z - 1.0, 0.24, chain=Z - 0.4)
    chandelier(R, 16, 16, 10.8, 2.6, n=16, chain=R.hi - 0.1, bulb=0.15, tiers=2)
    for (x, y) in ((3.5, 3.5), (16, 3.5), (28.5, 3.5), (3.5, 16), (28.5, 16), (3.5, 28.5), (16, 28.5), (28.5, 28.5)):
        R.light(box(x - 1.6, y - 1.6, R.hi - 0.16, x + 1.6, y + 1.6, R.hi - 0.14, 'e_sky'))
    for (x, y) in ((4.0, 2.5), (28.0, 29.5), (12.0, 29.5), (20.0, 2.5)):
        R.light(sphere(x, y, 0.4, 0.14, 8, 4, 'e_amber'))
        R.parts.add(cyl(x, y, 0, 0.26, 0.2, 10, side='tile', top='tile'))
    # walkers: the floor, and the square of bridges
    loop(R, ((8, 2.0), (16, 2.0), (24, 2.0), (24, 8), (30, 8), (30, 24), (24, 24), (24, 30), (8, 30), (8, 24), (2, 24), (2, 8), (8, 8)))
    loop(R, ((8, 8), (24, 8), (24, 24), (8, 24)), z=Z)
    R.spot('probe', 16, 20, 6.0)
    R.meta.update(label='The Bridges', weight=6,
                  blurb='Four bridges cross a room eight metres deep, and the floor down there is bookcases as far as the walls. The stair looks like it was an afterthought. It probably was.')
    R.meta['box'] = [[T, 0, T], [W - T, R.hi - 0.1, W - T]]
    return R


def _pieces(a, b, gaps):
    out = [(a, b)]
    for (g0, g1) in gaps:
        nxt = []
        for (s0, s1) in out:
            if g1 <= s0 or g0 >= s1: nxt.append((s0, s1)); continue
            if g0 > s0: nxt.append((s0, g0))
            if g1 < s1: nxt.append((g1, s1))
        out = nxt
    return [p for p in out if p[1] - p[0] > 0.05]
