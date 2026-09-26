"""The Hanging Library: a dark hall two floors deep, and in it tall bookcases hang on chains from the
ceiling at different heights, their tops railed like little decks. Planks with iron rails run between
them from the gallery round the walls, up and down, a walk through the air. Some cases, out of reach,
sway very slightly. One pair of cases stands less than a metre apart with nothing between: jump it if you
like (there is a net). The tallest case of all has no plank to it; the way up is a ladder on its hidden
side, and on its top someone has made a reading nook."""
from kit_h7 import *

W = D = 64.0
UP = LH
LE = 4.6                       # the gallery's inner edge (from the walls)
PW = 1.3                       # plank width

# the cases you can walk on: name -> (cx, cy, half size, top z, height)
CASES = {
    'c1': (20.25, 14.25, 1.5, 8.0, 5.0),
    'c2': (32.25, 14.25, 1.5, 8.6, 6.0),
    'c3': (32.25, 26.25, 1.75, 9.4, 7.0),
    'c4': (44.25, 26.25, 1.5, 9.4, 5.0),
    'c5': (20.25, 26.25, 1.5, 9.0, 5.0),
    'c6': (20.25, 40.25, 1.5, 9.8, 6.0),
    'c8': (44.25, 40.25, 1.5, 9.0, 5.0),
    'c9': (44.25, 52.25, 1.5, 8.4, 5.0),
    'top': (32.25, 40.25, 2.0, 12.6, 9.0),     # the tallest (the secret)
    'j': (21.25, 43.85, 1.2, 9.8, 2.0),        # the one you jump to
}
NET = (16.1, 41.1, 22.6, 46.4, 7.3)            # the net under the jump
LADX_NET = 19.25
BRK = (28.0, 36.3, 30.25, 45.4, 9.8)           # the bracket on the tallest case's west face (x0, y0, x1, y1, z)


def make():
    R = Room('hanginglib', 4, 4, levels=2, res=2048)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, R.hi - 0.1, 'tile', bottom='slate', top='plaster'))
    gallery(R)
    stair(R)
    for k, c in CASES.items():
        case(R, k, *c)
    planks(R)
    jump(R)
    tallest(R)
    swingers(R)
    floor(R)
    fx(R, 'dust', [LE, LE, 6.0, W - LE, D - LE, 14.0])
    fx(R, 'fog', [LE, LE, 0.0, W - LE, D - LE, 4.0], density=0.05)
    e = 2.3
    navloop(R, [(e, 6), (e, 32), (e, D - e), (32, D - e), (W - e, D - e), (W - e, 32), (W - e, e), (32, 6)])
    navloop(R, [(e, e), (32, e), (W - e, e), (W - e, 32), (W - e, D - e), (32, D - e), (e, D - e), (e, 32)], z=UP)
    return finish(R, 'The Hanging Library', weight=2, probe=(32.0, 20.0, 11.0), top=R.hi,
                  blurb='The bookcases here hang from the ceiling on chains, at every height, a long way above the floor. Planks run between them. The cases creak when you step onto them, but only a little.')


