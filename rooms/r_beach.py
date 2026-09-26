"""The Beach: the north doors of an ordinary marble reading room stand open, and outside them is a grey
beach under an overcast sky. Sand has drifted in over the marble. A line of bookcases stands along the
tide line and walks on out into the sea, smaller and smaller, toward a horizon that is painted on the
wall. Two timber piers run out to the doorways, which stand in the sky at their ends. Against the east
end of the beach is a striped bathing hut; its door is padlocked, but one board at the back has gone."""
from kit_h9 import *

W, D = 32.0, 32.0
LY0, LY1 = 10.4, 11.0          # the library's north wall
LH_ = 6.8                      # the library's ceiling
SKY = TOP - 0.08               # the sky over the beach
WT, WB = -0.25, -1.85          # the sea's surface and the bottom of the basin
DX0, DX1, DZ = 12.8, 19.2, 5.0 # the great door
PIERS = (8.0, 24.0)
QY0, QY1 = 22.2, 25.8          # the quays from the side doors to the piers
HX0, HX1, HY0, HY1, HZ = 28.3, 31.45, 12.2, 15.1, 0.25   # the bathing hut


def sand(x, y):
    if y <= 13.5: z = 0.0
    elif y <= 22.0: z = -0.45 * (y - 13.5) / 8.5
    else: z = -0.45 - 1.25 * (y - 22.0) / (D - T - 22.0)
    # ripples and a low drift along the library wall
    z += 0.035 * math.sin(x * 1.3 + y * 0.4) * min(1.0, max(0.0, (y - 12.5) / 3))
    z += 0.12 * smooth_bump(y - LY1, 1.6) * (0.6 + 0.4 * math.sin(x * 0.7))
    return z


