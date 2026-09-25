"""The Motel: a long low corridor of patterned carpet and numbered doors, a fluorescent panel every
few metres, the hum you can almost hear. Some doors stand open on the same room: a made bed, a green
lamp, one bookcase. In two of them, where the window should be, is a doorway into the library. Room
216 has no way in from the corridor at all; but the wardrobe in 212 has no back."""
from kit_h9 import *

W, D = 32.0, 16.0
CY0, CY1, CH = 6.5, 9.5, 3.0       # the corridor
RH = 2.8                           # the rooms' ceilings
RD = 5.75                          # a room's depth, back wall to corridor wall
MODS = (4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0)
OPEN = {('S', 8.0): 'door', ('S', 24.0): 'door', ('N', 8.0): 'door', ('N', 24.0): 'door',
        ('S', 16.0): 'mirror', ('N', 12.0): 'closet', ('N', 16.0): 'hidden', ('S', 28.0): 'plain'}


def num(side, c):
    return (100 if side == 'S' else 200) + int(c)


def make():
    R = Room('motel', 2, 1, res=2048)
    R.sockets(floor='damask', wall='ivory', rect=2.6)
    corridor(R)
    for side in 'SN':
        for c in MODS:
            kind = OPEN.get((side, c))
            if kind: room(R, side, c, kind)
            else: shut_door(R, side, c)
    secret(R, 16.0, 12.6, 0.0, 'Room 216',
           'A room with no door. The bed has been slept in, the lamp is on, and every wall is books to the ceiling. The television is showing the corridor outside, empty, from above.')
    ids = navloop(R, [(1.6, 8.0), (8.0, 7.6), (16.0, 8.4), (24.0, 7.6), (30.4, 8.0)], close=False)
    for (c, sd) in ((8.0, 'S'), (24.0, 'S'), (8.0, 'N'), (24.0, 'N')):
        p = [R.navpt(*to_xy(sd, c, u, v)) for (u, v) in ((-0.8, 4.9), (0.9, 4.2), (0.9, 1.5))]
        R.link(ids[1 if c < 16 else 3], *p)
    return finish(R, 'The Motel', weight=3, probe=(16, 8, 1.6), top=CH,
                  blurb='A motel corridor, carpeted, lit, very long. Every door has a number and every room behind them is the same room. There is no desk, no car park, no road.')


# ---------------------------------------------------------------------------
def corridor(R):
    R.cut(box(T - 0.02, CY0, 0, W - T + 0.02, CY1, CH, 'ivory', bottom='damask', top='plaster'))
    # a patterned border down each side of the carpet
    for (a, b) in ((CY0, CY0 + 0.25), (CY1 - 0.25, CY1)):
        R.nocol.add(box(T, a, 0, W - T, b, 0.006, 'oxblood'))
    R.nocol.add(box(T, CY0 + 0.3, 0, W - T, CY0 + 0.34, 0.007, 'gilt'))
    R.nocol.add(box(T, CY1 - 0.34, 0, W - T, CY1 - 0.3, 0.007, 'gilt'))
    # a dado of dark wood, a picture rail, a cornice
    for (y0, y1) in ((CY0, CY0 + 0.03), (CY1 - 0.03, CY1)):
        R.nocol.add(box(T, y0, 0.0, W - T, y1, 1.0, 'walnut'))
        R.nocol.add(box(T, y0 - 0.005, 1.0, W - T, y1 + 0.005, 1.05, 'oak'))
        R.nocol.add(box(T, y0 - 0.01, CH - 0.15, W - T, y1 + 0.01, CH, 'ivory'))
    # fluorescent panels, and green lamps between the doors
    for k in range(8):
        x = 2.0 + k * 4.0
        R.light(box(x - 0.3, 7.4, CH - 0.03, x + 0.3, 8.6, CH - 0.01, 'e_panel'))
        R.nocol.add(box(x - 0.36, 7.34, CH - 0.05, x + 0.36, 8.66, CH - 0.03, 'chrome'))
    for c in MODS:
        for (y, f) in ((CY0 + 0.03, 1), (CY1 - 0.03, -1)):
            x = c + 1.0
            R.nocol.add(box(x - 0.04, min(y, y + 0.22 * f), 1.9, x + 0.04, max(y, y + 0.22 * f), 1.96, 'brass'))
            R.nocol.add(frustum(x, y + 0.26 * f, 1.78, 1.98, 0.16, 0.06, 10, 'green', inner='ivory'))
            R.light(cyl(x, y + 0.26 * f, 1.82, 1.85, 0.08, 8, side='e_amber', top='e_amber', bottom='e_amber'))


