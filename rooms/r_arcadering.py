"""The Arcade Loop: a vaulted, arched corridor that goes round and round a solid block of stone. The block
has books set into its outside walls; there is no way in. The outer walls have niches with candles."""
from lib import *
from kit_c import *


def make():
    R = Room('arcadering', 1, 1, res=1024)
    R.sockets(floor='mosaic', wall='tile')
    b0, b1 = 4.5, C - 4.5                  # the sealed block
    w = b0 - T
    c0, c1 = (T + b0) / 2, (C - T + b1) / 2
    js = 3.0                               # vault springing
    for (axis, c) in (('x', c0), ('x', c1), ('y', c0), ('y', c1)):
        pr = arch_profile(c, w + 0.04, 0, js, 20)
        R.cut(prism(pr, axis, T - 0.02, C - T + 0.02, arch_mats(len(pr), 'mosaic', 'tile')))
    r = (w + 0.04) / 2
    # transverse arches (ribs on pilasters) across the corridor
    for p in (b0 + 0.1, 6.15, C - 6.15, b1 - 0.1):
        for (axis, c, lo, hi) in (('x', c0, T, b0), ('x', c1, b1, C - T), ('y', c0, T, b0), ('y', c1, b1, C - T)):
            R.parts.add(arch_ring(axis, p - 0.18, p + 0.18, c, w + 0.04 - 0.44, js, 0.24, m='tile', segs=8))
            for (q0, q1) in ((lo - 0.01, lo + 0.2), (hi - 0.2, hi + 0.01)):
                if axis == 'x': R.parts.add(box(p - 0.18, q0, 0, p + 0.18, q1, js, 'tile', skip=('-z',)))
                else: R.parts.add(box(q0, p - 0.18, 0, q1, p + 0.18, js, 'tile', skip=('-z',)))
    # blind arches in the block, three a side, each holding a bookcase
    nw, nd, nj = 1.9, 0.6, 2.4
    npr = arch_profile(0, nw, 0, nj, 16)
    for off in (-2.3, 0.0, 2.3):
        m = C / 2 + off
        R.cut(prism([(p + m, q) for p, q in npr], 'y', b0 - 0.05, b0 + nd, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(m + nw / 2 - 0.06, b0 + nd, 0, nw - 0.12, '-y', rows=5, frame='oak', sides=False, back=False)
        R.cut(prism([(p + m, q) for p, q in npr], 'y', b1 - nd, b1 + 0.05, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(m - nw / 2 + 0.06, b1 - nd, 0, nw - 0.12, '+y', rows=5, frame='oak', sides=False, back=False)
        R.cut(prism([(p + m, q) for p, q in npr], 'x', b0 - 0.05, b0 + nd, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(b0 + nd, m - nw / 2 + 0.06, 0, nw - 0.12, '-x', rows=5, frame='oak', sides=False, back=False)
        R.cut(prism([(p + m, q) for p, q in npr], 'x', b1 - nd, b1 + 0.05, arch_mats(len(npr), 'tile', 'tile')))
        R.shelf(b1 - nd, m + nw / 2 - 0.06, 0, nw - 0.12, '+x', rows=5, frame='oak', sides=False, back=False)
    # shallow niches in the outer walls either side of each door: a candle on a ledge over a few books
    ow, od, oj = 1.3, 0.26, 2.0
    opr = arch_profile(0, ow, 0.0, oj, 14)
    for m in (2.45, C - 2.45):
        for side in 'SNWE':
            if side == 'S': R.cut(prism([(p + m, q) for p, q in opr], 'y', T - od, T + 0.05, arch_mats(len(opr), 'tile', 'tile')))
            if side == 'N': R.cut(prism([(p + m, q) for p, q in opr], 'y', C - T - 0.05, C - T + od, arch_mats(len(opr), 'tile', 'tile')))
            if side == 'W': R.cut(prism([(p + m, q) for p, q in opr], 'x', T - od, T + 0.05, arch_mats(len(opr), 'tile', 'tile')))
            if side == 'E': R.cut(prism([(p + m, q) for p, q in opr], 'x', C - T - 0.05, C - T + od, arch_mats(len(opr), 'tile', 'tile')))
            L = ow - 0.1
            if side == 'S': R.shelf(m - L / 2, T - od, 0, L, '+y', rows=3, row_h=0.36, depth=0.3, frame='walnut', sides=False, back=False); cx_, cy_ = m, T - od + 0.15
            if side == 'N': R.shelf(m + L / 2, C - T + od, 0, L, '-y', rows=3, row_h=0.36, depth=0.3, frame='walnut', sides=False, back=False); cx_, cy_ = m, C - T + od - 0.15
            if side == 'W': R.shelf(T - od, m + L / 2, 0, L, '+x', rows=3, row_h=0.36, depth=0.3, frame='walnut', sides=False, back=False); cx_, cy_ = T - od + 0.15, m
            if side == 'E': R.shelf(C - T + od, m - L / 2, 0, L, '-x', rows=3, row_h=0.36, depth=0.3, frame='walnut', sides=False, back=False); cx_, cy_ = C - T + od - 0.15, m
            candle(R, cx_, cy_, 3 * 0.36 + 0.035 + 0.08 + 0.06, h=0.22, r=0.04)
    # a lamp in every bay
    spots = set()
    for p in (c0, 5.33, C / 2, C - 5.33, c1):
        for q in ((p, c0), (p, c1), (c0, p), (c1, p)): spots.add((round(q[0], 3), round(q[1], 3)))
    for (x, y) in sorted(spots):
        hang_lamp(R, x, y, 3.3, js + r, r=0.15)
    # walkers: the loop
    navloop(R, ((c0, c0), (C / 2, c0), (c1, c0), (c1, C / 2), (c1, c1), (C / 2, c1), (c0, c1), (c0, C / 2)))
    R.spot('probe', c0, C / 2, 1.7)
    R.meta.update(label='The Arcade Loop', weight=6,
                  blurb='A vaulted walk goes round a block of solid stone, with books set into its outside. You go round it twice looking for a door. There is no door.')
    R.meta['box'] = [[T, 0, T], [C - T, js + r, C - T]]
    return R
