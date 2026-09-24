"""The Ladder Hall: bookcases seven metres tall on both long walls. An iron catwalk runs along the
north wall at 3.6 m, reached by a stair at each end; rolling ladders stand along the shelves."""
from lib import *
from kit_e import *


def ladder(R, x, y, z0, z1, s, lean=0.9):
    """A rolling ladder against a bookcase wall: foot at (x, y + s*lean, z0), top at (x, y, z1)."""
    g = Geo()
    for dx in (-0.24, 0.24):
        g.add(beam((x + dx, y + s * lean, z0), (x + dx, y, z1), 0.05, 0.06, 'oak'))
    n = int((z1 - z0) / 0.3)
    for k in range(1, n):
        t = k / n
        yy, zz = y + s * lean * (1 - t), z0 + (z1 - z0) * t
        g.add(box(x - 0.24, yy - 0.02, zz, x + 0.24, yy + 0.02, zz + 0.035, 'oak'))
    # wheels at the foot, a hook on the rail at the top
    g.add(cyl(x - 0.24, y + s * lean, z0, z0 + 0.07, 0.05, 8, side='brass', top='brass', bottom='brass'))
    g.add(cyl(x + 0.24, y + s * lean, z0, z0 + 0.07, 0.05, 8, side='brass', top='brass', bottom='brass'))
    R.nocol.add(g)