def to_xy(side, c, u, v):
    """Room-local (u across, v from the back wall) to plan."""
    return (c + u, T + v) if side == 'S' else (c + u, D - T - v)


def rbox(side, c, u0, v0, u1, v1, z0, z1, m, **kw):
    x0, y0 = to_xy(side, c, u0, v0); x1, y1 = to_xy(side, c, u1, v1)
    return box(min(x0, x1), min(y0, y1), z0, max(x0, x1), max(y0, y1), z1, m, **kw)


def door_frame(R, side, c):
    """The corridor side of a room's door: a frame and a brass number."""
    u0, u1 = -1.3, -0.3
    yw = CY0 if side == 'S' else CY1
    f = 1 if side == 'S' else -1
    for u in (u0 - 0.1, u1):
        R.nocol.add(box(c + u, min(yw, yw + 0.05 * f), 0, c + u + 0.1, max(yw, yw + 0.05 * f), 2.3, 'oak'))
    R.nocol.add(box(c + u0 - 0.1, min(yw, yw + 0.05 * f), 2.2, c + u1 + 0.1, max(yw, yw + 0.05 * f), 2.3, 'oak'))
    return yw, f


def shut_door(R, side, c):
    yw, f = door_frame(R, side, c)
    ya, yb = sorted((yw, yw + 0.03 * f))
    R.nocol.add(box(c - 1.3, ya, 0, c - 0.3, yb, 2.2, 'walnut'))
    for (z0, z1) in ((0.2, 0.95), (1.1, 2.0)):
        yc, yd = sorted((yw + 0.03 * f, yw + 0.045 * f))
        R.nocol.add(box(c - 1.18, yc, z0, c - 0.42, yd, z1, 'oxblood'))
    yc, yd = sorted((yw + 0.03 * f, yw + 0.1 * f))
    R.nocol.add(box(c - 0.45, yc, 1.0, c - 0.38, yd, 1.07, 'brass'))
    plate(R, c - 0.8, yw + 0.03 * f, 1.62, f, num(side, c))
    if (side, c) in (('S', 12.0), ('N', 20.0)):     # do not disturb
        R.nocol.add(box(c - 0.5, min(yc, yd) + 0.0, 0.75, c - 0.35, max(yc, yd) + 0.0, 1.0, 'oxblood'))