def make():
    R = Room('beach', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    library(R)
    beach(R)
    sky(R)
    piers(R)
    stacks(R)
    hut(R)
    fx(R, 'fog', [T, 18.0, WT, W - T, D - T, 5.0], density=0.03)
    # walkers
    navloop(R, [(3.0, 3.0), (16.0, 3.2), (29.0, 3.0), (29.0, 8.0), (16.0, 8.6), (3.0, 8.0)])
    pts = [(16.0, 12.4), (21.0, 15.2), (24.0, 15.8), (24.0, 29.0), (24.0, 20.0), (16.0, 17.0), (8.0, 20.0), (8.0, 29.0), (8.0, 15.8), (11.0, 15.2)]
    ids = [R.navpt(x, y, 0.0 if (abs(x - 8) < 1.6 or abs(x - 24) < 1.6) and y > 15.1 else sand(x, y)) for (x, y) in pts]
    R.link(*ids); R.link(ids[-1], ids[0])
    R.link(4, ids[0])
    secret(R, 29.9, 13.65, HZ, 'The Bathing Hut',
           'Inside the hut it is dry and smells of creosote and old paperbacks. A deckchair faces a little window onto the sea, and on the shelf is every book anyone has ever left on a beach.')
    R.meta['water_tint'] = [0.07, 0.13, 0.15]   # a grey northern sea, not a pool
    return finish(R, 'The Beach', weight=3, probe=(16, 18, 1.8),
                  blurb='The doors at the end of the reading room are open, and there is a beach outside. The sea is grey and very calm, and the bookcases go on out into it.')


# ---------------------------------------------------------------------------
def library(R):
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, LY0, LH_, 'tile', bottom='terrazzo', top='plaster'))
    # the great door, and two tall windows onto the beach
    R.cut(box(DX0, LY0 - 0.05, 0, DX1, LY1 + 0.05, DZ, 'tile', bottom='terrazzo', top='tile'))
    for c in (5.2, 26.8):
        R.cut(box(c - 1.3, LY0 - 0.05, 1.0, c + 1.3, LY1 + 0.05, 5.2, 'tile', bottom='tile', top='tile'))
        R.col.add(box(c - 1.3, LY0, 1.0, c + 1.3, LY1, 5.2, 'tile'))
        for k in (-1, 0, 1):
            R.nocol.add(box(c + k * 0.65 - 0.03, LY0 + 0.25, 1.0, c + k * 0.65 + 0.03, LY0 + 0.31, 5.2, 'iron'))
        for z in (2.4, 3.8):
            R.nocol.add(box(c - 1.3, LY0 + 0.25, z - 0.03, c + 1.3, LY0 + 0.31, z + 0.03, 'iron'))
        R.parts.add(box(c - 1.45, LY0 - 0.25, 0.85, c + 1.45, LY0, 1.0, 'tile'))
    # the door case and its two leaves, swung open into the room
    for x in (DX0 - 0.35, DX1):
        R.parts.add(box(x, LY0 - 0.2, 0, x + 0.35, LY0, DZ + 0.4, 'walnut'))
    R.parts.add(box(DX0 - 0.45, LY0 - 0.25, DZ, DX1 + 0.45, LY0, DZ + 0.5, 'walnut'))
    lw = (DX1 - DX0) / 2 - 0.02
    for (hx, ang) in ((DX0, -1.2), (DX1, math.pi + 1.2)):
        R.nocol.add(door_leaf(lw, DZ - 0.05, 'walnut', 'oak').xform(ang, hx, LY0 - 0.04, 0))
        R.col.add(obox(hx, LY0 - 0.04, hx + lw * math.cos(ang), LY0 - 0.04 + lw * math.sin(ang), 0, DZ - 0.1, 0.1, 'tile'))
    # books: the south wall, the ends, and either side of the great door
    rows = 13
    for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, W - 0.6)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, 6.2),):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
    for (a, b) in ((0.6, 3.7), (6.7, DX0 - 0.5), (DX1 + 0.5, 25.3), (28.3, W - 0.6)):
        sh(R, '-y', LY0, a, b, rows=rows, frame='walnut')
    for c in (8.0, 24.0):
        sh(R, '+y', T, c - 2.0, c + 2.0, z=4.3, rows=5, frame='walnut')
    for c in (8.0,):
        sh(R, '+x', T, c - 2.0, 9.9, z=4.3, rows=5, frame='walnut')
        sh(R, '-x', W - T, c - 2.0, 9.9, z=4.3, rows=5, frame='walnut')
    # reading desks with green lamps, chairs; one chair turned to face the sea
    for (x0, x1) in ((3.0, 10.5), (21.5, 29.0)):
        R.parts.add(table(x0, 4.6, x1, 5.8, 0.78, 'walnut', top='leather'))
        for k in range(3):
            desk_lamp(R, x0 + (x1 - x0) * (k + 0.5) / 3, 5.2, 0.78)
        for k in range(5):
            xx = x0 + (x1 - x0) * (k + 0.5) / 5
            R.parts.add(chair(xx, 4.1, math.pi / 2)); R.spot('sit', xx, 4.1, 0.48, math.pi / 2)
    R.parts.add(chair(16.0, 7.2, math.pi / 2)); R.spot('sit', 16.0, 7.2, 0.48, math.pi / 2)
    # sand blown in over the marble, a wet patch
    R.nocol.add(field(lambda x, y: 0.1 * smooth_bump(math.hypot((x - 16) / 3.2, (y - LY0) / 1.6), 1.0) + 0.004,
                      DX0 - 1.0, LY0 - 2.6, DX1 + 1.0, LY0, 16, 8, 'sand', floor=0.012))
    # a vaulted ceiling of coffers and pendant lamps
    for k in range(1, 8):
        x = T + k * (W - 2 * T) / 8
        R.nocol.add(box(x - 0.14, T, LH_ - 0.35, x + 0.14, LY0, LH_, 'ivory'))
    R.nocol.add(box(T, 5.2, LH_ - 0.35, W - T, 5.5, LH_, 'ivory'))
    for x in (4.0, 12.0, 20.0, 28.0):
        pendant(R, x, 5.2, 3.6, LH_, r=0.26)
    for (x, y) in ((1.4, 9.4), (W - 1.4, 9.4)):
        floor_lamp(R, x, y, 1.6, m='e_amber')


