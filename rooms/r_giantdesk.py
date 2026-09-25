"""The Desk: you come out of the upper doorways onto a gallery round a writing desk the size of a city
block. Its top is the upper floor: a fountain pen lies across it like a fallen column, an inkwell is a
black lake, books are stacked into towers you can climb by the ledges of their covers. Below, in the dark,
the desk's underside: legs like towers, a pedestal of drawers like a building. One drawer stands open a
crack; inside it, a long wooden hall of pencils and a candle. The lower level climbs to the desk top by a
stair inside the hollow back leg."""
from kit_h1 import *

W = D = 64.0
DX0, DY0, DX1, DY1 = 9.0, 9.0, 55.0, 55.0      # the desk top
DZ = GZ                                          # its top (the upper doorways' level)
DB = 7.0                                         # its underside
E = T + GW                                       # the gallery's inner edge, from each wall
# the hollow leg (NW) and its stair
LX0, LY0, LX1, LY1 = 9.0, 47.0, 17.0, 55.0
LW = 0.6
IX0, IY0, IX1, IY1 = LX0 + LW, LY0 + LW, LX1 - LW, LY1 - LW      # its inside: 6.8 square
LN = 1.4                                         # lane width
# the SW pedestal and its drawer
PX0, PY0, PX1, PY1 = 9.0, 9.0, 23.0, 25.0
DRZ = 0.45                                       # the drawer's floor
DRO = 1.25                                       # how far it stands open
INK = (46.0, 41.5, 6.5)                          # the inkwell: centre, outer radius
COVERS = ('oxblood', 'green', 'leather', 'walnut', 'velvet', 'oxblood', 'green', 'slate')


def make():
    R = Room('giantdesk', 4, 4, levels=2, res=2048)
    R.sockets(floor='floor', wall='tile')
    top = R.hi - 0.2
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, top, 'tile', bottom='floor', top='plaster'))
    rnd = random.Random(1010)
    gaps = [('S', 26.9, 30.6), ('N', 44.4, 52.6), ('W', 29.9, 31.5)]
    gallery(R, gaps=gaps)
    gallery_cases(R, rows=13)
    gallery_lamps(R, skip=lambda x, y: (26.0 < x < 31.5 and y < 5) or (44.0 < x < 53.0 and y > 59))
    lower_cases(R, rows=15)
    ceiling(R, top)
    desk(R)
    bridges(R)
    leg_stair(R)
    pedestals(R)
    drawer(R)
    desk_things(R, rnd)
    underside(R, rnd)
    towers(R, rnd)
    nav(R)
    R.spot('probe', 32.0, 30.0, 10.5)
    R.meta.update(label='The Desk', weight=2,
                  blurb='Somebody is writing a letter on a desk the size of a parish. The pen has been put down mid-sentence. You would not like to meet the hand.')
    R.meta['box'] = [[T, 0, T], [W - T, top, D - T]]
    fx(R, 'dust', [DX0, DY0, DZ + 0.5, DX1, DY1, top - 1.0])
    secret(R, 16.0, 19.0, DRZ, 'The Pencil Drawer',
           'A drawer left open a crack. Inside, pencils as long as barges, all sharpened, and one candle somebody lit and forgot. It has been burning for a very long time.', r=3.0)
    return tidy(R)


# ---------------------------------------------------------------------------
def ceiling(R, top):
    # a dark coffered ceiling and great pendant lamps hanging over the desk
    for k in range(9):
        x = 4.0 + k * 7.0
        R.parts.add(box(x - 0.3, T, top - 0.5, x + 0.3, D - T, top, 'walnut'))
        R.parts.add(box(T, x - 0.3, top - 0.5, W - T, x + 0.3, top, 'walnut'))
    for (x, y) in ((20, 28), (32, 22), (44, 13), (33, 36), (46, 41.5), (38, 50), (24, 53), (52, 34), (30, 44)):
        R.parts.add(cyl(x, y, 12.8, top - 0.5, 0.04, 6, side='iron', caps=False))
        R.nocol.add(frustum(x, y, 12.4, 13.2, 1.5, 0.35, 16, m='green', inner='ivory'))
        R.light(sphere(x, y, 12.5, 0.55, 12, 6, 'e_lamp'))