def make():
    R = Room('ladderhall', 2, 1, res=1024)
    R.sockets()
    W, D = R.W, R.D
    cy = D / 2
    H = 7.5
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='floor', top='plaster'))
    # coffered ceiling with lay-lights
    for k in range(7):
        x = 4.0 + 4.0 * k
        R.cut(box(x - 1.6, cy - 3.6, H - 0.05, x + 1.6, cy + 3.6, H + 0.09, 'plaster'))
        R.light(box(x - 1.3, cy - 3.0, H + 0.04, x + 1.3, cy + 3.0, H + 0.07, 'e_sky'))
    # the great bookcases: 16 rows, floor to near ceiling, on both long walls
    rows = 16
    for (a, b) in LONG_SEGS:
        R.shelf(a, T, 0, b - a, '+y', rows=rows, frame='walnut')
        R.shelf(b, D - T, 0, b - a, '-y', rows=rows, frame='walnut')
    # over the doorways, the cases carry on above the arches
    for x in (8.0, 24.0):
        R.shelf(x - 1.9, T, 4.4, 3.8, '+y', rows=6, frame='walnut', sides=False)
        R.shelf(x + 1.9, D - T, 4.4, 3.8, '-y', rows=6, frame='walnut', sides=False)
    # end walls: tall cases beside the doorways
    for (a, b) in ((T + 0.1, 6.2), (9.8, D - T - 0.1)):
        R.shelf(T, b, 0, b - a, '+x', rows=rows, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=rows, frame='walnut')
    # the catwalk along the north wall, 3.6 m up
    cz, cw = 3.6, 1.3
    yf = D - T - 0.36                           # front of the north bookcases
    y0 = yf - cw
    R.parts.add(box(T, y0, cz - 0.12, W - T, yf, cz, 'iron', top='oak'))
    for x in [1.2 + 2.4 * k for k in range(13)]:           # brackets under it
        R.parts.add(beam((x, yf, cz - 0.9), (x, y0 + 0.1, cz - 0.14), 0.05, 0.06, 'iron'))
    # stairs at both ends, rising along the front of the catwalk, with landings
    n, rs, rn = 18, cz / 18, 0.28
    L = n * rn
    sw = 1.15
    ys = y0 - sw
    xs0, xs1 = 1.4, W - 1.4                     # feet of the two flights
    R.flight(xs0, ys, 0, sw, n, rs, rn, '+x', m='oak', side='walnut')
    R.flight(xs1, ys, 0, sw, n, rs, rn, '-x', m='oak', side='walnut')
    R.col.add(slope_box(xs0 + 0.3, xs0 + L, ys, ys + sw, 0, 0, 0.02, cz - 0.3, 'tile'))     # nothing gets under the flights
    R.col.add(slope_box(xs1 - L, xs1 - 0.3, ys, ys + sw, 0, 0, cz - 0.3, 0.02, 'tile'))
    lw = 1.2
    for (la, lb) in ((xs0 + L, xs0 + L + lw), (xs1 - L - lw, xs1 - L)):
        R.parts.add(box(la, ys, cz - 0.12, lb, y0 + 0.01, cz, 'iron', top='oak'))
        R.parts.add(cyl((la + lb) / 2, ys + 0.1, 0, cz - 0.12, 0.05, 8, side='iron', caps=False))
    # rails: the flights' open sides, the landings, the catwalk's edge
    rail(R, [(xs0, ys + 0.03, 0), (xs0 + L, ys + 0.03, cz), (xs0 + L + lw - 0.03, ys + 0.03, cz), (xs0 + L + lw - 0.03, y0 + 0.03, cz)])
    rail(R, [(xs1, ys + 0.03, 0), (xs1 - L, ys + 0.03, cz), (xs1 - L - lw + 0.03, ys + 0.03, cz), (xs1 - L - lw + 0.03, y0 + 0.03, cz)])
    rail(R, [(T + 0.02, y0 + 0.03, cz), (xs0 + L, y0 + 0.03, cz)])
    rail(R, [(xs1 - L, y0 + 0.03, cz), (W - T - 0.02, y0 + 0.03, cz)])
    rail(R, [(xs0 + L + lw - 0.03, y0 + 0.03, cz), (xs1 - L - lw + 0.03, y0 + 0.03, cz)])
    # a rail on the flights' other side too, where they rise beside the space under the catwalk
    rail(R, [(xs0 + 1.2, y0 - 0.03, 1.2 * rs / rn), (xs0 + L, y0 - 0.03, cz)], h=0.9)
    rail(R, [(xs1 - 1.2, y0 - 0.03, 1.2 * rs / rn), (xs1 - L, y0 - 0.03, cz)], h=0.9)
    # rolling ladders: on a brass rail along the south cases, and along the upper north cases
    for (y, z) in ((T + 0.4, 6.6), (D - T - 0.4, 6.6)):
        R.parts.add(box(T + 0.3, y - 0.02, z, W - T - 0.3, y + 0.02, z + 0.04, 'brass'))
    for x in (3.5, 13.0, 19.5, 29.0):
        ladder(R, x, T + 0.42, 0, 6.6, 1, 1.0)
    for x in (4.2, 11.5, 16.0, 21.0, 27.5):
        ladder(R, x, D - T - 0.42, cz, 6.6, -1, 0.55)
    # reading tables down the south half, lamps over them
    for (xa, xb) in ((10.6, 14.6), (17.4, 21.4)):
        table(R, xa, 4.6, xb, 5.6, m='walnut', top='leather')
        for k in range(3):
            x = xa + 0.7 + k * (xb - xa - 1.4) / 2
            chair(R, x, 4.1, math.pi / 2)
            chair(R, x, 6.1, -math.pi / 2)
            table_lamp(R, x, 5.1, 0.76)
    for x in (4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0):
        pendant(R, x, cy - 1.8, 4.6, H, r=0.28)
    # lamps under the catwalk, lighting the lower shelves
    for x in (4.0, 12.0, 16.0, 20.0, 28.0):
        R.light(cyl(x, (y0 + yf) / 2, cz - 0.16, cz - 0.12, 0.22, 16, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # night lamps on the catwalk rail
    for x in (3.0, 9.0, 16.0, 23.0, 29.0):
        R.light(sphere(x, y0 + 0.03, cz + 1.08, 0.07, 8, 4, 'e_amber'))
    # walkers: the floor loop, the stairs and the catwalk
    fl = loop(R, [(1.6, 1.6), (8.0, 1.6), (16.0, 2.2), (24.0, 1.6), (W - 1.6, 1.6), (W - 1.6, cy), (W - 3.0, ys - 0.7), (24.0, ys - 0.7), (16.0, ys - 0.7),
                  (8.0, ys - 0.7), (3.0, ys - 0.7), (1.6, cy)])
    c0 = R.navpt(xs0 - 0.5, ys + sw / 2); c1 = R.navpt(xs1 + 0.5, ys + sw / 2)
    t0 = R.navpt(xs0 + L + lw / 2, ys + 0.6, cz); t1 = R.navpt(xs1 - L - lw / 2, ys + 0.6, cz)
    k0 = R.navpt(xs0 + L + lw / 2, y0 + cw / 2, cz); k1 = R.navpt(xs1 - L - lw / 2, y0 + cw / 2, cz)
    mid = R.navpt(16.0, y0 + cw / 2, cz)
    R.link(fl[11], c0, t0, k0, mid, k1, t1, c1, fl[5])
    R.spot('probe', 16.0, cy, 2.2)
    R.meta.update(label='The Ladder Hall', weight=8,
                  blurb='The shelves go up seven metres and the ladders go most of the way. Somebody has left a book on the top rung of every one.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    return R
