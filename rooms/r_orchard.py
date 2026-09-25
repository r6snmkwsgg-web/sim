"""The Orchard: rows of old trees on a lawn under a glass roof, and the fruit is books, hanging on
strings, ripe; the windfalls lie in the grass. The biggest tree stands where the path splits. There is
a reading platform up in it, and a ladder on the side nobody looks at."""
from lib import *
from kit_h4 import *

W = 32.0
JAMB, RISE = 5.0, 2.4
BT = (16.0, 20.5)          # the biggest tree
PZ = 3.4                   # its platform
PR0, PR1 = 0.72, 2.7


def arc_band(c, w, jamb, rise, d0, d1, segs=40):
    a = arch_profile(c, w - 2 * d0, 0, jamb, segs, rise=rise - d0)
    b = arch_profile(c, w - 2 * d1, 0, jamb, segs, rise=rise - d1)
    return a[2:] + list(reversed(b[2:]))


def make():
    R = Room('orchard', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    rnd = random.Random(32)
    w = W - 2 * T + 0.04
    pr = arch_profile(W / 2, w, 0, JAMB, 48, rise=RISE)
    R.cut(prism(pr, 'y', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'grass', 'tile')))
    # the glass: a painted sky just under the vault, iron ribs and purlins holding it
    R.light(prism(arc_band(W / 2, w, JAMB, RISE, 0.0, 0.03), 'y', T, W - T, 'e_skydome', cap='e_skydome'))
    for k in range(17):
        y = T + 0.05 + k * (W - 2 * T - 0.1) / 16
        R.nocol.add(prism(arc_band(W / 2, w, JAMB, RISE, 0.03, 0.22), 'y', y - 0.05, y + 0.05, 'iron', cap='iron'))
    band = arch_profile(W / 2, w - 0.1, 0, JAMB, 48, rise=RISE - 0.05)[2:-1]
    for i in range(0, len(band), 3):
        p, q = band[i]
        R.nocol.add(box(p - 0.03, T, q - 0.1, p + 0.03, W - T, q - 0.03, 'iron'))
    for (x0, x1) in ((T, T + 0.35), (W - T - 0.35, W - T)):
        R.parts.add(box(x0, T, JAMB - 0.35, x1, W - T, JAMB, 'ivory'))
    # the path: marble up the middle, round the big tree
    R.nocol.add(box(14.4, T, 0.0, 17.6, BT[1] - 3.6, 0.015, 'marble'))
    R.nocol.add(box(14.4, BT[1] + 3.6, 0.0, 17.6, W - T, 0.015, 'marble'))
    R.nocol.add(ring(BT[0], BT[1], 0.0, 0.015, 2.9, 4.3, 40, top='marble', bottom='marble', inner='marble', outer='marble'))
    R.nocol.add(box(T, 15.0, 0.0, 14.4, 17.0, 0.015, 'marble'))
    R.nocol.add(box(17.6, 15.0, 0.0, W - T, 17.0, 0.015, 'marble'))

    walls(R, rnd)
    k = 0
    for x in (5.0, 10.2, 21.8, 27.0):
        for y in (4.4, 10.0, 21.4, 27.0):
            tree(R, x + rnd.uniform(-0.3, 0.3), y + rnd.uniform(-0.3, 0.3), rnd, h=3.0 + rnd.uniform(-0.2, 0.3), spread=1.9 if x in (5.0, 27.0) else 2.2, seed=k)
            k += 1
    big_tree(R, rnd)
    grass(R, rnd)

    navloop(R, [(16.0, 1.6), (16.0, 12.0), (13.5, 16.0), (12.5, 20.5), (13.5, 24.8), (16.0, 26.0), (16.0, 30.4), (16.0, 26.0), (18.5, 24.8), (19.5, 20.5), (18.5, 16.0), (16.0, 12.0)], close=False)
    navloop(R, [(1.6, 16.0), (7.6, 16.0), (13.5, 16.0)], close=False)
    navloop(R, [(18.5, 16.0), (24.4, 16.0), (30.4, 16.0)], close=False)
    navloop(R, [(7.6, 1.8), (7.6, 30.2), (24.4, 30.2), (24.4, 1.8)])
    R.spot('probe', 16.0, 9.0, 3.0)
    R.meta.update(label='The Orchard', weight=4,
                  blurb='The trees are heavy this year. Pick whatever you like; it is all the same fruit, more or less, and none of it is quite ripe.')
    R.meta['box'] = [[T, 0, T], [W - T, JAMB + RISE, W - T]]
    fx(R, 'dust', [T, T, 0.3, W - T, W - T, 6.0])
    secret(R, BT[0], BT[1] - 1.8, PZ, 'The Platform in the Tree',
           'Nobody looks at the back of the big tree. Up here someone has put a chair, a lamp and a stack of the ones that fell, and the glass is close enough to touch.', r=2.2)
    return tidy(R)


