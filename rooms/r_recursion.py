"""The Gallery of Frames: a picture gallery of gilded frames, and two of the pictures are of this gallery,
seen from where the other one hangs, each with the other in it, and so on down. Low in one wall hangs a
large empty frame, dark inside. You can climb into it. It lets you out, through a frame of its own, into a
small dark room hung with frames, which has a way back under a low bookcase."""
from kit_h11 import *

W = D = 16.0
GX1 = 14.5                    # the gallery's east wall (thick: the frames' recesses are in it)
SX1, SY1 = 3.9, 4.2           # the small room (x < SX1, y < SY1)
GH = 7.2
VW, VH, VZ = 2.0, 1.4, 1.1    # the two view frames
DW2, DH2, DZ2 = 1.8, 1.3, 0.45  # the low frame, and its twin in the small room
AY2, BY2 = 3.0, 2.1           # where they hang (y)


def make():
    R = Room('recursion', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    gallery(R)
    frames(R)
    small_room(R)
    # the views: the north frame looks out of the east frame; the east frame out of the north one
    portal(R, P((12.0, D - T, VZ), (0, 1, 0), VW, VH), P((GX1, 12.0, VZ), (-1, 0, 0), VW, VH))
    # the low frame opens into the small room (you come out of its twin facing west)
    portal(R, P((GX1, AY2, DZ2), (1, 0, 0), DW2, DH2), P((SX1, BY2, DZ2), (-1, 0, 0), DW2, DH2))
    navloop(R, [(2.5, 7.0), (2.5, 13.5), (8.0, 13.5), (12.5, 13.5), (12.5, 8.0), (12.5, 2.5), (8.0, 2.5), (7.0, 7.0)])
    secret(R, 1.9, 2.1, 0.0, 'The Room Inside the Frame',
           'You climbed into a picture and came out of another one, into a little dark room hung with frames of its own. Some of them are pictures of the gallery. One of them is a picture of this room, with you in it, looking at a picture.', r=1.6)
    return done(R, 'The Gallery of Frames', weight=3, probe=(8.0, 9.0, 2.2), top=GH,
                blurb='A gallery of gilded frames. Two of the pictures are of this gallery, from the other end, and in each of them hangs the other. Low in the far wall there is an empty frame, and it is dark inside, and it is big enough to climb into.')


def gallery(R):
    R.cut(box(T - 0.01, SY1 + 0.6, 0, GX1, D - T + 0.01, GH, 'tile', bottom='floor', top='plaster'))
    R.cut(box(SX1 + 1.3, T - 0.01, 0, GX1, SY1 + 0.62, GH, 'tile', bottom='floor', top='plaster'))
    # the east doorway carried through the thick wall
    tunnel_x(R, 8.0, GX1 - 0.05, W - T + 0.02, floor='floor', wall='tile')
    # coffered ceiling with a lantern light, dado rail, green-lamped tables
    for k in range(1, 5):
        t = 16.0 * k / 5
        R.parts.add(box(t - 0.12, T, GH - 0.35, t + 0.12, D - T, GH, 'plaster', skip=('+z',)))
        R.parts.add(box(T, t - 0.12, GH - 0.35, GX1, t + 0.12, GH, 'plaster', skip=('+z',)))
    R.light(box(6.0, 8.0, GH - 0.03, 10.0, 12.0, GH, 'e_sky'))
    for (x0, y0, x1, y1) in ((T, SY1 + 0.6, T + 0.05, D - T), (T, D - T - 0.05, GX1, D - T), (GX1 - 0.05, T, GX1, D - T), (SX1 + 1.3, T, GX1, T + 0.05)):
        R.nocol.add(box(x0, y0, 0.95, x1, y1, 1.0, 'walnut'))
        R.nocol.add(box(x0, y0, 0.0, x1, y1, 0.18, 'walnut'))
    for (x, y) in ((8.0, 10.0), (8.0, 6.3)):
        R.parts.add(ltable(x - 1.4, y - 0.5, x + 1.4, y + 0.5, top='leather'))
        for dx in (-0.8, 0.8):
            llamp(R, x + dx, y, 0.76)
        for dx in (-0.8, 0.8):
            R.nocol.add(lchair(x + dx, y - 0.9, math.pi / 2)); R.nocol.add(lchair(x + dx, y + 0.9, -math.pi / 2))
    # a long bookcase on the west wall (and the false low one that hides the way back)
    sh(R, '+x', T, SY1 + 0.9, 6.3, rows=14, frame='walnut')
    sh(R, '+x', T, 9.7, D - 0.6, rows=14, frame='walnut')
    shelf(R, 0.9, SY1 + 0.6, 0, 1.5, '+y', rows=3, frame='walnut', solid=False)
    for (x, y) in ((4.0, 4.0 + 5.0), (12.0, 4.0 + 5.0), (8.0, 14.0), (4.0, 14.0)):
        pendant(R, x, y, 4.6, GH, r=0.3)
    lantern(R, 13.8, 5.2, 0.0)
    lantern(R, 1.0, D - 1.0, 0.0)


def hang(R, x, y, face, w, h, z, m='gilt', bw=0.16, pic=None, crest=0.0):
    """A gilded frame on a wall (face: the way it looks), optionally with a painted panel inside."""
    R.parts.add(local(frame_geo(w, h, bw=bw, depth=0.1, m=m, crest=crest), face, x, y, z))
    if pic:
        c, s = math.cos(face), math.sin(face)
        px, py = x + c * 0.02, y + s * 0.02
        g = local(box(-w / 2, 0.0, 0.0, w / 2, 0.02, h, pic), face, px, py, z)
        R.nocol.add(g)


def frames(R):
    # the two view frames (portals) and the low empty frame, cut into the walls behind
    R.cut(box(12.0 - VW / 2, D - T - 0.02, VZ, 12.0 + VW / 2, D - T + 0.12, VZ + VH, 'black'))
    R.cut(box(GX1 - 0.02, 12.0 - VW / 2, VZ, GX1 + 0.12, 12.0 + VW / 2, VZ + VH, 'black'))
    hang(R, 12.0, D - T, -math.pi / 2, VW, VH, VZ, bw=0.22, crest=0.6)
    hang(R, GX1, 12.0, math.pi, VW, VH, VZ, bw=0.22, crest=0.6)
    recess(R, (GX1, AY2, DZ2), (1, 0, 0), DW2, DH2, depth=1.0, floor='oak', wall='black', top='black', back=0.02)
    hang(R, GX1, AY2, math.pi, DW2, DH2, DZ2, bw=0.26, crest=0.8)
    # a step up to it
    R.parts.add(box(GX1 - 0.5, AY2 - DW2 / 2, 0, GX1, AY2 + DW2 / 2, 0.22, 'walnut', top='oak'))
    # ordinary pictures: dark paintings in gilt, in rows
    pics = [('green', 1.2, 1.6), ('oxblood', 0.9, 1.2), ('damask', 1.6, 1.1), ('velvet', 0.8, 1.0), ('slate', 1.1, 1.4), ('leather', 1.4, 1.0)]
    k = 0
    for (x, y, face) in ((2.2, D - T, -math.pi / 2), (4.6, D - T, -math.pi / 2), (14.1, D - T, -math.pi / 2),
                         (GX1, 14.6, math.pi), (GX1, 5.1, math.pi), (11.0, T, math.pi / 2), (13.2, T, math.pi / 2)):
        m, w, h = pics[k % len(pics)]; k += 1
        hang(R, x, y, face, w, h, 1.3 if k % 2 else 1.6, pic=m)
        hang(R, x, y, face, w * 0.7, h * 0.7, 4.2, pic=pics[(k + 2) % len(pics)][0])
    # big pictures high up on the view walls
    hang(R, 12.0, D - T, -math.pi / 2, 1.8, 1.6, 3.6, pic='damask', crest=0.5)
    hang(R, GX1, 12.0, math.pi, 1.8, 1.6, 3.6, pic='damask', crest=0.5)


def small_room(R):
    R.cut(box(T - 0.01, T - 0.01, 0, SX1, SY1, 3.0, 'damask', bottom='floor', top='plaster'))
    recess(R, (SX1, BY2, DZ2), (1, 0, 0), DW2, DH2, depth=1.0, floor='oak', wall='black', top='black', back=0.02)
    hang(R, SX1, BY2, math.pi, DW2, DH2, DZ2, bw=0.26, crest=0.8)
    R.parts.add(box(SX1 - 0.5, BY2 - DW2 / 2, 0, SX1, BY2 + DW2 / 2, 0.22, 'walnut', top='oak'))
    # the crawl back to the gallery, under the low false bookcase
    R.cut(box(1.0, SY1 - 0.02, 0, 2.3, SY1 + 0.62, 1.25, 'tile', bottom='floor', top='tile'))
    # frames all round, small, some over others
    pics = ('green', 'oxblood', 'slate', 'velvet', 'leather')
    k = 0
    for (x, y, face) in ((0.9, SY1, -math.pi / 2), (3.1, SY1, -math.pi / 2), (T, 1.0, 0.0), (T, 2.2, 0.0), (T, 3.4, 0.0),
                         (1.2, T, math.pi / 2), (2.6, T, math.pi / 2), (SX1, 0.8, math.pi), (SX1, 3.6, math.pi)):
        for z in (1.5, 2.3):
            if y == SY1 and z < 1.6 and x < 2.4: continue
            hang(R, x, y, face, 0.42, 0.52, z, bw=0.07, pic=pics[k % 5]); k += 1
    pendant(R, 2.0, 2.2, 2.2, 3.0, r=0.2, m='e_lamp')
    lantern(R, 3.3, 0.8, 0.0)
    R.parts.add(lchair(1.9, 2.0, 0.0))
    R.spot('sit', 1.9, 2.0, 0.48, 0.0)
    candles(R, [(0.8, 0.8, 0.0), (0.95, 0.7, 0.0)], rng(9), 0.3, 0.6, 0.03, 0.05)
    R.spot('plaque', 1.9, 0.6, 1.4, math.pi / 2, text='Please do not climb into the pictures.')
