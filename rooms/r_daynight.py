"""Noon and Midnight: a long vaulted reading hall cut in two by a brass line in the floor. West of it,
noon: sun in every window. East of it, midnight: stars in the same windows, candles on the desks. On the
line, one bookcase that belongs to neither."""
from kit_h5 import *

W, D = 2 * C, C
XL = 16.0                     # the line
YS, YN = 3.6, D - T           # the hall; the dusk room hides in the thick south wall
YC = (YS + YN) / 2
JAMB, RISE = 5.4, 2.0         # the vault
GZ = 4.45                     # the gallery ledge
WZ0, WZ1 = 4.75, 6.4          # the windows (above the gallery)
DX0, DX1 = 12.6, 19.4         # the dusk room
DY0, DY1 = 0.6, 3.2
DZ = 3.2
FW = 1.5                      # the false bookcase, centred on the line


def make():
    R = Room('daynight', 2, 1, res=2048)
    rng = random.Random(41)
    R.sockets(floor='terrazzo', wall='tile')
    pr = arch_profile(YC, YN - YS, 0, JAMB, 24, rise=RISE)
    # noon in pale stone and cream marble; midnight the same hall in dark slate, so no light carries
    mats = ['terrazzo'] + ['tile'] * 2 + ['plaster'] * (len(pr) - 4) + ['tile']
    R.cut(prism(pr, 'x', T - 0.02, XL, mats, cap='tile'))
    mats = ['slate'] + ['slate'] * (len(pr) - 1)
    R.cut(prism(pr, 'x', XL, W - T + 0.02, mats, cap='slate'))
    dp = arch_profile(0, DW, 0, DJ)
    for x in (8.0, 24.0):
        f, w = ('terrazzo', 'tile') if x < XL else ('slate', 'slate')
        R.cut(prism([(p + x, q) for p, q in dp], 'y', T, YS + 0.05, arch_mats(len(dp), f, w)))
    # transverse ribs across the vault every four metres, the one on the line gilded
    for k in range(1, 8):
        x = k * 4.0
        m = 'gilt' if abs(x - XL) < 0.1 else ('tile' if x < XL else 'slate')
        n = 12
        pts = []
        for j in range(n + 1):
            t = j / n
            y = YS + (YN - YS) * t
            c = (YN - YS) / 2
            Rr = (c * c + RISE * RISE) / (2 * RISE)
            z = JAMB + RISE - Rr + math.sqrt(max(0.0, Rr * Rr - (y - YC) ** 2))
            pts.append((x, y, z - 0.12))
        for p, q in zip(pts, pts[1:]):
            R.nocol.add(beam(p, q, 0.34, m, 0.24))
    # the brass meridian in the floor
    R.nocol.add(box(XL - 0.035, YS, 0, XL + 0.035, YN, 0.008, 'brass'))
    for k in range(9):
        y = YS + 0.6 + k * (YN - YS - 1.2) / 8
        R.nocol.add(box(XL - 0.12, y - 0.012, 0, XL + 0.12, y + 0.012, 0.008, 'brass'))
    windows(R, rng)
    gallery(R, rng)
    # bookcases under the gallery, both walls, between the doors
    rows = 9
    for (a, b) in ((0.7, 6.2), (9.8, 22.2), (25.8, 31.3)):
        sh(R, '-y', YN, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.7, 6.2), (9.8, XL - FW / 2 - 0.05), (XL + FW / 2 + 0.05, 22.2), (25.8, 31.3)):
        sh(R, '+y', YS, a, b, rows=rows, frame='walnut')
    shelf(R, XL - FW / 2, YS, 0, FW, '+y', rows=rows, frame='walnut', solid=False)
    R.cut(box(XL - FW / 2 + 0.08, DY1 - 0.1, 0, XL + FW / 2 - 0.08, YS + 0.05, 2.25, 'tile', bottom='terrazzo'))
    # reading tables down the hall; lamps unlit at noon, lit with candle-light at midnight
    for x in (4.1, 8.8, 13.2, 18.8, 23.2, 27.9):
        for y in (YC - 2.4, YC + 2.4):
            R.parts.add(table(x - 1.3, y - 0.5, x + 1.3, y + 0.5, 0.78, 'walnut', top='leather'))
            for dx in (-0.65, 0.65):
                if x > XL: desk_lamp(R, x + dx, y, 0.78, m='e_candle')
                else: unlit_lamp(R, x + dx, y, 0.78)
                for s in (-1, 1):
                    R.parts.add(chair(x + dx, y + s * 0.85, -s * math.pi / 2))
                    R.spot('sit', x + dx, y + s * 0.85, 0.48, -s * math.pi / 2)
            if x > XL:
                for k in range(2):
                    candle(R, x + rng.uniform(-1.0, 1.0), y + rng.uniform(-0.3, 0.3), 0.78, h=rng.uniform(0.08, 0.2))
    dusk(R, rng)
    navloop(R, [(2.2, 8), (6, YC), (XL - 1.0, YC), (XL + 1.0, YC), (26, YC), (29.8, 8)], close=False)
    a = R.navpt(8, YS + 0.9); b = R.navpt(24, YS + 0.9); c = R.navpt(8, YN - 0.9); d = R.navpt(24, YN - 0.9)
    R.link(a, 1, c); R.link(b, 4, d)
    R.spot('probe', XL, YC, 2.4)
    R.meta.update(label='Noon and Midnight', weight=3,
                  blurb='At one end of the hall it is noon. At the other it is midnight, and has been for as long as anyone remembers. The line between them is brass, and nobody reads on it.')
    R.meta['box'] = [[T, 0, YS], [W - T, JAMB + RISE, YN]]
    fx(R, 'dust', [T, 0, YS, XL, JAMB + RISE, YN])
    return tidy(R)


