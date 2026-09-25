"""The Unfinished Room: a hall still being built. A half-raised arcade wall with its timber centring
still in the arches, stone waiting on pallets, the floor half laid, bookcases with no books on them yet,
tools where the masons put them down. Scaffolding climbs the north wall in three stepped bays; the top
one reaches a rough hole into a room above that nobody has even plastered: bare concrete."""
from kit_h6 import *
from kit_h5 import rubble

W = D = 32.0
YN = 25.4                     # the north wall; the concrete room is above the doorways, behind it
UZ = 4.8                      # the concrete room's floor
UP = (3.4, YN + 0.3, 28.6, D - 0.7)
AY = 13.0                     # the arcade wall (centre line), 1 m thick
BAYS = ((10.0, 14.0, 1.6), (14.0, 18.0, 3.2), (18.0, 22.0, UZ))   # scaffold bays: x0, x1, deck height
SY0 = 22.2                    # scaffold front


def make():
    R = Room('unfinished', 2, 2, res=2048)
    hall(R, y1=YN, h=TOP - 0.1, wall='tile', floor='concrete', ceil='concrete')
    rs = rng(48)
    arcade(R, rs)
    floor_laying(R, rs)
    cases(R, rs)
    scaffold(R, rs)
    upper(R, rs)
    yard(R, rs)
    lamps(R)
    fx(R, 'dust', [T, T, 0.2, W - T, YN, 7.2])
    fx(R, 'dust', [5.0, 6.0, 0.0, 11.0, 12.0, 7.4])
    p = navloop(R, [(2.2, 2.4), (8.0, 2.4), (24.0, 2.4), (29.8, 2.4), (29.8, 7.0), (29.8, 19.5), (24.0, 19.5), (8.0, 19.5), (2.2, 19.5), (2.2, 7.0)])
    a, b, c = R.navpt(8.0, 7.0), R.navpt(16.0, 7.0), R.navpt(24.0, 7.0)
    R.link(p[9], a, b, c, p[4])
    R.link(a, R.navpt(8.0, 10.6), R.navpt(8.0, 15.5), p[7]); R.link(c, R.navpt(24.0, 10.6), R.navpt(24.0, 15.5), p[6])
    return finish(R, 'The Unfinished Room', weight=3, probe=(16, 8.0, 2.4),
                  blurb='The masons have gone for lunch and not come back. The shelves are up, the books are not, and the dust is still settling from the last stone laid.')


def empty_case(R, x0, y0, x1, y1, face, rows=12, row_h=0.42, frame='oak', depth=0.34, missing=()):
    """A bookcase frame with no books on it yet (drawn, one collider). face '+y','-y','+x','-x'."""
    H = rows * row_h + 0.12
    g = Geo()
    along_x = face in ('+y', '-y')
    L = (x1 - x0) if along_x else (y1 - y0)
    for r in range(rows + 1):
        if r in missing: continue
        g.add(box(0, 0, r * row_h, L, depth, r * row_h + 0.035, frame, skip=('-z',) if r == 0 else ()))
    for u in (0.0, L - 0.04):
        g.add(box(u, 0, 0, u + 0.04, depth + 0.02, H, frame, skip=('-z',)))
    n = int(L / 1.0)
    for k in range(1, n):
        u = L * k / n
        g.add(box(u - 0.02, 0, 0, u + 0.02, depth, H, frame, skip=('-z',)))
    g.add(box(0, 0, 0, L, 0.02, H, 'plaster' if len(missing) else frame, skip=('-z', '+z')))
    ang = {'+y': 0.0, '-y': math.pi, '+x': -math.pi / 2, '-x': math.pi / 2}[face]
    ox, oy = {'+y': (x0, y0), '-y': (x1, y1), '+x': (x0, y1), '-x': (x1, y0)}[face]
    g.xform(ang, ox, oy, 0)
    R.nocol.add(g)
    R.col.add(box(0, 0, 0, L, depth + 0.02, H, 'tile').xform(ang, ox, oy, 0))


