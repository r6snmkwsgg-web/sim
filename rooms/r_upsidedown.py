"""The Upside-Down Reading Room: fifteen metres up, the parquet ceiling is where the furniture is: rugs,
long reading tables with their chairs and green lamps, bookcases, all hanging the wrong way, and the
books hanging with them. Down here on the plaster floor the chandeliers stand up on their chains and
their candles burn downward. A strip of black glass down the middle shows the ceiling the right way up.
The tallest chandelier's stem is a spiral of brass rungs: it climbs all the way to a bookcase on the
east wall that is not a bookcase but a room, the one place in the hall that is the right way up."""
from kit_h8 import *

W = D = 32.0
CT = 15.2                         # the ceiling (the upside-down floor)
ZC = CT / 2                       # flip about this plane
SX, SY = 26.5, 22.5               # the secret chandelier
HR0, HR1, HW = 0.12, 1.1, 1.18    # its helix: stem radius, outer radius, cage radius
NZ = 11.2                         # the niche floor
NX0, NY0, NY1 = 28.4, 20.0, 25.0  # the niche: x NX0..W-T, y NY0..NY1


def make():
    R = Room('upsidedown', 2, 2, levels=2, res=2048)
    skip = [(s, i, 1) for s in 'SNWE' for i in range(2)]
    seal(R, skip, floor='plaster', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, CT, 'tile', bottom='plaster', top='floor'))
    windows(R)
    ceiling_world(R)
    wall_books(R)
    chandeliers(R)
    secret_stem(R)
    niche(R)
    # the black glass down the middle
    R.parts.add(box(5.0, 13.2, 0, 27.0, 18.8, 0.01, 'black'))
    for (x0, y0, x1, y1) in ((4.9, 13.1, 27.1, 13.2), (4.9, 18.8, 27.1, 18.9), (4.9, 13.2, 5.0, 18.8), (27.0, 13.2, 27.1, 18.8)):
        R.parts.add(box(x0, y0, 0, x1, y1, 0.012, 'brass'))
    R.meta['mirrors'] = [{'c': [16.0, 13.2, 0.012], 'n': [0, 0, 1], 'up': [0, 1, 0], 'w': 22.0, 'h': 5.6}]
    g = navloop(R, [(3, 4), (16, 4), (29.2, 4), (29.2, 28), (16, 28), (3, 28)])
    a, b = R.navpt(11, 16), R.navpt(21, 16)
    R.link(g[1], a, g[4]); R.link(a, b); R.link(g[1], b, g[4])
    fx(R, 'dust', [4, 4, 6, 28, 28, 14])
    secret(R, 30.0, 22.5, NZ, 'The Right Way Up',
           'You climb the chandelier into a bookcase and come out standing on a floor, under a ceiling, with a lamp that shines down. After the hall it is almost too much.')
    return finish(R, 'The Upside-Down Reading Room', weight=3, probe=(16, 10, 5.0), top=CT,
                  blurb='The reading room is on the ceiling, and nothing has fallen off it. You are the only thing in here the wrong way up.')


# ---------------------------------------------------------------------------
def inverted(R, fn):
    """Build something the right way up on the floor (z = 0) with fn(), then hang it from the ceiling."""
    saved = (R.parts, R.nocol, R.col, R.emit)
    R.parts, R.nocol, R.col, R.emit = Geo(), Geo(), Geo(), Geo()
    n0, s0 = len(R.slabs), len(R.spots)
    fn()
    g = Geo(); g.add(R.parts); g.add(R.nocol)
    e = R.emit
    R.parts, R.nocol, R.col, R.emit = saved
    R.nocol.add(flipz(g, ZC)); R.emit.add(flipz(e, ZC))
    for s in R.slabs[n0:]:
        o = list(s['o']); o[2] = 2 * ZC - o[2] - s['v'][2]; s['o'] = o
    del R.spots[s0:]


