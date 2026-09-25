"""The Whale: a long hall inside a ribcage. Bone ribs arch over the aisle from the floor to a spine
along the ceiling, the bookcases stand between them, and the light is red and low. Behind one
bookcase, the heart."""
from kit_h5 import *

W, D = 2 * C, C
H = TOP - 0.1
YS = 4.4                        # the hall's south wall; the heart chamber lies behind it
YN = D - T
YC = (YS + YN) / 2              # the ribcage's centre line
RF = 1.6                        # rib feet stand this far in from the bookcases
RIBS = (3.0, 5.9, 10.1, 13.05, 16.0, 18.95, 21.9, 26.1, 29.0)
HX0, HX1 = 12.4, 19.6           # the heart chamber
HY0, HY1 = 0.65, 3.95
HZ = 3.3
FX0, FX1 = 15.25, 16.75         # the false bookcase


def make():
    R = Room('whaleribs', 2, 1, res=2048)
    rng = random.Random(38)
    R.sockets(floor='floor', wall='tile', skip=())
    R.cut(box(T - 0.02, YS, 0, W - T + 0.02, YN + 0.02, H, 'oxblood', bottom='floor', top='velvet'))
    pr = arch_profile(0, DW, 0, DJ)
    for x in (8.0, 24.0):
        R.cut(prism([(p + x, q) for p, q in pr], 'y', T, YS + 0.05, arch_mats(len(pr), 'floor', 'tile')))
    # the ribs
    for x in RIBS:
        rib(R, x)
    spine(R, rng)
    # bookcases along both walls between the ribs, and over the doors
    rows = 14
    slabs = []
    for (a, b) in ((0.8, 6.3), (9.7, FX0), (FX1, 22.3), (25.7, 31.2)):
        slabs += sh(R, '+y', YS, a, b, rows=rows, frame='walnut')
    shelf(R, FX0, YS, 0, FX1 - FX0, '+y', rows=rows, frame='walnut', solid=False)
    for (a, b) in ((0.8, 6.3), (9.7, 22.3), (25.7, 31.2)):
        slabs += sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
    for x in (8.0, 24.0):
        sh(R, '+y', YS, x - 1.7, x + 1.7, z=4.3, rows=6, frame='walnut')
        sh(R, '-y', YN, x - 1.7, x + 1.7, z=4.3, rows=6, frame='walnut')
    for (x0, x1) in ((T, 0.8), (31.2, W - T)):
        pass
    # the red: low coves along both walls behind the rib feet, and glowing flesh between the ribs overhead
    for (y0, y1) in ((YS + 0.36, YS + 0.44), (YN - 0.44, YN - 0.36)):
        R.light(box(0.8, y0, 0.02, 31.2, y1, 0.08, 'e_red'))
    for k in range(len(RIBS) - 1):
        xm = (RIBS[k] + RIBS[k + 1]) / 2
        for s in (-1, 1):
            R.light(box(xm - 0.6, YC + s * 2.6 - 0.5, H - 0.03, xm + 0.6, YC + s * 2.6 + 0.5, H - 0.01, 'e_red'))
    # green lamps on little desks in the bays, alternating sides
    for k in range(len(RIBS) - 1):
        xm = (RIBS[k] + RIBS[k + 1]) / 2
        if abs(xm - 8) < 2.6 or abs(xm - 24) < 2.6: continue
        y = YS + RF + 0.2 if k % 2 == 0 else YN - RF - 0.2
        sgn = 1 if k % 2 == 0 else -1
        R.parts.add(table(xm - 0.55, y - 0.3, xm + 0.55, y + 0.3, 0.78, 'walnut', top='leather'))
        desk_lamp(R, xm, y - sgn * 0.1, 0.78, m='e_dim')
        R.parts.add(chair(xm, y + sgn * 0.62, -sgn * math.pi / 2))
    # a long runner down the aisle
    R.nocol.add(box(0.8, YC - 0.9, 0, 31.2, YC + 0.9, 0.012, 'carpet'))
    for s in (-1, 1):
        R.nocol.add(box(0.8, YC + s * 0.9 - 0.04, 0, 31.2, YC + s * 0.9 + 0.04, 0.014, 'gilt'))
    # amber night lamps at the ends
    for x in (1.2, 30.8):
        for y in (YS + 1.2, YN - 1.2):
            R.parts.add(cyl(x, y, 0, 1.4, 0.02, 6, side='brass', caps=False))
            R.parts.add(cyl(x, y, 0, 0.03, 0.18, 12, side='brass', top='brass'))
            R.light(sphere(x, y, 1.5, 0.11, 10, 5, 'e_amber'))
    heart(R, rng)
    navloop(R, [(2.0, YC), (8.0, YC - 0.5), (16.0, YC), (24.0, YC + 0.5), (30.0, YC)], close=False)
    a = R.navpt(8.0, YS + 0.8); b = R.navpt(24.0, YN - 0.8); c = R.navpt(8.0, YN - 0.8); d = R.navpt(24.0, YS + 0.8)
    R.link(a, 1, c); R.link(d, 3, b)
    R.spot('probe', 16.0, YC, 3.0)
    R.meta.update(label='The Whale', weight=3,
                  blurb='You are inside something that was once alive and very large. The ribs hold up the ceiling now, and the shelves between them are full.')
    R.meta['box'] = [[T, 0, YS], [W - T, H, YN]]
    return tidy(R)


def rib_pts(x, n=14, flare=0.35):
    a = (YN - YS) / 2 - RF
    h = H - 0.55
    pts = []
    for k in range(n + 1):
        t = math.pi * k / n
        f = flare * (1 - math.sin(t)) ** 2          # the feet splay outward
        y = YC - (a + f) * math.cos(t)
        z = h * math.sin(t) ** 0.85
        pts.append((x, y, z))
    return pts


