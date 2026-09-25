"""The Fog Maze: a labyrinth of tall bookcases standing in a fog so thick the far end of any aisle is a
rumour. Green lamps on the stacks, wet stone underfoot, and over the middle of the maze a glow in the
ceiling that you can never quite walk towards. One dead end is not a dead end: its back is a false
bookcase, and behind it is the lit room at the centre."""
from kit_h3 import *

W = D = 32.0
S = 3.2                      # maze cell (doorways fall on cell centres: 8 and 24 are the 3rd and 8th)
N = 10
ROWS = 12
CENTRE = {(4, 4), (4, 5), (5, 4), (5, 5)}
H = 7.5


def maze(seed):
    rnd = random.Random(seed)
    cells = [(i, j) for i in range(N) for j in range(N) if (i, j) not in CENTRE]
    open_ = set()
    start = (0, 0); seen = {start}; st = [start]
    while st:
        c = st[-1]
        nb = [(c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        nb = [n for n in nb if 0 <= n[0] < N and 0 <= n[1] < N and n not in CENTRE and n not in seen]
        if not nb: st.pop(); continue
        n = rnd.choice(nb); seen.add(n); st.append(n); open_.add(frozenset((c, n)))
    # a few loops, so it is a maze and not only a tree
    extra = 0
    while extra < 9:
        c = rnd.choice(cells); dx, dy = rnd.choice(((1, 0), (0, 1)))
        n = (c[0] + dx, c[1] + dy)
        if n[0] >= N or n[1] >= N or n in CENTRE: continue
        e = frozenset((c, n))
        if e in open_: continue
        open_.add(e); extra += 1
    # the doorway cells: open straight in from each doorway
    for (c, n) in (((2, 0), (2, 1)), ((7, 0), (7, 1)), ((2, 9), (2, 8)), ((7, 9), (7, 8)),
                   ((0, 2), (1, 2)), ((0, 7), (1, 7)), ((9, 2), (8, 2)), ((9, 7), (8, 7))):
        open_.add(frozenset((c, n)))
    return open_


def degree(open_, c):
    return sum(1 for e in open_ if c in e)


def pick(seed=0):
    """A maze with a dead end next to the centre, whose back wall faces the centre room."""
    while True:
        o = maze(seed)
        for (c, inner) in (((3, 4), (4, 4)), ((3, 5), (4, 5)), ((6, 4), (5, 4)), ((6, 5), (5, 5)),
                           ((4, 3), (4, 4)), ((5, 3), (5, 4)), ((4, 6), (4, 5)), ((5, 6), (5, 5))):
            if degree(o, c) == 1: return o, c, inner
        seed += 1


def make():
    R = Room('fogmaze', 2, 2, res=2048)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='slate', top='slate'))
    open_, dead, inner = pick(3)
    walls = []                                   # (x0, y0, x1, y1, ghost)
    posts = set()
    for i in range(N):
        for j in range(N):
            for (dx, dy) in ((1, 0), (0, 1)):
                n = (i + dx, j + dy)
                if n[0] >= N or n[1] >= N: continue
                c = (i, j)
                if c in CENTRE and n in CENTRE: continue
                if frozenset((c, n)) in open_: continue
                ghost = {c, n} == {dead, inner}
                if dx: x0 = x1 = (i + 1) * S; y0, y1 = j * S, (j + 1) * S
                else: y0 = y1 = (j + 1) * S; x0, x1 = i * S, (i + 1) * S
                walls.append((x0, y0, x1, y1, ghost))
                posts.add((x0, y0)); posts.add((x1, y1))
    k = 0
    for (x0, y0, x1, y1, ghost) in walls:
        if x0 == x1:
            stack(R, 'y', x0, y0 + 0.36, y1 - 0.36, rows=ROWS, frame='walnut', solid=not ghost)
        else:
            stack(R, 'x', y0, x0 + 0.36, x1 - 0.36, rows=ROWS, frame='walnut', solid=not ghost)
        k += 1
    hh = ROWS * 0.42 + 0.2
    for (x, y) in posts:
        if x in (0, W) or y in (0, D): continue
        R.parts.add(box(x - 0.36, y - 0.36, 0, x + 0.36, y + 0.36, hh + 0.35, 'walnut', skip=('-z',)))
        R.parts.add(box(x - 0.42, y - 0.42, hh + 0.35, x + 0.42, y + 0.42, hh + 0.5, 'walnut'))
    # the room's own walls: books, except at the doorways
    for side in 'SNWE':
        for c in range(N):
            ctr = c * S + S / 2
            if abs(ctr - 8) < 1 or abs(ctr - 24) < 1: continue
            a, b = c * S + (0.4 if c == 0 else 0.36), (c + 1) * S - (0.4 if c == N - 1 else 0.36)
            if side == 'S': sh(R, '+y', T, a, b, rows=ROWS, frame='walnut')
            elif side == 'N': sh(R, '-y', D - T, a, b, rows=ROWS, frame='walnut')
            elif side == 'W': sh(R, '+x', T, a, b, rows=ROWS, frame='walnut')
            else: sh(R, '-x', W - T, a, b, rows=ROWS, frame='walnut')
    lamps(R, walls, open_)
    centre(R, dead, inner)
    fx(R, 'fog', [T, T, 0, W - T, D - T, H], density=0.09)
    # walking graph: the maze itself
    ids = {}
    for i in range(N):
        for j in range(N):
            if (i, j) in CENTRE: continue
            ids[(i, j)] = R.navpt(i * S + S / 2, j * S + S / 2)
    for e in open_:
        a, b = tuple(e)
        if a in ids and b in ids: R.link(ids[a], ids[b])
    R.link(ids[dead], R._inner_nav)
    secret(R, 16.0, 16.0, 0.0, 'The Room in the Middle',
           'The fog stops at the false bookcase as if it were a wall. Inside it is bright and dry and perfectly still, and there is a desk with a map of the maze on it, drawn by someone who never finished.')
    return finish(R, 'The Fog Maze', weight=4, probe=(8.0, 8.0, 1.8), top=H,
                  blurb='The stacks go up into fog and the aisles go off into fog. Somewhere in the middle there is a light. There is always a light in the middle.')


