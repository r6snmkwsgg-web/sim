"""The Door in the Ceiling: a steep stair climbs to a landing under an open trapdoor that gives onto
darkness. High in the north wall another door stands ajar, four metres up, with no way to reach it."""
from lib import *
from kit_a import *

H = 6.6                      # the ceiling (the trap's dark shaft goes on above it)
YN = 14.9                    # north wall thickened for the high door's reveal
LZ = 4.4                     # the landing under the trap
FX0, FX1 = 4.0, 5.3          # the stair, climbing +y
N, RISE, RUN = 20, LZ / 20, 0.3
FY1 = 8.7
FY0 = FY1 - N * RUN
LX0, LX1, LY0, LY1 = 3.9, 5.7, FY1, FY1 + 1.7


def make():
    R = Room('ceilingdoor', 1, 1, res=1024)
    shell(R, y1=YN, wall='ivory', floor='floor', ceil='plaster', h=H)
    # the trap: a black shaft into the slab above the landing, an oak frame, the leaf hanging open
    tx0, tx1, ty0, ty1 = LX0 + 0.1, LX1 - 0.1, LY0 + 0.1, LY1 - 0.1
    R.cut(box(tx0, ty0, H - 0.05, tx1, ty1, R.hi - 0.05, 'black', top='black', bottom='black'))
    for (x0, y0, x1, y1) in ((tx0 - 0.12, ty0 - 0.12, tx1 + 0.12, ty0), (tx0 - 0.12, ty1, tx1 + 0.12, ty1 + 0.12),
                             (tx0 - 0.12, ty0, tx0, ty1), (tx1, ty0, tx1 + 0.12, ty1)):
        R.nocol.add(box(x0, y0, H - 0.06, x1, y1, H, 'oak'))
    leaf = box(-0.04, 0, -(tx1 - tx0 - 0.04), 0.0, ty1 - ty0 - 0.04, 0, 'oak', sides='walnut')
    rot(leaf, 'y', 0.22)
    leaf.xform(0, tx0 - 0.02, ty0 + 0.02, H - 0.02)
    R.nocol.add(leaf)
    for k in range(3):
        R.nocol.add(box(tx0 - 0.1, ty0 + 0.2 + k * 0.55, H - 0.35, tx0 - 0.02, ty0 + 0.25 + k * 0.55, H - 0.02, 'iron'))
    R.nocol.add(cyl(tx0 - 0.3, ty0 + 0.8, H - 1.3, H - 1.2, 0.08, 10, side='iron', top='iron', bottom='iron'))   # the ring pull
    # the stair and landing, on iron posts, railed all the way
    open_flight(R, FX0, FY0, 0, FX1 - FX0, N, RISE, RUN, tread='oak', stringer='walnut')
    R.parts.add(box(LX0, LY0, LZ - 0.25, LX1, LY1, LZ, 'oak', sides='walnut', bottom='walnut'))
    for (x, y) in ((LX0 + 0.08, LY0 + 0.08), (LX1 - 0.08, LY0 + 0.08), (LX0 + 0.08, LY1 - 0.08), (LX1 - 0.08, LY1 - 0.08)):
        R.parts.add(box(x - 0.06, y - 0.06, 0, x + 0.06, y + 0.06, LZ - 0.25, 'iron', skip=('-z',)))
    for x in (FX0 + 0.04, FX1 - 0.04):
        stair_rail(R, x, FY0 + RUN, RISE, x, FY1, LZ, m='brass')
    rail(R, LX0 + 0.04, LY0, LX0 + 0.04, LY1 - 0.04, LZ)
    rail(R, LX0 + 0.04, LY1 - 0.04, LX1 - 0.04, LY1 - 0.04, LZ)
    rail(R, LX1 - 0.04, LY1 - 0.04, LX1 - 0.04, LY0, LZ)
    rail(R, LX1 - 0.04, LY0 + 0.04, FX1 - 0.04, LY0 + 0.04, LZ)
    # the high door, ajar, 4 m up the north wall, a sign over it
    hx, hw, hz, hh = 11.6, 1.3, 4.0, 2.25
    R.cut(box(hx - hw / 2, YN - 0.05, hz, hx + hw / 2, YN + 0.7, hz + hh, 'black', bottom='oak', top='black'))
    R.parts.add(box(hx - hw / 2 - 0.16, YN - 0.08, hz + hh, hx + hw / 2 + 0.16, YN, hz + hh + 0.16, 'walnut'))
    for s in (-1, 1):
        x = hx + s * (hw / 2 + 0.08)
        R.parts.add(box(x - 0.08, YN - 0.08, hz - 0.1, x + 0.08, YN, hz + hh, 'walnut'))
    R.parts.add(box(hx - hw / 2 - 0.2, YN - 0.18, hz - 0.12, hx + hw / 2 + 0.2, YN, hz, 'tile'))   # a sill
    door = box(0, -0.05, 0, hw - 0.04, 0.0, hh - 0.04, 'oak')
    for (z0, z1) in ((0.15, 0.95), (1.15, 2.05)):
        door.add(box(0.12, -0.07, z0, hw - 0.16, -0.05, z1, 'walnut'))
    door.add(box(hw - 0.2, -0.12, 1.0, hw - 0.14, -0.05, 1.06, 'brass'))
    door.xform(-1.05, hx - hw / 2 + 0.02, YN + 0.02, hz)
    R.nocol.add(door)
    R.parts.add(box(hx - 0.35, YN - 0.1, hz + hh + 0.2, hx + 0.35, YN, hz + hh + 0.42, 'black'))
    R.light(box(hx - 0.3, YN - 0.12, hz + hh + 0.23, hx + 0.3, YN - 0.1, hz + hh + 0.39, 'e_exit'))
    # a ladder leaning up toward it that stops far too short
    R.nocol.add(ladder(hx + 0.1, YN - 0.36, -math.pi / 2, h=2.3, lean=0.8))
    # books on every wall
    rows = 14
    sh(R, '+y', T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '+y', T, 9.9, C - 0.5, rows=rows, frame='walnut')
    sh(R, '+x', T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '+x', T, 9.9, YN - 0.1, rows=rows, frame='walnut')
    sh(R, '-x', C - T, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '-x', C - T, 9.9, YN - 0.1, rows=rows, frame='walnut')
    sh(R, '-y', YN, 0.5, 6.1, rows=rows, frame='walnut')
    sh(R, '-y', YN, 9.9, hx - hw / 2 - 0.35, rows=9, frame='walnut')
    sh(R, '-y', YN, hx + hw / 2 + 0.35, C - 0.5, rows=9, frame='walnut')
    sh(R, '+y', T, 6.1, 9.9, z=4.4, rows=4, frame='walnut')     # over the south door
    # a reading table and lamps
    R.parts.add(table(9.0, 5.0, 12.5, 6.2, 0.78, 'walnut', top='leather'))
    desk_lamp(R, 9.8, 5.6, 0.78); desk_lamp(R, 11.7, 5.6, 0.78)
    for x in (9.8, 11.7):
        R.parts.add(chair(x, 4.45, math.pi / 2))
        R.spot('sit', x, 4.45, 0.48, math.pi / 2)
    for (x, y) in ((3.4, 3.4), (12.6, 3.4), (12.6, 11.2), (8.0, 8.0)):
        bulb(R, x, y, 3.6, r=0.16, top=H)
    for (x, y) in ((2.0, 13.4), (C - 2.0, 1.6)):
        R.parts.add(cyl(x, y, 0, 1.5, 0.02, 6, side='brass', caps=False))
        R.parts.add(cyl(x, y, 0, 0.03, 0.18, 12, side='brass', top='brass'))
        R.light(sphere(x, y, 1.6, 0.12, 12, 6, 'e_amber'))
    navloop(R, [(2.0, 2.0), (8, 2.0), (C - 2.0, 2.0), (C - 2.0, 8), (C - 2.0, 13.3), (8, 13.3), (2.4, 12.0), (2.0, 8)])
    a = R.navpt(8, 8); R.link(3, a, 7); R.link(1, a, 5)
    a, b = R.navpt((FX0 + FX1) / 2, FY0 - 0.5), R.navpt((LX0 + LX1) / 2, LY0 + 0.8, LZ)
    R.link(a, b)
    R.spot('probe', 8, 11.5, 1.7)
    R.meta.update(label='The Door in the Ceiling', weight=3,
                  blurb='A stair climbs to a trapdoor that someone has left open. Above it there is nothing at all, which is somehow worse than something.')
    R.meta['box'] = [[T, 0, T], [C - T, H, YN]]
    return tidy(R)