def desk(R):
    """The desk top: a slab of walnut with a green leather writing surface, a moulded edge and a brass
    gallery rail; a hole over the hollow leg where its stair comes up."""
    # the slab, in pieces round the leg's stairwell (the ring between the leg's walls and its newel)
    NX0, NY0, NX1, NY1 = IX0 + LN, IY0 + LN, IX1 - LN, IY1 - LN
    pieces = [(DX0, DY0, DX1, IY0), (IX1, IY0, DX1, DY1), (DX0, IY1, IX1, DY1), (DX0, IY0, IX0, IY1),
              (NX0, NY0, NX1, NY1)]
    for (x0, y0, x1, y1) in pieces:
        R.parts.add(box(x0, y0, DB, x1, y1, DZ, 'walnut', bottom='walnut'))
    # the landing at the top of the stair, flush with the desk
    R.parts.add(box(IX0, IY0, DZ - 0.4, NX0 + 1.0, NY0, DZ, 'walnut'))
    # green leather inset (drawn over the top)
    R.nocol.add(box(DX0 + 3.5, DY0 + 3.5, DZ, DX1 - 3.5, DY1 - 3.5, DZ + 0.006, 'green', skip=('-z',)))
    for (x0, y0, x1, y1) in ((DX0 + 3.3, DY0 + 3.3, DX1 - 3.3, DY0 + 3.5), (DX0 + 3.3, DY1 - 3.5, DX1 - 3.3, DY1 - 3.3),
                             (DX0 + 3.3, DY0 + 3.5, DX0 + 3.5, DY1 - 3.5), (DX1 - 3.5, DY0 + 3.5, DX1 - 3.3, DY1 - 3.5)):
        R.nocol.add(box(x0, y0, DZ, x1, y1, DZ + 0.01, 'gilt', skip=('-z',)))
    # a moulded edge under the lip
    for (x0, y0, x1, y1) in ((DX0 - 0.25, DY0 - 0.25, DX1 + 0.25, DY0), (DX0 - 0.25, DY1, DX1 + 0.25, DY1 + 0.25),
                             (DX0 - 0.25, DY0, DX0, DY1), (DX1, DY0, DX1 + 0.25, DY1)):
        R.parts.add(box(x0, y0, DZ - 0.35, x1, y1, DZ - 0.05, 'walnut'))
    # the brass gallery rail round the desk top, open where the bridges land
    i = 0.18
    rails = [((DX0 + i, DY0 + i), (26.9, DY0 + i)), ((30.6, DY0 + i), (DX1 - i, DY0 + i)),
             ((DX1 - i, DY0 + i), (DX1 - i, DY1 - i)),
             ((DX1 - i, DY1 - i), (52.6, DY1 - i)), ((44.4, DY1 - i), (DX0 + i, DY1 - i)),
             ((DX0 + i, DY1 - i), (DX0 + i, 31.5)), ((DX0 + i, 29.9), (DX0 + i, DY0 + i))]
    for (p, q) in rails:
        rail(R, p[0], p[1], q[0], q[1], DZ, h=1.0)
    # rails round the stairwell: its outer edges on the desk, and the newel
    rail(R, NX0 + 1.0, IY0 - 0.05, IX1 + 0.05, IY0 - 0.05, DZ)
    rail(R, IX1 + 0.05, IY0 - 0.05, IX1 + 0.05, IY1 + 0.05, DZ)
    rail(R, IX1 + 0.05, IY1 + 0.05, IX0 - 0.05, IY1 + 0.05, DZ)
    rail(R, IX0 - 0.05, IY1 + 0.05, IX0 - 0.05, NY0 + 0.05, DZ)
    rail(R, IX0 - 0.05, NY0 + 0.05, NX1 - 0.05, NY0 + 0.05, DZ)
    rail(R, NX1 - 0.05, NY0 + 0.05, NX1 - 0.05, NY1 - 0.05, DZ)
    rail(R, NX1 - 0.05, NY1 - 0.05, NX0 + 0.05, NY1 - 0.05, DZ)
    rail(R, NX0 + 0.05, NY1 - 0.05, NX0 + 0.05, NY0 + 0.05, DZ)
    # a brass lamp on the newel over the stairwell (a normal-sized one)
    cx, cy = (NX0 + NX1) / 2, (NY0 + NY1) / 2
    R.parts.add(cyl(cx, cy, DZ, DZ + 0.05, 0.25, 12, side='brass', top='brass'))
    R.parts.add(cyl(cx, cy, DZ + 0.05, DZ + 1.7, 0.03, 6, side='brass', caps=False))
    R.nocol.add(frustum(cx, cy, DZ + 1.62, DZ + 1.9, 0.36, 0.14, 12, m='green', inner='ivory'))
    R.light(cyl(cx, cy, DZ + 1.6, DZ + 1.63, 0.32, 12, side='e_lamp', top='e_lamp', bottom='e_lamp'))


