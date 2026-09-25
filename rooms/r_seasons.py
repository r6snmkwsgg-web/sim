"""The Gallery of Seasons: a vaulted corridor with four great arches off it, and through each arch a
bay of the library in its own season: snow, autumn, blossom, high summer. At the east end the last
arch is bricked up with a bookcase. It is not a bookcase."""
from kit_h6 import *

W, D = 32.0, 16.0
CY0, CY1 = 5.2, 10.8            # the corridor
CJ, CR = 4.6, 2.2               # its vault: springing, rise
BN = (11.4, D - T)              # north bays
BS = (T, 4.6)                   # south bays
BW = 3.2                        # half-width of a bay
AW, AJ = 5.0, 3.8               # the bay arches: width, springing
BH = 7.4                        # bay ceilings (open sky)
FIFTH = (27.9, 11.4, 31.3, 15.3)


def make():
    R = Room('seasons', 2, 1, res=2048)
    hall(R, y0=CY0, y1=CY1, h=CJ, wall='tile', floor='terrazzo', ceil='plaster')
    pr = arch_profile(8, CY1 - CY0, 0, CJ, 24, rise=CR)
    R.cut(prism([(p + 0, q) for p, q in arch_profile((CY0 + CY1) / 2, CY1 - CY0, 0, CJ, 24, rise=CR)], 'x', T - 0.02, W - T + 0.02,
                ['terrazzo'] + ['plaster'] * (len(pr) - 1), cap='plaster'))
    rs = rng(49)
    # transverse ribs and lanterns down the corridor
    for k in range(9):
        x = 0.35 + 2.0 + k * 3.41
        R.nocol.add(prism(arc_band((CY0 + CY1) / 2, CY1 - CY0, CJ, CR, 0.0, 0.25, 18), 'x', x - 0.15, x + 0.15, 'tile', cap='tile'))
    for x in (4.0, 12.0, 16.0, 20.0, 28.0):
        lantern_hung(R, x, 8.0, 4.4, CJ + CR - 0.05)
    # a runner down the middle
    R.nocol.add(box(1.6, 7.0, 0, W - 1.6, 9.0, 0.012, 'carpet', skip=('-z',)))
    R.nocol.add(box(1.5, 6.9, 0, W - 1.5, 9.1, 0.008, 'gilt', skip=('-z',)))
    # the four bays
    bays = (('winter', 8.0, BN), ('autumn', 24.0, BN), ('spring', 8.0, BS), ('summer', 24.0, BS))
    for (name, cx, (y0, y1)) in bays:
        R.cut(box(cx - BW, y0, 0, cx + BW, y1, BH, 'tile', bottom='terrazzo', top='plaster'))
        R.light(box(cx - BW, y0, BH - 0.06, cx + BW, y1, BH - 0.04, 'e_skydome'))
        yw0, yw1 = (CY1 - 0.1, y0 + 0.1) if y0 > 8 else (y1 - 0.1, CY0 + 0.1)
        arch_hole(R, 'y', cx, min(yw0, yw1), max(yw0, yw1), AW, AJ, floor='terrazzo', wall='tile', segs=18)
        arch_frame(R, cx, CY1 if y0 > 8 else CY0, 1 if y0 > 8 else -1)
    winter(R, rng(1)); autumn(R, rng(2)); spring(R, rng(3)); summer(R, rng(4))
    corridor(R, rs)
    fifth(R, rng(5))
    fx(R, 'snow', [8 - BW, BN[0], 0, 8 + BW, BN[1], BH])
    fx(R, 'dust', [24 - BW, BN[0], 0.2, 24 + BW, BN[1], 5.0])
    fx(R, 'dust', [8 - BW, BS[0], 0.2, 8 + BW, BS[1], 5.0])
    fx(R, 'fog', [24 - BW, BS[0], 0, 24 + BW, BS[1], BH], density=0.04)
    fx(R, 'dust', [FIFTH[0], FIFTH[1], 0.2, FIFTH[2], FIFTH[3], 4.2])
    # walking graph
    c = navloop(R, [(1.8, 8.0), (8.0, 8.0), (16.0, 8.0), (24.0, 8.0), (30.2, 8.0)], close=False)
    for (cx, y) in ((8.0, 13.4), (24.0, 13.4), (8.0, 2.6), (24.0, 2.6)):
        a = R.navpt(cx, y); R.link(a, c[1] if cx < 16 else c[3])
    return finish(R, 'The Gallery of Seasons', weight=4, probe=(16, 8, 2.4),
                  blurb='Four arches off a long corridor, and through each one the library is having a different time of year. The corridor itself has no weather at all.')


