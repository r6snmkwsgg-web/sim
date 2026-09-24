"""Shared helpers for batch d rooms (single cells)."""
from lib import *

I0, I1 = T, C - T          # interior bounds
M = C / 2                  # centre line (doorways)


def shell(R, H=TOP, floor='floor', wall='tile', top='plaster', seal=(), rect=None):
    """Doorways + the main hall cut. seal: sides ('N','S','E','W') to leave solid."""
    sealed = [(s, 0, 0) for s in seal]
    R.sockets(floor=floor, wall=wall, skip=tuple(sealed), rect=rect)
    if H:
        H = min(H, TOP - 0.05)
        R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, H, wall, bottom=floor, top=top))
    if sealed: R.meta['sealed'] = sealed
    R.meta['box'] = [[T, 0, T], [C - T, H or TOP, C - T]]


def wall_shelf(R, face, a, b, z=0.0, rows=6, off=0.0, **kw):
    """A bookcase against a wall plane. face: the way it faces ('+x','-x','+y','-y');
    the back sits on the plane at coordinate off along the facing axis (default: the room wall);
    a..b is its span along the other axis."""
    if face == '+y':   bookcase(R, a, off or I0, z, b - a, '+y', rows, **kw)
    elif face == '-y': bookcase(R, b, off or I1, z, b - a, '-y', rows, **kw)
    elif face == '+x': bookcase(R, off or I0, b, z, b - a, '+x', rows, **kw)
    else:              bookcase(R, off or I1, a, z, b - a, '-x', rows, **kw)


def shelf_at(R, cx, cy, z, length, ang, rows, **kw):
    """A bookcase whose back face is centred on (cx, cy), facing angle ang (radians)."""
    e = ang - math.pi / 2
    x = cx - math.cos(e) * length / 2; y = cy - math.sin(e) * length / 2
    return bookcase(R, x, y, z, length, ang, rows, **kw)


def pendant(R, x, y, z, r=0.18, m='e_lamp', top=TOP, rod='iron', shade='brass'):
    """A hanging lamp: a rod from the ceiling, a small shade, a glowing bulb disc under it."""
    s = 8 if r < 0.12 else 12
    R.nocol.add(box(x - 0.01, y - 0.01, z + 0.1, x + 0.01, y + 0.01, top, rod, skip=('-z', '+z')))
    R.nocol.add(cyl(x, y, z + 0.02, z + 0.12, r * 1.25, s, side=shade, top=shade, bottom=shade))
    R.light(cyl(x, y, z - 0.03, z + 0.02, r, s, side=m, top=m, bottom=m, caps=True))


