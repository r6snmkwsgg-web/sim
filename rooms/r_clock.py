"""The Clock Room: one enormous clock face fills the north wall, lit round its rim. The door has
eaten the bottom of it: there is no five, six or seven. A pendulum case stands against the west wall."""
from lib import *
from kit_a import *

H = TOP - 0.1
YN = 14.9                 # north wall thickened for the face's recess
CX, CZ, RF = 8.0, 3.95, 3.45


def in_door(x, z, pad=0.25):
    return abs(x - 8.0) < DW / 2 + pad and z < DJ + DR + pad


def numeral(R, k, cx, cz, y, s=0.42):
    """Roman numeral k (1..12) as strokes, centred at (cx, cz), s tall, drawn on the plane y (facing -y)."""
    marks = {1: 'I', 2: 'II', 3: 'III', 4: 'IIII', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}[k]
    w = {'I': 0.1, 'V': 0.3, 'X': 0.3}
    tot = sum(w[c] for c in marks) * s + 0.04 * s * (len(marks) - 1)
    x = cx - tot / 2
    t = 0.06 * s / 0.42
    for c in marks:
        cw = w[c] * s
        if c == 'I':
            R.nocol.add(xz_plate(quad_poly(x + cw / 2, cz - s / 2, s, t * 1.4, math.pi / 2), y - 0.02, y, 'black'))
        elif c == 'V':
            a = math.atan2(s, cw / 2)
            R.nocol.add(xz_plate(quad_poly(x + cw / 2, cz - s / 2, math.hypot(s, cw / 2), t, math.pi - a), y - 0.02, y, 'black'))
            R.nocol.add(xz_plate(quad_poly(x + cw / 2, cz - s / 2, math.hypot(s, cw / 2), t, a), y - 0.02, y, 'black'))
        else:
            a = math.atan2(s, cw)
            R.nocol.add(xz_plate(quad_poly(x, cz - s / 2, math.hypot(s, cw), t, a), y - 0.02, y, 'black'))
            R.nocol.add(xz_plate(quad_poly(x + cw, cz - s / 2, math.hypot(s, cw), t, math.pi - a), y - 0.02, y, 'black'))
        x += cw + 0.04 * s


