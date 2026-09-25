"""Bigger on the Inside: every doorway leads into a plain little room, cream plaster and a bare bulb,
with a plain wooden door standing open in its far wall. Through the door, a reading hall so large its
far end is blue with distance: reading tables in rows, bookcases to the horizon, clouds drifting in the
coffers of the ceiling. On the far wall, ladders climb from ledge to ledge to a catwalk under the
ceiling, and the catwalk leads to a door painted into a patch of sky."""
from lib import *
from kit_h2 import *

B = 4.6               # the band of little rooms round the hall
VH = 3.0              # their ceiling
HT = 15.35
BAY = None
CAT = 11.4            # the catwalk
SR = (43.4, 50.4, 59.75, 63.2)    # the room behind the door in the sky (x0, x1, y0, y1), floor at CAT
SKYD = 46.6           # the door's x


def make():
    R = Room('biggerinside', 4, 4, levels=2, res=2048)
    W, D = R.W, R.D
    seal_sockets(R, all_sockets_except(R), floor='floor', wall='tile')
    R.cut(box(B, B, 0, W - B, D - B, HT, 'tile', bottom='marble', top='plaster'))
    vestibules(R, W, D)
    ceiling(R, W, D)
    walls(R, W, D)
    tables(R, W, D)
    climb(R, W, D)
    fx(R, 'fog', [B, B, 0.0, W - B, D - B, HT], density=0.03)
    R.spot('probe', 32.0, 32.0, 3.0)
    R.meta.update(label='Bigger on the Inside', weight=3,
                  blurb='A small plain room with a plain door. You open it, and the library opens with it, further than the building could possibly go.')
    R.meta['box'] = [[T, 0, T], [W - T, HT, D - T]]
    return tidy(R)


def doors_list(W, D):
    out = []
    for i in range(4):
        c = i * C + C / 2
        out.append(('S', c)); out.append(('N', c)); out.append(('W', c)); out.append(('E', c))
    return out


