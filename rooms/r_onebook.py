"""One Book: a two-storey hall with a single open book in it, twenty metres from head to foot. Its
pages are hills of paper you can walk over, lines of print running across them like furrows; the
edges curl up like a lip. A ladder leans on one fore-edge and a torn flap of page makes a ramp down to
the floor on the other side. A gallery runs round the walls at the upper floor. Where the pages part
at the left-hand fore-edge there is a low gap you can crawl into."""
from lib import *
from kit_h2 import *

XA, XB = 4.5, 27.5          # the text block's fore-edges (west, east)
XS = 16.0                   # the spine
YA, YB = 6.0, 26.0          # head and foot (south, north)
CB = 0.5                    # the covers stand out this far
GW = 2.2                    # gallery width
GZ = LH
CAVE = dict(px=(XA - 0.35, 8.6), py=(11.2, 12.4), cx=(7.4, 11.8), cy=(12.4, 17.2), z0=0.35, z1=1.68)
LADY = 18.0                 # where the ladder leans (east fore-edge)
FLAP = (10.6, 13.8)         # the torn flap on the south edge of the left page (x range)


def cr(pts, u):
    """Catmull-Rom through [(u, z), ...]."""
    if u <= pts[0][0]: return pts[0][1]
    if u >= pts[-1][0]: return pts[-1][1]
    for i in range(len(pts) - 1):
        if pts[i][0] <= u <= pts[i + 1][0]: break
    p0 = pts[max(0, i - 1)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(len(pts) - 1, i + 2)]
    t = (u - p1[0]) / (p2[0] - p1[0])
    m1 = (p2[1] - p0[1]) / (p2[0] - p0[0]) * (p2[0] - p1[0])
    m2 = (p3[1] - p1[1]) / (p3[0] - p1[0]) * (p2[0] - p1[0])
    t2, t3 = t * t, t * t * t
    return (2 * t3 - 3 * t2 + 1) * p1[1] + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2[1] + (t3 - t2) * m2


PROF = [(0.0, 1.5), (0.06, 2.3), (0.16, 3.4), (0.3, 4.1), (0.5, 4.0), (0.75, 3.55), (1.0, 3.05)]


def base_z(x, y):
    u = abs(x - XS) / (XS - XA if x < XS else XB - XS)
    z = cr(PROF, u)
    # the corners lift a little at head and foot
    v = min(y - YA, YB - y)
    if v < 2.5: z += 0.25 * (1 - v / 2.5) ** 2 * u
    return z


def lip(x, y):
    """The curl at the page edges: a raised rim 0.9 m high over the last 0.45 m (a parapet),
    except at the ladder and the torn flap, and not at the spine."""
    d_fore = min(x - XA, XB - x)
    d_head = min(y - YA, YB - y)
    near_spine = abs(x - XS) < 1.2
    h = 0.0
    if d_fore < 0.45:
        if not (x > XS and abs(y - LADY) < 0.75):
            h = max(h, 0.9 * (1 - d_fore / 0.45) ** 0.6)
    if d_head < 0.45 and not near_spine:
        if not (y < 10 and FLAP[0] - 0.05 < x < FLAP[1] + 0.05):
            h = max(h, 0.9 * (1 - d_head / 0.45) ** 0.6)
    return h


def page_z(x, y):
    return base_z(x, y) + lip(x, y)


def grid_x():
    xs = []
    for (a, b, n) in ((XA - 0.1, XA, 1), (XA, XA + 0.45, 3), (XA + 0.45, XS - 1.3, 16), (XS - 1.3, XS, 5),
                      (XS, XS + 1.3, 5), (XS + 1.3, XB - 0.45, 16), (XB - 0.45, XB, 3), (XB, XB + 0.1, 1)):
        for k in range(n): xs.append(a + (b - a) * k / n)
    xs.append(XB + 0.1)
    return xs


def grid_y():
    ys = []
    for (a, b, n) in ((YA - 0.1, YA, 1), (YA, YA + 0.45, 3), (YA + 0.45, YB - 0.45, 20), (YB - 0.45, YB, 3), (YB, YB + 0.1, 1)):
        for k in range(n): ys.append(a + (b - a) * k / n)
    ys.append(YB + 0.1)
    # extra lines at the flap and the ladder so the lip opens cleanly
    for v in (LADY - 0.75, LADY + 0.75):
        ys.append(v)
    return sorted(set(round(v, 4) for v in ys))


