"""Shared helpers for batch "a" rooms (empty, waiting, chapel, lecture, ...)."""
from lib import *


# ---------------------------------------------------------------------------
# shells
def shell(R, x0=None, y0=None, x1=None, y1=None, h=TOP - 0.1, wall='tile', floor='floor', ceil='plaster', skip=()):
    """Doorways plus the main hall. When the hall is inset from T (thick walls), the doorway
    tunnels are carried through the extra thickness."""
    x0 = T if x0 is None else x0; y0 = T if y0 is None else y0
    x1 = C - T if x1 is None else x1; y1 = C - T if y1 is None else y1
    R.sockets(floor=floor, wall=wall, skip=skip)
    R.cut(box(x0 - 0.02, y0 - 0.02, 0, x1 + 0.02, y1 + 0.02, h, wall, bottom=floor, top=ceil))
    pr = arch_profile(0, DW, 0, DJ)
    for side, a, b in (('S', T, y0 + 0.05), ('N', y1 - 0.05, C - T), ('W', T, x0 + 0.05), ('E', x1 - 0.05, C - T)):
        if (side, 0, 0) in skip or b - a < 0.62: continue
        if side in 'SN': R.cut(prism([(p + C / 2, q) for p, q in pr], 'y', a, b, arch_mats(len(pr), floor, wall)))
        else: R.cut(prism([(p + C / 2, q) for p, q in pr], 'x', a, b, arch_mats(len(pr), floor, wall)))


def pointed_profile(c, w, z0, jamb, rise, segs=12):
    """A two-centred pointed (gothic) arch: rise must exceed w/2."""
    r = w / 2
    Rr = (r * r + rise * rise) / (2 * r)
    zc = z0 + jamb
    pts = [(c - r, z0), (c + r, z0), (c + r, zc)]
    a1 = math.acos((Rr - r) / Rr)          # right arc centred at c + r - Rr
    for k in range(1, segs + 1):
        t = a1 * k / segs
        pts.append((c + r - Rr + Rr * math.cos(t), zc + Rr * math.sin(t)))
    for k in range(segs - 1, 0, -1):
        t = a1 * k / segs
        pts.append((c - r + Rr - Rr * math.cos(t), zc + Rr * math.sin(t)))
    pts.append((c - r, zc))
    # drop the duplicated apex
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-6: out.append(p)
    return out


def circle_pts(cx, cz, r, n=32, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cz + r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


# ---------------------------------------------------------------------------
# oriented pieces
def obox(x0, y0, x1, y1, z0, z1, w, m='tile', **kw):
    """A box of width w running from (x0, y0) to (x1, y1) in plan."""
    L = math.hypot(x1 - x0, y1 - y0)
    return box(0, -w / 2, z0, L, w / 2, z1, m, **kw).xform(math.atan2(y1 - y0, x1 - x0), x0, y0, 0)


def beam(p0, p1, w, m='brass', h=None):
    """A square-section bar between two 3D points (w wide, h tall)."""
    h = w if h is None else h
    d = [p1[i] - p0[i] for i in range(3)]
    L = math.sqrt(sum(c * c for c in d)) or 1e-6
    d = [c / L for c in d]
    up = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
    s = (d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0])
    sl = math.sqrt(sum(c * c for c in s)); s = [c / sl for c in s]
    u = (s[1] * d[2] - s[2] * d[1], s[2] * d[0] - s[0] * d[2], s[0] * d[1] - s[1] * d[0])
    g = Geo(); ids = []
    for p in (p0, p1):
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ids.append(g.vert([p[i] + s[i] * a * w / 2 + u[i] * b * h / 2 for i in range(3)]))
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        g.face([ids[i] for i in f], m, [(0, 0), (1, 0), (1, 1), (0, 1)])
    return g.fix()


def rot(g, ax, ang, cx=0.0, cy=0.0, cz=0.0):
    """Rotate a Geo about an axis ('x', 'y' or 'z') through (cx, cy, cz)."""
    c, s = math.cos(ang), math.sin(ang)
    out = []
    for x, y, z in g.v:
        x, y, z = x - cx, y - cy, z - cz
        if ax == 'x': y, z = y * c - z * s, y * s + z * c
        elif ax == 'y': x, z = x * c + z * s, -x * s + z * c
        else: x, y = x * c - y * s, x * s + y * c
        out.append((x + cx, y + cy, z + cz))
    g.v = out
    return g


