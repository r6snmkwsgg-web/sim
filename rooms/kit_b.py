"""Shared helpers for batch "b" rooms."""
from lib import *

SEGS = ((0.6, 6.2), (9.8, C - 0.6))        # wall stretches either side of a doorway


def shell(R, H=TOP, wall='tile', floor='floor', ceil='plaster', inset=T):
    R.sockets(floor=floor, wall=wall)
    R.cut(box(inset - 0.02, inset - 0.02, 0, C - inset + 0.02, C - inset + 0.02, H, wall, bottom=floor, top=ceil))


def bshelf(R, x, y, z, length, dirn, rows=5, row_h=0.42, depth=0.34, **kw):
    """R.shelf drawn without collision, plus one invisible box that collides: far fewer collision
    triangles for the same bookcase."""
    ids = R.shelf(x, y, z, length, dirn, rows=rows, row_h=row_h, depth=depth, solid=False, **kw)
    a = {'+y': math.pi / 2, '-y': -math.pi / 2, '+x': 0.0, '-x': math.pi}[dirn] if isinstance(dirn, str) else dirn
    H = rows * row_h + 0.035 + 0.08 + (0.06 if kw.get('crown', True) else 0.0)
    R.col.add(box(-0.04, 0, 0, length + 0.04, depth + 0.03, H, 'tile').xform(a - math.pi / 2, x, y, z))
    return ids


def wall_shelves(R, rows=7, frame='oak', sides='SNWE', segs=SEGS, z=0.0, inset=T, **kw):
    for (a, b) in segs:
        if 'S' in sides: bshelf(R, a, inset, z, b - a, '+y', rows=rows, frame=frame, **kw)
        if 'N' in sides: bshelf(R, b, C - inset, z, b - a, '-y', rows=rows, frame=frame, **kw)
        if 'W' in sides: bshelf(R, inset, b, z, b - a, '+x', rows=rows, frame=frame, **kw)
        if 'E' in sides: bshelf(R, C - inset, a, z, b - a, '-x', rows=rows, frame=frame, **kw)