def hf_cutter(xs, ys, zf, ztop, m='ivory', side='ivory'):
    """A closed solid over a height field: bottom z = zf(x, y) on the grid, top flat at ztop."""
    g = Geo()
    nx, ny = len(xs), len(ys)
    B = [[g.vert((xs[i], ys[j], zf(xs[i], ys[j]))) for j in range(ny)] for i in range(nx)]
    Tp = [[None] * ny for _ in range(nx)]
    for i in (0, nx - 1):
        for j in range(ny): Tp[i][j] = g.vert((xs[i], ys[j], ztop))
    for j in (0, ny - 1):
        for i in range(nx):
            if Tp[i][j] is None: Tp[i][j] = g.vert((xs[i], ys[j], ztop))
    # bottom (the page): faces pointing down (outward of the cutter)
    for i in range(nx - 1):
        for j in range(ny - 1):
            q = [B[i][j], B[i][j + 1], B[i + 1][j + 1], B[i + 1][j]]
            g.face(q, m, [(xs[i], ys[j]), (xs[i], ys[j + 1]), (xs[i + 1], ys[j + 1]), (xs[i + 1], ys[j])])
    # sides
    ring_ = [(i, 0) for i in range(nx)] + [(nx - 1, j) for j in range(1, ny)] + [(i, ny - 1) for i in range(nx - 2, -1, -1)] + [(0, j) for j in range(ny - 2, 0, -1)]
    for k in range(len(ring_)):
        a, b = ring_[k], ring_[(k + 1) % len(ring_)]
        g.face([B[a[0]][a[1]], B[b[0]][b[1]], Tp[b[0]][b[1]], Tp[a[0]][a[1]]], side, [(0, 0), (1, 0), (1, 1), (0, 1)])
    g.face([Tp[a[0]][a[1]] for a in ring_], side, [(xs[a[0]], ys[a[1]]) for a in ring_])
    return g.fix()


def make():
    R = Room('onebook', 2, 2, levels=2, res=2048)
    W, D = R.W, R.D
    R.sockets(floor='floor', wall='tile')
    HT = R.hi - 0.25
    # the hall round the book, and thin cutters that give the text block its paper edges
    e = 0.3
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, W - T + 0.02, YA - e + 0.15), (T - 0.02, YB + e - 0.15, W - T + 0.02, D - T + 0.02),
                             (T - 0.02, T - 0.02, XA - e + 0.15, D - T + 0.02), (XB + e - 0.15, T - 0.02, W - T + 0.02, D - T + 0.02)):
        R.cut(box(x0, y0, 0, x1, y1, HT, 'tile', bottom='floor', top='plaster'))
    for (x0, y0, x1, y1) in ((XA - e, YA - e, XB + e, YA), (XA - e, YB, XB + e, YB + e), (XA - e, YA - e, XA, YB + e), (XB, YA - e, XB + e, YB + e)):
        R.cut(box(x0, y0, 0, x1, y1, HT, 'bed', bottom='floor', top='plaster'))
    # over the pages
    R.cut(hf_cutter(grid_x(), grid_y(), page_z, HT, m='ivory', side='plaster'))
    book(R)
    cave(R)
    gallery(R, W, D, HT)
    hall(R, W, D, HT)
    R.spot('probe', 16.0, 3.0, 3.0)
    R.meta.update(label='One Book', weight=3,
                  blurb='There is one book in this hall, lying open. You could walk across it. People do; there are footprints in the margins.')
    R.meta['box'] = [[T, 0, T], [W - T, HT, D - T]]
    return tidy(R)


