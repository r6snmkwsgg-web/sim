"""The Lighthouse: a hall the size of a harbour, and its floor is a dark sea of books, heaped in slow
waves. Round the walls a quay runs under a railed gallery; two long stairs go down from the gallery into
the sea. In the middle, on a rock of stone and books, a white lighthouse. Its door is open, a stair winds
up inside it, and at the top is the keeper's room, and above that, up a steep ladder through a hatch,
the lamp itself, turning (fx beam), and a gallery round it looking out over the whole dark sea."""
from kit_h7 import *
from kit_h5 import cone

W = D = 64.0
CX = CY = 32.0
LE = 5.4                       # the gallery (and the quay under it) from the walls
UP = LH                        # gallery floor
RT0, RT1 = 4.0, 3.4            # the tower's outer radius at its foot and at its top
RI = 3.1                       # the tower's inside
RN = 1.3                       # the newel (the stair winds from RN to RI)
TH0 = math.radians(162)        # the stair starts here (so the keeper's floor is the west half)
RISE = 5.0                     # per turn
ZK = 9.0                       # the keeper's room floor
ZL = 12.0                      # the lamp room / gallery floor
RL = 2.55                      # the lantern's glazing
RG = 3.9                       # the lamp gallery's edge
LADX = CX - 1.75               # the ladder from the keeper's room to the lamp, climbing +y
LY0, LY1 = CY - 1.25, CY + 1.75


def ro(z):
    return RT0 + (RT1 - RT0) * z / ZL


def make():
    R = Room('lighthouse', 4, 4, levels=2, res=2048)
    R.sockets(floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, R.hi - 0.1, 'tile', bottom='floor', top='plaster'))
    sea(R)
    quay(R)
    tower(R)
    keeper(R)
    lamp(R)
    fx(R, 'beam', None, at=[CX, CY, ZL + 1.4], r=0.9)
    fx(R, 'fog', [LE, LE, 0.0, W - LE, D - LE, 5.0], density=0.03)
    e = 2.4
    navloop(R, [(e, e), (32, e), (W - e, e), (W - e, 32), (W - e, D - e), (32, D - e), (e, D - e), (e, 32)])
    e = 4.6
    navloop(R, [(e, e), (24, e), (40, e), (W - e, e), (W - e, 32), (W - e, D - e), (40, D - e), (24, D - e), (e, D - e), (e, 32)], z=UP)
    return finish(R, 'The Lighthouse', weight=2, probe=(CX + 12, CY - 12, 3.0), top=R.hi,
                  blurb='The floor of this hall is a sea of books, heaped in long dark waves, and out in the middle of it a lighthouse is keeping watch. Nobody knows what for. The lamp turns anyway.')


def sea_h(x, y):
    """The sea: slow waves of heaped books, calm at the quay, a rock round the tower."""
    d_edge = min(x - LE, y - LE, W - LE - x, D - LE - y)
    if d_edge < 0: return 0.0
    fade = min(1.0, d_edge / 5.0)
    r = math.hypot(x - CX, y - CY)
    w = 0.32 * (math.sin(x * 0.31 + y * 0.12) + 0.6 * math.sin(y * 0.43 - x * 0.17 + 1.3) + 0.4 * math.sin((x + y) * 0.21 + 0.7)) + 0.45
    w = max(0.0, w) * fade
    # calm lanes where the stairs come down
    for (sx, sy) in ((CX, 17.0), (CX, D - 17.0)):
        dd = math.hypot((x - sx) * 1.4, (y - sy) * 0.6)
        if dd < 4.5: w *= dd / 4.5
    if r < 9.0: w *= max(0.0, (r - 7.0) / 2.0)
    return w


