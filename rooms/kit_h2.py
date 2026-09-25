"""Shared helpers for batch h2 of the Deep Stacks (scale gone wrong, smaller): onebook, dollhouse,
antgalleries, cardcatalogue, keyhole, shrinkcorridor, biggerinside, stairforest."""
from lib import *
from kit_a import *
import random


# ---------------------------------------------------------------------------
# solids
def hexa(P, m, top=None, bottom=None):
    """A closed solid from 8 corners (bottom 0..3 counter-clockwise seen from above, top 4..7 the same)."""
    g = Geo(); ids = [g.vert(p) for p in P]
    for f, key in (((0, 3, 2, 1), 'b'), ((4, 5, 6, 7), 't'), ((0, 1, 5, 4), 's'), ((1, 2, 6, 5), 's'), ((2, 3, 7, 6), 's'), ((3, 0, 4, 7), 's')):
        mm = (top if key == 't' else bottom if key == 'b' else None) or m
        pts = [P[i] for i in f]
        uv = [(p[0], p[1]) for p in pts] if key != 's' else [(p[0] + p[1], p[2]) for p in pts]
        g.face([ids[i] for i in f], mm, uv)
    return g.fix()


def loft_x(prof0, prof1, x0, x1, m, cap=None):
    """A closed solid between two (y, z) profiles with the same number of points, at x0 and x1.
    m: one material or a list per profile edge."""
    g = Geo(); n = len(prof0)
    a = [g.vert((x0, y, z)) for (y, z) in prof0]
    b = [g.vert((x1, y, z)) for (y, z) in prof1]
    for i in range(n):
        j = (i + 1) % n
        mm = m[i] if isinstance(m, (list, tuple)) else m
        g.face([a[i], a[j], b[j], b[i]], mm, [(prof0[i][0], prof0[i][1]), (prof0[j][0], prof0[j][1]), (prof1[j][0] + (x1 - x0), prof1[j][1]), (prof1[i][0] + (x1 - x0), prof1[i][1])])
    cm = cap or (m if isinstance(m, str) else m[0])
    g.face(list(reversed(a)), cm, [prof0[i] for i in reversed(range(n))])
    g.face(b, cm, list(prof1))
    return g.fix()


def ramp(R, p0, p1, w):
    """An invisible walkable ramp (one quad, facing up) from 3D point p0 to p1, w wide."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    q = [(p0[0] - nx, p0[1] - ny, p0[2]), (p1[0] - nx, p1[1] - ny, p1[2]), (p1[0] + nx, p1[1] + ny, p1[2]), (p0[0] + nx, p0[1] + ny, p0[2])]
    g = Geo(); ids = [g.vert(p) for p in q]
    g.face(ids, 'floor', [(0, 0)] * 4)
    a = Vector(q[1]) - Vector(q[0]); b = Vector(q[2]) - Vector(q[0])
    if a.cross(b).z < 0: g.f = [tuple(reversed(f)) for f in g.f]
    R.col.add(g)


def climb_ladder(R, xt, yt, z0, z1, ang, run=None, w=0.8, m='oak', rails='brass', side_rails=True):
    """A walkable library ladder: its top at (xt, yt, z1) against a face; it stands out toward angle ang,
    the foot `run` out at z0. Drawn as a ladder (nocol), walked as a steep invisible ramp with
    invisible side walls. The checker needs slope <= 0.55/grid (0.25 m grid: ~65 deg; 0.5 m: ~47 deg)."""
    h = z1 - z0
    run = run if run is not None else h * 0.5
    ca, sa = math.cos(ang), math.sin(ang)
    xf, yf = xt + ca * run, yt + sa * run
    g = Geo()
    px, py = -sa, ca
    for s in (-w / 2, w / 2):
        g.add(beam((xf + px * s, yf + py * s, z0), (xt + px * s, yt + py * s, z1 + 0.9), 0.07, m, 0.05))
    n = max(2, int(h / 0.3))
    for k in range(1, n + 1):
        t = k / n
        cx, cy, cz = xf + (xt - xf) * t, yf + (yt - yf) * t, z0 + h * t - 0.02
        g.add(beam((cx - px * w / 2, cy - py * w / 2, cz), (cx + px * w / 2, cy + py * w / 2, cz), 0.045, m, 0.035))
    for s in (-w / 2, w / 2):
        g.add(cyl(xf + px * s, yf + py * s, z0, z0 + 0.08, 0.045, 6, side=rails, top=rails))
    R.nocol.add(g)
    # the ramp the feet use: from a little beyond the foot to the top
    ramp(R, (xf + ca * 0.1, yf + sa * 0.1, z0), (xt - ca * 0.05, yt - sa * 0.05, z1), w + 0.5)
    if side_rails:
        for s in (-(w / 2 + 0.26), w / 2 + 0.26):
            p0 = (xf + px * s, yf + py * s); p1 = (xt + px * s, yt + py * s)
            wall_col(R, p0, p1, z0, z1, 1.3)


def wall_col(R, p0, p1, z0, z1, h=1.2, t=0.06):
    """An invisible sloped wall from p0 (at z0) to p1 (at z1), h tall."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L * t / 2, dx / L * t / 2
    P = [(p0[0] - nx, p0[1] - ny, z0 - 0.4), (p1[0] - nx, p1[1] - ny, z1 - 0.4), (p1[0] + nx, p1[1] + ny, z1 - 0.4), (p0[0] + nx, p0[1] + ny, z0 - 0.4)]
    P += [(p[0], p[1], p[2] + h + 0.4) for p in P]
    R.col.add(hexa(P, 'tile'))


