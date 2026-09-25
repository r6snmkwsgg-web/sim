"""The Catwalks: a square of library sixty metres across with no floor. An iron grid of catwalks
crosses it at the height of the upper doors, railed in brass, and under every span a bookcase hangs on
rods over nothing; far below them, a long way below, the sky. The walls are books all the way down.
Under the crossing at (40, 24) hangs an iron box you would take for one more bookcase: a hatch in the
crossing, a steep stair, and the maintenance room of the grid."""
from kit_h8 import *

W = D = 64.0
Z = 8.0                          # the catwalks
G = (8.0, 24.0, 40.0, 56.0)      # the grid lines, on the doorways
HW = 1.2                         # half a catwalk
SQ = 2.0                         # half a crossing
PE = T + 2.0                     # the perimeter walkway's inner edge
MX, MY = 40.0, 24.0              # the crossing with the maintenance room under it
MR = 2.4                         # half the room
MZ = 4.6                         # its floor
HX0, HX1, HY0, HY1 = 39.2, 40.8, 23.3, 25.9     # the hatch (the stair comes down it toward -y)


def make():
    R = Room('catwalks', 4, 4, levels=2, res=2048)
    skip = [(s, i, 0) for s in 'SNWE' for i in range(4)]
    seal(R, skip, floor='iron', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, -1.9, W - T + 0.02, D - T + 0.02, 15.2, 'tile', bottom='slate', top='plaster'))
    R.light(box(T, T, -1.9, W - T, D - T, -1.88, 'e_skydome'))
    grid(R)
    books(R)
    lamps(R)
    maintenance(R)
    nav(R)
    fx(R, 'fog', [T, T, -1.9, W - T, D - T, 3.0], density=0.03)
    fx(R, 'dust', [T, T, 4, W - T, D - T, 13])
    secret(R, 39.0, 23.6, MZ, 'The Maintenance Room',
           'Under the crossing, behind what looks from the catwalks like one more hanging bookcase, is the room where somebody keeps the grid: a bench of tools, a cot, a kettle, a logbook. The last entry says: all rails sound.')
    return finish(R, 'The Catwalks', weight=2, probe=(24, 24, Z + 2.0), top=15.2, bot=-1.9,
                  blurb='There is no floor. There is a grid of iron walkways, and bookcases hanging from them on rods, and a long way down, the sky.')


def deck(R, x0, y0, x1, y1):
    """An iron grating walk with a stringer each side."""
    R.parts.add(box(x0, y0, Z - 0.1, x1, y1, Z, 'iron'))
    R.nocol.add(box(x0, y0, Z - 0.45, x1, y0 + 0.12, Z - 0.1, 'iron'))
    R.nocol.add(box(x0, y1 - 0.12, Z - 0.45, x1, y1, Z - 0.1, 'iron'))
    R.nocol.add(box(x0, y0, Z - 0.45, x0 + 0.12, y1, Z - 0.1, 'iron'))
    R.nocol.add(box(x1 - 0.12, y0, Z - 0.45, x1, y1, Z - 0.1, 'iron'))


def rail(R, x0, y0, x1, y1):
    if math.hypot(x1 - x0, y1 - y0) > 0.15: iron_rail(R, x0, y0, x1, y1, Z)


def grid(R):
    e = 0.06
    # the perimeter walkway, round the walls
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, W - T + 0.02, PE), (T - 0.02, D - PE, W - T + 0.02, D - T + 0.02),
                             (T - 0.02, PE, PE, D - PE), (W - PE, PE, W - T + 0.02, D - PE)):
        deck(R, x0, y0, x1, y1)
    cuts = [PE] + [c + s * HW for c in G for s in (-1, 1)] + [W - PE]
    for k in range(0, len(cuts), 2):
        a, b = cuts[k], cuts[k + 1]
        rail(R, a, PE - e, b, PE - e); rail(R, a, D - PE + e, b, D - PE + e)
        rail(R, PE - e, a, PE - e, b); rail(R, W - PE + e, a, W - PE + e, b)
    # crossings and spans
    for cx in G:
        for cy in G:
            if (cx, cy) == (MX, MY): crossing_hatch(R)
            else: deck(R, cx - SQ, cy - SQ, cx + SQ, cy + SQ)
            for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                # the four corners of the square, railed round from the catwalk's edge to the corner
                xc, yc = cx + sx * (SQ - e), cy + sy * (SQ - e)
                rail(R, cx + sx * HW, yc, xc, yc)
                rail(R, xc, cy + sy * HW, xc, yc)
    ends = [PE] + [c + s * SQ for c in G for s in (-1, 1)] + [W - PE]
    for c in G:
        for k in range(0, len(ends), 2):
            a, b = ends[k], ends[k + 1]
            deck(R, a - 0.02, c - HW, b + 0.02, c + HW)
            rail(R, a, c - HW + e, b, c - HW + e); rail(R, a, c + HW - e, b, c + HW - e)
            deck(R, c - HW, a - 0.02, c + HW, b + 0.02)
            rail(R, c - HW + e, a, c - HW + e, b); rail(R, c + HW - e, a, c + HW - e, b)
            # hangers and a bookcase hung under each long span, over nothing
            if b - a > 8:
                hang_stack(R, 'x', c, a + 1.0, b - 1.0, skip=(c == MY and a < MX < b + 3))
                hang_stack(R, 'y', c, a + 1.0, b - 1.0, skip=(c == MX and a < MY < b + 3))
    # cross-bracing under the grid, iron beams to the walls at every line
    for c in G:
        R.nocol.add(box(T, c - 0.08, Z - 1.1, W - T, c + 0.08, Z - 0.45, 'iron'))
        R.nocol.add(box(c - 0.08, T, Z - 1.3, c + 0.08, D - T, Z - 1.1, 'iron'))


