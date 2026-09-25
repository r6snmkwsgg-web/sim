"""The Hive: a hall whose walls are honeycomb, every cell a reading carrel or a cell of books, all of
it golden wax, honey creeping down from the edges. In the middle stands a hexagonal tower of comb
with a carrel in each face. One of them has no desk in it and a back wall that is very thin."""
from lib import *
from kit_h4 import *

W = 32.0
H = 7.5
F0, F1 = 3.4, 28.6                  # the hall's faces (the comb walls are 3 m thick)
S = 16.0 / 6                        # column spacing: doors fall on columns
RC = 1.62                           # cut radius of a cell (flat floor, flat top)
HC = RC * math.sqrt(3)              # its height
TILE = S / 1.5 * math.sqrt(3)       # tier spacing
CC = (16.0, 16.0)
TR = 4.6                            # the tower (vertex radius); faces at 30 + 60k degrees
TA = TR * math.sqrt(3) / 2          # its apothem
QR = 2.8                            # the queen's chamber inside it
SECRET_FACE = 150.0


def loc(fc, phi, x, y):
    c, s = math.cos(phi), math.sin(phi)
    return (fc[0] + x * c - y * s, fc[1] + x * s + y * c)


def hex_cut(R, fc, phi, zc, depth, m='wax', bottom='wax'):
    """A hexagonal cell cut into a comb face at fc (its outward normal at angle phi), centred at height zc."""
    pr = hexpts(0.0, zc, RC)
    mats = [m] * 6
    mats[4] = bottom          # the flat edge at the bottom: hexpts starts at angle 0; edge 4-5 is the lowest
    g = prism(pr, 'x', -depth, 0.35, mats, cap=m)
    R.cut(g.xform(phi, fc[0], fc[1], 0))


def carrel(R, fc, phi, depth, rnd, desk=True):
    hex_cut(R, fc, phi, HC / 2, depth, bottom='oak')
    L = lambda x, y: loc(fc, phi, x, y)
    if desk:
        R.parts.add(_table_local(-depth + 0.05, -0.7, -depth + 0.72, 0.7).xform(phi, fc[0], fc[1], 0))
        x, y = L(-depth + 1.2, 0.0)
        chair(R, x, y, phi + math.pi, 0.0)
        x, y = L(-depth + 0.3, 0.45)
        desk_lamp(R, x, y, 0.76)
        if rnd.random() < 0.6:
            x, y = L(-depth + 0.45, -0.25); open_book(R, x, y, 0.76, phi + math.pi / 2)
        else:
            x, y = L(-depth + 0.4, -0.3); book_pile(R, x, y, 0.76, rnd.randint(2, 5), rnd)
        for k, z in enumerate((1.25, 1.67)):
            x, y = L(-depth + 0.02, 1.0)
            row_case(R, x, y, z, 2.0, phi, frame='wax', depth=0.26, top=(k == 1))
    drips(R, fc, phi, HC, rnd, 5)


def niche(R, fc, phi, zc, rnd, depth=0.95):
    hex_cut(R, fc, phi, zc, depth)
    for (d0, d1) in ((-0.63, -0.21), (-0.21, 0.21), (0.21, 0.63)):
        wdt = 2 * (RC - max(abs(d0), abs(d1)) / math.sqrt(3)) - 0.16
        x, y = loc(fc, phi, -depth + 0.01, wdt / 2)
        row_case(R, x, y, zc + d0, wdt, phi, frame='wax', depth=0.3, top=(d1 > 0.5))
    drips(R, fc, phi, zc + HC / 2, rnd, 3)


def drips(R, fc, phi, ztop, rnd, n):
    for k in range(n):
        u = rnd.uniform(-RC * 0.45, RC * 0.45)
        x, y = loc(fc, phi, 0.06, u)
        L = rnd.uniform(0.15, 0.9)
        R.nocol.add(cone(x, y, ztop + 0.02, ztop - L, rnd.uniform(0.04, 0.08), 0.01, 5, 'honey'))


