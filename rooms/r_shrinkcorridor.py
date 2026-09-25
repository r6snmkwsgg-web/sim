"""The Shrinking Corridor: a vaulted gallery that gets smaller as you walk down it. The doors, the
bookcases, the lamps and the arches all shrink with it, until you have to stoop, then crouch. At the
very end, a door the size of a cupboard opens into a warm room of perfectly ordinary size. Two plain
passages run along either side, and nobody who walks them would guess what lies between."""
from lib import *
from kit_h2 import *

XA, XB = T - 0.02, 23.0          # the corridor, from the west doorway to the little door
CY = 8.0
HW0, J0 = 3.1, 4.4               # half-width and jamb height at the mouth
S1 = 0.2                         # the scale at the far end
DOORX = [3.0]
PASS_NAV = []
PS = (T, 3.7)                    # the south passage (y range)
PN = (12.3, C - T)               # the north passage
PH = 4.2
HR = (23.5, 28.8, 4.4, 11.6)     # the hidden room
HH = 3.5
EX = 29.3                        # the east passage (x from here to the wall)


def s_at(x):
    t = (x - XA) / (XB - XA)
    return 1.0 + (S1 - 1.0) * t


def hw(x): return HW0 * s_at(x)
def jb(x): return J0 * s_at(x)


def section(x, segs=16):
    return arch_profile(CY, 2 * hw(x), 0.0, jb(x), segs)


def make():
    R = Room('shrinkcorridor', 2, 1, res=2048)
    W, D = R.W, R.D
    R.sockets(floor='floor', wall='tile')
    # the corridor: a vault lofted from full size to a fifth
    p0, p1 = section(XA), section(XB)
    R.cut(loft_x(p0, p1, XA, XB + 0.02, arch_mats(len(p0), 'floor', 'tile')))
    passages(R, W, D)
    corridor(R)
    hidden(R)
    R.spot('probe', 5.0, CY, 2.0)
    R.meta.update(label='The Shrinking Corridor', weight=4,
                  blurb='The corridor narrows as you go. So do the doors, and the bookcases, and the lamps. You tell yourself it is perspective until you have to duck.')
    R.meta['box'] = [[T, 0, T], [W - T, TOP, D - T]]
    return tidy(R)


def wall_pt(x, side):
    """A point on the south (side=-1) or north (+1) wall of the corridor at x."""
    return (x, CY + side * hw(x))


