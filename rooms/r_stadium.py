"""The Stadium: a football ground at night, empty, every floodlight on. Stands of green seats rise on
all four sides from the pitch to the rim, and on every seat is a book, as if for a crowd that has not
arrived. Under the stands a concourse runs round the whole ground; tunnels come up through the lower
rows onto the pitch. The players' tunnel on the south side, under its folded canopy, ends at a shutter
stuck halfway down; under it is the home dressing room, where the lockers are full of books."""
from kit_h9 import *

W, D = 64.0, 64.0
IX0, IX1, IY0, IY1 = 15.5, 48.5, 18.0, 46.0      # the bowl's inner edge (pitch and track)
PX0, PX1, PY0, PY1 = 17.0, 47.0, 19.5, 44.5      # the pitch
NR = 12                                           # rows of seats
Z0, RISE = 1.2, 0.6                               # row 0's floor, and the rise per 1 m row
RIM = 8.0
CH = 3.8                                          # the concourse ceiling
SC = 6.0                                          # the concourse reaches under the stands to s = 6
TW = 4.0                                          # tunnel width
TRENCH = 5                                        # rows cut by a tunnel (z_k < CH)
SKYZ = 15.5
AISLES = {'S': (23.0, 41.0), 'N': (23.0, 41.0), 'W': (25.0, 39.0), 'E': (25.0, 39.0)}
TUNNELS = {'S': 32.0, 'N': 32.0, 'W': 32.0, 'E': 32.0}   # S is the players' tunnel
LX0, LX1, LY0, LY1 = 26.0, 38.0, 6.4, 13.0        # the dressing room


def zk(k): return Z0 + RISE * k


def pt(side, s, t):
    """A point s metres out from the bowl's inner edge on `side`, t along it."""
    if side == 'S': return (t, IY0 - s)
    if side == 'N': return (t, IY1 + s)
    if side == 'W': return (IX0 - s, t)
    return (IX1 + s, t)


def sbox(side, s0, s1, t0, t1, z0, z1, m, **kw):
    a = pt(side, s0, t0); b = pt(side, s1, t1)
    return box(min(a[0], b[0]), min(a[1], b[1]), z0, max(a[0], b[0]), max(a[1], b[1]), z1, m, **kw)


def trange(side, k):
    if side in 'SN': return (IX0 - (k + 1), IX1 + (k + 1))
    return (IY0 - k - 0.5, IY1 + k + 0.5)


def skips(side, k):
    out = [(a - 0.6, a + 0.6) for a in AISLES[side]]
    if k < TRENCH: out.append((TUNNELS[side] - TW / 2 - 0.1, TUNNELS[side] + TW / 2 + 0.1))
    return out


def spans(a, b, cut):
    segs = [(a, b)]
    for (c0, c1) in cut:
        nxt = []
        for (s0, s1) in segs:
            if c1 <= s0 or c0 >= s1: nxt.append((s0, s1)); continue
            if c0 > s0: nxt.append((s0, c0))
            if c1 < s1: nxt.append((c1, s1))
        segs = nxt
    return [s for s in segs if s[1] - s[0] > 0.3]


def make():
    R = Room('stadium', 4, 4, levels=2, res=2048)
    R.sockets(floor='concrete', wall='concrete')
    bowl(R)
    seats(R)
    rails_(R)
    concourse(R)
    tunnels(R)
    dressing_room(R)
    pitch(R)
    rim(R)
    floodlights(R)
    sky(R)
    fx(R, 'dust', [PX0, PY0, 0.5, PX1, PY1, 9.0])
    fx(R, 'fog', [T, T, 0.0, W - T, D - T, SKYZ], density=0.012)
    # walkers: the concourse ring, the pitch, the rim
    navloop(R, [(5.0, 5.0), (32.0, 5.0), (59.0, 5.0), (59.0, 32.0), (59.0, 59.0), (32.0, 59.0), (5.0, 59.0), (5.0, 32.0)])
    p = navloop(R, [(20.0, 22.0), (32.0, 21.0), (44.0, 22.0), (44.0, 42.0), (32.0, 43.0), (20.0, 42.0)])
    w0, w1, w2 = R.navpt(8.0, 32.0), R.navpt(15.9, 32.0), R.navpt(16.2, 28.6)
    R.link(7, w0, w1, w2, p[0])
    r = navloop(R, [(2.5, 4.0), (32.0, 4.0), (61.5, 4.0), (61.5, 32.0), (61.5, 60.0), (32.0, 60.0), (2.5, 60.0), (2.5, 32.0)], z=RIM)
    secret(R, 32.0, 9.8, 0.0, 'The Home Dressing Room',
           'Under the shutter: the home dressing room, the kit hung on its pegs, the tactics on the board. Every locker is full of books, and on the bench is a note that says only: next match, see fixture list, and the fixture list is a book.')
    return finish(R, 'The Stadium', weight=2, probe=(32, 32, 6.0), top=SKYZ,
                  blurb='A football ground at night, every floodlight on, every seat empty. There is a book on each seat. You find yourself looking for yours.')


