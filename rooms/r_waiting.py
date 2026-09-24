"""The Waiting Room: rows of chairs all facing one door that has never opened. A counter with a bell
nobody answers, a large clock, a green sign."""
from lib import *
from kit_a import *

H = 6.6


def clock(R, cx, cz, r, y, face='ivory'):
    """A wall clock on the north wall (face toward -y), its plane at y."""
    R.parts.add(xz_plate(circle_pts(cx, cz, r + 0.09, 40), y - 0.06, y, 'walnut'))
    R.parts.add(xz_plate(circle_pts(cx, cz, r, 40), y - 0.08, y - 0.06, face))
    for k in range(12):
        a = math.pi / 2 - k * math.pi / 6
        L = 0.16 if k % 3 == 0 else 0.08
        R.parts.add(xz_plate(quad_poly(cx + math.cos(a) * (r - 0.05 - L), cz + math.sin(a) * (r - 0.05 - L), L, 0.035 if k % 3 else 0.06, a), y - 0.1, y - 0.08, 'black'))
    # ten to four, forever
    for (a, L, w) in ((math.pi / 2 - 2 * math.pi * (3.83 / 12), r * 0.55, 0.06), (math.pi / 2 - 2 * math.pi * (50 / 60), r * 0.85, 0.035)):
        R.parts.add(xz_plate(quad_poly(cx, cz, L, w, a), y - 0.12, y - 0.1, 'iron'))
    R.parts.add(xz_plate(circle_pts(cx, cz, 0.05, 12), y - 0.14, y - 0.08, 'brass'))


