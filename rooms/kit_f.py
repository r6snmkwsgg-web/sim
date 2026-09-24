"""Shared helpers for batch f rooms (rails, stacks, book pillars, domes, lamps)."""
from lib import *


def bar(p0, p1, w=0.05, h=None, m='brass'):
    """An oriented box (square-ish section w x h) from point p0 to point p1 (centre line)."""
    h = h or w
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    hl = math.hypot(dx, dy)
    if hl < 1e-6:
        n = (1.0, 0.0, 0.0)
    else:
        n = (-dy / hl, dx / hl, 0.0)
    d = (dx / L, dy / L, dz / L)
    u = (d[1] * n[2] - d[2] * n[1], d[2] * n[0] - d[0] * n[2], d[0] * n[1] - d[1] * n[0])
    g = Geo()
    P = []
    for p in (p0, p1):
        for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            P.append(tuple(p[i] + a * n[i] * w / 2 + b * u[i] * h / 2 for i in range(3)))
    ids = [g.vert(p) for p in P]
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        g.face([ids[i] for i in f], m, [(0, 0), (L, 0), (L, w), (0, w)])
    return g.fix()


def rail_line(R, x0, y0, z0, x1, y1, z1, h=0.95, m='brass', post=None, spacing=1.0, mid=False, ends=True):
    """A post-and-rail balustrade from (x0,y0) to (x1,y1); z0/z1 = walking surface at each end."""
    post = post or m
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(math.ceil(L / spacing)))
    g = Geo()
    for k in range(n + 1):
        if not ends and k in (0, n): continue
        t = k / n
        x, y, z = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        g.add(box(x - 0.028, y - 0.028, z, x + 0.028, y + 0.028, z + h, post, skip=('-z',)))
    g.add(bar((x0, y0, z0 + h), (x1, y1, z1 + h), 0.07, 0.05, m))
    if mid:
        g.add(bar((x0, y0, z0 + h * 0.5), (x1, y1, z1 + h * 0.5), 0.035, 0.035, post))
    R.parts.add(g)


def balus(R, x0, y0, x1, y1, z, h=1.0, m='tile', cap='brass'):
    """Solid stone balustrade between two points on an axis line (0.2 thick)."""
    t = 0.1
    if abs(y1 - y0) < 1e-6:
        a, b = min(x0, x1), max(x0, x1)
        R.parts.add(balustrade(a, y0 - t, b, y0 + t, z, h, m, cap))
    else:
        a, b = min(y0, y1), max(y0, y1)
        R.parts.add(balustrade(x0 - t, a, x0 + t, b, z, h, m, cap))


def _gaps(a, b, opens):
    """Split [a, b] removing the open intervals; returns kept pieces."""
    segs = [(a, b)]
    for (o0, o1) in opens:
        nxt = []
        for (s0, s1) in segs:
            if o1 <= s0 or o0 >= s1: nxt.append((s0, s1)); continue
            if o0 > s0: nxt.append((s0, o0))
            if o1 < s1: nxt.append((o1, s1))
        segs = nxt
    return [s for s in segs if s[1] - s[0] > 0.05]


def rect_rails(R, x0, y0, x1, y1, z, opens=None, sides='SNWE', kind='rail', inset=0.06, **kw):
    """Rails round a rectangle at height z. opens: {'S': [(xa, xb)], 'W': [(ya, yb)], ...}.
    kind 'rail' (post and brass rail) or 'stone' (solid balustrade). Rails sit just inside the edge."""
    opens = opens or {}
    e = inset
    for s in sides:
        if s in 'SN':
            y = y0 + e if s == 'S' else y1 - e
            for (a, b) in _gaps(x0, x1, opens.get(s, [])):
                if kind == 'rail': rail_line(R, a + (e if a == x0 else 0), y, z, b - (e if b == x1 else 0), y, z, **kw)
                else: balus(R, a, y + (0.04 if s == 'S' else -0.04), b, y + (0.04 if s == 'S' else -0.04), z, **kw)
        else:
            x = x0 + e if s == 'W' else x1 - e
            for (a, b) in _gaps(y0, y1, opens.get(s, [])):
                if kind == 'rail': rail_line(R, x, a + (e if a == y0 else 0), z, x, b - (e if b == y1 else 0), z, **kw)
                else: balus(R, x + (0.04 if s == 'W' else -0.04), a, x + (0.04 if s == 'W' else -0.04), b, z, **kw)