def sea(R):
    rnd = rng(58)
    R.parts.add(field(sea_h, LE, LE, W - LE, D - LE, 53, 53, m='walnut', floor=0.0, eps=0.01))
    # the rock at the tower's foot: stone blocks and piled books
    R.parts.add(ring(CX, CY, 0.0, 0.45, RT0 - 0.2, 6.6, 48, top='slate', bottom='slate', inner='slate', outer='slate'))
    for k in range(26):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(6.4, 8.3)
        x, y = CX + r * math.cos(a), CY + r * math.sin(a)
        if abs(((a - TH0 + 0.35 + math.pi) % (2 * math.pi)) - math.pi) < 0.35: continue       # the way to the door
        s = rnd.uniform(0.5, 1.1)
        g = box(-s, -s * 0.7, 0, s, s * 0.7, rnd.uniform(0.2, 0.5), rnd.choice(('slate', 'slate', 'tile')))
        g.xform(rnd.uniform(0, math.pi), x, y, 0)
        R.nocol.add(g)
    # books lying on the waves
    g = Geo()
    for k in range(2600):
        x, y = rnd.uniform(LE + 0.5, W - LE - 0.5), rnd.uniform(LE + 0.5, D - LE - 0.5)
        if math.hypot(x - CX, y - CY) < 6.5: continue
        book_scatter(g, x, y, sea_h(x, y) + 0.005, rnd, 1, spread=0.0, tilt=0.3)
    # and heaps of them here and there, like the tops of waves
    for k in range(70):
        x, y = rnd.uniform(LE + 3, W - LE - 3), rnd.uniform(LE + 3, D - LE - 3)
        if math.hypot(x - CX, y - CY) < 8.5 or abs(x - CX) < 3: continue
        z = sea_h(x, y)
        for j in range(rnd.randint(4, 12)):
            book_scatter(g, x, y, z + j * 0.045, rnd, 1, spread=0.12, tilt=0.12)
    R.nocol.add(g)
    # buoys: little lanterns on posts out in the sea
    for (x, y) in ((18, 22), (46, 20), (44, 46), (20, 44), (12, 32), (52, 33)):
        z = sea_h(x, y)
        R.parts.add(cyl(x, y, 0, z + 0.9, 0.08, 8, side='iron', caps=False))
        R.parts.add(box(x - 0.14, y - 0.14, z + 0.9, x + 0.14, y + 0.14, z + 0.95, 'iron'))
        R.light(sphere(x, y, z + 1.1, 0.13, 10, 5, 'e_candle'))
        R.parts.add(box(x - 0.15, y - 0.15, z + 1.25, x + 0.15, y + 0.15, z + 1.3, 'iron'))


def quay(R):
    """The quay round the walls, the gallery over it (railed), its columns, its books and lamps, and the
    two long stairs from the gallery down into the sea."""
    th = 0.45
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, W - T + 0.02, LE), (T - 0.02, D - LE, W - T + 0.02, D - T + 0.02),
                             (T - 0.02, LE, LE, D - LE), (W - LE, LE, W - T + 0.02, D - LE)):
        R.parts.add(box(x0, y0, UP - th, x1, y1, UP, 'tile', top='floor', bottom='plaster'))
    # a stone kerb where the quay meets the sea
    for (x0, y0, x1, y1) in ((LE - 0.3, LE - 0.3, W - LE + 0.3, LE), (LE - 0.3, D - LE, W - LE + 0.3, D - LE + 0.3),
                             (LE - 0.3, LE, LE, D - LE), (W - LE, LE, W - LE + 0.3, D - LE)):
        R.parts.add(box(x0, y0, 0, x1, y1, 0.18, 'tile'))
    # columns under the gallery's edge
    for p in (LE, 16.0, 32.0, 48.0, W - LE):
        for (x, y) in ((p, LE), (p, D - LE), (LE, p), (W - LE, p)):
            if p == 32.0 and x == 32.0: continue            # the stairs land there
            R.parts.add(box(x - 0.35, y - 0.35, 0.18, x + 0.35, y + 0.35, UP - th, 'tile', skip=('-z',)))
    # the rail round the gallery, broken where the stairs leave it
    sw = 2.4
    xs0, xs1 = CX - sw / 2, CX + sw / 2
    r_ = 0.12
    for (y, ya) in ((LE - r_, LE), (D - LE + r_, D - LE)):
        brail(R, LE - r_, y, xs0, y, UP)
        brail(R, xs1, y, W - LE + r_, y, UP)
    brail(R, LE - r_, LE, LE - r_, D - LE, UP)
    brail(R, W - LE + r_, LE, W - LE + r_, D - LE, UP)
    # the stairs: 40 steps from the gallery's edge down to the sea, railed both sides
    n, rise, run = 40, UP / 40, 0.3
    for (y0, ax) in ((LE + n * run, '-y'), (D - LE - n * run, '+y')):
        gflight(R, xs0, y0, 0.0, sw, n, rise, run, ax, m='tile', riser='tile', side='tile')
        gflight_rail(R, xs0, y0, 0.0, sw, n, rise, run, ax, which=(0, 1), m='tile', cap='brass')
    # books on every wall, both levels; tables and lamps on the gallery
    wall_cases(R, rows=13, frame='walnut')
    wall_cases(R, z=UP, rows=11, frame='walnut')
    for (x, y, ax) in ((16, 3.0, 'x'), (48, 3.0, 'x'), (16, D - 3.0, 'x'), (48, D - 3.0, 'x'), (3.0, 16, 'y'), (3.0, 48, 'y'), (W - 3.0, 16, 'y'), (W - 3.0, 48, 'y')):
        if ax == 'x': reading_table(R, x - 1.8, y - 0.5, x + 1.8, y + 0.5, lamps=2, z=UP)
        else: reading_table(R, x - 0.5, y - 1.8, x + 0.5, y + 1.8, lamps=2, z=UP, axis='y')
    # little lamps on the rail posts, and dim lamps under the gallery
    for p in (12.0, 20.0, 28.0, 36.0, 44.0, 52.0):
        for (x, y) in ((p, LE - 0.12), (p, D - LE + 0.12), (LE - 0.12, p), (W - LE + 0.12, p)):
            R.light(sphere(x, y, UP + 1.25, 0.09, 8, 4, 'e_amber'))
            R.nocol.add(cyl(x, y, UP + 1.06, UP + 1.18, 0.02, 6, side='brass', caps=False))
        for (x, y) in ((p, LE - 1.5), (p, D - LE + 1.5), (LE - 1.5, p), (W - LE + 1.5, p)):
            R.light(sphere(x, y, UP - th - 0.4, 0.12, 8, 4, 'e_dim'))
            R.nocol.add(cyl(x, y, UP - th - 0.3, UP - th, 0.01, 4, side='iron', caps=False))
    for (x, y) in ((8, 8), (W - 8, 8), (8, D - 8), (W - 8, D - 8)):
        pendant(R, x, y, UP + 3.4, R.hi - 0.1, r=0.3)