def book(R):
    # the covers, standing out round the block, and the spine's headbands
    g = Geo()
    g.add(box(XA - CB, YA - CB, 0, XB + CB, YA, 0.35, 'leather', skip=('-z',)))
    g.add(box(XA - CB, YB, 0, XB + CB, YB + CB, 0.35, 'leather', skip=('-z',)))
    g.add(box(XA - CB, YA, 0, XA, YB, 0.35, 'leather', skip=('-z',)))
    g.add(box(XB, YA, 0, XB + CB, YB, 0.35, 'leather', skip=('-z',)))
    g.add(box(XA - CB, YA - CB, 0.35, XB + CB, YA - CB + 0.04, 0.4, 'gilt', skip=('-z',)))
    R.parts.add(weld(g))
    for y in (YA - 0.02, YB + 0.02):
        R.nocol.add(cyl(XS, y, 0.35, 1.5, 0.28, 10, side='velvet', top='gilt'))
    # a ribbon bookmark from the gutter over the head, down the edge and away across the floor
    rb = Geo()
    w = 0.35
    pts = [(XS + 0.25, YB - 3.0, base_z(XS + 0.25, YB - 3.0) + 0.02), (XS + 0.3, YB - 0.2, base_z(XS + 0.3, YB - 0.2) + 0.03),
           (XS + 0.35, YB + 0.05, 1.2), (XS + 0.4, YB + 0.2, 0.36), (XS + 0.6, YB + 0.6, 0.36), (XS + 1.0, YB + 1.2, 0.01), (XS + 2.6, YB + 3.2, 0.01)]
    for (a, b) in zip(pts, pts[1:]):
        rb.add(hexa([(a[0] - w / 2, a[1], a[2]), (a[0] + w / 2, a[1], a[2]), (b[0] + w / 2, b[1], b[2]), (b[0] - w / 2, b[1], b[2]),
                     (a[0] - w / 2, a[1], a[2] + 0.01), (a[0] + w / 2, a[1], a[2] + 0.01), (b[0] + w / 2, b[1], b[2] + 0.01), (b[0] - w / 2, b[1], b[2] + 0.01)], 'velvet'))
    R.nocol.add(weld(rb))
    # the lines of print: dark furrows following the paper, broken into words
    rnd = random.Random(11)
    tx = Geo()
    for (xa, xb) in ((XA + 1.0, XS - 1.3), (XS + 1.3, XB - 1.0)):
        y = YA + 1.6
        ln = 0
        while y < YB - 1.4:
            x = xa + (0.9 if ln == 0 and xa < XS else 0.0)
            end = xb - (rnd.random() * 3.5 if rnd.random() < 0.15 else 0.0)
            while x < end - 0.3:
                wl = min(end - x, 0.35 + rnd.random() * 1.3)
                n = max(1, int(wl / 0.5))
                word = Geo()
                for k in range(n):
                    x0 = x + wl * k / n; x1 = x + wl * (k + 1) / n
                    z0, z1 = base_z(x0, y) + 0.04, base_z(x1, y) + 0.04
                    word.add(hexa([(x0, y - 0.07, z0 - 0.01), (x1, y - 0.07, z1 - 0.01), (x1, y + 0.07, z1 - 0.01), (x0, y + 0.07, z0 - 0.01),
                                   (x0, y - 0.07, z0), (x1, y - 0.07, z1), (x1, y + 0.07, z1), (x0, y + 0.07, z0)], 'slate'))
                tx.add(weld(word))
                x += wl + 0.22 + rnd.random() * 0.1
            y += 0.52 if rnd.random() > 0.1 else 1.1
            ln += 1
    R.nocol.add(tx)
    # a red initial at the top of the left page
    ix0, iy1 = XA + 1.0, YB - 1.4
    for (x0, x1) in ((ix0, ix0 + 0.4), (ix0 + 0.4, ix0 + 0.8)):
        pass
    R.nocol.add(hexa([(ix0, iy1 - 1.4, base_z(ix0, iy1) + 0.003), (ix0 + 0.75, iy1 - 1.4, base_z(ix0 + 0.75, iy1) + 0.003),
                      (ix0 + 0.75, iy1, base_z(ix0 + 0.75, iy1) + 0.003), (ix0, iy1, base_z(ix0, iy1) + 0.003),
                      (ix0, iy1 - 1.4, base_z(ix0, iy1) + 0.02), (ix0 + 0.75, iy1 - 1.4, base_z(ix0 + 0.75, iy1) + 0.02),
                      (ix0 + 0.75, iy1, base_z(ix0 + 0.75, iy1) + 0.02), (ix0, iy1, base_z(ix0, iy1) + 0.02)], 'oxblood'))
    # the torn flap: a triangle of page folded down to the floor on the south side
    fx0, fx1 = FLAP
    ztop0, ztop1 = base_z(fx0, YA), base_z(fx1, YA)
    yfoot = YA - 5.2
    flap = hexa([(fx0, YA + 0.05, ztop0 - 0.12), (fx1, YA + 0.05, ztop1 - 0.12), (fx1 + 0.3, yfoot, -0.1), (fx0 - 0.3, yfoot, -0.1),
                 (fx0, YA + 0.05, ztop0), (fx1, YA + 0.05, ztop1), (fx1 + 0.3, yfoot, 0.02), (fx0 - 0.3, yfoot, 0.02)], 'ivory')
    R.parts.add(flap)
    # a few words on the flap too, upside down now
    for k in range(4):
        t = 0.2 + k * 0.17
        y = YA + (yfoot - YA) * t
        z = (1 - t) * (ztop0 + ztop1) / 2 + t * 0.02 + 0.012
        R.nocol.add(box(fx0 + 0.3, y - 0.08, z - 0.01, fx1 - 0.5 - (k % 2) * 0.8, y + 0.08, z, 'black'))
    # the ladder on the east fore-edge
    climb_ladder(R, XB + 0.05, LADY, 0.0, base_z(XB - 0.2, LADY), 0.0, run=1.4)
    # nav: over the pages
    a = R.navpt((fx0 + fx1) / 2, YA - 3.8, 0.0 + 0.9)
    b = R.navpt((fx0 + fx1) / 2, YA + 1.2, base_z((fx0 + fx1) / 2, YA + 1.2))
    c = R.navpt(9.0, 16.0, base_z(9.0, 16.0)); d = R.navpt(XS, 16.0, base_z(XS, 16.0))
    e = R.navpt(22.0, 16.0, base_z(22.0, 16.0)); f = R.navpt(XB - 1.0, LADY, base_z(XB - 1.0, LADY))
    R.link(b, c, d, e, f)
    NAV['flap'] = (a, b)
    NAV['lad'] = f