# ---------------------------------------------------------------------------
def gallery(R):
    """The gallery round the walls at the upper doors, railed at the void (with openings for the planks),
    books on its walls and under it."""
    th = 0.45
    hole = (11.5, 2.5, 17.5, LE)       # the stairwell
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, hole[0], LE), (hole[2], T - 0.02, W - T + 0.02, LE), (hole[0], T - 0.02, hole[2], hole[1]),
                             (T - 0.02, D - LE, W - T + 0.02, D - T + 0.02), (T - 0.02, LE, LE, D - LE), (W - LE, LE, W - T + 0.02, D - LE)):
        R.parts.add(box(x0, y0, UP - th, x1, y1, UP, 'tile', top='floor', bottom='plaster'))
    # rail round the gallery's edge, open where the planks leave (x or y centre of each opening)
    r_ = -0.1                  # rails stand just inside the edge (so the walk check sees them)
    opens = {'S': [20.25], 'N': [44.25], 'W': [26.25], 'E': [26.25]}
    def edge(a, b, fixed, along_x, gaps):
        p = a
        for g in sorted(gaps) + [None]:
            q = b if g is None else g - PW / 2 - 0.05
            if q - p > 0.1:
                pts = [(p, fixed), (q, fixed)] if along_x else [(fixed, p), (fixed, q)]
                rail_line(R, pts, UP, m='iron')
            if g is not None: p = g + PW / 2 + 0.05
    edge(hole[2], W - LE + r_, LE + r_, True, opens['S'])
    edge(LE - r_, hole[0], LE + r_, True, [])
    edge(LE - r_, W - LE + r_, D - LE - r_, True, opens['N'])
    edge(LE + r_, D - LE - r_, LE + r_, False, opens['W'])
    edge(LE + r_, D - LE - r_, W - LE - r_, False, opens['E'])
    # books on the walls, both levels (not where the stair runs)
    wall_cases(R, z=UP, rows=11, frame='walnut')
    wall_cases(R, rows=13, frame='walnut', sides='NWE')
    sh(R, '+y', T, 0.6, 6.2, rows=13, frame='walnut')
    sh(R, '+y', T, 25.8, 38.2, rows=13, frame='walnut')
    sh(R, '+y', T, 41.8, 54.2, rows=13, frame='walnut')
    sh(R, '+y', T, 57.8, W - 0.6, rows=13, frame='walnut')
    # lamps: little ones on the rail, dim ones under the gallery, a few hanging
    for p in (10.0, 18.0, 30.0, 38.0, 50.0, 58.0):
        for (x, y) in ((p, LE + r_), (p, D - LE - r_), (LE + r_, p), (W - LE - r_, p)):
            R.light(sphere(x, y, UP + 1.15, 0.08, 8, 4, 'e_amber'))
        for (x, y) in ((p, LE - 1.6), (p, D - LE + 1.6), (LE - 1.6, p), (W - LE + 1.6, p)):
            R.light(sphere(x, y, UP - th - 0.35, 0.12, 8, 4, 'e_dim'))
    for (x, y) in ((2.4, 2.4), (W - 2.4, 2.4), (2.4, D - 2.4), (W - 2.4, D - 2.4)):
        hanging(R, x, y, R.hi - 0.1, UP + 3.4, r=0.4, e='e_lamp', shade='green')


def stair(R):
    """Two flights against the south wall from the floor of the hall to the gallery."""
    n, rise, run = 20, 0.2, 0.3
    R.flight(11.5, 0.4, 0.0, 2.0, n, rise, run, '+x', m='tile', riser='tile', side='tile')
    R.parts.add(box(11.5, 2.4, 0.0, 17.5, LE, 4.0, 'tile', skip=('-z',)))
    R.parts.add(box(17.5, 0.4, 0.0, 20.0, LE, 4.0, 'tile', top='terrazzo', skip=('-z',)))
    R.flight(17.5, 2.6, 4.0, 2.0, n, rise, run, '-x', m='tile', riser='tile', side='tile')
    stair_rail(R, 17.2, LE - 0.05, 4.0 + rise, 12.1, LE - 0.05, UP, m='iron')
    rail_line(R, [(20.0 - 0.05, LE - 0.05), (17.5, LE - 0.05)], 4.0, m='iron')
    rail_line(R, [(20.0 - 0.05, 0.5), (20.0 - 0.05, LE - 0.05)], 4.0, m='iron')
    rail_line(R, [(12.6, 2.45), (17.5, 2.45), (17.5, LE - 0.1)], UP, m='iron')


# ---------------------------------------------------------------------------
def case(R, name, cx, cy, s, top, h):
    """A tall bookcase hanging on chains: books on all four faces, a railed deck on top."""
    z0 = top - h
    rows = max(3, int((h - 0.35) / 0.42))
    d = 0.36
    sh(R, '-y', cy - s + d, cx - s, cx + s, z=z0, rows=rows, frame='walnut')
    sh(R, '+y', cy + s - d, cx - s, cx + s, z=z0, rows=rows, frame='walnut')
    sh(R, '-x', cx - s + d, cy - s + d, cy + s - d, z=z0, rows=rows, frame='walnut')
    sh(R, '+x', cx + s - d, cy - s + d, cy + s - d, z=z0, rows=rows, frame='walnut')
    R.parts.add(box(cx - s - 0.06, cy - s - 0.06, top - 0.28, cx + s + 0.06, cy + s + 0.06, top, 'walnut', top='oak'))
    R.parts.add(box(cx - s + 0.3, cy - s + 0.3, z0 - 0.35, cx + s - 0.3, cy + s - 0.3, z0, 'walnut'))
    for (px, py) in ((cx - s + 0.12, cy - s + 0.12), (cx + s - 0.12, cy - s + 0.12), (cx - s + 0.12, cy + s - 0.12), (cx + s - 0.12, cy + s - 0.12)):
        chain(R, px, py, top + 1.0, R.hi - 0.1, link=0.32, w=0.05)
        R.nocol.add(box(px - 0.03, py - 0.03, top, px + 0.03, py + 0.03, top + 1.05, 'iron'))
    # a lantern hung under it
    if name == 'j': return
    R.nocol.add(cyl(cx, cy, z0 - 1.1, z0 - 0.35, 0.01, 4, side='iron', caps=False))
    R.light(sphere(cx, cy, z0 - 1.25, 0.14, 10, 5, 'e_amber'))
    R.nocol.add(box(cx - 0.16, cy - 0.16, z0 - 1.1, cx + 0.16, cy + 0.16, z0 - 1.05, 'iron'))