def arcade(R, rs):
    """A dividing wall of stone half raised across the hall: three great arches, the east end stepping
    down course by course to nothing, timber centring still standing in the unfinished arch."""
    y0, y1 = AY - 0.5, AY + 0.5
    arches = ((8.0, 5.0), (16.0, 5.0), (24.0, 5.0))
    AJ = 3.6
    # the courses: each 0.5 m high, built as blocks except in the arch openings
    top_at = lambda x: 7.2 if x < 12.5 else 1.2 * math.floor((7.2 - (x - 12.5) * 0.42) / 1.2 + 1e-6)
    xs = [T] + [c + s * w / 2 for (c, w) in arches for s in (-1, 1)] + [W - T]
    for k in range(12):
        z0, z1 = k * 0.6, k * 0.6 + 0.6
        x = T
        stagger = 0.35 if k % 2 else 0.0
        while x < W - T - 0.05:
            L = min(1.2 + (0.0 if x > T + 0.1 else stagger), W - T - x)
            xm = x + L / 2
            ok = z1 <= top_at(xm) + 0.01
            for (c, w) in arches:
                r = w / 2
                if abs(xm - c) < r + 0.05:
                    # inside the arch's width: only above the arch curve
                    dz = z0 - AJ
                    if dz < 0 or (dz < r and abs(xm - c) < math.sqrt(max(0.0, r * r - dz * dz)) + 0.2): ok = False
            if ok:
                inset = rs.uniform(0.0, 0.02)
                R.parts.add(box(x + 0.01, y0 + inset, z0, x + L - 0.01, y1 - inset, z1 - 0.012, 'tile'))
            elif z1 <= top_at(xm) + 0.61 and z0 <= top_at(xm) and rs.random() < 0.25 and not any(abs(xm - c) < w / 2 + 0.05 for (c, w) in arches):
                # a block set down on the top course, not yet mortared
                R.parts.add(box(x + 0.1, y0 + 0.15, z0, x + L - 0.3, y1 - 0.1, z1 - 0.05, 'tile'))
            x += L
    # arch voussoirs round the two finished arches, a timber centring in the unfinished one
    for (c, w) in arches[:2]:
        R.nocol.add(prism(arc_band(c, w, AJ, w / 2, -0.06, 0.4, 16), 'y', y0 - 0.04, y1 + 0.04, 'tile', cap='tile'))
    c, w = arches[2]
    for (yy0, yy1) in ((y0 + 0.05, y0 + 0.2), (y1 - 0.2, y1 - 0.05)):
        R.nocol.add(prism(arc_band(c, w, AJ, w / 2, 0.0, 0.18, 16), 'y', yy0, yy1, 'oak', cap='oak'))
    for k in range(9):
        a = math.pi * (k + 0.5) / 9
        px, pz = c + math.cos(a) * (w / 2 - 0.2), AJ + math.sin(a) * (w / 2 - 0.2)
        R.nocol.add(box(px - 0.04, y0 + 0.05, AJ, px + 0.04, y1 - 0.05, pz, 'oak') if pz - AJ > 0.2 else Geo())
    for x in (c - w / 2 + 0.2, c + w / 2 - 0.2):
        for yy in (y0 + 0.12, y1 - 0.12):
            R.parts.add(box(x - 0.08, yy - 0.08, 0, x + 0.08, yy + 0.08, AJ, 'oak'))
    R.nocol.add(box(c - w / 2 + 0.1, y0 + 0.05, AJ - 0.15, c + w / 2 - 0.1, y1 - 0.05, AJ, 'oak'))
    # a few voussoirs laid on the centring, the rest waiting on the floor
    for k in range(4):
        a = math.pi - math.pi * (k + 0.5) / 16
        px, pz = c + math.cos(a) * (w / 2 + 0.1), AJ + math.sin(a) * (w / 2 + 0.1)
        b = box(-0.2, -0.45, -0.22, 0.2, 0.45, 0.22, 'tile')
        rot(b, 'y', math.pi / 2 - a)
        R.nocol.add(b.xform(0, px, AY, pz))