def rails(R, pts, z=0.0, closed=False, **kw):
    """Brass rails along a polyline at floor height z."""
    pp = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(pp, pp[1:]):
        rail(R, a[0], a[1], b[0], b[1], z, **kw)


def railed_flight(R, x0, y0, z0, width, n, rise, run, axis, m='oak', riser='walnut', side='walnut', which=(0, 1), rail_m='brass', stringer=None):
    """R.flight plus handrails on the chosen sides (0 = the left/low-coordinate side, 1 = the other)."""
    R.flight(x0, y0, z0, width, n, rise, run, axis, m=m, riser=riser, side=side)
    L, H = n * run, n * rise
    for k in which:
        if axis in ('+y', '-y'):
            x = x0 + 0.05 if k == 0 else x0 + width - 0.05
            ya, yb = (y0, y0 + L) if axis == '+y' else (y0, y0 - L)
            stair_rail(R, x, ya, z0 + rise * 0.5, x, yb, z0 + H, m=rail_m)
        else:
            y = y0 + 0.05 if k == 0 else y0 + width - 0.05
            xa, xb = (x0, x0 + L) if axis == '+x' else (x0, x0 - L)
            stair_rail(R, xa, y, z0 + rise * 0.5, xb, y, z0 + H, m=rail_m)


def slab_poly(poly, z0, z1, m='oak', side='walnut', bottom='walnut'):
    return poly_prism(poly, z0, z1, side=side, top=m, bottom=bottom)


# ---------------------------------------------------------------------------
# helix stairs with rails (spiral stairs round a newel)
def helix_stair(R, cx, cy, r0, r1, z0, z1, a0, turns_per_m=None, rise_per_turn=4.2, m='oak', side='walnut', bottom='walnut',
                newel='iron', rail_m='brass', inner_rail=False, walk=True, thick=0.3):
    """A spiral stair climbing counter-clockwise from angle a0 at z0 to z1 round (cx, cy). Treads are
    drawn as wedge steps; walked on a smooth helical ramp; brass rail on the outside."""
    H = z1 - z0
    turns = H / rise_per_turn
    a1 = a0 + turns * 2 * math.pi
    nst = max(4, int(round(H / 0.19)))
    da = (a1 - a0) / nst
    g = Geo()
    for k in range(nst):
        aa = a0 + k * da; zt = z0 + (k + 1) * H / nst
        g.add(ring(cx, cy, zt - thick, zt, r0, r1, 3, top=m, bottom=bottom, inner=side, outer=side, a0=aa, a1=aa + da * 1.02))
    R.nocol.add(g)
    if newel:
        R.parts.add(cyl(cx, cy, z0, z1 + 1.0, r0, 12, side=newel, top='brass'))
    if walk:
        R.col.add(helix(cx, cy, r0, r1, z0, rise_per_turn, a0, a1, thick=0.1, segs=max(12, int(turns * 40)), top='floor', side='tile', bottom='tile'))
        # outer rail: posts and a bar, and an invisible fence
        nseg = max(6, int(turns * 24))
        rr = r1 - 0.06
        for k in range(nseg + 1):
            t = k / nseg; a = a0 + (a1 - a0) * t; z = z0 + H * t
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            R.nocol.add(box(x - 0.025, y - 0.025, z, x + 0.025, y + 0.025, z + 0.95, rail_m, skip=('-z', '+z')))
            if k:
                tp = (k - 1) / nseg; ap = a0 + (a1 - a0) * tp; zp = z0 + H * tp
                xp, yp = cx + rr * math.cos(ap), cy + rr * math.sin(ap)
                R.nocol.add(beam((xp, yp, zp + 0.95), (x, y, z + 0.95), 0.05, rail_m, 0.04))
                wall_col(R, (xp, yp), (x, y), zp, z, 1.3)
    return a1


