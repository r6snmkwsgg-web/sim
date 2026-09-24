"""The Amphitheatre: a round bowl of oak terraces steps down to a stage with a single lectern, under
a drum-shaped ceiling with an oculus. A ring of bookcases stands along the rim; a ring of lamps
hangs over the seats. Nobody is speaking, and everybody is listening."""
from lib import *
from kit_f import *


def make():
    R = Room('amphitheatre', 2, 2, res=2048)
    R.sockets(floor='floor', wall='tile')
    W = R.W
    cx = cy = W / 2
    Hc = 6.0
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, Hc, 'tile', bottom='floor', top='plaster'))
    # the drum over the bowl, an oculus in it
    R.cut(cyl(cx, cy, Hc - 0.02, TOP - 0.45, 14.2, 64, side='tile', top='plaster', bottom='plaster'))
    R.cut(cyl(cx, cy, TOP - 0.47, TOP - 0.1, 2.6, 40, side='tile', top='plaster', bottom='plaster'))
    R.light(cyl(cx, cy, TOP - 0.14, TOP - 0.12, 2.6, 40, side='e_sky', top='e_sky', bottom='e_sky'))
    R.parts.add(ring(cx, cy, Hc - 0.25, Hc, 14.2, 14.6, 64, top='tile', bottom='tile', inner='tile', outer='tile'))
    # the terraces
    radii = [12.8, 11.4, 10.0, 8.6, 7.2]
    step = 0.38
    for k, r in enumerate(radii):
        R.cut(cyl(cx, cy, -step * (k + 1), 0.05, r, 72, side='tile', top='tile', bottom='terrazzo' if k == 4 else 'floor'))
    # step lights in the risers, on four radial lines
    for k, r in enumerate(radii):
        for q in range(8):
            a = q * math.pi / 4 + math.pi / 8
            z = -step * (k + 1)
            g = box(-0.2, -0.03, z + 0.1, 0.2, 0.0, z + 0.2, 'e_pool').xform(a - math.pi / 2, cx + math.cos(a) * r, cy + math.sin(a) * r)
            R.light(g)
    # the stage and the lectern
    zb = -step * 5
    R.parts.add(cyl(cx, cy, zb, zb + 0.4, 3.2, 48, side='tile', top='terrazzo', bottom='tile'))
    zs = zb + 0.4
    R.parts.add(ring(cx, cy, zs, zs + 0.06, 3.1, 3.25, 48, top='brass', bottom='brass', inner='brass', outer='brass'))
    lx, ly = cx, cy + 0.6
    R.parts.add(box(lx - 0.35, ly - 0.25, zs, lx + 0.35, ly + 0.25, zs + 1.0, 'walnut', skip=('-z',)))
    g = Geo()
    P = [(lx - 0.45, ly - 0.35, zs + 1.0), (lx + 0.45, ly - 0.35, zs + 1.0), (lx + 0.45, ly + 0.35, zs + 1.0), (lx - 0.45, ly + 0.35, zs + 1.0),
         (lx - 0.45, ly - 0.35, zs + 1.05), (lx + 0.45, ly - 0.35, zs + 1.05), (lx + 0.45, ly + 0.35, zs + 1.3), (lx - 0.45, ly + 0.35, zs + 1.3)]
    ids = [g.vert(p) for p in P]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        g.face([ids[i] for i in f], 'walnut', [(0, 0), (1, 0), (1, 1), (0, 1)])
    R.parts.add(g.fix())
    R.parts.add(box(lx - 0.28, ly - 0.2, zs + 1.1, lx + 0.28, ly + 0.15, zs + 1.2, 'ivory'))     # an open book
    R.light(sphere(lx + 0.38, ly + 0.25, zs + 1.45, 0.07, 8, 4, 'e_candle'))
    R.nocol.add(cyl(lx + 0.38, ly + 0.25, zs + 1.3, zs + 1.4, 0.02, 6, side='brass', caps=False))
    R.spot('read', lx, ly - 0.7, zs, -math.pi / 2)
    # the lamp ring over the seats
    rr, zl = 10.0, 4.6
    R.nocol.add(ring(cx, cy, zl + 0.3, zl + 0.4, rr - 0.08, rr + 0.08, 64, top='brass', bottom='brass', inner='brass', outer='brass'))
    for q in range(24):
        a = q * 2 * math.pi / 24
        lamp(R, cx + rr * math.cos(a), cy + rr * math.sin(a), zl, 0.17, shade=False)
        R.nocol.add(cyl(cx + rr * math.cos(a), cy + rr * math.sin(a), zl + 0.1, zl + 0.3, 0.012, 4, side='brass', caps=False))
    for q in range(6):
        a = q * math.pi / 3
        R.nocol.add(cyl(cx + rr * math.cos(a), cy + rr * math.sin(a), zl + 0.4, TOP - 0.45, 0.015, 5, side='iron', caps=False))
    # bookcases round the rim, with gaps toward the doorways
    gap = math.radians(5.4)
    for q in range(8):
        c = q * math.pi / 4
        half = math.radians(27) if q % 2 == 0 else math.radians(18)
        n = 4 if q % 2 == 0 else 2
        arc_shelf(R, cx, cy, 13.45, c - half + gap, c + half - gap, n, 0, 6, frame='walnut')
    # corners: a lamp and an armchair each, facing the bowl
    for (x, y) in ((3.2, 3.2), (W - 3.2, 3.2), (3.2, W - 3.2), (W - 3.2, W - 3.2)):
        a = math.atan2(cy - y, cx - x)
        R.parts.add(box(-0.45, -0.45, 0, 0.45, 0.45, 0.45, 'velvet', skip=('-z',)).xform(a, x, y))
        R.parts.add(box(-0.45, -0.45, 0.45, -0.3, 0.45, 1.05, 'velvet').xform(a, x, y))
        R.spot('sit', x, y, 0.45, a)
        lx2, ly2 = x - math.cos(a) * 0.1 + math.cos(a + math.pi / 2) * 0.9, y - math.sin(a) * 0.1 + math.sin(a + math.pi / 2) * 0.9
        R.parts.add(cyl(lx2, ly2, 0, 1.5, 0.025, 6, side='brass', caps=False))
        R.parts.add(cyl(lx2, ly2, 0, 0.04, 0.2, 12, side='brass', top='brass'))
        R.light(cyl(lx2, ly2, 1.5, 1.75, 0.2, 12, side='e_amber', top='e_amber', bottom='e_amber'))
    wall_shelves(R, ((0.8, 5.6), (26.4, W - 0.8)), rows=9, frame='walnut')
    # walkers
    loop(R, [(cx + 14.6 * math.cos(q * math.pi / 4 + math.pi / 8), cy + 14.6 * math.sin(q * math.pi / 4 + math.pi / 8)) for q in range(8)])
    mid = loop(R, [(cx + 12.1 * math.cos(q * math.pi / 4), cy + 12.1 * math.sin(q * math.pi / 4)) for q in range(8)], z=-0.38)
    low = loop(R, [(cx + 5.2 * math.cos(q * math.pi / 4), cy + 5.2 * math.sin(q * math.pi / 4)) for q in range(8)], z=zb)
    for q in (0, 4):
        R.link(mid[q], R.navpt(cx + 9.3 * math.cos(q * math.pi / 4), cy + 9.3 * math.sin(q * math.pi / 4), -1.14), low[q])
    R.spot('probe', cx, cy, 1.0)
    R.meta.update(label='The Amphitheatre', weight=5,
                  blurb='Terraces of seats go down to a stage and a lectern with a book left open on it. The acoustics are perfect. You could hear a page turn.')
    R.meta['box'] = [[T, zb, T], [W - T, TOP - 0.1, W - T]]
    return R
