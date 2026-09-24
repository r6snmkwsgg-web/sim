"""The Lift Shaft: an open lift shaft through every floor, framed in an iron cage. On each floor a
landing, folding gates drawn shut, a dial above them whose needle never moves. No lift has ever come."""
from lib import *
from kit_e import *


def scissor_gate(R, x0, x1, y, z, h=2.2, pitch=0.34, m='iron'):
    """A closed folding gate across x0..x1 at y: diagonal lattice, top and bottom rails, pickets."""
    g = Geo()
    L = x1 - x0
    n = int(L / pitch)
    p = L / n
    for k in range(-n, n + 1):
        # two families of diagonals, clipped to the gate's rectangle
        for s in (1, -1):
            xa = x0 + k * p
            # line x = xa + s * (zz - z) * (L / h) * 0.25 ... keep it simple: slope of 1 horizontal per 1 vertical * 0.5
            pts = []
            for zz in (z + 0.1, z + h - 0.1):
                pts.append((xa + s * (zz - z - 0.1) * 0.5, zz))
            (xa_, za), (xb_, zb) = pts
            # clip to x0..x1
            def clip(xa_, za, xb_, zb):
                if xa_ > xb_: xa_, za, xb_, zb = xb_, zb, xa_, za
                if xb_ < x0 or xa_ > x1: return None
                if xa_ < x0: za = za + (zb - za) * (x0 - xa_) / (xb_ - xa_); xa_ = x0
                if xb_ > x1: zb = za + (zb - za) * (x1 - xa_) / (xb_ - xa_) if xb_ != xa_ else zb; xb_ = x1
                return xa_, za, xb_, zb
            c = clip(xa_, za, xb_, zb)
            if not c or c[2] - c[0] < 0.05: continue
            g.add(beam((c[0], y, c[1]), (c[2], y, c[3]), 0.025, 0.03, m))
    for zz in (z, z + 0.08, z + h - 0.08):
        g.add(box(x0, y - 0.03, zz, x1, y + 0.03, zz + 0.06, m))
    for k in range(n + 1):
        x = x0 + k * p
        g.add(box(x - 0.015, y - 0.02, z, x + 0.015, y + 0.02, z + h, m))
    R.nocol.add(g)
    R.col.add(box(x0, y - 0.06, z, x1, y + 0.06, z + h + 0.05, 'iron'))


