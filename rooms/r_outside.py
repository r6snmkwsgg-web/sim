"""The Outside: a plaza 64 m square under a painted sky, paved in slate. Stone walls stand about on
their own with doorways that lead to more plaza; iron lamps burn in daylight; dead trees of iron rods,
benches round a dry fountain, and a few bookcases out in the open, as if someone were moving house.
The facades round the edge have windows, all dark but one."""
from lib import *
from kit_g import *


def free_wall(R, cx, cy, ang, L=8.0, Hh=4.6, t=0.5, closed=False):
    g = Geo()
    hw, dh = 0.8, 2.6
    g.add(box(-L / 2, -t / 2, 0, -hw, t / 2, Hh, 'tile'))
    g.add(box(hw, -t / 2, 0, L / 2, t / 2, Hh, 'tile'))
    g.add(box(-hw, -t / 2, dh, hw, t / 2, Hh, 'tile'))
    g.add(box(-L / 2 - 0.1, -t / 2 - 0.1, Hh, L / 2 + 0.1, t / 2 + 0.1, Hh + 0.25, 'tile'))
    if closed:
        g.add(box(-hw, -0.05, 0, hw, 0.05, dh, 'oak'))
        g.add(box(hw - 0.25, -0.1, 1.0, hw - 0.17, 0.1, 1.08, 'brass'))
    R.parts.add(g.xform(ang, cx, cy))
    if closed:
        R.light(box(-0.25, t / 2 + 0.01, dh + 0.25, 0.25, t / 2 + 0.05, dh + 0.45, 'e_exit').xform(ang, cx, cy))


def tree(R, x, y, seed):
    import random
    rnd = random.Random(seed)
    R.parts.add(box(x - 0.9, y - 0.9, 0, x + 0.9, y + 0.9, 0.3, 'slate', skip=('-z',)))
    h = 3.6 + rnd.random() * 1.2
    R.parts.add(cyl(x, y, 0.3, h, 0.11, 6, side='iron', top='iron', caps=True))
    for k in range(5):
        a = k * 2 * math.pi / 5 + rnd.random() * 0.8
        z = h * (0.5 + 0.1 * k)
        Lb = 1.2 + rnd.random() * 1.3
        up = 0.6 + rnd.random() * 0.9
        R.parts.add(sloped('x', 0, Lb, -0.035, 0.035, z, z + up, z + 0.07, z + up + 0.07, 'iron').xform(a, x, y))
        # a twig off the end
        ex, ey, ez = x + math.cos(a) * Lb, y + math.sin(a) * Lb, z + up
        b = a + (0.7 if k % 2 else -0.7)
        R.parts.add(sloped('x', 0, 0.8, -0.025, 0.025, ez, ez + 0.6, ez + 0.05, ez + 0.65, 'iron').xform(b, ex, ey))


