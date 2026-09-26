"""The Floating Islands: a dark hall two floors deep, and in the dark hang chunks of parquet floor torn out
of some reading room, their undersides raw stone and plaster, each still carrying its desk and its green
lamp. They float close enough to step between, each roped off with velvet like an exhibit, from the gallery
round the walls out to the biggest island in the middle. One small island drifts back and forth on its
own; ride it out to a lonely island nobody can reach on foot. Under the rug on the biggest island is a
trapdoor, and a ladder down into a room hanging in the stone beneath it."""
from kit_h7 import *
from kit_h5 import cone

W = D = 64.0
UP = LH
LE = 4.6
GAP = 0.15
AP = math.cos(math.pi / 8)          # an octagon's apothem / circumradius


def octa_pts(cx, cy, r):
    return [(cx + r * math.cos(math.pi / 8 + k * math.pi / 4), cy + r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]


# islands: name -> [cx, cy, r, top]; placed side by side (flat sides facing, a crack between)
ISL = {}
LINKS = []           # (a, b, direction in degrees from a to b)


def place(name, r, top, after=None, dirn=0, at=None):
    if at is not None:
        ISL[name] = [at[0], at[1], r, top]
    else:
        ax, ay, ar, at_ = ISL[after]
        d = ar * AP + GAP + r * AP
        ISL[name] = [ax + d * math.cos(math.radians(dirn)), ay + d * math.sin(math.radians(dirn)), r, top]
        LINKS.append((after, name, dirn))


place('i1', 3.0, 8.0, at=(LE + GAP + 3.0 * AP, 20.25))
place('i2', 2.6, 8.3, 'i1', 0)
place('i3', 2.6, 8.6, 'i2', 90)
place('big', 6.2, 9.0, 'i3', 0)
place('i4', 2.6, 9.3, 'big', 0)
place('i6', 2.6, 8.7, 'big', 270)
place('i7', 2.6, 8.4, 'i6', 270)
place('i9', 2.8, 9.3, 'big', 90)
place('i10', 2.4, 9.6, 'i9', 90)
place('i11', 2.6, 9.3, 'i10', 180)
# the south end of the chain reaches down to the south gallery
_i7 = ISL['i7']
place('i8', (_i7[1] - _i7[2] * AP - GAP - (LE + GAP)) / 2 / AP, 8.1, 'i7', 270)
# the drifter rests against i4's east side and slides north to the lonely island
MR = 1.8
_i4 = ISL['i4']
MX, MY = _i4[0] + _i4[2] * AP + GAP + MR * AP, _i4[1]
MD = 9.0                                    # how far it drifts (north)
LONE = [MX - MR * AP - GAP - 3.0 * AP, MY + MD, 3.0, _i4[3]]
OPEN = {k: set() for k in ISL}
for (a, b, dn) in LINKS:
    OPEN[a].add(dn % 360); OPEN[b].add((dn + 180) % 360)
OPEN['i1'].add(180)                         # onto the west gallery
OPEN['i8'].add(270)                         # onto the south gallery
OPEN['i4'].add(0)                           # the drifter's berth
OPEN['lone'] = {0}


def make():
    R = Room('floatislands', 4, 4, levels=2, res=2048)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, R.hi - 0.1, 'tile', bottom='slate', top='plaster'))
    gallery(R)
    rnd = rng(63)
    for k, (cx, cy, r, top) in ISL.items():
        island(R, R, cx, cy, r, top, OPEN[k], rnd, hole=(k == 'big'))
        if k != 'big': furnish(R, k, cx, cy, r, top, rnd)
    island(R, R, *LONE, OPEN['lone'], rnd)
    lonely(R)
    drifter(R, rnd)
    big(R)
    distant(R, rnd)
    floor(R)
    fx(R, 'dust', [LE, LE, 7.0, W - LE, D - LE, 13.0])
    fx(R, 'fog', [LE, LE, 0.0, W - LE, D - LE, 4.5], density=0.05)
    e = 2.3
    navloop(R, [(e, 6), (e, 32), (e, D - e), (32, D - e), (W - e, D - e), (W - e, 32), (W - e, e), (32, 6)])
    navloop(R, [(e, e), (32, e), (W - e, e), (W - e, 32), (W - e, D - e), (32, D - e), (e, D - e), (e, 32)], z=UP)
    b = ISL['big']
    R.link(R.navpt(ISL['i1'][0], ISL['i1'][1], 8.0), R.navpt(ISL['i2'][0], ISL['i2'][1], 8.3))
    return finish(R, 'The Floating Islands', weight=2, probe=(b[0], b[1] - 9.0, 10.5), top=R.hi,
                  blurb='Pieces of a reading room float in the dark here, each with its desk and its lamp, as if the floor had simply come apart. They are roped off like exhibits. People step between them very carefully.')


