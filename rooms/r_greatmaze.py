"""The Great Maze: a true labyrinth of bookcase walls three metres high and a metre thick, with
corridors two metres wide between them and square lamps overhead. Every doorway connects to every
other, eventually."""
from lib import *
from kit_f import *
import random


def hedge(R, a, b, c, axis, H0, rows, t=1.2, core='walnut', frame='oak', books=(True, True)):
    """A thick wall of books along axis ('x' or 'y') from a to b at cross coordinate c."""
    d = 0.34
    H = rows * 0.42 + 0.035 + 0.08
    g = Geo()
    lo = c - t / 2 + (d if books[0] else 0.0)
    hi = c + t / 2 - (d if books[1] else 0.0)
    g.add(box(a, lo, 0, b, hi, H, core, skip=('-z',)))
    for r in range(rows + 1):
        h = r * 0.42
        for side in (0, 1):
            if not books[side]: continue
            y0, y1 = (c - t / 2, lo) if side == 0 else (hi, c + t / 2)
            g.add(box(a, y0, h, b, y1, h + 0.035, frame, skip=('-z',) if r == 0 else ()))
    g.add(box(a - 0.02, c - t / 2 - 0.04, H, b + 0.02, c + t / 2 + 0.04, H + 0.1, 'walnut'))
    if axis == 'y':   # build along x then swap x and y
        g.v = [(y, x, z) for (x, y, z) in g.v]
        g.fix()
    R.parts.add(g)
    L = b - a
    for side in (0, 1):
        if not books[side]: continue
        if axis == 'x':
            if side == 0: slab_row(R, b - 0.02, c - t / 2 + d, 0, L - 0.04, -math.pi / 2, rows, 0.42, d)
            else: slab_row(R, a + 0.02, c + t / 2 - d, 0, L - 0.04, math.pi / 2, rows, 0.42, d)
        else:
            if side == 0: slab_row(R, c - t / 2 + d, a + 0.02, 0, L - 0.04, math.pi, rows, 0.42, d)
            else: slab_row(R, c + t / 2 - d, b - 0.02, 0, L - 0.04, 0.0, rows, 0.42, d)
    return H


