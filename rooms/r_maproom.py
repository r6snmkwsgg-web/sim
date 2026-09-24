"""The Map Room: a table the size of a room carries a relief of an imaginary country made of
bookcases, terraced like rice fields. Plan chests of shallow drawers, a great glowing globe."""
from lib import *
from kit_b import *


def terrain(x, y):
    h = (0.32 * math.sin(0.62 * x + 0.8) * math.cos(0.75 * y - 0.3) + 0.22 * math.sin(1.3 * x - 0.9 * y + 2.0)
         + 0.12 * math.cos(2.1 * x + 1.7 * y) + 0.08)
    d = math.hypot(x - 10.6, y - 9.6)
    h += 0.45 * math.exp(-d * d / 1.3)                  # the mountain
    return h


def make():
    R = Room('maproom', 1, 1, res=1024)
    H = 5.2
    shell(R, H, wall='damask', floor='terrazzo', ceil='walnut')
    # a deep coffer over the table
    R.cut(box(3.0, 4.0, H - 0.05, 13.0, 12.0, H + 0.6, 'green', top='plaster'))
    # dado and cornice
    for (x0, y0, x1, y1) in ((T, T, C - T, T + 0.05), (T, C - T - 0.05, C - T, C - T), (T, T, T + 0.05, C - T), (C - T - 0.05, T, C - T, C - T)):
        R.parts.add(box(x0, y0, H - 0.3, x1, y1, H, 'walnut'))
    # the table
    X0, Y0, X1, Y1, TZ = 3.6, 4.6, 12.4, 11.4, 0.92
    R.parts.add(box(X0 - 0.12, Y0 - 0.12, TZ - 0.1, X1 + 0.12, Y1 + 0.12, TZ, 'walnut', top='slate'))
    R.parts.add(box(X0 + 0.3, Y0 + 0.3, 0, X1 - 0.3, Y1 - 0.3, TZ - 0.1, 'walnut', skip=('-z',)))
    # the relief: terraces of stone, each carrying a tiny bookcase row
    s = 0.44
    nx, ny = int((X1 - X0) / s), int((Y1 - Y0) / s)
    ox, oy = X0 + ((X1 - X0) - nx * s) / 2, Y0 + ((Y1 - Y0) - ny * s) / 2
    for i in range(nx):
        for j in range(ny):
            x, y = ox + i * s, oy + j * s
            q = int(terrain(x, y) * 1.35 / 0.055)
            if q <= 0: continue
            top = TZ + q * 0.075
            R.nocol.add(box(x, y, TZ, x + s, y + s, top, 'books', top='tile', skip=('-z',)))
            if (i * 7 + j * 3) % 5 != 0:
                if (i // 2 + q) % 2: R.nocol.add(box(x + 0.06, y + 0.19, top, x + s - 0.06, y + 0.25, top + 0.09, 'walnut', skip=('-z',)))
                else: R.nocol.add(box(x + 0.19, y + 0.06, top, x + 0.25, y + s - 0.06, top + 0.09, 'walnut', skip=('-z',)))
    R.col.add(box(X0 - 0.12, Y0 - 0.12, TZ, X1 + 0.12, Y1 + 0.12, 2.2, 'tile'))
    # a pin: you are here
    R.parts.add(cyl(6.3, 7.1, TZ, TZ + 0.3, 0.008, 5, side='brass', caps=False))
    R.light(sphere(6.3, 7.1, TZ + 0.32, 0.035, 8, 4, 'e_red'))
    # the globe, hung over the mountain
    gx, gy, gz = 8.0, 8.0, 3.2
    R.light(sphere(gx, gy, gz, 0.5, 20, 10, 'e_fluor'))
    R.parts.add(ring(gx, gy, gz - 0.03, gz + 0.03, 0.54, 0.62, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.parts.add(cyl(gx, gy, gz + 0.5, H + 0.6, 0.02, 6, side='iron', caps=False))
    # plan chests along the walls, with shelves standing on them
    def chest(x0, y0, x1, y1, face):
        R.parts.add(box(x0, y0, 0, x1, y1, 1.0, 'oak', top='walnut', skip=('-z',)))
        for k in range(7):
            z = 0.1 + k * 0.125
            if face == '+y': R.nocol.add(box(x0 + 0.03, y1, z, x1 - 0.03, y1 + 0.015, z + 0.11, 'oak', skip=('-y', '-x', '+x')))
            if face == '-y': R.nocol.add(box(x0 + 0.03, y0 - 0.015, z, x1 - 0.03, y0, z + 0.11, 'oak', skip=('+y', '-x', '+x')))
            if face == '+x': R.nocol.add(box(x1, y0 + 0.03, z, x1 + 0.015, y1 - 0.03, z + 0.11, 'oak'))
            if face == '-x': R.nocol.add(box(x0 - 0.015, y0 + 0.03, z, x0, y1 - 0.03, z + 0.11, 'oak'))
            c = ((x0 + x1) / 2, (y0 + y1) / 2)
            if face[1] == 'y':
                yy = y1 + 0.015 if face == '+y' else y0 - 0.035
                for dx in (0.0,): R.nocol.add(box(c[0] + dx - 0.12, yy, z + 0.045, c[0] + dx + 0.12, yy + 0.02, z + 0.065, 'brass', skip=('-z', '+z')))
            else:
                xx = x1 + 0.015 if face == '+x' else x0 - 0.035
                for dy in (0.0,): R.nocol.add(box(xx, c[1] + dy - 0.12, z + 0.045, xx + 0.02, c[1] + dy + 0.12, z + 0.065, 'brass', skip=('-z', '+z')))
    for (a, b) in ((0.6, 6.1), (9.9, C - 0.6)):
        for k in range(3):
            w = (b - a) / 3
            chest(a + k * w + 0.03, T, a + (k + 1) * w - 0.03, T + 0.95, '+y')
            chest(a + k * w + 0.03, C - T - 0.95, a + (k + 1) * w - 0.03, C - T, '-y')
        bshelf(R, a, T, 1.0, b - a, '+y', rows=7, frame='walnut', depth=0.3)
        bshelf(R, b, C - T, 1.0, b - a, '-y', rows=7, frame='walnut', depth=0.3)
    # maps on the east and west walls: pale sheets in gilt frames
    for (a, b) in ((1.2, 5.6), (10.4, C - 1.2)):
        for side in (0, 1):
            x = T if side == 0 else C - T
            sg = 1 if side == 0 else -1
            R.parts.add(box(min(x, x + sg * 0.06), a, 1.2, max(x, x + sg * 0.06), b, 3.7, 'gilt'))
            R.parts.add(box(min(x, x + sg * 0.08), a + 0.12, 1.32, max(x, x + sg * 0.08), b - 0.12, 3.58, 'plaster'))
            # coastlines: a few dark strokes
            for k in range(14):
                yy = a + 0.45 + k * (b - a - 0.9) / 13
                zz = 2.3 + 0.7 * math.sin(k * 0.8 + side * 2) + 0.25 * math.sin(k * 2.3)
                R.nocol.add(box(min(x, x + sg * 0.09), yy - 0.18, zz, max(x, x + sg * 0.09), yy + 0.18, zz + 0.12, 'books', skip=('-z', '+z')))
                if k % 3 == 1: R.nocol.add(box(min(x, x + sg * 0.09), yy - 0.04, zz - 0.6, max(x, x + sg * 0.09), yy + 0.04, zz - 0.1, 'oxblood', skip=('-z', '+z')))
            R.light(box(min(x, x + sg * 0.25), a + 0.5, 3.9, max(x, x + sg * 0.25), b - 0.5, 3.96, 'e_fluor'))
            R.parts.add(box(min(x, x + sg * 0.28), a + 0.45, 3.96, max(x, x + sg * 0.28), b - 0.45, 4.02, 'brass'))
    # standing globe lamps in the corners of the table
    for (x, y) in ((X0 - 0.9, Y0 - 0.9), (X1 + 0.9, Y0 - 0.9), (X0 - 0.9, Y1 + 0.9), (X1 + 0.9, Y1 + 0.9)):
        R.parts.add(cyl(x, y, 0, 0.04, 0.22, 12, side='brass', top='brass', bottom='brass'))
        R.parts.add(cyl(x, y, 0.04, 1.55, 0.025, 6, side='brass', caps=False))
        R.light(sphere(x, y, 1.72, 0.16, 10, 5, 'e_dim'))
    # stools along the table
    for x in (5.0, 8.0, 11.0):
        for (y, f) in ((Y0 - 0.5, math.pi / 2), (Y1 + 0.5, -math.pi / 2)):
            R.parts.add(cyl(x, y, 0, 0.65, 0.2, 14, side='walnut', top='leather', bottom='walnut'))
            R.spot('sit', x, y, 0.65, f)
    loop(R, [(2.2, 2.2), (8, 2.2), (C - 2.2, 2.2), (C - 2.2, 8), (C - 2.2, C - 2.2), (8, C - 2.2), (2.2, C - 2.2), (2.2, 8)])
    R.spot('read', 8, Y0 - 0.6, 0, math.pi / 2)
    R.spot('probe', 8, 3.0, 1.7)
    R.meta.update(label='The Map Room', weight=5,
                  blurb='A map of the library, to scale, if the scale is generous. There is a pin in it. The pin is not where you are.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
