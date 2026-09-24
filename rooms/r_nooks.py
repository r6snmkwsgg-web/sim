"""The Nooks: walls a metre and a half thick, honeycombed with arched cells three tiers high.
The low ones each hold a chair and a lamp, or a bookcase; the high ones hold books nobody can reach."""
from lib import *
from kit_b import *

W0 = 1.6          # wall thickness


def cell_cut(R, side, c, z0, w, jamb, depth, floor, wall):
    pr = arch_profile(0, w, z0, jamb, 8)
    m = arch_mats(len(pr), floor, wall)
    if side == 'S': R.cut(prism([(p + c, q) for p, q in pr], 'y', W0 - depth, W0 + 0.05, m))
    if side == 'N': R.cut(prism([(p + c, q) for p, q in pr], 'y', C - W0 - 0.05, C - W0 + depth, m))
    if side == 'W': R.cut(prism([(p + c, q) for p, q in pr], 'x', W0 - depth, W0 + 0.05, m))
    if side == 'E': R.cut(prism([(p + c, q) for p, q in pr], 'x', C - W0 - 0.05, C - W0 + depth, m))


def frame(side, c, d):
    """Local frame of a cell: returns (x, y) of a point d metres out from the cell's back wall at c,
    and the angle facing out into the room."""
    if side == 'S': return (lambda u, dd: (c + u, W0 - d + dd)), math.pi / 2
    if side == 'N': return (lambda u, dd: (c - u, C - W0 + d - dd)), -math.pi / 2
    if side == 'W': return (lambda u, dd: (W0 - d + dd, c - u)), 0.0
    return (lambda u, dd: (C - W0 + d - dd, c + u)), math.pi


def make():
    R = Room('nooks', 1, 1, res=1024)
    H = 7.4
    R.sockets(floor='floor', wall='tile')
    R.cut(box(W0 - 0.02, W0 - 0.02, 0, C - W0 + 0.02, C - W0 + 0.02, H, 'tile', bottom='floor', top='plaster'))
    for s in 'SNWE': door_tunnel(R, s, W0, 'floor', 'tile')
    # an oculus
    R.cut(cyl(8, 8, H - 0.05, R.hi + 0.5, 1.3, 32, side='plaster', top='plaster', bottom='plaster'))
    R.light(cyl(8, 8, R.hi - 0.08, R.hi - 0.05, 1.3, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    P = 1.45                       # pitch of the cells
    low = (2.35, 3.8, 5.25, 10.75, 12.2, 13.65)
    mid = (3.075, 4.525, 11.475, 12.925)
    top = (2.35, 3.8, 5.25, 6.7, 8.0, 9.3, 10.75, 12.2, 13.65)
    cw, depth = 1.1, 1.25
    k = 0
    for side in 'SNWE':
        for i, c in enumerate(low):
            chair_cell = i % 3 != 1
            cell_cut(R, side, c, 0, cw, 1.55, depth, 'carpet', 'damask')
            f, ang = frame(side, c, depth)
            if chair_cell:
                x, y = f(0, 0.6)
                chair(R, x, y, ang, frame='walnut', seat='velvet', arms=True)
                lx, ly = f(0, 0.05)
                bulb(R, lx, ly, 1.75, 0.07, 'e_amber')
                R.nocol.add(box(-0.05, -0.1, 1.62, 0.12, 0.1, 1.67, 'brass').xform(ang, lx, ly))
                # a stack of books on the floor beside it
                bx, by = f(0.36, 0.3)
                R.nocol.add(box(-0.12, -0.09, 0, 0.12, 0.09, 0.08 + 0.05 * (k % 4), 'leather', skip=('-z',)).xform(ang + 0.3 * (k % 3), bx, by))
            else:
                bx, by = f(-(cw / 2 - 0.02), 0.0)
                bshelf(R, bx, by, 0.0, cw - 0.04, ang, rows=5, row_h=0.38, depth=0.34, frame='walnut', sides=False, crown=False)
            k += 1
        for c in mid:
            cell_cut(R, side, c, 2.55, cw, 1.2, 0.8, 'tile', 'damask')
            f, ang = frame(side, c, 0.8)
            bx, by = f(-(cw / 2 - 0.02), 0.0)
            bshelf(R, bx, by, 2.55, cw - 0.04, ang, rows=2, row_h=0.5, depth=0.3, frame='walnut', back=False, sides=False, crown=False)
        for i, c in enumerate(top):
            cell_cut(R, side, c, 4.85, cw, 1.2, 0.8, 'tile', 'damask')
            f, ang = frame(side, c, 0.8)
            if i % 2:
                bx, by = f(-(cw / 2 - 0.02), 0.0)
                bshelf(R, bx, by, 4.85, cw - 0.04, ang, rows=2, row_h=0.5, depth=0.3, frame='walnut', back=False, sides=False, crown=False)
            else:   # a lamp and a single urn
                lx, ly = f(0, 0.4)
                R.nocol.add(cyl(lx, ly, 4.85, 5.35, 0.16, 8, side='bronze', top='black', bottom='bronze'))
                bulb(R, lx, ly, 5.75, 0.07, 'e_lamp')
    # a round carpet and a chandelier of small lamps
    R.nocol.add(cyl(8, 8, 0, 0.012, 3.6, 40, side='carpet', top='carpet', bottom='carpet'))
    R.nocol.add(cyl(8, 8, 3.6, H, 0.02, 6, side='iron', caps=False))
    R.nocol.add(ring(8, 8, 3.55, 3.62, 1.0, 1.08, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
    for k in range(12):
        a = k * math.pi / 6
        bulb(R, 8 + math.cos(a) * 1.04, 8 + math.sin(a) * 1.04, 3.7, 0.07)
    R.light(sphere(8, 8, 3.45, 0.14, 12, 6, 'e_lamp'))
    # a low round table in the middle with a lamp and books
    round_table(R, 8, 8, 0.7, 0.55, 'walnut', top='leather')
    table_lamp(R, 8, 8, 0.55, shade='green', r=0.2)
    loop(R, [(3.4, 3.4), (8, 3.2), (C - 3.4, 3.4), (C - 3.2, 8), (C - 3.4, C - 3.4), (8, C - 3.2), (3.4, C - 3.4), (3.2, 8)])
    for (a, b) in (((8, 0.9), 1), ((8, C - 0.9), 5), ((0.9, 8), 7), ((C - 0.9, 8), 3)):
        R.link(R.navpt(*a), b)
    R.spot('probe', 8, 8, 1.7)
    R.meta.update(label='The Nooks', weight=6,
                  blurb='A chair for everyone, each in its own little cave, each facing out, each with its lamp on. The chairs are warm, as if someone just got up.')
    R.meta['box'] = [[W0, 0, W0], [C - W0, H, C - W0]]
    return R
