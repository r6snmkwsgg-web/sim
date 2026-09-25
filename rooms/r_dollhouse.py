"""The Dollhouse: an ordinary reading hall, except that the whole north side is a library built at a
tenth of the size: knee-high doors, windows the height of a hand, lamps lit in rooms you could hold
in your palm, shelves of books the size of sugar cubes. Its grand gallery is just tall enough to crawl
along. At its far end a hole in the skirting leads to a room that is a copy of the little rooms, at
the size of a real one."""
from lib import *
from kit_h2 import *

YF = 9.0                  # the dollhouse's front
YG0, YG1 = YF + 0.35, YF + 1.45   # its grand gallery (crawl height)
GH = 1.3
GX0, GX1 = 10.9, 21.1     # the gallery's length (between the two north doorways)
HR = (11.2, 20.8, 12.3, C - T - 0.25)   # the full-size room behind
HRH = 3.4
H = 6.8                   # the hall's ceiling
S0 = (1.45, 1.95)         # the two upper storeys of little rooms (window bottom, top)
S1 = (2.2, 2.7)


def slab(R, x0, x1, yb, z, h, depth, n=(0, -1, 0)):
    """Books standing against a back wall at y=yb, facing -y."""
    R.slabs.append({'o': [x1, yb - depth, z], 'u': [-(x1 - x0), 0, 0], 'v': [0, 0, h], 'n': list(n),
                    'len': x1 - x0, 'h': h, 'depth': depth - 0.005, 'ghost': False})


def make():
    R = Room('dollhouse', 2, 1, res=2048)
    W, D = R.W, R.D
    shell2(R, W, D)
    facade(R, W)
    gallery(R)
    hidden(R)
    hall(R, W, D)
    return tidy(R)


def shell2(R, W, D):
    R.sockets(floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, YF, H, 'tile', bottom='floor', top='plaster'))
    pr = arch_profile(0, DW, 0, DJ)
    for i in range(2):
        cx = i * C + C / 2
        R.cut(prism([(p + cx, q) for p, q in pr], 'y', YF - 0.05, D - T + 0.01, arch_mats(len(pr), 'floor', 'tile')))


def little_room(R, x0, x1, z0, z1, depth, rnd, lamps, inner):
    """A window into a room a tenth of the size: damask walls, a red carpet, a shelf of books the size of
    sugar cubes, a desk and a lamp."""
    y1 = YF + depth
    R.cut(box(x0, YF - 0.05, z0, x1, y1, z1, 'damask', bottom='carpet', top='plaster'))
    # its bookcase against the back wall: two rows
    inner.add(box(x0 + 0.03, y1 - 0.06, z0, x1 - 0.03, y1, z0 + 0.2, 'walnut', skip=('+y', '-z')))
    slab(R, x0 + 0.05, x1 - 0.05, y1 - 0.005, z0 + 0.012, 0.05, 0.05)
    slab(R, x0 + 0.05, x1 - 0.05, y1 - 0.005, z0 + 0.09, 0.05, 0.05)
    inner.add(box(x0 + 0.04, y1 - 0.055, z0 + 0.075, x1 - 0.04, y1 - 0.005, z0 + 0.085, 'walnut', skip=('+y', '-x', '+x')))
    # a desk with a lamp, and a chair
    dx = x0 + (x1 - x0) * (0.3 + 0.4 * rnd.random()); dy = YF + depth * 0.45
    inner.add(box(dx - 0.06, dy - 0.03, z0 + 0.06, dx + 0.06, dy + 0.03, z0 + 0.075, 'walnut', skip=('-z',)))
    inner.add(box(dx - 0.055, dy - 0.02, z0, dx + 0.055, dy + 0.02, z0 + 0.06, 'walnut', skip=('-z', '+z', '-x', '+x')))
    lamps.add(box(dx + 0.02, dy - 0.01, z0 + 0.1, dx + 0.05, dy + 0.01, z0 + 0.108, 'e_lamp'))
    inner.add(box(dx + 0.018, dy - 0.013, z0 + 0.108, dx + 0.052, dy + 0.013, z0 + 0.118, 'green', skip=('-z',)))
    inner.add(box(dx - 0.02, dy - 0.075, z0, dx + 0.02, dy - 0.045, z0 + 0.09, 'leather', skip=('-z',)))
    # a window frame and a sill, and glazing bars
    g = Geo()
    g.add(box(x0 - 0.03, YF - 0.04, z0 - 0.04, x1 + 0.03, YF, z0, 'ivory', skip=('+y',)))
    g.add(box(x0 - 0.03, YF - 0.03, z1, x1 + 0.03, YF, z1 + 0.03, 'ivory', skip=('+y',)))
    return g


