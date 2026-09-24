"""The Endless Corridor: one vaulted passage 128 m long, 4 m wide and 10 m high, down the middle of
the footprint. Bookcases on both sides, a lamp on a long cord every four metres, all the way to a
point. Low arched side passages reach out to the doorways on the long walls; cross passages at the
ends reach the doorways there."""
from lib import *
from kit_g import *


def make():
    R = Room('corridor', 8, 2, levels=2, res=2048)
    W, D = R.W, R.D
    seal(R, upper_sockets(R), floor='floor', wall='tile')
    cy, hw = D / 2, 2.0                       # corridor centre line, half width
    jamb, crown = 8.0, 8.0 + hw
    pr = arch_profile(cy, 2 * hw, 0, jamb, 16)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'floor', 'tile')))
    # end cross passages, reaching the doorways at y = 8 and 24 on the short walls
    ew = 3.6
    for (x0, x1) in ((T - 0.02, T + ew), (W - T - ew, W - T + 0.02)):
        p2 = arch_profile((x0 + x1) / 2, x1 - x0, 0, 3.0, 12)
        R.cut(prism(p2, 'y', 8 - DW / 2 - 0.4, D - 8 + DW / 2 + 0.4, arch_mats(len(p2), 'floor', 'tile')))
    # side passages to the doorways on the long walls
    sw = 3.0
    for i in range(R.w):
        x = i * C + C / 2
        p3 = arch_profile(x, sw, 0, 2.6, 12)
        R.cut(prism([(q, z) for q, z in p3], 'y', T - 0.1, cy - hw + 0.02, arch_mats(len(p3), 'floor', 'tile')))
        R.cut(prism([(q, z) for q, z in p3], 'y', cy + hw - 0.02, D - T + 0.1, arch_mats(len(p3), 'floor', 'tile')))
        for y in (T + 4.5, D - T - 4.5):
            R.light(box(x - 0.25, y - 0.25, 3.98, x + 0.25, y + 0.25, 4.02, 'e_dim'))
    # bookcases down both sides, broken at the side passages
    stops = [T + ew] + sum([[i * C + C / 2 - sw / 2, i * C + C / 2 + sw / 2] for i in range(R.w)], []) + [W - T - ew]
    for k in range(0, len(stops), 2):
        a, b = stops[k] + 0.15, stops[k + 1] - 0.15
        if b - a < 1.0: continue
        R.shelf(a, cy - hw, 0, b - a, '+y', rows=11, frame='walnut', depth=0.32)
        R.shelf(b, cy + hw, 0, b - a, '-y', rows=11, frame='walnut', depth=0.32)
    # a lamp on a long cord every four metres
    x = 2.0 + T
    while x < W - 1:
        hanging(R, x, cy, crown - 0.05, 3.3, r=0.13, e='e_lamp', segs=8)
        x += 4.0
    # a night light at each end, on the end wall
    for xw in (T + 0.02, W - T - 0.02):
        s = 1 if xw < W / 2 else -1
        R.light(box(min(xw, xw + s * 0.06), cy - 0.3, 2.2, max(xw, xw + s * 0.06), cy + 0.3, 2.5, 'e_amber'))
    # walkers: a long loop down the corridor, spurs out to two doorways
    xa, xb = T + ew / 2, W - T - ew / 2
    xs = [xa, 2 * C + C / 2, 5 * C + C / 2, xb]
    south = [R.navpt(x, cy - 0.8) for x in xs]
    north = [R.navpt(x, cy + 0.8) for x in reversed(xs)]
    R.link(*south, *north, south[0])
    lp = [south[0], None, None, north[-1]]
    for k in (1, 2):
        x = xs[k]
        R.link(south[k], R.navpt(x, T + 2.0))
        R.link(north[3 - k], R.navpt(x, D - T - 2.0))
    e0, e1 = R.navpt(xa, 8.0), R.navpt(xa, D - 8.0)
    R.link(e0, lp[0]); R.link(lp[3], e1)
    R.spot('probe', 40, cy, 2.5)
    R.meta.update(label='The Endless Corridor', weight=4,
                  blurb='A corridor, and lamps, and books, and more corridor. Perspective is doing most of the work here, and it is tired.')
    R.meta['box'] = [[T, 0, T], [W - T, crown, D - T]]
    return R
