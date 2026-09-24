"""The Shrine: four long passages through walls four metres thick lead to a small round chamber under
a dome. In it, on a pedestal behind a velvet rope, one book; round it, tier on tier, hundreds of candles."""
import random
from lib import *
from kit_b import *

W0 = 4.0            # the walls' thickness: the chamber is the middle 8 m


def cheap_candle(R, x, y, z, h, r=0.022):
    R.nocol.add(cyl(x, y, z, z + h, r, 4, side='ivory', caps=False, a0=0.4, a1=0.4 + 2 * math.pi))
    R.light(cyl(x, y, z + h + 0.008, z + h + 0.07, 0.014, 3, side='e_candle', caps=False))


def make():
    R = Room('shrine', 1, 1, res=1024)
    rnd = random.Random(3)
    R.sockets(floor='slate', wall='tile')
    cx = cy = 8.0
    rc, zs = 4.0, 3.0
    # passages: full width through the outer part, then a narrow arched passage
    pw = 1.8
    for s in 'SNWE': door_tunnel(R, s, 2.3, 'slate', 'tile')
    pr = arch_profile(cx, pw, 0, 2.1, 14)
    R.cut(prism(pr, 'y', 2.2, cy, arch_mats(len(pr), 'slate', 'tile')))
    R.cut(prism(pr, 'y', cy, C - 2.2, arch_mats(len(pr), 'slate', 'tile')))
    R.cut(prism(pr, 'x', 2.2, cx, arch_mats(len(pr), 'slate', 'tile')))
    R.cut(prism(pr, 'x', cx, C - 2.2, arch_mats(len(pr), 'slate', 'tile')))
    # the chamber and its dome, with a little eye at the top
    R.cut(cyl(cx, cy, 0, zs + 0.01, rc, 32, side='tile', bottom='slate', top='tile'))
    R.cut(sphere(cx, cy, zs, rc, 32, 10, 'tile', lower=False))
    R.cut(cyl(cx, cy, zs + rc - 0.3, R.hi + 0.5, 0.35, 16, side='tile', top='tile', bottom='tile'))
    R.light(cyl(cx, cy, R.hi - 0.08, R.hi - 0.05, 0.35, 16, side='e_dim', top='e_dim', bottom='e_dim'))
    # tiers of candles round the chamber wall, broken at the passages
    gap = math.asin((pw / 2 + 0.15) / rc)
    n_c = 0
    for q in range(4):
        a0 = q * math.pi / 2 + gap
        a1 = (q + 1) * math.pi / 2 - gap
        for (z, r0) in ((0.35, 3.25), (0.7, 3.5), (1.05, 3.75)):
            R.parts.add(ring(cx, cy, 0, z, r0, rc + 0.05, 8, top='tile', bottom='tile', inner='tile', outer='tile', a0=a0, a1=a1))
            rm = r0 + 0.13
            n = int((a1 - a0) * rm / 0.2)
            for k in range(n):
                a = a0 + (k + 0.5) * (a1 - a0) / n + rnd.uniform(-0.01, 0.01)
                d = rnd.uniform(-0.06, 0.06)
                cheap_candle(R, cx + math.cos(a) * (rm + d), cy + math.sin(a) * (rm + d), z, rnd.uniform(0.06, 0.26))
                n_c += 1
        # and a row on the floor in front of the lowest tier
        rm = 3.05
        n = int((a1 - a0) * rm / 0.26)
        for k in range(n):
            a = a0 + (k + 0.5) * (a1 - a0) / n
            cheap_candle(R, cx + math.cos(a) * rm, cy + math.sin(a) * rm, 0.0, rnd.uniform(0.1, 0.35), 0.03)
            n_c += 1
    # candles in the passages, along the foot of both walls
    for s in range(4):
        ang = s * math.pi / 2
        ux, uy = math.cos(ang), math.sin(ang)
        vx, vy = -uy, ux
        for k in range(8):
            t = 4.25 + k * 0.21
            for side in (-1, 1):
                x = cx + ux * t + vx * side * (pw / 2 - 0.1)
                y = cy + uy * t + vy * side * (pw / 2 - 0.1)
                cheap_candle(R, x, y, 0.0, rnd.uniform(0.08, 0.3), 0.028)
                n_c += 1
    # the pedestal and the book
    R.parts.add(cyl(cx, cy, 0, 0.15, 0.95, 24, side='tile', top='tile', bottom='tile'))
    R.parts.add(cyl(cx, cy, 0.15, 0.3, 0.7, 24, side='tile', top='tile', bottom='tile'))
    R.parts.add(cyl(cx, cy, 0.3, 1.0, 0.24, 16, side='tile', top='tile', bottom='tile'))
    pr = [(cy - 0.32, 1.0), (cy + 0.32, 1.0), (cy + 0.32, 1.22), (cy - 0.32, 1.06)]
    R.parts.add(prism(pr, 'x', cx - 0.36, cx + 0.36, 'tile', cap='tile'))
    k = (1.22 - 1.06) / 0.64
    for s in (-1, 1):
        a0_, a1_ = (cx + 0.01, cx + 0.25) if s > 0 else (cx - 0.25, cx - 0.01)
        pp = [(cy - 0.2, 1.06 + 0.12 * k + 0.01), (cy + 0.2, 1.06 + 0.52 * k + 0.01), (cy + 0.2, 1.06 + 0.52 * k + 0.04), (cy - 0.2, 1.06 + 0.12 * k + 0.04)]
        R.nocol.add(prism(pp, 'x', a0_, a1_, 'ivory', cap='ivory'))
    pp = [(cy - 0.22, 1.06 + 0.1 * k), (cy + 0.22, 1.06 + 0.54 * k), (cy + 0.22, 1.06 + 0.54 * k + 0.012), (cy - 0.22, 1.06 + 0.1 * k + 0.012)]
    R.nocol.add(prism(pp, 'x', cx - 0.27, cx + 0.27, 'leather', cap='leather'))
    for (x, y) in ((cx - 0.3, cy + 0.36), (cx + 0.3, cy + 0.36)):
        candle(R, x, y, 1.0, h=0.3, r=0.03, flame=0.045)
    # the velvet rope on brass posts
    rr = 1.55
    posts = [(cx + math.cos(k * math.pi / 4 + math.pi / 8) * rr, cy + math.sin(k * math.pi / 4 + math.pi / 8) * rr) for k in range(8)]
    for (x, y) in posts:
        R.parts.add(cyl(x, y, 0, 0.05, 0.13, 10, side='brass', top='brass', bottom='brass'))
        R.parts.add(cyl(x, y, 0.05, 0.9, 0.03, 6, side='brass', caps=False))
        R.nocol.add(sphere(x, y, 0.93, 0.05, 6, 3, 'brass'))
    for k in range(8):
        (x0, y0), (x1, y1) = posts[k], posts[(k + 1) % 8]
        L = math.hypot(x1 - x0, y1 - y0); a = math.atan2(y1 - y0, x1 - x0)
        R.nocol.add(box(0.04, -0.025, 0.72, L / 2, 0.025, 0.77, 'velvet').xform(a, x0, y0))
        R.nocol.add(box(L / 2, -0.025, 0.72, L - 0.04, 0.025, 0.77, 'velvet').xform(a, x0, y0))
        R.nocol.add(box(L / 2 - 0.1, -0.025, 0.68, L / 2 + 0.1, 0.025, 0.73, 'velvet').xform(a, x0, y0))
    R.col.add(cyl(cx, cy, 0, 0.95, rr + 0.05, 16, side='tile', top='tile', bottom='tile'))
    R.spot('read', cx, cy - 2.0, 0, math.pi / 2)
    R.spot('read', cx, cy + 2.0, 0, -math.pi / 2)
    # walks
    ring_ = loop(R, [(cx + math.cos(k * math.pi / 4) * 2.35, cy + math.sin(k * math.pi / 4) * 2.35) for k in range(8)])
    for k, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
        a = R.navpt(cx + dx * 5.0, cy + dy * 5.0)
        b = R.navpt(cx + dx * 7.0, cy + dy * 7.0)
        R.link(ring_[k * 2], a, b)
    R.spot('probe', cx, cy - 2.4, 1.7)
    R.meta.update(label='The Shrine', weight=3,
                  blurb='One book, on its own, behind a rope, with more candles than anyone could light. Whoever keeps them lit is very quiet about it.')
    R.meta['box'] = [[2.2, 0, 2.2], [C - 2.2, zs + rc, C - 2.2]]
    print('shrine candles:', n_c)
    return R