def bridges(R):
    # south: a ruler laid from the gallery onto the desk
    x0, x1, y0, y1, z = 27.0, 30.5, 1.8, 37.0, DZ + 0.14
    R.parts.add(box(x0, y0, DZ, x1, y1, z, 'oak', bottom='oak'))
    R.nocol.add(box(x0, y0, z, x0 + 0.08, y1, z + 0.01, 'brass', skip=('-z',)))
    for k in range(int((y1 - y0 - 0.6) / 0.5)):
        y = y0 + 0.4 + k * 0.5
        L = 0.9 if k % 10 == 0 else 0.55 if k % 2 == 0 else 0.35
        R.nocol.add(box(x1 - L, y - 0.025, z, x1 - 0.06, y + 0.025, z + 0.006, 'black', skip=('-z',)))
    for x in (x0 + 0.12, x1 - 0.12):
        rail(R, x, E - 0.3, x, DY0 + 0.3, z)
    # north: a closed book, bridging
    book_block(R, 44.5, 53.0, 52.5, D - 2.1, DZ, DZ + 0.45, cover='green', spine='+x', over=0.15)
    for x in (44.62, 52.38):
        rail(R, x, DY1 - 0.3, x, D - E + 0.3, DZ + 0.45)
    # west: a paper knife, its ivory handle on the desk
    y0, y1, z = 30.0, 31.4, DZ + 0.1
    R.parts.add(box(1.2, y0, DZ, 20.0, y1, z, 'brass'))
    R.parts.add(prism([(y0, DZ), (y1, DZ), (y1, z), ((y0 + y1) / 2, z + 0.02), (y0, z)], 'x', 0.7, 1.2, 'brass', cap='brass'))
    R.parts.add(box(20.0, y0 - 0.3, DZ, 20.6, y1 + 0.3, DZ + 0.5, 'gilt'))
    R.parts.add(box(20.6, y0 - 0.15, DZ, 27.0, y1 + 0.15, DZ + 1.3, 'ivory'))
    for y in (y0 + 0.12, y1 - 0.12):
        rail(R, E - 0.3, y, DX0 + 0.3, y, z)


def leg_stair(R):
    """The hollow NW leg: a square stair round a solid newel, one lap from the floor to the desk top."""
    # the leg's walls, a door at its SW foot
    dx0, dx1 = IX0 + 0.1, IX0 + LN - 0.05
    walls = [(LX0, LY0, dx0, IY0), (dx1, LY0, LX1, IY0), (LX0, IY1, LX1, LY1), (LX0, IY0, IX0, IY1), (IX1, IY0, LX1, IY1)]
    for (x0, y0, x1, y1) in walls:
        R.parts.add(box(x0, y0, 0, x1, y1, DB, 'walnut'))
    R.parts.add(box(dx0, LY0, 2.7, dx1, IY0, DB, 'walnut'))
    # a turned foot and a collar: the leg as seen from outside
    for (x0, y0, x1, y1) in ((LX0 - 0.3, LY0 - 0.3, dx0, LY0), (dx1, LY0 - 0.3, LX1 + 0.3, LY0), (LX1, LY0, LX1 + 0.3, LY1 + 0.3),
                             (LX0 - 0.3, LY1, LX1, LY1 + 0.3), (LX0 - 0.3, LY0, LX0, LY1)):
        R.parts.add(box(x0, y0, 0, x1, y1, 0.7, 'walnut', skip=('-z',)))
        R.parts.add(box(x0, y0, DB - 1.0, x1, y1, DB, 'walnut'))
    # the door's brass frame and a green sign
    R.nocol.add(box(dx0 - 0.1, LY0 - 0.06, 0, dx0, LY0, 2.8, 'brass'))
    R.nocol.add(box(dx1, LY0 - 0.06, 0, dx1 + 0.1, LY0, 2.8, 'brass'))
    R.nocol.add(box(dx0 - 0.1, LY0 - 0.06, 2.7, dx1 + 0.1, LY0, 2.8, 'brass'))
    R.light(box(dx0 + 0.3, LY0 - 0.05, 3.0, dx1 - 0.3, LY0 - 0.02, 3.25, 'e_exit'))
    # newel
    NX0, NY0, NX1, NY1 = IX0 + LN, IY0 + LN, IX1 - LN, IY1 - LN
    R.parts.add(box(NX0, NY0, 0, NX1, NY1, DB, 'walnut'))
    n, rise, run = 10, 0.2, 0.3
    L = n * run
    # W lane: up +y from z 0 to 2
    R.flight(IX0, NY0, 0, LN, n, rise, run, '+y', m='oak', riser='walnut', side='walnut')
    R.parts.add(box(IX0, NY0 + L, 0, NX0, IY1, 2.0, 'walnut', top='oak'))
    # N lane: up +x from 2 to 4
    R.parts.add(box(NX0, NY1, 0, NX0 + L, IY1, 2.0, 'walnut'))
    R.flight(NX0, NY1, 2.0, LN, n, rise, run, '+x', m='oak', riser='walnut', side='walnut')
    R.parts.add(box(NX0 + L, NY1, 0, IX1, IY1, 4.0, 'walnut', top='oak'))
    # E lane: up -y from 4 to 6
    R.parts.add(box(NX1, NY1 - L, 0, IX1, NY1, 4.0, 'walnut'))
    R.flight(NX1, NY1, 4.0, LN, n, rise, run, '-y', m='oak', riser='walnut', side='walnut')
    R.parts.add(box(NX1, IY0, 0, IX1, NY1 - L, 6.0, 'walnut', top='oak'))
    # S lane: up -x from 6 to 8
    R.parts.add(box(NX1 - L, IY0, 0, NX1, NY0, 6.0, 'walnut'))
    R.flight(NX1, IY0, 6.0, LN, n, rise, run, '-x', m='oak', riser='walnut', side='walnut')
    # candles in niches of the newel on the way up
    for (x, y, z) in ((NX0 - 0.02, NY0 + 2.5, 1.4), (NX0 + 2.0, NY1 + 0.02, 3.8), (NX1 + 0.02, NY1 - 1.5, 5.6), (NX1 - 2.2, NY0 - 0.02, 7.4)):
        R.light(sphere(x, y, z + 0.2, 0.07, 8, 4, 'e_candle'))
        R.parts.add(cyl(x, y, z - 0.1, z + 0.12, 0.06, 8, side='ivory', top='ivory'))
    bulb(R, NX0 + 1.0, IY0 + 0.7, 5.2, r=0.14, m='e_dim', top=DB)


