"""The Door in the Ceiling: a stair climbs to a landing under an open trapdoor. Through it, a low loft
the size of the hall where somebody lived; from its far corner a slot of a passage inside the north wall
steps down to the door that stands ajar high in the hall's wall, too high to reach from the floor."""
from lib import *
from kit_a import *

H = 5.35                     # the hall's ceiling; the loft sits on top of it
AZ = 5.55
LT = 7.5                     # the loft's ceiling (the solid ends at 7.6)                    # the loft floor (kept under 6 m: above that the game counts the next floor up)
YN = 13.8                    # the hall's north wall; the passage runs behind it
LZ = 3.3                     # the landing under the trap
FX0, FX1 = 4.0, 5.3          # the stairs, climbing +y
N, RISE, RUN = 14, LZ / 14, 0.3
FY1 = 8.7
FY0 = FY1 - N * RUN
LX0, LX1, LY0, LY1 = 3.9, 5.7, FY1, FY1 + 1.7
N2, RISE2, RUN2 = 10, (AZ - LZ) / 10, 0.28          # the steep flight up through the trap
TY1 = LY1 + N2 * RUN2                                # where it tops out, in the loft
PX0, PY0, PY1 = 9.9, 14.05, 15.45                    # the passage inside the north wall (east of the doorway)
DZ = 3.4                                             # its lower end: the high door's sill
HX, HW, HH = 10.8, 1.3, 1.9


def make():
    R = Room('ceilingdoor', 1, 1, res=1024)
    shell(R, y1=YN, wall='ivory', floor='floor', ceil='plaster', h=H)
    # the trap: the slab opened over the upper flight, an oak frame, the leaf hanging open
    tx0, tx1, ty0, ty1 = FX0, FX1 + 0.05, LY1, TY1
    R.cut(box(tx0, ty0, H - 0.05, tx1, ty1, AZ + 0.05, 'oak', top='oak', bottom='oak'))
    for (x0, y0, x1, y1) in ((tx0 - 0.12, ty0 - 0.12, tx1 + 0.12, ty0), (tx0 - 0.12, ty1, tx1 + 0.12, ty1 + 0.12),
                             (tx0 - 0.12, ty0, tx0, ty1), (tx1, ty0, tx1 + 0.12, ty1)):
        R.nocol.add(box(x0, y0, H - 0.06, x1, y1, H, 'oak'))
    lw = 1.4
    leaf = box(-0.04, 0, -lw, 0.0, 1.5, 0, 'oak', sides='walnut')
    rot(leaf, 'y', -0.22)
    leaf.xform(0, tx0 - 0.02, ty1 - 1.6, H - 0.02)
    R.nocol.add(leaf)
    for k in range(3):
        R.nocol.add(box(tx0 - 0.1, ty1 - 1.4 + k * 0.55, H - 0.35, tx0 - 0.02, ty1 - 1.35 + k * 0.55, H - 0.02, 'iron'))
    # the stairs and landing, on iron posts, railed all the way; then the steep flight up into the loft
    open_flight(R, FX0, FY0, 0, FX1 - FX0, N, RISE, RUN, tread='oak', stringer='walnut')
    R.parts.add(box(LX0, LY0, LZ - 0.25, LX1, LY1, LZ, 'oak', sides='walnut', bottom='walnut'))
    for (x, y) in ((LX0 + 0.08, LY0 + 0.08), (LX1 - 0.08, LY0 + 0.08), (LX0 + 0.08, LY1 - 0.08), (LX1 - 0.08, LY1 - 0.08)):
        R.parts.add(box(x - 0.06, y - 0.06, 0, x + 0.06, y + 0.06, LZ - 0.25, 'iron', skip=('-z',)))
    open_flight(R, FX0, LY1, LZ, FX1 - FX0, N2, RISE2, RUN2, tread='oak', stringer='walnut')
    for x in (FX0 + 0.04, FX1 - 0.04):
        stair_rail(R, x, FY0 + RUN, RISE, x, FY1, LZ, m='brass')
        stair_rail(R, x, LY1 + RUN2, LZ + RISE2, x, TY1 - 3 * RUN2, AZ - 3 * RISE2, m='brass')
    rail(R, LX0 + 0.04, LY0, LX0 + 0.04, LY1, LZ)
    rail(R, LX1 - 0.04, LY1, LX1 - 0.04, LY0, LZ)
    rail(R, LX1 - 0.04, LY1 - 0.04, FX1, LY1 - 0.04, LZ)
    rail(R, LX1 - 0.04, LY0 + 0.04, FX1 - 0.04, LY0 + 0.04, LZ)
    # a rail round the hole in the loft floor, open at its north end where the flight arrives
    # (open over its last few steps: there the stair is within a step of the loft floor)
    ye = ty1 - 3 * RUN2
    rail(R, tx0 - 0.1, ye, tx0 - 0.1, ty0 - 0.1, AZ)
    rail(R, tx0 - 0.1, ty0 - 0.1, tx1 + 0.1, ty0 - 0.1, AZ)
    rail(R, tx1 + 0.1, ty0 - 0.1, tx1 + 0.1, ye, AZ)
    loft(R)
    passage(R)
    # the high door, ajar, in the north wall, too high to reach from the floor
    hz = DZ
    R.cut(box(HX - HW / 2, YN - 0.05, hz, HX + HW / 2, PY0 + 0.05, hz + HH, 'black', bottom='oak', top='ivory'))
    R.parts.add(box(HX - HW / 2 - 0.16, YN - 0.08, hz + HH, HX + HW / 2 + 0.16, YN, hz + HH + 0.12, 'walnut'))
    for s_ in (-1, 1):
        x = HX + s_ * (HW / 2 + 0.08)
        R.parts.add(box(x - 0.08, YN - 0.08, hz - 0.1, x + 0.08, YN, hz + HH, 'walnut'))
    R.parts.add(box(HX - HW / 2 - 0.2, YN - 0.18, hz - 0.12, HX + HW / 2 + 0.2, YN, hz, 'tile'))   # a sill
    door = box(0, -0.05, 0, HW - 0.04, 0.0, HH - 0.04, 'oak')
    for (z0, z1) in ((0.15, 0.85), (1.05, 1.75)):
        door.add(box(0.12, -0.07, z0, HW - 0.16, -0.05, z1, 'walnut'))
    door.add(box(HW - 0.2, -0.12, 0.95, HW - 0.14, -0.05, 1.01, 'brass'))
    door.xform(-1.05, HX - HW / 2 + 0.02, YN + 0.02, hz)
    R.nocol.add(door)
    R.parts.add(box(HX - 0.35, YN - 0.1, hz - 0.62, HX + 0.35, YN, hz - 0.4, 'black'))
    R.light(box(HX - 0.3, YN - 0.12, hz - 0.59, HX + 0.3, YN - 0.1, hz - 0.43, 'e_exit'))
    # a ladder leaning up toward it that stops too short
    R.nocol.add(ladder(HX + 0.1, YN - 0.36, -math.pi / 2, h=1.9, lean=0.7))
    return hall(R)


