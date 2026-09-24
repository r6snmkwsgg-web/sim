"""The Coil: a square spiral of bookcases winding inward, corridor after corridor, to one chair under
one lamp in the middle. A corridor runs round the outside past the doors."""
from lib import *
from kit_a import *

H = TOP - 0.1
CX = CY = C / 2
HS, PT = 5.3, 2.1        # half-size of the outer turn, pitch between turns
HW = 0.28               # half the wall thickness
WH_ROWS = 9             # 3.9 m walls


def make():
    R = Room('coil', 1, 1, res=1024)
    shell(R, wall='damask', floor='carpet', ceil='plaster', h=H)
    h, p = HS, PT
    pts = [(-h, -h), (h, -h), (h, h), (-h, h), (-h, -h + p), (h - p, -h + p), (h - p, h - p), (-h + p, h - p), (-h + p, -h + 2 * p), (h - 2 * p, -h + 2 * p)]
    P = [(CX + x, CY + y) for x, y in pts]
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        dx, dy = (x1 - x0) / L, (y1 - y0) / L
        R.parts.add(obox(x0, y0, x1, y1, 0, WH_ROWS * 0.42 + 0.12, 0.06, 'walnut'))
        a0, a1 = HW, L - HW
        # the two faces: left (inward) and right (outward) of the direction of travel
        for s in (1, -1):
            nx, ny = -dy * s, dx * s
            ang = math.atan2(ny, nx)
            bx0, by0 = x0 + dx * a0 + nx * 0.03, y0 + dy * a0 + ny * 0.03
            bx1, by1 = x0 + dx * a1 + nx * 0.03, y0 + dy * a1 + ny * 0.03
            # R.shelf wants the back-left corner seen from the front: that is the end on the viewer's left
            th = ang - math.pi / 2
            ux, uy = math.cos(th), math.sin(th)
            start = (bx0, by0) if (bx1 - bx0) * ux + (by1 - by0) * uy > 0 else (bx1, by1)
            shelf(R, start[0], start[1], 0, a1 - a0, ang, rows=WH_ROWS, depth=0.24, frame='wood', back=False, sides=False)
    for (x, y) in P:
        R.parts.add(box(x - HW, y - HW, 0, x + HW, y + HW, WH_ROWS * 0.42 + 0.2, 'walnut'))
        R.parts.add(box(x - HW - 0.04, y - HW - 0.04, WH_ROWS * 0.42 + 0.2, x + HW + 0.04, y + HW + 0.04, WH_ROWS * 0.42 + 0.28, 'walnut'))
    # the room's own walls are books as well, except at the doors
    for (f, bk) in (('+y', T), ('-y', C - T), ('+x', T), ('-x', C - T)):
        sh(R, f, bk, T + 0.05, 6.2, rows=WH_ROWS, depth=0.24, frame='wood')
        sh(R, f, bk, 9.8, C - T - 0.05, rows=WH_ROWS, depth=0.24, frame='wood')
    # dim bulbs down the corridor, following the coil in
    Q = [(CX - h - 1.0, CY - h + p / 2)]
    ns = []
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        L = math.hypot(x1 - x0, y1 - y0); ns.append((-(y1 - y0) / L, (x1 - x0) / L))
    for i in range(1, 6):
        n0, n1 = ns[i - 1], ns[i]
        Q.append((P[i][0] + p / 2 * (n0[0] + n1[0]), P[i][1] + p / 2 * (n0[1] + n1[1])))
    Q.append((Q[-1][0], CY + 0.2))
    lamps = []
    for (x0, y0), (x1, y1) in zip(Q, Q[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / 3.6))
        for t in range(n):
            f = (t + 0.5) / n
            lamps.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    for (x, y) in lamps[1:]:
        bulb(R, x, y, 3.1, r=0.1, m='e_fluor', top=H)
    for (x, y) in ((1.3, 1.3), (C - 1.3, 1.3), (C - 1.3, C - 1.3), (1.3, C - 1.3)):
        bulb(R, x, y, 3.3, r=0.1, m='e_amber', top=H)
    for (x, y) in ((1.5, 5.2), (1.5, 10.8), (C - 1.5, 5.2), (C - 1.5, 10.8), (5.2, 1.5), (10.8, 1.5), (5.2, C - 1.5), (10.8, C - 1.5)):
        bulb(R, x, y, 3.2, r=0.11, m='e_lamp', top=H)
    # the middle: one chair, one lamp
    mx, my = CX + 0.0, CY + 1.05
    R.parts.add(chair(mx, my, -math.pi / 2, frame='walnut', seat='velvet'))
    R.spot('sit', mx, my, 0.48, -math.pi / 2)
    R.parts.add(box(mx - 1.3, my - 1.0, 0, mx + 1.3, my + 1.0, 0.012, 'damask'))
    R.nocol.add(cyl(mx, my, 2.15, H, 0.012, 6, side='iron', caps=False))
    R.nocol.add(cyl(mx, my, 2.0, 2.2, 0.34, 20, side='green', top='green', bottom='green', caps=True))
    R.light(cyl(mx, my, 1.96, 2.0, 0.26, 20, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    # walkers: round the outside, then the coil
    navloop(R, [(1.4, 1.4), (8, 1.4), (C - 1.4, 1.4), (C - 1.4, 8), (C - 1.4, C - 1.4), (8, C - 1.4), (1.4, C - 1.4), (1.4, 8)])
    ids = [R.navpt(x, y) for (x, y) in Q]
    R.link(*ids)
    c = R.navpt(mx - 1.2, my); R.link(ids[-1], c)
    R.link(7, ids[0])
    R.spot('probe', CX - h - 1.0, CY, 1.7)
    R.meta.update(label='The Coil', weight=4,
                  blurb='The corridor turns left, and left, and left. At the end of it there is a chair, and a lamp, and nothing else, and it is very restful.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