def deck_rails(R, name, opens):
    """Rails round a case's deck; opens: list of (side, centre, width) left open."""
    cx, cy, s, top, h = CASES[name]
    e = s - 0.05
    sides = {'S': ((cx - e, cy - e), (cx + e, cy - e)), 'N': ((cx - e, cy + e), (cx + e, cy + e)),
             'W': ((cx - e, cy - e), (cx - e, cy + e)), 'E': ((cx + e, cy - e), (cx + e, cy + e))}
    for sd, (a, b) in sides.items():
        along_x = sd in 'SN'
        lo, hi = (a[0], b[0]) if along_x else (a[1], b[1])
        cuts = sorted([(c - w / 2, c + w / 2) for (s2, c, w) in opens if s2 == sd])
        p = lo
        for (c0, c1) in cuts + [(None, None)]:
            q = hi if c0 is None else c0
            if q - p > 0.1:
                rail_line(R, [(p, a[1]), (q, a[1])] if along_x else [(a[0], p), (a[0], q)], top, m='iron')
            if c0 is not None: p = c1


def plank(R, ax, a0, a1, c, z0, z1):
    """A plank walk along ax ('x' or 'y') from a0 (height z0) to a1 (z1), centred on c, railed both sides."""
    w = PW
    if a1 < a0: a0, a1, z0, z1 = a1, a0, z1, z0
    R.parts.add(gsloped(ax, a0, a1, c - w / 2, c + w / 2, z0 - 0.1, z1 - 0.1, z0, z1, 'oak'))
    # cross battens under it
    n = int((a1 - a0) / 1.2)
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / max(1, n)
        z = z0 + (z1 - z0) * (a - a0) / (a1 - a0)
        g = box(a - 0.05, c - w / 2 - 0.08, z - 0.22, a + 0.05, c + w / 2 + 0.08, z - 0.1, 'walnut') if ax == 'x' else box(c - w / 2 - 0.08, a - 0.05, z - 0.22, c + w / 2 + 0.08, a + 0.05, z - 0.1, 'walnut')
        R.nocol.add(g)
    for s in (-1, 1):
        cc = c + s * (w / 2 - 0.04)
        if ax == 'x': stair_rail(R, a0, cc, z0, a1, cc, z1, m='iron', post=1.2)
        else: stair_rail(R, cc, a0, z0, cc, a1, z1, m='iron', post=1.2)
    # a small lamp at its middle
    am = (a0 + a1) / 2; zm = (z0 + z1) / 2
    x, y = (am, c + w / 2 - 0.04) if ax == 'x' else (c + w / 2 - 0.04, am)
    R.light(sphere(x, y, zm + 1.12, 0.06, 6, 3, 'e_candle'))


def gsloped(ax, a0, a1, c0, c1, zb0, zb1, zt0, zt1, m):
    from kit_g import sloped
    return sloped(ax, a0, a1, c0, c1, zb0, zb1, zt0, zt1, m)


