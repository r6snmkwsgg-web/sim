"""Shared helpers for batch 10 of the Deep Stacks (wrong places II, traces of others): deadmall, bigbedroom,
highway, banquet, waitingroom2, classroom, coatroom, ballroom, lostshrine, dormitory2, bigtheatre,
graffitistair, lastreader. Rooms made for people who are not there, but were, a moment ago.

Many of these rooms are full of repeated things (chairs, desks, coats, beds, plates): the pieces here
are a handful of boxes each, with the faces nobody sees left out, so the lightmap packs well."""
import random
from lib import *
import lib
from kit_a import (shell, obox, beam, rot, rail, stair_rail, shelf, sh, stack, chair, table, bulb, desk_lamp,
                   candle, navloop, tidy, frustum, floor_lamp, open_flight, ladder)
from kit_h9 import (secret, fx, finish, seal, tunnel_x, tunnel_y, quad, panel_x, panel_y, panel_z, door_leaf, rug,
                    cot, crate, book_row_flat, xtube, ytube, ztube, shell_cyl)
from kit_h4 import tube, curve, ladder_up, ramp, book, book_pile, sconce, water, rwater, pillar, BOOKM
from kit_h3 import window, pendant, lamp_post, arch_hole, armchair
from kit_h2 import weld, lattice, hung_flight, railed_flight
from kit_f import rail_line, rect_rails, balus, chandelier
from kit_h5 import hdisc, blob, cone, orient, lantern
from kit_g import upper_sockets

NEW_MATS = {
    'asphalt':  (0.10, 0.10, 0.10),
    'lineW':    (0.80, 0.80, 0.76),   # road paint
    'lineY':    (0.78, 0.58, 0.12),
    'coat1':    (0.13, 0.085, 0.055),   # tweed
    'coat2':    (0.022, 0.028, 0.06),   # navy
    'coat3':    (0.045, 0.045, 0.048),   # charcoal
    'coat4':    (0.26, 0.16, 0.08),   # camel
    'coat5':    (0.03, 0.065, 0.04),   # bottle green
    'coat6':    (0.17, 0.05, 0.03),   # rust red
    'ink':      (0.05, 0.04, 0.035),
    'inkblue':  (0.06, 0.08, 0.18),
    'inkred':   (0.30, 0.05, 0.04),
    'chalk':    (0.78, 0.78, 0.72),
    'steel':    (0.52, 0.53, 0.55),
    'cloth':    (0.88, 0.86, 0.80),   # table linen
    'food':     (0.55, 0.30, 0.12),   # roast, bread
    'fruit':    (0.60, 0.16, 0.10),
    'grape':    (0.22, 0.10, 0.20),
    'shoe':     (0.16, 0.09, 0.05),
    'wool':     (0.20, 0.30, 0.42),   # a child's blue blanket
}
NEW_EMIT = {
    'e_sodium': ((1.00, 0.52, 0.16), 18.0),   # motorway lamps
    'e_moon':   ((0.55, 0.68, 1.00), 3.2),    # moonlight through a window
    'e_digit':  ((0.30, 1.00, 0.55), 6.0),    # the number display: stays lit
    'e_flame':  ((1.00, 0.50, 0.18), 8.0),    # a stove's low fire: stays lit
    'e_reader': ((1.00, 0.80, 0.52), 24.0),   # the one lamp left on: stays lit
}
for _k, _v in NEW_MATS.items(): lib.MATS.setdefault(_k, _v)
for _k, _v in NEW_EMIT.items(): lib.EMIT.setdefault(_k, _v)
lib.NIGHT_ON.update({'e_digit', 'e_flame', 'e_moon', 'e_reader'})


def rng(seed):
    return random.Random(seed)


# ---------------------------------------------------------------------------
# light pieces for rooms full of them (return Geo; the caller adds them, merged)
def lchair(x, y, face, frame='walnut', seat='leather', back_h=0.95, s=1.0):
    """A chair of three boxes (legs read as a dark skirt under the seat): about 14 faces. The sitter faces `face`."""
    g = Geo()
    g.add(box(-0.19 * s, -0.19 * s, 0, 0.19 * s, 0.19 * s, 0.42 * s, frame, skip=('-z', '+z')))
    g.add(box(-0.23 * s, -0.23 * s, 0.42 * s, 0.23 * s, 0.23 * s, 0.48 * s, seat, sides=frame, skip=('-z',)))
    g.add(box(-0.25 * s, -0.23 * s, 0.48 * s, -0.19 * s, 0.23 * s, back_h * s, frame, skip=('-z',)))
    return g.xform(face, x, y, 0)


