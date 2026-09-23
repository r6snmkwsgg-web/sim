"""The Labyrinth: low rooms of green damask and red carpet, lamps set into the ceiling, and a maze
of walls that goes on a little too long. Bookcases on half the walls."""
from lib import *
import random


def make():
    R = Room('backrooms', 2, 2, res=2048)
    H = 3.1
    R.sockets(floor='carpet', wall='paper', rect=3.0)
    W = R.W
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, H, 'paper', bottom='carpet', top='ceiltile'))
    rnd = random.Random(1297)
    N = 8                       # 4 m blocks
    # walls on interior grid edges: v[(i, j)] is the wall on x = 4i between y = 4j and 4j + 4; h[(i, j)] on y = 4j
    v = {(i, j): rnd.random() < 0.34 for i in range(1, N) for j in range(N)}
    h = {(i, j): rnd.random() < 0.34 for i in range(N) for j in range(1, N)}
    for (i, j) in ((2, 0), (2, N - 1), (6, 0), (6, N - 1)): v[(i, j)] = False      # keep door approaches clear
    for (i, j) in ((0, 2), (N - 1, 2), (0, 6), (N - 1, 6)): h[(i, j)] = False
    def nbrs(a):
        i, j = a
        if i > 0 and not v[(i, j)]: yield (i - 1, j)
        if i < N - 1 and not v[(i + 1, j)]: yield (i + 1, j)
        if j > 0 and not h[(i, j)]: yield (i, j - 1)
        if j < N - 1 and not h[(i, j + 1)]: yield (i, j + 1)
    while True:
        seen = {(0, 0)}; st = [(0, 0)]
        while st:
            a = st.pop()
            for b in nbrs(a):
                if b not in seen: seen.add(b); st.append(b)
        if len(seen) == N * N: break
        # open a wall between the reached region and the rest
        cands = []
        for (i, j) in seen:
            if i < N - 1 and (i + 1, j) not in seen and v[(i + 1, j)]: cands.append(('v', i + 1, j))
            if j < N - 1 and (i, j + 1) not in seen and h[(i, j + 1)]: cands.append(('h', i, j + 1))
            if i > 0 and (i - 1, j) not in seen and v[(i, j)]: cands.append(('v', i, j))
            if j > 0 and (i, j - 1) not in seen and h[(i, j)]: cands.append(('h', i, j))
        k, i, j = rnd.choice(cands)
        (v if k == 'v' else h)[(i, j)] = False
    t = 0.1
    faces = []
    for (i, j), on in v.items():
        if not on: continue
        x = i * 4.0; y0, y1 = j * 4.0 - t, j * 4.0 + 4 + t
        y0, y1 = max(y0, T), min(y1, W - T)
        R.parts.add(box(x - t, y0, 0, x + t, y1, H, 'paper', skip=('-z', '+z')))
        faces.append(('v', x, y0, y1))
    for (i, j), on in h.items():
        if not on: continue
        y = j * 4.0; x0, x1 = i * 4.0 - t, i * 4.0 + 4 + t
        x0, x1 = max(x0, T), min(x1, W - T)
        R.parts.add(box(x0, y - t, 0, x1, y + t, H, 'paper', skip=('-z', '+z')))
        faces.append(('h', y, x0, x1))
    # bookcases on some wall faces
    for f in faces:
        if rnd.random() < 0.45:
            k, c, a, b = f
            side = rnd.random() < 0.5
            a, b = a + 0.35, b - 0.35
            if k == 'v':
                if side: R.shelf(c + t, b, 0, b - a, '+x', rows=5, frame='oak', row_h=0.4)
                else:    R.shelf(c - t, a, 0, b - a, '-x', rows=5, frame='oak', row_h=0.4)
            else:
                if side: R.shelf(a, c + t, 0, b - a, '+y', rows=5, frame='oak', row_h=0.4)
                else:    R.shelf(b, c - t, 0, b - a, '-y', rows=5, frame='oak', row_h=0.4)
    # a few against the outer walls too
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        if rnd.random() < 0.6: R.shelf(a, T, 0, b - a, '+y', rows=5, frame='oak', row_h=0.4)
        if rnd.random() < 0.6: R.shelf(b, W - T, 0, b - a, '-y', rows=5, frame='oak', row_h=0.4)
    # ceiling lamps on a 2.4 m grid, a few dead
    x = 1.6
    while x < W - 1:
        y = 1.6
        while y < W - 1:
            if rnd.random() < 0.8:
                R.light(box(x - 0.6, y - 0.3, H - 0.03, x + 0.6, y + 0.3, H - 0.01, 'e_fluor'))
            y += 2.4
        x += 2.4
    # walkers: block centres, linked where there is no wall
    ids = {(i, j): R.navpt(i * 4 + 2, j * 4 + 2) for i in range(N) for j in range(N)}
    for (i, j) in ids:
        for b in nbrs((i, j)):
            if b > (i, j): R.link(ids[(i, j)], ids[b])
    R.spot('probe', 14, 14, 1.6)
    R.meta['label'] = 'The Labyrinth'
    R.meta['box'] = [[T, 0, T], [W - T, H, W - T]]
    return R