def xz_plate(poly, y0, y1, m, cap=None):
    """A flat shape drawn in the x-z plane (a wall facing +-y), extruded from y0 to y1."""
    return prism(poly, 'y', y0, y1, m, cap=cap or m)


def yz_plate(poly, x0, x1, m, cap=None):
    return prism(poly, 'x', x0, x1, m, cap=cap or m)


def quad_poly(cx, cz, L, w, ang):
    """A rectangle (for strokes and hands) in a plane, from (cx, cz) along angle ang, length L, width w."""
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + s * w / 2, cz - c * w / 2), (cx + c * L + s * w / 2, cz + s * L - c * w / 2),
            (cx + c * L - s * w / 2, cz + s * L + c * w / 2), (cx - s * w / 2, cz + c * w / 2)]


# ---------------------------------------------------------------------------
# rails
def rail(R, x0, y0, x1, y1, z=0.0, h=0.95, m='brass', post=1.1, solid=False, mat='tile'):
    """A brass rail from (x0,y0) to (x1,y1) standing on z: posts at most `post` apart, a top bar
    and a mid bar, plus an invisible wall so nobody slips through. solid=True: a stone balustrade."""
    if solid:
        R.parts.add(obox(x0, y0, x1, y1, z, z + h, 0.2, mat, skip=('-z',)))
        R.parts.add(obox(x0, y0, x1, y1, z + h, z + h + 0.06, 0.26, m))
        return
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(math.ceil(L / post)))
    for k in range(n + 1):
        t = k / n; x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        R.nocol.add(box(x - 0.025, y - 0.025, z, x + 0.025, y + 0.025, z + h, m, skip=('-z', '+z')))
    R.nocol.add(obox(x0, y0, x1, y1, z + h, z + h + 0.05, 0.06, m))
    R.nocol.add(obox(x0, y0, x1, y1, z + h * 0.5, z + h * 0.5 + 0.03, 0.03, m, skip=('-x', '+x')))
    R.col.add(obox(x0, y0, x1, y1, z, z + h + 0.15, 0.06, 'tile'))


def stair_rail(R, x0, y0, z0, x1, y1, z1, h=0.95, m='brass', post=1.1):
    """A handrail following a stair's slope from (x0,y0,z0) to (x1,y1,z1) (the nosing line)."""
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(math.ceil(L / post)))
    for k in range(n + 1):
        t = k / n; x, y, z = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        R.parts.add(box(x - 0.025, y - 0.025, z - 0.1, x + 0.025, y + 0.025, z + h, m))
    R.parts.add(beam((x0, y0, z0 + h), (x1, y1, z1 + h), 0.06, m, 0.05))
    R.parts.add(beam((x0, y0, z0 + h * 0.5), (x1, y1, z1 + h * 0.5), 0.03, m))
    # invisible sloped wall
    g = Geo()
    dx, dy = x1 - x0, y1 - y0; nx, ny = -dy / L * 0.03, dx / L * 0.03
    P = [(x0 - nx, y0 - ny, z0 - 0.3), (x1 - nx, y1 - ny, z1 - 0.3), (x1 + nx, y1 + ny, z1 - 0.3), (x0 + nx, y0 + ny, z0 - 0.3)]
    P += [(p[0], p[1], p[2] + h + 0.45) for p in P]
    ids = [g.vert(p) for p in P]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        g.face([ids[i] for i in f], 'tile', [(0, 0)] * 4)
    R.col.add(g.fix())