def lchair_legs(x, y, face, frame='walnut', seat='leather', back_h=0.95):
    """A chair with four real legs (about 26 faces): for the few chairs you look at closely."""
    return chair(x, y, face, frame, seat, back_h)


def ltable(x0, y0, x1, y1, h=0.76, m='walnut', top=None, legs=True):
    g = box(x0, y0, h - 0.05, x1, y1, h, m, top=top)
    if legs:
        for (px, py) in ((x0 + 0.08, y0 + 0.08), (x1 - 0.08, y0 + 0.08), (x1 - 0.08, y1 - 0.08), (x0 + 0.08, y1 - 0.08)):
            g.add(box(px - 0.035, py - 0.035, 0, px + 0.035, py + 0.035, h - 0.05, m, skip=('-z', '+z')))
    return g


def llamp(R, x, y, z, a=0.0, lit=True, m='e_lamp', col=False):
    """A banker's lamp of four boxes; lit=False leaves the shade dark."""
    g = Geo()
    g.add(box(-0.08, -0.06, 0, 0.08, 0.06, 0.03, 'brass', skip=('-z',)))
    g.add(box(-0.012, -0.012, 0.03, 0.012, 0.012, 0.36, 'brass', skip=('-z', '+z')))
    g.add(box(-0.18, -0.07, 0.36, 0.18, 0.07, 0.45, 'green', bottom='ivory' if lit else 'green'))
    (R.parts if col else R.nocol).add(g.xform(a, x, y, z))
    if lit:
        R.light(box(-0.15, -0.045, 0.345, 0.15, 0.045, 0.36, m, skip=('+z',)).xform(a, x, y, z))


def lcandle(x, y, z, h=0.2, r=0.025, m='ivory'):
    """A candle as a square stick (4 faces + top); returns (stick, flame)."""
    a0 = (x * 7.1 + y * 3.3) % 6.28
    st = poly_prism([(x + r * 1.2 * math.cos(a0 + k * 2.094), y + r * 1.2 * math.sin(a0 + k * 2.094)) for k in range(3)], z, z + h, side=m, top=m, bottom=m)
    st.f = st.f[:-2] + st.f[-1:]; st.m = st.m[:-2] + st.m[-1:]; st.uv = st.uv[:-2] + st.uv[-1:]
    fl = box(x - r * 0.45, y - r * 0.45, z + h + 0.005, x + r * 0.45, y + r * 0.45, z + h + 0.06, 'e_candle', skip=('-z',))
    return st, fl


def candles(R, pts, rs, hmin=0.1, hmax=0.35, rmin=0.018, rmax=0.04, m='ivory'):
    """Candles at the given (x, y, z) points, drawn merged; their flames glow and stay lit."""
    g = Geo(); f = Geo()
    for (x, y, z) in pts:
        st, fl = lcandle(x, y, z, rs.uniform(hmin, hmax), rs.uniform(rmin, rmax), m)
        g.add(st); f.add(fl)
    R.nocol.add(g); R.light(f)


def candlestick(R, x, y, z, h=0.45, arms=0, rs=None):
    """A brass candlestick (optionally a candelabrum with arms) with lit candles."""
    g = Geo()
    g.add(box(x - 0.07, y - 0.07, z, x + 0.07, y + 0.07, z + 0.03, 'brass', skip=('-z',)))
    g.add(box(x - 0.015, y - 0.015, z + 0.03, x + 0.015, y + 0.015, z + h, 'brass', skip=('-z', '+z')))
    tops = [(x, y, z + h)]
    if arms:
        for k in range(arms):
            a = 2 * math.pi * k / arms
            ex, ey = x + math.cos(a) * 0.16, y + math.sin(a) * 0.16
            g.add(beam((x, y, z + h * 0.72), (ex, ey, z + h * 0.8), 0.018, 'brass'))
            g.add(box(ex - 0.02, ey - 0.02, z + h * 0.8, ex + 0.02, ey + 0.02, z + h * 0.84, 'brass'))
            tops.append((ex, ey, z + h * 0.84))
    g.add(box(x - 0.03, y - 0.03, z + h - 0.01, x + 0.03, y + 0.03, z + h, 'brass'))
    R.nocol.add(g)
    candles(R, tops, rs or rng(int(x * 7 + y * 13)), 0.14, 0.24, 0.016, 0.02)


