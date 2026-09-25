"""The Breathing Hall: a long vaulted reading room whose walls swell between their ribs like the
flanks of something asleep. The bookcases have swollen with them: every row bellies out and leans in
with the vault. Between two of the bulges on the north side there is a gap, and behind it, an alcove."""
from lib import *
from kit_h4 import *

W, D = 32.0, 16.0
Y0, Y1 = 1.3, 14.7                  # the hall's side walls (thick, so the alcove can go into one)
JAMB, RISE = 2.2, 5.2
HW = (Y1 - Y0) / 2
RR = (HW * HW + RISE * RISE) / (2 * RISE)
ZC = JAMB + RISE - RR
RIBS = [2.3, 5.6, 10.4, 13.7, 18.3, 21.6, 26.4, 29.7]
ROW = 0.42


def off(z):
    """How far the vault has come in from the side wall at height z."""
    if z <= JAMB: return 0.0
    return HW - math.sqrt(max(0.0, RR * RR - (z - ZC) ** 2))


def make():
    R = Room('breathinghall', 2, 1, res=2048)
    R.sockets(floor='terrazzo', wall='plaster')
    rnd = random.Random(30)
    pr = arch_profile(D / 2, Y1 - Y0, 0, JAMB, 32, rise=RISE)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr), 'terrazzo', 'plaster')))
    # the doorways in the long walls are carried through their thickness
    dp = arch_profile(0, DW, 0, DJ, 16)
    for cx in (8.0, 24.0):
        R.cut(prism([(p + cx, q) for p, q in dp], 'y', T - 0.1, Y0 + 0.05, arch_mats(len(dp), 'terrazzo', 'plaster')))
        R.cut(prism([(p + cx, q) for p, q in dp], 'y', Y1 - 0.05, D - T + 0.1, arch_mats(len(dp), 'terrazzo', 'plaster')))
    # oculi in the crown of the vault, one per bay
    for x in (3.95, 8.0, 12.05, 16.0, 19.95, 24.0, 28.05):
        R.cut(cyl(x, D / 2, 6.6, R.hi + 0.5, 0.75, 20, side='plaster', top='plaster', bottom='plaster'))
        R.light(cyl(x, D / 2, R.hi - 0.1, R.hi - 0.07, 0.75, 20, side='e_sky', top='e_sky', bottom='e_sky'))
        R.nocol.add(ring(x, D / 2, JAMB + RISE - 0.1, JAMB + RISE - 0.02, 0.74, 0.95, 20, top='brass', bottom='brass', inner='brass', outer='brass'))

    ribs(R, rnd)
    bellies(R, rnd)
    alcove(R, rnd)
    furnish(R, rnd)

    navloop(R, [(2.0, 4.2), (8.0, 3.6), (16.0, 4.4), (24.0, 3.6), (30.0, 4.2), (30.0, 8.0), (30.0, 11.8), (24.0, 12.4), (16.0, 11.6), (8.0, 12.4), (2.0, 11.8), (2.0, 8.0)])
    a, b = R.navpt(8.0, 6.3), R.navpt(8.0, 9.7); R.link(a, b)
    a, b = R.navpt(24.0, 6.3), R.navpt(24.0, 9.7); R.link(a, b)
    R.spot('probe', 16.0, 8.0, 3.0)
    R.meta.update(label='The Breathing Hall', weight=4,
                  blurb='The walls are further in than they were a moment ago. Now they are not. Try not to count along with them.')
    R.meta['box'] = [[T, 0, T], [W - T, JAMB + RISE, D - T]]
    fx(R, 'breathe', [T, Y0, 0.0, W - T, Y1, JAMB + RISE], period=7.0, amp=0.12)
    fx(R, 'dust', [2.0, 5.0, 0.5, 30.0, 11.0, 6.5])
    secret(R, 16.0, Y1 + 0.2, 0.0, 'Between the Ribs',
           'You squeezed between two of the swellings. Behind them it is warm, and quiet, and the wall at your back rises and falls, very slowly.', r=1.4)
    return tidy(R)


def ribs(R, rnd):
    """Thick ribs following the vault, each swollen a little differently, sconces on their flanks."""
    for k, x in enumerate(RIBS):
        swell = 0.15 + 0.35 * (0.5 + 0.5 * math.sin(k * 2.1))
        pts, rs = [], []
        n = 22
        for i in range(n + 1):
            t = i / n
            # walk the section: up the south wall, over the arch, down the north wall
            if t < 0.12: y, z = Y0, JAMB * t / 0.12
            elif t > 0.88: y, z = Y1, JAMB * (1 - t) / 0.12
            else:
                u = (t - 0.12) / 0.76
                a0 = math.atan2(JAMB - ZC, -HW); a1 = math.atan2(JAMB - ZC, HW)
                a = a0 + (a1 - a0) * u
                y, z = D / 2 + RR * math.cos(a), ZC + RR * math.sin(a)
            # push inward (toward the section's middle), more at the haunches: the swell
            cy, cz = D / 2, 1.6
            dy, dz = cy - y, cz - z
            L = math.hypot(dy, dz) or 1.0
            r = 0.44 - 0.16 * math.sin(math.pi * t)
            d = r * 0.8 + swell * math.sin(math.pi * t) ** 0.7
            pts.append((x, y + dy / L * d, max(0.0, z + dz / L * d * (0.3 if z < JAMB else 1.0))))
            rs.append(r)
        pts[0] = (x, pts[0][1], -0.05); pts[-1] = (x, pts[-1][1], -0.05)
        R.parts.add(tube(pts, rs, 10, 'plaster'))
        for (y, s) in ((Y0 + 0.75, 1), (Y1 - 0.75, -1)):
            sconce(R, x, y, 2.5, math.pi / 2 * s, r=0.09)


