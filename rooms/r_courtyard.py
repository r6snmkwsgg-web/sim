"""The Courtyard: a cloister open to a painted sky. A roofed arcade on stone columns runs round
the walls, bookcases under it; in the middle a dry fountain and a sundial with no shadow."""
from lib import *


def make():
    R = Room('courtyard', 1, 1, res=1024)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, TOP - 0.1, 'tile', bottom='slate', top='plaster'))
    # the sky over everything; the arcade roof hides its edges
    R.light(box(T, T, TOP - 0.14, C - T, C - T, TOP - 0.12, 'e_skydome'))
    a0, a1, rh = 3.2, C - 3.2, 3.6          # arcade inner edge, roof height
    # arcade roof: a slab round the edge, a moulded lip, columns under the lip
    for (x0, y0, x1, y1) in ((T, T, C - T, a0), (T, a1, C - T, C - T), (T, a0, a0, a1), (a1, a0, C - T, a1)):
        R.parts.add(box(x0, y0, rh, x1, y1, rh + 0.45, 'tile', bottom='plaster'))
    for (x0, y0, x1, y1) in ((a0 - 0.1, a0 - 0.1, a1 + 0.1, a0 + 0.1), (a0 - 0.1, a1 - 0.1, a1 + 0.1, a1 + 0.1),
                             (a0 - 0.1, a0 + 0.1, a0 + 0.1, a1 - 0.1), (a1 - 0.1, a0 + 0.1, a1 + 0.1, a1 - 0.1)):
        R.parts.add(box(x0, y0, rh + 0.45, x1, y1, rh + 0.62, 'tile'))
    for k in range(5):
        p = a0 + k * (a1 - a0) / 4
        for (x, y) in ((p, a0), (p, a1), (a0, p), (a1, p)):
            R.parts.add(cyl(x, y, 0, rh, 0.22, 20, side='tile', caps=False))
            R.parts.add(box(x - 0.32, y - 0.32, rh - 0.22, x + 0.32, y + 0.32, rh, 'tile', skip=('+z',)))
            R.parts.add(box(x - 0.3, y - 0.3, 0, x + 0.3, y + 0.3, 0.2, 'tile', skip=('-z',)))
    # lamps hanging under the arcade roof
    for k in range(4):
        p = 1.8 + k * 4.13
        for (x, y) in ((p, 1.75), (p, C - 1.75), (1.75, p), (C - 1.75, p)):
            R.light(cyl(x, y, rh - 0.5, rh - 0.35, 0.14, 12, side='e_lamp', top='e_lamp', bottom='e_lamp'))
            R.parts.add(cyl(x, y, rh - 0.35, rh, 0.012, 6, side='iron', caps=False))
    # bookcases on the back walls of the arcade
    for (a, b) in ((0.7, 6.1), (9.9, C - 0.7)):
        R.shelf(a, T, 0, b - a, '+y', rows=7, frame='walnut')
        R.shelf(b, C - T, 0, b - a, '-y', rows=7, frame='walnut')
        R.shelf(T, b, 0, b - a, '+x', rows=7, frame='walnut')
        R.shelf(C - T, a, 0, b - a, '-x', rows=7, frame='walnut')
    # the dry fountain: a round stone basin with a stepped rim, and a basin on a stem in the middle
    R.parts.add(ring(8, 8, 0, 0.55, 2.0, 2.35, 48, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.parts.add(cyl(8, 8, 0, 0.05, 2.0, 48, side='slate', top='slate', bottom='slate'))
    R.parts.add(cyl(8, 8, 0, 1.3, 0.18, 16, side='tile', top='tile'))
    R.parts.add(cyl(8, 8, 1.3, 1.45, 0.75, 32, side='tile', top='tile', bottom='tile'))
    # four benches facing the fountain
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        R.parts.add(box(-0.8, -0.22, 0, 0.8, 0.22, 0.45, 'walnut', skip=('-z',)).xform(a + math.pi / 2, 8 + math.cos(a) * 4.0, 8 + math.sin(a) * 4.0))
        R.spot('sit', 8 + math.cos(a) * 4.0, 8 + math.sin(a) * 4.0, 0.45, a + math.pi)
    ring_ = [R.navpt(8 + math.cos(k * math.pi / 4) * 3.1, 8 + math.sin(k * math.pi / 4) * 3.1) for k in range(8)]
    R.link(*ring_, ring_[0])
    walk = [R.navpt(x, y) for (x, y) in ((1.7, 1.7), (8, 1.7), (C - 1.7, 1.7), (C - 1.7, 8), (C - 1.7, C - 1.7), (8, C - 1.7), (1.7, C - 1.7), (1.7, 8))]
    R.link(*walk, walk[0])
    for k in range(4): R.link(walk[k * 2 + 1], ring_[(k * 2 + 6) % 8])
    R.spot('probe', 8, 8, 2.2)
    R.meta.update(label='The Courtyard', weight=6,
                  blurb='Sky. Real sky, or something painted to look like it, over a cloister and a dry fountain. It never rains.')
    R.meta['box'] = [[T, 0, T], [C - T, TOP - 0.12, C - T]]
    return R