# ---------------------------------------------------------------------------
def bowl(R):
    R.cut(box(T - 0.02, T - 0.02, RIM, W - T + 0.02, D - T + 0.02, SKYZ, 'concrete', bottom='concrete', top='black'))
    R.cut(box(IX0, IY0, 0.0, IX1, IY1, RIM + 0.1, 'concrete', bottom='slate'))
    for k in range(NR):
        R.cut(box(IX0 - (k + 1), IY0 - (k + 1), zk(k), IX1 + (k + 1), IY1 + (k + 1), RIM + 0.1, 'concrete', bottom='concrete'))


def seats(R):
    """Per row: a continuous seat pan (collided) and back (drawn), seat dividers, a book on each seat;
    in the aisles, a half step instead."""
    rnd = random.Random(83)
    pans = Geo(); backs = Geo(); bits = Geo(); steps = Geo()
    for side in 'SNWE':
        for k in range(NR):
            z = zk(k)
            a, b = trange(side, k)
            for (t0, t1) in spans(a, b, skips(side, k)):
                pans.add(sbox(side, k + 0.5, k + 0.95, t0, t1, z, z + 0.45, 'seat', top='seat'))
                backs.add(sbox(side, k + 0.9, k + 0.98, t0, t1, z + 0.45, z + 0.98, 'seat'))
                n = int((t1 - t0) / 0.55)
                for i in range(n):
                    t = t0 + (t1 - t0) * (i + 0.5) / n
                    # a divider (an armrest) between seats, a book on the seat
                    ta = t0 + (t1 - t0) * i / n
                    if i: bits.add(sbox(side, k + 0.55, k + 0.9, ta - 0.02, ta + 0.02, z + 0.45, z + 0.62, 'iron', skip=('-z',)))
                    bw = rnd.uniform(0.14, 0.2) / 2; bl = rnd.uniform(0.2, 0.26) / 2; ds = rnd.uniform(-0.04, 0.04); dt = rnd.uniform(-0.05, 0.05)
                    bits.add(sbox(side, k + 0.72 - bl + ds, k + 0.72 + bl + ds, t - bw + dt, t + bw + dt, z + 0.45, z + 0.45 + rnd.uniform(0.03, 0.06),
                                  rnd.choice(BOOKM), skip=('-z',)))
            for a_ in AISLES[side]:
                if k < NR - 1:
                    steps.add(sbox(side, k + 0.45, k + 1.0, a_ - 0.6, a_ + 0.6, z, z + 0.3, 'concrete', skip=('-z',)))
    R.parts.add(pans); R.nocol.add(backs); R.nocol.add(bits); R.parts.add(steps)
    # the aisle lamps, low on the step ends: they stay on
    for side in 'SNWE':
        for a_ in AISLES[side]:
            for k in range(1, NR, 3):
                x, y = pt(side, k + 0.47, a_ - 0.62)
                R.light(box(x - 0.05, y - 0.05, zk(k) + 0.08, x + 0.05, y + 0.05, zk(k) + 0.16, 'e_amber'))


