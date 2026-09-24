"""The Burrows: the whole cell is solid shelving, and low tunnels wind through it, lined with
books on both sides, joining the four doors round a ring, with two spurs into an octagonal den
in the middle. Where they meet the doorways the tunnels rise into full-height arches."""
from lib import *
from kit_d import *

TH, HW = 2.2, 1.25         # tunnel height, half width of the cut (shelves take 0.36 off each side)


def tunnel(R, pts, door_ends=(), nav=True):
    """Cut a winding tunnel along pts, knuckles at the joints, shelves down both walls."""
    for (x, y) in pts:
        R.cut(cyl(x, y, 0, TH, HW, 10, side='walnut', top='oak', bottom='floor'))
    ids = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0); a = math.atan2(y1 - y0, x1 - x0)
        R.cut(box(0, -HW, 0, L, HW, TH, 'walnut', top='oak', bottom='floor').xform(a, x0, y0))
        t0 = 1.7 if i == 0 and 0 in door_ends else 0.4
        t1 = 1.7 if i == len(pts) - 2 and 1 in door_ends else 0.4
        sl = L - t0 - t1
        if sl > 0.5:
            ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
            mx, my = x0 + ux * (t0 + sl / 2), y0 + uy * (t0 + sl / 2)
            for s in (1, -1):
                shelf_at(R, mx + s * nx * HW, my + s * ny * HW, 0, sl, math.atan2(-s * ny, -s * nx), 4, frame='walnut', row_h=0.42)
        # a lamp in the ceiling of each run
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        R.light(box(-0.16, -0.16, TH - 0.05, 0.16, 0.16, TH - 0.04, 'e_lamp', skip=('+z', '-x', '+x', '-y', '+y')).xform(a, mx, my))
    if nav:
        ids = [R.navpt(x, y) for (x, y) in pts]
        R.link(*ids)
    return ids


def make():
    R = Room('tunnels', 1, 1, res=1024)
    shell(R, None, floor='floor', wall='tile')
    R.meta['box'] = [[T, 0, T], [C - T, 4.2, C - T]]
    for s in 'NSEW':
        door_arch_cut(R, s, 2.9)
    S, E, N, W = (8, 2.9), (13.1, 8), (8, 13.1), (2.9, 8)
    tunnel(R, [S, (10.4, 3.5), (12.5, 5.3), E], door_ends=(0, 1))
    tunnel(R, [E, (12.9, 10.7), (10.9, 12.5), N], door_ends=(0, 1))
    tunnel(R, [N, (5.3, 12.7), (3.6, 10.9), W], door_ends=(0, 1))
    tunnel(R, [W, (3.3, 5.6), (5.6, 3.3), S], door_ends=(0, 1))
    # two spurs into the den
    tunnel(R, [(12.9, 10.7), (11.2, 9.6), (9.9, 8.0)])
    tunnel(R, [(3.3, 5.6), (5.0, 6.9), (6.1, 8.0)])
    # the den: an octagon of shelves with a lamp over a table
    ro = 2.0 / math.cos(math.pi / 8)
    oc = [(8 + ro * math.cos(math.pi / 8 + k * math.pi / 4), 8 + ro * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    R.cut(poly_prism(oc, 0, 2.6, side='tile', top='plaster', bottom='floor'))
    L = 2 * 2.0 * math.tan(math.pi / 8)
    for k in (1, 2, 3, 5, 6, 7):
        a = k * math.pi / 4
        shelf_at(R, 8 + 2.0 * math.cos(a), 8 + 2.0 * math.sin(a), 0, L - 0.1, a + math.pi, 5, frame='walnut')
    R.parts.add(cyl(8, 8, 0, 0.7, 0.12, 10, side='walnut', caps=False))
    R.parts.add(cyl(8, 8, 0.7, 0.75, 0.6, 20, side='walnut', top='walnut', bottom='walnut'))
    book(R, 8.1, 7.95, 0.75, 0.3, m='oxblood', open_=True)
    pendant(R, 8, 8, 1.95, r=0.2, top=2.6)
    R.light(cyl(8.35, 7.8, 0.75, 0.85, 0.03, 8, side='e_candle', top='e_candle', bottom='e_candle'))
    # night-lights in the ceiling at the ring's corners, for the night
    for (x, y) in ((12.5, 5.3), (10.9, 12.5), (3.6, 10.9), (5.6, 3.3)):
        R.light(box(x - 0.1, y - 0.1, TH - 0.02, x + 0.1, y + 0.1, TH - 0.01, 'e_candle', skip=('+z', '-x', '+x', '-y', '+y')))
    R.spot('probe', 8, 8, 1.6)
    R.meta.update(label='The Burrows', weight=5,
                  blurb='The shelves have closed in until there is no room left, only tunnels. Something made them. You hope it was people.')
    return R
