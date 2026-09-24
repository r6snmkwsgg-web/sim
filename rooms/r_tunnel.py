"""The Tunnel: a low barrel vault lined with books, a lamp every two metres, all the way to a point.
Two cross vaults lead off to the side doorways."""
from lib import *
from kit_e import *


def make():
    R = Room('tunnel', 2, 1, res=1024)
    R.sockets()
    W, D = R.W, R.D
    cy = D / 2
    tw, tj, tr = 4.4, 2.45, 0.8                 # main tunnel: width, wall height, rise of the vault (crown 3.25)
    sw = 4.0                                    # cross vaults
    pr = arch_profile(cy, tw, 0, tj, 32, rise=tr)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'floor', 'tile')))
    for x in (8.0, 24.0):
        ps = arch_profile(x, sw, 0, tj, 32, rise=tr)
        R.cut(prism(ps, 'y', T - 0.02, D - T + 0.02, arch_mats(len(ps), 'floor', 'tile')))
        # a small lantern over each crossing
        R.cut(cyl(x, cy, tj + tr - 0.3, tj + tr + 1.6, 0.9, 32, side='plaster', top='plaster', bottom='plaster'))
        R.light(cyl(x, cy, tj + tr + 1.5, tj + tr + 1.55, 0.9, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    # niches half way along, each with a bench
    for (y0, y1, face) in ((cy - tw / 2 - 1.0, cy - tw / 2 + 0.05, math.pi / 2), (cy + tw / 2 - 0.05, cy + tw / 2 + 1.0, -math.pi / 2)):
        pn = arch_profile(16.0, 2.6, 0, 1.6, 20)
        R.cut(prism(pn, 'y', y0, y1, arch_mats(len(pn), 'floor', 'tile')))
        yb = y0 + 0.02 if face > 0 else y1 - 0.5
        bench(R, 14.9, yb, 17.1, yb + 0.48, m='walnut', seat='velvet', spots=False)
        for x in (15.4, 16.6):
            R.spot('sit', x, yb + 0.24, 0.45, face)
    # books: both walls of the main tunnel, both walls of the cross vaults
    ya, yb = cy - tw / 2, cy + tw / 2
    for (a, b) in ((1.9, 6.0 - 0.02), (10.0 + 0.02, 14.6), (17.4, 22.0 - 0.02), (26.0 + 0.02, W - 1.9)):
        R.shelf(a, ya, 0, b - a, '+y', rows=5, frame='walnut')
        R.shelf(b, yb, 0, b - a, '-y', rows=5, frame='walnut')
    for x in (8.0, 24.0):
        xa, xb = x - sw / 2, x + sw / 2
        for (a, b) in ((2.2, ya - 0.02), (yb + 0.02, D - 2.2)):
            R.shelf(xa, b, 0, b - a, '+x', rows=5, frame='walnut')
            R.shelf(xb, a, 0, b - a, '-x', rows=5, frame='walnut')
    # the lamps: one every two metres down the crown of every vault
    zc = tj + tr
    for k in range(16):
        x = 1.0 + 2.0 * k
        if abs(x - 8.0) < 1.5 or abs(x - 24.0) < 1.5: continue
        globe(R, x, cy, zc - 0.62, zc, r=0.13)
    for x in (8.0, 24.0):
        for y in (1.2, 3.2, 5.2, D - 5.2, D - 3.2, D - 1.2):
            globe(R, x, y, zc - 0.62, zc, r=0.13)
    # low amber lights at the foot of the shelves, which stay on at night
    for k in range(8):
        x = 3.0 + 4.0 * k
        if abs(x - 8.0) < 2.5 or abs(x - 24.0) < 2.5 or abs(x - 16.0) < 1.5: continue
        R.light(box(x - 0.18, ya + 0.37, 0.04, x + 0.18, ya + 0.4, 0.1, 'e_amber'))
        R.light(box(x - 0.18, yb - 0.4, 0.04, x + 0.18, yb - 0.37, 0.1, 'e_amber'))
    R.parts.add(box(1.0, cy - 0.6, 0, W - 1.0, cy + 0.6, 0.012, 'carpet', skip=('-z',)))
    # walkers
    m = loop(R, [(1.2, cy), (8.0, cy - 0.9), (16.0, cy - 0.9), (24.0, cy - 0.9), (W - 1.2, cy), (24.0, cy + 0.9), (16.0, cy + 0.9), (8.0, cy + 0.9)])
    for (x, i, j) in ((8.0, 1, 7), (24.0, 3, 5)):
        s = R.navpt(x, 1.2); n = R.navpt(x, D - 1.2)
        R.link(s, m[i]); R.link(m[j], n)
    R.spot('probe', 16.0, cy, 1.7)
    R.meta.update(label='The Tunnel', weight=7,
                  blurb='A lamp every two metres, and the lamps go on until they meet. The books on either side are within reach the whole way, which somehow makes it worse.')
    R.meta['box'] = [[T, 0, T], [W - T, zc + 1.6, D - T]]
    return R