def flight_box(x0, y0, width, n, run, axis):
    """Plan rectangle (x0, y0, x1, y1) covered by a flight."""
    L = n * run
    if axis == '+y': return (x0, y0, x0 + width, y0 + L)
    if axis == '-y': return (x0, y0 - L, x0 + width, y0)
    if axis == '+x': return (x0, y0, x0 + L, y0 + width)
    return (x0 - L, y0, x0, y0 + width)


def flight(R, x0, y0, z0, width, n, rise, run, axis, m='terrazzo', side='tile', rails='LR', rail_m='brass', skip_lo=0.0, skip_hi=0.0, h=0.95):
    """R.flight plus handrails on its sides. rails: 'L'/'R' = the sides at the lower/higher cross
    coordinate (x0 side is 'L' for a y flight, y0 side is 'L' for an x flight).
    skip_lo/skip_hi: leave the rail off this far from the foot/top."""
    R.flight(x0, y0, z0, width, n, rise, run, axis, m=m, side=side)
    L = n * run
    sg = 1 if axis[0] == '+' else -1
    for s in rails:
        off = 0.06 if s == 'L' else width - 0.06
        a, b = skip_lo, L - skip_hi
        za, zb = z0 + rise + a * n * rise / L, z0 + rise + b * n * rise / L - rise
        zb = max(zb, za)
        if axis[1] == 'y':
            rail_line(R, x0 + off, y0 + sg * a, za, x0 + off, y0 + sg * b, zb, h=h, m=rail_m)
        else:
            rail_line(R, x0 + sg * a, y0 + off, za, x0 + sg * b, y0 + off, zb, h=h, m=rail_m)


def slab_row(R, ox, oy, z, length, a, rows, row_h=0.42, depth=0.32, board=0.035):
    """Add book slabs only (no frame) for a shelf face: (ox, oy) = the corner where the face starts
    (on the back plane), running along angle a - pi/2, facing angle a."""
    th = a - math.pi / 2
    c, s_ = math.cos(th), math.sin(th)
    rot = lambda p: (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c, p[2])
    for r in range(rows):
        h0 = r * row_h + board; h1 = h0 + row_h - board - 0.03
        o = rot((0, depth - 0.02, h0)); o = (o[0] + ox, o[1] + oy, o[2] + z)
        R.slabs.append({'o': o, 'u': list(rot((length, 0, 0))), 'v': [0, 0, h1 - h0], 'n': [math.cos(a), math.sin(a), 0],
                        'len': length, 'h': h1 - h0, 'depth': depth - 0.04, 'ghost': False})


def book_pillar(R, cx, cy, z0, s, rows, z_top=None, row_h=0.42, depth=0.3, frame='wood', core='wood', board=0.04, cap='tile'):
    """A square column clad in books on all four faces. s = half-size of the core (books stand
    in front of it, depth deep). One shelf plate per row runs right round the column."""
    H = rows * row_h + board
    S = s + depth
    g = Geo()
    zt = z_top if z_top is not None else z0 + H + 0.1
    g.add(box(cx - s, cy - s, z0, cx + s, cy + s, zt, core, skip=('-z',) + (('+z',) if z_top is not None else ())))
    for r in range(rows + 1):
        h = z0 + r * row_h
        g.add(box(cx - S, cy - S, h, cx + S, cy + S, h + board, frame, skip=('-z',) if r == 0 else ()))
    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x, y = cx + sx * (S - 0.03), cy + sy * (S - 0.03)
        g.add(box(x - 0.035, y - 0.035, z0 + board, x + 0.035, y + 0.035, z0 + H, frame, skip=('-z', '+z')))
    g.add(box(cx - S - 0.05, cy - S - 0.05, z0 + H, cx + S + 0.05, cy + S + 0.05, z0 + H + 0.12, cap))
    R.parts.add(g)
    L = 2 * s - 0.1
    for k in range(4):
        a = k * math.pi / 2               # face normal
        nx, ny = math.cos(a), math.sin(a)
        tx, ty = math.cos(a - math.pi / 2), math.sin(a - math.pi / 2)
        ox, oy = cx + nx * s - tx * (L / 2), cy + ny * s - ty * (L / 2)
        slab_row(R, ox, oy, z0, L, a, rows, row_h, depth + 0.02, board)