def corridor(R):
    L = XB - XA
    th = math.atan2(HW0 - HW0 * S1, L)            # the walls' lean in plan
    # the bays: each a little shorter than the last
    xs = [XA + 0.6]
    while True:
        nx = xs[-1] + 4.2 * s_at(xs[-1])
        if nx > XB - 0.6: break
        xs.append(nx)
    ribs = Geo()
    for k, x in enumerate(xs[1:]):
        s = s_at(x); h_, j_ = hw(x), jb(x); t = 0.22 * s; d = 0.4 * s
        # pilasters and an arch band standing out from the vault
        for side in (-1, 1):
            y0 = CY + side * h_
            ribs.add(box(x - d / 2, min(y0, y0 - side * t), 0, x + d / 2, max(y0, y0 - side * t), j_, 'tile'))
            ribs.add(box(x - d / 2 - 0.04 * s, min(y0, y0 - side * (t + 0.05 * s)), j_ - 0.14 * s, x + d / 2 + 0.04 * s, max(y0, y0 - side * (t + 0.05 * s)), j_, 'tile'))
        n = 14
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            q = [(CY + h_ * math.cos(a0), j_ + h_ * math.sin(a0)), (CY + h_ * math.cos(a1), j_ + h_ * math.sin(a1)),
                 (CY + (h_ - t) * math.cos(a1), j_ + (h_ - t) * math.sin(a1)), (CY + (h_ - t) * math.cos(a0), j_ + (h_ - t) * math.sin(a0))]
            ribs.add(prism(q, 'x', x - d / 2, x + d / 2, 'tile', cap='tile'))
    R.parts.add(weld(ribs))
    # between the ribs: bookcases, doors and lamps, all at the local scale
    doors_real = 1                      # the first bay's doors are real: they open to the side passages
    for k in range(len(xs) - 1):
        xa_, xb_ = xs[k] + 1.05 * s_at(xs[k]), xs[k + 1] - 0.3 * s_at(xs[k + 1])
        xm = (xa_ + xb_) / 2; s = s_at(xm)
        for side in (-1, 1):
            if k < doors_real:
                real_door(R, xm, side); DOORX[0] = xm
            elif (k + (side > 0)) % 2 == 0:
                fake_door(R, xm, side, th)
            else:
                wall_case(R, xa_ + 0.1 * s, xb_ - 0.1 * s, side, th)
        # a console and a green lamp on each side, between door and case
        # a pendant down the middle
        zc = jb(xm) + hw(xm) * 0.55
        top = jb(xm) + hw(xm) - 0.02
        R.nocol.add(cyl(xm, CY, zc + 0.2 * s, top, 0.012 * max(s, 0.4), 4, side='brass', caps=False))
        R.light(sphere(xm, CY, zc, 0.2 * s, 10, 5, 'e_lamp'))
        R.nocol.add(cyl(xm, CY, zc + 0.12 * s, zc + 0.26 * s, 0.24 * s, 10, side='brass', top='brass', bottom='brass'))
    # consoles with green lamps at every rib, on both sides
    for x in xs[1:]:
        s = s_at(x)
        for side in (-1, 1):
            yw = CY + side * hw(x) - side * (0.22 * s + 0.2 * s)
            y0, y1 = sorted((yw, yw - side * 0.35 * s))
            xc = x + 0.55 * s
            g = table(xc - 0.35 * s, y0, xc + 0.35 * s, y1, 0.8 * s, 'walnut')
            R.parts.add(g)
            green_lamp(R, xc, (y0 + y1) / 2, 0.8 * s, 0.0, s=s)
    # a runner down the floor, narrowing with it
    g = Geo()
    P = [(XA + 1.0, CY - 1.1), (XB - 0.1, CY - 1.1 * S1), (XB - 0.1, CY + 1.1 * S1), (XA + 1.0, CY + 1.1)]
    R.nocol.add(poly_prism(P, 0.0, 0.012, side='oxblood', top='carpet', bottom='carpet'))
    # the little door at the end, ajar
    s = S1
    dw, dh = 0.82, 1.24
    R.cut(box(XB - 0.05, CY - dw / 2, 0, HR[0] + 0.05, CY + dw / 2, dh, 'walnut', bottom='floor', top='walnut'))
    R.parts.add(box(XB - 0.06, CY - dw / 2 - 0.1, 0, XB, CY - dw / 2, dh + 0.1, 'walnut', skip=('-z',)))
    R.parts.add(box(XB - 0.06, CY + dw / 2, 0, XB, CY + dw / 2 + 0.1, dh + 0.1, 'walnut', skip=('-z',)))
    R.parts.add(box(XB - 0.06, CY - dw / 2 - 0.1, dh, XB, CY + dw / 2 + 0.1, dh + 0.1, 'walnut'))
    leaf = box(0, -0.04, 0, dw - 0.04, 0.0, dh - 0.03, 'oak')
    leaf.add(box(dw - 0.14, -0.08, 0.6, dw - 0.1, -0.04, 0.64, 'brass'))
    leaf.xform(math.pi / 2 + 1.1, HR[0] + 0.02, CY - dw / 2 + 0.02, 0)
    R.nocol.add(leaf)
    # warm light leaking under and round it
    R.light(box(XB + 0.2, CY - 0.3, 0.02, XB + 0.3, CY + 0.3, 0.05, 'e_candle'))
    # the walkers' path down the middle
    pts = [R.navpt(x, CY) for x in (2.0, DOORX[0], 6.5, 10.0, 14.0, 18.0, 21.5)]
    R.link(*pts)
    a, b = R.navpt(DOORX[0], (PS[0] + PS[1]) / 2), R.navpt(DOORX[0], (PN[0] + PN[1]) / 2)
    R.link(PASS_NAV[0], a, pts[1], b, PASS_NAV[1])
    return pts


def fake_door(R, x, side, th):
    s = s_at(x)
    dw, dh = 1.1 * s, 2.3 * s
    xw, yw = wall_pt(x, side)
    ang = th if side < 0 else math.pi - th     # local +y points into the corridor
    g = Geo()
    g.add(box(-dw / 2 - 0.12 * s, 0, 0, dw / 2 + 0.12 * s, 0.06 * s, dh + 0.14 * s, 'walnut'))
    g.add(box(-dw / 2, 0.06 * s, 0, dw / 2, 0.1 * s, dh, 'oak', sides='walnut'))
    for (z0, z1) in ((0.15, 0.95), (1.2, 2.1)):
        g.add(box(-dw / 2 + 0.12 * s, 0.1 * s, z0 * s, dw / 2 - 0.12 * s, 0.12 * s, z1 * s, 'walnut'))
    g.add(box(dw / 2 - 0.2 * s, 0.1 * s, 1.0 * s, dw / 2 - 0.13 * s, 0.17 * s, 1.07 * s, 'brass'))
    g.xform(ang, xw, yw)
    R.parts.add(weld(g))


