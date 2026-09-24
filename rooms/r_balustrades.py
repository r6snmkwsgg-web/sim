"""The Balustrade Maze: an open marble hall filled with a maze of waist-high stone balustrades.
You can see straight across it, and the lectern in the middle, but you have to walk the long way
round (or climb over, if nobody is looking). Lamp posts stand on some of the corners."""
from lib import *
from kit_d import *
import random

BH = 0.82          # balustrade body height (the cap adds 0.08)


def rail_run(R, x0, y0, x1, y1):
    R.parts.add(box(x0, y0, 0, x1, y1, 0.12, 'slate', skip=('-z',)))
    R.parts.add(box(x0 + 0.03, y0 + 0.03, 0.12, x1 - 0.03, y1 - 0.03, BH, 'tile', skip=('-z', '+z')))
    R.parts.add(box(x0 - 0.04, y0 - 0.04, BH, x1 + 0.04, y1 + 0.04, BH + 0.08, 'tile'))


def make():
    R = Room('balustrades', 1, 1, res=1024)
    shell(R, TOP, floor='terrazzo', wall='tile', top='plaster')
    N = 7
    s = (I1 - I0) / N
    rnd = random.Random(909)
    # perfect maze by depth-first search, then a few extra openings
    v = {(i, j): True for i in range(1, N) for j in range(N)}      # wall on x = I0 + i*s between rows j
    h = {(i, j): True for i in range(N) for j in range(1, N)}      # wall on y = I0 + j*s between columns i
    seen = {(3, 3)}; st = [(3, 3)]
    while st:
        i, j = st[-1]
        nb = [(a, b) for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)) if 0 <= a < N and 0 <= b < N and (a, b) not in seen]
        if not nb: st.pop(); continue
        a, b = rnd.choice(nb)
        if a != i: v[(max(a, i), j)] = False
        else: h[(i, max(b, j))] = False
        seen.add((a, b)); st.append((a, b))
    for k in list(v):
        if v[k] and rnd.random() < 0.12: v[k] = False
    for k in list(h):
        if h[k] and rnd.random() < 0.12: h[k] = False
    # keep the doors' approaches clear
    for j in (0, N - 1):
        v[(3, j)] = v[(4, j)] = False
    for i in (0, N - 1):
        h[(i, 3)] = h[(i, 4)] = False
    t = 0.12
    for (i, j), on in v.items():
        if on:
            x = I0 + i * s
            rail_run(R, x - t, I0 + j * s + (t if j == 0 else 0), x + t, I0 + (j + 1) * s - (t if j == N - 1 else 0))
    for (i, j), on in h.items():
        if on:
            y = I0 + j * s
            rail_run(R, I0 + i * s + (t if i == 0 else 0), y - t, I0 + (i + 1) * s - (t if i == N - 1 else 0), y + t)
    # newel posts at every inner corner that has a rail, lamp posts on some
    lamps = 0
    for i in range(1, N):
        for j in range(1, N):
            n = v.get((i, j - 1), False) + v.get((i, j), False) + h.get((i - 1, j), False) + h.get((i, j), False)
            if not n: continue
            x, y = I0 + i * s, I0 + j * s
            R.parts.add(box(x - 0.2, y - 0.2, 0, x + 0.2, y + 0.2, BH + 0.2, 'tile', skip=('-z',)))
            R.parts.add(box(x - 0.24, y - 0.24, BH + 0.2, x + 0.24, y + 0.24, BH + 0.28, 'tile'))
            if (i + j) % 3 == 0:
                R.parts.add(cyl(x, y, BH + 0.28, 3.0, 0.045, 8, side='iron', caps=False))
                R.nocol.add(cyl(x, y, 3.0, 3.06, 0.14, 10, side='iron', top='iron', bottom='iron'))
                R.light(sphere(x, y, 3.25, 0.2, 10, 5, 'e_lamp'))
                lamps += 1
    # the lectern in the middle of the middle cell
    R.parts.add(box(8.5, 8.5, 0, 8.9, 8.9, 1.0, 'walnut', skip=('-z',)))
    R.parts.add(slope_box(8.35, 9.05, 8.35, 9.05, 1.0, 1.2, 1.06, 1.26, 'walnut'))
    book(R, 8.7, 8.7, 1.14, math.pi / 2, 'oxblood', open_=True)
    R.light(cyl(8.6, 8.6, TOP - 0.06, TOP - 0.03, 0.5, 16, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    R.spot('read', 7.95, 8.7, 0, 0.0)
    # bookcases round the walls, and a dim glow over the whole maze
    for (a, b) in ((0.8, 6.2), (9.8, C - 0.8)):
        for f in ('+y', '-y', '+x', '-x'):
            wall_shelf(R, f, a, b, 0, rows=10, frame='oak')
    for (x, y) in ((4, 4), (12, 4), (4, 12), (12, 12)):
        R.light(box(x - 1.2, y - 1.2, TOP - 0.06, x + 1.2, y + 1.2, TOP - 0.05, 'e_dim', skip=('+z', '-x', '+x', '-y', '+y')))
    # night: amber lights on the walls
    for p in (3.0, 13.0):
        for (x, y) in ((p, I0 + 0.05), (p, I1 - 0.05), (I0 + 0.05, p), (I1 - 0.05, p)):
            R.light(cyl(x, y, 4.8, 5.0, 0.08, 8, side='e_amber', top='e_amber', bottom='e_amber'))
    # walkers: the cell centres, linked where there is no rail
    c = lambda i, j: (I0 + (i + 0.5) * s, I0 + (j + 0.5) * s)
    ids = {(i, j): R.navpt(*c(i, j)) for i in range(N) for j in range(N)}
    for i in range(N):
        for j in range(N):
            if i + 1 < N and not v[(i + 1, j)]: R.link(ids[(i, j)], ids[(i + 1, j)])
            if j + 1 < N and not h[(i, j + 1)]: R.link(ids[(i, j)], ids[(i, j + 1)])
    R.spot('probe', 8, 6.0, 1.7)
    R.meta.update(label='The Balustrade Maze', weight=5,
                  blurb='A maze you can see over. It does not make it any shorter. Climbing over is allowed, but somehow it feels like cheating.')
    return R
