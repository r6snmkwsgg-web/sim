"""The Chapel: a pointed stone vault over a nave of pews, side aisles behind an arcade, lancet
windows of coloured glass that look out on nothing, a lectern with one book, and candles."""
from lib import *
from kit_a import *

W0, W1 = 1.1, C - 1.1          # thick walls: room for window reveals
NX0, NX1 = 4.4, C - 4.4        # the nave between the arcades
AH = 3.4                       # aisle ceiling / arcade lintel


def lancet(R, axis, wall, face, c, z0, w, jamb, rise, depth=0.55, cols=('e_blue', 'e_red', 'e_green')):
    """A lancet window in a wall: a pointed niche with glass at the back, leaded into three colours.
    axis: 'x' for a window in a wall facing +-x (at x=wall), 'y' for a wall facing +-y."""
    pr = pointed_profile(c, w, z0, jamb, rise, 8)
    a0, a1 = (wall - depth, wall + 0.05) if face > 0 else (wall - 0.05, wall + depth)
    back = wall - depth if face > 0 else wall + depth
    R.cut(prism(pr, 'x' if axis == 'x' else 'y', a0, a1, 'tile', cap='tile'))
    g0, g1 = (back, back + 0.03) if face > 0 else (back - 0.03, back)
    # glass bands: bottom, middle, the pointed head
    zc = z0 + jamb
    ins = 0.07
    b1 = [(c - w / 2 + ins, z0 + ins), (c + w / 2 - ins, z0 + ins), (c + w / 2 - ins, z0 + jamb * 0.45), (c - w / 2 + ins, z0 + jamb * 0.45)]
    b2 = [(c - w / 2 + ins, z0 + jamb * 0.45 + 0.04), (c + w / 2 - ins, z0 + jamb * 0.45 + 0.04), (c + w / 2 - ins, zc), (c - w / 2 + ins, zc)]
    b3 = pointed_profile(c, w - 2 * ins, zc + 0.04, 0.001, rise - ins - 0.06, 8)
    for poly, m in zip((b1, b2, b3), cols):
        R.light(prism(poly, 'x' if axis == 'x' else 'y', g0, g1, m, cap=m))
    # lead cames: a mullion and bars across
    gi = (g1 + 0.012) if face > 0 else (g0 - 0.012)
    for zz in (z0 + jamb * 0.225, z0 + jamb * 0.45 + 0.02, zc + 0.02, zc + rise * 0.45):
        if axis == 'x': R.nocol.add(box(gi - 0.012, c - w / 2, zz - 0.015, gi + 0.012, c + w / 2, zz + 0.015, 'iron', skip=('-x' if face < 0 else '+x', '-y', '+y', '-z', '+z')))
        else: R.nocol.add(box(c - w / 2, gi - 0.012, zz - 0.015, c + w / 2, gi + 0.012, zz + 0.015, 'iron', skip=('-y' if face < 0 else '+y', '-x', '+x', '-z', '+z')))
    if axis == 'x': R.nocol.add(box(gi - 0.012, c - 0.015, z0, gi + 0.012, c + 0.015, zc + rise - 0.1, 'iron', skip=('-x' if face < 0 else '+x', '-z', '+z')))
    else: R.nocol.add(box(c - 0.015, gi - 0.012, z0, c + 0.015, gi + 0.012, zc + rise - 0.1, 'iron', skip=('-y' if face < 0 else '+y', '-z', '+z')))


def pew(R, x0, x1, y, books=True):
    """A pew facing +y: its back at y."""
    R.nocol.add(box(x0, y + 0.08, 0.4, x1, y + 0.5, 0.46, 'oak', sides='walnut'))
    R.nocol.add(box(x0, y, 0.0, x1, y + 0.08, 0.98, 'walnut', skip=('-z',)))
    for x in (x0, x1 - 0.06):
        R.nocol.add(box(x, y - 0.02, 0.0, x + 0.06, y + 0.52, 1.05, 'walnut', skip=('-z',)))
    R.col.add(box(x0, y - 0.02, 0, x1, y + 0.52, 0.46, 'tile'))
    R.col.add(box(x0, y - 0.02, 0.46, x1, y + 0.08, 1.05, 'tile'))
    if books:   # a rack of hymnals on the back, for whoever sits behind
        shelf(R, x1 - 0.1, y, 0.62, x1 - x0 - 0.2, '-y', rows=1, row_h=0.24, depth=0.13, frame='walnut', back=False, sides=False, crown=False, solid=False)


