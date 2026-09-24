"""The Void Hall: a hall 128 m square and 31 m high, almost entirely dark. Iron lamp posts stand far
apart on the marble; bookcases line the distant walls. In the middle one lit staircase winds round a
stone pier up into the dark, to a railed platform with a lectern, one book, and one hanging lamp."""
from lib import *
from kit_g import *


def make():
    R = Room('voidhall', 8, 8, levels=4, res=2048)
    W, D = R.W, R.D
    seal(R, upper_sockets(R), floor='terrazzo', wall='tile')
    ceil = R.hi - 0.4
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, ceil, 'tile', bottom='terrazzo', top='plaster'))

    # --- the staircase: six flights round a square pier, up to a platform at 24 m -----------------
    cx = cy = W / 2
    n, rise, run, fw = 20, 0.2, 0.3, 2.4
    L, H = n * run, n * rise
    s = L / 2                                   # pier half-size
    o = s + fw                                  # outer half-size
    top = 6 * H
    R.parts.add(box(cx - s, cy - s, 0, cx + s, cy + s, top - 0.5, 'tile'))
    # flights: (foot x, foot y, axis, outer side)
    legs = [(cx - s, cy - o, '+x', 0), (cx + s, cy - s, '+y', 1), (cx + s, cy + s, '-x', 1), (cx - o, cy + s, '-y', 0)]
    corners = {'+x': (1, -1), '+y': (1, 1), '-x': (-1, 1), '-y': (-1, -1)}      # the landing each flight arrives at
    for k in range(6):
        x0, y0, ax, side = legs[k % 4]
        z0 = k * H
        flight(R, x0, y0, z0, fw, n, rise, run, ax, m='terrazzo', riser='tile', side='tile')
        flight_rail(R, x0, y0, z0, fw, n, rise, run, ax, which=(side,))
        if k == 5: break
        # the landing at its top, railed on its two outer edges, a lamp on its corner
        sx, sy = corners[ax]; z = z0 + H
        lx0, lx1 = (cx + s, cx + o) if sx > 0 else (cx - o, cx - s)
        ly0, ly1 = (cy + s, cy + o) if sy > 0 else (cy - o, cy - s)
        R.parts.add(box(lx0, ly0, z - 0.45, lx1, ly1, z, 'tile', top='terrazzo', bottom='plaster'))
        ex, ey = cx + sx * (o - 0.07), cy + sy * (o - 0.07)
        rail(R, lx0, ey, lx1, ey, z); rail(R, ex, ly0, ex, ly1, z)
        R.parts.add(box(ex - 0.12, ey - 0.12, z + 1.06, ex + 0.12, ey + 0.12, z + 1.12, 'brass'))
        R.light(cyl(ex, ey, z + 1.12, z + 1.42, 0.1, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # the platform on top of the pier (open over the last flight, on the east)
    R.parts.add(box(cx - o, cy - o, top - 0.5, cx + s, cy + o, top, 'tile', top='floor', bottom='plaster'))
    R.parts.add(box(cx + s, cy + s, top - 0.5, cx + o, cy + o, top, 'tile', top='floor', bottom='plaster'))
    e = 0.07
    rail(R, cx - o + e, cy - o, cx - o + e, cy + o, top)
    rail(R, cx - o, cy - o + e, cx + s, cy - o + e, top)
    rail(R, cx - o, cy + o - e, cx + o, cy + o - e, top)
    rail(R, cx + s - e, cy - o, cx + s - e, cy + s, top)
    rail(R, cx + o - e, cy + s, cx + o - e, cy + o, top)
    # a lectern and one book, under one lamp
    lx, ly = cx - 1.0, cy
    R.parts.add(box(lx - 0.25, ly - 0.25, top, lx + 0.25, ly + 0.25, top + 0.1, 'walnut'))
    R.parts.add(box(lx - 0.09, ly - 0.09, top + 0.1, lx + 0.09, ly + 0.09, top + 1.0, 'walnut'))
    R.parts.add(sloped('x', lx - 0.3, lx + 0.3, ly - 0.35, ly + 0.35, top + 0.95, top + 0.95, top + 1.25, top + 1.0, 'walnut'))
    R.parts.add(sloped('x', lx - 0.2, lx + 0.2, ly - 0.25, ly + 0.25, top + 1.205, top + 1.04, top + 1.26, top + 1.095, 'leather', cap='ivory'))
    R.spot('read', lx + 0.55, ly, top, math.pi)
    hanging(R, lx + 0.1, ly, ceil, top + 2.6, r=0.28, e='e_lamp')
    R.light(cyl(lx + 0.1, ly, ceil - 0.02, ceil, 0.6, 12, side='e_candle', top='e_candle', bottom='e_candle'))

    # --- the floor: far-apart iron lamp posts --------------------------------------------------------
    for i in range(1, 7):
        for j in range(1, 7):
            if (i + j) % 2: continue
            lamppost(R, i * C + C / 2, j * C + C / 2, h=3.6, e='e_dim', r=0.18)
    # a night lamp at the foot of the stair
    lamppost(R, cx - o - 1.2, cy - o - 1.2, h=2.4, e='e_amber', r=0.14)

    # --- bookcases round the walls, and a few lamps over them ------------------------------------
    wall_cases(R, rows=14, frame='walnut')
    for k in range(R.w):
        x = k * C + C / 2
        for (px, py) in ((x - 4.5, T + 1.2), (x + 4.5, D - T - 1.2)):
            R.light(box(px - 0.5, py - 0.08, 6.4, px + 0.5, py + 0.08, 6.5, 'e_dim'))
    for k in range(R.d):
        y = k * C + C / 2
        for (px, py) in ((T + 1.2, y + 4.5), (W - T - 1.2, y - 4.5)):
            R.light(box(px - 0.08, py - 0.5, 6.4, px + 0.08, py + 0.5, 6.5, 'e_dim'))

    # --- walkers ---------------------------------------------------------------------------------
    r = o + 3.0
    ring_ = [R.navpt(cx + a * r, cy + b * r) for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    R.link(*ring_, ring_[0])
    big = [R.navpt(x, y) for (x, y) in ((16, 16), (64, 16), (112, 16), (112, 64), (112, 112), (64, 112), (16, 112), (16, 64))]
    R.link(*big, big[0])
    R.link(big[0], ring_[0]); R.link(big[4], ring_[2])
    R.spot('probe', cx - 14, cy - 14, 3.0)
    R.meta.update(label='The Void Hall', weight=3,
                  blurb='The far walls are only a rumour of lamplight. In the middle a staircase climbs into the dark to one lit book, which is almost certainly not yours.')
    R.meta['box'] = [[T, 0, T], [W - T, ceil, D - T]]
    return R