def wall_case(R, x0, x1, side, th):
    s = s_at((x0 + x1) / 2)
    rows = max(2, int(jb((x0 + x1) / 2) * 0.92 / (0.42 * s)))
    if side < 0:
        x, y = wall_pt(x0, side)
        shelf(R, x, y + 0.01, 0, (x1 - x0) / math.cos(th), (math.pi / 2 + th) if side < 0 else (-math.pi / 2 - th), rows=rows, row_h=0.42 * s, depth=0.34 * s,
              frame='walnut', board=0.035 * s, top_gap=0.08 * s)
    else:
        x, y = wall_pt(x1, side)
        shelf(R, x, y - 0.01, 0, (x1 - x0) / math.cos(th), (math.pi / 2 + th) if side < 0 else (-math.pi / 2 - th), rows=rows, row_h=0.42 * s, depth=0.34 * s,
              frame='walnut', board=0.035 * s, top_gap=0.08 * s)


def real_door(R, x, side):
    """A doorway through the corridor's wall into the side passage."""
    s = s_at(x)
    dw, dh = 1.6, 2.6
    y0, y1 = (PS[1] - 0.05, CY - hw(x) + 0.3) if side < 0 else (CY + hw(x) - 0.3, PN[0] + 0.05)
    pr = arch_profile(x, dw, 0, dh - dw / 2, 12)
    R.cut(prism(pr, 'y', y0, y1, arch_mats(len(pr), 'floor', 'tile')))


def passages(R, W, D):
    """Two plain vaulted passages along the long walls and one across the east end."""
    for (y0, y1) in (PS, PN):
        R.cut(box(T - 0.02, y0 - (0.02 if y0 < 1 else 0), 0, W - T + 0.02, y1 + (0.02 if y1 > D - 1 else 0), PH, 'tile', bottom='floor', top='plaster'))
    R.cut(box(EX, T - 0.02, 0, W - T + 0.02, D - T + 0.02, PH, 'tile', bottom='floor', top='plaster'))
    # bookcases along the outer walls, broken at the doorways
    for (a, b) in ((0.6, 6.0), (10.0, 22.0), (26.0, EX - 0.2)):
        sh(R, '+y', T, a, b, rows=8, frame='oak')
        sh(R, '-y', D - T, a, b, rows=8, frame='oak')
    # the inner walls, where the corridor's wall is thick enough
    for (a, b) in ((8.0, 22.5), (24.2, 28.6)):
        sh(R, '-y', PS[1], a, b, rows=7, frame='oak')
        sh(R, '+y', PN[0], a, b, rows=7, frame='oak')
    sh(R, '-x', W - T, T + 0.3, 6.0, rows=8, frame='oak')
    sh(R, '-x', W - T, 10.0, D - T - 0.3, rows=8, frame='oak')
    # lamps
    for x in (3.0, 11.0, 16.0, 21.0, 27.0):
        for y in ((PS[0] + PS[1]) / 2, (PN[0] + PN[1]) / 2):
            bulb(R, x, y, PH - 0.9, r=0.13, m='e_lamp', top=PH, shade='brass')
    bulb(R, (EX + W - T) / 2, CY, PH - 0.9, r=0.13, m='e_lamp', top=PH, shade='brass')
    for (x, y) in ((EX + 0.4, 2.2), (EX + 0.4, D - 2.2)):
        R.light(box(x - 0.05, y - 0.15, 2.6, x, y + 0.15, 2.75, 'e_exit'))
    # benches along the passages
    for x in (14.5, 19.0):
        R.parts.add(box(x - 1.0, PS[1] - 0.8, 0.42, x + 1.0, PS[1] - 0.4, 0.48, 'walnut', sides='walnut'))
        R.parts.add(box(x - 0.9, PS[1] - 0.75, 0, x + 0.9, PS[1] - 0.45, 0.42, 'walnut', skip=('-z',)))
        R.spot('sit', x, PS[1] - 0.6, 0.48, -math.pi / 2)
    ys, yn = (PS[0] + PS[1]) / 2, (PN[0] + PN[1]) / 2
    xe = (EX + W - T) / 2
    loop_ = navloop(R, [(1.5, ys), (8.0, ys), (16.0, ys), (24.0, ys), (xe, ys), (xe, CY), (xe, yn), (24.0, yn), (16.0, yn), (8.0, yn), (1.5, yn)], close=False)
    PASS_NAV[:] = [loop_[0], loop_[-1]]


