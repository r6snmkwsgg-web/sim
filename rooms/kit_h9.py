"""Shared helpers for batch 9 of the Deep Stacks (wrong places): behindroom, beach, subway, motel,
stadium, wheatfield, airportgate, drainedpool. Doors in the library that open onto somewhere that is
not a library at all, built of the library's materials and full of its books."""
import random
from lib import *
import lib
from kit_a import (shell, obox, beam, rot, rail, stair_rail, shelf, sh, stack, chair, table, bulb, desk_lamp,
                   candle, navloop, tidy, frustum, floor_lamp, open_flight)
from kit_h4 import tube, curve, ladder_up, ramp, book, book_pile, sconce, water, pillar, BOOKM   # noqa (also registers grass, leaf...)
from kit_f import rail_line, rect_rails, balus
from kit_h3 import field, smooth_bump, ellipsoid, fill_under, window, pendant

NEW_MATS = {
    'sand':     (0.60, 0.57, 0.50),   # grey beach sand
    'wetsand':  (0.38, 0.36, 0.32),
    'wheat':    (0.80, 0.60, 0.26),   # ripe wheat
    'wheatdk':  (0.52, 0.37, 0.15),
    'earth':    (0.30, 0.22, 0.15),   # beaten earth path
    'wtile':    (0.86, 0.87, 0.85),   # white glazed tile (pool, subway)
    'turf':     (0.13, 0.30, 0.10),   # floodlit pitch
    'turf2':    (0.10, 0.25, 0.08),   # the mown stripes
    'seat':     (0.09, 0.22, 0.16),   # green stadium / airport seats
    'tactile':  (0.72, 0.56, 0.14),   # the yellow edge of a platform
    'concrete': (0.60, 0.60, 0.58),
    'rust':     (0.36, 0.19, 0.10),
    'hutred':   (0.64, 0.20, 0.16),
    'fuselage': (0.84, 0.85, 0.86),
    'path':     (0.52, 0.42, 0.29),   # a beaten track through a field
}
NEW_EMIT = {
    'e_fog':   ((0.86, 0.88, 0.90), 2.2),    # the lit fog beyond a window
    'e_flood': ((0.95, 0.97, 1.00), 22.0),   # stadium floodlight
    'e_sun':   ((1.00, 0.62, 0.26), 30.0),   # a low sun
    'e_dusk':  ((1.00, 0.66, 0.36), 5.0),    # the sky round a low sun
    'e_board': ((1.00, 0.70, 0.25), 5.0),    # departure board letters: stay lit
    'e_signal': ((1.00, 0.20, 0.10), 5.0),   # red tunnel signal: stays lit
}
for _k, _v in NEW_MATS.items(): lib.MATS.setdefault(_k, _v)
for _k, _v in NEW_EMIT.items(): lib.EMIT.setdefault(_k, _v)
lib.NIGHT_ON.update({'e_board', 'e_signal'})


# ---------------------------------------------------------------------------
# bookkeeping
def secret(R, x, y, z, name, text, r=1.6):
    R.meta.setdefault('secrets', []).append({'at': [round(x, 2), round(y, 2), round(z, 2)], 'r': r, 'name': name, 'text': text})


def fx(R, kind, bx=None, **kw):
    d = {'type': kind}
    if bx is not None: d['box'] = [round(float(v), 2) for v in bx]
    d.update(kw)
    R.meta.setdefault('fx', []).append(d)


def finish(R, label, blurb, weight=3, probe=(16, 8, 1.8), top=TOP):
    R.spot('probe', *probe)
    R.meta.update(label=label, weight=weight, blurb=blurb)
    R.meta['box'] = [[T, 0, T], [R.W - T, top, R.D - T]]
    return tidy(R)


def seal(R, skip, **kw):
    R.sockets(skip=skip, **kw)
    R.meta['sealed'] = [list(s) for s in skip]


def tunnel_x(R, cy, x0, x1, floor='floor', wall='tile', z=0.0):
    """Carry a W/E doorway arch through extra wall thickness (x0..x1) at y=cy."""
    pr = arch_profile(cy, DW, z, DJ)
    R.cut(prism(pr, 'x', x0, x1, arch_mats(len(pr), floor, wall)))


def tunnel_y(R, cx, y0, y1, floor='floor', wall='tile', z=0.0):
    pr = arch_profile(cx, DW, z, DJ)
    R.cut(prism(pr, 'y', y0, y1, arch_mats(len(pr), floor, wall)))


# ---------------------------------------------------------------------------
# pieces
def quad(p, m, uv=None, flip=False):
    """One face from 3D points (drawn one-sided: its front is counter-clockwise)."""
    g = Geo(); ids = [g.vert(q) for q in p]
    if flip: ids = ids[::-1]
    g.face(ids, m, uv or [(q[0] + q[1], q[2]) for q in (p[::-1] if flip else p)])
    return g


def panel_x(x, y0, y1, z0, z1, m, face=1):
    """A single vertical face in the plane x=const, facing +x (face=1) or -x."""
    P = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
    return quad(P, m, [(p[1], p[2]) for p in P], flip=face < 0)


def panel_y(y, x0, x1, z0, z1, m, face=1):
    """A single vertical face in the plane y=const, facing +y (face=1) or -y."""
    P = [(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)]
    return quad(P, m, [(p[0], p[2]) for p in P], flip=face < 0)