def rails_(R):
    # the front of row 0, above the track, open where the flights arrive and the tunnels come through
    opens = {'S': [], 'N': [], 'W': [], 'E': []}
    for side in 'SNWE':
        for a_ in AISLES[side]: opens[side].append((a_ - 0.6, a_ + 0.6))
        opens[side].append((TUNNELS[side] - TW / 2 - 0.1, TUNNELS[side] + TW / 2 + 0.1))
    for side in 'SNWE':
        a, b = (IX0, IX1) if side in 'SN' else (IY0, IY1)
        for (t0, t1) in spans(a - 0.9, b + 0.9, opens[side]):
            p0, p1 = pt(side, 0.08, t0), pt(side, 0.08, t1)
            rail_line(R, p0[0], p0[1], zk(0), p1[0], p1[1], zk(0), m='brass', post='iron', spacing=1.2, mid=True)
    # the flights from the track up to row 0, at each aisle
    for side in 'SNWE':
        for a_ in AISLES[side]:
            flight_up(R, side, a_)
    # the tunnels' trenches: rails down both sides, stepping with the rows, and across the mouth above
    for side in 'SNWE':
        c = TUNNELS[side]
        for t in (c - TW / 2 - 0.08, c + TW / 2 + 0.08):
            for k in range(TRENCH):
                p0, p1 = pt(side, k + 0.02, t), pt(side, k + 0.98, t)
                rail_line(R, p0[0], p0[1], zk(k), p1[0], p1[1], zk(k), m='brass', post='iron', spacing=1.0, mid=True)
                R.col.add(sbox(side, k, k + 1, t - 0.04, t + 0.04, zk(k), zk(k) + 1.15, 'tile'))
        p0, p1 = pt(side, TRENCH + 0.08, c - TW / 2 - 0.1), pt(side, TRENCH + 0.08, c + TW / 2 + 0.1)
        rail_line(R, p0[0], p0[1], zk(TRENCH), p1[0], p1[1], zk(TRENCH), m='brass', post='iron', spacing=1.0, mid=True)


def flight_up(R, side, a_):
    """Six steps up the track beside the pitch wall to a landing at row 0's level, in the aisle's mouth."""
    n, rise, run = 6, zk(0) / 6, 0.3
    L = n * run
    t_top = a_ - 0.6
    s0, s1 = -1.5, 0.0                         # across the track, against the wall
    if side in 'SN':
        yy = sorted((pt(side, s0, 0)[1], pt(side, s1, 0)[1]))
        R.flight(t_top - L, yy[0], 0.0, 1.5, n, rise, run, '+x', m='concrete', side='concrete')
    else:
        xx = sorted((pt(side, s0, 0)[0], pt(side, s1, 0)[0]))
        R.flight(xx[0], t_top - L, 0.0, 1.5, n, rise, run, '+y', m='concrete', side='concrete')
    R.parts.add(sbox(side, s0, 0.0, t_top, a_ + 0.6, 0.0, zk(0), 'concrete'))
    # rails: the pitch side of the flight and the landing, and the landing's far end
    p0, p1 = pt(side, s0 + 0.06, t_top - L + 0.3), pt(side, s0 + 0.06, t_top)
    rail_line(R, p0[0], p0[1], rise * 1.5, p1[0], p1[1], zk(0), m='brass', post='iron', spacing=1.0, mid=True)
    p0, p1 = pt(side, s0 + 0.06, t_top), pt(side, s0 + 0.06, a_ + 0.54)
    rail_line(R, p0[0], p0[1], zk(0), p1[0], p1[1], zk(0), m='brass', post='iron', spacing=1.0, mid=True)
    p0, p1 = pt(side, s0 + 0.06, a_ + 0.54), pt(side, 0.08, a_ + 0.54)
    rail_line(R, p0[0], p0[1], zk(0), p1[0], p1[1], zk(0), m='brass', post='iron', spacing=1.0, mid=True)