def planks(R):
    C = CASES
    def face(n, sd):
        cx, cy, s, top, h = C[n]
        return {'S': cy - s, 'N': cy + s, 'W': cx - s, 'E': cx + s}[sd]
    P = [
        # (axis, a0, a1, centre, z0, z1, (case, side) at a0, (case, side) at a1)
        ('y', LE, face('c1', 'S'), 20.25, UP, C['c1'][3], None, ('c1', 'S')),
        ('x', face('c1', 'E'), face('c2', 'W'), 14.25, C['c1'][3], C['c2'][3], ('c1', 'E'), ('c2', 'W')),
        ('y', face('c2', 'N'), face('c3', 'S'), 32.25, C['c2'][3], C['c3'][3], ('c2', 'N'), ('c3', 'S')),
        ('x', face('c3', 'E'), face('c4', 'W'), 26.25, C['c3'][3], C['c4'][3], ('c3', 'E'), ('c4', 'W')),
        ('x', face('c4', 'E'), W - LE, 26.25, C['c4'][3], UP, ('c4', 'E'), None),
        ('x', face('c5', 'E'), face('c3', 'W'), 26.25, C['c5'][3], C['c3'][3], ('c5', 'E'), ('c3', 'W')),
        ('x', LE, face('c5', 'W'), 26.25, UP, C['c5'][3], None, ('c5', 'W')),
        ('y', face('c5', 'N'), face('c6', 'S'), 20.25, C['c5'][3], C['c6'][3], ('c5', 'N'), ('c6', 'S')),
        ('y', face('c4', 'N'), face('c8', 'S'), 44.25, C['c4'][3], C['c8'][3], ('c4', 'N'), ('c8', 'S')),
        ('y', face('c8', 'N'), face('c9', 'S'), 44.25, C['c8'][3], C['c9'][3], ('c8', 'N'), ('c9', 'S')),
        ('y', face('c9', 'N'), D - LE, 44.25, C['c9'][3], UP, ('c9', 'N'), None),
        # from c6 east to the bracket on the tallest case
        ('x', face('c6', 'E'), BRK[0], 40.25, C['c6'][3], BRK[4], ('c6', 'E'), None),
    ]
    opens = {k: [] for k in C}
    for (ax, a0, a1, c, z0, z1, ea, eb) in P:
        plank(R, ax, a0, a1, c, z0, z1)
        for e in (ea, eb):
            if e: opens[e[0]].append((e[1], c, PW + 0.1))
    opens['c6'].append(('N', 20.25, 3.2))      # the jump (and the ladder up from the net)
    for k in C:
        if k in ('top', 'j'): continue
        deck_rails(R, k, opens[k])
    # things on the decks: a green lamp standard on each, a chair here and there, books
    rnd = rng(61)
    for k in ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c8', 'c9'):
        cx, cy, s, top, h = C[k]
        lamp_post(R, cx + s - 0.35, cy + s - 0.35, z=top, h=1.7)
        if rnd.random() < 0.6:
            R.parts.add(chair(cx - 0.5, cy - 0.4, rnd.uniform(0, 6.28)).xform(0, 0, 0, top))
        book_pile(R, cx + 0.3, cy - s + 0.45, top, rnd.randint(3, 7), seed=rnd.randint(0, 99))


def jump(R):
    """The jump: c6 to the small case 'j', under a metre apart. A net below catches the unlucky; a ladder
    goes from the net back up onto c6."""
    x0, y0, x1, y1, z = NET
    R.parts.add(box(x0, y0, z - 0.08, x1, y1, z, 'oak'))
    for k in range(int((x1 - x0) / 0.3)):
        x = x0 + 0.15 + k * 0.3
        R.nocol.add(box(x - 0.015, y0, z, x + 0.015, y1, z + 0.02, 'leather'))
    for k in range(int((y1 - y0) / 0.3)):
        y = y0 + 0.15 + k * 0.3
        R.nocol.add(box(x0, y - 0.015, z, x1, y + 0.015, z + 0.02, 'leather'))
    rail_line(R, [(x0 + 0.05, y0 + 0.05), (x0 + 0.05, y1 - 0.05), (x1 - 0.05, y1 - 0.05), (x1 - 0.05, y0 + 0.05), (x0 + 0.05, y0 + 0.05)], z, m='iron')
    for (px, py) in ((x0 + 0.05, y0 + 0.05), (x1 - 0.05, y0 + 0.05), (x0 + 0.05, y1 - 0.05), (x1 - 0.05, y1 - 0.05)):
        R.nocol.add(beam((px, py, z + 1.0), (px, py, R.hi - 0.1), 0.03, 'iron'))
    c6 = CASES['c6']
    ladder_up(R, LADX_NET, c6[1] + c6[2] + (c6[3] - z), z, c6[3], '-y', w=1.0, m='oak', rail='iron', ang=math.radians(45))
    # on the far case: a lamp, a stool, a note
    cx, cy, s, top, h = CASES['j']
    lamp_post(R, cx + s - 0.3, cy + s - 0.3, z=top, h=1.5)
    R.parts.add(box(cx - 0.2, cy - 0.2, top, cx + 0.2, cy + 0.2, top + 0.45, 'walnut'))
    open_book(R, cx + 0.3, cy + 0.3, top, 0.7)
    R.spot('plaque', cx, cy + s - 0.1, top + 1.2, -math.pi / 2, text='WELL JUMPED. THE WAY BACK IS THE SAME, ONLY BACKWARDS.')