# ---------------------------------------------------------------------------
# small things
def green_lamp(R, x, y, z, ang=0.0, s=1.0, m='e_lamp'):
    """A banker's lamp on a surface at height z, scaled by s (s=0.1 for a dollhouse)."""
    R.nocol.add(cyl(x, y, z, z + 0.03 * s, 0.08 * s, 8, side='brass', top='brass'))
    R.nocol.add(box(x - 0.012 * s, y - 0.012 * s, z + 0.03 * s, x + 0.012 * s, y + 0.012 * s, z + 0.36 * s, 'brass', skip=('-z', '+z')))
    sh_ = box(-0.17 * s, -0.065 * s, 0.36 * s, 0.17 * s, 0.065 * s, 0.44 * s, 'green').xform(ang, x, y, z)
    R.nocol.add(sh_)
    R.light(box(-0.15 * s, -0.045 * s, 0.345 * s, 0.15 * s, 0.045 * s, 0.36 * s, m).xform(ang, x, y, z))


def desk(R, x0, y0, x1, y1, z=0.0, h=0.76, m='walnut', top='leather', col=True):
    g = table(x0, y0, x1, y1, h, m, top=top)
    g.v = [(a, b, c + z) for a, b, c in g.v]
    (R.parts if col else R.nocol).add(g)


def seat(R, x, y, a, z=0.0, spot=True):
    g = chair(x, y, a); g.v = [(p[0], p[1], p[2] + z) for p in g.v]
    R.parts.add(g)
    if spot: R.spot('sit', x, y, z + 0.48, a)


def open_book_prop(R, x, y, z, ang=0.0, s=1.0):
    g = Geo()
    g.add(box(-0.2 * s, -0.14 * s, 0, 0.0, 0.14 * s, 0.03 * s, 'ivory', sides='leather'))
    g.add(box(0.0, -0.14 * s, 0, 0.2 * s, 0.14 * s, 0.03 * s, 'ivory', sides='leather'))
    R.nocol.add(g.xform(ang, x, y, z))


def book_pile(R, x, y, z, n=5, seed=0, s=1.0):
    rnd = random.Random(seed)
    g = Geo(); zz = 0.0
    for i in range(n):
        th = (0.035 + rnd.random() * 0.03) * s
        w, d = (0.2 + rnd.random() * 0.1) * s, (0.14 + rnd.random() * 0.06) * s
        b = box(-w / 2, -d / 2, zz, w / 2, d / 2, zz + th, rnd.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet')), top='ivory' if i == n - 1 else None)
        g.add(b.xform(rnd.uniform(-0.4, 0.4)))
        zz += th
    R.nocol.add(g.xform(rnd.random() * 3, x, y, z))


def secret(R, x, y, z, name, text, r=1.5):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, box_, **kw):
    d = {'type': kind, 'box': [round(v, 2) for v in box_]}; d.update(kw)
    R.meta.setdefault('fx', []).append(d)


def all_sockets_except(R, keep_levels=(0,), keep=()):
    """Skip list for every doorway on levels not in keep_levels, except those in keep."""
    sk = []
    for L in range(R.levels):
        if L in keep_levels: continue
        for i in range(R.w):
            for s in 'SN':
                if (s, i, L) not in keep: sk.append((s, i, L))
        for j in range(R.d):
            for s in 'WE':
                if (s, j, L) not in keep: sk.append((s, j, L))
    return sk


def seal_sockets(R, skip, **kw):
    R.sockets(skip=skip, **kw)
    if skip: R.meta['sealed'] = [list(s) for s in skip]