def vestibules(R, W, D):
    """A little room inside each doorway, and a plain door into the hall."""
    hw = 2.5
    for (side, c) in doors_list(W, D):
        if side == 'S':
            vb = (c - hw, T - 0.02, c + hw, B - 0.3); door = ('y', c, B - 0.32, B + 0.02)
        elif side == 'N':
            vb = (c - hw, D - B + 0.3, c + hw, D - T + 0.02); door = ('y', c, D - B - 0.02, D - B + 0.32)
        elif side == 'W':
            vb = (T - 0.02, c - hw, B - 0.3, c + hw); door = ('x', c, B - 0.32, B + 0.02)
        else:
            vb = (W - B + 0.3, c - hw, W - T + 0.02, c + hw); door = ('x', c, W - B - 0.02, W - B + 0.32)
        x0, y0, x1, y1 = vb
        R.cut(box(x0, y0, 0, x1, y1, VH, 'ivory', bottom='floor', top='plaster'))
        # the plain door: an opening 1.2 x 2.25, a frame, the leaf standing open into the hall
        ax, cc, a0, a1 = door
        dw, dh = 1.2, 2.25
        if ax == 'y':
            R.cut(box(cc - dw / 2, a0, 0, cc + dw / 2, a1, dh, 'oak', bottom='floor', top='oak'))
        else:
            R.cut(box(a0, cc - dw / 2, 0, a1, cc + dw / 2, dh, 'oak', bottom='floor', top='oak'))
        leaf = box(0, 0, 0, dw - 0.05, 0.05, dh - 0.03, 'oak')
        leaf.add(box(dw - 0.2, 0.05, 0.95, dw - 0.14, 0.1, 1.01, 'brass'))
        leaf.add(box(dw - 0.2, -0.05, 0.95, dw - 0.14, 0.0, 1.01, 'brass'))
        inward = {'S': (0, 1), 'N': (0, -1), 'W': (1, 0), 'E': (-1, 0)}[side]
        # hinge at one jamb on the hall side; the leaf swung 100 degrees into the hall
        if side == 'S': hx, hy, ang = cc - dw / 2, B + 0.02, math.radians(100)
        elif side == 'N': hx, hy, ang = cc + dw / 2, D - B - 0.02, math.radians(280)
        elif side == 'W': hx, hy, ang = B + 0.02, cc + dw / 2, math.radians(10)
        else: hx, hy, ang = W - B - 0.02, cc - dw / 2, math.radians(190)
        R.nocol.add(leaf.xform(ang, hx, hy, 0))
        # a frame round the opening on the hall side
        if ax == 'y':
            yy = B if side == 'S' else D - B
            s = 1 if side == 'S' else -1
            for xx in (cc - dw / 2 - 0.12, cc + dw / 2):
                R.parts.add(box(xx, min(yy, yy + s * 0.06), 0, xx + 0.12, max(yy, yy + s * 0.06), dh + 0.12, 'oak'))
            R.parts.add(box(cc - dw / 2 - 0.12, min(yy, yy + s * 0.06), dh, cc + dw / 2 + 0.12, max(yy, yy + s * 0.06), dh + 0.12, 'oak'))
        else:
            xx = B if side == 'W' else W - B
            s = 1 if side == 'W' else -1
            for yy in (cc - dw / 2 - 0.12, cc + dw / 2):
                R.parts.add(box(min(xx, xx + s * 0.06), yy, 0, max(xx, xx + s * 0.06), yy + 0.12, dh + 0.12, 'oak'))
            R.parts.add(box(min(xx, xx + s * 0.06), cc - dw / 2 - 0.12, dh, max(xx, xx + s * 0.06), cc + dw / 2 + 0.12, dh + 0.12, 'oak'))
        # a bare bulb, a chair against the wall, a row of coat hooks, a skirting
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        bulb(R, mx, my, VH - 0.6, r=0.1, m='e_lamp', top=VH)
        # the chair sits by a side wall, clear of the door and the way through
        if side in 'SN':
            px, py, a = x1 - 0.45, my + (0.6 if side == 'S' else -0.6), math.pi
            R.nocol.add(box(x0 + 0.02, my - 0.6, 1.75, x0 + 0.06, my + 0.6, 1.8, 'walnut'))
            for k in range(4): R.nocol.add(box(x0 + 0.02, my - 0.45 + k * 0.3, 1.62, x0 + 0.12, my - 0.42 + k * 0.3, 1.75, 'brass'))
        else:
            px, py, a = mx + (0.6 if side == 'W' else -0.6), y1 - 0.45, -math.pi / 2
            R.nocol.add(box(mx - 0.6, y0 + 0.02, 1.75, mx + 0.6, y0 + 0.06, 1.8, 'walnut'))
            for k in range(4): R.nocol.add(box(mx - 0.45 + k * 0.3, y0 + 0.02, 1.62, mx - 0.42 + k * 0.3, y0 + 0.12, 1.75, 'brass'))
        R.parts.add(chair(px, py, a))
        R.spot('sit', px, py, 0.48, a)
        # nav: doorway, little room, the door, into the hall
        if side == 'S': pts = [(c, 1.4), (c, B - 0.9), (c, B + 1.4)]
        elif side == 'N': pts = [(c, D - 1.4), (c, D - B + 0.9), (c, D - B - 1.4)]
        elif side == 'W': pts = [(1.4, c), (B - 0.9, c), (B + 1.4, c)]
        else: pts = [(W - 1.4, c), (W - B + 0.9, c), (W - B - 1.4, c)]
        ids = [R.navpt(x, y) for (x, y) in pts]
        R.link(*ids)
        NAV.setdefault('in', []).append(ids[-1])


NAV = {}


