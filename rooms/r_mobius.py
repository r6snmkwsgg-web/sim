"""The Mobius Hall: a long reading hall with a ribbon of shelves overhead that turns half over along its
length, lamps hanging from it at every angle, ribs twisting round it and a brass line on the floor tracing
its shadow. The far end is a portal onto the near end, so the ribbon meets itself upside down and the hall
never ends. Behind the tightest point of the twist, a gap in the shelves opens on a nook where nothing is
turned at all."""
from kit_h11 import *

W, D = 32.0, 16.0
HY0, HY1 = 2.6, 13.4          # the hall's walls
HZ = 7.4                      # its ceiling
XA, XB = 27.0, 5.0            # the portal planes: the far end (a) opens onto the near end (b)
FT = 0.5                      # the end frames' thickness
OY0, OY1, OH = 3.2, 12.8, 7.0 # the frames' opening
CY, CZ, HW = 8.0, 5.0, 2.3    # the ribbon: axis, half width
BAYS = [XB + FT, 11.0, 16.5, 22.0, XA]
NK = (14.4, 17.6, 14.0)       # the nook: x0, x1, y0 (to the north wall)


def theta(x):
    return math.pi * (x - XB) / (XA - XB)


def make():
    R = Room('mobius', 2, 1, res=2048)
    R.sockets(floor='floor', wall='tile')
    hall(R)
    frames(R)
    ribbon(R)
    ribs(R)
    walls(R)
    nook(R)
    portal(R, P((XA, CY, 0.0), (1, 0, 0), OY1 - OY0, OH), P((XB, CY, 0.0), (1, 0, 0), OY1 - OY0, OH))
    # walkers: along the hall (both sides of the tables), out to the doors
    a = navloop(R, [(6.5, 11.5), (12.0, 11.5), (19.0, 11.5), (25.5, 11.5), (25.5, 6.0), (19.0, 6.0), (12.0, 6.0), (6.5, 6.0)])
    for (x, y0, y1) in ((8.0, 6.0, 1.2), (24.0, 6.0, 1.2), (8.0, 11.5, 14.8), (24.0, 11.5, 14.8)):
        i0, i1 = R.navpt(x, y0), R.navpt(x, y1)
        R.link(i0, i1)
    R.link(a[0], R.navpt(2.5, 8.0)); R.link(a[3], R.navpt(29.5, 8.0))
    secret(R, 16.0, 14.8, 0.0, 'The Level Nook',
           'Behind the place where the shelves overhead stand on their edge, a gap, and behind the gap a nook where everything is level: the floor, the shelf, the lamp, the book on the table, lying perfectly flat. You had not noticed how tilted you felt until now.', r=1.6)
    fx(R, 'dust', [XB, HY0, 0.5, XA, HY1, HZ - 0.3])
    return done(R, 'The Mobius Hall', weight=3, probe=(16.0, 5.5, 2.0), top=HZ,
                blurb='A long reading hall, and overhead a ribbon of shelves that turns slowly over as it goes, lamps hanging off it at every angle. At the far end the hall begins again. The ribbon is upside down now. So, you suspect, are you.')


def hall(R):
    R.cut(box(XB - 0.02, HY0, 0, XA + FT + 0.02, HY1, HZ, 'tile', bottom='floor', top='plaster'))
    # vestibules at each end, and the ways through to the doors in the long walls
    R.cut(box(T - 0.01, T - 0.01, 0, XB + 0.01, D - T + 0.01, 5.2, 'tile', bottom='floor', top='plaster'))
    R.cut(box(XA + FT - 0.01, T - 0.01, 0, W - T + 0.01, D - T + 0.01, 5.2, 'tile', bottom='floor', top='plaster'))
    for x in (8.0, 24.0):
        R.cut(prism(arch_profile(x, DW, 0, DJ), 'y', T, HY0 + 0.05, arch_mats(len(arch_profile(x, DW, 0, DJ)), 'floor', 'tile')))
        R.cut(prism(arch_profile(x, DW, 0, DJ), 'y', HY1 - 0.05, D - T, arch_mats(len(arch_profile(x, DW, 0, DJ)), 'floor', 'tile')))
    # the floor's brass line: the ribbon's shadow, twisting
    g = Geo()
    n = 88
    for k in range(n):
        x0, x1 = XB + FT + (XA - XB - FT) * k / n, XB + FT + (XA - XB - FT) * (k + 1) / n
        for s in (-1, 1):
            y0, y1 = CY + s * HW * math.cos(theta(x0)), CY + s * HW * math.cos(theta(x1))
            g.add(panel_z(0.004, 0, 0, 1, 1, 'gilt'))
            g.v[-4:] = [(x0, y0 - 0.04, 0.004), (x1, y1 - 0.04, 0.004), (x1, y1 + 0.04, 0.004), (x0, y0 + 0.04, 0.004)]
    R.nocol.add(g)