def windows(R):
    """Tall windows in the lower walls, their arches at the bottom."""
    w, z0, z1 = 3.2, 1.0, 7.0
    r = w / 2
    pr = [(-r, z1), (r, z1), (r, z0 + r)]
    for k in range(1, 12):
        t = math.pi * k / 12
        pr.append((r * math.cos(t), z0 + r - r * math.sin(t)))
    pr.append((-r, z0 + r))
    pr = pr[::-1]
    for (side, c) in (('S', 16.0), ('N', 16.0), ('W', 16.0), ('E', 16.0)):
        if side in 'SN':
            y0, y1 = (T - 0.3, T + 0.02) if side == 'S' else (D - T - 0.02, D - T + 0.3)
            R.cut(prism([(c + p, q) for p, q in pr], 'y', y0, y1, 'tile', cap='tile'))
            yb = T - 0.28 if side == 'S' else D - T + 0.28
            g = poly_plate_y([(c + p, q) for p, q in pr], yb, side == 'S')
            R.light(g)
            for k in (-1, 0, 1):
                R.nocol.add(box(c + k * 0.8 - 0.03, yb - 0.04 if side == 'S' else yb, z0, c + k * 0.8 + 0.03, yb + 0.04 if side == 'S' else yb + 0.04, z1, 'iron'))
        else:
            x0, x1 = (T - 0.3, T + 0.02) if side == 'W' else (W - T - 0.02, W - T + 0.3)
            R.cut(prism([(c + p, q) for p, q in pr], 'x', x0, x1, 'tile', cap='tile'))
            xb = T - 0.28 if side == 'W' else W - T + 0.28
            R.light(poly_plate_x([(c + p, q) for p, q in pr], xb, side == 'W'))
            for k in (-1, 0, 1):
                R.nocol.add(box(xb - 0.04 if side == 'W' else xb, c + k * 0.8 - 0.03, z0, xb + 0.04 if side == 'W' else xb + 0.04, c + k * 0.8 + 0.03, z1, 'iron'))
        for zz in (2.6, 4.1, 5.6):
            if side in 'SN':
                R.nocol.add(box(c - r, yb - 0.03, zz, c + r, yb + 0.03, zz + 0.05, 'iron'))
            else:
                R.nocol.add(box(xb - 0.03, c - r, zz, xb + 0.03, c + r, zz + 0.05, 'iron'))


def poly_plate_y(pts, y, face_pos):
    g = Geo(); ids = [g.vert((p, y, q)) for p, q in pts]
    # face +y (into the room from the south wall) or -y
    g.face(ids if not face_pos else ids[::-1], 'e_skydome', [(p, q) for p, q in pts] if not face_pos else [(p, q) for p, q in pts[::-1]])
    _orient(g, (0, 1 if face_pos else -1, 0))
    return g


def poly_plate_x(pts, x, face_pos):
    g = Geo(); ids = [g.vert((x, p, q)) for p, q in pts]
    g.face(ids, 'e_skydome', [(p, q) for p, q in pts])
    _orient(g, (1 if face_pos else -1, 0, 0))
    return g


def _orient(g, want):
    f = g.f[0]; a, b, c = g.v[f[0]], g.v[f[1]], g.v[f[2]]
    u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    # use the polygon's area normal (Newell) for robustness
    nx = ny = nz = 0.0
    P = [g.v[i] for i in f]
    for i in range(len(P)):
        p, q = P[i], P[(i + 1) % len(P)]
        nx += (p[1] - q[1]) * (p[2] + q[2]); ny += (p[2] - q[2]) * (p[0] + q[0]); nz += (p[0] - q[0]) * (p[1] + q[1])
    if nx * want[0] + ny * want[1] + nz * want[2] < 0:
        g.f = [tuple(reversed(ff)) for ff in g.f]; g.uv = [list(reversed(u_)) for u_ in g.uv]


def ceiling_world(R):
    """Everything a reading room keeps on its floor, on the ceiling."""
    def build():
        # rugs
        for (x0, y0, x1, y1) in ((4.5, 5.0, 27.5, 11.5), (4.5, 20.5, 25.5, 27.0)):
            R.parts.add(box(x0, y0, 0, x1, y1, 0.02, 'carpet'))
            R.parts.add(box(x0 + 0.3, y0 + 0.3, 0.02, x1 - 0.3, y1 - 0.3, 0.025, 'velvet'))
        # four long reading tables with chairs and green lamps
        for (x0, y0) in ((6.0, 6.8), (17.0, 6.8), (6.0, 22.2), (15.5, 22.2)):
            reading_table(R, x0, y0, x0 + 8.0, y0 + 1.4, lamps=3)
            book_pile(R, x0 + 1.2, y0 + 0.5, 0.78, 5, seed=int(x0 + y0))
            open_book(R, x0 + 3.6, y0 + 0.9, 0.78, 0.2)
        # double-sided stacks down the middle, either side of the mirror line
        for x in (8.0, 16.0, 24.0):
            stack(R, 'x', 16.0, x - 2.6, x + 2.6, rows=7, frame='walnut')
        # a globe, a card catalogue, armchairs by a standard lamp
        R.parts.add(cyl(28.5, 9.0, 0, 0.8, 0.06, 8, side='brass', top='brass'))
        R.parts.add(sphere(28.5, 9.0, 1.25, 0.45, 16, 8, 'ivory'))
        R.parts.add(box(2.0, 13.0, 0, 3.2, 19.0, 1.3, 'oak', top='walnut'))
        for k in range(6):
            for j in range(3):
                R.parts.add(box(3.2, 13.1 + k, 0.2 + j * 0.38, 3.22, 13.9 + k, 0.5 + j * 0.38, 'brass'))
        armchair(R, 27.0, 14.0, math.pi)
        armchair(R, 27.0, 18.0, math.pi)
        floor_lamp(R, 28.2, 16.0, 1.7)
    inverted(R, build)