def band(R, z0, z1, gaps=(), m='ivory', inner='tile', segs=48):
    """One course of the tower wall from z0 to z1, tapered, with window or door gaps (angle, half-width)."""
    prof = [(RI, z0), (ro(z0), z0), (ro(z1), z1), (RI, z1)]
    mats = ['tile', m, 'tile', inner]
    if not gaps:
        R.parts.add(lathe(CX, CY, prof, segs, mats)); return
    gs = sorted(((a - h) % (2 * math.pi), (a + h) % (2 * math.pi)) for (a, h) in gaps)
    edges = []
    for (s, e) in gs: edges.append((s, e))
    for i in range(len(edges)):
        a0 = edges[i][1]; a1 = edges[(i + 1) % len(edges)][0]
        if a1 <= a0: a1 += 2 * math.pi
        n = max(2, int(segs * (a1 - a0) / (2 * math.pi)))
        R.parts.add(lathe(CX, CY, prof, n, mats, a0=a0, a1=a1))


def tower(R):
    """The tower: stone at the foot, white above with red bands, a door on the south, slit windows where the
    stair runs a metre under them; inside, the stair winds round a stone newel."""
    door = (TH0 - 0.4, 0.2)
    wa = TH0 + 2 * math.pi * 1.6 / RISE  # the stair is 1.6 m up here: a window at 2.6
    wb = TH0 + 2 * math.pi * 5.0 / RISE  # and 5.0 m up here: a window at 6.0
    band(R, 0.0, 2.6, [door], m='tile')
    band(R, 2.6, 3.8, [(wa, 0.12)])
    band(R, 3.8, 6.0, m='oxblood')
    band(R, 6.0, 7.2, [(wb, 0.12)])
    band(R, 7.2, ZK + 0.6)
    band(R, ZK + 0.6, ZK + 1.8, [(TH0 + k * math.pi / 2 + math.pi / 4, 0.12) for k in range(4)])
    band(R, ZK + 1.8, ZL - 0.3, m='oxblood')
    # a door frame, and the door standing open
    dx, dy = math.cos(door[0]), math.sin(door[0])
    px, py = -dy, dx
    for s in (-1, 1):
        a = door[0] + s * (door[1] + 0.02)
        R.parts.add(box(CX + (RT0 + 0.02) * math.cos(a) - 0.1, CY + (RT0 + 0.02) * math.sin(a) - 0.1, 0, CX + (RT0 + 0.02) * math.cos(a) + 0.1, CY + (RT0 + 0.02) * math.sin(a) + 0.1, 2.7, 'walnut'))
    R.light(box(CX + dx * (RT0 + 0.05) - 0.12, CY + dy * (RT0 + 0.05) - 0.12, 2.75, CX + dx * (RT0 + 0.05) + 0.12, CY + dy * (RT0 + 0.05) + 0.12, 3.0, 'e_amber'))
    # the newel, the stair, a handrail on the newel, the floor inside
    R.parts.add(cyl(CX, CY, 0.0, ZK, RN, 32, side='tile', top='oak'))
    turns = ZK / RISE
    R.parts.add(helix(CX, CY, RN, RI + 0.02, 0.0, RISE, TH0, TH0 + 2 * math.pi * turns, 0.35, 160, top='oak', side='tile', bottom='plaster'))
    R.nocol.add(helix(CX, CY, RN - 0.05, RN + 0.02, 0.95, RISE, TH0 + 0.2, TH0 + 2 * math.pi * turns - 0.1, 0.06, 150, top='brass', side='brass', bottom='brass'))
    # lamps up the stair (on the newel)
    for k in range(6):
        a = TH0 + 0.6 + k * 2 * math.pi * turns / 6.3
        z = RISE * (a - TH0) / (2 * math.pi) + 2.1
        R.light(sphere(CX + (RN + 0.15) * math.cos(a), CY + (RN + 0.15) * math.sin(a), z, 0.07, 8, 4, 'e_lamp'))
    # the cornice under the lamp gallery
    R.parts.add(lathe(CX, CY, [(RI, ZL - 0.3), (RT1 + 0.05, ZL - 0.3), (RG, ZL - 0.05), (RI, ZL - 0.05)], 48, 'ivory'))


