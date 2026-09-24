"""The Carrels: four rows of identical study carrels, back to back along three corridors. Each has a
desk, a chair, a lamp and a shelf of books. They are all free. They are always all free."""
from lib import *
from kit_e import *


def carrel(R, x0, x1, yb, yf, lamp='e_lamp'):
    """One carrel between x0 and x1; its desk against the back at yb, open toward yf."""
    s = 1 if yf > yb else -1
    Y = lambda d: yb + s * d
    lo = lambda a, b: min(Y(a), Y(b)); hi = lambda a, b: max(Y(a), Y(b))
    xm = (x0 + x1) / 2
    # the desk, spanning partition to partition
    R.parts.add(box(x0 + 0.03, lo(0, 0.62), 0.72, x1 - 0.03, hi(0, 0.62), 0.76, 'oak'))
    R.parts.add(box(x0 + 0.03, lo(0.05, 0.6), 0.6, x1 - 0.03, hi(0.05, 0.6), 0.72, 'oak', skip=('+z',)))
    # a shelf of books over it
    if s > 0: R.shelf(x0 + 0.04, yb, 1.05, x1 - x0 - 0.08, '+y', rows=2, row_h=0.36, depth=0.26, frame='oak', sides=False, back=False, crown=False)
    else:     R.shelf(x1 - 0.04, yb, 1.05, x1 - x0 - 0.08, '-y', rows=2, row_h=0.36, depth=0.26, frame='oak', sides=False, back=False, crown=False)
    # a green-shaded lamp on the desk
    lx, ly = x1 - 0.3, Y(0.33)
    R.parts.add(cyl(lx, ly, 0.76, 0.79, 0.07, 10, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(lx, ly, 0.79, 1.05, 0.012, 6, side='brass', caps=False))
    R.parts.add(box(lx - 0.16, ly - 0.07, 1.02, lx + 0.12, ly + 0.07, 1.1, 'green'))
    R.light(box(lx - 0.14, ly - 0.05, 1.0, lx + 0.1, ly + 0.05, 1.02, lamp))
    # the chair, facing the desk
    chair(R, xm, Y(0.95), -s * math.pi / 2, frame='oak', seat='green')


def make():
    R = Room('carrels', 2, 1, res=1024)
    R.sockets(floor='floor')
    W, D = R.W, R.D
    cy = D / 2
    H = 4.3
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='floor', top='plaster'))
    # rows (south half; mirrored north): outer corridor | row A (opens south) | spine | row B (opens to middle) | middle corridor
    ra0, sp0, sp1, rb1 = 2.5, 4.35, 4.5, 6.35       # row A from ra0 to sp0, spine, row B from sp1 to rb1
    ph, sh = 1.45, 2.05                               # partition height, spine height
    segs = [(2.0, 6.4, 3), (9.6, 22.4, 8), (25.6, 30.0, 3)]
    k = 0
    for side in (0, 1):
        f = (lambda y: y) if side == 0 else (lambda y: D - y)
        lo_hi = lambda a, b: (min(f(a), f(b)), max(f(a), f(b)))
        for (xa, xb, n) in segs:
            p = (xb - xa) / n
            # the spine between the two rows, full length of the segment
            y0, y1 = lo_hi(sp0, sp1)
            R.parts.add(box(xa - 0.05, y0, 0, xb + 0.05, y1, sh, 'walnut'))
            R.parts.add(box(xa - 0.07, y0 - 0.02, sh, xb + 0.07, y1 + 0.02, sh + 0.05, 'brass'))
            # partitions
            for i in range(n + 1):
                x = xa + i * p
                for (a, b) in ((ra0, sp0), (sp1, rb1)):
                    y0, y1 = lo_hi(a, b)
                    R.parts.add(box(x - 0.03, y0, 0, x + 0.03, y1, ph, 'walnut'))
            for i in range(n):
                x0, x1 = xa + i * p, xa + (i + 1) * p
                k += 1
                lamp = 'e_amber' if k % 5 == 2 else 'e_lamp'
                carrel(R, x0, x1, f(sp0), f(ra0), lamp)       # row A: desk against the spine, opens to the outer corridor
                k += 1
                lamp = 'e_amber' if k % 5 == 2 else 'e_lamp'
                carrel(R, x0, x1, f(sp1), f(rb1), lamp)       # row B: opens to the middle
    # bookcases on the outer walls and the end walls of the outer corridors
    wall_shelves(R, rows=9, frame='walnut', sides='SN')
    for (a, b) in ((T + 0.1, ra0 - 0.2), (D - ra0 + 0.2, D - T - 0.1)):
        R.shelf(T, b, 0, b - a, '+x', rows=9, frame='walnut')
        R.shelf(W - T, a, 0, b - a, '-x', rows=9, frame='walnut')
    # ceiling lights: a grid of flat panels over the corridors
    for x in [2.0 + 2.0 * i for i in range(15)]:
        for y in ((T + ra0) / 2, cy, D - (T + ra0) / 2):
            w = 0.45 if y != cy else 0.6
            R.light(box(x - w, y - w, H - 0.04, x + w, y + w, H - 0.01, 'e_panel'))
    for x in (8.0, 24.0):
        for y in (3.4, 5.4, D - 5.4, D - 3.4):
            R.light(box(x - 0.6, y - 0.6, H - 0.04, x + 0.6, y + 0.6, H - 0.01, 'e_panel'))
    # walkers: the three corridors and the two cross corridors
    mid = loop(R, [(1.2, cy), (8.0, cy), (16.0, cy), (24.0, cy), (W - 1.2, cy)], close=False)
    so = loop(R, [(1.2, 1.5), (8.0, 1.5), (16.0, 1.5), (24.0, 1.5), (W - 1.2, 1.5)], close=False)
    no = loop(R, [(1.2, D - 1.5), (8.0, D - 1.5), (16.0, D - 1.5), (24.0, D - 1.5), (W - 1.2, D - 1.5)], close=False)
    R.link(so[1], mid[1], no[1]); R.link(so[3], mid[3], no[3]); R.link(so[0], mid[0], no[0]); R.link(so[4], mid[4], no[4])
    R.spot('probe', 16.0, cy, 1.9)
    R.meta.update(label='The Carrels', weight=7,
                  blurb='Row after row of study carrels, each with its lamp lit and its chair pushed in, each exactly like the last. Choose one. It makes no difference which.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    return R