def walls(R, rnd):
    # bookcases round the walls between pilasters, lamps on little tables in front of them
    for (a, b) in ((0.8, 5.95), (10.05, 13.9), (18.1, 21.95), (26.05, W - 0.8)):
        sh(R, '+x', T, a, b, rows=10, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=10, frame='walnut')
        sh(R, '+y', T, a, b, rows=11, frame='walnut')
        sh(R, '-y', W - T, a, b, rows=11, frame='walnut')
    for p in (0.55, 6.25, 9.75, 14.15, 17.85, 22.25, 25.75, W - 0.55):
        for (x, y, d) in ((T, p, '+x'), (W - T, p, '-x'), (p, T, '+y'), (p, W - T, '-y')):
            R.parts.add(box(x - 0.25 if d == '-x' else x, y - 0.25, 0, x + 0.25 if d == '+x' else x, y + 0.25, JAMB - 0.35, 'ivory', skip=('-z',))
                        if d in ('+x', '-x') else
                        box(x - 0.25, y - 0.25 if d == '-y' else y, 0, x + 0.25, y + 0.25 if d == '+y' else y, JAMB - 0.35, 'ivory', skip=('-z',)))
    for (x, y, a) in ((1.4, 12.0, 0.0), (1.4, 20.0, 0.0), (W - 1.4, 12.0, math.pi), (W - 1.4, 20.0, math.pi), (12.0, 1.3, math.pi / 2), (20.0, W - 1.3, -math.pi / 2)):
        table(R, x - 0.4, y - 0.7, x + 0.4, y + 0.7) if a in (0.0, math.pi) else table(R, x - 0.7, y - 0.4, x + 0.7, y + 0.4)
        desk_lamp(R, x, y, 0.76)
    for (x, y) in ((13.9, 6.0), (18.1, 6.0), (13.9, 11.0), (18.1, 11.0), (13.9, 28.5), (18.1, 28.5)):
        post_lamp(R, x, y, 0.0, 2.6)


def leaves(R, cx, cy, cz, r, rnd, n=5):
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.2, 0.7) * r if k else 0.0
        rr = r * rnd.uniform(0.55, 0.85)
        R.nocol.add(blob(cx + math.cos(a) * d, cy + math.sin(a) * d, cz + rnd.uniform(-0.3, 0.3) * r, rr, rr, rr * 0.75, 'leaf', 6, 4, rnd.uniform(0, 3)))


def fruit(R, x, y, ztop, rnd):
    """A book hanging on a string."""
    L = rnd.uniform(0.25, 0.9)
    R.nocol.add(box(x - 0.006, y - 0.006, ztop - L, x + 0.006, y + 0.006, ztop, 'ivory'))
    b = box(-0.1, -0.03, -0.27, 0.1, 0.03, 0.0, rnd.choice(BOOKM))
    R.nocol.add(b.xform(rnd.uniform(0, math.pi), x, y, ztop - L))