def globe(R, x, y, z, r=0.15, m='e_lamp', segs=12):
    R.light(sphere(x, y, z, r, segs, max(4, segs // 2), m))


def ramp(R, pts):
    """An invisible walking surface (4 corners), made to face up."""
    g = Geo(); ids = [g.vert(p) for p in pts]; g.face(ids, 'floor', [(0, 0)] * 4)
    a = Vector(pts[1]) - Vector(pts[0]); b = Vector(pts[2]) - Vector(pts[0])
    if a.cross(b).z < 0: g.f = [tuple(reversed(f)) for f in g.f]
    R.col.add(g)


def armchair(R, x, y, ang, m='leather', sit=True):
    """A club armchair at (x, y) facing ang."""
    g = Geo()
    g.add(box(-0.38, -0.42, 0.08, 0.38, 0.42, 0.44, m))               # seat block
    g.add(box(-0.5, -0.46, 0.08, -0.3, 0.46, 1.0, m))                 # back
    g.add(box(-0.42, -0.5, 0.08, 0.42, -0.34, 0.66, m))               # arms
    g.add(box(-0.42, 0.34, 0.08, 0.42, 0.5, 0.66, m))
    g.add(box(-0.44, -0.44, 0.0, 0.4, 0.44, 0.08, 'walnut'))          # plinth
    R.parts.add(g.xform(ang, x, y, 0))
    if sit: R.spot('sit', x + math.cos(ang) * 0.05, y + math.sin(ang) * 0.05, 0.44, ang)


def chair(R, x, y, ang, m='walnut', sit=True):
    g = Geo()
    for (a, b) in ((-0.2, -0.2), (-0.2, 0.2), (0.2, -0.2), (0.2, 0.2)):
        g.add(box(a - 0.02, b - 0.02, 0, a + 0.02, b + 0.02, 0.45, m, skip=('-z',)))
    g.add(box(-0.23, -0.23, 0.45, 0.23, 0.23, 0.5, m))
    g.add(box(-0.25, -0.23, 0.5, -0.21, 0.23, 0.98, m))
    R.parts.add(g.xform(ang, x, y, 0))
    if sit: R.spot('sit', x, y, 0.5, ang)


def table(R, x0, y0, x1, y1, h=0.76, m='walnut', leg=0.06):
    R.parts.add(box(x0, y0, h - 0.05, x1, y1, h, m))
    for (x, y) in ((x0 + 0.05, y0 + 0.05), (x1 - 0.05 - leg, y0 + 0.05), (x0 + 0.05, y1 - 0.05 - leg), (x1 - 0.05 - leg, y1 - 0.05 - leg)):
        R.parts.add(box(x, y, 0, x + leg, y + leg, h - 0.05, m, skip=('-z',)))


def book(R, x, y, z, ang=0.0, m='leather', w=0.17, l=0.24, t=0.04, open_=False):
    """A lone book lying flat (or open, pages up)."""
    g = Geo()
    if open_:
        g.add(box(-w, -l / 2, 0, w, l / 2, 0.012, m, skip=('-z',)))
        g.add(box(-w + 0.01, -l / 2 + 0.01, 0.012, -0.004, l / 2 - 0.01, 0.03, 'ivory', skip=('-z', '-x', '+x')))
        g.add(box(0.004, -l / 2 + 0.01, 0.012, w - 0.01, l / 2 - 0.01, 0.03, 'ivory', skip=('-z', '-x', '+x')))
    else:
        g.add(box(-w / 2, -l / 2, 0, w / 2, l / 2, t, m))
    R.parts.add(g.xform(ang, x, y, z))


def exit_sign(R, x, y, z, face, w=0.5, h=0.2):
    """A little green sign on a wall; face = the direction it faces ('+x','-x','+y','-y')."""
    d = 0.05
    if face in ('+y', '-y'):
        s = 1 if face == '+y' else -1
        y0, y1 = sorted((y, y + s * d))
        R.nocol.add(box(x - w / 2 - 0.03, y0, z - 0.03, x + w / 2 + 0.03, y1, z + h + 0.03, 'iron'))
        yy = y1 if s > 0 else y0
        R.light(box(x - w / 2, min(yy, yy + s * 0.01), z, x + w / 2, max(yy, yy + s * 0.01), z + h, 'e_exit'))
    else:
        s = 1 if face == '+x' else -1
        x0, x1 = sorted((x, x + s * d))
        R.nocol.add(box(x0, y - w / 2 - 0.03, z - 0.03, x1, y + w / 2 + 0.03, z + h + 0.03, 'iron'))
        xx = x1 if s > 0 else x0
        R.light(box(min(xx, xx + s * 0.01), y - w / 2, z, max(xx, xx + s * 0.01), y + w / 2, z + h, 'e_exit'))


def brass_rail(R, x0, y0, z0, x1, y1, z1, h=0.95, post=1.1, m='brass', r=0.025, wall=True):
    """A straight brass handrail with posts (may slope), plus an invisible wall under it."""
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(math.ceil(L / post)))
    for k in range(n + 1):
        t = k / n
        x, y, z = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        R.parts.add(box(x - r, y - r, z, x + r, y + r, z + h, m, skip=('-z',)))
    # the rail itself: a thin slab along the line
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy * 0.03, ux * 0.03
    g = Geo()
    P = [(x0 - nx, y0 - ny, z0 + h), (x1 - nx, y1 - ny, z1 + h), (x1 + nx, y1 + ny, z1 + h), (x0 + nx, y0 + ny, z0 + h)]
    P += [(p[0], p[1], p[2] + 0.05) for p in P]
    ids = [g.vert(p) for p in P]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        g.face([ids[i] for i in f], m, [(0, 0)] * 4)
    R.parts.add(g.fix())
    if wall:   # invisible barrier so nothing slips between the posts
        g = Geo()
        P = [(x0 - nx, y0 - ny, z0), (x1 - nx, y1 - ny, z1), (x1 + nx, y1 + ny, z1), (x0 + nx, y0 + ny, z0)]
        P += [(p[0], p[1], p[2] + h) for p in P]
        ids = [g.vert(p) for p in P]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            g.face([ids[i] for i in f], 'tile', [(0, 0)] * 4)
        R.col.add(g.fix())


def loop(R, pts, z=0.0, close=True):
    ids = [R.navpt(x, y, z) for (x, y) in pts]
    R.link(*(ids + [ids[0]] if close else ids))
    return ids


def door_arch_cut(R, side, depth, floor='floor', wall='tile', w=DW, jamb=DJ, rise=None):
    """Extend the doorway's arch 'depth' metres into the room (a passage through thick walls)."""
    pr = arch_profile(0, w, 0, jamb, 18, rise)
    if side == 'S':   R.cut(prism([(p + M, q) for p, q in pr], 'y', -0.5, depth, arch_mats(len(pr), floor, wall)))
    elif side == 'N': R.cut(prism([(p + M, q) for p, q in pr], 'y', C - depth, C + 0.5, arch_mats(len(pr), floor, wall)))
    elif side == 'W': R.cut(prism([(p + M, q) for p, q in pr], 'x', -0.5, depth, arch_mats(len(pr), floor, wall)))
    else:             R.cut(prism([(p + M, q) for p, q in pr], 'x', C - depth, C + 0.5, arch_mats(len(pr), floor, wall)))


def fake_door(R, side, floor='floor', wall='tile', frame='walnut', sign=True, leaf='oak', depth=0.2):
    """Dress a sealed doorway: a shallow arched recess, a moulded frame, a sign over it."""
    pr = arch_profile(0, DW - 0.4, 0, DJ - 0.2, 18)
    g = prism([(p, q) for p, q in pr], 'y', -0.02, depth, arch_mats(len(pr), floor, wall))
    fr = Geo()
    # frame: two jambs and a lintel standing proud of the wall
    w2 = (DW - 0.4) / 2
    fr.add(box(-w2 - 0.22, -0.12, 0, -w2, 0.0, DJ + w2 + 0.05, frame))
    fr.add(box(w2, -0.12, 0, w2 + 0.22, 0.0, DJ + w2 + 0.05, frame))
    fr.add(box(-w2 - 0.3, -0.16, DJ + w2 + 0.05, w2 + 0.3, 0.0, DJ + w2 + 0.3, frame))
    # a flat leaf in the back of the recess (a door that does not open)
    lf = box(-w2 + 0.02, depth - 0.06, 0.0, w2 - 0.02, depth - 0.01, DJ - 0.2, leaf) if leaf else None
    ang, tx, ty = {'S': (0, M, I0), 'N': (math.pi, M, I1), 'W': (-math.pi / 2, I0, M), 'E': (math.pi / 2, I1, M)}[side]
    # local frame: x along the wall, y into the wall (away from the room)
    if side == 'S':   rot = lambda gg: gg.xform(math.pi, M, I0)
    elif side == 'N': rot = lambda gg: gg.xform(0, M, I1)
    elif side == 'W': rot = lambda gg: gg.xform(math.pi / 2, I0, M)
    else:             rot = lambda gg: gg.xform(-math.pi / 2, I1, M)
    R.cut(rot(g))
    R.parts.add(rot(fr))
    if lf: R.parts.add(rot(lf))
    if sign:
        s = Geo()
        s.add(box(-0.3, -0.07, DJ + w2 + 0.45, 0.3, 0.0, DJ + w2 + 0.72, 'iron'))
        R.nocol.add(rot(s))
        e = box(-0.26, -0.08, DJ + w2 + 0.48, 0.26, -0.07, DJ + w2 + 0.69, 'e_exit')
        R.light(rot(e))


def add_slab(R, x, y, z, length, a, h0, h1, depth=0.34, solid=True):
    """One row of books (what R.shelf adds per row): (x, y, z) back-left corner of the case, a its facing."""
    th = a - math.pi / 2
    c, s_ = math.cos(th), math.sin(th)
    rot = lambda p: (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c, p[2])
    o = rot((0, depth - 0.02, h0)); o = (o[0] + x, o[1] + y, o[2] + z)
    R.slabs.append({'o': o, 'u': list(rot((length, 0, 0))), 'v': [0, 0, h1 - h0], 'n': [math.cos(a), math.sin(a), 0],
                    'len': length, 'h': h1 - h0, 'depth': depth - 0.04, 'ghost': not solid})


def bookcase(R, x, y, z, length, dirn, rows=5, row_h=0.42, depth=0.34, frame='wood', board=0.035, top_gap=0.08,
             back=True, backface=False, sides=True, crown=True, solid=True):
    """Like R.shelf (same placement and books) but with only the faces you can see: much lighter.
    backface=True also closes the back (for cases standing free of a wall)."""
    a = {'+y': math.pi / 2, '-y': -math.pi / 2, '+x': 0.0, '-x': math.pi}[dirn] if isinstance(dirn, str) else dirn
    th = a - math.pi / 2
    H = rows * row_h + board + top_gap
    g = Geo()
    if back: g.add(box(0, 0, 0, length, 0.02, H, frame, skip=('-z', '+z', '-x', '+x') + (() if backface else ('-y',))))
    if sides:
        sk = ('-z',) if backface else ('-z', '-y')
        g.add(box(-0.04, 0, 0, 0, depth + 0.02, H + 0.03, frame, skip=sk))
        g.add(box(length, 0, 0, length + 0.04, depth + 0.02, H + 0.03, frame, skip=sk))
    if crown: g.add(box(-0.06, 0, H, length + 0.06, depth + 0.05, H + 0.06, frame, skip=() if backface else ('-y',)))
    for r in range(rows + 1):
        h = r * row_h
        g.add(box(0, 0.02, h, length, depth + 0.01, h + board, frame, skip=('-x', '+x', '-y') + (('-z',) if r == 0 else ())))
    g.xform(th, x, y, z)
    (R.parts if solid else R.nocol).add(g)
    for r in range(rows):
        h0 = r * row_h + board
        add_slab(R, x, y, z, length, a, h0, h0 + row_h - board - 0.03, depth, solid)


def slope_y(x0, x1, y0, y1, b0, b1, t0, t1, m='tile'):
    """Like slope_box, but the bottom (b0 -> b1) and top (t0 -> t1) slope along y from y0 to y1."""
    return slope_box(y0, y1, -x1, -x0, b0, b1, t0, t1, m).xform(math.pi / 2)
