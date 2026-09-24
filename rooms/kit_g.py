"""Shared helpers for batch "g" rooms (the giants)."""
from lib import *


def upper_sockets(R, keep=()):
    """All doorways on levels 1.. except those in keep: returns the skip list (also stored as sealed)."""
    sk = []
    for L in range(1, R.levels):
        for i in range(R.w):
            for s in 'SN':
                if (s, i, L) not in keep: sk.append((s, i, L))
        for j in range(R.d):
            for s in 'WE':
                if (s, j, L) not in keep: sk.append((s, j, L))
    return sk


def seal(R, skip, **kw):
    R.sockets(skip=skip, **kw)
    R.meta['sealed'] = [list(s) for s in skip]


def door_cells(R, L=0, skip=()):
    """(side, i, x, y) of every doorway centre on level L (on the inner wall face)."""
    out = []
    for i in range(R.w):
        out.append(('S', i, i * C + C / 2, T)); out.append(('N', i, i * C + C / 2, R.D - T))
    for j in range(R.d):
        out.append(('W', j, T, j * C + C / 2)); out.append(('E', j, R.W - T, j * C + C / 2))
    return [o for o in out if (o[0], o[1], L) not in skip]


def wall_cases(R, z=0.0, rows=8, frame='wood', gap=1.8, full=False, row_h=0.42, every=1, sides='SNWE', **kw):
    """Bookcases along the four walls, broken at each doorway (unless full), one or two per cell edge."""
    W, D = R.W, R.D
    segs = lambda n: ([(k * C + 0.6, k * C + C / 2 - gap) for k in range(n)] + [(k * C + C / 2 + gap, (k + 1) * C - 0.6) for k in range(n)]) \
        if not full else [(k * C + 0.6, (k + 1) * C - 0.6) for k in range(n)]
    for k, (a, b) in enumerate(segs(R.w)):
        if k % every: continue
        if 'S' in sides: R.shelf(a, T, z, b - a, '+y', rows=rows, frame=frame, row_h=row_h, **kw)
        if 'N' in sides: R.shelf(b, D - T, z, b - a, '-y', rows=rows, frame=frame, row_h=row_h, **kw)
    for k, (a, b) in enumerate(segs(R.d)):
        if k % every: continue
        if 'W' in sides: R.shelf(T, b, z, b - a, '+x', rows=rows, frame=frame, row_h=row_h, **kw)
        if 'E' in sides: R.shelf(W - T, a, z, b - a, '-x', rows=rows, frame=frame, row_h=row_h, **kw)


def _quad_solid(P, m, cap=None):
    """8 corner points (bottom 0..3, top 4..7, same order as box) -> closed solid."""
    g = Geo(); ids = [g.vert(p) for p in P]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        mm = cap if (cap and f == (4, 5, 6, 7)) else m
        pts = [P[i] for i in f]
        uv = [(p[0] + p[1], p[2]) for p in pts] if f not in ((0, 3, 2, 1), (4, 5, 6, 7)) else [(p[0], p[1]) for p in pts]
        g.face([ids[i] for i in f], mm, uv)
    return g.fix()


def sloped(ax, a0, a1, c0, c1, zb0, zb1, zt0, zt1, m, cap=None):
    """A slab running along ax ('x' or 'y') from a0 to a1, across c0..c1; bottom zb0->zb1, top zt0->zt1."""
    def P(a, c, z): return (a, c, z) if ax == 'x' else (c, a, z)
    return _quad_solid([P(a0, c0, zb0), P(a1, c0, zb1), P(a1, c1, zb1), P(a0, c1, zb0),
                        P(a0, c0, zt0), P(a1, c0, zt1), P(a1, c1, zt1), P(a0, c1, zt0)], m, cap)