def keeper(R):
    """At the top of the stair: the keeper's room, round, with a bed, a desk and the log, a stove, books.
    A steep ladder goes up through a hatch to the lamp."""
    z = ZK
    a_hole0 = TH0 + 2 * math.pi * (ZK / RISE) - math.pi       # the stair comes up through here
    a_hole1 = TH0 + 2 * math.pi * (ZK / RISE)
    R.parts.add(ring(CX, CY, z - 0.3, z, RN, RI + 0.02, 40, top='floor', bottom='plaster', inner='tile', outer='tile', a0=a_hole1, a1=a_hole0 + 2 * math.pi))
    # rails round the hole (not at its top end, where the stair arrives)
    ring_rail(R, CX, CY, RN - 0.1, z, a_hole0, a_hole1 - 0.35, n=6, m='brass')
    rail_line(R, [(CX + (RN - 0.1) * math.cos(a_hole0), CY + (RN - 0.1) * math.sin(a_hole0)), (CX + (RI - 0.1) * math.cos(a_hole0), CY + (RI - 0.1) * math.sin(a_hole0))], z, m='brass')
    # the room's things (on the side away from the stair hole)
    rnd = rng(12)
    def at(r, a): return CX + r * math.cos(a), CY + r * math.sin(a)
    x, y = at(2.5, math.radians(245))
    g = box(-1.0, -0.45, 0, 1.0, 0.45, 0.45, 'bed', sides='walnut'); g.add(box(0.8, -0.45, 0, 0.9, 0.45, 0.9, 'walnut'))
    g.xform(math.radians(245) + math.pi / 2, x, y, z); R.parts.add(g)
    R.spot('bed', x, y, z + 0.45, math.radians(245))
    x, y = at(2.55, math.radians(103))
    desk(R, x, y, math.radians(103) + math.pi / 2, z=z, w=1.2, d=0.55)
    desk_lamp(R, x, y, z + 0.78)
    open_book(R, x + 0.2, y - 0.1, z + 0.78, math.radians(50))
    cx_, cy_ = at(1.85, math.radians(103))
    R.parts.add(chair(cx_, cy_, math.radians(103)).xform(0, 0, 0, z))
    R.spot('sit', cx_, cy_, z + 0.48, math.radians(103))
    R.light(sphere(*at(2.9, math.radians(265)), z + 0.9, 0.06, 8, 4, 'e_candle'))
    for a in (math.radians(180), math.radians(205)):
        half = 0.7
        bx, by = at(RI - 0.05, a)
        fa = a + math.pi
        ux, uy = math.sin(fa), -math.cos(fa)
        shelf(R, bx - ux * half, by - uy * half, z, 2 * half, fa, rows=5, frame='walnut', depth=0.28)
    book_pile(R, *at(0.7, math.radians(300)), z, 6, seed=3)
    bulb(R, *at(1.0, math.radians(180)), ZL - 0.8, r=0.1, top=ZL - 0.3, shade='green')
    # the ladder up through the hatch (45 degrees: the walk check samples every half metre here)
    ladder_up(R, LADX, LY0, z, ZL, '+y', w=1.0, m='oak', rail='brass', ang=math.radians(45))
    R.spot('plaque', *at(RI - 0.05, math.radians(160)), z + 1.5, math.radians(160) + math.pi, text='KEEPER: KEEP THE LAMP LIT. NO SHIPS HAVE COME. KEEP IT LIT.')
    secret(R, *at(0.8, math.radians(180)), z, "The Keeper's Room",
           'At the top of the stair, a round room with a narrow bed, a stove and a log kept in a careful hand. Every entry says the same thing: lamp lit, no ships.', r=2.0)