def vdisk(cx, cy, cz, r, t, axis='y', m='tile', segs=24):
    """A disk standing upright: its face looks along axis ('y' or 'x'); t is its thickness."""
    c = cx if axis == 'y' else cy
    pr = [(c + r * math.cos(2 * math.pi * k / segs), cz + r * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    if axis == 'y': return prism(pr, 'y', cy - t / 2, cy + t / 2, m, cap=m)
    return prism(pr, 'x', cx - t / 2, cx + t / 2, m, cap=m)


def rbox(cx, cy, z0, hx, hy, z1, ang, m, **kw):
    """A box of half-sizes hx, hy centred at (cx, cy), turned by ang."""
    return box(-hx, -hy, z0, hx, hy, z1, m, **kw).xform(ang, cx, cy)


def chair(R, x, y, face, frame='walnut', seat='leather', h=0.46, spot=True, arms=False):
    """A chair whose sitter faces `face` (radians, Blender xy)."""
    g = Geo()
    g.add(box(-0.22, -0.22, h - 0.06, 0.22, 0.22, h, frame, top=seat))
    for (a, b) in ((-0.21, -0.21), (0.17, -0.21), (-0.21, 0.17), (0.17, 0.17)):
        g.add(box(a, b, 0, a + 0.04, b + 0.04, h - 0.06, frame, skip=('-z', '+z')))
    g.add(box(-0.24, -0.21, h, -0.19, 0.21, h + 0.5, frame))
    if arms:
        for s in (-1, 1): g.add(box(-0.2, s * 0.22 - 0.03, h + 0.18, 0.2, s * 0.22 + 0.03, h + 0.24, frame))
    R.nocol.add(g.xform(face, x, y))
    R.col.add(box(-0.23, -0.23, 0, 0.23, 0.23, h, frame).xform(face, x, y))
    R.col.add(box(-0.25, -0.22, h, -0.18, 0.22, h + 0.5, frame).xform(face, x, y))
    if spot: R.spot('sit', x, y, h, face)


def armchair(R, x, y, face, m='velvet', frame='walnut'):
    g = Geo()
    g.add(box(-0.42, -0.42, 0, 0.42, 0.42, 0.44, m, skip=('-z',)))
    g.add(box(-0.42, -0.42, 0.44, -0.24, 0.42, 1.05, m))
    g.add(box(-0.24, -0.42, 0.44, 0.4, -0.28, 0.66, m))
    g.add(box(-0.24, 0.28, 0.44, 0.4, 0.42, 0.66, m))
    g.add(box(-0.44, -0.44, 0, 0.44, 0.44, 0.08, frame, skip=('-z',)))
    R.parts.add(g.xform(face, x, y))
    R.spot('sit', x, y, 0.44, face)


def candle(R, x, y, z, h=0.14, r=0.025, flame=0.035):
    R.nocol.add(cyl(x, y, z, z + h, r, 6, side='ivory', top='ivory', bottom='ivory', caps=False))
    R.light(cyl(x, y, z + h + 0.01, z + h + 0.01 + flame * 1.8, flame * 0.5, 4, side='e_candle', top='e_candle', bottom='e_candle'))


def candelabrum(R, x, y, h=1.5, m='iron', n=3):
    R.parts.add(cyl(x, y, 0, 0.05, 0.2, 10, side=m, top=m, bottom=m))
    R.parts.add(cyl(x, y, 0.05, h, 0.025, 5, side=m, caps=False))
    R.nocol.add(box(x - 0.28, y - 0.02, h - 0.02, x + 0.28, y + 0.02, h + 0.02, m))
    for k in range(n):
        cx = x + (k - (n - 1) / 2) * (0.5 / max(1, n - 1))
        R.nocol.add(cyl(cx, y, h + 0.02, h + 0.06, 0.04, 6, side=m, top=m, bottom=m))
        candle(R, cx, y, h + 0.06, h=0.18)


def pendant(R, x, y, z, top, r=0.18, m='brass', em='e_lamp'):
    """A hanging lamp: a cord from `top` down to a shade at z with a glowing disc under it."""
    R.nocol.add(cyl(x, y, z + 0.2, top, 0.012, 4, side='iron', caps=False))
    R.nocol.add(cyl(x, y, z + 0.05, z + 0.2, r, 12, side=m, top=m, bottom=m))
    R.light(cyl(x, y, z, z + 0.05, r * 0.8, 12, side=em, top=em, bottom=em))


def table_lamp(R, x, y, z, shade='green', r=0.16):
    R.nocol.add(cyl(x, y, z, z + 0.03, 0.08, 8, side='brass', top='brass', bottom='brass'))
    R.nocol.add(cyl(x, y, z + 0.03, z + 0.36, 0.015, 4, side='brass', caps=False))
    R.nocol.add(cyl(x, y, z + 0.36, z + 0.46, r, 12, side=shade, top=shade, bottom=shade))
    R.light(cyl(x, y, z + 0.33, z + 0.36, r * 0.8, 12, side='e_lamp', top='e_lamp', bottom='e_lamp'))


def round_table(R, x, y, r=0.45, h=0.74, m='walnut', top=None):
    R.parts.add(cyl(x, y, h - 0.04, h, r, 20, side=m, top=top or m, bottom=m))
    R.parts.add(cyl(x, y, 0.03, h - 0.04, 0.05, 8, side=m, caps=False))
    R.parts.add(cyl(x, y, 0, 0.03, 0.24, 12, side=m, top=m, bottom=m))


def bench(R, x0, y0, x1, y1, m='walnut', h=0.45, spots=True):
    R.parts.add(box(x0, y0, h - 0.06, x1, y1, h, m))
    for (a, b) in ((x0 + 0.05, y0 + 0.05), (x1 - 0.13, y0 + 0.05), (x0 + 0.05, y1 - 0.13), (x1 - 0.13, y1 - 0.13)):
        R.parts.add(box(a, b, 0, a + 0.08, b + 0.08, h - 0.06, m, skip=('-z',)))
    if spots:
        if x1 - x0 > y1 - y0:
            n = max(1, int((x1 - x0) / 0.8))
            for k in range(n):
                R.spot('sit', x0 + (k + 0.5) * (x1 - x0) / n, (y0 + y1) / 2, h, math.pi / 2)
        else:
            n = max(1, int((y1 - y0) / 0.8))
            for k in range(n):
                R.spot('sit', (x0 + x1) / 2, y0 + (k + 0.5) * (y1 - y0) / n, h, 0.0)


def loop(R, pts, close=True):
    ids = [R.navpt(x, y) for (x, y) in pts]
    R.link(*(ids + ([ids[0]] if close else [])))
    return ids


def outer_loop(R, d=2.0):
    return loop(R, [(d, d), (8, d), (C - d, d), (C - d, 8), (C - d, C - d), (8, C - d), (d, C - d), (d, 8)])


def door_tunnel(R, side, depth, floor='floor', wall='tile', w=DW, jamb=DJ):
    """Carry the doorway on `side` through a wall thickened to `depth` from the room's boundary."""
    pr = arch_profile(0, w, 0, jamb, 18)
    m = arch_mats(len(pr), floor, wall)
    if side == 'S': R.cut(prism([(p + 8, q) for p, q in pr], 'y', -0.1, depth + 0.05, m))
    if side == 'N': R.cut(prism([(p + 8, q) for p, q in pr], 'y', C - depth - 0.05, C + 0.1, m))
    if side == 'W': R.cut(prism([(p + 8, q) for p, q in pr], 'x', -0.1, depth + 0.05, m))
    if side == 'E': R.cut(prism([(p + 8, q) for p, q in pr], 'x', C - depth - 0.05, C + 0.1, m))


def palm(R, x, y, z=0.0, h=2.6, pot='brass', n=9, seed=0.0):
    """A potted palm made of cylinders and flat fronds."""
    R.parts.add(cyl(x, y, z, z + 0.55, 0.32, 16, side=pot, top='slate', bottom=pot))
    R.nocol.add(cyl(x, y, z + 0.55, z + 0.56, 0.3, 16, side='books', top='books', caps=True))
    segs = 6
    for k in range(segs):
        z0 = z + 0.55 + k * (h - 0.55) / segs
        R.parts.add(cyl(x + 0.02 * math.sin(k + seed), y, z0, z0 + (h - 0.55) / segs + 0.02, 0.09 - 0.008 * k, 8, side='wood' if k % 2 else 'oak', caps=False))
    for k in range(n):
        a = k * 2 * math.pi / n + seed
        L = 1.0 + 0.35 * math.sin(k * 2.3 + seed)
        zz = z + h - 0.05 * (k % 3)
        g = Geo()
        g.add(box(0.0, -0.1, 0, L * 0.5, 0.1, 0.03, 'green'))
        g.add(box(L * 0.45, -0.14, -0.12, L, 0.14, -0.09, 'green'))
        g.add(box(L * 0.9, -0.08, -0.3, L * 1.2, 0.08, -0.27, 'green'))
        R.nocol.add(g.xform(a, x, y, zz))


def quad(a0, a1, w, z0, z1, m, facing):
    """A single upright quad: facing '+y'/'-y' spans x a0..a1 at y=w; facing '+x'/'-x' spans y a0..a1 at x=w."""
    g = Geo()
    if facing[1] == 'y':
        P = [(a0, w, z0), (a1, w, z0), (a1, w, z1), (a0, w, z1)]
    else:
        P = [(w, a1, z0), (w, a0, z0), (w, a0, z1), (w, a1, z1)]
    ids = [g.vert(p) for p in P]
    uv = [(a0, z0), (a1, z0), (a1, z1), (a0, z1)]
    if facing in ('+y', '+x'): ids = ids[::-1]; uv = uv[::-1]
    g.face(ids, m, uv)
    return g


def bulb(R, x, y, z, r, m='e_lamp', segs=6):
    """A small glowing lamp: a short cylinder, cheaper than a sphere."""
    R.light(cyl(x, y, z - r, z + r, r, segs, side=m, top=m, bottom=m))