NAV = {}


def cave(R):
    """Where the pages part at the west fore-edge: a crawl between the leaves to a small hollow."""
    c = CAVE
    z0, z1 = c['z0'], c['z1']
    R.cut(box(c['px'][0], c['py'][0], z0, c['px'][1], c['py'][1], z1, 'ivory', bottom='ivory', top='ivory'))
    R.cut(box(c['cx'][0], c['cy'][0] - 0.05, z0, c['cx'][1], c['cy'][1], z1 + 0.25, 'ivory', bottom='ivory', top='ivory'))
    # the layers of the pages showing in the walls: thin darker lines
    g = Geo()
    for k in range(5):
        z = z0 + 0.3 + k * 0.28
        g.add(box(c['cx'][0], c['cy'][1] - 0.01, z, c['cx'][1], c['cy'][1], z + 0.012, 'plaster', skip=('+y',)))
    R.nocol.add(g)
    x0, x1, y0, y1 = c['cx'][0], c['cx'][1], c['cy'][0], c['cy'][1]
    # a bed of loose pages, a candle, a pressed flower, a small lamp, a book (an ordinary one)
    R.parts.add(box(x1 - 1.9, y1 - 1.2, z0, x1 - 0.2, y1 - 0.2, z0 + 0.18, 'ivory', sides='bed'))
    for k in range(6):
        a = k * 0.9
        R.nocol.add(box(-0.3, -0.2, 0, 0.3, 0.2, 0.01, 'bed').xform(a, x1 - 1.0 + 0.3 * math.cos(a), y1 - 0.7 + 0.2 * math.sin(a), z0 + 0.18 + k * 0.006))
    candle(R, x0 + 0.5, y1 - 0.4, z0, h=0.18)
    R.nocol.add(cyl(x0 + 1.6, y0 + 1.3, z0, z0 + 0.005, 0.25, 10, side='velvet', top='oxblood'))
    for k in range(5):
        a = k * 2 * math.pi / 5
        R.nocol.add(sphere(x0 + 1.6 + 0.12 * math.cos(a), y0 + 1.3 + 0.12 * math.sin(a), z0 + 0.01, 0.08, 6, 3, 'velvet'))
    R.nocol.add(box(x0 + 1.58, y0 + 0.5, z0, x0 + 1.62, y0 + 1.2, z0 + 0.01, 'green'))
    book_pile(R, x1 - 0.5, y0 + 0.5, z0, n=4, seed=3)
    R.light(sphere(x0 + 2.6, y0 + 2.4, z1 + 0.1, 0.09, 8, 4, 'e_lamp'))
    green_lamp(R, x0 + 0.6, y0 + 0.5, z0, 0.3)
    R.nocol.add(cyl(x0 + 2.6, y0 + 2.4, z1 + 0.14, z1 + 0.25, 0.005, 4, side='brass', caps=False))
    R.spot('plaque', x0 + 0.2, (y0 + y1) / 2, z0 + 0.6, 0.0)
    secret(R, (x0 + x1) / 2, (y0 + y1) / 2, z0, 'Between the Pages',
           'Where the leaves part at the edge there is room to crawl in. Someone has made a bed of loose pages here, and pressed a flower, and read by candlelight with the whole book over their head.', r=1.8)
    a = R.navpt(XA - 1.3, (c['py'][0] + c['py'][1]) / 2, 0.0)
    b = R.navpt(c['px'][1] - 0.6, (c['py'][0] + c['py'][1]) / 2, z0)
    d = R.navpt((x0 + x1) / 2 - 0.6, (y0 + y1) / 2, z0)
    R.link(a, b, d)
    NAV['cave'] = a