def tallest(R):
    """The tallest case, standing far higher than the rest. A plank from c6 ends at a bracket on its west
    face, and the ladder up from the bracket is on the side you cannot see from the planks. On top: a
    reading nook under a little canopy."""
    x0, y0, x1, y1, z = BRK
    R.parts.add(box(x0, y0, z - 0.2, x1, y1, z, 'oak', bottom='walnut', sides='walnut'))
    for (bx, by) in ((x0 + 0.2, y0 + 0.3), (x0 + 0.2, y1 - 0.3)):
        R.nocol.add(beam((bx, by, z - 0.2), (x1, by, z - 1.3), 0.08, 'iron'))
    cx, cy, s, top, h = CASES['top']
    # rails: the bracket's outer edge and ends (open where the plank arrives, and at the ladder's foot)
    rail_line(R, [(x0 + 0.05, y0 + 0.05), (x0 + 0.05, 39.5)], z, m='iron')
    rail_line(R, [(x0 + 0.05, 41.0), (x0 + 0.05, y1 - 0.05), (x1, y1 - 0.05)], z, m='iron')
    rail_line(R, [(x0 + 0.05, y0 + 0.05), (x1, y0 + 0.05)], z, m='iron')
    rail_line(R, [(x1 - 0.05, y0 + 0.05), (x1 - 0.05, CASES['top'][1] - CASES['top'][2])], z, m='iron')
    rail_line(R, [(x1 - 0.05, 44.0), (x1 - 0.05, y1 - 0.05)], z, m='iron')
    # the ladder climbs -y along the face, from the bracket's north end up to the top's west edge;
    # a walk beside it on the bracket leads round to its foot
    L = top - z
    yf = 41.2 + L
    ladder_up(R, 29.75, yf, z, top, '-y', w=1.0, m='oak', rail='iron', ang=math.radians(45))
    # a landing at the top of the ladder, joined to the deck
    R.parts.add(box(29.2, 39.9, top - 0.2, cx - s + 0.1, 41.25, top, 'oak', bottom='walnut', sides='walnut'))
    rail_line(R, [(29.25, 41.2), (29.25, 39.95), (cx - s, 39.95)], top, m='iron')
    # rails round the top deck, open on the west where the landing joins
    deck_rails_top(R, cx, cy, s, top, (39.9, 41.25))
    # the nook: an armchair, a lamp, a little table, a rug, books, a canopy on posts
    armchair(R, cx + 0.6, cy + 0.6, -3 * math.pi / 4, m='velvet', z=top)
    R.parts.add(cyl(cx - 0.4, cy + 1.1, top, top + 0.6, 0.25, 12, side='walnut', top='walnut'))
    desk_lamp(R, cx - 0.4, cy + 1.1, top + 0.6)
    book_pile(R, cx + 1.2, cy - 0.9, top, 8, seed=9)
    open_book(R, cx - 0.35, cy + 1.0, top + 0.6, 0.4)
    rug(R, cx - 1.2, cy - 1.0, cx + 1.4, cy + 1.4, top)
    for (px, py) in ((cx - s + 0.2, cy - s + 0.2), (cx + s - 0.2, cy - s + 0.2), (cx - s + 0.2, cy + s - 0.2), (cx + s - 0.2, cy + s - 0.2)):
        R.parts.add(box(px - 0.05, py - 0.05, top, px + 0.05, py + 0.05, top + 2.3, 'walnut'))
    R.parts.add(box(cx - s, cy - s, top + 2.3, cx + s, cy + s, top + 2.42, 'walnut'))
    R.nocol.add(box(cx - s - 0.1, cy - s - 0.1, top + 2.42, cx + s + 0.1, cy + s + 0.1, top + 2.5, 'velvet'))
    R.light(sphere(cx, cy, top + 2.1, 0.12, 10, 5, 'e_candle'))
    R.spot('plaque', cx + s - 0.1, cy, top + 1.2, math.pi, text='THE HIGHEST SHELF. PLEASE RETURN BOOKS TO THE FLOOR, EVENTUALLY.')
    secret(R, cx, cy, top, 'The Top of the Tallest Case',
           'No plank reaches it; the ladder is round the back. On top, far above everything, an armchair, a lamp and a stack of books someone carried up one at a time.', r=2.0)


