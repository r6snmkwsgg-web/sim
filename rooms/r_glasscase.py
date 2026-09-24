"""The Display Cases: a dark museum gallery of brass-framed cases with no glass and no lids, each
holding one open book on red velvet under its own little light. A taller case in the middle."""
from lib import *
from kit_d import *


def case(R, x, y, w=0.62, d=0.46, h=0.88, fh=0.42, ang=0.0):
    """One display case: walnut plinth, velvet bed, an open book, an empty brass frame above."""
    g = Geo()
    g.add(box(-w / 2 - 0.04, -d / 2 - 0.04, 0, w / 2 + 0.04, d / 2 + 0.04, 0.12, 'walnut', skip=('-z',)))
    g.add(box(-w / 2, -d / 2, 0.12, w / 2, d / 2, h, 'walnut', skip=('-z', '+z')))
    g.add(box(-w / 2 + 0.02, -d / 2 + 0.02, h, w / 2 - 0.02, d / 2 - 0.02, h + 0.03, 'velvet', skip=('-z',)))
    b = Geo()
    for (px, py) in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)):
        b.add(box(px - 0.015, py - 0.015, h, px + 0.015, py + 0.015, h + fh - 0.02, 'brass', skip=('-z', '+z')))
    zz = h + fh - 0.02
    b.add(box(-w / 2 - 0.015, -d / 2 - 0.015, zz, w / 2 + 0.015, -d / 2 + 0.015, zz + 0.025, 'brass', skip=('-z',)))
    b.add(box(-w / 2 - 0.015, d / 2 - 0.015, zz, w / 2 + 0.015, d / 2 + 0.015, zz + 0.025, 'brass', skip=('-z',)))
    b.add(box(-w / 2 - 0.015, -d / 2 + 0.015, zz, -w / 2 + 0.015, d / 2 - 0.015, zz + 0.025, 'brass', skip=('-x', '+x', '-z')))
    b.add(box(w / 2 - 0.015, -d / 2 + 0.015, zz, w / 2 + 0.015, d / 2 - 0.015, zz + 0.025, 'brass', skip=('-x', '+x', '-z')))
    R.parts.add(g.xform(ang, x, y))
    R.parts.add(b.xform(ang, x, y))
    book(R, x, y, h + 0.03, ang + math.pi / 2 + 0.06, m='oxblood', open_=True)


def make():
    R = Room('glasscase', 1, 1, res=1024)
    H = 5.0
    shell(R, H, floor='terrazzo', wall='damask', top='walnut')
    # a dark walnut dado and a brass picture rail round the walls
    for (x0, y0, x1, y1) in ((I0, I0, I1, I0 + 0.04), (I0, I1 - 0.04, I1, I1), (I0, I0, I0 + 0.04, I1), (I1 - 0.04, I0, I1, I1)):
        R.nocol.add(box(x0, y0, 0, x1, y1, 1.0, 'walnut', skip=('-z',)))
        R.nocol.add(box(x0, y0, 3.2, x1, y1, 3.25, 'brass'))
    # a deep coffered ceiling: dark beams on a 2 m grid
    for p in (1.5, 3.3, 5.1, 6.9, 9.1, 10.9, 12.7, 14.5):
        R.parts.add(box(p - 0.1, I0, H - 0.45, p + 0.1, I1, H, 'walnut', skip=('+z',)))
        R.parts.add(box(I0, p - 0.1, H - 0.45, I1, p + 0.1, H, 'walnut', skip=('+z',)))
    # the cases, in rows, with cross aisles to the four doors
    xs = (2.4, 4.2, 6.0, 10.0, 11.8, 13.6)
    k = 0
    for x in xs:
        for y in xs:
            k += 1
            case(R, x, y)
            # a small spot over each case
            R.light(box(x - 0.15, y - 0.15, H - 0.02, x + 0.15, y + 0.15, H - 0.01, 'e_lamp', skip=('+z', '-x', '+x', '-y', '+y')))
    # the one in the middle: a stepped marble plinth, a tall empty brass cage, one closed book
    R.parts.add(box(6.9, 6.9, 0, 9.1, 9.1, 0.18, 'terrazzo', sides='tile'))
    R.parts.add(box(7.2, 7.2, 0.18, 8.8, 8.8, 0.36, 'terrazzo', sides='tile'))
    R.parts.add(box(7.55, 7.55, 0.36, 8.45, 8.45, 1.1, 'walnut'))
    R.parts.add(box(7.6, 7.6, 1.1, 8.4, 8.4, 1.14, 'velvet'))
    cage = Geo()
    for (px, py) in ((7.55, 7.55), (8.45, 7.55), (8.45, 8.45), (7.55, 8.45)):
        cage.add(box(px - 0.025, py - 0.025, 1.1, px + 0.025, py + 0.025, 2.6, 'brass', skip=('-z',)))
    for zz in (1.1, 2.55):
        cage.add(box(7.52, 7.52, zz, 8.48, 7.58, zz + 0.05, 'brass')); cage.add(box(7.52, 8.42, zz, 8.48, 8.48, zz + 0.05, 'brass'))
        cage.add(box(7.52, 7.58, zz, 7.58, 8.42, zz + 0.05, 'brass')); cage.add(box(8.42, 7.58, zz, 8.48, 8.42, zz + 0.05, 'brass'))
    R.nocol.add(cage)
    R.col.add(box(7.55, 7.55, 1.1, 8.45, 8.45, 2.6, 'tile'))
    book(R, 8, 8, 1.14, 0.4, m='leather', w=0.2, l=0.28, t=0.07)
    # its light comes from a round opening in the ceiling
    R.cut(cyl(8, 8, H - 0.1, H + 1.2, 1.2, 32, side='plaster', top='plaster'))
    R.light(cyl(8, 8, H + 1.1, H + 1.12, 1.0, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    # low bookcases along the walls, between the doors
    for (a, b) in ((0.8, 6.2), (9.8, C - 0.8)):
        for f in ('+y', '-y', '+x', '-x'):
            wall_shelf(R, f, a, b, 0, rows=3, row_h=0.4, frame='walnut', off=0.0)
    # a few dim sconces over the shelves
    for p in (3.5, 12.5):
        for (x, y) in ((p, I0 + 0.12), (p, I1 - 0.12), (I0 + 0.12, p), (I1 - 0.12, p)):
            R.light(cyl(x, y, 2.3, 2.5, 0.08, 8, side='e_amber', top='e_amber', bottom='e_amber'))
    # night: candles by the doors
    loop(R, [(1.5, 1.5), (8, 1.5), (14.5, 1.5), (14.5, 8), (14.5, 14.5), (8, 14.5), (1.5, 14.5), (1.5, 8)])
    loop(R, [(5.1, 5.1), (8, 5.1), (10.9, 5.1), (10.9, 10.9), (8, 10.9), (5.1, 10.9)])
    for (x, y, a) in ((8, 3.3, math.pi / 2), (8, 12.7, -math.pi / 2)):
        R.spot('read', x, y, 0, a)
    R.spot('probe', 8, 5.1, 1.7)
    R.meta.update(label='The Display Cases', weight=5,
                  blurb='Each case holds a single book, open on velvet and lit like a relic. There is no glass. Nobody has ever said what makes these ones special.')
    return R