def gallery(R, W, D, HT):
    """A gallery all round at the upper floor, on columns, reached by a long stair on the north side."""
    z = GZ
    g = Geo()
    gx0, gx1, gy0, gy1 = T + GW, W - T - GW, T + GW, D - T - GW
    for (x0, y0, x1, y1) in ((T, T, W - T, gy0), (T, gy1, W - T, D - T), (T, gy0, gx0, gy1), (gx1, gy0, W - T, gy1)):
        g.add(box(x0, y0, z - 0.4, x1, y1, z, 'plaster', top='floor', skip=()))
    R.parts.add(g)
    # its edge: a balustrade, open where the stair arrives
    SX0, SN = 10.0, 40
    SX1 = SX0 + SN * 0.3
    SY0, SY1 = gy1 - 1.7, gy1 - 0.02
    rail(R, gx0, gy0, gx1, gy0, z, h=1.0, solid=True, mat='tile')
    rail(R, gx0, gy0, gx0, gy1, z, h=1.0, solid=True, mat='tile')
    rail(R, gx1, gy0, gx1, gy1, z, h=1.0, solid=True, mat='tile')
    rail(R, gx0, gy1, SX1 - 0.4, gy1, z, h=1.0, solid=True, mat='tile')
    rail(R, SX1 + 1.9, gy1, gx1, gy1, z, h=1.0, solid=True, mat='tile')
    # the stair: along the north, climbing east, and a landing out to the gallery
    railed_flight(R, SX0, SY0, 0.0, SY1 - SY0, SN, z / SN, 0.3, '+x', m='oak', riser='walnut', side='walnut', which=(0, 1))
    R.parts.add(box(SX1, SY0, z - 0.4, SX1 + 1.8, gy1 + 0.05, z, 'plaster', top='floor'))
    rail(R, SX1, SY0 + 0.05, SX1 + 1.8, SY0 + 0.05, z)
    rail(R, SX1 + 1.75, SY0 + 0.05, SX1 + 1.75, gy1, z)
    # a solid wall under the stair's north side
    R.parts.add(slope_box(SX0, SX1, SY1, SY1 + 0.15, 0, 0, 0.0, z, 'tile'))
    # columns
    for k in (4.0, 12.0, 20.0, 28.0):
        for (x, y) in ((k, gy0 - 0.2), (gx0 - 0.2, k), (gx1 + 0.2, k)):
            R.parts.add(cyl(x, y, 0, z - 0.4, 0.22, 16, side='tile', caps=False))
            R.parts.add(box(x - 0.3, y - 0.3, z - 0.7, x + 0.3, y + 0.3, z - 0.4, 'tile', skip=('+z',)))
        if not (SX0 - 0.5 < k < SX1 + 2.3):
            R.parts.add(cyl(k, gy1 + 0.2, 0, z - 0.4, 0.22, 16, side='tile', caps=False))
    # bookcases along the gallery walls
    rows = 16
    for (a, b) in ((0.7, 6.0), (10.0, 22.0), (26.0, W - 0.7)):
        sh(R, '+y', T, a, b, z=z, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, z=z, rows=rows, frame='walnut')
        sh(R, '+x', T, a, b, z=z, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, z=z, rows=rows, frame='walnut')
    ids = navloop(R, [(1.5, 1.5), (16, 1.5), (W - 1.5, 1.5), (W - 1.5, 16), (W - 1.5, D - 1.5), (SX1 + 0.9, D - 1.5), (1.5, D - 1.5), (1.5, 16)], z=z)
    a, b = R.navpt(SX0 - 0.6, (SY0 + SY1) / 2, 0.0), R.navpt(SX1 + 0.9, (SY0 + SY1) / 2, z)
    R.link(a, b, ids[5])
    NAV['stair'] = a