def panel_z(z, x0, y0, x1, y1, m, up=True):
    P = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    return quad(P, m, [(p[0], p[1]) for p in P], flip=not up)


def shell_cyl(cx, cy, z0, z1, r, segs, m, inner=None, t=0.06, a0=0.0, a1=2 * math.pi):
    """An open cylinder wall seen from both sides (outer face m, inner face `inner`)."""
    g = cyl(cx, cy, z0, z1, r, segs, side=m, caps=False, a0=a0, a1=a1)
    gi = cyl(cx, cy, z0, z1, r - t, segs, side=inner or m, caps=False, a0=a0, a1=a1)
    gi.f = [tuple(reversed(f)) for f in gi.f]; gi.uv = [list(reversed(u)) for u in gi.uv]
    g.add(gi)
    return g


def xtube(x0, x1, cy, cz, r, segs=12, m='iron'):
    """A horizontal pipe along x."""
    return tube([(x0, cy, cz), (x1, cy, cz)], r, segs, m)


def ytube(y0, y1, cx, cz, r, segs=12, m='iron'):
    return tube([(cx, y0, cz), (cx, y1, cz)], r, segs, m)


def ztube(z0, z1, cx, cy, r, segs=12, m='iron'):
    return cyl(cx, cy, z0, z1, r, segs, side=m, top=m, bottom=m)


def door_leaf(w, h, m='walnut', panel='oak', knob='brass', t=0.05):
    """A panelled door leaf standing in the x-z plane from x=0 to w, y -t..0 (hinge at x=0)."""
    g = box(0, -t, 0, w, 0.0, h, m)
    for (z0, z1) in ((0.18, h * 0.45), (h * 0.52, h - 0.18)):
        g.add(box(0.12, -t - 0.015, z0, w - 0.12, -t, z1, panel))
        g.add(box(0.12, 0.0, z0, w - 0.12, 0.015, z1, panel))
    g.add(box(w - 0.14, -t - 0.07, 1.0, w - 0.08, 0.07, 1.06, knob))
    return g


def rug(R, x0, y0, x1, y1, z=0.0, m='carpet', border='gilt'):
    R.nocol.add(box(x0, y0, z, x1, y1, z + 0.012, border))
    R.nocol.add(box(x0 + 0.12, y0 + 0.12, z + 0.012, x1 - 0.12, y1 - 0.12, z + 0.02, m))


def cot(R, x0, y0, x1, y1, z=0.0, h=0.42, frame='iron', blanket='green', pillow='bed', along='x'):
    """A narrow bed: frame, mattress, a blanket, a pillow at the x0 (or y0) end."""
    R.parts.add(box(x0, y0, z + 0.12, x1, y1, z + h - 0.12, frame))
    for (px, py) in ((x0 + 0.05, y0 + 0.05), (x1 - 0.05, y0 + 0.05), (x1 - 0.05, y1 - 0.05), (x0 + 0.05, y1 - 0.05)):
        R.parts.add(box(px - 0.03, py - 0.03, z, px + 0.03, py + 0.03, z + 0.12, frame))
    R.parts.add(box(x0 + 0.02, y0 + 0.02, z + h - 0.12, x1 - 0.02, y1 - 0.02, z + h, 'bed'))
    if along == 'x':
        R.nocol.add(box(x0 + 0.55, y0 - 0.02, z + h - 0.06, x1 + 0.02, y1 + 0.02, z + h + 0.04, blanket))
        R.nocol.add(box(x0 + 0.08, y0 + 0.1, z + h, x0 + 0.5, y1 - 0.1, z + h + 0.12, pillow))
        R.spot('bed', (x0 + x1) / 2, (y0 + y1) / 2, z + h, 0.0)
    else:
        R.nocol.add(box(x0 - 0.02, y0 + 0.55, z + h - 0.06, x1 + 0.02, y1 + 0.02, z + h + 0.04, blanket))
        R.nocol.add(box(x0 + 0.1, y0 + 0.08, z + h, x1 - 0.1, y0 + 0.5, z + h + 0.12, pillow))
        R.spot('bed', (x0 + x1) / 2, (y0 + y1) / 2, z + h, math.pi / 2)


def crate(R, x, y, z, s=0.6, h=None, m='oak', ang=0.0, col=True):
    h = h or s
    g = box(-s / 2, -s / 2, 0, s / 2, s / 2, h, m)
    for k in (-1, 1):
        g.add(box(-s / 2 - 0.01, k * s / 2 - 0.04 if k > 0 else -s / 2 - 0.0, 0.05, s / 2 + 0.01, (k * s / 2 + 0.01) if k > 0 else -s / 2 + 0.04, 0.12, 'walnut'))
    (R.parts if col else R.nocol).add(g.xform(ang, x, y, z))


def book_row_flat(g, x, y, z, ang, rnd, n=1):
    """n books lying flat, stacked (into a Geo)."""
    h = 0.0
    for i in range(n):
        t = rnd.uniform(0.03, 0.055)
        g.add(box(-0.12, -0.085, h, 0.12, 0.085, h + t, rnd.choice(BOOKM), skip=('-z',)).xform(ang + rnd.uniform(-0.25, 0.25), x, y, z))
        h += t
    return h
