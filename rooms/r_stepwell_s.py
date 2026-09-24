"""The Stepwell: a square well that steps down in three great terraces, each too tall to step, climbed by
little flights of stairs that meet in pairs and zigzag down the sides. Books wait on the landings."""
from lib import *
from kit_c import *


def make():
    R = Room('stepwell_s', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    shell(R, TOP, floor='floor', ceil='plaster')
    e0, st, n = 2.5, 1.3, 3
    dz = 1.9 / n
    for k in range(n):
        a = e0 + k * st
        R.cut(box(a, a, -(k + 1) * dz, C - a, C - a, 0.3, 'tile', bottom='tile' if k < n - 1 else 'mosaic', top='tile'))
    fw, run = 0.6, 0.3
    ns = 3
    rise = dz / ns
    fl = ns * run

    def side_flight(side, e, u0, z0, sgn):
        """A flight against the riser at e on `side`, its foot at u0, climbing along +u (sgn>0) or -u."""
        if side == 'S': R.flight(u0, e, z0, fw, ns, rise, run, '+x' if sgn > 0 else '-x', m='tile', side='tile')
        if side == 'N': R.flight(u0, C - e - fw, z0, fw, ns, rise, run, '+x' if sgn > 0 else '-x', m='tile', side='tile')
        if side == 'W': R.flight(e, u0, z0, fw, ns, rise, run, '+y' if sgn > 0 else '-y', m='tile', side='tile')
        if side == 'E': R.flight(C - e - fw, u0, z0, fw, ns, rise, run, '+y' if sgn > 0 else '-y', m='tile', side='tile')

    def side_box(side, e, u0, u1, z0, z1, m='tile'):
        if side == 'S': R.parts.add(box(u0, e, z0, u1, e + fw, z1, m, skip=('-z',)))
        if side == 'N': R.parts.add(box(u0, C - e - fw, z0, u1, C - e, z1, m, skip=('-z',)))
        if side == 'W': R.parts.add(box(e, u0, z0, e + fw, u1, z1, m, skip=('-z',)))
        if side == 'E': R.parts.add(box(C - e - fw, u0, z0, C - e, u1, z1, m, skip=('-z',)))

    def side_books(side, e, u0, u1, z0, h):
        L = u1 - u0
        if side == 'S': book_riser(R, u0, e, L, z0, h, '+y')
        if side == 'N': book_riser(R, u1, C - e, L, z0, h, '-y')
        if side == 'W': book_riser(R, e, u1, L, z0, h, '+x')
        if side == 'E': book_riser(R, C - e, u0, L, z0, h, '-x')

    # (riser index, pair centres along the side, measured from the middle)
    plan = {0: (-3.3, 0.0, 3.3), 1: (-2.0, 2.0), 2: (0.0,)}
    for j in range(n):
        e = e0 + j * st
        zt, zb = -j * dz, -(j + 1) * dz
        half = C / 2 - e
        for side in 'SNWE':
            pairs = plan[j] if side in 'SN' else tuple(-p for p in plan[j])
            occupied = []
            for p in pairs:
                um = C / 2 + p
                side_flight(side, e, um - fw / 2 - fl, zb, 1)
                side_box(side, e, um - fw / 2, um + fw / 2, zb, zt)
                side_flight(side, e, um + fw / 2 + fl, zb, -1)
                occupied.append((um - fw / 2 - fl - 0.1, um + fw / 2 + fl + 0.1))
            # books along the rest of the riser
            lo, hi = C / 2 - half + 0.75, C / 2 + half - 0.75
            cuts = [lo] + [v for o in sorted(occupied) for v in o] + [hi]
            for a, b in zip(cuts[::2], cuts[1::2]):
                if b - a > 0.6: side_books(side, e, a, b, zb, dz - 0.02)
    # the bottom: a table with lamps, four chairs, a skylight far above
    zb = -1.9
    table_at(R, 7.0, 7.4, 9.0, 8.6, zb, top='leather')
    desk_lamp(R, 7.4, 8.0, zb + 0.76); desk_lamp(R, 8.6, 8.0, zb + 0.76)
    open_book(R, 8.0, 7.8, zb + 0.76, 0.1)
    for (x, y, f) in ((7.5, 6.85, math.pi / 2), (8.5, 6.85, math.pi / 2), (7.5, 9.15, -math.pi / 2), (8.5, 9.15, -math.pi / 2)):
        chair(R, x, y, f, z=zb)
    for (x, y) in ((5.4, 5.4), (C - 5.4, 5.4), (C - 5.4, C - 5.4), (5.4, C - 5.4)):
        R.parts.add(box(x - 0.34, y - 0.34, zb, x + 0.34, y + 0.34, zb + 0.5, 'tile', skip=('-z',)))
        R.light(box(x - 0.2, y - 0.2, zb + 0.5, x + 0.2, y + 0.2, zb + 0.56, 'e_pool'))
    R.cut(box(4.6, 4.6, TOP - 0.2, C - 4.6, C - 4.6, R.hi + 0.5, 'plaster'))
    R.light(box(4.6, 4.6, R.hi - 0.08, C - 4.6, C - 4.6, R.hi - 0.05, 'e_sky'))
    # the room round the well
    wall_shelves(R, rows=9, frame='walnut')
    for (x, y) in ((1.5, 1.5), (C - 1.5, 1.5), (C - 1.5, C - 1.5), (1.5, C - 1.5)):
        hang_lamp(R, x, y, 3.8, TOP, r=0.15)
    # walkers: round the rim, down one flight pair to the first terrace, and round the bottom
    rim = std_nav(R, 1.5)
    t0 = navloop(R, ((3.45, 3.45), (C - 3.45, 3.45), (C - 3.45, C - 3.45), (3.45, C - 3.45)), z=-dz)
    bot = navloop(R, ((5.8, 5.8), (C - 5.8, 5.8), (C - 5.8, C - 5.8), (5.8, C - 5.8)), z=-1.9)
    R.spot('probe', 8, 5.8, 0.0)
    R.meta.update(label='The Stepwell', weight=5,
                  blurb='A well with no water, only stairs: little flights that meet and part and meet again all the way down. At the bottom somebody has set out a table.')
    R.meta['box'] = [[T, -1.9, T], [C - T, TOP, C - T]]
    return R