def make():
    R = Room('chapel', 1, 1, res=1024)
    shell(R, W0, W0, W1, W1, h=AH, wall='tile', floor='terrazzo', ceil='plaster')
    # the nave's pointed vault
    pr = pointed_profile(8, NX1 - NX0, 0, AH, 3.95, 20)
    R.cut(prism(pr, 'y', W0 - 0.02, W1 + 0.02, arch_mats(len(pr), 'terrazzo', 'tile')))
    # vault ribs: transverse pointed ribs above each pair of columns
    cols_y = [2.3, 4.55, 6.8, 9.2, 11.45, 13.7]
    for y in cols_y:
        outer = pointed_profile(8, NX1 - NX0 + 0.02, AH - 0.02, 0.02, 3.97, 12)
        inner = pointed_profile(8, NX1 - NX0 - 0.36, AH, 0.0, 3.62, 12)
        arcs_o = outer[2:]            # from right spring over the top to the left
        arcs_i = inner[2:]
        poly = arcs_o + list(reversed(arcs_i))
        R.nocol.add(prism(poly, 'y', y - 0.12, y + 0.12, 'tile', cap='tile'))
    # the arcade: columns carrying a stone lintel along each side of the nave
    for x in (NX0, NX1):
        R.parts.add(box(x - 0.3, W0, AH - 0.4, x + 0.3, W1, AH + 0.02, 'tile'))
        for y in cols_y:
            R.nocol.add(cyl(x, y, 0, AH - 0.4, 0.24, 12, side='tile', caps=False))
            R.col.add(box(x - 0.24, y - 0.24, 0, x + 0.24, y + 0.24, AH - 0.4, 'tile'))
            R.parts.add(box(x - 0.34, y - 0.34, AH - 0.62, x + 0.34, y + 0.34, AH - 0.4, 'tile', skip=('+z',)))
            R.parts.add(box(x - 0.32, y - 0.32, 0, x + 0.32, y + 0.32, 0.25, 'tile', skip=('-z',)))
    # lancet windows in both aisles, tall ones either side of each end door, a rose over the north door
    for y in (3.4, 5.7, 10.3, 12.6):
        lancet(R, 'x', W0, +1, y, 0.95, 0.72, 1.25, 0.95, cols=('e_blue', 'e_red', 'e_green'))
        lancet(R, 'x', W1, -1, y, 0.95, 0.72, 1.25, 0.95, cols=('e_red', 'e_blue', 'e_green'))
    for x in (5.55, 10.45):
        lancet(R, 'y', W1, -1, x, 1.2, 0.8, 3.0, 1.2, cols=('e_blue', 'e_red', 'e_blue'))
        lancet(R, 'y', W0, +1, x, 1.2, 0.8, 3.0, 1.2, cols=('e_red', 'e_blue', 'e_red'))
    rz, rr = 5.55, 1.05
    R.cut(xz_plate(circle_pts(8, rz, rr, 32), W1 - 0.05, W1 + 0.5, 'tile'))
    for k in range(8):
        a0, a1 = k * math.pi / 4, (k + 1) * math.pi / 4
        pts = [(8 + 0.34 * math.cos(a0 + (a1 - a0) * t / 4), rz + 0.34 * math.sin(a0 + (a1 - a0) * t / 4)) for t in range(5)]
        pts += [(8 + (rr - 0.06) * math.cos(a1 - (a1 - a0) * t / 4), rz + (rr - 0.06) * math.sin(a1 - (a1 - a0) * t / 4)) for t in range(5)]
        R.light(xz_plate(pts, W1 + 0.45, W1 + 0.48, 'e_red' if k % 2 else 'e_blue'))
        R.nocol.add(xz_plate(quad_poly(8, rz, rr, 0.04, a0), W1 + 0.42, W1 + 0.45, 'iron'))
    R.light(xz_plate(circle_pts(8, rz, 0.32, 16), W1 + 0.45, W1 + 0.48, 'e_green'))
    R.nocol.add(xz_plate(circle_pts(8, rz, 0.36, 16), W1 + 0.43, W1 + 0.45, 'iron'))
    # the dais, the lectern and its one book
    R.parts.add(box(5.6, 10.5, 0, 10.4, 12.7, 0.22, 'tile', top='carpet'))
    R.parts.add(box(7.7, 11.45, 0.22, 8.3, 11.85, 1.05, 'walnut'))
    lec = box(-0.36, -0.28, -0.03, 0.36, 0.28, 0.03, 'walnut')
    rot(lec, 'x', 0.35); lec.xform(0, 8, 11.6, 1.17)
    R.parts.add(lec)
    for s in (-1, 1):
        pg = box(0, -0.16, 0, 0.2, 0.16, 0.025, 'ivory')
        rot(pg, 'x', 0.35); pg.xform(0, 8 + (0.005 if s > 0 else -0.205), 11.6, 1.2)
        R.parts.add(pg)
    R.spot('read', 8, 11.1, 0.22, math.pi / 2)
    for (x, y) in ((6.0, 11.0), (10.0, 11.0), (6.0, 12.3), (10.0, 12.3)):
        candle(R, x, y, 0.22, h=0.35, r=0.04, stand=1.25)
    # a rack of votive candles in each aisle
    for (x, y) in ((2.0, 13.8), (C - 2.0, 13.8)):
        R.parts.add(box(x - 0.6, y - 0.2, 0, x + 0.6, y + 0.2, 0.8, 'iron'))
        for i in range(5):
            candle(R, x - 0.48 + i * 0.24, y + (0.08 if i % 2 else -0.08), 0.8, h=0.06 + 0.03 * (i % 3), r=0.025)
    # pews, with hymnals on their backs
    for k in range(7):
        y = 3.2 + k * 0.98
        pew(R, NX0 + 0.45, 7.35, y)
        pew(R, 8.65, NX1 - 0.45, y)
        R.spot('sit', 6.0, y + 0.3, 0.46, math.pi / 2)
    R.parts.add(box(7.45, W0, 0, 8.55, 10.5, 0.015, 'carpet'))
    # bookcases under the aisle windows and along the end walls of the aisles
    for y in (3.4, 5.7, 10.3, 12.6):
        sh(R, '+x', W0, y - 0.75, y + 0.75, rows=2, frame='walnut', crown=True)
        sh(R, '-x', W1, y - 0.75, y + 0.75, rows=2, frame='walnut')
    for (a, b) in ((W0 + 0.1, 4.0),):
        sh(R, '+y', W0, a, b, rows=7, frame='walnut')
        sh(R, '+y', W0, C - b, C - a, rows=7, frame='walnut')
        sh(R, '-y', W1, a, b - 0.6, rows=7, frame='walnut')
        sh(R, '-y', W1, C - b + 0.6, C - a, rows=7, frame='walnut')
    # iron candle-wheels hanging in the nave, lamps in the aisles
    for y in (4.2, 8.0, 11.8):
        R.nocol.add(ring(8, y, 4.3, 4.36, 0.82, 0.9, 16, top='iron', bottom='iron', inner='iron', outer='iron'))
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            R.nocol.add(beam((8 + 0.86 * math.cos(a), y + 0.86 * math.sin(a), 4.36), (8, y, 5.4), 0.015, 'iron'))
        R.nocol.add(cyl(8, y, 5.4, 7.3, 0.012, 6, side='iron', caps=False))
        for k in range(8):
            a = k * math.pi / 4
            x1, y1 = 8 + 0.86 * math.cos(a), y + 0.86 * math.sin(a)
            R.nocol.add(cyl(x1, y1, 4.36, 4.55, 0.035, 5, side='ivory', top='ivory'))
            R.light(box(x1 - 0.025, y1 - 0.025, 4.57, x1 + 0.025, y1 + 0.025, 4.66, 'e_candle'))
        R.light(sphere(8, y, 4.2, 0.13, 10, 5, 'e_lamp'))
    for y in (2.6, 7.0, 9.0, 13.4):
        for x in (2.75, C - 2.75):
            R.nocol.add(cyl(x, y, AH - 0.4, AH, 0.012, 6, side='iron', caps=False))
            R.light(sphere(x, y, AH - 0.5, 0.11, 8, 4, 'e_lamp'))
    navloop(R, [(2.7, 2.2), (8, 2.2), (C - 2.7, 2.2), (C - 2.7, 8), (C - 2.7, 12.4), (C - 2.7, 13.9), (8, 13.6), (2.7, 13.9), (2.7, 12.4), (2.7, 8)])
    a = R.navpt(8, 9.9); R.link(1, a, 6)
    R.spot('probe', 8, 7.0, 2.2)
    R.meta.update(label='The Chapel', weight=5,
                  blurb='The windows glow though there is nothing behind them. The book on the lectern is open at your page.')
    R.meta['box'] = [[W0, 0, W0], [W1, 7.35, W1]]
    return tidy(R)