# ---------------------------------------------------------------------------
# Lightmap islands: lib.build packs every face group that smart_project splits off (each face of a box
# is its own island) with a 4.5 px margin, so a room with ~10k small faces at 1024 px packs to nothing
# and bakes black. Keep face counts down, and weld coplanar pieces so they share one island.
def weld(g, eps=1e-4):
    """Merge coincident vertices of a Geo, so faces that touch edge-to-edge form one lightmap island."""
    key = {}; remap = []; nv = []
    for p in g.v:
        k = (round(p[0] / eps), round(p[1] / eps), round(p[2] / eps))
        if k not in key: key[k] = len(nv); nv.append(p)
        remap.append(key[k])
    g.v = nv; g.f = [tuple(remap[i] for i in f) for f in g.f]
    return g


def lattice(xs, zs, holes, y, m='walnut', facing=-1):
    """A flat grid of bars in the x-z plane at y (facing -y by default): xs and zs are the sorted
    grid lines of the bar edges; holes(i, j) says whether the cell between xs[i..i+1], zs[j..j+1] is
    open. One connected mesh (one lightmap island)."""
    g = Geo(); idx = {}
    def V(i, j):
        if (i, j) not in idx: idx[(i, j)] = g.vert((xs[i], y, zs[j]))
        return idx[(i, j)]
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            if holes(i, j): continue
            f = [V(i, j), V(i + 1, j), V(i + 1, j + 1), V(i, j + 1)]
            if facing > 0: f = f[::-1]
            g.face(f, m, [(xs[i], zs[j]), (xs[i + 1], zs[j]), (xs[i + 1], zs[j + 1]), (xs[i], zs[j + 1])][::(1 if facing < 0 else -1)])
    return g


def count_faces(R):
    return len(R.parts.f) + len(R.nocol.f) + len(R.slabs)


def ribbon_stair(n, rise, run, width, th=0.35, m='oak', riser='walnut', side='walnut', under='plaster'):
    """A flight drawn as a ribbon (sawtooth top, sloped underside) climbing local +x from the origin,
    across local y 0..width. For stairs that hang in the air. Place it with .xform()."""
    L = n * run
    prof = [(0.0, 0.0)]
    for i in range(n):
        prof.append((i * run, (i + 1) * rise)); prof.append(((i + 1) * run, (i + 1) * rise))
    # the underside, parallel to the pitch line, th below it
    prof.append((L, n * rise - th)); prof.append((0.0, -th))
    mats = []
    for k in range(len(prof)):
        if k == 0: mats.append(riser)
        elif k < 2 * n + 1: mats.append(m if k % 2 == 1 else riser)
        elif k == 2 * n + 1: mats.append(under)
        else: mats.append(riser)
    # build as a prism along y (profile in x-z)
    return prism(prof, 'y', 0.0, width, mats, cap=side)


def flip_z(g, z0):
    """Mirror a Geo upside down about the plane z = z0 (fixing the winding)."""
    g.v = [(a, b, 2 * z0 - c) for a, b, c in g.v]
    g.f = [tuple(reversed(f)) for f in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    return g


def hung_flight(R, x0, y0, z0, width, n, rise, run, axis, m='oak', riser='walnut', side='walnut', under='plaster', th=0.4, rails_=(0, 1)):
    """A flight like R.flight (same arguments: (x0, y0) the foot's corner, climbing along axis), drawn
    as a ribbon with a sloped soffit so you can walk underneath it; collided, with the invisible ramp
    and handrails."""
    g = ribbon_stair(n, rise, run, width, th=th, m=m, riser=riser, side=side, under=under)
    if axis == '+x': g.xform(0.0, x0, y0, z0)
    elif axis == '-x': g.xform(math.pi, x0, y0 + width, z0)
    elif axis == '+y': g.xform(math.pi / 2, x0 + width, y0, z0)
    else: g.xform(-math.pi / 2, x0, y0, z0)
    R.parts.add(g)
    save = R.nocol; R.nocol = Geo()
    R.flight(x0, y0, z0, width, n, rise, run, axis)     # only for its ramp
    R.nocol = save
    L, H = n * run, n * rise
    for k in rails_:
        if axis in ('+y', '-y'):
            x = x0 + 0.05 if k == 0 else x0 + width - 0.05
            yb = y0 + L if axis == '+y' else y0 - L
            stair_rail(R, x, y0, z0 + rise * 0.5, x, yb, z0 + H)
        else:
            y = y0 + 0.05 if k == 0 else y0 + width - 0.05
            xb = x0 + L if axis == '+x' else x0 - L
            stair_rail(R, x0, y, z0 + rise * 0.5, xb, y, z0 + H)