def pedestals(R):
    """The SW pedestal (its bottom drawer open: see drawer()) and the SE one, the NE leg."""
    # SW pedestal carcass
    R.parts.add(box(PX0, PY0, 0, PX0 + 0.5, PY1, DB, 'walnut'))
    R.parts.add(box(PX1 - 0.5, PY0, 0, PX1, PY1, DB, 'walnut'))
    R.parts.add(box(PX0 + 0.5, PY1 - 0.5, 0, PX1 - 0.5, PY1, DB, 'walnut'))
    R.parts.add(box(PX0 + 0.5, PY0, 3.4, PX1 - 0.5, PY1 - 0.5, DB, 'walnut'))
    R.parts.add(box(PX0 + 0.5, PY0, 0, PX1 - 0.5, PY1 - 0.5, 0.25, 'walnut'))
    drawer_fronts(R, PX0, PX1, PY0, ((3.5, 5.2), (5.3, 6.95)))
    # SE pedestal, all drawers shut
    X0, X1 = 41.0, DX1
    R.parts.add(box(X0, PY0, 0, X1, PY1, DB, 'walnut'))
    drawer_fronts(R, X0, X1, PY0, ((0.3, 3.35), (3.5, 5.2), (5.3, 6.95)))
    # the other back leg (NE), solid
    x0, y0, x1, y1 = 47.0, 47.0, DX1, DY1
    R.parts.add(box(x0, y0, 0, x1, y1, DB, 'walnut'))
    for (a, b, c, d) in ((x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3),):
        R.parts.add(box(a, b, 0, c, d, 0.7, 'walnut', skip=('-z',)))
        R.parts.add(box(a, b, DB - 1.0, c, d, DB, 'walnut'))


def drawer_fronts(R, x0, x1, y, rows):
    for (z0, z1) in rows:
        R.parts.add(box(x0 + 0.2, y - 0.12, z0, x1 - 0.2, y, z1, 'walnut'))
        R.nocol.add(box(x0 + 0.5, y - 0.16, z0 + 0.3, x1 - 0.5, y - 0.12, z1 - 0.3, 'walnut'))
        pull(R, (x0 + x1) / 2, y - 0.16, (z0 + z1) / 2)


