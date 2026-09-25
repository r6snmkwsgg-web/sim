"""The Stair Forest: a parquet floor sixty metres square, planted with staircases. Short flights that
climb to a railed landing and stop; flights that start in mid-air and go nowhere; flights hanging upside
down from the ceiling; spirals twisting round each other up into the fog. Four grand flights come down
from doorways in the walls. One spiral, if you climb it all the way, reaches a reading platform up
among the ceiling lights, where somebody left their lamp on."""
from lib import *
from kit_h2 import *

N = 8                 # cells of 8 m; stairs stand inside them, 2 m lanes between
HT = 15.35
SEC = (5, 5)          # the secret spiral's cell
BAL = {('W', 1): 'W', ('E', 2): 'E', ('N', 2): 'N', ('S', 1): 'S'}   # upper doorways with balconies


def make():
    R = Room('stairforest', 4, 4, levels=2, res=2048)
    W, D = R.W, R.D
    keep = list((s, i, 1) for (s, i) in BAL)
    seal_sockets(R, all_sockets_except(R, keep=keep), floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, HT, 'tile', bottom='floor', top='plaster'))
    used = set()
    balconies(R, W, D, used)
    secret_spiral(R, used)
    forest(R, used)
    walls(R, W, D)
    lights(R, W, D)
    fx(R, 'fog', [T, T, 0.0, W - T, D - T, HT], density=0.025)
    fx(R, 'fog', [T, T, 7.0, W - T, D - T, HT], density=0.07)
    R.spot('probe', 32.0, 32.0, 2.5)
    R.meta.update(label='The Stair Forest', weight=3,
                  blurb='Staircases, hundreds of them, going up into the mist. Most of them stop. Some of them start in the air. You have the feeling that one of them goes somewhere.')
    R.meta['box'] = [[T, 0, T], [W - T, HT, D - T]]
    return tidy(R)


