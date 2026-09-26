"""Shared helpers for batch 11 of the Deep Stacks (engine rooms I: portals): mobius, escherloop, recursion,
klein, folded, penrose, tesseract, rotunda5, loopcorridor, reflectstair.

Portals (see AUTHORING.md, "Engine features"): a pair of rectangles; `n` is the way you walk in at `a` and
the way you come out at `b`. The frame's +Z is n; the quad is drawn 2 cm past the plane (so every portal
needs a real opening behind it), and a portal only shows from its front. Keep planes off cell boundaries
(x or y a multiple of 16): the game forgets where you were when you change cell, and a crossing made in
the same step would be missed."""
import math
import random
from lib import *
import lib
from kit_h10 import *            # noqa: the batch-10 kit (and through it kits a, f, h2..h9)
from kit_h3 import open_book, reading_table
from kit_h10 import rng, lchair, ltable, llamp, candles, candlestick, door_panel, false_case, rects_minus, prune, done, count


# ---------------------------------------------------------------------------
# portals and mirrors
def P(c, n, w, h, up=None):
    d = {'c': [round(float(v), 3) for v in c], 'n': [round(float(v), 4) for v in n], 'w': round(float(w), 3), 'h': round(float(h), 3)}
    if up: d['up'] = [round(float(v), 4) for v in up]
    return d


def portal(R, a, b):
    R.meta.setdefault('portals', []).append({'a': a, 'b': b})


def mirror(R, c, n, w, h):
    R.meta.setdefault('mirrors', []).append(P(c, n, w, h))


def hdir(a):
    """Unit plan vector for an angle in radians."""
    return (math.cos(a), math.sin(a), 0.0)


# ---------------------------------------------------------------------------
# geometry in a local frame standing on the floor: u across (to the right as you face `face`), v up,
# t toward `face` (the viewer). face is a plan angle.
def local(g, face, cx, cy, cz):
    """Geo built with local x = u (across), y = t (toward the viewer), z = v (up) -> placed at (cx, cy, cz)
    with its +t facing plan angle `face`."""
    return g.xform(face - math.pi / 2, cx, cy, cz)


def lbox(u0, t0, v0, u1, t1, v1, m, **kw):
    return box(u0, t0, v0, u1, t1, v1, m, **kw)


def frame_geo(w, h, bw=0.22, depth=0.18, m='gilt', crest=0.0, t0=0.0, sill=True):
    """A moulded frame round a w x h opening whose bottom-middle is the local origin, standing proud of
    the wall (t 0..depth). Three stepped rings of mouldings; crest adds a raised cartouche on top."""
    g = Geo()
    for (e, d) in ((bw, depth * 0.55), (bw * 0.62, depth), (bw * 0.25, depth * 0.8)):
        # left, right, top, bottom bars of this ring
        g.add(lbox(-w / 2 - e, t0, -e if sill else 0.0, -w / 2, t0 + d, h + e, m, skip=('-y',)))
        g.add(lbox(w / 2, t0, -e if sill else 0.0, w / 2 + e, t0 + d, h + e, m, skip=('-y',)))
        g.add(lbox(-w / 2, t0, h, w / 2, t0 + d, h + e, m, skip=('-y',)))
        if sill: g.add(lbox(-w / 2, t0, -e, w / 2, t0 + d, 0.0, m, skip=('-y',)))
    if crest:
        g.add(lbox(-crest / 2, t0, h + bw, crest / 2, t0 + depth * 1.1, h + bw + crest * 0.45, m, skip=('-y',)))
        g.add(lbox(-crest * 0.3, t0, h + bw + crest * 0.45, crest * 0.3, t0 + depth * 0.9, h + bw + crest * 0.7, m, skip=('-y',)))
    return g


def architrave(w, h, m='walnut', bw=0.24, depth=0.12, t0=0.0, cornice=True):
    """A door surround: two pilasters and a lintel with a cornice, local frame (see frame_geo)."""
    g = Geo()
    g.add(lbox(-w / 2 - bw, t0, 0, -w / 2, t0 + depth, h, m, skip=('-y',)))
    g.add(lbox(w / 2, t0, 0, w / 2 + bw, t0 + depth, h, m, skip=('-y',)))
    g.add(lbox(-w / 2 - bw, t0, h, w / 2 + bw, t0 + depth, h + bw * 1.2, m, skip=('-y',)))
    if cornice:
        g.add(lbox(-w / 2 - bw * 1.5, t0, h + bw * 1.2, w / 2 + bw * 1.5, t0 + depth * 2.0, h + bw * 1.6, m, skip=('-y',)))
        g.add(lbox(-w / 2 - bw * 1.3, t0, h + bw * 1.6, w / 2 + bw * 1.3, t0 + depth * 1.4, h + bw * 1.75, m, skip=('-y',)))
    # plinths
    g.add(lbox(-w / 2 - bw - 0.03, t0, 0, -w / 2 + 0.01, t0 + depth + 0.04, 0.32, m, skip=('-y', '-z')))
    g.add(lbox(w / 2 - 0.01, t0, 0, w / 2 + bw + 0.03, t0 + depth + 0.04, 0.32, m, skip=('-y', '-z')))
    return g


