"""The Reading Lamp: a green banker's lamp as tall as a nave stands on a colossal table and lights one
enormous page. A stair of dictionaries climbs to the table top; steps cut into the lamp's brass foot, and a
stair winding up its stem, climb to where the arm meets the shade. Through a hatch there, you are inside
the shade: a long warm room of green glass, hung with its pull chains."""
from kit_h1 import *

W = D = 64.0
TX0, TY0, TX1, TY1, TZ = 14.0, 10.0, 50.0, 36.0, 4.0     # the table top
SX, SY = 32.0, 30.5                                        # the lamp's stem
SR = 1.3
HR1 = 2.9                                                  # the stem stair's outer radius
PZ = 6.0                                                   # the top of the foot
AZ = 12.5                                                  # the arm, and the floor inside the shade
AY, AZX = 24.3, 12.4                                       # the shade's axis (along x): y, z
SHO, SHT = 2.8, 0.2                                        # its radius, its glass
SX0, SX1 = 24.0, 40.0                                      # its length
HX0, HX1 = 31.6, 33.4                                      # the hatch in its back
BX0, BX1, BY0 = 11.4, 14.0, 14.0                           # the stair of dictionaries


def make():
    R = Room('titanlamp', 4, 4, levels=2, res=2048)
    R.sockets(floor='floor', wall='tile')
    top = R.hi - 0.2
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, top, 'tile', bottom='floor', top='plaster'))
    rnd = random.Random(1717)
    g1 = wall_flight(R, 'W', 26.0, wd=2.0, rise=0.22, run=0.28, up=+1)
    g2 = wall_flight(R, 'E', 38.0, wd=2.0, rise=0.22, run=0.28, up=-1)
    gallery(R, gaps=[g1, g2])
    gallery_cases(R, rows=13)
    gallery_lamps(R, night=2)
    lower_cases(R, rows=15)
    vault(R, top)
    table_(R, rnd)
    book_stair(R, rnd)
    foot(R)
    stem(R)
    shade(R, rnd)
    nav(R)
    R.spot('probe', 20.0, 20.0, 7.0)
    R.meta.update(label='The Reading Lamp', weight=2,
                  blurb='Someone left the lamp on. It is the only light for a long way, and it falls on a single page the size of a field. You cannot read it from down here.')
    R.meta['box'] = [[T, 0, T], [W - T, top, D - T]]
    fx(R, 'dust', [SX0, AY - 5.0, TZ + 0.3, SX1, AY + 3.0, AZX - 0.5])
    return tidy(R)


def vault(R, top):
    """Dark: a ribbed ceiling, a few weak lamps high on the walls. The lamp is the light."""
    for k in range(9):
        y = 0.35 + k * 7.9
        R.parts.add(box(T, y - 0.3, top - 0.6, W - T, y + 0.3, top, 'tile', bottom='plaster'))
    for (x, y) in ((4.0, 4.0), (60.0, 4.0), (60.0, 60.0), (4.0, 60.0), (32.0, 60.0), (32.0, 4.0)):
        R.parts.add(cyl(x, y, 10.5, top - 0.6, 0.02, 6, side='iron', caps=False))
        R.light(sphere(x, y, 10.3, 0.22, 8, 4, 'e_dim'))