# ---------------------------------------------------------------------------
def concourse(R):
    xw, xe, ys, yn = IX0 - SC, IX1 + SC, IY0 - SC, IY1 + SC     # its inner walls
    R.cut(box(T - 0.02, T - 0.02, 0, xw, D - T + 0.02, CH, 'concrete', bottom='terrazzo', top='plaster'))
    R.cut(box(xe, T - 0.02, 0, W - T + 0.02, D - T + 0.02, CH, 'concrete', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, yn, 0, W - T + 0.02, D - T + 0.02, CH, 'concrete', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, T - 0.02, 0, LX0 - 0.4, ys, CH, 'concrete', bottom='terrazzo', top='plaster'))
    R.cut(box(LX1 + 0.4, T - 0.02, 0, W - T + 0.02, ys, CH, 'concrete', bottom='terrazzo', top='plaster'))
    R.cut(box(LX0 - 0.6, T - 0.02, 0, LX1 + 0.6, LY0 - 0.4, CH, 'concrete', bottom='terrazzo', top='plaster'))
    # books all round the outer walls, broken at the doorways; more on the inner walls
    for (a, b) in [(k * C + 0.8, k * C + C / 2 - 2.0) for k in range(4)] + [(k * C + C / 2 + 2.0, (k + 1) * C - 0.8) for k in range(4)]:
        sh(R, '+y', T, a, b, rows=8, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=8, frame='walnut')
        sh(R, '+x', T, a, b, rows=8, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=8, frame='walnut')
    for (a, b) in ((ys + 1.0, 29.0), (35.0, yn - 1.0)):
        sh(R, '-x', xw, a, b, rows=8, frame='oak')
        sh(R, '+x', xe, a, b, rows=8, frame='oak')
    for (a, b) in ((xw + 1.0, 29.0), (35.0, xe - 1.0)):
        sh(R, '+y', yn, a, b, rows=8, frame='oak')
    for (a, b) in ((xw + 1.0, LX0 - 0.6), (LX1 + 0.6, xe - 1.0)):
        sh(R, '-y', ys, a, b, rows=8, frame='oak')
    sh(R, '-y', LY0 - 0.4, LX0 + 0.4, LX1 - 0.4, rows=8, frame='oak')
    # lights down the middle of the ring, green signs over the tunnels
    for k in range(15):
        t = 3.5 + k * 4.0
        for (x, y) in ((t, (T + ys) / 2 if not (LX0 < t < LX1) else (T + LY0 - 0.4) / 2), (t, (yn + D - T) / 2), ((T + xw) / 2, t), ((xe + W - T) / 2, t)):
            R.light(box(x - 0.5, y - 0.5, CH - 0.03, x + 0.5, y + 0.5, CH - 0.01, 'e_fluor'))
    for (x, y, ax) in ((xw, 32.0, 'x'), (xe, 32.0, 'x'), (32.0, yn, 'y')):
        if ax == 'x':
            R.parts.add(box(x - 0.1, 30.4, 3.0, x + 0.1, 33.6, 3.4, 'black'))
            R.light(box(x - 0.12, 30.6, 3.07, x + 0.12, 33.4, 3.33, 'e_exit'))
        else:
            R.parts.add(box(30.4, y - 0.1, 3.0, 33.6, y + 0.1, 3.4, 'black'))
            R.light(box(30.6, y - 0.12, 3.07, 33.4, y + 0.12, 3.33, 'e_exit'))
    # turnstiles in the corners, benches
    for (x, y) in ((4.0, 4.0), (60.0, 4.0), (4.0, 60.0), (60.0, 60.0)):
        R.parts.add(box(x - 0.9, y - 0.3, 0, x + 0.9, y + 0.3, 1.0, 'iron', top='chrome'))