def lamps(R, walls, open_):
    """Green-shaded lamps on some stack faces, a few amber night-lamps, dim bulbs high in the fog."""
    rnd = random.Random(4)
    k = 0
    for (x0, y0, x1, y1, ghost) in walls:
        k += 1
        if ghost or k % 3: continue
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        s = rnd.choice((-1, 1))
        if x0 == x1: lx, ly, dx, dy = mx + s * 0.42, my, s, 0
        else: lx, ly, dx, dy = mx, my + s * 0.42, 0, s
        if not (0.8 < lx < W - 0.8 and 0.8 < ly < D - 0.8): continue
        z = 2.3
        R.nocol.add(obox(lx - dx * 0.1, ly - dy * 0.1, lx + dx * 0.25, ly + dy * 0.25, z + 0.3, z + 0.34, 0.03, 'brass'))
        R.nocol.add(frustum(lx + dx * 0.25, ly + dy * 0.25, z, z + 0.22, 0.2, 0.07, 10, 'green', inner='ivory'))
        R.light(cyl(lx + dx * 0.25, ly + dy * 0.25, z + 0.03, z + 0.07, 0.12, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    for (x, y) in ((8.0, 1.6), (24.0, D - 1.6), (1.6, 24.0), (W - 1.6, 8.0), (8.0, 20.8), (27.2, 17.6)):
        R.nocol.add(cyl(x, y, 0, 1.2, 0.02, 6, side='brass', caps=False))
        R.light(sphere(x, y, 1.3, 0.09, 10, 5, 'e_amber'))
    for i in range(0, N, 2):
        for j in range(1, N, 2):
            x, y = i * S + S / 2 + (S if j % 4 == 1 else 0), j * S + S / 2
            if x > W - 1 or (12.8 < x < 19.2 and 12.8 < y < 19.2): continue
            bulb(R, x, y, 6.2, r=0.13, m='e_dim', top=H)


def centre(R, dead, inner):
    """The lit room: four cells walled with books on every side, a bright ceiling over it."""
    x0, y0, x1, y1 = 4 * S + 0.36, 4 * S + 0.36, 6 * S - 0.36, 6 * S - 0.36
    R.light(box(x0 + 0.6, y0 + 0.6, H - 0.03, x1 - 0.6, y1 - 0.6, H - 0.01, 'e_panel', skip=('+z',)))
    R.parts.add(box(x0, y0, 0, x1, y1, 0.02, 'carpet'))
    R.parts.add(box(x0 + 0.5, y0 + 0.5, 0.02, x1 - 0.5, y1 - 0.5, 0.03, 'oxblood'))
    # a desk with the unfinished map, a chair, a globe of a lamp, armchairs
    R.parts.add(table(14.8, 15.3, 17.2, 16.7, 0.78, 'walnut', top='leather'))
    R.nocol.add(box(15.1, 15.5, 0.78, 16.9, 16.5, 0.785, 'ivory'))
    for k in range(9):
        a = k * 0.7
        R.nocol.add(box(15.2 + (k % 3) * 0.55, 15.6 + (k // 3) * 0.3, 0.785, 15.25 + (k % 3) * 0.55 + 0.3 * abs(math.cos(a)), 15.62 + (k // 3) * 0.3, 0.788, 'black'))
    desk_lamp(R, 16.9, 16.4, 0.78)
    candle(R, 15.0, 16.5, 0.78, h=0.15)
    R.parts.add(chair(16.0, 14.8, math.pi / 2))
    R.spot('sit', 16.0, 14.8, 0.48, math.pi / 2)
    R.spot('read', 16.0, 16.0, 0.78, math.pi / 2)
    armchair(R, 13.6, 18.2, -0.6)
    armchair(R, 18.4, 18.2, math.pi + 0.6)
    floor_lamp(R, 16.0, 18.6, 1.7)
    R.spot('plaque', 16.0, y0 + 0.4, 1.6, math.pi / 2, text='YOU ARE HERE')
    # a trail of chalk marks on the floor from the false case to the desk
    ix, iy = inner[0] * S + S / 2, inner[1] * S + S / 2
    dx, dy = dead[0] - inner[0], dead[1] - inner[1]
    for k in range(5):
        t = (k + 0.5) / 5
        px, py = ix + dx * S * 0.45 * (1 - t) + (16 - ix) * t * 0.6, iy + dy * S * 0.45 * (1 - t) + (16 - iy) * t * 0.6
        R.nocol.add(box(px - 0.12, py - 0.02, 0.03, px + 0.12, py + 0.02, 0.034, 'ivory'))
    a, b = R.navpt(ix, iy), R.navpt(16.0, 17.6)
    R.link(a, b)
    R._inner_nav = a