def floor_laying(R, rs):
    """Marble flags laid over the south-west of the concrete, the edge ragged, a pile of flags waiting."""
    s = 0.8
    for i in range(int((W - 2 * T) / s)):
        for j in range(int((AY - 0.6 - T) / s)):
            x, y = T + i * s, T + j * s
            edge = 7.0 + 9.0 * (1 - j * s / AY) + 2.5 * math.sin(j * 1.7)
            if x > edge: continue
            if x > edge - 1.6 and rs.random() < 0.4: continue
            R.parts.add(box(x + 0.01, y + 0.01, 0, x + s - 0.01, y + s - 0.01, 0.03, 'terrazzo', skip=('-z',)))
    for k in range(9):
        R.parts.add(box(17.6, 3.0, k * 0.03, 17.6 + s, 3.0 + s, k * 0.03 + 0.03, 'terrazzo').xform(rs.uniform(-0.1, 0.1), 0, 0, 0))
    R.parts.add(box(15.8, 4.0, 0, 16.4, 4.5, 0.3, 'iron', top='concrete'))   # a tub of mortar


def cases(R, rs):
    """Bookcases up the walls, most still empty; one run half filled."""
    for (a, b) in ((0.7, 6.3), (9.7, 22.3)):
        empty_case(R, T, a, T + 0.34, b, '+x', rows=14, missing=(3, 7) if a < 5 else ())
        empty_case(R, W - T - 0.34, a, W - T, b, '-x', rows=14, missing=(9, 10, 11, 12, 13, 14) if a > 5 else ())
    for (a, b) in ((0.7, 6.3), (25.7, W - 0.7)):
        empty_case(R, a, T, b, T + 0.34, '+y', rows=14)
    # the one run somebody has started filling
    sh(R, '+y', T, 9.7, 22.3, rows=5, frame='oak')
    empty_case(R, 9.7, T, 22.3, T + 0.34, '+y', rows=14, missing=(0, 1, 2, 3, 4, 5))
    # boxes of books waiting to go up
    for k in range(7):
        x, y = 10.5 + k * 1.6 + rs.uniform(-0.2, 0.2), 1.2
        R.parts.add(box(x - 0.3, y - 0.22, 0, x + 0.3, y + 0.22, 0.4, 'oak', top='leather'))
        book_pile(R, x, y, 0.4, n=rs.randint(2, 6), seed=k, col=False)