def wall_books(R):
    """Bookcases round the upper walls, hanging from the ceiling; an upside-down balustrade under them."""
    def build():
        for (a, b) in ((0.6, 7.4), (8.6, 15.4), (16.6, 23.4), (24.6, W - 0.6)):
            R.shelf(a, T, 0, b - a, '+y', rows=12, frame='walnut')
            R.shelf(b, D - T, 0, b - a, '-y', rows=12, frame='walnut')
            R.shelf(T, b, 0, b - a, '+x', rows=12, frame='walnut')
        for (a, b) in ((0.6, 7.4), (8.6, 15.4), (16.6, NY0 - 0.2), (NY1 + 0.2, W - 0.6)):
            R.shelf(W - T, a, 0, b - a, '-x', rows=12, frame='walnut')
        # the niche's front: a bookcase you can walk straight through
        R.shelf(NX0, NY0 + 0.2, 0, NY1 - NY0 - 0.4, '-x', rows=9, frame='walnut', solid=False)
    inverted(R, build)
    # the band under them: an upside-down gallery rail
    z = CT - 5.35
    e = 0.95
    for (x0, y0, x1, y1, rail) in ((T, T, W - T, e, (T, e - 0.2, W - T, e)), (T, D - e, W - T, D - T, (T, D - e, W - T, D - e + 0.2)),
                                   (T, e, e, D - e, (e - 0.2, e, e, D - e)), (W - e, e, W - T, NY0 - 0.2, (W - e, e, W - e + 0.2, NY0 - 0.2)),
                                   (W - e, NY1 + 0.2, W - T, D - e, (W - e, NY1 + 0.2, W - e + 0.2, D - e))):
        R.parts.add(box(x0, y0, z - 0.25, x1, y1, z, 'tile'))
        g = balustrade(rail[0], rail[1], rail[2], rail[3], 0, 0.9, 'tile', 'brass')
        R.nocol.add(flipz(g, (z - 0.25) / 2))


