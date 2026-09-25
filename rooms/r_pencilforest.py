"""The Pencil Wood: sharpened pencils twelve to fifteen metres tall stand about the hall like pines, in a
drift of cedar shavings, under a long skylight. A gallery of ordinary bookcases runs round the walls at the
height of their painted shoulders. One pencil, the one with the broken point, is hollow: a slot in its
rubber lets you in, and a spiral stair climbs inside it to a crow's nest in the splintered crown."""
from kit_h1 import *

W = D = 64.0
SC = (57.2, 45.0)        # the hollow pencil
SR, ST = 2.3, 0.25       # its corner radius, wall
STOP = 12.2              # the crow's nest floor
RISE = 3.0               # its stair's rise per turn
HA0 = math.radians(25)   # where its stair starts (just past the slot, which faces east)


def make():
    R = Room('pencilforest', 4, 4, levels=2, res=2048)
    R.sockets(floor='floor', wall='tile')
    top = R.hi - 0.2
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, top, 'tile', bottom='floor', top='plaster'))
    rnd = random.Random(1919)
    g1 = wall_flight(R, 'S', 26.1, wd=2.0, rise=0.22, run=0.28, up=+1)
    g2 = wall_flight(R, 'N', 37.9, wd=2.0, rise=0.22, run=0.28, up=-1)
    gallery(R, gaps=[g1, g2])
    gallery_cases(R, rows=13)
    gallery_lamps(R)
    lower_cases(R, rows=15)
    roof(R, top)
    desks(R)
    hollow_pencil(R)
    forest(R, rnd)
    shavings(R, rnd)
    nav(R)
    R.spot('probe', 32.0, 30.0, 6.0)
    R.meta.update(label='The Pencil Wood', weight=2,
                  blurb='A wood of pencils, all sharpened, standing in their own shavings. It smells of cedar and of school. Nobody has written anything with them yet.')
    R.meta['box'] = [[T, 0, T], [W - T, top, D - T]]
    fx(R, 'dust', [26.0, 5.0, 1.0, 38.0, 59.0, top - 1.0])
    return tidy(R)


def roof(R, top):
    """A long skylight down the middle, stone ribs across the vault every eight metres."""
    R.light(box(27.0, 3.5, top - 0.06, 37.0, D - 3.5, top - 0.03, 'e_sky', skip=('+z',)))
    for k in range(9):
        y = 0.35 + k * 7.9
        R.parts.add(box(T, y - 0.35, top - 0.7, W - T, y + 0.35, top, 'tile', bottom='plaster'))
    for x in (26.6, 37.4):
        R.parts.add(box(x - 0.4, T, top - 0.7, x + 0.4, D - T, top, 'tile', bottom='plaster'))
    # warm pendant globes over the side woods
    for (x, y) in ((12, 16), (12, 40), (52, 24), (48, 56), (16, 56), (50, 8)):
        R.parts.add(cyl(x, y, 11.6, top - 0.7, 0.03, 6, side='iron', caps=False))
        R.light(sphere(x, y, 11.3, 0.4, 12, 6, 'e_lamp'))


def desks(R):
    """Reading desks under the gallery, lit by green lamps: the ordinary library at the edge of the wood."""
    for (x, y, s) in ((T + 0.4, 16.0, 1), (T + 0.4, 32.0, 1), (T + 0.4, 48.0, 1), (W - T - 0.4, 16.0, -1), (W - T - 0.4, 32.0, -1)):
        x0, x1 = (x, x + 1.1) if s > 0 else (x - 1.1, x)
        R.parts.add(table(x0, y - 1.3, x1, y + 1.3, 0.76, 'walnut', top='leather'))
        desk_lamp(R, (x0 + x1) / 2, y - 0.6, 0.76)
        R.parts.add(box((x0 + x1) / 2 - 0.25, y + 0.1, 0.76, (x0 + x1) / 2 + 0.2, y + 0.55, 0.79, 'ivory'))
        cxh = x1 + 0.45 if s > 0 else x0 - 0.45
        R.parts.add(chair(cxh, y, math.pi if s > 0 else 0.0))
        R.spot('sit', cxh, y, 0.48, math.pi if s > 0 else 0.0)
        R.light(sphere(cxh, y + 1.6, 0.2, 0.06, 6, 3, 'e_amber'))


def forest(R, rnd):
    doors = [(i * C + C / 2, 0) for i in range(4)] + [(i * C + C / 2, D) for i in range(4)] + \
            [(0, j * C + C / 2) for j in range(4)] + [(W, j * C + C / 2) for j in range(4)]
    placed = [(SC[0], SC[1], SR)]
    xs = [7.5, 14.5, 21.0, 43.0, 49.5, 56.5]
    for i, x in enumerate(xs):
        for k in range(8):
            y = 7.0 + k * 7.2 + (3.6 if i % 2 else 0.0)
            px, py = x + rnd.uniform(-1.3, 1.3), y + rnd.uniform(-1.3, 1.3)
            r = rnd.uniform(0.95, 1.3)
            if py < 7.5 or py > D - 7.5: continue
            if any(math.hypot(px - dx, py - dy) < 7.5 for dx, dy in doors): continue
            if any(math.hypot(px - qx, py - qy) < r + qr + 2.4 for qx, qy, qr in placed): continue
            if (px < 7.0 and any(abs(py - yy) < 3.4 for yy in (16, 32, 48))) or (px > 57.0 and any(abs(py - yy) < 3.4 for yy in (16, 32))): continue
            placed.append((px, py, r))
            L = rnd.uniform(12.0, 14.2)
            body = 'gilt' if rnd.random() < 0.82 else rnd.choice(['green', 'oxblood', 'gilt'])
            pencil_up(R, px, py, 0.0, L, r, body=body, a0=rnd.uniform(0, math.pi / 3))
    # two along the aisle, fallen: one leaning on another, one lying (walk along it)
    R.placed = placed