def scaffold(R, rs):
    """Three bays of tube-and-plank scaffolding stepping up the north wall, ladders between them,
    rails on every open edge; the top deck reaches the hole into the room above."""
    y0, y1 = SY0, YN
    poles = set()
    for (x0, x1, z) in BAYS:
        for x in (x0, x1):
            for y in (y0, y1 - 0.15):
                poles.add((x, y))
    top = UZ + 1.2
    for (x, y) in sorted(poles):
        R.parts.add(box(x - 0.05, y - 0.05, 0, x + 0.05, y + 0.05, top, 'iron', skip=('-z',)))
        R.parts.add(box(x - 0.15, y - 0.15, 0, x + 0.15, y + 0.15, 0.03, 'oak'))
    for (x0, x1, z) in BAYS:
        # the deck: planks with gaps between, a toe board; ledgers at every lift
        for k in range(8):
            yy = y0 + 0.02 + k * (y1 - y0 - 0.04) / 8
            R.parts.add(box(x0 - 0.05, yy + 0.01, z - 0.06, x1 + 0.05, yy + (y1 - y0 - 0.04) / 8 - 0.02, z, 'oak', bottom='walnut'))
        for zz in [v for v in (1.6, 3.2, UZ) if v <= z + 0.01] + [z + 1.0]:
            R.nocol.add(box(x0, y0 - 0.04, zz - 0.12, x1, y0 + 0.04, zz - 0.06, 'iron'))
            R.nocol.add(box(x0 - 0.04, y0, zz - 0.12, x0 + 0.04, y1, zz - 0.06, 'iron'))
            R.nocol.add(box(x1 - 0.04, y0, zz - 0.12, x1 + 0.04, y1, zz - 0.06, 'iron'))
        # diagonal braces on the front
        R.nocol.add(beam((x0, y0 - 0.06, 0.1), (x1, y0 - 0.06, z - 0.1), 0.04, 'iron'))
        # nobody under the low bay: it is full of stone and sacks
        if z < 2.2:
            R.col.add(box(x0, y0, 0, x1, y1, z - 0.06, 'tile'))
            for k in range(5):
                bx = x0 + 0.3 + k * 0.75
                R.nocol.add(box(bx, y0 + 0.3, 0, bx + 0.6, y0 + 1.2, rs.uniform(0.35, 0.9), 'tile'))
            R.nocol.add(puffs(x0 + 1.5, y1 - 1.0, 0.2, 0.5, 3, 'ivory', seed=3, flat=0.5, segs=8, rings=4))
    # rails: the front of every deck, the open sides, gaps where the ladders arrive
    (a0, a1, za), (b0, b1, zb), (c0, c1, zc) = BAYS
    lad_y = 23.8
    rail(R, a0, y0 + 0.05, 11.4, y0 + 0.05, za)
    rail(R, 12.6, y0 + 0.05, a1, y0 + 0.05, za)
    rail(R, a0 + 0.05, y0, a0 + 0.05, y1 - 0.1, za)
    rail(R, b0, y0 + 0.05, b1, y0 + 0.05, zb)
    rail(R, b0 + 0.05, y0, b0 + 0.05, lad_y - 0.6, zb)
    rail(R, b0 + 0.05, lad_y + 0.6, b0 + 0.05, y1 - 0.1, zb)
    rail(R, b1 - 0.05, y0, b1 - 0.05, lad_y - 0.7, zb)
    rail(R, b1 - 0.05, lad_y + 0.7, b1 - 0.05, y1 - 0.1, zb)
    rail(R, c0, y0 + 0.05, c1, y0 + 0.05, zc)
    rail(R, c0 + 0.05, y0, c0 + 0.05, lad_y - 0.6, zc)
    rail(R, c0 + 0.05, lad_y + 0.6, c0 + 0.05, y1 - 0.1, zc)
    rail(R, c1 - 0.05, y0, c1 - 0.05, y1 - 0.1, zc)
    # ladders: floor to the low deck, low deck to the middle, middle to the top
    climb_ladder(R, 12.0, y0 - 0.02, 0.0, za, -math.pi / 2, run=0.8, w=0.6, m='oak', rails='iron')
    climb_ladder(R, b0 - 0.02, lad_y, za, zb, math.pi, run=0.85, w=0.6, m='oak', rails='iron')
    climb_ladder(R, c0 - 0.02, lad_y, zb, zc, math.pi, run=0.85, w=0.6, m='oak', rails='iron')
    # the hole in the wall at the top deck: stone knocked out, the concrete showing
    R.cut(box(c0 + 0.7, YN - 0.1, zc, c1 - 0.7, UP[1] + 0.1, zc + 2.2, 'concrete', bottom='concrete', top='concrete'))
    for k in range(7):
        R.nocol.add(box(c0 + 0.5 + rs.uniform(0, 3), YN - 0.35 - rs.uniform(0, 0.4), zc, c0 + 0.8 + rs.uniform(0, 3), YN - 0.2, zc + rs.uniform(0.08, 0.2), 'tile'))
    # buckets, a rope, a bag of tools on the decks
    R.nocol.add(cyl(a0 + 0.5, y1 - 0.6, za, za + 0.3, 0.14, 10, side='iron', top='concrete'))
    R.nocol.add(cyl(b1 - 0.6, y1 - 0.5, zb, zb + 0.3, 0.14, 10, side='iron', top='concrete'))
    R.nocol.add(box(c0 + 2.6, y0 + 0.3, zc, c0 + 3.3, y0 + 0.7, zc + 0.25, 'leather'))