def belly_rows(R, xa, xb, side, sag, rnd, shape='full', top_z=5.9, z0=0.0):
    """Rows of books between two ribs, each row pushed out by the belly and leaning in with the vault.
    side 'S' (facing +y) or 'N' (facing -y). shape 'full' | 'rise' (0 -> sag) | 'fall' (sag -> 0) | 'flat'."""
    nseg = 3
    xs = [xa + (xb - xa) * i / nseg for i in range(nseg + 1)]
    def bel(u):
        if shape == 'full': return math.sin(math.pi * u)
        if shape == 'rise': return math.sin(math.pi / 2 * u)
        if shape == 'fall': return math.cos(math.pi / 2 * u)
        return 0.0
    z = z0; i = 0
    while z + ROW <= top_z + 1e-6:
        breath = 0.55 + 0.45 * math.sin(math.pi * min(1.0, z / 6.0))
        o = off(z + ROW) + 0.03
        pts = []
        for x in xs:
            u = (x - xa) / (xb - xa)
            d = o + sag * bel(u) * breath
            pts.append((x, Y0 + d) if side == 'S' else (x, Y1 - d))
        if side == 'N': pts = pts[::-1]
        last = z + 2 * ROW > top_z + 1e-6
        for (p, q) in zip(pts, pts[1:]):
            L = math.hypot(q[0] - p[0], q[1] - p[1])
            ang = math.atan2(q[1] - p[1], q[0] - p[0]) + math.pi / 2
            row_case(R, p[0], p[1], z, L + 0.02, ang, frame='walnut', top=last, ends=(shape in ('rise', 'fall')))
        z += ROW; i += 1


def bellies(R, rnd):
    sags = {(2.3, 5.6): (0.7, 1.0), (10.4, 13.7): (1.1, 0.8), (13.7, 18.3): (0.9, None), (18.3, 21.6): (0.8, 1.2), (26.4, 29.7): (1.0, 0.7)}
    for (xa, xb), (ss, sn) in sags.items():
        belly_rows(R, xa + 0.25, xb - 0.25, 'S', ss, rnd)
        if sn is not None: belly_rows(R, xa + 0.25, xb - 0.25, 'N', sn, rnd)
    # the split bay: two swellings that nearly meet, a gap between them
    belly_rows(R, 13.95, 15.45, 'N', 1.35, rnd, 'rise')
    belly_rows(R, 16.55, 18.05, 'N', 1.35, rnd, 'fall')
    # the short end bays, and books over the doors in the door bays
    for (xa, xb) in ((T + 0.1, 2.05), (29.95, W - T - 0.1)):
        belly_rows(R, xa, xb, 'S', 0.0, rnd, 'flat')
        belly_rows(R, xa, xb, 'N', 0.0, rnd, 'flat')
    for (xa, xb) in ((5.85, 10.15), (21.85, 26.15)):
        for side in ('S', 'N'):
            belly_rows(R, xa, xb, side, 0.5, rnd, 'full', top_z=5.9, z0=4.64)
            belly_rows(R, xa, xa + 0.5, side, 0.0, rnd, 'flat', top_z=4.62)
            belly_rows(R, xb - 0.5, xb, side, 0.0, rnd, 'flat', top_z=4.62)
    # the end walls either side of their doors
    for (x, dirn) in ((T, '+x'), (W - T, '-x')):
        for (a, b) in ((Y0 + 1.6, 6.2), (9.8, Y1 - 1.6)):
            sh(R, dirn, x, a, b, rows=10, frame='walnut')


def alcove(R, rnd):
    R.cut(box(14.3, Y1 - 0.05, 0, 17.7, D - T - 0.1, 2.5, 'plaster', bottom='floor', top='plaster'))
    R.parts.add(box(14.3, Y1 - 0.05, 2.5 - 0.02, 17.7, D - T - 0.1, 2.5 + 0.12, 'walnut'))
    for k in range(5):
        row_case(R, 14.3, 14.75, 0.3 + k * ROW, 0.8, '+x', frame='walnut', top=(k == 4), depth=0.26, ends=True)
        row_case(R, 17.7, 15.55, 0.3 + k * ROW, 0.8, '-x', frame='walnut', top=(k == 4), depth=0.26, ends=True)
    chair(R, 16.0, 15.15, -math.pi / 2, frame='walnut', seat='velvet')
    floor_lamp(R, 14.85, 15.3, 1.55, m='e_dim')
    book_pile(R, 17.2, 15.35, 0.0, 5, rnd)
    open_book(R, 16.0, 15.15, 0.48, 0.3)
    candle(R, 16.8, 15.4, 0.0, h=0.18)
    R.spot('plaque', 16.0, 14.9, 0.0, math.pi / 2, text='In. Out. In. Out. It has been doing this since before the books, and it will go on after.')


def furnish(R, rnd):
    for (xa, xb) in ((3.4, 7.2), (10.2, 14.2), (17.8, 21.8), (24.8, 28.6)):
        table(R, xa, 7.45, xb, 8.55, top='leather')
        n = int((xb - xa) / 1.3)
        for k in range(n):
            x = xa + (k + 0.5) * (xb - xa) / n
            chair(R, x, 6.95, math.pi / 2); chair(R, x, 9.05, -math.pi / 2)
        for x in (xa + 0.8, xb - 0.8):
            desk_lamp(R, x, 8.0, 0.76)
        candle(R, (xa + xb) / 2, 8.0, 0.76, h=0.2)
        if rnd.random() < 0.6: open_book(R, (xa + xb) / 2 - 0.5, 7.8, 0.76, rnd.uniform(-0.4, 0.4))
    # a long runner of carpet down the middle
    R.nocol.add(box(2.6, 6.2, 0.0, W - 2.6, 9.8, 0.012, 'carpet'))
