"""The Motorway: a barrel-vaulted hall with a dual carriageway down the middle of it: asphalt, white
dashes, sodium lamps on tall posts, and bookcases with green lamps on the central reservation. It
comes out of a tunnel at one end and goes into a tunnel at the other, and the tunnels are the same
tunnel: the road goes on for ever. One of the reservation's bookcases is hollow; a stair inside it goes
down to the maintenance tunnel under the road."""
from kit_h10 import *

W, D = 32.0, 16.0
ZR = -0.2                           # the road surface (the pavements and the reservation are at 0)
SY0, SY1 = 1.4, 7.0                 # the southern carriageway
NY0, NY1 = 9.0, 14.6                # the northern one
JAMB, RISE = 4.8, 2.6
MOUTH = ((3.9, 4.6), (12.1, 4.6))   # tunnel mouths in the end walls: (centre y, width)
HB0, HB1 = 11.2, 16.2               # the hollow reservation block
HY0, HY1 = 7.4, 8.6                 # inside it
SN, SR, SRUN = 10, 0.21, 0.3
SX0 = HB0 + 0.45                    # the stair's top (it goes down +x)
SX1 = SX0 + SN * SRUN
KZ = -2.1
TX1 = 29.6                          # the tunnel's east end
PX0, PX1, PY0, PY1 = 25.4, 29.6, 5.6, 10.6    # the pump room


def make():
    R = Room('highway', 2, 1, res=2048, lo=-4.0)
    R.sockets(floor='floor', wall='tile')
    vault_cut(R, 'x', D / 2, D - 2 * T + 0.04, T - 0.02, W - T + 0.02, 0.0, JAMB, rise=RISE, m='plaster', floor='terrazzo', wall='tile')
    ribs(R, 'x', D / 2, D - 2 * T, [T + (W - 2 * T) * k / 8 for k in range(1, 8)], 0.0, JAMB, rise=RISE, d=0.35, t=0.45)
    road(R)
    mouths(R)
    walls(R)
    reservation(R)
    tunnel(R)
    lamps(R)
    navloop(R, [(1.8, 0.9), (16.0, 0.9), (30.2, 0.9)], close=False)
    navloop(R, [(1.8, 15.1), (16.0, 15.1), (30.2, 15.1)], close=False)
    a = navloop(R, [(2.5, 4.2), (16.0, 3.0), (29.5, 4.2), (29.5, 11.8), (16.0, 13.0), (2.5, 11.8)])
    b, c = R.navpt(1.8, 8.0), R.navpt(30.2, 8.0)
    R.link(a[0], b, a[5]); R.link(a[2], c, a[3])
    secret(R, 27.5, 8.1, KZ, 'The Maintenance Tunnel',
           'Under the road there is a tunnel for the people who look after it: pipes, cables, a desk with a telephone and a logbook. Every entry in the logbook says the same thing: No traffic.')
    fx(R, 'fog', [T, T, 0.0, W - T, D - T, 7.4], density=0.03)
    R.meta['portals'] = [
        {'a': {'c': [31.05, MOUTH[0][0], ZR], 'n': [1, 0, 0], 'w': 4.0, 'h': 3.3}, 'b': {'c': [0.95, MOUTH[0][0], ZR], 'n': [1, 0, 0], 'w': 4.0, 'h': 3.3}},
        {'a': {'c': [0.95, MOUTH[1][0], ZR], 'n': [-1, 0, 0], 'w': 4.0, 'h': 3.3}, 'b': {'c': [31.05, MOUTH[1][0], ZR], 'n': [-1, 0, 0], 'w': 4.0, 'h': 3.3}}]
    return done(R, 'The Motorway', weight=4, probe=(16.0, 4.2, 2.2),
                blurb='A motorway, three hundred yards of it, lit orange, running through the library from a tunnel to a tunnel. There is no traffic. There has never been any traffic. You look both ways anyway.')


