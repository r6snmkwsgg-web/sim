"""The Negative: a vaulted reading hall with aisles of stacks, long tables down the nave, lamps on the
tables and hung from the vault. Inside it the picture inverts, like a photographic negative: the dark
shelves stand white, the white lampshades go black, and the lamps, which are built to glow black,
shine. At its heart a small cabinet of bookcases, and inside that, through the one case that is not
there, a little room where the effect stops and everything is its own colour again."""
from kit_h12 import *

W = D = 32.0
NX0, NX1 = 9.8, 22.2           # the nave between its arcades
AH = 4.6                       # the aisles' flat ceilings
SPRING, RISE = 5.2, 2.3
ARCH_Y = (4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0)
HX0, HX1, HY0, HY1 = 13.0, 19.0, 13.5, 18.5    # the heart cabinet (outside faces)
HT = 0.3
HH = 3.4


def make():
    R = Room('negative', 2, 2, res=2048)
    rs = rng(74)
    R.sockets(floor='terrazzo', wall='slate')
    vault_y(R, T - 0.02, D - T + 0.02, (NX0 + NX1) / 2, NX1 - NX0, SPRING, RISE, wall='slate', floor='white')
    for (x0, x1) in ((T - 0.02, NX0 - 0.6), (NX1 + 0.6, W - T + 0.02)):
        R.cut(box(x0, T - 0.02, 0, x1, D - T + 0.02, AH, 'slate', bottom='terrazzo', top='plaster'))
    arcade(R)
    aisles(R, rs)
    nave(R, rs)
    heart(R, rs)
    # the effect: the whole room but the heart's inside
    ix0, iy0, ix1, iy1 = HX0 + HT, HY0 + HT, HX1 - HT, HY1 - HT
    for bx in ([T, T, 0, W - T, iy0, TOP], [T, iy1, 0, W - T, D - T, TOP], [T, iy0, 0, ix0, iy1, TOP], [ix1, iy0, 0, W - T, iy1, TOP]):
        fx(R, 'negative', bx)
    fx(R, 'dust', [NX0, T, 1.0, NX1, D - T, 7.0])
    ids = navgrid(R, {
        'a': (11.2, 3.0), 'b': (16.0, 3.0), 'c': (20.8, 3.0), 'd': (20.8, 12.0), 'e': (20.8, 20.0), 'f': (20.8, 29.0),
        'g': (16.0, 29.0), 'h': (11.2, 29.0), 'i': (11.2, 20.0), 'j': (11.2, 12.0), 'k': (16.0, 12.0), 'l': (16.0, 20.0),
        'wa': (7.5, 8.0), 'wb': (7.5, 24.0), 'ea': (24.5, 8.0), 'eb': (24.5, 24.0),
        'w1': (1.6, 8.0), 'w2': (1.6, 24.0), 'e1': (30.4, 8.0), 'e2': (30.4, 24.0),
        's1': (8.0, 1.6), 's2': (24.0, 1.6), 'n1': (8.0, 30.4), 'n2': (24.0, 30.4)},
        [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g'), ('g', 'h'), ('h', 'i'), ('i', 'j'), ('j', 'a'),
         ('j', 'k'), ('k', 'd'), ('i', 'l'), ('l', 'e'), ('j', 'wa'), ('i', 'wb'), ('d', 'ea'), ('e', 'eb'),
         ('wa', 'w1'), ('wb', 'w2'), ('ea', 'e1'), ('eb', 'e2'), ('wa', 's1'), ('ea', 's2'), ('wb', 'n1'), ('eb', 'n2')])
    secret(R, 16.0, 16.0, 0.0, 'The Positive',
           'Inside the cabinet at the middle of the hall the colours come back: red chair, green lamp, brown books. You had forgotten what they were. You stay longer than you meant to.', r=1.6)
    return finish(R, 'The Negative', weight=3, probe=(16.0, 8.0, 2.4), top=SPRING + RISE,
                  blurb='The shelves are white and the lampshades are black, and the lamps shine black light that somehow shows you everything. It is only the library, printed the wrong way.')