def tree(R, x, y, rnd, h=3.0, spread=2.1, seed=0):
    """An old orchard tree: a leaning trunk, four or five limbs, a canopy, books hanging from it."""
    lean = (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3))
    top = (x + lean[0], y + lean[1], h * 0.62)
    R.parts.add(tube([(x, y, -0.1), (x + lean[0] * 0.4, y + lean[1] * 0.4, h * 0.3), top], [0.36, 0.28, 0.24], 10, 'bark'))
    for k in range(4):     # root flare
        a = k * math.pi / 2 + rnd.uniform(-0.4, 0.4)
        R.nocol.add(tube([(x, y, 0.35), (x + math.cos(a) * 0.55, y + math.sin(a) * 0.55, 0.05), (x + math.cos(a) * 0.9, y + math.sin(a) * 0.9, -0.05)], [0.16, 0.1, 0.05], 6, 'bark'))
    n = rnd.randint(4, 5)
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.3, 0.3)
        d = spread * rnd.uniform(0.7, 1.0)
        end = (top[0] + math.cos(a) * d, top[1] + math.sin(a) * d, h + rnd.uniform(0.4, 1.2))
        mid = (top[0] + math.cos(a) * d * 0.45, top[1] + math.sin(a) * d * 0.45, h * 0.62 + (end[2] - h * 0.62) * 0.7)
        R.nocol.add(tube([top, mid, end], [0.15, 0.09, 0.04], 6, 'bark'))
        leaves(R, end[0], end[1], end[2] + 0.2, rnd.uniform(1.1, 1.4), rnd, 2)
        for j in range(rnd.randint(2, 3)):
            fx_, fy = end[0] + rnd.uniform(-0.8, 0.8), end[1] + rnd.uniform(-0.8, 0.8)
            fruit(R, fx_, fy, end[2] - 0.35, rnd)
    leaves(R, top[0], top[1], h + 1.0, 1.5, rnd, 2)
    # windfalls
    for k in range(rnd.randint(2, 5)):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.7, 2.4)
        R.nocol.add(book(x + math.cos(a) * d, y + math.sin(a) * d, 0.0, rnd.uniform(0, 3.1), rnd.choice(BOOKM), t=0.04))