def ceiling(R, W, D):
    """A coffered ceiling: deep beams, and in three long bands of coffers, the sky."""
    n = 10
    step = (W - 2 * B) / n
    g = Geo()
    for k in range(n + 1):
        a = B + k * step
        g.add(box(a - 0.3, B, HT - 1.0, a + 0.3, D - B, HT, 'plaster', top='plaster', skip=('+z',)))
        g.add(box(B, a - 0.3, HT - 1.0, W - B, a + 0.3, HT, 'plaster', top='plaster', skip=('+z',)))
    R.parts.add(g)
    sky = Geo(); pan = Geo()
    for i in range(n):
        for j in range(n):
            x0, y0 = B + i * step + 0.3, B + j * step + 0.3
            x1, y1 = x0 + step - 0.6, y0 + step - 0.6
            if i in (2, 5, 7):
                sky.add(box(x0, y0, HT - 0.04, x1, y1, HT - 0.02, 'e_skydome', skip=('+z',)))
            elif (i + j) % 3 == 0:
                pan.add(box(x0 + 1.2, y0 + 1.2, HT - 0.04, x1 - 1.2, y1 - 1.2, HT - 0.02, 'e_panel', skip=('+z',)))
            else:
                R.parts.add(box((x0 + x1) / 2 - 0.35, (y0 + y1) / 2 - 0.35, HT - 0.1, (x0 + x1) / 2 + 0.35, (y0 + y1) / 2 + 0.35, HT - 0.02, 'gilt', skip=('+z',)))
    R.light(sky); R.light(pan)


def walls(R, W, D):
    """Bookcases round the hall between the little doors; above them tall windows full of daylight."""
    rows = 12
    for k in range(4):
        a, b = k * C + (0.4 if k else B + 0.1), k * C + C / 2 - 1.2
        c_, d = k * C + C / 2 + 1.2, (k + 1) * C - (0.4 if k < 3 else B + 0.1)
        for (p, q) in ((a, b), (c_, d)):
            if q - p < 1.0: continue
            sh(R, '+y', B, p, q, rows=rows, frame='walnut')
            sh(R, '-x', W - B, p, q, rows=rows, frame='walnut')
            sh(R, '+x', B, p, q, rows=rows, frame='walnut')
            if not (42.5 < p < 54 or 42.5 < q < 54):
                sh(R, '-y', D - B, p, q, rows=rows, frame='walnut')
        # over each little door, a short case
        for (face, bk) in (('+y', B), ('-y', D - B), ('+x', B), ('-x', W - B)):
            sh(R, face, bk, k * C + C / 2 - 1.2, k * C + C / 2 + 1.2, z=2.6, rows=6, frame='walnut')
    # a cornice over the bookcases
    zc = rows * 0.42 + 0.2
    for (x0, y0, x1, y1) in ((B, B, W - B, B + 0.5), (B, D - B - 0.5, W - B, D - B), (B, B, B + 0.5, D - B), (W - B - 0.5, B, W - B, D - B)):
        R.parts.add(box(x0, y0, zc, x1, y1, zc + 0.35, 'tile'))
    # tall windows above, recessed into the band, lit like afternoon
    for k in range(10):
        c = B + (k + 0.5) * (W - 2 * B) / 10
        for side in 'SWE' + ('N' if not (SR[0] - 1.5 < c < SR[1] + 1.5) else ''):
            pr = arch_profile(c, 2.4, 7.0, 4.2, 12)
            if side in 'SN':
                y0, y1 = (B - 0.35, B + 0.02) if side == 'S' else (D - B - 0.02, D - B + 0.35)
                R.cut(prism(pr, 'y', y0, y1, 'tile'))
                yl = B - 0.3 if side == 'S' else D - B + 0.28
                R.light(prism(pr, 'y', yl, yl + 0.02, 'e_sky', cap='e_sky'))
            else:
                x0, x1 = (B - 0.35, B + 0.02) if side == 'W' else (W - B - 0.02, W - B + 0.35)
                R.cut(prism(pr, 'x', x0, x1, 'tile'))
                xl = B - 0.3 if side == 'W' else W - B + 0.28
                R.light(prism(pr, 'x', xl, xl + 0.02, 'e_sky', cap='e_sky'))


