"""The Apse: a short vaulted nave with pews, side aisles behind arcades, and at the end a half-dome over a
single lectern among candles. Coloured light falls from three slots in the dome. Books line the apse."""
from lib import *
from kit_c import *


def make():
    R = Room('apse', 1, 1, res=1024)
    R.sockets(floor='terrazzo', wall='tile')
    nx0, nx1 = 4.0, C - 4.0                  # the nave
    js = 3.5
    ay = 11.65                               # centre of the apse
    ra = (nx1 - nx0) / 2
    pr = arch_profile(8, nx1 - nx0, 0, js, 32)
    R.cut(prism(pr, 'y', T - 0.02, ay + 0.01, arch_mats(len(pr), 'terrazzo', 'tile')))
    # the apse: a polygonal half-drum and a half-dome
    na = 8
    R.cut(cyl(8, ay, 0, js + 0.01, ra / math.cos(math.pi / (2 * na)), na, side='tile', top='tile', bottom='terrazzo', a0=0, a1=math.pi))
    R.cut(sphere(8, ay, js, ra, 32, 10, 'plaster', lower=False))
    # side aisles, lower, behind arcades
    for (x0, x1) in ((T - 0.02, nx0 - 0.4), (nx1 + 0.4, C - T + 0.02)):
        apr = arch_profile((x0 + x1) / 2, x1 - x0, 0, 2.9, 20)
        R.cut(prism(apr, 'y', T - 0.02, 12.2, arch_mats(len(apr), 'terrazzo', 'tile')))
    for yc in (3.3, 6.75, 10.2):
        a = arch_profile(yc, 2.3, 0, 2.3, 16)
        R.cut(prism(a, 'x', nx0 - 0.45, nx0 + 0.05, arch_mats(len(a), 'terrazzo', 'tile')))
        R.cut(prism(a, 'x', nx1 - 0.05, nx1 + 0.45, arch_mats(len(a), 'terrazzo', 'tile')))
    # three slots of coloured glass in the half-dome
    for (ang, m) in ((math.pi * 0.28, 'e_blue'), (math.pi * 0.5, 'e_red'), (math.pi * 0.72, 'e_blue')):
        g = box(-0.22, 3.0, 4.3, 0.22, 4.18, 5.7, 'tile').xform(ang - math.pi / 2, 8, ay)
        R.cut(g)
        R.light(box(-0.22, 4.1, 4.3, 0.22, 4.14, 5.7, m).xform(ang - math.pi / 2, 8, ay))
    # a skylight at the top of the nave vault, over the pews
    R.cut(box(7.4, 2.5, js + ra - 0.4, 8.6, 10.0, R.hi + 0.5, 'plaster'))
    R.light(box(7.4, 2.5, R.hi - 0.08, 8.6, 10.0, R.hi - 0.05, 'e_sky'))
    # a low dais in the apse
    R.parts.add(cyl(8, ay, 0, 0.18, ra - 0.4, 24, side='tile', top='terrazzo', bottom='tile', a0=0, a1=math.pi))
    R.parts.add(box(nx0 + 0.4, ay - 0.6, 0, nx1 - 0.4, ay, 0.18, 'tile', top='terrazzo'))
    # books round the apse (not in front of the doorway)
    fd = ra                                  # the flat faces sit at the apse radius
    L = 2 * fd * math.tan(math.pi / (2 * na)) - 0.04
    for k in range(na):
        if k in (3, 4): continue
        a = (k + 0.5) * math.pi / na
        bx, by = 8 + fd * math.cos(a), ay + fd * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        R.shelf(bx - tx * L / 2, by - ty * L / 2, 0, L, a + math.pi, rows=7, frame='walnut')
    # the lectern, facing the pews, among candles
    lectern(R, 8, ay - 0.3, -math.pi / 2, z=0.18)
    for (x, y) in ((6.6, ay - 0.1), (9.4, ay - 0.1), (6.2, ay + 1.3), (9.8, ay + 1.3)):
        candle_stand(R, x, y, 0.18, h=1.2)
    for k in range(9):
        a = math.pi * (0.12 + 0.76 * k / 8)
        candle(R, 8 + 2.9 * math.cos(a), ay + 2.9 * math.sin(a), 0.18, h=0.18 + 0.1 * (k % 3), r=0.04)
    # pews
    for y in (3.0, 4.2, 5.4, 6.6, 7.8, 9.0):
        for (x0, x1) in ((nx0 + 0.45, 7.25), (8.75, nx1 - 0.45)):
            R.parts.add(box(x0, y, 0.42, x1, y + 0.42, 0.48, 'walnut'))
            R.parts.add(box(x0, y - 0.06, 0.0, x1, y, 0.95, 'walnut'))
            for x in (x0, x1 - 0.06):
                R.parts.add(box(x, y - 0.06, 0, x + 0.06, y + 0.42, 0.62, 'walnut', skip=('-z',)))
            R.spot('sit', (x0 + x1) / 2, y + 0.22, 0.47, math.pi / 2)
    # the aisles: tall cases on the outer walls, lamps
    for (x, d) in ((T, '+x'), (C - T, '-x')):
        for (p, q) in ((0.6, 6.2), (9.8, 11.9)):
            if d == '+x': R.shelf(x, q, 0, q - p, d, rows=6, frame='walnut')
            else: R.shelf(x, p, 0, q - p, d, rows=6, frame='walnut')
        for y in (3.3, 10.2):
            hang_lamp(R, 1.95 if d == '+x' else C - 1.95, y, 3.0, 4.5, r=0.13, m='e_dim')
    for y in (3.6, 7.2):
        pendant(R, 8, y, 4.3, js + ra, r=0.4)
    # walkers: up the middle, round through the aisles
    mid = [R.navpt(8, 1.4), R.navpt(8, 9.9), R.navpt(6.4, ay - 0.9), R.navpt(9.6, ay - 0.9)]
    R.link(mid[0], mid[1], mid[2]); R.link(mid[1], mid[3])
    w = [R.navpt(1.95, 1.4), R.navpt(1.95, 11.2), R.navpt(C - 1.95, 1.4), R.navpt(C - 1.95, 11.2)]
    R.link(mid[0], w[0], w[1]); R.link(mid[0], w[2], w[3])
    R.link(w[1], R.navpt(1.95, 10.2), R.navpt(4.6, 10.2))
    R.spot('probe', 8, 10.0, 1.8)
    R.meta.update(label='The Apse', weight=5,
                  blurb='Pews, and at the end of them a lectern under a half-dome, with the candles lit. Whatever is going to be read out, you have arrived in time for it.')
    R.meta['box'] = [[T, 0, T], [C - T, js + ra, C - T]]
    return R
