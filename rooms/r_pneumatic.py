"""The Pneumatic Exchange: brass tubes in every direction, up the walls, across the ceiling, down to
desks, with glass sections where you can see the books inside and capsules shooting through. One tube
lying on the floor is big enough to walk into. It goes into the north wall, to the office where
everything was going."""
from kit_h6 import *

W = D = 32.0
YN = 25.4                        # the hall's north wall; the office is in the thickness behind it
BT = (16.0, 15.2, YN + 0.95)     # the big tube: x, mouth y, far end y (in the office)
BTR = 1.35                       # its radius
BTZ = 1.45                       # its axis height
BTF = 0.5                        # its floor
OF = (10.6, YN + 0.9, 21.4, D - 0.5)   # the office (x0, y0, x1, y1)
OH = 3.3


def make():
    R = Room('pneumatic', 2, 2, res=2048)
    hall(R, y1=YN, h=TOP - 0.1, wall='tile', floor='terrazzo', ceil='plaster')
    rs = rng(51)
    walls(R)
    big_tube(R, rs)
    office(R, rs)
    tubes(R, rs)
    stations(R, rs)
    lamps(R)
    fx(R, 'fog', [T, T, 0, W - T, YN, TOP], density=0.025)
    fx(R, 'dust', [T, T, 0.5, W - T, YN, 7.0])
    p = navloop(R, [(13.4, 24.2), (2.2, 24.2), (2.2, 13.0), (2.2, 2.2), (16, 2.2), (29.8, 2.2), (29.8, 13.0), (29.8, 24.2), (18.6, 24.2)], close=False)
    a = R.navpt(8, 13.0); b = R.navpt(24, 13.0); c = R.navpt(16, 10.0); m = R.navpt(16, 13.8)
    R.link(p[2], a, c, b, p[6]); R.link(c, m)
    return finish(R, 'The Pneumatic Exchange', weight=3, probe=(16, 9.0, 2.6),
                  blurb='Brass tubes run everywhere, and every so often something goes through one with a sigh. You never see where anything is sent.')


