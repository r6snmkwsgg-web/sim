"""The Ant Galleries: the north wall of an ordinary reading room is honeycombed with hundreds of lit
libraries the size of matchboxes, each with its own shelves, desk and green lamp. One of the niches at
the foot of the wall is the size of a person. Behind it, a narrow workshop inside the wall where
somebody sat and made them."""
from lib import *
from kit_h2 import *

YW = 12.0          # the hall's north face (the honeycomb starts here)
HD = 0.5           # depth of the little rooms
YB = YW + HD       # their back wall
CW, RH = 0.5, 0.42 # cell width and storey height
Z0 = 0.62          # top of the plinth: the first storey's floor
NX0, NX1 = 1.9, 2.9    # the person-sized niche
SR = (0.7, 6.1, YB + 0.4, 15.35)   # the workshop behind the wall
SH = 3.0


def slab(R, x0, x1, yb, z, h, depth):
    """A row of books standing against a back wall at y=yb, facing -y (the hall)."""
    R.slabs.append({'o': [x1, yb - depth, z], 'u': [-(x1 - x0), 0, 0], 'v': [0, 0, h], 'n': [0, -1, 0],
                    'len': x1 - x0, 'h': h, 'depth': depth - 0.01, 'ghost': False})


def make():
    R = Room('antgalleries', 1, 1, res=1024)
    H = 7.5
    shell(R, y1=YW, h=H, wall='tile', floor='floor', ceil='plaster')
    # the honeycomb band: the little rooms are cut this deep into the north wall
    R.cut(box(T - 0.02, YW - 0.05, 0, C - T + 0.02, YB, H, 'walnut', bottom='floor', top='plaster'))
    honeycomb(R, H)
    workshop(R)
    hall(R, H)
    return tidy(R)