def unlit_lamp(R, x, y, z):
    R.parts.add(cyl(x, y, z, z + 0.03, 0.08, 12, side='brass', top='brass'))
    R.parts.add(cyl(x, y, z + 0.03, z + 0.36, 0.012, 6, side='brass', caps=False))
    R.parts.add(obox(x - 0.17, y, x + 0.17, y, z + 0.36, z + 0.44, 0.13, 'green'))


def windows(R, rng):
    """Arched windows above the gallery on both walls: sky on the noon side, stars on the midnight side."""
    wp = arch_profile(0, 1.9, WZ0, WZ1 - WZ0 - 0.95, 12)
    for k in range(8):
        x = 2.0 + k * 4.0
        if abs(x - XL) < 3.0: continue
        noon = x < XL
        for (y0, y1, yb) in ((YN - 0.05, YN + 0.3, YN + 0.27), (YS - 0.3, YS + 0.05, YS - 0.27)):
            R.cut(prism([(p + x, q) for p, q in wp], 'y', y0, y1, 'tile', cap='tile'))
            pane = prism([(p + x, q) for p, q in wp], 'y', yb - 0.02, yb + 0.02, 'e_sky' if noon else 'black', cap='e_sky' if noon else 'black')
            if noon: R.light(pane)
            else: R.parts.add(pane)
            yf = yb - 0.05 if yb > YC else yb + 0.05
            for dx in (-0.32, 0.32):
                R.nocol.add(box(x + dx - 0.025, yf - 0.02, WZ0, x + dx + 0.025, yf + 0.02, WZ1 + 0.9, 'iron'))
            for z in (5.3, 5.9):
                R.nocol.add(box(x - 0.95, yf - 0.02, z - 0.02, x + 0.95, yf + 0.02, z + 0.02, 'iron'))
            if not noon:
                ys = yb - 0.04 if yb > YC else yb + 0.04
                for j in range(26):
                    sx = x + rng.uniform(-0.85, 0.85); sz = rng.uniform(WZ0 + 0.1, WZ1 + 0.5)
                    if (sz > WZ1 - 0.05) and abs(sx - x) > math.sqrt(max(0, 0.95 ** 2 - (sz - (WZ1 - 0.05)) ** 2)) - 0.08: continue
                    s = rng.choice((0.012, 0.018, 0.025))
                    R.light(box(sx - s, ys - 0.005, sz - s, sx + s, ys + 0.005, sz + s, 'e_kiosk'))
                if k == 6 and yb > YC:   # a moon, in one window
                    R.light(disc_v(x + 0.35, ys - 0.01, 6.0, 0.2, -math.pi / 2, 16, 'e_kiosk'))
                    R.nocol.add(disc_v(x + 0.44, ys - 0.02, 6.03, 0.19, -math.pi / 2, 16, 'black'))


