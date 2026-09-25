"""Shared helpers for batch 8 of the Deep Stacks (voids II, inversions): stairblack, catwalks, singlechair,
upsidedown, insideout, ceilinggarden, symmetry, waterceiling."""
import random
from lib import *
import lib
from kit_a import (sh, shelf as kshelf, stack, chair as chair_geo, table as table_geo, bulb, desk_lamp, candle, floor_lamp,
                   navloop, tidy, beam, rot, frustum, obox, rail as brass_rail, stair_rail, inv_shelf)
from kit_g import (flight as rflight, flight_rail, rail as stone_rail, iron_rail, wall_cases, seal, upper_sockets,
                   lamppost, hanging, sloped)
from kit_f import rect_rails, rail_line, chandelier, bar
from kit_h4 import ladder_up, ramp, tube, branches, moss_slab, NEW_MATS
from kit_h5 import leaves, vine, cone, blob, orient
from kit_h3 import pendant, armchair, reading_table, book_pile, open_book, lamp_post

for _k, _v in {'fish': (0.55, 0.52, 0.46), 'fishred': (0.70, 0.30, 0.16), 'rope': (0.55, 0.44, 0.28)}.items():
    lib.MATS.setdefault(_k, _v)


# ---------------------------------------------------------------------------
# bookkeeping
def secret(R, x, y, z, name, text, r=1.5):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, bx=None, **kw):
    d = {'type': kind}
    if bx is not None: d['box'] = [round(float(v), 2) for v in bx]
    for k, v in kw.items(): d[k] = [round(float(c), 2) for c in v] if isinstance(v, (list, tuple)) else v
    R.meta.setdefault('fx', []).append(d)


def finish(R, label, blurb, weight=3, probe=(16, 16, 1.8), top=TOP, bot=0.0):
    R.spot('probe', *probe)
    R.meta.update(label=label, weight=weight, blurb=blurb)
    R.meta['box'] = [[T, bot, T], [R.W - T, top, R.D - T]]
    return tidy(R)


# ---------------------------------------------------------------------------
# furniture
def chair(R, x, y, face, z=0.0, frame='walnut', seat='leather', spot=True, col=True):
    g = chair_geo(x, y, face, frame, seat); g.xform(0, 0, 0, z)
    (R.parts if col else R.nocol).add(g)
    if spot: R.spot('sit', x, y, z + 0.48, face)


def table(R, x0, y0, x1, y1, z=0.0, h=0.76, m='walnut', top=None):
    g = table_geo(x0, y0, x1, y1, h, m, top); g.xform(0, 0, 0, z); R.parts.add(g)


