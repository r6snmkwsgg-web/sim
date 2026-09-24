"""The Crawlspace: three doorways walled up, and the fourth leads only to a blank wall with a
hole at its foot, just big enough to crawl through. On the other side, a tiny dusty room: one
chair, one lamp, one book."""
from lib import *
from kit_d import *


def make():
    R = Room('secret_crawl', 1, 1, res=1024)
    shell(R, None, floor='slate', wall='tile', seal=('N', 'E', 'W'))
    R.meta['secret'] = True
    vd = 2.5                                   # depth of the arched vestibule behind the south door
    door_arch_cut(R, 'S', vd, floor='slate', wall='tile')
    # the hole: 1 m wide, 1.3 m high, through 0.6 m of wall, with a stone lintel
    hy0, hy1 = vd - 0.02, vd + 0.6
    R.cut(box(M - 0.5, hy0, 0, M + 0.5, hy1, 1.3, 'tile', bottom='slate', top='tile'))
    R.parts.add(box(M - 0.7, vd - 0.08, 1.3, M + 0.7, vd, 1.5, 'slate'))
    # the room: 3.4 x 3 m, low, bare plaster
    rx0, rx1, ry0, ry1, H = 6.3, 9.7, hy1 - 0.02, hy1 + 3.0, 2.3
    R.cut(box(rx0, ry0, 0, rx1, ry1, H, 'plaster', bottom='floor', top='plaster'))
    R.meta['box'] = [[rx0, 0, T], [rx1, 4.1, ry1]]
    # a dim bulb in the vestibule, over the hole
    R.nocol.add(box(M - 0.01, vd - 0.3, 3.2, M + 0.01, vd - 0.28, 4.05, 'iron', skip=('-z', '+z')))
    R.light(sphere(M, vd - 0.29, 3.12, 0.07, 8, 4, 'e_dim'))
    # one chair, one lamp, one book
    chair(R, 7.2, ry1 - 1.1, -0.4)
    book(R, 7.25, ry1 - 1.1, 0.5, 0.7, 'oxblood', t=0.05)
    R.parts.add(cyl(9.1, ry1 - 0.5, 0, 0.03, 0.14, 8, side='brass', top='brass', caps=True))
    R.parts.add(box(9.08, ry1 - 0.52, 0.03, 9.12, ry1 - 0.48, 1.35, 'brass', skip=('-z', '+z')))
    R.nocol.add(cyl(9.1, ry1 - 0.5, 1.3, 1.52, 0.2, 10, side='ivory', caps=False))
    R.light(cyl(9.1, ry1 - 0.5, 1.33, 1.37, 0.08, 8, side='e_amber', top='e_amber', bottom='e_amber'))
    # a dust sheet over something low in the corner
    R.parts.add(box(rx1 - 0.5, ry0 + 0.2, 0, rx1 - 0.05, ry0 + 1.1, 0.5, 'ivory', skip=('-z',)))
    R.spot('sit', 7.2, ry1 - 1.1, 0.5, -0.4)
    loop(R, [(M, 1.4), (M, vd - 0.5)], close=False)
    loop(R, [(M, ry0 + 0.6), (8.6, ry1 - 0.9), (7.6, ry1 - 0.5)], close=False)
    R.spot('probe', M, 1.6, 1.6)
    R.meta.update(label='The Crawlspace', weight=2,
                  blurb='You had to crawl to get in here. Someone else did too, once, and brought a chair, a lamp and a book, and never took them away.')
    return R