# ---------------------------------------------------------------------------
def beach(R):
    # carve the beach down in bands so the sand sheet lies on solid ground
    y = LY1
    while y < D - T - 1e-6:
        y1 = min(D - T + 0.02, y + 0.6)
        zmin = min(sand(x, yy) for x in (T, 4, 8, 12, 16, 20, 24, 28, W - T) for yy in (y, y1)) - 0.08
        R.cut(box(T - 0.02, y - (0.02 if y == LY1 else 0.0), max(WB, zmin), W - T + 0.02, y1, SKY + 0.05, 'sand', bottom='sand', top='plaster'))
        y = y1
    R.parts.add(field(sand, T, LY1, W - T, 20.4, 40, 20, 'sand', floor=-9))
    R.parts.add(field(sand, T, 20.4, W - T, 25.2, 40, 10, 'wetsand', floor=-9))
    R.parts.add(field(sand, T, 25.2, W - T, D - T, 40, 14, 'slate', floor=-9))
    R.water.append(dict(x0=T, y0=18.6, x1=W - T, y1=D - T, top=WT, bot=WB))
    # a darker band where the sand is wet, and a line of foam at the water's edge
    R.nocol.add(field(lambda x, y: sand(x, y) + 0.01, T, 16.8, W - T, 20.4, 40, 6, 'wetsand', floor=-9))
    rnd = random.Random(4)
    for k in range(26):
        x0 = T + k * (W - 2 * T) / 26; x1 = x0 + (W - 2 * T) / 26 * rnd.uniform(0.6, 1.0)
        y = 19.2 + 0.25 * math.sin(k * 0.9)
        R.nocol.add(box(x0, y, WT + 0.005, x1, y + rnd.uniform(0.12, 0.3), WT + 0.02, 'ivory'))
    # things left on the sand: open books drying, a bucket, a deckchair or two
    for (x, y, a) in ((11.5, 14.2, 0.6), (20.5, 13.0, 2.1), (4.0, 15.8, 1.2), (14.3, 16.9, 2.9), (26.0, 16.4, 0.2)):
        g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, rnd.choice(BOOKM))
        g.add(box(-0.19, -0.13, 0.02, -0.005, 0.13, 0.045, 'ivory')); g.add(box(0.005, -0.13, 0.02, 0.19, 0.13, 0.045, 'ivory'))
        R.nocol.add(g.xform(a, x, y, sand(x, y)))
    for (x, y, a) in ((6.2, 13.2, 0.4), (22.8, 12.8, -0.3)):
        deckchair(R, x, y, a)


def deckchair(R, x, y, a, z=None, cloth='hutred'):
    z = sand(x, y) if z is None else z
    g = Geo()
    for s in (-0.3, 0.3):
        g.add(beam((-0.5, s, 0), (0.45, s, 0.9), 0.04, 'oak'))
        g.add(beam((0.45, s, 0), (-0.2, s, 0.45), 0.04, 'oak'))
    g.add(beam((-0.45, 0, 0.12), (0.4, 0, 0.82), 0.02, cloth, 0.58))
    R.parts.add(g.xform(a, x, y, z))


# ---------------------------------------------------------------------------
def door_frame_sky(R, side, c, z0=-0.3):
    """A stone surround where a doorway stands in the painted sky."""
    if side == 'N':
        y = D - T
        R.parts.add(box(c - 2.1, y - 0.4, z0, c - 1.5, y, 4.8, 'tile'))
        R.parts.add(box(c + 1.5, y - 0.4, z0, c + 2.1, y, 4.8, 'tile'))
        R.parts.add(box(c - 2.3, y - 0.5, 4.4, c + 2.3, y, 5.0, 'tile'))
    else:
        x0, x1 = (T, T + 0.4) if side == 'W' else (W - T - 0.4, W - T)
        e0, e1 = (T, T + 0.5) if side == 'W' else (W - T - 0.5, W - T)
        R.parts.add(box(x0, c - 2.1, z0, x1, c - 1.5, 4.8, 'tile'))
        R.parts.add(box(x0, c + 1.5, z0, x1, c + 2.1, 4.8, 'tile'))
        R.parts.add(box(e0, c - 2.3, 4.4, e1, c + 2.3, 5.0, 'tile'))