def flipz(g, zc):
    """Mirror a piece upside down about the plane z = zc (fixing its winding)."""
    g.v = [(a, b, 2 * zc - c) for a, b, c in g.v]
    g.f = [tuple(reversed(f)) for f in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    return g


def book_row(x0, y0, x1, y1, z, h=0.26, rnd=None, t=0.2):
    """Loose upright books standing in a row between two points (drawn, not collided)."""
    rnd = rnd or random.Random(1)
    g = Geo()
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    s = 0.0
    while s < L - 0.05:
        w = rnd.uniform(0.03, 0.06); hh = h * rnd.uniform(0.75, 1.0)
        b = box(0, -t / 2, 0, w - 0.004, t / 2, hh, rnd.choice(('oxblood', 'green', 'leather', 'walnut', 'velvet')))
        b.xform(math.atan2(uy, ux), x0 + ux * s, y0 + uy * s, z)
        g.add(b); s += w
    return g


def green_standard(R, x, y, z, h=1.5, m='e_lamp'):
    """A brass standard with a green banker's shade, standing on a balustrade or a newel."""
    R.nocol.add(cyl(x, y, z, z + 0.05, 0.1, 10, side='brass', top='brass'))
    R.nocol.add(cyl(x, y, z + 0.05, z + h, 0.02, 6, side='brass', caps=False))
    R.nocol.add(frustum(x, y, z + h - 0.16, z + h + 0.04, 0.3, 0.12, 12, 'green', inner='ivory'))
    R.light(cyl(x, y, z + h - 0.1, z + h - 0.07, 0.14, 8, side=m, top=m, bottom=m))


def fish(x, y, z, a, L=0.6, m='fish', fin='fishred'):
    """A fish: a lozenge body, a tail, a dorsal fin; swimming toward plan angle a."""
    g = Geo()
    g.add(blob(0, 0, 0, L / 2, L * 0.12, L * 0.18, segs=8, rings=4, m=m))
    tl = Geo(); ids = [tl.vert(p) for p in ((-L * 0.45, 0, 0), (-L * 0.75, 0, L * 0.2), (-L * 0.75, 0, -L * 0.2))]
    tl.face(ids, fin, [(0, 0)] * 3); tl.face(ids[::-1], fin, [(0, 0)] * 3)
    g.add(tl)
    df = Geo(); ids = [df.vert(p) for p in ((L * 0.1, 0, L * 0.15), (-L * 0.2, 0, L * 0.15), (-L * 0.15, 0, L * 0.3))]
    df.face(ids, fin, [(0, 0)] * 3); df.face(ids[::-1], fin, [(0, 0)] * 3)
    g.add(df)
    return g.xform(a, x, y, z)


def inverted(R, fn, zc):
    """Build something the right way up on the floor (z = 0) with fn(), then hang it upside down from a
    ceiling at 2 * zc (drawn, not collided). Its book slabs and emitters go with it; its spots are dropped."""
    saved = (R.parts, R.nocol, R.col, R.emit)
    R.parts, R.nocol, R.col, R.emit = Geo(), Geo(), Geo(), Geo()
    n0, s0 = len(R.slabs), len(R.spots)
    fn()
    g = Geo(); g.add(R.parts); g.add(R.nocol)
    e = R.emit
    R.parts, R.nocol, R.col, R.emit = saved
    R.nocol.add(flipz(g, zc)); R.emit.add(flipz(e, zc))
    for s in R.slabs[n0:]:
        o = list(s['o']); o[2] = 2 * zc - o[2] - s['v'][2]; s['o'] = o
    del R.spots[s0:]


def tree_geo(R, x, y, rnd, h=5.5, spread=2.4, m_bark='bark', m_leaf='leaf', crown=1.0):
    """A broad tree standing at (x, y, 0): trunk, root flare, limbs, a crown of leaf clusters (drawn only)."""
    lean = (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4))
    top = (x + lean[0], y + lean[1], h * 0.55)
    R.nocol.add(tube([(x, y, -0.1), (x + lean[0] * 0.4, y + lean[1] * 0.4, h * 0.3), top], [0.42, 0.32, 0.26], 10, m_bark))
    for k in range(5):
        a = k * 2 * math.pi / 5 + rnd.uniform(-0.4, 0.4)
        R.nocol.add(tube([(x, y, 0.45), (x + math.cos(a) * 0.7, y + math.sin(a) * 0.7, 0.08), (x + math.cos(a) * 1.3, y + math.sin(a) * 1.3, -0.05)], [0.2, 0.12, 0.05], 6, m_bark))
    n = rnd.randint(4, 6)
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.3, 0.3)
        d = spread * rnd.uniform(0.7, 1.0)
        end = (top[0] + math.cos(a) * d, top[1] + math.sin(a) * d, h + rnd.uniform(-0.3, 0.8))
        mid = (top[0] + math.cos(a) * d * 0.45, top[1] + math.sin(a) * d * 0.45, top[2] + (end[2] - top[2]) * 0.7)
        R.nocol.add(tube([top, mid, end], [0.17, 0.1, 0.05], 6, m_bark))
        leaves(R, end[0], end[1], end[2] + 0.3, rnd.uniform(1.2, 1.6) * crown, int(3 * crown + 0.5), rnd, m=m_leaf)
    leaves(R, top[0], top[1], h + 0.9, 1.8 * crown, int(4 * crown + 0.5), rnd, m=m_leaf)