def arcade(R):
    """Arches between nave and aisles, with tiers of shelves above them under the vault."""
    pr0 = arch_profile(0, 3.0, 0, 3.0, 14)
    for y in ARCH_Y:
        for (a0, a1) in ((NX0 - 0.62, NX0 + 0.02), (NX1 - 0.02, NX1 + 0.62)):
            R.cut(prism([(p + y, q) for p, q in pr0], 'x', a0, a1, arch_mats(len(pr0), 'terrazzo', 'slate'), cap='slate'))
    for (x, s) in ((NX0, 1), (NX1, -1)):
        # a ledge and a rail over the arcade; an upper tier of cases behind it
        R.parts.add(box(min(x, x + s * 0.7), T, 4.62, max(x, x + s * 0.7), D - T, 4.75, 'walnut'))
        brass_rail(R, x + s * 0.66, T + 0.1, x + s * 0.66, D - T - 0.1, 4.75, h=0.9)
        sh(R, '+x' if s > 0 else '-x', x, T + 0.2, D - T - 0.2, z=4.75, rows=5, frame='walnut')
        # pilasters between the arches
        for y in [2.0 + 4.0 * k for k in range(8)]:
            R.parts.add(box(min(x, x + s * 0.12), y - 0.35, 0, max(x, x + s * 0.12), y + 0.35, 4.62, 'slate', skip=('-z',)))


def aisles(R, rs):
    """In each aisle: stacks reaching in from the outer wall, keeping clear of the doorways; a lamp over
    every alcove (white shade, black glow)."""
    ys = (2.2, 4.6, 11.4, 13.8, 16.2, 18.6, 20.8, 27.4, 29.8)
    for (xw, s) in ((T, 1), (W - T, -1)):
        for y in ys:
            x0, x1 = (xw, xw + 5.4) if s > 0 else (xw - 5.4, xw)
            sh(R, '+y', y + 0.01, x0 + 0.02, x1 - 0.02, rows=9, frame='walnut')
            sh(R, '-y', y - 0.01, x0 + 0.02, x1 - 0.02, rows=9, frame='walnut')
            R.parts.add(box(x0, y - 0.4, 3.9, x1, y + 0.4, 3.98, 'walnut'))
        for (a, b) in zip(ys, ys[1:]):
            if b - a > 3.0: continue
            yc = (a + b) / 2
            xc = xw + s * 2.2
            R.nocol.add(cyl(xc, yc, 3.0, AH, 0.012, 4, side='brass', caps=False))
            R.nocol.add(frustum(xc, yc, 2.95, 3.25, 0.34, 0.1, 12, 'white', inner='white'))
            R.light(cyl(xc, yc, 2.96, 3.0, 0.22, 10, side='e_black', top='e_black', bottom='e_black'))
            # the real light: a panel in the aisle ceiling
            R.light(box(xc - 0.5, yc - 0.5, AH - 0.02, xc + 0.5, yc + 0.5, AH - 0.01, 'e_panel'))
        # panels in the aisle ceiling by the doorways
        for yc in (8.0, 24.0):
            R.light(box(xw + s * 4.0 - 0.7, yc - 0.7, AH - 0.02, xw + s * 4.0 + 0.7, yc + 0.7, AH - 0.01, 'e_panel'))