def make():
    R = Room('liftshaft', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets(floor='terrazzo')
    cx = cy = C / 2
    s0, s1 = 6.0, 10.0                         # the shaft
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, TOP, 'damask', bottom='terrazzo', top='plaster'))
    R.cut(box(s0, s0, -LH, s1, s1, 2 * LH, 'tile'))
    # the cage: corner posts through every floor, girders at each floor, cross-bracing above the gates
    pw = 0.16
    for (x, y) in ((s0, s0), (s1, s0), (s0, s1), (s1, s1)):
        R.parts.add(box(x - pw, y - pw, -0.4, x + pw, y + pw, 7.6, 'iron'))
    for (x, y) in ((s0, cy), (s1, cy)):
        R.parts.add(box(x - 0.08, y - 0.08, -0.4, x + 0.08, y + 0.08, 7.6, 'iron'))
    for z in (-0.4, 2.35, 7.25):
        hz = 0.4 if z == -0.4 else 0.25
        for (x0, y0, x1, y1) in ((s0 - 0.12, s0 - 0.12, s1 + 0.12, s0 + 0.02), (s0 - 0.12, s1 - 0.02, s1 + 0.12, s1 + 0.12),
                                 (s0 - 0.12, s0, s0 + 0.02, s1), (s1 - 0.02, s0, s1 + 0.12, s1)):
            R.parts.add(box(x0, y0, z, x1, y1, z + hz, 'iron'))
    for (a, b, fixed, axis) in ((s0, s1, s0 - 0.05, 'x'), (s0, s1, s1 + 0.05, 'x'), (s0, cy, s0 - 0.05, 'y'), (cy, s1, s0 - 0.05, 'y'),
                                (s0, cy, s1 + 0.05, 'y'), (cy, s1, s1 + 0.05, 'y')):
        for (za, zb) in ((2.6, 7.25),):
            for (p, q) in (((a, za), (b, zb)), ((a, zb), (b, za))):
                if axis == 'x': R.parts.add(beam((p[0], fixed, p[1]), (q[0], fixed, q[1]), 0.04, 0.05, 'iron'))
                else:           R.parts.add(beam((fixed, p[0], p[1]), (fixed, q[0], q[1]), 0.04, 0.05, 'iron'))
    # the gates (south and north), drawn shut; the lattice sides (east and west)
    scissor_gate(R, s0 + 0.16, s1 - 0.16, s0 - 0.06, 0.0)
    scissor_gate(R, s0 + 0.16, s1 - 0.16, s1 + 0.06, 0.0)
    for x in (s0 - 0.06, s1 + 0.06):
        g = Geo()
        for k in range(1, 16):
            y = s0 + k * (s1 - s0) / 16
            g.add(box(x - 0.015, y - 0.015, 0, x + 0.015, y + 0.015, 2.35, 'iron'))
        for zz in (0.0, 1.05):
            g.add(box(x - 0.03, s0, zz, x + 0.03, s1, zz + 0.05, 'brass' if zz > 0.5 else 'iron'))
        R.nocol.add(g)
        R.col.add(box(x - 0.06, s0, 0, x + 0.06, s1, 2.4, 'iron'))
    # guide rails and cables down the shaft
    for x in (s0 + 0.25, s1 - 0.25):
        R.parts.add(box(x - 0.05, cy - 0.06, -0.4, x + 0.05, cy + 0.06, 7.6, 'iron'))
    for (x, y) in ((cx - 0.3, cy + 0.2), (cx + 0.3, cy + 0.2), (cx, cy - 0.25)):
        R.nocol.add(cyl(x, y, -0.4, 7.6, 0.02, 6, side='iron', caps=False))
    # the floor dial above each gate, its needle stuck; a call button that glows
    for (y, s) in ((s0 - 0.12, -1), (s1 + 0.12, 1)):
        prof = [(cx + 0.55 * math.cos(math.pi * k / 16), 2.75 + 0.55 * math.sin(math.pi * k / 16)) for k in range(17)]
        R.parts.add(prism(prof, 'y', min(y, y + s * 0.05), max(y, y + s * 0.05), 'brass', cap='brass'))
        R.light(prism([(cx + 0.45 * math.cos(math.pi * k / 16), 2.8 + 0.45 * math.sin(math.pi * k / 16)) for k in range(17)], 'y',
                      min(y + s * 0.05, y + s * 0.06), max(y + s * 0.05, y + s * 0.06), 'e_amber', cap='e_amber'))
        R.parts.add(beam((cx, y + s * 0.07, 2.8), (cx - 0.3, y + s * 0.07, 3.1), 0.02, 0.025, 'black'))
        yp = (s0 - pw) if s < 0 else (s1 + pw)
        R.parts.add(box(s1 - 0.1, min(yp, yp + s * 0.04), 1.1, s1 + 0.1, max(yp, yp + s * 0.04), 1.5, 'brass'))
        R.light(cyl(s1, yp + s * 0.05, 1.27, 1.33, 0.035, 10, side='e_red', top='e_red', bottom='e_red'))
    # lamps down the shaft on the posts, so you can see the floors going down
    for (x, y) in ((s0 + 0.25, s0 + 0.25), (s1 - 0.25, s1 - 0.25)):
        R.light(sphere(x, y, 5.2, 0.12, 10, 6, 'e_dim'))
    # the landing: tall books all round, benches facing the gates, ceiling lamps
    wall_shelves(R, rows=9, frame='walnut', segs_x=CELL_SEGS, segs_y=CELL_SEGS)
    for y, f in ((3.2, math.pi / 2), (C - 3.2, -math.pi / 2)):
        for (x0, x1) in ((2.4, 4.6), (11.4, 13.6)):
            bench(R, x0, y - 0.25, x1, y + 0.25, m='walnut', seat='velvet', spots=False)
            for x in (x0 + 0.55, x1 - 0.55):
                R.spot('sit', x, y, 0.45, f)
    for (x, y) in ((3.2, 3.2), (C - 3.2, 3.2), (3.2, C - 3.2), (C - 3.2, C - 3.2)):
        pendant(R, x, y, 3.6, TOP, r=0.34)
    for (x, y) in ((cx, 2.6), (cx, C - 2.6), (2.6, cy), (C - 2.6, cy)):
        R.light(cyl(x, y, TOP - 0.05, TOP - 0.02, 0.5, 20, side='e_panel', top='e_panel', bottom='e_panel'))
    # walkers
    g = 2.2
    pts = loop(R, [(g, g), (cx, g), (C - g, g), (C - g, cy), (C - g, C - g), (cx, C - g), (g, C - g), (g, cy)])
    for (x, y, f) in ((cx, s0 - 0.7, math.pi / 2), (cx, s1 + 0.7, -math.pi / 2), (s0 - 0.7, cy, 0), (s1 + 0.7, cy, math.pi)):
        R.spot('edge', x, y, 0, f)
    R.spot('probe', 2.6, 8.0, 1.7)
    R.meta.update(label='The Lift Shaft', weight=35,
                  blurb='An iron cage round an empty shaft, and a gate drawn shut. Above it a dial shows which floor the lift is on. The needle has not moved in living memory, and nobody here is living.')
    R.meta['shaft'] = [s0, s0, s1, s1]
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]
    return R