def make():
    R = Room('outside', 4, 4, levels=2, res=2048)
    W, D = R.W, R.D
    seal(R, upper_sockets(R), floor='slate', wall='tile')
    sky = R.hi - 0.4
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, sky, 'tile', bottom='slate', top='plaster'))
    R.light(box(T, T, sky - 0.04, W - T, D - T, sky - 0.02, 'e_skydome', skip=('+z',)))
    # the facades: a string course and dark windows, one lit
    for z in (5.2,):
        for (x0, y0, x1, y1) in ((T, T, W - T, T + 0.25), (T, D - T - 0.25, W - T, D - T), (T, T, T + 0.25, D - T), (W - T - 0.25, T, W - T, D - T)):
            R.parts.add(box(x0, y0, z, x1, y1, z + 0.3, 'tile'))
    lit = (('N', 5, 1),)
    for row, zw in enumerate((7.0, 10.8)):
        for k in range(8):
            c = 4.0 + k * 8.0
            for side in 'SNWE':
                m = 'e_amber' if (side, k, row) in lit else 'black'
                if side == 'S':   g = box(c - 0.6, T, zw, c + 0.6, T + 0.04, zw + 2.2, m)
                elif side == 'N': g = box(c - 0.6, D - T - 0.04, zw, c + 0.6, D - T, zw + 2.2, m)
                elif side == 'W': g = box(T, c - 0.6, zw, T + 0.04, c + 0.6, zw + 2.2, m)
                else:             g = box(W - T - 0.04, c - 0.6, zw, W - T, c + 0.6, zw + 2.2, m)
                (R.light if m.startswith('e_') else R.parts.add)(g)
    # the dry fountain
    cx = cy = W / 2
    R.parts.add(ring(cx, cy, 0, 0.6, 4.0, 4.4, 32, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.parts.add(cyl(cx, cy, 0, 0.1, 4.0, 32, side='slate', top='slate', bottom='slate'))
    R.parts.add(cyl(cx, cy, 0.1, 1.6, 0.3, 12, side='tile', top='tile'))
    R.parts.add(cyl(cx, cy, 1.6, 1.8, 1.4, 24, side='tile', top='tile', bottom='tile'))
    R.parts.add(cyl(cx, cy, 1.8, 2.9, 0.12, 8, side='tile', top='tile'))
    R.parts.add(cyl(cx, cy, 2.9, 3.0, 0.6, 16, side='tile', top='tile', bottom='tile'))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        bench(R, cx + math.cos(a) * 7.0, cy + math.sin(a) * 7.0, a - math.pi / 2)
    # freestanding walls with doorways to nowhere
    free_wall(R, 18, 34, math.pi / 2)
    free_wall(R, 44, 44, 0.0)
    free_wall(R, 32, 13, 0.0, closed=True)
    free_wall(R, 50, 22, math.pi / 2, L=6.0, Hh=3.8)
    free_wall(R, 12, 52, 0.3, L=6.0, closed=True)
    # dead iron trees
    for k, (x, y) in enumerate(((14, 14), (50, 12), (22, 48), (52, 52), (40, 30), (9, 26), (30, 55))):
        tree(R, x, y, 17 + k)
    # iron lamp posts, lit at noon
    for (x, y) in ((25, 25), (39, 25), (25, 39), (39, 39), (8, 40), (56, 36), (36, 6), (28, 58), (57, 6), (6, 58)):
        lamppost(R, x, y, h=3.4, e='e_lamp', r=0.15)
    for (x, y) in ((36, 6), (28, 58)):
        R.light(box(x - 0.08, y - 0.08, 0.3, x + 0.08, y + 0.08, 0.34, 'e_candle'))
    # bookcases standing out in the open
    R.shelf(10, 36, 0, 3.0, '+x', rows=6, frame='walnut')
    R.shelf(54, 26, 0, 3.0, '-x', rows=6, frame='walnut')
    R.shelf(42, 50, 0, 3.0, '-y', rows=6, frame='walnut')
    R.shelf(19.0, 20.0, 0, 2.4, math.pi / 2 + 0.35, rows=6, frame='walnut')
    R.shelf(46, 16, 0, 2.0, math.pi, rows=4, frame='oak')
    # walkers
    rg = [R.navpt(cx + math.cos(k * math.pi / 4) * 5.4, cy + math.sin(k * math.pi / 4) * 5.4) for k in range(8)]
    R.link(*rg, rg[0])
    out = [R.navpt(x, y) for (x, y) in ((6, 6), (26, 8), (58, 16), (58, 58), (34, 60), (6, 44))]
    R.link(*out, out[0])
    R.link(out[1], rg[5]); R.link(out[4], rg[2])
    R.spot('probe', 28, 22, 2.0)
    R.meta.update(label='The Outside', weight=3,
                  blurb='Outside. Sky, paving, trees, a fountain. For a moment you almost believe it, and then you notice the lamps are lit at noon and the trees are made of iron.')
    R.meta['box'] = [[T, 0, T], [W - T, sky, D - T]]
    return R
