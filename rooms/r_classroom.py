"""The Classroom: a hall of desks, row on row of them, facing a blackboard the size of a house, covered in
chalk: sums, circles, a spiral that might be a galaxy. Sun comes in sideways through tall windows. The
blackboard stands a little out from the wall; behind its east end you can slip into the gap, and in the
wall behind it is the door of the teacher's store room."""
from kit_h10 import *

W = D = 32.0
YN = 28.0                          # the hall's north wall
H = 7.4
BX0, BX1, BY0, BY1, BZ0, BZ1 = 10.4, 21.4, 26.95, 27.12, 0.0, 6.9     # the blackboard, standing off the wall
SX0, SX1, SY0, SY1, SH = 12.2, 19.8, YN + 0.3, D - T - 0.05, 3.2       # the store room
DX0, DX1 = 15.4, 16.5                                                # its door, behind the board


def make():
    R = Room('classroom', 2, 2, res=2048)
    R.sockets(floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, YN, H, 'tile', bottom='floor', top='plaster'))
    tunnel_y(R, 8.0, YN - 0.05, D - T - 0.5)
    tunnel_y(R, 24.0, YN - 0.05, D - T - 0.5)
    ceiling(R)
    walls(R)
    board(R)
    desks(R)
    dais(R)
    store(R)
    navloop(R, [(16.0, 2.0), (16.0, 12.0), (16.0, 22.4), (22.0, 23.6), (30.0, 23.0), (30.0, 12.0), (30.0, 2.4), (22.0, 2.2)])
    a, b, c = R.navpt(2.0, 23.0), R.navpt(2.0, 12.0), R.navpt(9.0, 2.2)
    R.link(2, a, b, c, 0)
    secret(R, 16.0, 30.0, 0.0, "The Teacher's Store Room",
           "Behind the blackboard is the store room: chalk by the crate, maps rolled up, a globe with a dent in it, and on the desk the register, open, with every name you have ever had written in it, and a tick against each one: present.")
    secret(R, 21.0, 27.55, 0.0, 'Behind the Blackboard', 'The blackboard stands out from the wall, and there is just room to slip behind it.', r=1.0)
    for y in (4.0, 12.0, 16.0, 20.0):
        fx(R, 'dust', [0.5, y - 1.2, 0.5, 14.0, y + 1.2, 6.5])
    return done(R, 'The Classroom', weight=5, probe=(16.0, 6.0, 2.6),
                blurb='Desks for a thousand, all facing the blackboard, and on the blackboard a lesson nobody has rubbed out. You have the uneasy feeling you were supposed to have learned it by now.')


# ---------------------------------------------------------------------------
def ceiling(R):
    g = Geo()
    for k in range(1, 8):
        x = T + (W - 2 * T) * k / 8
        g.add(box(x - 0.18, T, H - 0.45, x + 0.18, YN, H, 'walnut', skip=('+z',)))
    for k in range(1, 7):
        y = T + (YN - T) * k / 7
        g.add(box(T, y - 0.14, H - 0.35, W - T, y + 0.14, H, 'walnut', skip=('+z',)))
    R.nocol.add(g)
    for x in (6.0, 11.0, 21.0, 26.0):
        for y in (6.0, 13.0, 20.0):
            pendant(R, x, y, 4.3, H - 0.4, r=0.26)


def walls(R):
    # tall windows on the west wall, the sun coming through them
    for y in (4.0, 12.0, 16.0, 20.0):
        window(R, 'W', y, 1.1, 2.2, 4.4, depth=0.3, em='e_sky', frame='iron', mull=2, trans=3)
    # between them, bookcases
    for (a, b) in ((0.6, 2.7), (5.3, 6.2), (13.3, 14.7), (17.3, 18.7), (21.3, 22.1), (25.9, YN - 0.3)):
        sh(R, '+x', T, a, b, rows=10, frame='walnut')
    # the east wall: bookcases the whole way, two tiers, a ladder
    for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, YN - 0.3)):
        sh(R, '-x', W - T, a, b, rows=10, frame='walnut')
        sh(R, '-x', W - T, a, b, z=4.45, rows=6, frame='walnut')
    R.nocol.add(ladder(W - T - 0.36, 15.0, math.pi, h=4.3, lean=0.9))
    # the south wall and the north wall's ends
    for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, W - 0.6)):
        sh(R, '+y', T, a, b, rows=10, frame='walnut')
    for (a, b) in ((0.6, 6.1), (25.9, W - 0.6)):
        sh(R, '-y', YN, a, b, rows=10, frame='walnut')
    sh(R, '-y', YN, 9.9, BX0 - 0.1, rows=10, frame='walnut')
    for (a, b) in ((6.1, 9.9), (22.1, 25.9)):
        sh(R, '+y', T, a, b, z=3.9, rows=3, frame='walnut')
        sh(R, '-y', YN, a, b, z=3.9, rows=3, frame='walnut')
    # the aisle down the middle: a strip of marble
    R.nocol.add(box(14.9, T, 0, 17.1, 23.0, 0.01, 'terrazzo', skip=('-z',)))