def hang_stack(R, axis, c, a, b, skip=False):
    """A double-sided bookcase hung by rods under a span."""
    if skip: return
    rows = 8
    H = rows * 0.42 + 0.12
    z = Z - 0.55 - H
    stack(R, axis, c, a, b, z=z, rows=rows, frame='walnut')
    for t in (a + 0.3, (a + b) / 2, b - 0.3):
        for s in (-0.25, 0.25):
            x, y = (t, c + s) if axis == 'x' else (c + s, t)
            R.nocol.add(box(x - 0.02, y - 0.02, z + H, x + 0.02, y + 0.02, Z - 0.1, 'iron'))
    if axis == 'x': R.nocol.add(box(a, c - 0.4, z - 0.12, b, c + 0.4, z, 'walnut'))
    else:           R.nocol.add(box(c - 0.4, a, z - 0.12, c + 0.4, b, z, 'walnut'))


def crossing_hatch(R):
    """The crossing over the maintenance room: a deck with a railed hatch in it, the stair going down."""
    x0, y0, x1, y1 = MX - MR, MY - MR, MX + MR, MY + MR
    for (a0, b0, a1, b1) in ((x0, y0, x1, HY0), (x0, HY1, x1, y1), (x0, HY0, HX0, HY1), (HX1, HY0, x1, HY1)):
        R.parts.add(box(a0, b0, Z - 0.3, a1, b1, Z, 'iron', bottom='walnut'))
    rail(R, HX0 - 0.05, HY1, HX0 - 0.05, HY0 - 0.05)
    rail(R, HX0 - 0.05, HY0 - 0.05, HX1 + 0.05, HY0 - 0.05)
    rail(R, HX1 + 0.05, HY0 - 0.05, HX1 + 0.05, HY1)
    R.nocol.add(box(HX0, HY1 + 0.02, Z, HX1, HY1 + 0.06, Z + 0.9, 'iron'))      # the hatch's leaf, standing open
    R.light(box(HX1 + 0.1, HY1 + 0.05, Z + 0.95, HX1 + 0.3, HY1 + 0.09, Z + 1.05, 'e_amber'))