def honeycomb(R, H):
    rnd = random.Random(14)
    ncol = int((C - 2 * T - 0.16) / CW)
    xs0 = (C - ncol * CW) / 2
    nrow = int((H - 0.2 - Z0) / RH)
    door = (6.25, 9.75, 4.45)                     # keep clear of the doorway arch (x0, x1, z top)
    nz = 2.1
    # the plinth, a stone surround for the doorway, and one for the big niche
    R.parts.add(box(T, YW - 0.12, 0, NX0 - 0.05, YB, Z0, 'tile', skip=('-z', '+y')))
    R.parts.add(box(NX1 + 0.05, YW - 0.12, 0, door[0], YB, Z0, 'tile', skip=('-z', '+y')))
    R.parts.add(box(door[1], YW - 0.12, 0, C - T, YB, Z0, 'tile', skip=('-z', '+y')))
    R.parts.add(box(door[0] - 0.06, YW - 0.12, 0, door[0] + 0.25, YB, door[2], 'tile', skip=('-z', '+y')))
    R.parts.add(box(door[1] - 0.25, YW - 0.12, 0, door[1] + 0.06, YB, door[2], 'tile', skip=('-z', '+y')))
    R.parts.add(box(door[0] - 0.06, YW - 0.12, 4.1, door[1] + 0.06, YB, door[2] + 0.2, 'tile', skip=('+y',)))
    R.parts.add(box(NX0 - 0.12, YW - 0.12, 0, NX0, YB, nz + 0.1, 'tile', skip=('-z', '+y')))
    R.parts.add(box(NX1, YW - 0.12, 0, NX1 + 0.12, YB, nz + 0.1, 'tile', skip=('-z', '+y')))
    R.parts.add(box(NX0 - 0.12, YW - 0.12, nz, NX1 + 0.12, YB, nz + 0.16, 'tile', skip=('+y',)))

    def blocked(x0, x1, z0, z1):
        if x1 > door[0] - 0.06 and x0 < door[1] + 0.06 and z0 < door[2] + 0.2: return True
        if x1 > NX0 - 0.12 and x0 < NX1 + 0.12 and z0 < nz + 0.16: return True
        return False

    cells = [(c, r) for r in range(nrow) for c in range(ncol)
             if not blocked(xs0 + c * CW, xs0 + (c + 1) * CW, Z0 + r * RH, Z0 + (r + 1) * RH)]
    live = set(cells)
    # the front: one lattice of walnut bars (dividers, floor edges, a lintel over each little room)
    xs = []
    for c in range(ncol + 1):
        x = xs0 + c * CW; xs += [x - 0.025, x + 0.025]
    zs = []
    for r in range(nrow + 1):
        z = Z0 + r * RH; zs += [z - 0.05, z] + ([z + RH - 0.13] if r < nrow else [])

    def hole(i, j):
        # which cell does this lattice piece border? bars belong to any live cell next to them
        c = (i - 1) // 2 if i % 2 == 1 else None          # odd x-interval: inside column c
        r, part = j // 3, j % 3                              # 0: floor bar, 1: opening, 2: lintel
        if c is not None and part == 1: return True          # the opening itself
        cs = [c] if c is not None else [i // 2 - 1, i // 2]
        rs = [r] if part else [r - 1, r]
        return not any((cc, rr) in live for cc in cs for rr in rs)
    R.parts.add(lattice(xs, zs, hole, YW - 0.07, 'walnut'))
    fr = Geo(); inner = Geo(); lamps = Geo()
    # dividers (their two sides), and the floor plates (top: a red carpet; underside: the ceiling below)
    for (c, r) in cells:
        z = Z0 + r * RH
        for cc in (c, c + 1):
            if cc == c + 1 and (c + 1, r) in live: continue
            x = xs0 + cc * CW
            fr.add(box(x - 0.025, YW - 0.07, z, x + 0.025, YB, z + RH - 0.05, 'walnut', skip=('+y', '-y', '-z', '+z')))
    for r in range(nrow + 1):
        z = Z0 + r * RH
        run = None
        for c in range(ncol + 1):
            on = c < ncol and (((c, r) in live) or ((c, r - 1) in live))
            if on and run is None: run = c
            if not on and run is not None:
                xa, xb = xs0 + run * CW - 0.025, xs0 + c * CW + 0.025
                below = any((k, r - 1) in live for k in range(run, c)); above = any((k, r) in live for k in range(run, c))
                sk = ('+y', '-y', '-x', '+x') + (() if above else ('+z',)) + (() if below else ('-z',))
                fr.add(box(xa, YW - 0.07, z - 0.05, xb, YB, z, 'plaster', top='carpet', skip=sk))
                if above:   # the little rooms' shelf board, one long piece behind the dividers
                    fr.add(box(xa, YB - 0.08, z + 0.135, xb, YB, z + 0.15, 'walnut', skip=('+y', '-x', '+x', '-z')))
                run = None
    for (c, r) in cells:
        x0 = xs0 + c * CW; x1 = x0 + CW; z = Z0 + r * RH
        kind = rnd.random()
        slab(R, x0 + 0.04, x1 - 0.04, YB, z + 0.005, 0.125, 0.07)
        if kind < 0.5:
            slab(R, x0 + 0.04, x1 - 0.04, YB, z + 0.155, 0.1, 0.07)
        dx = x0 + 0.12 + rnd.random() * 0.2
        dy = YB - 0.26 - rnd.random() * 0.06
        inner.add(box(dx - 0.07, dy - 0.035, z, dx + 0.07, dy + 0.035, z + 0.075, 'walnut', skip=('-z', '+y', '-x', '+x')))
        if kind < 0.85:
            lamps.add(box(dx + 0.025, dy - 0.01, z + 0.105, dx + 0.055, dy + 0.01, z + 0.115, 'e_fluor', skip=('-z',)))
            inner.add(box(dx + 0.022, dy - 0.014, z + 0.115, dx + 0.058, dy + 0.014, z + 0.125, 'green', skip=('-z', '-x', '+x', '+y')))
        else:   # a hanging bulb instead, brighter
            lamps.add(box(x0 + 0.235, YB - 0.2, z + RH - 0.17, x0 + 0.265, YB - 0.17, z + RH - 0.14, 'e_lamp'))
    R.parts.add(fr)
    R.nocol.add(inner)
    R.light(lamps)
    # a rolling ladder on a brass rail, left against the wall as if for the people who live there
    R.parts.add(box(T, YW - 0.2, 6.6, C - T, YW - 0.16, 6.64, 'brass', skip=('+y',)))
    R.nocol.add(ladder(12.3, YW - 0.2, -math.pi / 2, h=6.6, lean=1.6))


def workshop(R):
    """Behind the big niche: a passage, then a slot of a room inside the wall, the maker's bench."""
    x0, x1, y0, y1 = SR
    # the niche and its short passage
    R.cut(box(NX0, YW - 0.2, 0, NX1, y0 + 0.05, 2.1, 'walnut', bottom='floor', top='walnut'))
    R.cut(box(x0, y0, 0, x1, y1, SH, 'plaster', bottom='floor', top='walnut'))
    # beams
    for k in range(5):
        x = x0 + 0.5 + k * 1.2
        R.nocol.add(box(x - 0.07, y0, SH - 0.16, x + 0.07, y1, SH, 'walnut'))
    # the bench along the back, with a lamp, a magnifier, and half-made rooms
    R.parts.add(box(x0 + 1.4, y1 - 0.75, 0.86, x1 - 0.2, y1, 0.92, 'oak', sides='walnut'))
    for x in (x0 + 1.5, x1 - 0.3):
        R.parts.add(box(x - 0.04, y1 - 0.7, 0, x + 0.04, y1 - 0.05, 0.86, 'walnut'))
    green_lamp(R, x1 - 0.7, y1 - 0.35, 0.92, 0.0)
    rnd = random.Random(3)
    for k in range(5):   # little rooms under construction: open boxes with a floor of red carpet
        bx = x0 + 1.8 + k * 0.62; by = y1 - 0.45
        R.nocol.add(box(bx - 0.25, by - 0.2, 0.92, bx + 0.25, by + 0.2, 0.935, 'carpet', sides='walnut'))
        R.nocol.add(box(bx - 0.25, by + 0.18, 0.935, bx + 0.25, by + 0.2, 1.3, 'walnut'))
        if k % 2 == 0: R.nocol.add(box(bx - 0.25, by - 0.2, 0.935, bx - 0.23, by + 0.2, 1.3, 'walnut'))
        if k != 3:
            slab(R, bx - 0.2, bx + 0.2, by + 0.18, 0.94, 0.13, 0.07)
    # a magnifying glass on an arm
    R.nocol.add(box(x0 + 2.4, y1 - 0.2, 0.92, x0 + 2.44, y1 - 0.16, 1.5, 'brass'))
    R.nocol.add(ring(x0 + 2.42, y1 - 0.5, 1.48, 1.5, 0.14, 0.17, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
    # a stool, a candle, shelves of spare furniture, a cot
    seat(R, x0 + 3.2, y1 - 1.0, math.pi / 2)
    R.parts.add(box(x0 + 0.1, y0 + 0.1, 0, x0 + 0.95, y1 - 0.1, 0.35, 'bed', sides='walnut'))
    R.nocol.add(box(x0 + 0.15, y1 - 0.5, 0.35, x0 + 0.9, y1 - 0.15, 0.45, 'ivory'))
    candle(R, x1 - 0.35, y0 + 0.2, 0.0, h=0.2, stand=0.8)
    sh(R, '+y', y0, x0 + 1.6, x1 - 0.2, z=1.6, rows=2, frame='walnut', depth=0.22)
    bulb(R, x0 + 3.0, (y0 + y1) / 2, 2.3, r=0.09, m='e_lamp', top=SH)
    bulb(R, x0 + 0.8, (y0 + y1) / 2, 2.4, r=0.07, m='e_dim', top=SH)
    R.spot('plaque', x0 + 3.0, y1 - 0.4, 0.92, -math.pi / 2)
    secret(R, x0 + 3.0, (y0 + y1) / 2, 0.0, 'The Maker\'s Bench',
           'A bench, a lamp, a magnifying glass and a row of rooms not yet finished. Somebody has spent a very long time building places too small to go into.', r=1.8)
    loop_ = [R.navpt(NX0 + 0.5, YW - 1.0), R.navpt(NX0 + 0.5, y0 + 0.3), R.navpt(x0 + 2.2, 14.0)]
    R.link(*loop_)


def hall(R, H):
    rows = 14
    sh(R, '+y', T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '+y', T, 9.9, C - 0.5, rows=rows, frame='walnut')
    sh(R, '+x', T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '+x', T, 9.9, YW - 0.2, rows=rows, frame='walnut')
    sh(R, '-x', C - T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '-x', C - T, 9.9, YW - 0.2, rows=rows, frame='walnut')
    sh(R, '+y', T, 6.1, 9.9, z=4.35, rows=7, frame='walnut')
    # a long table facing the wall, with a lamp and a magnifying glass on a stand
    R.parts.add(table(4.5, 7.6, 11.5, 8.6, 0.78, 'walnut', top='leather'))
    desk_lamp(R, 5.6, 8.1, 0.78); desk_lamp(R, 10.4, 8.1, 0.78)
    for x in (6.2, 8.0, 9.8):
        R.parts.add(chair(x, 7.05, math.pi / 2))
        R.spot('sit', x, 7.05, 0.48, math.pi / 2)
    open_book_prop(R, 8.0, 8.1, 0.78)
    # the big magnifier on its brass stand, turned to the wall
    mx, my = 13.2, 10.2
    R.parts.add(cyl(mx, my, 0, 0.05, 0.3, 12, side='brass', top='brass'))
    R.parts.add(cyl(mx, my, 0.05, 1.5, 0.03, 6, side='brass', caps=False))
    lens = Geo()
    lens.add(ring(0, 0, -0.03, 0.03, 0.34, 0.4, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    rot(lens, 'x', math.pi / 2)
    lens.xform(0.0, mx, my + 0.05, 1.85)
    R.nocol.add(lens)
    R.nocol.add(box(mx - 0.02, my + 0.02, 1.45, mx + 0.02, my + 0.06, 1.5, 'brass'))
    # dim room light: let the wall glow
    for (x, y) in ((4.0, 4.0), (12.0, 4.0), (8.0, 9.3)):
        bulb(R, x, y, 4.6, r=0.14, m='e_dim', top=H)
    for (x, y) in ((1.4, 11.0), (C - 1.4, 11.0)):
        R.nocol.add(cyl(x, y, 0, 1.2, 0.02, 6, side='brass', caps=False))
        R.nocol.add(cyl(x, y, 0, 0.03, 0.16, 10, side='brass', top='brass'))
        R.col.add(box(x - 0.1, y - 0.1, 0, x + 0.1, y + 0.1, 1.2, 'tile'))
        R.light(sphere(x, y, 1.3, 0.1, 10, 5, 'e_amber'))
    navloop(R, [(2.0, 2.0), (8, 2.0), (C - 2.0, 2.0), (C - 2.0, 6.0), (C - 2.0, 11.0), (8, 11.0), (2.4, 11.0), (2.0, 6.0)])
    R.spot('probe', 8, 10.3, 1.7)
    R.meta.update(label='The Ant Galleries', weight=4,
                  blurb='The north wall is full of libraries, hundreds of them, each the size of a shoebox and each with its lamp lit. Nobody could read in any of them. Somebody keeps them dusted.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