def pull(R, x, y, z):
    """A brass bail pull: two round plates and a hanging handle."""
    for s in (-1, 1):
        R.parts.add(box(x + s * 1.1 - 0.25, y - 0.08, z - 0.25, x + s * 1.1 + 0.25, y, z + 0.25, 'brass'))
    R.parts.add(box(x - 1.15, y - 0.3, z - 0.55, x + 1.15, y - 0.08, z - 0.45, 'brass'))
    for s in (-1, 1):
        R.parts.add(box(x + s * 1.1 - 0.05, y - 0.3, z - 0.55, x + s * 1.1 + 0.05, y - 0.08, z, 'brass'))


def drawer(R):
    """The bottom drawer of the SW pedestal, pulled out a crack. The side panel of its open end is
    split away, so a person can squeeze in from the west between the front and the carcass."""
    fy1 = PY0 - DRO                  # back face of the pulled-out front
    fy0 = fy1 - 0.4
    ix0, ix1 = PX0 + 0.6, PX1 - 0.6  # the drawer box
    # the front, proud of the carcass, with its pull
    R.parts.add(box(PX0 + 0.2, fy0, 0.3, PX1 - 0.2, fy1, 3.35, 'walnut'))
    R.nocol.add(box(PX0 + 0.5, fy0 - 0.04, 0.6, PX1 - 0.5, fy0, 3.05, 'walnut'))
    pull(R, (PX0 + PX1) / 2, fy0 - 0.04, 1.8)
    # bottom, east side, back
    R.parts.add(box(ix0, fy1, 0.0, ix1, PY1 - 0.7, DRZ, 'oak', top='oak'))
    R.parts.add(box(ix1 - 0.2, fy1, DRZ, ix1, PY1 - 0.7, 3.15, 'oak'))
    R.parts.add(box(ix0, PY1 - 0.9, DRZ, ix1, PY1 - 0.7, 3.15, 'oak'))
    # the west side, split away along the part that stands out of the carcass
    R.parts.add(box(ix0, PY0, DRZ, ix0 + 0.2, PY1 - 0.9, 3.15, 'oak'))
    R.nocol.add(box(ix0, PY0 - 0.35, DRZ, ix0 + 0.2, PY0, 1.2, 'oak').xform(0, 0, 0, 0))
    # inside: a long dark hall of pencils
    y0, y1 = PY0 + 0.3, PY1 - 2.0
    for k, (x, r, L, body) in enumerate(((ix0 + 0.75, 0.5, 13.5, 'gilt'), (ix0 + 1.85, 0.5, 12.0, 'green'),
                                         (ix0 + 1.3, 0.45, 9.0, 'gilt'), (ix1 - 0.75, 0.5, 14.0, 'gilt'),
                                         (ix1 - 1.85, 0.5, 11.0, 'oxblood'), (ix1 - 1.3, 0.45, 8.5, 'gilt'))):
        zc = DRZ + r * 0.87 + (0.0 if k % 3 != 2 else r * 1.6)
        if k in (0, 3): pencil_lying(R, (x, y1, zc), (x, y1 - L, zc), r, body=body, spin=math.pi / 6)
        elif k in (1, 4): pencil_lying(R, (x, y1 - 0.4, zc), (x, y1 - 0.4 - L, zc), r, body=body, spin=math.pi / 6)
        else: pencil_lying(R, (x, y1 - 1.0, zc), (x, y1 - 1.0 - L, zc), r, body=body, spin=math.pi / 6)
    # one pencil across the far end, a stub of rubber, a brass clip
    pencil_lying(R, (ix0 + 3.2, y1 + 0.55, DRZ + 0.4), (ix1 - 3.2, y1 + 0.6, DRZ + 0.4), 0.46, body='gilt', spin=math.pi / 6)
    R.parts.add(box(12.6, 13.0, DRZ, 14.2, 14.2, DRZ + 0.7, 'oxblood'))
    R.nocol.add(ring(19.0, 12.5, DRZ, DRZ + 0.05, 0.9, 1.0, 24, top='brass', bottom='brass', inner='brass', outer='brass'))
    # the candle, far in, and a book open beside it
    cx, cy = 16.0, y1 - 2.0
    R.parts.add(cyl(cx, cy, DRZ, DRZ + 0.08, 0.45, 16, side='brass', top='brass'))
    R.parts.add(cyl(cx, cy, DRZ + 0.08, DRZ + 0.9, 0.16, 12, side='ivory', top='ivory'))
    R.light(sphere(cx, cy, DRZ + 1.02, 0.07, 8, 4, 'e_candle'))
    R.light(cyl(cx, cy, DRZ + 0.9, DRZ + 0.95, 0.02, 6, side='e_candle', top='e_candle'))
    R.parts.add(box(cx + 0.9, cy - 0.3, DRZ, cx + 1.5, cy + 0.2, DRZ + 0.06, 'ivory'))
    R.spot('read', cx + 1.2, cy - 0.6, DRZ, math.pi / 2)
    R.spot('plaque', cx, cy - 0.8, DRZ)