def gallery(R, rng):
    """A ledge along both walls under the windows, balustraded, with busts looking down. Nobody goes up."""
    for (y0, y1, yr) in ((YN - 0.9, YN, YN - 0.85), (YS, YS + 0.9, YS + 0.85)):
        R.parts.add(box(T, y0, GZ - 0.25, W - T, y1, GZ, 'walnut', top='oak'))
        rail(R, T, yr, W - T, yr, GZ, h=0.9, post=0.6)
        for k in range(8):
            x = 2.0 + k * 4.0 + 2.0
            if x > W - 1: continue
            yb = (y0 + y1) / 2
            R.nocol.add(box(x - 0.2, yb - 0.2, GZ, x + 0.2, yb + 0.2, GZ + 0.9, 'tile'))
            R.nocol.add(blob(x, yb, GZ + 1.12, 0.24, 0.2, 0.26, 10, 5, 'ivory'))
            R.nocol.add(blob(x, yb, GZ + 1.35, 0.13, 0.15, 0.18, 10, 5, 'ivory'))
            if x > XL:
                R.light(sphere(x + 0.45, yb, GZ + 0.12, 0.07, 8, 4, 'e_amber'))
    # brackets under the ledges
    for k in range(16):
        x = 1.0 + k * 2.0
        for (y0, y1) in ((YN - 0.7, YN), (YS, YS + 0.7)):
            R.nocol.add(box(x - 0.08, y0, GZ - 0.7, x + 0.08, y1, GZ - 0.25, 'walnut'))


def dusk(R, rng):
    """Behind the bookcase on the line: a narrow room where it is always a quarter past sunset."""
    R.cut(box(DX0, DY0, 0, DX1, DY1, DZ, 'damask', bottom='carpet', top='plaster'))
    # the window: a long low horizon, orange at the bottom, going to blue
    wx0, wx1 = DX0 + 0.6, DX1 - 0.6
    R.cut(box(wx0, DY0 - 0.2, 0.8, wx1, DY0 + 0.05, 2.9, 'tile'))
    R.light(box(wx0, DY0 - 0.2, 0.8, wx1, DY0 - 0.16, 1.15, 'e_amber'))
    R.light(box(wx0, DY0 - 0.2, 1.15, wx1, DY0 - 0.16, 1.4, 'e_red'))
    R.light(box(wx0, DY0 - 0.2, 1.4, wx1, DY0 - 0.16, 1.7, 'e_blue'))
    R.parts.add(box(wx0, DY0 - 0.21, 1.7, wx1, DY0 - 0.2, 2.9, 'black'))
    for j in range(14):
        sx = rng.uniform(wx0 + 0.1, wx1 - 0.1); sz = rng.uniform(2.0, 2.85)
        R.light(box(sx - 0.012, DY0 - 0.2, sz - 0.012, sx + 0.012, DY0 - 0.19, sz + 0.012, 'e_kiosk'))
    for k in range(5):   # a line of hills against the glow
        x0 = wx0 + (wx1 - wx0) * k / 5
        R.nocol.add(slope_box(x0, x0 + (wx1 - wx0) / 5, DY0 - 0.17, DY0 - 0.15, 0.8, 0.8, 0.95 + 0.12 * (k % 2), 1.0 + 0.1 * ((k + 1) % 3), 'black'))
    n = 8
    for k in range(n + 1):
        x = wx0 + (wx1 - wx0) * k / n
        R.nocol.add(box(x - 0.03, DY0 - 0.12, 0.8, x + 0.03, DY0 - 0.06, 2.9, 'walnut'))
    R.nocol.add(box(wx0, DY0 - 0.12, 2.1, wx1, DY0 - 0.06, 2.16, 'walnut'))
    R.parts.add(box(wx0 - 0.1, DY0, 0, wx1 + 0.1, DY0 + 0.3, 0.8, 'walnut', top='oak'))
    # a long sofa facing it, a low table, books at both ends
    R.parts.add(box(XL - 1.6, DY1 - 0.95, 0, XL + 1.6, DY1 - 0.15, 0.42, 'velvet', sides='walnut'))
    R.parts.add(box(XL - 1.6, DY1 - 0.3, 0.42, XL + 1.6, DY1 - 0.1, 0.95, 'velvet', sides='walnut'))
    for dx in (-0.8, 0.0, 0.8):
        R.spot('sit', XL + dx, DY1 - 0.6, 0.42, -math.pi / 2)
    R.parts.add(table(XL - 0.7, DY0 + 0.75, XL + 0.7, DY0 + 1.2, 0.45, 'walnut'))
    ob = open_book(0.18, 0.26, 0.2, 'oxblood'); orient(ob, 0.1, 0, 0, XL + 0.2, DY0 + 0.97, 0.47)
    R.nocol.add(ob)
    R.spot('plaque', XL + 0.2, DY0 + 0.97, 0.47)
    candle(R, XL - 0.45, DY0 + 0.97, 0.45, h=0.15)
    sh(R, '+x', DX0, DY0 + 0.2, DY1 - 0.1, rows=6, frame='walnut')
    sh(R, '-x', DX1, DY0 + 0.2, DY1 - 0.1, rows=6, frame='walnut')
    secret(R, XL, (DY0 + DY1) / 2, 0, 'The Dusk Room',
           'On the line there is a door, and behind it the sun has just gone down. It will not get any darker in here. It has promised.', r=1.6)