def make():
    R = Room('waiting', 1, 1, res=1024)
    shell(R, wall='ivory', floor='terrazzo', ceil='plaster', h=H, skip=(('N', 0, 0),))
    # a green dado with an oak rail round the walls (broken at the live doors)
    for (a, b) in ((T, 6.45), (9.55, C - T)):
        R.parts.add(box(a, T, 0, b, T + 0.02, 1.25, 'green', skip=('-z',)))
        R.parts.add(box(a, T, 1.25, b, T + 0.05, 1.31, 'oak'))
        R.parts.add(box(T, a, 0, T + 0.02, b, 1.25, 'green', skip=('-z',)))
        R.parts.add(box(T, a, 1.25, T + 0.05, b, 1.31, 'oak'))
        R.parts.add(box(C - T - 0.02, a, 0, C - T, b, 1.25, 'green', skip=('-z',)))
        R.parts.add(box(C - T - 0.05, a, 1.25, C - T, b, 1.31, 'oak'))
    R.parts.add(box(T, C - T - 0.02, 0, C - T, C - T, 1.25, 'green', skip=('-z',)))
    R.parts.add(box(T, C - T - 0.05, 1.25, C - T, C - T, 1.31, 'oak'))
    # THE door: a tall double door in a heavy frame, flush in the north wall, never opened
    yN = C - T
    dw, dh = 1.45, 3.9          # half width and height of the leaves
    R.parts.add(box(8 - dw - 0.3, yN - 0.12, 0, 8 + dw + 0.3, yN, dh + 0.3, 'walnut'))                 # architrave
    R.parts.add(box(8 - dw, yN - 0.16, 0, 8 + dw, yN - 0.12, dh, 'oak', skip=('-z',)))                # the leaves
    R.parts.add(box(7.99, yN - 0.17, 0, 8.01, yN - 0.16, dh - 0.02, 'walnut', skip=('-z',)))
    for x in (8 - dw + 0.18, 8 + 0.18):
        for (z0, z1) in ((0.3, 1.7), (1.95, dh - 0.2)):
            R.parts.add(box(x, yN - 0.18, z0, x + dw - 0.36, yN - 0.16, z1, 'walnut'))
    for x in (7.8, 8.2):
        R.parts.add(box(x - 0.02, yN - 0.24, 1.25, x + 0.02, yN - 0.16, 1.3, 'brass'))
        R.parts.add(box(x - 0.025, yN - 0.26, 1.1, x + 0.025, yN - 0.22, 1.3, 'brass'))
    R.parts.add(box(8 - dw - 0.42, yN - 0.22, dh + 0.3, 8 + dw + 0.42, yN, dh + 0.5, 'walnut'))      # cornice
    R.parts.add(box(7.45, yN - 0.12, dh + 0.62, 8.55, yN - 0.02, dh + 0.95, 'black'))
    R.light(box(7.5, yN - 0.14, dh + 0.66, 8.5, yN - 0.12, dh + 0.91, 'e_exit'))
    clock(R, 8, 5.75, 0.62, yN - 0.02)
    R.meta['sealed'] = [('N', 0, 0)]
    # rows of identical chairs, all facing the door
    rows = [2.9, 4.0, 5.1, 6.2, 9.8, 10.9]
    for y in rows:
        for x0 in (2.7, 10.2):
            for k in range(6):
                R.nocol.add(chair(x0 + k * 0.62, y, math.pi / 2, frame='chrome', seat='oxblood', back_h=0.92))
            R.col.add(box(x0 - 0.25, y - 0.25, 0, x0 + 5 * 0.62 + 0.25, y + 0.23, 0.48, 'tile'))
            R.col.add(box(x0 - 0.25, y - 0.25, 0.48, x0 + 5 * 0.62 + 0.25, y - 0.2, 0.92, 'tile'))
        R.spot('sit', 3.32, y, 0.48, math.pi / 2)
        R.spot('sit', 11.44, y, 0.48, math.pi / 2)
    # a counter with a bell and a sign, in the north-east corner; files behind it
    cx0, cx1, cy0, cy1 = 12.9, 13.6, 11.6, C - T
    R.parts.add(box(cx0, cy0, 0, cx1, cy1, 1.05, 'walnut'))
    R.parts.add(box(cx0 - 0.06, cy0 - 0.06, 1.05, cx1 + 0.02, cy1, 1.1, 'oak'))
    R.parts.add(cyl(cx0 + 0.3, 12.2, 1.1, 1.12, 0.06, 12, side='walnut', top='walnut'))
    R.parts.add(sphere(cx0 + 0.3, 12.2, 1.12, 0.055, 12, 6, 'brass', lower=False))
    R.parts.add(cyl(cx0 + 0.3, 12.2, 1.17, 1.19, 0.008, 6, side='brass', top='brass'))
    R.parts.add(box(cx0 + 0.1, 12.6, 1.1, cx0 + 0.14, 13.0, 1.32, 'ivory'))   # 'please ring'
    sh(R, '-x', C - T, 11.6, C - T - 0.05, rows=7, frame='oak')
    R.parts.add(box(C - T - 0.1, 11.2, 3.3, C - T, 12.8, 3.8, 'black'))
    R.light(box(C - T - 0.12, 11.3, 3.38, C - T - 0.1, 12.7, 3.72, 'e_amber'))   # now serving: nobody
    # low bookcases of old magazines and forms along the south wall, and a side table of them
    sh(R, '+y', T, 0.8, 6.0, rows=3, frame='oak')
    sh(R, '+y', T, 10.0, 15.2, rows=3, frame='oak')
    sh(R, '+x', T, 10.4, 14.6, rows=3, frame='oak')
    sh(R, '+x', T, 1.4, 5.6, rows=3, frame='oak')
    sh(R, '-x', C - T, 1.4, 5.6, rows=3, frame='oak')
    R.parts.add(table(7.3, 2.8, 8.7, 3.5, 0.5, 'oak'))
    # plain ceiling panels, a grid of them
    for x in (3.2, 8.0, 12.8):
        for y in (3.5, 8.0, 12.5):
            R.parts.add(box(x - 0.9, y - 0.5, H - 0.05, x + 0.9, y + 0.5, H, 'chrome'))
            R.light(box(x - 0.8, y - 0.4, H - 0.07, x + 0.8, y + 0.4, H - 0.05, 'e_panel'))
    navloop(R, [(2.0, 2.0), (8, 2.2), (14.0, 2.0), (14.0, 8.0), (12.3, 13.2), (8, 13.4), (2.0, 13.6), (2.0, 8)])
    a, b = R.navpt(5, 8), R.navpt(11, 8)
    R.link(7, a, b, 3); R.link(a, 5)
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Waiting Room', weight=5,
                  blurb='Every chair faces the same door. The clock says ten to four. You find you have already sat down.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