def board(R):
    """The blackboard: a walnut-framed board standing just off the wall, covered in chalk."""
    g = Geo()
    g.add(box(BX0, BY0, BZ0, BX1, BY1, BZ1, 'walnut', sides='walnut'))
    R.parts.add(g)
    # the board's face and frame
    bz0 = 1.05
    R.nocol.add(panel_y(BY0 - 0.005, BX0 + 0.25, BX1 - 0.25, bz0, BZ1 - 0.25, 'blackboard', face=-1))
    fr = Geo()
    fr.add(box(BX0, BY0 - 0.08, bz0 - 0.12, BX1, BY0, bz0, 'walnut'))
    fr.add(box(BX0, BY0 - 0.2, bz0 - 0.08, BX1, BY0, bz0 - 0.03, 'oak'))
    fr.add(box(BX0, BY0 - 0.08, BZ1 - 0.25, BX1, BY0, BZ1, 'walnut'))
    fr.add(box(BX0, BY0 - 0.08, bz0 - 0.12, BX0 + 0.25, BY0, BZ1, 'walnut'))
    fr.add(box(BX1 - 0.25, BY0 - 0.08, bz0 - 0.12, BX1, BY0, BZ1, 'walnut'))
    fr.add(box(BX0 - 0.1, BY0 - 0.1, BZ1, BX1 + 0.1, BY1 + 0.02, BZ1 + 0.2, 'walnut'))
    R.parts.add(fr)
    # chalk: the lesson
    rs = rng(12)
    y = BY0 - 0.012
    ch = Geo()

    def stroke(x0, z0, x1, z1, w=0.025):
        L = math.hypot(x1 - x0, z1 - z0)
        if L < 1e-3: return
        nx, nz = -(z1 - z0) / L * w / 2, (x1 - x0) / L * w / 2
        P = [(x0 - nx, y, z0 - nz), (x1 - nx, y, z1 - nz), (x1 + nx, y, z1 + nz), (x0 + nx, y, z0 + nz)]
        q = quad(P, 'chalk', [(p[0], p[2]) for p in P])
        # face -y
        A = [P[1][i] - P[0][i] for i in range(3)]; B = [P[2][i] - P[0][i] for i in range(3)]
        if (A[2] * B[0] - A[0] * B[2]) > 0: q.f = [tuple(reversed(f)) for f in q.f]
        ch.add(q)

    def circle(cx, cz, r, n=20, a0=0.0, a1=2 * math.pi):
        pts = [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cz + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
        for p, q in zip(pts, pts[1:]): stroke(p[0], p[1], q[0], q[1])

    # a spiral galaxy, top middle
    gx, gz = 15.6, 5.3
    for arm in range(2):
        pts = []
        for k in range(40):
            t = k / 39
            a = arm * math.pi + t * 3.2 * math.pi
            r = 0.08 + 1.1 * t
            pts.append((gx + r * math.cos(a) * 1.3, gz + r * math.sin(a) * 0.55))
        for p, q in zip(pts, pts[1:]): stroke(p[0], p[1], q[0], q[1], 0.03)
    circle(gx, gz, 0.12, 10)
    # circles and a triangle, a square, bottom right
    for (cx, cz, r) in ((18.6, 2.3, 0.55), (19.9, 2.3, 0.55), (19.25, 3.3, 0.55), (13.0, 2.2, 0.7)):
        circle(cx, cz, r, 22)
    for (p, q) in (((12.3, 1.7), (13.7, 1.7)), ((13.7, 1.7), (13.0, 2.9)), ((13.0, 2.9), (12.3, 1.7))):
        stroke(p[0], p[1], q[0], q[1])
    for (p, q) in (((16.2, 1.5), (17.2, 1.5)), ((17.2, 1.5), (17.2, 2.5)), ((17.2, 2.5), (16.2, 2.5)), ((16.2, 2.5), (16.2, 1.5)), ((16.2, 1.5), (17.2, 2.5))):
        stroke(p[0], p[1], q[0], q[1])
    circle(20.2, 5.3, 0.7, 24); stroke(19.5, 5.3, 20.9, 5.3); stroke(20.2, 4.6, 20.2, 6.0)
    # lines of working: rows of dashes (words), left side and along the bottom
    for (x0, x1, z0, z1) in ((10.8, 14.2, 3.6, 6.4), (10.8, 12.0, 1.3, 3.4), (14.3, 16.0, 1.3, 1.1 + 0.9), (17.4, 21.0, 4.1, 4.4)):
        z = z1
        while z > z0:
            x = x0 + rs.uniform(0, 0.2)
            while x < x1:
                L = rs.uniform(0.06, 0.32)
                if x + L > x1: break
                wob = rs.uniform(-0.02, 0.02)
                stroke(x, z + wob, x + L, z + wob + rs.uniform(-0.02, 0.02), 0.018)
                if rs.random() < 0.25: stroke(x + L * 0.5, z - 0.05, x + L * 0.5, z + 0.06, 0.016)
                x += L + rs.uniform(0.05, 0.14)
            z -= rs.uniform(0.16, 0.22)
    R.nocol.add(ch)
    # chalk and a duster on the ledge
    R.nocol.add(box(13.0, BY0 - 0.18, bz0 - 0.03, 13.3, BY0 - 0.08, bz0 + 0.04, 'oak'))
    for k in range(3):
        R.nocol.add(box(14.0 + k * 0.2, BY0 - 0.16, bz0 - 0.03, 14.09 + k * 0.2, BY0 - 0.14, bz0 - 0.01, 'chalk'))
    # the door behind it, and a bulb over the gap
    R.cut(box(DX0, YN - 0.1, 0, DX1, SY0 + 0.05, 2.2, 'wood', bottom='floor', top='wood'))
    R.nocol.add(box(DX0 - 0.1, YN - 0.06, 2.2, DX1 + 0.1, YN, 2.32, 'walnut'))
    R.light(sphere(19.0, (BY1 + YN) / 2, 3.2, 0.05, 6, 3, 'e_dim'))


def desk_unit(g, x0, x1, y, rs, lamps):
    """A long desk for four, its front edge at y (the sitters face +y, the board)."""
    d = 0.62
    g.add(box(x0, y, 0.72, x1, y + d, 0.77, 'oak', sides='walnut'))
    for x in (x0 + 0.03, x1 - 0.06):
        g.add(box(x, y + 0.05, 0.0, x + 0.03, y + d - 0.02, 0.72, 'walnut', skip=('-z', '+z')))
    g.add(box(x0 + 0.06, y + d - 0.04, 0.3, x1 - 0.06, y + d - 0.02, 0.72, 'walnut', skip=('-z', '+z')))
    g.add(box(x0 + 0.06, y + 0.06, 0.55, x1 - 0.06, y + d - 0.05, 0.58, 'walnut', skip=('-z',)))
    n = 4
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n
        pushed = rs.uniform(0.0, 0.25) if rs.random() < 0.3 else 0.0
        g.add(lchair(x + rs.uniform(-0.05, 0.05), y - 0.22 - pushed, math.pi / 2 + rs.uniform(-0.1, 0.1), frame='oak', seat='oak', back_h=0.9))
        r = rs.random()
        if r < 0.3:
            g.add(box(x - 0.12, y + 0.15, 0.77, x + 0.12, y + 0.42, 0.8 + rs.uniform(0, 0.05), rs.choice(BOOKM)).xform(0, 0, 0, 0))
        elif r < 0.4:
            g.add(box(x - 0.1, y + 0.1, 0.77, x + 0.12, y + 0.4, 0.772, 'ivory'))
    return [(x0 + (x1 - x0) * (k + 0.5) / 2, y + d - 0.14) for k in range(2)] if lamps else []


def desks(R):
    rs = rng(8)
    g = Geo()
    lamps = []
    y = 3.2
    while y < 21.8:
        for (a, b) in ((3.0, 14.6), (17.4, 30.2)):
            n = 3
            for k in range(n):
                x0 = a + (b - a) * k / n + 0.05
                x1 = a + (b - a) * (k + 1) / n - 0.05
                for p in desk_unit(g, x0, x1, y, rs, rs.random() < 0.6):
                    lamps.append(p)
            # one invisible block for the row's desks and chairs, so nobody drops into the gaps between them
            R.col.add(box(a, y - 0.5, 0, b, y + 0.62, 0.77, 'tile'))
        y += 1.55
    R.nocol.add(g)
    for k, (x, yy) in enumerate(lamps):
        llamp(R, x, yy, 0.77, 0.0, lit=(rs.random() < 0.12), m='e_lamp')
    for (x, y) in ((6.0, 2.98), (20.0, 8.48)):
        R.spot('sit', x, y, 0.48, math.pi / 2)


def dais(R):
    x0, x1, y0, y1 = 11.2, 20.8, 23.4, 26.3
    R.parts.add(box(x0, y0, 0, x1, y1, 0.3, 'oak', sides='walnut', skip=('-z',)))
    R.parts.add(box(12.6, 24.9, 0.3, 15.4, 25.8, 1.08, 'walnut', top='leather'))
    R.parts.add(lchair_legs(14.0, 26.05, -math.pi / 2).xform(0, 0, 0, 0.3))
    R.spot('sit', 14.0, 26.05, 0.78, -math.pi / 2)
    llamp(R, 12.95, 25.35, 1.08, 0.0, lit=True, m='e_lamp')
    R.nocol.add(cyl(15.1, 25.3, 1.08, 1.12, 0.05, 8, side='brass', top='brass'))
    R.nocol.add(sphere(15.1, 25.3, 1.14, 0.04, 6, 3, 'brass', lower=False))
    R.nocol.add(blob(13.8, 25.2, 1.13, 0.05, 0.05, 0.05, 8, 4, 'fruit'))
    for k in range(9):
        R.nocol.add(box(14.2, 25.0, 1.08 + k * 0.012, 14.5, 25.4, 1.09 + k * 0.012, 'ivory').xform(0, 0, 0, 0))
    # a globe on a stand
    R.parts.add(cyl(18.8, 25.0, 0.3, 1.0, 0.04, 8, side='walnut', caps=False))
    R.parts.add(cyl(18.8, 25.0, 0.3, 0.36, 0.3, 12, side='walnut', top='walnut'))
    R.nocol.add(sphere(18.8, 25.0, 1.3, 0.32, 14, 7, 'green'))
    R.nocol.add(ring(18.8, 25.0, 1.28, 1.32, 0.34, 0.37, 20, top='brass', bottom='brass', inner='brass', outer='brass'))


def store(R):
    R.cut(box(SX0, SY0, 0, SX1, SY1, SH, 'plaster', bottom='floor', top='plaster'))
    # shelves of chalk boxes, slates and rolled maps; a desk with the register
    sh(R, '-y', SY1, SX0 + 0.3, SX1 - 0.3, rows=6, frame='oak', depth=0.4)
    rs = rng(6)
    g = Geo()
    for k in range(18):
        x = rs.uniform(SX0 + 0.5, SX1 - 0.5)
        z = rs.choice((0.04, 0.46, 0.88, 1.3, 1.72, 2.14)) + 0.035
        g.add(box(x - 0.15, SY1 - 0.4, z, x + 0.15, SY1 - 0.05, z + 0.2, rs.choice(('ivory', 'chalk', 'oak'))))
    for k in range(7):
        x = SX0 + 0.3 + k * 0.12
        g.add(cyl(x, SY0 + 0.35, 0.0, 1.1 + rs.uniform(0, 0.5), 0.05, 6, side=rs.choice(('ivory', 'plaster', 'bed')), top='oak'))
    R.nocol.add(g)
    R.parts.add(ltable(SX1 - 2.4, SY0 + 0.25, SX1 - 0.4, SY0 + 1.0, 0.78, 'walnut', top='leather'))
    ob = box(-0.24, -0.17, 0, 0.0, 0.17, 0.03, 'ivory', sides='leather'); ob.add(box(0.0, -0.17, 0, 0.24, 0.17, 0.03, 'ivory', sides='leather'))
    R.nocol.add(ob.xform(0.0, SX1 - 1.4, SY0 + 0.6, 0.78))
    R.nocol.add(blob(SX1 - 0.8, SY0 + 0.5, 0.83, 0.05, 0.05, 0.05, 8, 4, 'fruit'))
    llamp(R, SX1 - 2.1, SY0 + 0.75, 0.78, 0.0, lit=True, m='e_amber')
    R.parts.add(lchair_legs(SX1 - 1.4, SY0 + 1.45, -math.pi / 2))
    R.spot('sit', SX1 - 1.4, SY0 + 1.45, 0.48, -math.pi / 2)
    R.nocol.add(sphere(SX0 + 1.4, SY1 - 0.9, 0.35, 0.33, 12, 6, 'green'))
    R.nocol.add(cone(SX0 + 2.2, SY0 + 0.5, 0.0, 0.7, 0.2, 0.01, 8, 'ivory'))
    bulb(R, (SX0 + SX1) / 2, (SY0 + SY1) / 2, SH - 0.6, r=0.09, m='e_dim', top=SH)
    R.spot('plaque', SX1 - 1.4, SY0 + 0.6, 0.8, math.pi / 2, text='REGISTER. Present. Present. Present. Present.')
    a, b = R.navpt(SX0 + 1.0, SY0 + 1.6), R.navpt(SX1 - 2.8, SY0 + 1.9)
    R.link(a, b)
