"""The Last Reader: a great dark reading hall, vaulted, every lamp out but one. At that one table a chair
is pulled out, a book lies open, a cup of tea is still steaming. Whoever was reading has just got up.
The bookcase behind the table is a door, and behind it is the reader's own small room: a bed, a kettle
on the hob, a coat on the hook."""
from kit_h10 import *

W = D = 32.0
YN = 27.6                         # the north wall; the reader's room is behind it, in the west
NX0, NX1 = 10.0, 22.0             # the nave between the arcades
JAMB, RISE = 4.4, 3.0
AJ, AR = 3.4, 1.9                 # the aisles' vaults
LX0, LX1, LY0, LY1 = 2.9, 6.1, 25.2, 26.1     # the lit table
FX0, FX1 = 3.9, 5.1               # the false bookcase behind it
KX0, KX1, KY0, KY1, KH = 0.6, 6.2, YN + 0.3, D - T - 0.05, 3.1   # the reader's room


def make():
    R = Room('lastreader', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    vault_cut(R, 'y', 16.0, NX1 - NX0 + 0.04, T - 0.02, YN, 0.0, JAMB, rise=RISE, m='slate', floor='terrazzo', wall='tile')
    for c, w in (((T + NX0) / 2, NX0 - T + 0.3), ((NX1 + W - T) / 2, W - T - NX1 + 0.3)):
        vault_cut(R, 'y', c, w, T - 0.02, YN, 0.0, AJ, rise=AR, m='slate', floor='terrazzo', wall='tile')
    ribs(R, 'y', 16.0, NX1 - NX0, [4.0 * k for k in range(1, 7)], 0.0, JAMB, rise=RISE, d=0.3, t=0.35)
    tunnel_y(R, 8.0, YN - 0.05, D - T - 0.5, floor='terrazzo')
    tunnel_y(R, 24.0, YN - 0.05, D - T - 0.5, floor='terrazzo')
    arcades(R)
    walls(R)
    tables(R)
    reader(R)
    room(R)
    navloop(R, [(16.0, 2.2), (16.0, 12.0), (16.0, 25.8), (22.0, 26.2), (29.8, 24.0), (29.8, 16.0), (29.8, 8.0), (24.0, 2.2)])
    a, e, b, c, d = R.navpt(10.0, 26.4), R.navpt(8.0, 23.2), R.navpt(2.2, 22.0), R.navpt(2.2, 12.0), R.navpt(8.0, 2.2)
    R.link(2, a, e, b, c, d, 0)
    secret(R, 3.4, 29.6, 0.0, "The Reader's Room",
           'Behind the bookcase is the reader\'s room: a narrow bed, a coat on the hook, the kettle just off the boil. Everything is ready for them to come back. You have the feeling it would be rude to wait.')
    fx(R, 'afterimage', [NX0 + 0.5, 1.0, 0.0, NX1 - 0.5, YN - 1.0, 3.0])
    fx(R, 'dust', [LX0 - 1.0, LY0 - 1.5, 0.6, LX1 + 1.0, LY1 + 1.0, 3.0])
    return done(R, 'The Last Reader', weight=4, probe=(16.0, 12.0, 2.6),
                blurb='Every lamp in the hall is out but one. Under it a book lies open, a chair is pushed back, the tea is still hot. You are sure, quite sure, that you are the last reader. Then who was this?')


# ---------------------------------------------------------------------------
def arcades(R):
    for x in (NX0, NX1):
        for k in range(1, 7):
            y = 4.0 * k
            g = Geo()
            g.add(box(x - 0.45, y - 0.45, 0, x + 0.45, y + 0.45, 0.45, 'tile', skip=('-z',)))
            for (dx, dy) in ((0, 0), (0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3)):
                g.add(cyl(x + dx, y + dy, 0.45, AJ, 0.16 if (dx or dy) else 0.3, 10, side='tile', caps=False))
            g.add(box(x - 0.5, y - 0.5, AJ - 0.35, x + 0.5, y + 0.5, AJ, 'tile', skip=('+z',)))
            R.parts.add(g)
            if k % 2: sconce(R, x + (0.52 if x < 16 else -0.52), y, 2.8, 0.0 if x < 16 else math.pi, m='e_candle', r=0.05)
        R.parts.add(box(x - 0.3, T, AJ, x + 0.3, YN, JAMB, 'tile'))
        # arches between the piers (a thin arched screen from the pier tops up to the vault spring)
        for k in range(0, 7):
            y0, y1 = 4.0 * k + (0.5 if k else T), 4.0 * (k + 1) - 0.5 if k < 6 else YN
            if y1 - y0 < 1.0: continue
            R.parts.add(box(x - 0.28, y0, AJ - 0.05, x + 0.28, y1, AJ + 0.15, 'tile'))


def walls(R):
    rows = 8
    for (x, face) in ((T, '+x'), (W - T, '-x')):
        for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, YN - 0.3)):
            sh(R, face, x, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, FX0 - 0.05), (FX1 + 0.05, 6.1)):
        sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
    false_case(R, FX1, YN, FX1 - FX0, '-y', rows=rows, frame='walnut', h=2.3, depth=0.4, floor='terrazzo')
    R.cut(box(FX0 + 0.05, YN - 0.1, 0, FX1 - 0.05, KY0 + 0.05, 2.3, 'wood', bottom='floor', top='wood'))
    for (a, b) in ((NX1 + 0.6, 22.1), (25.9, W - 0.6)):
        sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, 6.1), (25.9, W - 0.6), (9.9, 14.6), (17.4, 22.1)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
    sh(R, '-y', YN, NX0 + 0.1, 14.6, rows=rows, frame='walnut')
    sh(R, '-y', YN, 17.4, NX1 - 0.1, rows=rows, frame='walnut')
    # tall windows at both ends of the nave: moonlight, the only light apart from the lamp
    window(R, 'N', 16.0, 2.6, 1.6, 2.8, depth=0.3, em='e_moon', frame='iron', mull=1, trans=3, wallpos=YN)
    window(R, 'S', 16.0, 2.6, 1.6, 2.8, depth=0.3, em='e_moon', frame='iron', mull=1, trans=3)
    # a black-and-cream band down the nave floor
    for x in (14.2, 17.8):
        R.nocol.add(box(x - 0.08, T, 0, x + 0.08, YN, 0.008, 'slate', skip=('-z',)))