# ---------------------------------------------------------------------------
def road(R):
    for (y0, y1) in ((SY0, SY1), (NY0, NY1)):
        R.cut(box(T - 0.02, y0, ZR, W - T + 0.02, y1, 0.3, 'tile', bottom='asphalt', top='tile'))
    # markings: dashed lane lines, solid edge lines, yellow lines by the reservation
    g = Geo(); y_ = Geo()
    for (y0, y1) in ((SY0, SY1), (NY0, NY1)):
        yc = (y0 + y1) / 2
        x = 1.2
        while x < W - 1.2:
            g.add(box(x, yc - 0.06, ZR, min(x + 2.0, W - 1.2), yc + 0.06, ZR + 0.006, 'lineW', skip=('-z',)))
            x += 4.0
        for yy in (y0 + 0.25, y1 - 0.25):
            m = 'lineY' if (abs(yy - (SY1 - 0.25)) < 0.01 or abs(yy - (NY0 + 0.25)) < 0.01) else 'lineW'
            (y_ if m == 'lineY' else g).add(box(T + 0.7, yy - 0.06, ZR, W - T - 0.7, yy + 0.06, ZR + 0.006, m, skip=('-z',)))
    R.nocol.add(g); R.nocol.add(y_)
    # kerbs: a stone edge along the pavements and the reservation
    k = Geo()
    for yy in (SY0, SY1, NY0, NY1):
        k.add(box(T, yy - 0.12, ZR, W - T, yy + 0.12, 0.02, 'tile', skip=('-z',)))
    R.parts.add(k)


def mouths(R):
    """Tunnel mouths in both end walls, one for each carriageway (a portal joins east to west)."""
    for (c, w) in MOUTH:
        for (a0, a1) in ((0.05, T + 0.1), (W - T - 0.1, W - 0.05)):
            pr = arch_profile(c, w, ZR, 2.6, 14)
            R.cut(prism(pr, 'x', a0, a1, arch_mats(len(pr), 'asphalt', 'slate')))
        # the tunnel beyond (seen when the portals are not drawn): black, with a line of lamps
        for (x, s_) in ((0.05, 1), (W - 0.05, -1)):
            R.parts.add(box(min(x, x + s_ * 0.01), c - w / 2, ZR, max(x, x + s_ * 0.01), c + w / 2, 5.0, 'black'))
            R.light(box(min(x, x + s_ * 0.02), c - 0.3, 3.4, max(x, x + s_ * 0.02), c + 0.3, 3.5, 'e_sodium'))
        # a stone surround with a keystone
        for x in (T, W - T):
            s_ = 1 if x < 16 else -1
            R.parts.add(box(min(x, x + s_ * 0.2), c - 0.35, ZR + 2.6 + w / 2, max(x, x + s_ * 0.2), c + 0.35, ZR + 2.6 + w / 2 + 0.6, 'tile'))


def walls(R):
    # piers along both long walls and bookcases between them, above the pavements
    xs = [T + (W - 2 * T) * k / 8 for k in range(1, 8)]
    for x in xs:
        for (y0, y1) in ((T, T + 0.55), (D - T - 0.55, D - T)):
            R.parts.add(box(x - 0.35, y0, 0, x + 0.35, y1, JAMB, 'tile', skip=('-z', '+z')))
            R.parts.add(box(x - 0.45, y0, JAMB - 0.3, x + 0.45, y1 + (0.1 if y0 < 8 else 0.0) - (0.0 if y0 < 8 else 0.1), JAMB, 'tile'))
    edges = [T] + xs + [W - T]
    for (a, b) in zip(edges, edges[1:]):
        a0, b0 = a + 0.4, b - 0.4
        for (y, face) in ((T, '+y'), (D - T, '-y')):
            spans = [(a0, b0)]
            # keep the doorways clear
            out = []
            for (p, q) in spans:
                cut = False
                for c in (8.0, 24.0):
                    if p < c + 1.9 and q > c - 1.9:
                        if c - 1.9 - p > 0.8: out.append((p, c - 1.9))
                        if q - (c + 1.9) > 0.8: out.append((c + 1.9, q))
                        cut = True
                if not cut: out.append((p, q))
            for (p, q) in out:
                sh(R, face, y, p, q, rows=9, depth=0.3, frame='walnut')
            for c in (8.0, 24.0):
                if a0 < c < b0:
                    sh(R, face, y, c - 1.9, c + 1.9, z=3.6, rows=2, depth=0.3, frame='walnut')