def recess(R, c, n, w, h, depth=1.0, floor='floor', wall='tile', top='plaster', back=0.0):
    """Cut the opening a portal stands in: a box w x h reaching `depth` past the plane in direction n
    (and `back` before it)."""
    a = math.atan2(n[1], n[0])
    g = box(-back, -w / 2, 0, depth, w / 2, h, wall, bottom=floor, top=top)
    R.cut(g.xform(a, c[0], c[1], c[2]))


# ---------------------------------------------------------------------------
# stairs at any plan angle
def flight_at(R, x, y, z, ang, width, n, rise, run, m='terrazzo', riser=None, side='tile', solid_to=None):
    """A walkable flight climbing along plan angle `ang` from (x, y, z): (x, y) is the middle of its foot.
    Visible steps (nocol) plus the invisible ramp. solid_to: fill under the steps down to this z."""
    g = stairs(0, -width / 2, z, width, n, rise, run, '+x', m, riser, side)
    R.nocol.add(g.xform(ang, x, y, 0))
    L, Hh = n * run, n * rise
    q = [(-0.02, -width / 2, z), (L, -width / 2, z + Hh), (L, width / 2, z + Hh), (-0.02, width / 2, z)]
    gg = Geo(); ids = [gg.vert(p) for p in q]; gg.face(ids, 'floor', [(0, 0)] * 4)
    R.col.add(gg.xform(ang, x, y, 0))
    if solid_to is not None:
        R.parts.add(box(0, -width / 2, solid_to, L, width / 2, z, side, skip=('+z',)).xform(ang, x, y, 0))
    return (x + math.cos(ang) * L, y + math.sin(ang) * L, z + Hh)


def seg_rail(R, p0, p1, h=0.95, m='brass', post=1.1):
    """A rail from p0=(x,y,z) to p1 (sloped if the z differ): posts, top bar, invisible wall."""
    if abs(p0[2] - p1[2]) < 1e-6:
        rail(R, p0[0], p0[1], p1[0], p1[1], z=p0[2], h=h, m=m, post=post)
    else:
        stair_rail(R, p0[0], p0[1], p0[2], p1[0], p1[1], p1[2], h=h, m=m, post=post)


# ---------------------------------------------------------------------------
# books that are not on real shelves (tilted, curved): coloured blocks
BOOK_MATS = ('leather', 'oxblood', 'green', 'walnut', 'velvet', 'damask', 'leather', 'oxblood', 'slate')


def book_band(p0, du, dv, dn, L, H, rs, seg=(0.25, 0.6), depth=0.03):
    """Rows of book spines standing on a (possibly tilted) board: a band from point p0 along unit du for
    L metres, books up to H tall along unit dv, fronts facing unit dn. Returns {material: Geo}."""
    out = {}
    s = 0.0
    while s < L - 0.05:
        w = min(rs.uniform(*seg), L - s)
        hh = H * rs.uniform(0.72, 0.97)
        m = rs.choice(BOOK_MATS)
        dd = depth * rs.uniform(0.2, 1.0)
        P0 = [p0[i] + du[i] * s + dn[i] * dd for i in range(3)]
        pts = [P0, [P0[i] + du[i] * w for i in range(3)], [P0[i] + du[i] * w + dv[i] * hh for i in range(3)], [P0[i] + dv[i] * hh for i in range(3)]]
        g = out.setdefault(m, Geo())
        ids = [g.vert(tuple(p)) for p in pts]
        # face toward dn
        A = [pts[1][i] - pts[0][i] for i in range(3)]; B = [pts[3][i] - pts[0][i] for i in range(3)]
        cr = (A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0])
        if sum(cr[i] * dn[i] for i in range(3)) < 0: ids = ids[::-1]
        g.face(ids, m, [(0, 0), (w, 0), (w, hh), (0, hh)])
        s += w + 0.004
    return out


def add_bands(R, bands, col=False):
    for m, g in bands.items():
        (R.parts if col else R.nocol).add(g)


def merge_bands(acc, bands):
    for m, g in bands.items():
        acc.setdefault(m, Geo()).add(g)
    return acc


def floor_book(R, x, y, z=0.0, a=0.0, m='green'):
    """A single closed book lying on the floor."""
    g = Geo()
    g.add(box(-0.12, -0.09, 0, 0.12, 0.09, 0.045, m, skip=('-z',)))
    g.add(box(-0.105, -0.095, 0.006, 0.115, -0.09, 0.039, 'ivory', skip=('-z', '+z')))
    R.nocol.add(g.xform(a, x, y, z))


def painted_door(R, x, y, z, a, w=1.1, h=2.2, up=True):
    """A door painted flat on a floor (up=True) or a ceiling: the trompe-l'oeil hatches."""
    g = Geo()
    zz = z + (0.004 if up else -0.004)
    g.add(panel_z(zz, -w / 2 - 0.12, -h / 2 - 0.12, w / 2 + 0.12, h / 2 + 0.12, 'walnut', up=up))
    g.add(panel_z(zz + (0.002 if up else -0.002), -w / 2, -h / 2, w / 2, h / 2, 'oak', up=up))
    for (y0, y1) in ((-h / 2 + 0.15, -0.05), (0.08, h / 2 - 0.15)):
        g.add(panel_z(zz + (0.004 if up else -0.004), -w / 2 + 0.14, y0, w / 2 - 0.14, y1, 'walnut', up=up))
    g.add(panel_z(zz + (0.006 if up else -0.006), w / 2 - 0.22, -0.04, w / 2 - 0.12, 0.06, 'brass', up=up))
    R.nocol.add(g.xform(a, x, y, 0))