def arch_frame(R, cx, yw, s):
    """A moulded stone surround on the corridor face of a bay arch, and bookcases flanking it."""
    pr = arc_band(cx, AW + 0.5, AJ, AW / 2 + 0.25, 0.0, 0.25, 18)
    y0, y1 = (yw - 0.12, yw) if s > 0 else (yw, yw + 0.12)
    R.nocol.add(prism(pr, 'y', y0, y1, 'tile', cap='tile'))
    for x in (cx - AW / 2 - 0.25, cx + AW / 2):
        R.parts.add(box(x, y0, 0, x + 0.25, y1, AJ, 'tile', skip=('-z',)))


def lantern_hung(R, x, y, z, top):
    R.nocol.add(cyl(x, y, z + 0.45, top, 0.012, 6, side='brass', caps=False))
    R.light(box(x - 0.13, y - 0.13, z, x + 0.13, y + 0.13, z + 0.38, 'e_lamp'))
    R.nocol.add(box(x - 0.17, y - 0.17, z + 0.38, x + 0.17, y + 0.17, z + 0.46, 'brass'))
    R.nocol.add(box(x - 0.17, y - 0.17, z - 0.06, x + 0.17, y + 0.17, z, 'brass'))
    for (px, py) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        R.nocol.add(box(x + px * 0.15 - 0.015, y + py * 0.15 - 0.015, z, x + px * 0.15 + 0.015, y + py * 0.15 + 0.015, z + 0.38, 'brass', skip=('-z', '+z')))


def corridor(R, rs):
    """Bookcases between the arches, a green lamp on a pedestal at each pier, benches facing the bays."""
    rows = 9
    for (a, b) in ((11.6, 20.4),):
        sh(R, '-y', CY1, a, b, rows=rows, frame='walnut')
        sh(R, '+y', CY0, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, 4.4),):
        sh(R, '+y', CY0, a, b, rows=rows, frame='walnut')
    sh(R, '+y', CY0, 27.6, W - 0.6, rows=rows, frame='walnut')
    # the west end's blind arch (a real bookcase) and the east end's (a false one)
    for (cx, solid) in ((2.5, True), (29.6, False)):
        arch_hole(R, 'y', cx, CY1 - 0.1, BN[0] + 0.05, 2.7, 2.55, floor='terrazzo', wall='tile', segs=14)
        R.shelf(cx + 1.2, BN[0] - 0.02, 0, 2.4, '-y', rows=5, frame='walnut', solid=solid)
        # the tympanum over the bookcase, painted with a sun and moon
        pr = arch_profile(cx, 2.7, 2.3, 0.25, 14)
        R.parts.add(prism(pr, 'y', BN[0] - 0.4, BN[0] - 0.05, 'plaster', cap='plaster'))
        R.nocol.add(prism(arch_profile(cx, 0.5, 2.8, 0.05, 10), 'y', BN[0] - 0.43, BN[0] - 0.4, 'gilt', cap='gilt'))
        arch_frame_small(R, cx, CY1)
    for x in (4.9, 11.3, 20.7, 27.1):
        for (y, s) in ((CY1 - 0.35, 1), (CY0 + 0.35, -1)):
            R.parts.add(box(x - 0.25, y - 0.25, 0, x + 0.25, y + 0.25, 1.0, 'tile'))
            green_lamp(R, x, y, 1.0)
    for (x, y, a) in ((16.0, 9.3, -math.pi / 2), (16.0, 6.7, math.pi / 2)):
        R.parts.add(box(-0.9, -0.22, 0, 0.9, 0.22, 0.45, 'walnut', skip=('-z',)).xform(0, x, y, 0))
        R.spot('sit', x, y, 0.45, a)


def arch_frame_small(R, cx, yw):
    pr = arc_band(cx, 3.1, 2.55, 1.55, 0.0, 0.2, 14)
    R.nocol.add(prism(pr, 'y', yw - 0.1, yw, 'tile', cap='tile'))