def lamp(R):
    """The lamp room: the floor over the keeper's room (with the hatch), the lantern's iron frame, the lamp
    and its brass lens, a gallery round it all, railed, over the sea; a copper-green roof."""
    hx0, hx1, hy0, hy1 = LADX - 0.6, LADX + 0.6, LY0 + 0.8, LY1 + 0.05
    R.parts.add(disc_with_hole(CX, CY, RG, ZL - 0.3, ZL, (hx0, hy0, hx1, hy1), 48, top='floor', side='ivory', bottom='plaster'))
    rail_line(R, [(hx1 + 0.06, hy1), (hx1 + 0.06, hy0 - 0.06), (hx0 - 0.06, hy0 - 0.06), (hx0 - 0.06, hy1)], ZL, m='brass')
    ring_rail(R, CX, CY, RG - 0.12, ZL, 0, 2 * math.pi, n=40, m='iron')
    # the lantern: posts, a sill, the roof
    for k in range(10):
        a = 2 * math.pi * (k + 0.5) / 10
        x, y = CX + RL * math.cos(a), CY + RL * math.sin(a)
        if hx0 - 0.3 < x < hx1 + 0.3 and hy0 - 0.3 < y < hy1 + 0.6: continue
        R.parts.add(box(x - 0.06, y - 0.06, ZL, x + 0.06, y + 0.06, ZL + 2.75, 'iron'))
        for zz in (ZL + 0.9, ZL + 1.9):
            b = (CX + RL * math.cos(a + math.pi / 10 * 2), CY + RL * math.sin(a + math.pi / 10 * 2))
            R.nocol.add(beam((x, y, zz), (b[0], b[1], zz), 0.03, 'iron'))
    R.parts.add(ring(CX, CY, ZL + 2.75, ZL + 2.95, RL - 0.1, RL + 0.35, 40, top='iron', bottom='iron', inner='iron', outer='iron'))
    R.parts.add(cone(CX, CY, ZL + 2.95, R.hi - 0.18, RL + 0.35, 0.1, 24, m='green', bottom='iron'))
    R.parts.add(sphere(CX, CY, R.hi - 0.16, 0.12, 10, 5, 'brass'))
    # the lamp on its pedestal inside a lens of brass rings
    R.parts.add(cyl(CX, CY, ZL, ZL + 0.85, 0.45, 20, side='brass', top='brass'))
    R.light(sphere(CX, CY, ZL + 1.4, 0.38, 20, 10, 'e_lamp'))
    for k in range(7):
        zz = ZL + 0.95 + k * 0.15
        rr = 0.62 - abs(k - 3) * 0.05
        R.nocol.add(ring(CX, CY, zz, zz + 0.05, rr, rr + 0.05, 28, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.col.add(cyl(CX, CY, ZL, ZL + 2.1, 0.75, 16))
    R.light(ring(CX, CY, ZL + 2.6, ZL + 2.62, 0.2, 0.9, 20, top='e_dim', bottom='e_dim', inner='e_dim', outer='e_dim'))
    secret(R, CX + 1.8, CY - 0.6, ZL, 'The Lamp',
           'Up the ladder, through the hatch, and you are standing beside the lamp itself, with the whole dark sea of books below you and the beam going round and round over it, looking for something.', r=1.8)