def hollow_pencil(R):
    cx, cy = SC
    a0 = -math.pi / 6                          # faces: face 0 looks east
    gap = [(0, 0.24, 0.76, 0.0, 1.28)]           # the slot in the rubber, facing the wall
    hex_shell(R, cx, cy, SR * 0.97, ST, 0.0, 1.3, outer='oxblood', inner='oak', a0=a0, gaps=gap)
    hex_shell(R, cx, cy, SR * 1.0, ST, 1.3, 2.4, outer='brass', inner='oak', a0=a0)
    hex_shell(R, cx, cy, SR, ST, 2.4, STOP, outer='gilt', inner='oak', a0=a0)
    # the crown: the wood where the point snapped, splintered, as a parapet round the nest
    for k, hh in enumerate((1.05, 1.5, 0.98, 1.3, 1.1, 1.62)):
        hex_shell(R, cx, cy, SR, ST, STOP, STOP + hh, outer='oak', inner='oak', a0=a0, faces=(k,))
    # a painted scallop where the sharpener began
    R.nocol.add(cone(cx, cy, STOP - 0.02, STOP + 0.25, SR * 1.005, SR * 0.87, 6, side='gilt', top='gilt', bottom='gilt', a0=a0))
    # the newel and the stair winding up inside
    R.parts.add(cyl(cx, cy, 0.0, STOP + 1.0, 0.35, 12, side='walnut', top='brass'))
    turns = STOP / RISE
    a1 = HA0 + 2 * math.pi * turns
    ri, ro = 0.35, SR * math.cos(math.pi / 6) - ST - 0.02
    R.parts.add(spiral_band(cx, cy, HA0, a1, ri, ro, 0.02, STOP, int(36 * turns), top='oak', side='walnut', bottom='walnut', thick=0.3))
    # the nest: a landing sector at the top, railed where it ends over the stair
    la = math.radians(62)
    R.parts.add(spiral_band(cx, cy, a1, a1 + la, ri, ro + 0.2, STOP, STOP, 8, top='walnut', side='walnut', bottom='walnut', thick=0.3))
    e = a1 + la - 0.02
    rail(R, cx + (ri + 0.05) * math.cos(e), cy + (ri + 0.05) * math.sin(e), cx + (ro + 0.25) * math.cos(e), cy + (ro + 0.25) * math.sin(e), STOP)
    # a lamp on the newel's head, candles up the walls, a stool and a note in the nest
    R.light(sphere(cx, cy, STOP + 1.15, 0.12, 8, 4, 'e_lamp'))
    for k in range(8):
        a = HA0 + 0.3 + k * 2 * math.pi * 0.52
        z = min(STOP - 0.5, (a - HA0) / (2 * math.pi) * RISE + 1.6)
        rr = SR * math.cos(math.pi / 6) - ST - 0.04
        R.light(sphere(cx + rr * math.cos(a), cy + rr * math.sin(a), z, 0.06, 6, 3, 'e_candle'))
    am = a1 + la / 2
    mx, my = cx + 1.05 * math.cos(am), cy + 1.05 * math.sin(am)
    R.spot('plaque', mx, my, STOP)
    R.light(sphere(cx + 0.5, cy - 0.2, 0.2, 0.08, 6, 3, 'e_candle'))
    secret(R, mx, my, STOP, 'The Crow\'s Nest',
           'Inside the pencil with the broken point, a stair; at the top, the splintered crown, and the points of all the others around you like a sea of spires. Someone has carved initials in the wood.', r=1.6)


def shavings(R, rnd):
    placed = R.placed
    n = 0
    tries = 0
    while n < 150 and tries < 5000:
        tries += 1
        # drifts: round the pencil feet and along the edges of the aisle
        if rnd.random() < 0.6:
            qx, qy, qr = placed[rnd.randrange(len(placed))]
            a = rnd.uniform(0, 2 * math.pi); d = qr + rnd.uniform(0.6, 3.2)
            x, y = qx + d * math.cos(a), qy + d * math.sin(a)
        else:
            x = rnd.choice([rnd.uniform(24.0, 27.5), rnd.uniform(36.5, 40.0)]); y = rnd.uniform(7.0, 57.0)
        if not (4.0 < x < W - 4.0 and 6.5 < y < D - 6.5): continue
        if abs(x - SC[0]) < 5 and abs(y - SC[1]) < 5 and x > SC[0]: continue
        r1 = rnd.uniform(0.6, 1.5)
        g = shaving(r1 * 0.22, r1, r1 * 0.4, rnd.uniform(3.6, 5.4), segs=6)
        rot(g, 'x', rnd.uniform(-0.5, 0.5)); rot(g, 'y', rnd.uniform(-0.3, 0.3))
        g.xform(rnd.uniform(0, 2 * math.pi), x, y, rnd.uniform(-0.12, 0.05))
        R.nocol.add(g)
        n += 1


def nav(R):
    g = 1.6
    gal = [R.navpt(x, y, GZ) for (x, y) in ((g, g), (W - g, g), (W - g, D - g), (g, D - g))]
    R.link(*gal, gal[0])
    aisle = [R.navpt(x, y) for (x, y) in ((29.0, 8.0), (35.0, 8.0), (35.0, 56.0), (29.0, 56.0))]
    R.link(*aisle, aisle[0])
    edge = [R.navpt(x, y) for (x, y) in ((6.0, 8.0), (6.0, 56.0))]
    R.link(aisle[0], edge[0], edge[1], aisle[3])