def frames(R):
    """The two end frames, identical: a stone wall across the hall with a great rectangular opening."""
    for x in (XB, XA):
        g = Geo()
        g.add(box(x, HY0, 0, x + FT, OY0, HZ, 'tile', skip=('+z',)))
        g.add(box(x, OY1, 0, x + FT, HY1, HZ, 'tile', skip=('+z',)))
        g.add(box(x, OY0, OH, x + FT, OY1, HZ, 'tile', skip=('+z',)))
        R.parts.add(g)
        for (face, xx) in ((math.pi, x), (0.0, x + FT)):
            R.parts.add(local(frame_geo(OY1 - OY0, OH, bw=0.25, depth=0.12, m='walnut', sill=False), face, xx, CY, 0))


def ribbon(R):
    """The twisting ribbon of shelves: a band about the hall's axis turning through half a turn from one
    end frame to the other; books on both faces, shelf boards between the rows, brass edges, and lamps
    hanging off its lower face along its normal."""
    rs = rng(21)
    n = 88
    x0_, x1_ = XB + FT, XA
    rows = 10
    rh = 2 * HW / rows
    core = Geo(); boards = Geo(); edges = Geo(); bands = {}
    def P_(x, u, off, side):
        t = theta(x)
        nn = (0.0, -math.sin(t), math.cos(t))
        return (x, CY + u * math.cos(t) + side * off * nn[1], CZ + u * math.sin(t) + side * off * nn[2])
    for k in range(n):
        xa, xb = x0_ + (x1_ - x0_) * k / n, x0_ + (x1_ - x0_) * (k + 1) / n
        xm = (xa + xb) / 2
        t = theta(xm)
        dv = (0.0, math.cos(t), math.sin(t))
        for side in (-1, 1):
            nn = (0.0, -math.sin(t) * side, math.cos(t) * side)
            # the core face (walnut) at 0.06 off the centre
            q = [P_(xa, -HW, 0.06, side), P_(xb, -HW, 0.06, side), P_(xb, HW, 0.06, side), P_(xa, HW, 0.06, side)]
            gg = Geo(); ids = [gg.vert(p) for p in q]
            A = [q[1][i] - q[0][i] for i in range(3)]; B = [q[3][i] - q[0][i] for i in range(3)]
            cr = (A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0])
            if sum(cr[i] * nn[i] for i in range(3)) < 0: ids = ids[::-1]
            gg.face(ids, 'walnut', [(0, 0), (xb - xa, 0), (xb - xa, 2 * HW), (0, 2 * HW)])
            core.add(gg)
            # books in each row
            for r in range(rows):
                u0 = -HW + r * rh + 0.03
                p0 = P_(xa, u0, 0.07, side)
                merge_bands(bands, book_band(p0, (1, 0, 0), dv, nn, xb - xa, rh - 0.07, rs, seg=(0.1, 0.25), depth=0.02))
            # the boards between rows, standing off the face
            for r in range(rows + 1):
                u = -HW + r * rh
                q = [P_(xa, u, 0.06, side), P_(xb, u, 0.06, side), P_(xb, u, 0.34, side), P_(xa, u, 0.34, side)]
                for flip in (False, True):
                    gg = Geo(); ids = [gg.vert(p) for p in q]
                    if flip: ids = ids[::-1]
                    gg.face(ids, 'walnut', [(0, 0), (1, 0), (1, 0.3), (0, 0.3)])
                    boards.add(gg)
        # brass edges
        for u in (-HW - 0.05, HW + 0.05):
            edges.add(beam(P_(xa, u, 0, 1), P_(xb, u, 0, 1), 0.1, 'brass', 0.72))
    R.nocol.add(core); R.nocol.add(boards); R.nocol.add(edges)
    add_bands(R, bands)
    # lamps hanging off its lower face, along the face's normal
    for x in [b + 1.4 for b in BAYS[:-1]] + [b + 4.1 for b in BAYS[:-1]]:
        t = theta(x)
        for u in (-1.2, 1.2):
            for side in (-1, 1):
                nz = math.cos(t) * side
                if nz > -0.2: continue
                a = P_(x, u, 0.34, side)
                L = 1.1
                nn = (0.0, -math.sin(t) * side, math.cos(t) * side)
                b = (x, a[1] + nn[1] * L, a[2] + nn[2] * L)
                if b[2] < 2.9: b = (x, a[1] + nn[1] * (a[2] - 2.9) / max(0.2, -nn[2]), 2.9)
                R.nocol.add(beam(a, b, 0.02, 'brass'))
                R.light(sphere(b[0], b[1], b[2], 0.16, 8, 4, 'e_lamp'))
                R.nocol.add(frustum(b[0], b[1], b[2] + 0.08, b[2] + 0.3, 0.3, 0.1, 10, 'green', inner='ivory'))