def facade(R, W):
    """The front of the little library: stone, three storeys, cornices, a pediment, lit windows."""
    rnd = random.Random(12)
    lamps = Geo(); inner = Geo(); fr = Geo()
    runs = ((T + 0.25, 6.2), (9.8, 22.2), (25.8, W - T - 0.25))
    for (a, b) in runs:
        # plinth, string courses, cornice
        fr.add(box(a, YF - 0.06, 0, b, YF, 0.12, 'tile', skip=('+y', '-z')))
        for z in (1.3, 2.05):
            fr.add(box(a, YF - 0.07, z, b, YF, z + 0.07, 'ivory', skip=('+y',)))
        fr.add(box(a - 0.05, YF - 0.12, 2.85, b + 0.05, YF, 2.97, 'ivory', skip=('+y',)))
        # a balustrade on the roof line, with little urns
        fr.add(box(a, YF - 0.08, 2.97, b, YF, 3.0, 'ivory', skip=('+y', '-z')))
        fr.add(box(a, YF - 0.08, 3.14, b, YF, 3.17, 'ivory', skip=('+y',)))
        n = int((b - a) / 0.07)
        for k in range(n):
            x = a + 0.035 + k * (b - a - 0.07) / max(1, n - 1)
            fr.add(box(x - 0.012, YF - 0.06, 3.0, x + 0.012, YF - 0.02, 3.14, 'ivory', skip=('+y', '-z', '+z')))
        # the little rooms, two storeys of them; pilasters between
        nw = int((b - a) / 0.62)
        pitch = (b - a) / nw
        for k in range(nw):
            xc = a + (k + 0.5) * pitch
            for (z0, z1) in (S0, S1):
                fr.add(little_room(R, xc - 0.17, xc + 0.17, z0, z1, 0.55, rnd, lamps, inner))
            if k:
                x = a + k * pitch
                fr.add(box(x - 0.03, YF - 0.05, 1.37, x + 0.03, YF, 2.85, 'ivory', skip=('+y', '-z', '+z')))
        # the ground storey: knee-high doors into the gallery (only the middle run has one behind it)
        if a < 9:   # west run: blind arcade with doors that do not open
            ground_blind(R, a, b, fr, rnd)
        elif b > 23:
            ground_blind(R, a, b, fr, rnd)
    # the middle run's ground storey: an arcade of knee-high doorways looking into the gallery,
    # and the grand entrance in the middle, crawl height, with steps and columns
    a, b = runs[1]
    for k in range(14):
        xc = GX0 + 0.5 + k * (GX1 - GX0 - 1.0) / 13
        if abs(xc - 16.0) < 1.0: continue
        pr = arch_profile(xc, 0.3, 0.12, 0.42, 8)
        R.cut(prism(pr, 'y', YF - 0.05, YG0 + 0.02, arch_mats(len(pr), 'tile', 'ivory')))
        fr.add(box(xc - 0.19, YF - 0.05, 0.12, xc - 0.15, YF, 0.54, 'ivory', skip=('+y', '-z')))
        fr.add(box(xc + 0.15, YF - 0.05, 0.12, xc + 0.19, YF, 0.54, 'ivory', skip=('+y', '-z')))
        if k % 3 == 1:   # a little door leaf, half open
            leaf = box(0, -0.02, 0, 0.28, 0.0, 0.55, 'oak')
            leaf.add(box(0.22, -0.035, 0.26, 0.25, -0.02, 0.29, 'brass'))
            R.nocol.add(leaf.xform(-1.9, xc + 0.15, YF - 0.01, 0.12))
    # the grand entrance
    pr = arch_profile(16.0, 1.0, 0.0, GH - 0.5, 12)
    R.cut(prism(pr, 'y', YF - 0.05, YG0 + 0.02, arch_mats(len(pr), 'floor', 'ivory')))
    for x in (15.35, 16.65):
        fr.add(cyl(x, YF - 0.25, 0, 1.25, 0.08, 10, side='ivory', caps=False))
        fr.add(box(x - 0.12, YF - 0.37, 1.25, x + 0.12, YF - 0.13, 1.33, 'ivory'))
    fr.add(box(15.1, YF - 0.45, 1.33, 16.9, YF, 1.43, 'ivory', skip=('+y',)))
    ped = [(15.05, 1.43), (16.95, 1.43), (16.0, 1.8)]
    fr.add(prism(ped, 'y', YF - 0.45, YF, 'ivory', cap='ivory'))
    # an engraved name plate and a tiny clock in the pediment
    fr.add(box(15.5, YF - 0.47, 1.35, 16.5, YF - 0.45, 1.41, 'brass'))
    fr.add(box(15.93, YF - 0.47, 1.5, 16.07, YF - 0.45, 1.64, 'brass'))
    # a pediment over the whole middle run, with a dome behind
    ped = [(12.0, 3.17), (20.0, 3.17), (16.0, 4.1)]
    fr.add(prism(ped, 'y', YF - 0.15, YF + 1.2, 'ivory', cap='ivory'))
    R.parts.add(weld(fr))
    R.nocol.add(inner)
    R.light(lamps)