def make():
    R = Room('clock', 1, 1, res=1024)
    shell(R, y1=YN, wall='tile', floor='terrazzo', ceil='plaster', h=H)
    yb = YN + 0.45         # the face, recessed into the wall
    R.cut(xz_plate(circle_pts(CX, CZ, RF, 48), YN - 0.05, yb, 'ivory', cap='ivory'))
    # a bronze bezel round the recess and a lit ring inside it, both broken where the door bit through
    n = 60
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        am = (a0 + a1) / 2
        if in_door(CX + (RF + 0.1) * math.cos(am), CZ + (RF + 0.1) * math.sin(am), 0.05): continue
        pts = [(CX + r * math.cos(a), CZ + r * math.sin(a)) for (r, a) in ((RF + 0.3, a0), (RF + 0.3, a1), (RF - 0.02, a1), (RF - 0.02, a0))]
        R.parts.add(xz_plate(pts, YN - 0.12, YN + 0.02, 'bronze'))
        pts = [(CX + r * math.cos(a), CZ + r * math.sin(a)) for (r, a) in ((RF - 0.05, a0), (RF - 0.05, a1), (RF - 0.2, a1), (RF - 0.2, a0))]
        R.light(xz_plate(pts, yb - 0.04, yb - 0.02, 'e_panel'))
        # minute marks
        rm = RF - 0.32
        L = 0.24 if k % 5 == 0 else 0.1
        R.nocol.add(xz_plate(quad_poly(CX + (rm - L) * math.cos(a0), CZ + (rm - L) * math.sin(a0), L, 0.06 if k % 5 == 0 else 0.025, a0), yb - 0.03, yb - 0.01, 'black'))
    # numerals (the door has had five, six and seven)
    for k in range(1, 13):
        a = math.pi / 2 - k * math.pi / 6
        x, z = CX + (RF - 0.95) * math.cos(a), CZ + (RF - 0.95) * math.sin(a)
        if in_door(x, z, 0.4): continue
        numeral(R, k, x, z, yb - 0.01)
    # the hands: three minutes to eleven, always
    for (frac, L, w, tail) in ((10.95 / 12, RF * 0.6, 0.16, 0.5), (57 / 60, RF * 0.9, 0.09, 0.7)):
        a = math.pi / 2 - 2 * math.pi * frac
        R.nocol.add(xz_plate(quad_poly(CX - math.cos(a) * tail, CZ - math.sin(a) * tail, L + tail, w, a), yb - 0.12, yb - 0.08, 'iron'))
        tip = (CX + math.cos(a) * L, CZ + math.sin(a) * L)
        R.nocol.add(xz_plate([(tip[0] + math.cos(a) * 0.3, tip[1] + math.sin(a) * 0.3), (tip[0] - math.sin(a) * w * 1.3, tip[1] + math.cos(a) * w * 1.3),
                              (tip[0] + math.sin(a) * w * 1.3, tip[1] - math.cos(a) * w * 1.3)], yb - 0.12, yb - 0.08, 'iron'))
    R.nocol.add(xz_plate(circle_pts(CX, CZ, 0.2, 16), yb - 0.16, yb - 0.06, 'brass'))
    # the pendulum case against the west wall: a tall walnut box, open-fronted, a brass bob swinging nowhere
    px, py, pw, pd, ph = T, 11.0, 1.3, 0.75, 6.4
    R.parts.add(box(px, py - pw / 2, 0, px + pd, py + pw / 2, 0.5, 'walnut', skip=('-z',)))
    R.parts.add(box(px, py - pw / 2, 0.5, px + 0.08, py + pw / 2, ph, 'walnut'))
    for s in (-1, 1):
        R.parts.add(box(px, py + s * pw / 2 - (0.1 if s > 0 else 0), 0.5, px + pd, py + s * pw / 2 + (0 if s > 0 else 0.1), ph, 'walnut'))
    R.parts.add(box(px, py - pw / 2 - 0.08, ph - 1.5, px + pd + 0.08, py + pw / 2 + 0.08, ph, 'walnut'))
    R.parts.add(box(px, py - pw / 2 - 0.12, ph, px + pd + 0.12, py + pw / 2 + 0.12, ph + 0.18, 'walnut'))
    R.nocol.add(yz_plate(circle_pts(py, ph - 0.75, 0.52, 32), px + pd + 0.08, px + pd + 0.1, 'ivory'))
    R.nocol.add(yz_plate(circle_pts(py, ph - 0.75, 0.56, 32), px + pd + 0.07, px + pd + 0.085, 'brass'))
    for (frac, L, w) in ((10.95 / 12, 0.3, 0.035), (57 / 60, 0.45, 0.02)):
        a = math.pi / 2 - 2 * math.pi * frac
        R.nocol.add(yz_plate(quad_poly(py, ph - 0.75, L, w, math.pi - a), px + pd + 0.1, px + pd + 0.12, 'iron'))
    rod_top, bob = ph - 1.6, 1.3
    ang = 0.12
    bx, bz = py + math.sin(ang) * (rod_top - bob), bob
    R.nocol.add(beam((px + 0.4, py, rod_top), (px + 0.4, bx, bz), 0.03, 'brass'))
    R.nocol.add(yz_plate(circle_pts(bx, bz, 0.3, 24), px + 0.33, px + 0.47, 'brass'))
    R.light(box(px + 0.1, py - pw / 2 + 0.12, ph - 1.62, px + 0.14, py + pw / 2 - 0.12, ph - 1.58, 'e_amber'))
    # books on the other walls
    for (f, bk, a, b) in (('+y', T, 0.6, 6.2), ('+y', T, 9.8, C - 0.6), ('-x', C - T, 0.6, 6.2), ('-x', C - T, 9.8, YN - 0.05),
                          ('+x', T, 0.6, 6.2), ('+x', T, py + pw / 2 + 0.15, YN - 0.05)):
        sh(R, f, bk, a, b, rows=12, frame='walnut')
    # benches to sit and watch it not move, and lamps
    for x in (5.2, 10.8):
        R.parts.add(box(x - 1.1, 8.9, 0, x + 1.1, 9.4, 0.45, 'walnut', top='velvet', skip=('-z',)))
        R.spot('sit', x, 9.15, 0.45, math.pi / 2)
    for (x, y, m) in ((4.0, 4.0, 'e_lamp'), (12.0, 4.0, 'e_lamp'), (3.0, 10.5, 'e_dim'), (13.0, 10.5, 'e_dim')):
        bulb(R, x, y, 3.6, r=0.12, m=m, top=H)
    for (x, y) in ((2.0, 2.0), (C - 2.0, 2.0)):
        R.parts.add(cyl(x, y, 0, 1.4, 0.02, 6, side='brass', caps=False))
        R.parts.add(cyl(x, y, 0, 0.03, 0.18, 12, side='brass', top='brass'))
        R.light(sphere(x, y, 1.5, 0.11, 10, 5, 'e_amber'))
    navloop(R, [(2.2, 3.4), (8, 2.2), (13.8, 3.4), (13.8, 8), (13.2, 12.8), (8, 12.8), (2.8, 12.8), (2.2, 8)])
    a = R.navpt(8, 7.0); R.link(1, a, 5); R.link(7, a, 3)
    R.spot('probe', 8, 8.0, 1.8)
    R.meta.update(label='The Clock Room', weight=5,
                  blurb='A clock the size of a wall, stopped at three minutes to eleven. The door has eaten five, six and seven. You wait for it to tick. It does not.')
    R.meta['box'] = [[T, 0, T], [C - T, H, YN]]
    return tidy(R)