def walls(R):
    rows = 15
    for (a, b) in ((0.7, 6.3), (9.7, 22.3)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    sh(R, '+x', T, 25.7, YN - 0.1, rows=rows, frame='walnut')
    sh(R, '-x', W - T, 25.7, YN - 0.1, rows=rows, frame='walnut')
    for (a, b) in ((0.7, 6.3), (9.7, 22.3), (25.7, W - 0.7)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.7, 6.3), (9.7, BT[0] - BTR - 0.5), (BT[0] + BTR + 0.5, 22.3), (25.7, W - 0.7)):
        sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
    for c in (8.0, 24.0):
        sh(R, '+y', T, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
        sh(R, '-y', YN, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
        sh(R, '+x', T, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
        sh(R, '-x', W - T, c - 1.7, c + 1.7, z=4.3, rows=7, frame='walnut')
    # the long passages to the north doorways, through the thick wall: books along them
    for c in (8.0, 24.0):
        R.nocol.add(box(c - 1.55, YN, 0, c - 1.5, D - T, 2.6, 'walnut'))


def tube_shell(p0, p1, r, m='brass', inner='iron', segs=24, t=0.06):
    """A big open tube you can see into (and walk inside): outer and inner skins, no caps."""
    L = math.dist(p0, p1)
    g = cyl(0, 0, 0, L, r, segs, side=m, caps=False)
    gi = cyl(0, 0, 0, L, r - t, segs, side=inner, caps=False)
    gi.f = [tuple(reversed(f)) for f in gi.f]; gi.uv = [list(reversed(u)) for u in gi.uv]
    g.add(gi)
    rot(g, 'y', math.pi / 2)
    return along(g, p0, p1)


def flange(x, y, z, r, axis='y', w=0.12, m='brass', segs=24):
    g = ring(0, 0, -w / 2, w / 2, r - 0.02, r + 0.1, segs, top=m, bottom=m, inner=m, outer=m)
    if axis == 'y': rot(g, 'x', math.pi / 2)
    elif axis == 'x': rot(g, 'y', math.pi / 2)
    g.v = [(a + x, b + y, c + z) for a, b, c in g.v]
    return g


def big_tube(R, rs):
    """The walk-in tube: lying on cradles from the middle of the hall into the north wall, a glass
    section half way along, a hatch standing open at its mouth."""
    x, y0, y1 = BT
    yg0, yg1 = 18.4, 21.2            # the glass section
    for (a, b) in ((y0, yg0), (yg1, y1)):
        R.nocol.add(tube_shell((x, a, BTZ), (x, b, BTZ), BTR))
    R.nocol.add(cage_tube((x, yg0, BTZ), (x, yg1, BTZ), BTR, 'brass', ribs=14, hoops=4, segs=24))
    for y in (y0, yg0, yg1, YN - 0.05):
        R.nocol.add(flange(x, y, BTZ, BTR))
    # cradles under it
    for y in (y0 + 1.0, 20.0 + 0.0, YN - 1.2):
        R.parts.add(box(x - 1.2, y - 0.2, 0, x + 1.2, y + 0.2, 0.35, 'iron', skip=('-z',)))
    # inside: a plank floor, invisible walls where the round sides are too low to stand under
    R.parts.add(box(x - 0.9, y0, 0.1, x + 0.9, y1, BTF, 'oak', sides='walnut'))
    for s in (-1, 1):
        R.col.add(box(x + s * 0.95 - 0.05, y0, BTF, x + s * 0.95 + 0.05, y1, BTZ + BTR, 'tile'))
    R.col.add(box(x - 1.0, y0, BTZ + BTR - 0.05, x + 1.0, y1, BTZ + BTR + 0.05, 'tile'))
    # a step up into the mouth, and the hatch hanging open on its hinge
    R.parts.add(box(x - 0.8, y0 - 0.55, 0, x + 0.8, y0, 0.25, 'brass', top='oak'))
    hatch = cyl(0, 0, -0.04, 0.04, BTR + 0.05, 24, side='brass', top='brass', bottom='brass')
    rot(hatch, 'x', math.pi / 2)
    hatch.v = [(a + BTR + 0.05, b, c) for a, b, c in hatch.v]
    hatch.xform(-2.1, x - BTR - 0.05, y0 - 0.05, BTZ)
    R.nocol.add(hatch)
    R.nocol.add(box(x - BTR - 0.18, y0 - 0.1, BTZ - 0.3, x - BTR - 0.02, y0 + 0.05, BTZ + 0.3, 'iron'))
    R.nocol.add(wheel(x - BTR + 0.5 - 1.4, y0 - 1.25, BTZ, 0.3, axis='y', spokes=4, rim=0.04, w=0.05, m='iron'))
    # a hole through the wall for it, and a trolley of books inside the glass
    R.cut(prism([(x - 0.95, BTF), (x + 0.95, BTF), (x + 0.95, BTZ + 0.7), (x, BTZ + BTR - 0.02), (x - 0.95, BTZ + 0.7)], 'y', YN - 0.1, OF[1] + 0.1,
                ['oak', 'brass', 'brass', 'brass', 'brass'], cap='brass'))
    R.parts.add(box(x + 0.35, 19.3, BTF, x + 0.9, 20.3, BTF + 0.75, 'walnut'))
    for k in range(3):
        book_pile(R, x + 0.62, 19.5 + k * 0.3, BTF + 0.75, n=rs.randint(3, 6), seed=40 + k, col=False)
    for y in (17.0, 23.5):
        R.light(sphere(x, y, BTZ + BTR - 0.25, 0.06, 8, 4, 'e_dim'))


def office(R, rs):
    """The sorting office at the end of the tube: pigeonholes to the ceiling, a desk under a green
    lamp, capsules waiting in racks, and the tubes from the hall all arriving here."""
    x0, y0, x1, y1 = OF
    R.cut(box(x0, y0, 0, x1, y1, OH, 'damask', bottom='floor', top='plaster'))
    # pigeonholes on the back wall and the side walls
    sh(R, '-y', y1, x0 + 0.2, x1 - 0.2, rows=7, frame='oak', row_h=0.4, depth=0.3)
    for k in range(1, 12):
        x = x0 + 0.2 + (x1 - x0 - 0.4) * k / 12
        R.nocol.add(box(x - 0.015, y1 - 0.3, 0, x + 0.015, y1, 7 * 0.4 + 0.1, 'oak'))
    sh(R, '+x', x0, y0 + 0.3, y1 - 0.4, rows=7, frame='oak', row_h=0.4, depth=0.3)
    sh(R, '-x', x1, y0 + 0.3, y1 - 0.4, rows=7, frame='oak', row_h=0.4, depth=0.3)
    # the desk and its lamp, stamps, a ledger
    R.parts.add(desk(13.2, 29.0, math.pi / 2 + math.pi, w=1.6, d=0.8))
    R.parts.add(stool(13.2, 29.75, -math.pi / 2))
    R.spot('sit', 13.2, 29.75, 0.47, -math.pi / 2)
    desk_lamp(R, 12.7, 28.85, 0.76)
    open_book(R, 13.4, 29.05, 0.76, 0.1)
    for k in range(4):
        R.nocol.add(cyl(13.9 + k * 0.1, 28.8, 0.76, 0.84, 0.025, 6, side='walnut', top='walnut'))
    # capsule racks, and the tubes coming down through the ceiling onto a sorting table
    for k in range(6):
        cx = 17.4 + k * 0.5
        R.nocol.add(solid_tube((cx, y0 + 0.2, OH - 0.05), (cx, y0 + 0.2, 1.2), 0.1, 'brass', 12))
        R.nocol.add(frustum(cx, y0 + 0.2, 1.0, 1.2, 0.16, 0.1, 10, 'brass', inner='iron'))
    R.parts.add(table(17.0, y0 + 0.05, 20.4, y0 + 0.75, 0.9, 'walnut', top='leather'))
    for k in range(9):
        cx, cy = 17.3 + (k % 5) * 0.62, y0 + 0.3 + (k // 5) * 0.25
        R.nocol.add(solid_tube((cx - 0.12, cy, 0.95), (cx + 0.12, cy, 0.95), 0.045, 'brass', 8))
    R.parts.add(box(19.2, 29.6, 0, 21.2, 30.8, 0.9, 'walnut', top='leather'))
    for k in range(14):
        cx, cy = 19.4 + (k % 7) * 0.26, 29.8 + (k // 7) * 0.6
        R.nocol.add(solid_tube((cx, cy - 0.15, 1.0), (cx, cy + 0.15, 1.0), 0.05, 'brass', 8))
    R.light(box(15.4, 29.0, OH - 0.04, 16.6, 30.2, OH - 0.02, 'e_panel'))
    R.light(sphere(x1 - 0.5, y0 + 0.5, 2.2, 0.06, 8, 4, 'e_amber'))
    R.spot('plaque', 13.2, 28.9, 0.76, -math.pi / 2,
           text='Every request for every book arrives here, in a capsule. Most ask for a book that would explain everything. We send them all the same reply: it is on a shelf, somewhere.')
    secret(R, 15.0, 28.5, 0.0, 'The Sorting Office',
           'At the end of the big tube, a little office where every capsule in the library ends up, pigeonholed and answered. The last reply was written today.')


def v_tube(R, x, y, r, rs, z0=0.0, z1=TOP - 0.1, glass=None, books=True):
    """A vertical tube floor to ceiling, collided at the bottom; a glass section with books stacked inside."""
    if glass is None: glass = (rs.uniform(1.0, 2.2), rs.uniform(3.2, 4.8))
    ga, gb = glass
    R.parts.add(cyl(x, y, z0, z0 + 0.3, r + 0.14, 16, side='brass', top='brass'))
    R.col.add(box(x - r, y - r, z0, x + r, y + r, 2.4, 'tile'))
    R.nocol.add(cyl(x, y, z0 + 0.3, ga, r, 16, side='brass', caps=False))
    R.nocol.add(cage_tube((x, y, ga), (x, y, gb), r, 'brass', ribs=8, hoops=3, segs=16))
    R.nocol.add(cyl(x, y, gb, z1, r, 16, side='brass', caps=False))
    for z in (ga, gb, z1 - 0.2):
        R.nocol.add(ring(x, y, z - 0.05, z + 0.05, r - 0.01, r + 0.07, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
    if books:
        zz = ga
        while zz < gb - 0.3:
            h = rs.uniform(0.22, 0.34)
            b = box(-r * 0.55, -0.05, 0, r * 0.55, 0.05, h, rs.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet')))
            R.nocol.add(b.xform(rs.uniform(0, 3), x, y, zz)); zz += h * rs.uniform(0.3, 0.5) + 0.02


def h_tube(R, p0, p1, r, rs, glass=(0.35, 0.65), capsule=True, books=True):
    """A horizontal (or sloping) tube with a glass stretch; a capsule shoots to and fro inside it."""
    L = math.dist(p0, p1)
    lerp = lambda t: tuple(p0[i] + (p1[i] - p0[i]) * t for i in range(3))
    ga, gb = lerp(glass[0]), lerp(glass[1])
    R.nocol.add(solid_tube(p0, ga, r, 'brass', 14, caps=False))
    R.nocol.add(cage_tube(ga, gb, r, 'brass', ribs=8, hoops=3, segs=14))
    R.nocol.add(solid_tube(gb, p1, r, 'brass', 14, caps=False))
    for p in (ga, gb):
        R.nocol.add(solid_tube(tuple(p[i] - (p1[i] - p0[i]) / L * 0.05 for i in range(3)), tuple(p[i] + (p1[i] - p0[i]) / L * 0.05 for i in range(3)), r + 0.06, 'brass', 14))
    d = tuple((gb[i] - ga[i]) for i in range(3))
    if books:
        n = int(math.dist(ga, gb) / 0.5)
        for k in range(n):
            t = (k + 0.5) / n
            c = tuple(ga[i] + d[i] * t for i in range(3))
            b = box(-0.1, -r * 0.45, -r * 0.45, 0.1, r * 0.45, r * 0.3, rs.choice(('oxblood', 'green', 'leather', 'walnut')))
            R.nocol.add(along(b, c, tuple(c[i] + d[i] * 0.01 for i in range(3))))
    if capsule:
        M = R.mover('slide', delta=tuple(round(-(p1[i] - p0[i]) * 0.8, 3) for i in range(3)), period=rs.uniform(3.0, 5.0), pause=rs.uniform(1.5, 4.0), phase=rs.random())
        c0 = lerp(0.9)
        cap = solid_tube(c0, tuple(c0[i] + (p1[i] - p0[i]) / L * 0.45 for i in range(3)), r * 0.8, 'chrome', 10)
        M.nocol.add(cap)


def elbow(R, p0, p1, bend, r, segs=12):
    R.nocol.add(tube(curve(p0, p1, bend, 7), r, segs, 'brass', caps=False))


def tubes(R, rs):
    """The tubes: vertical ones standing about the hall, horizontal ones crossing overhead and running
    along the walls, elbows turning them down into the vertical ones and into the walls."""
    vs = [(5.0, 11.5, 0.45), (11.0, 6.5, 0.55), (21.0, 6.5, 0.4), (27.0, 11.5, 0.6), (5.5, 19.5, 0.35), (26.5, 19.5, 0.5),
          (11.5, 13.0, 0.3), (20.5, 13.0, 0.35), (12.2, 21.0, 0.45), (19.8, 21.0, 0.4)]
    for (x, y, r) in vs:
        v_tube(R, x, y, r, rs)
    # overhead: tubes linking the vertical ones at different heights
    links = [((5.0, 11.5), (11.0, 6.5), 5.2, 0.28), ((11.0, 6.5), (21.0, 6.5), 6.3, 0.4), ((21.0, 6.5), (27.0, 11.5), 4.8, 0.3),
             ((27.0, 11.5), (26.5, 19.5), 6.0, 0.35), ((5.0, 11.5), (5.5, 19.5), 3.6, 0.25), ((11.5, 13.0), (20.5, 13.0), 4.4, 0.22),
             ((12.2, 21.0), (19.8, 21.0), 5.6, 0.3), ((5.5, 19.5), (12.2, 21.0), 6.6, 0.25), ((26.5, 19.5), (19.8, 21.0), 3.9, 0.28),
             ((11.0, 6.5), (11.5, 13.0), 3.2, 0.2), ((21.0, 6.5), (20.5, 13.0), 6.9, 0.2)]
    for (a, b, z, r) in links:
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        # a stub out of each vertical tube, then the run
        p0 = (a[0] + ux * 0.7, a[1] + uy * 0.7, z); p1 = (b[0] - ux * 0.7, b[1] - uy * 0.7, z)
        R.nocol.add(solid_tube((a[0], a[1], z), p0, r, 'brass', 12, caps=False))
        R.nocol.add(solid_tube(p1, (b[0], b[1], z), r, 'brass', 12, caps=False))
        h_tube(R, p0, p1, r, rs, glass=(rs.uniform(0.15, 0.35), rs.uniform(0.6, 0.85)))
    # long runs along the walls under the ceiling, and a few diving into the walls
    for (p0, p1, r) in (((T + 0.6, 2.0, 6.8), (T + 0.6, YN - 1.0, 6.8), 0.3), ((W - T - 0.6, 2.0, 6.4), (W - T - 0.6, YN - 1.0, 6.4), 0.35),
                        ((2.0, T + 0.6, 7.0), (W - 2.0, T + 0.6, 7.0), 0.28), ((2.0, YN - 0.6, 6.6), (W - 2.0, YN - 0.6, 6.6), 0.32)):
        h_tube(R, p0, p1, r, rs, glass=(0.4, 0.6))
    for (x, y, r, z) in ((5.0, 11.5, 0.3, 6.8), (27.0, 11.5, 0.35, 6.4), (11.0, 6.5, 0.28, 7.0), (19.8, 21.0, 0.32, 6.6)):
        # elbows from the vertical tubes to the wall runs
        if y < 10: tgt = (x, T + 0.6, z)
        elif y > 20: tgt = (x, YN - 0.6, z)
        elif x < 16: tgt = (T + 0.6, y, z)
        else: tgt = (W - T - 0.6, y, z)
        R.nocol.add(solid_tube((x, y, z), tgt, r * 0.8, 'brass', 10, caps=False))
    # a sloping tube from high on the west wall down to a station, and one from the ceiling into the big tube
    elbow(R, (T + 0.6, 16.0, 6.0), (7.5, 16.0, 1.5), (2.0, 0, 2.0), 0.22)
    elbow(R, (W - T - 0.6, 16.0, 6.2), (24.5, 16.0, 1.5), (-2.0, 0, 2.0), 0.22)
    R.nocol.add(solid_tube((BT[0], 23.0, TOP - 0.1), (BT[0], 23.0, BTZ + BTR - 0.05), 0.4, 'brass', 14, caps=False))
    # manifold chests with dials where the tubes meet the floor
    for (x, y) in ((11.0, 6.5), (27.0, 11.5), (12.2, 21.0)):
        R.parts.add(box(x - 0.9, y - 0.6, 0, x - 0.4, y + 0.6, 1.3, 'iron', top='brass'))


def stations(R, rs):
    """Sending desks: a tube drops to each, a capsule waiting in a brass cup."""
    for (x, y, a) in ((7.5, 16.0, 0.0), (24.5, 16.0, math.pi), (16.0, 4.2, math.pi / 2), (11.5, 23.0, -math.pi / 2), (20.5, 23.0, -math.pi / 2)):
        R.parts.add(desk(x, y, a, w=1.2, d=0.7))
        R.parts.add(stool(x - math.cos(a) * 0.7, y - math.sin(a) * 0.7, a))
        R.nocol.add(frustum(x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 0.9, 1.5, 0.2, 0.14, 12, 'brass', inner='iron'))
        R.nocol.add(solid_tube((x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 1.5), (x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 1.6), 0.14, 'brass', 10))
        R.nocol.add(solid_tube((x - 0.2, y + 0.3, 0.8), (x + 0.2, y + 0.3, 0.8), 0.05, 'chrome', 8).xform(0, 0, 0, 0))
        if abs(y - 16) > 1: R.nocol.add(cyl(x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 1.6, TOP - 0.1, 0.14, 10, side='brass', caps=False))
        desk_lamp(R, x - math.sin(a) * 0.4, y + math.cos(a) * 0.4, 0.76)


def lamps(R):
    for (x, y) in ((8.0, 9.5), (24.0, 9.5), (16.0, 12.0), (8.0, 17.5), (24.0, 17.5), (16.0, 2.5), (3.0, 23.0), (29.0, 23.0)):
        pendant(R, x, y, 3.4, TOP - 0.1, r=0.22)
    for (x, y) in ((2.2, 2.2), (29.8, 2.2), (2.2, YN - 1.8), (29.8, YN - 1.8)):
        R.light(sphere(x, y, 2.3, 0.08, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, y, 2.35, TOP - 0.1, 0.01, 4, side='iron', caps=False))