# ---------------------------------------------------------------------------
class _H:
    pass


def rope_rail(H, pts, z, h=0.92, post=1.1):
    """Brass stanchions and a velvet rope along a polyline, with an invisible wall (H: R or a mover)."""
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 0.05: continue
        n = max(1, int(math.ceil(L / post)))
        for k in range(n + 1):
            x, y = a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n
            H.nocol.add(box(x - 0.03, y - 0.03, z, x + 0.03, y + 0.03, z + h + 0.05, 'brass', skip=('-z',)))
        H.nocol.add(beam((a[0], a[1], z + h - 0.08), (b[0], b[1], z + h - 0.08), 0.04, 'velvet'))
        H.col.add(obox(a[0], a[1], b[0], b[1], z, z + h + 0.15, 0.08, 'tile'))


def island_ropes(H, cx, cy, r, top, opens, inset=0.3):
    """Ropes round an octagonal island, inset from its edge, leaving the flat sides in `opens` (normal angle
    in degrees) open, with short stubs out to the edge beside each opening."""
    ro = r
    ri = (r * AP - inset) / AP
    Vo = octa_pts(cx, cy, ro); Vi = octa_pts(cx, cy, ri)
    # side s (normal angle 45*s) runs from vertex s-1 to vertex s
    sides = [(k * 45) % 360 for k in range(8)]
    roped = [(s not in opens) for s in sides]
    if all(roped):
        rope_rail(H, [Vi[(k - 1) % 8] for k in range(8)] + [Vi[7]], top); return
    # start just after an open side
    k0 = next(k for k in range(8) if not roped[k])
    k = (k0 + 1) % 8
    for _ in range(8):
        if roped[k]:
            run = []
            j = k
            while roped[j]:
                run.append(j); j = (j + 1) % 8
                if j == k: break
            a = (run[0] - 1) % 8; b = run[-1] % 8
            pts = [Vo[a], Vi[a]] + [Vi[s] for s in run] + [Vo[b]]
            rope_rail(H, pts, top)
            k = j
            if k == (k0 + 1) % 8 or len(run) >= 8: break
        else:
            k = (k + 1) % 8
            if k == (k0 + 1) % 8: break


def island(R, H, cx, cy, r, top, opens, rnd, hole=False, parts=None, nocol=None):
    """A chunk of parquet floor with a raw underside: plaster, stone, a tapering ragged bottom."""
    parts = parts if parts is not None else R.parts
    nocol = nocol if nocol is not None else R.nocol
    V = octa_pts(cx, cy, r)
    depth = 1.8 + r * 0.55
    if not hole:
        parts.add(poly_prism(V, top - 0.3, top, side='walnut', top='floor', bottom='plaster'))
        nocol.add(cone(cx, cy, top - 0.3 - 0.35, top - 0.3, r * 0.98, r * 0.96, 8, m='plaster', a0=math.pi / 8))
        nocol.add(cone(cx, cy, top - 0.65 - depth, top - 0.65, r * 0.3, r * 0.92, 8, m='tile', a0=math.pi / 8))
    for k in range(int(4 + r * 2)):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.2, 0.75) * r
        s = rnd.uniform(0.25, 0.6)
        zb = top - 0.65 - depth * (1 - d / r) * rnd.uniform(0.5, 1.0)
        g = box(-s, -s * 0.7, -s * 0.8, s, s * 0.7, 0, rnd.choice(('tile', 'tile', 'plaster', 'slate', 'oxblood')))
        g.xform(rnd.uniform(0, math.pi), cx + d * math.cos(a), cy + d * math.sin(a), zb + 0.1)
        nocol.add(g)
    # the ropes
    island_ropes(H, cx, cy, r, top, opens)