def tables(R, W, D):
    """Long reading tables in rows, green lamps all down them; tall stacks down both sides."""
    tg = Geo(); lamps = Geo(); shade = Geo()
    xs = [11.0 + k * 4.6 for k in range(10)]
    xs = [x for x in xs if abs(x - 32.0) > 2.5]
    for x in xs:
        for (y0, y1) in ((9.5, 18.5), (21.5, 30.0), (34.0, 42.5), (45.5, 54.5)):
            tg.add(box(x - 0.6, y0, 0.72, x + 0.6, y1, 0.78, 'walnut', top='leather'))
            tg.add(box(x - 0.5, y0 + 0.1, 0, x + 0.5, y0 + 0.3, 0.72, 'walnut', skip=('-z', '+z')))
            tg.add(box(x - 0.5, y1 - 0.3, 0, x + 0.5, y1 - 0.1, 0.72, 'walnut', skip=('-z', '+z')))
            tg.add(box(x - 0.04, y0 + 0.3, 0.78, x + 0.04, y1 - 0.3, 1.05, 'walnut', skip=('-z',)))
            n = int((y1 - y0) / 2.2)
            for k in range(n):
                y = y0 + (k + 0.5) * (y1 - y0) / n
                shade.add(box(x - 0.07, y - 0.18, 1.12, x + 0.07, y + 0.18, 1.2, 'green', skip=('-z',)))
                shade.add(box(x - 0.012, y - 0.012, 1.05, x + 0.012, y + 0.012, 1.12, 'brass', skip=('-z', '+z')))
                lamps.add(box(x - 0.055, y - 0.16, 1.11, x + 0.055, y + 0.16, 1.12, 'e_lamp', skip=('+z',)))
    R.parts.add(tg); R.nocol.add(shade); R.light(lamps)
    # tall stacks down both sides, like a street going away
    for x in (7.5, W - 7.5):
        for (y0, y1) in ((9.0, 22.0), (26.0, 38.0), (42.0, 55.0)):
            stack(R, 'y', x, y0, y1, rows=14, frame='walnut')
    # chairs, a few, pushed back
    rnd = random.Random(2)
    for k in range(30):
        x = rnd.choice(xs) + rnd.choice((-1, 1)) * 0.95
        y = rnd.uniform(10.0, 54.0)
        if any(a - 0.5 < y < b + 0.5 for (a, b) in ((18.5, 21.5), (30.0, 34.0), (42.5, 45.5))): continue
        R.parts.add(chair(x, y, 0.0 if x % 4.6 > 2 else math.pi))
    # walkers: up the middle and along the rows
    mid = [R.navpt(32.0, y) for y in (6.5, 20.0, 32.0, 44.0, 57.5)]
    R.link(*mid)
    ring_ = navloop(R, [(6.2, 6.2), (32.0, 6.2), (W - 6.2, 6.2), (W - 6.2, 20.0), (W - 6.2, 32.0), (W - 6.2, 44.0), (W - 6.2, D - 6.2), (32.0, D - 6.2),
                        (6.2, D - 6.2), (6.2, 44.0), (6.2, 32.0), (6.2, 20.0)])
    R.link(mid[0], ring_[1]); R.link(mid[-1], ring_[7])
    for a in NAV['in']:
        p = R.nav[a]
        best = min(ring_, key=lambda b: math.hypot(R.nav[b][0] - p[0], R.nav[b][1] - p[1]))
        R.link(a, best)
    NAV['ring'] = ring_


