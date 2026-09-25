"""The Hall of Clocks: every wall is clocks, floor to ceiling, none of them agreeing. Longcase clocks
stand at the ends of the stacks; down the middle, reading tables, and at the end of the carpet the
tallest clock in the library, its trunk door not quite shut."""
from kit_h5 import *

W = D = 2 * C
H = TOP - 0.1
YN = 29.6                     # the hall's north wall; the passage runs inside it
GX0, GX1 = 15.0, 17.0         # the great clock
GD = 1.15                     # its depth
GH = H - 0.15
DX0, DX1 = 15.35, 16.65       # its trunk door
DH = 2.3
SY0, SY1 = 30.1, 31.3         # the stair behind the wall, going down east
NS, SR, SU = 18, 0.2, 0.28
SX0 = DX1 - 0.05
SX1 = SX0 + NS * SU
CZ = -NS * SR                 # the works: the chamber under the floor
WX0, WX1, WY0, WY1 = 11.0, SX1 + 1.4, 21.0, 29.4


def make():
    R = Room('clockroom2', 2, 2, res=2048, lo=-4.0)
    rng = random.Random(43)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, YN, H, 'damask', bottom='terrazzo', top='plaster'))
    pr = arch_profile(0, DW, 0, DJ)
    for x in (8.0, 24.0):
        R.cut(prism([(p + x, q) for p, q in pr], 'y', YN - 0.05, D - T + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
    # coffers
    for k in range(1, 8):
        R.nocol.add(box(T, k * 3.7 - 0.1, H - 0.3, W - T, k * 3.7 + 0.1, H, 'walnut', bottom='gilt'))
    # the stacks: double-sided cases running in from the side walls, clocks on their tops, a longcase
    # clock at each end
    stacks = []
    for yc in (3.2, 12.4, 16.0, 19.6, 27.4):
        for (x0, x1, end, a) in ((T + 0.02, 5.4, 5.4, 0.0), (26.6, W - T - 0.02, 26.6, math.pi)):
            sh(R, '+y', yc + 0.01, x0, x1, rows=10, frame='walnut')
            sh(R, '-y', yc - 0.01, x0, x1, rows=10, frame='walnut')
            stacks.append((x0, x1, yc))
            grandfather(R, end + (0.02 if a == 0 else -0.02), yc, a, rng.uniform(2.3, 2.9), rng)
            for k in range(int((x1 - x0) / 0.9)):
                x = x0 + 0.45 + k * 0.9
                mantel(R, x, yc, 4.38, rng)
    # every wall: clocks
    walls(R, rng, stacks)
    # tables down the middle, a carpet to the great clock
    R.nocol.add(box(15.1, 1.2, 0, 16.9, YN - GD - 0.1, 0.012, 'carpet'))
    for s in (-1, 1):
        R.nocol.add(box(16 + s * 0.9 - 0.04, 1.2, 0, 16 + s * 0.9 + 0.04, YN - GD - 0.1, 0.014, 'gilt'))
    for y in (3.4, 11.6, 14.8, 18.0, 21.2):
        for xc in (12.6, 19.4):
            R.parts.add(table(xc - 1.4, y - 0.5, xc + 1.4, y + 0.5, 0.78, 'walnut', top='leather'))
            for dx in (-0.7, 0.7):
                desk_lamp(R, xc + dx, y, 0.78)
                for s in (-1, 1):
                    R.parts.add(chair(xc + dx, y + s * 0.85, -s * math.pi / 2))
                    R.spot('sit', xc + dx, y + s * 0.85, 0.48, -s * math.pi / 2)
            clock(R, xc, y + 0.1, 0.95, 0.09, -math.pi / 2, rng, style='case')
    # chandeliers down the aisles, amber sconces for the night
    for (x, y) in ((8, 8), (24, 8), (8, 24), (24, 24), (16, 8), (16, 17)):
        R.nocol.add(cyl(x, y, 5.6, H - 0.3, 0.012, 4, side='brass', caps=False))
        R.nocol.add(ring(x, y, 5.5, 5.6, 0.5, 0.62, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
        for k in range(6):
            a = 2 * math.pi * k / 6
            R.light(sphere(x + math.cos(a) * 0.56, y + math.sin(a) * 0.56, 5.72, 0.07, 8, 4, 'e_lamp'))
    for (x, y) in ((6.2, 0.9), (9.8, 0.9), (22.2, 0.9), (25.8, 0.9)):
        R.light(sphere(x, y, 2.2, 0.09, 8, 4, 'e_amber'))
        R.nocol.add(box(x - 0.05, T, 2.0, x + 0.05, y, 2.1, 'brass'))
    great_clock(R, rng)
    works(R, rng)
    navloop(R, [(8, 2.5), (8, 8), (8, 16), (8, 24), (8, 27.6), (24, 27.6), (24, 24), (24, 16), (24, 8), (24, 2.5)])
    a = R.navpt(2.5, 8); b = R.navpt(29.5, 8); c = R.navpt(2.5, 24); d = R.navpt(29.5, 24)
    R.link(a, 1); R.link(8, b); R.link(c, 3); R.link(6, d)
    e = R.navpt(16, 8); f = R.navpt(16, 26.5); R.link(1, e, 8); R.link(e, f)
    R.spot('probe', 16, 9.5, 2.2)
    R.meta.update(label='The Hall of Clocks', weight=4,
                  blurb='A thousand clocks and not one of them agrees. You check your wrist out of habit. There is nothing there, and it is also wrong.')
    R.meta['box'] = [[T, 0, T], [W - T, H, YN]]
    # the pendulums swing for real: swing movers (see kit_h5.pendulum)
    return tidy(R)


def mantel(R, x, y, z, rng):
    """A small clock standing on a case top."""
    r = rng.uniform(0.09, 0.15)
    R.nocol.add(box(x - r * 1.2, y - 0.1, z, x + r * 1.2, y + 0.1, z + r * 2.6, 'walnut'))
    for a in (-math.pi / 2, math.pi / 2):
        clock(R, x, y + math.sin(a) * 0.1, z + r * 1.4, r, a, rng, style='round', rim='gilt')


def walls(R, rng, stacks):
    """Clocks over every wall face, dense, all sizes, avoiding doorways and the cases that butt the walls."""
    faces = [('S', T, 0.0, W), ('N', YN, 0.0, W), ('W', T, 0.0, YN), ('E', W - T, 0.0, YN)]
    n = 0
    for (side, c, a0, a1) in faces:
        ang = {'S': math.pi / 2, 'N': -math.pi / 2, 'W': 0.0, 'E': math.pi}[side]
        doors = [8.0, 24.0] if side in 'SN' else [8.0, 24.0]
        z = 0.9
        row = 0
        while z < H - 0.5:
            u = a0 + 0.5 + (0.35 if row % 2 else 0.0)
            while u < a1 - 0.5:
                r = rng.choice((0.12, 0.16, 0.2, 0.25, 0.3))
                ok = True
                for dc in doors:
                    if abs(u - dc) < 2.0 + r and z < 4.4 + r: ok = False
                if side == 'N' and GX0 - 0.6 < u < GX1 + 0.6: ok = False
                if side in 'WE':
                    for (x0, x1, yc) in stacks:
                        if ((side == 'W' and x0 < 1) or (side == 'E' and x1 > W - 1)) and abs(u - yc) < 0.5 + r and z < 4.8 + r: ok = False
                if side == 'N' and z < 3.2 + r and (u < 5.6 or u > 26.4): ok = False
                if ok and rng.random() < 0.9:
                    x, y = (u, c) if side in 'SN' else (c, u)
                    dd = rng.uniform(0.0, 0.09)
                    x, y = x + math.cos(ang) * dd, y + math.sin(ang) * dd
                    zz = z + rng.uniform(-0.08, 0.08)
                    clock(R, x, y, zz, r, ang, rng)
                    n += 1
                u += 2 * r + rng.uniform(0.16, 0.36)
            z += 0.62 + rng.uniform(-0.04, 0.04)
            row += 1
    # longcase clocks along the north wall's corners and the south wall
    for (x, y, a) in ((2.0, YN, -math.pi / 2), (3.2, YN, -math.pi / 2), (4.4, YN, -math.pi / 2), (27.6, YN, -math.pi / 2),
                      (28.8, YN, -math.pi / 2), (30.0, YN, -math.pi / 2), (12.0, T, math.pi / 2), (13.4, T, math.pi / 2),
                      (18.6, T, math.pi / 2), (20.0, T, math.pi / 2)):
        grandfather(R, x, y, a, rng.uniform(2.4, 3.1), rng)
    R.meta['clocks'] = n


def great_clock(R, rng):
    """The tallest clock: a longcase the height of the room against the north wall. Its trunk door is
    ajar, and the trunk has no back."""
    y0, y1 = YN - GD, YN
    # sides, the hood and the head, the base under the door
    R.parts.add(box(GX0, y0, 0, DX0, y1, GH - 1.9, 'walnut'))
    R.parts.add(box(DX1, y0, 0, GX1, y1, GH - 1.9, 'walnut'))
    R.parts.add(box(DX0, y0, DH, DX1, y1, GH - 1.9, 'walnut'))
    R.parts.add(box(GX0 - 0.2, y0 - 0.2, GH - 1.9, GX1 + 0.2, y1, GH, 'walnut', top='gilt'))
    R.parts.add(box(GX0 - 0.1, y0 - 0.1, 0, GX1 + 0.1, y0 + 0.05, 0.2, 'walnut'))
    # the inside of the trunk: dark, and a gap at the back into the wall
    R.nocol.add(box(DX0, y0 + 0.05, DH - 0.02, DX1, y1, DH, 'walnut'))
    R.cut(box(DX0, YN - 0.05, 0, DX1, SY0 + 0.05, DH, 'walnut', bottom='oak'))
    # moulding up the trunk, a glazed window above the door and the pendulum behind it
    for x in (GX0 + 0.08, GX1 - 0.08):
        R.nocol.add(box(x - 0.05, y0 - 0.05, 0.2, x + 0.05, y0, GH - 1.9, 'gilt'))
    R.nocol.add(box(DX0 + 0.1, y0 - 0.02, DH + 0.3, DX1 - 0.1, y0, GH - 2.3, 'black'))
    pg = Geo()
    pg.add(quad_v(16.0, y0 - 0.03, GH - 2.4, -math.pi / 2, (GH - 2.4) - (DH + 1.0), 0.04, -math.pi / 2, 'brass'))
    pg.add(disc_v(16.0, y0 - 0.03, DH + 0.95, 0.3, -math.pi / 2, 16, 'brass', off=0.01))
    M = R.mover('swing', pivot=(16.0, y0 - 0.03, GH - 2.4), axis='y', amp=0.06, period=4.0)
    M.nocol.add(pg)
    # the face
    fz = GH - 0.95
    R.nocol.add(disc_v(16.0, y0 - 0.2, fz, 0.9, -math.pi / 2, 28, 'gilt', off=0.01))
    R.nocol.add(disc_v(16.0, y0 - 0.2, fz, 0.8, -math.pi / 2, 28, 'ivory', off=0.02))
    for k in range(12):
        a = math.pi / 2 - k * math.pi / 6
        R.nocol.add(quad_v(16.0 + math.cos(a) * 0.6, y0 - 0.2, fz + math.sin(a) * 0.6, -math.pi / 2, 0.14, 0.035 if k % 3 else 0.06, a, 'black', off=0.025))
    for (frac, L, w) in ((11.95 / 12, 0.45, 0.06), (57 / 60, 0.7, 0.035)):
        a = math.pi / 2 - 2 * math.pi * frac
        R.nocol.add(quad_v(16.0, y0 - 0.2, fz, -math.pi / 2, L, w, a, 'iron', off=0.035))
    R.light(disc_v(16.0, y0 - 0.2, fz - 0.95 - 0.3, 0.06, -math.pi / 2, 8, 'e_amber', off=0.03))
    # the door, ajar
    door = box(0, -0.04, 0, DX1 - DX0 - 0.02, 0.0, DH - 0.03, 'walnut')
    door.add(box(0.12, -0.05, 0.3, DX1 - DX0 - 0.14, -0.04, DH - 0.3, 'black'))
    door.add(box(DX1 - DX0 - 0.12, -0.09, 1.0, DX1 - DX0 - 0.08, -0.04, 1.12, 'brass'))
    door.xform(-0.5, DX0 + 0.01, y0, 0)
    R.nocol.add(door)
    # behind the wall: a landing, then the stair going down east to the works
    R.cut(box(DX0, SY0, 0, SX0 + 0.02, SY1, DH + 0.2, 'tile', bottom='oak', top='tile'))
    R.cut(box(SX0, SY0, CZ, SX1, SY1, DH + 0.2, 'tile', bottom='slate', top='tile'))
    save = R.nocol; R.nocol = Geo()
    R.flight(SX1, SY0, CZ, SY1 - SY0, NS, SR, SU, '-x', m='oak', riser='walnut', side='tile')
    g = R.nocol; R.nocol = save; R.nocol.add(g)
    R.light(sphere(DX0 + 0.3, SY1 - 0.25, 1.9, 0.06, 8, 4, 'e_candle'))
    for k in range(3):
        x = SX0 + 1.2 + k * 1.6
        z = -(x - SX0) / SU * SR + 2.3
        R.light(sphere(x, SY1 - 0.1, z, 0.06, 8, 4, 'e_amber'))
    for k in range(12):
        clock(R, SX0 + 0.3 + k * 0.42, SY1, 1.0 - k * 0.3 + 0.9, 0.12, -math.pi / 2, rng, style='round')


def works(R, rng):
    """The room under the hall where all the clocks are driven from: brass wheels, a long pendulum,
    a bench with a lamp. One clock down here is right."""
    R.cut(box(WX0, WY0, CZ, WX1, WY1, -0.6, 'tile', bottom='slate', top='slate'))
    R.cut(box(SX1 - 0.3, WY1 - 0.05, CZ, WX1, SY1, -0.6, 'tile', bottom='slate', top='slate'))
    # great wheels standing on edge along the north and south walls, their axles in the walls
    for (x, y, r, a) in ((13.0, WY0 + 0.25, 1.35, math.pi / 2), (16.2, WY0 + 0.25, 1.0, math.pi / 2), (19.4, WY0 + 0.25, 1.3, math.pi / 2),
                         (13.2, WY1 - 0.25, 1.1, -math.pi / 2), (WX0 + 0.25, 25.2, 1.25, 0.0)):
        gear_v(R, x, y, CZ + r + 0.35, r, a, rng)
    # a horizontal wheel overhead and a long pendulum hanging through it
    gx, gy = 16.5, 25.0
    R.nocol.add(cyl(gx, gy, -1.0, -0.88, 1.6, 32, side='brass', top='brass', bottom='brass'))
    for k in range(32):
        a = 2 * math.pi * k / 32
        R.nocol.add(box(-0.06, -0.06, -1.0, 0.06, 0.06, -0.88, 'brass').xform(a, gx + math.cos(a) * 1.64, gy + math.sin(a) * 1.64, 0))
    R.nocol.add(cyl(gx, gy, -0.88, -0.6, 0.08, 10, side='iron', caps=False))
    M = R.mover('swing', pivot=(gx, gy, -0.9), axis='y', amp=0.22, period=6.0)
    M.nocol.add(beam((gx, gy, -0.9), (gx, gy, CZ + 0.75), 0.04, 'brass'))
    M.nocol.add(disc_v(gx, gy, CZ + 0.75, 0.35, math.pi / 2, 16, 'brass', off=0.0))
    M.nocol.add(disc_v(gx, gy, CZ + 0.75, 0.35, -math.pi / 2, 16, 'brass', off=0.0))
    R.col.add(box(gx - 0.75, gy - 0.25, CZ, gx + 0.75, gy + 0.25, CZ + 1.3))   # keeps you out of its swing
    # the bench, the lamp, the one right clock
    R.parts.add(table(20.5, WY0 + 0.3, 23.0, WY0 + 1.1, 0.9, 'oak').xform(0, 0, 0, CZ))
    for k in range(5):
        x = 20.8 + k * 0.45
        R.nocol.add(cyl(x, WY0 + 0.7, CZ + 0.9, CZ + 0.93, 0.1 + 0.03 * (k % 3), 12, side='brass', top='brass'))
    clock(R, 22.0, WY0, CZ + 1.9, 0.3, math.pi / 2, rng, style='case', rim='gilt')
    bulb(R, 21.8, WY0 + 0.8, CZ + 2.2, r=0.1, m='e_lamp', top=-0.6, shade='green')
    bulb(R, 14.0, 26.0, CZ + 2.3, r=0.1, m='e_dim', top=-0.6)
    R.light(sphere(WX1 - 0.4, WY1 - 0.4, CZ + 0.15, 0.06, 8, 4, 'e_candle'))
    R.spot('plaque', 22.0, WY0 + 0.7, CZ + 0.9)
    secret(R, 17.5, 23.5, CZ, 'The Works',
           'Behind the tallest clock, a stair down to the machinery. Every clock above is driven from here, and every one is slow, except the little one on the bench.', r=2.5)


def gear_v(R, x, y, z, r, a, rng, m='brass', t=0.12, teeth=None):
    """A toothed wheel standing on edge, its face toward plan angle a, centred at (x, y, z)."""
    teeth = teeth or max(12, int(r * 14))
    g = Geo()
    g.add(cyl(0, 0, 0, t, r, 24, side=m, top=m, bottom=m))
    for k in range(teeth):
        b = 2 * math.pi * k / teeth
        g.add(box(-0.05, -0.06, 0, 0.05, 0.06, t, m).xform(b, math.cos(b) * (r + 0.05), math.sin(b) * (r + 0.05), 0))
    g.add(cyl(0, 0, -0.1, t + 0.1, 0.12, 10, side='iron', top='iron', bottom='iron'))
    # stand it up: the wheel's axis (z) turned to horizontal along the facing
    rot(g, 'y', math.pi / 2)
    g.xform(a, x, y, z)
    R.parts.add(g)
