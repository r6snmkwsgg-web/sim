"""The Radial Stacks: twelve double bookcases radiate like spokes from a round librarian's desk,
stepping up in height as they go out, so the room is a sunburst of books. Lamps ring the desk."""
from lib import *
from kit_b import *


def make():
    R = Room('radial', 1, 1, res=1024)
    H = 6.4
    shell(R, H, wall='tile', floor='floor', ceil='plaster')
    cx = cy = 8.0
    # a round coffer over the desk, a lantern of light in it
    R.cut(cyl(cx, cy, H - 0.05, H + 0.8, 3.2, 48, side='plaster', top='plaster', bottom='plaster'))
    R.light(ring(cx, cy, H + 0.7, H + 0.74, 1.2, 3.1, 48, top='e_sky', bottom='e_sky', inner='e_sky', outer='e_sky'))
    R.nocol.add(ring(cx, cy, H + 0.5, H + 0.8, 1.1, 1.25, 32, top='plaster', bottom='plaster', inner='plaster', outer='plaster'))
    # the spokes
    n = 12
    steps = ((2.9, 7.6, 6),)
    for k in range(n):
        phi = (k + 0.5) * 2 * math.pi / n
        ux, uy = math.cos(phi), math.sin(phi)
        nx, ny = -uy, ux
        lim = (8 - 1.35) / max(abs(ux), abs(uy))
        if abs(abs(ux) - abs(uy)) > 0.6: lim = min(lim, 5.7)     # the spokes beside the doors stop short
        for (r0, r1, rows) in steps:
            if r0 > lim - 0.6: break
            r1 = min(r1, lim)
            L = r1 - r0
            # left face: faces phi + 90, extends outward from r0
            bshelf(R, cx + ux * r0 + nx * 0.012, cy + uy * r0 + ny * 0.012, 0, L, phi + math.pi / 2, rows=rows, frame='oak', depth=0.3)
            bshelf(R, cx + ux * r1 - nx * 0.012, cy + uy * r1 - ny * 0.012, 0, L, phi - math.pi / 2, rows=rows, frame='oak', depth=0.3, sides=False)
            # a brass lamp on the outer end of each step
            ex, ey = cx + ux * (r1 + 0.05), cy + uy * (r1 + 0.05)
            hh = rows * 0.42 + 0.2
            R.nocol.add(box(-0.03, -0.03, 0, 0.03, 0.03, 0.25, 'brass').xform(phi, ex, ey, hh))
            bulb(R, ex, ey, hh + 0.33, 0.09, 'e_lamp' if rows > 5 else 'e_amber')
    # the desk: a ring with a gap to the south-west, a chair inside
    a0, a1 = math.radians(-100), math.radians(210)
    R.parts.add(ring(cx, cy, 0, 0.92, 1.45, 1.95, 40, top='walnut', bottom='walnut', inner='walnut', outer='walnut', a0=a0, a1=a1))
    R.parts.add(ring(cx, cy, 0.92, 0.97, 1.4, 2.02, 40, top='leather', bottom='walnut', inner='walnut', outer='walnut', a0=a0, a1=a1))
    R.parts.add(ring(cx, cy, 0.97, 1.25, 1.88, 2.02, 40, top='walnut', bottom='walnut', inner='walnut', outer='walnut', a0=a0, a1=a1))
    chair(R, cx, cy + 0.6, math.pi / 2, frame='walnut', seat='leather')
    chair(R, cx + 0.5, cy - 0.3, -math.pi / 6, frame='walnut', seat='leather')
    for k in range(8):
        a = a0 + (k + 0.5) * (a1 - a0) / 8
        table_lamp(R, cx + math.cos(a) * 1.68, cy + math.sin(a) * 1.68, 0.97, shade='green', r=0.17)
    # a pile of returns on the desk
    for k in range(5):
        a = math.radians(40)
        R.nocol.add(box(-0.14, -0.1, 0.97 + k * 0.06, 0.14, 0.1, 1.02 + k * 0.06, 'leather').xform(a + k * 0.3, cx + math.cos(a) * 1.7, cy + math.sin(a) * 1.7))
    # walks: round the desk and out along the aisles to the doors
    ring_ = loop(R, [(cx + math.cos(k * math.pi / 6) * 2.5, cy + math.sin(k * math.pi / 6) * 2.5) for k in range(12)])
    for k, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
        a = R.navpt(cx + dx * 6.4, cy + dy * 6.4)
        R.link(ring_[k * 3], a)
    for k in range(4):
        phi = k * math.pi / 2 + math.pi / 4 + math.pi / 12
        R.spot('read', cx + math.cos(phi) * 3.6, cy + math.sin(phi) * 3.6, 0, phi + math.pi / 2)
    R.spot('probe', cx, cy - 2.6, 1.7)
    R.meta.update(label='The Radial Stacks', weight=7,
                  blurb='Every aisle leads to the desk. The desk is staffed, you are sure of it, just not at the moment.')
    R.meta['box'] = [[T, 0, T], [C - T, H + 0.8, C - T]]
    return R
