"""The Great Dome: four long tunnels, each two meeting, lead into a round hall under a dome cut from
a sphere fifteen metres across its radius; it springs from a low drum lined with books and rises to
an oculus. Under the oculus stands a blank globe."""
from lib import *
from kit_f import *


def make():
    R = Room('greatdome', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    cx = cy = W / 2
    Rs, crown = 15.0, 7.05
    zc = crown - Rs
    Rf = 11.0
    zs = zc + math.sqrt(Rs * Rs - Rf * Rf)          # where the dome meets the drum (~2.25)
    R.cut(cyl(cx, cy, 0, zs + 0.01, Rf, 72, side='tile', bottom='terrazzo', top='plaster'))
    R.cut(dome_cap(cx, cy, zs, Rf, crown - zs, 72, 12, 'plaster', 'plaster'))
    R.cut(cyl(cx, cy, crown - 0.3, TOP - 0.06, 1.5, 32, side='tile', top='plaster', bottom='plaster'))
    R.light(cyl(cx, cy, TOP - 0.1, TOP - 0.08, 1.5, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    R.parts.add(ring(cx, cy, crown - 0.32, crown - 0.2, 1.5, 1.75, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    # the tunnels from the doorways; each pair meets before it reaches the hall
    pr = arch_profile(0, DW, 0, DJ, 18)
    Lt = 10.0
    for c in (8.0, 24.0):
        R.cut(prism([(p + c, q) for p, q in pr], 'y', T - 0.05, Lt, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism([(p + c, q) for p, q in pr], 'y', W - Lt, W - T + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism([(p + c, q) for p, q in pr], 'x', T - 0.05, Lt, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism([(p + c, q) for p, q in pr], 'x', W - Lt, W - T + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
    for (x, y) in ((8, 8), (24, 8), (8, 24), (24, 24)):
        lamp(R, x, y, 3.0, 0.2, chain=4.1)
        sx = 1 if x > cx else -1; sy = 1 if y > cy else -1
        for (dx, dy) in ((sx * 4.5, 0), (0, sy * 4.5)):
            lamp(R, x + dx, y + dy, 3.0, 0.15, chain=4.1)
    # books along the tunnels
    for c in (8.0, 24.0):
        for (a, b) in ((2.6, 6.3), (W - 6.3, W - 2.6)):
            R.shelf(c - DW / 2, b, 0, b - a, '+x', rows=5, frame='walnut')
            R.shelf(c + DW / 2, a, 0, b - a, '-x', rows=5, frame='walnut')
            R.shelf(a, c - DW / 2, 0, b - a, '+y', rows=5, frame='walnut')
            R.shelf(b, c + DW / 2, 0, b - a, '-y', rows=5, frame='walnut')
    # ribs up the dome
    nr = 16
    for k in range(nr):
        a = (k + 0.5) * 2 * math.pi / nr
        pts = []
        for q in range(9):
            r = Rf - 0.02 - (Rf - 1.8) * q / 8
            z = zc + math.sqrt(Rs * Rs - r * r) - 0.08
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
        for p0, p1 in zip(pts, pts[1:]):
            R.nocol.add(bar(p0, p1, 0.22, 0.16, 'tile'))
    R.parts.add(ring(cx, cy, zs - 0.2, zs + 0.05, Rf - 0.25, Rf + 0.05, 72, top='tile', bottom='tile', inner='tile', outer='tile'))
    # books round the drum, between the four entrances
    mouth = math.radians(19)
    for q in range(4):
        c = q * math.pi / 2
        arc_shelf(R, cx, cy, Rf - 0.05, c - math.pi / 4 + mouth, c + math.pi / 4 - mouth, 4, 0, 5, frame='walnut')
    # an inner ring of low double-sided stacks, open on the diagonals
    ri = 6.6
    for q in range(4):
        c = q * math.pi / 2
        n = 4
        a0 = c - math.radians(30)
        for k in range(n):
            t0 = a0 + math.radians(60) * k / n + 0.02; t1 = a0 + math.radians(60) * (k + 1) / n - 0.02
            p0 = (cx + ri * math.cos(t0), cy + ri * math.sin(t0)); p1 = (cx + ri * math.cos(t1), cy + ri * math.sin(t1))
            stack2_ax(R, p0[0], p0[1], p1[0], p1[1], 0, 4, frame='oak', crown='walnut', ends='walnut')
    # hanging lamps between the rings
    for k in range(12):
        a = k * 2 * math.pi / 12
        r = 8.8
        lamp(R, cx + r * math.cos(a), cy + r * math.sin(a), 3.1, 0.2, chain=zc + math.sqrt(Rs * Rs - r * r))
    # the blank globe under the oculus, a round bench about it
    R.parts.add(cyl(cx, cy, 0, 0.12, 1.6, 40, side='tile', top='tile'))
    R.parts.add(cyl(cx, cy, 0.12, 0.9, 0.12, 12, side='bronze', caps=False))
    R.parts.add(sphere(cx, cy, 2.1, 1.2, 24, 12, 'ivory'))
    R.nocol.add(ring(cx, cy, 2.05, 2.15, 1.3, 1.36, 48, top='bronze', bottom='bronze', inner='bronze', outer='bronze'))
    for q in range(4):
        R.parts.add(bar((cx + 1.32 * math.cos(q * math.pi / 2), cy + 1.32 * math.sin(q * math.pi / 2), 2.1), (cx + 0.9 * math.cos(q * math.pi / 2), cy + 0.9 * math.sin(q * math.pi / 2), 0.9), 0.05, 0.05, 'bronze'))
    R.parts.add(ring(cx, cy, 0, 0.45, 3.2, 3.7, 64, top='velvet', bottom='walnut', inner='walnut', outer='walnut'))
    for q in range(8):
        a = q * math.pi / 4 + math.pi / 8
        R.spot('sit', cx + 3.45 * math.cos(a), cy + 3.45 * math.sin(a), 0.45, a)
        R.light(box(-0.2, -0.02, 0.1, 0.2, 0.0, 0.2, 'e_pool').xform(a - math.pi / 2, cx + 3.72 * math.cos(a), cy + 3.72 * math.sin(a)))
    # walkers
    ring0 = loop(R, [(cx + 9.3 * math.cos(q * math.pi / 4), cy + 9.3 * math.sin(q * math.pi / 4)) for q in range(8)])
    ring1 = loop(R, [(cx + 4.7 * math.cos(q * math.pi / 4 + math.pi / 4), cy + 4.7 * math.sin(q * math.pi / 4 + math.pi / 4)) for q in range(8)])
    for q in range(4):
        a = q * math.pi / 2 + math.pi / 4
        m = R.navpt(cx + 7.8 * math.cos(a), cy + 7.8 * math.sin(a))
        R.link(ring1[q * 2], m, ring0[q * 2 + 1], R.navpt(cx + 11.3 * math.cos(a), cy + 11.3 * math.sin(a)))
    R.spot('probe', cx + 5.0, cy, 1.7)
    R.meta.update(label='The Great Dome', weight=5,
                  blurb='A dome as round as the inside of a thought, and under the hole in its top a globe with nothing drawn on it.')
    R.meta['box'] = [[T, 0, T], [W - T, TOP - 0.06, W - T]]
    return R