def sky(R):
    zb = WB
    R.light(panel_z(SKY, T, LY1, W - T, D - T, 'e_skydome', up=False))
    # the north wall: sky, with the two doorways standing in it
    yn = D - T - 0.02
    xs = [T, 8.0 - 2.1, 8.0 + 2.1, 24.0 - 2.1, 24.0 + 2.1, W - T]
    for k in range(0, len(xs) - 1):
        if k % 2 == 0: R.light(panel_y(yn, xs[k], xs[k + 1], zb, SKY, 'e_skydome', face=-1))
        else: R.light(panel_y(yn, xs[k], xs[k + 1], 4.8, SKY, 'e_skydome', face=-1))
    for c in PIERS: door_frame_sky(R, 'N', c, z0=WB)
    # the side walls beyond the library: sky too
    for (side, x, f) in (('W', T + 0.02, 1), ('E', W - T - 0.02, -1)):
        ys = [LY1, 24.0 - 2.1, 24.0 + 2.1, D - T]
        R.light(panel_x(x, ys[0], ys[1], zb, SKY, 'e_skydome', face=f))
        R.light(panel_x(x, ys[1], ys[2], 4.8, SKY, 'e_skydome', face=f))
        R.light(panel_x(x, ys[2], ys[3], zb, SKY, 'e_skydome', face=f))
        door_frame_sky(R, side, 24.0)
    # the library's outside wall, seen from the beach: stone, a cornice, the sign of a door
    R.parts.add(box(T, LY1, SKY - 0.9, W - T, LY1 + 0.35, SKY - 0.6, 'tile'))
    R.parts.add(box(DX0 - 0.6, LY1, 0, DX0 - 0.2, LY1 + 0.3, DZ + 0.8, 'tile'))
    R.parts.add(box(DX1 + 0.2, LY1, 0, DX1 + 0.6, LY1 + 0.3, DZ + 0.8, 'tile'))
    R.parts.add(box(DX0 - 0.8, LY1, DZ + 0.3, DX1 + 0.8, LY1 + 0.4, DZ + 0.9, 'tile'))


# ---------------------------------------------------------------------------
def piers(R):
    for c in PIERS:
        x0, x1 = c - 1.5, c + 1.5
        y0 = 15.0
        R.parts.add(box(x0, y0, -0.14, x1, D - T, 0.0, 'oak', bottom='walnut', sides='walnut'))
        for k in range(int((D - T - y0) / 0.3)):
            y = y0 + 0.15 + k * 0.3
            R.nocol.add(box(x0, y - 0.005, 0.0, x1, y + 0.005, 0.004, 'walnut'))
        y = y0 + 1.0
        while y < D - T:
            for x in (x0 + 0.15, x1 - 0.15):
                R.parts.add(cyl(x, y, sand(x, y) - 0.05, -0.14, 0.13, 8, side='walnut', top='walnut', bottom='walnut'))
            y += 2.4
        # rails where the water is deep
        for x in (x0 + 0.06, x1 - 0.06):
            rail_line(R, x, 25.9, 0.0, x, D - T - 0.3, 0.0, m='oak', post='walnut', spacing=1.2, mid=True)
        lamp_post_(R, x0 + 0.25, 29.5)
        lamp_post_(R, x1 - 0.25, 20.0)
    # the quays from the side doorways out to the piers, with steps down to the sand
    for (x0, x1) in ((T, PIERS[0] - 1.5), (PIERS[1] + 1.5, W - T)):
        R.parts.add(box(x0, QY0, WB, x1, QY1, 0.0, 'tile'))
        R.parts.add(box(x0, QY0 - 0.5, WB, x1, QY0, -0.22, 'tile'))
        for (a, b) in ((QY1 - 0.06, QY1 - 0.06),):
            rail_line(R, x0 + 0.1, a, 0.0, x1 - 0.1, b, 0.0, m='oak', post='walnut', spacing=1.2, mid=True)
        for k in range(int((x1 - x0) / 1.5)):
            x = x0 + 0.75 + k * 1.5
            R.nocol.add(box(x - 0.2, QY0 + 0.3, 0.0, x + 0.2, QY0 + 0.7, 0.02, 'slate'))
        R.nocol.add(cyl((x0 + x1) / 2, QY0 + 1.8, 0.0, 0.35, 0.16, 10, side='iron', top='iron', bottom='iron'))


def lamp_post_(R, x, y, h=2.8):
    R.parts.add(cyl(x, y, 0.0, 0.1, 0.14, 8, side='iron', top='iron', bottom='iron'))
    R.parts.add(cyl(x, y, 0.1, h, 0.03, 6, side='iron', caps=False))
    R.nocol.add(frustum(x, y, h - 0.02, h + 0.2, 0.32, 0.1, 12, 'green', inner='ivory'))
    R.light(cyl(x, y, h - 0.02, h + 0.03, 0.18, 10, side='e_amber', top='e_amber', bottom='e_amber'))