def stack2(R, x0, y0, ang, L, z0, rows, depth=0.32, frame='wood', row_h=0.42, board=0.035, crown='wood', ends=None):
    """A free-standing double-sided bookcase. Its spine runs from (x0, y0) along angle ang for L."""
    H = rows * row_h + board + 0.08
    d = depth
    ends = ends or frame
    g = Geo()
    g.add(box(0, -0.02, 0, L, 0.02, H, frame, skip=('-z',)))
    for r in range(rows + 1):
        h = r * row_h
        g.add(box(0, -d, h, L, d, h + board, frame, skip=('-z',) if r == 0 else ()))
    g.add(box(-0.05, -d - 0.03, H, L + 0.05, d + 0.03, H + 0.07, crown))
    g.add(box(-0.05, -d - 0.03, 0, 0, d + 0.03, H, ends, skip=('-z',)))
    g.add(box(L, -d - 0.03, 0, L + 0.05, d + 0.03, H, ends, skip=('-z',)))
    g.xform(ang, x0, y0, z0)
    R.parts.add(g)
    c, s = math.cos(ang), math.sin(ang)
    # face on local +y: normal ang + pi/2, starts at local (0, 0)
    slab_row(R, x0 - s * 0.02, y0 + c * 0.02, z0, L, ang + math.pi / 2, rows, row_h, d, board)
    # face on local -y: normal ang - pi/2, starts at local (L, 0)
    slab_row(R, x0 + c * L + s * 0.02, y0 + s * L - c * 0.02, z0, L, ang - math.pi / 2, rows, row_h, d, board)
    return H + 0.07


def stack2_ax(R, x0, y0, x1, y1, z0, rows, **kw):
    """Double-sided bookcase along an axis-aligned centre line from (x0,y0) to (x1,y1)."""
    ang = math.atan2(y1 - y0, x1 - x0)
    return stack2(R, x0, y0, ang, math.hypot(x1 - x0, y1 - y0), z0, rows, **kw)


def wall_shelves(R, spans, z=0, rows=7, frame='wood', W=None, sides='SNWE', **kw):
    """Bookcases against the outer walls over the given spans (a, b) along each wall."""
    W = W or R.W
    for (a, b) in spans:
        if 'S' in sides: R.shelf(a, T, z, b - a, '+y', rows=rows, frame=frame, **kw)
        if 'N' in sides: R.shelf(b, W - T, z, b - a, '-y', rows=rows, frame=frame, **kw)
        if 'W' in sides: R.shelf(T, b, z, b - a, '+x', rows=rows, frame=frame, **kw)
        if 'E' in sides: R.shelf(W - T, a, z, b - a, '-x', rows=rows, frame=frame, **kw)


def arc_shelf(R, cx, cy, r, a0, a1, n, z, rows, inward=True, frame='wood', **kw):
    """Straight bookcase segments round an arc of radius r (their backs on the arc)."""
    for k in range(n):
        t0 = a0 + (a1 - a0) * k / n; t1 = a0 + (a1 - a0) * (k + 1) / n
        p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0)); p1 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) - 0.1
        tm = (t0 + t1) / 2
        if inward:   # face the centre: run direction = face - pi/2
            face = tm + math.pi
            run = face - math.pi / 2          # = tm + pi/2: counter-clockwise, from p0
            R.shelf(p0[0] + math.cos(run) * 0.05, p0[1] + math.sin(run) * 0.05, z, L, face, rows=rows, frame=frame, **kw)
        else:
            face = tm
            R.shelf(p1[0] + math.cos(tm - math.pi / 2) * 0.05, p1[1] + math.sin(tm - math.pi / 2) * 0.05, z, L, face, rows=rows, frame=frame, **kw)


