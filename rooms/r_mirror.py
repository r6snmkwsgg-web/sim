"""The Symmetric Room: an arcade down the middle, and on each side of it the same vaulted room: the
same shelves, the same table and lamp, the same open book, one chair each, facing each other."""
from lib import *
from kit_c import *


def make():
    R = Room('mirror', 1, 1, res=1024)
    R.sockets(floor='mosaic', wall='tile')
    b0, b1 = 2.9, C - 2.9                 # the halls run between these; flat-ceilinged bands at the ends
    hb = 4.5
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, b0, hb, 'tile', bottom='mosaic', top='plaster'))
    R.cut(box(T - 0.02, b1, 0, C - T + 0.02, C - T + 0.02, hb, 'tile', bottom='mosaic', top='plaster'))
    aw = 0.2                              # half the arcade wall
    for (x0, x1) in ((T - 0.02, 8 - aw), (8 + aw, C - T + 0.02)):
        c, w = (x0 + x1) / 2, x1 - x0
        pr = arch_profile(c, w, 0, 3.5, 32)
        R.cut(prism(pr, 'y', b0 - 0.01, b1 + 0.01, arch_mats(len(pr), 'mosaic', 'tile')))
    # three arches through the arcade
    for yc in (4.9, 8.0, 11.1):
        pr = arch_profile(yc, 2.2, 0, 2.6, 20)
        R.cut(prism(pr, 'x', 8 - aw - 0.05, 8 + aw + 0.05, arch_mats(len(pr), 'mosaic', 'tile')))
    R.parts.add(box(8 - aw - 0.04, b0, 3.95, 8 + aw + 0.04, b1, 4.1, 'tile'))     # a string course along the arcade
    # the two halves, exactly mirrored
    for s in (-1, 1):
        X = lambda d: 8 + s * d
        A = lambda a: a if s > 0 else math.pi - a
        def bx(d0, y0, d1, y1, z0, z1, m, **kw):
            xa, xb = sorted((X(d0), X(d1)))
            R.parts.add(box(xa, y0, z0, xb, y1, z1, m, **kw))
        # tall cases on the outer wall either side of the side door, and on the end walls
        wx = X(8 - T)
        for (p, q) in ((3.0, 6.2), (9.8, 13.0)):
            if s < 0: R.shelf(wx, q, 0, q - p, '+x', rows=8, frame='oak')
            else: R.shelf(wx, p, 0, q - p, '-x', rows=8, frame='oak')
        for (d0, d1) in ((2.0, 7.4),):
            xa, xb = sorted((X(d0), X(d1)))
            R.shelf(xa, T, 0, xb - xa, '+y', rows=9, frame='oak')
            R.shelf(xb, C - T, 0, xb - xa, '-y', rows=9, frame='oak')
        # a rug, a table with a lamp and an open book, one chair looking through the middle arch
        xa, xb = sorted((X(2.0), X(5.4)))
        rug(R, xa, 6.2, xb, 9.8)
        xa, xb = sorted((X(2.4), X(3.3)))
        table(R, xa, 7.2, xb, 8.8, m='walnut', top='leather')
        desk_lamp(R, X(2.85), 8.45, 0.76)
        open_book(R, X(2.85), 7.75, 0.76, A(math.pi / 2))
        chair(R, X(3.9), 8.0, A(math.pi))
        # candles either side of the chair, and a book dropped on the floor
        candle_stand(R, X(4.6), 6.6); candle_stand(R, X(4.6), 9.4)
        R.parts.add(box(-0.13, -0.09, 0, 0.13, 0.09, 0.04, 'oxblood').xform(A(0.6), X(5.6), 10.6))
        # lamps hanging in the vault, and over the end bands
        for y in (4.9, 8.0, 11.1):
            hang_lamp(R, X(4.07), y, 4.6, 7.3, r=0.17)
        for y in (1.6, C - 1.6):
            hang_lamp(R, X(4.07), y, 3.2, hb, r=0.14)
    # night lights on the arcade piers, both faces
    for y in (3.35, 6.45, 9.55, 12.65):
        for s in (-1, 1):
            R.light(box(8 + s * (aw + 0.01) - 0.02, y - 0.06, 2.2, 8 + s * (aw + 0.01) + 0.02, y + 0.06, 2.34, 'e_amber'))
    # walkers: a figure of eight through the arches
    w = navloop(R, ((1.4, 1.6), (4.1, 1.6), (6.5, 4.9), (6.5, 11.1), (4.1, C - 1.6), (1.4, C - 1.6), (1.4, 8)))
    e = navloop(R, ((C - 1.4, 1.6), (C - 4.1, 1.6), (C - 6.5, 4.9), (C - 6.5, 11.1), (C - 4.1, C - 1.6), (C - 1.4, C - 1.6), (C - 1.4, 8)))
    R.link(w[2], e[2]); R.link(w[3], e[3]); R.link(w[1], R.navpt(8, 1.6), e[1]); R.link(w[4], R.navpt(8, C - 1.6), e[4])
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Symmetric Room', weight=5,
                  blurb='Everything on this side of the arches is on the other side too, the other way round. There is a chair on each side, and you are not sure which one you were sitting in.')
    R.meta['box'] = [[T, 0, T], [C - T, 7.3, C - T]]
    return R