def ground_blind(R, a, b, fr, rnd):
    n = int((b - a) / 0.5)
    for k in range(n):
        xc = a + (k + 0.5) * (b - a) / n
        pr = arch_profile(xc, 0.28, 0.12, 0.4, 8)
        if k % 2 == 0:
            R.cut(prism(pr, 'y', YF - 0.05, YF + 0.06, arch_mats(len(pr), 'tile', 'ivory')))
            fr.add(box(xc - 0.14, YF + 0.04, 0.12, xc + 0.14, YF + 0.06, 0.66, 'oak', skip=('+y',)))
            fr.add(box(xc + 0.08, YF + 0.02, 0.35, xc + 0.1, YF + 0.04, 0.37, 'brass'))
        else:   # a little lit window instead
            R.cut(box(xc - 0.1, YF - 0.05, 0.45, xc + 0.1, YF + 0.3, 0.85, 'damask', bottom='carpet', top='plaster'))
            R.light(box(xc - 0.015, YF + 0.2, 0.7, xc + 0.015, YF + 0.23, 0.73, 'e_lamp'))
            slab(R, xc - 0.08, xc + 0.08, YF + 0.3, 0.46, 0.05, 0.05)


def gallery(R):
    """The little library's grand gallery: a hall thirteen metres high at its own scale, crawl height at
    ours. Book alcoves along its back, chandeliers the size of a fist."""
    R.cut(box(GX0, YG0, 0, GX1, YG1, GH, 'ivory', bottom='floor', top='plaster'))
    rnd = random.Random(5)
    lamps = Geo(); g = Geo()
    # alcoves of books along the back, each a real bookcase at a tenth of the size
    n = 16
    for k in range(n):
        x0 = GX0 + 0.25 + k * (GX1 - GX0 - 0.5) / n; x1 = x0 + (GX1 - GX0 - 0.5) / n - 0.12
        if abs((x0 + x1) / 2 - 20.45) < 0.75: continue      # keep the way out clear
        R.cut(box(x0, YG1 - 0.05, 0, x1, YG1 + 0.2, 1.05, 'walnut', bottom='floor', top='walnut'))
        for r in range(12):
            z = 0.02 + r * 0.082
            slab(R, x0 + 0.02, x1 - 0.02, YG1 + 0.2, z, 0.055, 0.1)
            g.add(box(x0, YG1 - 0.05, z - 0.012, x1, YG1 + 0.2, z, 'walnut', skip=('-z', '+y', '-x', '+x')))
        # pilasters between
        g.add(box(x1 + 0.01, YG1 - 0.06, 0, x1 + 0.11, YG1, 1.15, 'ivory', skip=('+y', '-z')))
    # a coffered ceiling line and little chandeliers
    for k in range(6):
        x = GX0 + 1.0 + k * (GX1 - GX0 - 2.0) / 5
        R.nocol.add(cyl(x, (YG0 + YG1) / 2, 1.1, GH, 0.005, 4, side='brass', caps=False))
        R.nocol.add(ring(x, (YG0 + YG1) / 2, 1.06, 1.08, 0.06, 0.08, 10, top='brass', bottom='brass', inner='brass', outer='brass'))
        for j in range(5):
            a = j * 2 * math.pi / 5
            lamps.add(sphere(x + 0.07 * math.cos(a), (YG0 + YG1) / 2 + 0.07 * math.sin(a), 1.1, 0.012, 6, 3, 'e_lamp'))
    # a runner, and little benches and globes down the middle
    R.nocol.add(box(GX0 + 0.3, (YG0 + YG1) / 2 - 0.25, 0, GX1 - 0.3, (YG0 + YG1) / 2 + 0.25, 0.008, 'carpet', sides='oxblood'))
    R.parts.add(weld(g))
    R.light(lamps)
    # the way out: a hole in the skirting at the east end, into the wall
    R.cut(box(19.9, YG1 - 0.05, 0, 21.0, HR[2] + 0.05, 1.25, 'plaster', bottom='floor', top='plaster'))
    # somebody's things left in the crawlway
    R.light(box(20.35, YG1 + 0.4, 0.01, 20.55, YG1 + 0.45, 0.04, 'e_candle'))
    a, b, c = R.navpt(16.0, YF - 1.2), R.navpt(16.0, (YG0 + YG1) / 2), R.navpt(20.45, (YG0 + YG1) / 2)
    d = R.navpt(20.45, HR[2] + 0.8)
    R.link(a, b, c, d)
    R.navpt(12.0, (YG0 + YG1) / 2); R.link(b, len(R.nav) - 1)