def upper(R, rs):
    """The room above: bare concrete, formwork marks, rebar, one bulb, and somebody's drawings."""
    x0, y0, x1, y1 = UP
    R.cut(box(x0, y0, UZ, x1, y1, TOP - 0.1, 'concrete', bottom='concrete', top='concrete'))
    # columns of raw concrete with rebar sticking out of the tops
    for x in (9.0, 15.0, 22.0):
        R.parts.add(box(x - 0.3, y0 + 1.8, UZ, x + 0.3, y0 + 2.4, TOP - 0.1, 'concrete'))
    for k in range(10):
        x = rs.uniform(x0 + 0.3, x1 - 0.3)
        R.nocol.add(box(x - 0.012, y1 - 0.1, UZ, x + 0.012, y1 - 0.08, UZ + rs.uniform(0.3, 1.2), 'iron'))
    # formwork board marks on the walls
    for z in (UZ + 0.6, UZ + 1.2, UZ + 1.8):
        R.nocol.add(box(x0, y1 - 0.01, z - 0.01, x1, y1, z + 0.01, 'slate'))
    # a trestle table of drawings: the plans of the library
    R.parts.add(table(11.0, 29.0, 13.4, 30.2, 0.85, 'oak'))
    R.nocol.add(box(11.1, 29.1, 0.85 + UZ - UZ, 13.3, 30.1, 0.86, 'newsprint').xform(0, 0, 0, UZ))
    for k in range(6):
        R.nocol.add(sheet(11.4 + k * 0.35, 29.5 + rs.uniform(-0.2, 0.2), UZ + 0.862, rs.uniform(-0.4, 0.4), w=0.4, l=0.55, m='ivory'))
    R.nocol.add(cyl(13.0, 29.4, UZ + 0.86, UZ + 0.88, 0.2, 10, side='newsprint', top='newsprint'))
    R.parts.add(stool(12.2, 28.4, math.pi / 2, back=False).xform(0, 0, 0, UZ))
    # a bedroll, a kettle, a single bulb on a cable
    R.parts.add(box(19.5, 29.6, UZ, 21.5, 30.4, UZ + 0.12, 'green'))
    R.nocol.add(box(19.55, 29.65, UZ + 0.12, 20.1, 30.35, UZ + 0.24, 'bed'))
    R.spot('bed', 20.5, 30.0, UZ + 0.12, 0.0)
    R.nocol.add(cyl(18.8, 30.6, UZ, UZ + 0.2, 0.1, 10, side='iron', top='iron'))
    bulb(R, 12.2, 29.6, UZ + 1.9, r=0.1, m='e_lamp', top=TOP - 0.1)
    bulb(R, 20.0, 28.4, UZ + 1.9, r=0.06, m='e_amber', top=TOP - 0.1)
    bulb(R, 6.0, 28.5, UZ + 1.9, r=0.09, m='e_lamp', top=TOP - 0.1)
    bulb(R, 25.5, 28.5, UZ + 1.9, r=0.08, m='e_dim', top=TOP - 0.1)
    R.spot('plaque', 12.2, 29.6, UZ + 0.86, math.pi / 2,
           text='THE LIBRARY, AS DRAWN. Sheet 1 of an uncountable number. Revision: none. Every room is marked "to be finished later". So is this one.')
    secret(R, 16.0, 28.3, UZ, 'The Room Above',
           'At the top of the scaffolding, through the hole: a room nobody has finished, bare concrete, a bedroll, and on the table the plans. They are drawn in pencil. They go on for ever.')


