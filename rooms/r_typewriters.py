"""The Typing Pool: a plain of typewriters on desks in ranks to the walls, under three long vaults on
piers, a page in every machine and every page begun. In the east wall one bookcase is not a bookcase:
behind it, an alcove with one typewriter and one page, finished."""
from kit_h6 import *

W = D = 32.0
X1 = 29.2                    # the hall's east wall; the alcove is in the thickness behind it
VJ = 4.3                     # the vaults' springing height
VX = (T, 10.4, 21.6, X1)     # the vaults' edges: piers stand under the two valleys
AL = (29.2, 14.4, 31.45, 17.6)   # the secret alcove (x0, y0, x1, y1)
PIERS_X = None


def vaults():
    return [((a + b) / 2, b - a, min(3.1, (b - a) * 0.28)) for a, b in zip(VX, VX[1:])]


def make():
    R = Room('typewriters', 2, 2, res=2048)
    hall(R, x1=X1, h=VJ, wall='tile', floor='slate', ceil='plaster')
    vs = vaults()
    for (c, w, VR) in vs:
        pr = arch_profile(c, w + 0.04, 0, VJ, 28, rise=VR)
        R.cut(prism(pr, 'y', T - 0.02, D - T + 0.02, ['slate'] + ['plaster'] * (len(pr) - 1), cap='plaster'))
    # piers and an entablature under the two valleys between the vaults
    px = list(VX[1:3])
    for x in px:
        R.parts.add(box(x - 0.35, T, VJ - 0.45, x + 0.35, D - T, VJ + 0.25, 'tile'))
        for k in range(8):
            y = 2.0 + k * 4.0
            pier(R, x, y, 0, VJ - 0.45, s=0.6)
    # transverse ribs in every vault over each pier
    for (c, w, VR) in vs:
        for k in range(8):
            y = 2.0 + k * 4.0
            R.nocol.add(prism(arc_band(c, w, VJ, VR, 0.0, 0.32, 20), 'y', y - 0.2, y + 0.2, 'tile', cap='tile'))
    walls(R)
    pool(R, px)
    alcove(R)
    lamps(R, vs)
    fx(R, 'dust', [T, T, 0.5, X1, D - T, 5.5])
    # the walking graph: the four door aisles and the cross aisles
    g = {}
    for x in (8.0, 16.0, 24.0):
        for y in (2.2, 8.0, 16.0, 24.0, 29.8):
            g[(x, y)] = R.navpt(x, y)
    for x in (8.0, 16.0, 24.0):
        R.link(*[g[(x, y)] for y in (2.2, 8.0, 16.0, 24.0, 29.8)])
    for y in (8.0, 16.0, 24.0):
        R.link(g[(8.0, y)], g[(16.0, y)], g[(24.0, y)])
    a, b = R.navpt(2.0, 8.0), R.navpt(2.0, 24.0)
    R.link(a, g[(8.0, 8.0)]); R.link(b, g[(8.0, 24.0)])
    a, b = R.navpt(27.6, 8.0), R.navpt(27.6, 24.0)
    R.link(a, g[(24.0, 8.0)]); R.link(b, g[(24.0, 24.0)])
    return finish(R, 'The Typing Pool', weight=4, probe=(16, 16, 2.4),
                  blurb='Hundreds of typewriters on hundreds of desks, a sheet wound into every one. Each page has a few lines on it, and each stops mid-word.')


def walls(R):
    rows = 10
    for (a, b) in ((0.7, 6.3), (9.7, 22.3), (25.7, D - 0.7)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.7, 6.3), (9.7, AL[1] - 0.1), (AL[3] + 0.1, 22.3), (25.7, D - 0.7)):
        sh(R, '-x', X1, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.7, 6.3), (9.7, 22.3), (25.7, X1 - 0.5)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
    # over each doorway, a short case
    for x in (8.0, 24.0):
        sh(R, '+y', T, x - 1.7, x + 1.7, z=4.25, rows=0 + 1, frame='walnut')
        sh(R, '-y', D - T, x - 1.7, x + 1.7, z=4.25, rows=1, frame='walnut')


def columns(px):
    """Desk centres across the room: each block between aisles, piers and walls filled evenly."""
    stops = sorted([(0.0, 1.35)] + [(a - 1.3, a + 1.3) for a in (8.0, 16.0, 24.0)] + [(a - 0.45, a + 0.45) for a in px] + [(X1 - 1.05, 99.0)])
    xs = []
    for (a, b), (c, d) in zip(stops, stops[1:]):
        L = c - b
        n = int((L + 0.25) / 1.3)
        for k in range(n):
            xs.append(b + (L - n * 1.3 + 0.25) / 2 + 0.525 + k * 1.3)
    return xs