def hidden(R):
    """Behind: a room exactly like the little ones, at full size. Damask walls, a red carpet, a bookcase,
    a desk with a green lamp, a chair."""
    x0, x1, y0, y1 = HR
    R.cut(box(x0, y0, 0, x1, y1, HRH, 'damask', bottom='carpet', top='plaster'))
    sh(R, '-y', y1, x0 + 0.3, x1 - 0.3, rows=7, frame='walnut')
    R.parts.add(box(x0, y0, 0, x1, y0 + 0.05, 0.15, 'walnut', skip=('-z',)))
    dx, dy = 14.5, y0 + 1.3
    R.parts.add(table(dx - 0.8, dy - 0.4, dx + 0.8, dy + 0.4, 0.76, 'walnut', top='leather'))
    desk_lamp(R, dx + 0.45, dy + 0.15, 0.76)
    R.parts.add(chair(dx - 0.2, dy - 0.75, math.pi / 2))
    R.spot('sit', dx - 0.2, dy - 0.75, 0.48, math.pi / 2)
    open_book_prop(R, dx - 0.2, dy - 0.05, 0.76)
    # a window that looks out onto nothing but a painted garden, a bed, a clock
    R.light(box(x0 + 0.01, y0 + 0.6, 1.0, x0 + 0.03, y1 - 0.8, 2.3, 'e_sky'))
    R.parts.add(box(x0, y0 + 0.5, 0.95, x0 + 0.12, y1 - 0.7, 1.0, 'ivory'))
    R.parts.add(box(x1 - 2.1, y0 + 0.1, 0, x1 - 0.2, y0 + 1.0, 0.5, 'bed', sides='walnut'))
    R.nocol.add(box(x1 - 0.7, y0 + 0.2, 0.5, x1 - 0.3, y0 + 0.9, 0.62, 'ivory'))
    R.spot('bed', x1 - 1.2, y0 + 0.55, 0.5, math.pi)
    bulb(R, (x0 + x1) / 2, (y0 + y1) / 2, HRH - 0.7, r=0.14, m='e_lamp', top=HRH, shade='brass')
    candle(R, x0 + 0.5, y1 - 0.6, 0.0, h=0.25, stand=0.9)
    R.spot('plaque', 17.5, y0 + 0.2, 1.5, math.pi / 2)
    secret(R, 17.0, (y0 + y1) / 2, 0.0, 'The Room Behind the Dollhouse',
           'You crawl out of the little library into one of its rooms, the same wallpaper, the same lamp, the same chair. Except that this one is your size. Or you are its.', r=2.5)
    a, b = R.navpt(18.5, y0 + 1.2), R.navpt(12.5, y0 + 2.2)
    R.link(a, b)
    R.link(3, a)