# ---------------------------------------------------------------------------
# bookcases
# ---------------------------------------------------------------------------
# a lighter bookcase: same slabs as Room.shelf, but only the faces you can see are drawn (not
# collided), and one invisible box does the colliding. About a third of the bytes.
def shelf(R, x, y, z, length, dirn, rows=5, row_h=0.42, depth=0.34, frame='wood', board=0.035, top_gap=0.08,
          back=True, sides=True, crown=True, solid=True, open_back=False):
    a = {'+y': math.pi / 2, '-y': -math.pi / 2, '+x': 0.0, '-x': math.pi}[dirn] if isinstance(dirn, str) else dirn
    th = a - math.pi / 2
    Hh = rows * row_h + board + top_gap
    g = Geo()
    if back: g.add(box(0, 0, 0, length, 0.02, Hh, frame, skip=('-x', '+x', '-z', '+z') + (() if open_back else ('-y',))))
    if sides:
        for (x0, x1, sk) in ((-0.04, 0, '+x'), (length, length + 0.04, '-x')):
            g.add(box(x0, 0, 0, x1, depth + 0.02, Hh + 0.03, frame, skip=('-z', '-y') + (('+z',) if crown else ())))
    if crown: g.add(box(-0.06, 0, Hh, length + 0.06, depth + 0.05, Hh + 0.06, frame, skip=('-y',)))
    for r in range(rows + 1):
        h = r * row_h
        sk = ('-y',) + (('-x', '+x') if sides else ()) + (('-z',) if r == 0 else ()) + (('+z',) if (r == rows and crown and top_gap < 0.01) else ())
        g.add(box(0, 0.02, h, length, depth + 0.01, h + board, frame, skip=sk))
    g.xform(th, x, y, z)
    R.nocol.add(g)
    if solid:
        R.col.add(box(-0.04, 0, 0, length + 0.04, depth + 0.03, Hh + 0.06, 'tile').xform(th, x, y, z))
    c, s_ = math.cos(th), math.sin(th)
    rot_ = lambda p: (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c, p[2])
    ids = []
    for r in range(rows):
        h0 = r * row_h + board; h1 = h0 + row_h - board - 0.03
        o = rot_((0, depth - 0.02, h0)); o = (o[0] + x, o[1] + y, o[2] + z)
        R.slabs.append({'o': o, 'u': list(rot_((length, 0, 0))), 'v': [0, 0, h1 - h0], 'n': [math.cos(a), math.sin(a), 0],
                        'len': length, 'h': h1 - h0, 'depth': depth - 0.04, 'ghost': not solid})
        ids.append(len(R.slabs) - 1)
    return ids



def sh(R, facing, bk, a, b, z=0.0, rows=5, **kw):
    """A bookcase against a line: facing '+y'/'-y' (back at y=back, spanning x a..b) or '+x'/'-x'
    (back at x=back, spanning y a..b)."""
    L = b - a
    if facing == '+y': return shelf(R, a, bk, z, L, '+y', rows=rows, **kw)
    if facing == '-y': return shelf(R, b, bk, z, L, '-y', rows=rows, **kw)
    if facing == '+x': return shelf(R, bk, b, z, L, '+x', rows=rows, **kw)
    return shelf(R, bk, a, z, L, '-x', rows=rows, **kw)


def stack(R, axis, c, a, b, z=0.0, rows=5, depth=0.34, cap='wood', **kw):
    """A double-sided freestanding bookcase on centre line c, running along axis from a to b."""
    if axis == 'x':
        sh(R, '+y', c + 0.01, a, b, z, rows, depth=depth, **kw)
        sh(R, '-y', c - 0.01, a, b, z, rows, depth=depth, **kw)
    else:
        sh(R, '+x', c + 0.01, a, b, z, rows, depth=depth, **kw)
        sh(R, '-x', c - 0.01, a, b, z, rows, depth=depth, **kw)


def ang_shelf(R, x, y, ang, L, z=0.0, rows=5, **kw):
    """A bookcase centred at (x, y) whose front faces angle ang (radians)."""
    th = ang - math.pi / 2
    bx, by = x - math.cos(th) * L / 2, y - math.sin(th) * L / 2
    return shelf(R, bx, by, z, L, ang, rows=rows, **kw)