def furnish(R, k, cx, cy, r, top, rnd):
    """Each island keeps its desk, its chair, its green lamp; some a rug, a stack of books, a globe."""
    a = rnd.choice((0.0, math.pi / 2, math.pi, -math.pi / 2)) + rnd.uniform(-0.3, 0.3)
    dx, dy = 0.35 * math.cos(a), 0.35 * math.sin(a)
    desk(R, cx + dx, cy + dy, a, z=top, w=1.4, d=0.7)
    desk_lamp(R, cx + dx + 0.45 * math.cos(a), cy + dy + 0.45 * math.sin(a), top + 0.78)
    open_book(R, cx + dx - 0.2 * math.cos(a), cy + dy - 0.2 * math.sin(a), top + 0.78, a)
    px, py = cx + dx - 0.75 * math.sin(a), cy + dy + 0.75 * math.cos(a)
    R.parts.add(chair(px, py, a - math.pi / 2).xform(0, 0, 0, top))
    R.spot('sit', px, py, top + 0.48, a - math.pi / 2)
    if rnd.random() < 0.7:
        rug(R, cx - r * 0.55, cy - r * 0.4, cx + r * 0.55, cy + r * 0.4, top, ang=a)
    if rnd.random() < 0.6:
        book_pile(R, cx - 0.9 * math.cos(a), cy - 0.9 * math.sin(a), top, rnd.randint(4, 9), seed=rnd.randint(0, 99), col=False)


def gallery(R):
    """The gallery round the walls at the upper doors (railed, with openings where islands berth), books,
    and a stair down to the floor of the hall."""
    th = 0.45
    hole = (11.5, 2.5, 17.5, LE)
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, hole[0], LE), (hole[2], T - 0.02, W - T + 0.02, LE), (hole[0], T - 0.02, hole[2], hole[1]),
                             (T - 0.02, D - LE, W - T + 0.02, D - T + 0.02), (T - 0.02, LE, LE, D - LE), (W - LE, LE, W - T + 0.02, D - LE)):
        R.parts.add(box(x0, y0, UP - th, x1, y1, UP, 'tile', top='floor', bottom='plaster'))
    i1, i8 = ISL['i1'], ISL['i8']
    wo = i1[2] * math.sin(math.pi / 8)          # half a flat side
    so = i8[2] * math.sin(math.pi / 8)
    r_ = -0.1
    def edge(a, b, fixed, along_x, gaps):
        p = a
        for (g0, g1) in sorted(gaps) + [(None, None)]:
            q = b if g0 is None else g0
            if q - p > 0.1:
                rail_line(R, [(p, fixed), (q, fixed)] if along_x else [(fixed, p), (fixed, q)], UP, m='iron')
            if g0 is not None: p = g1
    edge(hole[2], W - LE - r_, LE + r_, True, [(i8[0] - so, i8[0] + so)])
    edge(LE + r_, hole[0], LE + r_, True, [])
    edge(LE + r_, W - LE - r_, D - LE - r_, True, [])
    edge(LE + r_, D - LE - r_, LE + r_, False, [(i1[1] - wo, i1[1] + wo)])
    edge(LE + r_, D - LE - r_, W - LE - r_, False, [])
    # the stair (two flights on the south wall)
    n, rise, run = 20, 0.2, 0.3
    R.flight(11.5, 0.4, 0.0, 2.0, n, rise, run, '+x', m='tile', riser='tile', side='tile')
    R.parts.add(box(11.5, 2.4, 0.0, 17.5, LE, 4.0, 'tile', skip=('-z',)))
    R.parts.add(box(17.5, 0.4, 0.0, 20.0, LE, 4.0, 'tile', top='terrazzo', skip=('-z',)))
    R.flight(17.5, 2.6, 4.0, 2.0, n, rise, run, '-x', m='tile', riser='tile', side='tile')
    stair_rail(R, 17.2, LE - 0.05, 4.0 + rise, 12.1, LE - 0.05, UP, m='iron')
    rail_line(R, [(20.0 - 0.05, LE - 0.05), (17.5, LE - 0.05)], 4.0, m='iron')
    rail_line(R, [(20.0 - 0.05, 0.5), (20.0 - 0.05, LE - 0.05)], 4.0, m='iron')
    rail_line(R, [(12.6, 2.45), (17.5, 2.45), (17.5, LE - 0.1)], UP, m='iron')
    # books
    wall_cases(R, z=UP, rows=11, frame='walnut')
    wall_cases(R, rows=13, frame='walnut', sides='NWE')
    for (a, b) in ((0.6, 6.2), (25.8, 38.2), (41.8, 54.2), (57.8, W - 0.6)):
        sh(R, '+y', T, a, b, rows=13, frame='walnut')
    for p in (10.0, 18.0, 30.0, 38.0, 50.0, 58.0):
        for (x, y) in ((p, LE - 0.15), (p, D - LE + 0.15), (LE - 0.15, p), (W - LE + 0.15, p)):
            R.light(sphere(x, y, UP + 1.15, 0.08, 8, 4, 'e_amber'))
        for (x, y) in ((p, LE - 1.6), (p, D - LE + 1.6), (LE - 1.6, p), (W - LE + 1.6, p)):
            R.light(sphere(x, y, UP - th - 0.35, 0.12, 8, 4, 'e_dim'))
    for (x, y) in ((2.4, 2.4), (W - 2.4, 2.4), (2.4, D - 2.4), (W - 2.4, D - 2.4), (2.4, 32), (W - 2.4, 32), (32, D - 2.4)):
        hanging(R, x, y, R.hi - 0.1, UP + 3.4, r=0.4, e='e_lamp', shade='green')


