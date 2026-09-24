"""The Arches: rows of freestanding stone walls, each pierced by one arch, standing under a high
bright ceiling. Some bays are divided again. Some arches are filled with bookcases, so the way
through is a maze of doorways; you can always see over the books, never through them."""
from lib import *
from kit_d import *
import random

WT, WH, AW, AJ = 0.6, 4.4, 1.6, 2.3      # wall thickness, height, arch width, arch jamb


def arch_wall(R, c0, c1, p, axis, fill=None, rnd=None):
    """A wall from c0 to c1 along axis ('x' or 'y') at cross coordinate p, with an arch in the middle.
    fill: None, or the direction (+1/-1) the bookcase in the arch faces."""
    L = c1 - c0; mid = (c0 + c1) / 2
    r = AW / 2
    prof = [(c0, 0), (mid - r, 0), (mid - r, AJ)]
    for k in range(1, 12):
        t = math.pi - math.pi * k / 12
        prof.append((mid + r * math.cos(t), AJ + r * math.sin(t)))
    prof += [(mid + r, AJ), (mid + r, 0), (c1, 0), (c1, WH), (c0, WH)]
    if axis == 'x':   # wall runs along x, profile in (x, z), extruded along y
        g = prism(prof[::-1], 'y', p - WT / 2, p + WT / 2, 'tile', cap='tile')
        R.parts.add(g)
        R.parts.add(box(c0, p - WT / 2 - 0.06, WH, c1, p + WT / 2 + 0.06, WH + 0.18, 'tile'))
        R.parts.add(box(c0, p - WT / 2 - 0.04, 0, c1, p + WT / 2 + 0.04, 0.22, 'slate', skip=('-z',)))
    else:
        pr = [(q, z) for q, z in prof]
        g = prism(pr, 'x', p - WT / 2, p + WT / 2, 'tile', cap='tile')
        R.parts.add(g)
        R.parts.add(box(p - WT / 2 - 0.06, c0, WH, p + WT / 2 + 0.06, c1, WH + 0.18, 'tile'))
        R.parts.add(box(p - WT / 2 - 0.04, c0, 0, p + WT / 2 + 0.04, c1, 0.22, 'slate', skip=('-z',)))
    if fill:
        # a bookcase standing in the arch, as tall as the jamb
        if axis == 'x':
            if fill > 0: bookcase(R, mid - r + 0.02, p - 0.17, 0, AW - 0.04, '+y', 5, frame='walnut', backface=True, row_h=0.43)
            else:        bookcase(R, mid + r - 0.02, p + 0.17, 0, AW - 0.04, '-y', 5, frame='walnut', backface=True, row_h=0.43)
        else:
            if fill > 0: bookcase(R, p - 0.17, mid + r - 0.02, 0, AW - 0.04, '+x', 5, frame='walnut', backface=True, row_h=0.43)
            else:        bookcase(R, p + 0.17, mid - r + 0.02, 0, AW - 0.04, '-x', 5, frame='walnut', backface=True, row_h=0.43)
    else:
        # a small lamp under the crown of every open arch
        if axis == 'x':
            R.light(box(mid - 0.1, p - 0.1, AJ + r - 0.02, mid + 0.1, p + 0.1, AJ + r - 0.01, 'e_amber', skip=('+z', '-x', '+x', '-y', '+y')))
        else:
            R.light(box(p - 0.1, mid - 0.1, AJ + r - 0.02, p + 0.1, mid + 0.1, AJ + r - 0.01, 'e_amber', skip=('+z', '-x', '+x', '-y', '+y')))


def make():
    R = Room('archmaze', 1, 1, res=1024)
    shell(R, TOP, floor='terrazzo', wall='tile', top='plaster')
    rnd = random.Random(77)
    NB = 5
    bx = [I0 + k * (I1 - I0) / NB for k in range(NB + 1)]        # segment boundaries along x
    rows_y = (3.0, 6.0, 10.0, 13.0)
    split = (1, 3)                                              # bays divided by cross walls
    # cells: (bay, i); unsplit bays are one cell (bay, 0)
    def cell(bay, i): return (bay, i if bay in split else 0)
    edges = []
    for r, y in enumerate(rows_y):
        for i in range(NB):
            edges.append((('row', r, i), cell(r, i), cell(r + 1, i)))
    for bay in split:
        for k in range(1, NB):
            edges.append((('cross', bay, k), (bay, k - 1), (bay, k)))
    filled = {e[0] for e in edges if rnd.random() < 0.42}
    for e in edges:     # keep the straight way from the south door open for the first row only
        if e[0] == ('row', 0, 2): filled.discard(e[0])
    cells = {e[1] for e in edges} | {e[2] for e in edges}
    while True:
        adj = {c: [] for c in cells}
        for key, a, b in edges:
            if key not in filled: adj[a].append(b); adj[b].append(a)
        seen = {(0, 0)}; st = [(0, 0)]
        while st:
            a = st.pop()
            for b in adj[a]:
                if b not in seen: seen.add(b); st.append(b)
        if len(seen) == len(cells): break
        cands = [key for key, a, b in edges if key in filled and ((a in seen) != (b in seen))]
        filled.discard(rnd.choice(cands))
    for key, a, b in edges:
        f = (1 if rnd.random() < 0.5 else -1) if key in filled else None
        if key[0] == 'row':
            _, r, i = key
            arch_wall(R, bx[i], bx[i + 1], rows_y[r], 'x', f)
        else:
            _, bay, k = key
            arch_wall(R, rows_y[bay - 1] + WT / 2, rows_y[bay] - WT / 2, bx[k], 'y', f)
    # books round the outer walls, between the doors
    for (a, b) in ((0.8, 6.2), (9.8, C - 0.8)):
        for f in ('+y', '-y', '+x', '-x'):
            wall_shelf(R, f, a, b, 0, rows=7, frame='walnut')
    # a bright ceiling: big square lights on a grid, like a sky seen through a roof
    for i in range(4):
        for j in range(4):
            x, y = 2 + i * 4, 2 + j * 4
            R.cut(box(x - 1.3, y - 1.3, TOP - 0.1, x + 1.3, y + 1.3, TOP + 0.25, 'plaster'))
            R.light(box(x - 1.15, y - 1.15, TOP + 0.2, x + 1.15, y + 1.15, TOP + 0.21, 'e_panel', skip=('+z', '-x', '+x', '-y', '+y')))
    # walkers: through the cell centres
    cy = {0: 1.6, 1: 4.5, 2: 8.0, 3: 11.5, 4: 14.4}
    def ctr(c):
        bay, i = c
        return ((bx[i] + bx[i + 1]) / 2 if bay in split else 8.0, cy[bay])
    ids = {c: R.navpt(*ctr(c)) for c in cells}
    for key, a, b in edges:
        if key in filled: continue
        if key[0] == 'row':
            x = (bx[key[2]] + bx[key[2] + 1]) / 2
            pa = R.navpt(x, cy[a[0]]); pb = R.navpt(x, cy[b[0]])
            R.link(ids[a], pa, pb, ids[b]) if a[0] not in split else R.link(ids[a], pb, ids[b])
        else:
            R.link(ids[a], ids[b])
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Arches', weight=6,
                  blurb='Arch after arch after arch, and some of them are full of books. The way on is always the one next to the one you picked.')
    return R