# ---------------------------------------------------------------------------
# architecture
def vault_cut(R, axis, c, w, a0, a1, z0, jamb, rise=None, m='plaster', floor='floor', wall='tile', segs=16):
    """Carve a barrel-vaulted hall running along axis ('x' or 'y') between a0 and a1, w wide centred on c,
    walls to `jamb`, then a round (or flattened, by rise) vault."""
    pr = arch_profile(c, w, z0, jamb, segs, rise=rise)
    n = len(pr)
    mats = [floor, wall] + [m] * (n - 3) + [wall]
    R.cut(prism(pr, axis, a0, a1, mats, cap=wall))


def ribs(R, axis, c, w, positions, z0, jamb, rise=None, d=0.35, t=0.4, m='tile', segs=16):
    """Transverse arch ribs under a vault (at the given positions along axis)."""
    from kit_h3 import arc_band
    band = arc_band(c, w, jamb, rise if rise is not None else w / 2, 0.0, d, segs)
    band = [(p, q + z0) for p, q in band]
    for s in positions:
        R.parts.add(prism(band, axis, s - t / 2, s + t / 2, m, cap=m))


def piers_line(R, axis, fixed, a0, a1, n, z0, z1, s=0.6, m='tile'):
    """n square piers evenly spaced along a line."""
    out = []
    for k in range(n):
        p = a0 + (a1 - a0) * (k + 0.5) / n
        x, y = (p, fixed) if axis == 'x' else (fixed, p)
        R.parts.add(box(x - s / 2, y - s / 2, z0, x + s / 2, y + s / 2, z1, m, skip=('-z', '+z')))
        R.parts.add(box(x - s / 2 - 0.1, y - s / 2 - 0.1, z0, x + s / 2 + 0.1, y + s / 2 + 0.1, z0 + 0.35, m, skip=('-z',)))
        R.parts.add(box(x - s / 2 - 0.12, y - s / 2 - 0.12, z1 - 0.3, x + s / 2 + 0.12, y + s / 2 + 0.12, z1, m, skip=('+z',)))
        out.append((x, y))
    return out


def door_panel(R, x, y, face, w=1.2, h=2.3, m='walnut', panel='oak', ajar=0.0, col=True):
    """A closed (or ajar) panelled door standing at (x, y) on a wall, its front facing plan angle face.
    x, y is the middle of its bottom edge on the wall face."""
    lf = door_leaf(w, h, m, panel)
    # leaf spans local x 0..w, y -t..0: put its front (the -y side) toward `face`
    if ajar:
        rot(lf, 'z', ajar)
    lf.xform(face + math.pi / 2, 0, 0, 0)
    ca, sa = math.cos(face + math.pi / 2), math.sin(face + math.pi / 2)
    lf.xform(0, x - ca * w / 2, y - sa * w / 2, 0)
    (R.parts if col else R.nocol).add(lf)