def green_lamp(R, x, y, z, m='e_lamp'):
    R.nocol.add(cyl(x, y, z, z + 0.03, 0.08, 8, side='brass', top='brass'))
    R.nocol.add(box(x - 0.01, y - 0.01, z + 0.03, x + 0.01, y + 0.01, z + 0.4, 'brass'))
    R.nocol.add(cyl(x, y, z + 0.4, z + 0.52, 0.17, 10, side='green', top='green', bottom='green'))
    R.light(cyl(x, y, z + 0.385, z + 0.4, 0.14, 10, side=m, top=m, bottom=m))


def bay_cases(R, cx, y0, y1, north, rows=12, frame='walnut', snow=False):
    """Tall bookcases down both side walls of a bay."""
    ya, yb = (y0 + 0.4, y1 - 0.1) if north else (y0 + 0.1, y1 - 0.4)
    sh(R, '+x', cx - BW, ya, yb, rows=rows, frame=frame)
    sh(R, '-x', cx + BW, ya, yb, rows=rows, frame=frame)
    for x in (cx - BW, cx + BW - 0.4):
        if snow: blanket(R, x, ya, x + 0.4, yb, rows * 0.42 + 0.18, t=0.1, m='snow')
    # the back wall either side of the doorway
    bk = y1 if north else y0
    f = '-y' if north else '+y'
    sh(R, f, bk, cx - BW + 0.4, cx - 1.8, rows=rows, frame=frame)
    sh(R, f, bk, cx + 1.8, cx + BW - 0.4, rows=rows, frame=frame)
    sh(R, f, bk, cx - 1.8, cx + 1.8, z=4.25, rows=rows - 10, frame=frame)
    return rows