def cell_of(x, y):
    return (int(x // 8), int(y // 8))


def balconies(R, W, D, used):
    """At four upper doorways a railed balcony, and a grand flight down from it into the room."""
    z = LH
    n, rise, run, wd = 40, LH / 40, 0.28, 2.0
    L = n * run
    for (side, i), _ in BAL.items():
        c = i * C + C / 2
        if side == 'W':
            bx = (T, c - 2.5, T + 3.2, c + 2.5); fx0, fy0, ax = T + 3.2 + L, c - wd / 2, '-x'
        elif side == 'E':
            bx = (W - T - 3.2, c - 2.5, W - T, c + 2.5); fx0, fy0, ax = W - T - 3.2 - L, c - wd / 2, '+x'
        elif side == 'N':
            bx = (c - 2.5, D - T - 3.2, c + 2.5, D - T); fx0, fy0, ax = c - wd / 2, D - T - 3.2 - L, '+y'
        else:
            bx = (c - 2.5, T, c + 2.5, T + 3.2); fx0, fy0, ax = c - wd / 2, T + 3.2 + L, '-y'
        x0, y0, x1, y1 = bx
        R.parts.add(box(x0, y0, z - 0.45, x1, y1, z, 'walnut', top='oak'))
        for (px, py) in ((x0 + 0.3 if side != 'W' else x1 - 0.3, y0 + 0.3), (x1 - 0.3 if side != 'E' else x0 + 0.3, y1 - 0.3)):
            pass
        # the flight, foot on the floor, climbing to the balcony over the doorway below
        hung_flight(R, fx0, fy0, 0.0, wd, n, rise, run, ax)
        # balcony rails, open where the stair arrives
        if side in 'WE':
            xe = x1 if side == 'W' else x0
            rails(R, [(xe, y0), (xe, fy0)]); rails(R, [(xe, fy0 + wd), (xe, y1)])
            rails(R, [(x0, y0 + 0.04), (x1, y0 + 0.04)]); rails(R, [(x0, y1 - 0.04), (x1, y1 - 0.04)])
            for k in range(0, 4):
                pass
        else:
            ye = y0 if side == 'N' else y1
            rails(R, [(x0, ye), (fx0, ye)]); rails(R, [(fx0 + wd, ye), (x1, ye)])
            rails(R, [(x0 + 0.04, y0), (x0 + 0.04, y1)]); rails(R, [(x1 - 0.04, y0), (x1 - 0.04, y1)])
        # brackets under it, into the wall
        for (px, py) in ((x0 + 0.2, y0 + 0.2), (x1 - 0.2, y0 + 0.2), (x0 + 0.2, y1 - 0.2), (x1 - 0.2, y1 - 0.2)):
            if side == 'W' and px < 2: continue
            if side == 'E' and px > W - 2: continue
            if side == 'S' and py < 2: continue
            if side == 'N' and py > D - 2: continue
            R.parts.add(beam((px, py, z - 0.45), (px, py, z - 2.2), 0.14, 'walnut'))
        # newel lamps at the foot
        if ax[1] == 'x':
            xf = fx0 if ax == '+x' else fx0
            for y in (fy0 - 0.15, fy0 + wd + 0.15):
                newel(R, xf + (-0.25 if ax == '+x' else 0.25), y)
        else:
            for x in (fx0 - 0.15, fx0 + wd + 0.15):
                newel(R, x, fy0 + (-0.25 if ax == '+y' else 0.25))
        # mark the cells the flight runs through
        xs = sorted((fx0, fx0 + (L if ax == '+x' else -L if ax == '-x' else wd)))
        ys = sorted((fy0, fy0 + (L if ax == '+y' else -L if ax == '-y' else wd)))
        for cx in range(N):
            for cy in range(N):
                if xs[1] > cx * 8 + 0.8 and xs[0] < cx * 8 + 7.2 and ys[1] > cy * 8 + 0.8 and ys[0] < cy * 8 + 7.2:
                    used.add((cx, cy))
        # nav: foot to balcony
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if ax == '-x': foot = (fx0 + 0.8, c)
        elif ax == '+x': foot = (fx0 - 0.8, c)
        elif ax == '-y': foot = (c, fy0 + 0.8)
        else: foot = (c, fy0 - 0.8)
        a, b = R.navpt(foot[0], foot[1], 0.0), R.navpt(mx, my, z)
        R.link(a, b)
        NAV.setdefault('feet', []).append(a)


NAV = {}


def newel(R, x, y, h=1.25):
    R.parts.add(box(x - 0.12, y - 0.12, 0, x + 0.12, y + 0.12, h, 'walnut'))
    R.parts.add(cyl(x, y, h, h + 0.12, 0.08, 8, side='brass', top='brass'))
    R.light(sphere(x, y, h + 0.25, 0.1, 8, 4, 'e_amber'))


def secret_spiral(R, used):
    """One spiral that goes all the way up, to a railed reading platform in the fog under the lights."""
    ci, cj = SEC
    cx, cy = ci * 8 + 4.8, cj * 8 + 3.2
    r0, r1 = 0.28, 1.9
    zt = 12.9
    rpt = 4.3
    turns = zt / rpt
    a1 = math.pi / 2
    a0 = a1 - turns * 2 * math.pi
    helix_stair(R, cx, cy, r0, r1, 0.0, zt, a0, rise_per_turn=rpt, m='oak', side='walnut', bottom='walnut', newel='iron')
    # the platform: north-west of the axis, where the last step arrives
    px0, px1, py0, py1 = cx - 4.4, cx + 0.02, cy - 0.3, cy + 3.9
    R.parts.add(box(px0 - 0.45, py0 - 0.45, zt - 0.3, cx - r1 - 0.1, py1 + 0.45, zt, 'walnut', top='oak'))
    R.parts.add(box(cx - r1 - 0.1, cy - 0.02, zt - 0.3, px1, py1 + 0.45, zt, 'walnut', top='oak'))
    R.parts.add(box(cx - r1 - 0.1, py0 - 0.45, zt - 0.3, cx - r1 + 0.4, cy - 0.02, zt, 'walnut', top='oak'))
    R.parts.add(box(px1, cy + r1 + 0.1, zt - 0.3, px1 + 0.45, py1 + 0.45, zt, 'walnut', top='oak'))
    R.parts.add(box(cx - 0.02, cy + r0, zt - 0.3, cx + 0.3, cy + r1, zt, 'walnut', top='oak'))
    rails(R, [(px1 - 0.04, cy + r1), (px1 - 0.04, py1 - 0.04), (px0 + 0.04, py1 - 0.04), (px0 + 0.04, py0 + 0.04), (cx - r1 - 0.05, py0 + 0.04)], z=zt)
    rails(R, [(cx - r1 - 0.05, py0 + 0.04), (cx - r1 - 0.05, cy - 0.02)], z=zt)
    # hanging from the ceiling on rods
    for (x, y) in ((px0 + 0.2, py0 + 0.2), (px0 + 0.2, py1 - 0.2), (px1 - 0.4, py1 - 0.2)):
        R.nocol.add(cyl(x, y, zt, HT, 0.03, 6, side='iron', caps=False))
    # a desk, a chair, a lamp, a book open
    desk(R, px0 + 0.5, py1 - 1.3, px0 + 2.3, py1 - 0.5, z=zt, h=0.76)
    green_lamp(R, px0 + 1.9, py1 - 0.9, zt + 0.76, math.pi / 2)
    open_book_prop(R, px0 + 1.2, py1 - 0.9, zt + 0.76)
    seat(R, px0 + 1.3, py1 - 1.75, math.pi / 2, z=zt)
    book_pile(R, px0 + 0.5, py0 + 0.6, zt, n=6, seed=9)
    book_pile(R, px0 + 0.9, py0 + 0.5, zt, n=4, seed=10)
    R.light(sphere(px0 + 3.2, py0 + 0.6, zt + 1.9, 0.12, 10, 5, 'e_candle'))
    R.nocol.add(cyl(px0 + 3.2, py0 + 0.6, zt + 2.0, HT, 0.01, 4, side='iron', caps=False))
    R.spot('plaque', px0 + 0.3, (py0 + py1) / 2, zt + 1.2, 0.0)
    secret(R, px0 + 1.8, (py0 + py1) / 2, zt, 'The Platform in the Fog',
           'Only one of the staircases goes anywhere, and it comes here: a desk hung from the ceiling on rods, a lamp, a book left open. From up here the stairs below look like a forest in winter.', r=2.2)
    for k in (ci, ci - 1):
        for l in (cj, cj + 1):
            used.add((k, l))
    a = R.navpt(cx + r1 + 0.6, cy, 0.0)
    b = R.navpt(px0 + 2.6, py0 + 1.0, zt)
    R.link(a, b)
    NAV['sec'] = a


def dead_end(R, x, y, ang, rnd):
    """A straight flight on a solid stringer that climbs to a small railed landing and stops."""
    n = rnd.randint(9, 16); rise = 0.22; run = 0.28; wd = rnd.choice((1.2, 1.5, 1.8))
    L = n * run; H = n * rise
    g = stairs(0, 0, 0, wd, n, rise, run, '+x', m='oak', riser='walnut', side='walnut')
    land = box(L, 0, 0, L + 0.9, wd, H, 'walnut', top='oak')
    c, s = math.cos(ang), math.sin(ang)
    ox, oy = x - (c * (L + 0.9) / 2 - s * wd / 2), y - (s * (L + 0.9) / 2 + c * wd / 2)
    R.nocol.add(g.xform(ang, ox, oy, 0))
    R.parts.add(land.xform(ang, ox, oy, 0))
    P = lambda u, v: (ox + c * u - s * v, oy + s * u + c * v)
    # the ramp, and rails on both sides and across the end
    ramp(R, (*P(-0.02, wd / 2), 0.0), (*P(L, wd / 2), H), wd)
    for v in (0.05, wd - 0.05):
        a, b = P(0.0, v), P(L, v)
        stair_rail(R, a[0], a[1], rise * 0.5, b[0], b[1], H)
        rail(R, *P(L, v), *P(L + 0.86, v), H)
    rail(R, *P(L + 0.86, 0.05), *P(L + 0.86, wd - 0.05), H)
    # a newel post at the foot with a lamp on one of them
    for v in (-0.12, wd + 0.12):
        px, py = P(-0.1, v)
        R.parts.add(box(px - 0.1, py - 0.1, 0, px + 0.1, py + 0.1, 1.2, 'walnut'))
    if rnd.random() < 0.5:
        px, py = P(-0.1, -0.12)
        R.light(sphere(px, py, 1.4, 0.09, 8, 4, 'e_amber'))
    return P(-0.8, wd / 2)


def floating(R, x, y, rnd):
    """A flight in mid-air, going nowhere."""
    n = rnd.randint(8, 22); rise = 0.2; run = 0.28; wd = rnd.choice((1.2, 1.5))
    g = ribbon_stair(n, rise, run, wd, th=0.3)
    z0 = rnd.uniform(3.2, 9.0)
    ang = rnd.uniform(0, 2 * math.pi)
    L = n * run
    g.xform(0, -L / 2, -wd / 2, 0)
    tilt = rnd.uniform(-0.25, 0.25)
    rot(g, 'y', tilt)
    g.xform(ang, x, y, z0)
    R.nocol.add(g)
    # a banister on one side
    c, s = math.cos(ang), math.sin(ang)
    return g


def hanging(R, x, y, rnd):
    """A flight upside down, hanging from the ceiling."""
    n = rnd.randint(8, 18); rise = 0.2; run = 0.28; wd = rnd.choice((1.2, 1.5, 1.8))
    g = stairs(0, 0, 0, wd, n, rise, run, '+x', m='oak', riser='walnut', side='walnut')
    L = n * run
    g.xform(rnd.uniform(0, 2 * math.pi) if False else 0, -L / 2, -wd / 2, 0)
    g.xform(rnd.choice((0, math.pi / 2, math.pi, -math.pi / 2)) + rnd.uniform(-0.2, 0.2), x, y, 0)
    flip_z(g, HT / 2)
    R.nocol.add(g)
    # its banisters, upside down too
    return g


def spiral_pair(R, x, y, rnd, twin=True):
    """Spirals round one newel, starting above head height: they twist up into the fog."""
    z0 = rnd.uniform(2.4, 3.6); z1 = rnd.uniform(9.0, 13.5)
    r0, r1 = 0.22, rnd.uniform(1.2, 1.7)
    R.parts.add(cyl(x, y, 0, z1 + 0.6, r0, 10, side='iron', top='brass'))
    R.parts.add(cyl(x, y, 0, 0.15, 0.5, 12, side='iron', top='iron'))
    rpt = 3.6
    nst = int((z1 - z0) / 0.22)
    da = (z1 - z0) / rpt * 2 * math.pi / nst
    for b in range(2 if twin else 1):
        a0 = rnd.uniform(0, 2 * math.pi) + b * math.pi
        g = Geo()
        for k in range(nst):
            aa = a0 + k * da; zt = z0 + (k + 1) * (z1 - z0) / nst
            g.add(ring(x, y, zt - 0.06, zt, r0, r1, 1, top='oak', bottom='walnut', inner='walnut', outer='walnut', a0=aa, a1=aa + da * 1.15))
        # an outer handrail: a chain of bars
        rr = r1 - 0.05
        for k in range(0, nst, 2):
            aa = a0 + k * da; zt = z0 + (k + 1) * (z1 - z0) / nst
            ab = a0 + (k + 2) * da; zb = z0 + (k + 3) * (z1 - z0) / nst
            g.add(beam((x + rr * math.cos(aa), y + rr * math.sin(aa), zt + 0.9), (x + rr * math.cos(ab), y + rr * math.sin(ab), zb + 0.9), 0.04, 'brass'))
        R.nocol.add(g)


def tower(R, x, y, rnd):
    """A tower of bookcases, square, going up into the mist."""
    s = rnd.uniform(1.4, 2.0)
    h = rnd.choice((5.5, 7.5, 9.5, 12.0))
    R.parts.add(box(x - s, y - s, 0, x + s, y + s, h, 'walnut', top='walnut'))
    rows = int(min(h, 7.0) / 0.42) - 1
    for (face, bk, a, b) in (('+x', x + s, y - s + 0.1, y + s - 0.1), ('-x', x - s, y - s + 0.1, y + s - 0.1),
                             ('+y', y + s, x - s + 0.1, x + s - 0.1), ('-y', y - s, x - s + 0.1, x + s - 0.1)):
        sh(R, face, bk, a, b, rows=rows, frame='walnut', depth=0.3)
    R.parts.add(box(x - s - 0.15, y - s - 0.15, h, x + s + 0.15, y + s + 0.15, h + 0.3, 'walnut'))
    if h > 8:   # a flight that climbs out of its top and stops
        g = ribbon_stair(10, 0.2, 0.28, 1.2, th=0.3)
        g.xform(rnd.choice((0, math.pi / 2, math.pi)), x - 0.6, y - 0.6, h + 0.3)
        R.nocol.add(g)


def reading(R, x, y, rnd):
    ang = rnd.choice((0.0, math.pi / 2))
    g = table(-1.6, -0.6, 1.6, 0.6, 0.78, 'walnut', top='leather').xform(ang, x, y)
    R.parts.add(g)
    c, s = math.cos(ang), math.sin(ang)
    for u in (-0.8, 0.8):
        green_lamp(R, x + c * u, y + s * u, 0.78, ang)
        for v in (-1.05, 1.05):
            R.parts.add(chair(x + c * u - s * v, y + s * u + c * v, ang - math.pi / 2 * (1 if v > 0 else -1)))
    book_pile(R, x - s * 0.1, y + c * 0.1, 0.78, n=5, seed=int(x * 7 + y))


def forest(R, used):
    rnd = random.Random(9)
    kinds = []
    for i in range(N):
        for j in range(N):
            if (i, j) in used: continue
            x = i * 8 + 4 + rnd.uniform(-0.3, 0.3); y = j * 8 + 4 + rnd.uniform(-0.3, 0.3)
            edge = i in (0, N - 1) or j in (0, N - 1)
            if edge:   # keep clear of the walls' doorways
                x = min(max(x, 4.6), 64 - 4.6); y = min(max(y, 4.6), 64 - 4.6)
            r = rnd.random()
            if edge and r < 0.3: r = 0.3 + r * 1.5
            if r < 0.36: k = 'dead'
            elif r < 0.52: k = 'spiral'
            elif r < 0.66: k = 'tower'
            elif r < 0.8: k = 'read'
            else: k = 'empty'
            kinds.append((i, j, k))
            if k == 'dead':
                foot = dead_end(R, x, y, rnd.choice((0, math.pi / 2, math.pi, -math.pi / 2)), rnd)
            elif k == 'spiral':
                spiral_pair(R, x, y, rnd, twin=rnd.random() < 0.7)
            elif k == 'tower':
                tower(R, x, y, rnd)
            elif k == 'read':
                reading(R, x, y, rnd)
            # the air above is never empty
            near_sec = abs(i - SEC[0]) <= 1 and abs(j - SEC[1]) <= 1
            if k != 'spiral' and not near_sec and rnd.random() < 0.85:
                floating(R, i * 8 + 4, j * 8 + 4, rnd)
            if k in ('empty', 'read', 'dead') and not near_sec and rnd.random() < 0.5:
                floating(R, i * 8 + 4 + rnd.uniform(-2, 2), j * 8 + 4 + rnd.uniform(-2, 2), rnd)
            if not near_sec and k not in ('spiral',) and rnd.random() < 0.5:
                hanging(R, i * 8 + 4 + rnd.uniform(-1, 1), j * 8 + 4 + rnd.uniform(-1, 1), rnd)
    # the walkers wander the lanes
    lanes = {}
    for i in range(N + 1):
        for j in range(N + 1):
            if 0 < i < N and 0 < j < N:
                lanes[(i, j)] = R.navpt(i * 8.0, j * 8.0)
    for (i, j), a in lanes.items():
        if (i + 1, j) in lanes: R.link(a, lanes[(i + 1, j)])
        if (i, j + 1) in lanes: R.link(a, lanes[(i, j + 1)])
    for a in NAV.get('feet', []):
        p = R.nav[a]; best = min(lanes.values(), key=lambda b: math.hypot(R.nav[b][0] - p[0], R.nav[b][1] - p[1]))
        R.link(a, best)
    p = R.nav[NAV['sec']]
    best = min(lanes.values(), key=lambda b: math.hypot(R.nav[b][0] - p[0], R.nav[b][1] - p[1]))
    R.link(NAV['sec'], best)


def walls(R, W, D):
    rows = 17
    for k in range(4):
        a, b = k * C + 0.8, k * C + C / 2 - 2.0
        c, d = k * C + C / 2 + 2.0, (k + 1) * C - 0.8
        for (p, q) in ((a, b), (c, d)):
            sh(R, '+y', T, p, q, rows=rows, frame='walnut')
            sh(R, '-y', D - T, p, q, rows=rows, frame='walnut')
            sh(R, '+x', T, p, q, rows=rows, frame='walnut')
            sh(R, '-x', W - T, p, q, rows=rows, frame='walnut')


def lights(R, W, D):
    """A ceiling of lay-lights, bright through the mist."""
    for i in range(N):
        for j in range(N):
            x, y = i * 8 + 4, j * 8 + 4
            if (i, j) in ((SEC[0], SEC[1]), (SEC[0] - 1, SEC[1])):
                continue
            R.cut(box(x - 2.6, y - 2.6, HT - 0.05, x + 2.6, y + 2.6, HT + 0.2, 'plaster'))
            R.light(box(x - 2.2, y - 2.2, HT + 0.14, x + 2.2, y + 2.2, HT + 0.16, 'e_panel', skip=('+z',)))
    for (x, y) in ((1.0, 16.0), (W - 1.0, 48.0), (16.0, D - 1.0), (48.0, 1.0)):
        R.light(sphere(x, y, 2.4, 0.12, 10, 5, 'e_amber'))