def hidden(R):
    x0, x1, y0, y1 = HR
    R.cut(box(x0, y0, 0, x1, y1, HH, 'damask', bottom='floor', top='plaster'))
    # a wainscot, bookcases, a fireplace of candles, an armchair and a bed
    R.parts.add(box(x0, y0, 0, x1, y0 + 0.04, 0.9, 'walnut', skip=('-z',)))
    sh(R, '-x', x1, y0 + 0.3, y1 - 0.3, rows=7, frame='walnut')
    sh(R, '-y', y1, x0 + 1.5, x1 - 0.5, rows=7, frame='walnut')
    # a rug
    R.nocol.add(box(x0 + 1.2, y0 + 1.4, 0, x1 - 1.3, y1 - 1.8, 0.012, 'carpet', sides='oxblood'))
    # armchair and side table with a lamp
    ax, ay = x0 + 2.8, y0 + 3.2
    R.parts.add(box(ax - 0.45, ay - 0.45, 0, ax + 0.45, ay + 0.45, 0.45, 'velvet', skip=('-z',)))
    R.parts.add(box(ax - 0.45, ay + 0.3, 0.45, ax + 0.45, ay + 0.45, 1.1, 'velvet'))
    R.parts.add(box(ax - 0.45, ay - 0.45, 0.45, ax - 0.3, ay + 0.3, 0.7, 'velvet'))
    R.parts.add(box(ax + 0.3, ay - 0.45, 0.45, ax + 0.45, ay + 0.3, 0.7, 'velvet'))
    R.spot('sit', ax, ay - 0.05, 0.45, -math.pi / 2)
    R.parts.add(table(ax + 0.7, ay - 0.3, ax + 1.3, ay + 0.3, 0.62, 'walnut'))
    green_lamp(R, ax + 1.0, ay, 0.62, math.pi / 2)
    open_book_prop(R, ax - 0.1, ay - 0.7, 0.012, 0.4)
    # the bed along the south wall
    R.parts.add(box(x1 - 2.4, y0 + 0.1, 0, x1 - 0.5, y0 + 1.1, 0.5, 'bed', sides='walnut'))
    R.parts.add(box(x1 - 0.55, y0 + 0.1, 0, x1 - 0.45, y0 + 1.1, 1.0, 'walnut'))
    R.nocol.add(box(x1 - 1.0, y0 + 0.2, 0.5, x1 - 0.6, y0 + 1.0, 0.62, 'ivory'))
    R.spot('bed', x1 - 1.4, y0 + 0.6, 0.5, math.pi)
    # candles on the mantel of a blind fireplace
    fx0 = x0 + 0.9
    R.parts.add(box(fx0, y0, 0, fx0 + 0.2, y0 + 0.5, 1.1, 'tile'))
    R.parts.add(box(fx0 + 1.4, y0, 0, fx0 + 1.6, y0 + 0.5, 1.1, 'tile'))
    R.parts.add(box(fx0 - 0.1, y0, 1.1, fx0 + 1.7, y0 + 0.6, 1.22, 'tile'))
    R.parts.add(box(fx0 + 0.2, y0, 0, fx0 + 1.4, y0 + 0.1, 1.1, 'black'))
    for k in range(4):
        candle(R, fx0 + 0.15 + k * 0.45, y0 + 0.3, 1.22, h=0.18 + 0.05 * (k % 2))
    for k in range(3):
        candle(R, fx0 + 0.5 + k * 0.3, y0 + 0.3, 0.0, h=0.3 + 0.1 * k)
    bulb(R, (x0 + x1) / 2, (y0 + y1) / 2, HH - 0.8, r=0.14, m='e_lamp', top=HH, shade='brass')
    R.spot('plaque', x0 + 0.6, y1 - 0.2, 1.4, -math.pi / 2)
    secret(R, (x0 + x1) / 2, (y0 + y1) / 2, 0.0, 'The Room at the End',
           'You crawled through a door made for a child and stood up in a room of ordinary size, warm and lit. It is bigger than the corridor was.', r=2.5)
    a, b, c = R.navpt(XB - 0.2, CY), R.navpt(x0 + 1.0, CY), R.navpt(x0 + 2.2, y0 + 1.5)
    R.link(a, b, c)