def hall(R, W, D):
    rows = 14
    sh(R, '+y', T, 0.6, 6.0, rows=rows, frame='walnut')
    sh(R, '+y', T, 10.0, 22.0, rows=rows, frame='walnut')
    sh(R, '+y', T, 26.0, W - 0.6, rows=rows, frame='walnut')
    sh(R, '+x', T, 0.6, 6.0, rows=rows, frame='walnut')
    sh(R, '-x', W - T, 0.6, 6.0, rows=rows, frame='walnut')
    # full-size books over the little library's roof
    sh(R, '-y', YF, 0.6, W - 0.6, z=4.35, rows=5, frame='walnut')
    # coffered ceiling with lay-lights
    for k in range(4):
        x = 4.0 + k * 8.0
        R.cut(box(x - 2.4, 2.2, H - 0.05, x + 2.4, 6.6, H + 0.4, 'plaster'))
        R.light(box(x - 2.0, 2.6, H + 0.34, x + 2.0, 6.2, H + 0.36, 'e_sky', skip=('+z',)))
    # two reading tables, with chairs facing the little library
    for x0 in (3.0, 19.5):
        R.parts.add(table(x0, 4.0, x0 + 9.5, 5.2, 0.78, 'walnut', top='leather'))
        for k in range(3):
            x = x0 + 1.2 + k * 3.5
            desk_lamp(R, x, 4.6, 0.78)
            R.parts.add(chair(x + 0.9, 5.75, -math.pi / 2))
            R.spot('sit', x + 0.9, 5.75, 0.48, -math.pi / 2)
    # a stool and a cushion in front of the entrance, for kneeling
    R.parts.add(box(14.2, YF - 1.4, 0, 14.8, YF - 0.8, 0.14, 'velvet', skip=('-z',)))
    for (x, y) in ((1.4, YF - 0.7), (W - 1.4, YF - 0.7)):
        R.nocol.add(cyl(x, y, 0, 1.2, 0.02, 6, side='brass', caps=False))
        R.nocol.add(cyl(x, y, 0, 0.03, 0.16, 10, side='brass', top='brass'))
        R.col.add(box(x - 0.1, y - 0.1, 0, x + 0.1, y + 0.1, 1.2, 'tile'))
        R.light(sphere(x, y, 1.3, 0.1, 10, 5, 'e_amber'))
    ids = navloop(R, [(2.0, 2.0), (8.0, 2.0), (16.0, 2.2), (24.0, 2.0), (W - 2.0, 2.0), (W - 2.0, 7.2), (24.0, 7.2), (16.0, 7.2), (8.0, 7.2), (2.0, 7.2)])
    R.link(ids[7], 0)
    R.spot('probe', 16.0, 6.8, 1.7)
    R.meta.update(label='The Dollhouse', weight=4,
                  blurb='Along the north wall somebody has built the library again, at a tenth of the size, and left all its lamps on. Its front door is just big enough, if you kneel.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
