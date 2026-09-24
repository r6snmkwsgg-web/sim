"""The Vestibule: a stone hall where a procession of free-standing arches, each smaller and closer than
the last, runs east to a door a metre high. The perspective lies; the real doors are where they always are."""
from lib import *
from kit_b import *


def arch_ring(R, x, yc, w, jamb, t, thick, m='tile'):
    """A free-standing arch across y at x: two legs and a round head, thick along x."""
    r_in, r_out = w / 2, w / 2 + t
    n = 16
    outer = [(yc + r_out * math.cos(math.pi * k / n), jamb + r_out * math.sin(math.pi * k / n)) for k in range(n + 1)]
    inner = [(yc + r_in * math.cos(math.pi * k / n), jamb + r_in * math.sin(math.pi * k / n)) for k in range(n + 1)]
    R.parts.add(prism(outer + inner[::-1], 'x', x - thick / 2, x + thick / 2, m, cap=m))
    for s in (-1, 1):
        a, b = sorted((yc + s * r_in, yc + s * r_out))
        R.parts.add(box(x - thick / 2, a, 0, x + thick / 2, b, jamb, m, skip=('-z',)))
        # a plinth and an impost
        R.nocol.add(box(x - thick / 2 - 0.04 * t / 0.5, a - 0.04 * t / 0.5, 0, x + thick / 2 + 0.04 * t / 0.5, b + 0.04 * t / 0.5, 0.3 * t / 0.5, m, skip=('-z',)))
        R.nocol.add(box(x - thick / 2 - 0.05 * t / 0.5, a - 0.05 * t / 0.5, jamb - 0.14 * t / 0.5, x + thick / 2 + 0.05 * t / 0.5, b + 0.05 * t / 0.5, jamb, m))


def make():
    R = Room('vestibule', 1, 1, res=1024)
    H = TOP - 0.1
    shell(R, H, wall='tile', floor='slate', ceil='tile')
    yc = 11.8
    # the procession of arches, shrinking toward the east wall
    x, s, sp = 2.7, 1.0, 1.7
    k = 0
    xs = []
    while x < C - T - 0.6:
        w, jamb, t = 4.4 * s, 3.4 * s, 0.5 * s
        if not (6.2 < x < 9.8 and yc + w / 2 + t > 13.5):
            arch_ring(R, x, yc, w, jamb, t, 0.4 * s)
            bulb(R, x, yc, jamb + w / 2 - 0.3 * s, 0.08 * max(s, 0.4), 'e_lamp' if k % 2 == 0 else 'e_amber')
            R.nocol.add(cyl(x, yc, jamb + w / 2 - 0.22 * s, jamb + w / 2, 0.01, 4, side='iron', caps=False))
        xs.append((x, s))
        x += sp * s
        s *= 0.88
        k += 1
    # the little door at the end, a metre high, with light under it, on a dark wall
    R.nocol.add(box(C - T - 0.02, yc - 2.15, 0, C - T, yc + 2.9, 6.3, 'slate', skip=('+x',)))
    xe = C - T
    dw, dh = 0.62, 1.0
    R.nocol.add(box(xe - 0.08, yc - dw / 2 - 0.08, 0, xe - 0.02, yc + dw / 2 + 0.08, dh + 0.1, 'walnut'))
    R.nocol.add(box(xe - 0.1, yc - dw / 2, 0, xe - 0.08, yc + dw / 2, dh, 'oak'))
    R.nocol.add(box(xe - 0.13, yc + dw / 2 - 0.1, 0.48, xe - 0.1, yc + dw / 2 - 0.06, 0.52, 'brass'))
    R.light(quad(yc - dw / 2 + 0.02, yc + dw / 2 - 0.02, xe - 0.105, 0.0, 0.02, 'e_amber', '-x'))
    R.light(box(xe - 0.05, yc - 0.1, dh + 0.14, xe - 0.03, yc + 0.1, dh + 0.21, 'e_exit'))
    # a path of dark stone narrowing to it
    pts = [(2.7, yc - 2.2), (xe, yc - dw / 2), (xe, yc + dw / 2), (2.7, yc + 2.2)]
    R.nocol.add(poly_prism(pts, 0, 0.01, side='slate', top='terrazzo', bottom='slate'))
    # the vestibule proper: columns, benches, bookcases on the south, west and east walls
    for (cx_, cy_) in ((4.2, 4.2), (C - 4.2, 4.2)):
        R.parts.add(cyl(cx_, cy_, 0, H, 0.35, 20, side='tile', caps=False))
        R.parts.add(box(cx_ - 0.5, cy_ - 0.5, 0, cx_ + 0.5, cy_ + 0.5, 0.35, 'tile', skip=('-z',)))
        R.parts.add(box(cx_ - 0.5, cy_ - 0.5, H - 0.4, cx_ + 0.5, cy_ + 0.5, H, 'tile', skip=('+z',)))
    wall_shelves(R, rows=9, frame='walnut', sides='S')
    wall_shelves(R, rows=9, frame='walnut', sides='WE', segs=((0.6, 6.2),))
    for (x0, x1) in ((2.8, 5.8), (10.2, 13.2)):
        R.parts.add(box(x0, 7.2, 0, x1, 7.7, 0.45, 'tile', skip=('-z',)))
        for k2 in range(3):
            R.spot('sit', x0 + 0.5 + k2 * 1.0, 7.45, 0.45, -math.pi / 2)
    # lanterns
    for (x, y) in ((8, 4.0), (8, 8.3)):
        pendant(R, x, y, 3.4, H, r=0.25, m='iron', em='e_lamp')
    R.light(box(T, 9.2, H - 0.05, C - T, 9.4, H - 0.02, 'e_fluor'))
    loop(R, [(1.8, 1.8), (8, 1.8), (C - 1.8, 1.8), (C - 1.8, 8.4), (8, 8.8), (1.8, 8.4)])
    a = R.navpt(8, C - 1.2); R.link(a, 4)
    b = R.navpt(3.0, yc); R.link(b, 5)
    R.spot('probe', 8, 6.0, 1.8)
    R.meta.update(label='The Vestibule', weight=4,
                  blurb='The arches go on and on, getting smaller, to a little door at the end. It takes eleven steps to get there. It should take a hundred.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