def winter(R, rs):
    cx, (y0, y1) = 8.0, BN
    bay_cases(R, cx, y0, y1, True, snow=True)
    # drifts: deep against the walls, thin in the middle, clear round the doorway
    def fn(x, y):
        z = 0.04 + 0.03 * math.sin(x * 2.3 + y * 1.7)
        for wd in (x - (cx - BW + 0.34), (cx + BW - 0.34) - x):
            if wd < 1.2: z = max(z, 0.38 * smooth_bump(wd, 1.2))
        z = max(z, 0.3 * smooth_bump(math.hypot(x - (cx - 1.9), y - 12.9), 0.9))
        f = min(1.0, max(0.0, (y - y0) / 0.8))
        return 0.005 + (z - 0.005) * f
    R.parts.add(field(fn, cx - BW + 0.34, y0, cx + BW - 0.34, y1 - 0.02, 26, 17, m='snow', floor=-1))
    tree(R, cx - 1.9, 12.9, 5.2, 2.0, rs, bark='walnut', snow=True, bare=True, z=0.25)
    # a reading table and two chairs left out in the snow
    R.parts.add(table(cx + 0.9, 12.3, cx + 2.2, 13.3, 0.76, 'walnut'))
    blanket(R, cx + 0.88, 12.28, cx + 2.22, 13.32, 0.76, t=0.06, m='snow')
    for (x, y, a) in ((cx + 1.55, 11.95, math.pi / 2 + 0.3), (cx + 2.55, 12.8, math.pi + 0.2)):
        R.parts.add(chair(x, y, a))
        blanket(R, x - 0.22, y - 0.22, x + 0.22, y + 0.22, 0.48, t=0.05, m='snow')
    for (x0, y0_, x1, y1_) in ((5.6, 9.6, 10.4, 11.4), (6.2, 9.0, 9.6, 9.7), (7.0, 8.6, 8.9, 9.1)):
        R.nocol.add(box(x0, y0_, 0, x1, y1_, 0.02, 'snow', skip=('-z',)))
    R.light(sphere(cx + 1.3, 12.8, 1.0, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(box(cx + 1.26, 12.76, 0.76, cx + 1.34, 12.84, 0.95, 'brass'))
    book_pile(R, cx + 1.8, 12.9, 0.76, n=4, seed=11, col=False)
    blanket(R, cx + 1.65, 12.75, cx + 1.95, 13.05, 0.95, t=0.03, m='snow')


def autumn(R, rs):
    cx, (y0, y1) = 24.0, BN
    bay_cases(R, cx, y0, y1, True, frame='oak')
    R.nocol.add(box(cx - BW + 0.34, y0 + 0.2, 0, cx + BW - 0.34, y1 - 0.1, 0.015, 'leather', skip=('-z',)))
    tree(R, cx + 1.9, 13.0, 5.6, 2.2, rs, bark='walnut', leaf=('rust', 'amberleaf', 'rust'), n=7, puff=1.1)
    litter(R, cx - BW + 0.35, y0 + 0.1, cx + BW - 0.35, y1 - 0.1, 650, rs, ('rust', 'amberleaf', 'rust', 'oxblood'), z=0.015, s=(0.05, 0.1))
    litter(R, cx - 4.0, CY1 - 2.0, cx + 4.0, CY1, 90, rs, ('rust', 'amberleaf'))
    # a heap of raked leaves, a rake against the case, an armchair
    R.nocol.add(puffs(cx - 1.9, 13.4, 0.0, 0.8, 4, 'rust', seed=21, flat=0.5, segs=8, rings=4))
    R.col.add(box(cx - 2.5, 12.8, 0, cx - 1.3, 14.0, 0.35, 'tile'))
    R.nocol.add(beam((cx - BW + 0.45, 12.0, 0.0), (cx - BW + 0.4, 12.2, 1.6), 0.04, 'oak'))
    R.nocol.add(box(cx - BW + 0.37, 11.95, 1.55, cx - BW + 0.47, 12.45, 1.62, 'iron'))
    armchair(R, cx - 1.6, 11.9 + 0.1, math.pi / 2 - 0.3, m='oxblood')
    R.light(sphere(cx + 0.2, 12.0, 1.2, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(cyl(cx + 0.2, 12.0, 0, 1.15, 0.02, 6, side='brass', caps=False))
    R.col.add(box(cx + 0.15, 11.95, 0, cx + 0.25, 12.05, 1.2, 'tile'))


def spring(R, rs):
    cx, (y0, y1) = 8.0, BS
    bay_cases(R, cx, y0, y1, False, frame='oak')
    # grass underfoot, blossom trees, petals everywhere
    R.nocol.add(box(cx - BW + 0.34, y0 + 0.2, 0, cx + BW - 0.34, y1 - 0.1, 0.02, 'leafg', skip=('-z',)))
    for (x, y, h) in ((cx - 1.9, 2.8, 4.8), (cx + 2.0, 3.0, 4.2)):
        tree(R, x, y, h, 1.8, rs, bark='walnut', leaf=('blossom', 'blossom', 'ivory'), n=6, puff=0.95)
    litter(R, cx - BW + 0.35, y0 + 0.2, cx + BW - 0.35, y1, 600, rs, ('blossom', 'ivory'), z=0.02, s=(0.025, 0.05))
    litter(R, cx - 4.0, CY0, cx + 4.0, CY0 + 2.2, 120, rs, ('blossom',), s=(0.02, 0.04))
    R.parts.add(box(-0.9, -0.22, 0, 0.9, 0.22, 0.45, 'walnut', skip=('-z',)).xform(0, cx, 3.9, 0))
    R.spot('sit', cx, 3.9, 0.45, math.pi / 2)
    open_book(R, cx + 0.4, 3.9, 0.45, 0.2)
    litter(R, cx - 0.8, 3.75, cx + 0.8, 4.05, 14, rs, ('blossom',), z=0.45, s=(0.02, 0.04))


def summer(R, rs):
    cx, (y0, y1) = 24.0, BS
    bay_cases(R, cx, y0, y1, False, frame='oak')
    R.nocol.add(box(cx - BW + 0.34, y0 + 0.2, 0, cx + BW - 0.34, y1 - 0.1, 0.03, 'leafg', skip=('-z',)))
    tree(R, cx - 2.0, 2.9, 5.8, 2.4, rs, bark='walnut', leaf=('leafg', 'green'), n=7, puff=1.2)
    # long grass tufts, a deckchair in the sun, a jug on a stool
    g = Geo()
    for _ in range(320):
        x, y = rs.uniform(cx - BW + 0.4, cx + BW - 0.4), rs.uniform(y0 + 0.3, y1 - 0.2)
        if abs(x - cx) < 1.8 and y < y0 + 2.2: continue
        h = rs.uniform(0.2, 0.6); a = rs.uniform(0, math.pi)
        g.add(blade(x, y, 0.02, h, 0.1, a, rs.choice(('leafg', 'amberleaf', 'green')), lean=rs.uniform(-0.08, 0.08)))
    R.nocol.add(g)
    R.parts.add(slope_box(-0.35, 0.35, -0.28, 0.28, 0.25, 0.25, 0.32, 0.32, 'oak').xform(0.4, cx + 1.4, 3.5, 0))
    R.nocol.add(beam((cx + 1.4 - 0.2, 3.5 + 0.3, 0.3), (cx + 1.4 - 0.5, 3.5 + 0.55, 1.0), 0.5, 'damask', 0.03))
    R.nocol.add(box(cx + 1.0, 3.2, 0, cx + 1.8, 3.8, 0.28, 'oak'))
    R.spot('sit', cx + 1.4, 3.5, 0.32, math.pi / 2 + 0.4)
    R.parts.add(stool(cx + 2.4, 3.9, 0, back=False))
    R.nocol.add(cyl(cx + 2.4, 3.9, 0.47, 0.72, 0.07, 10, side='ivory', top='ivory'))
    book_pile(R, cx + 0.7, 3.6, 0.03, n=3, seed=7, col=False)


def fifth(R, rs):
    """Behind the last arch: a bay where it is some other season, one with no name. The tree is paper,
    its leaves are pages, and they are falling."""
    x0, y0, x1, y1 = FIFTH
    R.cut(box(x0, y0, 0, x1, y1, 4.4, 'plaster', bottom='floor', top='plaster'))
    R.light(box(x0 + 0.3, y0 + 0.3, 4.34, x1 - 0.3, y1 - 0.3, 4.36, 'e_skydome'))
    cx, cy = (x0 + x1) / 2 + 0.3, (y0 + y1) / 2 + 0.6
    # a trunk of stacked books, a crown of pages
    zz = 0.0
    for k in range(16):
        w = 0.42 - k * 0.012
        R.parts.add(box(-w / 2, -w * 0.36, 0, w / 2, w * 0.36, 0.14, rs.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet')), skip=('-z',)).xform(rs.uniform(0, 3.14), cx, cy, zz))
        zz += 0.14
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        end = (cx + math.cos(a) * 1.2, cy + math.sin(a) * 0.9, zz + 0.6 + rs.uniform(0, 0.5))
        R.nocol.add(tube(curve((cx, cy, zz - 0.2), end, (0, 0, 0.25), 4), [0.07, 0.05, 0.04, 0.03], 5, 'leather'))
        R.nocol.add(puffs(end[0], end[1], end[2], 0.6, 3, 'newsprint', seed=100 + k, flat=0.55, segs=8, rings=4))
    litter(R, x0 + 0.2, y0 + 0.2, x1 - 0.2, y1 - 0.2, 170, rs, ('newsprint', 'ivory'), s=(0.09, 0.15))
    # pages caught in the air
    for _ in range(40):
        x, y, z = rs.uniform(x0 + 0.4, x1 - 0.4), rs.uniform(y0 + 0.4, y1 - 0.4), rs.uniform(0.6, 3.4)
        p = blade(0, 0, -0.07, 0.14, 0.2, 0.0, 'newsprint')
        rot(p, 'x', rs.uniform(-1.2, 1.2) + 1.57); rot(p, 'y', rs.uniform(-1.2, 1.2))
        R.nocol.add(p.xform(rs.uniform(0, 6.28), x, y, z))
    sh(R, '+x', x0, y0 + 0.3, y1 - 0.9, rows=9, frame='walnut')
    sh(R, '-x', x1, y0 + 0.3, y1 - 0.9, rows=9, frame='walnut')
    sh(R, '-y', y1, x0 + 2.1, x1 - 0.1, rows=9, frame='walnut')
    R.parts.add(box(x0 + 0.3, y1 - 0.75, 0, x0 + 1.9, y1 - 0.3, 0.45, 'walnut', skip=('-z',)))
    R.spot('sit', x0 + 1.1, y1 - 0.55, 0.45, -math.pi / 2)
    R.light(sphere(x1 - 0.5, y1 - 0.5, 1.1, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(box(x1 - 0.54, y1 - 0.54, 0, x1 - 0.46, y1 - 0.46, 1.05, 'brass'))
    secret(R, cx - 0.6, cy - 1.2, 0.0, 'The Fifth Season',
           'Behind the last arch it is a season nobody has named. The tree is made of books and it is dropping its pages, one at a time, and none of them lands.')
