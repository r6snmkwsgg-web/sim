"""The Great Cloister: a vaulted arcade of books runs round a courtyard open to a painted sky.
Round-arched openings look in on a dry stepped basin and four trees made of spheres. High in the
courtyard walls a few windows are lit, though there is no way up to them."""
from lib import *
from kit_f import *
import random


def make():
    R = Room('cloister', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    rnd = random.Random(77)
    a0, a1 = 4.4, 5.0                 # the arcade's inner wall (courtyard face at a1)
    A1 = W - a1
    # the arcade: a barrel vault down each side (groined at the corners)
    cw = a0 - T
    for (lo, hi) in ((T - 0.02, a0), (W - a0, W - T + 0.02)):
        pr = arch_profile((lo + hi) / 2, hi - lo, 0, 3.3, 24)
        R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism(pr, 'y', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
    # the courtyard, open to the sky
    R.cut(box(a1, a1, 0, A1, A1, TOP - 0.1, 'tile', bottom='slate', top='plaster'))
    R.light(box(a1, a1, TOP - 0.14, A1, A1, TOP - 0.12, 'e_skydome'))
    # arches through the inner wall, one in line with each doorway and four between
    centres = [8 + 3.2 * k for k in range(6)]
    for c in centres:
        pr = arch_profile(c, 2.4, 0, 2.3, 18)
        R.cut(prism(pr, 'y', a0 - 0.05, a1 + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism(pr, 'y', W - a1 - 0.05, W - a0 + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism(pr, 'x', a0 - 0.05, a1 + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism(pr, 'x', W - a1 - 0.05, W - a0 + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
    # upper windows in the courtyard walls; a few lit
    wp = arch_profile(0, 1.0, 5.2, 1.0, 12)
    for c in centres:
        for side in range(4):
            lit = rnd.random() < 0.3
            prw = [(p + c, q) for p, q in wp]
            if side == 0:
                R.cut(prism(prw, 'y', a1 - 0.25, a1 + 0.05, arch_mats(len(prw), 'tile', 'tile')))
                back = box(c - 0.5, a1 - 0.24, 5.2, c + 0.5, a1 - 0.22, 6.7, 'e_amber' if lit else 'black')
            elif side == 1:
                R.cut(prism(prw, 'y', A1 - 0.05, A1 + 0.25, arch_mats(len(prw), 'tile', 'tile')))
                back = box(c - 0.5, A1 + 0.22, 5.2, c + 0.5, A1 + 0.24, 6.7, 'e_amber' if lit else 'black')
            elif side == 2:
                R.cut(prism(prw, 'x', a1 - 0.25, a1 + 0.05, arch_mats(len(prw), 'tile', 'tile')))
                back = box(a1 - 0.24, c - 0.5, 5.2, a1 - 0.22, c + 0.5, 6.7, 'e_amber' if lit else 'black')
            else:
                R.cut(prism(prw, 'x', A1 - 0.05, A1 + 0.25, arch_mats(len(prw), 'tile', 'tile')))
                back = box(A1 + 0.22, c - 0.5, 5.2, A1 + 0.24, c + 0.5, 6.7, 'e_amber' if lit else 'black')
            (R.light if lit else R.parts.add)(back)
    # a cornice round the courtyard under the sky, and a string course over the arches
    for (x0, y0, x1, y1) in ((a1, a1, A1, a1 + 0.3), (a1, A1 - 0.3, A1, A1), (a1, a1 + 0.3, a1 + 0.3, A1 - 0.3), (A1 - 0.3, a1 + 0.3, A1, A1 - 0.3)):
        R.parts.add(box(x0, y0, TOP - 0.55, x1, y1, TOP - 0.35, 'tile'))
    for (x0, y0, x1, y1) in ((a1, a1, A1, a1 + 0.15), (a1, A1 - 0.15, A1, A1), (a1, a1 + 0.15, a1 + 0.15, A1 - 0.15), (A1 - 0.15, a1 + 0.15, A1, A1 - 0.15)):
        R.parts.add(box(x0, y0, 4.6, x1, y1, 4.8, 'tile'))
    # the dry basin: square, stepped down 1.2 m, with a pedestal in the middle
    R.pool(12.6, 12.6, W - 12.6, W - 12.6, 1.2, m='mosaic')
    R.parts.add(cyl(16, 16, -1.2, 0.2, 0.35, 16, side='tile', top='tile'))
    R.parts.add(cyl(16, 16, 0.2, 0.4, 0.9, 24, side='tile', top='tile', bottom='tile'))
    for (x, y) in ((16, 12.61), (16, W - 12.61), (12.61, 16), (W - 12.61, 16)):
        if abs(y - 16) > 1: R.light(box(x - 0.25, y - 0.03, -0.26, x + 0.25, y + 0.03, -0.12, 'e_pool'))
        else: R.light(box(x - 0.03, y - 0.25, -0.26, x + 0.03, y + 0.25, -0.12, 'e_pool'))
    # four raised beds, each with a tree of spheres
    for (px, py) in ((9.6, 9.6), (W - 9.6, 9.6), (9.6, W - 9.6), (W - 9.6, W - 9.6)):
        R.parts.add(box(px - 1.5, py - 1.5, 0, px + 1.5, py + 1.5, 0.5, 'tile', skip=('-z', '+z')))
        for (x0, y0, x1, y1) in ((-1.5, -1.5, 1.5, -1.25), (-1.5, 1.25, 1.5, 1.5), (-1.5, -1.25, -1.25, 1.25), (1.25, -1.25, 1.5, 1.25)):
            R.parts.add(box(px + x0, py + y0, 0.49, px + x1, py + y1, 0.55, 'tile', skip=('-z',)))
        R.parts.add(box(px - 1.25, py - 1.25, 0, px + 1.25, py + 1.25, 0.42, 'green', skip=('-z',)))
        R.parts.add(cyl(px, py, 0.42, 3.4, 0.2, 10, side='walnut', caps=False))
        R.parts.add(bar((px, py, 2.4), (px + 0.9, py + 0.4, 3.6), 0.12, 0.12, 'walnut'))
        R.parts.add(bar((px, py, 2.6), (px - 0.7, py - 0.6, 3.8), 0.1, 0.1, 'walnut'))
        for (dx, dy, dz, r) in ((0, 0, 4.6, 1.5), (0.9, 0.4, 3.9, 1.0), (-0.8, -0.6, 4.1, 1.05), (0.2, -0.9, 5.3, 0.95), (-0.4, 0.8, 5.0, 1.0)):
            R.parts.add(sphere(px + dx, py + dy, dz, r, 10, 6, 'green'))
    # benches round the basin
    for k in range(4):
        a = k * math.pi / 2
        for s in (-1, 1):
            bx = 16 + math.cos(a) * 4.9 + math.cos(a + math.pi / 2) * s * 2.2
            by = 16 + math.sin(a) * 4.9 + math.sin(a + math.pi / 2) * s * 2.2
            R.parts.add(box(-0.8, -0.22, 0, 0.8, 0.22, 0.45, 'walnut', skip=('-z',)).xform(a + math.pi / 2, bx, by))
            R.spot('sit', bx, by, 0.45, a + math.pi)
    # lamps down the arcade, one in each bay
    for k in range(10):
        p = 1.9 + k * (W - 3.8) / 9
        for (x, y) in ((p, (T + a0) / 2), (p, W - (T + a0) / 2), ((T + a0) / 2, p), (W - (T + a0) / 2, p)):
            lamp(R, x, y, 3.3, 0.16, chain=5.3)
    # books on the arcade's outer walls
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), rows=7, frame='oak')
    # walkers: round the arcade, and round the basin
    ring0 = loop(R, ((2.4, 2.4), (8, 2.4), (24, 2.4), (W - 2.4, 2.4), (W - 2.4, 8), (W - 2.4, 24), (W - 2.4, W - 2.4), (24, W - 2.4), (8, W - 2.4), (2.4, W - 2.4), (2.4, 24), (2.4, 8)))
    ring1 = loop(R, ((8, 8), (16, 7.4), (24, 8), (24.6, 16), (24, 24), (16, 24.6), (8, 24), (7.4, 16)))
    R.link(ring0[1], R.navpt(8, 6.0), ring1[0]); R.link(ring0[7], R.navpt(24, 26.0), ring1[4])
    R.spot('probe', 16, 16, 2.0)
    R.meta.update(label='The Great Cloister', weight=5,
                  blurb='A courtyard under an open sky, and four trees that do not move when the wind does not blow. Someone has left a light on upstairs.')
    R.meta['box'] = [[T, -1.2, T], [W - T, TOP - 0.1, W - T]]
    return R