def table_(R, rnd):
    R.parts.add(box(TX0, TY0, TZ - 0.5, TX1, TY1, TZ, 'walnut'))
    R.parts.add(box(TX0 - 0.2, TY0 - 0.2, TZ - 0.35, TX1 + 0.2, TY1 + 0.2, TZ - 0.1, 'walnut'))
    for (x0, y0, x1, y1) in ((TX0 + 1.0, TY0 + 1.0, TX1 - 1.0, TY0 + 1.4), (TX0 + 1.0, TY1 - 1.4, TX1 - 1.0, TY1 - 1.0),
                             (TX0 + 1.0, TY0 + 1.4, TX0 + 1.4, TY1 - 1.4), (TX1 - 1.4, TY0 + 1.4, TX1 - 1.0, TY1 - 1.4)):
        R.parts.add(box(x0, y0, TZ - 1.4, x1, y1, TZ - 0.5, 'walnut'))
    for (x, y) in ((TX0 + 1.6, TY0 + 1.6), (TX1 - 1.6, TY0 + 1.6), (TX1 - 1.6, TY1 - 1.6), (TX0 + 1.6, TY1 - 1.6)):
        R.parts.add(box(x - 1.1, y - 1.1, 0, x + 1.1, y + 1.1, 0.6, 'walnut'))
        R.parts.add(cyl(x, y, 0.6, 1.4, 0.95, 16, side='walnut', top='walnut'))
        R.parts.add(cone(x, y, 1.4, TZ - 1.4, 0.75, 0.95, 16, side='walnut', top='walnut', bottom='walnut'))
        R.parts.add(box(x - 1.1, y - 1.1, TZ - 1.45, x + 1.1, y + 1.1, TZ - 0.5, 'walnut'))
    # the brass rail round the top, open where the dictionaries arrive
    i = 0.15
    ya, yb = 23.0, 24.45
    for (p, q) in (((TX0 + i, TY0 + i), (TX1 - i, TY0 + i)), ((TX1 - i, TY0 + i), (TX1 - i, TY1 - i)),
                   ((TX1 - i, TY1 - i), (TX0 + i, TY1 - i)), ((TX0 + i, TY1 - i), (TX0 + i, yb)), ((TX0 + i, ya), (TX0 + i, TY0 + i))):
        rail(R, p[0], p[1], q[0], q[1], TZ)
    # the page: one sheet the size of a field, a corner lifting, lines of a hand too big to read
    px0, py0, px1, py1 = 16.5, 12.0, 45.0, 26.5
    R.nocol.add(box(px0, py0, TZ, px1, py1, TZ + 0.02, 'ivory', skip=('-z',)))
    for k in range(17):
        y = py1 - 1.4 - k * 0.72
        x = px0 + 2.0 + (1.2 if k == 0 else 0.0)
        L = (px1 - px0 - 4.0) * (rnd.uniform(0.55, 1.0) if k % 6 != 5 else rnd.uniform(0.2, 0.45))
        while L > 0.5:
            wl = min(L, rnd.uniform(0.8, 3.2))
            R.nocol.add(box(x, y, TZ + 0.02, x + wl, y + 0.09, TZ + 0.024, 'walnut', skip=('-z',)))
            x += wl + rnd.uniform(0.35, 0.6); L -= wl + 0.45
    g = Geo()
    for k in range(6):
        a0, a1 = k * 0.16, (k + 1) * 0.16
        g.add(sloped('x', px1 + 3.0 * a0 / 0.96 - 3.0, px1 + 3.0 * a1 / 0.96 - 3.0, py0, py0 + 3.2,
                     TZ + 0.02 + 1.8 * a0 ** 2, TZ + 0.02 + 1.8 * a1 ** 2, TZ + 0.04 + 1.8 * a0 ** 2, TZ + 0.04 + 1.8 * a1 ** 2, 'ivory'))
    R.nocol.add(g)
    # under the table: dark, a camp of someone who reads by the light that comes over the edge
    R.light(sphere(24.0, 16.0, 0.25, 0.1, 8, 4, 'e_amber'))
    R.light(sphere(42.0, 30.0, 0.25, 0.1, 8, 4, 'e_amber'))
    for (x, y) in ((24.0, 16.0), (42.0, 30.0)):
        R.parts.add(cyl(x, y, 0, 0.14, 0.2, 10, side='brass', top='brass'))
    bulb(R, 32.0, 22.0, 2.4, r=0.14, m='e_dim', top=TZ - 0.5)