def _table_local(x0, y0, x1, y1, h=0.76):
    g = box(x0, y0, h - 0.05, x1, y1, h, 'wax', top='leather')
    for (px, py) in ((x0 + 0.08, y0 + 0.08), (x1 - 0.08, y0 + 0.08), (x1 - 0.08, y1 - 0.08), (x0 + 0.08, y1 - 0.08)):
        g.add(box(px - 0.04, py - 0.04, 0, px + 0.04, py + 0.04, h - 0.05, 'wax', skip=('-z',)))
    return g


def make():
    R = Room('hive', 2, 2, res=2048)
    R.sockets(floor='oak', wall='wax')
    rnd = random.Random(35)
    # the hall: everything between the comb walls and the tower (two halves, overlapping on the centre line)
    hx = [(CC[0] + TR * math.cos(math.radians(60 * k)), CC[1] + TR * math.sin(math.radians(60 * k))) for k in range(6)]
    west = [(F0, F0), (16.1, F0), (16.1, hx[5][1]), hx[4], hx[3], hx[2], (16.1, hx[1][1]), (16.1, F1), (F0, F1)]
    east = [(15.9, F0), (F1, F0), (F1, F1), (15.9, F1), (15.9, hx[1][1]), hx[1], hx[0], hx[5], (15.9, hx[5][1])]
    R.cut(poly_prism(west, 0.0, H, side='wax', top='wax', bottom='oak'))
    R.cut(poly_prism(east, 0.0, H, side='wax', top='wax', bottom='oak'))
    # the doorways carried through the comb
    dp = arch_profile(0, DW, 0, DJ, 16)
    for c in (8.0, 24.0):
        R.cut(prism([(p + c, q) for p, q in dp], 'y', T - 0.1, F0 + 0.05, arch_mats(len(dp), 'oak', 'wax')))
        R.cut(prism([(p + c, q) for p, q in dp], 'y', F1 - 0.05, W - T + 0.1, arch_mats(len(dp), 'oak', 'wax')))
        R.cut(prism([(p + c, q) for p, q in dp], 'x', T - 0.1, F0 + 0.05, arch_mats(len(dp), 'oak', 'wax')))
        R.cut(prism([(p + c, q) for p, q in dp], 'x', F1 - 0.05, W - T + 0.1, arch_mats(len(dp), 'oak', 'wax')))
    # the comb walls: carrels at the floor in the door columns' rhythm, cells of books above and between
    faces = [(lambda p: (p, F0), math.pi / 2), (lambda p: (p, F1), -math.pi / 2), (lambda p: (F0, p), 0.0), (lambda p: (F1, p), math.pi)]
    for (pos, phi) in faces:
        for k in range(-1, 8):
            p = 8.0 + k * S
            if p < F0 + 1.7 or p > F1 - 1.7: continue
            fc = pos(p)
            door = abs(p - 8.0) < 0.1 or abs(p - 24.0) < 0.1
            if k % 2 == 0:
                if not door:
                    carrel(R, fc, phi, 2.4, rnd)
                    niche(R, fc, phi, HC / 2 + TILE, rnd)
                else:
                    drips(R, fc, phi, DJ + DR + 0.1, rnd, 4)
            else:
                niche(R, fc, phi, HC / 2 + TILE / 2, rnd)
                niche(R, fc, phi, HC / 2 + TILE * 1.5, rnd)
    # the tower: a carrel in each face, a cell of books over it; one carrel is not what it seems
    for k in range(6):
        ang = math.radians(30 + 60 * k)
        fc = (CC[0] + TA * math.cos(ang), CC[1] + TA * math.sin(ang))
        sec = abs(30 + 60 * k - SECRET_FACE) < 1
        if sec: secret_carrel(R, fc, ang, rnd)
        else: carrel(R, fc, ang, 1.45, rnd)
        niche(R, fc, ang, HC / 2 + TILE, rnd, depth=0.9)
    queen(R, rnd)
    hall(R, rnd, hx)

    pts = [(CC[0] + 6.6 * math.cos(math.radians(60 * k + 30)), CC[1] + 6.6 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    ids = navloop(R, pts)
    for p in ((8.0, 4.6), (24.0, 4.6), (8.0, 27.4), (24.0, 27.4), (4.6, 8.0), (4.6, 24.0), (27.4, 8.0), (27.4, 24.0)):
        j = min(range(6), key=lambda i: math.hypot(pts[i][0] - p[0], pts[i][1] - p[1]))
        R.link(R.navpt(*p), ids[j])
    R.spot('probe', 16.0, 7.0, 3.5)
    R.meta.update(label='The Hive', weight=4,
                  blurb='Every cell has a reader\'s chair in it, or a shelf, or both. The wax is warm. Something, somewhere in the comb, is humming.')
    R.meta['box'] = [[T, 0, T], [W - T, H, W - T]]
    fx(R, 'dust', [F0, F0, 0.3, F1, F1, H - 0.2])
    secret(R, CC[0], CC[1], 0.0, "The Queen's Chamber",
           'You pushed through the wax at the back of the empty carrel. In the middle of the comb there is one chair, bigger than the others, and one book, bigger than the others.', r=2.0)
    return tidy(R)


def secret_carrel(R, fc, phi, rnd):
    depth = TA - QR * math.sqrt(3) / 2 + 0.3          # right through into the chamber
    hex_cut(R, fc, phi, HC / 2, depth, bottom='oak')
    # the back of it is a sheet of wax you can walk through: it looks like every other back wall
    back = -1.45
    pr = hexpts(0.0, HC / 2, RC + 0.05)
    R.nocol.add(prism(pr, 'x', back - 0.04, back, 'wax', cap='wax').xform(phi, fc[0], fc[1], 0))
    for k in range(9):
        u = rnd.uniform(-1.0, 1.0); z = rnd.uniform(0.6, 2.4)
        x, y = loc(fc, phi, back + 0.02, u)
        R.nocol.add(cone(x, y, z, z - rnd.uniform(0.2, 0.6), 0.05, 0.01, 5, 'honey'))
    # an empty carrel: a stool pushed aside, a lamp on the floor
    x, y = loc(fc, phi, -0.5, 0.55)
    R.parts.add(cyl(x, y, 0.0, 0.45, 0.2, 10, side='wax', top='leather'))
    x, y = loc(fc, phi, -1.1, -0.5)
    R.parts.add(cyl(x, y, 0.0, 0.03, 0.09, 8, side='brass', top='brass'))
    R.light(sphere(x, y, 0.12, 0.08, 8, 4, 'e_candle'))
    drips(R, fc, phi, HC, rnd, 6)


def queen(R, rnd):
    cx, cy = CC
    hq = [(cx + QR * math.cos(math.radians(60 * k)), cy + QR * math.sin(math.radians(60 * k))) for k in range(6)]
    R.cut(poly_prism(hq, 0.0, 4.6, side='wax', top='wax', bottom='honey'))
    hq2 = [(cx + 1.9 * math.cos(math.radians(60 * k)), cy + 1.9 * math.sin(math.radians(60 * k))) for k in range(6)]
    R.cut(poly_prism(hq2, 4.5, 6.6, side='wax', top='wax', bottom='wax'))
    R.light(poly_prism([(cx + 0.6 * math.cos(math.radians(60 * k)), cy + 0.6 * math.sin(math.radians(60 * k))) for k in range(6)], 6.55, 6.58, 'e_honey', 'e_honey', 'e_honey'))
    # glowing cells set into the walls
    for k in range(6):
        a = math.radians(60 * k + 30)
        ap = QR * math.sqrt(3) / 2 - 0.02
        for (du, z) in ((0.0, 3.9),):
            x = cx + ap * math.cos(a) - du * math.sin(a); y = cy + ap * math.sin(a) + du * math.cos(a)
            g = prism(hexpts(0.0, z, 0.22), 'x', -0.02, 0.0, 'e_candle', cap='e_candle')
            R.light(g.xform(a, x, y, 0))
    # the throne, facing the way in; the great book; honey on the floor
    ta = math.radians(SECRET_FACE) + math.pi
    tx, ty = cx + 1.7 * math.cos(ta), cy + 1.7 * math.sin(ta)
    g = box(-0.45, -0.6, 0.0, 0.45, 0.6, 0.5, 'velvet', sides='wax')
    g.add(box(-0.45, -0.6, 0.5, -0.25, 0.6, 2.1, 'wax'))
    g.add(box(-0.45, -0.75, 0.0, 0.4, -0.6, 0.85, 'wax')); g.add(box(-0.45, 0.6, 0.0, 0.4, 0.75, 0.85, 'wax'))
    for k in range(5):
        g.add(box(-0.47, -0.55 + k * 0.275, 2.1, -0.23, -0.45 + k * 0.275, 2.3 + (0.15 if k == 2 else 0.0), 'gilt'))
    R.parts.add(g.xform(ta + math.pi, tx, ty, 0.0))
    R.spot('sit', tx, ty, 0.5, ta + math.pi)
    lx, ly = cx + 0.1 * math.cos(ta), cy + 0.1 * math.sin(ta)
    R.parts.add(box(lx - 0.3, ly - 0.3, 0.0, lx + 0.3, ly + 0.3, 0.95, 'wax'))
    bk = box(-0.45, -0.32, 0.0, 0.45, 0.32, 0.05, 'leather')
    bk.add(box(-0.43, -0.3, 0.05, -0.01, 0.3, 0.13, 'ivory')); bk.add(box(0.01, -0.3, 0.05, 0.43, 0.3, 0.13, 'ivory'))
    R.nocol.add(bk.xform(ta + math.pi / 2, lx, ly, 0.95))
    R.spot('plaque', cx, cy, 0.0, ta + math.pi, text='Long live the Queen, who has read every book in the hive, and says they are all the same book.')
    R.nocol.add(cyl(cx - 0.9, cy + 1.0, 0.0, 0.015, 0.7, 16, side='honey', top='honey'))
    for k in range(14):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.3, 1.7)
        z = 4.6 if d > 1.2 else 6.6
        R.nocol.add(cone(cx + d * math.cos(a), cy + d * math.sin(a), z, z - rnd.uniform(0.3, 1.4), 0.06, 0.01, 5, 'honey'))


def hall(R, rnd, hx):
    # hexagonal reading tables round the tower, lamps; honey light in the ceiling over them
    for k in range(6):
        a = math.radians(60 * k)
        x, y = CC[0] + 8.2 * math.cos(a), CC[1] + 8.2 * math.sin(a)
        top = [(x + 0.85 * math.cos(math.radians(60 * j)), y + 0.85 * math.sin(math.radians(60 * j))) for j in range(6)]
        R.parts.add(poly_prism(top, 0.72, 0.78, 'wax', 'leather', 'wax'))
        R.parts.add(cyl(x, y, 0.0, 0.72, 0.1, 8, side='wax', top='wax'))
        R.parts.add(cyl(x, y, 0.0, 0.04, 0.4, 12, side='wax', top='wax'))
        desk_lamp(R, x, y, 0.78)
        for j in range(3):
            b = math.radians(60 * j * 2 + 30)
            chair(R, x + 1.25 * math.cos(b), y + 1.25 * math.sin(b), b + math.pi, 0.0)
        R.light(poly_prism([(x + 1.0 * math.cos(math.radians(60 * j)), y + 1.0 * math.sin(math.radians(60 * j))) for j in range(6)], H - 0.04, H - 0.02, 'e_honey', 'e_honey', 'e_honey'))
        R.nocol.add(poly_prism([(x + 1.15 * math.cos(math.radians(60 * j)), y + 1.15 * math.sin(math.radians(60 * j))) for j in range(6)], H - 0.1, H - 0.02, 'gilt', 'wax', 'gilt'))
    # honey down the tower's edges and pooled on the floor
    for (x, y) in hx:
        for k in range(3):
            z = rnd.uniform(3.0, H)
            R.nocol.add(cone(x, y, z, z - rnd.uniform(0.6, 2.2), 0.09, 0.015, 5, 'honey'))
    for k in range(10):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(5.2, 10.5)
        R.nocol.add(blob(CC[0] + d * math.cos(a), CC[1] + d * math.sin(a), 0.0, rnd.uniform(0.3, 0.8), rnd.uniform(0.3, 0.8), 0.02, 'honey', 10, 3, a))
    # night lamps on posts
    for k in range(6):
        a = math.radians(60 * k + 30)
        post_lamp(R, CC[0] + 11.0 * math.cos(a), CC[1] + 11.0 * math.sin(a), 0.0, 2.4)