def big(R):
    """The biggest island: a reading room's worth of floor, two desks, a short stack, lamp standards, a rug
    thrown back from a trapdoor. Under it, in the stone, a room: a ladder down, a bed, a desk, a window."""
    cx, cy, r, top = ISL['big']
    V = octa_pts(cx, cy, r)
    # the ladder climbs +x from the room's floor to the trapdoor; its centre line on the walk-check grid
    ly = math.floor(cy / 0.5) * 0.5 + 0.25
    RZ = top - 3.0
    lx0 = cx - 1.6                        # foot
    lx1 = lx0 + 3.0                       # top (45 degrees)
    hx0, hx1, hy0, hy1 = lx0 + 0.8, lx1, ly - 0.6, ly + 0.6
    # the floor with the hole: convex pieces of the octagon round the rectangle
    for rect in ((-1e9, -1e9, hx0, 1e9), (hx1, -1e9, 1e9, 1e9), (hx0, -1e9, hx1, hy0), (hx0, hy1, hx1, 1e9)):
        P = clip_poly(V, *rect)
        if len(P) >= 3: R.parts.add(poly_prism(P, top - 0.3, top, side='walnut', top='floor', bottom='plaster'))
    rail_line(R, [(hx0 - 0.05, hy1 + 0.05), (hx0 - 0.05, hy0 - 0.05)], top, m='brass')
    rail_line(R, [(hx0 - 0.05, hy0 - 0.05), (hx1 - 0.2, hy0 - 0.05)], top, m='brass')
    rail_line(R, [(hx0 - 0.05, hy1 + 0.05), (hx1 - 0.2, hy1 + 0.05)], top, m='brass')
    hatch_frame(R, hx0, hy0, hx1, hy1, top, m='oak', t=0.08)
    lid = box(0, 0, 0, hx1 - hx0, 0.05, hy1 - hy0, 'oak'); rot(lid, 'x', -0.25); lid.xform(0, hx0, hy1 + 0.05, top)
    R.nocol.add(lid)
    # the rug, thrown back in a heap beside it
    rug(R, cx + 1.4, cy - 2.6, cx + 4.2, cy + 0.4, top)
    R.nocol.add(box(hx0 - 1.2, hy0 - 0.9, top, hx0 - 0.2, hy1 + 0.9, top + 0.12, 'carpet'))
    # the underside: a hollow shell of stone (the room is inside it)
    zt = top - 0.3
    zb = RZ - 1.4
    rb = 3.8
    prof = [(r * AP, zt), (rb, zb), (0.05, zb), (0.05, zb + 0.3), (rb - 0.32, zb + 0.3), (r * AP - 0.32, zt)]
    R.parts.add(lathe(cx, cy, prof, 8, ['tile', 'tile', 'tile', 'plaster', 'plaster', 'plaster'], a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    rnd = rng(630)
    for k in range(18):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.3, 1.0) * rb
        s = rnd.uniform(0.3, 0.7)
        g = box(-s, -s * 0.7, -s, s, s * 0.7, 0, rnd.choice(('tile', 'slate', 'plaster', 'oxblood')))
        g.xform(rnd.uniform(0, 3), cx + d * math.cos(a), cy + d * math.sin(a), zb + 0.25 + (1 - d / rb) * 0.3)
        R.nocol.add(g)
    # the room: a plank floor and plank walls inside the shell
    x0, x1, y0, y1 = cx - 3.0, cx + 2.6, cy - 1.8, cy + 1.8
    R.parts.add(box(x0, y0, RZ - 0.2, x1, y1, RZ, 'walnut', top='oak'))
    for (a0, b0, a1, b1) in ((x0, y0, x1, y0 + 0.1), (x0, y1 - 0.1, x1, y1), (x0, y0, x0 + 0.1, y1), (x1 - 0.1, y0, x1, y1)):
        R.parts.add(box(a0, b0, RZ, a1, b1, zt, 'walnut'))
    ladder_up(R, lx0, ly, RZ, top, '+x', w=1.0, m='oak', rail='brass', ang=math.radians(45))
    # inside: a narrow bed, a desk and lamp, a shelf, candles, a plaque
    R.parts.add(box(x1 - 2.0, y1 - 1.0, RZ, x1 - 0.12, y1 - 0.12, RZ + 0.42, 'bed', sides='walnut'))
    R.spot('bed', x1 - 1.0, y1 - 0.55, RZ + 0.42, 0.0)
    desk(R, x1 - 1.0, y0 + 0.5, 0.0, z=RZ, w=1.4, d=0.65)
    desk_lamp(R, x1 - 1.4, y0 + 0.5, RZ + 0.78)
    open_book(R, x1 - 0.8, y0 + 0.5, RZ + 0.78, 0.1)
    R.parts.add(chair(x1 - 1.0, y0 + 1.15, -math.pi / 2).xform(0, 0, 0, RZ))
    R.spot('sit', x1 - 1.0, y0 + 1.15, RZ + 0.48, -math.pi / 2)
    sh(R, '+x', x0 + 0.1, y0 + 0.15, ly - 0.8, z=RZ, rows=5, frame='walnut', depth=0.28)
    sh(R, '+x', x0 + 0.1, ly + 0.8, y1 - 0.15, z=RZ, rows=5, frame='walnut', depth=0.28)
    candle(R, x0 + 1.0, y1 - 0.3, RZ, h=0.22)
    R.light(sphere(cx, cy - 1.1, zt - 0.4, 0.1, 8, 4, 'e_lamp'))
    R.nocol.add(cyl(cx, cy - 1.1, zt - 0.3, zt, 0.008, 4, side='iron', caps=False))
    R.spot('plaque', x1 - 0.12, cy, RZ + 1.5, math.pi, text='BELOW THE ISLAND. PLEASE KEEP THE TRAPDOOR SHUT: IT IS A LONG WAY DOWN, EVEN FROM HERE.')
    secret(R, cx, cy + 0.4, RZ, 'The Room Under the Island',
           'The rug on the biggest island hides a trapdoor. Down the ladder, inside the raw stone underneath, someone has fitted out a room with a bed and a desk, and slept here, floating.', r=2.2)
    # up top: two more desks, a short stack, lamp standards
    for (dx, dy, a) in ((-3.0, 2.2, math.pi / 2), (-2.8, -2.4, -math.pi / 2)):
        desk(R, cx + dx, cy + dy, a, z=top, w=1.6, d=0.8)
        desk_lamp(R, cx + dx + 0.5 * math.cos(a + math.pi / 2), cy + dy + 0.5 * math.sin(a + math.pi / 2), top + 0.78)
    stack(R, 'y', cx - 0.5, cy + 1.6, cy + 4.0, top, rows=5, frame='walnut')
    for (dx, dy) in ((3.2, 3.2), (-4.0, 0.0), (1.0, -4.2)):
        lamp_post(R, cx + dx, cy + dy, z=top, h=2.4)


def drifter(R, rnd):
    """A small island that drifts north along i4's east side to the lonely island and back (a slide mover).
    Only its west side is open: at one end it faces i4, at the other the lonely island."""
    M = R.mover('slide', delta=(0.0, MD, 0.0), period=44.0, pause=9.0)
    top = ISL['i4'][3]
    H = _H(); H.nocol = M.nocol; H.col = M.col
    V = octa_pts(MX, MY, MR)
    M.parts.add(poly_prism(V, top - 0.3, top, side='walnut', top='floor', bottom='plaster'))
    M.nocol.add(cone(MX, MY, top - 0.3 - 2.4, top - 0.3, MR * 0.3, MR * 0.92, 8, m='tile', a0=math.pi / 8))
    island_ropes(H, MX, MY, MR, top, {180})
    M.parts.add(chair(MX + 0.5, MY, math.pi).xform(0, 0, 0, top))
    g = table(MX - 0.1, MY - 0.9, MX + 0.5, MY - 0.4, 0.7, 'walnut', top='leather'); g.xform(0, 0, 0, top)
    M.parts.add(g)
    M.nocol.add(box(MX + 0.05, MY - 0.8, top + 0.7, MX + 0.35, MY - 0.55, top + 0.76, 'oxblood'))


def lonely(R):
    """The island only the drifter reaches: an armchair facing the dark, a lamp, a note."""
    cx, cy, r, top = LONE
    armchair(R, cx - 0.6, cy + 0.4, math.pi * 0.75, m='velvet', z=top)
    lamp_post(R, cx - 1.4, cy - 0.4, z=top, h=1.6)
    R.parts.add(cyl(cx - 0.2, cy - 0.6, top, top + 0.55, 0.22, 12, side='walnut', top='walnut'))
    book_pile(R, cx - 0.2, cy - 0.6, top + 0.55, 5, seed=4)
    R.spot('plaque', cx + 1.2, cy - 1.8, top + 1.0, math.pi / 2, text='THE ISLAND WILL COME BACK FOR YOU. IT ALWAYS HAS SO FAR.')


def distant(R, rnd):
    """More islands out in the dark, beyond reach, at every height, each with a lamp still lit."""
    spots = [(48, 12, 2.2, 11.5), (54, 22, 1.8, 7.0), (46, 44, 2.6, 12.0), (54, 52, 2.0, 9.5), (36, 54, 2.2, 13.0), (14, 50, 2.4, 11.0),
             (10, 38, 1.7, 6.5), (26, 8, 1.8, 12.5), (40, 36, 1.6, 12.8), (22, 44, 1.5, 6.8)]
    for (x, y, r, top) in spots:
        V = octa_pts(x, y, r)
        R.nocol.add(poly_prism(V, top - 0.3, top, side='walnut', top='floor', bottom='plaster'))
        R.nocol.add(cone(x, y, top - 0.3 - 1.5 - r * 0.5, top - 0.3, r * 0.3, r * 0.92, 8, m='tile', a0=math.pi / 8))
        g = table(x - 0.6, y - 0.35, x + 0.6, y + 0.35, 0.76, 'walnut', top='leather'); g.xform(rnd.uniform(0, 3), 0, 0, top)
        R.nocol.add(g)
        R.nocol.add(cyl(x, y, top + 0.76, top + 1.1, 0.012, 6, side='brass', caps=False))
        R.nocol.add(obox(x - 0.17, y, x + 0.17, y, top + 1.1, top + 1.18, 0.13, 'green'))
        R.light(obox(x - 0.15, y, x + 0.15, y, top + 1.085, top + 1.1, 0.09, 'e_lamp'))


def floor(R):
    rnd = rng(64)
    g = Geo()
    for k in range(300):
        x, y = rnd.uniform(LE + 1, W - LE - 1), rnd.uniform(LE + 1, D - LE - 1)
        book_scatter(g, x, y, 0.0, rnd, 1, spread=0.0, tilt=0.2)
    R.nocol.add(g)
    for (x, y) in ((16, 30), (40, 18), (30, 46), (50, 40)):
        lamppost(R, x, y, h=2.6, e='e_candle', r=0.12)
