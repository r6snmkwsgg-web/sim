"""Shared helpers for batch 12 of the Deep Stacks (engine rooms II: motion, mirrors, effects):
clockwork, elevator, orrery, waterwheel, dumbwaiters, afterimage, mirrorlake, mirrorhall, negative."""
import math
import random
import lib
from lib import *
from kit_a import (sh, shelf as kshelf, stack, chair as chair_geo, table as table_geo, bulb, desk_lamp, candle,
                   navloop, tidy, beam, rot, frustum, obox, rail as brass_rail, stair_rail, ang_shelf, ladder)
from kit_g import flight as rflight, flight_rail, rail as stone_rail, iron_rail, upper_sockets, seal
from kit_h1 import along, xcyl
from kit_h3 import pendant, armchair, reading_table, book_pile, open_book, lamp_post, arc_band
from kit_h6 import wheel, gear, solid_tube, cage_tube, tunnels, stool, NEW_MATS
from kit_h7 import ring_rail, rail_line, helix_rail

# a few extra materials: albedo only, the game paints them
for _k, _v in {'white': (0.90, 0.89, 0.86), 'ebony': (0.05, 0.04, 0.04), 'glass': (0.05, 0.06, 0.07),
               'water': (0.10, 0.16, 0.16)}.items():
    lib.MATS.setdefault(_k, _v)
# a lamp that glows black (for the negative room: in the inverted picture it shines white)
lib.EMIT.setdefault('e_black', ((0.02, 0.025, 0.03), 1.0))
BOOKC = ('oxblood', 'green', 'leather', 'walnut', 'velvet', 'bronze', 'slate', 'ivory')


def rng(seed):
    return random.Random(seed)


# ---------------------------------------------------------------------------
# bookkeeping
def secret(R, x, y, z, name, text, r=1.5):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, bx=None, **kw):
    d = {'type': kind}
    if bx is not None: d['box'] = [round(float(v), 2) for v in bx]
    for k, v in kw.items(): d[k] = [round(float(c), 2) for c in v] if isinstance(v, (list, tuple)) else v
    R.meta.setdefault('fx', []).append(d)


def mirror(R, c, n, w, h, up=None):
    d = {'c': [round(float(v), 3) for v in c], 'n': list(n), 'w': w, 'h': h}
    if up: d['up'] = list(up)
    R.meta.setdefault('mirrors', []).append(d)


def portal(R, a, b):
    R.meta.setdefault('portals', []).append({'a': a, 'b': b})


def finish(R, label, blurb, weight=3, probe=(16, 16, 1.8), top=TOP, bot=0.0):
    R.spot('probe', *probe)
    R.meta.update(label=label, weight=weight, blurb=blurb)
    R.meta['box'] = [[T, bot, T], [R.W - T, top, R.D - T]]
    return tidy(R)


# ---------------------------------------------------------------------------
# small geometry
def ybox(x, y0, y1, z0, z1, t, m, **kw):
    """A thin panel in the x = const plane."""
    return box(x - t / 2, y0, z0, x + t / 2, y1, z1, m, **kw)


def xbox(y, x0, x1, z0, z1, t, m, **kw):
    return box(x0, y - t / 2, z0, x1, y + t / 2, z1, m, **kw)


def frame_rect(ax, c, u0, u1, z0, z1, off, w=0.14, d=0.08, m='gilt'):
    """A picture/mirror frame round a rectangle in a wall plane. ax 'x': the wall is x = c (u runs along y);
    'y': the wall is y = c (u along x). off: the side of the wall it stands proud on (+1 / -1)."""
    g = Geo()
    a, b = (c, c + off * d) if off > 0 else (c + off * d, c)
    def B(u0_, u1_, z0_, z1_):
        return box(a, u0_, z0_, b, u1_, z1_, m) if ax == 'x' else box(u0_, a, z0_, u1_, b, z1_, m)
    g.add(B(u0 - w, u1 + w, z1, z1 + w))
    g.add(B(u0 - w, u1 + w, z0 - w, z0))
    g.add(B(u0 - w, u0, z0, z1))
    g.add(B(u1, u1 + w, z0, z1))
    return g


def book_row_geo(g, rs, x0, x1, y, z, depth=0.24, hmin=0.24, hmax=0.34, face=1, lean=True):
    """Box books standing in a row along x from x0 to x1, spines toward y + face*depth. For movers
    (the game's real books cannot ride a moving part)."""
    x = x0
    while x < x1 - 0.03:
        t = rs.uniform(0.035, 0.075)
        if x + t > x1: break
        hb = rs.uniform(hmin, hmax)
        m = rs.choice(BOOKC)
        ya, yb = (y, y + face * depth) if face > 0 else (y + face * depth, y)
        g.add(box(x, ya, z, x + t, yb, z + hb, m, skip=('-z',)))
        x += t + rs.uniform(0.0, 0.012)
    return g


def fake_case(rs, L, rows, row_h=0.42, depth=0.32, frame='walnut', both=False, top=True):
    """A bookcase built as plain geometry (frame + box books), its back on y=0 facing +y, from x=0 to L.
    For moving parts. both=True: books on both faces (a free-standing double case, centred on y=0)."""
    g = Geo()
    H = rows * row_h + 0.04
    y0 = -depth if both else 0.0
    g.add(box(-0.04, y0, 0, 0.0, depth, H, frame))
    g.add(box(L, y0, 0, L + 0.04, depth, H, frame))
    if not both: g.add(box(0, -0.02, 0, L, 0.0, H, frame))
    else: g.add(box(0, -0.01, 0, L, 0.01, H, frame))
    for r in range(rows + 1):
        z = r * row_h
        g.add(box(0, y0, z, L, depth, z + 0.035, frame))
        if r < rows:
            book_row_geo(g, rs, 0.02, L - 0.02, 0.01, z + 0.035, depth=depth - 0.06, hmax=min(0.36, row_h - 0.06))
            if both: book_row_geo(g, rs, 0.02, L - 0.02, -0.01, z + 0.035, depth=depth - 0.06, face=-1, hmax=min(0.36, row_h - 0.06))
    if top: g.add(box(-0.08, y0 - 0.02, H, L + 0.08, depth + 0.03, H + 0.06, frame))
    return g