def seg_digit(R, x, y, z, ch, face, s=0.5, m='e_digit', back='black'):
    """A seven-segment digit ch ('0'-'9') on a wall facing plan angle face; (x, y, z) its bottom-left."""
    SEG = {'0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg', '5': 'acdfg', '6': 'acdefg',
           '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
    w, h, t = s * 0.55, s, s * 0.1
    rects = {'a': (t, h - t, w - t, h), 'g': (t, h / 2 - t / 2, w - t, h / 2 + t / 2), 'd': (t, 0, w - t, t),
             'f': (0, h / 2, t, h - t), 'b': (w - t, h / 2, w, h - t), 'e': (0, t, t, h / 2), 'c': (w - t, t, w, h / 2)}
    ux, uy = math.cos(face + math.pi / 2), math.sin(face + math.pi / 2)
    nx, ny = math.cos(face), math.sin(face)
    for k in SEG[ch]:
        u0, v0, u1, v1 = rects[k]
        P = [(x + ux * u0 + nx * 0.01, y + uy * u0 + ny * 0.01, z + v0), (x + ux * u1 + nx * 0.01, y + uy * u1 + ny * 0.01, z + v0),
             (x + ux * u1 + nx * 0.01, y + uy * u1 + ny * 0.01, z + v1), (x + ux * u0 + nx * 0.01, y + uy * u0 + ny * 0.01, z + v1)]
        g = quad(P, m)
        # face it toward +n
        A = [P[1][i] - P[0][i] for i in range(3)]; B = [P[2][i] - P[0][i] for i in range(3)]
        cr = (A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2])
        if cr[0] * nx + cr[1] * ny < 0: g.f = [tuple(reversed(f)) for f in g.f]
        R.light(g)


def false_case(R, x, y, L, dirn, rows=6, frame='walnut', h=2.3, depth=0.6, floor='floor', wall='tile', top='plaster', thru=None):
    """A false bookcase standing in a wall face at (x, y) (as R.shelf: back-left corner seen from the front),
    with the opening behind it cut `depth` (or up to `thru`) into the wall."""
    shelf(R, x, y, 0, L, dirn, rows=rows, frame=frame, solid=False)
    a = {'+y': math.pi / 2, '-y': -math.pi / 2, '+x': 0.0, '-x': math.pi}[dirn]
    th = a - math.pi / 2
    c, s_ = math.cos(th), math.sin(th)
    # the wall face is at the case's back; the opening goes behind it (against the facing direction)
    nx, ny = math.cos(a), math.sin(a)
    x1, y1 = x + c * L, y + s_ * L
    d = depth
    xs = [x + c * 0.05 - nx * 0.05, x1 - c * 0.05 - nx * 0.05, x + c * 0.05 - nx * d, x1 - c * 0.05 - nx * d]
    ys = [y + s_ * 0.05 - ny * 0.05, y1 - s_ * 0.05 - ny * 0.05, y + s_ * 0.05 - ny * d, y1 - s_ * 0.05 - ny * d]
    R.cut(box(min(xs), min(ys), 0, max(xs), max(ys), h, wall, bottom=floor, top=top))


def confetti(R, x0, y0, x1, y1, z, n, rs, mats=('gilt', 'ivory', 'oxblood', 'green'), s=0.04):
    """Flat scraps on a floor, merged per material."""
    gs = {m: Geo() for m in mats}
    for k in range(n):
        x, y = rs.uniform(x0, x1), rs.uniform(y0, y1)
        a = rs.uniform(0, math.pi)
        m = rs.choice(mats)
        ss = s * rs.uniform(0.6, 1.4)
        gs[m].add(panel_z(z + 0.004 + 0.001 * (k % 3), -ss, -ss * 0.6, ss, ss * 0.6, m).xform(a, x, y, 0))
    for g in gs.values():
        if g.f: R.nocol.add(g)


def streamer(R, x, y, ztop, L, rs, m='gilt', r=0.07, turns=None, w=0.03):
    """A curling paper streamer hanging from the ceiling: a flat ribbon spiralling down (two sheets a
    hair apart, so it shows from both sides)."""
    turns = turns or L / 0.45
    n = int(turns * 8)
    g = Geo()
    prev = None
    a0 = rs.uniform(0, 6.28)
    for k in range(n + 1):
        t = k / n
        a = a0 + turns * 2 * math.pi * t
        z = ztop - L * t
        cx, cy = x + r * math.cos(a), y + r * math.sin(a)
        ix, iy = x + (r - 0.004) * math.cos(a), y + (r - 0.004) * math.sin(a)
        ux, uy = -math.sin(a) * w, math.cos(a) * w
        cur = (g.vert((cx, cy, z - w)), g.vert((cx, cy, z + w)), g.vert((ix, iy, z - w)), g.vert((ix, iy, z + w)))
        if prev:
            g.face([prev[0], cur[0], cur[1], prev[1]], m, [(0, 0), (1, 0), (1, 1), (0, 1)])
            g.face([prev[3], cur[3], cur[2], prev[2]], m, [(0, 0), (1, 0), (1, 1), (0, 1)])
        prev = cur
    R.nocol.add(g)