def block(R, x0, x1, hollow=False):
    """A double-sided bookcase block on the reservation, a green lamp on its top."""
    y0, y1, h = 7.05, 8.95, 2.3
    if not hollow:
        sh(R, '-y', HY0 - 0.02, x0, x1, rows=5, depth=0.3, frame='walnut')
        sh(R, '+y', HY1 + 0.02, x0, x1, rows=5, depth=0.3, frame='walnut')
        R.parts.add(box(x0 - 0.06, HY0 - 0.02, 0, x1 + 0.06, HY1 + 0.02, 2.25, 'walnut', skip=('-z',)))
    else:
        sh(R, '-y', HY0 - 0.02, x0, x1, rows=5, depth=0.3, frame='walnut')
        sh(R, '+y', HY1 + 0.02, x0, x1, rows=5, depth=0.3, frame='walnut')
        R.parts.add(box(x1 - 0.02, HY0 - 0.02, 0, x1 + 0.06, HY1 + 0.02, 2.25, 'walnut'))
        R.parts.add(box(x0 - 0.06, HY0 - 0.02, 2.25, x1 + 0.06, HY1 + 0.02, 2.3, 'walnut'))
        R.parts.add(box(x0 + 0.02, HY0 - 0.02, 2.0, x1 - 0.02, HY1 + 0.02, 2.25, 'walnut'))
        # the west end is a narrow false bookcase: walk into it
        shelf(R, x0 + 0.32, HY0, 0, HY1 - HY0, '-x', rows=4, frame='walnut', solid=False)
    R.parts.add(box(x0 - 0.1, y0 + 0.15, 2.25, x1 + 0.1, y1 - 0.15, 2.35, 'walnut', top='oak'))
    llamp(R, (x0 + x1) / 2, 8.0, 2.35, 0.0, lit=True, m='e_lamp', col=False)


def reservation(R):
    x = 3.6
    L = 2.6
    while x + L <= W - 3.6:
        if x + L > HB0 - 0.6 and x < HB1:
            block(R, HB0, HB1, hollow=True)
            x = HB1 + 1.2
            continue
        block(R, x, x + L)
        x += L + 1.2
    # a few cones, a book trolley abandoned in a lane
    rs = rng(4)
    for (cx, cy) in ((6.0, 6.3), (6.8, 6.4), (7.6, 6.5), (25.0, 9.7)):
        R.parts.add(cone(cx, cy, ZR, ZR + 0.7, 0.18, 0.03, 8, 'oxblood'))
        R.nocol.add(cone(cx, cy, ZR + 0.3, ZR + 0.42, 0.115, 0.09, 8, 'ivory'))
        R.parts.add(box(cx - 0.22, cy - 0.22, ZR, cx + 0.22, cy + 0.22, ZR + 0.04, 'black'))
    t = Geo()
    t.add(box(-0.5, -0.25, 0.25, 0.5, 0.25, 0.3, 'oak'))
    t.add(box(-0.5, -0.25, 0.75, 0.5, 0.25, 0.8, 'oak'))
    for (px, py) in ((-0.45, -0.2), (0.45, -0.2), (0.45, 0.2), (-0.45, 0.2)):
        t.add(box(px - 0.02, py - 0.02, 0.05, px + 0.02, py + 0.02, 0.8, 'iron'))
    R.parts.add(t.xform(0.4, 20.0, 11.2, ZR))
    bk = Geo()
    book_row_flat(bk, 20.0, 11.2, ZR + 0.8, 0.4, rs, 4)
    book_row_flat(bk, 20.7, 10.6, ZR, 1.4, rs, 1)
    R.nocol.add(bk)


