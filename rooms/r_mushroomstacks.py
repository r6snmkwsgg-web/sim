"""The Mushroom Stacks: dark aisles of damp bookcases where blue mushrooms grow out of the shelves and
light the way. In the middle, a ring of giant ones with their caps grown together; under them, a hollow."""
from kit_h5 import *

W = D = 2 * C
H = TOP - 0.1
GX, GY = 16.0, 16.0          # the grove
RW0, RW1 = 3.0, 3.35        # the fused ring of stalks
EA = -math.pi * 0.75         # the crawl gap in the ring: toward the south-west
CRAWL = 1.3


def make():
    R = Room('mushroomstacks', 2, 2, res=2048)
    rng = random.Random(36)
    R.sockets(floor='slate', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'slate', bottom='slate', top='slate'))
    # beams across the ceiling, and stone piers at the aisle crossings
    for k in range(9):
        y = 1.9 + k * 3.53
        R.nocol.add(box(T, y - 0.14, H - 0.45, W - T, y + 0.14, H, 'walnut'))
    for x in (6.0, 10.0, 22.0, 26.0):
        for y in (6.0, 10.0, 22.0, 26.0):
            if 10.0 < x < 22.0 and 10.0 < y < 22.0: continue
            R.parts.add(cyl(x, y, 0, H, 0.42, 16, side='slate', caps=False))
            R.parts.add(box(x - 0.55, y - 0.55, 0, x + 0.55, y + 0.55, 0.4, 'slate', skip=('-z',)))
            R.parts.add(box(x - 0.55, y - 0.55, H - 0.9, x + 0.55, y + 0.55, H, 'slate', skip=('+z',)))
    slabs = []
    rows = 12
    # --- the stacks: long double-sided cases in the blocks between the aisles
    # blocks north and south of the grove: cases running north-south
    for (y0, y1) in ((T + 0.2, 5.6), (26.4, D - T - 0.2)):
        for xc in (12.6, 16.0, 19.4):
            slabs += stack2(R, 'y', xc, y0, y1, rows)
    # blocks west and east of the grove: cases running east-west
    for (x0, x1) in ((T + 0.02, 5.6), (26.4, W - T - 0.02)):
        for yc in (12.6, 16.0, 19.4):
            slabs += stack2(R, 'x', yc, x0, x1, rows)
    # corner blocks: books on the two outer walls, a lectern in the corner
    for (cx, cy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        xa, xb = (T, 5.4) if cx == 0 else (26.6, W - T)
        ya, yb = (T, 5.4) if cy == 0 else (26.6, D - T)
        if cy == 0: slabs += sh(R, '+y', T, xa + 0.4, xb - 0.4, rows=rows, frame='walnut')
        else: slabs += sh(R, '-y', D - T, xa + 0.4, xb - 0.4, rows=rows, frame='walnut')
        if cx == 0: slabs += sh(R, '+x', T, ya + 0.8, yb - 0.4, rows=rows, frame='walnut')
        else: slabs += sh(R, '-x', W - T, ya + 0.8, yb - 0.4, rows=rows, frame='walnut')
    # the grove's own low cases, round its square, open at the middle of each side
    low = []
    for (a, b) in ((10.9, 14.3), (17.7, 21.1)):
        low += sh(R, '-y', 10.9, a, b, rows=5, frame='walnut')
        low += sh(R, '+y', 21.1, a, b, rows=5, frame='walnut')
        low += sh(R, '-x', 10.9, a, b, rows=5, frame='walnut')
        low += sh(R, '+x', 21.1, a, b, rows=5, frame='walnut')
    shrooms_on_slabs(R, slabs, rng, per=0.3)
    shrooms_on_slabs(R, low, rng, per=0.7, big=0.12)
    # bracket fungi up the ends of the stacks, and big ones on the floor at their feet
    for (x, y, a) in stack_ends():
        for k in range(rng.randint(2, 5)):
            z = rng.uniform(0.6, 4.6); rr = rng.uniform(0.12, 0.3)
            R.light(ring(x, y, z, z + 0.05, 0.02, rr, 10, top='e_blue', bottom='e_blue', inner='e_blue', outer='e_blue', a0=a - 1.2, a1=a + 1.2))
        for k in range(rng.randint(1, 3)):
            d = rng.uniform(0.15, 0.5); b_ = a + rng.uniform(-0.9, 0.9)
            mushroom(R, x + math.cos(b_) * d, y + math.sin(b_) * d, 0, rng.uniform(0.25, 0.7), rng.uniform(0.12, 0.28),
                     lean=rng.uniform(0.0, 0.3), lean_dir=b_, segs=8, gills='ivory')
    # moss hanging from the high shelves
    for i in rng.sample(slabs, 40):
        s = R.slabs[i]; o, u, n = s['o'], s['u'], s['n']
        t = rng.uniform(0.1, 0.9)
        vine(R, o[0] + u[0] * t + n[0] * 0.04, o[1] + u[1] * t + n[1] * 0.04, max(0.3, o[2] - rng.uniform(0.6, 1.6)), o[2] + 0.02, rng, m='damask', w=0.03)
    # puddles in the aisles
    for (x0, y0, x1, y1) in ((6.9, 3.0, 8.6, 5.1), (23.2, 13.0, 25.1, 15.9), (12.0, 7.1, 15.4, 8.9), (18.0, 23.2, 20.2, 24.6),
                             (7.4, 17.5, 9.0, 20.5), (27.0, 7.3, 29.0, 8.7), (23.4, 27.5, 24.6, 29.8)):
        R.cut(box(x0, y0, -0.07, x1, y1, 0.3, 'slate', top='slate'))
        R.water.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, top=-0.015, bot=-0.07))
    # green lamps on lecterns down the main aisles, dim; amber lanterns that stay lit
    for (x, y) in ((6.7, 14.0), (9.3, 18.0), (22.7, 18.0), (25.3, 14.0), (14.0, 6.7), (18.0, 9.3), (14.0, 25.3), (18.0, 22.7),
                   (3.0, 3.0), (29.0, 3.0), (3.0, 29.0), (29.0, 29.0)):
        lectern_lamp(R, x, y)
    for (x, y) in ((8.0, 8.0), (24.0, 8.0), (8.0, 24.0), (24.0, 24.0)):
        R.nocol.add(cyl(x, y, 4.2, H - 0.45, 0.01, 4, side='iron', caps=False))
        lantern(R, x, y, 3.9, s=1.6)
    grove(R, rng)
    # walking
    navloop(R, [(8, 2.5), (8, 8), (8, 16), (8, 24), (8, 29.5), (24, 29.5), (24, 24), (24, 16), (24, 8), (24, 2.5)])
    a = R.navpt(2.5, 8); b = R.navpt(29.5, 8); c = R.navpt(2.5, 24); d = R.navpt(29.5, 24)
    R.link(a, 1); R.link(8, b); R.link(c, 3); R.link(6, d); R.link(1, 8); R.link(3, 6)
    e = R.navpt(16, 8.0); f = R.navpt(16, 11.4); R.link(e, f)
    R.spot('probe', 16, 8, 2.2)
    R.meta.update(label='The Mushroom Stacks', weight=4,
                  blurb='The shelves are damp and something has taken root in them. The mushrooms give off just enough light to read by, and they are growing toward the books.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    fx(R, 'dust', [T, 0, T, W - T, H - 0.5, D - T])
    fx(R, 'fog', [T, 0, T, W - T, 1.2, D - T], density=0.04)
    return tidy(R)


def stack2(R, axis, c, a, b, rows):
    ids = []
    if axis == 'y':
        ids += sh(R, '+x', c + 0.01, a, b, rows=rows, frame='walnut')
        ids += sh(R, '-x', c - 0.01, a, b, rows=rows, frame='walnut')
    else:
        ids += sh(R, '+y', c + 0.01, a, b, rows=rows, frame='walnut')
        ids += sh(R, '-y', c - 0.01, a, b, rows=rows, frame='walnut')
    return ids


def stack_ends():
    out = []
    for xc in (12.6, 16.0, 19.4):
        out += [(xc, 5.65, math.pi / 2), (xc, 26.35, -math.pi / 2)]
    for yc in (12.6, 16.0, 19.4):
        out += [(5.65, yc, 0.0), (26.35, yc, math.pi)]
    return out


def grove(R, rng):
    """The ring of giant mushrooms. Their stalks have fused into a wall; their caps into one roof. One
    low gap, behind small mushrooms, lets you crawl into the hollow underneath."""
    gap = 0.34                                  # radians of the crawl gap
    # moss floor
    R.nocol.add(hdisc(GX, GY, 0.01, 5.2, 24, 'damask'))
    # the fused wall: a ring, open at the gap; over the gap a lintel at crawl height
    R.parts.add(ring(GX, GY, 0, 3.1, RW0, RW1, 40, top='ivory', bottom='ivory', inner='ivory', outer='ivory', a0=EA + gap / 2, a1=EA + 2 * math.pi - gap / 2))
    R.parts.add(ring(GX, GY, CRAWL, 3.1, RW0, RW1, 4, top='ivory', bottom='ivory', inner='ivory', outer='ivory', a0=EA - gap / 2, a1=EA + gap / 2))
    # the giant stalks standing out of the wall, and their caps grown together overhead
    n = 7
    for k in range(n):
        a = EA + math.pi / n + 2 * math.pi * k / n
        sx, sy = GX + math.cos(a) * 3.2, GY + math.sin(a) * 3.2
        top = 4.3 + 0.9 * math.sin(k * 2.1)
        R.parts.add(cone(sx, sy, 0, top, 0.62, 0.45, 12, 'ivory'))
        cr = 2.7 + 0.4 * math.cos(k * 1.7)
        cx, cy = GX + math.cos(a) * 3.6, GY + math.sin(a) * 3.6
        R.nocol.add(blob(cx, cy, top - 0.1, cr, cr, 1.3, 14, 4, 'ivory', lower=False))
        R.light(ring(cx, cy, top - 0.16, top - 0.13, cr * 0.9, cr * 0.97, 14, top='e_blue', bottom='e_blue', inner='e_blue', outer='e_blue'))
        for j in range(9):   # glowing spots on the cap
            b = 2 * math.pi * j / 9 + k
            d = cr * (0.35 + 0.4 * ((j * 7) % 5) / 5)
            e = math.sqrt(max(0.0, 1 - (d / cr) ** 2))
            R.light(blob(cx + math.cos(b) * d, cy + math.sin(b) * d, top - 0.1 + 1.3 * e, 0.16, 0.16, 0.06, 6, 2, 'e_blue'))
        R.nocol.add(hdisc(cx, cy, top - 0.12, cr * 0.97, 14, 'ivory', up=False))
        # gill ridges under the cap
        for j in range(10):
            b = 2 * math.pi * j / 10
            R.nocol.add(beam((cx, cy, top - 0.35), (cx + math.cos(b) * cr * 0.9, cy + math.sin(b) * cr * 0.9, top - 0.2), 0.04, 'bed', 0.18))
    # the roof over the hollow: a low dome of cap flesh under the ring of caps
    R.parts.add(cone(GX, GY, 3.1, 3.5, RW1 + 0.05, 1.5, 24, 'ivory', bottom='bed'))
    R.nocol.add(blob(GX, GY, 4.0, 2.8, 2.8, 1.9, 16, 4, 'ivory', lower=False))
    # small mushrooms crowding the gap from outside, so it reads as a clump, not a door
    gx, gy = GX + math.cos(EA) * 3.9, GY + math.sin(EA) * 3.9
    for (d, s, hh, rr) in ((-1.0, 1, 0.9, 0.35), (1.0, 1, 1.1, 0.4), (-0.6, 1.4, 0.55, 0.22), (0.7, 1.3, 0.6, 0.25), (-1.5, 0.6, 0.5, 0.2), (1.5, 0.7, 0.7, 0.25)):
        ux, uy = -math.sin(EA), math.cos(EA)
        px, py = gx + ux * d + math.cos(EA) * (s - 1) * 0.6, gy + uy * d + math.sin(EA) * (s - 1) * 0.6
        mushroom(R, px, py, 0, hh, rr, lean=0.2, lean_dir=EA + d * 0.3, segs=10, gills='ivory')
        R.col.add(cyl(px, py, 0, hh, 0.07, 6))
    # inside: a bed of moss, a stump with an open book, a candle, and more light
    R.parts.add(box(GX + 0.2, GY - 1.2, 0, GX + 2.2, GY + 0.1, 0.35, 'damask', top='green'))
    R.spot('bed', GX + 1.2, GY - 0.55, 0.35, math.pi / 2)
    R.parts.add(cyl(GX - 1.1, GY + 0.9, 0, 0.7, 0.4, 12, side='wood', top='oak'))
    ob = open_book(0.2, 0.28, 0.2, 'green'); orient(ob, 0.4, 0, 0, GX - 1.1, GY + 0.9, 0.72)
    R.nocol.add(ob)
    candle(R, GX - 0.8, GY + 1.1, 0.7, h=0.12)
    R.spot('read', GX - 1.1, GY + 0.1, 0, math.pi / 2)
    R.spot('plaque', GX - 1.1, GY + 0.9, 0.72)
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.3
        if abs(math.remainder(a - EA, 2 * math.pi)) < 0.5: continue
        mushroom(R, GX + math.cos(a) * 2.7, GY + math.sin(a) * 2.7, 0, 0.3 + 0.2 * (k % 3), 0.12 + 0.05 * (k % 2), lean=0.25, lean_dir=a + math.pi, segs=8)
    R.light(sphere(GX, GY, 2.9, 0.12, 8, 4, 'e_amber'))
    secret(R, GX, GY, 0, 'The Hollow Under the Caps',
           'You crawl under the gills and stand up inside the ring. Somebody has been sleeping here, and the mushrooms have been reading over their shoulder.', r=2.2)
