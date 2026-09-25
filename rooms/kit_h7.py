"""Shared helpers for batch 7 of the Deep Stacks (machines II, voids I): lighthouse, bridgevoid,
hanginglib, wellofstairs, floatislands, theedge, starfloor, drain."""
import random
from lib import *
from kit_h3 import (secret, fx, finish, field, reading_table, pendant, lamp_post, book_pile, open_book, armchair,
                    shell, obox, beam, rot, rail, stair_rail, shelf, sh, chair, table, bulb, desk_lamp, candle,
                    ladder, navloop, tidy, frustum, floor_lamp, open_flight, ellipsoid)
from kit_a import stack, ang_shelf, inv_shelf
from kit_g import (upper_sockets, seal, wall_cases, iron_rail, lamppost, hanging, bench)
from kit_g import flight as gflight, flight_rail as gflight_rail, rail as brail
from kit_h4 import ladder_up, ramp


def rng(seed):
    return random.Random(seed)


def ring_rail(R, cx, cy, r, z, a0=0.0, a1=2 * math.pi, n=None, h=1.0, m='iron'):
    """A round iron railing on radius r from angle a0 to a1: posts, top and mid bars, and an invisible wall."""
    L = abs(a1 - a0) * r
    n = n or max(3, int(math.ceil(L / 1.0)))
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        R.nocol.add(box(x - 0.03, y - 0.03, z, x + 0.03, y + 0.03, z + h, m, skip=('-z',)))
    for k in range(n):
        p = [(cx + r * math.cos(a0 + (a1 - a0) * t / n), cy + r * math.sin(a0 + (a1 - a0) * t / n)) for t in (k, k + 1)]
        R.nocol.add(obox(p[0][0], p[0][1], p[1][0], p[1][1], z + h - 0.05, z + h, 0.07, 'brass' if m == 'brass' else m))
        R.nocol.add(obox(p[0][0], p[0][1], p[1][0], p[1][1], z + 0.1, z + 0.14, 0.05, m))
        R.col.add(obox(p[0][0], p[0][1], p[1][0], p[1][1], z, z + h + 0.1, 0.08, 'tile'))


def rail_line(R, pts, z, h=1.0, m='iron', post=1.1, closed=False):
    """iron_rail along a polyline in plan."""
    P = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 0.05: continue
        n = max(1, int(math.ceil(L / post)))
        for k in range(n + 1):
            x, y = a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n
            R.nocol.add(box(x - 0.03, y - 0.03, z, x + 0.03, y + 0.03, z + h, m, skip=('-z',)))
        R.nocol.add(obox(a[0], a[1], b[0], b[1], z + h - 0.05, z + h, 0.07, m))
        R.nocol.add(obox(a[0], a[1], b[0], b[1], z + 0.1, z + 0.14, 0.05, m))
        R.col.add(obox(a[0], a[1], b[0], b[1], z, z + h + 0.1, 0.08, 'tile'))


def helix_rail(R, cx, cy, r, z0, rise, a0, a1, h=0.95, m='iron', segs=None):
    """A handrail on a helix (posts, a top bar, an invisible sloped wall) at radius r."""
    segs = segs or max(8, int(abs(a1 - a0) * r / 1.0))
    zf = lambda a: z0 + rise * (a - a0) / (2 * math.pi)
    P = lambda a: (cx + r * math.cos(a), cy + r * math.sin(a))
    for k in range(segs + 1):
        a = a0 + (a1 - a0) * k / segs
        x, y = P(a)
        R.nocol.add(box(x - 0.025, y - 0.025, zf(a) - 0.05, x + 0.025, y + 0.025, zf(a) + h, m, skip=('-z',)))
    R.nocol.add(helix(cx, cy, r - 0.035, r + 0.035, z0 + h + 0.05, rise, a0, a1, 0.06, segs * 2, top=m, side=m, bottom=m))
    R.col.add(helix(cx, cy, r - 0.05, r + 0.05, z0 + h + 0.15, rise, a0, a1, h + 0.5, segs * 2, top='tile', side='tile', bottom='tile'))