def book_globe(cx, cy, cz, r, rs, bands=None, segs=None, band_m='gilt', axis_m='brass'):
    """A planet made of bound books: latitude bands of spines (each facet a different binding, set a
    little proud or sunk), a gilt equator band. Drawn geometry."""
    g = Geo()
    bands = bands or max(5, int(r * 5))
    segs = segs or max(10, int(r * 12))
    for i in range(bands):
        p0 = -math.pi / 2 + math.pi * i / bands
        p1 = -math.pi / 2 + math.pi * (i + 1) / bands
        for j in range(segs):
            a0 = 2 * math.pi * j / segs + (0.5 * i)
            a1 = 2 * math.pi * (j + 1) / segs + (0.5 * i)
            rr = r * rs.uniform(0.97, 1.03)
            def P(p, a, q=rr):
                return (cx + q * math.cos(p) * math.cos(a), cy + q * math.cos(p) * math.sin(a), cz + q * math.sin(p))
            m = rs.choice(BOOKC)
            if i == 0: ids = [g.vert(P(p0, 0)), g.vert(P(p1, a1)), g.vert(P(p1, a0))]
            elif i == bands - 1: ids = [g.vert(P(p0, a0)), g.vert(P(p0, a1)), g.vert(P(p1, 0))]
            else: ids = [g.vert(P(p0, a0)), g.vert(P(p0, a1)), g.vert(P(p1, a1)), g.vert(P(p1, a0))]
            g.face(ids, m, [(0, 0), (1, 0), (1, 1), (0, 1)][:len(ids)])
    g.add(ring(cx, cy, cz - r * 0.06, cz + r * 0.06, r * 0.99, r * 1.06, max(16, segs), top=band_m, bottom=band_m, inner=band_m, outer=band_m))
    return g


def lattice_panel(g, p0, p1, z0, z1, m='brass', bars=None, rails_=3, t=0.035):
    """A brass grille between two plan points: verticals every ~0.18 m, a few horizontal rails, diagonals."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = bars or max(2, int(L / 0.2))
    for k in range(n + 1):
        u = k / n
        x, y = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u
        g.add(box(x - t / 2, y - t / 2, z0, x + t / 2, y + t / 2, z1, m))
    for k in range(rails_):
        z = z0 + (z1 - z0) * k / max(1, rails_ - 1)
        g.add(obox(p0[0], p0[1], p1[0], p1[1], z - 0.03, z + 0.03, t * 1.3, m))
    return g


def cyl_lattice(g, cx, cy, r, z0, z1, a0, a1, m='brass', step=0.22, hoops=(0.0, 0.5, 1.0), t=0.035, hoop_w=0.06):
    """A cylindrical brass grille (vertical bars and hoops) on radius r between angles a0..a1."""
    L = abs(a1 - a0) * r
    n = max(2, int(L / step))
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        g.add(box(x - t / 2, y - t / 2, z0, x + t / 2, y + t / 2, z1, m))
    for h in hoops:
        z = z0 + (z1 - z0) * h
        g.add(ring(cx, cy, z - hoop_w / 2, z + hoop_w / 2, r - 0.03, r + 0.03, max(8, int(n)), top=m, bottom=m, inner=m, outer=m, a0=a0, a1=a1))
    return g


def sconce(R, x, y, z, ang, m='e_lamp', shade='green'):
    """A brass wall arm with a small green-shaded lamp, the wall behind it at (x, y), arm pointing ang."""
    ca, sa = math.cos(ang), math.sin(ang)
    R.nocol.add(beam((x, y, z - 0.25), (x + ca * 0.32, y + sa * 0.32, z), 0.03, 'brass'))
    R.nocol.add(frustum(x + ca * 0.32, y + sa * 0.32, z - 0.05, z + 0.12, 0.16, 0.06, 10, shade, inner='ivory'))
    R.light(cyl(x + ca * 0.32, y + sa * 0.32, z - 0.03, z, 0.09, 8, side=m, top=m, bottom=m))


def vault_x(R, x0, x1, yc, w, spring, rise, wall='tile', floor='terrazzo', ceil='plaster', segs=28, z0=0.0):
    """Carve a barrel-vaulted hall running along x (floor z0, walls to `spring`, then an arch of `rise`)."""
    pr = arch_profile(yc, w, z0, spring - z0, segs, rise=rise)
    mats = [floor, wall] + [ceil] * (len(pr) - 3) + [wall]
    R.cut(prism(pr, 'x', x0, x1, mats, cap=wall))


def vault_y(R, y0, y1, xc, w, spring, rise, wall='tile', floor='terrazzo', ceil='plaster', segs=28, z0=0.0):
    pr = arch_profile(xc, w, z0, spring - z0, segs, rise=rise)
    mats = [floor, wall] + [ceil] * (len(pr) - 3) + [wall]
    R.cut(prism(pr, 'y', y0, y1, mats, cap=wall))


def navgrid(R, pts, links, z=0.0):
    ids = {k: R.navpt(p[0], p[1], p[2] if len(p) > 2 else z) for k, p in pts.items()}
    for a, b in links: R.link(ids[a], ids[b])
    return ids