def inv_shelf(R, x, y, ztop, length, dirn, rows=5, row_h=0.42, depth=0.34, frame='wood', book_h=0.24):
    """An upside-down bookcase fixed to a ceiling at ztop: its crown against the ceiling, books hanging
    from the (now upper) boards."""
    save, savec = R.nocol, R.col; R.nocol = Geo(); R.col = Geo(); n0 = len(R.slabs)
    shelf(R, x, y, 0.0, length, dirn, rows=rows, row_h=row_h, depth=depth, frame=frame)
    g = R.nocol; gc = R.col; R.nocol, R.col = save, savec
    gc.v = [(a, b, ztop - c) for a, b, c in gc.v]; gc.f = [tuple(reversed(f)) for f in gc.f]; gc.uv = [list(reversed(u)) for u in gc.uv]
    R.col.add(gc)
    g.v = [(a, b, ztop - c) for a, b, c in g.v]
    g.f = [tuple(reversed(f)) for f in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    R.nocol.add(g)
    board = 0.035
    for r, s in enumerate(R.slabs[n0:]):
        # row r (counted from the crown down); its upper board underside is at ztop - (r*row_h + board)... mirrored:
        h0 = r * row_h + board                      # original bottom of the row (above the board)
        z_board = ztop - h0                         # that board, mirrored, is now above the row
        s['o'] = [s['o'][0], s['o'][1], z_board - book_h]
        s['v'] = [0, 0, book_h]; s['h'] = book_h


# ---------------------------------------------------------------------------
# furniture and lamps
def chair(x, y, a, frame='walnut', seat='leather', back_h=1.0):
    """A chair at (x, y); the sitter faces angle a."""
    g = Geo()
    for (px, py) in ((-0.2, -0.2), (0.2, -0.2), (0.2, 0.2), (-0.2, 0.2)):
        g.add(box(px - 0.02, py - 0.02, 0, px + 0.02, py + 0.02, 0.42, frame, skip=('-z', '+z')))
    g.add(box(-0.23, -0.23, 0.42, 0.23, 0.23, 0.48, seat, sides=frame))
    g.add(box(-0.25, -0.23, 0.48, -0.2, 0.23, back_h, frame, skip=('-z',)))
    return g.xform(a, x, y, 0)


def table(x0, y0, x1, y1, h=0.76, m='walnut', top=None):
    g = box(x0, y0, h - 0.05, x1, y1, h, m, top=top)
    for (px, py) in ((x0 + 0.08, y0 + 0.08), (x1 - 0.08, y0 + 0.08), (x1 - 0.08, y1 - 0.08), (x0 + 0.08, y1 - 0.08)):
        g.add(box(px - 0.04, py - 0.04, 0, px + 0.04, py + 0.04, h - 0.05, m, skip=('-z',)))
    return g


def bulb(R, x, y, z, r=0.12, m='e_lamp', top=TOP - 0.1, cord='iron', shade=None):
    """A bare bulb hanging on a cord from the ceiling."""
    R.light(sphere(x, y, z, r, 8, 4, m))
    R.nocol.add(cyl(x, y, z + r * 0.8, top, 0.01, 6, side=cord, caps=False))
    if shade:
        R.nocol.add(cyl(x, y, z + r * 0.6, z + r * 1.4, r * 0.7, 12, side=shade, top=shade, bottom=shade))


def desk_lamp(R, x, y, z, m='e_lamp'):
    """A green banker's lamp standing on a table top at height z."""
    R.parts.add(cyl(x, y, z, z + 0.03, 0.08, 12, side='brass', top='brass'))
    R.parts.add(cyl(x, y, z + 0.03, z + 0.36, 0.012, 6, side='brass', caps=False))
    R.parts.add(obox(x - 0.17, y, x + 0.17, y, z + 0.36, z + 0.44, 0.13, 'green'))
    R.light(obox(x - 0.15, y, x + 0.15, y, z + 0.345, z + 0.36, 0.09, m))


def candle(R, x, y, z, h=0.25, r=0.03, stand=0.0):
    if stand > 0:
        R.parts.add(cyl(x, y, z, z + 0.04, 0.14, 12, side='brass', top='brass'))
        R.parts.add(cyl(x, y, z + 0.04, z + stand, 0.02, 6, side='brass', caps=False))
        R.parts.add(cyl(x, y, z + stand, z + stand + 0.03, 0.06, 10, side='brass', top='brass', bottom='brass'))
        z = z + stand + 0.03
    R.nocol.add(cyl(x, y, z, z + h, r, 6, side='ivory', top='ivory', bottom='ivory'))
    R.light(box(x - r * 0.5, y - r * 0.5, z + h + 0.01, x + r * 0.5, y + r * 0.5, z + h + 0.07, 'e_candle'))


def ladder(x, y, a, h=4.0, lean=0.9, m='oak', rail='brass'):
    """A rolling library ladder leaning against a bookcase face at (x, y); a is the direction the
    ladder stands out from the shelf (its foot is `lean` out that way). Draw it in nocol."""
    g = Geo()
    for s in (-0.23, 0.23):
        g.add(beam((lean, s, 0.08), (0.05, s, h), 0.06, m, 0.04))
    n = int(h / 0.3)
    for k in range(1, n):
        t = k / n
        g.add(box(lean + (0.05 - lean) * t - 0.03, -0.23, h * t - 0.015 + 0.08 * (1 - t), lean + (0.05 - lean) * t + 0.03, 0.23, h * t + 0.015 + 0.08 * (1 - t), m, skip=('-y', '+y')))
    for s in (-0.23, 0.23):
        g.add(cyl(lean, s, 0, 0.08, 0.04, 6, side=rail, top=rail, caps=True))
    g.add(box(0.0, -0.3, h - 0.03, 0.06, 0.3, h + 0.02, rail))
    return g.xform(a, x, y, 0)


def stair_side(R, x0, y0, x1, y1, z0, z1, m='tile'):
    """A solid wall under/along the side of a flight: a sloped-top slab from z0 at (x0,y0) to z1 at (x1,y1)."""
    if abs(y1 - y0) < 1e-6:   # runs along x
        R.parts.add(slope_box(min(x0, x1), max(x0, x1), y0 - 0.08, y0 + 0.08, 0, 0, z0 if x0 < x1 else z1, z1 if x0 < x1 else z0, m))
    else:
        g = slope_box(min(y0, y1), max(y0, y1), -0.08, 0.08, 0, 0, z0 if y0 < y1 else z1, z1 if y0 < y1 else z0, m)
        g.v = [(-b + x0, a, c) for a, b, c in g.v]   # rotate a quarter turn: along y
        R.parts.add(g)


def navloop(R, pts, z=0.0, close=True):
    ids = [R.navpt(x, y, z) for (x, y) in pts]
    R.link(*ids)
    if close: R.link(ids[-1], ids[0])
    return ids


def tidy(R):
    """Round the book slabs' numbers (they travel as plain JSON, so every digit costs)."""
    r = lambda v: [round(float(c), 4) + 0.0 for c in v]
    for s in R.slabs:
        for k in ('o', 'u', 'v', 'n'): s[k] = r(s[k])
        for k in ('len', 'h', 'depth'): s[k] = round(float(s[k]), 4)
    return R


def frustum(cx, cy, z0, z1, r0, r1, segs=16, m='green', inner=None, t=0.015):
    """A lampshade: an open truncated cone from radius r0 at z0 to r1 at z1, with an inside face."""
    g = Geo()
    ang = [2 * math.pi * k / segs for k in range(segs)]
    for (dr, mm, flip_) in ((0.0, m, False), (-t, inner or m, True)):
        b = [g.vert((cx + (r0 + dr) * math.cos(a), cy + (r0 + dr) * math.sin(a), z0)) for a in ang]
        tp = [g.vert((cx + (r1 + dr) * math.cos(a), cy + (r1 + dr) * math.sin(a), z1)) for a in ang]
        for k in range(segs):
            j = (k + 1) % segs
            f = [b[k], b[j], tp[j], tp[k]]
            u = [(ang[k] * r0, z0), (ang[k] * r0 + 0.1, z0), (ang[k] * r0 + 0.1, z1), (ang[k] * r0, z1)]
            if flip_: f, u = f[::-1], u[::-1]
            g.face(f, mm, u)
    return g


def floor_lamp(R, x, y, h, shade='green', m='e_lamp', scale=1.0):
    """A standing lamp: iron foot, brass pole, a green conical shade with a glowing disc under it."""
    s = scale
    R.nocol.add(cyl(x, y, 0, 0.04, 0.2 * s, 8, side='iron', top='iron', bottom='iron'))
    R.nocol.add(cyl(x, y, 0.04, h, 0.022 * s, 4, side='brass', caps=False))
    R.col.add(box(x - 0.05, y - 0.05, 0, x + 0.05, y + 0.05, h, 'tile'))
    R.nocol.add(frustum(x, y, h - 0.28 * s, h + 0.02, 0.34 * s, 0.12 * s, 12, shade, inner='ivory'))
    R.light(cyl(x, y, h - 0.16 * s, h - 0.13 * s, 0.14 * s, 8, side=m, top=m, bottom=m))


def open_flight(R, x0, y0, z0, width, n, rise, run, tread='oak', stringer='walnut'):
    """An open stair climbing +y: floating treads on two stringers, with the usual invisible ramp."""
    save = R.nocol; R.nocol = Geo()
    R.flight(x0, y0, z0, width, n, rise, run, '+y')
    R.nocol = save
    for k in range(n):
        zt = z0 + (k + 1) * rise
        R.nocol.add(box(x0 + 0.06, y0 + k * run - 0.02, zt - 0.05, x0 + width - 0.06, y0 + (k + 1) * run + 0.02, zt, tread))
    L = n * run
    for x in (x0 + 0.04, x0 + width - 0.04):
        R.nocol.add(beam((x, y0 - 0.1, z0 + 0.05), (x, y0 + L, z0 + n * rise - 0.12), 0.08, stringer, 0.34))