def book_stair(R, rnd):
    """Dictionaries stacked into a stair against the table's west side."""
    run, n = 1.3, 8
    y1 = BY0 + run * n
    for k in range(n):
        book_block(R, BX0, BY0 + run * k, BX1, y1, 0.5 * k, 0.5 * (k + 1) - 0.004,
                   cover=('oxblood', 'green', 'leather', 'walnut', 'oxblood', 'slate', 'green', 'leather')[k], spine='-x', over=0.12)
    stair_rail(R, BX0 + 0.1, BY0 + 0.4, 0.5, BX0 + 0.1, y1 - 0.9, 0.5 * n)
    stair_rail(R, BX1 - 0.1, BY0 + run + 0.4, 1.0, BX1 - 0.1, y1 - run - 0.1, 0.5 * (n - 1))
    rail(R, BX0 + 0.1, y1 - 0.1, BX1 - 0.02, y1 - 0.1, 0.5 * n)
    rail(R, BX0 + 0.1, y1 - 0.9, BX0 + 0.1, y1 - 0.1, 0.5 * n)


def foot(R):
    """The lamp's brass foot, in three tiers, a flight cut into its south face."""
    notch = math.radians(19)
    s = -math.pi / 2
    tiers = ((5.0, TZ, TZ + 0.7), (4.2, TZ + 0.7, TZ + 1.4), (3.4, TZ + 1.4, PZ))
    for (r, z0, z1) in tiers:
        R.parts.add(ring(SX, SY, z0, z1, SR - 0.05, r, 48, top='brass', bottom='brass', inner='brass', outer='brass',
                         a0=s + notch, a1=s + 2 * math.pi - notch))
        R.nocol.add(ring(SX, SY, z1 - 0.12, z1, r, r + 0.08, 48, top='gilt', bottom='gilt', inner='gilt', outer='gilt',
                         a0=s + notch, a1=s + 2 * math.pi - notch))
    # the notch's floor and its flight
    R.flight(SX - 1.0, SY - 5.5, TZ, 2.0, 10, (PZ - TZ) / 10, 0.3, '+y', m='brass', riser='bronze', side='brass')
    R.parts.add(box(SX - 1.0, SY - 2.5, TZ, SX + 1.0, SY - SR + 0.05, PZ, 'brass', top='brass'))
    # a felt pad under the foot, green
    R.nocol.add(cyl(SX, SY, TZ - 0.001, TZ + 0.05, 5.1, 48, side='green', top='green', bottom='green'))


def stem(R):
    """The stem, and a stair winding twice round it up to the arm."""
    R.parts.add(cyl(SX, SY, PZ, AZ + 1.2, SR, 24, side='brass', top='brass'))
    for z in (PZ + 0.3, 9.4, AZ + 0.9):
        R.parts.add(cyl(SX, SY, z - 0.15, z + 0.15, SR + 0.12, 24, side='gilt', top='gilt', bottom='gilt'))
    R.parts.add(sphere(SX, SY, AZ + 1.9, 0.95, 16, 8, 'brass'))
    R.nocol.add(beam((SX, SY, AZ + 1.9), (SX, AY + 1.0, AZX + SHO - 0.1), 0.55, 'brass'))
    a_s = -math.pi / 2
    turns = 2.0
    a_e = a_s + 2 * math.pi * turns
    R.parts.add(spiral_band(SX, SY, a_s, a_e, SR - 0.05, HR1, PZ, AZ, int(64 * turns), top='oak', side='bronze', bottom='bronze', thick=0.3))
    # the landing at the top, toward the shade
    le = math.radians(45)
    R.parts.add(spiral_band(SX, SY, a_e, a_e + le, SR - 0.05, HR1, AZ, AZ, 8, top='oak', side='bronze', bottom='bronze', thick=0.3))
    # rails on the outside of the stair: open for the first stretch, where it leaves the foot
    rr = HR1 - 0.1
    k0 = 6
    n = int(64 * turns)
    pts = []
    for k in range(k0, n + 1, 3):
        a = a_s + (a_e - a_s) * k / n
        pts.append((SX + rr * math.cos(a), SY + rr * math.sin(a), PZ + (AZ - PZ) * k / n))
    for p, q in zip(pts, pts[1:]):
        stair_rail(R, p[0], p[1], p[2], q[0], q[1], q[2], post=1.2)
    # the landing: railed on its outside beyond the arm, and at its end
    ae = a_e + le
    rail(R, SX + rr * math.cos(a_e + 0.62), SY + rr * math.sin(a_e + 0.62), SX + rr * math.cos(ae), SY + rr * math.sin(ae), AZ)
    rail(R, SX + (SR + 0.05) * math.cos(ae - 0.02), SY + (SR + 0.05) * math.sin(ae - 0.02), SX + rr * math.cos(ae - 0.02), SY + rr * math.sin(ae - 0.02), AZ)
    # the arm, from the landing into the back of the shade
    ay0 = AY + SHO - 0.3
    R.parts.add(box(HX0 - 0.2, ay0, AZ - 0.5, HX1 + 0.2, SY - SR, AZ, 'brass'))
    for x in (HX0 - 0.1, HX1 + 0.1):
        rail(R, x, ay0 + 0.25, x, SY - HR1 + 0.1, AZ)