def dome_cap(cx, cy, zs, r, rise, segs=48, rings=12, m='plaster', bottom='plaster'):
    """A closed spherical cap: base disc of radius r at zs, crown at zs + rise."""
    Rs = (r * r + rise * rise) / (2 * rise)
    zc = zs + rise - Rs
    e0 = math.asin(max(-1.0, min(1.0, (zs - zc) / Rs)))
    g = Geo()
    rs = []
    for i in range(rings):
        e = e0 + (math.pi / 2 - e0) * i / rings
        rs.append([g.vert((cx + Rs * math.cos(e) * math.cos(a), cy + Rs * math.cos(e) * math.sin(a), zc + Rs * math.sin(e)))
                   for a in [2 * math.pi * k / segs for k in range(segs)]])
    top = g.vert((cx, cy, zs + rise))
    for i in range(rings):
        for k in range(segs):
            j = (k + 1) % segs
            ua, ub = 2 * math.pi * k / segs * r, 2 * math.pi * (k + 1) / segs * r
            va, vb = i * rise, (i + 1) * rise
            if i + 1 == rings:
                g.face([rs[i][k], rs[i][j], top], m, [(ua, va), (ub, va), ((ua + ub) / 2, vb)])
            else:
                g.face([rs[i][k], rs[i][j], rs[i + 1][j], rs[i + 1][k]], m, [(ua, va), (ub, va), (ub, vb), (ua, vb)])
    g.face(list(reversed(rs[0])), bottom, [(g.v[i][0], g.v[i][1]) for i in reversed(rs[0])])
    return g.fix()


def dome_z(r, R0, zs, rise):
    """Height of the dome cap surface at radius r."""
    Rs = (R0 * R0 + rise * rise) / (2 * rise)
    zc = zs + rise - Rs
    return zc + math.sqrt(max(0.0, Rs * Rs - r * r))


def upright(g, cx, yf, cz):
    """Stand a piece built flat (in x, y about the origin, z = thickness) up in the x-z plane at y = yf:
    local y becomes height, local z becomes depth toward -y."""
    g.v = [(cx + x, yf - z, cz + y) for (x, y, z) in g.v]
    return g.fix()


def lamp(R, x, y, z, r=0.2, m='e_lamp', chain=None, shade=True):
    """A hanging globe lamp with a brass cap; chain up to z = chain."""
    R.light(sphere(x, y, z, r, 8, 4, m))
    if shade:
        R.nocol.add(cyl(x, y, z + r * 0.7, z + r * 1.05, r * 0.55, 10, side='brass', top='brass', bottom='brass'))
    if chain:
        R.nocol.add(cyl(x, y, z + r * 1.05, chain, 0.012, 5, side='iron', caps=False))