def loft(R):
    """Above the trap: a low loft the size of the hall, under the next floor's slab. Somebody lived here."""
    R.cut(box(0.6, 0.6, AZ, C - 0.6, YN + 0.1, LT, 'plaster', bottom='floor', top='oak'))
    # rafters, low enough to duck under
    for k in range(7):
        y = 1.6 + k * 2.0
        R.nocol.add(box(0.6, y - 0.09, LT - 0.2, C - 0.6, y + 0.09, LT, 'walnut'))
    # low shelves round the walls, and books stacked on the boards
    sh(R, '+y', 0.6, 1.0, C - 1.0, z=AZ, rows=3, frame='walnut')
    sh(R, '+x', 0.6, 1.4, 9.0, z=AZ, rows=3, frame='walnut')
    sh(R, '-x', C - 0.6, 1.4, 12.3, z=AZ, rows=3, frame='walnut')
    for (x, y, n, a) in ((7.5, 11.0, 6, 0.3), (7.9, 11.3, 4, 1.1), (10.6, 4.2, 8, 0.7), (11.0, 3.8, 5, 2.0),
                         (2.4, 11.8, 7, 1.4), (12.8, 9.5, 3, 0.2), (8.8, 7.2, 5, 2.6)):
        g = Geo()
        for i in range(n):
            g.add(box(-0.13, -0.09, i * 0.045, 0.13, 0.09, i * 0.045 + 0.04, ('oxblood', 'green', 'leather', 'walnut')[i % 4]))
        g.xform(a, x, y, AZ)
        R.nocol.add(g)
    # a bed on the boards, a chair facing the wall, a candle
    R.parts.add(box(11.4, 10.2, AZ, 13.4, 11.2, AZ + 0.22, 'bed'))
    c = chair(0, 0, math.pi); c.xform(0, 2.0, 6.5, AZ); R.parts.add(c)
    R.spot('sit', 2.0, 6.5, AZ + 0.48, math.pi)
    R.parts.add(box(11.2, 12.0, AZ, 11.5, 12.3, AZ + 0.05, 'brass'))
    R.light(cyl(11.35, 12.15, AZ + 0.05, AZ + 0.2, 0.025, 8, side='e_candle', top='e_candle', bottom='e_candle'))
    for (x, y, m) in ((4.8, 4.0, 'e_lamp'), (10.5, 6.5, 'e_dim'), (13.2, 12.6, 'e_dim'), (8.0, 11.0, 'e_lamp'), (2.4, 12.2, 'e_dim')):
        bulb(R, x, y, LT - 0.5, r=0.1, m=m, top=LT - 0.2)
    R.light(sphere(3.0, 2.0, AZ + 0.12, 0.08, 8, 4, 'e_candle'))
    # the way into the wall: a gap in the loft's north side at its east end
    R.cut(box(13.6, YN - 0.05, AZ, C - 0.6, PY0 + 0.05, LT, 'plaster', bottom='floor', top='oak'))


