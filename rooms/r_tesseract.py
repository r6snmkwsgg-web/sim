"""The Tesseract Study: a cubic study, as tall as it is wide, with a door in the middle of every wall. Go in
by the south door and you come in by the east one; go in by the north and you come in by the west; go out
by the east and you are outside the south door. (From outside the east and west doors are shut; from
inside, the south and north.) The
doors in the floor and the ceiling are painted on. The fifth door is behind a bookcase, and goes to a
plain corridor and a small room with the only window."""
from kit_h11 import *

W = D = 16.0
S0, S1 = 4.8, 11.2            # the study's inside
WT = 0.4                      # its walls
SH = 6.4                      # its ceiling (a cube)
DW_, DH_ = 1.4, 2.6           # its doors
NE = 10.0                     # the hidden corner (x, y > NE)
SDX0, SDX1 = 10.02, 10.77     # the fifth door, in the study's north wall


def make():
    R = Room('tesseract', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    ring(R)
    study(R)
    hidden(R)
    # the portals: in at the south door -> out of the east door; in at the north -> out of the west
    portal(R, P((8.0, S0 - WT, 0.0), (0, 1, 0), DW_, DH_), P((S1 + WT, 8.0, 0.0), (-1, 0, 0), DW_, DH_))
    portal(R, P((8.0, S1 + WT, 0.0), (0, -1, 0), DW_, DH_), P((S0 - WT, 8.0, 0.0), (1, 0, 0), DW_, DH_))
    # walkers: round the corridor, and into the study through each door
    o = navloop(R, [(2.3, 2.3), (8.0, 2.3), (13.7, 2.3), (13.7, 8.0), (13.7, 8.0), (8.0, 2.3), (2.3, 2.3), (2.3, 8.0), (2.3, 13.7), (8.0, 13.7), (2.3, 13.7), (2.3, 8.0)], close=False)
    st = [R.navpt(x, y) for (x, y) in ((6.2, 6.2), (9.8, 6.2), (9.8, 9.8), (6.2, 9.8))]
    R.link(st[0], st[1], st[2], st[3], st[0])
    secret(R, 13.9, 13.6, 0.0, 'The Room with the Window',
           'Behind the bookcase there is a plain corridor, and at the end of it a small room with a chair and, for the only time you can remember, a window. Outside it is a sky. You do not open it. You are not sure it would be kind to.', r=1.8)
    return done(R, 'The Tesseract Study', weight=3, probe=(8.0, 8.0, 3.0), top=7.4,
                blurb='A study with a door in every wall. You go out by one and come back in by another, and the desk has turned to face you. There is a door in the ceiling too, and one in the floor, but those are only painted on.')


def open_leaf(R, hx, hy, ang, w=DW_, h=DH_):
    """An open door leaf hinged at (hx, hy), standing out along plan angle ang."""
    g = Geo()
    g.add(obox(0, 0, w, 0, 0, h, 0.06, 'walnut'))
    for s in (-1, 1):
        for (z0, z1) in ((0.2, h * 0.45), (h * 0.52, h - 0.2)):
            g.add(obox(0.14, s * 0.035, w - 0.14, s * 0.035, z0, z1, 0.02, 'oak'))
    g.add(obox(w - 0.2, 0, w - 0.12, 0, 1.0, 1.06, 0.18, 'brass'))
    R.parts.add(g.xform(ang, hx, hy, 0))


def ring(R):
    """The corridor round the study: south and west all the way, north and east stopping short of the
    hidden corner."""
    for (x0, y0, x1, y1) in ((T, T, W - T, S0 - WT), (T, T, S0 - WT, D - T), (S1 + WT, T, W - T, NE - 0.4), (T, S1 + WT, NE - 0.4, D - T)):
        R.cut(box(x0 - 0.01, y0 - 0.01, 0, x1 + 0.01, y1 + 0.01, 7.4, 'tile', bottom='floor', top='plaster'))
    rows = 13
    # books on the outer walls, clear of the doorways
    sh(R, '+y', T, 0.9, 6.3, rows=rows, frame='walnut'); sh(R, '+y', T, 9.7, W - 0.9, rows=rows, frame='walnut')
    sh(R, '+x', T, 0.9, 6.3, rows=rows, frame='walnut'); sh(R, '+x', T, 9.7, D - 0.9, rows=rows, frame='walnut')
    sh(R, '-x', W - T, 0.9, 6.3, rows=rows, frame='walnut')
    sh(R, '-y', D - T, 0.9, 6.3, rows=rows, frame='walnut')
    # the dead ends of the north and east corridors
    shelf(R, NE - 0.4, S1 + WT + 0.2, 0, 13.3 - (S1 + WT + 0.2), '-x', rows=rows, frame='walnut', solid=False)
    R.cut(box(NE - 0.45, 12.0, 0, NE + 0.05, 13.0, 2.3, 'plaster', bottom='floor', top='plaster'))
    sh(R, '-y', NE - 0.4, S1 + WT + 0.2, 13.3, rows=rows, frame='walnut')
    # the study's outside: panelled, with the doors' surrounds and their leaves standing open
    for (face, x, y, hx, hy, la) in ((-math.pi / 2, 8.0, S0 - WT, 8.0 + DW_ / 2, S0 - WT, -math.pi / 2),
                                     (0.0, S1 + WT, 8.0, S1 + WT, 8.0 + DW_ / 2, 0.0),
                                     (math.pi / 2, 8.0, S1 + WT, 8.0 - DW_ / 2, S1 + WT, math.pi / 2),
                                     (math.pi, S0 - WT, 8.0, S0 - WT, 8.0 - DW_ / 2, math.pi)):
        R.parts.add(local(architrave(DW_, DH_, 'walnut', bw=0.22, depth=0.1), face, x, y, 0))
        if abs(math.sin(face)) > 0.5:
            open_leaf(R, hx + math.cos(face) * 0.05, hy + math.sin(face) * 0.05, la)
    # the east and west doors are shut on this side, in deep reveals (and the south and north ones are shut
    # on the inside): a portal must never be seen from behind
    for (sx, x) in ((1, S1 + WT), (-1, S0 - WT)):
        xa, xb = (x, x + sx * 0.85) if sx > 0 else (x + sx * 0.85, x)
        R.parts.add(box(xa, 8.0 - DW_ / 2 - 0.12, 0, xb, 8.0 - DW_ / 2, DH_ + 0.1, 'walnut'))
        R.parts.add(box(xa, 8.0 + DW_ / 2, 0, xb, 8.0 + DW_ / 2 + 0.12, DH_ + 0.1, 'walnut'))
        R.parts.add(box(xa, 8.0 - DW_ / 2, DH_, xb, 8.0 + DW_ / 2, DH_ + 0.1, 'walnut'))
        lx = x + sx * 0.85
        lf = door_leaf(DW_, DH_)
        R.parts.add(lf.xform(math.pi / 2 if sx > 0 else -math.pi / 2, lx, 8.0 - DW_ / 2 if sx > 0 else 8.0 + DW_ / 2, 0))
    # dado and sconces on the study's outer walls
    for (face, fx_, fy_) in ((-math.pi / 2, 0, -1), (0.0, 1, 0), (math.pi / 2, 0, 1), (math.pi, -1, 0)):
        for s in (-1, 1):
            cx, cy = 8.0 + fx_ * (3.2 + WT) + (s * 1.9 if fy_ else 0), 8.0 + fy_ * (3.2 + WT) + (s * 1.9 if fx_ else 0)
            sconce(R, cx, cy, 2.4, face)
    for (x, y) in ((2.3, 2.3), (2.3, 13.7), (13.7, 2.3), (2.3, 8.0), (8.0, 2.3), (13.7, 8.0), (8.0, 13.7)):
        pendant(R, x, y, 4.6, 7.4, r=0.28)
    for (x, y) in ((1.0, 1.0), (1.0, D - 1.0), (W - 1.0, 1.0)):
        lantern(R, x, y, 0.0)


def study(R):
    R.cut(box(S0, S0, 0, S1, S1, SH, 'damask', bottom='floor', top='plaster'))
    # the four doors
    for (x0, y0, x1, y1) in ((8.0 - DW_ / 2, S0 - WT - 0.02, 8.0 + DW_ / 2, S0 + 0.02), (8.0 - DW_ / 2, S1 - 0.02, 8.0 + DW_ / 2, S1 + WT + 0.02),
                             (S0 - WT - 0.02, 8.0 - DW_ / 2, S0 + 0.02, 8.0 + DW_ / 2), (S1 - 0.02, 8.0 - DW_ / 2, S1 + WT + 0.02, 8.0 + DW_ / 2)):
        R.cut(box(x0, y0, 0, x1, y1, DH_, 'walnut', bottom='floor', top='walnut'))
    # inside: a surround on every door, bookcases either side, a cornice
    for (face, x, y) in ((math.pi / 2, 8.0, S0), (-math.pi / 2, 8.0, S1), (0.0, S0, 8.0), (math.pi, S1, 8.0)):
        R.parts.add(local(architrave(DW_, DH_, 'walnut', bw=0.22, depth=0.1), face, x, y, 0))
    rows = 11
    a, b = S0 + 0.1, 8.0 - DW_ / 2 - 0.4
    c, d = 8.0 + DW_ / 2 + 0.4, S1 - 0.1
    sh(R, '+y', S0, a, b, rows=rows, frame='walnut'); sh(R, '+y', S0, c, d, rows=rows, frame='walnut')
    sh(R, '+x', S0, a, b, rows=rows, frame='walnut'); sh(R, '+x', S0, c, d, rows=rows, frame='walnut')
    sh(R, '-x', S1, a, b, rows=rows, frame='walnut'); sh(R, '-x', S1, c, d, rows=rows, frame='walnut')
    sh(R, '-y', S1, a, b, rows=rows, frame='walnut')
    for (sy, y) in ((1, S0), (-1, S1)):
        ya, yb = (y, y + sy * 0.45) if sy > 0 else (y + sy * 0.45, y)
        R.parts.add(box(8.0 - DW_ / 2 - 0.12, ya, 0, 8.0 - DW_ / 2, yb, DH_ + 0.1, 'walnut'))
        R.parts.add(box(8.0 + DW_ / 2, ya, 0, 8.0 + DW_ / 2 + 0.12, yb, DH_ + 0.1, 'walnut'))
        R.parts.add(box(8.0 - DW_ / 2, ya, DH_, 8.0 + DW_ / 2, yb, DH_ + 0.1, 'walnut'))
        ly = y + sy * 0.45
        lf = door_leaf(DW_, DH_)
        R.parts.add(lf.xform(0.0 if sy > 0 else math.pi, 8.0 - DW_ / 2 if sy > 0 else 8.0 + DW_ / 2, ly + (0.05 if sy > 0 else -0.05), 0))
    # the north-east bookcase is the fifth door
    shelf(R, d, S1, 0, d - c, '-y', rows=rows, frame='walnut', solid=False)
    R.cut(box(SDX0, S1 - 0.05, 0, SDX1, S1 + WT + 0.05, 2.2, 'tile', bottom='floor', top='plaster'))
    for (x0, y0, x1, y1) in ((S0, S0, S1, S0 + 0.25), (S0, S1 - 0.25, S1, S1), (S0, S0, S0 + 0.25, S1), (S1 - 0.25, S0, S1, S1)):
        R.parts.add(box(x0, y0, SH - 0.35, x1, y1, SH, 'plaster', skip=('+z',)))
    # coffers
    for k in (1, 2, 3):
        t = S0 + (S1 - S0) * k / 4
        R.parts.add(box(t - 0.1, S0, SH - 0.3, t + 0.1, S1, SH, 'walnut', skip=('+z',)))
        R.parts.add(box(S0, t - 0.1, SH - 0.3, S1, t + 0.1, SH, 'walnut', skip=('+z',)))
    # the painted doors
    painted_door(R, 8.0, 6.05, 0.0, 0.0, w=1.3, h=1.0, up=True)
    painted_door(R, 8.0, 8.0, SH, 0.0, w=1.2, h=1.2, up=False)
    # the desk, turned a little, the chair, a lamp, a rug
    rug(R, 6.0, 6.8, 10.0, 10.2)
    R.parts.add(ltable(7.0, 8.2, 9.0, 9.2, h=0.78, top='leather'))
    R.parts.add(box(7.1, 8.3, 0, 7.6, 9.1, 0.72, 'walnut', skip=('-z',)))
    R.parts.add(box(8.4, 8.3, 0, 8.9, 9.1, 0.72, 'walnut', skip=('-z',)))
    llamp(R, 7.5, 8.95, 0.78)
    open_book(R, 8.2, 8.6, 0.78, ang=0.1)
    book_pile(R, 8.7, 9.0, 0.78, 4, rng(3))
    R.parts.add(lchair(8.0, 7.55, math.pi / 2, seat='leather', back_h=1.1))
    R.spot('sit', 8.0, 7.55, 0.48, math.pi / 2)
    chandelier(R, 8.0, 8.0, 4.5, 0.7, n=8, chain=SH - 0.3)
    for (x, y) in ((S0 + 0.4, S0 + 0.4), (S1 - 0.4, S0 + 0.4), (S0 + 0.4, S1 - 0.4)):
        candlestick(R, x, y, 0.0, h=1.1)


def hidden(R):
    """Behind the fifth door: a plain corridor, then a small room with the only window."""
    R.cut(box(NE + 0.02, S1 + WT - 0.02, 0, NE + 1.0, 14.2, 2.6, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(NE + 0.02, 13.2, 0, 12.8, 14.2, 2.6, 'plaster', bottom='floor', top='plaster'))
    R.cut(box(12.4, 11.9, 0, W - T, D - T, 3.2, 'plaster', bottom='floor', top='plaster'))
    R.nocol.add(box(NE + 0.2, S1 + WT + 0.1, 0, NE + 0.8, 13.95, 0.01, 'carpet'))
    R.nocol.add(box(NE + 0.8, 13.45, 0, 12.6, 13.95, 0.01, 'carpet'))
    bulb(R, NE + 0.5, 12.6, 2.2, r=0.08, m='e_dim', top=2.6)
    window(R, 'E', 13.8, 1.0, 1.3, 1.1, depth=0.3, mull=1, trans=1)
    R.parts.add(lchair(14.9, 13.8, 0.0, seat='velvet'))
    R.spot('sit', 14.9, 13.8, 0.48, 0.0)
    R.parts.add(ltable(13.3, 14.7, 14.3, 15.5, top='leather'))
    llamp(R, 13.8, 15.2, 0.76, lit=True, m='e_amber')
    open_book(R, 13.8, 14.95, 0.76, ang=0.0)
    sh(R, '+y', 11.9, 12.6, W - 0.5, rows=4, frame='walnut')
    R.spot('plaque', 12.5, 15.2, 1.4, 0.0, text='The window does not open. It was never meant to.')