def deck_rails_top(R, cx, cy, s, top, gap):
    e = s - 0.05
    rail_line(R, [(cx - e, cy - e), (cx + e, cy - e), (cx + e, cy + e), (cx - e, cy + e), (cx - e, gap[1] + 0.05)], top, m='iron')
    if gap[0] - 0.05 > cy - e:
        rail_line(R, [(cx - e, gap[0] - 0.05), (cx - e, cy - e)], top, m='iron')


def swingers(R):
    """Cases out of reach, deep in the dark, that sway very slightly on their chains (drawn only)."""
    rnd = rng(611)
    spots = [(10, 40, 12.0, 6), (12, 50, 10.5, 5), (26, 52, 13.0, 7), (36, 54, 9.5, 4), (54, 44, 12.5, 6), (54, 14, 11.0, 5),
             (40, 8, 12.8, 6), (8, 14, 10.0, 4), (26, 34, 13.5, 5), (38, 33, 11.5, 4), (52, 34, 13.0, 5), (14, 33, 12.2, 4), (27, 8, 13.4, 5)]
    for (x, y, top, h) in spots:
        s = rnd.uniform(0.9, 1.4)
        M = R.mover('swing', pivot=(x, y, R.hi - 0.1), axis=rnd.choice(('x', 'y')), amp=round(rnd.uniform(0.012, 0.03), 3),
                    period=round(rnd.uniform(9, 15), 1), phase=round(rnd.random(), 2))
        g = Geo()
        z0 = top - h
        g.add(box(x - s, y - s, top - 0.2, x + s, y + s, top, 'walnut'))
        g.add(box(x - s + 0.2, y - s + 0.2, z0 - 0.3, x + s - 0.2, y + s - 0.2, z0, 'walnut'))
        for (px, py) in ((x - s, y - s), (x + s, y - s), (x - s, y + s), (x + s, y + s)):
            g.add(box(px - 0.05, py - 0.05, z0, px + 0.05, py + 0.05, top, 'walnut'))
        rows = int((h - 0.3) / 0.45)
        for r in range(rows):
            zb = z0 + 0.1 + r * 0.45
            g.add(box(x - s, y - s, zb - 0.03, x + s, y + s, zb, 'walnut'))
            for (fa, fb, along) in (((y - s), -1, 'x'), ((y + s), 1, 'x'), ((x - s), -1, 'y'), ((x + s), 1, 'y')):
                p = -s + 0.08
                while p < s - 0.1:
                    wbk = rnd.uniform(0.5, 1.0)
                    hb = rnd.uniform(0.26, 0.38)
                    m = rnd.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet', 'ivory', 'bronze'))
                    q = min(p + wbk, s - 0.08)
                    if along == 'x': g.add(box(x + p, fa - 0.02 * fb - (0.24 if fb > 0 else 0), zb, x + q, fa - 0.02 * fb + (0.24 if fb < 0 else 0), zb + hb, m, skip=('-z',)))
                    else: g.add(box(fa - 0.02 * fb - (0.24 if fb > 0 else 0), y + p, zb, fa - 0.02 * fb + (0.24 if fb < 0 else 0), y + q, zb + hb, m, skip=('-z',)))
                    p = q + 0.01
        for (px, py) in ((x - s + 0.1, y - s + 0.1), (x + s - 0.1, y + s - 0.1), (x - s + 0.1, y + s - 0.1), (x + s - 0.1, y - s + 0.1)):
            g.add(box(px - 0.025, py - 0.006, top, px + 0.025, py + 0.006, R.hi - 0.1, 'iron'))
        M.nocol.add(g)


def floor(R):
    """The floor of the hall, far below: dark slate, fallen books, a few lamps."""
    rnd = rng(62)
    g = Geo()
    for k in range(600):
        x, y = rnd.uniform(LE + 1, W - LE - 1), rnd.uniform(LE + 1, D - LE - 1)
        book_scatter(g, x, y, 0.0, rnd, 1, spread=0.0, tilt=0.2)
    R.nocol.add(g)
    for (x, y) in ((16, 20), (40, 18), (28, 46), (48, 48), (12, 44)):
        lamppost(R, x, y, h=2.6, e='e_candle', r=0.12)
