"""The Shelf Canyon: bookcases seven metres tall standing in a maze of narrow winding canyons,
lit only by slits of sky far overhead. Rolling ladders lean where somebody left them."""
from lib import *
from kit_a import *
import random

H = TOP - 0.1
NG = 5
S = (C - 2 * T) / NG        # cell pitch
WT = 1.56                   # wall thickness: two bookcases on a solid core
ROWS, RH = 13, 0.5           # nearly 7 m of books
LOOPS = 2
DOORS = {(2, 0): 'S', (2, NG - 1): 'N', (0, 2): 'W', (NG - 1, 2): 'E'}


def make():
    R = Room('canyon', 1, 1, res=1024)
    shell(R, wall='tile', floor='floor', ceil='plaster', h=H)
    rnd = random.Random(11)
    # walls: ('v', i, j) between cells (i-1, j) and (i, j); ('h', i, j) between (i, j-1) and (i, j)
    walls = set(('v', i, j) for i in range(1, NG) for j in range(NG)) | set(('h', i, j) for i in range(NG) for j in range(1, NG))
    seen = {(2, 2)}; st = [(2, 2)]
    while st:
        i, j = st[-1]
        nb = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= i + di < NG and 0 <= j + dj < NG and (i + di, j + dj) not in seen]
        if not nb: st.pop(); continue
        a, b = rnd.choice(nb)
        walls.discard(('v', max(i, a), j) if a != i else ('h', i, max(j, b)))
        seen.add((a, b)); st.append((a, b))
    for _ in range(LOOPS):   # a few loops, so it winds instead of dead-ending everywhere
        walls.discard(rnd.choice(sorted(walls)))
    # a little plaza inside each door, and the clearing in the middle
    for (i, j), side in DOORS.items():
        if side in 'SN':
            walls.add(('v', i, j)); walls.add(('v', i + 1, j))
        else:
            walls.add(('h', i, j)); walls.add(('h', i, j + 1))
    for w in (('v', 2, 2), ('v', 3, 2), ('h', 2, 2), ('h', 2, 3)):
        walls.discard(w)
    P = lambda k: T + k * S
    hw = WT / 2
    deg = {}
    for (o, i, j) in walls:
        for nd, d in ((((i, j), 'n' if o == 'v' else 'e')), (((i, j + 1) if o == 'v' else (i + 1, j)), 's' if o == 'v' else 'w')):
            deg.setdefault(nd, set()).add(d)
    # a pillar wherever walls end, turn or meet (not where one runs straight on)
    pillars = set(nd for nd, d in deg.items() if d not in ({'n', 's'}, {'e', 'w'}))
    # the walls either side of a door stop 2.3 m short of it, so each doorway opens on a little court
    stubs = {(2, 0): 'S', (3, 0): 'S', (2, NG): 'N', (3, NG): 'N', (0, 2): 'W', (0, 3): 'W', (NG, 2): 'E', (NG, 3): 'E'}
    pillars -= set(stubs)
    for (i, j) in pillars:
        x, y = P(i), P(j)
        R.parts.add(box(max(T, x - hw), max(T, y - hw), 0, min(C - T, x + hw), min(C - T, y + hw), 7.05, 'tile'))
        R.parts.add(box(max(T, x - hw - 0.05), max(T, y - hw - 0.05), 7.05, min(C - T, x + hw + 0.05), min(C - T, y + hw + 0.05), 7.15, 'walnut'))
    bays = []
    def runs(line, o):
        ks = sorted(k for k in range(NG) if (o, line, k) in walls) if o == 'v' else sorted(k for k in range(NG) if (o, k, line) in walls)
        out = []
        for k in ks:
            if out and out[-1][1] == k - 1: out[-1][1] = k
            else: out.append([k, k])
        return out
    for o in ('v', 'h'):
        for line in range(1, NG):
            for (k0, k1) in runs(line, o):
                a, b = P(k0), P(k1 + 1)
                n0 = (line, k0) if o == 'v' else (k0, line); n1 = (line, k1 + 1) if o == 'v' else (k1 + 1, line)
                a0 = a + 2.3 if n0 in stubs else None; b0 = b - 2.3 if n1 in stubs else None
                if a0: a = a0
                if b0: b = b0
                cw = hw - 0.3
                if o == 'v': R.parts.add(box(P(line) - cw, a, 0, P(line) + cw, b, 7.0, 'tile'))
                else: R.parts.add(box(a, P(line) - cw, 0, b, P(line) + cw, 7.0, 'tile'))
                for side in (1, -1):
                    # break the bookcase where a cross wall meets this face
                    cuts = [k0] + [k for k in range(k0 + 1, k1 + 1) if
                                   ((('h', line if side > 0 else line - 1, k) in walls) if o == 'v' else (('v', k, line if side > 0 else line - 1) in walls))
                                   or (((line, k) if o == 'v' else (k, line)) in pillars)] + [k1 + 1]
                    for c0, c1 in zip(cuts, cuts[1:]):
                        lo, hi = P(c0) + hw, P(c1) - hw
                        if c0 == k0 and a0: lo = a0 + 0.05
                        if c1 == k1 + 1 and b0: hi = b0 - 0.05
                        if hi - lo < 0.4: continue
                        bk = P(line) + side * (hw - 0.3)
                        f = ('+x' if side > 0 else '-x') if o == 'v' else ('+y' if side > 0 else '-y')
                        sh(R, f, bk, lo, hi, rows=ROWS, row_h=RH, depth=0.3, frame='wood', back=False, sides=False)
                        bays.append((f, bk, lo, hi))
    # the outer walls are books too, except at the doors
    for side in 'SNWE':
        f, bk = {'S': ('+y', T), 'N': ('-y', C - T), 'W': ('+x', T), 'E': ('-x', C - T)}[side]
        nd = (lambda k: (k, 0)) if side == 'S' else (lambda k: (k, NG)) if side == 'N' else (lambda k: (0, k)) if side == 'W' else (lambda k: (NG, k))
        cuts = [0] + [k for k in range(1, NG) if nd(k) in deg] + [NG]
        for c0, c1 in zip(cuts, cuts[1:]):
            a = P(c0) + (hw if c0 > 0 else 0.02); b = P(c1) - (hw if c1 < NG else 0.02)
            for (lo, hi) in ((a, min(b, 8 - 1.8)), (max(a, 8 + 1.8), b)):
                if hi - lo < 0.5: continue
                sh(R, f, bk, lo, hi, rows=7, row_h=RH, depth=0.3, frame='wood', sides=False)
    # rolling ladders left leaning here and there
    for (f, bk, a, b) in rnd.sample(bays, 5):
        m = (a + b) / 2
        ang = {'+x': 0, '-x': math.pi, '+y': math.pi / 2, '-y': -math.pi / 2}[f]
        x, y = (bk + math.cos(ang) * 0.3, m) if f[1] == 'x' else (m, bk + math.sin(ang) * 0.3)
        R.nocol.add(ladder(x, y, ang, h=rnd.choice((4.2, 5.4, 6.6)), lean=0.8))
    # slits of sky: along some rows and columns of cells, far overhead
    rows_y = [P(j) + S / 2 for j in (1, 3)]
    for y in rows_y:
        R.cut(box(T + 0.3, y - 0.14, H - 0.05, C - T - 0.3, y + 0.14, R.hi + 0.5, 'plaster'))
        R.light(box(T + 0.3, y - 0.14, R.hi - 0.08, C - T - 0.3, y + 0.14, R.hi - 0.05, 'e_sky'))
    for i in (0, 2, 4):
        x = P(i) + S / 2
        for (a, b) in ((T + 0.3, rows_y[0] - 0.2), (rows_y[0] + 0.2, rows_y[1] - 0.2), (rows_y[1] + 0.2, C - T - 0.3)):
            R.cut(box(x - 0.14, a, H - 0.05, x + 0.14, b, R.hi + 0.5, 'plaster'))
            R.light(box(x - 0.14, a, R.hi - 0.08, x + 0.14, b, R.hi - 0.05, 'e_sky'))
    # a few dim lamps low in the canyons, for the night
    for (i, j) in ((2, 2), (1, 1), (3, 3), (1, 3), (3, 1), (2, 0), (2, 4), (0, 2), (4, 2)):
        x, y = P(i) + S / 2, P(j) + S / 2
        bulb(R, x, y, 3.4, r=0.1, m='e_amber', top=H)
    # the clearing: one chair
    R.parts.add(chair(8.0, 8.4, -math.pi / 2))
    R.spot('sit', 8.0, 8.4, 0.48, -math.pi / 2)
    # walkers: a node in every open cell, linked through the gaps
    ids = {}
    for i in range(NG):
        for j in range(NG):
            ids[(i, j)] = R.navpt(P(i) + S / 2, P(j) + S / 2)
    for i in range(NG):
        for j in range(NG):
            if i + 1 < NG and ('v', i + 1, j) not in walls: R.link(ids[(i, j)], ids[(i + 1, j)])
            if j + 1 < NG and ('h', i, j + 1) not in walls: R.link(ids[(i, j)], ids[(i, j + 1)])
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Shelf Canyon', weight=6,
                  blurb='The shelves go up and up. The sky is a crack far overhead. The way back is the way you came, if you can remember which way that was.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return tidy(R)