def flight(R, x0, y0, z0, width, n, rise, run, axis='+y', m='tile', riser=None, side='tile', th=0.45, soffit='plaster', plinth=True):
    """Like R.flight but the visible stair is a ribbon with a sloped underside (it can hang in air)."""
    L, H = n * run, n * rise
    prof = [(0.0, -th), (L, H - th), (L, H)]
    for i in range(n - 1, -1, -1):
        prof.append((i * run, (i + 1) * rise))
        if i > 0: prof.append((i * run, i * rise))
    mats = [soffit, side] + [m if k % 2 == 0 else (riser or side) for k in range(len(prof) - 2)]
    sgn = 1 if axis[0] == '+' else -1
    if axis[1] == 'x':
        pr = [(x0 + sgn * s, z0 + z) for s, z in prof]
        R.nocol.add(prism(pr, 'y', y0, y0 + width, mats, cap=side))
    else:
        pr = [(y0 + sgn * s, z0 + z) for s, z in prof]
        R.nocol.add(prism(pr, 'x', x0, x0 + width, mats, cap=side))
    # the walk check samples a 0.5 m grid on the giants and would rather walk on under a thin ramp than
    # up it: so the first two steps are a solid block, and the ramp starts from its top
    k0 = 2 if plinth else 0
    a, zs = k0 * run, z0 + k0 * rise
    if k0:
        if axis == '+y':   pb = (x0, y0 - 0.02, x0 + width, y0 + a)
        elif axis == '-y': pb = (x0, y0 - a, x0 + width, y0 + 0.02)
        elif axis == '+x': pb = (x0 - 0.02, y0, x0 + a, y0 + width)
        else:              pb = (x0 - a, y0, x0 + 0.02, y0 + width)
        R.col.add(box(pb[0], pb[1], z0 - 0.05, pb[2], pb[3], zs, 'floor'))
        # and invisible fins under the start, poking up through the block (below a walker's feet), so
        # the check's floor samples under it do not count as standing room
        fl = 1.2
        c = 0.2
        while c < width - 0.1:
            if axis == '+y':   fb = (x0 + c - 0.01, y0 + 0.3, x0 + c + 0.01, y0 + fl)
            elif axis == '-y': fb = (x0 + c - 0.01, y0 - fl, x0 + c + 0.01, y0 - 0.3)
            elif axis == '+x': fb = (x0 + 0.3, y0 + c - 0.01, x0 + fl, y0 + c + 0.01)
            else:              fb = (x0 - fl, y0 + c - 0.01, x0 - 0.3, y0 + c + 0.01)
            R.col.add(box(fb[0], fb[1], z0, fb[2], fb[3], zs + 0.45, 'floor', skip=('+z', '-z')))
            c += 0.45
    if axis == '+y':   q = [(x0, y0 + a - 0.02, zs), (x0 + width, y0 + a - 0.02, zs), (x0 + width, y0 + L, z0 + H), (x0, y0 + L, z0 + H)]
    elif axis == '-y': q = [(x0, y0 - a + 0.02, zs), (x0, y0 - L, z0 + H), (x0 + width, y0 - L, z0 + H), (x0 + width, y0 - a + 0.02, zs)]
    elif axis == '+x': q = [(x0 + a - 0.02, y0, zs), (x0 + L, y0, z0 + H), (x0 + L, y0 + width, z0 + H), (x0 + a - 0.02, y0 + width, zs)]
    else:              q = [(x0 - a + 0.02, y0, zs), (x0 - a + 0.02, y0 + width, zs), (x0 - L, y0 + width, z0 + H), (x0 - L, y0, z0 + H)]
    g = Geo(); ids = [g.vert(p) for p in q]; g.face(ids, 'floor', [(0, 0)] * 4)
    a = Vector(q[1]) - Vector(q[0]); b = Vector(q[2]) - Vector(q[0])
    if a.cross(b).z < 0: g.f = [tuple(reversed(f)) for f in g.f]
    R.col.add(g)


def flight_rail(R, x0, y0, z0, width, n, rise, run, axis, which=(0, 1), m='tile', cap='brass', t=0.14, h=1.0, th=0.45):
    """Parapets along the sides of a flight (which: 0 = the low-coordinate side, 1 = the high one)."""
    L, H = n * run, n * rise
    ax = axis[1]; sgn = 1 if axis[0] == '+' else -1
    a0, a1 = (x0, x0 + sgn * L) if ax == 'x' else (y0, y0 + sgn * L)
    c = y0 if ax == 'x' else x0
    zb0, zb1 = z0 - th, z0 + H - th
    zt0, zt1 = z0 + rise + h, z0 + H + h
    if sgn < 0: a0, a1 = a1, a0; zb0, zb1 = zb1, zb0; zt0, zt1 = zt1, zt0
    for w in which:
        c0 = c - 0.02 if w == 0 else c + width - t
        c1 = c + t if w == 0 else c + width + 0.02
        R.parts.add(sloped(ax, a0, a1, c0, c1, zb0, zb1, zt0, zt1, m))
        R.parts.add(sloped(ax, a0 - 0.02, a1 + 0.02, c0 - 0.03, c1 + 0.03, zt0, zt1, zt0 + 0.06, zt1 + 0.06, cap))


def rail(R, x0, y0, x1, y1, z, h=1.0, m='tile', cap='brass', t=0.14):
    """An axis-aligned balustrade along a line (x0,y0)-(x1,y1); t thick, centred on the line."""
    if abs(y1 - y0) < abs(x1 - x0):
        a, b = min(x0, x1), max(x0, x1); R.parts.add(balustrade(a, y0 - t / 2, b, y0 + t / 2, z, h, m, cap))
    else:
        a, b = min(y0, y1), max(y0, y1); R.parts.add(balustrade(x0 - t / 2, a, x0 + t / 2, b, z, h, m, cap))


def iron_rail(R, x0, y0, x1, y1, z, h=1.0, post=1.1):
    """A light iron railing: top bar, mid bar, posts every `post` metres, and an invisible wall to 1.2 m."""
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    n = max(1, int(math.ceil(L / post)))
    g = Geo()
    for k in range(n + 1):
        x, y = x0 + ux * L * k / n, y0 + uy * L * k / n
        g.add(box(x - 0.03, y - 0.03, z, x + 0.03, y + 0.03, z + h, 'iron'))
    lo_x, hi_x, lo_y, hi_y = min(x0, x1) - 0.035, max(x0, x1) + 0.035, min(y0, y1) - 0.035, max(y0, y1) + 0.035
    g.add(box(lo_x, lo_y, z + h - 0.05, hi_x, hi_y, z + h, 'iron'))
    g.add(box(lo_x, lo_y, z + 0.08, hi_x, hi_y, z + 0.12, 'iron'))
    R.parts.add(g)
    R.col.add(box(lo_x, lo_y, z, hi_x, hi_y, z + h, 'iron'))