def plate(R, x, y, z, f, n):
    """Brass numerals, as little bars (three digits). The game shows Blender's world mirrored, so the
    numbers are laid out to read right way round in the game."""
    g = Geo()
    ya, yb = sorted((y, y + 0.012 * f))
    g.add(box(x - 0.16, ya, z - 0.07, x + 0.16, yb, z + 0.07, 'walnut'))
    ya, yb = sorted((y + 0.012 * f, y + 0.02 * f))
    SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcfgd'}
    for i, ch in enumerate(str(n)):
        cx = x - 0.1 + i * 0.1
        w, h, t = 0.035, 0.05, 0.008
        seg = {'a': (cx - w, z + h - t, cx + w, z + h + t), 'g': (cx - w, z - t, cx + w, z + t), 'd': (cx - w, z - h - t, cx + w, z - h + t)}
        for s in SEG[ch]:
            if s in seg:
                a_, b_, c_, d_ = seg[s]; g.add(box(a_, ya, b_, c_, yb, d_, 'brass'))
            else:
                xx = cx + w if s in 'bc' else cx - w
                za, zb = (z, z + h) if s in 'bf' else (z - h, z)
                g.add(box(xx - t, ya, za, xx + t, yb, zb, 'brass'))
    if f < 0:        # a plate facing -y: mirror it about its centre so it reads in the game
        g.v = [(2 * x - vx, vy, vz) for (vx, vy, vz) in g.v]
        g.f = [tuple(reversed(q)) for q in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    R.nocol.add(g)


# ---------------------------------------------------------------------------
def room(R, side, c, kind):
    x0, x1 = c - 1.9, c + 1.9
    y0, y1 = (T, CY0 - 0.4) if side == 'S' else (CY1 + 0.4, D - T)
    R.cut(box(x0, y0 - (0.02 if side == 'S' else 0), 0, x1, y1 + (0.02 if side == 'N' else 0), RH, 'damask', bottom='carpet', top='plaster'))
    B = lambda *a, **k: rbox(side, c, *a, **k)
    if kind != 'hidden':
        yw, f = door_frame(R, side, c)
        R.cut(B(-1.3, RD - 0.05, -0.3, RD + 0.45, 0, 2.2, 'oak', bottom='carpet', top='oak'))
        plate(R, c - 0.8, yw + 0.03 * f, 1.62, f, num(side, c))
        # the door, open into the room
        hx, hy = to_xy(side, c, -0.3, RD - 0.04)
        ang = (math.pi + 1.25) if side == 'S' else (math.pi - 1.25)
        leaf = door_leaf(0.98, 2.15, 'walnut', 'oxblood')
        R.nocol.add(leaf.xform(ang, hx, hy, 0))
    else:
        shut_door(R, side, c)
    # a skirting board
    for (u0, v0, u1, v1) in ((-1.9, 0, 1.9, 0.02), (-1.9, 0, -1.88, RD), (1.88, 0, 1.9, RD), (-1.9, RD - 0.02, 1.9, RD)):
        R.nocol.add(B(u0, v0, u1, v1, 0, 0.12, 'walnut'))
    rnd = random.Random(int(c) * 7 + (1 if side == 'N' else 0))
    face_in = 0.0 if side == 'S' else math.pi        # direction of +v, as an angle... (unused)
    vdir = math.pi / 2 if side == 'S' else -math.pi / 2   # +v in plan
    if kind == 'door':
        bed(R, side, c, (-1.9, 2.3), along='u')
        shelf_on(R, side, c, 1.9, 2.3, 5.4, rows=6)
        nightstand(R, side, c, -1.85, 4.55, lamp=True)
    elif kind == 'closet':
        bed(R, side, c, (0.0, 0.0), along='v')
        nightstand(R, side, c, -1.3, 0.05, lamp=True); nightstand(R, side, c, 0.85, 0.05, lamp=False)
        shelf_on(R, side, c, -1.9, 2.5, 4.6, rows=6)
        wardrobe(R, side, c)
    elif kind == 'mirror':
        bed(R, side, c, (0.0, 0.0), along='v')
        nightstand(R, side, c, -1.3, 0.05, lamp=True); nightstand(R, side, c, 0.85, 0.05, lamp=True)
        shelf_on(R, side, c, 1.9, 2.6, 5.4, rows=6)
        # a dresser and a mirror on the other wall
        R.parts.add(B(-1.9, 2.8, -1.4, 4.2, 0, 0.8, 'walnut', top='oak'))
        xm, ym = to_xy(side, c, -1.88, 3.5)
        R.nocol.add(B(-1.9, 2.95, -1.86, 4.05, 1.0, 2.3, 'gilt'))
        R.meta.setdefault('mirrors', []).append({'c': [round(xm + 0.03, 2), round(ym, 2), 1.08], 'n': [1, 0, 0], 'w': 0.94, 'h': 1.14})
    elif kind == 'plain':
        bed(R, side, c, (0.0, 0.0), along='v', unmade=True)
        nightstand(R, side, c, -1.3, 0.05, lamp=True)
        shelf_on(R, side, c, 1.9, 2.6, 5.4, rows=6)
        chairat(R, side, c, -1.2, 3.6, rnd)
    elif kind == 'hidden':
        hidden(R, side, c)
    # a picture, a ceiling lamp, a rug
    if kind != 'hidden':
        pu, pv = (0.0, 0.03) if kind != 'door' else (-1.87, 3.3)
        if kind != 'door':
            R.nocol.add(B(-0.6, 0.02, 0.6, 0.05, 1.45, 2.15, 'gilt'))
            R.nocol.add(B(-0.52, 0.05, 0.52, 0.06, 1.53, 2.07, rnd.choice(('green', 'slate', 'oxblood'))))
        x, y = to_xy(side, c, 0.2, 3.3)
        bulb(R, x, y, RH - 0.45, r=0.13, m='e_lamp', top=RH, shade='ivory')
        R.nocol.add(B(-1.3, 2.4, 1.2, 4.6, 0.0, 0.012, 'oxblood'))


def bed(R, side, c, at, along='v', unmade=False):
    B = lambda *a, **k: rbox(side, c, *a, **k)
    if along == 'v':      # headboard on the back wall, centred at u=at[0]
        u0, u1, v0, v1 = at[0] - 0.8, at[0] + 0.8, 0.02, 2.1
        R.parts.add(B(u0, v0, u1, v0 + 0.08, 0, 1.25, 'walnut'))
        R.parts.add(B(u0, v0 + 0.08, u1, v1, 0, 0.3, 'walnut'))
        R.parts.add(B(u0 + 0.03, v0 + 0.1, u1 - 0.03, v1 - 0.03, 0.3, 0.55, 'bed'))
        if unmade:
            g = rbox(side, c, u0, v0 + 0.9, u1 + 0.08, v1 + 0.06, 0.5, 0.62, 'green')
            rot(g, 'y', 0.05, *to_xy(side, c, u1, 1.5), 0.55)
            R.nocol.add(g)
        else:
            R.nocol.add(B(u0 - 0.03, v0 + 0.7, u1 + 0.03, v1 + 0.03, 0.46, 0.6, 'green'))
        R.nocol.add(B(u0 + 0.12, v0 + 0.15, u0 + 0.75, v0 + 0.55, 0.55, 0.68, 'bed'))
        R.nocol.add(B(u1 - 0.75, v0 + 0.15, u1 - 0.12, v0 + 0.55, 0.55, 0.68, 'bed'))
        x, y = to_xy(side, c, at[0], 1.2)
        R.spot('bed', x, y, 0.55, math.pi / 2 if side == 'S' else -math.pi / 2)
    else:                 # headboard on the side wall at u=at[0] (u=-1.9), bed along u, from v=at[1]
        u0, u1, v0, v1 = -1.88, -1.88 + 2.05, at[1], at[1] + 1.6
        R.parts.add(B(u0, v0, u0 + 0.08, v1, 0, 1.25, 'walnut'))
        R.parts.add(B(u0 + 0.08, v0, u1, v1, 0, 0.3, 'walnut'))
        R.parts.add(B(u0 + 0.1, v0 + 0.03, u1 - 0.03, v1 - 0.03, 0.3, 0.55, 'bed'))
        R.nocol.add(B(u0 + 0.7, v0 - 0.03, u1 + 0.03, v1 + 0.03, 0.46, 0.6, 'green'))
        R.nocol.add(B(u0 + 0.15, v0 + 0.12, u0 + 0.55, v0 + 0.75, 0.55, 0.68, 'bed'))
        R.nocol.add(B(u0 + 0.15, v1 - 0.75, u0 + 0.55, v1 - 0.12, 0.55, 0.68, 'bed'))
        x, y = to_xy(side, c, (u0 + u1) / 2, (v0 + v1) / 2)
        R.spot('bed', x, y, 0.55, 0.0)


def nightstand(R, side, c, u, v, lamp=True):
    B = lambda *a, **k: rbox(side, c, *a, **k)
    R.parts.add(B(u, v, u + 0.45, v + 0.42, 0, 0.6, 'walnut', top='oak'))
    if lamp:
        x, y = to_xy(side, c, u + 0.22, v + 0.2)
        R.nocol.add(cyl(x, y, 0.6, 0.64, 0.07, 10, side='brass', top='brass'))
        R.nocol.add(cyl(x, y, 0.64, 0.9, 0.012, 6, side='brass', caps=False))
        R.nocol.add(frustum(x, y, 0.86, 1.06, 0.17, 0.09, 12, 'green', inner='ivory'))
        R.light(cyl(x, y, 0.9, 0.93, 0.09, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))


def shelf_on(R, side, c, u, v0, v1, rows=6):
    """The room's one bookcase, against the side wall at u=+-1.9."""
    xw = c + u
    if u > 0:
        ya, yb = to_xy(side, c, u, v0)[1], to_xy(side, c, u, v1)[1]
        sh(R, '-x', xw, min(ya, yb), max(ya, yb), rows=rows, frame='walnut', depth=0.3)
    else:
        ya, yb = to_xy(side, c, u, v0)[1], to_xy(side, c, u, v1)[1]
        sh(R, '+x', xw, min(ya, yb), max(ya, yb), rows=rows, frame='walnut', depth=0.3)


def chairat(R, side, c, u, v, rnd):
    x, y = to_xy(side, c, u, v)
    a = rnd.uniform(0, 2 * math.pi)
    R.parts.add(chair(x, y, a)); R.spot('sit', x, y, 0.48, a)


def wardrobe(R, side, c):
    """A wardrobe in the corner by the door, doors open, coats inside, and no back."""
    B = lambda *a, **k: rbox(side, c, *a, **k)
    u0, u1, v0, v1 = 0.95, 1.9, RD - 1.2, RD - 0.03
    R.parts.add(B(u0, v0, u1, v0 + 0.05, 0, 2.3, 'walnut'))           # the side toward the bed
    R.parts.add(B(u0, v0, u1, v1, 2.3, 2.4, 'walnut'))                # the top
    R.parts.add(B(u0 - 0.05, v0, u0, v0 + 0.12, 0, 2.4, 'walnut'))    # the front posts
    R.parts.add(B(u0 - 0.05, v1 - 0.12, u0, v1, 0, 2.4, 'walnut'))
    # the wall behind: gone, into the next room
    gy = sorted((to_xy(side, c, 0, v0 + 0.1)[1], to_xy(side, c, 0, v1 - 0.1)[1]))
    R.cut(box(c + 1.85, gy[0], 0, c + 2.15, gy[1], 2.05, 'wood', bottom='carpet', top='wood'))
    # coats on a rail across it (drawn only: you push through them)
    ra, rb = to_xy(side, c, u0 + 0.1, (v0 + v1) / 2), to_xy(side, c, u1 - 0.05, (v0 + v1) / 2)
    R.nocol.add(beam((ra[0], ra[1], 1.95), (rb[0], rb[1], 1.95), 0.025, 'brass'))
    for k in range(4):
        t = 0.2 + k * 0.2
        x = ra[0] + (rb[0] - ra[0]) * t
        R.nocol.add(box(x - 0.04, min(ra[1], rb[1]) - 0.28, 0.9, x + 0.04, max(ra[1], rb[1]) + 0.28, 1.92, ('slate', 'oxblood', 'walnut', 'green')[k]))
    # the doors stand open
    for (v, dv) in ((v0 + 0.05, -0.25), (v1 - 0.05, 0.25)):
        p0 = to_xy(side, c, u0 - 0.03, v); p1 = to_xy(side, c, u0 - 0.5, v + dv)
        R.nocol.add(obox(p0[0], p0[1], p1[0], p1[1], 0.05, 2.25, 0.04, 'walnut'))


def hidden(R, side, c):
    """Room 216, reached only through the wardrobe of 212: somebody lives here."""
    B = lambda *a, **k: rbox(side, c, *a, **k)
    # books on every wall, to the ceiling
    xa, xb = c - 1.9, c + 1.9
    y0, y1 = CY1 + 0.4, D - T
    sh(R, '-y', y1, xa + 0.1, xb - 0.1, rows=6, frame='walnut', depth=0.3)
    sh(R, '-x', xb, y0 + 0.1, y1 - 0.4, rows=6, frame='walnut', depth=0.3)
    sh(R, '+x', xa, y0 + 1.3, y1 - 0.4, rows=6, frame='walnut', depth=0.3)
    sh(R, '+y', y0, xa + 0.9, xb - 0.4, rows=6, frame='walnut', depth=0.3)
    # the unmade bed, a desk, a lamp, the television showing the corridor
    bed(R, side, c, (0.2, 0.0), along='v', unmade=True)
    R.parts.add(B(-1.5, 3.0, -0.5, 3.6, 0, 0.76, 'walnut', top='leather'))
    x, y = to_xy(side, c, -1.0, 3.3)
    desk_lamp(R, x - 0.3, y, 0.76)
    g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, 'oxblood'); g.add(box(-0.19, -0.13, 0.02, 0.19, 0.13, 0.04, 'ivory'))
    R.nocol.add(g.xform(0.3, x + 0.1, y, 0.76))
    xc, yc = to_xy(side, c, -1.0, 2.5)
    R.parts.add(chair(xc, yc, -math.pi / 2)); R.spot('sit', xc, yc, 0.48, -math.pi / 2)
    R.parts.add(B(0.8, 3.4, 1.5, 3.9, 0, 0.55, 'walnut'))
    R.parts.add(B(0.85, 3.45, 1.45, 3.85, 0.55, 1.05, 'black'))
    R.light(B(0.9, 3.44, 1.4, 3.45, 0.62, 0.98, 'e_kiosk'))
    book_pile(R, *to_xy(side, c, 1.4, 1.6), 0.0, 9, random.Random(5), 0.4)
    book_pile(R, *to_xy(side, c, 1.3, 2.4), 0.0, 6, random.Random(6), 1.4)
    R.nocol.add(B(-1.3, 1.9, 1.3, 4.2, 0.0, 0.012, 'velvet'))
    x, y = to_xy(side, c, 0.2, 3.3)
    bulb(R, x, y, RH - 0.5, r=0.12, m='e_amber', top=RH, shade='ivory')