def rib(R, x):
    pts = rib_pts(x)
    n = len(pts) - 1
    for k in range(n):
        t = abs(k + 0.5 - n / 2) / (n / 2)          # 1 at the feet, 0 at the crown
        w = 0.26 + 0.2 * t
        R.parts.add(beam(pts[k], pts[k + 1], w * 0.8, 'ivory', w + 0.05))
    for p in (pts[0], pts[-1]):
        R.parts.add(cone(p[0], p[1], 0, 0.5, 0.42, 0.26, 10, 'ivory'))


def spine(R, rng):
    """The vertebrae along the crown: a chain of bone blocks with spines up into the flesh."""
    z = H - 0.55
    x = 0.6
    while x < W - 0.6:
        L = 0.62
        R.nocol.add(box(x, YC - 0.34, z - 0.28, x + L, YC + 0.34, z + 0.18, 'ivory'))
        R.nocol.add(box(x + 0.12, YC - 0.12, z + 0.18, x + L - 0.12, YC + 0.12, H, 'ivory'))
        for s in (-1, 1):
            R.nocol.add(beam((x + L / 2, YC + s * 0.3, z), (x + L / 2 + 0.05, YC + s * 0.95, z - 0.12 + 0.04 * rng.random()), 0.14, 'ivory', 0.1))
        R.nocol.add(box(x + L, YC - 0.25, z - 0.2, x + L + 0.1, YC + 0.25, z + 0.1, 'bed'))
        x += L + 0.12


def heart(R, rng):
    """Behind the false bookcase: a chamber the shape of a lung, and the heart hanging in it."""
    r = (HY1 - HY0) / 2
    cy = (HY0 + HY1) / 2
    R.cut(box(HX0 + r, HY0, 0, HX1 - r, HY1, HZ, 'velvet', bottom='oxblood', top='velvet'))
    for x in (HX0 + r, HX1 - r):
        R.cut(cyl(x, cy, 0, HZ, r, 20, side='velvet', top='velvet', bottom='oxblood'))
    R.cut(box(FX0 + 0.05, HY1 - 0.1, 0, FX1 - 0.05, YS + 0.05, 2.3, 'velvet', bottom='oxblood'))
    # small ribs round the chamber walls
    for x in (HX0 + r + 0.6, 14.9, 17.1, HX1 - r - 0.6):
        for k in range(8):
            t0, t1 = math.pi * k / 8, math.pi * (k + 1) / 8
            p0 = (x, cy - (r - 0.1) * math.cos(t0), (HZ - 0.15) * math.sin(t0) + 0.0)
            p1 = (x, cy - (r - 0.1) * math.cos(t1), (HZ - 0.15) * math.sin(t1))
            if max(p0[2], p1[2]) < 0.4 or abs(x - 16) < 1.2 and min(p0[1], p1[1]) > cy + 0.6 and min(p0[2], p1[2]) < 2.4: continue
            R.nocol.add(beam(p0, p1, 0.12, 'ivory', 0.16))
    # the heart, hung in the west lobe
    hx, hy, hz = HX0 + r, cy, 1.9
    R.nocol.add(blob(hx, hy, hz, 0.75, 0.62, 0.85, 12, 6, 'oxblood'))
    R.nocol.add(blob(hx + 0.35, hy - 0.2, hz - 0.35, 0.5, 0.5, 0.6, 10, 5, 'velvet'))
    R.nocol.add(blob(hx - 0.3, hy + 0.3, hz + 0.6, 0.42, 0.4, 0.38, 10, 4, 'oxblood'))
    R.col.add(cyl(hx, hy, 0.9, HZ, 0.8, 10))
    for (dx, dy, rr) in ((0.1, 0.15, 0.2), (-0.3, -0.25, 0.14), (0.35, 0.1, 0.12)):
        R.nocol.add(cyl(hx + dx, hy + dy, hz + 0.5, HZ, rr, 10, side='oxblood', caps=False))
    # veins, glowing
    for k in range(9):
        a = 2 * math.pi * k / 9
        p0 = (hx + math.cos(a) * 0.55, hy + math.sin(a) * 0.45, hz + rng.uniform(-0.4, 0.5))
        p1 = (hx + math.cos(a + 0.4) * 0.7, hy + math.sin(a + 0.4) * 0.58, p0[2] - 0.35)
        R.light(beam(p0, p1, 0.03, 'e_red'))
    R.light(box(hx - 0.5, hy - 0.5, 0.0, hx + 0.5, hy + 0.5, 0.03, 'e_red'))
    # in the east lobe: a chair facing it, a table, a book, a candle
    ex = HX1 - r
    R.parts.add(chair(ex - 0.2, cy, math.pi))
    R.spot('sit', ex - 0.2, cy, 0.48, math.pi)
    R.parts.add(table(ex + 0.35, cy - 0.35, ex + 1.0, cy + 0.35, 0.72, 'walnut'))
    ob = open_book(0.19, 0.27, 0.25, 'oxblood'); orient(ob, 0.2, 0, 0, ex + 0.68, cy, 0.74)
    R.nocol.add(ob)
    candle(R, ex + 0.85, cy + 0.22, 0.72, h=0.14)
    R.spot('plaque', ex + 0.68, cy, 0.74)
    secret(R, 16.0, cy, 0, 'The Heart Chamber',
           'Behind the books, something very large is still keeping time. You have the feeling it has been waiting for a reader.', r=2.0)
    fx(R, 'breathe', [HX0, HY0, 0, HX1, HY1, HZ])