def big_tree(R, rnd):
    cx, cy = BT
    # a massive trunk, flared into roots over the lawn
    R.parts.add(tube([(cx, cy, -0.2), (cx + 0.1, cy, 2.0), (cx - 0.1, cy + 0.1, 4.2), (cx, cy, 5.7)], [1.05, 0.85, 0.72, 0.62], 16, 'bark'))
    for k in range(7):
        a = 2 * math.pi * k / 7 + rnd.uniform(-0.2, 0.2)
        if abs(math.atan2(math.sin(a - math.pi / 2), math.cos(a - math.pi / 2))) < 0.5: continue    # keep the ladder's foot clear
        L = rnd.uniform(2.0, 3.2)
        R.parts.add(tube([(cx + math.cos(a) * 0.6, cy + math.sin(a) * 0.6, 1.0), (cx + math.cos(a) * 1.3, cy + math.sin(a) * 1.3, 0.3),
                          (cx + math.cos(a) * L, cy + math.sin(a) * L, 0.02)], [0.42, 0.28, 0.08], 8, 'bark'))
    R.col.add(cyl(cx, cy, 0.0, PZ, 0.8, 12))     # the trunk is solid wood: nobody stands inside it
    # great limbs high over the platform, a canopy almost to the glass
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        d = rnd.uniform(4.2, 5.6)
        end = (cx + math.cos(a) * d, cy + math.sin(a) * d, 6.2 + rnd.uniform(-0.2, 0.4))
        mid = (cx + math.cos(a) * d * 0.45, cy + math.sin(a) * d * 0.45, 6.1)
        R.nocol.add(tube([(cx, cy, 5.3), mid, end], [0.42, 0.25, 0.08], 8, 'bark'))
        leaves(R, end[0], end[1], 6.4, 1.5, rnd, 4)
        leaves(R, mid[0], mid[1], 6.8, 1.3, rnd, 2)
        for j in range(5):
            t = rnd.uniform(0.35, 1.0)
            fruit(R, cx + math.cos(a) * d * t + rnd.uniform(-0.5, 0.5), cy + math.sin(a) * d * t + rnd.uniform(-0.5, 0.5), 5.6 + rnd.uniform(0, 0.4), rnd)
    leaves(R, cx, cy, 7.0, 1.6, rnd, 3)
    # the platform: an octagon of planks round the trunk, railed but for where the ladder comes up
    n = 8
    R.parts.add(ring(cx, cy, PZ - 0.16, PZ, PR0, PR1, n, top='oak', bottom='walnut', inner='walnut', outer='walnut', a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    for k in range(n):
        a0 = math.pi / 8 + 2 * math.pi * k / n; a1 = a0 + 2 * math.pi / n
        p0 = (cx + (PR1 - 0.08) * math.cos(a0), cy + (PR1 - 0.08) * math.sin(a0))
        p1 = (cx + (PR1 - 0.08) * math.cos(a1), cy + (PR1 - 0.08) * math.sin(a1))
        am = (a0 + a1) / 2
        if abs(math.atan2(math.sin(am - math.pi / 2), math.cos(am - math.pi / 2))) < 0.3:
            continue     # the gap, facing north
        arail(R, p0[0], p0[1], p1[0], p1[1], PZ, m='bark')
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        R.parts.add(tube([(cx + 0.8 * math.cos(a), cy + 0.8 * math.sin(a), 1.6), (cx + (PR1 - 0.4) * math.cos(a), cy + (PR1 - 0.4) * math.sin(a), PZ - 0.16)], 0.08, 6, 'bark'))
    # the ladder up the north side, behind a veil of leaves
    ladder_up(R, cx, cy + PR1 * math.cos(math.pi / 8) - 0.05 + PZ / math.tan(math.radians(60)), 0.0, PZ, '-y', w=0.9, m='bark', rail='bark')
    for k in range(4):
        R.nocol.add(blob(cx + rnd.choice((-1.4, 1.4)) + rnd.uniform(-0.3, 0.3), cy + PR1 + rnd.uniform(0.4, 1.8), rnd.uniform(1.6, 2.8), 0.6, 0.5, 0.8, 'leaf', 10, 5))
    # up there: a chair, a lamp, a small table, the windfalls somebody gathered
    chair(R, cx - 1.6, cy - 1.0, math.radians(35), PZ, frame='walnut', seat='velvet')
    table(R, cx - 0.9, cy - 2.3, cx + 0.1, cy - 1.6, PZ, h=0.7, top='leather')
    desk_lamp(R, cx - 0.6, cy - 1.95, PZ + 0.7)
    open_book(R, cx - 0.1, cy - 1.9, PZ + 0.7, 0.4)
    book_pile(R, cx + 1.5, cy - 1.2, PZ, 7, rnd)
    book_pile(R, cx + 1.7, cy + 0.5, PZ, 4, rnd)
    R.spot('plaque', cx + 1.0, cy - 1.8, PZ, -math.pi / 2, text='Everything in this orchard was planted by somebody who wanted to sit exactly here.')
    for (a, m) in ((0.9, 'e_candle'), (2.6, 'e_amber'), (4.4, 'e_candle')):
        x, y = cx + 3.4 * math.cos(a), cy + 3.4 * math.sin(a)
        R.nocol.add(cyl(x, y, 4.6, 5.9, 0.01, 4, side='iron', caps=False))
        R.light(sphere(x, y, 4.5, 0.12, 8, 4, m))


def grass(R, rnd):
    # tufts, and a few flowers of paper
    for k in range(0):
        x, y = rnd.uniform(1.2, W - 1.2), rnd.uniform(1.2, W - 1.2)
        if 14.2 < x < 17.8 or (15.0 < y < 17.0) or math.hypot(x - BT[0], y - BT[1]) < 4.4: continue
        h = rnd.uniform(0.08, 0.22)
        g = Geo()
        for j in range(2):
            a = j * math.pi / 2 + rnd.uniform(0, 1)
            g.add(box(-0.12, -0.004, 0.0, 0.12, 0.004, h, 'grass').xform(a, 0, 0, 0))
        R.nocol.add(g.xform(0, x, y, 0))
    # lanterns hung in the trees for the night
    for (x, y) in ((7.6, 7.2), (24.4, 7.2), (7.6, 24.2), (24.4, 24.2), (7.6, 13.0), (24.4, 19.0)):
        R.nocol.add(cyl(x, y, 3.3, 4.3, 0.008, 4, side='iron', caps=False))
        R.light(sphere(x, y, 3.2, 0.1, 8, 4, 'e_amber'))