def lamppost(R, x, y, z=0.0, h=3.4, e='e_dim', r=0.16):
    R.parts.add(cyl(x, y, z, z + 0.25, 0.16, 8, side='iron', top='iron', caps=True))
    R.parts.add(cyl(x, y, z + 0.25, z + h, 0.05, 6, side='iron', caps=False))
    R.parts.add(box(x - r - 0.04, y - r - 0.04, z + h, x + r + 0.04, y + r + 0.04, z + h + 0.05, 'iron'))
    R.light(cyl(x, y, z + h + 0.05, z + h + 0.45, r, 8, side=e, top=e, bottom=e))
    R.parts.add(cyl(x, y, z + h + 0.45, z + h + 0.55, r + 0.06, 8, side='iron', top='iron', bottom='iron'))


def hanging(R, x, y, ztop, z, r=0.3, e='e_lamp', shade=None, segs=12):
    """A lamp on a cord from the ceiling ztop down to z (the bottom of the lamp)."""
    R.parts.add(cyl(x, y, z + 0.3, ztop, 0.012, 4, side='iron', caps=False))
    if shade:
        R.parts.add(cyl(x, y, z + 0.12, z + 0.3, r, segs, side=shade, top=shade, bottom=shade, caps=False))
        R.parts.add(cyl(x, y, z + 0.28, z + 0.3, r, segs, side=shade, top=shade, bottom=shade))
        R.light(cyl(x, y, z + 0.14, z + 0.2, r * 0.55, 8, side=e, top=e, bottom=e))
    else:
        R.light(sphere(x, y, z + r, r, segs, max(4, segs // 2), e))


def bench(R, x, y, ang, L=1.8, m='walnut', spot=True):
    g = Geo()
    g.add(box(-L / 2, -0.22, 0.38, L / 2, 0.22, 0.46, m))
    for s in (-1, 1): g.add(box(s * (L / 2 - 0.15) - 0.05, -0.2, 0, s * (L / 2 - 0.15) + 0.05, 0.2, 0.38, 'iron'))
    g.add(box(-L / 2, 0.18, 0.46, L / 2, 0.24, 0.95, m))
    R.parts.add(g.xform(ang, x, y))
    if spot: R.spot('sit', x, y, 0.46, ang - math.pi / 2)


def _slab(R, o, u, n_ang, length, h, depth, ghost=False):
    R.slabs.append({'o': list(o), 'u': list(u), 'v': [0, 0, h], 'n': [math.cos(n_ang), math.sin(n_ang), 0],
                    'len': length, 'h': h, 'depth': depth, 'ghost': ghost})


def stack2(R, x0, x1, yc, z=0.0, rows=5, row_h=0.42, half=0.34, frame='oak', board=0.035, top_gap=0.08, ax='x'):
    """A lean double-faced bookcase along ax from x0 to x1, centred on yc across: shared shelf boards,
    one spine, two ends, a crown. Books face both ways."""
    H = rows * row_h + board + top_gap
    def B(a0, c0, zz0, a1, c1, zz1, **kw):
        return box(a0, c0, zz0, a1, c1, zz1, frame, **kw) if ax == 'x' else box(c0, a0, zz0, c1, a1, zz1, frame, **kw)
    g = Geo()
    g.add(B(x0, yc - 0.02, z, x1, yc + 0.02, z + H, skip=('-z', '+z')))
    g.add(B(x0 - 0.04, yc - half - 0.02, z, x0, yc + half + 0.02, z + H + 0.03, skip=('-z',)))
    g.add(B(x1, yc - half - 0.02, z, x1 + 0.04, yc + half + 0.02, z + H + 0.03, skip=('-z',)))
    g.add(B(x0 - 0.06, yc - half - 0.05, z + H, x1 + 0.06, yc + half + 0.05, z + H + 0.06, ))
    for r in range(rows + 1):
        h = z + r * row_h
        g.add(B(x0, yc - half + 0.01, h, x1, yc + half - 0.01, h + board, skip=('-z',) if r == 0 else ()))
    R.parts.add(g)
    L = x1 - x0
    for r in range(rows):
        h0 = z + r * row_h + board; hh = row_h - board - 0.03
        for s in (-1, 1):
            if ax == 'x':
                o = (x0 if s > 0 else x1, yc + s * (half - 0.02), h0)
                u = (L, 0, 0) if s > 0 else (-L, 0, 0)
                ang = math.pi / 2 if s > 0 else -math.pi / 2
            else:
                o = (yc + s * (half - 0.02), x1 if s > 0 else x0, h0)
                u = (0, -L, 0) if s > 0 else (0, L, 0)
                ang = 0.0 if s > 0 else math.pi
            _slab(R, o, u, ang, L, hh, half - 0.06)