def ribs(R):
    """Square ribs round the ribbon, turned with it, drawn only above the bookcases."""
    zlo, zhi = 3.75, HZ - 0.02
    hs = 3.4
    g = Geo()
    for x in [b for b in BAYS[1:-1]] + [b + 2.75 for b in BAYS[:-1]]:
        t = theta(x) + math.pi / 4
        corners = []
        for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            yy, zz = a * hs, b * hs
            corners.append((CY + yy * math.cos(t) - zz * math.sin(t), CZ + yy * math.sin(t) + zz * math.cos(t)))
        for i in range(4):
            (y0, z0), (y1, z1) = corners[i], corners[(i + 1) % 4]
            # clip the edge to zlo..zhi and to the hall's width
            ts = [0.0, 1.0]
            for (v0, v1, lo, hi) in ((z0, z1, zlo, zhi), (y0, y1, HY0 + 0.1, HY1 - 0.1)):
                if abs(v1 - v0) < 1e-9:
                    if not (lo <= v0 <= hi): ts = None; break
                    continue
                ta, tb = (lo - v0) / (v1 - v0), (hi - v0) / (v1 - v0)
                ta, tb = min(ta, tb), max(ta, tb)
                ts = [max(ts[0], ta), min(ts[1], tb)]
                if ts[0] >= ts[1]: ts = None; break
            if not ts: continue
            pa = (x, y0 + (y1 - y0) * ts[0], z0 + (z1 - z0) * ts[0])
            pb = (x, y0 + (y1 - y0) * ts[1], z0 + (z1 - z0) * ts[1])
            if math.dist(pa, pb) > 0.2:
                g.add(beam(pa, pb, 0.22, 'walnut', 0.3))
    R.nocol.add(g)


def walls(R):
    # pilasters at the bays, bookcases between, windows above on the south side, tables down the middle
    for x in BAYS[1:-1]:
        for (y0, y1) in ((HY0, HY0 + 0.35), (HY1 - 0.35, HY1)):
            R.parts.add(box(x - 0.3, y0, 0, x + 0.3, y1, HZ, 'tile', skip=('+z',)))
    for i in range(4):
        a, b = BAYS[i] + (0.35 if i else 0.05), BAYS[i + 1] - (0.35 if i < 3 else 0.05)
        for (face, bk) in (('+y', HY0), ('-y', HY1)):
            spans = [(a, b)]
            for dx in (8.0, 24.0):
                if a < dx < b: spans = [(a, dx - DW / 2 - 0.2), (dx + DW / 2 + 0.2, b)]
            if face == '-y' and a < 16.0 < b:
                spans = [(a, 15.6), (16.4, b)]
            for (p, q) in spans:
                if q - p > 0.6:
                    sh(R, face, bk, p, q, rows=8, frame='walnut')
        c = (BAYS[i] + BAYS[i + 1]) / 2
        if not (c - 1.3 < 8.0 < c + 1.3 or c - 1.3 < 24.0 < c + 1.3):
            window(R, 'S', c, 3.85, 1.6, 2.0, depth=0.3, wallpos=HY0, mull=2, trans=1)
        R.parts.add(ltable(c - 1.5, 7.3, c + 1.5, 8.7, top='leather'))
        for dx in (-0.9, 0.9):
            llamp(R, c + dx, 8.0, 0.76, a=math.pi / 2 * 0)
            R.nocol.add(lchair(c + dx, 6.75, math.pi / 2)); R.nocol.add(lchair(c + dx, 9.25, -math.pi / 2))
    # vestibules: books round them, lanterns
    for (x0, x1) in ((T, XB), (XA + FT, W - T)):
        sh(R, '+y', T, x0 + 0.4, x1 - 0.4, rows=11, frame='walnut') if x1 - x0 > 2 else None
        sh(R, '-y', D - T, x0 + 0.4, x1 - 0.4, rows=11, frame='walnut') if x1 - x0 > 2 else None
        lantern(R, (x0 + x1) / 2, 1.0, 0.0)
        pendant(R, (x0 + x1) / 2, 4.0, 3.6, 5.2, r=0.26)
        pendant(R, (x0 + x1) / 2, 12.0, 3.6, 5.2, r=0.26)
    for (x, s) in ((T, 1), (W - T, -1)):
        f = '+x' if s > 0 else '-x'
        sh(R, f, x, 0.8, 6.3, rows=11, frame='walnut'); sh(R, f, x, 9.7, D - 0.8, rows=11, frame='walnut')


def nook(R):
    x0, x1, y0 = NK
    R.cut(box(15.6, HY1 - 0.05, 0, 16.4, y0 + 0.05, 2.3, 'tile', bottom='floor', top='plaster'))
    R.cut(box(x0, y0, 0, x1, D - T, 2.8, 'damask', bottom='floor', top='plaster'))
    sh(R, '-y', D - T, x0 + 0.1, x1 - 0.1, rows=5, frame='walnut')
    armchair(R, x0 + 0.6, y0 + 0.75, 0.0)
    R.parts.add(ltable(15.6, 14.3, 16.6, 14.9, top='leather'))
    llamp(R, 15.8, 14.75, 0.76)
    open_book(R, 16.25, 14.55, 0.76, ang=0.0)
    R.spot('plaque', x1 - 0.4, y0 + 0.8, 1.3, math.pi, text='Level.')
    bulb(R, 16.8, 14.6, 2.3, r=0.07, m='e_amber', top=2.8)