def hall(R, W, D, HT):
    rows = 17
    for (a, b) in ((GW + 0.8, 6.0), (10.0, 22.0), (26.0, W - GW - 0.8)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((GW + 0.8, 6.0), (10.0, 22.0), (26.0, D - GW - 0.8)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    # a normal desk, a green lamp and a stack of normal books by the book, for scale
    R.parts.add(table(1.2 + GW, 1.0 + GW - 1.8, 3.6 + GW, 2.0 + GW - 1.8, 0.78, 'walnut', top='leather'))
    # tall windows high in the east and west walls, and lay-lights over the book
    for y in (4.0, 12.0, 20.0, 28.0):
        for (x0, x1) in ((W - T - 0.02, W - T + 0.2), (T - 0.2, T + 0.02)):
            R.cut(box(x0, y - 0.9, 10.0, x1, y + 0.9, 14.6, 'tile'))
        R.light(box(W - T + 0.12, y - 0.9, 10.0, W - T + 0.14, y + 0.9, 14.6, 'e_sky'))
        R.light(box(T - 0.14, y - 0.9, 10.0, T - 0.12, y + 0.9, 14.6, 'e_sky'))
    for k in range(3):
        y = 9.0 + k * 7.0
        R.cut(box(7.0, y - 1.6, HT - 0.05, 25.0, y + 1.6, HT + 0.2, 'plaster'))
        R.light(box(7.4, y - 1.2, HT + 0.14, 24.6, y + 1.2, HT + 0.16, 'e_sky', skip=('+z',)))
    # standing lamps round the book
    for (x, y) in ((3.5, 3.5), (W - 3.5, 3.5), (3.5, D - 3.3), (W - 3.5, D - 3.3), (XS - 3.0, 3.0), (XS + 3.0, 3.0)):
        floor_lamp(R, x, y, 1.7)
    R.light(sphere(1.2, 16.0, 1.5, 0.1, 10, 5, 'e_amber')); R.parts.add(box(0.36, 15.8, 1.3, 0.6, 16.2, 1.4, 'brass'))
    R.light(sphere(W - 1.2, 16.0, 1.5, 0.1, 10, 5, 'e_amber')); R.parts.add(box(W - 0.6, 15.8, 1.3, W - 0.36, 16.2, 1.4, 'brass'))
    ids = navloop(R, [(2.2, 2.2), (8.0, 2.4), (NAV_flap_x(), 2.4), (24.0, 2.4), (W - 2.2, 2.2), (W - 1.9, 8.0), (W - 1.9, LADY), (W - 1.9, 24.0), (W - 2.2, D - 2.2),
                      (24.0, D - 2.0), (16.0, D - 2.3), (8.0, D - 2.3), (2.2, D - 2.2), (1.9, 24.0), (1.9, 16.0), (1.9, 8.0)])
    R.link(ids[2], NAV['flap'][0], NAV['flap'][1])
    lf = R.navpt(XB + CB + 1.9, LADY, 0.0)
    R.link(ids[6], lf, NAV['lad'])
    R.link(ids[14], NAV['cave'])
    R.link(ids[11], NAV['stair'])


def NAV_flap_x():
    return (FLAP[0] + FLAP[1]) / 2