def yard(R, rs):
    """The masons' yard in the middle of the hall: a workbench with tools, stone on pallets, a
    wheelbarrow, a sheer-legs hoist with a block swinging on its rope."""
    # the workbench
    R.parts.add(table(4.0, 8.8, 6.8, 9.8, 0.85, 'oak'))
    for (x, y, a, L, m) in ((4.5, 9.2, 0.3, 0.35, 'oak'), (5.2, 9.4, -0.2, 0.25, 'iron'), (6.1, 9.1, 1.1, 0.5, 'chrome')):
        R.nocol.add(obox(x, y, x + math.cos(a) * L, y + math.sin(a) * L, 0.85, 0.89, 0.04, m))
    R.nocol.add(box(5.6, 9.3, 0.85, 5.8, 9.5, 0.97, 'oak'))
    R.nocol.add(sheet(4.8, 9.5, 0.852, 0.2, w=0.3, l=0.42, m='newsprint'))
    desk_lamp(R, 6.4, 9.55, 0.85)
    # stone blocks on pallets
    for (x, y, n) in ((9.8, 5.2, 3), (11.4, 5.4, 2), (21.0, 9.0, 4), (26.0, 5.5, 3), (27.4, 10.2, 2)):
        R.parts.add(box(x - 0.6, y - 0.5, 0, x + 0.6, y + 0.5, 0.14, 'oak'))
        z = 0.14
        for k in range(n):
            R.parts.add(box(x - 0.55 + rs.uniform(0, 0.05), y - 0.4, z, x + 0.5 - rs.uniform(0, 0.05), y + 0.4, z + 0.45, 'tile'))
            z += 0.45
    rubble(R, 13.0, 11.2, 0.9, 0.3, rs, n=14, m=('tile', 'concrete', 'plaster'))
    # a wheelbarrow
    g = Geo()
    g.add(box(-0.4, -0.3, 0.35, 0.4, 0.3, 0.7, 'green'))
    g.add(cyl(0, 0, -0.05, 0.05, 0.2, 10, side='iron', top='iron', bottom='iron'))
    wh = cyl(0, 0, -0.04, 0.04, 0.2, 10, side='iron', top='iron', bottom='iron')
    rot(wh, 'x', math.pi / 2); wh.v = [(a + 0.55, b, c + 0.2) for a, b, c in wh.v]
    g.add(wh)
    for s in (-0.25, 0.25):
        g.add(beam((0.55, s * 0.4, 0.2), (-1.0, s, 0.6), 0.04, 'oak'))
        g.add(box(-0.3, s - 0.02, 0, -0.26, s + 0.02, 0.4, 'iron'))
    R.parts.add(g.xform(0.5, 23.0, 5.2, 0))
    # the sheer-legs hoist over the stone, a block hanging on the rope and swinging a little
    hx, hy = 21.0, 9.0
    for (dx, dy) in ((-1.6, -1.2), (1.6, -1.2), (0.0, 1.6)):
        R.nocol.add(beam((hx + dx, hy + dy, 0), (hx, hy, 6.4), 0.14, 'oak'))
        R.parts.add(box(hx + dx - 0.1, hy + dy - 0.1, 0, hx + dx + 0.1, hy + dy + 0.1, 1.2, 'oak'))
    R.nocol.add(wheel(hx, hy, 6.2, 0.3, axis='x', spokes=4, rim=0.05, w=0.08, m='iron'))
    M = R.mover('swing', pivot=(hx, hy, 6.2), axis='x', amp=0.05, period=7.0)
    M.nocol.add(box(hx - 0.015, hy - 0.015, 4.2, hx + 0.015, hy + 0.015, 6.2, 'leather'))
    M.nocol.add(box(hx - 0.1, hy - 0.1, 4.0, hx + 0.1, hy + 0.1, 4.2, 'iron'))
    M.nocol.add(box(hx - 0.5, hy - 0.35, 3.4, hx + 0.5, hy + 0.35, 4.0, 'tile'))
    rail(R, hx - 1.3, hy - 1.3, hx + 1.3, hy - 1.3, 0.0, h=0.9)
    # sacks, a ladder lying down, a sawhorse
    for (x, y) in ((3.0, 11.0), (3.5, 11.6), (2.6, 11.7)):
        R.nocol.add(puffs(x, y, 0.2, 0.35, 2, 'ivory', seed=int(x * 10), flat=0.6, segs=8, rings=4))
    R.nocol.add(box(24.0, 16.0, 0, 28.0, 16.1, 0.08, 'oak'))
    R.nocol.add(box(24.0, 16.5, 0, 28.0, 16.6, 0.08, 'oak'))
    for k in range(12):
        R.nocol.add(box(24.2 + k * 0.32, 16.0, 0.0, 24.25 + k * 0.32, 16.6, 0.05, 'oak'))


def lamps(R):
    # the unfinished roof: a hole where the daylight comes in, over the yard
    R.cut(box(5.0, 6.0, TOP - 0.15, 11.0, 12.0, TOP + 0.3, 'concrete', bottom='concrete', top='concrete'))
    R.light(box(5.0, 6.0, TOP + 0.24, 11.0, 12.0, TOP + 0.26, 'e_sky'))
    for k in range(5):
        R.nocol.add(box(5.0 + k * 1.4, 6.0, TOP - 0.2, 5.15 + k * 1.4, 12.0, TOP - 0.05, 'oak'))
    # work lamps strung on cables, bare bulbs
    for (x, y) in ((16.0, 5.0), (24.0, 4.0), (28.0, 10.0), (16.0, 18.0), (8.0, 18.5), (24.0, 18.5), (3.5, 4.0)):
        bulb(R, x, y, 3.6, r=0.12, m='e_lamp', top=TOP - 0.15, shade='iron')
    for (x, y) in ((9.6, 20.8), (22.8, 21.0)):
        R.light(sphere(x, y, 1.1, 0.07, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, y, 0, 1.05, 0.02, 6, side='iron', caps=False))
        R.col.add(box(x - 0.05, y - 0.05, 0, x + 0.05, y + 0.05, 1.1, 'tile'))