def tunnels(R):
    for side in 'WEN':
        c = TUNNELS[side]
        R.cut(sbox(side, -0.3, SC + 0.3, c - TW / 2, c + TW / 2, 0.0, CH, 'concrete', bottom='slate', top='plaster'))
    # the players' tunnel: its trench from the pitch to the dressing room, under a folded canopy
    c = TUNNELS['S']
    R.cut(box(c - TW / 2, LY1 - 0.1, 0.0, c + TW / 2, IY0 + 0.3, CH, 'concrete', bottom='slate', top='plaster'))
    r, zc = 1.9, 2.3
    L = IY0 + 1.6 - LY1
    for k in range(7):
        y0 = LY1 + k * L / 7; y1 = y0 + L / 7 - 0.03
        g = shell_cyl(0, 0, 0, y1 - y0, r + 0.06 * (k % 2), 16, 'ivory', inner='slate', t=0.04, a0=0.0, a1=math.pi)
        rot(g, 'x', math.pi / 2)
        g.xform(0, c, y1, zc)
        R.nocol.add(g)
        g = ring(0, 0, 0, 0.1, r - 0.06, r + 0.1, 16, top='iron', bottom='iron', inner='iron', outer='iron', a0=0.0, a1=math.pi)
        rot(g, 'x', math.pi / 2); g.xform(0, c, y1, zc)
        R.nocol.add(g)
    for x in (c - r - 0.05, c + r + 0.05):
        R.parts.add(box(x - 0.05, IY0 + 0.6, 0.0, x + 0.05, IY0 + 1.6, zc, 'iron'))
    # the shutter, stuck halfway down
    R.parts.add(box(c - TW / 2, LY1 - 0.06, 1.25, c + TW / 2, LY1 + 0.04, CH, 'iron'))
    for k in range(12):
        z = 1.3 + k * 0.2
        R.nocol.add(box(c - TW / 2, LY1 + 0.04, z, c + TW / 2, LY1 + 0.06, z + 0.03, 'chrome'))
    R.nocol.add(box(c - TW / 2, LY1 + 0.04, 1.2, c + TW / 2, LY1 + 0.1, 1.3, 'iron'))