def passage(R):
    """Inside the north wall: a slot of a room, one person wide, full height, stepping down to the high door."""
    R.cut(box(PX0, PY0, DZ, C - 0.6, PY1, LT, 'ivory', bottom='oak', top='plaster'))
    n = 10; rise = (AZ - DZ) / n; run = 0.3
    x_top = C - 0.6 - 0.6                       # a small head landing at the east end, level with the loft
    x_foot = x_top - n * run
    R.parts.add(box(x_top, PY0, DZ, C - 0.6, PY1, AZ, 'oak', sides='walnut'))
    R.flight(x_foot, PY0, DZ, PY1 - PY0, n, rise, run, '+x', m='oak', riser='walnut', side='walnut')
    # books on the slot's back wall, all the way up
    sh(R, '-y', PY1, PX0 + 0.1, x_foot - 0.1, z=DZ, rows=9, frame='walnut', depth=0.24)
    R.light(sphere(PX0 + 0.35, PY1 - 0.3, DZ + 2.3, 0.07, 8, 4, 'e_candle'))
    bulb(R, x_top - 1.5, (PY0 + PY1) / 2, DZ + 3.2, r=0.08, m='e_dim', top=LT)


def hall(R):
    # books on every wall
    rows = 11
    sh(R, '+y', T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '+y', T, 9.9, C - 0.5, rows=rows, frame='walnut')
    sh(R, '+x', T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '+x', T, 9.9, YN - 0.1, rows=rows, frame='walnut')
    sh(R, '-x', C - T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '-x', C - T, 9.9, YN - 0.1, rows=rows, frame='walnut')
    sh(R, '-y', YN, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '-y', YN, HX + HW / 2 + 0.35, C - 0.5, rows=7, frame='walnut')
    sh(R, '+y', T, 6.1, 9.9, z=4.3, rows=2, frame='walnut')     # over the south door
    # a reading table and lamps
    R.parts.add(table(9.0, 5.0, 12.5, 6.2, 0.78, 'walnut', top='leather'))
    desk_lamp(R, 9.8, 5.6, 0.78); desk_lamp(R, 11.7, 5.6, 0.78)
    for x in (9.8, 11.7):
        R.parts.add(chair(x, 4.45, math.pi / 2))
        R.spot('sit', x, 4.45, 0.48, math.pi / 2)
    for (x, y) in ((3.4, 3.4), (12.6, 3.4), (12.6, 10.8), (8.0, 8.0)):
        bulb(R, x, y, 3.9, r=0.16, top=H)
    for (x, y) in ((2.0, 12.6), (C - 2.0, 1.6)):
        R.parts.add(cyl(x, y, 0, 1.5, 0.02, 6, side='brass', caps=False))
        R.parts.add(cyl(x, y, 0, 0.03, 0.18, 12, side='brass', top='brass'))
        R.light(sphere(x, y, 1.6, 0.12, 12, 6, 'e_amber'))
    navloop(R, [(2.0, 2.0), (8, 2.0), (C - 2.0, 2.0), (C - 2.0, 8), (C - 2.0, 12.3), (8, 12.3), (2.4, 11.4), (2.0, 8)])
    a = R.navpt(8, 8); R.link(3, a, 7); R.link(1, a, 5)
    a, b = R.navpt((FX0 + FX1) / 2, FY0 - 0.5), R.navpt((LX0 + LX1) / 2, LY0 + 0.8, LZ)
    R.link(a, b)
    R.spot('probe', 8, 11.0, 1.7)
    R.meta.update(label='The Door in the Ceiling', weight=3,
                  blurb='A stair climbs to a trapdoor that someone has left open. High in the north wall a door stands ajar, and no ladder in the room is long enough.')
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]
    return tidy(R)