def chain(R, x, y, z0, z1, link=0.16, w=0.035, m='iron'):
    """A hanging chain: alternating links (thin boxes turned 90 degrees), drawn only."""
    n = max(1, int((z1 - z0) / link))
    g = Geo()
    for k in range(n):
        za = z0 + k * (z1 - z0) / n; zb = za + (z1 - z0) / n * 1.15
        if k % 2: g.add(box(x - w, y - 0.006, za, x + w, y + 0.006, zb, m))
        else: g.add(box(x - 0.006, y - w, za, x + 0.006, y + w, zb, m))
    R.nocol.add(g)
    return g


def book_scatter(g, x, y, z, rnd, n=1, spread=0.3, tilt=0.35):
    """Loose books lying about (added to Geo g): small boxes with random turn and a little tilt."""
    for _ in range(n):
        w, d, t = rnd.uniform(0.17, 0.3), rnd.uniform(0.13, 0.22), rnd.uniform(0.03, 0.07)
        b = box(-w / 2, -d / 2, 0, w / 2, d / 2, t, rnd.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet', 'ivory')))
        if tilt: rot(b, 'x', rnd.uniform(-tilt, tilt))
        b.xform(rnd.uniform(0, math.pi), x + rnd.uniform(-spread, spread), y + rnd.uniform(-spread, spread), z)
        g.add(b)
    return g


def rug(R, x0, y0, x1, y1, z=0.0, m='carpet', border='oxblood', ang=0.0, cx=None, cy=None, lift=0.012):
    """A flat rug with a border, drawn only (optionally turned by ang about its centre)."""
    cx = (x0 + x1) / 2 if cx is None else cx; cy = (y0 + y1) / 2 if cy is None else cy
    g = box(x0 - cx, y0 - cy, 0, x1 - cx, y1 - cy, lift, border)
    g.add(box(x0 - cx + 0.18, y0 - cy + 0.18, lift, x1 - cx - 0.18, y1 - cy - 0.18, lift + 0.004, m))
    g.xform(ang, cx, cy, z)
    R.nocol.add(g)


def green_lamp(R, x, y, z, a=0.0):
    desk_lamp(R, x, y, z)


def desk(R, x, y, a=0.0, z=0.0, w=1.5, d=0.75, h=0.78, top='leather', m='walnut', drawers=True):
    """A pedestal writing desk centred at (x, y), turned by a; collided."""
    g = Geo()
    g.add(box(-w / 2, -d / 2, h - 0.05, w / 2, d / 2, h, m, top=top))
    if drawers:
        for s in (-1, 1):
            g.add(box(s * w / 2 - (0.42 if s > 0 else 0), -d / 2 + 0.03, 0, s * w / 2 + (0.42 if s < 0 else 0), d / 2 - 0.03, h - 0.05, m))
            for k in range(3):
                zz = 0.08 + k * 0.22
                xa = s * w / 2 - (0.38 if s > 0 else 0) if s > 0 else -w / 2 + 0.04
                g.add(box(xa, -d / 2 + 0.01, zz, xa + 0.34, -d / 2 + 0.03, zz + 0.18, 'oak'))
                g.add(box(xa + 0.14, -d / 2 - 0.01, zz + 0.08, xa + 0.2, -d / 2 + 0.01, zz + 0.1, 'brass'))
        g.add(box(-w / 2 + 0.42, d / 2 - 0.06, 0.25, w / 2 - 0.42, d / 2 - 0.03, h - 0.05, m))
    else:
        for (px, py) in ((-w / 2 + 0.06, -d / 2 + 0.06), (w / 2 - 0.06, -d / 2 + 0.06), (w / 2 - 0.06, d / 2 - 0.06), (-w / 2 + 0.06, d / 2 - 0.06)):
            g.add(box(px - 0.04, py - 0.04, 0, px + 0.04, py + 0.04, h - 0.05, m, skip=('-z',)))
    g.xform(a, x, y, z)
    R.parts.add(g)


def hatch_frame(R, x0, y0, x1, y1, z, m='oak', t=0.1):
    for (a, b, c, d) in ((x0 - t, y0 - t, x1 + t, y0), (x0 - t, y1, x1 + t, y1 + t), (x0 - t, y0, x0, y1), (x1, y0, x1 + t, y1)):
        R.nocol.add(box(a, b, z - 0.02, c, d, z + 0.03, m))


def lathe(cx, cy, prof, segs=48, mats='tile', a0=0.0, a1=2 * math.pi):
    """A solid of revolution: the closed (r, z) polygon `prof` (all r > 0) turned round the vertical
    axis through (cx, cy). mats: one material or one per profile edge. Partial turns get end caps."""
    g = Geo()
    full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    n = len(prof)
    na = segs if full else segs + 1
    ang = [a0 + (a1 - a0) * k / segs for k in range(na)]
    V = [[g.vert((cx + r * math.cos(a), cy + r * math.sin(a), z)) for (r, z) in prof] for a in ang]
    for k in range(segs):
        j = (k + 1) % na
        for i in range(n):
            i2 = (i + 1) % n
            (r0, z0), (r1, z1) = prof[i], prof[i2]
            m = mats[i] if isinstance(mats, (list, tuple)) else mats
            q = [V[k][i], V[j][i], V[j][i2], V[k][i2]]
            if abs(z1 - z0) < 0.3 * abs(r1 - r0):
                uv = [(g.v[v][0], g.v[v][1]) for v in q]
            else:
                uv = [(ang[k] * r0, z0), (ang[k] * r0 + (a1 - a0) / segs * r0, z0), (ang[k] * r1 + (a1 - a0) / segs * r1, z1), (ang[k] * r1, z1)]
            g.face(q, m, uv)
    if not full:
        for (row, a) in ((V[0], ang[0]), (V[-1], ang[-1])):
            g.face(list(row), mats[0] if isinstance(mats, (list, tuple)) else mats, [(r, z) for (r, z) in prof])
    return g.fix()


def tilt_place(g, x, y, z, toward, slope):
    """Lean a piece built at the origin (base at z=0) down toward plan angle `toward` by `slope` radians,
    then set it at (x, y, z)."""
    rot(g, 'y', slope)
    return g.xform(toward, x, y, z)


def circle_pts(cx, cy, r, n=48, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def clip_poly(pts, x0=-1e9, y0=-1e9, x1=1e9, y1=1e9):
    """Clip a convex polygon to an axis-aligned rectangle (Sutherland-Hodgman). Returns a convex polygon."""
    def clip(P, inside, cross):
        out = []
        for i in range(len(P)):
            a, b = P[i - 1], P[i]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia: out.append(cross(a, b))
                out.append(b)
            elif ia: out.append(cross(a, b))
        return out
    def cx_(v):
        return lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / ((b[0] - a[0]) or 1e-9))
    def cy_(v):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / ((b[1] - a[1]) or 1e-9), v)
    P = list(pts)
    for (ins, cr) in ((lambda p: p[0] >= x0, cx_(x0)), (lambda p: p[0] <= x1, cx_(x1)), (lambda p: p[1] >= y0, cy_(y0)), (lambda p: p[1] <= y1, cy_(y1))):
        if not P: break
        P = clip(P, ins, cr)
    return P


def disc_with_hole(cx, cy, r, z0, z1, hole, n=48, top='floor', side='tile', bottom='plaster'):
    """A round slab with a rectangular hole (hx0, hy0, hx1, hy1) inside it, as convex prisms."""
    hx0, hy0, hx1, hy1 = hole
    C = circle_pts(cx, cy, r, n)
    g = Geo()
    for rect in ((-1e9, -1e9, hx0, 1e9), (hx1, -1e9, 1e9, 1e9), (hx0, -1e9, hx1, hy0), (hx0, hy1, hx1, 1e9)):
        P = clip_poly(C, *rect)
        if len(P) >= 3: g.add(poly_prism(P, z0, z1, side=side, top=top, bottom=bottom))
    return g