def tunnel(R):
    """Inside the hollow block a stair goes down, and a tunnel runs east under the reservation."""
    R.cut(box(HB0 - 0.1, HY0, 0.0, HB1 - 0.02, HY1, 2.0, 'walnut', bottom='oak', top='walnut'))
    R.cut(box(SX0 - 0.02, HY0 + 0.05, KZ, SX1 + 0.02, HY1 - 0.05, 0.05, 'tile', bottom='floor', top='tile'))
    R.flight(SX1, HY0 + 0.05, KZ, HY1 - HY0 - 0.1, SN, SR, SRUN, '-x', m='slate', riser='iron', side='tile')
    R.cut(box(SX1 - 0.02, HY0, KZ, TX1, HY1, -0.3, 'tile', bottom='slate', top='plaster'))
    R.cut(box(PX0, PY0, KZ, PX1, PY1, -0.3, 'tile', bottom='slate', top='plaster'))
    # pipes and cables along the tunnel, bulbs in cages
    g = Geo()
    for (z, r, m) in ((-0.55, 0.07, 'iron'), (-0.75, 0.05, 'bronze')):
        g.add(xtube(SX1, PX0, HY1 - 0.1, z, r, 8, m))
    for (z, r, m) in ((-0.6, 0.06, 'rust'),):
        g.add(xtube(SX1, PX0, HY0 + 0.1, z, r, 8, m))
    R.nocol.add(g)
    for x in (17.5, 21.0, 24.5):
        bulb(R, x, 8.0, -0.75, r=0.06, m='e_dim', top=-0.3)
    # the pump room: a desk, a telephone, the logbook, a chair, a big valve, a grating
    R.parts.add(ltable(PX1 - 1.6, PY1 - 1.0, PX1 - 0.2, PY1 - 0.3, 0.78, 'steel', top='oak').xform(0, 0, 0, KZ))
    R.parts.add(lchair_legs(PX1 - 0.9, PY1 - 1.5, math.pi / 2).xform(0, 0, 0, KZ))
    R.spot('sit', PX1 - 0.9, PY1 - 1.5, KZ + 0.48, math.pi / 2)
    ob = box(-0.2, -0.14, 0, 0.0, 0.14, 0.02, 'ivory', sides='oxblood'); ob.add(box(0.0, -0.14, 0, 0.2, 0.14, 0.02, 'ivory', sides='oxblood'))
    R.nocol.add(ob.xform(0.0, PX1 - 0.9, PY1 - 0.65, KZ + 0.78))
    R.nocol.add(box(PX1 - 1.5, PY1 - 0.9, KZ + 0.78, PX1 - 1.25, PY1 - 0.65, KZ + 0.86, 'black'))
    R.nocol.add(box(PX1 - 1.52, PY1 - 0.82, KZ + 0.9, PX1 - 1.23, PY1 - 0.74, KZ + 0.94, 'black'))
    llamp(R, PX1 - 0.4, PY1 - 0.55, KZ + 0.78, 0.4, lit=True, m='e_amber')
    R.parts.add(ztube(KZ, -0.3, PX0 + 0.6, PY0 + 0.6, 0.25, 12, 'iron'))
    R.parts.add(box(PX0 + 0.25, PY0 + 0.25, KZ, PX0 + 0.95, PY0 + 0.95, KZ + 0.3, 'iron'))
    wheel = Geo()
    for k in range(10):
        a0, a1 = 2 * math.pi * k / 10, 2 * math.pi * (k + 1) / 10
        wheel.add(beam((PX0 + 0.6 + 0.3 * math.cos(a0), PY0 + 0.9, KZ + 1.2 + 0.3 * math.sin(a0)), (PX0 + 0.6 + 0.3 * math.cos(a1), PY0 + 0.9, KZ + 1.2 + 0.3 * math.sin(a1)), 0.04, 'oxblood'))
    R.nocol.add(wheel)
    sh(R, '+y', PY0, PX0 + 1.4, PX1 - 0.3, z=KZ, rows=3, frame='iron', depth=0.3)
    bulb(R, (PX0 + PX1) / 2, (PY0 + PY1) / 2, -0.8, r=0.07, m='e_dim', top=-0.3)
    R.spot('plaque', PX1 - 0.9, PY1 - 0.65, KZ + 0.8, -math.pi / 2, text='LOG. 00:00 No traffic. 01:00 No traffic. 02:00 No traffic.')
    a, b, c = R.navpt(SX1 + 0.6, 8.0, KZ), R.navpt(PX0 - 0.6, 8.0, KZ), R.navpt(PX0 + 2.0, PY0 + 2.2, KZ)
    R.link(a, b, c)


def lamps(R):
    """Sodium lamps on tall posts on both pavements, their arms reaching out over the lanes."""
    for x in (4.0, 12.0, 20.0, 28.0):
        for (y, s_) in ((0.95, 1), (D - 0.95, -1)):
            R.parts.add(cyl(x, y, 0, 0.3, 0.14, 8, side='iron', top='iron'))
            R.parts.add(cyl(x, y, 0.3, 5.0, 0.06, 8, side='iron', caps=False))
            R.nocol.add(beam((x, y, 4.95), (x, y + s_ * 1.6, 5.25), 0.07, 'iron'))
            R.nocol.add(box(x - 0.35, y + s_ * 1.5 - 0.18, 5.2, x + 0.35, y + s_ * 1.5 + 0.18, 5.34, 'iron'))
            R.light(box(x - 0.3, y + s_ * 1.5 - 0.13, 5.16, x + 0.3, y + s_ * 1.5 + 0.13, 5.2, 'e_sodium'))
    # small amber lamps low on the piers (they stay on)
    for x in (T + (W - 2 * T) * k / 8 for k in (2, 6)):
        for y in (T + 0.6, D - T - 0.6):
            R.light(sphere(x, y, 2.4, 0.1, 8, 4, 'e_amber'))