def pleats(x0, x1, y, z0, z1, n, depth=0.12, m='velvet', face=-1, t=0.02):
    """A curtain in the x-z plane at y: a zigzag of n folds, as a thin closed sheet (t thick)."""
    xs = [x0 + (x1 - x0) * k / (2 * n) for k in range(2 * n + 1)]
    prof = [(xx, y + (depth if k % 2 else 0.0) * -face) for k, xx in enumerate(xs)]
    back = [(xx, yy - face * t) for (xx, yy) in reversed(prof)]
    pts = prof + back
    return poly_prism(pts, z0, z1, side=m, top=m, bottom=m)


def glass_rail(R, x0, y0, x1, y1, z, h=1.0, m='steel', cap='brass'):
    """A mall-style parapet: a solid low panel with a brass cap (collided)."""
    R.parts.add(obox(x0, y0, x1, y1, z, z + h, 0.12, m, skip=('-z',)))
    R.parts.add(obox(x0, y0, x1, y1, z + h, z + h + 0.06, 0.18, cap))


def count(R):
    return len(R.parts.f) + len(R.nocol.f)


def rects_minus(x0, y0, x1, y1, holes):
    """The rectangle minus some rectangular holes, as a few rectangles (grid split, merged along x)."""
    xs = sorted(set([x0, x1] + [min(max(h[0], x0), x1) for h in holes] + [min(max(h[2], x0), x1) for h in holes]))
    ys = sorted(set([y0, y1] + [min(max(h[1], y0), y1) for h in holes] + [min(max(h[3], y0), y1) for h in holes]))
    out = []
    for j in range(len(ys) - 1):
        run = None
        for i in range(len(xs) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            inside = any(h[0] <= cx <= h[2] and h[1] <= cy <= h[3] for h in holes)
            if not inside and xs[i + 1] - xs[i] > 1e-6 and ys[j + 1] - ys[j] > 1e-6:
                run = [run[0], xs[i + 1]] if run else [xs[i], xs[i + 1]]
            else:
                if run: out.append((run[0], ys[j], run[1], ys[j + 1])); run = None
        if run: out.append((run[0], ys[j], run[1], ys[j + 1]))
    return out


def solid_minus(g, x0, y0, x1, y1, z0, z1, holes, m='tile', top=None, bottom=None, sides=None):
    for (a, b, c, d) in rects_minus(x0, y0, x1, y1, holes):
        g.add(box(a, b, z0, c, d, z1, m, top=top, bottom=bottom, sides=sides))
    return g


def prune(R, amin=1.5e-4, tmin=0.006):
    """Drop faces too small to see (under ~1.2 cm square): they only crowd the lightmap, and very thin
    slivers can crash Blender's island packer."""
    def area(g, f):
        P = [g.v[i] for i in f]
        ax = ay = az = 0.0
        for i in range(1, len(P) - 1):
            ux, uy, uz = P[i][0] - P[0][0], P[i][1] - P[0][1], P[i][2] - P[0][2]
            vx, vy, vz = P[i + 1][0] - P[0][0], P[i + 1][1] - P[0][1], P[i + 1][2] - P[0][2]
            ax += uy * vz - uz * vy; ay += uz * vx - ux * vz; az += ux * vy - uy * vx
        A = 0.5 * math.sqrt(ax * ax + ay * ay + az * az)
        L = max(math.dist(P[i], P[(i + 1) % len(P)]) for i in range(len(P)))
        return A if 2 * A / max(L, 1e-9) >= tmin else 0.0
    gs = [R.parts, R.nocol] + [M.parts for M in R.movers] + [M.nocol for M in R.movers]
    n = 0
    for g in gs:
        keep = [k for k, f in enumerate(g.f) if area(g, f) >= amin]
        n += len(g.f) - len(keep)
        g.f = [g.f[k] for k in keep]; g.m = [g.m[k] for k in keep]; g.uv = [g.uv[k] for k in keep]
    return n


def done(R, label, blurb, weight=3, probe=(16, 8, 1.8), top=TOP):
    prune(R)
    return finish(R, label, blurb, weight=weight, probe=probe, top=top)