def chandelier_up(R, cx, cy, h=2.3, r=1.0, n=10):
    """A chandelier standing on its chain: a rose on the floor, the chain up, the body at the top, its
    candles hanging from the arms and burning downward."""
    R.parts.add(cyl(cx, cy, 0, 0.1, 0.35, 16, side='gilt', top='gilt'))
    R.parts.add(cyl(cx, cy, 0.1, h, 0.04, 8, side='brass', caps=False))
    for k in range(int(h / 0.25)):
        z = 0.2 + k * 0.25
        R.nocol.add(ring(cx, cy, z, z + 0.05, 0.035, 0.07, 8, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.col.add(cyl(cx, cy, 0, h, 0.3, 8))
    R.nocol.add(sphere(cx, cy, h + 0.15, 0.28, 12, 6, 'gilt'))
    R.nocol.add(cone(cx, cy, h + 0.4, h + 1.3, 0.12, 0.01, 8, m='gilt'))
    for (rr, zz, nn) in ((r, h + 0.1, n), (r * 0.6, h + 0.55, n - 4)):
        R.nocol.add(ring(cx, cy, zz - 0.03, zz + 0.03, rr - 0.04, rr + 0.04, 24, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
        for k in range(nn):
            a = 2 * math.pi * (k + 0.5 * (rr < r)) / nn
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            R.nocol.add(bar((cx, cy, h + 0.15), (x, y, zz), 0.03, 0.03, 'gilt'))
            R.nocol.add(cyl(x, y, zz - 0.06, zz, 0.05, 6, side='gilt', top='gilt', bottom='gilt'))
            R.nocol.add(cyl(x, y, zz - 0.26, zz - 0.06, 0.022, 6, side='ivory', top='ivory', bottom='ivory'))
            R.light(box(x - 0.012, y - 0.012, zz - 0.33, x + 0.012, y + 0.012, zz - 0.27, 'e_candle'))


def chandeliers(R):
    for (x, y) in ((6.0, 9.0), (16.0, 9.0), (26.0, 9.0), (6.0, 23.0), (16.0, 23.0), (SX, SY)):
        R.parts.add(ring(x, y, 0, 0.012, 1.0, 1.25, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
        R.parts.add(ring(x, y, 0, 0.008, 1.25, 1.9, 32, top='ivory', bottom='ivory', inner='ivory', outer='ivory'))
        if (x, y) != (SX, SY): chandelier_up(R, x, y)
    # paintings on the lower walls, hung upside down, their wires and nails below them
    for c in (3.6, 12.0, 20.0, 28.4):
        for side in 'SNWE':
            painting(R, side, c, 3.2)


def painting(R, side, c, z, w=1.6, h=1.2):
    g = Geo()
    g.add(box(-w / 2, 0, z, w / 2, 0.06, z + h, 'gilt'))
    g.add(box(-w / 2 + 0.12, 0.06, z + 0.12, w / 2 - 0.12, 0.07, z + h - 0.12, 'oxblood' if int(c) % 2 else 'green'))
    g.add(box(-w / 2 + 0.3, 0.07, z + 0.3, -w / 2 + 0.7, 0.075, z + 0.62, 'ivory'))
    g.add(bar((-w / 2 + 0.1, 0.03, z), (0, 0.03, z - 0.45), 0.012, 0.012, 'iron'))
    g.add(bar((w / 2 - 0.1, 0.03, z), (0, 0.03, z - 0.45), 0.012, 0.012, 'iron'))
    g.add(box(-0.03, 0.0, z - 0.5, 0.03, 0.08, z - 0.44, 'brass'))
    ang, ox, oy = {'S': (0.0, c, T), 'N': (math.pi, c, D - T), 'W': (-math.pi / 2, T, c), 'E': (math.pi / 2, W - T, c)}[side]
    g.xform(ang, ox, oy, 0)
    R.nocol.add(g)


def secret_stem(R):
    """The tall chandelier: its stem a brass cage with rungs wound round inside it, a spiral you can climb."""
    cx, cy = SX, SY
    rise = 2.4
    turns = (NZ - 0.0) / rise
    a1 = 0.0
    a0 = a1 - turns * 2 * math.pi
    # walking surface (invisible) and the rungs you see
    R.col.add(helix(cx, cy, HR0, HR1, 0.0, rise, a0, a1, thick=0.06, segs=int(turns * 40)))
    n = int(NZ / 0.2)
    for k in range(n + 1):
        t = k / n
        a = a0 + (a1 - a0) * t; z = NZ * t
        R.nocol.add(bar((cx + HR0 * math.cos(a), cy + HR0 * math.sin(a), z), (cx + HR1 * math.cos(a), cy + HR1 * math.sin(a), z), 0.06, 0.04, 'brass'))
    R.parts.add(cyl(cx, cy, 0, NZ + 1.4, HR0, 8, side='brass', caps=False))
    R.parts.add(cyl(cx, cy, 0, 0.12, HW + 0.25, 24, side='gilt', top='gilt'))
    # the cage: brass uprights and hoops; an invisible wall inside them, open where you step on and off
    for k in range(12):
        a = 2 * math.pi * k / 12
        R.nocol.add(box(cx + HW * math.cos(a) - 0.02, cy + HW * math.sin(a) - 0.02, 0.12, cx + HW * math.cos(a) + 0.02, cy + HW * math.sin(a) + 0.02, NZ + 1.3, 'brass'))
    for z in [2.2 + 1.2 * k for k in range(8)]:
        R.nocol.add(ring(cx, cy, z, z + 0.04, HW - 0.02, HW + 0.02, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    ga = (a0 % (2 * math.pi))     # the angle where the spiral starts, at the floor
    R.col.add(ring(cx, cy, 0.12, 2.2, HW - 0.02, HW + 0.02, 28, a0=ga + 1.0, a1=ga + 2 * math.pi - 0.4))
    R.col.add(ring(cx, cy, 2.2, NZ - 0.9, HW - 0.02, HW + 0.02, 32))
    R.col.add(ring(cx, cy, NZ - 0.9, NZ + 1.3, HW - 0.02, HW + 0.02, 28, a0=0.45, a1=2 * math.pi - 0.45))
    # the chandelier itself, at the top of its stem: rings of downward candles round the cage
    zz = NZ - 1.0
    for (rr, z0, nn) in ((HW + 0.9, zz, 14), (HW + 0.5, zz + 0.5, 10)):
        R.nocol.add(ring(cx, cy, z0 - 0.03, z0 + 0.03, rr - 0.05, rr + 0.05, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
        for k in range(nn):
            a = 2 * math.pi * (k + 0.5) / nn
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            R.nocol.add(bar((cx + HW * math.cos(a), cy + HW * math.sin(a), z0 + 0.4), (x, y, z0), 0.035, 0.035, 'gilt'))
            R.nocol.add(cyl(x, y, z0 - 0.26, z0 - 0.04, 0.025, 6, side='ivory', top='ivory', bottom='ivory'))
            R.light(box(x - 0.014, y - 0.014, z0 - 0.34, x + 0.014, y + 0.014, z0 - 0.27, 'e_candle'))
    # the top: a gilt rose on the stem, and a little brass bridge east into the bookcase
    R.nocol.add(cone(cx, cy, NZ + 1.4, NZ + 2.6, 0.2, 0.01, 8, m='gilt'))
    R.parts.add(box(cx + 0.35, cy - 0.55, NZ - 0.12, NX0 + 0.1, cy + 0.55, NZ, 'brass', top='oak'))
    R.col.add(ring(cx, cy, NZ - 0.1, NZ, 0.1, HR1 + 0.05, 24, a0=-0.5, a1=0.5))
    for s_ in (-1, 1):
        brass_rail(R, cx + HW + 0.02, cy + s_ * 0.55, NX0, cy + s_ * 0.55, NZ, post=0.8)


def niche(R):
    """Behind the false bookcase: a small room the right way up, on a floor, under the ceiling."""
    x0, x1, y0, y1 = NX0, W - T, NY0, NY1
    zb = NZ - 0.3
    R.parts.add(box(x0, y0, zb, x1 + 0.02, y1, NZ, 'walnut', top='floor'))
    R.parts.add(box(x0, y0 - 0.2, zb, x1 + 0.02, y0, CT, 'walnut'))
    R.parts.add(box(x0, y1, zb, x1 + 0.02, y1 + 0.2, CT, 'walnut'))
    # a closed front either side of the way in, hidden behind the false bookcase
    R.col.add(box(x0 - 0.05, y0, NZ, x0, cy_lo(), CT, 'tile'))
    R.col.add(box(x0 - 0.05, cy_hi(), NZ, x0, y1, CT, 'tile'))
    # the underside, seen from the hall: more of the hanging bookcases' dark wood, and a brass edge
    R.nocol.add(box(x0 - 0.05, y0 - 0.25, zb - 0.08, x1, y1 + 0.25, zb, 'brass'))
    # inside: the right way up
    R.parts.add(box(x0 + 0.4, y0 + 0.3, NZ, x1 - 0.3, y1 - 0.3, NZ + 0.02, 'carpet'))
    sh(R, '-x', x1, y0 + 0.3, y1 - 0.3, z=NZ, rows=8, frame='walnut')
    armchair(R, 30.3, 21.4, math.pi / 2, z=NZ)
    table(R, 29.6, 23.0, 30.6, 23.9, z=NZ, h=0.74)
    open_book(R, 30.1, 23.45, NZ + 0.74, 0.3)
    desk_lamp(R, 30.4, 23.7, NZ + 0.74)
    lamp_post(R, 29.4, 20.8, NZ, h=1.7, m='e_lamp')
    bulb(R, 29.8, 22.5, CT - 1.2, r=0.1, m='e_candle', top=CT)
    pendant(R, 30.0, 22.4, CT - 1.8, CT, r=0.26, m='e_lamp')
    R.spot('plaque', x1 - 0.4, 24.6, NZ + 1.6, math.pi, text='DOWN IS THIS WAY')


def cy_lo(): return SY - 0.6
def cy_hi(): return SY + 0.6