# ---------------------------------------------------------------------------
def stacks(R):
    rnd = random.Random(21)
    # along the tide line, standing in the shallows, facing the land; lamps on top
    for (x, y, a) in ((2.8, 20.2, -0.1), (11.8, 19.7, 0.08), (20.2, 20.4, -0.05), (28.6, 19.9, 0.12), (4.8, 26.5, 0.2), (27.8, 27.0, -0.15)):
        L = 2.4
        z = sand(x, y)
        rows = 6
        th = -math.pi / 2 + a
        bx, by = x - math.cos(th + math.pi / 2) * 0, y
        shelf(R, x + L / 2 * math.cos(a), y + L / 2 * math.sin(a), z, L, -math.pi / 2 + a, rows=rows, frame='walnut', depth=0.36)
        shelf(R, x - L / 2 * math.cos(a), y - L / 2 * math.sin(a) + 0.0, z, L, math.pi / 2 + a, rows=rows, frame='walnut', depth=0.36)
        top = z + 2.7
        desk_lamp(R, x + 0.5, y, top)
    # the line that walks out to sea, each one smaller, to fake the distance
    for k, (y, s) in enumerate(((22.6, 1.0), (25.6, 0.72), (27.8, 0.52), (29.4, 0.38), (30.5, 0.27), (31.2, 0.19))):
        x = 16.0 + 0.1 * math.sin(k)
        z = sand(x, y)
        L = 2.4 * s
        rows = 6
        shelf(R, x + L / 2, y, z, L, -math.pi / 2, rows=rows, row_h=0.42 * s, depth=0.36 * s, frame='walnut', board=0.035 * s, top_gap=0.08 * s)
        shelf(R, x - L / 2, y + 0.005, z, L, math.pi / 2, rows=rows, row_h=0.42 * s, depth=0.36 * s, frame='walnut', board=0.035 * s, top_gap=0.08 * s)
        top = z + rows * 0.42 * s + 0.14 * s
        R.parts.add(cyl(x + 0.4 * s, y, top, top + 0.03 * s, 0.08 * s, 10, side='brass', top='brass'))
        R.parts.add(cyl(x + 0.4 * s, y, top, top + 0.36 * s, 0.012 * s + 0.004, 6, side='brass', caps=False))
        R.parts.add(obox(x + 0.4 * s - 0.17 * s, y, x + 0.4 * s + 0.17 * s, y, top + 0.36 * s, top + 0.44 * s, 0.13 * s, 'green'))
        R.light(obox(x + 0.4 * s - 0.15 * s, y, x + 0.4 * s + 0.15 * s, y, top + 0.345 * s, top + 0.36 * s, 0.09 * s, 'e_lamp'))