def make():
    R = Room('greatmaze', 2, 2, res=2048)
    R.sockets(floor='floor', wall='tile')
    W, Hc = R.W, 4.4
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, Hc, 'tile', bottom='floor', top='plaster'))
    rnd = random.Random(20511)
    N, P = 10, 3.2
    # v[(i, j)]: wall on x = P*i between cells (i-1, j) and (i, j); h[(i, j)]: on y = P*j between (i, j-1) and (i, j)
    v = {(i, j): True for i in range(1, N) for j in range(N)}
    h = {(i, j): True for i in range(N) for j in range(1, N)}
    # carve a spanning tree (randomised depth-first)
    seen = {(0, 0)}; st = [(0, 0)]
    while st:
        a = st[-1]
        i, j = a
        opts = [b for b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)) if 0 <= b[0] < N and 0 <= b[1] < N and b not in seen]
        if not opts: st.pop(); continue
        b = rnd.choice(opts)
        if b[0] != i: v[(max(i, b[0]), j)] = False
        else: h[(i, max(j, b[1]))] = False
        seen.add(b); st.append(b)
    # a few loops, so it is a maze and not a tree
    ks = sorted(k for k in v if v[k]); rnd.shuffle(ks)
    for k in ks[:7]: v[k] = False
    ks = sorted(k for k in h if h[k]); rnd.shuffle(ks)
    for k in ks[:7]: h[k] = False
    # keep the doorway cells' side walls out of the doorways
    for (i, j) in ((2, 0), (3, 0), (7, 0), (8, 0), (2, N - 1), (3, N - 1), (7, N - 1), (8, N - 1)): v[(i, j)] = False
    for (i, j) in ((0, 2), (0, 3), (0, 7), (0, 8), (N - 1, 2), (N - 1, 3), (N - 1, 7), (N - 1, 8)): h[(i, j)] = False
    # posts where walls meet or end
    deg = {}
    for (i, j), on in v.items():
        if on:
            for q in ((i, j), (i, j + 1)): deg.setdefault(q, set()).add('v')
    for (i, j), on in h.items():
        if on:
            for q in ((i, j), (i + 1, j)): deg.setdefault(q, set()).add('h')
    def cnt(q):
        i, j = q
        return sum([v.get((i, j - 1), False), v.get((i, j), False), h.get((i - 1, j), False), h.get((i, j), False)])
    post = {q for q in deg if not (cnt(q) == 2 and len(deg[q]) == 1) and 0 < q[0] < N and 0 < q[1] < N}
    t = 1.2
    H = 0
    nslab0 = len(R.slabs)
    # runs of walls between posts
    for i in range(1, N):
        j = 0
        while j < N:
            if not v[(i, j)]: j += 1; continue
            j0 = j
            while j < N and v[(i, j)] and (j == j0 or (i, j) not in post): j += 1
            a, b = j0 * P, j * P
            a = a + t / 2 + 0.05 if (i, j0) in post else max(a, T)
            b = b - t / 2 - 0.05 if (i, j) in post else min(b, W - T)
            bk = (rnd.random() < 0.55, rnd.random() < 0.55)
            H = hedge(R, a, b, i * P, 'y', 0, 6, t, core='damask', books=bk)
    for j in range(1, N):
        i = 0
        while i < N:
            if not h[(i, j)]: i += 1; continue
            i0 = i
            while i < N and h[(i, j)] and (i == i0 or (i, j) not in post): i += 1
            a, b = i0 * P, i * P
            a = a + t / 2 + 0.05 if (i0, j) in post else max(a, T)
            b = b - t / 2 - 0.05 if (i, j) in post else min(b, W - T)
            bk = (rnd.random() < 0.55, rnd.random() < 0.55)
            H = hedge(R, a, b, j * P, 'x', 0, 6, t, core='damask', books=bk)
    for (i, j) in post:
        x, y = i * P, j * P
        s = t / 2 + 0.05
        R.parts.add(box(x - s, y - s, 0, x + s, y + s, H + 0.25, 'walnut', skip=('-z',)))
        R.parts.add(box(x - s - 0.06, y - s - 0.06, H + 0.25, x + s + 0.06, y + s + 0.06, H + 0.35, 'oak'))
    # books on the outer walls, here and there
    for j in range(N):
        for (side, x) in (('W', T), ('E', W - T)):
            if j in (2, 7) or rnd.random() < 0.75: continue
            a, b = j * P + 0.7, (j + 1) * P - 0.7
            if side == 'W': R.shelf(x, b, 0, b - a, '+x', rows=7, frame='oak')
            else: R.shelf(x, a, 0, b - a, '-x', rows=7, frame='oak')
    for i in range(N):
        for (side, y) in (('S', T), ('N', W - T)):
            if i in (2, 7) or rnd.random() < 0.75: continue
            a, b = i * P + 0.7, (i + 1) * P - 0.7
            if side == 'S': R.shelf(a, y, 0, b - a, '+y', rows=7, frame='oak')
            else: R.shelf(b, y, 0, b - a, '-y', rows=7, frame='oak')
    print('maze slabs', len(R.slabs) - nslab0)
    # lamps: a square panel over each cell, a few dead
    for i in range(N):
        for j in range(N):
            x, y = (i + 0.5) * P, (j + 0.5) * P
            if rnd.random() < 0.12: continue
            R.cut(box(x - 0.55, y - 0.55, Hc - 0.02, x + 0.55, y + 0.55, Hc + 0.2, 'tile', top='plaster'))
            R.light(box(x - 0.42, y - 0.42, Hc + 0.16, x + 0.42, y + 0.42, Hc + 0.18, 'e_panel'))
    # a few night lamps on posts
    for q in sorted(post)[::6]:
        x, y = q[0] * P, q[1] * P
        R.light(sphere(x, y, H + 0.55, 0.12, 8, 4, 'e_amber'))
    # walkers: the cell graph
    def nbrs(a):
        i, j = a
        if i > 0 and not v[(i, j)]: yield (i - 1, j)
        if i < N - 1 and not v[(i + 1, j)]: yield (i + 1, j)
        if j > 0 and not h[(i, j)]: yield (i, j - 1)
        if j < N - 1 and not h[(i, j + 1)]: yield (i, j + 1)
    ids = {(i, j): R.navpt((i + 0.5) * P, (j + 0.5) * P) for i in range(N) for j in range(N)}
    for a in ids:
        for b in nbrs(a):
            if b > a: R.link(ids[a], ids[b])
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Great Maze', weight=6,
                  blurb='Walls of books a little higher than you can see over. The way out is the way you came in, or one of the other seven.')
    R.meta['box'] = [[T, 0, T], [W - T, Hc, W - T]]
    return R
