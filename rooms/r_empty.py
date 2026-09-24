"""An Empty Room: bare plaster, far too big, one bulb on a long cord, and one book lying on the floor."""
from lib import *
from kit_a import *


def make():
    R = Room('empty', 1, 1, res=1024)
    shell(R, wall='plaster', floor='floor', ceil='plaster')
    # skirting and a picture rail: ordinary house trim, stretched round a room far too big for it

    for side in 'SNWE':
        for (a, b) in ((T, 8 - 1.55), (8 + 1.55, C - T)):
            if side == 'S': R.parts.add(box(a, T, 0, b, T + 0.03, 0.16, 'ivory', skip=('-z',)))
            if side == 'N': R.parts.add(box(a, C - T - 0.03, 0, b, C - T, 0.16, 'ivory', skip=('-z',)))
            if side == 'W': R.parts.add(box(T, a, 0, T + 0.03, b, 0.16, 'ivory', skip=('-z',)))
            if side == 'E': R.parts.add(box(C - T - 0.03, a, 0, C - T, b, 0.16, 'ivory', skip=('-z',)))
    for (x0, y0, x1, y1) in ((T, T, C - T, T + 0.05), (T, C - T - 0.05, C - T, C - T), (T, T, T + 0.05, C - T), (C - T - 0.05, T, C - T, C - T)):
        R.parts.add(box(x0, y0, 5.6, x1, y1, 5.66, 'ivory'))
        R.parts.add(box(x0, y0, TOP - 0.34, x1, y1, TOP - 0.1, 'ivory'))   # cornice
    # a light switch by the south door, at the height of a normal house
    R.parts.add(box(9.9, T, 1.25, 10.0, T + 0.015, 1.37, 'ivory'))
    R.parts.add(box(9.93, T + 0.015, 1.29, 9.97, T + 0.03, 1.33, 'ivory'))
    # a night-light plugged in low on the east wall
    R.parts.add(box(C - T - 0.03, 11.9, 0.28, C - T, 12.02, 0.4, 'ivory'))
    R.light(box(C - T - 0.05, 11.93, 0.3, C - T - 0.03, 11.99, 0.38, 'e_amber'))
    # the bulb: a ceiling rose, a long cord, a bare globe
    R.parts.add(cyl(8, 8, TOP - 0.15, TOP - 0.1, 0.14, 16, side='ivory', top='ivory', bottom='ivory'))
    bulb(R, 8, 8, 2.75, r=0.16, m='e_lamp')
    R.nocol.add(cyl(8, 8, 2.86, 2.98, 0.045, 10, side='brass', top='brass', bottom='brass'))
    # the book, alone, a little off true
    bx, by, a = 8.45, 8.75, 0.31
    R.parts.add(box(-0.12, -0.085, 0, 0.12, 0.085, 0.034, 'ivory', skip=('-z',)).xform(a, bx, by, 0))
    R.parts.add(box(-0.125, -0.088, 0.034, 0.125, 0.088, 0.041, 'oxblood', skip=()).xform(a, bx, by, 0))
    R.parts.add(box(-0.125, -0.088, 0.0, 0.125, 0.088, 0.004, 'oxblood', skip=('-z',)).xform(a, bx, by, 0))
    R.parts.add(box(-0.129, -0.088, 0.0, -0.12, 0.088, 0.041, 'oxblood', skip=('-z',)).xform(a, bx, by, 0))
    R.spot('read', bx - 0.6, by - 0.3, 0, a)
    navloop(R, [(2.5, 2.5), (8, 2.4), (13.5, 2.5), (13.6, 8), (13.5, 13.5), (8, 13.6), (2.5, 13.5), (2.4, 8)])
    c = R.navpt(7.0, 7.0); R.link(c, 1); R.link(c, 5); R.link(c, 3); R.link(c, 7)
    R.spot('probe', 6, 9, 1.7)
    R.meta.update(label='An Empty Room', weight=4,
                  blurb='Nothing here but a bulb and a book. Someone left the book. Nobody has come back for it.')
    R.meta['box'] = [[T, 0, T], [C - T, TOP - 0.1, C - T]]
    return tidy(R)