def climb(R, W, D):
    """Up the far (north) wall: ladders from ledge to ledge to a catwalk, and the door in the sky."""
    yw = D - B                     # the north face of the hall
    yf = yw - 0.34                 # the bookcases' front
    # three platforms on iron brackets, stepping east and west up the wall, each reached by a
    # library ladder that runs along the bookcases
    L1, L2 = 3.8, 7.6
    lw = 1.6
    yl = 58.5                  # the ladders' line
    run = 3.8
    P1, P2, P3 = (45.6, 52.0), (50.4, 55.0), (42.9, 50.7)
    for (z, (x0, x1)) in ((L1, P1), (L2, P2), (CAT, P3)):
        R.parts.add(box(x0, yf - lw, z - 0.2, x1, yf, z, 'iron', top='oak'))
        rails(R, [(x0 + 0.3, yf - lw + 0.04), (x1 - 0.3, yf - lw + 0.04)], z=z)
        for x in (x0 + 0.3, (x0 + x1) / 2, x1 - 0.3):
            R.parts.add(beam((x, yf, z - 1.2), (x, yf - lw + 0.1, z - 0.2), 0.08, 'iron'))
    # end rails, open where a ladder arrives
    rails(R, [(P1[0] + 0.04, yf - lw), (P1[0] + 0.04, yl - 0.45)], z=L1); rails(R, [(P1[0] + 0.3, yf - lw + 0.04), (P1[0] + 0.04, yf - lw + 0.04)], z=L1)
    rails(R, [(P1[1] - 0.04, yf - lw), (P1[1] - 0.04, yf)], z=L1); rails(R, [(P1[1] - 0.3, yf - lw + 0.04), (P1[1] - 0.04, yf - lw + 0.04)], z=L1)
    rails(R, [(P2[0] + 0.04, yf - lw), (P2[0] + 0.04, yl - 0.45)], z=L2); rails(R, [(P2[0] + 0.3, yf - lw + 0.04), (P2[0] + 0.04, yf - lw + 0.04)], z=L2)
    rails(R, [(P2[1] - 0.04, yf - lw), (P2[1] - 0.04, yf)], z=L2); rails(R, [(P2[1] - 0.3, yf - lw + 0.04), (P2[1] - 0.04, yf - lw + 0.04)], z=L2)
    rails(R, [(P3[0] + 0.04, yf - lw), (P3[0] + 0.04, yf)], z=CAT); rails(R, [(P3[0] + 0.3, yf - lw + 0.04), (P3[0] + 0.04, yf - lw + 0.04)], z=CAT)
    rails(R, [(P3[1] - 0.04, yf - lw), (P3[1] - 0.04, yl - 0.45)], z=CAT); rails(R, [(P3[1] - 0.3, yf - lw + 0.04), (P3[1] - 0.04, yf - lw + 0.04)], z=CAT)
    # the bookcases here carry on up the wall
    sh(R, '-y', yw, 42.6, 53.8, rows=12, frame='walnut')
    sh(R, '-y', yw, 42.6, 53.8, z=5.4, rows=14, frame='walnut')
    sh(R, '-y', yw, 42.6, 53.8, z=11.4 + 3.4, rows=0, frame='walnut') if False else None
    # the ladders
    climb_ladder(R, P1[0] + 0.05, yl, 0.0, L1, math.pi, run=run)
    climb_ladder(R, P2[0] + 0.05, yl, L1, L2, math.pi, run=run)
    climb_ladder(R, P3[1] - 0.05, yl, L2, CAT, 0.0, run=run)
    # the door in the sky: a patch of painted sky on the wall round it, the door ajar
    dx, dw, dh = SKYD, 1.2, 2.2
    R.cut(box(dx - dw / 2, yw - 0.05, CAT, dx + dw / 2, SR[2] + 0.05, CAT + dh, 'oak', bottom='oak', top='oak'))
    R.light(box(dx - 3.2, yw - 0.02, CAT - 0.4, dx - dw / 2 - 0.15, yw - 0.005, CAT + 3.4, 'e_skydome'))
    R.light(box(dx + dw / 2 + 0.15, yw - 0.02, CAT - 0.4, dx + 3.2, yw - 0.005, CAT + 3.4, 'e_skydome'))
    R.light(box(dx - dw / 2 - 0.15, yw - 0.02, CAT + dh + 0.15, dx + dw / 2 + 0.15, yw - 0.005, CAT + 3.4, 'e_skydome'))
    for xx in (dx - dw / 2 - 0.15, dx + dw / 2):
        R.parts.add(box(xx, yw - 0.08, CAT, xx + 0.15, yw, CAT + dh + 0.15, 'ivory'))
    R.parts.add(box(dx - dw / 2 - 0.15, yw - 0.08, CAT + dh, dx + dw / 2 + 0.15, yw, CAT + dh + 0.15, 'ivory'))
    leaf = box(0, -0.05, 0, dw - 0.05, 0.0, dh - 0.03, 'e_skydome')
    R.light(leaf.xform(-math.radians(70), dx - dw / 2 + 0.02, yw - 0.02, CAT))
    # the room behind: a garret above the sky
    x0, x1, y0, y1 = SR
    R.cut(box(x0, y0, CAT, x1, y1, CAT + 3.1, 'plaster', bottom='floor', top='walnut'))
    for k in range(5):
        x = x0 + 0.6 + k * 1.6
        R.nocol.add(box(x - 0.07, y0, CAT + 2.9, x + 0.07, y1, CAT + 3.1, 'walnut'))
    R.parts.add(box(x1 - 2.2, y1 - 1.0, CAT, x1 - 0.2, y1 - 0.1, CAT + 0.45, 'bed', sides='walnut'))
    R.nocol.add(box(x1 - 0.7, y1 - 0.9, CAT + 0.45, x1 - 0.3, y1 - 0.2, CAT + 0.56, 'ivory'))
    R.spot('bed', x1 - 1.2, y1 - 0.55, CAT + 0.45, 0.0)
    desk(R, x0 + 0.3, y1 - 0.9, x0 + 2.0, y1 - 0.15, z=CAT, h=0.76)
    green_lamp(R, x0 + 1.6, y1 - 0.5, CAT + 0.76)
    open_book_prop(R, x0 + 0.9, y1 - 0.5, CAT + 0.76)
    seat(R, x0 + 1.1, y1 - 1.35, math.pi / 2, z=CAT)
    sh(R, '+x', x0, y0 + 0.2, y1 - 1.2, z=CAT, rows=6, frame='walnut', depth=0.28)
    # a little window looking down into the hall, through the painted sky
    R.cut(box(x1 - 1.6, yw - 0.05, CAT + 1.2, x1 - 0.6, y0 + 0.05, CAT + 1.9, 'plaster'))
    bulb(R, (x0 + x1) / 2, (y0 + y1) / 2, CAT + 2.4, r=0.1, m='e_lamp', top=CAT + 2.9)
    candle(R, x1 - 1.1, y0 + 0.3, CAT + 0.76 - 0.76, h=0.2, stand=0.8)
    R.spot('plaque', x0 + 3.5, y1 - 0.1, CAT + 1.5, -math.pi / 2)
    secret(R, (x0 + x1) / 2, (y0 + y1) / 2, CAT, 'The Door in the Sky',
           'Up three ladders and along a catwalk under the clouds there is a door, painted round with sky. Behind it, a garret with a bed, a lamp and a window looking down on all of it.', r=2.2)
    # nav up the ladders
    ids = [R.navpt(P1[0] - run - 0.8, yl, 0.0), R.navpt(P1[0] + 0.6, yl, L1), R.navpt(P2[0] - run - 0.2, yl, L1), R.navpt(P2[0] + 0.6, yl, L2),
           R.navpt(P3[1] + run + 0.2, yl, L2), R.navpt(P3[1] - 0.6, yl, CAT), R.navpt(dx, yl, CAT), R.navpt(dx, y0 + 0.9, CAT)]
    R.link(*ids)
    best = min(NAV['ring'], key=lambda b: math.hypot(R.nav[b][0] - R.nav[ids[0]][0], R.nav[b][1] - R.nav[ids[0]][1]))
    R.link(ids[0], best)