def table_row(R, g, x0, x1, y0, y1, rs, along='y'):
    g.add(ltable(x0, y0, x1, y1, 0.78, 'walnut', top='leather'))
    if along == 'y':
        n = int((y1 - y0) / 1.1)
        for k in range(n):
            y = y0 + (y1 - y0) * (k + 0.5) / n
            for (x, a) in ((x0 - 0.3, 0.0), (x1 + 0.3, math.pi)):
                g.add(lchair(x, y, a, frame='walnut', seat='green', back_h=1.0))
            if k % 2 == 0:
                llamp(R, (x0 + x1) / 2, y, 0.78, math.pi / 2, lit=False)
    else:
        n = int((x1 - x0) / 1.1)
        for k in range(n):
            x = x0 + (x1 - x0) * (k + 0.5) / n
            for (y, a) in ((y0 - 0.3, math.pi / 2), (y1 + 0.3, -math.pi / 2)):
                g.add(lchair(x, y, a, frame='walnut', seat='green', back_h=1.0))
            if k % 2 == 0:
                llamp(R, x, (y0 + y1) / 2, 0.78, 0.0, lit=False)


def tables(R):
    rs = rng(14)
    g = Geo()
    for (x0, x1) in ((12.2, 13.3), (18.7, 19.8)):
        for (y0, y1) in ((3.4, 10.6), (13.4, 20.6)):
            table_row(R, g, x0, x1, y0, y1, rs)
    for (x0, x1) in ((5.0, 6.1), (25.9, 27.0)):
        for (y0, y1) in ((3.4, 6.6), (9.4, 14.6), (17.4, 21.6)):
            table_row(R, g, x0, x1, y0, y1, rs)
    R.parts.add(g)
    # a few books left on the dark tables
    bk = Geo()
    for k in range(10):
        x, y = rs.choice(((12.75, rs.uniform(4, 20)), (19.25, rs.uniform(4, 20)), (5.55, rs.uniform(4, 21))))
        book_row_flat(bk, x, y, 0.78, rs.uniform(0, 3), rs, rs.randint(1, 3))
    R.nocol.add(bk)