# ---------------------------------------------------------------------------
def hut(R):
    """A striped bathing hut on low stilts against the east end of the beach."""
    x0, x1, y0, y1, z = HX0, HX1, HY0, HY1, HZ
    hw = 2.5                      # walls up to here, then the roof
    # the floor on stilts, and a step at the (locked) front door
    R.parts.add(box(x0, y0, z - 0.1, x1, y1, z, 'oak', bottom='walnut'))
    for (px, py) in ((x0 + 0.1, y0 + 0.1), (x1 - 0.1, y0 + 0.1), (x0 + 0.1, y1 - 0.1), (x1 - 0.1, y1 - 0.1)):
        R.parts.add(box(px - 0.08, py - 0.08, -0.3, px + 0.08, py + 0.08, z - 0.1, 'walnut'))
    t = 0.08
    # striped plank walls: west (the front, with the locked door), south, north (with the loose board)
    def striped(axis, c, a, b, z0, z1, skip=None):
        n = int((b - a) / 0.25 + 0.5)
        for k in range(n):
            p0 = a + (b - a) * k / n; p1 = a + (b - a) * (k + 1) / n
            if skip and skip[0] <= (p0 + p1) / 2 <= skip[1]:
                continue
            m = 'hutred' if k % 2 == 0 else 'ivory'
            if axis == 'x': R.parts.add(box(c - t / 2, p0, z0, c + t / 2, p1, z1, m))
            else: R.parts.add(box(p0, c - t / 2, z0, p1, c + t / 2, z1, m))
    dy0, dy1 = 13.2, 14.1
    striped('x', x0 + t / 2, y0, dy0, z, z + hw)
    striped('x', x0 + t / 2, dy1, y1, z, z + hw)
    R.parts.add(box(x0, dy0, z + 2.05, x0 + t, dy1, z + hw, 'ivory'))
    R.parts.add(box(x0 - 0.02, dy0, z, x0 + t, dy1, z + 2.05, 'hutred'))       # the door, shut
    R.parts.add(box(x0 - 0.1, dy1 - 0.16, z + 1.0, x0 - 0.02, dy1 - 0.08, z + 1.2, 'brass'))   # padlock
    R.parts.add(box(x0 - 0.6, dy0 - 0.2, -0.1, x0, dy1 + 0.2, 0.08, 'oak'))
    striped('y', y0 + t / 2, x0, x1, z, z + hw)
    gx0, gx1 = 29.5, 30.3          # the gone board, at the back of the north side
    striped('y', y1 - t / 2, x0, x1, z, z + hw, skip=(gx0, gx1))
    R.parts.add(box(gx0, y1 - t, z + 1.3, gx1, y1, z + hw, 'hutred'))       # the upper half of the board is still there
    R.parts.add(box(x1 - t, y0, z, x1, y1, z + hw, 'ivory'))                   # the back, against the sky
    # a pitched roof (north-south ridge along y)
    xm = (x0 + x1) / 2
    for s in (-1, 1):
        g = Geo()
        P = [(xm, y0 - 0.25, z + hw + 0.9), (xm, y1 + 0.25, z + hw + 0.9), (xm + s * (x1 - x0) / 2 + s * 0.25, y1 + 0.25, z + hw - 0.1), (xm + s * (x1 - x0) / 2 + s * 0.25, y0 - 0.25, z + hw - 0.1)]
        R.parts.add(prism([(P[0][0], P[0][2]), (P[3][0], P[3][2]), (P[3][0], P[3][2] + 0.1), (P[0][0], P[0][2] + 0.1)], 'y', y0 - 0.25, y1 + 0.25, 'hutred', cap='ivory'))
    R.parts.add(prism([(x0, z + hw), (x1, z + hw), (xm, z + hw + 0.9)], 'y', y0 + 0.01, y0 + 0.08, 'ivory', cap='ivory'))
    R.parts.add(prism([(x0, z + hw), (x1, z + hw), (xm, z + hw + 0.9)], 'y', y1 - 0.08, y1 - 0.01, 'ivory', cap='ivory'))
    # a little window in the north side, looking out to sea
    # (a stack of deckchairs leans against the hut, half hiding the gap)
    for k in range(3):
        g = Geo()
        g.add(box(-0.3, -0.02, 0, 0.3, 0.02, 1.25, 'oak'))
        g.add(box(-0.26, 0.02, 0.1, 0.26, 0.04, 1.15, 'hutred' if k % 2 else 'ivory'))
        rot(g, 'x', 0.22 + 0.05 * k)
        R.nocol.add(g.xform(0, 29.75 + k * 0.07, y1 + 0.35 + k * 0.08, sand(29.8, y1 + 0.4)))
    # inside: a deckchair facing the sea, a shelf of paperbacks, a lantern, a towel on a hook
    deckchair(R, 29.3, 12.95, math.pi / 2 - 0.2, z=z, cloth='green')
    R.spot('sit', 29.4, 13.0, z + 0.4, math.pi / 2)
    shelf(R, x1 - t, y0 + 0.2, z + 0.3, 2.4, '-x', rows=4, frame='oak', depth=0.26)
    R.parts.add(box(x0 + t, y1 - 0.6, z, x0 + 0.7, y1 - t, z + 0.5, 'oak'))
    candle(R, x0 + 0.4, y1 - 0.35, z + 0.5, h=0.14, r=0.03)
    R.nocol.add(box(x0 + t, 12.5, z + 0.6, x0 + t + 0.03, 12.9, z + 1.6, 'hutred'))
    bulb(R, xm, 13.65, z + 2.2, r=0.07, m='e_amber', top=z + hw + 0.8)