def rows_y():
    ys = []
    for (a, b) in ((1.4, 6.7), (9.3, 14.7), (17.3, 22.7), (25.3, D - 1.3)):
        n = int((b - a + 0.6) / 2.0)
        ys += [a + (b - a - (n - 1) * 2.0) / 2 + k * 2.0 for k in range(n)]
    return ys


def pool(R, px):
    """The desks: ranks facing north, a typewriter on each, a chair pushed back from most."""
    rs = rng(57)
    k = 0
    for y in rows_y():
        for x in columns(px):
            k += 1
            a = math.pi / 2
            R.parts.add(desk(x, y, a, w=1.05, d=0.62))
            tw = typewriter(x + rs.uniform(-0.06, 0.06), y + 0.02, a + rs.uniform(-0.06, 0.06), 0.76)
            R.nocol.add(tw)
            R.col.add(box(x - 0.3, y - 0.2, 0.76, x + 0.3, y + 0.2, 1.0, 'tile'))
            if rs.random() < 0.9:
                c = stool(x + rs.uniform(-0.08, 0.08), y - 0.62 - rs.uniform(0, 0.12), a + rs.uniform(-0.25, 0.25))
                R.parts.add(c)
            if k % 5 == 2:
                R.nocol.add(sheet(x + 0.35, y + 0.1, 0.76, rs.uniform(-0.3, 0.3)))
            if k % 4 == 1:
                green_lamp(R, x - 0.4, y + 0.15, 0.76)
            elif rs.random() < 0.2:
                book_pile(R, x - 0.38, y + 0.12, 0.76, n=rs.randint(2, 5), seed=k, col=False)


def green_lamp(R, x, y, z, m='e_lamp'):
    R.nocol.add(cyl(x, y, z, z + 0.03, 0.07, 8, side='brass', top='brass', caps=True))
    R.nocol.add(box(x - 0.008, y - 0.008, z + 0.03, x + 0.008, y + 0.008, z + 0.34, 'brass'))
    R.nocol.add(obox(x - 0.15, y, x + 0.15, y, z + 0.34, z + 0.42, 0.12, 'green'))
    R.light(obox(x - 0.13, y, x + 0.13, y, z + 0.325, z + 0.34, 0.08, m))


def lamps(R, vs):
    for (c, w, VR) in vs:
        for k in range(4):
            y = 4.0 + k * 8.0
            pendant(R, c, y, 3.7, VJ + VR - 0.05, r=0.24)
    # a few night lamps at the doors
    for (x, y) in ((8.0 - 2.0, 1.2), (24.0 + 2.0, 1.2), (8.0 + 2.0, D - 1.2), (24.0 - 2.0, D - 1.2)):
        R.light(sphere(x, y, 2.6, 0.08, 8, 4, 'e_amber'))
        R.nocol.add(box(x - 0.05, y - 0.05, 2.35, x + 0.05, y + 0.05, 2.52, 'brass'))


def alcove(R):
    """Behind a false bookcase in the east wall: one typewriter, one lamp, one finished page."""
    x0, y0, x1, y1 = AL
    R.cut(box(x0 - 0.05, y0, 0, x1, y1, 2.7, 'damask', bottom='floor', top='plaster'))
    R.shelf(X1, y0 + 0.1, 0, (y1 - y0) - 0.2, '-x', rows=10, frame='walnut', solid=False)
    cx, cy = (x0 + x1) / 2 + 0.35, (y0 + y1) / 2
    R.parts.add(desk(cx + 0.2, cy, 0.0, w=1.1, d=0.62))
    R.nocol.add(typewriter(cx + 0.22, cy, 0.0, 0.76, page=False))
    # the page, wound in and typed to the bottom
    p = box(-0.005, -0.105, 0.2, 0.0, 0.105, 0.56, 'ivory')
    rot(p, 'y', 0.22, 0, 0, 0.24)
    R.nocol.add(p.xform(0, cx + 0.22 + 0.11, cy, 0.76))
    R.parts.add(stool(cx - 0.45, cy, 0.0))
    R.light(sphere(cx + 0.3, y1 - 0.25, 1.4, 0.06, 8, 4, 'e_amber'))
    R.nocol.add(box(cx + 0.28, y1 - 0.27, 0.76, cx + 0.32, y1 - 0.23, 1.35, 'brass'))
    bulb(R, cx, cy, 2.1, r=0.08, m='e_dim', top=2.7)
    R.spot('plaque', cx + 0.2, cy, 0.76, 0.0,
           text='I have typed it at last, every letter in its place: the book of my life, as it was, without a single error. '
                'It is one page long. I have left it in the machine for you. Do not correct anything.')
    secret(R, cx - 0.2, cy, 0.0, 'The Last Page',
           'Behind the shelves, one typewriter with one page in it, typed all the way to the bottom. Somebody finished.')