def shade(R, rnd):
    """The shade: a half-cylinder of green glass, ivory inside, closed at its ends, with a floor at the
    level of the arm. Its underside is the light."""
    cy, cz = AY, AZX
    ro, ri = SHO, SHO - SHT
    nphi = 16
    phis = [math.pi * k / nphi for k in range(nphi + 1)]
    xs = [SX0, HX0, HX1, SX1]
    hole = lambda x0, x1, k: x0 >= HX0 - 1e-6 and x1 <= HX1 + 1e-6 and phis[k + 1] <= math.radians(57)
    P = lambda x, r, ph: (x, cy + r * math.cos(ph), cz + r * math.sin(ph))
    g = Geo()
    def quad(pts, m):
        ids = [g.vert(p) for p in pts]
        g.face(ids, m, [(p[0], p[2] + p[1]) for p in pts])
    for a in range(3):
        x0, x1 = xs[a], xs[a + 1]
        for k in range(nphi):
            if hole(x0, x1, k): continue
            p0, p1 = phis[k], phis[k + 1]
            quad([P(x0, ro, p0), P(x0, ro, p1), P(x1, ro, p1), P(x1, ro, p0)], 'green')          # outside
            quad([P(x0, ri, p0), P(x1, ri, p0), P(x1, ri, p1), P(x0, ri, p1)], 'ivory')          # inside
    # the hole's edges
    kh = max(k for k in range(nphi) if phis[k + 1] <= math.radians(57))
    ph = phis[kh + 1]
    quad([P(HX0, ro, ph), P(HX1, ro, ph), P(HX1, ri, ph), P(HX0, ri, ph)], 'brass')
    for x in (HX0, HX1):
        for k in range(kh + 1):
            quad([P(x, ri, phis[k]), P(x, ri, phis[k + 1]), P(x, ro, phis[k + 1]), P(x, ro, phis[k])], 'brass')
    # the lips along the bottom
    for ph_ in (0.0, math.pi):
        for a in range(3):
            if a == 1 and ph_ == 0.0: continue
            quad([P(xs[a], ri, ph_), P(xs[a], ro, ph_), P(xs[a + 1], ro, ph_), P(xs[a + 1], ri, ph_)], 'brass')
    R.parts.add(g)
    # end caps: half discs, green outside, ivory in
    for (x, m0, m1) in ((SX0, 'green', 'ivory'), (SX1, 'ivory', 'green')):
        cap = cyl(0, 0, 0, SHT, ro, 24, side='brass', top=m1, bottom=m0, a0=0.0, a1=math.pi)
        x0 = x if x == SX0 else x - SHT
        cap.v = [(x0 + vz, cy + vx, cz + vy) for vx, vy, vz in cap.v]
        R.parts.add(cap)
    # the floor inside, level with the arm; its underside is the glow you see from below
    R.parts.add(box(SX0 + SHT, cy - ri, AZ - 0.3, SX1 - SHT, cy + ri, AZ, 'oak', bottom='ivory'))
    R.light(box(SX0 + 0.6, cy - ri + 0.4, AZ - 0.33, SX1 - 0.6, cy + ri - 0.4, AZ - 0.31, 'e_lamp', skip=('+z',)))
    tube = xcyl(SX1 - SX0 - 2.0, 0.3, 12, side='e_lamp')
    tube.v = [(vx + SX0 + 1.0, vy + cy, vz + AZ - 0.75) for vx, vy, vz in tube.v]
    R.light(tube)
    for x in (SX0 + 1.0, SX1 - 1.0):
        R.parts.add(box(x - 0.2, cy - 0.2, AZ - 1.0, x + 0.2, cy + 0.2, AZ - 0.3, 'brass'))
    # the pull chain hanging from the front toward the page, a brass pull at its end
    cx, cyy = 36.5, cy - ro + 0.25
    for k in range(22):
        z = AZX - 0.3 - k * 0.24
        R.nocol.add(sphere(cx, cyy, z, 0.06, 6, 3, 'brass'))
    R.nocol.add(cone(cx, cyy, AZX - 0.3 - 22 * 0.24 - 0.5, AZX - 0.3 - 22 * 0.24, 0.16, 0.05, 10, side='brass', top='brass', bottom='brass'))
    # inside: a long room; chains hang from the glass with little bulbs; a chair, a table, a book, a bed
    for (x, n) in ((26.5, 7), (29.5, 8), (35.5, 8), (38.0, 7)):
        for k in range(n):
            R.nocol.add(sphere(x, cy, AZX + ri - 0.15 - k * 0.2, 0.04, 6, 3, 'brass'))
        R.light(sphere(x, cy, AZX + ri - 0.25 - n * 0.2, 0.08, 8, 4, 'e_lamp'))
    ch = chair(0, 0, 0.0, seat='velvet'); ch.xform(-0.3, 27.0, cy + 0.6, AZ)
    R.parts.add(ch)
    R.spot('sit', 27.0, cy + 0.6, AZ + 0.48, -0.3)
    t = table(27.6, cy - 0.2, 28.8, cy + 1.0, 0.74, 'walnut', top='leather'); t.v = [(vx, vy, vz + AZ) for vx, vy, vz in t.v]
    R.parts.add(t)
    R.parts.add(box(27.9, cy + 0.2, AZ + 0.74, 28.5, cy + 0.7, AZ + 0.77, 'ivory'))
    candle(R, 28.6, cy - 0.05, AZ + 0.74)
    R.parts.add(box(37.2, cy - 1.0, AZ, 39.4, cy + 0.2, AZ + 0.35, 'bed'))
    R.parts.add(box(39.0, cy - 1.0, AZ + 0.35, 39.4, cy + 0.2, AZ + 0.5, 'velvet'))
    R.spot('bed', 38.2, cy - 0.4, AZ + 0.35, 0.0)
    R.spot('plaque', 30.0, cy - 1.0, AZ)
    for k in range(9):
        x = SX0 + 1.2 + k * 1.7
        if HX0 - 0.6 < x < HX1 + 0.6: continue
        R.light(sphere(x, cy - ri + 0.12, AZ + 0.12, 0.04, 6, 3, 'e_candle'))
    secret(R, 30.0, cy, AZ, 'Inside the Shade',
           'The inside of the lamp: a long room of green glass, warm as an afternoon, hung with the pull chains. Somebody lives up here, where it is never dark.', r=3.0)


def nav(R):
    g = 1.6
    gal = [R.navpt(x, y, GZ) for (x, y) in ((g, g), (W - g, g), (W - g, D - g), (g, D - g), (g, 37.0))]
    R.link(*gal, gal[0])
    fl = [R.navpt(x, y) for (x, y) in ((7.0, 6.0), (57.0, 6.0), (57.0, 58.0), (7.0, 58.0), (7.0, 25.3))]
    R.link(*fl, fl[0])
    R.link(fl[4], R.navpt(4.1, 25.3), R.navpt(4.1, 37.1, GZ), gal[4])
    tb = [R.navpt(x, y, TZ) for (x, y) in ((16.0, 25.0), (16.0, 12.0), (48.0, 12.0), (48.0, 34.0), (38.0, 34.0))]
    R.link(*tb)
    R.link(tb[0], R.navpt(12.7, 23.8, TZ))