def maintenance(R):
    """The iron box under the crossing, dressed outside with shelves like the hanging bookcases."""
    x0, y0, x1, y1 = MX - MR, MY - MR, MX + MR, MY + MR
    t = 0.12
    R.parts.add(box(x0, y0, MZ - 0.3, x1, y1, MZ, 'iron', top='oak'))
    wz = Z - 0.3
    # walls, with a window in the north side (sill a metre up), west of the stair
    R.parts.add(box(x0, y0, MZ, x1, y0 + t, wz, 'iron'))
    R.parts.add(box(x0, y0 + t, MZ, x0 + t, y1, wz, 'iron'))
    R.parts.add(box(x1 - t, y0 + t, MZ, x1, y1, wz, 'iron'))
    wx0, wx1 = x0 + 0.4, 39.1
    R.parts.add(box(x0 + t, y1 - t, MZ, x1 - t, y1, MZ + 1.0, 'iron'))
    R.parts.add(box(x0 + t, y1 - t, MZ + 2.2, x1 - t, y1, wz, 'iron'))
    R.parts.add(box(x0 + t, y1 - t, MZ + 1.0, wx0, y1, MZ + 2.2, 'iron'))
    R.parts.add(box(wx1, y1 - t, MZ + 1.0, x1 - t, y1, MZ + 2.2, 'iron'))
    for xx in (wx0 + 0.5,):
        R.parts.add(box(xx, y1 - t, MZ + 1.0, xx + 0.06, y1, MZ + 2.2, 'iron'))
    # outside: bookcases on its faces, so from the grid it looks like one more case
    sh(R, '-y', y0, x0 + 0.1, x1 - 0.1, z=MZ - 0.3, rows=7, frame='walnut')
    sh(R, '-x', x0, y0 + 0.1, y1 - 0.1, z=MZ - 0.3, rows=7, frame='walnut')
    sh(R, '+x', x1, y0 + 0.1, y1 - 0.1, z=MZ - 0.3, rows=7, frame='walnut')
    for (x, y) in ((x0 + 0.3, y0 + 0.3), (x1 - 0.3, y0 + 0.3), (x0 + 0.3, y1 - 0.3), (x1 - 0.3, y1 - 0.3)):
        R.nocol.add(box(x - 0.03, y - 0.03, MZ - 0.3, x + 0.03, y + 0.03, Z - 0.3, 'iron'))
    # the steep stair from the hatch
    n = 14
    rise = (Z - MZ) / n; run = 0.29
    fy = HY1 - n * run
    R.flight(HX0 + 0.02, fy, MZ, HX1 - HX0 - 0.04, n, rise, run, '+y', m='iron', side='iron')
    stair_rail(R, HX0 + 0.04, fy + run, MZ + rise, HX0 + 0.04, HY1 - 0.3, Z - 0.3 * rise / run, m='iron')
    stair_rail(R, HX1 - 0.04, fy + run, MZ + rise, HX1 - 0.04, HY1 - 0.3, Z - 0.3 * rise / run, m='iron')
    # inside: a workbench, a rack of spare rail, a cot, a kettle, a lamp, the logbook
    table(R, x1 - 1.0, y0 + 0.3, x1 - 0.2, y0 + 2.4, z=MZ, h=0.9, m='oak')
    open_book(R, x1 - 0.6, y0 + 1.0, MZ + 0.9, 1.57)
    R.parts.add(cyl(x1 - 0.5, y0 + 1.9, MZ + 0.9, MZ + 1.1, 0.09, 10, side='iron', top='iron'))
    chair(R, x1 - 0.6, 24.45, -math.pi / 2, z=MZ, frame='oak', seat='oak')
    for k in range(6):
        R.nocol.add(box(x0 + t, y1 - 2.4, MZ + 1.2 + 0.2 * k, x0 + t + 0.06, y1 - 0.4, MZ + 1.24 + 0.2 * k, 'brass'))
    R.parts.add(box(x0 + t + 0.02, y0 + 0.2, MZ, x0 + t + 0.85, y0 + 2.1, MZ + 0.42, 'bed'))
    R.parts.add(box(x0 + t + 0.02, y0 + 0.2, MZ + 0.42, x0 + t + 0.85, y0 + 0.6, MZ + 0.54, 'ivory'))
    R.spot('bed', x0 + 0.55, y0 + 1.1, MZ + 0.42, math.pi / 2)
    bulb(R, 38.5, 25.4, Z - 1.0, r=0.1, m='e_lamp', top=Z - 0.3, shade='green')
    R.light(sphere(x1 - 0.3, y1 - 0.4, MZ + 1.6, 0.06, 8, 4, 'e_candle'))
    R.spot('plaque', x1 - 0.13, 25.2, MZ + 1.5, math.pi, text='CATWALK INSPECTION. Rails: sound. Hangers: sound. Floor: see below.')


def books(R):
    """Books all the way down the walls, and round the walkway above the doors."""
    wall_cases(R, z=Z, rows=12, frame='walnut')
    for z in (-1.9, 3.0):
        wall_cases(R, z=z, rows=11 if z < 0 else 10, frame='walnut', full=True)


def lamps(R):
    for cx in G:
        for cy in G:
            pendant(R, cx, cy, Z + 3.0, 15.2, r=0.34, m='e_lamp')
    for c in (16.0, 32.0, 48.0):
        for (x, y) in ((c, 1.0), (c, D - 1.0), (1.0, c), (W - 1.0, c)):
            if y < 2 or y > D - 2: y = PE - 0.06 if y < 2 else D - PE + 0.06
            else: x = PE - 0.06 if x < 2 else W - PE + 0.06
            green_standard(R, x, y, Z + 1.0, h=0.8)
    rnd = random.Random(68)
    for k in range(10):
        x, y = rnd.uniform(12, 52), rnd.uniform(12, 52)
        if min(abs(x - c) for c in G) < 3 or min(abs(y - c) for c in G) < 3: continue
        R.nocol.add(cyl(x, y, 1.5, 15.2, 0.012, 4, side='iron', caps=False))
        R.light(sphere(x, y, 1.3, 0.2, 8, 4, 'e_amber'))


def nav(R):
    ids = {}
    for cx in G:
        for cy in G:
            if (cx, cy) == (MX, MY): continue
            ids[(cx, cy)] = R.navpt(cx, cy, Z)
    for cx in G:
        col = [ids[(cx, cy)] for cy in G if (cx, cy) in ids]
        R.link(*col)
    for cy in G:
        row = [ids[(cx, cy)] for cx in G if (cx, cy) in ids]
        if cy == MY:
            R.link(row[0], row[1]); continue
        R.link(*row)
    e = 1.35
    per = navloop(R, [(e, e), (W - e, e), (W - e, D - e), (e, D - e)], z=Z)
    for c in G:
        a = R.navpt(e, c, Z); R.link(a, ids[(G[0], c)]) if (G[0], c) in ids else None
        b = R.navpt(c, e, Z); R.link(b, ids[(c, G[0])])