def desk_things(R, rnd):
    # the inkwell: a squat black glass well with a brass collar, full of ink; steps inside
    cx, cy, ro = INK
    ri = ro - 0.6
    rim = DZ + 2.8
    R.parts.add(ring(cx, cy, DZ, rim - 0.3, ri, ro, 32, top='black', bottom='black', inner='black', outer='black'))
    R.parts.add(ring(cx, cy, rim - 0.3, rim, ri - 0.05, ro + 0.1, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
    zs = [rim - 0.55 - 0.5 * k for k in range(5)]
    for k, z in enumerate(zs):
        r = ri - 0.6 * k
        R.parts.add(cyl(cx, cy, DZ, z, r, 32, side='slate', top='slate', bottom='slate'))
    R.parts.add(cyl(cx, cy, DZ, DZ + 0.02, ri - 3.0, 24, side='black', top='black'))
    R.water.append(dict(cx=cx, cy=cy, r=ri - 0.02, top=rim - 0.4, bot=DZ))
    # books spilt against it as steps up to the rim
    steps = [(cx - ro - 3.2, cy - 2.2, cx - ro + 0.3, cy + 1.6, DZ, DZ + 0.5),
             (cx - ro - 2.4, cy - 1.8, cx - ro + 0.3, cy + 1.4, DZ + 0.5, DZ + 1.0),
             (cx - ro - 1.6, cy - 1.6, cx - ro + 0.4, cy + 1.2, DZ + 1.0, DZ + 1.5),
             (cx - ro - 0.8, cy - 1.4, cx - ro + 0.5, cy + 1.0, DZ + 1.5, DZ + 2.0),
             (cx - ro - 0.2, cy - 1.2, cx - ro + 0.9, cy + 0.9, DZ + 2.0, DZ + 2.45)]
    for k, (x0, y0, x1, y1, z0, z1) in enumerate(steps):
        book_block(R, x0, y0, x1, y1, z0, z1, cover=COVERS[k + 2], spine='-y' if k % 2 else '+y')
    # the fountain pen, lying across: cap posted on the back, the nib touching the desk
    p0 = (41.5, 31.0, DZ + 1.12)
    p1 = (33.0, 11.8, DZ + 0.08)
    L = math.dist(p0, p1)
    g = Geo()
    sp = math.pi / 16
    g.add(xcyl(7.2, 1.12, 16, side='black', a0=sp))
    for (a, b) in ((0.4, 0.75), (6.5, 6.9)):
        c = xcyl(b - a, 1.15, 16, side='gilt', a0=sp); c.v = [(x + a, y, z) for x, y, z in c.v]; g.add(c)
    c = xcyl(L - 7.2 - 5.8, 1.02, 16, side='black', a0=sp); c.v = [(x + 7.2, y, z) for x, y, z in c.v]; g.add(c)
    a = L - 5.8
    c = xcyl(0.4, 1.06, 16, side='gilt', a0=sp); c.v = [(x + a, y, z) for x, y, z in c.v]; g.add(c)
    c = xcone(1.8, 1.0, 0.72, 16, side='black', a0=sp); c.v = [(x + a + 0.4, y, z) for x, y, z in c.v]; g.add(c)
    c = xcone(3.6, 0.72, 0.03, 16, side='gilt', a0=sp); c.v = [(x + a + 2.2, y, z) for x, y, z in c.v]; g.add(c)
    # the clip, down the side of the cap
    g.add(box(0.8, -1.25, -0.25, 6.2, -1.1, 0.25, 'gilt'))
    R.parts.add(along(g, p0, p1))
    # fill its hollow so nobody finds a room inside the pen
    R.col.add(along(box(0.3, -0.7, -1.4, L - 4.0, 0.7, 0.4, 'tile'), p0, p1))
    # the nib's slit and breather hole, drawn on its top
    # a sheet of writing paper by the knife handle
    sheet = box(0, 0, 0, 13.0, 9.0, 0.02, 'ivory', skip=('-z',))
    for k in range(12):
        sheet.add(box(1.0, 1.0 + k * 0.62, 0.02, 1.0 + rnd.uniform(5.0, 11.5), 1.08 + k * 0.62, 0.025, 'walnut', skip=('-z',)))
    R.nocol.add(sheet.xform(-0.12, 11.0, 23.8, DZ))
    # a pair of spectacles folded on the desk
    for dx in (0.0, 5.2):
        R.parts.add(ring(22.0 + dx, 50.5, DZ, DZ + 0.35, 2.0, 2.25, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    R.parts.add(box(24.25, 50.3, DZ + 0.1, 24.95, 50.7, DZ + 0.35, 'gilt'))


def underside(R, rnd):
    """The dark under the desk: cross-rails, a few weak bulbs, lost things on the floor."""
    for x in (20.0, 32.0, 44.0):
        R.parts.add(box(x - 0.35, DY0, DB - 0.8, x + 0.35, DY1, DB, 'walnut'))
    for y in (26.0, 38.0):
        R.parts.add(box(DX0, y - 0.35, DB - 0.8, DX1, y + 0.35, DB, 'walnut'))
    for (x, y) in ((26, 16), (38, 20), (30, 32), (40, 42), (22, 44), (50, 34)):
        bulb(R, x, y, 5.2, r=0.14, m='e_dim', top=DB - 0.8)
    for (x, y) in ((24.5, 28.8), (41.5, 44.0), (6.0, 45.0)):
        floor_lamp(R, x, y, 1.7)
    for (x, y) in ((19.0, 46.0), (39.5, 26.0)):
        R.light(sphere(x, y, 0.25, 0.1, 8, 4, 'e_amber'))
        R.parts.add(cyl(x, y, 0, 0.12, 0.18, 10, side='brass', top='brass'))
    # a crumpled ball of paper, a dropped coin, a pencil shaving the size of a boat
    R.parts.add(sphere(33.0, 38.0, 2.2, 2.6, 12, 8, 'ivory'))
    R.parts.add(cyl(26.0, 34.0, 0, 0.35, 2.4, 32, side='brass', top='brass', bottom='brass'))
    R.nocol.add(cyl(26.0, 34.0, 0.35, 0.37, 1.8, 32, side='brass', top='gilt', bottom='brass'))
    pencil_lying(R, (44.0, 30.0, 0.55), (36.0, 44.0, 0.55), 0.62, body='green', spin=math.pi / 6)
    # iron hooks and a lantern in the moat, round the desk
    for (x, y) in ((2.0, 2.0), (62.0, 2.0), (62.0, 62.0), (2.0, 62.0), (32.0, 2.0), (2.0, 32.0), (62.0, 32.0), (32.0, 62.0)):
        R.light(sphere(x, y, 5.0, 0.2, 8, 4, 'e_lamp'))
        R.nocol.add(cyl(x, y, 5.2, DZ - 0.55, 0.02, 6, side='iron', caps=False))


def tower(R, rnd, x0, y0, x1, y1, n, start, s=1.25, t=0.5, crown=None):
    """A stack of n books, each a strip smaller than the one below on one side, the side turning each
    time: you climb it by the ledges round its edge. Rails where a ledge overhangs more than a step."""
    rects = [(x0, y0, x1, y1)]
    order = ['S', 'E', 'N', 'W']
    dirs = [None]
    for k in range(1, n):
        d = order[(start + k - 1) % 4]
        a, b, c, e = rects[-1]
        if d == 'S': b += s
        elif d == 'N': e -= s
        elif d == 'W': a += s
        else: c -= s
        rects.append((a, b, c, e)); dirs.append(d)
    tops = [DZ + t * (k + 1) for k in range(n)]
    for k, (a, b, c, e) in enumerate(rects):
        cov = COVERS[rnd.randrange(len(COVERS))]
        sp = rnd.choice(['-x', '+x', '-y', '+y'])
        book_block(R, a, b, c, e, tops[k] - t, tops[k] - 0.002, cover=cov, spine=sp, over=0.14)
    def top_at(x, y):
        h = DZ
        for k, (a, b, c, e) in enumerate(rects):
            if a < x < c and b < y < e: h = max(h, tops[k])
        return h
    for k, (a, b, c, e) in enumerate(rects):
        nxt = rects[k + 1] if k + 1 < n else None
        zk = tops[k]
        for side in 'SENW':
            if side in 'SN':
                yy = b if side == 'S' else e; sg = -1 if side == 'S' else 1
                P = lambda u: (u, yy); Lo, Hi = a, c; nrm = (0, sg)
            else:
                xx = a if side == 'W' else c; sg = -1 if side == 'W' else 1
                P = lambda u: (xx, u); Lo, Hi = b, e; nrm = (sg, 0)
            m = max(2, int((Hi - Lo) / 0.25))
            flags = []
            for i in range(m):
                u = Lo + (Hi - Lo) * (i + 0.5) / m
                px, py = P(u)
                ix, iy = px - nrm[0] * 0.3, py - nrm[1] * 0.3
                ox, oy = px + nrm[0] * 0.3, py + nrm[1] * 0.3
                exposed = not (nxt and nxt[0] < ix < nxt[2] and nxt[1] < iy < nxt[3])
                flags.append(exposed and zk - top_at(ox, oy) > 0.6)
            i = 0
            while i < m:
                if not flags[i]: i += 1; continue
                j = i
                while j + 1 < m and flags[j + 1]: j += 1
                ua = Lo + (Hi - Lo) * i / m; ub = Lo + (Hi - Lo) * (j + 1) / m
                ua = max(Lo + 0.1, ua); ub = min(Hi - 0.1, ub)
                pa, pb = P(ua), P(ub)
                pa = (pa[0] - nrm[0] * 0.1, pa[1] - nrm[1] * 0.1); pb = (pb[0] - nrm[0] * 0.1, pb[1] - nrm[1] * 0.1)
                rail(R, pa[0], pa[1], pb[0], pb[1], zk, h=0.95)
                i = j + 1
    return rects[-1], tops[-1]


def towers(R, rnd):
    # the tall one: a reading nook on its top, a normal-sized chair and lamp, the whole room below
    (a, b, c, e), z = tower(R, rnd, 13.0, 34.0, 26.0, 45.5, 10, 0, t=0.48)
    cx, cy = (a + c) / 2, (b + e) / 2
    ch = chair(cx - 0.6, cy, 0.0); ch.v = [(x, y, zz + z) for x, y, zz in ch.v]
    R.parts.add(ch)
    R.spot('sit', cx - 0.6, cy, z + 0.48, 0.0)
    t = table(cx + 0.1, cy - 0.5, cx + 1.1, cy + 0.5, 0.74, 'walnut', top='leather')
    t.v = [(x, y, zz + z) for x, y, zz in t.v]
    R.parts.add(t)
    desk_lamp(R, cx + 0.6, cy + 0.25, z + 0.74)
    R.parts.add(box(cx + 0.25, cy - 0.35, z + 0.74, cx + 0.75, cy, z + 0.77, 'ivory'))
    R.spot('read', cx - 0.6, cy, z, 0.0)
    # two lower stacks
    tower(R, rnd, 13.0, 12.0, 23.0, 21.5, 8, 2)
    tower(R, rnd, 46.0, 18.0, 54.0, 27.5, 6, 1)
    # books lying about singly
    for (x, y, w_, d_, ang) in ((50.0, 12.0, 3.5, 5.0, -0.5), (36.0, 52.0, 5.0, 3.6, 0.2)):
        book_block(R, x - w_ / 2, y - d_ / 2, x + w_ / 2, y + d_ / 2, DZ, DZ + 0.5, cover=COVERS[rnd.randrange(8)], ang=ang)


def nav(R):
    g = 1.6
    gal = [R.navpt(x, y, GZ) for (x, y) in ((g, g), (28.75, g), (W - g, g), (W - g, D - g), (48.5, D - g), (g, D - g), (g, 30.7))]
    R.link(*gal, gal[0])
    low = [R.navpt(x, y) for (x, y) in ((5.0, 5.0), (32, 5.0), (W - 5.0, 5.0), (W - 5.0, 32), (W - 5.0, D - 5.0), (32, D - 5.0), (5.0, D - 5.0), (5.0, 32))]
    R.link(*low, low[0])
    under = [R.navpt(x, y) for (x, y) in ((28.0, 14.0), (36.0, 30.0), (28.0, 40.0), (18.0, 32.0), (26.0, 26.0))]
    R.link(*under, under[0])
    R.link(low[1], under[0])
    r1, a, c = R.navpt(28.75, 20.0, DZ + 0.14), R.navpt(33.0, 38.0, DZ), R.navpt(40.0, 49.0, DZ)
    bk = R.navpt(48.5, 57.0, DZ + 0.45)
    kn, k = R.navpt(11.0, 30.7, DZ + 0.1), R.navpt(12.0, 27.0, DZ)
    R.link(gal[1], r1, a, c, bk, gal[4])
    R.link(gal[6], kn, k, r1)