def nave(R, rs):
    """Long tables down the nave, white-shaded lamps on them; black-glowing pendants down the vault; skylights."""
    for (y0, y1) in ((2.0, 11.4), (20.6, 30.0)):
        for xc in (11.9, 20.1):
            R.parts.add(table_geo(xc - 0.55, y0, xc + 0.55, y1, 0.78, 'walnut', top='white'))
            n = int((y1 - y0) / 2.4)
            for k in range(n):
                y = y0 + (k + 0.5) * (y1 - y0) / n
                white_lamp(R, xc, y, 0.78)
                for s in (-1, 1):
                    R.parts.add(chair_geo(xc + s * 0.9, y, math.pi if s > 0 else 0.0, frame='walnut', seat='white'))
    for y in (4.0, 8.0, 12.0, 20.0, 24.0, 28.0):
        R.nocol.add(cyl(16.0, y, 4.3, SPRING + RISE - 0.05, 0.015, 4, side='brass', caps=False))
        R.nocol.add(frustum(16.0, y, 4.0, 4.45, 0.62, 0.12, 16, 'white', inner='white'))
        R.light(cyl(16.0, y, 4.02, 4.07, 0.45, 12, side='e_black', top='e_black', bottom='e_black'))
    for y in (6.0, 26.0):
        R.cut(box(14.8, y - 3.0, SPRING + RISE - 0.35, 17.2, y + 3.0, SPRING + RISE + 0.2, 'plaster'))
        R.light(box(14.8, y - 3.0, SPRING + RISE + 0.1, 17.2, y + 3.0, SPRING + RISE + 0.12, 'e_sky'))
    # a globe on a stand at each end of the nave
    for y in (1.6, D - 1.6):
        R.parts.add(cyl(16.0, y, 0, 0.9, 0.12, 10, side='walnut', top='walnut'))
        R.parts.add(cyl(16.0, y, 0, 0.08, 0.5, 14, side='walnut', top='walnut'))
        R.nocol.add(sphere(16.0, y, 1.55, 0.62, 18, 9, 'slate'))
        R.nocol.add(ring(16.0, y, 1.5, 1.6, 0.64, 0.72, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.nocol.add(box(15.0, 2.4, 0, 17.0, 12.8, 0.012, 'slate'))
    R.nocol.add(box(15.0, 19.2, 0, 17.0, 29.6, 0.012, 'slate'))


def white_lamp(R, x, y, z):
    R.parts.add(cyl(x, y, z, z + 0.03, 0.09, 12, side='brass', top='brass'))
    R.parts.add(cyl(x, y, z + 0.03, z + 0.42, 0.014, 6, side='brass', caps=False))
    R.nocol.add(frustum(x, y, z + 0.38, z + 0.58, 0.24, 0.08, 12, 'white', inner='white'))
    R.light(cyl(x, y, z + 0.39, z + 0.41, 0.15, 10, side='e_black', top='e_black', bottom='e_black'))


def heart(R, rs):
    """The cabinet at the middle: bookcases on every outside face; the north one is a way in. Inside,
    a small warm room where the picture is the right way round."""
    for bx in ((HX0, HY0, HX1, HY0 + HT), (HX0, HY0, HX0 + HT, HY1), (HX1 - HT, HY0, HX1, HY1),
               (HX0, HY1 - HT, 15.2, HY1), (16.8, HY1 - HT, HX1, HY1)):
        R.parts.add(box(bx[0], bx[1], 0, bx[2], bx[3], HH, 'damask', top='walnut', skip=('-z',)))
    R.parts.add(box(15.2, HY1 - HT, 2.3, 16.8, HY1, HH, 'damask', top='walnut'))
    R.parts.add(box(HX0 + HT, HY0 + HT, HH - 0.3, HX1 - HT, HY1 - HT, HH, 'plaster', top='walnut'))
    R.parts.add(box(HX0 - 0.1, HY0 - 0.1, HH, HX1 + 0.1, HY1 + 0.1, HH + 0.15, 'walnut'))
    # outside cases, and the gap in the north face behind the false one
    sh(R, '-y', HY0, HX0 + 0.1, HX1 - 0.1, rows=7, frame='walnut')
    sh(R, '-x', HX0, HY0 + 0.1, HY1 - 0.1, rows=7, frame='walnut')
    sh(R, '+x', HX1, HY0 + 0.1, HY1 - 0.1, rows=7, frame='walnut')
    sh(R, '+y', HY1, HX0 + 0.1, 15.1, rows=7, frame='walnut')
    sh(R, '+y', HY1, 16.9, HX1 - 0.1, rows=7, frame='walnut')
    R.shelf(15.1, HY1, 0, 1.8, '+y', rows=7, frame='walnut', solid=False)
    # inside: an armchair, a green lamp, a little case of books, a rug, all their own colours
    ix0, iy0, ix1, iy1 = HX0 + HT, HY0 + HT, HX1 - HT, HY1 - HT
    R.nocol.add(box(ix0 + 0.6, iy0 + 0.5, 0, ix1 - 0.6, iy1 - 1.4, 0.012, 'carpet'))
    armchair(R, 15.0, 15.2, 0.0)
    R.spot('sit', 15.0, 15.2, 0.45, 0.0)
    R.parts.add(table_geo(15.8, 14.7, 16.6, 15.5, 0.62, 'walnut', top='leather'))
    desk_lamp(R, 16.2, 15.1, 0.62)
    open_book(R, 16.3, 14.95, 0.62, 0.3)
    sh(R, '+y', iy0, 16.9, ix1 - 0.1, rows=6, frame='oak')
    sh(R, '-x', ix1, iy0 + 0.2, iy1 - 1.6, rows=6, frame='oak')
    R.light(sphere(14.0, 17.4, 2.6, 0.08, 8, 4, 'e_amber'))
    R.nocol.add(cyl(14.0, 17.4, 2.66, HH - 0.3, 0.01, 4, side='brass', caps=False))
    R.spot('plaque', 16.0, 17.6, 0.0, math.pi / 2,
           text='Pinned inside the door: a photograph of this hall, printed the right way round. Somebody has written on it: DO NOT BELIEVE THE WHITE ONE.')