def dressing_room(R):
    R.cut(box(LX0, LY0, 0.0, LX1, LY1, 3.6, 'wtile', bottom='terrazzo', top='plaster'))
    # lockers round the walls, every one full of books; pegs of kit above the bench
    for (a, b) in ((LX0 + 0.3, 30.6), (33.4, LX1 - 0.3)):
        for k in range(int((b - a) / 1.0)):
            x = a + k * 1.0
            shelf(R, x + 0.95, LY1, 0.0, 0.9, '-y', rows=5, frame='green', depth=0.4)
    for k in range(5):
        y = LY0 + 0.3 + k * 1.2
        shelf(R, LX0, y + 1.1, 0.0, 1.1, '+x', rows=5, frame='green', depth=0.4)
    rnd = random.Random(9)
    for k in range(9):
        y = LY0 + 0.4 + k * 0.7
        R.nocol.add(box(LX1 - 0.12, y - 0.02, 1.8, LX1, y + 0.02, 1.84, 'brass'))
        R.nocol.add(box(LX1 - 0.2, y - 0.25, 1.0, LX1 - 0.12, y + 0.25, 1.8, rnd.choice(('oxblood', 'ivory'))))
    R.parts.add(box(LX1 - 0.7, LY0 + 0.2, 0.0, LX1 - 0.25, LY1 - 0.3, 0.45, 'oak'))
    for k in range(4): R.spot('sit', LX1 - 0.48, LY0 + 1.0 + k * 1.4, 0.45, math.pi)
    # the tactics board, a massage table, a kit basket, the note on the bench
    R.parts.add(box(28.0, LY0 + 0.02, 0.9, 31.0, LY0 + 0.1, 2.5, 'blackboard'))
    for (x, z) in ((28.6, 1.9), (29.3, 1.4), (30.2, 2.0), (29.8, 1.2)):
        R.nocol.add(box(x - 0.06, LY0 + 0.1, z - 0.06, x + 0.06, LY0 + 0.11, z + 0.06, 'ivory'))
    R.nocol.add(beam((28.6, LY0 + 0.11, 1.9), (29.8, LY0 + 0.11, 1.2), 0.02, 'ivory'))
    R.parts.add(table(31.4, 8.6, 33.4, 9.4, 0.8, 'iron', top='leather'))
    R.parts.add(box(34.0, 7.0, 0.0, 34.9, 7.7, 0.7, 'oak'))
    for k in range(6):
        R.nocol.add(box(34.05 + (k % 3) * 0.28, 7.05 + (k // 3) * 0.3, 0.7, 34.3 + (k % 3) * 0.28, 7.3 + (k // 3) * 0.3, 0.76, ('ivory', 'oxblood')[k % 2]))
    g = box(-0.12, -0.08, 0, 0.12, 0.08, 0.01, 'ivory')
    R.nocol.add(g.xform(0.3, LX1 - 0.45, 9.8, 0.45))
    book_pile(R, LX1 - 0.45, 10.4, 0.45, 5, rnd, 0.6)
    for (x, y) in ((29.0, 9.7), (35.0, 9.7), (32.0, 7.6)):
        R.light(box(x - 0.6, y - 0.3, 3.56, x + 0.6, y + 0.3, 3.59, 'e_panel'))
    R.light(box(31.9, LY1 - 0.4, 3.0, 32.1, LY1 - 0.2, 3.1, 'e_amber'))


# ---------------------------------------------------------------------------
def pitch(R):
    R.nocol.add(box(PX0, PY0, 0.0, PX1, PY1, 0.02, 'turf'))
    n = 10
    for k in range(0, n, 2):
        x0 = PX0 + (PX1 - PX0) * k / n; x1 = PX0 + (PX1 - PX0) * (k + 1) / n
        R.nocol.add(box(x0, PY0, 0.02, x1, PY1, 0.024, 'turf2'))
    L = lambda x0, y0, x1, y1: R.nocol.add(box(x0, y0, 0.024, x1, y1, 0.03, 'ivory'))
    w = 0.08; m = 0.6
    a0, a1, b0, b1 = PX0 + m, PX1 - m, PY0 + m, PY1 - m
    L(a0, b0, a1, b0 + w); L(a0, b1 - w, a1, b1); L(a0, b0, a0 + w, b1); L(a1 - w, b0, a1, b1)
    cx, cy = (PX0 + PX1) / 2, (PY0 + PY1) / 2
    L(cx - w / 2, b0, cx + w / 2, b1)
    R.nocol.add(ring(cx, cy, 0.024, 0.03, 3.6, 3.6 + w, 40, top='ivory', bottom='ivory', inner='ivory', outer='ivory'))
    R.nocol.add(cyl(cx, cy, 0.024, 0.031, 0.18, 10, side='ivory', top='ivory', bottom='ivory'))
    for (x, s) in ((a0, 1), (a1, -1)):
        bw, bd = 12.0, 5.0
        xa, xb = sorted((x, x + s * bd))
        L(xa, cy - bw / 2, xb, cy - bw / 2 + w); L(xa, cy + bw / 2 - w, xb, cy + bw / 2)
        L(x + s * bd - (w if s > 0 else 0), cy - bw / 2, x + s * bd + (0 if s > 0 else w), cy + bw / 2)
        sw = 5.0
        xa, xb = sorted((x, x + s * 1.8))
        L(xa, cy - sw / 2, xb, cy - sw / 2 + w); L(xa, cy + sw / 2 - w, xb, cy + sw / 2)
        L(x + s * 1.8 - (w if s > 0 else 0), cy - sw / 2, x + s * 1.8 + (0 if s > 0 else w), cy + sw / 2)
        R.nocol.add(cyl(x + s * 3.6, cy, 0.024, 0.031, 0.12, 8, side='ivory', top='ivory', bottom='ivory'))
        # the goal: posts, bar, and a net of thin cords
        gw, gh, gd = 5.2, 2.0, 1.0
        for y in (cy - gw / 2, cy + gw / 2):
            R.parts.add(cyl(x, y, 0.0, gh, 0.06, 8, side='ivory', top='ivory', bottom='ivory'))
        R.parts.add(box(x - 0.06, cy - gw / 2, gh - 0.06, x + 0.06, cy + gw / 2, gh + 0.06, 'ivory'))
        xb_ = x - s * gd
        for k in range(9):
            y = cy - gw / 2 + gw * k / 8
            R.nocol.add(beam((x, y, gh), (xb_, y, 0.02), 0.012, 'ivory'))
        for k in range(1, 5):
            t = k / 5
            R.nocol.add(beam((x - s * gd * t, cy - gw / 2, gh * (1 - t)), (x - s * gd * t, cy + gw / 2, gh * (1 - t)), 0.012, 'ivory'))
        R.col.add(box(min(x, xb_), cy - gw / 2, 0.0, max(x, xb_), cy + gw / 2, gh, 'tile'))
    # corner flags
    for (x, y) in ((a0, b0), (a1, b0), (a0, b1), (a1, b1)):
        R.nocol.add(cyl(x, y, 0.0, 1.5, 0.02, 6, side='ivory', caps=False))
        R.nocol.add(box(x, y - 0.005, 1.15, x + 0.35, y + 0.005, 1.45, 'hutred'))
    # a ball on the centre spot
    R.parts.add(sphere(cx, cy, 0.14, 0.11, 10, 6, 'ivory'))
    R.nocol.add(box(IX0, IY0, 0.0, IX1, PY0, 0.01, 'earth')); R.nocol.add(box(IX0, PY1, 0.0, IX1, IY1, 0.01, 'earth'))
    R.nocol.add(box(IX0, PY0, 0.0, PX0, PY1, 0.01, 'earth')); R.nocol.add(box(PX1, PY0, 0.0, IX1, PY1, 0.01, 'earth'))
    # dugouts on the south side of the pitch
    for x in (24.5, 39.5):
        R.parts.add(box(x - 2.0, PY0 - 0.02, 0.0, x + 2.0, PY0 + 0.1, 1.6, 'green'))
        R.parts.add(box(x - 2.0, PY0 + 0.1, 1.5, x + 2.0, PY0 + 1.0, 1.6, 'green'))
        for s in (-1, 1): R.parts.add(box(x + s * 2.0 - 0.05, PY0 + 0.1, 0.0, x + s * 2.0 + 0.05, PY0 + 1.0, 1.5, 'green'))
        R.parts.add(box(x - 1.8, PY0 + 0.12, 0.0, x + 1.8, PY0 + 0.5, 0.45, 'seat'))
        for k in range(6): R.spot('sit', x - 1.5 + k * 0.6, PY0 + 0.32, 0.45, math.pi / 2)


def rim(R):
    # the top walkway: bookcases round the walls, a rail at its inner edge is not needed (row 11 is a step below)
    for (a, b) in [(k * C + 0.8, k * C + C / 2 - 2.0) for k in range(4)] + [(k * C + C / 2 + 2.0, (k + 1) * C - 0.8) for k in range(4)]:
        if a < 3.0 or b > W - 3.0:
            a, b = max(a, 3.2), min(b, W - 3.2)
        for (fn, bk) in (('+y', T), ('-y', D - T), ('+x', T), ('-x', W - T)):
            if fn == '+x' and 22.0 < a < 42.0: continue   # the scoreboard wall
            sh(R, fn, bk, a, b, z=RIM, rows=12, frame='walnut')
    for c in (8.0, 24.0, 40.0, 56.0):
        for (fn, bk) in (('+y', T), ('-y', D - T), ('+x', T), ('-x', W - T)):
            if fn == '+x' and c in (24.0, 40.0): continue
            sh(R, fn, bk, c - 2.0, c + 2.0, z=RIM + 4.3, rows=5, frame='walnut')
    # the scoreboard on the west wall
    R.parts.add(box(T, 22.5, RIM + 2.0, T + 0.3, 41.5, RIM + 6.8, 'black'))
    R.nocol.add(box(T + 0.3, 22.4, RIM + 6.7, T + 0.36, 41.6, RIM + 6.9, 'gilt'))
    R.nocol.add(box(T + 0.3, 22.4, RIM + 1.9, T + 0.36, 41.6, RIM + 2.1, 'gilt'))
    rnd = random.Random(12)
    g = Geo()
    for (y0, y1, z0, z1) in ((23.5, 30.5, RIM + 5.0, RIM + 6.2), (33.5, 40.5, RIM + 5.0, RIM + 6.2)):
        x = T + 0.31
        yy = y0
        while yy < y1 - 0.3:
            g.add(box(x, yy, z0, x + 0.01, yy + 0.24, z1, 'e_board')); yy += 0.36
    for (yc, zc) in ((27.0, RIM + 3.4), (37.0, RIM + 3.4)):   # nought, nought
        g.add(box(T + 0.31, yc - 0.9, zc - 1.1, T + 0.32, yc - 0.6, zc + 1.1, 'e_board'))
        g.add(box(T + 0.31, yc + 0.6, zc - 1.1, T + 0.32, yc + 0.9, zc + 1.1, 'e_board'))
        g.add(box(T + 0.31, yc - 0.6, zc + 0.8, T + 0.32, yc + 0.6, zc + 1.1, 'e_board'))
        g.add(box(T + 0.31, yc - 0.6, zc - 1.1, T + 0.32, yc + 0.6, zc - 0.8, 'e_board'))
    R.light(g)


def tower(R, x, y, h, face_to, bank_w=4.0, bank_h=2.4, lamps=(5, 3), mast=True):
    """A floodlight: a lattice mast from the rim, a bank of lamps aimed at the pitch."""
    z0 = RIM
    s = 0.7
    if mast:
        legs = [(x - s, y - s), (x + s, y - s), (x + s, y + s), (x - s, y + s)]
        for (lx, ly) in legs:
            R.nocol.add(box(lx - 0.07, ly - 0.07, z0, lx + 0.07, ly + 0.07, h, 'iron'))
        for k in range(int((h - z0) / 1.4)):
            za, zb = z0 + k * 1.4, z0 + (k + 1) * 1.4
            for i in range(4):
                p, q = legs[i], legs[(i + 1) % 4]
                R.nocol.add(beam((p[0], p[1], za), (q[0], q[1], zb), 0.04, 'iron'))
        R.col.add(box(x - s - 0.1, y - s - 0.1, z0, x + s + 0.1, y + s + 0.1, h, 'tile'))
    # the bank, tilted down toward the pitch
    ang = math.atan2(face_to[1] - y, face_to[0] - x)
    tilt = math.atan2(h - 1.0, math.hypot(face_to[0] - x, face_to[1] - y))
    g = box(-0.15, -bank_w / 2, -bank_h / 2, 0.0, bank_w / 2, bank_h / 2, 'iron')
    lg = Geo()
    nx, nz = lamps
    for i in range(nx):
        for j in range(nz):
            yy = -bank_w / 2 + bank_w * (i + 0.5) / nx; zz = -bank_h / 2 + bank_h * (j + 0.5) / nz
            e = bank_w / nx * 0.36
            g.add(box(0.0, yy - e - 0.04, zz - e - 0.04, 0.08, yy + e + 0.04, zz + e + 0.04, 'chrome'))
            lg.add(box(0.08, yy - e, zz - e, 0.1, yy + e, zz + e, 'e_flood'))
    for gg in (g, lg):
        rot(gg, 'y', tilt)
        gg.xform(ang, x, y, h + 0.6)
    R.nocol.add(g); R.light(lg)


def floodlights(R):
    ctr = (32.0, 32.0)
    for (x, y) in ((1.6, 1.6), (W - 1.6, 1.6), (1.6, D - 1.6), (W - 1.6, D - 1.6)):
        tower(R, x, y, 13.0, ctr, bank_w=4.4, bank_h=2.6, lamps=(6, 3))
    for x in (20.0, 44.0):
        for y in (2.2, D - 2.2):
            tower(R, x, y, 13.6, (x, 32.0), bank_w=3.6, bank_h=1.4, lamps=(5, 2))
    # lamps under the rim's edge, lighting the upper rows
    for side in 'SNWE':
        a, b = trange(side, NR - 1)
        for k in range(8):
            t = a + (b - a) * (k + 0.5) / 8
            x, y = pt(side, NR + 0.3, t)
            R.light(box(x - 0.15, y - 0.15, RIM + 0.02, x + 0.15, y + 0.15, RIM + 0.08, 'e_amber'))


def sky(R):
    """A black night sky over the ground, a few stars."""
    rnd = random.Random(31)
    g = Geo()
    for k in range(160):
        x, y = rnd.uniform(3, W - 3), rnd.uniform(3, D - 3)
        e = rnd.uniform(0.03, 0.07)
        g.add(box(x - e, y - e, SKYZ - 0.03, x + e, y + e, SKYZ - 0.01, 'e_dim'))
    R.light(g)