def reader(R):
    """The one lit table: the chair pushed out, the book open, the tea."""
    R.parts.add(ltable(LX0, LY0, LX1, LY1, 0.78, 'walnut', top='leather'))
    llamp(R, LX0 + 0.6, (LY0 + LY1) / 2 + 0.1, 0.78, 0.15, lit=True, m='e_reader')
    # the chair, pushed back and turned
    R.parts.add(lchair_legs(LX0 + 1.9, LY0 - 1.45, math.pi / 2 - 0.5, frame='walnut', seat='green'))
    R.spot('sit', LX0 + 1.9, LY0 - 1.45, 0.48, math.pi / 2 - 0.5)
    for (x, a) in ((LX0 + 0.8, math.pi / 2), (LX1 - 0.6, math.pi / 2)):
        R.parts.add(lchair(x, LY0 - 0.3, a, frame='walnut', seat='green', back_h=1.0))
    # the open book
    ob = box(-0.24, -0.17, 0, 0.0, 0.17, 0.03, 'ivory', sides='leather'); ob.add(box(0.0, -0.17, 0, 0.24, 0.17, 0.03, 'ivory', sides='leather'))
    ob.add(box(-0.2, -0.13, 0.03, -0.02, 0.13, 0.045, 'ivory')); ob.add(box(0.02, -0.13, 0.03, 0.2, 0.13, 0.045, 'ivory'))
    R.nocol.add(ob.xform(-0.12, LX0 + 1.75, LY0 + 0.4, 0.78))
    R.spot('read', LX0 + 1.75, LY0 + 0.4, 0.8, math.pi / 2)
    # the cup of tea on its saucer, steam rising
    cx, cy = LX0 + 2.45, LY0 + 0.45
    R.nocol.add(hdisc(cx, cy, 0.783, 0.08, 10, 'ivory'))
    R.nocol.add(cyl(cx, cy, 0.785, 0.86, 0.045, 10, side='ivory', bottom='ivory', caps=False))
    R.nocol.add(hdisc(cx, cy, 0.845, 0.043, 10, 'food'))
    R.nocol.add(beam((cx + 0.045, cy, 0.84), (cx + 0.075, cy, 0.815), 0.012, 'ivory'))
    rs = rng(3)
    for k in range(3):
        streamer(R, cx + rs.uniform(-0.02, 0.02), cy + rs.uniform(-0.02, 0.02), 1.1 + k * 0.05, 0.25 + k * 0.03, rs, m='bed', r=0.018, turns=1.2, w=0.006)
    # a stack of books by the lamp, spectacles folded on top
    book_row_flat(ob := Geo(), LX1 - 0.6, LY0 + 0.45, 0.78, 0.2, rs, 5)
    R.nocol.add(ob)
    rug(R, LX0 - 0.6, LY0 - 1.6, LX1 + 0.6, LY1 + 0.5, m='carpet', border='gilt')


def room(R):
    """Behind the bookcase: the reader's own room."""
    R.cut(box(KX0, KY0, 0, KX1, KY1, KH, 'damask', bottom='floor', top='plaster'))
    cot(R, KX0 + 0.1, KY1 - 1.0, KX0 + 2.1, KY1 - 0.08, 0.0, h=0.5, frame='walnut', blanket='green', pillow='bed')
    # the hob with a kettle, glowing
    R.parts.add(box(KX1 - 0.8, KY1 - 0.7, 0, KX1 - 0.05, KY1 - 0.05, 0.85, 'iron'))
    R.light(box(KX1 - 0.7, KY1 - 0.72, 0.15, KX1 - 0.15, KY1 - 0.71, 0.35, 'e_flame'))
    R.nocol.add(cyl(KX1 - 0.42, KY1 - 0.38, 0.85, 1.05, 0.12, 10, side='bronze', top='bronze'))
    R.nocol.add(beam((KX1 - 0.3, KY1 - 0.38, 0.98), (KX1 - 0.18, KY1 - 0.38, 1.06), 0.03, 'bronze'))
    # a coat on the hook by the door, an armchair, a shelf of their own books, a candle, a small window
    R.nocol.add(box(FX1 + 0.3, KY0 + 0.02, 1.75, FX1 + 0.36, KY0 + 0.12, 1.8, 'brass'))
    from kit_h2 import hexa
    x, y = FX1 + 0.33, KY0 + 0.2
    R.nocol.add(hexa([(x - 0.28, y - 0.06, 0.7), (x + 0.28, y - 0.06, 0.7), (x + 0.28, y + 0.06, 0.7), (x - 0.28, y + 0.06, 0.7),
                      (x - 0.18, y - 0.05, 1.75), (x + 0.18, y - 0.05, 1.75), (x + 0.18, y + 0.05, 1.75), (x - 0.18, y + 0.05, 1.75)], 'coat1'))
    armchair(R, KX0 + 3.3, KY1 - 0.7, -math.pi / 2)
    sh(R, '+x', KX0, KY0 + 0.3, KY1 - 1.2, rows=6, frame='oak', depth=0.26)
    R.parts.add(box(KX0 + 2.3, KY1 - 0.5, 0, KX0 + 2.8, KY1 - 0.05, 0.55, 'walnut'))
    st, fl = lcandle(KX0 + 2.55, KY1 - 0.3, 0.55, 0.14, 0.025)
    R.nocol.add(st); R.light(fl)
    window(R, 'N', KX0 + 2.55, 1.2, 0.7, 1.1, depth=0.15, em='e_moon', frame='iron', mull=1, trans=1, wallpos=KY1)
    rug(R, KX0 + 1.5, KY0 + 0.6, KX0 + 4.4, KY0 + 2.2, m='velvet', border='oxblood')
    a, b = R.navpt(FX0 + 0.5, KY0 + 0.8), R.navpt(KX0 + 2.0, KY0 + 1.2)
    R.link(a, b)