def chandelier(R, cx, cy, z, r, n=12, chain=None, bulb=0.14, tiers=1):
    """A brass ring chandelier with n globes, hung from z = chain."""
    for t in range(tiers):
        rr = r * (1 - 0.35 * t); zz = z + 0.9 * t
        R.nocol.add(ring(cx, cy, zz - 0.05, zz + 0.05, rr - 0.06, rr + 0.06, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
        for k in range(n - 3 * t):
            a = 2 * math.pi * k / (n - 3 * t)
            R.light(sphere(cx + rr * math.cos(a), cy + rr * math.sin(a), zz + 0.16, bulb, 8, 4, 'e_lamp'))
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            R.nocol.add(bar((cx + rr * math.cos(a), cy + rr * math.sin(a), zz), (cx, cy, zz + 1.2), 0.025, 0.025, 'brass'))
    R.nocol.add(sphere(cx, cy, z + 0.05, 0.25, 12, 6, 'brass'))
    if chain:
        R.nocol.add(cyl(cx, cy, z + 1.2, chain, 0.02, 6, side='iron', caps=False))


def pier(R, x, y, z0, z1, s=0.25, m='tile', cap=True):
    """A square stone pier with a small capital."""
    R.parts.add(box(x - s, y - s, z0, x + s, y + s, z1, m, skip=('-z', '+z')))
    if cap:
        R.parts.add(box(x - s - 0.08, y - s - 0.08, z1 - 0.18, x + s + 0.08, y + s + 0.08, z1, m, skip=('+z',)))


def deck(R, x0, y0, x1, y1, z, th=0.3, top='terrazzo', m='tile', bottom='plaster'):
    """A walkable slab whose top is at z."""
    R.parts.add(box(x0, y0, z - th, x1, y1, z, m, top=top, bottom=bottom))


def loop(R, pts, z=0.0, close=True):
    ids = [R.navpt(x, y, z) for (x, y) in pts]
    if close: R.link(*ids, ids[0])
    else: R.link(*ids)
    return ids


def flight_rect(R, rect, axis, z0, z1, run=0.3, rails='LR', m='terrazzo', side='tile', rail_m='brass', **kw):
    """A railed flight filling a plan rectangle, climbing along axis from z0 to z1."""
    x0, y0, x1, y1 = rect
    L = (x1 - x0) if axis[1] == 'x' else (y1 - y0)
    n = int(round(L / run))
    rise = (z1 - z0) / n
    width = (y1 - y0) if axis[1] == 'x' else (x1 - x0)
    fx = x0 if axis == '+x' else x1 if axis == '-x' else x0
    fy = y0 if axis == '+y' else y1 if axis == '-y' else y0
    flight(R, fx, fy, z0, width, n, rise, L / n, axis, m=m, side=side, rails=rails, rail_m=rail_m, **kw)


def rot180(W, D=None):
    """Helpers to mirror plan data through the room centre."""
    D = D or W
    rr = lambda r: (W - r[2], D - r[3], W - r[0], D - r[1])
    ra = lambda a: ('-' if a[0] == '+' else '+') + a[1]
    rs = lambda s: ''.join({'L': 'R', 'R': 'L', 'S': 'N', 'N': 'S', 'W': 'E', 'E': 'W'}[c] for c in s)
    def ro(opens, horiz_w=W, vert_d=D):
        out = {}
        for k, v in opens.items():
            k2 = {'S': 'N', 'N': 'S', 'W': 'E', 'E': 'W'}[k]
            out[k2] = [((horiz_w if k in 'SN' else vert_d) - b, (horiz_w if k in 'SN' else vert_d) - a) for (a, b) in v]
        return out
    return rr, ra, rs, ro


def pointed_profile(c, w, z0, jamb, rise, segs=16):
    """Closed profile of a (drop) pointed arch: width w centred on c, springing at z0 + jamb, crown rise above."""
    h = w / 2
    Rp = (h * h + rise * rise) / (2 * h) if rise > h else None
    zs = z0 + jamb
    pts = [(c - h, z0), (c + h, z0), (c + h, zs)]
    if Rp is None:   # not pointed: fall back to a segmental/round arch
        return arch_profile(c, w, z0, jamb, segs * 2, rise)
    # right arc: centre at (c + h - Rp, zs), from angle 0 up to the crown
    ox = c + h - Rp
    a1 = math.acos((c - ox) / Rp)
    for k in range(1, segs):
        t = a1 * k / segs
        pts.append((ox + Rp * math.cos(t), zs + Rp * math.sin(t)))
    pts.append((c, zs + rise))
    ox2 = c - h + Rp
    for k in range(segs - 1, 0, -1):
        t = math.pi - a1 * k / segs
        pts.append((ox2 + Rp * math.cos(t), zs + Rp * math.sin(t)))
    pts.append((c - h, zs))
    return pts


def flight_thin(R, x0, y0, z0, width, n, rise, run, axis='+y', m='terrazzo', riser=None, side='tile', under='plaster', thick=0.45, fill=2.2):
    """A flight whose underside follows the pitch (you can walk under its high end), plus the ramp collider."""
    L = n * run
    s0 = thick * run / rise
    prof = [(0.0, 0.0), (s0, 0.0), (L, n * rise - thick), (L, n * rise)]
    for i in range(n - 1, -1, -1):
        prof.append((i * run, (i + 1) * rise))
        if i > 0: prof.append((i * run, i * rise))
    mats = [side, under, side] + [m if k % 2 == 0 else (riser or side) for k in range(len(prof) - 3)]
    sgn = 1 if axis[0] == '+' else -1
    if axis[1] == 'x':
        pr = [(x0 + sgn * s, z0 + z) for s, z in prof]
        g = prism(pr, 'y', y0, y0 + width, mats, cap=side)
    else:
        pr = [(y0 + sgn * s, z0 + z) for s, z in prof]
        g = prism(pr, 'x', x0, x0 + width, mats, cap=side)
    R.nocol.add(g)
    Hh = n * rise
    if axis == '+y':   q = [(x0, y0 - 0.02, z0), (x0 + width, y0 - 0.02, z0), (x0 + width, y0 + L, z0 + Hh), (x0, y0 + L, z0 + Hh)]
    elif axis == '-y': q = [(x0, y0 + 0.02, z0), (x0, y0 - L, z0 + Hh), (x0 + width, y0 - L, z0 + Hh), (x0 + width, y0 + 0.02, z0)]
    elif axis == '+x': q = [(x0 - 0.02, y0, z0), (x0 + L, y0, z0 + Hh), (x0 + L, y0 + width, z0 + Hh), (x0 - 0.02, y0 + width, z0)]
    else:              q = [(x0 + 0.02, y0, z0), (x0 + 0.02, y0 + width, z0), (x0 - L, y0 + width, z0 + Hh), (x0 - L, y0, z0 + Hh)]
    gq = Geo(); ids = [gq.vert(p) for p in q]
    a = [q[1][i] - q[0][i] for i in range(3)]; b = [q[2][i] - q[0][i] for i in range(3)]
    if a[0] * b[1] - a[1] * b[0] < 0: ids = list(reversed(ids))
    gq.face(ids, 'floor', [(0, 0)] * 4)
    R.col.add(gq)
    # below the low end, where nobody could stand, fill in solid (a stone wedge) so there is no crawl space
    sf = (fill + thick) * run / rise
    if fill > 0 and sf > s0:
        sf = min(sf, L)
        zf = sf * rise / run - thick
        wedge = [(0.0, 0.0), (sf, 0.0), (sf, zf + 0.01)]
        if axis[1] == 'x':
            R.parts.add(prism([(x0 + sgn * s_, z0 + z) for s_, z in wedge], 'y', y0 + 0.01, y0 + width - 0.01, side, cap=side))
        else:
            R.parts.add(prism([(y0 + sgn * s_, z0 + z) for s_, z in wedge], 'x', x0 + 0.01, x0 + width - 0.01, side, cap=side))


def rose(R, cx, yf, cz, r, facing=-1):
    """A rose window of stained-glass emitters in the plane y = yf (facing -y if facing < 0)."""
    parts = []
    parts.append((ring(0, 0, 0, 0.03, 0.0001, r * 0.2, 24, top='e_red', bottom='e_red', inner='e_red', outer='e_red')))
    n = 12
    for k in range(n):
        a0 = 2 * math.pi * k / n + 0.03; a1 = 2 * math.pi * (k + 1) / n - 0.03
        parts.append(ring(0, 0, 0, 0.03, r * 0.25, r * 0.62, 4, top='e_blue', bottom='e_blue', inner='e_blue', outer='e_blue', a0=a0, a1=a1))
        parts.append(ring(0, 0, 0, 0.03, r * 0.66, r * 0.8, 3, top='e_red' if k % 2 else 'e_green', bottom='e_red' if k % 2 else 'e_green',
                          inner='e_red' if k % 2 else 'e_green', outer='e_red' if k % 2 else 'e_green', a0=a0, a1=a1))
    for k in range(2 * n):
        a0 = math.pi * k / n + 0.03; a1 = math.pi * (k + 1) / n - 0.03
        mm = 'e_blue' if k % 2 else 'e_red'
        parts.append(ring(0, 0, 0, 0.03, r * 0.84, r * 0.97, 2, top=mm, bottom=mm, inner=mm, outer=mm, a0=a0, a1=a1))
    for g in parts:
        g.v = [(cx + x, yf + (-z if facing < 0 else z), cz + y) for (x, y, z) in g.v]
        g.fix()
        R.light(g)
